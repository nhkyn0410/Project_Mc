"""Bộ mô phỏng dòng ngắt (docs/03-du-lieu.md, mục 4).

Sinh dòng ngắt từ các nét của một dòng liền trong tập tự thu. Kết quả đi qua đúng bước
gán nét vào hàng và ghép đoạn mà ứng dụng dùng, nên lỗi gán nét cũng được tính.
"""
import numpy as np

TOP_PAD = 14.0
# Chiều cao thân chữ trên hàng ảo, tính theo chiều cao hàng. Buổi thử viết bằng bút cho khoảng 0,34,
# còn chữ viết bằng ngón tay dự kiến to hơn (docs/07-nhat-ky-thi-nghiem.md, mục 10).
BODY_RANGE = (0.35, 0.5)
SCALE_RANGE = (0.8, 1.25)
BASELINE_JITTER = 0.12  # Lệch đường chân chữ, tính theo chiều cao hàng
LEFT_JITTER = 0.5  # Lệch điểm bắt đầu đoạn, tính theo chiều cao hàng


def word_gaps(strokes, n_gaps):
    """Tìm n_gaps khoảng trống ngang lớn nhất. Trả về các hoành độ cắt, tăng dần."""
    spans = sorted((s[:, 0].min(), s[:, 0].max()) for s in strokes)
    merged = [list(spans[0])]
    for left, right in spans[1:]:
        if left <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], right)
        else:
            merged.append([left, right])
    gaps = sorted(((merged[i + 1][0] - merged[i][1], (merged[i + 1][0] + merged[i][1]) / 2.0) for i in range(len(merged) - 1)), reverse=True)
    return sorted(x for _, x in gaps[: n_gaps])


def choose_cuts(word_boundaries, n_cuts, rng):
    """Chọn n_cuts ranh giới, chia dòng thành các đoạn có độ dài gần nhau, có nhiễu nhỏ."""
    n = len(word_boundaries)
    if n == 0 or n_cuts == 0:
        return []
    targets = [(i + 1) * (n + 1) / (n_cuts + 1) - 1 + rng.uniform(-0.5, 0.5) for i in range(n_cuts)]
    chosen = sorted({int(np.clip(round(t), 0, n - 1)) for t in targets})
    return [word_boundaries[i] for i in chosen]


def simulate(strokes, cuts, row_px, rng, top_pad=TOP_PAD):
    """Đặt các đoạn của dòng lên các hàng của khung kẻ ảo. Trả về nét theo thứ tự viết."""
    edges = [-np.inf] + list(cuts) + [np.inf]
    body = float(np.subtract(*np.percentile(np.concatenate(strokes)[:, 1], [85, 15])))
    fit = rng.uniform(*BODY_RANGE) * row_px / max(body, 1.0)
    out = []
    for row in range(len(edges) - 1):
        group = [s for s in strokes if edges[row] <= s[:, 0].mean() < edges[row + 1]]
        if not group:
            continue
        points = np.concatenate(group)
        left = points[:, 0].min()
        base = np.percentile(points[:, 1], 85)
        scale = fit * rng.uniform(*SCALE_RANGE)
        target_base = top_pad + row_px * (row + 0.72) + rng.uniform(-BASELINE_JITTER, BASELINE_JITTER) * row_px
        start = rng.uniform(0.2, 0.2 + LEFT_JITTER) * row_px
        for s in group:
            moved = np.empty_like(s, dtype=np.float64)
            moved[:, 0] = start + (s[:, 0] - left) * scale
            moved[:, 1] = target_base + (s[:, 1] - base) * scale
            out.append(moved)
    return out
