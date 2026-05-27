# Next Session — Pickup Pointer

**Latest activity:** 2026-05-27 — Probe 7 v1 closed NULL (see §"Probe 7 v1" below).
**Prior anchor:** 2026-05-22 (commit `273be36` on `main`) — Paper 2 amended-protocol arc published.

---

## Probe 8a (2026-05-27 — feature-space decomposition)

| Document | Verdict | Lock commit |
|---|---|---|
| literature/41 (8a pre-reg) | — | `8cfbecc` |
| literature/42 (8a result) | **FEATURE-SPACE IS THE DIVIDING LINE.** Variant (i) residuals-only [current C3] 0/3 at L2; variants (ii) aged-absolute, (iii) fresh-absolute, (iv) fresh+aged stacked, (v) fresh+residual stacked all **2/3 PASS LEVEL ROBUST at L2** (thickness + particle_radius). Transference structurally invisible across all variants. | _to be set_ |

**Implication:** The C3 framework's Level-2 noise sensitivity is architecturally caused by the residual-feature choice. Math: multiplicative percentage noise on absolute values gives signal/noise ~1.1 for thickness; residuals see ~50× worse signal/noise because aging shift (μΩ) is small relative to absolute baseline (mΩ).

**C3 amendment proposal (literature/42 §B, NOT a locked recommendation):**
- Switch feature space from residuals to absolute (variant (iv) fresh+aged stacked is the strongest candidate, th F=14.3 / pr F=13.6 at L2)
- Trade-off: changes the scientific claim from "aging-direction inversion" (residual-specific) to "aged-state design discrimination" or "fresh/aged impedance design fingerprinting" — operationally simpler, theoretically less specific
- Transference needs a different operator entirely (sub-10 mHz EIS, GITT, or different physical observable)

**Probe 8b/c/d:** lower-priority now that 8a established Level-2 survival. 8b (Mahalanobis distance) + 8c (projection) likely improve F-values on variant (iv) further but don't change the headline. 8d (test statistic) only if 8b+8c reveal unexpected results.

## Probe 7 arc (2026-05-27 — EIS-triad noise-robustness)

| Document | Verdict | Lock commit |
|---|---|---|
| literature/37 (v1 pre-reg) | — | `771de3a` |
| literature/38 (v1 result) | **PROBE 7 NULL** at Level 2: 0/3 EIS-triad PASS vs 0/3 HPPC baseline (P7_F4 reproduces literature/26). Operator triad does NOT carry noise rejection under B7 LAM-proxy. | `a5a6ba1` |
| literature/39 (v2 pre-reg) | — | `1097b5b` |
| literature/40 (v2 result) | **PROBE 7 v2 PRIMARY NULL**: B5' cycling-read aged-EIS doesn't rescue Level-2 noise rejection either (0/3 at N1, 1/3 WEAK at N2). Fresh-state×N1 secondary 2/3 PASS LEVEL ROBUST (different test, different question). **The C3 noise sensitivity is architectural, not operator-extraction-driven.** | `b17f11a` |

### v1 to v2 trajectory

**v1 (B7 LAM-proxy):** Aged-state EIS modified active material volume fractions by per-cell Q-loss. Smoke comparison to v2 revealed B7 was off-target — PyBaMM Chen2020 + Yang2017 SEI doesn't actually change amvf during cycling; the real aging is SEI growth + porosity collapse. v1 result therefore conditional on an off-target proxy.

**v2 (B5' cycling-read state):** Aged-state EIS modified `Initial SEI thickness` and `Negative electrode porosity` to the values read from the cycling solution at the uniform-anchor cycle. R_diff growth ~27× stronger (mean residual 0.104 Ω vs B7's 0.0038 Ω). R_ohmic_residual |s/n| went from 5.3 → 32.5 (not dead, as v1 implied — porosity affects high-freq impedance via Bruggeman). **Despite cleaner aging extraction, primary B5'×N1 PERMANOVA still NULL at Level 2** (0/3 PASS). Confirms the architecture-level noise sensitivity.

### Combined Probe 7 closure

Three independent operator-extraction methodologies (HPPC, B7, B5') × five-level noise grid × four PERMANOVA architectures (residual×N1, residual×N2, fresh-state×N1, fresh-state×N2). The **only configuration that survives Level 2 academic noise is fresh-state features × N1** (R_ohmic_fresh's 746× cathode-thickness discriminator dominates), which tests "do design parameters affect fresh impedance" — different question from C3's aging-direction-inversion claim.

**C3 framework status updated:** noise-rejection is not recoverable by operator-triad swap, even with corrected aging extraction. Future C3 work would need (a) architecture amendment to a non-residual / non-unit-vector / non-cosine PERMANOVA framework, (b) sub-Level-1 instrumentation per Probe 6 closure, or (c) a real-cell EIS cohort with design-varied conditions that doesn't currently exist in the corpus.

No further Probe 7 versions planned.

**Earlier "Aggron" pre-reg draft (retracted, not committed):** its §1 motivation that "Probe 6 used marginal PERMANOVAs, joint will recover signal" was factually wrong — Probe 6 already runs the joint-vector cosine PERMANOVA on the C1 architecture.

---

## Paper 2 amended-protocol full result chain

| Document | Verdict | Lock commit |
|---|---|---|
| literature/27 (operator catalog pre-reg) | — | 13e9f80 |
| literature/28 (selection + cascade pre-reg + amendments) | — | 7fae62a / 153fbd3 / 3ad6c5c / 7633f7e |
| literature/29 (strict-pre-reg result) | **PAPER 2 INVALID** | 2ffb513 |
| literature/30 (Gate I diagnostic-driven amendment) | — | 3ad6c5c |
| literature/31 (amended-cascade primary) | **PARTIAL REPLICATION** (PyBaMM-holdout F=57.26 PASS, WMG SECONDARY vacant) | d3b1662 |
| literature/32 (cascade noise pre-reg) | — | 7633f7e |
| literature/33 (WMG SECONDARY broadening) | — | 7633f7e |
| literature/34 (noise probe result) | **CASCADE NOISE-ROBUST** at Level 2 (barely; F=3.19 just > 3.0; 95% reduction from baseline) | 273be36 |
| literature/35 (WMG cross-substrate result) | **CASCADE CROSS-SUBSTRATE NULL** (F=0.92, p=0.58 on C2-only restricted cascade) | 273be36 |

## Combined headline (literature/35 §6)

> Paper 2 (amended protocol): partial replication within-substrate (PyBaMM holdout F=57, p<0.001), barely robust to typical academic instrumentation noise (F=3.2 just above the 3.0 threshold), and not cross-transferable via the cascade's dominant operator to a real-cell NMC811 cohort (WMG F=0.92, p=0.58 NULL). The framework as designed has a narrow operational regime: synthetic, low-noise, design-condition-discriminating only.

## Where things stand

Both strict-pre-reg (literature/29: INVALID) and amended-pre-reg with full robustness audit (literature/31 + 34 + 35: PARTIAL REPLICATION + NOISE-ROBUST barely + CROSS-SUBSTRATE NULL) are published. The Paper 2 narrative is closed pending future methodological work.

## Outstanding follow-ups (NOT pre-registered)

1. **Cross-substrate-as-primary-gate redesign.** A Paper-3-equivalent pre-reg that locks cross-substrate validation as a PRIMARY gate alongside (not after) Gate I/II selection. Operators that pass Gate I+II but fail cross-substrate would be dropped. This would change the cascade's operator set.

2. **Expanded operator catalog with cross-substrate-applicable features.** WMG fails because trajectory operators are not extractable from snapshot data. A redesigned catalog could include EIS-derived operators with broader applicability (full Nyquist features, Warburg-region slopes if extractable on more cohorts).

3. **Tighter rank-stability threshold.** Currently ρ_median ≥ 0.50; empirical floor was 0.994. Tightening to 0.85+ would drop weaker operators ex ante.

4. **Train-with-noise cascade.** Inject training-time noise to learn noise-invariant features. Would change the operator-selection priorities. Pre-reg first.

5. **Full-coverage real-cell cohort acquisition.** Identify or generate a real-cell cohort with trajectory + EIS + design-condition coverage matching PyBaMM/Khan/Severson. Without this, the cross-substrate generalization claim cannot be tested end-to-end.

6. **Cross-paper integration writeup.** Paper 1 (independence-framework, C2 N=7 sign-test result + 6 C3 probes) + Paper 2 (noise-robust cascade with full robustness audit) side-by-side methodology paper.

7. **Methodology corpus integration.** Battery substrate alongside sports / SPX / cancer / hydrology / gun violence / NFL / sharks / women's health in cross-substrate methodology paper.

## Repo state

Branch `main` at `273be36`. Push to `origin/main` synced. All literature 00-35 present. All code in `code/`. All parquets in `data/processed/` (gitignored).

New artifacts from this session (2026-05-22):
- literature/30, 31, 32, 33, 34, 35 (full Paper 2 amended-protocol arc + robustness audit)
- code/paper2_gate_I_v2.py, paper2_gate_II_v2.py, paper2_cascade_v2.py, paper2_cascade_v2_noise.py, paper2_cascade_v2_wmg.py
- data/processed/paper2_gate_I_v2_results.parquet, paper2_gate_II_v2_results.parquet, paper2_cascade_v2_summary.pkl, paper2_cascade_v2_importances.parquet, paper2_cascade_v2_noise_results.parquet, paper2_cascade_v2_wmg_results.pkl

## Key result numbers (for citation)

- Amended cascade PRIMARY (PyBaMM-holdout): F=57.26, p=0.0001 (within-substrate, n=36, 9 L9 classes)
- Cascade noise calibration: F=64.5 → 6.0 → 3.2 → 2.0 → 2.0 (Levels 0-4); Level 2 pre-reg PASS at threshold edge
- Cascade WMG SECONDARY (C2-only restricted): F=0.92, p=0.58, NULL (n=19, 4 SOH bins {80, 85, 90, 95})
- 7-operator cascade variable importance: C2 27%, T1 20%, T4 16%, T5 14%, T2 12%, T3 6%, C1 5%
- C2-only restricted cascade 5-fold OOF accuracy: 0.461 (vs 7-op 0.684; vs chance 0.071)
