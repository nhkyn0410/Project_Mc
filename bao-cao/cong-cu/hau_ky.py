"""Việc sau khi Word lưu: bật updateFields để Word cập nhật trường khi mở tệp, bỏ mục thư mục trong tệp zip,
và kiểm tra tài liệu không còn gạch dài, mũi tên hay chỗ giữ công thức.
Dùng: python hau_ky.py <tệp .docx>"""
import re, sys, zipfile, shutil

CAM = ["—", "–", "→", "←", "↔", "⇒", "⇔", "➜", "=>", "->", "…"]

def main(docx):
    tmp = docx + ".tmp"
    with zipfile.ZipFile(docx) as zin:
        names = [i for i in zin.infolist() if not i.filename.endswith("/")]
        settings = zin.read("word/settings.xml").decode("utf-8")
        if "w:updateFields" not in settings:
            settings = re.sub(r"(<w:settings[^>]*>)", r'\1<w:updateFields w:val="true"/>', settings, count=1)
        report = []
        for part in [n.filename for n in names if n.filename.startswith("word/") and n.filename.endswith(".xml")]:
            xml = zin.read(part).decode("utf-8")
            text = "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", xml))
            for c in CAM:
                k = text.count(c)
                if k:
                    i = text.find(c)
                    report.append(f"{part}: {k} lần '{c}', ví dụ: ...{text[max(0, i - 40):i + 40]}...")
            # trong công thức chỉ cấm gạch và mũi tên; dấu ba chấm của dãy số như z1, ..., zT là ký hiệu toán
            math = "".join(re.findall(r"<m:t(?: [^>]*)?>([^<]*)</m:t>", xml))
            for c in [x for x in CAM if x != "…"]:
                k = math.count(c)
                if k:
                    report.append(f"{part}: {k} lần '{c}' trong công thức")
            if "⟦CT" in xml:
                report.append(f"{part}: còn chỗ giữ công thức")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in names:
                data = settings.encode("utf-8") if item.filename == "word/settings.xml" else zin.read(item.filename)
                zout.writestr(item, data)
    shutil.move(tmp, docx)
    print("updateFields: bật")
    print("\n".join(report) if report else "không còn gạch dài, mũi tên hay chỗ giữ công thức")

if __name__ == "__main__":
    main(sys.argv[1])
