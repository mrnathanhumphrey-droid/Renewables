"""C3 Probe 8b — distance-metric decomposition.

Pre-reg: literature/43_probe8b_prereg.md.

Tests three distance metrics on the winning Probe 8a feature space
(variant iv: fresh + aged 6D stacked) at N1 noise grid:

  - Cosine (baseline, reproduces 8a variant iv)
  - Euclidean
  - Mahalanobis (pooled within-condition covariance)

Question: does Mahalanobis recover transference signal that cosine
misses, and/or improve th+pr F-values?
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

N1_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.00, "sigma_Rd": 0.00, "name": "N1-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.05, "sigma_Rd": 0.10, "name": "N1-L1 best lab"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.15, "sigma_Rd": 0.20, "name": "N1-L2 PRIMARY"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.30, "sigma_Rd": 0.30, "name": "N1-L3 noisy field"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.50, "sigma_Rd": 0.50, "name": "N1-L4 instrument issue"},
]

RNG_SEED_BASE = 2000


def build_clean_table(df_raw):
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


def build_variant_iv_features(df_noisy):
    """Fresh + aged stacked, centered + z-scored."""
    feats = df_noisy[["fQ_n", "fRo_n", "fRd_n", "aQ_n", "aRo_n", "aRd_n"]].values
    feats = feats - feats.mean(axis=0, keepdims=True)
    pooled_sd = feats.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = feats / pooled_sd
    return z


def dist_cosine(z):
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = u @ u.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    return 1.0 - cos_mat


def dist_euclidean(z):
    diff = z[:, None, :] - z[None, :, :]
    return np.linalg.norm(diff, axis=-1)


def dist_mahalanobis(z, labels):
    """Pooled within-condition covariance Mahalanobis distance."""
    labels = np.asarray(labels)
    unique = np.unique(labels)
    a = len(unique)
    n, d = z.shape
    pooled_S = np.zeros((d, d))
    df_total = 0
    for g in unique:
        mask = labels == g
        n_g = int(mask.sum())
        if n_g < 2:
            continue
        z_g = z[mask]
        centroid = z_g.mean(axis=0, keepdims=True)
        diffs = z_g - centroid
        pooled_S += diffs.T @ diffs
        df_total += n_g - 1
    if df_total <= 0:
        return None, "df_total<=0"
    pooled_S /= df_total
    cond = np.linalg.cond(pooled_S)
    flag = None
    if cond > 1e10:
        flag = f"cond={cond:.2e}, pinv fallback"
        S_inv = np.linalg.pinv(pooled_S)
    else:
        try:
            S_inv = np.linalg.inv(pooled_S)
        except np.linalg.LinAlgError:
            flag = "LinAlgError, pinv fallback"
            S_inv = np.linalg.pinv(pooled_S)
    # Pairwise Mahalanobis distance
    diff = z[:, None, :] - z[None, :, :]
    # d^2 = (diff)^T S_inv (diff) per pair
    # Vectorized: d^2[i,j] = sum_{kl} diff[i,j,k] * S_inv[k,l] * diff[i,j,l]
    tmp = diff @ S_inv  # shape (n, n, d)
    d_sq = np.einsum("ijk,ijk->ij", tmp, diff)
    d_sq = np.maximum(d_sq, 0.0)  # numerical safety
    return np.sqrt(d_sq), flag


def permanova_pseudoF_from_dist(d_mat, labels):
    n = len(d_mat)
    labels = np.asarray(labels)
    unique = np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for g in unique:
        mask = labels == g
        n_g = int(mask.sum())
        if n_g < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_g)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan")
    return (between_ss / (a - 1)) / (within_ss / (n - a))


def permanova_test_dist(d_mat, labels, rng, n_perms=N_PERMS):
    F_obs = permanova_pseudoF_from_dist(d_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
        F_p = permanova_pseudoF_from_dist(d_mat, perm)
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


def run_metric(df_clean, metric_label, noise_levels):
    print(f"\n========== Metric {metric_label} ==========")
    summary_rows = []
    mahalanobis_flags = []
    for nl in noise_levels:
        df_noisy = apply_noise(df_clean, nl["sigma_Q"], nl["sigma_Ro"], nl["sigma_Rd"], nl["level"])
        z = build_variant_iv_features(df_noisy)
        rng_p = np.random.default_rng(RNG_SEED_BASE + 999000 + nl["level"])
        verdicts = {}
        Fs = {}
        ps = {}
        for param_col in ["thickness_level", "transference_level", "particle_radius_level"]:
            if metric_label == "cosine":
                d_mat = dist_cosine(z)
            elif metric_label == "euclidean":
                d_mat = dist_euclidean(z)
            elif metric_label == "mahalanobis":
                d_mat, flag = dist_mahalanobis(z, df_noisy[param_col].values)
                if flag:
                    mahalanobis_flags.append((nl["level"], param_col, flag))
            else:
                raise ValueError(metric_label)
            F, p = permanova_test_dist(d_mat, df_noisy[param_col].values, rng_p)
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
            "metric": metric_label,
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
    if mahalanobis_flags:
        print(f"  Mahalanobis flags raised: {mahalanobis_flags}")
    return pd.DataFrame(summary_rows)


def main():
    print(f"=== Probe 8b -- distance-metric decomposition (pre-reg literature/43) ===")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_clean = build_clean_table(df_raw)
    print(f"\nClean cells: {len(df_clean)} (expected 101)")

    metrics = ["cosine", "euclidean", "mahalanobis"]
    all_summaries = []
    for m in metrics:
        s = run_metric(df_clean, m, N1_LEVELS)
        all_summaries.append(s)

    summary = pd.concat(all_summaries, ignore_index=True)
    out = OUT_DIR / "probe8b_distance_metric_results.parquet"
    summary.to_parquet(out)
    print(f"\nWritten: {out}")

    print(f"\n\n========== PROBE 8b HEADLINES (Level 2) ==========")
    for m in metrics:
        sv = summary[(summary["metric"] == m) & (summary["level"] == 2)].iloc[0]
        n_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "PASS")
        n_weak = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "WEAK PASS")
        print(f"  {m:12s}: {n_pass} PASS + {n_weak} WEAK -- "
              f"th F={sv['F_thickness']:.2f} ({sv['verdict_thickness']}) | "
              f"tn F={sv['F_transference']:.2f} ({sv['verdict_transference']}) | "
              f"pr F={sv['F_particle']:.2f} ({sv['verdict_particle']}) | {sv['level_verdict']}")

    print(f"\n========== DISPOSITION ==========")
    maha_l2 = summary[(summary["metric"] == "mahalanobis") & (summary["level"] == 2)].iloc[0]
    cos_l2 = summary[(summary["metric"] == "cosine") & (summary["level"] == 2)].iloc[0]
    maha_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"] if maha_l2[c] == "PASS")
    cos_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"] if cos_l2[c] == "PASS")
    if maha_pass >= 3:
        print(f"  MAHALANOBIS RECOVERS TRANSFERENCE: {maha_pass}/3 PASS at L2 (vs cosine {cos_pass}/3)")
    elif maha_pass == cos_pass and maha_l2["F_thickness"] > cos_l2["F_thickness"] * 1.5:
        print(f"  MAHALANOBIS PARTIAL IMPROVEMENT: same PASS count, but th F={maha_l2['F_thickness']:.2f} vs cosine {cos_l2['F_thickness']:.2f}")
    elif maha_pass == cos_pass:
        print(f"  DISTANCE METRIC NEUTRAL: all metrics {maha_pass}/3 at L2")
    else:
        print(f"  MAHALANOBIS DEGRADES: {maha_pass}/3 < cosine {cos_pass}/3")


if __name__ == "__main__":
    main()
