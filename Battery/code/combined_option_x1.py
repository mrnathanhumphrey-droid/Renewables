"""
Phase 2.4 (Option X1) — Cross-lifecycle pipeline with per-cell fresh reference
anchored at first-life RPTs 1-3 of the same physical cell.

Rationale: V4/W8/W9/W10/G1 are the SAME physical cells in first- and
second-life. Their truly-fresh baseline is the first life's RPTs 1-3, not
the second life's RPTs 5-7 (which are already at ~90% SOH).

Cells fresh ref:
  V4   <- V4 first-life RPTs 1-3
  W8   <- W8 first-life RPTs 1-3
  W9   <- W9 first-life RPTs 1-3
  W10  <- W10 first-life RPTs 1-3
  G1   <- G1 first-life RPTs 1-3 (but G1 first-life has NO EIS, only HPPC)
  V5   <- V5 first-life RPTs 1-3 (only 2 valid RPTs; marginal)

For G1 second-life EIS: no first-life EIS exists. G1 must be excluded from
the unified alpha-gamma triad analysis OR use a different reference. Options:
  (a) Exclude G1 second-life from the X1 alpha-gamma pool
  (b) Use Khan 2025 fresh-period as a population-level "fresh manifold" for G1
  (c) Use the AVERAGE of W8/W9/W10/V4 first-life fresh as G1's reference

For this push, take Option (a): exclude G1 second-life from the EIS-bearing
pool. G1's first-life trajectory still contributes to Triad beta later.

Same applies to V5 second-life — V5 first-life has only 2 EIS RPTs, which
is insufficient for fresh-period covariance contribution. Exclude.

This leaves the X1 pool:
  V4 first-life + V4 second-life
  W8 first-life + W8 second-life
  W9 first-life + W9 second-life
  W10 first-life + W10 second-life
= 4 cells, 8 trajectories (each cell contributes 2)
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

OUT_DIR = Path("D:/Renewables/Battery/data/processed")


def load_and_unify():
    fl = pd.read_parquet(OUT_DIR / "features_first_life.parquet")
    sl = pd.read_parquet(OUT_DIR / "features_second_life.parquet")

    fl_alpha = fl[fl["triad"] == "alpha"].rename(
        columns={"R_ohmic_soc50": "R_ohmic_mid", "R_diff_soc50": "R_diff_mid"}
    )
    sl_gamma = sl.rename(
        columns={"R_ohmic_v363": "R_ohmic_mid", "R_diff_v363": "R_diff_mid"}
    )
    cols = ["cell_id", "lifecycle", "rpt_idx", "Q_max_Ah", "R_ohmic_mid", "R_diff_mid"]
    return pd.concat([fl_alpha[cols], sl_gamma[cols]], ignore_index=True)


def run_option_x1(df, operators=("Q_max_Ah", "R_ohmic_mid", "R_diff_mid")):
    operators = list(operators)
    df = df[["cell_id", "lifecycle", "rpt_idx"] + operators].dropna(subset=operators).copy()
    df["trajectory_id"] = df["cell_id"] + "_" + df["lifecycle"]

    # X1 cohort restriction: only cells with a valid first-life fresh-period reference
    valid_cells = {"V4", "W8", "W9", "W10"}  # these have full first-life EIS at RPTs 1-3
    print(f"X1 cohort: {sorted(valid_cells)} (cells with both first-life fresh ref AND second-life EIS)\n")

    df = df[df["cell_id"].isin(valid_cells)]
    print(f"Working data: {len(df)} (cell, RPT) rows across {df['trajectory_id'].nunique()} trajectories")
    cov = df.groupby("trajectory_id")["rpt_idx"].agg(["count", "min", "max"])
    print(cov.to_string())

    # Per-cell fresh = first-life RPTs 1-3 of the same cell
    z_rows = []
    fresh_pool = []
    cell_stats = {}
    for cell in valid_cells:
        first_life_data = df[(df["cell_id"] == cell) & (df["lifecycle"] == "first_life")]
        fresh = first_life_data[first_life_data["rpt_idx"].isin([1, 2, 3])]
        # If RPT 1 missing for this cell, use 2-3
        if len(fresh) < 2:
            print(f"[skip] {cell}: only {len(fresh)} fresh-period observations")
            continue
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        sd = np.where(sd < 1e-12, 1e-12, sd)
        cell_stats[cell] = (mu, sd)
        # Standardize BOTH lifecycles using first-life fresh stats
        for lifecycle in ["first_life", "second_life"]:
            sub = df[(df["cell_id"] == cell) & (df["lifecycle"] == lifecycle)]
            if sub.empty:
                continue
            sub = sub.sort_values("rpt_idx").reset_index(drop=True)
            z = (sub[operators].values - mu) / sd
            z_df = sub[["trajectory_id", "cell_id", "lifecycle", "rpt_idx"]].reset_index(drop=True)
            for k, op in enumerate(operators):
                z_df[f"z_{op}"] = z[:, k]
            z_rows.append(z_df)
            # Fresh pool = first-life RPTs 1-3 only (not second-life)
            if lifecycle == "first_life":
                fresh_mask = sub["rpt_idx"].isin([1, 2, 3])
                fresh_pool.append(z[fresh_mask.values])

    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]
    fresh_stack = np.vstack(fresh_pool)
    print(f"\nPooled fresh-period observations: {len(fresh_stack)} (first-life RPTs 1-3 across {len(cell_stats)} cells)")

    pooled_cov = np.cov(fresh_stack.T, ddof=1)
    diag = np.sqrt(np.diag(pooled_cov))
    pooled_corr = pooled_cov / np.outer(diag, diag)
    print("\nPooled fresh-period correlation (3x3) — should match first-life-only result:")
    print(pd.DataFrame(pooled_corr, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    cov_inv = np.linalg.inv(pooled_cov + 1e-4 * np.eye(3))
    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    print("\n=== PPC: fresh-period dist^2 vs chi^2(3) ===")
    fresh_first_mask = ((z_all["lifecycle"] == "first_life") & z_all["rpt_idx"].isin([1, 2, 3]))
    fresh_d2 = d2[fresh_first_mask.values]
    ks_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue
    print(f"  fresh n={len(fresh_d2)}, mean d^2={np.mean(fresh_d2):.3f} (expected 3.0), KS p={ks_p:.4f}")

    # Trajectories
    print("\n=== Per-trajectory Mahalanobis distance ===")
    pivot = z_all.pivot(index="rpt_idx", columns="trajectory_id", values="m_dist")
    fl_cols = sorted([c for c in pivot.columns if "first_life" in c])
    sl_cols = sorted([c for c in pivot.columns if "second_life" in c])
    pivot = pivot[fl_cols + sl_cols]
    print(pivot.to_string(float_format=lambda x: f"{x:6.2f}" if pd.notna(x) else "    -"))

    # Onset detection
    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold (99th pct chi^2(3)): {thr:.2f}")
    onsets = []
    for traj_id, group in z_all.groupby("trajectory_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        above = (group["m_dist"] > thr).astype(int).values
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(group["rpt_idx"].iloc[i])
                break
        onsets.append({
            "trajectory_id": traj_id,
            "lifecycle": group["lifecycle"].iloc[0],
            "onset_rpt": onset_rpt,
            "n_rpts": len(group),
            "max_dist": float(group["m_dist"].max()),
            "final_dist": float(group["m_dist"].iloc[-1]),
        })
    print("\n=== Disagreement-onset (K=2 consecutive above threshold) ===")
    onset_df = pd.DataFrame(onsets)
    print(onset_df.to_string(index=False))

    z_all.to_parquet(OUT_DIR / "mahalanobis_option_x1.parquet")
    print(f"\nWritten: {OUT_DIR / 'mahalanobis_option_x1.parquet'}")


def main():
    df = load_and_unify()
    run_option_x1(df)


if __name__ == "__main__":
    main()
