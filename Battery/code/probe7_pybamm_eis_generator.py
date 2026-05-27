"""Probe 7 — PyBaMM EIS-augmented L9 synthetic generator.

Reproduces the Probe 5/6 cohort (same L9 design, same per-cell seeds as
modal_pybamm_c3.py) but adds EIS-derived R_ohmic and R_diff at fresh and
aged states.

EIS architecture (B7 in design log):
  - Fresh-state EIS: pybamm.EISSimulation on the cell's design-parameter
    ParameterValues at fresh state -> R_ohmic_fresh, R_diff_fresh.
  - Aged-state EIS: pybamm.EISSimulation on a MODIFIED ParameterValues
    where active material volume fractions are reduced by the per-cell
    cycling-derived Q-loss fraction (LAM proxy). True cycled-state EIS
    via time-domain AC injection is a Probe 7.1 follow-up.

Local multiprocessing 16-wide. ~35-70 min wall on 108 cells.

Run: python code/probe7_pybamm_eis_generator.py
"""

import json
import os
import sys
import time
import traceback
from multiprocessing import Pool, set_start_method

import numpy as np

# ---- L9 design (identical to modal_pybamm_c3.py) ----
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

# EIS frequency grid: 100 kHz -> 10 mHz, 30 points (log-spaced)
EIS_FREQS = np.logspace(-2, 5, 30)

OUT_PARQUET = "D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis.parquet"


def _build_param_values(cond_idx, cell_idx):
    """Per-cell ParameterValues. Matches modal_pybamm_c3.make_param_values exactly."""
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
    """Build EISSimulation on the given ParameterValues, solve, return (R_ohmic, R_diff)."""
    import pybamm
    model = pybamm.lithium_ion.DFN(options=eis_options)
    eis = pybamm.EISSimulation(model, parameter_values=pv)
    sol = eis.solve(EIS_FREQS)
    Z = np.asarray(sol.impedance)
    # EIS_FREQS[0] = 0.01 Hz (low), EIS_FREQS[-1] = 100 kHz (high)
    R_ohmic = float(Z.real[-1])
    R_low = float(Z.real[0])
    R_diff = R_low - R_ohmic
    return R_ohmic, R_diff


def simulate_cell(args):
    """Run one cell: cycling + fresh EIS + aged-proxy EIS. Returns result dict."""
    cond_idx, cell_idx = args
    try:
        import pybamm
        import numpy as _np  # local rebind inside worker
    except Exception as e:
        return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                "error": f"import failed: {type(e).__name__}: {e}"}

    try:
        # 1) Build fresh ParameterValues
        pv_fresh, eps_pos, eps_neg, nom_pos_amvf, nom_neg_amvf = _build_param_values(cond_idx, cell_idx)

        # 2) Fresh-state EIS (cheap, ~0.2s)
        eis_options = {
            "surface form": "differential",
            "SEI": "ec reaction limited",
            "SEI porosity change": "true",
        }
        try:
            R_ohmic_fresh, R_diff_fresh = _eis_extract(pv_fresh, eis_options)
        except Exception as ex:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"fresh EIS failed: {type(ex).__name__}: {str(ex)[:200]}"}

        # 3) Cycling sim (the slow part, ~5-10 min)
        # Use same model options as modal_pybamm_c3.py (no surface form needed for cycling)
        cycle_options = {"SEI": "ec reaction limited", "SEI porosity change": "true"}
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

        # 4) Extract per-cycle HPPC operators (Q_max, R_DC, R_total) -- matches modal_pybamm_c3
        rpts = []
        n_cycles = len(sol.cycles) if sol.cycles is not None else 0
        skipped = {"None": 0, "steps_err": 0, "t_short": 0, "Q_low": 0}
        for k in range(n_cycles):
            cyc = sol.cycles[k]
            if cyc is None:
                skipped["None"] += 1
                continue
            try:
                disch = cyc.steps[0]
                t = disch["Time [s]"].entries
                V = disch["Terminal voltage [V]"].entries
                I = disch["Current [A]"].entries
                if len(t) < 3:
                    skipped["t_short"] += 1
                    continue
                trap = getattr(_np, "trapezoid", None) or _np.trapz
                Q_max = float(_np.abs(trap(I, t)) / 3600.0)
                if Q_max < 0.1:
                    skipped["Q_low"] += 1
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
                skipped["steps_err"] += 1
                continue

        if len(rpts) < 6:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(rpts)} valid RPTs; skipped={skipped}",
                    "R_ohmic_fresh": R_ohmic_fresh, "R_diff_fresh": R_diff_fresh}

        # Fresh = cycles 5-25 mean
        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(fresh_rpts)} fresh-window RPTs",
                    "R_ohmic_fresh": R_ohmic_fresh, "R_diff_fresh": R_diff_fresh}
        fresh_Q = float(_np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(_np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(_np.mean([r["R_total"] for r in fresh_rpts]))

        # Aged = first crossing of 80% SOH after fresh window (matches Probe 4 logic)
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

        # 5) Aged-state EIS (B7 proxy): rebuild ParameterValues with active material
        #    fractions reduced proportional to per-cell Q-loss at the UNIFORM ANCHOR
        #    (SOH 0.92, matching Probe 5 convention -- not the cycling-sim terminal).
        target_soh_anchor = 0.92
        target_Q_anchor = target_soh_anchor * fresh_Q
        anchor_rpt = min(post, key=lambda r: abs(r["Q_max"] - target_Q_anchor))
        anchor_aged_Q = anchor_rpt["Q_max"]
        anchor_aged_SOH = anchor_aged_Q / fresh_Q
        anchor_aged_cycle = anchor_rpt["cycle"]
        anchor_partial = abs(anchor_aged_SOH - target_soh_anchor) > 0.02
        Q_loss_frac = max(0.0, 1.0 - anchor_aged_Q / fresh_Q)
        pv_aged = pybamm.ParameterValues("Chen2020")
        # Re-apply design parameters
        th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
        nominal_pos_thick = pv_aged["Positive electrode thickness [m]"]
        pv_aged["Positive electrode thickness [m]"] = nominal_pos_thick * THICKNESS_MULT[th_lvl]
        pv_aged["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
        pv_aged["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
        # Apply per-cell perturbation AND aging reduction
        # Aged active material = fresh perturbed value * (1 - Q_loss_frac)
        pv_aged["Positive electrode active material volume fraction"] = (
            nom_pos_amvf * (1 + eps_pos) * (1 - Q_loss_frac)
        )
        pv_aged["Negative electrode active material volume fraction"] = (
            nom_neg_amvf * (1 + eps_neg) * (1 - Q_loss_frac)
        )
        try:
            R_ohmic_aged, R_diff_aged = _eis_extract(pv_aged, eis_options)
        except Exception as ex:
            R_ohmic_aged = float("nan")
            R_diff_aged = float("nan")
            aged_eis_err = f"{type(ex).__name__}: {str(ex)[:120]}"
        else:
            aged_eis_err = None

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
            "R_ohmic_fresh": R_ohmic_fresh,
            "R_diff_fresh": R_diff_fresh,
            "R_ohmic_aged": R_ohmic_aged,
            "R_diff_aged": R_diff_aged,
            "anchor_aged_Q": anchor_aged_Q,
            "anchor_aged_SOH": anchor_aged_SOH,
            "anchor_aged_cycle": anchor_aged_cycle,
            "anchor_partial": anchor_partial,
            "Q_loss_frac_for_eis": Q_loss_frac,
            "aged_eis_error": aged_eis_err,
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
    print(f"=== Probe 7 PyBaMM EIS generator: {len(tasks)} cells, {N_WORKERS}-wide ===")
    print(f"   Output: {OUT_PARQUET}")
    t0 = time.time()
    with Pool(processes=N_WORKERS) as pool:
        # imap_unordered for live progress; chunk=1 so we see each completion
        results = []
        for i, r in enumerate(pool.imap_unordered(simulate_cell, tasks, chunksize=1)):
            results.append(r)
            elapsed = time.time() - t0
            status = "OK" if r.get("error") is None else f"ERR: {r['error'][:60]}"
            print(f"  [{i+1}/{len(tasks)}] cond={r.get('cond_idx')} cell={r.get('cell_idx')} "
                  f"({elapsed:.0f}s elapsed) {status}", flush=True)
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
