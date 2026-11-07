// 10_revtex_docx.js - Build the two-column (APS REVTeX-style) preprint as a Word file.
//
// Plain-language summary: reads paper/revtex_content.json (made by
// 09_revtex_content.py from the manuscript) and lays it out like the arXiv
// template: centred title block, one-column abstract, two-column body in
// Palatino, Roman-numeral sections, "TABLE I" captions above tables with
// double rules, "FIG. 1" captions below figures, numbered equations, blue
// citations and red cross-references, and a two-column reference list.
// Output: paper/Abdulwahab_State_Resistance_Atlas_preprint_REVTeX_style.docx
const fs = require("fs");
const path = require("path");
const d = require("docx");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, SectionType, Header, PageNumber, TabStopType, Tab, Math: OMath, MathRun, MathFraction,
  MathSubScript, MathSuperScript, MathSubSuperScript, MathSum, FootnoteReferenceRun, ExternalHyperlink,
  ShadingType, VerticalAlign,
} = d;

const ROOT = path.resolve(__dirname, "..");
const PAPER = path.join(ROOT, "paper");
const C = JSON.parse(fs.readFileSync(path.join(PAPER, "revtex_content.json"), "utf8"));
const OUT = path.join(PAPER, "Abdulwahab_State_Resistance_Atlas_preprint_REVTeX_style.docx");

const FONT = "Palatino Linotype";
const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1080, GAP = 360;
const TEXT_W = PAGE_W - 2 * MARGIN;            // 10080 twips = 7.0 in
const COL_W = (TEXT_W - GAP) / 2;              // 4860 twips = 3.375 in
const PX = (tw) => Math.round(tw / 1440 * 96); // twips -> 96-dpi pixels
const BODY = 20, SMALL = 18, TINY = 15;        // half-points

// ---------------------------------------------------------------- runs
function runs(list, size = BODY, extra = {}) {
  const out = [];
  for (const r of list) {
    const base = {
      text: r.t, bold: !!r.b || !!extra.bold, italics: !!r.i, size, font: r.code ? "Courier New" : FONT,
      color: r.c || undefined, subScript: !!r.sub, superScript: !!r.sup,
    };
    if (r.code) base.size = size - 2;
    const urls = r.t.split(/(https?:\/\/[^\s)]+[^\s).,;])/);
    for (const part of urls) {
      if (!part) continue;
      if (/^https?:\/\//.test(part)) {
        out.push(new ExternalHyperlink({ link: part, children: [new TextRun({ ...base, text: part, color: "1F4FBF" })] }));
      } else {
        out.push(new TextRun({ ...base, text: part }));
      }
    }
  }
  return out;
}
const plain = (t, o = {}) => new TextRun({ text: t, font: FONT, size: BODY, ...o });

// ---------------------------------------------------------------- equations
const mr = (t) => new MathRun(t);
const sub = (b, s) => new MathSubScript({ children: [mr(b)], subScript: [mr(s)] });
const frac = (n, dd) => new MathFraction({ numerator: n, denominator: dd });
const EQ = {
  pct: () => [sub("p̂", "k,s,y"), mr("=100×"), frac([sub("R", "k,s,y")], [sub("N", "k,s,y")])],
  midp_lo: () => [mr("P(X>x∣"), sub("p", "L"), mr(")+"), frac([mr("1")], [mr("2")]), mr("P(X=x∣"), sub("p", "L"), mr(")="), frac([mr("α")], [mr("2")])],
  midp_hi: () => [mr("P(X<x∣"), sub("p", "U"), mr(")+"), frac([mr("1")], [mr("2")]), mr("P(X=x∣"), sub("p", "U"), mr(")="), frac([mr("α")], [mr("2")])],
  share: () => [sub("S", "s,y"), mr("=100×"), frac([new MathSubSuperScript({ children: [mr("H")], subScript: [mr("s,y")], superScript: [mr("SR")] })], [sub("H", "s,y")])],
  spearman: () => [mr("ρ=1−"), frac(
    [mr("6"), new MathSum({ children: [new MathSubSuperScript({ children: [mr("d")], subScript: [mr("i")], superScript: [mr("2")] })], subScript: [mr("i=1")], superScript: [mr("n")] })],
    [mr("n("), new MathSuperScript({ children: [mr("n")], superScript: [mr("2")] }), mr("−1)")])],
  topthird: () => [sub("𝒯", "k,y"), mr("={s:"), sub("S", "s,y"), mr("≥"), sub("Q", "2/3"), mr("("), sub("S", "y"), mr("),"),
                   sub("p̂", "k,s,y"), mr("≥"), sub("Q", "2/3"), mr("("), sub("p̂", "k,y"), mr(")}")],
};
function equation(b) {
  // typeset by Matplotlib mathtext (Palatino) at 600 dpi; shown at its natural 10.5-pt size
  const { w, h, buf } = pngSize(b.path);
  const width = Math.round(w / 600 * 96), height = Math.round(h / 600 * 96);
  return new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: COL_W / 2 }, { type: TabStopType.RIGHT, position: COL_W }],
    spacing: { before: 120, after: 120 },
    children: [new TextRun({ children: [new Tab()] }),
               new ImageRun({ type: "png", data: buf, transformation: { width, height },
                              altText: { title: `Equation ${b.n}`, description: `Equation ${b.n}`, name: `eq${b.n}` } }),
               new TextRun({ children: [new Tab()] }), plain(`(${b.n})`)],
  });
}

// ---------------------------------------------------------------- blocks
function para(b) {
  const hasUrl = b.runs.some((r) => /https?:\/\//.test(r.t));
  return new Paragraph({
    alignment: hasUrl ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
    indent: b.noindent ? undefined : { firstLine: 240 },
    spacing: { after: 0, line: 245 },
    children: runs(b.runs),
  });
}
function h1(text, first) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, keepLines: true,
    spacing: { before: first ? 120 : 360, after: 200 },
    children: [plain(text, { bold: true, size: 19 })],
  });
}
function h2(b) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, keepLines: true,
    spacing: { before: 280, after: 160 },
    children: runs(b.runs, BODY, { bold: true }),
  });
}

function pngSize(file) {
  const buf = fs.readFileSync(file);
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20), buf };
}
function figure(b) {
  const { w, h, buf } = pngSize(b.path);
  const width = b.full ? PX(TEXT_W) - 6 : PX(COL_W) - 4;
  const height = Math.round(width * h / w);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 },
      children: [new ImageRun({ type: "png", data: buf, transformation: { width, height },
                                altText: { title: `Figure ${b.n}`, description: b.caption.map((r) => r.t).join(""), name: `fig${b.n}` } })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 240, line: 230 },
      indent: b.full ? { left: 360, right: 360 } : { left: 120, right: 120 },
      children: [plain(`FIG. ${b.n}: `, { size: SMALL }), ...runs(b.caption, SMALL)],
    }),
  ];
}

function table(b) {
  const W = b.full ? TEXT_W : COL_W;
  const ncol = b.rows[0].length;
  // column widths proportional to the longest cell text (bounded)
  const len = Array(ncol).fill(4);
  b.rows.forEach((row, i) => row.forEach((cell, j) => {
    const txt = cell.map((r) => r.t).join("");
    const L = i === 0 ? Math.max(...txt.split(/\s+/).map((w) => w.length)) * 1.15 : Math.min(txt.length, 40);
    len[j] = Math.max(len[j], L);
  }));
  const tot = len.reduce((a, x) => a + x, 0);
  const widths = len.map((x) => Math.floor(W * x / tot));
  widths[ncol - 1] += W - widths.reduce((a, x) => a + x, 0);
  const size = b.full ? 16 : TINY;
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const dbl = { style: BorderStyle.DOUBLE, size: 4, color: "000000" };
  const single = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const rows = b.rows.map((row, i) => new TableRow({
    tableHeader: i === 0, cantSplit: true,
    children: row.map((cell, j) => new TableCell({
      width: { size: widths[j], type: WidthType.DXA },
      margins: { top: 25, bottom: 25, left: 70, right: 70 },
      verticalAlign: VerticalAlign.BOTTOM,
      borders: {
        top: i === 0 ? dbl : none, bottom: i === 0 ? single : (i === b.rows.length - 1 ? dbl : none),
        left: none, right: none,
      },
      children: [new Paragraph({
        alignment: (b.align && b.align[j] === "right") ? AlignmentType.RIGHT : AlignmentType.LEFT,
        spacing: { after: 0, line: 220 }, children: runs(cell, size),
      })],
    })),
  }));
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 200, after: 120, line: 230 },
      indent: b.full ? { left: 360, right: 360 } : undefined,
      children: [plain(`TABLE ${b.roman}: `, { size: SMALL }), ...runs(b.caption, SMALL)],
    }),
    new Table({
      width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows,
      borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    }),
    new Paragraph({
      alignment: AlignmentType.JUSTIFIED, spacing: { before: 60, after: 240, line: 220 },
      children: runs(b.note, TINY),
    }),
  ];
}

// ---------------------------------------------------------------- front matter
const icon = fs.readFileSync(path.join(PAPER, "orcid_icon.png"));
const front = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200, line: 280 },
                  children: [plain(C.title, { bold: true, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [
    plain(C.author.name, { size: 21 }),
    new ExternalHyperlink({ link: `https://orcid.org/${C.author.orcid}`, children: [
      new ImageRun({ type: "png", data: icon, transformation: { width: 10, height: 10 },
                     altText: { title: "ORCID", description: `ORCID ${C.author.orcid}`, name: "orcid" } })] }),
    plain(",1,", { size: 21, superScript: true }),
    new FootnoteReferenceRun(1),
  ] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 280 }, children: [
    plain("1", { size: 19, superScript: true }), plain(C.author.affiliation, { size: 19, italics: true })] }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 720, right: 720, firstLine: 240 },
                  spacing: { after: 60, line: 245 }, children: runs(C.abstract) }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { left: 720, right: 720 }, spacing: { after: 240 },
                  children: [plain("Keywords: ", { bold: true }), plain(C.keywords)] }),
];

// ---------------------------------------------------------------- sections
const header = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
  children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: BODY })] })] });
const firstHeader = new Header({ children: [new Paragraph({ children: [] })] });
const pageProps = {
  page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: 1080, bottom: 1080, left: MARGIN, right: MARGIN, header: 576 } },
};
const sections = [{
  properties: { ...pageProps, titlePage: true },
  headers: { default: header, first: firstHeader },
  children: front,
}];
let cur = [];
const twoCol = () => ({ properties: { ...pageProps, type: SectionType.CONTINUOUS, column: { count: 2, space: GAP, equalWidth: true } } });
const oneCol = () => ({ properties: { ...pageProps, type: SectionType.CONTINUOUS, column: { count: 1 } } });
function flush() { if (cur.length) { sections.push({ ...twoCol(), children: cur }); cur = []; } }

let firstH1 = true;
for (const b of C.blocks) {
  if (b.type === "h1") { cur.push(h1(b.text, firstH1)); firstH1 = false; }
  else if (b.type === "h2") cur.push(h2(b));
  else if (b.type === "p") cur.push(para(b));
  else if (b.type === "eq") cur.push(equation(b));
  else if (b.type === "figure" || b.type === "table") {
    const items = b.type === "figure" ? figure(b) : table(b);
    if (b.full) { flush(); sections.push({ ...oneCol(), children: items }); }
    else cur.push(...items);
  }
}
// references: short centred rule, then numbered list in small type
cur.push(new Paragraph({ spacing: { before: 360, after: 200 }, indent: { left: 1500, right: 1500 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "000000", space: 1 } }, children: [] }));
C.references.forEach((r, k) => cur.push(new Paragraph({
  alignment: AlignmentType.LEFT, indent: { left: 400, hanging: 400 }, spacing: { after: 40, line: 220 },
  tabStops: [{ type: TabStopType.LEFT, position: 400 }],
  children: [new TextRun({ text: `[${k + 1}]`, font: FONT, size: 16 }), new TextRun({ children: [new Tab()], size: 16 }), ...runs(r, 16)],
})));
flush();
sections.push({ ...oneCol(), children: [new Paragraph({ spacing: { after: 0 }, children: [] })] });

const doc = new Document({
  creator: C.author.name, title: C.title, description: "Preprint",
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  footnotes: { 1: { children: [new Paragraph({ children: [plain(C.author.email, { size: 16 })] })] } },
  sections,
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", path.relative(ROOT, OUT), `${sections.length} sections`); });
