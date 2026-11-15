"""Vẽ lại ảnh VNOnDB bằng đúng bộ vẽ của ứng dụng.

Ảnh của dòng không phụ thuộc thứ tự viết, nên chỉ cần hình dạng nét. Lấy khung xương của nét
trên ảnh gốc rồi vẽ lại bằng ink.render, ta có ảnh giống ảnh mà điện thoại sẽ tạo ra.
Chế độ dòng lệnh đo độ nhạy của mô hình với độ dày nét trên tập kiểm định.
"""
import argparse
import json
import multiprocessing as mp
import os

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from skimage.morphology import skeletonize

import data as D
import ink

THRESHOLD = 80  # Giá trị cho tỷ lệ lỗi thấp nhất trong các giá trị đã thử, xem nhật ký thí nghiệm
BLUR = 0.0  # Làm mờ khiến các vòng nhỏ của chữ dính lại nên không dùng
_NEIGHBORS = ((0, 1), (1, 0), (1, 1), (1, -1))


def skeleton_strokes(path):
    """Trả về danh sách các đoạn thẳng hai điểm (x, y) theo tọa độ ảnh gốc."""
    with Image.open(path) as im:
        gray = ImageOps.invert(im.convert("L"))
    if BLUR:
        gray = gray.filter(ImageFilter.GaussianBlur(BLUR))
    skeleton = skeletonize(np.asarray(gray, dtype=np.uint8) > THRESHOLD)
    ys, xs = np.nonzero(skeleton)
    if len(xs) == 0:
        return [np.array([[0.0, 0.0]])]
    strokes = []
    lit = set(zip(ys.tolist(), xs.tolist()))
    linked = set()
    for y, x in lit:
        for dy, dx in _NEIGHBORS:
            if (y + dy, x + dx) in lit:
                strokes.append(np.array([[x, y], [x + dx, y + dy]], np.float64))
                linked.add((y, x)); linked.add((y + dy, x + dx))
    for y, x in lit - linked:
        strokes.append(np.array([[x, y]], np.float64))
    return strokes


def set_skeleton_options(threshold, blur):
    global THRESHOLD, BLUR
    THRESHOLD, BLUR = threshold, blur


_W = {}


def _render_one(i):
    strokes = skeleton_strokes(_W["paths"][i])
    return [ink.render(strokes, _W["width"], _W["height"], stroke_width=s, max_ink=_W["cap"]) for s in _W["strokes"]]


def render_all(lines_dir, stems, width, height, stroke_widths, workers=8, cap=0):
    """Trả về mảng (số dòng, số độ dày nét, height, width) kiểu uint8."""
    _W.update(paths=[os.path.join(lines_dir, s + ".png") for s in stems], width=width, height=height, strokes=stroke_widths, cap=cap)
    with mp.get_context("fork").Pool(workers) as pool:
        out = pool.map(_render_one, range(len(stems)), chunksize=16)
    return np.array(out, np.uint8)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--model", default="m_float16.tflite")
    p.add_argument("--stroke-widths", type=float, nargs="+", default=[0.6, 0.8, 1.0, 1.2, 1.5, 2.0])
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--data", default=os.path.expanduser("~/vnhw/data"))
    p.add_argument("--threshold", type=int, default=THRESHOLD)
    p.add_argument("--blur", type=float, default=BLUR)
    a = p.parse_args()
    set_skeleton_options(a.threshold, a.blur)

    config = json.load(open(f"{a.run}/config.json", encoding="utf8"))
    width, height, crop = config["width"], config["height"], not config["no_crop"]
    cap = config.get("max_ink", 0) or 0
    stems = D.read_split(f"{a.data}/splits/val.ln")
    if a.limit:
        stems = stems[: a.limit]
    lines = f"{a.data}/lines"
    labels = [D.read_label(lines, s) for s in stems]
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    charset = D.Charset(chars)
    original = D.load_images(lines, stems, width, height, crop, max_ink=cap)
    variants = render_all(lines, stems, width, height, a.stroke_widths, cap=cap)

    import tensorflow as tf

    from metrics import error_rates

    interpreter = tf.lite.Interpreter(model_path=f"{a.run}/{a.model}", num_threads=8)
    interpreter.allocate_tensors()
    in_i, out_i = interpreter.get_input_details()[0]["index"], interpreter.get_output_details()[0]["index"]

    def score(images):
        texts = []
        for image in images:
            interpreter.reset_all_variables()
            interpreter.set_tensor(in_i, image[None, ..., None].astype(np.float32) / 255.0)
            interpreter.invoke()
            texts.append(charset.decode_greedy(interpreter.get_tensor(out_i)[0].argmax(-1).tolist()))
        return round(error_rates(labels, texts)[1], 5)

    report = dict(lines=len(stems), original=score(original))
    print("original", report["original"], flush=True)
    for k, s in enumerate(a.stroke_widths):
        report[str(s)] = score(variants[:, k])
        print("stroke", s, report[str(s)], "mean_ink", round(float(variants[:, k][variants[:, k] > 40].mean()), 1), flush=True)
    json.dump(report, open(f"{a.run}/rerender_report.json", "w"), indent=1)


if __name__ == "__main__":
    main()
