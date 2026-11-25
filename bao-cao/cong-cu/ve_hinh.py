"""Vẽ các hình của báo cáo vào ../hinh. Chữ dùng Times New Roman, nét đen trên nền trắng.
Dùng: python ve_hinh.py <thư mục training> <tệp buổi thu .json của tập đánh giá>"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TRAINING, SESSION = sys.argv[1], sys.argv[2]
sys.path.insert(0, TRAINING)
import ink  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "hinh")
os.makedirs(OUT, exist_ok=True)
F = r"C:\Windows\Fonts\times.ttf"
FB = r"C:\Windows\Fonts\timesbd.ttf"
FI = r"C:\Windows\Fonts\timesi.ttf"
S = 3  # hệ số phóng để ảnh nét ở 300 dpi


def font(path, pt):
    return ImageFont.truetype(path, int(pt * S * 1.33))


def arrow(d, a, b, w=2, head=9, dash=False, color=(0, 0, 0)):
    (x0, y0), (x1, y1) = a, b
    if dash:
        n = int(np.hypot(x1 - x0, y1 - y0) // (8 * S))
        for k in range(n):
            if k % 2 == 0:
                t0, t1 = k / n, min(1, (k + 1) / n)
                d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=color, width=w * S)
    else:
        d.line([a, b], fill=color, width=w * S)
    ang = np.arctan2(y1 - y0, x1 - x0)
    h = head * S
    p1 = (x1 - h * np.cos(ang - 0.45), y1 - h * np.sin(ang - 0.45))
    p2 = (x1 - h * np.cos(ang + 0.45), y1 - h * np.sin(ang + 0.45))
    d.polygon([b, p1, p2], fill=color)


def box(d, xy, text, f, fill=(255, 255, 255), radius=10, bold=False):
    x0, y0, x1, y1 = xy
    if fill is not None:
        d.rounded_rectangle(xy, radius=radius * S, outline=(0, 0, 0), width=2 * S, fill=fill)
    lines = text.split("\n")
    hs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
    th = sum(b[3] - b[1] for b in hs) + (len(lines) - 1) * 6 * S
    y = (y0 + y1) / 2 - th / 2
    for ln, bb in zip(lines, hs):
        w = bb[2] - bb[0]
        d.text(((x0 + x1) / 2 - w / 2 - bb[0], y - bb[1]), ln, fill=(0, 0, 0), font=f)
        y += bb[3] - bb[1] + 6 * S


def luong_xu_ly():
    W, H = 1000 * S, 380 * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f = font(FB, 14)
    fl = font(FI, 13)
    bw, bh = 225 * S // 2 * 2 // 2, 74 * S
    gap = 48 * S
    # hàng trên: xử lý dòng ngắt; hàng dưới: nhận dạng dòng ảo
    top_y, bot_y = 62 * S, 205 * S
    x0 = 70 * S
    names_top = ["1. Nhận nét\ntừ khung viết", "2. Gán nét\nvào hàng", "3. Ghép đoạn\nthành dòng ảo"]
    names_bot = ["4. Vẽ dòng\nthành ảnh", "5. CNN 2D\nvà BiLSTM", "6. Beam search\nvà n-gram"]
    bw = 190 * S
    xs = [x0 + i * (bw + gap) for i in range(3)]
    for i, n in enumerate(names_top):
        box(d, (xs[i], top_y, xs[i] + bw, top_y + bh), n, f)
        if i:
            arrow(d, (xs[i - 1] + bw + 4 * S, top_y + bh / 2), (xs[i] - 4 * S, top_y + bh / 2))
    for i, n in enumerate(names_bot):
        box(d, (xs[i], bot_y, xs[i] + bw, bot_y + bh), n, f, fill=(240, 240, 240))
        if i:
            arrow(d, (xs[i - 1] + bw + 4 * S, bot_y + bh / 2), (xs[i] - 4 * S, bot_y + bh / 2))
    # nối bước 3 xuống bước 4
    mx = xs[2] + bw / 2
    my = (top_y + bh + bot_y) / 2
    d.line([(mx, top_y + bh + 4 * S), (mx, my)], fill=(0, 0, 0), width=2 * S)
    d.line([(mx, my), (xs[0] + bw / 2, my)], fill=(0, 0, 0), width=2 * S)
    arrow(d, (xs[0] + bw / 2, my), (xs[0] + bw / 2, bot_y - 4 * S))
    # ba ứng viên
    ex = xs[2] + bw + gap
    ew = 150 * S
    d.ellipse((ex, bot_y, ex + ew, bot_y + bh), outline=(0, 0, 0), width=2 * S)
    box(d, (ex, bot_y, ex + ew, bot_y + bh), "Ba ứng viên", f, fill=None)
    arrow(d, (xs[2] + bw + 4 * S, bot_y + bh / 2), (ex - 4 * S, bot_y + bh / 2))
    # vòng phản hồi: người dùng viết tiếp
    fy = bot_y + bh + 34 * S
    cx = ex + ew / 2
    d.line([(cx, bot_y + bh + 4 * S), (cx, fy)], fill=(90, 90, 90), width=2 * S)
    for k in range(int((cx - (x0 - 40 * S)) // (16 * S))):
        xa = cx - k * 16 * S
        d.line([(xa, fy), (xa - 8 * S, fy)], fill=(90, 90, 90), width=2 * S)
    lx = x0 - 40 * S
    d.line([(lx, fy), (lx, top_y + bh / 2)], fill=(90, 90, 90), width=2 * S)
    arrow(d, (lx, top_y + bh / 2), (xs[0] - 4 * S, top_y + bh / 2), color=(90, 90, 90))
    t = "Người dùng viết tiếp: chạy lại cả luồng trên mọi nét đã có"
    bb = d.textbbox((0, 0), t, font=fl)
    d.text(((lx + cx) / 2 - (bb[2] - bb[0]) / 2, fy + 6 * S), t, fill=(60, 60, 60), font=fl)
    # nhãn hai phần
    fl2 = font(FI, 13)
    for txt, y in (("Xử lý dòng ngắt", top_y - 36 * S), ("Nhận dạng dòng ảo", bot_y - 36 * S)):
        d.text((xs[1] + bw / 2 - d.textbbox((0, 0), txt, font=fl2)[2] / 2, y), txt, fill=(60, 60, 60), font=fl2)
    im = trim(im)
    im.save(os.path.join(OUT, "luong-xu-ly.png"), dpi=(300, 300))


def trim(im, pad=12):
    g = np.asarray(im.convert("L"))
    ys, xs = np.where(g < 250)
    return im.crop((max(0, xs.min() - pad * S), max(0, ys.min() - pad * S), min(im.width, xs.max() + pad * S), min(im.height, ys.max() + pad * S)))


def vi_du_dong_ngat(code, idx):
    d = json.load(open(SESSION, encoding="utf-8"))
    sess = d["sessions"] if d.get("schema") == "thu-net-bundle/1" else [d]
    s = [x for x in sess if x["participant"] == code][0]
    line = s["lines"][idx]
    strokes = ink.strokes_of(line)
    f = line["frame"]
    # (a) nét trên khung có hàng kẻ
    sc = 2.0 * S / 2
    W = int(f["canvasW"] * sc)
    ymax = max(p[:, 1].max() for p in strokes) + f["rowPx"] * 0.4
    H = int(ymax * sc)
    a = Image.new("RGB", (W, H), "white")
    da = ImageDraw.Draw(a)
    r = f["topPad"]
    while r < ymax:
        da.line([(0, r * sc), (W, r * sc)], fill=(150, 175, 220), width=max(1, S))
        r += f["rowPx"]
    for p in strokes:
        q = [(x * sc, y * sc) for x, y in p]
        if len(q) == 1:
            da.ellipse([q[0][0] - 3 * S, q[0][1] - 3 * S, q[0][0] + 3 * S, q[0][1] + 3 * S], fill="black")
        else:
            da.line(q, fill="black", width=int(2.2 * S), joint="curve")
    da.rectangle([0, 0, W - 1, H - 1], outline=(120, 120, 120), width=S)
    # (b) dòng ảo do lớp ghép đoạn tạo ra, vẽ như đầu vào của mô hình
    rows = ink.assign_rows(strokes, f["topPad"], f["rowPx"])
    stitched = ink.stitch(strokes, f["topPad"], f["rowPx"])
    img = ink.render(stitched)
    b = Image.fromarray(255 - img).convert("RGB")  # ảnh của mô hình có nền đen, in ngược lại cho dễ nhìn
    b = b.resize((b.width * 3 * S // 2, b.height * 3 * S // 2), Image.NEAREST)
    db = ImageDraw.Draw(b)
    db.rectangle([0, 0, b.width - 1, b.height - 1], outline=(120, 120, 120), width=S)
    # ghép: (a) bên trái, (b) bên phải phía dưới, có nhãn
    fl = font(F, 20)
    pad = 30 * S
    Wt = a.width + pad + b.width
    Ht = max(a.height, b.height) + 50 * S
    out = Image.new("RGB", (Wt, Ht), "white")
    out.paste(a, (0, 0))
    by = (a.height - b.height) // 2
    out.paste(b, (a.width + pad, by))
    do = ImageDraw.Draw(out)
    for txt, cx in (("(a)", a.width / 2), ("(b)", a.width + pad + b.width / 2)):
        bb = do.textbbox((0, 0), txt, font=fl)
        do.text((cx - (bb[2] - bb[0]) / 2, Ht - 44 * S), txt, fill="black", font=fl)
    arrow(do, (a.width + 4 * S, by + b.height / 2), (a.width + pad - 4 * S, by + b.height / 2), w=2, head=8)
    out.save(os.path.join(OUT, "vi-du-dong-ngat.png"), dpi=(300, 300))
    print("dòng:", line["text"], "| số dòng chữ khi gán:", int(rows.max()) + 1, "| ảnh mô hình:", img.shape)


def kien_truc():
    """Kiến trúc M1 lớn, mô hình đưa vào ứng dụng, xếp từ trên xuống."""
    # Chữ trong hình in ra khoảng 10 pt khi hình rộng 12 cm, nên dòng dài được chia làm hai
    rows = [
        ("Ảnh xám của dòng liền hoặc dòng ảo", "64 × 512 × 1", False),
        ("Khối 1: tích chập 3 × 3, 48 bộ lọc,\nchuẩn hóa theo lô, ReLU, max pooling 2 × 2", "32 × 256 × 48", True),
        ("Khối 2: tích chập 3 × 3, 96 bộ lọc,\nchuẩn hóa theo lô, ReLU, max pooling 2 × 1", "16 × 256 × 96", True),
        ("Khối 3: tích chập 3 × 3, 192 bộ lọc,\nchuẩn hóa theo lô, ReLU, max pooling 2 × 1", "8 × 256 × 192", True),
        ("Khối 4: tích chập 3 × 3, 192 bộ lọc,\nchuẩn hóa theo lô, ReLU, max pooling 2 × 1", "4 × 256 × 192", True),
        ("Đổi thành chuỗi 256 bước,\nlớp kết nối đầy đủ 192 ô, ReLU", "256 × 192", False),
        ("BiLSTM thứ nhất: 192 ô mỗi chiều, dropout 0,5", "256 × 384", False),
        ("BiLSTM thứ hai: 192 ô mỗi chiều, dropout 0,5", "256 × 384", False),
        ("Lớp kết nối đầy đủ, softmax trên 161 nhãn", "256 × 161", False),
        ("Huấn luyện: hàm mất mát CTC\nNhận dạng: beam search và n-gram âm tiết", "", None),
    ]
    bw, gap = 340 * S, 16 * S
    x0 = 20 * S
    xshape = x0 + bw + 22 * S
    hs = [(40 if "\n" in r[0] else 24) * S for r in rows]
    W = xshape + 140 * S
    H = sum(hs) + gap * (len(rows) - 1) + 80 * S
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f = font(F, 10.5)
    fb = font(FB, 10.5)
    fs = font(FI, 10.5)
    y = 50 * S
    d.text((xshape, y - 44 * S), "Kích thước đầu ra\n(cao × rộng × kênh)", fill=(60, 60, 60), font=fs, spacing=4 * S)
    for i, ((txt, shape, cnn), bh) in enumerate(zip(rows, hs)):
        fill = (235, 235, 235) if cnn else (255, 255, 255)
        box(d, (x0, y, x0 + bw, y + bh), txt, f, fill=fill, radius=8 if cnn is None else 0)
        if shape:
            bb = d.textbbox((0, 0), shape, font=fb)
            d.text((xshape, y + bh / 2 - (bb[3] - bb[1]) / 2 - bb[1]), shape, fill="black", font=fb)
        if i < len(rows) - 1:
            arrow(d, (x0 + bw / 2, y + bh + 2 * S), (x0 + bw / 2, y + bh + gap - 2 * S), w=2, head=6)
        y += bh + gap
    im = trim(im)
    im.save(os.path.join(OUT, "kien-truc-m1l.png"), dpi=(300, 300))


if __name__ == "__main__":
    luong_xu_ly()
    vi_du_dong_ngat("NV-DNPM", 12)
    kien_truc()
    print("xong")
