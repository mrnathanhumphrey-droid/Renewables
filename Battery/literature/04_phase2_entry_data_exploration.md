# Phase 2 Entry — Data Exploration and Conditional Null Model Setup

**Date:** 2026-05-21
**Status:** Phase 2 in flight. Data exploration revealed two findings that reshape the headline pre-reg.

---

## Data structure summary

### First-life SECL (consolidated `.mat` files at `data/secl_first_life/diagnostic_processed/`)

Clean 15 × 10 grid (15 diagnostic timepoints × 10 cells), one entry per (RPT, cell). Cell labels: W3, W4, W5, W7, W8, W9, W10, G1, V4, V5.

**Per-RPT files:**
- `capacity_test.mat` — fields: time, vcell, curr, cap (each is the full capacity-sweep time series, ~71k points at 1 Hz across ~20 hr)
- `EIS_test.mat` — fields: freq, re_z, im_z (19 frequencies × 3 SOC levels per spectrum). Frequency 0.01 Hz – 10 kHz. SOC: 20/50/80%.
- `HPPC_test.mat` — pulse-response time series structured like capacity but ~37k points

### Second-life SECL (extracted at `data/secl_second_life/SL_Dataset_SECL_INR21700-M50T/`)

19 RPTs × 6 cells (G1, V4, V5, W8, W9, W10). EIS only from RPT_5 onward (15 of 19 RPTs have EIS). Capacity stored as raw per-cell `.xlsx` (no consolidated .mat). EIS is denser: 43 frequencies × 3 SOC levels per spectrum.

### Khan 2025 (at `data/khan_2025/`)

22 cells (S1, S3–S17, S19–S26 valid). Capacity at days 0/10/20/40/90. EIS at all timepoints. No continuous thermal.

---

## Finding 1: EIS coverage on first-life is sparse

Actual EIS data availability per first-life cell:

| Cell | Capacity RPTs | HPPC RPTs | EIS RPTs | Notes |
|---|---|---|---|---|
| W3 | 3 | 3 | 3 | Early termination |
| W4 | 8 | 8 | **0** | No EIS measured |
| W5 | 15 | 14 | **0** | No EIS measured |
| W7 | 4 | 4 | **0** | Early termination + no EIS |
| **W8** | **15** | **15** | **15** | **Full trajectory** ✅ |
| **W9** | **15** | **15** | **15** | **Full trajectory** ✅ |
| **W10** | **15** | **15** | **15** | **Full trajectory** ✅ |
| G1 | 11 | 11 | **0** | No EIS measured |
| V4 | 11 | 11 | 10 | Substantial EIS, partial trajectory |
| V5 | 4 | 4 | 2 | Early termination |

**First-life cells with full N=3 (electrical+thermal+EIS) over full trajectory: 3 cells (W8/W9/W10) + 1 partial (V4).**

This breaks the assumption that all 10 first-life cells contribute to the EIS-bearing headline analysis.

## Finding 2: First-life cells don't reach 80%-SOH within the 15-RPT trajectory

Capacity fade across 15 RPTs:

| Cell | Initial cap (Ah) | Final cap (Ah) | Final SOH |
|---|---|---|---|
| W5 | 4.857 | 4.451 | 91.6% |
| W8 | 4.877 | 4.457 | 91.4% |
| W9 | 4.874 | 4.464 | 91.6% |
| W10 | 4.866 | 4.459 | 91.6% |

**None of the cells cross the standard 80%-SOH knee threshold.** The original Phase 3.4 framing of "lead time over single-operator 80%-SOH threshold" is not directly testable on first-life cells alone.

Second-life cells enter at ~90% SOH and decline further over 19 RPTs — they may reach 80% but per-cell capacity trajectories need to be extracted from raw .xlsx files for confirmation.

## Reframe required for Phase 3.4

Replace "80%-SOH threshold" with **capacity-knee-point** as the single-operator comparator. Knee-point can be detected via:
- Curvature-based identification (Zhang/Altaf/Wik 2024 arxiv 2304.11671 method)
- dQ/dV or dV/dQ inflection
- Capacity-curve second-derivative threshold

This is also closer to Ding 2024's "knee-onset to knee-point" framing, which makes the cross-paper comparison cleaner.

**New Phase 3 falsification structure:**
- Disagreement-onset (C2) vs capacity-knee-point (single-operator baseline) — measure lead time in cycle count
- Pre-reg minimum effect floor: 50 cycles at 95% lower credible bound (from Phase 1.8 power calc)
- Acknowledge in pre-reg: 80%-SOH threshold would be a cleaner industrial comparator but is not measurable on this dataset

---

## Phase 2.1 — Exogenous conditioning variables

The operators (capacity, EIS, HPPC, thermal) are functions of cell state AND operating conditions. Conditional null must absorb the operating-condition variance so the residual disagreement-onset signal is interpretable.

**Per-RPT conditioning variables (measured directly):**
- SOC at measurement (3 discrete: 20%, 50%, 80% for first-life EIS; 326/363/400 mV mapping for second-life EIS)
- Ambient T (chamber-controlled: 23 °C first-life, 25 °C second-life)
- RPT temperature (consistent across all RPTs per cell, controlled by chamber)
- Cycle count at RPT (mapping from RPT index to cumulative cycles via cycling_tests folder names: every 25 or 50 cycles)
- Calendar age at RPT (from timestamps in raw data)

**Pre-RPT conditioning variables (from preceding cycling segment):**
- Charging C-rate of preceding segment (encoded in filename: CC_3C, CC_C4, etc.)
- SOC window of preceding segment (encoded: SOC20_80, SOC10_90, etc.)
- Number of cycles in preceding segment (encoded as N25, N50)
- Time elapsed since previous RPT (calendar age delta)

**Cell-level conditioning:**
- Lifecycle stage (first-life vs second-life) — fixed effect
- Cell ID — random effect
- Operator triad available for this cell — fixed effect (heterogeneous cohort)
- Cohort entry SOH (100% for first-life cells, ~90% for second-life)

**Joint conditioning structure:**

Under the design null, each operator's response is modeled as:

```
operator_k(t) | conditions = f_k(SOC, T, cycle_age, calendar_age, cell_id, lifecycle) + ε_k
```

with `ε_k` independent across operators in healthy cells. C2's disagreement-onset signal is the residual correlation between operators (or shift in their independent response) that exceeds the null model's tolerance.

---

## Phase 2 cohort architecture (REVISED post-data-exploration)

Given the EIS sparsity finding, three operator triads are needed to cover all cells:

| Triad | Operators | Cells | Notes |
|---|---|---|---|
| α | electrical + thermal + EIS | First-life: W8, W9, W10 (full), V4 (partial 10/15) | Gold standard cohort |
| β | electrical + thermal + HPPC | First-life: W3, W4, W5, W7, G1, V5 | Replaces EIS with HPPC as third operator. Tradeoff: HPPC has DC-resistance info but lacks EIS frequency-band sub-operator structure |
| γ | electrical + EIS-ohmic + EIS-diffusion | Second-life: G1, V4, V5, W8, W9, W10 (all 6, RPTs 5-19) | No continuous thermal in second-life cycling, so within-EIS frequency-band sub-operators serve as N=3 |

**Effective Phase 3 headline cohort: 16 cells across three triads.**

Heterogeneity is handled in the hierarchical Bayesian model as a triad-fixed-effect plus cell-random-effect. The "operator-agnostic" Phase 0 claim is now operationalized by demonstrating the methodology works on three different operator combinations within one paper.

**Tradeoff:** Triad β (HPPC-based) has not been pre-registered as a Ding-style intra-modal baseline target. Phase 4 mode classification using HPPC alone is a Phase 4 task addition.

---

## Phase 2 task status

- 2.1 ✅ Exogenous conditioning variables specified (above)
- 2.2 ⏳ Hierarchical Bayesian model structure: triad-fixed-effect + lifecycle-fixed-effect + cell-random-effect. Stan or PyMC. To-be-written.
- 2.3 ⏳ Marginal null models per operator — capacity decay model (Severson-style), EIS spectrum decomposition (Cole-Cole or RC-ladder fit), HPPC pulse-response model. To-be-fit.
- 2.4 ⏳ Fit null on early-cycle (fresh-cell) data — RPTs 1-3 from first-life as "fresh" reference.
- 2.5 ⏳ Posterior predictive checks.

---

## What changes in the phase plan

1. **Phase 3.4** must replace "80%-SOH threshold" with "capacity-knee-point" as the single-operator comparator. Adjust pre-reg accordingly.
2. **Phase 4.5** must add a HPPC-based intra-modal Ding-style baseline alongside the EIS-based one.
3. **Phase 2.2** model must specify three operator-triads with appropriate fixed effects.
4. **Cohort table** should explicitly assign each cell to a triad.

---

## Decisions locked (2026-05-21)

1. **Triad β IS in headline cohort.** Frame as operator-agnostic strength. N=16 across three triads is the locked Phase 3 headline cohort.
2. **Dual comparator report.** Primary = capacity-knee-point (curvature-based on N=16). Secondary = 80%-SOH lead time on cell subset that crosses it (likely second-life). Both pre-registered; primary is the headline statistic.
