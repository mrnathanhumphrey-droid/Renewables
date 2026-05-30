"""Probe 18 - SECL second-life HPPC-pulse operator extractor.

Pre-reg: literature/70_probe18_secl_hppc_pulse_operators_prereg.md (lock 497047b).
Output: data/processed/secl_pulse_ops.parquet

For each Capacity_test_with_pulses xlsx, extracts 3 operators per pulse pair (discharge +
charge at 3 SOC levels) -> 9D feature vector per (cell, round):
  R_ohmic_pulse_{soc} = |V_pre - V_pulse_start| / |I_pulse|         (ohmic from voltage jump)
  eta_8s_pulse_{soc}  = |V_pulse_end - V_pulse_start| / |I_pulse|   (kinetic+early-diffusion)
  dV_rebound_{soc}    = |dV/dt| during first ~10s post-pulse rest   (early relaxation)
Discharge (steps 6/10/14, I>0) and charge (steps 8/12/16, I<0) pulses at same SOC averaged.
SOC indexed by voltage convention 326/363/400 mV (matches Probe 11 EIS).
"""

import re, os, glob
import numpy as np
import pandas as pd

ROOT = "D:/Renewables/Battery/data/secl_second_life/SL_Dataset_SECL_INR21700-M50T"
OUT = "D:/Renewables/Battery/data/processed/secl_pulse_ops.parquet"
REBOUND_WINDOW_S = 10.0

# step_index -> (soc_label_volt, pulse_kind)
PULSE_STEPS = {6: (400, "dis"), 8: (400, "chg"),
               10: (363, "dis"), 12: (363, "chg"),
               14: (326, "dis"), 16: (326, "chg")}
CELL_RE = re.compile(r"_(g1|v4|v5|w8|w9|w10|w3|w4|w5|w7)_", re.IGNORECASE)
RPT_RE = re.compile(r"RPT_(\d+)", re.IGNORECASE)


def extract_pulse_ops(df, step_idx):
    """Return dict(R_ohmic, eta_8s, dV_rebound) for one pulse step, or None on failure."""
    S = df["Step_Index"].values
    T = df["Test_Time(s)"].values
    V = df["Voltage(V)"].values
    I = df["Current(A)"].values
    mask = S == step_idx
    if mask.sum() < 4:
        return None
    idx = np.where(mask)[0]
    i_start, i_end = idx[0], idx[-1]
    if i_start == 0:
        return None
    # pre-pulse rest sample (immediately before pulse start)
    V_pre = float(V[i_start - 1])
    V_ps = float(V[i_start])
    V_pe = float(V[i_end])
    I_p = float(np.mean(I[mask]))
    if abs(I_p) < 0.1:
        return None
    R_ohmic = abs(V_pre - V_ps) / abs(I_p)
    eta_8s = abs(V_pe - V_ps) / abs(I_p)
    # rebound: linear slope of V vs t over first REBOUND_WINDOW_S of next step
    next_mask = (S == S[i_end + 1]) if (i_end + 1) < len(S) else None
    dV_rebound = float("nan")
    if next_mask is not None and next_mask.sum() >= 3:
        next_idx = np.where(next_mask)[0]
        t0 = T[next_idx[0]]
        win = next_idx[T[next_idx] - t0 <= REBOUND_WINDOW_S]
        if len(win) >= 3:
            tw, vw = T[win] - t0, V[win]
            # least-squares slope
            slope = np.polyfit(tw, vw, 1)[0]
            dV_rebound = abs(float(slope))
    return {"R_ohmic": R_ohmic, "eta_8s": eta_8s, "dV_rebound": dV_rebound}


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "diagnostic_tests", "RPT_*",
                                          "Capacity_test_with_pulses", "**", "*.xlsx"),
                             recursive=True))
    files = [f for f in files if "MACOSX" not in f and "Channel" in f]
    print(f"Pulse xlsx files: {len(files)}")

    rows = []
    fail = 0
    for f in files:
        base = os.path.basename(f)
        mc = CELL_RE.search(f); mr = RPT_RE.search(f)
        if not (mc and mr):
            continue
        cell = mc.group(1).lower(); rnd = int(mr.group(1))
        try:
            xl = pd.ExcelFile(f)
            ch = [s for s in xl.sheet_names if s != "Global_Info"][0]
            df = xl.parse(ch)
        except Exception as e:
            print(f"  err {base}: {type(e).__name__}"); fail += 1; continue
        if not {"Step_Index", "Voltage(V)", "Current(A)", "Test_Time(s)"}.issubset(df.columns):
            fail += 1; continue
        # per (soc), collect dis + chg ops then average
        per_soc = {soc: {"R_ohmic": [], "eta_8s": [], "dV_rebound": []} for soc in [326, 363, 400]}
        for step, (soc, kind) in PULSE_STEPS.items():
            r = extract_pulse_ops(df, step)
            if r is None:
                continue
            for k, v in r.items():
                if np.isfinite(v):
                    per_soc[soc][k].append(v)
        row = {"cell": cell, "round": rnd}
        n_complete = 0
        for soc in [326, 363, 400]:
            for op in ["R_ohmic", "eta_8s", "dV_rebound"]:
                vals = per_soc[soc][op]
                row[f"{op}_pulse_{soc}"] = float(np.mean(vals)) if vals else np.nan
            if all(per_soc[soc][op] for op in ["R_ohmic", "eta_8s"]):
                n_complete += 1
        row["n_soc"] = n_complete
        rows.append(row)
    df_out = pd.DataFrame(rows)
    # drop rows where < 2 SOC levels have core ops; median-impute single missing across cohort
    df_out = df_out[df_out["n_soc"] >= 2].copy()
    featcols = [f"{op}_pulse_{soc}" for soc in [326, 363, 400] for op in ["R_ohmic", "eta_8s", "dV_rebound"]]
    for c in featcols:
        df_out[c] = df_out[c].fillna(df_out[c].median())
    df_out = df_out.sort_values(["cell", "round"]).reset_index(drop=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df_out.to_parquet(OUT)

    print(f"\nExtracted: {len(df_out)} (cell, round) rows  (skipped n_soc<2; xlsx fail={fail})")
    print(f"Cells: {sorted(df_out.cell.unique())}")
    print("Per-cell counts:")
    print(df_out.groupby("cell").size().to_string())
    print("\nFeature stats (mOhm-ish or V/s):")
    for c in featcols:
        v = df_out[c]
        print(f"  {c:30s}: median={v.median()*1000:.2f}  min={v.min()*1000:.2f}  max={v.max()*1000:.2f}")
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
