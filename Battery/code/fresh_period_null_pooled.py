"""
Phase 2.4/2.5 v2 — Pooled fresh-period null.

Fix for the v1 degeneracy: estimate fresh-period covariance by POOLING RPTs 1-3
across all alpha cells (12 observations of a 3-vector instead of 3 per cell).
Standardization remains per-cell to absorb absolute-magnitude differences.

Also reports per-operator z-score trajectories for diagnostic transparency.
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
    operators = ["Q_max_Ah", "R_ohmic_soc50", "R_diff_soc50"]
    df = df[["cell_id", "rpt_idx"] + operators].dropna(subset=operators)

    fresh_rpts = [1, 2, 3]

    # --- Per-cell standardization on fresh period ---
    cell_stats = {}
    z_rows = []
    for cell, group in df.groupby("cell_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        fresh = group[group["rpt_idx"].isin(fresh_rpts)]
        if len(fresh) < 2:
            print(f"[skip] {cell}: insufficient fresh-period data ({len(fresh)} obs)")
            continue
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        sd = np.where(sd < 1e-12, 1e-12, sd)
        cell_stats[cell] = (mu, sd)
        z = (group[operators].values - mu) / sd
        z_df = group[["cell_id", "rpt_idx"]].copy().reset_index(drop=True)
        for k, op in enumerate(operators):
            z_df[f"z_{op}"] = z[:, k]
        z_rows.append(z_df)

    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]

    # --- POOLED fresh-period covariance ---
    pooled_fresh = z_all[z_all["rpt_idx"].isin(fresh_rpts)][z_cols].values
    print(f"Pooled fresh-period observations: {len(pooled_fresh)} (RPTs 1-3 across {len(cell_stats)} cells)")

    pooled_cov = np.cov(pooled_fresh.T, ddof=1)
    print("\nPooled fresh-period covariance (3x3):")
    print(pd.DataFrame(pooled_cov, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    # Correlation form for readability
    diag = np.sqrt(np.diag(pooled_cov))
    pooled_corr = pooled_cov / np.outer(diag, diag)
    print("\nPooled fresh-period correlation (3x3):")
    print(pd.DataFrame(pooled_corr, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    cov_inv = np.linalg.inv(pooled_cov + 1e-4 * np.eye(3))

    # --- Mahalanobis per (cell, RPT) using pooled cov ---
    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    pivot = z_all.pivot(index="rpt_idx", columns="cell_id", values="m_dist")
    print("\n=== Mahalanobis distance per (cell, RPT) — pooled covariance ===")
    print(pivot.to_string(float_format=lambda x: f"{x:.2f}" if pd.notna(x) else "    -"))
    pivot.to_parquet(OUT_DIR / "mahalanobis_trajectories_alpha_pooled.parquet")

    # --- Per-operator z-score trajectories ---
    print("\n=== Per-operator z-score trajectories ===")
    for op in operators:
        z_pivot = z_all.pivot(index="rpt_idx", columns="cell_id", values=f"z_{op}")
        print(f"\n  -- {op} --")
        print(z_pivot.to_string(float_format=lambda x: f"{x:+.2f}" if pd.notna(x) else "    -"))

    # --- PPC against chi^2(3) ---
    print("\n=== PPC: fresh-period dist^2 vs chi^2(3) ===")
    fresh_d2 = d2[z_all["rpt_idx"].isin(fresh_rpts).values]
    ks_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue
    print(f"  fresh n  = {len(fresh_d2)}")
    print(f"  mean d^2 = {np.mean(fresh_d2):.3f} (expected 3.0)")
    print(f"  KS p-val = {ks_p:.4f}  (>0.05 = PPC pass)")

    # --- Onset detection ---
    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold (99th pct of chi^2(3)): {thr:.2f}")
    onsets = []
    for cell, group in z_all.groupby("cell_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        above = (group["m_dist"] > thr).astype(int).values
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(group["rpt_idx"].iloc[i])
                break
        onsets.append({
            "cell_id": cell,
            "onset_rpt": onset_rpt,
            "n_rpts": len(group),
            "max_dist": float(group["m_dist"].max()),
            "final_dist": float(group["m_dist"].iloc[-1]),
        })
    print("\n=== Disagreement-onset (K=2 consecutive above threshold) ===")
    print(pd.DataFrame(onsets).to_string(index=False))


if __name__ == "__main__":
    main()
