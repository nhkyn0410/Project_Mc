"""Thay các chỗ giữ công thức trong tệp .docx bằng công thức của Word (OMML).
LaTeX chuyển sang MathML bằng latex2mathml, rồi sang OMML bằng MML2OMML.XSL của Office.
Dùng: python cong_thuc.py <tệp .docx> <cong-thuc.json>"""
import json, re, sys, zipfile, shutil, os
import latex2mathml.converter as l2m
from lxml import etree

XSL = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
transform = etree.XSLT(etree.parse(XSL))
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

def prepare(tex):
    tex = re.sub(r"\\tag\{[^}]*\}", "", tex)
    tex = tex.replace(r"\,", r"\;").replace("{,}", ",")
    # latex2mathml để nguyên dấu & của aligned, đổi sang array hai cột căn phải và căn trái
    tex = re.sub(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", lambda m: r"\begin{array}{rl}" + m.group(1) + r"\end{array}", tex, flags=re.S)
    return tex.strip()

def to_omml(tex):
    mml = l2m.convert(prepare(tex))
    root = etree.fromstring(mml.encode("utf-8"))
    res = transform(root)
    s = etree.tostring(res.getroot(), encoding="unicode")
    # bỏ khai báo namespace lặp lại trong từng công thức, gốc tài liệu đã khai báo
    s = re.sub(r'\s+xmlns:(m|w)="[^"]*"', "", s)
    return s

def main(docx, eq_json):
    eqs = json.load(open(eq_json, encoding="utf-8"))
    tmp = docx + ".tmp"
    with zipfile.ZipFile(docx) as zin:
        xml = zin.read("word/document.xml").decode("utf-8")
        if 'xmlns:m="' not in xml[:3000]:
            xml = xml.replace("<w:document ", f'<w:document xmlns:m="{M_NS}" ', 1)
        bad = []
        def repl(m):
            i = int(m.group(1))
            try:
                om = to_omml(eqs[i]["tex"])
                if not eqs[i].get("display"):
                    return om
                # công thức riêng dòng nằm một mình trong ô giữa của bảng không viền, số đã nằm ở ô bên phải
                return "<m:oMathPara>" + om + "</m:oMathPara>"
            except Exception as e:  # công thức lỗi: để lại chữ LaTeX để sửa
                bad.append((i, eqs[i]["tex"], str(e)[:80]))
                return m.group(0)
        run_re = re.compile(r"<w:r>(?:(?!</w:r>).)*?⟦CT(\d+)⟧(?:(?!</w:r>).)*?</w:r>", re.S)
        xml, n = run_re.subn(repl, xml)
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = xml.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
                zout.writestr(item, data)
    shutil.move(tmp, docx)
    left = xml.count("⟦CT")
    print(f"đã thay {n - len(bad)} công thức, lỗi {len(bad)}, còn chỗ giữ {left}")
    for b in bad:
        print("  lỗi:", b)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
