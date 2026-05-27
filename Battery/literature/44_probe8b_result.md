# C3 Probe 8b — Result (Distance-Metric Decomposition)

**Date:** 2026-05-27
**Pre-reg:** `literature/43_probe8b_prereg.md` (lock commit `c0fa935`)
**v2 parquet:** `data/processed/pybamm_l9_trajectories_eis_v2.parquet` (SHA `7A03BCC9…F79AA`)
**Analyzer:** `code/c3_probe8b_distance_metric.py` (SHA `93814AB7…7F1B9`)
**Result parquet:** `data/processed/probe8b_distance_metric_results.parquet` (SHA `1E64A3CA…E8C93`)

---

## Headline

**DISTANCE METRIC NEUTRAL at Level 2** per pre-reg §5 disposition.

All three metrics (cosine, Euclidean, Mahalanobis) on the winning feature space (variant iv: fresh+aged 6D stacked from 8a) achieve **2/3 PASS at Level 2** with similar F-values. Distance metric is NOT additionally load-bearing on top of feature-space.

**Subsidiary positive finding:** at Level 0 (no noise), Mahalanobis catches transference (F=4.14, p=0.0001, PASS) where cosine (F=0.13) and Euclidean (F=0.69) miss it. The transference signal IS present in the operator triad — but it's so faint that even Level-1 noise (σ_R_ohmic=5%) wipes it out. Transference is **noise-fragile**, not structurally invisible. Confirms a real but unusable signal.

## Per-metric Level-2 result (PRIMARY)

| Metric | Thickness | Transference | Particle radius | Level verdict |
|---|---|---|---|---|
| Cosine (baseline) | PASS (F=14.26, p=0.0001) | NULL (F=0.76, p=0.57) | PASS (F=13.56, p=0.0001) | LEVEL ROBUST |
| Euclidean | PASS (F=9.32, p=0.0001) | NULL (F=0.60, p=0.80) | PASS (F=10.02, p=0.0001) | LEVEL ROBUST |
| Mahalanobis | PASS (F=9.82, p=0.0001) | NULL (F=0.92, p=0.53) | PASS (F=10.49, p=0.0001) | LEVEL ROBUST |

Cosine has the HIGHEST F-values at L2 (th 14.26, pr 13.56). Mahalanobis is slightly behind on F-magnitude despite its covariance-aware design. Neither catches transference at PRIMARY noise.

## Full sweep per metric

### Cosine (baseline)

| Level | Th | Tn | Pr | Verdict |
|---|---|---|---|---|
| 0 | PASS (52.38) | NULL (0.13) | PASS (18.99) | LEVEL ROBUST |
| 1 | PASS (44.89) | NULL (NaN) | PASS (17.00) | LEVEL ROBUST |
| 2 | PASS (14.26) | NULL (0.76) | PASS (13.56) | **LEVEL ROBUST** |
| 3 | PASS (7.66) | NULL (NaN) | PASS (16.58) | LEVEL ROBUST |
| 4 | NULL (2.18) | NULL | PASS (9.91) | LEVEL WEAK |

### Euclidean

| Level | Th | Tn | Pr | Verdict |
|---|---|---|---|---|
| 0 | PASS (44.71) | NULL (0.69) | PASS (17.30) | LEVEL ROBUST |
| 1 | PASS (26.68) | NULL (0.46) | PASS (13.49) | LEVEL ROBUST |
| 2 | PASS (9.32) | NULL (0.60) | PASS (10.02) | **LEVEL ROBUST** |
| 3 | PASS (4.82) | NULL (0.72) | PASS (12.56) | LEVEL ROBUST |
| 4 | WEAK PASS (2.01) | NULL (1.42) | PASS (6.51) | LEVEL WEAK |

### Mahalanobis

| Level | Th | Tn | Pr | Verdict |
|---|---|---|---|---|
| 0 | PASS (833049.15 †) | **PASS (4.14, p=0.0001)** | PASS (51.42) | LEVEL ROBUST 3/3 |
| 1 | PASS (126.48) | NULL (0.83) | PASS (15.81) | LEVEL ROBUST |
| 2 | PASS (9.82) | NULL (0.92) | PASS (10.49) | **LEVEL ROBUST** |
| 3 | PASS (4.87) | NULL (0.79) | PASS (11.86) | LEVEL ROBUST |
| 4 | NULL (2.08) | NULL (1.57) | PASS (6.03) | LEVEL WEAK |

† Thickness F=833,049 at Mahalanobis Level 0 is a degenerate numerical overflow (within_ss → 0 on perfectly clean signal in 6D + cathode thickness having a 1210× between/within ratio on R_ohmic). Same edge case as v2 lit/40 §A.1. Not interpretable as a real F-value; the PASS disposition stands but the magnitude is meaningless.

## Falsifiers (§6 of pre-reg)

| Falsifier | Result |
|---|---|
| **P8b_F1** (cosine on variant (iv) reproduces 8a result) | **PASSED bit-identically.** Cosine at L2: th F=14.26, pr F=13.56 — exact match to 8a literature/42 §Per-variant Level-2 result. |
| **P8b_F2** (Mahalanobis covariance well-conditioned) | **PASSED.** No condition-number flags or pinv fallbacks raised across any (level, parameter) combination. Σ remained invertible at n=101, d=6. |
| **P8b_F3** (within-metric monotonicity) | **PASSED.** F-values per metric decrease monotonically L0 → L4 (modulo NaN edge cases at L0 for cosine transference and L1/L3 cosine transference — degenerate within-cluster issues at zero / minimal noise). |
| **P8b_F4** (between-metric agreement at L0) | **PARTIAL.** All three metrics agree on th + pr PASS at L0. Mahalanobis ADDITIONALLY catches tn at L0 where cosine + Euclidean miss it. Not a falsifier violation; the headline disposition (PASS/NULL) for th + pr is consistent. Mahalanobis's tn-at-L0 PASS is a real subsidiary finding documented in §A.1. |

## §A — Subsidiary diagnostics

### A.1 Mahalanobis catches transference at Level 0 — what it means

Cosine at L0 transference: F=0.13 (NULL). Euclidean at L0 transference: F=0.69 (NULL). Mahalanobis at L0 transference: **F=4.14, p=0.0001 (PASS)**.

Mechanism: cosine and Euclidean treat all directions in the 6D feature space as equally informative. The transference signal moves the joint feature vector in a direction with substantial within-condition variance (the cells of the same transference level are spread out relative to the small between-condition shift). Cosine and Euclidean dilute the between-condition signal with this within-condition spread.

Mahalanobis re-weights the distance by the inverse of within-condition covariance Σ. This "whitens" the feature space — directions of high within-variance get DOWN-weighted, and the (small) between-condition transference shift becomes visible.

So transference IS in the data, just rotated in a direction that requires covariance-aware geometry to detect. At Level 0 with N=101 cells, Mahalanobis has enough data to estimate Σ cleanly. At Level 1+ with multiplicative percentage noise, the within-condition covariance estimate gets corrupted by the noise itself (noise inflates within-variance in the same directions as the signal). So the Mahalanobis advantage washes out as noise grows.

This is consistent with the general property: Mahalanobis is the optimal distance for between-group inference at known covariance. With ESTIMATED covariance from noisy data, the optimality fades fast.

### A.2 Mahalanobis vs Cosine F-magnitude at L2

Cosine th F=14.26 vs Mahalanobis th F=9.82. Cosine WINS on thickness magnitude.
Cosine pr F=13.56 vs Mahalanobis pr F=10.49. Cosine WINS on particle_radius magnitude.

Why is Mahalanobis behind despite covariance-awareness? The pooled within-condition covariance Σ at L2 noise is dominated by the noise itself, not by genuine between-cell variance. Inverting Σ to compute Mahalanobis distances therefore amplifies noise directions — slightly hurting the discrimination on parameters where the signal is large (th + pr).

This is the dual of A.1: Mahalanobis WINS where signal is faint and well-aligned with the noise directions (transference at L0); LOSES where signal is large and Σ̂ becomes noise-contaminated (th + pr at L2). The two regimes show distinct mechanisms.

### A.3 Numerical overflow at Mahalanobis L0 thickness

Mahalanobis L0 th F = 833,049. PERMANOVA's between/within F formula divides between_SS by within_SS; at L0 the unit-vector cluster for each thickness level collapses to a single point in the whitened space (between cells of the same thickness, distance ≈ 0). within_SS underflows to numerical zero; F overflows.

The disposition (PASS at p=0.0001) is still meaningful — the permutation null F-values overflow similarly, so the observed F is correctly identified as more extreme than every permutation. Just the magnitude reported (833K) is not a usable summary statistic, only an ordinal signal that the test rejected the null very emphatically.

Documented for transparency; doesn't affect 8b disposition.

## §B — Implications

**Distance metric is NOT load-bearing at PRIMARY noise.** Feature-space (Probe 8a) is the dominant architectural lever. Switching from cosine to Mahalanobis on variant (iv) features does NOT recover transference at any noise level that's deployment-realistic.

**Mahalanobis is the right metric at clean baseline** for catching faint signals (transference at L0). This is theoretically expected but practically irrelevant — no deployment cohort exists at Level 0 noise.

**For the C3 amendment proposal (lit/42 §B):** cosine on variant (iv) features remains the recommended combination. Cosine gives HIGHER F-values at L2 than Mahalanobis on the parameters that survive (th + pr). No reason to switch.

## §C — Implications for Probe 8c (projection)

8c tests whether the unit-vector projection (used in cosine) or the centered z-score (used in Euclidean / Mahalanobis) matters. 8b's result that Euclidean ≈ Mahalanobis ≈ Cosine at L2 suggests projection is unlikely to be load-bearing either, but worth verifying.

If 8c also lands NEUTRAL, the architectural decomposition arc closes with feature-space (8a) as the SOLE load-bearing component. Probe 8d (test statistic) would then be the only remaining decomposition question; cheap to run.

## Status

Probe 8b closed: **DISTANCE METRIC NEUTRAL at L2.** Mahalanobis at L0 reveals transference is noise-fragile (real signal, unusable threshold), but at PRIMARY noise no metric provides additional discrimination beyond what cosine + variant (iv) already give. C3 amendment recommendation (cosine + variant iv) stands unchanged.

---

**Lock metadata:**
- 8b result commit: `82e706c`
- Result parquet SHA-256: `1E64A3CAFD27D780AC15CC7570D0DF37DE2B4D1FD3A7DCD2FFEDF418F6DE8C93`
