"""C3 Probe 12 - Wide-range (first+second-life) SOH triage analyzer.

Pre-reg: literature/60_probe12_widerange_soh_triage_prereg.md (lock b5e71c7).
Inputs:
  data/processed/secl_firstlife_eis_soh.parquet      (NEW, lifecycle='first')
  data/processed/secl_eis_soh_observations.parquet   (Probe 11, reused; lifecycle='second')
Output:
  data/processed/probe12_widerange_results.parquet

Tests (pre-reg s4/s5):
  F1  - R tracks SOH on the pooled cohort (positive control).
  F4  - cohort-delivery guard: >=3 cells with within-cell SOH span >=7pt.
  H12 - PRIMARY: LOCO PLS(n=2) EIS->SOH, pooled R2>0 + majority cells improve (raw, full 6D).
  F2  - domain confound: logistic CV-AUC first-vs-second at MATCHED SOH (overlap band)
        + harmonized arm (subtract band-estimated domain offset from second-life, re-run LOCO).
  F3  - feature-set stability gate: pooled R2 sign across 6 pre-registered configs (>=4/6 positive).
  PERMANOVA (descriptive, cell-stratified null) for continuity with Probe 11.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe9_extended_permanova import build_pca, cosine_dist, permanova_pseudoF
from c3_probe11_soh_triage import (
    f1_positive_control, loco_regression, cell_labels,
    permanova_naive, permanova_cellstrat, FEATCOLS, SOC_VOLTS,
)

FIRST = Path("D:/Renewables/Battery/data/processed/secl_firstlife_eis_soh.parquet")
SECOND = Path("D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe12_widerange_results.parquet")

PRIMARY_CELLS = ["w8", "w9", "w10", "v4", "v5", "g1"]  # locked pre-reg s2
SECONDLIFE_R2_REF = -4.19  # Probe 11 pooled LOCO R2 (second-life only)

# F3 pre-registered config panel (pre-reg s4 F3)
CONFIGS = {
    "full_6D":      FEATCOLS,
    "drop_326_4D":  [c for c in FEATCOLS if not c.endswith("326")],
    "drop_363_4D":  [c for c in FEATCOLS if not c.endswith("363")],
    "drop_400_4D":  [c for c in FEATCOLS if not c.endswith("400")],
    "Rdiff_only_3D":  [c for c in FEATCOLS if c.startswith("R_diff")],
    "Rohmic_only_3D": [c for c in FEATCOLS if c.startswith("R_ohmic")],
}


def load_pooled():
    a = pd.read_parquet(FIRST)
    b = pd.read_parquet(SECOND)
    if "lifecycle" not in b.columns:
        b = b.copy(); b["lifecycle"] = "second"
    if "lifecycle" not in a.columns:
        a = a.copy(); a["lifecycle"] = "first"
    keep = ["cell", "round", "SOH", "cap_Ah", *FEATCOLS, "n_soc", "lifecycle"]
    df = pd.concat([a[keep], b[keep]], ignore_index=True)
    df = df[df["cell"].isin(PRIMARY_CELLS)].reset_index(drop=True)
    return df


def f4_cohort_guard(df, min_span_pt=7.0, min_cells=3):
    print("\n=== F4 cohort-delivery guard: >=3 cells with within-cell SOH span >=7pt ===")
    spans = []
    for cell, g in df.groupby("cell"):
        span = (g["SOH"].max() - g["SOH"].min()) * 100
        lives = sorted(g["lifecycle"].unique())
        spans.append((cell, span, len(g), lives))
        print(f"  {cell:4s}: n={len(g):3d}  within-cell span {span:4.1f}pt  lifecycles={lives}")
    n_wide = sum(1 for _, s, _, _ in spans if s >= min_span_pt)
    ok = n_wide >= min_cells
    print(f"  cells with span>={min_span_pt}pt: {n_wide}  -> F4 {'PASS' if ok else 'FAIL (VOID)'}")
    return ok, pd.DataFrame(spans, columns=["cell", "span_pt", "n", "lifecycles"])


def f2_domain_confound(df):
    """Domain classifier (first vs second) at MATCHED SOH (overlap band) + harmonized LOCO."""
    print("\n=== F2 domain confound: first-vs-second separability at MATCHED SOH ===")
    first = df[df.lifecycle == "first"]; second = df[df.lifecycle == "second"]
    lo = max(first.SOH.min(), second.SOH.min())
    hi = min(first.SOH.max(), second.SOH.max())
    print(f"  SOH-overlap band: {lo*100:.1f}% - {hi*100:.1f}%")
    band = df[(df.SOH >= lo) & (df.SOH <= hi)].copy()
    nb_first = int((band.lifecycle == "first").sum())
    nb_second = int((band.lifecycle == "second").sum())
    print(f"  in-band rows: first={nb_first}  second={nb_second}")
    auc = float("nan")
    if nb_first >= 5 and nb_second >= 5:
        X = band[FEATCOLS].values.astype(float)
        y = (band.lifecycle == "second").astype(int).values
        nsplit = int(min(5, nb_first, nb_second))
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        cv = StratifiedKFold(n_splits=nsplit, shuffle=True, random_state=12)
        auc = float(np.mean(cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")))
        print(f"  domain classifier {nsplit}-fold CV-AUC = {auc:.3f}  "
              f"(<=0.70 clean / >0.70 confound flagged)")
    else:
        print("  too few in-band rows for a stable classifier (reporting harmonized arm only)")

    # harmonized arm: estimate per-feature domain offset on the band (SOH matched -> pure rig/state offset)
    delta = {}
    for c in FEATCOLS:
        d = float(band.loc[band.lifecycle == "second", c].mean()
                  - band.loc[band.lifecycle == "first", c].mean())
        delta[c] = d
    dfh = df.copy()
    for c in FEATCOLS:
        dfh.loc[dfh.lifecycle == "second", c] = dfh.loc[dfh.lifecycle == "second", c] - delta[c]
    _, r2_harm, mae_harm = loco_regression(dfh)
    print("  per-feature band offset (second-first, mOhm): "
          + ", ".join(f"{c.split('_')[-1]}{'o' if 'ohmic' in c else 'd'}={delta[c]*1000:+.2f}" for c in FEATCOLS))
    print(f"  HARMONIZED LOCO R2 = {r2_harm:.3f}  (conservative read)")
    auc_clean = (not np.isfinite(auc)) or (auc <= 0.70)
    return auc, r2_harm, auc_clean, delta


def f3_stability_panel(df):
    print("\n=== F3 feature-set stability gate (6 pre-registered configs; need >=4/6 R2>0) ===")
    rows = []
    for name, fc in CONFIGS.items():
        _, r2, mae = loco_regression(df, featcols=fc)
        rows.append({"config": name, "n_feat": len(fc), "r2": r2, "positive": r2 > 0})
        print(f"  {name:14s} ({len(fc)}D): pooled R2 = {r2:+.3f}  {'(+)' if r2 > 0 else '(-)'}")
    panel = pd.DataFrame(rows)
    n_pos = int(panel["positive"].sum())
    ok = n_pos >= 4
    print(f"  configs with R2>0: {n_pos}/6  -> F3 {'STABLE' if ok else 'FRAGILE'}")
    return ok, panel, n_pos


def main():
    df = load_pooled()
    print(f"POOLED cohort: {len(df)} obs  cells={sorted(df.cell.unique())}")
    print(f"  by lifecycle: {df.lifecycle.value_counts().to_dict()}")
    print(f"  pooled SOH: {df.SOH.min()*100:.1f}% - {df.SOH.max()*100:.1f}%")

    f1_ok, f1_df = f1_positive_control(df)
    f4_ok, f4_df = f4_cohort_guard(df)

    print("\n=== H12-main PRIMARY: LOCO PLS regression (raw, full 6D) ===")
    percell, r2, mae_pooled = loco_regression(df)
    print(percell.to_string(index=False))
    n_imp = int(percell["improved"].sum()); n_cells = len(percell)
    print(f"\n  Pooled LOCO R2 = {r2:+.3f}  MAE = {mae_pooled*100:.3f}% SOH")
    print(f"  Cells improved over baseline: {n_imp}/{n_cells}")
    print(f"  (Probe 11 second-life-only reference R2 = {SECONDLIFE_R2_REF})")
    h12_pass = (n_imp > n_cells / 2) and (r2 > 0)
    print(f"  H12-main {'PASS' if h12_pass else 'FAIL'} (majority improved AND pooled R2>0)")

    f3_ok, f3_panel, n_pos = f3_stability_panel(df)
    auc, r2_harm, auc_clean, delta = f2_domain_confound(df)
    f2_clean = auc_clean or (r2_harm > 0)

    # descriptive PERMANOVA (cell-stratified)
    print("\n=== DESCRIPTIVE: C3 PERMANOVA on SOH tertiles (cell-stratified null) ===")
    t1, t2 = df["SOH"].quantile([1/3, 2/3]).values
    labels = cell_labels(df, np.array([t1, t2])); cells = df["cell"].values
    feats = df[FEATCOLS].values.astype(float)
    perm_rows = []
    for k in [2, 3]:
        pca, _ = build_pca(feats, k)
        F_n, p_n = permanova_naive(pca, labels, np.random.default_rng(11000 + k))
        F_c, p_c = permanova_cellstrat(pca, labels, cells, np.random.default_rng(12000 + k))
        perm_rows.append({"pca_k": k, "F": F_n, "p_naive": p_n, "p_cellstrat": p_c})
        print(f"  k={k}: F={F_n:.3f}  p_naive={p_n:.4f}  p_cellstrat={p_c:.4f}")
    perm_df = pd.DataFrame(perm_rows)
    sig_cellstrat = bool((perm_df["p_cellstrat"] < 0.0167).any())

    # disposition (pre-reg s5 ladder)
    if not f1_ok:
        disp = "PROBE 12 INVALID (R does not track SOH)"
    elif not f4_ok:
        disp = "PROBE 12 VOID (cohort did not deliver wide within-cell range)"
    elif not h12_pass:
        disp = "RANGE-INSUFFICIENT / FUNDAMENTAL NULL"
    elif not f3_ok:
        disp = "FEATURE-FRAGILE"
    elif not f2_clean:
        disp = "TRANSFERABLE-BUT-DOMAIN-LIMITED"
    else:
        disp = "TRANSFERABLE-TRIAGE (strong)"

    print("\n" + "=" * 72)
    print("PROBE 12 DISPOSITION (per lit/60 sec 5)")
    print("=" * 72)
    print(f"  F1 positive control:        {'PASS' if f1_ok else 'FAIL'}")
    print(f"  F4 cohort-delivery guard:   {'PASS' if f4_ok else 'FAIL'}")
    print(f"  H12-main LOCO (raw 6D):     {'PASS' if h12_pass else 'FAIL'}  (R2={r2:+.3f}, {n_imp}/{n_cells} cells)")
    print(f"  F3 feature-stability gate:  {'STABLE' if f3_ok else 'FRAGILE'}  ({n_pos}/6 configs R2>0)")
    print(f"  F2 domain confound:         AUC={auc:.3f}  harmonized R2={r2_harm:+.3f}  -> {'CLEAN' if f2_clean else 'CONFOUNDED'}")
    print(f"  PERMANOVA (cell-strat):     {'sig' if sig_cellstrat else 'NULL'}")
    print(f"\n  ==> {disp}")

    out = {"r2_raw": r2, "mae_pooled": mae_pooled, "n_improved": n_imp, "n_cells": n_cells,
           "secondlife_ref_r2": SECONDLIFE_R2_REF,
           "f1_ok": f1_ok, "f4_ok": f4_ok, "h12_pass": h12_pass,
           "f3_ok": f3_ok, "n_configs_positive": n_pos,
           "domain_auc": auc, "r2_harmonized": r2_harm, "f2_clean": f2_clean,
           "sig_cellstrat": sig_cellstrat, "disposition": disp}
    pd.DataFrame([out]).to_parquet(OUT)
    perm_df.to_parquet(OUT.with_name("probe12_permanova.parquet"))
    percell.to_parquet(OUT.with_name("probe12_loco_percell.parquet"))
    f3_panel.to_parquet(OUT.with_name("probe12_f3_panel.parquet"))
    print(f"\nWritten: {OUT}")
    print("=" * 72)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 72)


if __name__ == "__main__":
    main()
