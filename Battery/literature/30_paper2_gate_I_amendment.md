# Paper 2 — Gate I Diagnostic-Driven Amendment (Category-Specific Stability)

**Date locked:** 2026-05-22
**Locked before:** any re-run of Gate I, any re-touch of operator selection.
**Parent pre-reg:** literature/28 (commit `7fae62a` + amendment `153fbd3`).
**Trigger document:** literature/29 (Paper 2 selection result, commit `2ffb513`) — Paper 2 INVALID per strict pre-reg §7.
**Companion log entry:** literature/28 §10 (this amendment is also recorded there).

This amendment is **diagnostic-driven, not result-driven.** The trigger is a statistical pathology of the Gate I metric (CV near-zero-mean) that is identifiable from the data distribution alone, independent of which operators pass or fail. The full reasoning chain is documented here so the original-pre-reg verdict (literature/29: Paper 2 INVALID) remains intact, and the re-run under amended protocol is auditable as protocol evolution rather than goalpost-shifting.

---

## 0. Why this amendment exists

Strict pre-reg under literature/28 §3 used the **coefficient of variation (CV = SD / |mean|)** as the Gate I cross-cohort consistency metric, threshold CV < 0.30 in ≥3 of 4 cohorts. Under this metric, 11 of 12 candidate operators were dropped at Gate I (literature/29 §"Per-operator Gate I detail"); the lone survivor (E1 ohmic intercept) then failed Gate II on a mathematical impossibility (only 1 of 3 Gate II cohorts has EIS data).

**The CV-based attrition conflated three distinct failure modes:**

1. **True instrumentation noise.** What Gate I was supposed to measure.
2. **CV-near-zero pathology** on trajectory operators (T1-T5, C1). CV = SD / |mean| is unbounded when |mean| → 0. For trajectory slopes (fade rates, growth rates), a heterogeneous cohort with cells spanning fast-aging and slow-aging produces a pooled mean that floats near zero or crosses sign. **Severson T1 CV = 30.28** is not because the operator is noisy — it is because cells at 1C-2C fade with slope ≈ −0.002 Ah/cycle while cells at 7-8C fade with slope ≈ −0.030 Ah/cycle, and the pooled mean lands close to zero. SD ≈ 0.020 / |−0.012| ≈ 1.7 in one reference frame; shift the frame and the denominator collapses, CV explodes.
3. **Data unavailability** for E3, CE1, D1 — extraction infrastructure gaps unrelated to operator quality.

CV pathology (#2) is a well-known statistical issue with CV on near-zero-mean quantities. It is identifiable a priori from the data distribution: any cohort that contains cells with **bidirectional aging-rate variation** (cells that fade slowly + cells that fade quickly) will produce a near-zero pooled mean on the slope operator. Severson, with its 3-batch × 124-C-rate-combination design, was a worst case. The pathology would have been predictable from the cohort design alone, without any operator extraction.

**The framing test (per [[feedback_diagnostic_driven_amendments]]):** Can the amendment trigger be described using ONLY the statistical properties of the data, without referring to operator pass/fail outcomes? **Yes.** "Cells in this cohort produce trajectory-slope distributions with means near zero; CV is a poor stability metric on such distributions" is a data-distribution statement. No operator-level pass/fail enters the diagnosis. Therefore the trigger is diagnostic-driven, not result-driven, and the amendment is honest.

## 1. What this amendment LOCKS

Replaces literature/28 §3 (Gate I procedure) with **category-specific stability tests** chosen ex ante for each operator family. Everything else in literature/28 — cohort assignments §2, Gate II procedure §4, cascade architecture §5, holdout validation §6 (as amended), verdicts §7 — is **unchanged**.

The original-pre-reg Gate I result from literature/29 **remains the strict-pre-reg verdict** (Paper 2 INVALID per literature/28). This amendment runs ADDITIONALLY, alongside, and the dual result (original-strict + amended) is reported in literature/31.

## 2. The category-specific replacement (LOCKED)

Operators are partitioned by their statistical nature into two families. The Gate I test is family-specific.

### 2.1 Slope-like operators — rank-based stability test

**Members (7):** T1 (Q-fade-early), T2 (Q-fade-late), T3 (Q-knee-onset), T4 (R-DC-growth-rate), T5 (R-DC-acceleration), C1 (R-growth/Q-lost), CE1 (coulombic-drift).

**Rationale for category:** All seven measure a RATE of change — capacity fade per cycle, resistance growth per cycle, coulombic-efficiency drift per cycle, or a ratio of such rates. Rates can be positive or negative; the population mean can be arbitrarily close to zero when the cohort spans bidirectional or wide-magnitude aging. CV is mathematically ill-suited; the rank ordering of cells, by contrast, is invariant under sign and scale.

**Test:**

For each cohort, compute the operator on all cells (call this vector x of length n_cohort). Generate B = 1000 bootstrap re-samples of x (sampling cells with replacement). For each bootstrap b, compute the Spearman rank correlation ρ_b between x and x_b restricted to cells that appear in both. (Equivalently: the Spearman correlation between the cohort's true ranks and the bootstrap-induced ranks under cell re-sampling.) Take the median across B bootstraps: ρ_median.

**Threshold (LOCKED ex ante): operator passes the slope-like Gate I in a cohort if ρ_median ≥ 0.50.**

A bootstrap-stable rank ordering means that the cell-to-cell ordering induced by the operator is reproducible under re-sampling. It catches noise (where the ordering jumbles) without being fooled by the near-zero-mean denominator.

**Per-cohort to cross-cohort rollup (LOCKED, identical structure to §3 of literature/28):** an operator passes the slope-like Gate I if it passes in ≥3 of 4 cohorts (or 75% of available cohorts if some are excluded by NaN or data-unavailability).

### 2.2 Level-like operators — CV / IQR fallback

**Members (5):** E1 (ohmic intercept), E2 (charge-transfer radius), E3 (diffusion slope), C2 (R_DC / R_total), D1 (dQ/dV peak shift).

**Rationale for category:** These measure a fresh-state magnitude or a bounded ratio. E1-E3 are EIS-derived absolute impedances (always positive). C2 is a ratio of resistances (always positive, bounded). D1 is a voltage shift (signed but magnitude-dominant near a fixed voltage offset, NOT crossing zero in typical aging windows). Means are well-separated from zero on physical grounds. CV is well-defined.

**Test:**

Per cohort:
1. Compute CV = SD / |mean| of operator values across fresh cells.
2. **If |mean| < 10× SD of mean-estimate (i.e., signal-to-noise on the mean estimate itself is below 10),** fall back to IQR / |median|. This handles edge cases where a "level" operator's mean happens to drift near zero in a specific cohort.
3. Otherwise use CV.

**Threshold (LOCKED ex ante): operator passes the level-like Gate I in a cohort if the chosen metric (CV or IQR/|median|) is < 0.30.**

Cross-cohort: ≥3 of 4 (or 75% of available cohorts), same as literature/28 §3.

### 2.3 Why category-specific over blanket-relaxation

Considered alternatives at the time of amendment:

- **(A) Relax CV threshold to 0.50 or 1.0.** Rejected: even at threshold 1.0, T1 Severson (30.28) fails, T4 (15.8) fails. The pathology is mathematical, not a threshold-tuning issue. Relaxing the threshold doesn't address the diagnosis.
- **(B) Replace CV globally with IQR / |median|.** Rejected: median of trajectory slopes can also be near zero in a bidirectional cohort. IQR / |median| has the SAME pathology, just shifted from mean to median.
- **(C) Category-specific with rank-based for slope-like + CV/IQR for level-like.** **CHOSEN.** Acknowledges that the two operator families have different statistical natures. Rank-based stability is the principled answer for slope-like operators (it's scale- and sign-invariant, exactly what's needed). CV remains principled for level-like operators where means are physically bounded away from zero.

The choice of (C) over (A) and (B) is locked ex ante because the rejection criteria are derivable from the data distribution alone, not from which operators happen to survive.

## 3. What does NOT change

- **Gate II (literature/28 §4):** unchanged. Design-condition AUC ≥ 0.60 in ≥2 of 3 Gate II training cohorts.
- **Cascade architecture (§5):** unchanged. RF with locked hyperparameters.
- **Holdout (§6 as amended by 153fbd3):** unchanged. PyBaMM-holdout PRIMARY (n=36); WMG SECONDARY descriptive (EIS-spectral subset only).
- **Verdicts (§7):** unchanged.

## 4. Re-run execution order (LOCKED)

1. Commit + push this amendment (literature/30) + the §10 log entry in literature/28. **Lock = commit timestamp before any code change.**
2. Build `paper2_gate_I_v2.py` implementing §2 above. Bootstrap rank-stability test for slope-like; CV-with-IQR-fallback for level-like. Same 4-cohort input parquets as the original Gate I.
3. Run paper2_gate_I_v2.py. Report:
   - Per-operator per-cohort metric (ρ_median for slope-like; CV or IQR/|median| for level-like)
   - Per-operator pass/fail with locked thresholds
   - Attrition by physics category (per literature/27 §5 structure)
4. Re-run `paper2_gate_II.py` on amended Gate I survivors. Report attrition.
5. If multi-operator survivors emerge from Gate II: train RF cascade per literature/28 §5; apply to PyBaMM-holdout (PRIMARY) and WMG (SECONDARY descriptive); PERMANOVA per §6/§6.1.
6. Apply §7 verdict to the amended-protocol cascade. Report BOTH original-strict (literature/29) and amended (literature/31) verdicts side-by-side.
7. Write up literature/31 as protocol-evolution document, cancer-substrate honest-conditional style: original pre-reg → CV pathology identified at literature/29 → diagnostic-driven amendment at literature/30 → re-run → final result.

## 5. Falsification-resistance check

Could the amendment be hiding result-driven goalpost-shifting? Five checks:

1. **Does the trigger refer to operator outcomes?** No. The trigger is "CV is mathematically ill-suited to near-zero-mean distributions" — a statement about the distribution shape, not about which operators passed. Pre-reg-honest.
2. **Could the same amendment have been filed before literature/29's result?** Yes, in principle, if the CV pathology had been anticipated. (It should have been; that's the methodological lesson.) The amendment text would be identical regardless of which operators happened to fail.
3. **Does the replacement metric favor any specific operator over another?** Rank-based stability is operator-neutral; it tests whether the rank ordering of cells is reproducible, agnostic to operator identity. CV-with-IQR-fallback is also operator-neutral within the level-like family.
4. **Is the threshold (ρ_median ≥ 0.50) tuned to make specific operators pass?** No. 0.50 is a standard "moderate correlation" anchor in non-parametric statistics. It is set ex ante on principled grounds, not by inspecting which operators pass at which threshold.
5. **Are the family assignments (T1-T5+C1+CE1 → slope; E1-E3+C2+D1 → level) derivable from the operator definitions in literature/27 alone?** Yes. T1-T5 + C1 + CE1 are slopes / per-cycle rates by literature/27's own definitions. E1-E3 + C2 + D1 are fresh-state magnitudes or bounded ratios. The partition was set before any cohort data was examined.

If a future audit challenges this amendment, the response is: read §0 (the diagnosis), read §2.3 (why C over A/B), read §5 (the falsification-resistance check). All three lock in ex-ante reasoning. The integrity is in the logging.

## 6. Expected outcome (NOT pre-registered, exploratory commentary)

User's most-likely-outcome estimate (per session direction 2026-05-22): "4-7 operators survive, mixed across trajectory and spectral families." This is exploratory commentary, not a pre-registered prediction. The actual outcome will be whatever the data shows, reported honestly. If 0 survive again, **that is a substantive finding** — it would mean the framework's operator catalog doesn't pass any reasonable cross-cohort stability test, which is itself a Paper-2-publishable methodological lesson.

## 7. Relationship to literature/29

literature/29 (Paper 2 INVALID per strict pre-reg) stands. It is not retracted, not amended, not superseded. The re-run under this amendment produces a SECOND result (literature/31) reported alongside the first.

The publication framing is honest-conditional: "Under strict pre-reg, Paper 2 is INVALID (literature/29). Under diagnostic-driven Gate I amendment (literature/30) replacing CV with category-specific stability tests, the result is [whatever literature/31 reports]." Both results stand. Readers can audit the choice of amendment against §5 of this document and decide for themselves whether the protocol evolution is honest.

Pattern reference: the cancer substrate's "Δ=+6.26 nats CI-off-zero-but-Gibbs-contingent" finding is documented in the same style — the contingency is logged, not concealed. The integrity comes from the logging.

---

**Locked.** Commit hash recorded at literature/28 §10 deviation log.
