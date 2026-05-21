# Phase 2.4 (extended) — Combined First-Life + Second-Life Mahalanobis

**Date:** 2026-05-21
**Status:** Combined pipeline runs on 10 alpha-or-gamma trajectories. PPC formally passes but reveals a **fresh-period definition problem** that the first-life-only analysis didn't expose.

---

## Trajectories included (N=10 for alpha-or-gamma)

| Trajectory | Lifecycle | RPTs with all 3 operators | Fresh window used |
|---|---|---|---|
| V4_first_life | first | 10 (RPTs 2-11) | 2-3 |
| W8_first_life | first | 15 (RPTs 1-15) | 1-3 |
| W9_first_life | first | 15 | 1-3 |
| W10_first_life | first | 15 | 1-3 |
| G1_second_life | second | 4 (RPTs 5-8) | 5-7 |
| V4_second_life | second | 4 | 5-7 |
| V5_second_life | second | 4 | 5-7 |
| W8_second_life | second | 4 | 5-7 |
| W9_second_life | second | 4 | 5-7 |
| W10_second_life | second | 4 | 5-7 |

Triad-β cells (G1/W4/W5 with HPPC instead of EIS) and triad-α cells without full coverage are not yet included.

---

## Combined PPC

```
fresh n=29, mean d^2=2.884, KS p=0.4654   → PASS
```

By the formal PPC, the pooled fresh-period covariance fits the joint distribution.

## ⚠️ Problem hidden in PPC: fresh-period correlations are anomalous

Pooled fresh-period operator correlations on the combined cohort:

| | Q_max | R_ohmic | R_diff |
|---|---|---|---|
| **Q_max** | +1.000 | **−0.895** | **−0.928** |
| **R_ohmic** | −0.895 | +1.000 | +0.984 |
| **R_diff** | −0.928 | +0.984 | +1.000 |

Compare to the **first-life-only** fresh-period correlations:

| | Q_max | R_ohmic | R_diff |
|---|---|---|---|
| **Q_max** | +1.000 | -0.071 | +0.198 |
| **R_ohmic** | -0.071 | +1.000 | +0.105 |
| **R_diff** | +0.198 | +0.105 | +1.000 |

First-life cells in their first 3 RPTs are essentially uncorrelated across operators — consistent with the "design null" of conditionally-independent operators in healthy cells.

Second-life cells in their first EIS-bearing RPTs (5-7) are **not truly fresh** — they enter second-life at ~90% SOH and have undergone full first-life aging. Treating RPTs 5-7 of second-life as the "fresh reference" pulls aging-induced cross-operator correlations into the null model. The Mahalanobis distance then becomes a measurement of deviation from a *partly-aged covariance structure*, not from a healthy-baseline structure.

This is a methodological problem. The PPC passes because the fresh-period observations are self-consistent within the pooled cov — but the cov itself encodes aging structure, not the design null.

---

## Mahalanobis distance trajectories

```
trajectory       RPT:   1     2     3     4     5     6     7     8     9    10    11    12    13    14    15
W8_first_life          1.47  2.65  2.27  2.42  6.74  6.64  5.52  7.66  8.33  7.06 11.31  7.92  7.98  8.49 10.82
W9_first_life          1.45  2.90  2.51  7.73 11.45  9.57 14.75 17.50 20.16 16.03 14.18 18.90 20.32 19.77 20.78
W10_first_life         1.52  2.88  2.36 12.62 17.23 16.25 22.47 22.31 24.81 22.14 19.67 24.71 24.18 26.59 36.37
V4_first_life           -   0.88  0.88  6.53  9.98 13.95 14.72 18.53 21.44 22.87 24.60   -     -     -     -
G1_second_life           -     -     -     -   1.55  1.57  1.41  7.02   -     -     -     -     -     -     -
V4_second_life           -     -     -     -   1.15  1.00  1.42  7.44   -     -     -     -     -     -     -
V5_second_life           -     -     -     -   1.63  1.73  1.41  7.32   -     -     -     -     -     -     -
W8_second_life           -     -     -     -   1.67  1.81  1.41  7.48   -     -     -     -     -     -     -
W9_second_life           -     -     -     -   1.12  0.96  1.42  7.26   -     -     -     -     -     -     -
W10_second_life          -     -     -     -   0.98  0.82  1.43  6.87   -     -     -     -     -     -     -
```

Two distinct patterns:

**First-life cells:** clear monotonic excursion from fresh-period baseline. Onsets at RPT 4-5. Distances grow to 10-36 by end of trajectory.

**Second-life cells:** quiet at RPTs 5-7 (all distances ~1.0-1.8), then **synchronized jump to ~7 at RPT 8 across all 6 cells**. None crosses the K=2 consecutive-RPT threshold within the available 4-RPT window.

## The RPT-8 synchronized jump — three possible explanations

1. **Real aging event.** Cells underwent an interim shared physical process between RPTs 7 and 8 (cycling segment 7→8 in calendar terms is May 22 → June 18 2023, ~25 days). This is the most scientifically interesting interpretation but unverifiable without more RPT data.
2. **Methodological artifact from short fresh window.** With only 3 RPTs of fresh data per trajectory and only 6 trajectories pooled (18 fresh obs total per lifecycle), the second-life fresh covariance is noise-dominated. Any deviation looks large.
3. **Instrument/calibration shift at RPT 8.** Common in long EIS campaigns; would show as constant offset across all cells, which is what we see.

Distinguishing requires EIS data from RPTs 9-19 of second-life. If the elevated distance persists, hypothesis 1. If it returns to baseline, hypothesis 3. Currently the EIS extraction is blocked on the per-cell `.DTA` folder parser for RPTs 9-19.

---

## Onset detection summary

| Trajectory | Onset RPT | Reason for no detection |
|---|---|---|
| V4_first_life | 4 | — |
| W8_first_life | 5 | — |
| W9_first_life | 4 | — |
| W10_first_life | 4 | — |
| G1_second_life | none | trajectory ends at RPT 8 (only 4 EIS RPTs total) |
| V4_second_life | none | same |
| V5_second_life | none | same |
| W8_second_life | none | same |
| W9_second_life | none | same |
| W10_second_life | none | same |

**Onset detection on second-life cohort is impossible with current EIS coverage.**

---

## What this changes

1. **The combined pipeline's first attempt has a fresh-period definition problem.** The honest fix is one of:
   - **Option X1:** Use first-life RPTs 1-3 as the fresh reference *for the same cells across both lifecycles*. V4/W8/W9/W10/G1 are the same physical cells; their truly-fresh state is first-life RPT 1-3.
   - **Option X2:** Treat each lifecycle as a separate experiment; never pool covariance across lifecycle stages.
   - **Option X3:** Use the Khan 2025 cohort's fresh-period EIS as a population-level "fresh manifold" reference, with cell-specific shifts allowed.
2. **Second-life EIS coverage at RPTs 5-8 only is insufficient** for onset detection. Per-cell `.DTA` folder parser for RPTs 9-19 is now a blocking prerequisite for any Phase 3 second-life lead-time analysis.
3. **First-life-only Phase 2.4 results (from `06_phase2_4_5_first_results.md`) remain the cleanest available signal**. Recommendation: treat that as the primary Phase 2 validation result; combined cohort as a secondary stress test with documented limitations.
4. **The RPT-8 synchronized jump is a flag worth investigating** but cannot be interpreted with current data.

---

## Phase 2 task status update

- 2.4 ⚠️ Combined-cohort proof-of-concept ran, but fresh-period definition for cross-lifecycle pooling needs revision (Options X1/X2/X3 above).
- **Next-push priorities:**
  1. Implement second-life EIS extractor for RPTs 9-19 from per-cell `.DTA` folders (.DTA is plain-text format; parser is straightforward)
  2. Re-run combined pipeline with Option X1 (per-cell fresh = first-life RPT 1-3 of same cell)
  3. Build capacity-knee-point detector (Zhang/Altaf/Wik 2024 curvature method)
  4. Start Stan hierarchical model

## Output files

- `data/processed/features_combined.parquet`
- `data/processed/mahalanobis_combined.parquet`
- `code/combine_and_run.py`
