#!/usr/bin/env python3
"""
02_build.py - Clean both sources and join them into the state-by-year atlas table.

Plain-language summary: this script takes the raw CDC resistance tables and the
raw CMS hospital lists, applies the rules written in docs/CODEBOOK.md, and
writes the finished tables to data/processed/. The main output is
atlas_state_year.csv: one row per state per year (52 places x 14 years),
with resistance for each organism next to hospital counts by size and rural
location. You do not need to open this file; the rules it applies are listed
in the CODEBOOK and the decisions you approve are in config.json.
"""
import json, math, os
import pandas as pd
from scipy import optimize, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
CFG = json.load(open(os.path.join(ROOT, "config.json")))
YEARS = list(range(CFG["first_year"], CFG["last_year"] + 1))

# 50 states + DC + Puerto Rico: the places CDC reports at state level.
STATES = {
 "Alabama":("AL","01"),"Alaska":("AK","02"),"Arizona":("AZ","04"),"Arkansas":("AR","05"),
 "California":("CA","06"),"Colorado":("CO","08"),"Connecticut":("CT","09"),"Delaware":("DE","10"),
 "District of Columbia":("DC","11"),"Florida":("FL","12"),"Georgia":("GA","13"),"Hawaii":("HI","15"),
 "Idaho":("ID","16"),"Illinois":("IL","17"),"Indiana":("IN","18"),"Iowa":("IA","19"),
 "Kansas":("KS","20"),"Kentucky":("KY","21"),"Louisiana":("LA","22"),"Maine":("ME","23"),
 "Maryland":("MD","24"),"Massachusetts":("MA","25"),"Michigan":("MI","26"),"Minnesota":("MN","27"),
 "Mississippi":("MS","28"),"Missouri":("MO","29"),"Montana":("MT","30"),"Nebraska":("NE","31"),
 "Nevada":("NV","32"),"New Hampshire":("NH","33"),"New Jersey":("NJ","34"),"New Mexico":("NM","35"),
 "New York":("NY","36"),"North Carolina":("NC","37"),"North Dakota":("ND","38"),"Ohio":("OH","39"),
 "Oklahoma":("OK","40"),"Oregon":("OR","41"),"Pennsylvania":("PA","42"),"Rhode Island":("RI","44"),
 "South Carolina":("SC","45"),"South Dakota":("SD","46"),"Tennessee":("TN","47"),"Texas":("TX","48"),
 "Utah":("UT","49"),"Vermont":("VT","50"),"Virginia":("VA","51"),"Washington":("WA","53"),
 "West Virginia":("WV","54"),"Wisconsin":("WI","55"),"Wyoming":("WY","56"),"Puerto Rico":("PR","72"),
}
USPS = {v[0]: (k, v[1]) for k, v in STATES.items()}
EVENT_NORMAL = {
    "All Infectious Event Type Data": "ALL",
    "CAUTI": "CAUTI", "Catheter-Associated Urinary Tract Infections": "CAUTI",
    "CLABSI": "CLABSI", "Central Line-Associated Bloodstream Infections": "CLABSI",
    "SSI": "SSI", "Surgical Site Infections": "SSI",
}
PHENO_SHORT = {"MRSA": "mrsa", "CRE": "cre", "VRE_faecalis": "vre_faecalis",
               "VRE_faecium": "vre_faecium"}


def midp_ci(x, n, alpha=0.05):
    """Two-sided mid-P exact 95% CI for a binomial proportion, in percent (CDC's method)."""
    if n <= 0:
        return (math.nan, math.nan)
    def lower_eq(p):  # P(X > x) + 0.5 P(X = x) = alpha/2
        return stats.binom.sf(x, n, p) + 0.5 * stats.binom.pmf(x, n, p) - alpha / 2
    def upper_eq(p):  # P(X < x) + 0.5 P(X = x) = alpha/2
        return stats.binom.cdf(x - 1, n, p) + 0.5 * stats.binom.pmf(x, n, p) - alpha / 2
    lo = 0.0 if x == 0 else optimize.brentq(lower_eq, 1e-12, 1 - 1e-12)
    hi = 1.0 if x == n else optimize.brentq(upper_eq, 1e-12, 1 - 1e-12)
    return (round(100 * lo, 1), round(100 * hi, 1))


# ---------------------------------------------------------------- resistance
def build_resistance():
    r = pd.read_csv(os.path.join(RAW, "arpsp", "arpsp_state_year.csv"))
    n_in = len(r)
    dropped = r[~r.state.isin(STATES)]
    r = r[r.state.isin(STATES)].copy()
    r["event_type"] = r.eventType.map(EVENT_NORMAL)
    assert r.event_type.notna().all(), "unknown event type label in CDC data"
    r["usps"] = r.state.map(lambda s: STATES[s][0])
    r["state_fips"] = r.state.map(lambda s: STATES[s][1])
    # CDC shows no percent when fewer than 20 isolates were tested. In 2011-2022
    # the portal stores those cells as 0 resistant / 0 tested / 0%; in 2023-2024
    # as blanks. Both mean "insufficient data", never "0% resistant".
    tested = r.isolatesTestedCount
    insufficient = tested.isna() | (tested < CFG["min_isolates"]) | r.percentResistant.isna()
    r["status"] = "reported"
    r.loc[insufficient, "status"] = "insufficient_data"
    for c in ["percentResistant", "resistantCount", "isolatesTestedCount", "lowerCi", "upperCi"]:
        r.loc[insufficient, c] = pd.NA
    long = r.rename(columns={"state": "state_name", "percentResistant": "pct_resistant",
                             "resistantCount": "n_resistant", "isolatesTestedCount": "n_tested",
                             "lowerCi": "ci_lower", "upperCi": "ci_upper"})
    long = long[["state_name", "usps", "state_fips", "year", "phenotype_key", "phenotype",
                 "event_type", "pct_resistant", "n_resistant", "n_tested", "ci_lower",
                 "ci_upper", "status"]].sort_values(["phenotype_key", "event_type", "usps", "year"])
    for c in ["n_resistant", "n_tested"]:
        long[c] = long[c].astype("Int64")
    for c in ["pct_resistant", "ci_lower", "ci_upper"]:  # CDC stores some unrounded floats
        long[c] = long[c].astype(float).round(1)
    log = {"cdc_rows_in": n_in, "cdc_rows_dropped_non_state": len(dropped),
           "cdc_dropped_labels": sorted(dropped.state.unique().tolist()),
           "cdc_rows_kept": len(long)}
    return long, log


# ---------------------------------------------------------------- hospitals
def band(beds):
    for lo, hi, label in CFG["bed_bands"]:
        if lo <= beds <= hi:
            return label
    return "unknown"


def build_hospitals():
    rows, log = [], {}
    for y in YEARS:
        d = pd.read_csv(os.path.join(RAW, "pos", f"pos_hospitals_dec{y}.csv"), dtype=str)
        d = d.apply(lambda s: s.str.strip())
        n_all = len(d)
        d["subtype"] = d.PRVDR_CTGRY_SBTYP_CD.str.zfill(2)
        d = d[d.subtype.isin(CFG["hospital_subtypes"].keys())]
        n_type = len(d)
        d = d[d.PGM_TRMNTN_CD == "00"]  # 00 = active provider
        n_active = len(d)
        d = d[d.STATE_CD.isin(USPS)]
        n_state = len(d)
        d["beds"] = pd.to_numeric(d.CRTFD_BED_CNT, errors="coerce")
        excl = (d.subtype == "01") & (d.beds <= CFG["exclude_short_term_max_beds"])
        d["excluded_reason"] = ""
        d.loc[excl, "excluded_reason"] = (f"short-term hospital with <= "
                                          f"{CFG['exclude_short_term_max_beds']} certified beds")
        d["year"] = y
        rows.append(d)
        log[y] = {"pos_hospital_rows": n_all, "target_subtypes": n_type, "active": n_active,
                  "in_52_states": n_state, "excluded_tiny": int(excl.sum()),
                  "counted": int(n_state - excl.sum())}
    h = pd.concat(rows)
    h["hospital_type"] = h.subtype.map(CFG["hospital_subtypes"])
    h["rural"] = h.CBSA_URBN_RRL_IND.map({"R": True, "U": False})
    h["bed_band"] = h.beds.map(band)
    h["small"] = h.beds < CFG["small_hospital_max_beds"] + 1
    h["lt200"] = h.beds < 200
    facility = h.rename(columns={"PRVDR_NUM": "ccn", "FAC_NAME": "facility_name",
                                 "CITY_NAME": "city", "STATE_CD": "usps", "beds": "certified_beds",
                                 "CBSA_URBN_RRL_IND": "urban_rural_code"})
    facility = facility[["year", "ccn", "facility_name", "city", "usps", "subtype", "hospital_type",
                         "certified_beds", "bed_band", "urban_rural_code", "excluded_reason"]]
    facility = facility.sort_values(["year", "usps", "ccn"])

    c = h[h.excluded_reason == ""].copy()
    c["usps"] = c.STATE_CD
    g = c.groupby(["usps", "year"])
    agg = pd.DataFrame({
        "hosp_total": g.size(),
        "hosp_short_term_acute": g.apply(lambda x: (x.subtype == "01").sum()),
        "hosp_critical_access": g.apply(lambda x: (x.subtype == "11").sum()),
        "hosp_rural": g.rural.apply(lambda s: (s == True).sum()),
        "hosp_urban": g.rural.apply(lambda s: (s == False).sum()),
        "hosp_rural_unknown": g.rural.apply(lambda s: s.isna().sum()),
        "hosp_small": g.small.sum(),
        "hosp_small_rural": g.apply(lambda x: (x.small & (x.rural == True)).sum()),
        # Critical access hospitals the CMS flag marks urban (about 1 in 5 nationally).
        "hosp_critical_access_cms_urban": g.apply(lambda x: ((x.subtype == "11") & (x.rural == False)).sum()),
        # Alternative definition: small-and-rural, plus every critical access hospital
        # whatever its CMS flag or bed count.
        "hosp_small_rural_or_cah": g.apply(lambda x: ((x.small & (x.rural == True)) | (x.subtype == "11")).sum()),
        "hosp_lt200_beds": g.lt200.sum(),
        "beds_total": g.beds.sum(),
        "beds_in_small": g.apply(lambda x: x.loc[x.small, "beds"].sum()),
        "beds_in_rural": g.apply(lambda x: x.loc[x.rural == True, "beds"].sum()),
    })
    for lo, hi, label in CFG["bed_bands"]:
        agg[f"hosp_beds_{label}"] = g.bed_band.apply(lambda s, l=label: (s == l).sum())
    agg = agg.reset_index()
    # States with no hospitals of a kind still need a row: fill the full grid.
    grid = pd.MultiIndex.from_product([sorted(USPS), YEARS], names=["usps", "year"]).to_frame(index=False)
    agg = grid.merge(agg, on=["usps", "year"], how="left").fillna(0)
    for col in agg.columns:
        if col not in ("usps",):
            agg[col] = agg[col].astype(int)
    agg["pct_hosp_small"] = (100 * agg.hosp_small / agg.hosp_total).round(1)
    agg["pct_hosp_rural"] = (100 * agg.hosp_rural / agg.hosp_total).round(1)
    agg["pct_hosp_small_rural"] = (100 * agg.hosp_small_rural / agg.hosp_total).round(1)
    agg["pct_hosp_small_rural_or_cah"] = (100 * agg.hosp_small_rural_or_cah / agg.hosp_total).round(1)
    agg["pct_hosp_critical_access"] = (100 * agg.hosp_critical_access / agg.hosp_total).round(1)
    agg["pct_beds_in_small"] = (100 * agg.beds_in_small / agg.beds_total).round(1)
    agg["pct_beds_in_rural"] = (100 * agg.beds_in_rural / agg.beds_total).round(1)
    return agg, facility, log


# ---------------------------------------------------------------- join
def build_atlas(long, hosp):
    a = long[long.event_type == "ALL"]
    wide = None
    for key, short in PHENO_SHORT.items():
        p = a[a.phenotype_key == key][["usps", "year", "pct_resistant", "n_resistant", "n_tested",
                                        "ci_lower", "ci_upper", "status"]]
        for c in ["n_resistant", "n_tested"]:
            p[c] = p[c].astype("Int64")
        p = p.rename(columns={c: f"{short}_{c}" for c in p.columns if c not in ("usps", "year")})
        wide = p if wide is None else wide.merge(p, on=["usps", "year"], how="outer")
    # Pooled vancomycin-resistant Enterococcus (E. faecalis + E. faecium), derived here.
    # Only computed when both species have published counts; CDC's hidden counts
    # (< 20 isolates) cannot be recovered, so pooling across them is not possible.
    both = wide.vre_faecalis_n_tested.notna() & wide.vre_faecium_n_tested.notna()
    r = wide.vre_faecalis_n_resistant + wide.vre_faecium_n_resistant
    n = wide.vre_faecalis_n_tested + wide.vre_faecium_n_tested
    wide["vre_pooled_n_resistant"] = r.where(both).astype("Int64")
    wide["vre_pooled_n_tested"] = n.where(both).astype("Int64")
    wide["vre_pooled_pct_resistant"] = (100 * r / n).where(both).astype(float).round(1)
    cis = [midp_ci(int(x), int(m)) if ok else (math.nan, math.nan)
           for x, m, ok in zip(r.fillna(0), n.fillna(0), both)]
    wide["vre_pooled_ci_lower"] = [c[0] for c in cis]
    wide["vre_pooled_ci_upper"] = [c[1] for c in cis]
    wide["vre_pooled_status"] = ["derived" if ok else "not_computable" for ok in both]

    atlas = hosp.merge(wide, on=["usps", "year"], how="outer", indicator=True)
    match = atlas._merge.value_counts().to_dict()
    atlas = atlas.drop(columns="_merge")
    atlas.insert(1, "state_name", atlas.usps.map(lambda u: USPS[u][0]))
    atlas.insert(2, "state_fips", atlas.usps.map(lambda u: USPS[u][1]))
    atlas = atlas.sort_values(["usps", "year"]).reset_index(drop=True)
    return atlas, {str(k): int(v) for k, v in match.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    long, rlog = build_resistance()
    hosp, facility, hlog = build_hospitals()
    atlas, match = build_atlas(long, hosp)
    nat = pd.read_csv(os.path.join(RAW, "arpsp", "arpsp_national_facility_type.csv"))
    nat = nat.rename(columns={"percentResistant": "pct_resistant", "resistantCount": "n_resistant",
                              "isolatesTestedCount": "n_tested", "lowerCi": "ci_lower",
                              "upperCi": "ci_upper", "facility": "facility_code"})
    long.to_csv(os.path.join(OUT, "resistance_state_year_long.csv"), index=False)
    hosp.to_csv(os.path.join(OUT, "hospitals_state_year.csv"), index=False)
    facility.to_csv(os.path.join(OUT, "hospital_list_by_year.csv"), index=False)
    atlas.to_csv(os.path.join(OUT, "atlas_state_year.csv"), index=False)
    nat.to_csv(os.path.join(OUT, "resistance_national_by_facility_type.csv"), index=False)
    json.dump({"resistance": rlog, "hospitals_by_year": hlog, "join": match},
              open(os.path.join(OUT, "build_log.json"), "w"), indent=2)
    print(f"atlas_state_year.csv: {len(atlas)} rows x {atlas.shape[1]} columns; join {match}")


if __name__ == "__main__":
    main()
