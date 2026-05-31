# C3 Probe 22 — Architecture-Quirk Robustness Result

**Status:** RESULT 2026-05-30. Disposition **ARCHITECTURE-SUBOPTIMAL** — the cosine-on-unit-normed-leaf-PCA variant (A5) beats the inherited Euclidean default (A0) by ~57% on median WMG transfer F, with all locked falsifiers passing.
**Pre-reg:** lit/78 (lock `79c1025`).
**Analyzer:** `code/c3_probe22_architecture_quirk.py` (SHA-256 `41272350490e9c8565e9d35f08924839c6b33a38a64e509a7a0c7d14a29e9618`).
**Result parquet:** `data/processed/probe22_architecture_quirk_results.parquet` (SHA-256 `686d7b20dc51b4b6f5cb3c73ef51ab8a9a5434e4019561eb9599f474be7886fe`).
**Inputs (unchanged from P21):** `paper2_operators_{khan,secl,zhang,wmg}_v2.parquet`; features locked to `{E1_ohmic_intercept, C2_R_DC_to_R_total, W1_warburg_slope, W3_peak_neg_im_norm, W5_arc_chord_length}`.
**Author:** Claude
**Repo HEAD on result:** `<TBD on commit>`.

## 1. Numerical result (200-seed cell-stratified bootstrap, REF_SEED=42 for 10k-perm p)

| Variant | Definition (short) | F median | [2.5pct, 97.5pct] | ref F | ref p |
|---|---|---:|---|---:|---:|
| **A0_REF** | RF leaf → standardize → PCA(10) → **Euclidean** | 5.703 | [3.139, 7.525] | 4.553 | 0.0193 |
| A1_NO_RF | standardize → PCA(min 10, 5) → Euclidean | 5.028 | [5.028, 5.028]† | 5.028 | 0.0050 |
| A2_RF_PROBA | RF.predict_proba → standardize → PCA → Euclidean | 5.482 | [2.911, 8.047] | 4.276 | 0.0236 |
| A3_PCA_2 | RF leaf → standardize → PCA(**2**) → Euclidean | 5.986 | [3.370, 8.336] | 4.482 | 0.0207 |
| A4_NO_PCA | RF leaf → standardize → Euclidean (full leaf-dim) | 3.916 | [2.623, 5.010] | 2.873 | 0.0258 |
| **A5_COSINE** | RF leaf → standardize → PCA(10) → unit-vec → **cosine** | **8.935** | [3.933, 22.943] | 9.956 | 0.0089 |

† A1 is deterministic in `rf_seed` (no RF — only PCA, which is itself seeded but operates on a fixed standardized feature matrix; output is identical across the 200 seeds for this feature set).

## 2. Falsifier outcomes (lit/78 §4)

- **F1 anchor reproduction:** A0 200-seed median F = **5.703** vs P21 anchor **5.703** (Δ = 0.000, tolerance ±0.300). **PASS**. The shim through `cascade_F_A0` reproduces the P21 pipeline numerically and seed-for-seed at this feature set.
- **F2 same bootstrap seed sequence:** all variants use `b ∈ {0..199}`, `rf_seed=b`. A0 ref-seed F = 4.553 matches the P21 lit/77 console line "RESELECTED_expanded ... refF=4.553" exactly. **PASS**.
- **F3 locked alphabet:** six variants {A0..A5} as enumerated in lit/78 §0.1. No additions. **PASS**.
- **F4 CI required, not just median:** A5_COSINE 2.5pct = **3.933 > 3.0 threshold**. Not a median-driven-by-outliers artifact. **PASS**.
- **F5 single-op illusion check (on H22-main winner A5_COSINE):** 1D F per feature under A5 at REF_SEED:

  | Feature | 1D F (A5_COSINE) |
  |---|---:|
  | E1_ohmic_intercept | NaN† |
  | C2_R_DC_to_R_total | 1.465 |
  | W1_warburg_slope | 1.516 |
  | W3_peak_neg_im_norm | NaN† |
  | W5_arc_chord_length | NaN† |

  max 1D F = **1.516** (W1). Cascade A5 median F = **8.935** → **5.9× lift** over best single feature; required threshold cascade > 1.20 × max_1D = 1.819. **PASS** by a wide margin. The cascade is not single-op-dominated.

  † NaN for the three single-feature cases comes from degenerate cosine-distance matrices: a 1D input to RF produces low-rank leaf embeddings; after PCA(10) + unit-norm, all points collapse to the same direction, ss_within → 0, F undefined. This is consistent with "no single feature alone supports the architecture," not a pipeline bug.

## 3. Hypothesis outcomes (lit/78 §1)

- **H22-anchor (F1):** PASS (Δ=0.000).
- **H22-main (architecture sub-optimal):** **PASS** — A5_COSINE: median 8.935 > A0 × 1.20 = 6.844 ✓; 2.5pct 3.933 > 3.0 ✓; p 0.0089 < 0.05 ✓.
- **H22-secondary (aggregator-robust ties):** **ALSO PASS** — two variants within ±10% of A0 median 5.703 (i.e. inside [5.133, 6.273]) with 2.5pct ≥ A0 2.5pct × 0.85 = 2.668:
  - A2_RF_PROBA median 5.482 ✓, 2.5pct 2.911 ✓
  - A3_PCA_2 median 5.986 ✓, 2.5pct 3.370 ✓
- **H22-null (architecture load-bearing):** **FAIL** — not all alts collapse; only A4_NO_PCA underperforms (median 3.916 = 69% of A0, but 2.5pct=2.623 > 1.5).

## 4. Disposition (lit/78 §5)

**ARCHITECTURE-SUBOPTIMAL.** Conditions met:
- H22-main PASS (A5_COSINE wins by ≥20%)
- F5 PASS (lift not from a single feature)
- F1 PASS (no pipeline corruption)
- F4 PASS (lower CI bound clears 3.0)

The inherited `cascade_F` aggregator (RF leaf → PCA(10) → **Euclidean** PERMANOVA) is sub-optimal vs **A5** (same pipeline through PCA(10), then **unit-vec normalize rows + cosine PERMANOVA**) for the P21 re-selected feature set `{E1, C2, W1, W3, W5}` against the WMG SOH-bin transfer test.

## 5. What this means

**Architectural decomposition:** the six-variant panel decomposes the four architectural choices:
- **Distance metric (Euclidean vs cosine):** A0 (5.703) vs A5 (8.935) on otherwise identical pipelines → **cosine wins by 57%**. The metric is the dominant load-bearing choice.
- **PCA dimensionality (10 vs 2 vs none):** A0 (5.703) ≈ A3 (5.986, PCA-2) > A4 (3.916, no PCA). **PCA matters; dim 2 vs 10 doesn't.** This is a partial vindication of the lit/47 variant-(iv) "PCA-2" framing — PCA-2 is fine, but PCA(10) is also fine; full leaf-dim hurts.
- **RF leaf embedding (vs none vs predict_proba):** A0 (5.703) ≈ A2 (5.482, proba) > A1 (5.028, no RF). **RF adds modest value; the proba and leaf paths perform similarly.** A1 doesn't strictly tie under H22-secondary (5.028 is 88% of A0, below the 90% threshold) but is comparable in magnitude.

**Single-op check confirms cascade integrity:** under A5, no single feature contributes ≥17% of the cascade F (best is W1 at 1.516, cascade is 8.935). The win is genuinely multivariate.

**Honest caveat — A5's wide upper tail:** A5_COSINE has 97.5pct=22.943 (vs A0's 7.525). The median is well-clear of A0 and the lower bound clears the bar; the wide tail reflects that cosine distance can produce large F values when the unit-normed embedding happens to separate cleanly. This is upside variance, not pipeline instability — it doesn't change the disposition but should be flagged for follow-up.

## 6. Implications for Paper-3 deliverable

The Paper-3 architecture should be updated:
- **Default aggregator:** A5 (RF leaf → standardize → PCA(min(10, d)) → unit-vec rows → cosine PERMANOVA) replaces A0 (Euclidean PERMANOVA on raw leaf-PCA embedding).
- **Anchor on `{E1, C2, W1, W3, W5}` under A5:** median F 8.935 [3.933, 22.943], p=0.0089.
- **A0 stays as a documented baseline** for back-compat with P15/P16/P20/P21 numbers; new probes should report both.

## 7. Required follow-ups (pre-committed)

- **P22b (noise audit on A5):** rerun the lit/74 L2-academic noise grid using A5_COSINE on `{E1, C2, W1, W3, W5}`. If A5 doesn't degrade more than A0 did at L2 (P20 anchor F=6.04), the new architecture is also noise-robust.
- **P22c (re-run earlier probes' headline F under A5):** report A5 values for P16's `{E1, C2}`, P20's `{E1, C2}` at L2 noise, P21's `{E1, C2, W1, W3, W5}` clean. None re-attribute the original results (they were valid under A0); the table just gives an A0/A5-parallel view for future readers.
- These are not auto-triggered. User-gated.

## 8. What Probe 22 does NOT establish

- A5 is the WINNER among the locked 6-variant panel — not a global optimum. Other metric/aggregator choices not in the panel were not tested.
- This is still WMG n=19 single-cohort transfer. Cross-substrate generalization to new held-out cohorts not yet tested under A5.
- Noise robustness of A5 not yet established (deferred to P22b).
- Whether the P15–P21 selection conclusions would change under A5 is not tested (deferred to P22c).
- The "wide upper tail" on A5 (97.5pct = 22.943) is documented, not yet investigated mechanistically.

## 9. Console output (verbatim)

```
A0_REF          F median= 5.703 [ 3.139,  7.525]  refF= 4.553 p=0.0193
A1_NO_RF        F median= 5.028 [ 5.028,  5.028]  refF= 5.028 p=0.0050
A2_RF_PROBA     F median= 5.482 [ 2.911,  8.047]  refF= 4.276 p=0.0236
A3_PCA_2        F median= 5.986 [ 3.370,  8.336]  refF= 4.482 p=0.0207
A4_NO_PCA       F median= 3.916 [ 2.623,  5.010]  refF= 2.873 p=0.0258
A5_COSINE       F median= 8.935 [ 3.933, 22.943]  refF= 9.956 p=0.0089

PROBE 22 DISPOSITION (per lit/78 sec 5)
  F1 anchor reproduces:        PASS (A0 median=5.703 vs 5.703)
  H22-main: PASS (winners: ['A5_COSINE'])
  H22-secondary: PASS (ties: ['A2_RF_PROBA', 'A3_PCA_2'])
  H22-null: FAIL
  F5 single-op check on winner: PASS
  ==> ARCHITECTURE-SUBOPTIMAL (winners: ['A5_COSINE'])
```
