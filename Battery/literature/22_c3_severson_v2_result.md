# Phase C3 Probe 2 Amendment — Severson Alternative-Axis Result

**Date:** 2026-05-21
**Pre-registration:** literature/21_c3_severson_v2_pre_registration.md, locked commit `3fb179a`
**Verdict (per pre-reg §6 strict reading):** **H5 WEAK.** No alternative design axis survives within-Batch-2.

---

## Headline

Three alternative design axes (last-step C-rate, SOC at handoff, severity score)
were pre-registered in literature/21 to test whether the within-batch null
observed for first-step C-rate in Probe 2 (literature/17) was axis-specific
or batch-specific.

**All three alternative axes show the same pattern as first-step C-rate:**
either no pooled signal, or pooled signal that collapses inside Batch 2.

| Axis | Pooled F | Pooled p | Batch 2 F | Batch 2 p | Verdict |
|---|---|---|---|---|---|
| last_step_C | 10.005 | 0.0002 | 3.380 | 0.106 | AXIS POOLED-ONLY PASS |
| soc_handoff | 2.165 | 0.132 | 1.239 | 0.385 | AXIS NULL |
| severity | 4.766 | 0.013 | 3.062 | 0.093 | AXIS POOLED-ONLY PASS |

Joint verdict: **H5 WEAK** (no AXIS PASS, but 2 of 3 are POOLED-ONLY PASS).

---

## What this changes about Probe 2

The literature/17 within-batch failure on first-step C-rate is **not axis-specific**.
Two additional axes (last-step C-rate, severity score) show the SAME pattern:
strong pooled signal, fails within Batch 2 (the well-aged cohort with balanced
bins). A third axis (SOC handoff) shows no separation at all even pooled.

This is informative: **the partial-batch behavior in Probe 2 is a property of the
Severson cohort, not a property of "we picked the wrong design axis."** Batch 2's
null is robust to alternative axis choice.

Mechanism hypothesis (NOT under pre-reg test, exploratory):
- Batch 2 cells aged cleanly to 80% SOH (all 43 crossed), giving uniform aged-anchor SOH
- Batch 1 + 3 cells had non-uniform terminal SOH (~81-83%), giving more spread in residual magnitudes that aligns with design-axis differences
- The "within-batch design-condition signal" we detect in Batch 1 may actually be a "residual-magnitude spread driven by partial aging × design condition" interaction, not a pure design-direction signal

This is testable: the residual unit-direction (which is what we use) should NOT
depend on magnitude. But if there's a magnitude-direction interaction (e.g., very
small residuals are essentially noise direction, while larger residuals carry
real signal), then Batch 2's cleaner-aged cells with uniform large residuals
would have well-defined directions clustered tightly, while Batch 1's spread of
partial-aging cells would have direction noise that correlates with design
condition through aging-extent. That's a confound.

The C3 framework's claim is "residual DIRECTION (not magnitude) inverts to
design parameter." This Probe 2 amendment exposes that on the Severson cohort,
the within-batch signal may be a magnitude-direction artifact rather than a
clean direction-design relation. The PyBaMM Probe 4 (literature/20) showed clean
direction-design inversion in a controlled-magnitude setting; Severson real data
shows a more complex picture.

## What this does NOT change about C3 overall

- **PyBaMM Probe 4 STRONG SUPPORT** stands. The synthetic ground-truth probe
  showed clean material-design inversion via residual direction (literature/20).
- **Probe 2 H2 PASS** on first-step C-rate stands. The pre-reg §5 verdict
  thresholds were cleared.
- The honest reading of all 5 C3 probes (1 exploratory + 4 pre-registered):
  - **Synthetic data (Probe 4): C3 mechanism validated.**
  - **Real data (Probes 1-3 + this amendment): C3 detection on real cohorts is
    sensitive to N, batch effects, and possibly aging-extent confounds.**

This is methodologically meaningful but does not invalidate the C3 deliverable.
It tightens the framing for the eventual paper: synthetic + Khan (cohort-level)
support; Severson + WMG show known-N and known-batch limitations.

---

## Detailed per-axis results

### Last-step C-rate

Tertile cuts: T1 < 3.6C, T2 ∈ [3.6C, 4.6C), T3 ≥ 4.6C. Distribution skewed
(n=21/67/51) because many protocols have a slow second stage (≥3.6C predominates).

```
Pooled PERMANOVA:  F = 10.005, p = 0.0002  → PASSES Bonferroni alpha/3 = 0.0167
Batch 1 (n=50):    F = 3.496,  p = 0.0494  → just inside alpha=0.05 (weak)
Batch 2 (n=43):    F = 3.380,  p = 0.1056  → FAILS within-batch
Batch 3 (n=46):    F = NaN,    p = NaN     → bin imbalance (T1 has n=2; not testable)

VERDICT: AXIS POOLED-ONLY PASS
```

Last-step C-rate carries pooled signal but Batch 2 (well-aged, balanced) doesn't
detect it.

### SOC at handoff

Tertile cuts: T1 < 36%, T2 ∈ [36%, 60%), T3 ≥ 60%. Reasonably balanced.

```
Pooled PERMANOVA:  F = 2.165, p = 0.132   → FAILS even at alpha=0.05
Batch 1 (n=50):    F = 4.152, p = 0.0311
Batch 2 (n=43):    F = 1.239, p = 0.385
Batch 3 (n=46):    F = 1.874, p = 0.298

VERDICT: AXIS NULL
```

SOC at handoff is the WEAKEST design axis tested. No pooled signal at all. The
where-protocol-switches axis doesn't carry residual-direction information
extractable at this N. Batch 1 alone shows weak signal but pooled cancels it
(possibly opposite-sign batch effects across batches).

### Severity (SOC-weighted average C-rate)

Tertile cuts: T1 < 4.69, T2 ∈ [4.69, 4.80), T3 ≥ 4.80. Heavy concentration near 4.7-4.8.

```
Pooled PERMANOVA:  F = 4.766, p = 0.0132  → PASSES Bonferroni alpha/3
Batch 1 (n=50):    F = 1.382, p = 0.302   → FAILS within-batch
Batch 2 (n=43):    F = 3.062, p = 0.093   → close to alpha=0.05 (weak)
Batch 3 (n=46):    F = NaN,   p = NaN     → bin imbalance

VERDICT: AXIS POOLED-ONLY PASS
```

Interesting subtlety: severity is the ONLY axis where Batch 2's p drops to ~0.093
(close to weak-pass territory). The aggregate severity metric weakly differentiates
Batch 2 cells where individual rate axes don't. But Batch 1 here goes nearly NULL
(p=0.302), opposite of Batch 1's pattern on first-step / last-step / handoff.

The fact that severity weakly hits in Batch 2 but not in Batch 1 — while
first-step / last-step / handoff all show the opposite (Batch 1 hits, Batch 2
fails) — strongly suggests the residual-direction signal **interacts with
batch and axis differently**. There's no single design axis that lights up
consistently within all batches.

## Output

- `data/processed/c3_severson_v2_results.parquet` — extended parquet with
  alternative axes (last_step_C, soc_handoff, severity) and tertile bin labels
- `code/c3_severson_v2.py` — parser + analysis script

## Implications for next moves

This amendment refines the C3 status in two ways:

1. **Tightens Probe 2's framing.** "First-step C-rate" was not the unique axis
   driving Probe 2's pooled PASS. Other axes (last-step C-rate, severity) also
   show pooled signal. The pooled-PASS pattern is general; the within-batch
   failure is also general.
2. **Exposes a possible aging-magnitude confound.** Batch 2 (well-aged) doesn't
   show within-batch design-axis signal across 3 of 4 axes tested. Batches 1
   and 3 (partial-aging) do. This suggests the framework's residual-direction
   signal may be partially driven by aging-extent variation interacting with
   design condition — not pure design-direction inversion as the C3 claim
   asserts.

The synthetic Probe 4 (literature/20) demonstrated direction-design inversion
in a controlled setting where aging extent is uniform across cells (all reach
80% capacity vs nominal). That probe is unaffected by this concern. Real-cohort
probes remain mixed.

The honest next probe (NOT pre-registered here; would need new lock) would be:
**within-Severson, condition on aged_SOH** as a covariate. Test whether the
residual-direction × design-axis effect persists after controlling for terminal
aging extent. If it does → C3 robust. If it doesn't → C3 framework needs a
magnitude-condition step before direction inversion.

---

Joint C3 status across all 5 pre-registered analyses:

| Probe | Cohort | Verdict | Reading |
|---|---|---|---|
| 1 (lit/15, exploratory) | Khan NMC/graphite prismatic | SOC range hit, F=8.79 p=0.036 | motivating finding |
| 2 (lit/17) | Severson LFP/graphite (N=139, first-step C-rate) | **H2 PASS** pooled | partial within-batch replication |
| 3 (lit/18) | WMG NMC811_cyl (N=19, SOH bins) | **H3 NULL** by p (F=5.30 above floor) | underpower, not absence |
| 4 (lit/20) | PyBaMM synthetic (N=106, L9 factorial) | **H4 STRONG SUPPORT** | 2/3 design params PASS |
| 2v2 (lit/22, this) | Severson alt-axes (N=139, 3 axes) | **H5 WEAK** | partial-batch failure is general, not axis-specific |

C3 status: synthetic-validated, real-cohort-mixed. Promotion to paper requires
either (a) experimental cohort with controlled aging extent, or (b) framework
amendment that handles aging-extent × design-condition interactions.
