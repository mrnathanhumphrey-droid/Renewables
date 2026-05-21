"""
Phase 2.3 — Operator feature extraction pipeline.

Outputs per-(cell, RPT) feature table to data/processed/features.parquet:
  cell_id, lifecycle, rpt_idx, cycle_count_estimate,
  Q_max_Ah,
  R_ohmic_soc20, R_ohmic_soc50, R_ohmic_soc80,    # EIS high-f real impedance
  R_diff_soc20,  R_diff_soc50,  R_diff_soc80,     # EIS low-f real impedance
  R_DC_pulse,                                      # HPPC pulse DC resistance
  tau_pulse_s,                                     # HPPC pulse time constant

Triad assignment derived from feature availability:
  alpha: {Q_max, R_ohmic, R_diff}   when EIS available
  beta : {Q_max, R_DC,    tau    }  when HPPC available, EIS missing

Defers raw-cycling thermal-operator extraction (would need 6.4 GB raw .xlsx pass).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.optimize import curve_fit


DATA_DIR = Path("D:/Renewables/Battery/data")
OUT_DIR = DATA_DIR / "processed"
OUT_DIR.mkdir(exist_ok=True)


def _is_valid_array(x):
    return not np.isscalar(x) and np.ndim(x) > 0 and np.size(x) > 0


def extract_capacity_feature(cap_struct, cell_col, rpt_row):
    """Q_max = max discharge capacity observed in the test (Ah)."""
    q = cap_struct["cap"][rpt_row, cell_col]
    if not _is_valid_array(q):
        return np.nan
    return float(np.max(q) - np.min(q))


def extract_eis_features(eis_struct, cell_col, rpt_row, soc_levels=(20, 50, 80)):
    """EIS sub-operators per SOC level:
      R_ohmic  = Re(Z) at highest frequency (≈ contact + electrolyte resistance)
      R_diff   = Re(Z) at lowest frequency (≈ ohmic + charge-transfer + Warburg-tail)

    Returns dict; missing values -> NaN.
    """
    freq = eis_struct["freq"][rpt_row, cell_col]
    re_z = eis_struct["re_z"][rpt_row, cell_col]

    if not _is_valid_array(freq) or not _is_valid_array(re_z):
        return {f"R_ohmic_soc{s}": np.nan for s in soc_levels} | {f"R_diff_soc{s}": np.nan for s in soc_levels}

    # First-life shape: (n_freqs, n_soc_levels). Columns ordered per eis_struct['soc_level']
    soc_axis = eis_struct["soc_level"]
    out = {}
    for s in soc_levels:
        # locate the SOC column
        idx = np.where(np.asarray(soc_axis) == s)[0]
        if len(idx) == 0:
            out[f"R_ohmic_soc{s}"] = np.nan
            out[f"R_diff_soc{s}"] = np.nan
            continue
        c = idx[0]
        f_col = freq[:, c]
        r_col = re_z[:, c]
        # high-f point
        hf = np.argmax(f_col)
        # low-f point
        lf = np.argmin(f_col)
        out[f"R_ohmic_soc{s}"] = float(r_col[hf])
        out[f"R_diff_soc{s}"] = float(r_col[lf])
    return out


def _pulse_response(t, R_inf, R0, tau):
    """Single-RC pulse-response model: V_rest(t) = R_inf + R0 * exp(-t / tau)."""
    return R_inf + R0 * np.exp(-t / tau)


def extract_hppc_features(hppc_struct, cell_col, rpt_row):
    """Fit a single-RC model to the first observed pulse rest segment.

    Returns {R_DC_pulse, tau_pulse_s}. Missing -> NaN.

    Strategy: HPPC consists of rest -> pulse -> rest -> pulse ... segments. The
    DC resistance is best estimated as |ΔV / ΔI| at the immediate pulse instant.
    The time constant comes from the post-pulse voltage relaxation fit.
    """
    t = hppc_struct["time"][rpt_row, cell_col]
    v = hppc_struct["vcell"][rpt_row, cell_col]
    i = hppc_struct["curr"][rpt_row, cell_col]
    if not _is_valid_array(v) or not _is_valid_array(i) or not _is_valid_array(t):
        return {"R_DC_pulse": np.nan, "tau_pulse_s": np.nan}

    t = np.asarray(t).flatten()
    v = np.asarray(v).flatten()
    i = np.asarray(i).flatten()

    # Identify the first significant current pulse onset.
    abs_i = np.abs(i)
    if np.max(abs_i) < 0.1:  # no real pulse
        return {"R_DC_pulse": np.nan, "tau_pulse_s": np.nan}

    # threshold = 50% of max current
    threshold = 0.5 * np.max(abs_i)
    above = abs_i > threshold
    # find first transition into pulse
    onset_candidates = np.where(np.diff(above.astype(int)) == 1)[0]
    if len(onset_candidates) == 0:
        return {"R_DC_pulse": np.nan, "tau_pulse_s": np.nan}
    p_start = onset_candidates[0] + 1
    # find pulse end (transition out)
    end_candidates = np.where(np.diff(above.astype(int)) == -1)[0]
    end_after = end_candidates[end_candidates > p_start]
    if len(end_after) == 0:
        return {"R_DC_pulse": np.nan, "tau_pulse_s": np.nan}
    p_end = end_after[0]

    # R_DC = magnitude of the immediate voltage step / current step
    pre_v = v[max(0, p_start - 5)]
    pulse_v = v[p_start + 1] if p_start + 1 < len(v) else v[p_start]
    pulse_i = i[p_start + 1] if p_start + 1 < len(i) else i[p_start]
    if abs(pulse_i) < 0.01:
        return {"R_DC_pulse": np.nan, "tau_pulse_s": np.nan}
    R_DC = abs((pulse_v - pre_v) / pulse_i)

    # Fit relaxation: from p_end to p_end + N samples (capped)
    fit_n = min(500, len(v) - p_end - 1)
    if fit_n < 20:
        return {"R_DC_pulse": float(R_DC), "tau_pulse_s": np.nan}
    t_rel = t[p_end : p_end + fit_n] - t[p_end]
    v_rel = v[p_end : p_end + fit_n]
    try:
        v_inf = v_rel[-1]
        amp_guess = v_rel[0] - v_inf
        popt, _ = curve_fit(
            _pulse_response,
            t_rel,
            v_rel,
            p0=[v_inf, amp_guess, 10.0],
            maxfev=2000,
        )
        tau = abs(popt[2])
    except Exception:
        tau = np.nan
    return {"R_DC_pulse": float(R_DC), "tau_pulse_s": float(tau) if not np.isnan(tau) else np.nan}


def extract_first_life():
    """Build a per-(cell, RPT) feature DataFrame from first-life consolidated .mat files."""
    base = DATA_DIR / "secl_first_life" / "diagnostic_processed"
    cap = sio.loadmat(str(base / "capacity_test.mat"), squeeze_me=True)
    eis = sio.loadmat(str(base / "EIS_test.mat"), squeeze_me=True)
    hp = sio.loadmat(str(base / "HPPC_test.mat"), squeeze_me=True)

    cell_labels = [str(x).strip() for x in cap["col_cell_label"]]
    rows = []
    for cell_idx, label in enumerate(cell_labels):
        for rpt_idx in range(15):
            row = {
                "cell_id": label,
                "lifecycle": "first_life",
                "rpt_idx": rpt_idx + 1,  # 1-based to match row_diag_number
            }
            # capacity
            row["Q_max_Ah"] = extract_capacity_feature(cap, cell_idx, rpt_idx)
            # EIS sub-operators
            row.update(extract_eis_features(eis, cell_idx, rpt_idx))
            # HPPC features
            row.update(extract_hppc_features(hp, cell_idx, rpt_idx))
            rows.append(row)
    df = pd.DataFrame(rows)
    return df


def assign_triad(df):
    """Per-cell triad assignment from feature availability.

    A cell goes into triad alpha if at least 5 RPTs have non-NaN R_ohmic at any SOC,
    otherwise triad beta if HPPC features are available, otherwise 'unavailable'.
    """
    triads = {}
    for cell, group in df.groupby("cell_id"):
        eis_ok = group[["R_ohmic_soc20", "R_ohmic_soc50", "R_ohmic_soc80"]].notna().any(axis=1).sum()
        hppc_ok = group[["R_DC_pulse"]].notna().sum().iloc[0]
        if eis_ok >= 5:
            triads[cell] = "alpha"
        elif hppc_ok >= 5:
            triads[cell] = "beta"
        else:
            triads[cell] = "unavailable"
    df["triad"] = df["cell_id"].map(triads)
    return df, triads


def main():
    print("=== Extracting first-life features ===")
    df_fl = extract_first_life()
    df_fl, triads = assign_triad(df_fl)

    print(f"\nFirst-life: {len(df_fl)} rows, {df_fl['cell_id'].nunique()} cells")
    print("\nPer-cell feature availability:")
    summary = df_fl.groupby("cell_id").agg(
        rpts_total=("rpt_idx", "count"),
        capacity_n=("Q_max_Ah", lambda s: s.notna().sum()),
        eis_ohmic_n=("R_ohmic_soc50", lambda s: s.notna().sum()),
        hppc_n=("R_DC_pulse", lambda s: s.notna().sum()),
        triad=("triad", "first"),
    )
    print(summary.to_string())

    print("\nTriad counts:")
    print(df_fl.drop_duplicates("cell_id")["triad"].value_counts())

    out_path = OUT_DIR / "features_first_life.parquet"
    df_fl.to_parquet(out_path)
    print(f"\nWritten: {out_path}")

    # Quick aging-trajectory sanity check for alpha cells
    print("\n=== Alpha-triad capacity trajectories ===")
    alpha_cells = [c for c, t in triads.items() if t == "alpha"]
    pivot = df_fl[df_fl["cell_id"].isin(alpha_cells)].pivot(
        index="rpt_idx", columns="cell_id", values="Q_max_Ah"
    )
    print(pivot.to_string(float_format=lambda x: f"{x:.3f}" if pd.notna(x) else "    -"))


if __name__ == "__main__":
    main()
