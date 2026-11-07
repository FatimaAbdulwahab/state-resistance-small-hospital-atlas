# Verification record, version 1.0.0

*What was checked before release, by whom, and what changed as a result.*

**Reviewer:** Fatima Abdulwahab. **Date:** 6 November 2026.

## Independent checks performed by the author

- All 23 raw files matched their recorded SHA-256 fingerprints.
- Rebuilt from the package: every processed table, `stats.json`, the QA report, the README and the map were byte-for-byte identical. QA ended "Checks failed: 0".
- Fresh download from CDC and CMS on 6 November 2026 and rebuild: outputs identical. Two CDC VRE pages had new fingerprints with the same size and identical extracted numbers (page wrapper change only).
- Separate code written by the author, not reusing the project scripts: all 11,888 CDC rows matched; every hospital count and bed total matched in all 728 state-years; pooled VRE values and intervals matched; CDC's intervals confirmed as mid-P (200 of 200 sampled MRSA intervals reproduced).
- Headline numbers confirmed: 4,500 hospitals (3,132 short-term, 1,368 critical access); 51.6% small; 10.6% of beds in small hospitals; 31 of 52 places mostly small; Texas MRSA 43.1% (270 of 627).
- All Part 3 checklist values matched the files, including West Virginia MRSA 64.4%, Puerto Rico CRE 43.2%, the Vermont and Alaska insufficient-data cells, the five random CRE rows and the five Dallas hospitals.
- Every reported percent rests on at least 20 isolates; no "0 of 0" cell appears as 0%; real zeros kept.
- The 240 dropped "New England" rows are a Census-division total equal to the sum of its six states (MRSA 2022: 428 tested).
- Map: no errors, no outside requests, no sideways scrolling on a phone.

## Changes made after review

1. **Critical access hospitals and the rural flag.** In 2024, 266 of 1,368 critical access hospitals (19%) carry the CMS urban flag, and 68 list more than 25 certified beds (up to 138). Decision: keep the CMS flag, and add `hosp_small_rural_or_cah` / `pct_hosp_small_rural_or_cah`, which counts every critical access hospital, as a map measure and table column. The map tile no longer describes critical access hospitals as "25 beds or fewer, rural". LIMITATIONS #9, the codebook and the glossary explain the mismatch.
2. **Publish gate.** Map libraries now ship as separate files in `docs/vendor/`; `tools/run_gate.sh` exempts the scripts, templates, libraries and CDC's saved pages. The gate passes on the released package.
3. **DOI order.** The DOI placeholder was removed. Version 1.0.0 is released without a DOI line; once Zenodo mints it, a commit to `main` adds it (no new release). See `docs/PUBLISH_GUIDE.md`.
4. **Wording.** "0 of 0" cells: also one cell each in 2023 and 2024 (README, LIMITATIONS #6, codebook). CDC's half-up rounding noted in the README.
5. **Scatter chart.** The highest and lowest resistance states are now labeled too (2024 MRSA: West Virginia, North Dakota).
6. **Children's hospitals.** Kept excluded, now with measured numbers in LIMITATIONS #11 (2024: 94 active, none flagged rural, 38 under 100 beds).

## Decisions as released

Exclude short-term hospitals with 2 or fewer certified beds; small = under 100 beds; count critical access hospitals; keep pooled VRE, labeled as derived; CMS rural flag plus the critical-access alternative; keep the scatter highlight; children's hospitals excluded; data CC BY 4.0, code MIT.
