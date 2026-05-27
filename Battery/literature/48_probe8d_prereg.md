# C3 Probe 8d — Test-Statistic Decomposition Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any 8d run fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/48_probe8d_prereg.md`
**Prior:** lit/41+42 (8a), lit/43+44 (8b), lit/45+46 (8c), lit/47 (C3 amendment lock `50c851e`). HEAD `50c851e`.

---

## 0. Why Probe 8d exists

8a + 8b + 8c established two load-bearing architectural levers (feature-space, projection) and one neutral component (distance metric). The C3 amendment was locked at `50c851e` based on this evidence. 8d closes the architectural decomposition arc by testing whether the **test statistic itself** (PERMANOVA's permutation-based pseudo-F) is load-bearing — or whether alternative model-based classifiers (Random Forest, logistic regression) on the same locked architecture (variant iv + PCA-2) give substantially different L2 dispositions.

This is a refinement question. The locked amendment's L2 PASS is already secured by PERMANOVA. 8d's outcomes:
- If RF / logistic match or modestly beat PERMANOVA → confirms PERMANOVA is a reasonable test for this architecture; amendment unchanged
- If RF / logistic catch transference where PERMANOVA misses → reopens the transference question (the amendment's transference NULL would be PERMANOVA-specific, not architecturally inevitable)
- If RF / logistic substantially DEGRADE → PERMANOVA is unusually good for this geometry; amendment still works but the choice of test is a load-bearing decision

## 1. Hypotheses (LOCKED)

**H8d-main-1 (RF matches or beats PERMANOVA):** Random Forest classifier 3-fold CV accuracy on the locked amendment's PCA-2 features achieves ≥ chance + 0.20 (vs the 1/3 = 0.33 chance baseline for the 3-level design parameters; threshold = 0.53) on at least 2 of 3 design parameters at Level 2 noise.

**H8d-main-2 (logistic catches transference where PERMANOVA misses):** Logistic regression (multinomial) on PCA-2 features achieves chance+0.20 on transference at Level 2 noise. If TRUE, transference would be recoverable by changing JUST the test statistic — reopens the transference question. If FALSE, transference is irrecoverable across PERMANOVA + RF + logistic; confirms it's not a test-statistic artifact.

**H8d-null:** RF and logistic give same L2 disposition pattern as PERMANOVA (th + pr PASS, transference NULL). Test statistic is NEUTRAL.

## 2. Setup (LOCKED)

- Cohort: 101 cells from v2 parquet (same filter).
- Architecture FIXED at the C3 amendment lock: variant iv 6D features → centered z-score → PCA k=2 → unit-vector projection.
- Wait — for RF and logistic, we don't need the unit-vector projection or cosine distance. The classifier operates directly on the PCA-2 z-scored features. So actual flow per cell:
  - x_i = (3 fresh + 3 aged absolute operators) → center+z-score → PCA k=2 → **classifier input = (PC1_i, PC2_i)**
- Noise grid: N1 only.
- Three tests on the same input features:
  1. PERMANOVA (baseline, reproduces 8c PCA-2 unit cosine)
  2. Random Forest classifier (sklearn `RandomForestClassifier`, n_estimators=500, max_depth=None, random_state=42), 3-fold CV accuracy
  3. Multinomial logistic regression (sklearn `LogisticRegression`, multi_class='multinomial', solver='lbfgs', max_iter=1000), 3-fold CV accuracy

For RF and logistic: per-parameter test = "can the classifier predict design parameter level from PC1, PC2?" Accuracy is the metric; chance is 1/3 = 0.333 for 3-level parameters.

**Verdict thresholds for RF and logistic (LOCKED):**
- Strong PASS: 3-fold CV accuracy ≥ 0.67 (≥ 2× chance) AND p < 0.0167 by per-fold permutation test (1000 perms, label shuffled within fold)
- PASS: accuracy ≥ 0.53 (chance + 0.20) AND p < 0.0167
- WEAK PASS: accuracy ≥ 0.45 (chance + 0.12) AND p < 0.05
- NULL: otherwise

For PERMANOVA: PASS/WEAK PASS/NULL per Probe 5/6 convention (p < 0.0167 + F > 3.0; etc.).

## 3. Cross-validation + permutation test detail

**RF/logistic CV:** 3-fold stratified by design parameter labels. Same seed (random_state=42) across folds. Train on 2/3 of cohort, test on 1/3, repeat 3 times, report mean accuracy across folds.

**Permutation test for RF/logistic:** to compute p-values for classifier accuracy, run 1000 label permutations: shuffle the design-parameter labels, re-run 3-fold CV, record accuracy. p-value = (n_perm_acc ≥ observed_acc + 1) / (n_perms + 1). One permutation distribution per design parameter per noise level per classifier.

This is more expensive than PERMANOVA's 10K perms because each permutation requires a full 3-fold CV — but with N=101 and shallow RF + lightweight logistic, total runtime should be ~5-15 min wall for all 5 levels × 3 params × 2 classifiers × 1000 perms.

## 4. Disposition criteria (LOCKED)

Headline = Level-2 outcome per classifier (count of PASSES + WEAK PASSES).

| Outcome | Verdict |
|---|---|
| RF or logistic catches transference at L2 (≥ PASS, while PERMANOVA L2 transference is NULL) | **TEST STATISTIC IS LOAD-BEARING.** Transference is PERMANOVA-fragile, not architecturally invisible. Reopens the transference question and potentially adds the chosen classifier as a third architectural lever. |
| RF and logistic both give same pattern as PERMANOVA (th + pr PASS, transference NULL) at L2 | **TEST STATISTIC NEUTRAL.** Amendment unchanged. Choice of PERMANOVA is justified but not necessary. |
| RF or logistic substantially DEGRADE at L2 (≤ 1/3 PASS) | **PERMANOVA IS THE LOAD-BEARING CHOICE.** RF/logistic can't handle the 2D PCA geometry well at N=101; PERMANOVA's distance-based approach is necessary for the amendment. |

## 5. Falsifiers (LOCKED)

**P8d_F1 (PERMANOVA reproduces 8c PCA-2 result):** PERMANOVA on PCA-2 + cosine at L2 must produce th F=21.24, pr F=20.87 bit-identically. INVALID otherwise.

**P8d_F2 (RF chance baseline at Level 0):** RF on PCA-2 at Level 0 should be NEAR-PERFECT on thickness + particle_radius (≥ 0.85 accuracy expected because the design signal is large at zero noise on a 6D base + 2D PCA). If RF doesn't beat 0.50 at L0 on either th or pr, RF is broken or hyperparameters need adjustment.

**P8d_F3 (logistic LinearSeparability at Level 0):** Multinomial logistic on PCA-2 at Level 0 on thickness should achieve ≥ 0.70 accuracy because the thickness signal in PC1 is essentially linear. If not, logistic is broken or the design is mis-encoded.

**P8d_F4 (monotonicity):** All three classifiers' accuracy decreases monotonically Level 0 → Level 4 (modulo ±10% noise floor).

## 6. What 8d does NOT establish

- Not a real-cell validation.
- Not a closure of the C3 amendment lock — even MAHALANOBIS RECOVERS TRANSFERENCE would be a separate amendment refinement, not a re-lock.

## 7. Operational protocol

1. Sign-off + commit pre-reg as `literature/48_probe8d_prereg.md`. Lock anchor = commit hash.
2. Build `code/c3_probe8d_test_statistic.py` — PERMANOVA + RF + logistic on PCA-2 features.
3. Run analyzer. Output: `data/processed/probe8d_test_statistic_results.parquet`.
4. Apply §4 disposition + §5 falsifiers.
5. Write up `literature/49_probe8d_result.md`.

Cost: 0 new data; modest CPU (1000-perm CV bootstrap). ~10-15 min wall expected.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD — recorded in follow-up commit>`
- v2 parquet SHA-256 (reused): `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
- Analyzer script SHA-256: `3B0A37D778DF393282EFD1E2A7E1363CF4DB75683190581D670DEEFD5271EF9C` (`code/c3_probe8d_test_statistic.py`)
