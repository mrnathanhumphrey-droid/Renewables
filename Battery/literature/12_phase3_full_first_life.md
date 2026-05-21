# Phase 3 (extended) — Full First-Life Cohort N=7 Lead-Time Result

**Date:** 2026-05-21
**Status:** Triad β X1 pipeline runs (G1/W4/W5 with HPPC operators). Combined alpha + beta first-life cohort = **N=7**. Direction confirmed (sign test p=0.031); magnitude below pre-reg 50-cycle floor.

---

## Cohort and result

| Cell | Triad | Disagreement onset (cyc) | Knee point (cyc) | Lead time (cyc) | Final SOH |
|---|---|---|---|---|---|
| V4 | α | 70 | 95 | **+25** | 95% |
| W8 | α | 148 | 148 | 0 | 91% |
| W9 | α | 122 | 146 | **+24** | 92% |
| W10 | α | 122 | 151 | **+29** | 92% |
| G1 | β | 37 | 37 | 0 | 94% |
| W4 | β | 123 | 176 | **+53** | 94% |
| W5 | β | 125 | 167 | **+42** | 92% |

## Aggregate

- **N = 7**
- **Mean lead time = +24.71 cyc** (sd 19.75, se 7.46)
- **Two-sided 95% CI on mean: [+6.45, +42.98]**
- **One-sided 95% lower bound: +10.21 cyc**
- Pre-reg falsification threshold: 50-cyc one-sided LCB → **NOT MET**

## Sign test

- 5/7 cells with non-zero lead time, all positive direction
- 0/7 cells with negative lead
- **Sign test p = 0.031** (one-sided, H1: lead > 0)

→ **Direction of C2's first claim is statistically supported.**
→ **Magnitude is below the pre-registered effect size.**

## By triad

| Triad | N | Mean | SD | Lead times |
|---|---|---|---|---|
| α (Q_max + EIS bands) | 4 | +19.50 | 13.18 | [25, 0, 24, 29] |
| β (Q_max + HPPC features) | 3 | +31.67 | 27.97 | [0, 53, 42] |

Triad β cells trend toward larger lead times than Triad α, though confidence interval overlap is substantial at N=3 vs N=4.

## PPC for both triads — both pass

| Triad | Fresh n | Mean d² | KS p | Verdict |
|---|---|---|---|---|
| α | 11 | 2.72 | 0.547 | PASS |
| β | 8 | 2.62 | 0.790 | PASS |

Both triads' pooled-fresh-period covariance reproduces the χ²(3) reference within statistical tolerance.

## Operator-correlation structure differs between triads

**Triad α fresh-period correlations (Q_max, R_ohmic, R_diff):** all |ρ| < 0.20 — operators are nearly independent in healthy cells. This is the "clean" design-null structure.

**Triad β fresh-period correlations (Q_max, R_DC_pulse, τ_pulse):** |ρ| 0.62-0.84 — operators are physiologically coupled (HPPC features share underlying mechanism). The joint Mahalanobis distance still works because PPC passes, but it's measuring deviation from a *correlated* null, not an independent one.

**Implication for C2's framework:** the operator-independence assumption from Phase 2.2 holds well for some operator triads (EIS bands at well-separated frequencies) but is approximate for others (HPPC features). The framework is robust either way (PPC passes both), but the interpretation differs. For Triad β, the "disagreement" being measured is *deviation from the cell-specific correlated baseline*, not from a fully independent null.

This is worth a paragraph in the paper's discussion: not all 3-operator triads are created equal under C2. The cross-operator framework adapts to whatever correlation structure the operator set provides, as long as the fresh-period structure passes PPC.

---

## What this means for the C2 paper

The Phase 3 first-claim ("disagreement onset precedes capacity-knee-point") has **directional support but magnitude shortfall** on the first-life cohort:

- Direction: confirmed (sign test p=0.031, 5/7 positive, 0/7 negative)
- Magnitude: ~25 cycles on average, well below the Ding 2024 reference (280-323 cycles between pressure-knee-onset and capacity-knee-point)
- Why the magnitude gap: Ding used mechanical pressure as a single non-electrical operator with very different physics; C2's cross-operator approach on electrical + EIS or electrical + HPPC measures something more subtle and apparently smaller

This is an **honest small-N exploratory readout that supports the C2 hypothesis directionally**. The pre-reg threshold of 50 cyc was set based on the Phase 0 Ding-scale assumption; on this cohort with these operators, the effect is closer to 25 cyc. Two possible interpretations:

1. **C2 captures a smaller but methodologically distinct signal.** Cross-operator divergence is real (sign test) but operates at a smaller cycle-count scale than pressure-vs-electrical lead time. The methodology still adds value but in a different magnitude regime.
2. **The first-life cohort is too pre-knee for the full effect to show.** Final SOHs are 91-95%; none of these cells are deeply into the post-knee accelerated-degradation regime. The full lead-time effect may only manifest on cells that reach 80% SOH or below, which our cohort doesn't.

**Held-out cohorts can resolve this.** Khan 2025 calendar+cycle 22-cell prismatic + Zhang Cambridge 12-cell + WMG 25-cell NMC811 are the pre-registered cross-validation cohorts. If they show larger lead times at later aging stages, interpretation 2 is supported. If they show similar ~25-cycle effects, interpretation 1.

## What the result does NOT say

- It does not falsify C2. The direction is confirmed and the magnitude is positive at the lower bound.
- It does not confirm C2 at the pre-registered magnitude. The 50-cycle threshold was not met.
- It says nothing about Phase 4 mode-classification. That's a different claim with its own pre-reg (literature/09_phase4_pre_registration.md), and the V4-vs-W cell residual-direction pattern preview is still the strongest qualitative C2 evidence.

## Honest paper-framing draft

> On a cohort of 7 lithium-ion cells, the disagreement-onset metric precedes capacity-knee-point detection by a mean of 24.7 cycles (95% LCB +10.2, sign test p=0.031). The direction is statistically supported; the magnitude is approximately one-tenth the scale of pressure-based early-warning signals reported by Ding et al. (2024). The cross-operator framework adapts to operator triads with different internal correlation structures (PPC passing for both an EIS-band triad and an HPPC-feature triad), supporting the operator-agnostic methodology claim. The mode-classification analysis (Phase 4) is locked in pre-registration before any classifier touches held-out data; that analysis is the place where the framework's mode-discrimination signal is expected to land most strongly.

## Outputs

- `data/processed/mahalanobis_triad_beta.parquet`
- `code/triad_beta_pipeline.py`
- `code/combined_alpha_beta_leadtime.py`
