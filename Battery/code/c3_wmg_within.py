"""
C3 Probe 3 — WMG within-cohort PERMANOVA, pre-registered.

Pre-reg: literature/16_c3_pre_registration.md (commit 1ef1b94, locked 2026-05-21).

Operates on data/processed/wmg_25cell_classification.parquet (produced by
code/wmg_extract_features.py).

Per pre-reg §2 Probe 3:
  - Use existing per-cell residual unit vectors (u_Q_max, u_R_ohmic, u_R_diff)
  - 19 aged cells; 5 100SOH controls excluded (they ARE the fresh reference)

Per pre-reg §3 Probe 3:
  - Groups = 4 terminal-SOH bins: {80%, 85%, 90%, 95%}
  - n = {5, 5, 4, 5}

Per pre-reg §4-5:
  - PERMANOVA pseudo-F on cosine-distance
  - 10000 perms
  - Bonferroni alpha/2 = 0.025
  - Effect floor pseudo-F > 3.0

  H3 PASS:        p<0.025 AND pseudo-F>3.0
  H3 WEAK PASS:   p in [0.025, 0.05] OR pseudo-F in [2.0, 3.0]
  H3 NULL:        p>=0.05 OR pseudo-F<2.0

H3 = "residual direction is reproducible at a given aging stage" framework
coherence test. Not a C3 replication (no design-parameter variation within WMG).
"""

from pathlib import Path
import numpy as np
import pandas as pd


OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG = np.random.default_rng(seed=42)
N_PERMS = 10000

ALPHA_BONFERRONI = 0.025
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


def verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "H3 INVALID: NaN test statistic"
    if p < ALPHA_BONFERRONI and F > EFFECT_F_FLOOR:
        return "H3 PASS"
    if (p < ALPHA_BONFERRONI and F > EFFECT_F_WEAK) or (p < ALPHA_WEAK and F > EFFECT_F_FLOOR):
        return "H3 WEAK PASS"
    if p < ALPHA_WEAK and F > EFFECT_F_WEAK:
        return "H3 WEAK PASS"
    return "H3 NULL"


def main():
    print("=== C3 Probe 3 — WMG within-cohort PERMANOVA (pre-reg literature/16) ===\n")
    df = pd.read_parquet(OUT_DIR / "wmg_25cell_classification.parquet")
    print(f"WMG cells in parquet: {len(df)}")

    soh_counts = df.groupby("soh_eis").size().to_dict()
    print(f"\nPer-SOH cell counts: {soh_counts}")

    u = df[["u_Q_max", "u_R_ohmic", "u_R_diff"]].values
    labels = df["soh_eis"].astype(str).values

    print(f"\nPER-BIN CENTROID DIRECTIONS:")
    for soh, g in df.groupby("soh_eis"):
        uu = g[["u_Q_max", "u_R_ohmic", "u_R_diff"]].values
        c = uu.mean(axis=0)
        c_n = c / max(np.linalg.norm(c), 1e-12)
        print(f"  SOH={int(soh)}% (n={len(g)}): centroid = ({c_n[0]:+.3f}, {c_n[1]:+.3f}, {c_n[2]:+.3f})")

    F, p = permanova_test(u, labels)
    print(f"\nPERMANOVA on 4 SOH bins:")
    print(f"  pseudo-F = {F:.3f}")
    print(f"  p (10000 perm) = {p:.4f}")
    print(f"  Bonferroni alpha/2 = {ALPHA_BONFERRONI}")
    print(f"  Effect-size floor = {EFFECT_F_FLOOR}")
    print(f"\nVERDICT: {verdict(F, p)}")


if __name__ == "__main__":
    main()
