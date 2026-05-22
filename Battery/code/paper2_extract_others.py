"""
Paper 2 — Multi-cohort operator extraction for cohorts other than Severson.

Pulls from existing parquets:
  SECL first-life: features_first_life.parquet  (longitudinal w/ EIS + HPPC)
  Khan 2025:       raw khan_2025/{capacity,eis_csv}/ (re-extract: capacity files
                   + EIS at SOC=50%)
  Zhang Cambridge v2: zhang_features_v2.parquet  (per-sweep longitudinal)
  PyBaMM Probe 5:  pybamm_l9_trajectories.parquet  (full rpts_json)
  WMG:             wmg_25cell_classification.parquet  (snapshot only, EIS-only)

Computes the 12 candidate operators per cell, NaN where not computable.

Output per cohort: paper2_operators_{cohort}.parquet
"""

from pathlib import Path
import json
import re
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


PROCESSED = Path("D:/Renewables/Battery/data/processed")
KHAN_DATA = Path("D:/Renewables/Battery/data/khan_2025")


def _slope(x, y):
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    if np.std(x[mask]) < 1e-12:
        return float("nan")
    return float(np.polyfit(x[mask], y[mask], 1)[0])


def _knee_onset(cycles, q):
    mask = np.isfinite(cycles) & np.isfinite(q)
    cycles = cycles[mask]; q = q[mask]
    if len(q) < 8:
        return float("nan")
    win = min(7, len(q) - (1 - len(q) % 2))
    if win < 5:
        return float("nan")
    if win % 2 == 0:
        win -= 1
    try:
        q_s = savgol_filter(q, win, polyorder=2)
        d2 = np.gradient(np.gradient(q_s, cycles), cycles)
        k_lo = max(1, int(0.1 * len(cycles)))
        k_hi = min(len(cycles) - 1, int(0.9 * len(cycles)))
        if k_hi <= k_lo:
            return float("nan")
        k = int(np.argmax(np.abs(d2[k_lo:k_hi]))) + k_lo
        return float(cycles[k])
    except Exception:
        return float("nan")


def _empty_row(cell_id, cohort):
    return {
        "cell_id": cell_id, "cohort": cohort,
        "T1_Q_fade_early": float("nan"),
        "T2_Q_fade_late": float("nan"),
        "T3_Q_knee_onset": float("nan"),
        "T4_R_DC_growth_rate": float("nan"),
        "T5_R_DC_acceleration": float("nan"),
        "E1_ohmic_intercept": float("nan"),
        "E2_charge_transfer_radius": float("nan"),
        "E3_diffusion_slope": float("nan"),
        "C1_R_growth_per_Q_lost": float("nan"),
        "C2_R_DC_to_R_total": float("nan"),
        "CE1_coulombic_drift": float("nan"),
        "D1_dQdV_peak_shift": float("nan"),
    }


# ---------- SECL first-life ----------

def extract_secl():
    print("=== SECL first-life ===")
    df = pd.read_parquet(PROCESSED / "features_first_life.parquet")
    rows = []
    for cell, g in df.groupby("cell_id"):
        g = g.sort_values("rpt_idx").reset_index(drop=True)
        r = _empty_row(cell, "SECL_first_life")
        # RPT idx serves as "cycle" axis (linearly spaced ~ every 25-50 cycles)
        cycle = g["rpt_idx"].values.astype(float)
        q = g["Q_max_Ah"].values.astype(float)
        r_ohmic = g["R_ohmic_soc50"].values.astype(float) if "R_ohmic_soc50" in g else np.full(len(g), np.nan)
        r_diff = g["R_diff_soc50"].values.astype(float) if "R_diff_soc50" in g else np.full(len(g), np.nan)

        # T1: Q fade rate first few RPTs (~early phase)
        if len(cycle) >= 4:
            r["T1_Q_fade_early"] = _slope(cycle[:min(4, len(cycle))], q[:min(4, len(cycle))])
        # T2: Q fade rate late RPTs
        if len(cycle) >= 6:
            r["T2_Q_fade_late"] = _slope(cycle[-min(5, len(cycle)):], q[-min(5, len(cycle)):])
        # T3: knee
        r["T3_Q_knee_onset"] = _knee_onset(cycle, q)
        # T4: R_ohmic slope (using R_ohmic@SOC50 as R_DC analog)
        if np.any(np.isfinite(r_ohmic)) and len(cycle) >= 4:
            r["T4_R_DC_growth_rate"] = _slope(cycle[:min(6, len(cycle))], r_ohmic[:min(6, len(cycle))])
        # T5: max |d2 R_ohmic|
        if (np.isfinite(r_ohmic)).sum() >= 6:
            try:
                rs = savgol_filter(r_ohmic[np.isfinite(r_ohmic)], min(5, np.isfinite(r_ohmic).sum() - 1), polyorder=2)
                cs = cycle[np.isfinite(r_ohmic)]
                if len(rs) >= 3:
                    d2 = np.gradient(np.gradient(rs, cs), cs)
                    r["T5_R_DC_acceleration"] = float(np.max(np.abs(d2)))
            except Exception:
                pass
        # E1, E2, E3 -- need full EIS spectrum to fit; we only have R_ohmic + R_diff at SOC=50.
        # Use them as proxies: E1 ≈ R_ohmic (mean of fresh), E2 = R_diff - R_ohmic (semicircle ≈ charge-transfer),
        # E3 = NaN (no full Warburg slope)
        fresh_r_ohmic = r_ohmic[:3] if len(r_ohmic) >= 3 else r_ohmic
        fresh_r_diff = r_diff[:3] if len(r_diff) >= 3 else r_diff
        r["E1_ohmic_intercept"] = float(np.nanmean(fresh_r_ohmic)) if len(fresh_r_ohmic) else float("nan")
        if len(fresh_r_diff) and len(fresh_r_ohmic):
            r["E2_charge_transfer_radius"] = float(np.nanmean(fresh_r_diff) - np.nanmean(fresh_r_ohmic))
        r["E3_diffusion_slope"] = float("nan")  # need full EIS spectrum, not present in this parquet
        # C1
        if np.isfinite(r["T4_R_DC_growth_rate"]) and np.isfinite(r["T2_Q_fade_late"]) and abs(r["T2_Q_fade_late"]) > 1e-12:
            r["C1_R_growth_per_Q_lost"] = r["T4_R_DC_growth_rate"] / abs(r["T2_Q_fade_late"])
        # C2: R_ohmic / R_diff ratio
        if len(fresh_r_diff) and len(fresh_r_ohmic):
            denom = float(np.nanmean(fresh_r_diff))
            if abs(denom) > 1e-12:
                r["C2_R_DC_to_R_total"] = float(np.nanmean(fresh_r_ohmic)) / denom
        # CE1, D1 -- need raw cycling data not in features parquet; NaN
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper2_operators_secl.parquet")
    print(f"  SECL: {len(out)} cells, written.")
    return out


# ---------- Khan 2025 ----------

def extract_khan():
    print("=== Khan 2025 ===")
    # Re-extract from raw khan_2025 data per khan_extract_and_classify pipeline
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from khan_extract_and_classify import (
            extract_qmax_per_cell_per_day, extract_eis_per_cell_per_day, EXCLUDE_CELLS
        )
        cap = extract_qmax_per_cell_per_day()
        eis = extract_eis_per_cell_per_day(soc="S50")
    except Exception as e:
        print(f"  Khan extraction error: {e}")
        return pd.DataFrame()
    df = cap.merge(eis, on=["cell_id", "day"], how="inner")
    rows = []
    for cell, g in df.groupby("cell_id"):
        g = g.sort_values("day").reset_index(drop=True)
        r = _empty_row(cell, "Khan_2025")
        day = g["day"].values.astype(float)
        q = g["Q_max_Ah"].values.astype(float)
        r_oh = g["R_ohmic"].values.astype(float)
        r_di = g["R_diff"].values.astype(float)
        # 5 timepoints (0, 10, 20, 40, 90 days) -- limited; T1 ~ early slope, T2 hard
        if len(day) >= 3:
            r["T1_Q_fade_early"] = _slope(day[:min(3, len(day))], q[:min(3, len(day))])
        if len(day) >= 3:
            r["T2_Q_fade_late"] = _slope(day[-min(3, len(day)):], q[-min(3, len(day)):])
        r["T3_Q_knee_onset"] = _knee_onset(day, q)
        if len(day) >= 3:
            r["T4_R_DC_growth_rate"] = _slope(day[:min(3, len(day))], r_oh[:min(3, len(day))])
            if (np.isfinite(r_oh)).sum() >= 4:
                try:
                    rs = savgol_filter(r_oh[np.isfinite(r_oh)], min(5, np.isfinite(r_oh).sum() - 1), polyorder=2)
                    cs = day[np.isfinite(r_oh)]
                    if len(rs) >= 3:
                        d2 = np.gradient(np.gradient(rs, cs), cs)
                        r["T5_R_DC_acceleration"] = float(np.max(np.abs(d2)))
                except Exception:
                    pass
        # E1 = R_ohmic fresh, E2 = R_diff - R_ohmic at fresh, E3 = NaN (no full spectrum here)
        if len(r_oh) > 0:
            r["E1_ohmic_intercept"] = float(r_oh[0])
        if len(r_oh) > 0 and len(r_di) > 0:
            r["E2_charge_transfer_radius"] = float(r_di[0] - r_oh[0])
        r["E3_diffusion_slope"] = float("nan")
        if np.isfinite(r["T4_R_DC_growth_rate"]) and np.isfinite(r["T2_Q_fade_late"]) and abs(r["T2_Q_fade_late"]) > 1e-12:
            r["C1_R_growth_per_Q_lost"] = r["T4_R_DC_growth_rate"] / abs(r["T2_Q_fade_late"])
        if len(r_di) > 0 and abs(float(r_di[0])) > 1e-12:
            r["C2_R_DC_to_R_total"] = float(r_oh[0]) / float(r_di[0])
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper2_operators_khan.parquet")
    print(f"  Khan: {len(out)} cells, written.")
    return out


# ---------- Zhang Cambridge v2 ----------

def extract_zhang():
    print("=== Zhang Cambridge v2 ===")
    df = pd.read_parquet(PROCESSED / "zhang_features_v2.parquet")
    rows = []
    for cell, g in df.groupby("cell_id"):
        g = g.sort_values("sweep").reset_index(drop=True)
        r = _empty_row(cell, "Zhang_Cambridge_v2")
        cycle = g["sweep"].values.astype(float)  # sweep index serves as cycle proxy
        q = g["Q_max"].values.astype(float)
        r_oh = g["R_ohmic"].values.astype(float)
        r_di = g["R_diff"].values.astype(float)
        # Zhang has ~190 sweeps per cell -- generous trajectory data
        if len(cycle) >= 10:
            n_early = max(3, len(cycle) // 4)
            r["T1_Q_fade_early"] = _slope(cycle[:n_early], q[:n_early])
            r["T2_Q_fade_late"] = _slope(cycle[-n_early:], q[-n_early:])
        r["T3_Q_knee_onset"] = _knee_onset(cycle, q)
        if len(cycle) >= 10:
            r["T4_R_DC_growth_rate"] = _slope(cycle[:max(3, len(cycle)//4)], r_oh[:max(3, len(cycle)//4)])
            try:
                rs = savgol_filter(r_oh[np.isfinite(r_oh)], min(11, (np.isfinite(r_oh).sum() - 1) | 1), polyorder=2)
                cs = cycle[np.isfinite(r_oh)]
                if len(rs) >= 5:
                    d2 = np.gradient(np.gradient(rs, cs), cs)
                    r["T5_R_DC_acceleration"] = float(np.max(np.abs(d2)))
            except Exception:
                pass
        fresh_oh = r_oh[:5] if len(r_oh) >= 5 else r_oh
        fresh_di = r_di[:5] if len(r_di) >= 5 else r_di
        if len(fresh_oh):
            r["E1_ohmic_intercept"] = float(np.nanmean(fresh_oh))
        if len(fresh_oh) and len(fresh_di):
            r["E2_charge_transfer_radius"] = float(np.nanmean(fresh_di) - np.nanmean(fresh_oh))
        r["E3_diffusion_slope"] = float("nan")
        if np.isfinite(r["T4_R_DC_growth_rate"]) and np.isfinite(r["T2_Q_fade_late"]) and abs(r["T2_Q_fade_late"]) > 1e-12:
            r["C1_R_growth_per_Q_lost"] = r["T4_R_DC_growth_rate"] / abs(r["T2_Q_fade_late"])
        if len(fresh_di):
            denom = float(np.nanmean(fresh_di))
            if abs(denom) > 1e-12:
                r["C2_R_DC_to_R_total"] = float(np.nanmean(fresh_oh)) / denom
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper2_operators_zhang.parquet")
    print(f"  Zhang: {len(out)} cells, written.")
    return out


# ---------- PyBaMM Probe 5 ----------

def extract_pybamm():
    print("=== PyBaMM Probe 5 ===")
    df = pd.read_parquet(PROCESSED / "pybamm_l9_trajectories.parquet")
    df = df[df["error"].isna()].copy() if "error" in df.columns else df.copy()
    rows = []
    for _, row in df.iterrows():
        rpts = json.loads(row["rpts_json"]) if isinstance(row["rpts_json"], str) else row["rpts_json"]
        if not rpts:
            continue
        cell_id = f"PyBaMM_C{int(row['cond_idx'])}_K{int(row['cell_idx'])}"
        r = _empty_row(cell_id, "PyBaMM_L9")
        cycle = np.array([p["cycle"] for p in rpts], dtype=float)
        q = np.array([p["Q_max"] for p in rpts], dtype=float)
        r_dc = np.array([p["R_DC"] for p in rpts], dtype=float)
        r_tot = np.array([p["R_total"] for p in rpts], dtype=float)
        n = len(cycle)
        if n >= 5:
            n_early = max(3, n // 4)
            r["T1_Q_fade_early"] = _slope(cycle[:n_early], q[:n_early])
            r["T2_Q_fade_late"] = _slope(cycle[-n_early:], q[-n_early:])
        r["T3_Q_knee_onset"] = _knee_onset(cycle, q)
        if n >= 5:
            r["T4_R_DC_growth_rate"] = _slope(cycle[:max(3, n//4)], r_dc[:max(3, n//4)])
            try:
                rs = savgol_filter(r_dc[np.isfinite(r_dc)], min(7, (np.isfinite(r_dc).sum() - 1) | 1), polyorder=2)
                cs = cycle[np.isfinite(r_dc)]
                if len(rs) >= 5:
                    d2 = np.gradient(np.gradient(rs, cs), cs)
                    r["T5_R_DC_acceleration"] = float(np.max(np.abs(d2)))
            except Exception:
                pass
        # PyBaMM has no EIS -- mark E1-E3 NaN
        if np.isfinite(r["T4_R_DC_growth_rate"]) and np.isfinite(r["T2_Q_fade_late"]) and abs(r["T2_Q_fade_late"]) > 1e-12:
            r["C1_R_growth_per_Q_lost"] = r["T4_R_DC_growth_rate"] / abs(r["T2_Q_fade_late"])
        # C2: R_DC / R_total (both are time-domain proxies)
        fresh_r_dc = r_dc[:5] if n >= 5 else r_dc
        fresh_r_tot = r_tot[:5] if n >= 5 else r_tot
        denom = float(np.nanmean(fresh_r_tot)) if len(fresh_r_tot) else float("nan")
        if abs(denom) > 1e-12:
            r["C2_R_DC_to_R_total"] = float(np.nanmean(fresh_r_dc)) / denom
        # Add cohort metadata for design labels
        r["thickness_level"] = row["thickness_level"]
        r["transference_level"] = row["transference_level"]
        r["particle_radius_level"] = row["particle_radius_level"]
        r["cond_idx"] = int(row["cond_idx"])
        r["cell_idx"] = int(row["cell_idx"])
        rows.append(r)

    full = pd.DataFrame(rows)
    # Deterministic train/holdout split per literature/28 §2
    # seed = 3000 + cond_idx; 8 train, 4 holdout per condition
    train_rows = []
    holdout_rows = []
    for c in range(9):
        sub = full[full["cond_idx"] == c].sort_values("cell_idx").reset_index(drop=True)
        if len(sub) < 12:
            # fewer than expected; assign first ⌈8/12 * len⌉ to train
            n_train = max(1, int(round(len(sub) * 8 / 12)))
        else:
            n_train = 8
        rng = np.random.default_rng(3000 + c)
        idx = rng.permutation(len(sub))
        train_idx = idx[:n_train]
        holdout_idx = idx[n_train:]
        train_rows.append(sub.iloc[train_idx])
        holdout_rows.append(sub.iloc[holdout_idx])
    train_df = pd.concat(train_rows, ignore_index=True)
    holdout_df = pd.concat(holdout_rows, ignore_index=True)
    train_df.to_parquet(PROCESSED / "paper2_operators_pybamm_train.parquet")
    holdout_df.to_parquet(PROCESSED / "paper2_operators_pybamm_holdout.parquet")
    print(f"  PyBaMM: {len(full)} cells -> {len(train_df)} train + {len(holdout_df)} holdout, written.")
    return full


# ---------- WMG ----------

def extract_wmg():
    print("=== WMG ===")
    df = pd.read_parquet(PROCESSED / "wmg_25cell_classification.parquet")
    rows = []
    for _, row in df.iterrows():
        r = _empty_row(f"WMG_Cell{int(row['cell']):02d}", "WMG_25cell")
        # Snapshot only: no trajectory ops. EIS-derived ops only.
        r["E1_ohmic_intercept"] = float(row.get("R_ohmic", float("nan")))
        # E2 = R_diff - R_ohmic (charge-transfer proxy)
        if "R_diff" in row and "R_ohmic" in row:
            r["E2_charge_transfer_radius"] = float(row["R_diff"]) - float(row["R_ohmic"])
        r["E3_diffusion_slope"] = float("nan")  # no full spectrum available in classification parquet
        # C2: R_ohmic / R_diff at fresh = same as cohort baseline ratio
        if "R_diff" in row and abs(float(row["R_diff"])) > 1e-12:
            r["C2_R_DC_to_R_total"] = float(row["R_ohmic"]) / float(row["R_diff"])
        r["soh_eis"] = int(row.get("soh_eis", -1))
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper2_operators_wmg.parquet")
    print(f"  WMG: {len(out)} cells, written.")
    return out


def main():
    print(f"=== Paper 2 multi-cohort operator extraction ===\n")
    secl = extract_secl()
    khan = extract_khan()
    zhang = extract_zhang()
    pybamm = extract_pybamm()
    wmg = extract_wmg()

    # Summary
    print("\n=== Per-cohort row counts ===")
    print(f"  SECL_first_life:    {len(secl)}")
    print(f"  Khan_2025:          {len(khan)}")
    print(f"  Zhang_Cambridge_v2: {len(zhang)}")
    print(f"  PyBaMM_L9 (total):  {len(pybamm)}")
    print(f"  WMG_25cell:         {len(wmg)}")


if __name__ == "__main__":
    main()
