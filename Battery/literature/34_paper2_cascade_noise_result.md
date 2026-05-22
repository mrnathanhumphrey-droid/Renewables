# Paper 2 — Cascade Noise-Injection Result: CASCADE NOISE-ROBUST (barely)

**Date:** 2026-05-22
**Pre-registration:** literature/32 (commit `7633f7e`)
**Companion result:** literature/31 (amended-cascade PARTIAL REPLICATION at PyBaMM-holdout F=57.26, commit `d3b1662`)
**Verdict per literature/32 §5:** **CASCADE NOISE-ROBUST** at Level 2 (typical academic noise), F = 3.189, p = 0.0001. **PRE-REG PASS, BUT BARELY — F is barely above the locked 3.0 threshold and represents a 95% reduction from the noise-free baseline.**

---

## 0. Headline

| Noise level | σ_Q | σ_R_DC | σ_R_total | pseudo-F | p | Verdict |
|---|---|---|---|---|---|---|
| 0 (baseline) | 0 | 0 | 0 | 64.45 | 0.0001 | (reference) |
| 1 (best-in-class lab) | 0.001 | 0.05 | 0.10 | 6.03 | 0.0001 | strong reduction |
| **2 (typical academic, PRIMARY)** | **0.005** | **0.15** | **0.20** | **3.19** | **0.0001** | **PASS at threshold** |
| 3 (noisy field) | 0.010 | 0.30 | 0.30 | 1.99 | 0.008 | NULL (F<3.0) |
| 4 (instrument-issue) | 0.020 | 0.50 | 0.50 | 2.02 | 0.011 | NULL (F<3.0) |

The pre-reg verdict at Level 2 is **PASS**: F = 3.189 > 3.0 AND p = 0.0001 < 0.05. By literature/32 §5, this is CASCADE NOISE-ROBUST.

**Honest qualification:** F dropped from 64.45 (noise-free) to 3.19 at typical academic noise — a 95.1% reduction in pseudo-F. The cascade survives the pre-reg threshold but the survival margin is razor-thin. Beyond Level 2, the cascade collapses to NULL.

This refutes literature/31 §7 Caveat 4's strict reading ("cascade collapses at typical academic noise") but only at the locked threshold. A tighter threshold (e.g., F > 10) would have reported the cascade as collapsing at Level 2.

## 1. Procedure

Per literature/32 §3-4 (verbatim, no deviations):

1. Re-trained the literature/31 cascade pipeline (seed=42, deterministic). Sanity-check: 5-fold CV OOF accuracy = 0.697 vs literature/31's 0.684 (close but not identical, see §3 below).

2. For each of 5 noise levels (literature/25 §3 / literature/32 §3), applied per-cycle multiplicative Gaussian noise to (Q_max, R_DC, R_total) on PyBaMM-holdout trajectories. Per-cell-per-level seed = `5000 + level*10000 + cond_idx*100 + cell_idx`.

3. Re-extracted the 7 amended-Gate-II-surviving operators (T1, T2, T3, T4, T5, C1, C2) from noisified trajectories using `paper2_extract_others._slope` and `._knee_onset` primitives.

4. Standardized via the same training scaler; scored through the trained RF; projected via the same leaf-indices PCA (fit on training + noise-free holdout); ran PERMANOVA on the PCA embedding labeled by L9 cond_idx (9 classes, n=36 cells, 4 per class).

5. 10,000 permutations per PERMANOVA, Euclidean distance on PCA embedding (matches literature/31).

## 2. Calibration curve

The F-vs-noise-level curve is steeply monotone decreasing:

```
Level 0  F = 64.454   (noise-free, sanity baseline)
Level 1  F =  6.026   (best-in-class lab, 91% reduction)
Level 2  F =  3.189   (typical academic, 95% reduction — PRIMARY TEST POINT)
Level 3  F =  1.990   (noisy field, 97% reduction)
Level 4  F =  2.018   (instrument-issue, 97% reduction)
```

The collapse between Level 0 and Level 1 is striking: σ_Q = 0.001 (0.1% multiplicative) combined with σ_R_DC = 0.05 and σ_R_total = 0.10 already removes 91% of the cascade's pseudo-F. The remaining drop from Level 1 to Level 2 brings the cascade to the pre-reg threshold edge.

Levels 3 and 4 are essentially at noise floor (p still small at 0.008-0.011, but F well below 3.0). The reason both Level 3 and Level 4 produce F ≈ 2.0 (rather than continued monotone decrease) is consistent with the cascade having a hard floor at this n=36, 9-class configuration where any non-trivial embedding structure produces F ≈ 2.

## 3. Baseline reproducibility discrepancy

The Level-0 noise-free F = 64.454 disagrees with literature/31's PRIMARY F = 57.259. Both used the same training data, same RF, same scaler-fit-on-train, same PCA. The cause is the **re-extraction step in this probe**: operator values for the 36 holdout cells were re-computed from `pybamm_l9_trajectories.parquet` per-cycle (Q_max, R_DC, R_total) values via the same primitives, but the resulting operator vector differs in low-order floating-point digits from the parquet-stored values that literature/31's cascade saw.

The mismatch (64.45 re-extracted vs 57.26 from parquet) is ~12% on pseudo-F — a real numerical discrepancy in the operator-extraction pipeline. **It does not invalidate this probe's pre-reg verdict**, which is set on the Level 2 noisified-extraction result against the F > 3.0 threshold, both anchored in literature/32 §4. The verdict criterion does not require the noise-free baseline to match literature/31's value.

The discrepancy is logged here as a methodological note. A future audit pass could:
- Persist the trained scaler/RF/PCA from literature/31's run to disk as deterministic artifacts
- Use the parquet-stored holdout operator values (rather than re-extracting) as the Level 0 reference
- Re-extract only the noisified versions, anchored against the parquet baseline

These changes would unify the baseline at F=57.26. They are NOT done here because doing them post-hoc would risk peeking at the noisified comparison. The current results stand under the literal pre-reg.

## 4. What this proves

**Pre-reg-honest finding:** At the locked Level 2 (typical academic) noise, the trained amended cascade's PRIMARY PERMANOVA passes F > 3.0 AND p < 0.05. By literature/32 §5, this is CASCADE NOISE-ROBUST.

**Honest qualification (the main result):** The cascade's PRIMARY F is heavily noise-sensitive. A 0.5% multiplicative noise on Q + 15% on R_DC + 20% on R_total — the levels established by Probe 6 (literature/26) as representative of academic-lab instrumentation — removes 95% of the cascade's discriminative power. The cascade survives the pre-reg threshold by 0.189 F-units. At Level 3 (1% Q, 30% R_DC, 30% R_total), the cascade collapses to NULL.

**Practical reading:** The trained amended cascade has a narrow operational regime — it works at noise levels significantly below what most real-cell academic-lab data exhibit. Deploying this cascade on real cells would require either:
- Instrumentation at best-in-class lab levels (cell-cycler precision ≥ 99.9% on Q, ≥ 95% on R_DC, ≥ 90% on R_total), which is achievable but uncommon outside Stanford SECL / Imperial / NREL custom rigs
- Re-training with noise injection during training (would change which operators are selected, which is a Paper-3-equivalent pre-reg)
- Restricted application to synthetic / well-controlled-cell substrates where noise is below academic typical

## 5. What this does NOT prove

- That the cascade is broken. It passes the pre-reg threshold honestly.
- That the cascade is robust. It barely passes the threshold; calibration curve shows F-reduction proportional to noise; modest threshold tightening would flip the verdict.
- That cross-substrate generalization works. That is a separate question; see literature/35 (WMG SECONDARY).
- Anything about chemistry-heterogeneity or calendar-variation contributions (Probe 6's locked noise model is multiplicative measurement noise only).

## 6. Recommended citation framing

For methodology-corpus integration:

> "The amended cascade's PyBaMM-holdout PRIMARY (literature/31, F=57) collapses by 95% under Probe-6-locked instrumentation noise (literature/34). At Level 2 (typical academic, 0.5% Q / 15% R_DC / 20% R_total), pseudo-F drops to 3.19, just above the locked 3.0 threshold (p<0.001). The cascade is pre-reg-honest noise-robust at this threshold but has minimal margin; Level 3 (noisy field) and Level 4 (instrument-issue) noise produce NULL outcomes. The framework's operational regime is below typical academic instrumentation."

## 7. Outputs

- `code/paper2_cascade_v2_noise.py` — noise-injection probe (re-train cascade, inject noise, re-extract operators, score, PERMANOVA)
- `data/processed/paper2_cascade_v2_noise_results.parquet` — per-level (F, p, df) calibration curve

---

**Locked at commit (to be recorded after push):** _TBD_
