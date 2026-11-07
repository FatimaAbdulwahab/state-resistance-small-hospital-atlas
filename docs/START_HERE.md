# Start here

*A one-page explainer of Project 4, written so you could read it aloud to a friend outside microbiology.*

## What you are building, in one sentence

A free online map and table showing, for every U.S. state from 2011 to 2024, how common three dangerous drug-resistant bacteria are in hospital infections, next to how many of that state's hospitals are small or rural.

## Why it matters

Small and rural hospitals often have small laboratories, fewer infectious disease specialists, and less access to rapid testing. When resistance is common in a state, those hospitals still have to recognize it and act on it. Until now, the resistance numbers (from CDC) and the hospital numbers (from Medicare) lived in two separate places. Put side by side, they show where small hospitals carry a large share of care in states where resistance is high. That helps state health departments, laboratory networks, and hospital associations decide where support, training, and testing help would reach the most hospitals.

## Where the information comes from

- **CDC's Antimicrobial Resistance & Patient Safety Portal.** Hospitals report certain infections to CDC. For each state and year, CDC publishes what percent of bacteria from those infections were resistant. One row looks like: *Texas, 2024, MRSA: 270 of 627 tested were resistant, 43.1%.* Free and public.
- **Medicare's Provider of Services file.** The federal list of every Medicare-certified hospital, updated every quarter. One row looks like: *a critical access hospital in Sonora, Texas, 12 certified beds, flagged rural.* Free and public.

## What you will have at the end

1. A **dataset** with a permanent citation number (a DOI from Zenodo): one row per state per year, 728 rows.
2. A **public map** on GitHub Pages anyone can open, with a year slider, a hover card for each state, a scatter chart, and a sortable table.
3. A **public project page** on GitHub with the code, so anyone can rebuild the numbers.
4. Supporting files: a codebook, a limitations page, a quality report, and a 60-second talk track.

## How it connects to your work

You have worked in both an academic medical center laboratory and a community hospital laboratory, and you have run identification and susceptibility testing on BioFire, BD Phoenix, and MALDI-TOF. This atlas describes the setting you now work in: the smaller hospital that sees resistant organisms without the resources of a large center. It sits alongside your other projects on rapid resistance testing and its agreement with growth-based results.

## What you need to do, and how long it takes

1. Answer a few decisions in the checklist (10 min).
2. Check the results by hand against CDC and CMS (1 to 2 hours, one sitting).
3. Rewrite the README summary in your own words (20 min, I can help line by line).
4. Approve publishing (5 min). Then GitHub, the map, and the DOI take about 20 minutes together.

## The steps ahead

1. Data collected (done)
2. Data cleaned and combined (done)
3. Quality checks run (done, all pass)
4. Public map built (done, marked draft)
5. Documents and your checklist (done)
6. You check everything, then we publish

**Good news on the January 2027 decision:** your plan said the atlas would fall back to published state figures if the portal could not export state tables. It turned out CDC's pages contain the complete state tables, with counts and confidence intervals. That decision is already settled.
