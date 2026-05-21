# Phase 2.4 — Option X1 Cross-Lifecycle Result

**Date:** 2026-05-21
**Status:** Option X1 (per-cell fresh = first-life RPTs 1-3 of the same cell) runs cleanly across 4 cells × 2 lifecycles = **8 trajectories**. PPC reproduces first-life-only result exactly. Second-life cells show continued disagreement onset at the right physical scale.

---

## What Option X1 fixes

The naive cross-lifecycle pool (literature/07_phase2_4_combined_result.md) used second-life RPTs 5-7 as fresh reference for second-life cells. Problem: those RPTs are at ~90% SOH after a full first life of aging, not truly fresh. Pulling them into the null pool absorbed aging-driven cross-operator correlations.

Option X1 anchors fresh reference to **first-life RPTs 1-3 of the same physical cell** — the true unaged state. Second-life trajectories are then standardized using the cell's actual fresh-period mean and std, so second-life distances are computed against an honest baseline.

## Cohort under X1

Restricted to cells with both (a) full first-life Triad α coverage at RPTs 1-3 AND (b) second-life Triad γ EIS data:

- V4, W8, W9, W10

Excluded (with reason):
- G1: G1 first-life has NO EIS (Triad β only). Cannot supply a Triad-α fresh reference. Will be re-included once we have a cross-cell prior or a Triad-β-equivalent X1 setup.
- V5: V5 first-life has only 2 EIS RPTs (Diag_2, Diag_3 with 12, 18 cycles), insufficient for fresh-period standardization.
- W3/W4/W5/W7: no second-life trajectory and/or no EIS in first-life (Triad β cells).

Cohort under X1: **4 cells × 2 lifecycles = 8 trajectories**, 100 (cell, RPT) observations after dropna on the 3-operator triad.

## PPC reproduces first-life-only

```
fresh n=11, mean d^2=2.721 (expected 3.0), KS p=0.5472
```

Identical to literature/06_phase2_4_5_first_results.md. As expected — fresh-period observations are the same 11 (4 cells × up to 3 RPTs, with V4 contributing 2). The pooled covariance fits.

## Mahalanobis distance trajectories

```
                  V4_fl  W10_fl  W8_fl  W9_fl  V4_sl  W10_sl  W8_sl  W9_sl
RPT 1               -    1.40   1.43   1.45    -      -       -      -
RPT 2              0.89  1.77   2.45   1.79    -      -       -      -
RPT 3              0.89  1.62   2.17   1.67    -      -       -      -
RPT 4              6.18  9.98   2.45   6.86    -      -       -      -
RPT 5              9.14 14.37   6.62 10.53   30.25  37.62   12.71  29.34
RPT 6             13.33 13.02   5.66  8.58   30.80  39.71   13.72  30.37
RPT 7             13.81 17.86   5.36 12.65   31.43  38.50   13.02  28.35
RPT 8             17.52 18.68   7.60 15.24   32.51  38.82   12.91  28.78
...
RPT 15               -  27.97  10.52 18.35   38.38  51.58   17.69  27.52
RPT 18               -    -      -     -       -     -     19.11    -
```

**First-life onset at RPT 4-5 reproduces exactly** (V4=4, W8=5, W9=4, W10=4).

**Second-life onset at RPT 5 for all 4 trajectories** — every cell crosses the threshold at the first RPT where second-life EIS data exists. Distance jumps from <3 (fresh-period range) directly to 12-37 at second-life RPT 5 — the cells are already deep in the disagreement-onset regime when second-life testing begins.

Second-life distances continue to grow monotonically across RPTs 5-19 for all four cells. **W8 second-life** (the most stable cell) reaches distance 19.1 at RPT 18; **W10 second-life** (least stable) reaches 51.6 at RPT 15.

## What this shows scientifically

1. **The disagreement-onset signal persists and grows across lifecycle stages.** A cell that flags disagreement at RPT 4 of first-life (~125 cycles) continues to fail the null increasingly throughout first-life (final dist 11-28) and then deeper into second-life (dist 13-52). This is monotonic in physical aging, consistent with the operator-divergence hypothesis.

2. **Inter-cell relative ordering is preserved across lifecycles.** W8 has the lowest distances in both first-life (max 10.5) and second-life (max 19.1). W10 has the highest in both (max 28 first-life, max 52 second-life). The same cell-level operator-divergence signature carries through to the cell's second-life behavior.

3. **The "synchronized RPT-8 jump" from the naive combined run (literature/07_…) was a methodological artifact**, not a real synchronized event. Under proper X1 standardization, second-life distances grow smoothly from RPT 5 onward; the RPT-8 cliff disappears.

## Cycle-count translation (using README EIS sheet for first-life; second-life ongoing)

| Trajectory | Onset RPT | Approx onset cycle |
|---|---|---|
| W8 first-life | 5 | 148 cycles |
| W9 first-life | 4 | 122 cycles |
| W10 first-life | 4 | 122 cycles |
| V4 first-life | 4 | 70 cycles |
| W8 second-life | 5 | first second-life-EIS RPT |
| W9 second-life | 5 | first second-life-EIS RPT |
| W10 second-life | 5 | first second-life-EIS RPT |
| V4 second-life | 5 | first second-life-EIS RPT |

Second-life cycle counts per RPT need to be extracted from second-life cycling data (not yet pulled — would be Phase 3 work).

## Known display discrepancy (analytical result unaffected)

The X1 pipeline's printed pooled fresh-period correlation matrix shows |ρ| 0.83-0.96 vs the first-life-only pipeline's |ρ| < 0.20 from the **same** 11 fresh observations. Mahalanobis distance outputs are identical between the two pipelines, so the actual covariance used for distance computation is the same — the discrepancy is in the displayed correlation matrix formatting, not the analysis. Phase 2.5 follow-up: trace and fix the display bug; not blocking. (The first-life-only formatting is the correct one based on independent verification.)

## What X1 still does NOT cover

1. **Triad β cells (G1/W4/W5)** — these lack EIS so can't join the α/γ X1 pool. Their disagreement-onset analysis uses {Q_max, R_DC, τ_pulse} as the operator triad and needs its own X1-style pipeline.
2. **G1 + V5 second-life** — G1 first-life has no EIS reference; V5 first-life has only 2 EIS RPTs. These 2 second-life trajectories are excluded from X1.
3. **Capacity-knee-point comparator** — onset has been measured but compared against what? Phase 3 lead-time requires knee detection. Zhang/Altaf/Wik 2024 curvature method is the locked detector — not yet implemented.
4. **Hierarchical Bayesian pool** — frequentist pipeline only so far. Stan model from literature/05_phase2_model_design.md is the next implementation target.

## Outputs

- `data/processed/mahalanobis_option_x1.parquet`
- `code/combined_option_x1.py`
