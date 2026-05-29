"""C3 Probe 15 - Cross-substrate-as-primary-gate redesign (Paper-3-equivalent).

Pre-reg: literature/66_probe15_crosssubstrate_primary_gate_prereg.md (lock 4128561).
Inputs (reused unchanged):
  paper2_operators_{khan,secl,zhang,wmg}.parquet + data/khan_2025/cell_conditions.csv
Output:
  data/processed/probe15_crosssubstrate_gate_results.parquet

Operationalizes lit/35 §6. The cross-substrate gate (extractable on held-out snapshot
cohort WMG) admits exactly {E1_ohmic_intercept, E2_charge_transfer_radius, C2}. Mirrors
the lit/35 RF-cascade -> leaf-PCA -> WMG-SOH-PERMANOVA protocol, generalized to a feature
list, trained on the real-EIS cohorts {Khan,SECL,Zhang} (n=37). Runs BOTH {C2} (matched
baseline, F2) and {E1,E2,C2} (gated set). 200-seed RF multi-seed stability gate (9b lesson;
lit/35's F=0.92 was one seed). Headline p at reference seed 42, 10,000 perms.
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
import warnings
warnings.filterwarnings("ignore")

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
OUT = PROCESSED / "probe15_crosssubstrate_gate_results.parquet"

RF_PARAMS = dict(n_estimators=500, max_depth=4, min_samples_leaf=5,
                 class_weight="balanced", n_jobs=-1)
N_SEEDS = 200
REF_SEED = 42
N_PERM = 10000
F_FLOOR = 3.0

FEATURE_SETS = {
    "C2_only": ["C2_R_DC_to_R_total"],
    "E1E2C2": ["E1_ohmic_intercept", "E2_charge_transfer_radius", "C2_R_DC_to_R_total"],
}


def permanova_F(X, labels):
    D = squareform(pdist(X, metric="euclidean"))
    n = len(labels); levels = pd.Series(labels).unique(); a = len(levels)
    def ss_within(lab):
        ss = 0.0
        for lvl in levels:
            idx = np.where(lab == lvl)[0]
            if len(idx) < 2: continue
            ss += (D[np.ix_(idx, idx)] ** 2).sum() / (2 * len(idx))
        return ss
    lab = np.asarray(labels)
    ss_w = ss_within(lab); ss_t = (D ** 2).sum() / (2 * n); ss_b = ss_t - ss_w
    df_b, df_w = a - 1, n - a
    if ss_w <= 0 or df_b == 0: return float("nan")
    return (ss_b / df_b) / (ss_w / df_w)


def permanova_p(X, labels, seed, n_perm=N_PERM):
    F_obs = permanova_F(X, labels)
    if not np.isfinite(F_obs): return F_obs, float("nan")
    rng = np.random.default_rng(seed); lab = np.asarray(labels); n_ge = 1
    for _ in range(n_perm):
        if permanova_F(X, rng.permutation(lab)) >= F_obs:
            n_ge += 1
    return F_obs, n_ge / (n_perm + 1)


def load_training():
    khan = pd.read_parquet(PROCESSED / "paper2_operators_khan.parquet")
    secl = pd.read_parquet(PROCESSED / "paper2_operators_secl.parquet")
    zhang = pd.read_parquet(PROCESSED / "paper2_operators_zhang.parquet")
    kc = pd.read_csv(KHAN_COND)
    khan = khan.merge(kc[["cell", "aging_type"]], left_on="cell_id", right_on="cell", how="inner")
    khan = khan[khan["aging_type"] != "excluded"].reset_index(drop=True)  # drop n=2, breaks stratify
    khan_lab = np.array([f"kh_{a}" for a in khan["aging_type"]])
    secl_lab = np.array(["secl"] * len(secl))
    zhang_lab = np.array(["zhang"] * len(zhang))
    return khan, secl, zhang, khan_lab, secl_lab, zhang_lab


def cascade_F(features, rf_seed, Xtr, ytr, Xwmg, soh_bins, with_p=False):
    imp = SimpleImputer(strategy="mean"); sc = StandardScaler()
    Xtr_s = sc.fit_transform(imp.fit_transform(Xtr))
    Xwmg_s = sc.transform(imp.transform(Xwmg))
    rf = RandomForestClassifier(random_state=rf_seed, **RF_PARAMS)
    rf.fit(Xtr_s, ytr)
    lt = rf.apply(Xtr_s).astype(float); lw = rf.apply(Xwmg_s).astype(float)
    comb = StandardScaler().fit_transform(np.vstack([lt, lw]))
    pca = PCA(n_components=min(10, comb.shape[1]), random_state=rf_seed)
    emb = pca.fit_transform(comb)
    emb_wmg = emb[len(Xtr_s):]
    if with_p:
        return permanova_p(emb_wmg, soh_bins, REF_SEED), rf, Xtr_s, ytr
    return permanova_F(emb_wmg, soh_bins)


def main():
    khan, secl, zhang, klab, slab, zlab = load_training()
    wmg = pd.read_parquet(PROCESSED / "paper2_operators_wmg.parquet")
    soh_bins = wmg["soh_eis"].values
    y = np.concatenate([klab, slab, zlab])
    print(f"Training cohorts: Khan={len(khan)} SECL={len(secl)} Zhang={len(zhang)}  n={len(y)}")
    print(f"  label classes: {dict(pd.Series(y).value_counts())}")
    print(f"WMG test: n={len(wmg)}  SOH bins {dict(pd.Series(soh_bins).value_counts().sort_index())}")
    print(f"  Reference baseline (lit/35): C2-only(PyBaMM+Khan+Severson) F=0.921 p=0.576 NULL\n")

    rows = []
    summary = {}
    for fname, feats in FEATURE_SETS.items():
        Xtr = np.vstack([khan[feats].values, secl[feats].values, zhang[feats].values]).astype(float)
        Xwmg = wmg[feats].values.astype(float)

        # CV sanity (F1) at ref seed; small classes -> 3-fold
        min_class = pd.Series(y).value_counts().min()
        nsplit = int(max(2, min(3, min_class)))
        imp = SimpleImputer(strategy="mean"); sc = StandardScaler()
        Xtr_s = sc.fit_transform(imp.fit_transform(Xtr))
        rf = RandomForestClassifier(random_state=REF_SEED, **RF_PARAMS)
        cv = StratifiedKFold(n_splits=nsplit, shuffle=True, random_state=REF_SEED)
        oof = cross_val_predict(rf, Xtr_s, y, cv=cv)
        cv_acc = float((oof == y).mean()); chance = 1.0 / pd.Series(y).nunique()

        # multi-seed F distribution
        Fs = np.array([cascade_F(feats, b, Xtr, y, Xwmg, soh_bins) for b in range(N_SEEDS)])
        med, lo, hi = np.nanmedian(Fs), np.nanpercentile(Fs, 2.5), np.nanpercentile(Fs, 97.5)
        frac_pass = float(np.mean(Fs > F_FLOOR))
        # reference-seed p
        (F_ref, p_ref), _, _, _ = cascade_F(feats, REF_SEED, Xtr, y, Xwmg, soh_bins, with_p=True)

        robust_pass = (med > F_FLOOR) and (lo > F_FLOOR) and (p_ref < 0.05)
        summary[fname] = dict(cv_acc=cv_acc, chance=chance, F_median=med, F_lo=lo, F_hi=hi,
                              frac_pass=frac_pass, F_ref=F_ref, p_ref=p_ref, robust_pass=robust_pass)
        rows.append({"feature_set": fname, "n_feat": len(feats), "cv_acc": cv_acc, "chance": chance,
                     "F_median": med, "F_2.5pct": lo, "F_97.5pct": hi, "frac_F_gt3": frac_pass,
                     "F_refseed": F_ref, "p_refseed": p_ref, "robust_pass": robust_pass})
        print(f"=== {fname} ({len(feats)} feat) ===")
        print(f"  CV OOF acc = {cv_acc:.3f} (chance {chance:.3f}, {nsplit}-fold)")
        print(f"  WMG PERMANOVA F: 200-seed median={med:.3f} [2.5pct={lo:.3f}, 97.5pct={hi:.3f}]  frac F>3 = {frac_pass:.2f}")
        print(f"  ref-seed(42): F={F_ref:.3f} p={p_ref:.4f}")
        print(f"  robust PASS (median>3 AND 2.5pct>3 AND p<0.05): {robust_pass}\n")

    pd.DataFrame(rows).to_parquet(OUT)

    # disposition
    c2 = summary["C2_only"]; gated = summary["E1E2C2"]
    f1_ok = (c2["cv_acc"] > c2["chance"]) and (gated["cv_acc"] > gated["chance"])
    f2_c2_null = not c2["robust_pass"]
    if not f1_ok:
        disp = "PROBE 15 INVALID (cascade does not learn above chance)"
    elif not f2_c2_null:
        disp = "MATCHED-BASELINE-NOT-NULL (C2-only on {Khan,SECL,Zhang} unexpectedly PASSES)"
    elif gated["robust_pass"]:
        disp = "CROSS-SUBSTRATE-GATE-RECOVERS"
    else:
        disp = "CROSS-SUBSTRATE-STILL-NULL"

    print("=" * 74)
    print("PROBE 15 DISPOSITION (per lit/66 §5)")
    print("=" * 74)
    print(f"  F1 cascade-learns:                {'PASS' if f1_ok else 'FAIL'} (C2 acc {c2['cv_acc']:.2f}, gated acc {gated['cv_acc']:.2f} vs chance ~{c2['chance']:.2f})")
    print(f"  F2 matched {{C2}}-only NULL:         {'YES (apples-to-apples)' if f2_c2_null else 'NO'} (median F={c2['F_median']:.2f}, p={c2['p_ref']:.3f})")
    print(f"  H15-main {{E1,E2,C2}} robust transfer: {'PASS' if gated['robust_pass'] else 'FAIL'} (median F={gated['F_median']:.2f} [{gated['F_lo']:.2f},{gated['F_hi']:.2f}], p={gated['p_ref']:.3f})")
    print(f"\n  ==> {disp}")
    print(f"\nWritten: {OUT}")
    print("=" * 74)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 74)


if __name__ == "__main__":
    main()
