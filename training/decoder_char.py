"""Beam search CTC kết hợp n-gram âm tiết và n-gram ký tự (docs/07-nhat-ky-thi-nghiem.md, mục 14).

Đây là bản thử sau khi chốt cấu hình, không thay decoder.py. Khi không có n-gram ký tự,
CharDecoder cho kết quả giống hệt Decoder. Có hai cách dùng n-gram ký tự:

- joint: mỗi ký tự, kể cả khoảng trắng, được cộng alpha_c nhân log xác suất theo n-gram ký tự
  và gamma_c. Khi kết thúc, chuỗi được cộng thêm alpha_c nhân log xác suất của ký hiệu cuối câu.
  N-gram âm tiết vẫn chấm mỗi âm tiết khi âm tiết kết thúc, như Decoder.
- lookahead: chỉ các ký tự của âm tiết đang viết dở được chấm theo n-gram ký tự.
  Khi âm tiết kết thúc, phần điểm này bị trừ đi và thay bằng điểm n-gram âm tiết.
"""
import numpy as np

from decoder import NEG, Decoder, _add

EOS = -1


class CharDecoder(Decoder):
    def __init__(self, chars, lm=None, alpha=0.5, beta=0.0, clm=None, alpha_c=0.0, gamma_c=0.0, mode="joint",
                 beam=30, top_chars=8, min_prob=0.002, cache=None):
        super().__init__(chars, lm, alpha, beta, beam, top_chars, min_prob)
        if mode not in ("joint", "lookahead"):
            raise ValueError(mode)
        self.clm, self.alpha_c, self.gamma_c, self.mode = clm, alpha_c, gamma_c, mode
        if clm is not None:
            self.n1 = clm.order - 1
            self.label_sym = [clm.sym.of(c) for c in chars]
        self.cache = {} if cache is None else cache

    def _char_lp(self, prefix, k):
        """log P của nhãn k (hoặc ký hiệu cuối câu) sau tiền tố, theo n-gram ký tự."""
        tail = prefix[-self.n1:] if len(prefix) >= self.n1 else "\x00" + prefix
        key = (tail, k)
        value = self.cache.get(key)
        if value is None:
            symbol = self.clm.sym.eos if k == EOS else self.label_sym[k]
            value = self.clm.logp_symbols(self.clm.context_of(prefix), symbol)
            if len(self.cache) > 1_000_000:
                self.cache.clear()
            self.cache[key] = value
        return value

    def decode(self, probs, keep=3):
        if self.clm is None:
            return super().decode(probs, keep)
        lookahead = self.mode == "lookahead"
        log_probs = np.log(np.clip(probs, 1e-12, 1.0))
        # Trạng thái: (điểm ngôn ngữ, a, b, âm tiết đang viết, điểm ký tự của âm tiết đang viết).
        beam = {"": (0.0, NEG, (0.0, -1, -1, "", 0.0))}
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
                    c = self.alpha_c * self._char_lp(prefix, k) + self.gamma_c
                    if k == self.space:
                        word = self._word_score(state[:4])
                        score = word[0] - state[4] if lookahead else word[0] + c
                        new_state = (score, word[1], word[2], "", 0.0)
                    else:
                        new_state = (state[0] + c, state[1], state[2], state[3] + ch, state[4] + c if lookahead else 0.0)
                    update(prefix + ch, NEG, base + float(lp[k]), new_state)
            ranked = sorted(nxt.items(), key=lambda kv: _add(kv[1][0], kv[1][1]) + kv[1][2][0], reverse=True)
            beam = dict(ranked[: self.beam])
        finals = []
        for prefix, (lb, lnb, state) in beam.items():
            score = self._word_score(state[:4])[0]
            score = score - state[4] if lookahead else score + self.alpha_c * self._char_lp(prefix, EOS)
            finals.append((_add(lb, lnb) + score, prefix.strip()))
        finals.sort(reverse=True)
        return finals[:keep]
