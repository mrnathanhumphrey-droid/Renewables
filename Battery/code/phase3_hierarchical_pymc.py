"""
Phase 3 hierarchical Bayesian model — PyMC implementation.

Lead-time data from literature/12_phase3_full_first_life.md (N=7 first-life):
  Triad alpha (Q_max + EIS bands):
    V4:  +25 cyc lead
    W8:    0 cyc
    W9:  +24
    W10: +29
  Triad beta (Q_max + HPPC features):
    G1:    0
    W4:  +53
    W5:  +42

Model:
  lead_time[i] ~ Normal(mu_pop + beta_triad[triad[i]], sigma_cell)
  mu_pop ~ Normal(0, 100)        # weakly informative, centered at zero
  beta_triad[a] ~ Normal(0, 50)  # triad fixed effects
  sigma_cell ~ HalfNormal(50)

Headline statistic: posterior on mu_pop (population mean lead time).
Pre-reg falsification: 95% credible-interval lower bound > 50 cycles.

Note: lifecycle effect not yet included because we only have first-life cells
with valid knee-detection. Second-life requires day-axis trajectory work
(separate script).
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az


# From combined_alpha_beta_leadtime.py — locked at commit 30d2792
DATA = pd.DataFrame([
    {"cell": "V4",  "triad": "alpha", "lead_cyc": 25},
    {"cell": "W8",  "triad": "alpha", "lead_cyc": 0},
    {"cell": "W9",  "triad": "alpha", "lead_cyc": 24},
    {"cell": "W10", "triad": "alpha", "lead_cyc": 29},
    {"cell": "G1",  "triad": "beta",  "lead_cyc": 0},
    {"cell": "W4",  "triad": "beta",  "lead_cyc": 53},
    {"cell": "W5",  "triad": "beta",  "lead_cyc": 42},
])


def main():
    triad_idx = {t: i for i, t in enumerate(["alpha", "beta"])}
    DATA["triad_id"] = DATA["triad"].map(triad_idx)
    y = DATA["lead_cyc"].values.astype(float)
    triad = DATA["triad_id"].values.astype(int)
    n = len(DATA)

    print(f"N = {n}; raw mean = {y.mean():.2f} cyc; raw sd = {y.std(ddof=1):.2f}\n")

    with pm.Model() as model:
        mu_pop = pm.Normal("mu_pop", mu=0.0, sigma=100.0)
        beta_triad = pm.Normal("beta_triad", mu=0.0, sigma=50.0, shape=2)
        sigma_cell = pm.HalfNormal("sigma_cell", sigma=50.0)
        mu_per_cell = mu_pop + beta_triad[triad]
        pm.Normal("lead", mu=mu_per_cell, sigma=sigma_cell, observed=y)
        idata = pm.sample(2000, tune=1500, chains=4, target_accept=0.95,
                          random_seed=42, progressbar=False)

    # Posterior summary
    print("=== Posterior summary ===")
    print(az.summary(idata, var_names=["mu_pop", "beta_triad", "sigma_cell"], round_to=3))

    posterior_mu = idata.posterior["mu_pop"].values.flatten()
    print(f"\n=== Headline: mu_pop posterior ===")
    print(f"  Posterior mean:       {posterior_mu.mean():+.2f} cyc")
    print(f"  Posterior SD:         {posterior_mu.std():.2f}")
    q025, q50, q975 = np.quantile(posterior_mu, [0.025, 0.5, 0.975])
    q05 = np.quantile(posterior_mu, 0.05)
    print(f"  95% credible interval: [{q025:+.2f}, {q975:+.2f}]")
    print(f"  Median:                {q50:+.2f}")
    print(f"  95% one-sided LCB:     {q05:+.2f}")

    print(f"\n=== Pre-reg falsification (95% LCB > 50 cyc) ===")
    if q05 > 50:
        print(f"  PASS: posterior lower bound {q05:.2f} exceeds 50-cyc threshold")
    elif q05 > 0:
        print(f"  PARTIAL: posterior lower bound positive ({q05:.2f}) but below 50-cyc threshold")
    else:
        print(f"  NULL: posterior lower bound includes zero")

    # P(mu > 0) and P(mu > 50)
    p_pos = float((posterior_mu > 0).mean())
    p_50 = float((posterior_mu > 50).mean())
    print(f"\n=== Posterior probabilities ===")
    print(f"  P(mu_pop > 0)  = {p_pos:.4f}")
    print(f"  P(mu_pop > 50) = {p_50:.4f}")

    # Per-triad posteriors
    bt = idata.posterior["beta_triad"].values
    bt = bt.reshape(-1, 2)
    print(f"\n=== Triad fixed effects ===")
    for i, name in enumerate(["alpha", "beta"]):
        q025_b, q50_b, q975_b = np.quantile(bt[:, i], [0.025, 0.5, 0.975])
        print(f"  beta_triad[{name}]: median {q50_b:+.2f} cyc, 95% CI [{q025_b:+.2f}, {q975_b:+.2f}]")

    # Compare to the frequentist 95% LCB +10.21 cyc
    print(f"\n=== Comparison vs frequentist N=7 result ===")
    print(f"  Frequentist 95% one-sided LCB: +10.21 cyc")
    print(f"  Bayesian   95% one-sided LCB:  {q05:+.2f} cyc")
    print(f"  Difference: shrinkage of Bayesian estimate toward prior (centered at 0)")


if __name__ == "__main__":
    main()
