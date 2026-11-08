# Quy tắc viết tài liệu

Trạng thái: Nháp

Tài liệu này đặt quy tắc chung cho mọi tài liệu phát triển của đề tài. Các tài liệu còn là nguồn để viết báo cáo và phần cơ sở lý thuyết, nên quy tắc nhắm tới ba điều: cùng một cấu trúc, chép sang báo cáo được ngay, và kiểm tra được bằng công cụ. Ai viết hoặc sửa tài liệu, kể cả trợ lý AI, đọc tài liệu này trước.

## 1. Phạm vi áp dụng

- Áp dụng cho mọi tệp Markdown trong thư mục `docs/` và tệp `CLAUDE.md` ở thư mục gốc.
- Hai tệp `docs/README.md` và `CLAUDE.md` chỉ theo quy tắc về ngôn ngữ và ký tự, không theo quy tắc cấu trúc ở mục 4, mục 6, mục 7 và mục 8.
- Không áp dụng cho mã nguồn, tệp cấu hình và dữ liệu.
- Quy tắc ký tự ở mục 3 không áp dụng bên trong khối mã, đoạn mã nội dòng và công thức, vì cú pháp Kotlin, Python và LaTeX có dùng các ký tự này.

## 2. Ngôn ngữ và văn phong

- Viết tiếng Việt có dấu đầy đủ, lưu tệp bằng UTF-8, chữ ở chuẩn Unicode NFC.
- Đặt dấu thanh theo kiểu cũ, giống `01-mo-ta-de-tai.md`: viết "hòa", "khỏe", "thủy", không viết `hoà`, `khoẻ`, `thuỷ`. Sau "qu", dấu đặt trên nguyên âm cuối: "quý", "quỳ".
- Dùng từ tiếng Việt khi đã có từ quen dùng: mô hình, tập huấn luyện, lượng tử hóa, độ trễ. Giữ nguyên tiếng Anh cho tên riêng và thuật ngữ chưa có từ tiếng Việt quen dùng: CTC, BiLSTM, beam search, n-gram, LiteRT.
- Lần đầu dùng một chữ viết tắt trong mỗi tài liệu, viết đầy đủ rồi đặt chữ viết tắt trong ngoặc, ví dụ "tỷ lệ lỗi ký tự (CER)". Mọi chữ viết tắt phải có trong `ky-hieu-va-viet-tat.md`.
- Viết theo ngôi khách quan, chủ ngữ là "đề tài", "hệ thống", "mô hình". Không dùng "tôi", "chúng tôi", "mình", "bạn".
- Mỗi khái niệm chỉ có một tên trong toàn bộ tài liệu, theo Bảng 2 ở mục 11.

## 3. Ký tự hạn chế

Bảng 1 liệt kê các ký tự không dùng trong câu văn, tiêu đề, bảng và tên hình, cùng cách viết thay.

Bảng 1: Ký tự hạn chế và cách viết thay

| Ký tự | Tên | Viết thay bằng |
| --- | --- | --- |
| `→` `←` `↔` `⇒` `⇔` `➜` | Mũi tên | Viết bằng chữ: "dẫn đến", "chuyển thành", "sau đó". Các bước nối tiếp nhau thì dùng danh sách đánh số |
| `->` `=>` `<-` | Mũi tên gõ bằng ký tự thường | Như mũi tên |
| `—` | Gạch dài | Tách thành hai câu, hoặc dùng dấu phẩy, dấu hai chấm, ngoặc đơn |
| `–` | Gạch ngắn | Khoảng số viết "từ 2 đến 3" trong câu, "2-3" trong bảng |
| Gạch nối có khoảng trắng hai bên, như `A - B` | Gạch nối dùng thay gạch dài | Như gạch dài |
| `·` `•` | Chấm giữa, chấm tròn | Dùng dấu phẩy, hoặc tách thành danh sách với dấu `-` của Markdown |
| `…` và `...` | Dấu ba chấm | Liệt kê đủ, hoặc viết "và các mục khác" |
| Biểu tượng cảm xúc, `✓` `✗` | Biểu tượng | Viết "Có", "Không", "Đạt", "Chưa đạt" |

Ngoài các ký tự trong Bảng 1:

- Dấu chấm câu vẫn dùng bình thường. Tiêu đề không kết thúc bằng dấu chấm.
- Ký hiệu toán như `≤`, `≥`, `×`, `±` chỉ dùng trong công thức và bảng. Trong câu văn, viết "không quá", "ít nhất", "nhân", "cộng trừ".
- Sơ đồ cần mũi tên thì vẽ bằng Mermaid, theo mục 7.

## 4. Cấu trúc một tài liệu

Mỗi tài liệu có các phần theo thứ tự sau:

1. Tiêu đề cấp 1, chỉ có một, ở dòng đầu tiên.
2. Dòng trạng thái, nhận một trong ba giá trị: `Trạng thái: Nháp`, `Trạng thái: Chờ duyệt`, `Trạng thái: Đã chốt`.
3. Đoạn mở đầu từ 2 đến 3 câu, nói tài liệu dùng để làm gì và ai đọc.
4. Các mục cấp 2 đánh số liên tục từ 1, dạng `## 1. Tên mục`.
5. Trong mỗi mục cấp 2, các mục con cấp 3 đánh số theo mục cha và liên tục từ 1, dạng `### 2.1. Tên mục con`.

Các quy định đi kèm:

- Không dùng tiêu đề cấp 4 trở xuống. Nội dung cần chia nhỏ hơn thì dùng danh sách có nhãn đậm.
- Không để mục trống. Mục chưa viết thì ghi "Chưa viết" kèm lý do hoặc thời điểm sẽ viết.
- Tài liệu trong `docs/ly-thuyet/` và `docs/bao-cao/` có các mục cấp 2 cố định theo mẫu, xem mục 12 và mục 13.
- Không ghi lịch sử thay đổi hay số phiên bản trong tài liệu. Lịch sử nằm trong git.
- Một nội dung chỉ viết ở một nơi. Tài liệu khác cần đến thì dẫn chiếu, ví dụ "xem `03-du-lieu.md`, mục 2".
- Tài liệu không có mục "Tài liệu tham khảo" riêng. Danh mục nguồn dùng chung nằm ở `tai-lieu-tham-khao.bib`, theo mục 10.

## 5. Câu và đoạn

- Mỗi câu một ý. Câu dài hơn khoảng 25 từ thì tách.
- Mỗi đoạn văn không quá 5 câu.
- Viết câu chủ động, nói rõ cái gì làm gì: viết "Lớp ghép đoạn nối các hàng", không viết "Các hàng được nối".
- Có số liệu thì đưa số liệu, không dùng "khá", "rất", "nhiều".
- Dẫn chiếu bằng số mục, số bảng, số hình, số công thức. Không viết "ở trên", "bên dưới", "như đã nói", vì vị trí sẽ đổi khi chép sang báo cáo.
- Chữ đậm chỉ dùng cho nhãn đầu dòng trong danh sách và cho thuật ngữ ở chỗ định nghĩa, không dùng để nhấn mạnh giữa câu.
- Không viết hoa cả từ để nhấn mạnh.

## 6. Danh sách và bảng

- Dùng danh sách khi có từ ba ý song song trở lên. Danh sách không thứ tự dùng `-`, các bước có thứ tự dùng `1.`.
- Danh sách lồng nhau tối đa hai cấp.
- Dùng bảng khi so sánh nhiều đối tượng theo cùng các tiêu chí. Ô bảng viết ngắn, không kết thúc bằng dấu chấm.
- Mỗi bảng có tên trên một dòng riêng, đặt phía trên bảng và cách bảng một dòng trống, dạng `Bảng 2: Thống kê bộ dữ liệu`.
- Bảng đánh số liên tục từ 1 trong mỗi tài liệu. Khi chép sang báo cáo thì đánh lại số theo chương.
- Mỗi bảng được nhắc tới ít nhất một lần trong lời văn bằng số của nó, ví dụ `Bảng 2 cho thấy`.

## 7. Hình và sơ đồ

- Sơ đồ quy trình và kiến trúc vẽ bằng Mermaid, trong khối mã `mermaid`, để không bị mất khi xuất tệp hay đổi định dạng.
- Ảnh đặt trong `docs/hinh/`, tên tệp không dấu.
- Mỗi hình có tên trên một dòng riêng, đặt phía dưới hình và cách hình một dòng trống, dạng `Hình 1: Luồng xử lý một dòng ngắt`.
- Hình đánh số và được nhắc tới trong lời văn theo cùng cách với bảng ở mục 6.
- Không chép hình từ bài báo. Vẽ lại, rồi ghi nguồn ở cuối tên hình, ví dụ `Hình 2: Kiến trúc mô hình, vẽ lại theo [@carbune2019]`.
- Không nhúng nội dung mà bản Markdown không hiển thị được.

## 8. Công thức

- Công thức viết bằng cú pháp LaTeX. Công thức trong dòng đặt giữa hai dấu `$`, ví dụ `$T$`.
- Công thức riêng dòng đặt giữa hai dòng chỉ chứa `$$`, đánh số bằng `\tag{}` liên tục từ 1 trong mỗi tài liệu.
- Ký hiệu nào xuất hiện lần đầu trong một công thức riêng dòng thì được định nghĩa ngay sau công thức, trong một câu bắt đầu bằng "trong đó".
- Ký hiệu lấy từ bảng ký hiệu trong `ky-hieu-va-viet-tat.md`. Cần ký hiệu mới thì thêm vào bảng đó trước rồi mới dùng.
- Nhắc tới công thức bằng số, ví dụ "theo công thức (1)".

Ví dụ một công thức viết đúng quy tắc:

```markdown
$$
\mathrm{CER} = \frac{S + I + D}{N} \tag{1}
$$

trong đó $S$, $I$, $D$ là số ký tự bị thay, chèn và xóa, $N$ là số ký tự của chuỗi đúng.
```

## 9. Số liệu, đơn vị và ngày tháng

- Số viết theo kiểu Việt Nam: dấu chấm ngăn cách hàng nghìn, dấu phẩy ngăn cách phần thập phân. Ví dụ: 4.433 dòng, khoảng cách 0,05.
- Trong khối mã, tên tệp và cấu hình, giữ cách viết số của chương trình, ví dụ `0.05`.
- Giữa số và đơn vị có khoảng trắng: 20 MB, 300 ms, 1 giây. Phần trăm viết liền: 3,24%.
- Chênh lệch giữa hai tỷ lệ phần trăm gọi là "điểm phần trăm".
- Ngày trong lời văn viết theo dạng ngày/tháng/năm, ví dụ 07/11/2026. Ngày trong tên tệp viết theo dạng năm-tháng-ngày, ví dụ `2026-11-07`, để tệp tự xếp theo thời gian.
- Mỗi số liệu thuộc một trong ba loại và phải nói rõ loại nào:
  - **Đã đo**: ghi lần chạy trong `07-nhat-ky-thi-nghiem.md` cho ra số đó.
  - **Trích dẫn**: ghi khóa trích dẫn theo mục 10.
  - **Dự kiến**: ghi rõ chữ "dự kiến" hoặc "giả định". Không trình bày số dự kiến như kết quả.

## 10. Trích dẫn

- Mọi nguồn dùng làm căn cứ, kể cả trang web, có một mục trong `docs/tai-lieu-tham-khao.bib`.
- Khóa trích dẫn gồm họ của tác giả đầu, viết thường không dấu, nối với năm, ví dụ `carbune2019`. Trùng khóa thì thêm `a`, `b` vào cuối. Với tên người Việt, họ là chữ đầu tiên, nên khóa của bài do Pham Thach Thanh Truc viết bắt đầu bằng `pham`.
- Nguồn không có tác giả là người, như trang tài liệu của Google, thì khóa dùng tên ngắn của tổ chức hoặc trang, ví dụ `google2026a`, `vohtr2026a`. Trang web không ghi năm thì dùng năm truy cập.
- Trong tệp `.bib`, tên tác giả ghi dạng `Họ, Tên đệm và tên`, ví dụ `Pham, Thach Thanh Truc`, để công cụ xuất đúng thứ tự tên.
- Trong lời văn, trích bằng `[@carbune2019]`. Nhiều nguồn viết `[@carbune2019; @le2019]`, kèm số trang viết `[@carbune2019, tr. 5]`.
- Trang web ghi thêm ngày truy cập trong trường `urldate`.
- Liên kết trần chỉ dùng cho tài nguyên không làm căn cứ, như trang tải phần mềm hay kho mã.
- Tóm tắt nguồn bằng lời của mình, không chép nguyên văn đoạn dài.
- Tên bài báo có gạch dài thì thay gạch dài bằng dấu hai chấm.

Một mục trong tệp `.bib` có dạng:

```bibtex
@misc{carbune2019,
  author        = {Carbune, Victor and Gonnet, Pedro and others},
  title         = {Fast Multi-language {LSTM}-based Online Handwriting Recognition},
  year          = {2019},
  eprint        = {1902.10525},
  archiveprefix = {arXiv},
  url           = {https://arxiv.org/abs/1902.10525}
}
```

Cách trích này cho phép Pandoc tự tạo danh mục tài liệu tham khảo khi xuất báo cáo. Thêm tham số `--csl` để chọn kiểu trích dẫn theo yêu cầu của trường:

```bash
pandoc docs/01-mo-ta-de-tai.md --citeproc --bibliography docs/tai-lieu-tham-khao.bib -o chuong-1.docx
```

## 11. Thuật ngữ thống nhất

Bảng 2 chốt tên của các khái niệm dùng nhiều trong đề tài. Khi cần thuật ngữ mới, thêm vào Bảng 2 trước rồi mới dùng. Ký hiệu toán và chữ viết tắt nằm ở `ky-hieu-va-viet-tat.md`.

Bảng 2: Thuật ngữ thống nhất

| Thuật ngữ | Nghĩa | Không dùng |
| --- | --- | --- |
| nét | Chuỗi điểm từ lúc đặt bút đến lúc nhấc bút | stroke, nét vẽ |
| chữ viết tay dạng nét | Chữ viết tay lưu dưới dạng chuỗi nét theo thứ tự viết | online, trực tuyến |
| chữ viết tay dạng ảnh | Chữ viết tay lưu dưới dạng ảnh | offline, ngoại tuyến |
| hàng | Một hàng kẻ trên khung viết | dòng, khi nói về khung viết |
| dòng | Đơn vị văn bản cần nhận dạng, có thể nằm trên nhiều hàng | hàng, khi nói về văn bản |
| đoạn | Phần của một dòng nằm trên cùng một hàng | segment, khúc |
| dòng liền | Dòng viết trọn trên một hàng, không bị ngắt | |
| dòng ngắt | Dòng viết trên nhiều hàng, hoặc có tạm dừng giữa chừng | |
| dòng ảo | Dòng liền tạo ra bằng cách ghép các đoạn | |
| lớp ghép đoạn | Bước nối các đoạn thành dòng ảo | |
| nét trễ | Nét viết sau, nằm xa chữ cái mà nó thuộc về, thường là dấu thanh hoặc dấu phụ | delayed stroke |
| dấu thanh | Sắc, huyền, hỏi, ngã, nặng | dấu giọng |
| dấu phụ | Phần dấu tạo ra ă, â, ê, ô, ơ, ư, đ | dấu mũ, khi nói chung |
| tập huấn luyện, tập kiểm định, tập kiểm thử | Ba phần của một bộ dữ liệu | tập train, tập val, tập test |
| tập tự thu | Dữ liệu đề tài tự thu trên điện thoại | |

Không viết "dấu" một mình ở chỗ có thể hiểu nhầm giữa dấu thanh và dấu phụ.

## 12. Tài liệu lý thuyết

Phần cơ sở lý thuyết của báo cáo được viết dần trong thư mục `docs/ly-thuyet/`, theo các quy định sau:

- Mỗi tệp viết về một chủ đề, đặt tên dạng `NN-ten-chu-de.md`. Chủ đề dài hơn khoảng 2.000 từ thì tách thành hai tệp.
- Tạo tệp mới bằng cách chép mẫu `docs/mau/ly-thuyet.md`. Năm mục cấp 2 phải giữ đúng tên và thứ tự trong mẫu:
  1. Bài toán: kỹ thuật giải quyết vấn đề gì, đầu vào và đầu ra là gì.
  2. Nguyên lý: cách hoạt động, kèm công thức theo mục 8.
  3. Ví dụ minh họa: một ví dụ nhỏ tính được bằng tay, hoặc một hình vẽ lại.
  4. Áp dụng trong đề tài: dùng ở bước nào, chọn tham số nào và vì sao, dẫn chiếu tới tài liệu thiết kế.
  5. Hạn chế: giới hạn của kỹ thuật và ảnh hưởng tới đề tài.
- Lý thuyết chỉ viết sâu đến mức cần để hiểu cách đề tài dùng nó. Chứng minh dài thì dẫn nguồn thay vì chép lại.
- Mỗi tệp lý thuyết có ít nhất một trích dẫn tới nguồn gốc của kỹ thuật.
- Danh sách chủ đề dự kiến nằm trong `docs/README.md`.

## 13. Báo cáo

Mục này quy định cách dùng tài liệu cho hai loại báo cáo: báo cáo cuối kỳ và báo cáo tiến độ.

### 13.1. Báo cáo cuối kỳ

Bảng 3 là bố cục dự kiến của báo cáo cuối kỳ, cần chỉnh theo mẫu của trường khi có. Cột "Phần trong báo cáo" của `docs/README.md` ghi mỗi tài liệu đi vào phần nào.

Bảng 3: Bố cục dự kiến của báo cáo cuối kỳ

| Phần | Nội dung | Lấy từ |
| --- | --- | --- |
| Chương 1: Tổng quan | Bối cảnh, mục tiêu, phạm vi | `01-mo-ta-de-tai.md`, phần mục tiêu của `02-yeu-cau-va-danh-gia.md` |
| Chương 2: Cơ sở lý thuyết | Các kỹ thuật đề tài sử dụng | `ly-thuyet/` |
| Chương 3: Dữ liệu và phương pháp | Dữ liệu, lớp ghép đoạn, mô hình, giải mã | `03-du-lieu.md`, `04-thiet-ke-he-thong.md` |
| Chương 4: Thực nghiệm và đánh giá | Chỉ số, kịch bản, kết quả, phân tích lỗi | `02-yeu-cau-va-danh-gia.md`, `05-ke-hoach-thi-nghiem.md`, `07-nhat-ky-thi-nghiem.md` |
| Chương 5: Triển khai trên Android | Chuyển đổi, lượng tử hóa, ứng dụng, độ trễ | `06-trien-khai-android.md` |
| Kết luận | Kết quả đạt được, hạn chế, hướng phát triển | Viết khi kết thúc đề tài |
| Danh mục ký hiệu và chữ viết tắt | Ký hiệu toán, chữ viết tắt | `ky-hieu-va-viet-tat.md` |
| Tài liệu tham khảo | Danh mục nguồn | `tai-lieu-tham-khao.bib` |

Các quy tắc ở mục 2, mục 5, mục 9 và mục 10 giúp mỗi mục của tài liệu chép sang báo cáo được ngay, không phải viết lại.

### 13.2. Báo cáo tiến độ

- Báo cáo tiến độ đặt trong `docs/bao-cao/`, tên tệp dạng `2026-11-21-bao-cao-tien-do.md` theo ngày nộp.
- Tạo bằng cách chép mẫu `docs/mau/bao-cao-tien-do.md` và giữ đúng bốn mục cấp 2: Việc đã làm, Kết quả, Vấn đề và cách xử lý, Việc tiếp theo.
- Báo cáo tiến độ chỉ tóm tắt và dẫn chiếu. Số liệu chi tiết nằm ở nhật ký thí nghiệm, không chép lại.
- Báo cáo đã nộp thì chuyển sang `Trạng thái: Đã chốt` và không sửa nữa.

## 14. Tên tệp, thư mục và mục lục

- Tài liệu nội dung đặt trong `docs/`, tên tệp dạng `NN-ten-khong-dau.md`: hai chữ số, chữ thường không dấu, các từ nối bằng gạch ngang. Số thứ tự là thứ tự nên đọc.
- Các tệp và thư mục có tên cố định:
  - `docs/README.md`: mục lục của toàn bộ tài liệu.
  - `docs/ky-hieu-va-viet-tat.md`: bảng ký hiệu toán và bảng chữ viết tắt.
  - `docs/tai-lieu-tham-khao.bib`: danh mục nguồn.
  - `docs/mau/`: các tệp mẫu.
  - `docs/ly-thuyet/` và `docs/bao-cao/`: tài liệu lý thuyết và báo cáo tiến độ.
  - `docs/hinh/`: ảnh dùng trong tài liệu.
- Thêm, đổi tên hoặc xóa một tài liệu thì cập nhật `docs/README.md` trong cùng lần sửa. Tài liệu đã lên kế hoạch nhưng chưa có tệp thì ghi trạng thái "Chưa viết".
- Trạng thái ghi trong `docs/README.md` phải trùng với dòng trạng thái trong tài liệu.

## 15. Kiểm tra trước khi lưu

1. Chạy công cụ kiểm tra ở thư mục gốc của kho:

   ```bash
   python tools/check_docs.py
   ```

   Chỉ lưu khi công cụ báo không có lỗi. Công cụ kiểm tra các nhóm lỗi sau:
   - Ký tự hạn chế, chữ chưa ở chuẩn NFC, dấu thanh đặt theo kiểu mới.
   - Tiêu đề cấp 1, dòng trạng thái, đoạn mở đầu, số thứ tự các mục, mục trống, tiêu đề cấp 4.
   - Tên và số của bảng, hình, công thức, và việc mỗi bảng, hình được nhắc tới trong lời văn.
   - Khóa trích dẫn không có trong `tai-lieu-tham-khao.bib`, tệp lý thuyết không có trích dẫn nào.
   - Mục cấp 2 của tài liệu lý thuyết và báo cáo tiến độ so với mẫu.
   - Mục lục `docs/README.md` so với các tệp thật.

2. Đọc lại và tự hỏi:
   - Mỗi số liệu đã ghi rõ là đã đo, trích dẫn hay dự kiến chưa?
   - Thuật ngữ đã đúng Bảng 2 chưa?
   - Có đoạn nào lặp lại nội dung của tài liệu khác không?
   - Có chỗ nào dẫn chiếu bằng vị trí, như "ở trên", không?

## 16. Sửa quy tắc

Muốn đổi một quy tắc thì sửa tài liệu này và công cụ kiểm tra trước, sau đó mới áp dụng cho các tài liệu khác.
