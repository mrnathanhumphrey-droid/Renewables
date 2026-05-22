"""
Paper 2 — Cascade noise-injection probe (literature/32, locked 7633f7e).

Procedure:
1. Re-train the literature/31 cascade exactly (deterministic seed=42).
2. For each of 5 noise levels per literature/25 §3 / literature/32 §3, inject
   multiplicative Gaussian noise per cycle on Q_max, R_DC, R_total trajectories
   of PyBaMM-holdout cells (36 cells, deterministic split per literature/28 §2).
3. Re-extract the 7 amended-Gate-II-surviving operators from the noisified
   trajectories using paper2_extract_others._slope / _knee_onset.
4. Apply the SAME training scaler, the SAME trained RF, the SAME PCA from
   the noise-free cascade. Project noisy holdout into the embedding space.
5. PERMANOVA on the noisy holdout embedding labeled by L9 cond_idx.
6. Apply §5 verdict.

Per literature/32 §4: PASS at Level 2 = F > 3.0 AND p < 0.05. Other levels
are calibration curve descriptive.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

# Reuse extraction primitives
from paper2_extract_others import _slope, _knee_onset

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND_CSV = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
RNG_SEED = 42
N_PERMUTATIONS = 10000

RF_PARAMS = dict(
    n_estimators=500, max_depth=4, min_samples_leaf=5,
    class_weight="balanced", random_state=RNG_SEED, n_jobs=-1,
)

SURVIVORS = [
    "T1_Q_fade_early", "T2_Q_fade_late", "T3_Q_knee_onset",
    "T4_R_DC_growth_rate", "T5_R_DC_acceleration",
    "C1_R_growth_per_Q_lost", "C2_R_DC_to_R_total",
]

# literature/32 §3 noise levels
NOISE_LEVELS = [
    dict(level=0, sigma_Q=0.000, sigma_R_DC=0.00, sigma_R_total=0.00, label="baseline"),
    dict(level=1, sigma_Q=0.001, sigma_R_DC=0.05, sigma_R_total=0.10, label="best-in-class lab"),
    dict(level=2, sigma_Q=0.005, sigma_R_DC=0.15, sigma_R_total=0.20, label="typical academic"),
    dict(level=3, sigma_Q=0.010, sigma_R_DC=0.30, sigma_R_total=0.30, label="noisy field"),
    dict(level=4, sigma_Q=0.020, sigma_R_DC=0.50, sigma_R_total=0.50, label="instrument-issue"),
]


def extract_operators_from_trajectory(rpts):
    """Re-extract the 7 amended-Gate-II survivors from a list of per-cycle dicts."""
    cycle = np.array([p["cycle"] for p in rpts], dtype=float)
    q = np.array([p["Q_max"] for p in rpts], dtype=float)
    r_dc = np.array([p["R_DC"] for p in rpts], dtype=float)
    r_tot = np.array([p["R_total"] for p in rpts], dtype=float)
    n = len(cycle)

    r = {op: float("nan") for op in SURVIVORS}
    if n >= 5:
        n_early = max(3, n // 4)
        r["T1_Q_fade_early"] = _slope(cycle[:n_early], q[:n_early])
        r["T2_Q_fade_late"] = _slope(cycle[-n_early:], q[-n_early:])
    r["T3_Q_knee_onset"] = _knee_onset(cycle, q)
    if n >= 5:
        r["T4_R_DC_growth_rate"] = _slope(cycle[:max(3, n//4)], r_dc[:max(3, n//4)])
        try:
            r_dc_fin = r_dc[np.isfinite(r_dc)]
            cs = cycle[np.isfinite(r_dc)]
            if len(r_dc_fin) >= 5:
                win = min(7, (len(r_dc_fin) - 1) | 1)
                if win >= 5 and win % 2 == 1:
                    rs = savgol_filter(r_dc_fin, win, polyorder=2)
                    d2 = np.gradient(np.gradient(rs, cs), cs)
                    r["T5_R_DC_acceleration"] = float(np.max(np.abs(d2)))
        except Exception:
            pass
    if np.isfinite(r["T4_R_DC_growth_rate"]) and np.isfinite(r["T2_Q_fade_late"]) and abs(r["T2_Q_fade_late"]) > 1e-12:
        r["C1_R_growth_per_Q_lost"] = r["T4_R_DC_growth_rate"] / abs(r["T2_Q_fade_late"])
    fresh_r_dc = r_dc[:5] if n >= 5 else r_dc
    fresh_r_tot = r_tot[:5] if n >= 5 else r_tot
    denom = float(np.nanmean(fresh_r_tot)) if len(fresh_r_tot) else float("nan")
    if abs(denom) > 1e-12:
        r["C2_R_DC_to_R_total"] = float(np.nanmean(fresh_r_dc)) / denom
    return r


def inject_noise_and_extract(rpts, sigma_Q, sigma_R_DC, sigma_R_total, seed):
    """Apply per-cycle multiplicative Gaussian noise, then extract operators."""
    rng = np.random.default_rng(seed)
    noisy = []
    for p in rpts:
        eps_Q = rng.normal(0, sigma_Q) if sigma_Q > 0 else 0.0
        eps_R_DC = rng.normal(0, sigma_R_DC) if sigma_R_DC > 0 else 0.0
        eps_R_tot = rng.normal(0, sigma_R_total) if sigma_R_total > 0 else 0.0
        noisy.append({
            "cycle": p["cycle"],
            "Q_max": p["Q_max"] * (1 + eps_Q),
            "R_DC": p["R_DC"] * (1 + eps_R_DC),
            "R_total": p["R_total"] * (1 + eps_R_tot),
        })
    return extract_operators_from_trajectory(noisy)


def get_holdout_cell_ids():
    """Return the set of (cond_idx, cell_idx) tuples in PyBaMM-holdout per literature/28 §2."""
    holdout_df = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_holdout.parquet")
    return set(zip(holdout_df["cond_idx"].astype(int), holdout_df["cell_idx"].astype(int)))


def permanova_one_way(X, labels, n_perm=N_PERMUTATIONS, seed=RNG_SEED):
    """One-way PERMANOVA with permutation p-value (Euclidean on embedding)."""
    from scipy.spatial.distance import pdist, squareform
    rng = np.random.default_rng(seed)
    D = squareform(pdist(X, metric="euclidean"))
    n = len(labels)
    levels = pd.Series(labels).unique()
    a = len(levels)

    def ss_within(perm_labels):
        ss = 0.0
        for lvl in levels:
            idx = np.where(perm_labels == lvl)[0]
            if len(idx) < 2:
                continue
            sub = D[np.ix_(idx, idx)]
            ss += (sub ** 2).sum() / (2 * len(idx))
        return ss

    ss_w_obs = ss_within(np.asarray(labels))
    ss_t = (D ** 2).sum() / (2 * n)
    ss_b_obs = ss_t - ss_w_obs
    df_b = a - 1
    df_w = n - a
    if ss_w_obs <= 0 or df_b == 0:
        return float("nan"), float("nan"), df_b, df_w
    F_obs = (ss_b_obs / df_b) / (ss_w_obs / df_w)
    n_ge = 1
    for _ in range(n_perm):
        perm = rng.permutation(np.asarray(labels))
        sw = ss_within(perm)
        sb = ss_t - sw
        if sw > 0:
            F_perm = (sb / df_b) / (sw / df_w)
            if F_perm >= F_obs:
                n_ge += 1
    return float(F_obs), float(n_ge / (n_perm + 1)), int(df_b), int(df_w)


def build_training_pipeline():
    """Re-train the cascade exactly as literature/31, return (scaler, rf, pca, leaves_train_combined_count)."""
    pt = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_train.parquet")
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    sev = pd.read_parquet(PROCESSED / "paper2_operators_severson.parquet")

    if KHAN_COND_CSV.exists():
        kc = pd.read_csv(KHAN_COND_CSV)
        khan = khan.merge(kc, left_on="cell_id", right_on="cell", how="inner")
        khan_labels = np.array([f"kh_{a}" for a in khan["aging_type"].values])
    else:
        khan_labels = np.array(["kh_unknown"] * len(khan))

    pt_labels = np.array([f"pb_{int(c)}" for c in pt["cond_idx"].values])

    # Severson tertiles on first_step_C (matches paper2_gate_II.get_severson_axes)
    first = sev["first_step_C"].astype(float).values
    valid = first[np.isfinite(first)]
    t33, t67 = float(np.percentile(valid, 33.33)), float(np.percentile(valid, 66.67))
    sev_labels = np.array([
        f"sv_{('T1' if v < t33 else ('T2' if v < t67 else 'T3'))}"
        for v in first
    ])

    X_train = np.vstack([pt[SURVIVORS].values, khan[SURVIVORS].values, sev[SURVIVORS].values])
    y_train = np.concatenate([pt_labels, khan_labels, sev_labels])

    imputer = SimpleImputer(strategy="mean")
    X_train_imp = imputer.fit_transform(X_train)
    scaler = StandardScaler()
    X_train_std = scaler.fit_transform(X_train_imp)

    rf = RandomForestClassifier(**RF_PARAMS)

    # OOF acc
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG_SEED)
    oof = cross_val_predict(rf, X_train_std, y_train, cv=cv)
    cv_acc = (oof == y_train).mean()

    rf.fit(X_train_std, y_train)

    # PCA on combined leaves (train + noise-free holdout) to match literature/31
    ph = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_holdout.parquet")
    X_ph = ph[SURVIVORS].values
    X_ph_imp = imputer.transform(X_ph)
    X_ph_std = scaler.transform(X_ph_imp)

    leaves_train = rf.apply(X_train_std).astype(float)
    leaves_ph = rf.apply(X_ph_std).astype(float)
    combined = np.vstack([leaves_train, leaves_ph])
    leaves_scaler = StandardScaler()
    combined_std = leaves_scaler.fit_transform(combined)
    pca = PCA(n_components=min(10, combined.shape[1]), random_state=RNG_SEED)
    pca.fit(combined_std)

    return imputer, scaler, rf, leaves_scaler, pca, X_train_std, cv_acc


def main():
    print("=== Paper 2 Cascade v2 — Noise-Injection Probe (literature/32) ===\n")
    print("Step 1: re-train cascade pipeline (deterministic seed 42)")
    imputer, scaler, rf, leaves_scaler, pca, X_train_std, cv_acc = build_training_pipeline()
    print(f"  cv_acc (sanity check vs literature/31): {cv_acc:.3f} (expected 0.684)")
    print(f"  n_classes: {len(rf.classes_)}, n_train_cells: {len(X_train_std)}\n")

    # Baseline check: noise-free PyBaMM-holdout should reproduce literature/31's F=57.26
    print("Step 2: baseline noise-free PyBaMM-holdout (sanity check vs literature/31)\n")
    ph = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_holdout.parquet")
    X_ph = ph[SURVIVORS].values
    X_ph_imp = imputer.transform(X_ph)
    X_ph_std = scaler.transform(X_ph_imp)
    leaves_ph = rf.apply(X_ph_std).astype(float)
    leaves_ph_std = leaves_scaler.transform(leaves_ph)
    embed_ph_baseline = pca.transform(leaves_ph_std)
    ph_labels = np.array([f"pb_{int(c)}" for c in ph["cond_idx"].values])
    F_base, p_base, dfb_base, dfw_base = permanova_one_way(embed_ph_baseline, ph_labels)
    print(f"  Baseline F = {F_base:.3f}, p = {p_base:.5f} (expected F~57.26, p<0.001)")
    print(f"  Match literature/31: {'YES' if (abs(F_base - 57.26) < 5.0 and p_base < 0.01) else 'NO (investigate)'}\n")

    # Build holdout-cell-trajectory lookup
    print("Step 3: load PyBaMM trajectories, filter to holdout cells")
    traj = pd.read_parquet(PROCESSED / "pybamm_l9_trajectories.parquet")
    holdout_cells = get_holdout_cell_ids()
    traj_holdout = traj[traj.apply(
        lambda row: (int(row["cond_idx"]), int(row["cell_idx"])) in holdout_cells, axis=1
    )].reset_index(drop=True)
    print(f"  Holdout cells: {len(holdout_cells)} expected; {len(traj_holdout)} matched in trajectories")
    assert len(traj_holdout) >= 30, f"Insufficient holdout trajectories: {len(traj_holdout)}"

    # Per-level noise injection + re-extract + score + PERMANOVA
    print("\nStep 4: per-noise-level cascade scoring\n")
    results = []
    for nl in NOISE_LEVELS:
        level = nl["level"]
        print(f"  --- Level {level} ({nl['label']}): "
              f"sigma_Q={nl['sigma_Q']}, sigma_R_DC={nl['sigma_R_DC']}, sigma_R_total={nl['sigma_R_total']}")

        rows = []
        for _, tr in traj_holdout.iterrows():
            rpts = json.loads(tr["rpts_json"]) if isinstance(tr["rpts_json"], str) else tr["rpts_json"]
            if not rpts:
                continue
            seed = 5000 + level * 10000 + int(tr["cond_idx"]) * 100 + int(tr["cell_idx"])
            ops = inject_noise_and_extract(
                rpts, nl["sigma_Q"], nl["sigma_R_DC"], nl["sigma_R_total"], seed
            )
            ops["cond_idx"] = int(tr["cond_idx"])
            ops["cell_idx"] = int(tr["cell_idx"])
            rows.append(ops)

        noisy_df = pd.DataFrame(rows)
        X_noisy = noisy_df[SURVIVORS].values
        X_noisy_imp = imputer.transform(X_noisy)
        X_noisy_std = scaler.transform(X_noisy_imp)
        leaves_noisy = rf.apply(X_noisy_std).astype(float)
        leaves_noisy_std = leaves_scaler.transform(leaves_noisy)
        embed_noisy = pca.transform(leaves_noisy_std)

        labels = np.array([f"pb_{int(c)}" for c in noisy_df["cond_idx"].values])
        F, p, dfb, dfw = permanova_one_way(embed_noisy, labels)
        print(f"      cells extracted: {len(noisy_df)}; finite operator stats: "
              f"{(np.isfinite(X_noisy).sum(axis=0).tolist())}")
        print(f"      F = {F:.3f}, p = {p:.5f}, df_b={dfb}, df_w={dfw}")
        results.append({
            "level": level, "label": nl["label"],
            "sigma_Q": nl["sigma_Q"], "sigma_R_DC": nl["sigma_R_DC"], "sigma_R_total": nl["sigma_R_total"],
            "F": F, "p": p, "df_b": dfb, "df_w": dfw,
            "n_cells": len(noisy_df),
        })

    res_df = pd.DataFrame(results)
    print("\n=== Calibration curve (F vs noise level) ===\n")
    print(res_df[["level", "label", "F", "p"]].to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # H8 verdict (Level 2 is primary)
    level_2 = res_df[res_df["level"] == 2].iloc[0]
    print(f"\n=== H8 Verdict per literature/32 §5 ===\n")
    print(f"Level 2 (primary test point, typical academic noise):")
    print(f"  F = {level_2['F']:.3f}, p = {level_2['p']:.5f}")
    level_2_pass = (level_2["F"] > 3.0) and (level_2["p"] < 0.05)
    if level_2_pass:
        verdict = "CASCADE NOISE-ROBUST"
        print(f"  -> {verdict}: cascade survives typical academic noise (literature/31 §7 Caveat 4 refuted)")
    else:
        level_1 = res_df[res_df["level"] == 1].iloc[0]
        level_1_pass = (level_1["F"] > 3.0) and (level_1["p"] < 0.05)
        if level_1_pass:
            verdict = "CASCADE NOISE-WEAK"
            print(f"  -> {verdict}: cascade survives best-in-class lab noise but collapses at academic noise")
        else:
            verdict = "CASCADE NOISE-FRAGILE"
            print(f"  -> {verdict}: cascade collapses at best-in-class lab noise")

    res_df["verdict"] = verdict
    res_df.to_parquet(PROCESSED / "paper2_cascade_v2_noise_results.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_cascade_v2_noise_results.parquet'}")


if __name__ == "__main__":
    main()
