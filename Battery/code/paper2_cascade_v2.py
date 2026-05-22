"""
Paper 2 — Cascade v2 (RF on amended-Gate-II survivors).

Architecture LOCKED at literature/28 §5 (unchanged by literature/30 amendment):
  Random Forest, n_estimators=500, max_depth=4, min_samples_leaf=5,
  class_weight='balanced', random_state=42.

Training: PyBaMM-train (n=70) + Khan (n=19) + Severson (n=139), features =
the 7 operators that passed amended Gate II (T1-T5, C1, C2). Target =
per-cohort design-condition multinomial label, pooled across cohorts so
each cohort's design conditions are distinct classes.

Output: leaf-indices PCA embedding for the trained cohorts + applied to
PyBaMM-holdout (n=36, PRIMARY validation) and WMG (n=19, SECONDARY
descriptive). PERMANOVA on:
  - PRIMARY: PyBaMM-holdout embedding labeled by L9 cond_idx
  - SECONDARY: vacant under literature/28 §10 amendment (no E1/E2/E3
    survived to Gate II); a descriptive C2-on-WMG univariate report is
    appended as exploratory commentary outside the pre-reg.
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
    n_estimators=500,
    max_depth=4,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=RNG_SEED,
    n_jobs=-1,
)


def build_severson_axes(df):
    """Compute Severson first_step_C tertile labels (consistent with Gate II)."""
    import re
    def parse(p):
        if not isinstance(p, str): return float("nan")
        fname = re.split(r"[\\/]+", p)[-1]
        body = re.sub(r"^\d{8}[-_]?", "", fname, count=1)
        m = re.match(r"(\d+)(?:_(\d+))?C", body, re.IGNORECASE)
        if not m: return float("nan")
        return float(f"{m.group(1)}.{m.group(2)}") if m.group(2) else float(m.group(1))
    # first_step_C already a column, but verify
    if "first_step_C" in df.columns:
        first = df["first_step_C"].astype(float).values
    else:
        first = np.array([parse(p) for p in df["protocol"].values])
    valid = first[np.isfinite(first)]
    if len(valid) < 9:
        return np.array(["X"] * len(df))
    t33 = float(np.percentile(valid, 33.33))
    t67 = float(np.percentile(valid, 66.67))
    labels = np.where(first < t33, "T1", np.where(first < t67, "T2", "T3"))
    return labels


def permanova_one_way(X, labels, n_perm=N_PERMUTATIONS, seed=RNG_SEED):
    """One-way PERMANOVA per Anderson 2001 with permutation p-value.
    X = (n, d) feature matrix; labels = (n,) categorical. Cosine distance
    consistent with the rest of the substrate's PERMANOVA usage."""
    rng = np.random.default_rng(seed)
    # cosine distance via 1 - cosine similarity on standardized features
    # but PCA-projected — use Euclidean on standardized embedding instead
    # (cleaner since the embedding is already low-dim and centered)
    D = squareform(pdist(X, metric="euclidean"))
    n = len(labels)
    grand_mean_d2 = (D ** 2).sum() / (2 * n)
    levels = pd.Series(labels).unique()
    a = len(levels)
    # Between-group sum of squared distances
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
    F_obs = (ss_b_obs / df_b) / (ss_w_obs / df_w)
    # Permutation
    n_ge = 1  # include observed
    for _ in range(n_perm):
        perm = rng.permutation(np.asarray(labels))
        sw = ss_within(perm)
        sb = ss_t - sw
        F_perm = (sb / df_b) / (sw / df_w)
        if F_perm >= F_obs:
            n_ge += 1
    p_val = n_ge / (n_perm + 1)
    return float(F_obs), float(p_val), int(df_b), int(df_w)


def main():
    print("=== Paper 2 Cascade v2 — RF on amended-Gate-II survivors ===\n")

    # Load amended Gate II survivors
    gate_II = pd.read_parquet(PROCESSED / "paper2_gate_II_v2_results.parquet")
    survivors = gate_II[gate_II["passed_gate_II"]]["operator"].tolist()
    print(f"Amended-Gate-II survivors ({len(survivors)}):")
    for op in survivors:
        print(f"  - {op}")
    print()

    # Load cohorts
    pt = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_train.parquet")
    ph = pd.read_parquet(PROCESSED / "paper2_operators_pybamm_holdout.parquet")
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    sev = pd.read_parquet(PROCESSED / "paper2_operators_severson.parquet")
    wmg = pd.read_parquet(PROCESSED / "paper2_operators_wmg.parquet")

    # Build pooled training set with per-cohort design-condition labels
    # PyBaMM: cond_idx (1-9) → "pb_<idx>"
    pt_labels = np.array([f"pb_{int(c)}" for c in pt["cond_idx"].values])
    # Khan: merge aging_type from conditions table → "kh_<aging>"
    if KHAN_COND_CSV.exists():
        kc = pd.read_csv(KHAN_COND_CSV)
        khan_merged = khan.merge(kc, left_on="cell_id", right_on="cell", how="inner")
        khan = khan_merged
        khan_labels = np.array([f"kh_{a}" for a in khan["aging_type"].values])
    else:
        khan_labels = np.array([f"kh_unknown"] * len(khan))
    # Severson: first_step_C tertile
    sev_labels = np.array([f"sv_{t}" for t in build_severson_axes(sev)])

    # Pooled training X + y
    X_pt = pt[survivors].values
    X_kh = khan[survivors].values
    X_sv = sev[survivors].values
    X_train = np.vstack([X_pt, X_kh, X_sv])
    y_train = np.concatenate([pt_labels, khan_labels, sev_labels])
    cohort_train = np.array(["PyBaMM"] * len(pt) + ["Khan"] * len(khan) + ["Severson"] * len(sev))

    print(f"Pooled training matrix: X={X_train.shape}, y={len(y_train)}")
    print(f"Per-cohort breakdown: PyBaMM={len(pt)}, Khan={len(khan)}, Severson={len(sev)}")
    print(f"Unique target classes: {len(np.unique(y_train))}")
    print(f"Class distribution: {dict(pd.Series(y_train).value_counts())}\n")

    # NaN imputation (cohort-wise mean for missing operator values; some
    # operators may be NaN in some cohorts because of data unavailability)
    n_nan_pre = pd.DataFrame(X_train).isna().sum().sum()
    print(f"NaN values pre-imputation: {n_nan_pre} (across {X_train.size} cells)")
    imputer = SimpleImputer(strategy="mean")
    X_train_imp = imputer.fit_transform(X_train)
    print(f"NaN values post-imputation: {pd.DataFrame(X_train_imp).isna().sum().sum()}\n")

    # Standardize
    scaler = StandardScaler()
    X_train_std = scaler.fit_transform(X_train_imp)

    # Train RF + 5-fold CV
    rf = RandomForestClassifier(**RF_PARAMS)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG_SEED)

    # Out-of-fold predictions for honest accuracy
    print("=== 5-fold stratified CV (out-of-fold) ===")
    try:
        oof_pred = cross_val_predict(rf, X_train_std, y_train, cv=cv)
        cv_acc = (oof_pred == y_train).mean()
        print(f"  Out-of-fold accuracy: {cv_acc:.3f}")
    except Exception as e:
        print(f"  CV failed: {e}")
        cv_acc = float("nan")

    # Train final RF on all training data
    rf.fit(X_train_std, y_train)
    print(f"  OOB accuracy not computed (oob_score=False); train accuracy: {rf.score(X_train_std, y_train):.3f}\n")

    # Variable importance
    print("=== RF variable importance ===")
    importances = pd.DataFrame({
        "operator": survivors,
        "importance": rf.feature_importances_,
    }).sort_values("importance", ascending=False)
    for _, r in importances.iterrows():
        print(f"  {r['operator']:<28} {r['importance']:.4f}")
    print()

    # Apply cascade to PyBaMM-holdout (PRIMARY)
    print("=== PRIMARY validation: PyBaMM-holdout PERMANOVA on L9 condition ===\n")
    X_ph = ph[survivors].values
    X_ph_imp = imputer.transform(X_ph)
    X_ph_std = scaler.transform(X_ph_imp)
    ph_labels_l9 = np.array([f"pb_{int(c)}" for c in ph["cond_idx"].values])

    # Project via leaf indices → PCA
    leaves_train = rf.apply(X_train_std)  # (n_train, n_estimators)
    leaves_ph = rf.apply(X_ph_std)
    # PCA on the combined leaf matrix (whitening), then take ph subset
    combined_leaves = np.vstack([leaves_train, leaves_ph]).astype(float)
    # Standardize per-tree (each estimator's leaf indices are categorical;
    # use one-hot encoded reduction via PCA on float leaf indices as a
    # crude embedding — consistent with pre-reg §5 "PCA on leaf-indices matrix")
    leaves_scaler = StandardScaler()
    combined_leaves_std = leaves_scaler.fit_transform(combined_leaves)
    pca = PCA(n_components=min(10, combined_leaves.shape[1]), random_state=RNG_SEED)
    embed_combined = pca.fit_transform(combined_leaves_std)
    embed_train = embed_combined[:len(X_train_std)]
    embed_ph = embed_combined[len(X_train_std):]
    print(f"PCA embedding: n_components={embed_combined.shape[1]}, "
          f"explained_variance_ratio[:5] = {[f'{v:.3f}' for v in pca.explained_variance_ratio_[:5]]}")
    print(f"PyBaMM-holdout embedding: shape={embed_ph.shape}\n")

    F_ph, p_ph, dfb_ph, dfw_ph = permanova_one_way(embed_ph, ph_labels_l9)
    print(f"PRIMARY PERMANOVA (PyBaMM-holdout n={len(embed_ph)}, "
          f"labels=L9 cond_idx, {len(np.unique(ph_labels_l9))} classes):")
    print(f"  pseudo-F = {F_ph:.3f}, df_between = {dfb_ph}, df_within = {dfw_ph}")
    print(f"  permutation p ({N_PERMUTATIONS} perms) = {p_ph:.5f}")
    print(f"  Pre-reg §7 PASS criterion: F > 3.0 AND p < 0.05 "
          f"(no Bonferroni, single primary test per §10 first amendment)\n")

    primary_pass = (F_ph > 3.0) and (p_ph < 0.05)
    print(f"  PRIMARY result: {'PASS' if primary_pass else 'FAIL'}")

    # SECONDARY descriptive on WMG — restricted to EIS-spectral subset (E1-E3)
    print("\n=== SECONDARY descriptive validation: WMG (literature/28 §10 first amendment) ===\n")
    eis_subset = [op for op in survivors if op.startswith(("E1", "E2", "E3"))]
    print(f"EIS-spectral subset of survivors: {eis_subset}")
    if not eis_subset:
        print("  No EIS-spectral operators survived Gate II under the amended protocol.")
        print("  -> WMG SECONDARY is VACANT under literature/28 sec.10 first amendment.")
        wmg_pass = None
        wmg_note = "VACANT_NO_EIS_SURVIVORS"
    else:
        print("  [path would run here]")
        wmg_pass = None
        wmg_note = "unreached"

    # Exploratory commentary: C2 on WMG (outside pre-reg)
    print("\n=== Exploratory (OUTSIDE pre-reg): C2 on WMG ===\n")
    if "C2_R_DC_to_R_total" in wmg.columns:
        c2_wmg = wmg["C2_R_DC_to_R_total"].values
        c2_finite = c2_wmg[np.isfinite(c2_wmg)]
        if len(c2_finite) >= 3:
            print(f"  WMG C2_R_DC_to_R_total: n={len(c2_finite)}, "
                  f"mean={c2_finite.mean():.3f}, sd={c2_finite.std():.3f}, "
                  f"range=[{c2_finite.min():.3f}, {c2_finite.max():.3f}]")
        # SOH bin structure (terminal)
        if "soh_eis" in wmg.columns:
            soh = wmg["soh_eis"].values
            print(f"  WMG soh_eis distribution: mean={np.nanmean(soh):.3f}, "
                  f"range=[{np.nanmin(soh):.3f}, {np.nanmax(soh):.3f}]")

    # Aggregate verdict
    print("\n=== AMENDED-PROTOCOL CASCADE VERDICT (per literature/28 §7) ===\n")
    if primary_pass and (wmg_pass is True):
        verdict = "PAPER 2 STRONG REPLICATION (amended)"
    elif primary_pass and (wmg_pass is None):
        verdict = "PAPER 2 PARTIAL REPLICATION (PRIMARY PASS; SECONDARY vacant)"
    elif primary_pass:
        verdict = "PAPER 2 PARTIAL REPLICATION (PRIMARY PASS only)"
    elif (wmg_pass is True):
        verdict = "PAPER 2 PARTIAL REPLICATION (SECONDARY only)"
    else:
        verdict = "PAPER 2 NULL (amended-protocol cascade)"
    print(f"  {verdict}")

    # Persist
    out = {
        "n_survivors_amended_gate_II": len(survivors),
        "amended_gate_II_survivors": survivors,
        "cv_acc": cv_acc,
        "variable_importance": importances.to_dict("records"),
        "primary_F": F_ph,
        "primary_p": p_ph,
        "primary_pass": primary_pass,
        "secondary_status": wmg_note,
        "verdict": verdict,
    }
    pd.to_pickle(out, PROCESSED / "paper2_cascade_v2_summary.pkl")
    importances.to_parquet(PROCESSED / "paper2_cascade_v2_importances.parquet")
    print(f"\nWritten: {PROCESSED / 'paper2_cascade_v2_summary.pkl'}")
    print(f"         {PROCESSED / 'paper2_cascade_v2_importances.parquet'}")


if __name__ == "__main__":
    main()
