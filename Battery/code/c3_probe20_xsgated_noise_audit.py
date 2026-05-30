"""C3 Probe 20 - Noise-robustness audit of the cross-substrate-gated {E1, C2} cascade.

Pre-reg: literature/74_probe20_xsgated_cascade_noise_audit_prereg.md (lock c4acbd5).
Inputs (reused unchanged): Probe-15/16 operator parquets + Khan conditions CSV.
Output: data/processed/probe20_xsgated_noise_audit_results.parquet

Applies the lit/34 noise grid (multiplicative per-feature Gaussian) to the Probe-16 cascade
+ protocol on WMG transfer. Per noise level × feature set × 200 seeds: inject noise into
Xtr (Khan+SECL+Zhang) AND Xwmg, run RF (fixed random_state=42) -> leaf-PCA -> WMG PERMANOVA
F. Reference-seed (b=42) at each level with full 10k-perm p for headline.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe15_crosssubstrate_gate import load_training, cascade_F

PROCESSED = Path("D:/Renewables/Battery/data/processed")
OUT = PROCESSED / "probe20_xsgated_noise_audit_results.parquet"

# Locked noise grid (per lit/34, applied to feature classes)
NOISE_LEVELS = [
    {"level": 0, "name": "L0 baseline",    "Ro": 0.00, "Rd": 0.00, "C2": 0.000},
    {"level": 1, "name": "L1 best lab",    "Ro": 0.05, "Rd": 0.10, "C2": 0.001},
    {"level": 2, "name": "L2 academic",    "Ro": 0.15, "Rd": 0.20, "C2": 0.005},
    {"level": 3, "name": "L3 noisy field", "Ro": 0.30, "Rd": 0.30, "C2": 0.010},
    {"level": 4, "name": "L4 instrument",  "Ro": 0.50, "Rd": 0.50, "C2": 0.020},
]
N_SEEDS = 200
RF_SEED = 42
F_PASS, F_LO_BAR, P_BAR = 3.0, 2.0, 0.05

# feature-class sigma map
def sigma_for(col, ln):
    if col.startswith("C2"):
        return ln["C2"]
    if col.startswith("E1") or col == "R_ohmic":
        return ln["Ro"]
    if col.startswith("E2") or col == "R_diff":
        return ln["Rd"]
    return ln["Rd"]  # default

FEATURE_SETS = {
    "C2_only": ["C2_R_DC_to_R_total"],
    "E1C2":    ["E1_ohmic_intercept", "C2_R_DC_to_R_total"],
    "E1E2C2":  ["E1_ohmic_intercept", "E2_charge_transfer_radius", "C2_R_DC_to_R_total"],
}


def inject(X, sigmas, rng):
    if all(s == 0 for s in sigmas):
        return X.copy()
    out = X.astype(float).copy()
    for j, s in enumerate(sigmas):
        if s > 0:
            out[:, j] = out[:, j] * (1.0 + rng.normal(0, s, size=out.shape[0]))
    return out


def main():
    khan, secl, zhang, klab, slab, zlab = load_training()
    wmg = pd.read_parquet(PROCESSED / "paper2_operators_wmg.parquet")
    soh_bins = wmg["soh_eis"].values
    y = np.concatenate([klab, slab, zlab])
    print(f"Cohort: train n={len(y)}  test WMG n={len(wmg)}")

    rows = []
    print("\n=== Noise audit: 5 levels × 3 feature sets × 200 seeds ===")
    for ln in NOISE_LEVELS:
        for fname, feats in FEATURE_SETS.items():
            sigmas = [sigma_for(c, ln) for c in feats]
            # base matrices
            Xtr_base = np.vstack([khan[feats].values, secl[feats].values, zhang[feats].values]).astype(float)
            Xwmg_base = wmg[feats].values.astype(float)
            # multi-seed
            Fs = np.empty(N_SEEDS)
            for b in range(N_SEEDS):
                rng_tr = np.random.default_rng(b + ln["level"] * 1_000_000)
                rng_te = np.random.default_rng(b + ln["level"] * 1_000_000 + 500)
                Xtr_n = inject(Xtr_base, sigmas, rng_tr)
                Xwmg_n = inject(Xwmg_base, sigmas, rng_te)
                Fs[b] = cascade_F(feats, RF_SEED, Xtr_n, y, Xwmg_n, soh_bins, with_p=False)
            med, lo, hi = float(np.median(Fs)), float(np.percentile(Fs, 2.5)), float(np.percentile(Fs, 97.5))
            # ref-seed full p
            rng_tr_r = np.random.default_rng(42 + ln["level"] * 1_000_000)
            rng_te_r = np.random.default_rng(42 + ln["level"] * 1_000_000 + 500)
            Xtr_r = inject(Xtr_base, sigmas, rng_tr_r)
            Xwmg_r = inject(Xwmg_base, sigmas, rng_te_r)
            (F_ref, p_ref), _, _, _ = cascade_F(feats, RF_SEED, Xtr_r, y, Xwmg_r, soh_bins, with_p=True)
            pass_main = (med > F_PASS) and (lo > F_LO_BAR) and (p_ref < P_BAR)
            rows.append({"level": ln["level"], "level_name": ln["name"],
                         "feature_set": fname, "n_feat": len(feats),
                         "F_median": med, "F_2.5pct": lo, "F_97.5pct": hi,
                         "F_ref": F_ref, "p_ref": p_ref, "pass_main": pass_main})
            print(f"  {ln['name']:18s} {fname:8s}: med={med:5.2f} [{lo:5.2f}, {hi:5.2f}]  refF={F_ref:5.2f} p={p_ref:.4f}  {'PASS' if pass_main else 'fail'}")

    rdf = pd.DataFrame(rows)
    rdf.to_parquet(OUT)

    # ---- disposition (H20-main on {E1C2} at L2) ----
    L0 = rdf[(rdf.feature_set == "E1C2") & (rdf.level == 0)].iloc[0]
    L2 = rdf[(rdf.feature_set == "E1C2") & (rdf.level == 2)].iloc[0]
    L1 = rdf[(rdf.feature_set == "E1C2") & (rdf.level == 1)].iloc[0]
    L4_any = rdf[(rdf.level == 4)]
    f1_ok = abs(L0.F_median - 3.681) < 0.1  # Probe 16 ref-seed clean
    f2_ok = (L4_any.F_median < 3).all()      # noise actually degrades

    if not f1_ok:
        disp = "PROBE 20 INVALID (L0 doesn't reproduce Probe-16 clean anchor)"
    elif bool(L2.pass_main):
        disp = "NOISE-ROBUST"
    elif bool(L1.pass_main):
        disp = "NOISE-FRAGILE-AT-L2"
    else:
        disp = "NOISE-FRAGILE-AT-L1"

    print("\n" + "=" * 78)
    print("PROBE 20 DISPOSITION (per lit/74 §5)")
    print("=" * 78)
    print(f"  F1 L0 reproduces Probe-16:   {'PASS' if f1_ok else 'FAIL'} (L0 E1C2 median={L0.F_median:.3f} vs anchor 3.681)")
    print(f"  F2 noise degrades at L4:     {'PASS' if f2_ok else 'FAIL'}")
    print(f"  H20-main {{E1,C2}} at L2:      {'PASS' if L2.pass_main else 'FAIL'} (med={L2.F_median:.2f}>3? 2.5pct={L2['F_2.5pct']:.2f}>2? p={L2.p_ref:.4f}<0.05?)")
    print(f"  L1 reference (best lab):     {'PASS' if L1.pass_main else 'FAIL'} (med={L1.F_median:.2f})")
    print(f"\n  ==> {disp}")
    print(f"\nWritten: {OUT}")
    print("=" * 78)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 78)


if __name__ == "__main__":
    main()
