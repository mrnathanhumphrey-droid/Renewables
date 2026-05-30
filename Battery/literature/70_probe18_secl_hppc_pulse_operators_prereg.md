# C3 Probe 18 — Real-Cell HPPC-Pulse Operators on SECL: Port of the P14 GITT-Class Win to Real Cells Pre-Registration

**Status:** LOCKED 2026-05-30 at commit `<TBD>`. No Probe 18 extraction/analysis had fired at lock time. Feasibility (§0.2) verified read-only on 3 sample pulse xlsx files.
**Date drafted:** 2026-05-30
**Authored:** Claude
**Repo target on lock:** `Battery/literature/70_probe18_secl_hppc_pulse_operators_prereg.md`
**Prior:** Probe 14 (lit/64+65) promoted GITT 8D as the superior **particle-radius** operator on synthetic L9 PyBaMM (F=72 vs EIS 27, multi-seed robust). lit/65 flagged synthetic-only as the binding scope. Probe 11 (lit/58+59) showed EIS reads SOH within-cell on SECL second-life (R_diff_400 Spearman ρ=−0.93). This probe attempts the natural real-cell port. HEAD `d1fac3e`.

## 0. Motivation — does the P14 GITT-class operator win port to real cells?

P14 established that a finite-amplitude operator class (`eta_inst`, `eta_conc`, `dV_slow`) discriminates particle radius far better than the small-signal EIS class on synthetic PyBaMM. **No GITT-capable real-cell cohort exists in the corpus** — but SECL second-life's `Capacity_test_with_pulses` carries discrete HPPC-style current pulses + relaxation, which is the closest **real-cell analog** of GITT physics (current pulse → voltage observable). This probe asks: does the operator class transfer to real cells, when applied to the practically-available target (**SOH**, since SECL has no particle-radius design sweep)?

In **RMD-SRC** terms: a cross-substrate (synthetic→real) and cross-target (pr→SOH) port of an operator class, gated by predictive correlation (RMD_F3) on a real cohort with known labels.

## 0.1 What this probe IS and is NOT (integrity disclosure)

- **IS:** an operator-class port (HPPC-pulse adaptation of GITT-class operators) to real cells, evaluated on SECL second-life SOH (the available real-cell target).
- **IS NOT** a strict 1:1 reproduction of P14 — SECL has no particle-radius design sweep and the pulses are short (~8s + ~10s inter-pulse rest) vs P14's full GITT (~30s pulse + 30-min relaxation). The "slow" diffusion tail is therefore NOT fully accessed; the extracted operators capture the same *physics families* (ohmic, kinetic+early-diffusion, early-relaxation) on a shorter timescale.
- The relevant comparison is **against the Probe-11 EIS baseline on the same SECL cohort** (R_diff_400 ρ=−0.93 for SOH), not against P14's synthetic numbers.

## 0.2 Feasibility (verified read-only before drafting)

113 `Capacity_test_with_pulses` xlsx files (RPT 5–19 × 6 cells {g1, v4, v5, w8, w9, w10}), Arbin format. Structure **bit-identical across sampled files** (g1/RPT10, v5/RPT19, w9/RPT9): six discrete current pulses at step indices {6, 8, 10, 12, 14, 16}, each ~7.9 s at |I|≈2.2 A, alternating discharge/charge at **three SOC levels** (high V≈3.94/4.07; mid V≈3.57/3.70; low V≈3.20/3.33) — which **align with Probe 11's EIS SOC voltages** (3.26/3.63/4.00 V). Inter-pulse rest ≈10 s (allows early-relaxation slope, not full diffusion tail). 1-hr long rests at file start/end exist but are not directly post-pulse → only the 10 s window is usable for `dV_rebound`.

## 1. Operator definitions (LOCKED — the real-cell adaptation)

Per pulse pair (discharge step + charge step at each SOC level) → average the two:

- **R_ohmic_pulse_{soc}** = |V_pre − V_pulse_start| / |I_pulse|. Captures ohmic resistance from the instantaneous voltage jump at pulse onset (analog of P14's `eta_inst` normalized to R).
- **eta_8s_pulse_{soc}** = (V_pulse_start − V_pulse_end) signed by pulse sign, **minus** the ohmic-jump component, divided by |I|. Captures polarization beyond ohmic developing during the 8 s pulse = kinetic + early-diffusion overpotential (real-cell-timescale analog of P14's `eta_conc`).
- **dV_rebound_{soc}** = early-time voltage-recovery slope during the first 10 s of post-pulse rest (linear fit of V vs t over the 10 s window) (truncated analog of P14's `dV_slow`).

**Feature vector per (cell, round): 9D = 3 SOC × 3 operators.** Parallels the Probe-11 EIS 6D (3 SOC × {R_ohmic, R_diff}) and combines cleanly to 15D.

## 1.1 Hypotheses (LOCKED)

**H18-F1 (extraction sanity):** ≥1 pulse operator tracks SOH on the pooled cohort (Spearman ρ<0, p<0.05). Mirrors Probe 11 F1.

**H18-secondary (P14-class port — the strongest read):** ≥1 pulse operator has |ρ| ≥ 0.85 with SOH — i.e., the pulse-derived operator class achieves correlation strength **comparable to** the best EIS operator (Probe 11's R_diff_400 |ρ|=0.93). This is the "GITT-class IS comparable to EIS on real cells" claim.

**H18-main (information additivity):** the combined **{EIS_6D + pulse_9D = 15D}** feature set's C3 PERMANOVA on SOH tertiles (cell-stratified null, k∈{2,3}, mirroring Probe 11 §5) achieves a **pseudo-F at least 25% larger** than {EIS_6D only} on the same cohort — i.e., pulse operators add material information to EIS for SOH discrimination. (Probe-11 baseline: EIS 6D PERMANOVA F=25.51 at k=2 cell-stratified p=0.0027.)

**H18-null:** pulse operators do not track SOH meaningfully (H18-F1 fails) OR they track but the combined set does not exceed EIS-only by ≥25% (no additive value).

## 2. Cohort + data (LOCKED)

- **Source:** `data/secl_second_life/SL_Dataset_SECL_INR21700-M50T/diagnostic_tests/RPT_*/Capacity_test_with_pulses/**/*.xlsx`.
- **Cohort:** SECL second-life, 6 cells × RPT rounds 5–19. Final per-(cell, round) cohort = inner-merge with **Probe 11's `secl_eis_soh_observations.parquet`** (SHA `9dd867c5…`) on (cell, round) — so each row has BOTH the 6D EIS features (Probe 11) AND the new 9D pulse features AND the SOH label. Expected n≈45 (the Probe 11 cohort).
- **Independent unit:** physical cell (cell-stratified null per Probe 11 §5).

## 3. Method (LOCKED)

1. **Extract** per pulse file: identify pulse steps {6,8,10,12,14,16}; locate the preceding rest sample (V_pre); the first pulse sample (V_pulse_start); the last pulse sample (V_pulse_end); the post-pulse 10 s window. Compute the three operators per SOC level, averaging the discharge+charge pulse pair at each SOC.
2. **Merge** with Probe 11's EIS+SOH parquet on (cell, round). Drop rows missing >1 SOC operator (median-impute single missing, matching Probe 11 policy).
3. **F1 + H18-secondary:** Spearman ρ(operator, SOH) for each pulse op on the pooled cohort + p; report alongside the locked Probe-11 EIS values.
4. **H18-main:** reuse Probe-11's PERMANOVA core (`c3_probe11_soh_triage.py::permanova_cellstrat`). Run on three feature sets {EIS_6D, pulse_9D, EIS+pulse_15D} × PCA-k ∈ {2,3}. SOH tertiles computed on pooled SOH (Probe 11 convention). Report F, naive p, cell-stratified p per combination.

## 4. Falsifiers (LOCKED)

**P-Probe18_F1 (extraction sanity):** as H18-F1 above. If ZERO pulse operators track SOH at p<0.05, extraction is broken or operators are uninformative → INVALID.

**P-Probe18_F2 (EIS baseline reproduction):** EIS_6D PERMANOVA on the merged cohort must reproduce Probe 11's F=25.51 at k=2 within 5% (cohort might differ slightly if pulse files miss some Probe-11 rows). Confirms apples-to-apples comparison.

**P-Probe18_F3 (cell-stratified null is more conservative):** as in Probe 11 — cell-stratified p ≥ 3× naive p (or |Δp|>0.01) for the combined set. Confirms non-independence handled.

**P-Probe18_F4 (no operator dominance illusion):** if H18-main passes BUT a single pulse operator alone (1D) matches the combined F, the "additivity" claim is illusory (one dominant operator, not a true combined effect). Flag and document.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **PULSE-OPS-SUPERIOR** (strongest port) | H18-F1 PASS AND H18-secondary PASS (≥1 pulse op |ρ|≥0.85) AND H18-main PASS (combined F ≥1.25× EIS F) | Real-cell pulse-class operators carry SOH signal comparable to EIS AND add complementary information — the P14 GITT-class win ports to real cells. |
| **PULSE-OPS-COMPLEMENTARY** | H18-F1 PASS AND H18-main PASS but H18-secondary FAIL (no pulse op |ρ|≥0.85) | Pulse ops track SOH and add material information when combined with EIS, but no single pulse op matches the best EIS op alone. Useful addition, not a replacement. |
| **PULSE-OPS-REDUNDANT** | H18-F1 PASS but H18-main FAIL (combined F < 1.25× EIS F) | Pulse ops track SOH but encode the same information as EIS — no additive value on this cohort. |
| **PULSE-OPS-NULL** | H18-F1 FAIL | Pulse-derived operators do not track SOH meaningfully — P14's GITT-class win is synthetic-only (or this real-cell adaptation's short timescale is insufficient). |
| **PROBE 18 INVALID** | F2 fails (cannot reproduce Probe 11 EIS baseline within 5%) | Cohort merge or pipeline broken. Debug. |

## 6. What Probe 18 does NOT establish

- Not a strict P14 reproduction — different target (SOH vs pr), different cohort (real SECL vs synthetic L9), and shorter timescale (8 s pulses, 10 s rest vs full GITT). A NULL bounds the real-cell adaptation, not P14's synthetic finding.
- Not a transferable cross-cell model — Probe 11 showed cross-cell SOH transfer is structurally limited on SECL (R²=−4.19, SOH-triage arc terminus). This probe is **within-cohort discrimination + additivity**, not transfer.
- Not a deployment claim — same n=45, 6 cells, 1 chemistry caveats as Probe 11.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock anchor = commit hash). **Push.**
2. Build `code/probe18_secl_pulse_extractor.py` — parse 113 pulse xlsx, emit `data/processed/secl_pulse_ops.parquet` (cell, round, 9 features, n_soc).
3. Build `code/c3_probe18_pulse_vs_eis.py` — merge with Probe 11 EIS+SOH parquet; F1 ρ; reuse Probe 11 PERMANOVA core for {EIS, pulse, combined} × {k=2, k=3}.
4. Run. Output `data/processed/probe18_pulse_vs_eis_results.parquet`.
5. Apply §5 disposition + §4 falsifiers. Write `literature/71_probe18_..._result.md`. Commit + push + lock hashes.

**Cost:** parsing 113 xlsx (a few minutes I/O); analysis trivial (Spearman + PERMANOVA on n=45 × ~15 features). No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD>`
- Extractor SHA-256: `<TBD>`
- Pulse parquet SHA-256: `<TBD>`
- Analyzer SHA-256: `<TBD>`
- Result parquet SHA-256: `<TBD>`
- Reused EIS+SOH parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (Probe 11, unchanged)
- Result writeup: `literature/71_probe18_secl_hppc_pulse_operators_result.md` — disposition `<TBD>`
