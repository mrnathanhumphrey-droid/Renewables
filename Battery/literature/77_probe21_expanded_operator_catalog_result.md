# C3 Probe 21 — Expanded Operator Catalog Under the Cross-Substrate-Primary Gate RESULT

**Status:** COMPLETE. Disposition = **EXPANDED-GATE-IMPROVES.** The cross-substrate-primary gate, applied to a 17-operator catalog (12 existing + 5 new EIS-snapshot W-operators), admits **3 of the 5 new operators** and re-selects {E1, C2, W1, W3, W5}. The expanded cascade lifts WMG transfer 200-seed median F from Probe-16's **3.72 to 5.70 (+53%)** while preserving noise-robustness at L2 academic (median F=6.04, p=0.005). The Paper-3 deliverable substantively strengthens; the gate's discrimination is reaffirmed (it correctly admitted 3 physically-grounded operators and rejected 2 weaker ones).
**Date:** 2026-05-30
**Authored:** Claude
**Pre-reg:** `literature/76_probe21_expanded_operator_catalog_prereg.md` (lock `ddcb429`).
**Prior:** Probe 16 (lit/68+69) re-selected {E1, C2} under the XS-primary gate (WMG transfer F=3.72). Probe 20 (lit/74+75) showed {E1, C2} is noise-robust at L2 (F=4.21). lit/76 §0 motivated the expansion: the existing catalog discarded 58 of 60 mid-frequency points per WMG spectrum.

---

## 0. One-line result

W-operators extracted on Khan (19/19), WMG (19/19), SECL first-life (6/10 — the 6 EIS-equipped cells per Probe-12 / Probe-18 inventory). All 5 W-ops are extractable on the held-out WMG snapshot. XS-primary procedure on the 17-op catalog admits **{W1_warburg_slope, W3_peak_neg_im_norm, W5_arc_chord_length}** as new operators, joining {E1, C2} from Probe 16. Two new ops correctly dropped: W2 (Khan AUC=0.500, chance) and W4 (W-CV stability 1/2, cell/fixture-specific). Re-selected {E1, C2, W1, W3, W5} clean WMG transfer median F=**5.70** [3.14, 7.53], ref p=**0.019**; L2 noise median F=**6.04** [3.57, 13.12], ref p=**0.005**. Probe-16 baseline reproduces exactly (3.724 vs anchor 3.72). All locked thresholds clear.

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** extraction sanity | ≥3 of 5 W-ops extractable on WMG + ≥2 training | 5/5 on WMG; W-ops on Khan + SECL (2 training cohorts) | **PASS** |
| **F2** anchor reproduces | Probe-16 {E1,C2} clean F=3.72 ± 0.1 under new pipeline | median F = **3.724** | **PASS** (exact) |
| **F3** procedure-not-headline judged | catalog locked; no post-hoc threshold tuning | held | **PASS** |
| **F4** no post-hoc threshold tuning | XS-1/2/3 thresholds frozen at Probe-16 settings | held | **PASS** |
| **H21-extraction** | ≥3 of 5 W-ops extractable broadly | 5/5 on WMG + Khan, 5/5 on SECL (6 cells subset) | **PASS** |
| **H21-selection** | ≥1 new W-op admitted by XS-primary | **3 admitted** (W1, W3, W5) | **PASS** |
| **H21-main** | clean median F>4.5 AND 2.5pct>3 AND p<0.05 | median **5.70**, 2.5pct **3.14**, p **0.019** | **PASS** |
| **H21-secondary** | L2 noise median F>3, 2.5pct>2, p<0.05 | median **6.04**, 2.5pct **3.57**, p **0.005** | **PASS** |

## 2. Attrition under XS-primary on the 17-op catalog

| operator | extractable on WMG? | n train cohorts (≥3 finite) | XS-1 | XS-2 (stability) | Khan AUC | XS-3 | **re-selected** |
|---|---|---|---|---|---|---|---|
| T1–T5 (trajectory) | ✗ | 3–4 | ✗ | (pass) | 0.73–0.94 | (pass) | **no** (XS-1) |
| **E1_ohmic_intercept** | ✓ | 3 | ✓ | Gate-I PASS | 1.000 | ✓ | **YES** |
| E2_charge_transfer_radius | ✓ | 3 | ✓ | Gate-I FAIL (2/3) | — | — | **no** (XS-2) |
| E3_diffusion_slope | ✗ | 0 | ✗ | — | — | — | no |
| C1_R_growth_per_Q_lost | ✗ | 4 | ✗ | (pass) | 0.971 | (pass) | **no** (XS-1) |
| **C2_R_DC_to_R_total** | ✓ | 3 | ✓ | Gate-I PASS | 0.971 | ✓ | **YES** |
| CE1 / D1 | ✗ | 1 / 0 | ✗ | — | — | — | no |
| **W1_warburg_slope** | ✓ | 2 | ✓ | W-CV PASS (2/2) | 0.854 | ✓ | **YES** |
| W2_peak_neg_im_log_freq | ✓ | 2 | ✓ | W-CV PASS (2/2) | **0.500** | **✗** | **no** (XS-3) |
| **W3_peak_neg_im_norm** | ✓ | 2 | ✓ | W-CV PASS (2/2) | 0.859 | ✓ | **YES** |
| W4_inductive_tail | ✓ | 2 | ✓ | **W-CV FAIL (1/2)** | 0.971 | (skipped) | **no** (XS-2) |
| **W5_arc_chord_length** | ✓ | 2 | ✓ | W-CV PASS (2/2) | **1.000** | ✓ | **YES** |

**Final re-selected: {E1_ohmic_intercept, C2_R_DC_to_R_total, W1_warburg_slope, W3_peak_neg_im_norm, W5_arc_chord_length}** (5 operators total; 3 new W-ops + the 2 from Probe 16).

The two new-operator rejections are physically interpretable:
- **W2 Khan AUC = 0.500 (chance):** log10(peak −Im frequency) does not separate Khan aging types. The RC-time-constant proxy is too coarse to discriminate Khan's design axes — sensibly dropped.
- **W4 stability fails 1/2:** the HF inductive-tail ratio is cell/fixture-specific (cable inductance, fixture impedance differ per cell), failing the modality-matched CV threshold on Khan. Sensibly dropped.

The gate's procedure correctly admitted the **3 physically-grounded mid-spectrum operators** (Warburg slope, normalized charge-transfer peak height, Nyquist arc length) and rejected the **2 weaker ones**, without any post-hoc tuning.

## 3. Validation panel (WMG transfer, train n=37, 200-seed)

| feature set | dim | clean F median [2.5, 97.5] | ref F | ref p |
|---|---:|---|---:|---:|
| Probe-16 baseline {E1, C2} | 2 | 3.72 [3.35, 4.16] | 3.68 | 0.020 |
| **Expanded {E1, C2, W1, W3, W5}** | **5** | **5.70 [3.14, 7.53]** | **4.55** | **0.019** |

**+53% improvement on the median clean F** vs Probe 16, with comparable p (slightly tighter). The 2.5pct of the expanded set (3.14) is closer to the F=3 floor than {E1, C2}'s 2.5pct (3.35) — the distribution is wider, reflecting the larger feature space contributing additional variance, but still safely above the locked 3.0 threshold.

## 4. Noise audit at L2 academic (lit/74-analog grid, 200 seeds)

| set | dim | L2-noise median F [2.5, 97.5] | ref F | ref p |
|---|---:|---|---:|---:|
| Probe-20 baseline {E1, C2} | 2 | 4.21 [2.60, 7.76] | 4.97 | 0.007 |
| **Expanded {E1, C2, W1, W3, W5}** | **5** | **6.04 [3.57, 13.12]** | **6.99** | **0.005** |

**Noise-robustness preserved and strengthened.** The expanded cascade at L2 has higher median (6.04 vs 4.21) and a 2.5pct (3.57) comfortably above the locked 2.0 floor and above the F=3 PASS threshold. The same small-cohort PERMANOVA quirk seen in Probe 20 reappears (L2 median ≥ L0 median); the 2.5pct shift from clean L0 to L2 (3.14 → 3.57) is positive here, indicating the noise-injected ensemble's lower tail is actually slightly tighter than clean — a small-N artifact, not a claim noise helps.

## 5. Mechanism — why the gate admitted W1/W3/W5 and not W2/W4

- **W1 Warburg slope** captures solid-state diffusion impedance directly — physically distinct from R_ohmic/R_diff endpoints. Stable across Khan + SECL (CV 2/2). Khan aging discrimination AUC 0.854.
- **W3 normalized −Im peak** captures the height of the mid-freq charge-transfer semicircle, normalized to electrolyte resistance. Stable + discriminating (AUC 0.859) — captures kinetic interface impedance.
- **W5 Nyquist arc length** is the most discriminating new operator on Khan (AUC 1.000) — full-spectrum shape complexity is a strong aging signature. Stable across cohorts.
- **W2 peak −Im log-freq** = log10(R_ct·C_dl)^(-1). Within a single chemistry, the RC time constant has limited cell-to-cell variation; the operator hits chance on Khan aging discrimination. The cross-substrate gate correctly dropped it.
- **W4 inductive tail** has strong Khan discrimination (AUC 0.971) but fails modality-matched stability — likely fixture/cable-specific. The gate's XS-2 stability filter correctly dropped it before any false positive could enter the cascade.

## 6. Disposition (per lit/76 §5)

**EXPANDED-GATE-IMPROVES.** All four hypotheses pass (F1 + F2 + H21-selection + H21-main + H21-secondary). The cross-substrate-primary gate, applied to a richer catalog, admits 3 of 5 new operators, re-selects {E1, C2, W1, W3, W5}, and the resulting 5-op cascade transfers WMG SOH at median F=5.70 (clean) / 6.04 (L2 noise) — substantially better than Probe-16's {E1, C2} baseline (3.72 clean / 4.21 noise) while preserving robustness.

## 7. What Probe 21 establishes / does not

**Establishes:**
- The cross-substrate-primary gate is robust under catalog expansion: with 5 candidate new operators added, the gate admits 3 of them and rejects 2 — exactly the procedure-faithful behavior expected.
- Mid-frequency EIS-spectrum operators (Warburg slope, charge-transfer peak, Nyquist arc length) carry **transferable** SOH information beyond the R_ohmic/R_diff endpoint summary the existing catalog used.
- The Paper-3 deliverable's cross-substrate transfer F improves +53% under the expanded catalog while preserving noise-robustness.
- The locked procedure's selectivity is reaffirmed: W2 (chance Khan AUC) and W4 (cohort-unstable) correctly dropped without intervention.

**Does NOT establish:**
- A strong/deployable transfer claim — WMG n=19, single held-out SOH cohort. Effects are modest in absolute terms (F ~5–6 vs the F>>10 strong-discrimination regime).
- Generalization to substrates beyond NMC811 / snapshot-EIS.
- That this is the "complete" operator catalog — Cole-Cole depression angle, ZARC fits, equivalent-circuit residuals are deferred.
- Zhang's contribution is unchanged (W-ops not extracted on Zhang due to differing raw-EIS format; deferred follow-up).
- Anything for the within-substrate (PyBaMM-holdout F=57) Paper-2 results — no change.

## 8. RMD-SRC framing

A catalog-expansion validation under a locked cross-substrate-primary procedure (RMD_F4 transferability + RMD_F2 robustness). The gate procedurally admitted exactly the physically-grounded operators that should pass (mid-spectrum Warburg + charge-transfer features) and rejected ones with structural weaknesses (chance discrimination, fixture-specific instability). Strengthens the Paper-3 deliverable while maintaining the discipline: re-selected set is data-determined by the locked procedure, not hand-picked.

---

**Lock metadata:**
- Pre-reg lock commit: `ddcb429`
- Result commit: `<recorded in this commit>`
- Extractor SHA-256: `38597c7ec27422c70b7402cdc7c35bc7c03913cb4625d5338322803929fd26f7`
- Analyzer SHA-256: `f8350043585d31fc1647abc41478d3f4904202c167387801e3b66291dbe1de1d`
- Augmented parquets SHA-256:
  - `paper2_operators_khan_v2.parquet`: `d7e9da2acd5762a60245725371814431204b71a2e59202027f45bf6a9e5e9d63`
  - `paper2_operators_wmg_v2.parquet`: `13f30d214cf5f05f71020c494f80352259cbd3e4812c018ff566c4c3ecaa7783`
  - `paper2_operators_secl_v2.parquet`: `f5eb19315d5ad5a38198eb16ec1f77d617fecb785d7b1fa8365c73ca66c03e44`
- Result parquet SHA-256: `9c7a15091a6ba15d10082f9fdbad37c21873c4e7b242037ae8b14813a83370e4`
- Reused (unchanged): `paper2_gate_I_v2_results.parquet`, `paper2_gate_II_v2_results.parquet`, `paper2_operators_zhang.parquet`, `paper2_operators_severson.parquet`

## 9. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
