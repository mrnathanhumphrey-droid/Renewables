# Phase 4 — SECL Held-Out + Zhang Cambridge Results

**Date:** 2026-05-21
**Status:** Two more cohorts run with the locked classifier. SECL beta + same-cell second-life produces a substantively different verdict from Khan; Zhang Cambridge result is INVALID due to a cycle-alignment issue in capacity extraction.

---

## Result 1 — SECL held-out cells (β cohort + second-life γ)

Pre-registered protocol applied to:
- **Independent held-out (N=3):** first-life β cells G1, W4, W5 (Triad β, never contributed to exploratory pattern)
- **Non-independent same-cell (N=4):** second-life cells V4, W8, W9, W10 (same physical cells as exploratory; reported as longitudinal consistency, not as confirmatory)
- **Exploratory (N=4):** first-life α cells V4, W8, W9, W10 (informed the pre-reg; included only for self-consistency check)

### Per-trajectory output

| Cell | Lifecycle | Trajectory | Independence | n_flagged | Class | Confidence | s_LLI | s_LAM_SEI |
|---|---|---|---|---|---|---|---|---|
| V4 | first | α | EXPLORATORY | 8 | LLI | 0.376 | 0.997 | 0.621 |
| V4 | second | γ | non-indep (same cell) | 11 | LLI | 0.311 | 0.989 | 0.679 |
| W8 | first | α | EXPLORATORY | 11 | LAM+SEI | 0.367 | 0.630 | 0.997 |
| W8 | second | γ | non-indep (same cell) | 12 | LAM+SEI | 0.469 | 0.529 | 0.998 |
| W9 | first | α | EXPLORATORY | 12 | unclassified | 0.218 | 0.745 | 0.962 |
| W9 | second | γ | non-indep (same cell) | 11 | LAM+SEI | 0.433 | 0.543 | 0.976 |
| W10 | first | α | EXPLORATORY | 12 | unclassified | 0.188 | 0.754 | 0.942 |
| W10 | second | γ | non-indep (same cell) | 11 | LAM+SEI | 0.406 | 0.544 | 0.951 |
| **G1** | first | β | **independent** | 8 | unclassified | 0.226 | 0.906 | 0.681 |
| **W4** | first | β | **independent** | 5 | **LLI** | 0.372 | 0.973 | 0.600 |
| **W5** | first | β | **independent** | 12 | **LAM+SEI** | 0.388 | 0.532 | 0.920 |

### Truly independent held-out (N=3, first-life β cohort)

- **Confidently classified: 2/3 (66.7%)** → ✅ meets pre-reg ≥50%
- LAM+SEI: 1/2 (W5), LLI: 1/2 (W4)
- N=3 is too small for the LAM+SEI ≥70% sub-criterion to be informative

### Longitudinal consistency check (non-independent, N=4)

Striking result: same physical cells classify the same way across two separate lifecycles measured with overlapping but distinct operator triads.

- **V4: LLI in both lifecycles** (V4_first = LLI conf 0.38; V4_second = LLI conf 0.31)
- **W8: LAM+SEI in both lifecycles** (W8_first = LAM+SEI conf 0.37; W8_second = LAM+SEI conf 0.47)
- W9, W10: unclassified in first-life, classified LAM+SEI in second-life (degradation deepened, signal sharpened)

This longitudinal-consistency finding is methodologically interesting: same physical cells, two campaigns separated by ~1 year, two different operator setups (first-life with thermal aux channel; second-life without), same residual-direction class. **The classifier picks up a real cell-level aging-mode signature, not a within-campaign artifact.**

But it's NOT confirmatory replication. The pre-reg flagged these cells explicitly as non-independent.

## Result 2 — Zhang Cambridge cohort: INVALID under current protocol

Pre-registered protocol ran on the Zhang Cambridge 25°C 8-cell cohort, but with a critical caveat.

### Q_max extraction failure

Zhang's EIS files use cycle numbers internal to the EIS measurement protocol (cycle_number = 1 throughout most EIS files), not the cell's aging-cycle timeline. The capacity files contain the full aging trajectory (cycle numbers up to 349 for cell 25C01) but the EIS-file cycle_number doesn't index into them.

Result: every cell's Q_max ended up looking the same across all states (the file-wide max capacity), making the Q_max z-score = 0 for every observation. The classifier output:

- 8/8 cells "confidently classified" with confidence 0.6-0.8
- But all classifications have s_LLI = 0.000 — that's the degenerate signature of Q_max not varying. The classification is effectively two-operator (R_ohmic + R_diff only) which is NOT what the pre-reg specifies.
- 7/8 labeled "LLI" but the underlying signal is actually negative s_LAM_SEI = resistance DECREASING over states (formation-effect dominated). The "LLI" label is a misclassification artifact of mapping a 2D residual into a 3D centroid space.

### Verdict on Zhang

**The Zhang Cambridge cohort cannot be validly classified under the current pre-registered protocol** without per-state cycle-alignment work that wasn't budgeted in the original feature-extraction plan. The classifier's "100% classified" output should NOT be treated as a pass — it's invalid because the feature vector is degenerate.

Two paths forward:
1. **Per-state cycle alignment** using EIS time-stamps (state I time = early seconds, state IX time = millions of seconds; capacity file timestamps span the same range). This is a non-trivial extraction project, ~1 day of careful work.
2. **Report Zhang as inapplicable** under the current protocol and note the limitation. The pre-reg's three-cohort replication structure then runs on Khan + SECL-β + (WMG when available) for the formal verdict.

For honesty: **Zhang verdict = INVALID, not PASS or FAIL.** Don't report it as either.

---

## Updated Phase 4 verdict — multi-cohort summary

| Cohort | N | Pre-reg verdict | Notes |
|---|---|---|---|
| Khan 2025 (independent NMC/graphite) | 19 | **FAIL** | Permutation p=1.0; 15.8% confidently classified |
| SECL β (independent NMC/Si-graphite, HPPC operators) | 3 | **PASS on size criterion** | 66.7% classified; small N, partial verdict |
| SECL γ (non-independent same cells) | 4 | Longitudinal consistency confirmed | NOT a confirmatory test |
| Zhang Cambridge (independent LCO/graphite) | 8 | **INVALID** | Feature extraction incompatible without cycle-alignment work |
| WMG 25-cell | — | pending | Mendeley UI download blocked |

**Two of three independent replication cohorts have given an honest verdict.** Khan FAILED. SECL-β shows positive separation at N=3 (too small for strong conclusion). Zhang is INVALID under the current protocol.

The Bonferroni-corrected pre-reg α/3 = 0.0167 falsification threshold (per cohort) is met by Khan (p=1.0 fails). To rescue Phase 4 at the protocol level we'd need WMG to succeed AND a Zhang re-extraction to also succeed at the pre-registered confidence threshold.

## What this changes for the paper

**Phase 4 second-claim status across cohorts:**
- 1 cohort FAILED at pre-reg (Khan)
- 1 cohort PASSED on partial criteria (SECL-β, N=3)
- 1 cohort INVALID at pre-reg
- 1 cohort pending (WMG)

**Net verdict so far: Phase 4 second-claim not confirmed at the pre-registered protocol on the first held-out cohort.** The smaller independent cohort (SECL-β, N=3) shows some separation. The methodology's mode-classification claim sits on shaky empirical ground.

**What survives:** the longitudinal consistency finding (V4 stays LLI both lifecycles, W8 stays LAM+SEI) is real and would be reported as a Phase 4 sub-result, with proper caveats about cell-level non-independence across lifecycles. It supports the idea that the residual-direction signature is a real cell-property rather than measurement noise — even though the classifier-as-pre-specified doesn't transfer cleanly across cohorts.

## Outputs

- `data/processed/secl_held_out_classification.parquet`
- `data/processed/zhang_cambridge_classification.parquet` (INVALID; do not use)
- `code/secl_held_out_classifier.py`
- `code/zhang_extract_and_classify.py` (Q_max extraction needs rework before re-running)
