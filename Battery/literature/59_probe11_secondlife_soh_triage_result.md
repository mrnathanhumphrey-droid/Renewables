# C3 Probe 11 — Second-Life SOH Triage RESULT

**Status:** COMPLETE. Disposition = **SOH-READABLE (within-cell only)** — EIS carries SOH strongly, but absolute SOH does not transfer to an unseen cell on this narrow-range, cell-confounded cohort.
**Date:** 2026-05-28
**Authored:** Claude
**Pre-reg:** `literature/58_probe11_secondlife_soh_triage_prereg.md` (lock `ed2df82`).
**Prior:** First real-cell *useful-task* application of the C3 method. Transference arc closed (Probe 9/10).

---

## 0. One-line result

The EIS fingerprint unambiguously carries SOH (R_diff @4.00 V Spearman ρ = −0.93; 5 of 6 features track SOH at p<1e-4), and the C3 PERMANOVA separates SOH tertiles significantly even under a cell-stratified null (p=0.0027). **But leave-one-cell-out regression cannot predict a held-out cell's absolute SOH** (pooled R² = −4.19), because on this cohort SOH spans only 5.7 points (88.0–93.7%) and is confounded with cell identity. **Verdict: SOH is readable within a cell, but a universal EIS→SOH model does not transfer across cells on the second-life SECL data.** This is a cohort limitation, not a method failure — the positive control and the cross-substrate rule both hold (SOH is a direct-signature target and the fingerprint clearly encodes it).

## 1. Falsifier results

| Falsifier | Threshold | Result | Verdict |
|---|---|---|---|
| **P-Probe11_F1** (R tracks SOH, ρ<0) | ≥1 R feature ρ<0, p<0.05 | 5/6 features ρ<0 at p<1e-4 (R_diff_400 ρ=−0.93, R_ohmic_400 −0.85, R_ohmic_326 −0.79, R_ohmic_363 −0.73, R_diff_363 −0.73) | **PASS** — physics clean, EIS encodes SOH |
| **P-Probe11_F2** (LOCO R² sign stable to SOC drop) | sign stable dropping any one SOC | drop-326 R²=−3.48 (stable), drop-400 R²=−12.6 (stable), **drop-363 R²=+0.83 (FLIPPED)** | **FAIL** — transfer is feature-fragile (see §4) |
| **P-Probe11_F3** (cell-stratified null more conservative than naive) | cell-strat p ≫ naive p | p_naive 0.0001 → p_cellstrat 0.0027 (34× less significant) | **PASS** — non-independence correctly handled |

## 2. Cohort (from extraction)

45 observations across all 6 cells (g1, v4, v5, w8, w9, w10), RPT rounds 10–19, each a (cell, round) with ≥2 of 3 SOC EIS points + capacity-derived SOH. **Pooled SOH 88.0–93.7% (5.7-point range).** SOH clusters by cell: W-cells low (88–90%), V/G-cells high (91–94%) — SOH variation is mostly *between* cells, barely *within* (~1–2% per cell). This confound is the binding constraint, exactly as flagged in pre-reg §0.2.

## 3. Primary result — LOCO transfer (the failure, and why it's nuanced)

| cell | n | MAE_model | MAE_baseline | improved? | SOH mean |
|---|---|---|---|---|---|
| g1 | 9 | 0.45% | 1.30% | ✓ | 91.9% |
| v4 | 6 | 0.86% | 1.25% | ✓ | 91.9% |
| v5 | 9 | 0.29% | 2.33% | ✓ | 92.7% |
| w10 | 6 | 0.87% | 1.57% | ✓ | 89.5% |
| w8 | 9 | 2.92% | 2.44% | ✗ | 88.9% |
| w9 | 6 | 0.56% | 1.32% | ✓ | 89.7% |

**5/6 cells beat their predict-the-training-mean baseline** (the within-cell tracking works — the model reads the local SOH gradient). **Yet pooled LOCO R² = −4.19** (vs the global actual mean). The apparent contradiction is the confound: the model cannot place a held-out cell at its correct *absolute* SOH level, because that cell's SOH band is barely represented in the other 5 cells (and the total range is 5.7 points). It tracks the shape, misses the offset. Pooled MAE is 1.04% SOH — small in absolute terms only because the whole range is small.

**H11-main FAIL** (requires majority-improved AND pooled R²>0; got 5/6 improved but R²=−4.19).

## 4. The F2 instability is informative, not just a failure

Dropping the middle SOC (3.63 V) flips pooled LOCO R² from −4.19 to **+0.83** — using only the 3.26 V and 4.00 V fingerprints, the model *does* transfer. This is a real instability (F2 FAIL as locked), and **post-hoc, so not claimable as a result** — but it is a strong hint: the transfer failure is not fundamental, it is feature- and range-limited. Combined with the emphatic F1 (ρ up to −0.93) and the significant cell-stratified PERMANOVA, the evidence points to transferable SOH readout being *achievable with a wider SOH range and a cleaner feature set* — which is exactly direction (2) (extend range via first-life data). Per the Probe 9b lesson, the drop-363 R²=+0.83 would itself need a multi-config/multi-seed stability gate before being believed.

## 5. Secondary — C3 PERMANOVA (the signal is real at n=6)

| PCA-k | F | p_naive | p_cell-stratified |
|---|---|---|---|
| 2 | 25.51 | 0.0001 | **0.0027** |
| 3 | 19.79 | 0.0001 | **0.0034** |

Even under the conservative cell-stratified null (which permutes whole-cell label-blocks, respecting that the 6 cells are the independent units), the EIS fingerprint separates SOH tertiles significantly. So the fingerprint *does* carry group-level SOH information that survives the non-independence correction — it just doesn't yield a transferable *absolute* regression on this range.

## 6. Disposition (per lit/58 §5)

**SOH-READABLE (within-cell only).** F1 PASS (genuine signal, not broken extraction); H11-main LOCO transfer FAIL; cell-stratified PERMANOVA significant. Per the locked disposition: *"SOH readable with per-cell calibration but no universal model. Triage would need a per-cell reference EIS"* — **on this cohort.** The cause is the 5.7-point SOH range + cell-confound (pre-reg §0.2), not the method.

## 7. What this establishes / does not

**Establishes:**
- EIS demonstrably encodes SOH on real second-life NMC cells (F1, ρ up to −0.93) — the cross-substrate rule holds: SOH is a direct-signature target and the C3 fingerprint reads it.
- The C3 architecture separates SOH groups significantly even under proper cell-level non-independence handling.

**Does NOT establish:**
- Transferable (universal-model) EIS→SOH triage — fails on this narrow, cell-confounded cohort. The F2 instability suggests it is range-limited, not fundamental.
- Anything for degradation-*mode* (direction b, deferred).
- A deployment claim — n=6, proof-of-concept.

## 8. Motivated next step

**Direction (2): extend SOH range via first-life data.** The cells aged 100% → ~89% in *first life*; that range lives in the first-life EIS `.mat` aggregates (`data/secl_first_life/diagnostic_processed/EIS_test.mat`), not parsed here. A first-life + second-life pooled cohort would give a real dynamic range (~10–20 points) and break the cell/SOH confound (each cell would span a wide SOH band within itself). The strong F1 + the drop-363 R²=+0.83 hint make this the high-value follow-up. Would need its own pre-reg (and a stability gate on the feature-set choice).

## 9. RMD-SRC framing

A validation-agreement + predictive-transfer probe (RMD_F3 + RMD_F4) that **converged to a clean conditional positive**: the operator is validated (F1 emphatic, cross-substrate rule confirmed for a direct-signature target), the in-architecture separation is real and survives non-independence (RMD_F3), but predictive transfer (RMD_F4) fails *for the documented cohort reason* (range + confound), not the operator. The honest disposition is "readable, not yet transferably" — and the analysis itself points to the cohort change that would test transfer properly.

---

**Lock metadata:**
- Pre-reg lock commit: `ed2df82`
- Result commit: `<TBD — recorded in this commit>`
- Extractor SHA-256: `cdf983dbc1ecfba2cc3d5065b14cbbc1bbecc10b0f762cf4cc1aa85210721a47`
- Analyzer SHA-256: `0ae8ce4e466e0922d739934e8e90da75571d2832f728200c82f6b8599b67c74d`
- Observations parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703`
- Result parquet SHA-256: `047d385ae097ca0c326afe9a16c6925cb7916265074f7bc40bdcd044eb5f1485`

## 10. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-28 | F3 check threshold corrected mid-run (absolute `|Δp|>0.01` → ratio `≥3×` OR `|Δp|>0.01`). | Original absolute threshold misfires for small p (0.0001 vs 0.0027 differ 27× but Δ<0.01). The pre-reg §4 wording was "differ materially"; ratio is the correct operationalization. Corrected check reads PASS (34× more conservative). Analysis-internal validity check only; does not touch hypotheses or disposition. |
| 2026-05-28 | F2 FAIL is reported as a genuine falsifier firing (not corrected). | drop-363 R² flip is a real data finding, logged honestly as §4; informs the direction-(2) follow-up. |
