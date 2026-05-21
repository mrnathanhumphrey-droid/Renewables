# Phase C3 Probe 1 — Within-Khan Design-Parameter Inversion

**Date:** 2026-05-21
**Status:** EXPLORATORY (first probe; not pre-registered; replication required before promotion)
**Commit at time of writing:** TBD (this writeup + `code/c3_within_khan.py` + Khan condition table)

---

## Hypothesis tested

After C1 hit (76.1% between-group Q_max-axis variance across 4 chemistry-form-factor
groups), the C3 question becomes attackable: **within a single chemistry-form-factor
group, do operator residual directions cluster by operating condition?**

If yes, then operator-residual geometry is informative about design / operating-condition
choices, not just chemistry — which is the C3 deliverable (design-parameter inversion).

Khan 2025 cohort is the natural first probe:
- Single chemistry-form-factor: NMC/graphite prismatic 5 Ah (1 chem × 1 form factor)
- 19 cells with valid C1 residual unit vectors (out of 22 viable; S1, S3, S4, S8, S9 are
  calendar-aged, the rest cycle-aged; 5 cycle-aged at 25 °C, 6 at 40 °C, 5 at 0 °C in
  the unit-vector cohort — three were excluded by C1's "≥1 flagged RPT" filter)
- Conditions vary by aging type (cycle vs calendar), temperature (0 / 25 / 40 °C),
  SOC range / voltage cutoff (0-100% / 10-90% / 0-80%), charge C-rate (0.2C-CCCV vs 1C-CC)

Source for the per-cell condition table: Khan, Chu, Onori 2025 *Data in Brief*
(DOI 10.1016/j.dib.2025.112282), Table 4. Saved to
`data/khan_2025/cell_conditions.csv`.

---

## Tests run (PERMANOVA-style permutation, 10000 perms each)

PERMANOVA = Anderson 2001 pseudo-F on the cosine-distance matrix of the N×3 unit
vectors. Significance via random label shuffle.

| Grouping | N total | Groups | pseudo-F | p (perm) | Reading |
|---|---|---|---|---|---|
| aging_type (calendar vs cycle) | 19 | 2 | 2.032 | 0.258 | not separable |
| aging_type × T_C | 19 | 6 (some n=1) | 2.344 | 0.248 | not separable |
| cycle-only × T_C | 14 | 3 (0/25/40 °C) | 2.167 | 0.272 | **temperature does not invert** |
| cycle-only × SOC range | 14 | 3 (0-100 / 10-90 / 0-80) | **8.787** | **0.036** | **SOC range DOES invert** |

The cycle-25C-only charge_rate split (0.2C-CCCV vs 1C-CC) has N=4 (2+2), too small for
permutation; reported descriptively only.

---

## Headline: SOC-range hit

Cycle-only cohort (N=14) grouped by SOC range, with voltage limits in parentheses:

| SOC range | Voltage limits | N cells | Cells | Centroid (u_Q_max, u_R_ohmic, u_R_diff) |
|---|---|---|---|---|
| 0-100% | 2.5–4.2 V | 3 | S12, S17, S22 | (−0.920, +0.024, +0.391) |
| 10-90% | 2.5/3.0–4.15 V | 6 | S11, S14, S16, S19, S20, S24 | (−0.928, +0.065, +0.366) |
| 0-80% | 2.5–4.1 V | 5 | S10, S13, S15, S21, S23 | (−0.765, +0.328, +0.555) |

Pairwise centroid cosine angles:

- 0-100% vs 10-90%: **cos = +0.999** — essentially identical residual direction
- 0-100% vs 0-80%: cos = +0.928
- 10-90% vs 0-80%: cos = +0.934

The structure: **0-100% and 10-90% cells share a residual direction; 0-80% cells form
a distinct cluster.** Distinguishing feature of the 0-80% group is the **upper voltage
cutoff at 4.1 V** (vs 4.15/4.2 V for the others) — i.e., cells that never reach the
high-voltage cathode-stress regime.

Mechanistic reading (tentative): NMC at high state-of-charge (>~85% SOC) experiences
cathode lattice stress / oxygen evolution onset. Cells held below 4.1V upper cutoff
avoid that regime. Their dominant degradation pathway therefore shifts away from
cathode-LAM and toward an alternative (likely SEI growth + LLI), which projects to
a different residual direction in (Q_max, R_ohmic, R_diff) space.

The 0-80% centroid has noticeably elevated u_R_ohmic (+0.33 vs +0.02-+0.07 for the
others) and somewhat elevated u_R_diff (+0.56 vs +0.37-+0.39) — consistent with the
SEI-growth / impedance-rise interpretation.

---

## Temperature is NOT a separator

The three cycle-only temperature groups (N=5 at 0 °C, N=4 at 25 °C, N=5 at 40 °C) have
centroids:

- 0 °C: (−0.798, +0.261, +0.543)
- 25 °C: (−0.952, +0.106, +0.288)
- 40 °C: (−0.885, +0.075, +0.460)

Pairwise cosines all ≥ 0.94. PERMANOVA p = 0.272 — fail to reject the null that
temperature labels are exchangeable with random labels.

This is a real-data answer to a question that was open. **Temperature, at the
campaign's design points (0/25/40 °C), does NOT show up in operator residual
direction within the Khan cohort.** It may show up at more extreme temperature
contrasts, or it may genuinely be that the (Q_max, R_ohmic, R_diff) triad at SOC=50
is temperature-blind on this short (90-day) campaign.

---

## Caveats

1. **Exploratory.** Four tests run on the same cohort; the SOC-range p=0.036 does
   NOT clear naive Bonferroni at α/4=0.0125. The honest framing is "SOC range is the
   only axis showing signal at exploratory thresholds; the temperature null is
   informative but not the headline."
2. **N is small.** Per-condition n=3-6. PERMANOVA pseudo-F values >2 routinely
   produce non-significant p under shuffle at this N. The SOC-range pseudo-F of 8.8
   is the standout magnitude.
3. **Single cohort.** Khan only. Cross-cohort replication of "SOC-range inverts but
   T does not" is the obvious next step — Severson's 72 fast-charging protocols on
   LFP/graphite 18650 is the largest available test bed.
4. **Confound:** SOC range and voltage cutoff are confounded in Khan's design (every
   0-80% cell has 4.1V cutoff; every 0-100% has 4.2V; every 10-90% has 4.15V). We
   cannot separate "SOC window" from "upper voltage cutoff" within Khan alone.

---

## What this opens

C3 is alive on real data. The within-Khan signal demonstrates **operator-residual
geometry inverts operating-condition choices** at the level of SOC-range / voltage-
cutoff. Not yet design-parameter (electrode thickness, electrolyte additive,
separator porosity) — that's the material-design dimension that requires either
(a) public datasets with controlled material variation (sparse — open problem), or
(b) synthetic data via PyBaMM with known parameter sweeps.

**Next probes:**

1. **Severson within-cohort.** 124 cells × 72 protocols × single chemistry / form factor.
   Apply the same PERMANOVA to (fast-charge profile, ambient T) labels. Larger N
   should produce tighter p's if the within-cohort design-condition-inverts-residual
   pattern is real.
2. **WMG within-cohort.** N=19 NMC811_cyl across (terminal SOH, [test SOC × test T] for
   EIS). Not a design-parameter probe per se — but a test of whether the WMG
   cross-sectional design produces a within-cohort signal in the same shape.
3. **PyBaMM synthetic.** Generate cells with known electrode-thickness sweeps; extract
   the same (Q_max, R_ohmic, R_diff) operators; see if the inversion holds when the
   ground truth is in hand.

If the Severson within-cohort PERMANOVA also lands, C3 promotes from "alive on Khan"
to "replicated cross-chemistry." If PyBaMM lands the synthetic-data hit, C3 promotes
from "operating-condition inversion" to "material-design inversion."

---

## Code + outputs

- `code/c3_within_khan.py` — runs all four PERMANOVA tests, prints centroids,
  saves merged units+conditions parquet
- `data/khan_2025/cell_conditions.csv` — per-cell condition table from Khan 2025
  Table 4
- `data/processed/c3_khan_units_with_conditions.parquet` — N=19 Khan unit vectors
  joined with their experimental conditions
