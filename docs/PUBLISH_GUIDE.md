# Publish guide

*Use this only after you have finished `docs/VERIFY_CHECKLIST.md` and approved publishing. Total time: about 20 minutes. If you give me a GitHub token in the chat session, I can do steps 1 to 3 for you, as with your earlier projects; Zenodo then mints the DOI automatically.*

## Copy-ready text

- **Repository name:** `state-resistance-small-hospital-atlas`
- **Description:** `State-by-year atlas joining CDC percent resistance (MRSA, CRE, VRE) to CMS counts of small and rural hospitals, 2011-2024. Data CC BY 4.0.`
- **Release tag and title:** `v1.0.0`
- **Release notes:**
  ```
  First release. 728 state-years (50 states, DC, Puerto Rico; 2011-2024) joining CDC AR & Patient Safety Portal percent resistance for MRSA, CRE, and vancomycin-resistant E. faecalis and E. faecium to counts of active short-term acute care and critical access hospitals by certified bed size and CMS rural flag (December Provider of Services files). Includes the pipeline, QA report (0 failed checks), codebook, limitations, facility-level hospital list, and a public state map.
  ```
- **Author:** Fatima Abdulwahab, Independent Researcher, Dallas, Texas, USA, ORCID 0009-0008-2298-8386

## Why the DOI comes last

Zenodo creates the DOI only after it archives a GitHub release, so version 1.0.0 is released without one. The map footer, README, and citation file simply leave the DOI out (no placeholder). Once Zenodo mints it, step 4 adds it with an ordinary commit to `main`. That updates the map and README straight away and does **not** need a new release or a second DOI. The Zenodo record itself always shows its own DOI.

## Step 0a: Run the release gate (1 min)

In a terminal in the project folder: `sh tools/run_gate.sh`. It should end with `gate: clear`. It skips the scripts, the map template, the map libraries in `docs/vendor/`, and CDC's saved pages, whose text contains the gate's trigger words by design.

## Step 0: Zenodo switch (2 min, do this before the release)

1. Go to https://zenodo.org and log in with ORCID or GitHub.
2. Click your name (top right), then **GitHub**.
3. Click **Sync now**. After the repository exists (step 1), find `state-resistance-small-hospital-atlas` and flip its switch **On**.

Zenodo reads `.zenodo.json` in the repository for the title, author, license, and description, so you do not type them.

## Step 1: Create the repository and push (5 min)

1. Go to https://github.com/new. Name: paste the repository name. Public. Do **not** add a README, license, or .gitignore. Click **Create repository**.
2. In a terminal in the project folder:
   ```
   git init -b main
   git add -A
   git commit -m "State Atlas of Hospital Resistance and Small Hospitals v1.0.0"
   git remote add origin https://github.com/FatimaAbdulwahab/state-resistance-small-hospital-atlas.git
   git push -u origin main
   ```
   The repository page should now show the README.

## Step 2: Turn on the map (2 min)

1. On the repository page: **Settings**, then **Pages** (left menu).
2. Under **Build and deployment**, Source: **Deploy from a branch**. Branch: `main`, folder: `/docs`. Click **Save**.
3. Wait 1 to 3 minutes. The map is live at https://fatimaabdulwahab.github.io/state-resistance-small-hospital-atlas/

## Step 3: Make the release (3 min)

1. On the repository page, click **Releases**, then **Draft a new release**.
2. **Choose a tag**: type `v1.0.0`, click **Create new tag**. Title: `v1.0.0`. Paste the release notes. Click **Publish release**.
3. Within a few minutes, Zenodo (step 0) archives it and emails you. Open https://zenodo.org/account/settings/github/ to see the DOI.

## Step 4: Put the DOI everywhere (5 min, I can do this)

Send me the DOI. I add it to `release.json` and `CITATION.cff`, run `python code/04_site.py --final` and `python code/05_docs.py --final`, and commit to `main` with the message "Add Zenodo DOI". Or do it yourself the same way. No new release is needed. Then log the evidence row the same day:

| date | artifact | type | venue | URL or DOI | status |
|---|---|---|---|---|---|
| (release day) | State Atlas of Hospital Resistance and Small Hospitals v1.0.0 | dataset | Zenodo | (DOI) | published |
| (release day) | State Atlas public map | interactive map | GitHub Pages | https://fatimaabdulwahab.github.io/state-resistance-small-hospital-atlas/ | live |

Save a PDF of the Zenodo record page and of the live map (browser: Print, Save as PDF) on the same day.
