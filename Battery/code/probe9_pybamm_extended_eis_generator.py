"""Probe 9 — Extended-frequency EIS generator (sub-mHz lane).

EXTENDS probe7v2_pybamm_b5_generator.py with sub-mHz EIS at both fresh
and B5'-aged states. Freq grid extended from logspace(-2, 5, 30) to
logspace(-3, 5, 33), enabling extraction of R_diff at 10 mHz (existing)
AND 1 mHz (new) from a single EIS solve per state.

Same L9 design + per-cell seeds as modal_pybamm_c3.py and probe7v2.
Cycling outputs bit-identical to v1/v2. EIS-state inputs (SEI thickness
+ negative porosity at the SOH 0.92 anchor cycle) bit-identical to v2.

New output columns (in addition to v2):
- R_diff_fresh_1mHz       (NEW: 1 mHz sub-mHz operator, fresh state)
- R_diff_aged_b5_1mHz     (NEW: 1 mHz sub-mHz operator, B5' aged state)

Existing v2 columns preserved verbatim including R_diff_fresh and
R_diff_aged_b5 which are now both extracted from the same extended-grid
EIS solve as 10 mHz reference points.

Per pre-reg lit/52 §2: R_ohmic = Re[Z(100 kHz)]; R_diff_<freq> =
Re[Z(<freq>)] - R_ohmic. v3 parquet output preserves v2 alongside.

Local multiprocessing 16-wide. ~80-120s wall expected on 108 cells
(slight slowdown vs v2 from 30->33 freq points + adding 1 mHz/0.1 mHz
to the steady-state solve which the linear EIS solver handles cheaply).

Run: python code/probe9_pybamm_extended_eis_generator.py
"""

import json
import os
import sys
import time
import traceback
from multiprocessing import Pool, set_start_method

import numpy as np

L9_DESIGN = [
    (0, 0, 0), (0, 1, 1), (0, 2, 2),
    (1, 0, 1), (1, 1, 2), (1, 2, 0),
    (2, 0, 2), (2, 1, 0), (2, 2, 1),
]
THICKNESS_MULT = [0.80, 1.00, 1.20]
TRANSFERENCE_ABS = [0.20, 0.2594, 0.32]
PARTICLE_RADIUS_ABS_M = [4.0e-6, 5.22e-6, 6.5e-6]

CELLS_PER_CONDITION = 12
MAX_CYCLES = 800
N_WORKERS = 16

# Extended grid: 1 mHz -> 100 kHz, 33 log-spaced points (pre-reg §2).
EIS_FREQS = np.logspace(-3, 5, 33)

# Target frequencies for R_diff extraction. Tolerance: nearest log-index.
F_OHMIC_HZ = 1.0e5
F_DIFF_10MHZ = 1.0e-2
F_DIFF_1MHZ = 1.0e-3

OUT_PARQUET = "D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet"


def _build_param_values(cond_idx, cell_idx):
    """Bit-identical to modal_pybamm_c3.make_param_values + v2 generator."""
    import pybamm
    pv = pybamm.ParameterValues("Chen2020")
    th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
    nominal_pos_thick = pv["Positive electrode thickness [m]"]
    pv["Positive electrode thickness [m]"] = nominal_pos_thick * THICKNESS_MULT[th_lvl]
    pv["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
    pv["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
    seed = 1000 + cond_idx * 100 + cell_idx
    rng = np.random.default_rng(seed)
    eps_pos = float(rng.normal(0, 0.02))
    eps_neg = float(rng.normal(0, 0.02))
    nom_pos_amvf = pv["Positive electrode active material volume fraction"]
    nom_neg_amvf = pv["Negative electrode active material volume fraction"]
    pv["Positive electrode active material volume fraction"] = nom_pos_amvf * (1 + eps_pos)
    pv["Negative electrode active material volume fraction"] = nom_neg_amvf * (1 + eps_neg)
    return pv, eps_pos, eps_neg, nom_pos_amvf, nom_neg_amvf


def _eis_extract_extended(pv, eis_options):
    """Solve EIS on the extended grid; return (R_ohmic, R_diff_10mHz, R_diff_1mHz).

    R_ohmic   = Re[Z] at f closest to 100 kHz (high-f limit; equals Z.real[-1] for the
                pre-reg grid since 100 kHz is the upper endpoint).
    R_diff_<freq> = Re[Z(<freq>)] - R_ohmic, with <freq> snapped to the nearest grid point.
    """
    import pybamm
    model = pybamm.lithium_ion.DFN(options=eis_options)
    eis = pybamm.EISSimulation(model, parameter_values=pv)
    sol = eis.solve(EIS_FREQS)
    Z = np.asarray(sol.impedance)
    # EIS_FREQS is monotone increasing in log; map by nearest grid point in log-space.
    log_freqs = np.log10(EIS_FREQS)
    idx_ohmic = int(np.argmin(np.abs(log_freqs - np.log10(F_OHMIC_HZ))))
    idx_10mHz = int(np.argmin(np.abs(log_freqs - np.log10(F_DIFF_10MHZ))))
    idx_1mHz = int(np.argmin(np.abs(log_freqs - np.log10(F_DIFF_1MHZ))))
    R_ohmic = float(Z.real[idx_ohmic])
    R_diff_10mHz = float(Z.real[idx_10mHz] - R_ohmic)
    R_diff_1mHz = float(Z.real[idx_1mHz] - R_ohmic)
    return R_ohmic, R_diff_10mHz, R_diff_1mHz


def _find_anchor_index(rpts, fresh_Q, target_soh=0.92):
    post = [r for r in rpts if r["cycle"] > 25]
    if not post:
        return None, True
    target_Q = target_soh * fresh_Q
    best = min(post, key=lambda r: abs(r["Q_max"] - target_Q))
    soh = best["Q_max"] / fresh_Q
    partial = abs(soh - target_soh) > 0.02
    return best, partial


def simulate_cell(args):
    """Cycling + fresh EIS + B5' aged EIS, all with extended freq grid."""
    cond_idx, cell_idx = args
    try:
        import pybamm
        import numpy as _np
    except Exception as e:
        return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                "error": f"import failed: {type(e).__name__}: {e}"}

    try:
        pv_fresh, eps_pos, eps_neg, nom_pos_amvf, nom_neg_amvf = _build_param_values(cond_idx, cell_idx)

        eis_options = {
            "surface form": "differential",
            "SEI": "ec reaction limited",
            "SEI porosity change": "true",
        }
        cycle_options = {"SEI": "ec reaction limited", "SEI porosity change": "true"}

        # Fresh EIS (extended grid)
        try:
            R_ohmic_fresh, R_diff_fresh_10mHz, R_diff_fresh_1mHz = _eis_extract_extended(pv_fresh, eis_options)
        except Exception as ex:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"fresh EIS failed: {type(ex).__name__}: {str(ex)[:200]}"}

        # Cycling sim with FULL aging-state output (bit-identical to v2)
        model_cycle = pybamm.lithium_ion.DFN(options=cycle_options)
        cycle_step = (
            "Discharge at 1C until 2.5 V",
            "Rest for 5 minutes",
            "Charge at 1C until 4.2 V",
            "Hold at 4.2 V until 50 mA",
            "Rest for 30 minutes",
        )
        experiment = pybamm.Experiment([cycle_step] * MAX_CYCLES,
                                       termination="80% capacity")
        try:
            solver = pybamm.IDAKLUSolver()
        except Exception:
            solver = pybamm.CasadiSolver(mode="safe")

        sim = pybamm.Simulation(model_cycle, parameter_values=pv_fresh,
                                experiment=experiment, solver=solver)
        sol = sim.solve(initial_soc=1.0)

        rpts = []
        n_cycles = len(sol.cycles) if sol.cycles is not None else 0
        for k in range(n_cycles):
            cyc = sol.cycles[k]
            if cyc is None:
                continue
            try:
                disch = cyc.steps[0]
                t = disch["Time [s]"].entries
                V = disch["Terminal voltage [V]"].entries
                I = disch["Current [A]"].entries
                if len(t) < 3:
                    continue
                trap = getattr(_np, "trapezoid", None) or _np.trapz
                Q_max = float(_np.abs(trap(I, t)) / 3600.0)
                if Q_max < 0.1:
                    continue
                I_disch = float(_np.median(_np.abs(I)))
                V_open = float(V[0])
                if k > 0 and sol.cycles[k-1] is not None:
                    prev = sol.cycles[k-1]
                    if hasattr(prev, "steps") and len(prev.steps) > 0:
                        try:
                            V_open = float(prev.steps[-1]["Terminal voltage [V]"].entries[-1])
                        except Exception:
                            pass
                idx_30 = int(_np.argmin(_np.abs(t - t[0] - 30.0)))
                V30 = float(V[idx_30])
                t_end = t[-1] - t[0]
                if t_end > 1800.0:
                    idx_long = int(_np.argmin(_np.abs(t - t[0] - 1800.0)))
                    V_long = float(V[idx_long])
                else:
                    V_long = float(V[-1])
                R_DC = (V_open - V30) / I_disch
                R_total = (V_open - V_long) / I_disch
                rpts.append({"cycle": k + 1, "Q_max": Q_max, "R_DC": R_DC, "R_total": R_total})
            except Exception:
                continue

        if len(rpts) < 6:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(rpts)} valid RPTs",
                    "R_ohmic_fresh": R_ohmic_fresh,
                    "R_diff_fresh_10mHz": R_diff_fresh_10mHz,
                    "R_diff_fresh_1mHz": R_diff_fresh_1mHz}

        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(fresh_rpts)} fresh-window RPTs",
                    "R_ohmic_fresh": R_ohmic_fresh,
                    "R_diff_fresh_10mHz": R_diff_fresh_10mHz,
                    "R_diff_fresh_1mHz": R_diff_fresh_1mHz}
        fresh_Q = float(_np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(_np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(_np.mean([r["R_total"] for r in fresh_rpts]))

        post = [r for r in rpts if r["cycle"] > 25]
        if not post:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": "no post-fresh cycles",
                    "R_ohmic_fresh": R_ohmic_fresh,
                    "R_diff_fresh_10mHz": R_diff_fresh_10mHz,
                    "R_diff_fresh_1mHz": R_diff_fresh_1mHz}
        crossed = [r for r in post if r["Q_max"] <= 0.80 * fresh_Q]
        partial = False
        if crossed:
            aged = crossed[0]
        else:
            aged = min(post, key=lambda r: r["Q_max"])
            partial = True
        aged_Q = aged["Q_max"]
        aged_R_DC = aged["R_DC"]
        aged_R_total = aged["R_total"]
        aged_cycle = aged["cycle"]
        aged_SOH = aged_Q / fresh_Q

        anchor_rpt, anchor_partial = _find_anchor_index(rpts, fresh_Q, 0.92)
        anchor_aged_Q = anchor_rpt["Q_max"] if anchor_rpt else float("nan")
        anchor_aged_SOH = anchor_aged_Q / fresh_Q if anchor_rpt else float("nan")
        anchor_aged_cycle = anchor_rpt["cycle"] if anchor_rpt else -1

        # B5' aged EIS: read SEI thickness + porosity at anchor cycle (v2 logic).
        sei_neg_aged = float("nan")
        neg_porosity_aged = float("nan")
        b5_state_err = None
        if anchor_rpt and sol.cycles is not None and 0 < anchor_aged_cycle <= len(sol.cycles):
            anchor_cyc = sol.cycles[anchor_aged_cycle - 1]
            if anchor_cyc is not None:
                try:
                    sei_arr = anchor_cyc["X-averaged negative SEI thickness [m]"].entries
                    if len(sei_arr):
                        sei_neg_aged = float(sei_arr[-1])
                except Exception as ex:
                    b5_state_err = f"SEI read: {type(ex).__name__}: {str(ex)[:120]}"
                try:
                    por_arr = anchor_cyc["X-averaged negative electrode porosity"].entries
                    if len(por_arr):
                        neg_porosity_aged = float(por_arr[-1])
                except Exception as ex:
                    if b5_state_err is None:
                        b5_state_err = f"Porosity read: {type(ex).__name__}: {str(ex)[:120]}"

        if not _np.isnan(sei_neg_aged) and not _np.isnan(neg_porosity_aged):
            pv_b5 = pybamm.ParameterValues("Chen2020")
            th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
            pv_b5["Positive electrode thickness [m]"] = pv_b5["Positive electrode thickness [m]"] * THICKNESS_MULT[th_lvl]
            pv_b5["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
            pv_b5["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
            pv_b5["Positive electrode active material volume fraction"] = nom_pos_amvf * (1 + eps_pos)
            pv_b5["Negative electrode active material volume fraction"] = nom_neg_amvf * (1 + eps_neg)
            pv_b5["Initial SEI thickness [m]"] = sei_neg_aged
            pv_b5["Negative electrode porosity"] = neg_porosity_aged
            try:
                R_ohmic_aged_b5, R_diff_aged_b5_10mHz, R_diff_aged_b5_1mHz = _eis_extract_extended(pv_b5, eis_options)
                b5_eis_err = None
            except Exception as ex:
                R_ohmic_aged_b5 = float("nan")
                R_diff_aged_b5_10mHz = float("nan")
                R_diff_aged_b5_1mHz = float("nan")
                b5_eis_err = f"{type(ex).__name__}: {str(ex)[:120]}"
        else:
            R_ohmic_aged_b5 = float("nan")
            R_diff_aged_b5_10mHz = float("nan")
            R_diff_aged_b5_1mHz = float("nan")
            b5_eis_err = "B5' state vars unavailable (NaN SEI or porosity)"

        th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
        return {
            "cond_idx": cond_idx,
            "cell_idx": cell_idx,
            "thickness_level": ["low", "mid", "high"][th_lvl],
            "transference_level": ["low", "mid", "high"][tn_lvl],
            "particle_radius_level": ["low", "mid", "high"][pr_lvl],
            "eps_pos_amvf": eps_pos,
            "eps_neg_amvf": eps_neg,
            "n_rpts": len(rpts),
            "fresh_Q": fresh_Q,
            "fresh_R_DC": fresh_R_DC,
            "fresh_R_total": fresh_R_total,
            "aged_Q": aged_Q,
            "aged_R_DC": aged_R_DC,
            "aged_R_total": aged_R_total,
            "aged_cycle": aged_cycle,
            "aged_SOH": aged_SOH,
            "partial_aging": partial,
            "anchor_aged_Q": anchor_aged_Q,
            "anchor_aged_SOH": anchor_aged_SOH,
            "anchor_aged_cycle": anchor_aged_cycle,
            "anchor_partial": anchor_partial if anchor_rpt else True,
            # Fresh EIS (extended grid)
            "R_ohmic_fresh": R_ohmic_fresh,
            "R_diff_fresh": R_diff_fresh_10mHz,        # v2-named alias = 10 mHz
            "R_diff_fresh_10mHz": R_diff_fresh_10mHz,
            "R_diff_fresh_1mHz": R_diff_fresh_1mHz,    # NEW
            # B5' aged EIS (extended grid)
            "R_ohmic_aged_b5": R_ohmic_aged_b5,
            "R_diff_aged_b5": R_diff_aged_b5_10mHz,    # v2-named alias = 10 mHz
            "R_diff_aged_b5_10mHz": R_diff_aged_b5_10mHz,
            "R_diff_aged_b5_1mHz": R_diff_aged_b5_1mHz,  # NEW
            "sei_neg_aged_m": sei_neg_aged,
            "neg_porosity_aged": neg_porosity_aged,
            "b5_eis_error": b5_eis_err,
            "b5_state_error": b5_state_err,
            "rpts_json": json.dumps(rpts),
            "error": None,
        }
    except Exception as e:
        return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                "error": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:1500]}


def main(n_cells_override=None):
    import pandas as pd
    tasks = [(c, i) for c in range(9) for i in range(CELLS_PER_CONDITION)]
    if n_cells_override is not None:
        tasks = tasks[:n_cells_override]
    print(f"=== Probe 9 PyBaMM extended-EIS generator: {len(tasks)} cells, {N_WORKERS}-wide ===")
    print(f"   Freq grid: 1 mHz -> 100 kHz, {len(EIS_FREQS)} points")
    print(f"   Output: {OUT_PARQUET}")
    t0 = time.time()
    with Pool(processes=N_WORKERS) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(simulate_cell, tasks, chunksize=1)):
            results.append(r)
            elapsed = time.time() - t0
            status = "OK" if r.get("error") is None else f"ERR: {r['error'][:60]}"
            print(f"  [{i+1}/{len(tasks)}] cond={r.get('cond_idx')} cell={r.get('cell_idx')} "
                  f"({elapsed:.0f}s) {status}", flush=True)
    df = pd.DataFrame(results)
    n_err = df["error"].notna().sum()
    n_ok = (df["error"].isna()).sum()
    print(f"\n=== Summary ({time.time()-t0:.0f}s wall) ===")
    print(f"  Successful: {n_ok}")
    print(f"  Failed:     {n_err}")
    if n_err > 0:
        print("\n  First 5 errors:")
        for _, r in df[df["error"].notna()].head(5).iterrows():
            print(f"    cond={r['cond_idx']} cell={r['cell_idx']}: {r['error']}")
    os.makedirs(os.path.dirname(OUT_PARQUET), exist_ok=True)
    df.to_parquet(OUT_PARQUET)
    print(f"\nWritten: {OUT_PARQUET}")


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            set_start_method("spawn", force=True)
        except RuntimeError:
            pass
    n_cells = None
    if len(sys.argv) > 1:
        n_cells = int(sys.argv[1])
    main(n_cells_override=n_cells)
