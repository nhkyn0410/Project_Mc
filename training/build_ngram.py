"""Đếm n-gram âm tiết bậc 3 từ tập huấn luyện VNOnDB và Wikipedia.

Câu có cụm 8 âm tiết trùng với tập kiểm thử bị loại khỏi kho văn bản
(docs/03-du-lieu.md, mục 5). Bước này chỉ đọc nhãn của tập kiểm thử, không chạy mô hình.
"""
import argparse
import collections
import os

import numpy as np

import data as D
from ngram import token

SHINGLE = 8


def shingles(tokens):
    return {" ".join(tokens[i : i + SHINGLE]) for i in range(len(tokens) - SHINGLE + 1)}


def merge(key_a, count_a, key_b, count_b):
    keys = np.concatenate([key_a, key_b])
    counts = np.concatenate([count_a, count_b])
    unique, inverse = np.unique(keys, return_inverse=True)
    summed = np.zeros(len(unique), np.int64)
    np.add.at(summed, inverse, counts)
    return unique, summed


def main():
    home = os.path.expanduser("~/vnhw")
    p = argparse.ArgumentParser()
    p.add_argument("--wiki", default=f"{home}/data/wiki/corpus.txt")
    p.add_argument("--no-wiki", action="store_true")
    p.add_argument("--vocab", type=int, default=30000)
    p.add_argument("--min-bi", type=int, default=3)
    p.add_argument("--min-tri", type=int, default=4)
    p.add_argument("--out", default=f"{home}/data/ngram.npz")
    p.add_argument("--extra-exclude", default="", help="Tệp câu cần loại, mỗi dòng một câu")
    a = p.parse_args()

    L, S = f"{home}/data/lines", f"{home}/data/splits"
    exclude = set()
    test_labels = [D.read_label(L, s) for s in D.read_split(f"{S}/test.ln")]
    for t in test_labels:
        exclude |= shingles([x for x in map(token, t.split()) if x])
    if a.extra_exclude:
        for line in open(a.extra_exclude, encoding="utf8"):
            exclude |= shingles([x for x in map(token, D.normalize_label(line).split()) if x])

    def corpus():
        for s in D.read_split(f"{S}/train.ln"):
            yield D.read_label(L, s)
        if not a.no_wiki:
            yield from open(a.wiki, encoding="utf8")

    counter = collections.Counter()
    sentences = dropped = 0
    for line in corpus():
        tokens = [x for x in map(token, line.split()) if x]
        if exclude and len(tokens) >= SHINGLE and shingles(tokens) & exclude:
            dropped += 1
            continue
        counter.update(tokens)
        sentences += 1
    vocab = [w for w, _ in counter.most_common(a.vocab)]
    ids = {w: i for i, w in enumerate(vocab)}
    total = sum(counter.values())
    print(f"sentences {sentences} dropped {dropped} tokens {total} types {len(counter)} vocab {len(vocab)}", flush=True)
    covered = sum(counter[w] for w in vocab) / total
    print(f"vocab coverage {covered:.4f}", flush=True)

    uni = np.array([counter[w] for w in vocab], np.int64)
    bi_k, bi_c = np.array([], np.int64), np.array([], np.int64)
    tri_k, tri_c = np.array([], np.int64), np.array([], np.int64)
    buf_b, buf_t = [], []

    def flush():
        nonlocal bi_k, bi_c, tri_k, tri_c
        if buf_b:
            k, c = np.unique(np.array(buf_b, np.int64), return_counts=True)
            bi_k, bi_c = merge(bi_k, bi_c, k, c)
        if buf_t:
            k, c = np.unique(np.array(buf_t, np.int64), return_counts=True)
            tri_k, tri_c = merge(tri_k, tri_c, k, c)
        buf_b.clear(); buf_t.clear()

    for line in corpus():
        tokens = [x for x in map(token, line.split()) if x]
        if exclude and len(tokens) >= SHINGLE and shingles(tokens) & exclude:
            continue
        w = [ids.get(t, -1) for t in tokens]
        for i in range(len(w)):
            if i >= 1 and w[i - 1] >= 0 and w[i] >= 0:
                buf_b.append((w[i - 1] << 20) | w[i])
                if i >= 2 and w[i - 2] >= 0:
                    buf_t.append((((w[i - 2] << 20) | w[i - 1]) << 20) | w[i])
        if len(buf_t) >= 20_000_000:
            flush()
    flush()
    keep_b, keep_t = bi_c >= a.min_bi, tri_c >= a.min_tri
    print(f"bigrams {len(bi_k)} kept {keep_b.sum()}, trigrams {len(tri_k)} kept {keep_t.sum()}", flush=True)
    np.savez_compressed(a.out, vocab=np.array(vocab), total=total, uni=uni,
                        bi_key=bi_k[keep_b], bi_count=bi_c[keep_b], tri_key=tri_k[keep_t], tri_count=tri_c[keep_t])
    print("saved", a.out, round(os.path.getsize(a.out) / 1e6, 1), "MB", flush=True)


if __name__ == "__main__":
    main()
