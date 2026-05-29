# C3 Probe 13 — R_diff-Only / Contact-Normalized Transferable SOH Triage RESULT

**Status:** COMPLETE. Disposition = **SINGLE-SPLIT ARTIFACT** (per locked lit/62 §5) — the recurring drop-ohmic hint has a positive *central tendency* but fails the pre-committed 95% bootstrap robustness bound, and does not transfer cross-instrument at all. **The SOH-triage arc closes: EIS reads SOH within a cell, but no transferable cross-cell model is achievable on this cohort.**
**Date:** 2026-05-29
**Authored:** Claude
**Pre-reg:** `literature/62_probe13_rdiff_transferable_soh_triage_prereg.md` (lock `be6a5d0`).
**Prior:** Probe 12 (lit/60+61) FUNDAMENTAL NULL localized the transfer failure to (a) non-transferable `R_ohmic` and (b) a perfect cross-instrument domain confound. This probe tested whether the ohmic-excluded (`R_diff`-only) signal is robust and deployable.

---

## 0. One-line result

The known calibration anchor reproduced exactly (`R_diff`-only full-LOCO R²=**+0.768**), and leave-2-cells-out was positive in all 6 splits (median +0.739). **But the pre-registered stability gate fails:** the 500-seed observation-bootstrap LOCO has median +0.744 with **2.5th-percentile −0.460** — the 95% lower bound crosses zero. Under the locked AND-gate (leave-2-out median>0 **AND** bootstrap 2.5pct>0), **H13-main FAILS**. Worse for deployment: **H13-cross (train-first/test-second) R²=−24.5** and the **`R_diff`-only domain classifier AUC is still 1.000** at matched SOH — ohmic-exclusion does *not* shrink the instrument seam. The contact-normalization mechanism is also rejected (R_ohmic stays at −202.8 vs raw −239.96). This is the 9b lesson realized: a clean-looking point estimate that does not survive proper resampling, and a within-instrument signal that is wholly non-portable across rigs.

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** (R_diff tracks SOH) | ≥1 ρ<0, p<0.05 | 3/3 ρ<0 (R_diff_400 ρ=−0.893) p<1e-9 | **PASS** |
| **anchor** (sanity, NOT a claim) | reproduce known +0.768 | full-LOCO R²=**+0.768** exactly | reproduced ✓ |
| **H13-main (a)** leave-2-cells-out | median R²>0 | median **+0.739** (all 6 splits 0.64–0.85) | (a) > 0 |
| **H13-main (b)** 500-seed obs-bootstrap | 2.5th-pct R²>0 | median +0.744, **2.5pct −0.460**, 97.5pct +0.808 | (b) FAIL |
| **H13-main** (overall, AND-gate) | both (a) and (b) | (a) pass, (b) fail | **FAIL** |
| **H13-cross** train-first/test-second | pooled R²>0 | **R²=−24.5**, MAE 2.38% | **FAIL** |
| **F2** R_diff-only domain AUC | <0.85 = confound reduced | **AUC=1.000** (= full-6D) | NOT reduced |
| **H13-ohmic** contact-norm R_ohmic | R²>0 (sign-flip from −239.96) | **−202.8** | **rejected** |

## 2. H13-main — why "all-positive leave-2-out" still FAILS the gate (the 9b lesson, exactly)

The two resampling schemes disagree, and the disagreement is the finding:

- **Leave-2-cells-out** (6 exhaustive cell partitions, train-on-2/test-on-2): every split positive, 0.645–0.845, median +0.739. At the *cell* level the signal looks solid.
- **Observation-bootstrap** (resample training-cell observations with replacement, 500 seeds): median +0.744 — same center — but a **heavy negative lower tail** (2.5pct = −0.460). The estimate is fragile to *which observations* enter training.

The locked PASS required BOTH. The bootstrap lower bound crossing zero triggers H13-null exactly as written ("does not survive resampling … bootstrap 2.5pct≤0"). **This is the 9b pattern** (lit/55: a +3.62 single-seed advantage washed to +1.24±4.88): a positive point estimate + positive cell-level resample, undone by a finer resample. Had Probe 13 judged on the +0.768 anchor or the leave-2-out alone — as the earlier post-hoc temptation would have — it would have falsely declared transferable triage. The pre-committed gate prevented that.

**Honest characterization:** the within-instrument `R_diff` signal is *not pure noise* (central tendency clearly +0.74), but it is **not robust at the locked 95% bound** — "suggestive, fails the robustness bar," not "confirmed."

## 3. H13-cross + F2 — the deeper reason it doesn't matter: R_diff isn't instrument-portable either

Even granting the within-instrument signal, deployment requires cross-instrument transfer, and that collapses completely:

- **H13-cross R²=−24.5.** Per-cell, the first-life-trained model predicts most second-life cells' SOH within MAE ~0.4–2% but **systematically over-predicts** (e.g. W8 predicted 94.8% vs actual 88.9%, MAE 6.25%) — a domain offset, not random error. The model places second-life cells as if they were still on the first-life rig.
- **F2 R_diff-only domain AUC = 1.000.** First-life vs second-life are *perfectly separable on `R_diff` alone* at matched SOH. So the instrument/state-axis seam (Probe 12 F2, full-6D AUC=1.0) is **not** an `R_ohmic` artifact — it lives in `R_diff` too. The hope that the charge-transfer/diffusion resistance was a cell- and rig-agnostic quantity is refuted.

So `R_diff`-exclusion of `R_ohmic` buys nothing against the domain confound, and the cross-instrument task — the only deployment-relevant one — fails by a wide margin.

## 4. H13-ohmic — contact-normalization mechanism rejected

Per-cell contact-referencing (subtract each cell's freshest R_ohmic per voltage) moved R_ohmic-only LOCO from −239.96 to −202.8 — a marginal, still-catastrophic value. **My §0.1 hypothesis (that R_ohmic's non-transferability is a removable per-cell contact offset) is not supported**: even after referencing each cell to its own fresh state, R_ohmic does not transfer. The non-transferability is not a single additive contact constant; R_ohmic's cell-to-cell behavior is more complex (and partly degenerate after referencing, since the fresh row becomes exactly zero). Mechanistic, not deployment — and negative.

## 5. Disposition (per lit/62 §5)

**SINGLE-SPLIT ARTIFACT.** F1 PASS (signal real within-cell), H13-main FAIL (bootstrap 2.5pct=−0.46 < 0), H13-cross FAIL (R²=−24.5), F2 AUC=1.0 (confound not reduced), H13-ohmic rejected. The locked bucket fires on H13-main FAIL; the cross-instrument + F2 results make the closure unambiguous.

**SOH-TRIAGE ARC TERMINUS.** Across three probes: EIS demonstrably **reads SOH within a cell** (F1 emphatic every time, ρ up to −0.92), but a **transferable cross-cell absolute-SOH model is not achievable on this SECL cohort** — not via wider range (Probe 12), not via ohmic-exclusion at the locked robustness bar (Probe 13 H13-main), and not across instruments (Probe 13 H13-cross R²=−24.5, domain AUC=1.0). Parallels the transference arc terminus: the limit is the cohort (cell count + cross-instrument seam), not the operator. **Deployable read: EIS SOH triage needs per-cell/per-rig calibration; no universal EIS→SOH model on this data.**

## 6. What Probe 13 establishes / does not

**Establishes:**
- The recurring drop-ohmic transfer hint (Probe 11/12) is **not robust** — it fails a pre-committed bootstrap stability gate. The hint was real-in-central-tendency but not claimable, exactly as the F3/9b discipline warned.
- The instrument domain confound is **feature-general** (in `R_diff`, not just `R_ohmic`): `R_diff`-only domain AUC=1.0; cross-instrument R²=−24.5.
- `R_ohmic`'s non-transferability is **not** a removable per-cell contact offset (H13-ohmic rejected).
- Methodological: the locked stability gate converted a tempting +0.768/+0.739 "win" into the correct negative. Three probes of pre-registration discipline converged on an honest arc closure.

**Does NOT establish:**
- That EIS can't read SOH (it clearly can within-cell — F1).
- That transferable triage is impossible in general — only that it is not achievable on *this* ≤6-cell, two-instrument SECL cohort. A larger same-instrument cohort with wide per-cell range remains the untested path, but that is a data-acquisition question, not an analysis one.

## 7. RMD-SRC framing

A predictive-transfer (RMD_F4) probe on a pre-committed, ohmic-excluded feature set, gated by a 9b-style multi-resample stability check. The operator is validated (RMD_F1 emphatic), but transfer fails both the within-instrument robustness bound and the cross-instrument test, and the adversarial domain check (F2) shows the confound is feature-general. The honest disposition — **suggestive central tendency, fails the locked robustness bar, non-portable across rigs** — closes the SOH-triage arc the same way the transference arc closed: a cohort/data limit, not an operator limit.

---

**Lock metadata:**
- Pre-reg lock commit: `be6a5d0`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `778c8c09d6787cb1a4be8649339ec624e45b53d9aa0925767831f2aafa12bd52`
- Result parquet SHA-256: `dbfd983f94f37cc18d43616e580a8ce1679a4a4cc50c43e5d45fec10995234b9`
- Reused first-life parquet SHA-256: `17d66ecef02b1c7ad2181d18189565c4f5c302257cd4fc9a5b2c075f96cb50db` (unchanged)
- Reused second-life parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (unchanged)

## 8. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
