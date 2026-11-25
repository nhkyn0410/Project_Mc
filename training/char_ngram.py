"""Mô hình ngôn ngữ n-gram ký tự (docs/07-nhat-ky-thi-nghiem.md, mục 14).

Mỗi ký tự trong bảng ký tự của mô hình nhận dạng là một ký hiệu, cộng ba ký hiệu riêng:
ký tự lạ, đầu câu và cuối câu. Một n-gram gói thành số nguyên, mỗi ký hiệu 8 bit,
ký hiệu đầu tiên ở các bit cao, nên khóa của một ngữ cảnh là khóa bỏ 8 bit thấp.

Mô hình lưu ở dạng lùi (backoff): với mỗi n-gram đã lưu có log xác suất,
với mỗi ngữ cảnh có log trọng số lùi. Xác suất của n-gram chưa lưu bằng
trọng số lùi của ngữ cảnh nhân với xác suất theo ngữ cảnh ngắn hơn.

Tệp nhị phân cho điện thoại (little endian): "VNCL", int32 phiên bản, int32 bậc, int32 số ký tự,
các ký tự (uint16 độ dài, UTF-8), float32 bước lượng tử của log xác suất và của trọng số lùi,
rồi với mỗi bậc: int32 số n-gram, khóa int32 tăng dần (băm FNV-1a các ký hiệu),
log xác suất uint8, và trọng số lùi uint8 nếu chưa phải bậc cao nhất.
"""
import math
import struct

import numpy as np

STEP_LOGP = 0.07
STEP_BOW = 0.05


class Symbols:
    """Ký hiệu 1 đến len(chars) là các ký tự, sau đó là ký tự lạ, đầu câu, cuối câu."""

    def __init__(self, chars):
        self.chars = list(chars)
        self.index = {c: i + 1 for i, c in enumerate(self.chars)}
        self.unk = len(self.chars) + 1
        self.bos = len(self.chars) + 2
        self.eos = len(self.chars) + 3
        if self.eos > 255:
            raise ValueError("too many symbols")

    def of(self, ch):
        return self.index.get(ch, self.unk)


def pack(symbols):
    key = 0
    for s in symbols:
        key = (key << 8) | s
    return key


def fnv(symbols):
    h = 2166136261
    for s in symbols:
        h = ((h ^ s) * 16777619) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h


def unpack(keys, n):
    """Mảng khóa bậc n thành ma trận ký hiệu (số n-gram, n)."""
    keys = np.asarray(keys, np.uint64)
    return np.stack([((keys >> np.uint64(8 * (n - 1 - j))) & np.uint64(255)).astype(np.uint8) for j in range(n)], axis=1)


def fnv_array(keys, n):
    h = np.full(len(keys), 2166136261, np.uint64)
    for column in unpack(keys, n).T:
        h = ((h ^ column.astype(np.uint64)) * np.uint64(16777619)) & np.uint64(0xFFFFFFFF)
    return h.astype(np.uint32).astype(np.int32)


class _Base:
    """Phần dùng chung của bản đọc số thực và bản đọc nhị phân: tra theo lùi dần ngữ cảnh."""

    order = 0
    sym = None

    def _find(self, n, symbols):
        raise NotImplementedError

    def logp_symbols(self, context, w):
        """log P(w | context), context là bộ ký hiệu, ký hiệu gần nhất ở cuối."""
        context = tuple(context[-(self.order - 1):]) if self.order > 1 else ()
        # Ngữ cảnh dài nhất đã có trong mô hình. Ngữ cảnh chưa có thì không có n-gram nào dài hơn nó.
        start = 0
        while start < len(context) and self._find(len(context) - start, context[start:]) is None:
            start += 1
        total = 0.0
        for s in range(start, len(context) + 1):
            h = context[s:]
            hit = self._find(len(h) + 1, h + (w,))
            if hit is not None:
                return total + hit[0]
            if h:
                ctx = self._find(len(h), h)
                if ctx is not None:
                    total += ctx[1]
        return total + self.floor

    def context_of(self, text):
        """Bộ ký hiệu ngữ cảnh của một tiền tố văn bản, có ký hiệu đầu câu nếu tiền tố ngắn."""
        tail = text[-(self.order - 1):] if self.order > 1 else ""
        symbols = tuple(self.sym.of(c) for c in tail)
        if len(text) < self.order - 1:
            symbols = (self.sym.bos,) + symbols
        return symbols

    def sentence_logp(self, text):
        """Tổng log xác suất của cả câu, kể cả ký hiệu cuối câu, và số ký hiệu đã đoán."""
        context, total = (self.sym.bos,), 0.0
        for c in text:
            s = self.sym.of(c)
            total += self.logp_symbols(context, s)
            context = (context + (s,))[-(self.order - 1):]
        total += self.logp_symbols(context, self.sym.eos)
        return total, len(text) + 1


class CharNGram(_Base):
    """Bản đọc số thực từ tệp .npz của build_char_ngram.py, dùng để thử trước khi lượng tử hóa."""

    def __init__(self, path):
        z = np.load(path, allow_pickle=False)
        self.order = int(z["order"])
        self.sym = Symbols(z["chars"].tolist())
        self.keys = [None] + [z[f"keys{n}"] for n in range(1, self.order + 1)]
        self.lp = [None] + [z[f"logp{n}"] for n in range(1, self.order + 1)]
        self.bw = [None] + [z[f"bow{n}"] for n in range(1, self.order + 1)]
        self.floor = float(self.lp[1][self.lp[1] > -50].min())

    def _find(self, n, symbols):
        if n > self.order:
            return None
        keys = self.keys[n]
        key = pack(symbols)
        i = int(np.searchsorted(keys, np.uint64(key)))
        if i < len(keys) and int(keys[i]) == key:
            return float(self.lp[n][i]), float(self.bw[n][i])
        return None

    def size(self):
        return sum(len(self.keys[n]) for n in range(1, self.order + 1))


def write(npz_path, out_path):
    """Ghi tệp nhị phân cho điện thoại từ tệp .npz."""
    z = np.load(npz_path, allow_pickle=False)
    order = int(z["order"])
    chars = z["chars"].tolist()
    with open(out_path, "wb") as f:
        f.write(b"VNCL" + struct.pack("<iii", 1, order, len(chars)))
        for c in chars:
            raw = c.encode("utf8")
            f.write(struct.pack("<H", len(raw)) + raw)
        f.write(struct.pack("<ff", STEP_LOGP, STEP_BOW))
        for n in range(1, order + 1):
            keys = fnv_array(z[f"keys{n}"], n)
            sort = np.argsort(keys, kind="stable")
            q_logp = np.clip(np.rint(-z[f"logp{n}"] / STEP_LOGP), 0, 255).astype(np.uint8)
            q_bow = np.clip(np.rint(-z[f"bow{n}"] / STEP_BOW), 0, 255).astype(np.uint8)
            f.write(struct.pack("<i", len(keys)) + keys[sort].astype("<i4").tobytes())
            f.write(q_logp[sort].tobytes())
            if n < order:
                f.write(q_bow[sort].tobytes())


class CharNGramBin(_Base):
    """Bản đọc tham chiếu của tệp nhị phân, bản Kotlin phải cho cùng kết quả."""

    def __init__(self, path):
        data = open(path, "rb").read()
        if data[:4] != b"VNCL":
            raise ValueError("bad magic")
        _, self.order, n_chars = struct.unpack_from("<iii", data, 4)
        pos, chars = 16, []
        for _ in range(n_chars):
            length = struct.unpack_from("<H", data, pos)[0]
            chars.append(data[pos + 2 : pos + 2 + length].decode("utf8"))
            pos += 2 + length
        self.sym = Symbols(chars)
        step_logp, step_bow = struct.unpack_from("<ff", data, pos); pos += 8
        self.keys, self.lp, self.bw = [None], [None], [None]
        for n in range(1, self.order + 1):
            count = struct.unpack_from("<i", data, pos)[0]; pos += 4
            # Chép ra mảng mới để khóa thẳng hàng bộ nhớ, tra nhanh hơn nhiều so với đọc thẳng từ vị trí lẻ.
            self.keys.append(np.frombuffer(data, "<i4", count, pos).astype(np.int32)); pos += 4 * count
            self.lp.append(-np.frombuffer(data, np.uint8, count, pos).astype(np.float64) * step_logp); pos += count
            if n < self.order:
                self.bw.append(-np.frombuffer(data, np.uint8, count, pos).astype(np.float64) * step_bow); pos += count
            else:
                self.bw.append(np.zeros(count))
        self.floor = -255 * step_logp

    def _find(self, n, symbols):
        if n > self.order:
            return None
        keys = self.keys[n]
        key = fnv(symbols)
        # Khóa phải cùng kiểu int32 với mảng, nếu không numpy chép cả mảng sang int64 ở mỗi lần tra.
        i = int(np.searchsorted(keys, np.int32(key)))
        if i < len(keys) and int(keys[i]) == key:
            return float(self.lp[n][i]), float(self.bw[n][i])
        return None


def load(path):
    return CharNGram(path) if path.endswith(".npz") else CharNGramBin(path)


def bits_per_char(lm, sentences):
    total = count = 0
    for s in sentences:
        lp, n = lm.sentence_logp(s)
        total += lp
        count += n
    return -total / count / math.log(2)
