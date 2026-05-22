# Phase C3 Probe 2 Amendment — Severson Alternative Design-Axis Pre-Registration

**Date locked:** 2026-05-21
**Locked before:** any alternative-axis analysis is run on the Severson cohort. The existing `severson_extracted.parquet` is read-only and was extracted under the locked pipeline in literature/17. This amendment only changes the per-cell bin LABELS, not the operator triad, fresh reference, aged anchor, or any other extraction step.

**Relation to literature/16:** This is the contingent amendment foreshadowed in literature/16 §8.5. It registers fresh per-axis Bonferroni accounting separate from the original probe-2/probe-3 Bonferroni.

Once committed and pushed, no edits permitted; deviations logged in §10.

---

## 0. Motivation

C3 Probe 2 (literature/17) on Severson 124-cell LFP/graphite 18650 cells produced:
- **H2 PASS pooled** on first-step C-rate (pseudo-F = 31.7, p = 0.0001 across 3 bins, N = 139)
- **Within-batch stratification (literature/17 §7):**
  - Batch 1 (2017-05-12, n=50): F=12.83, p=0.0002 — strong replication
  - Batch 2 (2017-06-30, n=43): F=1.69, p=0.276 — null within batch
  - Batch 3 (2018-04-12, n=46): F=1.22, p=0.194 — null but structurally underpowered (3/43/0 bin split)

The pooled signal was carried by Batch 1; Batch 2's null with balanced bins is the
meaningful caveat. **The honest question this amendment addresses:** is first-step
C-rate actually the right axis for within-cohort design inversion, or does a
different design axis show within-batch consistency?

This is **not** an attempt to overturn the Probe 2 pooled PASS — that stands. This is
an additional probe of WHICH design axis carries within-batch information.

## 1. Hypotheses

**H5-primary:** When the Severson 124-cell cohort is binned by one of three
alternative design axes (last-step C-rate, SOC at handoff, total time-to-charge),
**at least one** axis produces residual-direction separation that holds within
Batch 2 (the cohort that failed first-step C-rate within-batch).

**H5-secondary:** Each axis's pooled and within-batch PERMANOVA results are
characterized and reported regardless of direction.

**H5-null:** None of the three alternative axes shows within-batch separation
above the pre-registered effect-size and p thresholds.

## 2. Data and operator triad (LOCKED, INHERITED FROM literature/17)

No changes. Reads `data/processed/severson_extracted.parquet` (139 cells with
operator triad already extracted per literature/16 §2). The unit residual
vectors are recomputed exactly as in literature/17 §4 (pooled-fresh SD
standardization, unit-normalization).

## 3. Alternative design axes (LOCKED)

Three additional design axes parsed from the existing `protocol` column. NONE of
the original `first_step_C` field is used.

### Axis 1: Last-step C-rate

The C-rate of the final CC segment of the multi-step charge. For protocols like
`5.3C(54%)-4C`, last-step = 4C. For single-step protocols like `4_4C_80per_4_4C`,
last-step = first-step = 4.4C.

Extraction: parse the trailing C-rate token after the final SOC-handoff `%`.

### Axis 2: SOC at handoff

The fraction of charge delivered during the first stage before switching to the
second stage. For `5.3C(54%)-4C`, SOC handoff = 54%. For single-step protocols,
this is undefined → encoded as 100% (protocol never switches).

Extraction: parse the percentage value between parentheses or after the first
C-rate token's `%` marker.

### Axis 3: Total time-to-charge severity score

Aggregate metric proxying total time spent at high C-rate:

```
severity = first_step_C * (SOC_handoff / 100) + last_step_C * (1 - SOC_handoff / 100)
```

This is an SOC-weighted average C-rate. Cells charged predominantly at high
C-rate get high severity. Cells with rapid handoff to slower second stage get
lower severity.

## 4. Binning rule (LOCKED — TERTILE CUTS, FEATURE-BASED)

For each axis, **bin cells into 3 groups via tertile cuts on the empirical
distribution among included cells**. The 33rd and 67th percentiles are computed
from the actual observed values across all included cells, then cells assigned
to T1 (lowest tertile), T2, or T3 (highest tertile).

**This is the SAME pre-registered contingency-binning rule from literature/16 §3.**

No alternative binning schemes permitted under this amendment.

## 5. Primary tests (LOCKED)

For each of the three axes, the same PERMANOVA test as literature/16 §4:
- Anderson 2001 pseudo-F on cosine-distance of unit residual vectors
- 10000 permutations
- Pooled across batches (primary) AND batch-stratified (robustness)

**Bonferroni for this amendment:** 3 new tests, α = 0.05, **α/3 = 0.0167 per axis**.

This Bonferroni is INDEPENDENT of literature/16's α/2 for probes 2+3. The
amendment carries its own significance accounting per literature/16 §8.5.

**Effect-size floor:** pseudo-F > 3.0 (consistent across all C3 work).

## 6. Falsification thresholds (LOCKED)

For each per-axis test:

- **AXIS PASS:** p < 0.0167 AND pseudo-F > 3.0 AND
  the within-Batch-2 stratified test (literature/17 §7 pattern) has p < 0.05
- **AXIS POOLED-ONLY PASS:** pooled p < 0.0167 AND F > 3.0 BUT Batch 2 within-batch
  fails (p ≥ 0.05). This is "same problem as first-step C-rate."
- **AXIS WEAK PASS:** p in [0.0167, 0.05] AND F > 2.0
- **AXIS NULL:** p ≥ 0.05 OR F < 2.0

**H5 verdicts:**

- **H5 SUPPORT:** at least 1 axis is AXIS PASS (within-batch holds)
- **H5 WEAK:** 0 PASS but 2+ POOLED-ONLY PASS or WEAK PASS — multiple axes
  show pooled signal but none survives within-Batch-2
- **H5 NULL:** 0 axes show any pooled or within-batch separation. The Probe 2
  pooled PASS was likely batch-confounded
- **H5 INVALID:** parsing fails on >10% of cells (protocol-string ambiguous)

## 7. What this amendment changes vs literature/17

- **Adds:** three new bin-label columns to `severson_extracted.parquet` derived
  from the existing `protocol` string
- **Does not change:** the operator triad (Q_max, R_DC, T_can_amplitude); the
  per-cell fresh reference; the aged anchor; the cell-inclusion criteria;
  the pooled-fresh SD standardization; the PERMANOVA test specification

The Probe 2 pooled PASS verdict on first-step C-rate stands as filed. This
amendment is **additional** analysis, not a retraction.

## 8. Operational protocol (LOCKED execution order)

1. Commit this amendment + push to remote. Lock is the commit timestamp.
2. Implement `code/c3_severson_v2.py`:
   - Read existing `data/processed/severson_extracted.parquet`
   - Parse three new axis labels from `protocol` strings
   - Report parsing-success rate (must be ≥90% per §6 INVALID condition)
   - Compute tertile cuts per axis
   - Run PERMANOVA per axis (pooled + batch-stratified) per §5
3. Apply H5 verdict per §6
4. Write up in `literature/22_c3_severson_v2_result.md` regardless of direction
5. Update Battery/README.md with the amendment verdict

## 9. Explicitly NOT covered

- Re-analyzing other cohorts (Khan, Zhang, WMG) with alternative axes — would
  require separate pre-reg
- Re-running PyBaMM Probe 4 with different parameter sweeps — would require
  separate pre-reg (Probe 4 already STRONG SUPPORT)
- Bayesian hierarchical models on Severson — reserved for post-replication work
- Cross-axis interaction tests (e.g., joint PERMANOVA on last-step × handoff) —
  would inflate Bonferroni accounting, not pre-registered

## 10. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |
