# Phase 1.8 — Rough Power Calculation for N=16 Heterogeneous Headline Cohort

**Date:** 2026-05-21
**Cohort locked:** Option B, N=16 INR21700-M50T cells
**Purpose:** Sanity-check that N=16 is adequate for the headline lead-time claim before committing to Phase 2 model fitting.

---

## What we're trying to detect

Per the revised Phase 0 claim and the Ding 2024 anchor:
- **Effect of interest:** cycle-count lead time between inter-operator disagreement onset and 80%-SOH capacity threshold
- **Reference effect size (Ding):** 280-323 cycles between knee-onset (pressure) and knee-point (capacity). C2's lead time is a structurally different signal but the same scale.
- **Minimum useful effect (C2):** the lead time has to be meaningfully larger than the RPT timing resolution (±12.5 to ±25 cycles). Anything under ~50 cycles is in the noise floor.

## Headline statistic

Per-cell lead time `L_i = cycle_threshold_i − cycle_disagreement_i`, then population mean `μ_L = E[L_i]`.

**Hypothesis:** `μ_L > 0` (disagreement precedes threshold) with a population-level credible-interval lower bound that excludes zero and exceeds the RPT resolution floor.

## Per-cell measurement structure

| Lifecycle | Cells | RPTs/cell | Total RPT-cell observations |
|---|---|---|---|
| First-life | 10 | ~15-20 (every 25-50 cycles over 23-28 months) | ~150-200 |
| Second-life | 6 | 19 | 114 |
| **Total** | **16** | | **~265-315 RPT-cell timepoints** |

Per-cell lead time `L_i` is itself derived from the cell's RPT trajectory — not a single measurement. The within-cell signal-to-noise for estimating `L_i` is what matters most.

## Rough power assessment

### Cell-level Bayesian one-sample test (conservative — ignores within-cell repeated structure)

Assuming population SD of per-cell lead times σ_cell ≈ 100 cycles (a reasonable guess given Ding's NMC/LFP knee-onset variability):

- Cohen's d detectable at 80% power, α=0.05, N=16: ≈ 0.74
- Translates to **minimum detectable effect ≈ 74 cycles**

This is comfortably below Ding's 280-323 scale. Even with the cohort-heterogeneity penalty of mixing first-life and second-life operator sets, the headline lead-time claim should land cleanly if the underlying signal is real at the Ding scale.

### Hierarchical model with within-cell pooling (closer to actual Phase 2 setup)

With cell-level random effects and within-cell repeated RPT measurements, the effective sample size scales above 16. Conservatively:

- If within-cell measurements give effective ESS multiplier of 2-3× (intra-cell correlation ρ ≈ 0.5-0.7), effective N ≈ 32-48
- Minimum detectable effect drops to **~35-50 cycles** — at the resolution floor

### Marginal cases — where power is borderline

- **Sub-50-cycle lead times:** below RPT resolution. Can't claim those honestly regardless of N.
- **Heterogeneity between lifecycle stages:** if first-life and second-life have systematically different lead times (because second-life uses EIS sub-operators instead of thermal), the Phase 2 hierarchical model needs a lifecycle-stage fixed effect. With only 10 + 6 split, that fixed effect is identified but the uncertainty is non-trivial.
- **Mode-classification confidence intervals (Phase 4):** with N=16 cells × handful of mode labels per cell, per-mode posterior intervals will be wide. Expand to N=38 by adding Khan 2025 prismatic cells for Phase 4 specifically (already in plan).

## Verdict

- ✅ **N=16 is adequate for the headline lead-time claim** at Ding-scale effects (200+ cycles)
- ⚠️ **Tight at 50-100 cycle scale** — pre-reg should commit to one of:
  - (a) reporting the credible-interval lower bound and accepting null if it doesn't exceed the RPT resolution floor (~25 cycles), or
  - (b) pre-specifying a minimum-effect threshold of 50 cycles
- ⚠️ **Lifecycle-stage fixed effect uncertainty** — flag in pre-reg as a known limitation. Acceptable cost of the cohort extension.
- ❌ **Below 50 cycles** — claim impossible with this dataset, regardless of model. Resolution floor is real.

## What this changes in the phase plan

Phase 3.4 (falsification criterion / pre-registered effect size) should be locked at **50 cycles minimum lead time at 95% lower credible bound**. This is 4-5× the RPT resolution floor and ~1/5 the Ding magnitude — conservative enough to be a meaningful test, generous enough to land cleanly if the signal exists.

Phase 2 should:
- Build the hierarchical Bayesian model with cell-level random effects + lifecycle-stage fixed effect
- Pre-specify intra-cell correlation prior (informative based on Severson within-cell consistency literature)
- Run posterior predictive checks on the operator-level joint distributions before fitting the disagreement-onset metric

---

## Bottom line

N=16 cohort is good enough to do the work. Headline pre-reg can land at 50-cycle minimum lead-time threshold. Below that, the dataset can't support the claim and we honestly report null.
