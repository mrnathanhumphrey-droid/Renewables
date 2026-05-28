# C3 Probe 9b — PCA Component Decomposition RESULT

**Status:** COMPLETE. Disposition = **MECHANISM REAL BUT UNSTABLE**.
**Date:** 2026-05-27
**Authored:** Claude
**Pre-reg:** `literature/54_probe9b_pca_component_decomposition_prereg.md` (lock `d9dcdf6`).
**Prior:** Probe 9 CLOSED (lit/52+53). This investigates Probe 9's side finding only; lit/47 C3 amendment unchanged.

---

## 0. One-line result

The geometric mechanism is **real and exactly as hypothesized** — adding the 1 mHz diffusion operator demotes thickness's R_ohmic carrier from PC2 (6D) to PC3 (8D), and at the single Probe-9 noise seed that gives thickness a +3.62 F gain from including PC3. **But the gain does not survive resampling:** across 200 independent L2 noise seeds, Δ_th = F_th(k=3) − F_th(k=2) = **+1.24 ± 4.88, 95% CI [−8.07, +9.90]**, with only 58.5% of seeds favoring k=3. The single-seed advantage was a favorable draw. **Do not pursue adaptive-k; the 8c PCA-2 amendment stands.**

## 1. Falsifier results

| Falsifier | Threshold | Result | Verdict |
|---|---|---|---|
| **P-Probe9b_F1** (reproduces Probe 9 L2 k=2/k=3) | abs dev < 0.01 F | all 6 values dev < 5e-4 (th 15.829, pr 26.920, tn 0.771 @k2; th 19.447, pr 19.867, tn 0.022 @k3) | **PASS** — pipeline bit-identical |
| **P-Probe9b_F2** (loadings ↔ localization agree) | no conflict | loadings say R_ohmic→PC3 AND ΔF_th(PC3)>0 — both point same way | **COHERENT** |
| **P-Probe9b_F3** (pr neg-control stays k=2 across seeds) | Δ_pr 95% > 0 | Δ_pr mean +4.14 but 95% CI [−0.81, +9.79] | **FAILS strict bar** (see §4) |

## 2. (A) Loadings — the mechanism is confirmed at the single seed

8D stack at L2, mean |loading| of the channel groups (full matrix in `probe9b_loadings.parquet`):

| channel group | PC1 | PC2 | PC3 |
|---|---|---|---|
| R_ohmic (idx 1,5) | 0.269 | 0.292 | **0.536** |
| R_diff (idx 2,3,6,7) | 0.206 | **0.397** | 0.190 |

R_ohmic loads **heaviest on PC3** (0.536 vs 0.269/0.292). R_diff dominates PC1–2. **H9b-main HOLDS.**

6D stack at L2 (no 1 mHz), R_ohmic mean |loading|: PC1 0.295, **PC2 0.582**, PC3 0.246. In the un-augmented amendment space R_ohmic lives in PC1–2. **H9b-causation HOLDS** — adding the two 1 mHz columns is what pushed R_ohmic down to PC3. The diffusion-operator addition rotated the top-2 eigenvectors toward the diffusion (particle-radius) axis exactly as predicted.

## 3. (B) Marginal-gain — localization confirmed at the single seed

L2 cumulative-k cosine-PERMANOVA F (k=1 degenerate in the unit-vector metric, excluded):

| design param | F(k=2) | F(k=3) | F(k=4) | ΔF(PC3) | ΔF(PC4) |
|---|---|---|---|---|---|
| thickness | 15.83 | 19.45 | 16.25 | **+3.62** | −3.19 |
| transference | 0.77 | 0.02 | nan | −0.75 | — |
| particle_radius | 26.92 | 19.87 | 17.33 | **−7.05** | −2.54 |

Including PC3 helps thickness (+3.62) and hurts particle radius (−7.05) at this seed. **H9b-localization HOLDS** and agrees with the loadings (F2 coherent).

## 4. (C) Stability — the gain does NOT survive resampling (the decisive result)

200 independent L2 noise seeds (single-RNG draws, re-fit PCA per seed, F-only):

| quantity | mean | sd | 95% CI | fraction favorable |
|---|---|---|---|---|
| Δ_th = F_th(k3) − F_th(k2) | **+1.24** | 4.88 | **[−8.07, +9.90]** | 0.585 |
| Δ_pr = F_pr(k2) − F_pr(k3) | +4.14 | 2.75 | [−0.81, +9.79] | (k=2-favoring) |

Mean F across seeds: thickness k2 **22.01** / k3 23.26; particle radius k2 25.60 / k3 21.46.

**Why the single-seed finding was misleading:** the locked Probe-9 seed gave thickness-k2 = 15.83, but the 200-seed mean is **22.01** — the Probe-9 realization was a ~6-point-low draw on the 2-component thickness projection specifically. k=3 looked better there largely because that noise realization degraded PC1–2 more than PC1–3, a seed-specific accident, not a structural property. Across seeds the thickness k=3 advantage shrinks to +1.24 and straddles zero. **This is the L3 dip (lit/54 §0.1, fact 3) generalizing: the optimal-k for thickness at L2 noise is seed-noisy.**

**On the negative control (F3):** particle radius is far more reliably k=2-favoring than thickness is k=3-favoring — Δ_pr mean +4.14 vs Δ_th mean +1.24 — but at the strict 95% bar even Δ_pr's lower bound dips slightly negative (−0.81). The honest reading is **not** that the control collapsed, but that **at L2 (15–20% multiplicative noise) the per-parameter optimal-k is genuinely seed-noisy for both parameters.** There is no robust, exploitable per-parameter k structure at this noise level. That strengthens, rather than weakens, the "do not adopt adaptive-k" conclusion.

## 5. Disposition (per lit/54 §5)

**MECHANISM REAL BUT UNSTABLE.** Loadings (A) + localization (B) + causation all hold at the single seed and are mutually coherent (F2). But the multi-seed Δ_th 95% interval crosses zero (H9b-null on stability). Per the locked disposition table: *"The geometry is real at one realization but the F-advantage is within seed scatter (the L3 dip generalizes). Do NOT pursue adaptive-k. The 8c PCA-2 amendment stands; k=3 is not a robust improvement."*

## 6. What this closes

- **The PCA-3 thickness refinement is closed — negative.** The Probe 9 side finding (lit/53 §4) was a real geometric effect at one seed but not a robust improvement. No adaptive-k amendment will be drafted. The C3 amendment's PCA-2 choice (lit/47) stands unmodified.
- **Methodological lesson (logged):** a single-noise-seed k-sweep advantage of +3.62 F looked promising but evaporated under resampling. Architectural-choice comparisons at high noise must be multi-seed before adoption. The single-seed Probe-9 number was an unlucky-for-k2 draw, not a property of the geometry.

## 7. What this does NOT establish

- Not a transference result (Probe 9 closed that NULL; GITT remains the only path).
- Not a claim that PC3 is useless — it carries real R_ohmic signal; that signal's *F-advantage over PC2* is just not seed-stable at L2.
- Not generalizable beyond this L9 PyBaMM cohort / Chen2020 / this operator set.
- No change to lit/47.

## 8. RMD-SRC framing

A projection-decomposition probe (Probe 8c lineage) that **converged to a clean negative**: the decomposition is coherent (F2), the mechanism is physically interpretable (R_ohmic→PC3 under diffusion-operator addition), and the validation correctly rejects the candidate refinement on stability grounds. This is RMD-SRC working as intended — a tempting single-realization signal was pre-registered, tested against a multi-seed stability gate, and disposed of honestly rather than adopted.

---

**Lock metadata:**
- Pre-reg lock commit: `d9dcdf6`
- Result commit: `<TBD — recorded in this commit>`
- Analyzer SHA-256: `5e73fb1091361f316ee10fe1df9f74c48fc22e077e99b65c814e27e34487f35a` (`code/c3_probe9b_component_decomposition.py`)
- k-curve parquet SHA-256: `32507db6fcad52ff7254103dc7f2e4537d8a55d26861679d7cc64ce5312a93b7`
- loadings parquet SHA-256: `d58cdc3dcd5301950332b0949e76b5415dcf387b3f634cb631244a2fc3d1e85e`
- stability-seeds parquet SHA-256: `1d7b6a589993e13e0290d07ecbe7d459724632cc42145b6054890f5bc2a900e1`
- input v3 parquet SHA-256: `09c76cb21cf7a8a4065e1d0ce7d9e1a65a6c5617c561c7f19449d328616de850`
- input v2 parquet SHA-256: `7a03bcc9213f5939d4ce581c3aa77289356c122d1eb1f3782fbd417a053f79aa`

## 9. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-27 | 6D analysis used v3's 10 mHz columns rather than the separate v2 parquet. | Equivalent: F1 already proved v3's 10 mHz columns == v2 bit-identical (max\|v2−v3\|=0, lit/53). Avoids re-noising a second parquet with a different seed convention. v2 SHA still recorded for provenance. |
| 2026-05-27 | Part (C) used a single-RNG-per-seed noise draw, not Probe 9's per-cell seed formula. | Pre-reg §3C specified independent re-draws (seed 50000+s) for resampling; the per-cell formula is for single-realization reproduction (parts A/B/F1), which used the imported `apply_noise_8d` verbatim. Mean F differs from the single Probe-9 seed by construction — that difference is the finding (§4). |
