# C3 Probe 16 — Full Cascade Re-Selection Under the Cross-Substrate-Primary Gate RESULT

**Status:** COMPLETE. Disposition = **XS-GATE-YIELDS-TRANSFERABLE-CASCADE.** The cross-substrate-primary gate, run as a reproducible procedure on all 12 catalog operators, re-selects **{E1_ohmic_intercept, C2_R_DC_to_R_total}** — keeping the EIS-spectral operator the within-substrate Gate II discards for cohort-coverage, dropping all trajectory operators — and the re-selected cascade transfers robustly to WMG terminal-SOH (200-seed median F=3.72 [3.35, 4.16], p=0.019) where the within-substrate 7-operator cascade is structurally non-transferable (only 1 of 7 operators extractable on snapshot data).
**Date:** 2026-05-29
**Authored:** Claude
**Pre-reg:** `literature/68_probe16_cascade_reselection_under_gate_prereg.md` (lock `55beb41`).
**Prior:** Probe 15 (lit/66+67) showed lit/35's cross-substrate NULL was a training-cohort artifact and that modality-matched {C2}/{E1,E2,C2} transfer to WMG. This formalizes the gate as a selection procedure and validates the procedurally re-selected cascade — the Paper-3 deliverable.

---

## 0. One-line result

Applying the locked XS-primary procedure (extractability on held-out snapshot WMG [PRIMARY] → modality-matched stability → modality-matched discrimination) to all 12 operators yields the re-selected set **{E1, C2}** (12 → XS-1: {E1,E2,C2} → E2 dropped for stability → {E1, C2}). All five trajectory operators (T1–T5) fail XS-1 (non-extractable on snapshot data); E1 — which the existing Gate II discards because it is finite on only 1 of 3 within-substrate cohorts despite Khan AUC=1.000 — is *kept* by the modality-matched gate. The re-selected {E1,C2} cascade transfers robustly to WMG SOH (median F=3.72, p=0.019, robust across 200 RF seeds), beating C2-only (3.22) and approaching the full {E1,E2,C2} (3.82). The within-substrate 7-operator cascade has only C2 extractable on WMG (F2 PASS) — it cannot transfer by construction. **The cross-substrate-primary gate is a validated selection methodology: it produces a transferable cascade where within-substrate-only selection structurally cannot.**

## 1. Falsifier / hypothesis results

| Test | Locked criterion | Result | Verdict |
|---|---|---|---|
| **H16-selection** | EIS kept, trajectory dropped | re-selected {E1, C2}; T1–T5 all dropped at XS-1 | **YES** |
| **F1** procedure non-degenerate | non-empty, all WMG-extractable | {E1, C2}, both WMG-extractable | **PASS** |
| **F2** within-substrate non-transferable | ≤1 of Gate-I+II set WMG-extractable | 7-op set {C1,C2,T1–T5} → only **C2** extractable | **PASS** |
| **H16-main** re-selected transfers | 200-seed median>3 AND 2.5pct>3 AND p<0.05 | median **3.72** [3.35, 4.16], p=**0.019** | **PASS** |
| **F3** multi-seed stability | judged on distribution | 200-seed; 2.5pct=3.35>3 | **PASS** (robust) |
| **F4** reproducible procedure | deterministic from gate parquets | table logic, no RNG in selection | **PASS** |

## 2. The re-selection procedure + attrition (all 12 operators)

| operator | WMG-extractable | XS-1 | XS-2 stability | Khan AUC | XS-3 | **re-selected** |
|---|---|---|---|---|---|---|
| T1–T5 (trajectory) | ✗ | ✗ | (pass) | 0.73–0.94 | (pass) | **no** (XS-1) |
| E1_ohmic_intercept | ✓ | ✓ | ✓ | 1.000 | ✓ | **YES** |
| E2_charge_transfer_radius | ✓ | ✓ | ✗ (Gate-I 2/3) | — | — | **no** (XS-2) |
| E3_diffusion_slope | ✗ | ✗ | ✗ | — | — | no |
| C1_R_growth_per_Q_lost | ✗ | ✗ | ✓ | 0.971 | ✓ | **no** (XS-1) |
| C2_R_DC_to_R_total | ✓ | ✓ | ✓ | 0.971 | ✓ | **YES** |
| CE1 / D1 | ✗ | ✗ | — | — | — | no |

**Attrition: 12 → XS-1 (snapshot-extractable) {E1, E2, C2} → XS-2 (stability) drops E2 → XS-3 (discrimination) → re-selected {E1, C2}.** The PRIMARY filter (XS-1 extractability on a snapshot cohort) is the binding one — it alone removes 9 of 12 operators, including all trajectory operators. E2 is the one further casualty (unstable, Gate-I 2/3 — consistent with the original Gate I).

## 3. The key methodological finding: within-substrate selection discards the transferable operators

The existing Gate II rejected **E1** despite **Khan AUC=1.000** — purely because E1 is finite on only 1 of Gate II's 3 cohorts ({PyBaMM synthetic, Khan, Severson EIS-less}), failing the ≥2-cohort requirement. So the within-substrate pipeline *systematically discards the EIS-spectral operators that are exactly the ones extractable on a real-cell snapshot* — and keeps the trajectory operators that are not. The resulting 7-op cascade {C1, C2, T1–T5} has **only C2 extractable on WMG** (F2 PASS), which is why lit/35 could only test C2 and found NULL. The cross-substrate-primary gate inverts this: by requiring snapshot-extractability and scoring discrimination on modality-matched real cohorts, it keeps E1, drops T1–T5, and yields a cascade that transfers.

## 4. Validation panel (train {Khan,SECL,Zhang} n=37, test WMG n=19, 200 RF seeds)

| feature set | WMG PERMANOVA F median [2.5, 97.5] | ref-seed p | robust? |
|---|---|---|---|
| **{E1, C2} (re-selected, procedural)** | **3.72 [3.35, 4.16]** | **0.019** | **PASS** |
| {C2} only (lit/35 operator, matched-trained) | 3.22 [3.03, 3.41] | 0.024 | PASS |
| {E1, E2, C2} (Probe-15 max-EIS set) | 3.82 [3.49, 4.20] | 0.017 | PASS |

E1 contributes genuine lift over C2-alone (3.22 → 3.72); the unstable E2, correctly dropped by the procedure, would have added only marginally more (→3.82). The **principled re-selected set {E1, C2}** captures essentially all the transferable signal while excluding the operator that fails the stability gate. This is the satisfying outcome: the reproducible procedure, applied blind, lands on a stable transferable cascade.

## 5. Disposition (per lit/68 §5)

**XS-GATE-YIELDS-TRANSFERABLE-CASCADE.** H16-selection YES (EIS kept, trajectory dropped), F1 non-degenerate, F2 PASS (within-substrate set structurally non-transferable — 1/7 WMG-extractable), H16-main PASS (re-selected {E1,C2} robust median F=3.72, p=0.019). The cross-substrate-primary gate is validated as a selection methodology that produces a cross-substrate-transferable cascade.

## 6. What Probe 16 establishes / does not

**Establishes (the Paper-3 deliverable):**
- A **reproducible cross-substrate-primary selection procedure** that, applied to the catalog, re-selects {E1, C2} and **transfers to a held-out real-cell snapshot cohort** (WMG SOH, F=3.72, p=0.019, 200-seed robust) — where the within-substrate-only 7-op cascade is structurally non-transferable (1/7 extractable).
- The concrete **mechanism of the original failure:** within-substrate Gate II discards EIS-spectral operators (E1, Khan AUC=1.0) for cohort-coverage reasons (synthetic + EIS-less cohorts), yielding a trajectory-dominated cascade that cannot survive snapshot transfer.
- The procedure self-consistently drops the unstable E2 and keeps the {E1, C2} that carries the transferable signal.

**Does NOT establish:**
- Strong/deployable transfer — effects modest (F just above 3), WMG n=19, single held-out SOH cohort.
- Generalization beyond NMC811 / snapshot EIS, or beyond this corpus's cohort+label availability (SECL/Zhang lack condition labels, thinning XS-3 to Khan).
- Any change to Paper-2 within-substrate results (PyBaMM-holdout F=57 stands) or the lit/47 amendment scope.
- A multi-cohort held-out validation (only WMG carries SOH labels).

## 7. RMD-SRC framing

A selection-methodology (validation-layer) redesign validated by predictive transfer (RMD_F4). The cross-substrate-primary gate is the corrective: within-substrate selection (Gates I/II) optimized for synthetic+trajectory discrimination and structurally excluded the operators that transfer to real snapshot data. Making cross-substrate extractability the PRIMARY filter, with modality-matched stability/discrimination, re-selects {E1, C2} and yields robust (200-seed) transfer. The whole cross-substrate arc (Probe 15 → 16) converts lit/35's "CROSS-SUBSTRATE NULL" into "transferable under correct, cross-substrate-primary selection + modality-matched training," with honest modest-effect caveats.

---

**Lock metadata:**
- Pre-reg lock commit: `55beb41`
- Result commit: `<recorded in this commit>`
- Analyzer SHA-256: `62a45d9c1052a00c06f08bf5bd186042d545ff7490911671df9e362d5fd17245`
- Result parquet SHA-256: `a19f9527e98ed9844b1b9732bbc0e3006fcab542407c993b242a420bfef2a521`
- Reused: `paper2_gate_I_v2_results.parquet`, `paper2_gate_II_v2_results.parquet`, `paper2_operators_*.parquet` (unchanged)

## 8. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-29 | XS-3 discrimination scored on Khan AUC only (not SECL/Zhang). | SECL/Zhang operator parquets carry no condition labels; Khan is the only real-EIS cohort with design/aging axes. Thin but honest; the PRIMARY filter (XS-1) and XS-2 do the heavy lifting. |
