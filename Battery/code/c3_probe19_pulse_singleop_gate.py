"""C3 Probe 19 - Single-operator promotion gate for eta_8s_pulse_{363,400} (SECL SOH).

Pre-reg: literature/72_probe19_pulse_singleop_promotion_prereg.md (lock cc1c6d5).
Inputs (reused unchanged):
  data/processed/secl_pulse_ops.parquet           (Probe 18, SHA 6e9765aa...)
  data/processed/secl_eis_soh_observations.parquet (Probe 11, SHA 9dd867c5...)
Output:
  data/processed/probe19_pulse_singleop_gate_results.parquet

Cell-stratified bootstrap (N=500) + observation bootstrap (N=500) of the 1D PERMANOVA F
for the candidate dominant operators (anchor F=44.33 / 42.25 from Probe 18 F4). Paired
comparison vs EIS_6D cascade F (anchor 25.51). H19-main: median>25 AND 2.5pct>10 (both
bootstrap modes, both operators). H19-secondary: paired pulse>EIS in >=97.5% (cell-strat).
F3: ±2%-tertile-edge sensitivity arm.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c3_probe9_extended_permanova import build_pca, cosine_dist, permanova_pseudoF

PULSE = Path("D:/Renewables/Battery/data/processed/secl_pulse_ops.parquet")
EIS = Path("D:/Renewables/Battery/data/processed/secl_eis_soh_observations.parquet")
OUT = Path("D:/Renewables/Battery/data/processed/probe19_pulse_singleop_gate_results.parquet")

EIS_COLS = ["R_ohmic_326", "R_diff_326", "R_ohmic_363", "R_diff_363", "R_ohmic_400", "R_diff_400"]
CANDIDATES = ["eta_8s_pulse_363", "eta_8s_pulse_400"]
ANCHORS = {"eta_8s_pulse_363": 44.33, "eta_8s_pulse_400": 42.25, "EIS_6D": 25.51}
N_BOOT = 500
F_MEDIAN_BAR = 25.0
F_LO_BAR = 10.0
PAIRED_DOM_BAR = 0.975


def tertile_labels(soh, perturb_pct=0.0):
    q1, q2 = np.quantile(soh, [1/3, 2/3])
    if perturb_pct != 0:
        span = soh.max() - soh.min()
        q1 += perturb_pct/100 * span
        q2 += perturb_pct/100 * span
    return np.digitize(soh, [q1, q2])


def F_1d(x, labels):
    x = np.asarray(x, dtype=float)
    s = x.std()
    if s < 1e-12:
        return float("nan")
    z = ((x - x.mean()) / s).reshape(-1, 1)
    return permanova_pseudoF(cosine_dist(z), labels)


def F_eis6d(X, labels, k=2):
    pca, _ = build_pca(X, k)
    return permanova_pseudoF(cosine_dist(pca), labels)


def cell_strat_resample(df, rng):
    cells = sorted(df["cell"].unique())
    pick = rng.choice(cells, size=len(cells), replace=True)
    parts = [df[df.cell == c] for c in pick]
    res = pd.concat(parts, ignore_index=True)
    return res, len(set(pick))


def obs_resample(df, rng):
    idx = rng.choice(len(df), size=len(df), replace=True)
    return df.iloc[idx].reset_index(drop=True)


def boot_distributions(merged, mode, n=N_BOOT, perturb_pct=0.0, seed_base=0):
    """Return per-op F distribution + paired pulse-vs-EIS flags."""
    out = {op: np.empty(n) for op in CANDIDATES + ["EIS_6D"]}
    paired_pulse_gt = {op: 0 for op in CANDIDATES}
    n_degen = 0
    for b in range(n):
        rng = np.random.default_rng(seed_base + b)
        if mode == "cell":
            res, n_unique = cell_strat_resample(merged, rng)
            if n_unique < 2:
                n_degen += 1
                for op in out: out[op][b] = float("nan")
                continue
        else:
            res = obs_resample(merged, rng)
        soh = res["SOH"].values
        labels = tertile_labels(soh, perturb_pct=perturb_pct)
        if len(np.unique(labels)) < 2:
            n_degen += 1
            for op in out: out[op][b] = float("nan")
            continue
        for op in CANDIDATES:
            out[op][b] = F_1d(res[op].values, labels)
        out["EIS_6D"][b] = F_eis6d(res[EIS_COLS].values.astype(float), labels)
        for op in CANDIDATES:
            if np.isfinite(out[op][b]) and np.isfinite(out["EIS_6D"][b]) and out[op][b] > out["EIS_6D"][b]:
                paired_pulse_gt[op] += 1
    n_eff = n - n_degen
    paired_frac = {op: paired_pulse_gt[op] / max(1, n_eff) for op in CANDIDATES}
    return out, paired_frac, n_degen


def summary(F):
    F = F[np.isfinite(F)]
    return {"n": int(len(F)), "median": float(np.median(F)),
            "p2_5": float(np.percentile(F, 2.5)), "p97_5": float(np.percentile(F, 97.5)),
            "min": float(F.min()), "max": float(F.max())}


def main():
    pulse = pd.read_parquet(PULSE)
    eis = pd.read_parquet(EIS)
    merged = pulse.merge(eis, on=["cell", "round"], how="inner").reset_index(drop=True)
    print(f"Locked Probe-18 cohort: n={len(merged)} cells={sorted(merged.cell.unique())} SOH {merged.SOH.min()*100:.1f}-{merged.SOH.max()*100:.1f}%")

    # ---- F1 anchor reproduction ----
    labels0 = tertile_labels(merged.SOH.values)
    print("\n=== F1 anchor reproduction (deterministic cohort) ===")
    anchor_fs = {}
    for op in CANDIDATES:
        F = F_1d(merged[op].values, labels0)
        anchor_fs[op] = F
        ok = abs(F - ANCHORS[op]) < 0.05
        print(f"  {op:22s} F={F:7.3f}  expected ~{ANCHORS[op]}  {'OK' if ok else 'MISMATCH'}")
    F_eis = F_eis6d(merged[EIS_COLS].values.astype(float), labels0)
    anchor_fs["EIS_6D"] = F_eis
    ok_eis = abs(F_eis - ANCHORS["EIS_6D"]) < 0.05
    print(f"  EIS_6D                 F={F_eis:7.3f}  expected ~{ANCHORS['EIS_6D']}  {'OK' if ok_eis else 'MISMATCH'}")
    f1_ok = all(abs(anchor_fs[k] - ANCHORS[k]) < 0.05 for k in anchor_fs)

    # ---- H19-main: cell-stratified bootstrap ----
    print(f"\n=== Cell-stratified bootstrap (N={N_BOOT}) ===")
    cell_out, paired_cell, n_degen_c = boot_distributions(merged, "cell", n=N_BOOT, seed_base=0)
    print(f"  degenerate resamples (single-cell or single-tertile): {n_degen_c}/{N_BOOT}")
    cell_summary = {op: summary(cell_out[op]) for op in cell_out}
    for op in CANDIDATES + ["EIS_6D"]:
        s = cell_summary[op]
        print(f"  {op:22s} median={s['median']:7.2f} [{s['p2_5']:6.2f}, {s['p97_5']:6.2f}]  min={s['min']:.2f} max={s['max']:.2f}")
    print(f"  paired pulse>EIS fraction (cell-strat): "
          f"eta_363={paired_cell['eta_8s_pulse_363']:.3f}  eta_400={paired_cell['eta_8s_pulse_400']:.3f}")

    # ---- H19-main: observation bootstrap ----
    print(f"\n=== Observation bootstrap (N={N_BOOT}) ===")
    obs_out, _, n_degen_o = boot_distributions(merged, "obs", n=N_BOOT, seed_base=10000)
    print(f"  degenerate resamples: {n_degen_o}/{N_BOOT}")
    obs_summary = {op: summary(obs_out[op]) for op in obs_out}
    for op in CANDIDATES + ["EIS_6D"]:
        s = obs_summary[op]
        print(f"  {op:22s} median={s['median']:7.2f} [{s['p2_5']:6.2f}, {s['p97_5']:6.2f}]  min={s['min']:.2f} max={s['max']:.2f}")

    # ---- F3: tertile-edge ±2% perturbation (cell-strat) ----
    print(f"\n=== F3 tertile-edge sensitivity (±2%, cell-strat N={N_BOOT}) ===")
    tert_sens = {}
    for sign in [-2, +2]:
        out_p, _, _ = boot_distributions(merged, "cell", n=N_BOOT, perturb_pct=sign, seed_base=20000+sign)
        for op in CANDIDATES:
            s = summary(out_p[op])
            key = f"{op}_perturb_{sign:+d}pct"
            tert_sens[key] = s
            print(f"  {op:22s} {sign:+d}%  median={s['median']:7.2f} [{s['p2_5']:6.2f}, {s['p97_5']:6.2f}]")

    # ---- H19-main / H19-secondary verdicts ----
    def main_ok(op):
        c = cell_summary[op]; o = obs_summary[op]
        return (c["median"] > F_MEDIAN_BAR and c["p2_5"] > F_LO_BAR and
                o["median"] > F_MEDIAN_BAR and o["p2_5"] > F_LO_BAR)
    main_passes = {op: main_ok(op) for op in CANDIDATES}
    sec_passes = {op: paired_cell[op] >= PAIRED_DOM_BAR for op in CANDIDATES}

    # F3 verdict flip: median<25 OR 2.5pct<10 under either ±2% perturbation
    f3_flips = {}
    for op in CANDIDATES:
        flipped = False
        for sign in [-2, +2]:
            s = tert_sens[f"{op}_perturb_{sign:+d}pct"]
            if s["median"] <= F_MEDIAN_BAR or s["p2_5"] <= F_LO_BAR:
                if main_passes[op]:
                    flipped = True
        f3_flips[op] = flipped

    # disposition
    both_main = all(main_passes.values())
    both_sec = all(sec_passes.values())
    any_main = any(main_passes.values())
    any_flip = any(f3_flips.values())
    if not f1_ok:
        disp = "PROBE 19 INVALID (anchor F mismatch)"
    elif any_flip:
        disp = "BIN-ARTIFACT (tertile-edge ±2% flips H19-main verdict)"
    elif both_main and both_sec:
        disp = "PULSE-OP-DOMINANCE-PROMOTED"
    elif any_main:
        disp = "PULSE-OP-DOMINANCE-PARTIAL"
    else:
        disp = "PULSE-OP-DOMINANCE-WASHES-OUT"

    print("\n" + "=" * 76)
    print("PROBE 19 DISPOSITION (per lit/72 §5)")
    print("=" * 76)
    print(f"  F1 anchor reproduction:                    {'PASS' if f1_ok else 'FAIL'}")
    for op in CANDIDATES:
        c = cell_summary[op]; o = obs_summary[op]
        print(f"  H19-main {op}:")
        print(f"     cell-strat median={c['median']:.2f}>25? {c['median']>F_MEDIAN_BAR}  2.5pct={c['p2_5']:.2f}>10? {c['p2_5']>F_LO_BAR}")
        print(f"     obs-boot  median={o['median']:.2f}>25? {o['median']>F_MEDIAN_BAR}  2.5pct={o['p2_5']:.2f}>10? {o['p2_5']>F_LO_BAR}")
        print(f"     -> H19-main {op}: {'PASS' if main_passes[op] else 'FAIL'}")
        print(f"     H19-sec paired pulse>EIS frac={paired_cell[op]:.3f} >= 0.975? -> {'PASS' if sec_passes[op] else 'FAIL'}")
        print(f"     F3 tertile-edge flip: {'YES (flipped)' if f3_flips[op] else 'no'}")
    print(f"\n  ==> {disp}")

    # persist
    rows = []
    for op in CANDIDATES + ["EIS_6D"]:
        c = cell_summary[op]; o = obs_summary[op]
        rows.append({"op": op, "anchor_F": anchor_fs[op],
                     "cell_strat_median": c["median"], "cell_strat_2.5pct": c["p2_5"], "cell_strat_97.5pct": c["p97_5"],
                     "obs_boot_median": o["median"], "obs_boot_2.5pct": o["p2_5"], "obs_boot_97.5pct": o["p97_5"],
                     "paired_pulse_gt_EIS_frac": paired_cell.get(op, float("nan"))})
    pd.DataFrame(rows).assign(disposition=disp).to_parquet(OUT)
    print(f"\nWritten: {OUT}")
    print("=" * 76)
    print(f"FINAL DISPOSITION: {disp}")
    print("=" * 76)


if __name__ == "__main__":
    main()
