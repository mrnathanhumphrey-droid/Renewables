# C3 Khan Cross-Substrate Validation — Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any Khan PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/50_khan_cross_substrate_prereg.md`
**Prior:** C3 amendment (lit/47, lock `50c851e` + `275e0cf`). RMD-SRC parent spec at `D:/Resolve Research/RMD SRC Algorithm Specification.docx`. HEAD `275e0cf`.

---

## 0. Framework parentage

This is the C3 amendment's deployment gate per literature/47 §5.1 — the cross-substrate validation that determines whether the amendment is real (transfers off the synthetic PyBaMM substrate) or synthetic-only.

In **RMD-SRC** terms (parent spec §6 "Cross-cell mechanism inference"): this test asks whether the protocol's classifications hold across substrate change. Two-axis cross-substrate change:

- **Substrate axis:** synthetic PyBaMM LGM50 (101 cells, B5' cycling-read aged state) → real Khan 2025 NMC_prism (n=14 cycle cells, instrument EIS at days 0 + 90)
- **Design-type axis:** material parameters (cathode thickness, transference, particle radius) → operating conditions (cell temperature, SOC range, charge rate)

If the amendment's PCA-2-cosine PERMANOVA carries discriminative power across BOTH axis changes, it's an RMD-SRC substrate-generality finding worth promoting. If it fails, we learn whether the gap is substrate-driven (real-cell EIS noise) or design-type-driven (operating vs material conditions).

## 1. Hypotheses (LOCKED)

**H-Khan-main (amendment transfers):** On Khan's 14 cycle cells, the locked C3 amendment architecture (variant iv 6D fresh+aged stacked → centered z-score → PCA k=2 → unit-vector cosine PERMANOVA) achieves ≥ 2 of 3 PASS across the operating-condition design parameters {T_C, soc_range, charge_rate} at Khan's natural instrument noise (no synthetic noise injection).

**H-Khan-null:** ≤ 1 of 3 PASS. Amendment does not transfer at Khan's real-cell measurement noise. Synthetic-to-real gap is the next architectural problem to solve.

**H-Khan-secondary-T (predicted):** T_C is the strongest design discriminator (predicted PASS with the highest F-value). Mechanistic prior: temperature shifts both ionic conductivity (R_ohmic) and electrolyte diffusion (R_diff) consistently across the 3 levels {0°C, 25°C, 40°C}, and these signatures are well-captured in EIS.

**H-Khan-secondary-soc:** soc_range likely PASSES — different SOC windows during cycling produce different aging trajectories that the fresh-vs-aged contrast captures.

**H-Khan-secondary-rate (uncertain):** charge_rate {0.2C-CCCV, 1C-CC} may or may not separate; only 2 levels and rate-aging interactions are subtle in real cells.

## 2. Cohort + data (LOCKED)

- **Khan cycle cells (n=14):** {S6, S15, S16, S17, S19, S7, S20, S21, S22, S23, S24, S5, S10, S11, S12, S13, S14} ... wait, count: cycle cells per `data/khan_2025/cell_conditions.csv`. Cells excluded: S2, S18 (measurements only through Day 20/40 per Khan's notes — insufficient aging trace for Day 90 aged anchor). Cells excluded: S1, S3, S4, S8, S9 (calendar aging — no cycling operating-condition design). Remaining: 14 cycle cells.
- **Fresh-state operators:** Day 0 EIS, highest available SOC bin (≥90% if EIS at SOC=100% exists per Khan's protocol; else closest available).
- **Aged-state operators:** Day 90 EIS, same SOC bin.
- **Operator triad construction per cell:**
  - **Q_max:** day-0 and day-90 capacity from `data/khan_2025/capacity/` (cell-specific capacity-vs-cycle CSVs).
  - **R_ohmic:** Re[Z(f → ∞)] = highest-frequency real-axis intercept from Khan EIS spectrum.
  - **R_diff:** Re[Z(f → 0)] − R_ohmic = low-frequency Warburg-region real value minus R_ohmic.
- Source EIS files: `data/khan_2025/eis_xlsx/{cell}/` or `.../eis_csv/{cell}/`.

**Design-parameter labels (per cell, from `cell_conditions.csv`):**
- T_C ∈ {0, 25, 40} — 3 levels, ~4-6 cells per level
- soc_range ∈ {"0-100", "0-80", "10-90"} — 3 levels
- charge_rate ∈ {"0.2C-CCCV", "1C-CC"} — 2 levels

(Voltage_limits is multicollinear with soc_range — dropped to avoid the 3-vs-3 confound.)

## 3. Architecture (LOCKED — inherits C3 amendment lit/47 §1)

For each cell c ∈ Khan_cycle_14:

1. Compute fresh operator triplet (fresh_Q_c, fresh_R_ohmic_c, fresh_R_diff_c) from Day 0 EIS + capacity.
2. Compute aged operator triplet (aged_Q_c, aged_R_ohmic_c, aged_R_diff_c) from Day 90 EIS + capacity.
3. Stack: x_c = (fresh_Q, fresh_R_ohmic, fresh_R_diff, aged_Q, aged_R_ohmic, aged_R_diff) ∈ ℝ⁶.
4. Center + z-score by pooled cohort SD: z_c = (x_c − x̄) / σ_pooled.
5. PCA decompose: components = eigvecs of Cov(Z) sorted descending; retain top k=2.
6. Project: z_c^(PCA) = z_c · components[:, :2].
7. Unit-vector: u_c = z_c^(PCA) / ‖z_c^(PCA)‖₂.
8. For each design parameter p ∈ {T_C, soc_range, charge_rate}:
   - Cosine distance matrix d_ij = 1 − u_i · u_j.
   - Pseudo-F per Anderson 2001 PERMANOVA.
   - 10,000 label permutations.
   - PASS (p < 0.0167 AND F > 3.0), WEAK PASS (0.0167 ≤ p < 0.05 AND F > 2.0), NULL otherwise.

**No noise injection.** Khan's natural instrument noise IS the test condition — we explicitly want to know whether the amendment transfers at Khan's measurement noise level. (For reference: Khan's EIS instrumentation is mid-tier academic per the literature; not custom-rig sub-Level-1 nor commodity-cycler Level-3+.)

## 4. Falsifiers — RMD-SRC F1–F4 inheritance (LOCKED)

Each Khan falsifier explicitly maps to the parent RMD-SRC falsifier per `D:/Resolve Research/RMD SRC Algorithm Specification.docx` §"Pre-registered falsifiers":

**P-Khan_F1 ↔ RMD_F1 (initial cleanness):** Test whether ≥ 1 of 3 design parameters PASSES at Khan's natural noise *without* further decomposition. If 0/3, the amendment does not apply to this substrate — Khan is RMD_F1 "classical substrate" (well-described by something simpler than the amended C3 architecture). Report and stop; no decomposition.

**P-Khan_F2 ↔ RMD_F2 (decomposition convergence):** Not directly applicable in this single-substrate test — Khan is a flat 14-cell cohort, no recursive sub-decomposition planned. *Marked N/A* in §5 falsifier outcomes. (RMD-SRC F2 fires when sub-decomposition produces leaves below minimum cell size without achieving cleanness; not in scope for this probe.)

**P-Khan_F3 ↔ RMD_F3 (validation agreement):** Test whether PERMANOVA disposition agrees with a post-hoc classical inspection of unit-vector centroids. Specifically, for each design parameter, compute the median unit-vector centroid per level and the pairwise cosine angles between centroids. If PERMANOVA says PASS but pairwise cosines are not visually separable (e.g., all > 0.95 between condition centroids), document as §A inconsistency and flag the PASS as "PERMANOVA-driven, structurally degenerate." If PERMANOVA says NULL but centroids are clearly separable (all pairwise < 0.7), flag as "PERMANOVA-underpowered at n=14, signal exists."

**P-Khan_F4 ↔ RMD_F4 (predictive transfer):** Train-test split for predictive holdout. Randomly hold out 4 of 14 cells (stratified by design parameter, seed=42); fit PCA components on remaining 10 cells; project the 4 held-out cells onto those components; check whether held-out cells classify into their correct design-parameter level by nearest-centroid in the PCA-2 space. Repeat 100 times with different seeds; report mean held-out classification accuracy.

Pre-registered floor: held-out accuracy > 0.5 (above chance + 0.17 for 3-level params, chance + 0.0 for 2-level) on at least one design parameter that PERMANOVA called PASS. If F4 fails on all PASSED params, the PERMANOVA PASS is overfit to the Khan cohort — disposition downgrades.

## 5. Disposition criteria (LOCKED)

| Khan outcome | Verdict |
|---|---|
| **KHAN TRANSFERS** | ≥ 2/3 PASS at Khan natural noise, P-Khan_F1 satisfied, F4 holdout ≥ floor on at least one PASSED param | C3 amendment is real beyond synthetic. Battery substrate gets added to RMD-SRC parent doc's Substrate Applications table as "Done." Paper-ready promotion path opens. |
| **KHAN PARTIAL** | 1/3 PASS | Amendment partially transfers. Document which parameter(s) survived and which failed; investigate the failure mode (real-cell noise on R_ohmic? design-type insensitivity?). |
| **KHAN FAILS** | 0/3 PASS (P-Khan_F1 fires) | Amendment does not transfer at Khan natural noise. Substrate gap is the next architectural problem. Battery substrate added to parent doc as "framework-resistant" pending diagnosis. |
| **KHAN INCONSISTENT** | PERMANOVA-vs-centroid disagreement (P-Khan_F3 fires) | n=14 too small for clean PERMANOVA inference; report and design a larger-cohort follow-up (perhaps after corpus expansion). |
| **KHAN OVERFIT** | F4 holdout fails on all PASSED params | PASSED dispositions are PERMANOVA-overfit at n=14; downgrade by one tier. |

## 6. What this probe does NOT establish

- Not a chemistry-generality claim. Khan is NMC_prism; amendment validated on synthetic LGM50 (NMC-style cathode but different geometry). LFP, LCO, NMC811 are not tested here.
- Not a transference test. Khan doesn't vary cation transference; transference remains irrecoverable per Probe 7+8.
- Not a deployment readiness lock. Even KHAN TRANSFERS only moves the amendment one step closer to paper-ready; additional cohort scale-up (lit/47 §5.3) and possibly a third-substrate test would be needed before a Paper 3 / Paper 4 deployment claim.
- Not an instrument-noise calibration. We don't measure Khan's σ_R_ohmic etc. explicitly; we just use the natural instrument noise as the test condition.

## 7. Operational protocol

1. Sign-off + commit this pre-reg as `literature/50_khan_cross_substrate_prereg.md`. Lock anchor = commit hash.
2. Build `code/c3_khan_cross_substrate.py` — analyzer that:
   - Loads `data/khan_2025/cell_conditions.csv` for design labels
   - Extracts Day 0 + Day 90 EIS spectra from `data/khan_2025/eis_xlsx/{cell}/` or `eis_csv/{cell}/` (high-SOC bin)
   - Extracts Day 0 + Day 90 capacity from `data/khan_2025/capacity/{cell}` 
   - Computes (Q, R_ohmic, R_diff) at fresh + aged per cell
   - Runs PCA-2 + unit-vector + cosine PERMANOVA + F4 holdout
3. Run analyzer. Output: `data/processed/khan_cross_substrate_results.parquet`.
4. Apply §5 disposition + §4 falsifiers.
5. Write up `literature/51_khan_cross_substrate_result.md`.
6. If KHAN TRANSFERS, propose a parent-doc update to add Battery to RMD-SRC Substrate Applications table.

**Cost:** ~30 min analyzer build + ~5 min run. No new data generation (all Khan files exist locally).

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `a49c830`
- Khan cell_conditions.csv SHA-256: `749CD4CFC1C042D43B5944A3926993F98F23EC953B5B725D8AC756504C3D1F7A` (`data/khan_2025/cell_conditions.csv`)
- Analyzer script SHA-256: `<TBD — analyzer built post-sign-off, hash recorded with result lock>`
- Result parquet SHA-256: `<TBD — recorded with result lock>`
