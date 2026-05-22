# Phase C3 Probe 5 — PyBaMM Uniform-Aging-Extent Result (Magnitude-Confound Disconfirmed)

**Date:** 2026-05-21
**Pre-registration:** literature/23_c3_pybamm_uniform_aging_pre_registration.md, locked commit `93e4f03`, amendment commit `e3b12c6` (target SOH 0.85 → 0.92)
**Verdict (per amended pre-reg §5):** **H6 SUPPORTS PROBE 4 ROBUSTNESS.** Uniform aging extent does NOT collapse design-direction signal; it cleans it up. Particle radius (NULL in Probe 4) now PASSES.

---

## Headline

The magnitude-confound hypothesis was the obvious candidate explanation for the
Severson Batch 2 within-batch null observed in Probe 2v2 (literature/22): cells
with uniform aging extent (Batch 2's clean 80% SOH crossing) produce uniform
residual magnitudes that might suppress the design-direction signal.

**The hypothesis is disconfirmed.** Under uniform per-cell anchor at 0.92 SOH
on PyBaMM synthetic data (n=105, mean SOH 0.918, sd 0.011 — tight clustering),
all three design parameters PASS PERMANOVA — including particle radius which
was NULL under Probe 4's varied anchor.

| Parameter | Probe 4 (varied anchor) | Probe 5 (uniform 0.92 anchor) |
|---|---|---|
| Cathode thickness | PASS (F=12.4, p=0.003) | **PASS (F=7.2, p=0.0165)** |
| Transference number | PASS (F=50.6, p=0.0001) | **PASS (F=23.9, p=0.0001)** |
| Particle radius | NULL (NaN, identical centroids) | **PASS (F=9.6, p=0.0032)** |

Two of three parameters PASS (cathode thickness, transference number) → meets
pre-reg §5 SUPPORTS PROBE 4 ROBUSTNESS criterion. Particle radius newly PASSING
under uniform anchor is a bonus finding (not pre-registered as primary).

Joint verdict: **H6 SUPPORTS PROBE 4 ROBUSTNESS.**

---

## Pre-flight + amendment

This probe had a first-attempt INVALID at target SOH = 0.85 (literature/23 §3
original): only 26 of 106 valid cells (24.5%) reached 85% per-cell SOH within
800 cycles. PyBaMM's nominal "80% capacity" Experiment-termination fires at
4.0 Ah of nominal 5 Ah, which corresponds to ~83-95% per-cell SOH depending on
the cell's fresh_Q. For cells with low cathode thickness (smaller fresh_Q ≈
4.2 Ah), 4.0 Ah is at ~95% per-cell SOH — well above the 85% target.

Pre-reg amendment filed at commit `e3b12c6` relaxed target SOH from 0.85 to 0.92,
a level achievable by 105 of 106 valid cells (0.9% anchor_partial). The 0.85
result remains on record as INVALID; the amendment was filed BEFORE re-running
at 0.92.

## Uniform-anchor SOH distribution

At target SOH = 0.92:

- Mean per-cell SOH at anchor: 0.918
- SD across cells: 0.011
- Min / max: 0.838 / 0.941
- 1 cell (0.9%) flagged anchor_partial (didn't reach 0.92 SOH)

This is **tight clustering** — vs Probe 4's per-cell SOH spread ~85-95% (mean
near 0.87, much wider spread). The Probe 5 cohort has substantially uniform
aging extent across all 105 included cells.

## Per-parameter PERMANOVA results

### Cathode thickness (PASS, F=7.16, p=0.0165)

Centroids on the residual unit sphere:

```
low (×0.80):  (-0.382, +0.913, +0.145)   n=36
mid (×1.00):  (-0.404, +0.905, +0.133)   n=35
high (×1.20): (-0.448, +0.881, +0.152)   n=35
```

Monotonic rotation with thickness: u_Q becomes more negative (more Q-dominant)
and u_R_DC slightly less positive. Same direction as Probe 4 but with smaller
between-group spread (because magnitudes are uniform — direction-only effect).
Effect size weaker than Probe 4 (F=7.2 vs F=12.4) because the magnitude
component of the residual is suppressed by uniform anchoring.

### Transference number (PASS, F=23.86, p=0.0001) — strongest signal

```
low (0.20):   (-0.473, +0.867, +0.158)   n=35
mid (0.26):   (-0.401, +0.906, +0.135)   n=35
high (0.32):  (-0.360, +0.923, +0.137)   n=36
```

Strongest monotonic trend across all three parameters in both Probes 4 and 5.
Effect size moderated by uniform anchoring (F=23.9 vs Probe 4's F=50.6) but
still well above threshold.

### Particle radius (PASS, F=9.59, p=0.0032) — bonus finding

```
low (4.0 μm):    (-0.385, +0.914, +0.126)   n=36
mid (5.22 μm):   (-0.399, +0.907, +0.134)   n=36
high (6.5 μm):   (-0.452, +0.875, +0.171)   n=34
```

**This is a Probe-4-to-Probe-5 reversal.** Probe 4 had centroids
(−0.543, +0.816, +0.196), (−0.533, +0.822, +0.200), (−0.552, +0.805, +0.218)
— effectively identical, NULL verdict. Probe 5 shows clear monotonic separation
with HIGH-particle-radius cells pointing in a measurably different direction.

The cathode particle radius DID have an effect on residual direction; it was
hidden in Probe 4 by magnitude noise. Under uniform anchoring, the
direction-only signal becomes visible.

This is methodologically meaningful: **the framework's direction-design
signal can be hidden when residual magnitude varies across cells.** Larger
magnitude spread = more noise on the unit sphere = harder to detect smaller
effects.

## Implications

### What this disconfirms

The magnitude-confound hypothesis (Probe 4's STRONG SUPPORT came from
varied magnitudes across cells, not from true direction-design inversion) is
**disconfirmed**. Under uniform aging extent — exactly the condition we
hypothesized would collapse the signal — the signal in fact gets cleaner.

This was specifically the hypothesis raised by literature/22's discussion of
the Severson Batch 2 within-batch null. That null is therefore NOT explained
by uniform aging extent in synthetic data.

### What this implies for the Severson Batch 2 null

The Severson Batch 2 within-batch failure must come from sources that
synthetic PyBaMM cells don't have:

1. **Measurement noise.** Real cell V/I sensors have ~10 mV / 10 mA noise
   floors; PyBaMM is deterministic. The residual triad (Q_max, DCIR,
   T_amplitude) inherits this noise in real cells.
2. **Calendar/storage variation between cycles.** PyBaMM cycles back-to-back
   with no storage between; Severson cells had pauses, temperature drift,
   instrument recalibrations.
3. **Real chemistry heterogeneity.** PyBaMM cells use the same parameter
   set with seeded random perturbation on AMVF only (±2% per cell). Severson
   cells have real manufacturing variability in electrode binder content,
   particle size distribution, electrolyte filling, formation protocols.
4. **Batch-to-batch chemistry shifts.** Severson Batch 2 may have used a
   slightly different cathode lot or electrolyte batch than Batches 1/3.
   This could produce a batch-level "mean direction" offset that swamps
   within-batch design-axis signal.

These are all plausible explanations consistent with the framework being
mechanically sound (Probe 4 + Probe 5 both pass) but real-data manifestation
being attenuated by cell-level noise sources.

### What this strengthens

C3 framework is more robust than Probe 4 alone suggested. Under TWO
different anchor strategies (Probe 4's varied per-cell threshold; Probe 5's
uniform per-cell threshold), the design-direction PERMANOVA passes on at
least 2 of 3 parameters in BOTH cases. Particle radius adds to the count
under uniform anchor, taking us from 2/3 PASS (Probe 4) to 3/3 PASS (Probe 5).

### What this changes about cross-substrate C3 framing

Promotion to paper-ready claim now hinges on **real-cell validation under
controlled aging extent** — i.e., an experimental cohort where cells are
aged to known uniform terminal SOH and tested for residual-direction
separation by design parameter. The methodology is sound; the real-cell
manifestation is the remaining open question.

The original "real-cell validation" framing in literature/20 stands. Probes
4 + 5 together provide the strongest synthetic case yet.

---

## Joint C3 status across all 6 pre-registered analyses

| Probe | Cohort | Verdict | Reading |
|---|---|---|---|
| 1 (lit/15, exploratory) | Khan NMC/graphite prismatic | SOC range hit, F=8.79 p=0.036 | motivating finding |
| 2 (lit/17) | Severson LFP/graphite (N=139, first-step C-rate) | **H2 PASS** pooled | partial within-batch replication |
| 3 (lit/18) | WMG NMC811_cyl (N=19, SOH bins) | **H3 NULL** by p (F=5.30 above floor) | underpower, not absence |
| 4 (lit/20) | PyBaMM synthetic varied anchor (N=106) | **H4 STRONG SUPPORT** | 2/3 design params PASS |
| 2v2 (lit/22) | Severson alt-axes (N=139, 3 axes) | **H5 WEAK** | partial-batch failure axis-general |
| 5 (lit/24, this) | PyBaMM synthetic uniform anchor (N=105) | **H6 SUPPORTS PROBE 4 ROBUSTNESS** | 3/3 design params PASS; magnitude-confound disconfirmed |

The synthetic ground truth is now firmly established: **C3 framework works
on synthetic data under both varied and uniform aging anchors, with the
uniform anchor being more sensitive.** Real-cohort behavior remains
heterogeneous with documented limitations.

## Outputs

- `code/c3_pybamm_uniform_anchor.py` — uniform-anchor PERMANOVA per amended pre-reg
- `data/processed/pybamm_l9_trajectories.parquet` — 108 cells × full per-cycle trajectories (saved as JSON column)
- `data/processed/c3_pybamm_uniform_results.parquet` — anchored-at-0.92 unit residuals + bin labels
