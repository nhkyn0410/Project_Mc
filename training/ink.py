"""Lớp ghép đoạn và bước vẽ dòng thành ảnh (docs/01-mo-ta-de-tai.md, mục 7.1 và docs/03-du-lieu.md, mục 3.2).

Nét là mảng numpy (số điểm, 2) gồm x, y theo tọa độ khung viết. Bản Kotlin phải cho cùng kết quả.
"""
import numpy as np

from data import MARGIN

SUPERSAMPLE = 4
STROKE_WIDTH = 1.2  # Độ dày nét trên khung cuối, cho CER thấp nhất khi vẽ lại ảnh kiểm định, chỉnh lại trên nhóm chỉnh
BODY_GUESS = 0.35  # Chiều cao thân chữ dự đoán ở lượt gán đầu, tính theo chiều cao hàng
BODY_LIMITS = (0.6, 1.5)  # Ở lượt đầu, chiều cao thân chữ của dòng đang viết được kẹp trong khoảng này nhân giá trị dự đoán
NEW_LINE_DROP = 1.2  # Tâm nét thấp hơn đường chân chữ quá chừng này lần chiều cao thân chữ thì mở dòng mới
DESCENDER_DROP = 0.5  # Tâm nét thấp hơn đường chân chữ quá chừng này và nét lùi về trái thì cũng mở dòng mới
RETURN_SHIFT = 2.0  # Độ lùi về trái của điểm đầu nét so với mép phải của dòng, tính theo chiều cao thân chữ
FLAT = 0.4  # Nét thấp hơn chừng này lần chiều cao thân chữ, như dấu chấm, dấu nặng, gạch ngang, không được mở dòng mới
UP_RETURN = 1.2  # Tâm nét cao hơn đỉnh thân chữ quá chừng này thì xét gán về một dòng trước
MAX_GAP = 2.0  # Khoảng trống ngang rộng hơn chừng này lần chiều cao thân chữ bị thu về GAP_RATIO
GAP_RATIO = 0.7  # Khoảng cách chèn giữa hai đoạn, tính theo chiều cao thân chữ
SCALE_LIMITS = (0.7, 1.4)
STRAY_GAP = 2.0  # Nét cách dải thân chữ theo chiều dọc xa hơn chừng này lần chiều cao thân chữ là nét lạc (docs/07, mục 10.15 đến mục 10.17)
STRAY_TALL = 5.0  # Nét cao hơn chừng này lần chiều cao thân chữ là nét quẹt nhầm


def _body(points):
    """Trả về (đỉnh thân chữ, đường chân chữ, chiều cao thân chữ) theo phân vị tọa độ y."""
    top, base = np.percentile(points[:, 1], [15, 85])
    return top, base, max(1.0, base - top)


def _segment(strokes, h_ref, adapt):
    """Một lượt gán nét vào dòng chữ theo thứ tự viết.

    adapt đúng: chiều cao thân chữ lấy theo dòng đang viết, kẹp trong BODY_LIMITS nhân h_ref.
    adapt sai: chiều cao thân chữ lấy bằng h_ref cho mọi dòng.
    """
    lines = []
    rows = np.zeros(len(strokes), dtype=int)
    for i, s in enumerate(strokes):
        if not lines:
            lines.append([i])
            continue
        cur = len(lines) - 1
        pts = np.concatenate([strokes[j] for j in lines[cur]])
        top, base, h = _body(pts)
        h = min(max(h, BODY_LIMITS[0] * h_ref), BODY_LIMITS[1] * h_ref) if adapt else h_ref
        cy = s[:, 1].mean()
        drop = cy - base
        flat = np.ptp(s[:, 1]) < FLAT * h
        if not flat and (drop > NEW_LINE_DROP * h or (drop > DESCENDER_DROP * h and s[:, 0].min() < pts[:, 0].max() - RETURN_SHIFT * h)):
            lines.append([i])
            rows[i] = len(lines) - 1
            continue
        target = cur
        if cy < top - UP_RETURN * h and cur > 0:
            # Nét viết bổ sung cho dòng trước: chỉ xét dòng có đường chân chữ thấp hơn tâm nét,
            # rồi chọn dòng có đỉnh thân chữ gần tâm nét hơn dòng đang viết.
            nearest = top - cy
            for k in range(cur):
                t, b, _ = _body(np.concatenate([strokes[j] for j in lines[k]]))
                if cy > b:
                    continue
                d = max(t - cy, 0.0)
                if d < nearest:
                    target, nearest = k, d
        lines[target].append(i)
        rows[i] = target
    return rows


def assign_rows(strokes, top_pad, row_px):
    """Gán mỗi nét vào một dòng chữ theo thứ tự viết (docs/04-thiet-ke-he-thong.md, mục 2.1).

    Người viết đi hết hàng này mới sang hàng sau, nên dòng chữ mới bắt đầu khi tâm nét xuống thấp hẳn
    dưới đường chân chữ của dòng đang viết, hoặc xuống thấp và lùi về bên trái. Chân chữ và nét dấu
    viết ngay sau chữ của chúng nên ở lại dòng đang viết. Lượt đầu dùng chiều cao thân chữ của dòng
    đang viết, kẹp quanh giá trị dự đoán theo chiều cao hàng. Lượt sau dùng chung cho mọi dòng trung vị
    chiều cao thân chữ của các dòng tìm được ở lượt đầu. Đường kẻ không được dùng, nên kết quả đúng
    cả khi người viết không theo đường kẻ. top_pad giữ lại để cùng chữ ký với bản Kotlin.
    """
    if not strokes:
        return np.zeros(0, dtype=int)
    rows = _segment(strokes, BODY_GUESS * row_px, True)
    heights = [_body(np.concatenate([s for s, r in zip(strokes, rows) if r == u]))[2] for u in range(rows.max() + 1)]
    return _segment(strokes, float(np.median(heights)), False)


def close_gaps(strokes, height):
    """Thu các khoảng trống ngang rộng hơn MAX_GAP lần chiều cao thân chữ về GAP_RATIO lần, giữ thứ tự nét."""
    order = sorted(range(len(strokes)), key=lambda i: strokes[i][:, 0].min())
    shift = np.zeros(len(strokes))
    right, total = None, 0.0
    for i in order:
        left = strokes[i][:, 0].min()
        if right is not None and left - right > MAX_GAP * height:
            total += left - right - GAP_RATIO * height
        shift[i] = total
        right = strokes[i][:, 0].max() if right is None else max(right, strokes[i][:, 0].max())
    return [s - np.array([shift[i], 0.0]) for i, s in enumerate(strokes)]


def stitch_rows(groups):
    """Nối các nhóm nét, mỗi nhóm một dòng chữ, thành dòng ảo: cùng cỡ chữ, cùng đường chân chữ, khoảng cách chuẩn."""
    bodies = [_body(np.concatenate(g)) for g in groups]
    groups = [close_gaps(g, b[2]) for g, b in zip(groups, bodies)]
    target = float(np.median([b[2] for b in bodies]))
    out, cursor = [], 0.0
    for group, (_, base, height) in zip(groups, bodies):
        scale = float(np.clip(target / height, *SCALE_LIMITS))
        left = min(s[:, 0].min() for s in group)
        right = max(s[:, 0].max() for s in group)
        for s in group:
            moved = s.astype(np.float64, copy=True)
            moved[:, 0] = cursor + (s[:, 0] - left) * scale
            moved[:, 1] = (s[:, 1] - base) * scale
            out.append(moved)
        cursor += (right - left) * scale + GAP_RATIO * target
    return out


def _gap(stroke, body):
    """Khoảng cách theo chiều dọc từ nét tới dải thân chữ, tính theo chiều cao thân chữ, bằng 0 nếu nét chạm dải."""
    top, base, h = body
    return max(top - stroke[:, 1].max(), stroke[:, 1].min() - base, 0.0) / h


def clean_rows(groups):
    """Bỏ nét lạc sau khi gán nét vào dòng chữ (docs/07-nhat-ky-thi-nghiem.md, mục 10.17).

    Nét cao hơn STRAY_TALL lần chiều cao thân chữ bị bỏ. Nét cách dải thân chữ của mọi dòng xa hơn STRAY_GAP lần
    chiều cao thân chữ của dòng đó cũng bị bỏ. Các nét khác giữ ở dòng đã gán, không chuyển dòng.
    Dải thân chữ tính theo phân vị nên vài nét lạc không kéo lệch được nó. Nếu luật bỏ hết nét thì giữ nguyên.
    """
    bodies = [_body(np.concatenate(g)) for g in groups]
    out = [[] for _ in groups]
    for u, group in enumerate(groups):
        for s in group:
            if np.ptp(s[:, 1]) > STRAY_TALL * bodies[u][2]:
                continue
            if min(_gap(s, b) for b in bodies) <= STRAY_GAP:
                out[u].append(s)
    out = [g for g in out if g]
    return out or groups


def stitch(strokes, top_pad, row_px, strays=False):
    """Gán nét vào dòng chữ, bỏ nét lạc nếu strays đúng, rồi nối các dòng chữ thành dòng ảo.

    Bộ lọc nét lạc tắt theo mặc định vì không đạt tiêu chí ghi trước (docs/07-nhat-ky-thi-nghiem.md, mục 10.17).
    """
    rows = assign_rows(strokes, top_pad, row_px)
    if not len(rows):
        return []
    groups = [[s for s, r in zip(strokes, rows) if r == u] for u in range(rows.max() + 1)]
    groups = [g for g in groups if g]
    if strays:
        groups = clean_rows(groups)
    return stitch_rows(groups)


def render(strokes, width=512, height=64, stroke_width=STROKE_WIDTH, max_ink=0):
    """Vẽ nét thành ảnh uint8 nền 0, theo cùng cách đặt vào khung của data.preprocess."""
    all_points = np.concatenate(strokes)
    mins = all_points.min(0)
    extent = np.maximum(all_points.max(0) - mins, 1.0)
    scale = min((width - 2 * MARGIN - stroke_width) / extent[0], ((max_ink or height) - stroke_width) / extent[1])
    new_h = extent[1] * scale
    k = SUPERSAMPLE
    grid = np.zeros((height * k, width * k), dtype=bool)
    radius = stroke_width * k / 2.0
    offset = np.array([MARGIN + stroke_width / 2, (height - new_h) / 2])
    for s in strokes:
        xy = ((s - mins) * scale + offset) * k
        if len(xy) == 1:
            _stamp(grid, xy[0], xy[0], radius)
        for a, b in zip(xy[:-1], xy[1:]):
            _stamp(grid, a, b, radius)
    counts = grid.reshape(height, k, width, k).sum(axis=(1, 3))
    return ((counts * 255 + k * k // 2) // (k * k)).astype(np.uint8)


def _stamp(grid, a, b, radius):
    """Đánh dấu các ô có tâm cách đoạn thẳng ab không quá radius. Bản Kotlin dùng đúng phép tính này."""
    h, w = grid.shape
    x0 = max(0, int(np.floor(min(a[0], b[0]) - radius)))
    x1 = min(w - 1, int(np.ceil(max(a[0], b[0]) + radius)))
    y0 = max(0, int(np.floor(min(a[1], b[1]) - radius)))
    y1 = min(h - 1, int(np.ceil(max(a[1], b[1]) + radius)))
    if x1 < x0 or y1 < y0:
        return
    xs = np.arange(x0, x1 + 1) + 0.5
    ys = np.arange(y0, y1 + 1)[:, None] + 0.5
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy
    if length2 == 0.0:
        t = 0.0
    else:
        t = np.clip(((xs - a[0]) * dx + (ys - a[1]) * dy) / length2, 0.0, 1.0)
    ex, ey = xs - (a[0] + t * dx), ys - (a[1] + t * dy)
    grid[y0 : y1 + 1, x0 : x1 + 1] |= ex * ex + ey * ey <= radius * radius


def strokes_of(line):
    """Lấy các nét của một dòng trong tệp thu-net/1, bỏ các nét bị hủy."""
    return [np.array(s["points"], np.float64)[:, :2] for s in line["strokes"] if not s.get("cancelled") and s["points"]]
