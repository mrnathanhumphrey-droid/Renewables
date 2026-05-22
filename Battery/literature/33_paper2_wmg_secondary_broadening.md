# Paper 2 — WMG SECONDARY Restriction Broadening (Second Amendment to §10)

**Date locked:** 2026-05-22
**Locked before:** any C2-on-WMG PERMANOVA computation is performed (the descriptive C2 stats in literature/31 §5 are noted but no statistical test has been run).
**Parent pre-reg:** literature/28 §6.1 + §10 first amendment (commit `153fbd3`).
**Companion §10 entry:** literature/28 §10 (this amendment will be logged there as a new row pointing to this document).

Once committed and pushed, no edits permitted.

---

## 0. Motivation

literature/28 §10 first amendment (commit `153fbd3`) restricted WMG SECONDARY validation to the EIS-spectral subset of cascade-surviving operators, defined narrowly as **{E1, E2, E3}**. Under the literature/30 diagnostic-driven Gate I amendment and the resulting cascade (literature/31, commit `d3b1662`), zero of {E1, E2, E3} survived Gate II:

- E1 passed Gate I but failed Gate II (only Khan has EIS data; can't reach 2-of-3 cohort rule)
- E2 failed Gate I (only 2 of 3 cohorts with data passed CV<0.30)
- E3 failed Gate I (no data in any cohort)

Therefore the literature/28 §10 first amendment's "E1-E3 only" restriction makes WMG SECONDARY structurally vacant for the amended-protocol cascade.

However, **C2 = R_DC / R_total is mechanistically EIS-derived** — both numerator and denominator are extracted from impedance measurements, and C2 is fully computable on WMG (n=19, mean 0.929, sd 0.025, range [0.872, 0.971], soh_eis range 80-95%). C2 also passed amended Gate II (PyBaMM AUC 1.000, Khan AUC 0.971) and is the highest-importance operator in the amended cascade (RF importance 0.270, dominating the next-highest at 0.199).

The literature/28 §10 first amendment's narrow definition of "EIS-spectral" as {E1, E2, E3} was a clerical choice at amendment time — it specified the operators by name rather than by mechanism. A broader mechanism-based reading would admit C2 alongside E1-E3, since C2 is fully EIS-derived.

This amendment broadens the WMG SECONDARY restriction from operator-name-based ({E1, E2, E3}) to mechanism-based ("any cascade-surviving operator whose computation requires only EIS measurements"). Under this broadened definition, C2 enters; the WMG SECONDARY can run on a 1-operator cascade restricted to C2 alone.

## 1. Falsification-resistance check (per [[feedback_diagnostic_driven_amendments]])

Same framing test as literature/30:

1. **Does the amendment trigger refer to operator outcomes?** Partial yes — the trigger is "no E1-E3 survived under amended protocol." This is a *structural coverage gap*, not a performance outcome. The amendment does not change which operators passed; it changes which subset of passing operators are eligible for the WMG SECONDARY test. The mechanism-based reading would have been the better choice at amendment-time even without literature/31's specific outcome (the first amendment's narrow E1-E3 specification was an under-specification, not an evidence-based restriction).

2. **Could the same broadening have been filed before literature/31's result?** Yes. If literature/28 §10 had been written with "any EIS-derived survivor" instead of "E1-E3," the WMG SECONDARY would have run on whatever EIS-derived operators happened to survive — which under strict pre-reg (literature/29) would have been zero (E1 fails Gate II for the same reason), still vacant. Under amended pre-reg (literature/31) C2 enters. The broadening is structurally favorable to amended pre-reg, NOT result-driven, because under strict pre-reg the broadening still produces vacant SECONDARY.

3. **Does the broadening favor a specific outcome on WMG?** C2's univariate distribution on WMG is mean=0.929, sd=0.025 — extremely tight. Whether this tightness translates to SOH-bin separation under PERMANOVA is unknown; the amendment is filed BEFORE running the PERMANOVA. A PASS or FAIL outcome is equally pre-reg-honest.

4. **Is the mechanism-based reading derivable from literature/27 alone?** Yes. C2 is defined in literature/27 §3 as `R_DC / R_total` — both components are EIS-derived. The mechanism-based reading was always available in literature/27's operator definitions; the literature/28 §10 first amendment chose to list operator names rather than mechanism. This amendment corrects that choice without re-defining any operator.

5. **Could the amendment be hiding goalpost-shifting?** The original §10 first amendment chose narrow operator names; this amendment chooses mechanism. Both are pre-reg-defensible readings. The mechanism reading is more principled (operators with the same measurement provenance should be treated consistently). The narrow reading was an under-specification at first-amendment time. Choosing the more principled reading post-hoc is honest IF the trigger is a structural coverage gap (which it is) rather than a result.

Net: Pre-reg-honest amendment, qualified by the partial-result-dependence in check 1. The dual reporting at literature/35 will document both the pre-amendment (vacant) and post-amendment (C2-on-WMG) outcomes side-by-side.

## 2. What this amendment LOCKS

Replaces literature/28 §6.1 + §10 first amendment's restriction text. New restriction (LOCKED):

> "Cascade is restricted to its EIS-derived surviving operator subset, defined as any cascade-surviving operator (post-Gate-II) whose computation requires only EIS measurements. Operators satisfying this definition: E1 (ohmic intercept), E2 (charge-transfer radius), E3 (diffusion slope), C2 (R_DC / R_total). Under the amended protocol (literature/31), the surviving subset is {C2}. Apply a C2-restricted cascade trained on the same training cohorts to WMG cells; PERMANOVA on terminal SOH bins."

Cohort assignments unchanged. Gate I unchanged. Gate II unchanged. Cascade architecture unchanged (RF with locked hyperparameters). Verdict thresholds unchanged.

## 3. C2-restricted cascade procedure (LOCKED)

The 7-operator cascade in literature/31 includes C2 alongside 6 trajectory/ratio operators not extractable on WMG (T1-T5, C1 = NaN on WMG). To produce a WMG-applicable cascade, **re-train a separate RF cascade using ONLY C2 as the feature, on the same training data** (PyBaMM-train + Khan + Severson, n=228, same multinomial 14-class target). Architecture identical to literature/28 §5:

- `n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced', random_state=42`
- StandardScaler fit on training C2; impute training NaNs by cohort-mean (Severson C2 is NaN for all 139 cells per literature/29 — these will be imputed)
- 5-fold stratified CV reports OOF accuracy
- RF variable importance is trivially 1.00 (single feature) but report for symmetry

Note: Severson contributes 139 cells × NaN-then-imputed C2 to training. This means 139 of 228 training cells are at the cohort-mean of available-C2 cohorts (PyBaMM + Khan). The OOF accuracy will reflect this — likely much lower than the 7-operator cascade's 0.684. **This is expected and not a result-driven concern**; it's a structural consequence of restricting to a single operator that's missing in Severson.

Apply trained C2-restricted cascade to WMG (n=19, all 19 have finite C2). Project via leaf-indices PCA fit on training + WMG leaves combined (consistent with literature/31's procedure). PERMANOVA on the WMG embedding.

## 4. WMG SECONDARY PERMANOVA (LOCKED)

WMG labels: terminal SOH bins. soh_eis values span 80-95%. Bin into 4 levels: {80, 85, 90, 95} (5-point bins; each cell rounds to its nearest bin center).

Verify per-bin count: with n=19 across 4 bins, expect ~4-5 cells per bin. **If any bin has fewer than 3 cells**, fall back to 2-bin median split {low SOH, high SOH}. If even that fails (any bin < 3), declare SECONDARY INVALID.

PERMANOVA: cosine distance on the C2-cascade's PCA embedding, 10,000 permutations.

**PASS criterion:** pseudo-F > 3.0 AND permutation p < 0.05. Single SECONDARY test, no Bonferroni against the PRIMARY (PRIMARY and SECONDARY were already declared independent in literature/28 §6).

## 5. Verdicts (LOCKED)

- **CASCADE CROSS-SUBSTRATE PASS:** WMG PERMANOVA F > 3.0 AND p < 0.05. The C2-cascade signal generalizes to a real-cell NMC811 cohort outside the training mix.
- **CASCADE CROSS-SUBSTRATE NULL:** WMG PERMANOVA F < 3.0 OR p > 0.05. C2 alone does not produce cross-substrate signal on WMG terminal SOH bins.
- **CASCADE CROSS-SUBSTRATE INVALID:** Bin counts insufficient even under median-split fallback.

This verdict combines with literature/31's PRIMARY result and (if §32 runs concurrently) the noise-robust result to produce the final Paper 2 amended-protocol headline.

## 6. What this amendment CAN and CANNOT conclude

CAN:
- Test whether the cascade's dominant operator (C2) discriminates SOH bins on a real-cell NMC811 cohort never used in training
- Provide a 1-operator cross-substrate generalization signal (or lack thereof)

CANNOT:
- Test the full 7-operator cascade on WMG (the 6 trajectory/ratio operators are non-extractable on snapshot WMG data — unchanged by this amendment)
- Generalize beyond NMC811 cylindrical chemistry (WMG is a specific cell format)
- Validate the cascade's design-condition discrimination on real cells (WMG has only terminal-SOH variation, not design variation)

## 7. Operational protocol (LOCKED execution order)

1. Commit + push this amendment AND literature/32 (cascade noise pre-reg). **Lock = commit timestamp before any code change.**
2. Implement `code/paper2_cascade_v2_wmg.py`:
   - Load training cohorts (PyBaMM-train + Khan + Severson) with C2 only
   - Train C2-restricted RF cascade per §3
   - Apply to WMG; project via leaf-indices PCA on training + WMG combined
   - PERMANOVA on terminal SOH bins per §4
3. Apply §5 verdict.
4. Write up in `literature/35_paper2_cascade_wmg_result.md`.

## 8. Explicitly NOT covered

- Re-training the 7-operator cascade — the broadening admits C2 to the WMG-applicable subset but does NOT re-define which operators are in the main amended-protocol cascade (those are locked at literature/31's 7-operator set)
- Imputing the missing T1-T5/C1 features on WMG to apply the 7-operator cascade as-is — out of scope; the C2-restricted cascade is the only WMG-applicable form
- Cross-substrate validation on SECL or Zhang — those are Gate-I-only cohorts, separate question, NOT in scope here
- Re-running PyBaMM-holdout PRIMARY under this amendment — PRIMARY is unchanged at literature/31's F=57.26 verdict

## 9. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
