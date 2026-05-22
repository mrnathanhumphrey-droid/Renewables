# Next Session — Pickup Pointer

**Locked:** 2026-05-22 (commit `d3b1662` on `main`)
**Last session ended:** Paper 2 dual-result published. Strict-pre-reg verdict (literature/29) PAPER 2 INVALID stands. Amended-protocol verdict (literature/31) PAPER 2 PARTIAL REPLICATION via diagnostic-driven Gate I amendment (literature/30) + 7-operator RF cascade with PRIMARY PyBaMM-holdout F=57.26, p=0.0001, SECONDARY WMG vacant.

---

## Where things stand

| Component | Status | Commit |
|---|---|---|
| Phase 0-4 + C1 + C2 + 6 C3 Probes (Paper 1) | LOCKED | 2ffb513 base |
| Paper 2 operator catalog pre-reg (literature/27) | LOCKED | 13e9f80 |
| Paper 2 selection pre-reg + §10 amendments | LOCKED | 7fae62a + 153fbd3 + 3ad6c5c |
| Paper 2 strict-pre-reg result (INVALID, literature/29) | LOCKED | 2ffb513 |
| Paper 2 Gate I diagnostic-driven amendment (literature/30) | LOCKED | 3ad6c5c |
| **Paper 2 amended-protocol result (PARTIAL REPLICATION, literature/31)** | **LOCKED** | **d3b1662** |

The Paper 2 narrative is closed for now: both pre-reg-honest verdicts are published, audited, and pushed. The methodological lesson (blanket dispersion metrics are ill-suited to mixed slope-and-level catalogs; category-stratify ex ante) is in the corpus.

## Open follow-ups (NOT pre-registered)

1. **Tighter rank-stability threshold.** The locked ρ_median ≥ 0.50 turned out to be far below the empirical floor (0.994-1.000). A future Paper-2-equivalent pre-reg could lock ρ_median ≥ 0.85 or use split-half rank concordance. Document as Paper 3 design consideration.

2. **WMG cross-substrate generalization.** Under the current §10 first amendment, WMG SECONDARY is vacant because no E1-E3 survived Gate II. A new pre-reg broadening the WMG restriction to "any EIS-derived survivor" (which would admit C2) would let WMG SECONDARY run. This must be a NEW pre-reg, locked before any C2-on-WMG analysis touches the data with PERMANOVA. The exploratory C2 stats in literature/31 §5 (mean 0.929, sd 0.025, range [0.872, 0.971], soh_eis range 80-95%) are descriptive only.

3. **Paper 2 noise-injection analog (Probe-6-style for cascade).** Test cascade-robustness under instrumentation noise (Probe 6 demonstrated 0.5% Q / 15% R_DC / 20% R_total noise collapses Paper 1 trajectory PERMANOVAs). Same noise injection on amended cascade: does F=57.26 survive? Pre-register first.

4. **True cross-substrate cascade.** Train on PyBaMM-train + Khan + Severson; validate on a real-cell substrate OTHER than the training cohorts (e.g., a future SECL second-life slice, or a new cohort). This would be the cleanest test of the framework's real-world claim. Substrate not yet identified.

5. **Cross-paper integration writeup.** Paper 1 (independence-framework) + Paper 2 (noise-robust cascade) side-by-side methodology paper. How the framework evolves from independence-Mahalanobis to RF-cascade when the operator catalog becomes mutually coupled.

6. **Methodology corpus integration.** Battery substrate alongside sports / SPX / cancer / hydrology / gun violence in the cross-substrate paper.

## Repo state

Branch `main` at `d3b1662`. Push to `origin/main` synced. All literature 00-31 present. All code in `code/`. All parquets in `data/processed/` (gitignored). New artifacts from this session:

- `code/paper2_gate_I_v2.py` — amended Gate I (rank-stability + CV/IQR fallback)
- `code/paper2_gate_II_v2.py` — Gate II on amended survivors (logic unchanged from v1)
- `code/paper2_cascade_v2.py` — RF cascade + PCA embedding + PERMANOVA on PyBaMM-holdout PRIMARY + WMG SECONDARY (vacant)
- `literature/30_paper2_gate_I_amendment.md` — diagnostic-driven amendment with falsification-resistance check
- `literature/31_paper2_amended_result.md` — dual-result protocol-evolution document
- `data/processed/paper2_gate_I_v2_results.parquet`
- `data/processed/paper2_gate_II_v2_results.parquet`
- `data/processed/paper2_cascade_v2_summary.pkl`
- `data/processed/paper2_cascade_v2_importances.parquet`

## Key result numbers (for citation)

- Amended Gate I: 8 of 12 operators survive (T1-T5, C1, C2, E1)
- Amended Gate II: 7 of 8 (E1 fails cohort-coverage; T1-T5 + C1 + C2 survive)
- Cascade 5-fold OOF accuracy: 0.684 (chance = 1/14 ≈ 0.071)
- PRIMARY PERMANOVA (PyBaMM-holdout, n=36): F=57.26, p=0.0001 → PASS
- Dominant cascade operators: C2 (27%), T1 (20%), T4 (16%), T5 (14%), T2 (12%)
- Verdict: PAPER 2 PARTIAL REPLICATION (PRIMARY PASS; SECONDARY vacant)
