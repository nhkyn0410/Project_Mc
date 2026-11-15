"""Mô hình ngôn ngữ n-gram âm tiết (docs/ly-thuyet/06-beam-search-va-n-gram.md).

Làm trơn bằng stupid backoff, vì cách này chỉ cần tra bảng đếm và dễ viết lại bằng Kotlin.
"""
import math
import re

import numpy as np

_NOT_WORD = re.compile(r"[^\w]")
_DIGIT = re.compile(r"\d")
BACKOFF = 0.4


def token(raw):
    """Đưa một đoạn tách theo khoảng trắng về dạng tra n-gram, trả về '' nếu chỉ có dấu câu."""
    t = _NOT_WORD.sub("", raw).lower()
    return "<số>" if _DIGIT.search(t) else t


class NGram:
    def __init__(self, path):
        z = np.load(path, allow_pickle=False)
        self.vocab = {w: i for i, w in enumerate(z["vocab"].tolist())}
        self.total = float(z["total"])
        self.uni = z["uni"]
        self.bi = dict(zip(z["bi_key"].tolist(), z["bi_count"].tolist()))
        self.tri = dict(zip(z["tri_key"].tolist(), z["tri_count"].tolist()))
        self.floor = math.log(0.5 / self.total)

    def wid(self, t):
        return self.vocab.get(t, -1)

    def logp(self, w, b=-1, a=-1):
        """log P(w | a, b). Âm tiết ngoài từ vựng nhận giá trị sàn."""
        if w < 0:
            return self.floor
        if a >= 0 and b >= 0:
            bigram = self.bi.get((a << 20) | b)
            trigram = self.tri.get((((a << 20) | b) << 20) | w)
            if trigram and bigram:
                return math.log(trigram / bigram)
            penalty = math.log(BACKOFF)
        else:
            penalty = 0.0
        if b >= 0:
            bigram = self.bi.get((b << 20) | w)
            if bigram:
                return penalty + math.log(bigram / max(1.0, float(self.uni[b])))
            penalty += math.log(BACKOFF)
        return penalty + math.log(max(0.5, float(self.uni[w])) / self.total)
