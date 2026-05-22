# Phase C3 Probe 5 Pre-Registration — PyBaMM Uniform-Aging-Extent (Magnitude-Confound Test)

**Date locked:** 2026-05-21
**Locked before:** any uniform-anchor PERMANOVA is run on synthetic data, and before the modified Modal app saves per-cycle trajectories.
**Relation to prior pre-regs:** Independent pre-reg. Bonferroni accounting is fresh.

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. Motivation

Probe 4 (literature/20) demonstrated H4 STRONG SUPPORT for material-design
inversion on PyBaMM synthetic data — 2 of 3 design parameters PASSED at
Bonferroni-cleared significance. In that probe, cells naturally aged to **varied
terminal SOH** (PyBaMM `termination="80% capacity"` against nominal 5 Ah;
per-cell SOH at extraction varied across ~85-95% per-fresh-cell).

Probe 2v2 (literature/22) exposed that Severson cohort's Batch 2 (uniform aging
to 80% SOH, balanced bins, n=43) fails within-batch PERMANOVA across MULTIPLE
design axes (first-step C-rate, last-step C-rate, severity, SOC handoff). The
ONLY of these axes that even reaches "weak" within Batch 2 is severity score
(p=0.093, just outside α=0.05). The partial-batch failure is axis-general.

**The hypothesis under test here:** Severson Batch 2's within-batch null could
be driven by an aging-extent × design-condition interaction in the residual-
direction operator triad. Cells with uniform aging extent (Batch 2 hits 80% SOH
cleanly) produce uniform residual magnitudes that suppress the design-direction
signal Probe 4 detected. Cells with non-uniform aging extent (Batches 1+3 with
varied 81-83% SOH endpoints) have magnitude spread aligning with design-condition.

Probe 4's varied terminal SOH may have been what gave it strong signal. If we
re-run synthetic with uniform per-cell aging anchor, does design-direction
signal collapse?

## 1. Hypotheses

**H6-primary:** When 108 synthetic LGM50 cells are simulated under the same L9
Taguchi design as Probe 4, but with **per-cell residual extraction anchored at
the cycle nearest to a uniform 85% per-cell SOH** (eliminating
varied-magnitude across cells), at least one of (cathode_thickness,
transference_number) retains its PASS-or-WEAK-PASS verdict from Probe 4.

**H6-null:** Both cathode_thickness AND transference_number collapse to NULL
under uniform-anchor extraction. Magnitude-spread was the operative variable
in Probe 4's STRONG SUPPORT.

## 2. Simulation protocol (LOCKED)

Same as Probe 4 (literature/19 §2-4), with the following changes:

### Changes from Probe 4

- **Maximum cycles increased from 500 to 800** to ensure all L9 conditions
  reach the 85% per-cell SOH anchor before sim termination
- **Termination criterion:** keep PyBaMM Experiment's `"80% capacity"` (nominal-
  referenced; some cells will hit this before per-cell 85%, others won't —
  that's fine, the per-cell anchor is post-hoc)
- **Save per-cycle trajectory** in the parquet (every cycle's Q_max, R_DC,
  R_total), not just the fresh + aged anchors. This requires modifying
  `code/modal_pybamm_c3.py` to expose the full `rpts` list per cell

### Unchanged from Probe 4

- L9 Taguchi 9-condition × 12-cell design (108 cells total)
- Cell-to-cell ±2% active material volume fraction perturbations, same seeded RNG
- Operator triad: Q_max (per-cycle discharge), R_DC ((V_open − V_30s)/I_1C),
  R_total ((V_open − V_30min)/I_1C). V_open from preceding rest step's last V
- Standardization: pooled-fresh SD across included cells
- Unit-normalize residual to direction vector
- PERMANOVA test, 10000 perms, Bonferroni α/3 = 0.0167, effect-size floor F > 3.0

## 3. Per-cell anchor selection (LOCKED — the key change)

For each cell:
- **Fresh reference** (same as Probe 4): mean of (Q_max, R_DC, R_total) over
  cycles 5-25
- **Aged anchor** (CHANGED): cycle index `k_anchor` where `Q_max[k] / fresh_Q`
  is closest to **0.85 per-cell SOH** (across ALL post-fresh cycles available)

If no cycle achieves SOH ≤ 0.85 per-fresh within the sim's recorded cycles
(cell didn't age enough), use the cell's lowest-SOH cycle and flag as
`anchor_partial`. Per pre-reg §6 INVALID condition: if >30% of cells are
anchor_partial → declare H6 INVALID.

The choice of 0.85 (vs Probe 4's 0.80) is a deliberate target chosen because
in Probe 4 most cells reached 87% SOH but few crossed 80% per-cell. 0.85 should
be achievable for nearly all cells given the bumped 800-cycle ceiling.

## 4. Primary tests (LOCKED)

Same as Probe 4: three per-parameter PERMANOVAs (one per design parameter), each
on the uniform-anchor unit residual vectors.

- PERMANOVA(u_i | cathode_thickness ∈ {low, mid, high})
- PERMANOVA(u_i | transference_number ∈ {low, mid, high})
- PERMANOVA(u_i | particle_radius ∈ {low, mid, high})

Bonferroni α/3 = 0.0167; effect-size floor F > 3.0.

## 5. Falsification thresholds (LOCKED)

Per-parameter verdicts (identical to Probe 4 §8):

- **PARAMETER PASS:** p < 0.0167 AND F > 3.0
- **PARAMETER WEAK PASS:** p ∈ [0.0167, 0.05] AND F > 2.0
- **PARAMETER NULL:** p ≥ 0.05 OR F < 2.0

**H6 verdicts:**

- **H6 SUPPORTS PROBE 4 ROBUSTNESS:** at least 1 of (cathode_thickness,
  transference_number) is PASS OR WEAK PASS. Probe 4's strong signal survives
  uniform-anchor magnitude conditioning. Magnitude-spread was NOT the operative
  variable.
- **H6 EXPLAINS SEVERSON BATCH 2:** both cathode_thickness AND transference_number
  collapse to NULL. Uniform aging-extent eliminates the design-direction signal,
  consistent with Severson Batch 2's pattern. Framework needs a magnitude-
  conditioning step to handle real-cohort heterogeneity.
- **H6 AMBIGUOUS:** mixed outcomes not covered above (e.g., one PASS one NULL).
  Report descriptively.
- **H6 INVALID:** >30% of cells are `anchor_partial` (didn't reach 85% per-cell
  SOH within 800 cycles), OR <70% successful sim completions (matches Probe 4).

## 6. What this probe tests

This probe is specifically a **counterfactual test of the Probe 4 result under a
single methodological perturbation** (uniform anchor vs varied anchor).
Everything else identical to Probe 4.

If Probe 4's STRONG SUPPORT persists under uniform anchor → C3 framework is
robust to aging-extent variation across cells, and Severson Batch 2's null is
either (a) something other than magnitude-confound, or (b) interacts with
real-cell noise that synthetic cells don't have.

If Probe 4's STRONG SUPPORT collapses under uniform anchor → C3 framework's
direction-design inversion is partly an artifact of varied magnitudes within
the cohort, and the framework needs amendment to handle aging-extent-controlled
real cohorts (like Severson Batch 2).

## 7. Compute estimate

Same as Probe 4: ~10 min Modal wall time, ~$1.50 cost. Saving per-cycle
trajectories adds <1 MB per cell → parquet size grows from a few hundred KB
to ~50-100 MB. Manageable.

## 8. Operational protocol (LOCKED execution order)

1. Commit this pre-reg + push to remote. Lock is the commit timestamp.
2. Modify `code/modal_pybamm_c3.py` to:
   - Bump MAX_CYCLES from 500 to 800
   - Save full per-cycle `rpts` list to the parquet (per cell, as a JSON
     string column to keep parquet compatibility)
3. Re-run 108-cell sweep on Modal under same parametric design as Probe 4.
4. Write `code/c3_pybamm_uniform_anchor.py` that:
   - Reads full-trajectory parquet
   - For each cell, picks the per-cell 85% SOH anchor cycle
   - Reports `anchor_partial` count
   - Computes unit residuals + PERMANOVAs per pre-reg §4
   - Applies H6 verdict per pre-reg §5
5. Write up in `literature/24_c3_pybamm_uniform_aging_result.md` regardless of
   direction.

## 9. Explicitly NOT covered

- Re-running real cohorts with aging-extent conditioning — would require
  separate pre-reg (and would change the operator triad if we add an
  aging-extent covariate)
- Mixed-aging-extent synthetic probe (varying aging extent INTENTIONALLY
  across cells within each condition) — this is "the other counterfactual"
  but Probe 4 effectively already tested this since cells aged varied
- Other anchor levels (e.g., 90% SOH, 80% SOH) — only 85% SOH anchor is
  pre-registered here. Alternative anchors would be exploratory

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
