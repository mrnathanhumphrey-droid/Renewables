"""
C3 Probe 5 — PyBaMM uniform-aging-extent (magnitude-confound test) PERMANOVA.

Pre-reg: literature/23_c3_pybamm_uniform_aging_pre_registration.md (commit 93e4f03).

Reads data/processed/pybamm_l9_trajectories.parquet (produced by the modified
modal_pybamm_c3.py with MAX_CYCLES=800 and per-cycle trajectories saved).

Per pre-reg sec.3, picks per-cell aged anchor at the cycle nearest to 0.85
per-cell SOH (instead of Probe 4's "first cycle <= 0.80 per-cell SOH"). This
eliminates magnitude spread across cells -- all cells anchored at the same
per-cell SOH level.

Verdicts (pre-reg sec.5):
  PARAMETER PASS      : p<0.0167 AND F>3.0
  PARAMETER WEAK PASS : p in [0.0167, 0.05] AND F>2.0
  PARAMETER NULL      : p>=0.05 OR F<2.0

  H6 SUPPORTS PROBE 4 ROBUSTNESS  : >=1 of (cathode_thickness, transference) PASS or WEAK PASS
  H6 EXPLAINS SEVERSON BATCH 2    : BOTH cathode_thickness AND transference collapse to NULL
  H6 AMBIGUOUS                    : mixed
  H6 INVALID                      : >30% anchor_partial OR <70% sim success
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG = np.random.default_rng(seed=42)
N_PERMS = 10000

ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05
TARGET_SOH = 0.92  # per pre-reg sec.3 + amendment sec.10 (2026-05-21)


def permanova_pseudoF(u_mat, labels):
    n = len(u_mat)
    norms = np.linalg.norm(u_mat, axis=1, keepdims=True)
    um = u_mat / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = um @ um.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    d_mat = 1.0 - cos_mat
    labels = np.asarray(labels)
    unique = np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for u in unique:
        mask = (labels == u)
        n_u = int(mask.sum())
        if n_u < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_u)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan")
    return (between_ss / (a - 1)) / (within_ss / (n - a))


def permanova_test(u_mat, labels, n_perms=N_PERMS):
    F_obs = permanova_pseudoF(u_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = RNG.permutation(labels)
        F_p = permanova_pseudoF(u_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def parameter_verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > EFFECT_F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > EFFECT_F_WEAK:
        return "WEAK PASS"
    return "NULL"


def joint_verdict(verdicts):
    """Per pre-reg sec.5: focuses on cathode_thickness and transference_number
    (the two that were PASS in Probe 4)."""
    primary_verdicts = [verdicts["thickness_level"], verdicts["transference_level"]]
    n_pass_or_weak = sum(1 for v in primary_verdicts if v in ("PASS", "WEAK PASS"))
    n_null = sum(1 for v in primary_verdicts if v == "NULL")
    if n_pass_or_weak >= 1:
        return "H6 SUPPORTS PROBE 4 ROBUSTNESS"
    if n_null == 2:
        return "H6 EXPLAINS SEVERSON BATCH 2"
    return "H6 AMBIGUOUS"


def select_uniform_anchor(rpts, fresh_Q, target_soh):
    """Pick the cycle nearest to target_soh of per-cell fresh_Q.

    Returns (aged_dict, partial_flag) where aged_dict has {Q_max, R_DC, R_total,
    cycle, SOH}, or (None, True) if no valid cycle found.
    """
    if not rpts:
        return None, True
    target_Q = target_soh * fresh_Q
    # Only consider post-fresh-window cycles (cycle > 25)
    post = [r for r in rpts if r["cycle"] > 25]
    if not post:
        return None, True
    # Find cycle whose Q_max is closest to target_Q
    best = min(post, key=lambda r: abs(r["Q_max"] - target_Q))
    soh = best["Q_max"] / fresh_Q
    # Mark partial if the cell never went below target_soh (i.e., closest cycle still > target)
    partial = soh > target_soh + 0.02  # 2% tolerance band
    return {
        "Q_max": best["Q_max"],
        "R_DC": best["R_DC"],
        "R_total": best["R_total"],
        "cycle": best["cycle"],
        "SOH": soh,
    }, partial


def main():
    print(f"=== C3 Probe 5 -- PyBaMM uniform-anchor PERMANOVA (pre-reg literature/23) ===\n")
    df = pd.read_parquet(IN_PARQUET)
    n_total = len(df)
    n_valid_sim = df["error"].isna().sum() if "error" in df.columns else n_total
    print(f"Cells in parquet: {n_total}")
    print(f"Valid sim (no error): {n_valid_sim}")

    sim_success_frac = n_valid_sim / n_total if n_total > 0 else 0
    if sim_success_frac < 0.70:
        print(f"\nH6 INVALID: sim success only {sim_success_frac*100:.1f}% < 70% pre-reg floor")
        return

    df = df[df["error"].isna()].copy()

    # Re-anchor each cell at uniform target SOH
    anchor_rows = []
    for _, row in df.iterrows():
        rpts = json.loads(row["rpts_json"]) if isinstance(row["rpts_json"], str) else row["rpts_json"]
        aged, partial = select_uniform_anchor(rpts, row["fresh_Q"], TARGET_SOH)
        rec = {
            "cond_idx": row["cond_idx"],
            "cell_idx": row["cell_idx"],
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": row["fresh_Q"],
            "fresh_R_DC": row["fresh_R_DC"],
            "fresh_R_total": row["fresh_R_total"],
            "anchor_partial": partial,
        }
        if aged is not None:
            rec.update({
                "uniform_aged_Q": aged["Q_max"],
                "uniform_aged_R_DC": aged["R_DC"],
                "uniform_aged_R_total": aged["R_total"],
                "uniform_aged_cycle": aged["cycle"],
                "uniform_aged_SOH": aged["SOH"],
            })
        else:
            for k in ("uniform_aged_Q", "uniform_aged_R_DC", "uniform_aged_R_total",
                      "uniform_aged_cycle", "uniform_aged_SOH"):
                rec[k] = float("nan")
        anchor_rows.append(rec)

    a_df = pd.DataFrame(anchor_rows)
    n_anchor_partial = a_df["anchor_partial"].sum()
    partial_frac = n_anchor_partial / len(a_df) if len(a_df) > 0 else 0
    print(f"\nUniform anchor (target SOH = {TARGET_SOH}):")
    print(f"  Cells reaching anchor: {(~a_df['anchor_partial']).sum()}")
    print(f"  Anchor_partial (didn't reach 85% SOH): {n_anchor_partial}  ({partial_frac*100:.1f}%)")

    if partial_frac > 0.30:
        print(f"\nH6 INVALID: anchor_partial {partial_frac*100:.1f}% > 30% pre-reg floor")
        a_df.to_parquet(OUT_DIR / "c3_pybamm_uniform_results.parquet")
        return

    # Drop cells with NaN operators
    a_df = a_df.dropna(subset=["uniform_aged_Q", "uniform_aged_R_DC", "uniform_aged_R_total"])

    # Achieved SOH summary -- evidence that anchor IS uniform
    s = a_df["uniform_aged_SOH"]
    print(f"\nAchieved per-cell SOH at anchor:")
    print(f"  mean={s.mean():.4f}, sd={s.std():.4f}, min={s.min():.4f}, max={s.max():.4f}")
    print(f"  (Probe 4 had varied SOH; this run should show tightly clustered SOH around target {TARGET_SOH})")

    # Compute unit residuals (same logic as Probe 4)
    raw_resid = a_df[["uniform_aged_Q", "uniform_aged_R_DC", "uniform_aged_R_total"]].values - \
                a_df[["fresh_Q", "fresh_R_DC", "fresh_R_total"]].values
    fresh_pool = a_df[["fresh_Q", "fresh_R_DC", "fresh_R_total"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    a_df["u1"] = u[:, 0]
    a_df["u2"] = u[:, 1]
    a_df["u3"] = u[:, 2]

    print(f"\n=== Per-parameter PERMANOVAs (Bonferroni alpha/3 = {ALPHA_BONFERRONI}) ===")
    verdicts = {}
    for param_col, label in [("thickness_level", "Cathode thickness"),
                              ("transference_level", "Transference number"),
                              ("particle_radius_level", "Particle radius")]:
        print(f"\n--- {label} ---")
        counts = a_df.groupby(param_col).size().to_dict()
        for lvl in ["low", "mid", "high"]:
            print(f"  {lvl}: n={counts.get(lvl, 0)}")
        for lvl, g in a_df.groupby(param_col):
            uu = g[["u1", "u2", "u3"]].values
            c = uu.mean(axis=0)
            c_n = c / max(np.linalg.norm(c), 1e-12)
            print(f"  centroid {lvl}: ({c_n[0]:+.3f}, {c_n[1]:+.3f}, {c_n[2]:+.3f})  n={len(g)}")
        F, p = permanova_test(a_df[["u1", "u2", "u3"]].values, a_df[param_col].values)
        v = parameter_verdict(F, p)
        verdicts[param_col] = v
        print(f"\n  pseudo-F = {F:.3f}")
        print(f"  p (10000 perm) = {p:.4f}")
        print(f"  VERDICT: {v}")

    jv = joint_verdict(verdicts)
    print(f"\n=== H6 JOINT VERDICT (pre-reg sec.5) ===")
    print(f"  Cathode thickness:   {verdicts['thickness_level']}")
    print(f"  Transference number: {verdicts['transference_level']}")
    print(f"  Particle radius:     {verdicts['particle_radius_level']}  (NULL in Probe 4 also, not primary)")
    print(f"\n  {jv}")

    print(f"\n--- Comparison to Probe 4 (varied-anchor, literature/20) ---")
    print(f"  Probe 4 cathode thickness:   PASS  (F=12.4, p=0.003)")
    print(f"  Probe 4 transference number: PASS  (F=50.6, p=0.0001)")
    print(f"  Probe 4 particle radius:     NULL")

    a_df.to_parquet(OUT_DIR / "c3_pybamm_uniform_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_pybamm_uniform_results.parquet'}")


if __name__ == "__main__":
    main()
