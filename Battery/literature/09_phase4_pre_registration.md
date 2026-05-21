# Phase 4 Pre-Registration — Degradation-Mode Classification Protocol

**Date locked:** 2026-05-21
**Locked before:** any classifier touches G1/W4/W5/V5 or any second-life cell.
**Reason for early lock:** The Phase 2.4 N=4 alpha-triad analysis (V4 vs W8/W9/W10) produced an exploratory observation that V4 shows an LLI-dominant residual-direction signature and the W-cells show a coupled LAM+SEI signature. That observation is **post-hoc** and **unblinded**. To make the Phase 4 mode-classification claim honest, the analysis protocol must be locked before any classifier sees the held-out cells.

This document is the pre-registration. Once committed and pushed to the git remote, no edits to the protocol are permitted — only amendments via explicit deviation entries that quote both the old and new text.

---

## 0. Status and exploratory disclosure

**Exploratory (unblinded, USED to inform this pre-reg):**
- First-life alpha cells: V4, W8, W9, W10 (N=4 trajectories)
- Operators: Q_max, R_ohmic_soc50, R_diff_soc50
- Source of pattern: per-operator z-scores at late RPTs (RPT 11)
- Pattern observed: V4 = capacity drop without resistance growth (LLI-dominant); W-cells = capacity drop coupled with R_ohmic and R_diff growth (LAM+SEI-dominant)

**Held out, NEVER yet seen by a classifier (LOCK BEFORE TOUCHING):**
- First-life beta cells: G1, W4, W5 (3 cells with HPPC instead of EIS)
- First-life dismissed-early cells: V5, W3, W7 (insufficient RPTs for trajectory analysis but included as fail-safe presence check)
- Second-life gamma cells: G1, V4, V5, W8, W9, W10 (6 cells with EIS, RPTs 5-19 — RPTs 9-19 require .DTA parser before classifier can run)
- Khan 2025 cohort: 22 prismatic NMC/graphite cells with capacity + EIS
- WMG 25-cell cohort: NMC811 cylindrical with EIS at SOH breakpoints
- Zhang Cambridge 2020 cohort: 12 cells with EIS aging-mode labels

The honest holdout structure is the row above. A pre-registered classifier will be applied to it and the result reported regardless of direction.

---

## 1. Hypothesis to be tested

H1 (primary, replication): The LLI-dominant vs LAM+SEI-dominant cluster separation observed exploratorily on N=4 first-life alpha cells **replicates on at least one independent held-out cohort** in the geometric structure of unit-norm operator residual vectors.

H1-null: Residual-direction unit vectors of held-out cells do not separate into the V4-like (LLI) and W-cell-like (LAM+SEI) clusters more reliably than chance under a permutation null.

## 2. Features (LOCKED)

**Unit of analysis:** per-trajectory operator residual-direction vector.

**Per trajectory:**
1. Take all RPTs with `m_dist > threshold_99pct` (i.e., the disagreement-flagged RPTs from Phase 2.4)
2. For each such RPT, take the standardized operator residual vector `z = (z_op1, z_op2, z_op3)`
3. Normalize to unit length: `u = z / ||z||`
4. Per-trajectory residual-direction vector = **median across flagged-RPT unit vectors** (median preserves directionality, robust to outlier RPTs)

This is a 3-D unit vector per trajectory. It encodes the *direction* of disagreement in operator space, not the magnitude. **Magnitude is explicitly excluded from Phase 4 features** — magnitude is the Phase 3 lead-time signal, not the Phase 4 mode-classification signal.

For Triad β (HPPC instead of EIS), the operator dimensions differ but the unit-vector construction is identical. Direct comparison of Triad α and β unit vectors is not meaningful (different operator axes), but cluster structure within each triad can be evaluated separately.

## 3. Cluster reference points (derived from exploratory cohort, LOCKED)

Two reference unit-vector centroids in (z_Q_max, z_R_ohmic, z_R_diff) space:

- **LLI-like centroid (`u_LLI`):** unit vector pointing in direction (−1, 0, 0). Capacity loss without resistance growth.
- **LAM+SEI-like centroid (`u_LAM_SEI`):** unit vector pointing in direction (−1, +1, +1) / norm = (−0.577, +0.577, +0.577). Capacity loss coupled with resistance growth.

These are derived geometrically from the exploratory N=4 observation but expressed as physics-motivated reference directions, not as fitted centroids from V4/W-cells specifically. They are testable on Triad α cohorts. Triad γ (second-life α-equivalent) uses the same reference points.

For Triad β, an analogous pair must be defined based on the equivalent HPPC features `(z_Q_max, z_R_DC, z_tau)`:
- **LLI-like (β):** (−1, 0, 0)
- **LAM+SEI-like (β):** (−1, +1, +1) / √3

(These are the same direction in standardized-residual space, regardless of which third operator is in slot 3.)

## 4. Classification metric (LOCKED)

For each held-out trajectory's residual-direction vector `u_test`:

- `s_LLI(u_test) = u_test · u_LLI` (cosine similarity to LLI reference)
- `s_LAM_SEI(u_test) = u_test · u_LAM_SEI`
- **assigned class:** argmax over `{s_LLI, s_LAM_SEI}`
- **assignment confidence:** `|s_LLI - s_LAM_SEI|` (gap between top-2 similarities)

Per-cell confidence threshold of `0.3` for a "confident" assignment. Trajectories with confidence below 0.3 are reported as "unclassified" — the protocol must not silently discard low-confidence assignments.

## 5. Falsification thresholds (LOCKED)

**Replication test on held-out alpha-or-gamma cells (G1 second-life, V4 second-life, V5 second-life, W8 second-life, W9 second-life, W10 second-life):**

⚠️ **Important nuance:** W8/W9/W10/V4/G1 second-life are the SAME physical cells as their first-life counterparts. Their residual-direction in second-life is not statistically independent of the exploratory pattern. Truly independent held-out cells for replication are:
- **V5 second-life** (V5's first-life was dismissed early, so its operator pattern was not used in the exploratory analysis)
- **Khan 2025 cohort** (different chemistry, different lab)
- **Zhang Cambridge cohort** (different chemistry, has explicit aging-mode labels for direct validation)

**H1 supported if all three of the following hold:**
1. At least 50% of held-out cells (Triad α or β or γ) are "confidently classified" (confidence ≥ 0.3) into one of {LLI, LAM+SEI}
2. At least 70% of held-out cells classified by this protocol fall into the LAM+SEI cluster (matches expected aging-mode prevalence for NMC/graphite at moderate SOH)
3. Permutation null (shuffle cell-trajectory assignments, recompute centroid alignment, repeat 10,000×) yields p < 0.05 for cluster-separation statistic

**H1 falsified if any of:**
- Held-out V5 second-life classifies confidently as LAM+SEI (would refute the LLI-only-on-V4 specificity claim if V4-second was also classified LAM+SEI — i.e., both V4 and V5 in second-life show LAM+SEI direction)
- Khan 2025 cohort (independent chemistry) fails the cluster-separation test
- Permutation null p ≥ 0.05

**H1 partial / inconclusive if:**
- Some but not all replication conditions hold
- Confidence-below-threshold rate exceeds 50%
- Cohort size insufficient for permutation null power

## 6. Multiple-comparison handling

The pre-registered analysis runs the same protocol on three independent cohorts (held-out SECL, Khan 2025, Zhang Cambridge). Treat as three independent replication attempts; report Bonferroni-corrected p-values (α/3 = 0.0167) for the cluster-separation test.

## 7. Operational protocol (the order of execution, LOCKED)

1. Extract held-out cell features using the pipeline already validated on alpha cells. **No tuning of feature extraction on held-out data.**
2. Compute per-trajectory unit residual-direction vectors as specified in §2.
3. Apply classifier (§4) and report per-trajectory assignment and confidence.
4. Run permutation null (§5) and report Bonferroni-corrected p-values.
5. **Write up regardless of result direction.** If H1 is falsified, the writeup says so and the C2 second-claim is null.

## 8. Pre-registration deviations log

(Deviations from this protocol must be appended below with date, rationale, and exact diff. Once a deviation is logged, the original protocol stands as the published intent and the deviation is reported transparently in the paper.)

| Date | Deviation | Rationale |
|---|---|---|
| (none yet) | | |

## 9. What this pre-registration does NOT cover

- Phase 3 lead-time analysis (covered by separate Phase 3 pre-reg, pending)
- Hierarchical Bayesian pooling of mode-classification posteriors (Phase 4 v2, after this pre-reg's frequentist version lands)
- Subgroup analyses (lifecycle stage, triad type, chemistry) — these are descriptive and not pre-registered as confirmatory claims
- Stan model fit diagnostics — model implementation freedom is preserved as long as the pre-registered classifier protocol is what gets reported

---

## Signature equivalent

This document is the locking commit. The git commit message that introduces this file is the timestamp of the pre-registration. Reviewers can verify the lock by inspecting the commit log of `Renewables/Battery/literature/09_phase4_pre_registration.md` and confirming the file's introduction predates any analysis run on held-out cells.
