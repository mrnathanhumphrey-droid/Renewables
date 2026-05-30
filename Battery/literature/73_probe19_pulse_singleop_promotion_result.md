# C3 Probe 19 — Pulse Single-Operator Promotion Gate RESULT

**Status:** COMPLETE. Disposition = **PULSE-OP-DOMINANCE-WASHES-OUT.** The Probe-18 F4-surfaced single-operator dominance (eta_8s_pulse_363 alone F=44.33, eta_8s_pulse_400 alone F=42.25) does NOT survive the pre-registered 9b-style stability gate. Cell-stratified bootstrap 2.5th-pct = 6.73 / 4.37 (locked bar = 10) and paired pulse-beats-EIS frac = 0.618 / 0.650 (locked bar = 0.975) both fail. **The F=44 anchor was a cell-composition artifact; the locked Probe-18 PULSE-OPS-REDUNDANT disposition stands.**
**Date:** 2026-05-30
**Authored:** Claude
**Pre-reg:** `literature/72_probe19_pulse_singleop_promotion_prereg.md` (lock `cc1c6d5`).
**Prior:** Probe 18 (lit/70+71) F4 falsifier surfaced single-operator dominance; lit/71 §7 named this probe as the next disciplined step before any promotion.

---

## 0. One-line result

The anchor F values reproduce exactly (44.333 / 42.250 / 25.507 — matches Probe 18 to 0.001). The 9b-style stability gate then fires the locked **PULSE-OP-DOMINANCE-WASHES-OUT** disposition: cell-stratified bootstrap (N=500) drives the 1D F's 2.5th-percentile down to **6.73 (eta_363) / 4.37 (eta_400)** — both well below the locked bar of 10 — while the paired pulse-beats-EIS-cascade fraction is only **0.618 / 0.650** (locked bar 0.975). Observation-bootstrap looks robust (2.5pct = 34.5 / 23.6, both clearing 10), but the two bootstrap modes disagreeing IS the finding — cells are the independent unit, so cell-stratified is the honest read. The Probe-18 F=44 anchor sat at a favorable cell composition; under cell resampling, F crashes as low as 0.7 (min). **The locked Probe-18 disposition `PULSE-OPS-REDUNDANT` stands without amendment.**

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** anchor reproduction | within 0.05 of {44.33, 42.25, 25.51} | 44.333 / 42.250 / 25.507 | **PASS** |
| **F2** degenerate-bootstrap guard | <5% degenerate resamples | 0/500 cell-strat, 0/500 obs | **PASS** |
| **F3** tertile-edge ±2% sensitivity | verdict must not flip | both directions: same WASHES-OUT verdict (no flip) | **PASS** (not binning-fragile) |
| **F4** distribution-not-anchor judgment | H19-main judged on bootstrap, not anchor | judged on bootstrap (discipline applied) | **PASS** |
| **H19-main eta_8s_pulse_363** | cell-strat AND obs-boot both median>25 AND 2.5pct>10 | cell-strat 2.5pct=**6.73** < 10 | **FAIL** |
| **H19-main eta_8s_pulse_400** | same | cell-strat 2.5pct=**4.37** < 10 | **FAIL** |
| **H19-secondary** paired pulse>EIS ≥97.5% (cell-strat) | — | eta_363 = **0.618**, eta_400 = **0.650** | **FAIL** |

## 2. The two bootstrap modes disagree — and the disagreement is the finding

| feature | mode | median F | 2.5pct | 97.5pct | min | max |
|---|---|---:|---:|---:|---:|---:|
| eta_8s_pulse_363 | cell-strat | 44.33 | **6.73** | 225.00 | 0.73 | 256.00 |
| eta_8s_pulse_363 | obs-boot | 49.00 | 34.53 | 211.00 | 20.60 | 213.58 |
| eta_8s_pulse_400 | cell-strat | 45.00 | **4.37** | 136.94 | 0.76 | 271.06 |
| eta_8s_pulse_400 | obs-boot | 46.47 | 23.61 | 113.11 | 14.17 | 217.00 |
| EIS_6D (cascade) | cell-strat | 30.96 | 4.38 | 88.90 | 1.31 | 405.48 |
| EIS_6D (cascade) | obs-boot | 31.09 | 15.41 | 73.01 | 6.75 | 229.38 |

Observation-bootstrap preserves cell composition (each obs is sampled independently from the pool of n=45 rows; cells stay roughly proportionally represented). Cell-stratified bootstrap resamples 6 cells with replacement — duplicated or dropped cells reshape the cohort drastically. **The pulse 1D F is dominated by which cells get included**; obs-boot hides this dependency, cell-strat exposes it. This is the **same pattern that distinguished P13's failure** — when two bootstrap modes disagree, the cell-level mode is the honest read because cells are the independent unit.

The paired comparison nails it: in matched cell-strat resamples, **pulse beats the EIS cascade only ~62–65% of the time** — barely above the 50% chance baseline, far below the locked 97.5% non-overlap criterion. There IS *some* signal (>50%), but not the dominance the F=44 anchor suggested.

## 3. Mechanism — why F=44 was a cohort artifact

The anchor cohort (Probe-18 merged) has 6 cells with SOH grouped by cell: g1≈92% (n=9), v4≈92% (n=6), v5≈93% (n=9), w8≈89% (n=9), w9≈90% (n=6), w10≈90% (n=6). Pulse `eta_8s_pulse_363` happens to **separate the high-SOH cells (g1, v4, v5) from low-SOH cells (w8, w9, w10) very cleanly** in the deterministic cohort — yielding F=44. Under cell-stratified bootstrap, sampling 6 cells with replacement frequently produces unbalanced selections (e.g., all-high-SOH or all-low-SOH cells, or 4× one cell + 2× another), corrupting that clean class separation. The F-distribution becomes wide [0.7, 256] with a heavy negative tail.

**The deterministic F=44 was a fortunate cell composition, not an operator property.** This is the exact 9b failure mode the gate exists to detect — and it did.

## 4. Disposition (per lit/72 §5)

**PULSE-OP-DOMINANCE-WASHES-OUT.** F1 PASS (anchor reproduces), F4 discipline applied, both candidate operators FAIL the cell-stratified 2.5pct bar AND the paired-dominance bar. The locked **Probe-18 PULSE-OPS-REDUNDANT** disposition is upheld without amendment. F4-surfaced finding was a cell-composition single-realization artifact, exactly as the gate is designed to catch.

## 5. What Probe 19 establishes / does not

**Establishes:**
- The 9b stability gate **rejected another dominance-finding** that looked compelling at a single realization, consistent with the discipline's track record (rejected: 9b PCA-3, P13 R_diff-only, now P19 pulse-dominance; promoted: P14 GITT-pr; caught lit/35 re-attribution at P15).
- A **mechanism** for why the F4 finding was an artifact: pulse `eta_8s` cleanly separates the 6 cells' SOH means by cell identity — under cell-resampling, that clean separation breaks.
- The **two bootstrap modes' disagreement** (cell-strat vs obs-boot) as a diagnostic — when they disagree, cell-strat is the honest read because cells are the independent unit.
- The pre-registered F3 tertile-edge perturbation confirmed the failure is NOT binning-fragility (the verdict holds under ±2%).

**Does NOT establish:**
- That pulse operators are uninformative — they ARE competitive with EIS (Probe 18 |ρ|=0.91 vs 0.93; pulse-beats-EIS ~62% > chance 50%), just not dominantly so.
- That the EIS_6D cascade is robust either — EIS cell-strat 2.5pct = 4.4 shows EIS suffers the same fragility on n=6 cells. The cohort is small; both feature sets have cell-composition-sensitive Fs.
- Anything about the GITT-class operator class on real cells beyond the dominance claim — the H18-secondary `competitiveness` PASS in Probe 18 (best pulse \|ρ\|=0.91) is unchanged by this probe.

## 6. RMD-SRC framing

A predictive-validation (RMD_F3) promotion gate that returned NEGATIVE under proper cell-stratified resampling — the 9b discipline applied verbatim. The locked Probe-18 disposition holds; the F4 falsifier did its intended job (surface the dominance possibility); Probe 19 did its intended job (gate the dominance honestly). **Pre-registration discipline once again rejected an attractive single-realization finding** — the same gate that promoted GITT-pr and rejected 9b-PCA-3 / P13-R_diff-only.

---

**Lock metadata:**
- Pre-reg lock commit: `cc1c6d5`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `4782e7065d045663cc62091ad13f6c1cbb108858da0f25bd6de9d9acdab57594`
- Result parquet SHA-256: `c05240af98128446e84453d8c594a08c61214362926f20e3e69c0500fef0b4f2`
- Reused pulse parquet SHA-256: `6e9765aa4102c2f6c63b4164f16c76dfcf522cf25b86d83b5460c35ef82eb60a` (Probe 18, unchanged)
- Reused EIS+SOH parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (Probe 11, unchanged)

## 7. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
