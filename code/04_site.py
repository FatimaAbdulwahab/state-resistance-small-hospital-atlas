#!/usr/bin/env python3
"""
04_site.py - Build the public map page (docs/index.html) from the finished table.

Plain-language summary: this script takes atlas_state_year.csv and stats.json
and writes one self-contained web page, docs/index.html, which GitHub Pages
serves as the public map. Every number on the page comes from those two files,
so the map cannot disagree with the dataset. The page carries a DRAFT banner
until you run it with --final after checking the data.

  python code/04_site.py            # draft
  python code/04_site.py --final    # after verification
"""
import json, math, os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
SRC = os.path.join(ROOT, "site_src")
META = json.load(open(os.path.join(ROOT, "release.json")))
FINAL = "--final" in sys.argv

a = pd.read_csv(os.path.join(P, "atlas_state_year.csv"), dtype={"state_fips": str})
stats = json.load(open(os.path.join(P, "stats.json")))
num = lambda v: None if (v is None or (isinstance(v, float) and math.isnan(v))) else (round(float(v), 1) if isinstance(v, float) else int(v))

rows = []
for _, r in a.iterrows():
    d = {"u": r.usps, "name": r.state_name, "f": r.state_fips, "y": int(r.year),
         "ht": int(r.hosp_total), "nsm": int(r.hosp_small), "nru": int(r.hosp_rural),
         "nsr": int(r.hosp_small_rural), "nca": int(r.hosp_critical_access), "ncu": int(r.hosp_critical_access_cms_urban),
         "hsm": num(r.pct_hosp_small), "hru": num(r.pct_hosp_rural), "hsr": num(r.pct_hosp_small_rural),
         "hca": num(r.pct_hosp_critical_access), "hsc": num(r.pct_hosp_small_rural_or_cah), "hbs": num(r.pct_beds_in_small)}
    for p in ["mrsa", "cre", "vre_faecalis", "vre_faecium", "vre_pooled"]:
        ok = r[f"{p}_status"] in ("reported", "derived")
        d[p] = [num(r[f"{p}_pct_resistant"]), num(r[f"{p}_n_resistant"]), num(r[f"{p}_n_tested"]),
                num(r[f"{p}_ci_lower"]), num(r[f"{p}_ci_upper"])] if ok else None
    rows.append(d)
data = {"rows": rows, "fips": sorted(a.state_fips.unique().tolist())}

access = "unknown"
prov = os.path.join(ROOT, "data", "raw", "PROVENANCE.txt")
for line in open(prov):
    if not line.startswith("#"):
        access = line.split(" | ")[0]
        break

html = open(os.path.join(SRC, "template.html")).read()
rep = {
    "/*__TOPO__*/null": open(os.path.join(SRC, "vendor", "states-10m.json")).read(),
    "/*__DATA__*/null": json.dumps(data, separators=(",", ":")),
    "__FIRST__": str(stats["first_year"]), "__LATEST__": str(stats["latest_year"]),
    "__HOSP__": f"{stats['hospitals_latest']:,}", "__PCT_SMALL__": str(stats["pct_small_latest"]),
    "__PCT_BEDS_SMALL__": str(stats["pct_beds_in_small_latest"]),
    "__CAH__": f"{stats['critical_access_latest']:,}", "__ACCESS__": access,
    "__VERSION__": META["version"],
    # No DOI exists until Zenodo archives the GitHub release; the footer then
    # simply omits it, and a later commit to main adds it (see docs/PUBLISH_GUIDE.md).
    "__DOI__": (f' <a href="https://doi.org/{META["doi"]}">https://doi.org/{META["doi"]}</a>.'
                if META.get("doi") else ""),
    "<!--DRAFT-->": "" if FINAL else '<div class="draft" role="status">DRAFT: not yet verified by the author. Numbers may change before release.</div>',
}
for k, v in rep.items():
    if k not in html:
        sys.exit(f"template placeholder {k} missing")
    html = html.replace(k, v)
os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
out = os.path.join(ROOT, "docs", "index.html")
open(out, "w").write(html)
# A plain data file next to the page, for anyone who wants the numbers behind the map.
os.makedirs(os.path.join(ROOT, "docs", "data"), exist_ok=True)
a.to_csv(os.path.join(ROOT, "docs", "data", "atlas_state_year.csv"), index=False)
open(os.path.join(ROOT, "docs", ".nojekyll"), "w").close()
# The map libraries are served as separate files (with their licenses) next to the page.
import shutil
os.makedirs(os.path.join(ROOT, "docs", "vendor"), exist_ok=True)
for fn in ["d3.min.js", "topojson-client.min.js", "LICENSE-d3.txt", "LICENSE-topojson-client.txt", "LICENSE-us-atlas.txt"]:
    shutil.copy(os.path.join(SRC, "vendor", fn), os.path.join(ROOT, "docs", "vendor", fn))
print(f"wrote {out} ({os.path.getsize(out):,} bytes){' FINAL' if FINAL else ' DRAFT'}")
