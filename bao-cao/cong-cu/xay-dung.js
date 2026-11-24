// Dựng báo cáo .docx từ các tệp nội dung trong ../noi-dung theo định dạng báo cáo đồ án.
// Cách dùng: node xay-dung.js <tệp ra .docx> <tệp nội dung>...
// Cú pháp nội dung (một tập con của Markdown):
//   # Tiêu đề chương (Heading 1, sang trang mới)   ## Heading 2   ### Heading 3
//   Đoạn văn: các dòng liền nhau, cách đoạn bằng một dòng trống.
//   - mục danh sách        1. mục danh sách có số
//   **đậm**  *nghiêng*  `mã`  $công thức$  [@khóa] hoặc [@a; @b]
//   {{bang:khoa}} {{hinh:khoa}} {{ct:khoa}}: số của bảng, hình, công thức
//   $$ latex $$ {#ct:khoa}: công thức riêng dòng, có số (chương.thứ tự)
//   Bảng: | a | b | ... rồi dòng chú thích "Bảng: Tên bảng {#bang:khoa w=20,40,40 co=12}" ngay sau bảng
//   Hình: ![Tên hình](tep.png){#hinh:khoa rong=15} (rộng tính bằng cm)
//   Dòng "@@muc-luc", "@@danh-muc-bang", "@@danh-muc-hinh": chèn trường tự động
//   Dòng "@@khong-so" trước một tiêu đề cấp 1: tiêu đề không có trong số chương
const fs = require("fs");
const path = require("path");
const D = require("docx");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
  VerticalAlign, ImageRun, TableOfContents, SequentialIdentifier, Footer, PageNumber, NumberFormat,
  TabStopType, LevelFormat, LineRuleType, HeadingLevel, SectionType,
} = D;

const FONT = "Times New Roman";
const PT = (p) => Math.round(p * 2); // cỡ chữ tính bằng nửa điểm
const LINE = 312; // giãn dòng Multiple 1,3
const AFTER = 120; // cách sau 6 pt
const TEXT_W = 9072; // bề rộng vùng chữ: 21 - 3 - 2 = 16 cm
const CM = 567; // 1 cm tính bằng twip

const out = process.argv[2];
const files = process.argv.slice(3);
const ROOT = path.resolve(__dirname, "..");

// ---------- Bước 1: đọc nội dung, đánh số bảng, hình, công thức, trích dẫn ----------
const blocks = [];
for (const f of files) parse(fs.readFileSync(f, "utf8").replace(/\r\n/g, "\n"), path.dirname(f));

function parse(text, dir) {
  const lines = text.split("\n");
  let i = 0;
  let para = [];
  const flush = () => { if (para.length) { blocks.push({ t: "p", text: para.join(" ") }); para = []; } };
  while (i < lines.length) {
    const ln = lines[i];
    const s = ln.trim();
    if (s.startsWith("<!--")) { flush(); while (i < lines.length && !lines[i].includes("-->")) i++; i++; continue; }
    if (s === "") { flush(); i++; continue; }
    let m;
    if (s.startsWith("@@")) { flush(); blocks.push({ t: "cmd", name: s.slice(2) }); i++; continue; }
    if ((m = s.match(/^(#{1,3}) (.*)$/))) { flush(); blocks.push({ t: "h", level: m[1].length, text: m[2] }); i++; continue; }
    if (s.startsWith("|")) {
      flush();
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        const r = lines[i].trim();
        if (!/^\|\s*-{3}/.test(r)) rows.push(splitRow(r));
        i++;
      }
      let cap = null;
      while (i < lines.length && lines[i].trim() === "") i++;
      let opts = {};
      if (i < lines.length && (m = lines[i].trim().match(/^Bảng: (.*?)\s*(\{#bang:[^}]*\})?$/))) { cap = { text: m[1], opts: parseOpts(m[2]) }; opts = cap.opts; i++; }
      else if (i < lines.length && (m = lines[i].trim().match(/^\{bang (.*)\}$/))) { opts = parseOpts("{#bang:khong " + m[1] + "}"); i++; }
      blocks.push({ t: "table", rows, cap, opts });
      continue;
    }
    if ((m = s.match(/^!\[(.*)\]\((.*?)\)\s*(\{#hinh:[^}]*\})?$/))) {
      flush();
      blocks.push({ t: "img", cap: m[1], file: path.resolve(dir, m[2]), opts: parseOpts(m[3]) });
      i++; continue;
    }
    if ((m = s.match(/^\$\$(.*)\$\$\s*(\{#ct:[^}]*\})?$/))) { flush(); blocks.push({ t: "eq", tex: m[1].trim(), opts: parseOpts(m[2]) }); i++; continue; }
    if ((m = s.match(/^- (.*)$/))) { flush(); blocks.push({ t: "li", kind: "bullet", text: m[1] }); i++; continue; }
    if ((m = s.match(/^(\d+)\. (.*)$/)) && !/^\d+\.\d/.test(s)) { flush(); blocks.push({ t: "li", kind: "num", text: m[2] }); i++; continue; }
    para.push(s); i++;
  }
  flush();
}
function splitRow(r) { return r.replace(/^\|/, "").replace(/\|$/, "").split(/(?<!\\)\|/).map((c) => c.trim().replace(/\\\|/g, "|")); }
function parseOpts(s) {
  const o = {};
  if (!s) return o;
  const m = s.match(/^\{#(\w+):([\w-]+)\s*(.*)\}$/);
  if (!m) return o;
  o.kind = m[1]; o.key = m[2];
  for (const kv of m[3].split(/\s+/).filter(Boolean)) { const [k, v] = kv.split("="); o[k] = v; }
  return o;
}

// Đánh số theo thứ tự xuất hiện. Công thức đánh số theo chương.
const nums = { bang: {}, hinh: {}, ct: {} };
const cites = [];
{
  let chap = 0, nb = 0, nh = 0, nc = 0, numbered = true;
  for (const b of blocks) {
    if (b.t === "cmd" && b.name === "khong-so") numbered = false;
    if (b.t === "h" && b.level === 1) { const cm = b.text.match(/^CHƯƠNG (\d+)/); if (cm) { chap = Number(cm[1]); nc = 0; } b.numbered = numbered; numbered = true; }
    if (b.t === "table" && b.cap) { nb++; b.num = nb; if (b.cap.opts.key) nums.bang[b.cap.opts.key] = nb; }
    if (b.t === "img") { nh++; b.num = nh; if (b.opts.key) nums.hinh[b.opts.key] = nh; }
    if (b.t === "eq") { nc++; b.num = `${chap}.${nc}`; if (b.opts.key) nums.ct[b.opts.key] = b.num; }
    for (const t of textsOf(b)) for (const m of t.matchAll(/\[@([^\]]+)\]/g)) for (const k of m[1].split(";").map((x) => x.trim().replace(/^@/, ""))) if (!cites.includes(k)) cites.push(k);
  }
}
function textsOf(b) {
  if (b.t === "p" || b.t === "li" || b.t === "h") return [b.text];
  if (b.t === "table") return [...b.rows.flat(), b.cap ? b.cap.text : ""];
  if (b.t === "img") return [b.cap];
  return [];
}
fs.writeFileSync(path.join(path.dirname(out), "trich-dan.json"), JSON.stringify(cites, null, 1));

// ---------- Bước 2: công thức thành chỗ giữ, sau đó công_thuc.py thay bằng OMML ----------
const eqs = [];
function eqHolder(tex, display, num) { eqs.push({ tex, display, num }); return `⟦CT${eqs.length - 1}⟧`; }

// ---------- Bước 3: chữ trong đoạn thành các TextRun ----------
function resolveRefs(s) {
  return s
    .replace(/\{\{(bang|hinh|ct):([\w-]+)\}\}/g, (_, k, key) => {
      const v = nums[k][key];
      if (v === undefined) throw new Error(`Không thấy ${k}:${key}`);
      return String(v);
    })
    .replace(/\[@([^\]]+)\]/g, (_, ks) => "[" + ks.split(";").map((x) => cites.indexOf(x.trim().replace(/^@/, "")) + 1).join(", ") + "]");
}
function runs(text, base = {}) {
  text = resolveRefs(text);
  const out = [];
  // tách theo $..$, **..**, *..*, `..`
  const re = /(\$[^$]+\$|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("$")) out.push(new TextRun({ text: eqHolder(tok.slice(1, -1), false), ...base }));
    else if (tok.startsWith("**")) out.push(new TextRun({ text: tok.slice(2, -2), ...base, bold: true }));
    else if (tok.startsWith("`")) out.push(new TextRun({ text: tok.slice(1, -1), ...base }));
    else out.push(new TextRun({ text: tok.slice(1, -1), ...base, italics: true }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

// ---------- Bước 4: dựng các phần tử Word ----------
const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" }; // 0,5 pt
const tableBorders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };

function makeTable(b) {
  const opts = b.opts || (b.cap && b.cap.opts) || {};
  const size = opts.co ? PT(Number(opts.co)) : PT(13);
  const ncol = Math.max(...b.rows.map((r) => r.length));
  let widths;
  if (opts.w) {
    const w = opts.w.split(",").map(Number);
    const sum = w.reduce((a, c) => a + c, 0);
    widths = w.map((x) => Math.round((x / sum) * TEXT_W));
  } else {
    // ước lượng theo độ dài chữ dài nhất của mỗi cột, chặn dưới để cột ngắn không bị bẻ dòng
    const len = Array.from({ length: ncol }, (_, c) => Math.max(...b.rows.map((r) => strip(r[c] || "").length)));
    const want = len.map((L) => Math.min(Math.max(L, 4), 60));
    const sum = want.reduce((a, c) => a + c, 0);
    widths = want.map((x) => Math.round((x / sum) * TEXT_W));
  }
  widths[widths.length - 1] += TEXT_W - widths.reduce((a, c) => a + c, 0);
  const align = (opts.can || "").split(",");
  const rows = b.rows.map((r, ri) => {
    const header = ri === 0;
    const lastRow = ri === b.rows.length - 1;
    return new TableRow({
      tableHeader: header,
      cantSplit: true,
      children: Array.from({ length: ncol }, (_, c) => new TableCell({
        width: { size: widths[c], type: WidthType.DXA },
        verticalAlign: VerticalAlign.CENTER,
        margins: { top: 40, bottom: 40, left: 90, right: 90 },
        children: [new Paragraph({
          alignment: header ? AlignmentType.CENTER : (align[c] === "g" ? AlignmentType.CENTER : align[c] === "p" ? AlignmentType.RIGHT : AlignmentType.LEFT),
          spacing: { before: 0, after: 0, line: LINE, lineRule: LineRuleType.AUTO },
          keepNext: lastRow,
          children: runs(r[c] || "", { size, bold: header || undefined }),
        })],
      })),
    });
  });
  const els = [new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, borders: tableBorders, rows })];
  if (b.cap) els.push(caption("Bảng", b.cap.text));
  return els;
}
function strip(s) { return s.replace(/\$[^$]*\$/g, "xxxx").replace(/[*`]/g, ""); }
function caption(label, text) {
  return new Paragraph({
    style: "Caption",
    children: [new TextRun({ text: `${label} ` }), new SequentialIdentifier(label), ...runs(`: ${text}`)],
  });
}
function makeImage(b) {
  const buf = fs.readFileSync(b.file);
  const { w, h } = pngSize(buf);
  const widthCm = Number(b.opts.rong || 15);
  const wpx = Math.round((widthCm / 2.54) * 96);
  const hpx = Math.round((wpx * h) / w);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      keepNext: true,
      spacing: { before: 60, after: 60, line: 240, lineRule: LineRuleType.AUTO },
      children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: hpx } })],
    }),
    caption("Hình", b.cap),
  ];
}
function pngSize(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }
function makeEq(b) {
  // Công thức riêng dòng: bảng 3 cột không viền, công thức ở giữa, số (chương.thứ tự) sát lề phải.
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const nb = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
  const w = [1134, TEXT_W - 2268, 1134];
  const cell = (i, children, align) => new TableCell({
    width: { size: w[i], type: WidthType.DXA }, borders: { top: none, bottom: none, left: none, right: none },
    verticalAlign: VerticalAlign.CENTER, margins: { top: 0, bottom: 0, left: 0, right: 0 },
    children: [new Paragraph({ alignment: align, keepLines: true, spacing: { before: 40, after: 40, line: LINE, lineRule: LineRuleType.AUTO }, children })],
  });
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: w, borders: nb,
    rows: [new TableRow({ cantSplit: true, children: [
      cell(0, [], AlignmentType.LEFT),
      cell(1, [new TextRun({ text: eqHolder(b.tex, true, b.num) })], AlignmentType.CENTER),
      cell(2, [new TextRun({ text: `(${b.num})` })], AlignmentType.RIGHT),
    ] })],
  });
}

for (let k = 1; k < blocks.length; k++) {
  const a = blocks[k - 1], c = blocks[k];
  // bảng có chú thích kết thúc bằng đoạn chú thích, nên chỉ công thức và bảng không chú thích mới dính vào bảng sau
  const endsWithTable = (x) => x.t === "eq" || (x.t === "table" && !x.cap);
  const startsWithTable = (x) => x.t === "eq" || x.t === "table";
  if (endsWithTable(a) && startsWithTable(c)) throw new Error("Hai bảng đứng liền nhau: " + JSON.stringify(c).slice(0, 80));
}
const sections = [];
let cur = null;
let listId = 0;
function newSection(kind) { cur = { kind, children: [] }; sections.push(cur); }
newSection("front");
let prevLi = null;
let pendingNoNum = false;
for (const b of blocks) {
  if (b.t !== "li") prevLi = null;
  if (b.t === "cmd") {
    if (b.name === "phan-chinh") { newSection("main"); continue; }
    if (b.name === "khong-so") continue;
    if (b.name === "muc-luc") { cur.children.push(new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-3" })); continue; }
    if (b.name === "danh-muc-bang") { cur.children.push(new TableOfContents("Danh mục bảng", { hyperlink: true, captionLabelIncludingNumbers: "Bảng" })); continue; }
    if (b.name === "danh-muc-hinh") { cur.children.push(new TableOfContents("Danh mục hình ảnh", { hyperlink: true, captionLabelIncludingNumbers: "Hình" })); continue; }
    if (b.name === "trang-moi") { cur.children.push(new Paragraph({ pageBreakBefore: true, spacing: { after: 0 }, children: [] })); continue; }
    if (b.name.startsWith("tieu-de-khong-muc-luc ")) {
      // tiêu đề trình bày như Heading 1 nhưng không vào mục lục (dùng cho chữ MỤC LỤC)
      cur.children.push(new Paragraph({ style: "TieuDeRieng", pageBreakBefore: cur.children.length > 0, children: [new TextRun(b.name.slice(22))] }));
      continue;
    }
    throw new Error("Lệnh lạ: " + b.name);
  }
  if (b.t === "h") {
    const lv = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][b.level - 1];
    cur.children.push(new Paragraph({ heading: lv, pageBreakBefore: b.level === 1 && cur.children.length > 0, children: runs(b.text) }));
  } else if (b.t === "p") {
    cur.children.push(new Paragraph({ children: runs(b.text) }));
  } else if (b.t === "li") {
    if (!prevLi || prevLi.kind !== b.kind) listId++;
    prevLi = b;
    cur.children.push(new Paragraph({
      numbering: { reference: b.kind === "bullet" ? "cham" : "so", level: 0, instance: listId },
      children: runs(b.text),
    }));
  } else if (b.t === "table") {
    cur.children.push(...makeTable(b));
  } else if (b.t === "img") {
    cur.children.push(...makeImage(b));
  } else if (b.t === "eq") {
    cur.children.push(makeEq(b));
  }
}
fs.writeFileSync(path.join(path.dirname(out), "cong-thuc.json"), JSON.stringify(eqs));

// ---------- Bước 5: trang bìa ----------
const bia = JSON.parse(fs.readFileSync(path.join(ROOT, "noi-dung", "bia.json"), "utf8"));
const coverChildren = bia.dong.map((d) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: d.truoc ? d.truoc * 20 : 0, after: d.sau !== undefined ? d.sau * 20 : 0, line: d.gian || 276, lineRule: LineRuleType.AUTO },
  children: [new TextRun({ text: d.chu, bold: !!d.dam, size: PT(d.co || 13), font: FONT, allCaps: !!d.hoa })],
}));

const footer = new Footer({
  children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 240 }, children: [new TextRun({ children: [PageNumber.CURRENT], size: PT(12), font: FONT })] })],
});
const page = { size: { width: 11906, height: 16838 }, margin: { top: 1417, bottom: 1417, left: 1701, right: 1134, header: 709, footer: 709 } };

const doc = new Document({
  creator: "",
  title: bia.tieuDeTep || "Báo cáo đồ án",
  features: { updateFields: true },
  styles: {
    default: {
      document: { run: { font: { ascii: FONT, hAnsi: FONT, cs: FONT, eastAsia: FONT }, size: PT(13), color: "000000" }, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: AFTER, line: LINE, lineRule: LineRuleType.AUTO } } },
      heading1: { run: { font: FONT, size: PT(13), bold: true, color: "000000", allCaps: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 240, line: LINE, lineRule: LineRuleType.AUTO }, keepNext: true, keepLines: true } },
      heading2: { run: { font: FONT, size: PT(13), bold: true, color: "000000" }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: AFTER, line: LINE, lineRule: LineRuleType.AUTO }, keepNext: true, keepLines: true } },
      heading3: { run: { font: FONT, size: PT(13), bold: true, italics: true, color: "000000" }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 120, after: AFTER, line: LINE, lineRule: LineRuleType.AUTO }, keepNext: true, keepLines: true } },
    },
    paragraphStyles: [
      { id: "Caption", name: "caption", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: PT(12), italics: true, bold: false, color: "000000" }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 60, after: AFTER, line: LINE, lineRule: LineRuleType.AUTO } } },
      { id: "TieuDeRieng", name: "Tieu de rieng", basedOn: "Normal", next: "Normal", run: { font: FONT, size: PT(13), bold: true, allCaps: true }, paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 240, line: LINE, lineRule: LineRuleType.AUTO }, keepNext: true } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal", run: { font: FONT, size: PT(13), bold: true }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 60, after: 60, line: LINE, lineRule: LineRuleType.AUTO }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: "dot" }] } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal", run: { font: FONT, size: PT(13) }, paragraph: { alignment: AlignmentType.LEFT, indent: { left: 280 }, spacing: { before: 0, after: 40, line: LINE, lineRule: LineRuleType.AUTO }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: "dot" }] } },
      { id: "TOC3", name: "toc 3", basedOn: "Normal", next: "Normal", run: { font: FONT, size: PT(13), italics: true }, paragraph: { alignment: AlignmentType.LEFT, indent: { left: 560 }, spacing: { before: 0, after: 40, line: LINE, lineRule: LineRuleType.AUTO }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: "dot" }] } },
      { id: "TableofFigures", name: "table of figures", basedOn: "Normal", next: "Normal", run: { font: FONT, size: PT(13) }, paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 0, after: 60, line: LINE, lineRule: LineRuleType.AUTO }, tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: "dot" }] } },
    ],
  },
  numbering: {
    config: [
      { reference: "cham", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } }, run: { font: { ascii: FONT, hAnsi: FONT, cs: FONT, eastAsia: FONT } } } }] },
      { reference: "so", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } }, run: { font: { ascii: FONT, hAnsi: FONT, cs: FONT, eastAsia: FONT } } } }] },
    ],
  },
  sections: [
    { properties: { page }, children: coverChildren },
    ...sections.map((s) => ({
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { ...page, pageNumbers: { start: 1, formatType: s.kind === "front" ? NumberFormat.LOWER_ROMAN : NumberFormat.DECIMAL } },
      },
      footers: { default: footer },
      children: s.children,
    })),
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log(`đã ghi ${out}: ${blocks.length} khối, ${Object.keys(nums.bang).length} bảng có khóa, ${eqs.length} công thức, ${cites.length} trích dẫn`);
});
