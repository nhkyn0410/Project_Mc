"""Tỷ lệ lỗi theo docs/02-yeu-cau-va-danh-gia.md, mục 2."""


def edit_distance(a, b):
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (x != y)))
        previous = current
    return previous[-1]


def error_rates(truths, predictions, unit=None):
    """Trả về (công thức 1: tổng lỗi chia tổng độ dài, công thức 2: trung bình theo dòng)."""
    split = (lambda s: s.split()) if unit == "word" else (lambda s: s)
    total_errors = total_length = 0
    per_line = []
    for truth, prediction in zip(truths, predictions):
        t, p = split(truth), split(prediction)
        errors = edit_distance(t, p)
        total_errors += errors
        total_length += len(t)
        per_line.append(errors / max(1, len(t)))
    return total_errors / max(1, total_length), sum(per_line) / max(1, len(per_line))
