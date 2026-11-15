"""Chỉnh alpha, beta của bộ giải mã trên tập kiểm định và đo tỷ lệ lỗi.

Chỉ đọc tập kiểm định. Chạy trong Ubuntu:
    python tune_decoder.py --run ~/vnhw/runs/m1_v2 --lm ~/vnhw/data/ngram.npz
"""
import argparse
import json
import multiprocessing as mp
import os
import time

import numpy as np

import data as D
from decoder import Decoder
from metrics import error_rates
from ngram import NGram

_G = {}


def _work(args):
    i, alpha, beta, use_lm, beam = args
    d = Decoder(_G["chars"], _G["lm"] if use_lm else None, alpha, beta, beam=beam)
    return d.decode(_G["probs"][i], keep=1)[0][1]


def scores(pool, indices, labels, alpha, beta, use_lm, beam):
    started = time.time()
    out = pool.map(_work, [(i, alpha, beta, use_lm, beam) for i in indices], chunksize=8)
    truth = [labels[i] for i in indices]
    cer1, cer2 = error_rates(truth, out)
    wer1, wer2 = error_rates(truth, out, "word")
    return dict(alpha=alpha, beta=beta, lm=use_lm, beam=beam, lines=len(indices), cer_line=round(cer2, 5), wer_line=round(wer2, 5),
                cer_total=round(cer1, 5), wer_total=round(wer1, 5), ms_per_line=round((time.time() - started) * 1000 * _G["workers"] / len(indices), 1)), out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--lm", required=True)
    p.add_argument("--data", default=os.path.expanduser("~/vnhw/data"))
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--subset", type=int, default=400)
    p.add_argument("--alphas", type=float, nargs="+", default=[0.3, 0.45, 0.6, 0.8])
    p.add_argument("--betas", type=float, nargs="+", default=[1.0, 2.0, 3.0, 4.0, 6.0, 8.0])
    a = p.parse_args()

    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
    import keras

    config = json.load(open(f"{a.run}/config.json", encoding="utf8"))
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    stems = D.read_split(f"{a.data}/splits/val.ln")
    labels = [D.read_label(f"{a.data}/lines", s) for s in stems]
    cache = f"{a.run}/val_probs.npy"
    if os.path.exists(cache):
        probs = np.load(cache)
    else:
        model = keras.models.load_model(f"{a.run}/best.keras")
        images = D.load_images(f"{a.data}/lines", stems, config["width"], config["height"], not config["no_crop"], config.get("max_ink", 0))
        probs = np.concatenate([model(images[i : i + 32][..., None].astype("float32") / 255.0, training=False).numpy()
                                for i in range(0, len(images), 32)]).astype("float32")
        np.save(cache, probs)
    _G.update(chars=chars, probs=probs, lm=NGram(a.lm), workers=a.workers)
    print("loaded", probs.shape, flush=True)

    charset = D.Charset(chars)
    greedy = [charset.decode_greedy(r.argmax(-1).tolist()) for r in probs]
    c1, c2 = error_rates(labels, greedy); w1, w2 = error_rates(labels, greedy, "word")
    report = dict(greedy=dict(cer_line=round(c2, 5), wer_line=round(w2, 5), cer_total=round(c1, 5), wer_total=round(w1, 5)))
    print(json.dumps(report), flush=True)

    every = max(1, len(stems) // a.subset)
    subset = list(range(0, len(stems), every))
    all_lines = list(range(len(stems)))
    with mp.get_context("fork").Pool(a.workers) as pool:
        report["beam_no_lm"], _ = scores(pool, all_lines, labels, 0.0, 0.0, False, 30)
        print(json.dumps(report["beam_no_lm"]), flush=True)
        grid = []
        for alpha in a.alphas:
            for beta in a.betas:
                row, _ = scores(pool, subset, labels, alpha, beta, True, 30)
                grid.append(row); print(json.dumps(row), flush=True)
        best = min(grid, key=lambda r: r["cer_line"])
        report["grid"] = grid
        report["best_lm"], preds = scores(pool, all_lines, labels, best["alpha"], best["beta"], True, 30)
        print("BEST_LM", json.dumps(report["best_lm"]), flush=True)
        for beam in (10, 20, 50):
            row, _ = scores(pool, all_lines, labels, best["alpha"], best["beta"], True, beam)
            report[f"beam_{beam}"] = row; print(json.dumps(row), flush=True)
    json.dump(report, open(f"{a.run}/decoder_report.json", "w", encoding="utf8"), indent=1)
    with open(f"{a.run}/val_predictions_lm.txt", "w", encoding="utf8") as f:
        for t, q in zip(labels, preds):
            f.write(t + "\n" + q + "\n\n")


if __name__ == "__main__":
    main()
