"""
Severson 2019 (BEEP-structured) operator extraction.

Per pre-reg literature/16 (locked 2026-05-21, commit 1ef1b94) Probe 2 §2:

Operators (3-vector per cell, per RPT-equivalent point):
  1. Q_max = summary.discharge_capacity   (per-cycle, BEEP-aggregated)
  2. DCIR = summary.dc_internal_resistance (per-cycle, BEEP pre-computed)
  3. T_can_amplitude = summary.temperature_maximum - summary.temperature_minimum

Note: Severson's cycling protocol is fast-charge -> 1C-CCCV discharge for EVERY
cycle. There is no separated diagnostic-cycle structure in the BEEP file
(diagnostic_summary is None). Per pre-reg, "diagnostic cycle" reinterprets to
"any cycle" in this cohort -- Q_max is just the per-cycle discharge capacity.

Fresh reference per cell: mean of operator triad over cycles 5-15.
Aged snapshot per cell:
  - First cycle where Q_max drops to <= 0.80 * fresh_Q_max (80% SOH crossing)
  - If never crosses, use the lowest-SOH cycle (lifetime-end value) and flag
    as partial_aging.

Batch identification from protocol filename:
  '2017-05-12_tests\\...' -> batch_1
  '2017-06-30_tests\\...' -> batch_2
  '2018-04-12_tests\\...' -> batch_3

First-step C-rate from protocol filename:
  e.g., '20170630-4_65C_69per_6C.sdu' -> 4.65 (the '4_65C' before the first per/_)

Includes all cells passing pre-reg §6 cell-inclusion:
  - >=5 cycles in cycles 5-15 (trivially true if cell ran past cycle 15)
  - reaches >=80% SOH OR has >=100 cycles total
"""

from pathlib import Path
import json
import re
import zipfile
from io import BytesIO
import numpy as np
import pandas as pd


ZIP_PATH = Path("D:/Renewables/Battery/data/severson/FastCharge.zip")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
SOH_TARGET = 0.80
FRESH_CYC_START = 5
FRESH_CYC_END = 15
MIN_CYCLES_REQUIRED = 100  # alternative to reaching 80% SOH

# Batch identifier = leading YYYY-MM-DD at start of protocol string. Severson original 3 batches:
#   '2017-05-12_TESTS\\20170512-...' -> batch 2017-05-12 (Batch 1)
#   '2017-06-30_tests\\20170630-...' -> batch 2017-06-30 (Batch 2)
#   '2018-04-12_batch8\\20180412-...' -> batch 2018-04-12 (Batch 3)
BATCH_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")

# First-step C-rate parser: after the YYYYMMDD- prefix in the filename, the first
# token is either '<digit>C' (integer) or '<digit>_<digit>C' (underscore-as-decimal).
# Examples after stripping date prefix:
#   '7C-30PER_3_6C.SDU'              -> 7.0
#   '4_4C_55per_6C.sdu'              -> 4.4
#   '3_7C_31per_5_9C_newstructure'   -> 3.7
#   '5C_67per_4C_newstructure'       -> 5.0
FIRST_C_RATE_RE = re.compile(r"^(\d+)(?:_(\d+))?C", re.IGNORECASE)


def parse_protocol(protocol_str):
    """Return (batch_date, first_step_c_rate) from protocol filename string."""
    batch_m = BATCH_RE.search(protocol_str)
    batch = batch_m.group(1) if batch_m else None

    # Get filename part after the last path separator (slash or backslash)
    fname = re.split(r"[\\/]+", protocol_str)[-1]
    # Strip the date prefix in the filename: 'YYYYMMDD-' or 'YYYYMMDD_'
    after_date = re.sub(r"^\d{8}[-_]?", "", fname, count=1)
    m = FIRST_C_RATE_RE.match(after_date)
    if m:
        if m.group(2):
            rate = float(f"{m.group(1)}.{m.group(2)}")
        else:
            rate = float(m.group(1))
    else:
        rate = float("nan")
    return batch, rate


def extract_cell_summary(zfile, member_name):
    """Read one BEEP cell JSON from zip; return dict of operators or None if invalid."""
    with zfile.open(member_name) as f:
        # Stream the raw bytes then decode
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    # Python's json.loads accepts NaN as float by default
    data = json.loads(text)
    proto = data.get("protocol", "")
    batch, first_c = parse_protocol(proto)
    summary = data.get("summary", {})
    cycle_index = np.array(summary.get("cycle_index", []), dtype=float)
    q = np.array(summary.get("discharge_capacity", []), dtype=float)
    r = np.array(summary.get("dc_internal_resistance", []), dtype=float)
    tmax = np.array(summary.get("temperature_maximum", []), dtype=float)
    tmin = np.array(summary.get("temperature_minimum", []), dtype=float)
    tamp = tmax - tmin

    if len(cycle_index) < FRESH_CYC_END:
        return None

    # Fresh window: cycles 5-15
    fresh_mask = (cycle_index >= FRESH_CYC_START) & (cycle_index <= FRESH_CYC_END)
    if fresh_mask.sum() < 5:
        return None
    fresh_q = np.nanmean(q[fresh_mask])
    fresh_r = np.nanmean(r[fresh_mask])
    fresh_t = np.nanmean(tamp[fresh_mask])

    # Aged anchor: first cycle where Q <= 0.80 * fresh_q (after the fresh window)
    post_fresh_mask = cycle_index > FRESH_CYC_END
    if post_fresh_mask.sum() == 0:
        return None

    q_post = q[post_fresh_mask]
    r_post = r[post_fresh_mask]
    t_post = tamp[post_fresh_mask]
    idx_post = cycle_index[post_fresh_mask]
    soh_post = q_post / fresh_q

    crossed = np.where(soh_post <= SOH_TARGET)[0]
    if len(crossed) > 0:
        aged_idx = int(crossed[0])
        partial = False
    else:
        # Never crossed 80% SOH; use lowest-SOH cycle
        if len(soh_post) < MIN_CYCLES_REQUIRED:
            return None
        aged_idx = int(np.nanargmin(soh_post))
        partial = True

    aged_q = float(q_post[aged_idx])
    aged_r = float(r_post[aged_idx])
    aged_t = float(t_post[aged_idx])
    aged_cycle = float(idx_post[aged_idx])
    aged_soh = aged_q / fresh_q

    return {
        "barcode": data.get("barcode"),
        "channel_id": data.get("channel_id"),
        "protocol": proto,
        "batch_date": batch,
        "first_step_C": first_c,
        "n_cycles": int(cycle_index.max()) if len(cycle_index) else 0,
        "fresh_Q": fresh_q,
        "fresh_R": fresh_r,
        "fresh_T_amp": fresh_t,
        "aged_Q": aged_q,
        "aged_R": aged_r,
        "aged_T_amp": aged_t,
        "aged_cycle": aged_cycle,
        "aged_SOH": aged_soh,
        "partial_aging": partial,
    }


def main():
    print(f"=== Severson BEEP extraction ===")
    print(f"  Source: {ZIP_PATH}")

    cells = []
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        members = [m for m in zf.namelist() if m.endswith(".json")]
        print(f"  Cells in archive: {len(members)}")
        for i, m in enumerate(members):
            try:
                row = extract_cell_summary(zf, m)
            except Exception as e:
                print(f"  [err {i+1}/{len(members)}] {m}: {type(e).__name__}: {str(e)[:80]}")
                continue
            if row is None:
                continue
            row["file"] = m
            cells.append(row)
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{len(members)}] extracted; running n_kept={len(cells)}")

    df = pd.DataFrame(cells)
    print(f"\n=== Extraction summary ===")
    print(f"  Cells with extracted operators: {len(df)}")
    print(f"  Cells reaching 80% SOH (full aging): {(~df['partial_aging']).sum()}")
    print(f"  Cells flagged partial_aging:         {df['partial_aging'].sum()}")
    print(f"\n  Per-batch counts:")
    print(df.groupby("batch_date").agg(n=("barcode", "count"),
                                        n_partial=("partial_aging", "sum"),
                                        med_first_C=("first_step_C", "median")).to_string())

    print(f"\n  First-step C-rate distribution (all cells):")
    fc = df["first_step_C"].values
    fc = fc[~np.isnan(fc)]
    print(f"    min={fc.min():.2f}, 25th={np.percentile(fc, 25):.2f}, median={np.median(fc):.2f}, 75th={np.percentile(fc, 75):.2f}, max={fc.max():.2f}")
    print(f"    locked bins (pre-reg sec.3): <4.5C / 4.5-6C / >=6C")
    bin_a = (fc < 4.5).sum()
    bin_b = ((fc >= 4.5) & (fc < 6.0)).sum()
    bin_c = (fc >= 6.0).sum()
    print(f"    bin A (<4.5C):    n={bin_a}")
    print(f"    bin B (4.5-6C):   n={bin_b}")
    print(f"    bin C (>=6C):     n={bin_c}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "severson_extracted.parquet"
    df.to_parquet(out_path)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
