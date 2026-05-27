"""Probe 7 v2 — PyBaMM B5'-augmented L9 synthetic generator.

Same L9 design + per-cell seeds as code/modal_pybamm_c3.py (bit-identical
cycling outputs to v1). REPLACES the B7 LAM-proxy aged-state EIS with
B5': read actual aged-state vars (SEI thickness, negative porosity) from
the cycling solution at the uniform-anchor cycle (SOH 0.92), then run EIS
on a ParameterValues with those values baked in as initial state.

The B7 v1 modification (Q_loss-driven amvf reduction) was off-target -- the
PyBaMM cycling sim doesn't actually move amvf. The real aging in this model
is SEI growth + porosity collapse (lithium loss is captured via SEI).

Output columns (in addition to v1):
- R_ohmic_aged_b5, R_diff_aged_b5    (NEW: B5' aged EIS)
- sei_neg_aged_m                      (NEW: read-out X-avg negative SEI thickness)
- neg_porosity_aged                   (NEW: read-out X-avg negative porosity)
- (R_ohmic_aged, R_diff_aged from v1's B7 also kept for direct compare)

Local multiprocessing 16-wide. ~1-2 min wall on 108 cells.

Run: python code/probe7v2_pybamm_b5_generator.py
"""

import json
import os
import sys
import time
import traceback
from multiprocessing import Pool, set_start_method

import numpy as np

# L9 design (identical to modal_pybamm_c3.py)
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

EIS_FREQS = np.logspace(-2, 5, 30)

OUT_PARQUET = "D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v2.parquet"


def _build_param_values(cond_idx, cell_idx):
    """Matches modal_pybamm_c3.make_param_values exactly."""
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


def _eis_extract(pv, eis_options):
    """Build EISSimulation, solve, return (R_ohmic, R_diff)."""
    import pybamm
    model = pybamm.lithium_ion.DFN(options=eis_options)
    eis = pybamm.EISSimulation(model, parameter_values=pv)
    sol = eis.solve(EIS_FREQS)
    Z = np.asarray(sol.impedance)
    R_ohmic = float(Z.real[-1])  # f -> inf
    R_low = float(Z.real[0])      # f -> 0
    R_diff = R_low - R_ohmic
    return R_ohmic, R_diff


def _find_anchor_index(rpts, fresh_Q, target_soh=0.92):
    """Return (rpt_dict, anchor_partial) for the cycle closest to target_soh."""
    post = [r for r in rpts if r["cycle"] > 25]
    if not post:
        return None, True
    target_Q = target_soh * fresh_Q
    best = min(post, key=lambda r: abs(r["Q_max"] - target_Q))
    soh = best["Q_max"] / fresh_Q
    partial = abs(soh - target_soh) > 0.02
    return best, partial


def simulate_cell(args):
    """Run one cell: cycling + fresh EIS + B5' aged EIS (SEI+porosity from cycling state)."""
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

        # Fresh EIS
        try:
            R_ohmic_fresh, R_diff_fresh = _eis_extract(pv_fresh, eis_options)
        except Exception as ex:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"fresh EIS failed: {type(ex).__name__}: {str(ex)[:200]}"}

        # Cycling sim with FULL aging-state output
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

        # Per-cycle HPPC extraction (bit-identical to v1)
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
                    "R_ohmic_fresh": R_ohmic_fresh, "R_diff_fresh": R_diff_fresh}

        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(fresh_rpts)} fresh-window RPTs",
                    "R_ohmic_fresh": R_ohmic_fresh, "R_diff_fresh": R_diff_fresh}
        fresh_Q = float(_np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(_np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(_np.mean([r["R_total"] for r in fresh_rpts]))

        # Terminal aging anchor (per Probe 4 logic, bit-identical to v1)
        post = [r for r in rpts if r["cycle"] > 25]
        if not post:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx, "error": "no post-fresh cycles",
                    "R_ohmic_fresh": R_ohmic_fresh, "R_diff_fresh": R_diff_fresh}
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

        # Uniform anchor cycle (SOH 0.92, Probe 5 convention)
        anchor_rpt, anchor_partial = _find_anchor_index(rpts, fresh_Q, 0.92)
        anchor_aged_Q = anchor_rpt["Q_max"] if anchor_rpt else float("nan")
        anchor_aged_SOH = anchor_aged_Q / fresh_Q if anchor_rpt else float("nan")
        anchor_aged_cycle = anchor_rpt["cycle"] if anchor_rpt else -1

        # ===== B7 (v1) AGED EIS: LAM proxy =====
        Q_loss_frac_b7 = max(0.0, 1.0 - anchor_aged_Q / fresh_Q) if anchor_rpt else float("nan")
        pv_b7 = pybamm.ParameterValues("Chen2020")
        th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
        pv_b7["Positive electrode thickness [m]"] = pv_b7["Positive electrode thickness [m]"] * THICKNESS_MULT[th_lvl]
        pv_b7["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
        pv_b7["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
        if anchor_rpt:
            pv_b7["Positive electrode active material volume fraction"] = (
                nom_pos_amvf * (1 + eps_pos) * (1 - Q_loss_frac_b7)
            )
            pv_b7["Negative electrode active material volume fraction"] = (
                nom_neg_amvf * (1 + eps_neg) * (1 - Q_loss_frac_b7)
            )
        try:
            R_ohmic_aged_b7, R_diff_aged_b7 = _eis_extract(pv_b7, eis_options)
            b7_eis_err = None
        except Exception as ex:
            R_ohmic_aged_b7 = float("nan")
            R_diff_aged_b7 = float("nan")
            b7_eis_err = f"{type(ex).__name__}: {str(ex)[:120]}"

        # ===== B5' AGED EIS: read SEI thickness + porosity at ANCHOR CYCLE =====
        # Find the time index in the cycling solution corresponding to the anchor cycle
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
            pv_b5["Positive electrode thickness [m]"] = pv_b5["Positive electrode thickness [m]"] * THICKNESS_MULT[th_lvl]
            pv_b5["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
            pv_b5["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
            pv_b5["Positive electrode active material volume fraction"] = nom_pos_amvf * (1 + eps_pos)
            pv_b5["Negative electrode active material volume fraction"] = nom_neg_amvf * (1 + eps_neg)
            pv_b5["Initial SEI thickness [m]"] = sei_neg_aged
            pv_b5["Negative electrode porosity"] = neg_porosity_aged
            try:
                R_ohmic_aged_b5, R_diff_aged_b5 = _eis_extract(pv_b5, eis_options)
                b5_eis_err = None
            except Exception as ex:
                R_ohmic_aged_b5 = float("nan")
                R_diff_aged_b5 = float("nan")
                b5_eis_err = f"{type(ex).__name__}: {str(ex)[:120]}"
        else:
            R_ohmic_aged_b5 = float("nan")
            R_diff_aged_b5 = float("nan")
            b5_eis_err = "B5' state vars unavailable (NaN SEI or porosity)"

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
            "R_ohmic_fresh": R_ohmic_fresh,
            "R_diff_fresh": R_diff_fresh,
            # B7 (v1) aged EIS -- kept for direct comparison vs B5'
            "R_ohmic_aged_b7": R_ohmic_aged_b7,
            "R_diff_aged_b7": R_diff_aged_b7,
            "Q_loss_frac_b7": Q_loss_frac_b7,
            "b7_eis_error": b7_eis_err,
            # B5' aged EIS -- the v2 primary aged-state measurement
            "R_ohmic_aged_b5": R_ohmic_aged_b5,
            "R_diff_aged_b5": R_diff_aged_b5,
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
    print(f"=== Probe 7 v2 PyBaMM B5'+B7 EIS generator: {len(tasks)} cells, {N_WORKERS}-wide ===")
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
