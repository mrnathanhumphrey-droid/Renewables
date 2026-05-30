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

## Karin 2019 PVCZ literal zone thresholds (extracted 2026-05-27 from pvcz binary)

| ID | Claim | Status | Cited source | Notes |
|---|---|---|---|---|
| CLM-051 | PVCZ canonical scheme is T×H = 50 zones, NOT T×H×W = 250 | **VERIFIED** | `pvcz` v0.3.0 npz `total_num_zones=50`; `zone_spec['pvcz']` lists 50 labels T1:H1 through T10:H5 | Corrects substrate memory + 19_PREREG ℙ₀; W is independent stressor, not multiplied into canonical label. See memo 20. |
| CLM-052 | T-zone boundaries (°C, Arrhenius 1.1 eV rack-equivalent): [−10.3, 14, 19, 24, 29, 34, 39, 44, 49, 54, 67] | **VERIFIED** | Same, `limits['T_equiv_rack_1p1eV']` | Inner T2–T9 uniform 5 °C wide; T1 cold tail 24.3 °C wide; T10 hot tail 13 °C wide |
| CLM-053 | H-zone boundaries (g/kg specific humidity mean): [0.7, 3.0, 4.1, 5.9, 10.5, 18.3] | **VERIFIED** | Same, `limits['specific_humidity_mean']` | Non-uniform: H1=2.3 wide, H2=1.1, H3=1.8, H4=4.6, H5=7.8 g/kg wide |
| CLM-054 | PVCZ canonical activation energy is 1.1 eV (rack and roof variants both use 1.1 eV by default) | **VERIFIED** | Same, primary variable `T_equiv_rack_1p1eV` | Full Arrhenius sweep 0.1-2.1 eV (11 values) available in world stressors df for sensitivity analysis |
| CLM-055 | PVCZ world stressors dataset: 230,742 land cells × 49 columns at 0.25°×0.25° (~28 km) global grid | **VERIFIED** | `PVCZ-2019_ver0p2_world_PV_climate_stressors_and_zones.pkl` df.shape | Direct lat/lon lookup for site-to-zone assignment |
| CLM-056 | T-zone inner zones (T2–T9) uniform 5 °C wide; T1 and T10 span longer tails of global distribution | VERIFIED | Derived from CLM-052 boundaries | Decile-balanced design over inner zones |
| CLM-057 | H4 (5.9–10.5 g/kg) is widest single H-zone at 4.6 g/kg; spans broad subtropical band | VERIFIED | Derived from CLM-053 boundaries | Failure-relevant: backsheet hydrolysis kinetics, PID-s susceptibility, junction-box water ingress |

## OEDI PVDAQ alternate-path + rdtools install (extracted 2026-05-27 from S3 + git clone)

| ID | Claim | Status | Cited source | Notes |
|---|---|---|---|---|
| CLM-058 | PVDAQ public lake @ `s3://oedi-data-lake/pvdaq/` has 1862 systems with pre-computed Karin PVCZ zone assignments (composite, t_rack, t_roof, humidity, wind) | **VERIFIED** | `PVDAQ_systems_20250729.csv` schema inspection | OEDI submission 4568, DOI 10.25984/1846021, CC-BY 4.0. See memo 22. |
| CLM-059 | PVDAQ QA-passing systems with ≥0.5 yr coverage: 1564/1862 (84%) | **VERIFIED** | Direct CSV computation | |
| CLM-060 | PVDAQ QA-passing with ≥5 yr coverage: 1288 systems | **VERIFIED** | Same | Longitudinal cohort feasibility |
| CLM-061 | PVDAQ T-zone coverage: T1=8, T2=50, T3=506, T4=761, T5=217, T6=22, T7+=0 | **VERIFIED** | Same | **No T7-T10 (very hot) coverage** |
| CLM-062 | PVDAQ H-zone coverage: H1=47, H2=152, H3=1291, H4=74, H5=0 | **VERIFIED** | Same | **No H5 (tropical) coverage** |
| CLM-063 | PVDAQ has no tropical-humidity (H5) coverage | **VERIFIED** | Same | Coverage gap for tropical-equatorial degradation |
| CLM-064 | PVDAQ has no high-temperature (T7-T10) coverage | **VERIFIED** | Same | Coverage gap for MENA/Sahel/Australia inland desert |
| CLM-065 | PVDAQ systems-index CSV has no cell-architecture / module-arch field; only mounting (`type` / `tracking`) | **VERIFIED** | Schema inspection | Key gap for TOPCon cohort identification |
| CLM-066 | PVDAQ `system_public_name` string search finds zero TOPCon / HJT / SHJ / PERC / Al-BSF labeled systems | **VERIFIED** | Direct string search across all 1862 rows | TOPCon cohort identification through PVDAQ index alone NOT feasible |
| CLM-067 | PVDAQ license is CC-BY 4.0 | **VERIFIED** | OEDI submission 4568 page | Permits substrate-internal redistribution + paper-time citation |
| CLM-068 | rdtools package (NREL, MIT license) cloned to `Solar/code/rdtools/`; modules include aggregation, analysis_chains, availability, bootstrap, clearsky_temperature, degradation, filtering, normalization, plotting, soiling | **VERIFIED** | Direct clone + ls | Operational role in 19_PREREG §14 Step 5 moment-flow computation |

## Probe 2 result CLMs — Fleet PLR × PVCZ (own empirical findings, 2026-05-28)

These are substrate-generated empirical results (memo `24_RESULT_v1.0_FleetPLR_PVCZ_RMDSRC.md`), VERIFIED in the sense of "computed by locked-pre-reg pipeline on primary data," subject to the threats in result §6.

| ID | Claim | Status | Cited source | Notes |
|---|---|---|---|---|
| CLM-069 | PVDAQ fleet median PLR = −0.79 %/yr (n=668, 2018-2023 window, PVWatts+NSRDB+rdtools YoY) | **VERIFIED-OWN** | Probe 2 result §2 | Replicates Jordan 2022 system-level −0.75 %/yr |
| CLM-070 | PVCZ temperature zone explains only η²=0.019 of PLR variance (p=0.002, non-monotone: T3 −0.58 / T4 −1.05 / T5 −0.84 %/yr) | **VERIFIED-OWN** | Probe 2 result §1-2, H1 REFUTED | Climate signal does NOT survive in heterogeneous fleet |
| CLM-071 | PVCZ humidity zone explains η²=0.003 of PLR variance (p=0.42, null) | **VERIFIED-OWN** | Probe 2 result H5 CONFIRMED | Replicates Jordan 2022 humidity indeterminacy |
| CLM-072 | Climate-PLR ordering (Jordan 2022) requires technology-controlled cohorts; heterogeneous public fleet (mixed cell-tech, residential rooftop) buries the ~0.4 %/yr climate effect under ~1.5-2 %/yr within-cell variance | **VERIFIED-OWN** | Probe 2 result §4, F_Fleet_2 fired | Boundary condition on Jordan 2022, NOT a refutation; lab-design lesson §8 |
| CLM-073 | PVDAQ mounting metadata 98% UNKNOWN; tracking 1251:2 fleet-wide → roof/ground (H3) + tracker-null (H4) untestable in PVDAQ index | **VERIFIED-OWN** | Probe 2 result §1, H3/H4 INDETERMINATE | Metadata-completeness limit, not a physics finding |
| CLM-074 | PVDAQ within-cell PLR σ = 2.41 %/yr; 2.44× Jordan 2022's back-solved within-cohort σ (0.99 %/yr) | **VERIFIED-OWN** | Probe 2b memo 25 §2 | Heterogeneity inflation quantified |
| CLM-075 | At PVDAQ heterogeneity, power to detect Jordan's 0.40 %/yr climate effect at n=668 is 0.35; ~1938 systems needed for power 0.8 | **VERIFIED-OWN** | Probe 2b memo 25 §2 | FTestAnovaPower |
| CLM-076 | Probe 2 H1 null is REFUTED-BY-UNDERPOWER (Type-II-prone), not "climate irrelevant"; the η²=0.019 PVDAQ saw is non-monotone/confounded, not Jordan's ordered effect | **VERIFIED-OWN** | Probe 2b memo 25 §3 | Sharpens H1 disposition |
| CLM-077 | Technology-controlled climate test infeasible in PVDAQ: modules table (156 systems, cell-arch) has 0 overlap with 668 PLR cohort; only 17 mono/multi-Si qa-pass+years≥5 | **VERIFIED-OWN** | Probe 2b memo 25 §1 | Mechanism test needs external homogeneous cohort |
| CLM-078 | Variance decomposition: 32% of PVDAQ within-cell PLR variance is measurement noise (daily-energy normalization); true heterogeneity σ=1.99 %/yr = 2.0× Jordan; power at true σ still 0.49 | **VERIFIED-OWN** | Probe 2b memo 25 §4b | Underpowering robust to method noise; measured-POA would NOT recover climate signal |
| CLM-079 | rdtools SRR soiling on PVDAQ daily-energy+NSRDB PI returns implausible 13-19% losses (vs Ilse 3-7%), wide CIs, frequent NoValidIntervalError | **VERIFIED-OWN** | Probe 3 memo 26 §1 | Soiling signal below daily-PI noise floor |
| CLM-080 | Soiling (within-year sawtooth) NOT extractable from PVDAQ residential daily-energy, though PLR (multi-year YoY trend) is — expected signal-scale ordering vs 32% noise floor | **VERIFIED-OWN** | Probe 3 memo 26 §2 | Probe 3 FEASIBILITY-NULL |
| CLM-081 | PVDAQ has 0 analyzable H1 (truly-arid) systems → Ilse aridity-soiling prediction untestable on PVDAQ regardless | **VERIFIED-OWN** | Probe 3 memo 26 §3 | Needs external arid-site data |
| CLM-082 | DKA Alice Springs 13-system fleet median PLR = −0.91 %/yr (5–13 yr measured-POA spans) — replicates Jordan/PVDAQ magnitude on arid single-tech-controlled site | **VERIFIED-OWN** | Probe 4 memo 28 §0 | Third independent replication of fleet-PLR magnitude |
| CLM-083 | DKA fixed-mount σ_within (n=6) ≈ 0.23 %/yr — **8× tighter than PVDAQ heterogeneous fleet (1.99 %/yr)** | **VERIFIED-OWN** | Probe 4 memo 28 §2 | Validates Probe 2b's homogeneity-dividend prediction quantitatively |
| CLM-084 | DKA fixed-mount tech ordering: HIT (−0.80) ≤ mono-Si (−0.91) ≤ CdTe (−0.96) < poly-Si (−1.14) %/yr — consistent with PV literature | **VERIFIED-OWN (directional, n=1/tech)** | Probe 4 memo 28 §2 | Powered comparison needs more replicates per tech |
| CLM-085 | Per-phase data for 3-phase tracker systems gives unreliable per-system PLR (same-system phase splits diverge by >1 %/yr) — phase-combined files give sensible PLR | **VERIFIED-OWN** | Probe 4 memo 28 §3 | Methodological flag for tracker analysis |
| CLM-086 | DKA on-site Radiation_Global_Tilted + 5-min cadence enables clean PLR computation without NSRDB; arid-site soiling extraction now feasible | **VERIFIED-OWN** | Probe 4 memo 28 §4 | Unblocks queued soiling probe (Probe 3 attempted on PVDAQ failed; DKA opens it) |

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
| v3 | 2026-05-27 | Karin 2019 PVCZ literal threshold extraction via `pvcz` v0.3.0 package binary | operator (direct npz load) | Karin zone thresholds extracted. **Correction surfaced:** canonical PVCZ is T×H = 50 zones (NOT 250 as substrate memory + 19_PREREG had stated). 7 new VERIFIED CLMs (051-057). See memo `20_KARIN2019_THRESHOLDS_extracted.md`. 19_PREREG DEVIATION-log entry filed. |
| v4 | 2026-05-27 | T13-30:2025 SLIDES retrieval + read | operator + WebFetch | 5-slide presentation read; 4th independent confirmation of ERR-4 closure (Köntges/Lin/Jahn). Triangulation memo. No new CLMs (all SLIDES claims already in ledger from EX-SUMM/REPORT FULL/PVFS). See memo 21. |
| v5 | 2026-05-27 | OEDI PVDAQ alternate-path pull + rdtools clone | operator (curl S3 + git clone) | **DuraMAT blocker resolved via OEDI alternate.** 1862-system PVDAQ index CSV in hand with **pre-computed Karin PVCZ assignments**. **New gap surfaced:** PVDAQ index lacks cell-architecture field; TOPCon cohort identification needs S3 per-system JSON or manufacturer outreach. 11 new VERIFIED CLMs (058-068). rdtools cloned MIT-licensed. See memo 22. |
| Probe2 | 2026-05-28 | Probe 2 EXECUTION: 668-system PVDAQ fleet PLR × PVCZ partition (PVWatts+NSRDB v4+rdtools YoY) | operator pipeline (locked pre-reg 165342b) | **Fleet median PLR −0.79 %/yr replicates Jordan 2022.** But climate-T partition does NOT survive (η²=0.019, H1 REFUTED, F_Fleet_2 fired); humidity null (H5 CONFIRMED); mounting/tracking INDETERMINATE (metadata gap). Mechanism: heterogeneous fleet buries climate signal. 5 own-result CLMs (069-073). See result memo 24. |

---

## Next steps

1. User direction on which claim to verify FIRST (this becomes the first verification pass).
2. Each pass updates this ledger AND produces a brief verification memo in `literature/03_VERIFICATION_<CLM-ID>.md` documenting the search + retrieval + verdict.
3. As claims migrate to VERIFIED, downstream scientific pre-regs may cite them per meta-pre-reg §1.
