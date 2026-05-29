# C3 Probe 12 — Wide-Range (First+Second-Life) SOH Triage Pre-Registration

**Status:** LOCKED 2026-05-28 at commit `b5e71c7`. No Probe 12 extraction/analysis had fired at lock time. First-life `.mat` inspection (read-only, scipy) was done before drafting (see §0.1) — no features computed, no model run.
**Date drafted:** 2026-05-28
**Authored:** Claude
**Repo target on lock:** `Battery/literature/60_probe12_widerange_soh_triage_prereg.md`
**Prior:** Probe 11 (lit/58+59) = **SOH-READABLE (within-cell only)**. F1 emphatic (R_diff@4.00V ρ=−0.93); H11-main LOCO transfer FAIL (pooled R²=−4.19) on a **5.7-point, cell-confounded** second-life range. The post-hoc drop-363 R²=+0.83 hint motivated direction (2): extend SOH range via first-life data. HEAD `1136dd1`.

---

## 0. Motivation — does wide range fix transfer, or is the failure fundamental?

Probe 11 established that the EIS fingerprint **reads SOH within a cell** but does **not transfer** a held-out cell's *absolute* SOH. The diagnosis was that the second-life cohort spanned only 5.7 SOH points (88–94%), with SOH almost entirely *between* cells (W-cells low, V/G-cells high) and barely *within* — so the model learned shape, missed offset. That is a **cohort limitation hypothesis**, and it is falsifiable: if we widen the within-cell SOH range and decorrelate SOH from cell identity, transfer should appear. If it still fails, the failure is **more fundamental than range** (mechanism/extraction) and the "range-limited" story is wrong.

The first-life diagnostic data supplies the missing range: the same physical cells aged 100% → ~92% in first life. Pooling first+second life gives W8/W9/W10 a within-cell sweep of ~12pt and V4 ~8.5pt, and a pooled axis of ~88–101% — SOH now varies **within** cells, not just between them.

In **RMD-SRC** terms this is a clean **predictive-transfer (RMD_F4)** re-test under the documented cohort fix, with two new adversarial guards (RMD_F2/F3) for the seams that pooling introduces.

## 0.1 Feasibility (verified read-only before drafting)

First-life `data/secl_first_life/diagnostic_processed/{EIS_test,capacity_test}.mat` are **MATLAB v7** files — read directly with `scipy.io.loadmat` (NOT v7.3/HDF5; `h5py` fails with "file signature not found"). Schema confirmed against the shipped `data_analysis.m`:

- **Cell-index → label** (1-based col): `1→W3, 2→W4, 3→W5, 4→W7, 5→W8, 6→W9, 7→W10, 8→G1, 9→V4, 10→V5`. `col_cell_label` carries the labels.
- **`cap`,`vcell`,`curr`,`time`** = (15 diag × 10 cell) object arrays; each valid element is a discharge curve. **SOH = max(cap[i,cell]) / 4.85 Ah** (same nominal as Probe 11). Missing diagnostics stored as scalar NaN.
- **`re_z`,`im_z`,`freq`** = (15 × 10) object; each valid element is an **(n_freq × 3 SOC)** matrix. **`soc_level = [20, 50, 80]` %**. Frequency grid **10 kHz → 10 mHz, 19 points** — the low-freq end (10 mHz) is the **same** as the second-life Gamry grid (10 kHz → 10 mHz, 43 pts), so `R_ohmic`/`R_diff` are computed identically and are comparable.

**Measured first-life cohort (this inspection):**

| Cell | First-life SOH span | First-life EIS spectra |
|---|---|---|
| W8 | 100.6→91.9% (8.7pt) | **15** |
| W9 | 100.5→92.0% (8.5pt) | **15** |
| W10 | 100.3→91.9% (8.4pt) | **15** |
| V4 | 100.4→94.9% (5.5pt) | **10** |
| V5 | 97.0–100.2% | 3 |
| W3 | (1.8pt) | 3 |
| W4 / W5 / W7 / G1 | 5.9–8.4pt cap | **0** (no first-life EIS — README "equipment issues") |

**Pooled first-life SOH: n=101 capacity points, 91.8–101.1% (9.3pt).**

Second-life cohort (from Probe 11 parquet, unchanged): 6 cells {g1, v4, v5, w8, w9, w10}, 45 obs, SOH 88.0–93.7%, 6D = {R_ohmic, R_diff} × {3.26, 3.63, 4.00 V}. **Cell IDs overlap first life** — so W8/W9/W10/V4 carry the same physical cell across both lives.

## 0.2 The binding constraints + new seams (stated up front)

1. **Still ~6 independent cells.** Pooling adds *range within* cells, not new independent cells. The statistical ceiling (cell count) is unchanged; the dynamic range is what improves.
2. **State-axis seam (NEW).** First life is indexed by **SOC%** (20/50/80); second life by **voltage** (3.26/3.63/4.00 V). For NMC these correspond approximately (low/mid/high), but the OCV map is inexact and drifts with age — strongest at the low state (3.26 V ≈ ~10–15% SOC vs nominal 20%). `R_ohmic` (high-freq intercept) is largely state-insensitive; `R_diff` (charge-transfer/diffusion) is state-sensitive and therefore the vulnerable feature. **Locked mapping: 20%→326, 50%→363, 80%→400.** Tested, not assumed, by F2.
3. **Rig/batch seam (NEW).** First-life EIS = Stanford diagnostic rig; second-life EIS = Gamry. A systematic `R_ohmic` offset (cabling/fixture/contact) would alias with SOH because first-life = high SOH and second-life = low SOH. **This is the lead threat to a transfer claim** and is the explicit target of F2 + the harmonized arm.
4. **Confound-direction reversal.** Probe 11's confound was SOH≈cell-identity. Pooling fixes that (SOH now varies within cell) but *introduces* SOH≈lifecycle-domain (first=high, second=low). The whole point of F2 is to check we didn't trade one confound for another.

This remains a **proof-of-concept on a thin real cohort**, not a deployment claim.

## 1. Hypotheses (LOCKED)

**H12-main (wide-range transfer):** On the pooled first+second-life cohort (SOH ~88–101%), leave-one-cell-out (LOCO) EIS→SOH regression achieves **pooled R² > 0** AND beats the predict-train-mean baseline MAE on a **majority of held-out cells**. This promotes the Probe 11 post-hoc hint to a primary, pre-registered test: *if Probe 11's transfer failure was range-limited, it disappears here.*

**H12-secondary (range mechanism):** The improvement over Probe 11 is attributable to within-cell dynamic range, not to more data per se — operationalized as: pooled LOCO R² rises monotonically (or at least flips negative→positive) relative to the second-life-only R²=−4.19 baseline, with the wide-range cells (W8/W9/W10) being the ones whose held-out predictions most improve.

**H12-null:** LOCO still fails (pooled R² ≤ 0) even with ~9–13pt within-cell range and a decorrelated SOH axis. This would **falsify the range-limited story** and say the transfer failure is more fundamental (rig confound, state-axis mismatch, or genuine mechanism limit) — itself a strong, publishable negative that closes the "just needs more range" hypothesis.

## 2. Cohort + data (LOCKED)

- **Source:** `data/secl_first_life/diagnostic_processed/{EIS_test,capacity_test}.mat` (NEW, v7 scipy) + the **existing** Probe 11 parquet `data/processed/secl_eis_soh_observations.parquet` (SHA `9dd867c5…`, reused byte-for-byte; second-life arm is NOT recomputed).
- **Observation unit:** (cell, lifecycle ∈ {first, second}, diagnostic/round) carrying the 6D feature + capacity-derived SOH in the same diagnostic. First-life features computed with the **identical** `R_ohmic`/`R_diff` definitions as the Probe 11 extractor (§3), on the per-cell (n_freq×3 SOC) spectra, SOC→voltage mapped per §0.2.
- **PRIMARY cohort:** all EIS-usable cells across both lives = **{W8, W9, W10, V4, V5, G1}** (6 independent cells). First-life EIS rows are added to W8/W9/W10/V4 (and the 3 thin V5 rows); G1 stays second-life-only (it is a *narrow held-out* cell — a fair stress test of whether a wide-range-trained model can place a cell it only sees narrowly). Final N + per-cell counts + per-cell within-cell SOH span **recorded in the extraction output**, not asserted here.
- **Independent unit:** physical cell (a cell's first + second life share one LOCO block).
- **`lifecycle` column** retained on every row for the F2 domain test and the harmonized arm.

## 3. Architecture + method (LOCKED — identical to Probe 11 except cohort)

**EIS feature per (cell, lifecycle, diagnostic):** `R_ohmic` = Re(Z) at the high-freq Im(Z)=0 crossing (interpolated; min-Re fallback). `R_diff` = Re(Z, lowest freq = 10 mHz) − `R_ohmic`. Per state-point → **6D = 3 states × {R_ohmic, R_diff}**. >1 state missing ⇒ drop row; single missing state ⇒ cohort-median impute (logged).

**SOH label:** SOH = Q_diag / 4.85 Ah, continuous. Tertile bins (for the descriptive PERMANOVA) computed on the pooled label distribution before any feature use.

**H12-main — LOCO regression (PRIMARY):** for each held-out cell, fit **PLS, n_components=2** on z-scored 6D features of all other cells; predict held-out SOH. Metrics: pooled LOCO R² + per-cell MAE vs predict-train-mean baseline. (PLS/n=2 locked identical to Probe 11 for direct comparability.)

**Descriptive:** C3 PERMANOVA (z→PCA-k {2,3}→unit→cosine) on SOH tertiles with the **cell-stratified null** (reported, not claim-bearing), for continuity with Probe 11 §5.

## 4. Falsifiers (LOCKED)

**P-Probe12_F1 ↔ RMD_F1 (physics positive control).** ≥1 R feature must track SOH (Spearman ρ<0, p<0.05) on the pooled cohort. Expected to pass trivially (Probe 11 gave ρ=−0.93); if it fails, the first-life extraction is broken → **INVALID**, not "untransferable."

**P-Probe12_F2 ↔ RMD_F2 (DOMAIN CONFOUND — lead threat).** Train a domain classifier (logistic regression, 5-fold CV) first-life-vs-second-life on the 6D feature, **restricted to the SOH-overlap band** (the SOH interval covered by both lifecycles, ≈ 92–94%, where any first-vs-second difference is *not* SOH and is therefore pure rig/state-axis offset). Pre-committed read: **domain CV-AUC ≤ 0.70 = clean** (transfer claim admissible on raw features); **> 0.70 = confound flagged** (raw transfer is contaminated). REGARDLESS of AUC, also run a **harmonized arm**: estimate each feature's additive domain offset Δ on the overlap band (Δ = mean_second − mean_first there, so SOH is matched and Δ is pure rig/state offset), subtract Δ from second-life rows, re-fit LOCO. Report **raw and harmonized** pooled R². The harmonized R² is the conservative read used in disposition.

**P-Probe12_F3 ↔ RMD_F3 (FEATURE-SET STABILITY GATE — the 9b/Probe-11 lesson, mandatory).** Probe 11's drop-363 R²=+0.83 was post-hoc and uncommitted. Here the panel is **pre-registered**: evaluate H12-main on the fixed config set **{full 6D, drop-326 4D, drop-363 4D, drop-400 4D, R_diff-only 3D, R_ohmic-only 3D}**. **Headline = full 6D.** Disposition requires the **sign of pooled R² to be positive in ≥4 of the 6 configs** (a majority, not a cherry-pick). If only an isolated config is positive, that is a stability FAIL — transfer is feature-fragile, exactly as in Probe 11, and cannot be claimed. (Note: the R_ohmic-only vs R_diff-only split also diagnoses the §0.2 state-axis seam — R_diff is the state-sensitive feature, so a large ohmic/diff divergence localizes the failure.)

**P-Probe12_F4 (COHORT-DELIVERY GUARD).** The pooled cohort must actually deliver the premise: **≥3 cells with within-cell SOH span ≥ 7pt**. (By construction W8/W9/W10 give ~12pt, so this should pass; if the merge/alignment silently drops first-life rows it fails and the test is **VOID** — re-scope rather than report a false negative.)

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **TRANSFERABLE-TRIAGE (strong)** | H12-main PASS (raw pooled R²>0 + majority cells improve) AND F3 sign-stable (≥4/6 configs R²>0) AND F2 clean (domain AUC ≤0.70 **or** harmonized R²>0) | Wide range fixes transfer. EIS→SOH triage generalizes across real cells given adequate dynamic range — Probe 11's failure was range-limited, as hypothesized. Next: scale cohort + external dataset. |
| **TRANSFERABLE-BUT-DOMAIN-LIMITED** | H12-main PASS on raw but F2 flags confound (AUC>0.70) AND harmonized R²≤0 | Apparent transfer is partly a rig/state-axis artifact; cannot be cleanly claimed. Honest conditional — points to instrument harmonization as the real blocker, not range. |
| **FEATURE-FRAGILE** | H12-main PASS on full 6D but F3 fails (<4/6 configs positive) | Transfer exists only for a feature subset — same fragility as Probe 11, now pre-registered. Not claimable as robust triage. |
| **RANGE-INSUFFICIENT / FUNDAMENTAL NULL** | H12-main FAIL (pooled R²≤0) despite wide within-cell range | Falsifies the range-limited story. Transfer failure is more fundamental than range (mechanism/extraction/rig). Strong negative — closes "just needs more range." |
| **PROBE 12 VOID** | F4 fails (cohort didn't deliver ≥3 cells ≥7pt) | Merge/alignment bug. Fix + re-run; no claim. |
| **PROBE 12 INVALID** | F1 fails (R doesn't track SOH pooled) | First-life extraction broken. Debug + re-run. |

## 6. What Probe 12 does NOT establish

- Not a deployment claim — still ~6 cells, one chemistry (INR21700-M50T), one lab.
- Not a degradation-*mode* classifier (direction b, deferred).
- A positive result does not validate the SOC%↔voltage mapping as physically exact — only that transfer survives whatever residual mismatch exists (F2/F3 bound it).
- A NULL is cohort-limited (rig/state seam or 6-cell ceiling), not a claim EIS can't read SOH (it demonstrably can — F1).

## 7. Operational protocol

1. Sign-off + commit this pre-reg. Lock anchor = commit hash (filled into §0 + lock metadata).
2. Build `code/probe12_firstlife_eis_soh_extractor.py` — parse first-life `.mat` (scipy v7): per (cell, diagnostic) compute the 6D `R_ohmic`/`R_diff` (SOC→voltage mapped) + SOH=max(cap)/4.85; emit `data/processed/secl_firstlife_eis_soh.parquet` with a `lifecycle='first'` column. Report N + per-cell counts + within-cell SOH span.
3. Build `code/c3_probe12_widerange_soh_triage.py` — load + concat first-life parquet with the **unchanged** second-life parquet (`lifecycle='second'`); run LOCO PLS (raw + harmonized), the F3 config panel, the F2 domain classifier, F4 guard, F1 control, and the descriptive PERMANOVA.
4. Run. Output: `data/processed/probe12_widerange_results.parquet`.
5. Apply §5 disposition + §4 falsifiers.
6. Write `literature/61_probe12_widerange_soh_triage_result.md`. Commit + lock hashes.

**Cost:** extraction parses 2 `.mat` files (seconds) + reuses the second-life parquet; analyzer trivial (LOCO on 6 cells + a CV classifier + 6-config panel). No new simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `b5e71c7`
- First-life extractor SHA-256: `845e44df0d89244d83a1c350384d01f7a24be40d6f004316dfae003ae0665f87`
- First-life parquet SHA-256: `17d66ecef02b1c7ad2181d18189565c4f5c302257cd4fc9a5b2c075f96cb50db`
- Analyzer SHA-256: `9fb41ba8ef677a404089c5041954fd8172e350740628030b3be4508b9051116a`
- Result parquet SHA-256: `9cfa5a5076560d4c046d28af9f35e9e6de37c3caf5765818a071538551273d31`
- Reused second-life parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (from Probe 11, unchanged)
- Result writeup: `literature/61_probe12_widerange_soh_triage_result.md` — disposition RANGE-INSUFFICIENT / FUNDAMENTAL NULL
