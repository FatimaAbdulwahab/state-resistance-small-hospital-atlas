#!/usr/bin/env python3
"""
03_qa.py - Quality checks on the finished tables, plus the stats file.

Plain-language summary: this script re-checks the finished tables against the
raw data and against simple rules (percentages between 0 and 100, counts that
add up, every state present every year). It writes two files:
  data/processed/qa_report.txt  - every check, with PASS or FAIL. Read this first.
  data/processed/stats.json     - every number quoted in the README, the map
                                  page, and the talk track, so text and data
                                  can never disagree.
It stops with an error if any hard check fails.
"""
import json, os, random, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
build = import_module("02_build")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
CFG = json.load(open(os.path.join(ROOT, "config.json")))
atlas = pd.read_csv(os.path.join(P, "atlas_state_year.csv"), dtype={"state_fips": str})
long = pd.read_csv(os.path.join(P, "resistance_state_year_long.csv"), dtype={"state_fips": str})
hosp_list = pd.read_csv(os.path.join(P, "hospital_list_by_year.csv"), dtype=str)
nat = pd.read_csv(os.path.join(P, "resistance_national_by_facility_type.csv"))
blog = json.load(open(os.path.join(P, "build_log.json")))
YEARS = list(range(CFG["first_year"], CFG["last_year"] + 1))
PH = ["mrsa", "cre", "vre_faecalis", "vre_faecium"]
LATEST = CFG["last_year"]

lines, fails = [], []
def check(name, ok, detail=""):
    lines.append(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    if not ok:
        fails.append(name)
def note(text=""):
    lines.append(text)

note("QA REPORT - State Atlas of Hospital Resistance and Small Hospitals")
note(f"Config: {json.dumps({k: v for k, v in CFG.items() if not k.startswith('_')})}")
note()
note("== 1. Row counts and coverage ==")
check("atlas has 52 places x 14 years = 728 rows", len(atlas) == 52 * len(YEARS), f"{len(atlas)} rows")
check("no duplicate state-year rows", not atlas.duplicated(["usps", "year"]).any())
check("join matched every state-year on both sides",
      blog["join"].get("both") == len(atlas) and not blog["join"].get("left_only") and not blog["join"].get("right_only"),
      str(blog["join"]))
r = blog["resistance"]
note(f"CDC rows read: {r['cdc_rows_in']}; dropped as non-state labels: {r['cdc_rows_dropped_non_state']} "
     f"({', '.join(r['cdc_dropped_labels'])}); kept: {r['cdc_rows_kept']}")
note("Hospitals by year (POS hospital rows -> target types -> active -> 52 places -> excluded tiny -> counted):")
for y, v in blog["hospitals_by_year"].items():
    note(f"  {y}: {v['pos_hospital_rows']} -> {v['target_subtypes']} -> {v['active']} -> "
         f"{v['in_52_states']} -> -{v['excluded_tiny']} -> {v['counted']}")
note()

note("== 2. Resistance values ==")
for p in PH:
    rep = atlas[atlas[f"{p}_status"] == "reported"]
    # CDC rounds halves up (31.25 -> 31.3); recompute the same way.
    exact = 1000 * rep[f"{p}_n_resistant"].astype(float) / rep[f"{p}_n_tested"].astype(float)
    recomputed = (exact + 0.5 + 1e-9).apply(int) / 10
    diff = (recomputed - rep[f"{p}_pct_resistant"]).abs().max()
    check(f"{p}: percent = resistant / tested, rounded half-up (max gap {diff:.2f})", diff <= 0.001)
    check(f"{p}: 0 <= percent <= 100", rep[f"{p}_pct_resistant"].between(0, 100).all())
    check(f"{p}: every reported value has >= {CFG['min_isolates']} isolates tested",
          (rep[f"{p}_n_tested"] >= CFG["min_isolates"]).all())
    inside = ((rep[f"{p}_ci_lower"] <= rep[f"{p}_pct_resistant"] + 0.05) &
              (rep[f"{p}_pct_resistant"] <= rep[f"{p}_ci_upper"] + 0.05)).all()
    check(f"{p}: CDC confidence interval contains the percent", inside)
    ins = atlas[atlas[f"{p}_status"] == "insufficient_data"]
    check(f"{p}: insufficient-data cells carry no percent (never shown as 0%)",
          ins[f"{p}_pct_resistant"].isna().all(), f"{len(ins)} cells insufficient of {len(atlas)}")

# Our mid-P interval (used only for the derived pooled VRE value) must reproduce CDC's own.
random.seed(4)
samp = long[(long.status == "reported") & (long.event_type == "ALL")].sample(300, random_state=4)
gaps = []
for _, x in samp.iterrows():
    lo, hi = build.midp_ci(int(x.n_resistant), int(x.n_tested))
    gaps.append(max(abs(lo - x.ci_lower), abs(hi - x.ci_upper)))
gaps = pd.Series(gaps)
check("mid-P method reproduces CDC's 95% CI on 300 random cells (within 0.1 point)",
      (gaps <= 0.11).mean() >= 0.98, f"{(gaps <= 0.11).mean():.1%} within 0.1; max gap {gaps.max():.2f}")
pool = atlas[atlas.vre_pooled_status == "derived"]
check("pooled VRE counts = E. faecalis + E. faecium counts",
      ((pool.vre_pooled_n_tested == pool.vre_faecalis_n_tested + pool.vre_faecium_n_tested) &
       (pool.vre_pooled_n_resistant == pool.vre_faecalis_n_resistant + pool.vre_faecium_n_resistant)).all())

# State sums vs CDC's national facility-type table (national also includes territories
# and events with no state, so states should be a little under, never over).
nat_all = nat.groupby(["phenotype_key", "year"])[["n_resistant", "n_tested"]].sum()
key = {"mrsa": "MRSA", "cre": "CRE", "vre_faecalis": "VRE_faecalis", "vre_faecium": "VRE_faecium"}
for p in PH:
    s = atlas.groupby("year")[f"{p}_n_tested"].sum()
    n = nat_all.loc[key[p], "n_tested"]
    ratio = (s / n).round(3)
    check(f"{p}: sum of published state counts <= national total every year",
          (ratio <= 1.0).all(), f"state share of national isolates {ratio.min():.0%}-{ratio.max():.0%}")
note()

note("== 3. Hospital counts ==")
hc = atlas
check("short-term + critical access = total", (hc.hosp_short_term_acute + hc.hosp_critical_access == hc.hosp_total).all())
check("rural + urban + unknown = total", (hc.hosp_rural + hc.hosp_urban + hc.hosp_rural_unknown == hc.hosp_total).all())
bands = [c for c in hc.columns if c.startswith("hosp_beds_")]
check("bed-size bands add up to total", (hc[bands].sum(axis=1) == hc.hosp_total).all())
check("small-and-rural <= small and <= rural", ((hc.hosp_small_rural <= hc.hosp_small) & (hc.hosp_small_rural <= hc.hosp_rural)).all())
check("every state has at least one counted hospital every year", (hc.hosp_total > 0).all())
check("small-and-rural <= small-rural-or-critical-access <= total",
      ((hc.hosp_small_rural <= hc.hosp_small_rural_or_cah) & (hc.hosp_small_rural_or_cah <= hc.hosp_total)).all())
check("critical access hospitals flagged urban <= critical access", (hc.hosp_critical_access_cms_urban <= hc.hosp_critical_access).all())
_cah = hosp_list[(hosp_list.year == str(LATEST)) & (hosp_list.subtype == "11")]
note(f"  Critical access hospitals {LATEST}: {len(_cah)}; CMS urban flag {int((_cah.urban_rural_code == 'U').sum())}; "
     f"more than 25 certified beds {int((_cah.certified_beds.astype(int) > 25).sum())} (max {_cah.certified_beds.astype(int).max()})")
for y in [CFG["first_year"], 2019, 2020, 2022, 2023, LATEST]:
    t = hc[hc.year == y]
    note(f"  {y}: {t.hosp_total.sum()} hospitals ({t.hosp_short_term_acute.sum()} short-term, "
         f"{t.hosp_critical_access.sum()} critical access); {t.hosp_small.sum()} small; {t.hosp_rural.sum()} rural")
excl = hosp_list[hosp_list.excluded_reason.notna()]
note(f"Excluded tiny short-term hospitals by year: {excl.groupby('year').size().to_dict()}")
# Year-over-year swings in hospital counts (flag, not fail)
h = hc.sort_values(["usps", "year"]).copy()
h["chg"] = h.groupby("usps").hosp_total.pct_change()
big = h[h.chg.abs() > 0.10]
note(f"State-years with >10% change in hospital count from prior year (review): "
     + (", ".join(f"{a} {b} ({c:+.0%})" for a, b, c in zip(big.usps, big.year, big.chg)) or "none"))
note()

note("== 4. Named spot checks (verify by hand; see docs/VERIFY_CHECKLIST.md) ==")
def cell(u, y, col):
    return atlas.loc[(atlas.usps == u) & (atlas.year == y), col].iloc[0]
spots = [
    ("TX", LATEST, "mrsa"), ("AL", LATEST, "mrsa"), ("MS", LATEST, "mrsa"),
    ("NY", LATEST, "cre"), ("AK", LATEST, "mrsa"), ("VT", 2011, "mrsa"), ("CA", 2015, "vre_faecium"),
]
for u, y, p in spots:
    st = cell(u, y, f"{p}_status")
    val = (f"{cell(u, y, f'{p}_pct_resistant')}% ({int(cell(u, y, f'{p}_n_resistant'))}/{int(cell(u, y, f'{p}_n_tested'))})"
           if st == "reported" else "insufficient data")
    note(f"  {u} {y} {p}: {val}")
for u in ["TX", "IA", "WY", "NJ"]:
    note(f"  {u} {LATEST}: hospitals {cell(u, LATEST, 'hosp_total')}, critical access {cell(u, LATEST, 'hosp_critical_access')}, "
         f"small (<{CFG['small_hospital_max_beds'] + 1} beds) {cell(u, LATEST, 'hosp_small')}, rural {cell(u, LATEST, 'hosp_rural')}")
note()

# ------------------------------------------------------------ stats file
L = atlas[atlas.year == LATEST]
def top(df, col, n=5, asc=False):
    d = df.dropna(subset=[col]).sort_values(col, ascending=asc).head(n)
    return [{"usps": a, "state": b, "value": float(c)} for a, b, c in zip(d.usps, d.state_name, d[col])]
# States in the top third for BOTH small-and-rural share and resistance (descriptive only).
quad = {}
for p in ["mrsa", "cre", "vre_faecium"]:
    d = L[L[f"{p}_status"] == "reported"]
    hi_r = d[f"{p}_pct_resistant"] >= d[f"{p}_pct_resistant"].quantile(2 / 3)
    hi_s = d.pct_hosp_small_rural >= L.pct_hosp_small_rural.quantile(2 / 3)
    quad[p] = sorted(d[hi_r & hi_s].usps.tolist())
first = atlas[atlas.year == CFG["first_year"]]
stats = {
    "latest_year": LATEST, "first_year": CFG["first_year"], "n_places": int(atlas.usps.nunique()),
    "n_rows": int(len(atlas)), "n_columns": int(atlas.shape[1]),
    "hospitals_latest": int(L.hosp_total.sum()),
    "short_term_latest": int(L.hosp_short_term_acute.sum()),
    "critical_access_latest": int(L.hosp_critical_access.sum()),
    "small_latest": int(L.hosp_small.sum()),
    "pct_small_latest": round(100 * L.hosp_small.sum() / L.hosp_total.sum(), 1),
    "rural_latest": int(L.hosp_rural.sum()),
    "pct_rural_latest": round(100 * L.hosp_rural.sum() / L.hosp_total.sum(), 1),
    "small_rural_latest": int(L.hosp_small_rural.sum()),
    "pct_small_rural_latest": round(100 * L.hosp_small_rural.sum() / L.hosp_total.sum(), 1),
    "cah_cms_urban_latest": int(L.hosp_critical_access_cms_urban.sum()),
    "pct_cah_cms_urban_latest": round(100 * L.hosp_critical_access_cms_urban.sum() / L.hosp_critical_access.sum(), 1),
    "cah_over_25_beds_latest": int((hosp_list[(hosp_list.year == str(LATEST)) & (hosp_list.subtype == "11")].certified_beds.astype(int) > 25).sum()),
    "small_rural_or_cah_latest": int(L.hosp_small_rural_or_cah.sum()),
    "pct_small_rural_or_cah_latest": round(100 * L.hosp_small_rural_or_cah.sum() / L.hosp_total.sum(), 1),
    "pct_beds_in_small_latest": round(100 * L.beds_in_small.sum() / L.beds_total.sum(), 1),
    "hospitals_first": int(first.hosp_total.sum()),
    "states_majority_small_latest": int((L.pct_hosp_small >= 50).sum()),
    "reported_cells_latest": {p: int((L[f"{p}_status"] == "reported").sum()) for p in PH},
    "insufficient_cells_all_years": {p: int((atlas[f"{p}_status"] == "insufficient_data").sum()) for p in PH},
    "excluded_tiny_by_year": {str(k): int(v) for k, v in excl.groupby("year").size().items()},
    "top_mrsa_latest": top(L, "mrsa_pct_resistant"),
    "top_vre_faecium_latest": top(L, "vre_faecium_pct_resistant"),
    "top_cre_latest": top(L, "cre_pct_resistant"),
    "top_small_rural_share_latest": top(L, "pct_hosp_small_rural"),
    "high_resistance_and_high_small_rural_latest": quad,
    "qa_failures": len(fails),
}
json.dump(stats, open(os.path.join(P, "stats.json"), "w"), indent=2)
note("== 5. Summary ==")
note(f"Checks failed: {len(fails)}" + (f" ({'; '.join(fails)})" if fails else ""))
open(os.path.join(P, "qa_report.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if fails else 0)
