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

C1 hitting is what opens **C3 — design-parameter inversion from operator
residuals**, which is the actual deliverable of the program.

## Current state (2026-05-21)

| Component | Status | Location |
|---|---|---|
| Phase 0 (lit review + decision memo) | LOCKED | literature/00, 01 |
| Phase 1 (dataset inventory + power calc + cell disposition) | LOCKED | literature/02, 03, 08 |
| Phase 2 (PPC, conditional null, Option X1 cross-lifecycle) | LOCKED | literature/04, 05, 06, 07, 10 |
| Phase 3 (lead-time, N=7 frequentist + Bayesian) | LOCKED | literature/11, 12 |
| Phase 4 (multi-cohort held-out classification) | LOCKED | literature/09 (pre-reg), 13 (Khan FAIL), 14 (SECL-β PARTIAL PASS, Zhang v2 PASS) |
| C1 cross-chemistry hierarchical (3 groups) | LOCKED | commit 505284f |
| C1 cross-chemistry hierarchical (4 groups w/ WMG) | LOCKED | this README's commit |
| Second-life days-axis null | LOCKED | commit 44ece58 |
| C3 design parameter inversion | NEXT | — |

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
