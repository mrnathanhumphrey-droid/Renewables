# Phase 0 Decision Memo — C2 Battery Multi-Operator Differential Study

**Date:** 2026-05-21
**Decision:** **PROCEED to Phase 1** with substantially narrowed contribution claim (initially called "sharpened framing"; post-chase, the narrowing is more material)
**Update 2026-05-21 evening:** chased the operando-pressure paper to full bibliographic resolution. No OA copy exists. Graphical abstract bullets + search snippets recovered enough to lock the threat assessment without the full PDF.
**Evidence base:** [00_phase0_lit_index.md](00_phase0_lit_index.md)

---

## The C2 claim, restated for testing

> The onset time at which independent physical operators (electrical, thermal, impedance) begin **disagreeing** about cell state precedes single-operator threshold crossing by a measurable, statistically significant margin, **and the type of inconsistency identifies the degradation mode.**

## What the literature actually does

| Category | Representative work | Framing |
|---|---|---|
| Multi-modal fusion → single SOH | Liu/Hu 2025 Nature Comms; multi-expert fusion 2025 | **Integrative** — combine modalities into one regression head, optimize accuracy |
| Single-modality SOH | Severson 2019, Attia 2020, Zhang 2020 Cambridge EIS | **Univariate** — electrical-only or EIS-only |
| Intra-modal differentials | Bello 2025 (arxiv 2503.14327); IC/DV/DTV literature | **Derivatives within one modality** (dQ/dV, dT/dV) |
| One operator leads another | Operando-pressure 2024 | **Operator-substitution** — "pressure is a better leading indicator than electrical" |
| Inter-cell inconsistency | CALCE / Hua joint estimation | **Within one operator, across cells in a pack** |

**What is NOT in the literature surveyed:**
- A method that takes N independent operators, defines pairwise disagreement-onset under a conditional null, and uses that disagreement-pattern as both (a) an early-warning signal and (b) a degradation-mode classifier.
- A pre-registered comparison of disagreement-onset lead time vs single-operator threshold crossing.
- The Li 2025 SOH review explicitly enumerates modalities but does not categorize any method as inter-operator-differential.

## The one real threat: Ding 2024/2025 operando pressure (Energy Storage Materials)

**Full citation:** Ding S., Wang L., Dai H., He X. "Prognosticating nonlinear degradation in lithium-ion batteries: operando pressure as an early indicator preceding other signals of capacity fade and safety risks." *Energy Storage Materials* 75, 103998 (2025). DOI: 10.1016/j.ensm.2024.103998. Closed access; no preprint exists.

### Framing — now resolved from graphical abstract bullets

The paper's own three headline claims:
1. "Irreversible cumulative mechanical pressure signals predict nonlinear degradation onset"
2. "Operando pressure measurements reveal early signs of degradation in pouch cells"
3. **"Pressure signal monitoring differentiates degradation modes, aiding battery diagnostics"**

Plus the dP/dQ plateau as the intra-pressure differential signature for lithium plating, and lead-time numbers of 323 cycles (LFP) / 280 cycles (NMC) between knee-onset and knee-point.

### What this means for C2

Both halves of the original C2 claim — (a) earlier warning than single-operator electrical thresholds and (b) mode identification from disagreement type — are achieved in Ding 2024 via a **different mechanism**:

| | Ding 2024 | C2 (proposed) |
|---|---|---|
| Number of operators | 1 (pressure) | N ≥ 3 (electrical, thermal, EIS, ...) |
| Source of "differential" | **Intra-modal** (dP/dQ within pressure signal) | **Inter-operator** (disagreement onset across modalities) |
| Mode classifier input | Signature within pressure curve (e.g., dP/dQ plateau) | Cross-operator disagreement vector |
| Requires mechanical sensor? | Yes | No |
| Generalizes to N operators? | No (pressure-specific) | Yes (operator-agnostic) |

### The honest contribution C2 can still claim

C2 is no longer "the first to show non-electrical operators give earlier warning than electrical" — Ding has that.
C2 is no longer "the first to show operator signatures classify degradation mode" — Ding has that for pressure.

C2's remaining novelty is **methodological**:
- A formal framework for inter-operator disagreement onset under a conditional null, applicable to any N ≥ 3 operator set
- Demonstration that the cross-operator pattern itself (not signatures within any single operator) carries mode-identification information
- Critically: the framework works on public datasets without mechanical instrumentation, which is where most of the field actually lives. Ding's approach requires pouch cells with operando pressure rigs; C2's would work on Severson, Stanford SECL, Cambridge EIS, etc.

This is a more modest contribution than the original C2 phrasing suggested, but it's still defensible and useful.

### Carryover before Phase 3 pre-reg lock

The full PDF is unobtainable without paid access. The Phase 0 finding is sufficient for the go/no-go call — but before pre-reg lock, get the full text via library access if possible. Specifically need to verify:
- Whether Ding tests with the pressure-precedes-electrical lead time *under a hierarchical null* (which would push closer to C2's territory) or simply via threshold-crossing comparison
- Whether the "differentiates degradation modes" claim is supported by classification accuracy numbers C2 should benchmark against
- Whether the paper's pouch-cell dataset is publicly available

## What changes about C2 framing as a result (REVISED after operando-pressure chase)

1. **Drop "differential" as the headline term in the pre-reg.** Collides with (a) Bello 2025 (intra-modal derivatives), (b) Ding 2024 (dP/dQ intra-pressure), and (c) the IC/DV/DTV literature. Candidates: "inter-operator disagreement onset," "cross-modality timing inconsistency."

2. **Mode-identification is NOT the cleanest novelty anymore.** The original memo claimed Phase 4 was where C2's novelty was strongest. After the operando-pressure chase, Ding 2024 explicitly claims pressure-signal-based mode discrimination. C2 must distinguish itself by claiming mode-identification from the **cross-operator pattern**, not from signatures within any single operator. The Phase 4 falsification criterion needs to compare against Ding-style intra-modal classification as one of the baselines.

3. **Position C2 as an operator-agnostic generalization** of the Ding insight. The Ding-style "non-electrical operator carries unique early-warning information" finding is established. C2 generalizes by asking: which mathematical structure across N operators encodes the joint information optimally? The contribution is the framework, not any single operator's lead time.

4. **C2's natural-dataset advantage matters more now.** Ding requires pouch cells with operando pressure rigs. C2 works on Stanford SECL, Severson, Zhang Cambridge EIS — datasets without mechanical instrumentation. This is where C2 has practical relevance: deployment to the vast majority of public battery data that doesn't have pressure sensors.

5. **Replace the original headline claim** in c2_battery_phases.md with the narrower version. Current text: "The onset time at which independent physical operators... begin disagreeing... precedes single-operator threshold crossing... and the type of inconsistency identifies the degradation mode." This phrasing is now partially preempted by Ding 2024 when read broadly. Revised version should explicitly require N ≥ 3 operators and explicitly frame the contribution as cross-operator pattern, not single-operator lead.

## Recommendation (REVISED after operando-pressure chase)

- **Go/no-go:** GO, with the C2 claim narrowed. Proceed to Phase 1 (dataset acquisition and operator inventory).
- **Headline-claim rewrite required before Phase 3:**
  - OLD: "operator-differential onset precedes single-operator threshold crossing, and the type of inconsistency identifies the degradation mode"
  - NEW (draft): "Under a hierarchical conditional null model on N ≥ 3 independent operators (electrical, thermal, impedance, ...), the joint structure of pairwise disagreement onset times carries (a) cycle-count lead time over standard 80%-SOH thresholds and (b) classification information for degradation modes that exceeds what any single operator's intra-modal signature provides — including the pressure-based dP/dQ signatures recently established by Ding et al. 2024."
- **Pre-reg adjustments (carry into Phase 3):**
  - Drop the word "differential" from the headline; replace with "inter-operator disagreement onset"
  - State the contribution as *operator-agnostic methodology*, with explicit non-claim that any single operator is privileged
  - Phase 4 mode-classification benchmark MUST include a Ding-style intra-pressure (or intra-electrical) baseline
- **Open carryover (must resolve before Phase 3 lock):**
  - Library/paid access to Ding 2024 (10.1016/j.ensm.2024.103998) for full methods + numbers
  - Sweep Sandia / Argonne / NREL technical reports for any operator-disagreement work
  - Fetch Zhang 2022 (s41467-022-32422-w) and thermal-runaway transformer paper (s41598-025-20886-x) — both behind Nature auth wall this pass

## Open questions from c2_battery_phases.md, now answered

- **Q1 (Hank for retrieval, Wilson for synthesis):** Phase 0 ran without that division — Claude did both. If the project survives Phase 0.5 (direct read of pressure paper) and goes to Phase 1, the role split makes sense for the literature corpus that supports the writeup. Defer.
- **Q2 (parallel vs sequential Phase 0/Phase 1):** Phase 0 returned PROCEED, so the question is moot — but the design choice held: read first, wrangle second.
- **Q3 (external Phase-5 collaborator):** Premature. Revisit at Phase 5 entry.
