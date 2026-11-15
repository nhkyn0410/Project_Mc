"""Chọn câu đề cho tập tự thu từ các bài Wikipedia đã giữ riêng (docs/03-du-lieu.md, mục 6).

Mỗi bài lấy tối đa một câu. Nhóm chỉnh và nhóm kiểm thử dùng hai bộ câu khác nhau.
"""
import argparse
import json
import os
import random
import re

from ngram import NGram, token

BLOCK = ("giết", "chết", "tử vong", "thảm sát", "hiếp", "tự tử", "tự sát", "khủng bố", "ma túy", "đảng", "chính trị",
         "chiến tranh", "quân", "cộng sản", "tôn giáo", "tù", "bắn", "bom", "phát xít", "giao chiến", "thuốc", "nghiện",
         "kinh thánh", "thánh", "giáo hoàng", "phật", "bồ tát", "chúa", "giáo phái", "bệnh", "não", "khuất",
         "thịt người", "tình dục", "lính", "pháo", "binh", "sau đây")
ALLOWED_PUNCT = re.compile(r"^[\w\s,.]+$")
VIETNAMESE = re.compile(r"[ăâđêôơưáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ]", re.I)


def usable(sentence, charset, lm):
    tokens = sentence.split()
    if not 11 <= len(tokens) <= 15:
        return False
    if not sentence.endswith(".") or sentence.count(".") != 1 or not sentence[0].isupper():
        return False
    # Câu bị tách nhầm ở chữ viết tắt, ví dụ "Arthur C.", kết thúc bằng một chữ cái đơn.
    if len(tokens[-1]) <= 2 or tokens[-1][:-1].isupper():
        return False
    if not ALLOWED_PUNCT.match(sentence) or any(c.isdigit() for c in sentence):
        return False
    if any(c not in charset for c in sentence):
        return False
    lowered = sentence.lower()
    if any(word in lowered for word in BLOCK):
        return False
    cleaned = [token(t) for t in tokens]
    if any(lm.wid(t) < 0 or lm.uni[lm.wid(t)] < 200 for t in cleaned):
        return False
    # Câu tiếng Việt phải có nhiều âm tiết mang dấu, và ít danh từ riêng viết hoa.
    if sum(bool(VIETNAMESE.search(t)) for t in tokens) < 0.55 * len(tokens):
        return False
    return sum(t[0].isupper() for t in tokens[1:]) <= 2


def main():
    home = os.path.expanduser("~/vnhw")
    p = argparse.ArgumentParser()
    p.add_argument("--prompts", default=f"{home}/data/wiki2/prompts.txt")
    p.add_argument("--run", default=f"{home}/runs/m1_v2_clean")
    p.add_argument("--lm", default=f"{home}/data/ngram_clean.npz")
    p.add_argument("--per-set", type=int, default=20)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=11)
    a = p.parse_args()
    charset = set(json.load(open(f"{a.run}/charset.json", encoding="utf8")))
    lm = NGram(a.lm)
    by_article = {}
    total = 0
    for line in open(a.prompts, encoding="utf8"):
        title, _, sentence = line.rstrip("\n").partition("\t")
        total += 1
        if usable(sentence, charset, lm):
            by_article.setdefault(title, []).append(sentence)
    rng = random.Random(a.seed)
    titles = sorted(by_article)
    rng.shuffle(titles)
    chosen = [(t, rng.choice(by_article[t])) for t in titles[: 2 * a.per_set]]
    print(f"{total} câu, {len(by_article)} bài có câu dùng được, chọn {len(chosen)}")
    os.makedirs(a.out, exist_ok=True)
    groups = {"nhom-chinh": chosen[: a.per_set], "nhom-kiem-thu": chosen[a.per_set :]}
    for name, rows in groups.items():
        with open(os.path.join(a.out, f"{name}.txt"), "w", encoding="utf8") as f:
            f.write("\n".join(s for _, s in rows) + "\n")
    with open(os.path.join(a.out, "nguon.tsv"), "w", encoding="utf8") as f:
        f.write("nhóm\ttên bài trên Wikipedia tiếng Việt\tcâu\n")
        for name, rows in groups.items():
            for title, sentence in rows:
                f.write(f"{name}\t{title}\t{sentence}\n")


if __name__ == "__main__":
    main()
