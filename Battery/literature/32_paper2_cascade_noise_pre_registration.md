# Paper 2 — Cascade Noise-Injection Pre-Registration (Probe-6-Analog)

**Date locked:** 2026-05-22
**Locked before:** any noise-injection analysis is run on the trained cascade.
**Companion pre-regs:** literature/25 (Probe 6 noise model, commit `4a3e932`), literature/28 (selection + cascade, commit `7fae62a` + amendments), literature/30 (Gate I amendment, commit `3ad6c5c`), literature/31 (amended-protocol cascade result, commit `d3b1662`).

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. Motivation

literature/31 reported amended-cascade PRIMARY validation F = 57.26, p = 0.0001 on PyBaMM-holdout (n=36). literature/31 §7 Caveat 4 flagged that **the cascade was trained on noise-free synthetic, and Probe 6 (literature/26) established that the trajectory operators T1-T5 collapse at typical academic noise levels (0.5% Q / 15% R_DC / 20% R_total)**. Since 4 of 5 dominant cascade operators are trajectory operators, the F = 57.26 may be inflated by the noise-free training and noise-free holdout.

This probe tests **whether the trained cascade's PRIMARY F survives Probe 6's locked noise levels when noise is injected into the PyBaMM-holdout trajectories before operator re-extraction**.

If the cascade survives Level 2 (typical academic noise) → headline upgrades from "PARTIAL REPLICATION within-substrate" to "PARTIAL REPLICATION + noise-robust within-substrate."

If the cascade collapses at Level 2 → confirms Caveat 4: the 7-operator framework as currently defined is brittle to realistic instrumentation noise. The PARTIAL REPLICATION verdict from literature/31 is preserved but qualified.

## 1. Hypotheses

**H8-primary:** At Probe 6's Level 2 noise (σ_Q=0.005, σ_R_DC=0.15, σ_R_total=0.20), the PRIMARY PyBaMM-holdout PERMANOVA pseudo-F drops below 3.0 OR permutation p rises above 0.05. The cascade collapses to NULL or near-NULL under typical academic noise.

**H8-null:** At Level 2 noise, PRIMARY F > 3.0 AND p < 0.05. The cascade survives realistic noise.

**H8-secondary (calibration curve):** Run the PRIMARY PERMANOVA at all 5 Probe-6 noise levels {0, 1, 2, 3, 4} and report the F-vs-noise-level curve descriptively.

## 2. Data source (LOCKED)

`data/processed/pybamm_l9_trajectories.parquet` — same parquet as Probe 6 (commit `4a3e932` source). 108 PyBaMM cells from Probe 5 (uniform 0.92 SOH anchor). The 36 PyBaMM-holdout cells per literature/28 §2 deterministic seed split are a subset.

No new PyBaMM simulations. Re-extraction with noise on existing trajectories.

## 3. Noise model (LOCKED — inherited verbatim from literature/25 §3)

Multiplicative Gaussian noise per cycle on Q, R_DC, R_total:

| Level | σ_Q | σ_R_DC | σ_R_total | Interpretation |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | Baseline (noise-free, = literature/31 PRIMARY) |
| 1 | 0.001 | 0.05 | 0.10 | Best-in-class lab cycler |
| 2 | **0.005** | **0.15** | **0.20** | **Typical academic-lab noise (PRIMARY test point)** |
| 3 | 0.010 | 0.30 | 0.30 | Noisy field-cycler |
| 4 | 0.020 | 0.50 | 0.50 | Instrument-issue / sparse-RPT |

Per-cycle independent Gaussian noise (multiplicative). Random seed per-cell, per-noise-level: `seed = 5000 + level*10000 + cond_idx*100 + cell_idx`. New seed offset (5000) so noise realizations are independent from Probe 6's seed (2000).

Noise is applied at the **per-cycle measurement level**, then the 7 amended-cascade-surviving operators (T1, T2, T3, T4, T5, C1, C2) are re-extracted from the noisified trajectories using the same extraction logic as `paper2_extract_others.py`. The cascade trained at commit `d3b1662` is NOT re-trained. The noisy operator values feed the existing cascade unchanged.

## 4. Primary test (LOCKED)

Per noise level, re-extract the 7 operators on all 36 PyBaMM-holdout cells. Standardize using the SAME fit-on-train scaler from literature/31 cascade (no peeking — the holdout was already standardized using train scaler in literature/31). Apply the trained RF cascade. Compute leaf-indices matrix. Project via the SAME PCA fit on training+original-holdout leaves used in literature/31 (also no peeking).

PERMANOVA on the PCA embedding labeled by L9 cond_idx (9 classes, 4 cells per class). 10,000 permutations, Euclidean distance on the PCA embedding (matches literature/31).

**PASS criterion at Level 2 (primary test point):** pseudo-F > 3.0 AND permutation p < 0.05.

**Bonferroni:** single primary test (Level 2). α = 0.05. The other 4 noise levels are descriptive calibration points, no Bonferroni penalty.

## 5. Falsification thresholds (LOCKED)

**Level-2 verdicts:**

- **CASCADE NOISE-ROBUST:** Level 2 F > 3.0 AND p < 0.05. Headline upgrades to "PARTIAL REPLICATION + noise-robust at typical academic noise."
- **CASCADE NOISE-WEAK:** Level 2 F < 3.0 OR p > 0.05 BUT Level 1 still passes. Cascade survives best-in-class lab noise but collapses at academic noise.
- **CASCADE NOISE-FRAGILE:** Level 1 (best-in-class) collapses. Cascade is brittle to even high-end instrumentation noise.
- **CASCADE INVALID:** trajectory parquet missing or contains <30 holdout cells.

**Cross-level expected pattern (NOT a verdict, exploratory):** F monotone decreasing as noise level increases. A non-monotone curve is a methodological concern (suggests noise-injection bug or chance variation).

## 6. What this probe CAN and CANNOT conclude

CAN:
- Identify whether the literature/31 PRIMARY F survives realistic noise
- Calibrate the cascade's noise-tolerance curve
- Confirm or refute Caveat 4 from literature/31

CANNOT:
- Validate against real-cell noise on Khan or Severson (those weren't in the holdout)
- Quantify chemistry-heterogeneity or calendar-variation contributions
- Conclude anything about cross-substrate noise transfer (the WMG SECONDARY is handled separately at literature/33)

## 7. Operational protocol (LOCKED execution order)

1. Commit + push this pre-reg AND literature/33 (WMG broadening). **Lock = commit timestamp before any code change.**
2. Implement `code/paper2_cascade_v2_noise.py`:
   - Load `pybamm_l9_trajectories.parquet` and `paper2_cascade_v2_summary.pkl` (trained cascade artifacts)
   - Filter to PyBaMM-holdout 36 cells (deterministic seed split per literature/28 §2)
   - For each of 5 noise levels, inject Gaussian noise per §3, re-extract 7 operators, standardize via training scaler, score through cascade, project via PCA, run PERMANOVA
   - Output: `paper2_cascade_v2_noise_results.parquet` with (level, F, p, df_between, df_within)
3. Apply §5 verdict at Level 2.
4. Write up in `literature/34_paper2_cascade_noise_result.md`.

## 8. Explicitly NOT covered

- Re-training the cascade on noisified training data — locked OUT; this probe tests the ALREADY-TRAINED cascade's robustness
- Adversarial noise patterns beyond Gaussian — out of scope
- Variable per-cycle noise levels within a single cell — out of scope (constant σ per level)
- Operator-level (rather than measurement-level) noise injection — locked OUT, measurement-level mirrors real cells

## 9. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
