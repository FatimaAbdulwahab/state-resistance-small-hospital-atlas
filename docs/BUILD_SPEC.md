# Build spec

*Plain-language summary: the one-page plan the whole build follows. If the project changes shape, this file changes first. Each line in italics says what the field means for you.*

```
PROJECT:       State Atlas of Hospital Resistance and Small Hospitals (Project 4).
               Archetypes: dataset + atlas (map).
QUESTION:      In which U.S. states is resistance among hospital-reported infections
               high, and how much of the state's general hospital network is small
               and rural?
SOURCES:       1. CDC AR & Patient Safety Portal, AR HAI dataset, 4 phenotype profile
                  pages (MRSA, CRE, VR E. faecalis, VR E. faecium), 2011-2024,
                  state x year x infection type; accessed 2026-11-06; U.S. government work.
               2. CMS Provider of Services File, Hospital & Non-Hospital Facilities,
                  December release 2011-2024 (14 files, URLs from data.cms.gov/data.json);
                  accessed 2026-11-06; U.S. government work.
UNIT:          State-year: 50 states + DC + PR, 2011-2024 = 728 rows.
MEASURES:      Percent resistant, resistant n, tested n, 95% CI per organism (CDC, all
               infection types combined); pooled VRE (derived, mid-P CI); counts of
               active short-term acute and critical access hospitals by certified bed
               band and CMS rural flag; shares of hospitals and beds that are small
               (<100 beds), rural, small and rural, critical access.
OUTPUTS:       data/processed/atlas_state_year.csv (main), resistance long table,
               hospital list by year, QA report, stats.json; docs/index.html (map);
               README, codebook, limitations, verification checklist, talk track.
VENUES:        GitHub repository -> GitHub release v1.0.0 -> Zenodo DOI (via GitHub
               integration) -> GitHub Pages map from /docs. Target dates in the plan:
               table on Zenodo August 2027, map live August 2027 (built early).
VERIFY POINTS: 2-bed exclusion rule; small = <100 beds; count critical access
               hospitals; pooled VRE; CMS rural flag; scatter highlight; names and
               licenses; hand checks of 20 rows (docs/VERIFY_CHECKLIST.md).
LICENSE:       Data and docs CC BY 4.0; code MIT.
DECISIONS:     As released in v1.0.0 after the author's review (2026-11-06): exclude
               short-term hospitals with <= 2 certified beds; small = < 100 beds;
               count critical access hospitals; keep pooled VRE (labeled derived);
               keep the CMS rural flag and add "small and rural, or critical
               access" for the 1 in 5 critical access hospitals flagged urban;
               keep the scatter highlight and also label the highest and lowest
               resistance; children's hospitals excluded; names and licenses as
               in earlier projects. The plan's January 2027 fallback (published state
               figures only) is not needed: full state tables are embedded in the
               portal pages.
```

- *Question: what a reader learns from the atlas.*
- *Sources: two free federal sources; every download is fingerprinted in `data/raw/PROVENANCE.txt`.*
- *Unit: every row of the main table is one state in one year.*
- *Measures: each column is defined in `docs/CODEBOOK.md`.*
- *Verify points: the decisions you rule on in `docs/VERIFY_CHECKLIST.md`, Part 4.*
