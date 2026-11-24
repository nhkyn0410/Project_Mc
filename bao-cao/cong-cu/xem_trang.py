"""Dựng các trang PDF thành ảnh để kiểm tra bố cục.
Dùng: python xem_trang.py <tệp .pdf> <thư mục ra> [trang đầu] [trang cuối] [số trang mỗi tấm] [dpi]
Mỗi tấm ảnh ghép nhiều trang theo hàng ngang, có ghi số trang PDF ở góc."""
import sys, os
import fitz
from PIL import Image, ImageDraw, ImageFont

pdf, outdir = sys.argv[1], sys.argv[2]
doc = fitz.open(pdf)
a = int(sys.argv[3]) if len(sys.argv) > 3 else 1
b = int(sys.argv[4]) if len(sys.argv) > 4 else doc.page_count
per = int(sys.argv[5]) if len(sys.argv) > 5 else 4
dpi = int(sys.argv[6]) if len(sys.argv) > 6 else 60
os.makedirs(outdir, exist_ok=True)
font = ImageFont.truetype("arial.ttf", 22)
pages = list(range(a, min(b, doc.page_count) + 1))
print("số trang PDF:", doc.page_count)
for k in range(0, len(pages), per):
    group = pages[k:k + per]
    ims = []
    for p in group:
        pix = doc[p - 1].get_pixmap(dpi=dpi)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, im.width - 1, im.height - 1], outline=(150, 150, 150))
        d.text((6, 4), str(p), fill=(220, 0, 0), font=font)
        ims.append(im)
    W = sum(i.width for i in ims) + 10 * (len(ims) - 1)
    H = max(i.height for i in ims)
    sheet = Image.new("RGB", (W, H), "white")
    x = 0
    for im in ims:
        sheet.paste(im, (x, 0)); x += im.width + 10
    name = os.path.join(outdir, f"trang-{group[0]:03d}-{group[-1]:03d}.png")
    sheet.save(name)
    print(name)
