"""C3 Probe 11 — Second-life SOH triage analyzer.

Pre-reg: literature/58_probe11_secondlife_soh_triage_prereg.md (lock ed2df82).
Input:   data/processed/secl_eis_soh_observations.parquet
Output:  data/processed/probe11_soh_triage_results.parquet

- F1 positive control: does R track SOH (Spearman rho<0)?
- PRIMARY: LOCO PLS regression (n_comp=2) EIS->SOH, vs predict-mean baseline.
- SECONDARY: C3 PERMANOVA on SOH tertiles, PCA-k {2,3}, naive + cell-stratified null.
- F2: LOCO R2 sign stable to dropping any single SOC.
- F3: cell-stratified null differs from naive (non-independence handled).
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cross_decomposition import PLSRegression
import warnings
warnings.filterwarnings("ignore")

from c3_probe9_extended_permanova import build_pca, cosine_dist, permanova_pseudoF

IN = Path("D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe11_soh_triage_results.parquet")

SOC_VOLTS = [326, 363, 400]
FEATCOLS = [f"{op}_{v}" for v in SOC_VOLTS for op in ["R_ohmic", "R_diff"]]
N_PERMS = 10000


def zscore_fit(X):
    mu = X.mean(axis=0); sd = X.std(axis=0, ddof=1)
    sd = np.where(sd < 1e-12, 1e-12, sd)
    return mu, sd


def f1_positive_control(df):
    print("\n=== F1 positive control: does R track SOH? (Spearman, expect rho<0) ===")
    rows = []
    any_ok = False
    for c in FEATCOLS:
        rho, p = spearmanr(df[c], df["SOH"])
        ok = (rho < 0) and (p < 0.05)
        any_ok = any_ok or ok
        rows.append({"feature": c, "rho": rho, "p": p, "tracks": ok})
        print(f"  {c:16s}: rho={rho:+.3f} p={p:.4f} {'<-- tracks SOH' if ok else ''}")
    print(f"  F1 {'PASS' if any_ok else 'FAIL'} (>=1 R feature with rho<0, p<0.05)")
    return any_ok, pd.DataFrame(rows)


def loco_regression(df, featcols=FEATCOLS):
    """Leave-one-cell-out PLS regression EIS->SOH. Returns per-cell + pooled."""
    cells = sorted(df["cell"].unique())
    all_actual, all_pred = [], []
    percell = []
    for held in cells:
        tr = df[df["cell"] != held]
        te = df[df["cell"] == held]
        Xtr = tr[featcols].values.astype(float)
        Xte = te[featcols].values.astype(float)
        mu, sd = zscore_fit(Xtr)
        Ztr = (Xtr - mu) / sd
        Zte = (Xte - mu) / sd
        pls = PLSRegression(n_components=2)
        pls.fit(Ztr, tr["SOH"].values)
        pred = pls.predict(Zte).ravel()
        base = tr["SOH"].mean()
        mae_model = float(np.mean(np.abs(pred - te["SOH"].values)))
        mae_base = float(np.mean(np.abs(base - te["SOH"].values)))
        percell.append({"cell": held, "n": len(te), "mae_model": mae_model,
                        "mae_base": mae_base, "improved": mae_model < mae_base,
                        "soh_mean": float(te["SOH"].mean())})
        all_actual.extend(te["SOH"].values.tolist())
        all_pred.extend(pred.tolist())
    a = np.array(all_actual); p = np.array(all_pred)
    ss_res = float(np.sum((a - p) ** 2))
    ss_tot = float(np.sum((a - a.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    mae_pooled = float(np.mean(np.abs(a - p)))
    return pd.DataFrame(percell), r2, mae_pooled


def cell_labels(df, bins):
    """Tertile SOH-bin per observation."""
    return np.digitize(df["SOH"].values, bins)


def permanova_naive(pca, labels, rng, n=N_PERMS):
    d = cosine_dist(pca)
    F = permanova_pseudoF(d, labels)
    if not np.isfinite(F):
        return F, float("nan")
    ge = 0
    for _ in range(n):
        if permanova_pseudoF(d, rng.permutation(labels)) >= F:
            ge += 1
    return F, (ge + 1) / (n + 1)


def permanova_cellstrat(pca, labels, cells, rng, n=N_PERMS):
    """Cell-stratified null: permute labels by shuffling whole-cell label-blocks."""
    d = cosine_dist(pca)
    F = permanova_pseudoF(d, labels)
    if not np.isfinite(F):
        return F, float("nan")
    uniq = np.array(sorted(set(cells)))
    # each cell's observations keep their relative labels; we shuffle the cell->labelblock map
    cell_to_idx = {c: np.where(cells == c)[0] for c in uniq}
    cell_label_blocks = {c: labels[cell_to_idx[c]] for c in uniq}
    ge = 0
    for _ in range(n):
        perm_cells = rng.permutation(uniq)
        permlab = np.empty_like(labels)
        for src, dst in zip(uniq, perm_cells):
            # assign src cell's positions the label-block of dst cell (sized to src)
            src_idx = cell_to_idx[src]
            dst_block = cell_label_blocks[dst]
            if len(dst_block) >= len(src_idx):
                permlab[src_idx] = dst_block[:len(src_idx)]
            else:
                reps = int(np.ceil(len(src_idx) / len(dst_block)))
                permlab[src_idx] = np.tile(dst_block, reps)[:len(src_idx)]
        if permanova_pseudoF(d, permlab) >= F:
            ge += 1
    return F, (ge + 1) / (n + 1)


def main():
    df = pd.read_parquet(IN).reset_index(drop=True)
    print(f"Observations: {len(df)}  cells: {sorted(df['cell'].unique())}")
    print(f"Pooled SOH: {df['SOH'].min()*100:.1f}% - {df['SOH'].max()*100:.1f}%")

    f1_ok, f1_df = f1_positive_control(df)

    # PRIMARY: LOCO regression
    print("\n=== PRIMARY: LOCO PLS regression EIS -> SOH ===")
    percell, r2, mae_pooled = loco_regression(df)
    print(percell.to_string(index=False))
    n_imp = int(percell["improved"].sum())
    n_cells = len(percell)
    print(f"\n  Pooled LOCO R2 = {r2:.3f}  MAE = {mae_pooled*100:.3f}% SOH")
    print(f"  Cells improved over baseline: {n_imp}/{n_cells}")
    loco_pass = (n_imp > n_cells / 2) and (r2 > 0)
    print(f"  H11-main {'PASS' if loco_pass else 'FAIL'} (majority improved AND pooled R2>0)")

    # F2: drop-one-SOC stability of LOCO R2 sign
    print("\n=== F2: LOCO R2 sign stability to dropping one SOC ===")
    f2_signs = []
    for vdrop in SOC_VOLTS:
        fc = [c for c in FEATCOLS if not c.endswith(str(vdrop))]
        _, r2d, _ = loco_regression(df, featcols=fc)
        f2_signs.append(np.sign(r2d) == np.sign(r2))
        print(f"  drop SOC {vdrop}: LOCO R2={r2d:.3f} (sign {'stable' if f2_signs[-1] else 'FLIPPED'})")
    f2_ok = all(f2_signs)

    # SECONDARY: PERMANOVA on tertiles
    print("\n=== SECONDARY: C3 PERMANOVA on SOH tertiles (naive vs cell-stratified null) ===")
    t1, t2 = df["SOH"].quantile([1/3, 2/3]).values
    bins = np.array([t1, t2])
    labels = cell_labels(df, bins)
    cells = df["cell"].values
    feats = df[FEATCOLS].values.astype(float)
    perm_rows = []
    for k in [2, 3]:
        pca, _ = build_pca(feats, k)
        F_n, p_n = permanova_naive(pca, labels, np.random.default_rng(11000 + k))
        F_c, p_c = permanova_cellstrat(pca, labels, cells, np.random.default_rng(12000 + k))
        perm_rows.append({"pca_k": k, "F": F_n, "p_naive": p_n, "p_cellstrat": p_c})
        print(f"  k={k}: F={F_n:.3f}  p_naive={p_n:.4f}  p_cellstrat={p_c:.4f}")
    perm_df = pd.DataFrame(perm_rows)

    # F3: cell-stratified null must be MORE conservative than naive (non-indep handled).
    # Correct test = cell-stratified p meaningfully LARGER (>=3x) or abs diff > 0.01.
    ratio = (perm_df["p_cellstrat"] / perm_df["p_naive"].replace(0, 1e-9))
    f3_ok = bool(np.any((ratio >= 3.0) | (np.abs(perm_df["p_naive"] - perm_df["p_cellstrat"]) > 0.01)))
    print(f"\n=== F3: cell-stratified null more conservative than naive? "
          f"{'YES' if f3_ok else 'NO (debug)'}  (max ratio {ratio.max():.1f}x) ===")

    # Disposition
    print("\n" + "=" * 72)
    print("PROBE 11 DISPOSITION (per lit/58 sec 5)")
    print("=" * 72)
    sig_cellstrat = bool((perm_df["p_cellstrat"] < 0.0167).any())
    if not f1_ok:
        disp = "PROBE 11 INVALID (R does not track SOH)"
    elif loco_pass:
        disp = "SOH-READABLE (transferable)"
    elif sig_cellstrat:
        disp = "SOH-READABLE (within-cell only)"
    else:
        disp = "SOH NULL (cohort-limited)"
    print(f"  F1 positive control: {'PASS' if f1_ok else 'FAIL'}")
    print(f"  H11-main LOCO transfer: {'PASS' if loco_pass else 'FAIL'} (R2={r2:.3f}, {n_imp}/{n_cells} cells)")
    print(f"  Secondary PERMANOVA (cell-stratified): {'sig' if sig_cellstrat else 'NULL'}")
    print(f"  F2 SOC-drop stability: {'OK' if f2_ok else 'FAIL'}   F3 null-differ: {'OK' if f3_ok else 'FAIL'}")
    print(f"\n  ==> {disp}")

    # persist
    out = {"r2": r2, "mae_pooled": mae_pooled, "n_improved": n_imp, "n_cells": n_cells,
           "f1_ok": f1_ok, "f2_ok": f2_ok, "f3_ok": f3_ok, "disposition": disp}
    pd.DataFrame([out]).to_parquet(OUT)
    perm_df.to_parquet(OUT.with_name("probe11_permanova.parquet"))
    percell.to_parquet(OUT.with_name("probe11_loco_percell.parquet"))
    print(f"\nWritten: {OUT}")
    print("\n" + "=" * 72)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 72)


if __name__ == "__main__":
    main()
