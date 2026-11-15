"""Tạo tệp cho ứng dụng Android và bộ mẫu đối chiếu Python với Kotlin.

Chạy trong Ubuntu sau export_tflite.py:
    python export_assets.py --run ~/vnhw/runs/m1_v2 --lm ~/vnhw/data/ngram_clean.npz --alpha 0.6 --beta 4
"""
import argparse
import json
import os
import shutil

import numpy as np

import ink
import lm_binary
from decoder import Decoder

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "android", "app", "src", "main", "assets")
TEST_RES = os.path.join(HERE, "..", "android", "app", "src", "test", "resources")


def random_strokes(rng, n_rows):
    """Nét tổng hợp viết lần lượt từng hàng, có chân chữ, nét dấu viết sau, khoảng trống lớn và dấu bổ sung cho hàng trên."""
    strokes = []
    top, row = 14.0, 90.0
    for r in range(n_rows):
        x = rng.uniform(5, 30)
        mid = top + row * (r + 0.5)
        for _ in range(rng.integers(3, 7)):
            n = rng.integers(8, 30)
            xs = x + np.cumsum(rng.uniform(0.5, 3.5, n))
            ys = mid + rng.uniform(-22, 22) * np.sin(np.linspace(0, rng.uniform(4, 14), n))
            strokes.append(np.stack([xs, ys], axis=1))
            if rng.random() < 0.3:
                # Chân chữ: nét riêng đi xuống dưới thân chữ.
                strokes.append(np.stack([xs[-1] + np.linspace(0, rng.uniform(-6, 6), 10), mid + 15 + np.linspace(0, rng.uniform(25, 45), 10)], axis=1))
            if rng.random() < 0.3:
                # Nét dấu viết sau, nằm trên thân chữ.
                cx = rng.uniform(xs[0], xs[-1])
                strokes.append(np.array([[cx, mid - 40], [cx + 4, mid - 44]]))
            x = xs[-1] + (rng.uniform(150, 300) if rng.random() < 0.15 else rng.uniform(4, 25))
        if r > 0 and rng.random() < 0.4:
            # Dấu bổ sung cho hàng trên, viết sau khi đã sang hàng này.
            cx = rng.uniform(20, 120)
            strokes.append(np.array([[cx, mid - row - 40], [cx + 3, mid - row - 45]]))
    return strokes


def write_parity(run, lm_path, alpha, beta, max_ink=0, stroke_width=ink.STROKE_WIDTH):
    os.makedirs(TEST_RES, exist_ok=True)
    rng = np.random.default_rng(7)
    with open(os.path.join(TEST_RES, "ink_parity.txt"), "w", encoding="utf8") as f:
        for case in range(12):
            strokes = random_strokes(rng, int(rng.integers(1, 4)))
            rows = ink.assign_rows(strokes, 14.0, 90.0)
            stitched = ink.stitch(strokes, 14.0, 90.0)
            image = ink.render(stitched, stroke_width=stroke_width, max_ink=max_ink)
            f.write(f"case {len(strokes)}\n")
            for s in strokes:
                f.write(" ".join(repr(float(v)) for v in s.ravel().tolist()) + "\n")
            f.write(" ".join(map(str, rows.tolist())) + "\n")
            f.write(" ".join(repr(float(v)) for s in stitched for v in s.ravel().tolist()) + "\n")
            f.write(" ".join(map(str, image.ravel().tolist())) + "\n")
    chars = json.load(open(os.path.join(run, "charset.json"), encoding="utf8"))
    probs = np.load(os.path.join(run, "val_probs.npy"))
    lm = lm_binary.NGramBin(lm_path)
    d = Decoder(chars, lm, alpha, beta)
    idx = [0, 200, 700]
    probs[idx].astype("<f4").tofile(os.path.join(TEST_RES, "decoder_probs.bin"))
    with open(os.path.join(TEST_RES, "decoder_expected.txt"), "w", encoding="utf8") as f:
        for i in idx:
            result = d.decode(probs[i], keep=3)
            f.write("\t".join(t for _, t in result) + "\n")
    with open(os.path.join(TEST_RES, "params.txt"), "w", encoding="utf8") as f:
        f.write(f"{alpha} {beta} {probs.shape[1]} {probs.shape[2]} {len(idx)} {max_ink} {stroke_width}\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--lm", required=True)
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--model", default="m_float16.tflite")
    p.add_argument("--stroke-width", type=float, default=ink.STROKE_WIDTH)
    a = p.parse_args()
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(TEST_RES, exist_ok=True)
    lm_path = os.path.join(ASSETS, "lm.bin")
    lm_binary.write(a.lm, lm_path)
    shutil.copy(lm_path, os.path.join(TEST_RES, "lm.bin"))
    shutil.copy(os.path.join(a.run, a.model), os.path.join(ASSETS, "model.tflite"))
    chars = json.load(open(os.path.join(a.run, "charset.json"), encoding="utf8"))
    for folder in (ASSETS, TEST_RES):
        with open(os.path.join(folder, "chars.txt"), "w", encoding="utf8") as f:
            f.write("".join(chars))
    config = json.load(open(os.path.join(a.run, "config.json"), encoding="utf8"))
    max_ink = config.get("max_ink", 0) or 0
    with open(os.path.join(ASSETS, "params.txt"), "w", encoding="utf8") as f:
        f.write(f"{a.alpha} {a.beta} {max_ink} {a.stroke_width}\n")
    write_parity(a.run, lm_path, a.alpha, a.beta, max_ink, a.stroke_width)
    sizes = {n: round(os.path.getsize(os.path.join(ASSETS, n)) / 1e6, 2) for n in os.listdir(ASSETS)}
    print(json.dumps(sizes), "total MB", round(sum(sizes.values()), 2))


if __name__ == "__main__":
    main()
