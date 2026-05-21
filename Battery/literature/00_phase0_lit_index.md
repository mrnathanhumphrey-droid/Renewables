# Phase 0 Literature Index — C2 Battery Multi-Operator Differential Study

**Pulled:** 2026-05-21
**Purpose:** Null-baseline check for C2's novelty claim — is "operator-differential onset precedes single-operator threshold crossing, and the type of disagreement identifies the degradation mode" already established literature, or is it open?

---

## Tier 1 — Gating papers (the specific ones c2_battery_phases.md called out)

### Liu, Li, Hu et al. 2025 — Multi-modal Nature Comms (THE gating paper)
- **Title:** Multi-modal framework for battery state of health evaluation using open-source electric vehicle data
- **DOI:** 10.1038/s41467-025-56485-7
- **PMC:** PMC11779878
- **Affiliations:** Chongqing University; State Key Lab of Intelligent Vehicle Safety
- **Modalities:** 2D voltage feature map (96×96), 1D capacity sequence, 1D temperature sequence, 15 scalar point features → fused via ResNet + FC layers
- **Framing:** **INTEGRATIVE FUSION, not differential.** Feeds all modalities into a single regression head. No disagreement measurement. No lead-time claim.
- **Headline result:** MAPE 2.83% across SOH range; 4.69% on SOH<85%
- **Dataset:** 300 EVs over 3 years, NCM packs, 155 Ah, real-world charging, publicly released
- **Verdict for C2 novelty:** ✅ Does **not** preempt C2's differential framing.

### Severson et al. 2019 — Cycle life prediction
- **Title:** Data-driven prediction of battery cycle life before capacity degradation
- **DOI:** 10.1038/s41560-019-0356-8
- **Modalities:** Electrical only (discharge voltage curves)
- **Headline:** 9.1% test error from first 100 cycles; 4.9% classification error from first 5 cycles
- **Dataset:** 124 LFP cells, fast charging, 150–2300 cycle lives
- **Verdict for C2:** ✅ Single-operator. Foundational, not preemptive.

### Attia et al. 2020 — Closed-loop fast-charging
- **Title:** Closed-loop optimization of fast-charging protocols for batteries with machine learning
- **DOI:** 10.1038/s41586-020-1994-5
- **Modalities:** Electrical (charging protocols + cycle life), Bayesian opt
- **Verdict for C2:** ✅ Not a multi-operator paper. Optimization methodology.

### Zhang et al. 2020 — Cambridge EIS
- **Title:** Identifying degradation patterns of lithium ion batteries from impedance spectroscopy using machine learning
- **DOI:** 10.1038/s41467-020-15235-7
- **PMC:** PMC7136228
- **Modalities:** **EIS only.** Single-operator (impedance), univariate Gaussian process on full spectrum
- **Dataset:** 20,000+ EIS spectra, commercial Li-ion, varying SOH/SOC/T
- **Verdict for C2:** ✅ Single-operator. Validates within-EIS frequency-band sub-operator decomposition (Phase 4 substrate), but no inter-operator differential framing.

---

## Tier 2 — Closest existing prior art (real novelty threats)

### Ding, Wang, Dai, He 2024/2025 — **CRITICAL THREAT, partial preemption of BOTH C2 claims**
- **Title:** Prognosticating nonlinear degradation in lithium-ion batteries: operando pressure as an early indicator preceding other signals of capacity fade and safety risks
- **Journal:** Energy Storage Materials, vol 75, art. 103998, Feb 2025 (published 2024-12-31)
- **DOI:** 10.1016/j.ensm.2024.103998
- **Authors:** Shicong Ding (corresponding, first), Li Wang, Haifeng Dai (Tongji), Xiangming He (Tsinghua)
- **OA status:** CLOSED via Unpaywall. No preprint, no institutional repository copy. Full text unobtainable without paid access.
- **Recovered evidence (graphical abstract bullets + search snippets):**
  1. "Irreversible cumulative mechanical pressure signals predict nonlinear degradation onset"
  2. "Operando pressure measurements reveal early signs of degradation in pouch cells"
  3. **"Pressure signal monitoring differentiates degradation modes, aiding battery diagnostics"**
  4. Lead times: knee-onset to knee-point = **323 cycles (LFP) / 280 cycles (NMC)**
  5. Mechanism: the **dP/dQ plateau** acts as a definitive indicator of lithium plating onset and growth (intra-modal differential within pressure)
- **Resolved framing distinction:**
  - **Not operator-differential.** Both C2-relevant claims (early warning + mode ID) are achieved via a *single operator* (pressure) plus *intra-modal differentials* on it (dP/dQ).
  - Approach: operator-substitution (pressure replaces electrical as the leading indicator) + intra-modal differential analysis (dP/dQ plateau classifies the failure mode).
  - C2's specific construct — *inter-operator timing disagreement across N ≥ 3 operators, scored under a conditional null* — is NOT what Ding does.
- **Verdict for C2:** ⚠️ Partial preemption on **both halves of the C2 claim, in their broad reading.** C2 must narrow its contribution to what remains:
  - Operator-agnostic methodology — the framework works on any combination of N independent operators, not contingent on having pressure data
  - Inter-operator pattern as the classifier — uses the full vector of cross-operator disagreement onsets, not signatures within any one operator
  - Generalization to datasets without mechanical instrumentation (most public datasets) — Ding's approach requires pressure measurements; C2's should work on electrical + thermal + EIS alone
- **What C2 can still claim:**
  - A methodology that does not require pressure instrumentation
  - A formal inter-operator disagreement onset statistic with a conditional null
  - Mode classification from the cross-operator disagreement vector, not the within-operator signature
- **What C2 CANNOT claim:** to be the first to show (a) one modality leads electrical at the knee or (b) a non-electrical operator carries mode-identification information. Both established by Ding.

### Bello et al. 2025 — Optical fiber + "Differential SOH Metrics" (arxiv 2503.14327)
- **Title:** Multi-Parameter Analysis of Li-ion Battery Degradation: Integrating Optical Fiber Sensing with Differential State of Health Metrics
- **arxiv:** 2503.14327 (March 2025)
- **Modalities:** FBG optical sensing (volume + thermal) + electrical (capacity, voltage) + strain
- **Definition of "differential":** **Intra-modal derivatives** (dCapacity/dV, dStrain/dV, dT/dV) — NOT inter-operator disagreement
- **Framing:** Multi-parameter monitoring + LSTM/GRU/ANN fused predictor. No lead-time claim. No disagreement signal.
- **Dataset:** Commercial button cells, 600 cycles
- **Verdict for C2:** ✅ Does **not** preempt C2's specific framing. ⚠️ But creates NAMING COLLISION — they use "differential" first in a multi-modal battery context. **C2 needs different terminology in pre-reg.**

### Zhang et al. 2022 — Impedance-based forecasting under uneven usage
- **DOI:** 10.1038/s41467-022-32422-w
- **Status:** Behind Nature auth wall, not retrieved this pass. Likely follow-on to Cambridge 2020 EIS work. Single-operator (EIS).
- **Verdict:** Likely ✅ does not preempt, but verify.

### Zhang/Altaf/Wik 2024 — Knee-onset via curvature (arxiv 2304.11671)
- **Title:** Battery Capacity Knee-Onset Identification and Early Prediction Using Degradation Curvature
- **Framing:** Single-operator (capacity curve curvature). Detects knee-onset within one modality.
- **Verdict for C2:** ✅ Not multi-operator. C2's framing distinct.

---

## Tier 3 — Methodology review (substrate frontier)

### Li et al. 2025 — Materials review on SOH estimation
- **Title:** State of Health Estimation and Battery Management: A Review of Health Indicators, Models and Machine Learning
- **DOI:** 10.3390/ma18010145
- **Journal:** Materials, 2025 Jan 2; 18(1):145
- **PMC:** PMC12068027
- **Categorization:** Surveys electrical, thermal, electrochemical, mechanical/structural modalities. **All fusion described as integrative (weighted-average / ensemble), NONE described as differential-onset.** Review does not flag operator-disagreement timing as an open problem.
- **Verdict for C2:** ✅ Confirms the field's standard taxonomy is integrative. C2's differential framing sits in an unfilled niche per this survey.

---

## Tier 4 — Adjacent / non-preemptive

### Joint cell-inconsistency + SOH (CALCE / Hua)
- "Joint Estimation of Inconsistency and State of Health for Series Battery Packs" (Springer Automotive Innovation)
- **Inconsistency** here = inter-CELL within a pack (one cell vs others, same operator). NOT inter-OPERATOR.
- **Verdict for C2:** ✅ Different problem entirely.

### Acoustic emission corpus (MIT 2025, MDPI 2025 review, etc.)
- Single-operator (acoustic), often paired with electrical for confirmation
- No "disagreement-onset between operators" framing surfaced
- **Verdict for C2:** ✅ Acoustic = candidate Path-B operator, not a preemption.

---

## Search terms tried (Phase 0.2 coverage)

- "differential multi-modal battery state of health early warning operator divergence onset" — surfaces fusion + intra-modal differential, not inter-operator differential
- "joint impedance capacity inconsistency" OR "operator differential" battery state health — surfaces inter-cell inconsistency, not inter-operator
- battery degradation operator disagreement onset early warning multi-modal divergence lead time — surfaces operando-pressure paper (the key threat) + thermal-runaway fusion frameworks
- battery acoustic emission precedes capacity fade lead time lithium plating early warning — acoustic + differential pressure for plating detection
- battery state of health methodology review 2025 multi-sensor fusion impedance thermal electrical — the Li 2025 review

## Open gaps in this pass

1. **Operando pressure paper** — could not direct-fetch. Resolve framing distinction (substitution vs differential) before Phase 3 pre-reg lock.
2. **Zhang 2022 Cambridge follow-on** — Nature auth wall, not retrieved.
3. **Sandia / Argonne / NREL technical reports** — not searched this pass. Worth a sweep before lock, especially for any internal/government work on multi-sensor onset detection.
4. **Thermal runaway transformer fusion paper** (s41598-025-20886-x) — Nature auth wall. May contain a related fusion-precedence framing.
