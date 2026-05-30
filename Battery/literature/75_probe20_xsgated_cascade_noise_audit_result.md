# C3 Probe 20 — Noise-Robustness Audit of the Cross-Substrate-Gated {E1, C2} Cascade RESULT

**Status:** COMPLETE. Disposition = **NOISE-ROBUST.** The Probe-16 re-selected {E1, C2} cross-substrate-gated cascade is **both transferable AND noise-robust** at typical-academic noise (L2 median F=4.21, 2.5pct=2.60, ref p=0.0067) and remains robust through L3 noisy field (median F=4.37). Cross-substrate transferability does **not** come at a noise-robustness cost — and the inclusion of E1 alongside C2 provides additional noise-robustness benefit beyond the modest transfer lift Probe 16 documented.
**Date:** 2026-05-30
**Authored:** Claude
**Pre-reg:** `literature/74_probe20_xsgated_cascade_noise_audit_prereg.md` (lock `c4acbd5`).
**Prior:** Probe 16 (lit/68+69) re-selected {E1, C2} cascade, clean WMG transfer F=3.72 (200-seed median). lit/34 (Paper-2 era) documented 7-op cascade was "barely robust" at L2 (PyBaMM-holdout F=3.19, different cascade/cohort/target).

---

## 0. One-line result

Applying the lit/34 noise grid (multiplicative Gaussian on EIS R-features at locked sigmas) to the Probe-16 cascade and protocol, across 200 noise seeds per (level, feature set), and reference-seed 10k-perm PERMANOVA at each level: **the {E1, C2} cascade passes the locked H20-main at L2 academic noise** — median WMG PERMANOVA pseudo-F=**4.21** [2.5pct **2.60**, 97.5pct 7.76], ref-seed F=4.97 p=**0.0067**. F1 reproduces the Probe-16 clean anchor exactly (L0 median 3.681 = anchor 3.681). F2 confirms noise degrades at L4 (all medians <3). The cascade also **survives L3 noisy field** (median F=4.37, ref p=0.0147) — the single-feature {C2}-only baseline does NOT (ref p=0.097 at L3). Adding E1 to C2 therefore provides **both** modest transfer lift AND a real noise-robustness extension into harder conditions, independent of any selection-procedure consideration.

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** L0 reproduces Probe-16 anchor (~3.68) | within 0.1 | L0 E1C2 median = **3.681** (exact) | **PASS** |
| **F2** noise degrades at L4 | all L4 medians <3 | C2=2.60, E1C2=2.93, E1E2C2=2.75 — all <3 | **PASS** |
| **F3** lit/34 grid is the locked grid | no post-hoc sigma tuning | held to locked sigmas L0–L4 | **PASS** (held) |
| **H20-main** {E1,C2} at L2: median>3 AND 2.5pct>2 AND ref p<0.05 | — | median **4.21** > 3 ✓; 2.5pct **2.60** > 2 ✓; p **0.0067** < 0.05 ✓ | **PASS** |

## 2. Full noise-degradation panel (200 seeds per cell + 10k-perm ref p)

| level | name | feature set | median F | 2.5pct | 97.5pct | ref F | ref p |
|---|---|---|---:|---:|---:|---:|---:|
| L0 | baseline (clean) | C2 / E1C2 / E1E2C2 | 3.26 / **3.68** / 3.64 | (deterministic) | | | 0.024/0.020/0.017 |
| L1 | best lab | C2 / E1C2 / E1E2C2 | 3.28 / **3.67** / 3.72 | 3.11 / 3.49 / 3.40 | 5.03 / 6.17 / 5.64 | 3.22 / 3.58 / 5.38 | 0.025/0.021/0.004 |
| **L2** | **academic (PRIMARY)** | C2 / **E1C2** / E1E2C2 | 3.69 / **4.21** / 4.42 | 2.37 / **2.60** / 2.91 | 6.51 / 7.76 / 7.90 | 3.19 / **4.97** / 5.30 | 0.025/**0.007**/0.004 |
| L3 | noisy field | C2 / E1C2 / E1E2C2 | 3.55 / **4.37** / 4.46 | 1.81 / 2.08 / 2.08 | 7.75 / 11.42 / 9.06 | 2.04 / 4.08 / 5.54 | **0.097**/0.015/0.006 |
| L4 | instrument issue | C2 / E1C2 / E1E2C2 | 2.60 / 2.93 / 2.75 | 0.94 / 1.01 / 0.91 | 8.56 / 10.71 / 7.74 | 2.67 / 3.65 / 2.51 | 0.061/0.012/0.072 |

Key reads:
- **{E1, C2} median F at L2 (4.21) > clean L0 (3.68).** This is a small-cohort PERMANOVA quirk — added measurement noise can occasionally improve apparent class separation in PCA-2 projection by perturbing borderline cells into clearer bins. The more meaningful measure of degradation is the **2.5pct dropping from L0=3.68 to L2=2.60** (still above the locked 2.0 floor). Don't read the median-going-up as "noise helps."
- **{E1, C2} robust through L3** (ref p=0.015, median 4.37); **{C2}-only fails p at L3** (p=0.097). The E1 addition extends robustness, not just transfer.
- **L4 (50% R-noise) defeats all feature sets** — as designed (the locked F2 sanity).

## 3. Interpretation — transferability + noise-robustness are independent gains

Probe 16 already established that the {E1, C2} re-selection beats {C2}-only on clean transfer (F=3.72 vs 3.22). Probe 20 adds: the re-selection ALSO yields a **noise-robustness extension** through L3 that {C2}-only lacks. So the gate's value is multi-axis:
- (lit/35 → P15 lesson) modality-matched training fixes the published cross-substrate NULL.
- (P16 lesson) re-selecting drops trajectory ops, admits E1, gives modest clean transfer (F=3.72).
- (P20 lesson — new) the re-selected {E1, C2} cascade is noise-robust at typical-academic AND noisy-field levels; E1 inclusion is independently justified by noise-extension beyond pure transfer lift.

vs lit/34 reference (different cascade/cohort/target): the 7-op within-substrate cascade was "barely robust" at PyBaMM-holdout L2 (F=3.19 just above 3.0). The cross-substrate-gated 2-op {E1, C2} cascade at WMG-transfer L2 has median F=4.21 — substantially more robust on this cross-substrate task. **Cross-substrate gain does not cost noise-robustness on this cohort.**

## 4. Disposition (per lit/74 §5)

**NOISE-ROBUST.** F1 PASS (anchor reproduces), F2 PASS (L4 degrades), F3 held (locked grid), H20-main PASS at L2. The locked threshold ladder fires the strongest outcome. {E1, C2} is the validated cross-substrate-gated cascade across BOTH transferability (P16) AND noise-robustness (this probe) on the WMG transfer task.

## 5. What Probe 20 establishes / does not

**Establishes:**
- Cross-substrate-gated {E1, C2} cascade is noise-robust at typical-academic L2 AND noisy-field L3 conditions (median F>3, 2.5pct>2, ref p<0.05 at both).
- E1 inclusion beyond C2 provides independent noise-robustness benefit (L3 ref p 0.015 vs C2-only 0.097), not just transfer lift.
- Cross-substrate transferability and noise-robustness are not mutually exclusive — both achievable on the re-selected cascade.

**Does NOT establish:**
- Real-world instrument-noise calibration — multiplicative-Gaussian is the stylized lit/34 model; actual noise distributions differ.
- L4-level (50%) robustness — by design, that level defeats the cascade (and was not the target).
- A re-run of lit/34's PyBaMM-holdout result — different cascade, cohort, target; lit/34's F=3.19 stands as the within-substrate 7-op reference.
- Multi-cohort robustness — still WMG-only (single held-out SOH cohort).

## 6. RMD-SRC framing

A robustness audit (RMD_F2 stability) of a validated predictive-transfer (RMD_F4) result. The {E1, C2} cascade's clean transfer (P16) AND noise-robustness (this probe) both pass at the locked thresholds; the multi-axis validation strengthens the Paper-3 deliverable's claim. The methodological lesson: **cross-substrate-primary selection + modality-matched training simultaneously buys transferability AND noise-robustness on this cohort** — the gate's value is broader than just the lit/35-NULL re-attribution.

---

**Lock metadata:**
- Pre-reg lock commit: `c4acbd5`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `221ee96c1d63d96449e05bf3af7a8053317f49c37861cf18bca0d1dc99c07d04`
- Result parquet SHA-256: `b2190d4d63fc8decec1f6f524c28b6e4d002eae5d4e3b367d05708790097e4eb`
- Reused operator parquets: `paper2_operators_{khan,secl,zhang,wmg}.parquet` (Probe 15/16, unchanged)
- External reference: lit/34 7-op cascade L2 F=3.19 (different cascade/cohort/target)

## 7. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
