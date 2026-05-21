"""
Phase 4 v2 — Zhang Cambridge cohort with correct time-alignment.

Discovery: each "state" file is 261 EIS sweeps over 42 days at a fixed
SOC/protocol, NOT 9 discrete aging timepoints. Cycle_number within EIS
file = sweep index, not cell-aging cycle.

Use state V (canonical mid-SOC for the 9-state SOC sweep).
Per EIS sweep: extract R_ohmic + R_diff + sweep start time.
Look up Q_max in capacity file via time alignment.

Result is a (cell, sweep, cell_cycle, Q_max, R_ohmic, R_diff) table with
~260 observations per cell, spanning the cell's full aging trajectory.

Pre-registered classifier protocol applies as before (cosine similarity
to LLI / LAM+SEI centroids).
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd
from scipy import stats


BASE = Path("D:/Renewables/Battery/data/zhang_cambridge")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
CANONICAL_STATE = "V"  # mid of 9 SOC states

U_LLI = np.array([-1.0, 0.0, 0.0])
U_LLI = U_LLI / np.linalg.norm(U_LLI)
U_LAM_SEI = np.array([-1.0, +1.0, +1.0])
U_LAM_SEI = U_LAM_SEI / np.linalg.norm(U_LAM_SEI)
CONF = 0.3


def parse_capacity_file(path: Path):
    """Return per-cycle Q_max DataFrame.
    Handles 4-col (time, cycle, oxred, cap) AND 6-col (time, cycle, oxred, Ewe, I, cap) layouts.
    Use tab delimiter (NOT whitespace) because column headers contain spaces e.g. 'cycle number'."""
    df = pd.read_csv(path, sep="\t", engine="python", header=0)
    df.columns = [c.strip().lower() for c in df.columns]
    # Drop empty trailing unnamed columns
    df = df.loc[:, ~df.columns.str.startswith("unnamed")]
    # Identify columns by name fragments
    time_col = next((c for c in df.columns if c.startswith("time")), None)
    cap_col = next((c for c in df.columns if "capacity" in c), None)
    cyc_col = next((c for c in df.columns if c == "cycle" or "cycle" in c and "number" in c), None)
    if cyc_col is None:
        # Sometimes the cycle header is munged; find column with integer-like discrete values
        for c in df.columns:
            try:
                vals = pd.to_numeric(df[c], errors="coerce").dropna()
                if vals.nunique() > 1 and vals.nunique() < 1000 and (vals == vals.astype(int)).all():
                    cyc_col = c
                    break
            except Exception:
                continue
    if time_col is None or cap_col is None or cyc_col is None:
        raise ValueError(f"could not identify columns in {path.name}: {df.columns.tolist()}")
    df = df[[time_col, cyc_col, cap_col]].rename(
        columns={time_col: "time_s", cyc_col: "cycle", cap_col: "cap"}
    )
    df["time_s"] = pd.to_numeric(df["time_s"], errors="coerce")
    df["cycle"] = pd.to_numeric(df["cycle"], errors="coerce")
    df["cap"] = pd.to_numeric(df["cap"], errors="coerce")
    df = df.dropna()
    per_cycle = df.groupby("cycle").agg(
        q_max=("cap", "max"),
        cycle_start_time=("time_s", "min"),
        cycle_end_time=("time_s", "max"),
    ).reset_index()
    return per_cycle


def parse_eis_sweeps(path: Path):
    """Return per-sweep summary with R_ohmic, R_diff, sweep_time."""
    df = pd.read_csv(path, sep="\t", engine="python", header=0)
    df.columns = [c.strip() for c in df.columns]
    fcol = next((c for c in df.columns if "freq" in c.lower() or "Hz" in c), None)
    rcol = next((c for c in df.columns if c.startswith("Re(Z)") or "Re(Z)" in c), None)
    cyc_col = next((c for c in df.columns if "cycle" in c.lower()), None)
    tcol = next((c for c in df.columns if "time" in c.lower()), None)
    if not all([fcol, rcol, cyc_col, tcol]):
        return None
    df = df[[fcol, rcol, cyc_col, tcol]].rename(
        columns={fcol: "freq", rcol: "ReZ", cyc_col: "sweep", tcol: "time_s"}
    )
    # Per sweep: take highest-freq Re_Z (R_ohmic), lowest-freq Re_Z (R_diff), start time
    sweeps = []
    for sweep_id, g in df.groupby("sweep"):
        g_sorted = g.sort_values("freq")
        r_diff = float(g_sorted.iloc[0]["ReZ"])
        r_ohmic = float(g_sorted.iloc[-1]["ReZ"])
        t_sweep = float(g["time_s"].min())
        sweeps.append({"sweep": int(sweep_id), "time_s": t_sweep,
                       "R_ohmic": r_ohmic, "R_diff": r_diff})
    return pd.DataFrame(sweeps).sort_values("sweep").reset_index(drop=True)


def align_capacity(sweeps_df, per_cycle):
    """For each sweep, find Q_max at the cell-cycle the sweep was taken."""
    rows = []
    for _, sw in sweeps_df.iterrows():
        t = sw["time_s"]
        # Cycle whose time window contains this sweep's start time
        match = per_cycle[(per_cycle["cycle_start_time"] <= t) & (per_cycle["cycle_end_time"] >= t)]
        if len(match) == 0:
            # nearest cycle
            idx = (per_cycle["cycle_start_time"] - t).abs().idxmin()
            match = per_cycle.iloc[[idx]]
        cyc = float(match["cycle"].iloc[0])
        q = float(match["q_max"].iloc[0])
        rows.append({"sweep": int(sw["sweep"]), "time_s": t,
                     "cell_cycle": cyc, "Q_max": q,
                     "R_ohmic": sw["R_ohmic"], "R_diff": sw["R_diff"]})
    return pd.DataFrame(rows)


def process_cell(cell_id):
    eis_path = BASE / "EIS data" / f"EIS_state_{CANONICAL_STATE}_{cell_id}.txt"
    cap_path = BASE / "Capacity data" / f"Data_Capacity_{cell_id}.txt"
    if not eis_path.exists() or not cap_path.exists():
        return None
    sweeps = parse_eis_sweeps(eis_path)
    if sweeps is None or sweeps.empty:
        return None
    per_cycle = parse_capacity_file(cap_path)
    aligned = align_capacity(sweeps, per_cycle)
    aligned["cell_id"] = cell_id
    return aligned


def run_classifier(df, fresh_n=3):
    operators = ["Q_max", "R_ohmic", "R_diff"]
    z_rows = []
    fresh_pool = []
    cell_stats = {}
    for cell, group in df.groupby("cell_id"):
        group = group.sort_values("sweep").reset_index(drop=True)
        fresh = group.head(fresh_n)
        if len(fresh) < 2:
            continue
        mu = fresh[operators].mean().values
        sd = fresh[operators].std(ddof=1).values
        sd = np.where(sd < 1e-12, 1e-12, sd)
        cell_stats[cell] = (mu, sd)
        z = (group[operators].values - mu) / sd
        zdf = group[["cell_id", "sweep", "cell_cycle"]].reset_index(drop=True)
        for k, op in enumerate(operators):
            zdf[f"z_{op}"] = z[:, k]
        z_rows.append(zdf)
        fresh_z = (fresh[operators].values - mu) / sd
        fresh_pool.append(fresh_z)
    z_all = pd.concat(z_rows, ignore_index=True)
    z_cols = [f"z_{op}" for op in operators]
    fresh_stack = np.vstack(fresh_pool)
    pooled_cov = np.cov(fresh_stack.T, ddof=1) + 1e-3 * np.eye(3)
    cov_inv = np.linalg.inv(pooled_cov)
    diag = np.sqrt(np.diag(pooled_cov))
    corr = pooled_cov / np.outer(diag, diag)
    print("\nPooled fresh-period correlation:")
    print(pd.DataFrame(corr, index=operators, columns=operators).to_string(float_format=lambda x: f"{x:+.3f}"))

    z_mat = z_all[z_cols].values
    d2 = np.einsum("ij,jk,ik->i", z_mat, cov_inv, z_mat)
    z_all["m_dist"] = np.sqrt(d2)

    fresh_mask_all = []
    for cell, group in z_all.groupby("cell_id"):
        idx = z_all.index[z_all["cell_id"] == cell][:fresh_n]
        fresh_mask_all.extend(idx.tolist())
    fresh_d2 = d2[fresh_mask_all]
    ks_p = stats.kstest(fresh_d2, "chi2", args=(3,)).pvalue if len(fresh_d2) > 1 else None
    print(f"\nPPC: fresh n={len(fresh_d2)}, mean d^2={np.mean(fresh_d2):.3f}, KS p={ks_p:.4f}" if ks_p else "")

    thr = np.sqrt(stats.chi2.ppf(0.99, df=3))
    print(f"\nThreshold: {thr:.2f}")

    classifications = []
    for cell, group in z_all.groupby("cell_id"):
        group = group.sort_values("sweep").reset_index(drop=True)
        flagged = group[group["m_dist"] > thr]
        if flagged.empty:
            cls = {"cell": cell, "n_flagged": 0, "class": "unflagged",
                   "confidence": 0.0, "s_LLI": np.nan, "s_LAM_SEI": np.nan,
                   "final_cycle": float(group["cell_cycle"].iloc[-1])}
            classifications.append(cls)
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
        classifications.append({
            "cell": cell, "n_flagged": int(len(flagged)), "class": cls,
            "confidence": conf, "s_LLI": s_l, "s_LAM_SEI": s_a,
            "final_cycle": float(group["cell_cycle"].iloc[-1]),
        })
    return z_all, pd.DataFrame(classifications)


def main():
    # Get 25C cells
    cells_25c = sorted(set(re.findall(r"25C\d+", " ".join(p.name for p in (BASE / "EIS data").glob("EIS_state_*.txt")))))
    print(f"Processing {len(cells_25c)} 25C cells via state {CANONICAL_STATE}")
    rows = []
    for cell in cells_25c:
        df = process_cell(cell)
        if df is not None:
            rows.append(df)
            print(f"  {cell}: {len(df)} sweeps, cycles {df['cell_cycle'].min():.0f}-{df['cell_cycle'].max():.0f}, Q_max fade {(1 - df['Q_max'].iloc[-1]/df['Q_max'].iloc[0])*100:.1f}%")
    df_all = pd.concat(rows, ignore_index=True)
    print(f"\nTotal observations: {len(df_all)} across {df_all['cell_id'].nunique()} cells")

    z_all, cdf = run_classifier(df_all)
    print("\n=== Classifier per cell ===")
    print(cdf.to_string(index=False, float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x)))

    # Verdict
    n_cells = len(cdf)
    n_conf = (cdf["confidence"] >= CONF).sum()
    n_lam = (cdf["class"] == "LAM+SEI").sum()
    n_lli = (cdf["class"] == "LLI").sum()
    print(f"\n=== Zhang Cambridge 25C v2 verdict ===")
    print(f"  Total cells: {n_cells}")
    print(f"  Confidently classified: {n_conf}/{n_cells} ({n_conf/n_cells*100:.1f}%)")
    print(f"  LAM+SEI: {n_lam}/{max(n_conf,1)} ({n_lam/max(n_conf,1)*100:.1f}%)")
    print(f"  LLI: {n_lli}/{max(n_conf,1)} ({n_lli/max(n_conf,1)*100:.1f}%)")

    rng = np.random.default_rng(seed=42)
    null_n = np.array([int((rng.permutation(cdf["confidence"].values) >= CONF).sum()) for _ in range(10000)])
    p = float((null_n >= n_conf).mean())
    print(f"  Permutation null p = {p:.4f} (Bonferroni threshold 0.0167)")

    df_all.to_parquet(OUT_DIR / "zhang_features_v2.parquet")
    cdf.to_parquet(OUT_DIR / "zhang_classification_v2.parquet")


if __name__ == "__main__":
    main()
