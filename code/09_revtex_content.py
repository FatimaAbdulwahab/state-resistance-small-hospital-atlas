#!/usr/bin/env python3
"""
09_revtex_content.py - Convert paper/manuscript.md into the structured content
for the two-column (APS REVTeX-style) preprint built by code/10_revtex_docx.js.

Plain-language summary: the words and numbers come unchanged from the
manuscript (which 08_manuscript.py fills from the stats files). This script
only re-arranges them into the template's structure: Roman-numeral sections,
lettered subsections, "TABLE I" and "FIG. 1" captions, numbered equations in
the Methods, floats placed near their first mention, and colored citations
and cross-references. Output: paper/revtex_content.json.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
md = open(os.path.join(PAPER, "manuscript.md")).read()
md = re.sub(r"```\{=openxml\}.*?```", "", md, flags=re.S)  # drop page-break markers
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII"}
FULL_WIDTH_TABLES = {2, 3, 4}


# ---------------------------------------------------------------- figure numbering by first mention
_body = md.split("# Introduction", 1)[1].split("# Declarations", 1)[0]
_order = []
for m in re.finditer(r"(?<!Supplementary )Figure (\d)", _body):
    if int(m.group(1)) not in _order:
        _order.append(int(m.group(1)))
FIGMAP = {old: new for new, old in enumerate(_order, start=1)}
FULL_WIDTH_FIGS = {FIGMAP[1], FIGMAP[4]}  # the maps and the 2x2 scatter grid span both columns

# ---------------------------------------------------------------- text transforms
def xref(text):
    text = text.replace("Supplementary Figure S1", "Fig. 8 in Appendix A")
    text = text.replace("(see Results)", "(Sec. III)")
    text = re.sub(r"Figure (\d)([AB])\b", lambda m: f"Fig. {FIGMAP[int(m.group(1))]}({m.group(2).lower()})", text)
    text = re.sub(r"\bFigure (\d)", lambda m: f"Fig. {FIGMAP[int(m.group(1))]}", text)
    text = re.sub(r"\bTable (\d)", lambda m: f"Table {ROMAN[int(m.group(1))]}", text)
    return text


def inline(text, body=True):
    """Markdown-lite to runs: **bold**, *italic*, `code`; colors citations (blue) and cross-references (red)."""
    text = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", text)
    text = re.sub(r"(?<=\w)'(?=\w)", "\u2019", text)
    text = re.sub(r"(?<=[\s(=])-(?=\d)", "\u2212", text)  # true minus signs
    if body:
        text = xref(text)
    runs = []
    for tok in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+`)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            runs += [dict(r, b=True) for r in color(tok[2:-2])]
        elif tok.startswith("`"):
            runs.append({"t": tok[1:-1], "code": True})
        elif tok.startswith("*"):
            runs += [dict(r, i=True) for r in color(tok[1:-1])]
        else:
            runs += color(tok)
    return runs


PAT = re.compile(r"(\[\d+(?:[,–-]\d+)*\])|((?:Fig\.|Figs\.|Table|Tables|Eq\.|Eqs\.|Sec\.|Appendix) )"
                 r"((?:\d+|[IVX]+|[A-Z])(?:\([a-d]\))?(?:(?:, | and |–)(?:\d+|[IVX]+))*)"
                 r"|((?:Eq\.|Eqs\.) )(\(\d+\)(?: and \(\d+\))?)")


def color(text):
    out, pos = [], 0
    for m in PAT.finditer(text):
        if m.start() > pos:
            out.append({"t": text[pos:m.start()]})
        if m.group(1):
            inner = m.group(1)[1:-1]
            out += [{"t": "["}, {"t": inner, "c": "1F4FBF"}, {"t": "]"}]
        elif m.group(2):
            out += [{"t": m.group(2)}, {"t": m.group(3), "c": "C0001A"}]
        else:
            out += [{"t": m.group(4)}, {"t": m.group(5), "c": "C0001A"}]
        pos = m.end()
    if pos < len(text):
        out.append({"t": text[pos:]})
    return out


# ---------------------------------------------------------------- parse manuscript.md
title = re.search(r'^title: "(.+?)"', md, flags=re.M).group(1)
body = md.split("\n---\n", 1)[1]
lines = body.split("\n")

blocks, tables, figures, refs = [], {}, {}, []
abstract, keywords = [], ""
section = None; sec_no = 0; sub_no = 0
NUMBERED = ["Introduction", "Methods", "Results", "Discussion", "Conclusions"]
i = 0
cur_table = None
while i < len(lines):
    ln = lines[i].rstrip()
    i += 1
    if not ln.strip():
        continue
    if ln.startswith("**Keywords:**"):
        keywords = ln.split("**Keywords:**", 1)[1].strip(); continue
    if ln.startswith("**Correspondence") or ln.startswith("**Article type") or ln.startswith("**Running title"):
        continue
    if ln.startswith("# "):
        section = ln[2:].strip(); sub_no = 0
        if section in NUMBERED:
            sec_no += 1
            blocks.append({"type": "h1", "text": f"{ROMAN[sec_no]}.  {section.upper()}"})
        elif section == "Declarations":
            blocks.append({"type": "h1", "text": "DECLARATIONS"})
        continue
    if ln.startswith("## "):
        sub_no += 1
        blocks.append({"type": "h2", "runs": inline(f"{chr(64 + sub_no)}.  {ln[3:].strip()}")}); continue
    if section == "Abstract":
        abstract.append(re.sub(r"^\*\*[A-Za-z]+\.\*\*\s*", "", ln)); continue
    if section == "References":
        m = re.match(r"(\d+)\.\s+(.*)", ln)
        if m:
            refs.append(inline(m.group(2), body=False))
        continue
    if section == "Tables":
        m = re.match(r"\*\*Table (\d)\.\*\*\s*(.*)", ln)
        if m:
            cur_table = int(m.group(1)); tables[cur_table] = {"caption": m.group(2), "rows": [], "note": ""}; continue
        if ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                tables[cur_table]["rows"].append(cells)
            else:
                tables[cur_table]["align"] = ["right" if c.endswith(":") and not c.startswith(":") else "left" for c in cells]
            continue
        tables[cur_table]["note"] = ln; continue
    if section in ("Figures", "Supplementary material"):
        m = re.match(r"!\[\*\*(?:Supplementary )?Figure (S?\d)\.\*\*\s*(.*)\]\((.+?)\)", ln)
        if m:
            num = 8 if m.group(1) == "S1" else FIGMAP[int(m.group(1))]
            figures[num] = {"caption": m.group(2), "path": m.group(3)}
        continue
    # body paragraph
    if section == "Declarations":
        blocks.append({"type": "p", "runs": inline(ln), "noindent": True}); continue
    if section in NUMBERED:
        blocks.append({"type": "p", "runs": inline(ln), "raw": ln})

# ---------------------------------------------------------------- equations in Methods
def insert_after(substr, new_blocks):
    for k, b in enumerate(blocks):
        if b["type"] == "p" and substr in b.get("raw", ""):
            blocks[k + 1:k + 1] = new_blocks
            return
    raise SystemExit(f"anchor not found: {substr}")

P = lambda txt, noindent=True: {"type": "p", "runs": inline(txt), "noindent": noindent, "raw": txt}
insert_after("CDC computes a pooled mean percent resistant", [
    P("Formally, for organism *k*, state *s* and year *y*, with resistant isolates *R* and isolates tested *N* summed over all reporting hospitals,"),
    {"type": "eq", "id": "pct", "n": 1},
    P("CDC's 95% interval [*p*~L~, *p*~U~] is the two-sided mid-P exact interval [10]: with *X* ~ Binomial(*N*, *p*) and *x* = *R*, the limits solve"),
    {"type": "eq", "id": "midp_lo", "n": 2},
    {"type": "eq", "id": "midp_hi", "n": 3},
    P("with α = 0.05. Our implementation of Eqs. (2) and (3) reproduces CDC's published limits (Sec. II F)."),
])
insert_after("For each state-year we computed: counts of general hospitals", [
    P("For example, the small-and-rural share used throughout is"),
    {"type": "eq", "id": "share", "n": 4},
    P("where *H*~s,y~ is the number of counted general hospitals and *H*~s,y~^SR^ the number with fewer than 100 certified beds and the CMS rural flag; the other shares are defined in the same way."),
])
insert_after("All analyses are descriptive.", [
    P("For *n* states with published values, Spearman's coefficient is the Pearson correlation of the ranks, which in the absence of ties reduces to"),
    {"type": "eq", "id": "spearman", "n": 5},
    P("where *d*~i~ is the difference between the two ranks of state *i*; tied values receive average ranks. The set of states flagged in year *y* for organism *k* is"),
    {"type": "eq", "id": "topthird", "n": 6},
    P("where *Q*~2/3~ is the 66.7th percentile across states in that year."),
])

# ---------------------------------------------------------------- equations as images
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": "TeX Gyre Pagella",
                     "mathtext.it": "TeX Gyre Pagella:italic", "mathtext.bf": "TeX Gyre Pagella:bold",
                     "mathtext.fallback": "stix", "font.family": "TeX Gyre Pagella"})
TEX = {
    "pct": r"$\hat{p}_{k,s,y} = 100 \times \dfrac{R_{k,s,y}}{N_{k,s,y}}$",
    "midp_lo": r"$P(X > x \mid p_{\mathrm{L}}) + \dfrac{1}{2}\,P(X = x \mid p_{\mathrm{L}}) = \dfrac{\alpha}{2}$",
    "midp_hi": r"$P(X < x \mid p_{\mathrm{U}}) + \dfrac{1}{2}\,P(X = x \mid p_{\mathrm{U}}) = \dfrac{\alpha}{2}$",
    "share": r"$S_{s,y} = 100 \times \dfrac{H^{\mathrm{SR}}_{s,y}}{H_{s,y}}$",
    "spearman": r"$\rho = 1 - \dfrac{6\,\sum_{i=1}^{n} d_i^{\,2}}{n\,(n^{2}-1)}$",
    "topthird": r"$T_{k,y} = \{\, s : S_{s,y} \geq Q_{2/3}(S_{\cdot,y}),\; \hat{p}_{k,s,y} \geq Q_{2/3}(\hat{p}_{k,\cdot,y}) \,\}$",
}
EQDIR = os.path.join(PAPER, "equations"); os.makedirs(EQDIR, exist_ok=True)
for b_ in blocks:
    if b_["type"] == "eq":
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, TEX[b_["id"]], fontsize=9.5 if b_["id"] == "topthird" else 10.5)
        fn = os.path.join(EQDIR, f"eq{b_['n']}.png")
        fig.savefig(fn, dpi=600, bbox_inches="tight", pad_inches=0.02, transparent=False, facecolor="white")
        plt.close(fig)
        b_["path"] = fn

# ---------------------------------------------------------------- appendix
blocks += [{"type": "h1", "text": "Appendix A: CRITICAL ACCESS HOSPITALS AND THE CMS RURAL FLAG", "appendix": True},
           P(f"Critical access hospital status is a Medicare designation for small, generally rural hospitals limited to 25 acute inpatient beds, yet the Provider of Services file lists some with more certified beds and assigns some an urban flag. Fig. 8 shows the distribution of certified beds among critical access hospitals in the final year, by CMS urban-rural flag. Most list 21 to 25 beds; those listing more likely include swing beds or distinct-part psychiatric or rehabilitation units. The urban-flagged share motivates the alternative small-and-rural-or-critical-access measure used in Table III.", noindent=False)]
# Footnote-like note on subscripts: convert ~x~ (sub) and ^x^ (sup) inside runs
def subsup(runs):
    out = []
    for r in runs:
        parts = re.split(r"(~[^~]+~|\^[^^]+\^)", r["t"])
        for p_ in parts:
            if not p_:
                continue
            if p_.startswith("~"):
                out.append(dict(r, t=p_[1:-1], sub=True))
            elif p_.startswith("^"):
                out.append(dict(r, t=p_[1:-1], sup=True))
            else:
                out.append(dict(r, t=p_))
    return out
for b in blocks:
    if "runs" in b:
        b["runs"] = subsup(b["runs"])

# ---------------------------------------------------------------- place floats after first mention
def first_mention(pattern, start=0):
    for k, b in enumerate(blocks):
        if k < start:
            continue
        if b["type"] == "p" and re.search(pattern, "".join(r["t"] for r in b["runs"])):
            return k
    return None
placements = []
for n_, t in tables.items():
    k = first_mention(rf"Table {ROMAN[n_]}\b")
    placements.append((k, {"type": "table", "n": n_, "roman": ROMAN[n_], "full": n_ in FULL_WIDTH_TABLES,
                           "caption": subsup(inline(t["caption"], body=False)),
                           "rows": [[subsup(inline(c, body=False)) for c in row] for row in t["rows"]],
                           "align": t.get("align"), "note": subsup(inline(t["note"], body=False))}))
for n_, f in figures.items():
    app = next(j for j, b in enumerate(blocks) if b.get("appendix"))
    k = first_mention(rf"Fig\. {n_}\b", start=app if n_ == 8 else 0)
    placements.append((k, {"type": "figure", "n": n_, "full": n_ in FULL_WIDTH_FIGS,
                           "caption": subsup(inline(re.sub(r"^\(A\)", "(a)", f["caption"]).replace(" (B) ", " (b) "), body=True)),
                           "path": os.path.join(PAPER, f["path"])}))
# insert from the end so indices stay valid; keep float order (table before figure if same anchor)
for k, fl in sorted(placements, key=lambda x: (x[0], 0 if x[1]["type"] == "table" else 1, x[1]["n"]), reverse=True):
    blocks.insert(k + 1, fl)
for b in blocks:
    b.pop("raw", None)

out = {"title": title,
       "author": {"name": "Fatima Abdulwahab", "orcid": "0009-0008-2298-8386", "email": "abdulwahabfatima43@gmail.com",
                  "affiliation": "Independent Researcher, Dallas, Texas, USA"},
       "abstract": subsup(inline(" ".join(abstract), body=False)),
       "keywords": keywords.replace(";", ","),
       "blocks": blocks, "references": [subsup(r) for r in refs]}
json.dump(out, open(os.path.join(PAPER, "revtex_content.json"), "w"), indent=1, ensure_ascii=False)
print(f"blocks {len(blocks)}; tables {sorted(tables)}; figures {sorted(figures)}; refs {len(refs)}")
print("float placements:", [(b['type'], b['n']) for b in blocks if b['type'] in ('table', 'figure')])
