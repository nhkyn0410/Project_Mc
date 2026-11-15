"""Đọc bản dump Wikipedia tiếng Việt từ stdin, ghi văn bản đã làm sạch.

Dùng:
    curl -sL -A vnhw-research/0.1 <url .bz2> | python wiki_extract.py --out ~/vnhw/data/wiki

Cứ 50 bài lấy 1 bài vào prompts.txt để làm nguồn câu đề của tập tự thu.
Các bài đó không được dùng để học n-gram (docs/03-du-lieu.md, mục 5 và mục 6).
"""
import argparse
import bz2
import html
import os
import re
import sys

import data as D

TAG_TEXT = re.compile(r"<text\b[^>]*>(.*?)</text>", re.S)
TAG_TITLE = re.compile(r"<title>(.*?)</title>", re.S)
SENT = re.compile(r"(?<=[.!?])\s+")
COMMENT = re.compile(r"<!--.*?-->", re.S)
REF = re.compile(r"<ref\b[^>]*?/>|<ref\b.*?</ref>", re.S)
ANY_TAG = re.compile(r"<[^>]+>")
TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
TABLE = re.compile(r"\{\|.*?\|\}", re.S)
FILE_LINK = re.compile(r"\[\[(?:Tập tin|Hình|File|Image|Thể loại|Category)[^\[\]]*(?:\[\[[^\[\]]*\]\][^\[\]]*)*\]\]", re.I)
LINK = re.compile(r"\[\[(?:[^\[\]|]*\|)?([^\[\]]*)\]\]")
EXT = re.compile(r"\[https?://\S+\s*([^\]]*)\]")
HEADING = re.compile(r"^=+.*?=+\s*$", re.M)
LIST_LINE = re.compile(r"^[*#:;|!].*$", re.M)
VIETNAMESE = re.compile(r"[ăâđêôơưáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ]", re.I)


def clean(text):
    text = html.unescape(text)
    text = COMMENT.sub(" ", text)
    text = REF.sub(" ", text)
    for _ in range(6):
        text, n = TEMPLATE.subn(" ", text)
        if not n:
            break
    text = TABLE.sub(" ", text)
    text = FILE_LINK.sub(" ", text)
    text = LINK.sub(r"\1", text)
    text = EXT.sub(r"\1", text)
    text = ANY_TAG.sub(" ", text)
    text = HEADING.sub("\n", text)
    text = LIST_LINE.sub("\n", text)
    return text.replace("'''", "").replace("''", "")


def sentences(text):
    for paragraph in text.split("\n"):
        for s in SENT.split(paragraph):
            s = D.normalize_label(s)
            tokens = s.split()
            if 5 <= len(tokens) <= 60 and VIETNAMESE.search(s):
                yield s


def pages(stream):
    d = bz2.BZ2Decompressor()
    buffer = ""
    decoder = __import__("codecs").getincrementaldecoder("utf8")("ignore")
    while True:
        chunk = stream.read(1 << 20)
        if not chunk:
            return
        if d.eof:
            rest = d.unused_data
            d = bz2.BZ2Decompressor()
            chunk = rest + chunk
        buffer += decoder.decode(d.decompress(chunk))
        while True:
            end = buffer.find("</page>")
            if end < 0:
                break
            yield buffer[buffer.find("<page>") : end]
            buffer = buffer[end + 7 :]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--max-mb", type=int, default=300)
    p.add_argument("--min-chars", type=int, default=2000)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    limit, written, kept, seen = a.max_mb * 1_000_000, 0, 0, 0
    with open(f"{a.out}/corpus.txt", "w", encoding="utf8") as corpus, open(f"{a.out}/prompts.txt", "w", encoding="utf8") as prompts:
        for page in pages(sys.stdin.buffer):
            seen += 1
            if "<ns>0</ns>" not in page or "<redirect" in page:
                continue
            match = TAG_TEXT.search(page)
            if not match:
                continue
            text = clean(match.group(1))
            # Bỏ các bài ngắn, phần lớn là bài do bot sinh hàng loạt.
            if len(text) < a.min_chars:
                continue
            kept += 1
            is_prompt = kept % 50 == 0
            title = html.unescape(TAG_TITLE.search(page).group(1)) if is_prompt else ""
            target = prompts if is_prompt else corpus
            for s in sentences(text):
                # Tệp câu đề ghi kèm tên bài để ghi nguồn theo giấy phép của Wikipedia.
                target.write((f"{title}\t{s}" if is_prompt else s) + "\n")
                written += len(s.encode("utf8")) + 1
            if kept % 5000 == 0:
                print(f"pages {seen} kept {kept} MB {written / 1e6:.0f}", flush=True)
            if written >= limit:
                break
    print(f"DONE pages {seen} kept {kept} MB {written / 1e6:.0f}", flush=True)


if __name__ == "__main__":
    main()
