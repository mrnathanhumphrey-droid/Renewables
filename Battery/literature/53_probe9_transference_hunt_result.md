# C3 Probe 9 — Transference Operator Hunt RESULT

**Status:** COMPLETE. Disposition = **TRANSFERENCE STILL NULL**.
**Date:** 2026-05-27
**Authored:** Claude
**Pre-reg:** `literature/52_probe9_transference_hunt_prereg.md` (lock `288a7f8`).
**Prior:** C3 amendment lit/47 (Transference NULL, validated scope thickness+particle radius). Probe 8 arc closed. Khan PARTIAL TRANSFER (lit/50+51).

---

## 0. One-line result

Adding a sub-mHz (1 mHz) EIS operator to the C3 amendment's 6D fresh+aged stack did **not** recover transference at L2. Transference moved from the 8c baseline F=0.67 to a best-across-PCA-k F=0.77 (PCA-2, p=0.52) — a +15% nudge that remains far below the WEAK PASS floor (F_WEAK=2.0). The 2.8× within-cell sub-mHz amplification observed in smoke did not translate into between-condition discriminating power. **EIS-based architectures are confirmed transference-blind, even with sub-mHz extension.**

## 1. Falsifier results (all locked thresholds met)

| Falsifier | Threshold | Result | Verdict |
|---|---|---|---|
| **P-Probe9_F1** (10 mHz reproduces 8c PCA-2 at L2) | dev < 1% vs th 21.24 / pr 20.87 / tn 0.67 | th 21.237 (0.016%), pr 20.871 (0.005%), tn 0.672 (0.363%) | **PASS** — v3 parquet inherits v2 cycling + 10 mHz EIS bit-clean |
| **P-Probe9_F2** (PCA-k coherence across {2,3,4}) | no verdict oscillation (PASS-NULL-PASS) | transference NULL at all three k; no oscillation | **COHERENT** — operator stable, just non-discriminating |
| **P-Probe9_F3** (no regression of th/pr) | th F ≥ 16, pr F ≥ 15.6 at L2 | th best F=19.447 (k=3), pr best F=26.920 (k=2) | **PASS** — no regression; pr IMPROVED +29% |

F1 reproduction is the strongest cross-check: the v3 extended-grid parquet reproduces the 8c amendment result to within 0.4% on the most drift-sensitive parameter (transference itself), and to 0.02% / 0.005% on thickness / particle radius. The 33-point log grid (1 mHz–100 kHz) recovers the identical 10 mHz operator values as the v2 30-point grid (0.01 Hz–100 kHz) — max|v2−v3| = 0.0 across all 9 shared columns on n=106 cells.

## 2. Full L2 PRIMARY grid (best PCA-k per design parameter)

| Design param | PCA-2 F | PCA-3 F | PCA-4 F | Best | Verdict |
|---|---|---|---|---|---|
| thickness | 15.829 | **19.447** | 16.252 | k=3 | PASS |
| transference | **0.771** | 0.022 | nan | k=2 | **NULL** |
| particle_radius | **26.920** | 19.867 | 17.326 | k=2 | PASS |

8c PCA-2 baselines at L2: th 21.24, pr 20.87, tn 0.67.

## 3. Why the smoke amplification didn't transfer

Smoke 2 (lit/52 §0.1) found R_diff transference *spread* jumps from 0.97% at 10 mHz to 2.73% at 1 mHz — a 2.8× within-cell amplification. That was a real, reproducible measurement. At population scale (this probe, n=101 clean cells) the per-channel population spread also amplifies: fresh R_diff std/mean rises 3.98% (10 mHz) → 9.49% (1 mHz).

But spread amplification ≠ between-condition separability. The transference signal at *any* EIS frequency sits in a feature direction that is (a) small relative to within-condition cell-to-cell variability (eps_amvf draws, SEI/porosity scatter), and (b) nearly collinear with the dominant thickness/particle-radius variance the cohort design injects. After z-score → PCA, the transference-bearing direction lands in the truncated tail (PC ≥ 3), and the unit-vector cosine projection then averages it away. PCA-k=3 and k=4 *retain* more variance (65.8% → 77.0% at L2) but transference F stays at 0.02 / nan — confirming the new operator does not carry an independent, retainable transference axis. **The amplified within-cell sub-mHz signal is orthogonal to the between-condition design channel.**

This is the same mechanism documented in the C3 amendment (lit/47): transference is mechanism-mediated, and its EIS fingerprint is too weak relative to direct-physics design parameters (thickness, particle radius) whose fresh-state EIS signatures dominate the variance structure.

## 4. Side finding (not the main thesis): PCA-3 helps thickness

PCA-k=3 beats PCA-2 for thickness at L2 (F 15.83 → 19.45, +23%) while PCA-2 remains best for particle radius. The third principal component carries real thickness signal that the 2-dimensional cosine projection discards. This is a small, free improvement to the C3 amendment's thickness disposition under noise, available without any new operator. **Not promoted to an amendment change here** — it is logged as a candidate refinement (would need its own pre-reg + falsifier set, since changing PCA-k retroactively across the Probe 5–8 arc is a methodology change, not a result).

## 5. Disposition (per lit/52 §5)

**TRANSFERENCE STILL NULL** — transference F at L2 < 2.0 in all PCA-k variants (0.77 / 0.02 / nan).

Per the locked disposition table: *"EIS-based architectures (even sub-mHz extension) are fundamentally transference-blind. GITT-class finite-amplitude operator is the only remaining path. Probe 10 candidate (separate pre-reg) would implement GITT-style time-domain relaxation."*

## 6. What this closes and what it opens

**Closes:**
- The sub-mHz EIS recovery path for transference. Confirmed dead at L2.
- Three EIS-operator-extension attempts now NULL on transference: 10 mHz (Probe 5–8), low-SoC EIS (Probe 9 smoke 1), sub-mHz EIS (Probe 9 main). The EIS lane is exhausted.

**Opens:**
- **Probe 10 candidate (separate pre-reg, NOT locked here):** GITT-class finite-amplitude time-domain operator. The hypothesis is that transference's signature is a *large-signal* concentration-overpotential transient that linearized small-signal EIS cannot see at any frequency. GITT applies a finite current pulse and reads the relaxation — a fundamentally different operator class.
- The PCA-3 thickness refinement (§4) as an independent candidate.

## 7. What Probe 9 does NOT establish (unchanged from pre-reg §6)

- Not a real-cell validation (Khan has no sub-mHz EIS).
- Not a transference deployment.
- Not a closure of the transference question writ large — GITT remains untested.
- No change to lit/47. The C3 amendment's validated scope (thickness + particle radius, transference NULL) stands exactly as locked.

## 8. RMD-SRC framing

In RMD-SRC terms (parent doc `D:/Resolve Research/RMD SRC Algorithm Specification.docx`): this Step 4a operator-set expansion **converged to H9-null**. The decomposition is stable (F2 COHERENT) and the validation parameters did not regress (F3 PASS), so the expansion is *clean* — it simply found that the new operator carries no transference load. Per RMD_F2, "the operator either RECOVERS transference or LEAVES IT NULL with F modestly increased (e.g., 0.67 to 1–2 but not >3)": observed 0.67 → 0.77, squarely in the "leaves it null, modest F increase" convergence regime. The operator-set expansion is decomposition-convergent, not incoherent.

Cross-substrate rule (unchanged, reinforced): the C3 amendment transfers for design parameters with **direct fresh-state EIS physics signatures** (thickness, particle radius, T_C in Khan) and fails on **aging-mechanism-mediated parameters** (transference, soc_range, charge_rate). Probe 9 confirms that broadening the EIS operator set within the linear-response regime does not move a mechanism-mediated parameter into the transferable class.

---

**Lock metadata:**
- Pre-reg lock commit: `288a7f8`
- Result commit: `<TBD — recorded in this commit>`
- Generator SHA-256: `a78d6d077c7b87edf016eb49e564abd828265f7899387d51e314d9531d217d82` (`code/probe9_pybamm_extended_eis_generator.py`)
- Analyzer SHA-256: `14c4a3c3cea50f08da0a95feee3afe6df24e07a8475fb541abf775e655183654` (`code/c3_probe9_extended_permanova.py`)
- v3 parquet SHA-256: `09c76cb21cf7a8a4065e1d0ce7d9e1a65a6c5617c561c7f19449d328616de850`
- Result parquet SHA-256: `408cd681a13674d7dd589b17cc1a6b1e4d69442635628e655c7e71b915f290c1`
- F1 reproduction parquet SHA-256: `3235764aa85670d9192c97af030f91d6a58007ca5b94e743033a85a4f68eaf7e`

## 9. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-27 | Clean-cell count 101 (not 108 or 106). | 2 cells `no post-fresh cycles` (cond4cell0, cond6cell4 — same as v2); 5 more dropped by `anchor_partial` filter (didn't reach SOH 0.92 cleanly). Identical filtering to 8c/8d on v2; per-condition n=7–12 retained. No imbalance concern (all 9 conditions populated). |
| 2026-05-27 | PCA-k=4 transference F = nan at several noise levels. | Degenerate within-group structure when k=4 retains a near-zero-variance 4th component; cosine distance collapses. Documented as expected; k=2/k=3 finite and both NULL, so disposition unaffected. |
