# C3 Framework Amendment — Architectural Lock

**Status:** LOCKED 2026-05-27.
**Authored:** Claude.
**Repo target:** `Battery/literature/47_c3_amendment_lock.md`.
**Supersedes:** the original C3 framework architecture defined implicitly in Paper 1 + Probe 4/5/6 (residual unit-vector cosine PERMANOVA on the triad β operators or HPPC equivalents).
**Evidentiary basis:** Probe 7 v1 + v2 (lit/37-40), Probe 8a (lit/41+42), Probe 8b (lit/43+44), Probe 8c (lit/45+46). HEAD `62b78d6` on `main`.

---

## 0. Framework parentage — RMD-SRC

This amendment is a refinement of the Battery substrate's instantiation of **RMD-SRC** (Recursive Moment-flow Decomposition with Statistical-Rule Classification), the substrate-agnostic algorithm specified at `D:/Resolve Research/RMD SRC Algorithm Specification.docx` (Nathan Humphrey, working draft May 2026). The C3 framework is the Battery substrate's mapping to RMD-SRC; the amendment touches two RMD-SRC steps specifically:

- **RMD-SRC Step 2 (trajectory classification)** — the representation of each cell's moment-flow signature. The original C3 architecture represented each cell as a *residual unit vector* in 3D operator space (aged − fresh, projected to unit sphere). The amended architecture represents each cell as a *PCA-2 unit vector* of the centered z-score of the 6D (fresh + aged) operator stack. This is a Step-2 representation change.

- **RMD-SRC Step 3 (response-function validation)** — the test of whether the moment-flow representation carries design-cell information. The PERMANOVA pseudo-F + permutation p-value is the response-function check for the Battery substrate; that test mechanism is unchanged. The amendment changes WHAT goes into PERMANOVA, not WHAT PERMANOVA does.

The amendment's pre-registration falsifiers (P-amend_F1–F4 implicitly through Probes 7–8) inherit from RMD-SRC §"Pre-registered falsifiers" (RMD_F1–F4: initial cleanness, decomposition convergence, validation agreement, predictive transfer). This inheritance is structural; explicit mapping is documented in each probe's pre-reg.

When the Khan cross-substrate validation (forward condition §5.1) closes, the RMD-SRC §"Substrate applications" table at the parent doc should be updated to add Battery as either "Done" (if Khan PASSES) or "framework-resistant" (if Khan FAILS). That update is to the parent doc, not this lock.

## 0.1 Why this amendment exists

The original C3 framework — residual unit-vector cosine PERMANOVA on a 3-operator EIS or HPPC triad — was demonstrated to collapse at typical academic instrumentation noise (Probe 6, lit/26: 0/3 PASS at Level 2). The substrate-saving framework search ran in two parallel directions:

- **Branch A: operator extraction (Probe 7).** Tested whether swapping the operator triad from HPPC to EIS — both via B7 LAM-proxy and B5' cycling-read state — could recover Level-2 survival. **Outcome: NULL.** All three operator extractions collapse identically at L2; operator triad is not the lever.

- **Branch B: architectural decomposition (Probe 8a/b/c).** Tested whether feature-space, distance metric, or projection choices were load-bearing. **Outcome: feature-space (8a) and projection (8c) are both load-bearing in the positive direction.** Switching from residuals to fresh+aged stacked features and PCA-reducing to 2 components STRENGTHENS Level-2 discrimination to th F=21.24, pr F=20.87 (vs the original 0/3 PASS collapse).

This amendment locks the architectural change identified by Probe 8a + 8c as the corrected C3 specification, with the supporting evidence chain and the scientific-claim shift documented explicitly.

## 1. The amended C3 architecture (LOCKED)

For each cell i:

1. **Compute fresh and aged absolute operator triplets.**
   - Fresh: (Q_max_fresh, R_ohmic_fresh, R_diff_fresh) measured at cycles 5-25 of nominal cycling
   - Aged: (Q_max_aged, R_ohmic_aged, R_diff_aged) measured at the uniform-anchor cycle (closest to SOH 0.92)
   - The operators may be derived from HPPC (R_DC, R_total) or EIS (R_ohmic, R_diff). HPPC is the simpler instrument; EIS is the more general operator (better physical interpretation, but requires impedance hardware). The amendment is operator-agnostic; downstream architecture is the same.

2. **Stack into a 6-dimensional feature vector** per cell:
   x_i = (Q_max_fresh, R_ohmic_fresh, R_diff_fresh, Q_max_aged, R_ohmic_aged, R_diff_aged)

3. **Center and z-score by pooled cohort SD:**
   z_i = (x_i − x̄) / σ_pooled, where σ_pooled is computed across all cells per feature dimension.

4. **Reduce to 2 principal components.**
   Compute PCA on the cohort z-score matrix. Retain the top 2 components.
   z_i^(PCA) = z_i · components[:, :2]  (n×2 matrix from n×6 z-scores)

5. **Project to unit vector on the 2-sphere:**
   u_i = z_i^(PCA) / ‖z_i^(PCA)‖₂

6. **Cosine PERMANOVA per design parameter to test:**
   - Distance: d_ij = 1 − u_i · u_j
   - F-statistic: pseudo-F per Anderson 2001 PERMANOVA decomposition
   - 10,000 label permutations
   - Per-parameter verdict: PASS (p < α/k AND F > 3.0), WEAK PASS (α/k ≤ p < α AND F > 2.0), NULL otherwise, where k is the number of design parameters tested simultaneously (Bonferroni correction)

## 2. Operational implications

**Required measurements:** Every cell in a C3 cohort needs BOTH fresh-state and aged-state operator triplet measurements. The amended architecture does not function with aged-only or fresh-only data. (Reason: PC2's design-relevant direction loads on both fresh and aged R_ohmic — see literature/46 §PC loadings.)

**Cohort size minimum:** PCA + PERMANOVA with N_cells ≈ 100 and 3-level Taguchi factorial works (validated at N=101 cells, 9 conditions). Smaller cohorts may face PCA stability issues; larger is always better.

**Anchor convention:** Aged-state measurement should be at a UNIFORM SOH anchor (recommend 0.92, per Probe 5 convention). Variable-anchor aging (where each cell's aged value is at its natural end-of-life SOH) is not validated under this amendment.

**Design-parameter discrimination scope:** Validated for the L9 Taguchi factorial on cathode thickness × cation transference number × cathode particle radius. Other design parameters (anode thickness, separator porosity, electrolyte concentration, etc.) are NOT validated under this amendment; their discriminability under the architecture is an open question.

## 3. Scientific claim — shift from original C3

**Original C3 claim:** Cells with similar aging-direction (in residual operator space) come from similar design-condition manifolds. The framework identifies design parameters from aging-direction inversion of fresh-to-aged residual vectors.

**Amended C3 claim:** Design parameters are discriminable from the principal-component decomposition of fresh + aged absolute operator triplets. The framework identifies design parameters from absolute-feature design fingerprinting (in PCA-reduced space), not aging-direction inversion.

The shift is real and load-bearing:
- The original claim was a STATEMENT ABOUT AGING TRAJECTORIES (the direction in which a cell ages encodes its design parameters)
- The amended claim is a STATEMENT ABOUT ABSOLUTE IMPEDANCE FINGERPRINTS (a cell's fresh + aged impedance signatures separately and jointly encode its design parameters)

Operationally, the amended claim is SIMPLER (no longitudinal aging trajectory needed at PERMANOVA time; just fresh + a single aged anchor). Theoretically, it's LESS SPECIFIC (it overlaps with static-impedance design fingerprinting that doesn't need aging at all). The amendment retains the C3 framing because:

1. The aged-state operators are still required for the 2/3 PASS at L2 — fresh-only doesn't catch particle_radius as cleanly
2. The PC2 direction loads on BOTH fresh and aged R_ohmic + R_diff, reflecting genuine aging-stat information
3. The framework remains substrate-applicable to chemistries where fresh-state design discrimination is less informative (e.g., chemistries with smaller manufacturing variance in fresh impedance)

But honest framing in any paper based on this architecture must acknowledge the shift: the C3 framework is no longer testing "aging-direction inversion" specifically.

## 4. What the amendment does NOT do

- **Does not recover transference.** Across all 5 architectural decomposition components tested (Probe 7 operator extraction + 8a feature-space + 8b distance + 8c projection), transference number is irrecoverable at PRIMARY noise. Distinguishing transference requires a different physical observable (sub-10 mHz EIS for bulk-electrolyte signatures, or GITT, or a different operator entirely). Transference is OUT OF SCOPE for the amended C3 framework as locked here; future operator-set expansion is a separate architectural question.

- **Does not validate on real cells.** All Probe 7 + 8 evidence is on the 108-cell PyBaMM synthetic cohort. Real-cell EIS noise has different characteristics (especially at the high-frequency intercept). Cross-substrate validation against Khan's 19-cell NMC_prism cohort (the closest real-cell EIS cohort in the corpus) is the gating step before paper-ready promotion. Until that runs, this amendment is a synthetic-substrate architectural specification, not a deployment-ready framework.

- **Does not close Probe 7's open question.** Probe 7 v1 + v2 ruled out operator-triad swap as a noise-rejection lever; both HPPC and EIS triads collapsed under residual architecture. The amended architecture works on either triad. The choice of HPPC vs EIS instrumentation in a deployment is an operational decision, not an architectural one, under the amendment.

- **Does not replace Probe 5's uniform-anchor convention.** The aged-state measurement is still at SOH 0.92 ± 0.02. Cells outside this anchor band (`anchor_partial=True`) are excluded.

- **Does not amend the C2 framework (independence-framework lead-time).** Paper 1's C2 result on disagreement-onset lead time remains as published. The C3 amendment is specific to the design-parameter inversion claim.

## 5. Forward conditions before paper-ready promotion

The amended architecture is locked at synthetic-substrate level. Before any Paper 3 / Paper 4 / future-paper promotion using this architecture as the C3 specification:

1. **Cross-substrate validation on Khan (n=19) NMC_prism cohort.** Khan has EIS at 5 SOC bins at days 0/10/20/40/90. Apply the amended architecture, test design-parameter discrimination on Khan's aging-condition labels (cycle conditions). Expected: at least particle radius (if Khan has particle-size variation) should pass at Khan's measurement-noise level. If Khan fails, the synthetic-to-real gap remains — narrowing to "synthetic-only architecture."

2. **Probe 8d (test statistic) — OPTIONAL.** PERMANOVA vs RF classifier accuracy vs logistic regression. May find that PERMANOVA itself is a noise-fragile choice; if so, the amendment can be sharpened further. Not a blocker since L2 PASS is already secured.

3. **Cohort scale-up.** N=101 is small for PCA-PERMANOVA. Re-validate on a larger synthetic cohort (e.g., 500-1000 cells with broader L9 sampling) to confirm the architecture's stability against per-cell variance growth. Not a blocker for synthetic-substrate claims but advisable before any real-cell deployment.

4. **Transference operator addition (NOT in this amendment).** Adding a low-frequency EIS or GITT operator to the triad to attempt transference discrimination is a SEPARATE amendment, not covered here.

## 6. Lock summary

| Component | Specification |
|---|---|
| Operator triad | Q_max + (R_ohmic, R_diff) [EIS] OR Q_max + (R_DC, R_total) [HPPC] |
| Required state pairs | Fresh (cycles 5-25 mean) AND aged (uniform anchor SOH 0.92) |
| Feature space | 6D stacked: (3 fresh, 3 aged) |
| Standardization | Center + pooled cohort SD z-score |
| Projection | PCA reduce to k=2 (PC1 = thickness axis, PC2 = particle_radius axis) |
| Distance | Cosine on unit-vector-projected PCA-2 features |
| Test | PERMANOVA, 10,000 permutations |
| Verdict thresholds | PASS: p < 0.0167 + F > 3.0; WEAK: 0.0167 ≤ p < 0.05 + F > 2.0; NULL otherwise |
| Cohort minimum | N ≈ 100 cells, ≥ 3 levels per design parameter |
| Validated scope | Cathode thickness + cathode particle radius. Transference NULL. |
| Forward-required validation | Cross-substrate (Khan), optional 8d test-stat decomp, scale-up |

## 7. Lock metadata

**Lock anchor:** commit hash of this file's first repo commit, to be recorded in §7.1 post-commit.

**Supporting evidence chain (in dependency order):**
- literature/26 (Probe 6 noise injection result) — original residual + cosine architecture 0/3 at L2
- literature/37+38 (Probe 7 v1, B7 LAM-proxy NULL)
- literature/39+40 (Probe 7 v2, B5' cycling-read NULL)
- literature/41+42 (Probe 8a, feature-space dividing line, variant iv 2/3 PASS at L2 with F=14/13)
- literature/43+44 (Probe 8b, distance metric neutral)
- literature/45+46 (Probe 8c, PCA-2 strongest at L2 with F=21/20)

**Reference implementation:** the existing analyzer `code/c3_probe8c_projection.py` runs the full pipeline (apply_noise → build_zscore_feats → pca_project(k=2) → unit_project → cosine_distance_matrix → permanova_test_dist) in `run_projection(df_clean, "pca_2_unit", N1_LEVELS)`. A dedicated reference implementation will be promoted to `code/c3_amended.py` in the next commit.

### 7.1 Post-commit lock anchor

- Lock commit: `<TBD — recorded in follow-up commit>`
