"""
Phase 3.4 prep — Capacity-knee-point detector.

Implements the curvature-based knee identification from Zhang, Altaf, Wik
(2024) arxiv 2304.11671. The knee is the second peak in the absolute
second-derivative of the normalized capacity trajectory; knee-onset is the
earlier curvature deviation that signals the transition into the accelerating-
degradation phase.

For C2's Phase 3.4 lead-time analysis, the relevant comparator is the
knee-point (or knee-onset). We compute both and report.

Approach:
  1. Per cell, build the cycle-vs-Qmax trajectory (cycles from README EIS sheet
     for first-life; second-life cycles from cycling segment summaries —
     deferred since we don't yet have per-segment cycle counts).
  2. Smooth the Q_max trajectory (LOWESS or low-order polynomial) to suppress
     measurement noise.
  3. Compute discrete second derivative d^2Q/dcycle^2.
  4. Knee-point = cycle of MAXIMUM |d^2Q/dcycle^2| (or first peak beyond a
     fresh-period threshold).
  5. Knee-onset = earlier curvature deviation (first |d^2Q/dcycle^2| crossing
     a threshold derived from fresh-period derivative noise).

For this first cut, work only on first-life cells (we have cycle counts from
README EIS sheet). Triad-alpha cells (W8/W9/W10/V4) prioritized.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


OUT_DIR = Path("D:/Renewables/Battery/data/processed")

# Cycle count per (cell, RPT) from Pozzato 2022 README EIS sheet
# (cells with EIS data only; W4/W5/G1 have N for equipment issues)
FIRST_LIFE_CYCLES = {
    "W3":  {1: 0, 2: 25, 3: 75},
    "W7":  {},  # no EIS-cycle data; HPPC-only cell
    "W8":  {1: 0, 2: 25, 3: 75, 4: 125, 5: 148, 6: 150, 7: 151, 8: 157, 9: 185, 10: 222, 11: 247, 12: 272, 13: 297, 14: 322, 15: 347},
    "W9":  {1: 0, 2: 25, 3: 75, 4: 122, 5: 144, 6: 145, 7: 146, 8: 150, 9: 179, 10: 216, 11: 241, 12: 266, 13: 291, 14: 316, 15: 341},
    "W10": {1: 0, 2: 25, 3: 75, 4: 122, 5: 146, 6: 148, 7: 151, 8: 159, 9: 188, 10: 225, 11: 250, 12: 275, 13: 300, 14: 325, 15: 350},
    "V4":  {2: 20, 3: 45, 4: 70, 5: 95, 6: 120, 7: 145, 8: 170, 9: 194, 10: 219, 11: 244},
    "V5":  {2: 12, 3: 18},
}


def detect_knee(cycles, capacity, fresh_n=3):
    """Return (knee_point_cycle, knee_onset_cycle, sigma_baseline).

    Returns NaN for events that can't be measured on the trajectory.
    """
    cycles = np.asarray(cycles, dtype=float)
    capacity = np.asarray(capacity, dtype=float)
    n = len(cycles)

    if n < fresh_n + 4:
        return float("nan"), float("nan"), float("nan")

    # Normalize capacity to initial
    q_norm = capacity / capacity[0]

    # First derivative (using central differences)
    dq = np.gradient(q_norm, cycles)

    # Second derivative
    d2q = np.gradient(dq, cycles)

    # Baseline noise from fresh period of |d2q|
    baseline = np.abs(d2q[:fresh_n])
    sigma = float(np.std(baseline, ddof=1)) if len(baseline) >= 2 else float(np.mean(baseline) + 1e-8)

    # Knee-point: largest |d2q| in the trajectory (excluding the first 2 RPTs
    # which can have spurious large derivatives from edge effects)
    abs_d2q = np.abs(d2q[2:])
    knee_idx_offset = int(np.argmax(abs_d2q))
    knee_idx = knee_idx_offset + 2
    knee_point_cycle = float(cycles[knee_idx])
    knee_magnitude = float(abs_d2q[knee_idx_offset])

    # Knee-onset: first cycle past fresh period where |d2q| exceeds 3*sigma_baseline
    threshold = 3.0 * sigma
    onset_cycle = float("nan")
    for i in range(fresh_n, n):
        if abs(d2q[i]) > threshold:
            onset_cycle = float(cycles[i])
            break

    return knee_point_cycle, onset_cycle, sigma


def detect_knee_with_smoothing(cycles, capacity, window=5, polyorder=2, fresh_n=3):
    """Same as detect_knee but applies Savitzky-Golay smoothing first."""
    cycles = np.asarray(cycles, dtype=float)
    capacity = np.asarray(capacity, dtype=float)
    n = len(cycles)
    if n < max(window, fresh_n + 4):
        return detect_knee(cycles, capacity, fresh_n)
    smoothed = savgol_filter(capacity, window_length=window, polyorder=polyorder)
    return detect_knee(cycles, smoothed, fresh_n)


def main():
    df = pd.read_parquet(OUT_DIR / "features_first_life.parquet")

    results = []
    for cell, group in df.groupby("cell_id"):
        if cell not in FIRST_LIFE_CYCLES or not FIRST_LIFE_CYCLES[cell]:
            continue
        cycle_map = FIRST_LIFE_CYCLES[cell]
        # Pair (cycle, Qmax) for valid RPTs
        rows = []
        for rpt, cycles in cycle_map.items():
            sub = group[group["rpt_idx"] == rpt]
            if sub.empty:
                continue
            q = sub["Q_max_Ah"].iloc[0]
            if pd.notna(q):
                rows.append((cycles, q))
        if len(rows) < 4:
            print(f"[{cell}] only {len(rows)} valid (cycle, Q) points — skipping")
            continue
        rows.sort()
        cycles, qs = zip(*rows)
        knee_raw, onset_raw, sigma_raw = detect_knee(cycles, qs)
        knee_smoothed, onset_smoothed, sigma_smoothed = detect_knee_with_smoothing(cycles, qs, window=5, polyorder=2)
        results.append({
            "cell_id": cell,
            "n_points": len(rows),
            "final_cycle": float(cycles[-1]),
            "final_SOH": float(qs[-1] / qs[0]),
            "knee_cycle_raw": knee_raw,
            "knee_onset_raw": onset_raw,
            "knee_cycle_smoothed": knee_smoothed,
            "knee_onset_smoothed": onset_smoothed,
            "sigma_baseline_raw": sigma_raw,
        })

    print("=== Knee-point detection (first-life cells with EIS-cycle data) ===")
    rdf = pd.DataFrame(results)
    print(rdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    # Lead-time analysis: onset of disagreement (from option X1) vs knee-point
    print("\n=== Lead time: disagreement onset cycle vs knee-point cycle ===")
    # Hardcoded disagreement-onset cycles from Phase 2.4 results
    disagree_onset = {
        "V4": 70,    # RPT 4 -> 70 cycles
        "W8": 148,   # RPT 5
        "W9": 122,   # RPT 4
        "W10": 122,  # RPT 4
    }
    lead = []
    for r in results:
        c = r["cell_id"]
        if c not in disagree_onset:
            continue
        d = disagree_onset[c]
        lead_smoothed = r["knee_cycle_smoothed"] - d if not np.isnan(r["knee_cycle_smoothed"]) else float("nan")
        lead_onset = r["knee_onset_smoothed"] - d if not np.isnan(r["knee_onset_smoothed"]) else float("nan")
        lead.append({
            "cell_id": c,
            "disagreement_onset_cycle": d,
            "knee_point_smoothed": r["knee_cycle_smoothed"],
            "knee_onset_smoothed": r["knee_onset_smoothed"],
            "lead_over_knee_point": lead_smoothed,
            "lead_over_knee_onset": lead_onset,
            "final_SOH": r["final_SOH"],
        })
    ldf = pd.DataFrame(lead)
    print(ldf.to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x, float) else str(x)))

    rdf.to_parquet(OUT_DIR / "knee_point_first_life.parquet")
    print(f"\nWritten: {OUT_DIR / 'knee_point_first_life.parquet'}")


if __name__ == "__main__":
    main()
