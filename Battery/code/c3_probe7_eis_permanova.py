"""C3 Probe 7 v1 — EIS-triad noise-injection PERMANOVA.

Pre-reg: literature/37_probe7_prereg.md.

Clone of c3_noise_injection.py with the operator triad swapped from
(Q_max, R_DC, R_total) to (Q_max, R_ohmic, R_diff). Reads the EIS-augmented
parquet from probe7_pybamm_eis_generator.py. Same noise levels, same seeds,
same PERMANOVA infra as Probe 6 (per pre-reg §4 + §5).

Headline outcome at Level 2 ("typical academic" noise) is the test of H7.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG_SEED_BASE = 2000  # IDENTICAL to c3_noise_injection.py
N_PERMS = 10000

ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05
TARGET_SOH = 0.92  # uniform anchor convention

# Noise grid N1 -- IDENTICAL Probe-6 sigma values applied to EIS triad
# (sigma_R_DC -> sigma_R_ohmic; sigma_R_total -> sigma_R_diff)
NOISE_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_R_ohmic": 0.00, "sigma_R_diff": 0.00, "name": "0  (baseline)"},
    {"level": 1, "sigma_Q": 0.001, "sigma_R_ohmic": 0.05, "sigma_R_diff": 0.10, "name": "1  (best lab)"},
    {"level": 2, "sigma_Q": 0.005, "sigma_R_ohmic": 0.15, "sigma_R_diff": 0.20, "name": "2  (typical academic, PRIMARY)"},
    {"level": 3, "sigma_Q": 0.010, "sigma_R_ohmic": 0.30, "sigma_R_diff": 0.30, "name": "3  (noisy field)"},
    {"level": 4, "sigma_Q": 0.020, "sigma_R_ohmic": 0.50, "sigma_R_diff": 0.50, "name": "4  (instrument issue)"},
]


def permanova_pseudoF(u_mat, labels):
    """IDENTICAL to c3_noise_injection.permanova_pseudoF."""
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


def build_eis_operator_table(df_raw):
    """Build per-cell fresh + aged EIS-triad operators.

    Aged values come straight from the generator (B7 LAM-proxy applied
    per cell at uniform-anchor Q_loss). Drops cells with anchor_partial=True
    or any NaN EIS column, matching Probe 6's filter convention.
    """
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        if pd.isna(row.get("R_ohmic_aged")) or pd.isna(row.get("R_diff_aged")):
            continue
        if row.get("anchor_partial") is True:
            continue
        rows.append({
            "cond_idx": int(row["cond_idx"]),
            "cell_idx": int(row["cell_idx"]),
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": float(row["fresh_Q"]),
            "fresh_R_ohmic": float(row["R_ohmic_fresh"]),
            "fresh_R_diff": float(row["R_diff_fresh"]),
            "aged_Q": float(row["anchor_aged_Q"]),
            "aged_R_ohmic": float(row["R_ohmic_aged"]),
            "aged_R_diff": float(row["R_diff_aged"]),
        })
    return pd.DataFrame(rows)


def inject_noise_and_standardize(df_clean, sigma_Q, sigma_R_ohmic, sigma_R_diff, level):
    """Per-cell multiplicative Gaussian noise + unit-residual projection.

    Seeds match c3_noise_injection.inject_noise_and_standardize EXACTLY so
    the Q_max noise realizations are bit-identical to Probe 6. The R noise
    realizations differ because the sigma values are applied to different
    operators (R_ohmic vs R_DC; R_diff vs R_total).
    """
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps_fresh_Q = np.empty(n)
    eps_fresh_Ro = np.empty(n)
    eps_fresh_Rd = np.empty(n)
    eps_aged_Q = np.empty(n)
    eps_aged_Ro = np.empty(n)
    eps_aged_Rd = np.empty(n)
    for i, row in df.iterrows():
        seed = RNG_SEED_BASE + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(seed)
        eps_fresh_Q[i] = rng.normal(0, sigma_Q)
        eps_fresh_Ro[i] = rng.normal(0, sigma_R_ohmic)
        eps_fresh_Rd[i] = rng.normal(0, sigma_R_diff)
        eps_aged_Q[i] = rng.normal(0, sigma_Q)
        eps_aged_Ro[i] = rng.normal(0, sigma_R_ohmic)
        eps_aged_Rd[i] = rng.normal(0, sigma_R_diff)

    df["fresh_Q_noisy"] = df["fresh_Q"] * (1 + eps_fresh_Q)
    df["fresh_R_ohmic_noisy"] = df["fresh_R_ohmic"] * (1 + eps_fresh_Ro)
    df["fresh_R_diff_noisy"] = df["fresh_R_diff"] * (1 + eps_fresh_Rd)
    df["aged_Q_noisy"] = df["aged_Q"] * (1 + eps_aged_Q)
    df["aged_R_ohmic_noisy"] = df["aged_R_ohmic"] * (1 + eps_aged_Ro)
    df["aged_R_diff_noisy"] = df["aged_R_diff"] * (1 + eps_aged_Rd)

    raw_resid = df[["aged_Q_noisy", "aged_R_ohmic_noisy", "aged_R_diff_noisy"]].values - \
                df[["fresh_Q_noisy", "fresh_R_ohmic_noisy", "fresh_R_diff_noisy"]].values
    fresh_pool = df[["fresh_Q_noisy", "fresh_R_ohmic_noisy", "fresh_R_diff_noisy"]].values
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
    print(f"=== Probe 7 v1 -- EIS-triad noise-injection PERMANOVA (pre-reg literature/37) ===\n")
    df_raw = pd.read_parquet(IN_PARQUET)
    print(f"Parquet rows: {len(df_raw)}")
    print(f"Successful sims: {df_raw['error'].isna().sum()}")

    df_clean = build_eis_operator_table(df_raw)
    print(f"After anchor-partial + NaN filter: {len(df_clean)} cells")
    if len(df_clean) < 90:
        print(f"\nPROBE 7 INVALID: < 90 cells after filter (got {len(df_clean)})")
        return

    # Pre-reg P7_F3 prep: compute per-feature signal-to-noise on residuals
    raw_q = df_clean["aged_Q"] - df_clean["fresh_Q"]
    raw_ro = df_clean["aged_R_ohmic"] - df_clean["fresh_R_ohmic"]
    raw_rd = df_clean["aged_R_diff"] - df_clean["fresh_R_diff"]
    print(f"\n=== Per-feature signal/noise on clean residuals (P7_F3 prep) ===")
    print(f"  Q_residual:        mean={raw_q.mean():.6g}, sd={raw_q.std():.6g}, |s/n|={abs(raw_q.mean()/raw_q.std()):.2f}")
    print(f"  R_ohmic_residual:  mean={raw_ro.mean():.6g}, sd={raw_ro.std():.6g}, |s/n|={abs(raw_ro.mean()/raw_ro.std()):.2f}")
    print(f"  R_diff_residual:   mean={raw_rd.mean():.6g}, sd={raw_rd.std():.6g}, |s/n|={abs(raw_rd.mean()/raw_rd.std()):.2f}")

    summary_rows = []
    for nl in NOISE_LEVELS:
        print(f"\n--- Noise Level {nl['name']} ---")
        print(f"  sigma_Q={nl['sigma_Q']:.3f}, sigma_R_ohmic={nl['sigma_R_ohmic']:.2f}, sigma_R_diff={nl['sigma_R_diff']:.2f}")
        df_noisy = inject_noise_and_standardize(
            df_clean, nl["sigma_Q"], nl["sigma_R_ohmic"], nl["sigma_R_diff"], nl["level"]
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
            print(f"  {label:25s}: pseudo-F={F:>7.3f}  p={p:.4f}  -> {v}")
        lv = level_verdict(verdicts)
        print(f"  LEVEL VERDICT: {lv}")
        summary_rows.append({
            "level": nl["level"],
            "name": nl["name"],
            "sigma_Q": nl["sigma_Q"],
            "sigma_R_ohmic": nl["sigma_R_ohmic"],
            "sigma_R_diff": nl["sigma_R_diff"],
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
    print("\n=== Calibration curve (EIS triad) ===")
    print(summary[["level", "name", "verdict_thickness", "verdict_transference",
                   "verdict_particle", "level_verdict"]].to_string(index=False))

    # H7 verdict at Level 2 (PRIMARY)
    level_2 = summary[summary["level"] == 2].iloc[0]
    n_pass_at_2 = sum(1 for v in [level_2["verdict_thickness"],
                                    level_2["verdict_transference"],
                                    level_2["verdict_particle"]] if v == "PASS")
    print(f"\n=== PROBE 7 v1 VERDICT (Level 2 = PRIMARY) ===")
    print(f"  EIS-triad params PASSING at Level 2: {n_pass_at_2}/3")
    print(f"  Probe 6 HPPC-triad baseline at Level 2: 0/3 PASS (literature/26)")
    if n_pass_at_2 >= 2:
        verdict = "PROBE 7 STRONG"
        msg = "Operator triad choice carries noise rejection. EIS-derived triad survives where HPPC collapsed."
    elif n_pass_at_2 == 1:
        verdict = "PROBE 7 PARTIAL"
        msg = "EIS triad gains some rejection but doesn't fully reverse Probe 6's collapse."
    else:
        verdict = "PROBE 7 NULL"
        msg = "Operator triad does not carry the noise rejection under the B7 LAM-proxy."
    print(f"  {verdict}")
    print(f"  {msg}")

    # P7_F1 sanity check: Level 0 must achieve >=2/3 PASS
    level_0 = summary[summary["level"] == 0].iloc[0]
    n_pass_at_0 = sum(1 for v in [level_0["verdict_thickness"],
                                    level_0["verdict_transference"],
                                    level_0["verdict_particle"]] if v == "PASS")
    print(f"\n  P7_F1 sanity at Level 0: {n_pass_at_0}/3 PASS",
          "OK" if n_pass_at_0 >= 2 else "VIOLATED -> INCOHERENT")

    summary.to_parquet(OUT_DIR / "probe7_eis_noise_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'probe7_eis_noise_results.parquet'}")


if __name__ == "__main__":
    main()
