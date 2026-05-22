"""
C3 Probe 4 — PyBaMM synthetic material-design inversion, executed on Modal.

Implements pre-reg literature/19 (commit d03a558).

L9 Taguchi orthogonal fractional factorial design across 3 design parameters
(cathode thickness, transference number, cathode particle radius) at 3 levels each.
9 conditions x 12 cells per condition = 108 synthetic cells.

Each cell runs Chen2020 (LGM50 NMC811/graphite) DFN with stress-driven SEI growth
(Yang2017) under 1C/1C cycling until 80% SOH or 500 cycles. Operator triad
(Q_max, R_DC, R_total) extracted at the cell's fresh (cycles 5-25 mean) and
aged (first cycle to 80% SOH or last available) anchors.

Run: modal run code/modal_pybamm_c3.py
"""

import modal

app = modal.App("pybamm-c3")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("pybamm", "pandas", "numpy", "pyarrow"))

# L9 Taguchi orthogonal design matrix.
# Each row: (cathode_thickness_level, transference_level, particle_radius_level)
# Levels coded as 0 (low), 1 (mid), 2 (high)
L9_DESIGN = [
    (0, 0, 0),  # condition 1
    (0, 1, 1),  # condition 2
    (0, 2, 2),  # condition 3
    (1, 0, 1),  # condition 4
    (1, 1, 2),  # condition 5
    (1, 2, 0),  # condition 6
    (2, 0, 2),  # condition 7
    (2, 1, 0),  # condition 8
    (2, 2, 1),  # condition 9
]

# Level multipliers / absolute values per pre-reg sec.2
THICKNESS_MULT = [0.80, 1.00, 1.20]
TRANSFERENCE_ABS = [0.20, 0.2594, 0.32]
PARTICLE_RADIUS_ABS_M = [4.0e-6, 5.22e-6, 6.5e-6]

CELLS_PER_CONDITION = 12
RPT_CADENCE = 25
MAX_CYCLES = 500
SOH_TERMINATION = 0.80


def make_param_values(cond_idx, cell_idx):
    """Construct PyBaMM ParameterValues with design + per-cell perturbations."""
    import pybamm
    import numpy as np

    pv = pybamm.ParameterValues("Chen2020")

    # Design parameters per L9
    th_lvl, tn_lvl, pr_lvl = L9_DESIGN[cond_idx]
    nominal_pos_thick = pv["Positive electrode thickness [m]"]
    pv["Positive electrode thickness [m]"] = nominal_pos_thick * THICKNESS_MULT[th_lvl]
    pv["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
    pv["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]

    # Per-cell active material volume fraction perturbation
    seed = 1000 + cond_idx * 100 + cell_idx
    rng = np.random.default_rng(seed)
    eps_pos = float(rng.normal(0, 0.02))
    eps_neg = float(rng.normal(0, 0.02))
    nom_pos_amvf = pv["Positive electrode active material volume fraction"]
    nom_neg_amvf = pv["Negative electrode active material volume fraction"]
    pv["Positive electrode active material volume fraction"] = nom_pos_amvf * (1 + eps_pos)
    pv["Negative electrode active material volume fraction"] = nom_neg_amvf * (1 + eps_neg)

    return pv, eps_pos, eps_neg


@app.function(image=image, timeout=2700, cpu=1.0, memory=2048)
def simulate_cell(cond_idx: int, cell_idx: int):
    """Run one synthetic cell, return operator triad dict.

    Operators per pre-reg sec.6:
      - Q_max = discharge capacity per RPT cycle
      - R_DC = (V at t=0 of discharge step - V at t=30s) / 1C current
      - R_total = (V at t=0 of discharge - V at t=30min) / 1C current
    """
    import pybamm
    import numpy as np

    try:
        pv, eps_pos, eps_neg = make_param_values(cond_idx, cell_idx)

        # SEI growth + LLI submodel (Yang 2017 / interstitial diffusion limited)
        options = {"SEI": "ec reaction limited", "SEI porosity change": "true"}
        model = pybamm.lithium_ion.DFN(options=options)

        # Cycling experiment: 1C/1C with 30-min rest, repeated
        # Run in batches of RPT_CADENCE cycles, extract diagnostics each batch
        cycle_step = ("Discharge at 1C until 2.5 V",
                      "Rest for 5 minutes",
                      "Charge at 1C until 4.2 V",
                      "Hold at 4.2 V until 50 mA",
                      "Rest for 30 minutes")
        # Termination goes on Experiment (PyBaMM API), not on solve()
        experiment = pybamm.Experiment([cycle_step] * MAX_CYCLES,
                                       termination="80% capacity")
        # Prefer IDAKLU solver (faster on DAEs); fall back to CasADi if not installed
        try:
            solver = pybamm.IDAKLUSolver()
        except Exception:
            solver = pybamm.CasadiSolver(mode="safe")
        sim = pybamm.Simulation(model, parameter_values=pv, experiment=experiment, solver=solver)
        sol = sim.solve(initial_soc=1.0)

        # Per-cycle Q_max and impedance proxies
        rpts = []
        n_cycles = len(sol.cycles) if sol.cycles is not None else 0
        skipped_reasons = {"None": 0, "steps_err": 0, "t_short": 0, "Q_low": 0, "other": 0}
        for k in range(0, n_cycles, 1):
            cyc = sol.cycles[k]
            if cyc is None:
                skipped_reasons["None"] += 1
                continue
            # Discharge step (step 0 = "Discharge at 1C until 2.5 V")
            try:
                disch = cyc.steps[0]
                t = disch["Time [s]"].entries
                V = disch["Terminal voltage [V]"].entries
                I = disch["Current [A]"].entries
                if len(t) < 3:
                    skipped_reasons["t_short"] += 1
                    continue
                # Q delivered in this discharge step = integral of |I| dt
                # np.trapezoid is NumPy 2.x; np.trapz removed
                trap = getattr(np, "trapezoid", None) or np.trapz
                Q_max = float(np.abs(trap(I, t)) / 3600.0)
                if Q_max < 0.1:
                    skipped_reasons["Q_low"] += 1
                    continue
                I_disch = float(np.median(np.abs(I)))
                # V_open = V at end of preceding rest step (true open-circuit)
                # For cycle 0, no preceding rest -> fall back to V[0] of discharge
                V_open = float(V[0])
                if k > 0 and sol.cycles[k-1] is not None:
                    prev = sol.cycles[k-1]
                    if hasattr(prev, "steps") and len(prev.steps) > 0:
                        prev_last = prev.steps[-1]  # last step = "Rest for 30 minutes"
                        try:
                            V_open = float(prev_last["Terminal voltage [V]"].entries[-1])
                        except Exception:
                            pass
                # V at 30 sec into discharge
                idx_30 = int(np.argmin(np.abs(t - t[0] - 30.0)))
                V30 = float(V[idx_30])
                # V at 30 min into discharge (or end if step shorter)
                t_end = t[-1] - t[0]
                if t_end > 1800.0:
                    idx_long = int(np.argmin(np.abs(t - t[0] - 1800.0)))
                    V_long = float(V[idx_long])
                else:
                    V_long = float(V[-1])
                R_DC = (V_open - V30) / I_disch
                R_total = (V_open - V_long) / I_disch
                rpts.append({"cycle": k + 1, "Q_max": Q_max, "R_DC": R_DC, "R_total": R_total})
            except Exception as ex:
                skipped_reasons["steps_err"] += 1
                if skipped_reasons["steps_err"] <= 2:
                    skipped_reasons[f"first_err_msg"] = f"{type(ex).__name__}: {str(ex)[:200]}"
                continue

        if len(rpts) < 6:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                    "error": f"only {len(rpts)} valid RPTs (n_cycles={n_cycles}, skipped={skipped_reasons})"}

        # Fresh = mean of cycles 5-25
        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 5:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx, "error": f"only {len(fresh_rpts)} fresh-window RPTs"}
        fresh_Q = float(np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(np.mean([r["R_total"] for r in fresh_rpts]))

        # Aged = first cycle where Q <= 0.80 * fresh_Q (after the fresh window)
        post = [r for r in rpts if r["cycle"] > 25]
        if not post:
            return {"cond_idx": cond_idx, "cell_idx": cell_idx, "error": "no post-fresh cycles"}
        crossed = [r for r in post if r["Q_max"] <= 0.80 * fresh_Q]
        partial = False
        if crossed:
            aged = crossed[0]
        else:
            # Use minimum-Q cycle as lifetime-end anchor
            aged = min(post, key=lambda r: r["Q_max"])
            partial = True
        aged_Q = aged["Q_max"]
        aged_R_DC = aged["R_DC"]
        aged_R_total = aged["R_total"]
        aged_cycle = aged["cycle"]
        aged_SOH = aged_Q / fresh_Q

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
            "error": None,
        }
    except Exception as e:
        import traceback
        return {"cond_idx": cond_idx, "cell_idx": cell_idx, "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc()[:1500]}


@app.local_entrypoint()
def smoke():
    """Run 1 cell as smoke test to verify the PyBaMM API + Modal pipeline."""
    print("=== Smoke test: 1 cell (cond=0, cell=0) ===")
    r = simulate_cell.remote(0, 0)
    print(f"\nResult keys: {list(r.keys()) if isinstance(r, dict) else type(r)}")
    if isinstance(r, dict):
        for k, v in r.items():
            if k == "traceback":
                print(f"  {k}: {str(v)[:500]}")
            else:
                print(f"  {k}: {v}")


@app.function(image=image, timeout=2700, cpu=1.0, memory=2048)
def debug_solution_schema():
    """Probe pybamm sol.cycles structure to understand API."""
    import pybamm, numpy as np
    pv, _, _ = make_param_values(0, 0)
    options = {"SEI": "ec reaction limited", "SEI porosity change": "true"}
    model = pybamm.lithium_ion.DFN(options=options)
    cycle_step = ("Discharge at 1C until 2.5 V",
                  "Rest for 5 minutes",
                  "Charge at 1C until 4.2 V",
                  "Hold at 4.2 V until 50 mA",
                  "Rest for 30 minutes")
    # Just 5 cycles for fast debug
    experiment = pybamm.Experiment([cycle_step] * 5)
    try:
        solver = pybamm.IDAKLUSolver()
    except Exception:
        solver = pybamm.CasadiSolver(mode="safe")
    sim = pybamm.Simulation(model, parameter_values=pv, experiment=experiment, solver=solver)
    sol = sim.solve(initial_soc=1.0)
    info = {
        "type_sol": type(sol).__name__,
        "sol_dir": [a for a in dir(sol) if not a.startswith("_")][:40],
        "cycles_is_none": sol.cycles is None if hasattr(sol, "cycles") else None,
        "cycles_len": len(sol.cycles) if (hasattr(sol, "cycles") and sol.cycles is not None) else 0,
        "cycles_kinds": [type(c).__name__ if c is not None else "None" for c in (sol.cycles or [])[:5]],
        "summary_var_type": type(sol.summary_variables).__name__ if hasattr(sol, "summary_variables") else None,
        "summary_var_dir": [a for a in dir(sol.summary_variables) if not a.startswith("_")][:30] if hasattr(sol, "summary_variables") else None,
    }
    # Try various access patterns on summary_variables
    if hasattr(sol, "summary_variables"):
        sv = sol.summary_variables
        for try_key in ["Capacity [A.h]", "Discharge capacity [A.h]", "Cycle number"]:
            try:
                v = sv[try_key]
                info[f"sv[{try_key!r}]"] = {"type": type(v).__name__, "head": list(v[:3]) if hasattr(v, "__getitem__") else None}
            except Exception as e:
                info[f"sv[{try_key!r}]_err"] = str(e)[:120]
    return info


@app.local_entrypoint()
def probe():
    """Inspect the pybamm Solution API on a 5-cycle run."""
    r = debug_solution_schema.remote()
    import json
    print(json.dumps(r, default=str, indent=2)[:5000])


@app.local_entrypoint()
def main():
    import pandas as pd
    import json

    print(f"=== C3 Probe 4: PyBaMM L9 sweep, 9 conditions x {CELLS_PER_CONDITION} cells = {9*CELLS_PER_CONDITION} sims ===")
    tasks = [(c, i) for c in range(9) for i in range(CELLS_PER_CONDITION)]
    print(f"Total tasks: {len(tasks)}")

    # return_exceptions=True turns per-task timeouts/errors into Exception values
    # rather than crashing the local entrypoint. We coerce them to error dicts
    # so the parquet captures partial-success status.
    raw = list(simulate_cell.starmap(tasks, return_exceptions=True))
    results = []
    for (cond, cell), r in zip(tasks, raw):
        if isinstance(r, BaseException):
            results.append({"cond_idx": cond, "cell_idx": cell,
                            "error": f"{type(r).__name__}: {str(r)[:200]}"})
        else:
            results.append(r)

    df = pd.DataFrame(results)
    n_err = df["error"].notna().sum()
    n_ok = (df["error"].isna()).sum()
    print(f"\n=== Simulation summary ===")
    print(f"  Successful: {n_ok}")
    print(f"  Failed:     {n_err}")
    if n_err > 0:
        print(f"\n  First 5 errors:")
        err_df = df[df["error"].notna()].head(5)
        for _, r in err_df.iterrows():
            print(f"    cond {r['cond_idx']} cell {r['cell_idx']}: {r['error']}")

    out_path = "D:/Renewables/Battery/data/processed/pybamm_l9_results.parquet"
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_parquet(out_path)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    print("Run with: modal run code/modal_pybamm_c3.py")
