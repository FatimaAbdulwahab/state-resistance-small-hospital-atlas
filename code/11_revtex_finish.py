#!/usr/bin/env python3
"""
11_revtex_finish.py - Final touches to the two-column Word file, then a PDF.

Plain-language summary: sets the author footnote mark to a symbol (*) as in
the template, removes empty folder entries from the file (some cloud services
refuse files that have them), and renders a matching PDF with LibreOffice.
"""
import os, re, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "paper", "Abdulwahab_State_Resistance_Atlas_preprint_REVTeX_style.docx")
tmp = F + ".tmp"
with zipfile.ZipFile(F) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for item in zi.infolist():
        if item.filename.endswith("/"):
            continue
        data = zi.read(item.filename)
        if item.filename == "word/document.xml":
            x = data.decode("utf8")
            # symbol footnote marks (*, †, ‡) in every section; footnotePr precedes w:type / w:pgSz
            fp = '<w:footnotePr><w:numFmt w:val="chicago"/></w:footnotePr>'
            x = re.sub(r"(<w:sectPr[^>]*>(?:<w:headerReference[^>]*/>|<w:footerReference[^>]*/>)*)", r"\1" + fp, x)
            data = x.encode("utf8")
        if item.filename == "word/settings.xml":
            x = data.decode("utf8")
            if "<w:footnotePr>" in x:
                x = re.sub(r"<w:footnotePr>", '<w:footnotePr><w:numFmt w:val="chicago"/>', x, count=1)
            data = x.encode("utf8")
        zo.writestr(item, data)
os.replace(tmp, F)
exe = shutil.which("soffice") or shutil.which("libreoffice")
if exe:
    with tempfile.TemporaryDirectory() as t:
        subprocess.run([exe, "--headless", f"-env:UserInstallation=file://{t}/p", "--convert-to", "pdf",
                        "--outdir", os.path.dirname(F), F], check=True, capture_output=True)
    print("wrote", os.path.basename(F), "and PDF")
