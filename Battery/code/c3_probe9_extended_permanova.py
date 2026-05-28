"""C3 Probe 9 — Extended PERMANOVA on sub-mHz operator-augmented feature space.

Pre-reg: literature/52_probe9_transference_hunt_prereg.md (lock 288a7f8).
Input:   data/processed/pybamm_l9_trajectories_eis_v3.parquet (extended-grid generator).
Output:  data/processed/probe9_transference_results.parquet

Pipeline per cell c at SOH 0.92 uniform anchor:

  x_c = (fresh_Q, fresh_R_ohmic, fresh_R_diff_10mHz, fresh_R_diff_1mHz,
          aged_Q, aged_R_ohmic, aged_R_diff_10mHz, aged_R_diff_1mHz)  in R^8

  center -> z-score by pooled SD -> PCA k in {2, 3, 4} -> unit-vector projection
  -> cosine PERMANOVA per design parameter (10K perms, Bonferroni alpha/3 = 0.0167)

All five N1 noise levels x three design params x three PCA-k variants = 45 tests.
Plus F1 baseline = 6D-only at PCA-2 on v3 parquet (must reproduce 8c bit-identical).

Disposition + falsifiers per pre-reg sections 4-5.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet")
V2_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v2.parquet")
OUT_PARQUET = Path("D:/Renewables/Battery/data/processed/probe9_transference_results.parquet")
OUT_F1_PARQUET = Path("D:/Renewables/Battery/data/processed/probe9_F1_reproduction.parquet")

N_PERMS = 10000
ALPHA_BONFERRONI = 0.0167
ALPHA_WEAK = 0.05
F_FLOOR = 3.0
F_WEAK = 2.0

# 8c PCA-2 baseline values from lit/47 amendment (for F1 reproduction tolerance check)
EIGHT_C_TARGETS_L2 = {
    "thickness_level": 21.24,
    "particle_radius_level": 20.87,
    "transference_level": 0.67,
}
F1_TOLERANCE_PCT = 1.0  # 1 % tolerance band

N1_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.00, "sigma_Rd": 0.00, "name": "N1-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.05, "sigma_Rd": 0.10, "name": "N1-L1 best lab"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.15, "sigma_Rd": 0.20, "name": "N1-L2 PRIMARY"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.30, "sigma_Rd": 0.30, "name": "N1-L3 noisy field"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.50, "sigma_Rd": 0.50, "name": "N1-L4 instrument issue"},
]

RNG_SEED_BASE = 2000
PCA_K_VARIANTS = [2, 3, 4]
DESIGN_PARAMS = ["thickness_level", "transference_level", "particle_radius_level"]


def build_clean_table(df_raw):
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        # All 4 fresh + 4 aged columns must be present
        required = ["R_ohmic_fresh", "R_diff_fresh_10mHz", "R_diff_fresh_1mHz",
                    "R_ohmic_aged_b5", "R_diff_aged_b5_10mHz", "R_diff_aged_b5_1mHz",
                    "anchor_aged_Q", "fresh_Q"]
        if any(pd.isna(row.get(c)) for c in required):
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
            "fresh_R_diff_10mHz": float(row["R_diff_fresh_10mHz"]),
            "fresh_R_diff_1mHz": float(row["R_diff_fresh_1mHz"]),
            "aged_Q": float(row["anchor_aged_Q"]),
            "aged_R_ohmic": float(row["R_ohmic_aged_b5"]),
            "aged_R_diff_10mHz": float(row["R_diff_aged_b5_10mHz"]),
            "aged_R_diff_1mHz": float(row["R_diff_aged_b5_1mHz"]),
        })
    return pd.DataFrame(rows)


def apply_noise_8d(df_clean, sigma_Q, sigma_Ro, sigma_Rd, level):
    """Inject independent multiplicative noise on 8 observable channels.

    Pre-reg uses sigma_Rd from the existing N1 grid for BOTH R_diff_10mHz
    and R_diff_1mHz channels (same physical measurement class).
    """
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps = {k: np.empty(n) for k in
           ["fq", "fo", "fd10", "fd1", "aq", "ao", "ad10", "ad1"]}
    for i, row in df.iterrows():
        s = RNG_SEED_BASE + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(s)
        # Same seed sequence ordering as 8d for the first 6 channels (so the v3
        # 6D-baseline reproduces 8c at L2 bit-identical on F1).
        eps["fq"][i] = rng.normal(0, sigma_Q)
        eps["fo"][i] = rng.normal(0, sigma_Ro)
        eps["fd10"][i] = rng.normal(0, sigma_Rd)
        eps["aq"][i] = rng.normal(0, sigma_Q)
        eps["ao"][i] = rng.normal(0, sigma_Ro)
        eps["ad10"][i] = rng.normal(0, sigma_Rd)
        # New 1 mHz channels follow, independent draws from same RNG state.
        eps["fd1"][i] = rng.normal(0, sigma_Rd)
        eps["ad1"][i] = rng.normal(0, sigma_Rd)
    df["fQ_n"] = df["fresh_Q"] * (1 + eps["fq"])
    df["fRo_n"] = df["fresh_R_ohmic"] * (1 + eps["fo"])
    df["fRd10_n"] = df["fresh_R_diff_10mHz"] * (1 + eps["fd10"])
    df["fRd1_n"] = df["fresh_R_diff_1mHz"] * (1 + eps["fd1"])
    df["aQ_n"] = df["aged_Q"] * (1 + eps["aq"])
    df["aRo_n"] = df["aged_R_ohmic"] * (1 + eps["ao"])
    df["aRd10_n"] = df["aged_R_diff_10mHz"] * (1 + eps["ad10"])
    df["aRd1_n"] = df["aged_R_diff_1mHz"] * (1 + eps["ad1"])
    return df


def build_pca(features, k):
    f = features - features.mean(axis=0, keepdims=True)
    pooled_sd = f.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = f / pooled_sd
    cov = np.cov(z.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    components = eigvecs[:, idx][:, :k]
    return z @ components, eigvals[idx]


def cosine_dist(z):
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = u @ u.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    return 1.0 - cos_mat


def permanova_pseudoF(d_mat, labels):
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


def permanova_test(pca_feats, labels, rng, n_perms=N_PERMS):
    d_mat = cosine_dist(pca_feats)
    F_obs = permanova_pseudoF(d_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
        F_p = permanova_pseudoF(d_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > F_WEAK:
        return "WEAK PASS"
    return "NULL"


# -------------------- F1 reproduction (6D-only on v3) --------------------

def run_f1_reproduction(df_clean):
    """Apply the SAME 6D pipeline (8c PCA-2 unit cosine) to the v3 parquet's
    10 mHz columns ONLY. Must reproduce 8c at L2 within F1_TOLERANCE_PCT.
    """
    print("\n=== F1 reproduction: 6D PCA-2 on v3 parquet (must match 8c at L2) ===")
    L2 = N1_LEVELS[2]
    df_n = apply_noise_8d(df_clean, L2["sigma_Q"], L2["sigma_Ro"], L2["sigma_Rd"], L2["level"])
    feats_6d = df_n[["fQ_n", "fRo_n", "fRd10_n", "aQ_n", "aRo_n", "aRd10_n"]].values
    pca2, _ = build_pca(feats_6d, k=2)
    rows = []
    for dv in DESIGN_PARAMS:
        labels = df_n[dv].values
        rng = np.random.default_rng(7777 + hash(dv) % 1000)
        F, p = permanova_test(pca2, labels, rng)
        target = EIGHT_C_TARGETS_L2[dv]
        dev_pct = abs(F - target) / target * 100 if target > 0 else float("inf")
        passes = dev_pct < F1_TOLERANCE_PCT
        rows.append({"dv": dv, "F_obs_v3": F, "F_target_8c": target,
                     "dev_pct": dev_pct, "F1_pass": passes, "p_obs": p})
        print(f"  {dv:25s}: F_v3={F:.3f}  F_8c={target:.3f}  dev={dev_pct:.3f}%  {'PASS' if passes else 'FAIL'}")
    return pd.DataFrame(rows)


# -------------------- Probe 9 main grid --------------------

def run_probe9(df_clean):
    print("\n=== Probe 9 main: 8D + PCA-k in {2,3,4} x 3 design params x 5 noise levels ===")
    results = []
    for ln in N1_LEVELS:
        df_n = apply_noise_8d(df_clean, ln["sigma_Q"], ln["sigma_Ro"], ln["sigma_Rd"], ln["level"])
        feats_8d = df_n[["fQ_n", "fRo_n", "fRd10_n", "fRd1_n",
                         "aQ_n", "aRo_n", "aRd10_n", "aRd1_n"]].values
        for k in PCA_K_VARIANTS:
            pca_feats, eigvals = build_pca(feats_8d, k=k)
            for dv in DESIGN_PARAMS:
                labels = df_n[dv].values
                rng = np.random.default_rng(RNG_SEED_BASE + ln["level"] * 1000 + k * 100 + hash(dv) % 100)
                F, p = permanova_test(pca_feats, labels, rng)
                v = verdict(F, p)
                results.append({
                    "noise_level": ln["level"],
                    "noise_name": ln["name"],
                    "pca_k": k,
                    "design_param": dv,
                    "F_obs": F,
                    "p_perm": p,
                    "verdict": v,
                    "n_cells": len(df_n),
                    "var_explained_top_k": float(eigvals[:k].sum() / eigvals.sum()),
                })
                print(f"  L{ln['level']} k={k} {dv:25s}: F={F:7.3f} p={p:.4f} -> {v}"
                      f"  (var_expl={eigvals[:k].sum()/eigvals.sum()*100:.1f}%)")
    return pd.DataFrame(results)


def apply_disposition(probe9_df, f1_df):
    print("\n" + "=" * 78)
    print("PROBE 9 DISPOSITION (per lit/52 sections 4-5)")
    print("=" * 78)

    # P-Probe9_F1
    f1_all_pass = f1_df["F1_pass"].all()
    print(f"\nP-Probe9_F1 (10 mHz reproduces 8c PCA-2 at L2): "
          f"{'PASS' if f1_all_pass else 'FAIL'}")
    if not f1_all_pass:
        print("  PROBE 9 INVALID: v3 parquet does not inherit v2 cleanly. Debug + re-run.")
        return

    # L2 PRIMARY headline per design parameter, across PCA-k variants
    l2 = probe9_df[probe9_df["noise_level"] == 2].copy()
    headline = {}
    for dv in DESIGN_PARAMS:
        sub = l2[l2["design_param"] == dv]
        best = sub.sort_values("F_obs", ascending=False).iloc[0]
        headline[dv] = {
            "pca_k": int(best["pca_k"]),
            "F": float(best["F_obs"]),
            "p": float(best["p_perm"]),
            "verdict": best["verdict"],
        }
        print(f"\nL2 PRIMARY {dv:25s}: best PCA-k={best['pca_k']}  "
              f"F={best['F_obs']:.3f} p={best['p_perm']:.4f} -> {best['verdict']}")

    # P-Probe9_F2 (decomposition convergence / coherence across PCA-k)
    print("\n=== P-Probe9_F2 (PCA-k coherence across {2,3,4}) ===")
    for dv in DESIGN_PARAMS:
        sub = l2[l2["design_param"] == dv].sort_values("pca_k")
        verdicts = sub["verdict"].tolist()
        Fs = sub["F_obs"].tolist()
        ks = sub["pca_k"].tolist()
        # Coherent = all same verdict OR monotonic F trajectory; incoherent = oscillating verdicts
        v_set = set(verdicts)
        coherent = len(v_set) <= 2  # PASS+WEAK or NULL+WEAK ok; PASS+NULL+PASS = incoherent
        # Stricter check: PASS bracketed by NULL
        passes = [v in {"PASS", "WEAK PASS"} for v in verdicts]
        oscillating = (passes[0] and not passes[1] and passes[2]) if len(passes) == 3 else False
        coh_str = "INCOHERENT" if oscillating else "COHERENT"
        print(f"  {dv:25s}: k={ks} F={[f'{f:.2f}' for f in Fs]} v={verdicts} -> {coh_str}")

    # P-Probe9_F3 (no regression on th + pr)
    print("\n=== P-Probe9_F3 (no regression of th/pr vs 8c baseline) ===")
    floors = {"thickness_level": 16.0, "particle_radius_level": 15.6}
    for dv, floor in floors.items():
        F = headline[dv]["F"]
        ok = F >= floor
        print(f"  {dv:25s}: F={F:.3f}  floor={floor}  {'OK' if ok else 'REGRESSED (>25% drop)'}")
        if not ok:
            print(f"    WARN: {dv} dropped substantially — flag in result writeup")

    # Disposition table
    print("\n=== DISPOSITION ===")
    tn = headline["transference_level"]
    if tn["verdict"] in {"PASS", "WEAK PASS"}:
        # Confirm no th/pr regression
        if all(headline[dv]["F"] >= floors.get(dv, 0) for dv in ["thickness_level", "particle_radius_level"]):
            disp = "TRANSFERENCE RECOVERED"
        else:
            disp = "TRANSFERENCE RECOVERED (with th/pr regression flag)"
    elif tn["F"] > F_WEAK:
        disp = "TRANSFERENCE PARTIAL"
    elif tn["F"] < F_WEAK:
        disp = "TRANSFERENCE STILL NULL"
    else:
        disp = "AMBIGUOUS"
    print(f"  ==> {disp}")
    print(f"      transference best: PCA-k={tn['pca_k']}, F={tn['F']:.3f}, p={tn['p']:.4f}, "
          f"verdict={tn['verdict']}")
    return disp, headline


def main():
    print(f"Reading {IN_PARQUET}")
    df_raw = pd.read_parquet(IN_PARQUET)
    print(f"  Raw rows: {len(df_raw)}")
    df_clean = build_clean_table(df_raw)
    print(f"  Clean rows (no err, no NaN, no anchor_partial): {len(df_clean)}")
    print(f"  Distribution per condition:")
    print(df_clean.groupby(["thickness_level", "transference_level", "particle_radius_level"]).size().to_string())

    f1_df = run_f1_reproduction(df_clean)
    f1_df.to_parquet(OUT_F1_PARQUET)
    print(f"\nF1 reproduction written: {OUT_F1_PARQUET}")

    p9_df = run_probe9(df_clean)
    p9_df.to_parquet(OUT_PARQUET)
    print(f"\nProbe 9 results written: {OUT_PARQUET}")

    disp, headline = apply_disposition(p9_df, f1_df)

    print("\n" + "=" * 78)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 78)


if __name__ == "__main__":
    main()
