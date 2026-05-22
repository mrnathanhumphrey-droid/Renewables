"""
C3 Probe 4 — PyBaMM L9 PERMANOVA, pre-registered.

Pre-reg: literature/19_c3_pybamm_pre_registration.md (commit d03a558).

Reads data/processed/pybamm_l9_results.parquet (produced by Modal run of
code/modal_pybamm_c3.py and copied locally).

Primary test: 3 PERMANOVAs (one per design parameter), Bonferroni alpha/3 = 0.0167,
effect-size floor pseudo-F > 3.0.

Falsification verdicts (pre-reg sec.8):
  PARAMETER PASS:      p<0.0167 AND F>3.0
  PARAMETER WEAK PASS: p in [0.0167, 0.05] AND F>2.0
  PARAMETER NULL:      p>=0.05 OR F<2.0

H4 verdicts:
  STRONG SUPPORT: 2+ params PASS
  SUPPORT:        1 param PASS
  WEAK:           0 PASS, 2+ WEAK PASS
  NULL:           0 PASS, <2 WEAK PASS
  INVALID:        <70% valid cells
"""

from pathlib import Path
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_results.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG = np.random.default_rng(seed=42)
N_PERMS = 10000

ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05


def permanova_pseudoF(u_mat, labels):
    n = len(u_mat)
    norms = np.linalg.norm(u_mat, axis=1, keepdims=True)
    um = u_mat / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = um @ um.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    d_mat = 1.0 - cos_mat
    labels = np.asarray(labels)
    unique = np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for u in unique:
        mask = (labels == u)
        n_u = int(mask.sum())
        if n_u < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_u)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan")
    return (between_ss / (a - 1)) / (within_ss / (n - a))


def permanova_test(u_mat, labels, n_perms=N_PERMS):
    F_obs = permanova_pseudoF(u_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = RNG.permutation(labels)
        F_p = permanova_pseudoF(u_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def parameter_verdict(F, p):
    # PERMANOVA returns NaN when between-group SS collapses to zero (centroids
    # essentially identical). Per pre-reg sec.8, INVALID is reserved for sim
    # failures (<70% valid cells). A NaN here is "effect undetectable" -> NULL.
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > EFFECT_F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > EFFECT_F_WEAK:
        return "WEAK PASS"
    if p >= ALPHA_WEAK or F < EFFECT_F_WEAK:
        return "NULL"
    return "WEAK PASS"  # fallback


def joint_verdict(verdicts):
    n_pass = sum(1 for v in verdicts.values() if v == "PASS")
    n_weak = sum(1 for v in verdicts.values() if v == "WEAK PASS")
    if n_pass >= 2:
        return "H4 STRONG SUPPORT"
    if n_pass == 1:
        return "H4 SUPPORT"
    if n_pass == 0 and n_weak >= 2:
        return "H4 WEAK"
    return "H4 NULL"


def main():
    print("=== C3 Probe 4 — PyBaMM L9 PERMANOVA (pre-reg literature/19) ===\n")
    df = pd.read_parquet(IN_PARQUET)
    n_total = len(df)
    n_valid = df["error"].isna().sum() if "error" in df.columns else n_total
    print(f"Total cells: {n_total}")
    print(f"Valid cells (no sim error): {n_valid}")
    if "error" in df.columns:
        n_err = df["error"].notna().sum()
        print(f"Failed cells: {n_err}")

    valid_frac = n_valid / n_total if n_total > 0 else 0
    if valid_frac < 0.70:
        print(f"\nH4 INVALID: only {valid_frac*100:.1f}% of cells produced valid residuals (pre-reg floor 70%)")
        return

    df = df[df["error"].isna()].copy() if "error" in df.columns else df.copy()
    df = df[np.isfinite(df["fresh_Q"]) & np.isfinite(df["aged_Q"])].copy()
    df = df[np.isfinite(df["fresh_R_DC"]) & np.isfinite(df["aged_R_DC"])].copy()
    df = df[np.isfinite(df["fresh_R_total"]) & np.isfinite(df["aged_R_total"])].copy()
    print(f"After dropping NaN residuals: {len(df)}")

    # Compute per-cell unit residuals
    raw_resid = df[["aged_Q", "aged_R_DC", "aged_R_total"]].values - \
                df[["fresh_Q", "fresh_R_DC", "fresh_R_total"]].values
    fresh_pool = df[["fresh_Q", "fresh_R_DC", "fresh_R_total"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    df["u1"] = u[:, 0]
    df["u2"] = u[:, 1]
    df["u3"] = u[:, 2]
    df["mahal"] = norms.flatten()

    print(f"\nPer-condition cell counts:")
    print(df.groupby("cond_idx").size())

    # Three per-parameter PERMANOVAs
    verdicts = {}
    print(f"\n=== Per-parameter PERMANOVAs (Bonferroni alpha/3 = {ALPHA_BONFERRONI}) ===")
    for param_col, label in [("thickness_level", "Cathode thickness"),
                              ("transference_level", "Transference number"),
                              ("particle_radius_level", "Particle radius")]:
        print(f"\n--- {label} ---")
        counts = df.groupby(param_col).size().to_dict()
        for lvl in ["low", "mid", "high"]:
            print(f"  {lvl}: n={counts.get(lvl, 0)}")
        # Per-level centroid direction
        for lvl, g in df.groupby(param_col):
            uu = g[["u1", "u2", "u3"]].values
            c = uu.mean(axis=0)
            c_n = c / max(np.linalg.norm(c), 1e-12)
            print(f"  centroid {lvl}: ({c_n[0]:+.3f}, {c_n[1]:+.3f}, {c_n[2]:+.3f})  n={len(g)}")
        F, p = permanova_test(df[["u1", "u2", "u3"]].values, df[param_col].values)
        v = parameter_verdict(F, p)
        verdicts[param_col] = v
        print(f"\n  pseudo-F = {F:.3f}")
        print(f"  p (10000 perm) = {p:.4f}")
        print(f"  VERDICT: {v}")

    jv = joint_verdict(verdicts)
    print(f"\n=== H4 JOINT VERDICT (pre-reg sec.8) ===")
    print(f"  Cathode thickness:   {verdicts['thickness_level']}")
    print(f"  Transference number: {verdicts['transference_level']}")
    print(f"  Particle radius:     {verdicts['particle_radius_level']}")
    print(f"\n  {jv}")

    df.to_parquet(OUT_DIR / "c3_pybamm_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_pybamm_results.parquet'}")


if __name__ == "__main__":
    main()
