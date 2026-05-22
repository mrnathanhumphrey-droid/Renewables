"""
Paper 2 — Gate II v2 (design-condition AUC on amended-Gate-I survivors).

Identical logic to paper2_gate_II.py per literature/28 §4 (which is
UNCHANGED by the literature/30 amendment). Only the input file changes:
reads paper2_gate_I_v2_results.parquet; writes paper2_gate_II_v2_results.parquet.

This preserves the strict-pre-reg Gate II result alongside the amended
result for honest dual-reporting at literature/31.
"""

from pathlib import Path
import numpy as np
import pandas as pd

# Re-use all helpers from paper2_gate_II.py
from paper2_gate_II import (
    max_ovr_auc, get_pybamm_axes, get_khan_axes, get_severson_axes,
    AUC_THRESHOLD, COHORT_PASS_REQUIRED, PROCESSED,
)


def main():
    print("=== Paper 2 Gate II v2 — design-condition AUC on amended-Gate-I survivors ===")
    print("    Same locked procedure as literature/28 §4; input = paper2_gate_I_v2_results.parquet\n")

    gate_I_results = pd.read_parquet(PROCESSED / "paper2_gate_I_v2_results.parquet")
    survivors = gate_I_results[gate_I_results["passed_gate_I"]]["operator"].tolist()
    print(f"Operators surviving amended Gate I: {len(survivors)}")
    for op in survivors:
        print(f"  - {op}")

    pybamm_train = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_train.parquet")
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    severson = pd.read_parquet(PROCESSED / "paper2_operators_severson.parquet")

    khan_axes = get_khan_axes(khan)
    if "_filtered_indices" in khan_axes:
        khan = khan.iloc[khan_axes.pop("_filtered_indices")].reset_index(drop=True)
    pybamm_axes = get_pybamm_axes(pybamm_train)
    severson_axes = get_severson_axes(severson)

    print(f"\nGate II training cohort counts:")
    print(f"  PyBaMM (train): n={len(pybamm_train)}, axes={list(pybamm_axes.keys())}")
    print(f"  Khan:           n={len(khan)},        axes={list(khan_axes.keys())}")
    print(f"  Severson:       n={len(severson)},    axes={list(severson_axes.keys())}\n")

    rows = []
    for op in survivors:
        cohort_max_auc = {}
        for cname, df, axes in [
            ("PyBaMM_train", pybamm_train, pybamm_axes),
            ("Khan", khan, khan_axes),
            ("Severson", severson, severson_axes),
        ]:
            if op not in df.columns:
                cohort_max_auc[cname] = float("nan")
                continue
            v = df[op].values
            per_axis = []
            for axis_name, labels in axes.items():
                a = max_ovr_auc(v, labels)
                if np.isfinite(a):
                    per_axis.append((axis_name, a))
            if not per_axis:
                cohort_max_auc[cname] = float("nan")
            else:
                cohort_max_auc[cname] = max(a for _, a in per_axis)

        finite_count = sum(1 for v in cohort_max_auc.values() if np.isfinite(v))
        pass_count = sum(1 for v in cohort_max_auc.values()
                          if np.isfinite(v) and v >= AUC_THRESHOLD)
        required = COHORT_PASS_REQUIRED
        if finite_count < 3:
            required = max(1, int(np.ceil((2.0 / 3) * finite_count)))
        passed = (pass_count >= required) and (finite_count >= 2)

        rows.append({
            "operator": op,
            "category": gate_I_results.loc[gate_I_results["operator"] == op, "category"].iloc[0],
            "family": gate_I_results.loc[gate_I_results["operator"] == op, "family"].iloc[0],
            "passed_gate_II": bool(passed),
            "cohorts_with_data": finite_count,
            "cohorts_above_AUC_threshold": pass_count,
            "required_pass_count": required,
            "AUC_PyBaMM": cohort_max_auc.get("PyBaMM_train", float("nan")),
            "AUC_Khan": cohort_max_auc.get("Khan", float("nan")),
            "AUC_Severson": cohort_max_auc.get("Severson", float("nan")),
        })

    df_gate2 = pd.DataFrame(rows)

    print("=== Per-operator Gate II v2 results ===\n")
    fmt = lambda v: f"{v:.3f}" if np.isfinite(v) else "  --"
    print(f"{'operator':<26} {'category':<25} {'PyBaMM':>7} {'Khan':>7} {'Sevn':>7} {'n_pass':>7} {'req':>5} {'PASS':>6}")
    for _, r in df_gate2.iterrows():
        verdict = "YES" if r["passed_gate_II"] else "no"
        print(f"  {r['operator']:<24} {r['category']:<25}  "
              f"{fmt(r['AUC_PyBaMM']):>7} {fmt(r['AUC_Khan']):>7} "
              f"{fmt(r['AUC_Severson']):>7} "
              f"{int(r['cohorts_above_AUC_threshold']):>5}/{int(r['cohorts_with_data']):<2} "
              f"{int(r['required_pass_count']):>5} {verdict:>6}")

    print("\n=== Attrition by physics category (Gate II v2) ===\n")
    for cat in sorted(df_gate2["category"].unique()):
        sub = df_gate2[df_gate2["category"] == cat]
        n_pass = sub["passed_gate_II"].sum()
        n_total = len(sub)
        print(f"  {cat:30s}: {n_pass}/{n_total} survived")

    n_pass = df_gate2["passed_gate_II"].sum()
    n_total = len(df_gate2)
    print(f"\nGate II v2 survivors: {n_pass}/{n_total}")
    print(f"\nPipeline: 12 initial -> {len(survivors)} after amended Gate I -> {n_pass} after Gate II")

    df_gate2.to_parquet(PROCESSED / "paper2_gate_II_v2_results.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_gate_II_v2_results.parquet'}")


if __name__ == "__main__":
    main()
