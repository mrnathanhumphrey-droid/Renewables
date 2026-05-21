"""
Phase 2.4 + Phase 3 preview for Triad beta (HPPC instead of EIS).

Cells: G1, W4, W5 — first-life only (no second-life HPPC consolidated yet).
Operators: Q_max_Ah, R_DC_pulse, tau_pulse_s

Same pipeline structure as combined_option_x1.py but on the beta operator triad.

Phase 4 pre-reg hard gate: this script extracts per-cell disagreement-onset and
runs the lead-time vs knee-point comparison. It does NOT touch the
mode-classification protocol — that requires the pre-registered classifier
pipeline which still hasn't been written.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter


OUT_DIR = Path("D:/Renewables/Battery/data/processed")

# Cumulative cycle count per RPT for triad-beta cells.
# Computed from Pozzato 2022 README Cycling_test sheet:
#   W4 cycles per segment: 25,50,48,9,27,17,3,-,-,-,-,-,-,-
#   W5 cycles per segment: 25,50,50,34,8,20,7,25,25,25,25,25,25,25
#   G1 cycles per segment: 25,5,7,25,25,25,25,25,25,25,-,-,-,-
# Diag_N occurs AFTER Cycling_(N-1), so Diag_1=0, Diag_2=Cycling_1, Diag_3=Cyc_1+Cyc_2, etc.
def cum_cycles(per_segment):
    """Given [c1, c2, ...] return [0, c1, c1+c2, ...]."""
    out = [0]
    for c in per_segment:
        out.append(out[-1] + c)
    return out


BETA_CYCLES = {
    "G1": dict(zip(range(1, 12), cum_cycles([25, 5, 7, 25, 25, 25, 25, 25, 25, 25]))),
    "W4": dict(zip(range(1, 9), cum_cycles([25, 50, 48, 9, 27, 17, 3]))),
    "W5": dict(zip(range(1, 16), cum_cycles([25, 50, 50, 34, 8, 20, 7, 25, 25, 25, 25, 25, 25, 25]))),
}


def run_beta_pipeline():
    df = pd.read_parquet(OUT_DIR / "features_first_life.parquet")
    beta_cells = ["G1", "W4", "W5"]
    operators = ["Q_max_Ah", "R_DC_pulse", "tau_pulse_s"]

    df = df[df["cell_id"].isin(beta_cells)].copy()
    df = df[["cell_id", "rpt_idx"] + operators].dropna(subset=operators)
    print(f"Triad-beta cohort: {beta_cells}")
    print(f"Working data: {len(df)} (cell, RPT) rows\n")
    cov = df.groupby("cell_id")["rpt_idx"].agg(["count", "min", "max"])
    print(cov.to_string())

    # Per-cell standardization on RPTs 1-3
    fresh_rpts = [1, 2, 3]
    cell_stats = {}
    z_rows = []
    fresh_pool = []
    for cell in beta_cells:
        sub = df[df["cell_id"] == cell].sort_values("rpt_idx").reset_index(drop=True)
        fresh = sub[sub["rpt_idx"].isin(fresh_rpts)]
        if len(fresh) < 2:
            print(f"[skip] {cell}: only {len(fresh)} fresh-period observations")
            continue
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        sd = np.where(sd < 1e-12, 1e-12, sd)
        cell_stats[cell] = (mu, sd)
        z = (sub[operators].values - mu) / sd
        z_df = sub[["cell_id", "rpt_idx"]].reset_index(drop=True)
        for k, op in enumerate(operators):
            z_df[f"z_{op}"] = z[:, k]
        z_rows.append(z_df)
        fresh_mask = sub["rpt_idx"].isin(fresh_rpts)
        fresh_pool.append(z[fresh_mask.values])

    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]
    fresh_stack = np.vstack(fresh_pool)
    print(f"\nPooled fresh-period observations: {len(fresh_stack)} across {len(cell_stats)} cells")

    pooled_cov = np.cov(fresh_stack.T, ddof=1)
    diag = np.sqrt(np.diag(pooled_cov))
    pooled_corr = pooled_cov / np.outer(diag, diag)
    print("\nPooled fresh-period correlation (3x3):")
    print(pd.DataFrame(pooled_corr, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    cov_inv = np.linalg.inv(pooled_cov + 1e-4 * np.eye(3))
    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    print("\n=== PPC: fresh-period dist^2 vs chi^2(3) ===")
    fresh_mask = z_all["rpt_idx"].isin(fresh_rpts)
    fresh_d2 = d2[fresh_mask.values]
    if len(fresh_d2) >= 2:
        ks_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue
        print(f"  fresh n={len(fresh_d2)}, mean d^2={np.mean(fresh_d2):.3f} (expected 3.0), KS p={ks_p:.4f}")

    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold (99th pct chi^2(3)): {thr:.2f}")

    print("\n=== Per-cell Mahalanobis distance ===")
    pivot = z_all.pivot(index="rpt_idx", columns="cell_id", values="m_dist")
    print(pivot.to_string(float_format=lambda x: f"{x:6.2f}" if pd.notna(x) else "    -"))

    # Onset detection
    onsets = []
    for cell, group in z_all.groupby("cell_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        above = (group["m_dist"] > thr).astype(int).values
        onset_rpt = None
        for i in range(len(above) - 1):
            if above[i] == 1 and above[i + 1] == 1:
                onset_rpt = int(group["rpt_idx"].iloc[i])
                break
        cyc = BETA_CYCLES.get(cell, {}).get(onset_rpt) if onset_rpt else None
        onsets.append({
            "cell_id": cell,
            "onset_rpt": onset_rpt,
            "onset_cycle": cyc,
            "max_dist": float(group["m_dist"].max()),
        })
    print("\n=== Disagreement-onset (K=2 consecutive) ===")
    onset_df = pd.DataFrame(onsets)
    print(onset_df.to_string(index=False))

    # Knee-point on capacity for these cells
    print("\n=== Capacity knee-point detection on triad-beta cells ===")
    knee_results = []
    for cell in beta_cells:
        sub = df[df["cell_id"] == cell].sort_values("rpt_idx").reset_index(drop=True)
        cycle_map = BETA_CYCLES.get(cell, {})
        if not cycle_map:
            continue
        rows = []
        for _, r in sub.iterrows():
            rpt = int(r["rpt_idx"])
            if rpt in cycle_map:
                rows.append((cycle_map[rpt], r["Q_max_Ah"]))
        if len(rows) < 4:
            continue
        rows.sort()
        cycles, qs = zip(*rows)
        cycles = np.asarray(cycles, dtype=float)
        qs = np.asarray(qs, dtype=float)
        # Smoothing if enough points
        if len(qs) >= 5:
            smoothed = savgol_filter(qs, window_length=5, polyorder=2)
        else:
            smoothed = qs
        q_norm = smoothed / smoothed[0]
        dq = np.gradient(q_norm, cycles)
        d2q = np.gradient(dq, cycles)
        abs_d2q = np.abs(d2q[2:])
        knee_idx = int(np.argmax(abs_d2q)) + 2
        knee_cycle = float(cycles[knee_idx])
        knee_results.append({
            "cell_id": cell,
            "n_pts": len(rows),
            "final_cycle": float(cycles[-1]),
            "final_SOH": float(qs[-1] / qs[0]),
            "knee_cycle": knee_cycle,
        })
    kdf = pd.DataFrame(knee_results)
    print(kdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    # Lead time
    print("\n=== Lead time over knee-point (triad beta) ===")
    onset_map = {r["cell_id"]: r["onset_cycle"] for r in onsets if r["onset_cycle"] is not None}
    lead = []
    for kr in knee_results:
        c = kr["cell_id"]
        if c not in onset_map:
            continue
        lead.append({
            "cell_id": c,
            "disagreement_onset_cycle": onset_map[c],
            "knee_cycle": kr["knee_cycle"],
            "lead_over_knee": kr["knee_cycle"] - onset_map[c],
            "final_SOH": kr["final_SOH"],
        })
    ldf = pd.DataFrame(lead)
    print(ldf.to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x, float) else str(x)))

    z_all.to_parquet(OUT_DIR / "mahalanobis_triad_beta.parquet")


if __name__ == "__main__":
    run_beta_pipeline()
