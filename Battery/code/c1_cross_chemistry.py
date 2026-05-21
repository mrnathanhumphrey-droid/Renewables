"""
C1 hierarchical cross-chemistry pooling model.

Goal: test the central claim that variance attributed to "manufacturing variability"
in single-pool models is partially misclassified design-axis structure. If the
hierarchical model with chemistry_form_factor as a group-level random effect
captures meaningful between-group variance in cell-level residual directions,
then C1 hits and C3 (design parameter inversion) becomes attackable.

Per-cell features:
  Median unit-norm residual-direction vector at flagged RPTs/sweeps.
  Three operators: (Q_max, R_ohmic, R_diff), consistent across alpha/gamma/Khan/Zhang.

Cohorts (4 chemistry-form-factor groups):
  SECL alpha + gamma: NMC/Si-graphite cylindrical, N=10 trajectories
    (4 first-life alpha + 6 second-life gamma)
  Khan 2025: NMC/graphite prismatic, N=19
  Zhang Cambridge v2: LCO/graphite button (LR2032), N=8
  WMG 25-cell (Rashid 2023): NMC811/graphite 21700 cylindrical, N=19 (cross-sectional)

Hierarchical model:
  u[i] = unit residual direction for cell i (3-vector)
  u[i] ~ MVNormal(group_mean[chem_id[i]], cell_cov)
  group_mean[g] ~ MVNormal(grand_mean, group_cov)

Test:
  - Variance decomposition: between-group vs within-group
  - Group-centroid direction differences (do NMC_cyl vs NMC_prism vs LCO_button
    point in interpretably different operator-space directions?)
  - C1 HITS if between-group variance is non-trivial AND directions are
    interpretable in terms of chemistry/form-factor differences
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from pathlib import Path
from scipy import stats


OUT_DIR = Path("D:/Renewables/Battery/data/processed")
THR = float(np.sqrt(stats.chi2.ppf(0.99, df=3)))


def get_secl_alpha_gamma_units():
    """Median unit-norm residual at flagged RPTs from SECL alpha + gamma trajectories."""
    z = pd.read_parquet(OUT_DIR / "mahalanobis_option_x1.parquet")
    z_cols = ["z_Q_max_Ah", "z_R_ohmic_mid", "z_R_diff_mid"]
    units = []
    for traj_id, group in z.groupby("trajectory_id"):
        flagged = group[group["m_dist"] > THR]
        if flagged.empty:
            continue
        v = flagged[z_cols].values
        n = np.linalg.norm(v, axis=1, keepdims=True)
        u = v / np.where(n < 1e-12, 1e-12, n)
        u_med = np.median(u, axis=0)
        u_med = u_med / max(np.linalg.norm(u_med), 1e-12)
        units.append({"cell_traj": traj_id, "chem": "NMC_cyl",
                      "u1": u_med[0], "u2": u_med[1], "u3": u_med[2]})
    return pd.DataFrame(units)


def get_khan_units():
    """Re-derive Khan unit residual directions from features + per-cell day-0 ref."""
    # Walk Khan capacity + EIS, compute per-(cell, day) Q_max + R_ohmic + R_diff at SOC50
    # Use the same logic as khan_extract_and_classify.py
    import sys; sys.path.insert(0, "code")
    from khan_extract_and_classify import (
        extract_qmax_per_cell_per_day, extract_eis_per_cell_per_day, EXCLUDE_CELLS
    )
    cap = extract_qmax_per_cell_per_day()
    eis = extract_eis_per_cell_per_day(soc="S50")
    df = cap.merge(eis, on=["cell_id", "day"], how="inner")
    operators = ["Q_max_Ah", "R_ohmic", "R_diff"]

    # Per-cell day-0 reference (mu), pooled across-cell sd
    cell_mu = {}
    for cell, g in df.groupby("cell_id"):
        d0 = g[g["day"] == 0]
        if d0.empty:
            continue
        cell_mu[cell] = d0[operators].values[0]
    if not cell_mu:
        return pd.DataFrame()
    sd = np.vstack(list(cell_mu.values())).std(axis=0, ddof=1)
    sd = np.where(sd < 1e-12, 1e-12, sd)

    # Pooled cov from day-0 standardized residuals
    z_d0 = []
    for cell in cell_mu:
        z_d0.append((cell_mu[cell] - cell_mu[cell]) / sd)
    # Day-0 z-scores are zero by construction; need cross-cell variation
    # Approximate the cov from across-cell day-0 dispersion:
    day0_vals = np.vstack(list(cell_mu.values()))
    pooled_cov = np.cov(((day0_vals - day0_vals.mean(axis=0)) / sd).T, ddof=1) + 1e-3 * np.eye(3)
    cov_inv = np.linalg.inv(pooled_cov)

    units = []
    for cell, g in df.groupby("cell_id"):
        if cell not in cell_mu:
            continue
        g = g.sort_values("day")
        z = (g[operators].values - cell_mu[cell]) / sd
        d2 = np.einsum("ij,jk,ik->i", z, cov_inv, z)
        flagged_idx = np.where(np.sqrt(d2) > THR)[0]
        if len(flagged_idx) == 0:
            continue
        v = z[flagged_idx]
        n = np.linalg.norm(v, axis=1, keepdims=True)
        u = v / np.where(n < 1e-12, 1e-12, n)
        u_med = np.median(u, axis=0)
        u_med = u_med / max(np.linalg.norm(u_med), 1e-12)
        units.append({"cell_traj": f"Khan_{cell}", "chem": "NMC_prism",
                      "u1": u_med[0], "u2": u_med[1], "u3": u_med[2]})
    return pd.DataFrame(units)


def get_wmg_units():
    """Load pre-computed WMG residual unit vectors.

    WMG is cross-sectional aging: each cell terminates at one SOH stage.
    Residual direction comes directly from (z_Q_max, z_R_ohmic, z_R_diff) at
    the cell's terminal SOH, standardized vs the 5 100SOH controls. No
    per-cell trajectory + per-RPT flagging step needed (one observation per cell).

    See code/wmg_extract_features.py.
    """
    path = OUT_DIR / "wmg_25cell_classification.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    units = []
    for _, r in df.iterrows():
        units.append({"cell_traj": f"WMG_Cell{int(r['cell']):02d}",
                      "chem": "NMC811_cyl",
                      "u1": float(r["u_Q_max"]),
                      "u2": float(r["u_R_ohmic"]),
                      "u3": float(r["u_R_diff"])})
    return pd.DataFrame(units)


def get_zhang_units():
    """Median unit residual from Zhang v2 features parquet."""
    df = pd.read_parquet(OUT_DIR / "zhang_features_v2.parquet")
    operators = ["Q_max", "R_ohmic", "R_diff"]
    # Per-cell standardize using first 3 sweeps as fresh
    cell_mu = {}
    cell_sd = {}
    for cell, g in df.groupby("cell_id"):
        g = g.sort_values("sweep").reset_index(drop=True)
        fresh = g.head(3)
        if len(fresh) < 2:
            continue
        cell_mu[cell] = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        cell_sd[cell] = np.where(sd < 1e-12, 1e-12, sd)
    if not cell_mu:
        return pd.DataFrame()

    # Pooled cov from fresh-period z-scores across cells
    fresh_z_pool = []
    for cell, g in df.groupby("cell_id"):
        if cell not in cell_mu:
            continue
        g = g.sort_values("sweep").reset_index(drop=True)
        fresh = g.head(3)
        z = (fresh[operators].values - cell_mu[cell]) / cell_sd[cell]
        fresh_z_pool.append(z)
    pooled_cov = np.cov(np.vstack(fresh_z_pool).T, ddof=1) + 1e-3 * np.eye(3)
    cov_inv = np.linalg.inv(pooled_cov)

    units = []
    for cell, g in df.groupby("cell_id"):
        if cell not in cell_mu:
            continue
        g = g.sort_values("sweep").reset_index(drop=True)
        z = (g[operators].values - cell_mu[cell]) / cell_sd[cell]
        d2 = np.einsum("ij,jk,ik->i", z, cov_inv, z)
        flagged_idx = np.where(np.sqrt(d2) > THR)[0]
        if len(flagged_idx) == 0:
            continue
        v = z[flagged_idx]
        n = np.linalg.norm(v, axis=1, keepdims=True)
        u = v / np.where(n < 1e-12, 1e-12, n)
        u_med = np.median(u, axis=0)
        u_med = u_med / max(np.linalg.norm(u_med), 1e-12)
        units.append({"cell_traj": f"Zhang_{cell}", "chem": "LCO_button",
                      "u1": u_med[0], "u2": u_med[1], "u3": u_med[2]})
    return pd.DataFrame(units)


def main():
    print("=== Building cross-chemistry cohort ===")
    secl = get_secl_alpha_gamma_units()
    khan = get_khan_units()
    zhang = get_zhang_units()
    wmg = get_wmg_units()
    print(f"  SECL  alpha+gamma (NMC/Si-graphite cylindrical): N={len(secl)}")
    print(f"  Khan  2025        (NMC/graphite prismatic):      N={len(khan)}")
    print(f"  Zhang v2          (LCO/graphite button):         N={len(zhang)}")
    print(f"  WMG   25-cell     (NMC811/graphite 21700 cyl):   N={len(wmg)}")
    all_units = pd.concat([secl, khan, zhang, wmg], ignore_index=True)
    print(f"  Total: N={len(all_units)}\n")

    print("=== Cohort-level mean residual direction (raw) ===")
    for chem, g in all_units.groupby("chem"):
        mean_u = g[["u1", "u2", "u3"]].mean().values
        mean_u_norm = mean_u / max(np.linalg.norm(mean_u), 1e-12)
        print(f"  {chem:15s} N={len(g):3d} mean unit = ({mean_u_norm[0]:+.3f}, {mean_u_norm[1]:+.3f}, {mean_u_norm[2]:+.3f})")

    chems = ["NMC_cyl", "NMC_prism", "LCO_button", "NMC811_cyl"]
    chem_id = all_units["chem"].map(lambda c: chems.index(c)).values.astype(int)
    u_obs = all_units[["u1", "u2", "u3"]].values.astype(float)
    n_groups = len(chems)
    n = len(all_units)

    print("\n=== Hierarchical Bayesian model ===")
    with pm.Model() as m:
        # Group-level mean (grand mean)
        grand_mean = pm.Normal("grand_mean", mu=0.0, sigma=1.0, shape=3)
        # Between-group sd per axis
        sigma_group = pm.HalfNormal("sigma_group", sigma=0.5, shape=3)
        # Group means as offsets from grand
        group_mean_offset = pm.Normal("group_offset", mu=0.0, sigma=1.0, shape=(n_groups, 3))
        group_mean = pm.Deterministic("group_mean", grand_mean + sigma_group * group_mean_offset)
        # Within-group sd
        sigma_cell = pm.HalfNormal("sigma_cell", sigma=0.5, shape=3)
        # Observation
        pm.Normal("u_obs", mu=group_mean[chem_id], sigma=sigma_cell, observed=u_obs)
        idata = pm.sample(2000, tune=1500, chains=4, target_accept=0.95,
                          random_seed=42, progressbar=False)

    print("\n=== Posterior summary ===")
    print(az.summary(idata, var_names=["grand_mean", "sigma_group", "sigma_cell", "group_mean"], round_to=3))

    # Variance decomposition: between-group vs within-group
    sg = idata.posterior["sigma_group"].values.reshape(-1, 3)
    sc = idata.posterior["sigma_cell"].values.reshape(-1, 3)
    var_ratio = (sg**2) / (sg**2 + sc**2)
    print("\n=== Variance decomposition (between-group / total per axis) ===")
    for k, axis_name in enumerate(["u1 (Q_max)", "u2 (R_ohmic)", "u3 (R_diff)"]):
        q025, q50, q975 = np.quantile(var_ratio[:, k], [0.025, 0.5, 0.975])
        print(f"  {axis_name}: median {q50*100:.1f}%, 95% CI [{q025*100:.1f}%, {q975*100:.1f}%]")

    # Group centroid directions (median posterior)
    print("\n=== Posterior group-centroid directions (median) ===")
    gm = idata.posterior["group_mean"].values
    gm_flat = gm.reshape(-1, n_groups, 3)
    for i, name in enumerate(chems):
        med = np.median(gm_flat[:, i, :], axis=0)
        med_norm = med / max(np.linalg.norm(med), 1e-12)
        print(f"  {name:15s} centroid unit = ({med_norm[0]:+.3f}, {med_norm[1]:+.3f}, {med_norm[2]:+.3f})")

    # Pairwise group separation
    print("\n=== Pairwise group-centroid cosine angle ===")
    pairs = [(i, j) for i in range(n_groups) for j in range(i+1, n_groups)]
    for i, j in pairs:
        cos_angles = []
        for s in range(gm_flat.shape[0]):
            a = gm_flat[s, i]; b = gm_flat[s, j]
            cos = np.dot(a, b) / max(np.linalg.norm(a) * np.linalg.norm(b), 1e-12)
            cos_angles.append(cos)
        cos_angles = np.array(cos_angles)
        med = np.median(cos_angles)
        q025, q975 = np.quantile(cos_angles, [0.025, 0.975])
        print(f"  {chems[i]:15s} vs {chems[j]:15s}: median cos = {med:+.3f} (1.0=same), 95% CI [{q025:+.3f}, {q975:+.3f}]")

    all_units.to_parquet(OUT_DIR / "c1_cell_units.parquet")
    print(f"\nWritten: {OUT_DIR / 'c1_cell_units.parquet'}")


if __name__ == "__main__":
    main()
