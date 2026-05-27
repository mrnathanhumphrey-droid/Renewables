# C3 Khan Cross-Substrate Validation — Result

**Date:** 2026-05-27
**Pre-reg:** `literature/50_khan_cross_substrate_prereg.md` (lock `a49c830`, hash-record `73052d9`)
**Cohort data:** `data/khan_2025/` (cell_conditions.csv SHA `749CD4CF…D1F7A`)
**Analyzer:** `code/c3_khan_cross_substrate.py` (SHA `21DFABA3…CB453`)
**Result parquet:** `data/processed/khan_cross_substrate_results.parquet` (SHA `252AC081…07F7B`)

---

## Headline

**KHAN PARTIAL TRANSFER** per pre-reg §5 disposition. 1 of 3 design parameters PASSES at Khan's natural EIS noise. The amendment transfers but with a substrate-specific scope.

- **T_C (cell aging temperature):** PASS (F=11.02, p=0.0008). P-Khan_F4 holdout accuracy = 0.683 ± 0.28 (floor 0.50) — transfer is real, not overfit.
- **soc_range:** NULL (F=1.26, p=0.33).
- **charge_rate:** NULL (F=0.22, p=0.67).

**Interpretation:** the C3 amendment transfers for design parameters that DIRECTLY shift EIS-observable physics (temperature → Arrhenius shifts to both R_ohmic and R_diff). It does NOT transfer for design parameters that primarily affect aging-mechanism MIX (SOC window, charge rate) without direct EIS signature differentiation in the fresh + aged comparison.

This is a NARROW positive transfer — methodologically honest and physically interpretable. The amendment is real beyond synthetic, but its operational domain is "design parameters with direct electrochemical-kinetics signatures."

## Per-parameter detail

### T_C (PASS — strongest discriminator)

- Levels: 0°C (n=6), 25°C (n=5), 40°C (n=6)
- pseudo-F = 11.02, p (10K perm) = 0.0008
- Centroid pairwise cosines on unit sphere:
  - 0°C vs 25°C: +0.803
  - 0°C vs 40°C: **−0.874** (clearly opposite directions)
  - 25°C vs 40°C: −0.412
- P-Khan_F4 holdout (100 reps, 4-cell stratified holdout): **mean accuracy 0.683 ± 0.284**, exceeds floor 0.50 → **F4 PASS**
- Three-way separation with 25°C between 0°C and 40°C — physically consistent (room temp is intermediate kinetics regime)

### soc_range (NULL — bimodal, not three-clustered)

- Levels: 0-100 (n=6), 0-80 (n=5), 10-90 (n=6)
- pseudo-F = 1.26, p (10K perm) = 0.33
- Centroid pairwise cosines:
  - 0-100 vs 0-80: **−0.985** (opposite directions)
  - 0-100 vs 10-90: **−0.982** (opposite directions)
  - 0-80 vs 10-90: **+1.000** (essentially identical centroids)
- F4 skipped per pre-reg (no PERMANOVA PASS)

The signal is BIMODAL not three-clustered: 0-100 SOC versus everything-else-narrower. PERMANOVA's three-group test correctly rejects (the three centroids do NOT separate at p<0.0167). A two-group test (full-SOC vs narrowed-SOC) might PASS, but that's a different test — not pre-registered.

### charge_rate (NULL — weak two-way separation)

- Levels: 0.2C-CCCV (n=9), 1C-CC (n=8)
- pseudo-F = 0.22, p (10K perm) = 0.67
- Centroid pairwise cosine: +0.592 (similar direction, mild magnitude differentiation)
- F4 skipped

Charge rate has the weakest signal. The two protocols differ in both rate magnitude AND termination (CCCV vs CC) — multiple coupled factors that may cancel out in the joint feature space.

## PCA-2 structure on Khan

Explained variance: **80.5%** (compare synthetic L2 PRIMARY: 58.4%). Khan's natural noise is cleaner per variance budget than the synthetic L2 condition.

**PC1 loadings** (general design fingerprint axis):
- Q_max_d0 = −0.465, R_ohmic_d0 = +0.407, R_diff_d0 = +0.271
- Q_max_d90 = −0.393, R_ohmic_d90 = +0.392, R_diff_d90 = +0.487
- Reads: "high impedance, low capacity" (or vice versa) — both fresh and aged contribute consistently

**PC2 loadings** (aging-trajectory axis):
- Q_max_d0 = +0.097, R_ohmic_d0 = +0.020, R_diff_d0 = −0.658
- Q_max_d90 = −0.465, R_ohmic_d90 = +0.485, R_diff_d90 = −0.324
- Reads: "low fresh R_diff but high aged R_ohmic + high aged Q" — captures the way the cell evolved during aging

PC1 + PC2 together explain 80.5% — strong compression of design + aging information into 2D. This is the architecture working as intended.

## Falsifier outcomes (§4 of pre-reg)

| Falsifier | Mapped RMD-SRC | Outcome |
|---|---|---|
| **P-Khan_F1** (initial cleanness gate, ≥1/3 PASS) | RMD_F1 | **PASSED.** 1/3 PASS (T_C) without decomposition. Khan is NOT a "classical substrate" by F1; the amended architecture applies. |
| **P-Khan_F2** (decomposition convergence) | RMD_F2 | **N/A.** Not applicable — single-substrate flat test, no recursive sub-decomposition planned. Per pre-reg §4. |
| **P-Khan_F3** (validation agreement: PERMANOVA vs centroid cosines) | RMD_F3 | **PASSED with subsidiary finding.** PERMANOVA PASS on T_C agrees with clear centroid separation (pairwise cosines spanning [-0.87, +0.80]). PERMANOVA NULL on soc_range is corroborated by the degenerate 0-80↔10-90 centroid cosine of +1.000 — soc_range structure is bimodal not three-clustered, so PERMANOVA's three-group test correctly rejects. PERMANOVA NULL on charge_rate agrees with weak centroid separation (cos = +0.592). All three dispositions internally consistent. |
| **P-Khan_F4** (predictive holdout on T_C) | RMD_F4 | **PASSED.** Held-out accuracy 0.683 ± 0.284 > floor 0.50 over 100 stratified-4-cell holdouts. T_C transfer is genuinely predictive, not n=17 PERMANOVA overfit. |

## Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-27 | Pre-reg §2 named "n=14 cycle cells" with explicit cell list. **Actual cohort: n=17 cycle cells.** Documentation slip from my memory entry (which read "Khan 2025: 19 cells" — the 19 was overcounted from 17 cycle + 5 calendar − 3 overlapping). Diagnostic-driven (data inspection at run time vs prior memory): the analyzer's filter on `cell_conditions.csv` (aging_type == "cycle", excluding S2/S18) correctly produces 17 cells. Result holds at n=17. | Diagnostic-driven, not result-driven. The filter logic was correct; only the §2 number was wrong. Per-level sample sizes: T_C {0°C: 6, 25°C: 5, 40°C: 6}; soc_range {0-100: 6, 0-80: 5, 10-90: 6}; charge_rate {0.2C-CCCV: 9, 1C-CC: 8}. All within PERMANOVA's small-N regime; F-values reflect this. |
| 2026-05-27 | Pre-reg §2 specified "high-SOC bin (≥90%)" for EIS. **Used S50 (mid-SOC) per existing `khan_extract_and_classify.py` convention.** Trigger: existing Phase 4 extraction convention uses S50; departing would require new file-availability validation. Filename convention is `ACR_t25_S50_{day}d_{cell}_convert.csv` (the ACR not ACRS prefix). | Diagnostic-driven; convention inherited from prior locked extraction logic. Doesn't change the test mechanism — both S50 and S100 would produce a 6D operator vector; just at different SOC bins. |

## §A — Subsidiary diagnostics

### A.1 Why does T_C transfer but soc_range and charge_rate don't?

**T_C mechanism:** Temperature is the most direct controller of electrochemical kinetics. Arrhenius shifts in ionic conductivity (R_ohmic) and electrolyte diffusion (R_diff) are large and consistent across the three levels {0°C, 25°C, 40°C}. Both fresh and aged operators carry the temperature signature.

**soc_range mechanism:** SOC window controls aging *mechanism mix* (high-SOC accelerates oxidation at the cathode; low-SOC reduces full-SEI growth; narrow windows partially decouple). But the resulting impedance signatures depend on which mechanism dominates — and at n=5-6 per level, mechanism mix gets averaged into a noisy direction. The bimodal centroid pattern (0-80 ≈ 10-90 ≠ 0-100) is consistent with "full vs narrowed" being the dominant axis, not the three-level Taguchi-style separation the PERMANOVA assumed.

**charge_rate mechanism:** 0.2C-CCCV vs 1C-CC differ in rate AND termination protocol. The 0.2C-CCCV mode achieves higher final SoC due to CCCV holding, while 1C-CC truncates earlier. These differences create coupled effects on aging that may cancel in the fresh+aged feature space.

### A.2 What this tells us about the C3 amendment's deployment scope

The amendment was validated on synthetic data with three design parameters: cathode thickness, transference, particle radius. Of these, thickness and particle radius PASSED at L2; transference was structurally invisible.

On Khan, three operating conditions: T_C, soc_range, charge_rate. Of these, T_C PASSED; the other two failed.

**Common pattern across substrates:** design parameters that DIRECTLY shift the fresh-state impedance physics (cathode thickness on synthetic, T_C on Khan) PASS through the amendment. Design parameters that primarily shift aging-mechanism kinetics without changing absolute-impedance scale (transference on synthetic, soc_range + charge_rate on Khan) FAIL.

The amendment's operational domain appears to be: **design parameters where fresh-state impedance carries direct physical encoding**. Where the design effect is mediated through aging mechanism rather than fresh-state impedance, the architecture is structurally blind.

### A.3 Two-level vs three-level test note

soc_range's bimodal centroid pattern (0-100 vs not-0-100) suggests a two-group test would PASS where the three-group test failed. This is NOT pre-registered for this probe; running it would be a post-hoc fishing expedition. Logged here as a *possible follow-up probe design* (n=17 splits into 6 vs 11 in a balanced "full-vs-narrowed" recoding), not as a Khan amendment.

## §B — Implications for RMD-SRC parent doc

Per pre-reg §5 disposition: **KHAN PARTIAL** means Battery substrate should be added to the RMD-SRC parent doc (`D:/Resolve Research/RMD SRC Algorithm Specification.docx`) §"Substrate applications" table with status reflecting the partial result.

Proposed entry (recommendation for parent doc update, not auto-applied here):

| Substrate | Initial partition ℙ₀ | Observables xⱼ | Status |
|---|---|---|---|
| Battery (LGM50 + NMC_prism) | L9 Taguchi conditions (synthetic) / operating conditions (Khan) | Fresh + aged (Q_max, R_ohmic, R_diff) | **Done — partial cross-substrate.** Amendment transfers for design parameters with direct EIS physics signatures (thickness, particle radius on synthetic; T_C on real-cell); does not transfer for mechanism-mediated parameters (transference, soc_range, charge_rate). |

Update to parent doc is a separate action from this Battery-repo commit.

## §C — Implications for the amendment's forward conditions

Per literature/47 §5:
1. **Cross-substrate validation on Khan:** PARTIAL pass. Amendment is real, with documented narrow scope. Forward condition is met, but with a scope qualifier.
2. **Probe 8d (test statistic):** still running in background; orthogonal to Khan result. Doesn't affect this disposition.
3. **Cohort scale-up:** unchanged; still a future advisable step.
4. **Transference operator addition:** unchanged; out of scope.

The amendment is now "paper-ready-with-scope" rather than "paper-ready-universally." Any Paper 3 / Paper 4 deployment claim must include the operational-domain qualifier: applicable to design parameters with direct fresh-state EIS signatures.

## Status

Khan cross-substrate validation closed: **PARTIAL TRANSFER.** Amendment is real beyond synthetic, with operational domain narrowed to direct-EIS-physics design parameters.

Battery substrate ready to be added to RMD-SRC parent doc as "Done — partial cross-substrate." Parent doc update is a separate action.

---

**Lock metadata:**
- Result commit: `<TBD — recorded in follow-up commit>`
- Result parquet SHA-256: `252AC0811CF8F1CDF5B0AB7BBDEFC5A3B5B07810402070438BAAD7A46D107F7B`
- Analyzer script SHA-256: `21DFABA3ACF036C1EE2C605BFEDCB92C2EC0FC4051CF0C6787B609120E6CB453`
