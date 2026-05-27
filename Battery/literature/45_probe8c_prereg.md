# C3 Probe 8c — Projection Decomposition Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any 8c PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/45_probe8c_prereg.md`
**Prior:** literature/41+42 (8a — feature-space dividing line; variant iv winning), literature/43+44 (8b — distance-metric neutral at L2). HEAD `d14f9d6`.

---

## 0. Why Probe 8c exists

8a established feature-space as the load-bearing architectural lever. 8b established distance metric as NEUTRAL at L2 (all three of cosine, Euclidean, Mahalanobis give 2/3 PASS on variant iv). The remaining architectural component to test is **projection** — specifically, whether the unit-vector projection step (used by cosine, implicit in Euclidean post-z-score) is necessary, or whether the magnitude information it discards would help.

Question: on variant (iv) features (fresh+aged 6D stacked), does dropping the unit-vector projection step improve discrimination? Or PCA-reducing the 6D feature space to 2-3 principal components?

Three projection variants on the cosine + variant-iv combination:
1. **Unit-vector** (current baseline) — used by cosine in 8a/8b
2. **Raw centered z-score** (no projection) — features stay in R^6, no normalization to sphere
3. **PCA-reduced** — first k principal components (k=2 or 3)

## 1. Hypotheses (LOCKED)

**H8c-main (raw improves discrimination):** Raw centered z-score features (no unit-vector projection) give higher F-values at L2 than unit-vector cosine on variant (iv). The magnitude information that unit-projection discards is informative for design separation.

**H8c-secondary-1 (PCA narrows but doesn't lose):** PCA-reducing 6D to 2-3 components preserves the L2 disposition (2/3 PASS) on variant (iv). The reduction captures the design-relevant variance without losing thickness or particle_radius signal.

**H8c-secondary-2 (PCA k=2 vs k=3):** Reporting both, no PASS/FAIL prediction; descriptive only.

**H8c-null:** Raw and PCA give similar dispositions to unit-vector cosine at L2. Projection is NEUTRAL on this feature space.

## 2. Setup (LOCKED)

- **Cohort:** 101 cells from v2 parquet (same filter as 8a / 8b).
- **Feature space FIXED at variant (iv):** fresh+aged 6D stacked.
- **Noise grid:** N1 only.
- **Distance metric FIXED at cosine** (per 8b neutrality, and to match 8a baseline).
- **Three projection variants:**
  1. Unit-vector projection (baseline, reproduces 8a variant iv): u_i = z_i / ||z_i||₂
  2. Raw centered z-score (no projection): use z_i directly
  3. PCA-reduced: compute PCA on the 101×6 z-score matrix; project onto first k principal components (k=2 and k=3 reported)

For variants 1 and 2: cosine PERMANOVA on the resulting vectors.
For variant 3: cosine PERMANOVA on the PCA-projected vectors (which live in R^k).

## 3. PERMANOVA architecture

Per (projection, noise level, design parameter):

1. Apply noise to fresh + aged values (same as 8a/8b).
2. Build variant (iv) features (6D fresh+aged stacked).
3. Center + z-score (same as 8a/8b).
4. Apply projection:
   - Unit: u_i = z_i / ||z_i||₂; cosine distance d_ij = 1 - u_i·u_j
   - Raw: u_i = z_i; cosine distance d_ij = 1 - (z_i·z_j) / (||z_i|| ||z_j||) [equivalent to unit-vector — wait, this means "raw cosine" = "unit cosine" mathematically]

Hmm — cosine distance on raw vectors IS the unit-vector projection by construction. So "raw" only differs from "unit" if we change the distance to Euclidean or use a non-cosine metric.

Reformulating:
- Variant 1 (unit + cosine) = baseline (8a variant iv result)
- Variant 2 (raw + Euclidean) = "no projection, Euclidean distance" — equivalent to 8b's Euclidean
- Variant 3 (PCA-reduced + cosine, k=2)
- Variant 4 (PCA-reduced + cosine, k=3)

So 8c effectively tests: does projection to a lower-dim PCA subspace help vs the full 6D unit projection?

Variant 2 ("raw + Euclidean") is already tested in 8b; not repeated.

Three new tests:
- Unit-vector cosine on PCA-2 (k=2)
- Unit-vector cosine on PCA-3 (k=3)
- (Implicit reference: 8a/8b unit cosine on full 6D)

5. PERMANOVA per design parameter, 10,000 permutations.
6. PASS/WEAK PASS/NULL per Probe 5/6 convention.

## 4. Disposition criteria (LOCKED)

Headline = Level-2 outcome.

| Outcome | Verdict |
|---|---|
| PCA-2 or PCA-3 ≥ 2/3 PASS at L2 with F-values comparable to or higher than full-6D | **PROJECTION REDUCTION SAFE** — full 6D feature space is over-parameterized; PCA can simplify without loss. C3 amendment refines to "variant iv + PCA-k". |
| PCA-2 or PCA-3 < 2/3 PASS at L2 while full-6D PASSES | **PROJECTION HURTS** — full 6D is necessary; PCA discards signal. C3 amendment recommendation unchanged. |
| PCA-3 ≥ PCA-2 at L2 | **PCA-3 PREFERRED** — third component carries informative variance for design separation. |

## 5. Falsifiers (LOCKED)

**P8c_F1 (full-6D baseline):** Full-6D unit cosine at L2 must reproduce 8a variant (iv) result (th F≈14.3, pr F≈13.6). Within ±5%. INVALID if not.

**P8c_F2 (PCA variance retained):** k=2 PCA retains > 70% of total variance; k=3 retains > 85%. If not, the 6D feature space has structure that's not well-captured by leading PCs — report and flag.

**P8c_F3 (within-projection monotonicity):** F-values per projection decrease monotonically L0 → L4.

**P8c_F4 (PCA component direction interpretation):** Report the loading of the top 2 PCs. If PC1 is approximately the "thickness axis" (heavy weight on R_ohmic_fresh + R_ohmic_aged) and PC2 is the "particle radius axis," this is expected from the 8a data. If they're mixed, document as §A.

## 6. What 8c does NOT establish

- Not a real-cell validation.
- Not a test of test statistic (deferred to 8d, optional).
- Not a closure of the C3 amendment — depends on cross-substrate testing not in this scope.

## 7. Operational protocol

1. Sign-off + commit pre-reg as `literature/45_probe8c_prereg.md`.
2. Build `code/c3_probe8c_projection.py` — three projections on variant (iv) features.
3. Run analyzer. Output: `data/processed/probe8c_projection_results.parquet`.
4. Apply §4 disposition + §5 falsifiers.
5. Write up `literature/46_probe8c_result.md`.

Cost: 0 new compute. ~3 min wall.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `139ac25`
- v2 parquet SHA-256 (reused): `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
- Analyzer script SHA-256: `D3C6767AC2E9AFAB5F7AC79B2F4E0A2C8CA07DB4F20D7A0489A1A22F18964D44` (`code/c3_probe8c_projection.py`)
