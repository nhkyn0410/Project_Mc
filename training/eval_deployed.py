"""Đo đúng cấu hình đưa lên điện thoại: tệp .tflite đã lượng tử hóa và lm.bin.

Mặc định đo trên tập kiểm định. Chỉ dùng --split test một lần ở cuối đề tài
(docs/02-yeu-cau-va-danh-gia.md, mục 5).
"""
import argparse
import json
import multiprocessing as mp
import os
import time

import numpy as np

import data as D
from decoder import Decoder
from lm_binary import NGramBin
from metrics import error_rates

_G = {}


def _work(i):
    d = Decoder(_G["chars"], _G["lm"], _G["alpha"], _G["beta"], beam=_G["beam"])
    return d.decode(_G["probs"][i], keep=1)[0][1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--lm", required=True, help="tệp lm.bin")
    p.add_argument("--alpha", type=float, required=True)
    p.add_argument("--beta", type=float, required=True)
    p.add_argument("--beam", type=int, default=30)
    p.add_argument("--model", default="m_float16.tflite")
    p.add_argument("--split", default="val", choices=["val", "test"])
    p.add_argument("--confirm-test", action="store_true")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--data", default=os.path.expanduser("~/vnhw/data"))
    a = p.parse_args()
    if a.split == "test" and not a.confirm_test:
        raise SystemExit("Tập kiểm thử chỉ chạy một lần ở cuối. Thêm --confirm-test khi đã chốt mọi tham số.")

    import tensorflow as tf

    config = json.load(open(f"{a.run}/config.json", encoding="utf8"))
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    stems = D.read_split(f"{a.data}/splits/{a.split}.ln")
    labels = [D.read_label(f"{a.data}/lines", s) for s in stems]
    images = D.load_images(f"{a.data}/lines", stems, config["width"], config["height"], not config["no_crop"], config.get("max_ink", 0))
    interpreter = tf.lite.Interpreter(model_path=f"{a.run}/{a.model}", num_threads=8)
    interpreter.allocate_tensors()
    in_i = interpreter.get_input_details()[0]["index"]
    out_i = interpreter.get_output_details()[0]["index"]
    probs, started = [], time.time()
    for image in images:
        interpreter.reset_all_variables()
        interpreter.set_tensor(in_i, image[None, ..., None].astype(np.float32) / 255.0)
        interpreter.invoke()
        probs.append(interpreter.get_tensor(out_i)[0].copy())
    probs = np.stack(probs)
    model_s = time.time() - started
    _G.update(chars=chars, probs=probs, lm=NGramBin(a.lm), alpha=a.alpha, beta=a.beta, beam=a.beam)
    with mp.get_context("fork").Pool(a.workers) as pool:
        predictions = pool.map(_work, range(len(stems)), chunksize=8)
    cer1, cer2 = error_rates(labels, predictions)
    wer1, wer2 = error_rates(labels, predictions, "word")
    charset = D.Charset(chars)
    greedy = [charset.decode_greedy(r.argmax(-1).tolist()) for r in probs]
    report = dict(split=a.split, lines=len(stems), model=a.model, alpha=a.alpha, beta=a.beta, beam=a.beam,
                  cer_line=round(cer2, 5), wer_line=round(wer2, 5), cer_total=round(cer1, 5), wer_total=round(wer1, 5),
                  greedy_cer_line=round(error_rates(labels, greedy)[1], 5), model_ms_per_line_pc=round(model_s * 1000 / len(stems), 1))
    print(json.dumps(report, indent=1))
    json.dump(report, open(f"{a.run}/deployed_{a.split}.json", "w", encoding="utf8"), indent=1)
    with open(f"{a.run}/deployed_{a.split}_pred.txt", "w", encoding="utf8") as f:
        for t, q in zip(labels, predictions):
            f.write(t + "\n" + q + "\n\n")


if __name__ == "__main__":
    main()
