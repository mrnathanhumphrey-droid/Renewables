# Phase C3 Probe 6 Pre-Registration — Synthetic Noise Injection (Real-Cell-Noise Threshold Test)

**Date locked:** 2026-05-21
**Locked before:** any noise-injection analysis is run on Probe 5's PyBaMM trajectories.
**Relation to prior pre-regs:** Independent. Bonferroni fresh.

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. Motivation

Probe 5 (literature/24) disconfirmed the magnitude-confound hypothesis. Under
uniform aging extent on PyBaMM synthetic data, all 3 design parameters PASS
PERMANOVA — including particle radius which was NULL in Probe 4. Synthetic
data with uniform anchoring shows STRONGER design-direction signal than with
varied anchoring.

Yet Severson Batch 2 (real cells, uniform 80% SOH aging, balanced bins, n=43)
fails within-batch PERMANOVA across multiple design axes. The cause must
therefore come from sources that PyBaMM synthetic doesn't reproduce.

Candidates listed in literature/24 §Implications:
1. Measurement noise (V/I sensor noise on real cells)
2. Calendar/storage variation between cycles
3. Real chemistry heterogeneity (electrode binder, particle distribution, etc.)
4. Batch-to-batch chemistry shifts

This probe tests **whether (1) alone — measurement noise injected onto otherwise-
clean synthetic operators — is sufficient to reproduce a Severson-Batch-2-like
collapse of the design-direction PERMANOVA.**

If yes: real-cell noise is the operative variable. We can predict the noise
threshold at which the framework breaks and design experimental protocols
to stay above that threshold.

If no: noise alone isn't the explanation. Other sources (chemistry
heterogeneity, calendar variation, batch effects) are required to reproduce
Severson's null.

## 1. Hypotheses

**H7-primary:** At noise levels matching documented real-cell instrument noise
on the operator triad (Level 2 in §3 below: ~0.5% relative noise on Q_max, ~15%
on R_DC, ~20% on R_total), the per-parameter PERMANOVAs from Probe 5 collapse
to ≤1 of 3 parameters PASSING.

**H7-null:** Even at Level 2 noise, 2+ parameters PASS. Real-cell noise alone
is NOT sufficient to explain Severson's within-batch null.

**H7-secondary (calibration curve):** Run the PERMANOVA at noise levels {0, 1,
2, 3, 4} and report the curve of "params PASSING vs noise magnitude" as
descriptive output.

## 2. Data source (LOCKED)

`data/processed/pybamm_l9_trajectories.parquet` from Probe 5 sweep
(commit `dda4bdc`). 105 valid cells (anchor at uniform per-cell SOH 0.92).

No new PyBaMM simulations needed. This is purely a post-hoc noise injection
on existing operator values.

## 3. Noise model (LOCKED)

Multiplicative Gaussian noise on each operator at each RPT cycle, applied
INDEPENDENTLY to fresh-reference and aged-anchor values per cell.

```
Q_obs    = Q_true    * (1 + ε_Q),    ε_Q    ~ N(0, σ_Q)
R_DC_obs = R_DC_true * (1 + ε_R_DC), ε_R_DC ~ N(0, σ_R_DC)
R_tot_obs = R_tot_true * (1 + ε_R_t),  ε_R_t ~ N(0, σ_R_t)
```

**Five pre-registered noise levels:**

| Level | σ_Q | σ_R_DC | σ_R_total | Interpretation |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | Baseline (= Probe 5 result) |
| 1 | 0.001 (0.1%) | 0.05 (5%) | 0.10 (10%) | Best-in-class lab cycler instrument |
| 2 | 0.005 (0.5%) | 0.15 (15%) | 0.20 (20%) | Typical academic-lab real-cell noise |
| 3 | 0.010 (1.0%) | 0.30 (30%) | 0.30 (30%) | Noisy field-cycler / harsh-environment data |
| 4 | 0.020 (2.0%) | 0.50 (50%) | 0.50 (50%) | Instrument-issue / sparse-RPT real cells |

Level 2 magnitudes are derived from literature on EIS / DCIR measurement
uncertainty in academic battery labs (Stanford SECL, NREL, Imperial College).
This is the primary test point.

**Random seed for noise:** per-cell, per-noise-level. Seed = `2000 + level * 10000 + cond_idx * 100 + cell_idx`. Reproducible.

Noise is applied to BOTH fresh-reference values and aged-anchor values per
cell. Per-cell standardization is then recomputed from the pooled noisy
fresh-reference values. This mirrors what would happen in real-cell extraction:
the experimenter doesn't know the "true" fresh value, only the noisy measurement.

## 4. Primary test (LOCKED)

Per noise level, three per-parameter PERMANOVAs (one per design parameter),
identical specification to Probe 4/5 §4-5:

- PERMANOVA(u_i | cathode_thickness)
- PERMANOVA(u_i | transference_number)
- PERMANOVA(u_i | particle_radius)

Cosine-distance PERMANOVA, 10000 permutations per test.

**Bonferroni:** within each noise level, α = 0.05 / 3 = 0.0167.

**Across noise levels:** descriptive. The calibration curve IS the result.
Levels are not Bonferroni-corrected against each other; they are independent
calibration points.

**Effect-size floor:** pseudo-F > 3.0.

## 5. Falsification thresholds (LOCKED)

Per-level verdicts (within each noise level):

- **LEVEL ROBUST:** ≥2 params PASS (p < 0.0167 AND F > 3.0)
- **LEVEL WEAK:** exactly 1 param PASS, others ≤ WEAK PASS
- **LEVEL COLLAPSED:** 0 params PASS

**H7 verdicts:**

- **H7 SUPPORTS NOISE EXPLANATION:** Level 2 is LEVEL COLLAPSED or LEVEL WEAK.
  Real-cell noise alone is sufficient to reproduce Severson-like null.
- **H7 REJECTS NOISE EXPLANATION:** Level 2 is LEVEL ROBUST. Noise alone is
  NOT sufficient; other real-cell variability sources (chemistry heterogeneity,
  calendar variation, batch effects) are required.
- **H7 BORDERLINE:** Level 2 outcome ambiguous (e.g., 2 PASS but pseudo-F
  collapses below floor at Level 3).
- **H7 INVALID:** Probe 5 parquet missing or contains <90 valid cells.

## 6. What this probe CAN and CANNOT conclude

CAN:
- Identify the approximate real-cell-noise threshold at which the C3 framework
  breaks
- Distinguish "noise is the operative variable" from "noise is not sufficient"
- Predict whether Severson-like nulls can be avoided by better instrumentation
  alone

CANNOT:
- Quantify the role of chemistry heterogeneity, calendar variation, or
  batch-to-batch shifts (these are not modeled)
- Validate the noise model parameters against any specific real-cell dataset
  (these are literature-derived plausible levels)
- Conclude anything about real-cell experiments at lower or higher than these
  noise levels (only the 5 pre-registered points)

## 7. Compute estimate

Pure post-hoc analysis on existing parquet. No PyBaMM, no Modal. Local Python
on the 9950X3D, expected runtime ~3 minutes for 5 levels × 3 tests × 10000
permutations = 150,000 PERMANOVA evaluations.

## 8. Operational protocol (LOCKED execution order)

1. Commit this pre-reg + push to remote. Lock is the commit timestamp.
2. Implement `code/c3_noise_injection.py`:
   - Read `data/processed/pybamm_l9_trajectories.parquet`
   - For each cell, recompute fresh + uniform-anchor operators (per Probe 5
     pipeline with target SOH 0.92)
   - For each of 5 noise levels, inject multiplicative Gaussian noise per §3
   - Standardize using NOISY fresh-pool SD; unit-normalize
   - Run 3 per-parameter PERMANOVAs per noise level
   - Apply LEVEL and H7 verdicts per §5
3. Write up in `literature/26_c3_noise_injection_result.md` regardless of
   direction.

## 9. Explicitly NOT covered

- Calendar / storage variation injection — would require modeling
  measurement-to-measurement temperature drift; out of scope
- Chemistry heterogeneity (cathode binder, particle distribution) — would
  require new PyBaMM runs with varied chemistry parameters
- Batch-to-batch shifts — would require multi-batch synthetic
- Noise correlation between operators — assumed independent; cross-operator
  correlated noise is a follow-up
- Non-Gaussian noise (e.g., systematic drift, calibration jumps) — Gaussian
  only

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
