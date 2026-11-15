"""Đọc bản ảnh VNOnDB và tiền xử lý theo docs/03-du-lieu.md, mục 3."""
import json
import os
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

_NEW_TONE = re.compile(
    r"(?<![qQ])([oO])([àáảãạÀÁẢÃẠèéẻẽẹÈÉẺẼẸ])(?![\wÀ-ỹ])"
    r"|(?<![qQ])([uU])([ýỳỷỹỵÝỲỶỸỴ])(?![\wÀ-ỹ])"
)


def _old_tone(match):
    first = match.group(1) or match.group(3)
    second = match.group(2) or match.group(4)
    base, tone = unicodedata.normalize("NFD", second)
    return unicodedata.normalize("NFC", first + tone) + base


def normalize_label(text):
    """Chuẩn hóa nhãn theo 03, mục 3.1: NFC, dấu thanh kiểu cũ, khoảng trắng."""
    text = unicodedata.normalize("NFC", text)
    text = _NEW_TONE.sub(_old_tone, text)
    return " ".join(text.split())


def read_split(path):
    with open(path, encoding="utf8") as f:
        return [os.path.splitext(os.path.basename(x.strip()))[0] for x in f if x.strip()]


def read_label(lines_dir, stem):
    with open(os.path.join(lines_dir, stem + ".txt"), encoding="utf8") as f:
        return normalize_label(f.read())


MARGIN = 8  # Lề hai bên, để phép co giãn và nghiêng không đẩy nét ra khỏi khung


def preprocess(path, width, height, crop, max_ink=0):
    """Trả về ảnh uint8 cao height, rộng width, nền bằng 0, nét sáng (03, mục 3.3).

    max_ink khác 0 giới hạn chiều cao phần nét sau khi co, để dòng ngắn không bị phóng đầy khung.
    """
    with Image.open(path) as im:
        ink = 255 - np.asarray(im.convert("L"), dtype=np.uint8)
    if crop:
        ys, xs = np.where(ink > 40)
        if len(xs):
            ink = ink[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    h, w = ink.shape
    scale = min((width - 2 * MARGIN) / w, (max_ink or height) / h)
    new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
    small = np.asarray(Image.fromarray(ink).resize((new_w, new_h), Image.BILINEAR))
    canvas = np.zeros((height, width), np.uint8)
    top = (height - new_h) // 2
    canvas[top : top + new_h, MARGIN : MARGIN + new_w] = small
    return canvas


def load_images(lines_dir, stems, width, height, crop, max_ink=0):
    paths = [os.path.join(lines_dir, s + ".png") for s in stems]
    with ThreadPoolExecutor(8) as pool:
        return np.stack(list(pool.map(lambda p: preprocess(p, width, height, crop, max_ink), paths)))


class Charset:
    """Bảng ký tự. Nhãn trống của CTC là chỉ số cuối cùng."""

    def __init__(self, chars):
        self.chars = chars
        self.index = {c: i for i, c in enumerate(chars)}
        self.blank = len(chars)
        self.num_classes = len(chars) + 1

    @classmethod
    def from_labels(cls, labels):
        return cls(sorted(set("".join(labels))))

    def encode(self, text):
        return [self.index[c] for c in text]

    def decode_greedy(self, best_path):
        out, previous = [], None
        for k in best_path:
            if k != previous and k != self.blank:
                out.append(self.chars[k])
            previous = k
        return "".join(out)

    def save(self, path):
        with open(path, "w", encoding="utf8") as f:
            json.dump(self.chars, f, ensure_ascii=False)
