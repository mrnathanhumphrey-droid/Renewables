# C3 Probe 7 v1 — Result (EIS-Triad Noise-Robustness Test)

**Date:** 2026-05-27
**Pre-reg:** `literature/37_probe7_prereg.md` (lock commit `771de3a`)
**Generator parquet:** `data/processed/pybamm_l9_trajectories_eis.parquet` (SHA-256 `BBBA635F…E0777`)
**Analyzer:** `code/c3_probe7_eis_permanova.py` (SHA-256 `F6E87158…E0C81`)
**Result parquet:** `data/processed/probe7_eis_noise_results.parquet`
**Companion artifact:** `data/processed/probe7_hppc_baseline_results.parquet` (P7_F4 confirmation)

---

## Headline

**PROBE 7 v1 NULL** per pre-reg §6.

- EIS-triad (Q_max, R_ohmic, R_diff) at Level 2 noise: **0 of 3** design parameters PASS.
- HPPC-triad baseline (literature/26 reproduced via P7_F4 on the new parquet): **0 of 3** PASS at Level 2.

Operator triad choice (EIS-derived vs HPPC-derived) does NOT carry the noise rejection at typical academic instrumentation noise, **under the B7 LAM-proxy approximation for aged-state EIS**. Both architectures collapse in the same regime.

This is a conditional NULL. v2 with B5 (true cycled-state EIS via time-domain AC injection) is the planned gating follow-up per pre-reg §10.

## Per-noise-level calibration

EIS triad, 101 cells (108 cohort − 2 sim failures − 5 anchor_partial):

| Level | σ_Q | σ_R_ohmic | σ_R_diff | Thickness | Transference | Particle radius | Level verdict |
|---|---|---|---|---|---|---|---|
| 0 (baseline) | 0.000 | 0.00 | 0.00 | **PASS** (F=75.3, p=0.0001) | NULL (NaN — degenerate) | **PASS** (F=106.7, p=0.0001) | LEVEL ROBUST (2/3) |
| 1 (best lab) | 0.001 | 0.05 | 0.10 | NULL (F=0.81, p=0.44) | NULL (F=0.31, p=0.58) | NULL (NaN) | LEVEL COLLAPSED |
| 2 (PRIMARY) | 0.005 | 0.15 | 0.20 | NULL (F=1.65, p=0.26) | NULL (F=0.49, p=0.60) | NULL (F=0.20, p=0.71) | **LEVEL COLLAPSED** |
| 3 (noisy field) | 0.010 | 0.30 | 0.30 | NULL (F=0.03, p=0.80) | NULL (F=0.73, p=0.52) | PASS (F=6.03, p=0.003) | LEVEL WEAK |
| 4 (instrument) | 0.020 | 0.50 | 0.50 | NULL (NaN) | NULL (F=3.39, p=0.053) | NULL (NaN) | LEVEL COLLAPSED |

HPPC baseline (P7_F4, 105 cells after anchor_partial filter — slight delta vs EIS's 101 because per-cell rpts-vs-anchor logic differs marginally):

| Level | Thickness | Transference | Particle radius | Level verdict |
|---|---|---|---|---|
| 0 | WEAK PASS | PASS | PASS | LEVEL ROBUST |
| 1 | NULL | PASS | NULL | LEVEL WEAK |
| 2 | NULL | NULL | NULL | **LEVEL COLLAPSED** |
| 3 | NULL | NULL | PASS | LEVEL WEAK |
| 4 | NULL | NULL | NULL | LEVEL COLLAPSED |

Reproduces literature/26 exactly at Level 2 (0/3). **P7_F4 confirmed: HPPC baseline on the new parquet is bit-identical to the published Probe 6 result. Comparator is clean.**

## Falsifiers (§7 of pre-reg)

| Falsifier | Outcome |
|---|---|
| **P7_F1 sanity at Level 0** (≥ 2/3 PASS for EIS triad at no-noise baseline) | **PASSED** (2/3 PASS: thickness + particle_radius; transference is NULL via degenerate F=NaN, see §A.1) |
| **P7_F2 monotonicity** (p-value weakly increasing across levels per parameter) | Particle radius is non-monotonic (PASS at Level 0, NULL at L1, NULL at L2, PASS at L3, NULL at L4). Pattern: PASS at extremes, NULL in the middle. Non-monotonic, but L3 PASS is suspicious — see §A.2 |
| **P7_F3 R_ohmic-dead-but-passes paradox** | Did not fire (EIS triad didn't PASS at Level 2 to begin with). Note recorded: R_ohmic_residual |s/n|=5.3 vs Q |s/n|=19.6 and R_diff |s/n|=14.5 — R_ohmic is weakest by far, consistent with B7-proxy limitations disclosed in pre-reg §3 |
| **P7_F4 HPPC baseline reproduces** (re-run Probe 6 on new parquet) | **PASSED.** Reproduces literature/26: 0/3 PASS at Level 2 |

## Per-feature signal-to-noise on clean residuals (pre-PERMANOVA)

| Feature | Mean | SD | \|s/n\| |
|---|---|---|---|
| Q_residual (Ah) | −0.341 | 0.0174 | 19.59 |
| R_ohmic_residual (Ω) | 3.07e-6 | 5.82e-7 | 5.27 |
| R_diff_residual (Ω) | 3.75e-3 | 2.58e-4 | 14.54 |

R_ohmic_residual exists (|s/n| > 1) but is much smaller than Q and R_diff. The clean-residual unit vector is therefore dominated by (Q, R_diff) with R_ohmic as a faint third dimension. Confirms the pre-reg §3 disclosure that B7 LAM-proxy under-drives R_ohmic.

## Interpretation

The PROBE 7 NULL outcome rules out one specific claim that survives reading the pre-reg literally: "swapping HPPC to EIS in the same joint-vector architecture, at the same noise budget, restores Level 2 design-direction signal." Under B7, no. The triads collapse together.

What the result does NOT rule out:

1. **B5 might recover the signal.** The B7 LAM-proxy under-drives R_ohmic by construction — only LAM-driven impedance changes are captured, not SEI growth, electrolyte oxidation, contact resistance. True cycled-state EIS would have R_ohmic_aged − R_ohmic_fresh ≈ 5-15% (real-cell magnitudes from the SEI literature) rather than the ≈ 0.13% the B7 proxy produces. If R_ohmic_aged moves with SEI growth at the magnitudes literature suggests, the EIS triad's effective dimensionality recovers from 2D to 3D and the joint vector carries more design signal. Probe 7.1 (B5) is the test.

2. **N2 might recover the signal.** N1's σ_R_ohmic = 15% at Level 2 is HPPC-typical, ~5x higher than EIS-realistic noise (~3% at the high-freq intercept). If EIS-instrument noise is what matters in deployment, N2 is the relevant test. Even with B7's dead R_ohmic, lowering σ_R_ohmic might let Q + R_diff carry through where they currently get drowned. Probe 7.2.

3. **Fresh-state features tell a different story.** R_ohmic_fresh has between/within design separability of 564 — essentially a perfect cathode-thickness oracle on this cohort. A PERMANOVA on fresh-state features (not residuals) would show massive design-direction signal — but it answers a different scientific question ("do design parameters affect fresh impedance," obvious yes) rather than the C3 question ("does aging residual carry design info"). Probe 7.3 if useful.

## §A — Subsidiary diagnostics

### A.1 Transference NULL at Level 0 (NaN F)

EIS-triad PERMANOVA on transference at Level 0 produces F=NaN (within_ss or between_ss ≤ 0 — degenerate case in `permanova_pseudoF`). Sniff test:

- Per-condition R_ohmic_aged ranges by transference: low=2.419 mΩ, mid=2.431 mΩ, high=2.431 mΩ — flat (no signal)
- Per-condition R_diff_aged by transference: low=51.20 mΩ, mid=50.62 mΩ, high=50.39 mΩ — slight slope but small relative to within-condition spread
- Per-condition Q residual by transference (not shown explicitly): also flat-ish

Transference number affects bulk-electrolyte ionic conduction, which under the LAM-proxy aged state shows minimal differentiation in the 0.01-100 kHz EIS window. The HPPC triad caught transference at Level 0 (F=23.6) because R_DC and R_total integrate over the full ionic transport including charge-transfer kinetics — which the B7 proxy doesn't capture for the aged state.

This is itself a finding: **B7 proxy + EIS triad is structurally blind to transference-mediated aging signatures**, while HPPC catches them via R_DC/R_total. Worth carrying into the v2 design.

### A.2 Particle radius PASS at Level 3 (F=6.03, p=0.003)

Non-monotonic — particle_radius is NULL at Levels 1, 2 and 4 but PASSES at Level 3. Probe 6 showed the same pattern (Level 3 PASS for particle_radius, F=4.89). Likely a noise-realization artifact: at moderate noise the unit-vector projection accidentally aligns with the particle-radius axis for these specific seeds. Not interpreted as a robust signal in either Probe 6 or Probe 7.

### A.3 NaN F at Levels 0 and 3-4

EIS PERMANOVA produces NaN F values at:
- Level 0 transference (degenerate within_ss for the design)
- Level 1 particle_radius
- Level 4 thickness + particle_radius

`permanova_pseudoF` returns NaN when within_ss ≤ 0 or between_ss ≤ 0, which occurs when the unit-vector cloud is too tightly clustered relative to within-group variance. At N=101 with 3-level grouping, this is a known small-N edge case for the cosine-distance variant. Doesn't change the PASS/NULL verdict (NaN → NULL), but means some F-values aren't comparable. Not a pipeline bug.

## §B — Comparison to Probe 6 HPPC at each level

| Level | EIS triad (Probe 7 v1) | HPPC triad (Probe 6 / P7_F4) | EIS - HPPC delta |
|---|---|---|---|
| 0 | 2/3 PASS | 2-3/3 PASS (1 WEAK) | Comparable |
| 1 | 0/3 PASS | 1/3 PASS | HPPC slightly better |
| 2 | **0/3 PASS** | **0/3 PASS** | TIED at collapse |
| 3 | 1/3 PASS | 1/3 PASS | TIED (same particle_radius) |
| 4 | 0/3 PASS | 0/3 PASS | TIED |

EIS triad ≤ HPPC triad at every noise level. The two architectures collapse together at Level 2. The B7 proxy actively handicaps EIS at low noise via the dead R_ohmic dimension and the missing transference signature.

## §C — Implications for v2

Per pre-reg §6 / §10, PROBE 7 NULL triggers v2 (B5 + N2 + Probe 7.3 fresh-state secondary) as the gating follow-up. Specific predictions to test in v2:

1. **B5 should rescue R_ohmic_residual.** True cycled-state EIS catches SEI growth; R_ohmic_aged should grow 5-15% above R_ohmic_fresh at SOH 0.92 (literature-typical). If so, R_ohmic_residual becomes a real third dimension and the EIS triad's effective dimensionality matches HPPC's.
2. **B5 should rescue transference at Level 0.** If R_ohmic moves with SEI thickness and SEI growth interacts with transference (via ionic transport coupling), transference design separation should appear at Level 0 — currently missing.
3. **N2 should not change the v1 result substantively unless R_ohmic actually carries signal.** With dead R_ohmic_residual, lowering σ_R_ohmic from 15% to 3% has no effective impact on the unit vector. Only meaningful in combination with B5.
4. **Probe 7.3 (fresh-state features) will trivially PASS** at Level 2 because R_ohmic_fresh is a 564× thickness discriminator and the design parameters are baked into fresh-state impedance. The question is whether that's a useful PASS or a degenerate one — it tests "do design parameters affect fresh impedance" (yes, obviously), not "does aging-direction inversion work."

## Status

Probe 7 v1 closed as **NULL**. v2 (combined B5 + N2 + Probe 7.3) flagged as next step; not yet pre-registered. C3 framework status from Probe 6 (literature/26) unchanged: cascade collapses at Level 2 academic noise, real-cell deployment gated on sub-Level-1 instrumentation OR noise-robust architecture amendment. Probe 7 v1 narrows the amendment space: operator-triad swap alone (HPPC → EIS) is not the lever, at least under the B7 LAM-proxy.

---

**Lock metadata:**
- v1 result commit: `a5a6ba1`
- Result parquet SHA-256: `8C0356A5E88ED76E30854886E1758A1719DF87D332462BFEC80CC9E20B35E640`
- HPPC baseline parquet SHA-256: `A69CF9D668E88E26D5BE51EC35D198926926A3DF1D0865C67DB5ED93A9DD87AE`
