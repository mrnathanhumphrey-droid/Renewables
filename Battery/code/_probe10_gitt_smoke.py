"""Probe 10 GITT smoke (THROWAWAY — not committed, no pre-reg).

Question: does a GITT-derived finite-amplitude operator carry transference
signal that linearized EIS (10 mHz / 1 mHz / low-SoC) all missed?

Design: ONE nominal cell (mid thickness, mid particle radius, no amvf
perturbation), fresh state, run at the three transference levels
{0.20, 0.2594, 0.32}. Protocol per level:
    Rest 10 min (settle to OCV) -> Discharge 1C 10 min (GITT pulse) ->
    Rest 1 hour (relaxation).
Vary ONLY transference, so any operator spread across the 3 levels is a
pure transference signal (mirrors the Probe 9 smoke's R_diff-spread screen).

Candidate operators (concentration polarization + slow relaxation tail are
the transference-sensitive ones; ohmic/fast-kinetics are not):
  eta_total  = OCV - V(pulse end)            total polarization
  eta_inst   = OCV - V(pulse start)          ~ohmic + fast kinetics
  eta_conc   = eta_total - eta_inst          concentration polarization  <-- candidate
  dV_slow    = V(relax end) - V(relax 60s)   slow diffusion tail         <-- candidate
  dV_fast    = V(relax 10s) - V(relax 0s)    fast charge-transfer recovery
  V_relax_end= quasi-OCV after 1 hr rest

Screen: if eta_conc or dV_slow spread >> EIS R_diff spread (~1-3%), GITT may
carry the signal -> worth a pre-reg. If all flat -> GITT also transference-blind.

Run: python code/_probe10_gitt_smoke.py
"""

import time
import numpy as np
import pybamm

TRANSFERENCE_ABS = [0.20, 0.2594, 0.32]
PARTICLE_RADIUS_NOM = 5.22e-6  # mid level


def run_gitt(t_plus):
    pv = pybamm.ParameterValues("Chen2020")
    pv["Cation transference number"] = t_plus
    pv["Positive particle radius [m]"] = PARTICLE_RADIUS_NOM
    model = pybamm.lithium_ion.DFN()
    experiment = pybamm.Experiment([(
        "Rest for 10 minutes",
        "Discharge at 1C for 10 minutes",
        "Rest for 1 hour",
    )])
    try:
        solver = pybamm.IDAKLUSolver()
    except Exception:
        solver = pybamm.CasadiSolver(mode="safe")
    sim = pybamm.Simulation(model, parameter_values=pv,
                            experiment=experiment, solver=solver)
    t0 = time.time()
    sol = sim.solve(initial_soc=0.9)
    wall = time.time() - t0

    cyc = sol.cycles[0]
    s_rest0, s_pulse, s_relax = cyc.steps[0], cyc.steps[1], cyc.steps[2]

    V_ocv = float(s_rest0["Terminal voltage [V]"].entries[-1])
    Vp = s_pulse["Terminal voltage [V]"].entries
    V_pulse_start = float(Vp[0])
    V_pulse_end = float(Vp[-1])

    tr = s_relax["Time [s]"].entries
    Vr = s_relax["Terminal voltage [V]"].entries
    tr0 = tr - tr[0]

    def Vat(target):
        return float(Vr[int(np.argmin(np.abs(tr0 - target)))])

    V_relax_0 = float(Vr[0])
    V_relax_end = float(Vr[-1])

    eta_total = V_ocv - V_pulse_end
    eta_inst = V_ocv - V_pulse_start
    eta_conc = eta_total - eta_inst
    dV_slow = V_relax_end - Vat(60.0)
    dV_fast = Vat(10.0) - V_relax_0

    return {
        "t_plus": t_plus,
        "wall_s": wall,
        "V_ocv": V_ocv,
        "eta_total": eta_total,
        "eta_inst": eta_inst,
        "eta_conc": eta_conc,
        "dV_slow": dV_slow,
        "dV_fast": dV_fast,
        "V_relax_end": V_relax_end,
    }


def main():
    print("=== Probe 10 GITT smoke: nominal cell x 3 transference levels (fresh) ===")
    rows = []
    for tp in TRANSFERENCE_ABS:
        print(f"  solving t_plus={tp} ...", flush=True)
        r = run_gitt(tp)
        rows.append(r)
        print(f"    ({r['wall_s']:.1f}s)  eta_conc={r['eta_conc']*1e3:.3f} mV  "
              f"dV_slow={r['dV_slow']*1e3:.3f} mV", flush=True)

    ops = ["eta_total", "eta_inst", "eta_conc", "dV_slow", "dV_fast", "V_relax_end"]
    print("\n=== Operator values by transference level (mV) ===")
    print(f"{'operator':14s} " + "  ".join(f"t={r['t_plus']:.4f}" for r in rows) + "   spread%")
    for op in ops:
        vals = np.array([r[op] for r in rows])
        mean = np.mean(vals)
        spread = (vals.max() - vals.min()) / abs(mean) * 100 if abs(mean) > 1e-12 else 0.0
        cells = "  ".join(f"{v*1e3:9.3f}" for v in vals)
        print(f"{op:14s} {cells}   {spread:6.2f}%")

    print("\n=== Screen ===")
    print("EIS R_diff transference spread for reference: 10 mHz ~0.97%, 1 mHz ~2.73% (Probe 9 smoke).")
    for op in ["eta_conc", "dV_slow"]:
        vals = np.array([r[op] for r in rows])
        mean = np.mean(vals)
        spread = (vals.max() - vals.min()) / abs(mean) * 100 if abs(mean) > 1e-12 else 0.0
        verdict = "PROMISING (>> EIS)" if spread > 5.0 else ("comparable to EIS" if spread > 1.0 else "FLAT (transference-blind)")
        print(f"  {op}: spread {spread:.2f}%  -> {verdict}")
    print(f"\nPer-cell wall (fresh GITT, 1 pulse): ~{np.mean([r['wall_s'] for r in rows]):.1f}s")


if __name__ == "__main__":
    main()
