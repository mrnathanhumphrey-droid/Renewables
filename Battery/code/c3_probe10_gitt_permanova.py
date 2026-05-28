"""C3 Probe 10 — GITT finite-amplitude transference PERMANOVA.

Pre-reg: literature/56_probe10_gitt_transference_prereg.md (lock 6f2d4f8).
Inputs:  data/processed/pybamm_l9_trajectories_gitt_v1.parquet (GITT operators)
         data/processed/pybamm_l9_trajectories_eis_v3.parquet (Q channel + clean filter)
Output:  data/processed/probe10_transference_results.parquet

Runs the C3 architecture (z-score -> PCA-k -> unit-vector -> cosine PERMANOVA)
on the GITT operator stacks, under the locked voltage-noise grid (cycler
precision, much tighter than EIS). Parallels Probe 9 exactly.

6D primary stack: (fresh_Q, fresh_eta_inst, fresh_eta_conc,
                   aged_Q,  aged_eta_inst,  aged_eta_conc)
8D secondary:     + (fresh_dV_slow, aged_dV_slow)

Reuses Probe 9's build_pca / cosine_dist / permanova_pseudoF / permanova_test.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from c3_probe9_extended_permanova import (
    build_pca, cosine_dist, permanova_pseudoF, permanova_test,
)

GITT_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_gitt_v1.parquet")
V3_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet")
OUT_PARQUET = Path("D:/Renewables/Battery/data/processed/probe10_transference_results.parquet")

N_PERMS = 10000
ALPHA_BONFERRONI = 0.0167
ALPHA_WEAK = 0.05
F_FLOOR = 3.0
F_WEAK = 2.0

# Locked voltage-noise grid (pre-reg §3.1) — multiplicative per operator.
V_NOISE_LEVELS = [
    {"level": 0, "sigma": 0.0000, "name": "L0 clean"},
    {"level": 1, "sigma": 0.0025, "name": "L1 best lab"},
    {"level": 2, "sigma": 0.0050, "name": "L2 PRIMARY typical academic"},
    {"level": 3, "sigma": 0.0100, "name": "L3 field"},
    {"level": 4, "sigma": 0.0200, "name": "L4 poor instrument"},
]

RNG_SEED_BASE = 3000
PCA_K_VARIANTS = [2, 3, 4]
DESIGN_PARAMS = ["thickness_level", "transference_level", "particle_radius_level"]

STACK_6D = ["fresh_Q", "fresh_eta_inst", "fresh_eta_conc",
            "aged_Q", "aged_eta_inst", "aged_eta_conc"]
STACK_8D = STACK_6D + ["fresh_dV_slow", "aged_dV_slow"]


def build_clean_table():
    gitt = pd.read_parquet(GITT_PARQUET)
    v3 = pd.read_parquet(V3_PARQUET)
    # Q channel from v3 (same capacity values as Probe 9)
    qcols = v3[["cond_idx", "cell_idx", "fresh_Q", "anchor_aged_Q", "error", "anchor_partial"]].copy()
    qcols = qcols.rename(columns={"anchor_aged_Q": "aged_Q"})
    df = gitt.merge(qcols, on=["cond_idx", "cell_idx"], suffixes=("", "_v3"))
    # clean: both parquets error-free, no anchor_partial, no NaN in any stack column
    df = df[df["error"].isna() & df["error_v3"].isna() & (df["anchor_partial"] != True)]  # noqa: E712
    need = list(set(STACK_8D))
    df = df.dropna(subset=need)
    return df.reset_index(drop=True)


def apply_vnoise(df_clean, sigma, level, cols):
    """Multiplicative voltage noise on the stack columns (per-operator, independent)."""
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    out = {}
    for j, c in enumerate(cols):
        vals = df[c].values.astype(float)
        eps = np.empty(n)
        for i in range(n):
            s = RNG_SEED_BASE + level * 10000 + j * 1000 + int(df.loc[i, "cond_idx"]) * 100 + int(df.loc[i, "cell_idx"])
            eps[i] = np.random.default_rng(s).normal(0, sigma)
        out[c] = vals * (1 + eps)
    return pd.DataFrame(out), df


def verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > F_WEAK:
        return "WEAK PASS"
    return "NULL"


def run(df_clean):
    print(f"\n=== Probe 10 GITT PERMANOVA: 2 stacks x 3 PCA-k x 3 params x 5 noise levels ===")
    results = []
    for stack_name, cols in [("6D", STACK_6D), ("8D", STACK_8D)]:
        for ln in V_NOISE_LEVELS:
            feats_df, base = apply_vnoise(df_clean, ln["sigma"], ln["level"], cols)
            feats = feats_df[cols].values
            for k in PCA_K_VARIANTS:
                pca_feats, eigvals = build_pca(feats, k)
                for dv in DESIGN_PARAMS:
                    labels = base[dv].values
                    rng = np.random.default_rng(RNG_SEED_BASE + ln["level"] * 1000 + k * 100 + hash(dv) % 100)
                    F, p = permanova_test(pca_feats, labels, rng)
                    v = verdict(F, p)
                    results.append({
                        "stack": stack_name, "noise_level": ln["level"], "noise_name": ln["name"],
                        "pca_k": k, "design_param": dv, "F_obs": F, "p_perm": p,
                        "verdict": v, "n_cells": len(base),
                        "var_expl": float(eigvals[:k].sum() / eigvals.sum()),
                    })
                    print(f"  [{stack_name}] L{ln['level']} k={k} {dv:22s}: F={F:7.3f} p={p:.4f} -> {v}")
    return pd.DataFrame(results)


def disposition(df):
    print("\n" + "=" * 78)
    print("PROBE 10 DISPOSITION (per lit/56 sections 4-5)")
    print("=" * 78)

    # P-Probe10_F1 positive control: th + pr must PASS at L0 (any stack/k)
    l0 = df[df.noise_level == 0]
    th_l0 = l0[l0.design_param == "thickness_level"]["verdict"].tolist()
    pr_l0 = l0[l0.design_param == "particle_radius_level"]["verdict"].tolist()
    th_ok = any(v in {"PASS", "WEAK PASS"} for v in th_l0)
    pr_ok = any(v in {"PASS", "WEAK PASS"} for v in pr_l0)
    f1_ok = th_ok and pr_ok
    print(f"\nP-Probe10_F1 positive control (th+pr separate at L0): "
          f"th={'OK' if th_ok else 'FAIL'} pr={'OK' if pr_ok else 'FAIL'} -> {'PASS' if f1_ok else 'FAIL'}")
    if not f1_ok:
        print("  ==> PROBE 10 INVALID — GITT operators uninformative (not transference-blind).")
        # still print the L0 th/pr F for diagnosis
        for dv in ["thickness_level", "particle_radius_level"]:
            best = l0[l0.design_param == dv].sort_values("F_obs", ascending=False).iloc[0]
            print(f"    L0 {dv}: best F={best['F_obs']:.3f} ({best['stack']} k={best['pca_k']})")
        return "PROBE 10 INVALID"

    # L2 PRIMARY transference headline (best over stack x pca_k)
    l2 = df[df.noise_level == 2]
    print("\n--- L2 PRIMARY best (stack, PCA-k) per design parameter ---")
    headline = {}
    for dv in DESIGN_PARAMS:
        sub = l2[l2.design_param == dv].sort_values("F_obs", ascending=False).iloc[0]
        headline[dv] = sub
        print(f"  {dv:22s}: best={sub['stack']} k={sub['pca_k']}  F={sub['F_obs']:.3f} p={sub['p_perm']:.4f} -> {sub['verdict']}")

    # Also report transference at L0 (the variation-vs-signal screen)
    tn_l0 = l0[l0.design_param == "transference_level"].sort_values("F_obs", ascending=False).iloc[0]
    print(f"\n  transference at L0 (best): {tn_l0['stack']} k={tn_l0['pca_k']}  "
          f"F={tn_l0['F_obs']:.3f} p={tn_l0['p_perm']:.4f} -> {tn_l0['verdict']}")

    tn = headline["transference_level"]
    print("\n=== DISPOSITION ===")
    if tn["verdict"] in {"PASS", "WEAK PASS"}:
        disp = "TRANSFERENCE RECOVERED"
    elif tn["F_obs"] > F_WEAK:
        disp = "TRANSFERENCE PARTIAL"
    else:
        disp = "TRANSFERENCE STILL NULL"
    print(f"  ==> {disp}")
    print(f"      transference L2 best: {tn['stack']} k={tn['pca_k']}, F={tn['F_obs']:.3f}, "
          f"p={tn['p_perm']:.4f}, verdict={tn['verdict']}")
    print(f"      transference L0 best: F={tn_l0['F_obs']:.3f} (if NULL at L0, noise grid is moot per §3.1)")
    return disp


def main():
    df_clean = build_clean_table()
    print(f"Clean cells (GITT + v3 merge, no NaN/partial): {len(df_clean)}")
    print(df_clean.groupby(["thickness_level", "transference_level", "particle_radius_level"]).size().to_string())
    res = run(df_clean)
    res.to_parquet(OUT_PARQUET)
    print(f"\nResults written: {OUT_PARQUET}")
    disp = disposition(res)
    print("\n" + "=" * 78)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 78)


if __name__ == "__main__":
    main()
