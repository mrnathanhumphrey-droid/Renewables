"""
Phase 2.4 (extended) — Combine first-life + second-life features and run
the pooled fresh-period Mahalanobis pipeline across all triad-alpha/gamma
trajectories.

10 trajectories total:
  first-life alpha: V4, W8, W9, W10           (fresh RPTs 1-3)
  second-life gamma: G1, V4, V5, W10, W8, W9  (fresh RPTs 5-7)

Operators: {Q_max, R_ohmic_mid, R_diff_mid}
  first-life mid = SOC50%
  second-life mid = 363 mV (~ mid-SOC for NMC chemistry)

Outputs:
  data/processed/features_combined.parquet
  data/processed/mahalanobis_combined.parquet
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

OUT_DIR = Path("D:/Renewables/Battery/data/processed")


def load_and_unify():
    fl = pd.read_parquet(OUT_DIR / "features_first_life.parquet")
    sl = pd.read_parquet(OUT_DIR / "features_second_life.parquet")

    # First-life alpha: rename SOC50 features to "mid"
    fl_alpha = fl[fl["triad"] == "alpha"].rename(
        columns={"R_ohmic_soc50": "R_ohmic_mid", "R_diff_soc50": "R_diff_mid"}
    )
    fl_alpha["triad_unified"] = "alpha_gamma"

    # Second-life gamma: rename v363 to "mid"
    sl_gamma = sl.rename(
        columns={"R_ohmic_v363": "R_ohmic_mid", "R_diff_v363": "R_diff_mid"}
    )
    sl_gamma["triad_unified"] = "alpha_gamma"

    cols = ["cell_id", "lifecycle", "triad_unified", "rpt_idx", "Q_max_Ah", "R_ohmic_mid", "R_diff_mid"]
    combined = pd.concat([fl_alpha[cols], sl_gamma[cols]], ignore_index=True)
    return combined


def run_pipeline(df, operators=("Q_max_Ah", "R_ohmic_mid", "R_diff_mid")):
    operators = list(operators)
    df = df[["cell_id", "lifecycle", "rpt_idx"] + operators].dropna(subset=operators).copy()
    df["trajectory_id"] = df["cell_id"] + "_" + df["lifecycle"]

    print(f"Working data: {len(df)} (trajectory, RPT) rows across {df['trajectory_id'].nunique()} trajectories\n")

    print("Per-trajectory coverage with all 3 operators:")
    cov = df.groupby("trajectory_id")["rpt_idx"].agg(["count", "min", "max"])
    print(cov.to_string())

    # Per-trajectory fresh window: first-life = RPTs 1-3, second-life = RPTs 5-7
    def fresh_rpts_for(lifecycle):
        return [1, 2, 3] if lifecycle == "first_life" else [5, 6, 7]

    z_rows = []
    cell_stats = {}
    for traj_id, group in df.groupby("trajectory_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        lifecycle = group["lifecycle"].iloc[0]
        fresh = group[group["rpt_idx"].isin(fresh_rpts_for(lifecycle))]
        if len(fresh) < 2:
            print(f"[skip] {traj_id}: only {len(fresh)} fresh-period observations")
            continue
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        sd = np.where(sd < 1e-12, 1e-12, sd)
        cell_stats[traj_id] = (mu, sd)
        z = (group[operators].values - mu) / sd
        z_df = group[["trajectory_id", "cell_id", "lifecycle", "rpt_idx"]].reset_index(drop=True)
        for k, op in enumerate(operators):
            z_df[f"z_{op}"] = z[:, k]
        z_rows.append(z_df)

    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]

    # Build pooled fresh-period observation set
    def is_fresh(row):
        return row["rpt_idx"] in fresh_rpts_for(row["lifecycle"])

    fresh_mask = z_all.apply(is_fresh, axis=1)
    pooled_fresh = z_all[fresh_mask][z_cols].values
    print(f"\nPooled fresh-period observations: {len(pooled_fresh)} across {z_all[fresh_mask]['trajectory_id'].nunique()} trajectories")

    pooled_cov = np.cov(pooled_fresh.T, ddof=1)
    diag = np.sqrt(np.diag(pooled_cov))
    pooled_corr = pooled_cov / np.outer(diag, diag)
    print("\nPooled fresh-period correlation (3x3):")
    print(pd.DataFrame(pooled_corr, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    cov_inv = np.linalg.inv(pooled_cov + 1e-4 * np.eye(3))
    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    print("\n=== PPC: pooled fresh-period dist^2 vs chi^2(3) ===")
    fresh_d2 = d2[fresh_mask.values]
    ks_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue
    print(f"  fresh n={len(fresh_d2)}, mean d^2={np.mean(fresh_d2):.3f} (expected 3.0), KS p={ks_p:.4f}")

    # Mahalanobis trajectories per trajectory_id
    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold (99th pct chi^2(3)): {thr:.2f}")

    print("\n=== Per-trajectory Mahalanobis distance ===")
    pivot = z_all.pivot(index="rpt_idx", columns="trajectory_id", values="m_dist")
    # Order columns for readability
    fl_cols = sorted([c for c in pivot.columns if "first_life" in c])
    sl_cols = sorted([c for c in pivot.columns if "second_life" in c])
    pivot = pivot[fl_cols + sl_cols]
    print(pivot.to_string(float_format=lambda x: f"{x:6.2f}" if pd.notna(x) else "    -"))

    # Onset detection
    onsets = []
    for traj_id, group in z_all.groupby("trajectory_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        above = (group["m_dist"] > thr).astype(int).values
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(group["rpt_idx"].iloc[i])
                break
        q_at_onset = float("nan")
        if onset_rpt is not None:
            row = group[group["rpt_idx"] == onset_rpt]
            if not row.empty:
                q_at_onset = float(row["z_Q_max_Ah"].iloc[0])
        onsets.append({
            "trajectory_id": traj_id,
            "lifecycle": group["lifecycle"].iloc[0],
            "onset_rpt": onset_rpt,
            "n_rpts": len(group),
            "max_dist": float(group["m_dist"].max()),
            "z_Q_max_at_onset": q_at_onset,
        })

    print("\n=== Disagreement-onset (K=2 consecutive above threshold) ===")
    onset_df = pd.DataFrame(onsets)
    print(onset_df.to_string(index=False))

    # Outputs
    z_all.to_parquet(OUT_DIR / "mahalanobis_combined.parquet")
    print(f"\nWritten: {OUT_DIR / 'mahalanobis_combined.parquet'}")


def main():
    combined = load_and_unify()
    combined.to_parquet(OUT_DIR / "features_combined.parquet")
    print(f"Written: {OUT_DIR / 'features_combined.parquet'} ({len(combined)} rows)\n")
    run_pipeline(combined)


if __name__ == "__main__":
    main()
