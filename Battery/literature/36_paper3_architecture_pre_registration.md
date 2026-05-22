# Paper 3 — Architecture Pre-Registration: Aging-Mode Cascade with PyBaMM-Labeled Truth

**Date locked:** 2026-05-22
**Locked before:** any PyBaMM aging-mode-labeled synthetic generation, any operator extraction under the new catalog, any noise-injection training, any LOCO selection run, any real-cell cascade scoring under this framework.
**Companion documents:** literature/29 (Paper 2 strict-pre-reg INVALID), literature/31 (Paper 2 amended PARTIAL REPLICATION), literature/34 (Paper 2 noise-robust barely at threshold), literature/35 (Paper 2 cross-substrate NULL). Paper 3 is a SEPARATE paper, not a Paper 2 amendment.

Once committed and pushed, no edits permitted; deviations logged in §11.

---

## 0. Why Paper 3 exists (the diagnostic)

Paper 2's amended-protocol arc (literature/31, 34, 35) bounded the framework's operational regime to: synthetic, low-noise, design-condition-discriminating only. Three failure modes identified at literature/35 §6:

1. **Cross-substrate NULL on real cells** (literature/35: WMG F=0.92, p=0.58)
2. **95% F-reduction under realistic noise** (literature/34: Level 2 F=3.19 barely above 3.0)
3. **Within-substrate PRIMARY inflation** (literature/31: PyBaMM-train→PyBaMM-holdout shares L9 design + simulator + noise model)

The root cause is **target mis-specification**: Paper 2's cascade predicts cohort-specific design labels (PyBaMM L9, Khan aging_type, Severson C-rate tertile). These targets exist nowhere outside their training cohorts. A cascade that maximizes these targets memorizes cohort fingerprints, not substrate-invariant aging structure.

The right reframe is **substrate-invariant target**: aging-mode decomposition {LLI, LAM-NE, LAM-PE, kinetic-R} as continuous fractions. These mechanisms exist in every Li-ion cell; a cascade that predicts mode fractions from observables is substrate-invariant by construction.

This is not an amendment. The selection criterion, target, operator catalog, training procedure, and validation method are all different from Paper 2. This is Paper 3.

## 1. Hypotheses (LOCKED)

**H9-primary (substrate-invariant prediction):** A cascade trained on PyBaMM-labeled aging-mode fractions, using noise-resistant operators with noise-injection training and LOCO ex-ante selection, predicts aging-mode fractions on real-cell cohorts (Khan, Severson, SECL first-life) with **Spearman ρ ≥ 0.50 between cascade-predicted fractions and independent mode-decomposition estimates (IC analysis + EIS-DRT) on at least 2 of 3 real cohorts**.

**H9-null:** Spearman ρ < 0.50 in ≥ 2 of 3 real cohorts. Cascade does not transfer to real cells under independent-method validation.

**H9-secondary (noise robustness):** PRIMARY validation (LOCO across synthetic + real-cohort splits) survives Probe-6 Level 2 noise injection at F > 3.0 AND p < 0.05 with ≥ 70% of the noise-free baseline F retained (vs Paper 2's 5% retention). Tests whether noise-injection training delivers genuine noise robustness.

**H9-secondary-null:** Noise-injection training does not deliver substantial noise robustness; F retention < 70% at Level 2.

**H9-tertiary (mechanistic interpretability):** RF variable importance over the noise-resistant operator catalog assigns interpretable physics meaning. E.g., the "cycles-to-90%-SOH" operator has high importance for LLI fraction; "IC peak height" operators have high importance for LAM-NE/LAM-PE; "R_DC growth rate" has high importance for kinetic-R. Reported descriptively, not gated.

## 2. Aging mode taxonomy (LOCKED)

4-way decomposition per Birkl 2017 / Edge 2022 framework:

| Mode | Symbol | Definition |
|---|---|---|
| Loss of Lithium Inventory | LLI | Cyclable Li trapped in SEI; total Q decreases proportional to LLI |
| Loss of Active Material (negative electrode) | LAM-NE | NE active mass loss; affects capacity at low SOC |
| Loss of Active Material (positive electrode) | LAM-PE | PE active mass loss; affects capacity at high SOC |
| Kinetic resistance growth | kinetic-R | SEI thickening + charge-transfer resistance; affects R_DC profile |

For PyBaMM cells, mode fractions are read directly from simulator state at each cycle:
- LLI(t) = (initial cyclable Li - cyclable Li at cycle t) / initial cyclable Li
- LAM-NE(t) = (initial NE active volume - NE active volume at cycle t) / initial NE active volume (via porosity changes)
- LAM-PE(t) = same for PE
- kinetic-R(t) = (R_DC(t) - R_DC(0)) / R_DC(0)

Reported as fractions in [0, 1]. Mode fractions at each cell's terminal cycle (when SOH reaches ~80%) are the training labels.

## 3. PyBaMM synthetic generation (LOCKED)

**Scope:** **5000 PyBaMM cells**, varied across design + aging-trajectory parameters. Generated via Modal CPU parallel (~$1-5 cost, ~30 min wall clock at 100 parallel CPUs).

**Parameter sweep (LOCKED):**

| Parameter | Range | Sampling |
|---|---|---|
| Cathode thickness | 0.5x - 1.5x Chen2020 default | Uniform within range |
| Transference number | 0.2 - 0.5 | Uniform |
| NE particle radius | 0.5x - 2x default | Log-uniform |
| PE particle radius | 0.5x - 2x default | Log-uniform |
| Initial SEI rate (Yang2017 k_SEI) | 0.5x - 5x default | Log-uniform |
| Charge C-rate (calendar profile) | 0.5C - 4C | Uniform |
| Temperature | 15°C - 45°C | Uniform |

Each cell run with PyBaMM `lithium_ion.DFN` + Yang2017 SEI growth + IDAKLU solver, terminated at "80% capacity" per Probe 4/5/6 convention. Per-cycle (Q_max, R_DC, R_total, V_OCV at 5%, 50%, 95% SOC) recorded plus per-cycle aging-mode fractions.

**Sampling design:** Latin Hypercube Sampling (LHS) over 7-dimensional parameter space, 5000 samples. Random seed = 36000 (literature/36 lock anchor).

**Cells excluded from training (deterministic holdout split):**
- Test split: 500 cells (10%) reserved for cascade validation post-training, NOT used in LOCO selection
- LOCO held-out cohort splits: rotating folds across synthetic + Khan + Severson per §6

## 4. Operator catalog (LOCKED — by mechanism, not extractability)

10 noise-resistant operators chosen by their relationship to specific aging modes:

### Capacity-based (related to LLI + LAM)

1. **N90:** cycle count to first SOH ≤ 0.90 (linear interp on Q_max vs cycle). Replaces T1/T2.
2. **N80:** cycle count to first SOH ≤ 0.80. Replaces T1/T2.
3. **N90_to_N80_ratio:** N80 / N90 — measures whether fade accelerates (kneeing) vs linear. Replaces T3 (knee-onset).

### IC-peak-based (related to LAM-NE / LAM-PE, per Birkl 2017)

4. **IC_peak_low_height:** height of dQ/dV peak in the low-SOC voltage window (3.5-3.7 V), at terminal cycle. LAM-NE signature.
5. **IC_peak_high_height:** height of dQ/dV peak in the high-SOC voltage window (4.0-4.2 V), at terminal cycle. LAM-PE signature.
6. **IC_peak_low_shift:** voltage shift of low-SOC peak from cycle 5 to terminal cycle. LLI signature.

### Resistance-based (related to kinetic-R)

7. **N_R_double:** cycle count until R_DC doubles its fresh value. Replaces T4 (R growth rate).
8. **R_DC_fresh:** R_DC at cycle 5 (fresh-cell baseline).

### EIS-based (related to kinetic-R, where EIS is available)

9. **R_ohmic_fresh:** Re-axis intercept at fresh state (= E1 from Paper 2).
10. **R_charge_transfer_fresh:** R_diff - R_ohmic at fresh state (= E2 from Paper 2).

All operators are scalar per cell. NaN where not extractable.

**Mechanism mapping (mode → operators that are mechanistically informative):**
- LLI: N90, N80, IC_peak_low_shift
- LAM-NE: N90_to_N80_ratio, IC_peak_low_height
- LAM-PE: IC_peak_high_height
- kinetic-R: N_R_double, R_DC_fresh, R_ohmic_fresh, R_charge_transfer_fresh

## 5. Training architecture (LOCKED)

**Algorithm:** Random Forest **multi-output regressor** (sklearn `RandomForestRegressor` with multi-output) predicting 4 mode fractions per cell simultaneously.

**Hyperparameters (LOCKED):**
- `n_estimators = 500`
- `max_depth = 6` (deeper than Paper 2's 4; multi-output regression benefits from more capacity)
- `min_samples_leaf = 10` (regularization for noise-injection training)
- `random_state = 42`

**Noise injection (LOCKED):** Per Probe-6 / literature/32 noise levels {1, 2, 3} only (skip Level 0 because noise-free training is what failed in Paper 2; skip Level 4 because it's beyond realistic deployment range). For each synthetic cell, generate **5 noise replicates per level × 3 levels = 15 noisy copies**. Training set expands from 4500 (5000 - 500 holdout) to **67,500 noisy training cells**.

Noise injection follows literature/32 §3 (multiplicative Gaussian per cycle on Q_max, R_DC, R_total). Per-cell-per-replicate-per-level seed = `36000 + level*1e6 + cell_idx*100 + replicate_idx`.

Training labels (mode fractions) remain noise-free — only the observable trajectories get noise; the targets stay as their PyBaMM ground truth. This trains the cascade to predict CLEAN targets from NOISY observables, which is the deployment goal.

**Loss:** mean squared error across 4 mode fractions (sklearn default for multi-output RF regression). Per-mode R² reported separately.

## 6. LOCO selection gate (LOCKED — ex ante, not post-hoc)

Real-cell cohorts: **Khan (n=19), Severson (n=139), SECL first-life (n=10)**. PyBaMM synthetic generates aging-mode-labeled training data; real cohorts provide cross-substrate selection signal.

**LOCO procedure during operator selection:**

For each operator in the catalog of 10:
- For each of 3 LOCO folds {hold out Khan; hold out Severson; hold out SECL}:
  - Train cascade on synthetic + 2 of 3 real cohorts using ONLY this operator + the 3 always-included physics anchors (N80, IC_peak_low_height, R_DC_fresh — these are mechanism-essential, never dropped)
  - Note: real cohorts contribute observables but NO aging-mode labels during training; treated as semi-supervised regularization via cohort-blinding (force cascade to embed real cells near synthetic neighbors)
  - Score held-out cohort cells through trained cascade, compare to **independent IC + DRT mode-decomposition estimates** (§7) via Spearman ρ on each mode fraction
- **Operator passes LOCO gate** if Spearman ρ ≥ 0.30 between cascade-predicted and IC/DRT-estimated mode fractions on at least 2 of 3 LOCO folds, averaged across 4 mode fractions.
- Operators failing LOCO are dropped from the cascade.

This locks cross-substrate validity at SELECTION time, not at deployment time.

**Bootstrap variance on Spearman ρ:** ρ is computed via 1000 bootstrap resamples of held-out cells; median ρ used for the threshold. Avoids point-estimate fragility on small held-out cohorts (e.g., Khan n=19).

## 7. Independent mode-decomposition methods for real cells (LOCKED)

For real cells, IC analysis + EIS-DRT provide independent (non-cascade) aging-mode estimates. The cascade's predictions are validated against these estimates.

**IC analysis (Birkl 2017):** From per-cycle dV/dQ curves, identify low- and high-SOC peaks at each cycle. Peak height changes track LAM; peak shifts track LLI. Implemented per `code/ic_analysis.py` (to be written).

**EIS-DRT decomposition:** From EIS Nyquist spectra at fresh + aged states, decompose into discrete relaxation timescales. R_ct (charge-transfer) shifts track kinetic-R. Implemented via `pyDRTtools` or equivalent.

For cohorts with both dV/dQ and EIS (Khan): use both methods, take consensus (mean of normalized estimates).
For cohorts with only dV/dQ (Severson): use IC analysis only.
For cohorts with only EIS-snapshot (SECL first-life — limited cycling but EIS at each RPT): use EIS-DRT primarily, supplement with limited IC if dV/dQ extractable.

**Important caveat:** IC + DRT are themselves interpretive methods with their own assumptions. The validation target is fuzzy; ρ ≥ 0.50 is the gate, not ρ → 1.

## 8. Verdicts (LOCKED)

**Cascade-level verdicts:**

- **PAPER 3 STRONG SUPPORT:** H9-primary PASS (Spearman ρ ≥ 0.50 in ≥ 2 of 3 real cohorts, averaged across modes) AND H9-secondary PASS (Level 2 noise retains ≥ 70% baseline F)
- **PAPER 3 PARTIAL SUPPORT:** Either H9-primary or H9-secondary passes, not both
- **PAPER 3 NULL:** Both fail
- **PAPER 3 INVALID:** PyBaMM generation fails OR LOCO drops < 4 operators (insufficient catalog) OR IC/DRT methods unavailable on real cohorts

**Operator-level findings (always reported):**
- Initial 10 → LOCO survivors (with mechanism mapping per §4)
- RF variable importance per mode (LLI, LAM-NE, LAM-PE, kinetic-R)
- Per-mode R² on synthetic-test holdout (500 cells)
- Per-mode Spearman ρ on each real cohort (LOCO fold) with bootstrap CI

## 9. Operational protocol (LOCKED execution order)

1. **Commit + push this pre-reg.** Lock = commit timestamp.
2. **Build `code/paper3_pybamm_generator.py`:** Modal-CPU-parallel PyBaMM at 5000-cell scale with LHS sampling per §3, mode-fraction extraction from simulator state. Output: `data/processed/paper3_pybamm_synthetic.parquet`.
3. **Build `code/paper3_extract_operators.py`:** Re-extract the 10 noise-resistant operators per §4 on synthetic + real cohorts (Khan, Severson, SECL first-life). Outputs per-cohort parquets.
4. **Build `code/ic_analysis.py` + `code/drt_decomposition.py`:** IC analysis on dV/dQ curves; EIS-DRT decomposition. Outputs per-cell aging-mode estimates for real cohorts.
5. **Build `code/paper3_train_cascade.py`:** Multi-output RF regression with noise injection per §5. Train + 5-fold CV on synthetic. Persist trained cascade + scaler + imputer to disk.
6. **Build `code/paper3_loco_selection.py`:** LOCO gate per §6. Output: surviving operators.
7. **Re-train cascade with LOCO survivors only.** Apply to real cohorts. Compute Spearman ρ vs IC/DRT.
8. **Build `code/paper3_noise_audit.py`:** Apply Probe-6 Level 2 noise to trained cascade per H9-secondary.
9. **Apply §8 verdicts.**
10. **Write up in `literature/37_paper3_result.md`.**

Estimated wall clock: ~3-5 sessions (Modal compute + multiple iterative validation steps).
Estimated compute spend: ~$5-30 on Modal (PyBaMM scale + potential re-runs).

## 10. Explicitly NOT covered

- Alternative aging-mode taxonomies (5-way splitting kinetic-R into SEI vs CT; 6-way adding electrolyte loss + mechanical) — locked to 4-way for v1
- Alternative cascade algorithms (gradient boosting, neural network) — locked to RF multi-output regression
- Alternative IC/DRT methods (e.g., neural-network IC peak detection) — locked to Birkl 2017 + classical DRT regularization
- Real-cell teardown validation — destructive, not in scope; cell suppliers don't provide post-mortem data
- Chemistry-specific calibration (LFP, LCO, NMC variants) — single-chemistry framework (NMC811-centric); generalization to other chemistries is Paper-4 work
- Deployment under field conditions (variable temperature, irregular cycling) — synthetic cycling profiles only; field-data adaptation is post-Paper-3

## 11. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-22 | **4-mode taxonomy collapses to 2-mode (LLI + kinetic-R only) for v1.** §2 originally locked {LLI, LAM-NE, LAM-PE, kinetic-R}. v1 cascade trains on {LLI, kinetic-R} only; LAM-NE and LAM-PE are NaN labels and excluded from the regression target. Operator catalog (§4) unchanged. H9-primary threshold "Spearman ρ ≥ 0.50 averaged across 4 modes" becomes "averaged across 2 modes." | **Solver-feasibility-driven, not result-driven.** Two smoke runs (IDAKLU pass + CasadiSolver "safe" pass) on PyBaMM `lithium_ion.DFN` + OKane2022 + "particle mechanics: swelling and cracking" + "loss of active material: stress-driven" produced 60-80% failure rate (timeouts + IDA_CONV_FAIL crashes) across the locked 7-d parameter sweep. The mechanics submodel is the failure point — IDAKLU crashes on edge-of-feasible parameter combinations; CasadiSolver "safe" mode either crashes or times out at 1 hour per cell. Both failure modes are at the PyBaMM solver level, not at our orchestration. Dropping mechanics + LAM extraction (keeping Yang2017 SEI for LLI + kinetic-R) reverts to the proven-stable Probe 4/5/6 configuration (Chen2020 + IDAKLU + EC-reaction-limited SEI). Trigger is identifiable from smoke runs alone (PyBaMM solver behavior on parameter ranges), independent of any cascade-training outcome. Falsification-resistance check: this deviation would have been filed regardless of which operators happen to predict LLI vs LAM well downstream; the trigger is purely PyBaMM-feasibility. v2 of the framework would tackle LAM via either a different mechanics submodel implementation (PyBaMM's "stress-driven" without "particle mechanics: swelling and cracking" — needs separate validation), a real-cell-data-augmented LAM target (e.g., IC-derived LAM fractions on Khan as training labels for that mode), or a different cell modeling framework (DUALFOIL, COMSOL). Lock = next code-commit timestamp before re-smoke. |

---

**Locked at commit:** `3b9e1d6` on `main`, pushed to `origin/main` 2026-05-22.

---

## 12. Addendum — Paper 3 v1 shelved 2026-05-22

### Shelf state

Work proceeded through pre-reg lock (`3b9e1d6`) + Path A scope adjustment (`88977c3`, §11 first deviation: dropped mechanics, 4-mode → 2-mode v1). PyBaMM 5000-cell synthetic generation **completed** (4909 cells successful, 98.2% yield) and labeled with {LLI, kinetic-R} fractions. Operator extraction on synthetic revealed an unanticipated catalog-coverage problem that gates v1 progress:

| Catalog operator | Synthetic coverage | Reason for NaN |
|---|---|---|
| N90, N80, N90_to_N80_ratio | 53-83% | requires cell to cross 90/80% SOH threshold |
| N_R_double, R_DC_fresh | 57-100% | computable from per-cycle R_DC |
| IC_peak_low_height, IC_peak_high_height, IC_peak_low_shift | **0%** | generator did not save per-cycle V curves (no dV/dQ available) |
| R_ohmic_fresh, R_charge_transfer_fresh | **0%** | PyBaMM DFN cycling does not produce EIS spectra |

Net: 5 of 10 locked-catalog operators are NaN on synthetic. The five available operators are all cycle-count or fresh-R-DC based — highly correlated, measuring "aging extent" rather than distinguishing aging *mechanism*. The IC peak operators (3) and EIS operators (2) are precisely the ones that would mechanistically distinguish LLI from kinetic-R; without them, the cascade is likely to learn a 1-2 dimensional "general aging score" rather than the substrate-invariant mode decomposition that motivates Paper 3.

Three resumption paths were considered:

- **A. Train on 5 operators as-is.** Cheap; cascade likely degrades to aging-extent predictor; file §11 second deviation. Rejected: defeats the substrate-invariance claim.
- **B. Re-run generator with per-cycle V-curve saving → recover IC peak operators.** ~1-2 hours of code + another Modal run ($50-100). Mechanistically distinguishes LAM-NE/LAM-PE proxies; net catalog becomes 8 of 10. Selected as the trajectory-forward path.
- **C. Re-run with V-curves + PyBaMM EIS simulation at fresh + terminal.** Full 10-operator catalog. 2-5x compute, $100-200. v2 scope.

**Decision (2026-05-22):** **shelf Paper 3 v1 at commit `88977c3`.** Not willing to spend another $50-100 in this session. Pivot to other work; resume Paper 3 when budget + bandwidth align.

### Trajectory forward when Paper 3 resumes

1. **Modify `code/paper3_pybamm_generator.py` to save per-cycle V + Q discharge curves** (e.g., 50 sample points per discharge step) in the `rpts_json` payload. Adds ~10x to parquet size (estimated ~500 MB at 5000 cells); acceptable for local storage.
2. **Re-run the 5000-cell production** with the modified generator on Modal. Cost projected $50-100, time ~30-60 min wall clock at 100 parallel CPUs (same as v1's actual run).
3. **Extend `code/paper3_extract_operators.py`** to compute dQ/dV from V + Q curves, detect peaks in the 3.5-3.7 V (low SOC) and 4.0-4.2 V (high SOC) windows, and produce IC_peak_low_height, IC_peak_high_height, IC_peak_low_shift per cell.
4. **Validate IC peak operators against PyBaMM ground-truth LLI/kinetic-R** as a sanity check: high-LLI cells should show peak voltage shifts; high-kinetic-R cells should show peak height decreases.
5. **Proceed with §9 steps 5-10**: cascade training (multi-output regression on LLI + kinetic-R, with noise-injection per §5), LOCO selection, real-cohort cascade application, IC + DRT cross-validation.

If step 4 confirms IC peaks track the synthetic-truth modes, Paper 3 v1 is on track. If IC peaks fail to track modes (e.g., Yang2017 SEI doesn't generate the right voltage-shift signatures), then v1 needs a different physics model (likely DUALFOIL or PyBaMM with explicit lithium-plating + electrolyte loss) — a v2-scale redesign.

### State preserved for resumption

- **literature/36** (this document): architecture + §11 Path A deviation + §12 shelf addendum, all locked
- **`code/paper3_pybamm_generator.py`** at `88977c3`: produces working 2-mode synthetic data (Chen2020 + Yang2017 SEI + IDAKLU); v2 will modify to save V-curves
- **`code/paper3_extract_operators.py`** at `88977c3`: 5 working operators on synthetic + cohort stubs (Khan/Severson raw re-extraction TODO)
- **`data/processed/paper3_pybamm_synthetic.parquet`** (gitignored, local-only): 4909 cells with mode-fraction labels; usable for v1.1 (5-operator cascade) without re-running generator if we decide to ship as aging-extent predictor instead of mode decomposition

### Non-Paper-3 next-session pickup pointer

When Paper 3 resumes, it lives in this addendum's §12.5. When the corpus pivots to other work, NEXT.md is updated to point at whatever the new active substrate is. Paper 3 v1 is not abandoned; it is paused pending budget alignment.

---

**Shelf addendum locked at commit:** `e04c275` on `main`, pushed to `origin/main` 2026-05-22.
