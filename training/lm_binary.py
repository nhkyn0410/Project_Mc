"""Định dạng n-gram gọn cho điện thoại và bộ đọc tham chiếu.

Bố cục tệp (little endian): "VNLM", int32 phiên bản, int32 số từ, float64 tổng số âm tiết,
rồi từ vựng (uint16 độ dài, UTF-8), uni (int32 mỗi âm tiết),
rồi int32 số cụm hai, khóa int32 tăng dần, số đếm uint8,
rồi int32 số cụm ba, khóa int32 tăng dần (băm FNV-1a), số đếm uint8.
Số đếm lưu theo thang logarit: q = round(ln(c) / ln(1,1)).
"""
import math
import struct

import numpy as np

from ngram import BACKOFF

BASE = 1.1
VOCAB_BITS = 15


def fnv3(a, b, w):
    h = 2166136261
    for v in (a, b, w):
        h = ((h ^ v) * 16777619) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h


def quantize(counts):
    return np.clip(np.rint(np.log(counts) / math.log(BASE)), 0, 255).astype(np.uint8)


def write(npz_path, out_path):
    z = np.load(npz_path, allow_pickle=False)
    vocab = z["vocab"].tolist()
    if len(vocab) >= (1 << VOCAB_BITS):
        raise ValueError("vocab too large")
    bi_a = (z["bi_key"] >> 20) & 0xFFFFF
    bi_b = z["bi_key"] & 0xFFFFF
    bi_key = ((bi_a << VOCAB_BITS) | bi_b).astype(np.int32)
    order = np.argsort(bi_key)
    tri_a = (z["tri_key"] >> 40) & 0xFFFFF
    tri_b = (z["tri_key"] >> 20) & 0xFFFFF
    tri_w = z["tri_key"] & 0xFFFFF
    # Băm từng phần tử bằng numpy, cùng công thức với fnv3.
    h = np.full(len(tri_a), 2166136261, np.uint64)
    for v in (tri_a, tri_b, tri_w):
        h = ((h ^ v.astype(np.uint64)) * np.uint64(16777619)) & np.uint64(0xFFFFFFFF)
    tri_key = h.astype(np.uint32).astype(np.int32)
    tri_order = np.argsort(tri_key, kind="stable")
    with open(out_path, "wb") as f:
        f.write(b"VNLM" + struct.pack("<iid", 1, len(vocab), float(z["total"])))
        for word in vocab:
            raw = word.encode("utf8")
            f.write(struct.pack("<H", len(raw)) + raw)
        f.write(z["uni"].astype("<i4").tobytes())
        f.write(struct.pack("<i", len(bi_key)) + bi_key[order].astype("<i4").tobytes())
        f.write(quantize(z["bi_count"])[order].tobytes())
        f.write(struct.pack("<i", len(tri_key)) + tri_key[tri_order].astype("<i4").tobytes())
        f.write(quantize(z["tri_count"])[tri_order].tobytes())


class NGramBin:
    """Bộ đọc tham chiếu, bản Kotlin phải cho cùng kết quả."""

    def __init__(self, path):
        data = open(path, "rb").read()
        if data[:4] != b"VNLM":
            raise ValueError("bad magic")
        _, n, self.total = struct.unpack_from("<iid", data, 4)
        pos, self.vocab = 20, {}
        for i in range(n):
            length = struct.unpack_from("<H", data, pos)[0]
            self.vocab[data[pos + 2 : pos + 2 + length].decode("utf8")] = i
            pos += 2 + length
        self.uni = np.frombuffer(data, "<i4", n, pos); pos += 4 * n
        count = struct.unpack_from("<i", data, pos)[0]; pos += 4
        self.bi_key = np.frombuffer(data, "<i4", count, pos); pos += 4 * count
        self.bi_q = np.frombuffer(data, np.uint8, count, pos); pos += count
        count = struct.unpack_from("<i", data, pos)[0]; pos += 4
        self.tri_key = np.frombuffer(data, "<i4", count, pos); pos += 4 * count
        self.tri_q = np.frombuffer(data, np.uint8, count, pos)
        self.floor = math.log(0.5 / self.total)
        self.bi = {int(k): int(q) for k, q in zip(self.bi_key.tolist(), self.bi_q.tolist())}
        self.tri = {int(k): int(q) for k, q in zip(self.tri_key.tolist(), self.tri_q.tolist())}

    def wid(self, t):
        return self.vocab.get(t, -1)

    def _bi(self, a, b):
        q = self.bi.get((a << VOCAB_BITS) | b)
        return None if q is None else BASE ** q

    def logp(self, w, b=-1, a=-1):
        if w < 0:
            return self.floor
        penalty = 0.0
        if a >= 0 and b >= 0:
            context = self._bi(a, b)
            q = self.tri.get(fnv3(a, b, w))
            if q is not None and context is not None:
                return min(0.0, q * math.log(BASE) - math.log(context))
            penalty = math.log(BACKOFF)
        if b >= 0:
            pair = self._bi(b, w)
            if pair is not None:
                return min(0.0, penalty + math.log(pair) - math.log(max(1.0, float(self.uni[b]))))
            penalty += math.log(BACKOFF)
        return penalty + math.log(max(0.5, float(self.uni[w])) / self.total)
