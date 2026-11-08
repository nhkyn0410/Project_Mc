# Nhận dạng chữ viết tay tiếng Việt trên thiết bị cảm ứng

Đề tài xây hệ thống nhận dạng chữ viết tay tiếng Việt theo dòng, chạy offline trên điện thoại Android và cho phép ngắt dòng khi viết.

## Viết tài liệu

- Tài liệu phát triển nằm trong `docs/` và viết theo `docs/00-quy-tac-viet-tai-lieu.md`. Đọc tệp đó trước khi viết hoặc sửa bất kỳ tài liệu nào. Mục lục nằm ở `docs/README.md`.
- Những điểm hay sai nhất:
  - Không dùng mũi tên, gạch dài, gạch ngắn, chấm giữa, chấm tròn, dấu ba chấm và biểu tượng cảm xúc trong câu văn, tiêu đề, bảng (mục 3).
  - Dòng đầu là tiêu đề cấp 1, tiếp theo là dòng trạng thái và đoạn mở đầu, các mục đánh số liên tục (mục 4).
  - Bảng có tên `Bảng N: Tên` phía trên, hình có tên `Hình N: Tên` phía dưới, công thức riêng dòng đánh số bằng `\tag{}` (mục 6, mục 7, mục 8).
  - Trích dẫn bằng `[@khóa]`, khóa phải có trong `docs/tai-lieu-tham-khao.bib` (mục 10).
  - Tài liệu lý thuyết và báo cáo tiến độ tạo từ mẫu trong `docs/mau/` (mục 12, mục 13).
  - Thêm, đổi tên hoặc xóa tài liệu thì cập nhật `docs/README.md` (mục 14).
  - Đặt dấu thanh kiểu cũ (hòa, khỏe, thủy), viết số kiểu Việt Nam (4.433 và 0,05).
- Sau khi sửa tài liệu, chạy `python tools/check_docs.py` và sửa hết lỗi trước khi báo xong.
