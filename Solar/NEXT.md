# Next Session — Pickup Pointer (Solar Substrate)

**Locked:** 2026-05-27 at HEAD `050e9aa` on `main`, github.com/mrnathanhumphrey-droid/Renewables.
**Last session ended:** First scientific pre-reg `19_PREREG_v1.0_TOPCon_UVID.md` LOCKED at `fc32be4`. Substrate scaffolded with strict pre-reg + anti-LLM evidence discipline; 9 anchor papers verified; 5 attribution errors caught in v0 LLM-written landscape docs.

---

## 0. Where things stand — substrate state

| Layer | Status | Doc(s) |
|---|---|---|
| Substrate root | LIVE | `Solar/README.md` |
| Meta-pre-reg (evidence discipline) | **LOCKED** at fc32be4 | `01_METAPREREG_v1.0_evidence_discipline.md` |
| Claims ledger | LIVE; 50+ entries | `02_CLAIMS_LEDGER.md` |
| RMD-SRC × solar framing | NEEDS-VERIFICATION (operator endorsement pending) | `03_RMDSRC_SOLAR_FRAMING_v0.md` |
| v0 landscape docs | DEMOTED + per-axis correction banners | `00` + `04` + `05` + `06` |
| Verification memos (9 anchors) | LIVE | `07_` through `18_` + `12_` summary |
| First scientific pre-reg | **LOCKED** at fc32be4 | `19_PREREG_v1.0_TOPCon_UVID.md` |
| Local PDFs (gitignored) | 10 papers in `Solar/data/raw/papers/` | — |
| DuraMAT fleet dataset | BLOCKED (NREL SSL/TLS) | metadata-only CSV in `Solar/data/raw/datasets/` |

## 1. What was done this session — punch list

1. Substrate scaffold (Solar/{README.md, literature/, code/, data/{raw/{papers, datasets, nrel, ...}}})
2. Meta-pre-reg v1.0 LOCKED — anti-LLM provisions explicit; LLM outputs NEVER count as primary evidence
3. v0 landscape (00) DEMOTED with banner; all numeric claims → NEEDS-VERIFICATION
4. 22-claim CLM ledger built from v0 doc; subsequently expanded with 28 new VERIFIED CLMs from pass v2
5. RMD-SRC × solar framing doc (03) mapping algorithm inputs to solar data sources
6. 3 axis-specific landscape docs (degradation 04 / reliability 05 / siting-yield 06) with per-axis correction banners
7. Verification pass v1 — 5 parallel subagents on canonical anchors
8. Verification pass v2 — Jordan 2016 Compendium + Köntges 2025 T13-30 (PVFS + EX-SUMM + REPORT FULL) + Jordan 2022 fleet + Karin 2019 PVCZ
9. First scientific pre-reg `19_PREREG_v1.0_TOPCon_UVID.md` drafted + LOCKED
10. WebFetch permissions expanded in `~/.claude/settings.json` for 28 academic hosts + 13 additional after EX-SUMM-retrieval host issues surfaced

## 2. 5 attribution errors caught in v0 (closed by primary-source verification)

| ID | v0 said | Actually |
|---|---|---|
| ERR-1 | "c-Si median 0.5%/yr" cited Jordan-Kurtz 2013 | 0.5%/yr is **all-tech** median; c-Si qualifier added by v0 LLM |
| ERR-2 | "c-Si mean 0.8-0.9%/yr" cited Jordan-Kurtz 2013 | Originates in **Jordan 2016 Compendium** (DOI 10.1002/pip.2744) |
| ERR-3 | "soiling 3-7%/yr arid" cited Ilse 2019 | Ilse's 3-4% is **global aggregate** current loss; 4-7% projected global 2023 |
| ERR-4 | "Jahn et al. T13-09:2017" | Lead author is **Köntges**; Jahn is 3rd |
| ERR-5 | "climate-specific aging established" cited Köntges 2017 | T13-09:2017 found **no strong** correlation at 2017 N. **OVERTURNED by Jordan 2022 at p<0.001** for temperature axis (Al-BSF c-Si ground-mount fleet, n=1528 inv) |

## 3. 9 verified anchor papers (with DOIs)

1. Jordan & Kurtz 2013, *Prog. Photovolt.* — DOI 10.1002/pip.1182. NREL preprint local. **Local PDF.**
2. Jordan 2016 Compendium, *Prog. Photovolt.* — DOI 10.1002/pip.2744. OSTI 1259256. **Operator-pulled local.**
3. **Jordan 2022 PV Fleet, *Prog. Photovolt.* — DOI 10.1002/pip.3566.** NREL fy22osti/81314.pdf. CLOSES ERR-5. **Local.**
4. Köntges 2017 T13-09 IEA-PVPS — ISBN 978-3-906042-54-1. Open-access PDF on iea-pvps.org. **Local.**
5. Köntges 2025 T13-30 PVFS Annex — failure fact-sheet digest, 30 modes. **Local.**
6. Köntges 2025 T13-30 REPORT EX-SUMM — 3pp Köntges25 executive. **Local.**
7. **Köntges 2025 T13-30 REPORT FULL — 68pp technical body.** Fraunhofer CSP mirror. **Local.**
8. Sengupta 2018 NSRDB, *RSER* — DOI 10.1016/j.rser.2018.03.003. **Local.**
9. Holmgren 2018 pvlib, *JOSS* — DOI 10.21105/joss.00884. CC-BY. **Local.**
10. Ilse 2019, *Joule* — DOI 10.1016/j.joule.2019.08.019. DLR open. **Local.**
11. **Karin 2019 PVCZ**, *IEEE PVSC-46* — DOI 10.1109/PVSC40753.2019.8980831. **Local.** Open-source `pvcz` package on GitHub.

(11 papers total — original ledger said "9 anchors" but counting individual papers reaches 11.)

## 4. First scientific pre-reg headline (19_PREREG_v1.0)

**Scope:** TOPCon-cell c-Si modules with ≥6 months outdoor field exposure.
**Question:** Does TOPCon UVID admit RMD-SRC partition into clean trajectory regimes?

**ℙ₀ axes** (locked exogenous categoricals):
- Manufacturer × Encapsulation × Vintage × Karin PVCZ T-zone × Karin H-zone × Mounting

**Observable vector x_j** (10-dimensional):
- Electrical: yield, Isc, Voc, FF, Rs (annual)
- Diagnostic: EL defect fraction, spectral response loss
- Environmental gradient: UV dose, T×time, humidity (monthly)

**5 hypotheses with falsification gates:**
- **H1** Encapsulation dominates UVID variance (η²>0.30) — T13-30 §2.6.1 Sen et al. 4-65% DH variance
- **H2** Hot-climate Concentrating (boson) regime ≥40% (batch-cohort reinforcement)
- **H3** Field rate 2-10× LOWER than lab 60 kWh/m² test (MPP-vs-short-circuit gap)
- **H4** Manufacturer η²>0.50 after controls
- **H5** Manufacturer × climate interaction BF>10

**7 falsifiers:**
- RMD universal F1-F4 (partition cleanness, decomposition convergence, validation agreement, predictive transfer r<0.4)
- Substrate-specific F_TOPCon_1 (no-signal), F_TOPCon_2 (encapsulation null), **F_TOPCon_3 (field-exceeds-lab inversion = publish immediately)**

**Termination:** n_c ≥ 50 per leaf; σ²_residual ≤ 0.25·σ²_marginal; ≥24 monthly bins.

## 5. Blockers carried forward

1. **DuraMAT Fleet Insights CSV (DOI 10.21948/1842958)** — NREL SSL/TLS host issue. Only OSTI citation metadata captured. Alternates: OEDI PVDAQ (`data.openei.org/submissions/4568`); `duramat-help@nrel.gov` for non-NREL mirror; or SSL fix on NREL side.
2. **Karin 2019 zone thresholds (literal °C and g/kg)** — in `PVCZ-2019_ver0p2_zones.npz` binary in the pvcz repo OR PDF tables. Operator-runnable: `pip install pvcz` then `np.load('...zones.npz')`.
3. **T13-30:2025 SLIDES** — not yet retrieved (iea-pvps.org URL known).
4. **TOPCon field cohort identification** — DuraMAT blocked; PVDAQ has limited TOPCon n; manufacturer/RTC partnerships needed.

## 6. Operational protocol on resume (per 19_PREREG §14)

1. **Operator endorsement** of pre-reg v1.0 if any revisions surface; otherwise proceed.
2. **Cohort identification** — TOPCon-cell modules with ≥6 months field exposure.
3. **ℙ₀ partition assignment** from exogenous categoricals only. No outcome inspection.
4. **Observable data acquisition** — monthly x_1, x_8-x_10; annual x_2-x_6.
5. **Step 1** moment-flow computation per RMD-SRC algorithm.
6. **Step 2-6** trajectory classification → response-function validation → sub-decomposition if not-clean → termination → cross-cell mechanism inference.
7. **Hypothesis verdicts** H1-H5 + F1-F7 per §12.
8. **Write up** `result_v1.0_TOPCon_UVID_RMDSRC.md`.

## 7. Discipline patterns established this session

1. **Meta-pre-reg lock BEFORE any content writing** — caught v0 doc as LLM-generated NEEDS-VERIFICATION rather than treating as fact.
2. **LLM outputs explicitly disallowed as primary sources.** Bibliographic claims from LLMs require double-verification (cite exists + claim appears in cite). LLMs hallucinate citations.
3. **Verification memo per anchor citation** — produces a per-paper NEEDS-VERIFICATION → VERIFIED audit trail. Each memo cites the operator + retrieval method + section/page refs.
4. **Pre-reg LOCK SHA convention** — file pre-reg with placeholder, commit (gets SHA), second commit fills SHA in placeholder; from that second commit forward the pre-reg is immutable.
5. **Falsifier prominence** — both RMD-SRC universal F1-F4 AND substrate-specific F_TOPCon_x falsifiers are listed; field-exceeds-lab inversion is pre-registered as research-area-critical disposition.

## 8. Repository state

- Branch `main` at `050e9aa`. Up-to-date with origin/main (push deferred to operator action).
- 2 commits this session: `fc32be4` (Solar v1 substrate scaffold + literature + pre-reg) + `050e9aa` (lock-SHA fill).
- Battery substrate at unrelated WIP `Battery/code/c3_probe8d_test_statistic.py` — left untouched.
- All Solar/data/* gitignored except OSTI metadata CSV; 10 PDFs in data/raw/papers/ local only.

## 9. Memory pointers for next-session recall

- Topic: Solar PV-panel research lab / Resolve Research substrate
- Repo: github.com/mrnathanhumphrey-droid/Renewables (subdir Solar/)
- Last commit on lock: `050e9aa` (lock SHA fc32be4)
- Methodology core: RMD-SRC algorithm (Humphrey May 2026; spec at `D:/Resolve Research/RMD SRC Algorithm Specification.docx`)
- Evidence discipline: meta-pre-reg LLM-output-disallowed; 30-min verification budget; 5 knowledge-state labels
- First scientific pre-reg topic: TOPCon UVID field cohort RMD-SRC application
- Open thread: Karin 2019 zone-threshold extraction + DuraMAT dataset alternate-path pull + TOPCon field cohort identification
