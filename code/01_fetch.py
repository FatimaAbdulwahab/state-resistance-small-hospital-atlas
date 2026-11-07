#!/usr/bin/env python3
"""
01_fetch.py - Collect every raw input for the atlas, with provenance.

Plain-language summary: this script downloads the two public sources the atlas
is built from and saves them, unchanged or lightly trimmed, in data/raw/. Every
file it saves is logged in data/raw/PROVENANCE.txt with its size, a digital
fingerprint (SHA-256), the web address it came from, and the date. You do not
need to open this file; you only need to run it if you want to rebuild.

Sources
  1. CDC Antimicrobial Resistance & Patient Safety Portal (AR&PSP),
     https://arpsp.cdc.gov - one public profile page per resistance phenotype.
     Each page embeds the full state-by-year table that drives its "by State"
     map (percent resistant, resistant count, isolates tested, 95% CI,
     suppression flag) and a national table by facility type. We save the
     page HTML and extract those embedded tables to CSV.
  2. CMS Provider of Services (POS) file, Hospital & Non-Hospital Facilities,
     December (Q4) release for each year 2011-2024, from data.cms.gov. The
     download URLs come from the data.cms.gov catalog (data.json); CMS rotates
     them, so the script rediscovers them from the catalog every run. Only
     hospital rows (PRVDR_CTGRY_CD = 01) and the columns the atlas needs are
     kept, to keep the repository small; the full-file SHA-256 is logged.
"""
import csv, datetime, hashlib, io, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROV = os.path.join(RAW, "PROVENANCE.txt")
UA = {"User-Agent": "state-resistance-atlas/1.0 (open research pipeline)"}

ARPSP_BASE = "https://arpsp.cdc.gov/psp/listing/antimicrobial-resistance/profile/"
PHENOTYPES = {
    "MRSA": "methicillin-resistant-staphylococcus-aureus",
    "CRE": "carbapenem-resistant-enterobacterales",
    "VRE_faecalis": "vancomycin-resistant-enterococcus-faecalis",
    "VRE_faecium": "vancomycin-resistant-enterococcus-faecium",
}
ARPSP_DOCS = [
    "https://arpsp.cdc.gov/resources/AR_DataMethodology_2026.pdf",
    "https://arpsp.cdc.gov/resources/AR_Data_Dictionary_2023.pdf",
    "https://arpsp.cdc.gov/resources/Guide_to_NHSN_HAI_Pathogen_and_AR_Data_2026.pdf",
]
# Facility type codes as defined in the portal's own front-end code.
FACILITY_LABELS = {"109": "General Acute Care Hospitals",
                   "110": "Long Term Acute Care Hospitals",
                   "111": "Inpatient Rehabilitation Facilities"}

CMS_CATALOG = "https://data.cms.gov/data.json"
POS_TITLE = "Provider of Services File - Hospital & Non-Hospital Facilities"
YEARS = range(2011, 2025)
POS_KEEP = ["PRVDR_NUM", "FAC_NAME", "CITY_NAME", "STATE_CD", "FIPS_STATE_CD",
            "FIPS_CNTY_CD", "PRVDR_CTGRY_CD", "PRVDR_CTGRY_SBTYP_CD",
            "PGM_TRMNTN_CD", "CBSA_URBN_RRL_IND", "CRTFD_BED_CNT", "BED_CNT"]


def get(url, timeout=600):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def log(path, url, digest, nbytes, note=""):
    line = " | ".join([datetime.date.today().isoformat(), os.path.relpath(path, RAW),
                       f"{nbytes} bytes", f"sha256:{digest}", url, note]).rstrip(" |")
    with open(PROV, "a") as f:
        f.write(line + "\n")


def save(path, data, url, note=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    log(path, url, hashlib.sha256(data).hexdigest(), len(data), note)


def extract_tables(html):
    """Return (state_rows, facility_rows) embedded in a portal profile page."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, flags=re.S)
    s = json.loads('"' + "".join(chunks) + '"')  # undo JSON string escaping
    dec = json.JSONDecoder()
    state_rows, fac_rows = [], []
    for m in re.finditer(r'"data":\[\{', s):
        try:
            arr, _ = dec.raw_decode(s, m.start() + 7)
        except ValueError:
            continue
        if arr and "state" in arr[0]:
            state_rows.extend(arr)
        elif arr and "facility" in arr[0]:
            fac_rows.extend(arr)
    return state_rows, fac_rows


def fetch_arpsp():
    out_s = os.path.join(RAW, "arpsp", "arpsp_state_year.csv")
    out_f = os.path.join(RAW, "arpsp", "arpsp_national_facility_type.csv")
    s_fields = ["phenotype_key", "phenotype", "state", "stateId", "year", "eventType",
                "eventTypeId", "percentResistant", "resistantCount",
                "isolatesTestedCount", "lowerCi", "upperCi", "suppressed"]
    f_fields = ["phenotype_key", "phenotype", "facility", "facility_label", "year",
                "percentResistant", "resistantCount", "isolatesTestedCount",
                "lowerCi", "upperCi", "suppressed"]
    srows, frows = [], []
    for key, slug in PHENOTYPES.items():
        url = ARPSP_BASE + slug
        data = get(url)
        save(os.path.join(RAW, "arpsp", f"{slug}.html"), data, url,
             "profile page; state and facility tables are embedded in the page data")
        st, fa = extract_tables(data.decode("utf-8"))
        if not st:
            sys.exit(f"No state table found on {url}; the page layout may have changed.")
        clean = lambda p: re.sub(r"<[^>]+>", "", p)
        for r in st:
            srows.append({**{k: r.get(k) for k in s_fields}, "phenotype_key": key,
                          "phenotype": clean(r["phenotype"])})
        for r in fa:
            frows.append({**{k: r.get(k) for k in f_fields}, "phenotype_key": key,
                          "phenotype": clean(r["phenotype"]),
                          "facility_label": FACILITY_LABELS.get(r["facility"], "")})
        print(f"  AR&PSP {key}: {len(st)} state rows, {len(fa)} facility-type rows")
    for path, fields, rows in [(out_s, s_fields, srows), (out_f, f_fields, frows)]:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        with open(path, "rb") as f:
            b = f.read()
        log(path, "derived from the profile pages above", hashlib.sha256(b).hexdigest(),
            len(b), "extracted by 01_fetch.py extract_tables()")
    for url in ARPSP_DOCS:
        try:
            save(os.path.join(RAW, "arpsp", "docs", os.path.basename(url)), get(url), url,
                 "CDC methodology/reference document")
        except Exception as e:
            print(f"  warning: could not fetch {url}: {e}")


def pos_urls():
    cat = json.loads(get(CMS_CATALOG))
    found = {}
    for ds in cat["dataset"]:
        # Hospital files are listed either under their own title or under the
        # "Quality Improvement and Evaluation System" dataset (not the iQIES one).
        if not (ds["title"].startswith(POS_TITLE) or
                ds["title"].startswith("Provider of Services File - Quality Improvement")):
            continue
        for d in ds.get("distribution", []):
            u = d.get("downloadURL") or ""
            t = d.get("title") or ds["title"]
            m = re.search(r"(\d{4})-12-\d\d$", t)
            if m and u.lower().endswith(".csv") and "CLIA" not in u.upper():
                found[int(m.group(1))] = (t, u)
    return found


def fetch_pos():
    urls = pos_urls()
    for y in YEARS:
        if y not in urls:
            sys.exit(f"No December POS hospital file listed for {y} in {CMS_CATALOG}")
        title, url = urls[y]
        out = os.path.join(RAW, "pos", f"pos_hospitals_dec{y}.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        data = get(url, timeout=1800)
        digest = hashlib.sha256(data).hexdigest()
        text = data.decode("latin-1")
        rdr = csv.DictReader(io.StringIO(text))
        rows = [{k: r.get(k, "") for k in POS_KEEP} for r in rdr
                if (r.get("PRVDR_CTGRY_CD") or "").strip().lstrip("0") == "1"]
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=POS_KEEP)
        w.writeheader()
        w.writerows(rows)
        b = buf.getvalue().encode("utf-8")
        with open(out, "wb") as f:
            f.write(b)
        log(out, url, hashlib.sha256(b).hexdigest(), len(b),
            f"hospital rows only, {len(POS_KEEP)} columns; full file {len(data)} bytes "
            f"sha256:{digest}; URL found in {CMS_CATALOG} under '{title}'")
        print(f"  POS {y}: {len(rows)} hospital rows kept")


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    with open(PROV, "w") as f:  # fresh log every full run
        f.write(f"# Provenance log. Format: access date | file | size | sha256 | source URL | note\n")
    print("CDC AR&PSP ...")
    fetch_arpsp()
    print("CMS Provider of Services ...")
    fetch_pos()
    print("Done.")
