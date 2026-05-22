# Next Session — Pickup Pointer

**Locked:** 2026-05-22 (commit 2ffb513 on `main`)
**Last session ended:** Paper 2 selection collapsed to INVALID per strict pre-reg; methodological negative result documented at literature/29. User then directed a diagnostic-driven amendment (NOT a result-driven re-run) and asked to compact first.

---

## Next session goal (in order)

1. **File literature/30 — Paper 2 Gate I diagnostic-driven amendment.** Replace CV-based dispersion with category-specific stability tests:
   - **Slope-like operators** (T1, T2, T3, T4, T5, C1, CE1 — trajectory + ratio operators where mean-near-zero is a real possibility): **rank-based stability test**. Per cohort: bootstrap the cell-level operator values, count fraction of bootstrap replicates where the rank-correlation of cells against any external covariate (e.g., design-condition labels, or just bootstrap-vs-bootstrap rank-correlation) exceeds a threshold. Concrete rule: "operator is rank-stable if Spearman rank correlation of original vs bootstrap re-sampled values > 0.50 in median across 1000 bootstraps."
   - **Level-like operators** (E1, E2, E3, C2, D1 — fresh-state or EIS-spectral values where mean is well-separated from zero): keep CV<0.30 OR fall back to IQR/|median|<0.30 if mean is near zero.
2. **Log the amendment in literature/28 §10** with full reasoning: CV pathology is real (mean-near-zero is a known statistical issue, not a result-driven excuse), category-specific tests are more principled than blanket-relaxing CV threshold, IQR/|median| has the same pathology if medians cross zero.
3. **Re-run Gate I under amended protocol.** Expected outcome: 4-7 operators survive, mixed across trajectory and spectral families. If 0 survive again, that's a substantive finding — the framework's operators don't pass any reasonable cross-cohort test.
4. **Then Gate II as originally planned** on whatever survives. Cascade if multi-operator survivors emerge.
5. **Document everything as protocol evolution** in literature/31 (Paper 2 v2 result): original pre-reg → CV pathology identified at literature/29 → diagnostic-driven amendment at literature/30 → re-run → final result. Pattern mirrors the cancer substrate's "Δ=+6.26 nats CI-off-zero-but-Gibbs-contingent" honest-conditional documentation.

The user's exact framing: "diagnostic-driven, not result-driven. The integrity comes from the logging, not from refusing to amend."

---

## Where things stand

| Component | Status | Commit |
|---|---|---|
| Phase 0 (lit + decision memo) | LOCKED | early-session commits |
| Phase 1 (dataset inventory + power calc + disposition) | LOCKED | early-session |
| Phase 2 (PPC, conditional null, Option X1) | LOCKED | early-session |
| Phase 3 (lead-time N=7 frequentist + Bayesian) | LOCKED | early-session |
| Phase 4 (multi-cohort held-out, Khan FAIL + SECL-β PARTIAL + Zhang v2 PASS) | LOCKED | early-session |
| C1 cross-chemistry hierarchical (3 groups) | LOCKED | 505284f |
| C1 cross-chemistry hierarchical (4 groups, +WMG) | LOCKED | ce400df |
| Second-life days-axis null | LOCKED | 44ece58 |
| C3 Probe 1 (Khan exploratory, SOC range hit) | LOCKED | a388308 |
| C3 pre-reg for Probes 2+3 | LOCKED | 1ef1b94 |
| C3 Probe 2 (Severson H2 PASS pooled, partial within-batch) | LOCKED | ed997e8 |
| C3 Probe 3 (WMG H3 NULL by p, F above floor) | LOCKED | ed997e8 |
| C3 Probe 4 pre-reg (PyBaMM synthetic material-design) | LOCKED | d03a558 |
| C3 Probe 4 (H4 STRONG SUPPORT, 2/3 design params PASS) | LOCKED | 399e572 |
| C3 Probe 2 amendment pre-reg (Severson alt-axes) | LOCKED | 3fb179a |
| C3 Probe 2v2 (alt-axes H5 WEAK; partial-batch is axis-general) | LOCKED | 9e87966 |
| C3 Probe 5 pre-reg (PyBaMM uniform aging) | LOCKED + amendment | 93e4f03 + e3b12c6 |
| C3 Probe 5 (H6 SUPPORTS Probe 4 ROBUSTNESS; 3/3 PASS) | LOCKED | dda4bdc |
| C3 Probe 6 pre-reg (noise injection threshold test) | LOCKED | 4a3e932 |
| C3 Probe 6 (H7 SUPPORTS NOISE EXPLANATION; threshold at typical academic noise) | LOCKED | 6fc2d92 |
| Paper 2 operator catalog pre-reg | LOCKED | 13e9f80 |
| Paper 2 selection pre-reg + §6 amendment | LOCKED | 7fae62a + 153fbd3 |
| **Paper 2 selection result (INVALID per strict pre-reg)** | **LOCKED** | **2ffb513** |
| Paper 2 v2 amendment (Gate I diagnostic-driven) | **NEXT** | — |
| Paper 2 v2 re-run + writeup | NEXT | — |

## Paper 2 result detail (literature/29) for context

- 12 candidates → Gate I → 1 (E1 only)
- 1 candidate → Gate II → 0 (E1 only computable on Khan; can't pass 2-of-3 cohort rule)
- Cascade INVALID per pre-reg §7

CV-based Gate I dropped 11 of 12. Most attrition driven by:
- **CV pathology** on near-zero-mean trajectory operators (T1-T5, C1)
- **Data unavailability** for E3, CE1, D1 (extraction infra gaps)
- Genuine cross-cohort instability for some operators

E1 had AUC=1.000 on Khan (perfect aging-condition separation) but failed Gate II because PyBaMM and Severson lack EIS data.

## Pattern of documentation to follow (per user direction)

The user explicitly cited the cancer substrate's "Δ=+6.26 nats CI-off-zero-but-Gibbs-contingent" documentation as the model — conditional, honest, fully audited. The amendment in literature/30 + re-run + writeup at literature/31 should:

1. **Open with the diagnostic.** What was wrong with Gate I as locked? CV near-zero-mean pathology.
2. **State the amendment with explicit before/after text.** Slope-like operators get rank-based stability; level-like keep CV.
3. **Justify category-specific over blanket-relaxation.** IQR/|median| has same pathology; trajectory vs spectral operators are statistically different beasts.
4. **Re-run and report,** with attrition tracked alongside the original Gate I result for transparency.
5. **Frame as protocol evolution,** NOT as "Gate I was wrong so we changed it to make things pass."

## Outstanding items NOT covered above

- Paper 2 noise-injection analog of C3 Probe 6 (test cascade's noise robustness if cascade emerges)
- Paper 2 + Paper 1 cross-comparison writeup
- Methodology corpus paper integrating the C2 battery substrate alongside sports / SPX / cancer / hydrology / gun violence

These are NEXT-NEXT-session work.

## Repo state

Branch `main` at `2ffb513`. Push to `origin/main` synced. WMG, Severson FastCharge.zip, all parquets present in `data/`. All code in `code/`. All literature in `literature/00`–`literature/29`.

Total commits in this session lineage: 12+ (from `505284f` C1 onward through `2ffb513` Paper 2 INVALID).
