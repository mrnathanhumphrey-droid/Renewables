"""C3 Probe 18 - SECL HPPC-pulse operators vs EIS for SOH discrimination.

Pre-reg: literature/70_probe18_secl_hppc_pulse_operators_prereg.md (lock 497047b).
Inputs:
  data/processed/secl_pulse_ops.parquet           (Probe 18 extractor)
  data/processed/secl_eis_soh_observations.parquet (Probe 11, reused; SHA 9dd867c5...)
Output:
  data/processed/probe18_pulse_vs_eis_results.parquet
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe9_extended_permanova import build_pca, cosine_dist, permanova_pseudoF
from c3_probe11_soh_triage import permanova_naive, permanova_cellstrat, cell_labels

PULSE = Path("D:/Renewables/Battery/data/processed/secl_pulse_ops.parquet")
EIS = Path("D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe18_pulse_vs_eis_results.parquet")

EIS_COLS = ["R_ohmic_326", "R_diff_326", "R_ohmic_363", "R_diff_363", "R_ohmic_400", "R_diff_400"]
PULSE_COLS = [f"{op}_pulse_{soc}" for soc in [326, 363, 400] for op in ["R_ohmic", "eta_8s", "dV_rebound"]]
PROBE11_REF_F_K2 = 25.51  # Probe 11 §5, EIS 6D PERMANOVA F at k=2 cell-stratified


def perm_F_p(feats, labels, cells, k, seed=11000):
    pca, _ = build_pca(feats, k)
    rng_n = np.random.default_rng(seed + k)
    rng_c = np.random.default_rng(seed + 1000 + k)
    F, p_n = permanova_naive(pca, labels, rng_n)
    _, p_c = permanova_cellstrat(pca, labels, cells, rng_c)
    return F, p_n, p_c


def main():
    pulse = pd.read_parquet(PULSE)
    eis = pd.read_parquet(EIS)
    merged = pulse.merge(eis, on=["cell", "round"], how="inner")
    print(f"Pulse rows: {len(pulse)}  EIS rows: {len(eis)}  merged: {len(merged)}")
    print(f"Cells in merged: {sorted(merged.cell.unique())}")
    print(f"SOH range: {merged.SOH.min()*100:.1f}% - {merged.SOH.max()*100:.1f}%")

    cells = merged["cell"].values
    soh = merged["SOH"].values

    # ---- F1 / H18-secondary: Spearman rho per pulse op vs SOH ----
    print("\n=== F1 + H18-secondary: Spearman rho(pulse_op, SOH) ===")
    rho_rows = []
    for c in PULSE_COLS:
        rho, p = spearmanr(merged[c].values, soh)
        rho_rows.append({"op": c, "rho": float(rho), "p": float(p)})
        flag = " <-- tracks (p<0.05)" if (p < 0.05 and rho < 0) else ""
        print(f"  {c:30s} rho={rho:+.3f} p={p:.4f}{flag}")
    rho_df = pd.DataFrame(rho_rows)
    f1_ok = bool(((rho_df.rho < 0) & (rho_df.p < 0.05)).any())
    best_pulse_rho = float(rho_df.rho.abs().max())
    h18_sec = best_pulse_rho >= 0.85
    print(f"\n  F1 ({'PASS' if f1_ok else 'FAIL'}): >=1 pulse op tracks SOH (rho<0, p<0.05)")
    print(f"  H18-secondary ({'PASS' if h18_sec else 'FAIL'}): best |rho|={best_pulse_rho:.3f} >= 0.85? "
          f"(Probe-11 EIS best |rho| = 0.93 for R_diff_400)")

    # also: EIS rho for reference (Probe 11 reproduction)
    print("\n  [reference] EIS op Spearman rho on merged cohort:")
    for c in EIS_COLS:
        rho, p = spearmanr(merged[c].values, soh)
        print(f"    {c:14s} rho={rho:+.3f} p={p:.4f}")

    # ---- SOH tertiles ----
    t1, t2 = np.quantile(soh, [1/3, 2/3])
    bins = np.array([t1, t2])
    labels = cell_labels(merged, bins)

    # ---- H18-main: PERMANOVA on {EIS_6D, pulse_9D, combined_15D} x {k=2,3} ----
    print(f"\n=== H18-main + F2/F3: PERMANOVA on SOH tertiles (cell-stratified null) ===")
    print(f"  Probe-11 reference: EIS_6D k=2 F={PROBE11_REF_F_K2}")
    results = []
    for fname, fcols in [("EIS_6D", EIS_COLS), ("pulse_9D", PULSE_COLS), ("combined_15D", EIS_COLS + PULSE_COLS)]:
        for k in [2, 3]:
            F, p_n, p_c = perm_F_p(merged[fcols].values.astype(float), labels, cells, k)
            results.append({"feature_set": fname, "n_feat": len(fcols), "pca_k": k,
                            "F": float(F), "p_naive": float(p_n), "p_cellstrat": float(p_c)})
            print(f"  {fname:14s} k={k}: F={F:7.3f}  p_naive={p_n:.4f}  p_cellstrat={p_c:.4f}")
    rdf = pd.DataFrame(results)

    eis_F_k2 = float(rdf[(rdf.feature_set == "EIS_6D") & (rdf.pca_k == 2)].F.iloc[0])
    pulse_F_k2 = float(rdf[(rdf.feature_set == "pulse_9D") & (rdf.pca_k == 2)].F.iloc[0])
    comb_F_k2 = float(rdf[(rdf.feature_set == "combined_15D") & (rdf.pca_k == 2)].F.iloc[0])

    # F2: EIS_6D F at k=2 reproduces Probe 11 within 5%
    f2_ok = abs(eis_F_k2 - PROBE11_REF_F_K2) / PROBE11_REF_F_K2 < 0.05
    print(f"\n  F2 ({'PASS' if f2_ok else 'FAIL'}): EIS k=2 F={eis_F_k2:.2f} vs Probe-11 ref {PROBE11_REF_F_K2} (diff {abs(eis_F_k2-PROBE11_REF_F_K2)/PROBE11_REF_F_K2*100:.1f}%)")
    h18_main = comb_F_k2 >= 1.25 * eis_F_k2
    print(f"  H18-main ({'PASS' if h18_main else 'FAIL'}): combined F={comb_F_k2:.2f} >= 1.25x EIS F={eis_F_k2:.2f} ({comb_F_k2/eis_F_k2:.2f}x)")

    # F4: operator-dominance check — does ANY single 1D pulse op alone match comb F?
    print(f"\n=== F4 operator-dominance check (1-D PERMANOVA per pulse op) ===")
    f4_violator = None; max_1d_F = -np.inf
    for c in PULSE_COLS:
        x = merged[c].values.astype(float).reshape(-1, 1)
        pca = (x - x.mean()) / (x.std() if x.std() > 0 else 1)
        F1d = permanova_pseudoF(cosine_dist(pca), labels)
        if F1d > max_1d_F:
            max_1d_F = F1d
        if F1d >= comb_F_k2:
            f4_violator = c
        print(f"  {c:30s} 1D F = {F1d:7.3f}")
    f4_ok = (f4_violator is None)
    print(f"\n  F4 ({'PASS' if f4_ok else 'FAIL — illusion'}): max 1D pulse F = {max_1d_F:.2f} < combined F = {comb_F_k2:.2f}? {'YES' if f4_ok else f'NO ({f4_violator})'}")

    # ---- disposition ----
    if not f2_ok:
        disp = "PROBE 18 INVALID (EIS baseline reproduction failed)"
    elif not f1_ok:
        disp = "PULSE-OPS-NULL (no pulse op tracks SOH)"
    elif h18_main and h18_sec:
        disp = "PULSE-OPS-SUPERIOR (P14 class win ports to real cells)"
    elif h18_main:
        disp = "PULSE-OPS-COMPLEMENTARY (adds to EIS, not single-op superior)"
    else:
        disp = "PULSE-OPS-REDUNDANT (tracks SOH but no additive value)"

    print("\n" + "=" * 76)
    print("PROBE 18 DISPOSITION (per lit/70 §5)")
    print("=" * 76)
    print(f"  F1 pulse-tracks-SOH:      {'PASS' if f1_ok else 'FAIL'} (best |rho|={best_pulse_rho:.3f})")
    print(f"  F2 EIS baseline:          {'PASS' if f2_ok else 'FAIL'} (EIS F={eis_F_k2:.2f} vs ref {PROBE11_REF_F_K2})")
    print(f"  F4 no single-op illusion: {'PASS' if f4_ok else 'FAIL'} (max 1D F={max_1d_F:.2f})")
    print(f"  H18-secondary (|rho|>=0.85): {'PASS' if h18_sec else 'FAIL'}")
    print(f"  H18-main (combined>=1.25x EIS): {'PASS' if h18_main else 'FAIL'} (combined {comb_F_k2:.2f}/EIS {eis_F_k2:.2f}={comb_F_k2/eis_F_k2:.2f}x)")
    print(f"\n  ==> {disp}")

    pd.concat([
        rho_df.assign(block="rho"),
        rdf.assign(block="permanova"),
        pd.DataFrame([{"block": "disposition", "feature_set": disp,
                       "F": comb_F_k2, "p_cellstrat": float(rdf[(rdf.feature_set=='combined_15D')&(rdf.pca_k==2)].p_cellstrat.iloc[0]),
                       "n_feat": int(len(merged))}]),
    ], ignore_index=True).to_parquet(OUT)
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
