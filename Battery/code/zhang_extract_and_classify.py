"""
Phase 4 confirmation — Zhang Cambridge 2020 held-out cohort.

12 cells (8 at 25°C, 2 at 35°C, 2 at 45°C). Per cell, 9 aging states
(I, II, III, IV, V, VI, VII, VIII, IX). Per state, capacity + full EIS spectrum.

Features per (cell, state):
  Q_max_Ah:  max discharge capacity at that aging state (from cap trajectory)
  R_ohmic:   Re(Z) at highest frequency (from EIS spectrum)
  R_diff:    Re(Z) at lowest frequency

Fresh reference: per-cell state I (the freshest state for that cell).

For the Phase 4 pre-reg, only 25°C cohort is comparable to SECL (which is at
23-25°C). 35/45°C cells are reported as supplementary; they're a different
aging-temperature regime.
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd
from scipy import stats


BASE = Path("D:/Renewables/Battery/data/zhang_cambridge")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")

U_LLI = np.array([-1.0, 0.0, 0.0])
U_LLI = U_LLI / np.linalg.norm(U_LLI)
U_LAM_SEI = np.array([-1.0, +1.0, +1.0])
U_LAM_SEI = U_LAM_SEI / np.linalg.norm(U_LAM_SEI)
CONF = 0.3
STATES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]


def parse_eis_file(path: Path):
    """Return DataFrame with EIS data."""
    df = pd.read_csv(path, sep="\t", engine="python", header=0)
    df.columns = [c.strip() for c in df.columns]
    fcol = next((c for c in df.columns if c.startswith("freq") or "Hz" in c), None)
    rcol = next((c for c in df.columns if c.startswith("Re(Z)") or "Re(Z)" in c), None)
    cyc_col = next((c for c in df.columns if "cycle" in c.lower()), None)
    if fcol is None or rcol is None:
        raise ValueError(f"missing freq/Re(Z) cols in {path.name}: {list(df.columns)}")
    keep = [fcol, rcol]
    if cyc_col:
        keep.append(cyc_col)
    df = df[keep].rename(columns={fcol: "freq", rcol: "ReZ"})
    if cyc_col:
        df = df.rename(columns={cyc_col: "cycle"})
    else:
        df["cycle"] = np.nan
    return df


def extract_eis_features(path: Path):
    """Return (R_ohmic, R_diff, eis_cycle) for the file."""
    try:
        df = parse_eis_file(path)
    except Exception as e:
        print(f"  [eis parse fail] {path.name}: {e}")
        return float("nan"), float("nan"), float("nan")
    if df.empty:
        return float("nan"), float("nan"), float("nan")
    # Sort by freq, take first (highest freq → R_ohmic) and last (lowest freq → R_diff)
    df_sorted = df.sort_values("freq").reset_index(drop=True)
    r_diff = float(df_sorted.iloc[0]["ReZ"])     # lowest freq
    r_ohmic = float(df_sorted.iloc[-1]["ReZ"])   # highest freq
    # Use the most common cycle number as the timestamp
    eis_cycle = float(df["cycle"].mode().iloc[0]) if not df["cycle"].dropna().empty else float("nan")
    return r_ohmic, r_diff, eis_cycle


_CAP_CACHE = {}


def _load_capacity_per_cycle(path: Path):
    """Cache per-cycle max capacity for the whole file."""
    if str(path) in _CAP_CACHE:
        return _CAP_CACHE[str(path)]
    try:
        df = pd.read_csv(path, sep="\t", engine="python", header=0)
        df.columns = [c.strip() for c in df.columns]
    except Exception as e:
        print(f"  [cap parse fail] {path.name}: {e}")
        return None
    cap_col = next((c for c in df.columns if "Capacity" in c or "capacity" in c), None)
    cyc_col = next((c for c in df.columns if "cycle" in c.lower()), None)
    if cap_col is None or cyc_col is None:
        return None
    # Per-cycle Q_max = max capacity reached during that cycle
    per_cycle = df.groupby(cyc_col)[cap_col].max().reset_index()
    per_cycle.columns = ["cycle", "Q_max"]
    _CAP_CACHE[str(path)] = per_cycle
    return per_cycle


def extract_capacity_at_cycle(path: Path, target_cycle: float):
    """Q_max at the cycle closest to target_cycle, from per-cycle aggregation."""
    per_cycle = _load_capacity_per_cycle(path)
    if per_cycle is None or per_cycle.empty:
        return float("nan")
    if np.isnan(target_cycle):
        return float(per_cycle["Q_max"].iloc[-1])
    nearest_idx = (per_cycle["cycle"] - target_cycle).abs().idxmin()
    return float(per_cycle.loc[nearest_idx, "Q_max"])


def main():
    cell_ids = []
    eis_files = sorted((BASE / "EIS data").glob("EIS_state_*.txt"))
    for f in eis_files:
        m = re.match(r"^EIS_state_([IVX]+)_(\d{2}C\d{2})\.txt$", f.name)
        if m and m.group(2) not in cell_ids:
            cell_ids.append(m.group(2))
    cell_ids.sort()
    print(f"Cells found: {len(cell_ids)} = {cell_ids}\n")

    rows = []
    for cell in cell_ids:
        cap_path = BASE / "Capacity data" / f"Data_Capacity_{cell}.txt"
        if not cap_path.exists():
            print(f"[warn] no capacity file for {cell}")
            continue
        for state in STATES:
            eis_path = BASE / "EIS data" / f"EIS_state_{state}_{cell}.txt"
            if not eis_path.exists():
                continue
            r_ohmic, r_diff, eis_cycle = extract_eis_features(eis_path)
            q = extract_capacity_at_cycle(cap_path, eis_cycle)
            rows.append({
                "cell_id": cell,
                "state": state,
                "state_idx": STATES.index(state) + 1,
                "eis_cycle": eis_cycle,
                "Q_max": q,
                "R_ohmic": r_ohmic,
                "R_diff": r_diff,
                "temperature": int(cell[:2]),
            })
    df = pd.DataFrame(rows)
    print(f"Extracted {len(df)} (cell, state) rows")
    print("\nPer-cell state coverage:")
    print(df.groupby("cell_id")["state"].agg(list).to_string())

    print("\nQ_max trajectory per cell (across states I-IX):")
    pivot = df.pivot(index="state_idx", columns="cell_id", values="Q_max")
    print(pivot.to_string(float_format=lambda x: f"{x:.3f}" if pd.notna(x) else "    -"))

    # Restrict to 25°C cohort for pre-reg primary
    df25 = df[df["temperature"] == 25].dropna(subset=["Q_max", "R_ohmic", "R_diff"]).copy()
    print(f"\n25C cohort: {df25['cell_id'].nunique()} cells, {len(df25)} (cell, state) rows")

    operators = ["Q_max", "R_ohmic", "R_diff"]
    # Per-cell standardization on state I = fresh reference
    cell_stats = {}
    z_rows = []
    fresh_pool = []
    for cell, group in df25.groupby("cell_id"):
        group = group.sort_values("state_idx").reset_index(drop=True)
        fresh = group[group["state_idx"] == 1]
        if fresh.empty:
            continue
        cell_stats[cell] = fresh[operators].values[0]

    if not cell_stats:
        print("[abort] no fresh state-I references")
        return

    fresh_stack = np.vstack(list(cell_stats.values()))
    pooled_sd = fresh_stack.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    print(f"\nPooled state-I SD across {len(cell_stats)} cells:")
    for k, op in enumerate(operators):
        print(f"  {op}: {pooled_sd[k]:.4f}")

    for cell, group in df25.groupby("cell_id"):
        if cell not in cell_stats:
            continue
        group = group.sort_values("state_idx").reset_index(drop=True)
        mu = cell_stats[cell]
        z = (group[operators].values - mu) / pooled_sd
        zdf = group[["cell_id", "state", "state_idx"]].reset_index(drop=True)
        for k, op in enumerate(operators):
            zdf[f"z_{op}"] = z[:, k]
        z_rows.append(zdf)
    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]

    # Pooled cov from state-I observations (after per-cell mean-centering)
    fresh_z = z_all[z_all["state_idx"] == 1][z_cols].values
    pooled_cov = np.cov(fresh_z.T, ddof=1) + 1e-3 * np.eye(3)
    cov_inv = np.linalg.inv(pooled_cov)
    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold (99th pct chi^2(3)): {thr:.2f}")
    print("\n=== Mahalanobis trajectory per cell (25C, state I-IX) ===")
    pivot_d = z_all.pivot(index="state_idx", columns="cell_id", values="m_dist")
    print(pivot_d.to_string(float_format=lambda x: f"{x:6.2f}" if pd.notna(x) else "    -"))

    # Classifier
    print("\n=== Phase 4 classifier on Zhang 25C cohort ===")
    classifications = []
    for cell, group in z_all.groupby("cell_id"):
        group = group.sort_values("state_idx").reset_index(drop=True)
        flagged = group[group["m_dist"] > thr]
        if flagged.empty:
            classifications.append({"cell": cell, "n_flagged": 0, "class": "unflagged",
                                    "confidence": 0.0, "s_LLI": np.nan, "s_LAM_SEI": np.nan})
            continue
        z = flagged[z_cols].values
        norms = np.linalg.norm(z, axis=1, keepdims=True)
        u = z / np.where(norms < 1e-12, 1e-12, norms)
        u_med = np.median(u, axis=0)
        u_med = u_med / max(np.linalg.norm(u_med), 1e-12)
        s_l = float(np.dot(u_med, U_LLI))
        s_a = float(np.dot(u_med, U_LAM_SEI))
        conf = abs(s_l - s_a)
        cls = "unclassified" if conf < CONF else ("LLI" if s_l > s_a else "LAM+SEI")
        classifications.append({"cell": cell, "n_flagged": int(len(flagged)), "class": cls,
                                "confidence": conf, "s_LLI": s_l, "s_LAM_SEI": s_a})

    cdf = pd.DataFrame(classifications)
    print(cdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    n_cells = len(cdf)
    n_conf = (cdf["confidence"] >= CONF).sum()
    n_lam = (cdf["class"] == "LAM+SEI").sum()
    n_lli = (cdf["class"] == "LLI").sum()
    print(f"\n=== Pre-reg falsification (Zhang Cambridge 25C, N={n_cells}) ===")
    print(f"  Confidently classified: {n_conf}/{n_cells} ({n_conf/n_cells*100:.1f}%)  pre-reg req >=50%")
    if n_conf > 0:
        print(f"  LAM+SEI: {n_lam}/{n_conf} ({n_lam/n_conf*100:.1f}%)  (NOTE: pre-reg 70% threshold was for NMC; Zhang is LCO/graphite)")
        print(f"  LLI:     {n_lli}/{n_conf} ({n_lli/n_conf*100:.1f}%)")

    rng = np.random.default_rng(seed=42)
    null_n_confident = np.array([
        int((rng.permutation(cdf["confidence"].values) >= CONF).sum())
        for _ in range(10000)
    ])
    perm_p = float((null_n_confident >= n_conf).mean())
    print(f"  Permutation null (10000 shuffles of confidence): p = {perm_p:.4f}")
    print(f"  Bonferroni threshold for 3 replication cohorts: alpha/3 = 0.0167")

    cdf.to_parquet(OUT_DIR / "zhang_cambridge_classification.parquet")
    print(f"\nWritten: {OUT_DIR / 'zhang_cambridge_classification.parquet'}")


if __name__ == "__main__":
    main()
