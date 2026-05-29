# C3 Probe 16 — Full Cascade Re-Selection Under the Cross-Substrate-Primary Gate (Paper-3 deliverable) Pre-Registration

**Status:** LOCKED 2026-05-29 at commit `<TBD>`. No Probe 16 re-selection/validation had fired at lock time. Scoping (re-ran the existing Gate I v2 + Gate II v2 read-only to read current attrition) done before drafting (§0.2).
**Date drafted:** 2026-05-29
**Authored:** Claude
**Repo target on lock:** `Battery/literature/68_probe16_cascade_reselection_under_gate_prereg.md`
**Prior:** Probe 15 (lit/66+67) showed the lit/35 cross-substrate NULL was a training-cohort artifact: with modality-matched real-EIS training, {C2} and {E1,E2,C2} transfer to WMG SOH. lit/67 §9 named the follow-up: full cascade re-selection under the gate. HEAD `df18fcd`.

## 0. Motivation — does cross-substrate-primary selection yield a transferable cascade where within-substrate selection does not?

The existing Paper-2 pipeline selects operators by Gate I (rank-stability across 4 cohorts) → Gate II (design-condition AUC on {PyBaMM, Khan, Severson}). Probe 15 + the §0.2 re-run expose a structural flaw: **two of Gate II's three cohorts (synthetic PyBaMM, EIS-less Severson) cannot extract the EIS-spectral operators**, so those operators are dropped for *cohort coverage*, not for lack of signal. The 7-operator cascade is therefore trajectory-dominated — and trajectory operators are exactly the ones that cannot be computed on a real-cell *snapshot* test cohort (WMG). This probe makes cross-substrate extractability + modality-matched discrimination a **primary** selection gate, re-selects the cascade as a reproducible procedure, and tests whether the re-selected set transfers where the within-substrate set structurally cannot.

In **RMD-SRC** terms: a selection-methodology (RMD Step-0/validation) redesign, validated by predictive transfer (RMD_F4) on a held-out real cohort, with the multi-seed stability discipline (9b).

## 0.1 The cross-substrate-primary selection procedure (LOCKED)

Run on all 12 catalog operators. An operator is **re-selected** iff it passes all three:
- **XS-1 Extractability (PRIMARY):** ≥3 finite values on the held-out snapshot real cohort **WMG** AND on ≥2 real training cohorts ({Khan, SECL, Zhang, Severson}). (Structural, label-free.)
- **XS-2 Modality-matched stability:** the Gate-I metric (slope: bootstrap rank-stability ρ≥0.50; level: CV<0.30 with IQR/|median| fallback) computed on the real cohorts where the operator is genuinely extractable (NOT synthetic PyBaMM, NOT mean-imputed), cross-cohort rule ≥3 of 4 (or ≥75% of available). **Reuses the locked Gate-I v2 results.**
- **XS-3 Modality-matched discrimination:** Gate-II metric (max one-vs-rest AUC ≥ 0.70) on ≥1 real cohort with design/aging labels where the operator is extractable (Khan has aging_type/T_C/soc_range; SECL/Zhang carry no condition labels). **Reuses the locked Gate-II v2 metrics, re-scored on modality-matched cohorts.**

The procedure OUTPUT (the re-selected set) is determined by the data — it is NOT pre-specified here (only the procedure is locked).

## 0.2 Current attrition (verified read-only before drafting — re-ran Gate I v2 + Gate II v2)

- **Gate I v2 (stability, 4 cohorts):** 8/12 survive — {C1, C2, E1, T1, T2, T3, T4, T5}. (E2 fails 2/3; CE1, D1, E3 fail/no-data.)
- **Gate II v2 (discrimination, {PyBaMM, Khan, Severson}):** 7/8 survive — {C1, C2, T1, T2, T3, T4, T5}. **E1 dropped — but with Khan AUC=1.000; it failed only because it is finite on 1 of the 3 Gate-II cohorts (<2 required), i.e. cohort-coverage, not signal.**
- **Within-substrate 7-op cascade extractability on WMG (snapshot):** only **C2** is extractable (T1–T5 need trajectories; C1 needs trajectory R-growth). → the 7-op cascade reduces to C2-only on WMG (the lit/35 setup).
- **Cross-substrate-extractable on WMG:** {E1, E2, C2} only.

## 1. Hypotheses (LOCKED)

**H16-selection (the procedure re-selects an EIS set):** the cross-substrate-primary procedure (§0.1) re-selects a non-empty operator set dominated by snapshot-extractable EIS operators, *keeping* operators the within-substrate Gate II discards for cohort-coverage (E1) and *dropping* the trajectory operators (T1–T5) it keeps. (Procedure output, reported; the exact set is data-determined.)

**H16-main (re-selected cascade transfers):** the re-selected cascade, trained on modality-matched real-EIS cohorts {Khan, SECL, Zhang}, discriminates WMG terminal-SOH — PERMANOVA pseudo-F **robustly > 3.0** (200-seed median AND 2.5th-pct) AND reference-seed p < 0.05 — whereas the within-substrate 7-op cascade **cannot even be evaluated** on WMG beyond C2 (structural non-extractability). This is the methodological claim: cross-substrate-primary selection yields a transferable cascade; within-substrate-only selection does not.

**H16-null:** the re-selected cascade does NOT transfer robustly (median/2.5pct F≤3 or p≥0.05). Then the cross-substrate-primary gate cleanly identifies the transferable operator set but that set still fails to transfer on this cohort → the binding limit is the substrate gap, not selection. (Arc-terminus parallel.)

## 2. Cohort + data (LOCKED)

- **Source (reused unchanged):** `paper2_gate_I_v2_results.parquet`, `paper2_gate_II_v2_results.parquet`, `paper2_operators_{khan,secl,zhang,wmg,pybamm_train,severson}.parquet`, `data/khan_2025/cell_conditions.csv`.
- **Re-selected-cascade training:** modality-matched real-EIS cohorts {Khan(19), SECL(10), Zhang(8)} = n=37 (the Probe-15 training set; labels kh_{aging_type}/secl/zhang).
- **Held-out cross-substrate test:** WMG, n=19, SOH bins {80,85,90,95} (`soh_eis`).
- WMG labels used ONLY in the transfer test; selection (XS-1/2/3) uses extractability + design/aging labels, never WMG SOH → not circular.

## 3. Method (LOCKED)

1. **Re-selection:** apply §0.1 procedure using the locked Gate-I/II parquets + the extractability map; emit the attrition table (12 → XS-1 → XS-2 → XS-3 → re-selected set) and the re-selected operator list.
2. **Validation (mirrors Probe 15 / `c3_probe15_crosssubstrate_gate.py`):** RF (`n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced'`) on the re-selected feature set, trained on {Khan,SECL,Zhang}; leaf-indices → PCA(≤10) on train+WMG → WMG PERMANOVA (Euclidean, 10k perms at ref seed 42). **200-seed RF multi-seed** → F distribution (median, 2.5/97.5 pct, frac>3). 5-fold→3-fold CV sanity.
3. **Comparison panel:** report WMG transfer for {re-selected set}, {C2}-only (lit/35 op, matched-trained), {E1,E2,C2} (Probe-15 max-EIS set), and note the within-substrate 7-op cascade's WMG-extractable subset (= {C2}).

## 4. Falsifiers (LOCKED)

**P-Probe16_F1 (procedure non-degenerate):** the re-selected set is non-empty and every member is extractable on WMG. Empty/degenerate → reconsider thresholds (report, don't force).

**P-Probe16_F2 (within-substrate set is structurally non-transferable):** the Gate-I+II 7-op set must have ≤1 operator extractable on WMG (confirming the transfer problem is structural, not incidental). Expected: only C2. If >1, the framing is wrong — flag.

**P-Probe16_F3 (multi-seed stability — the 9b gate):** H16-main judged on the 200-seed F distribution, never a single seed. Single-seed-only pass with failing CI → FAIL.

**P-Probe16_F4 (reproducible procedure):** the re-selection is deterministic from the locked gate parquets + extractability (no hidden randomness). Re-running yields the identical set.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **XS-GATE-YIELDS-TRANSFERABLE-CASCADE** | H16-selection (EIS set re-selected, trajectory ops dropped) AND H16-main PASS (re-selected cascade robust F>3, p<0.05) AND F2 (within-substrate set ≤1 WMG-extractable) | The cross-substrate-primary gate is a validated selection methodology: it re-selects a transferable cascade where within-substrate-only selection structurally cannot transfer. The Paper-3 deliverable. |
| **XS-GATE-SELECTS-BUT-NO-TRANSFER** | H16-selection holds but H16-main FAIL | The gate correctly isolates the transferable operator set, but that set still does not transfer on this cohort → substrate-gap limit, not selection. Honest negative; still re-scopes the methodology. |
| **PROCEDURE-DEGENERATE** | F1 fails (empty/trivial re-selected set) | Thresholds too strict for the corpus. Report; reconsider. |

## 6. What Probe 16 does NOT establish

- Not a strong/deployable transfer claim — WMG n=19, effects modest (Probe 15: F just above 3).
- Not a change to Paper-2 within-substrate results (PyBaMM-holdout F=57 stands) or the lit/47 amendment scope.
- The re-selected set is corpus-specific (depends on which real cohorts + labels exist; SECL/Zhang lack condition labels, thinning XS-3).
- Not a multi-held-out-cohort validation — WMG is the only SOH-labeled real cohort (single held-out fold).

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock = commit hash). **Push.**
2. Build `code/c3_probe16_reselection.py` — apply §0.1 procedure (read gate parquets + extractability), emit attrition + re-selected set; reuse Probe-15 cascade machinery for the 200-seed WMG validation + comparison panel.
3. Run. Output `data/processed/probe16_reselection_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/69_probe16_..._result.md`. Commit + push + lock hashes.

**Cost:** analysis-only on existing parquets; selection is table logic; validation is 200 RF fits on n=37. Minutes. No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD>`
- Analyzer SHA-256: `<TBD — filled in result commit>`
- Result parquet SHA-256: `<TBD>`
- Reused: `paper2_gate_I_v2_results.parquet`, `paper2_gate_II_v2_results.parquet`, `paper2_operators_*.parquet` (unchanged)
- Result writeup: `literature/69_probe16_cascade_reselection_under_gate_result.md` — disposition `<TBD>`
