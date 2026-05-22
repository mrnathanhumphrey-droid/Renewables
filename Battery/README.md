# Battery — Multi-Operator Disagreement-Onset Framework

A research substrate for renewables-improvement: deploy a joint-operator
consistency check as an early-warning indicator of battery aging, and use
the residual-direction structure of the disagreement as the signal that
inverts to chemistry / form-factor / design-parameter differences.

This README is a state-of-the-work pointer. The decision memos in
[literature/](literature/) are the canonical record.

## What this study is, at the highest level

Battery aging is usually summarized by capacity fade (Q_max trajectory).
The framework here adds two more independent operators (EIS R_ohmic, EIS R_diff
— at fixed SOC and temperature; HPPC R_DC and time-constant in operator
triad β) and asks: **when does the joint behavior of these operators stop
being consistent with the healthy-cell joint null?** That disagreement-onset
is the signal.

Two layers of result:

1. **C2 — disagreement-onset as an early-warning differential**
   On the cells we can score, the joint disagreement onset precedes the
   capacity knee by a small but statistically nonzero margin (sign test
   p=0.031 on N=7, ~25 cycles median lead, frequentist 95% LCB ~+10 cyc,
   Bayesian hierarchical posterior 95% LCB +X cyc — see literature/12).
   Honest-partial: smaller than the original 50-cycle pre-reg floor.

2. **C1 — cross-chemistry hierarchical pooling**
   Per-cell residual-direction unit vectors cluster by chemistry-form-factor.
   With 4 groups (NMC_cyl SECL, NMC_prism Khan, LCO_button Zhang,
   NMC811_cyl WMG): **76.1% of Q_max-axis variance is between-group**
   (95% CI [39.7%, 95.4%]). Group centroids point in distinguishable
   directions on the residual unit sphere. **C1 HIT.**

C1 hitting opens **C3 — design-parameter / operating-condition inversion from
operator residuals**, which is the actual deliverable of the program. C3 has
now been probed across 3 cohorts:

3. **C3 Probe 1 (Khan within-cohort, exploratory)** — SOC range / upper-voltage
   cutoff separates Khan cycle-aged cells at pseudo-F = 8.79, p = 0.036
   (10000 perms). Temperature does NOT separate the same cells (F=2.17,
   p=0.272). Motivated the C3 pre-registration. (literature/15)
4. **C3 Probe 2 (Severson within-cohort, pre-registered)** — pooled
   PERMANOVA on N=139 cells across 3 batches: pseudo-F = 31.7, p = 0.0001
   on first-step C-rate. **H2 PASS** per pre-reg §5. But batch-stratified
   robustness check shows only 1 of 3 batches independently replicates;
   pooled signal is partly batch-driven. (literature/17)
5. **C3 Probe 3 (WMG within-cohort, pre-registered framework coherence)** —
   pseudo-F = 5.30 (above 3.0 floor) but p = 0.067 — **H3 NULL** by strict
   pre-reg, underpower-failure not signal-absence. (literature/18)
6. **C3 Probe 4 (PyBaMM synthetic material-design, pre-registered)** —
   108 synthetic LGM50 cells in L9 Taguchi factorial; cathode thickness PASS
   (F=12.37 p=0.003), transference number PASS (F=50.57 p=0.0001), particle
   radius NULL (centroids essentially identical). **H4 STRONG SUPPORT** per
   pre-reg §8. First validation of C3's material-design inversion claim on
   data where ground truth is known. (literature/19 pre-reg, literature/20 result)
7. **C3 Probe 2 amendment (Severson alternative design axes, pre-registered)** —
   3 alt axes (last-step C-rate, SOC handoff, severity score) tested per
   literature/21. All 3 show the same pattern as first-step C-rate: pooled
   signal exists for 2 of 3, but Batch 2 within-batch fails on ALL 3.
   **H5 WEAK** per pre-reg §6. The partial-batch failure in Probe 2 is
   axis-general (cohort property), not axis-specific. Raised the
   magnitude-confound hypothesis. (literature/22)
8. **C3 Probe 5 (PyBaMM uniform-aging-extent magnitude-confound test, pre-registered)** —
   108 synthetic cells re-anchored at uniform per-cell SOH 0.92 (mean SOH
   0.918, sd 0.011 — tight clustering). **H6 SUPPORTS PROBE 4 ROBUSTNESS**:
   all 3 design parameters PASS, including particle radius which was NULL
   in Probe 4 (now F=9.6, p=0.003). **Magnitude-confound hypothesis
   disconfirmed.** Severson Batch 2's null is not explained by uniform
   aging extent. Cause must be real-cell variability sources (measurement
   noise, instrument drift, real chemistry heterogeneity, batch-to-batch
   shifts) that synthetic PyBaMM cells don't reproduce. (literature/23
   pre-reg + amendment, literature/24 result)

Joint C3 status across all 6 pre-registered analyses: **synthetic-validated
under TWO anchor strategies (Probes 4 + 5, total 3/3 design params PASS
under uniform anchor); real-cohort mixed (Probe 2 PASS pooled; Probes 3,
2v2 fail on real cohorts due to noise sources NOT modeled in synthetic).**
Promotion to paper-ready claim now hinges on real-cell experimental validation
under controlled aging extent. Framework methodology is sound.

## Current state (2026-05-21)

| Component | Status | Location |
|---|---|---|
| Phase 0 (lit review + decision memo) | LOCKED | literature/00, 01 |
| Phase 1 (dataset inventory + power calc + cell disposition) | LOCKED | literature/02, 03, 08 |
| Phase 2 (PPC, conditional null, Option X1 cross-lifecycle) | LOCKED | literature/04, 05, 06, 07, 10 |
| Phase 3 (lead-time, N=7 frequentist + Bayesian) | LOCKED | literature/11, 12 |
| Phase 4 (multi-cohort held-out classification) | LOCKED | literature/09 (pre-reg), 13 (Khan FAIL), 14 (SECL-β PARTIAL PASS, Zhang v2 PASS) |
| C1 cross-chemistry hierarchical (3 groups) | LOCKED | commit 505284f |
| C1 cross-chemistry hierarchical (4 groups w/ WMG) | LOCKED | commit ce400df |
| Second-life days-axis null | LOCKED | commit 44ece58 |
| C3 probe 1 (Khan within-cohort, exploratory) | LOCKED — SOC range hit, pseudo-F 8.79 p=0.036 | literature/15, commit a388308 |
| C3 pre-reg probes 2+3 (locked) | LOCKED | literature/16, commit 1ef1b94 |
| C3 probe 2 (Severson within-cohort) | LOCKED — H2 PASS pooled (F=31.7 p=0.0001) but partial within-batch replication | literature/17 |
| C3 probe 3 (WMG within-cohort, framework coherence) | LOCKED — H3 NULL by p, effect size above floor (underpower) | literature/18 |
| C3 pre-reg probe 4 (PyBaMM synthetic, locked) | LOCKED | literature/19, commit d03a558 |
| C3 probe 4 (PyBaMM material-design synthetic) | LOCKED — **H4 STRONG SUPPORT** (2/3 design params PASS: cathode thickness F=12.4 p=0.003; transference F=50.6 p=0.0001; particle radius NULL) | literature/20 |
| C3 probe 2 amendment pre-reg (Severson alt-axes) | LOCKED | literature/21, commit 3fb179a |
| C3 probe 2v2 (Severson alt-axes result) | LOCKED — **H5 WEAK**: last_step_C + severity POOLED-ONLY PASS (Batch 2 fails); soc_handoff NULL. Partial-batch failure is axis-general | literature/22 |
| C3 probe 5 pre-reg (PyBaMM uniform anchor magnitude-confound test) | LOCKED + amended (target SOH 0.85 → 0.92) | literature/23, commit 93e4f03 + amendment e3b12c6 |
| C3 probe 5 (PyBaMM uniform anchor result) | LOCKED — **H6 SUPPORTS PROBE 4 ROBUSTNESS**: all 3 params PASS (cathode F=7.2 p=0.017; transference F=23.9 p=0.0001; particle radius F=9.6 p=0.003 — was NULL in Probe 4). Magnitude-confound disconfirmed | literature/24 |

## Cohorts in the cross-chemistry C1 model

| Cohort | Chemistry / form factor | N (cells contributing residual vector) | Design |
|---|---|---|---|
| SECL (Stanford, ours) | NMC / Si-graphite, cylindrical 21700 | 8 (4 first-life α + ~4 second-life γ) | Longitudinal RPTs |
| Khan 2025 | NMC / graphite, prismatic | 19 (22 minus excluded S2 + S18) | Longitudinal, days 0/10/20/40/90 |
| Zhang Cambridge v2 | LCO / graphite, button (LR2032) | 8 | Per-sweep time-aligned |
| WMG 25-cell (Rashid 2023) | NMC811 / graphite, 21700 cylindrical | 19 (24 minus 5 100SOH controls) | Cross-sectional aging to terminal SOH |

Total: 54 per-cell residual unit vectors fed into the hierarchical model.

## Posterior group-centroid directions (median, 4-group model)

```
NMC_cyl     (SECL)     centroid unit = (-0.786, +0.482, +0.387)
NMC_prism   (Khan)     centroid unit = (-0.885, +0.124, +0.448)
LCO_button  (Zhang)    centroid unit = (-0.505, +0.533, +0.679)
NMC811_cyl  (WMG)      centroid unit = (-0.947, +0.195, +0.256)
```

Axes are (u_Q_max, u_R_ohmic, u_R_diff): negative u_Q_max = capacity fade;
positive u_R_ohmic / u_R_diff = impedance growth.

## Pairwise group-centroid cosine angle (median, 95% CI)

```
NMC_cyl     vs NMC_prism   : +0.926  [+0.821, +0.990]
NMC_cyl     vs LCO_button  : +0.908  [+0.802, +0.975]
NMC_cyl     vs NMC811_cyl  : +0.934  [+0.843, +0.986]
NMC_prism   vs LCO_button  : +0.814  [+0.671, +0.919]
NMC_prism   vs NMC811_cyl  : +0.974  [+0.936, +0.995]
LCO_button  vs NMC811_cyl  : +0.751  [+0.610, +0.867]
```

The strongest cluster is NMC_prism ↔ NMC811_cyl (cos 0.974) despite
different form factors. Suggests chemistry-family (NMC) dominates form
factor on the residual direction. LCO_button stays the most distinct
(lowest pairwise cosine across the board). SECL NMC_cyl is the outlier
inside the NMC group, likely driven by its Si-graphite anode.

## Variance decomposition (between-group / total)

```
u_Q_max:    median 76.1%, 95% CI [39.7%, 95.4%]
u_R_ohmic:  median 40.7%, 95% CI [ 5.7%, 86.5%]
u_R_diff:   median 41.9%, 95% CI [ 7.6%, 89.7%]
```

Q_max axis is the cleanest discriminator of chemistry-form-factor. EIS
axes carry signal but with wider uncertainty at this N.

## Repository layout

```
Battery/
  c2_battery_phases.md     master phase plan (Phase 0 → Phase 4 → C1/C2/C3)
  NEXT.md                  pickup pointer for the next session
  literature/              decision memos (sequenced 00 → 14)
  code/                    extraction + analysis scripts (see manifest below)
  data/                    cohort data + processed/ feature parquets
    secl_first_life/       Stanford SECL first-life RPTs
    secl_second_life/      Stanford SECL second-life RPTs
    khan_2025/             Khan 2025 (Mendeley)
    zhang_cambridge/       Zhang Cambridge v2
    wmg_25cell/            WMG 25-cell (Rashid 2023, Mendeley mn9fb7xdx6/3)
    processed/             parquet outputs (features, mahalanobis, classifications)
```

## Code manifest

| Script | What it does |
|---|---|
| `extract_features.py` | First-life feature pipeline from consolidated `.mat` files |
| `extract_features_second_life.py` | Second-life capacity + EIS extraction |
| `extract_eis_per_cell.py` | Second-life EIS RPTs 9–19 from per-cell `.xlsx` |
| `fresh_period_null_pooled.py` | First-life Mahalanobis using pooled fresh covariance |
| `combine_and_run.py` | Naive cross-lifecycle combiner (deprecated; see Option X1) |
| `combined_option_x1.py` | Option X1 pipeline (per-cell fresh = first-life RPT 1–3) |
| `triad_beta_pipeline.py` | β triad (G1/W4/W5) with HPPC operators |
| `knee_point_detector.py` | Capacity-knee detection (Zhang/Altaf/Wik 2024 curvature) |
| `combined_alpha_beta_leadtime.py` | N=7 lead-time aggregation |
| `phase3_hierarchical_pymc.py` | Bayesian Phase 3 lead-time model |
| `khan_extract_and_classify.py` | Khan 2025 held-out classifier (Phase 4) |
| `secl_held_out_classifier.py` | SECL β + γ held-out classifier (Phase 4) |
| `zhang_extract_and_classify.py` | Zhang v1 (INVALID — degenerate Q_max) |
| `zhang_v2_extract_classify.py` | Zhang v2 time-aligned per-sweep classifier (PASSES) |
| `wmg_extract_features.py` | WMG 25-cell cross-sectional residual extractor |
| `c1_cross_chemistry.py` | C1 hierarchical pooling model (now 4 groups) |
| `second_life_days_axis.py` | Honest null on second-life knee (days axis) |

## How to reproduce the headline C1 4-group result

```bash
cd Battery
# 1. (one-time) populate cohort data — most under data/, some require manual download
#    WMG requires manual download from https://data.mendeley.com/datasets/mn9fb7xdx6/3
#    into data/wmg_25cell/; the script handles the rest of the structure.

# 2. Extract WMG residual vectors
python code/wmg_extract_features.py
# Writes data/processed/wmg_25cell_classification.parquet

# 3. Run cross-chemistry hierarchical model with all 4 groups
python code/c1_cross_chemistry.py
# Prints variance decomposition + pairwise centroid cosines; writes
# data/processed/c1_cell_units.parquet
```

The other cohorts (SECL, Khan, Zhang) feed into `c1_cross_chemistry.py`
through their own extraction pipelines and their parquets must exist in
`data/processed/` before C1 will assemble all 54 cells. See the code
manifest for what produces each parquet.

## What's next

See [NEXT.md](NEXT.md) for the live pickup pointer. Short version:
**begin C3 design parameter inversion**. Two probe modes in parallel:

- **Real-data probe** — within-cohort design / operating-condition
  variation. Khan has 18 cycle-conditions across 19 cells; Severson has
  72 fast-charging protocols across 124 cells. Test: do operator residual
  directions cluster by condition within a single chemistry-form-factor
  group?
- **Synthetic-data probe** — PyBaMM with controlled electrode-thickness
  / electrolyte-additive / separator-porosity variation. Closes the
  material-design dimension that's sparse in public data.

## Caveats

- N is small at the per-group level. The 4-group decomposition is
  robust on the Q_max axis but wide-CI on the EIS axes.
- The WMG cohort is cross-sectional (one observation per cell at its
  terminal SOH), unlike the longitudinal SECL/Khan/Zhang cohorts. The
  per-cell residual vector is still well-defined, but WMG cannot
  contribute to a per-cell lead-time analysis (only to the C1
  cross-chemistry geometry).
- The Phase 4 multi-cohort verdict is 2-of-3 cohorts passing under
  pre-registered Bonferroni; the Khan failure was explanatory (Khan is
  NMC_prism, a distinct centroid not anticipated by the pre-reg's
  NMC-cyl-anchored LLI/LAM+SEI centroids).
