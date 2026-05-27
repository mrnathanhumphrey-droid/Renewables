# C3 Probe 8b — Distance-Metric Decomposition Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any 8b PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/43_probe8b_prereg.md`
**Prior:** literature/41+42 (Probe 8a — feature-space established as dividing line; variant (iv) fresh+aged 6D stacked is the winning configuration with 2/3 PASS at L2: th F=14.3, pr F=13.6). HEAD `0b3c2f4`.

---

## 0. Why Probe 8b exists

8a established that feature-space is the load-bearing component for L2 noise survival. With the winning feature space (variant iv), the C3 architecture passes thickness + particle_radius at L2 but transference remains NULL (F=0.76, p=0.57). 8a §A.4 attributed transference invisibility to the operator triad not capturing electrolyte-ionic-conduction signatures.

8b tests an alternative explanation: **does the distance metric matter?** Cosine distance on unit-vectors discards magnitude information; Mahalanobis distance accounts for within-condition covariance. If transference variation moves the joint feature vector in a direction that cosine sees as "same angle, different magnitude," then Mahalanobis might catch it where cosine fails.

This is the second probe in the C3 architectural-decomposition series. 8c (projection) and 8d (test statistic) follow.

## 1. Hypotheses (LOCKED)

**H8b-main (Mahalanobis recovers transference):** At Level 2 N1 noise, on the winning feature space (variant iv: fresh+aged 6D stacked from 8a), Mahalanobis-distance PERMANOVA achieves 3/3 PASS (catching transference where cosine fails 2/3 in 8a).

**H8b-null:** Mahalanobis fails to add transference. All three distance metrics give similar disposition at L2.

**H8b-secondary-1 (Euclidean ≈ Cosine):** Euclidean distance on the same feature space gives similar disposition to cosine. Both are magnitude-respecting in different ways; neither accounts for within-condition covariance the way Mahalanobis does. Predict NULL on transference for both.

**H8b-secondary-2 (Mahalanobis improves F-values on th + pr):** Even if transference stays NULL, Mahalanobis should give substantially higher F-values on thickness and particle_radius at L2 than cosine, because covariance-aware distance is generally tighter for between-group inference than the unit-vector cosine bound.

## 2. Setup (LOCKED)

- **Cohort:** Same 101-cell filtered v2 parquet as Probe 8a (`pybamm_l9_trajectories_eis_v2.parquet`, SHA `7A03BCC9…F79AA`).
- **Feature space FIXED at variant (iv):** fresh + aged 6D stacked. Per cell: (fresh_Q, R_ohmic_fresh, R_diff_fresh, anchor_aged_Q, R_ohmic_aged_b5, R_diff_aged_b5).
- **Noise grid:** N1 only (same as 8a).
- **Three distance metrics tested:** Cosine (baseline / reproducibility), Euclidean, Mahalanobis.

## 3. Distance metric definitions (LOCKED)

For 101-cell feature matrix Z (post-z-score):

1. **Cosine** (baseline, matches 8a): unit-project u_i = z_i / ||z_i||; d(i,j) = 1 − cos(θ_ij) = 1 − u_i · u_j.

2. **Euclidean**: d(i,j) = ||z_i − z_j||₂. No unit-vector projection — uses centered z-scores directly.

3. **Mahalanobis**: d(i,j) = sqrt((z_i − z_j)ᵀ Σ⁻¹ (z_i − z_j)), where Σ is the **pooled within-condition covariance** computed across the cohort. Pooled per the standard PERMANOVA convention: Σ = (1/(N − a)) Σ_g Σ_{i ∈ g} (z_i − ẑ_g)(z_i − ẑ_g)ᵀ, where ẑ_g is the centroid of condition g and a is the number of conditions for the design parameter being tested. Computed ONCE per design parameter (thickness/transference/particle_radius); not noise-level-dependent within a level.

**Numerical stability:** At n=101 cells and d=6 features, Σ is well-conditioned. If `np.linalg.cond(Σ) > 1e10`, fall back to pseudoinverse via `np.linalg.pinv` and log a flag. Document deviation if pinv fires.

## 4. PERMANOVA method (LOCKED — distance-metric-agnostic)

Per (metric, noise level, design parameter):

1. Construct feature matrix per variant (iv) on noisy fresh + noisy aged values (same noise injection as 8a).
2. Compute pairwise distance matrix D using the metric.
3. Compute pseudo-F via the standard PERMANOVA decomposition (between-group SS / within-group SS), independent of distance metric.
4. 10,000 label permutations, p-value = (n_ge + 1) / (n_perms + 1).
5. PASS / WEAK PASS / NULL per Probe 5/6 convention (p < 0.0167 AND F > 3.0; or 0.0167 ≤ p < 0.05 AND F > 2.0).

**Note on permutation invariance:** PERMANOVA's pseudo-F is well-defined for any distance metric, not just cosine. The between/within SS decomposition uses the distance matrix as the "geometry"; metric choice changes the geometry. This is methodologically standard.

## 5. Disposition criteria (LOCKED)

Headline = Level-2 outcome per metric on variant (iv) features.

| Outcome | Verdict |
|---|---|
| Mahalanobis ≥ 3/3 PASS at L2 (catches transference) | **MAHALANOBIS RECOVERS TRANSFERENCE** — distance metric is additionally load-bearing on top of feature-space. C3 amendment candidate strengthens: variant (iv) + Mahalanobis as the L2-robust deployment combo. |
| Mahalanobis 2/3 PASS at L2 with higher F-values than cosine | **MAHALANOBIS PARTIAL IMPROVEMENT** — same number of PASSES as cosine but stronger discrimination on th+pr. Refinement, not transference recovery. Doesn't change L2 disposition but improves the deployment safety margin. |
| Mahalanobis = Cosine at L2 (2/3 PASS, similar F) | **DISTANCE METRIC NEUTRAL** — feature-space choice (from 8a) is the dominant lever; metric choice is secondary. |
| Mahalanobis < Cosine at L2 | **MAHALANOBIS DEGRADES** — unexpected; investigate (likely covariance estimation issue at N=101 with multiple conditions). |
| Euclidean ≈ Cosine | Confirms H8b-secondary-1 (both magnitude-respecting; neither covariance-aware). |

## 6. Falsifiers (LOCKED)

**P8b_F1 (cosine on variant (iv) reproduces 8a result):** Cosine at L2 must produce 2/3 PASS (th + pr) with F-values matching 8a's variant (iv) result (th F≈14.3, pr F≈13.6) within ±10%. If not, the analyzer differs from `code/c3_probe8a_feature_space.py` in a way that breaks reproducibility. INVALID disposition.

**P8b_F2 (Mahalanobis covariance well-conditioned):** Σ for each design parameter must have condition number < 1e10. If not, pinv fallback fires; document in §A.

**P8b_F3 (monotonicity within metric):** F-values per metric decrease monotonically across noise levels 0 → 4 (modulo permutation variance, ±25%). Major violations trigger debug.

**P8b_F4 (between-metric correlation at extremes):** At Level 0 (no noise), all three metrics should give the same PASS/NULL disposition. If they disagree at L0, metric choice is interacting with the synthetic baseline in unexpected ways; investigate.

## 7. What 8b does NOT establish

- Not a real-cell validation.
- Not a test of feature-space (already established as load-bearing in 8a).
- Not a test of projection (deferred to 8c).
- Not a test of test statistic (deferred to 8d).
- Even MAHALANOBIS RECOVERS TRANSFERENCE doesn't close the C3 framework — would need cross-substrate validation on a real-cell EIS cohort that doesn't currently exist in the corpus.

## 8. Operational protocol

1. Sign-off + commit this pre-reg as `literature/43_probe8b_prereg.md`. Lock anchor = commit hash.
2. Build `code/c3_probe8b_distance_metric.py` — three distance metrics on variant (iv) features.
3. Run analyzer. Output: `data/processed/probe8b_distance_metric_results.parquet`.
4. Apply §5 disposition + §6 falsifiers.
5. Write up `literature/44_probe8b_result.md`.

Cost: 0 new compute (analyzer-only on v2 parquet). ~3-5 min wall.

## 9. Pre-commit checklist

- [ ] Nathan signs off on Probe 8b spec
- [ ] Pre-reg + analyzer committed BEFORE running analyzer

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `c0fa935`
- v2 parquet SHA-256 (reused): `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
- Analyzer script SHA-256: `93814AB7B650B12E7398D292EFD06C127232EFC6BC29DF7B989F8FC9A5F7F1B9` (`code/c3_probe8b_distance_metric.py`)
