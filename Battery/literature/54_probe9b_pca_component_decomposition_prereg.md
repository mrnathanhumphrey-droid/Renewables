# C3 Probe 9b — PCA Component Decomposition Pre-Registration

**Status:** LOCKED 2026-05-27 at commit `d9dcdf6`. No Probe 9b analysis had fired at lock time.
**Date drafted:** 2026-05-27
**Authored:** Claude
**Repo target on lock:** `Battery/literature/54_probe9b_pca_component_decomposition_prereg.md`
**Prior:** Probe 9 CLOSED (lit/52+53, `288a7f8` + `8d3ff3c`) — TRANSFERENCE STILL NULL. This probe investigates Probe 9's **side finding**, not its headline. C3 amendment lit/47 unchanged. HEAD `8d3ff3c`.

---

## 0. Framework parentage

This is a follow-up to **Probe 9's logged side finding** (lit/53 §4): in the 8D operator-augmented feature stack, PCA-k=3 beats PCA-k=2 for **thickness** discrimination at L2 noise (F 15.83 → 19.45), while particle radius stays k=2-best. Probe 9's headline (transference) is untouched here.

In **RMD-SRC** terms (parent at `D:/Resolve Research/RMD SRC Algorithm Specification.docx`): this is a **projection/architecture decomposition** probe in the lineage of **Probe 8c** (lit/45+46, "PCA-2 improves"). 8c established that PCA-2 beats the full-6D cosine PERMANOVA. Probe 9 then added a sub-mHz diffusion operator (6D → 8D), which **re-opened the projection question**: in the augmented space the optimal k is no longer uniformly 2, and it differs by design parameter. This probe localizes *why*.

This is **analysis-only**. No new PyBaMM generation. It reruns the already-committed `pybamm_l9_trajectories_eis_v2.parquet` (6D) and `_v3.parquet` (8D) under the same N1 noise grid.

## 0.1 Motivating evidence (from the locked Probe 9 run)

**The k-sweep is parameter- AND noise-dependent.** From `probe9_transference_results.parquet`:

Thickness PERMANOVA F by (noise level × PCA-k):

| | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| k=2 | 53.70 | 46.68 | 15.83 | **7.39** | 0.78 |
| k=3 | 45.06 | 40.84 | **19.45** | 5.76 | **3.21** |
| k=4 | 47.69 | 38.85 | 16.25 | 7.56 | 2.54 |

Particle radius PERMANOVA F by (noise level × PCA-k):

| | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| k=2 | 30.29 | 31.27 | **26.92** | **26.54** | **16.70** |
| k=3 | 28.19 | 25.73 | 19.87 | 20.89 | 13.51 |
| k=4 | 28.28 | 22.14 | 17.33 | 19.91 | 11.29 |

Three facts to explain:
1. **Thickness optimal-k crosses from 2 (clean, L0/L1) to 3 (noisy, L2 and L4).** PCA-2 dominates at low noise; PCA-3 wins at L2 and L4.
2. **Particle radius is k=2-best at every level, monotone decreasing in k.** Rock-solid PC1–2.
3. **The crossover is non-monotonic — at L3, k=3 DIPS below both k=2 and k=4** (5.76 vs 7.39/7.56). This is a yellow flag: part of the L2 thickness-k3 advantage could be noise-seed scatter rather than stable geometry.

**Baseline transition (6D → 8D at L2, from lit/53):**
- 6D PCA-2: th **21.24**, pr 20.87 (this is the 8c amendment baseline)
- 8D PCA-2: th **15.83** (↓), pr **26.92** (↑)
- 8D PCA-3: th **19.45** (recovered), pr 19.87

Adding the two 1 mHz columns simultaneously *demoted* thickness and *promoted* particle radius under k=2. PCA-3 recovers thickness. **Hypothesis: the 1 mHz operator addition pushed thickness's carrier out of the top-2 eigenvectors.**

## 1. Hypotheses (LOCKED)

**H9b-main (carrier demotion):** In the 8D stack at L2, thickness's primary observable carrier — the R_ohmic channels (column indices 1 = fresh_R_ohmic, 5 = aged_R_ohmic) — loads more heavily onto PC3 than onto PC1 or PC2, while the four R_diff channels (indices 2,3,6,7 = 10 mHz + 1 mHz, fresh + aged) load dominantly onto PC1–2. The 1 mHz columns, being near-collinear with the 10 mHz columns, add variance weight to the diffusion direction, rotating PC1–2 toward the particle-radius axis and demoting the ohmic/thickness axis to PC3.

**H9b-localization (in-architecture marginal gain):** The marginal cosine-PERMANOVA gain from including PC3, ΔF_th(PC3) = F_th(cumulative k=3) − F_th(cumulative k=2), is **positive and material at L2** (consistent with the +3.62 already observed), whereas for particle radius ΔF_pr(PC3) ≤ 0 (PC3 inclusion does not help, consistent with the observed −7.05).

**H9b-causation (6D control):** In the 6D stack (no 1 mHz columns), thickness's carrier loads onto PC1–2 (consistent with 6D-PCA2 F=21.24 already known). Therefore the demotion is *caused* by adding the 1 mHz columns, not an intrinsic property of the ohmic channels.

**H9b-null (seed artifact):** The L2 k=3 > k=2 thickness advantage does not survive multi-seed resampling — the distribution of [F_th(k=3) − F_th(k=2)] across independent noise seeds has a 95% interval crossing zero. The single-seed advantage is noise scatter (the L3 dip generalizes), and there is no stable geometric effect to formalize.

## 2. Cohort + data (LOCKED)

- **Inputs:** `data/processed/pybamm_l9_trajectories_eis_v2.parquet` (6D) and `data/processed/pybamm_l9_trajectories_eis_v3.parquet` (8D). Both already committed/SHA-locked (lit/53 metadata). **No new generation.**
- **Cohort:** identical 101 clean cells (no error, no NaN, no `anchor_partial`) used in Probe 9.
- **Noise grid:** identical N1 grid (L0–L4), same seed convention as Probe 9's `apply_noise_8d` for the single-realization analyses.
- **8D column order (fixed):** `(fresh_Q, fresh_R_ohmic, fresh_R_diff_10mHz, fresh_R_diff_1mHz, aged_Q, aged_R_ohmic, aged_R_diff_10mHz, aged_R_diff_1mHz)` → indices 0–7.

## 3. Method (LOCKED)

Three computations, all on the z-scored stacks (center + pooled-SD), identical preprocessing to Probe 9.

**(A) Eigenvector loadings matrix.** Compute the PCA eigenvectors for the 8D stack at L2 (single Probe-9 seed) and the 6D stack at L2. Report the loadings matrices (8×4 and 6×k) and, per design parameter, identify which observable indices dominate PC1, PC2, PC3. Metric-independent. Tests H9b-main + H9b-causation.

**(B) Cumulative-k cosine-PERMANOVA F curve.** For k ∈ {1, 2, 3, 4} (k=1 added vs Probe 9's {2,3,4}), the in-architecture metric: z-score → PCA-k → unit-vector → cosine distance → PERMANOVA (10K perms, same as Probe 9). Report F per design parameter and the marginal gains ΔF(PCk) = F(k) − F(k−1). The headline quantity is ΔF_th(PC3) at L2. Tests H9b-localization.
- Note on k=1: unit-vector projection in 1D collapses to ±sign, so the cosine metric is degenerate at k=1; k=1 F is reported for completeness but flagged as degenerate and excluded from the marginal-gain interpretation (first valid marginal is ΔF(PC2)).

**(C) Multi-seed stability resampling.** Repeat (B) at L2 for **N=200 independent noise seeds** (seed = 50000 + s, s ∈ 0..199; re-draw the multiplicative noise, re-fit PCA, re-run PERMANOVA F — F-observed only, not the full 10K-perm p each time, to keep it tractable). Report the distribution of:
- Δ_th = F_th(k=3) − F_th(k=2)
- Δ_pr = F_pr(k=2) − F_pr(k=3)
with mean, SD, and 95% percentile interval. This is the stability gate (H9b-null vs the others). Particle radius (Δ_pr) is the **negative control**.

All three run for L2 PRIMARY as the locked headline level; (B) reported at all five levels for context.

## 4. Falsifiers — RMD-SRC F1–F4 inheritance (LOCKED)

**P-Probe9b_F1 ↔ RMD_F1 (reproduction):** The cumulative-k F curve at k=2 must reproduce Probe 9's reported 8D-PCA2 values bit-identically at L2 (th 15.83, pr 26.92, tn 0.77) on the single Probe-9 seed. And k=3 must reproduce th 19.45 / pr 19.87. Validates that the decomposition reruns the same pipeline. INVALID otherwise.

**P-Probe9b_F2 ↔ RMD_F2 (loadings ↔ localization agreement):** The loadings story (A) and the marginal-gain story (B) must **agree**. If loadings say R_ohmic dominates PC3 but ΔF_th(PC3) ≤ 0 (PC3 inclusion doesn't help thickness) — or vice versa, ΔF_th(PC3) > 0 but R_ohmic does NOT dominate PC3 — the mechanism is INCOHERENT and H9b-main is refuted with the conflict documented.

**P-Probe9b_F3 ↔ RMD_F3 (negative control holds):** Particle radius must remain k=2-favoring across the multi-seed resampling: mean Δ_pr > 0 with 95% interval excluding zero. If particle radius *also* starts favoring PC3 under resampling, the "selective demotion" framing collapses — the effect is not parameter-specific. Documented as a §5 concern.

**P-Probe9b_F4 ↔ RMD_F4 (predictive transfer):** N/A — this is a diagnostic decomposition, not a predictive operator. No holdout.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Verdict |
|---|---|---|
| **MECHANISM CONFIRMED (stable)** | H9b-main (loadings: R_ohmic on PC3) + H9b-localization (ΔF_th(PC3) > 0) + H9b-causation (6D: R_ohmic on PC1–2) ALL hold, AND multi-seed Δ_th 95% interval excludes zero (> 0), AND F3 negative control holds | Adding the 1 mHz diffusion operator stably demotes thickness's ohmic carrier to PC3. The k=3-for-thickness advantage is a real, noise-dependent geometric effect. Motivates a **separate** adaptive-/per-parameter-k amendment pre-reg (NOT auto-applied here). |
| **MECHANISM REAL BUT UNSTABLE** | Loadings + localization + causation hold at the single seed, BUT multi-seed Δ_th 95% interval crosses zero (H9b-null on stability) | The geometry is real at one realization but the F-advantage is within seed scatter (the L3 dip generalizes). Do NOT pursue adaptive-k. The 8c PCA-2 amendment stands; k=3 is not a robust improvement. |
| **MECHANISM REFUTED** | Loadings do NOT show R_ohmic dominating PC3, OR localization disagrees with loadings (F2 fires) | H9b-main wrong. The k=3 thickness advantage has another cause; document what the loadings actually show. |
| **PROBE 9b INVALID** | F1 fails (k=2/k=3 don't reproduce Probe 9 values) | Pipeline mismatch. Debug + re-run. |

## 6. What Probe 9b does NOT establish

- **Not an amendment change.** Even MECHANISM CONFIRMED only *motivates* a separate adaptive-k amendment pre-reg with its own falsifiers — because changing PCA-k retroactively across the Probe 5–8 arc is a methodology change, and per-parameter k selection is itself a new architectural degree of freedom that needs its own validation.
- **Not a transference result.** Transference stays NULL (Probe 9). GITT remains the only transference path.
- **Not generalizable** beyond this L9 PyBaMM cohort, Chen2020 chemistry, and this specific operator set. A different operator addition would rotate the PCs differently.
- **Not a claim that more components are better.** The entire point is the *selectivity* — PCA-2 is best for particle radius and at low noise; PCA-3 helps only thickness and only at higher noise.

## 7. Operational protocol

1. Sign-off + commit this pre-reg as `literature/54_probe9b_pca_component_decomposition_prereg.md`. Lock anchor = commit hash.
2. Build `code/c3_probe9b_component_decomposition.py` — loadings (A) + cumulative-k F curve (B) + multi-seed resampling (C). Reuses Probe 9's `apply_noise_8d`, `build_pca`, `cosine_dist`, `permanova_*` (import or copy verbatim for bit-identical F1 reproduction).
3. Run. Output: `data/processed/probe9b_component_decomposition.parquet` (+ a loadings dump).
4. Apply §5 disposition + §4 falsifiers.
5. Write up `literature/55_probe9b_component_decomposition_result.md`. Commit + lock-hashes.

**Cost:** Loadings + k-curve negligible. Multi-seed = 200 seeds × 3 design params × ~F-only PERMANOVA (no 10K-perm p) at L2 ≈ a few minutes wall. No new generation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `d9dcdf6`
- Analyzer script SHA-256: `5e73fb1091361f316ee10fe1df9f74c48fc22e077e99b65c814e27e34487f35a`
- Result parquet SHA-256: `32507db6fcad52ff7254103dc7f2e4537d8a55d26861679d7cc64ce5312a93b7` (k-curve)
- Result writeup: `literature/55_probe9b_component_decomposition_result.md` — disposition MECHANISM REAL BUT UNSTABLE
- Input parquet (8D, already locked in lit/53): `09c76cb21cf7a8a4065e1d0ce7d9e1a65a6c5617c561c7f19449d328616de850` (`pybamm_l9_trajectories_eis_v3.parquet`).
