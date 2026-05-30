"""C3 Probe 21 - Expanded EIS-spectrum operator extraction (5 W-operators).

Pre-reg: literature/76_probe21_expanded_operator_catalog_prereg.md (lock ddcb429).
Augments existing paper2_operators_{khan,secl,wmg}.parquet with 5 new columns:
  W1_warburg_slope, W2_peak_neg_im_log_freq, W3_peak_neg_im_norm,
  W4_inductive_tail, W5_arc_chord_length
Canonical state per cohort: SOC=50% (Khan S50 / SECL first-life SOC idx 1 / WMG 50SOC), T=25C.
Output: data/processed/paper2_operators_{khan,secl,wmg}_v2.parquet (= original + 5 cols).
"""

import os, re, glob
from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io as sio
import warnings
warnings.filterwarnings("ignore")

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_CSV = Path("D:/Renewables/Battery/data/khan_2025/eis_csv")
WMG_EIS = Path("D:/Renewables/Battery/data/wmg_25cell/DIB_Data/DIB_Data/.csvfiles/EIS_Test")
SECL_FL_MAT = Path("D:/Renewables/Battery/data/secl_first_life/diagnostic_processed/EIS_test.mat")

W_COLS = ["W1_warburg_slope", "W2_peak_neg_im_log_freq", "W3_peak_neg_im_norm",
          "W4_inductive_tail", "W5_arc_chord_length"]


def compute_w_ops(freq, re, im_neg):
    """5 W-operators from (freq, Re, -Im(Z)) arrays. im_neg should be positive in capacitive region."""
    mask = np.isfinite(freq) & np.isfinite(re) & np.isfinite(im_neg)
    if mask.sum() < 10:
        return {c: float("nan") for c in W_COLS}
    f, r, im = freq[mask], re[mask], im_neg[mask]
    # Sort by descending frequency (high to low)
    order = np.argsort(-f)
    f, r, im = f[order], r[order], im[order]
    # R_ohmic via Im=0 sign change (im in the original Im(Z) convention = -im_neg)
    im_z = -im
    R_ohmic = None
    for i in range(len(im_z) - 1):
        if im_z[i] == 0:
            R_ohmic = float(r[i]); break
        if im_z[i] * im_z[i + 1] < 0:
            t = im_z[i] / (im_z[i] - im_z[i + 1])
            R_ohmic = float(r[i] + t * (r[i + 1] - r[i])); break
    if R_ohmic is None or R_ohmic <= 0:
        R_ohmic = float(np.min(r)) if float(np.min(r)) > 0 else float("nan")
    # W1 warburg slope: lowest 30% freq, Re vs omega^-0.5
    n_low = max(3, int(0.3 * len(f)))
    f_low, r_low = f[-n_low:], r[-n_low:]
    omega = 2 * np.pi * f_low
    x = omega ** (-0.5)
    W1 = float(np.polyfit(x, r_low, 1)[0]) if (np.std(x) > 1e-12 and len(x) >= 3) else float("nan")
    # W2 log10 freq at max -Im
    idx_peak = int(np.argmax(im))
    W2 = float(np.log10(f[idx_peak])) if f[idx_peak] > 0 else float("nan")
    # W3 max(-Im) / R_ohmic
    W3 = float(im[idx_peak] / R_ohmic) if (R_ohmic and np.isfinite(R_ohmic) and R_ohmic > 0) else float("nan")
    # W4 (Re@highest - R_ohmic) / R_ohmic
    W4 = float((r[0] - R_ohmic) / R_ohmic) if (R_ohmic and np.isfinite(R_ohmic) and R_ohmic > 0) else float("nan")
    # W5 arc chord length sum in (Re, -Im) space
    dx, dy = np.diff(r), np.diff(im)
    W5 = float(np.sum(np.sqrt(dx ** 2 + dy ** 2)))
    return {"W1_warburg_slope": W1, "W2_peak_neg_im_log_freq": W2,
            "W3_peak_neg_im_norm": W3, "W4_inductive_tail": W4,
            "W5_arc_chord_length": W5}


# ---------- Khan ----------
def extract_khan_w():
    base = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    for c in W_COLS:
        base[c] = float("nan")
    n_ok = 0
    for i, row in base.iterrows():
        cell_id = row["cell_id"]
        path = KHAN_CSV / cell_id / f"ACR_t25_S50_0d_{cell_id}_convert.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if not {"Frequency", "ReZ", "ImZ"}.issubset(df.columns):
            continue
        freq = df["Frequency"].values.astype(float)
        re_arr = df["ReZ"].values.astype(float)
        im_neg = -df["ImZ"].values.astype(float)  # ImZ is Im(Z); im_neg = positive in capacitive region
        ops = compute_w_ops(freq, re_arr, im_neg)
        for c in W_COLS:
            base.at[i, c] = ops[c]
        n_ok += 1
    print(f"  Khan: {n_ok}/{len(base)} cells W-extracted (SOC=50, day=0)")
    out_path = PROCESSED / "paper2_operators_khan_v2.parquet"
    base.to_parquet(out_path)
    return base, out_path


# ---------- WMG ----------
WMG_RE = re.compile(r"^Cell(\d+)_(\d+)SOH_(\d+)degC_(\d+)SOC_\d+\.xls$")

def extract_wmg_w():
    base = pd.read_parquet(PROCESSED / "paper2_operators_wmg.parquet")
    for c in W_COLS:
        base[c] = float("nan")
    # index WMG raw .xls files (canonical T=25, SOC=50)
    cell_to_file = {}
    for p in sorted(WMG_EIS.glob("*.xls")):
        m = WMG_RE.match(p.name)
        if not m:
            continue
        cell, soh, t, soc = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        if t == 25 and soc == 50:
            cell_to_file[cell] = p  # one file per cell at canonical state
    n_ok = 0
    for i, row in base.iterrows():
        cid = row["cell_id"]
        m = re.match(r"WMG_Cell(\d+)", cid)
        if not m:
            continue
        cell_n = int(m.group(1))
        if cell_n not in cell_to_file:
            continue
        df = pd.read_excel(cell_to_file[cell_n], header=None)
        df.columns = ["freq", "ReZ", "negImZ"]
        freq = df["freq"].values.astype(float)
        re_arr = df["ReZ"].values.astype(float)
        im_neg = df["negImZ"].values.astype(float)  # already -Im(Z)
        ops = compute_w_ops(freq, re_arr, im_neg)
        for c in W_COLS:
            base.at[i, c] = ops[c]
        n_ok += 1
    print(f"  WMG: {n_ok}/{len(base)} cells W-extracted (T=25, SOC=50)")
    out_path = PROCESSED / "paper2_operators_wmg_v2.parquet"
    base.to_parquet(out_path)
    return base, out_path


# ---------- SECL first-life ----------
SECL_CELL_ORDER = ["W3", "W4", "W5", "W7", "W8", "W9", "W10", "G1", "V4", "V5"]  # per data_analysis.m

def extract_secl_w():
    base = pd.read_parquet(PROCESSED / "paper2_operators_secl.parquet")
    for c in W_COLS:
        base[c] = float("nan")
    eis = sio.loadmat(str(SECL_FL_MAT), squeeze_me=True, struct_as_record=False)
    re_z = eis["re_z"]; im_z = eis["im_z"]; freq_arr = eis["freq"]
    labels = [str(x) for x in np.atleast_1d(eis["col_cell_label"]).ravel()]
    # SOC=50 -> index 1 (soc_level=[20,50,80])
    SOC_IDX = 1
    n_ok = 0
    for i, row in base.iterrows():
        cell_id = row["cell_id"]  # e.g. "W8"
        try:
            j = labels.index(cell_id)
        except ValueError:
            continue
        # use fresh diagnostic (smallest finite) - find first valid diagnostic
        for d in range(re_z.shape[0]):
            spec_re = np.asarray(re_z[d, j], dtype=float)
            if spec_re.ndim != 2 or spec_re.shape[0] < 5:
                continue
            spec_im = np.asarray(im_z[d, j], dtype=float)
            spec_fr = np.asarray(freq_arr[d, j], dtype=float)
            freq = spec_fr[:, SOC_IDX]
            re_arr = spec_re[:, SOC_IDX]
            im_neg = -spec_im[:, SOC_IDX]  # im_z is Im(Z); im_neg positive for capacitive
            ops = compute_w_ops(freq, re_arr, im_neg)
            if all(np.isfinite(ops[c]) for c in W_COLS):
                for c in W_COLS:
                    base.at[i, c] = ops[c]
                n_ok += 1
                break
    print(f"  SECL first-life: {n_ok}/{len(base)} cells W-extracted (fresh diagnostic, SOC=50)")
    out_path = PROCESSED / "paper2_operators_secl_v2.parquet"
    base.to_parquet(out_path)
    return base, out_path


def main():
    print("=== Probe 21 expanded catalog extraction (5 W-ops on raw EIS spectra) ===")
    khan, _ = extract_khan_w()
    wmg, _  = extract_wmg_w()
    secl, _ = extract_secl_w()
    print("\n=== Per-cohort W-op extractability (>=3 finite) ===")
    for name, df in [("Khan", khan), ("WMG", wmg), ("SECL", secl)]:
        line = f"  {name:6s}: "
        for c in W_COLS:
            n_fin = int(np.isfinite(df[c]).sum())
            line += f"{c.split('_')[0]}={n_fin}/{len(df)} "
        print(line)
    print("\nWritten: paper2_operators_{khan,wmg,secl}_v2.parquet")


if __name__ == "__main__":
    main()
