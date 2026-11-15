"""Kiểm tra lớp ghép đoạn và bước vẽ bằng nét tổng hợp. Chạy: python test_ink.py"""
import numpy as np

import ink
import simulate


def word(x, y, w=60.0, h=30.0):
    """Một nét lượn hình sin dài w, cao h, tâm tại (x + w / 2, y)."""
    t = np.linspace(0, 1, 40)
    return np.stack([x + w * t, y + h / 2 * np.sin(t * 12)], axis=1)


def dot(x, y):
    return np.array([[x, y], [x + 2.0, y + 1.0]])


TOP, ROW = 14.0, 100.0


def row_center(r):
    return TOP + ROW * (r + 0.5)


def test_row_assignment():
    strokes = [word(10, row_center(0)), word(100, row_center(0)), word(10, row_center(1))]
    assert ink.assign_rows(strokes, TOP, ROW).tolist() == [0, 0, 1]


def descender(x, y, length=30.0):
    """Nét chân chữ: bắt đầu ở đường chân chữ y rồi đi xuống."""
    t = np.linspace(0, 1, 20)
    return np.stack([x + 6 * np.sin(t * 3), y + length * t], axis=1)


def test_descender_crossing_the_rule_stays_with_its_word():
    # Chữ viết sát đường kẻ, chân chữ là nét riêng có tâm nằm dưới đường kẻ.
    w = word(10, 95)
    base = np.percentile(w[:, 1], 85)
    tail = descender(65, base)
    assert tail[:, 1].mean() > TOP + ROW
    strokes = [w, tail, word(100, 95), word(10, row_center(1) + 30)]
    assert ink.assign_rows(strokes, TOP, ROW).tolist() == [0, 0, 0, 1]


def test_two_text_lines_in_one_ruled_row_are_split():
    # Hàng kẻ cao 200 điểm ảnh, người viết viết hai dòng chữ trong cùng một hàng kẻ.
    strokes = [word(10, 60), word(100, 60), word(10, 130), word(100, 130)]
    assert ink.assign_rows(strokes, TOP, 200.0).tolist() == [0, 0, 1, 1]


def test_mark_of_current_line_stays():
    strokes = [word(10, row_center(0)), word(10, row_center(1)), dot(40, row_center(1) - 25)]
    assert ink.assign_rows(strokes, TOP, ROW).tolist() == [0, 1, 1]


def test_late_mark_returns_to_previous_line():
    # Dấu bổ sung cho dòng trên, viết sau khi đã sang dòng dưới.
    strokes = [word(10, row_center(0)), word(100, row_center(0)), word(10, row_center(1)), dot(40, row_center(0) - 25)]
    assert ink.assign_rows(strokes, TOP, ROW).tolist() == [0, 0, 1, 0]


def test_stray_dot_below_does_not_open_line():
    w = word(10, row_center(0))
    base = np.percentile(w[:, 1], 85)
    strokes = [w, dot(60, base + 40), word(100, row_center(0))]
    assert ink.assign_rows(strokes, TOP, ROW).tolist() == [0, 0, 0]


def test_late_dot_below_first_word_stays():
    # Dấu nặng viết sau cho từ đầu hàng: nằm dưới đường chân chữ và lùi về trái, nhưng dẹt.
    words = [word(10, row_center(0)), word(100, row_center(0)), word(190, row_center(0))]
    base = np.percentile(np.concatenate(words)[:, 1], 85)
    mark = np.array([[30.0, base + 15], [38.0, base + 15.5]])
    assert ink.assign_rows(words + [mark, word(280, row_center(0))], TOP, ROW).tolist() == [0, 0, 0, 0, 0]


def test_dense_rows_with_one_short_word_each():
    # Hàng chỉ cao khoảng 2 lần thân chữ, mỗi hàng một từ ngắn.
    strokes = [word(10, 30, 40), word(10, 80, 40), word(10, 130, 40)]
    assert ink.assign_rows(strokes, TOP, 50.0).tolist() == [0, 1, 2]


def test_high_mark_of_lower_line_stays_below_upper_baseline():
    # Dấu viết cao của dòng dưới, nằm giữa hai dòng, không bị kéo về dòng trên.
    upper, lower = word(10, row_center(0)), word(10, row_center(1))
    top = np.percentile(lower[:, 1], 15)
    mark = dot(40, top - 40)
    assert mark[:, 1].mean() > np.percentile(upper[:, 1], 85)
    assert ink.assign_rows([upper, lower, mark], TOP, ROW).tolist() == [0, 1, 1]


def test_close_gaps_shrinks_only_large_gaps():
    a, b, c = word(0, 0, 50), word(70, 0, 50), word(400, 0, 50)
    out = ink.close_gaps([a, b, c], 30.0)
    assert np.allclose(out[0], a) and np.allclose(out[1], b)
    assert abs(out[2][:, 0].min() - out[1][:, 0].max() - ink.GAP_RATIO * 30.0) < 1e-9


def test_stitch_closes_scroll_gap_in_continuous_line():
    strokes = [word(0, 50, 60), word(70, 50, 60), word(600, 50, 60)]
    out = ink.stitch(strokes, TOP, ROW)
    spans = sorted((s[:, 0].min(), s[:, 0].max()) for s in out)
    assert spans[2][0] - spans[1][1] < 0.8 * ROW


def test_stitch_orders_rows_left_to_right_and_aligns_baselines():
    a, b = word(10, row_center(0), h=40), word(30, row_center(1), h=60)
    out = ink.stitch([a, b], TOP, ROW)
    assert out[0][:, 0].max() < out[1][:, 0].min()
    base = [np.percentile(s[:, 1], 85) for s in out]
    assert abs(base[0] - base[1]) < 1e-6
    heights = [np.subtract(*np.percentile(s[:, 1], [85, 15])) for s in out]
    assert abs(heights[0] - heights[1]) / heights[0] < 0.05


def test_single_row_keeps_shape():
    a = word(10, row_center(0))
    out = ink.stitch([a], TOP, ROW)
    assert np.allclose(np.diff(out[0][:, 0]), np.diff(a[:, 0]))


def test_render_shape_and_margin():
    image = ink.render([word(0, 0, 900, 40)])
    assert image.shape == (64, 512) and image.max() > 100
    assert image[:, :ink.MARGIN - 1].max() == 0 and image[:, 512 - ink.MARGIN + 1:].max() == 0


def test_render_dot_visible():
    image = ink.render([word(0, 0, 400, 40), np.array([[50.0, -40.0]])])
    assert image[:12].max() > 50


def test_max_ink_limits_short_line_height():
    image = ink.render([word(0, 0, 30, 30)], max_ink=32)
    assert (image.max(1) > 0).sum() <= 34


def test_word_gaps_finds_largest_spaces():
    strokes = [word(0, 0, 50), word(55, 0, 50), word(160, 0, 50), word(300, 0, 50)]
    assert simulate.word_gaps(strokes, 2) == [132.5, 255.0]


def test_simulated_break_is_recovered_by_row_assignment():
    rng = np.random.default_rng(3)
    strokes = [word(i * 120.0, 0, 90) for i in range(8)]
    cuts = simulate.word_gaps(strokes, 7)
    chosen = simulate.choose_cuts(cuts, 2, rng)
    placed = simulate.simulate(strokes, chosen, ROW, rng)
    rows = ink.assign_rows(placed, simulate.TOP_PAD, ROW)
    assert len(set(rows.tolist())) == 3
    assert rows.tolist() == sorted(rows.tolist())
    stitched = ink.stitch(placed, simulate.TOP_PAD, ROW)
    xs = [s[:, 0].min() for s in stitched]
    assert xs == sorted(xs)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"OK {len(tests)} tests")
