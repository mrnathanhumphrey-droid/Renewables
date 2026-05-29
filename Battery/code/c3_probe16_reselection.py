"""C3 Probe 16 - Full cascade re-selection under the cross-substrate-primary gate.

Pre-reg: literature/68_probe16_cascade_reselection_under_gate_prereg.md (lock 55beb41).
Inputs (reused unchanged):
  paper2_gate_I_v2_results.parquet, paper2_gate_II_v2_results.parquet,
  paper2_operators_{khan,secl,zhang,wmg}.parquet, data/khan_2025/cell_conditions.csv
Output:
  data/processed/probe16_reselection_results.parquet

Applies the locked XS-primary selection procedure (lit/68 §0.1) to all 12 catalog operators:
  XS-1 extractability on held-out snapshot WMG (PRIMARY) + >=2 real training cohorts
  XS-2 modality-matched stability  (reuse Gate-I v2 passed flag)
  XS-3 modality-matched discrimination (Gate-II Khan AUC >= 0.70)
Emits attrition + re-selected set; validates the re-selected cascade transfer to WMG SOH
(200-seed multi-seed gate, reusing Probe-15 machinery), with a comparison panel.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe15_crosssubstrate_gate import (
    load_training, cascade_F, F_FLOOR, N_SEEDS, REF_SEED,
)

PROCESSED = Path("D:/Renewables/Battery/data/processed")
OUT = PROCESSED / "probe16_reselection_results.parquet"
AUC_THRESH = 0.70

ALL_OPS = ["T1_Q_fade_early", "T2_Q_fade_late", "T3_Q_knee_onset",
           "T4_R_DC_growth_rate", "T5_R_DC_acceleration",
           "E1_ohmic_intercept", "E2_charge_transfer_radius", "E3_diffusion_slope",
           "C1_R_growth_per_Q_lost", "C2_R_DC_to_R_total",
           "CE1_coulombic_drift", "D1_dQdV_peak_shift"]
REAL_TRAIN = ["khan", "secl", "zhang", "severson"]


def extractable(df, op, k=3):
    return (op in df.columns) and (np.isfinite(df[op].values.astype(float)).sum() >= k)


def main():
    g1 = pd.read_parquet(PROCESSED / "paper2_gate_I_v2_results.parquet").set_index("operator")
    g2 = pd.read_parquet(PROCESSED / "paper2_gate_II_v2_results.parquet").set_index("operator")
    parqs = {c: pd.read_parquet(PROCESSED / f"paper2_operators_{c}.parquet")
             for c in ["khan", "secl", "zhang", "severson", "wmg"]}

    # ---- XS-primary procedure ----
    print("=== XS-primary re-selection procedure (12 operators) ===")
    rows = []
    for op in ALL_OPS:
        wmg_ok = extractable(parqs["wmg"], op)
        n_realtrain = sum(extractable(parqs[c], op) for c in REAL_TRAIN)
        xs1 = wmg_ok and (n_realtrain >= 2)
        xs2 = bool(g1.loc[op, "passed_gate_I"]) if op in g1.index else False
        auc_khan = float(g2.loc[op, "AUC_Khan"]) if (op in g2.index and np.isfinite(g2.loc[op, "AUC_Khan"])) else float("nan")
        xs3 = np.isfinite(auc_khan) and (auc_khan >= AUC_THRESH)
        reselected = xs1 and xs2 and xs3
        rows.append({"operator": op, "wmg_extractable": wmg_ok, "n_real_train": n_realtrain,
                     "XS1_extractability": xs1, "XS2_stability": xs2,
                     "AUC_Khan": auc_khan, "XS3_discrimination": xs3, "reselected": reselected})
    attr = pd.DataFrame(rows)
    print(attr.to_string(index=False))
    reselected = attr[attr.reselected]["operator"].tolist()
    xs1_set = attr[attr.XS1_extractability]["operator"].tolist()
    print(f"\nAttrition: 12 -> XS-1 {len(xs1_set)} {xs1_set} -> XS-2&3 -> RE-SELECTED {len(reselected)}: {reselected}")

    # within-substrate 7-op set + WMG extractability (F2)
    ws7 = g2[g2.passed_gate_II].index.tolist()
    ws7_wmg = [op for op in ws7 if extractable(parqs["wmg"], op)]
    print(f"\nWithin-substrate Gate-I+II set ({len(ws7)}): {ws7}")
    print(f"  of those, extractable on snapshot WMG: {ws7_wmg}  (F2 expects <=1)")

    # ---- validation: re-selected cascade + comparison panel ----
    khan, secl, zhang, klab, slab, zlab = load_training()
    wmg = parqs["wmg"]; soh_bins = wmg["soh_eis"].values
    y = np.concatenate([klab, slab, zlab])

    panel = {"RESELECTED": reselected,
             "C2_only": ["C2_R_DC_to_R_total"],
             "E1E2C2_probe15": ["E1_ohmic_intercept", "E2_charge_transfer_radius", "C2_R_DC_to_R_total"]}
    print(f"\n=== Validation panel (train {{Khan,SECL,Zhang}} n={len(y)}, test WMG, {N_SEEDS}-seed) ===")
    vrows = []
    for name, feats in panel.items():
        if not feats:
            continue
        Xtr = np.vstack([khan[feats].values, secl[feats].values, zhang[feats].values]).astype(float)
        Xwmg = wmg[feats].values.astype(float)
        Fs = np.array([cascade_F(feats, b, Xtr, y, Xwmg, soh_bins) for b in range(N_SEEDS)])
        med, lo, hi = np.nanmedian(Fs), np.nanpercentile(Fs, 2.5), np.nanpercentile(Fs, 97.5)
        (F_ref, p_ref), _, _, _ = cascade_F(feats, REF_SEED, Xtr, y, Xwmg, soh_bins, with_p=True)
        robust = (med > F_FLOOR) and (lo > F_FLOOR) and (p_ref < 0.05)
        vrows.append({"feature_set": name, "features": "+".join(feats), "n_feat": len(feats),
                      "F_median": med, "F_2.5pct": lo, "F_97.5pct": hi, "F_ref": F_ref,
                      "p_ref": p_ref, "robust_pass": robust})
        print(f"  {name:16s} {feats}")
        print(f"      F median={med:.3f} [{lo:.3f},{hi:.3f}]  ref F={F_ref:.3f} p={p_ref:.4f}  robust={'PASS' if robust else 'FAIL'}")

    vdf = pd.DataFrame(vrows)
    pd.concat([attr.assign(block="attrition"), vdf.assign(block="validation")], ignore_index=True).to_parquet(OUT)

    # ---- disposition ----
    resel = next(r for r in vrows if r["feature_set"] == "RESELECTED")
    h16_selection = (set(reselected) & {"E1_ohmic_intercept", "E2_charge_transfer_radius", "C2_R_DC_to_R_total"}) \
        and not (set(reselected) & {"T1_Q_fade_early", "T2_Q_fade_late", "T3_Q_knee_onset", "T4_R_DC_growth_rate", "T5_R_DC_acceleration"})
    f1_ok = len(reselected) > 0 and all(extractable(parqs["wmg"], op) for op in reselected)
    f2_ok = len(ws7_wmg) <= 1
    h16_main = resel["robust_pass"]

    if not f1_ok:
        disp = "PROCEDURE-DEGENERATE (empty/non-WMG-extractable re-selected set)"
    elif h16_selection and h16_main and f2_ok:
        disp = "XS-GATE-YIELDS-TRANSFERABLE-CASCADE"
    elif h16_selection and not h16_main:
        disp = "XS-GATE-SELECTS-BUT-NO-TRANSFER"
    else:
        disp = "AMBIGUOUS (see falsifiers)"

    print("\n" + "=" * 74)
    print("PROBE 16 DISPOSITION (per lit/68 §5)")
    print("=" * 74)
    print(f"  Re-selected set: {reselected}")
    print(f"  H16-selection (EIS kept, trajectory dropped): {'YES' if h16_selection else 'NO'}")
    print(f"  F1 procedure non-degenerate:                  {'PASS' if f1_ok else 'FAIL'}")
    print(f"  F2 within-substrate set <=1 WMG-extractable:  {'PASS' if f2_ok else 'FAIL'} ({ws7_wmg})")
    print(f"  H16-main re-selected cascade transfers:       {'PASS' if h16_main else 'FAIL'} (median F={resel['F_median']:.2f} [{resel['F_2.5pct']:.2f},{resel['F_97.5pct']:.2f}], p={resel['p_ref']:.3f})")
    print(f"\n  ==> {disp}")
    print(f"\nWritten: {OUT}")
    print("=" * 74)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 74)


if __name__ == "__main__":
    main()
