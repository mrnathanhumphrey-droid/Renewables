"""Probe 12 - SECL FIRST-life EIS + SOH extractor (direction 2).

Pre-reg: literature/60_probe12_widerange_soh_triage_prereg.md (lock b5e71c7).
Output:  data/processed/secl_firstlife_eis_soh.parquet

Parses the Stanford SECL first-life diagnostic .mat aggregates (MATLAB v7,
scipy-readable; NOT v7.3/HDF5):
- EIS_test.mat : re_z/im_z/freq are (15 diag x 10 cell) object arrays; each
  valid element is an (n_freq x 3 SOC) matrix. soc_level = [20,50,80] %,
  freq grid 10 kHz -> 10 mHz (19 pts). -> R_ohmic (Im=0 intercept) +
  R_diff (Re@10mHz - R_ohmic) per SOC, IDENTICAL definition to the Probe 11
  second-life extractor so features are comparable across lives.
- capacity_test.mat : cap is (15 x 10) object; SOH = max(cap)/4.85 Ah.

SOC -> second-life voltage convention (pre-reg s0.2): 20%->326, 50%->363, 80%->400.
Cell-index -> label per data_analysis.m: 1..10 = W3,W4,W5,W7,W8,W9,W10,G1,V4,V5.
Emits one row per (cell, diagnostic) with the 6D feature + SOH + lifecycle='first',
matching the second-life parquet column schema (plus 'lifecycle').
"""

import os
import numpy as np
import pandas as pd
import scipy.io as sio

BASE = "D:/Renewables/Battery/data/secl_first_life/diagnostic_processed/"
OUT = "D:/Renewables/Battery/data/processed/secl_firstlife_eis_soh.parquet"
NOMINAL_AH = 4.85
# cell column index (0-based) -> label, per data_analysis.m
SOC_TO_VOLT = {0: 326, 1: 363, 2: 400}  # soc_level [20,50,80]% -> 3.26/3.63/4.00 V


def as_2col(x):
    """Coerce an EIS object element to (n_freq, 3) float, or None if missing/NaN."""
    arr = np.asarray(x, dtype=float)
    if arr.ndim == 2 and arr.shape[0] > 1 and arr.shape[1] >= 3:
        return arr
    return None


def r_ohmic_rdiff(freq, re, im):
    """R_ohmic = Re at highest-freq Im=0 crossing (interp; min-Re fallback);
    R_diff = Re@lowest-freq - R_ohmic. Identical to Probe 11 extractor."""
    order = np.argsort(-freq)  # high -> low freq
    fr, re, im = freq[order], re[order], im[order]
    R_ohmic = None
    for i in range(len(im) - 1):
        if im[i] == 0:
            R_ohmic = re[i]; break
        if im[i] * im[i + 1] < 0:  # sign change -> Im=0 crossing
            t = im[i] / (im[i] - im[i + 1])
            R_ohmic = re[i] + t * (re[i + 1] - re[i])
            break
    if R_ohmic is None:
        R_ohmic = float(np.min(re))
    R_low = re[-1]  # lowest freq (10 mHz)
    return float(R_ohmic), float(R_low - R_ohmic)


def main():
    eis = sio.loadmat(BASE + "EIS_test.mat", squeeze_me=True, struct_as_record=False)
    cap_m = sio.loadmat(BASE + "capacity_test.mat", squeeze_me=True, struct_as_record=False)

    labels = [str(x) for x in np.atleast_1d(eis["col_cell_label"]).ravel()]
    re_z, im_z, freq = eis["re_z"], eis["im_z"], eis["freq"]
    diag_num = np.atleast_1d(eis["row_diag_number"]).ravel().astype(int)
    cap = cap_m["cap"]
    cap_diag = np.atleast_1d(cap_m["row_diag_number"]).ravel().astype(int)

    ndiag, ncell = re_z.shape
    assert np.array_equal(diag_num, cap_diag), "EIS/capacity diagnostic rows misaligned"

    rows = []
    skipped_no_cap, skipped_no_eis = 0, 0
    for j in range(ncell):
        cell = labels[j].lower()
        for i in range(ndiag):
            spec_re = as_2col(re_z[i, j])
            if spec_re is None:
                continue  # no EIS this diagnostic
            spec_im = as_2col(im_z[i, j])
            spec_fr = as_2col(freq[i, j])
            if spec_im is None or spec_fr is None:
                continue
            # SOH from capacity of the SAME diagnostic row
            cap_el = np.asarray(cap[i, j], dtype=float).ravel()
            if cap_el.size <= 1 or not np.isfinite(np.nanmax(cap_el)):
                skipped_no_cap += 1
                continue
            cap_ah = float(np.nanmax(cap_el))
            if cap_ah <= 1.0:
                skipped_no_cap += 1
                continue
            soh = cap_ah / NOMINAL_AH

            feat = {"cell": cell, "round": int(diag_num[i]),
                    "SOH": soh, "cap_Ah": cap_ah, "lifecycle": "first"}
            present = 0
            for s, volt in SOC_TO_VOLT.items():
                fr = spec_fr[:, s]; rr = spec_re[:, s]; ii = spec_im[:, s]
                good = np.isfinite(fr) & np.isfinite(rr) & np.isfinite(ii)
                if good.sum() < 4:
                    feat[f"R_ohmic_{volt}"] = np.nan
                    feat[f"R_diff_{volt}"] = np.nan
                    continue
                R_oh, R_df = r_ohmic_rdiff(fr[good], rr[good], ii[good])
                feat[f"R_ohmic_{volt}"] = R_oh
                feat[f"R_diff_{volt}"] = R_df
                present += 1
            feat["n_soc"] = present
            rows.append(feat)

    df = pd.DataFrame(rows)
    # match Probe 11 policy: drop if >1 SOC missing; median-impute single missing
    df = df[df["n_soc"] >= 2].copy()
    featcols = [f"{op}_{v}" for v in SOC_TO_VOLT.values() for op in ["R_ohmic", "R_diff"]]
    for c in featcols:
        df[c] = df[c].fillna(df[c].median())

    # column order: match second-life schema + lifecycle
    cols = ["cell", "round", "SOH", "cap_Ah",
            "R_ohmic_326", "R_diff_326", "R_ohmic_363", "R_diff_363",
            "R_ohmic_400", "R_diff_400", "n_soc", "lifecycle"]
    df = df[cols].sort_values(["cell", "round"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_parquet(OUT)

    print("=" * 70)
    print("FIRST-LIFE COHORT SUMMARY")
    print("=" * 70)
    print(f"Final first-life observations (cell,diag with >=2 SOC + SOH): {len(df)}")
    print(f"Skipped (no/short capacity): {skipped_no_cap}")
    print(f"Independent cells with first-life EIS: {sorted(df['cell'].unique())} (n={df['cell'].nunique()})")
    print("\nPer-cell first-life observation counts + SOH range + within-cell span:")
    for cell, g in df.groupby("cell"):
        lo, hi = g["SOH"].min() * 100, g["SOH"].max() * 100
        print(f"  {cell:4s}: n={len(g):3d}  SOH {lo:5.1f}-{hi:5.1f}%  span {hi-lo:4.1f}pt  rounds {sorted(g['round'].unique())}")
    print(f"\nPooled first-life SOH range: {df['SOH'].min()*100:.1f}-{df['SOH'].max()*100:.1f}%")
    print(f"Written: {OUT}")


if __name__ == "__main__":
    main()
