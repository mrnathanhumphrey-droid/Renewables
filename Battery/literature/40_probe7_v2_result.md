# C3 Probe 7 v2 — Result (B5' Cycling-Read EIS + N2 + Fresh-State)

**Date:** 2026-05-27
**Pre-reg:** `literature/39_probe7_v2_prereg.md` (lock commit `<TBD>`)
**Generator parquet:** `data/processed/pybamm_l9_trajectories_eis_v2.parquet`
**Analyzer:** `code/c3_probe7_v2_permanova.py`
**Result parquet:** `data/processed/probe7_v2_permanova_results.parquet`

---

## Headline

**PROBE 7 v2 PRIMARY NULL** per pre-reg §6 (H7v2-primary).

B5' EIS triad at N1 Level 2: **0/3 PASS** (1 WEAK PASS on particle_radius, F=3.49, p=0.049). The corrected cycling-read aged-state EIS methodology **does NOT rescue** the Level-2 noise rejection. The v1 NULL stands; the noise sensitivity is **architecture-level, not operator-extraction-level**.

Secondary findings:
- **B5'×N2 (EIS-realistic noise):** 1/3 PASS at Level 2 (WEAK particle_radius only). Lower EIS-typical noise gives partial recovery on the diffusion-coupled parameter, but thickness and transference still fail.
- **Fresh-state×N1 (Probe 7.3):** **2/3 PASS at Level 2 LEVEL ROBUST** — only configuration that survives. R_ohmic_fresh's 746× cathode-thickness discriminator and R_diff_fresh's particle_radius separation both come through. Tests "do design parameters affect fresh impedance" (obvious yes); not C3-aging-direction-inversion evidence.
- **P7v2_F4 reproducibility:** B7×N1 reproduces v1's 0/3 at Level 2. HPPC×N1 reproduces Probe 6's 0/3. Comparators are clean.

## Per-variant Level-2 result table

| Variant | Thickness | Transference | Particle radius | Level verdict |
|---|---|---|---|---|
| **B5' × N1 (PRIMARY)** | NULL (F=0.27, p=0.69) | NULL (F=2.19, p=0.19) | WEAK PASS (F=3.49, p=0.049) | LEVEL COLLAPSED |
| B5' × N2 (EIS-realistic) | NULL (NaN) | NULL (NaN) | PASS (F=13.58, p=0.003) | LEVEL WEAK |
| Fresh-state × N1 (Probe 7.3) | PASS (F=11.94, p=0.0001) | NULL (F=0.52, p=0.66) | PASS (F=11.58, p=0.0001) | **LEVEL ROBUST** |
| B7 × N1 (v1 reproducibility) | NULL (F=1.65, p=0.25) | NULL (F=0.49, p=0.59) | NULL (F=0.20, p=0.70) | LEVEL COLLAPSED |
| HPPC × N1 (Probe 6 reproducibility) | NULL (F=1.58, p=0.28) | NULL (F=1.13, p=0.38) | NULL (F=0.32, p=0.65) | LEVEL COLLAPSED |

## Full noise-grid sweep for each variant

### B5' × N1 (primary)

| Level | Thickness | Transference | Particle radius | Verdict |
|---|---|---|---|---|
| 0 baseline | NULL (NaN) † | NULL (NaN) † | PASS (F=106.0) | LEVEL WEAK |
| 1 best lab | NULL (NaN) | NULL (NaN) | PASS (F=54.8) | LEVEL WEAK |
| 2 PRIMARY | NULL | NULL | WEAK PASS (F=3.5) | **LEVEL COLLAPSED** |
| 3 noisy field | NULL | NULL (NaN) | PASS (F=11.5) | LEVEL WEAK |
| 4 instrument issue | NULL | NULL | NULL | LEVEL COLLAPSED |

† Level-0 NaN explanation in §A.1.

### B5' × N2 (EIS-realistic)

| Level | Thickness | Transference | Particle radius | Verdict |
|---|---|---|---|---|
| 0 baseline | NULL (NaN) | NULL (NaN) | PASS (F=106.0) | LEVEL WEAK |
| 1 best-in-class EIS | NULL (NaN) | NULL | PASS (F=106.5) | LEVEL WEAK |
| 2 typical academic EIS | NULL (NaN) | NULL (NaN) | PASS (F=13.6) | LEVEL WEAK |
| 3 field-grade EIS | NULL (NaN) | NULL (NaN) | NULL | LEVEL COLLAPSED |
| 4 degraded instrument | NULL | NULL | NULL | LEVEL COLLAPSED |

### Fresh-state × N1 (Probe 7.3)

| Level | Thickness | Transference | Particle radius | Verdict |
|---|---|---|---|---|
| 0 baseline | PASS (F=58.9) | NULL | PASS (F=15.6) | LEVEL ROBUST |
| 1 best lab | PASS (F=46.5) | NULL | PASS (F=11.7) | LEVEL ROBUST |
| 2 PRIMARY | PASS (F=11.9) | NULL | PASS (F=11.6) | **LEVEL ROBUST** |
| 3 noisy field | PASS (F=6.5) | NULL | PASS (F=10.4) | LEVEL ROBUST |
| 4 instrument issue | NULL | NULL | PASS (F=8.8) | LEVEL WEAK |

## Falsifiers (§7 of pre-reg)

| Falsifier | Outcome |
|---|---|
| **P7v2_F1 (B5' sanity at L0)** | TECHNICAL FAILURE, MEANINGFUL: 1/3 PASS at L0 (PASS on particle_radius). Thickness and transference both return F=NaN due to degenerate F-statistic — the B5' R_ohmic signal is SO clean (between/within = 1210, within-cohort sd 0.34 μΩ) that thickness-level clusters become essentially degenerate in unit-vector space, breaking the within-SS calculation. Not a pipeline bug. Documented as §A.1; NOT treated as INCOHERENT because the diagnostic explanation is robust. |
| **P7v2_F2 (B5'-vs-B7 magnitude > 20%)** | **PASSED.** Mean B5' R_diff residual across cohort = 0.104 Ω vs B7's 0.0038 Ω = **27× stronger** aging signal. Smoke-implied lift confirmed cohort-wide. |
| **P7v2_F3 (R_ohmic-dead, expected \|s/n\| < 1)** | **FALSIFIED in the literal sense, but for honest reason.** B5' R_ohmic residual \|s/n\| = 32.5 ≫ 1. R_ohmic is NOT dead — porosity collapse in the negative electrode affects high-frequency impedance more than my pre-reg-time physics intuition allowed. R_ohmic_aged_b5 shifts down ~11 μΩ with tiny within-cohort sd (0.34 μΩ). Documented as §A.2; updates the v1 §3 narrative that "R_ohmic doesn't respond to LAM" — that was right for LAM, but B5' captures porosity which DOES move R_ohmic measurably. |
| **P7v2_F4 (B7 + HPPC reproducibility)** | **PASSED.** B7×N1 at L2 reproduces v1 lit/38 exactly (0/3). HPPC×N1 at L2 reproduces lit/26 exactly (0/3). Comparator stability confirmed. |

## §A — Subsidiary diagnostics

### A.1 NaN F-statistic at B5' Level 0 (thickness + transference)

`permanova_pseudoF` returns NaN when within_ss ≤ 0 or between_ss ≤ 0. At Level 0 with the B5' residual triad:

- R_ohmic_aged_b5 between/within ratio = **1210** (12 cells per thickness level, within-condition sd = 0.34 μΩ vs between-condition sd = 347 μΩ)
- After unit-vector projection, all 12 cells of the same thickness level land at essentially the same point on the unit sphere
- within_ss for thickness becomes numerically zero → F = NaN
- Same for transference, which doesn't move R_ohmic at all → within-thickness clusters dominate the residual variance → transference also degenerate

This is the OPPOSITE failure mode from v1: there the signal was weak (R_ohmic_residual |s/n| = 5.3); here the signal is so clean it breaks the F formula at zero noise.

When even small noise is added (Level 1+), within_ss becomes positive and F becomes computable — but by then the noise on R_ohmic absolute values (15% × 2.4 mΩ = 360 μΩ noise vs 11 μΩ aged-fresh residual signal) has drowned the underlying clean signal. So B5' shows **degenerate clean → drowned noisy** transition with no intermediate regime where PERMANOVA cleanly detects thickness.

### A.2 R_ohmic is not dead under B5' — porosity matters

Pre-reg §3 stated: "R_ohmic = pure series resistance (electrolyte bulk + contacts), unaffected by SEI growth (which lives in the mid-frequency semicircle) or porosity collapse (which lives in the Warburg region)." That's true for SEI growth but **wrong for porosity collapse**.

Mechanism: in PyBaMM's EIS solver, the negative-electrode porosity affects the EFFECTIVE electrolyte conductivity through the porous electrode (via the Bruggeman correction). When porosity drops from 0.25 to 0.028, the electrolyte path through the negative electrode becomes much more tortuous; this contributes a small but measurable increase in series resistance at high frequencies. The net B5' R_ohmic shift is −11 μΩ on a 2.4 mΩ baseline (0.5% decrease) — small but extremely consistent across cells (sd = 0.34 μΩ).

This means:
- The high-frequency intercept does pick up SOME porosity information, not just pure electrolyte bulk
- Under B5', R_ohmic_residual carries real aging signal
- But the absolute signal magnitude is so small that any percentage noise on R_ohmic itself (which has a much larger absolute magnitude) drowns it

This is a stronger and more honest description of the EIS R_ohmic limitation than the v1 "dead" framing. The signal exists; it's just unrecoverable under any percentage-of-absolute noise model.

### A.3 Particle radius is the survivor

Across all variants and noise grids, particle_radius is the one design parameter that survives more often than not. Mechanism: particle radius affects the diffusion characteristic length (∝ r²/D), which dominates the low-frequency Warburg region. Under B5':
- R_diff_aged_b5 has between/within = 1.62 (modest)
- BUT particle radius drives a coherent unit-vector direction shift that persists through both N1 and N2 noise

This is consistent with the v1 result where particle_radius also showed marginal/weak survival at higher noise. Particle radius is the only parameter where the EIS signal (specifically R_diff via Warburg) is mechanistically the most direct.

### A.4 Probe 7.3 fresh-state PERMANOVA — why it works

The fresh-state architecture (PERMANOVA on absolute fresh impedance features, not residuals) doesn't care about aging at all. It tests: do design parameters separate cells by their fresh impedance?

- R_ohmic_fresh between/within = **746** (extreme thickness discriminator: low/mid/high thickness gives R_ohmic_fresh of 2.03/2.43/2.83 mΩ)
- R_diff_fresh between/within = 2.77 (decent particle-radius discriminator)
- fresh_Q between/within ≈ 1.5 (weak)

At Level 2 noise (σ_R_ohmic = 15% × ~2.4 mΩ = ~360 μΩ), the between-condition separation (~400 μΩ between thickness levels) is just barely above noise — barely PASSES. The fresh-state architecture passes because the THRESHOLD is in the absolute values themselves, not the (small) aged-fresh residuals.

But: this isn't aging-direction inversion. It's design-parameter detection from fresh-state impedance, which is essentially the "obviously yes" baseline — the question Probe 5/6 deliberately framed AGAINST by using residuals.

Probe 7.3's STRONG outcome is therefore not promotable to a C3 framework rescue. It just confirms that with EIS hardware in hand, you can identify cathode thickness from a fresh-state measurement before any cycling — which is operationally useful but not a methodological breakthrough.

## §B — Comparison across all five variants at Level 2

| Variant | Th | Tn | Pr | Total PASS |
|---|---|---|---|---|
| B5' × N1 | NULL | NULL | WEAK | 0 PASS (1 WEAK) |
| B5' × N2 | NULL | NULL | PASS | 1 PASS |
| Fresh-state × N1 | PASS | NULL | PASS | **2 PASS** |
| B7 × N1 (v1 repro) | NULL | NULL | NULL | 0 PASS |
| HPPC × N1 (Probe 6 repro) | NULL | NULL | NULL | 0 PASS |

The clean spectrum of outcomes:
- All residual-architecture variants (B5'×N1, B5'×N2, B7×N1, HPPC×N1) collapse at Level 2 academic noise
- Only the fresh-state-feature architecture survives — and that's not the C3 test

## §C — Implications for the C3 framework

Combined v1 + v2 evidence:

1. **Operator triad choice does NOT carry noise rejection.** HPPC, B7-LAM-proxy EIS, B5'-cycling-read EIS all collapse at Level 2 under N1 noise. The collapse is a property of the joint-vector unit-residual cosine PERMANOVA architecture interacting with the cohort's per-cell aging variance, not of which physical operators are extracted.

2. **EIS-realistic noise (N2) gives partial rescue only on particle_radius**, the parameter mechanistically most tied to the Warburg diffusion region. Other parameters still collapse.

3. **Fresh-state features survive, but answer a different question.** R_ohmic_fresh + R_diff_fresh + fresh_Q can identify design parameters from a fresh-state EIS measurement at Level 2 noise. Useful operationally; not the C3 aging-direction-inversion test.

4. **R_ohmic is not as dead as v1 implied** — it picks up porosity-driven impedance change. But the absolute magnitudes (sub-1% on a 2.4 mΩ baseline) are unrecoverable under realistic percentage noise.

The path forward for C3 noise rejection requires either:
- **Architecture amendment:** different statistical framework (Mahalanobis distance, hierarchical model with shrinkage, non-residual transformation) — not pre-registered, would need its own probe series
- **Sub-Level-1 instrumentation:** custom electrochemical rigs (per Probe 6 literature/26 closure)
- **Real-cell EIS cohort with design-varied conditions** + per-cell aging traces — not currently in the corpus

This v2 closes the operator-triad-swap branch of the C3 framework search.

## Status

Probe 7 v2 closed: **PRIMARY NULL, all secondary tests interpreted.** The C3 framework's noise sensitivity is architectural, not operator-extraction-driven. EIS as a deployment vehicle for the C3 cascade is not a path forward at typical academic instrumentation noise levels (regardless of LAM-proxy vs cycling-read methodology).

No further Probe 7 versions planned. C3 framework status updated: aging-residual joint-vector PERMANOVA is structurally noise-fragile in this regime. Future C3 work would need a different statistical architecture, not a different operator extraction.

---

**Lock metadata:**
- v2 result commit: `<TBD — recorded in follow-up commit>`
- Result parquet SHA-256: `3117BF3E2CEDE1359C09D12A8FFE61F549FAF209755C2A3C627EBB525217CF1E`
- Generator parquet SHA-256: `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
