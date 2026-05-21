"""
Phase 4 held-out classifier runs on the SECL cohort cells that did NOT
inform the exploratory N=4 LLI/LAM+SEI pattern.

Held-out per the Phase 4 pre-registration:
  Truly independent (no first-life alpha involvement):
    - First-life beta cells: G1, W4, W5 (Triad β: Q_max + R_DC + tau)
    - Second-life V5 (first-life was dismissed early, never contributed
      to the exploratory alpha pattern)
  Non-independent (same physical cells as exploratory):
    - Second-life V4, W8, W9, W10, G1 — report but flag as not-independent
      replication, only useful for longitudinal consistency check

Pre-registered protocol:
  Features: median unit-norm residual direction at flagged RPTs
  Centroids: LLI = (-1, 0, 0); LAM+SEI = (-1, +1, +1)/sqrt(3)
  Classification: cosine similarity, argmax, confidence = |s_LLI - s_LAM_SEI|
  Threshold: 0.3
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats


OUT_DIR = Path("D:/Renewables/Battery/data/processed")

U_LLI = np.array([-1.0, 0.0, 0.0])
U_LLI = U_LLI / np.linalg.norm(U_LLI)
U_LAM_SEI = np.array([-1.0, +1.0, +1.0])
U_LAM_SEI = U_LAM_SEI / np.linalg.norm(U_LAM_SEI)
CONF = 0.3
THR = np.sqrt(stats.chi2.ppf(0.99, df=3))


def classify_trajectory(z_mat, m_dist):
    """Given a trajectory's z-vectors and Mahalanobis distances, classify per pre-reg."""
    flagged = m_dist > THR
    n_flagged = int(flagged.sum())
    if n_flagged == 0:
        return dict(n_flagged=0, class_="unflagged", confidence=0.0, s_LLI=np.nan, s_LAM_SEI=np.nan)
    z = z_mat[flagged]
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    u_med = np.median(u, axis=0)
    u_med = u_med / max(np.linalg.norm(u_med), 1e-12)
    s_l = float(np.dot(u_med, U_LLI))
    s_a = float(np.dot(u_med, U_LAM_SEI))
    conf = abs(s_l - s_a)
    if conf < CONF:
        cls = "unclassified"
    else:
        cls = "LLI" if s_l > s_a else "LAM+SEI"
    return dict(n_flagged=n_flagged, class_=cls, confidence=conf, s_LLI=s_l, s_LAM_SEI=s_a)


def run_alpha_gamma_classifier():
    """First-life α (exploratory) + second-life γ (same-cell non-independent + V5 independent)."""
    z_all = pd.read_parquet(OUT_DIR / "mahalanobis_option_x1.parquet")
    z_cols = ["z_Q_max_Ah", "z_R_ohmic_mid", "z_R_diff_mid"]
    classifications = []
    for traj_id, group in z_all.groupby("trajectory_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        z = group[z_cols].values
        m = group["m_dist"].values
        info = classify_trajectory(z, m)
        info["trajectory_id"] = traj_id
        info["lifecycle"] = group["lifecycle"].iloc[0]
        info["cell_id"] = group["cell_id"].iloc[0]
        # Independence flag
        if group["lifecycle"].iloc[0] == "first_life":
            info["independence"] = "EXPLORATORY"
        elif group["cell_id"].iloc[0] in {"V4", "W8", "W9", "W10", "G1"}:
            info["independence"] = "non-indep (same cell)"
        else:
            info["independence"] = "independent"
        classifications.append(info)
    return pd.DataFrame(classifications)


def run_beta_classifier():
    """First-life β (truly independent — these cells never had EIS and never
    contributed to the exploratory pattern)."""
    z_all = pd.read_parquet(OUT_DIR / "mahalanobis_triad_beta.parquet")
    z_cols = ["z_Q_max_Ah", "z_R_DC_pulse", "z_tau_pulse_s"]
    classifications = []
    for cell, group in z_all.groupby("cell_id"):
        group = group.sort_values("rpt_idx").reset_index(drop=True)
        z = group[z_cols].values
        m = group["m_dist"].values
        info = classify_trajectory(z, m)
        info["trajectory_id"] = f"{cell}_first_life_beta"
        info["lifecycle"] = "first_life"
        info["cell_id"] = cell
        info["independence"] = "independent (triad beta)"
        classifications.append(info)
    return pd.DataFrame(classifications)


def main():
    df_ag = run_alpha_gamma_classifier()
    df_b = run_beta_classifier()
    df = pd.concat([df_ag, df_b], ignore_index=True)
    cols = ["cell_id", "lifecycle", "trajectory_id", "independence", "n_flagged",
            "class_", "confidence", "s_LLI", "s_LAM_SEI"]
    df = df[cols]
    df = df.rename(columns={"class_": "class"})
    print("=== All SECL trajectories ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    print("\n=== Stratified pre-reg verdict ===")

    # Truly independent held-out: first-life beta + V5 second-life (if present)
    independent_mask = df["independence"].str.startswith("independent")
    indep = df[independent_mask]
    print(f"\n--- Independent held-out (N={len(indep)}) ---")
    if len(indep) > 0:
        n_conf = (indep["confidence"] >= CONF).sum()
        n_lam = (indep["class"] == "LAM+SEI").sum()
        n_lli = (indep["class"] == "LLI").sum()
        print(f"  Confidently classified: {n_conf}/{len(indep)} ({n_conf/len(indep)*100:.1f}%)  pre-reg req >=50%")
        if n_conf > 0:
            print(f"  LAM+SEI: {n_lam}/{n_conf} ({n_lam/n_conf*100:.1f}%)")
            print(f"  LLI:     {n_lli}/{n_conf} ({n_lli/n_conf*100:.1f}%)")

    # Non-independent (same cells as exploratory)
    nonindep = df[df["independence"].str.startswith("non-indep")]
    print(f"\n--- Non-independent same-cell replication (N={len(nonindep)}) ---")
    if len(nonindep) > 0:
        n_conf = (nonindep["confidence"] >= CONF).sum()
        n_lam = (nonindep["class"] == "LAM+SEI").sum()
        n_lli = (nonindep["class"] == "LLI").sum()
        print(f"  Confidently classified: {n_conf}/{len(nonindep)} ({n_conf/len(nonindep)*100:.1f}%)")
        if n_conf > 0:
            print(f"  LAM+SEI: {n_lam}/{n_conf} ({n_lam/n_conf*100:.1f}%)")
            print(f"  LLI:     {n_lli}/{n_conf} ({n_lli/n_conf*100:.1f}%)")

    # Exploratory (first-life alpha)
    explor = df[df["independence"] == "EXPLORATORY"]
    print(f"\n--- Exploratory first-life alpha (informed the pre-reg, NOT confirmatory) ---")
    print(explor[["cell_id", "class", "confidence", "s_LLI", "s_LAM_SEI"]].to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    df.to_parquet(OUT_DIR / "secl_held_out_classification.parquet")


if __name__ == "__main__":
    main()
