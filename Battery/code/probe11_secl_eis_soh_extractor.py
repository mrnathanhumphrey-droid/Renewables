"""Probe 11 — SECL second-life EIS + SOH extractor.

Pre-reg: literature/58_probe11_secondlife_soh_triage_prereg.md (lock ed2df82).
Output:  data/processed/secl_eis_soh_observations.parquet

Parses the SECL second-life dataset:
- EIS (Gamry ACIM sheet: Freq/Zmod/Zphz) -> R_ohmic (Im=0 intercept) +
  R_diff (Re@10mHz - R_ohmic), per (cell, RPT-round, SOC voltage).
- Capacity tests -> SOH = max Discharge_Capacity / 4.85 Ah nominal,
  per (cell, RPT-round).
Merges to one row per (cell, round) with the 6D feature
(3 SOC x {R_ohmic, R_diff}) + SOH. Reports final N, per-cell counts,
pooled SOH range, tertile bin edges.
"""

import re
import glob
import os
import numpy as np
import pandas as pd

ROOT = "D:/Renewables/Battery/data/secl_second_life/SL_Dataset_SECL_INR21700-M50T"
OUT = "D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet"
NOMINAL_AH = 4.85
SOC_VOLTS = [326, 363, 400]  # 3.26 / 3.63 / 4.00 V


def parse_eis_file(path):
    """Return (R_ohmic, R_diff) from a Gamry EIS xlsx ACIM sheet."""
    xl = pd.ExcelFile(path)
    acim = [s for s in xl.sheet_names if s.upper().startswith("ACIM")]
    if not acim:
        return None
    df = xl.parse(acim[0])
    if not {"Freq", "Zmod", "Zphz"}.issubset(df.columns):
        return None
    fr = df["Freq"].astype(float).values
    zmod = df["Zmod"].astype(float).values
    zphz = df["Zphz"].astype(float).values
    re = zmod * np.cos(np.deg2rad(zphz))
    im = zmod * np.sin(np.deg2rad(zphz))
    order = np.argsort(-fr)  # high -> low freq
    fr, re, im = fr[order], re[order], im[order]
    # R_ohmic = Re at highest-freq Im=0 crossing (interpolated); fallback min Re
    R_ohmic = None
    for i in range(len(im) - 1):
        if im[i] == 0:
            R_ohmic = re[i]; break
        if im[i] * im[i + 1] < 0:  # sign change
            t = im[i] / (im[i] - im[i + 1])
            R_ohmic = re[i] + t * (re[i + 1] - re[i])
            break
    if R_ohmic is None:
        R_ohmic = float(np.min(re))
    # R_diff = Re at lowest freq - R_ohmic
    R_low = re[-1]
    return float(R_ohmic), float(R_low - R_ohmic)


def parse_capacity_file(path):
    """Return max Discharge_Capacity(Ah) from an Arbin capacity xlsx."""
    xl = pd.ExcelFile(path)
    sheets = [s for s in xl.sheet_names if "Channel" in s and "_" in s and s != "Global_Info"]
    sheet = sheets[-1] if sheets else None
    if sheet is None:
        return None
    df = xl.parse(sheet)
    dcol = [c for c in df.columns if "Discharge_Capacity" in str(c)]
    if not dcol:
        return None
    return float(df[dcol[0]].astype(float).max())


CELL_RE = re.compile(r"_(g1|v4|v5|w8|w9|w10|w3|w4|w5|w7)_", re.IGNORECASE)
RPT_RE = re.compile(r"RPT_(\d+)", re.IGNORECASE)
EISV_RE = re.compile(r"EIS(\d{3})V", re.IGNORECASE)


def main():
    # 1) EIS files
    eis_files = glob.glob(os.path.join(ROOT, "diagnostic_tests", "RPT_*", "EIS_*", "**", "*.xlsx"),
                          recursive=True)
    eis_files = [f for f in eis_files if "MACOSX" not in f]
    print(f"Found {len(eis_files)} EIS xlsx files")
    eis_rows = []
    for f in eis_files:
        base = os.path.basename(f)
        mc = CELL_RE.search(base) or CELL_RE.search(f)
        mr = RPT_RE.search(f)
        mv = EISV_RE.search(base) or EISV_RE.search(f)
        if not (mc and mr and mv):
            continue
        cell = mc.group(1).lower()
        rnd = int(mr.group(1))
        volt = int(mv.group(1))
        if volt not in SOC_VOLTS:
            continue
        try:
            res = parse_eis_file(f)
        except Exception as e:
            print(f"  EIS parse err {base}: {type(e).__name__}")
            continue
        if res is None:
            continue
        R_ohmic, R_diff = res
        eis_rows.append({"cell": cell, "round": rnd, "volt": volt,
                         "R_ohmic": R_ohmic, "R_diff": R_diff})
    eis = pd.DataFrame(eis_rows)
    print(f"Parsed {len(eis)} EIS (cell,round,SOC) points; cells={sorted(eis['cell'].unique())}")

    # 2) capacity only for (cell, round) that have EIS
    need = eis[["cell", "round"]].drop_duplicates()
    cap_files = glob.glob(os.path.join(ROOT, "diagnostic_tests", "RPT_*",
                                       "Capacity_test_with_pulses", "**", "*.xlsx"), recursive=True)
    cap_files = [f for f in cap_files if "MACOSX" not in f and "Channel" in f]
    cap_map = {}
    for f in cap_files:
        mc = CELL_RE.search(os.path.basename(f)) or CELL_RE.search(f)
        mr = RPT_RE.search(f)
        if not (mc and mr):
            continue
        cell = mc.group(1).lower(); rnd = int(mr.group(1))
        if not ((need["cell"] == cell) & (need["round"] == rnd)).any():
            continue
        if (cell, rnd) in cap_map:
            continue
        try:
            cap = parse_capacity_file(f)
        except Exception as e:
            print(f"  cap parse err {os.path.basename(f)}: {type(e).__name__}")
            continue
        if cap and cap > 1.0:
            cap_map[(cell, rnd)] = cap
    print(f"Parsed capacity for {len(cap_map)} (cell,round) combos")

    # 3) pivot EIS to 6D per (cell, round); attach SOH
    rows = []
    for (cell, rnd), grp in eis.groupby(["cell", "round"]):
        if (cell, rnd) not in cap_map:
            continue
        soh = cap_map[(cell, rnd)] / NOMINAL_AH
        feat = {"cell": cell, "round": rnd, "SOH": soh, "cap_Ah": cap_map[(cell, rnd)]}
        present = 0
        for v in SOC_VOLTS:
            sub = grp[grp["volt"] == v]
            if len(sub):
                feat[f"R_ohmic_{v}"] = float(sub["R_ohmic"].iloc[0])
                feat[f"R_diff_{v}"] = float(sub["R_diff"].iloc[0])
                present += 1
            else:
                feat[f"R_ohmic_{v}"] = np.nan
                feat[f"R_diff_{v}"] = np.nan
        feat["n_soc"] = present
        rows.append(feat)
    df = pd.DataFrame(rows)
    # median-impute single missing SOC; drop if >1 missing
    df = df[df["n_soc"] >= 2].copy()
    featcols = [f"{op}_{v}" for v in SOC_VOLTS for op in ["R_ohmic", "R_diff"]]
    for c in featcols:
        df[c] = df[c].fillna(df[c].median())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_parquet(OUT)

    print("\n" + "=" * 70)
    print("COHORT SUMMARY")
    print("=" * 70)
    print(f"Final observations (cell,round with >=2 SOC + SOH): {len(df)}")
    print(f"Independent cells: {sorted(df['cell'].unique())}  (n={df['cell'].nunique()})")
    print("\nPer-cell observation counts + SOH range:")
    for cell, g in df.groupby("cell"):
        print(f"  {cell:4s}: n={len(g):3d}  SOH {g['SOH'].min()*100:.1f}% - {g['SOH'].max()*100:.1f}%  "
              f"rounds {sorted(g['round'].unique())}")
    print(f"\nPooled SOH range: {df['SOH'].min()*100:.1f}% - {df['SOH'].max()*100:.1f}%")
    t1, t2 = df["SOH"].quantile([1/3, 2/3])
    print(f"Tertile bin edges: {t1*100:.2f}% / {t2*100:.2f}%")
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
