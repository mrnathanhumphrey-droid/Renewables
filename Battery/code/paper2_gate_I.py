"""
Paper 2 — Gate I (cross-cohort consistency).

Per pre-reg literature/28 §3: for each candidate operator, compute the
coefficient of variation (CV) across cells within each Gate I cohort. Pass if
CV < 0.30 in at least 3 of 4 cohorts. Cohorts where the operator is uniformly
NaN are excluded from the count (denominator adjusts).

Gate I cohorts: SECL + Khan + Zhang + Severson.

Output: paper2_gate_I_survivors.parquet (operator list with PASS/FAIL +
per-cohort CV).
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROCESSED = Path("D:/Renewables/Battery/data/processed")
CV_THRESHOLD = 0.30
COHORT_PASS_REQUIRED = 3  # of 4 cohorts

OPERATOR_COLS = [
    "T1_Q_fade_early", "T2_Q_fade_late", "T3_Q_knee_onset",
    "T4_R_DC_growth_rate", "T5_R_DC_acceleration",
    "E1_ohmic_intercept", "E2_charge_transfer_radius", "E3_diffusion_slope",
    "C1_R_growth_per_Q_lost", "C2_R_DC_to_R_total",
    "CE1_coulombic_drift", "D1_dQdV_peak_shift",
]

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


def compute_cv(values):
    """CV = SD / |mean|; NaN if insufficient finite values or near-zero mean."""
    v = np.array(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) < 3:
        return float("nan")
    mu = float(np.mean(v))
    sd = float(np.std(v, ddof=1))
    if abs(mu) < 1e-12:
        return float("nan")
    return sd / abs(mu)


def main():
    print("=== Paper 2 Gate I — cross-cohort consistency (pre-reg literature/28 §3) ===\n")

    # Load all 4 Gate I cohorts
    cohorts = {}
    for name, path in [
        ("SECL_first_life", "paper2_operators_secl.parquet"),
        ("Khan_2025", "paper2_operators_khan.parquet"),
        ("Zhang_Cambridge_v2", "paper2_operators_zhang.parquet"),
        ("Severson", "paper2_operators_severson.parquet"),
    ]:
        p = PROCESSED / path
        if not p.exists():
            print(f"  [WARNING] {name} parquet missing at {p} — excluded from Gate I")
            continue
        cohorts[name] = pd.read_parquet(p)

    print(f"Cohorts loaded: {list(cohorts.keys())}")
    print(f"Per-cohort n: {[(k, len(v)) for k, v in cohorts.items()]}\n")

    rows = []
    for op in OPERATOR_COLS:
        per_cohort_cv = {}
        for cname, df in cohorts.items():
            if op not in df.columns:
                continue
            cv = compute_cv(df[op].values)
            per_cohort_cv[cname] = cv

        # Count cohorts where CV is finite AND below threshold
        finite_cv_count = sum(1 for v in per_cohort_cv.values() if np.isfinite(v))
        pass_count = sum(1 for v in per_cohort_cv.values()
                          if np.isfinite(v) and v < CV_THRESHOLD)

        # PASS logic: at least 3 of 4 if all 4 available; or 3 of remaining if
        # one cohort excluded; down to 1 of 2 = NOT enough.
        required = COHORT_PASS_REQUIRED
        if finite_cv_count < 4:
            # Reduce required proportionally: ceil(3/4 * finite_cv_count)
            required = max(2, int(np.ceil(0.75 * finite_cv_count)))
        passed = (pass_count >= required) and (finite_cv_count >= 2)

        row = {
            "operator": op,
            "category": CATEGORY[op],
            "passed_gate_I": bool(passed),
            "cohorts_with_data": finite_cv_count,
            "cohorts_below_CV_threshold": pass_count,
            "required_pass_count": required,
            "CV_SECL": per_cohort_cv.get("SECL_first_life", float("nan")),
            "CV_Khan": per_cohort_cv.get("Khan_2025", float("nan")),
            "CV_Zhang": per_cohort_cv.get("Zhang_Cambridge_v2", float("nan")),
            "CV_Severson": per_cohort_cv.get("Severson", float("nan")),
        }
        rows.append(row)

    df_gate1 = pd.DataFrame(rows)

    # Report by operator
    print("=== Per-operator Gate I results ===\n")
    fmt_cv = lambda v: f"{v:.3f}" if np.isfinite(v) else "  --"
    print(f"{'operator':<26} {'category':<25} {'SECL':>6} {'Khan':>6} {'Zhang':>6} {'Sevn':>6} {'n_pass':>7} {'req':>5} {'PASS':>6}")
    for _, r in df_gate1.iterrows():
        verdict = "YES" if r["passed_gate_I"] else "no"
        print(f"  {r['operator']:<24} {r['category']:<25}  "
              f"{fmt_cv(r['CV_SECL']):>6} {fmt_cv(r['CV_Khan']):>6} "
              f"{fmt_cv(r['CV_Zhang']):>6} {fmt_cv(r['CV_Severson']):>6} "
              f"{int(r['cohorts_below_CV_threshold']):>5}/{int(r['cohorts_with_data']):<2} "
              f"{int(r['required_pass_count']):>5} {verdict:>6}")

    # Attrition summary by physics category (per pre-reg literature/27 §5)
    print("\n=== Attrition by physics category ===\n")
    for cat in sorted(df_gate1["category"].unique()):
        sub = df_gate1[df_gate1["category"] == cat]
        n_pass = sub["passed_gate_I"].sum()
        n_total = len(sub)
        print(f"  {cat:30s}: {n_pass}/{n_total} survived")

    n_pass = df_gate1["passed_gate_I"].sum()
    n_total = len(df_gate1)
    print(f"\nOverall: {n_pass}/{n_total} operators survived Gate I (CV<{CV_THRESHOLD} in >={COHORT_PASS_REQUIRED} of available cohorts)")

    df_gate1.to_parquet(PROCESSED / "paper2_gate_I_results.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_gate_I_results.parquet'}")


if __name__ == "__main__":
    main()
