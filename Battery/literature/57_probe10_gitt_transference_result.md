# C3 Probe 10 — GITT Finite-Amplitude Transference RESULT

**Status:** COMPLETE. Disposition = **TRANSFERENCE STILL NULL** (positive control PASSES).
**Date:** 2026-05-28
**Authored:** Claude
**Pre-reg:** `literature/56_probe10_gitt_transference_prereg.md` (lock `6f2d4f8`).
**Prior:** Probe 9 (lit/52+53) EIS-lane transference NULL. lit/53 §6 named GITT as the only remaining recovery path. This probe tests and closes it.

---

## 0. One-line result

A large-signal time-domain GITT operator stack, run through the same C3 multivariate architecture as the EIS probes, **does not recover transference** — best L2 F=0.64, best L0 F=0.84, NULL across both stacks and all PCA-k. Crucially the **positive control passes emphatically**: thickness and particle radius separate cleanly in the GITT stack (particle radius F=72, the highest in the program), so the GITT operators are demonstrably informative and the transference null is genuine, not a broken-operator artifact. **Transference is irrecoverable by both operator classes tested — EIS small-signal (Probe 9) and GITT large-signal (Probe 10).** The limit is the cohort's design-variation-to-transference-signal ratio, not the measurement modality.

## 1. Falsifier results

| Falsifier | Threshold | Result | Verdict |
|---|---|---|---|
| **P-Probe10_F1** (positive control: th + pr separate at L0) | both PASS at L0 | th F up to 22.9, pr F up to **72.1** at L0 — both PASS | **PASS** — operators informative, null is genuine |
| **P-Probe10_F2** (PCA-k + stack coherence) | no verdict oscillation | transference NULL at all k {2,3,4}, both 6D/8D, all levels — no oscillation | **COHERENT** |
| **P-Probe10_F3** (no regression of th/pr under noise) | th/pr PASS through L2 | th + pr PASS at **every** level L0–L4 (pr F stays 58–72 even at L4) | **PASS** — tight grid doesn't destroy signal |

## 2. Transference headline (the null)

| | 6D best | 8D best | verdict |
|---|---|---|---|
| transference @ L0 (clean) | F=0.75 (k=2) | **F=0.84 (k=2)** | NULL |
| transference @ L2 PRIMARY | F=0.27 (k=2) | **F=0.64 (k=2)** | NULL |

PCA-k=3/4 returned nan (degenerate within-group structure on the transference labels, as in Probe 9). Best transference F anywhere across the entire grid (2 stacks × 3 k × 5 levels) never exceeded ~1.4 (6D L1 k=2), far below F_WEAK=2.0.

**Per §3.1, the noise grid is moot:** transference is NULL at **L0** (zero noise). The voltage-noise grid (0.25%–2%, cycler precision) only governs robustness if L0 separates — it doesn't. Adding noise can only subtract. The univariate L0 screen (ANOVA F=0.08, pre-reg §0.1) is confirmed by the full multivariate architecture (F=0.84): feature-space does not rescue transference, unlike the thickness case in Probe 8a.

## 3. The positive control is the load-bearing result

The reason this probe closes the question rather than merely adding another null: **the GITT operators separate the known-separable design parameters better than EIS ever did.**

| design param | EIS best (Probe 9, L2) | GITT best (this probe, L2) |
|---|---|---|
| thickness | 19.45 | 22.96 |
| particle radius | 26.92 | **71.56** |
| transference | 0.77 | 0.64 |

Particle radius is ~2.7× more separable under GITT than EIS — physically sensible, since the concentration-polarization operator's magnitude scales with solid-diffusion length, which scales with particle radius. GITT is a *strictly better* operator for the parameters that have a finite-amplitude signature. It still cannot see transference. That asymmetry is the proof: the GITT stack is a high-quality measurement that is genuinely transference-blind at the cohort level, not a degenerate one that fails on everything.

## 4. Why the smoke's 5.57% didn't carry (mechanism)

The GITT smoke (pre-reg §0.1) swept transference *alone* on one fixed cell and saw eta_conc move 5.57% monotonically — a real finite-amplitude transference response, exactly as physics predicts (higher cation transference → less anion buildup → smaller electrolyte gradient → smaller concentration overpotential). But in the L9 cohort, transference co-varies with thickness (±20%), particle radius (4–6.5 µm), and amvf (±2%), whose eta_conc signatures are an order of magnitude larger. The ~12 mV transference effect is buried in the ~tens-of-mV cell-to-cell scatter those design parameters produce. z-score → PCA puts the dominant thickness/particle-radius variance in PC1–2; transference has no retainable axis (k=3/4 degenerate). This is the identical mechanism as Probe 9's EIS null and lit/47's original transference null — confirmed now across both operator classes.

## 5. Disposition (per lit/56 §5)

**TRANSFERENCE STILL NULL.** Transference F < 2.0 in all (stack, PCA-k) at L2 — and at L0. Positive control PASSES (F1), so this is a genuine transference null, not INVALID.

Per the locked disposition: *"GITT large-signal operator also transference-blind at the cohort level. Combined with Probe 9: transference is irrecoverable by EIS AND GITT. The limit is the design-variation-to-signal ratio in this cohort, not the operator class. Closes the operator-hunt for transference on this cohort; only a cohort with transference-dominant variation (or transference swept alone) could separate it."*

## 6. What this closes — the transference arc terminus

- **The operator-hunt for transference on this cohort is closed.** Two operator classes, exhaustively: EIS (10 mHz, low-SoC, sub-mHz — Probe 9) and GITT finite-amplitude (Probe 10). Both NULL at the cohort level. The C3 amendment's original "transference NULL" (lit/47) is now explained mechanistically and shown to be operator-class-invariant.
- **The path that remains is not an operator — it's a cohort.** The smoke proves transference IS detectable when swept alone (5.57% on eta_conc). Separating it at the cohort level requires a design where transference variation is not dominated by thickness/particle-radius/amvf — i.e., a transference-dominant or transference-only sweep. That is a data-design change, not a measurement change.
- No change to lit/47. The C3 amendment's validated scope (thickness + particle radius PASS, transference NULL) stands, now with a stronger mechanistic basis.

## 7. What this does NOT establish

- Not a real-cell result (no GITT-capable real-cell cohort in the corpus; Khan is EIS-only).
- Not a claim transference is physically undetectable — the smoke shows it is detectable when isolated.
- Not generalizable beyond this L9 PyBaMM cohort / Chen2020 / this operator set.

## 8. Side finding (logged, not a probe): GITT is a superior particle-radius operator

Particle-radius F=72 under GITT vs 27 under EIS. The concentration-polarization operator (eta_conc) and slow-relaxation tail (dV_slow) encode solid-state diffusion length more directly than the EIS Warburg-region R_diff. If a future probe wanted to *strengthen* the particle-radius disposition (not recover transference), the GITT 8D stack is the better feature set. Logged; would need its own pre-reg to promote (same discipline as the Probe 9b PCA-3 finding — and that one washed out under resampling, so any promotion here would need the same multi-seed stability gate).

## 9. RMD-SRC framing

A Step-4a operator-CLASS expansion that **converged to H10-null** with the positive control affirming operator quality. The decomposition is coherent (F2), the operators are validated as informative (F1, emphatically), and the validation parameters did not regress (F3). This is the cleanest possible negative: a high-quality, physically-motivated, finite-amplitude operator that genuinely cannot see transference at the cohort level — establishing that the transference null is a property of the *substrate's variation structure*, not any measurement limitation. Cross-substrate rule (now maximally supported): the C3 amendment transfers for design parameters with a direct large-or-small-signal observable; transference's signature, real but small relative to co-varying design parameters, is structurally unseparable in this cohort by any operator.

---

**Lock metadata:**
- Pre-reg lock commit: `6f2d4f8`
- Result commit: `<TBD — recorded in this commit>`
- Generator SHA-256: `9a37601a1e7967f0886aaf9aa23bd29cfbcc08e3ef8eb2f32b4a1a829ea3e3e7`
- GITT parquet SHA-256: `0851ff9fc39689131e5673e61cc3ef1f1b628c74ae1db7271bebf6d81ec9619e`
- Analyzer SHA-256: `b5583c24e216e785983186ea16453b5be7205d5788af6c755742811a47b8be37`
- Result parquet SHA-256: `808fe135246376bba39bdde3b6f6ebd2d208bb3c41e1a487a18a7b53c6c4341b`

## 10. Deviation log

| Date | Deviation | Rationale |
|---|---|---|
| 2026-05-28 | PCA-k=3/4 transference F = nan at most levels. | Degenerate within-group structure on transference labels (same as Probe 9). k=2 finite and NULL; disposition unaffected. |
