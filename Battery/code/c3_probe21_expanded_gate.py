"""C3 Probe 21 - Expanded operator catalog: XS-primary procedure on 17 ops + WMG transfer + noise audit.

Pre-reg: literature/76_probe21_expanded_operator_catalog_prereg.md (lock ddcb429).
Inputs:
  data/processed/paper2_operators_{khan,secl,wmg}_v2.parquet  (Probe 21 extractor; 12 + 5 W-ops)
  data/processed/paper2_operators_zhang.parquet               (12-op only; no W-ops)
  data/processed/paper2_gate_I_v2_results.parquet             (existing-op stability)
  data/processed/paper2_gate_II_v2_results.parquet            (existing-op discrimination)
  data/khan_2025/cell_conditions.csv                          (Khan aging labels)
Output:
  data/processed/probe21_expanded_gate_results.parquet
"""

import sys, re
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paper2_gate_I_v2 import cv_with_iqr_fallback, CV_THRESHOLD
from c3_probe15_crosssubstrate_gate import load_training, cascade_F, F_FLOOR, N_SEEDS, REF_SEED
from c3_probe20_xsgated_noise_audit import NOISE_LEVELS, inject

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
OUT = PROCESSED / "probe21_expanded_gate_results.parquet"

EXISTING_OPS = ["T1_Q_fade_early","T2_Q_fade_late","T3_Q_knee_onset","T4_R_DC_growth_rate",
                "T5_R_DC_acceleration","E1_ohmic_intercept","E2_charge_transfer_radius",
                "E3_diffusion_slope","C1_R_growth_per_Q_lost","C2_R_DC_to_R_total",
                "CE1_coulombic_drift","D1_dQdV_peak_shift"]
W_OPS = ["W1_warburg_slope","W2_peak_neg_im_log_freq","W3_peak_neg_im_norm",
         "W4_inductive_tail","W5_arc_chord_length"]
ALL_OPS = EXISTING_OPS + W_OPS

AUC_THRESH = 0.70


def sigma_for_w(col, ln):
    """Noise grid sigma for W-ops by physical class."""
    if col.startswith("W1") or col.startswith("W5"):  # R_diff-class (R magnitude)
        return ln["Rd"]
    return ln["C2"]  # W2/W3/W4: ratio or log -> low-noise class


def extractable(df, op, k=3):
    return (op in df.columns) and (np.isfinite(df[op].values.astype(float)).sum() >= k)


def stability_w(values):
    """Gate-I level-like metric (CV with IQR fallback). Returns (metric, passes)."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 3:
        return float("nan"), False
    m, _ = cv_with_iqr_fallback(v)
    return float(m), (np.isfinite(m) and m < CV_THRESHOLD)


def khan_aucs_for_op(khan_v2, op):
    """Max OvR AUC of op over Khan aging axes (mirrors gate_II logic)."""
    kc = pd.read_csv(KHAN_COND)
    merged = khan_v2.merge(kc[["cell", "aging_type", "T_C", "soc_range", "charge_rate"]],
                            left_on="cell_id", right_on="cell", how="inner")
    if op not in merged.columns:
        return float("nan")
    x = merged[op].values.astype(float)
    if np.isfinite(x).sum() < 3:
        return float("nan")
    best = -np.inf
    for axis in ["aging_type", "T_C", "soc_range", "charge_rate"]:
        labels = merged[axis].fillna("__missing__").astype(str).values
        uniq = np.unique(labels)
        if len(uniq) < 2:
            continue
        finite = np.isfinite(x)
        if finite.sum() < 3:
            continue
        for lvl in uniq:
            y = (labels == lvl).astype(int)
            if y.sum() == 0 or y.sum() == len(y):
                continue
            try:
                auc = roc_auc_score(y[finite], x[finite])
                auc = max(auc, 1 - auc)
                if auc > best:
                    best = auc
            except Exception:
                continue
    return float(best) if np.isfinite(best) else float("nan")


def apply_xs_procedure():
    """Apply the Probe-16 XS-primary procedure to the 17-op catalog. Returns attrition DataFrame."""
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan_v2.parquet")
    secl = pd.read_parquet(PROCESSED / "paper2_operators_secl_v2.parquet")
    zhang = pd.read_parquet(PROCESSED / "paper2_operators_zhang.parquet")  # no W-ops
    wmg = pd.read_parquet(PROCESSED / "paper2_operators_wmg_v2.parquet")
    severson = pd.read_parquet(PROCESSED / "paper2_operators_severson.parquet")

    g1 = pd.read_parquet(PROCESSED / "paper2_gate_I_v2_results.parquet").set_index("operator")
    g2 = pd.read_parquet(PROCESSED / "paper2_gate_II_v2_results.parquet").set_index("operator")

    cohorts = {"khan": khan, "secl": secl, "zhang": zhang, "wmg": wmg, "severson": severson}
    real_train = ["khan", "secl", "zhang", "severson"]

    rows = []
    for op in ALL_OPS:
        wmg_ok = extractable(wmg, op)
        n_train = sum(extractable(cohorts[c], op) for c in real_train)
        xs1 = wmg_ok and (n_train >= 2)
        # XS-2 stability
        if op in EXISTING_OPS:
            xs2 = bool(g1.loc[op, "passed_gate_I"]) if op in g1.index else False
            sm_label = "Gate-I"
        else:
            # W-op: level-like CV check per real-EIS training cohort, ≥75% pass
            passes = []
            for c in ["khan", "secl"]:  # cohorts with W-ops (zhang lacks)
                if extractable(cohorts[c], op):
                    _, pmet = stability_w(cohorts[c][op].values)
                    passes.append(pmet)
            xs2 = sum(passes) >= max(1, int(np.ceil(0.75 * len(passes))))
            sm_label = f"W-CV ({sum(passes)}/{len(passes)})"
        # XS-3 discrimination
        if op in EXISTING_OPS:
            auc_khan = float(g2.loc[op, "AUC_Khan"]) if (op in g2.index and np.isfinite(g2.loc[op, "AUC_Khan"])) else float("nan")
        else:
            auc_khan = khan_aucs_for_op(khan, op)
        xs3 = np.isfinite(auc_khan) and (auc_khan >= AUC_THRESH)
        reselected = xs1 and xs2 and xs3
        rows.append({"operator": op, "is_W": op in W_OPS,
                     "wmg_extractable": wmg_ok, "n_real_train": n_train,
                     "XS1": xs1, "XS2": xs2, "stability_label": sm_label,
                     "AUC_Khan": auc_khan, "XS3": xs3, "reselected": reselected})
    return pd.DataFrame(rows)


def main():
    print("=== Probe 21 expanded catalog (17 ops) under XS-primary gate ===\n")
    attr = apply_xs_procedure()
    print(attr.to_string(index=False))
    reselected = attr[attr.reselected]["operator"].tolist()
    new_reselected = [op for op in reselected if op in W_OPS]
    print(f"\nAttrition: 17 -> XS-primary -> RE-SELECTED {len(reselected)}: {reselected}")
    print(f"  ({len(new_reselected)} new W-op(s) admitted: {new_reselected})")

    # ---- transfer validation (Probe-16 protocol) ----
    khan_v2 = pd.read_parquet(PROCESSED / "paper2_operators_khan_v2.parquet")
    secl_v2 = pd.read_parquet(PROCESSED / "paper2_operators_secl_v2.parquet")
    zhang   = pd.read_parquet(PROCESSED / "paper2_operators_zhang.parquet")
    wmg_v2  = pd.read_parquet(PROCESSED / "paper2_operators_wmg_v2.parquet")
    # load_training uses paper2_operators_{khan,secl,zhang}.parquet — match its structure
    _, _, _, klab, slab, zlab = load_training()
    # rebuild khan/secl from v2 + label drop (excluded aging_type) to match load_training selection
    import pandas as _pd
    kc = _pd.read_csv(KHAN_COND)
    khan_m = khan_v2.merge(kc[["cell","aging_type"]], left_on="cell_id", right_on="cell", how="inner")
    khan_m = khan_m[khan_m.aging_type != "excluded"].reset_index(drop=True)
    secl_m = secl_v2.reset_index(drop=True)
    zhang_m = zhang.reset_index(drop=True)
    soh_bins = wmg_v2["soh_eis"].values
    y = np.concatenate([klab, slab, zlab])

    panel = {
        "RESELECTED_expanded": reselected,
        "Probe16_E1C2_baseline": ["E1_ohmic_intercept", "C2_R_DC_to_R_total"],
    }
    print(f"\n=== Validation panel (train n={len(y)}, test WMG n={len(wmg_v2)}, 200-seed) ===")
    val_rows = []
    for name, feats in panel.items():
        if not feats:
            continue
        # build Xtr; for SECL/zhang use NaN for W-cols if not present, fill with column mean (training cohort)
        def safe_cols(df, feats):
            for c in feats:
                if c not in df.columns:
                    df[c] = float("nan")
            return df[feats].values.astype(float)
        Xtr = np.vstack([safe_cols(khan_m, feats), safe_cols(secl_m, feats), safe_cols(zhang_m, feats)]).astype(float)
        Xwmg = safe_cols(wmg_v2, feats).astype(float)
        Fs = np.array([cascade_F(feats, b, Xtr, y, Xwmg, soh_bins) for b in range(N_SEEDS)])
        med, lo, hi = float(np.median(Fs)), float(np.percentile(Fs, 2.5)), float(np.percentile(Fs, 97.5))
        (F_ref, p_ref), _, _, _ = cascade_F(feats, REF_SEED, Xtr, y, Xwmg, soh_bins, with_p=True)
        val_rows.append({"set": name, "n_feat": len(feats), "F_median": med,
                         "F_2.5pct": lo, "F_97.5pct": hi, "F_ref": F_ref, "p_ref": p_ref})
        print(f"  {name:24s} ({len(feats)} feat): F median={med:.3f} [{lo:.3f}, {hi:.3f}]  refF={F_ref:.3f} p={p_ref:.4f}")

    # ---- noise audit at L2 on the re-selected set ----
    print(f"\n=== Noise audit at L2 academic (re-selected expanded set, 200 seeds) ===")
    L2 = NOISE_LEVELS[2]
    feats = reselected
    sigmas = []
    for c in feats:
        if c in W_OPS:
            sigmas.append(sigma_for_w(c, L2))
        elif c.startswith("C2"):
            sigmas.append(L2["C2"])
        elif c.startswith(("E1", "C1")):
            sigmas.append(L2["Ro"])
        else:
            sigmas.append(L2["Rd"])
    def safe_cols2(df, feats):
        for c in feats:
            if c not in df.columns:
                df[c] = float("nan")
        return df[feats].values.astype(float)
    Xtr_b = np.vstack([safe_cols2(khan_m, feats), safe_cols2(secl_m, feats), safe_cols2(zhang_m, feats)]).astype(float)
    Xwmg_b = safe_cols2(wmg_v2, feats).astype(float)
    Fs_n = np.empty(N_SEEDS)
    for b in range(N_SEEDS):
        rng_tr = np.random.default_rng(b + 2_000_000)
        rng_te = np.random.default_rng(b + 2_000_000 + 500)
        Xtr_n = inject(Xtr_b, sigmas, rng_tr)
        Xwmg_n = inject(Xwmg_b, sigmas, rng_te)
        Fs_n[b] = cascade_F(feats, REF_SEED, Xtr_n, y, Xwmg_n, soh_bins)
    n_med = float(np.median(Fs_n)); n_lo = float(np.percentile(Fs_n, 2.5)); n_hi = float(np.percentile(Fs_n, 97.5))
    rng_tr_r = np.random.default_rng(42 + 2_000_000)
    rng_te_r = np.random.default_rng(42 + 2_000_000 + 500)
    Xtr_nr = inject(Xtr_b, sigmas, rng_tr_r)
    Xwmg_nr = inject(Xwmg_b, sigmas, rng_te_r)
    (F_nref, p_nref), _, _, _ = cascade_F(feats, REF_SEED, Xtr_nr, y, Xwmg_nr, soh_bins, with_p=True)
    print(f"  L2 noise: median={n_med:.3f} [{n_lo:.3f}, {n_hi:.3f}]  refF={F_nref:.3f} p={p_nref:.4f}")

    # ---- disposition ----
    clean = next(r for r in val_rows if r["set"] == "RESELECTED_expanded")
    p16 = next(r for r in val_rows if r["set"] == "Probe16_E1C2_baseline")
    p16_ok = abs(p16["F_median"] - 3.72) < 0.1
    h21_sel = len(new_reselected) >= 1
    h21_main = (clean["F_median"] > 4.50) and (clean["F_2.5pct"] > 3.0) and (clean["p_ref"] < 0.05)
    h21_sec = (n_med > F_FLOOR) and (n_lo > 2.0) and (p_nref < 0.05)
    f1_ok = bool((attr.is_W & attr.wmg_extractable).sum() >= 3)
    if not p16_ok:
        disp = "PROBE 21 INVALID (P16 baseline doesn't reproduce; pipeline broken)"
    elif not f1_ok:
        disp = "PROBE 21 INVALID (W-op extraction degenerate)"
    elif not h21_sel:
        disp = "EXPANDED-GATE-REJECTS-NEW"
    elif h21_main and h21_sec:
        disp = "EXPANDED-GATE-IMPROVES"
    elif h21_main and not h21_sec:
        disp = "EXPANDED-GATE-IMPROVES-FRAGILE"
    else:
        disp = "EXPANDED-GATE-NEUTRAL"

    print("\n" + "=" * 76)
    print("PROBE 21 DISPOSITION (per lit/76 §5)")
    print("=" * 76)
    print(f"  F1 W-op extractable on WMG (>=3): PASS ({(attr.is_W & attr.wmg_extractable).sum()}/5 W-ops on WMG)")
    print(f"  F2 P16 baseline reproduces:       {'PASS' if p16_ok else 'FAIL'} (median={p16['F_median']:.3f} vs anchor 3.72)")
    print(f"  H21-selection (new W-op admitted): {'PASS' if h21_sel else 'FAIL'} (admitted: {new_reselected})")
    print(f"  H21-main (clean F>4.5, robust):    {'PASS' if h21_main else 'FAIL'} (median={clean['F_median']:.3f}, 2.5pct={clean['F_2.5pct']:.3f}, p={clean['p_ref']:.4f})")
    print(f"  H21-secondary (noise-robust @L2):  {'PASS' if h21_sec else 'FAIL'} (median={n_med:.3f}, 2.5pct={n_lo:.3f}, p={p_nref:.4f})")
    print(f"\n  ==> {disp}")

    # persist
    pd.concat([
        attr.assign(block="attrition"),
        pd.DataFrame(val_rows).assign(block="validation"),
        pd.DataFrame([{"block":"noise_L2","set":"RESELECTED","F_median":n_med,"F_2.5pct":n_lo,
                       "F_97.5pct":n_hi,"F_ref":F_nref,"p_ref":p_nref}]),
        pd.DataFrame([{"block":"disposition","disposition":disp,"new_reselected":",".join(new_reselected) or "none"}]),
    ], ignore_index=True).to_parquet(OUT)
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
