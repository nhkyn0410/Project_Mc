"""Chuyển bảy tài liệu docs/ly-thuyet thành Chương 2 của báo cáo.
Mỗi tài liệu thành một mục 2.k. Các mục con của phần Nguyên lý được đưa lên cùng cấp với Bài toán, Ví dụ,
nên chương chỉ dùng ba cấp tiêu đề. Công thức, bảng và dẫn chiếu được đánh số lại theo báo cáo.
Dùng: python chuyen_ly_thuyet.py <thư mục docs> <tệp ra>"""
import re, sys, os

DOCS, OUT = sys.argv[1], sys.argv[2]
FILES = ["01-nhan-dang-chu-viet-tay-tu-anh.md", "02-tien-xu-ly-anh.md", "03-cnn-2d.md", "04-lstm-va-bilstm.md",
         "05-ctc.md", "06-beam-search-va-n-gram.md", "07-luong-tu-hoa-mo-hinh.md"]

# Dẫn chiếu tới tài liệu ngoài phần lý thuyết, đổi sang mục của báo cáo
EXT = {
    ("01-mo-ta-de-tai.md", "7.3"): "mục 3.2.4", ("01-mo-ta-de-tai.md", ""): "Chương 1",
    ("02-yeu-cau-va-danh-gia.md", "1"): "mục 1.2", ("02-yeu-cau-va-danh-gia.md", "2.5"): "mục 1.5.3",
    ("02-yeu-cau-va-danh-gia.md", ""): "mục 1.5",
    ("03-du-lieu.md", ""): "mục 3.1", ("03-du-lieu.md", "3"): "mục 3.1.3", ("03-du-lieu.md", "3.2"): "mục 3.1.3",
    ("03-du-lieu.md", "3.3"): "mục 3.1.3", ("03-du-lieu.md", "3.4"): "mục 3.1.3", ("03-du-lieu.md", "4"): "mục 3.1.4",
    ("04-thiet-ke-he-thong.md", ""): "mục 3.2", ("04-thiet-ke-he-thong.md", "3"): "mục 3.2.3",
    ("04-thiet-ke-he-thong.md", "4"): "mục 3.2.5", ("04-thiet-ke-he-thong.md", "5"): "mục 3.2.6",
    ("05-ke-hoach-thi-nghiem.md", ""): "Chương 4",
    ("06-trien-khai-android.md", ""): "Chương 5", ("06-trien-khai-android.md", "1"): "mục 5.1",
    ("07-nhat-ky-thi-nghiem.md", ""): "Chương 4", ("07-nhat-ky-thi-nghiem.md", "5"): "mục 4.3",
    ("07-nhat-ky-thi-nghiem.md", "6"): "mục 4.7", ("07-nhat-ky-thi-nghiem.md", "10.5"): "mục 4.4",
    ("07-nhat-ky-thi-nghiem.md", "11.3"): "mục 4.3", ("07-nhat-ky-thi-nghiem.md", "11.2"): "mục 4.5",
}

def sections_of(text):
    """Trả về danh sách (số mục cũ, tiêu đề) theo thứ tự, và bảng đổi số mục cũ sang số mới."""
    heads = re.findall(r"^(##+) (\d+(?:\.\d+)?)\. (.+)$", text, re.M)
    return heads

def build_map(k, text):
    heads = sections_of(text)
    mapping, order, n = {}, [], 0
    has_sub = {h[1].split(".")[0] for h in heads if "." in h[1]}
    for lv, num, title in heads:
        if lv == "##" and num in has_sub:
            mapping[num] = None  # phần chỉ chứa mục con, bỏ tiêu đề
            continue
        n += 1
        mapping[num] = f"2.{k}.{n}"
        order.append((num, title))
    # mục cha bị bỏ trỏ tới mục con đầu tiên
    for num, v in list(mapping.items()):
        if v is None:
            first = next(m for m in mapping if m.startswith(num + ".") and mapping[m])
            mapping[num] = mapping[first]
    return mapping

maps = {}
texts = {}
for k, f in enumerate(FILES, 1):
    t = open(os.path.join(DOCS, f), encoding="utf-8").read().replace("\r\n", "\n")
    texts[f] = t
    maps[f] = build_map(k, t)

def ref_ext(doc, sec):
    if doc in maps:
        if not sec:
            return "mục 2.%d" % (FILES.index(doc) + 1)
        return "mục " + maps[doc][sec]
    key = (doc, sec)
    if key not in EXT:
        key = (doc, sec.split(".")[0]) if (doc, sec.split(".")[0]) in EXT else (doc, "")
    if key not in EXT:
        raise KeyError((doc, sec))
    return EXT[key]

out = ["# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", "",
       "Chương này trình bày các kiến thức nền mà hệ thống dựa vào, theo thứ tự của luồng xử lý: bài toán nhận dạng dòng chữ viết tay dạng ảnh, cách vẽ nét thành ảnh, mạng tích chập hai chiều, mạng hồi quy LSTM và BiLSTM, hàm mất mát CTC, giải mã bằng beam search kết hợp mô hình ngôn ngữ n-gram, và lượng tử hóa mô hình. Mỗi mục nêu bài toán, nguyên lý, một ví dụ tính tay và cách áp dụng trong đề tài.", ""]
report = []
for k, f in enumerate(FILES, 1):
    t = texts[f]
    m = maps[f]
    lines = t.split("\n")
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:])
    # bỏ dòng trạng thái và đoạn giới thiệu tài liệu
    body = re.sub(r"^\s*Trạng thái:[^\n]*\n", "", body)
    paras = body.strip("\n").split("\n\n")
    if paras and paras[0].startswith("Tài liệu này"):
        report.append((f, "bỏ đoạn mở đầu: " + paras[0][:90]))
        paras = paras[1:]
    body = "\n\n".join(paras)
    # công thức riêng dòng nhiều dòng thành một dòng có khóa
    def eq(mm):
        tex = " ".join(x.strip() for x in mm.group(1).strip().split("\n"))
        tag = re.search(r"\\tag\{(\d+)\}", tex)
        tex = re.sub(r"\s*\\tag\{\d+\}", "", tex).strip()
        key = f"d{k}-{tag.group(1)}" if tag else None
        return f"$${tex}$$" + (f" {{#ct:{key}}}" if key else "")
    body = re.sub(r"\$\$\n?(.*?)\n?\$\$", eq, body, flags=re.S)
    # công thức (n), kể cả dãy (n) và (m)
    def eqref(mm):
        return re.sub(r"\((\d+)\)", lambda x: "({{ct:d%d-%s}})" % (k, x.group(1)), mm.group(0))
    body = re.sub(r"[Cc]ông thức \(\d+\)(?:(?:,| và| hoặc| đến| tới)+ \(\d+\))*", eqref, body)
    body = re.sub(r"(?<=[Tt]heo )\((\d+)\)", lambda x: "({{ct:d%d-%s}})" % (k, x.group(1)), body)
    # bảng: chú thích chuyển xuống dưới bảng
    def table(mm):
        n, cap, tab = mm.group(1), mm.group(2), mm.group(3)
        return f"{tab.rstrip()}\n\nBảng: {cap} {{#bang:d{k}-b{n}}}\n"
    body = re.sub(r"^Bảng (\d+): (.+)\n\n((?:\|.*\n)+)", table, body, flags=re.M)
    body = re.sub(r"Bảng (\d+)(?!\d)", lambda x: "Bảng {{bang:d%d-b%s}}" % (k, x.group(1)), body)
    # dẫn chiếu sang tài liệu khác
    def xref(mm):
        doc, sec = mm.group(1), mm.group(2) or ""
        return ref_ext(os.path.basename(doc), sec)
    body = re.sub(r"`(?:ly-thuyet/)?([0-9a-z-]+\.md)`(?:, mục (\d+(?:\.\d+)?))?", xref, body)
    # dẫn chiếu trong cùng tài liệu
    body = re.sub(r"(?<![\w.])mục (\d+(?:\.\d+)?)(?= của tài liệu này)", lambda x: "mục " + m[x.group(1)], body)
    body = body.replace(" của tài liệu này", "")
    body = re.sub(r"(?<![\w.`])mục (\d\.\d)(?![\d.])", lambda x: "mục " + m.get(x.group(1), x.group(1)), body)
    body = re.sub(r"(?<![\w.`])mục (\d)(?![\d.])", lambda x: "mục " + m.get(x.group(1), x.group(1)), body)
    # tiêu đề: bỏ tiêu đề phần chỉ chứa mục con, đánh số lại
    def head(mm):
        num, tt = mm.group(2), mm.group(3)
        lv = mm.group(1)
        if lv == "##" and any(x.startswith(num + ".") for x in m if x != num):
            return ""
        return f"### {m[num]}. {tt}"
    body = re.sub(r"^(##+) (\d+(?:\.\d+)?)\. (.+)$", head, body, flags=re.M)
    body = re.sub(r"\n{3,}", "\n\n", body)
    out += [f"## 2.{k}. {title}", "", body.strip(), ""]

text = "\n".join(out) + "\n"
open(OUT, "w", encoding="utf-8").write(text)
for r in report:
    print(*r)
left = re.findall(r"`[^`]*\.md`|tài liệu này|docs/", text)
print("còn sót:", left[:10])
print("số công thức có khóa:", len(re.findall(r"\{#ct:", text)), "số bảng:", len(re.findall(r"\{#bang:", text)))
