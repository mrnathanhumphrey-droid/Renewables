"""
Paper 2 — Severson per-cell trajectory operators.

Walks data/severson/FastCharge.zip (BEEP-structured), extracts the 12-candidate
operators (where computable on Severson, which lacks EIS):

  Trajectory: T1, T2, T3, T4, T5 (computable -- Severson has long trajectories)
  EIS spectral: E1, E2, E3 (NOT computable -- no EIS)
  Ratios: C1 (R_DC growth / Q fade late); C2 (R_DC/R_total) -- R_total not in
                Severson, so C2 also NOT computable
  Differential: CE1 (computable from charge/discharge per cycle); D1 (dQ/dV
                peak shift, requires cycles_interpolated voltage -- skipping
                for compute reasons, mark NaN)

Per-cell output saved to data/processed/paper2_operators_severson.parquet.
"""

from pathlib import Path
import json
import re
import zipfile
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


ZIP_PATH = Path("D:/Renewables/Battery/data/severson/FastCharge.zip")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")

FRESH_START = 5
FRESH_END = 25
EARLY_END = 50
LATE_START = 100


# Re-use protocol parser from Paper 1's extractor
import sys
sys.path.insert(0, str(Path(__file__).parent))
from severson_extract_features import parse_protocol


def _slope(x, y):
    """Linear-regression slope; NaN if <3 points or all-y NaN."""
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    xx = x[mask]
    yy = y[mask]
    if np.std(xx) < 1e-12:
        return float("nan")
    return float(np.polyfit(xx, yy, 1)[0])


def _knee_onset(cycles, q):
    """Estimate knee onset cycle via second-derivative method on smoothed Q.
    Returns the cycle index of maximum |d^2Q/dn^2|. Smoothing via Savitzky-Golay.
    """
    mask = np.isfinite(cycles) & np.isfinite(q)
    cycles = cycles[mask]
    q = q[mask]
    if len(q) < 21:
        return float("nan")
    win = min(31, len(q) - (1 - len(q) % 2))
    if win < 5:
        return float("nan")
    if win % 2 == 0:
        win -= 1
    try:
        q_smooth = savgol_filter(q, window_length=win, polyorder=3)
        d2 = np.gradient(np.gradient(q_smooth, cycles), cycles)
        # Skip very early/late cycles to find a real knee
        k_lo = max(5, int(0.1 * len(cycles)))
        k_hi = min(len(cycles) - 5, int(0.9 * len(cycles)))
        if k_hi <= k_lo:
            return float("nan")
        k = int(np.argmax(np.abs(d2[k_lo:k_hi]))) + k_lo
        return float(cycles[k])
    except Exception:
        return float("nan")


def extract_operators(zfile, member_name):
    """Return per-cell operator dict, or None on extraction failure."""
    with zfile.open(member_name) as f:
        text = f.read().decode("utf-8", errors="replace")
    data = json.loads(text)
    proto = data.get("protocol", "")
    batch, first_c = parse_protocol(proto)
    summary = data.get("summary", {})
    cycle = np.array(summary.get("cycle_index", []), dtype=float)
    q = np.array(summary.get("discharge_capacity", []), dtype=float)
    qc = np.array(summary.get("charge_capacity", []), dtype=float)
    r = np.array(summary.get("dc_internal_resistance", []), dtype=float)

    if len(cycle) < EARLY_END:
        return None

    # Determine usable cycle range -- avoid post-aged-cycle data if cell crashed
    # Use up to first cycle where Q < 0.70 * fresh_Q (avoid degenerate tail)
    fresh_mask = (cycle >= FRESH_START) & (cycle <= FRESH_END)
    if fresh_mask.sum() < 5:
        return None
    fresh_q = float(np.nanmean(q[fresh_mask]))
    fresh_r = float(np.nanmean(r[fresh_mask]))
    bad = q < (0.5 * fresh_q)
    if bad.any():
        last_good = int(np.argmax(bad))
        cycle = cycle[:last_good]
        q = q[:last_good]
        qc = qc[:last_good]
        r = r[:last_good]

    # T1 -- Q fade rate early (cycles 5-50)
    m_early = (cycle >= FRESH_START) & (cycle <= EARLY_END)
    T1 = _slope(cycle[m_early], q[m_early])

    # T2 -- Q fade rate late (cycles 100+)
    m_late = (cycle >= LATE_START)
    T2 = _slope(cycle[m_late], q[m_late])

    # T3 -- knee onset
    T3 = _knee_onset(cycle, q)

    # T4 -- R_DC growth rate early
    if np.any(np.isfinite(r)):
        T4 = _slope(cycle[m_early], r[m_early])
        # T5 -- max |d^2 R / dn^2| over trajectory
        if (np.isfinite(r)).sum() >= 21:
            try:
                rmask = np.isfinite(r) & np.isfinite(cycle)
                rc = cycle[rmask]
                rr = r[rmask]
                if len(rr) >= 21:
                    win = min(31, len(rr) - (1 - len(rr) % 2))
                    if win % 2 == 0:
                        win -= 1
                    rs = savgol_filter(rr, win, polyorder=3)
                    d2r = np.gradient(np.gradient(rs, rc), rc)
                    k_lo = max(5, int(0.1 * len(rc)))
                    k_hi = min(len(rc) - 5, int(0.9 * len(rc)))
                    if k_hi > k_lo:
                        T5 = float(np.max(np.abs(d2r[k_lo:k_hi])))
                    else:
                        T5 = float("nan")
                else:
                    T5 = float("nan")
            except Exception:
                T5 = float("nan")
        else:
            T5 = float("nan")
    else:
        T4 = float("nan")
        T5 = float("nan")

    # C1 -- R_DC growth per Q lost (T4 / |T2|)
    if np.isfinite(T4) and np.isfinite(T2) and abs(T2) > 1e-12:
        C1 = T4 / abs(T2)
    else:
        C1 = float("nan")

    # C2 -- R_DC / R_total: Severson has only R_DC (internal resistance from
    # BEEP), no R_total equivalent. Mark NaN.
    C2 = float("nan")

    # CE1 -- coulombic efficiency drift (slope of QC/QD vs cycle)
    if np.any(np.isfinite(qc)) and np.any(np.isfinite(q)):
        ce_mask = np.isfinite(qc) & np.isfinite(q) & (q > 0)
        if ce_mask.sum() >= 10:
            ce = qc[ce_mask] / q[ce_mask]
            cyc_ce = cycle[ce_mask]
            CE1 = _slope(cyc_ce, ce)
        else:
            CE1 = float("nan")
    else:
        CE1 = float("nan")

    # D1 -- dQ/dV peak shift; needs voltage curve. Skip for Severson (compute cost).
    D1 = float("nan")

    return {
        "barcode": data.get("barcode"),
        "channel_id": data.get("channel_id"),
        "protocol": proto,
        "batch_date": batch,
        "first_step_C": first_c,
        "fresh_Q": fresh_q,
        "fresh_R": fresh_r,
        "T1_Q_fade_early": T1,
        "T2_Q_fade_late": T2,
        "T3_Q_knee_onset": T3,
        "T4_R_DC_growth_rate": T4,
        "T5_R_DC_acceleration": T5,
        "E1_ohmic_intercept": float("nan"),     # no EIS on Severson
        "E2_charge_transfer_radius": float("nan"),
        "E3_diffusion_slope": float("nan"),
        "C1_R_growth_per_Q_lost": C1,
        "C2_R_DC_to_R_total": C2,
        "CE1_coulombic_drift": CE1,
        "D1_dQdV_peak_shift": D1,
        "cohort": "Severson",
    }


def main():
    print(f"=== Paper 2 Severson trajectory-operator extraction ===\n")
    rows = []
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        members = sorted([m for m in zf.namelist() if m.endswith(".json")])
        for i, m in enumerate(members):
            try:
                op = extract_operators(zf, m)
            except Exception as e:
                print(f"  [err {i+1}/{len(members)}] {m}: {type(e).__name__}: {str(e)[:80]}")
                continue
            if op is None:
                continue
            op["file"] = m
            rows.append(op)
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{len(members)}]  kept={len(rows)}")
    df = pd.DataFrame(rows)
    print(f"\nExtracted {len(df)} cells.")
    out_path = OUT_DIR / "paper2_operators_severson.parquet"
    df.to_parquet(out_path)
    print(f"Written: {out_path}")
    print(f"\nOperator NaN rates:")
    op_cols = [c for c in df.columns if c.startswith(("T", "E", "C", "CE", "D"))]
    for c in op_cols:
        nan_frac = df[c].isna().mean()
        print(f"  {c:30s} NaN={nan_frac*100:5.1f}%")


if __name__ == "__main__":
    main()
