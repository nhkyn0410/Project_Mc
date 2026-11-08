"""Kiểm tra tài liệu Markdown theo docs/00-quy-tac-viet-tai-lieu.md.

Cách dùng:
    python tools/check_docs.py                 kiểm tra toàn bộ docs/ và CLAUDE.md
    python tools/check_docs.py <tệp|thư mục>   chỉ kiểm tra các đường dẫn chỉ định

Khi chạy không có tham số, công cụ kiểm tra thêm mục lục docs/README.md và báo
các nguồn trong docs/tai-lieu-tham-khao.bib chưa được trích ở tài liệu nào.
Mã thoát: 0 nếu không có lỗi, 1 nếu có lỗi, 2 nếu đường dẫn không tồn tại.
Cảnh báo được in ra nhưng không tính là lỗi.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INDEX = DOCS / "README.md"
BIB = DOCS / "tai-lieu-tham-khao.bib"

# Tệp chỉ theo quy tắc ngôn ngữ và ký tự, không theo quy tắc cấu trúc.
STRUCTURE_EXEMPT = {"README.md", "CLAUDE.md"}
# Thư mục con của docs/ mà mục cấp 2 phải đúng theo mẫu.
TEMPLATES = {"ly-thuyet": "mau/ly-thuyet.md", "bao-cao": "mau/bao-cao-tien-do.md"}
# Thư mục con của docs/ mà mỗi tệp phải có ít nhất một trích dẫn.
NEED_CITATION = {"ly-thuyet"}
STATUSES = ("Nháp", "Chờ duyệt", "Đã chốt")
INDEX_STATUSES = (*STATUSES, "Chưa viết")

HINT_ARROW = "viết bằng chữ, hoặc dùng danh sách đánh số cho các bước"
HINT_DASH = (
    "tách câu, hoặc dùng dấu phẩy, dấu hai chấm, ngoặc đơn; "
    "khoảng số viết 'từ 2 đến 3' hoặc '2-3'"
)
HINT_DOT = "dùng dấu phẩy, hoặc tách thành danh sách với '-'"
HINT_ELLIPSIS = "liệt kê đủ, hoặc viết 'và các mục khác'"
HINT_SYMBOL = "viết bằng chữ: Có, Không, Đạt, Chưa đạt"

DOTS = {
    "\u00b7": "chấm giữa",
    "\u2027": "chấm giữa",
    "\u2022": "chấm tròn",
    "\u2219": "chấm tròn",
    "\u25cf": "chấm tròn",
    "\u25e6": "chấm tròn",
    "\u25aa": "ô vuông nhỏ",
}
ELLIPSIS = "\u2026"
HORIZONTAL_BAR = "\u2015"  # tên Unicode không chứa chữ DASH

# Cú pháp Markdown
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
MATH_FENCE = re.compile(r"^\s*\$\$\s*$")
INLINE_CODE = re.compile(r"(`+).+?\1")
INLINE_MATH = re.compile(r"\$(?=\S)[^$\n]*?(?<=\S)\$(?!\d)")
HTML_COMMENT = re.compile(r"<!--.*?-->")
ANY_HEADING = re.compile(r"^(#{1,6})\s")
H1 = re.compile(r"^# \S")
H2 = re.compile(r"^## (\d+)\. (\S.*?)\s*$")
H3 = re.compile(r"^### (\d+)\.(\d+)\. (\S.*?)\s*$")
STATUS = re.compile(r"^Trạng thái: (.+?)\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
TABLE_CAPTION = re.compile(r"^Bảng (\d+): \S")
FIGURE_CAPTION = re.compile(r"^Hình (\d+): \S")
TABLE_REF = re.compile(r"Bảng (\d+)(?!\d)")
FIGURE_REF = re.compile(r"Hình (\d+)(?!\d)")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
URL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:")
TAG = re.compile(r"\\tag\{(\d+)\}")
CITE_GROUP = re.compile(r"\[[^\[\]]*@[^\[\]]*\]")
CITE_KEY = re.compile(r"(?<![\w.])@([A-Za-z][A-Za-z0-9_-]*)")
BIB_ENTRY = re.compile(r"^[ \t]*@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
LINK_TARGET = re.compile(r"\]\(([^)#\s]+)")
CODE_SPAN = re.compile(r"`([^`]+)`")

# Kiểm tra từng dòng
WORD = re.compile(r"\w+")
ASCII_ARROW = re.compile(r"<->|->|=>|<-")
ASCII_ELLIPSIS = re.compile(r"\.{3,}")
SPACED_HYPHEN = re.compile(r"(?<=[^\s|])[ \t]+-[ \t]+(?=[^\s|])")
# Âm tiết mở kết thúc bằng oa, oe, uy mà dấu thanh nằm trên nguyên âm sau là kiểu mới.
# Sau "qu" thì dấu luôn nằm trên nguyên âm sau, nên bỏ qua.
NEW_STYLE_TONE = re.compile(r"(?<![qQ])(?:o[àáảãạ]|o[èéẻẽẹ]|u[ỳýỷỹỵ])$", re.IGNORECASE)
HEADING_PERIOD = re.compile(r"^ {0,3}#{1,6}\s.*\.\s*$")
OTHER_LIST_MARKER = re.compile(r"^\s*[*+]\s+\S")


@dataclass
class Line:
    no: int
    raw: str
    text: str  # phần được kiểm tra: mã, công thức và chú thích HTML đã thay bằng khoảng trắng
    kind: str  # "text", "code", "math" hoặc "comment"


@dataclass
class Block:
    kind: str  # "mermaid" hoặc "math"
    start: int  # số dòng mở khối
    end: int  # số dòng đóng khối
    content: list[str]


@dataclass
class Report:
    errors: list[tuple[str, int, int, str]] = field(default_factory=list)
    warnings: list[tuple[str, int, int, str]] = field(default_factory=list)

    def error(self, where: str, line: int, col: int, message: str) -> None:
        self.errors.append((where, line, col, message))

    def warn(self, where: str, line: int, col: int, message: str) -> None:
        self.warnings.append((where, line, col, message))


def display(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def blank(match: re.Match[str]) -> str:
    return " " * (match.end() - match.start())


def parse(text: str, where: str, report: Report) -> tuple[list[Line], list[Block]]:
    """Tách tệp thành các dòng, đánh dấu dòng nào là mã, công thức hay chú thích."""
    lines: list[Line] = []
    blocks: list[Block] = []
    fence: str | None = None
    fence_info = ""
    in_math = False
    in_comment = False
    start_no = 0
    content: list[str] = []

    for no, raw in enumerate(text.splitlines(), start=1):
        if fence is not None:
            m = FENCE.match(raw)
            closing = m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence)
            if closing and not m.group(2).strip():
                if fence_info == "mermaid":
                    blocks.append(Block("mermaid", start_no, no, content))
                fence = None
            else:
                content.append(raw)
            lines.append(Line(no, raw, "", "code"))
            continue
        if in_math:
            if MATH_FENCE.match(raw):
                blocks.append(Block("math", start_no, no, content))
                in_math = False
            else:
                content.append(raw)
            lines.append(Line(no, raw, "", "math"))
            continue
        if not in_comment:
            m = FENCE.match(raw)
            if m:
                fence = m.group(1)
                info = m.group(2).strip().split()
                fence_info = info[0].lower() if info else ""
                start_no, content = no, []
                lines.append(Line(no, raw, "", "code"))
                continue
            if MATH_FENCE.match(raw):
                in_math = True
                start_no, content = no, []
                lines.append(Line(no, raw, "", "math"))
                continue

        part = raw
        if in_comment:
            end = part.find("-->")
            if end == -1:
                lines.append(Line(no, raw, "", "comment"))
                continue
            part = " " * (end + 3) + part[end + 3 :]
            in_comment = False
        part = HTML_COMMENT.sub(blank, part)
        start = part.find("<!--")
        if start != -1:
            part = part[:start] + " " * (len(part) - start)
            in_comment = True
        part = INLINE_CODE.sub(blank, part)
        if "$$" in part:
            report.error(where, no, part.find("$$") + 1, "công thức riêng dòng phải đặt giữa hai dòng chỉ chứa '$$'")
        part = INLINE_MATH.sub(blank, part)
        lines.append(Line(no, raw, part, "text"))

    if fence is not None:
        report.error(where, start_no, 1, "khối mã chưa được đóng")
    if in_math:
        report.error(where, start_no, 1, "công thức riêng dòng chưa được đóng bằng dòng '$$'")
    return lines, blocks


# ---------------------------------------------------------------- ký tự và chữ


def classify(ch: str) -> tuple[str, str] | None:
    """Trả về (tên ký tự, gợi ý) nếu ký tự bị hạn chế."""
    if ch.isascii():
        return None
    if ch == ELLIPSIS:
        return "dấu ba chấm", HINT_ELLIPSIS
    if ch in DOTS:
        return DOTS[ch], HINT_DOT
    name = unicodedata.name(ch, "")
    if "ARROW" in name:
        return "mũi tên", HINT_ARROW
    if "DASH" in name or ch == HORIZONTAL_BAR:
        return ("gạch ngắn" if name == "EN DASH" else "gạch dài"), HINT_DASH
    cp = ord(ch)
    if 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF or 0x1F000 <= cp <= 0x1FAFF:
        return "biểu tượng", HINT_SYMBOL
    return None


def old_style(pair: str) -> str:
    """Chuyển dấu thanh từ nguyên âm sau lên nguyên âm trước: oà thành òa."""
    first, second = pair
    decomposed = unicodedata.normalize("NFD", second)
    base, marks = decomposed[0], decomposed[1:]
    return unicodedata.normalize("NFC", first + marks) + base


def check_chars(where: str, line: Line, report: Report) -> None:
    text, no = line.text, line.no
    if not unicodedata.is_normalized("NFC", text):
        report.error(where, no, 1, "chữ chưa ở chuẩn Unicode NFC. Chuẩn hóa tệp về NFC")
        text = unicodedata.normalize("NFC", text)

    for col, ch in enumerate(text, start=1):
        found = classify(ch)
        if found:
            label, hint = found
            report.error(where, no, col, f"{label} '{ch}'. Gợi ý: {hint}")
    for m in ASCII_ARROW.finditer(text):
        report.error(where, no, m.start() + 1, f"mũi tên gõ tay '{m.group()}'. Gợi ý: {HINT_ARROW}")
    for m in ASCII_ELLIPSIS.finditer(text):
        report.error(where, no, m.start() + 1, f"dấu ba chấm '{m.group()}'. Gợi ý: {HINT_ELLIPSIS}")
    for m in SPACED_HYPHEN.finditer(text):
        report.error(where, no, m.start() + 1, f"gạch nối có khoảng trắng hai bên, dùng như gạch dài. Gợi ý: {HINT_DASH}")
    for word in WORD.finditer(text):
        m = NEW_STYLE_TONE.search(word.group())
        if m:
            w = word.group()
            fixed = w[: m.start()] + old_style(m.group()) + w[m.end() :]
            report.error(
                where, no, word.start() + m.start() + 1, f"dấu thanh đặt kiểu mới '{w}'. Viết theo kiểu cũ: '{fixed}'"
            )
    if HEADING_PERIOD.match(text):
        report.error(where, no, len(text.rstrip()), "tiêu đề kết thúc bằng dấu chấm. Bỏ dấu chấm cuối")
    if OTHER_LIST_MARKER.match(text):
        report.error(where, no, 1, "danh sách dùng ký hiệu khác '-'. Đổi thành '-'")


# ---------------------------------------------------------------- cấu trúc


def previous_nonempty(lines: list[Line], i: int) -> Line | None:
    for j in range(i - 1, -1, -1):
        if lines[j].raw.strip():
            return lines[j]
    return None


def next_nonempty(lines: list[Line], i: int) -> Line | None:
    for j in range(i + 1, len(lines)):
        if lines[j].raw.strip():
            return lines[j]
    return None


def h2_titles(lines: list[Line]) -> list[str]:
    titles = []
    for line in lines:
        m = H2.match(line.raw) if line.kind == "text" else None
        if m:
            titles.append(m.group(2))
    return titles


def check_structure(where: str, lines: list[Line], report: Report) -> str | None:
    """Kiểm tra tiêu đề cấp 1, dòng trạng thái, đoạn mở đầu và số thứ tự các mục."""
    status = None
    if not lines or lines[0].kind != "text" or not H1.match(lines[0].raw):
        report.error(where, 1, 1, "dòng đầu tiên phải là tiêu đề cấp 1, dạng '# Tên tài liệu'")

    status_line = next_nonempty(lines, 0) if lines else None
    m = STATUS.match(status_line.raw.strip()) if status_line and status_line.kind == "text" else None
    if m and m.group(1) in STATUSES:
        status = m.group(1)
    else:
        report.error(
            where,
            status_line.no if status_line else 1,
            1,
            "sau tiêu đề cấp 1 phải là dòng trạng thái: "
            "'Trạng thái: Nháp', 'Trạng thái: Chờ duyệt' hoặc 'Trạng thái: Đã chốt'",
        )

    headings = [(i, len(m.group(1))) for i, l in enumerate(lines) if l.kind == "text" and (m := ANY_HEADING.match(l.raw))]
    first_section = next((i for i, _ in headings if i > 0), len(lines))
    intro = [l for l in lines[1:first_section] if l.raw.strip() and l is not status_line]
    if not intro:
        report.error(where, status_line.no if status_line else 1, 1, "thiếu đoạn mở đầu từ 2 đến 3 câu sau dòng trạng thái")

    expected_h2, current_h2, expected_h3 = 1, 0, 1
    for i, level in headings:
        line = lines[i]
        if level == 1:
            if i != 0:
                report.error(where, line.no, 1, "tài liệu chỉ có một tiêu đề cấp 1, ở dòng đầu tiên")
            continue
        if level >= 4:
            report.error(where, line.no, 1, "không dùng tiêu đề cấp 4 trở xuống. Dùng danh sách có nhãn đậm")
            continue
        if level == 2:
            m2 = H2.match(line.raw)
            if not m2:
                report.error(where, line.no, 1, "tiêu đề cấp 2 phải có dạng '## 1. Tên mục'")
                continue
            number = int(m2.group(1))
            if number != expected_h2:
                report.error(where, line.no, 4, f"mục cấp 2 mang số {number}, số đúng là {expected_h2}")
            current_h2, expected_h2, expected_h3 = number, number + 1, 1
            continue
        m3 = H3.match(line.raw)
        if not m3:
            report.error(where, line.no, 1, "tiêu đề cấp 3 phải có dạng '### 1.1. Tên mục con'")
            continue
        parent, number = int(m3.group(1)), int(m3.group(2))
        if current_h2 == 0:
            report.error(where, line.no, 1, "mục cấp 3 phải nằm trong một mục cấp 2")
        elif parent != current_h2 or number != expected_h3:
            report.error(where, line.no, 5, f"mục con mang số {parent}.{number}, số đúng là {current_h2}.{expected_h3}")
        expected_h3 = number + 1

    for pos, (i, level) in enumerate(headings):
        if level == 1:
            continue
        nxt, nxt_level = headings[pos + 1] if pos + 1 < len(headings) else (len(lines), 0)
        has_content = any(l.raw.strip() for l in lines[i + 1 : nxt])
        if not has_content and nxt_level <= level:
            report.error(where, lines[i].no, 1, "mục trống. Viết nội dung, hoặc ghi 'Chưa viết' kèm lý do")
    return status


def check_captions_and_refs(
    where: str,
    lines: list[Line],
    report: Report,
    label: str,
    caption_re: re.Pattern[str],
    ref_re: re.Pattern[str],
    defined: dict[int, int],
    used: set[int],
) -> None:
    caption_lines = set()
    for line in lines:
        if line.kind == "text" and caption_re.match(line.raw.strip()):
            caption_lines.add(line.no)
            if line.no not in used:
                report.error(where, line.no, 1, f"dòng tên {label.lower()} không đi kèm {label.lower()} nào")

    mentioned: dict[int, tuple[int, int]] = {}
    for line in lines:
        if line.kind != "text" or line.no in caption_lines:
            continue
        for m in ref_re.finditer(line.text):
            mentioned.setdefault(int(m.group(1)), (line.no, m.start() + 1))

    for n, no in defined.items():
        if n not in mentioned:
            report.error(where, no, 1, f"{label} {n} chưa được nhắc tới trong lời văn")
    for n, (no, col) in mentioned.items():
        if n not in defined:
            report.warn(where, no, col, f"nhắc tới {label} {n} nhưng tài liệu không có {label.lower()} này")


def check_tables(where: str, lines: list[Line], report: Report) -> None:
    defined: dict[int, int] = {}
    used: set[int] = set()
    expected = 1
    i = 0
    while i < len(lines) - 1:
        line, nxt = lines[i], lines[i + 1]
        is_table = line.kind == "text" and TABLE_ROW.match(line.raw) and nxt.kind == "text" and TABLE_SEP.match(nxt.raw)
        if not is_table:
            i += 1
            continue
        cap = previous_nonempty(lines, i)
        m = TABLE_CAPTION.match(cap.raw.strip()) if cap is not None and cap.kind == "text" else None
        if m is None:
            report.error(where, line.no, 1, "bảng thiếu tên. Thêm dòng 'Bảng N: Tên bảng' phía trên, cách bảng một dòng trống")
        else:
            n = int(m.group(1))
            if n != expected:
                report.error(where, cap.no, 1, f"bảng mang số {n}, số đúng là {expected}")
            defined[n], expected = cap.no, n + 1
            used.add(cap.no)
        i += 2
        while i < len(lines) and lines[i].kind == "text" and TABLE_ROW.match(lines[i].raw):
            i += 1
    check_captions_and_refs(where, lines, report, "Bảng", TABLE_CAPTION, TABLE_REF, defined, used)


def check_figures(where: str, path: Path, lines: list[Line], blocks: list[Block], report: Report) -> None:
    index_of = {line.no: i for i, line in enumerate(lines)}
    anchors = []
    for i, line in enumerate(lines):
        if line.kind != "text" or not IMAGE.search(line.text):
            continue
        anchors.append(i)
        for m in IMAGE.finditer(line.text):
            target = unquote(m.group(1).split("#")[0].split("?")[0])
            if target and not URL_SCHEME.match(target) and not (path.parent / target).exists():
                report.error(where, line.no, m.start() + 1, f"không tìm thấy ảnh '{target}'")
    anchors += [index_of[b.end] for b in blocks if b.kind == "mermaid"]

    defined: dict[int, int] = {}
    used: set[int] = set()
    expected = 1
    for i in sorted(anchors):
        cap = next_nonempty(lines, i)
        m = FIGURE_CAPTION.match(cap.raw.strip()) if cap is not None and cap.kind == "text" else None
        if m is None:
            report.error(where, lines[i].no, 1, "hình thiếu tên. Thêm dòng 'Hình N: Tên hình' phía dưới, cách hình một dòng trống")
            continue
        n = int(m.group(1))
        if n != expected:
            report.error(where, cap.no, 1, f"hình mang số {n}, số đúng là {expected}")
        defined[n], expected = cap.no, n + 1
        used.add(cap.no)
    check_captions_and_refs(where, lines, report, "Hình", FIGURE_CAPTION, FIGURE_REF, defined, used)


def check_equations(where: str, blocks: list[Block], report: Report) -> None:
    expected = 1
    for block in blocks:
        if block.kind != "math":
            continue
        tags = TAG.findall("\n".join(block.content))
        if not tags:
            report.error(where, block.start, 1, "công thức riêng dòng thiếu số. Thêm \\tag{N} vào cuối công thức")
            continue
        for tag in tags:
            n = int(tag)
            if n != expected:
                report.error(where, block.start, 1, f"công thức mang số ({n}), số đúng là ({expected})")
            expected = n + 1


def collect_citations(lines: list[Line]) -> list[tuple[int, int, str]]:
    found = []
    for line in lines:
        if line.kind != "text":
            continue
        for group in CITE_GROUP.finditer(line.text):
            for key in CITE_KEY.finditer(group.group()):
                found.append((line.no, group.start() + key.start() + 1, key.group(1)))
    return found


def docs_subfolder(path: Path) -> str | None:
    """Tên thư mục con trực tiếp của docs/ chứa tệp, nếu có."""
    try:
        rel = path.resolve().relative_to(DOCS.resolve())
    except ValueError:
        return None
    return rel.parts[0] if len(rel.parts) > 1 else None


_template_titles: dict[str, list[str] | None] = {}


def template_titles(name: str) -> list[str] | None:
    if name not in _template_titles:
        path = DOCS / name
        if path.exists():
            lines, _ = parse(path.read_text(encoding="utf-8"), display(path), Report())
            _template_titles[name] = h2_titles(lines)
        else:
            _template_titles[name] = None
    return _template_titles[name]


# ---------------------------------------------------------------- từng tệp và toàn bộ


def check_file(path: Path, report: Report, bib_keys: set[str] | None) -> tuple[str | None, list[tuple[int, int, str]]]:
    where = display(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.error(where, 1, 1, "tệp không phải UTF-8. Lưu lại tệp bằng UTF-8")
        return None, []

    lines, blocks = parse(text, where, report)
    for line in lines:
        if line.kind == "text":
            check_chars(where, line, report)

    citations = collect_citations(lines)
    for no, col, key in citations:
        if bib_keys is None:
            report.error(where, no, col, f"trích '@{key}' nhưng chưa có tệp docs/tai-lieu-tham-khao.bib")
        elif key not in bib_keys:
            report.error(where, no, col, f"khóa trích dẫn '@{key}' không có trong docs/tai-lieu-tham-khao.bib")

    if path.name in STRUCTURE_EXEMPT:
        return None, citations

    status = check_structure(where, lines, report)
    check_tables(where, lines, report)
    check_figures(where, path, lines, blocks, report)
    check_equations(where, blocks, report)

    sub = docs_subfolder(path)
    if sub in TEMPLATES:
        expected = template_titles(TEMPLATES[sub])
        if expected is None:
            report.error(where, 1, 1, f"không tìm thấy mẫu docs/{TEMPLATES[sub]}")
        elif h2_titles(lines) != expected:
            report.error(
                where, 1, 1, f"các mục cấp 2 phải đúng tên và thứ tự trong mẫu docs/{TEMPLATES[sub]}: {', '.join(expected)}"
            )
    if sub in NEED_CITATION and not citations:
        report.error(where, 1, 1, "tài liệu lý thuyết phải có ít nhất một trích dẫn tới nguồn gốc của kỹ thuật")
    return status, citations


def load_bib(report: Report) -> tuple[set[str] | None, dict[str, int]]:
    if not BIB.exists():
        return None, {}
    text = BIB.read_text(encoding="utf-8")
    keys: dict[str, int] = {}
    for m in BIB_ENTRY.finditer(text):
        kind, key = m.group(1).lower(), m.group(2)
        if kind in {"comment", "string", "preamble"}:
            continue
        no = text.count("\n", 0, m.start()) + 1
        if key in keys:
            report.error(display(BIB), no, 1, f"khóa '{key}' bị trùng với mục ở dòng {keys[key]}")
        else:
            keys[key] = no
    return set(keys), keys


def check_index(report: Report, statuses: dict[Path, str]) -> None:
    """So mục lục docs/README.md với các tệp thật."""
    if not INDEX.exists():
        report.error(display(DOCS), 1, 1, "thiếu mục lục docs/README.md")
        return
    where = display(INDEX)
    listed: dict[str, tuple[int, str]] = {}
    for no, raw in enumerate(INDEX.read_text(encoding="utf-8").splitlines(), start=1):
        row = raw.strip()
        if not row.startswith("|") or TABLE_SEP.match(row):
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = LINK_TARGET.search(cells[0]) or CODE_SPAN.search(cells[0])
        if not m or not m.group(1).endswith(".md"):
            continue
        target = m.group(1)
        if target in listed:
            report.error(where, no, 1, f"'{target}' xuất hiện hai lần trong mục lục")
        listed[target] = (no, cells[2])

    for path in sorted(DOCS.rglob("*.md")):
        if path.resolve() == INDEX.resolve():
            continue
        if path.relative_to(DOCS).as_posix() not in listed:
            report.error(display(path), 1, 1, "tài liệu chưa có trong mục lục docs/README.md")

    for target, (no, status) in listed.items():
        path = DOCS / target
        if status not in INDEX_STATUSES:
            report.error(where, no, 1, f"trạng thái '{status}' không hợp lệ, chỉ dùng: {', '.join(INDEX_STATUSES)}")
        elif status == "Chưa viết":
            if path.exists():
                report.error(where, no, 1, f"tệp '{target}' đã có, đổi trạng thái trong mục lục cho khớp tài liệu")
        elif not path.exists():
            report.error(where, no, 1, f"mục lục ghi '{target}' nhưng tệp không tồn tại")
        else:
            actual = statuses.get(path.resolve())
            if actual is not None and actual != status:
                report.error(where, no, 1, f"mục lục ghi trạng thái '{status}', tài liệu ghi '{actual}'")


def iter_files(targets: list[Path]):
    for target in targets:
        if target.is_dir():
            yield from sorted(target.rglob("*.md"))
        elif target.is_file():
            yield target


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    full = not argv
    if full:
        targets = [t for t in (DOCS, ROOT / "CLAUDE.md") if t.exists()]
    else:
        targets = [Path(arg) for arg in argv]
        missing = [t for t in targets if not t.exists()]
        if missing:
            for t in missing:
                print(f"Không tìm thấy: {t}", file=sys.stderr)
            return 2

    report = Report()
    bib_keys, bib_lines = load_bib(report)
    statuses: dict[Path, str] = {}
    cited: set[str] = set()
    checked = 0
    for path in iter_files(targets):
        checked += 1
        status, citations = check_file(path, report, bib_keys)
        if status:
            statuses[path.resolve()] = status
        cited.update(key for _, _, key in citations)

    if full:
        if bib_keys is None:
            report.error(display(DOCS), 1, 1, "thiếu tệp docs/tai-lieu-tham-khao.bib")
        check_index(report, statuses)
        for key, no in bib_lines.items():
            if key not in cited:
                report.warn(display(BIB), no, 1, f"nguồn '{key}' chưa được trích ở tài liệu nào")

    for where, no, col, message in sorted(report.errors):
        print(f"{where}:{no}:{col}: {message}")
    for where, no, col, message in sorted(report.warnings):
        print(f"{where}:{no}:{col}: cảnh báo: {message}")

    summary = f"{checked} tệp, {len(report.errors)} lỗi, {len(report.warnings)} cảnh báo."
    if report.errors:
        print(f"\n{summary}")
        return 1
    print(f"Không có lỗi. {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
