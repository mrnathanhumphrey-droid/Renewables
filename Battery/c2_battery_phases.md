# C2: Battery Multi-Operator Disagreement-Onset Study — Phase Plan

**Substrate:** Lithium-ion battery storage (public datasets, Path A scope)
**Methodology corpus position:** Sixth substrate, slotting alongside sports / SPX options / cancer / hydrology / gun violence
**Status (live as of 2026-05-21):** Phase 0–4 complete and locked. C1 cross-chemistry hierarchical pooling HIT (76.1% between-group variance on 4 groups). C2 disagreement-onset early-warning lead time direction-confirmed at N=7 sign test p=0.031. **C3 active.** Probe 1 (Khan within-cohort, exploratory) hit on SOC range. Probes 2 + 3 pre-registered (literature/16, commit `1ef1b94`); Probe 2 (Severson) **H2 PASS pooled** F=31.7 p=0.0001 with partial within-batch replication caveat; Probe 3 (WMG within-cohort) **H3 NULL by p**, effect size above floor (underpower failure). See README.md for the live state table.

**Original Phase 0 entry status:** PHASE 0 COMPLETE (2026-05-21). Decision = PROCEED to Phase 1 with narrowed claim. See [literature/01_phase0_decision_memo.md](literature/01_phase0_decision_memo.md) and [literature/00_phase0_lit_index.md](literature/00_phase0_lit_index.md).

**Terminology note:** The earlier draft used "differential" as the headline term. This word now collides with three established usages — (a) Bello 2025 "Differential SOH Metrics" (intra-modal optical), (b) Ding 2024 dP/dQ intra-pressure analysis, and (c) the standard IC/DV/DTV differential-analysis literature. Replaced throughout with "inter-operator disagreement onset" or "cross-modality timing inconsistency."

**Core claim (revised after Phase 0):** Under a hierarchical conditional null model on N ≥ 3 independent operators (electrical, thermal, impedance, ...), the joint structure of pairwise disagreement-onset times carries (a) cycle-count lead time over standard 80%-SOH thresholds and (b) classification information for degradation modes that exceeds what any single operator's intra-modal signature provides — including the pressure-based dP/dQ signatures recently established by Ding et al. 2024.

**What this claim is NOT:**
- Not a claim that a non-electrical operator gives earlier warning than electrical — established by Ding 2024 (pressure leads electrical by 280-323 cycles at the knee).
- Not a claim that operator signatures classify degradation mode — established by Ding 2024 (dP/dQ plateau identifies plating).
- Not a claim about pressure specifically (or any single operator).

**What this claim IS:**
- A claim about the *cross-operator pattern* — that the joint disagreement-onset vector across N operators carries information beyond what any single operator's signature provides.
- A methodology that is **operator-agnostic** — works on any N ≥ 3 independent-operator combination.
- A methodology that runs on **public datasets without mechanical instrumentation** — the bulk of the field's data has electrical + thermal + EIS but no pressure rig.

**Phase 0 outcome — original gating list:**
- ✅ Liu/Hu 2025 Nature Comms (s41467-025-56485-7): integrative fusion only, no disagreement framing — does not preempt
- ✅ Severson 2019, Attia 2020, Zhang Cambridge 2020: all single-operator, foundational — do not preempt
- ✅ Li 2025 *Materials* review: confirms standard taxonomy is integrative; no method surveyed uses inter-operator disagreement onset
- ⚠️ Ding et al. 2024/2025 *Energy Storage Materials* (10.1016/j.ensm.2024.103998): partial preemption on both halves of original C2 claim via operator-substitution + intra-modal differential (dP/dQ plateau) — necessitated the claim narrowing above
- ✅ Bello 2025 (arxiv 2503.14327): naming collision on "differential" but technically distinct (intra-modal optical-fiber derivatives, not inter-operator) — does not preempt

**Open carryover (resolve before Phase 3 pre-reg lock):**
- Paid/library access to Ding 2024 for full methods + classification numbers
- Sweep Sandia / Argonne / NREL technical reports for any operator-disagreement work
- Resolve Zhang 2022 (s41467-022-32422-w) and thermal-runaway transformer paper (s41598-025-20886-x) — both hit Nature auth walls in Phase 0

---

## Phase 0 — Literature null-baseline check (COMPLETE 2026-05-21)

**Verdict:** PROCEED with narrowed claim. The original "operator-differential onset precedes single-operator threshold + type-of-inconsistency identifies mode" framing is partially preempted by Ding 2024 via operator-substitution. C2 survives as an *operator-agnostic methodology* for inter-operator disagreement-onset patterns across N ≥ 3 operators.

**Output:** [literature/01_phase0_decision_memo.md](literature/01_phase0_decision_memo.md) (decision + revised claim draft); [literature/00_phase0_lit_index.md](literature/00_phase0_lit_index.md) (annotated bibliography organized by threat tier).

**Coverage:**
- 0.1 ✅ Liu/Hu 2025 Nature Comms — integrative fusion, no disagreement framing
- 0.2 ✅ Differential/multi-modal divergence survey — surfaced Ding 2024 as the real threat
- 0.3 ✅ Severson 2019, Attia 2020, Zhang 2020 Cambridge EIS — all single-operator foundational, do not preempt
- 0.4 ✅ Li 2025 *Materials* review — taxonomy confirms inter-operator-disagreement-onset is an unfilled niche

**Open carryover before Phase 3 pre-reg lock** (not blockers for Phase 1/2):
- Library access to Ding 2024 *Energy Storage Materials* full PDF
- Sandia/NREL/Argonne tech-report sweep
- Zhang 2022 (s41467-022-32422-w) and thermal-runaway transformer paper (s41598-025-20886-x) — both hit Nature auth walls in Phase 0

---

## Phase 1 — Dataset acquisition and operator inventory (PARTIAL 2026-05-21)

**Inventory complete; acquisition outstanding.** See [literature/02_phase1_dataset_inventory.md](literature/02_phase1_dataset_inventory.md).

**Phase 1 falsification criterion TRIGGERED:** No single public dataset has all three required operators (electrical, thermal, EIS) at compatible cadences across multiple datasets. Scope narrows to **single-dataset primary** as designed.

**Resolved scope (post-download, locked 2026-05-21):**
- **Primary headline cohort: N=16 INR21700-M50T cells, heterogeneous operator set (Option B).** SECL first-life (10 cells, 23-28 months) use {electrical, thermal, EIS}. SECL second-life (6 cells, 24 months, 19 RPTs, ~90% starting SOH) use {electrical, EIS-ohmic, EIS-diffusion} — thermal substituted by within-EIS frequency-band sub-operators because second-life cycling files do not log Aux_Temperature. Same chemistry, same lab, aligned RPT structure across both lifecycle stages. This cohort directly demonstrates the operator-agnostic claim from Phase 0.
- **Secondary cohort for Phase 4 mode-classification: N=38 Onori-group cells.** Adds Khan/Chu/Onori 2025 22-cell calendar+cycle prismatic dataset for chemistry/format-robustness.
- **External cross-validation (Phase 4):** Zhang Cambridge 2020 (EIS aging-mode labels, different lab); WMG 25-cell NMC811 (Rashid 2023, Mendeley, different chemistry); Severson 2019 (electrical+thermal-only sub-test for the operator-agnostic claim).

**Tasks:**
- 1.1 ✅ Stanford SECL identified, structure characterized (cycling_tests + diagnostic_tests, RPT = capacity + HPPC + EIS), OSF link captured
- 1.2 ✅ Severson identified, no-EIS limitation locked
- 1.3 ✅ Zhang Cambridge identified, EIS-frequency-band role locked
- 1.4 — UCL acoustic (Galiounas) — held in reserve for Path B (unchanged)
- 1.5 ✅ Operator inventory tables built per dataset, cross-dataset compatibility matrix complete
- 1.6 — Operator-pair independence: deferred to Phase 2 (conditional null model construction is where independence assumptions belong)
- 1.7 ✅ Stanford SECL RPT cadence = every 25-50 cycles. Timing resolution ±12.5 to ±25 cycles. Adequate for Ding-scale claims with margin; tight for tens-of-cycles claims (flag as resolution floor in Phase 3 pre-reg)
- 1.8 ✅ Power calc complete. N=16 adequate for Ding-scale (200+ cycle) effects; tight but workable at 50-100 cycle scale; below 50 cycles is below RPT resolution floor. **Phase 3.4 falsification criterion to be locked at 50-cycle minimum lead time at 95% lower credible bound.** See [literature/03_phase1_power_calc.md](literature/03_phase1_power_calc.md).
- **NEW 1.9** ✅ Cohort extension — Onori group has THREE compatible public datasets: first-life SECL (10 cells), second-life SECL (6 cells), and 22-cell calendar+cycle prismatic (Khan 2025). All RPT-aligned with EIS. Headline cohort grows 10 → 16 (same chemistry); Phase 4 cohort grows to 38 (mixed chemistry/format)
- 1.10 ✅ OSF downloads complete + thermal verified (split outcome): first-life HAS continuous thermal during cycling; second-life does NOT. Cohort architecture locked as Option B (N=16 heterogeneous operator set). See [data/00_download_summary.md](data/00_download_summary.md).

**Open carryover (post-Phase 1 close):**
- WMG 25-cell — Mendeley UI download (programmatic blocked) — user task, deferred. Phase 4 cross-validation only, not blocking.
- Raw cycling .xlsx for SECL first-life — deferred. The 93 MB consolidated diagnostic `.mat` files give all RPT-level operator data needed for Phase 3 headline. Raw per-cell cycling data needed only if Phase 2 conditional null requires per-cycle operating-condition reconstruction beyond what filenames encode.
- BatteryArchive direct study-by-study scan for additional Sandia/NREL cohort extensions — opportunistic, not on critical path.

**Phase 1 status:** COMPLETE for the headline cohort. Phase 2 (conditional null model construction) can start.

---

## Phase 2 — Conditional null model (STARTED 2026-05-21)

**Purpose:** Build the model of expected joint operator behavior given exogenous conditions, against which "disagreement" is measured. This is the analog of the design-null in the physics detector and the cross-league pool in the Sloan paper.

**Phase 2 entry findings:** See [literature/04_phase2_entry_data_exploration.md](literature/04_phase2_entry_data_exploration.md). Two key results from data exploration:
1. **EIS coverage on first-life is sparse** — only 3 cells (W8/W9/W10) have full 15-RPT EIS trajectories; 4 cells have zero EIS. Cohort architecture now requires three operator triads to cover all 16 cells.
2. **First-life cells don't reach 80%-SOH** within the 15-RPT trajectory (final SOH ~91-92%). Phase 3.4 falsification comparator must shift from "80%-SOH threshold" to "capacity-knee-point" (which is what Ding 2024 actually compared against).

**Revised operator-triad architecture:**
- **Triad α (electrical + thermal + EIS):** First-life W8/W9/W10 (full) + V4 (partial) — gold standard
- **Triad β (electrical + thermal + HPPC):** First-life W3/W4/W5/W7/G1/V5 — HPPC as third operator where EIS not available
- **Triad γ (electrical + EIS-ohmic + EIS-diffusion):** Second-life G1/V4/V5/W8/W9/W10 (RPTs 5-19, 15 EIS RPTs each)

Total: **16 cells across 3 triads.** Heterogeneity becomes a strength of the operator-agnostic claim.

**Tasks:**
- 2.1 — Specify exogenous conditioning variables: SOC, C-rate, ambient temperature, cycle count, calendar age, depth of discharge. Per-dataset.
- 2.2 ✅ Hierarchical Stan model designed — see [literature/05_phase2_model_design.md](literature/05_phase2_model_design.md). 4-level structure: per-operator marginal nulls → joint Mahalanobis distance → per-cell onset detection → population pooling with triad + lifecycle fixed effects. Headline statistic = `μ_LT` posterior 95% lower credible bound; falsification threshold 50 cycles.
- 2.3 ✅ First-life feature extraction pipeline working (capacity + EIS + HPPC). See [code/extract_features.py](code/extract_features.py). Actual viable cohort: 4 alpha (V4/W8/W9/W10) + 3 beta (G1/W4/W5) on first-life. V5/W3/W7 dropped (<5 valid RPTs).
- 2.4 ⚠️ Partial. (a) First-life alpha subset Mahalanobis result [literature/06_phase2_4_5_first_results.md](literature/06_phase2_4_5_first_results.md). (b) Naive combined pipeline exposed fresh-period definition problem [literature/07_phase2_4_combined_result.md](literature/07_phase2_4_combined_result.md). (c) **Option X1 implemented** — per-cell fresh = first-life RPTs 1-3 of same cell, applied across both lifecycles [literature/10_phase2_option_x1_result.md](literature/10_phase2_option_x1_result.md). PPC reproduces, second-life onset at RPT 5 for all 4 cells in α/γ pool, cell-level distance ordering preserved across lifecycles (W8 stable, W10 worst). Triad β + G1/V5 second-life still excluded from X1 — separate pipeline needed. Hierarchical Stan pool still to be implemented.
- 2.5 ✅ **PPC passes on alpha subset** with pooled fresh-period covariance. Mean fresh-period d² = 2.72 vs χ²(3) expected 3.0; KS p = 0.547. Conditional-independence assumption empirically supported (fresh-period operator correlations all |ρ| < 0.20).
- **Bonus finding (Phase 4 preview, EXPLORATORY ONLY):** V4 vs W-cells already shows two distinct degradation-mode signatures in residual direction (V4 = LLI-dominant: capacity drop without resistance growth; W-cells = LAM+SEI: capacity drop coupled with R_ohmic + R_diff growth). C2's second-claim mode-classification signal is visible at N=4 before any classifier is fit. **This pattern is post-hoc and unblinded; it cannot be used as confirmatory evidence.** Pre-registered replication protocol locked at [literature/09_phase4_pre_registration.md](literature/09_phase4_pre_registration.md) before classifier touches beta/gamma/external cohorts.
- **Cell-disposition diagram (CONSORT-style):** [literature/08_cell_disposition.md](literature/08_cell_disposition.md). Three first-life cells dismissed early (W3/W7/V5, reasons not documented = potential informative censoring); three with EIS equipment issues throughout (W4/W5/G1 = MCAR); three with full coverage (W8/W9/W10); one with partial (V4, second-life transition). Cycle-count mapping per (cell, RPT) extracted from README EIS sheet (e.g., W8 onset RPT 5 = cycle 148).
- 2.3 — For each operator, specify the expected response under the design null as a function of exogenous variables + cell-level latent state. The joint null = product of marginal nulls UNDER ASSUMED INDEPENDENCE; document where assumption is approximate.
- 2.4 — Fit the null model on early-cycle data (fresh cells) to establish the joint operator covariance structure under "healthy" operation.
- 2.5 — Posterior predictive checks. The null model must reproduce fresh-cell joint behavior before we trust it to flag disagreement later.

**Falsification criterion:** If the joint null model fails posterior predictive checks on held-out fresh-cell data, we don't have a working baseline. Iterate on conditioning structure or admit the conditional null is too noisy for the disagreement-onset signal we need.

**Output:** Fitted null model, PPC diagnostics, joint covariance structure characterization.

**Estimated effort:** 3-5 sessions. Primary compute load. Probably Agent 1 leading on model fitting.

---

## Phase 3 — Differential measurement and pre-registration

**Purpose:** Define the actual test, lock the analysis plan, then run it. Pre-registration must precede the headline analysis.

**Tasks:**
- 3.1 — Define the disagreement-onset metric. Candidate: per-cell, per-cycle joint Mahalanobis distance under the null model. Onset = first cycle where the rolling joint distance exceeds a pre-specified threshold for K consecutive cycles. ✅ Implemented in `code/fresh_period_null_pooled.py` + `code/combined_option_x1.py`.

**Phase 3 preview result (2026-05-21, N=7 first-life alpha+beta cells, EXPLORATORY):** Lead time of disagreement-onset over capacity-knee-point = mean **+24.71 cyc** (sd 19.75), 5 of 7 cells positive direction, 0 of 7 negative. **Sign test p = 0.031** (direction supported). **95% LCB = +10.21 cyc** — positive but **below 50-cycle pre-reg falsification floor**. Triad β cells (HPPC operators) show larger lead times (mean +31.7) than Triad α (EIS operators, +19.5). Operator-correlation structure differs by triad: α operators near-independent (|ρ|<0.20), β operators physiologically coupled (|ρ| 0.6-0.84); PPC passes both. See [literature/11_phase3_preview_leadtime.md](literature/11_phase3_preview_leadtime.md) (alpha N=4) and [literature/12_phase3_full_first_life.md](literature/12_phase3_full_first_life.md) (combined N=7).
- 3.2 — Define the single-operator threshold comparator: **dual report (locked 2026-05-21).** (a) **Primary: capacity-knee-point** (curvature-based, Zhang/Altaf/Wik 2024 method) — measurable on all N=16, aligns with Ding 2024's actual comparator. (b) **Secondary: 80%-SOH threshold** — reported only on the cell subset that crosses it (likely second-life cells, possibly N≈6). Industrial standard preserved where the data supports it.
- 3.3 — Define the headline statistic: mean cycle-count lead time (disagreement onset cycle minus capacity threshold cycle), distribution across cells, fraction of cells where lead time is positive.
- 3.4 — Define the falsification criterion: pre-registered effect size (e.g., median lead time ≥ X cycles, with X selected from literature on existing early-warning methods), pre-registered p-value or Bayes factor threshold, pre-registered null-baseline comparison.
- 3.5 — Pre-register the analysis plan. Lock before running the headline analysis on the full dataset. Allow holdout cells for exploratory work.
- 3.6 — Run the headline analysis. Report results regardless of direction.

**Falsification criterion:** Pre-registered effect size not achieved → result is null → write it up as null. This is not a failure; it's the methodology working correctly.

**Output:** Pre-registration document, headline result, falsification check.

**Estimated effort:** 2-3 sessions for pre-reg, 1-2 sessions for the analysis once locked.

---

## Phase 4 — Degradation-mode identification

**HARD GATE (added 2026-05-21):** The Phase 2.4 exploratory analysis on N=4 first-life alpha cells (V4 + W8/W9/W10) produced a strong residual-direction pattern (V4 = LLI-dominant, W-cells = LAM+SEI-dominant). That observation **unblinded** the alpha-triad cohort. Before any classifier touches beta-triad cells (G1/W4/W5), second-life gamma cells, or external cross-validation cohorts (Khan/Zhang/WMG), the Phase 4 protocol must be locked. **Pre-registration:** [literature/09_phase4_pre_registration.md](literature/09_phase4_pre_registration.md). Held-out cells are off-limits to classifier code until the pre-reg commit predates any analysis run.

**Purpose:** Test the second half of the (revised) C2 claim: the **cross-operator disagreement pattern** identifies the degradation mode, beyond what any single operator's intra-modal signature provides. This is the bridge to C3.

**Tasks:**
- 4.1 ⚠️ **Multi-cohort verdict (2026-05-21):**
  - **Khan 2025 (N=19, independent NMC/graphite): FAIL** — 3/19 confidently classified, permutation p=1.0 [literature/13_phase4_khan_result.md](literature/13_phase4_khan_result.md)
  - **SECL first-life β (N=3, independent NMC/Si-graphite, HPPC operators): PARTIAL PASS** — 2/3 confidently classified (66.7%), meets ≥50% threshold but N too small for definitive verdict [literature/14_phase4_secl_holdout_zhang.md](literature/14_phase4_secl_holdout_zhang.md)
  - **SECL second-life γ (N=4 same-cell non-independent):** Longitudinal consistency confirmed — V4 stays LLI both lifecycles, W8 stays LAM+SEI both lifecycles. NOT a confirmatory test; supports cell-level residual-direction signature is real.
  - **Zhang Cambridge (N=8, independent LCO/graphite): INVALID** — Q_max extraction degenerate because Zhang EIS cycle-numbers don't index into the aging-cycle timeline of the capacity files. Per-state cycle alignment needed before pre-reg verdict possible.
  - **WMG 25-cell:** still pending Mendeley UI download.
  - **Net so far:** Phase 4 second-claim not confirmed at pre-reg protocol on the largest held-out cohort. Mode-classification claim sits on shaky empirical ground.
- 4.2 — Use the EIS frequency sweep as a within-modality operator decomposition: high-frequency (ohmic), mid-frequency (charge transfer), low-frequency (diffusion). Each frequency band acts as a sub-operator.
- 4.3 — Map operator-disagreement patterns to known degradation pathways: LLI (lithium inventory loss), LAM (active material loss), SEI growth, lithium plating, separator degradation.
- 4.4 — Cross-validate classification across datasets where possible.
- 4.5 — **REQUIRED BASELINE (added post-Phase 0): Ding-style intra-modal differential classifier.** For any operator the dataset supports (e.g., dQ/dV on electrical; dT/dV on thermal; if pressure data exists, dP/dQ), build a single-operator intra-modal classifier and report its accuracy on the same mode labels. C2's contribution depends on the cross-operator pattern classifier *exceeding* the best of these intra-modal baselines.

**Falsification criterion (revised):** If cross-operator-pattern classification does NOT beat the best intra-modal single-operator classifier (Ding-style) on the same mode labels, C2's second-claim is null. The intra-modal baseline must be honestly tuned, not strawmanned. Write the null result up regardless.

**Output:** Classification accuracy table for cross-operator-pattern classifier + intra-modal baseline per operator + confusion matrices for degradation modes.

**Estimated effort:** 2-3 sessions, +1 for the intra-modal baseline.

---

## Phase 5 — Writeup and corpus integration

**Purpose:** Methodology paper. Slot into corpus alongside existing substrates.

**Tasks:**
- 5.1 — Draft methodology paper. Frame as substrate validation, not battery-design contribution.
- 5.2 — Update methodology corpus substrate ledger: battery storage PASS / PARTIAL / FAIL alongside sports, SPX options, cancer, hydrology, gun violence.
- 5.3 — Document the C2 → C3 handoff: what would be needed to move to design parameter inversion, what instrumentation gap exists, candidate collaborators (Sandia, NREL, Argonne, Stanford GCEP, Imperial College electrochemical).
- 5.4 — Honest discussion of limitations: public dataset constraints, operator coverage gaps (no acoustic in Path A), single-chemistry vs. multi-chemistry generalization, missing failure modes (no thermal runaway data in mainstream public sets).

**Output:** Draft paper, corpus update, handoff document for C3 scoping.

**Estimated effort:** 3-5 sessions.

---

## Cross-phase rules

- **Walk-backs free.** If Phase 0 kills the project, that's a win — we saved months. If Phase 2 reveals the conditional null is too noisy, that's data about the substrate, not a personal failure.
- **Pre-registration is a hard gate between Phase 2 and Phase 3.** No exploratory runs of the headline statistic before pre-reg lock.
- **Null result is publishable.** The methodology corpus already documents substrates with PARTIAL and contingent results. Battery PARTIAL or FAIL is a legitimate corpus contribution.
- **No C3 work until C1 and C2 lock.** As established: C1 and C2 probe C3's feasibility; C3 is premature until those probes return.
- **Verify with the work, not vibes.** Effect-size thresholds anchored to existing literature, not to what would feel like a good result.

---

## Open questions before Phase 0 launch

1. Who leads Phase 0 reading? Hank for retrieval; Wilson for synthesis. Confirm.
2. Should Phase 1 dataset acquisition start in parallel with Phase 0, or strictly after the Phase 0 go/no-go? Recommendation: strictly after. Don't sink time into data wrangling if Phase 0 kills the project.
3. Is there an external collaborator to loop in at Phase 5 even on a null result? The handoff document is more useful with a real recipient.
