# C3 Probe 9 — Transference Operator Hunt Pre-Registration

**Status:** DRAFT — locks on Nathan's sign-off, before any Probe 9 PERMANOVA fires.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/52_probe9_transference_hunt_prereg.md`
**Prior:** C3 amendment lock at lit/47 (`50c851e` + `275e0cf`). Probe 8 arc closed (lit/41-49). Khan PARTIAL TRANSFER (lit/50+51). HEAD `61af1fc`.

---

## 0. Framework parentage

This is a follow-up to the C3 amendment specifically addressing the unrecovered transference signal documented at lit/47 §1 ("Validated scope: cathode thickness + cathode particle radius. Transference NULL.").

In **RMD-SRC** terms (parent at `D:/Resolve Research/RMD SRC Algorithm Specification.docx`): this is an **RMD-SRC Step 4a (categorical sub-partition / operator-set expansion)** probe. The original C3 amendment operator triad (Q_max, R_ohmic, R_diff) is structurally transference-blind across all 4 architectural choices tested in Probes 7+8. Step 4a applied to the operator dimension asks: does adding a NEW operator (sub-mHz R_diff) carry the transference signal?

If YES (TRANSFERENCE RECOVERED), the C3 amendment gets an operator-set extension (separate amendment to lit/47).
If NO (STILL NULL), it quantifies the limit of EIS-based architectures and points to GITT-class finite-amplitude operators as the only remaining recovery path.

## 0.1 Smoke evidence motivating Probe 9

Two smoke tests (2026-05-27) established:

**Smoke 1 — low-SoC EIS doesn't help.** At SoC=0.1 (where concentration polarization is large), R_diff transference spread = 0.93%, essentially identical to SoC=1.0 spread of 0.94%. Linearized EIS is SoC-insensitive for transference. Eliminates option B from consideration.

**Smoke 2 — sub-mHz EIS extension does help, modestly.** R_diff transference spread:
- 10 mHz grid (current): 0.97%
- 1 mHz grid: **2.73%** (~2.8× amplification)
- 0.1 mHz grid: 2.14% (peaks at 1 mHz, slight artifact at 0.1 mHz)

R_ohmic stays flat at any freq — pure series resistance, transference-blind by EIS physics.

The 2.73% amplification at 1 mHz is small absolute, but vs the current operator's 0.97% it's a meaningful 2.8× signal-to-baseline improvement. Empirical test needed to determine if it crosses the PERMANOVA threshold.

## 1. Hypotheses (LOCKED)

**H9-main (transference recovered):** Adding a sub-mHz operator triplet (`R_diff_1mHz_fresh`, `R_diff_1mHz_aged_b5`) to the C3 amendment's 6D fresh+aged stack, then applying the same downstream architecture (z-score → PCA → unit-vector cosine PERMANOVA), recovers transference at Level 2 N1 noise: transference verdict = PASS or WEAK PASS (vs lit/40 v2 PRIMARY F=0.67 NULL).

**H9-null:** Transference remains NULL at L2 even with sub-mHz operators added. Confirms EIS-based architectures are fundamentally transference-blind; recovery requires GITT-class finite-amplitude operators (Probe 10 candidate, not in this lock).

**H9-secondary-1 (no regression on th + pr):** Adding sub-mHz operators does not DEGRADE thickness or particle_radius dispositions at L2 below 8c PCA-2 baseline (th F=21.24, pr F=20.87). Documented in §5 falsifier P-Probe9_F3.

**H9-secondary-2 (PCA dimensionality choice):** Three PCA dimensionalities tested on the new 8D stack: k=2 (lossy compression — risks dropping the new transference dimension), k=3 (preserves the proposed transference axis), k=4 (preserves more, may dilute). Headline = whichever PCA-k achieves highest transference F at L2 (or PCA-2 if none differ substantially).

## 2. Cohort + data (LOCKED)

- **Cohort:** Same 108-cell PyBaMM L9 cohort. Same B5' methodology for aged-state EIS (cycling-read SEI + porosity baked into ParameterValues).
- **New observable per cell:** R_diff_1mHz at both fresh and aged states, computed as Re[Z(0.001 Hz)] − R_ohmic from a PyBaMM EISSimulation on a 33-point log-spaced grid from 1 mHz to 100 kHz.
- **R_ohmic:** unchanged. Re[Z(100 kHz)] from the same EIS solve. (Verified flat at all transference levels, so a single shared value is fine.)
- **R_diff:** unchanged. Re[Z(0.01 Hz)] − R_ohmic (the existing 10 mHz operator). Preserved alongside the new 1 mHz operator for direct comparison.
- **Q_max:** unchanged. From cycling sim.
- **Generator parquet:** new output at `data/processed/pybamm_l9_trajectories_eis_v3.parquet`. Existing v2 parquet preserved.

## 3. Architecture (LOCKED — extends C3 amendment lit/47)

Per cell c at the uniform-anchor cycle (closest cycle to SOH 0.92):

1. **Build extended 8D fresh+aged feature vector:**
   x_c = (fresh_Q, fresh_R_ohmic, fresh_R_diff_10mHz, fresh_R_diff_1mHz,
          aged_Q, aged_R_ohmic, aged_R_diff_10mHz, aged_R_diff_1mHz)
   ∈ ℝ⁸

2. **Center + z-score by pooled cohort SD:** z_c = (x_c − x̄) / σ_pooled

3. **PCA decompose, retain k components** (k ∈ {2, 3, 4} tested):
   z_c^(PCAk) = z_c · components[:, :k]

4. **Project to unit vector on the k-sphere:** u_c = z_c^(PCAk) / ‖z_c^(PCAk)‖₂

5. **Cosine PERMANOVA per design parameter** (10K perms, Bonferroni α/3 = 0.0167, PASS thresholds same as Probe 5/6/7/8).

Run for all three PCA-k values × all three design parameters × all five N1 noise levels.

Headline = transference verdict at L2 for the PCA-k that maximizes transference F.

## 4. Falsifiers — RMD-SRC F1–F4 inheritance (LOCKED)

**P-Probe9_F1 ↔ RMD_F1 (initial cleanness reproduction):** PCA-2 on the v3 parquet with the 10 mHz operators ONLY (drop the new 1 mHz columns from the feature stack) must reproduce 8c PCA-2 result bit-identically at L2 (th F=21.24, pr F=20.87, tn NULL F=0.67). Validates the v3 parquet inherits v2's cycling outputs cleanly. INVALID otherwise.

**P-Probe9_F2 ↔ RMD_F2 (decomposition convergence):** This probe is an operator-set expansion (RMD-SRC Step 4a). Convergence here means: adding the new operator either RECOVERS transference (PASS H9-main) or LEAVES IT NULL with the F-value modestly increased (e.g., F goes from 0.67 to 1-2 but not >3). If transference verdict swings RANDOMLY across the three PCA-k choices (PASS at k=2, NULL at k=3, PASS at k=4 — non-monotonic), the operator is unstable; document as INCOHERENT.

**P-Probe9_F3 ↔ RMD_F3 (validation agreement / no regression):** Adding the new operators must NOT degrade th + pr at L2 below 8c baseline by more than 25% in F. If th F drops below 16 or pr F drops below 15.6 at L2, the new operators are diluting the design signal — documented as a §A concern even if transference passes.

**P-Probe9_F4 ↔ RMD_F4 (predictive transfer):** N/A in this synthetic-only probe. If H9-main passes, P-Khan_F4-style holdout test on a Khan re-run (separate probe) becomes the gating step before any operator-set extension to the amendment.

## 5. Disposition criteria (LOCKED)

| Outcome | Verdict |
|---|---|
| **TRANSFERENCE RECOVERED** | Transference PASS or WEAK PASS at L2 in at least one PCA-k variant AND th + pr both still PASS at L2 (no regression per P-Probe9_F3) | Sub-mHz EIS operator carries transference signal that linearized 10 mHz EIS misses. Path opens to a separate amendment extension to lit/47. Khan retest with sub-mHz EIS would be the next step (if Khan has sub-mHz EIS data; otherwise gated on data acquisition). |
| **TRANSFERENCE PARTIAL** | Transference F at L2 > 2.0 in best PCA-k variant but p ≥ 0.05 (WEAK PASS threshold barely missed) | Operator carries signal but at sub-threshold magnitude. Cohort scale-up (lit/47 §5.3) becomes the next step to test whether more cells push the F above threshold. |
| **TRANSFERENCE STILL NULL** | Transference F at L2 < 2.0 in all PCA-k variants | EIS-based architectures (even sub-mHz extension) are fundamentally transference-blind. GITT-class finite-amplitude operator is the only remaining path. Probe 10 candidate (separate pre-reg) would implement GITT-style time-domain relaxation. |
| **PROBE 9 INVALID** | P-Probe9_F1 fails (10 mHz reproduction ≠ 8c) OR P-Probe9_F3 fires (th or pr regresses substantially) | Pipeline issue or operator addition is destabilizing. Debug + re-run. |

## 6. What Probe 9 does NOT establish

- Not a real-cell validation. Khan doesn't have sub-mHz EIS at the cell level (Khan EIS spans roughly 10 mHz to 10 kHz typical academic range).
- Not a transference operator deployment. Even TRANSFERENCE RECOVERED requires sub-mHz EIS instrument capability in any deployment — not standard academic hardware.
- Not a closure of the transference question. GITT-class operators remain the alternative if Probe 9 fails.
- Not an amendment update to lit/47. TRANSFERENCE RECOVERED would trigger a separate amendment-extension document, not modify lit/47 in place.

## 7. Operational protocol

1. Sign-off + commit this pre-reg as `literature/52_probe9_transference_hunt_prereg.md`. Lock anchor = commit hash.
2. Build `code/probe9_pybamm_extended_eis_generator.py` — extends `probe7v2_pybamm_b5_generator.py` with sub-mHz EIS solves at fresh + aged states. Output: `data/processed/pybamm_l9_trajectories_eis_v3.parquet`.
3. Smoke 1-cell run.
4. Full 108-cell production (~80-120s wall expected).
5. Build `code/c3_probe9_extended_permanova.py` — analyzer with three PCA-k variants on the 8D feature space.
6. Run analyzer. Output: `data/processed/probe9_transference_results.parquet`.
7. Apply §5 disposition + §4 falsifiers.
8. Write up `literature/53_probe9_transference_hunt_result.md`.

**Cost:** ~120s gen + ~10 min analyzer wall. No Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `288a7f8`
- Generator script SHA-256: `a78d6d077c7b87edf016eb49e564abd828265f7899387d51e314d9531d217d82`
- Analyzer script SHA-256: `14c4a3c3cea50f08da0a95feee3afe6df24e07a8475fb541abf775e655183654`
- Result parquet SHA-256: `408cd681a13674d7dd589b17cc1a6b1e4d69442635628e655c7e71b915f290c1`
- Result writeup: `literature/53_probe9_transference_hunt_result.md` — disposition TRANSFERENCE STILL NULL
