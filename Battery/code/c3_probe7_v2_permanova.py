"""C3 Probe 7 v2 — multi-variant PERMANOVA.

Pre-reg: literature/39_probe7_v2_prereg.md.

Runs five variants on the v2 EIS-augmented parquet:
  1. B5' EIS triad x N1 noise grid (PRIMARY for H7v2-primary)
  2. B5' EIS triad x N2 noise grid (secondary, H7v2-secondary-1)
  3. Fresh-state features x N1 noise grid (Probe 7.3, H7v2-secondary-2)
  4. B7 EIS triad x N1 noise grid (P7v2_F4 reproducibility -- should match v1 NULL)
  5. HPPC triad x N1 noise grid (P7v2_F4 reproducibility -- should match Probe 6 NULL)

Filters anchor_partial=True (matches v1 + Probe 6 convention). N=101 expected.
"""

from pathlib import Path
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v2.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")

N_PERMS = 10000
ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05
TARGET_SOH = 0.92

# Noise grids
N1_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.00, "sigma_Rd": 0.00, "name": "N1-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.05, "sigma_Rd": 0.10, "name": "N1-L1 best lab"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.15, "sigma_Rd": 0.20, "name": "N1-L2 PRIMARY"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.30, "sigma_Rd": 0.30, "name": "N1-L3 noisy field"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.50, "sigma_Rd": 0.50, "name": "N1-L4 instrument issue"},
]
N2_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.000, "sigma_Rd": 0.00, "name": "N2-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.010, "sigma_Rd": 0.05, "name": "N2-L1 best-in-class EIS"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.030, "sigma_Rd": 0.15, "name": "N2-L2 typical academic EIS"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.100, "sigma_Rd": 0.25, "name": "N2-L3 field-grade EIS"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.200, "sigma_Rd": 0.40, "name": "N2-L4 degraded instrument"},
]

N1_SEED_BASE = 2000  # matches Probe 6
N2_SEED_BASE = 3000  # separate seed family for N2


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


def build_eis_triad_table(df_raw, aged_R_ohmic_col, aged_R_diff_col, aged_Q_col="anchor_aged_Q"):
    """Build per-cell clean fresh+aged operator table, filtering anchor_partial."""
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        if pd.isna(row.get(aged_R_ohmic_col)) or pd.isna(row.get(aged_R_diff_col)):
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
            "aged_Q": float(row[aged_Q_col]),
            "aged_R_ohmic": float(row[aged_R_ohmic_col]),
            "aged_R_diff": float(row[aged_R_diff_col]),
        })
    return pd.DataFrame(rows)


def build_hppc_triad_table(df_raw):
    """HPPC triad with uniform-anchor Q. Same logic as c3_noise_injection.build_clean_operator_table."""
    import json
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        rpts = json.loads(row["rpts_json"]) if isinstance(row["rpts_json"], str) else row["rpts_json"]
        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            continue
        fresh_Q = float(np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(np.mean([r["R_total"] for r in fresh_rpts]))
        post = [r for r in rpts if r["cycle"] > 25]
        if not post:
            continue
        target_Q = TARGET_SOH * fresh_Q
        best = min(post, key=lambda r: abs(r["Q_max"] - target_Q))
        soh = best["Q_max"] / fresh_Q
        if abs(soh - TARGET_SOH) > 0.02:  # anchor_partial filter
            continue
        rows.append({
            "cond_idx": int(row["cond_idx"]),
            "cell_idx": int(row["cell_idx"]),
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": fresh_Q,
            "fresh_R_ohmic": fresh_R_DC,    # repurposing field names for triad agnosticism
            "fresh_R_diff": fresh_R_total,
            "aged_Q": float(best["Q_max"]),
            "aged_R_ohmic": float(best["R_DC"]),
            "aged_R_diff": float(best["R_total"]),
        })
    return pd.DataFrame(rows)


def inject_noise_unit_residual(df_clean, sigma_Q, sigma_Ro, sigma_Rd, level, seed_base):
    """Same as c3_noise_injection inject_noise_and_standardize."""
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps = {k: np.empty(n) for k in ["fq", "fo", "fd", "aq", "ao", "ad"]}
    for i, row in df.iterrows():
        s = seed_base + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
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
    raw_resid = df[["aQ_n", "aRo_n", "aRd_n"]].values - df[["fQ_n", "fRo_n", "fRd_n"]].values
    fresh_pool = df[["fQ_n", "fRo_n", "fRd_n"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    df["u1"] = u[:, 0]
    df["u2"] = u[:, 1]
    df["u3"] = u[:, 2]
    return df


def inject_noise_unit_freshstate(df_clean, sigma_Q, sigma_Ro, sigma_Rd, level, seed_base):
    """Probe 7.3: PERMANOVA on absolute fresh-state features (not residuals)."""
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps = {k: np.empty(n) for k in ["fq", "fo", "fd"]}
    for i, row in df.iterrows():
        s = seed_base + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(s)
        eps["fq"][i] = rng.normal(0, sigma_Q)
        eps["fo"][i] = rng.normal(0, sigma_Ro)
        eps["fd"][i] = rng.normal(0, sigma_Rd)
    df["fQ_n"] = df["fresh_Q"] * (1 + eps["fq"])
    df["fRo_n"] = df["fresh_R_ohmic"] * (1 + eps["fo"])
    df["fRd_n"] = df["fresh_R_diff"] * (1 + eps["fd"])
    feats = df[["fQ_n", "fRo_n", "fRd_n"]].values
    pooled_sd = feats.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = (feats - feats.mean(axis=0)) / pooled_sd  # also center to make unit projection meaningful
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    df["u1"] = u[:, 0]
    df["u2"] = u[:, 1]
    df["u3"] = u[:, 2]
    return df


def run_permanova_grid(df_clean, noise_levels, seed_base, variant_label, project_fn=inject_noise_unit_residual):
    print(f"\n========== {variant_label} ==========")
    print(f"N cells (post-filter): {len(df_clean)}")
    summary_rows = []
    for nl in noise_levels:
        df_noisy = project_fn(df_clean, nl["sigma_Q"], nl["sigma_Ro"], nl["sigma_Rd"], nl["level"], seed_base)
        u_mat = df_noisy[["u1", "u2", "u3"]].values
        rng_p = np.random.default_rng(seed_base + 999000 + nl["level"])
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
        print(f"  {nl['name']:32s} | "
              f"th: F={Fs['thickness_level']:6.2f} p={ps['thickness_level']:.4f} {verdicts['thickness_level']:9s} | "
              f"tn: F={Fs['transference_level']:6.2f} p={ps['transference_level']:.4f} {verdicts['transference_level']:9s} | "
              f"pr: F={Fs['particle_radius_level']:6.2f} p={ps['particle_radius_level']:.4f} {verdicts['particle_radius_level']:9s} | {lv}")
        summary_rows.append({
            "variant": variant_label,
            "level": nl["level"],
            "name": nl["name"],
            "sigma_Q": nl["sigma_Q"],
            "sigma_Ro": nl["sigma_Ro"],
            "sigma_Rd": nl["sigma_Rd"],
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
    print(f"=== Probe 7 v2 -- multi-variant PERMANOVA (pre-reg literature/39) ===")
    df_raw = pd.read_parquet(IN_PARQUET)
    print(f"\nParquet rows: {len(df_raw)} | Successful sims: {df_raw['error'].isna().sum()}")

    all_summaries = []

    # Variant 1: B5' EIS x N1 (PRIMARY)
    df_b5 = build_eis_triad_table(df_raw, "R_ohmic_aged_b5", "R_diff_aged_b5")
    s1 = run_permanova_grid(df_b5, N1_LEVELS, N1_SEED_BASE, "B5' EIS triad x N1 (PRIMARY)")
    all_summaries.append(s1)

    # Variant 2: B5' EIS x N2 (secondary)
    s2 = run_permanova_grid(df_b5, N2_LEVELS, N2_SEED_BASE, "B5' EIS triad x N2 (EIS-realistic)")
    all_summaries.append(s2)

    # Variant 3: Fresh-state features x N1 (Probe 7.3 secondary)
    s3 = run_permanova_grid(df_b5, N1_LEVELS, N1_SEED_BASE, "Fresh-state features x N1 (Probe 7.3)",
                             project_fn=inject_noise_unit_freshstate)
    all_summaries.append(s3)

    # Variant 4: B7 EIS x N1 (P7v2_F4 reproducibility -- expect 0/3 at L2 matching v1 lit/38)
    df_b7 = build_eis_triad_table(df_raw, "R_ohmic_aged_b7", "R_diff_aged_b7")
    s4 = run_permanova_grid(df_b7, N1_LEVELS, N1_SEED_BASE, "B7 EIS triad x N1 (P7v2_F4 v1-repro)")
    all_summaries.append(s4)

    # Variant 5: HPPC x N1 (P7v2_F4 reproducibility -- expect 0/3 at L2 matching lit/26)
    df_hppc = build_hppc_triad_table(df_raw)
    s5 = run_permanova_grid(df_hppc, N1_LEVELS, N1_SEED_BASE, "HPPC triad x N1 (P7v2_F4 Probe6-repro)")
    all_summaries.append(s5)

    summary = pd.concat(all_summaries, ignore_index=True)
    out = OUT_DIR / "probe7_v2_permanova_results.parquet"
    summary.to_parquet(out)
    print(f"\nAll variant results written: {out}")

    # Print disposition headlines
    print(f"\n\n========== PROBE 7 v2 HEADLINES ==========")
    for v in summary["variant"].unique():
        sv = summary[(summary["variant"] == v) & (summary["level"] == 2)].iloc[0]
        n_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "PASS")
        print(f"  {v}: {n_pass}/3 PASS at Level 2 -- {sv['level_verdict']}")


if __name__ == "__main__":
    main()
