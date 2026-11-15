# Thiết kế hệ thống

Trạng thái: Nháp

Tài liệu này mô tả thiết kế của lớp ghép đoạn, bước vẽ dòng thành ảnh, bộ giải mã và mô hình ngôn ngữ, ở mức đủ để viết lại mã. Tài liệu dành cho người viết mã và người viết Chương 3 của báo cáo. Kiến trúc mô hình nằm ở `01-mo-ta-de-tai.md`, mục 7.3, còn kết quả đo nằm ở `07-nhat-ky-thi-nghiem.md`.

## 1. Tổng quan

Hệ thống có một luồng xử lý chung cho Python và Kotlin, theo `01-mo-ta-de-tai.md`, mục 7. Mã Python trong `training/` là bản tham chiếu, và mã Kotlin trong `android/` phải cho cùng kết quả. Bảng 1 ghi mỗi thành phần nằm ở tệp nào.

Bảng 1: Vị trí mã của từng thành phần

| Thành phần | Bản Python | Bản Kotlin |
| --- | --- | --- |
| Gán nét vào hàng, ghép đoạn, vẽ ảnh | `training/ink.py` | `Ink.kt` |
| Mô hình ngôn ngữ | `training/lm_binary.py` | `NGramModel.kt` |
| Bộ giải mã | `training/decoder.py` | `CtcDecoder.kt` |
| Mô hình | `training/model.py` | `Recognizer.kt`, chạy tệp `.tflite` |

## 2. Lớp ghép đoạn

### 2.1. Gán nét vào dòng chữ

Lớp ghép đoạn gán nét theo thứ tự viết, không dựa vào đường kẻ. Người viết đi hết hàng này mới sang hàng sau, nên các nét của một dòng chữ đứng liền nhau trong thứ tự viết. Lớp ghép đoạn duyệt các nét theo thứ tự và so mỗi nét với dòng chữ đang viết, có đỉnh thân chữ, đường chân chữ và chiều cao thân chữ tính theo mục 2.2. Một nét mở dòng chữ mới khi nét cao ít nhất 0,4 lần chiều cao thân chữ và thỏa một trong hai điều kiện:

- Tâm của nét thấp hơn đường chân chữ quá 1,2 lần chiều cao thân chữ.
- Tâm của nét thấp hơn đường chân chữ quá 0,5 lần chiều cao thân chữ, và điểm trái nhất của nét nằm bên trái mép phải của dòng quá 2 lần chiều cao thân chữ.

Điều kiện thứ hai bắt được chỗ người viết quay về đầu hàng mới. Chân chữ của g và y được viết ngay sau chữ, nằm thấp nhưng không lùi về trái, nên ở lại dòng đang viết. Nét dẹt như dấu chấm, dấu nặng và gạch ngang không mở được dòng mới, kể cả khi người viết quay lại thêm dấu nặng cho từ đầu hàng. Nét có tâm cao hơn đỉnh thân chữ quá 1,2 lần chiều cao thân chữ được gán về một dòng trước, nếu tâm nét nằm trên đường chân chữ của dòng đó và gần đỉnh thân chữ của dòng đó hơn. Trường hợp này là dấu viết bổ sung cho dòng trên. Dấu viết cao của dòng đang viết nằm dưới đường chân chữ của dòng trên, nên không bị kéo lên.

Lớp ghép đoạn chạy hai lượt. Lượt đầu lấy chiều cao thân chữ của dòng đang viết, kẹp trong khoảng từ 0,6 đến 1,5 lần giá trị dự đoán bằng 0,35 lần chiều cao hàng kẻ, để dòng mới có ít nét không bị ước lượng sai. Lượt sau dùng chung cho mọi dòng trung vị chiều cao thân chữ của các dòng tìm được ở lượt đầu. Cách gán này vẫn đúng khi người viết không theo đường kẻ, ví dụ viết hai dòng chữ trong một hàng kẻ cao, theo `07-nhat-ky-thi-nghiem.md`, mục 10. Bảng 2 ghi các tham số, tất cả đều là giá trị dự kiến và sẽ chỉnh trên nhóm chỉnh.

Bảng 2: Tham số của lớp ghép đoạn (dự kiến)

| Tham số | Giá trị | Ý nghĩa |
| --- | --- | --- |
| Mở dòng mới | 1,2 | Độ thấp của tâm nét dưới đường chân chữ, theo chiều cao thân chữ |
| Mở dòng mới khi lùi về trái | 0,5 và 2 | Độ thấp của tâm nét và độ lùi về trái, theo chiều cao thân chữ |
| Nét dẹt | 0,4 | Nét thấp hơn chừng này lần chiều cao thân chữ không mở được dòng mới |
| Gán về dòng trước | 1,2 | Độ cao của tâm nét trên đỉnh thân chữ, theo chiều cao thân chữ |
| Chiều cao thân chữ dự đoán | 0,35 | Theo chiều cao hàng kẻ, chỉ dùng ở lượt đầu |
| Giới hạn chiều cao thân chữ ở lượt đầu | 0,6-1,5 | Theo giá trị dự đoán |
| Khoảng trống lớn nhất trong một đoạn | 2 | Theo chiều cao thân chữ của đoạn |
| Khoảng cách giữa hai đoạn | 0,7 | Theo chiều cao thân chữ |
| Giới hạn co giãn | 0,7-1,4 | Hệ số co giãn cỡ chữ của một đoạn |

### 2.2. Ghép các đoạn

Mỗi dòng chữ tạo thành một đoạn. Chiều cao thân chữ của đoạn là hiệu giữa phân vị 85 và phân vị 15 của tọa độ $y$, và đường chân chữ là phân vị 85. Lớp ghép đoạn lấy trung vị của chiều cao thân chữ trên các đoạn làm cỡ chữ chung, rồi thực hiện các bước sau cho từng đoạn theo thứ tự viết:

1. Thu các khoảng trống ngang rộng hơn 2 lần chiều cao thân chữ của đoạn về 0,7 lần. Khoảng trống này thường xuất hiện khi người viết cuộn khung viết rồi viết tiếp ở chỗ mới.
2. Co giãn đoạn về cỡ chữ chung, trong giới hạn ở Bảng 2.
3. Đưa đường chân chữ của đoạn về cùng một độ cao.
4. Đặt đoạn tiếp theo sau đoạn trước, cách một khoảng cố định.

Dòng liền cũng đi qua lớp ghép đoạn như một dòng ảo chỉ có một đoạn, nên cũng được thu khoảng trống. Kết quả là dòng ảo, vẫn giữ các nét riêng biệt để bước sau vẽ thành ảnh.

## 3. Vẽ dòng thành ảnh

Bước vẽ co dòng ảo vào khung theo `03-du-lieu.md`, mục 3.3, với độ dày nét 1,2 điểm ảnh trên khung cuối. Giá trị này cho CER thấp nhất khi vẽ lại ảnh kiểm định bằng bộ vẽ của ứng dụng, theo `07-nhat-ky-thi-nghiem.md`, mục 7, và sẽ chỉnh lại trên nhóm chỉnh.

Đề tài không dùng thư viện vẽ có sẵn, vì kết quả của Python và Android sẽ khác nhau. Cả hai bản dùng cùng một thuật toán trên lưới mịn gấp 4 lần mỗi chiều. Một ô được tô khi tâm ô cách đoạn thẳng của nét không quá nửa độ dày, rồi lưới mịn được lấy trung bình về khung cuối.

## 4. Mô hình ngôn ngữ

### 4.1. Cách tính

Mô hình ngôn ngữ là n-gram bậc 3 trên âm tiết. Đề tài làm trơn bằng stupid backoff với hệ số 0,4, thay vì Kneser-Ney [@kneser1995], vì cách này chỉ cần tra bảng đếm và dễ viết lại bằng Kotlin. Âm tiết được đưa về chữ thường và bỏ dấu câu, còn mọi âm tiết có chữ số được gộp thành một âm tiết đặc biệt.

### 4.2. Kho văn bản

Kho văn bản gồm tập huấn luyện VNOnDB và Wikipedia tiếng Việt [@wikimedia2026a], theo `03-du-lieu.md`, mục 5. Đề tài loại mọi câu có cụm 8 âm tiết trùng với tập kiểm định, tập kiểm thử hoặc câu đề của công cụ thu. Cứ 50 bài Wikipedia thì 1 bài được giữ riêng làm nguồn câu đề. Bài ngắn hơn 2.000 ký tự bị bỏ, vì phần lớn là bài do chương trình sinh hàng loạt.

### 4.3. Tệp trên điện thoại

Tệp `lm.bin` dùng 30.000 âm tiết, giữ các cụm hai có số đếm từ 3 trở lên và các cụm ba có số đếm từ 4 trở lên. Số đếm được lưu trong 1 byte theo thang logarit cơ số 1,1. Khóa cụm ba là giá trị băm FNV-1a 32 bit, nên có thể trùng với xác suất nhỏ. Bảng 3 ghi quy mô của tệp.

Bảng 3: Quy mô của tệp `lm.bin`, đã đo

| Thành phần | Số lượng |
| --- | --- |
| Âm tiết trong từ vựng | 30.000 |
| Cụm hai | 843.240 |
| Cụm ba | 1.273.828 |
| Dung lượng | 10,95 MB |

## 5. Bộ giải mã

Bộ giải mã là beam search trên tiền tố, theo `ly-thuyet/06-beam-search-va-n-gram.md`, mục 2.3. Mỗi bước chỉ xét tối đa 8 ký tự có xác suất từ 0,002 trở lên. Điểm n-gram được cộng khi một âm tiết kết thúc. Bảng 4 ghi các tham số đang dùng.

Bảng 4: Tham số của bộ giải mã

| Tham số | Giá trị | Cách chọn |
| --- | --- | --- |
| Độ rộng beam $W$ | 30 | Theo `07-nhat-ky-thi-nghiem.md`, mục 4 và mục 11.1 |
| $\alpha$ | 0,45 | Chỉnh trên tập kiểm định, chỉnh lại cho `m1l_rr_e100` theo `07-nhat-ky-thi-nghiem.md`, mục 11.1 |
| $\beta$ | 4 | Chỉnh trên tập kiểm định, chỉnh lại cho `m1l_rr_e100` theo `07-nhat-ky-thi-nghiem.md`, mục 11.1 |
| Số ứng viên trả về | 3 | Theo `01-mo-ta-de-tai.md`, mục 5 |

## 6. Vấn đề chưa chốt

Bảng 5 ghi các điểm thiết kế còn cần dữ liệu thật để chốt.

Bảng 5: Các vấn đề chưa chốt về thiết kế

| Vấn đề | Ảnh hưởng | Cách chốt |
| --- | --- | --- |
| Tham số ở Bảng 2 và độ dày nét mới thử trên 2 người viết bằng bút | Chất lượng dòng ảo và độ lệch với ảnh huấn luyện | Chỉnh trên nhóm chỉnh của tập tự thu, viết bằng ngón tay |
| Lớp ghép đoạn mới được kiểm tra trên 20 dòng ngắt thật của buổi thử | Chưa biết kết quả với người viết khác và khi viết bằng ngón tay | Chạy kịch bản Ngắt mô phỏng và Viết tay thật trên nhóm chỉnh |
| Người viết quay lại sửa một hàng ở giữa | Nét sửa có thể bị gán sai dòng | Đếm số trường hợp trên nhóm chỉnh, xử lý riêng nếu gặp nhiều |
