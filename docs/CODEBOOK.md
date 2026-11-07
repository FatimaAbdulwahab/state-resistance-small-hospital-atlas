# Codebook

*Plain-language summary: this file explains every column in the atlas tables, where each value comes from, and what was done to it. You need it when checking numbers or when someone asks "what exactly does this column mean?"*

## Files in `data/processed/`

| File | One row is | Rows |
|---|---|---|
| `atlas_state_year.csv` | one state in one year. **The main table.** | 728 (52 places × 14 years) |
| `resistance_state_year_long.csv` | one state, year, organism and infection type, from CDC | 11,648 |
| `hospitals_state_year.csv` | one state in one year, hospital counts only | 728 |
| `hospital_list_by_year.csv` | one hospital in one year's December file, with the rule applied to it (761 excluded rows kept and labeled) | 66,572 |
| `resistance_national_by_facility_type.csv` | one organism, year and facility type, national (CDC) | 168 |
| `qa_report.txt` | the quality checks, with PASS or FAIL | |
| `stats.json` | every number quoted in the README, map and talk track | |
| `build_log.json` | row counts at each step of the build | |

"Places" means the 50 states, the District of Columbia, and Puerto Rico, the same set CDC reports at state level.

## `atlas_state_year.csv`

### Identifiers

| Column | Meaning |
|---|---|
| `usps` | Two-letter postal code (TX). |
| `state_name` | Full name as CDC writes it (Texas). |
| `state_fips` | Two-digit federal (FIPS) state code, kept as text (48). |
| `year` | Calendar year, 2011 to 2024. For resistance: the year of the infection. For hospitals: the December Provider of Services file of that year. |

### Hospital counts (source: CMS Provider of Services file, December release)

Which hospitals are counted: rows in the hospital category (`PRVDR_CTGRY_CD` = 01) with subtype `PRVDR_CTGRY_SBTYP_CD` = **01 (short-term acute care)** or **11 (critical access)**, termination code `PGM_TRMNTN_CD` = 00 (active), located in one of the 52 places. Short-term hospitals listing **2 or fewer certified beds** are excluded (see `excluded_reason` in `hospital_list_by_year.csv`). Not counted: psychiatric, rehabilitation, long-term care, children's, and religious nonmedical hospitals, and Rural Emergency Hospitals (which have no inpatient beds). Bed size is `CRTFD_BED_CNT` (certified beds). For critical access hospitals this can exceed 25 (68 in 2024, up to 138), likely because swing beds or distinct-part psychiatric or rehabilitation units are counted.

| Column | Meaning |
|---|---|
| `hosp_total` | Counted general hospitals (short-term acute + critical access). |
| `hosp_short_term_acute` | Subtype 01. |
| `hosp_critical_access` | Subtype 11. |
| `hosp_rural` | `CBSA_URBN_RRL_IND` = R (CMS rural flag: not in a metropolitan core-based statistical area). Applied to every hospital as CMS records it, including critical access hospitals. |
| `hosp_urban` | `CBSA_URBN_RRL_IND` = U. |
| `hosp_rural_unknown` | Flag blank. 0 to 3 hospitals nationally per year. |
| `hosp_small` | Fewer than 100 certified beds (setting `small_hospital_max_beds` = 99 in `config.json`). |
| `hosp_small_rural` | Small and rural (CMS flag). |
| `hosp_critical_access_cms_urban` | Critical access hospitals the CMS flag marks urban (U). In 2024, 266 of 1,368. |
| `hosp_small_rural_or_cah` | Small and rural by the CMS flag, **or** a critical access hospital whatever its flag or bed count. Alternative to `hosp_small_rural` that counts every critical access hospital. |
| `hosp_lt200_beds` | Fewer than 200 certified beds. Matches CDC's own national "small facility" split, for comparison. |
| `beds_total` | Sum of certified beds in counted hospitals. |
| `beds_in_small` | Certified beds in small hospitals. |
| `beds_in_rural` | Certified beds in rural hospitals. |
| `hosp_beds_1_24` … `hosp_beds_400_plus` | Hospitals in each bed-size band: 1–24, 25–49, 50–99, 100–199, 200–399, 400 or more. The bands add up to `hosp_total`. |
| `pct_hosp_small` | `hosp_small / hosp_total × 100`, one decimal. |
| `pct_hosp_rural` | `hosp_rural / hosp_total × 100`. |
| `pct_hosp_small_rural` | `hosp_small_rural / hosp_total × 100`. **Used on the scatter chart.** |
| `pct_hosp_small_rural_or_cah` | `hosp_small_rural_or_cah / hosp_total × 100`. On the map as "Small and rural, or critical access." |
| `pct_hosp_critical_access` | `hosp_critical_access / hosp_total × 100`. |
| `pct_beds_in_small` | `beds_in_small / beds_total × 100`. |
| `pct_beds_in_rural` | `beds_in_rural / beds_total × 100`. |

### Resistance (source: CDC AR & Patient Safety Portal, AR HAI dataset, "All Infectious Event Type Data")

The same six columns repeat for each organism, with the prefix `mrsa_`, `cre_`, `vre_faecalis_`, `vre_faecium_`:

| Column | Meaning |
|---|---|
| `*_pct_resistant` | CDC's pooled mean percent resistant: resistant ÷ tested × 100, rounded half-up to one decimal. Blank when status is `insufficient_data`. |
| `*_n_resistant` | Isolates that tested resistant. |
| `*_n_tested` | Isolates tested for that drug class. |
| `*_ci_lower`, `*_ci_upper` | CDC's 95% confidence interval (mid-P exact), percent. |
| `*_status` | `reported`, or `insufficient_data` when CDC published no percent. |

Organisms, as CDC names its phenotypes (full definitions: CDC's Phenotype Definitions document on the portal):

- `mrsa`: methicillin-resistant *Staphylococcus aureus*, percent among *S. aureus* tested.
- `cre`: carbapenem-resistant Enterobacterales, percent among Enterobacterales tested.
- `vre_faecalis`: vancomycin-resistant *Enterococcus faecalis*.
- `vre_faecium`: vancomycin-resistant *Enterococcus faecium*.

**How "insufficient data" is set.** CDC does not publish a percent when fewer than 20 isolates were tested. The portal stores most of those cells as "0 resistant, 0 tested, 0%" in 2011 to 2022, plus one such cell in each of 2023 and 2024; the other 2023 and 2024 cells are blank. Both are recorded here as `insufficient_data` with all values blank. A genuine 0% (for example 0 of 44 tested) is kept as reported.

**Derived by this atlas (not published by CDC):**

| Column | Meaning |
|---|---|
| `vre_pooled_n_resistant`, `vre_pooled_n_tested` | *E. faecalis* + *E. faecium* counts added together. |
| `vre_pooled_pct_resistant` | Pooled resistant ÷ pooled tested × 100. |
| `vre_pooled_ci_lower`, `vre_pooled_ci_upper` | Mid-P exact 95% interval computed by `02_build.py`. The same method reproduces CDC's published intervals exactly (QA report, section 2). |
| `vre_pooled_status` | `derived` when both species have published counts; otherwise `not_computable` (CDC's hidden counts cannot be recovered). |

## `resistance_state_year_long.csv`

Same resistance fields in long form, plus `event_type`: `ALL` (all three infection types combined, used in the main table), `CLABSI` (central line bloodstream infections), `CAUTI` (catheter urinary tract infections), `SSI` (surgical site infections). CDC changed these labels from full names (2011–2023) to abbreviations (2024); they are harmonized here. `phenotype` is CDC's label with formatting tags removed.

## `hospital_list_by_year.csv`

One row per general hospital in each December file: `year`, `ccn` (CMS Certification Number), `facility_name`, `city`, `usps`, `subtype`, `hospital_type`, `certified_beds`, `bed_band`, `urban_rural_code` (R/U), and `excluded_reason` (blank if counted). Use it to check any state's count by hand.

## `resistance_national_by_facility_type.csv`

CDC's national figures by facility type: `facility_code` 109 = General Acute Care Hospitals, 110 = Long Term Acute Care Hospitals, 111 = Inpatient Rehabilitation Facilities (labels from the portal's own code). Context only; not joined to states.

## Raw files (`data/raw/`)

- `arpsp/*.html`: the four CDC profile pages as downloaded. `arpsp/arpsp_state_year.csv` and `arpsp/arpsp_national_facility_type.csv`: the tables embedded in those pages, extracted unchanged. `arpsp/docs/`: CDC's methodology, data dictionary, and guide.
- `pos/pos_hospitals_decYYYY.csv`: hospital rows and 12 columns from each December file. The full file's size and SHA-256 are in `PROVENANCE.txt`.
- `PROVENANCE.txt`: every downloaded file with date, size, SHA-256 fingerprint, and URL.
