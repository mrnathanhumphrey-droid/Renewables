"""
C3 Probe 6 — Synthetic noise injection (real-cell-noise threshold test).

Pre-reg: literature/25_c3_noise_injection_pre_registration.md (commit 4a3e932).

Post-hoc analysis on Probe 5's PyBaMM trajectories. Injects multiplicative
Gaussian noise on the operator triad at 5 pre-registered noise levels, recomputes
per-cell standardization with NOISY fresh-pool SD, re-runs the 3 per-parameter
PERMANOVAs.

Output: noise-level x parameter PASS table (calibration curve) + H7 joint verdict.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG_SEED_BASE = 2000
N_PERMS = 10000

ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05
TARGET_SOH = 0.92  # per Probe 5 amended pre-reg

NOISE_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_R_DC": 0.00, "sigma_R_total": 0.00, "name": "0  (baseline)"},
    {"level": 1, "sigma_Q": 0.001, "sigma_R_DC": 0.05, "sigma_R_total": 0.10, "name": "1  (best lab)"},
    {"level": 2, "sigma_Q": 0.005, "sigma_R_DC": 0.15, "sigma_R_total": 0.20, "name": "2  (typical academic, PRIMARY)"},
    {"level": 3, "sigma_Q": 0.010, "sigma_R_DC": 0.30, "sigma_R_total": 0.30, "name": "3  (noisy field)"},
    {"level": 4, "sigma_Q": 0.020, "sigma_R_DC": 0.50, "sigma_R_total": 0.50, "name": "4  (instrument issue)"},
]


# --- PERMANOVA infra (same as prior probes) ---

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


def permanova_test(u_mat, labels, rng, n_perms=N_PERMS):
    F_obs = permanova_pseudoF(u_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
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


def level_verdict(verdicts):
    n_pass = sum(1 for v in verdicts.values() if v == "PASS")
    n_weak = sum(1 for v in verdicts.values() if v == "WEAK PASS")
    if n_pass >= 2:
        return "LEVEL ROBUST"
    if n_pass == 1 and n_weak >= 1:
        return "LEVEL WEAK"
    if n_pass == 1:
        return "LEVEL WEAK"
    return "LEVEL COLLAPSED"


# --- Uniform-anchor pick (Probe 5 logic) ---

def select_uniform_anchor(rpts, fresh_Q, target_soh):
    if not rpts:
        return None, True
    target_Q = target_soh * fresh_Q
    post = [r for r in rpts if r["cycle"] > 25]
    if not post:
        return None, True
    best = min(post, key=lambda r: abs(r["Q_max"] - target_Q))
    soh = best["Q_max"] / fresh_Q
    partial = soh > target_soh + 0.02
    return {"Q_max": best["Q_max"], "R_DC": best["R_DC"], "R_total": best["R_total"],
            "cycle": best["cycle"], "SOH": soh}, partial


def build_clean_operator_table(df_raw):
    """Recompute Probe 5's uniform-anchor fresh + aged values per cell."""
    rows = []
    for _, row in df_raw.iterrows():
        rpts = json.loads(row["rpts_json"]) if isinstance(row["rpts_json"], str) else row["rpts_json"]
        if not rpts:
            continue
        # Fresh = mean over rpts in cycles 5-25
        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            continue
        fresh_Q = float(np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(np.mean([r["R_total"] for r in fresh_rpts]))
        aged, partial = select_uniform_anchor(rpts, fresh_Q, TARGET_SOH)
        if aged is None or partial:
            continue
        rows.append({
            "cond_idx": int(row["cond_idx"]),
            "cell_idx": int(row["cell_idx"]),
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": fresh_Q,
            "fresh_R_DC": fresh_R_DC,
            "fresh_R_total": fresh_R_total,
            "aged_Q": aged["Q_max"],
            "aged_R_DC": aged["R_DC"],
            "aged_R_total": aged["R_total"],
        })
    return pd.DataFrame(rows)


def inject_noise_and_standardize(df_clean, sigma_Q, sigma_R_DC, sigma_R_total, level):
    """Apply per-cell, per-operator multiplicative Gaussian noise on fresh + aged
    values. Return df with u1, u2, u3 unit residual vectors based on NOISY pool SD."""
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    # Per-cell noise: seed by level + cond + cell so reproducible
    eps_fresh_Q = np.empty(n)
    eps_fresh_R_DC = np.empty(n)
    eps_fresh_R_total = np.empty(n)
    eps_aged_Q = np.empty(n)
    eps_aged_R_DC = np.empty(n)
    eps_aged_R_total = np.empty(n)
    for i, row in df.iterrows():
        seed = RNG_SEED_BASE + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(seed)
        eps_fresh_Q[i] = rng.normal(0, sigma_Q)
        eps_fresh_R_DC[i] = rng.normal(0, sigma_R_DC)
        eps_fresh_R_total[i] = rng.normal(0, sigma_R_total)
        eps_aged_Q[i] = rng.normal(0, sigma_Q)
        eps_aged_R_DC[i] = rng.normal(0, sigma_R_DC)
        eps_aged_R_total[i] = rng.normal(0, sigma_R_total)

    df["fresh_Q_noisy"] = df["fresh_Q"] * (1 + eps_fresh_Q)
    df["fresh_R_DC_noisy"] = df["fresh_R_DC"] * (1 + eps_fresh_R_DC)
    df["fresh_R_total_noisy"] = df["fresh_R_total"] * (1 + eps_fresh_R_total)
    df["aged_Q_noisy"] = df["aged_Q"] * (1 + eps_aged_Q)
    df["aged_R_DC_noisy"] = df["aged_R_DC"] * (1 + eps_aged_R_DC)
    df["aged_R_total_noisy"] = df["aged_R_total"] * (1 + eps_aged_R_total)

    raw_resid = df[["aged_Q_noisy", "aged_R_DC_noisy", "aged_R_total_noisy"]].values - \
                df[["fresh_Q_noisy", "fresh_R_DC_noisy", "fresh_R_total_noisy"]].values
    fresh_pool = df[["fresh_Q_noisy", "fresh_R_DC_noisy", "fresh_R_total_noisy"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    df["u1"] = u[:, 0]
    df["u2"] = u[:, 1]
    df["u3"] = u[:, 2]
    return df


def main():
    print(f"=== C3 Probe 6 -- Noise-injection threshold test (pre-reg literature/25) ===\n")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_raw = df_raw[df_raw["error"].isna()].copy() if "error" in df_raw.columns else df_raw.copy()
    print(f"Probe 5 sim-success cells: {len(df_raw)}")

    df_clean = build_clean_operator_table(df_raw)
    print(f"After uniform-anchor at SOH {TARGET_SOH}: {len(df_clean)} cells (anchor_partial excluded)")
    if len(df_clean) < 90:
        print(f"\nH7 INVALID: < 90 cells after anchor")
        return

    # Run PERMANOVA at each noise level
    summary_rows = []
    for nl in NOISE_LEVELS:
        print(f"\n--- Noise Level {nl['name']}  ---")
        print(f"  sigma_Q={nl['sigma_Q']:.3f}, sigma_R_DC={nl['sigma_R_DC']:.2f}, sigma_R_total={nl['sigma_R_total']:.2f}")
        df_noisy = inject_noise_and_standardize(
            df_clean, nl["sigma_Q"], nl["sigma_R_DC"], nl["sigma_R_total"], nl["level"]
        )
        u_mat = df_noisy[["u1", "u2", "u3"]].values
        rng_p = np.random.default_rng(RNG_SEED_BASE + 999000 + nl["level"])
        verdicts = {}
        params_F = {}
        params_p = {}
        for param_col, label in [("thickness_level", "Cathode thickness"),
                                   ("transference_level", "Transference number"),
                                   ("particle_radius_level", "Particle radius")]:
            F, p = permanova_test(u_mat, df_noisy[param_col].values, rng_p)
            v = parameter_verdict(F, p)
            verdicts[param_col] = v
            params_F[param_col] = F
            params_p[param_col] = p
            print(f"  {label:25s}: pseudo-F={F:>6.3f}  p={p:.4f}  -> {v}")
        lv = level_verdict(verdicts)
        print(f"  LEVEL VERDICT: {lv}")
        summary_rows.append({
            "level": nl["level"],
            "name": nl["name"],
            "sigma_Q": nl["sigma_Q"],
            "sigma_R_DC": nl["sigma_R_DC"],
            "sigma_R_total": nl["sigma_R_total"],
            "F_thickness": params_F["thickness_level"],
            "p_thickness": params_p["thickness_level"],
            "F_transference": params_F["transference_level"],
            "p_transference": params_p["transference_level"],
            "F_particle": params_F["particle_radius_level"],
            "p_particle": params_p["particle_radius_level"],
            "verdict_thickness": verdicts["thickness_level"],
            "verdict_transference": verdicts["transference_level"],
            "verdict_particle": verdicts["particle_radius_level"],
            "level_verdict": lv,
        })

    summary = pd.DataFrame(summary_rows)
    print("\n=== Calibration curve (params PASSING per noise level) ===")
    print(summary[["level", "name", "verdict_thickness", "verdict_transference", "verdict_particle", "level_verdict"]].to_string(index=False))

    # H7 verdict: focus on Level 2 (PRIMARY)
    level_2 = summary[summary["level"] == 2].iloc[0]
    n_pass_at_2 = sum(1 for v in [level_2["verdict_thickness"], level_2["verdict_transference"], level_2["verdict_particle"]] if v == "PASS")
    print(f"\n=== H7 VERDICT (PRIMARY = Level 2: 0.5% Q, 15% R_DC, 20% R_total) ===")
    print(f"  Params PASSING at Level 2: {n_pass_at_2}/3")
    if n_pass_at_2 <= 1:
        h7 = "H7 SUPPORTS NOISE EXPLANATION"
        msg = "Level 2 (typical academic real-cell noise) collapses the C3 signal -- real-cell measurement noise IS sufficient to reproduce Severson-like null."
    elif n_pass_at_2 == 2:
        h7 = "H7 BORDERLINE"
        msg = "Level 2 retains 2 of 3 params PASSING (similar to Probe 4); on the threshold."
    else:
        h7 = "H7 REJECTS NOISE EXPLANATION"
        msg = "Level 2 retains all 3 params PASSING -- measurement noise alone NOT sufficient to reproduce Severson-like null. Other sources (chemistry heterogeneity, batch effects, calendar variation) required."
    print(f"  {h7}")
    print(f"  {msg}")

    summary.to_parquet(OUT_DIR / "c3_noise_injection_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_noise_injection_results.parquet'}")


if __name__ == "__main__":
    main()
