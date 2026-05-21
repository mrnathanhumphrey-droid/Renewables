# Phase 2.2 — Hierarchical Bayesian Model Design

**Date:** 2026-05-21
**Backend:** Stan (consistent with NHL / NFL / NBA projection projects). PyMC kept as fallback if Stan compilation friction.
**Purpose:** Specify the joint conditional null model under which inter-operator disagreement onset is measured.

---

## What the model has to do

Given the locked cohort (N=16 cells across three operator triads), the model must:

1. **Per cell, per RPT, produce a posterior over each operator's expected response** conditioned on operating conditions and the cell's healthy-state latent variables.
2. **Define a joint disagreement statistic** that aggregates per-operator residuals into one scalar per (cell, cycle).
3. **Locate the onset cycle** where this statistic exceeds a pre-specified threshold for K consecutive cycles.
4. **Compare** the per-cell onset cycle to the cell's capacity-knee-point cycle.
5. **Pool** across cells via hierarchical structure with triad and lifecycle fixed effects.

The conditional null = the model's prediction under "healthy" operation (early-RPT data). Disagreement-onset = the cycle where the joint signal stops looking like the null.

---

## Model structure (high-level)

### Level 1 — per-operator marginal nulls (one model per operator)

Each operator is modeled as a function of conditioning variables, capacity-fade-normalized so it's expressed in a comparable scale across cells.

**Capacity operator (electrical):**
```
Q_observed[c, r, t] = Q_max[c, r] · g_Q(SOC[t]; θ_Q[c]) + ε_Q
```
where `Q_max[c, r]` is the per-cell, per-RPT measured capacity (the actual aging signal) and `g_Q` is the normalized SOC-vs-capacity curve. The aging signal is in how `Q_max` evolves across RPTs.

**Thermal operator (when available — Triad α and β):**
```
T_cell[c, t] | I[t], T_amb, internal_state = h_T(I[t], R_int[c, r], T_amb) + ε_T
```
where `R_int[c, r]` is the per-RPT internal resistance (derived from HPPC). Aging shows as `R_int` increase.

**EIS operator (Triad α and γ):**
- Decompose each spectrum (re_z, im_z) at given SOC into three frequency-band sub-statistics:
  - **Ohmic:** Re(Z) at highest frequency (10 kHz first-life, max in second-life) ≈ pure electrolyte/contact resistance
  - **Charge-transfer:** Re(Z) at mid-frequency semicircle peak (~1-100 Hz region)
  - **Diffusion:** Re(Z) at lowest frequency (10 mHz) ≈ Warburg tail magnitude
- Each band acts as an operator under the C2 framework.
- For Triad γ (second-life, no thermal): ohmic + diffusion bands serve as 2nd and 3rd operators alongside electrical capacity.

**HPPC operator (Triad β only):**
```
ΔV_pulse[c, r, soc] = I_pulse · R_DC[c, r, soc] + transient(τ[c, r, soc])
```
Two scalar features per RPT: DC resistance `R_DC` (ohmic component) and time constant `τ` (capacitive/diffusive). Both grow with aging.

### Level 2 — joint hierarchical structure

```
operator_residual[c, r, k] = (operator_k[c, r] − predicted_operator_k[c, r]) / σ_k

joint_distance[c, r] = sqrt( residual^T · Σ_inv · residual )   # Mahalanobis
```

where `Σ` is the residual covariance matrix estimated from the first 3 RPTs of each cell (the "fresh" reference period). Under the null, `joint_distance` is approximately χ² with k degrees of freedom and a small mean.

### Level 3 — onset detection (per cell)

```
onset_cycle[c] = first cycle r* such that
                  joint_distance[c, r] > threshold for K consecutive RPTs
```

`threshold` and `K` are hyperparameters pre-specified in Phase 3 pre-reg. Candidates:
- `threshold` = 99th percentile of fresh-period joint_distance (per-cell or pooled)
- `K` = 2 (two consecutive RPTs above threshold to call onset, suppresses single-RPT noise)

### Level 4 — population pooling

```
lead_time[c] = capacity_knee_cycle[c] − onset_cycle[c]

lead_time[c] ~ Normal(μ_LT + β_triad · triad[c] + β_life · lifecycle[c], σ_cell)
μ_LT ~ Normal(0, 200)        # prior centered at zero (null), 200-cycle width
β_triad ~ Normal(0, 50)
β_life ~ Normal(0, 50)
σ_cell ~ HalfNormal(100)
```

**Headline statistic:** `μ_LT` posterior 95% lower credible bound. Pre-reg falsification = bound > 50 cycles.

---

## Conditioning variable handling

| Variable | Per-RPT or per-cycle | How it enters the model |
|---|---|---|
| SOC at measurement | Per-RPT | Discrete factor (20/50/80% for first-life EIS); continuous covariate inside per-RPT operator-marginal model |
| Chamber T | Per-cycle, per-RPT | Per-cell constant (23 °C first-life, 25 °C second-life). Enters as fixed-offset in thermal-operator equation |
| Cycle count at RPT | Per-RPT | Mapped from RPT index via cycling_tests folder names. This is the **x-axis** of the onset-detection trajectory |
| Calendar age at RPT | Per-RPT | From timestamps. Used to separate calendar vs cycle aging contributions (relevant for Khan 2025 calendar arm) |
| Cycle C-rate (preceding segment) | Per-cycle | From filename encoding (CC_3C etc.). Enters as covariate in capacity-fade marginal |
| SOC window (preceding) | Per-cycle | From filename (SOC20_80 etc.). Covariate in capacity-fade marginal |
| Cell ID | Per-cell | Random effect, varying intercept (and slope where data supports it) |
| Triad (operator availability) | Per-cell | Fixed effect on lead_time pooling |
| Lifecycle stage | Per-cell | Fixed effect; first-life vs second-life |

---

## Independence assumptions (Phase 2.3 task 1.6 carryover)

The joint null assumes operator residuals are **conditionally independent** given conditioning variables. Where this is approximate:

| Pair | Coupling | Conditional independence holds? |
|---|---|---|
| Electrical × Thermal | Joule heating (I²R) | Approximate. Conditional on `R_int` and `I[t]`, residuals decouple. **Document and check.** |
| Electrical × EIS | EIS is measured at controlled SOC, not during cycling | Effectively independent at RPT timescale |
| Thermal × EIS | EIS at 25 °C controlled; thermal-operator at chamber-controlled cycling T | Effectively independent |
| EIS-ohmic × EIS-diffusion | Same spectrum, different frequency bands | **Not independent within a single spectrum** — must use covariance-aware joint statistic, not product-of-marginals |
| HPPC × Electrical | HPPC measured during dedicated pulse RPT, not during cycling | Independent at RPT timescale |
| HPPC × Thermal | HPPC at 25 °C; thermal-during-cycling at chamber T | Effectively independent |

The within-EIS sub-operator coupling (ohmic × diffusion within Triad γ) is the main concern. Two options:
1. Use the full residual covariance matrix from fresh-period spectra (preferred — the joint Mahalanobis statistic naturally absorbs this)
2. Pre-transform with PCA / Cole-Cole fit to decorrelate before treating bands as independent operators

**Recommendation: option 1.** The joint distance under a fitted covariance handles dependence automatically. Phase 2.5 posterior predictive checks should explicitly verify covariance matches in fresh-period data before trusting it for disagreement-onset detection.

---

## Stan program outline (what gets implemented next)

```stan
data {
  int<lower=1> N_cells;
  int<lower=1> N_rpts_total;       // total RPT observations across all cells
  int<lower=1> N_operators;        // 3 (per-cell triad has 3 operators)
  int<lower=1> N_triads;           // 3 (alpha/beta/gamma)
  int<lower=1> N_lifecycles;       // 2 (first/second)

  int<lower=1, upper=N_cells> cell_idx[N_rpts_total];
  int<lower=1, upper=N_triads> triad_idx[N_cells];
  int<lower=1, upper=N_lifecycles> lifecycle_idx[N_cells];
  real cycle_count[N_rpts_total];

  matrix[N_rpts_total, N_operators] operator_obs;   // pre-normalized per-cell residuals
  // ... conditioning variables
}

parameters {
  // operator-marginal fresh-period reference (from RPTs 1-3)
  vector[N_operators] mu_op[N_cells];
  cholesky_factor_corr[N_operators] L_corr[N_cells];
  vector<lower=0>[N_operators] sigma_op[N_cells];

  // population-level
  real mu_LT;
  vector[N_triads] beta_triad;
  vector[N_lifecycles] beta_life;
  real<lower=0> sigma_cell;
  vector[N_cells] z_cell;     // cell random effect
}

model {
  // priors
  mu_LT ~ normal(0, 200);
  beta_triad ~ normal(0, 50);
  beta_life ~ normal(0, 50);
  sigma_cell ~ normal(0, 100);
  z_cell ~ std_normal();

  // per-cell operator multivariate normal (fresh-period covariance)
  // ... [joint operator likelihood]

  // lead time likelihood (after onset detection in generated quantities)
  // ... [population pooling on lead times]
}

generated quantities {
  // posterior predictive operator residuals
  // onset cycle per cell (deterministic post-fit)
  // lead time per cell
  // 95% lower bound on mu_LT
}
```

---

## Phase 2 task status post-design

- 2.1 ✅ Conditioning variables specified
- 2.2 ✅ Model structure designed (this doc)
- 2.3 ⏳ Marginal null fitting per operator — first implementation step
- 2.4 ⏳ Fit on fresh-period data (RPTs 1-3 of each cell)
- 2.5 ⏳ Posterior predictive checks on fresh-period covariance

Next push: write the operator-normalization pipeline (RPT → per-cell normalized residual matrix), then the first cut of the Stan model. Start with capacity operator alone as a single-operator sanity check, then layer in thermal, then EIS bands.

---

## Open carryover

- Cycle-count mapping from RPT index to cumulative cycle count — needs README.xlsx or filename parsing pass on cycling_tests folders
- Triad-β HPPC features still to be designed (`R_DC` and `τ` extraction from pulse data)
- Khan 2025 + Zhang Cambridge integration into Phase 4 (not blocking Phase 2/3)
