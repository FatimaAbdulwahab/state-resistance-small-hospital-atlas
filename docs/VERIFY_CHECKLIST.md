# Your verification checklist

*Before anything goes public under your name, you check it. Every item names the file, the row, the number, and where to confirm it. Total time: about 1.5 hours in one sitting. Tick each box and write the date.*

**How to open the files.** The data files are spreadsheets saved as `.csv`. Open them in Excel or Google Sheets (File, Open, choose the file). Turn on a filter row (Excel: Data, Filter; Sheets: Data, Create a filter) so you can pick a state and year from the column headings.

**How to read CDC's numbers.** Open the CDC link given, scroll to the section **Geographic Locations**, set **HAI Type** to *All Event Types*, set **Year**, then click **View Data** under the map. A table of states appears with the percent. Hovering a state on CDC's map also shows its numbers.

## Part 1: Make sure the results can be rebuilt (15 to 30 min)

Pick one:

- [ ] **Option A, run it yourself.** In a terminal inside the project folder, paste:
  ```
  pip install -r requirements.txt
  python code/01_fetch.py
  python code/02_build.py
  python code/03_qa.py
  python code/04_site.py
  ```
  The download takes about 3 minutes. The last lines of `03_qa.py` should say `Checks failed: 0`.
- [ ] **Option B, ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the project zip and say: *"Re-run this pipeline from scratch and give me the headline numbers."* They should match these 2024 figures: **4,500** hospitals counted; **3,132** short-term and **1,368** critical access; **51.6%** under 100 beds; **10.6%** of beds in those small hospitals; Texas MRSA **43.1%** (270 of 627).

Then:

- [ ] Open `data/processed/qa_report.txt`. The last section says `Checks failed: 0`. Skim section 3: the hospital totals per year should look steady (about 4,500 to 4,900).

## Part 2: Check the sources (10 min)

- [ ] CDC MRSA page loads and says "Years Included 2011 - 2024": https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance/profile/methicillin-resistant-staphylococcus-aureus
- [ ] CMS Provider of Services page loads: https://data.cms.gov/provider-characteristics/hospitals-and-other-facilities/provider-of-services-file-hospital-non-hospital-facilities
- [ ] Reuse is allowed. Both are U.S. federal government data published free for public use. The atlas credits both by name. Confirm you see no restriction on either page. If either page shows a newer year (2025), note it for version 1.1; it does not block release.

## Part 3: Check rows by hand (45 to 60 min)

All values below are in `data/processed/atlas_state_year.csv` unless another file is named.

**Five you know personally (Texas and Dallas).** Open `data/processed/hospital_list_by_year.csv`, filter `year` = 2024 and `usps` = TX.

- [ ] Parkland Health and Hospital System, CCN 450015: 968 certified beds, short-term, urban. ___
- [ ] Baylor University Medical Center, CCN 450021: 914 beds. ___
- [ ] UT Southwestern University Hospital, CCN 450044: 550 beds. ___
- [ ] Lillian M Hudspeth Memorial Hospital, Sonora, CCN 451324: critical access, 12 beds, rural. ___
- [ ] Texas 2024 row in the atlas: `hosp_total` 372, `hosp_critical_access` 91, `hosp_small` 220, `hosp_rural` 132. These are counts of the TX rows you just filtered (blank `excluded_reason` only). ___

  *To confirm a hospital at CMS:* open the CMS page above, click **View Data**, choose the **December 2024** version if offered, and search the CCN in the `PRVDR_NUM` column. Compare `CRTFD_BED_CNT`. Your own knowledge of these hospitals is also a valid check: does 968 sound right for Parkland's licensed beds?

**Five extreme values (most likely to be errors).**

- [ ] West Virginia 2024, `mrsa_pct_resistant` = 64.4 (38 of 59). Highest MRSA in 2024. Check on the CDC MRSA page, Year 2024. ___
- [ ] Puerto Rico 2024, `cre_pct_resistant` = 43.2 (118 of 273). By far the highest CRE. Check: https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance/profile/carbapenem-resistant-enterobacterales, Year 2024. Does this match what you know about carbapenemase-producing organisms in Puerto Rico? ___
- [ ] Arkansas 2024, `vre_faecium_pct_resistant` = 78.0. Check: https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance/profile/vancomycin-resistant-enterococcus-faecium ___
- [ ] North Dakota 2024, `mrsa_pct_resistant` = 14.3. Lowest MRSA. Check on the CDC MRSA page. ___
- [ ] AdventHealth Orlando (FL), CCN 100007, 3,289 certified beds in 2024. Largest hospital in the file. Check at CMS as above. ___

**Insufficient-data cells (the zeros that are not zeros).**

- [ ] Vermont 2011, MRSA: atlas says `insufficient_data` with blank percent. CDC's map for 2011 shows Vermont as insufficient data (or 0 of 0). ___
- [ ] Alaska 2024, MRSA: `insufficient_data`. CDC shows "Insufficient Data." ___

**Five random rows (chosen by computer, seed 11).** All CRE; check on the CDC CRE page.

- [ ] South Carolina 2012: 1.4% (7 of 497). ___
- [ ] Minnesota 2023: 0.9% (4 of 462). ___
- [ ] Vermont 2019: 0.0% (0 of 44). A real zero: 44 were tested. ___
- [ ] Vermont 2012: 0.0% (0 of 36). ___
- [ ] North Dakota 2017: insufficient data. ___

**One independent cross-check.**

- [ ] Critical access hospitals, 2024: the atlas counts **1,368** nationally. The Flex Monitoring Team (University of Minnesota and partners) reports "over 1,300" and keeps a list at https://www.flexmonitoring.org/critical-access-hospital-locations-list. The counts should be close; small differences come from timing and from territories. ___

## Part 4: Your decisions (10 min)

The build made these choices provisionally. Agree or change each. Changing one means editing `config.json` (I can do it) and re-running; every table and the map update together.

- [ ] **1. COVID-era temporary "hospitals."** Exclude short-term hospitals listing 2 or fewer certified beds? *Yes (recommended):* removes 225 to 273 surgery centers and freestanding ERs in 2020 to 2022 (146 in Texas in 2020), and only 1 to 5 real hospitals in other years. *No:* Texas would appear to gain about 140 tiny hospitals in 2020 and lose them in 2023. Your choice: ___
- [ ] **2. What counts as "small."** *Fewer than 100 beds (recommended):* a common cutoff; 51.6% of hospitals in 2024. *Fewer than 50 beds:* stricter. *Fewer than 200 beds:* matches CDC's own national split (column `hosp_lt200_beds` is already included). Your choice: ___
- [ ] **3. Critical access hospitals.** Your brief says "short-term hospitals." CMS lists critical access hospitals as a separate subtype. *Count both together (recommended),* since critical access hospitals are the smallest rural general hospitals and are the point of the atlas; both are also kept as separate columns. *Short-term only:* drops 1,368 hospitals. Your choice: ___
- [ ] **4. VRE.** CDC publishes *E. faecalis* and *E. faecium* separately. *Keep both, plus a pooled "both species" value labeled as the atlas's own calculation (recommended).* *Species only:* drop the pooled value. Your choice: ___
- [ ] **5. Rural definition.** *CMS's own rural flag in the Provider of Services file (recommended):* simple and in the same file. *Federal Office of Rural Health Policy definition:* broader; would need an extra county and census tract lookup (a version 1.1 task). Your choice: ___
- [ ] **6. The orange "top third on both" dots on the scatter chart.** *Keep, with the caution text (recommended):* it answers your brief's question directly. *Remove:* the chart then shows dots only, which is more neutral given CDC's caution about comparing states. Your choice: ___
- [ ] **7. Names.** Repository `state-resistance-small-hospital-atlas`, version 1.0.0, data under CC BY 4.0 and code under MIT, as in your earlier projects. Your choice: ___

## Part 5: Before it goes public (20 to 30 min)

- [ ] Rewrite the summary paragraph at the top of `README.md` in your own words (I can do it with you line by line).
- [ ] Read `docs/LIMITATIONS.md`. You agree with all 13 points and could explain each.
- [ ] Your name, ORCID, affiliation, and email are correct in `AUTHORS.json` and `CITATION.cff`.
- [ ] Open `docs/index.html` in your browser. Move the year slider, hover over Texas, sort the table. Nothing looks wrong.
- [ ] I regenerate everything with `--final` (removes the draft banner) and `tools/publish_gate.py` passes.
- [ ] On release day, add the evidence-log row (I will prepare it).

**When every box is ticked, reply in your own words that you have checked the package and approve publishing.**
