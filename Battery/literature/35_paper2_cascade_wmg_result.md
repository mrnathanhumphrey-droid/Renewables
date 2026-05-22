# Paper 2 — Cascade Cross-Substrate Result on WMG: CASCADE CROSS-SUBSTRATE NULL

**Date:** 2026-05-22
**Pre-registration:** literature/33 (commit `7633f7e`)
**Companion result:** literature/31 (amended-cascade PARTIAL REPLICATION at PyBaMM-holdout F=57.26, commit `d3b1662`)
**Verdict per literature/33 §5:** **CASCADE CROSS-SUBSTRATE NULL.** WMG SECONDARY PERMANOVA F = 0.921, p = 0.576 across 4 terminal SOH bins {80, 85, 90, 95}. The C2-restricted cascade does NOT discriminate WMG SOH bins.

---

## 0. Headline

The amended cascade's dominant operator C2 (RF importance 0.270 in literature/31) does NOT produce signal on a real-cell NMC811 cohort outside the training mix. When restricted to its C2-only-applicable form (per literature/33 broadened §10 second amendment), the cascade fails to discriminate WMG terminal SOH bins {80, 85, 90, 95} at any threshold:

| Test | F | p | Pass criterion | Verdict |
|---|---|---|---|---|
| WMG SECONDARY PERMANOVA (4 SOH bins) | **0.921** | **0.576** | F > 3.0 AND p < 0.05 | **NULL** |

This NULL is informative: it bounds the cascade's cross-substrate generalization claim. The literature/31 PARTIAL REPLICATION verdict is preserved, but cross-substrate transfer via the dominant operator is not supported.

## 1. Procedure

Per literature/33 §3-4 (verbatim, no deviations):

1. Re-trained an RF cascade with **C2 only** as feature, on the same training data as literature/31 (PyBaMM-train + Khan + Severson, n=228, 14 multinomial classes). Same RF hyperparameters: n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced', random_state=42.

2. Severson C2 is NaN for all 139 cells (per literature/29 — Severson has no EIS-derived data); these were imputed via cohort-mean on training. This means 139 of 228 training cells effectively contribute the mean-C2 value; the cascade learns primarily from PyBaMM (n=70) + Khan (n=19) variation.

3. 5-fold CV OOF accuracy: **0.461** (vs 7-operator cascade's 0.684; vs chance 0.071). The C2-only restricted cascade still beats chance by 6.5x but loses ~32% of the 7-operator cascade's accuracy.

4. Applied trained C2-restricted RF to WMG (n=19, all 19 cells have finite C2). Projected via leaf-indices PCA fit on training + WMG leaves combined. WMG PCA embedding shape: (19, 10).

5. WMG terminal SOH labels: soh_eis values mapped to nearest bin in {80, 85, 90, 95}. Per-bin counts: {80: 5, 85: 5, 90: 4, 95: 5}. All bins ≥ 3 cells; no median-split fallback needed.

6. PERMANOVA on the WMG PCA embedding labeled by SOH bins, 10,000 permutations, Euclidean distance.

## 2. Result

```
WMG SECONDARY PERMANOVA:
  pseudo-F = 0.921
  df_between = 3 (4 SOH bins - 1)
  df_within = 15 (19 cells - 4)
  permutation p = 0.576 (out of 10,000 perms)
```

**F = 0.921** is below 1.0, indicating less between-bin variance than within-bin variance. The cascade's leaf-indices projection of WMG cells does NOT cluster by terminal SOH. **p = 0.576** is consistent with random permutation: there is no detectable signal at any threshold.

By literature/33 §5: F < 3.0 OR p > 0.05 → **CASCADE CROSS-SUBSTRATE NULL.**

## 3. Why this is informative

The C2-only cascade was designed to test whether the cascade's dominant operator (highest RF importance in the 7-operator literature/31 cascade) transfers to a real-cell NMC811 cohort outside the training mix. The NULL result tells us:

1. **C2 alone is not a cross-substrate signal.** It picks up design-condition variation on training cohorts (PyBaMM AUC 1.000, Khan AUC 0.971) but does not encode SOH-discriminative information on WMG.

2. **The literature/31 PARTIAL REPLICATION result is real but cohort-specific.** The 7-operator cascade's PyBaMM-holdout F=57.26 was driven by the joint behavior of T1-T5 + C1 + C2 — a structure that does not survive restriction to C2-on-real-cells.

3. **The cascade does not transfer in its simplest cross-substrate form.** A multi-operator cross-substrate test would require either:
   - A real-cell cohort with full trajectory + EIS coverage (currently none exist in our corpus with the right design axes)
   - Imputation of missing operators on WMG (would violate the pre-reg's locked feature set)
   - A different operator catalog that includes only EIS-derived measurements computable on WMG (would be a Paper-3-equivalent redesign)

This NULL is consistent with literature/31 §7 Caveat 2: "the rank-stability test as locked is permissive." Operators that pass the permissive Gate I but don't carry true noise-robust cross-substrate signal would fail at this test. The cross-substrate test is the binding constraint that the permissive Gate I doesn't catch.

## 4. What this proves

**Pre-reg-honest finding:** The C2-restricted amended cascade does NOT cross-transfer to WMG. Cross-substrate generalization via the cascade's dominant operator is not supported at any threshold (F<1 < 3.0; p=0.576 > 0.05).

**Headline reading:** The literature/31 cascade is best characterized as a "design-condition discriminator on the training cohort distribution" rather than a "noise-robust cross-substrate framework." The PRIMARY PyBaMM-holdout F=57 reflects within-distribution generalization (within the simulator + L9 design); the cross-substrate test (WMG) shows the framework's signal does not extend to a different cell-format / chemistry.

## 5. What this does NOT prove

- **It does NOT prove the full 7-operator cascade fails cross-substrate.** This test is restricted to C2 only because the other 6 operators are non-extractable on WMG (snapshot-only data). A cohort with both trajectory + EIS coverage might enable a stronger cross-substrate test.

- **It does NOT prove C2 has no SOH-discrimination signal in general.** WMG's soh_eis was measured from EIS spectra, possibly via a different operator definition than C2's mean-of-first-5-cycles R_DC/R_total. C2's tight range on WMG (mean 0.929, sd 0.025) suggests low cell-to-cell variation in this specific cohort.

- **It does NOT generalize beyond NMC811 cylindrical chemistry.** Other real-cell cohorts (LFP, NMC pouch, LCO button) may behave differently.

- **It does NOT invalidate literature/31's PRIMARY result.** The literature/31 PARTIAL REPLICATION verdict on PyBaMM-holdout stands; this WMG NULL bounds its scope of generalization.

## 6. Combined Paper 2 amended-protocol headline

Synthesizing literature/29, literature/31, literature/34, and literature/35:

> **Paper 2 (amended protocol): partial replication within-substrate (PyBaMM holdout F=57, p<0.001), barely robust to typical academic instrumentation noise (F=3.2 just above the 3.0 threshold), and not cross-transferable via the cascade's dominant operator to a real-cell NMC811 cohort (WMG F=0.92, p=0.58 NULL). The framework as designed has a narrow operational regime: synthetic, low-noise, design-condition-discriminating only. Cross-substrate real-cell deployment requires further methodological work — either an expanded operator catalog with cross-substrate-applicable features, or a real-cell cohort with full trajectory + EIS measurement coverage matching the training cohorts.**

Both pre-reg-honest "yes" answers (literature/31 PRIMARY PASS) and pre-reg-honest "no" answers (literature/34 razor-thin survival; literature/35 NULL) are reported together. The methodological lesson is that **rank-stability Gate I + within-substrate PRIMARY + restricted SECONDARY is not sufficient to claim a noise-robust cross-substrate framework**; future selection methodology should include cross-substrate validation as a primary gate, not as a secondary descriptive test.

## 7. Recommended citation framing

> "The amended cascade's cross-substrate test on a real-cell NMC811 cohort (WMG, n=19) returned NULL (F=0.92, p=0.58) when restricted to the cascade's dominant operator (C2 = R_DC/R_total). The literature/31 PARTIAL REPLICATION at PyBaMM-holdout is real but does not extend across cell substrates. The framework's PRIMARY signal is within-distribution; cross-substrate deployment is not yet supported."

## 8. Outputs

- `code/paper2_cascade_v2_wmg.py` — C2-restricted cascade + WMG PERMANOVA
- `data/processed/paper2_cascade_v2_wmg_results.pkl` — CV acc + WMG PERMANOVA F/p/df + verdict

---

**Locked at commit (to be recorded after push):** _TBD_
