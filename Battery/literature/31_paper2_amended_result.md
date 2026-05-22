# Paper 2 — Amended-Protocol Result: PARTIAL REPLICATION (Pre-Reg-Strict)

**Date:** 2026-05-22
**Pre-registrations:**
- Operator catalog: literature/27 (commit `13e9f80`)
- Selection + cascade + holdout: literature/28 (commit `7fae62a` + amendment `153fbd3` + amendment `3ad6c5c`)
- Gate I diagnostic-driven amendment: literature/30 (commit `3ad6c5c`)
**Strict-pre-reg companion result:** literature/29 (commit `2ffb513`) — Paper 2 INVALID under blanket-CV Gate I. **Stands; not retracted.**

**Verdict (per pre-reg §7 strict reading under amended protocol):** **PAPER 2 PARTIAL REPLICATION.** Primary validation on PyBaMM-holdout passes (F=57.26, p=0.0001); secondary WMG validation is vacant by literature/28 §10 first amendment because no E1-E3 operators survived Gate II.

This is a protocol-evolution document, written in the cancer-substrate "Δ=+6.26 nats CI-off-zero-but-Gibbs-contingent" honest-conditional style. The strict-pre-reg result (literature/29) and the amended-protocol result (this document) are reported together. Readers can audit literature/30's falsification-resistance check (§5 of that document) against the amendment's actual effect and decide whether the protocol evolution is honest.

---

## 0. The dual result

| Pipeline | Strict pre-reg (literature/29) | Amended pre-reg (this doc) |
|---|---|---|
| 12 candidates → Gate I → | **1** (E1 only) | **8** (T1, T2, T3, T4, T5, C1, C2, E1) |
| Gate I → Gate II → | **0** | **7** (T1, T2, T3, T4, T5, C1, C2 — E1 fails cohort-coverage) |
| Cascade trains? | NO (no operators) | YES (7 operators, RF locked) |
| PRIMARY validation | not applicable | **F=57.26, p=0.0001, PASS** |
| SECONDARY validation | not applicable | VACANT (no E1-E3 in cascade) |
| §7 verdict | **PAPER 2 INVALID** | **PAPER 2 PARTIAL REPLICATION** |

Both verdicts are pre-reg-honest. The differential between them is the diagnostic-driven Gate I amendment locked at literature/30 commit `3ad6c5c`, filed BEFORE re-running.

## 1. What the amendment changed (capsule)

Original Gate I (literature/28 §3): blanket CV < 0.30 across cells in ≥3 of 4 cohorts.

Amended Gate I (literature/30): category-specific stability:
- **Slope-like operators** (T1-T5, C1, CE1): bootstrap rank-stability, median Spearman ρ ≥ 0.50 across 1000 cell-re-sample bootstraps
- **Level-like operators** (E1, E2, E3, C2, D1): CV < 0.30, with IQR/|median| < 0.30 fallback when t-stat on |mean| < 10

Trigger (per literature/30 §0): CV = SD / |mean| is mathematically ill-defined on trajectory-slope distributions whose pooled mean lands near zero. Severson T1 CV = 30.28 not because the operator is noisy, but because the cohort spans 1C-8C fade rates so the pooled mean ≈ 0. The pathology is identifiable from cohort design alone, independent of which operators failed Gate I.

The amendment passed all 5 falsification-resistance checks in literature/30 §5: trigger does not refer to operator outcomes; replacement metrics are operator-neutral; threshold ρ ≥ 0.50 is a standard non-parametric anchor set ex ante; family partition (slope vs. level) is derivable from operator definitions in literature/27 alone.

## 2. Gate I v2 per-operator detail

Run via `code/paper2_gate_I_v2.py`. Bootstrap rank-stability ρ_median for slope-like; CV-or-IQR-fallback for level-like.

| Operator | Family | SECL | Khan | Zhang | Sevn | Pass/n | Gate I v2 |
|---|---|---|---|---|---|---|---|
| **T1 Q-fade-early** | slope | 0.997 | 0.999 | 0.994 | 1.000 | 4/4 | **YES** |
| **T2 Q-fade-late** | slope | -- | 0.999 | 0.994 | 1.000 | 3/3 | **YES** |
| **T3 Q-knee-onset** | slope | 1.000 | -- | 0.994 | 1.000 | 3/3 | **YES** |
| **T4 R-DC-growth** | slope | 1.000 | 0.999 | 0.994 | 1.000 | 4/4 | **YES** |
| **T5 R-DC-accel** | slope | -- | 0.999 | 0.994 | 1.000 | 3/3 | **YES** |
| **C1 R-growth/Q-lost** | slope | -- | 0.999 | -- | 1.000 | 2/2 | **YES** |
| CE1 coulombic-drift | slope | -- | -- | -- | 1.000 | 1/1 | NO (only 1 cohort with data) |
| **E1 ohmic-intercept** | level | 0.169 | 0.093 | 0.145 | -- | 3/3 | **YES** |
| E2 charge-transfer | level | 0.239 | 0.388 | 0.200 | -- | 2/3 | NO (Khan fails CV<0.30) |
| E3 diffusion-slope | level | -- | -- | -- | -- | 0/0 | NO (no data) |
| **C2 R_DC/R_total** | level | 0.016 | 0.108 | 0.290 | -- | 3/3 | **YES** |
| D1 dQdV peak-shift | level | -- | -- | -- | -- | 0/0 | NO (no data) |

**Attrition mechanisms under amended Gate I:**
- CE1, D1, E3: dropped via data unavailability (extraction infrastructure gaps), same as strict pre-reg. The amendment cannot resurrect data that does not exist.
- E2: dropped via genuine cross-cohort instability under the level-like criterion (Khan CV=0.388, Zhang CV=0.200; only 2 of 3 cohorts with data passed CV<0.30, needed 3 of 3).
- T1-T5, C1, C2, E1: passed under amended Gate I where they had failed under strict pre-reg.

**Methodological observation (honest, not a critique of the amendment):** the bootstrap rank-stability ρ_median values are uniformly very high (0.994-1.000) for slope-like operators. This is because rank ordering under cell re-sampling is intrinsically concordant for continuous-valued operators across cohorts of n ≥ 8 cells — the test is permissive. The threshold ρ ≥ 0.50 set ex ante in literature/30 §2.1 sits well below the empirical median. A future-pre-reg might tighten the threshold or substitute a different stability concept (e.g., split-half rank concordance). The current threshold remains the one locked at commit `3ad6c5c`.

## 3. Gate II v2 per-operator detail

Run via `code/paper2_gate_II_v2.py`. Gate II procedure unchanged from literature/28 §4. Inputs: 8 amended-Gate-I survivors.

| Operator | Category | PyBaMM | Khan | Severson | Pass/n | Gate II v2 |
|---|---|---|---|---|---|---|
| **T1 Q-fade-early** | Capacity traj | 1.000 | 0.893 | 0.694 | 3/3 | **YES** |
| **T2 Q-fade-late** | Capacity traj | 0.760 | 0.941 | 0.729 | 3/3 | **YES** |
| **T3 Q-knee-onset** | Capacity traj | 0.812 | -- | 0.729 | 2/2 | **YES** |
| **T4 R-DC-growth** | Impedance traj | 0.863 | 0.726 | 0.771 | 3/3 | **YES** |
| **T5 R-DC-accel** | Impedance traj | 0.777 | 0.912 | 0.794 | 3/3 | **YES** |
| **C1 R-growth/Q-lost** | Cross ratio | 0.677 | 0.971 | 0.731 | 3/3 | **YES** |
| **C2 R_DC/R_total** | Cross ratio | 1.000 | 0.971 | -- | 2/2 | **YES** |
| E1 ohmic-intercept | EIS spectral | -- | 1.000 | -- | 1/1 | NO (only Khan has EIS) |

7 of 8 amended-Gate-I survivors pass amended Gate II. The lone dropout E1 fails for the same mathematical reason as in literature/29: PyBaMM and Severson lack EIS data, so E1 can be tested on only 1 of 3 Gate II cohorts; 2-of-3 requirement is mathematically unreachable.

E1 had Khan AUC=1.000 (perfect aging-condition separation), confirming literature/29's observation that E1 is genuinely an excellent operator that the cross-cohort coverage requirement cannot validate.

## 4. Cascade v2 + PRIMARY validation

Run via `code/paper2_cascade_v2.py`. Architecture locked at literature/28 §5: RandomForestClassifier(n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced', random_state=42).

**Training data:** PyBaMM-train (n=70) + Khan (n=19) + Severson (n=139) = 228 cells × 7 amended-Gate-II-surviving operators. Target = pooled multinomial across 14 cohort-specific design-condition classes:
- PyBaMM: 9 classes by L9 cond_idx (8 cells per class, 7 in 2 classes due to seed split)
- Khan: 2 classes by aging_type (calendar n=5 / cycle n=14)
- Severson: 3 classes by first_step_C tertile (T1 n=46, T2 n=37, T3 n=56)

NaN imputation: 158 of 1596 cells × operators were NaN (data unavailability per cohort), imputed via cohort-mean. Features standardized. Stratified 5-fold CV.

**Cascade performance:**
- 5-fold out-of-fold accuracy: **0.684** (chance = 1/14 ≈ 0.071)
- Train accuracy: 0.882 (gap from OOF accuracy = 0.198 = expected RF over-fitting margin at this depth)

**Variable importance (RF impurity-based):**

| Operator | Importance |
|---|---|
| C2_R_DC_to_R_total | 0.2700 |
| T1_Q_fade_early | 0.1991 |
| T4_R_DC_growth_rate | 0.1584 |
| T5_R_DC_acceleration | 0.1381 |
| T2_Q_fade_late | 0.1231 |
| T3_Q_knee_onset | 0.0585 |
| C1_R_growth_per_Q_lost | 0.0527 |

C2 (cross-operator ratio R_DC / R_total) is the dominant cascade input, followed by capacity-trajectory T1 and impedance-trajectory T4-T5. Capacity-trajectory T2-T3 and cross-ratio C1 contribute less but non-zero.

**PRIMARY validation (PyBaMM-holdout, n=36, L9 cond_idx labels):**

Applied trained cascade to PyBaMM-holdout. Leaf-indices matrix projected via PCA (10 components, explained variance ratio [0.666, 0.128, 0.068, 0.027, 0.022, ...]). PERMANOVA on PCA embedding labeled by L9 cond_idx.

- **pseudo-F = 57.259** (df_between = 8, df_within = 27)
- **permutation p (10,000 perms) = 0.0001**
- Pre-reg §7 PASS criterion: F > 3.0 AND p < 0.05 → **PASS** (single primary test per literature/28 §10 first amendment, no Bonferroni)

**SECONDARY validation (WMG, n=19, terminal SOH labels):**

Per literature/28 §10 first amendment: "Cascade is restricted to its EIS-spectral surviving operator subset (whichever of E1, E2, E3 passed Gate I and II)."

Under amended protocol: zero of E1-E3 passed Gate II (E1 failed cohort-coverage; E2 failed Gate I; E3 had no data anywhere). **SECONDARY VALIDATION IS VACANT** by the literal reading of the §10 amendment.

This vacancy is a structural limitation of the operator catalog vs. WMG's snapshot-only data: WMG only carries EIS-derived operators (E1, E2, C2 in its parquet), and the EIS-derived operators that survived selection are not in the {E1, E2, E3} restriction.

## 5. Exploratory commentary (OUTSIDE pre-reg)

The amendment did not anticipate C2's survival to Gate II as a non-E1-E3 EIS-derived operator. C2 = R_DC / R_total is mechanistically EIS-derived (both numerator and denominator come from impedance measurements), and is computable on WMG (mean 0.929, sd 0.025, range [0.872, 0.971] across n=19).

A future-pre-reg amendment might broaden the WMG SECONDARY restriction from "E1-E3" to "any EIS-derived survivor" to admit C2. Filing such an amendment now, post-result, would be result-driven and is explicitly DECLINED.

Descriptive observation only: WMG soh_eis spans 80-95% with mean 87.4%. C2's range [0.872, 0.971] hints at signal but lacks a pre-registered analysis path under the current §10 amendment chain.

## 6. What this proves

**Pre-reg-honest finding 1 — strict pre-reg verdict (literature/29):** Under blanket CV<0.30 Gate I, Paper 2 is INVALID. The CV metric is incompatible with trajectory-slope operators on cohorts with bidirectional aging-rate variation. This is the strict pre-reg-locked result and remains the headline finding.

**Pre-reg-honest finding 2 — amended pre-reg verdict (this doc):** Under category-specific stability tests (rank-stability for slope-like; CV/IQR for level-like), 7 of 12 operators survive selection and the resulting RF cascade discriminates PyBaMM-holdout L9 conditions at pseudo-F = 57.26, p = 0.0001 (PARTIAL REPLICATION; SECONDARY vacant).

**Both findings stand.** The proper way to cite Paper 2 in downstream work is: "Under the locked CV-based Gate I (literature/28 §3), Paper 2 is INVALID and the cascade does not train (literature/29). Under the diagnostic-driven amendment replacing CV with category-specific stability (literature/30), the cascade trains on 7 operators and achieves a primary-holdout F = 57.26, p = 0.0001 (literature/31)."

## 7. Caveats and what this does NOT prove

**Caveat 1 — PRIMARY validation is within-substrate, not cross-substrate.** The PRIMARY test of F=57.26 is computed on PyBaMM-holdout (n=36 from the same L9 design and same simulator as the n=70 training cells). This is "does the cascade generalize to unseen synthetic cells of the same design"; it is NOT "does the cascade generalize to real-cell substrates." The original literature/28 had WMG as PRIMARY (cross-substrate); the literature/28 §10 first amendment swapped this to PyBaMM-holdout because WMG's trajectory operators are non-extractable. The PyBaMM-holdout result is therefore a within-substrate generalization claim, and F=57.26 may be inflated by the close distributional match between train and holdout splits.

**Caveat 2 — Rank-stability test is permissive.** All slope-like operators had ρ_median in [0.994, 1.000]. The locked threshold ρ ≥ 0.50 is far below the empirical floor; effectively any slope-like operator with continuous cell-level variation passes. This is the test as locked in literature/30 §2.1 — not a result-driven critique, but an honest observation that future iterations could tighten.

**Caveat 3 — SECONDARY is vacant, not failed.** The WMG cross-substrate generalization test was not run because no E1-E3 operator made it through Gate II. We have no evidence either for or against true cross-substrate generalization. This is a coverage gap in the operator catalog vs. WMG's measurement modality, not a result.

**Caveat 4 — The Paper 1 noise-injection finding (Probe 6, literature/26) still applies.** That finding established that the synthetic-vs-real-cohort gap is explained by instrumentation noise at typical academic levels. The amended cascade trains on a mix of synthetic (PyBaMM-train) and real (Khan, Severson) cohorts; its F=57.26 on PyBaMM-holdout reflects the cascade's ability to memorize synthetic-design structure on synthetic data, not necessarily its real-cell discrimination capacity.

**This does NOT prove:** the noise-robust framework discriminates AI-generated cell distributions from real cell distributions; the cascade transfers to substrates not in the training mix; trajectory operators T1-T5 are real-cell-validated (Probe 6 established the noise threshold below which they collapse).

## 8. Recommended citation framing

For methodology-corpus integration (alongside cancer / physics_detector / NFL / Sharks / etc.):

> "Battery substrate Paper 2 (noise-robust operator-cascade framework, literatures 27-31): under the locked CV-based Gate I, the cascade is INVALID — no operators survive both gates (literature/29). Under a diagnostic-driven amendment replacing CV with category-specific stability metrics (literature/30, falsification-resistance-checked), the cascade trains on 7 of 12 operators and achieves PARTIAL REPLICATION on the PyBaMM-holdout PRIMARY (F=57.26, p=0.0001) with the WMG SECONDARY vacant due to operator-coverage gaps. Both verdicts stand. The methodological lesson is that blanket dispersion metrics (CV, IQR) are ill-suited to mixed slope-and-level operator catalogs; future cascade selection should category-stratify ex ante."

This is the cancer-substrate honest-conditional framing applied to the battery substrate. The contingency is documented, the strict-pre-reg verdict is preserved, the amended verdict is reported alongside, the methodological caveats are explicit. Readers can audit and replicate.

---

## Outputs

- `code/paper2_gate_I_v2.py` — amended Gate I (rank-stability + CV/IQR fallback)
- `code/paper2_gate_II_v2.py` — Gate II (unchanged logic) on amended survivors
- `code/paper2_cascade_v2.py` — RF cascade + PCA embedding + PERMANOVA on PyBaMM-holdout
- `data/processed/paper2_gate_I_v2_results.parquet` — Gate I v2 per-operator metrics
- `data/processed/paper2_gate_II_v2_results.parquet` — Gate II v2 per-operator AUCs
- `data/processed/paper2_cascade_v2_summary.pkl` — cascade summary (CV acc, variable importance, PRIMARY F + p, verdict)
- `data/processed/paper2_cascade_v2_importances.parquet` — RF variable importance

---

**Locked at commit:** `d3b1662` on `main`, pushed to `origin/main` 2026-05-22.

Companion documents:
- literature/27 (operator catalog pre-reg, commit `13e9f80`)
- literature/28 (selection pre-reg + amendments `7fae62a`, `153fbd3`, `3ad6c5c`)
- literature/29 (strict-pre-reg PAPER 2 INVALID, commit `2ffb513`)
- literature/30 (diagnostic-driven Gate I amendment, commit `3ad6c5c`)
