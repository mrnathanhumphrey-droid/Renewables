# C3 Probe 8a — Feature-Space Decomposition Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any 8a PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/41_probe8a_prereg.md`
**Prior:** literature/37-40 (Probe 7 v1 + v2 arc, HEAD `1f35b48`).

---

## 0. Why Probe 8a exists

Probe 7 v1 + v2 closed the operator-triad-swap branch of the C3 framework search: three independent operator extractions (HPPC, B7 LAM-proxy EIS, B5' cycling-read EIS) all collapse at typical academic Level-2 noise under the standard C3 architecture (residual unit-vector cosine PERMANOVA). But Probe 7.3 (fresh-state features × N1) PASSED 2/3 at Level 2 — same data, same noise, same operators, same PERMANOVA — only the feature space changed from "residuals" to "absolute fresh values."

That single positive variant is informative: at least one architectural component (feature-space choice) is on the dividing line between Level-2-collapse and Level-2-survival. Probe 8a localizes whether feature-space choice fully explains the survival pattern, or whether it's one of several load-bearing architectural choices.

This is the first probe in a planned decomposition series (8a feature space, 8b distance metric, 8c projection, 8d test statistic). 8a is the cleanest first step because all variants are computable from the existing v2 parquet — no new generator needed.

## 1. Hypotheses (LOCKED)

**H8a-main (feature-space is load-bearing):** At least one of the four new feature-space variants — (ii), (iii*), (iv), (v) — PASSES ≥ 2 of 3 design parameters at Level 2 under N1 noise, while variant (i) [current C3] continues to NULL at 0/3. Establishes feature-space as one explanatory variable in the L2 collapse pattern.

**H8a-null:** All five variants behave similarly at L2 (either all collapse or all survive). Feature-space is NOT a dividing architectural component.

**H8a-secondary (which feature-space survives best):** Reported descriptively. Predictions based on v2 data:
- (ii) Aged absolute: expected to PASS broadly (R_ohmic_aged_b5 between/within = 1210, even cleaner thickness oracle than fresh's 746)
- (iv) Fresh + aged stacked (6D): expected to PASS at L2 (stacking can't lose information vs single-set)
- (v) Fresh + residual stacked (6D): expected to PASS at L2 (residuals add some aging info on top of fresh discriminators)

\* Note: variant (iii) = fresh absolute already PASSED 2/3 at L2 in literature/40 §B (Probe 7.3). Re-running it in 8a is a reproducibility check, not new evidence.

## 2. Five feature-space variants (LOCKED)

All variants use the B5' aged-EIS values from the v2 parquet (`pybamm_l9_trajectories_eis_v2.parquet`). All use the same architecture downstream: per-noise-level pool-SD z-scoring → unit-vector projection → cosine PERMANOVA. Only the *feature construction* changes.

| Variant | Feature construction | Dimensionality | Established? |
|---|---|---|---|
| (i) | Residuals only: (aged_Q − fresh_Q, R_ohmic_aged_b5 − R_ohmic_fresh, R_diff_aged_b5 − R_diff_fresh) | 3 | Yes — v2 PRIMARY, 0/3 at L2 |
| (ii) | Aged absolute only: (aged_Q, R_ohmic_aged_b5, R_diff_aged_b5) | 3 | No |
| (iii) | Fresh absolute only: (fresh_Q, R_ohmic_fresh, R_diff_fresh) | 3 | Yes — v2 Probe 7.3, 2/3 at L2 |
| (iv) | Fresh + aged stacked: 6-vector concatenation | 6 | No |
| (v) | Fresh + residual stacked: 6-vector concatenation | 6 | No |

Noise injection: applied to all underlying fresh and aged absolute values BEFORE feature construction (so a residual in variant (i) sees noise on both fresh and aged components; an aged-absolute in variant (ii) sees noise only on aged; etc.). Same per-cell seed convention as `c3_noise_injection.py` (RNG_SEED_BASE = 2000).

## 3. Noise grid (LOCKED — N1 only)

Identical to literature/39 §5 N1 (Probe 6 / v1 / v2 PRIMARY noise grid). Five levels, with Level 2 ("typical academic") as the PRIMARY headline.

| Level | σ_Q | σ_R_ohmic | σ_R_diff |
|---|---|---|---|
| 0 | 0.000 | 0.00 | 0.00 |
| 1 | 0.001 | 0.05 | 0.10 |
| 2 | 0.005 | 0.15 | 0.20 |
| 3 | 0.010 | 0.30 | 0.30 |
| 4 | 0.020 | 0.50 | 0.50 |

N2 noise grid + Probe 8b/c/d are deferred to follow-up pre-regs.

## 4. PERMANOVA architecture (LOCKED — same as Probe 5/6/7)

For each (variant, noise level, design parameter):

1. Apply Gaussian noise to fresh AND aged absolute values (per-cell, per-side seeded; identical seed structure to v1+v2).
2. Construct feature vector per §2 variant.
3. Z-score by per-noise-level pool-SD (computed on the constructed features after centering on cohort mean).
4. Project to unit sphere: u_i = z_i / ‖z_i‖₂.
5. Cosine PERMANOVA per design parameter (10,000 permutations).
6. Verdict per Probe 5/6 convention: PASS (p < 0.0167 AND F > 3.0), WEAK PASS (0.0167 ≤ p < 0.05 AND F > 2.0), NULL otherwise.
7. Level verdict: LEVEL ROBUST (≥ 2/3 PASS), LEVEL WEAK (1 PASS or 1 PASS + 1 WEAK PASS), LEVEL COLLAPSED (0 PASS).

Cohort filter: 106 sim-success cells minus 5 anchor_partial = **101 cells** (same N as v2 PRIMARY).

## 5. Disposition criteria (LOCKED)

Headline = Level-2 outcome per variant.

| Outcome | Verdict | Implication for C3 decomposition |
|---|---|---|
| **FEATURE-SPACE IS THE DIVIDING LINE** | Variant (i) NULL at L2 AND ≥ 1 of {(ii), (iv), (v)} ≥ 2/3 PASS at L2 | Feature-space is at least one load-bearing architectural component. Probe 8b/c/d may still find additional load-bearing components but feature-space alone is sufficient to recover Level-2 survival. |
| **FEATURE-SPACE IS PARTIAL** | (i) NULL AND (iii) PASS [reproducing v2] AND (ii)/(iv)/(v) PARTIAL or NULL | Fresh-state specifically rescues, but generic feature-space changes don't. Suggests R_ohmic_fresh's 746× thickness oracle is the specific mechanism, not feature-space generality. |
| **FEATURE-SPACE NOT DIVIDING** | All five variants similar at L2 (all collapse or all survive) | Feature-space is NOT the load-bearing choice. Probe 8b (distance metric) becomes the higher-priority follow-up. |
| **PROBE 8a INVALID** | (i) ≠ v2 PRIMARY (0/3 at L2) OR (iii) ≠ v2 Probe 7.3 (2/3 at L2) | Pipeline bug; debug and re-run before disposition. |

## 6. Falsifiers (LOCKED)

**P8a_F1 (variant (i) v2 PRIMARY reproduction):** Variant (i) at L2 MUST produce 0/3 PASS to confirm the analyzer reproduces v2 PRIMARY exactly. If not, the analyzer's noise + standardization pipeline has drifted from c3_probe7_v2_permanova.py. INVALID disposition.

**P8a_F2 (variant (iii) v2 Probe 7.3 reproduction):** Variant (iii) at L2 MUST produce ≥ 2 PASS to confirm the analyzer reproduces v2 Probe 7.3 (which had th + pr both PASS). Same reasoning as F1. INVALID disposition if not.

**P8a_F3 (within-noise-level monotonicity):** Per design parameter, F-values should be largest at Level 0 and decrease monotonically (modulo permutation variance ± 25%). Major violations trigger debug.

**P8a_F4 (stacked-feature minimum-survival):** Variants (iv) and (v) stack additional features on top of variant (iii) (fresh absolute, which already passes 2/3 at L2). Stacking cannot REMOVE information — so (iv) and (v) at L2 should achieve ≥ as many PASSES as (iii) (≥ 2). If (iv) or (v) FAILS at L2 while (iii) PASSES at L2, something architecturally weird is happening (probably the cosine-distance + unit-vector projection interacting badly with the higher-dim feature space). Flag for §A but not invalidate.

## 7. What 8a does NOT establish

- Not a real-cell validation. Same gap as Probe 7.
- Not a closure of the C3 framework. Even if 8a identifies feature-space as dividing, the recommended C3 amendment (likely "switch to fresh+residual stacked features") needs cross-substrate testing on real cells before promotion.
- Not a test of distance metric, projection, or test statistic. Those are Probe 8b/c/d.
- Not a test of N2 EIS-realistic noise. N1 only in this lock.

## 8. Operational protocol

1. Sign-off + commit this pre-reg as `literature/41_probe8a_prereg.md`. Lock anchor = commit hash.
2. Compute and record SHA-256 of the analyzer script in the lock metadata.
3. Build `code/c3_probe8a_feature_space.py` — analyzer running all 5 variants × 5 noise levels against the v2 parquet.
4. Run analyzer. Output: `data/processed/probe8a_feature_space_results.parquet`.
5. Apply §5 disposition + §6 falsifiers.
6. Write up `literature/42_probe8a_result.md`.

Cost: 0 compute (no Modal, no PyBaMM, analyzer-only on existing v2 parquet). 5 variants × 5 noise levels × 3 PERMANOVAs × 10000 perms ≈ 75 PERMANOVAs. ~3-5 min wall.

## 9. Planned follow-ups (NOT pre-registered here)

- **Probe 8b — distance metric:** Mahalanobis vs Euclidean vs cosine on the winning feature-space from 8a.
- **Probe 8c — projection:** Unit-vector vs raw vs PCA on the winning combo.
- **Probe 8d — test statistic:** PERMANOVA vs RF classifier accuracy vs logistic-regression Wald.

These will be pre-registered separately based on 8a's outcome.

## 10. Pre-commit checklist

- [ ] Nathan signs off on Probe 8a spec
- [ ] v2 parquet (`pybamm_l9_trajectories_eis_v2.parquet`, SHA `7A03BCC9…F79AA`) present
- [ ] Analyzer to be built BEFORE the lock commit so its SHA can be recorded in §11
- [ ] Pre-reg committed BEFORE running analyzer

## 11. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD — recorded in follow-up commit>`
- v2 parquet SHA-256 (reused): `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
- Analyzer script SHA-256: `04B24CB1501F0C3C0F3689C7C07E1E6E3EE958A4C7C65544ECBDF7365632AD54` (`code/c3_probe8a_feature_space.py`)
