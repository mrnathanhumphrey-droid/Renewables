# C3 Probe 13 — R_diff-Only / Contact-Normalized Transferable SOH Triage Pre-Registration

**Status:** LOCKED 2026-05-29 at commit `be6a5d0`. No Probe 13 analysis had fired at lock time. **Integrity disclosure (§0.3): one Probe-13-relevant quantity is ALREADY KNOWN** from a Probe 12 post-hoc diagnostic and is treated as a *calibration anchor*, NOT a confirmatory claim — the pre-registered hypotheses below are the genuinely untested ones.
**Date drafted:** 2026-05-29
**Authored:** Claude
**Repo target on lock:** `Battery/literature/62_probe13_rdiff_transferable_soh_triage_prereg.md`
**Prior:** Probe 12 (lit/60+61, `96bc509`) = RANGE-INSUFFICIENT / FUNDAMENTAL NULL. Full-6D EIS→SOH LOCO transfer fails (pooled R²=−0.408; first-life-only R²=−3.387) because (a) `R_ohmic` is non-transferable (cell/fixture contact resistance; `R_ohmic`-only R²≈−240) and (b) a perfect cross-instrument domain confound (F2 AUC=1.000 first-vs-second at matched SOH). HEAD `96bc509`.

---

## 0. Motivation — is transferable SOH triage achievable on this chemistry *at all*?

Probe 12 falsified "more range fixes transfer" and localized the failure to two causes. It also produced a recurring, never-pre-registered hint across three probes (Probe 11 drop-363 R²=+0.83; Probe 12 pooled drop-363 +0.700; Probe 12 first-life-only `R_diff`-only +0.768): **dropping the ohmic / state-mismatched features makes transfer appear.** Per the F3 stability gate, none of these are claimable. Probe 13 asks the honest follow-up: **is `R_diff`-only (ohmic-excluded) transfer real and robust, or another single-split artifact — and does it survive the deployment-relevant cross-instrument test?**

In **RMD-SRC** terms: a focused **predictive-transfer (RMD_F4)** probe on a *pre-committed, ohmic-excluded* feature set, gated by the **9b multi-resample stability lesson** ([[feedback_diagnostic_driven_amendments]]) — the explicit purpose is to prevent a known single-LOCO point estimate from masquerading as a robust finding.

## 0.1 Physical hypothesis (why ohmic-exclusion should help)

`R_ohmic` (high-freq Im=0 intercept) is dominated by electrolyte + **contact/fixture resistance**, which is set per-cell at assembly and is not a portable function of SOH — so a model keyed on its absolute value cannot place an unseen cell. `R_diff` (low-freq Re − R_ohmic = charge-transfer + diffusion) is an intrinsic electrochemical quantity that grows with degradation and should be more cell-agnostic. **Prediction:** the transferable SOH signal lives in `R_diff`; `R_ohmic` is a per-cell nuisance offset.

## 0.2 Feasibility (verified before drafting)

`R_diff` at the 3 states is present in BOTH lives' parquets (first-life `secl_firstlife_eis_soh.parquet`; second-life `secl_eis_soh_observations.parquet`), computed by the identical definition (lit/60 §3). First-life single-instrument cells with EIS: W8/W9/W10 (15 obs), V4 (10), V5/W3 (3). No new extraction needed.

## 0.3 Integrity disclosure — what is already known (NOT re-claimable)

From Probe 12 §5 (post-hoc diagnostic, single-instrument first-life-only, deterministic PLS LOCO on the n≥5 cohort {W8,W9,W10,V4}):

| feature set | first-life-only LOCO R² | status |
|---|---|---|
| full 6D | −3.387 | known |
| **R_diff-only (3D)** | **+0.768** | **known — calibration anchor, NOT a Probe-13 claim** |
| drop-326 (4D) | +0.535 | known |
| R_ohmic-only (3D) | −239.96 | known |

These are **deterministic point estimates** I already computed. Probe 13 therefore does **not** re-assert "R_diff-only LOCO R²>0" as a finding. The pre-registered tests below concern quantities I have **not** computed: the **resampling distribution** of that estimate (does +0.768 survive, per 9b), the **cross-instrument** transfer (untested), and the **contact-normalization mechanism** (untested).

## 1. Hypotheses (LOCKED) — all genuinely untested

**H13-main (STABILITY — the decisive 9b gate):** the R_diff-only single-instrument transfer is **robust to cohort resampling**, not a single-LOCO artifact. Operationalized on the first-life cohort: (a) exhaustive **leave-2-cells-out** over {W8,W9,W10,V4} (C(4,2)=6 train-on-2/test-on-2 splits) → **median R² > 0**; (b) **observation-bootstrap** (resample training-cell observations with replacement, N=500 seeds, LOCO structure preserved) → **2.5th-percentile R² > 0**. PASS requires BOTH. *Rationale: 9b showed a +3.62 single-seed win wash to +1.24±4.88; this gate is exactly that check applied to the +0.768 anchor.*

**H13-cross (CROSS-INSTRUMENT — the deployment question):** an R_diff-only model trained on first-life cells predicts **second-life** cells' SOH with pooled R² > 0 (train-first / test-second, the cells {W8,W9,W10,V4,V5} present in both lives). This is the real triage scenario (model built on lab data, applied to field cells on a different rig) and is **untested**.

**H13-ohmic (CONTACT-MECHANISM — diagnostic, not deployment):** per-cell contact-referenced `R_ohmic` (each cell's R_ohmic minus that cell's highest-SOH/fresh R_ohmic) recovers toward transferability — contact-normalized R_ohmic-only LOCO R² **materially exceeds** the raw −239.96 (pre-committed: > 0, i.e. sign-flip). Confirms `R_ohmic`'s non-transferability is the per-cell contact offset, not a lack of SOH content. *Note: needs a per-cell reference EIS, so it is a mechanistic test, NOT a deployment claim (mirrors Probe 11's "per-cell reference" caveat).*

**H13-null:** R_diff-only transfer does not survive resampling (median R²≤0 or bootstrap 2.5pct≤0) AND/OR fails cross-instrument. Would mean the recurring drop-ohmic hint is a small-cohort artifact, not a real transferable signal — closing the SOH-triage arc as "within-cell only, no transferable model on this cohort/chemistry."

## 2. Cohort + data (LOCKED)

- **Source:** `data/processed/secl_firstlife_eis_soh.parquet` (lifecycle=first, SHA `17d66ece…`) + `data/processed/secl_eis_soh_observations.parquet` (lifecycle=second, SHA `9dd867c5…`). Both reused unchanged.
- **H13-main + H13-ohmic cohort (single-instrument):** first-life only. Primary = the n≥5 cells **{W8,W9,W10,V4}** (matches the §0.3 anchor exactly, so the resampling gate tests the known estimate, not a redefined one).
- **H13-cross cohort:** train = first-life {W8,W9,W10,V4,V5}; test = second-life {W8,W9,W10,V4,V5} (cells in both lives; G1 excluded — no first-life EIS).
- **Independent unit:** physical cell.

## 3. Method (LOCKED — identical model to Probe 11/12)

- **Model:** PLS regression, n_components=2, on z-scored features (z-fit on the training rows only). Identical to Probe 11/12 for comparability. *(For 3D feature sets PLS n=2 is retained; if a feature set has <2 columns the analysis is undefined and that arm is void.)*
- **LOCKED feature sets (no post-hoc config search — the F3 lesson enforced):**
  - `R_diff_3D` = {R_diff_326, R_diff_363, R_diff_400} — **H13-main + H13-cross primary feature set.**
  - `R_ohmic_contactnorm_3D` = {R_ohmic_v − R_ohmic_v(fresh,same cell)} for v∈{326,363,400} — **H13-ohmic only.**
- **Metrics:** pooled R² (vs global actual mean) + per-cell MAE vs predict-train-mean baseline. Stability: median + 2.5/97.5 percentiles of R² across the resampling scheme.
- **No feature-set panel sweep this time.** The feature sets are pre-committed by physical hypothesis (§0.1); reporting any *other* feature set is logged as an explicitly-labeled non-claimable diagnostic only.

## 4. Falsifiers (LOCKED)

**P-Probe13_F1 (positive control):** R_diff features still track SOH (≥1 with ρ<0, p<0.05) on each analysis cohort. Fail → extraction/cohort broken → INVALID.

**P-Probe13_F2 (R_diff domain separability — does ohmic-exclusion actually reduce the confound?):** repeat the Probe 12 F2 domain classifier (first-vs-second at matched SOH) but on **R_diff_3D only**. Pre-committed read: if R_diff-only domain AUC < the full-6D AUC of 1.000 by a material margin (≤0.85), ohmic-exclusion demonstrably shrinks the instrument confound; if it is still ≈1.0, the cross-instrument arm (H13-cross) is contaminated regardless of LOCO R² and H13-cross cannot be cleanly claimed.

**P-Probe13_F3 (stability is the gate, not a point estimate):** H13-main is judged ONLY on the resampling distribution (§1a+b), never on the single full-LOCO +0.768. If the full-LOCO is positive but the resampling median/CI is not, that is a FAIL (explicitly the 9b failure mode).

**P-Probe13_F4 (no silent cohort shrinkage):** the H13-main cohort must remain {W8,W9,W10,V4} (the anchor cohort). Any auto-drop of a cell voids the stability comparison.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **TRANSFERABLE-TRIAGE (robust, single-instrument)** | H13-main PASS (median R²>0 AND bootstrap 2.5pct>0) AND F1 holds | The ohmic-excluded fingerprint transfers SOH robustly within one instrument — Probe 12's failure was the ohmic feature + domain seam, not the physics. Deployable with same-rig calibration. |
| **TRANSFERABLE + CROSS-INSTRUMENT** | above AND H13-cross PASS (R²>0) AND F2 shows reduced domain AUC | Strongest result: lab-trained R_diff model triages field cells on a different rig. The genuine deployment claim. |
| **ROBUST-BUT-RIG-BOUND** | H13-main PASS but H13-cross FAIL (or F2 AUC still ≈1.0) | Transfer is real within-instrument but the cross-rig domain seam blocks deployment without harmonization. |
| **SINGLE-SPLIT ARTIFACT** | H13-main FAIL (resampling median/CI ≤0 despite full-LOCO +0.768) | The recurring drop-ohmic hint was a small-cohort artifact — exactly the 9b failure mode. Closes the SOH-triage arc: within-cell readable, no transferable model on this cohort. |
| **PROBE 13 INVALID** | F1 fails | Cohort/extraction broken. Debug. |

H13-ohmic is reported as a mechanistic finding under any disposition (it explains *why* R_ohmic fails; it is not part of the deployment ladder).

## 6. What Probe 13 does NOT establish

- Not a deployment claim beyond INR21700-M50T / this lab even if cross-instrument passes — still ≤6 cells.
- H13-ohmic's contact-normalization needs a per-cell reference EIS, so it is mechanistic, not field-deployable.
- A PASS does not revive `R_ohmic` as a portable absolute feature — only as a per-cell-referenced quantity.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock anchor = commit hash, filled into §0 + metadata). **Push to origin.**
2. Build `code/c3_probe13_rdiff_transfer.py` — reuse Probe 12 loaders + PLS LOCO; add leave-2-cells-out + observation-bootstrap (H13-main), train-first/test-second (H13-cross), per-cell contact-referencing (H13-ohmic), R_diff-only domain classifier (F2).
3. Run. Output `data/processed/probe13_rdiff_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/63_probe13_..._result.md`. Commit + lock hashes.

**Cost:** analysis-only on existing parquets (LOCO + 500-seed bootstrap on ≤6 cells; seconds–minutes). No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `be6a5d0`
- Analyzer SHA-256: `778c8c09d6787cb1a4be8649339ec624e45b53d9aa0925767831f2aafa12bd52`
- Result parquet SHA-256: `dbfd983f94f37cc18d43616e580a8ce1679a4a4cc50c43e5d45fec10995234b9`
- Reused first-life parquet SHA-256: `17d66ecef02b1c7ad2181d18189565c4f5c302257cd4fc9a5b2c075f96cb50db` (Probe 12, unchanged)
- Reused second-life parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (Probe 11, unchanged)
- Result writeup: `literature/63_probe13_rdiff_transferable_soh_triage_result.md` — disposition SINGLE-SPLIT ARTIFACT
