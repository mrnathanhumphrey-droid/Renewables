"""C3 Probe 8d — test-statistic decomposition.

Pre-reg: literature/48_probe8d_prereg.md.

Tests three test statistics on the amended C3 architecture's PCA-2 features
(variant iv 6D fresh+aged stacked -> centered z-score -> PCA k=2):

  1. PERMANOVA (baseline, reproduces 8c PCA-2 unit cosine)
  2. Random Forest classifier (3-fold CV accuracy + permutation p-value)
  3. Multinomial logistic regression (3-fold CV accuracy + permutation p-value)

Question: does the test statistic carry additional load-bearing capacity?
Most importantly: does RF or logistic catch transference where PERMANOVA misses?

Cost: PERMANOVA 10000 perms (fast) + RF/logistic 1000 perms x 3-fold CV
(moderate). Estimated ~10-15 min wall.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
import warnings
warnings.filterwarnings("ignore")


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v2.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")

N_PERMS_PERMANOVA = 10000
N_PERMS_CLASSIFIER = 1000

ALPHA_BONFERRONI = 0.0167
ALPHA_WEAK = 0.05

PERMANOVA_F_FLOOR = 3.0
PERMANOVA_F_WEAK = 2.0

# Classifier accuracy thresholds (3-level params, chance = 1/3 = 0.333)
ACC_STRONG = 0.67   # >= 2x chance
ACC_PASS = 0.53     # chance + 0.20
ACC_WEAK = 0.45     # chance + 0.12

N1_LEVELS = [
    {"level": 0, "sigma_Q": 0.000, "sigma_Ro": 0.00, "sigma_Rd": 0.00, "name": "N1-L0 baseline"},
    {"level": 1, "sigma_Q": 0.001, "sigma_Ro": 0.05, "sigma_Rd": 0.10, "name": "N1-L1 best lab"},
    {"level": 2, "sigma_Q": 0.005, "sigma_Ro": 0.15, "sigma_Rd": 0.20, "name": "N1-L2 PRIMARY"},
    {"level": 3, "sigma_Q": 0.010, "sigma_Ro": 0.30, "sigma_Rd": 0.30, "name": "N1-L3 noisy field"},
    {"level": 4, "sigma_Q": 0.020, "sigma_Ro": 0.50, "sigma_Rd": 0.50, "name": "N1-L4 instrument issue"},
]

RNG_SEED_BASE = 2000


def build_clean_table(df_raw):
    rows = []
    for _, row in df_raw.iterrows():
        if row.get("error") is not None:
            continue
        if pd.isna(row.get("R_ohmic_aged_b5")) or pd.isna(row.get("R_diff_aged_b5")):
            continue
        if row.get("anchor_partial") is True:
            continue
        rows.append({
            "cond_idx": int(row["cond_idx"]),
            "cell_idx": int(row["cell_idx"]),
            "thickness_level": row["thickness_level"],
            "transference_level": row["transference_level"],
            "particle_radius_level": row["particle_radius_level"],
            "fresh_Q": float(row["fresh_Q"]),
            "fresh_R_ohmic": float(row["R_ohmic_fresh"]),
            "fresh_R_diff": float(row["R_diff_fresh"]),
            "aged_Q": float(row["anchor_aged_Q"]),
            "aged_R_ohmic": float(row["R_ohmic_aged_b5"]),
            "aged_R_diff": float(row["R_diff_aged_b5"]),
        })
    return pd.DataFrame(rows)


def apply_noise(df_clean, sigma_Q, sigma_Ro, sigma_Rd, level):
    df = df_clean.copy().reset_index(drop=True)
    n = len(df)
    eps = {k: np.empty(n) for k in ["fq", "fo", "fd", "aq", "ao", "ad"]}
    for i, row in df.iterrows():
        s = RNG_SEED_BASE + level * 10000 + int(row["cond_idx"]) * 100 + int(row["cell_idx"])
        rng = np.random.default_rng(s)
        eps["fq"][i] = rng.normal(0, sigma_Q)
        eps["fo"][i] = rng.normal(0, sigma_Ro)
        eps["fd"][i] = rng.normal(0, sigma_Rd)
        eps["aq"][i] = rng.normal(0, sigma_Q)
        eps["ao"][i] = rng.normal(0, sigma_Ro)
        eps["ad"][i] = rng.normal(0, sigma_Rd)
    df["fQ_n"] = df["fresh_Q"] * (1 + eps["fq"])
    df["fRo_n"] = df["fresh_R_ohmic"] * (1 + eps["fo"])
    df["fRd_n"] = df["fresh_R_diff"] * (1 + eps["fd"])
    df["aQ_n"] = df["aged_Q"] * (1 + eps["aq"])
    df["aRo_n"] = df["aged_R_ohmic"] * (1 + eps["ao"])
    df["aRd_n"] = df["aged_R_diff"] * (1 + eps["ad"])
    return df


def build_pca2(df_noisy):
    """Variant iv -> z-score -> PCA k=2."""
    feats = df_noisy[["fQ_n", "fRo_n", "fRd_n", "aQ_n", "aRo_n", "aRd_n"]].values
    feats = feats - feats.mean(axis=0, keepdims=True)
    pooled_sd = feats.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = feats / pooled_sd
    cov = np.cov(z.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    components = eigvecs[:, idx][:, :2]
    return z @ components


def permanova_pseudoF(d_mat, labels):
    n = len(d_mat)
    labels = np.asarray(labels)
    unique = np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for g in unique:
        mask = labels == g
        n_g = int(mask.sum())
        if n_g < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_g)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan")
    return (between_ss / (a - 1)) / (within_ss / (n - a))


def cosine_dist(z):
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = u @ u.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    return 1.0 - cos_mat


def permanova_test(pca_feats, labels, rng, n_perms=N_PERMS_PERMANOVA):
    d_mat = cosine_dist(pca_feats)
    F_obs = permanova_pseudoF(d_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
        F_p = permanova_pseudoF(d_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def classifier_cv_accuracy(clf_fn, X, labels, seed):
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    accs = []
    labels = np.asarray(labels)
    for tr_idx, te_idx in skf.split(X, labels):
        clf = clf_fn()
        clf.fit(X[tr_idx], labels[tr_idx])
        pred = clf.predict(X[te_idx])
        acc = float((pred == labels[te_idx]).mean())
        accs.append(acc)
    return float(np.mean(accs))


def classifier_test(clf_fn, X, labels, seed, n_perms=N_PERMS_CLASSIFIER):
    acc_obs = classifier_cv_accuracy(clf_fn, X, labels, seed)
    labels = np.asarray(labels)
    rng = np.random.default_rng(seed)
    n_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(labels)
        acc_p = classifier_cv_accuracy(clf_fn, X, perm, seed)
        if acc_p >= acc_obs:
            n_ge += 1
    return acc_obs, (n_ge + 1) / (n_perms + 1)


def permanova_verdict(F, p):
    if not (np.isfinite(F) and np.isfinite(p)):
        return "NULL"
    if p < ALPHA_BONFERRONI and F > PERMANOVA_F_FLOOR:
        return "PASS"
    if ALPHA_BONFERRONI <= p < ALPHA_WEAK and F > PERMANOVA_F_WEAK:
        return "WEAK PASS"
    return "NULL"


def classifier_verdict(acc, p):
    if not (np.isfinite(acc) and np.isfinite(p)):
        return "NULL"
    if acc >= ACC_STRONG and p < ALPHA_BONFERRONI:
        return "STRONG PASS"
    if acc >= ACC_PASS and p < ALPHA_BONFERRONI:
        return "PASS"
    if acc >= ACC_WEAK and p < ALPHA_WEAK:
        return "WEAK PASS"
    return "NULL"


def level_verdict(verdicts):
    pass_count = sum(1 for v in verdicts.values() if v in ("PASS", "STRONG PASS"))
    weak_count = sum(1 for v in verdicts.values() if v == "WEAK PASS")
    if pass_count >= 2:
        return "LEVEL ROBUST"
    if pass_count == 1 and weak_count >= 1:
        return "LEVEL WEAK"
    if pass_count == 1:
        return "LEVEL WEAK"
    return "LEVEL COLLAPSED"


def main():
    print(f"=== Probe 8d -- test-statistic decomposition (pre-reg literature/48) ===")
    df_raw = pd.read_parquet(IN_PARQUET)
    df_clean = build_clean_table(df_raw)
    print(f"\nClean cells: {len(df_clean)} (expected 101)")
    print(f"PERMANOVA perms: {N_PERMS_PERMANOVA}; Classifier perms: {N_PERMS_CLASSIFIER}")

    rf_factory = lambda: RandomForestClassifier(n_estimators=500, max_depth=None, random_state=42, n_jobs=1)
    lr_factory = lambda: LogisticRegression(solver='lbfgs', max_iter=2000, random_state=42)

    summary_rows = []
    for nl in N1_LEVELS:
        print(f"\n========== {nl['name']} ==========")
        df_noisy = apply_noise(df_clean, nl["sigma_Q"], nl["sigma_Ro"], nl["sigma_Rd"], nl["level"])
        pca_feats = build_pca2(df_noisy)
        for param_col in ["thickness_level", "transference_level", "particle_radius_level"]:
            labels = df_noisy[param_col].values
            # PERMANOVA
            rng_p = np.random.default_rng(RNG_SEED_BASE + 999000 + nl["level"])
            F, p_perm = permanova_test(pca_feats, labels, rng_p)
            perm_v = permanova_verdict(F, p_perm)
            # RF
            acc_rf, p_rf = classifier_test(rf_factory, pca_feats, labels, seed=42)
            rf_v = classifier_verdict(acc_rf, p_rf)
            # Logistic
            acc_lr, p_lr = classifier_test(lr_factory, pca_feats, labels, seed=42)
            lr_v = classifier_verdict(acc_lr, p_lr)
            print(f"  {param_col:25s}: PERMANOVA F={F:7.2f} p={p_perm:.4f} {perm_v:9s} | "
                  f"RF acc={acc_rf:.3f} p={p_rf:.4f} {rf_v:11s} | "
                  f"LR acc={acc_lr:.3f} p={p_lr:.4f} {lr_v:11s}")
            summary_rows.append({
                "level": nl["level"],
                "name": nl["name"],
                "param": param_col,
                "permanova_F": F, "permanova_p": p_perm, "permanova_verdict": perm_v,
                "rf_acc": acc_rf, "rf_p": p_rf, "rf_verdict": rf_v,
                "lr_acc": acc_lr, "lr_p": p_lr, "lr_verdict": lr_v,
            })

    summary = pd.DataFrame(summary_rows)
    out = OUT_DIR / "probe8d_test_statistic_results.parquet"
    summary.to_parquet(out)
    print(f"\nWritten: {out}")

    print(f"\n\n========== PROBE 8d HEADLINES (Level 2) ==========")
    for test in ["permanova", "rf", "lr"]:
        lvl2 = summary[summary["level"] == 2]
        params_pass = sum(1 for _, row in lvl2.iterrows() if row[f"{test}_verdict"] in ("PASS", "STRONG PASS"))
        verdicts_at_l2 = {row["param"]: row[f"{test}_verdict"] for _, row in lvl2.iterrows()}
        if test == "permanova":
            lv = level_verdict({k: v for k, v in verdicts_at_l2.items()})
        else:
            lv = level_verdict({k: v for k, v in verdicts_at_l2.items()})
        print(f"  {test.upper():10s}: {params_pass}/3 (PASS/STRONG) -- "
              f"th: {verdicts_at_l2.get('thickness_level','-')} | "
              f"tn: {verdicts_at_l2.get('transference_level','-')} | "
              f"pr: {verdicts_at_l2.get('particle_radius_level','-')} | {lv}")

    print(f"\n========== DISPOSITION ==========")
    # Check transference at L2
    lvl2 = summary[summary["level"] == 2]
    tn_row = lvl2[lvl2["param"] == "transference_level"].iloc[0]
    perm_tn = tn_row["permanova_verdict"]
    rf_tn = tn_row["rf_verdict"]
    lr_tn = tn_row["lr_verdict"]
    if perm_tn == "NULL" and (rf_tn in ("PASS", "STRONG PASS") or lr_tn in ("PASS", "STRONG PASS")):
        winner = "RF" if rf_tn in ("PASS", "STRONG PASS") else "Logistic"
        print(f"  TEST STATISTIC LOAD-BEARING: {winner} catches transference at L2 where PERMANOVA misses!")
        print(f"  Reopens transference question. Amendment refinement candidate.")
    else:
        # Count agreement
        perm_pass = sum(1 for _, r in lvl2.iterrows() if r["permanova_verdict"] in ("PASS", "STRONG PASS"))
        rf_pass = sum(1 for _, r in lvl2.iterrows() if r["rf_verdict"] in ("PASS", "STRONG PASS"))
        lr_pass = sum(1 for _, r in lvl2.iterrows() if r["lr_verdict"] in ("PASS", "STRONG PASS"))
        if rf_pass >= perm_pass and lr_pass >= perm_pass:
            print(f"  TEST STATISTIC NEUTRAL: PERMANOVA {perm_pass}/3, RF {rf_pass}/3, LR {lr_pass}/3 at L2. Amendment unchanged.")
        elif rf_pass < perm_pass and lr_pass < perm_pass:
            print(f"  PERMANOVA IS LOAD-BEARING CHOICE: PERMANOVA {perm_pass}/3 > RF {rf_pass}/3, LR {lr_pass}/3 at L2.")
        else:
            print(f"  TEST STATISTIC MIXED: PERMANOVA {perm_pass}/3, RF {rf_pass}/3, LR {lr_pass}/3 at L2.")


if __name__ == "__main__":
    main()
