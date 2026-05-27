# C3 Probe 7 — EIS-Triad vs HPPC-Triad Noise-Robustness Test (Pre-Registration)

**Status:** DRAFT — locks on Nathan's sign-off, before any PERMANOVA runs.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/37_probe7_prereg.md`
**Lock anchor:** commit hash of the merge that lands this file + the generator parquet hash.

---

## 0. Why Probe 7 exists, restated (corrects an earlier motivation error)

An earlier draft (informally labeled "Aggron pre-reg") motivated Probe 7 as a "joint-vector vs marginal-PERMANOVA" test on the premise that Probe 6 used marginal per-operator PERMANOVAs. **That premise was wrong.** Probe 6 (`code/c3_noise_injection.py`, lines 183-194) already runs the joint-vector unit-residual PERMANOVA with cosine distance — the exact C1 architecture. Its "all 3 design-direction PERMANOVAs collapse at Level 2" outcome is three joint-vector PERMANOVAs *against three design parameters*, not three marginal tests.

So the actual unanswered question after Probe 6 is **whether the operator triad choice carries the noise rejection**. Probe 6 collapsed the joint-vector architecture on the HPPC triad (Q_max, R_DC, R_total). Probe 7 swaps in an EIS-derived triad (Q_max, R_ohmic, R_diff) — which measures different physical processes than HPPC — and asks whether the same joint-vector architecture survives Level 2 noise where the HPPC version failed.

## 1. Hypothesis (LOCKED)

**H7 (primary):** On the same Probe 5 cohort, at identical noise levels, joint-vector unit-residual cosine PERMANOVA on the EIS-derived triad (Q_max, R_ohmic, R_diff) recovers design-direction signal at Level 2 noise that the same architecture on the HPPC-derived triad (Q_max, R_DC, R_total) does not.

**Operationalization:** At Level 2 noise, ≥ 2 of 3 design parameters (cathode thickness, transference number, particle radius) PASS for the EIS triad under the standard parameter_verdict rule (p < 0.0167 AND F > 3.0). Probe 6's Level 2 result on the HPPC triad is the comparator (0 of 3 PASS).

**H7 (null):** EIS triad collapses similarly. ≤ 1 of 3 PASS at Level 2.

## 2. Cohort (LOCKED)

- **108-cell Probe 5 L9 Taguchi factorial** at the same per-cell seeds as `code/modal_pybamm_c3.py` (verified: cycling outputs for cond=0/cell=0 are bit-identical between v1 and the new EIS-augmented generator).
- **Source parquet:** `data/processed/pybamm_l9_trajectories_eis.parquet`, produced by `code/probe7_pybamm_eis_generator.py`. 106 of 108 cells successful (98.1% yield, identical to v1; same 2 cells fail with PyBaMM IDAKLU "no consistent states" at cycle ~25).
- **HPPC baseline comparator:** Probe 6 result on `data/processed/pybamm_l9_trajectories.parquet` (commit `273be36`, literature/26 "H7 SUPPORTS NOISE EXPLANATION" — 0/3 PASS at Level 2). Note: the new parquet's HPPC columns are bit-identical to v1's where the same cells exist.

## 3. EIS operator extraction method (LOCKED — with honest approximation disclosure)

The aged-state EIS in this v1 is an **approximation, not true cycled-state EIS**, because PyBaMM's `EISSimulation.set_initial_state()` does not accept a cycling-solution state vector (only SoC or voltage). The chosen approximation:

- **Fresh-state EIS:** `pybamm.EISSimulation` on the cell's design-parameter `ParameterValues` (Chen2020 + Yang2017 SEI + `surface form: differential`) at fresh state. R_ohmic = Re[Z(100 kHz)], R_diff = Re[Z(0.01 Hz)] − R_ohmic. 30-point log-spaced frequency grid.
- **Aged-state EIS ("B7 proxy"):** EIS on a *modified* `ParameterValues` where the positive and negative active material volume fractions are reduced by Q_loss_frac = 1 − (uniform_aged_Q / fresh_Q), with uniform_aged_Q = the cell's RPT closest to SOH 0.92 (matching Probe 5's uniform-anchor convention). Per-cell Q_loss_frac is recorded (mean ≈ 0.08, range ~0.06-0.16).

**What this approximation captures faithfully:** LAM-driven impedance changes — primarily R_diff growth via reduced active material area, secondarily reduced solid-state diffusion paths.

**What it does NOT capture:** SEI thickening, electrolyte oxidation, lithium plating, contact resistance growth. These are real cycled-state EIS signatures that the LAM-only proxy cannot produce. Notable empirical consequence already observed in the generated parquet:
- R_ohmic_aged ≈ R_ohmic_fresh (mean residual 3.1 µΩ on a 2.4 mΩ baseline ≈ 0.13% change)
- R_diff_aged grows ~7-8% above R_diff_fresh at uniform anchor

So in this v1, **R_ohmic_residual is effectively dead as an aging signal** and any per-cell variance in R_ohmic_residual is driven by the small (~2% sd) active-material-volume-fraction perturbation in `make_param_values`, not by aging. This is a known limitation of the B7 approach; **true cycled-state EIS via time-domain AC injection at the cycling-solver terminal state (the "B5" alternative) is the planned Probe 7.1 follow-up if v1 lands a substantive result.**

## 4. PERMANOVA method (LOCKED — identical architecture to `c3_noise_injection.py`)

Per cell *i* at noise level *L*:

1. Residual vector: r_i = (aged_Q − fresh_Q, R_ohmic_aged − R_ohmic_fresh, R_diff_aged − R_diff_fresh), with noise injected per §5 onto all six absolute values before differencing.
2. Z-score each coordinate by the fresh-pool SD (computed on the noisy fresh values, matching Probe 6's logic).
3. Project to unit vector: u_i = z_i / ||z_i||₂.
4. For each design parameter *p* ∈ {thickness_level, transference_level, particle_radius_level}:
   - PERMANOVA on the 108-cell unit-vector set (cosine distance: 1 − cos θ)
   - 10,000 label permutations
   - pseudo-F + permutation p-value
5. Per-parameter verdict (per Probe 5/6 convention):
   - **PASS:** p < 0.0167 (Bonferroni α/3) AND F > 3.0
   - **WEAK PASS:** 0.0167 ≤ p < 0.05 AND F > 2.0
   - **NULL:** otherwise

## 5. Noise grid (LOCKED — v1 = N1 only; secondary grids deferred to v2)

**N1 (PRIMARY, v1):** Identical to Probe 6's noise grid. Multiplicative Gaussian noise applied independently to fresh and aged values at each level. Per-cell seeds: `2000 + level*10000 + cond_idx*100 + cell_idx` (matches `c3_noise_injection.py` `RNG_SEED_BASE`).

| Level | σ_Q | σ_R_ohmic | σ_R_diff | Calibration story |
|---|---|---|---|---|
| 0 | 0.000 | 0.00 | 0.00 | Synthetic ground truth |
| 1 | 0.001 | 0.05 | 0.10 | "Best lab" — Probe 6's σ_R_DC and σ_R_total mapped to (R_ohmic, R_diff) by position in the magnitude order |
| 2 | 0.005 | 0.15 | 0.20 | **PRIMARY** — typical academic, identical magnitude to Probe 6 |
| 3 | 0.010 | 0.30 | 0.30 | Noisy field |
| 4 | 0.020 | 0.50 | 0.50 | Instrument issue |

**Rationale for N1:** keeps the EIS-vs-HPPC comparison apples-to-apples on noise magnitude. The σ values are physically generous to EIS instrument noise (real EIS-R_ohmic noise is typically 1-3%, not 15%; real EIS-R_diff noise is 5-15%, not 20%). v1 reports under the conservative-for-EIS choice; v2 will re-test under EIS-realistic levels (N2).

**Honest caveat baked into the pre-reg:** if v1 H7 PASSES at N1 noise, the result is "EIS survives even when handicapped to HPPC-typical noise levels" — a strong claim. If v1 H7 FAILS at N1, v2 must run before concluding the operator triad doesn't matter.

## 6. Disposition criteria (LOCKED)

| Verdict | Level 2 outcome | What it means |
|---|---|---|
| **PROBE 7 STRONG** | ≥ 2 of 3 EIS-triad PASS at Level 2 (vs 0/3 for HPPC at Level 2) | Operator triad choice carries noise rejection. EIS-derived triad is the better deployment vehicle. Path opens to a C3 framework amendment that requires EIS-based operators for real-cell deployment. |
| **PROBE 7 PARTIAL** | 1 of 3 EIS-triad PASS at Level 2 | EIS triad gains *some* rejection but doesn't fully reverse Probe 6's collapse. Worth a Probe 7.1 with B5 time-domain EIS to test whether the LAM-proxy approximation is what's holding it back. |
| **PROBE 7 NULL** | 0 of 3 EIS-triad PASS at Level 2, same as HPPC | Operator triad does not carry the noise rejection (under the B7 proxy). v2 (B5 method + N2 grid) becomes the gating follow-up; if both also fail, the C3 architecture's noise sensitivity is operator-agnostic. |
| **PROBE 7 INCOHERENT** | Level 0 EIS-triad fails to recover ≥ 2 of 3 PASS (the no-noise sanity check) | Pipeline bug or LAM-proxy artifact severe enough to break baseline. Debug + re-run. |

**Joint v1+v2 disposition (post-Probe 7.1, after running v2):** a separate writeup will integrate B7-vs-B5 + N1-vs-N2 + residual-vs-fresh-state findings. v1 alone does not amend the C3 closure.

## 7. Falsifiers (LOCKED)

**P7_F1 (sanity at Level 0):** If the EIS triad fails to achieve ≥ 2 of 3 PASS at noise Level 0 (where the same architecture on HPPC achieves 2-3 of 3), the B7 LAM-proxy approximation is too lossy to test H7. Disposition: INCOHERENT. Triggers B5 build before re-running.

**P7_F2 (monotonicity):** Noise-monotonicity check — at any per-parameter PERMANOVA, p-value should weakly increase across noise levels 0→4 (modulo permutation variance). Violations of >0.15 between adjacent levels for the same parameter trigger debug rather than reporting.

**P7_F3 (R_ohmic-dead-but-passes paradox):** If the EIS triad PASSES at Level 2 while the per-feature signal-to-noise of R_ohmic_residual is < 1 (i.e., R_ohmic_residual is dominated by amvf perturbation noise, contributes essentially nothing), the PASS is being carried by Q_residual + R_diff_residual alone — which is a 2D-effective signal. Report this explicitly. The PASS is real but the "EIS triad" framing weakens because R_ohmic is a passive third dimension.

**P7_F4 (HPPC re-run consistency):** Re-run Probe 6 against the NEW parquet (which has bit-identical cycling outputs to v1) to confirm the HPPC Level-2 baseline reproduces 0/3 PASS. If it doesn't, the comparator drifted and the EIS-vs-HPPC claim cannot be made cleanly. Triggers debug before Probe 7 result is published.

## 8. What this v1 does NOT establish

- **Not a real-cell validation.** Entirely synthetic; the synthetic-to-real gap closed by Probe 6 at Level 2 still applies. EIS triad PASS at Level 2 in synthetic does NOT mean EIS-equipped real cells would PASS.
- **Not a test of true cycled-state EIS.** The B7 LAM-proxy approximates only one aging mechanism (active material loss). v1 PASS or NULL is conditional on this approximation; B5 in v2 tests the full cycled-state EIS.
- **Not a C3 framework amendment.** Even PROBE 7 STRONG is one piece of evidence. The C3 amendment requires: STRONG at v1 + STRONG at v2 (B5) + a real-cell cohort with EIS or a defensible reason to skip that step.
- **Not a fresh-state-feature test.** The residual architecture matches Probe 5/6 by construction. A separate test using fresh-state features (where R_ohmic_fresh is a 564× between/within thickness oracle on this cohort) would change the test's meaning to "do design parameters affect fresh impedance" — a different and arguably less interesting question. Logged as planned Probe 7.3.

## 9. Operational protocol (LOCKED execution order)

1. Sign-off + commit this pre-reg as `literature/37_probe7_prereg.md`. Lock anchor = commit hash.
2. Lock the generator parquet hash: `data/processed/pybamm_l9_trajectories_eis.parquet` is the data of record. Compute SHA-256 and record at the bottom of this file post-commit (so re-runs are detectable).
3. Run `code/c3_probe7_eis_permanova.py` (clone of `c3_noise_injection.py` operating on the EIS triad, against the same noise grid). Write output to `data/processed/probe7_eis_noise_results.parquet`.
4. Re-run `code/c3_noise_injection.py` against the new parquet (HPPC baseline confirmation per P7_F4). Output to `data/processed/probe7_hppc_baseline_results.parquet`. If this doesn't reproduce literature/26's 0/3-at-Level-2, debug.
5. Apply §6 disposition criteria + §7 falsifiers.
6. Write up `literature/38_probe7_v1_result.md`.
7. If disposition is STRONG or PARTIAL, queue v2 (B5 + N2 + Probe 7.3 fresh-state secondary).

## 10. Planned v2 follow-ups (NOT pre-registered in this v1 lock, but explicitly named)

- **Probe 7.1 (B5):** Time-domain AC injection at cycling-solver terminal state. 1 kHz + 0.01 Hz sinusoidal current; FFT of V(t)/I(t) gives true cycled-state Z(f) at fresh + aged. Replaces B7's LAM-proxy. Each cell adds ~100 sec sim time → ~10 min wall at 16-wide.
- **Probe 7.2 (N2):** Re-run §4 PERMANOVA under EIS-instrument-realistic noise: σ_R_ohmic ≈ 1-3%, σ_R_diff ≈ 5-15% at Level 2.
- **Probe 7.3 (fresh-state secondary):** PERMANOVA on fresh-state features (R_ohmic_fresh, R_diff_fresh, fresh_Q) rather than residuals. Different test, different scientific claim — "do design parameters affect fresh impedance" — but lets R_ohmic_fresh's 564× cathode-thickness discrimination show its size.

All three follow-ups will be pre-registered separately if v1 result warrants.

## 11. Pre-commit checklist

- [ ] Nathan signs off on v1 spec as-locked (B7 proxy + residual architecture + N1 noise grid + planned v2 follow-ups)
- [ ] Generator parquet `pybamm_l9_trajectories_eis.parquet` exists at expected path
- [ ] Generator parquet HPPC columns reproduce v1 exactly (already verified for cond=0/cell=0)
- [ ] Pre-reg committed + pushed to `origin/main` BEFORE running PERMANOVA scripts
- [ ] Throwaway smoke files (`code/_probe7_*.py`) cleaned up

## 12. Pre-registration deviation log

_(Will be filled in if any deviations during execution.)_

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD — recorded in follow-up commit>`
- Generator parquet SHA-256: `BBBA635FCE7797919FA7140DF3D4CB2835FBA14F54F9261949C1B42C85A0E777`
- Generator script SHA-256: `E95E60B6C586F1E74204FD2AB37D41065EA17FE814CD3556F08409DCA8E6653F` (`code/probe7_pybamm_eis_generator.py`)
- Analyzer script SHA-256: `F6E87158EEFEE441D96209446A49BF4A950263CA720565B4B675C5078F3E0C81` (`code/c3_probe7_eis_permanova.py`)
