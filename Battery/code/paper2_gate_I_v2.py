"""
Paper 2 — Gate I v2 (category-specific stability tests).

Implements the diagnostic-driven amendment in literature/30:
- Slope-like operators (T1, T2, T3, T4, T5, C1, CE1): bootstrap rank-stability.
  For each cohort, B=1000 bootstrap re-samples of the cell-level operator
  vector. For each bootstrap, compute Spearman rank correlation between the
  original ranks and the bootstrap-induced ranks (restricted to cells that
  appear in both). Median across B bootstraps = rho_median.
  Pass cohort if rho_median >= 0.50.

- Level-like operators (E1, E2, E3, C2, D1): CV<0.30, with IQR/|median|<0.30
  fallback when signal-to-noise on the mean is below 10 (|mean| < 10 *
  SD/sqrt(n), i.e., t-stat of mean < 10).

Cross-cohort rule unchanged from literature/28 §3: pass if test passes in
>=3 of 4 cohorts (or >=75% of available cohorts if some excluded by NaN /
data unavailability).

Locked at literature/30, commit 3ad6c5c. Pre-reg-honest re-run.

Output: paper2_gate_I_v2_results.parquet.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, rankdata

PROCESSED = Path("D:/Renewables/Battery/data/processed")
BOOTSTRAPS = 1000
RANK_STABILITY_THRESHOLD = 0.50
CV_THRESHOLD = 0.30
SNR_FALLBACK_TRIGGER = 10.0  # |mean| < 10 * SE_mean → use IQR/|median|

SLOPE_LIKE = {
    "T1_Q_fade_early", "T2_Q_fade_late", "T3_Q_knee_onset",
    "T4_R_DC_growth_rate", "T5_R_DC_acceleration",
    "C1_R_growth_per_Q_lost", "CE1_coulombic_drift",
}
LEVEL_LIKE = {
    "E1_ohmic_intercept", "E2_charge_transfer_radius", "E3_diffusion_slope",
    "C2_R_DC_to_R_total", "D1_dQdV_peak_shift",
}
OPERATOR_COLS = sorted(SLOPE_LIKE | LEVEL_LIKE)

CATEGORY = {
    "T1_Q_fade_early": "Capacity trajectory",
    "T2_Q_fade_late": "Capacity trajectory",
    "T3_Q_knee_onset": "Capacity trajectory",
    "T4_R_DC_growth_rate": "Impedance trajectory",
    "T5_R_DC_acceleration": "Impedance trajectory",
    "E1_ohmic_intercept": "EIS spectral",
    "E2_charge_transfer_radius": "EIS spectral",
    "E3_diffusion_slope": "EIS spectral",
    "C1_R_growth_per_Q_lost": "Cross-operator ratio",
    "C2_R_DC_to_R_total": "Cross-operator ratio",
    "CE1_coulombic_drift": "Differential / shape",
    "D1_dQdV_peak_shift": "Differential / shape",
}

FAMILY = {op: ("slope" if op in SLOPE_LIKE else "level") for op in OPERATOR_COLS}


def rank_stability_bootstrap(values, n_boot=BOOTSTRAPS, seed=42):
    """
    Per literature/30 §2.1: bootstrap re-sample cells with replacement;
    on each bootstrap, compute Spearman rank correlation between original
    cell ranks and the bootstrap-induced ranks (a re-sampled value's rank
    among the bootstrap vector vs. its rank in the original vector). Take
    median across bootstraps.

    Returns NaN if fewer than 5 finite values (cannot bootstrap stably).
    """
    v = np.asarray(values, dtype=float)
    mask = np.isfinite(v)
    v = v[mask]
    n = len(v)
    if n < 5:
        return float("nan")

    rng = np.random.default_rng(seed)
    orig_ranks = rankdata(v, method="average")

    rhos = []
    for _ in range(n_boot):
        # Resample n cells WITH replacement
        idx = rng.integers(0, n, size=n)
        v_boot = v[idx]
        # The "bootstrap-induced rank" of each original cell = rank of its
        # ORIGINAL value when inserted into the bootstrap vector. Equivalently:
        # rank cell i by where it would sit in the bootstrap sample.
        # Operationally: for each cell i, the count of bootstrap values <= v[i].
        boot_sorted = np.sort(v_boot)
        # rank of v[i] in boot_sorted: fraction <= v[i], scaled
        boot_ranks = np.searchsorted(boot_sorted, v, side="right")
        # tie-corrected average rank
        boot_ranks_left = np.searchsorted(boot_sorted, v, side="left")
        boot_ranks_avg = 0.5 * (boot_ranks + boot_ranks_left + 1)
        rho, _ = spearmanr(orig_ranks, boot_ranks_avg)
        if np.isnan(rho):
            continue
        rhos.append(rho)

    if not rhos:
        return float("nan")
    return float(np.median(rhos))


def cv_with_iqr_fallback(values):
    """
    Per literature/30 §2.2: CV = SD/|mean|, but fall back to IQR/|median|
    when t-statistic on the mean (|mean| / SE_mean) is < 10. Returns
    (metric_value, which_metric_used).
    """
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    n = len(v)
    if n < 3:
        return float("nan"), "insufficient_data"

    mu = float(np.mean(v))
    sd = float(np.std(v, ddof=1))
    se_mu = sd / np.sqrt(n)

    # Signal-to-noise on the mean estimate itself
    if se_mu == 0:
        snr = float("inf")
    else:
        snr = abs(mu) / se_mu

    if snr >= SNR_FALLBACK_TRIGGER and abs(mu) > 1e-12:
        return sd / abs(mu), "CV"
    else:
        # IQR / |median| fallback
        q75, q25 = np.percentile(v, [75, 25])
        med = float(np.median(v))
        if abs(med) < 1e-12:
            return float("inf"), "IQR_over_zero_median"
        return (q75 - q25) / abs(med), "IQR_over_median"


def main():
    print("=== Paper 2 Gate I v2 — category-specific stability (literature/30) ===\n")
    print(f"Slope-like operators (rank-stability rho_median >= {RANK_STABILITY_THRESHOLD}):")
    for op in sorted(SLOPE_LIKE):
        print(f"  {op}")
    print(f"\nLevel-like operators (CV < {CV_THRESHOLD}, IQR/|median| fallback):")
    for op in sorted(LEVEL_LIKE):
        print(f"  {op}")
    print()

    cohorts = {}
    for name, path in [
        ("SECL_first_life", "paper2_operators_secl.parquet"),
        ("Khan_2025", "paper2_operators_khan.parquet"),
        ("Zhang_Cambridge_v2", "paper2_operators_zhang.parquet"),
        ("Severson", "paper2_operators_severson.parquet"),
    ]:
        p = PROCESSED / path
        if not p.exists():
            print(f"  [WARNING] {name} parquet missing at {p}")
            continue
        cohorts[name] = pd.read_parquet(p)

    print(f"Cohorts loaded: {list(cohorts.keys())}")
    print(f"Per-cohort n: {[(k, len(v)) for k, v in cohorts.items()]}\n")

    rows = []
    for op in OPERATOR_COLS:
        family = FAMILY[op]
        per_cohort = {}

        for cname, df in cohorts.items():
            if op not in df.columns:
                per_cohort[cname] = {"metric": float("nan"), "kind": "operator_missing"}
                continue
            vals = df[op].values
            finite = np.isfinite(vals).sum()
            if finite < 3:
                per_cohort[cname] = {"metric": float("nan"), "kind": "data_unavailable"}
                continue

            if family == "slope":
                m = rank_stability_bootstrap(vals)
                per_cohort[cname] = {"metric": m, "kind": "rank_stability_rho"}
            else:
                m, kind = cv_with_iqr_fallback(vals)
                per_cohort[cname] = {"metric": m, "kind": kind}

        # Determine passes
        if family == "slope":
            pass_flags = {c: (np.isfinite(d["metric"]) and d["metric"] >= RANK_STABILITY_THRESHOLD)
                          for c, d in per_cohort.items()}
        else:
            pass_flags = {c: (np.isfinite(d["metric"]) and d["metric"] < CV_THRESHOLD)
                          for c, d in per_cohort.items()}

        finite_count = sum(1 for d in per_cohort.values() if np.isfinite(d["metric"]))
        pass_count = sum(1 for v in pass_flags.values() if v)
        # Cross-cohort rule: >=3 of 4 ideal; 75% of available cohorts otherwise; never < 2
        if finite_count == 4:
            required = 3
        elif finite_count >= 2:
            required = max(2, int(np.ceil(0.75 * finite_count)))
        else:
            required = 99  # impossible to pass with <2 finite cohorts
        passed = (pass_count >= required) and (finite_count >= 2)

        row = {
            "operator": op,
            "category": CATEGORY[op],
            "family": family,
            "passed_gate_I": bool(passed),
            "cohorts_with_data": finite_count,
            "cohorts_passing": pass_count,
            "required_passes": required,
            "metric_SECL": per_cohort.get("SECL_first_life", {}).get("metric", float("nan")),
            "metric_Khan": per_cohort.get("Khan_2025", {}).get("metric", float("nan")),
            "metric_Zhang": per_cohort.get("Zhang_Cambridge_v2", {}).get("metric", float("nan")),
            "metric_Severson": per_cohort.get("Severson", {}).get("metric", float("nan")),
            "kind_SECL": per_cohort.get("SECL_first_life", {}).get("kind", ""),
            "kind_Khan": per_cohort.get("Khan_2025", {}).get("kind", ""),
            "kind_Zhang": per_cohort.get("Zhang_Cambridge_v2", {}).get("kind", ""),
            "kind_Severson": per_cohort.get("Severson", {}).get("kind", ""),
        }
        rows.append(row)

    df_gate1 = pd.DataFrame(rows)

    def fmt(v):
        return f"{v:.3f}" if np.isfinite(v) else "  --"

    print("=== Per-operator Gate I v2 results ===\n")
    print(f"{'operator':<26} {'family':<6} {'SECL':>7} {'Khan':>7} {'Zhang':>7} {'Sevn':>7}  {'pass/n':>6}  {'PASS':>5}")
    print("-" * 90)
    for _, r in df_gate1.iterrows():
        verdict = "YES" if r["passed_gate_I"] else "no"
        print(f"  {r['operator']:<24} {r['family']:<6} "
              f"{fmt(r['metric_SECL']):>7} {fmt(r['metric_Khan']):>7} "
              f"{fmt(r['metric_Zhang']):>7} {fmt(r['metric_Severson']):>7}  "
              f"{int(r['cohorts_passing'])}/{int(r['cohorts_with_data'])}    {verdict:>5}")

    print("\n=== Attrition by physics category ===\n")
    for cat in sorted(df_gate1["category"].unique()):
        sub = df_gate1[df_gate1["category"] == cat]
        n_pass = sub["passed_gate_I"].sum()
        n_total = len(sub)
        print(f"  {cat:30s}: {n_pass}/{n_total} survived")

    n_pass = df_gate1["passed_gate_I"].sum()
    n_total = len(df_gate1)
    print(f"\nOverall: {n_pass}/{n_total} operators survived amended Gate I")

    df_gate1.to_parquet(PROCESSED / "paper2_gate_I_v2_results.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_gate_I_v2_results.parquet'}")


if __name__ == "__main__":
    main()
