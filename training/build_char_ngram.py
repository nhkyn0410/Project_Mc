"""Dựng n-gram ký tự từ cùng kho văn bản với n-gram âm tiết (build_ngram.py).

Kho gồm nhãn của tập huấn luyện VNOnDB và Wikipedia. Câu có cụm 8 âm tiết trùng với tập kiểm thử
hoặc với các tệp --extra-exclude bị loại. Bước đếm chỉ đọc nhãn của tập kiểm thử, không chạy mô hình.

Bước 1 đếm n-gram mọi bậc đến --order, ghi mỗi bậc một tệp counts<n>.npz trong thư mục --out.
Bước 2 ước lượng xác suất theo Kneser-Ney sửa đổi, dạng nội suy, rồi tỉa n-gram có số đếm thấp
và tính lại trọng số lùi để tổng xác suất vẫn bằng 1 (docs/07-nhat-ky-thi-nghiem.md, mục 14).

    python build_char_ngram.py count --run ~/vnhw/runs/m1l_rr_e100 --order 8 --out ~/vnhw/data/char-ngram \
        --extra-exclude ~/vnhw/data/lm_exclude.txt ../tools/thu-net/cau-de/nhom-chinh.txt ../tools/thu-net/cau-de/nhom-kiem-thu.txt
    python build_char_ngram.py estimate --counts ~/vnhw/data/char-ngram --order 7 --min-count 1 1 2 2 3 3 4 \
        --out ~/vnhw/data/char-ngram/c7.npz
"""
import argparse
import json
import math
import os
import time

import numpy as np

import data as D
from char_ngram import Symbols, bits_per_char, CharNGram
from ngram import token

SHINGLE = 8
CHUNK = 40_000_000


def shingles(tokens):
    return {" ".join(tokens[i : i + SHINGLE]) for i in range(len(tokens) - SHINGLE + 1)}


def corpus_sentences(a):
    """Câu của kho văn bản sau khi loại, theo đúng quy tắc của build_ngram.py."""
    home = os.path.expanduser("~/vnhw")
    L, S = f"{home}/data/lines", f"{home}/data/splits"
    exclude = set()
    for t in (D.read_label(L, s) for s in D.read_split(f"{S}/test.ln")):
        exclude |= shingles([x for x in map(token, t.split()) if x])
    for path in a.extra_exclude:
        for line in open(path, encoding="utf8"):
            exclude |= shingles([x for x in map(token, D.normalize_label(line).split()) if x])

    def raw():
        for s in D.read_split(f"{S}/train.ln"):
            yield D.read_label(L, s)
        yield from (x.rstrip("\n") for x in open(a.wiki, encoding="utf8"))

    kept, dropped = [], 0
    for line in raw():
        tokens = [x for x in map(token, line.split()) if x]
        if len(tokens) >= SHINGLE and shingles(tokens) & exclude:
            dropped += 1
            continue
        kept.append(line)
    return kept, dropped


def encode(sentences, sym):
    """Nối các câu thành một mảng ký hiệu: đầu câu, các ký tự, cuối câu, câu tiếp theo."""
    text = "\n".join(sentences)
    cps = np.frombuffer(text.encode("utf-32-le"), dtype="<u4")
    table = np.full(int(cps.max()) + 1, sym.unk, np.uint8)
    for c, i in sym.index.items():
        table[ord(c)] = i
    table[ord("\n")] = 0
    seq = table[cps]
    del cps
    unknown = int((seq == sym.unk).sum())
    newline = np.flatnonzero(seq == 0)
    seq[newline] = sym.eos
    seq = np.insert(seq, newline + 1, sym.bos)
    return np.concatenate([[sym.bos], seq, [sym.eos]]).astype(np.uint8), unknown


def merge(parts):
    keys = np.concatenate([k for k, _ in parts])
    counts = np.concatenate([c for _, c in parts])
    order = np.argsort(keys, kind="stable")
    keys, counts = keys[order], counts[order]
    del order
    start = np.flatnonzero(np.r_[True, keys[1:] != keys[:-1]])
    return keys[start], np.add.reduceat(counts, start)


def count(a):
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    sym = Symbols(chars)
    started = time.time()
    sentences, dropped = corpus_sentences(a)
    total_chars = sum(len(s) for s in sentences)
    print(f"sentences {len(sentences)} dropped {dropped} chars {total_chars} ({time.time() - started:.0f} s)", flush=True)
    seq, unknown = encode(sentences, sym)
    del sentences
    print(f"symbols {len(seq)} unknown chars {unknown} ({unknown / total_chars:.5f})", flush=True)
    is_bos = seq == sym.bos
    bos_before = np.cumsum(is_bos, dtype=np.int32)
    os.makedirs(a.out, exist_ok=True)
    meta = dict(sentences=len(is_bos.nonzero()[0]), dropped=dropped, chars=total_chars, unknown=unknown,
                extra_exclude=[os.path.basename(p) for p in a.extra_exclude], order=a.order)
    json.dump(meta, open(f"{a.out}/counts.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    for n in range(1, a.order + 1):
        parts = []
        last = len(seq) - n + 1
        for start in range(0, last, CHUNK):
            end = min(start + CHUNK, last)
            if n == 1:
                valid = ~is_bos[start:end]
            else:
                # Cửa sổ không được chứa ký hiệu đầu câu, trừ ở vị trí đầu tiên.
                valid = bos_before[start + n - 1 : end + n - 1] == bos_before[start:end]
            key = np.zeros(end - start, np.uint64)
            for j in range(n):
                key = (key << np.uint64(8)) | seq[start + j : end + j].astype(np.uint64)
            k, c = np.unique(key[valid], return_counts=True)
            parts.append((k, c.astype(np.int64)))
            del key, valid
        keys, counts = merge(parts)
        del parts
        np.savez(f"{a.out}/counts{n}.npz", keys=keys, counts=counts)
        print(f"order {n}: {len(keys)} n-grams, {int(counts.sum())} windows ({time.time() - started:.0f} s)", flush=True)


def discounts(adj):
    n1, n2, n3, n4 = (int((adj == k).sum()) for k in (1, 2, 3, 4))
    if min(n1, n2, n3, n4) == 0:
        return 0.5, 1.0, 1.5
    y = n1 / (n1 + 2 * n2)
    d = (1 - 2 * y * n2 / n1, 2 - 3 * y * n3 / n2, 3 - 4 * y * n4 / n3)
    return tuple(float(min(max(x, 0.05), k)) for k, x in zip((1, 2, 3), d))


def _find_all(keys, wanted):
    idx = np.searchsorted(keys, wanted)
    idx = np.minimum(idx, len(keys) - 1)
    if not np.all(keys[idx] == wanted):
        raise ValueError("missing lower-order n-gram")
    return idx


def estimate(a):
    chars = json.load(open(f"{a.run}/charset.json", encoding="utf8"))
    sym = Symbols(chars)
    N = a.order
    t = list(a.min_count) + [a.min_count[-1]] * max(0, N - len(a.min_count))
    if any(t[i] > t[i + 1] for i in range(N - 1)):
        raise ValueError("--min-count must not decrease with order")
    keys, raw = [None], [None]
    for n in range(1, N + 1):
        z = np.load(f"{a.counts}/counts{n}.npz")
        keys.append(z["keys"]); raw.append(z["counts"])

    # Số đếm điều chỉnh: bậc cao nhất dùng số đếm thật, bậc thấp hơn dùng số ký hiệu khác nhau đứng trước,
    # trừ n-gram bắt đầu bằng ký hiệu đầu câu vì không có gì đứng trước.
    adj = [None] * (N + 1)
    adj[N] = raw[N]
    for n in range(N - 1, 0, -1):
        suffix = keys[n + 1] & np.uint64((1 << (8 * n)) - 1)
        s_keys, s_count = np.unique(suffix, return_counts=True)
        cont = np.zeros(len(keys[n]), np.int64)
        cont[_find_all(keys[n], s_keys)] = s_count
        starts_bos = (keys[n] >> np.uint64(8 * (n - 1))) == sym.bos
        adj[n] = np.where(starts_bos, raw[n], cont)
        if np.any(adj[n] <= 0):
            raise ValueError(f"order {n}: n-gram without left context")

    # Bậc 1: đủ mọi ký hiệu đoán được, nội suy với phân bố đều.
    predictable = [s for s in range(1, sym.eos + 1) if s != sym.bos]
    d = discounts(adj[1])
    disc = np.select([adj[1] == 1, adj[1] == 2], [d[0], d[1]], d[2])
    total = adj[1].sum()
    gamma0 = float(disc.sum() / total)
    p1 = np.full(sym.eos + 1, gamma0 / len(predictable))
    p1[keys[1].astype(np.int64)] += (adj[1] - disc) / total
    full1 = np.arange(1, sym.eos + 1, dtype=np.uint64)
    prob = [None, p1[1:]]
    keys[1], raw[1] = full1, np.full(len(full1), np.iinfo(np.int64).max)
    prob[1][sym.bos - 1] = 0.0
    report = {"discounts": {1: d}}

    for n in range(2, N + 1):
        k, an = keys[n], adj[n]
        ctx = k >> np.uint64(8)
        starts = np.flatnonzero(np.r_[True, ctx[1:] != ctx[:-1]])
        seg = np.repeat(np.arange(len(starts)), np.diff(np.r_[starts, len(k)]))
        d = discounts(an)
        report["discounts"][n] = d
        disc = np.select([an == 1, an == 2], [d[0], d[1]], d[2])
        total = np.add.reduceat(an, starts).astype(np.float64)
        gamma = np.add.reduceat(disc, starts) / total
        lower = _find_all(keys[n - 1], k & np.uint64((1 << (8 * (n - 1))) - 1))
        prob.append((an - disc) / total[seg] + gamma[seg] * prob[n - 1][lower])

    # Tỉa theo số đếm thật, giữ n-gram có số đếm từ t[n - 1] trở lên.
    keep = [None, np.ones(len(keys[1]), bool)]
    for n in range(2, N + 1):
        keep.append(raw[n] >= t[n - 1])
    out = {"order": np.int64(N), "chars": np.array(chars)}
    bows = [np.zeros(len(keys[n]), np.float64) if n else None for n in range(N + 1)]
    for n in range(2, N + 1):
        k, p = keys[n][keep[n]], prob[n][keep[n]]
        if not len(k):
            continue
        ctx = k >> np.uint64(8)
        starts = np.flatnonzero(np.r_[True, ctx[1:] != ctx[:-1]])
        lower = _find_all(keys[n - 1], k & np.uint64((1 << (8 * (n - 1))) - 1))
        if not np.all(keep[n - 1][lower]):
            raise ValueError("pruning broke suffix closure")
        num = 1.0 - np.add.reduceat(p, starts)
        den = 1.0 - np.add.reduceat(prob[n - 1][lower], starts)
        bow = np.maximum(num, 1e-12) / np.maximum(den, 1e-12)
        where = _find_all(keys[n - 1], ctx[starts])
        if not np.all(keep[n - 1][where]):
            raise ValueError("pruning broke prefix closure")
        bows[n - 1][where] = bow
    sizes = {}
    for n in range(1, N + 1):
        kk = keep[n]
        lp = np.log(np.maximum(prob[n][kk], 1e-300))
        if n == 1:
            lp[sym.bos - 1] = -99.0
        bw = np.where(bows[n][kk] > 0, np.log(np.maximum(bows[n][kk], 1e-300)), 0.0)
        out[f"keys{n}"] = keys[n][kk]
        out[f"logp{n}"] = lp.astype(np.float32)
        out[f"bow{n}"] = bw.astype(np.float32)
        sizes[n] = int(kk.sum())
    np.savez(a.out, **out)
    entries = sum(sizes.values())
    report.update(order=N, min_count=t[:N], entries=sizes, total=entries,
                  bytes_estimate=sum(v * (5 if n == N else 6) for n, v in sizes.items()))
    lm = CharNGram(a.out)
    home = os.path.expanduser("~/vnhw/data")
    val = [D.read_label(f"{home}/lines", s) for s in D.read_split(f"{home}/splits/val.ln")]
    report["bpc_val"] = round(bits_per_char(lm, val), 4)
    if a.prompts:
        prompts = [D.normalize_label(x) for x in open(a.prompts, encoding="utf8") if x.strip()]
        report["bpc_prompts"] = round(bits_per_char(lm, prompts), 4)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    json.dump(report, open(a.out.replace(".npz", ".json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)


def main():
    home = os.path.expanduser("~/vnhw")
    p = argparse.ArgumentParser()
    p.add_argument("step", choices=["count", "estimate"])
    p.add_argument("--run", default=f"{home}/runs/m1l_rr_e100")
    p.add_argument("--wiki", default=f"{home}/data/wiki/corpus.txt")
    p.add_argument("--extra-exclude", nargs="*", default=[])
    p.add_argument("--order", type=int, default=8)
    p.add_argument("--counts", default=f"{home}/data/char-ngram")
    p.add_argument("--min-count", type=int, nargs="+", default=[1])
    p.add_argument("--prompts", default="", help="Tệp câu đề để đo số bit mỗi ký tự, mỗi dòng một câu")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    count(a) if a.step == "count" else estimate(a)


if __name__ == "__main__":
    main()
