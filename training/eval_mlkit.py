"""Chấm kết quả bài đo trên điện thoại: ML Kit, ứng dụng có và không có n-gram ký tự, và độ trễ
(docs/07-nhat-ky-thi-nghiem.md, mục 15).

Đầu vào là các tệp lấy về từ điện thoại bằng adb pull: mlkit-chinh.jsonl, mlkit-danh-gia.jsonl và app-chinh.jsonl.
Trên tập đánh giá, ML Kit được so ghép cặp với kết quả từng dòng của cấu hình đã chốt (m2_1.2.txt của mục 12.2),
khoảng tin cậy 95% lấy bằng bootstrap với đơn vị lấy mẫu lại là người viết (docs/02-yeu-cau-va-danh-gia.md, mục 2.6).
Mô hình của đề tài không chạy lại trên tập đánh giá.

    python eval_mlkit.py --bench <thư mục tệp lấy về> --dump ~/vnhw/runs/m1l_rr_e100/nhom-chinh-dot3/m2_1.2.txt
"""
import argparse
import json
import os

import numpy as np

import data as D
from metrics import edit_distance, error_rates

KINDS = ("liền", "ngắt")


def read_jsonl(path):
    with open(path, encoding="utf8") as f:
        return [json.loads(x) for x in f if x.strip()]


def read_dump(path):
    """Kết quả từng dòng của eval_selfcollected.py --dump, theo (người viết, chỉ số dòng, loại dòng)."""
    out = {}
    for block in open(path, encoding="utf8").read().split("\n\n"):
        lines = block.strip("\n").split("\n")
        if len(lines) < 3 or not lines[0].startswith("["):
            continue
        scenario = lines[0][1:lines[0].index("]")].split("|")[-1].strip()
        who, index = lines[0][lines[0].index("]") + 1:].split()
        kind = {"liền": "liền", "ngắt, ghép": "ngắt"}.get(scenario)
        if kind:
            out[(who, int(index), kind)] = lines[2]
    return out


def score(labels, texts):
    c1, c2 = error_rates(labels, texts)
    w1, w2 = error_rates(labels, texts, "word")
    return {"cer2": round(c2 * 100, 2), "wer2": round(w2 * 100, 2), "cer1": round(c1 * 100, 2)}


def per_line(label, text):
    return edit_distance(label, text) / max(1, len(label))


def bootstrap(rows, key_a, key_b, n=10000, seed=0):
    """Hiệu CER (2) a trừ b, lấy mẫu lại người viết, trả về hiệu và khoảng tin cậy 95%."""
    writers = sorted({r["who"] for r in rows})
    by = {w: [(per_line(r["label"], r[key_a]), per_line(r["label"], r[key_b])) for r in rows if r["who"] == w] for w in writers}
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n):
        pick = rng.choice(len(writers), len(writers), replace=True)
        pairs = [p for i in pick for p in by[writers[i]]]
        a = np.mean([p[0] for p in pairs]); b = np.mean([p[1] for p in pairs])
        diffs.append(a - b)
    base = np.mean([p[0] for w in writers for p in by[w]]) - np.mean([p[1] for w in writers for p in by[w]])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return round(float(base) * 100, 2), round(float(lo) * 100, 2), round(float(hi) * 100, 2)


def read_pred(path):
    """Nhãn và kết quả của nhóm chỉnh trong tệp pred-*.txt của eval_char_lm.py, theo thứ tự dòng."""
    got = []
    for block in open(path, encoding="utf8").read().split("\n\n"):
        lines = block.split("\n")
        if len(lines) >= 3 and lines[0].startswith("[chinh]"):
            got.append((lines[1], lines[2]))
    return got


def latency(values):
    v = np.array(values, np.float64)
    return {"trung vị": round(float(np.median(v)), 1), "phân vị 95": round(float(np.percentile(v, 95)), 1), "lớn nhất": round(float(v.max()), 1)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bench", required=True)
    p.add_argument("--dump", required=True, help="m2_1.2.txt của cấu hình đã chốt trên tập đánh giá")
    p.add_argument("--chinh-new", default=os.path.expanduser("~/vnhw/runs/m1l_rr_e100/char-lm/pred-ket-hop-s6-bin-0.txt"))
    p.add_argument("--chinh-old", default=os.path.expanduser("~/vnhw/runs/m1l_rr_e100/char-lm/pred-goc-0.txt"))
    a = p.parse_args()
    report = {}
    norm = D.normalize_label

    # ML Kit trên hai tập, nét gốc và dòng ảo.
    for name in ("chinh", "danh-gia"):
        rows = read_jsonl(os.path.join(a.bench, f"mlkit-{name}.jsonl"))
        for r in rows:
            r["mlkit_raw"] = norm(r["raw"][0]) if r["raw"] else ""
            r["mlkit_stitched"] = norm(r["stitched"][0]) if r["stitched"] else ""
        for variant in ("mlkit_raw", "mlkit_stitched"):
            for kind in KINDS + ("gộp",):
                pick = [r for r in rows if kind == "gộp" or r["kind"] == kind]
                report[f"{name} | {variant} | {kind}"] = dict(score([r["label"] for r in pick], [r[variant] for r in pick]), dòng=len(pick))
            report[f"{name} | {variant} | thời gian ms"] = latency([r[variant.replace("mlkit_", "") + "Ms"] for r in rows])
            # Ảnh hưởng của bước chuẩn hóa: chấm kết quả thô của ML Kit.
            key = variant.replace("mlkit_", "")
            report[f"{name} | {variant} | chưa chuẩn hóa, gộp"] = score([r["label"] for r in rows], [r[key][0] if r[key] else "" for r in rows])
        if name == "chinh":
            for key, path in (("py_new", a.chinh_new), ("py_old", a.chinh_old)):
                got = read_pred(path)
                for r, (label, text) in zip(rows, got):
                    if label != r["label"]:
                        raise ValueError("thứ tự dòng của nhóm chỉnh khác nhau")
                    r[key] = text
            for kind in KINDS + ("gộp",):
                pick = [r for r in rows if kind == "gộp" or r["kind"] == kind]
                for key in ("py_old", "py_new"):
                    report[f"chinh | {key} | {kind}"] = dict(score([r["label"] for r in pick], [r[key] for r in pick]), dòng=len(pick))
                for variant in ("mlkit_raw", "mlkit_stitched"):
                    for key in ("py_old", "py_new"):
                        d, lo, hi = bootstrap(pick, variant, key)
                        report[f"chinh | {variant} trừ {key} | {kind}"] = {"hiệu": d, "khoảng tin cậy": [lo, hi]}
        if name == "danh-gia":
            dump = read_dump(a.dump)
            for r in rows:
                r["ours"] = dump[(r["who"], r["index"], r["kind"])]
            for kind in KINDS + ("gộp",):
                pick = [r for r in rows if kind == "gộp" or r["kind"] == kind]
                report[f"danh-gia | đã chốt | {kind}"] = dict(score([r["label"] for r in pick], [r["ours"] for r in pick]), dòng=len(pick))
                for variant in ("mlkit_raw", "mlkit_stitched"):
                    d, lo, hi = bootstrap(pick, variant, "ours")
                    report[f"danh-gia | {variant} trừ đã chốt | {kind}"] = {"hiệu": d, "khoảng tin cậy": [lo, hi]}
        json.dump(rows, open(os.path.join(a.bench, f"cham-{name}.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)

    # Ứng dụng trên điện thoại, nhóm chỉnh: kết quả và độ trễ, đối chiếu với bản Python.
    app_path = os.path.join(a.bench, "app-chinh.jsonl")
    if os.path.exists(app_path):
        rows = read_jsonl(app_path)
        py = {}
        for key, path in (("new", a.chinh_new), ("old", a.chinh_old)):
            got = []
            for block in open(path, encoding="utf8").read().split("\n\n"):
                lines = block.split("\n")
                if len(lines) >= 3 and lines[0].startswith("[chinh]"):
                    got.append((lines[1], lines[2]))
            py[key] = got
        for i, r in enumerate(rows):
            for key in ("new", "old"):
                label, text = py[key][i]
                if label != r["label"]:
                    raise ValueError(f"thứ tự dòng khác nhau ở dòng {i}")
                r[f"py_{key}"] = text
        for key in ("new", "old"):
            same = sum(r[key] == r[f"py_{key}"] for r in rows)
            report[f"chinh | ứng dụng {key} | trùng bản Python"] = f"{same} / {len(rows)}"
            for kind in KINDS + ("gộp",):
                pick = [r for r in rows if kind == "gộp" or r["kind"] == kind]
                report[f"chinh | ứng dụng {key} | {kind}"] = dict(score([r["label"] for r in pick], [r[key] for r in pick]), dòng=len(pick))
            report[f"chinh | ứng dụng {key} | độ trễ ms"] = latency([r[f"{key}Ms"] for r in rows])
            for part in ("Render", "Model", "Decode"):
                report[f"chinh | ứng dụng {key} | {part} ms"] = latency([r[f"{key}{part}"] for r in rows])
            longest = max(rows, key=lambda r: (len(r["label"]), r["points"]))
            report[f"chinh | ứng dụng {key} | dòng dài nhất"] = {"ký tự": len(longest["label"]), "điểm": longest["points"], "ms": round(longest[f"{key}Ms"], 1)}
    for k, v in report.items():
        print(k, v)
    json.dump(report, open(os.path.join(a.bench, "bao-cao.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
