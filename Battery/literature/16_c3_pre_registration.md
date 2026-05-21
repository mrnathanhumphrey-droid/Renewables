# Phase C3 Pre-Registration — Design-Parameter / Operating-Condition Inversion (Probes 2 + 3)

**Date locked:** 2026-05-21
**Locked before:** any Severson data is downloaded OR inspected; any WMG within-cohort analysis is run.
**Reason for pre-reg:** C3 Probe 1 (within-Khan, literature/15) was exploratory — 4 tests run on one cohort, SOC-range hit at p=0.036 does not clear naive Bonferroni at α/4. To promote the C3 "operating-condition inverts to operator-residual direction" claim from exploratory to confirmatory, we need independent replication under a locked protocol.

Once this file is committed and pushed, no edits are permitted — only amendments via explicit deviation entries that quote both the old and new text.

---

## 0. Exploratory disclosure (from C3 Probe 1)

Pattern observed on Khan NMC/graphite prismatic (literature/15):
- Within the 14 cycle-aged cells, **SOC range** (= upper-voltage cutoff) clustered residual directions: 0-100% (cos 0.999 with 10-90%) vs 0-80% (cos ~0.93 vs others). PERMANOVA pseudo-F = 8.79, p = 0.036.
- **Temperature did NOT cluster** the same cells: pseudo-F = 2.17, p = 0.272.
- Effect interpretation: upper-voltage cutoff at 4.1V (the 0-80% group) avoids the high-V cathode-stress regime → different degradation pathway → different residual direction (elevated R_ohmic, R_diff).

This is the pattern the pre-registered probes will attempt to replicate.

## 1. Hypotheses

**Probe 2 (Severson within-cohort, primary C3 replication):**

- **H2-primary:** Within the Severson 124-cell LFP/graphite 18650 cohort cycled under 72 fast-charging protocols, the cell-level operator residual-direction vectors separate by a pre-specified **operating-condition axis** (first-step C-rate, binned into 3 groups) at a level above the permutation null.
- **H2-null:** Residual-direction unit vectors do not separate by first-step C-rate label more than chance.

**Probe 3 (WMG within-cohort, calibration/coherence test):**

- **H3-primary:** Within the WMG NMC811 21700 cohort, cell-level operator residual-direction vectors at the same terminal SOH bin cluster tighter than chance, i.e., residual direction is reproducible at a given aging state (not dominated by per-cell idiosyncrasy).
- **H3-null:** Residual-direction unit vectors do not cluster by SOH-bin label more than chance.

(Probe 3 is **not** a C3 replication — WMG has only one chemistry-form-factor and no design-parameter variation. It is a framework-coherence test: if H3 is null, the framework cannot reliably resolve aging-stage within a single design, weakening the C3 program. If H3 is supported, the within-cohort signal is reproducible enough that design-parameter inversion is mechanically possible at this N.)

## 2. Operators and feature extraction (LOCKED — no tuning on either probe)

### Probe 2 (Severson)

**Operators (3-vector per cell, per RPT-equivalent point):**
1. `Q_max` — discharge capacity of the diagnostic cycle (1C-1C charge/discharge full window). Severson includes diagnostic cycles every ~100 cycles; use the nominal diagnostic capacity.
2. `DCIR` — derived from V drop at start of discharge step. Formula: `DCIR = |V_just_before_pulse − V_at_pulse_onset_plus_30s| / I_pulse`. Use the diagnostic cycle's 1C discharge step transition. If the diagnostic step structure does not expose a clean current step, use the C-rate transition closest to the diagnostic point and document.
3. `T_can_amplitude` — peak-to-peak can-temperature swing during the diagnostic 1C discharge: `max(T_can) − min(T_can)` over the discharge half-cycle.

**Fresh reference per cell:** mean of operator triad over diagnostic cycles 5–15 (post-formation, pre-aging). If a cell has fewer than 5 diagnostic cycles in that window, use whatever diagnostic cycles exist before cycle 50.

**Aged snapshot per cell:** operator triad at the diagnostic cycle nearest to the cell's 80% SOH crossing. If the cell never reaches 80% SOH within its observed lifetime, use the diagnostic cycle nearest to its lowest observed SOH and flag as `partial_aging`.

**Standardization:**
- Subtract per-cell fresh-reference triad from aged snapshot → raw residuals.
- Standardize each operator dimension by the pooled cross-cell standard deviation of fresh-reference values (population fresh-SD, computed across all included cells).
- Normalize the standardized 3-vector to unit length → `u = z / ||z||`.

### Probe 3 (WMG within-cohort)

Use the existing `data/processed/wmg_25cell_classification.parquet` produced by `code/wmg_extract_features.py`. No re-extraction. Per-cell residual unit vector `u = (u_Q_max, u_R_ohmic, u_R_diff)` from canonical SOC=50, T=25°C EIS at the cell's terminal SOH, standardized against the 5 100SOH controls.

**No new features for Probe 3.** All 19 aged WMG cells are included; the 5 controls are excluded (they ARE the fresh reference and contribute zero residual signal).

## 3. Bin / group definitions (LOCKED — no tuning after data peek)

### Probe 2 (Severson) — first-step C-rate bins

The 72 Severson protocols vary the first-stage charging C-rate from ~3.6C to ~8C (per the Severson 2019 paper's documented protocol space). **Primary bin definition (LOCKED):**

- **Bin A (low):** first-step C-rate < 4.5C
- **Bin B (mid):** first-step C-rate in [4.5C, 6.0C)
- **Bin C (high):** first-step C-rate ≥ 6.0C

These thresholds are a **pre-peek guess** at where balanced tertile-equivalent splits land, based on the documented 3.6C–8C protocol space in the Severson 2019 paper. We have not inspected the actual cell-level protocol distribution; the thresholds may turn out unbalanced. **The primary verdict in §5 is based on this locked guess.** The result on these locked bins is reported regardless of magnitude or direction.

#### Permitted re-binning (LOCKED contingency protocol)

**Trigger condition (purely feature-distribution dependent, NOT outcome-dependent):**

If, after extraction and inclusion-filtering, **any of the locked bins has n < 6 cells**, a secondary re-binned analysis is permitted. The re-binning rule is **fixed in advance** to prevent outcome-shopping:

- **Secondary bins:** tertile cut on the empirical distribution of first-step C-rate among the included cells. Compute the 33rd and 67th percentiles of the observed `first_step_C` values; assign cells to bins T1 (lowest tertile), T2, T3.
- **No alternative re-binning schemes are allowed.** Quartile cuts, custom thresholds, "natural break" cuts, mixture-model cuts — none of these are pre-registered and using any of them constitutes a new deviation requiring a separate pre-reg amendment.

**What the re-binned analysis is permitted to do:**

- Re-run the same PERMANOVA test on the new tertile-bin labels
- Report pseudo-F + p + per-bin n
- Compare to the locked-bin result (which is still the primary verdict)

**What the re-binned analysis MUST NOT do:**

- Replace the locked-bin verdict. The locked-bin result is the primary verdict for §5 falsification thresholds, full stop.
- Use a new significance threshold. Bonferroni is α/2 across the 2 pre-reg probes; the re-binned secondary test is exploratory and cannot be promoted to a primary claim. If it lands significant where the locked-bin did not, that is a candidate for a follow-up pre-reg, not a current confirmation.
- Trigger ANY new operator-extraction, inclusion, or feature decision. Only the bin labels change; everything upstream is identical.

**Documentation requirement:** if the re-binning is triggered, the deviation log (§10) MUST contain (a) the cell counts in the locked bins that triggered the re-bin, (b) the empirical 33rd/67th C-rate percentiles, (c) the resulting tertile cell counts, and (d) the locked-bin AND re-binned PERMANOVA results side-by-side.

The locked-bin result remains the primary verdict reported in §5 either way; the re-binning is an "obvious next step" robustness probe, NOT a replacement.

### Probe 3 (WMG) — terminal SOH bin labels

Groups are the 4 aged terminal-SOH bins as already present in the data: {80%, 85%, 90%, 95%}. Per-bin n = {5, 5, 4, 5}.

## 4. Primary test (LOCKED)

For each probe, the **single primary test** is a PERMANOVA-style permutation test on the cosine-distance matrix of unit residual vectors:

- Anderson 2001 pseudo-F statistic on the cosine-distance matrix
- Null distribution: 10,000 permutations of group labels
- p-value = (count of permuted pseudo-F ≥ observed + 1) / (n_perms + 1)

**Significance threshold (Bonferroni-adjusted for 2 pre-registered probes):**

- α = 0.05
- α / 2 (Bonferroni) = **0.025 per probe**

**Effect-size threshold (separate from p-value):**

Pseudo-F must exceed **3.0** to be considered a substantive effect, regardless of p-value. This guards against a tiny-but-significant effect from being over-interpreted. The threshold is derived from C3 Probe 1 (Khan SOC-range pseudo-F was 8.79, well above 3.0; the null tests landed at pseudo-F 2.0–2.3; 3.0 cleanly separates them).

## 5. Falsification thresholds (LOCKED)

### Probe 2 (Severson) — H2 verdicts

- **H2 PASS:** PERMANOVA p < 0.025 **AND** pseudo-F > 3.0 **AND** at least 2 of 3 bins have n ≥ 8 cells.
- **H2 WEAK PASS:** PERMANOVA p ∈ [0.025, 0.05] OR pseudo-F ∈ [2.0, 3.0] with otherwise PASS conditions. Effect direction is suggestive but doesn't clear pre-registered thresholds.
- **H2 NULL:** PERMANOVA p ≥ 0.05 OR pseudo-F < 2.0. C3 operating-condition inversion does NOT replicate on a second cohort with a different chemistry / triad.
- **H2 INVALID:** any of:
  - DCIR or T_can_amplitude extraction fails for >30% of cells (operator triad is not constructible on this dataset)
  - Fewer than 60 cells total pass inclusion criteria (sample size below feasibility floor)
  - Any single bin has n < 3 cells (PERMANOVA undefined on that bin)

### Probe 3 (WMG within-cohort) — H3 verdicts

- **H3 PASS:** PERMANOVA p < 0.025 AND pseudo-F > 3.0.
- **H3 WEAK PASS:** PERMANOVA p ∈ [0.025, 0.05] OR pseudo-F ∈ [2.0, 3.0] with otherwise PASS conditions.
- **H3 NULL:** PERMANOVA p ≥ 0.05 OR pseudo-F < 2.0. Within-cohort residual direction is dominated by per-cell idiosyncrasy at this N; framework coherence at single-design level is weak.

### Joint C3-replication verdict

- **C3 STRONG REPLICATED:** Probe 2 PASS, Probe 3 PASS or WEAK PASS.
- **C3 PARTIAL REPLICATED:** Probe 2 WEAK PASS OR (Probe 2 NULL with Probe 3 PASS). Operating-condition inversion property does not strongly replicate on Severson but framework coherence at single-design level holds.
- **C3 FAILED REPLICATION:** Probe 2 NULL AND Probe 3 NULL. Within-cohort signal is not extractable in the new cohorts at the operator-triad and N afforded by the available data. C3 retreats to "alive on Khan only" and needs synthetic-data (PyBaMM) probe before further public claims.
- **C3 INDETERMINATE:** Probe 2 INVALID. Cannot evaluate the primary replication test; report Probe 3 result alone and pause C3.

## 6. Cell-inclusion criteria (LOCKED before data peek)

### Severson

- **Include:** any cell that (a) has at least 5 diagnostic cycles in the cycles 5–15 fresh-reference window, AND (b) reaches at least 80% SOH OR has ≥ 100 diagnostic cycles total.
- **Exclude:** cells flagged in the original Severson 2019 metadata as anomalous / dropped (the paper documents a small number); cells with corrupted DCIR or T_can extraction (document count + reason).
- **Cell count target:** ≥ 90 cells (out of nominal 124) after inclusion. If fewer than 60 pass, declare H2 INVALID per §5.

### WMG

- **Include:** all 19 aged cells already in `wmg_25cell_classification.parquet`.
- **Exclude:** the 5 100SOH controls (they're the fresh reference).
- **No data-peek-dependent exclusions allowed.**

## 7. Batch / nuisance variable handling

### Severson — batch effect MUST be controlled

Severson cells come from 3 batches (41 / 43 / 40 cells) with different mean cycle lives. **The primary PERMANOVA test will be run TWICE on the Severson cohort:**

1. Pooled across all 3 batches with first-step C-rate bin as the grouping label.
2. Stratified within each batch separately (3 sub-tests), with results reported per batch.

**For the primary verdict (§5), the pooled test stands.** The stratified version is a robustness check; if the pooled test is significant but stratified within-batch tests all fail, the pooled signal is likely batch-confounded → re-classify as H2 WEAK PASS or NULL depending on magnitude.

### WMG — no nuisance variables, single-batch single-instrument

No batch effect to control. Operator extraction is from a single SOC × T canonical condition per cell; the within-cell EIS-condition heterogeneity is not part of Probe 3.

## 8. Operational protocol (LOCKED execution order)

1. Commit this pre-reg + push to remote. **Lock is the commit timestamp.**
2. **Probe 2 (Severson) first.**
   a. Download Severson Batch 1 + necessary subsets from `data.matr.io`. Document the URL + commit-hash of the dataset version used.
   b. Build `code/severson_extract_features.py` per §2; build `code/c3_severson.py` per §3–§4. Both deterministic per the pre-reg; **no tuning on observed data**.
   c. Run extraction; report cell-inclusion + exclusion counts BEFORE running the PERMANOVA test. If counts violate §6, declare H2 INVALID and stop.
   d. Run the primary PERMANOVA test; report p, pseudo-F, per-bin n, batch-stratified results.
   e. Write up in `literature/17_c3_severson_result.md` regardless of direction.
3. **Probe 3 (WMG within-cohort) second.**
   a. Build `code/c3_wmg_within.py` (Probe 3 is trivial given existing parquet); run primary PERMANOVA on the 4 SOH bins.
   b. Write up in `literature/18_c3_wmg_within_result.md` regardless of direction.
4. Update Battery/README.md and Battery/c2_battery_phases.md with verdicts.
5. **Contingent next step (NOT pre-registered here):** If Probe 3 reveals something operationally meaningful (e.g., a coherence signal that exposes a confound or motivates a new operator-extraction step on Severson), any subsequent Severson re-analysis MUST be filed as a separate pre-reg amendment with a fresh lock commit. The amendment must (a) state what WMG produced that justified re-touch, (b) describe the exact protocol delta, (c) acknowledge that the re-analyzed Severson result is no longer covered by the Bonferroni in §4 and must carry its own significance threshold.
6. If C3 is FAILED REPLICATION per §5, scope the PyBaMM synthetic probe as the next move.

## 9. What is explicitly NOT covered by this pre-reg

- Hyperparameter tuning of bin thresholds, DCIR extraction window length, or T_can-amplitude time-window length. All locked in §2–§3.
- Multiple SOH-anchor alternatives for Severson (e.g., 90% SOH vs 80% SOH vs 70% SOH snapshot). §2 specifies 80% SOH; deviation requires explicit pre-reg amendment.
- Alternative bin schemes for Severson protocols (e.g., total-time-to-charge, last-step C-rate). §3 specifies first-step C-rate bins; alternatives are exploratory only.
- Bayesian / hierarchical versions of the PERMANOVA test. Reserved for post-replication analysis if either probe lands.
- Cross-cohort centroid comparison between Severson and Khan. Different operator triads → different unit spheres → not directly comparable.
- Severson's headline "early-cycle voltage feature predicts cycle life" claim is orthogonal to C3 and not under test here.

## 10. Pre-registration deviation log

(Deviations from this protocol must be appended below with date, rationale, and exact diff.)

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |

---

## Signature equivalent

The git commit that introduces this file is the pre-registration timestamp. Reviewers can verify the lock by inspecting the commit log of `Renewables/Battery/literature/16_c3_pre_registration.md` and confirming the file's introduction predates any Severson data download or any WMG within-cohort analysis run.

C3 Probe 1 (within-Khan, literature/15) is acknowledged as exploratory and motivating; it is NOT counted toward the Bonferroni correction here. The Bonferroni α/2 = 0.025 covers only the two probes pre-registered above.
