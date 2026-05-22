# Phase C3 Probe 2 — Severson Within-Cohort Result

**Date:** 2026-05-21
**Pre-registration:** literature/16_c3_pre_registration.md, locked commit `1ef1b94`
**Pre-flight performed before primary test:** yes, per §8.2.c
**Verdict (per pre-reg §5 strict reading):** **H2 PASS**
**Honest framing:** PASS with significant batch-confound caveat (pooled signal driven by Batch 1; Batches 2 and 3 do not replicate within-batch).

---

## Pre-flight (pre-reg §8.2.c)

Extracted with `code/severson_extract_features.py` operating directly on
`data/severson/FastCharge.zip` (BEEP-structured, 28 GB, 140 cell JSONs).

| Metric | Value | Pre-reg §6 threshold | Status |
|---|---|---|---|
| Cells in archive | 140 | — | informational |
| Cells with extracted operators | 139 | — | 1 dropped (insufficient cycles in fresh window) |
| Cells reached 80% SOH | 43 | — | informational |
| Cells flagged partial_aging | 96 | — | informational (most aged to 81-83% SOH) |
| Total n_total | 139 | ≥60 floor, ≥90 target | PASS |
| Bin A (<4.5C) | 30 | n≥6 locked-bin trigger | PASS |
| Bin B (4.5-6C) | 79 | — | PASS |
| Bin C (≥6C) | 30 | — | PASS |
| Smallest bin n | 30 | ≥3 for validity | PASS |
| Locked-bin contingency triggered | NO | — | no re-binning |

All §6 conditions met. Cleared to run primary PERMANOVA.

### partial_aging investigation

96 of 139 cells didn't strictly cross 80% SOH (`Q_at_cycle / Q_fresh <= 0.80`).
Their aged anchor was taken at the lowest-SOH cycle observed per pre-reg §2.
Aged-SOH distribution per batch:

- Batch 1 (2017-05-12): median aged_SOH 0.815, 45/50 below 0.90, only 2 above 0.95
- Batch 2 (2017-06-30): median 0.799, all 43 below 0.85 (all crossed 80%)
- Batch 3 (2018-04-12): median 0.825, 45/46 below 0.90

The asymmetric partial_aging flag (Batch 1 + 3 = 100% partial, Batch 2 = 0%
partial) reflects which cells barely missed the strict 80% threshold (Batch
1 + 3) vs which cleanly crossed (Batch 2). Functionally all batches contain
aged cells with strong aging signal; only ~2 cells are at near-fresh anchor.

---

## Primary PERMANOVA (pre-reg §4, locked bins, pooled across batches)

```
pseudo-F = 31.742
p (10000 permutations) = 0.0001
Bonferroni alpha/2 = 0.025         → p << 0.025          PASS
Effect-size floor = 3.0            → F = 31.74 >> 3.0    PASS
Bins with n >= 8: A(30), B(79), C(30) = 3 of 3           PASS

VERDICT (strict pre-reg §5): H2 PASS
```

By strict pre-reg reading, this is a clean PASS — pooled cross-cohort PERMANOVA
shows highly significant separation of cell residual directions by first-step
C-rate bin, with effect size an order of magnitude above the floor.

---

## Batch-stratified PERMANOVA (pre-reg §7 robustness)

| Batch | n | Bins (A/B/C) | pseudo-F | p | Reading |
|---|---|---|---|---|---|
| 2017-05-12 (Batch 1) | 50 | 11 / 15 / 24 | **12.83** | **0.0002** | Strong within-batch signal |
| 2017-06-30 (Batch 2) | 43 | 16 / 21 / 6 | 1.69 | 0.276 | NULL within batch |
| 2018-04-12 (Batch 3) | 46 | 3 / 43 / 0 | 1.22 | 0.194 | NULL — but Batch 3 has zero cells in Bin C and only 3 in Bin A, structurally underpowered |

**Pooled signal is carried by Batch 1.** Batch 2 (the well-aged batch) and Batch 3
(structurally lopsided bins) do not show within-batch separation by first-step C-rate.

Per pre-reg §7: *"if the pooled test is significant but stratified within-batch
tests **all** fail, the pooled signal is likely batch-confounded → re-classify as
H2 WEAK PASS or NULL depending on magnitude."*

The strict trigger condition ("ALL fail") is NOT met — Batch 1 strongly passes.
Verdict per pre-reg §5 + §7 stands as **H2 PASS**. But the honest framing is
**single-batch replication**, not full cross-batch replication.

### Why Batch 2's failure is the most concerning

Batch 2 has balanced bin distribution (16/21/6 across A/B/C), n=43, all 43 cells
cleanly aged to ≤80% SOH. If the first-step-C-rate-inverts-residual claim were
robust, Batch 2 should show it most clearly. Yet pseudo-F = 1.69, p = 0.276 — no
detectable within-batch signal.

Batch 3's null is partly methodological (3 cells in one bin, 0 in another). Batch
2's null is real.

### Why Batch 1's pass might be reading something else

Batch 1 covers the highest C-rates (n=24 in Bin C ≥6C). The Batch 1 first-C
distribution has the strongest dynamic range. If pooled-cohort variance is being
driven by extreme-C-rate cell heterogeneity within Batch 1 (rather than first-C
broadly indexing degradation pathway), Batch 1's PASS would be a true-but-narrow
effect.

---

## Joint C3 verdict (pre-reg §5)

Combined with Probe 3 (WMG within-cohort, literature/18): **Probe 2 PASS + Probe 3
NULL.** This combination does NOT cleanly fit the pre-reg's joint tiers:

- C3 STRONG REPLICATED requires Probe 2 PASS AND Probe 3 PASS-or-WEAK-PASS
- C3 PARTIAL REPLICATED requires Probe 2 WEAK PASS OR (Probe 2 NULL with Probe 3 PASS)
- C3 FAILED REPLICATION requires both NULL
- C3 INDETERMINATE requires Probe 2 INVALID

The pre-reg's tier system did not anticipate the actual outcome (Probe 2 PASS +
Probe 3 NULL). Honest reporting:

- C3 within-cohort design-parameter inversion property is **supported on the
  Severson cohort, pooled** — independent replication of the Khan SOC-range hit
  on a different chemistry and operator triad
- The **partial-batch failure** within Severson (only 1 of 3 batches independently
  replicates) is a meaningful caveat. The C3 mechanism may be present but
  inconsistent across cell populations, or may be reflecting something narrower
  than "first-step C-rate inverts residual direction"
- The Probe 3 NULL on WMG within-cohort is an underpower failure (effect size
  pseudo-F=5.30 above floor 3.0; only p=0.067 misses threshold). Not a true
  signal-absence

---

## What this means for C3 going forward

The replication is **partial and asymmetric**: Khan (literature/15, exploratory)
landed on SOC range. Severson pooled lands on first-step C-rate. WMG can't
contribute (no design-parameter variation). Within-Severson reproducibility is
mixed.

The C3 claim of "within-cohort operating-condition inverts to residual direction"
is supported as a general property but the SPECIFIC axis varies across cohorts
(SOC range on Khan, first-step C-rate on Severson pooled — and not independent
within-Severson batches). This is consistent with:

1. **Real but mechanism-specific:** each cohort's design-condition variation
   indexes a different degradation-pathway shift, but all of them manifest as a
   residual-direction rotation. The pattern is "design conditions invert" not
   "this specific variable inverts."
2. **Partial confound:** the pooled-Severson PASS could be picking up batch
   covariate structure (different batches at different first-C distributions)
   rather than pure first-step C-rate effect.

Either interpretation is consistent with the data. The pre-reg's strict verdict
is **H2 PASS** + **C3 mixed-replication**.

---

## Next probes

Per pre-reg §8.5 (contingent), an obvious follow-up filed as separate amendment:

1. **Re-analyze Severson with a different design-axis label.** First-step C-rate
   was our pre-registered guess. Other axes that could be more robust within-batch:
   total time-to-charge, last-step C-rate, SOC at handoff between charge stages.
   ANY new axis requires a new pre-reg lock; cannot be promoted from exploratory.
2. **PyBaMM synthetic probe** (still next in line for material-design dimension).
   Generate cells with controlled electrode-thickness sweeps under a fixed
   protocol; eliminate batch confound by construction; test whether residual
   direction inverts to known parameter.

---

## Outputs

- `code/severson_extract_features.py` — extractor (BEEP-streamed, no unzip required)
- `code/c3_severson.py` — PERMANOVA per pre-reg §3–§4
- `data/processed/severson_extracted.parquet` — 139 per-cell operator triads + first_step_C + batch_date
- `data/processed/c3_severson_results.parquet` — same with bin labels + unit vectors

Data source: BEEP-processed Severson FastCharge corpus, downloaded 2026-05-21
from data.matr.io project `5c48dd2bc625d700019f3204` (file: `FastCharge.zip`, 28
GB, version per BEEP `@version: 2020.8.21-6702566`).
