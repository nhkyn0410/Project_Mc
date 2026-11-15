"""Phân tích lỗi trên tệp kết quả gồm các cặp dòng: nhãn, chuỗi đọc ra, dòng trống.

Tính CER sau khi bỏ dấu (docs/02-yeu-cau-va-danh-gia.md, mục 2.3), CER theo độ dài dòng
và các cặp ký tự hay nhầm nhất.
"""
import argparse
import collections
import json
import unicodedata

from metrics import error_rates

TONES = {"̀", "́", "̃", "̉", "̣"}


def strip_tones(text):
    """Bỏ sắc, huyền, hỏi, ngã, nặng, giữ ă, â, ê, ô, ơ, ư, đ."""
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", text) if c not in TONES))


def strip_all(text):
    """Đưa về 26 chữ cái Latinh cơ bản."""
    text = text.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"))


def align(truth, prediction):
    """Trả về danh sách phép sửa (ký tự đúng, ký tự đọc ra), '' là không có ký tự."""
    n, m = len(truth), len(prediction)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (truth[i - 1] != prediction[j - 1]))
    ops, i, j = [], n, m
    while i or j:
        if i and j and d[i][j] == d[i - 1][j - 1] + (truth[i - 1] != prediction[j - 1]):
            if truth[i - 1] != prediction[j - 1]:
                ops.append((truth[i - 1], prediction[j - 1]))
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            ops.append((truth[i - 1], ""))
            i -= 1
        else:
            ops.append(("", prediction[j - 1]))
            j -= 1
    return ops


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pred")
    p.add_argument("--out", default="")
    a = p.parse_args()
    raw = open(a.pred, encoding="utf8").read().split("\n")
    truths, preds = [], []
    for i in range(0, len(raw) - 2, 3):
        truths.append(raw[i]); preds.append(raw[i + 1])
    report = dict(lines=len(truths))

    def rates(fn=lambda s: s):
        t, q = [fn(x) for x in truths], [fn(x) for x in preds]
        c1, c2 = error_rates(t, q)
        return dict(cer_total=round(c1, 5), cer_line=round(c2, 5))

    report["normal"] = rates()
    report["no_tone"] = rates(strip_tones)
    report["no_diacritic"] = rates(strip_all)
    report["tone_share_points"] = round(report["normal"]["cer_line"] - report["no_tone"]["cer_line"], 5)
    report["tone_and_diacritic_share_points"] = round(report["normal"]["cer_line"] - report["no_diacritic"]["cer_line"], 5)

    buckets = [(1, 20), (21, 40), (41, 60), (61, 80), (81, 1000)]
    by_len = []
    for low, high in buckets:
        idx = [i for i, t in enumerate(truths) if low <= len(t) <= high]
        if idx:
            c1, c2 = error_rates([truths[i] for i in idx], [preds[i] for i in idx])
            by_len.append(dict(chars=f"{low}-{high}", lines=len(idx), cer_line=round(c2, 5), cer_total=round(c1, 5)))
    report["by_length"] = by_len

    subs, dels, ins = collections.Counter(), collections.Counter(), collections.Counter()
    for t, q in zip(truths, preds):
        for x, y in align(t, q):
            if x and y:
                subs[(x, y)] += 1
            elif x:
                dels[x] += 1
            else:
                ins[y] += 1
    report["errors"] = dict(substitutions=sum(subs.values()), deletions=sum(dels.values()), insertions=sum(ins.values()))
    report["top_substitutions"] = [[f"{x}>{y}", c] for (x, y), c in subs.most_common(25)]
    report["top_deletions"] = dels.most_common(12)
    report["top_insertions"] = ins.most_common(12)
    text = json.dumps(report, ensure_ascii=False, indent=1)
    print(text)
    if a.out:
        open(a.out, "w", encoding="utf8").write(text)


if __name__ == "__main__":
    main()
