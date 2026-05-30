# C3 Probe 20 — Noise-Robustness Audit of the Cross-Substrate-Gated {E1, C2} Cascade Pre-Registration

**Status:** LOCKED 2026-05-30 at commit `c4acbd5`. No Probe 20 analysis had fired at lock time. **Integrity disclosure (§0.3):** the clean (L0) WMG transfer F for {C2}, {E1,C2}, {E1,E2,C2} is ALREADY KNOWN from Probe 16/15. They are anchors to be stress-tested under noise, NOT claims — the pre-registered tests below concern noise-robustness, which is untested.
**Date drafted:** 2026-05-30
**Authored:** Claude
**Repo target on lock:** `Battery/literature/74_probe20_xsgated_cascade_noise_audit_prereg.md`
**Prior:** Probe 16 (lit/68+69) closed the cross-substrate arc with the re-selected {E1, C2} cascade transferring to WMG (median F=3.72 [3.35, 4.16], p=0.019, clean). lit/34 (Paper-2 era) documented the within-substrate 7-op cascade was "barely noise-robust" (PyBaMM-holdout F=3.19 just above 3.0 at L2 academic noise) — but that was a different cascade on a different cohort. This probe asks: **does the cross-substrate-gated cascade also pay a noise-robustness cost, or does the cross-substrate gain come for free?** HEAD `2397242`.

## 0. Motivation — does cross-substrate transferability come at a noise-robustness cost?

The Probe-16 re-selected cascade ({E1, C2}) transfers to WMG SOH where the within-substrate 7-op cascade structurally cannot (lit/35 + lit/69). But transferability and noise-robustness are separate axes — a model can be transferable AND noise-fragile (deployable in principle but useless in practice with realistic instrument noise). lit/34 (Probe-6 noise probe) reported the original 7-op cascade was *barely* noise-robust on PyBaMM-holdout (F=3.19 just above 3.0 at L2 = 5% Q / 15% R_ohmic / 20% R_diff academic noise). This probe applies an analogous noise grid to the cross-substrate cascade's WMG transfer task — is the {E1,C2} cascade noise-robust at typical-academic L2 noise?

In **RMD-SRC** terms: a robustness audit (RMD_F2 stability) of a validated predictive-transfer (RMD_F4) result.

## 0.1 What this probe IS and is NOT (integrity disclosure)

- **IS:** a noise-robustness audit of the **Probe-16 cascade and protocol** (RF + leaf-PCA + PERMANOVA on WMG SOH), inspired by lit/34's noise grid but applied to a different cascade (re-selected) and target (WMG SOH transfer, not PyBaMM-holdout).
- **IS NOT** a strict re-run of lit/34 — different cascade, different cohort, different target. The lit/34 F=3.19 result on the 7-op cascade stands unchanged.

## 0.2 Feasibility (verified — Probe 16 anchors are locked)

Probe-16 cohort and parquets are frozen. Clean (L0) anchor: {E1,C2} 200-seed median WMG F=3.72 [3.35, 4.16], ref-seed p=0.019 (lit/69 §4). Comparison-panel anchors {C2}=3.22, {E1,E2,C2}=3.82 (same source).

## 0.3 Integrity disclosure — what is already known (NOT re-claimable)

| quantity | known value | status |
|---|---|---|
| {E1, C2} clean L0 WMG F median | 3.72 | anchor; L0 sanity reproduction only |
| {C2} clean L0 WMG F median | 3.22 | reference panel |
| {E1, E2, C2} clean L0 WMG F median | 3.82 | reference panel |
| lit/34 7-op cascade L2 (PyBaMM-holdout) F | 3.19 | external reference (different cascade/cohort/target) |

Probe 20 does NOT re-assert any of those clean values. It pre-registers whether the re-selected cascade's transfer **survives noise** at lit/34-analog levels.

## 1. Hypotheses (LOCKED)

**H20-main (re-selected cascade is noise-robust at L2 academic):** at the lit/34 L2 noise level (sigma_R_ohmic = 0.15, sigma_R_diff = 0.20, sigma_Q = 0.005 multiplicative; applied to BOTH training and test features), the {E1, C2} cascade's WMG PERMANOVA pseudo-F across 200 noise seeds satisfies **median > 3.0 AND 2.5th-percentile > 2.0** AND reference-seed p < 0.05. (Lower 2.5pct bar than Probe 16's clean 2.5pct>3 because added measurement noise widens the distribution; F_WEAK=2.0 is the lit/34 floor.)

**H20-secondary (degradation profile):** report the F distributions at L0/L1/L2/L3/L4 for all three feature sets — descriptive characterization of the noise-degradation curve, NOT claim-bearing. Lock the level-by-level reporting but NOT a level threshold beyond H20-main.

**H20-null:** at L2 academic noise the {E1, C2} cascade FAILS the locked threshold (median ≤ 3.0 OR 2.5pct ≤ 2.0 OR ref p ≥ 0.05). → cross-substrate transferability comes at a noise-robustness cost; the cascade is transferable-in-principle but not noise-deployable.

## 2. Cohort + data (LOCKED)

- **Source (frozen, reused from Probe 16):** `paper2_operators_{khan,secl,zhang,wmg}.parquet` + `data/khan_2025/cell_conditions.csv`.
- **Training:** {Khan(19), SECL(10), Zhang(8)} = n=37 (Probe-15/16 set).
- **Test:** WMG, n=19, SOH bins {80,85,90,95}.
- **Feature sets:** {C2}, {E1,C2} (primary), {E1,E2,C2} (panel).

## 3. Method (LOCKED — mirrors Probe 16 exactly + lit/34-analog noise grid)

**Noise grid (LOCKED, per lit/34):**

| level | sigma_R_ohmic | sigma_R_diff | sigma_C2 |
|---|---|---|---|
| L0 baseline | 0.00 | 0.00 | 0.00 |
| L1 best lab | 0.05 | 0.10 | 0.001 |
| L2 PRIMARY academic | **0.15** | **0.20** | **0.005** |
| L3 noisy field | 0.30 | 0.30 | 0.010 |
| L4 instrument issue | 0.50 | 0.50 | 0.020 |

Multiplicative noise per feature per cell (independent draws): X_noised = X * (1 + eps), eps ~ N(0, sigma). C2 treated as the "ratio" channel (sigma_C2 ≈ sigma_Q from lit/34 since C2 is dimensionless). E1 = R_ohmic-class → sigma_R_ohmic. E2 = R_diff-class → sigma_R_diff.

**Per noise level × feature set:**
1. For 200 noise seeds b ∈ {0..199}: rng=default_rng(b + 1e6·level); inject noise into Xtr (Khan+SECL+Zhang) AND Xwmg.
2. Run the Probe-16 cascade (RF n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced', random_state=42 [fixed across noise seeds — isolating noise effect from RF-seed effect]) → leaf-PCA → WMG PERMANOVA pseudo-F (F_obs only per seed).
3. At reference noise seed b=42 with full 10,000-perm PERMANOVA: report headline F + p.

Per (level, feature_set) report median, 2.5/97.5 pct, ref p.

## 4. Falsifiers (LOCKED)

**P-Probe20_F1 (L0 baseline reproduction):** at L0 (clean) the {E1,C2} median F across 200 noise seeds reproduces Probe-16's clean anchor (3.72 ± 0.1; same RF seed=42, no noise → deterministic, so all 200 should give identical F=3.681 = the Probe-16 ref-seed value). Confirms pipeline integrity. Other feature sets similarly.

**P-Probe20_F2 (noise non-degeneracy):** at L4 (extreme noise), all feature sets degrade to F<3 in median (sanity that the noise injection actually does something). Fail → noise injection is broken.

**P-Probe20_F3 (lit/34 grid is the locked grid):** no post-hoc grid tuning. If H20-main fails at L2-as-locked, the answer is FAIL — don't re-tune sigmas to find a passing level.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **NOISE-ROBUST** | {E1,C2} at L2: median>3 AND 2.5pct>2 AND ref p<0.05 | Cross-substrate-gated cascade is BOTH transferable AND noise-robust at typical academic noise. Strongest result. |
| **NOISE-FRAGILE-AT-L2** | {E1,C2} at L2 fails ANY of the three thresholds, but L1 passes | Cascade is transferable + robust at best-lab noise only. Tradeoff identified: cross-substrate gain comes at noise-robustness cost. |
| **NOISE-FRAGILE-AT-L1** | {E1,C2} fails L1 too (passes only at L0 clean) | Cascade is transferable-in-principle but not deployable under realistic noise. Strong honest negative. |
| **PROBE 20 INVALID** | F1 fails (L0 doesn't reproduce Probe-16 anchor) | Pipeline broken. Debug. |

## 6. What Probe 20 does NOT establish

- Does not invalidate Probe 16's clean-transfer claim (separate axis).
- Does not invalidate lit/34's 7-op-cascade noise result (different cascade/cohort/target).
- Not a real-cell measurement-noise calibration — multiplicative-Gaussian is a stylized noise model from lit/34. Actual instrument noise distributions differ.
- Not a multi-cohort robustness test (still WMG-only).

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock = commit hash). **Push.**
2. Build `code/c3_probe20_xsgated_noise_audit.py` — reuse Probe-16/15 cascade machinery; loop noise levels × seeds × feature sets.
3. Run. Output `data/processed/probe20_xsgated_noise_audit_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/75_probe20_..._result.md`. Commit + push + lock hashes.

**Cost:** 5 noise levels × 3 feature sets × 200 RF fits (n=37) + 3 reference-seed 10k-perm PERMANOVAs. Minutes.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `c4acbd5`
- Analyzer SHA-256: `221ee96c1d63d96449e05bf3af7a8053317f49c37861cf18bca0d1dc99c07d04`
- Result parquet SHA-256: `b2190d4d63fc8decec1f6f524c28b6e4d002eae5d4e3b367d05708790097e4eb`
- Reused operator parquets: `paper2_operators_{khan,secl,zhang,wmg}.parquet` (Probe 15/16, unchanged)
- Reference baselines: Probe 16 lit/69 clean F values (3.72/3.22/3.82); lit/34 7-op cascade L2 F=3.19 (external reference)
- Result writeup: `literature/75_probe20_xsgated_cascade_noise_audit_result.md` — disposition NOISE-ROBUST ({E1,C2} at L2: median F=4.21, 2.5pct=2.60, p=0.0067; survives through L3)
