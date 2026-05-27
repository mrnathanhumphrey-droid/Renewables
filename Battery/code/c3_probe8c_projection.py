"""C3 Probe 8c — projection decomposition.

Pre-reg: literature/45_probe8c_prereg.md.

Tests three projection variants of the variant-iv + cosine combination:
  1. Full 6D unit-vector cosine (baseline = 8a variant iv)
  2. PCA-reduced to k=2 components + unit-vector cosine
  3. PCA-reduced to k=3 components + unit-vector cosine

Question: does PCA reduction preserve or improve L2 discrimination?
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


def build_zscore_feats(df_noisy):
    """Variant (iv): fresh+aged 6D stacked, centered + z-scored."""
    feats = df_noisy[["fQ_n", "fRo_n", "fRd_n", "aQ_n", "aRo_n", "aRd_n"]].values
    feats = feats - feats.mean(axis=0, keepdims=True)
    pooled_sd = feats.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    return feats / pooled_sd


def pca_project(z, k):
    """Project z (n×d) onto its top-k principal components. Returns (proj, explained_var_ratio, components)."""
    cov = np.cov(z.T)  # d×d
    eigvals, eigvecs = np.linalg.eigh(cov)
    # eigh returns ascending order; flip to descending
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    components = eigvecs[:, :k]  # d×k
    proj = z @ components  # n×k
    total_var = eigvals.sum()
    explained_ratio = eigvals[:k].sum() / total_var if total_var > 0 else 0
    return proj, float(explained_ratio), components


def unit_project(z):
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    return z / np.where(norms < 1e-12, 1e-12, norms)


def cosine_distance_matrix(u):
    cos_mat = u @ u.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    return 1.0 - cos_mat


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


def run_projection(df_clean, proj_label, noise_levels):
    print(f"\n========== Projection {proj_label} ==========")
    summary_rows = []
    explained_ratios_log = []
    for nl in noise_levels:
        df_noisy = apply_noise(df_clean, nl["sigma_Q"], nl["sigma_Ro"], nl["sigma_Rd"], nl["level"])
        z = build_zscore_feats(df_noisy)
        explained = None
        components = None
        if proj_label == "full_6d_unit":
            proj = z
        elif proj_label == "pca_2_unit":
            proj, explained, components = pca_project(z, 2)
            explained_ratios_log.append((nl["level"], explained))
        elif proj_label == "pca_3_unit":
            proj, explained, components = pca_project(z, 3)
            explained_ratios_log.append((nl["level"], explained))
        else:
            raise ValueError(proj_label)
        u = unit_project(proj)
        d_mat = cosine_distance_matrix(u)
        rng_p = np.random.default_rng(RNG_SEED_BASE + 999000 + nl["level"])
        verdicts = {}
        Fs = {}
        ps = {}
        for param_col in ["thickness_level", "transference_level", "particle_radius_level"]:
            F, p = permanova_test_dist(d_mat, df_noisy[param_col].values, rng_p)
            v = parameter_verdict(F, p)
            verdicts[param_col] = v
            Fs[param_col] = F
            ps[param_col] = p
        lv = level_verdict(verdicts)
        explained_str = f"  exp_var={explained:.3f}" if explained is not None else ""
        print(f"  {nl['name']:25s} | "
              f"th: F={Fs['thickness_level']:7.2f} p={ps['thickness_level']:.4f} {verdicts['thickness_level']:9s} | "
              f"tn: F={Fs['transference_level']:7.2f} p={ps['transference_level']:.4f} {verdicts['transference_level']:9s} | "
              f"pr: F={Fs['particle_radius_level']:7.2f} p={ps['particle_radius_level']:.4f} {verdicts['particle_radius_level']:9s} | {lv}{explained_str}")
        if components is not None and nl["level"] == 0:
            feature_names = ["fresh_Q", "fresh_R_ohmic", "fresh_R_diff", "aged_Q", "aged_R_ohmic", "aged_R_diff"]
            print(f"    PC loadings (L0):")
            for ki in range(components.shape[1]):
                print(f"      PC{ki+1}: " + ", ".join(f"{feature_names[j]}={components[j, ki]:+.3f}" for j in range(len(feature_names))))
        summary_rows.append({
            "projection": proj_label,
            "level": nl["level"],
            "name": nl["name"],
            "explained_var_ratio": explained,
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
    print(f"=== Probe 8c -- projection decomposition (pre-reg literature/45) ===")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_clean = build_clean_table(df_raw)
    print(f"\nClean cells: {len(df_clean)} (expected 101)")

    projections = ["full_6d_unit", "pca_2_unit", "pca_3_unit"]
    all_summaries = []
    for p in projections:
        s = run_projection(df_clean, p, N1_LEVELS)
        all_summaries.append(s)

    summary = pd.concat(all_summaries, ignore_index=True)
    out = OUT_DIR / "probe8c_projection_results.parquet"
    summary.to_parquet(out)
    print(f"\nWritten: {out}")

    print(f"\n\n========== PROBE 8c HEADLINES (Level 2) ==========")
    for p in projections:
        sv = summary[(summary["projection"] == p) & (summary["level"] == 2)].iloc[0]
        n_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "PASS")
        n_weak = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"]
                     if sv[c] == "WEAK PASS")
        exp = f" exp_var={sv['explained_var_ratio']:.3f}" if pd.notna(sv["explained_var_ratio"]) else ""
        print(f"  {p:15s}: {n_pass} PASS + {n_weak} WEAK -- "
              f"th F={sv['F_thickness']:.2f} ({sv['verdict_thickness']}) | "
              f"tn F={sv['F_transference']:.2f} ({sv['verdict_transference']}) | "
              f"pr F={sv['F_particle']:.2f} ({sv['verdict_particle']}) | {sv['level_verdict']}{exp}")

    print(f"\n========== DISPOSITION ==========")
    full_l2 = summary[(summary["projection"] == "full_6d_unit") & (summary["level"] == 2)].iloc[0]
    pca2_l2 = summary[(summary["projection"] == "pca_2_unit") & (summary["level"] == 2)].iloc[0]
    pca3_l2 = summary[(summary["projection"] == "pca_3_unit") & (summary["level"] == 2)].iloc[0]
    full_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"] if full_l2[c] == "PASS")
    pca2_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"] if pca2_l2[c] == "PASS")
    pca3_pass = sum(1 for c in ["verdict_thickness", "verdict_transference", "verdict_particle"] if pca3_l2[c] == "PASS")
    if pca3_pass >= full_pass and pca2_pass >= full_pass:
        print(f"  PROJECTION REDUCTION SAFE: PCA-2 {pca2_pass}/3, PCA-3 {pca3_pass}/3 vs full-6D {full_pass}/3.")
        print(f"  PCA reduction preserves L2 disposition without loss.")
    elif pca3_pass < full_pass and pca2_pass < full_pass:
        print(f"  PROJECTION HURTS: full-6D {full_pass}/3 > PCA-3 {pca3_pass}/3, PCA-2 {pca2_pass}/3.")
        print(f"  PCA reduction loses signal needed for L2 survival.")
    else:
        print(f"  PROJECTION MIXED: PCA-2 {pca2_pass}/3, PCA-3 {pca3_pass}/3, full {full_pass}/3.")


if __name__ == "__main__":
    main()
