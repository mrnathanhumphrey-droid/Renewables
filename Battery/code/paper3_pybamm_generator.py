"""
Paper 3 — PyBaMM aging-mode-labeled synthetic generator (literature/36 §3, locked 3b9e1d6).

Generates 5000 PyBaMM cells via Latin Hypercube Sampling over a 7-dimensional
parameter space (cathode thickness, transference, NE/PE particle radius,
SEI rate, charge C-rate, temperature). Each cell runs to 80% SOH or 1500
cycles. Per-cell terminal aging-mode fractions {LLI, LAM-NE, LAM-PE,
kinetic-R} are extracted directly from PyBaMM's solution state — these are
the substrate-invariant labels Paper 3 trains against.

Per-cycle trajectory (Q_max, R_DC, R_total, plus OCV at 5/50/95% SOC where
extractable) is also recorded for downstream operator extraction.

Modal CPU parallel. Smoke test: `modal run code/paper3_pybamm_generator.py::smoke`
Full run:  `modal run code/paper3_pybamm_generator.py::main`
"""

import modal

app = modal.App("paper3-pybamm-gen")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("pybamm", "pandas", "numpy", "pyarrow", "scipy"))

# LHS will be generated locally; for now lock the parameter ranges per pre-reg
PARAM_RANGES = {
    "thickness_mult":          (0.5, 1.5),      # uniform
    "transference":            (0.20, 0.50),    # uniform
    "ne_particle_radius_log":  (-1.0, 1.0),     # log-uniform; mult = 2^x in [0.5x, 2x] of default
    "pe_particle_radius_log":  (-1.0, 1.0),     # log-uniform
    "sei_rate_log":            (-1.0, 1.6),     # log-uniform; mult = 2^x in [0.5x, ~3x] of default
    "charge_C_rate":           (0.5, 4.0),      # uniform
    "temperature_C":           (15.0, 45.0),    # uniform
}

# Total cells in production run
N_CELLS = 5000
MAX_CYCLES = 1500


def generate_lhs_samples(n_samples, seed=36000):
    """Latin Hypercube Sample n_samples points in [0,1]^d, then map to param ranges."""
    from scipy.stats import qmc
    import numpy as np

    d = len(PARAM_RANGES)
    sampler = qmc.LatinHypercube(d=d, seed=seed)
    unit = sampler.random(n_samples)

    # Map to param ranges
    samples = []
    for row in unit:
        s = {}
        for (key, (lo, hi)), u in zip(PARAM_RANGES.items(), row):
            s[key] = lo + u * (hi - lo)
        samples.append(s)
    return samples


def make_param_values(params):
    """Construct PyBaMM ParameterValues from sample dict."""
    import pybamm
    import numpy as np

    # Chen2020 (proven-stable Probe 4/5/6 base). Mechanics dropped per
    # literature/36 §11 deviation; LAM-NE / LAM-PE collapse to NaN in v1.
    pv = pybamm.ParameterValues("Chen2020")

    # Cathode thickness multiplier
    nominal_pos_thick = pv["Positive electrode thickness [m]"]
    pv["Positive electrode thickness [m]"] = nominal_pos_thick * params["thickness_mult"]

    # Cation transference
    pv["Cation transference number"] = params["transference"]

    # NE particle radius (mult = 2^log)
    ne_pr_mult = 2.0 ** params["ne_particle_radius_log"]
    nominal_ne_pr = pv["Negative particle radius [m]"]
    pv["Negative particle radius [m]"] = nominal_ne_pr * ne_pr_mult

    # PE particle radius
    pe_pr_mult = 2.0 ** params["pe_particle_radius_log"]
    nominal_pe_pr = pv["Positive particle radius [m]"]
    pv["Positive particle radius [m]"] = nominal_pe_pr * pe_pr_mult

    # SEI growth rate (Yang2017 uses "EC initial concentration in electrolyte"
    # and reaction-limited kinetics; scale rate via "SEI reaction exchange current density")
    # Conservatively scale via "SEI kinetic rate constant [m.s-1]" or fallback
    sei_mult = 2.0 ** params["sei_rate_log"]
    try:
        nominal_sei = pv["SEI kinetic rate constant [m.s-1]"]
        pv["SEI kinetic rate constant [m.s-1]"] = nominal_sei * sei_mult
    except Exception:
        # Fallback: scale via inner SEI partial molar volume (also affects growth rate)
        try:
            nominal = pv["Inner SEI partial molar volume [m3.mol-1]"]
            pv["Inner SEI partial molar volume [m3.mol-1]"] = nominal * sei_mult
        except Exception:
            pass

    # Temperature
    pv["Ambient temperature [K]"] = 273.15 + params["temperature_C"]
    pv["Initial temperature [K]"] = 273.15 + params["temperature_C"]

    return pv


def extract_mode_fractions(sol, fresh_Q):
    """Extract terminal aging-mode fractions {LLI, LAM-NE, LAM-PE, kinetic-R}.

    LLI: total cumulative SEI capacity loss / fresh capacity
    LAM-NE: terminal LAM in negative electrode, fractional
    LAM-PE: terminal LAM in positive electrode, fractional
    kinetic-R: (terminal R_DC - fresh R_DC) / fresh R_DC

    Returns dict with 4 fractions in [0, 1] (or NaN if extraction fails).
    """
    import numpy as np

    modes = {"LLI": float("nan"), "LAM_NE": float("nan"),
             "LAM_PE": float("nan"), "kinetic_R": float("nan")}

    # LLI via SEI capacity loss
    try:
        sei_loss_ah = sol["Loss of capacity to SEI [A.h]"].entries
        terminal_loss = float(sei_loss_ah[-1]) if len(sei_loss_ah) else float("nan")
        modes["LLI"] = abs(terminal_loss) / fresh_Q if fresh_Q > 0 else float("nan")
    except Exception:
        # Alternative: Total lost lithium (mol) -> convert to capacity
        try:
            n_li_initial = sol["Total lithium in particles [mol]"].entries[0]
            n_li_terminal = sol["Total lithium in particles [mol]"].entries[-1]
            modes["LLI"] = max(0.0, (n_li_initial - n_li_terminal) / n_li_initial)
        except Exception:
            pass

    # LAM-NE
    for key_try in [
        "X-averaged loss of active material in negative electrode [%]",
        "Loss of active material in negative electrode [%]",
        "Negative electrode capacity [A.h]",  # fallback: capacity ratio
    ]:
        try:
            v = sol[key_try].entries
            if "Negative electrode capacity" in key_try:
                modes["LAM_NE"] = max(0.0, 1.0 - float(v[-1]) / float(v[0]))
            else:
                modes["LAM_NE"] = float(v[-1]) / 100.0  # % to fraction
            break
        except Exception:
            continue

    # LAM-PE
    for key_try in [
        "X-averaged loss of active material in positive electrode [%]",
        "Loss of active material in positive electrode [%]",
        "Positive electrode capacity [A.h]",
    ]:
        try:
            v = sol[key_try].entries
            if "Positive electrode capacity" in key_try:
                modes["LAM_PE"] = max(0.0, 1.0 - float(v[-1]) / float(v[0]))
            else:
                modes["LAM_PE"] = float(v[-1]) / 100.0
            break
        except Exception:
            continue

    # kinetic-R will be computed downstream from observed R_DC trajectory
    return modes


@app.function(image=image, timeout=3600, cpu=1.0, memory=2048)
def simulate_cell(cell_idx: int, params: dict):
    """Run one synthetic cell, return aging-mode labels + trajectory."""
    import pybamm
    import numpy as np
    import json

    try:
        pv = make_param_values(params)

        # Yang2017 SEI only. Mechanics + LAM dropped per literature/36 §11 deviation.
        options = {"SEI": "ec reaction limited", "SEI porosity change": "true"}
        model = pybamm.lithium_ion.DFN(options=options)

        # Cycling: charge at param['charge_C_rate'], discharge at 1C
        charge_C = params["charge_C_rate"]
        cycle_step = (
            "Discharge at 1C until 2.5 V",
            "Rest for 5 minutes",
            f"Charge at {charge_C}C until 4.2 V",
            "Hold at 4.2 V until 50 mA",
            "Rest for 30 minutes",
        )
        experiment = pybamm.Experiment([cycle_step] * MAX_CYCLES,
                                       termination="80% capacity")
        # IDAKLU is the proven-stable choice on Chen2020 + Yang2017 SEI
        # (used by Probe 4/5/6 with low failure rate).
        try:
            solver = pybamm.IDAKLUSolver()
        except Exception:
            solver = pybamm.CasadiSolver(mode="safe")

        sim = pybamm.Simulation(model, parameter_values=pv,
                                experiment=experiment, solver=solver)
        sol = sim.solve(initial_soc=1.0)

        # Per-cycle observables
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
                trap = getattr(np, "trapezoid", None) or np.trapz
                Q_max = float(np.abs(trap(I, t)) / 3600.0)
                if Q_max < 0.1:
                    continue
                I_disch = float(np.median(np.abs(I)))
                V_open = float(V[0])
                if k > 0 and sol.cycles[k-1] is not None:
                    prev = sol.cycles[k-1]
                    if hasattr(prev, "steps") and len(prev.steps) > 0:
                        try:
                            V_open = float(prev.steps[-1]["Terminal voltage [V]"].entries[-1])
                        except Exception:
                            pass
                idx_30 = int(np.argmin(np.abs(t - t[0] - 30.0)))
                V30 = float(V[idx_30])
                t_end = t[-1] - t[0]
                if t_end > 1800.0:
                    idx_long = int(np.argmin(np.abs(t - t[0] - 1800.0)))
                    V_long = float(V[idx_long])
                else:
                    V_long = float(V[-1])
                R_DC = (V_open - V30) / I_disch
                R_total = (V_open - V_long) / I_disch
                rpts.append({"cycle": k + 1, "Q_max": Q_max, "R_DC": R_DC, "R_total": R_total})
            except Exception:
                continue

        if len(rpts) < 6:
            return {"cell_idx": cell_idx, "error": f"only {len(rpts)} valid RPTs",
                    **params}

        fresh_rpts = [r for r in rpts if 5 <= r["cycle"] <= 25]
        if len(fresh_rpts) < 3:
            fresh_rpts = rpts[:min(10, len(rpts))]
        fresh_Q = float(np.mean([r["Q_max"] for r in fresh_rpts]))
        fresh_R_DC = float(np.mean([r["R_DC"] for r in fresh_rpts]))
        fresh_R_total = float(np.mean([r["R_total"] for r in fresh_rpts]))

        post = [r for r in rpts if r["cycle"] > 25]
        crossed = [r for r in post if r["Q_max"] <= 0.80 * fresh_Q] if post else []
        partial = False
        if crossed:
            aged = crossed[0]
        elif post:
            aged = min(post, key=lambda r: r["Q_max"])
            partial = True
        else:
            aged = rpts[-1]
            partial = True
        aged_R_DC = aged["R_DC"]
        kinetic_R_frac = (aged_R_DC - fresh_R_DC) / fresh_R_DC if fresh_R_DC > 0 else float("nan")

        # Aging-mode fractions from sol state
        modes = extract_mode_fractions(sol, fresh_Q)
        modes["kinetic_R"] = kinetic_R_frac

        return {
            "cell_idx": cell_idx,
            **params,
            "n_rpts": len(rpts),
            "fresh_Q": fresh_Q, "fresh_R_DC": fresh_R_DC, "fresh_R_total": fresh_R_total,
            "aged_Q": aged["Q_max"], "aged_R_DC": aged_R_DC, "aged_R_total": aged["R_total"],
            "aged_cycle": aged["cycle"], "aged_SOH": aged["Q_max"] / fresh_Q,
            "partial_aging": partial,
            "LLI": modes["LLI"], "LAM_NE": modes["LAM_NE"],
            "LAM_PE": modes["LAM_PE"], "kinetic_R": modes["kinetic_R"],
            "rpts_json": json.dumps(rpts),
            "error": None,
        }
    except Exception as e:
        import traceback
        return {"cell_idx": cell_idx, **params,
                "error": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:1500]}


@app.local_entrypoint()
def smoke():
    """5-cell smoke test to verify aging-mode extraction works."""
    import json
    print("=== Paper 3 PyBaMM smoke test (5 cells) ===")
    samples = generate_lhs_samples(5, seed=36001)
    for i, s in enumerate(samples):
        print(f"\nCell {i}: {s}")

    tasks = list(enumerate(samples))
    raw = list(simulate_cell.starmap(tasks, return_exceptions=True))

    print(f"\n=== Smoke results ===")
    for (idx, params), r in zip(tasks, raw):
        if isinstance(r, BaseException):
            print(f"  Cell {idx}: BASE_EXCEPTION {type(r).__name__}: {str(r)[:200]}")
            continue
        if r.get("error"):
            print(f"  Cell {idx}: ERROR {r['error']}")
            if "traceback" in r:
                print(f"    traceback: {r['traceback'][:500]}")
            continue
        print(f"  Cell {idx}: n_rpts={r['n_rpts']}, aged_SOH={r['aged_SOH']:.3f}, "
              f"LLI={r.get('LLI', float('nan')):.4f}, "
              f"LAM_NE={r.get('LAM_NE', float('nan')):.4f}, "
              f"LAM_PE={r.get('LAM_PE', float('nan')):.4f}, "
              f"kinetic_R={r.get('kinetic_R', float('nan')):.4f}")


@app.local_entrypoint()
def main():
    """Full 5000-cell run per literature/36 §3."""
    import pandas as pd
    import os
    print(f"=== Paper 3 PyBaMM generator: {N_CELLS} cells ===")
    samples = generate_lhs_samples(N_CELLS, seed=36000)
    tasks = list(enumerate(samples))
    print(f"Total tasks: {len(tasks)}")

    raw = list(simulate_cell.starmap(tasks, return_exceptions=True))
    results = []
    for (idx, params), r in zip(tasks, raw):
        if isinstance(r, BaseException):
            results.append({"cell_idx": idx, **params,
                            "error": f"{type(r).__name__}: {str(r)[:200]}"})
        else:
            results.append(r)

    df = pd.DataFrame(results)
    n_err = df["error"].notna().sum()
    n_ok = (df["error"].isna()).sum()
    print(f"\n=== Run summary ===")
    print(f"  Successful: {n_ok}")
    print(f"  Failed:     {n_err}")

    out_path = "D:/Renewables/Battery/data/processed/paper3_pybamm_synthetic.parquet"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_parquet(out_path)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    print("Run with: modal run code/paper3_pybamm_generator.py::smoke")
    print("      or: modal run code/paper3_pybamm_generator.py::main")
