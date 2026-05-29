"""C3 Probe 14 - GITT particle-radius multi-seed stability promotion.

Pre-reg: literature/64_probe14_gitt_particle_radius_stability_prereg.md (lock 7fd0e44).
Inputs (reused unchanged):
  data/processed/pybamm_l9_trajectories_gitt_v1.parquet  (GITT, SHA 0851ff9f...)
  data/processed/pybamm_l9_trajectories_eis_v3.parquet   (EIS,  SHA in lit/53)
Output:
  data/processed/probe14_gitt_pr_stability_results.parquet

Applies the 9b multi-seed stability gate to the Probe-10 side finding (GITT pr F=72 vs
EIS 27). Replaces the deterministic per-cell noise seed with N=200 independent random
seeds; reports the pr PERMANOVA F DISTRIBUTION per modality/level/k on the COMMON clean
cohort (EIS-clean intersect GITT-clean). PCA-2 primary; k in {2,3,4} for coherence.
Reproduces the deterministic 71.56/26.92 anchors as a sanity check (NOT a claim).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe9_extended_permanova import (
    build_clean_table as eis_clean_table, apply_noise_8d as eis_det_noise,
    build_pca, cosine_dist, permanova_pseudoF, permanova_test, N1_LEVELS,
)
from c3_probe10_gitt_permanova import (
    build_clean_table as gitt_clean_table, apply_vnoise as gitt_det_noise,
    V_NOISE_LEVELS, STACK_6D, STACK_8D,
)

EIS_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe14_gitt_pr_stability_results.parquet")

N_SEEDS = 200
F_FLOOR = 3.0
PR = "particle_radius_level"
TH = "thickness_level"
EIS_8D = ["fresh_Q", "fresh_R_ohmic", "fresh_R_diff_10mHz", "fresh_R_diff_1mHz",
          "aged_Q", "aged_R_ohmic", "aged_R_diff_10mHz", "aged_R_diff_1mHz"]


def common_cohort():
    eis = eis_clean_table(pd.read_parquet(EIS_PARQUET))
    gitt = gitt_clean_table()
    keys = pd.merge(eis[["cond_idx", "cell_idx"]], gitt[["cond_idx", "cell_idx"]],
                    on=["cond_idx", "cell_idx"])
    key_set = set(map(tuple, keys.values))
    em = eis[eis.apply(lambda r: (r.cond_idx, r.cell_idx) in key_set, axis=1)].reset_index(drop=True)
    gm = gitt[gitt.apply(lambda r: (r.cond_idx, r.cell_idx) in key_set, axis=1)].reset_index(drop=True)
    # align row order so labels match
    em = em.sort_values(["cond_idx", "cell_idx"]).reset_index(drop=True)
    gm = gm.sort_values(["cond_idx", "cell_idx"]).reset_index(drop=True)
    assert (em[["cond_idx", "cell_idx"]].values == gm[["cond_idx", "cell_idx"]].values).all()
    return em, gm


def pr_F(X, labels, k):
    pca, _ = build_pca(X, k)
    return permanova_pseudoF(cosine_dist(pca), labels)


def inject(base, cols, sigmas, rng):
    """Multiplicative noise; sigmas is scalar (all cols) or per-col list."""
    X = base[cols].values.astype(float)
    eps = np.zeros_like(X)
    if np.isscalar(sigmas):
        if sigmas > 0:
            eps = rng.normal(0, sigmas, size=X.shape)
    else:
        for j, s in enumerate(sigmas):
            if s > 0:
                eps[:, j] = rng.normal(0, s, size=X.shape[0])
    return X * (1 + eps)


def eis_sigmas(ln):
    sQ, sRo, sRd = ln["sigma_Q"], ln["sigma_Ro"], ln["sigma_Rd"]
    return [sQ, sRo, sRd, sRd, sQ, sRo, sRd, sRd]  # order of EIS_8D


def multiseed(base, cols, sigmas, labels, k, n=N_SEEDS):
    """Return F distribution across n random noise seeds (1 value if no noise)."""
    no_noise = (np.isscalar(sigmas) and sigmas == 0) or (not np.isscalar(sigmas) and all(s == 0 for s in sigmas))
    if no_noise:
        return np.array([pr_F(base[cols].values.astype(float), labels, k)])
    Fs = np.empty(n)
    for b in range(n):
        rng = np.random.default_rng(b)
        Fs[b] = pr_F(inject(base, cols, sigmas, rng), labels, k)
    return Fs


def dist_summary(Fs):
    return {"median": float(np.nanmedian(Fs)), "p2_5": float(np.nanpercentile(Fs, 2.5)),
            "p97_5": float(np.nanpercentile(Fs, 97.5)), "min": float(np.nanmin(Fs)),
            "max": float(np.nanmax(Fs)), "n": int(len(Fs))}


def main():
    em, gm = common_cohort()
    print(f"Common clean cohort (EIS intersect GITT): {len(gm)} cells")
    print(gm.groupby([TH, "transference_level", PR]).size().to_string())
    pr_labels = gm[PR].values  # same cells, same labels for both modalities

    # --- deterministic anchor reproduction (sanity, NOT a claim) ---
    print("\n=== Anchor reproduction (deterministic seed; expect GITT~71.56 / EIS~26.92 @ L2) ===")
    gitt_L2 = gitt_det_noise(gm, V_NOISE_LEVELS[2]["sigma"], 2, STACK_8D)[0]
    g_anchor = pr_F(gitt_L2[STACK_8D].values, gm[PR].values, 2)
    eis_L2n = eis_det_noise(em, N1_LEVELS[2]["sigma_Q"], N1_LEVELS[2]["sigma_Ro"], N1_LEVELS[2]["sigma_Rd"], 2)
    e_anchor = pr_F(eis_L2n[["fQ_n", "fRo_n", "fRd10_n", "fRd1_n", "aQ_n", "aRo_n", "aRd10_n", "aRd1_n"]].values,
                    em[PR].values, 2)
    print(f"  GITT 8D PCA-2 pr F (det L2) = {g_anchor:.3f}   EIS 8D PCA-2 pr F (det L2) = {e_anchor:.3f}")

    rows = []

    # --- H14-main + distributions: GITT 8D/6D + EIS 8D, all levels, k in {2,3,4} ---
    print(f"\n=== Multi-seed pr F distributions (N={N_SEEDS} random seeds) ===")
    levels = [0, 1, 2, 3, 4]
    for k in [2, 3, 4]:
        for lvl in levels:
            gln = V_NOISE_LEVELS[lvl]
            g8 = multiseed(gm, STACK_8D, gln["sigma"], pr_labels, k)
            g6 = multiseed(gm, STACK_6D, gln["sigma"], pr_labels, k)
            eln = N1_LEVELS[lvl]
            e8 = multiseed(em, EIS_8D, eis_sigmas(eln), em[PR].values, k)
            for tag, Fs in [("GITT_8D", g8), ("GITT_6D", g6), ("EIS_8D", e8)]:
                s = dist_summary(Fs)
                rows.append({"feature": tag, "pca_k": k, "level": lvl, **s,
                             "pass_floor": (s["median"] > F_FLOOR) and (s["p2_5"] > F_FLOOR)})
            if k == 2:
                print(f"  L{lvl} k=2: GITT_8D med={dist_summary(g8)['median']:.2f} "
                      f"[{dist_summary(g8)['p2_5']:.2f},{dist_summary(g8)['p97_5']:.2f}]  "
                      f"EIS_8D med={dist_summary(e8)['median']:.2f} "
                      f"[{dist_summary(e8)['p2_5']:.2f},{dist_summary(e8)['p97_5']:.2f}]")
    res = pd.DataFrame(rows)
    res.to_parquet(OUT)

    def get(feature, k, lvl):
        r = res[(res.feature == feature) & (res.pca_k == k) & (res.level == lvl)]
        return r.iloc[0]

    # ---- Falsifiers + hypotheses ----
    g8_L0 = get("GITT_8D", 2, 0); e8_L0 = get("EIS_8D", 2, 0)
    g8_L2 = get("GITT_8D", 2, 2); e8_L2 = get("EIS_8D", 2, 2)

    f1_ok = (g8_L0["median"] > F_FLOOR) and (e8_L0["median"] > F_FLOOR)

    # F2 coherence: GITT pr PASS at k=2,3,4 (use L2)
    f2_ok = all(get("GITT_8D", k, 2)["median"] > F_FLOOR for k in [2, 3, 4])

    # H14-main: GITT 8D k=2 L2 median+2.5pct > floor; stable across L0-L4
    h14_main = bool(g8_L2["pass_floor"]) and all(get("GITT_8D", 2, l)["pass_floor"] or l == 0 for l in levels)
    # (L0 has single value; pass_floor uses median==value)

    # H14-sec(i) intrinsic L0: GITT pr F(L0) >= 2x EIS pr F(L0)
    intrinsic_ratio = g8_L0["median"] / e8_L0["median"] if e8_L0["median"] > 0 else float("inf")
    sec_i = intrinsic_ratio >= 2.0
    # H14-sec(ii) realistic L2: GITT 2.5pct > EIS 97.5pct
    sec_ii = g8_L2["p2_5"] > e8_L2["p97_5"]
    h14_sec = sec_i and sec_ii

    if not f1_ok:
        disp = "PROBE 14 INVALID (pr does not separate at L0)"
    elif not h14_main:
        disp = "GITT-PR-FRAGILE (pr discrimination not robust to reseeding)"
    elif h14_sec:
        disp = "GITT-PR-SUPERIOR (robust)"
    else:
        disp = "GITT-PR-ROBUST-NOT-SUPERIOR"

    print("\n" + "=" * 74)
    print("PROBE 14 DISPOSITION (per lit/64 §5)")
    print("=" * 74)
    print(f"  common cohort N = {len(gm)} cells")
    print(f"  anchor reproduced: GITT={g_anchor:.2f} (known 71.56)  EIS={e_anchor:.2f} (known 26.92)")
    print(f"  F1 positive control (L0 both > {F_FLOOR}):        {'PASS' if f1_ok else 'FAIL'}")
    print(f"  F2 PCA-k coherence (GITT PASS k=2,3,4 @L2):    {'PASS' if f2_ok else 'FAIL'}")
    print(f"  H14-main GITT 8D k=2 robust (L2 med={g8_L2['median']:.2f}, 2.5pct={g8_L2['p2_5']:.2f}; stable L0-L4): {'PASS' if h14_main else 'FAIL'}")
    print(f"  H14-sec(i) intrinsic L0 ratio = {intrinsic_ratio:.2f}x (>=2):    {'PASS' if sec_i else 'FAIL'}")
    print(f"  H14-sec(ii) realistic L2 GITT[2.5pct]={g8_L2['p2_5']:.2f} > EIS[97.5pct]={e8_L2['p97_5']:.2f}: {'PASS' if sec_ii else 'FAIL'}")
    print(f"\n  ==> {disp}")
    print(f"\nWritten: {OUT}")
    print("=" * 74)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 74)


if __name__ == "__main__":
    main()
