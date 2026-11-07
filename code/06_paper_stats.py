#!/usr/bin/env python3
"""
06_paper_stats.py - Every number quoted in the preprint, computed from the atlas.

Plain-language summary: this script reads the finished atlas tables and writes
paper/paper_stats.json and a few tables in paper/tables/. The preprint quotes
numbers only from these files, so the paper cannot disagree with the data.
All analyses are descriptive. Correlations are across states within one year
(Spearman), reported with exact counts and no claim of causation or trend.
"""
import json, os
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "paper")
os.makedirs(os.path.join(OUT, "tables"), exist_ok=True)
a = pd.read_csv(os.path.join(P, "atlas_state_year.csv"), dtype={"state_fips": str})
h = pd.read_csv(os.path.join(P, "hospital_list_by_year.csv"), dtype={"ccn": str, "subtype": str})
nat = pd.read_csv(os.path.join(P, "resistance_national_by_facility_type.csv"))
base = json.load(open(os.path.join(P, "stats.json")))
cfg = json.load(open(os.path.join(ROOT, "config.json")))
Y0, Y1 = cfg["first_year"], cfg["last_year"]
ORG = ["mrsa", "cre", "vre_faecalis", "vre_faecium"]
S = {"first_year": Y0, "last_year": Y1, "n_places": 52, "n_rows": len(a)}
r1 = lambda x: None if pd.isna(x) else round(float(x), 1)
r2 = lambda x: None if pd.isna(x) else round(float(x), 2)
r3 = lambda x: None if pd.isna(x) else round(float(x), 3)

# ---------------------------------------------------------------- hospitals
L = a[a.year == Y1]
F = a[a.year == Y0]
S["hosp"] = {
    "total_last": int(L.hosp_total.sum()), "total_first": int(F.hosp_total.sum()),
    "short_last": int(L.hosp_short_term_acute.sum()), "short_first": int(F.hosp_short_term_acute.sum()),
    "cah_last": int(L.hosp_critical_access.sum()), "cah_first": int(F.hosp_critical_access.sum()),
    "small_last": int(L.hosp_small.sum()), "pct_small_last": r1(100 * L.hosp_small.sum() / L.hosp_total.sum()),
    "rural_last": int(L.hosp_rural.sum()), "pct_rural_last": r1(100 * L.hosp_rural.sum() / L.hosp_total.sum()),
    "small_rural_last": int(L.hosp_small_rural.sum()),
    "pct_small_rural_last": r1(100 * L.hosp_small_rural.sum() / L.hosp_total.sum()),
    "small_rural_or_cah_last": int(L.hosp_small_rural_or_cah.sum()),
    "pct_small_rural_or_cah_last": r1(100 * L.hosp_small_rural_or_cah.sum() / L.hosp_total.sum()),
    "beds_last": int(L.beds_total.sum()),
    "pct_beds_small_last": r1(100 * L.beds_in_small.sum() / L.beds_total.sum()),
    "pct_beds_rural_last": r1(100 * L.beds_in_rural.sum() / L.beds_total.sum()),
    "lt200_last": int(L.hosp_lt200_beds.sum()), "pct_lt200_last": r1(100 * L.hosp_lt200_beds.sum() / L.hosp_total.sum()),
    "states_majority_small": int((L.pct_hosp_small >= 50).sum()),
    "states_majority_small_rural": int((L.pct_hosp_small_rural >= 50).sum()),
    "median_state_pct_small": r1(L.pct_hosp_small.median()),
    "median_state_pct_small_rural": r1(L.pct_hosp_small_rural.median()),
    "iqr_state_pct_small_rural": [r1(L.pct_hosp_small_rural.quantile(.25)), r1(L.pct_hosp_small_rural.quantile(.75))],
    "min_state_small_rural": {"usps": L.loc[L.pct_hosp_small_rural.idxmin(), "usps"], "value": r1(L.pct_hosp_small_rural.min())},
    "states_zero_small_rural": sorted(L[L.hosp_small_rural == 0].usps.tolist()),
    "max_state_small_rural": {"usps": L.loc[L.pct_hosp_small_rural.idxmax(), "usps"], "value": r1(L.pct_hosp_small_rural.max())},
    "cah_cms_urban_last": int(L.hosp_critical_access_cms_urban.sum()),
    "pct_cah_cms_urban_last": r1(100 * L.hosp_critical_access_cms_urban.sum() / L.hosp_critical_access.sum()),
}
cah = h[(h.year == Y1) & (h.subtype == "11")]
S["hosp"]["cah_over_25_last"] = int((cah.certified_beds > 25).sum())
S["hosp"]["cah_max_beds_last"] = int(cah.certified_beds.max())
S["hosp"]["cah_median_beds_last"] = r1(cah.certified_beds.median())
# Bed-band distribution, last year: share of hospitals vs share of beds
cnt = h[(h.year == Y1) & h.excluded_reason.isna()]
bands = [b[2] for b in cfg["bed_bands"]]
bd = cnt.groupby("bed_band").agg(hospitals=("ccn", "size"), beds=("certified_beds", "sum")).reindex(bands)
bd["pct_hospitals"] = (100 * bd.hospitals / bd.hospitals.sum()).round(1)
bd["pct_beds"] = (100 * bd.beds / bd.beds.sum()).round(1)
bd.to_csv(os.path.join(OUT, "tables", "table_bed_bands_last_year.csv"))
S["bed_bands_last"] = {k: {c: (int(v) if c in ("hospitals", "beds") else float(v)) for c, v in row.items()} for k, row in bd.iterrows()}
# Annual national series
ann = a.groupby("year").agg(total=("hosp_total", "sum"), short=("hosp_short_term_acute", "sum"),
                            cah=("hosp_critical_access", "sum"), small=("hosp_small", "sum"),
                            rural=("hosp_rural", "sum"), small_rural=("hosp_small_rural", "sum"))
ex = h[h.excluded_reason.notna()].groupby("year").size().reindex(ann.index, fill_value=0)
ann["excluded_tiny"] = ex
ann.to_csv(os.path.join(OUT, "tables", "table_national_hospitals_by_year.csv"))
S["excluded_tiny"] = {str(k): int(v) for k, v in ex.items()}
S["excluded_tiny_2020_2022_total"] = int(ex.loc[2020:2022].sum())
tx = h[(h.excluded_reason.notna()) & (h.usps == "TX")].groupby("year").size()
S["excluded_tiny_tx_max"] = {"year": int(tx.idxmax()), "n": int(tx.max())}
S["change_total_pct"] = r1(100 * (S["hosp"]["total_last"] - S["hosp"]["total_first"]) / S["hosp"]["total_first"])
S["change_short_pct"] = r1(100 * (S["hosp"]["short_last"] - S["hosp"]["short_first"]) / S["hosp"]["short_first"])

# ---------------------------------------------------------------- resistance
res = {}
for p in ORG:
    rep = L[L[f"{p}_status"] == "reported"]
    allrep = a[a[f"{p}_status"] == "reported"]
    nr, nt = rep[f"{p}_n_resistant"].sum(), rep[f"{p}_n_tested"].sum()
    hi = rep.loc[rep[f"{p}_pct_resistant"].idxmax()]; lo = rep.loc[rep[f"{p}_pct_resistant"].idxmin()]
    res[p] = {
        "reported_last": int(len(rep)), "insufficient_last": int(52 - len(rep)),
        "insufficient_last_states": sorted(L[L[f"{p}_status"] != "reported"].usps.tolist()),
        "insufficient_all": int((a[f"{p}_status"] == "insufficient_data").sum()),
        "pooled_states_last": r1(100 * nr / nt), "n_tested_last": int(nt), "n_resistant_last": int(nr),
        "median_last": r1(rep[f"{p}_pct_resistant"].median()),
        "iqr_last": [r1(rep[f"{p}_pct_resistant"].quantile(.25)), r1(rep[f"{p}_pct_resistant"].quantile(.75))],
        "max_last": {"usps": hi.usps, "state": hi.state_name, "value": r1(hi[f"{p}_pct_resistant"]),
                     "r": int(hi[f"{p}_n_resistant"]), "n": int(hi[f"{p}_n_tested"])},
        "min_last": {"usps": lo.usps, "state": lo.state_name, "value": r1(lo[f"{p}_pct_resistant"]),
                     "r": int(lo[f"{p}_n_resistant"]), "n": int(lo[f"{p}_n_tested"])},
        "median_n_tested_last": r1(rep[f"{p}_n_tested"].median()),
        "n_tested_all_years": int(allrep[f"{p}_n_tested"].sum()),
        "zero_resistant_reported_all": int((allrep[f"{p}_n_resistant"] == 0).sum()),
    }
    # national series from sum of reported states
    g = a.groupby("year")[[f"{p}_n_resistant", f"{p}_n_tested"]].sum()
    res[p]["series_pooled"] = {str(y): r1(100 * r / n) for y, (r, n) in g.iterrows()}
S["res"] = res
vp = L[L.vre_pooled_status == "derived"]
S["vre_pooled_last"] = {"computable": int(len(vp)),
                        "pooled": r1(100 * vp.vre_pooled_n_resistant.sum() / vp.vre_pooled_n_tested.sum()),
                        "median": r1(vp.vre_pooled_pct_resistant.median())}
# National facility type, last year
nat_last = nat[nat.year == Y1].pivot(index="phenotype_key", columns="facility_label", values="pct_resistant")
nat_n = nat[nat.year == Y1].pivot(index="phenotype_key", columns="facility_label", values="n_tested")
S["national_by_facility_last"] = {k: {c: r1(v) for c, v in row.items()} for k, row in nat_last.iterrows()}
S["national_by_facility_n_last"] = {k: {c: (None if pd.isna(v) else int(v)) for c, v in row.items()} for k, row in nat_n.iterrows()}
keymap = {"mrsa": "MRSA", "cre": "CRE", "vre_faecalis": "VRE_faecalis", "vre_faecium": "VRE_faecium"}
# states' share of national tested isolates (all years)
for p in ORG:
    st = a[f"{p}_n_tested"].sum(); nn = nat[nat.phenotype_key == keymap[p]].n_tested.sum()
    S["res"][p]["state_share_of_national_isolates"] = r1(100 * st / nn)

# ---------------------------------------------------------------- suppression vs rurality
L3 = L.copy()
L3["tertile"] = pd.qcut(L3.pct_hosp_small_rural.rank(method="first"), 3, labels=["low", "middle", "high"])
supp = {}
for p in ORG:
    t = L3.groupby("tertile", observed=True)[f"{p}_status"].apply(lambda s: int((s != "reported").sum()))
    supp[p] = {str(k): int(v) for k, v in t.items()}
S["suppression_by_small_rural_tertile_last"] = supp
S["tertile_sizes"] = {str(k): int(v) for k, v in L3.tertile.value_counts().sort_index().items()}
S["tertile_cutpoints_last"] = [r1(L3.groupby("tertile", observed=True).pct_hosp_small_rural.max().iloc[i]) for i in range(2)]
# all years: suppression by tertile (within each year)
def tert_supp(df):
    d = df.copy()
    d["tertile"] = pd.qcut(d.pct_hosp_small_rural.rank(method="first"), 3, labels=["low", "middle", "high"])
    return d
all_t = a.groupby("year", group_keys=False).apply(tert_supp)
S["suppression_by_tertile_all_years"] = {
    p: {str(k): int(v) for k, v in all_t.groupby("tertile", observed=True)[f"{p}_status"].apply(lambda s: int((s != "reported").sum())).items()}
    for p in ORG}
# total suppressed cells (any organism) by tertile, all years
S["suppression_all_org_all_years_by_tertile"] = {
    k: int(sum(S["suppression_by_tertile_all_years"][p][k] for p in ORG)) for k in ["low", "middle", "high"]}

# ---------------------------------------------------------------- association across states
def spear(x, y):
    m = x.notna() & y.notna()
    rho, pv = stats.spearmanr(x[m], y[m])
    return {"rho": r2(rho), "p": r3(pv), "n": int(m.sum())}
assoc = {}
for p in ORG:
    rep = L[L[f"{p}_status"] == "reported"]
    assoc[p] = {
        "small_rural": spear(rep.pct_hosp_small_rural, rep[f"{p}_pct_resistant"]),
        "small_rural_or_cah": spear(rep.pct_hosp_small_rural_or_cah, rep[f"{p}_pct_resistant"]),
        "small": spear(rep.pct_hosp_small, rep[f"{p}_pct_resistant"]),
        "beds_in_small": spear(rep.pct_beds_in_small, rep[f"{p}_pct_resistant"]),
    }
    series = {}
    for y, g in a.groupby("year"):
        rp = g[g[f"{p}_status"] == "reported"]
        series[str(y)] = spear(rp.pct_hosp_small_rural, rp[f"{p}_pct_resistant"])
    assoc[p]["by_year_small_rural"] = series
    rhos = [v["rho"] for v in series.values()]
    assoc[p]["by_year_range"] = [min(rhos), max(rhos)]
    assoc[p]["by_year_n_p_lt_05"] = int(sum(v["p"] < 0.05 for v in series.values()))
    assoc[p]["by_year_n_negative"] = int(sum(v["rho"] < 0 for v in series.values()))
S["assoc_last"] = assoc
# Excluding Puerto Rico for CRE (an extreme single value)
rep = L[(L.cre_status == "reported") & (L.usps != "PR")]
S["assoc_last_cre_no_pr"] = spear(rep.pct_hosp_small_rural, rep.cre_pct_resistant)

# ---------------------------------------------------------------- overlap states (top third on both)
over = {}
for p in ORG:
    rep = L[L[f"{p}_status"] == "reported"]
    tr = rep[f"{p}_pct_resistant"].quantile(2 / 3); ts = L.pct_hosp_small_rural.quantile(2 / 3)
    sel = rep[(rep[f"{p}_pct_resistant"] >= tr) & (rep.pct_hosp_small_rural >= ts)]
    over[p] = {"threshold_resistance": r1(tr), "threshold_small_rural": r1(ts),
               "states": [{"usps": u, "state": n, "res": r1(x), "small_rural": r1(s), "hosp": int(t),
                           "small_rural_n": int(sr), "cah": int(c)}
                          for u, n, x, s, t, sr, c in zip(sel.usps, sel.state_name, sel[f"{p}_pct_resistant"],
                                                          sel.pct_hosp_small_rural, sel.hosp_total,
                                                          sel.hosp_small_rural, sel.hosp_critical_access)]}
    over[p]["n_small_rural_hospitals_in_overlap"] = int(sel.hosp_small_rural.sum())
S["overlap_last"] = over
# Overlap stability: count of years each state is in MRSA top-third-both
stab = {}
for y, g in a.groupby("year"):
    rep = g[g.mrsa_status == "reported"]
    tr = rep.mrsa_pct_resistant.quantile(2 / 3); ts = g.pct_hosp_small_rural.quantile(2 / 3)
    for u in rep[(rep.mrsa_pct_resistant >= tr) & (rep.pct_hosp_small_rural >= ts)].usps:
        stab[u] = stab.get(u, 0) + 1
S["mrsa_overlap_years_by_state"] = dict(sorted(stab.items(), key=lambda kv: -kv[1]))

# ---------------------------------------------------------------- sensitivity: small-hospital cutoff
sens = {}
for cut in [50, 100, 200]:
    c2 = cnt.assign(small=cnt.certified_beds < cut)
    sens[str(cut)] = {"n": int(c2.small.sum()), "pct": r1(100 * c2.small.mean()),
                      "pct_beds": r1(100 * c2.loc[c2.small, "certified_beds"].sum() / c2.certified_beds.sum())}
S["sensitivity_small_cutoff_last"] = sens

# ---------------------------------------------------------------- Table 1: state profiles last year
t1 = L[["usps", "state_name", "hosp_total", "hosp_critical_access", "pct_hosp_small", "pct_hosp_rural",
        "pct_hosp_small_rural", "pct_beds_in_small", "mrsa_pct_resistant", "mrsa_n_tested", "cre_pct_resistant",
        "cre_n_tested", "vre_faecium_pct_resistant", "vre_faecium_n_tested", "vre_faecalis_pct_resistant"]]
t1.sort_values("state_name").to_csv(os.path.join(OUT, "tables", "table_state_profile_last_year.csv"), index=False)

json.dump(S, open(os.path.join(OUT, "paper_stats.json"), "w"), indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps({k: S[k] for k in ["hosp", "sensitivity_small_cutoff_last", "suppression_by_small_rural_tertile_last",
                                    "suppression_all_org_all_years_by_tertile", "tertile_sizes", "tertile_cutpoints_last",
                                    "assoc_last_cre_no_pr", "mrsa_overlap_years_by_state", "excluded_tiny_tx_max",
                                    "change_total_pct", "change_short_pct", "vre_pooled_last"]}, indent=1, default=str))
for p in ORG:
    r = S["res"][p]; s = S["assoc_last"][p]
    print(p, {k: r[k] for k in ["reported_last", "insufficient_last_states", "pooled_states_last", "median_last", "iqr_last", "max_last", "min_last", "state_share_of_national_isolates", "median_n_tested_last"]})
    print("   assoc", {k: s[k] for k in ["small_rural", "small_rural_or_cah", "small", "beds_in_small", "by_year_range", "by_year_n_p_lt_05", "by_year_n_negative"]})
    print("   overlap", [x["usps"] for x in S["overlap_last"][p]["states"]], S["overlap_last"][p]["threshold_resistance"], S["overlap_last"][p]["threshold_small_rural"])
print(S["national_by_facility_last"]); print(S["bed_bands_last"])
