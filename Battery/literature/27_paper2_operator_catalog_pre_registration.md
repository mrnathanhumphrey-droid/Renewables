# Paper 2 (Noise-Robust C3 Sequel) — Operator Catalog Pre-Registration

**Date locked:** 2026-05-22
**Locked before:** any data is touched for operator selection on the noise-robust redesign. Gate I (cross-cohort fresh-cell consistency) and Gate II (synthetic + real holdout AUC) thresholds are NOT specified in this pre-reg and will be locked in a separate subsequent pre-reg before any selection analysis runs.
**Relation to existing C1/C2/C3 papers:** This is a **separate paper**, not a continuation. See §0.

Once committed and pushed, no edits to the candidate catalog permitted. New candidates added later constitute pre-reg amendments with full attrition accounting impact.

---

## 0. Scoping: this is a different paper

The existing battery substrate work (literature/00-26) is **Paper 1 (the
independence-framework paper)**. Its core claim is that under a hierarchical
conditional null on N≥3 conditionally-independent operators, joint
disagreement-onset times carry early-warning + design-discrimination
information. The conditional-independence assumption is a **first-class
methodological finding** (literature/06 §"design-null independence is real,
not assumed") and the joint Mahalanobis distance gets its interpretation from
that assumption.

Paper 1 is committed at HEAD: C1 hit, C2 N=7 sign test p=0.031, C3 across 6
pre-registered probes. The independence claim is preserved as the load-bearing
methodological contribution.

**Paper 2 (this pre-reg's scope)** is a noise-robust redesign motivated by C3
Probe 6 (literature/26). Its core claim will be that **redundant,
physically-coupled operators with cascade weighting and cross-validation
sustain design-direction signal at noise levels that obliterate the
independence-based framework.** The two papers share substrate (battery
aging) and tooling (PERMANOVA on residual geometry) but they are
different statistical contributions.

Paper 2 does NOT inherit Paper 1's independence claim. Operators here are
expected to be physically coupled. The cascade architecture handles
covariance; the independence interpretation is explicitly retired for
Paper 2.

## 1. What this pre-reg LOCKS

- The full ex ante candidate operator catalog (§3)
- Each candidate's physics-grounded justification (a documented degradation
  mechanism that should produce a non-zero signal in this operator)
- The classification of each candidate into a physics category (§4) for
  attrition accounting

## 2. What this pre-reg does NOT lock (and what comes next)

- Gate I / Gate II selection thresholds — separate pre-reg before any selection
- Cohort assignment for Gate I vs Gate II holdout — separate pre-reg
- Cascade construction algorithm (logistic regression vs random forest vs
  voting) — separate pre-reg
- Validation cohort identity (which cells held out from selection for final
  PERMANOVA) — separate pre-reg

No data-touching analysis on Paper 2 begins until BOTH this catalog lock AND
the subsequent selection-criteria lock are in place.

## 3. Candidate operator catalog (LOCKED — 12 candidates)

Each candidate is a per-cell scalar feature. Operators marked as requiring
EIS will be evaluated only on cohorts that have EIS data (SECL, Khan, Zhang,
WMG). Trajectory operators require ≥50 cycles of data; EIS-spectral operators
require at least one full sweep.

### Trajectory-shape operators (5 candidates)

These derive from a parametric fit to per-cycle operator trajectories. Fit
form: piecewise model (linear early + exponential late) or simple exponential,
chosen per cohort based on cycle density. Specific form will be locked in the
selection-criteria pre-reg.

| ID | Operator | Physics justification |
|---|---|---|
| T1 | `Q_fade_rate_early` (slope cycles 5-50) | SEI consumption regime: linear Li-inventory loss from continuous SEI growth on negative electrode (Yang 2017, Reniers 2019) |
| T2 | `Q_fade_rate_late` (slope cycles 100+) | LAM-dominated regime: post-knee fade rate diagnostic of active-material loss vs continuing SEI (Birkl 2017) |
| T3 | `Q_knee_onset_cycle` | Curvature inflection point; cycle where degradation mode transitions LLI → LAM+SEI (Severson 2019 paper's headline feature) |
| T4 | `R_DC_growth_rate` (slope) | Impedance growth from contact-resistance increase + SEI thickening (Schindler 2018) |
| T5 | `R_DC_acceleration` (curvature) | Catches sudden impedance jumps from electrolyte decomposition or lithium plating onset (Birkl 2017) |

### EIS spectral-shape operators (3 candidates — EIS cohorts only)

These derive from a parametric fit to per-cell EIS spectra at SOC=50%, T=25°C
(canonical condition). Equivalent-circuit-model fit (R0-RC-RC-Warburg) or
direct geometric extraction.

| ID | Operator | Physics justification |
|---|---|---|
| E1 | `ohmic_intercept` (R0, high-freq Re{Z} crossing) | Contact resistance + electrolyte resistance; sensitive to electrolyte degradation + current-collector adhesion (Schindler 2018) |
| E2 | `charge_transfer_radius` (first semicircle radius) | Charge-transfer kinetic resistance; sensitive to SEI thickening and cathode-side passivation (Dubarry 2017) |
| E3 | `diffusion_slope` (low-freq Warburg slope) | Solid-state diffusion limitation; sensitive to particle-cracking and LAM (Reniers 2019) |

### Cross-operator ratio operators (2 candidates)

These cancel absolute-magnitude calibration errors by taking ratios. Derived
from the trajectory operators above.

| ID | Operator | Physics justification |
|---|---|---|
| C1 | `R_growth_per_Q_lost` (= R_DC_growth_rate / Q_fade_rate_late) | Mode discriminator: LLI = Q lost without R growth (low ratio); LAM+SEI = both coupled (high ratio). Per Reniers 2019 mode-classification |
| C2 | `R_DC_to_R_total_ratio` (impedance-shape proxy) | Charge-transfer vs diffusion dominance; sensitive to particle-scale degradation distinct from interfacial degradation |

### Coulombic-efficiency-derived operator (1 candidate)

| ID | Operator | Physics justification |
|---|---|---|
| CE1 | `CE_drift_per_cycle` (slope of CE-vs-cycle) | Direct proxy for SEI-side reaction rate; CE deviates from 1 by exactly the Li lost to SEI per cycle (Smith 2010, Krause 2018) |

### Distributional / shape operator (1 candidate)

| ID | Operator | Physics justification |
|---|---|---|
| D1 | `dQ_dV_peak_shift` (voltage shift of largest peak in differential capacity curve) | Phase-transition voltage shift diagnostic of electrode-state-of-health; physically grounded in graphite-staging or NMC phase boundaries (Bloom 2010, Dubarry 2017) |

**Total: 12 candidates.** No additional candidates may be added without
pre-reg amendment + full attrition recount.

## 4. Physics-category classification (LOCKED)

For attrition accounting, candidates are pre-classified into 5 physics
categories. Final paper reports attrition rates per category so we can
identify whether one category is universally weak (a real finding) vs whether
attrition is operator-specific:

| Category | Candidates | What it probes |
|---|---|---|
| Capacity trajectory | T1, T2, T3 | LLI / LAM-dominated fade regime |
| Impedance trajectory | T4, T5 | Impedance-growth physics |
| EIS spectral | E1, E2, E3 | Frequency-domain degradation signature |
| Cross-operator ratio | C1, C2 | Mode discrimination via coupling |
| Differential / shape | CE1, D1 | Cycle-to-cycle micro-signatures |

If e.g. all 3 capacity-trajectory operators fail Gate I but EIS-spectral
operators pass, that's a methodological finding ("trajectory features are
universally less cohort-stable than EIS-spectral features for this
substrate") not a fishing-expedition artifact.

## 5. Attrition-accounting structure (LOCKED format for final report)

Paper 2 must report, in this structure, regardless of selection outcome:

```
Initial candidate operators: 12 (per §3)

Gate I (cross-cohort fresh-cell consistency):
  Dropped: <N> operators
    By category:
      Capacity trajectory: <m_1> of 3
      Impedance trajectory: <m_2> of 2
      EIS spectral:        <m_3> of 3
      Cross-op ratio:      <m_4> of 2
      Differential:        <m_5> of 2
  Surviving: <12 - N> operators

Gate II (synthetic + real holdout AUC):
  Dropped: <M> operators (of the Gate I survivors)
    By category: <same structure>
  Surviving: <12 - N - M> operators

Final cascade: <surviving operators by ID>
```

This structure prevents post-hoc operator addition by making the candidate
count load-bearing in the final reporting.

## 6. What cannot be added without pre-reg amendment

- New operator IDs beyond the 12 in §3 — would require amendment with
  physics justification AND impact statement on attrition recount
- Re-categorization of existing operators between physics categories in §4 —
  would require amendment
- Changes to physics justifications in §3 — would require amendment

## 7. Independence assumption — explicitly retired for Paper 2

Per §0, Paper 2 does not inherit Paper 1's conditional-independence claim.
The 12 candidates above are expected to be physically coupled:

- T1 ↔ T4 (Q fade and R growth share SEI-thickening mechanism)
- E1 ↔ E2 ↔ E3 (EIS spectral parameters are fit jointly to the same spectrum)
- C1 ↔ T2 ↔ T4 (the ratio C1 is computed from T2 and T4)
- T3 ↔ {T1, T2} (knee onset is a piecewise-linear changepoint determined by
  the two slopes)

The cascade architecture (locked in subsequent pre-reg) will explicitly
handle covariance via cascade weighting / random-forest variable importance
/ logistic regression with regularization. The interpretation of the final
output is NOT a joint conditional-null Mahalanobis distance; it is a
cascade-derived classification score whose claim is detection capability,
not joint-independence physics.

## 8. Operational protocol (LOCKED execution order)

1. Commit this pre-reg + push to remote. **Lock is the commit timestamp.**
2. Draft separate pre-reg locking Gate I + Gate II + cascade + holdout
   cohort definitions. Lock that pre-reg before any data is touched for
   selection.
3. Only after BOTH pre-regs are locked, begin operator extraction on the
   12 candidates across the 4-5 cohorts.
4. Run Gate I; report attrition per §5 structure.
5. Run Gate II on Gate-I survivors; report attrition.
6. Build cascade on Gate-II survivors per separate-pre-reg specification.
7. Validate on locked holdout cohort.
8. Write up Paper 2 with the attrition structure as a load-bearing section
   of methodology.

## 9. Explicitly NOT covered by this pre-reg

- Selection threshold values (Gate I CV cutoff, Gate II AUC cutoff)
- Cascade construction algorithm
- Validation cohort identity
- Real-cell vs synthetic mixing strategy in Gate II
- Cross-cohort weighting in cascade
- Noise-injection tests on the cascade (analog of Probe 6 for Paper 2)
- Comparison-with-Paper-1 framing for any joint discussion

All of the above are downstream pre-reg work to be done before any
selection analysis is run.

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
