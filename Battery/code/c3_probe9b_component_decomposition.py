"""C3 Probe 9b — PCA component decomposition.

Pre-reg: literature/54_probe9b_pca_component_decomposition_prereg.md (lock d9dcdf6).
Input:   data/processed/pybamm_l9_trajectories_eis_v3.parquet (8D) — already locked.
Output:  data/processed/probe9b_component_decomposition.parquet (+ loadings dump)

Analysis-only. Reruns the committed v3 parquet. No new PyBaMM generation.

Imports the Probe 9 analyzer's noise/PCA/PERMANOVA functions VERBATIM so the
cumulative-k F curve reproduces Probe 9's 8D-PCA2 / 8D-PCA3 values bit-identically
(falsifier P-Probe9b_F1).

Three computations (pre-reg section 3):
  (A) eigenvector loadings — 8D and 6D at L2 single Probe-9 seed
  (B) cumulative-k cosine-PERMANOVA F curve, k in {1,2,3,4}, marginal dF(PCk)
  (C) 200-seed L2 stability resampling — Delta_th, Delta_pr (pr = negative control)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from c3_probe9_extended_permanova import (
    build_clean_table, apply_noise_8d, build_pca, cosine_dist,
    permanova_pseudoF, permanova_test, N1_LEVELS, DESIGN_PARAMS,
)

IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet")
OUT_PARQUET = Path("D:/Renewables/Battery/data/processed/probe9b_component_decomposition.parquet")
OUT_LOADINGS = Path("D:/Renewables/Battery/data/processed/probe9b_loadings.parquet")

# 8D / 6D column orders (must match Probe 9's run_probe9 / run_f1_reproduction).
COLS_8D = ["fQ_n", "fRo_n", "fRd10_n", "fRd1_n", "aQ_n", "aRo_n", "aRd10_n", "aRd1_n"]
COLS_6D = ["fQ_n", "fRo_n", "fRd10_n", "aQ_n", "aRo_n", "aRd10_n"]
NAMES_8D = ["fresh_Q", "fresh_R_ohmic", "fresh_R_diff_10mHz", "fresh_R_diff_1mHz",
            "aged_Q", "aged_R_ohmic", "aged_R_diff_10mHz", "aged_R_diff_1mHz"]
NAMES_6D = ["fresh_Q", "fresh_R_ohmic", "fresh_R_diff_10mHz",
            "aged_Q", "aged_R_ohmic", "aged_R_diff_10mHz"]
OHMIC_IDX_8D = [1, 5]
RDIFF_IDX_8D = [2, 3, 6, 7]
OHMIC_IDX_6D = [1, 4]
RDIFF_IDX_6D = [2, 5]

# Probe 9 reported L2 values (for P-Probe9b_F1 reproduction assert).
P9_L2 = {
    2: {"thickness_level": 15.829, "transference_level": 0.771, "particle_radius_level": 26.920},
    3: {"thickness_level": 19.447, "transference_level": 0.022, "particle_radius_level": 19.867},
}
F1_TOL = 0.01  # absolute F tolerance

N_SEEDS = 200
SEED_BASE_C = 50000


def pca_components(features, k):
    """Identical PCA internals to build_pca, but returns the components (loadings).

    Returns (projection, eigvals_desc, components_kxd, components_full_dxd).
    """
    f = features - features.mean(axis=0, keepdims=True)
    pooled_sd = f.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = f / pooled_sd
    cov = np.cov(z.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    comp_full = eigvecs[:, idx]
    comp_k = comp_full[:, :k]
    return z @ comp_k, eigvals[idx], comp_k, comp_full


def noise_seeded(df_clean, sigma_Q, sigma_Ro, sigma_Rd, base_seed):
    """One independent noise realization drawn from a single RNG seeded by base_seed.

    Used only for part (C). Distinct from Probe 9's per-cell apply_noise_8d, which
    is reproduced exactly via the imported function for parts (A)/(B)/F1.
    """
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    rng = np.random.default_rng(base_seed)
    df["fQ_n"] = df["fresh_Q"] * (1 + rng.normal(0, sigma_Q, n))
    df["fRo_n"] = df["fresh_R_ohmic"] * (1 + rng.normal(0, sigma_Ro, n))
    df["fRd10_n"] = df["fresh_R_diff_10mHz"] * (1 + rng.normal(0, sigma_Rd, n))
    df["fRd1_n"] = df["fresh_R_diff_1mHz"] * (1 + rng.normal(0, sigma_Rd, n))
    df["aQ_n"] = df["aged_Q"] * (1 + rng.normal(0, sigma_Q, n))
    df["aRo_n"] = df["aged_R_ohmic"] * (1 + rng.normal(0, sigma_Ro, n))
    df["aRd10_n"] = df["aged_R_diff_10mHz"] * (1 + rng.normal(0, sigma_Rd, n))
    df["aRd1_n"] = df["aged_R_diff_1mHz"] * (1 + rng.normal(0, sigma_Rd, n))
    return df


def f_obs_at_k(df_noisy, cols, k, dv):
    feats = df_noisy[cols].values
    proj, _ = build_pca(feats, k)
    d = cosine_dist(proj)
    return permanova_pseudoF(d, df_noisy[dv].values)


# ---------------- (A) loadings ----------------

def part_A_loadings(df_clean):
    print("\n" + "=" * 78)
    print("(A) EIGENVECTOR LOADINGS at L2 (single Probe-9 seed)")
    print("=" * 78)
    L2 = N1_LEVELS[2]
    df_n = apply_noise_8d(df_clean, L2["sigma_Q"], L2["sigma_Ro"], L2["sigma_Rd"], L2["level"])

    rows = []
    # 8D
    feats8 = df_n[COLS_8D].values
    _, eig8, comp8, _ = pca_components(feats8, 8)
    print("\n8D loadings (sign arbitrary). |loading| per observable per PC:")
    print(f"{'observable':22s} {'PC1':>8s} {'PC2':>8s} {'PC3':>8s} {'PC4':>8s}")
    for i, nm in enumerate(NAMES_8D):
        l = np.abs(comp8[i, :4])
        print(f"{nm:22s} {l[0]:8.3f} {l[1]:8.3f} {l[2]:8.3f} {l[3]:8.3f}")
        rows.append({"stack": "8D", "observable": nm, "idx": i,
                     "PC1": float(comp8[i, 0]), "PC2": float(comp8[i, 1]),
                     "PC3": float(comp8[i, 2]), "PC4": float(comp8[i, 3])})
    var8 = eig8 / eig8.sum()
    print(f"{'var explained':22s} {var8[0]:8.3f} {var8[1]:8.3f} {var8[2]:8.3f} {var8[3]:8.3f}")

    # 6D
    feats6 = df_n[COLS_6D].values
    _, eig6, comp6, _ = pca_components(feats6, 6)
    print("\n6D loadings (no 1 mHz; the 8c amendment space). |loading| per observable per PC:")
    print(f"{'observable':22s} {'PC1':>8s} {'PC2':>8s} {'PC3':>8s}")
    for i, nm in enumerate(NAMES_6D):
        l = np.abs(comp6[i, :3])
        print(f"{nm:22s} {l[0]:8.3f} {l[1]:8.3f} {l[2]:8.3f}")
        rows.append({"stack": "6D", "observable": nm, "idx": i,
                     "PC1": float(comp6[i, 0]), "PC2": float(comp6[i, 1]),
                     "PC3": float(comp6[i, 2]), "PC4": float("nan")})
    var6 = eig6 / eig6.sum()
    print(f"{'var explained':22s} {var6[0]:8.3f} {var6[1]:8.3f} {var6[2]:8.3f}")

    # Quantified mechanism metrics
    print("\n--- mechanism metrics ---")
    # 8D: mean |loading| of R_ohmic channels per PC
    ohmic8 = np.abs(comp8[OHMIC_IDX_8D, :3]).mean(axis=0)
    rdiff8 = np.abs(comp8[RDIFF_IDX_8D, :3]).mean(axis=0)
    print(f"8D R_ohmic mean|load|:  PC1={ohmic8[0]:.3f} PC2={ohmic8[1]:.3f} PC3={ohmic8[2]:.3f}")
    print(f"8D R_diff  mean|load|:  PC1={rdiff8[0]:.3f} PC2={rdiff8[1]:.3f} PC3={rdiff8[2]:.3f}")
    ohmic_on_pc3 = (ohmic8[2] > ohmic8[0]) and (ohmic8[2] > ohmic8[1])
    rdiff_on_pc12 = (rdiff8[0] + rdiff8[1]) > 2 * rdiff8[2]
    print(f"  H9b-main 8D: R_ohmic dominant on PC3? {ohmic_on_pc3};  R_diff dominant on PC1-2? {rdiff_on_pc12}")
    # 6D: R_ohmic on PC1-2 (causation control)
    ohmic6 = np.abs(comp6[OHMIC_IDX_6D, :3]).mean(axis=0)
    print(f"6D R_ohmic mean|load|:  PC1={ohmic6[0]:.3f} PC2={ohmic6[1]:.3f} PC3={ohmic6[2]:.3f}")
    ohmic6_on_pc12 = (ohmic6[0] + ohmic6[1]) > 2 * ohmic6[2]
    print(f"  H9b-causation 6D: R_ohmic on PC1-2 (not PC3)? {ohmic6_on_pc12}")

    metrics = {
        "ohmic8_pc1": float(ohmic8[0]), "ohmic8_pc2": float(ohmic8[1]), "ohmic8_pc3": float(ohmic8[2]),
        "rdiff8_pc1": float(rdiff8[0]), "rdiff8_pc2": float(rdiff8[1]), "rdiff8_pc3": float(rdiff8[2]),
        "ohmic6_pc1": float(ohmic6[0]), "ohmic6_pc2": float(ohmic6[1]), "ohmic6_pc3": float(ohmic6[2]),
        "H9b_main_ohmic_on_pc3": bool(ohmic_on_pc3),
        "H9b_main_rdiff_on_pc12": bool(rdiff_on_pc12),
        "H9b_causation_6d_ohmic_pc12": bool(ohmic6_on_pc12),
    }
    pd.DataFrame(rows).to_parquet(OUT_LOADINGS)
    print(f"\nLoadings written: {OUT_LOADINGS}")
    return metrics


# ---------------- (B) cumulative-k F curve ----------------

def part_B_kcurve(df_clean):
    print("\n" + "=" * 78)
    print("(B) CUMULATIVE-k COSINE-PERMANOVA F CURVE (k=1..4, 10K perms)")
    print("=" * 78)
    rows = []
    for ln in N1_LEVELS:
        df_n = apply_noise_8d(df_clean, ln["sigma_Q"], ln["sigma_Ro"], ln["sigma_Rd"], ln["level"])
        feats = df_n[COLS_8D].values
        for dv in DESIGN_PARAMS:
            prev_F = None
            for k in [1, 2, 3, 4]:
                proj, _ = build_pca(feats, k)
                d = cosine_dist(proj)
                F = permanova_pseudoF(d, df_n[dv].values)
                # p only at L2 (headline level), full 10K perms; elsewhere F-only
                if ln["level"] == 2:
                    rng = np.random.default_rng(99000 + k * 100 + hash(dv) % 100)
                    _, p = permanova_test(proj, df_n[dv].values, rng)
                else:
                    p = float("nan")
                dF = (F - prev_F) if (prev_F is not None and np.isfinite(F) and np.isfinite(prev_F)) else float("nan")
                rows.append({"level": ln["level"], "design_param": dv, "k": k,
                             "F": F, "p": p, "dF": dF, "degenerate": (k == 1)})
                prev_F = F
    df = pd.DataFrame(rows)

    # Print L2 headline
    print("\nL2 PRIMARY (k=1 degenerate, excluded from marginal interpretation):")
    l2 = df[df.level == 2]
    for dv in DESIGN_PARAMS:
        sub = l2[l2.design_param == dv].sort_values("k")
        fs = {int(r.k): r.F for _, r in sub.iterrows()}
        dfs = {int(r.k): r.dF for _, r in sub.iterrows()}
        print(f"  {dv:22s}: F(k1)={fs[1]:6.2f}* F(k2)={fs[2]:6.2f} F(k3)={fs[3]:6.2f} F(k4)={fs[4]:6.2f}  "
              f"| dF(PC3)={dfs[3]:+6.2f} dF(PC4)={dfs[4]:+6.2f}")

    # F1 reproduction
    print("\n--- P-Probe9b_F1 reproduction (vs Probe 9 reported L2) ---")
    f1_ok = True
    for k in [2, 3]:
        for dv in DESIGN_PARAMS:
            got = float(l2[(l2.design_param == dv) & (l2.k == k)]["F"].iloc[0])
            want = P9_L2[k][dv]
            dev = abs(got - want)
            ok = dev < F1_TOL
            f1_ok = f1_ok and ok
            print(f"  k={k} {dv:22s}: got={got:.4f} want={want:.4f} dev={dev:.2e} {'OK' if ok else 'FAIL'}")

    # H9b-localization
    dF_th_pc3 = float(l2[(l2.design_param == "thickness_level") & (l2.k == 3)]["dF"].iloc[0])
    dF_pr_pc3 = float(l2[(l2.design_param == "particle_radius_level") & (l2.k == 3)]["dF"].iloc[0])
    print(f"\n  H9b-localization: dF_th(PC3)={dF_th_pc3:+.3f} (want >0), "
          f"dF_pr(PC3)={dF_pr_pc3:+.3f} (want <=0)")
    loc_ok = (dF_th_pc3 > 0) and (dF_pr_pc3 <= 0)

    df.to_parquet(OUT_PARQUET)
    print(f"\nk-curve written: {OUT_PARQUET}")
    return {"f1_ok": f1_ok, "loc_ok": loc_ok,
            "dF_th_pc3": dF_th_pc3, "dF_pr_pc3": dF_pr_pc3}


# ---------------- (C) multi-seed stability ----------------

def part_C_stability(df_clean):
    print("\n" + "=" * 78)
    print(f"(C) MULTI-SEED STABILITY at L2 (N={N_SEEDS} seeds, F-only)")
    print("=" * 78)
    L2 = N1_LEVELS[2]
    dth, dpr = [], []
    th_k2, th_k3, pr_k2, pr_k3 = [], [], [], []
    for s in range(N_SEEDS):
        df_n = noise_seeded(df_clean, L2["sigma_Q"], L2["sigma_Ro"], L2["sigma_Rd"], SEED_BASE_C + s)
        f_th2 = f_obs_at_k(df_n, COLS_8D, 2, "thickness_level")
        f_th3 = f_obs_at_k(df_n, COLS_8D, 3, "thickness_level")
        f_pr2 = f_obs_at_k(df_n, COLS_8D, 2, "particle_radius_level")
        f_pr3 = f_obs_at_k(df_n, COLS_8D, 3, "particle_radius_level")
        if all(np.isfinite(x) for x in [f_th2, f_th3, f_pr2, f_pr3]):
            dth.append(f_th3 - f_th2)
            dpr.append(f_pr2 - f_pr3)
            th_k2.append(f_th2); th_k3.append(f_th3); pr_k2.append(f_pr2); pr_k3.append(f_pr3)
    dth = np.array(dth); dpr = np.array(dpr)

    def summ(a):
        return float(np.mean(a)), float(np.std(a)), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))

    m_th, s_th, lo_th, hi_th = summ(dth)
    m_pr, s_pr, lo_pr, hi_pr = summ(dpr)
    print(f"\n  Delta_th = F_th(k3) - F_th(k2):  mean={m_th:+.3f} sd={s_th:.3f} 95%=[{lo_th:+.3f}, {hi_th:+.3f}]  (n={len(dth)})")
    print(f"  Delta_pr = F_pr(k2) - F_pr(k3):  mean={m_pr:+.3f} sd={s_pr:.3f} 95%=[{lo_pr:+.3f}, {hi_pr:+.3f}]")
    print(f"  th: mean F_k2={np.mean(th_k2):.2f} F_k3={np.mean(th_k3):.2f};  "
          f"pr: mean F_k2={np.mean(pr_k2):.2f} F_k3={np.mean(pr_k3):.2f}")
    frac_th_pos = float((dth > 0).mean())
    print(f"  Fraction of seeds with k3>k2 for thickness: {frac_th_pos:.3f}")

    th_stable = lo_th > 0
    pr_control_holds = lo_pr > 0
    print(f"\n  Delta_th 95% excludes zero (stable)? {th_stable}")
    print(f"  P-Probe9b_F3 negative control (Delta_pr 95% > 0)? {pr_control_holds}")

    pd.DataFrame({"delta_th": dth, "delta_pr": dpr}).to_parquet(
        Path("D:/Renewables/Battery/data/processed/probe9b_stability_seeds.parquet"))
    return {"th_stable": th_stable, "pr_control_holds": pr_control_holds,
            "delta_th_mean": m_th, "delta_th_ci": [lo_th, hi_th],
            "delta_pr_mean": m_pr, "delta_pr_ci": [lo_pr, hi_pr],
            "frac_th_pos": frac_th_pos}


def disposition(a, b, c):
    print("\n" + "=" * 78)
    print("PROBE 9b DISPOSITION (per lit/54 sections 4-5)")
    print("=" * 78)
    if not b["f1_ok"]:
        print("\n==> PROBE 9b INVALID — F1 reproduction failed.")
        return "PROBE 9b INVALID"

    main_ok = a["H9b_main_ohmic_on_pc3"] and a["H9b_main_rdiff_on_pc12"]
    caus_ok = a["H9b_causation_6d_ohmic_pc12"]
    loc_ok = b["loc_ok"]

    print(f"\n  F1 reproduction:           PASS")
    print(f"  H9b-main (loadings):       {'HOLDS' if main_ok else 'FAILS'}  "
          f"(R_ohmic on PC3={a['H9b_main_ohmic_on_pc3']}, R_diff on PC1-2={a['H9b_main_rdiff_on_pc12']})")
    print(f"  H9b-localization (dF):     {'HOLDS' if loc_ok else 'FAILS'}  "
          f"(dF_th(PC3)={b['dF_th_pc3']:+.2f}, dF_pr(PC3)={b['dF_pr_pc3']:+.2f})")
    print(f"  H9b-causation (6D):        {'HOLDS' if caus_ok else 'FAILS'}")
    print(f"  Stability (Delta_th 95%>0):{'HOLDS' if c['th_stable'] else 'FAILS'}  "
          f"(mean={c['delta_th_mean']:+.2f}, 95%={c['delta_th_ci']})")
    print(f"  F3 neg-control (Delta_pr): {'HOLDS' if c['pr_control_holds'] else 'FAILS'}")

    # F2 coherence: loadings (main) and localization must agree
    f2_incoherent = (main_ok != loc_ok)
    if f2_incoherent:
        print("\n  P-Probe9b_F2: INCOHERENT — loadings and marginal-gain disagree.")
        return "MECHANISM REFUTED (F2 incoherent)"

    if main_ok and loc_ok and caus_ok:
        if c["th_stable"] and c["pr_control_holds"]:
            disp = "MECHANISM CONFIRMED (stable)"
        else:
            disp = "MECHANISM REAL BUT UNSTABLE"
    else:
        disp = "MECHANISM REFUTED"
    print(f"\n==> {disp}")
    return disp


def main():
    print(f"Reading {IN_PARQUET}")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_clean = build_clean_table(df_raw)
    print(f"  Clean cells: {len(df_clean)}")

    a = part_A_loadings(df_clean)
    b = part_B_kcurve(df_clean)
    c = part_C_stability(df_clean)
    disp = disposition(a, b, c)

    print("\n" + "=" * 78)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 78)


if __name__ == "__main__":
    main()
