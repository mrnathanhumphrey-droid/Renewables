# Phase 1.10 — Download Summary and Thermal-Channel Verification

**Date:** 2026-05-21
**Total disk usage:** ~4.3 GB across four datasets

---

## Download outcomes

| Dataset | Status | Local path | Size | Notes |
|---|---|---|---|---|
| SECL first-life (Pozzato 2022) | ✅ partial — diagnostics + 1 cycling sample | `data/secl_first_life/` | 139 MB | OSF Dropbox addon required view-only token in path-based URLs |
| SECL second-life (Moy/Khan/Onori 2024) | ✅ complete (extracted) | `data/secl_second_life/SL_Dataset_SECL_INR21700-M50T/` | 4.1 GB | 2.15 GB zip → 4.1 GB unpacked |
| Khan 2025 calendar+cycle | ✅ complete (capacity + EIS) | `data/khan_2025/` | 65 MB | All Excel files + EIS csv/xlsx zips |
| WMG 25-cell (Rashid 2023) | ❌ blocked | `data/wmg_25cell/` (empty) | — | Mendeley uses dynamic signed S3 URLs from UI; programmatic download blocked |

---

## Critical finding — thermal channel coverage is split

### SECL first-life: ✅ continuous thermal logging during cycling
- Cycling .xlsx files: `Channel_3_1` sheet, column 14 = `Aux_Temperature(°C)_1`
- Also in `RawData_3_1` as column 40 = `Aux_Temperature(°C)_3`
- Sample value: 22.9 °C at 10 Hz, 185,534 rows per file = ~5 hrs continuous logging
- **C2's N=3 inter-operator framework (electrical + thermal + EIS) is viable on first-life cohort.**

### SECL second-life: ❌ NO thermal during cycling
- Cycling .xlsx files: `Channel_6_1` has 13 columns (Date_Time, Voltage, Current, capacity, energy, IR, dV/dt) — **no Aux_Temperature**
- `RawData_6_1` has 35 columns, all electrical — **no Aux_Temperature**
- Either the second-life Arbin setup didn't wire the thermocouple to the cycler's aux channel, or the thermal channel was logged to a separate file outside the cycling tests folder. Worth one more sweep of the second-life dataset to rule out the latter, but the immediate finding is the cycling files don't carry temperature.

### Implications for C2 cohort architecture

The original plan was a unified N=16 headline cohort (10 first-life + 6 second-life). That requires revisiting:

**Option A — N=10 first-life only for N=3 headline.** Drop second-life from the N=3 headline. Second-life still contributes to (a) the N=2 sub-test (electrical + EIS, demonstrating the operator-agnostic claim), and (b) Phase 4 mode classification via EIS features.

**Option B — Maintain N=16 via EIS-sub-operator substitution for second-life cells.** Use EIS frequency-band sub-operators (ohmic / charge-transfer / diffusion) as the "third operator" for second-life cells where thermal isn't available. Still N=3 per cell, but the operator set is heterogeneous across the cohort.

**Option C — Confirm whether thermal exists elsewhere in second-life.** Sweep second-life zip for any `_thermal/`, `_environment/`, or separate aux-channel data. Currently no evidence of such files in the extracted structure.

**Recommendation: Option B** — it's most consistent with the revised Phase 0 framing ("operator-agnostic methodology that works on any N ≥ 3 independent-operator combination"). The cohort heterogeneity becomes a feature: it lets us demonstrate the framework adapts to whatever operator set the dataset provides.

---

## Pre-processed MATLAB files — analysis pipeline accelerator

Both Onori datasets ship pre-processed `.mat` files:

**First-life:**
- `diagnostic_tests/_processed_mat/capacity_test.mat` (76 MB) — all capacity diagnostics, all cells, all 15 RPTs
- `diagnostic_tests/_processed_mat/HPPC_test.mat` (18 MB) — all HPPC pulse data
- `diagnostic_tests/_processed_mat/EIS_test.mat` (54 KB) — all EIS spectra
- `diagnostic_tests/_processed_mat/data_analysis.m` — authors' MATLAB processing script

**Second-life:**
- `cycling_tests/Cycling_1/_processed_mat/` (and presumably per-Cycling-segment) — per-cell .mat files: G1.mat, V4.mat, V5.mat, W8.mat, W9.mat, W10.mat, plus data_analysis.m
- Diagnostic tests structure: `RPT_1/` through `RPT_19/` — 19 RPTs (one more than the Moy 2024 paper noted at 16; possibly extended post-publication)

These pre-processed files give us the EIS / capacity / HPPC operators for the full cohort in a few hundred MB. Raw cycling .xlsx files (per-cell, 10-50 MB each, hundreds of files) are deferred unless Phase 2 needs per-cycle operating-condition reconstruction beyond what filenames encode.

---

## Khan 2025 inventory

- **Capacity_data/**: 8 .xlsx files
  - `CD_t25_0d.xlsx`, `CD_t25_10d.xlsx`, `CD_t25_20d.xlsx`, `CD_t25_40d.xlsx`, `CD_t25_90d.xlsx` — cycle-aged cells at 5 RPT timepoints
  - `CDS_t25_70d.xlsx`, `CDS_t25_90d.xlsx` — calendar-aged subset
  - `FCC_charge_discharge.xlsx` — reference data (22 KB)
- **EIS_data/csv/**: 26 cell folders (S1–S26; S2 + S18 excluded per paper, net N=22 valid)
- **EIS_data/xlsx/**: 7 .xlsx files (consolidated EIS sheets)

No thermal channel during cycling on Khan dataset (already known; chamber-level temp only). Phase 4 mode-classification role unchanged.

---

## Phase 1.10 verdict

- ✅ Phase 1.10 complete: thermal channel verified on first-life (continuous); not present on second-life (only electrical channels)
- ✅ Phase 1.7 RPT cadence already verified earlier (every 25-50 cycles for first-life)
- ⏳ Phase 1.8 — power calc for hierarchical Bayesian model still pending; cohort definition needs to land first (Option B vs A above)
- ⏳ WMG 25-cell — Phase 4 cross-validation dataset, manual download via Mendeley UI needed

---

## OSF / Mendeley URL patterns (for reference)

**OSF osfstorage (public files):** `https://osf.io/{guid}/download` works
**OSF Dropbox addon (view-only):** must use path-based URL with view-only token:
`https://files.osf.io/v1/resources/{node}/providers/dropbox/{path/to/file.ext}?action=download&view_only={token}`
**Mendeley:** requires UI-triggered signed S3 URL. No clean programmatic path found this pass.

---

## Outstanding tasks

- Decide N=3 cohort architecture: Option A (N=10 first-life headline) vs Option B (N=16 with EIS-sub-operator substitution for second-life)
- Phase 1.8 power calc on the chosen cohort
- WMG download — note for user to grab via Mendeley UI when convenient
- Raw cycling .xlsx download deferred (only if Phase 2 conditional null needs it)
