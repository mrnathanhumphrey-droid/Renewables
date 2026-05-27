# C3 Probe 7 v2 — Pre-Registration (B5' Cycling-Read Aged-EIS + N2 + Fresh-State Secondary)

**Status:** DRAFT — locks on Nathan's sign-off, before any v2 PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/39_probe7_v2_prereg.md`
**Prior:** literature/37 (v1 pre-reg, `771de3a`) + literature/38 (v1 NULL result, `a5a6ba1`) + commit-hash lock `9608810`.

---

## 0. Why v2 exists, in two parts

**Part A — v1 had a methodological flaw, not just an approximation.**
v1's B7 LAM-proxy aged-state EIS was based on a misconception. v1 pre-reg §3 disclosed it as "approximation, not true cycled-state EIS." A v2 smoke discovered something sharper: **PyBaMM Chen2020 + Yang2017 SEI cycling does not move active material volume fractions at all.** Aged X-averaged amvf at terminal = initial amvf, exactly. So B7's modification (reduce amvf by Q_loss_frac) imposed an aging mechanism (LAM) that **doesn't happen in this synthetic cohort** — the actual aging is SEI growth + negative-electrode porosity collapse. v1 result is therefore conditional on an off-target proxy, not just a partial one.

Actual cycling-derived aging at anchor SOH 0.92 (cond=0/cell=0 smoke):
- X-averaged negative SEI thickness: **5 nm → 557 nm** (110× growth)
- X-averaged negative-electrode porosity: **0.25 → 0.040** (84% collapse)
- Active material volume fractions: **unchanged**

**Part B — corrected B5' methodology with same hypothesis.**
For each cell, read the X-averaged negative SEI thickness and X-averaged negative-electrode porosity at the cycling solution's uniform-anchor cycle (closest to SOH 0.92). Build a new `ParameterValues` with `Initial SEI thickness [m]` and `Negative electrode porosity` set to those cycling-read values. Run `pybamm.EISSimulation` on the modified `ParameterValues`. Output R_ohmic_aged_b5 and R_diff_aged_b5.

Smoke result on cond=0/cell=0: **B5' R_diff_aged growth = +145% vs B7's +8%** (19× stronger aging signal). R_ohmic remained flat at −0.5%, consistent with EIS physics — R_ohmic = pure series resistance (electrolyte bulk + contacts), unaffected by SEI growth (which lives in the mid-frequency semicircle) or porosity collapse (which lives in the Warburg region).

## 1. Hypotheses (LOCKED)

**H7v2-primary (B5' under N1 noise grid):** The same joint-vector unit-residual cosine PERMANOVA on the EIS triad (Q_max, R_ohmic, R_diff) — with R_ohmic and R_diff now derived from B5' cycling-read state — passes Level 2 noise where v1 (B7) and Probe 6 (HPPC) collapsed. Operationalization: ≥ 2 of 3 design parameters PASS at Level 2 under N1 noise.

**H7v2-null:** ≤ 1 of 3 PASS at Level 2 under N1. B5' methodology does not rescue the EIS-triad noise rejection.

**H7v2-secondary-1 (N2 EIS-realistic noise):** Under N2 noise (σ_R_ohmic ∈ {0, 0.01, 0.03, 0.10, 0.20}, σ_R_diff ∈ {0, 0.05, 0.15, 0.25, 0.40}), B5' EIS triad passes ≥ 2 of 3 at Level 2. This tests whether the operator triad survives noise that is REALISTIC for EIS instrumentation (rather than HPPC-imported magnitudes from N1).

**H7v2-secondary-2 (Probe 7.3, fresh-state-feature PERMANOVA):** PERMANOVA on the absolute fresh-state EIS triad (Q_max_fresh, R_ohmic_fresh, R_diff_fresh) — NOT residuals — at the same noise grids passes nearly universally because R_ohmic_fresh has between/within design separability of 564 on this cohort (already established in v1 inspection). This is reported as a "different test answers a different question": *do design parameters affect fresh impedance?* Yes. Not as evidence for the C3 framework's noise rejection, just as a calibration of what the data structure permits.

## 2. Cohort + parquet (LOCKED)

- 108-cell Probe 5 L9 Taguchi factorial (identical seeds to `code/modal_pybamm_c3.py`).
- **Generator:** `code/probe7v2_pybamm_b5_generator.py` — outputs both v1's B7 aged-EIS values (kept for direct B5'-vs-B7 comparison) and v2's B5' aged-EIS values, plus cycling-read state variables (sei_neg_aged_m, neg_porosity_aged). Same L9 design + per-cell seed convention as v1 generator (bit-identical cycling outputs verified at smoke).
- **Parquet:** `data/processed/pybamm_l9_trajectories_eis_v2.parquet`.
- Expected yield: ~106/108 successful (same PyBaMM IDAKLU failure rate as v1).

## 3. Operator extraction (LOCKED — B5' methodology)

For each cell at the uniform-anchor cycle (closest cycle to SOH 0.92, ±0.02 band):

1. **Read aging state from cycling solution at anchor cycle:**
   - `sei_neg_aged_m` = `sol.cycles[anchor_cycle-1]["X-averaged negative SEI thickness [m]"].entries[-1]`
   - `neg_porosity_aged` = `sol.cycles[anchor_cycle-1]["X-averaged negative electrode porosity"].entries[-1]`
2. **Build aged-state ParameterValues:**
   - Start from Chen2020 with same design + per-cell perturbation as `make_param_values`
   - Override: `Initial SEI thickness [m]` = `sei_neg_aged_m`
   - Override: `Negative electrode porosity` = `neg_porosity_aged`
3. **Run `pybamm.EISSimulation` on the aged ParameterValues:**
   - 30-point log-spaced frequency grid from 0.01 Hz to 100 kHz
   - R_ohmic_aged_b5 = Re[Z(100 kHz)]
   - R_diff_aged_b5 = Re[Z(0.01 Hz)] − R_ohmic_aged_b5

**Honest scope limitation explicitly named:** This is still a parameter-modification approximation, not direct cycled-state EIS via time-domain AC injection. The "right" approach would be `set_initial_state(cycling_solution)` directly into `EISSimulation`, which PyBaMM 26.4.4 does not support. B5' is the best available approximation given the API, and it differs from B7 in being driven by *cycling-sim-observed* aging-state variables, not user-imposed Q-loss proxies.

**What B5' captures that B7 missed:**
- SEI growth (110× in cond=0/cell=0 smoke)
- Negative-electrode porosity collapse (84% loss)

**What B5' still doesn't capture:**
- Lithium loss as a separate operator (it's implicit in SEI growth via Loss of capacity to negative SEI, but no direct EIS hook)
- Electrolyte concentration shifts during aging
- Cell terminal voltage changes from aging (since EISSimulation re-equilibrates to fresh SoC=1.0, not the aged cell's actual fully-charged voltage)

The PROBE 7 v1 NULL stands as a finding about the B7 proxy; PROBE 7 v2's result is a finding about the B5' methodology. Neither is the final word on real-cell EIS deployment, which would require a real-cell cohort with EIS at design-varied conditions (not currently available in the corpus).

## 4. PERMANOVA architecture (LOCKED — identical to v1)

For each variant (B5'×N1, B5'×N2, fresh-state×N1, fresh-state×N2):

1. Residual or absolute vector per §4a/§4b.
2. Z-score by per-noise-level pool SD.
3. Project to unit sphere: u = z / ||z||.
4. Cosine PERMANOVA per design parameter (10,000 permutations).
5. PASS / WEAK PASS / NULL verdicts per Probe 5/6 convention (p < 0.0167 + F > 3.0; or 0.0167 ≤ p < 0.05 + F > 2.0).

### 4a. B5'×N1 and B5'×N2 (residual architecture)

Same as v1: residual vector r_i = (aged_b5 - fresh) per coordinate. Unit projection. PERMANOVA.

### 4b. Fresh-state (Probe 7.3)

Use absolute fresh-state values as features (not residuals): u_i = (fresh_Q, fresh_R_ohmic, fresh_R_diff). Z-score by pool SD. Unit projection. PERMANOVA.

This is methodologically distinct from Probe 5/6 (which use residuals); flagged in §1 as a different test answering a different question.

## 5. Noise grids (LOCKED)

**N1 (PRIMARY — apples-to-apples vs v1 + Probe 6):** Identical magnitudes to literature/37 §5.

| Level | σ_Q | σ_R_ohmic | σ_R_diff | Story |
|---|---|---|---|---|
| 0 | 0.000 | 0.00 | 0.00 | Synthetic ground truth |
| 1 | 0.001 | 0.05 | 0.10 | "Best lab" (HPPC-typical mapped) |
| 2 | 0.005 | 0.15 | 0.20 | Typical academic (PRIMARY) |
| 3 | 0.010 | 0.30 | 0.30 | Noisy field |
| 4 | 0.020 | 0.50 | 0.50 | Instrument issue |

**N2 (EIS-realistic):** σ_R_ohmic and σ_R_diff calibrated to EIS-typical instrument noise per the impedance-spectroscopy literature.

| Level | σ_Q | σ_R_ohmic | σ_R_diff | Story |
|---|---|---|---|---|
| 0 | 0.000 | 0.000 | 0.00 | Synthetic ground truth |
| 1 | 0.001 | 0.010 | 0.05 | Best-in-class EIS (modulator-fit at high freq) |
| 2 | 0.005 | 0.030 | 0.15 | Typical academic EIS (PRIMARY for N2) |
| 3 | 0.010 | 0.100 | 0.25 | Field-grade EIS |
| 4 | 0.020 | 0.200 | 0.40 | Degraded instrument |

**Seed convention:** N1 uses RNG_SEED_BASE = 2000 (matches Probe 6 + v1). N2 uses RNG_SEED_BASE = 3000 (separate seed family — different noise realizations from N1 even at matching levels).

## 6. Disposition criteria (LOCKED)

Per variant, headline is at Level 2.

| Variant | Level 2 outcome | Verdict |
|---|---|---|
| B5'×N1 | ≥ 2/3 PASS | **B5' RESCUES** — the corrected aged-EIS methodology recovers Level-2 noise rejection that v1's B7 proxy failed at. The C3 framework's noise sensitivity was operator-extraction-specific, not architecture-specific. |
| B5'×N1 | 1/3 PASS | **B5' PARTIAL RESCUE** — B5' is stronger than B7 but still doesn't fully reverse the Level-2 collapse. |
| B5'×N1 | 0/3 PASS | **B5' DOES NOT RESCUE** — even with cycling-read aging-state-derived EIS, the architecture collapses at Level 2 academic noise. Confirms v1's narrative: the C3 architecture's noise sensitivity is architectural, not operator-proxy-driven. |
| B5'×N2 | Compared to B5'×N1 | Records the EIS-instrument-realistic noise outcome. Headline reported but does not amend the C3 framework status alone. |
| Fresh-state × N1 | Records design-discrimination at all noise levels | Expected near-universal PASS via R_ohmic_fresh's 564× thickness oracle; reported as data-structure calibration, not framework evidence. |

## 7. Falsifiers (LOCKED)

**P7v2_F1 (B5' sanity at Level 0):** B5'×N1 at Level 0 must achieve ≥ 2/3 PASS. If not, the B5' methodology has destroyed signal that even no-noise residuals carry. INCOHERENT outcome.

**P7v2_F2 (B5'-vs-B7 magnitude check):** Mean B5' R_diff_aged growth across the cohort must be > 20% (smoke showed 145% on one cell; full-cohort average expected 30-150% range). If mean < 20%, the B5' extraction is not delivering the smoke-implied lift across the cohort — investigate before trusting v2 results.

**P7v2_F3 (R_ohmic-dead confirmation):** B5' R_ohmic_residual |s/n| at Level 0 is expected to remain < 1 (R_ohmic insensitive to SEI/porosity by EIS physics). If |s/n| > 5, the B5' methodology is moving R_ohmic in ways that contradict the high-freq-intercept interpretation — investigate.

**P7v2_F4 (HPPC + B7 sanity reproduces):** Re-run v1's analyzer against the new parquet's B7 aged values + re-run Probe 6 against the new parquet's HPPC columns. Both must reproduce their previously-recorded Level-2 verdicts (B7: 0/3; HPPC: 0/3). Comparator stability check.

## 8. Operational protocol

1. Sign-off + commit this pre-reg as `literature/39_probe7_v2_prereg.md`. Lock anchor = commit hash.
2. Compute and record SHA-256 of `pybamm_l9_trajectories_eis_v2.parquet`, the generator script, and the analyzer script in §11 below.
3. Run `code/c3_probe7_v2_permanova.py` (to be built post-sign-off) across all 4 variants (B5'×N1, B5'×N2, fresh-state×N1, fresh-state×N2).
4. Run §7 P7v2_F4 sanity (B7 and HPPC on new parquet, confirms previously-recorded 0/3 at Level 2).
5. Apply §6 disposition + §7 falsifiers.
6. Write up `literature/40_probe7_v2_result.md`.

## 9. What this v2 does NOT establish

- Not a real-cell validation. Same gap as v1.
- Not a definitive answer on EIS deployability. Real-cell EIS noise + real-cell aging interact in ways that synthetic EIS-via-parameter-modification cannot fully capture.
- Not a closure of the C3 framework status. Even B5' STRONG only opens a path to a framework amendment; the amendment requires real-cell evidence too.
- Not a fully time-domain-cycled-state EIS. Still uses parameter-modification (now from actual cycling-read state, not user-imposed proxies). The fully cycled-state-vector EIS would require either PyBaMM API changes (`set_initial_state(solution)` support) or hand-rolled time-domain AC injection. Both are deferred.

## 10. Pre-commit checklist

- [ ] Nathan signs off on v2 spec (B5' + N1 + N2 + Probe 7.3 fresh-state secondary)
- [ ] Generator parquet `pybamm_l9_trajectories_eis_v2.parquet` exists with expected B5' and B7 columns
- [ ] B5' smoke verified (cond=0/cell=0 shows R_diff growth > 100% under B5', flat R_ohmic — done)
- [ ] Throwaway smoke files (`code/_probe7v2_*.py`) cleaned up before commit
- [ ] Pre-reg committed + pushed BEFORE running v2 PERMANOVA

## 11. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `1097b5b`
- Generator parquet SHA-256: `7A03BCC9213F5939D4CE581C3AA77289356C122D1EB1F3782FBD417A053F79AA`
- Generator script SHA-256: `59D40B4F31A8F2632F64F32436691E6E9552147514F5F254AAAF5E99E5371562` (`code/probe7v2_pybamm_b5_generator.py`)
- Analyzer script SHA-256: `18A112FF8A430349291C20EEEFB92C943542925780445E8804A3A8382DE95305` (`code/c3_probe7_v2_permanova.py`)
