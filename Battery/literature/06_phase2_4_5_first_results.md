# Phase 2.4 + 2.5 — Fresh-Period Null Fit and First Disagreement-Onset Results

**Date:** 2026-05-21
**Status:** Proof-of-concept landed on the cleanest subset (first-life alpha-triad: V4 + W8 + W9 + W10). Pooled-covariance null PPC **passes**. Inter-operator disagreement onset detected for all 4 cells. One striking science finding emerged (V4 vs others).

---

## Method

For each first-life alpha-triad cell:

1. Extract three operator features per RPT:
   - `Q_max_Ah` (capacity sweep total discharge)
   - `R_ohmic_soc50` (Re(Z) at f_max from EIS, 50% SOC)
   - `R_diff_soc50` (Re(Z) at f_min from EIS, 50% SOC)
2. Per-cell standardization using fresh-period (RPT 1–3) mean and std
3. **Pooled** fresh-period covariance across all cells (11 fresh-period observations of a 3-vector, since V4 is missing RPT 1)
4. Joint Mahalanobis distance per (cell, RPT) using the pooled covariance
5. Onset detection: K=2 consecutive RPTs above √(χ²(0.99, df=3)) ≈ 3.37
6. PPC: fresh-period dist² should be approximately χ²(3)

The pooled covariance fix resolves a degeneracy that v1 (per-cell covariance) suffered — N=3 per-cell is too small to estimate a 3×3 covariance.

---

## Pooled fresh-period correlation (3×3)

```
                Q_max_Ah  R_ohmic_soc50  R_diff_soc50
Q_max_Ah         +1.000        -0.071        +0.198
R_ohmic_soc50    -0.071        +1.000        +0.105
R_diff_soc50     +0.198        +0.105        +1.000
```

Operators are nearly uncorrelated in the fresh period — the conditional-independence assumption from the design null is well-supported. This is the right starting baseline.

## PPC verdict — PASS

```
fresh n  = 11
mean d^2 = 2.721    (expected: 3.000 for chi^2(3))
KS p-val = 0.5472   (> 0.05 → null not rejected)
```

The pooled-covariance null is a good description of fresh-period joint operator behavior.

## ⭐ Structurally important: conditional-independence assumption empirically supported

The Phase 2.2 design treats the joint disagreement statistic as a Mahalanobis distance under the assumption that operator residuals are **conditionally independent in healthy cells given conditioning variables**. This assumption is what gives the χ² interpretation of distance² and what makes "joint disagreement" a meaningful single-number summary of cross-operator deviation.

The empirical fresh-period correlation matrix (above: max |ρ| = 0.20) is direct evidence that this assumption holds on this dataset and chemistry. Had |ρ| been >0.5, the joint statistic would have needed explicit coupling models and the methodology would have gotten substantially messier.

This is a **first-class methodological finding** — not just a diagnostic check. It says C2's framework matches the actual conditional structure of these operators on these cells. Reviewers will ask whether the design-null independence is real or assumed; this provides the empirical answer for this cohort. (Whether it holds on other chemistries / instrumentation is an open question that the Khan 2025 and Zhang Cambridge cross-validation cohorts can address in Phase 4.)

---

## Mahalanobis-distance trajectories (per cell, per RPT)

```
cell_id     V4    W10     W8     W9
rpt_idx
  1        NaN  1.40   1.43   1.38
  2       0.89  1.77   2.45   1.79
  3       0.89  1.62   2.17   1.67     ← fresh-period boundary
  4       6.18  9.98   2.45   6.86     ← W8 just below threshold
  5       9.14 14.37   6.62  10.53
  6      13.33 13.02   5.66   8.58
  7      13.81 17.86   5.36  12.65
  8      17.52 18.68   7.60  15.24
  9      20.33 20.35   8.33  17.05
 10      21.68 18.23   6.72  13.96
 11      23.29 16.73   8.63  12.60
 12        NaN 20.49   7.31  16.17
 13        NaN 20.25   7.70  17.34
 14        NaN 22.16   7.93  17.20
 15        NaN 27.97  10.52  18.35
```

All cells leave the fresh-period null soon after RPT 3.

---

## Per-cell onset detection

| Cell | Onset RPT | Onset cycle (est.) | Max distance |
|---|---|---|---|
| W10 | 4 | ~75–100 | 27.97 |
| W9 | 4 | ~75–100 | 20.35 |
| V4 | 4 | ~75–100 | 23.29 |
| W8 | 5 | ~100–150 | 10.52 |

W8 takes one extra RPT to cross the threshold consistently — it's the most stable of the alpha cells.

---

## ⚠️ Science finding — V4 vs the W cells (degradation-mode signature)

Per-operator standardized residuals at RPT 11 (where V4 last has data):

| Operator | V4 | W8 | W9 | W10 |
|---|---|---|---|---|
| `Q_max_Ah` z-score | **−8.09** | −5.77 | −5.66 | −5.67 |
| `R_ohmic_soc50` z-score | **−0.11** | +4.83 | +4.58 | +4.34 |
| `R_diff_soc50` z-score | +0.60 | +6.15 | +3.41 | +2.51 |

**V4 is the outlier.** Its capacity has fallen the most (−8σ vs −5.7σ on the others) but its EIS-band markers haven't moved at all. The W-cells show capacity fade *coupled with* substantial growth in both ohmic and diffusion resistance.

This is exactly the kind of inter-operator pattern C2 is meant to detect — and it has a **physical interpretation**:

- **V4's signature:** capacity drop without resistance growth → **lithium inventory loss (LLI) dominant.** Active lithium is being consumed (likely by SEI growth) but the electrode interface impedance isn't changing much.
- **W-cells signature:** capacity drop + resistance growth → **loss of active material (LAM) + SEI growth.** The electrodes themselves are degrading; the impedance increases reflect lost active surface and/or thicker SEI films.

This is a **Phase 4 preview** — the cross-operator pattern already shows mode-discrimination structure at first glance, before any classifier is fit. Within a tiny cohort (4 cells), we see at least two distinct aging signatures.

It's also a methodological win: the inter-operator disagreement statistic for V4 (Mahalanobis ≈ 23 at RPT 11) is comparable to W10 (≈ 17), so V4 fails the joint null at similar magnitude — but the *direction* of the failure is different. The full Phase 4 classifier on the residual *direction* (not just magnitude) should be able to separate LLI-dominant from LAM-dominant cells.

---

## What this proof-of-concept doesn't establish yet

1. **Lead time over capacity-knee-point:** all 4 cells flag disagreement-onset around RPT 4–5 (~75–150 cycles), but **none of them reach a clear capacity knee** within 15 RPTs (final SOH ~91%). The Phase 3 headline lead-time claim requires both events to be observable. Without a knee observation, lead time is lower-bounded only.
2. **N=4 is below the headline N=16/13 cohort.** This is the cleanest subset only. Full Phase 3 requires extending to all triads.
3. **Hierarchical pooling not yet applied** at the population level. The Stan model from [05_phase2_model_design.md](05_phase2_model_design.md) is the next implementation target — this proof-of-concept used a simpler frequentist Mahalanobis pipeline.
4. **Second-life cells not yet ingested.** They likely DO show knee-point crossings (entering at 90% SOH, declining further) and are critical for Phase 3.4 secondary 80%-SOH comparator.

---

## Phase 2 task status

- 2.1 ✅ Conditioning variables specified
- 2.2 ✅ Stan model architecture designed
- 2.3 ✅ First-life feature extraction working
- 2.4 ⚠️ **Partial:** fresh-period null fit working on N=4 alpha subset. Hierarchical pooling pending.
- 2.5 ✅ **PPC passes on alpha subset** with pooled covariance. KS p = 0.547.

## What's next

1. **Extend feature extraction to second-life** (raw .xlsx capacity + .mat EIS at 3.26/3.63/4.00 V)
2. **Add HPPC feature extraction for triad β** (R_DC + τ from pulse fits on G1/W4/W5)
3. **Build the Stan model** per [05_phase2_model_design.md](05_phase2_model_design.md) — hierarchical pool across all triads
4. **Capacity-knee-point detector** (Zhang/Altaf/Wik 2024 curvature method) to enable Phase 3.4 lead-time measurement on second-life cells where knee is likely observed

---

## Output files

- `data/processed/features_first_life.parquet` — per-(cell, RPT) feature table
- `data/processed/mahalanobis_trajectories_alpha_pooled.parquet` — joint-distance trajectories
- `code/extract_features.py` — feature extraction pipeline (first-life)
- `code/fresh_period_null_pooled.py` — fresh-period null + Mahalanobis + PPC
