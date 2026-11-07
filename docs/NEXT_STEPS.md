# Next steps

*What later versions could add, so version 1.0.0 is understood as a first step.*

- **Version 1.1, when CDC posts 2025 data.** Re-run the pipeline; add the December 2025 Provider of Services file. CMS moved hospital files to a new "Quality Improvement and Evaluation System" release series in 2025; `01_fetch.py` already searches both names.
- **Alternate rural definition.** Add the Federal Office of Rural Health Policy definition (rural counties plus rural census tracts) as a second set of columns.
- **County view.** Hospital counts and rural status can be mapped by county from the same CMS file; resistance stays state-level.
- **Laboratory context.** Join each hospital's CLIA laboratory certificate (the Provider of Services Clinical Laboratories file) to show how many small hospitals run their own microbiology testing. This connects the atlas to your rapid-testing projects.
- **Other organisms.** The same method works for every phenotype on the portal (for example carbapenem-resistant *Acinetobacter* and *Pseudomonas aeruginosa*, ESBL-type cephalosporin resistance).
- **Short data note.** A brief data descriptor or research letter describing the atlas, its methods, and the "0 of 0" pitfall in older portal data.
