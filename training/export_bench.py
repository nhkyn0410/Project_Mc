"""Ghi nét của nhóm chỉnh và tập đánh giá cho bài đo trên điện thoại (docs/07-nhat-ky-thi-nghiem.md, mục 15).

Mỗi dòng gồm nét gốc có thời điểm, và nét của dòng ảo sau lớp ghép đoạn, cùng số điểm và cùng thời điểm.
Dòng chép khác đề bị bỏ như eval_selfcollected.py. Tệp ghi vào android/app/src/androidTest/assets/bench/,
thư mục này không đưa vào git vì chứa nét của người viết.

    python export_bench.py chinh ~/vnhw/data/nhom-chinh
    python export_bench.py danh-gia ~/vnhw/data/nhom-chinh-dot3
"""
import argparse
import glob
import json
import os

import numpy as np

import data as D
import ink

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "android", "app", "src", "androidTest", "assets", "bench")


def lines_of(folder):
    review = json.load(open(f"{folder}/review.json", encoding="utf8"))
    miscopied = {(r["participant"], r["index"]) for r in review["lines"] if r.get("miscopied")}
    for path in sorted(glob.glob(f"{folder}/*.json")):
        if path.endswith("review.json"):
            continue
        obj = json.load(open(path, encoding="utf8"))
        for s in obj.get("sessions", [obj]):
            for line in s["lines"]:
                if not line.get("strokes") or line.get("review", {}).get("miscopied") or (s["participant"], line["index"]) in miscopied:
                    continue
                yield s, line


def stitched_with_times(raw, top, row):
    """Dòng ảo của ink.stitch, gắn lại thời điểm: lớp ghép đoạn giữ số điểm và thứ tự nét trong mỗi hàng."""
    xy = [p[:, :2] for p in raw]
    rows = ink.assign_rows(xy, top, row)
    order = [i for u in range(int(rows.max()) + 1) for i in range(len(xy)) if rows[i] == u]
    moved = ink.stitch(xy, top, row)
    if len(moved) != len(order) or any(len(m) != len(raw[i]) for m, i in zip(moved, order)):
        raise ValueError("lớp ghép đoạn đổi số nét hoặc số điểm")
    out = [np.column_stack([m, raw[i][:, 2]]) for m, i in zip(moved, order)]
    lo = np.min([o[:, :2].min(axis=0) for o in out], axis=0)
    return [o - np.array([lo[0], lo[1], 0.0]) for o in out]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("folder")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    n = 0
    with open(os.path.join(OUT, f"{a.name}.jsonl"), "w", encoding="utf8") as f:
        for s, line in lines_of(os.path.expanduser(a.folder)):
            raw = [np.array(st["points"], np.float64)[:, :3] for st in line["strokes"] if not st.get("cancelled") and st["points"]]
            frame = line["frame"]
            broken = line["condition"] == "broken"
            row = frame["rowPx"] if broken else frame["bandPx"]
            stitched = stitched_with_times(raw, frame["topPad"], row)
            xmax_raw = max(r[:, 0].max() for r in raw)
            xmax_st = max(o[:, 0].max() for o in stitched)
            ymax_st = max(o[:, 1].max() for o in stitched)
            item = {
                "who": s["participant"], "index": line["index"], "kind": "ngắt" if broken else "liền",
                "label": D.normalize_label(line["text"]), "topPad": frame["topPad"], "rowPx": row,
                # Vùng viết cho ML Kit: dòng ngắt gốc dùng cả khung viết, dòng liền và dòng ảo dùng chiều cao một hàng.
                "areaRaw": [max(frame["canvasW"], xmax_raw), frame["canvasH"] if broken else row],
                "areaStitched": [xmax_st, max(row, ymax_st)],
                "raw": [np.round(r, 2).tolist() for r in raw],
                "stitched": [np.round(o, 2).tolist() for o in stitched],
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            n += 1
    print(a.name, n, "dòng")


if __name__ == "__main__":
    main()
