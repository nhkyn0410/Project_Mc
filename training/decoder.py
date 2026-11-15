"""Beam search CTC kết hợp n-gram âm tiết (docs/ly-thuyet/06-beam-search-va-n-gram.md, mục 2.3)."""
import math

import numpy as np

from ngram import token

NEG = -1e9


def _add(a, b):
    if a < b:
        a, b = b, a
    return a if b < a - 30 else a + math.log1p(math.exp(b - a))


class Decoder:
    def __init__(self, chars, lm=None, alpha=0.5, beta=0.0, beam=30, top_chars=8, min_prob=0.002):
        self.chars = chars
        self.blank = len(chars)
        self.lm = lm
        self.alpha, self.beta, self.beam, self.top_chars, self.min_prob = alpha, beta, beam, top_chars, min_prob
        self.space = chars.index(" ")

    def _word_score(self, state):
        """Điểm n-gram của âm tiết vừa kết thúc. state = (điểm, a, b, âm tiết đang viết)."""
        score, a, b, current = state
        t = token(current)
        if not t:
            return score, a, b, ""
        if self.lm is None:
            return score + self.beta, a, b, ""
        w = self.lm.wid(t)
        return score + self.alpha * self.lm.logp(w, b, a) + self.beta, b, w, ""

    def decode(self, probs, keep=3):
        """probs có dạng (T, số nhãn). Trả về danh sách (điểm, chuỗi), điểm cao nhất trước."""
        log_probs = np.log(np.clip(probs, 1e-12, 1.0))
        beam = {"": (0.0, NEG, (0.0, -1, -1, ""))}  # tiền tố: (ln p_b, ln p_nb, trạng thái n-gram)
        for t in range(len(probs)):
            row = probs[t]
            order = np.argpartition(-row, self.top_chars)[: self.top_chars]
            labels = [int(k) for k in order if k != self.blank and row[k] >= self.min_prob]
            blank_lp = float(log_probs[t, self.blank])
            lp = log_probs[t]
            nxt = {}

            def update(prefix, lb, lnb, state):
                old = nxt.get(prefix)
                if old is None:
                    nxt[prefix] = (lb, lnb, state)
                else:
                    nxt[prefix] = (_add(old[0], lb), _add(old[1], lnb), old[2])

            for prefix, (lb, lnb, state) in beam.items():
                total = _add(lb, lnb)
                update(prefix, total + blank_lp, NEG, state)
                if prefix and lnb > NEG / 2:
                    update(prefix, NEG, lnb + float(lp[self._index[prefix[-1]]]), state)
                for k in labels:
                    ch = self.chars[k]
                    base = lb if prefix and self._index[prefix[-1]] == k else total
                    if base <= NEG / 2:
                        continue
                    if k == self.space:
                        new_state = self._word_score(state)
                        new_state = (new_state[0], new_state[1], new_state[2], "")
                    else:
                        new_state = (state[0], state[1], state[2], state[3] + ch)
                    update(prefix + ch, NEG, base + float(lp[k]), new_state)
            ranked = sorted(nxt.items(), key=lambda kv: _add(kv[1][0], kv[1][1]) + kv[1][2][0], reverse=True)
            beam = dict(ranked[: self.beam])
        finals = []
        for prefix, (lb, lnb, state) in beam.items():
            finals.append((_add(lb, lnb) + self._word_score(state)[0], prefix.strip()))
        finals.sort(reverse=True)
        return finals[:keep]

    @property
    def _index(self):
        if not hasattr(self, "_idx"):
            self._idx = {c: i for i, c in enumerate(self.chars)}
        return self._idx
