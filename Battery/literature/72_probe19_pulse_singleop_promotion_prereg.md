# C3 Probe 19 — Single-Operator Promotion of `eta_8s_pulse_{363,400}` for SECL SOH: Bootstrap Stability Gate Pre-Registration

**Status:** LOCKED 2026-05-30 at commit `<TBD>`. No Probe 19 analysis had fired at lock time. **Integrity disclosure (§0.3): the anchor 1D PERMANOVA F values are ALREADY KNOWN** from Probe 18's F4 falsifier (eta_8s_pulse_363 alone F=44.33; eta_8s_pulse_400 alone F=42.25 on the merged n=45 SECL cohort). They are *anchors to be stress-tested*, NOT claims — the pre-registered tests below concern resampling robustness, which has not been computed.
**Date drafted:** 2026-05-30
**Authored:** Claude
**Repo target on lock:** `Battery/literature/72_probe19_pulse_singleop_promotion_prereg.md`
**Prior:** Probe 18 (lit/70+71, `a2c9298`) closed PULSE-OPS-REDUNDANT (locked); the pre-reg's F4 falsifier (operator-dominance illusion check) surfaced that `eta_8s_pulse_363` alone (1D PERMANOVA F=44.33) and `eta_8s_pulse_400` alone (F=42.25) each individually exceed the EIS_6D combined cascade (F=25.51) and even the combined 15D cascade (F=28.05) on SECL second-life SOH tertiles. lit/71 §7 named this probe as the next step — pre-register the 9b stability gate before any promotion. HEAD `a2c9298`.

## 0. Motivation — does the F=44 single-operator dominance survive resampling, or is it the 9b failure mode?

The 9b lesson ([[feedback_diagnostic_driven_amendments]], lit/55) is canonical in this program: a +3.62 single-seed F advantage washed to +1.24±4.88 across 200 seeds. The discipline since: any single-realization advantage requires a multi-seed/bootstrap stability gate before promotion. **P14 (GITT-pr)** survived such a gate emphatically → first promotable positive. **P13 (R_diff-only SOH)** failed it (bootstrap 2.5pct=−0.46) → SINGLE-SPLIT ARTIFACT. Probe 18's F=44 single-operator finding is the next candidate. This probe applies the same gate.

In **RMD-SRC** terms: a predictive-validation (RMD_F3 + RMD_F4) promotion gate on a single-realization point estimate, using cell- and observation-bootstrap.

## 0.1 Physical hypothesis

Real-cell HPPC pulse-induced polarization at 8s captures kinetic + early-diffusion overpotential, both of which grow with SOH loss (impedance buildup at electrode/electrolyte interface). The mid-to-high SOC range (363/400 mV labels) is where ageing signatures are strongest on NMC cells. The dominance of `eta_8s_pulse_{363,400}` reflects that these operators read a SOH-portable polarization quantity directly. **If real, the dominance is a robust property of the operator, not a cohort/sampling accident.**

## 0.2 Feasibility (verified — Probe 18 anchors)

Probe 18's merged cohort (n=45, 6 cells, SOH 88.0–93.7%) is locked + frozen. Pulse-ops parquet SHA `6e9765aa…` + EIS+SOH parquet SHA `9dd867c5…` (Probe 11). 1D PERMANOVA F per operator already computed deterministically; the resampling distribution is what's untested.

## 0.3 Integrity disclosure — what is already known (NOT re-claimable)

| quantity | known value | status |
|---|---|---|
| eta_8s_pulse_363 1D PERMANOVA F on n=45 | **44.33** | anchor, to be stress-tested |
| eta_8s_pulse_400 1D PERMANOVA F on n=45 | **42.25** | anchor, to be stress-tested |
| EIS_6D combined PERMANOVA F on n=45 (Probe 11 / Probe 18 F2) | 25.51 | reference cascade |
| Best EIS 1D operator (R_diff_400) Spearman \|ρ\| | 0.926 | reference single-op |
| Best pulse operator (eta_8s_pulse_363) Spearman \|ρ\| | 0.910 | (already established competitive — Probe 18 H18-secondary PASS) |

Probe 19 does **not** re-assert "eta_8s_pulse_363 F=44." It pre-registers whether that value survives **cell-stratified bootstrap** AND **observation bootstrap** (with the bootstrap CI strictly dominating the EIS cascade) — quantities I have not computed.

## 1. Hypotheses (LOCKED)

**H19-main (the 9b-style stability gate — PRIMARY judgment):** for each candidate operator op ∈ {`eta_8s_pulse_363`, `eta_8s_pulse_400`}, the 1D PERMANOVA F is **robustly dominant**:
- (a) **cell-stratified bootstrap (N=500):** resample 6 cells with replacement; compute 1D F on the resampled cohort. Distribution requirement: **median > 25 AND 2.5th-percentile > 10**. (Median clears the EIS cascade F=25.51; 2.5pct stays well above the F_FLOOR=3 PASS threshold.)
- (b) **observation bootstrap (N=500):** resample 45 observations with replacement (within-cell membership preserved). Same distribution requirement: median > 25 AND 2.5pct > 10.
PASS requires **both** (a) and (b) for that operator.

**H19-secondary (apples-to-apples superiority — promotable claim):** under matched-resample (paired) bootstrap, the pulse 1D F **strictly dominates** the EIS_6D cascade F — pulse F > EIS_6D F in **≥ 97.5%** of resamples (cell-stratified, 500 seeds). This is the rigorous "single pulse operator robustly beats the entire EIS cascade" claim.

**H19-null:** F=44 / F=42 wash out (median ≤ 25 OR 2.5pct ≤ 10) for both operators OR the EIS-dominance fails (<97.5% wins under paired resample). → the F4 finding was single-realization artifact, do NOT promote. (Mirrors P13 SINGLE-SPLIT ARTIFACT.)

## 2. Cohort + data (LOCKED)

- **Source (frozen):** the Probe-18 merged cohort (`secl_pulse_ops.parquet` ∩ `secl_eis_soh_observations.parquet` on (cell, round)). n=45, 6 cells {g1,v4,v5,w8,w9,w10}, SOH 88.0–93.7%.
- **Tertile bins:** computed on each resample's SOH distribution (per-resample tertiles, so binning adapts to the resampled cohort — mirrors Probe 11/18 convention). NOT pre-computed on the locked cohort then frozen.
- **Independent unit for cell-stratified bootstrap:** physical cell.

## 3. Method (LOCKED)

For each candidate operator + EIS_6D (for paired comparison):
1. **Anchor reproduction:** compute the deterministic 1D PERMANOVA F on the locked cohort → must reproduce 44.33 / 42.25 / 25.51 (F1 sanity).
2. **Cell-stratified bootstrap (b=0..499):** rng=default_rng(b); sample 6 cell labels with replacement; build resampled cohort (cells may repeat); compute SOH tertile bins on resampled SOH; compute 1D PERMANOVA pseudo-F (no permutation null per seed — F_obs is the stability object).
3. **Observation bootstrap (b=0..499):** rng=default_rng(b+10000); sample 45 row indices with replacement from the locked cohort; compute SOH tertiles + 1D F.
4. **Paired comparison (cell-stratified, same seed b):** in each resample compute BOTH pulse 1D F AND EIS_6D cascade F; count fraction with pulse > EIS.
5. **Reference seed PERMANOVA p:** at the deterministic anchor (no resample) with 10,000 perms → reported as headline p alongside the bootstrap distribution.

PERMANOVA core reused verbatim from `c3_probe11_soh_triage.py` / `c3_probe9_extended_permanova.py`. Bootstrap variability per resample is the stability object; per-resample permutation p is omitted for speed (the F distribution is what's tested).

## 4. Falsifiers (LOCKED)

**P-Probe19_F1 (anchor reproduction):** the deterministic 1D F values must reproduce 44.33, 42.25, 25.51 within numerical tolerance (<0.01). Fail → pipeline broken → INVALID.

**P-Probe19_F2 (degenerate-bootstrap guard):** a cell-stratified resample with fewer than 2 unique cells produces a degenerate PERMANOVA (insufficient between-group structure). Filter and report; if >5% of resamples are degenerate, flag the cohort's sensitivity (6 cells, P(all-same)=6/6^6 = 0.013% — should be negligible).

**P-Probe19_F3 (tertile-edge sensitivity sanity):** repeat (a) cell-stratified bootstrap with SOH tertile edges PERTURBED by ±2% (a tertile-boundary cell can flip class). If the H19-main verdict flips, the dominance is binning-fragile (not a single-realization artifact but a binning artifact) — disposition adjusts.

**P-Probe19_F4 (H19-main is judged on distribution, not on the anchor):** if the anchor reproduces (F1 PASS) but the bootstrap median/CI fails, that IS the 9b failure mode — disposition = WASHES-OUT, regardless of how high the anchor was. (This is the discipline.)

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **PULSE-OP-DOMINANCE-PROMOTED** | H19-main PASS for **both** ops (cell-strat AND obs-boot median>25 AND 2.5pct>10) AND H19-secondary PASS (paired-bootstrap pulse>EIS in ≥97.5%) | Promote: `eta_8s_pulse_{363,400}` are robust single-operator SOH discriminators on real-cell HPPC pulses, dominating the EIS_6D cascade. Real-cell port of the P14 GITT-class win in single-operator form. |
| **PULSE-OP-DOMINANCE-PARTIAL** | H19-main PASS for ONE op only, OR H19-main PASS both but H19-secondary fails (CI overlap) | Partial promotion. Document which op survives and which doesn't; no joint claim. |
| **PULSE-OP-DOMINANCE-WASHES-OUT** | H19-main FAIL for both (the 9b failure mode) | F4-surfaced dominance was a single-realization artifact. Honest negative; closes the dominance claim and confirms the locked PULSE-OPS-REDUNDANT disposition. |
| **BIN-ARTIFACT** | F3 flips verdict under ±2% tertile-edge perturbation | The dominance is binning-fragile; not promotable as-is. |
| **PROBE 19 INVALID** | F1 fails (anchor doesn't reproduce) | Pipeline broken. Debug. |

## 6. What Probe 19 does NOT establish

- A cross-cell transferable model — Probe 11 closed that arc; this is within-cohort discrimination robustness only.
- A real-cell PR result — SECL has no pr design sweep. SOH is the target (same as Probe 18).
- A deployment claim — n=45, 6 cells, 1 chemistry.
- A statement that the C3 cascade architecture is wrong in general — only that for single-operator-dominance physics on THIS cohort, the cascade dilutes the signal (a methodological note, not a framework verdict).

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock = commit hash). **Push.**
2. Build `code/c3_probe19_pulse_singleop_gate.py` — reuse Probe 18/11 PERMANOVA core; cell-stratified + observation bootstrap (N=500 each); paired pulse-vs-EIS comparison; tertile-edge sensitivity arm.
3. Run. Output `data/processed/probe19_pulse_singleop_gate_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/73_probe19_..._result.md`. Commit + push + lock hashes.

**Cost:** analysis-only on existing parquets; 500 × 2 bootstrap modes × 3 features on n=45 (tiny). Seconds. No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD>`
- Analyzer SHA-256: `<TBD — filled in result commit>`
- Result parquet SHA-256: `<TBD>`
- Reused pulse parquet SHA-256: `6e9765aa4102c2f6c63b4164f16c76dfcf522cf25b86d83b5460c35ef82eb60a` (Probe 18, unchanged)
- Reused EIS+SOH parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (Probe 11, unchanged)
- Result writeup: `literature/73_probe19_pulse_singleop_promotion_result.md` — disposition `<TBD>`
