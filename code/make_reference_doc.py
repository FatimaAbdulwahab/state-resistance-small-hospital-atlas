#!/usr/bin/env python3
"""Make paper/reference.docx: the default preprint style used by 08_manuscript.py
(serif body, sans headings, US Letter, 1-inch margins, page numbers). Replace
paper/reference.docx with any Word template to restyle the manuscript."""
import os, subprocess
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paper")
src = os.path.join(P, "default_ref.docx")
subprocess.run(["pandoc", "-o", src, "--print-default-data-file", "reference.docx"], check=True)
d = Document(src)
def font(st, name, size, bold=None, color=None, italic=None):
    st.font.name = name; st.font.size = Pt(size)
    rpr = st.element.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None: rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(k), name)
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(k)) is not None: del rf.attrib[qn(k)]
    if bold is not None: st.font.bold = bold
    if italic is not None: st.font.italic = italic
    if color: st.font.color.rgb = RGBColor.from_string(color)
S = {st.name: st for st in d.styles}
for nm in ["Normal", "Body Text", "First Paragraph"]:
    if nm in S:
        font(S[nm], "Georgia", 10.5)
        pf = S[nm].paragraph_format; pf.space_after = Pt(6); pf.line_spacing = 1.2
if "Compact" in S:  # table cells
    font(S["Compact"], "Arial", 8.5); S["Compact"].paragraph_format.space_after = Pt(1); S["Compact"].paragraph_format.line_spacing = 1.05
font(S["Title"], "Arial", 17, bold=True, color="111111"); S["Title"].paragraph_format.space_after = Pt(10)
for nm in ["Author", "Subtitle"]:
    if nm in S: font(S[nm], "Arial", 10, color="333333")
for nm, sz, before in [("Heading 1", 13, 16), ("Heading 2", 11, 12), ("Heading 3", 10.5, 10)]:
    font(S[nm], "Arial", sz, bold=True, color="1c3f6e", italic=False)
    pf = S[nm].paragraph_format; pf.space_before = Pt(before); pf.space_after = Pt(4); pf.keep_with_next = True
for nm in ["Image Caption", "Table Caption", "Caption"]:
    if nm in S:
        font(S[nm], "Arial", 8.5, italic=False, color="222222"); S[nm].paragraph_format.space_after = Pt(10)
for sec in d.sections:
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"): setattr(sec, m, Inches(1))
    p = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
    p.alignment = 1
    r = p.add_run()
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    r.font.size = Pt(8.5); r.font.name = "Arial"
d.save(os.path.join(P, "reference.docx")); os.remove(src)
print("wrote paper/reference.docx")
