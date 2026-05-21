# Phase 1 Dataset and Operator Inventory

**Date started:** 2026-05-21 (Phase 0 close + Phase 1 entry)
**Purpose:** Lock the actual data C2 will use and confirm operator coverage matches the (revised) C2 claim's N ≥ 3 inter-operator requirement.

---

## Datasets evaluated

### A. Stanford SECL first-life INR21700-M50T (Pozzato, Onori et al. 2022)

- **Source:** Stanford Energy Control Laboratory; published as Pozzato et al., *Data in Brief* 41, 107995 (2022). ScienceDirect S2352340922002062.
- **Cells:** 10 × INR21700-M50T (21700 cylindrical, NMC cathode + graphite/silicon anode)
- **Cycling duration:** 23–28 months
- **Environment:** Amerex IC500R thermal chamber at 23 °C, T-type thermocouple on each cell
- **Cycler:** Arbin
- **Charging protocols:** CC-CV at variable rates from C/4 to 3C
- **Discharge profile:** UDDS EV-realistic driving profile
- **RPT cadence:** **Every 25 or 50 cycles** (most cells every 25). Fixed-interval, not condition-triggered.
- **RPT diagnostics:** capacity + HPPC + EIS (full set)
- **EIS:** 0.01 Hz – 10 kHz, at 20/50/80% SOC
- **Folder structure:** `Dataset_SECL_INR21700-M50T/{cycling_tests,diagnostic_tests}`
- **Access:** OSF — https://osf.io/qsabn/
- **Operator inventory:**

| Operator | Channel | Cadence |
|---|---|---|
| Electrical (V, I, Q) | Arbin logged | Continuous during cycling + RPT |
| Thermal (T_cell) | T-type thermocouple | **VERIFY ON DOWNLOAD** — chamber regulates 23 °C but Pozzato paper doesn't explicitly state continuous cycling-phase logging vs RPT-only logging |
| Impedance (EIS spectrum) | Gamry at 3 SOC | Every 25–50 cycles |
| HPPC pulse response | Arbin | Every 25–50 cycles |
| Mechanical/pressure | — | Not measured |

- **Verdict:** **Primary headline cohort, jointly with the second-life SECL extension below.**

### A2. Stanford SECL second-life grid storage (Moy, Khan, Onori et al. 2024) — **COHORT EXTENSION**

- **Source:** Same lab (SECL/Onori). Published as Moy et al., *Data in Brief* (2024). DOI 10.1016/j.dib.2024.111046.
- **Cells:** 6 × INR21700-M50T cells (V4, W8, W9, V5, W10, G1) — **same chemistry as first-life dataset**, entering second-life testing at approximately 90% SOH
- **Cycling duration:** 24 months
- **Environment:** Amerex IC500R chamber at 25 °C, T-type thermocouple (same instrumentation as first-life)
- **Cycler:** Arbin LBT21024
- **EIS hardware:** Gamry EIS 1010E
- **Cycling profile:** Synthetic grid-storage duty cycles (residential and commercial)
- **RPT-S cadence:** 16 RPTs over 24 months, between cycling batches
- **RPT-S diagnostics:** capacity test with pulses + EIS — **explicitly designed by authors to be comparable to first-life RPT structure**
- **Access:** OSF — https://osf.io/8jnr5/
- **Verdict:** **Primary cohort extension.** Same lab, same cell chemistry, intentionally aligned RPT structure. Adds 6 cells to the 10-cell first-life cohort for a combined **N=16 INR21700-M50T cells with electrical + EIS + (likely) thermal across both lifecycle stages**. Cells entering at 90% SOH spend more time in the knee regime — favorable for disagreement-onset analysis.

### A3. Onori group calendar+cycle aging dataset (Khan, Chu, Onori 2025) — **POSSIBLE PHASE 4 EXTENSION**

- **Source:** Same lab. Published as Khan et al., *Data in Brief* (2025). DOI 10.1016/j.dib.2025.112282.
- **Cells:** 22 × NMC/graphite **prismatic** 5 Ah (different format from SECL — cylindrical 21700 vs prismatic 5 Ah)
- **Aging campaign:** 90 days, 18 cycle conditions + 6 calendar conditions
- **RPT cadence:** Days 0, 10, 20, 40, 90 (5 RPTs)
- **RPT diagnostics:** capacity + EIS (no HPPC)
- **EIS:** 0.1 Hz – 20 kHz, 4 pts/decade, at 0/25/50/75/100% SOC, all at 25 °C
- **Thermal logging during cycling:** **NOT continuous** — chamber-level temperature only, no per-cell continuous logging documented
- **Access:** OSF — https://osf.io/j2sn4/
- **Verdict:** **Useful for Phase 4 mode-classification cross-validation only.** Cannot contribute to Phase 3 headline lead-time analysis because (a) no continuous thermal during cycling and (b) 90-day campaign is too short to resolve cycle-count lead time at Ding's 280–323 scale. Different chemistry/format from SECL makes it a robustness check rather than a primary cohort member.

### B. Severson/Toyota/MIT 2019 (Severson et al., *Nature Energy* 4, 383)

- **Cells:** 124 × A123 APR18650M1A (18650 cylindrical, LFP/graphite, 1.1 Ah, 3.3 V)
- **Batches:** 3 (41 / 43 / 40 cells)
- **Cycling:** ~96,700 cycles total; cycle lives 150–2300
- **Charging:** 72 fast-charging protocols (multi-step CC at varying rates)
- **Environment:** Forced-convection chamber (≈30 °C)
- **Access:** Public; data.matr.io
- **Operator inventory:**

| Operator | Channel | Cadence |
|---|---|---|
| Electrical (V, I, Q) | Continuous | Continuous |
| Thermal (T_can) | Continuous, can temperature | Continuous |
| Impedance (EIS) | **Not measured** | — |
| HPPC pulse | Not measured | — |
| Mechanical/pressure | — | Not measured |

- **Verdict:** **Scale benchmark / electrical-only secondary.** No EIS makes Severson unusable as a primary multi-operator C2 substrate. Useful for: (a) demonstrating C2 generalizes — even N=2 (electrical + thermal) version vs single-operator; (b) large-N statistical power for any electrical-only sub-analysis.

### D. WMG/Warwick 25-cell SOH-breakpoint dataset (Rashid, Faraji-Niri, Sansom, Sheikh, Widanage, Marco 2023)

- **Cells:** 25 × NMC811, 21700 cylindrical, 5 Ah (5 cells per SOH breakpoint: 80/85/90/95/100%)
- **Charging:** 0.5C charge, 1C discharge to SOH targets
- **Thermal during cycling:** aged at 25 °C; characterization at 15/25/35 °C
- **EIS:** 10 mHz – 10 kHz, at 5/20/50/70/95% SOC, 3 temperatures (375 total spectra)
- **No HPPC documented**
- **Access:** Mendeley — https://data.mendeley.com/datasets/mn9fb7xdx6/3
- **Verdict:** **Phase 4 cross-validation only.** Cells aged to discrete SOH breakpoints, not continuously cycled — so cannot support cycle-resolved disagreement-onset timing analysis. Useful for cross-validating any EIS-based mode classifier we build, on a different lab's cells.

### C. Zhang Cambridge 2020 EIS dataset (Zhang, Tang, Wang, Stimming, Lee)

- **Cells:** 12 × Eunicell LR2032 (2032 button cell, LCO/graphite, 45 mAh)
- **Spectra count:** >20,000 EIS measurements
- **Coverage:** 9 SOC values × 3 temperatures (25/35/45 °C)
- **Access:** Public (Cambridge repository)
- **Operator inventory:**

| Operator | Channel | Cadence |
|---|---|---|
| Electrical (V, I, Q) | Limited cycling data | Per spectrum |
| Thermal | Controlled variable, not a measurement signal | — |
| Impedance (EIS) | Full spectrum, primary signal | Dense |
| Aging-mode labels | EIS-pattern degradation labels | Per cell |
| HPPC pulse | Not measured | — |
| Mechanical | Not measured | — |

- **Verdict:** **EIS frequency-band sub-operator validation (Phase 4 task 4.2).** Within-EIS decomposition: high-frequency (ohmic), mid-frequency (charge transfer), low-frequency (diffusion). Sub-operators ARE multi-operator in the C2 sense, but all within one modality. Best fit for the Phase 4 mode-classification work, especially given EIS-based aging-mode labels.

---

## Cross-dataset operator-coverage matrix

| Operator | SECL 1st-life | SECL 2nd-life | Khan 2025 | Severson | Zhang Cam | WMG 25 |
|---|---|---|---|---|---|---|
| Cell count | 10 | 6 | 22 | 124 | 12 | 25 |
| Chemistry | NMC/Si-graphite | NMC/Si-graphite | NMC/graphite | LFP/graphite | LCO/graphite | NMC811 |
| Format | 21700 | 21700 | prismatic 5Ah | 18650 | 2032 button | 21700 |
| Electrical (V/I/Q) | ✓ | ✓ | ✓ | ✓ | partial | ✓ |
| Thermal (T_cell) cont. during cycling | likely✓¹ | likely✓¹ | ✗ chamber only | ✓ | ✗ | ✓ aged 25°C |
| Impedance (EIS) | ✓ | ✓ | ✓ | ✗ | ✓ primary | ✓ |
| HPPC pulse | ✓ | partial² | ✗ | ✗ | ✗ | ✗ |
| Aging-mode labels | partial | partial | ✗ | ✗ | ✓ | breakpoint only |
| RPT cadence | every 25-50 cyc | per batch (16 RPTs) | days 0/10/20/40/90 | n/a | n/a | per SOH bkpt |
| Continuous cycling? | ✓ | ✓ | 90-day campaign | ✓ | n/a | breakpoint-aged |

¹ T-thermocouple on cell; continuous-during-cycling logging to be confirmed at file-download time
² RPT-S = "capacity test with pulses + EIS" — pulses present, full HPPC structure to be confirmed

**Phase 1 falsification criterion (from c2_battery_phases.md):**
> "If the operators we need aren't measured at compatible cadences across datasets, or if the diagnostic-test intervals are too coarse to resolve 'onset of disagreement,' scope shrinks to single-dataset analysis."

**Status: PARTIALLY TRIGGERED — but mitigated by Onori-group cohort extension.**

The single-lab Onori cohort spans three datasets with intentionally aligned RPT structure across different lifecycle/aging regimes. This is not multi-dataset cross-replication, but it's substantially better than single-dataset.

---

## Phase 1 finding and recommended scope (REVISED with cohort extension)

### Primary headline cohort (Phase 3): **N = 16 INR21700-M50T cells**

- SECL first-life (10) + SECL second-life (6)
- Same chemistry, same lab, same cycler family, same EIS hardware, intentionally aligned RPT structure
- First-life cells: 23–28 months, RPTs every 25–50 cycles, enter at 100% SOH
- Second-life cells: 24 months, 16 RPTs, enter at ~90% SOH (faster knee-regime arrival)
- Hierarchical Bayesian model with lifecycle-stage as a fixed effect, cell-level random effects

### Secondary cohort (Phase 4 mode-classification): **N = 38 Onori-group cells**

Adds the Khan 2025 calendar+cycle 22-cell prismatic dataset for chemistry/format-robustness check. Mode-classification only, not lead-time analysis. Prismatic-vs-cylindrical effect absorbed as Stan random-effect.

### External cross-validation (Phase 4):

- **Zhang Cambridge 2020** — EIS aging-mode labels for cross-validating the mode classifier on a different lab's cells
- **WMG 25-cell** — different chemistry (NMC811), different lab, EIS-based SOH classifier benchmark
- **Severson 2019** — electrical+thermal-only sub-test to demonstrate the operator-agnostic claim from Phase 0 (methodology degrades gracefully when EIS is unavailable)

### Why this cohort is meaningfully better than the original 10-cell scope

| | Original (10) | Extended (16 → 38) |
|---|---|---|
| Headline cell-count | 10 | 16 |
| Lifecycle coverage | First-life only | First + second-life |
| Mode-classification N | 10 | 38 |
| External cross-val | none | Cambridge EIS labels + WMG + Severson |
| Lab confounder | one lab | one lab (Onori) for headline; multi-lab for mode |

### Cadence resolved (Phase 1.7 ✅)

SECL RPT cadence is every 25–50 cycles. Timing resolution of any inter-operator disagreement onset is ±12.5 to ±25 cycles. Adequate for Ding-scale claims (280–323) with margin. Tight for tens-of-cycles claims — flag this in Phase 3 pre-reg as the resolution floor.

### Thermal-channel verification (RESOLVED 2026-05-21 via download — split outcome)

- **First-life SECL: ✅ continuous thermal logging during cycling confirmed.** Cycling .xlsx files include `Aux_Temperature(°C)_1` in the per-channel sheet, sampled at 10 Hz alongside voltage/current. C2's N=3 framework (electrical + thermal + EIS) is fully supported by first-life data.
- **Second-life SECL: ❌ no thermal during cycling.** Cycling .xlsx files contain only electrical channels (35 columns of voltage/current/capacity/energy/dV/dt, no Aux_Temperature). The Moy 2024 paper documented T-type thermocouple instrumentation but the cycler aux-channel apparently was not configured to log it for the grid-storage campaign.

### Updated cohort architecture (post-thermal-verification)

**Recommended cohort plan (Option B):**

- **Phase 3 N=3 headline cohort: 16 cells, heterogeneous operator set.** First-life cells use {electrical, thermal, EIS}; second-life cells use {electrical, EIS-ohmic, EIS-diffusion} where the within-EIS frequency-band sub-operators serve as the third independent operator. This is consistent with the revised Phase 0 framing as an "operator-agnostic methodology."
- **Alternative (Option A): N=10 first-life only, all with thermal.** Cleaner per-cell operator coverage but smaller cohort.

The headline pre-reg should pre-specify which cohort definition is locked. Recommendation: **Option B** maintains the cohort extension benefit and lets us demonstrate the operator-agnostic claim in the same headline analysis. Option A becomes a "consistent-operator-set sensitivity check" reported alongside.

See [../data/00_download_summary.md](../data/00_download_summary.md) for downloaded file inventory and OSF/Mendeley URL patterns.

### Outstanding Phase 1 tasks

- 1.4 — UCL acoustic dataset (Galiounas et al.) — held in reserve for Path B (unchanged)
- 1.7 ✅ RPT cadence (every 25–50 cycles)
- 1.8 — Rough power calculation for N=16 headline cohort under hierarchical Bayesian framework (still open; do before Phase 2 model fitting)
- File download from OSF (SECL first-life + second-life) — actual data inspection to confirm thermal-channel logging
- BatteryArchive direct study-by-study scan for any additional cohort extensions (Sandia 18650 NCA/NMC/LFP studies could in principle extend, but EIS cadence + thermal-channel coverage needs confirmation per study)
