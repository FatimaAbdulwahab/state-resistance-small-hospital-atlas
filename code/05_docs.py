#!/usr/bin/env python3
"""
05_docs.py - Build README.md and docs/TALK_TRACK.md from stats.json.

Plain-language summary: the README and talk track quote numbers. Instead of
typing them by hand, this script fills them in from data/processed/stats.json,
so the words always match the data. Run with --final after verification to
change the README status line from draft to released.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = "--final" in sys.argv
s = json.load(open(os.path.join(ROOT, "data", "processed", "stats.json")))
meta = json.load(open(os.path.join(ROOT, "release.json")))
atlas_states = {}
import csv
for r in csv.DictReader(open(os.path.join(ROOT, "data", "processed", "atlas_state_year.csv"))):
    atlas_states[r["usps"]] = r["state_name"]
q = [atlas_states[u] for u in s["high_resistance_and_high_small_rural_latest"]["mrsa"]]
quad = ", ".join(q[:-1]) + (", and " if len(q) > 2 else " and ") + q[-1] if len(q) > 1 else (q[0] if q else "no state")

access = next(l.split(" | ")[0] for l in open(os.path.join(ROOT, "data", "raw", "PROVENANCE.txt")) if not l.startswith("#"))
doi = meta.get("doi")
version = meta["version"]
cite = (f"Abdulwahab F. *State Atlas of Hospital Resistance and Small Hospitals* (version {version}) "
        f"[dataset]. Zenodo; {meta.get('year', 2027) if doi else 'forthcoming'}. "
        + (f"https://doi.org/{doi}" if doi else "DOI assigned at release."))
fields = dict(s)
fields.update({
    "status": ("Released" if FINAL else "DRAFT, not yet verified by the author"),
    "version": version,
    "doi_line": (f"DOI [{doi}](https://doi.org/{doi})" if doi else "DOI assigned at release"),
    "pages_url": meta["pages_url"], "n_years": s["latest_year"] - s["first_year"] + 1,
    "access_date": access, "citation": cite, "quad_mrsa": quad,
    "pct_beds_in_small_latest_round": round(s["pct_beds_in_small_latest"]),
})
for src, dst in [("README.template.md", "README.md"), ("TALK_TRACK.template.md", os.path.join("docs", "TALK_TRACK.md"))]:
    text = open(os.path.join(ROOT, "docs_src", src)).read().format(**fields)
    open(os.path.join(ROOT, dst), "w").write(text)
    print("wrote", dst)
