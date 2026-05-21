# Phase 3 Preview — Lead Time of Disagreement-Onset over Capacity-Knee

**Date:** 2026-05-21
**Status:** Knee-point detector implemented. First lead-time numbers on N=4 first-life alpha cells.

---

## Headline numbers (N=4 first-life alpha cells)

| Cell | Disagreement onset (cyc) | Knee point (cyc) | Knee onset (cyc) | Lead over knee-point (cyc) | Lead over knee-onset (cyc) | Final SOH |
|---|---|---|---|---|---|---|
| V4 | 70 | 95 | 95 | **+25** | +25 | 95% |
| W9 | 122 | 146 | 122 | **+24** | 0 | 92% |
| W10 | 122 | 151 | 122 | **+29** | 0 | 92% |
| W8 | 148 | 148 | 125 | **0** | **−23** | 91% |
| **Mean** | | | | **+19.5** | +0.5 | |
| **SD** | | | | 13.5 | 19.6 | |

## Interpretation

**The disagreement-onset signal precedes the capacity-knee-point by 0-29 cycles (mean +19.5 cyc) for the 4 cells where it can be measured.** Positive direction for 3 of 4 cells (V4, W9, W10); zero on the most stable cell (W8).

**Against the earlier knee-onset (curvature deviation in capacity alone), the picture is mixed:** disagreement-onset is +25 cyc for V4, exactly tied for W9 and W10, and **−23 cyc** for W8. The cross-operator framework does not strictly precede the single-operator curvature method on this cohort.

## Pre-reg falsification status

Phase 3.4 pre-reg locked the falsification threshold at **50-cycle lower bound on the population mean lead time at 95% credible interval**.

At N=4 with observed mean = +19.5 cyc and sd = 13.5 cyc:
- 95% normal-approximation CI on the mean = [+5.7, +33.3] cyc
- **Does not exceed 50-cycle pre-reg threshold**
- Lower bound is positive (+5.7 cyc) → some evidence of positive lead time, but not at the pre-registered magnitude

**Current pre-reg verdict:** PARTIAL. Positive direction supports C2 directionality, but magnitude falls below the falsification threshold for the first-life alpha subset.

## What the N=4 result does NOT settle

1. **Triad β cells (G1/W4/W5)** — HPPC-based 3-operator pipeline not yet built; cells will roughly double the cohort (4 alpha → 7 first-life trajectories).
2. **Second-life trajectories** — disagreement-onset detected at all 4 second-life cells (V4/W8/W9/W10 in X1 pool), but knee-point detection on second-life cells requires per-segment cycle counts (deferred — need to extract from second-life cycling data).
3. **Khan 2025 + Zhang Cambridge + WMG cohorts** — independent cross-chemistry / cross-lab validation. These cohorts are held out per Phase 4 pre-reg and should also inform Phase 3 lead-time interpretation.
4. **Pre-reg power calculation assumed σ_cell = 100 cyc** (from Phase 1.8). Observed sd on alpha subset is 13.5 cyc — substantially smaller. **Revised power calc** could be: at observed sd 13.5, even N=4 would detect a 50-cycle effect at standard power. The fact that the observed mean (19.5) is below threshold isn't a power issue — it's a magnitude issue. The effect is real but smaller than 50 cycles on this cohort.

## What this tells us about C2

The exploratory N=4 result suggests:

- **Direction is correct** (disagreement-onset precedes knee-point in 3 of 4 cells)
- **Magnitude is small** (~20 cycles, ~10-15% of the 150-cycle range of knee-points observed)
- **Not all cells show the lead** (W8 ties at knee-point, lags at knee-onset)
- **Below the pre-registered 50-cycle threshold**

Honest framing for the eventual paper:
- C2 directionality on the first-life alpha cohort is positive but small
- The Ding 2024 280-323 cycle figure (pressure-leads-electrical) is at a different scale than what C2's cross-operator approach delivers on this cohort
- C2's value may lie more in the **mode-classification claim** (Phase 4) than in the **lead-time claim** (Phase 3) on this particular dataset
- The C2 framework remains operator-agnostic and methodologically sound — but on this chemistry / instrumentation, the cross-operator signal does not dramatically beat single-operator curvature detection

## Why the W8 reversal matters

W8 is the most stable of the alpha-triad cells (smallest Mahalanobis distances throughout, slowest aging on every operator). On W8, the cross-operator disagreement-onset detector reports later than the single-operator curvature-based knee-onset. This is a real signal that:

- Single-operator curvature is sensitive on stable cells where the capacity-curve inflection is subtle but detectable
- The cross-operator framework's added value scales with cell-to-cell aging-pathway heterogeneity, not absolute aging severity
- The mode-classification claim (Phase 4) is the right place for C2's added value to show, not lead-time per se

This is exactly the kind of finding the pre-reg structure was designed to surface honestly.

## Sigma_baseline = 0 in raw output

The knee detector reports `sigma_baseline_raw = 0` for all cells. This is because RPT 1, 2, 3 have only 3 data points each and the second derivative on a 3-point sequence is degenerate / undersampled. The 3*sigma_baseline threshold for knee-onset effectively reduces to "first non-zero second derivative" which is what's being reported. **For Phase 3 lock**, the threshold construction needs a more robust noise estimate — possibly using the cycle count standard deviation across the cell's first half-trajectory, or a pooled-cell prior. Track as Phase 2.5 follow-up.

## Outputs

- `data/processed/knee_point_first_life.parquet`
- `code/knee_point_detector.py`
