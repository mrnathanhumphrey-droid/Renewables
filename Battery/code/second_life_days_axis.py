"""
Second-life days-axis Q_max trajectory + knee-point detection + lead-time.

Cycle counts for second-life cycling segments are non-trivial to extract
(per-xlsx Cycle_Index = 1 for Arbin's grid-storage schedule). Pragmatic
alternative: use RPT calendar dates from folder names as the aging axis.

For each cell, days-since-first-RPT trajectory of Q_max → knee detection via
curvature method (Zhang/Altaf/Wik 2024 analog).

Pair with the disagreement-onset day from mahalanobis_option_x1.parquet to
get a second-life lead time in days.

Then merge with first-life cycle-based lead times via lifecycle indicator
in the hierarchical Phase 3 model.
"""

from pathlib import Path
import re
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


BASE = Path("D:/Renewables/Battery/data/secl_second_life/SL_Dataset_SECL_INR21700-M50T/diagnostic_tests")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
CELLS = ["G1", "V4", "V5", "W8", "W9", "W10"]


def get_rpt_dates(rpt_num: int):
    """Return {cell: datetime} for an RPT number, from Capacity_test_with_pulses subfolders."""
    rpt_dir = BASE / f"RPT_{rpt_num}" / "Capacity_test_with_pulses"
    out = {}
    if not rpt_dir.exists():
        return out
    for child in rpt_dir.iterdir():
        if not child.is_dir():
            continue
        m = re.match(r"^(\d{8})_([a-z0-9]+)_RPT$", child.name)
        if not m:
            continue
        date_str, cell_lc = m.group(1), m.group(2).upper()
        if cell_lc not in CELLS:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            out[cell_lc] = dt
        except ValueError:
            continue
    return out


def main():
    # Build per-cell (rpt_num, date) dict
    rpt_dates = {cell: {} for cell in CELLS}
    for rpt_num in range(1, 20):
        dates = get_rpt_dates(rpt_num)
        for cell, dt in dates.items():
            rpt_dates[cell][rpt_num] = dt

    print("=== Second-life RPT date coverage ===")
    for cell in CELLS:
        dts = rpt_dates[cell]
        if dts:
            first_rpt = min(dts.keys())
            last_rpt = max(dts.keys())
            d0 = dts[first_rpt]
            dn = dts[last_rpt]
            total_days = (dn - d0).days
            print(f"  {cell}: RPT_{first_rpt} ({d0.date()}) -> RPT_{last_rpt} ({dn.date()}) = {total_days} days, {len(dts)} RPTs")

    # Load second-life features to get Q_max per (cell, RPT)
    sl = pd.read_parquet(OUT_DIR / "features_second_life.parquet")
    sl["lifecycle"] = "second_life"

    print("\n=== Second-life Q_max trajectories on days axis ===")
    knee_results = []
    for cell in CELLS:
        sub = sl[sl["cell_id"] == cell].sort_values("rpt_idx").reset_index(drop=True)
        sub = sub[["rpt_idx", "Q_max_Ah"]].dropna()
        if sub.empty:
            continue
        rows = []
        for _, r in sub.iterrows():
            rpt = int(r["rpt_idx"])
            if rpt not in rpt_dates[cell] or 1 not in rpt_dates[cell]:
                continue
            d_since = (rpt_dates[cell][rpt] - rpt_dates[cell][1]).days
            rows.append((d_since, r["Q_max_Ah"]))
        if len(rows) < 4:
            continue
        rows.sort()
        days, qs = zip(*rows)
        days = np.array(days, dtype=float)
        qs = np.array(qs, dtype=float)
        # Smooth
        smoothed = savgol_filter(qs, window_length=min(5, len(qs)), polyorder=2) if len(qs) >= 5 else qs
        q_norm = smoothed / smoothed[0]
        dq = np.gradient(q_norm, days) if len(days) > 1 else np.zeros_like(q_norm)
        d2q = np.gradient(dq, days) if len(days) > 2 else np.zeros_like(dq)
        # Knee = day of max |d2q|, excluding first 2 points
        abs_d2q = np.abs(d2q[2:]) if len(d2q) > 3 else np.abs(d2q)
        knee_off = int(np.argmax(abs_d2q)) + 2 if len(d2q) > 3 else int(np.argmax(abs_d2q))
        knee_day = float(days[knee_off]) if knee_off < len(days) else float("nan")
        fade_pct = 100 * (1 - qs[-1] / qs[0])
        print(f"  {cell}: {len(rows):2d} pts, day [{days[0]:.0f}, {days[-1]:.0f}], fade {fade_pct:.1f}%, knee day = {knee_day:.0f}")
        knee_results.append({"cell": cell, "n_pts": len(rows), "final_day": float(days[-1]),
                             "final_SOH": float(qs[-1] / qs[0]), "knee_day": knee_day,
                             "fade_pct": fade_pct})

    # Disagreement-onset in days: from mahalanobis_option_x1 second-life rows
    z = pd.read_parquet(OUT_DIR / "mahalanobis_option_x1.parquet")
    z_sl = z[z["lifecycle"] == "second_life"].copy()
    THR = float(np.sqrt(7.815))  # chi^2(0.95, 3) for K=1 test; pre-reg uses 0.99 = 3.37, K=2
    THR_99 = float(np.sqrt(11.345))  # chi^2(0.99, 3)

    onset_days = {}
    for cell in CELLS:
        sub = z_sl[z_sl["cell_id"] == cell].sort_values("rpt_idx").reset_index(drop=True)
        if sub.empty:
            continue
        # First RPT where m_dist > threshold for K=2 consecutive
        above = (sub["m_dist"] > THR_99).astype(int).values
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(sub["rpt_idx"].iloc[i])
                break
        if onset_rpt is None:
            continue
        # Map to days
        if onset_rpt in rpt_dates[cell] and 1 in rpt_dates[cell]:
            onset_day = (rpt_dates[cell][onset_rpt] - rpt_dates[cell][1]).days
            onset_days[cell] = onset_day

    print("\n=== Second-life lead time: knee_day - onset_day ===")
    lead = []
    for kr in knee_results:
        c = kr["cell"]
        if c not in onset_days:
            continue
        ot = onset_days[c]
        kn = kr["knee_day"]
        lead.append({"cell": c, "onset_day": ot, "knee_day": kn,
                     "lead_days": kn - ot, "final_SOH": kr["final_SOH"]})
    ldf = pd.DataFrame(lead)
    print(ldf.to_string(index=False, float_format=lambda x: f"{x:.1f}" if isinstance(x, float) else str(x)))

    # Aggregate
    if not ldf.empty:
        n = len(ldf)
        mean = ldf["lead_days"].mean()
        sd = ldf["lead_days"].std(ddof=1) if n > 1 else 0
        se = sd / np.sqrt(n) if n > 1 else 0
        from scipy import stats
        t_one_sided = stats.t.ppf(0.95, df=n-1) if n > 1 else 0
        lcb = mean - t_one_sided * se
        print(f"\n  N = {n}")
        print(f"  Mean lead days = {mean:+.1f}")
        print(f"  SD            = {sd:.1f}")
        print(f"  95% one-sided LCB = {lcb:+.1f}")
        print(f"\n  NOTE: Days unit, not cycles. Don't directly compare to first-life's 50-cycle threshold.")

    ldf.to_parquet(OUT_DIR / "second_life_leadtime_days.parquet")


if __name__ == "__main__":
    main()
