# C3 Probe 14 — GITT Superior Particle-Radius Operator: Multi-Seed Stability Promotion Pre-Registration

**Status:** LOCKED 2026-05-29 at commit `7fd0e44`. No Probe 14 analysis had fired at lock time. **Integrity disclosure (§0.3):** the GITT pr F=71.56 (L2) and EIS pr F=26.92 (L2) single-realization values are ALREADY KNOWN (Probe 10 lit/57 §3/§8). They are *anchors to be stress-tested*, NOT claims — the pre-registered tests below are the multi-seed robustness questions that have not been run.
**Date drafted:** 2026-05-29
**Authored:** Claude
**Repo target on lock:** `Battery/literature/64_probe14_gitt_particle_radius_stability_prereg.md`
**Prior:** Probe 10 (lit/56+57) closed the transference arc and logged a side finding (§8): GITT operators discriminate particle radius (pr) far more strongly than EIS (F=72 vs 27), "would need its own pre-reg to promote … same multi-seed stability gate [as Probe 9b, which washed out]." This probe is that promotion attempt. HEAD `5d218e1`.

## 0. Motivation — is the GITT particle-radius advantage robust, or a single-realization artifact?

Across the program, GITT's finite-amplitude concentration-polarization operators (`eta_conc`, `dV_slow`) separated particle radius at F≈72 vs EIS's Warburg-region `R_diff` at F≈27 — physically sensible (concentration polarization magnitude scales with solid-diffusion length ∝ particle radius). But every F in Probes 9/10 was computed on **one deterministic noise realization** (the per-cell seed scheme in `apply_vnoise`/`apply_noise_8d`). The **9b lesson** ([[feedback_diagnostic_driven_amendments]], lit/55) is exactly that a single-realization advantage can evaporate under resampling (+3.62 → +1.24±4.88). Probe 14 applies that gate before any promotion: **does GITT's pr discrimination — and its superiority over EIS — survive multi-seed noise resampling?**

In **RMD-SRC** terms: a validation-agreement (RMD_F3) promotion of a *positive* finding (rare — most probes have been nulls), gated by the mandatory multi-seed stability check.

## 0.1 Physical hypothesis

GITT's `eta_conc` (concentration overpotential) and `dV_slow` (slow relaxation tail) encode solid-state diffusion length directly; EIS's `R_diff` encodes it indirectly through the Warburg region. GITT also has tighter realistic noise (cycler voltage precision ~0.25–2%) than EIS impedance (R-noise ~5–50%). **Prediction:** GITT pr discrimination is both intrinsically stronger (noise-free) and more robust (under realistic noise) than EIS.

## 0.2 Feasibility (verified read-only before drafting)

Both source parquets present: `pybamm_l9_trajectories_gitt_v1.parquet` (GITT, SHA `0851ff9f…`) + `pybamm_l9_trajectories_eis_v3.parquet` (EIS, SHA in lit/53). The existing `probe10_transference_results.parquet` shows GITT 8D PCA-2 pr F is **flat across the deterministic noise grid**: L0 72.08 / L1 72.18 / L2 71.56 / L3 68.78 / L4 66.34, and k-coherent (k=2/3/4 = 72.1/65.4/64.3 at L0). EIS pr 8D best L2 = 26.92 (Probe 9, lit/57 §3). Shared PERMANOVA core (`build_pca`/`cosine_dist`/`permanova_pseudoF`) is identical across both analyzers.

## 0.3 Integrity disclosure — what is already known (NOT re-claimable)

| quantity | known value | status |
|---|---|---|
| GITT 8D PCA-2 pr F @ L2 (1 deterministic realization) | **71.56** | anchor, to be stress-tested |
| EIS 8D PCA-2 pr F @ L2 (1 deterministic realization) | **26.92** | anchor, to be stress-tested |
| GITT pr F flat across L0–L4 (deterministic grid) | 72→66 | known (one seed per level) |

Probe 14 does **not** re-assert "GITT pr F≈72." It pre-registers whether that value (and its margin over EIS) is **robust to independent random noise reseeding** — a quantity not yet computed (the existing grid is one deterministic realization per level).

## 1. Hypotheses (LOCKED)

**H14-main (robust pr discrimination):** GITT (8D stack, PCA-2 — the canonical lit/47 amendment geometry) discriminates particle radius **robustly**: across **N=200 independent random noise-injection seeds** at L2 PRIMARY, the pr PERMANOVA F has **median > F_FLOOR=3.0 AND 2.5th-percentile > F_FLOOR**, i.e. verdict PASS is stable, not a single-realization accident. Reported at all levels L0–L4 (L0 = single clean F, no noise to reseed).

**H14-secondary (superior to EIS) — two pre-committed parts:**
- (i) **intrinsic (noise-free, L0):** GITT pr F(L0) ≥ **2×** EIS pr F(L0) — operator quality independent of noise magnitude.
- (ii) **realistic (each modality at its own locked L2, N=200 seeds):** the GITT pr F distribution **strictly dominates** EIS's — GITT 2.5th-pct > EIS 97.5th-pct (non-overlapping 95% intervals).

**H14-null:** GITT pr discrimination is not robust (median/CI fails F_FLOOR) AND/OR the superiority over EIS does not survive resampling (overlapping CIs, or intrinsic margin <2×). Would mean the F=72-vs-27 side finding was a single-realization artifact — same washout as 9b — and pr should NOT be promoted to the GITT stack.

## 2. Cohort + data (LOCKED)

- **Source:** the two parquets above, reused unchanged.
- **Common clean cohort (locked):** the **intersection** of the Probe 9 EIS-clean cells (`build_clean_table`, EIS) and the Probe 10 GITT-clean cells (`build_clean_table`, GITT) — so GITT and EIS pr F are computed on the **same physical cells**, removing cohort-composition as a confound in the comparison. Final N + per-condition counts recorded in the analysis output.
- **Labels:** `particle_radius_level` (the L9 Taguchi design levels). thickness reported as a secondary positive control only.
- **Independent unit:** synthetic L9 cell (this is a synthetic-cohort robustness probe; no real-cell claim).

## 3. Method (LOCKED — shared C3 core, identical to Probe 9/10)

- **Pipeline:** z-score → PCA-k → unit-vector → cosine PERMANOVA pseudo-F (`build_pca`/`cosine_dist`/`permanova_pseudoF` reused verbatim).
- **Feature stacks:** GITT 8D = {fresh,aged}×{Q, eta_inst, eta_conc} + {fresh,aged}_dV_slow (primary); GITT 6D = without dV_slow (secondary). EIS 8D = {fresh,aged}×{Q, R_ohmic, R_diff_10mHz, R_diff_1mHz}.
- **Geometry:** **PCA-2 primary** (canonical amendment); k∈{2,3,4} reported for F2 coherence.
- **Noise:** the locked per-modality grids (GITT voltage 0/0.25/0.5/1/2%; EIS Q/Ro/Rd grid from Probe 9). **Multi-seed change:** replace the deterministic per-cell seed with **N=200 independent random seeds** (seed = iteration index), re-injecting noise each iteration. Per seed compute pr F_obs (deterministic given the noised matrix). Permutation p computed once on the deterministic-anchor realization per level (reproduces the 71.56/26.92 anchors as a sanity check); F-distribution is the stability object.
- **Metrics:** per level, the pr F distribution (median, 2.5/97.5 pct, min, max) for GITT and EIS; the per-seed paired GITT−EIS margin.

## 4. Falsifiers (LOCKED)

**P-Probe14_F1 (positive control / extraction intact):** pr separates at L0 for both modalities (F > F_FLOOR). Fail → cohort/extraction broken → INVALID (not "fragile").

**P-Probe14_F2 (PCA-k coherence):** GITT pr verdict must not oscillate across k∈{2,3,4} (the F=72/65/64 pattern should stay PASS at all k). Oscillation → geometry-fragile, flagged.

**P-Probe14_F3 (THE stability gate — distribution, not single seed):** H14-main and H14-secondary are judged ONLY on the N=200-seed distributions, NEVER on the known single-realization 71.56/26.92. If the deterministic anchor is high but the resampled median/CI fails, that is the **9b washout** and H14 FAILS. (This is the whole point of the probe.)

**P-Probe14_F4 (fair comparison):** GITT and EIS pr F computed on the **same common clean cohort**, same PCA-2 geometry, same N seeds, each at its **own** locked L2 (not noise-matched — that is the realistic comparison; a noise-matched L0 sensitivity is the intrinsic arm H14-sec-i). No cross-modality mixing of cohort or geometry.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **GITT-PR-SUPERIOR (robust)** | H14-main PASS (median+2.5pct > F_FLOOR at L2, stable L0–L4) AND H14-sec (i) intrinsic ≥2× AND (ii) realistic CI non-overlap | Promote: GITT 8D is the robustly-better particle-radius operator. The side finding survives the 9b gate. Updates the amendment's pr recommendation toward GITT where a finite-amplitude signal is available. |
| **GITT-PR-ROBUST-NOT-SUPERIOR** | H14-main PASS but H14-sec fails (intrinsic <2× OR CIs overlap) | pr is robustly readable by GITT, but the "2.7× better than EIS" margin washes out under resampling — exactly the 9b failure mode for a comparative claim. Do NOT promote the superiority claim. |
| **GITT-PR-FRAGILE** | H14-main FAIL (resampled median/CI < F_FLOOR) | The pr discrimination itself is a single-realization artifact. (Unlikely given the tight GITT noise, but the gate must allow it.) |
| **PROBE 14 INVALID** | F1 fails (pr doesn't separate at L0) | Cohort/extraction broken. Debug. |

## 6. What Probe 14 does NOT establish

- Not a real-cell result — synthetic L9 PyBaMM cohort only (no GITT-capable real-cell cohort in the corpus).
- Not a transference result (that arc is closed; this is strictly the pr positive control promoted).
- A SUPERIOR verdict updates the *operator-selection guidance* (use GITT for pr when a finite-amplitude measurement exists), not the locked lit/47 amendment scope.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock anchor = commit hash). **Push.**
2. Build `code/c3_probe14_gitt_pr_stability.py` — reuse Probe 9/10 clean-table builders + noise injectors + shared PERMANOVA core; loop N=200 random seeds per level for GITT 8D/6D + EIS 8D on the common cohort; emit distributions + the deterministic-anchor reproduction.
3. Run. Output `data/processed/probe14_gitt_pr_stability_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/65_probe14_..._result.md`. Commit + push + lock hashes.

**Cost:** analysis-only on existing parquets; 200 seeds × 5 levels × 2 modalities × cheap F_obs (no per-seed permutation loop). Seconds–minutes. No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `7fd0e44`
- Analyzer SHA-256: `06e4c54d3e060bbd457c85cb54a66f4ef24b9150b0d50cd5659cfc410364de7b`
- Result parquet SHA-256: `4002412e258c3c565152d85e9f17f313b756190ee8b9a087369e8265b82a275e`
- Reused GITT parquet SHA-256: `0851ff9fc39689131e5673e61cc3ef1f1b628c74ae1db7271bebf6d81ec9619e` (Probe 10, unchanged)
- Reused EIS v3 parquet SHA-256: `09c76cb21cf7a8a4065e1d0ce7d9e1a65a6c5617c561c7f19449d328616de850` (Probe 9, unchanged)
- Result writeup: `literature/65_probe14_gitt_particle_radius_stability_result.md` — disposition GITT-PR-SUPERIOR (robust)
