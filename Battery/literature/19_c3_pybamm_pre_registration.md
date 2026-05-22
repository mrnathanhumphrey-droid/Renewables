# Phase C3 Probe 4 Pre-Registration — PyBaMM Synthetic Material-Design Inversion

**Date locked:** 2026-05-21
**Locked before:** any PyBaMM simulation is run on the L9 design matrix; any operator extraction is attempted on synthetic data.
**Reason for pre-reg:** This is the C3 material-design probe (electrode thickness, transference number, particle radius — *true* material-design parameters not available in any public dataset). Pre-registration prevents data-dependent design-parameter choice or operator selection.

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. Why synthetic for C3

C3 probes 1-3 (literature/15, 17, 18) tested **operating-condition** inversion (SOC range, first-step C-rate, terminal SOH). The original C3 deliverable is **material-design** inversion: do residual directions invert under changes to electrode thickness, electrolyte additive composition, particle morphology, etc.?

No public dataset varies material-design parameters in a controlled sweep. PyBaMM (Doyle-Fuller-Newman model implementation in Python) gives us:
- Ground-truth parameter knowledge per cell
- Eliminates batch confound by construction (same simulator, same protocol, only the parameter sweeps)
- Tractable compute (≤10 min per cell sim with Modal CPU parallelism)

The cost: PyBaMM is a model, not experimental data. A synthetic result is necessary-but-not-sufficient evidence for C3 — if the inversion fails in PyBaMM, it likely fails in reality. If it succeeds in PyBaMM, the next step would be experimental validation, not paper-ready claim.

## 1. Hypothesis

**H4-primary:** When three material-design parameters (cathode thickness, transference number, cathode particle radius) are varied across 3 levels each in an L9 Taguchi orthogonal fractional factorial design, **at least one of the three parameters' level labels separates per-cell residual-direction unit vectors** at PERMANOVA pseudo-F > 3.0 and Bonferroni-corrected p < α/3 = 0.0167.

**H4-secondary (descriptive):** Each parameter's effect on residual direction is characterized by per-level centroid directions.

**H4-null:** None of the three design parameters produces residual-direction separation above the pre-registered thresholds.

## 2. Design parameter sweep (LOCKED)

Three PyBaMM parameters, each varied at 3 levels relative to the nominal Chen2020 (LGM50 NMC811/graphite cylindrical) baseline:

| Parameter | PyBaMM parameter name | Nominal | Low | Mid | High |
|---|---|---|---|---|---|
| Cathode thickness | `Positive electrode thickness [m]` | nominal | nominal × 0.80 | nominal × 1.00 | nominal × 1.20 |
| Transference number | `Cation transference number` | 0.2594 | 0.20 | 0.2594 (nominal) | 0.32 |
| Cathode particle radius | `Positive particle radius [m]` | 5.22e-6 | 4.0e-6 | 5.22e-6 (nominal) | 6.5e-6 |

±20% sweep on thickness and particle radius (typical real-world tolerance band).
Transference number absolute values bracket published experimental range (0.20-0.32).

## 3. L9 Taguchi orthogonal design matrix (LOCKED)

9 conditions covering all (parameter, level) combinations in balanced 3×3 fashion. Each (parameter, level) appears in exactly 3 of 9 conditions.

| Condition | Cathode thickness | Transference number | Particle radius |
|---|---|---|---|
| 1 | low | low | low |
| 2 | low | mid | mid |
| 3 | low | high | high |
| 4 | mid | low | mid |
| 5 | mid | mid | high |
| 6 | mid | high | low |
| 7 | high | low | high |
| 8 | high | mid | low |
| 9 | high | high | mid |

Per-condition n: **12 synthetic cells**. Per-parameter level arm: 3 conditions × 12 cells = 36 cells per level. Total cells: 9 × 12 = **108**.

## 4. Cell-to-cell variability (LOCKED)

PyBaMM is deterministic for fixed parameter sets. To produce 12 distinct "cells" per condition, each cell's electrode active-material volume fractions receive an independent random perturbation:

- `Positive electrode active material volume fraction`: nominal × (1 + ε_pos), ε_pos ~ N(0, 0.02)
- `Negative electrode active material volume fraction`: nominal × (1 + ε_neg), ε_neg ~ N(0, 0.02)

Random seed sequence: cell `i` in condition `c` uses seed `1000 + c*100 + i`. Reproducible.

Other parameters held identical across cells within a condition.

## 5. Cycling and aging protocol (LOCKED)

Each synthetic cell undergoes the same cycling protocol:

- Charge: 1C constant current to 4.2 V, then CV to current < 0.05C
- Discharge: 1C constant current to 2.5 V
- Aging: PyBaMM "SEI growth (Yang2017)" submodel for SEI thickening + LLI on the negative electrode
- Termination: cell reaches 80% SOH **OR** 500 cycles, whichever first

RPT cadence: every 25 cycles, record diagnostic operator triad (§6).

## 6. Operator extraction (LOCKED)

Three operators per cell per RPT, matching the framework's triad shape (Q_max + 2 impedance descriptors):

1. **Q_max** = full discharge capacity of the RPT cycle (Ah)
2. **R_DC** = (V at start of discharge - V at 30 s into discharge) / I_pulse — the DCIR analog used for Severson
3. **R_diff** = low-freq impedance from EIS simulation at SOC=50%. PyBaMM `pybamm.experiment` supports an EIS test; use frequency 10 mHz to extract R_diff as Re{Z(10 mHz)}

**Fresh reference per cell:** mean of operator triad over RPTs at cycles 5–25.

**Aged snapshot per cell:** operator triad at first RPT where Q_max ≤ 0.80 × fresh_Q. If 80% SOH not reached within 500 cycles, use the lowest-SOH RPT (analog to "partial_aging" treatment in Severson, literature/17).

**Standardization & unit-vector:** subtract per-cell fresh from aged → raw residual. Standardize each operator by pooled cross-cell-pool standard deviation of the fresh-reference values (using the 108 cells as the fresh pool). Normalize the resulting 3-vector to unit length → u_i.

## 7. Primary test (LOCKED)

Three PERMANOVA tests, one per design parameter:

- PERMANOVA(u_i | cathode_thickness ∈ {low, mid, high}) — 3 arms × 36 cells each
- PERMANOVA(u_i | transference_number ∈ {low, mid, high}) — 3 arms × 36 cells each
- PERMANOVA(u_i | particle_radius ∈ {low, mid, high}) — 3 arms × 36 cells each

Cosine-distance matrix, Anderson 2001 pseudo-F, 10000 permutations per test.

**Bonferroni-corrected significance:** α = 0.05, three tests, α/3 = 0.0167.

**Effect-size floor:** pseudo-F > 3.0 (consistent with literature/16).

## 8. Falsification thresholds (LOCKED)

For each per-parameter test:

- **PARAMETER PASS:** p < 0.0167 AND pseudo-F > 3.0
- **PARAMETER WEAK PASS:** p ∈ [0.0167, 0.05] AND pseudo-F > 2.0
- **PARAMETER NULL:** p ≥ 0.05 OR pseudo-F < 2.0

**H4 verdicts:**

- **H4 STRONG SUPPORT:** at least 2 of 3 parameters PASS
- **H4 SUPPORT:** exactly 1 parameter PASS; 0-1 WEAK PASS
- **H4 WEAK:** 0 PASS but 2+ WEAK PASS
- **H4 NULL:** 0 PASS and < 2 WEAK PASS — synthetic-data probe does not detect material-design inversion at this design + N + operator triad
- **H4 INVALID:** PyBaMM simulation failures cause < 70% of cells to produce valid residuals (any of: solver diverges, aging mechanism crashes, EIS sim fails)

## 9. What this probe CANNOT conclude

- Real-cell results. PyBaMM is a model. A PyBaMM PASS doesn't validate C3 in experimental cells — it shows the framework's *machinery* can in principle invert design parameters under a known generative model. Experimental validation is a separate, much harder probe.
- Effects of design parameters NOT in the L9 sweep (electrolyte conductivity, separator porosity, binder content, current-collector resistance). Out of scope.
- Cross-cohort comparison. PyBaMM operator unit-sphere is on a DIFFERENT unit-sphere than Khan/SECL/Zhang/WMG/Severson (different operator-extraction details). Centroid directions cannot be directly compared.

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |

---

## Signature equivalent

This file's introducing commit is the lock timestamp. Reviewers can verify the lock predates any `data/processed/pybamm_cells.parquet` or any PERMANOVA result on synthetic data.

Compute & infrastructure note: PyBaMM CPU-only, no GPU benefit. Execution on Modal cloud (per-CPU container, ~10 min wall time for 108 cells in parallel) or local multiprocessing (32-core 9950X3D, ~10-15 min). Modal cost estimate ~$1.50; covered by $30/month free credit. Choice of execution venue does not affect the pre-registered protocol.
