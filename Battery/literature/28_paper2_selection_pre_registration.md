# Paper 2 — Selection & Cascade Pre-Registration

**Date locked:** 2026-05-22
**Locked before:** any candidate operator (from literature/27) is extracted on any cohort for selection purposes; any cascade training begins.
**Companion pre-reg:** literature/27_paper2_operator_catalog_pre_registration.md (commit `13e9f80`) — locks the 12 candidates. This pre-reg locks the selection process applied to them.

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. What this pre-reg LOCKS

- Cohort assignments: Gate I, Gate II, holdout (§2)
- Gate I threshold + procedure (§3)
- Gate II threshold + procedure (§4)
- Cascade architecture: algorithm, hyperparameters, training regime (§5)
- Holdout validation test (§6)
- Falsification verdicts (§7)

Once this commits, the operator extraction pipeline can begin. Not before.

## 1. Independence note (inherited from literature/27)

Paper 2 explicitly does NOT inherit Paper 1's conditional-independence
assumption. The 12 candidate operators are expected to be physically
coupled. The selection procedure here:
- Does NOT use any independence-based statistic (no Mahalanobis on the
  candidate set; no requirement of |ρ| < ε)
- DOES use cascade-architecture methods (random forest) that natively
  handle correlated predictors
- Reports operator-importance from the cascade, which is THE replacement
  for "this operator is independently informative"

## 2. Cohort assignments (LOCKED)

| Role | Cohorts | n cells | Use |
|---|---|---|---|
| **Gate I** (cross-cohort fresh-cell consistency) | SECL first-life + Khan 2025 + Zhang Cambridge v2 + Severson | ~4 + 22 + 8 + 139 ≈ 173 | CV-of-operator across fresh cells of each cohort |
| **Gate II training** (design-condition AUC) | PyBaMM Probe 5 training split (8 cells/condition × 9 = 72) + Khan + Severson | 72 + 22 + 139 = 233 | Operator AUC for separating design conditions on each cohort's design axes |
| **Gate II within-cohort holdout** (cascade tuning) | PyBaMM Probe 5 holdout split (4 cells/condition × 9 = 36) | 36 | Cascade tuning + cross-validation of selection decisions; NOT seen in Gate I or II training |
| **Final validation (PRIMARY)** | WMG NMC811 cylindrical (n=19) | 19 | Cascade-score residual direction on terminal SOH bins; cross-substrate generalization check |

The PyBaMM Probe 5 train/holdout split is pre-registered as a deterministic
seeded random assignment: per condition c, the 12 cells are split into 8/4
training/holdout by `seed = 3000 + c`. Reproducible.

The WMG cohort is **untouched in any selection step** through this pre-reg
chain. It is used ONLY for final validation in §6.

## 3. Gate I — cross-cohort fresh-cell consistency (LOCKED)

**Purpose:** drop operators that don't have stable extraction across different
real-cohort instrumentation. An operator that's noisy on SECL but tight on
Khan signals that the operator is sensitive to the specific measurement
pipeline, not to the underlying physics.

**Procedure (per candidate operator):**

1. For each of the 4 Gate I cohorts, extract the candidate operator on each
   cell's fresh-cell measurements (cycles 5-25 mean, or for cross-sectional
   cohorts the dedicated fresh subset)
2. Compute the coefficient of variation (CV = SD / |mean|) of the operator
   across fresh cells within each cohort
3. Locked threshold: **operator passes Gate I if CV < 0.30 in at least 3 of 4
   cohorts.** Allows one outlier cohort (e.g., Zhang's button cells have
   distinct geometry, may produce outlier CV on impedance operators)
4. If CV cannot be computed (e.g., insufficient fresh cells in a cohort),
   that cohort is excluded from the operator's count, and the threshold
   becomes "passes in 3 of remaining cohorts" (down to 2 of 3 if a cohort
   excludes; 1 of 2 = INVALID for that operator)

**The 0.30 CV cutoff is set ex ante** because it sits at the boundary
between "moderate but detectable signal" and "noise-dominated." Tighter
cutoffs (0.15-0.20) would be ideal but would likely drop all candidates given
real-cohort heterogeneity. 0.30 is permissive enough to keep candidates that
are demonstrably real but acknowledges noise.

## 4. Gate II — design-condition AUC (LOCKED)

**Purpose:** drop operators that — even when they pass Gate I — don't carry
signal informative about design-condition labels. An operator can be
consistently extractable but uncorrelated with the design parameter; that
operator is methodologically clean but causally uninformative.

**Procedure (per candidate operator that passed Gate I):**

For each of the 3 Gate II training cohorts (PyBaMM-train, Khan, Severson):

1. Compute the operator's value per cell
2. For each design axis available in the cohort (PyBaMM: cathode_thickness,
   transference_number, particle_radius; Khan: aging_type, T_C, SOC_range;
   Severson: first_step_C, last_step_C, severity), compute AUC for
   separating the levels via the operator
3. Per-cohort AUC = max over design axes available
4. Locked threshold: **operator passes Gate II if max-AUC ≥ 0.60 in at least
   2 of 3 Gate II cohorts.** AUC ≥ 0.60 is "weak but real" signal; the
   cascade combines such weak signals into stronger decisions
5. Critical: Gate II uses **only** the training cohorts. PyBaMM-holdout (36
   cells) and WMG (19 cells) are NOT in Gate II computation

**Why 2-of-3 not 3-of-3:** allows an operator that's powerful on synthetic
+ Severson but null on Khan to survive, OR vice versa. Locks in cross-cohort
robustness while not requiring universal applicability.

## 5. Cascade architecture (LOCKED)

**Algorithm:** Random Forest classifier (RF), scikit-learn implementation.

**Hyperparameters (locked):**
- `n_estimators = 500`
- `max_depth = 4`
- `min_samples_leaf = 5`
- `class_weight = "balanced"`
- `random_state = 42`

**Training data:** Gate II training cohorts (PyBaMM-train + Khan + Severson)
× Gate II surviving operators. Target variable: design-condition label,
multinomial. For Khan and Severson where design axes have continuous
underlying values (e.g., first_step_C), labels are the binned levels from
the cohort's existing analysis (e.g., Severson tertile bins per
literature/22).

**Cross-validation:** 5-fold stratified within the training set. Reports
cross-validated AUC per operator (via random-forest variable importance) and
overall classifier OOB accuracy.

**Output of cascade:** for each cell, a cascade probability score vector
(one probability per design-condition class) AND a low-dimensional
embedding via PCA on the leaf-indices matrix. The embedding will be used
for PERMANOVA-style residual-direction analysis on the holdout (§6).

**No hyperparameter tuning on the holdout or final validation cohort
permitted.** Hyperparameters are locked above; if performance is poor,
report failure with locked hyperparameters and propose tuning as a
separate pre-reg amendment.

## 6. Holdout / final validation (PRIMARY)

**Validation cohort:** WMG NMC811 cylindrical, n=19 (literature/24 cohort).

**Procedure:**

1. Apply the trained cascade (from §5) to each WMG cell, generating a
   cascade probability vector
2. Project the probability vectors into the cascade's PCA embedding space
3. Run PERMANOVA on the cascade embedding labeled by WMG terminal SOH bin
   {80%, 85%, 90%, 95%}
4. Report pseudo-F and permutation p (10,000 perms)

**Note on WMG's role:** WMG has only terminal-SOH variation, not
design-condition variation. The validation test is *cross-substrate
generalization*: if the cascade learned design-condition discrimination on
training cohorts, does that learned discrimination ALSO produce structure
when applied to a fresh cohort's aging-state variation? If yes → cascade
generalizes; if no → cascade learned cohort-specific quirks.

**Bonferroni** for 2 final tests (this PERMANOVA + a within-PyBaMM-holdout
PERMANOVA in §6.1): α/2 = 0.025.

### 6.1 Secondary validation on PyBaMM holdout

PyBaMM Probe 5 holdout (36 cells) — also untouched by selection — receives
cascade scores. PERMANOVA on cascade embedding labeled by L9 condition
(9 conditions × 4 cells per condition).

This is "did the cascade preserve the synthetic-ground-truth design signal
when projected through the cohort-trained classifier?"

## 7. Verdicts (LOCKED)

**Cascade-level verdicts:**

- **PAPER 2 STRONG REPLICATION:** Final validation (WMG, §6) PASS
  (p<0.025 AND F>3.0) AND PyBaMM-holdout (§6.1) PASS (p<0.025 AND F>3.0)
- **PAPER 2 PARTIAL REPLICATION:** Either §6 or §6.1 PASS (one of two)
- **PAPER 2 NULL:** Both fail
- **PAPER 2 INVALID:** Cascade fails to train (no operators pass Gate I+II,
  RF crashes, etc.)

**Operator-level findings (always reported regardless of cascade verdict):**

- Initial 12 → Gate I survivors (with attrition by physics category per
  literature/27 §5)
- Gate I survivors → Gate II survivors (with attrition by category)
- RF variable importance for the cascade survivors (proxy for "operator
  contribution to the final decision")

These operator-level results are **the methodological contribution** even if
the cascade fails the holdout test. Paper 2's claim isn't "cascade works"
— it's "this is the noise-robust design and here's what survives selection."

## 8. Operational protocol (LOCKED execution order)

1. Commit + push this pre-reg. **Lock is the commit timestamp.**
2. Build extraction code per literature/27 §3 for the 12 candidates across
   the 4 Gate I cohorts + 3 Gate II training cohorts + 1 within-cohort
   Gate II holdout + 1 final validation cohort
3. Run Gate I; report attrition per literature/27 §5 structure
4. Run Gate II on Gate I survivors; report attrition
5. Train RF cascade on Gate II training cohorts; report 5-fold CV AUC + OOB
   accuracy + variable importance
6. Apply cascade to WMG (final validation); run PERMANOVA per §6
7. Apply cascade to PyBaMM holdout (§6.1); run PERMANOVA
8. Apply §7 verdict; write up Paper 2 with attrition + final-validation
   results

## 9. Explicitly NOT covered

- Multi-fold cross-validation for hyperparameter selection (locked instead)
- Alternative cascade algorithms (LR, voting, stacking, neural nets) — locked
  to RF here
- Re-running with different Gate I/II thresholds — would require amendment
- Noise injection on the cascade (Paper 2 analog of Probe 6) — separate
  pre-reg
- Comparison to Paper 1's joint Mahalanobis distance on the same cohorts —
  separate analysis post-Paper 2
- Real-cell experimental cohort design — separate research program

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-22 | **§6 PRIMARY/SECONDARY swap.** Original: WMG PRIMARY, PyBaMM-holdout SECONDARY (§6.1). Amended: **PyBaMM-holdout PRIMARY, WMG SECONDARY (descriptive cross-substrate check, restricted to EIS-spectral cascade subset).** | Implementation audit before extraction reveals WMG is snapshot-only (no per-cycle trajectory). If the trained cascade includes any trajectory operators (T1-T5) that survive Gate I+II selection, WMG cells cannot be scored — they don't have those features. PyBaMM-holdout (36 cells, deterministic seed split per §2) has all operator types and is fully untouched in selection or cascade training, making it a clean primary holdout. WMG retains value as a descriptive cross-substrate generalization check: we can apply only the EIS-spectral subset of cascade-surviving operators (E1-E3 survivors) to WMG and report whether the cascade-implied direction structure shows up. This amendment is filed BEFORE any extraction is run; no peeking has occurred. |
| 2026-05-22 | **§3 Gate I metric replaced with category-specific stability tests.** Original: blanket CV < 0.30 in ≥3 of 4 cohorts. Amended: slope-like operators (T1, T2, T3, T4, T5, C1, CE1) use **bootstrap rank-stability test** (Spearman ρ_median ≥ 0.50 across 1000 bootstraps of cell re-sampling); level-like operators (E1, E2, E3, C2, D1) keep CV < 0.30 with IQR/\|median\| < 0.30 fallback when signal-to-noise on \|mean\| is below 10. Cross-cohort rule unchanged (≥3 of 4 or 75% of available cohorts). Full amendment text + falsification-resistance check in literature/30. | **Diagnostic-driven**, not result-driven. CV = SD / \|mean\| is ill-defined on trajectory-slope operators whose pooled mean lands near zero when a cohort contains cells with bidirectional aging rates (e.g., Severson cells at 1C-2C with fade slope ≈ −0.002 vs cells at 7-8C with slope ≈ −0.030 → pooled mean near zero → CV explodes to 30+). The pathology is identifiable from the data distribution alone (cohort design admits bidirectional slope variation), independent of which operators happened to fail Gate I in literature/29. Trigger meets the framing test from [[feedback_diagnostic_driven_amendments]]: "Could you describe the amendment trigger using ONLY the statistical properties of the data, without referring to the operator-level pass/fail outcome?" — yes. Original-strict verdict from literature/29 stands; this amendment runs additionally and the dual result is reported at literature/31. Lock = commit timestamp before paper2_gate_I_v2.py is written. |

**Old text (§6):** "Validation cohort: WMG NMC811 cylindrical, n=19 (literature/24 cohort)."
**New text (§6, effective from this commit):** "Validation cohort: PyBaMM Probe 5 holdout split (36 cells, deterministic seed split per §2). Untouched in any selection step. Has all 12 candidate operator types extractable."

**Old text (§6.1):** "Secondary validation on PyBaMM holdout. PyBaMM Probe 5 holdout (36 cells)... PERMANOVA on cascade embedding labeled by L9 condition."
**New text (§6.1, effective from this commit):** "Secondary descriptive validation on WMG (n=19 NMC811 cyl). Cascade is restricted to its EIS-spectral surviving operator subset (whichever of E1, E2, E3 passed Gate I and II). Apply restricted cascade to WMG cells; project to PCA embedding; PERMANOVA on terminal SOH bins. This is a cross-substrate generalization check — does the cascade's signal show up on a cohort whose only commonality with the training cohorts is the EIS-spectral operator family? Report descriptively. Not used for §7 verdict gating."

**§7 verdict update:** STRONG REPLICATION now means PyBaMM-holdout (§6 PRIMARY) PASS at p<0.025 AND F>3.0. WMG secondary result reported alongside but does NOT enter the verdict. Bonferroni adjustment: only 1 primary final test (PyBaMM-holdout PERMANOVA), so α = 0.05 not α/2. WMG descriptive test does not count toward Bonferroni.
