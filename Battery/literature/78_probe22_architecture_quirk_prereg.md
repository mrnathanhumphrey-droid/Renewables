# C3 Probe 22 — Architecture-Quirk Robustness Pre-Registration

**Status:** DRAFTED 2026-05-30. Awaiting user sign-off → lock.
**Date drafted:** 2026-05-30
**Authored:** Claude
**Repo target on lock:** `Battery/literature/78_probe22_architecture_quirk_prereg.md`
**Prior:** Probe 21 (lit/76+77) re-selected `{E1, C2, W1, W3, W5}` under the XS-primary gate and showed clean WMG transfer F=5.70 [3.14, 7.53] (200-seed cell-stratified bootstrap) and L2-noise F=6.04 [3.57, 13.12]. HEAD `32950ae`.

## 0. Motivation — is the cascade architecture load-bearing, or just a sensible default?

Every probe from P15 onward uses the same downstream aggregator (`cascade_F` in `c3_probe15_crosssubstrate_gate.py`):

> **REF architecture (A0):** impute(mean) → standardize feats → RandomForestClassifier on training cohort labels → `rf.apply()` to get leaf-id matrix → standardize leaves → PCA(min(10, n_dim)) → Euclidean PERMANOVA on WMG-only embedding vs SOH bins.

This pipeline was inherited from lit/35 / lit/47 amendments and never falsified. It encodes **four independent architectural choices** that could each be load-bearing or interchangeable:

1. **Leaf embedding via RF** (vs working directly on standardized features, vs RF predict-proba)
2. **PCA dimensionality** (10 components, vs 2, vs no PCA)
3. **Distance metric** (Euclidean, vs cosine on unit-normed embedding)
4. **The combination thereof**

If alternative aggregators yield comparable F on the same training/test partition, the lit/47-style architecture is interchangeable with simpler aggregators (and any claim that lit/47 itself is the "right" architecture is weakened). If alternatives collapse, the architecture IS the load-bearing piece.

In **RMD-SRC** terms: an RMD_F4 robustness check on the partition aggregator — pre-committed alphabet of aggregators, locked partition, data-determined ranking.

## 0.1 Six locked architecture variants

All variants share:
- Same input X-matrix (training stack [Khan, SECL_first_life, Zhang] augmented for W-ops where extractable; WMG held-out n=19) on the **P21 re-selected operators `{E1_ohmic_intercept, C2_R_DC_to_R_total, W1_warburg_slope, W3_peak_neg_im_norm, W5_arc_chord_length}`**.
- Same imputation (`SimpleImputer(strategy="mean")`) and same z-score (`StandardScaler` fit on training X, applied to WMG).
- Same training labels (cohort + Khan aging type; `load_training()` output).
- Same WMG SOH bins (`soh_eis`).
- Same 200-seed cell-stratified bootstrap protocol (seed `b ∈ {0..199}`; RF random_state=b).
- Same reference seed `REF_SEED=42` for the 10k-perm PERMANOVA p-value.

Variants (each is a single function defined verbatim below):

- **A0 (REF, P21 baseline):** `RF.apply(X)` leaves → standardize → `PCA(n_comp=min(10, n_dim))` → take WMG rows → Euclidean PERMANOVA on `soh_bins`.
- **A1 (NO_RF):** Skip RF entirely. Standardized X → `PCA(n_comp=min(10, n_feat))` → take WMG rows → Euclidean PERMANOVA on `soh_bins`.
- **A2 (RF_PROBA):** `RF.predict_proba(X)` (n_class-dim probability matrix) → standardize → `PCA(n_comp=min(10, n_class))` → take WMG rows → Euclidean PERMANOVA on `soh_bins`. Same RF as A0.
- **A3 (PCA-2):** Same as A0 through PCA, but `n_comp=2` instead of 10. Tests whether 10D embedding is overkill.
- **A4 (NO_PCA):** `RF.apply(X)` leaves → standardize → **skip PCA** → take WMG rows → Euclidean PERMANOVA on `soh_bins` (on the full leaf-embedding dimensionality).
- **A5 (COSINE):** Same as A0 through PCA, but **unit-normalize each row** then cosine-distance PERMANOVA instead of Euclidean. Tests the lit/47 variant-(iv) cosine intuition directly against the inherited Euclidean default.

No other variants will be added during execution. Six = locked alphabet.

## 0.2 Integrity disclosure — what is already known (NOT re-claimable)

- A0 with `{E1, C2, W1, W3, W5}`: median F=5.703 [3.139, 7.525], ref-seed F=4.553, p=0.0193 (P21 result, lit/77 — anchor).
- A0 with `{E1, C2}` (P16 baseline): median F=3.724 [3.354, 4.161] (P21 also reproduced this).

Probe 22 does NOT re-claim A0's transfer F; that's an anchor. The new claims are about the A1-A5 distributions and whether any alt-variant comes within ±10% (or beats by ≥20%) the A0 median under the same 200-seed bootstrap.

## 1. Hypotheses (LOCKED)

- **H22-anchor (F1 sanity):** A0 200-seed median F reproduces P21 anchor 5.703 ± 0.300 (allows for any incidental rounding in the cascade_F variant call sequence; tight).
- **H22-main (architecture sub-optimal):** at least one of {A1, A2, A3, A4, A5} has 200-seed median F > A0 median × 1.20 AND 2.5pct > 3.0 AND ref-seed p < 0.05.
- **H22-secondary (aggregator-robust):** at least one of {A1, A2, A3, A4, A5} has 200-seed median F within ±10% of A0 median AND 2.5pct ≥ A0 2.5pct × 0.85 AND ref-seed p < 0.05. (If H22-main also fires, H22-secondary is implied; this is the "tie" outcome.)
- **H22-null (architecture load-bearing):** all of {A1, A2, A3, A4, A5} have 200-seed median F < A0 median × 0.50 OR 2.5pct < 1.5. (Architecture is necessary; alternatives collapse.)

## 2. Cohort + data (LOCKED — inherited from P21)

- **Train:** Khan (n=19 post `aging_type != excluded`) + SECL first-life (n=10) + Zhang (n=8) = **n=37**. Features `{E1, C2, W1, W3, W5}` augmented from `paper2_operators_{khan,secl}_v2.parquet`; Zhang has only `{E1, C2}` (W-ops NaN → column-mean impute per the P21 protocol).
- **Test:** WMG held-out (n=19, SOH bins {80, 85, 90, 95}). `paper2_operators_wmg_v2.parquet`.
- No new data. No new extraction. Pure aggregator-swap analysis.

## 3. Method (LOCKED)

1. Build the 5-op X-matrices from the existing v2 parquets via the same `safe_cols` pattern P21 uses.
2. For each variant A0–A5, define a `cascade_F_variant(features, rf_seed, Xtr, ytr, Xwmg, soh_bins)` function returning the WMG-only PERMANOVA F per the locked recipe.
3. Run 200-seed bootstrap: for each `b ∈ {0..199}`, compute F_b = cascade_F_variant(..., rf_seed=b). Record median, 2.5pct, 97.5pct per variant.
4. Compute ref-seed F + 10k-perm PERMANOVA p-value at `rf_seed=REF_SEED=42` per variant.
5. Apply §4 falsifiers + §5 dispositions. Write `lit/79_probe22_..._result.md`.

## 4. Falsifiers (LOCKED)

- **P-Probe22_F1 (anchor reproduction):** as H22-anchor. Fail → pipeline broken (the architecture swap shim corrupted the baseline). INVALID.
- **P-Probe22_F2 (same bootstrap seed sequence):** all six variants use the IDENTICAL `b ∈ {0..199}` sequence with `RF random_state=b` where applicable. Pre-commit: verify the seed list matches P21's bootstrap signature (programmatically: same `cascade_F(features, b=42, ...)` returns the documented P21 ref F=4.553 to ±0.01).
- **P-Probe22_F3 (locked alphabet):** the six variants enumerated in §0.1 are the complete set. No mid-run additions, no parameter-sweep on `n_comp` beyond {2, 10, none}.
- **P-Probe22_F4 (CI required, not just median):** any "alt beats A0" claim under H22-main must have 2.5pct > 3.0. A median-only beat with 2.5pct < 1.0 = "MEDIAN-DRIVEN-BY-OUTLIERS," not "ARCHITECTURE-SUBOPTIMAL."
- **P-Probe22_F5 (operator-dominance illusion check):** if ARCHITECTURE-SUBOPTIMAL fires, follow up by checking whether the winning alt-variant's lift comes from a single feature (1D F per feature under the winning aggregator). A single-op-dominated win = same illusion P19 caught with HPPC pulses. Pre-commit: report 1D F for each of the 5 ops under the winning variant.

## 5. Disposition criteria (LOCKED)

| Outcome | Condition | Meaning |
|---|---|---|
| **ARCHITECTURE-SUBOPTIMAL** | H22-main PASS (some alt > A0 × 1.20, 2.5pct > 3.0, p<0.05) AND F5 single-op check passes (lift not from one feature) | An alt-variant materially beats the inherited architecture. lit/47 was a sensible default but not the best aggregator. Paper-3 architecture should be updated. |
| **ARCHITECTURE-SUBOPTIMAL-FRAGILE** | H22-main PASS but F5 fails (winning alt dominated by a single op) | Alt-variant headline lift is mechanically a one-feature artifact. Architecture inherits the load-bearing role; alt is not a legitimate replacement. |
| **AGGREGATOR-ROBUST** | H22-secondary PASS but H22-main FAIL (some alt within ±10%, no alt beats by 20%) | The architecture is interchangeable with at least one simpler aggregator. The lit/47-specific choices are not load-bearing; any sensible aggregator works. Strengthens the operator-selection story (it's the FEATURES that matter, not the cascade). |
| **ARCHITECTURE-LOAD-BEARING** | H22-null PASS (all alts < A0 × 0.5 OR 2.5pct < 1.5) | The full RF→PCA(10)→Euclidean pipeline IS the load-bearing piece. Simpler aggregators collapse on the same features. Strong vindication of the lit/47 amendment. |
| **ARCHITECTURE-PARTIALLY-LOAD-BEARING** | None of {H22-main, H22-secondary, H22-null} fire (some alts tie, some collapse, none beat) | Mixed — architecture choices have a "yes, some matter, some don't" structure. Default catch-all. |
| **PROBE 22 INVALID** | H22-anchor FAIL (A0 doesn't reproduce P21 anchor 5.703 ± 0.300) | Pipeline broken. Debug. |

## 6. What Probe 22 does NOT establish

- Not a new operator claim — features locked to P21's `{E1, C2, W1, W3, W5}`.
- Not a noise-robustness test — clean transfer only; noise audit deferred to P-Probe-22b if AGGREGATOR-ROBUST or ARCHITECTURE-SUBOPTIMAL fires.
- Not a Zhang re-do — Zhang W-op extraction still deferred per P21 §6.
- A POSITIVE "ARCHITECTURE-LOAD-BEARING" verdict doesn't establish lit/47 as optimal; only that the current default is needed against this specific alt-panel.

## 7. Operational protocol

1. Sign-off + commit this pre-reg (lock hash). **Push.**
2. Build `code/c3_probe22_architecture_quirk.py`:
   - Defines `cascade_F_A0..A5` as standalone functions.
   - Reuses `load_training()`, `permanova_F`, `permanova_p`, `REF_SEED`, `N_SEEDS` from `c3_probe15_crosssubstrate_gate`.
   - Loads `paper2_operators_{khan,secl,zhang,wmg}_v2.parquet` from P21.
   - For each variant: 200-seed bootstrap → (median, 2.5pct, 97.5pct, ref F, ref p).
   - Single-op 1D F under the winning variant if H22-main fires.
3. Run. Emit `data/processed/probe22_architecture_quirk_results.parquet` + console table.
4. Apply §4/§5. Write `literature/79_probe22_architecture_quirk_result.md`. Commit + push + lock hashes.

**Cost:** 6 variants × 200 seeds × cascade_F per seed. RF training dominates per-seed cost; should be minutes. No new data, no new extraction.

## 8. Pre-registration deviation log

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |

---

**Lock metadata (to be filled at lock):**
- Lock commit: `<TBD>`
- Analyzer SHA-256: `<TBD>`
- Result parquet SHA-256: `<TBD>`
- Result writeup: `literature/79_probe22_architecture_quirk_result.md` — disposition `<TBD>` after run.
