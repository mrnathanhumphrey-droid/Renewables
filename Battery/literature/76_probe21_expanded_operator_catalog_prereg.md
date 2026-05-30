# C3 Probe 21 — Expanded Operator Catalog Under the Cross-Substrate-Primary Gate Pre-Registration

**Status:** LOCKED 2026-05-30 at commit `<TBD>`. No Probe 21 extraction/analysis had fired at lock time. Feasibility (§0.2) verified read-only — full EIS spectra are available on disk for all real-EIS cohorts (WMG, Khan, SECL first-life, SECL second-life) but the existing operator catalog uses only R_ohmic + R_diff endpoints, discarding 58/60 mid-frequency points per WMG spectrum.
**Date drafted:** 2026-05-30
**Authored:** Claude
**Repo target on lock:** `Battery/literature/76_probe21_expanded_operator_catalog_prereg.md`
**Prior:** Probe 16 (lit/68+69) re-selected {E1, C2} as the cross-substrate-gated cascade (WMG F=3.72). Probe 20 (lit/74+75) showed it's noise-robust (L2 F=4.21). NEXT.md #2 has queued "expanded operator catalog with cross-substrate-applicable features" since 2026-05-22. This probe executes that queue item using the existing Probe-16 selection machinery. HEAD `22fd7d8`.

## 0. Motivation — can additional EIS-spectrum operators pass the cross-substrate gate and strengthen the Paper-3 deliverable?

The existing 12-op catalog reduces to **only {E1, C2}** under the cross-substrate-primary gate (Probe 16), giving modest transfer (clean F=3.72). The bottleneck is that the catalog's EIS-spectral operators (E1/E2/E3) were defined as endpoint statistics (high-freq Re intercept, low-freq Re minus intercept, or NaN) — discarding the mid-frequency information present in the raw spectra. WMG alone has 60 frequency points per spectrum; only Re@max-freq and Re@min-freq are used. **If physically-motivated mid-spectrum operators are admitted by the gate, the re-selected set grows and transfer F should improve.**

In **RMD-SRC** terms: a catalog expansion (RMD Step 0 / partition expansion) under a locked validation procedure (RMD_F4 transferability), preserving the same XS-primary gate as Probe 16.

## 0.1 Five locked candidate operators (NEW, EIS-snapshot-extractable on raw spectra)

Computed from a single EIS spectrum `(freq, Re(Z), -Im(Z))` at the canonical SOC (50% / ~3.63 V) per cell:

- **W1_warburg_slope** = σ_w from linear fit of Re(Z) vs ω^{-1/2} on the **lowest-frequency 30%** of points. Warburg-region slope = solid-state diffusion coefficient proxy.
- **W2_peak_neg_im_log_freq** = log10(frequency at which −Im(Z) is maximum). Apex of the mid-freq charge-transfer semicircle; inversely related to R_ct·C_dl time constant.
- **W3_peak_neg_im_norm** = max(−Im(Z)) divided by R_ohmic. Normalized semicircle height; charge-transfer impedance magnitude.
- **W4_inductive_tail** = (Re(Z) at highest freq − R_ohmic) / R_ohmic. Captures non-ideal HF inductive contribution.
- **W5_arc_chord_length** = sum of Euclidean distances between consecutive (Re, −Im) points across the full spectrum. Nyquist arc path length / shape complexity.

All five are computable from any (freq, Re, Im) triple of ≥10 points. All extractable on **WMG** (60 pts), **Khan** (raw EIS xlsx/csv), and **SECL** (first-life .mat has 19 pts × 3 SOC; second-life Gamry ACIM has 43 pts).

## 0.2 Feasibility (verified read-only before drafting)

- **WMG raw EIS:** `data/wmg_25cell/DIB_Data/DIB_Data/.csvfiles/EIS_Test/Cell{N}_{SOH}SOH_{T}degC_{SOC}SOC_*.xls` — 3 cols [freq, ReZ, −ImZ], 60 rows per file, 5 SOC × 3 T × 25 cells. Existing `wmg_extract_features.py` parses this format. Canonical: SOC=50, T=25.
- **Khan raw EIS:** `data/khan_2025/eis_csv/` + `eis_xlsx/`; existing `khan_extract_and_classify.py::extract_eis_per_cell_per_day(soc="S50")` returns R_ohmic + R_diff but accesses the same raw spectra used to compute those.
- **SECL first-life:** `data/secl_first_life/diagnostic_processed/EIS_test.mat` (scipy v7, Probe-12 path): `re_z`/`im_z`/`freq` as (15 diag × 10 cell) object arrays of (19 freq × 3 SOC) matrices. SOC index 1 = 50%.
- **SECL second-life:** Gamry ACIM xlsx per Probe-11 extractor (43 pts × 3 SOC voltages 3.26/3.63/4.00 V).

All four real-EIS cohort raw EIS sources verified to exist. Zhang excluded from this probe — different raw format, deferred to a follow-up.

## 0.3 Integrity disclosure — what is already known (NOT re-claimable)

The existing {E1, C2} clean WMG transfer F=3.72 (Probe 16) and L2 noise-robust median F=4.21 (Probe 20) are anchors to be matched/exceeded, NOT claims. Probe 21 does NOT re-assert them; the new claims concern whether the expanded catalog admits additional operators and whether the re-selected expanded cascade improves transfer.

## 1. Hypotheses (LOCKED)

**H21-extraction (F1 sanity):** ≥3 of the 5 new operators are extractable (≥3 finite values) on WMG AND on ≥2 of the real-EIS training cohorts {Khan, SECL_first_life, SECL_second_life}. (At least 3 of 5 new operators clear the XS-1 extractability gate before any selection is run.)

**H21-selection (gate admits new operators):** applying the **Probe-16 XS-primary procedure** (XS-1 extractability on held-out snapshot WMG + ≥2 training cohorts; XS-2 modality-matched stability; XS-3 modality-matched discrimination) to the **expanded 17-op catalog** (12 existing + 5 W-operators), the re-selected set contains **≥1 new operator** beyond {E1, C2}.

**H21-main (transfer improves materially):** the expanded re-selected cascade's WMG transfer 200-seed median F is **> 4.50** (clears Probe-16 anchor 3.72 by ≥20%; clears Probe-20 noise L2 anchor 4.21 by a small margin) AND 2.5th-pct > 3.0 AND ref-seed p < 0.05.

**H21-secondary (noise robustness preserved):** the expanded cascade at L2 academic noise (per lit/74 grid) still passes the locked Probe-20 thresholds (median F > 3, 2.5pct > 2, p < 0.05). Confirms catalog expansion doesn't sacrifice noise robustness.

**H21-null:** either H21-selection fails (no new operator survives XS-primary — the catalog expansion was tested and the gate held to {E1, C2}, honest negative) OR H21-main fails (new ops admitted but transfer F ≤ 4.50 → catalog expansion is neutral, not material). Both are honest pre-registered outcomes.

## 2. Cohort + data (LOCKED)

- **Source (frozen):** raw EIS data per §0.2 + existing operator parquets for the 12-op baseline + Probe-15/16 training cohort {Khan, SECL_first_life, Zhang} (n=37) + WMG held-out (n=19, SOH labels).
- **NEW operator emission:** per cohort, compute the 5 W-operators per cell at canonical state (SOC=50% / 3.63V / 363mV label as appropriate) → enrich each `paper2_operators_*.parquet` with 5 new columns. Skip Zhang (raw EIS access not yet wrapped — flagged as a follow-up).
- **Training set for the cascade:** unchanged from Probe 16 — {Khan (19), SECL first-life (10), Zhang (8) using existing E1/E2/C2 if any new op is selected only from cohorts with raw EIS extraction}. If Zhang's new-op columns are all NaN, exclude Zhang only when the selected feature set contains a new op (transparent per-config cohort handling, documented at run).
- **Held-out:** WMG (n=19, soh_eis bins {80,85,90,95}).

## 3. Method (LOCKED — mirrors Probe 16 + new extraction)

1. **Extract** the 5 W-operators per cohort (Khan, SECL first-life, SECL second-life, WMG) from raw EIS at SOC=50% (canonical state). Per-cohort extractor functions wrap the existing raw-EIS access patterns.
2. **Augment** existing `paper2_operators_*.parquet` with 5 new columns (NaN where extraction fails or cohort excluded).
3. **Apply XS-primary procedure** (Probe-16 §0.1) to the 17-operator catalog: XS-1 extractability on WMG + ≥2 real training cohorts; XS-2 modality-matched stability (reuse Gate-I rank-stability metric per op family — W-ops treated as level-like → CV<0.30); XS-3 modality-matched discrimination on Khan aging_type (AUC ≥0.70). Emit attrition table + re-selected set.
4. **Validate transfer** on WMG (Probe-16 protocol, 200-seed RF random_state bootstrap, reference-seed 10k-perm PERMANOVA). Compare to Probe-16 {E1, C2} clean baseline.
5. **Noise audit** at lit/74 L2 (academic) on the expanded cascade — 200-seed (matched Probe-20 protocol).

## 4. Falsifiers (LOCKED)

**P-Probe21_F1 (extraction sanity):** as H21-extraction (≥3 of 5 W-ops extractable on WMG + ≥2 training cohorts). Fail → extraction broken or W-ops degenerate → INVALID.

**P-Probe21_F2 (anchor reproduction):** existing {E1, C2} cascade clean WMG F under the new pipeline reproduces Probe-16 anchor (3.72 ± 0.1) — confirms the augmented parquet doesn't perturb the baseline. Fail → augmentation pipeline broken.

**P-Probe21_F3 (gate is the procedure, not the headline):** H21-selection judged by whether XS-primary admits any new operator — not by whether the transfer F goes up. If H21-selection holds but H21-main fails, that's "EXPANDED-GATE-NEUTRAL," not a procedure failure.

**P-Probe21_F4 (no post-hoc threshold tuning):** Probe-16 XS-primary thresholds (XS-1 ≥3 finite + ≥2 training; XS-2 Gate-I rules; XS-3 Khan AUC ≥0.70) and the 17-op catalog (12 existing + 5 locked W-ops) are pre-committed. No mid-run threshold tuning. New ops failing the locked thresholds is an honest outcome.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **EXPANDED-GATE-IMPROVES** | H21-selection PASS AND H21-main PASS AND H21-secondary PASS | The expanded catalog admits new operators that materially improve WMG transfer while preserving noise robustness. Paper-3 deliverable strengthens. |
| **EXPANDED-GATE-IMPROVES-FRAGILE** | H21-selection + H21-main PASS but H21-secondary FAIL (noise-fragile at L2) | New ops admitted and lift transfer but sacrifice noise robustness — tradeoff identified. |
| **EXPANDED-GATE-NEUTRAL** | H21-selection PASS (new op admitted) but H21-main FAIL (F ≤ 4.50) | New ops pass the gate but don't materially improve transfer. Honest neutral. |
| **EXPANDED-GATE-REJECTS-NEW** | H21-selection FAIL (no new W-op survives XS-primary) | The gate's locked thresholds reject the new operators. Catalog expansion was tested and the gate held to {E1, C2}. Honest negative; strengthens Probe-16's {E1, C2} robustness. |
| **PROBE 21 INVALID** | F1 fails (W-ops not extractable) OR F2 fails (anchor doesn't reproduce) | Pipeline broken. Debug. |

## 6. What Probe 21 does NOT establish

- Not a real-cell deployment claim — still WMG n=19 single-cohort test.
- Not an exhaustive catalog — only 5 new W-operators (physically-motivated, but not the complete set possible from a full EIS spectrum). E.g., Cole-Cole depression angle, ZARC fit parameters, full EIS-equivalent-circuit ECM fit residuals are deferred.
- Zhang excluded from new-op extraction (raw EIS access deferred); the gate runs on {Khan + SECL first/second-life + WMG} for new ops.
- A POSITIVE expanded-gate verdict does not redefine the Probe-16 deliverable; it strengthens it by extension.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock = commit hash). **Push.**
2. Build `code/c3_probe21_expanded_catalog_extractor.py` — per-cohort W-op extraction from raw EIS (Khan, SECL first-life .mat, SECL second-life Gamry, WMG xls). Emit augmented `paper2_operators_*_v2.parquet`.
3. Build `code/c3_probe21_expanded_gate.py` — apply Probe-16 XS-primary procedure to the 17-op catalog; report attrition + re-selected set; run Probe-16 200-seed WMG transfer validation; run Probe-20 L2 noise audit on the re-selected set.
4. Run. Output `data/processed/probe21_expanded_gate_results.parquet`.
5. Apply §5 disposition + §4 falsifiers. Write `literature/77_probe21_..._result.md`. Commit + push + lock hashes.

**Cost:** EIS-spectrum extraction across ~50 cells with full spectra each (Khan + SECL + WMG); 200-seed × 2 RF panels (clean + L2 noise). Minutes.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD>`
- Extractor SHA-256: `<TBD>`
- Augmented parquets SHA-256: `<TBD>`
- Analyzer SHA-256: `<TBD>`
- Result parquet SHA-256: `<TBD>`
- Reused (unchanged) baseline parquets: `paper2_gate_I_v2_results.parquet`, `paper2_gate_II_v2_results.parquet`, `paper2_operators_*.parquet` (for 12-op baselines)
- Result writeup: `literature/77_probe21_expanded_operator_catalog_result.md` — disposition `<TBD>`
