"""Đổi dữ liệu người viết gửi về thành tệp JSON thu-net/1, mỗi buổi một tệp.

    python tools/thu-net/giai-ma.py <tệp hoặc thư mục> ... [--ra <thư mục ra>]

Nhận ba dạng đầu vào, lẫn trong cùng một thư mục cũng được:
    tệp JSON của một buổi (thu-net/1), kể cả khi mang đuôi .txt;
    tệp gộp nhiều buổi (thu-net-bundle/1);
    văn bản dán từ nút Sao chép của công cụ: bản nén THUNET1|...|HET, hoặc JSON thô.

Mỗi buổi đọc được ghi thành <thư mục ra>/thu-net_<mã>_<cách nhập>_<ngày giờ>.json, mặc định thư mục ra là
thư mục da-giai-ma cạnh đầu vào đầu tiên. Bản nén và tệp một buổi được ghi lại đúng từng byte của JSON gốc.
Tệp bị cắt cụt hoặc sai mã kiểm tra được báo lỗi và không ghi. Chương trình chỉ đọc dữ liệu, không chạy mã nào
trong tệp, và trả mã thoát 1 khi có ít nhất một lỗi.
"""
import base64
import datetime
import gzip
import json
import os
import re
import sys
import zlib

BLOCK = re.compile(r"THUNET1\|([^|\s]+)\|(\d+)\|([0-9a-fA-F]{8})\|([A-Za-z0-9+/=\s]+?)\|HET")
INPUT_FILE = {"touch": "ngon-tay", "pen": "s-pen", "mouse": "chuot"}


def stamp(iso):
    """Ngày giờ theo giờ Việt Nam, như tên tệp mà công cụ đặt."""
    t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")) + datetime.timedelta(hours=7)
    return t.strftime("%Y%m%d-%H%M")


def check(s):
    """Trả về lỗi đầu tiên của một buổi, hoặc None khi buổi dùng được."""
    if not isinstance(s, dict) or s.get("schema") != "thu-net/1":
        return "không phải buổi thu-net/1"
    for key in ("id", "participant", "input", "createdAt", "lines", "device"):
        if key not in s:
            return "thiếu trường " + key
    if not isinstance(s["lines"], list) or not s["lines"]:
        return "không có dòng nào"
    return None


def describe(s):
    lines = s["lines"]
    written = sum(1 for l in lines if l.get("strokes"))
    verdicts = [(l.get("review") or {}).get("verdict") for l in lines]
    return "%s, %s, nhóm %s, %s, %d/%d dòng đã viết, chép đúng %d, chép khác %d, chưa rà soát %d, bản công cụ %s" % (
        s["participant"], s.get("cohort") or s.get("protocol"), s.get("group"), (s.get("device") or {}).get("model"),
        written, len(lines), verdicts.count("dung"), verdicts.count("khac"), verdicts.count(None), s.get("tool") or "trước 15/11/2026")


def sessions_of(path):
    """Trả về (danh sách (buổi, byte JSON gốc hoặc None), danh sách lỗi) của một tệp."""
    raw = open(path, "rb").read()
    text = raw.decode("utf-8-sig", errors="replace")
    found, errors = [], []
    blocks = list(BLOCK.finditer(text))
    if text.count("THUNET1|") > len(blocks):
        errors.append("có %d bản nén bị cắt cụt hoặc bị sửa, thiếu chữ HET ở cuối" % (text.count("THUNET1|") - len(blocks)))
    for m in blocks:
        code, size, crc = m.group(1), int(m.group(2)), int(m.group(3), 16)
        try:
            data = gzip.decompress(base64.b64decode(re.sub(r"\s+", "", m.group(4)), validate=True))
        except Exception as e:  # noqa: BLE001
            errors.append("bản nén của %s không giải được: %s" % (code, type(e).__name__))
            continue
        if len(data) != size or zlib.crc32(data) & 0xFFFFFFFF != crc:
            errors.append("bản nén của %s sai số byte hoặc sai mã kiểm tra, có thể đã bị cắt" % code)
            continue
        found.append((json.loads(data.decode("utf8")), data))
    if not blocks and "THUNET1|" not in text:
        body = text.strip()
        try:
            obj = json.loads(body)
        except ValueError:
            errors.append("không đọc được JSON, tệp có thể bị cắt cụt (%d ký tự, kết thúc bằng %r)" % (len(body), body[-20:]))
            return found, errors
        if isinstance(obj, dict) and obj.get("schema") == "thu-net-bundle/1":
            found += [(s, None) for s in obj.get("sessions", [])]
        else:
            found.append((obj, body.encode("utf8")))
    return found, errors


def main(argv):
    args = [a for a in argv if a != "--ra"]
    out = None
    if "--ra" in argv:
        out = argv[argv.index("--ra") + 1]
        args.remove(out)
    if not args:
        print(__doc__)
        return 1
    files = []
    for a in args:
        if os.path.isdir(a):
            files += [os.path.join(a, n) for n in sorted(os.listdir(a)) if os.path.isfile(os.path.join(a, n))]
        else:
            files.append(a)
    out = out or os.path.join(os.path.dirname(os.path.abspath(args[0])) if os.path.isfile(args[0]) else os.path.abspath(args[0]), "da-giai-ma")
    os.makedirs(out, exist_ok=True)
    seen, bad = {}, 0
    for path in files:
        found, errors = sessions_of(path)
        for e in errors:
            bad += 1
            print("LỖI  %s: %s" % (os.path.basename(path), e))
        for s, data in found:
            problem = check(s)
            if problem:
                bad += 1
                print("LỖI  %s: %s" % (os.path.basename(path), problem))
                continue
            # Cùng một buổi có thể được gửi nhiều lần: giữ bản rà soát sau cùng.
            key = s["id"]
            rank = (s.get("reviewedAt") or "", s.get("copiedAt") or "", s.get("exportedAt") or "")
            if key in seen and seen[key][0] >= rank:
                print("TRÙNG %s: buổi %s đã có, bỏ qua" % (os.path.basename(path), s["participant"]))
                continue
            name = "thu-net_%s_%s_%s.json" % (s["participant"], INPUT_FILE.get(s["input"], s["input"]), stamp(s["createdAt"]))
            payload = data if data is not None else json.dumps(s, ensure_ascii=False, separators=(",", ":")).encode("utf8")
            with open(os.path.join(out, name), "wb") as f:
                f.write(payload)
            seen[key] = (rank, name)
            print("ĐƯỢC %s: %s" % (name, describe(s)))
    print("\n%d buổi đã ghi vào %s, %d lỗi." % (len(seen), out, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
