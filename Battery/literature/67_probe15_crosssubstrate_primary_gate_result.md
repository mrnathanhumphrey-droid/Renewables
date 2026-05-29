# C3 Probe 15 — Cross-Substrate-as-Primary-Gate Redesign RESULT

**Status:** COMPLETE. Disposition = **MATCHED-BASELINE-NOT-NULL** — and this is the substantive finding, not a degenerate one: the pre-registered F2 falsifier reveals that **Paper 2's published cross-substrate NULL (lit/35, F=0.92) was substantially a training-cohort artifact.** When C2 is trained on the cross-substrate-extractable real-EIS cohorts {Khan, SECL, Zhang} instead of {PyBaMM+Khan+Severson}, it transfers to WMG terminal-SOH (median F=3.22, p=0.024, robust across 200 RF seeds). Adding the gated EIS-spectral operators {E1, E2} transfers more comfortably (F=3.82, p=0.017).
**Date:** 2026-05-29
**Authored:** Claude
**Pre-reg:** `literature/66_probe15_crosssubstrate_primary_gate_prereg.md` (lock `4128561`).
**Prior:** lit/35 CASCADE CROSS-SUBSTRATE NULL (C2-only, F=0.921, p=0.576), which itself documented (§3) that 139/228 of its training cells had C2 mean-imputed.

---

## 0. One-line result

The cross-substrate-primary gate admits exactly **{E1_ohmic_intercept, E2_charge_transfer_radius, C2}** (all five trajectory operators dropped — non-extractable on snapshot WMG). Mirroring the lit/35 RF-cascade → leaf-PCA → WMG-SOH-PERMANOVA protocol but trained on the gate's real-EIS cohorts {Khan, SECL, Zhang} (n=37): the matched **{C2}-only** baseline **unexpectedly PASSES** (200-seed median F=3.22 [2.5pct 3.03], ref-seed p=0.024), and **{E1,E2,C2}** passes more robustly (median F=3.82 [2.5pct 3.49], p=0.017, CV acc 0.78 vs 0.62). Because F2 (matched C2-only should be NULL) fired, the locked disposition is **MATCHED-BASELINE-NOT-NULL**: the published lit/35 NULL was largely a **training-cohort / imputation artifact**, not an intrinsic C2 limitation. The cross-substrate-primary gate's real value is the **training-cohort discipline** (force modality-matched real-EIS cohorts, no synthetic/imputed dilution); E1+E2 add incremental robustness, not the threshold-crossing.

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** cascade learns | CV OOF acc > chance (0.25) both sets | C2 **0.622**, {E1,E2,C2} **0.784** | **PASS** |
| **F2** matched {C2}-only NULL | C2 on {Khan,SECL,Zhang} should be NULL | median F=**3.22**, 2.5pct 3.03, p=**0.024** → **NOT NULL** | **FIRED** (the finding) |
| **H15-main** {E1,E2,C2} robust transfer | median>3 AND 2.5pct>3 AND p<0.05 | median **3.82** [3.49, 4.20], p=**0.017** | **PASS** |
| **F3** multi-seed stability | judged on 200-seed distribution | C2 frac F>3 = 0.99; gated = 1.00 — both robust, not single-seed | **PASS** (real) |
| **F4** WMG binning | bins {80,85,90,95} each ≥3 | {5,5,4,5}, no fallback | **PASS** |

## 2. The distributions (200 RF seeds; WMG PERMANOVA pseudo-F)

| feature set | CV OOF acc (chance 0.25) | F median | F 2.5pct | F 97.5pct | frac F>3 | ref-seed p |
|---|---|---|---|---|---|---|
| {C2} (matched baseline) | 0.622 | 3.22 | 3.03 | 3.41 | 0.99 | 0.024 |
| {E1, E2, C2} (gated set) | 0.784 | 3.82 | 3.49 | 4.20 | 1.00 | 0.017 |
| *lit/35 ref: {C2} on PyBaMM+Khan+Severson* | 0.461 | — | — | — | — | F=0.92, p=0.58 (NULL) |

## 3. Why the published NULL was a training-cohort artifact (mechanism, documented in lit/35 itself)

lit/35 §3 step 2 states verbatim: *"Severson C2 is NaN for all 139 cells … imputed via cohort-mean … 139 of 228 training cells effectively contribute the mean-C2 value; the cascade learns primarily from PyBaMM (n=70) + Khan (n=19) variation."* So in the published run, C2 genuinely varied on only **19 of 228** training cells (8%); the other 92% were either synthetic (PyBaMM) or constant (mean-imputed Severson). That is a degenerate training signal for a real-cell-EIS transfer task.

The cross-substrate-primary gate fixes this **by construction**: requiring cross-substrate extractability forces the training set to cohorts where the operator is genuinely measured (the real-EIS cohorts {Khan, SECL, Zhang}, all 37 cells with finite C2). With an undiluted, modality-matched training signal, the same C2 → leaf-PCA representation now clusters WMG by terminal SOH (F=3.22 > 3.0, p=0.024). **The gate's value is therefore the training-cohort discipline, not the operator additions** — exactly the re-interpretation the locked §5 anticipated for this branch.

## 4. What E1+E2 add (incremental, not threshold-crossing)

Adding the gated EIS-spectral operators lifts CV OOF accuracy 0.62 → 0.78 and the WMG transfer F-distribution from [3.03, 3.41] (median 3.22) to [3.49, 4.20] (median 3.82), with frac-F>3 rising 0.99 → 1.00. So E1 (ohmic intercept) + E2 (charge-transfer radius) carry **additional transferable SOH information** beyond C2's R_DC/R_total ratio — physically sensible (ohmic + charge-transfer growth are direct aging signatures). But C2 alone, correctly trained, already crosses the threshold; E1+E2 make the transfer more robust rather than enabling it.

## 5. Honest caveats (the effect is real-but-modest on small cohorts)

- **Marginal for C2-only:** median F=3.22 with 2.5pct=3.03 sits right at the locked F=3.0 threshold. The C2-only transfer is *robust-to-seed* (frac>3 = 0.99) but *weak in magnitude*. {E1,E2,C2} is more comfortably separated.
- **Small n:** WMG test n=19 (4 SOH bins), training n=37. These are weak-but-significant effects, not strong discrimination. p-values (0.017–0.024) clear 0.05 but not by a wide margin.
- **One chemistry / protocol:** WMG is NMC811 cylindrical, snapshot EIS. No claim beyond it.
- **F2 "firing" is the finding, not a failure:** the pre-reg locked MATCHED-BASELINE-NOT-NULL as a substantive branch; it correctly re-attributes the lit/35 NULL.

## 6. Disposition (per lit/66 §5)

**MATCHED-BASELINE-NOT-NULL.** F1 PASS (both cascades learn), F2 fired (C2-matched PASSES, median F=3.22, p=0.024), H15-main PASS ({E1,E2,C2} robust, median F=3.82, p=0.017), F3 multi-seed-robust, F4 binning clean. Per the locked meaning: *"The published NULL was partly a training-cohort artifact (PyBaMM+Severson dilution). Re-interpret; the gate's value is then in the training-cohort change, not E1+E2."*

## 7. What Probe 15 establishes / does not

**Establishes:**
- **Cross-substrate SOH transfer to WMG IS achievable** with the C3 cascade — the lit/35 NULL was substantially an artifact of diluted/imputed training cohorts (8% of cells with genuine C2 variation), not an intrinsic failure.
- **The cross-substrate-primary gate is a real selection-methodology improvement** — its mechanism is forcing modality-matched, genuinely-extracted training cohorts (and it cleanly drops the non-transferable trajectory operators).
- E1 + E2 (EIS-spectral aging signatures) carry transferable SOH information additive to C2 (CV 0.62→0.78, F 3.22→3.82).
- Methodological: the pre-registered apples-to-apples baseline (F2) + 200-seed stability gate were both decisive — F2 caught the re-attribution; F3 confirmed it isn't a single-seed fluke.

**Does NOT establish:**
- Strong/deployable transfer — effects are weak (F just above 3) on small cohorts (WMG n=19).
- Any change to Paper 2's within-substrate results (PyBaMM-holdout F=57 etc.) — those stand; this re-scopes only the cross-substrate NULL.
- Generalization beyond NMC811 / snapshot-EIS.
- A full cascade re-selection under the gate (follow-up: re-run Gates I/II with the cross-substrate gate as primary, then validate the full re-selected set).

## 8. RMD-SRC framing

A predictive-transfer (RMD_F4) redesign in which the pre-registered adversarial baseline (F2) overturned the expected story: cross-substrate transfer was not blocked by operator selection but by **training-cohort composition**. The cross-substrate-primary gate works — by forcing modality-matched real-cohort training it removes the dilution that produced lit/35's NULL. The honest disposition (MATCHED-BASELINE-NOT-NULL) is more valuable than either pre-imagined branch: it corrects a published null and localizes the true lever (training-cohort discipline). The multi-seed gate (9b discipline) confirmed the effect is real-but-modest, not a single-seed artifact.

## 9. Recommended follow-up

Full Paper-2 cascade **re-selection under the cross-substrate-primary gate**: re-run Gate I/II with cross-substrate extractability+discrimination as a primary filter and modality-matched training cohorts, then validate the re-selected operator set on a held-out real cohort. This probe establishes the principle on a fixed feature set; the full re-selection is the Paper-3 deliverable.

---

**Lock metadata:**
- Pre-reg lock commit: `4128561`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `8863541b92801df83fa82b0f26f4410d5f447606ba9e8f3f70c4081d7b86137d`
- Result parquet SHA-256: `4c1d023b339a63c287d463748e7f3dd8401dd2512b455723a028dcdac55ab378`
- Reused operator parquets: `paper2_operators_{khan,secl,zhang,wmg}.parquet` (unchanged)
- Reference baseline: lit/35 C2-only(PyBaMM+Khan+Severson) WMG F=0.921, p=0.576 NULL

## 10. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-29 | CV sanity (F1) used 3-fold (not lit/35's 5-fold). | n=37 with smallest class kh_calendar=5; 3-fold avoids stratification failure. F1 is a sanity check (learns > chance), not claim-bearing. |
| 2026-05-29 | Khan 'excluded' aging_type cells (n=2) dropped from training. | They were excluded in Khan's own analysis; would break stratification. Khan training cells = 19 (cycle 14 + calendar 5). |
