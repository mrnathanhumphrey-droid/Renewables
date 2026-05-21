"""
Phase 3 preview (extended) — combined alpha + beta cohort lead times.

N=7 first-life trajectories:
  alpha: V4, W8, W9, W10  (Q_max + EIS-ohmic + EIS-diff)
  beta:  G1, W4, W5       (Q_max + HPPC R_DC + HPPC tau)

Pre-registered headline statistic: 95% lower bound on population mean lead time
over knee-point. Falsification threshold: 50 cycles.
"""

import numpy as np
import pandas as pd
from scipy import stats


# From literature/11 + triad_beta_pipeline.py output
RESULTS = [
    {"cell": "V4",  "triad": "alpha", "onset_cyc": 70,  "knee_cyc": 95,  "final_SOH": 0.95},
    {"cell": "W8",  "triad": "alpha", "onset_cyc": 148, "knee_cyc": 148, "final_SOH": 0.91},
    {"cell": "W9",  "triad": "alpha", "onset_cyc": 122, "knee_cyc": 146, "final_SOH": 0.92},
    {"cell": "W10", "triad": "alpha", "onset_cyc": 122, "knee_cyc": 151, "final_SOH": 0.92},
    {"cell": "G1",  "triad": "beta",  "onset_cyc": 37,  "knee_cyc": 37,  "final_SOH": 0.94},
    {"cell": "W4",  "triad": "beta",  "onset_cyc": 123, "knee_cyc": 176, "final_SOH": 0.94},
    {"cell": "W5",  "triad": "beta",  "onset_cyc": 125, "knee_cyc": 167, "final_SOH": 0.92},
]


def main():
    df = pd.DataFrame(RESULTS)
    df["lead_cyc"] = df["knee_cyc"] - df["onset_cyc"]

    print("=== Per-cell lead-time table (N=7 first-life) ===")
    print(df.to_string(index=False))

    print("\n=== Aggregate statistics ===")
    n = len(df)
    mean = df["lead_cyc"].mean()
    sd = df["lead_cyc"].std(ddof=1)
    se = sd / np.sqrt(n)
    # 95% t-CI for the mean
    t_crit = stats.t.ppf(0.975, df=n - 1)
    ci_low = mean - t_crit * se
    ci_high = mean + t_crit * se
    # One-sided 95% lower bound
    t_one_sided = stats.t.ppf(0.95, df=n - 1)
    lower_one_sided = mean - t_one_sided * se

    print(f"  N = {n}")
    print(f"  Mean lead time          = {mean:+.2f} cyc")
    print(f"  SD                      = {sd:.2f}")
    print(f"  SE                      = {se:.2f}")
    print(f"  Two-sided 95% CI        = [{ci_low:+.2f}, {ci_high:+.2f}]")
    print(f"  One-sided 95% lower bd  = {lower_one_sided:+.2f} cyc")
    print(f"  Pre-reg falsification:  one-sided 95% LCB > 50 cyc")
    if lower_one_sided > 50:
        print("  VERDICT: PASS (lead time confirmed at pre-reg magnitude)")
    elif lower_one_sided > 0:
        print("  VERDICT: PARTIAL (positive direction, magnitude below 50-cyc threshold)")
    else:
        print("  VERDICT: NULL (direction not confirmed)")

    print("\n=== By triad ===")
    for triad, group in df.groupby("triad"):
        n_t = len(group)
        m_t = group["lead_cyc"].mean()
        sd_t = group["lead_cyc"].std(ddof=1) if n_t > 1 else float("nan")
        print(f"  triad {triad}: N={n_t}, mean={m_t:+.2f}, sd={sd_t:.2f}, lead times = {list(group['lead_cyc'])}")

    print("\n=== Cells crossing 50-cyc individual threshold ===")
    crossers = df[df["lead_cyc"] >= 50]
    print(crossers.to_string(index=False) if len(crossers) else "  None")

    print("\n=== Sign breakdown ===")
    pos = (df["lead_cyc"] > 0).sum()
    zero = (df["lead_cyc"] == 0).sum()
    neg = (df["lead_cyc"] < 0).sum()
    print(f"  Positive lead: {pos}/{n}")
    print(f"  Zero lead:     {zero}/{n}")
    print(f"  Negative lead: {neg}/{n}")
    print(f"  Sign test (one-sided H1: lead > 0): binom p = {stats.binomtest(pos, pos+neg, 0.5, alternative='greater').pvalue:.4f}")


if __name__ == "__main__":
    main()
