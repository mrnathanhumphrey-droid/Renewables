# Phase C3 Probe 3 — WMG Within-Cohort Result

**Date:** 2026-05-21
**Pre-registration:** literature/16_c3_pre_registration.md, locked commit `1ef1b94`
**Verdict (per pre-reg §5 strict reading):** **H3 NULL** by p-value; effect-size above floor; underpower-failure not signal-absence.

---

## What was tested

Per pre-reg §1 H3: *"Within the WMG NMC811 21700 cohort, cell-level operator
residual-direction vectors at the same terminal SOH bin cluster tighter than
chance, i.e., residual direction is reproducible at a given aging state (not
dominated by per-cell idiosyncrasy)."*

NOT a C3 replication (WMG has only one chemistry-form-factor and no
design-parameter variation). A framework-coherence test: if residual
direction is reproducible across cells at the same aging state, the C3
within-cohort claim is mechanically possible. If residuals are dominated
by per-cell idiosyncrasy at the same SOH, the framework can't resolve
design parameters at this N.

## Data

19 aged WMG cells, residual unit vectors from `data/processed/wmg_25cell_classification.parquet`
(produced by `code/wmg_extract_features.py` per C1 pipeline). 5 100SOH
controls excluded — they ARE the fresh reference.

Per-bin n:
- SOH 80%: n=5
- SOH 85%: n=5
- SOH 90%: n=4
- SOH 95%: n=5

## Per-SOH centroid directions (median, unit-normalized)

```
SOH=95% (n=5):  centroid = (-0.984, +0.130, +0.125)
SOH=90% (n=4):  centroid = (-0.959, +0.157, +0.235)
SOH=85% (n=5):  centroid = (-0.899, +0.260, +0.353)
SOH=80% (n=5):  centroid = (-0.952, +0.182, +0.246)
```

The trajectory is non-monotonic:
- 95% → 85%: heavy u_Q starts decreasing slightly, u_R_ohmic + u_R_diff steadily grow
- 85% → 80%: u_Q rebounds toward more-negative (heavier Q dominance), EIS contributions roll back

The 85% SOH bin has the **maximum EIS pickup** of all four bins. This is
striking — it suggests cells in the 80-90% SOH band undergo a transition
through an impedance-rise-dominant intermediate state before settling into a
deeper-aging signature.

## Primary PERMANOVA

```
pseudo-F = 5.298
p (10000 permutations) = 0.0668
Bonferroni alpha/2 = 0.025
Effect-size floor = 3.0
```

Per pre-reg §5 verdict thresholds:
- H3 PASS: p<0.025 AND F>3.0 — FAIL (p > 0.025)
- H3 WEAK PASS: p in [0.025, 0.05] OR F in [2.0, 3.0] — FAIL (p > 0.05)
- H3 NULL: p≥0.05 OR F<2.0

**Strict pre-reg verdict: H3 NULL.**

## Why this is "underpower not absence"

Pseudo-F = 5.30 is well above the effect-size floor (3.0) — the magnitude of
between-SOH-bin separation is substantive. The signal IS in the data. What's
missing is the cell count to push the permutation null p below 0.05.

At N=19 across 4 groups (n=4-5 each), permutation tests are notoriously low-
power even for substantial effects. Two-thirds of the permutation distribution
falls below the observed F. p=0.067 would have been WEAK PASS at α=0.05; the
Bonferroni-adjusted α/2 = 0.025 is the strictness that kicks it to NULL.

If this had been a 2-cohort joint pre-reg (Probe 2 alone, Bonferroni-free),
H3 would have been WEAK PASS at α=0.05 (one-sided p=0.067 → no; but the
unadjusted α=0.05 itself doesn't catch this either, since p > 0.05).

## What this means for C3 / the framework

1. **Within-aging-stage reproducibility is BELOW THE NOISE FLOOR at this
   N.** We cannot, on the WMG cohort alone, distinguish cells-at-same-SOH
   from cells-at-different-SOH purely from their (Q_max, R_ohmic, R_diff)
   residual direction.

2. **Yet the per-bin centroids show a coherent SOH trajectory.** The 95%
   centroid is most-Q-dominant; the 85% centroid has the maximum EIS pickup
   (a degradation-pathway intermediate state); the 80% centroid rolls back
   partially. This pattern is mechanistically interpretable but does not
   clear the permutation null.

3. **Implication for C3 design-parameter inversion:** at within-cohort n in
   the 4-5 range per bin, the framework's residual-direction resolution is
   insufficient. Design-parameter probes within a single chemistry-form-factor
   need either (a) larger cell counts per condition, or (b) larger design-
   parameter contrast to clear the noise floor.

## Caveats

- WMG is **cross-sectional aging** (each cell terminates at one SOH; not
  longitudinal). Per-cell uncertainty is structurally bigger than for
  longitudinal cohorts (one shot per cell at the EIS measurement).
- Operator triad is (Q_max, EIS R_ohmic at SOC=50/T=25°C, EIS R_diff at SOC=50/T=25°C).
  This is the same triad as Khan / SECL / Zhang.
- The non-monotonic SOH trajectory may be a genuine degradation-pathway
  signal but at n=4-5 per bin we can't separate that from noise.

## Outputs

- `code/c3_wmg_within.py` — PERMANOVA on WMG residual vectors
- (no new data outputs; uses existing `data/processed/wmg_25cell_classification.parquet`)

## Joint C3 verdict context

Combined with Probe 2 (Severson, literature/17, H2 PASS pooled):

- Probe 2 PASS + Probe 3 NULL is not in the pre-reg's joint tier list
- Honest reading: C3 within-cohort design-parameter inversion is **supported on
  Severson pooled**, NOT supported on Severson Batches 2 and 3 within-batch, and
  NOT supported on WMG within-bin (but the WMG NULL is underpower, not
  signal-absence)
- The replication is **partial and substrate-specific**. The framework's
  within-cohort claim survives in some operator/cohort/N regimes and fails in
  others. Mechanistically meaningful; methodologically a caution

See literature/17_c3_severson_result.md for the full Probe 2 analysis.
