"""
Paper 3 — Noise-resistant operator extraction (literature/36 §4, locked 3b9e1d6).

10 operators defined by mechanism (mapping to aging modes):

Capacity-based (LLI + LAM):
  1. N90: cycle count to first SOH <= 0.90
  2. N80: cycle count to first SOH <= 0.80
  3. N90_to_N80_ratio: N80 / N90 (kneeing detector)

IC-peak-based (LAM-NE / LAM-PE, per Birkl 2017):
  4. IC_peak_low_height: dQ/dV peak height in 3.5-3.7 V window at terminal cycle
  5. IC_peak_high_height: dQ/dV peak height in 4.0-4.2 V window at terminal cycle
  6. IC_peak_low_shift: voltage shift of low-SOC peak from cycle 5 to terminal

Resistance-based (kinetic-R):
  7. N_R_double: cycle count until R_DC doubles fresh value
  8. R_DC_fresh: R_DC at cycle 5 baseline

EIS-based (kinetic-R, where available):
  9. R_ohmic_fresh: Re-axis intercept at fresh (= E1 from Paper 2)
  10. R_charge_transfer_fresh: R_diff - R_ohmic at fresh

Extracts on synthetic + Khan + Severson + SECL first-life cohorts. NaN where
not extractable per cohort (IC requires dV/dQ curves; EIS requires impedance).

Output: paper3_operators_{cohort}.parquet for each cohort.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

PROCESSED = Path("D:/Renewables/Battery/data/processed")

OPERATORS = [
    "N90", "N80", "N90_to_N80_ratio",
    "IC_peak_low_height", "IC_peak_high_height", "IC_peak_low_shift",
    "N_R_double", "R_DC_fresh",
    "R_ohmic_fresh", "R_charge_transfer_fresh",
]


def _empty_row(cell_id, cohort):
    r = {"cell_id": cell_id, "cohort": cohort}
    for op in OPERATORS:
        r[op] = float("nan")
    return r


def _cycle_to_threshold(cycles, q, fresh_q, threshold):
    """Linear-interp cycle count where q first crosses threshold * fresh_q."""
    target = threshold * fresh_q
    finite = np.isfinite(cycles) & np.isfinite(q)
    if finite.sum() < 3:
        return float("nan")
    c = np.asarray(cycles)[finite]
    qv = np.asarray(q)[finite]
    # First idx where qv <= target
    below = np.where(qv <= target)[0]
    if len(below) == 0:
        return float("nan")  # never reaches threshold
    i = below[0]
    if i == 0:
        return float(c[0])
    # Linear interp between i-1 and i
    q0, q1 = qv[i-1], qv[i]
    c0, c1 = c[i-1], c[i]
    if q0 == q1:
        return float(c0)
    frac = (target - q0) / (q1 - q0)
    return float(c0 + frac * (c1 - c0))


def _ic_peak_height_in_window(voltage, dq_dv, v_lo, v_hi):
    """Max of dq_dv where voltage in [v_lo, v_hi]. NaN if no points in window."""
    v = np.asarray(voltage)
    d = np.asarray(dq_dv)
    mask = (v >= v_lo) & (v <= v_hi) & np.isfinite(v) & np.isfinite(d)
    if mask.sum() < 3:
        return float("nan")
    return float(np.max(d[mask]))


def _ic_peak_voltage_in_window(voltage, dq_dv, v_lo, v_hi):
    """Voltage at peak of dq_dv where voltage in [v_lo, v_hi]."""
    v = np.asarray(voltage)
    d = np.asarray(dq_dv)
    mask = (v >= v_lo) & (v <= v_hi) & np.isfinite(v) & np.isfinite(d)
    if mask.sum() < 3:
        return float("nan")
    v_in = v[mask]
    d_in = d[mask]
    return float(v_in[np.argmax(d_in)])


def extract_from_trajectory(rpts):
    """Extract the 10 operators from a per-cycle trajectory (list of dicts with
    cycle, Q_max, R_DC, R_total, and optionally V_OCV, dQ_dV)."""
    cycle = np.array([p["cycle"] for p in rpts], dtype=float)
    q = np.array([p["Q_max"] for p in rpts], dtype=float)
    r_dc = np.array([p.get("R_DC", float("nan")) for p in rpts], dtype=float)
    n = len(cycle)
    out = {op: float("nan") for op in OPERATORS}
    if n < 5:
        return out

    fresh_q = float(np.nanmean(q[:min(10, n)]))
    fresh_r_dc = float(np.nanmean(r_dc[:min(10, n)]))

    # Capacity-based
    out["N90"] = _cycle_to_threshold(cycle, q, fresh_q, 0.90)
    out["N80"] = _cycle_to_threshold(cycle, q, fresh_q, 0.80)
    if np.isfinite(out["N80"]) and np.isfinite(out["N90"]) and out["N90"] > 0:
        out["N90_to_N80_ratio"] = out["N80"] / out["N90"]

    # Resistance
    if np.isfinite(fresh_r_dc) and fresh_r_dc > 0:
        out["R_DC_fresh"] = fresh_r_dc
        # N_R_double: first cycle where R_DC >= 2 * fresh_r_dc
        above = np.where(r_dc >= 2 * fresh_r_dc)[0]
        if len(above):
            i = above[0]
            if i == 0:
                out["N_R_double"] = float(cycle[0])
            else:
                r0, r1 = r_dc[i-1], r_dc[i]
                c0, c1 = cycle[i-1], cycle[i]
                if r0 != r1:
                    frac = (2 * fresh_r_dc - r0) / (r1 - r0)
                    out["N_R_double"] = float(c0 + frac * (c1 - c0))

    # IC peaks: only if dQ_dV available
    if any("dQ_dV" in p and isinstance(p["dQ_dV"], list) for p in rpts):
        # Use cycle ~5 as fresh ref + terminal as aged
        fresh_idx = min(range(n), key=lambda i: abs(cycle[i] - 5))
        terminal_idx = n - 1
        for tag, idx in [("fresh", fresh_idx), ("terminal", terminal_idx)]:
            p = rpts[idx]
            if "dQ_dV" not in p or "V" not in p:
                continue
            volts = p["V"]
            dqdv = p["dQ_dV"]
            ph_low = _ic_peak_height_in_window(volts, dqdv, 3.5, 3.7)
            ph_high = _ic_peak_height_in_window(volts, dqdv, 4.0, 4.2)
            pv_low = _ic_peak_voltage_in_window(volts, dqdv, 3.5, 3.7)
            if tag == "terminal":
                out["IC_peak_low_height"] = ph_low
                out["IC_peak_high_height"] = ph_high
            if tag == "fresh" and np.isfinite(pv_low):
                fresh_v_low = pv_low
            elif tag == "terminal" and np.isfinite(pv_low):
                if "fresh_v_low" in dir():
                    out["IC_peak_low_shift"] = pv_low - fresh_v_low

    return out


# ---------- Cohort-specific extractors ----------

def extract_synthetic():
    """Extract operators on Paper 3 PyBaMM synthetic cells."""
    print("=== Paper 3 synthetic (PyBaMM) ===")
    p = PROCESSED / "paper3_pybamm_synthetic.parquet"
    if not p.exists():
        print(f"  WARN: {p} missing — run paper3_pybamm_generator.main first")
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df = df[df["error"].isna()].copy()
    rows = []
    for _, row in df.iterrows():
        rpts = json.loads(row["rpts_json"]) if isinstance(row["rpts_json"], str) else row["rpts_json"]
        if not rpts:
            continue
        r = _empty_row(f"PyBaMM_C{int(row['cell_idx'])}", "Paper3_synthetic")
        ops = extract_from_trajectory(rpts)
        r.update(ops)
        # Carry aging-mode labels through
        for label in ["LLI", "LAM_NE", "LAM_PE", "kinetic_R"]:
            r[label] = float(row.get(label, float("nan")))
        # Carry parameter axes for downstream
        for k in ["thickness_mult", "transference", "ne_particle_radius_log",
                  "pe_particle_radius_log", "sei_rate_log", "charge_C_rate",
                  "temperature_C", "aged_SOH", "n_rpts"]:
            r[k] = row.get(k, float("nan"))
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper3_operators_synthetic.parquet")
    print(f"  {len(out)} cells extracted. Non-NaN per op:")
    for op in OPERATORS:
        print(f"    {op}: {out[op].notna().sum()}/{len(out)}")
    return out


def extract_khan():
    """Khan: full per-cycle Q + R_DC + EIS. dV/dQ available from capacity files."""
    print("=== Khan 2025 ===")
    p = PROCESSED / "features_first_life.parquet"
    # Not Khan's parquet; Khan operator-level data is in paper2_operators_khan.parquet
    # plus raw capacity/EIS in data/khan_2025/
    # For Paper 3 we need to re-extract from raw capacity curves to get IC peaks.
    # Placeholder for now: read paper2 extraction and supplement what we can.
    paper2_khan = PROCESSED / "paper2_operators_khan.parquet"
    if not paper2_khan.exists():
        print(f"  WARN: {paper2_khan} missing")
        return pd.DataFrame()
    df = pd.read_parquet(paper2_khan)
    rows = []
    for _, row in df.iterrows():
        r = _empty_row(row["cell_id"], "Khan_2025")
        # Carry through what we have from Paper 2 extraction
        r["R_DC_fresh"] = float(row.get("E1_ohmic_intercept", float("nan")))
        r["R_ohmic_fresh"] = float(row.get("E1_ohmic_intercept", float("nan")))
        r["R_charge_transfer_fresh"] = float(row.get("E2_charge_transfer_radius", float("nan")))
        # Khan doesn't have full per-cycle trajectory in our parquet — needs re-extraction
        # from raw capacity files. For now leave N90/N80/IC peaks as NaN.
        # TODO: re-extract Khan from raw `data/khan_2025/capacity/*.csv` for full coverage
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper3_operators_khan.parquet")
    print(f"  {len(out)} cells extracted (limited to EIS-derived ops; full re-extraction TODO)")
    return out


def extract_severson():
    """Severson: BEEP-structured per-cycle Q + R_DC. No EIS. Per-cycle dQ/dV possible."""
    print("=== Severson ===")
    paper2_sev = PROCESSED / "paper2_operators_severson.parquet"
    if not paper2_sev.exists():
        print(f"  WARN: {paper2_sev} missing")
        return pd.DataFrame()
    # Severson per-cycle Q trajectory is needed for N90/N80. We'd need raw FastCharge.zip data.
    # For v1, use paper2 extraction outputs that proxy these.
    df = pd.read_parquet(paper2_sev)
    rows = []
    for _, row in df.iterrows():
        cell_id = f"Severson_{row.get('barcode', '?')}_ch{row.get('channel_id', '?')}"
        r = _empty_row(cell_id, "Severson")
        # T1/T2 from Paper 2 are slope-based; need to re-extract N90/N80 from raw BEEP
        # TODO: re-extract Severson from FastCharge.zip per-cycle Q trajectories
        r["R_DC_fresh"] = float(row.get("fresh_R", float("nan")))
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper3_operators_severson.parquet")
    print(f"  {len(out)} cells extracted (Severson re-extraction TODO for N90/N80)")
    return out


def extract_secl_first_life():
    """SECL first-life: longitudinal RPTs w/ EIS + HPPC."""
    print("=== SECL first-life ===")
    p = PROCESSED / "features_first_life.parquet"
    if not p.exists():
        print(f"  WARN: {p} missing")
        return pd.DataFrame()
    df = pd.read_parquet(p)
    rows = []
    for cell, g in df.groupby("cell_id"):
        g = g.sort_values("rpt_idx").reset_index(drop=True)
        # Reconstruct trajectory dict per cell (rpt_idx as cycle proxy)
        rpts = [{"cycle": int(rpt), "Q_max": float(q), "R_DC": float(r_dc)}
                for rpt, q, r_dc in zip(g["rpt_idx"].values,
                                        g["Q_max_Ah"].values,
                                        g.get("R_DC_ohm", pd.Series([float("nan")]*len(g))).values)]
        r = _empty_row(cell, "SECL_first_life")
        ops = extract_from_trajectory(rpts)
        r.update(ops)
        rows.append(r)
    out = pd.DataFrame(rows)
    out.to_parquet(PROCESSED / "paper3_operators_secl.parquet")
    print(f"  {len(out)} cells extracted")
    return out


def main():
    print("=== Paper 3 noise-resistant operator extraction ===\n")
    s = extract_synthetic()
    k = extract_khan()
    se = extract_severson()
    sc = extract_secl_first_life()
    print("\n=== Summary ===")
    print(f"  synthetic: {len(s)} cells")
    print(f"  khan:      {len(k)} cells")
    print(f"  severson:  {len(se)} cells")
    print(f"  secl:      {len(sc)} cells")


if __name__ == "__main__":
    main()
