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
    tex = tex.replace("{,}", ",")
    # latex2mathml không hiểu \arg, viết arg max thành chữ đứng
    tex = tex.replace(r"\arg\max", r"\mathrm{arg}\,\mathrm{max}")
    # báo cáo không dùng ký tự mũi tên, nên trạng thái chiều xuôi và chiều ngược của BiLSTM
    # viết bằng chỉ số trên f và b thay cho mũi tên phía trên
    nhom = r"\{((?:[^{}]|\{[^{}]*\})*)\}"
    tex = re.sub(r"\\overrightarrow" + nhom, lambda m: "{" + m.group(1) + "}^{\\mathrm{f}}", tex)
    tex = re.sub(r"\\overleftarrow" + nhom, lambda m: "{" + m.group(1) + "}^{\\mathrm{b}}", tex)
    # latex2mathml để nguyên dấu & của aligned, đổi sang array hai cột căn phải và căn trái
    tex = re.sub(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", lambda m: r"\begin{array}{rl}" + m.group(1) + r"\end{array}", tex, flags=re.S)
    return tex.strip()

# MML2OMML.XSL bỏ mspace, nên khoảng trắng của LaTeX được thay bằng ký tự khoảng trắng Unicode
def space_char(width_em):
    if width_em <= 0.2:
        return "\u2009"  # \, khoảng hẹp
    if width_em <= 0.3:
        return "\u2005"  # \; và \: khoảng vừa
    return "\u2003" * max(1, round(width_em))  # \quad, \qquad

FUNCS = "max|min|lim|log|exp|sup|inf|det|arg"

def to_omml(tex):
    mml = l2m.convert(prepare(tex))
    mml = re.sub(r'<mspace width="([\d.]+)em"\s*/>', lambda m: "<mtext>" + space_char(float(m.group(1))) + "</mtext>", mml)
    root = etree.fromstring(mml.encode("utf-8"))
    res = transform(root)
    s = etree.tostring(res.getroot(), encoding="unicode")
    # bỏ khai báo namespace lặp lại trong từng công thức, gốc tài liệu đã khai báo
    s = re.sub(r'\s+xmlns:(m|w)="[^"]*"', "", s)
    # tên hàm như max, min viết chữ đứng
    s = re.sub(r"<m:r><m:t>(" + FUNCS + r")</m:t></m:r>", r'<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>\1</m:t></m:r>', s)
    # dấu nhân chấm dùng ký tự toán tử chấm, không dùng chấm giữa của văn bản
    s = s.replace("·", "⋅")
    return s

JC = {"center": "center", "right": "right", "end": "right"}

def sua_cong_thuc_mot_minh(xml):
    """Word coi công thức đứng một mình trong đoạn là công thức riêng dòng và căn giữa.
    Bọc công thức đó trong m:oMathPara với căn lề theo đoạn, để ô bảng căn trái vẫn căn trái."""
    count = 0
    def fix(pm):
        nonlocal count
        p = pm.group(0)
        if "<m:oMathPara" in p or p.count("<m:oMath>") != 1:
            return p
        start, end = p.index("<m:oMath>"), p.index("</m:oMath>") + len("</m:oMath>")
        ngoai = p[:start] + p[end:]
        if "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", ngoai)).strip():
            return p
        jc = re.search(r'<w:pPr>.*?<w:jc w:val="(\w+)"/>.*?</w:pPr>', p, re.S)
        val = JC.get(jc.group(1), "left") if jc else "left"
        count += 1
        return p[:start] + f'<m:oMathPara><m:oMathParaPr><m:jc m:val="{val}"/></m:oMathParaPr>' + p[start:end] + "</m:oMathPara>" + p[end:]
    xml = re.sub(r"<w:p[ >](?:(?!</w:p>).)*</w:p>", fix, xml, flags=re.S)
    return xml, count

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
                # giữ cỡ chữ của run gốc, ví dụ 12 pt trong bảng, vì m:r không tự nhận cỡ của run
                sz = re.search(r'<w:sz w:val="(\d+)"/>', m.group(0))
                if sz:
                    rpr = f'<w:rPr><w:sz w:val="{sz.group(1)}"/><w:szCs w:val="{sz.group(1)}"/></w:rPr>'
                    om = re.sub(r"(<m:r>(?:<m:rPr>.*?</m:rPr>)?)", lambda k: k.group(1) + rpr, om)
                if not eqs[i].get("display"):
                    return om
                # công thức riêng dòng nằm một mình trong ô giữa của bảng không viền, số đã nằm ở ô bên phải
                return "<m:oMathPara>" + om + "</m:oMathPara>"
            except Exception as e:  # công thức lỗi: để lại chữ LaTeX để sửa
                bad.append((i, eqs[i]["tex"], str(e)[:80]))
                return m.group(0)
        run_re = re.compile(r"<w:r>(?:(?!</w:r>).)*?⟦CT(\d+)⟧(?:(?!</w:r>).)*?</w:r>", re.S)
        xml, n = run_re.subn(repl, xml)
        xml, lone = sua_cong_thuc_mot_minh(xml)
        print(f"công thức nằm một mình trong đoạn, đặt căn lề theo đoạn: {lone}")
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
