"""Probe 10 — GITT finite-amplitude operator generator.

Replaces EIS characterization with a GITT pulse (Rest 10min -> Discharge 1C
10min -> Rest 1hr) at fresh and B5'-aged states. Motivated by the GITT smoke:
eta_conc (concentration polarization at pulse end) showed 5.57% transference
spread, monotonic, ~2x the best EIS operator (1 mHz) and physically correct.
GITT is the finite-amplitude / large-signal operator class that lit/53
identified as the only remaining transference-recovery path after the EIS
lane (10 mHz / low-SoC / sub-mHz) was exhausted.

Aged state is READ from the committed Probe 9 v3 parquet (SEI thickness +
negative porosity per cell at the SOH 0.92 anchor) and baked into
ParameterValues via the B5' method — NO re-cycling. This makes the aged
state bit-identical to Probe 9 and the run fast (GITT solve ~0.4s/state).

Output columns per cell, at fresh + aged:
  eta_total, eta_inst, eta_conc, dV_slow, dV_fast, V_relax_end
(eta_conc and dV_slow are the transference candidates; eta_inst is the
ohmic/fast-kinetics control, expected transference-blind.)

Local multiprocessing 8-wide (fit running). ~1-2 min wall expected.

Run: python code/probe10_pybamm_gitt_generator.py [n_cells]
"""

import os
import sys
import time
import traceback
from multiprocessing import Pool, set_start_method

import numpy as np
import pandas as pd

THICKNESS_MULT = [0.80, 1.00, 1.20]
TRANSFERENCE_ABS = [0.20, 0.2594, 0.32]
PARTICLE_RADIUS_ABS_M = [4.0e-6, 5.22e-6, 6.5e-6]
LEVEL_IDX = {"low": 0, "mid": 1, "high": 2}

N_WORKERS = 8

V3_PARQUET = "D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_eis_v3.parquet"
OUT_PARQUET = "D:/Renewables/Battery/data/processed/pybamm_l9_trajectories_gitt_v1.parquet"

GITT_EXPERIMENT = [(
    "Rest for 10 minutes",
    "Discharge at 1C for 10 minutes",
    "Rest for 1 hour",
)]


def _gitt_extract(pv, model_options=None):
    """Run GITT pulse on the given ParameterValues; return operator dict."""
    import pybamm
    model = pybamm.lithium_ion.DFN(options=model_options) if model_options else pybamm.lithium_ion.DFN()
    experiment = pybamm.Experiment(GITT_EXPERIMENT)
    try:
        solver = pybamm.IDAKLUSolver()
    except Exception:
        solver = pybamm.CasadiSolver(mode="safe")
    sim = pybamm.Simulation(model, parameter_values=pv,
                            experiment=experiment, solver=solver)
    sol = sim.solve(initial_soc=0.9)

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

    eta_total = V_ocv - V_pulse_end
    eta_inst = V_ocv - V_pulse_start
    return {
        "eta_total": eta_total,
        "eta_inst": eta_inst,
        "eta_conc": eta_total - eta_inst,
        "dV_slow": float(Vr[-1]) - Vat(60.0),
        "dV_fast": Vat(10.0) - float(Vr[0]),
        "V_relax_end": float(Vr[-1]),
    }


def simulate_cell(rec):
    """rec = dict from the v3 parquet for one clean cell."""
    cond_idx = int(rec["cond_idx"])
    cell_idx = int(rec["cell_idx"])
    try:
        import pybamm
        import numpy as _np

        th_lvl = LEVEL_IDX[rec["thickness_level"]]
        tn_lvl = LEVEL_IDX[rec["transference_level"]]
        pr_lvl = LEVEL_IDX[rec["particle_radius_level"]]
        eps_pos = float(rec["eps_pos_amvf"])
        eps_neg = float(rec["eps_neg_amvf"])
        sei_aged = float(rec["sei_neg_aged_m"])
        por_aged = float(rec["neg_porosity_aged"])

        def base_pv():
            pv = pybamm.ParameterValues("Chen2020")
            pv["Positive electrode thickness [m]"] = pv["Positive electrode thickness [m]"] * THICKNESS_MULT[th_lvl]
            pv["Cation transference number"] = TRANSFERENCE_ABS[tn_lvl]
            pv["Positive particle radius [m]"] = PARTICLE_RADIUS_ABS_M[pr_lvl]
            nom_pos = pv["Positive electrode active material volume fraction"]
            nom_neg = pv["Negative electrode active material volume fraction"]
            pv["Positive electrode active material volume fraction"] = nom_pos * (1 + eps_pos)
            pv["Negative electrode active material volume fraction"] = nom_neg * (1 + eps_neg)
            return pv

        # Fresh GITT
        pv_fresh = base_pv()
        try:
            fresh = _gitt_extract(pv_fresh)
            fresh_err = None
        except Exception as ex:
            fresh = {k: float("nan") for k in
                     ["eta_total", "eta_inst", "eta_conc", "dV_slow", "dV_fast", "V_relax_end"]}
            fresh_err = f"{type(ex).__name__}: {str(ex)[:150]}"

        # B5'-aged GITT (SEI + porosity baked in; SEI submodel enabled)
        aged_opts = {"SEI": "ec reaction limited", "SEI porosity change": "true"}
        if not (_np.isnan(sei_aged) or _np.isnan(por_aged)):
            pv_aged = base_pv()
            pv_aged["Initial SEI thickness [m]"] = sei_aged
            pv_aged["Negative electrode porosity"] = por_aged
            try:
                aged = _gitt_extract(pv_aged, model_options=aged_opts)
                aged_err = None
            except Exception as ex:
                aged = {k: float("nan") for k in
                        ["eta_total", "eta_inst", "eta_conc", "dV_slow", "dV_fast", "V_relax_end"]}
                aged_err = f"{type(ex).__name__}: {str(ex)[:150]}"
        else:
            aged = {k: float("nan") for k in
                    ["eta_total", "eta_inst", "eta_conc", "dV_slow", "dV_fast", "V_relax_end"]}
            aged_err = "aged state vars NaN in v3"

        out = {
            "cond_idx": cond_idx, "cell_idx": cell_idx,
            "thickness_level": rec["thickness_level"],
            "transference_level": rec["transference_level"],
            "particle_radius_level": rec["particle_radius_level"],
            "eps_pos_amvf": eps_pos, "eps_neg_amvf": eps_neg,
            "sei_neg_aged_m": sei_aged, "neg_porosity_aged": por_aged,
            "fresh_eis_err": fresh_err, "aged_eis_err": aged_err,
            "error": None,
        }
        for k, v in fresh.items():
            out[f"fresh_{k}"] = v
        for k, v in aged.items():
            out[f"aged_{k}"] = v
        return out
    except Exception as e:
        return {"cond_idx": cond_idx, "cell_idx": cell_idx,
                "error": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:1500]}


def main(n_cells_override=None):
    v3 = pd.read_parquet(V3_PARQUET)
    clean = v3[v3["error"].isna()].copy()
    # Keep cells with usable aged state (match Probe 9 clean-table filter)
    clean = clean[clean["anchor_partial"] != True]  # noqa: E712
    recs = clean.to_dict("records")
    if n_cells_override is not None:
        recs = recs[:n_cells_override]
    print(f"=== Probe 10 GITT generator: {len(recs)} cells, {N_WORKERS}-wide ===")
    print(f"   Aged state read from {os.path.basename(V3_PARQUET)} (no re-cycling)")
    print(f"   Output: {OUT_PARQUET}")
    t0 = time.time()
    with Pool(processes=N_WORKERS) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(simulate_cell, recs, chunksize=1)):
            results.append(r)
            elapsed = time.time() - t0
            status = "OK" if r.get("error") is None else f"ERR: {r['error'][:50]}"
            ae = r.get("aged_eis_err")
            fe = r.get("fresh_eis_err")
            extra = ""
            if ae:
                extra += f" aged_err={ae[:40]}"
            if fe:
                extra += f" fresh_err={fe[:40]}"
            print(f"  [{i+1}/{len(recs)}] cond={r.get('cond_idx')} cell={r.get('cell_idx')} "
                  f"({elapsed:.0f}s) {status}{extra}", flush=True)
    df = pd.DataFrame(results)
    n_err = df["error"].notna().sum()
    n_ok = (df["error"].isna()).sum()
    print(f"\n=== Summary ({time.time()-t0:.0f}s wall) ===")
    print(f"  Successful: {n_ok}  Failed: {n_err}")
    if "aged_eis_err" in df.columns:
        print(f"  Aged GITT errors: {df['aged_eis_err'].notna().sum()}")
        print(f"  Fresh GITT errors: {df['fresh_eis_err'].notna().sum()}")
    os.makedirs(os.path.dirname(OUT_PARQUET), exist_ok=True)
    df.to_parquet(OUT_PARQUET)
    print(f"\nWritten: {OUT_PARQUET}")


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            set_start_method("spawn", force=True)
        except RuntimeError:
            pass
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(n_cells_override=n)
