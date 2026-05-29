# C3 Probe 12 — Wide-Range (First+Second-Life) SOH Triage RESULT

**Status:** COMPLETE. Disposition = **RANGE-INSUFFICIENT / FUNDAMENTAL NULL** (per locked lit/60 §5). Adding dynamic range did **not** rescue cross-cell transfer of the full-feature EIS→SOH model — falsifying Probe 11's "range-limited" hypothesis. The failure is more fundamental than range: a non-transferable feature (`R_ohmic`) compounded by a severe instrument/state-axis domain confound.
**Date:** 2026-05-29
**Authored:** Claude
**Pre-reg:** `literature/60_probe12_widerange_soh_triage_prereg.md` (lock `b5e71c7`).
**Prior:** Probe 11 (lit/58+59) = SOH-READABLE (within-cell only), LOCO R²=−4.19 on a 5.7pt cell-confounded cohort; the post-hoc drop-363 hint motivated this direction-(2) range extension.

---

## 0. One-line result

On a pooled first+second-life cohort that genuinely delivered wide within-cell SOH range (5 cells ≥7pt, W8=12.5pt; **F4 PASS**), the locked full-6D leave-one-cell-out model **still fails to transfer** (pooled LOCO R²=−0.408, even though 6/6 cells beat their own within-cell baseline). Three locked falsifiers explain *why*, and the answer is **not** "insufficient range":
- **F1 PASS, emphatic** — all 6 EIS features track SOH (ρ up to −0.924); the fingerprint clearly reads SOH on the wider cohort.
- **F2 = smoking gun** — a domain classifier separates first-life from second-life **perfectly at matched SOH (CV-AUC = 1.000)**; additive harmonization made R² *worse* (−0.408 → −1.116). Pooling across the Stanford-rig/SOC-label first life and the Gamry/voltage-label second life introduced an inseparable, non-additive batch effect.
- **F3 FRAGILE (1/6)** — the pre-registered stability gate caught that only one config (drop-363) is positive; the full-feature headline is negative. The gate did its job: it blocks the cherry-pick the Probe 11 lesson warned about.

A post-hoc, single-instrument diagnostic (first-life only, no domain seam) **still fails** at full 6D (R²=−3.387), localizing the deeper cause: **`R_ohmic` (ohmic intercept = cell/fixture-specific contact resistance) is non-transferable**, while `R_diff` (charge-transfer/diffusion) carries the transferable SOH signal. So range was necessary-not-sufficient; the binding limits are feature choice + cross-instrument domain shift.

## 1. Cohort (pooled, locked PRIMARY = {W8,W9,W10,V4,V5,G1})

103 observations: 58 first-life (new, from `EIS_test.mat`/`capacity_test.mat`, scipy v7) + 45 second-life (Probe 11 parquet, reused byte-for-byte, SHA `9dd867c5…`). Pooled SOH **88.0–100.6%**.

**F4 cohort-delivery guard — PASS** (≥3 cells with within-cell span ≥7pt):

| cell | n | within-cell SOH span | lifecycles |
|---|---|---|---|
| w8 | 24 | **12.5pt** | first+second |
| w10 | 21 | 11.3pt | first+second |
| w9 | 21 | 11.3pt | first+second |
| v4 | 16 | 8.1pt | first+second |
| v5 | 12 | 8.1pt | first+second |
| g1 | 9 | 1.6pt | second only (narrow held-out stress cell) |

The premise of direction (2) was met: SOH now varies **within** cells, not just between them. The Probe 11 confound (SOH≈cell-identity) is genuinely broken.

## 2. Falsifier results

| Falsifier | Threshold | Result | Verdict |
|---|---|---|---|
| **F1** (R tracks SOH, ρ<0) | ≥1 feature ρ<0, p<0.05 | **6/6** features ρ<0 at p<1e-9 (R_diff_400 ρ=−0.924, R_ohmic_326 −0.895, R_diff_363 −0.875) | **PASS** (emphatic) |
| **F4** (cohort delivers range) | ≥3 cells span ≥7pt | 5 cells ≥7pt (W8 12.5pt) | **PASS** — not VOID |
| **F2** (domain confound) | domain AUC ≤0.70 clean; harmonized R²>0 | AUC=**1.000** at matched SOH; harmonized R²=**−1.116** (worse) | **CONFOUNDED** — severe, non-additive rig/state seam |
| **F3** (feature stability) | ≥4/6 configs R²>0 | **1/6** (only drop_363 = +0.700) | **FRAGILE** — full-feature transfer not robust |

## 3. Primary — H12-main LOCO (the locked headline: FAIL)

| cell | n | MAE_model | MAE_base | improved? | SOH mean |
|---|---|---|---|---|---|
| g1 | 9 | 0.39% | 1.79% | ✓ | 91.9% |
| v4 | 16 | 2.74% | 2.75% | ✓ | 95.0% |
| v5 | 12 | 0.76% | 1.83% | ✓ | 94.1% |
| w10 | 21 | 1.16% | 2.66% | ✓ | 93.5% |
| w8 | 24 | 2.02% | 3.17% | ✓ | 92.8% |
| w9 | 21 | 0.84% | 2.64% | ✓ | 93.6% |

**Pooled LOCO R² = −0.408** (vs Probe 11 second-life-only −4.19 — a ~10× improvement, but still negative). **6/6 cells beat their within-cell baseline**, yet the pooled R²<0: the model reads each cell's local SOH *gradient* but cannot place a held-out cell's *absolute* level. **H12-main FAIL** (requires R²>0 AND majority improve).

**H12-secondary partial:** the improvement over Probe 11 (−4.19 → −0.408) tracks the added range, consistent with range *helping* — but not enough to cross zero, and confounded by the F2 domain shift, so secondary is not cleanly supported.

## 4. F3 stability panel (pre-registered — the Probe 11 lesson, enforced)

| config | dim | pooled R² |
|---|---|---|
| full_6D (headline) | 6 | −0.408 |
| drop_326 | 4 | −0.792 |
| **drop_363** | 4 | **+0.700** |
| drop_400 | 4 | −3.930 |
| R_diff_only | 3 | −0.219 |
| R_ohmic_only | 3 | −0.649 |

Only **drop_363** is positive (1/6) → **FRAGILE**. Note: drop_363 was *also* Probe 11's post-hoc winner — the signal recurs, but it is not robust across the pre-committed panel, so it is **not claimable**. This is exactly why F3 was locked after the 9b/Probe-11 lesson: had we cherry-picked drop_363 we would have falsely declared transfer.

## 5. Post-hoc diagnostic (NOT pre-registered, NOT claimable) — why it fails

Single-instrument, **first-life only** (no domain seam), LOCO on the 4 first-life cells with n≥5:

| config | pooled R² | | per-cell | improved |
|---|---|---|---|---|
| full_6D | **−3.387** | | w8/w9/w10 ✓, **v4 ✗** | 3/4 |
| drop_326 | +0.535 | | | |
| **R_diff_only** | **+0.768** | | | |
| R_ohmic_only | **−239.96** | | | |

Two clean takeaways (diagnostic, motivating Probe 13 — not a Probe 12 claim):
1. **Removing the domain seam does not fix full-feature transfer** (R²=−3.387). So the failure is genuinely more than the rig confound — it is fundamental at the locked feature set.
2. **`R_ohmic` is the transfer-killer.** Alone it is catastrophic (R²≈−240, because the ohmic intercept is dominated by cell/fixture-specific contact resistance); dropping it (`R_diff_only` +0.768) makes transfer appear. The charge-transfer/diffusion resistance is the cell-agnostic, SOH-bearing, transferable feature. (The high-SOH held-out cell V4, with the narrowest range, is the one the absolute-level model misses worst — extrapolation to a range edge.)

## 6. Disposition (per lit/60 §5)

**RANGE-INSUFFICIENT / FUNDAMENTAL NULL.** F1 PASS (signal real), F4 PASS (range delivered), H12-main FAIL (R²=−0.408 with wide range), F3 FRAGILE, F2 CONFOUNDED. The locked bucket name says "range-insufficient," but the precise mechanism — anticipated by the locked §5 meaning ("more fundamental than range: mechanism/extraction/rig") — is **(a) a non-transferable feature (`R_ohmic`) and (b) a perfect cross-instrument/state-axis domain confound**, not a lack of dynamic range. **Probe 11's range-limited hypothesis is falsified.**

## 7. What Probe 12 establishes / does not

**Establishes:**
- The EIS fingerprint reads SOH across the wider 88–100.6% cohort (F1 ρ up to −0.924) — the cross-substrate rule holds for SOH as a direct-signature target.
- **Adding dynamic range alone does not yield transferable absolute-SOH triage** — Probe 11's "just needs more range" hypothesis is dead.
- The transfer failure localizes to **`R_ohmic` non-transferability** (contact-resistance, cell/fixture-specific) and to a **severe pooled-domain confound** (AUC=1.0, additive harmonization insufficient).
- The pre-registered F3 stability gate worked: it blocked a recurring post-hoc cherry-pick (drop-363 / R_diff-only) from becoming a false positive.

**Does NOT establish:**
- That transferable triage is impossible — the diagnostic suggests an `R_ohmic`-excluded, single-instrument, contact-normalized model is the untested clean path.
- Anything for degradation-mode (direction b, deferred).
- A deployment claim — still 6 cells, one chemistry, two instruments.

## 8. Motivated next step (Probe 13 — needs its own pre-reg)

Promote the consistently-recurring post-hoc signal to a **pre-registered primary**: **`R_diff`-only (ohmic-excluded) EIS→SOH transfer**, on **single-instrument** data (to remove the F2 domain seam), with a **contact-resistance normalization** for any `R_ohmic` use (e.g., per-cell ohmic referencing). The clean test of "is transferable SOH triage achievable at all on this chemistry" is single-rig + diffusion-feature, not pooled + full-feature. Per the F3 lesson, lock the feature set *before* running and keep the stability panel.

## 9. RMD-SRC framing

A predictive-transfer (RMD_F4) re-test under a documented cohort fix that returned a **clean, mechanism-localizing negative**. The operator is validated (RMD_F1 emphatic), in-architecture separation survives non-independence (cell-stratified PERMANOVA p≈0.001, RMD_F3), but transfer (RMD_F4) fails — and the locked adversarial guards (RMD_F2 domain classifier, F3 stability gate) converted a would-be "wide range fixes it" success into the correct verdict: the limit is feature-transferability + instrument domain, not range. Honest disposition: **range falsified as the fix; the fragility/ohmic signal is the real lead.**

---

**Lock metadata:**
- Pre-reg lock commit: `b5e71c7`
- Result commit: `<recorded in this commit>`
- First-life extractor SHA-256: `845e44df0d89244d83a1c350384d01f7a24be40d6f004316dfae003ae0665f87`
- First-life parquet SHA-256: `17d66ecef02b1c7ad2181d18189565c4f5c302257cd4fc9a5b2c075f96cb50db`
- Analyzer SHA-256: `9fb41ba8ef677a404089c5041954fd8172e350740628030b3be4508b9051116a`
- Result parquet SHA-256: `9cfa5a5076560d4c046d28af9f35e9e6de37c3caf5765818a071538551273d31`
- Reused second-life parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (unchanged)

## 10. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-29 | Ran a post-hoc single-instrument (first-life-only) LOCO diagnostic (§5), not in the locked protocol. | Decision-relevant: distinguishes "transfer fundamentally fails" from "fails only due to the pooled domain seam." Explicitly labeled non-claimable, mirrors the Probe 11 drop-363 precedent; informs Probe 13 only. Does not touch the locked H12 disposition. |
