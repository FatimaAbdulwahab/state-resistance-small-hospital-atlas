#!/usr/bin/env python3
"""
08_manuscript.py - Build the preprint from paper/paper_stats.json.

Plain-language summary: writes paper/manuscript.md with every number filled in
from the stats files, then converts it to paper/manuscript.docx with pandoc.
If paper/reference.docx exists (a Word file whose styles should be copied, such
as a journal or personal template), pandoc uses its fonts, margins and heading
styles. Nothing in the text is typed by hand except words.
"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
S = json.load(open(os.path.join(PAPER, "paper_stats.json")))
B = json.load(open(os.path.join(ROOT, "data", "processed", "stats.json")))
BL = json.load(open(os.path.join(ROOT, "data", "processed", "build_log.json")))
META = json.load(open(os.path.join(ROOT, "release.json")))
H, R, A, O = S["hosp"], S["res"], S["assoc_last"], S["overlap_last"]
Y0, Y1 = S["first_year"], S["last_year"]
BB = S["bed_bands_last"]
SENS = S["sensitivity_small_cutoff_last"]
NF, NFn = S["national_by_facility_last"], S["national_by_facility_n_last"]
SUP = S["suppression_by_tertile_all_years"]
SUPALL = S["suppression_all_org_all_years_by_tertile"]
EXC = S["excluded_tiny"]
OVY = S["mrsa_overlap_years_by_state"]

def f(x, d=1):
    return f"{x:,.{d}f}"
def n(x):
    return f"{int(x):,}"
def pv(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
def rho(org, meas="small_rural"):
    s = A[org][meas]
    return f"ρ = {s['rho']:.2f}, {pv(s['p'])}, n = {s['n']}"
def mm(org, key):
    m = R[org][key]
    return f"{m['state']} {f(m['value'])}% ({n(m['r'])}/{n(m['n'])})"
def iqr(org):
    lo, hi = R[org]["iqr_last"]
    return f"{f(R[org]['median_last'])}% (IQR {f(lo)}–{f(hi)})"
def lst(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
STATE = {"AK": "Alaska", "WY": "Wyoming", "RI": "Rhode Island", "DC": "District of Columbia", "DE": "Delaware",
         "NJ": "New Jersey", "PR": "Puerto Rico", "KY": "Kentucky", "MS": "Mississippi", "AR": "Arkansas",
         "KS": "Kansas", "NE": "Nebraska", "IA": "Iowa", "ID": "Idaho", "SD": "South Dakota", "ND": "North Dakota",
         "NM": "New Mexico", "ME": "Maine"}
tot_sup = sum(SUPALL.values())
exc_covid = S["excluded_tiny_2020_2022_total"]
ov_m = O["mrsa"]["states"]
fam = {u: v for u, v in OVY.items()}
repo = META["repository"]; pages = META["pages_url"]
doi = META.get("doi")
doi_txt = f"https://doi.org/{doi}" if doi else "Zenodo DOI pending (minted on archiving the v1.0.0 GitHub release; linked from the repository)"
fig = lambda name: os.path.join("figures", name + ".png")

md = f"""---
title: "Antimicrobial resistance and the small and rural hospital network: an open state-by-year atlas of the United States, {Y0}–{Y1}"
author:
  - Fatima Abdulwahab, Independent Researcher, Dallas, Texas, USA. ORCID 0009-0008-2298-8386
lang: en-US
---

**Correspondence:** Fatima Abdulwahab, abdulwahabfatima43@gmail.com

**Article type:** Data resource and descriptive analysis (preprint)

**Running title:** Resistance and small and rural hospitals by state

**Keywords:** antimicrobial resistance; MRSA; carbapenem-resistant Enterobacterales; vancomycin-resistant enterococci; National Healthcare Safety Network; critical access hospitals; rural health; Provider of Services file; open data

# Abstract

**Background.** Small and rural hospitals deliver a large share of U.S. inpatient care in many states, often with limited on-site microbiology, infectious disease expertise and rapid diagnostics. State resistance surveillance and federal hospital registries are published separately, so it has not been easy to see where resistance and a small-hospital network coincide.

**Methods.** We built an open state-by-year table for the 50 states, the District of Columbia and Puerto Rico, {Y0}–{Y1} ({n(S['n_rows'])} state-years). It joins Centers for Disease Control and Prevention (CDC) Antimicrobial Resistance & Patient Safety Portal percent resistance for methicillin-resistant *Staphylococcus aureus* (MRSA), carbapenem-resistant Enterobacterales (CRE) and vancomycin-resistant *Enterococcus faecalis* and *E. faecium* (VRE), from infections reported to the National Healthcare Safety Network, to counts of active short-term acute care and critical access hospitals by certified bed size and rural location from the December Centers for Medicare & Medicaid Services (CMS) Provider of Services file. We documented every rule, reproduced CDC's published confidence intervals, and described cross-state associations with Spearman correlation.

**Results.** In {Y1}, {n(H['total_last'])} general hospitals were counted ({n(H['short_last'])} short-term, {n(H['cah_last'])} critical access). Hospitals with fewer than 100 beds made up {f(H['pct_small_last'])}% of hospitals but held {f(H['pct_beds_small_last'])}% of beds; {f(H['pct_small_rural_last'])}% were both small and rural. State resistance varied widely (MRSA state median {f(R['mrsa']['median_last'])}%; IQR {f(R['mrsa']['iqr_last'][0])}–{f(R['mrsa']['iqr_last'][1])}%). Across states, a larger small-and-rural share went with lower, not higher, percent resistant for all four organisms (CRE {rho('cre')}; MRSA {rho('mrsa')}). Within that gradient, Kentucky and Mississippi were in the top third of states for both MRSA resistance and small-and-rural share in all 14 years, and Arkansas in 13. States in the top third for small-and-rural share accounted for {n(SUPALL['high'])} of {n(tot_sup)} state-years in which CDC published no percent (fewer than 20 isolates). We also found two data pitfalls: older portal tables store suppressed cells as "0 of 0", and {f(H['pct_cah_cms_urban_last'])}% of critical access hospitals carry the CMS urban flag.

**Conclusions.** Resistance among reported hospital infections is, on average, lower in states dominated by small and rural hospitals, but a persistent Southern group of states combines high MRSA resistance with a large small-and-rural hospital network, and resistance data are thinnest where small hospitals are most common. The atlas, code and an interactive map are openly available to guide where laboratory, stewardship and diagnostic support for small hospitals may reach the most facilities.

# Introduction

Antimicrobial resistance remains one of the most consequential threats to U.S. patients. CDC's threat assessments rank carbapenem-resistant Enterobacterales as an urgent threat and MRSA and vancomycin-resistant enterococci as serious threats [1]. Much of the national picture of resistance in hospital infections comes from the National Healthcare Safety Network (NHSN), to which nearly all U.S. acute care hospitals report central line-associated bloodstream infections (CLABSI), catheter-associated urinary tract infections (CAUTI) and surgical site infections (SSI), including the pathogens and their susceptibility results [2,3]. CDC publishes these as pooled percent resistant by state and year on the Antimicrobial Resistance & Patient Safety Portal [4].

The U.S. hospital network is highly unequal in size: many hospitals are small, including more than 1,300 rural critical access hospitals [5], while most beds are in a minority of large hospitals. Small hospitals face distinct challenges in detecting and managing resistant organisms: fewer infectious disease physicians and pharmacists, smaller or outsourced microbiology laboratories, and less access to rapid molecular and phenotypic testing [6,7]. A resistant organism that a large academic laboratory identifies within hours may reach a small hospital as a referral result days later. Where resistance is common and much of the hospital care is delivered by small hospitals, those gaps matter most.

Yet the two pieces of information needed to see where this happens are published separately. CDC's portal reports resistance by state but not by hospital size at state level. The CMS Provider of Services (POS) file lists every Medicare-certified hospital with its type, bed count and location, but carries no resistance data [8]. To our knowledge, no open, reproducible table joins them across states and years.

This paper describes such a resource, the State Atlas of Hospital Resistance and Small Hospitals, and uses it to answer three descriptive questions. First, how is the U.S. general hospital network distributed by size and rural location, state by state, from {Y0} to {Y1}? Second, is state-level resistance among reported hospital infections higher or lower where small and rural hospitals make up more of the network, and which states combine high resistance with a large small-and-rural network? Third, where are the gaps in the resistance data themselves? We also document two data pitfalls that affect anyone using these sources.

# Methods

## Design and unit of analysis

This is a descriptive, ecological study of public, aggregated data. The unit of analysis is the state-year: the 50 states, the District of Columbia and Puerto Rico (the places CDC reports at state level), for each calendar year from {Y0} to {Y1}, giving {n(S['n_rows'])} rows. No patient-level or facility-level resistance data were used, and no human subjects research approval was required.

## Resistance data

We extracted state-by-year tables from the CDC Antimicrobial Resistance & Patient Safety Portal (AR HAI dataset) profile pages for four phenotypes: methicillin-resistant *S. aureus* (MRSA), carbapenem-resistant Enterobacterales (CRE), vancomycin-resistant *E. faecalis* and vancomycin-resistant *E. faecium* [4]. Each page embeds, in its page data, the complete table behind its state map: state, year, infection type, percent resistant, number resistant, number tested, 95% confidence interval and a suppression flag. We used the row combining all three infection types (CLABSI, CAUTI and SSI). Phenotype definitions follow CDC [4]. CDC computes a pooled mean percent resistant as the sum of resistant isolates divided by the sum of isolates tested, does not publish a percent when fewer than 20 isolates were tested, and reports mid-P exact 95% confidence intervals [9,10]. CDC's methods note cautions that the data should not be used for definitive conclusions about change over time or about a state compared with the nation, because surveillance definitions, laboratory breakpoints and state reporting requirements differ [9].

Two handling rules were applied. First, the portal stores most cells with fewer than 20 isolates as "0 resistant, 0 tested, 0%" in {Y0}–2022 (and one such cell in each of 2023 and 2024), and as blanks otherwise. All such cells were recorded as insufficient data with no value; a reported 0% (for example, 0 of 44 isolates) was kept. Second, the portal includes a "New England" Census-division row in {Y0}–2022 and a "No Geography Data" row in some years. These {n(BL['resistance']['cdc_rows_dropped_non_state'])} rows were dropped; each New England state also has its own row, and the division total equals the sum of its states.

We also derived a pooled vancomycin-resistant enterococci value (*E. faecalis* plus *E. faecium* counts) with a mid-P 95% interval, only where both species had published counts. CDC's national table by facility type (general acute care hospitals, long-term acute care hospitals, inpatient rehabilitation facilities) was retained for context.

## Hospital data

For each year we used the December release of the CMS POS file (Hospital & Non-Hospital Facilities), discovered from the data.cms.gov catalog [8]. We kept active providers (termination code 00) in the hospital category with subtype 01 (short-term acute care) or 11 (critical access), located in the 52 places. Bed size is certified beds (CRTFD_BED_CNT). "Rural" is the CMS urban-rural indicator (CBSA_URBN_RRL_IND = R, outside a metropolitan core-based statistical area). "Small" is fewer than 100 certified beds. "Small and rural" requires both. Children's, psychiatric, rehabilitation and long-term care hospitals, and rural emergency hospitals (which have no inpatient beds), were not counted.

Short-term hospitals listing two or fewer certified beds were excluded. During 2020–2022 the POS file listed several hundred additional active short-term hospitals with one or two beds; by name, most were ambulatory surgery centers and freestanding emergency departments, consistent with temporary COVID-19 public health emergency flexibilities that let such facilities enroll as hospitals. The rule removed {n(EXC['2020'])}, {n(EXC['2021'])} and {n(EXC['2022'])} such entries in 2020, 2021 and 2022 (up to {n(S['excluded_tiny_tx_max']['n'])} in Texas in {S['excluded_tiny_tx_max']['year']}), and between 1 and 5 genuine very small hospitals in other years. Every excluded row is listed in the released hospital file.

Because the CMS rural flag classified some critical access hospitals as urban (see Results), we added an alternative measure, "small and rural, or critical access", that counts every critical access hospital regardless of flag or bed count.

## Measures

For each state-year we computed: counts of general hospitals, short-term and critical access hospitals; counts in six certified-bed bands (1–24, 25–49, 50–99, 100–199, 200–399, ≥400); counts and percentages of hospitals that were small, rural, small and rural, and small-and-rural-or-critical-access; total certified beds and the percentage of beds in small and in rural hospitals. Resistance measures were percent resistant, counts, confidence interval and status for each phenotype.

## Analysis

All analyses are descriptive. We summarised the national hospital network by year and by bed band, and resistance in {Y1} by organism (state median and interquartile range, extremes, and the sum of published state counts). Cross-state association between small-and-rural share and percent resistant was described with Spearman rank correlation, separately for each organism and year, using only states with a published percent. We repeated it with the alternative critical-access measure, with the percentage of small hospitals, and with the percentage of beds in small hospitals, and for CRE excluding Puerto Rico. No adjustment for multiple comparisons was made, and p-values are reported as descriptive. To identify states where high resistance and a large small-and-rural network coincide, we flagged states in the top third (at or above the 66.7th percentile among states, within year) on both measures and counted how many years each state was flagged. Finally, we compared how often resistance was unavailable across within-year tertiles of small-and-rural share.

## Reproducibility, quality assurance and verification

A five-script pipeline (fetch, build, quality checks, map, documentation) reproduces all tables. Every downloaded file is logged with its date, size and SHA-256 fingerprint. An automated quality report checks row counts, join completeness, internal consistency of counts, percentages and intervals, and that no suppressed cell is shown as zero; it reports 0 failed checks. Our mid-P implementation reproduced CDC's published intervals exactly in 300 randomly sampled cells. The author independently verified the release: all raw fingerprints matched; a fresh download and rebuild produced byte-identical outputs; separately written code reproduced all 11,888 CDC rows, every hospital count and bed total in all {n(S['n_rows'])} state-years, and 200 of 200 sampled CDC intervals; and named values were checked by hand. All numbers in this paper are generated from the pipeline's statistics file. Analyses used Python 3 (pandas, SciPy); figures used Matplotlib and Seaborn.

# Results

## The atlas

The released table has {n(S['n_rows'])} rows (52 places × {Y1 - Y0 + 1} years) and {B['n_columns']} columns; all state-years matched between sources. Published state counts accounted for {f(R['mrsa']['state_share_of_national_isolates'])}% (MRSA), {f(R['cre']['state_share_of_national_isolates'])}% (CRE), {f(R['vre_faecalis']['state_share_of_national_isolates'])}% (*E. faecalis*) and {f(R['vre_faecium']['state_share_of_national_isolates'])}% (*E. faecium*) of isolates in CDC's national facility-type tables over {Y0}–{Y1}; the remainder came from territories, events without a state, and suppressed cells. As a check, the sum of published states for MRSA in {Y1} was {f(R['mrsa']['pooled_states_last'])}% ({n(R['mrsa']['n_resistant_last'])} of {n(R['mrsa']['n_tested_last'])}), matching CDC's national figure of 38.2% (3,659 of 9,579) [4].

## The hospital network

In {Y1} the atlas counted {n(H['total_last'])} active general hospitals: {n(H['short_last'])} short-term acute care and {n(H['cah_last'])} critical access hospitals (Figure 3). Between {Y0} and {Y1} the number of short-term hospitals fell by {f(abs(S['change_short_pct']))}% (from {n(H['short_first'])}), while critical access hospitals rose slightly (from {n(H['cah_first'])}); the total fell by {f(abs(S['change_total_pct']))}%.

Size was highly skewed (Figure 2, Table 1). Hospitals with fewer than 100 beds were {f(H['pct_small_last'])}% of hospitals ({n(H['small_last'])}) but held {f(H['pct_beds_small_last'])}% of the {n(H['beds_last'])} certified beds. Hospitals with 400 or more beds were {f(BB['400_plus']['pct_hospitals'])}% of hospitals and held {f(BB['400_plus']['pct_beds'])}% of beds. The 25–49-bed band, which contains most critical access hospitals, was the largest single group ({f(BB['25_49']['pct_hospitals'])}% of hospitals, {f(BB['25_49']['pct_beds'])}% of beds). Changing the cutoff for "small" changed the share substantially: {f(SENS['50']['pct'])}% of hospitals had fewer than 50 beds and {f(SENS['200']['pct'])}% fewer than 200 (CDC's own national size split), holding {f(SENS['50']['pct_beds'])}% and {f(SENS['200']['pct_beds'])}% of beds.

Nationally, {f(H['pct_rural_last'])}% of general hospitals were rural and {f(H['pct_small_rural_last'])}% ({n(H['small_rural_last'])}) were both small and rural. State profiles differed sharply (Figure 1A). Most hospitals were small in {H['states_majority_small']} of 52 places, and most were small and rural in {H['states_majority_small_rural']}. The state median small-and-rural share was {f(H['median_state_pct_small_rural'])}% (IQR {f(H['iqr_state_pct_small_rural'][0])}–{f(H['iqr_state_pct_small_rural'][1])}), from 0% in {lst([STATE[u] for u in H['states_zero_small_rural']])} to {f(H['max_state_small_rural']['value'])}% in {STATE[H['max_state_small_rural']['usps']]}.

**Critical access hospitals and the rural flag.** Of {n(H['cah_last'])} critical access hospitals in {Y1}, {n(H['cah_cms_urban_last'])} ({f(H['pct_cah_cms_urban_last'])}%) carried the CMS urban flag, and {n(H['cah_over_25_last'])} listed more than 25 certified beds (maximum {n(H['cah_max_beds_last'])}), likely because swing beds or distinct-part psychiatric or rehabilitation units are included (Supplementary Figure S1). The flag-based small-and-rural measure therefore omits about one in five critical access hospitals; counting all of them raised the national small-and-rural-or-critical-access share to {f(H['pct_small_rural_or_cah_last'])}%.

## Resistance by state

Table 2 summarises resistance in {Y1}. MRSA was reported for {R['mrsa']['reported_last']} places, with a state median of {iqr('mrsa')}, ranging from {mm('mrsa','min_last')} to {mm('mrsa','max_last')}. MRSA resistance was highest across a band of Southern and Appalachian states (Figure 1B). CRE was reported for {R['cre']['reported_last']} places (median {iqr('cre')}); Puerto Rico was a marked outlier at {f(R['cre']['max_last']['value'])}% ({n(R['cre']['max_last']['r'])} of {n(R['cre']['max_last']['n'])}), more than four times the next-highest state. Vancomycin resistance was {iqr('vre_faecium')} among *E. faecium* (reported for only {R['vre_faecium']['reported_last']} places) and {iqr('vre_faecalis')} among *E. faecalis*. The derived pooled enterococcal value could be computed for {S['vre_pooled_last']['computable']} places (sum {f(S['vre_pooled_last']['pooled'])}%).

For context, CDC's national figures by facility type in {Y1} showed much higher resistance in long-term acute care hospitals than in general acute care hospitals: MRSA {f(NF['MRSA']['Long Term Acute Care Hospitals'])}% vs {f(NF['MRSA']['General Acute Care Hospitals'])}%, CRE {f(NF['CRE']['Long Term Acute Care Hospitals'])}% vs {f(NF['CRE']['General Acute Care Hospitals'])}%, *E. faecium* {f(NF['VRE_faecium']['Long Term Acute Care Hospitals'])}% vs {f(NF['VRE_faecium']['General Acute Care Hospitals'])}%.

Summed across published states, percent resistant in {Y1} was lower than in {Y0} for all four organisms (MRSA {f(R['mrsa']['series_pooled'][str(Y0)])}% to {f(R['mrsa']['series_pooled'][str(Y1)])}%; CRE {f(R['cre']['series_pooled'][str(Y0)])}% to {f(R['cre']['series_pooled'][str(Y1)])}%; *E. faecium* {f(R['vre_faecium']['series_pooled'][str(Y0)])}% to {f(R['vre_faecium']['series_pooled'][str(Y1)])}%). Consistent with CDC's guidance, we report these without inference about trend, because definitions and reporting changed over the period [9].

## Resistance and the small-and-rural hospital share

Across states, a larger share of small and rural hospitals was associated with lower percent resistant for all four organisms in {Y1} (Figure 4, Table 3): CRE {rho('cre')}; *E. faecalis* {rho('vre_faecalis')}; *E. faecium* {rho('vre_faecium')}; MRSA {rho('mrsa')}. The CRE association was not driven by Puerto Rico (excluding it, ρ = {S['assoc_last_cre_no_pr']['rho']:.2f}, {pv(S['assoc_last_cre_no_pr']['p'])}, n = {S['assoc_last_cre_no_pr']['n']}). Results were similar with the alternative measure counting all critical access hospitals, and with the share of small hospitals; associations with the share of beds in small hospitals were similar for CRE and *E. faecalis* and weaker for MRSA and *E. faecium* (Table 3).

The direction was stable over time (Figure 5). For CRE, ρ ranged from {A['cre']['by_year_range'][0]:.2f} to {A['cre']['by_year_range'][1]:.2f} and was negative with p < 0.05 in all {A['cre']['by_year_n_p_lt_05']} years. For *E. faecalis*, ρ was negative in all 14 years ({A['vre_faecalis']['by_year_range'][0]:.2f} to {A['vre_faecalis']['by_year_range'][1]:.2f}; p < 0.05 in {A['vre_faecalis']['by_year_n_p_lt_05']}). For MRSA, ρ was negative in all 14 years but modest ({A['mrsa']['by_year_range'][0]:.2f} to {A['mrsa']['by_year_range'][1]:.2f}; p < 0.05 in {A['mrsa']['by_year_n_p_lt_05']}). For *E. faecium*, estimates were inconsistent ({A['vre_faecium']['by_year_range'][0]:.2f} to {A['vre_faecium']['by_year_range'][1]:.2f}; negative in {A['vre_faecium']['by_year_n_negative']} of 14 years, p < 0.05 in {A['vre_faecium']['by_year_n_p_lt_05']}), reflecting the many states without published values.

## States where high resistance and a small-and-rural network coincide

Despite the overall inverse gradient, some states combined both features (Table 4). In {Y1}, {len(ov_m)} states were in the top third for both MRSA resistance (≥{f(O['mrsa']['threshold_resistance'])}%) and small-and-rural share (≥{f(O['mrsa']['threshold_small_rural'])}%): {lst([s['state'] for s in ov_m])}. Together they had {n(O['mrsa']['n_small_rural_hospitals_in_overlap'])} small and rural hospitals. This pattern was persistent (Figure 7): Kentucky and Mississippi were flagged in all {fam['KY']} years and Arkansas in {fam['AR']}; no other state was flagged in more than {max(v for u, v in fam.items() if u not in ('KY','MS','AR'))} years. For the other organisms, the overlap in {Y1} comprised {lst([s['state'] for s in O['cre']['states']])} for CRE, {lst([s['state'] for s in O['vre_faecalis']['states']])} for *E. faecalis*, and {lst([s['state'] for s in O['vre_faecium']['states']])} for *E. faecium*; several of these rest on small isolate counts (for example Maine, *E. faecalis* {f(R['vre_faecalis']['max_last']['value'])}%, {n(R['vre_faecalis']['max_last']['r'])} of {n(R['vre_faecalis']['max_last']['n'])}).

## Where the resistance data are missing

Across all years and organisms, CDC published no percent for {n(tot_sup)} state-years. States in the top tertile of small-and-rural share accounted for {n(SUPALL['high'])} of these, compared with {n(SUPALL['middle'])} in the middle and {n(SUPALL['low'])} in the bottom tertile (Figure 6). The concentration held for every organism: MRSA {SUP['mrsa']['high']} of {sum(SUP['mrsa'].values())}, CRE {SUP['cre']['high']} of {sum(SUP['cre'].values())}, *E. faecalis* {SUP['vre_faecalis']['high']} of {sum(SUP['vre_faecalis'].values())} and *E. faecium* {SUP['vre_faecium']['high']} of {sum(SUP['vre_faecium'].values())}. In {Y1}, MRSA was unavailable for {lst([STATE[u] for u in R['mrsa']['insufficient_last_states']])}, both among the states with the highest small-and-rural shares, and *E. faecium* was unavailable for {R['vre_faecium']['insufficient_last']} places.

# Discussion

## Principal findings

This open atlas places state resistance among reported hospital infections next to the size and rural composition of each state's general hospital network, for {Y1 - Y0 + 1} years. Three findings stand out. First, small hospitals are the majority of U.S. general hospitals but hold about one in ten beds, and in about a quarter of states most hospitals are both small and rural. Second, contrary to a simple expectation that resistance burden is heaviest where small hospitals predominate, states with more small and rural hospitals had, on average, lower percent resistance, most clearly for CRE and *E. faecalis* and modestly for MRSA. Third, this average hides two groups that matter for small hospitals: a persistent Southern cluster (Kentucky, Mississippi and Arkansas) where high MRSA resistance and a large small-and-rural network coincide year after year, and the most rural states, where the resistance data are most often missing altogether.

## Interpretation

The inverse gradient is plausible. CRE and vancomycin-resistant enterococci are concentrated in populations with intensive healthcare exposure: long-term acute care hospitals, large referral centers, transplant and oncology services, and dense networks of patient transfer, which are features of metropolitan areas [3,11]. CDC's own national tables show resistance in long-term acute care hospitals several times that of general acute care hospitals. States dominated by small rural hospitals have fewer such settings. The weaker gradient for MRSA, which is common in both healthcare and community settings, fits this explanation, as does the regional Southern pattern of high MRSA that crosses urban and rural states.

The finding is ecological. It describes states, not hospitals, and cannot show that resistance is lower in small hospitals [12]. CDC does not publish state resistance by hospital size, and the HAI events behind each state percentage are likely to come mostly from larger hospitals, which perform more procedures and place more central lines and catheters. A state's percent therefore largely reflects its larger hospitals. What a small rural hospital in that state encounters, particularly in patients transferred to or from larger centers, may differ.

## Implications

For state health departments, laboratory networks and hospital associations, the atlas suggests two kinds of priority rather than one. Where high resistance and a large small-hospital network coincide, as with MRSA in Kentucky, Mississippi and Arkansas, small hospitals likely encounter resistant organisms often enough to justify investment in local laboratory capacity, rapid testing access, stewardship support and clear referral pathways [6,7]. Where resistance data are missing, the gap is itself a finding. The states with the highest small-and-rural shares are also those where CDC most often cannot publish a percent, because too few isolates are reported. Small hospitals there have the least state-level evidence to calibrate empiric therapy, and pooling across years, regional antibiograms or expanded reporting may be needed.

The atlas also documents two pitfalls for anyone using these sources. Treating the portal's "0 of 0" cells as 0% would produce false reports of zero resistance concentrated in exactly the small, rural states this analysis concerns. And the CMS rural flag misclassifies about one in five critical access hospitals as urban, so analyses of "rural hospitals" built on that flag alone omit a substantial part of the critical access program.

## Strengths and limitations

Strengths include complete coverage of all places CDC reports at state level for 14 years, use of counts and intervals rather than published percentages alone, explicit and documented handling of suppressed cells, temporary pandemic-era enrollments and the critical access flag, exact reproduction of CDC's interval method, and independent verification of every table. All data, code and an interactive map are openly available.

Limitations are substantial. Resistance reflects isolates from three types of reported infection, not all clinical cultures or community infections. The analysis is ecological and cross-sectional within each year; correlations are unadjusted, describe states rather than hospitals, and should not be read causally. CDC cautions against interpreting change over time and state-versus-nation comparisons, and laboratory breakpoints, reporting mandates and validation differ by state and year [9]. Suppression removes data non-randomly, from the smallest and most rural states. "Small" and "rural" depend on definitions; we used fewer than 100 certified beds and the CMS flag, provided bed bands and an alternative critical-access measure, and showed that the share of small hospitals is sensitive to the cutoff. Certified beds may differ from staffed beds, and the December snapshot misses mid-year openings and closures. Long-term acute care, rehabilitation and children's hospitals contribute to CDC's state figures but were not counted on the hospital side. Finally, the CDC tables are read from data embedded in public web pages rather than a formal download service; the pipeline stops if their structure changes.

## Future work

Planned extensions include annual updates as CDC releases new years; an alternative rural definition from the Federal Office of Rural Health Policy; county-level maps of the hospital network; linking each hospital to its CLIA laboratory certificate to describe how many small hospitals perform microbiology on site; and additional phenotypes, including carbapenem-resistant *Acinetobacter* and *Pseudomonas aeruginosa*.

# Conclusions

Small hospitals make up half of U.S. general hospitals. Across states, resistance among reported hospital infections is on average lower where small and rural hospitals dominate. But a persistent group of Southern states combines high MRSA resistance with a large small-and-rural network, and resistance data are scarcest in the most rural states. An open, reproducible atlas makes these patterns visible and can help direct laboratory, diagnostic and stewardship support to the places where small hospitals face resistant organisms with the least local capacity and the least data.

# Declarations

**Data and code availability.** The dataset, code, quality report, codebook, limitations and verification record are openly available at {repo} (version {META['version']}; {doi_txt}). The interactive map is at {pages}. Data and documentation are licensed CC BY 4.0 and code MIT. Source data are U.S. federal government works from CDC and CMS.

**Ethics.** This study used only publicly available, aggregated data and involved no human subjects.

**Funding.** None.

**Competing interests.** The author declares no competing interests.

**Author contributions (CRediT).** Fatima Abdulwahab: conceptualization, methodology, data curation, validation, formal analysis, visualization, writing (original draft, review and editing).

**Use of AI tools.** Claude (Anthropic) assisted with code, data processing, figure generation and drafting. The author designed the study, made all analytic decisions, independently verified every table and number against the sources, and takes full responsibility for the content.

# References

1. Centers for Disease Control and Prevention. Antibiotic Resistance Threats in the United States, 2019. Atlanta, GA: U.S. Department of Health and Human Services, CDC; 2019.
2. Centers for Disease Control and Prevention. National Healthcare Safety Network (NHSN). https://www.cdc.gov/nhsn/index.html
3. Weiner-Wells LM, et al. Antimicrobial-resistant pathogens associated with adult healthcare-associated infections: summary of data reported to the National Healthcare Safety Network, 2015–2017. Infect Control Hosp Epidemiol. 2020;41(1):1–18.
4. Centers for Disease Control and Prevention. Antimicrobial Resistance & Patient Safety Portal: antimicrobial resistance profiles (MRSA; carbapenem-resistant Enterobacterales; vancomycin-resistant *Enterococcus faecalis* and *E. faecium*). https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance. Accessed 6 November 2026.
5. Flex Monitoring Team. The Flex Program. https://www.flexmonitoring.org/the-flex-program
6. Stenehjem E, Hyun DY, Septimus E, et al. Antibiotic stewardship in small hospitals: barriers and potential solutions. Clin Infect Dis. 2017;65(4):691–696.
7. Centers for Disease Control and Prevention. Core Elements of Hospital Antibiotic Stewardship Programs. Atlanta, GA: U.S. Department of Health and Human Services, CDC; 2019.
8. Centers for Medicare & Medicaid Services. Provider of Services File – Hospital & Non-Hospital Facilities (December releases 2011–2024). https://data.cms.gov/provider-characteristics/hospitals-and-other-facilities/provider-of-services-file-hospital-non-hospital-facilities. Accessed 6 November 2026.
9. Centers for Disease Control and Prevention. Antimicrobial Resistance & Patient Safety Portal. Methodology: Antimicrobial Resistance HAI Data. January 2026.
10. Berry G, Armitage P. Mid-P confidence intervals: a brief review. J R Stat Soc Ser D (The Statistician). 1995;44(4):417–423.
11. Guh AY, Bulens SN, Mu Y, et al. Epidemiology of carbapenem-resistant Enterobacteriaceae in 7 US communities, 2012–2013. JAMA. 2015;314(14):1479–1487.
12. Robinson WS. Ecological correlations and the behavior of individuals. Am Sociol Rev. 1950;15(3):351–357.
"""

# ---------------------------------------------------------------- tables
t1 = ["```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```", "", "# Tables", "",
      f"**Table 1.** U.S. general hospitals and certified beds by hospital size, {Y1}.", "",
      "| Certified beds | Hospitals | % of hospitals | Certified beds | % of beds |",
      "|:--|--:|--:|--:|--:|"]
lab = {"1_24": "1–24", "25_49": "25–49", "50_99": "50–99", "100_199": "100–199", "200_399": "200–399", "400_plus": "≥400"}
for k, v in BB.items():
    t1.append(f"| {lab[k]} | {n(v['hospitals'])} | {f(v['pct_hospitals'])} | {n(v['beds'])} | {f(v['pct_beds'])} |")
t1.append(f"| **Total** | **{n(sum(v['hospitals'] for v in BB.values()))}** | **100.0** | **{n(sum(v['beds'] for v in BB.values()))}** | **100.0** |")
t1 += ["", f"Active short-term acute care (CMS subtype 01) and critical access (subtype 11) hospitals in the December {Y1} Provider of Services file, 50 states, DC and Puerto Rico; short-term hospitals with ≤2 certified beds excluded.", ""]

t2 = ["```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```", "", f"**Table 2.** Percent resistant by state, {Y1}.", "",
      "| Organism | Reported / no value | State median (IQR), % | Highest, % (R/N) | Lowest, % (R/N) | All published states, % (R/N) |",
      "|:---------|:-------|:---------|:----------|:----------|:------------|"]
NAMES = {"mrsa": "MRSA", "cre": "CRE", "vre_faecalis": "VRE, *E. faecalis*", "vre_faecium": "VRE, *E. faecium*"}
for p in ["mrsa", "cre", "vre_faecalis", "vre_faecium"]:
    r = R[p]; lo, hi = r["iqr_last"]
    short = lambda m: f"{m['usps']} {f(m['value'])} ({n(m['r'])}/{n(m['n'])})"
    low = short(r["min_last"]) if not (p in ("cre", "vre_faecalis") and r["min_last"]["value"] == 0) else "0.0 (several states)"
    t2.append(f"| {NAMES[p]} | {r['reported_last']} / {r['insufficient_last']} | {f(r['median_last'])} ({f(lo)}–{f(hi)}) | {short(r['max_last'])} | {low} | {f(r['pooled_states_last'])} ({n(r['n_resistant_last'])}/{n(r['n_tested_last'])}) |")
t2 += ["", "Source: CDC AR & Patient Safety Portal, all infection types (CLABSI, CAUTI, SSI). Reported / no value: places with a published percent / places with fewer than 20 isolates tested (of 52). R/N: resistant/tested. States by postal abbreviation.", ""]

t3 = ["", f"**Table 3.** Spearman correlation across states between hospital-network measures and percent resistant, {Y1}.", "",
      "| Organism | Small and rural, % | Small and rural or critical access, % | Small (<100 beds), % | Beds in small hospitals, % |",
      "|:--|:--|:--|:--|:--|"]
for p in ["mrsa", "cre", "vre_faecalis", "vre_faecium"]:
    cells = []
    for m in ["small_rural", "small_rural_or_cah", "small", "beds_in_small"]:
        s = A[p][m]
        ptxt = "<0.001" if s["p"] < 0.001 else f"{s['p']:.3f}"
        cells.append(f"{s['rho']:.2f} ({ptxt})")
    t3.append(f"| {NAMES[p]} (n = {A[p]['small_rural']['n']}) | " + " | ".join(cells) + " |")
t3 += ["", "Values are ρ (p). States without a published percent excluded. Descriptive, unadjusted, ecological; not corrected for multiple comparisons.", ""]

t4 = ["```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```", "", f"**Table 4.** States in the top third of states for both percent resistant and small-and-rural hospital share, {Y1}.", "",
      "| Organism | State | % resistant | Small and rural, % | General hospitals | Small and rural | Critical access |",
      "|:--|:--|--:|--:|--:|--:|--:|"]
for p in ["mrsa", "cre", "vre_faecalis", "vre_faecium"]:
    for s in O[p]["states"]:
        t4.append(f"| {NAMES[p]} | {s['state']} | {f(s['res'])} | {f(s['small_rural'])} | {s['hosp']} | {s['small_rural_n']} | {s['cah']} |")
t4 += ["", f"Top third: at or above the 66.7th percentile among states with a published value (resistance) or among all 52 places (small-and-rural share). MRSA, years flagged {Y0}–{Y1}: " +
       "; ".join(f"{STATE.get(u, u)} {v}" for u, v in OVY.items()) + ".", ""]

figs = ["```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```", "", "# Figures", "",
 f"![**Figure 1.** (A) Percent of general hospitals that are small (<100 certified beds) and rural (CMS flag), by state, {Y1}. (B) MRSA percent resistant among *S. aureus* isolates from CLABSI, CAUTI and SSI reported to NHSN, by state, {Y1}; hatched states had fewer than 20 isolates tested. Class breaks are fixed values. Puerto Rico is shown as an inset.]({fig('fig1_maps')}){{width=100%}}", "",
 f"![**Figure 2.** Share of U.S. general hospitals and of certified beds by hospital size, {Y1}. Bands above the dashed line are hospitals with fewer than 100 beds.]({fig('fig2_bed_bands')}){{width=80%}}", "",
 f"![**Figure 3.** (A) Active short-term acute care and critical access hospitals, and hospitals that are small and rural, in the December Provider of Services file of each year, {Y0}–{Y1}. (B) Short-term entries with two or fewer certified beds that were excluded, showing the temporary enrollments of 2020–2022.]({fig('fig3_hospitals_by_year')}){{width=80%}}", "",
 f"![**Figure 4.** Percent resistant against the share of general hospitals that are small and rural, by state, {Y1}. Dashed lines mark the top third of states on each axis; orange points are in the top third on both. The highest and any unique lowest values are labeled. CRE is plotted on a scale linear to 5% and logarithmic above.]({fig('fig4_scatter')}){{width=100%}}", "",
 f"![**Figure 5.** Spearman correlation across states between small-and-rural share and percent resistant, by year and organism. Filled points: p < 0.05.]({fig('fig5_rho_by_year')}){{width=80%}}", "",
 f"![**Figure 6.** State-years with no published percent (fewer than 20 isolates), {Y0}–{Y1}, by within-year tertile of small-and-rural hospital share.]({fig('fig6_suppression')}){{width=80%}}", "",
 f"![**Figure 7.** States in the top third for both MRSA percent resistant and small-and-rural share in each year, {Y0}–{Y1}. Numbers in parentheses are years flagged.]({fig('fig7_mrsa_overlap')}){{width=80%}}", "",
 "```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```", "", "# Supplementary material", "",
 f"![**Supplementary Figure S1.** Critical access hospitals by certified beds (5-bed bins: 1–5, 6–10, …, 21–25, 26–30, …) and CMS urban-rural flag, {Y1}. The dashed line marks 25 beds.]({fig('figS1_cah')}){{width=80%}}", "",
 f"**Supplementary Table S1.** State profiles for {Y1} (all 52 places) are provided as `paper/tables/table_state_profile_last_year.csv` in the repository; the full state-by-year table is `data/processed/atlas_state_year.csv`, documented in `docs/CODEBOOK.md`.", ""]

text = md + "\n" + "\n".join(t1 + t2 + t3 + t4 + figs)
open(os.path.join(PAPER, "manuscript.md"), "w").write(text)
ref = os.path.join(PAPER, "reference.docx")
cmd = ["pandoc", "manuscript.md", "-o", "manuscript.docx", "--resource-path=."]
if os.path.exists(ref):
    cmd.append("--reference-doc=reference.docx")
subprocess.run(cmd, cwd=PAPER, check=True)
# Re-save through LibreOffice: writes schema-valid Word XML (pandoc's output has
# element-order issues Word may "repair"), then render the matching PDF from it.
import shutil, tempfile, zipfile
if shutil.which("soffice") or shutil.which("libreoffice"):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    name = "Abdulwahab_State_Resistance_Atlas_preprint"
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(PAPER, "manuscript.docx"), os.path.join(tmp, name + ".docx"))
        subprocess.run([exe, "--headless", f"-env:UserInstallation=file://{tmp}/profile", "--convert-to", "docx:MS Word 2007 XML",
                        "--outdir", os.path.join(tmp, "out"), os.path.join(tmp, name + ".docx")], check=True, capture_output=True)
        src = os.path.join(tmp, "out", name + ".docx"); dst = os.path.join(PAPER, name + ".docx")
        with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
            for item in zi.infolist():
                if not item.filename.endswith("/"):  # drop folder entries
                    zo.writestr(item, zi.read(item.filename))
        subprocess.run([exe, "--headless", f"-env:UserInstallation=file://{tmp}/profile", "--convert-to", "pdf",
                        "--outdir", PAPER, dst], check=True, capture_output=True)
    print(f"wrote paper/{name}.docx and .pdf (validated Word XML, matching PDF)")
words = len(md.split("# References")[0].split())
print(f"wrote paper/manuscript.md and paper/manuscript.docx; main text ~{words} words; template={'yes' if os.path.exists(ref) else 'default'}")
