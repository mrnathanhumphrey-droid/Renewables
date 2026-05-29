"""C3 Probe 13 - R_diff-only / contact-normalized transferable SOH triage.

Pre-reg: literature/62_probe13_rdiff_transferable_soh_triage_prereg.md (lock be6a5d0).
Inputs (reused unchanged):
  data/processed/secl_firstlife_eis_soh.parquet      (lifecycle='first',  SHA 17d66ece...)
  data/processed/secl_eis_soh_observations.parquet   (lifecycle='second', SHA 9dd867c5...)
Output:
  data/processed/probe13_rdiff_results.parquet

Tests (pre-reg s1/s4/s5):
  F1        - R_diff tracks SOH (positive control).
  H13-main  - STABILITY of R_diff-only single-instrument transfer (the 9b gate):
              (a) exhaustive leave-2-cells-out over {W8,W9,W10,V4}: median R2>0
              (b) 500-seed observation-bootstrap LOCO: 2.5th-pct R2>0   (PASS = both)
  H13-cross - train first-life / test second-life, R_diff-only, pooled R2>0 (deployment).
  H13-ohmic - per-cell contact-referenced R_ohmic LOCO R2>0 (mechanism; vs raw -239.96).
  F2        - R_diff-only domain classifier (first-vs-second at matched SOH) AUC vs full-6D 1.000.
NOTE: the full-LOCO R_diff-only +0.768 is ALREADY KNOWN (Probe 12 diagnostic); it is a
calibration anchor reproduced for sanity, NOT a Probe-13 claim (pre-reg s0.3 / F3).
"""

import sys
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe11_soh_triage import loco_regression  # deterministic full-LOCO anchor

FIRST = Path("D:/Renewables/Battery/data/processed/secl_firstlife_eis_soh.parquet")
SECOND = Path("D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe13_rdiff_results.parquet")

RDIFF = ["R_diff_326", "R_diff_363", "R_diff_400"]
ROHMIC = ["R_ohmic_326", "R_ohmic_363", "R_ohmic_400"]
ROHMIC_NORM = ["R_ohmic_norm_326", "R_ohmic_norm_363", "R_ohmic_norm_400"]
ALL6 = ["R_ohmic_326", "R_diff_326", "R_ohmic_363", "R_diff_363", "R_ohmic_400", "R_diff_400"]

H13_MAIN_CELLS = ["w8", "w9", "w10", "v4"]      # first-life n>=5 (anchor cohort, locked)
H13_CROSS_CELLS = ["w8", "w9", "w10", "v4", "v5"]  # present in both lives
KNOWN_ANCHOR = 0.768  # Probe 12 first-life-only R_diff-only LOCO (disclosed, not a claim)


def load():
    a = pd.read_parquet(FIRST)
    b = pd.read_parquet(SECOND)
    if "lifecycle" not in a.columns: a = a.assign(lifecycle="first")
    if "lifecycle" not in b.columns: b = b.assign(lifecycle="second")
    return a.reset_index(drop=True), b.reset_index(drop=True)


def fit_predict(tr, te, featcols):
    Xtr = tr[featcols].values.astype(float); Xte = te[featcols].values.astype(float)
    mu = Xtr.mean(0); sd = Xtr.std(0, ddof=1); sd = np.where(sd < 1e-12, 1e-12, sd)
    pls = PLSRegression(n_components=2)
    pls.fit((Xtr - mu) / sd, tr["SOH"].values)
    return pls.predict((Xte - mu) / sd).ravel()


def r2_of(a, p):
    a = np.asarray(a); p = np.asarray(p)
    ss_res = float(np.sum((a - p) ** 2)); ss_tot = float(np.sum((a - a.mean()) ** 2))
    return 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def contact_normalize(df):
    """Per-cell contact reference: subtract each cell's freshest (max-SOH) R_ohmic per voltage."""
    df = df.copy()
    for v in [326, 363, 400]:
        df[f"R_ohmic_norm_{v}"] = np.nan
    for cell, g in df.groupby("cell"):
        fresh = g["SOH"].idxmax()
        for v in [326, 363, 400]:
            ref = df.loc[fresh, f"R_ohmic_{v}"]
            df.loc[g.index, f"R_ohmic_norm_{v}"] = df.loc[g.index, f"R_ohmic_{v}"] - ref
    return df


def leave2out(df, featcols):
    cells = sorted(df["cell"].unique())
    rows = []
    for test_cells in combinations(cells, 2):
        tr = df[~df["cell"].isin(test_cells)]; te = df[df["cell"].isin(test_cells)]
        pred = fit_predict(tr, te, featcols)
        rows.append({"test": "+".join(test_cells), "train": "+".join([c for c in cells if c not in test_cells]),
                     "r2": r2_of(te["SOH"].values, pred)})
    return pd.DataFrame(rows)


def bootstrap_loco(df, featcols, n=500):
    cells = sorted(df["cell"].unique())
    r2s = []
    for b in range(n):
        rng = np.random.default_rng(b)
        a_all, p_all = [], []
        for held in cells:
            tr = df[df["cell"] != held]; te = df[df["cell"] == held]
            idx = rng.choice(len(tr), size=len(tr), replace=True)
            trb = tr.iloc[idx]
            try:
                pred = fit_predict(trb, te, featcols)
            except Exception:
                pred = np.full(len(te), tr["SOH"].mean())
            a_all.extend(te["SOH"].values); p_all.extend(pred)
        r2s.append(r2_of(a_all, p_all))
    return np.array(r2s)


def f1_control(df, featcols, label):
    any_ok = False
    print(f"  [{label}] F1 R_diff-tracks-SOH:")
    for c in featcols:
        rho, p = spearmanr(df[c], df["SOH"])
        ok = (rho < 0) and (p < 0.05); any_ok = any_ok or ok
        print(f"    {c:14s}: rho={rho:+.3f} p={p:.4f} {'tracks' if ok else ''}")
    return any_ok


def f2_rdiff_domain(both):
    print("\n=== F2: R_diff-ONLY domain classifier (first vs second at matched SOH) ===")
    first = both[both.lifecycle == "first"]; second = both[both.lifecycle == "second"]
    lo = max(first.SOH.min(), second.SOH.min()); hi = min(first.SOH.max(), second.SOH.max())
    band = both[(both.SOH >= lo) & (both.SOH <= hi)]
    nf = int((band.lifecycle == "first").sum()); ns = int((band.lifecycle == "second").sum())
    print(f"  overlap band {lo*100:.1f}-{hi*100:.1f}%  in-band first={nf} second={ns}")
    auc = float("nan")
    if nf >= 5 and ns >= 5:
        X = band[RDIFF].values.astype(float); y = (band.lifecycle == "second").astype(int).values
        ns_fold = int(min(5, nf, ns))
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
        cv = StratifiedKFold(n_splits=ns_fold, shuffle=True, random_state=13)
        auc = float(np.mean(cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")))
    reduced = np.isfinite(auc) and auc <= 0.85
    print(f"  R_diff-only domain CV-AUC = {auc:.3f}  (full-6D was 1.000; <=0.85 => confound reduced: {reduced})")
    return auc, reduced


def main():
    fl, sl = load()
    main_fl = fl[fl.cell.isin(H13_MAIN_CELLS)].reset_index(drop=True)
    print(f"H13-main cohort (first-life {H13_MAIN_CELLS}): {len(main_fl)} obs")
    for c, g in main_fl.groupby("cell"):
        print(f"  {c:4s}: n={len(g):2d}  SOH {g.SOH.min()*100:.1f}-{g.SOH.max()*100:.1f}%")

    # F1
    print("\n=== F1 positive control ===")
    f1_ok = f1_control(main_fl, RDIFF, "first-life main")

    # anchor reproduction (KNOWN, not a claim)
    _, anchor_r2, _ = loco_regression(main_fl, featcols=RDIFF)
    print(f"\n[anchor] R_diff-only full-LOCO R2 = {anchor_r2:+.3f} (known {KNOWN_ANCHOR}; sanity only, NOT a Probe-13 claim)")

    # ---- H13-main STABILITY GATE ----
    print("\n=== H13-main (a): exhaustive leave-2-cells-out, R_diff-only ===")
    l2 = leave2out(main_fl, RDIFF)
    print(l2.to_string(index=False))
    med_l2 = float(l2["r2"].median())
    print(f"  leave-2-out median R2 = {med_l2:+.3f}  (PASS if >0)")

    print("\n=== H13-main (b): 500-seed observation-bootstrap LOCO, R_diff-only ===")
    boot = bootstrap_loco(main_fl, RDIFF, n=500)
    b_med = float(np.nanmedian(boot)); b_lo = float(np.nanpercentile(boot, 2.5)); b_hi = float(np.nanpercentile(boot, 97.5))
    print(f"  bootstrap R2: median={b_med:+.3f}  2.5pct={b_lo:+.3f}  97.5pct={b_hi:+.3f}  (PASS if 2.5pct>0)")
    h13_main_pass = (med_l2 > 0) and (b_lo > 0)
    print(f"  H13-main {'PASS' if h13_main_pass else 'FAIL'} (leave-2-out median>0 AND bootstrap 2.5pct>0)")

    # ---- H13-cross ----
    print("\n=== H13-cross: train first-life / test second-life, R_diff-only ===")
    tr = fl[fl.cell.isin(H13_CROSS_CELLS)]; te = sl[sl.cell.isin(H13_CROSS_CELLS)]
    print(f"  train(first)={len(tr)} obs  test(second)={len(te)} obs  cells={H13_CROSS_CELLS}")
    pred = fit_predict(tr, te, RDIFF)
    cross_r2 = r2_of(te["SOH"].values, pred)
    cross_mae = float(np.mean(np.abs(pred - te["SOH"].values)))
    print("  per-cell (held second-life):")
    for c, g in te.groupby("cell"):
        gp = fit_predict(tr, g, RDIFF)
        print(f"    {c:4s}: n={len(g):2d}  pred {gp.mean()*100:.1f}%  actual {g.SOH.mean()*100:.1f}%  MAE {np.mean(np.abs(gp-g.SOH.values))*100:.2f}%")
    print(f"  H13-cross pooled R2 = {cross_r2:+.3f}  MAE = {cross_mae*100:.2f}%  (PASS if >0)")
    h13_cross_pass = cross_r2 > 0

    # ---- H13-ohmic mechanism ----
    print("\n=== H13-ohmic: per-cell contact-referenced R_ohmic LOCO (vs raw -239.96) ===")
    mn = contact_normalize(main_fl)
    _, ohmic_norm_r2, _ = loco_regression(mn, featcols=ROHMIC_NORM)
    _, ohmic_raw_r2, _ = loco_regression(main_fl, featcols=ROHMIC)
    print(f"  raw R_ohmic-only LOCO R2      = {ohmic_raw_r2:+.3f}")
    print(f"  contact-norm R_ohmic LOCO R2  = {ohmic_norm_r2:+.3f}  (recovery if >0 / sign-flip)")
    h13_ohmic_pass = ohmic_norm_r2 > 0

    # ---- F2 ----
    both = pd.concat([fl[fl.cell.isin(H13_CROSS_CELLS)], sl[sl.cell.isin(H13_CROSS_CELLS)]], ignore_index=True)
    auc, f2_reduced = f2_rdiff_domain(both)

    # ---- disposition (pre-reg s5) ----
    if not f1_ok:
        disp = "PROBE 13 INVALID (R_diff does not track SOH)"
    elif not h13_main_pass:
        disp = "SINGLE-SPLIT ARTIFACT (R_diff-only transfer not robust to resampling)"
    elif h13_cross_pass and f2_reduced:
        disp = "TRANSFERABLE + CROSS-INSTRUMENT"
    elif h13_main_pass and (not h13_cross_pass or not f2_reduced):
        disp = "ROBUST-BUT-RIG-BOUND"
    else:
        disp = "TRANSFERABLE-TRIAGE (robust, single-instrument)"

    print("\n" + "=" * 72)
    print("PROBE 13 DISPOSITION (per lit/62 sec 5)")
    print("=" * 72)
    print(f"  F1 positive control:        {'PASS' if f1_ok else 'FAIL'}")
    print(f"  H13-main STABILITY gate:    {'PASS' if h13_main_pass else 'FAIL'}  (L2 median={med_l2:+.3f}, boot 2.5pct={b_lo:+.3f})")
    print(f"  H13-cross (deployment):     {'PASS' if h13_cross_pass else 'FAIL'}  (R2={cross_r2:+.3f})")
    print(f"  F2 R_diff domain AUC:       {auc:.3f}  ({'reduced' if f2_reduced else 'still confounded'} vs full-6D 1.000)")
    print(f"  H13-ohmic mechanism:        {'recovered' if h13_ohmic_pass else 'not recovered'}  (norm R2={ohmic_norm_r2:+.3f} vs raw {ohmic_raw_r2:+.3f})")
    print(f"\n  ==> {disp}")

    out = {"anchor_r2_known": anchor_r2, "l2_median_r2": med_l2,
           "boot_median_r2": b_med, "boot_lo_r2": b_lo, "boot_hi_r2": b_hi,
           "h13_main_pass": h13_main_pass, "cross_r2": cross_r2, "h13_cross_pass": h13_cross_pass,
           "ohmic_raw_r2": ohmic_raw_r2, "ohmic_norm_r2": ohmic_norm_r2, "h13_ohmic_pass": h13_ohmic_pass,
           "rdiff_domain_auc": auc, "f2_reduced": f2_reduced, "f1_ok": f1_ok, "disposition": disp}
    pd.DataFrame([out]).to_parquet(OUT)
    l2.to_parquet(OUT.with_name("probe13_leave2out.parquet"))
    pd.DataFrame({"boot_r2": boot}).to_parquet(OUT.with_name("probe13_bootstrap.parquet"))
    print(f"\nWritten: {OUT}")
    print("=" * 72)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 72)


if __name__ == "__main__":
    main()
