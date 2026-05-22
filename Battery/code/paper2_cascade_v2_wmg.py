"""
Paper 2 — C2-restricted cascade applied to WMG SECONDARY (literature/33, locked 7633f7e).

Procedure per literature/33 §3-4:
1. Train RF cascade using ONLY C2 as the feature, on the same training data as
   the main amended cascade (PyBaMM-train + Khan + Severson, n=228).
2. Same architecture: n_estimators=500, max_depth=4, min_samples_leaf=5,
   class_weight='balanced', random_state=42. Same 14-class multinomial target.
3. Apply trained C2-restricted RF to WMG (n=19). Project via leaf-indices PCA
   fit on training + WMG leaves combined.
4. PERMANOVA on WMG embedding labeled by terminal SOH bins {80, 85, 90, 95},
   10,000 permutations. Fall back to 2-bin median split if any bin n<3.
5. Apply §5 verdict.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from scipy.spatial.distance import pdist, squareform

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND_CSV = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
RNG_SEED = 42
N_PERMUTATIONS = 10000

RF_PARAMS = dict(
    n_estimators=500, max_depth=4, min_samples_leaf=5,
    class_weight="balanced", random_state=RNG_SEED, n_jobs=-1,
)

FEATURE = "C2_R_DC_to_R_total"


def permanova_one_way(X, labels, n_perm=N_PERMUTATIONS, seed=RNG_SEED):
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


def main():
    print("=== Paper 2 — C2-restricted cascade for WMG SECONDARY (literature/33) ===\n")

    # Step 1: build training data with C2 only
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

    first = sev["first_step_C"].astype(float).values
    valid = first[np.isfinite(first)]
    t33, t67 = float(np.percentile(valid, 33.33)), float(np.percentile(valid, 66.67))
    sev_labels = np.array([
        f"sv_{('T1' if v < t33 else ('T2' if v < t67 else 'T3'))}"
        for v in first
    ])

    # C2 only, reshape to (n, 1)
    X_pt = pt[[FEATURE]].values
    X_kh = khan[[FEATURE]].values
    X_sv = sev[[FEATURE]].values
    X_train = np.vstack([X_pt, X_kh, X_sv])
    y_train = np.concatenate([pt_labels, khan_labels, sev_labels])

    print(f"Training data: n={len(X_train)} cells x 1 feature (C2 only)")
    n_nan = np.isnan(X_train).sum()
    print(f"NaN C2 values pre-imputation: {n_nan} of {len(X_train)} cells")

    imputer = SimpleImputer(strategy="mean")
    X_train_imp = imputer.fit_transform(X_train)
    scaler = StandardScaler()
    X_train_std = scaler.fit_transform(X_train_imp)

    print(f"Per-cohort breakdown: PyBaMM={len(pt)}, Khan={len(khan)}, Severson={len(sev)}")
    print(f"Class distribution: {dict(pd.Series(y_train).value_counts())}\n")

    # Step 2: train RF + 5-fold CV
    rf = RandomForestClassifier(**RF_PARAMS)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG_SEED)
    oof = cross_val_predict(rf, X_train_std, y_train, cv=cv)
    cv_acc = (oof == y_train).mean()
    print(f"=== 5-fold CV (C2-only restricted cascade) ===")
    print(f"  Out-of-fold accuracy: {cv_acc:.3f} (vs 7-operator cascade 0.684; vs chance 0.071)")

    rf.fit(X_train_std, y_train)
    print(f"  Train accuracy: {rf.score(X_train_std, y_train):.3f}\n")

    # Step 3: apply to WMG, project via PCA on combined leaves
    wmg = pd.read_parquet(PROCESSED / "paper2_operators_wmg.parquet")
    print(f"=== WMG cohort ===")
    print(f"  n cells: {len(wmg)}")
    print(f"  C2 finite count: {np.isfinite(wmg[FEATURE].values).sum()}/{len(wmg)}")
    X_wmg = wmg[[FEATURE]].values
    X_wmg_imp = imputer.transform(X_wmg)
    X_wmg_std = scaler.transform(X_wmg_imp)

    leaves_train = rf.apply(X_train_std).astype(float)
    leaves_wmg = rf.apply(X_wmg_std).astype(float)
    combined = np.vstack([leaves_train, leaves_wmg])
    leaves_scaler = StandardScaler()
    combined_std = leaves_scaler.fit_transform(combined)
    pca = PCA(n_components=min(10, combined.shape[1]), random_state=RNG_SEED)
    embed_combined = pca.fit_transform(combined_std)
    embed_wmg = embed_combined[len(X_train_std):]
    print(f"\n  PCA components: {pca.n_components_}")
    print(f"  Explained variance ratio[:5]: {[f'{v:.3f}' for v in pca.explained_variance_ratio_[:5]]}")
    print(f"  WMG embedding shape: {embed_wmg.shape}\n")

    # Step 4: WMG SOH binning
    print(f"=== WMG SOH bins ===")
    soh = wmg["soh_eis"].values
    # Round each cell to nearest of {80, 85, 90, 95}
    bin_centers = np.array([80, 85, 90, 95])
    soh_bins = np.array([bin_centers[np.argmin(np.abs(bin_centers - s))] for s in soh])
    bin_counts = pd.Series(soh_bins).value_counts().sort_index()
    print(f"  Per-bin counts: {dict(bin_counts)}")

    if bin_counts.min() < 3:
        print(f"  -> some bin <3 cells, falling back to median split")
        med = float(np.median(soh))
        soh_bins = np.where(soh < med, "low", "high")
        bin_counts = pd.Series(soh_bins).value_counts()
        print(f"  Median split (med={med:.1f}): {dict(bin_counts)}")

    if pd.Series(soh_bins).value_counts().min() < 3:
        print(f"  -> still insufficient; SECONDARY INVALID")
        verdict = "CASCADE CROSS-SUBSTRATE INVALID"
        F_wmg, p_wmg, dfb, dfw = float("nan"), float("nan"), 0, 0
    else:
        F_wmg, p_wmg, dfb, dfw = permanova_one_way(embed_wmg, soh_bins)
        print(f"\n=== WMG SECONDARY PERMANOVA ===")
        print(f"  pseudo-F = {F_wmg:.3f}, df_b = {dfb}, df_w = {dfw}")
        print(f"  permutation p ({N_PERMUTATIONS} perms) = {p_wmg:.5f}")
        wmg_pass = (F_wmg > 3.0) and (p_wmg < 0.05)
        if wmg_pass:
            verdict = "CASCADE CROSS-SUBSTRATE PASS"
        else:
            verdict = "CASCADE CROSS-SUBSTRATE NULL"

    print(f"\n=== Verdict per literature/33 §5 ===\n  {verdict}")

    # Save
    out = {
        "cv_acc": cv_acc,
        "n_train": len(X_train),
        "n_wmg": len(wmg),
        "bin_counts": dict(pd.Series(soh_bins).value_counts()),
        "F": F_wmg,
        "p": p_wmg,
        "df_b": dfb,
        "df_w": dfw,
        "verdict": verdict,
    }
    pd.to_pickle(out, PROCESSED / "paper2_cascade_v2_wmg_results.pkl")
    print(f"\nWritten: {PROCESSED / 'paper2_cascade_v2_wmg_results.pkl'}")


if __name__ == "__main__":
    main()
