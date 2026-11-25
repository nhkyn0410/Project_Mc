"""Thử n-gram ký tự trên tập kiểm định VNOnDB và nhóm chỉnh (docs/07-nhat-ky-thi-nghiem.md, mục 14).

Chỉ dùng tập kiểm định và 9 buổi của nhóm chỉnh, không chạy tập kiểm thử và tập đánh giá.
Bước probs chạy mô hình float16 một lần và lưu xác suất đầu ra vào --cache.
Dòng của nhóm chỉnh được vẽ như ứng dụng, độ dày nét 1,2, bỏ các dòng chép khác đề.

    python eval_char_lm.py probs --chinh ~/vnhw/data/nhom-chinh
    python eval_char_lm.py grid --clm c7.npz --mode joint --alpha-c 0.1 0.2 --gamma-c 0 1 --tag joint-c7
    python eval_char_lm.py eval --clm c7.npz --mode joint --alpha-c 0.2 --gamma-c 1 --tag joint-c7
"""
import argparse
import glob
import itertools
import json
import multiprocessing as mp
import os
import time

import numpy as np

import data as D
from char_ngram import load
from decoder_char import CharDecoder
from lm_binary import NGramBin
from metrics import error_rates

_G = {}
GROUPS = ("liền", "ngắt, ghép")


def chinh_lines(folder, config):
    review = json.load(open(f"{folder}/review.json", encoding="utf8"))
    miscopied = {(r["participant"], r["index"]) for r in review["lines"] if r.get("miscopied")}
    import ink

    items = []
    for path in sorted(glob.glob(f"{folder}/*.json")):
        if path.endswith("review.json"):
            continue
        obj = json.load(open(path, encoding="utf8"))
        for s in obj.get("sessions", [obj]):
            for line in s["lines"]:
                if not line.get("strokes") or line.get("review", {}).get("miscopied") or (s["participant"], line["index"]) in miscopied:
                    continue
                strokes, frame = ink.strokes_of(line), line["frame"]
                row = frame["rowPx"] if line["condition"] == "broken" else frame["bandPx"]
                image = ink.render(ink.stitch(strokes, frame["topPad"], row), config["width"], config["height"],
                                   stroke_width=ink.STROKE_WIDTH, max_ink=config.get("max_ink", 0) or 0)
                kind = GROUPS[1] if line["condition"] == "broken" else GROUPS[0]
                items.append((kind, D.normalize_label(line["text"]), image))
    return items


def probs_step(a):
    import tensorflow as tf

    config = json.load(open(f"{a.run}/config.json", encoding="utf8"))
    it = tf.lite.Interpreter(model_path=f"{a.run}/m_float16.tflite", num_threads=8)
    it.allocate_tensors()
    in_i, out_i = it.get_input_details()[0]["index"], it.get_output_details()[0]["index"]

    def run(images):
        out = []
        for image in images:
            it.reset_all_variables()
            it.set_tensor(in_i, image[None, ..., None].astype(np.float32) / 255.0)
            it.invoke()
            out.append(it.get_tensor(out_i)[0].copy())
        return np.stack(out)

    os.makedirs(a.cache, exist_ok=True)
    items = chinh_lines(a.chinh, config)
    np.savez(f"{a.cache}/chinh.npz", probs=run([x[2] for x in items]), labels=np.array([x[1] for x in items]),
             kinds=np.array([x[0] for x in items]))
    data = os.path.expanduser("~/vnhw/data")
    stems = D.read_split(f"{data}/splits/val.ln")
    images = D.load_images(f"{data}/lines", stems, config["width"], config["height"], not config["no_crop"], config.get("max_ink", 0))
    labels = [D.read_label(f"{data}/lines", s) for s in stems]
    np.savez(f"{a.cache}/val.npz", probs=run(images), labels=np.array(labels))
    print(f"nhóm chỉnh {len(items)} dòng, kiểm định {len(stems)} dòng", flush=True)


def _work(job):
    c, i, which = job
    kw = _G["configs"][c]
    d = CharDecoder(_G["chars"], _G["lm"] if kw["alpha"] or kw["beta"] else None, kw["alpha"], kw["beta"],
                    clm=_G["clm"] if kw["alpha_c"] or kw["gamma_c"] else None, alpha_c=kw["alpha_c"],
                    gamma_c=kw["gamma_c"], mode=kw["mode"], beam=kw["beam"], cache=_G["cache"])
    started = time.process_time()
    text = d.decode(_G[which]["probs"][i], keep=1)[0][1]
    return c, i, which, text, time.process_time() - started


def setup(a):
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    _G.update(chars=chars, lm=NGramBin(a.lm), clm=load(a.clm) if a.clm else None, cache={})
    for which in ("val", "chinh"):
        z = np.load(f"{a.cache}/{which}.npz")
        _G[which] = {k: z[k] for k in z.files}
        _G[which]["labels"] = _G[which]["labels"].tolist()


def configs(a):
    out = []
    for alpha, beta, alpha_c, gamma_c, beam in itertools.product(a.alpha, a.beta, a.alpha_c, a.gamma_c, a.beam):
        out.append(dict(mode=a.mode, alpha=alpha, beta=beta, alpha_c=alpha_c, gamma_c=gamma_c, beam=beam))
    return out


def run_jobs(a, jobs):
    with mp.get_context("fork").Pool(a.workers) as pool:
        return pool.map(_work, jobs, chunksize=4)


def score(labels, texts):
    cer1, cer2 = error_rates(labels, texts)
    wer1, wer2 = error_rates(labels, texts, "word")
    return dict(cer2=round(cer2 * 100, 2), wer2=round(wer2 * 100, 2), cer1=round(cer1 * 100, 2))


def grid_step(a):
    setup(a)
    _G["configs"] = configs(a)
    val = _G["val"]["labels"]
    subset = list(range(0, len(val), a.every))
    jobs = [(c, i, "val") for c in range(len(_G["configs"])) for i in subset]
    started = time.time()
    res = run_jobs(a, jobs)
    rows = []
    for c, kw in enumerate(_G["configs"]):
        got = {i: (t, s) for cc, i, _, t, s in res if cc == c}
        row = dict(kw, **score([val[i] for i in subset], [got[i][0] for i in subset]))
        row["cpu_s"] = round(sum(s for _, s in got.values()) / len(got), 3)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    best = min(rows, key=lambda r: r["cer2"])
    print("BEST", json.dumps(best, ensure_ascii=False), f"{len(subset)} dòng, {time.time() - started:.0f} s", flush=True)
    json.dump(dict(lines=len(subset), clm=a.clm, rows=rows), open(f"{a.cache}/grid-{a.tag}.json", "w", encoding="utf8"),
              ensure_ascii=False, indent=1)


def eval_step(a):
    setup(a)
    _G["configs"] = configs(a)
    jobs = [(c, i, w) for c in range(len(_G["configs"])) for w in ("val", "chinh") for i in range(len(_G[w]["labels"]))]
    res = run_jobs(a, jobs)
    report = []
    for c, kw in enumerate(_G["configs"]):
        texts = {w: {} for w in ("val", "chinh")}
        cpu = []
        for cc, i, w, t, s in res:
            if cc == c:
                texts[w][i] = t
                cpu.append(s)
        row = dict(kw, clm=a.clm)
        val = _G["val"]["labels"]
        row["kiểm định"] = score(val, [texts["val"][i] for i in range(len(val))])
        chinh = _G["chinh"]
        for g in GROUPS + ("gộp",):
            pick = [i for i, k in enumerate(chinh["kinds"]) if g == "gộp" or k == g]
            row[f"nhóm chỉnh, {g}"] = score([chinh["labels"][i] for i in pick], [texts["chinh"][i] for i in pick])
        row["cpu_s"] = round(sum(cpu) / len(cpu), 3)
        report.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        with open(f"{a.cache}/pred-{a.tag}-{c}.txt", "w", encoding="utf8") as f:
            for w in ("val", "chinh"):
                for i, label in enumerate(_G[w]["labels"]):
                    f.write(f"[{w}] {i}\n{label}\n{texts[w][i]}\n\n")
    json.dump(report, open(f"{a.cache}/eval-{a.tag}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)


def main():
    home = os.path.expanduser("~/vnhw")
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["probs", "grid", "eval"])
    p.add_argument("--run", default=f"{home}/runs/m1l_rr_e100")
    p.add_argument("--chinh", default=f"{home}/data/nhom-chinh")
    p.add_argument("--cache", default=f"{home}/runs/m1l_rr_e100/char-lm")
    p.add_argument("--lm", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../android/app/src/main/assets/lm.bin"))
    p.add_argument("--clm", default="")
    p.add_argument("--mode", default="joint", choices=["joint", "lookahead"])
    p.add_argument("--alpha", type=float, nargs="+", default=[0.45])
    p.add_argument("--beta", type=float, nargs="+", default=[4.0])
    p.add_argument("--alpha-c", type=float, nargs="+", default=[0.0])
    p.add_argument("--gamma-c", type=float, nargs="+", default=[0.0])
    p.add_argument("--beam", type=int, nargs="+", default=[30])
    p.add_argument("--every", type=int, default=3, help="Bước grid dùng 1 trên mỗi every dòng kiểm định")
    p.add_argument("--workers", type=int, default=11)
    p.add_argument("--tag", default="thu")
    a = p.parse_args()
    {"probs": probs_step, "grid": grid_step, "eval": eval_step}[a.step](a)


if __name__ == "__main__":
    main()
