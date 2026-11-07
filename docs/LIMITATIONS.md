# Limitations

*Plain-language summary: what this atlas cannot tell you, and where its data is weak. Read this before quoting any number. Every claim in the README, the map, or a future paper has to stay inside these limits.*

1. **Resistance comes from reported infections, not all patients.** CDC's figures cover isolates from three kinds of healthcare-associated infection (central line bloodstream infections, catheter urinary tract infections, and surgical site infections) that hospitals report to the National Healthcare Safety Network (NHSN). They are not all clinical cultures and not community infections. A state's MRSA percent here is not the same as its hospital antibiogram.

2. **The two halves are joined by state, not by hospital.** The atlas shows that a state has high resistance *and* many small hospitals. It cannot show that resistance is high *in* those small hospitals. CDC does not publish state figures by hospital size. Its national figures split only by facility type and by fewer or more than 200 beds.

3. **CDC warns against two comparisons.** CDC's methods note says these data should not be used to draw definitive conclusions about change over time, or about one state's resistance compared with the nation's. Reasons it gives: NHSN definitions and protocols changed over the years, laboratories use different breakpoint versions, and reporting mandates and data validation differ by state. The map's year slider and the "top third on both" highlight are descriptive and must not be presented as rankings or trends.

4. **Small states often have no figure.** CDC withholds a percent when fewer than 20 isolates were tested. Across all years this affects 68 MRSA, 39 CRE, 93 *E. faecalis*, and 227 *E. faecium* state-years out of 728 each. These are often the most rural states, exactly where the question matters most.

5. **Pooled VRE is the atlas's own calculation.** CDC publishes *E. faecalis* and *E. faecium* separately. The pooled value adds their counts. It is computable only when both species are published, and its mix depends on how many of each species a state reported. Use the species columns for any formal statement.

6. **Older CDC years store "no data" as zeros.** Cells with too few isolates appear on the portal as 0 of 0 in most of 2011 to 2022 and in one cell each in 2023 and 2024; other 2023 and 2024 cells are blank. The atlas converts these to "insufficient data." Anyone using the portal's numbers directly could mistake them for 0% resistance.

7. **Hospital counts are a December snapshot.** Each year uses the December Provider of Services file. A hospital that opened or closed mid-year appears or disappears in that year's count. The CMS termination code and bed counts are as CMS recorded them; errors in the CMS file pass through.

8. **The 2-bed rule is a judgment call.** In 2020 to 2022 CMS listed 225 to 273 surgery centers and freestanding emergency rooms as active short-term hospitals, almost all with 1 or 2 beds, under temporary COVID-era flexibilities. The atlas excludes short-term hospitals with 2 or fewer certified beds. This also drops 1 to 5 genuine very small hospitals in ordinary years. Every excluded row is listed in `hospital_list_by_year.csv`.

9. **"Rural" is the CMS flag.** It marks hospitals outside a metropolitan core-based statistical area. Other definitions (for example the Federal Office of Rural Health Policy's, which adds rural census tracts inside metropolitan counties) would classify some hospitals differently. The flag disagrees with the critical access designation for about 1 in 5 critical access hospitals: in 2024, 266 of 1,368 carry the urban flag (critical access hospitals can qualify through state rural designations or rural census tracts inside metropolitan counties). The "small and rural" measure therefore leaves those hospitals out. The column `hosp_small_rural_or_cah` counts every critical access hospital as an alternative. Also, 68 critical access hospitals list more than 25 certified beds (up to 138), likely because swing beds or psychiatric or rehabilitation units are included, so the "under 100 beds" test, not a 25-bed rule, decides whether they count as small.

10. **"Small" is a cutoff, not a fact.** Fewer than 100 certified beds is a common threshold, but not a standard one. Certified beds can differ from staffed beds. The bed-size band columns let users apply other cutoffs.

11. **Only general hospitals are counted.** Long-term acute care hospitals and inpatient rehabilitation facilities report to the CDC data but are not counted on the hospital side. Children's hospitals (CMS subtype 06) are also left out, by choice: in 2024 there were 94 active, none flagged rural, and 38 with under 100 beds, so adding them would barely change the small-and-rural measures (and would raise the small-hospital count by under 2%). Their infections are, however, included in CDC's state figures. Psychiatric and other specialty hospitals are left out too.

12. **Puerto Rico is in the state rows only.** Both sources report it at state level, but CDC excludes it from regional summaries and U.S. maps usually draw it as an inset, so it is easy to overlook.

13. **Portal page structure may change.** The CDC tables are read from data embedded in each profile page, not from a formal download service. If CDC redesigns the portal, `01_fetch.py` will stop with a clear message rather than produce wrong numbers, and will need updating.
