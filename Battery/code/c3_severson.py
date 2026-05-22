"""
C3 Probe 2 — Severson within-cohort PERMANOVA, pre-registered.

Pre-reg: literature/16_c3_pre_registration.md (commit 1ef1b94, locked 2026-05-21).

Operates on data/processed/severson_extracted.parquet (produced by
code/severson_extract_features.py per pre-reg §2).

Primary test (pre-reg §4):
  - Group cells by first-step C-rate into 3 LOCKED bins:
      A: <4.5C   B: [4.5, 6.0)   C: >=6.0
  - PERMANOVA pseudo-F (Anderson 2001) on cosine-distance matrix of unit
    residual vectors
  - Null: 10000 permutations of bin labels
  - Bonferroni alpha/2 = 0.025
  - Effect-size floor: pseudo-F > 3.0

Robustness (pre-reg §7): also report batch-stratified PERMANOVA per batch.

Locked re-binning contingency (pre-reg §3): if any locked bin has n<6, re-run
on TERTILE cuts of empirical first-step C-rate distribution. Report locked
AND tertile results side-by-side. Locked-bin result remains primary verdict.

Inclusion: per pre-reg §6, cells already filtered by the extractor's logic
(>=5 fresh cycles AND (>=80% SOH crossed OR >=100 cycles total)). Cells
that didn't reach 80% SOH are flagged partial_aging but INCLUDED (they
satisfied the alt-clause).

Falsification verdicts (pre-reg §5):
  H2 PASS:        p<0.025 AND pseudo-F>3.0 AND >=2/3 bins with n>=8
  H2 WEAK PASS:   p in [0.025, 0.05] OR pseudo-F in [2.0, 3.0]
  H2 NULL:        p>=0.05 OR pseudo-F<2.0
  H2 INVALID:     extraction failures, n_total<60, any bin n<3
"""

from pathlib import Path
import numpy as np
import pandas as pd


OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG = np.random.default_rng(seed=42)
N_PERMS = 10000

# Pre-reg §3 locked bins
LOCKED_BIN_EDGES = [(None, 4.5, "A: <4.5C"),
                    (4.5, 6.0,  "B: [4.5, 6.0)"),
                    (6.0, None, "C: >=6.0")]

# Pre-reg §4-5 thresholds
ALPHA_BONFERRONI = 0.025
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05
MIN_BINS_AT_8 = 2
MIN_BIN_N_FOR_VALID = 3
MIN_TOTAL_N = 60
TARGET_TOTAL_N = 90


def assign_locked_bin(c):
    """Assign a first-step C-rate value to one of the 3 locked bins."""
    if not np.isfinite(c):
        return None
    for lo, hi, name in LOCKED_BIN_EDGES:
        if (lo is None or c >= lo) and (hi is None or c < hi):
            return name
    return None


def compute_unit_residuals(df):
    """Compute per-cell unit residual vectors against pooled-fresh standardization.

    Per pre-reg §2: subtract per-cell fresh ref from aged snapshot, standardize each
    operator dimension by pooled cross-cell standard deviation of fresh-reference
    values, normalize the resulting 3-vector to unit length.

    Returns df with added columns: z_Q, z_R, z_T, u1, u2, u3.
    """
    raw_resid = df[["aged_Q", "aged_R", "aged_T_amp"]].values - \
                df[["fresh_Q", "fresh_R", "fresh_T_amp"]].values
    fresh_pool = df[["fresh_Q", "fresh_R", "fresh_T_amp"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    out = df.copy()
    out["z_Q"] = z[:, 0]
    out["z_R"] = z[:, 1]
    out["z_T"] = z[:, 2]
    out["u1"] = u[:, 0]
    out["u2"] = u[:, 1]
    out["u3"] = u[:, 2]
    out["mahal"] = norms.flatten()
    return out


def permanova_pseudoF(u_mat, labels):
    """Anderson 2001 pseudo-F on cosine-distance matrix."""
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
    p = (n_ge + 1) / (n_perms + 1)
    return F_obs, p


def verdict(F, p, bin_counts, n_total):
    """Apply pre-reg §5 falsification thresholds."""
    if n_total < MIN_TOTAL_N:
        return f"H2 INVALID: n_total={n_total} < {MIN_TOTAL_N} floor"
    min_bin = min(bin_counts.values()) if bin_counts else 0
    if min_bin < MIN_BIN_N_FOR_VALID:
        return f"H2 INVALID: smallest bin n={min_bin} < {MIN_BIN_N_FOR_VALID}"
    bins_at_8 = sum(1 for n in bin_counts.values() if n >= 8)
    if not np.isfinite(F) or not np.isfinite(p):
        return "H2 INVALID: PERMANOVA returned NaN"

    f_pass = F > EFFECT_F_FLOOR
    f_weak = F > EFFECT_F_WEAK
    p_pass = p < ALPHA_BONFERRONI
    p_weak = p < ALPHA_WEAK

    if p_pass and f_pass and bins_at_8 >= MIN_BINS_AT_8:
        return "H2 PASS"
    if (p_pass and f_pass and bins_at_8 < MIN_BINS_AT_8):
        return "H2 WEAK PASS (bin-balance below threshold)"
    if p_weak and f_weak:
        return "H2 WEAK PASS"
    return "H2 NULL"


def main():
    print("=== C3 Probe 2 — Severson within-cohort PERMANOVA (pre-reg literature/16) ===\n")
    df_raw = pd.read_parquet(OUT_DIR / "severson_extracted.parquet")
    print(f"Extracted cells: {len(df_raw)}")
    print(f"  Reached 80% SOH:      {(~df_raw['partial_aging']).sum()}")
    print(f"  Flagged partial_aging: {df_raw['partial_aging'].sum()}")

    # Cells with valid first_step_C only
    df_raw = df_raw[np.isfinite(df_raw["first_step_C"])].copy()
    df_raw = df_raw[np.isfinite(df_raw["fresh_Q"]) & np.isfinite(df_raw["aged_Q"])].copy()
    df_raw = df_raw[np.isfinite(df_raw["fresh_R"]) & np.isfinite(df_raw["aged_R"])].copy()
    df_raw = df_raw[np.isfinite(df_raw["fresh_T_amp"]) & np.isfinite(df_raw["aged_T_amp"])].copy()
    print(f"After dropping NaN/missing operators: {len(df_raw)}")

    df = compute_unit_residuals(df_raw)
    df["bin_locked"] = df["first_step_C"].apply(assign_locked_bin)

    # === Primary test (locked bins, pooled) ===
    print("\n=== PRIMARY: locked-bin PERMANOVA (pooled across batches) ===")
    locked_counts = df.groupby("bin_locked").size().to_dict()
    for lo, hi, name in LOCKED_BIN_EDGES:
        n = locked_counts.get(name, 0)
        print(f"  {name}: n={n}")
    u = df[["u1", "u2", "u3"]].values
    F_locked, p_locked = permanova_test(u, df["bin_locked"].values)
    print(f"\n  pseudo-F = {F_locked:.3f}")
    print(f"  p (10000 perm) = {p_locked:.4f}")
    print(f"  Bonferroni alpha/2 = {ALPHA_BONFERRONI}")
    print(f"  Effect-size floor = {EFFECT_F_FLOOR}")
    v = verdict(F_locked, p_locked, locked_counts, len(df))
    print(f"\n  VERDICT (locked bins, primary): {v}")

    # === Batch-stratified ===
    print("\n=== Batch-stratified (robustness) ===")
    for batch, g in df.groupby("batch_date"):
        g_counts = g.groupby("bin_locked").size().to_dict()
        if len(g) < 3 or len(g_counts) < 2:
            print(f"  Batch {batch}: n={len(g)}, insufficient for stratified test")
            continue
        ug = g[["u1", "u2", "u3"]].values
        F_b, p_b = permanova_test(ug, g["bin_locked"].values)
        print(f"  Batch {batch}: n={len(g)}, pseudo-F={F_b:.3f}, p={p_b:.4f}")
        for lo, hi, name in LOCKED_BIN_EDGES:
            n = g_counts.get(name, 0)
            print(f"    {name}: n={n}")

    # === Contingency: re-binning if any locked bin n<6 ===
    print("\n=== Locked-bin contingency check ===")
    min_locked_bin = min(locked_counts.values()) if locked_counts else 0
    if min_locked_bin < 6:
        print(f"  Locked-bin minimum n = {min_locked_bin} < 6 — re-binning permitted per pre-reg §3.")
        print(f"  Triggering tertile re-bin on observed first-step C-rate distribution.")
        fc = df["first_step_C"].values
        t33 = float(np.percentile(fc, 33.33))
        t67 = float(np.percentile(fc, 66.67))
        df["bin_tertile"] = np.where(df["first_step_C"] < t33, "T1",
                              np.where(df["first_step_C"] < t67, "T2", "T3"))
        tert_counts = df.groupby("bin_tertile").size().to_dict()
        print(f"\n  Tertile cuts: 33rd={t33:.3f}C, 67th={t67:.3f}C")
        print(f"  T1 (<{t33:.3f}C):  n={tert_counts.get('T1', 0)}")
        print(f"  T2 (<{t67:.3f}C):  n={tert_counts.get('T2', 0)}")
        print(f"  T3 (>={t67:.3f}C): n={tert_counts.get('T3', 0)}")
        F_t, p_t = permanova_test(df[["u1", "u2", "u3"]].values, df["bin_tertile"].values)
        print(f"\n  Tertile PERMANOVA: pseudo-F={F_t:.3f}, p={p_t:.4f}")
        print(f"  NOTE: Per pre-reg, tertile result is robustness/secondary — locked-bin verdict stands as primary.")
    else:
        print(f"  Locked-bin minimum n = {min_locked_bin} >= 6 — no re-binning trigger.")

    # Save
    df.to_parquet(OUT_DIR / "c3_severson_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_severson_results.parquet'}")


if __name__ == "__main__":
    main()
