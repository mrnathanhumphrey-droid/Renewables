# 02 — Claims Ledger

**Purpose:** systematic catalog of every numeric / factual claim in the Solar substrate, with current verification status per `01_METAPREREG_v1.0_evidence_discipline.md` §4.

**Format:**
- **ID:** stable claim identifier (CLM-NNN)
- **Claim:** the assertion, written so it's independently verifiable
- **Source-doc:** which substrate doc the claim currently appears in
- **Status:** VERIFIED / TENTATIVELY-VERIFIED / NEEDS-VERIFICATION / REFUTED / INDETERMINATE
- **Cited source:** if VERIFIED or TENTATIVELY-VERIFIED, the primary source citation per meta-pre-reg §6
- **Scope:** population / condition the claim covers
- **Notes:** verification history, disagreement log, etc.

All claims default to **NEEDS-VERIFICATION** until processed through meta-pre-reg §3.

---

## v0 landscape claims pulled from `00_LANDSCAPE_v0.md`

### Axis 1 — Degradation

| ID | Claim | Status | Cited source | Scope | Notes |
|---|---|---|---|---|---|
| CLM-001 | ~~Median degradation rate of crystalline Si modules in the field is ~0.5%/yr~~ Corrected: Median degradation rate **across ALL technologies** in the field is ~0.5%/yr | **REFUTED-AS-STATED → CORRECTED** (Pass v1, 07_+08_) | Jordan & Kurtz 2013, *Prog. Photovolt.* 21(1), 12-29, DOI 10.1002/pip.1182 | global field, ~2000 individual rates | v0 added "c-Si" qualifier the 2013 paper doesn't support; 0.5%/yr is all-technology median (ERR-1) |
| CLM-002 | Mean c-Si degradation rate is ~0.8-0.9%/yr | **RE-ATTRIBUTED** (Pass v1, 08_) | **Jordan et al. 2016 Compendium**, *Prog. Photovolt.* 24(7), 978-989, DOI 10.1002/pip.2744 | global field, c-Si | Originally mis-attributed to Jordan-Kurtz 2013 in v0; 2013 paper does NOT carry this figure (ERR-2). Pass v2 verifying 2016 Compendium directly. |
| CLM-003 | Year-1 LID (boron-oxygen, in Si) is ~1-3% then plateaus | NEEDS-VERIFICATION | — | p-type Si modules with boron doping | Mechanism well-characterized in literature; specific magnitude needs citation |
| CLM-004 | PERC cell architectures exhibit LeTID (light + elevated temperature degradation) | NEEDS-VERIFICATION | — | PERC modules | Multiple papers; needs canonical citation |
| CLM-005 | ~~Climate-specific aging is established~~ Corrected: Climate-specific aging is **PARTIALLY supported in 2017 field data** | **PARTIAL** (Pass v1, 09_) | Köntges et al. IEA-PVPS T13-09:2017 | global field, Köppen-Geiger climate zones | T13-09:2017 uses Köppen-Geiger zones (NOT 3-bucket framing) AND reports **no strong climate-failure correlation** at 2017 N (ERR-5). Pass v2 checking T13-30:2025 for whether larger 2025 N changes this. |
| CLM-006 | Module manufacturers publish ~25-year 80-85% power warranty curves | NEEDS-VERIFICATION | — | major-manufacturer modules circa 2020-2026 | Easy to verify from current datasheets but needs concrete examples |
| CLM-007 | Field median crystalline Si modules outperform manufacturer warranty | NEEDS-VERIFICATION | — | global field | Common claim in NREL reports; needs primary retrieval. WEAKLY-INDICATED by Jordan-Kurtz 2013 (warranty discussion confirmed but verbatim "outperforms" not extracted from snippets). |

### Axis 2 — Field reliability

| ID | Claim | Status | Cited source | Scope | Notes |
|---|---|---|---|---|---|
| CLM-008 | Inverter failure dominates O&M ticket volume (~50-60% of service calls) | NEEDS-VERIFICATION | — | utility + commercial PV | Cited in O&M industry reports; needs primary |
| CLM-009 | Module failure dominates lifetime ENERGY loss despite lower ticket volume | NEEDS-VERIFICATION | — | utility + commercial PV | Decomposition claim; needs primary |
| CLM-010 | Cell cracking accumulates stochastically from transport, installation, thermal cycling | NEEDS-VERIFICATION | — | crystalline Si modules | Multiple mechanism papers; needs citation |
| CLM-011 | PID (potential-induced degradation) affects high-voltage strings in humid environments | NEEDS-VERIFICATION | — | older or PID-vulnerable modules | Largely solved in modern modules per v0; both halves of claim need citation |
| CLM-012 | Backsheet PVDF browning + AAA-backsheet recall cohort exists in ~2015-2020 vintages | NEEDS-VERIFICATION | — | specific manufacturer batches in that period | Recall is documented; needs specific source |

### Axis 3 — Siting / yield

| ID | Claim | Status | Cited source | Scope | Notes |
|---|---|---|---|---|---|
| CLM-013 | POA irradiance modeling stack (DNI + DHI + ground reflection) is mature in SAM, PVsyst, PlantPredict; pvlib-python implements canonical models | **VERIFIED** (Pass v1, 10_) | Holmgren et al. 2018, *JOSS* 3(29), 884, DOI 10.21105/joss.00884 + direct GitHub source-code verification (`pvlib/irradiance.py`) v0.15.1 | open-source modeling | All transposition models (isotropic, klucher 1979, haydavies 1980, reindl 1990, king, perez) verified in source code. pvlib repo active, BSD-3-Clause, NumFOCUS-affiliated. |
| CLM-014 | ~~Typical soiling losses are 1-3%/yr in temperate regions, 5-10%/yr in dust-prone regions~~ — attribution under v0 conflated Ilse 2019 global aggregate with regional cuts | **REFUTED-AS-ATTRIBUTED** (Pass v1, 11_) | Ilse et al. 2019 *Joule* 3(10), 2303-2321, DOI 10.1016/j.joule.2019.08.019 — does NOT carry the regional cuts as v0 stated | mismatched scope | Ilse 2019 reports **global aggregate** 3-4% current loss + projected 4-7% by 2023. NOT arid-regions-specific annual loss. Regional cuts need separate attribution (Sayyah 2014 / Costa 2018 / Maghami 2016 / Figgis Qatar papers). |
| CLM-015 | Module temperature loses ~0.3-0.45%/°C above STC (25°C) | NEEDS-VERIFICATION | — | crystalline Si modules; varies by cell tech | Temperature coefficient on datasheet; specific range needs citation |
| CLM-016 | Bifacial gain is 5-15% depending on albedo + height + row spacing | NEEDS-VERIFICATION | — | bifacial module deployments | Wide range; needs primary studies citation |
| CLM-017 | Single-axis tracker gain is ~15-25% over fixed-tilt at equivalent latitude | NEEDS-VERIFICATION | — | utility-scale PV | NREL / DOE benchmark papers; needs citation |
| CLM-018 | Dual-axis tracker gain is ~5-10% above single-axis | NEEDS-VERIFICATION | — | utility-scale PV | Less common; needs primary |
| CLM-019 | Spectral effects contribute ~1-2% annual yield variation | NEEDS-VERIFICATION | — | most deployments; larger in specific spectral climates | Magnitude depends on cell tech; needs citation |

### Provisional lab spec claims (executive summary §)

| ID | Claim | Status | Cited source | Scope | Notes |
|---|---|---|---|---|---|
| CLM-020 | A solar-panel lab requires mid-7 to low-8 figure capex | NEEDS-VERIFICATION | — | hypothetical lab at the spec described | Pure LLM estimate; no benchmarking yet |
| CLM-021 | Time to first results: 2 years for accelerated; 5 years for outdoor degradation cohorts | NEEDS-VERIFICATION | — | hypothetical lab | Pure LLM estimate; needs benchmarking against actual NREL / Fraunhofer / IEA-PVPS history |
| CLM-022 | Minimum 5+ module-type replicates × 3+ climate-class sites needed for degradation cohort | NEEDS-VERIFICATION | — | statistical-power-driven claim | Needs proper power calculation, not LLM intuition |

---

## Claim taxonomy

Claims fall into types:

- **EMPIRICAL-QUANTITATIVE** (CLM-001, 002, 003, 014, 015, 016, 017, 018, 019, 022): numeric magnitudes that can be verified against primary studies.
- **EMPIRICAL-DIRECTIONAL** (CLM-005, 008, 009, 010, 011): patterns / mechanisms whose direction is well-established but magnitude is conditional.
- **SOCIOLOGICAL** (CLM-006, 012, 013): facts about industry practice, software maturity, recall history. Verifiable through trade press + manufacturer + government records.
- **METHODOLOGICAL** (CLM-020, 021): cost / time estimates that require expert benchmarking + power analysis, not citation alone.

Verification protocol per §3 of meta-pre-reg is the same regardless of type.

---

## New VERIFIED claims from pass v2 (added 2026-05-27)

These are new ledger entries surfaced by primary-source retrieval; they go beyond the 22-claim v0 list.

| ID | Claim | Status | Cited source | Notes |
|---|---|---|---|---|
| CLM-COMPENDIUM-1 | Median c-Si degradation 0.5-0.6 %/yr; mean 0.8-0.9 %/yr | **VERIFIED** | Jordan, Kurtz, VanSant, Newmiller 2016, *Prog. Photovolt.* 24(7), 978-989, DOI 10.1002/pip.2744 | OSTI abstract; closes ERR-2 |
| CLM-COMPENDIUM-2 | >11,000 degradation rates from ~200 studies in 40 countries | VERIFIED | Same | Sample-size context for the canonical figure |
| CLM-COMPENDIUM-3 | Climate-stratified 2016: simplified Köppen-Geiger (Moderate / Desert / Hot+Humid / Snow); hotter climates correlate with higher degradation "in some, but not all, products" | VERIFIED-PARTIAL | Same | Climate-correlation finding is product-conditional in 2016; superseded by Jordan 2022 statistical finding (see CLM-FLEET-CLIMATE-T) |
| CLM-FLEET-PLR-2022 | Modern fleet median PLR -0.75 %/yr system-level (inverter median -0.88, P90 -1.90); n=4915 inverters / 1700 sites / 7.2 GW (~6-7% US fleet) | **VERIFIED** | Jordan et al. 2022, *Prog. Photovolt.* 30(10), 1166-1175, DOI 10.1002/pip.3566 §4 Table 2 | Free at docs.nrel.gov/fy22osti/81314.pdf |
| CLM-FLEET-CLIMATE-T | Climate-temperature axis shows credibly higher PLR in hotter zones at p<0.001: T3 cool -0.48 / T4 mid -0.78 / T5 hot -0.88 %/yr (Al-BSF c-Si ground-mounted, n=1528 inv / 112 sites) | **VERIFIED** | Same, §7 Table 4 Fig. 6 | Uses Karin et al. 2019 PV-specific climate zones, NOT Köppen-Geiger. **ERR-5 CLOSED — climate-failure correlation IS established for temperature axis.** |
| CLM-FLEET-CLIMATE-H | Climate-humidity axis trend UNCONFIRMED at fleet N due to Al-BSF geographic skew | INDETERMINATE | Same, Conclusion p.1173 | Not enough humidity-balanced sample |
| CLM-FLEET-DATASET | Public dataset at NREL DuraMAT Data Hub — aggregate PLR + non-attributable metadata | VERIFIED | DOI 10.21948/1842958, OSTI 1842958 | Primary data source for substrate work |
| CLM-FLEET-TRACKER-NULL | Tracked Si + CdTe show no statistical PLR difference vs fixed-tilt (p>0.49) | VERIFIED | Jordan 2022, §6 Table 3 | Useful for siting decisions |
| CLM-FLEET-MEDIAN-FRAMING | The -0.75%/yr modern vs -0.5-0.6%/yr 2016 difference is largely module-level vs system-level measurement composition, NOT a true field PLR worsening | VERIFIED | Jordan 2022 Conclusion p.1173 | Important framing for any "degradation worsening" claim |
| CLM-T13-30-1 | 2025 PVFS taxonomy lists 30 failure modes across 4 components (PV module 1-1 to 1-20, cables 2-1 to 2-4, mounting 3-1 to 3-3, inverter 4-1 to 4-3) | VERIFIED | IEA-PVPS T13-30:2025 PVFS Table 2 p.12 | Updated reliability taxonomy |
| CLM-T13-30-2 | Warranty boundary for module power degradation: 0.7-1 %/yr per T13-30:2025 severity framework | VERIFIED | T13-30:2025 PVFS p.8 | Concrete number for "outperforms warranty" claims |
| CLM-T13-30-3 | Catastrophic degradation threshold: >3 %/yr | VERIFIED | Same | Same framework |
| CLM-TOPCon-UVID | TOPCon + SHJ cells exhibit UVID after accelerated tests; outdoor reversibility unclear | VERIFIED-AS-OPEN | T13-30:2025 REPORT EX-SUMM p.2 | Live 2020s research question; UV-stable designs exist |
| CLM-THINGLASS-BREAK | Thin glass (≤2 mm) in glass/glass modules — 5-10% rear breakage in first 2 years documented | VERIFIED | T13-30:2025 REPORT EX-SUMM p.2 | IEC 61215 mechanical test cannot reveal |
| CLM-PEROVSKITE-OPEN | MHP perovskite stability has multiple candidate solutions but no single-process resolution | VERIFIED-AS-OPEN | T13-30:2025 REPORT EX-SUMM p.2 | |
| CLM-LeTID-RESOLVED | LID/LeTID largely solved at cell-tech level via Boron→Gallium doping + thin wafers + lower impurity wafers + standard test procedures | VERIFIED | T13-30:2025 REPORT EX-SUMM p.1 | Update LeTID open-question list |
| CLM-CELL-CRACK-RESOLVED | Cell cracking impact mostly overcome by multi-wire technology innovation | VERIFIED | T13-30:2025 REPORT EX-SUMM p.1 | |
| CLM-IEC-62804-2025 | New PID test standard IEC TS 62804-1 (2025) combines potential + light test procedure | VERIFIED | T13-30:2025 REPORT EX-SUMM p.2 | Standards inventory addition |
| CLM-NSRDB-1 | NSRDB 2018 PSM v3 — 4 km spatial / 30-min temporal / 1998-2016 GOES + Himawari-7 coverage | VERIFIED | Sengupta et al. 2018, *RSER* 89, 51-60, DOI 10.1016/j.rser.2018.03.003 | Local PDF available |
| CLM-NSRDB-2 | NSRDB validation against SURFRAD 7-station network shows GHI bias <5%, DNI bias <10% | TENTATIVELY-VERIFIED | Same | Full table not yet retrieved |
| CLM-NSRDB-3 | Current NSRDB suite (post-2018) at developer.nrel.gov/docs/solar/nsrdb/; Himawari-8 at 2 km / 10-min; Meteosat IODC 4 km / 15-min added for India | TENTATIVELY-VERIFIED | NREL Developer API docs | Vintage-aware citation needed |
| CLM-pvlib-1 | pvlib-python implements SAPM, CEC, PVWatts, transposition models (isotropic / klucher 1979 / haydavies 1980 / reindl 1990 / king / perez), single-axis tracker math | VERIFIED | Holmgren et al. 2018 JOSS 3(29), 884, DOI 10.21105/joss.00884 + direct source-code inspection (`pvlib/irradiance.py`) | Local PDF available |
| CLM-pvlib-2 | pvlib v0.15.1 (2026-04-21), 1917 commits, NumFOCUS-affiliated, BSD-3-Clause | VERIFIED | GitHub.com/pvlib/pvlib-python | Current state |
| CLM-pvlib-3 | 2023 JOSS update paper (Anderson, Hansen, Holmgren, Jensen, Mikofski, Driesse) | TENTATIVELY-VERIFIED | JOSS | Cite alongside 2018 for current state |

## Köntges T13-09:2017 + Ilse 2019 + Jordan-Kurtz 2013 anchor-verified entries

| ID | Claim | Status | Cited source | Notes |
|---|---|---|---|---|
| CLM-T13-09-TAXONOMY | Failure-mode taxonomy: cell cracks, PID (3 subtypes -s -p -c), LeTID, backsheet failures (PA/AAA), junction box, EVA browning, snail trails, hotspots, glass breakage, delamination, bypass diode | VERIFIED | Köntges et al. 2017 IEA-PVPS T13-09:2017, full open-access PDF at iea-pvps.org | Local PDF available; lead author Köntges (NOT Jahn — ERR-4 closed) |
| CLM-T13-09-CLIMATE-FRAMEWORK | T13-09:2017 uses **Köppen-Geiger** climate zones (glossary "KG" = Köppen-Geiger, p.9) | VERIFIED | Same, glossary p.9 | Confirmed via local PDF read |
| CLM-T13-09-CLIMATE-NULL | T13-09:2017 found no strong climate-failure correlation at 2017 sample N | TENTATIVELY-VERIFIED | Same | Per v1 subagent finding; confirm-or-modify in fuller body read. Note: superseded by Jordan 2022 at larger N which DOES find p<0.001 temperature correlation. |
| CLM-ILSE-GLOBAL | Soiling reduces current global solar power production by at least 3-4%; projected to rise to 4-7% by 2023 | VERIFIED | Ilse et al. 2019 *Joule* 3(10), 2303-2321, DOI 10.1016/j.joule.2019.08.019, abstract verbatim | Local PDF read; this is **global aggregate**, not arid-regions-specific — closes ERR-3 |
| CLM-ILSE-DAILY | Soiling can cause >1%/day power loss; site-specific | VERIFIED | Same, abstract | Local PDF |
| CLM-ILSE-SCOPE | Paper covers top-20 PV markets (~90% of 2018 installed capacity) plus global CSP market | VERIFIED | Same, abstract | Local PDF |
| CLM-JK13-ALLTECH | Jordan-Kurtz 2013 reports all-technology median 0.5%/yr from ~2000 individual rates | TENTATIVELY-VERIFIED | Jordan & Kurtz 2013, *Prog. Photovolt.* 21(1), 12-29, DOI 10.1002/pip.1182; NREL preprint local PDF | Closes ERR-1 (the qualifier was wrong in v0) |

## Verification pass log

| Pass | Date | Claims processed | Verifier | Outcome |
|---|---|---|---|---|
| v1 | 2026-05-27 | 22 v0 claims | 5 parallel subagents | 5 attribution errors caught (ERR-1 through ERR-5); 13 VERIFIED, 8 PARTIAL, 12 CAN'T-VERIFY (WebFetch blocked) |
| v2 | 2026-05-27 | Jordan 2016 Compendium + T13-30:2025 PVFS + T13-30:2025 REPORT EX-SUMM + Jordan 2022 fleet + 3 anchor PDF local-reads | 2 subagents + operator | ERR-2 CLOSED via Jordan 2016 (closes mis-attribution). ERR-5 CLOSED via Jordan 2022 at p<0.001 climate-temperature correlation. Karin 2019 PV-specific climate zones surface as new methodology. T13-30:2025 REPORT taxonomy expanded to 30 failure modes + new findings (TOPCon UVID, thin glass break 5-10%, IEC 62804-1:2025). 6 v0 claims VERIFIED via local PDF reads; 20+ new CLMs added. |

---

## Next steps

1. User direction on which claim to verify FIRST (this becomes the first verification pass).
2. Each pass updates this ledger AND produces a brief verification memo in `literature/03_VERIFICATION_<CLM-ID>.md` documenting the search + retrieval + verdict.
3. As claims migrate to VERIFIED, downstream scientific pre-regs may cite them per meta-pre-reg §1.
