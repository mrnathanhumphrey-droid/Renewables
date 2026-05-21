# Next Session — Pickup Pointer

**Locked:** 2026-05-21 (commit 44ece58 on `main`)
**Next session goals (in order):**
1. Pull WMG 25-cell dataset (4th chemistry-form-factor group: NMC811 cylindrical 21700)
2. Add WMG to the C1 cross-chemistry hierarchical model — does NMC811_cyl cluster with NMC_cyl (SECL) or land in a new direction?
3. Begin C3 — design parameter inversion from operator residuals

---

## Where things stand

The grand-scheme reframe (mid-session, lock this in your head):

- **C2 (joint operator consistency as early-warning differential) DONE** — this is what this whole session built. Honest-partial result: direction confirmed (sign test p=0.031), magnitude small (~25 cyc), Phase 4 cluster classifier failed Khan but Zhang v2 + SECL-β passed
- **C1 (hierarchical pooling) HIT 2026-05-21** — see commit 505284f. 68.9% between-group variance on Q_max axis across 3 chemistry-form-factor groups (NMC_cyl, NMC_prism, LCO_button). Three distinct centroid directions, statistically separable. **This is the corpus-infrastructure win that opens C3.**
- **C3 (design parameter inversion) — NEXT** — with chemistry-form-factor producing 70% of variance, design parameters within a group should give detectable smaller shifts

C2 is not a paper. It's **Phase 1 of a renewables-improvement program**. The disagreement-onset metric is deployable as a BMS binary aging alarm. C1 + C3 together build the design-parameter-inversion machine that's the actual deliverable.

## What WMG data adds

WMG 25-cell dataset (Rashid 2023, Mendeley `mn9fb7xdx6/3`):
- 25 cells × NMC811 chemistry × 21700 cylindrical × 5 Ah
- EIS at 5 SOC × 3 temperatures × 5 SOH breakpoints (375 spectra)
- DOWNLOAD BLOCKED on programmatic access — Mendeley uses UI-triggered signed S3 URLs. User to grab manually:
  1. Go to https://data.mendeley.com/datasets/mn9fb7xdx6/3
  2. Click "Download All" — saves as `mn9fb7xdx6-3.zip` or similar
  3. Place in `D:/Renewables/Battery/data/wmg_25cell/`
  4. Unzip in place

**WMG adds NMC811_cyl as a 4th chemistry-form-factor group.** Critical test for C1: does NMC811_cyl cluster with NMC_cyl (SECL) or land in a separate direction? If it clusters with SECL, that's evidence chemistry+form-factor signature is robust to specific Ni:Co ratio. If it lands separately, that's evidence the framework resolves Ni:Co (or other chemistry-detail) differences.

## What to do first in the next session

1. **Verify WMG data is unzipped** at `D:/Renewables/Battery/data/wmg_25cell/`
2. **Read `Battery/literature/02_phase1_dataset_inventory.md` section D** for WMG structure spec (25 cells, breakpoint-aged, EIS at 5 SOC × 3 T × 5 SOH)
3. **Build `code/wmg_extract_features.py`** following the pattern of `code/khan_extract_and_classify.py`:
   - Q_max from capacity files (if Rashid 2023 includes capacity per-SOH-breakpoint, use directly; otherwise derive from cycling files)
   - R_ohmic + R_diff from EIS at SOC=50, T=25°C (matching the cross-cohort canonical)
4. **Extend `code/c1_cross_chemistry.py`** to include WMG_NMC811_cyl as a 4th group
5. **Report:** does the hierarchical model show 4 distinct centroids, or do NMC_cyl + NMC811_cyl collapse into one chemistry-cluster?

## Starting C3 (design parameter inversion)

After WMG lands and C1 is re-run with 4 groups, the C3 question becomes attackable:

- Within a single chemistry-form-factor group (e.g., the 19 Khan NMC_prism cells), are there documented design variations? Khan's paper has 18 cycle-condition variations + 6 calendar-condition variations — those ARE design-parameter variations in the operating-condition sense, just not material-design.
- Severson 2019 has 72 fast-charging protocols across 124 cells — also operating-condition variation
- For TRUE material-design variation (electrode thickness, electrolyte additive, separator porosity), public datasets are sparse. Synthetic data via PyBaMM is a fallback.

C3 candidate first analysis:
- Within the Khan NMC_prism cohort, do the 18 cycle-condition cells cluster by cycle-condition in operator residual space?
- If yes → "operator residuals invert cycle-condition" → proof-of-concept for design-parameter inversion at the operating-condition level
- If no → either need finer features or genuine material-design variation

The user noted in mid-session that C3 needs BOTH (a) coarse-on-existing-data AND (b) synthetic-data probes — "i think its a mix."

## State summary (so anyone reading this — including future-you — knows what's locked)

| Component | Status | Where |
|---|---|---|
| Phase 0 lit/decision | LOCKED | literature/00_phase0_lit_index.md, 01_phase0_decision_memo.md |
| Phase 1 inventory + cohort | LOCKED | literature/02_phase1_dataset_inventory.md, 03_phase1_power_calc.md |
| Phase 2 (PPC, conditional null, X1) | LOCKED | literature/04, 05, 06, 07, 10 + code/*.py |
| Phase 3 lead-time (N=7 frequentist + Bayesian) | LOCKED | literature/11, 12 + code/combined_alpha_beta_leadtime.py + code/phase3_hierarchical_pymc.py |
| Phase 4 pre-reg | LOCKED at literature/09 BEFORE held-out runs | literature/09_phase4_pre_registration.md |
| Phase 4 multi-cohort verdict | LOCKED | literature/13 (Khan), 14 (SECL-β + Zhang v1), commits 84bbbdf + 3263b96 + 5702136 |
| **C1 cross-chemistry hierarchical** | **HIT** | commit 505284f, code/c1_cross_chemistry.py |
| Second-life days-axis (null) | LOCKED | commit 44ece58, code/second_life_days_axis.py |
| WMG download | **BLOCKED on user** | data/wmg_25cell/ empty |
| C3 design parameter inversion | **NEXT** | — |

## Commits on `main` (latest 5)

```
44ece58 Second-life days-axis Q_max trajectories: cells in stable plateau, no real knee
505284f C1 HITS: cross-chemistry hierarchical pooling reveals 3 distinct centroids
126d692 Phase 3 hierarchical Bayesian (PyMC) on N=7 first-life: posterior on lead time
5702136 Zhang Cambridge v2: time-aligned per-sweep extraction, classifier PASSES size
3263b96 Phase 4 multi-cohort: SECL beta PARTIAL PASS, Zhang INVALID, longitudinal consistency
```

Remote: https://github.com/mrnathanhumphrey-droid/Renewables — all on `main`.
