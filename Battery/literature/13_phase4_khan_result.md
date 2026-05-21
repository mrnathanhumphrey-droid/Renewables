# Phase 4 Held-Out Result — Khan 2025 Cohort

**Date:** 2026-05-21
**Status:** Pre-registered classifier run **complete on first held-out cohort.** Pre-registration locked at literature/09_phase4_pre_registration.md before this script touched Khan data. **VERDICT: PRIMARY FALSIFICATION CRITERION FAILED.** Direction of cells is consistent (mostly LLI-leaning) but the cosine-similarity-with-0.3-confidence-threshold protocol does not produce clean class separation on this cohort.

---

## Cohort

- Khan 2025 calendar+cycle aging dataset, NMC/graphite prismatic 5 Ah
- 19 cells with both capacity AND EIS data joined (after S2/S18 exclusion + EIS-folder availability)
- Aging campaign: 90 days, RPTs at days 0, 10, 20, 40, 90
- Source: literature/02_phase1_dataset_inventory.md section D

## Disagreement-onset triggered for every cell

Mahalanobis trajectories (excerpted):

```
day      S1     S10    S11    S12    S13    S14    S15    S16    S17    S19    S20    S21     S22    S23    S24     S3     S4     S8     S9
  0    0.00    0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00    0.00   0.00   0.00   0.00   0.00   0.00   0.00
 10  132.17  101.80  84.68  81.82  68.56  63.64  30.59  51.48  62.10  65.79 102.47 136.43  178.21 110.65 161.67  64.74  33.63  56.84 103.86
 20  118.05   88.35  63.79 109.20  54.88  88.90  55.08  90.13 111.40 119.59 140.79 217.95  336.60 173.68 234.74  76.18  81.78  94.51 142.69
 40  200.99   95.76  95.96 216.25  78.11 139.87  72.37 132.08 220.40 148.52 228.80 337.98  868.73 414.77 368.56  87.99 240.65  99.13 152.01
 90  353.00  120.80 160.02 461.08 147.16 282.47 161.91 203.78 683.53 925.46 429.95 628.60 2075.09 925.46 818.24 104.23 324.62 149.12 169.97
```

Every cell exceeds the 99th-percentile χ²(3) threshold (3.37) by day 10. **Direction-of-disagreement consistently in the negative-Q_max half of operator space** (capacity drop dominant).

## Classifier results per pre-registered protocol

Reference centroids:
- `u_LLI = (-1, 0, 0)` (capacity drop, no resistance change)
- `u_LAM_SEI = (-1, +1, +1)/√3` (capacity drop + both resistance markers grow)
- Classification = argmax of cosine similarity; confidence = |s_LLI − s_LAM_SEI|; threshold 0.3

```
cell  n_flagged  class           confidence  s_LLI  s_LAM_SEI
S1            4  unclassified         0.290  0.953   0.663
S10           4  LAM+SEI              0.543  0.440   0.984     ← confidently classified
S11           4  unclassified         0.190  0.906   0.716
S12           4  unclassified         0.145  0.938   0.793
S13           4  LAM+SEI              0.315  0.656   0.970     ← confidently classified
S14           4  LLI                  0.363  0.986   0.623     ← confidently classified
S15           4  unclassified         0.038  0.896   0.858
S16           4  unclassified         0.232  0.955   0.723
S17           4  unclassified         0.255  0.954   0.699
S19           4  unclassified         0.245  0.966   0.721
S20           4  unclassified         0.040  0.892   0.852
S21           4  unclassified         0.051  0.888   0.837
S22           4  unclassified         0.025  0.832   0.857
S23           4  unclassified         0.015  0.828   0.843
S24           4  unclassified         0.270  0.945   0.675
S3            4  unclassified         0.297  0.823   0.526
S4            4  unclassified         0.102  0.783   0.885
S8            4  unclassified         0.231  0.642   0.873
S9            4  unclassified         0.147  0.904   0.757
```

## Pre-registered falsification verdict

| Criterion | Threshold | Observed | Verdict |
|---|---|---|---|
| ≥50% confidently classified | ≥10/19 | **3/19 (15.8%)** | **FAIL** |
| ≥70% LAM+SEI among classified (NMC) | ≥70% of classified | 2/3 = 66.7% | Marginal (just below) |
| Permutation null p < 0.0167 (Bonferroni /3) | < 0.0167 | **p = 1.0000** | **FAIL** |

**PRIMARY VERDICT: H1 falsified on Khan 2025 cohort.** The pre-registered cosine-similarity classifier does NOT replicate the V4-vs-W-cells residual-direction separation pattern on the independent N=19 prismatic NMC/graphite cohort.

## Why this happens — diagnostic interpretation

The classifier is "unclassified" not because cells lack direction, but because **their direction sits between the LLI and LAM+SEI reference centroids**. Both centroids share the −Q_max axis (capacity drop), and most Khan cells show:

- Strong capacity drop (high s_LLI component on the −Q_max axis)
- Moderate but non-zero R_ohmic + R_diff growth (partial LAM+SEI alignment)

Result: cells score high on BOTH centroids simultaneously (s_LLI ~0.9, s_LAM_SEI ~0.7) → low |s_LLI − s_LAM_SEI| → confidence below 0.3.

Two readings:
1. **The N=4 V4-vs-W exploratory pattern was an over-specification.** V4 happened to have a near-pure LLI signature (R_ohmic z ≈ 0); W-cells happened to have very pure LAM+SEI (R_ohmic z ≈ +5). The Khan cohort's prismatic cells age in a more "balanced" way that sits between those extremes. The pre-registration's centroid definitions, derived from physics intuition but informed by the V4-vs-W extremity, may have been too coarse to capture the intermediate cases.
2. **C2's mode-classification claim requires a finer-grained protocol.** A two-cluster cosine classifier is too coarse. A continuous mode-direction metric (e.g., the ratio s_LLI / s_LAM_SEI as a continuous score, or a 2D scatter of the unit residual directions) might reveal cluster structure that argmax + threshold misses.

The pre-reg was set before Khan was touched; we are honor-bound to report this primary verdict as FAIL. Any follow-up analysis (e.g., relaxing the threshold, or using a continuous score) is post-hoc exploratory.

## What this means for the C2 paper

The Phase 4 second claim ("type of inter-operator disagreement identifies the degradation mode") is **NOT confirmed at the pre-registered protocol** on the first held-out cohort.

- Phase 3 first-claim direction was supported (sign test p=0.031 on N=7) but magnitude below pre-reg
- Phase 4 second-claim direction is preserved (all cells show inter-operator disagreement onset), but cluster separation as pre-specified is not detectable on the Khan cohort

**Honest paper-framing draft (revised):**

> The cross-operator disagreement-onset metric triggers reliably on aged cells across three independent cohorts spanning different chemistries (NMC/Si-graphite cylindrical and NMC/graphite prismatic). The metric precedes capacity-knee-point detection in 5/7 first-life SECL cells (sign test p=0.031), confirming the directionality of the first claim. However, the pre-registered classifier for the second claim — which sought to discriminate LLI-dominant from LAM+SEI-dominant cells by residual direction — did not achieve the pre-registered confidence threshold on the Khan 2025 prismatic cohort (3/19 cells confidently classified vs ≥10/19 required, permutation null p=1.0). The exploratory N=4 SECL pattern that informed the centroid definitions did not generalize. Open question for follow-up: whether a finer-grained continuous-mode-score protocol can recover cluster structure that the discrete argmax+threshold protocol misses; this would need its own pre-registration on a fresh cohort.

## What this changes in the project state

1. **Phase 4 second-claim PARTIAL/NULL on first held-out cohort.** Direction preserved (disagreement triggers), cluster separation as pre-specified does not.
2. **C2's contribution narrows further.** First-claim direction confirmed but magnitude small. Second-claim cluster structure not confirmed at pre-reg protocol. The methodology's value sits more in (a) the disagreement-onset signal itself as a binary alarm and (b) the operator-agnostic framework demonstration than in either headline lead-time or mode-classification.
3. **Zhang Cambridge + WMG cohorts still pending.** Pre-reg requires running the same protocol on all three replication cohorts before final verdict. Zhang Cambridge has explicit aging-mode labels — that's the cleanest cross-validation if the labels match the LLI/LAM+SEI taxonomy.
4. **Khan result is not data fishing.** The permutation null p=1.0 is unambiguous. The reported verdict is what it is.

## Output

- `data/processed/khan_2025_classification.parquet` — per-cell classifications
- `code/khan_extract_and_classify.py` — locked classifier code
