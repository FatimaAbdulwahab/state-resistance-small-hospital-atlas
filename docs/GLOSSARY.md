# Glossary

Plain definitions of the terms you will see in this project. The last section adds terms specific to this atlas.

**Abstract.** A short summary at the top of a paper, usually 150 to 300 words.

**Archive (release archive).** A single zip file containing a frozen copy of the whole project at one point in time.

**arXiv, medRxiv, bioRxiv, engrXiv.** Free public websites where researchers post papers before or alongside journal review. Each covers different fields.

**Citation file (CITATION.cff).** A small file that tells people and software exactly how to cite your project.

**Codebook.** A list explaining every column in your data: what it means, its units, and where it came from.

**Commit.** A saved snapshot of changes to the project, with a note describing what changed.

**Dataset.** An organized table (or set of tables) of information, like a spreadsheet.

**Docket.** The public file for a proposed government rule. Comments submitted to it become part of the official record.

**DOI (Digital Object Identifier).** A permanent link and ID for your work, like a library call number that never changes. It looks like `10.5281/zenodo.1234567`.

**Draft stamp.** A draft label on every figure and document until you have checked everything. It is removed only after your approval.

**Endorsement (arXiv).** A one-time approval some arXiv categories require from an existing author before your first post there.

**Figure.** A chart, graph, or map in a paper or report.

**GitHub.** A website that stores project files publicly and keeps every past version.

**License.** The terms under which others may reuse your work. CC BY 4.0 means anyone can reuse it if they credit you. MIT is a common equivalent for code.

**Limitations.** An honest list of what the project cannot tell you and where its data is weak. Every credible project has one.

**Metadata.** Information about your work: title, authors, description, keywords, license.

**Open data.** Information published free for anyone to use, usually by governments or research bodies.

**ORCID iD.** A free, permanent ID number for researchers, so your work is linked to you even if your name is spelled differently somewhere. It looks like `0000-0002-1825-0097`.

**Pipeline.** The set of scripts that downloads the data, cleans it, and produces the results, in order. Running it again gives the same results.

**Preprint.** A paper posted publicly before peer review.

**Provenance.** A record of exactly where each piece of data came from and when it was downloaded.

**Public comment.** Written feedback submitted to a government agency on a proposed rule, during a set comment period.

**QA (quality assurance) report.** A file listing the checks run on the data: counts, matches, and anything unusual.

**README.** The front page of a project. It explains what the project is and how to use it.

**Release.** A named, frozen version of the project (for example v1.0) that can be cited.

**Reproduce.** To re-run the project from scratch and get the same numbers. It proves the results are real.

**Repository (repo).** The project folder that lives online, usually on GitHub, with its full history.

**Sandbox.** A practice version of a website (like Zenodo's) for testing before doing it for real.

**Script.** A small program file that does one job, such as downloading data.

**Spot check.** Picking a few rows by hand and comparing them to the original source.

**Stats file.** A file the pipeline writes with every number used in the paper, so the text always matches the data.

**Token.** A temporary password that lets Claude upload to GitHub or Zenodo on your behalf. You can cancel it at any time.

**Tracking number.** The receipt ID you get after submitting a public comment. Save it.

**Vintage.** The year or edition of a data source.

**Zenodo.** A free, permanent research archive run by CERN. It gives your project a DOI.

## Terms specific to this atlas

**AR & Patient Safety Portal (AR&PSP).** CDC's public website for antimicrobial resistance and healthcare infection data, at arpsp.cdc.gov.

**NHSN (National Healthcare Safety Network).** CDC's system where hospitals report healthcare-associated infections and the bacteria that caused them.

**HAI (healthcare-associated infection).** An infection a patient gets while receiving care. This atlas uses three kinds: central line bloodstream infections (CLABSI), catheter urinary tract infections (CAUTI), and surgical site infections (SSI).

**Percent resistant.** Of the isolates tested for a drug class, the share that tested resistant.

**Confidence interval.** A range that shows how precise a percent is. Small numbers of isolates give wide ranges.

**Insufficient data.** CDC publishes no percent when fewer than 20 isolates were tested.

**Provider of Services (POS) file.** Medicare's list of every certified provider, with type, location, beds, and status, released every quarter.

**CCN (CMS Certification Number).** The six-digit ID Medicare gives each hospital.

**Critical access hospital.** A Medicare designation for small rural hospitals, generally limited to 25 acute inpatient beds and distant from other hospitals. In the CMS file some list more certified beds (swing or unit beds), and about 1 in 5 carry the CMS urban flag.

**Certified beds.** The beds a hospital is certified to use for Medicare patients, as listed in the POS file.

**FIPS code.** The federal number for a state (Texas is 48).

**Choropleth.** A map that colors each area by a value.

**GitHub Pages.** Free website hosting from GitHub. The atlas map is served from the `docs/` folder.
