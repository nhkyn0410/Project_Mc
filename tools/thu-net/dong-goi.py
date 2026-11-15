"""Đóng gói tools/thu-net/index.html thành một trang HTML đầy đủ để đặt lên một máy chủ tĩnh, ví dụ GitHub Pages.

    python tools/thu-net/dong-goi.py <thư mục ra>

Tệp index.html trong kho chỉ là phần thân trang, vì công cụ Artifact của claude.ai tự bọc phần đầu khi xuất bản.
Khi đặt trang ở nơi khác, trang cần khai báo doctype để trình duyệt vẽ đúng chuẩn, và cần phần lề an toàn mà khung
của claude.ai vẫn thêm. Trang chạy riêng như vậy gửi được tệp qua bảng chia sẻ của điện thoại, còn trang trong khung
của claude.ai thì người chưa đăng nhập chỉ sao chép được.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = (
    "<!doctype html>\n"
    '<html lang="vi">\n'
    "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
    "body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
)


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 1
    body = io.open(os.path.join(HERE, "index.html"), encoding="utf8").read()
    assert body.lstrip().startswith("<meta charset"), "index.html phải bắt đầu bằng thẻ meta charset"
    os.makedirs(argv[0], exist_ok=True)
    out = os.path.join(argv[0], "index.html")
    # Thẻ meta charset phải nằm trong 1024 byte đầu, nên phần thêm vào đặt ngay sau doctype và thật ngắn.
    with io.open(out, "w", encoding="utf8", newline="\n") as f:
        f.write(HEAD + body + "\n</html>\n")
    print("đã ghi", out, os.path.getsize(out), "byte")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
