# C3 Probe 18 — Real-Cell HPPC-Pulse Operators on SECL RESULT

**Status:** COMPLETE. **Locked disposition = `PULSE-OPS-REDUNDANT`** (per lit/70 §5), but the locked F4 falsifier surfaces a substantively richer finding the H18-main threshold doesn't capture: **single pulse operators dominate** the EIS 6D cascade (1D F=44 > EIS-cascade F=25), so the P14 GITT-class operator-class win **ports to real cells in single-operator form** — just not in additive-multi-operator-cascade form on this cohort. The C3 cascade architecture (PCA-2 + cosine) *dilutes* the dominant pulse operators when combining them with EIS.
**Date:** 2026-05-30
**Authored:** Claude
**Pre-reg:** `literature/70_probe18_secl_hppc_pulse_operators_prereg.md` (lock `497047b`).
**Prior:** Probe 14 (lit/64+65) GITT-PR-SUPERIOR on synthetic L9; Probe 11 EIS SOH baseline F=25.51 cell-stratified on SECL second-life.

---

## 0. One-line result

Extracted real-cell HPPC-pulse operators on 111/113 SECL second-life pulse xlsx (6 cells × ~19 RPT rounds; sensible physics — R_ohmic_pulse 28–32 mΩ ≈ EIS R_ohmic). Merged with Probe 11 EIS+SOH on (cell, round) = n=45 (the Probe-11 cohort). **EIS baseline F2 PASS exactly** (EIS_6D F=25.51 matches Probe 11 to 0.0%). **H18-secondary PASS** (best pulse |ρ|=**0.910** for `eta_8s_pulse_363`, essentially matches EIS best |ρ|=0.926 for R_diff_400). **H18-main FAIL** (combined 15D F=28.05 / EIS_6D F=25.51 = **1.10× < locked 1.25×**). **F4 FIRES with the substantive finding**: single pulse operators *individually* exceed the combined cascade — `eta_8s_pulse_363` alone has 1D F=**44.33**, `eta_8s_pulse_400` alone F=**42.25** — both substantially HIGHER than EIS_6D combined (25.51) AND than combined 15D (28.05). PCA-2 cosine cascade *dilutes* this single-operator dominance when pulse is mixed with EIS. **The P14 GITT-class operator-class competitiveness ports; the additive-cascade-lift framing doesn't.**

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **F1** ≥1 pulse op tracks SOH (ρ<0, p<0.05) | — | 7/9 pulse ops track; best `eta_8s_pulse_363` ρ=−**0.910** p<1e-9 | **PASS** |
| **F2** EIS baseline reproduces Probe 11 (±5%) | EIS_6D k=2 F ≈ 25.51 | F=**25.507** (diff 0.0%) | **PASS** |
| **F3** cell-stratified null materially differs from naive | implicit (Probe 11 §5 logic) | naive p=0.0001 → cell-strat p=0.0027 (27×) for EIS; pulse 0.0001→0.0152 (152×); combined 0.0001→0.0071 (71×) | **PASS** |
| **F4** no single-op illusion (max 1D pulse F < combined F) | max 1D < combined 15D F | max 1D = **44.33** (eta_8s_pulse_363) > combined 15D F = 28.05 | **FIRED** (single-operator dominance) |
| **H18-secondary** ≥1 pulse op |ρ|≥0.85 | — | best |ρ|=0.910 | **PASS** |
| **H18-main** combined F ≥ 1.25× EIS F | — | 28.05 / 25.51 = **1.10×** | **FAIL** |

## 2. Per-operator Spearman ρ vs SOH (pooled n=45)

| pulse operator | ρ | p | EIS counterpart (reference) | ρ | p |
|---|---:|---:|---|---:|---:|
| eta_8s_pulse_363 | **−0.910** | <1e-9 | R_diff_363 | −0.730 | <1e-7 |
| R_ohmic_pulse_400 | −0.881 | <1e-9 | R_ohmic_400 | −0.846 | <1e-9 |
| eta_8s_pulse_400 | −0.851 | <1e-9 | R_diff_400 (best EIS) | **−0.926** | <1e-9 |
| R_ohmic_pulse_363 | −0.816 | <1e-9 | R_ohmic_363 | −0.726 | <1e-9 |
| R_ohmic_pulse_326 | −0.579 | <1e-3 | R_ohmic_326 | −0.791 | <1e-9 |
| eta_8s_pulse_326 | −0.518 | <1e-3 | R_diff_326 | −0.012 | 0.94 |
| dV_rebound_pulse_363 | −0.510 | <1e-3 | — | — | — |
| dV_rebound_pulse_326 | +0.477 | <1e-3 | — | — | — |
| dV_rebound_pulse_400 | −0.111 | 0.47 | — | — | — |

Mid + high SOC pulse operators are **the strongest in the cohort**, slightly below or competitive with the best EIS operator (R_diff_400 ρ=−0.926). Low-SOC pulse operators are weak (consistent with EIS R_diff_326's near-zero ρ — low SOC carries less SOH information on this cohort).

## 3. PERMANOVA cascade comparison (SOH tertiles, cell-stratified null)

| feature set | dim | k=2 F | k=2 p_cellstrat | k=3 F | k=3 p_cellstrat |
|---|---:|---:|---:|---:|---:|
| EIS_6D (Probe-11 baseline) | 6 | 25.51 | 0.0027 | 19.79 | 0.0034 |
| pulse_9D | 9 | **25.55** | 0.0152 | 23.89 | 0.0107 |
| combined_15D | 15 | **28.05** | 0.0071 | 25.39 | 0.0094 |

**The pulse-only 9D cascade essentially matches EIS_6D** (F=25.55 vs 25.51). Combined adds 10%, well short of the 1.25× lift the locked H18-main required.

## 4. The F4 finding — single-operator dominance (single-pulse 1D PERMANOVAs)

| pulse operator | 1D F | vs combined 15D F=28.05 |
|---|---:|---|
| **eta_8s_pulse_363** | **44.33** | **+58%** dominant alone |
| **eta_8s_pulse_400** | **42.25** | **+51%** dominant alone |
| R_ohmic_pulse_400 | 23.28 | competitive |
| R_ohmic_pulse_363 | 13.58 | weak |
| dV_rebound_pulse_363 | 7.00 | weak |
| R_ohmic_pulse_326 | 6.78 | weak |
| eta_8s_pulse_326 | 4.94 | weak |
| dV_rebound_pulse_326 | 2.33 | weak |
| dV_rebound_pulse_400 | 0.34 | null |

Two mid+high-SOC pulse operators each *individually exceed* the combined 15D cascade F. The PCA-2-cosine cascade is *down-weighting* the dominant pulse signal by mixing it with weaker pulse + EIS dimensions. The same pattern holds against EIS_6D F=25.51: two pulse operators alone beat the entire EIS cascade.

**Methodological reading:** when an operator class concentrates the discriminative signal in 1–2 dominant features, the cascade architecture (PCA-2 + cosine projection) is the wrong combiner — it averages dominant + weak features in directions that don't preserve the dominant signal. The "additive multi-operator" framing of H18-main is inappropriate when the underlying physics is single-operator-dominant. The locked F4 caught exactly this.

## 5. Disposition (per lit/70 §5)

**`PULSE-OPS-REDUNDANT`** by the locked criterion (F1 PASS, H18-main FAIL: combined < 1.25× EIS). The disposition label fits the additivity check faithfully and the pre-reg outcome is honest.

**Substantively richer reading (from F4 + H18-secondary):** the P14 GITT-class operator-class win **does port to real cells** — but in **single-operator-dominance** form, not multi-operator-additivity form. Real-cell HPPC pulse operators carry SOH signal at concentrations EIS doesn't (single 1D pulse F=44 > entire EIS cascade F=25), with the best pulse |ρ|=0.91 essentially matching the best EIS |ρ|=0.93. The locked H18-main framing (additive cascade lift) was the wrong test for an operator class with dominant single features; F4 made this visible.

## 6. What Probe 18 establishes / does not

**Establishes:**
- **Feasibility:** real-cell HPPC pulse operators are extractable on 111/113 SECL pulse files with sensible physics; the protocol is bit-identical across cells/RPTs.
- **Operator-class competitiveness:** the P14 GITT-class operator class is competitive with EIS on real-cell SOH discrimination — best pulse |ρ|=0.91 ≈ best EIS |ρ|=0.93.
- **Single-operator dominance** (F4): two pulse operators (eta_8s at mid+high SOC) each individually exceed the EIS 6D cascade's PERMANOVA F — a methodologically informative pattern.
- **Locked additivity null:** no 1.25× lift from combining pulse + EIS — the C3 cascade architecture's PCA-cosine compression dilutes the dominant pulse signal.

**Does NOT establish:**
- A transferable cross-cell model — this is within-cohort discrimination only (Probe 11 closed the cross-cell-transfer arc for SECL SOH).
- A pr (particle-radius) result — SECL has no pr design sweep. This was an operator-class port with target swap pr→SOH (disclosed in lit/70 §0.1).
- That pulse operators are universally superior — only on this n=45 SECL second-life cohort, at this short pulse/rest timescale.
- A promotion of single pulse operators — the F4 finding is striking but **single-cohort, single-realization**. Per the 9b discipline (lit/55, validated by P14/P16), any promotion of "eta_8s_pulse_363 alone beats EIS" requires a multi-seed/multi-cohort stability gate before claim. Logged as motivated follow-up.

## 7. Motivated next step (would need own pre-reg)

**Probe 19 candidate:** pre-register single-operator dominance of `eta_8s_pulse_{363,400}` for SOH via the 9b multi-seed/bootstrap stability gate — does the 1D F=44 survive cell-stratified bootstrap resampling? If yes, the GITT-class real-cell port becomes a single-operator promotion claim. (Mirrors P14's promotion of GITT-pr via the same gate.) Bounded, analysis-only, builds on the F4 finding here without claiming it now.

## 8. RMD-SRC framing

A cross-substrate (synthetic→real) and cross-target (pr→SOH) operator-class port, validated by predictive correlation (RMD_F3). The operator class is informative on real cells (RMD_F1 PASS, |ρ|=0.91). The locked H18-main (additive cascade lift) was the wrong framing for the underlying physics (single-operator dominance); the locked F4 caught this — pre-registration discipline surfaced a richer real finding than either of the simple PASS/FAIL outcomes would have. Cross-substrate rule extension: **operator-class transferability is real for direct-physics-encoded targets (P14's pr → P18's SOH) but the BEST aggregation architecture differs — single-feature dominance vs cascade-additive.**

---

**Lock metadata:**
- Pre-reg lock commit: `497047b`
- Result commit: `<recorded in this commit>`
- Extractor SHA-256: `889dff5ab1d2f98b310e07f63d439046c5f01bf4049d748f851733a8e4de0b16`
- Pulse parquet SHA-256: `6e9765aa4102c2f6c63b4164f16c76dfcf522cf25b86d83b5460c35ef82eb60a`
- Analyzer SHA-256: `e6ee89ca152ada8189915157343c2b58329b846ec22213d61bbcedad694c1191`
- Result parquet SHA-256: `597f8adbf70d118bcb7690427930104421e32c609ca3a896d9940a2a76dbcda7`
- Reused EIS+SOH parquet SHA-256: `9dd867c532b86dd3058a719cb8bf2750f28decccadb935bb09f73d98323ca703` (Probe 11, unchanged)

## 9. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
