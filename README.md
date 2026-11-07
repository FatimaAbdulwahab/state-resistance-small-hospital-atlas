# State Atlas of Hospital Resistance and Small Hospitals

**Status:** Released · version 1.0.0 · DOI assigned at release · [Public map](https://fatimaabdulwahab.github.io/state-resistance-small-hospital-atlas/)

An open state-by-year table for the 50 states, the District of Columbia, and Puerto Rico, 2011 to 2024. It joins CDC's percent resistance for MRSA, carbapenem-resistant Enterobacterales (CRE), and vancomycin-resistant enterococci (VRE) to counts of Medicare-certified short-term and critical access hospitals by bed size and rural location. Side by side, they show where resistance is high and where much of the hospital network is made up of small and rural hospitals: the community hospitals and their laboratories that must recognize resistant organisms without the resources of a large medical center.

In 2024, the atlas counts 4,500 general hospitals (3,132 short-term acute care and 1,368 critical access). Of these, 51.6% have fewer than 100 certified beds, yet they hold only 10.6% of beds. In 31 of 52 places, most hospitals are small.

## What is in it

| File | What it is |
|---|---|
| `data/processed/atlas_state_year.csv` | **The main table.** 728 rows (52 places × 14 years), 61 columns. |
| `data/processed/resistance_state_year_long.csv` | CDC resistance by state, year, organism, and infection type. |
| `data/processed/hospital_list_by_year.csv` | Every counted (or excluded) hospital, every year, for checking by hand. |
| `data/processed/qa_report.txt` | Quality checks. Read this first. |
| `docs/index.html` | The public map (served by GitHub Pages). |
| `docs/CODEBOOK.md` | Every column explained. |
| `docs/LIMITATIONS.md` | What the atlas cannot tell you. |
| `docs/START_HERE.md` | A plain-language overview. |

## Sources

1. **CDC Antimicrobial Resistance & Patient Safety Portal**, AR HAI dataset, profile pages for methicillin-resistant *Staphylococcus aureus*, carbapenem-resistant Enterobacterales, and vancomycin-resistant *Enterococcus faecalis* and *E. faecium*, 2011–2024. https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance. Percent resistant among isolates from central line bloodstream infections, catheter urinary tract infections, and surgical site infections reported to the National Healthcare Safety Network. Accessed 2026-11-06.
2. **CMS Provider of Services File, Hospital & Non-Hospital Facilities**, December release of each year 2011–2024. https://data.cms.gov/provider-characteristics/hospitals-and-other-facilities/provider-of-services-file-hospital-non-hospital-facilities. Accessed 2026-11-06.

Every download is logged with its date, size, and SHA-256 fingerprint in `data/raw/PROVENANCE.txt`.

## Key rules

- Hospitals counted: active (termination code 00) short-term acute care (subtype 01) and critical access (subtype 11) hospitals. Short-term hospitals listing 2 or fewer certified beds are excluded; in 2020 to 2022 these were mostly temporary COVID-era enrollments of surgery centers and freestanding emergency rooms.
- Small: fewer than 100 certified beds. Rural: the CMS rural flag (outside a metropolitan core-based statistical area). That flag marks 266 of 1,368 critical access hospitals (19.4%) as urban in 2024, so a second measure, "small and rural, or critical access," counts every critical access hospital (39.4% of hospitals in 2024, against 33.5% by the flag alone).
- Children's, psychiatric, rehabilitation, and long-term care hospitals are not counted.
- CDC withholds a percent when fewer than 20 isolates were tested. The portal stores most of these as 0 of 0 in 2011 to 2022 (and one cell each in 2023 and 2024) and as blanks otherwise; the atlas records both as insufficient data, never as 0%. CDC rounds halves up (31.25% is published as 31.3%); the atlas keeps CDC's published values.
- All settings are in `config.json`.

CDC cautions against drawing conclusions about change over time or about a state compared with the nation. See `docs/LIMITATIONS.md`.

## Rebuild it

Requires Python 3.10 or later.

```
pip install -r requirements.txt
python code/01_fetch.py     # download sources, about 3 minutes
python code/02_build.py     # clean and join
python code/03_qa.py        # quality checks; ends with "Checks failed: 0"
python code/04_site.py      # build the map page
python code/05_docs.py      # build this README and the talk track from stats.json
```

## License

Data and documentation: CC BY 4.0. Code: MIT. See `LICENSE`. Underlying data are U.S. federal government works from CDC and CMS.

## Citation

Abdulwahab F. *State Atlas of Hospital Resistance and Small Hospitals* (version 1.0.0) [dataset]. Zenodo; forthcoming. DOI assigned at release.

See `CITATION.cff`.

## Author

Fatima Abdulwahab, Independent Researcher, Dallas, Texas. ORCID [0009-0008-2298-8386](https://orcid.org/0009-0008-2298-8386). abdulwahabfatima43@gmail.com

Related work: [U.S. Rapid Panel Resistance Marker Concordance Benchmark](https://github.com/FatimaAbdulwahab/us-rapid-panel-amr-concordance) · [Reference Isolate Verification Crosswalk](https://github.com/FatimaAbdulwahab/ar-isolate-bank-panel-crosswalk) · [FDA-Cleared Rapid Resistance Test Landscape](https://github.com/FatimaAbdulwahab/fda-rapid-resistance-test-landscape)

*Built with AI assistance (Claude) for code and data processing. The author made the analytic decisions and verified the results against the sources.*
