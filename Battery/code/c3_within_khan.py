"""
C3 within-Khan probe — design-parameter inversion from operator residuals.

C1 hit: chemistry-form-factor groups separate on the residual unit sphere
(76.1% between-group Q_max-axis variance, NMC_prism centroid distinct from
others). The C3 question: within a single chemistry-form-factor group, do
operator residual directions cluster by *operating condition*?

Khan 2025 cohort is the natural first probe:
- Single chemistry (NMC) + single form factor (prismatic)
- 22 viable cells across 17 cycle-aging conditions + 5 calendar-aging conditions
- Conditions vary by (T, SOC range, charge C-rate) for cycle; (T, storage SOC) for calendar

Per-cell residual unit vectors are already extracted in c1_cross_chemistry.py.
This script overlays the condition labels (from data/khan_2025/cell_conditions.csv,
sourced from Khan, Chu, Onori 2025 Data in Brief Table 4) and tests:

  1. Do the 6 (aging_type x T) groups separate in residual space?
  2. PERMANOVA-style permutation test: pseudo-F statistic of cosine-similarity
     between cells, comparing observed condition labels to random label shuffles
  3. Cycle-only sub-test: within the 17 cycle-aged cells, do the 3 temperatures
     produce separable residual directions?

Honest expectation: small N per condition (3-6 cells per (aging_type x T) cell)
makes pairwise centroid CIs wide. The headline test is PERMANOVA against the
shuffle null.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from itertools import combinations


OUT_DIR = Path("D:/Renewables/Battery/data/processed")
CONDITIONS_CSV = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
N_PERMS = 10000
RNG = np.random.default_rng(seed=42)


def load_khan_units_with_conditions():
    """Load Khan unit vectors from C1, merge with condition table."""
    units = pd.read_parquet(OUT_DIR / "c1_cell_units.parquet")
    khan = units[units["chem"] == "NMC_prism"].copy()
    khan["cell"] = khan["cell_traj"].str.replace("Khan_", "")
    conds = pd.read_csv(CONDITIONS_CSV)
    merged = khan.merge(conds, on="cell", how="inner")
    print(f"Khan units in C1: {len(khan)}")
    print(f"After condition merge: {len(merged)} (cells with both unit vector + condition)")
    missing = set(khan["cell"]) - set(merged["cell"])
    if missing:
        print(f"Khan cells without conditions: {sorted(missing)}")
    return merged


def cluster_summary(df, group_col, label=""):
    """Print group-level centroid directions + pairwise cosine angles."""
    print(f"\n=== Cluster summary by '{group_col}'{(' '+label) if label else ''} ===")
    grouped = []
    for grp_val, g in df.groupby(group_col):
        if len(g) < 1:
            continue
        u = g[["u1", "u2", "u3"]].values
        mean_u = u.mean(axis=0)
        mean_u_norm = mean_u / max(np.linalg.norm(mean_u), 1e-12)
        grouped.append({"group": str(grp_val), "n": len(g),
                        "centroid": mean_u_norm, "members": list(g["cell"].values)})
        print(f"  {str(grp_val):>20}  n={len(g):>2}  centroid=({mean_u_norm[0]:+.3f}, {mean_u_norm[1]:+.3f}, {mean_u_norm[2]:+.3f})  cells={list(g['cell'].values)}")
    if len(grouped) >= 2:
        print(f"\n  Pairwise centroid cosine angles:")
        for a, b in combinations(grouped, 2):
            cos = float(np.dot(a["centroid"], b["centroid"]))
            print(f"    {a['group']:>20} vs {b['group']:>20}: cos = {cos:+.3f}")
    return grouped


def permanova_pseudoF(u_mat, labels):
    """PERMANOVA-style pseudo-F on cosine-distance matrix.

    For each pair of cells, distance = 1 - cos(u_i, u_j). Pseudo-F = ratio of
    between-group SS to within-group SS, with degrees-of-freedom adjustment.
    """
    n = len(u_mat)
    # Normalize (should already be unit, but be safe)
    norms = np.linalg.norm(u_mat, axis=1, keepdims=True)
    u_mat = u_mat / np.where(norms < 1e-12, 1e-12, norms)
    # Cosine distance matrix
    cos_mat = u_mat @ u_mat.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    d_mat = 1.0 - cos_mat
    # PERMANOVA SS via Anderson 2001 formulation
    unique = np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan"), float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for u in unique:
        mask = (labels == u)
        n_u = mask.sum()
        if n_u < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_u)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan"), float("nan")
    F = (between_ss / (a - 1)) / (within_ss / (n - a))
    return F, total_ss


def permanova_test(u_mat, labels, n_perms=N_PERMS):
    """Return observed pseudo-F and permutation p-value."""
    F_obs, _ = permanova_pseudoF(u_mat, labels)
    if np.isnan(F_obs):
        return float("nan"), float("nan")
    n_ge = 0
    for _ in range(n_perms):
        perm = RNG.permutation(labels)
        F_perm, _ = permanova_pseudoF(u_mat, perm)
        if not np.isnan(F_perm) and F_perm >= F_obs:
            n_ge += 1
    p = (n_ge + 1) / (n_perms + 1)
    return F_obs, p


def main():
    print("=== C3 within-Khan: design-parameter inversion probe ===\n")
    df = load_khan_units_with_conditions()
    print("\n=== Cell-level table ===")
    print(df[["cell", "aging_type", "T_C", "soc_range", "charge_rate",
              "u1", "u2", "u3"]].to_string(
        index=False, float_format=lambda x: f"{x:+.3f}" if isinstance(x, float) else str(x)))

    # ===== Group 1: aging_type alone =====
    cluster_summary(df, "aging_type")
    u_all = df[["u1", "u2", "u3"]].values
    lbl = df["aging_type"].values
    F, p = permanova_test(u_all, lbl)
    print(f"\n  PERMANOVA (aging_type): pseudo-F = {F:.3f}, p = {p:.4f} (n_perm={N_PERMS})")

    # ===== Group 2: aging_type x T_C =====
    df["aging_T"] = df["aging_type"].astype(str) + "_T" + df["T_C"].astype(str)
    cluster_summary(df, "aging_T")
    lbl = df["aging_T"].values
    F, p = permanova_test(u_all, lbl)
    print(f"\n  PERMANOVA (aging_type x T_C): pseudo-F = {F:.3f}, p = {p:.4f} (n_perm={N_PERMS})")

    # ===== Group 3: cycle cells only by T_C =====
    cycle_df = df[df["aging_type"] == "cycle"].copy().reset_index(drop=True)
    print(f"\n--- Cycle-only sub-cohort: N={len(cycle_df)} ---")
    cluster_summary(cycle_df, "T_C", label="(cycle-only)")
    u_c = cycle_df[["u1", "u2", "u3"]].values
    lbl_c = cycle_df["T_C"].values
    F, p = permanova_test(u_c, lbl_c)
    print(f"\n  PERMANOVA (cycle-only, T_C): pseudo-F = {F:.3f}, p = {p:.4f} (n_perm={N_PERMS})")

    # ===== Group 4: cycle-25C cells by charge_rate (0.2C-CCCV vs 1C-CC) =====
    cycle25 = df[(df["aging_type"] == "cycle") & (df["T_C"] == 25)].copy().reset_index(drop=True)
    if len(cycle25) >= 4:
        print(f"\n--- Cycle-25C sub-cohort: N={len(cycle25)} ---")
        cluster_summary(cycle25, "charge_rate", label="(cycle-25C-only)")

    # ===== Group 5: cycle cells by SOC range =====
    cycle_only = df[df["aging_type"] == "cycle"].copy().reset_index(drop=True)
    cluster_summary(cycle_only, "soc_range", label="(cycle-only)")
    u_s = cycle_only[["u1", "u2", "u3"]].values
    lbl_s = cycle_only["soc_range"].values
    F, p = permanova_test(u_s, lbl_s)
    print(f"\n  PERMANOVA (cycle-only, soc_range): pseudo-F = {F:.3f}, p = {p:.4f} (n_perm={N_PERMS})")

    df.to_parquet(OUT_DIR / "c3_khan_units_with_conditions.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_khan_units_with_conditions.parquet'}")


if __name__ == "__main__":
    main()
