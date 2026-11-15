"""Tạo một tệp thu-net/1 tổng hợp để kiểm tra đường đi của eval_selfcollected.py."""
import json
import sys

import numpy as np


def word(x, y, w, h):
    t = np.linspace(0, 1, 30)
    return np.stack([x + w * t, y + h / 2 * np.sin(t * 12)], axis=1)


def stroke(points):
    return {"pointerType": "touch", "view": [0, 0], "points": [[float(x), float(y), 0, 0.5, 0, 0] for x, y in points]}


def main(out):
    session = dict(schema="thu-net/1", participant="P01", input="touch", device=dict(pxPerMm=16.0), lines=[])
    text = "một hai ba bốn năm sáu"
    row = 160.0
    strokes = [stroke(word(40 + i * 150.0, 14 + row * (i // 3 + 0.5), 110, 50)) for i in range(6)]
    session["lines"].append(dict(condition="broken", text=text, rowHeightMm=10, strokes=strokes, frame=dict(type="ruled", topPad=14, rowPx=row)))
    strokes = [stroke(word(40 + i * 150.0, 100, 110, 50)) for i in range(6)]
    session["lines"].append(dict(condition="continuous", text=text, rowHeightMm=None, strokes=strokes, frame=dict(type="scroll", topPad=14, bandPx=256)))
    with open(out, "w", encoding="utf8") as f:
        json.dump(session, f, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1])
