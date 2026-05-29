# C3 Probe 15 — Cross-Substrate-as-Primary-Gate Redesign (Paper-3-equivalent) Pre-Registration

**Status:** LOCKED 2026-05-29 at commit `<TBD>`. No Probe 15 analysis had fired at lock time. Scoping (read-only inspection of operator parquets + extractability map) was done before drafting (§0.2); no cascade was trained.
**Date drafted:** 2026-05-29
**Authored:** Claude
**Repo target on lock:** `Battery/literature/66_probe15_crosssubstrate_primary_gate_prereg.md`
**Prior:** Paper 2 (lit/35) closed CASCADE CROSS-SUBSTRATE NULL — the amended cascade's dominant operator C2 alone failed to discriminate WMG terminal-SOH bins (F=0.92, p=0.58). lit/35 §6 named the fix: "future selection methodology should include cross-substrate validation as a **primary gate**, not a secondary descriptive test." This probe operationalizes that. HEAD `c840543`.

## 0. Motivation — does a cross-substrate-primary gate recover transfer, or is the substrate gap fundamental?

Paper 2's cross-substrate test was restricted to C2 **because the other 6 cascade operators are non-extractable on WMG's snapshot data** (lit/35 §5). The proposed fix is to make **cross-substrate extractability + real-cohort discrimination a primary selection gate**, dropping operators that pass the (permissive) within-substrate Gates I/II but cannot be computed or do not transfer across substrates. This probe (a) formalizes that gate and reports the operator set it admits, and (b) tests whether the admitted set transfers to the held-out real cohort (WMG) where C2-alone failed.

In **RMD-SRC** terms: a predictive-transfer (RMD_F4) redesign of the operator-selection methodology, gated by the multi-seed stability discipline (the 9b lesson).

## 0.1 The cross-substrate-primary gate (definition, LOCKED)

An operator passes the gate iff it is **extractable (≥3 finite values) on a held-out real-cell cross-substrate cohort of a different measurement modality (snapshot EIS)** AND on ≥2 real-cell training cohorts. The held-out cohort is **WMG** (real NMC811, snapshot EIS, the only corpus cohort with an explicit SOH label, `soh_eis`).

## 0.2 What the gate admits (verified read-only before drafting)

Operator extractability across cohorts (≥3 finite), from the `paper2_operators_*.parquet` files:

| operator (category) | PyBaMM | Khan | SECL | Zhang | Severson | **WMG** |
|---|---|---|---|---|---|---|
| T1/T2/T3 capacity-traj | ✓ | T1,T2 | ✓ | ✓ | ✓ | ✗ |
| T4/T5 impedance-traj | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| E1 ohmic-intercept (EIS) | ✗ | ✓ | ✓ | ✓ | ✗ | **✓** |
| E2 charge-transfer-radius (EIS) | ✗ | ✓ | ✓ | ✓ | ✗ | **✓** |
| E3 diffusion-slope (EIS) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| C1 R-growth-per-Q-lost | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| C2 R_DC/R_total | ✓ | ✓ | ✓ | ✓ | ✗ | **✓** |
| CE1 / D1 | ✗/✗ | ✗ | ✗ | ✗ | CE1 | ✗ |

**The gate (extractable on WMG) admits exactly {E1_ohmic_intercept, E2_charge_transfer_radius, C2_R_DC_to_R_total}.** All five trajectory operators (T1–T5) and the differential operators are dropped — they are not computable on snapshot data. This is the central methodological finding regardless of the transfer outcome: a cross-substrate-primary gate collapses the cascade to the snapshot-EIS operator set.

The cohorts where all three gated operators co-exist (the gate's training set) are the real-EIS cohorts **{Khan (n=19), SECL (n=10), Zhang (n=8)}** = **n=37**. (PyBaMM and Severson lack E1/E2; excluded — exactly the gate's intent.)

## 1. Hypotheses (LOCKED)

**H15-main (gate recovers transfer):** an RF cascade on the gated set **{E1, E2, C2}** trained on {Khan, SECL, Zhang} produces a leaf-PCA representation that discriminates WMG terminal-SOH bins — WMG PERMANOVA pseudo-F **robustly > 3.0** (median AND 2.5th-percentile across 200 RF seeds) AND reference-seed (random_state=42) permutation **p < 0.05** — where the matched **{C2}-only** cascade (same training cohorts) is NULL. I.e., adding the cross-substrate-extractable EIS-spectral operators E1+E2 recovers the transfer C2 alone lacked.

**H15-null:** {E1, E2, C2} is also NULL (median F ≤ 3 or p ≥ 0.05). This would mean even the **full** cross-substrate-extractable operator set does not transfer to WMG — strengthening lit/35 from "C2 alone fails" to "the entire snapshot-EIS-extractable set fails." The cross-substrate-primary gate would then be a clean selection methodology that correctly identifies the transferable operator set, but that set still does not transfer on this cohort → the binding limit is the substrate gap (cell format / chemistry / cohort), not operator selection. (Parallels the transference and SOH-triage arc termini: method/selection sound, cohort is the limit.)

## 2. Cohort + data (LOCKED)

- **Source (reused unchanged):** `paper2_operators_{khan,secl,zhang,wmg}.parquet` + `data/khan_2025/cell_conditions.csv` (Khan aging labels).
- **Training set:** {Khan, SECL, Zhang}, n=37 (the gate's real-EIS cohorts).
- **Held-out cross-substrate test:** WMG, n=19, terminal-SOH bins {80, 85, 90, 95} (`soh_eis`; counts {5,5,4,5} per lit/35, all ≥3 — no fallback expected).
- **Training labels (heterogeneous per-cohort, mirroring lit/35's pb/kh/sv scheme):** Khan → `kh_{aging_type}` (cycle/calendar/excluded, from the conditions CSV); SECL → single class `secl`; Zhang → single class `zhang`. (SECL/Zhang have no internal condition sweep — each is its own class. The labels are supervision to grow forests that partition the {E1,E2,C2} geometry; the transfer claim rests on WMG SOH clustering, exactly as in lit/35.)
- **Independent unit:** physical cell. WMG labels (`soh_eis`) are used ONLY in the final transfer test, never in selection — extractability is a structural (non-label) property, so the gate is not circular w.r.t. the SOH signal.

## 3. Method (LOCKED — mirrors `paper2_cascade_v2_wmg.py` exactly, generalized to a feature list)

Per feature set ∈ {**{C2}** (matched baseline), **{E1,E2,C2}** (gated set)}:
1. Build training matrix on {Khan,SECL,Zhang}; mean-impute any missing; StandardScaler (fit on train).
2. RF: `n_estimators=500, max_depth=4, min_samples_leaf=5, class_weight='balanced'` (lit/35 hyperparameters). 5-fold CV OOF accuracy (sanity / F1).
3. `rf.apply` → leaf indices for train + WMG; StandardScaler on combined leaves; `PCA(n_components=min(10, n_leaf_cols))` fit on combined; extract WMG embedding.
4. PERMANOVA (Euclidean, 10,000 perms) on the WMG embedding labeled by SOH bins → pseudo-F + p. (Identical to lit/35.)
5. **Multi-seed stability (the 9b gate):** repeat steps 2–4 for RF `random_state` ∈ {0..199}; record the WMG pseudo-F **distribution** (median, 2.5/97.5 pct, fraction > 3.0). Headline p computed at the reference seed 42 with 10,000 perms.

## 4. Falsifiers (LOCKED)

**P-Probe15_F1 (cascade learns — sanity):** RF 5-fold CV OOF accuracy > chance (1/n_classes) on the training set for both feature sets. Fail → cascade is degenerate → INVALID (a WMG NULL would be uninterpretable).

**P-Probe15_F2 (matched-baseline NULL):** the {C2}-only cascade **on the same {Khan,SECL,Zhang} training set** must reproduce a NULL (F not robustly > 3). Confirms the comparison is apples-to-apples and the published NULL is not a training-cohort artifact. (If C2-matched unexpectedly PASSES, that itself is the finding — flag it; the gated comparison is then re-interpreted.)

**P-Probe15_F3 (multi-seed stability — THE gate, per 9b):** H15-main is judged on the 200-seed F distribution, NOT the single seed=42. If seed=42 gives F>3 but the distribution median/2.5pct does not clear 3.0, that is a single-seed artifact → FAIL. (Same discipline that killed the 9b PCA-3 finding and the SOH drop-ohmic hint, and confirmed the GITT-pr finding.)

**P-Probe15_F4 (WMG binning):** SOH bins {80,85,90,95} each ≥3 cells; else median-split fallback (documented). No silent re-binning.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **CROSS-SUBSTRATE-GATE-RECOVERS** | H15-main PASS ({E1,E2,C2} median F>3 AND 2.5pct>3 AND ref-seed p<0.05) AND F2 ({C2}-matched NULL) | The cross-substrate-primary gate, by admitting the EIS-spectral operators E1+E2, recovers cross-substrate SOH transfer that C2-alone lacked. Promote the gate as a real selection-methodology improvement; the Paper-2 cascade should be re-selected under it. |
| **CROSS-SUBSTRATE-STILL-NULL** | {E1,E2,C2} NULL (median F≤3 or p≥0.05) | Even the full snapshot-EIS-extractable operator set does not transfer to WMG. The gate is a sound selection methodology (correctly isolates the transferable set) but the binding limit is the substrate gap, not operator selection. Strengthens lit/35 to the operator-set level. Arc terminus parallel. |
| **MATCHED-BASELINE-NOT-NULL** | F2 fails ({C2}-matched on {Khan,SECL,Zhang} PASSES) | The published NULL was partly a training-cohort artifact (PyBaMM+Severson dilution). Re-interpret; the gate's value is then in the training-cohort change, not E1+E2. |
| **PROBE 15 INVALID** | F1 fails (cascade doesn't learn) | Degenerate cascade. Debug. |

## 6. What Probe 15 does NOT establish

- Not a real-cell SOH-deployment claim — WMG n=19, one chemistry, one snapshot protocol.
- A RECOVERS verdict promotes the *selection methodology*, not a new amendment scope; full re-selection of the Paper-2 cascade under the gate would be a follow-up.
- The gate's admitted set is corpus-specific (depends on which real cohorts exist); E3/CE1/D1 are dropped here for lack of any extractable cohort, not because they are inherently non-transferable.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock anchor = commit hash). **Push.**
2. Build `code/c3_probe15_crosssubstrate_gate.py` — reuse `paper2_cascade_v2_wmg.py` machinery (RF + leaf-PCA + PERMANOVA), generalized to a feature list + {Khan,SECL,Zhang} training + 200-seed multi-seed loop; run both {C2} and {E1,E2,C2}.
3. Run. Output `data/processed/probe15_crosssubstrate_gate_results.parquet`.
4. Apply §5 disposition + §4 falsifiers. Write `literature/67_probe15_..._result.md`. Commit + push + lock hashes.

**Cost:** analysis-only on existing parquets; 200 RF fits × 2 feature sets on n=37 (fast) + PERMANOVA. Minutes. No simulation, no Modal.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata:**
- Lock commit: `<TBD>`
- Analyzer SHA-256: `<TBD — filled in result commit>`
- Result parquet SHA-256: `<TBD>`
- Reused operator parquets: `paper2_operators_{khan,secl,zhang,wmg}.parquet` (unchanged)
- Reference baseline: lit/35 C2-only(PyBaMM+Khan+Severson) WMG F=0.921, p=0.576 NULL
- Result writeup: `literature/67_probe15_crosssubstrate_primary_gate_result.md` — disposition `<TBD>`
