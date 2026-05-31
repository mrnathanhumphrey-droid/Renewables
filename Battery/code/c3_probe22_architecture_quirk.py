"""C3 Probe 22 - Architecture-quirk robustness on the P21 re-selected cascade.

Pre-reg: literature/78_probe22_architecture_quirk_prereg.md (lock 79c1025).
Features locked to P21 re-selection: {E1, C2, W1, W3, W5} (no re-selection here).
Six aggregator variants (A0..A5) defined verbatim in lit/78 sec 0.1.

Inputs (reused unchanged):
  paper2_operators_{khan,secl,zhang,wmg}_v2.parquet
  data/khan_2025/cell_conditions.csv
Output:
  data/processed/probe22_architecture_quirk_results.parquet
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe15_crosssubstrate_gate import (
    load_training, permanova_F, N_SEEDS, REF_SEED, N_PERM, RF_PARAMS, F_FLOOR,
)

PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_COND = Path("D:/Renewables/Battery/data/khan_2025/cell_conditions.csv")
OUT = PROCESSED / "probe22_architecture_quirk_results.parquet"

# P21 re-selected feature set (locked)
FEATURES = ["E1_ohmic_intercept", "C2_R_DC_to_R_total",
            "W1_warburg_slope", "W3_peak_neg_im_norm", "W5_arc_chord_length"]

# P21 anchor (lit/77)
ANCHOR_MEDIAN = 5.703
ANCHOR_TOL = 0.300


# ---------- distance-aware PERMANOVA ----------
def permanova_F_metric(X, labels, metric):
    """PERMANOVA pseudo-F with arbitrary metric."""
    D = squareform(pdist(X, metric=metric))
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


def permanova_p_metric(X, labels, seed, metric, n_perm=N_PERM):
    F_obs = permanova_F_metric(X, labels, metric)
    if not np.isfinite(F_obs): return F_obs, float("nan")
    rng = np.random.default_rng(seed); lab = np.asarray(labels); n_ge = 1
    for _ in range(n_perm):
        if permanova_F_metric(X, rng.permutation(lab), metric) >= F_obs:
            n_ge += 1
    return F_obs, n_ge / (n_perm + 1)


# ---------- shared preproc ----------
def _preproc(Xtr, Xwmg):
    imp = SimpleImputer(strategy="mean"); sc = StandardScaler()
    Xtr_s = sc.fit_transform(imp.fit_transform(Xtr))
    Xwmg_s = sc.transform(imp.transform(Xwmg))
    return Xtr_s, Xwmg_s


def _rf_leaves(Xtr_s, ytr, Xwmg_s, rf_seed):
    rf = RandomForestClassifier(random_state=rf_seed, **RF_PARAMS)
    rf.fit(Xtr_s, ytr)
    lt = rf.apply(Xtr_s).astype(float); lw = rf.apply(Xwmg_s).astype(float)
    return lt, lw, rf


# ---------- six architecture variants ----------
def embed_A0(Xtr, ytr, Xwmg, rf_seed):
    """REF: RF leaf -> standardize -> PCA(min(10,d)) -> Euclidean."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    lt, lw, _ = _rf_leaves(Xtr_s, ytr, Xwmg_s, rf_seed)
    comb = StandardScaler().fit_transform(np.vstack([lt, lw]))
    pca = PCA(n_components=min(10, comb.shape[1]), random_state=rf_seed)
    emb = pca.fit_transform(comb)
    return emb[len(Xtr_s):]


def embed_A1(Xtr, ytr, Xwmg, rf_seed):
    """NO_RF: standardized feats -> PCA(min(10, n_feat)) -> Euclidean."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    comb = StandardScaler().fit_transform(np.vstack([Xtr_s, Xwmg_s]))
    pca = PCA(n_components=min(10, comb.shape[1]), random_state=rf_seed)
    emb = pca.fit_transform(comb)
    return emb[len(Xtr_s):]


def embed_A2(Xtr, ytr, Xwmg, rf_seed):
    """RF_PROBA: RF.predict_proba -> standardize -> PCA(min(10, n_class)) -> Euclidean."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    rf = RandomForestClassifier(random_state=rf_seed, **RF_PARAMS)
    rf.fit(Xtr_s, ytr)
    pt = rf.predict_proba(Xtr_s); pw = rf.predict_proba(Xwmg_s)
    comb = StandardScaler().fit_transform(np.vstack([pt, pw]))
    pca = PCA(n_components=min(10, comb.shape[1]), random_state=rf_seed)
    emb = pca.fit_transform(comb)
    return emb[len(Xtr_s):]


def embed_A3(Xtr, ytr, Xwmg, rf_seed):
    """PCA-2: same as A0 with PCA(2)."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    lt, lw, _ = _rf_leaves(Xtr_s, ytr, Xwmg_s, rf_seed)
    comb = StandardScaler().fit_transform(np.vstack([lt, lw]))
    pca = PCA(n_components=2, random_state=rf_seed)
    emb = pca.fit_transform(comb)
    return emb[len(Xtr_s):]


def embed_A4(Xtr, ytr, Xwmg, rf_seed):
    """NO_PCA: RF leaf -> standardize -> Euclidean (full leaf-dim)."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    lt, lw, _ = _rf_leaves(Xtr_s, ytr, Xwmg_s, rf_seed)
    comb = StandardScaler().fit_transform(np.vstack([lt, lw]))
    return comb[len(Xtr_s):]


def embed_A5(Xtr, ytr, Xwmg, rf_seed):
    """COSINE: A0 emb + unit-vec rows (metric switched to cosine downstream)."""
    Xtr_s, Xwmg_s = _preproc(Xtr, Xwmg)
    lt, lw, _ = _rf_leaves(Xtr_s, ytr, Xwmg_s, rf_seed)
    comb = StandardScaler().fit_transform(np.vstack([lt, lw]))
    pca = PCA(n_components=min(10, comb.shape[1]), random_state=rf_seed)
    emb = pca.fit_transform(comb)
    norms = np.linalg.norm(emb, axis=1, keepdims=True); norms[norms == 0] = 1.0
    return (emb / norms)[len(Xtr_s):]


VARIANTS = {
    "A0_REF":      (embed_A0, "euclidean"),
    "A1_NO_RF":    (embed_A1, "euclidean"),
    "A2_RF_PROBA": (embed_A2, "euclidean"),
    "A3_PCA_2":    (embed_A3, "euclidean"),
    "A4_NO_PCA":   (embed_A4, "euclidean"),
    "A5_COSINE":   (embed_A5, "cosine"),
}


# ---------- data assembly (same as P21) ----------
def safe_cols(df, feats):
    for c in feats:
        if c not in df.columns:
            df[c] = float("nan")
    return df[feats].values.astype(float)


def load_xy():
    khan_v2 = pd.read_parquet(PROCESSED / "paper2_operators_khan_v2.parquet")
    secl_v2 = pd.read_parquet(PROCESSED / "paper2_operators_secl_v2.parquet")
    zhang   = pd.read_parquet(PROCESSED / "paper2_operators_zhang.parquet")
    wmg_v2  = pd.read_parquet(PROCESSED / "paper2_operators_wmg_v2.parquet")

    _, _, _, klab, slab, zlab = load_training()
    kc = pd.read_csv(KHAN_COND)
    khan_m = khan_v2.merge(kc[["cell","aging_type"]], left_on="cell_id", right_on="cell", how="inner")
    khan_m = khan_m[khan_m.aging_type != "excluded"].reset_index(drop=True)
    secl_m = secl_v2.reset_index(drop=True)
    zhang_m = zhang.reset_index(drop=True)

    Xtr = np.vstack([safe_cols(khan_m, FEATURES),
                     safe_cols(secl_m, FEATURES),
                     safe_cols(zhang_m, FEATURES)]).astype(float)
    Xwmg = safe_cols(wmg_v2, FEATURES).astype(float)
    y = np.concatenate([klab, slab, zlab])
    soh_bins = wmg_v2["soh_eis"].values
    return Xtr, y, Xwmg, soh_bins, len(khan_m), len(secl_m), len(zhang_m)


# ---------- variant F at one seed ----------
def variant_F(name, b, Xtr, y, Xwmg, soh_bins):
    embed_fn, metric = VARIANTS[name]
    emb_wmg = embed_fn(Xtr, y, Xwmg, b)
    return permanova_F_metric(emb_wmg, soh_bins, metric)


def variant_F_p(name, b, Xtr, y, Xwmg, soh_bins):
    embed_fn, metric = VARIANTS[name]
    emb_wmg = embed_fn(Xtr, y, Xwmg, b)
    return permanova_p_metric(emb_wmg, soh_bins, REF_SEED, metric)


def single_op_1D(name, Xtr, y, Xwmg, soh_bins):
    """1D F per feature under variant `name` (P22 falsifier F5)."""
    rows = []
    for i, f in enumerate(FEATURES):
        Xtr_i = Xtr[:, [i]]; Xwmg_i = Xwmg[:, [i]]
        F = variant_F(name, REF_SEED, Xtr_i, y, Xwmg_i, soh_bins)
        rows.append({"feature": f, "F_1D_refseed": F})
    return pd.DataFrame(rows)


# ---------- main ----------
def main():
    print("=== Probe 22 architecture-quirk on P21 re-selected cascade ===\n")
    print(f"Features: {FEATURES}")
    Xtr, y, Xwmg, soh_bins, nk, ns, nz = load_xy()
    print(f"Training: Khan={nk}, SECL={ns}, Zhang={nz}, n={len(y)}")
    print(f"WMG test: n={len(Xwmg)}  SOH bins {dict(pd.Series(soh_bins).value_counts().sort_index())}\n")

    rows = []
    for name in VARIANTS:
        Fs = np.array([variant_F(name, b, Xtr, y, Xwmg, soh_bins) for b in range(N_SEEDS)])
        med, lo, hi = float(np.median(Fs)), float(np.percentile(Fs, 2.5)), float(np.percentile(Fs, 97.5))
        F_ref, p_ref = variant_F_p(name, REF_SEED, Xtr, y, Xwmg, soh_bins)
        rows.append({"variant": name, "F_median": med, "F_2.5pct": lo, "F_97.5pct": hi,
                     "F_ref": float(F_ref), "p_ref": float(p_ref)})
        print(f"  {name:14s}  F median={med:6.3f} [{lo:6.3f}, {hi:6.3f}]  refF={F_ref:6.3f} p={p_ref:.4f}")

    df = pd.DataFrame(rows)
    A0 = df[df.variant == "A0_REF"].iloc[0]
    print(f"\n  A0 anchor reproduction: median={A0.F_median:.3f} vs P21 5.703 (tol +/-{ANCHOR_TOL:.3f})")

    # ---- falsifiers + dispositions per lit/78 sec 4/5 ----
    f1_anchor = abs(A0.F_median - ANCHOR_MEDIAN) < ANCHOR_TOL
    alts = df[df.variant != "A0_REF"]
    h22_main_mask = (alts.F_median > A0.F_median * 1.20) & (alts["F_2.5pct"] > 3.0) & (alts.p_ref < 0.05)
    h22_sec_mask  = (alts.F_median.between(A0.F_median * 0.90, A0.F_median * 1.10)) & \
                    (alts["F_2.5pct"] >= A0["F_2.5pct"] * 0.85) & (alts.p_ref < 0.05)
    h22_null = ((alts.F_median < A0.F_median * 0.50) | (alts["F_2.5pct"] < 1.5)).all()

    h22_main = bool(h22_main_mask.any())
    h22_sec  = bool(h22_sec_mask.any())
    winners_main = alts[h22_main_mask].variant.tolist()
    ties_sec     = alts[h22_sec_mask].variant.tolist()

    # F5 single-op check on winning variant if H22-main fires
    single_op_df = None
    f5_pass = True
    if h22_main:
        # pick the strongest H22-main winner by median
        winner = alts[h22_main_mask].sort_values("F_median", ascending=False).iloc[0].variant
        single_op_df = single_op_1D(winner, Xtr, y, Xwmg, soh_bins)
        # F5 pass = cascade F > max(1D F) * 1.20 (lift not from one feature)
        cascade_F_winner = float(alts[alts.variant == winner].F_median.iloc[0])
        max_1d = float(single_op_df.F_1D_refseed.max())
        f5_pass = cascade_F_winner > max_1d * 1.20
        print(f"\n  F5 single-op illusion check on winner {winner}:")
        print(single_op_df.to_string(index=False))
        print(f"  cascade median F={cascade_F_winner:.3f}, max 1D F={max_1d:.3f}, "
              f"F5 {'PASS' if f5_pass else 'FAIL (cascade not > 1.20 x max 1D)'}")

    if not f1_anchor:
        disp = "PROBE 22 INVALID (A0 doesn't reproduce P21 anchor)"
    elif h22_main and f5_pass:
        disp = f"ARCHITECTURE-SUBOPTIMAL (winners: {winners_main})"
    elif h22_main and not f5_pass:
        disp = f"ARCHITECTURE-SUBOPTIMAL-FRAGILE (single-op-dominated; winner: {winners_main})"
    elif h22_null:
        disp = "ARCHITECTURE-LOAD-BEARING (all alts collapse)"
    elif h22_sec:
        disp = f"AGGREGATOR-ROBUST (ties: {ties_sec})"
    else:
        disp = "ARCHITECTURE-PARTIALLY-LOAD-BEARING"

    print("\n" + "=" * 76)
    print("PROBE 22 DISPOSITION (per lit/78 sec 5)")
    print("=" * 76)
    print(f"  F1 anchor reproduces:        {'PASS' if f1_anchor else 'FAIL'} (A0 median={A0.F_median:.3f} vs 5.703)")
    print(f"  H22-main (alt beats A0 x1.20, 2.5pct>3.0, p<.05): {'PASS' if h22_main else 'FAIL'} (winners: {winners_main})")
    print(f"  H22-secondary (alt within +/-10%, overlap CI):    {'PASS' if h22_sec else 'FAIL'} (ties: {ties_sec})")
    print(f"  H22-null (all alts collapse):                     {'PASS' if h22_null else 'FAIL'}")
    if h22_main:
        print(f"  F5 single-op check on winner: {'PASS' if f5_pass else 'FAIL'}")
    print(f"\n  ==> {disp}")

    # persist
    blocks = [df.assign(block="variant_F")]
    if single_op_df is not None:
        blocks.append(single_op_df.assign(block="single_op_1D"))
    blocks.append(pd.DataFrame([{"block": "disposition", "disposition": disp,
                                  "winners_main": ",".join(winners_main) or "none",
                                  "ties_sec": ",".join(ties_sec) or "none",
                                  "A0_median": A0.F_median, "A0_2.5pct": A0["F_2.5pct"],
                                  "f1_anchor": f1_anchor, "h22_main": h22_main,
                                  "h22_sec": h22_sec, "h22_null": h22_null,
                                  "f5_pass": f5_pass if h22_main else None}]))
    pd.concat(blocks, ignore_index=True).to_parquet(OUT)
    print(f"\nWritten: {OUT}")


if __name__ == "__main__":
    main()
