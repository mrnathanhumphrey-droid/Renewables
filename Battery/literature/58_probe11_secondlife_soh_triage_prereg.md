# C3 Probe 11 — Second-Life SOH Triage (real-cell SECL) Pre-Registration

**Status:** LOCKED 2026-05-28 at commit `ed2df82`. No Probe 11 extraction/PERMANOVA had fired at lock time.
**Date drafted:** 2026-05-28
**Authored:** Claude
**Repo target on lock:** `Battery/literature/58_probe11_secondlife_soh_triage_prereg.md`
**Prior:** Transference arc closed (Probe 9 lit/52+53, Probe 10 lit/56+57 — both operator classes NULL). This pivots from "what can the C3 method discriminate" to "can it do something useful for the world." HEAD `8a223f5`.

---

## 0. Framework parentage + real-world motivation

The biggest waste lever in the battery economy is retiring EV cells at ~80% SOH when they remain useful for stationary/grid storage. The reuse bottleneck is **fast, cheap state-of-health readout** to triage retired cells (reuse vs recycle) without slow full-capacity tests. EIS is a fast, non-invasive measurement; capacity tests are slow.

**This probe asks: can the C3 EIS fingerprint read a real cell's SOH — including generalizing to a cell it has never seen?** This is the first *real-cell, useful-task* application of the C3 method (prior real-cell work was Khan cross-substrate design-parameter discrimination, lit/50+51).

In **RMD-SRC** terms: a **validation-agreement + predictive-transfer** probe (RMD_F3 + RMD_F4 emphasis), applied to a real longitudinal cohort. Unlike transference (a mechanism-mediated parameter the method is structurally blind to, Probe 9/10), **SOH is a direct-signature target** — ohmic + diffusion resistance demonstrably grow as cells age — so the cross-substrate rule (lit/57) predicts this *should* be readable. That makes it both useful and a fair positive test of the rule.

## 0.1 Feasibility (verified before drafting)

- **EIS extractable and matched to synthetic:** SECL second-life EIS files (Gamry, `ACIM` sheet: Freq / Zmod / Zphz) span **10 kHz → 10 mHz, 43 points** — the low-freq end is the *same 10 mHz* as the synthetic C3 operator. Re(Z)=Zmod·cos(phase), Im(Z)=Zmod·sin(phase). R_ohmic + R_diff extract directly (e.g., G1 @3.63V: ohmic intercept ~24.3 mΩ, R_diff ~1.7 mΩ).
- **3 SOC points per EIS round:** 3.26 V / 3.63 V / 4.00 V.
- **SOH extractable:** max Discharge_Capacity(Ah) from each round's capacity test. G1 trajectory RPT_1→10→18 = 4.588 → 4.497 → 4.422 Ah, monotonic fade. Nominal 4.85 Ah.
- **Usable EIS cohort ≈ 4 cells:** W8, W9, W10 (full 15 first-life diagnostics) + V4 (~11); G1/V4/V5 have second-life EIS (RPT_5–19). W3/W4/W5/W7/G1/V5 have sparse/missing first-life EIS (README: "equipment issues"). Capacity coverage is broader than EIS.

## 0.2 The binding constraints (stated up front)

1. **~4 independent cells with usable EIS.** Many (cell, round, SOC) *observations* (~100–180) but only ~4 *independent* physical cells. This is the statistical ceiling.
2. **Non-independence:** observations from the same cell (and a cell's first + second life) are correlated. Naive pooled inference would massively over-count. Handled by leave-one-cell-out (LOCO) and cell-stratified permutation (§3).
3. **Narrow second-life SOH range** (~91–95% per cell). Mitigated by pooling first+second life where EIS exists (W-cells aged further in first life) and by the continuous-SOH regression arm.

This is explicitly a **proof-of-concept on a thin real cohort**, not a deployment claim.

## 1. Hypotheses (LOCKED)

**H11-main (SOH readable — predictive transfer):** A model trained on the C3 EIS fingerprint of N−1 cells predicts the held-out cell's SOH better than a no-EIS baseline (predict-the-mean): leave-one-cell-out (LOCO) regression beats baseline MAE, with the per-cell improvement positive for a majority of held-out cells.

**H11-secondary (in-architecture separation):** The C3 PERMANOVA on SOH bins (z-score → PCA-k → cosine), evaluated with a **cell-stratified permutation null**, separates SOH bins (PASS/WEAK by the standard thresholds). Reported descriptively; the predictive-transfer claim rests on H11-main, not on pooled PERMANOVA p-values.

**H11-null:** The EIS fingerprint does not generalize across cells (LOCO MAE ≤ baseline) — SOH is readable only within-cell (cell-specific calibration), not transferably. Still informative: it would say EIS-based triage needs per-cell calibration, not a universal model.

## 2. Cohort + data (LOCKED)

- **Source:** `data/secl_first_life/` + `data/secl_second_life/SL_Dataset_SECL_INR21700-M50T/` (Arbin/Gamry xlsx).
- **Observation unit:** (cell, lifecycle, RPT-round, SOC-point) with BOTH a valid EIS spectrum (10 kHz–10 mHz) AND a paired capacity-derived SOH in the same round.
- **Cohort:** all such observations across the ≈4 EIS-usable cells (W8/W9/W10/V4 primary; G1/V4/V5 second-life EIS included where valid). **Final N + per-cell counts recorded in the extraction output** (not asserted here).
- **Independent unit:** physical cell (a cell's first + second life share one block — matches the lit/51-era "non-indep (same cell)" flag).

## 3. Architecture + method (LOCKED)

**EIS feature extraction per (cell, round):**
- R_ohmic = real-axis ohmic intercept = Re(Z) at the high-frequency Im(Z)=0 crossing (interpolated; falls back to min Re if no clean crossing). *Chosen over Re@10 kHz because the 10 kHz point carries inductive contamination (Re@10kHz 31 mΩ vs intercept 24 mΩ in the G1 sample).*
- R_diff = Re(Z, 10 mHz) − R_ohmic.
- Per SOC point (3.26/3.63/4.00 V). **Feature vector = 3 SOC × {R_ohmic, R_diff} = 6D** (structurally parallels the synthetic fresh+aged 6D).
- Observations missing one SOC point: that SOC's two features imputed by cohort median (logged); observation dropped if >1 SOC missing.

**SOH label:** SOH = Q_round / 4.85 Ah (documented nominal), continuous. Bins for the secondary = **tertiles of the pooled observed SOH**, computed in the extraction step before any PERMANOVA (binning on the label distribution only — independent of the EIS features).

**H11-main — LOCO regression (PRIMARY inferential):**
- For each held-out cell c: fit a regressor (locked: **PLS regression, n_components=2**, on z-scored 6D features) on all other cells' observations; predict c's SOH.
- Metric: LOCO MAE and R², vs baseline = predict pooled-train mean SOH. PASS = LOCO MAE < baseline MAE on a majority of held-out cells AND pooled LOCO R² > 0.
- PLS chosen (not OLS) for stability at 6D with collinear EIS features + small N; n_components=2 locked to mirror the C3 PCA-2.

**H11-secondary — C3 PERMANOVA (in-architecture, DESCRIPTIVE):**
- z-score → PCA-k (k ∈ {2,3}) → unit-vector → cosine PERMANOVA on SOH-bin labels.
- **Two nulls reported:** (i) naive observation-level permutation (anti-conservative — flagged, not used for claims); (ii) **cell-stratified null** = permute whole-cell SOH-bin trajectories across cells (preserves within-cell correlation). Significance claims use (ii) only.

## 4. Falsifiers — RMD-SRC F1–F4 inheritance (LOCKED)

**P-Probe11_F1 ↔ RMD_F1 (physics positive control):** R_ohmic and/or R_diff must increase with decreasing SOH in the pooled data (monotone aging signature; Spearman ρ(R, SOH) < 0 at p<0.05 pooled). If resistance does NOT track SOH at all, the EIS extraction is broken → **INVALID**, not "SOH-unreadable."

**P-Probe11_F2 ↔ RMD_F2 (PCA-k + SOC coherence):** the SOH-separation verdict must not oscillate across PCA-k {2,3}; LOCO R² sign must be stable to dropping any single SOC point (no single SOC carrying everything in a way that breaks on omission).

**P-Probe11_F3 ↔ RMD_F3 (non-independence honesty):** the cell-stratified PERMANOVA null must differ materially from the naive null (confirming non-independence is real and being handled). If naive and stratified p are identical, the blocking is mis-implemented → debug.

**P-Probe11_F4 ↔ RMD_F4 (predictive transfer):** this IS H11-main — LOCO generalization to a held-out cell. The deployable-triage claim stands or falls here.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **SOH-READABLE (transferable)** | H11-main PASS (LOCO MAE < baseline on majority of cells, pooled R²>0) AND F1 positive control holds | EIS fingerprint reads SOH on cells it never saw. Proof-of-concept that C3-style EIS triage generalizes across real second-life cells. Next step = scale cohort. |
| **SOH-READABLE (within-cell only)** | H11-secondary separates bins but LOCO fails to beat baseline | SOH readable with per-cell calibration but no universal model. Triage would need a per-cell reference EIS. |
| **SOH NULL** | neither LOCO nor cell-stratified PERMANOVA beats chance | EIS fingerprint does not carry transferable SOH at this cohort/extraction. Document; likely cohort-size or SOH-range limited. |
| **PROBE 11 INVALID** | F1 fails (resistance doesn't track SOH) | Extraction/pipeline broken. Debug + re-run. |

## 6. What Probe 11 does NOT establish

- Not a deployment claim — ~4 cells is proof-of-concept only.
- Not a degradation-*mode* classifier (that is the harder, mechanism-mediated direction (b), deferred — existing low-confidence LLI/LAM+SEI labels live in `secl_held_out_classification.parquet`).
- Not generalizable beyond INR21700-M50T / this lab's protocol without a broader cohort.
- A NULL here is cohort-limited, not a claim that EIS can't read SOH in general (it demonstrably can in larger literature cohorts).

## 7. Operational protocol

1. Sign-off + commit this pre-reg as `literature/58_probe11_secondlife_soh_triage_prereg.md`. Lock anchor = commit hash.
2. Build `code/probe11_secl_eis_soh_extractor.py` — parse SECL first+second-life EIS (ACIM Zmod/Zphz → R_ohmic/R_diff per SOC) + capacity tests (→ SOH), merge to `data/processed/secl_eis_soh_observations.parquet`. Report final N + per-cell/per-lifecycle counts + pooled SOH range.
3. Build `code/c3_probe11_soh_triage.py` — LOCO PLS regression (primary) + C3 PERMANOVA with cell-stratified null (secondary) + F1–F3 checks.
4. Run. Output: `data/processed/probe11_soh_triage_results.parquet`.
5. Apply §5 disposition + §4 falsifiers.
6. Write up `literature/59_probe11_secondlife_soh_triage_result.md`. Commit + lock-hashes.

**Cost:** extraction parses ~hundreds of xlsx (a few min I/O); analyzer trivial (LOCO on ~4 cells + PERMANOVA). No new simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `ed2df82`
- Extractor SHA-256: `cdf983dbc1ecfba2cc3d5065b14cbbc1bbecc10b0f762cf4cc1aa85210721a47`
- Observations parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703`
- Analyzer SHA-256: `0ae8ce4e466e0922d739934e8e90da75571d2832f728200c82f6b8599b67c74d`
- Result parquet SHA-256: `047d385ae097ca0c326afe9a16c6925cb7916265074f7bc40bdcd044eb5f1485`
- Result writeup: `literature/59_probe11_secondlife_soh_triage_result.md` — disposition SOH-READABLE (within-cell only)
