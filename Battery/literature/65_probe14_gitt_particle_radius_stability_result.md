# C3 Probe 14 — GITT Superior Particle-Radius Operator RESULT

**Status:** COMPLETE. Disposition = **GITT-PR-SUPERIOR (robust)** — the GITT particle-radius advantage over EIS survives the 9b multi-seed stability gate emphatically. **The first promotable POSITIVE finding in the battery probe sequence**, and a demonstration that the same gate which killed the 9b PCA-3 finding and the SOH drop-ohmic hint *confirms* a real signal.
**Date:** 2026-05-29
**Authored:** Claude
**Pre-reg:** `literature/64_probe14_gitt_particle_radius_stability_prereg.md` (lock `7fd0e44`).
**Prior:** Probe 10 (lit/57 §8) logged GITT pr F=72 vs EIS 27 as an unpromoted side finding requiring its own multi-seed gate.

---

## 0. One-line result

On the common clean cohort (EIS∩GITT = **101 cells**), with the deterministic anchors reproduced exactly (GITT 8D PCA-2 pr F = **71.564** vs known 71.56; EIS = **26.920** vs known 26.92), the multi-seed stability gate (N=200 independent random noise seeds) **passes on every locked criterion**: GITT pr discrimination is robust (L2 median **71.28**, 95% band **[67.6, 74.5]**, stable L0→L4), intrinsically ≥2× EIS (L0 ratio **2.38×**), and the realistic-noise distributions **do not overlap** (GITT 2.5th-pct 67.63 ≫ EIS 97.5th-pct 35.98). **Disposition: GITT-PR-SUPERIOR (robust).** The contrast is itself instructive — EIS's pr F is *wide and noise-fragile* (L2 [18.2, 36.0], L4 [8.4, 25.0]), exactly the single-realization fragility the 9b gate guards against, while GITT's is tight because its realistic noise (cycler voltage ~0.5%) is far smaller than EIS impedance noise (~15–20%). The gate confirms the GITT operator rather than washing it out.

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **anchor** (sanity, not a claim) | reproduce 71.56 / 26.92 | **71.564 / 26.920** | reproduced ✓ |
| **F1** positive control (L0) | both pr F > 3.0 | GITT 72.08, EIS 30.29 | **PASS** |
| **F2** PCA-k coherence | GITT pr PASS at k∈{2,3,4} @L2 | all PASS (k=2/3/4 ≈ 71/66/65) | **PASS** |
| **H14-main** robust pr (GITT 8D k=2) | L2 median>3 AND 2.5pct>3; stable L0–L4 | median **71.28**, 2.5pct **67.63**; L0–L4 medians 69–72 | **PASS** |
| **H14-sec(i)** intrinsic (L0) | GITT/EIS ≥ 2× | **2.38×** (72.08/30.29) | **PASS** |
| **H14-sec(ii)** realistic (L2) | GITT 2.5pct > EIS 97.5pct | **67.63 > 35.98** (non-overlap) | **PASS** |

## 2. The multi-seed distributions (GITT 8D PCA-2 vs EIS 8D PCA-2, common cohort)

| level | GITT pr F median [2.5, 97.5] | EIS pr F median [2.5, 97.5] |
|---|---|---|
| L0 (clean) | 72.08 (single) | 30.29 (single) |
| L1 | 71.91 [70.10, 73.72] | 28.12 [21.21, 35.58] |
| **L2 PRIMARY** | **71.28 [67.63, 74.52]** | **25.77 [18.24, 35.98]** |
| L3 | 70.28 [64.90, 75.37] | 22.36 [14.98, 34.04] |
| L4 | 69.32 [62.42, 77.12] | 15.29 [8.41, 25.01] |

The bands never overlap at any level — GITT's *worst* draw exceeds EIS's *best* draw throughout. GITT's band is narrow (≈±5% at L2) because its locked realistic noise is tight (cycler voltage precision); EIS's is wide (≈±35% at L2) because impedance R-noise is large. At L4 EIS degrades toward the floor (median 15.3, low tail 8.4) while GITT stays ~69 — the finite-amplitude operator is both stronger and far more noise-robust for particle radius.

## 3. Why this is the 9b lesson working in the *positive* direction

The 9b finding (lit/55) and the SOH drop-ohmic hint (Probes 11–13) were *single-realization advantages that evaporated under resampling*. The same gate is applied here, and the GITT pr finding **passes** — median essentially equal to the deterministic anchor (71.28 vs 71.56) with a tight CI. The gate is not a null-maker; it is a discriminator. It rejected the fragile claims and confirms the robust one. The EIS pr distribution's width (a CV of ~17% at L2) is the concrete illustration: had the program promoted *EIS* pr from a single seed, that value (26.92) sits inside a [18, 36] band — exactly the kind of estimate the gate is designed to distrust. GITT's [67.6, 74.5] is not.

## 4. Mechanism

GITT's concentration-overpotential (`eta_conc`) and slow-relaxation tail (`dV_slow`) scale with solid-state diffusion length, which scales directly with particle radius; EIS's Warburg-region `R_diff` encodes the same physics only indirectly and at the noisy low-frequency end. The 8D GITT stack (adding `dV_slow`) beats the 6D consistently (L2 8D≈71 vs 6D≈50, from the distribution table in the results parquet), confirming the slow-relaxation channel carries independent particle-radius information. The result is physically expected; the contribution here is that it is now **robustly established**, not asserted from one noise draw.

## 5. Disposition (per lit/64 §5)

**GITT-PR-SUPERIOR (robust).** F1 PASS, F2 coherent, H14-main PASS (robust + stable), H14-secondary PASS on both arms (intrinsic 2.38×; realistic non-overlap). The Probe 10 §8 side finding is **promoted**: where a finite-amplitude (GITT-class) measurement is available, the GITT 8D stack is the robustly superior particle-radius operator versus the EIS triad.

## 6. What this establishes / does not

**Establishes:**
- The GITT > EIS particle-radius advantage is **robust to noise reseeding** (not a single-realization artifact) — it survives the mandatory 9b gate that killed comparable single-seed findings.
- A rare *positive* promotion in a program dominated by honest nulls/terminus, validating that the stability discipline discriminates real signals from fragile ones rather than only rejecting.
- Operator-selection guidance: prefer the GITT 8D stack for particle-radius discrimination when a finite-amplitude measurement exists.

**Does NOT establish:**
- Anything on real cells — synthetic L9 PyBaMM cohort only (no GITT-capable real-cell cohort in the corpus; this is the obvious next acquisition target if pr-on-real-cells is wanted).
- Any change to the locked lit/47 amendment *scope* (thickness + particle radius PASS, transference NULL stands) — this updates *which operator* is best for pr, not the amendment's validated parameter set.
- Anything about transference (that arc is closed) — this is strictly the pr positive control, promoted.

## 7. RMD-SRC framing

A validation-agreement (RMD_F3) promotion of a positive finding, gated by the multi-seed stability check. The operator class is validated as informative (F1), the geometry is coherent (F2), and the advantage is robust and dominant under resampling (H14-main + secondary). This is the cleanest possible *positive*: a physically-motivated finite-amplitude operator that robustly out-discriminates the small-signal alternative for the parameter whose signature it most directly encodes — established to the same evidentiary bar that the program used to reject its fragile findings.

---

**Lock metadata:**
- Pre-reg lock commit: `7fd0e44`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `06e4c54d3e060bbd457c85cb54a66f4ef24b9150b0d50cd5659cfc410364de7b`
- Result parquet SHA-256: `4002412e258c3c565152d85e9f17f313b756190ee8b9a087369e8265b82a275e`
- Reused GITT parquet SHA-256: `0851ff9fc39689131e5673e61cc3ef1f1b628c74ae1db7271bebf6d81ec9619e` (unchanged)
- Reused EIS v3 parquet SHA-256: `09c76cb21cf7a8a4065e1d0ce7d9e1a65a6c5617c561c7f19449d328616de850` (unchanged)

## 8. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-29 | Console `§`/`∩` glyphs replaced with ASCII in analyzer prints. | Windows cp1252 console can't encode them; cosmetic only, no effect on computation or results. |
