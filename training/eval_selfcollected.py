"""Đánh giá trên tệp thu từ công cụ tools/thu-net/ theo định dạng thu-net/1.

Chạy đúng luồng của điện thoại và báo CER, WER cho từng kịch bản:
    liền: dòng liền vẽ thẳng thành ảnh
    ngắt, ghép: dòng ngắt qua lớp ghép đoạn
    ngắt, từng hàng: mốc so sánh, nhận dạng từng hàng rồi nối chuỗi
    mô phỏng N chỗ nối: dòng liền được cắt N lần (docs/03-du-lieu.md, mục 4)

    python eval_selfcollected.py --run ~/vnhw/runs/m1_v2_clean --lm lm.bin --alpha 0.45 --beta 4 tep1.json tep2.json
"""
import argparse
import collections
import json

import numpy as np

import data as D
import ink
import simulate
from decoder import Decoder
from lm_binary import NGramBin
from metrics import error_rates


def sessions(paths):
    for path in paths:
        with open(path, encoding="utf8") as f:
            obj = json.load(f)
        if obj.get("schema") == "thu-net-bundle/1":
            yield from obj["sessions"]
        else:
            yield obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    p.add_argument("--run", required=True)
    p.add_argument("--lm", required=True)
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--model", default="m_float16.tflite")
    p.add_argument("--stroke-widths", type=float, nargs="+", default=[ink.STROKE_WIDTH])
    # Dòng ngắt thật của nhóm thử chiếm từ 3 đến 7 hàng (docs/07-nhat-ky-thi-nghiem.md, mục 10).
    p.add_argument("--cuts", type=int, nargs="*", default=[2, 4, 6])
    p.add_argument("--dump", default="", help="Ghi nhãn và kết quả nhận dạng ra tệp này, thêm độ dày nét vào tên khi đo nhiều độ dày")
    p.add_argument("--greedy", action="store_true", help="Giải mã đơn giản, không dùng mô hình ngôn ngữ (M1)")
    p.add_argument("--review", default="", help="Tệp rà soát riêng, đánh dấu thêm các dòng chép khác đề theo mã người viết và chỉ số dòng")
    p.add_argument("--drop-strays", action="store_true", help="Bỏ nét lạc khi ghép bằng ink.clean_rows, bộ lọc chưa được nhận (docs/07-nhat-ky-thi-nghiem.md, mục 10.15 đến mục 10.17)")
    p.add_argument("--by-writer", action="store_true", help="In thêm CER (2) của từng người viết, theo docs/02-yeu-cau-va-danh-gia.md, mục 2.6")
    a = p.parse_args()

    import tensorflow as tf

    config = json.load(open(f"{a.run}/config.json", encoding="utf8"))
    max_ink = config.get("max_ink", 0) or 0
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    interpreter = tf.lite.Interpreter(model_path=f"{a.run}/{a.model}", num_threads=8)
    interpreter.allocate_tensors()
    in_i, out_i = interpreter.get_input_details()[0]["index"], interpreter.get_output_details()[0]["index"]
    decoder = None if a.greedy else Decoder(chars, NGramBin(a.lm), a.alpha, a.beta)
    charset = D.Charset(chars)

    def read(strokes, width):
        image = ink.render(strokes, config["width"], config["height"], stroke_width=width, max_ink=max_ink)
        interpreter.reset_all_variables()
        interpreter.set_tensor(in_i, image[None, ..., None].astype(np.float32) / 255.0)
        interpreter.invoke()
        probs = interpreter.get_tensor(out_i)[0].copy()
        if decoder is None:
            return charset.decode_greedy(probs.argmax(-1).tolist())
        return decoder.decode(probs, keep=1)[0][1]

    def stitched(strokes, top, row, width):
        return read(ink.stitch(strokes, top, row, strays=a.drop_strays), width)

    def per_row(strokes, top, row, width):
        rows = ink.assign_rows(strokes, top, row)
        return " ".join(read(ink.stitch_rows([[s for s, r in zip(strokes, rows) if r == u]]), width) for u in sorted(set(rows.tolist())))

    miscopied = set()
    if a.review:
        with open(a.review, encoding="utf8") as f:
            miscopied = {(r["participant"], r["index"]) for r in json.load(f)["lines"] if r.get("miscopied")}
    lines, skipped = [], 0
    for s in sessions(a.files):
        for line in s["lines"]:
            if not line.get("strokes"):
                continue
            if line.get("review", {}).get("miscopied") or (s["participant"], line["index"]) in miscopied:
                skipped += 1
                continue
            lines.append((s, line, D.normalize_label(line["text"])))
    print(f"{len(lines)} dòng từ {len({x[0]['participant'] for x in lines})} người, bỏ {skipped} dòng chép khác đề", flush=True)

    for width in a.stroke_widths:
        groups = collections.defaultdict(lambda: ([], [], []))
        dump = []

        def note(key, label, text):
            groups[key][0].append(label)
            groups[key][1].append(text)
            groups[key][2].append(who)
            dump.append(f"[{key}] {who} {line['index']}\n{label}\n{text}\n")

        for index, (session, line, label) in enumerate(lines):
            kind = session["input"]
            who = session["participant"]
            strokes = ink.strokes_of(line)
            frame = line["frame"]
            if line["condition"] == "broken":
                top, row = frame["topPad"], frame["rowPx"]
                note(f"{kind} | ngắt, ghép", label, stitched(strokes, top, row, width))
                note(f"{kind} | ngắt, từng hàng", label, per_row(strokes, top, row, width))
                continue
            # Ứng dụng đưa mọi dòng qua lớp ghép đoạn, kể cả dòng liền, để thu các khoảng trống quá lớn.
            note(f"{kind} | liền", label, stitched(strokes, frame["topPad"], frame["bandPx"], width))
            boundaries = simulate.word_gaps(strokes, label.count(" "))
            row = 12.0 * session["device"]["pxPerMm"]
            for n in a.cuts:
                rng = np.random.default_rng(index * 100 + n)
                chosen = simulate.choose_cuts(boundaries, n, rng)
                placed = simulate.simulate(strokes, chosen, row, rng)
                note(f"{kind} | mô phỏng {n} chỗ nối, ghép", label, stitched(placed, simulate.TOP_PAD, row, width))
                note(f"{kind} | mô phỏng {n} chỗ nối, từng hàng", label, per_row(placed, simulate.TOP_PAD, row, width))

        print(f"độ dày nét {width}, {'M1 giải mã đơn giản' if a.greedy else 'M2 beam search và n-gram'}")
        for key, (truth, pred, _) in sorted(groups.items()):
            cer1, cer2 = error_rates(truth, pred)
            wer1, wer2 = error_rates(truth, pred, "word")
            print(f"  {key}: {len(truth)} dòng, CER (2) {cer2:.4f}, WER (2) {wer2:.4f}, CER (1) {cer1:.4f}, WER (1) {wer1:.4f}", flush=True)
        if a.by_writer:
            print("  CER (2) theo người viết, số dòng trong ngoặc")
            for key, (truth, pred, writers) in sorted(groups.items()):
                parts = []
                for w in sorted(set(writers)):
                    pick = [i for i, x in enumerate(writers) if x == w]
                    parts.append(f"{w} {error_rates([truth[i] for i in pick], [pred[i] for i in pick])[1]:.4f} ({len(pick)})")
                print(f"    {key}: " + ", ".join(parts), flush=True)
        if a.dump:
            path = a.dump if len(a.stroke_widths) == 1 else a.dump.replace(".txt", f"_{width}.txt")
            with open(path, "w", encoding="utf8") as f:
                f.write("\n".join(dump))


if __name__ == "__main__":
    main()
