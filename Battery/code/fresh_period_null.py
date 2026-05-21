"""
Phase 2.4 + 2.5 — Fresh-period null fit and disagreement-onset detector,
applied to the cleanest subset (first-life Triad alpha cells: W8/W9/W10/V4).

Per cell:
  1. Take the three operators {Q_max, R_ohmic_soc50, R_diff_soc50} across all RPTs
  2. Standardize each operator using RPTs 1-3 (fresh period) mean+std
  3. Estimate the 3x3 residual covariance from fresh-period data
  4. Compute joint Mahalanobis distance per RPT
  5. Per-cell PPC: are fresh-period distances consistent with chi^2(df=3)?
  6. Detect disagreement-onset as first RPT where dist > threshold for K=2 consecutive RPTs

This is a proof-of-concept; the full hierarchical Bayesian pool (population mu_LT)
comes after the per-cell statistics are validated.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

OUT_DIR = Path("D:/Renewables/Battery/data/processed")


def main():
    df = pd.read_parquet(OUT_DIR / "features_first_life.parquet")
    alpha_cells = ["W8", "W9", "W10", "V4"]
    df = df[df["cell_id"].isin(alpha_cells)].copy()

    # Use SOC=50% as canonical EIS sub-operators
    operators = ["Q_max_Ah", "R_ohmic_soc50", "R_diff_soc50"]
    df = df[["cell_id", "rpt_idx"] + operators].dropna(subset=operators)

    print(f"Working data: {len(df)} (cell, RPT) rows across {df['cell_id'].nunique()} cells\n")
    print("Per-cell RPT coverage with all 3 operators:")
    print(df.groupby("cell_id")["rpt_idx"].agg(["count", "min", "max"]).to_string())

    fresh_rpts = [1, 2, 3]
    results = []
    ppc_results = []
    onset_results = []

    for cell, group in df.groupby("cell_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        fresh = group[group["rpt_idx"].isin(fresh_rpts)]
        if len(fresh) < 3:
            print(f"\n[skip] {cell}: only {len(fresh)} fresh-period observations")
            continue

        # Standardize using fresh-period mean & std
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        # Guard against zero std (happens if operator constant over fresh period)
        sd = np.where(sd < 1e-12, 1e-12, sd)
        z = (group[operators].values - mu) / sd

        # Fresh-period residual covariance (using standardized residuals)
        z_fresh = (fresh[operators].values - mu) / sd
        # cov of fresh-period z-values
        if len(z_fresh) >= 2:
            cov = np.cov(z_fresh.T, ddof=1)
        else:
            cov = np.eye(3)
        # Regularize for invertibility
        cov_reg = cov + 1e-4 * np.eye(3)
        cov_inv = np.linalg.inv(cov_reg)

        # Mahalanobis distance per RPT
        dist = np.sqrt(np.einsum("ij,jk,ik->i", z, cov_inv, z))
        group = group.copy()
        group["m_dist"] = dist

        # PPC: fresh-period dist^2 should be chi^2(df=3)
        fresh_d2 = dist[group["rpt_idx"].isin(fresh_rpts).values] ** 2
        ppc_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue if len(fresh_d2) > 1 else np.nan

        # Onset detection: threshold = chi^2(0.99, df=3) sqrt
        thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
        above = (dist > thr).astype(int)
        # find first RPT where above[r]=1 and above[r+1]=1 (K=2 consecutive)
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(group["rpt_idx"].iloc[i])
                break

        results.append(group[["cell_id", "rpt_idx", "m_dist"]])
        ppc_results.append({
            "cell_id": cell,
            "fresh_n": int(len(fresh_d2)),
            "fresh_mean_d2": float(np.mean(fresh_d2)),
            "fresh_mean_d2_expected": 3.0,
            "ks_p": float(ppc_p) if not np.isnan(ppc_p) else None,
            "threshold_99pct": float(thr),
        })
        onset_results.append({
            "cell_id": cell,
            "onset_rpt": onset_rpt,
            "n_rpts_observed": int(len(group)),
            "max_dist": float(np.max(dist)),
            "final_dist": float(dist[-1]),
        })

    print("\n=== Per-cell Mahalanobis-distance trajectories ===")
    full = pd.concat(results, ignore_index=True)
    pivot = full.pivot(index="rpt_idx", columns="cell_id", values="m_dist")
    print(pivot.to_string(float_format=lambda x: f"{x:.2f}" if pd.notna(x) else "    -"))
    pivot.to_parquet(OUT_DIR / "mahalanobis_trajectories_alpha.parquet")

    print("\n=== Posterior predictive check (fresh-period dist^2 vs chi^2(3)) ===")
    ppc_df = pd.DataFrame(ppc_results)
    print(ppc_df.to_string(index=False))

    print("\n=== Disagreement-onset detection (K=2 consecutive above 99th-pct threshold) ===")
    onset_df = pd.DataFrame(onset_results)
    print(onset_df.to_string(index=False))


if __name__ == "__main__":
    main()
