# Tạo phần Tài liệu tham khảo của báo cáo theo kiểu IEEE từ docs/tai-lieu-tham-khao.bib.
# Thứ tự theo lần trích đầu tiên, lấy từ trich-dan.json do xay-dung.js ghi ra.
# Cách dùng: python tai_lieu.py <tệp .bib> <trich-dan.json> <tệp ra .md>
# Khoảng trang dùng gạch nối thường, không dùng gạch ngắn.
import json
import re
import sys
import unicodedata

DAU = {"'": "\u0301", '"': "\u0308", "`": "\u0300", "^": "\u0302", "~": "\u0303"}


def bo_latex(s):
    # {\'a} hoặc \'a thành chữ có dấu, rồi bỏ ngoặc nhọn
    s = re.sub(r"\{\\(['\"`^~])\{?(\w)\}?\}", lambda m: m.group(2) + DAU[m.group(1)], s)
    s = re.sub(r"\\(['\"`^~])\{?(\w)\}?", lambda m: m.group(2) + DAU[m.group(1)], s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", " ", s).strip()
    return unicodedata.normalize("NFC", s)


def doc_bib(path):
    text = open(path, encoding="utf-8").read()
    muc = {}
    for m in re.finditer(r"@(\w+)\{([\w-]+),(.*?)\n\}", text, flags=re.S):
        loai, khoa, than = m.group(1).lower(), m.group(2), m.group(3)
        truong = {}
        for t in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*$", than, flags=re.M):
            truong[t.group(1).lower()] = t.group(2)
        truong["_loai"] = loai
        muc[khoa] = truong
    return muc


def ten_mot_nguoi(a):
    a = a.strip()
    if a.startswith("{") and a.endswith("}"):
        return bo_latex(a)  # tên tổ chức
    a = bo_latex(a)
    if "," not in a:
        return a
    ho, ten = [x.strip() for x in a.split(",", 1)]
    viet_tat = []
    for tu in ten.split():
        if tu.endswith(".") and len(tu) <= 3:
            viet_tat.append(tu)
        else:
            viet_tat.append("-".join(p[0] + "." for p in tu.split("-")))
    return " ".join(viet_tat + [ho])


def tac_gia(s):
    ds = [x for x in re.split(r"\s+and\s+", s.strip())]
    con_nua = ds[-1].strip() == "others"
    ds = [ten_mot_nguoi(x) for x in ds if x.strip() != "others"]
    if con_nua or len(ds) > 6:
        return ds[0] + " et al."
    if len(ds) == 1:
        return ds[0]
    return ", ".join(ds[:-1]) + " và " + ds[-1]


def ngay(s):
    y, m, d = s.split("-")
    return f"{d}/{m}/{y}"


def trang(s):
    return re.sub(r"-{1,3}", "-", s)


def mot_muc(t):
    tg = tac_gia(t["author"])
    tieu_de = bo_latex(t["title"])
    # tên kết thúc bằng dấu hỏi thì không thêm dấu phẩy sau tên
    phay = "" if tieu_de.endswith(("?", "!")) else ","
    loai = t["_loai"]
    nam = t["year"]
    phan = []
    if loai == "article":
        s = f"{tg}, “{tieu_de}{phay}” *{bo_latex(t['journal'])}*"
        if "volume" in t:
            s += f", vol. {t['volume']}"
        if "number" in t:
            s += f", no. {t['number']}"
        if "pages" in t:
            s += f", pp. {trang(t['pages'])}"
        s += f", {nam}."
        phan.append(s)
    elif loai == "inproceedings":
        s = f"{tg}, “{tieu_de}{phay}” in *{bo_latex(t['booktitle'])}*, {nam}"
        if "volume" in t:
            s += f", vol. {t['volume']}"
        if "pages" in t:
            s += f", pp. {trang(t['pages'])}"
        s += "."
        phan.append(s)
    elif "eprint" in t:
        phan.append(f"{tg}, “{tieu_de}{phay}” arXiv:{t['eprint']}, {nam}.")
    else:
        phan.append(f"{tg}, “{tieu_de}{phay}” {nam}.")
        s = f"[Trực tuyến]. Địa chỉ: {t['url']}"
        if "urldate" in t:
            s += f". Truy cập ngày {ngay(t['urldate'])}"
        phan.append(s + ".")
    if "doi" in t:
        phan.append(f"doi: {t['doi']}.")
    return " ".join(phan)


def main():
    bib, thu_tu, ra = sys.argv[1], sys.argv[2], sys.argv[3]
    muc = doc_bib(bib)
    khoa = json.load(open(thu_tu, encoding="utf-8"))
    thieu = [k for k in khoa if k not in muc]
    if thieu:
        sys.exit("Không có trong .bib: " + ", ".join(thieu))
    dong = ["@@khong-so", "# TÀI LIỆU THAM KHẢO", ""]
    for i, k in enumerate(khoa, 1):
        dong.append(f"&& [{i}] {mot_muc(muc[k])}")
        dong.append("")
    open(ra, "w", encoding="utf-8", newline="\n").write("\n".join(dong))
    print(f"đã ghi {ra}: {len(khoa)} tài liệu, {len(muc) - len(khoa)} mục trong .bib không được trích")


if __name__ == "__main__":
    main()
