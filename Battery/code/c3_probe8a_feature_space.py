"""C3 Probe 8a — feature-space decomposition.

Pre-reg: literature/41_probe8a_prereg.md.

Runs 5 feature-space variants on the v2 EIS-augmented parquet at the
N1 noise grid, same cosine-PERMANOVA architecture as Probe 5/6/7:

  (i)   Residuals only (3D) -- the current C3 architecture
  (ii)  Aged absolute only (3D)
  (iii) Fresh absolute only (3D) -- Probe 7.3 reproduction
  (iv)  Fresh + aged stacked (6D)
  (v)   Fresh + residual stacked (6D)

Variant (i) at Level 2 MUST reproduce v2 PRIMARY (0/3 PASS).
Variant (iii) at Level 2 MUST reproduce v2 Probe 7.3 (2/3 PASS).
Other variants are the new evidence.

Headline: does feature-space choice carry the Level-2 survival?
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v2.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")

N_PERMS = 10000
ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05

N1_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.00, "sigma_Rd": 0.00, "name": "N1-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.05, "sigma_Rd": 0.10, "name": "N1-L1 best lab"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.15, "sigma_Rd": 0.20, "name": "N1-L2 PRIMARY"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.30, "sigma_Rd": 0.30, "name": "N1-L3 noisy field"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.50, "sigma_Rd": 0.50, "name": "N1-L4 instrument issue"},
]

RNG_SEED_BASE = 2000  # identical to v1 + v2 N1


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


def permanova_test(u_mat, labels, rng, n_perms=N_PERMS):
    F_obs = permanova_pseudoF(u_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
        F_p = permanova_pseudoF(u_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def parameter_verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > EFFECT_F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > EFFECT_F_WEAK:
        return "WEAK PASS"
    return "NULL"


def level_verdict(verdicts):
    n_pass = sum(1 for v in verdicts.values() if v == "PASS")
    n_weak = sum(1 for v in verdicts.values() if v == "WEAK PASS")
    if n_pass >= 2:
        return "LEVEL ROBUST"
    if n_pass == 1 and n_weak >= 1:
        return "LEVEL WEAK"
    if n_pass == 1:
        return "LEVEL WEAK"
    return "LEVEL COLLAPSED"


def build_clean_table(df_raw):
    """106 sim-success - 5 anchor_partial = 101 cells. Same filter as v2 PRIMARY."""
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        if pd.isna(row.get("R_ohmic_aged_b5")) or pd.isna(row.get("R_diff_aged_b5")):
            continue
        if row.get("anchor_partial") is True:
            continue
        rows.append({
            "cond_idx": int(row["cond_idx"]),
            "cell_idx": int(row["cell_idx"]),
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": float(row["fresh_Q"]),
            "fresh_R_ohmic": float(row["R_ohmic_fresh"]),
            "fresh_R_diff": float(row["R_diff_fresh"]),
            "aged_Q": float(row["anchor_aged_Q"]),
            "aged_R_ohmic": float(row["R_ohmic_aged_b5"]),
            "aged_R_diff": float(row["R_diff_aged_b5"]),
        })
    return pd.DataFrame(rows)


def apply_noise(df_clean, sigma_Q, sigma_Ro, sigma_Rd, level):
    """Multiplicative Gaussian noise on each fresh + aged absolute value.
    Same seed structure as c3_noise_injection.py / c3_probe7_eis_permanova.py /
    c3_probe7_v2_permanova.py."""
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps = {k: np.empty(n) for k in ["fq", "fo", "fd", "aq", "ao", "ad"]}
    for i, row in df.iterrows():
        s = RNG_SEED_BASE + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(s)
        eps["fq"][i] = rng.normal(0, sigma_Q)
        eps["fo"][i] = rng.normal(0, sigma_Ro)
        eps["fd"][i] = rng.normal(0, sigma_Rd)
        eps["aq"][i] = rng.normal(0, sigma_Q)
        eps["ao"][i] = rng.normal(0, sigma_Ro)
        eps["ad"][i] = rng.normal(0, sigma_Rd)
    df["fQ_n"] = df["fresh_Q"] * (1 + eps["fq"])
    df["fRo_n"] = df["fresh_R_ohmic"] * (1 + eps["fo"])
    df["fRd_n"] = df["fresh_R_diff"] * (1 + eps["fd"])
    df["aQ_n"] = df["aged_Q"] * (1 + eps["aq"])
    df["aRo_n"] = df["aged_R_ohmic"] * (1 + eps["ao"])
    df["aRd_n"] = df["aged_R_diff"] * (1 + eps["ad"])
    return df


def build_feature_matrix(df_noisy, variant):
    """Build the feature matrix for a given variant (pre-z-score, pre-projection)."""
    if variant == "i_residual":
        feats = df_noisy[["aQ_n", "aRo_n", "aRd_n"]].values - df_noisy[["fQ_n", "fRo_n", "fRd_n"]].values
        center = False  # residuals don't need centering (they're already "relative to fresh")
    elif variant == "ii_aged_abs":
        feats = df_noisy[["aQ_n", "aRo_n", "aRd_n"]].values
        center = True  # absolute features need centering for unit-vector projection
    elif variant == "iii_fresh_abs":
        feats = df_noisy[["fQ_n", "fRo_n", "fRd_n"]].values
        center = True
    elif variant == "iv_fresh_aged_stack":
        feats = df_noisy[["fQ_n", "fRo_n", "fRd_n", "aQ_n", "aRo_n", "aRd_n"]].values
        center = True
    elif variant == "v_fresh_resid_stack":
        # First 3 cols = fresh absolute; last 3 cols = residuals
        fresh = df_noisy[["fQ_n", "fRo_n", "fRd_n"]].values
        resid = df_noisy[["aQ_n", "aRo_n", "aRd_n"]].values - fresh
        feats = np.hstack([fresh, resid])
        center = True
    else:
        raise ValueError(f"Unknown variant: {variant}")
    return feats, center


def project_unit_vector(feats, center):
    """Z-score + center (if center=True) + unit-vector projection."""
    if center:
        feats = feats - feats.mean(axis=0, keepdims=True)
    pooled_sd = feats.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    # Use the raw (uncentered) SD for z-scoring if residuals; centered SD otherwise.
    # For residuals, the cohort SD is what makes sense for noise-comparability.
    z = feats / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    return u


def run_variant(df_clean, variant_label, noise_levels):
    print(f"\n========== Variant {variant_label} ==========")
    summary_rows = []
    for nl in noise_levels:
        df_noisy = apply_noise(df_clean, nl["sigma_Q"], nl["sigma_Ro"], nl["sigma_Rd"], nl["level"])
        feats, center = build_feature_matrix(df_noisy, variant_label)
        u_mat = project_unit_vector(feats, center)
        rng_p = np.random.default_rng(RNG_SEED_BASE + 999000 + nl["level"])
        verdicts = {}
        Fs = {}
        ps = {}
        for param_col in ["thickness_level", "transference_level", "particle_radius_level"]:
            F, p = permanova_test(u_mat, df_noisy[param_col].values, rng_p)
            v = parameter_verdict(F, p)
            verdicts[param_col] = v
            Fs[param_col] = F
            ps[param_col] = p
        lv = level_verdict(verdicts)
        print(f"  {nl['name']:25s} | "
              f"th: F={Fs['thickness_level']:7.2f} p={ps['thickness_level']:.4f} {verdicts['thickness_level']:9s} | "
              f"tn: F={Fs['transference_level']:7.2f} p={ps['transference_level']:.4f} {verdicts['transference_level']:9s} | "
              f"pr: F={Fs['particle_radius_level']:7.2f} p={ps['particle_radius_level']:.4f} {verdicts['particle_radius_level']:9s} | {lv}")
        summary_rows.append({
            "variant": variant_label,
            "level": nl["level"],
            "name": nl["name"],
            "F_thickness": Fs["thickness_level"],
            "p_thickness": ps["thickness_level"],
            "F_transference": Fs["transference_level"],
            "p_transference": ps["transference_level"],
            "F_particle": Fs["particle_radius_level"],
            "p_particle": ps["particle_radius_level"],
            "verdict_thickness": verdicts["thickness_level"],
            "verdict_transference": verdicts["transference_level"],
            "verdict_particle": verdicts["particle_radius_level"],
            "level_verdict": lv,
        })
    return pd.DataFrame(summary_rows)


def main():
    print(f"=== Probe 8a -- feature-space decomposition (pre-reg literature/41) ===")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_clean = build_clean_table(df_raw)
    print(f"\nClean cells (anchor_partial filtered): {len(df_clean)} (expected 101)")
    if len(df_clean) != 101:
        print(f"  WARN: expected 101 cells, got {len(df_clean)}; comparison to v2 PRIMARY may not be bit-identical")

    variants = ["i_residual", "ii_aged_abs", "iii_fresh_abs", "iv_fresh_aged_stack", "v_fresh_resid_stack"]
    all_summaries = []
    for v in variants:
        s = run_variant(df_clean, v, N1_LEVELS)
        all_summaries.append(s)

    summary = pd.concat(all_summaries, ignore_index=True)
    out = OUT_DIR / "probe8a_feature_space_results.parquet"
    summary.to_parquet(out)
    print(f"\nAll variant results written: {out}")

    # Headline: Level 2 per variant
    print(f"\n\n========== PROBE 8a HEADLINES (Level 2) ==========")
    pass_counts = {}
    for v in variants:
        sv = summary[(summary["variant"] == v) & (summary["level"] == 2)].iloc[0]
        n_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "PASS")
        n_weak = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "WEAK PASS")
        pass_counts[v] = (n_pass, n_weak)
        print(f"  {v:25s}: {n_pass} PASS + {n_weak} WEAK -- {sv['level_verdict']}")

    # Disposition
    print(f"\n========== DISPOSITION ==========")
    i_collapse = pass_counts["i_residual"][0] == 0
    iii_pass = pass_counts["iii_fresh_abs"][0] >= 2
    other_pass = any(pass_counts[v][0] >= 2 for v in ["ii_aged_abs", "iv_fresh_aged_stack", "v_fresh_resid_stack"])
    if not i_collapse:
        print(f"  PROBE 8a INVALID: variant (i) did NOT reproduce v2 PRIMARY 0/3 at L2 -- F1 falsifier triggered")
    elif not iii_pass:
        print(f"  PROBE 8a INVALID: variant (iii) did NOT reproduce v2 Probe 7.3 (>=2/3 at L2) -- F2 falsifier triggered")
    elif other_pass:
        print(f"  FEATURE-SPACE IS THE DIVIDING LINE: variant (i) NULL + at least one of (ii)/(iv)/(v) PASS at L2.")
        print(f"  Feature-space is at least one load-bearing architectural component.")
    else:
        print(f"  FEATURE-SPACE IS PARTIAL: variant (i) NULL + variant (iii) PASS but (ii)/(iv)/(v) all NULL at L2.")
        print(f"  Fresh-state specifically rescues; generic feature-space changes don't.")


if __name__ == "__main__":
    main()
