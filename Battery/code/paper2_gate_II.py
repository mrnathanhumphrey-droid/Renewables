"""
Paper 2 — Gate II (design-condition AUC).

Per pre-reg literature/28 §4: for each Gate-I-surviving operator, compute AUC
for separating design conditions in each of 3 Gate II training cohorts.
Operator passes Gate II if max-AUC across design axes >= 0.60 in at least
2 of 3 cohorts.

Gate II cohorts:
  - PyBaMM Probe 5 training split (70 cells, design axes: thickness, transference, particle_radius)
  - Khan 2025 (design axes: aging_type, T_C, soc_range)
  - Severson (design axes: first_step_C, last_step_C, severity)

Output: paper2_gate_II_results.parquet (operator list with PASS/FAIL +
per-cohort max-AUC per axis).
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND_CSV = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
AUC_THRESHOLD = 0.60
COHORT_PASS_REQUIRED = 2  # of 3


# ---------- max one-vs-rest AUC over levels ----------

def max_ovr_auc(values, labels):
    """For multi-level labels, take max over one-vs-rest AUC per level.
    Returns NaN if data insufficient."""
    v = np.asarray(values, dtype=float)
    mask = np.isfinite(v)
    if mask.sum() < 8:
        return float("nan")
    v = v[mask]
    labels = np.asarray(labels)[mask]
    levels = np.unique(labels[~pd.isna(labels)])
    if len(levels) < 2:
        return float("nan")
    aucs = []
    for lvl in levels:
        y = (labels == lvl).astype(int)
        if y.sum() < 2 or (len(y) - y.sum()) < 2:
            continue
        try:
            # AUC is symmetric: take max of AUC and 1-AUC since we don't a priori
            # know which direction of the operator value indicates "level"
            a = roc_auc_score(y, v)
            aucs.append(max(a, 1 - a))
        except Exception:
            continue
    if not aucs:
        return float("nan")
    return float(max(aucs))


# ---------- cohort-specific axis loaders ----------

def get_pybamm_axes(df):
    return {
        "thickness": df["thickness_level"].values,
        "transference": df["transference_level"].values,
        "particle_radius": df["particle_radius_level"].values,
    }


def get_khan_axes(df):
    """Khan: aging_type, T_C, soc_range from cell_conditions.csv"""
    if not KHAN_COND_CSV.exists():
        return {}
    conds = pd.read_csv(KHAN_COND_CSV)
    # cell_id in df matches `cell` column in conds (e.g., "S1")
    merged = df.merge(conds, left_on="cell_id", right_on="cell", how="inner")
    if len(merged) == 0:
        return {}
    return {
        "aging_type": merged["aging_type"].values,
        "T_C": merged["T_C"].astype(str).values,
        "soc_range": merged["soc_range"].values,
        # Pre-filter df to merged set (drop cells not in conditions table)
        "_filtered_indices": merged.index.values,
    }


def get_severson_axes(df):
    """Severson: first_step_C, last_step_C, severity (compute on the fly).
    Use tertile cuts to create 3-level labels per axis."""
    # Need last_step_C, soc_handoff, severity computed from protocol strings
    # Re-use logic from c3_severson_v2.py
    import re

    def parse_axes_from_protocol(protocol_str):
        fname = re.split(r"[\\/]+", protocol_str)[-1]
        body = re.sub(r"^\d{8}[-_]?", "", fname, count=1)
        body = re.sub(r"(?:_newstructure)?\.[sS][dD][uU]$", "", body)
        c_token_re = re.compile(r"(\d+)(?:_(\d+))?C(?![a-zA-Z])", re.IGNORECASE)
        handoff_re = re.compile(r"(\d+)(?:per|PER)", re.IGNORECASE)
        c_tokens = list(c_token_re.finditer(body))
        if not c_tokens:
            return float("nan"), float("nan"), float("nan")
        def dec(m):
            return float(f"{m.group(1)}.{m.group(2)}") if m.group(2) else float(m.group(1))
        first_c = dec(c_tokens[0])
        last_c = dec(c_tokens[-1])
        ho_m = handoff_re.search(body)
        ho = float(ho_m.group(1)) if ho_m else 100.0
        sev = first_c * (ho / 100.0) + last_c * (1 - ho / 100.0)
        return last_c, ho, sev

    parsed = df["protocol"].apply(lambda p: parse_axes_from_protocol(p) if isinstance(p, str) else (float("nan"),)*3)
    df = df.copy()
    df["last_step_C"] = [p[0] for p in parsed]
    df["soc_handoff"] = [p[1] for p in parsed]
    df["severity"] = [p[2] for p in parsed]

    axes = {}
    for col in ["first_step_C", "last_step_C", "severity"]:
        if col not in df.columns:
            continue
        s = df[col].astype(float)
        valid = s.dropna()
        if len(valid) < 9:
            continue
        t33 = float(np.percentile(valid, 33.33))
        t67 = float(np.percentile(valid, 66.67))
        labels = np.where(s < t33, "T1", np.where(s < t67, "T2", "T3"))
        axes[col] = labels
    return axes


def main():
    print("=== Paper 2 Gate II — design-condition AUC (pre-reg literature/28 §4) ===\n")

    # Load Gate I results
    gate_I_results = pd.read_parquet(PROCESSED / "paper2_gate_I_results.parquet")
    survivors = gate_I_results[gate_I_results["passed_gate_I"]]["operator"].tolist()
    print(f"Operators surviving Gate I: {len(survivors)}")
    for op in survivors:
        print(f"  - {op}")

    # Load Gate II training cohorts
    pybamm_train = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_train.parquet")
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    severson = pd.read_parquet(PROCESSED / "paper2_operators_severson.parquet")

    # Khan: merge in design labels
    khan_axes = get_khan_axes(khan)
    if "_filtered_indices" in khan_axes:
        khan = khan.iloc[khan_axes.pop("_filtered_indices")].reset_index(drop=True)
    pybamm_axes = get_pybamm_axes(pybamm_train)
    severson_axes = get_severson_axes(severson)

    print(f"\nGate II training cohort counts:")
    print(f"  PyBaMM (train): n={len(pybamm_train)}, axes={list(pybamm_axes.keys())}")
    print(f"  Khan:           n={len(khan)},        axes={list(khan_axes.keys())}")
    print(f"  Severson:       n={len(severson)},    axes={list(severson_axes.keys())}\n")

    # Per-operator Gate II evaluation
    rows = []
    for op in survivors:
        # Per cohort: max-AUC across design axes
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
            "passed_gate_II": bool(passed),
            "cohorts_with_data": finite_count,
            "cohorts_above_AUC_threshold": pass_count,
            "required_pass_count": required,
            "AUC_PyBaMM": cohort_max_auc.get("PyBaMM_train", float("nan")),
            "AUC_Khan": cohort_max_auc.get("Khan", float("nan")),
            "AUC_Severson": cohort_max_auc.get("Severson", float("nan")),
        })

    df_gate2 = pd.DataFrame(rows)

    print("=== Per-operator Gate II results ===\n")
    fmt = lambda v: f"{v:.3f}" if np.isfinite(v) else "  --"
    print(f"{'operator':<26} {'category':<25} {'PyBaMM':>7} {'Khan':>7} {'Sevn':>7} {'n_pass':>7} {'req':>5} {'PASS':>6}")
    for _, r in df_gate2.iterrows():
        verdict = "YES" if r["passed_gate_II"] else "no"
        print(f"  {r['operator']:<24} {r['category']:<25}  "
              f"{fmt(r['AUC_PyBaMM']):>7} {fmt(r['AUC_Khan']):>7} "
              f"{fmt(r['AUC_Severson']):>7} "
              f"{int(r['cohorts_above_AUC_threshold']):>5}/{int(r['cohorts_with_data']):<2} "
              f"{int(r['required_pass_count']):>5} {verdict:>6}")

    # Attrition by category
    print("\n=== Attrition by physics category (Gate II only — survivors of Gate I) ===\n")
    for cat in sorted(df_gate2["category"].unique()):
        sub = df_gate2[df_gate2["category"] == cat]
        n_pass = sub["passed_gate_II"].sum()
        n_total = len(sub)
        print(f"  {cat:30s}: {n_pass}/{n_total} survived")

    n_pass = df_gate2["passed_gate_II"].sum()
    n_total = len(df_gate2)
    print(f"\nGate II survivors: {n_pass}/{n_total} (of Gate I survivors)")
    print(f"\nOverall pipeline so far: 12 initial -> {len(gate_I_results[gate_I_results['passed_gate_I']])} after Gate I -> {n_pass} after Gate II")

    df_gate2.to_parquet(PROCESSED / "paper2_gate_II_results.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_gate_II_results.parquet'}")


if __name__ == "__main__":
    main()
