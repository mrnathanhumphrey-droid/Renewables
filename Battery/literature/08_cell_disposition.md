# Cell Disposition — CONSORT-Style Diagram for Phase 1-2 Cohort

**Date:** 2026-05-21
**Source:** Pozzato 2022 dataset README.xlsx (legend: `#`=available, `N`=equipment issue, empty=cell dismissed, `-`=not performed yet)

This document is the cohort-flow record for the C2 study. It lives in the paper's methods appendix as the cell-disposition diagram and feeds the limitations section's discussion of dropout.

---

## Per-cell disposition (first-life cohort, N=10 enrolled)

| Cell | Cycling status | EIS status | HPPC status | Capacity status | Disposition | Mechanism |
|---|---|---|---|---|---|---|
| **W3** | Cycling_1-2 only (75 cyc) | Available Diag_1-3 | Available Diag_1-3 | Available Diag_1-3 | **DISMISSED after Cycling_2** | UNKNOWN — flagged as potentially informative |
| **W4** | Cycling_1-7 (~211 cyc), then no further | EIS **`N`** all diags (equipment) | Available Diag_1-8 | Available Diag_1-8 | EIS missing throughout; cycling halted | EIS = MCAR; cycling halt mechanism unstated |
| **W5** | Cycling_1-14 full (~347 cyc) | EIS **`N`** all diags (equipment) | Available Diag_1-14 (missing Diag_1 HPPC) | Available Diag_1-15 | EIS missing throughout; otherwise complete | EIS = MCAR |
| **W7** | Cycling_1-4 only (116 cyc) | EIS **`N`** Diag_1-5, then empty | Available Diag_1-4 | Available Diag_1-4 | **DISMISSED after Cycling_4** | UNKNOWN — flagged as potentially informative |
| **W8** | Cycling_1-14 full (347 cyc at Diag_15) | Available all 15 diags | Available all 15 diags | Available all 15 diags | ✅ Complete | — |
| **W9** | Cycling_1-14 full (341 cyc) | Available all 15 diags | Available all 15 diags | Available all 15 diags | ✅ Complete | — |
| **W10** | Cycling_1-14 full (350 cyc) | Available all 15 diags | Available all 15 diags | Available all 15 diags | ✅ Complete | — |
| **G1** | Cycling_1-10 (~250 cyc), then "−" | EIS **`N`** Diag_2-11 (equipment) | Available Diag_1-11 | Available Diag_1-11 | EIS equipment issue throughout; **transitioned to second-life** | EIS = MCAR; planned transition |
| **V4** | Cycling_1-10 (244 cyc at Diag_11), then "−" | Available Diag_2-11 | Available Diag_1-11 | Available Diag_1-11 | Diag_1 missing first capacity; **transitioned to second-life** | Planned transition |
| **V5** | Cycling_1-3 (~18 cyc), then empty | Available Diag_2-3 only | Available Diag_2-4 | Available Diag_1-4 | **DISMISSED after Cycling_3** | UNKNOWN — flagged as potentially informative; **transitioned to second-life** |

## Dropout mechanism summary

**Three cells dismissed early** (W3 after 75 cycles, W7 after 116 cycles, V5 after 18 cycles). Pozzato 2022 README does not document dismissal reasons. **Limitation flag:** if dismissal was triggered by anomalous behavior or early-failure detection, this is *informative censoring* and could bias the headline cohort toward cells with normal aging trajectories.

**Three cells with EIS-equipment issues throughout** (W4, W5, G1). Pozzato 2022 README labels these `N` = equipment issues. Cycling and capacity / HPPC continued, so the missing-data mechanism is plausibly MCAR with respect to cell health. These cells contribute to Triad β (HPPC instead of EIS) without bias concern.

**Three cells with full first-life coverage** (W8, W9, W10). These are the cleanest Triad α data and form the basis of the Phase 2.4 proof-of-concept.

**V4 partial** (10 RPTs of EIS, RPTs 2-11): planned transition to second-life testing accounts for the truncated first-life trajectory. Not censoring.

## Second-life cohort (N=6)

V4, V5, W8, W9, W10, G1 (graduated from first-life). Second-life enrollment criterion: cell at approximately 90% SOH. V5's enrollment despite early first-life dismissal indicates the dismissal was for first-life-protocol reasons (e.g., transition to second-life), not for cell-state failure.

Second-life trajectory length:
- 5 cells through RPT 19 with capacity data
- W9 missing capacity at RPTs 17-19 (mechanism not yet investigated)
- EIS coverage at RPTs 5-19 (15 RPTs); RPTs 9-19 require per-cell .DTA parser (next push)

## What this changes in the writeup

1. **Cohort-flow / CONSORT diagram is now the source of truth** for the headline cohort. Cell counts (N=7 first-life with usable data, N=6 second-life, N=13 trajectories total) traceable to documented mechanisms.

2. **Limitations section gains a paragraph on informative censoring.** Three of ten first-life cells (W3, W7, V5) were dismissed for reasons not documented. The remaining seven form the analysis cohort. If dismissal mechanism is health-related, results may overstate stability and understate failure-rate variance. Pozzato or follow-up contact recommended to clarify dismissal reasons.

3. **MCAR equipment-issue cells (W4, W5, G1)** are properly handled by the triad-β architecture — they contribute HPPC features in place of missing EIS. No bias correction needed under MCAR assumption.

4. **Cycle-count mapping is now extractable from README.** The EIS sheet documents cycle count at each diagnostic per cell. This unlocks Phase 3 in real cycle-count units (rather than RPT index proxy).

---

## Cycle counts per (cell, RPT) — for Phase 3 lead-time work

From README EIS sheet (only EIS-bearing diagnostics are tagged; capacity / HPPC RPTs occur at the same cycles):

| Diag | W3 | W4 | W5 | W7 | W8 | W9 | W10 | G1 | V4 | V5 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | N | N | N | 0 | 0 | 0 | N | N | N |
| 2 | 25 | N | N | N | 25 | 25 | 25 | N | 20 | 12 |
| 3 | 75 | N | N | N | 75 | 75 | 75 | N | 45 | 18 |
| 4 | — | N | N | N | 125 | 122 | 122 | N | 70 | 29 |
| 5 | — | N | N | N | 148 | 144 | 146 | N | 95 | — |
| 6 | — | N | N | — | 150 | 145 | 148 | N | 120 | — |
| 7 | — | N | N | — | 151 | 146 | 151 | N | 145 | — |
| 8 | — | N | N | — | 157 | 150 | 159 | N | 170 | — |
| 9 | — | N | N | — | 185 | 179 | 188 | N | 194 | — |
| 10 | — | N | N | — | 222 | 216 | 225 | N | 219 | — |
| 11 | — | N | N | — | 247 | 241 | 250 | N | 244 | — |
| 12 | — | — | — | — | 272 | 266 | 275 | — | — | — |
| 13 | — | — | — | — | 297 | 291 | 300 | — | — | — |
| 14 | — | — | — | — | 322 | 316 | 325 | — | — | — |
| 15 | — | — | — | — | 347 | 341 | 350 | — | — | — |

**Phase 2.4 onset cycle in real cycles:**
- W8 onset at RPT 5 = **148 cycles**
- W9 onset at RPT 4 = **122 cycles**
- W10 onset at RPT 4 = **122 cycles**
- V4 onset at RPT 4 = **70 cycles**

These will replace the "RPT 4-5" placeholders in Phase 3 lead-time computations.

## What about cycle counts for cycling-only diagnostics (capacity, HPPC) when EIS is missing?

The Cycling_test sheet shows per-cell cycles-per-batch. Cumulative cycle count at each diagnostic for triad-β cells (W4/W5/G1) can be reconstructed from the running cycling sum. Computable in Phase 2.4-extension when triad-β is added to the pipeline.
