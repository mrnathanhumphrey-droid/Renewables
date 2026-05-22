"""
C3 Probe 2 amendment — Severson alternative-axis PERMANOVA.

Pre-reg: literature/21_c3_severson_v2_pre_registration.md (commit 3fb179a).

Reads existing data/processed/severson_extracted.parquet from literature/17
without re-extracting. Parses three new design axes from the existing
`protocol` strings:

  1. last_step_C    -- final CC segment C-rate
  2. soc_handoff    -- SOC fraction at which protocol transitions from first
                       stage to second
  3. severity       -- SOC-weighted average C-rate (the protocol's effective
                       overall stress level)

For each axis: tertile cuts on empirical distribution -> 3 bins.
PERMANOVA pooled + batch-stratified, 10000 perms, Bonferroni alpha/3 = 0.0167,
effect-size floor pseudo-F > 3.0.

Verdicts per pre-reg sec.6:
  AXIS PASS              : pooled p<0.0167 AND F>3.0 AND Batch-2 within-batch p<0.05
  AXIS POOLED-ONLY PASS  : pooled passes but Batch-2 within-batch fails
  AXIS WEAK PASS         : p in [0.0167, 0.05] AND F > 2.0
  AXIS NULL              : p>=0.05 OR F<2.0

H5 verdicts:
  H5 SUPPORT             : at least 1 axis is AXIS PASS
  H5 WEAK                : 0 PASS but 2+ POOLED-ONLY-PASS or WEAK PASS
  H5 NULL                : 0 axes show any separation
  H5 INVALID             : parsing fails on >10% of cells
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd


IN_PARQUET = Path("D:/Renewables/Battery/data/processed/severson_extracted.parquet")
OUT_DIR = Path("D:/Renewables/Battery/data/processed")
RNG = np.random.default_rng(seed=42)
N_PERMS = 10000

ALPHA_BONFERRONI = 0.0167
EFFECT_F_FLOOR = 3.0
EFFECT_F_WEAK = 2.0
ALPHA_WEAK = 0.05

# Regex to find C-rate tokens, allowing integer or underscore-as-decimal.
# Case-insensitive for Batch 1's uppercase 'C'.
C_RATE_TOKEN_RE = re.compile(r"(\d+)(?:_(\d+))?C(?![a-zA-Z])", re.IGNORECASE)
# Handoff: integer followed by 'per' or 'PER'
HANDOFF_RE = re.compile(r"(\d+)(?:per|PER)", re.IGNORECASE)


def _decode_c_rate(match):
    """Convert regex match (int, optional decimal) to a float C-rate."""
    if match.group(2):
        return float(f"{match.group(1)}.{match.group(2)}")
    return float(match.group(1))


def parse_alt_axes(protocol_str):
    """Return dict {first_step_C, last_step_C, soc_handoff, severity}
    or {error: "..."} on parse failure.
    """
    # Body = filename after path + date prefix
    fname = re.split(r"[\\/]+", protocol_str)[-1]
    body = re.sub(r"^\d{8}[-_]?", "", fname, count=1)
    # Drop trailing extension + any trailing suffix like _newstructure.sdu
    body = re.sub(r"(?:_newstructure)?\.[sS][dD][uU]$", "", body)

    c_tokens = list(C_RATE_TOKEN_RE.finditer(body))
    if len(c_tokens) == 0:
        return {"error": f"no C-rate tokens in {body!r}"}
    first_C = _decode_c_rate(c_tokens[0])
    last_C = _decode_c_rate(c_tokens[-1])

    handoff_m = HANDOFF_RE.search(body)
    if handoff_m:
        soc_handoff = float(handoff_m.group(1))
    elif len(c_tokens) == 1:
        # Single-step protocol -- no handoff, treat as 100% (never switches)
        soc_handoff = 100.0
    else:
        return {"error": f"multi-step but no handoff token in {body!r}"}

    # Severity = SOC-weighted average C-rate
    severity = first_C * (soc_handoff / 100.0) + last_C * (1.0 - soc_handoff / 100.0)

    return {
        "first_step_C": first_C,
        "last_step_C": last_C,
        "soc_handoff": soc_handoff,
        "severity": severity,
        "error": None,
    }


def permanova_pseudoF(u_mat, labels):
    n = len(u_mat)
    norms = np.linalg.norm(u_mat, axis=1, keepdims=True)
    um = u_mat / np.where(norms < 1e-12, 1e-12, norms)
    cos_mat = um @ um.T
    cos_mat = np.clip(cos_mat, -1.0, 1.0)
    d_mat = 1.0 - cos_mat
    labels = np.asarray(labels)
    unique = np.unique(labels[labels != "NA"]) if labels.dtype.kind in ("U", "O") else np.unique(labels)
    a = len(unique)
    if a < 2 or n - a < 1:
        return float("nan")
    total_ss = float((d_mat ** 2).sum()) / (2.0 * n)
    within_ss = 0.0
    for u in unique:
        mask = (labels == u)
        n_u = int(mask.sum())
        if n_u < 2:
            continue
        sub = d_mat[np.ix_(mask, mask)]
        within_ss += float((sub ** 2).sum()) / (2.0 * n_u)
    between_ss = total_ss - within_ss
    if within_ss <= 0 or between_ss <= 0:
        return float("nan")
    return (between_ss / (a - 1)) / (within_ss / (n - a))


def permanova_test(u_mat, labels, n_perms=N_PERMS):
    F_obs = permanova_pseudoF(u_mat, labels)
    if not np.isfinite(F_obs):
        return float("nan"), float("nan")
    labels = np.asarray(labels)
    n_ge = 0
    for _ in range(n_perms):
        perm = RNG.permutation(labels)
        F_p = permanova_pseudoF(u_mat, perm)
        if np.isfinite(F_p) and F_p >= F_obs:
            n_ge += 1
    return F_obs, (n_ge + 1) / (n_perms + 1)


def axis_verdict(F_pooled, p_pooled, F_b2, p_b2):
    """Per pre-reg sec.6 falsification thresholds for an alternative axis."""
    if not np.isfinite(F_pooled) or not np.isfinite(p_pooled):
        return "AXIS NULL"
    pooled_strong = (p_pooled < ALPHA_BONFERRONI) and (F_pooled > EFFECT_F_FLOOR)
    pooled_weak = (p_pooled >= ALPHA_BONFERRONI and p_pooled < ALPHA_WEAK and F_pooled > EFFECT_F_WEAK)
    b2_ok = np.isfinite(F_b2) and np.isfinite(p_b2) and p_b2 < ALPHA_WEAK
    if pooled_strong and b2_ok:
        return "AXIS PASS"
    if pooled_strong and not b2_ok:
        return "AXIS POOLED-ONLY PASS"
    if pooled_weak:
        return "AXIS WEAK PASS"
    return "AXIS NULL"


def joint_verdict(verdicts):
    n_pass = sum(1 for v in verdicts.values() if v == "AXIS PASS")
    n_pooled = sum(1 for v in verdicts.values() if v == "AXIS POOLED-ONLY PASS")
    n_weak = sum(1 for v in verdicts.values() if v == "AXIS WEAK PASS")
    if n_pass >= 1:
        return "H5 SUPPORT"
    if (n_pooled + n_weak) >= 2:
        return "H5 WEAK"
    return "H5 NULL"


def main():
    print("=== C3 Probe 2 amendment — Severson alt-axis PERMANOVA (pre-reg literature/21) ===\n")
    df = pd.read_parquet(IN_PARQUET)
    n_total = len(df)
    print(f"Loaded {n_total} Severson cells from extraction parquet.")

    # Parse new axes (drop first_step_C from parsed output -- duplicate with extractor)
    parsed_rows = [parse_alt_axes(p) for p in df["protocol"]]
    parse_df = pd.DataFrame(parsed_rows).drop(columns=["first_step_C"], errors="ignore")
    df = pd.concat([df.reset_index(drop=True), parse_df.reset_index(drop=True)], axis=1)
    if "error" in df.columns and isinstance(df["error"].iloc[0], (str, type(None))):
        # The parse_alt_axes "error" column collides with cell-extraction "error"
        # In severson_extracted.parquet there is no "error" col, so safe.
        pass
    # parse_df has its own "error" column; rename to disambiguate
    df = df.rename(columns={"error": "parse_error"}) if "parse_error" not in df.columns else df
    n_parse_err = df["parse_error"].notna().sum()
    n_parse_ok = (df["parse_error"].isna()).sum()
    parse_fail_frac = n_parse_err / n_total if n_total > 0 else 0
    print(f"Parsing: {n_parse_ok} OK, {n_parse_err} failed ({parse_fail_frac*100:.1f}% fail rate)")
    if parse_fail_frac > 0.10:
        print(f"\nH5 INVALID: parsing failed on {parse_fail_frac*100:.1f}% > 10% pre-reg floor.")
        return
    if n_parse_err > 0:
        print("Sample parse errors:")
        for _, r in df[df["parse_error"].notna()].head(5).iterrows():
            print(f"  {r['protocol']!r}: {r['parse_error']}")

    df = df[df["parse_error"].isna()].copy()

    # Recompute residual unit vectors (same logic as literature/17)
    df = df[np.isfinite(df["fresh_Q"]) & np.isfinite(df["aged_Q"])].copy()
    df = df[np.isfinite(df["fresh_R"]) & np.isfinite(df["aged_R"])].copy()
    df = df[np.isfinite(df["fresh_T_amp"]) & np.isfinite(df["aged_T_amp"])].copy()
    print(f"After dropping NaN operators: {len(df)}\n")

    raw_resid = df[["aged_Q", "aged_R", "aged_T_amp"]].values - \
                df[["fresh_Q", "fresh_R", "fresh_T_amp"]].values
    fresh_pool = df[["fresh_Q", "fresh_R", "fresh_T_amp"]].values
    pooled_sd = fresh_pool.std(axis=0, ddof=1)
    pooled_sd = np.where(pooled_sd < 1e-12, 1e-12, pooled_sd)
    z = raw_resid / pooled_sd
    norms = np.linalg.norm(z, axis=1, keepdims=True)
    u = z / np.where(norms < 1e-12, 1e-12, norms)
    df["u1"] = u[:, 0]
    df["u2"] = u[:, 1]
    df["u3"] = u[:, 2]

    print("=== Axis distributions ===")
    for col in ["last_step_C", "soc_handoff", "severity"]:
        s = df[col]
        print(f"  {col}: min={s.min():.2f}, 33%={np.percentile(s, 33.33):.2f}, "
              f"67%={np.percentile(s, 66.67):.2f}, max={s.max():.2f}")

    # Tertile cuts per axis
    for col in ["last_step_C", "soc_handoff", "severity"]:
        s = df[col]
        t33 = float(np.percentile(s, 33.33))
        t67 = float(np.percentile(s, 66.67))
        # Handle constant-axis edge case (e.g., if all soc_handoff are equal)
        if abs(t33 - t67) < 1e-9:
            df[f"{col}_bin"] = "T2"
        else:
            df[f"{col}_bin"] = np.where(s < t33, "T1",
                                np.where(s < t67, "T2", "T3"))

    # Run per-axis PERMANOVAs
    verdicts = {}
    print("\n=== Per-axis PERMANOVAs ===")
    u_mat_all = df[["u1", "u2", "u3"]].values
    for col in ["last_step_C", "soc_handoff", "severity"]:
        bin_col = f"{col}_bin"
        print(f"\n--- {col} ---")
        counts = df.groupby(bin_col).size().to_dict()
        for t in ["T1", "T2", "T3"]:
            print(f"  {t}: n={counts.get(t, 0)}")
        F_pooled, p_pooled = permanova_test(u_mat_all, df[bin_col].values)
        print(f"  Pooled PERMANOVA: pseudo-F = {F_pooled:.3f}, p = {p_pooled:.4f}")

        # Batch-stratified (focus on Batch 2)
        F_per_batch = {}
        p_per_batch = {}
        for batch, g in df.groupby("batch_date"):
            if len(g) < 3 or g[bin_col].nunique() < 2:
                continue
            F_b, p_b = permanova_test(g[["u1", "u2", "u3"]].values, g[bin_col].values)
            F_per_batch[batch] = F_b
            p_per_batch[batch] = p_b
            print(f"  Batch {batch}: n={len(g)}, F={F_b:.3f}, p={p_b:.4f}, counts={g.groupby(bin_col).size().to_dict()}")

        F_b2 = F_per_batch.get("2017-06-30", float("nan"))
        p_b2 = p_per_batch.get("2017-06-30", float("nan"))
        v = axis_verdict(F_pooled, p_pooled, F_b2, p_b2)
        verdicts[col] = v
        print(f"  VERDICT: {v}")

    jv = joint_verdict(verdicts)
    print(f"\n=== H5 JOINT VERDICT (pre-reg literature/21 sec.6) ===")
    for col, v in verdicts.items():
        print(f"  {col}: {v}")
    print(f"\n  {jv}")

    df.to_parquet(OUT_DIR / "c3_severson_v2_results.parquet")
    print(f"\nWritten: {OUT_DIR / 'c3_severson_v2_results.parquet'}")


if __name__ == "__main__":
    main()
