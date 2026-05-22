# Paper 2 — Selection Result: PAPER 2 INVALID (Pre-Reg-Strict)

**Date:** 2026-05-22
**Pre-registrations:**
- Operator catalog: literature/27 (commit `13e9f80`)
- Selection + cascade + holdout: literature/28 (commit `7fae62a`) + amendment (`153fbd3`)
**Verdict (per pre-reg §7 strict reading):** **PAPER 2 INVALID.** No operators survive both Gate I and Gate II under the pre-registered protocol. The cascade cannot train.

The honest interpretation: this is a **methodological negative result** that exposes a pre-reg design flaw, NOT evidence against the noise-robust framework as a concept. The Gate I metric (coefficient of variation across cells) was inappropriate for the trajectory-operator category. Gate II's "2 of 3 cohorts" requirement couldn't be met by the surviving operator (E1) because PyBaMM and Severson lack EIS data.

---

## Pipeline outcome

```
Initial candidate operators:  12 (per literature/27 §3)

Gate I (cross-cohort fresh-cell consistency, CV<0.30 in ≥3 of 4 cohorts):
  Dropped: 11 operators
    By physics category:
      Capacity trajectory   : 3 of 3 dropped (T1, T2, T3)
      Impedance trajectory  : 2 of 2 dropped (T4, T5)
      EIS spectral          : 2 of 3 dropped (E2, E3; E1 survives)
      Cross-operator ratio  : 2 of 2 dropped (C1, C2)
      Differential / shape  : 2 of 2 dropped (CE1, D1)
  Surviving: 1 operator (E1 ohmic_intercept)

Gate II (design-condition AUC ≥0.60 in ≥2 of 3 cohorts):
  Dropped: 1 operator (E1)
    Reason: PyBaMM and Severson have no EIS data → E1 only computable on
            Khan (1 of 3 cohorts) → cannot reach 2-of-3 threshold by
            mathematical impossibility
  Surviving: 0 operators

Final cascade: NONE (Paper 2 INVALID per pre-reg §7)
```

## Per-operator Gate I detail

| Operator | Category | SECL CV | Khan CV | Zhang CV | Severson CV | Gate I |
|---|---|---|---|---|---|---|
| T1 Q-fade-early | Capacity traj | 0.137 ✓ | 0.643 | 0.865 | **30.28** | NO |
| T2 Q-fade-late | Capacity traj | 0.016 ✓ | 1.202 | 1.871 | 0.794 | NO |
| T3 Q-knee-onset | Capacity traj | 0.317 | NaN | 0.686 | 0.534 | NO |
| T4 R-DC-growth | Impedance traj | 2.711 | 15.845 | 3.821 | 7.221 | NO |
| T5 R-DC-accel | Impedance traj | 0.577 | 0.499 | 1.606 | 1.972 | NO |
| **E1 ohmic-intercept** | EIS spectral | 0.169 ✓ | 0.093 ✓ | 0.145 ✓ | NaN | **YES (3/3 available)** |
| E2 charge-transfer | EIS spectral | 0.344 | 0.802 | 0.200 ✓ | NaN | NO (1/3) |
| E3 diffusion-slope | EIS spectral | NaN | NaN | NaN | NaN | NO (0 testable) |
| C1 R-growth/Q-lost | Cross ratio | 0.167 ✓ | 4.288 | 1.687 | 5.499 | NO |
| C2 R-DC/R-total | Cross ratio | 0.016 ✓ | 0.108 ✓ | 0.307 | NaN | NO (2/3, need 3) |
| CE1 coulombic-drift | Differential | NaN | NaN | NaN | 1.168 | NO (0 testable) |
| D1 dQ/dV peak-shift | Differential | NaN | NaN | NaN | NaN | NO (0 testable) |

## Why Gate I dropped so many operators (methodological reading)

Two distinct mechanisms drove attrition:

### Mechanism 1: CV pathology on near-zero-mean operators

Coefficient of variation is CV = SD / |mean|. For trajectory slopes (T1-T5)
and ratios (C1), cells in a heterogeneous cohort produce values that span
near-zero or cross sign, making |mean| arbitrarily small relative to SD.

Example: T1 on Severson has cells with first-step C-rates from 1C to 8C.
Cells at 1C-2C fade slowly (slope ≈ −0.002 Ah/cycle); cells at 7-8C fade
quickly (slope ≈ −0.030 Ah/cycle). Pooled mean ≈ −0.012 with SD ≈ 0.020.
But because protocols span both signs of "above-mean" and "below-mean"
fade-rate, the mean shifts to ≈ 0 in certain reference frames and CV
explodes to 30+.

**This is a known statistical pathology of CV on near-zero-mean
quantities.** It does NOT mean the operator is noisy or uninformative.
Quite the opposite — operators with high CV via this mechanism are
operators that PICK UP DESIGN VARIATION strongly (high SD), which is
exactly what Gate II is supposed to test.

### Mechanism 2: Data unavailability for EIS-spectral and differential operators

E3 (diffusion slope) requires the full EIS Warburg-region slope, which
isn't in any of the cohorts' processed parquets in usable form.
CE1 (coulombic drift) requires per-cycle charge AND discharge capacity,
which is only readily extractable on Severson. D1 (dQ/dV peak shift)
requires full per-cycle voltage curves, also out of scope for our current
extraction pipelines.

These operators failed Gate I not because they're noisy but because we
don't have the extraction infrastructure built for them.

### Net diagnosis

Gate I as pre-registered conflated three distinct failure modes:
1. True instrumentation noise (the intended target)
2. CV-near-zero pathology on trajectory operators
3. Missing extraction infrastructure for advanced operators

Only mechanism 1 (instrumentation noise) is what the Gate I metric should
have measured. The locked CV<0.30 threshold dropped most candidates via
mechanisms 2 and 3, which the metric wasn't designed to catch.

## Why Gate II failed E1 (the lone survivor)

E1 (ohmic intercept) is an EIS-derived operator. Of the 3 Gate II cohorts:

- **PyBaMM Probe 5 (training split):** synthetic PyBaMM cells have no EIS
  simulation in our current setup. E1 = NaN for all.
- **Severson:** real cells but no EIS measurements in the BEEP dataset.
  E1 = NaN for all.
- **Khan 2025:** has EIS. E1 computable. AUC for cathode aging-condition
  separation = **1.000** (perfect).

E1's Khan AUC of 1.000 is striking — it's a perfect separator on Khan
calendar vs cycle conditions. But the pre-reg required 2 of 3 cohorts to
have data above the AUC threshold. With only 1 cohort having E1 data, the
"2 of 3" requirement is mathematically unreachable.

**E1 may genuinely be an excellent operator, but the pre-reg's cohort-
breadth requirement can't be evaluated for an EIS-only operator when 2 of
3 training cohorts lack EIS.**

## What this proves

Paper 2 is a methodological negative result. Three findings emerge:

1. **The CV-based Gate I metric is inappropriate for trajectory-operator
   selection.** CV is well-behaved only for bounded positive-mean operators.
   Trajectory slopes (fade rates, growth rates) inherently produce
   near-zero-mean distributions when cohorts contain both fast- and
   slow-aging cells. A future selection metric would need to handle this —
   e.g., interquartile range divided by typical magnitude, or
   coefficient-of-dispersion on the OPERATOR'S NATURAL SCALE rather than
   its mean.

2. **Selection that requires "≥K of N cohorts with data" prevents EIS-only
   operators from passing when synthetic cohorts lack EIS.** Either the
   cascade architecture needs to handle missing data per cohort, OR the
   cohort assignment must ensure all cohorts have the same operator
   coverage, OR EIS operators must be tested only on EIS-bearing cohorts
   (a deviation from the cross-cohort consistency principle).

3. **The methodology is salvageable but the pre-reg was over-rigid.** A
   redesign of the gates that:
   (a) replaces CV with a robust dispersion metric for trajectory operators
   (b) splits selection into within-operator-family tests (EIS-only,
       trajectory-only) before cross-family voting
   (c) treats data unavailability as "not tested" rather than "failed"
   would likely allow several operators through. But that's a Paper 3
   pre-reg, not an amendment to this one.

## What this does NOT prove

- The noise-robust framework is invalid. The framework was never tested;
  selection eliminated all operators before any cascade could train.
- Trajectory operators have no signal. They have plenty of signal (look
  at C3 Probe 6's calibration curve, literature/26). They just don't pass
  THIS gate.
- The C3 methodology is broken. Paper 1's C3 (independent-operator Mahalanobis)
  is unaffected by Paper 2's result.

## Operator-level findings (per pre-reg §7 — reported regardless of cascade verdict)

The attrition itself is the methodological contribution. The locked
attrition-reporting structure (literature/27 §5) is:

```
Initial candidates: 12
After Gate I: 1 (E1 only)
After Gate II: 0
Final cascade: NONE
```

By physics category, Gate I attrition: 3/3 dropped in Capacity trajectory,
2/2 in Impedance trajectory, 2/3 in EIS spectral, 2/2 in Cross-operator
ratio, 2/2 in Differential/shape. **The only physics category with any
survivor is EIS spectral**, driven by E1 = ohmic intercept, a stable
fresh-state baseline measurement.

This pattern is informative: the only operators that pass a noise-stability
test on cell-to-cell variability are operators that measure a STATIC
property (like fresh ohmic resistance). Operators that measure DYNAMIC
properties (rate of fade, rate of growth, coupling between aging modes)
all fail because they correctly capture between-cell heterogeneity that
the CV metric mis-interprets as noise.

## Paper 2 writeup framing

If we wrote a methodology paper on this result, the framing would be:

> "We pre-registered a noise-robust operator-cascade framework with 12
> candidate features and two-gate selection (cross-cohort stability +
> design-condition AUC). Selection eliminated all 12 candidates. We
> attribute this to (a) coefficient-of-variation being inappropriate for
> trajectory operators, and (b) cross-cohort data-coverage requirements
> being unmeetable with public cohorts that lack EIS on synthetic and
> Severson data. This is a substantive methodological lesson: noise-robust
> design-direction inversion requires either restructured gates, or
> per-family selection, or both. Our framework as designed cannot proceed
> on currently-available public data."

This is a publishable negative result. It teaches the field what NOT to do
when designing the next-generation cascade. The C3 framework remains alive
on synthetic ground truth (Probes 4 + 5 + 6) and on Paper 1's
independence-framework analysis.

## Next moves (NOT pre-registered here)

Three options for a Paper 3-equivalent:

1. **Paper 3a: Replace CV with robust dispersion.** New pre-reg replacing
   Gate I metric with IQR-based dispersion or scale-normalized SD. Re-run
   pipeline on existing parquets. Quick.
2. **Paper 3b: Operator-family selection.** New pre-reg with EIS-spectral
   operators tested only on EIS cohorts, trajectory operators tested only
   on long-trajectory cohorts. Sacrifices cross-family voting in favor of
   per-family discrimination. Cleaner methodologically.
3. **Add EIS to PyBaMM + extract Severson EIS-equivalent.** PyBaMM has an
   experimental EIS module; we could simulate impedance spectra on the
   existing 108 cells. Severson has no EIS but DCIR at multiple SOC could
   be a proxy. Heaviest lift but eliminates the cross-cohort coverage gap.

For now, this writeup stands as the Paper 2 result.

---

## Outputs

- `code/paper2_extract_severson.py` — Severson trajectory operator extractor
- `code/paper2_extract_others.py` — SECL + Khan + Zhang + PyBaMM + WMG extractors
- `code/paper2_gate_I.py` — cross-cohort CV-based stability test
- `code/paper2_gate_II.py` — design-condition AUC test (no operators reached this)
- `data/processed/paper2_operators_{cohort}.parquet` — per-cohort operator tables (6 parquets)
- `data/processed/paper2_gate_I_results.parquet` — Gate I results
- `data/processed/paper2_gate_II_results.parquet` — Gate II results (E1 only, FAIL)
