# Next Session — Pickup Pointer

**Locked:** 2026-05-22 (commit `273be36` on `main`)
**Last session ended:** Paper 2 full 5-document amended-protocol arc published. Combined headline: "partial replication within-substrate; barely robust to typical academic noise; NOT cross-transferable to real-cell NMC811 via dominant operator." Narrow operational regime documented.

---

## Paper 2 amended-protocol full result chain

| Document | Verdict | Lock commit |
|---|---|---|
| literature/27 (operator catalog pre-reg) | — | 13e9f80 |
| literature/28 (selection + cascade pre-reg + amendments) | — | 7fae62a / 153fbd3 / 3ad6c5c / 7633f7e |
| literature/29 (strict-pre-reg result) | **PAPER 2 INVALID** | 2ffb513 |
| literature/30 (Gate I diagnostic-driven amendment) | — | 3ad6c5c |
| literature/31 (amended-cascade primary) | **PARTIAL REPLICATION** (PyBaMM-holdout F=57.26 PASS, WMG SECONDARY vacant) | d3b1662 |
| literature/32 (cascade noise pre-reg) | — | 7633f7e |
| literature/33 (WMG SECONDARY broadening) | — | 7633f7e |
| literature/34 (noise probe result) | **CASCADE NOISE-ROBUST** at Level 2 (barely; F=3.19 just > 3.0; 95% reduction from baseline) | 273be36 |
| literature/35 (WMG cross-substrate result) | **CASCADE CROSS-SUBSTRATE NULL** (F=0.92, p=0.58 on C2-only restricted cascade) | 273be36 |

## Combined headline (literature/35 §6)

> Paper 2 (amended protocol): partial replication within-substrate (PyBaMM holdout F=57, p<0.001), barely robust to typical academic instrumentation noise (F=3.2 just above the 3.0 threshold), and not cross-transferable via the cascade's dominant operator to a real-cell NMC811 cohort (WMG F=0.92, p=0.58 NULL). The framework as designed has a narrow operational regime: synthetic, low-noise, design-condition-discriminating only.

## Where things stand

Both strict-pre-reg (literature/29: INVALID) and amended-pre-reg with full robustness audit (literature/31 + 34 + 35: PARTIAL REPLICATION + NOISE-ROBUST barely + CROSS-SUBSTRATE NULL) are published. The Paper 2 narrative is closed pending future methodological work.

## Outstanding follow-ups (NOT pre-registered)

1. **Cross-substrate-as-primary-gate redesign.** A Paper-3-equivalent pre-reg that locks cross-substrate validation as a PRIMARY gate alongside (not after) Gate I/II selection. Operators that pass Gate I+II but fail cross-substrate would be dropped. This would change the cascade's operator set.

2. **Expanded operator catalog with cross-substrate-applicable features.** WMG fails because trajectory operators are not extractable from snapshot data. A redesigned catalog could include EIS-derived operators with broader applicability (full Nyquist features, Warburg-region slopes if extractable on more cohorts).

3. **Tighter rank-stability threshold.** Currently ρ_median ≥ 0.50; empirical floor was 0.994. Tightening to 0.85+ would drop weaker operators ex ante.

4. **Train-with-noise cascade.** Inject training-time noise to learn noise-invariant features. Would change the operator-selection priorities. Pre-reg first.

5. **Full-coverage real-cell cohort acquisition.** Identify or generate a real-cell cohort with trajectory + EIS + design-condition coverage matching PyBaMM/Khan/Severson. Without this, the cross-substrate generalization claim cannot be tested end-to-end.

6. **Cross-paper integration writeup.** Paper 1 (independence-framework, C2 N=7 sign-test result + 6 C3 probes) + Paper 2 (noise-robust cascade with full robustness audit) side-by-side methodology paper.

7. **Methodology corpus integration.** Battery substrate alongside sports / SPX / cancer / hydrology / gun violence / NFL / sharks / women's health in cross-substrate methodology paper.

## Repo state

Branch `main` at `273be36`. Push to `origin/main` synced. All literature 00-35 present. All code in `code/`. All parquets in `data/processed/` (gitignored).

New artifacts from this session (2026-05-22):
- literature/30, 31, 32, 33, 34, 35 (full Paper 2 amended-protocol arc + robustness audit)
- code/paper2_gate_I_v2.py, paper2_gate_II_v2.py, paper2_cascade_v2.py, paper2_cascade_v2_noise.py, paper2_cascade_v2_wmg.py
- data/processed/paper2_gate_I_v2_results.parquet, paper2_gate_II_v2_results.parquet, paper2_cascade_v2_summary.pkl, paper2_cascade_v2_importances.parquet, paper2_cascade_v2_noise_results.parquet, paper2_cascade_v2_wmg_results.pkl

## Key result numbers (for citation)

- Amended cascade PRIMARY (PyBaMM-holdout): F=57.26, p=0.0001 (within-substrate, n=36, 9 L9 classes)
- Cascade noise calibration: F=64.5 → 6.0 → 3.2 → 2.0 → 2.0 (Levels 0-4); Level 2 pre-reg PASS at threshold edge
- Cascade WMG SECONDARY (C2-only restricted): F=0.92, p=0.58, NULL (n=19, 4 SOH bins {80, 85, 90, 95})
- 7-operator cascade variable importance: C2 27%, T1 20%, T4 16%, T5 14%, T2 12%, T3 6%, C1 5%
- C2-only restricted cascade 5-fold OOF accuracy: 0.461 (vs 7-op 0.684; vs chance 0.071)
