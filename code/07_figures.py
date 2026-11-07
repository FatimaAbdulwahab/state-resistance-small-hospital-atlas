#!/usr/bin/env python3
"""
07_figures.py - Preprint figures (Matplotlib/Seaborn), from the atlas tables.

Plain-language summary: draws every figure in the preprint from the finished
data and paper/paper_stats.json, and saves each as PNG (300 dpi) and PDF in
paper/figures/. Nothing is typed in by hand.
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch
from matplotlib.collections import PatchCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
import seaborn as sns

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "paper", "figures")
os.makedirs(OUT, exist_ok=True)
a = pd.read_csv(os.path.join(P, "atlas_state_year.csv"), dtype={"state_fips": str})
h = pd.read_csv(os.path.join(P, "hospital_list_by_year.csv"), dtype={"ccn": str, "subtype": str})
S = json.load(open(os.path.join(ROOT, "paper", "paper_stats.json")))
Y1 = S["last_year"]
L = a[a.year == Y1].copy()

# Journal (REVTeX-like) style: boxed axes, inward ticks on all sides, minor ticks, no in-plot titles.
sns.set_theme(style="ticks", context="paper", font="DejaVu Sans")
plt.rcParams.update({"axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
                     "legend.fontsize": 6.5, "figure.dpi": 150, "savefig.dpi": 400, "axes.titleweight": "normal",
                     "axes.edgecolor": "black", "axes.linewidth": 0.7, "pdf.fonttype": 42,
                     "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
                     "xtick.minor.visible": True, "ytick.minor.visible": True,
                     "xtick.major.size": 3.5, "ytick.major.size": 3.5, "xtick.minor.size": 1.8, "ytick.minor.size": 1.8,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})
COL, FULL = 3.4, 7.0  # inches: one column, full page width
def panel(ax, letter):
    ax.text(0.0, 1.02, f"({letter})", transform=ax.transAxes, fontsize=8, fontweight="bold", va="bottom")
BLUES = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
C_BLUE, C_ORANGE, C_GRAY, C_AQUA, C_YELLOW = "#2a78d6", "#eb6834", "#8a8984", "#1baf7a", "#eda100"
ORG = {"mrsa": "MRSA", "cre": "CRE", "vre_faecium": "VRE, E. faecium", "vre_faecalis": "VRE, E. faecalis"}
ORG_IT = {"mrsa": "MRSA", "cre": "CRE", "vre_faecium": r"VRE, $\it{E.\ faecium}$", "vre_faecalis": r"VRE, $\it{E.\ faecalis}$"}
ORG_COL = {"mrsa": C_BLUE, "cre": C_ORANGE, "vre_faecium": C_AQUA, "vre_faecalis": C_YELLOW}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- topojson decode
def topo_polys(path, obj="states"):
    t = json.load(open(path))
    sc, tr = (t["transform"]["scale"], t["transform"]["translate"]) if "transform" in t else ([1, 1], [0, 0])
    arcs = []
    for arc in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            if "transform" in t:
                x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
            else:
                pts.append((dx, dy))
        arcs.append(pts)
    def ring(idx):
        pts = []
        for i in idx:
            seg = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(seg if not pts else seg[1:])
        return pts
    out = {}
    for g in t["objects"][obj]["geometries"]:
        rings = []
        if g["type"] == "Polygon":
            rings = [ring(r) for r in g["arcs"][:1]]
        elif g["type"] == "MultiPolygon":
            rings = [ring(p[0]) for p in g["arcs"]]
        out[g["id"]] = rings
    return out

VEND = os.path.join(ROOT, "site_src", "vendor")
ALB = os.path.join(VEND, "states-albers-10m.json")
GEO = topo_polys(ALB)
PR = topo_polys(os.path.join(VEND, "states-10m.json"))["72"]


def choropleth(ax, values, bins, letter, legend_title, na_label="<20 isolates tested"):
    cmap = ListedColormap(BLUES)
    norm = BoundaryNorm(bins, cmap.N)
    def draw(rings, v, xf=lambda p: p):
        for r in rings:
            pts = [xf(p) for p in r]
            if v is None or (isinstance(v, float) and np.isnan(v)):
                ax.add_patch(Polygon(pts, closed=True, facecolor="#eeeeec", edgecolor="#7a7a7a", hatch="//////", lw=0.3))
            else:
                ax.add_patch(Polygon(pts, closed=True, facecolor=cmap(norm(v)), edgecolor="white", lw=0.3))
    for fips, rings in GEO.items():
        draw(rings, values.get(fips))
    lon0, lat0 = -67.3, 17.9  # Puerto Rico inset from lon/lat
    xf = lambda p: (840 + (p[0] - lon0) * 38, 590 - (p[1] - lat0) * 38 * 1.05)
    draw(PR, values.get("72"), xf)
    ax.text(880, 618, "PR", ha="center", va="top", fontsize=6, color="#444444")
    ax.set_xlim(-60, 975); ax.set_ylim(630, 0); ax.set_aspect("equal"); ax.axis("off")
    ax.text(-55, 10, f"({letter})", fontsize=8, fontweight="bold", va="top")
    labels = [f"<{bins[1]:g}"] + [f"{bins[i]:g}–{bins[i+1]:g}" for i in range(1, len(bins) - 2)] + [f"≥{bins[-2]:g}"]
    handles = [Patch(facecolor=BLUES[i], edgecolor="#999999", lw=0.3, label=l) for i, l in enumerate(labels)]
    if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in values.values()):
        handles.append(Patch(facecolor="#eeeeec", edgecolor="#7a7a7a", hatch="//////", lw=0.3, label=na_label))
    ax.legend(handles=handles, title=legend_title, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3,
              title_fontsize=6.5, fontsize=6.5, handlelength=1.3, columnspacing=0.9, handletextpad=0.4)


# ---------------------------------------------------------------- Figure 1: maps (full width)
fig, axes = plt.subplots(1, 2, figsize=(FULL, 3.0))
v1 = dict(zip(L.state_fips, L.pct_hosp_small_rural))
v2 = {f: (v if s == "reported" else None) for f, v, s in zip(L.state_fips, L.mrsa_pct_resistant, L.mrsa_status)}
choropleth(axes[0], v1, [0, 10, 25, 40, 55, 101], "a", "Small and rural hospitals, % of general hospitals")
choropleth(axes[1], v2, [0, 30, 35, 40, 45, 101], "b", "MRSA, % resistant")
fig.subplots_adjust(wspace=0.04, left=0.01, right=0.99)
save(fig, "fig1_maps")

# ---------------------------------------------------------------- Figure 2: hospitals vs beds by band
bb = pd.read_csv(os.path.join(ROOT, "paper", "tables", "table_bed_bands_last_year.csv"), index_col=0)
lab = {"1_24": "1–24", "25_49": "25–49", "50_99": "50–99", "100_199": "100–199", "200_399": "200–399", "400_plus": "≥400"}
fig, ax = plt.subplots(figsize=(COL, 2.5))
yy = np.arange(len(bb))
ax.barh(yy - 0.19, bb.pct_hospitals, height=0.36, color=C_BLUE, label="Hospitals")
ax.barh(yy + 0.19, bb.pct_beds, height=0.36, color=C_ORANGE, label="Certified beds")
for i, (ph, pb) in enumerate(zip(bb.pct_hospitals, bb.pct_beds)):
    ax.text(ph + 0.7, i - 0.19, f"{ph:.1f}", va="center", fontsize=5.8)
    ax.text(pb + 0.7, i + 0.19, f"{pb:.1f}", va="center", fontsize=5.8)
ax.set_yticks(yy); ax.set_yticklabels([lab[i] for i in bb.index]); ax.invert_yaxis()
ax.tick_params(axis="y", which="minor", left=False, right=False)
ax.axhline(2.5, color="#555555", lw=0.6, ls="--")
ax.text(49, 2.42, "<100 beds above", fontsize=5.8, color="#444444", ha="right", va="bottom")
ax.set_xlabel("Share (%)"); ax.set_ylabel("Certified beds"); ax.set_xlim(0, 50)
ax.legend(loc="upper right")
save(fig, "fig2_bed_bands")

# ---------------------------------------------------------------- Figure 3: national counts by year
ann = pd.read_csv(os.path.join(ROOT, "paper", "tables", "table_national_hospitals_by_year.csv"), index_col=0)
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(COL, 3.5), sharex=True, gridspec_kw={"height_ratios": [2.1, 1], "hspace": 0.12})
ax.plot(ann.index, ann.short, marker="o", ms=3, color=C_BLUE, lw=1.2, label="Short-term acute care")
ax.plot(ann.index, ann.cah, marker="s", ms=3, color=C_ORANGE, lw=1.2, label="Critical access")
ax.plot(ann.index, ann.small_rural, marker="^", ms=3, color=C_AQUA, lw=1.2, label="Small and rural")
ax.set_ylabel("Hospitals"); ax.set_ylim(0, 4000)
ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.62))
panel(ax, "a")
ax2.bar(ann.index, ann.excluded_tiny, color=C_GRAY, width=0.7)
for x, v in zip(ann.index, ann.excluded_tiny):
    ax2.text(x, v + 8, str(int(v)), ha="center", fontsize=5.5)
ax2.set_ylabel("Excluded"); ax2.set_ylim(0, 340)
ax2.set_xticks(ann.index); ax2.set_xticklabels(ann.index, rotation=60)
ax2.tick_params(axis="x", which="minor", bottom=False, top=False)
panel(ax2, "b")
save(fig, "fig3_hospitals_by_year")

# ---------------------------------------------------------------- Figure 4: scatter grid (full width)
fig, axes = plt.subplots(2, 2, figsize=(FULL, 5.2))
for ax, p, letter in zip(axes.flat, ["mrsa", "cre", "vre_faecium", "vre_faecalis"], "abcd"):
    rep = L[L[f"{p}_status"] == "reported"]
    vals = rep[f"{p}_pct_resistant"]
    ov = {s["usps"] for s in S["overlap_last"][p]["states"]}
    ext = {S["res"][p]["max_last"]["usps"]}
    if (vals == vals.min()).sum() == 1:
        ext.add(S["res"][p]["min_last"]["usps"])
    tr, ts = S["overlap_last"][p]["threshold_resistance"], S["overlap_last"][p]["threshold_small_rural"]
    ax.axvline(ts, color="#777777", lw=0.6, ls="--"); ax.axhline(tr, color="#777777", lw=0.6, ls="--")
    col = [C_ORANGE if u in ov else C_BLUE for u in rep.usps]
    ax.scatter(rep.pct_hosp_small_rural, vals, s=16, c=col, edgecolor="white", lw=0.4, zorder=3)
    for u, x, y in zip(rep.usps, rep.pct_hosp_small_rural, vals):
        if u in ov or u in ext:
            off = (4, -8) if (p == "mrsa" and u == "AR") else (3, 2)
            ax.annotate(u, (x, y), xytext=off, textcoords="offset points", fontsize=6, fontweight="bold")
    st = S["assoc_last"][p]["small_rural"]
    ptxt = "$p<0.001$" if st["p"] < 0.001 else f"$p={st['p']:.3f}$"
    ax.text(0.97, 0.96 if p != "vre_faecalis" else 0.70, f"$\\rho={st['rho']:.2f}$\n{ptxt}\n$n={st['n']}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.5)
    ax.set_xlim(-3, 90)
    ax.set_ylim(min(0, vals.min()) - 0.04 * vals.max(), vals.max() * 1.22)
    ax.set_xlabel("Small and rural hospitals (% of general hospitals)")
    ax.set_ylabel(f"{ORG_IT[p]}, % resistant")
    if p == "cre":
        ax.set_yscale("symlog", linthresh=5, linscale=1.5); ax.set_ylim(-0.3, 70)
        ax.set_yticks([0, 1, 2, 3, 4, 5, 10, 20, 40]); ax.set_yticklabels(["0", "1", "2", "3", "4", "5", "10", "20", "40"])
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_ylabel("CRE, % resistant")
    panel(ax, letter)
fig.tight_layout(h_pad=1.6, w_pad=2.0)
save(fig, "fig4_scatter")

# ---------------------------------------------------------------- Figure 5: rho by year
fig, ax = plt.subplots(figsize=(COL, 2.6))
for p in ["mrsa", "cre", "vre_faecium", "vre_faecalis"]:
    ser = S["assoc_last"][p]["by_year_small_rural"]
    yrs = [int(y) for y in ser]; rho = [ser[y]["rho"] for y in ser]; pv = [ser[y]["p"] for y in ser]
    ax.plot(yrs, rho, color=ORG_COL[p], lw=1.1, label=ORG_IT[p])
    ax.scatter([y for y, q in zip(yrs, pv) if q < 0.05], [r for r, q in zip(rho, pv) if q < 0.05], color=ORG_COL[p], s=11, zorder=3)
    ax.scatter([y for y, q in zip(yrs, pv) if q >= 0.05], [r for r, q in zip(rho, pv) if q >= 0.05], facecolor="white", edgecolor=ORG_COL[p], s=11, lw=0.8, zorder=3)
ax.axhline(0, color="black", lw=0.6, ls=":")
ax.set_ylim(-0.85, 0.48); ax.set_ylabel(r"Spearman $\rho$ across states")
ax.set_xticks(range(S["first_year"], Y1 + 1)); ax.tick_params(axis="x", rotation=60)
ax.tick_params(axis="x", which="minor", bottom=False, top=False)
ax.legend(loc="upper center", ncol=2, columnspacing=1.0, handlelength=1.4, fontsize=6)
save(fig, "fig5_rho_by_year")

# ---------------------------------------------------------------- Figure 6: suppression by tertile
sup = S["suppression_by_tertile_all_years"]
rows = [(ORG[p], t, sup[p][t]) for p in ["mrsa", "cre", "vre_faecalis", "vre_faecium"] for t in ["low", "middle", "high"]]
d = pd.DataFrame(rows, columns=["org", "tertile", "n"])
fig, ax = plt.subplots(figsize=(COL, 2.4))
sns.barplot(data=d, x="org", y="n", hue="tertile", palette=[BLUES[1], BLUES[2], BLUES[4]], ax=ax, edgecolor="white", linewidth=0.4)
for c in ax.containers:
    ax.bar_label(c, fontsize=5.5, padding=1)
ax.set_xlabel(""); ax.set_ylabel("State-years with no published %")
ax.set_xticks(range(4)); ax.set_xticklabels(["MRSA", "CRE", r"$\it{E.\ faecalis}$", r"$\it{E.\ faecium}$"])
ax.tick_params(axis="x", which="minor", bottom=False, top=False)
ax.legend(title="Small-and-rural share (tertile)", ncol=3, loc="upper left", title_fontsize=6.5)
ax.set_ylim(0, max(d.n) * 1.3)
save(fig, "fig6_suppression")

# ---------------------------------------------------------------- Figure 7: MRSA overlap persistence
states = list(S["mrsa_overlap_years_by_state"].keys())
yrs = list(range(S["first_year"], Y1 + 1))
grid = np.zeros((len(states), len(yrs)))
for j, y in enumerate(yrs):
    g = a[a.year == y]; rep = g[g.mrsa_status == "reported"]
    tr = rep.mrsa_pct_resistant.quantile(2 / 3); ts = g.pct_hosp_small_rural.quantile(2 / 3)
    sel = set(rep[(rep.mrsa_pct_resistant >= tr) & (rep.pct_hosp_small_rural >= ts)].usps)
    for i, u in enumerate(states):
        grid[i, j] = 1 if u in sel else 0
fig, ax = plt.subplots(figsize=(COL, 2.3))
sns.heatmap(grid, cmap=ListedColormap(["#f1f0ec", C_ORANGE]), cbar=False, linewidths=0.8, linecolor="white",
            xticklabels=yrs, yticklabels=[f"{u} ({S['mrsa_overlap_years_by_state'][u]})" for u in states], ax=ax)
ax.set_xlabel(""); ax.tick_params(axis="x", rotation=60, labelsize=6); ax.tick_params(axis="y", rotation=0, labelsize=6.5)
ax.tick_params(which="both", top=False, right=False, length=0)
save(fig, "fig7_mrsa_overlap")

# ---------------------------------------------------------------- Figure 8 (appendix): critical access hospitals
cah = h[(h.year.astype(str) == str(Y1)) & (h.subtype == "11")]
fig, ax = plt.subplots(figsize=(COL, 2.3))
bins = np.arange(0.5, cah.certified_beds.max() + 5.5, 5)  # 1-5, 6-10, ..., 21-25, 26-30 ...
ax.hist([cah[cah.urban_rural_code == "R"].certified_beds, cah[cah.urban_rural_code == "U"].certified_beds],
        bins=bins, stacked=True, color=[C_BLUE, C_ORANGE], label=["CMS flag: rural", "CMS flag: urban"], edgecolor="white", linewidth=0.3)
ax.axvline(25.5, color="black", lw=0.6, ls="--"); ax.text(27, ax.get_ylim()[1] * 0.42, "25 beds", fontsize=6)
over = int((cah.certified_beds > 60).sum())
ax.set_xlim(0, 60.5)
ax.text(59, ax.get_ylim()[1] * 0.55, f"{over} hospitals >60 beds\n(max {int(cah.certified_beds.max())}) not shown", fontsize=5.8, ha="right")
ax.set_xlabel("Certified beds"); ax.set_ylabel("Critical access hospitals")
ax.legend(loc="upper right")
save(fig, "figS1_cah")
print("figures:", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
