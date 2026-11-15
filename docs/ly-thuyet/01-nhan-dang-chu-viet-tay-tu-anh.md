# Nhận dạng dòng chữ viết tay dạng ảnh

Trạng thái: Nháp

Tài liệu này trình bày bài toán nhận dạng một dòng chữ viết tay dạng ảnh, kiến trúc thường dùng và khác biệt so với nhận dạng chữ viết tay dạng nét. Đề tài thu nét trên điện thoại nhưng nhận dạng trên ảnh của dòng, nên cần hiểu cả hai cách. Tài liệu là phần mở đầu của các tài liệu lý thuyết, dành cho người viết phần cơ sở lý thuyết của báo cáo.

## 1. Bài toán

Đầu vào là ảnh $\mathbf{X}$ của một dòng chữ viết tay. Đầu ra là chuỗi ký tự $\mathbf{l}$ của dòng đó. Dữ liệu chỉ có nhãn theo cả dòng, không có vị trí của từng ký tự trên ảnh. Bài toán vì vậy có hai khó khăn: số ký tự thay đổi theo từng dòng, và không biết trước ký tự nào nằm ở cột nào.

Chữ viết tay có thể lưu dưới hai dạng. Dạng nét giữ thứ tự viết và điểm nhấc bút, còn dạng ảnh chỉ giữ hình dạng. Bảng 1 so sánh hai dạng theo các điểm có ảnh hưởng tới đề tài.

Bảng 1: So sánh chữ viết tay dạng nét và dạng ảnh

| Tiêu chí | Dạng nét | Dạng ảnh |
| --- | --- | --- |
| Thông tin có sẵn | Tọa độ, thứ tự viết, điểm nhấc bút | Hình dạng nét |
| Nét trễ | Nằm xa chữ cái trong chuỗi đầu vào | Nằm đúng chỗ trên ảnh |
| Phụ thuộc thứ tự viết | Có | Không |
| Kích thước đầu vào | Thay đổi theo số điểm | Khung cố định, dễ chạy trên điện thoại |
| Mức lỗi thấp nhất đã công bố trên VNOnDB | 1,02%, theo `02-yeu-cau-va-danh-gia.md`, mục 4 | 3,45%, cùng nguồn |

## 2. Nguyên lý

Kiến trúc phổ biến ghép ba phần [@shi2015]. Mạng nơ-ron tích chập (CNN) trích đặc trưng từ ảnh, lớp hồi quy đọc đặc trưng theo chiều ngang, và hàm mất mát Connectionist Temporal Classification (CTC) huấn luyện mô hình khi chỉ có nhãn theo dòng [@graves2006]. Puigcerver cho thấy kiến trúc CNN kết hợp LSTM hai chiều (BiLSTM) đạt kết quả tốt trên dòng chữ viết tay, kèm tăng cường dữ liệu phù hợp [@puigcerver2017].

Khi nhận dạng, mô hình tìm chuỗi có xác suất cao nhất theo ảnh:

$$
\hat{\mathbf{l}} = \arg\max_{\mathbf{l}} \, p(\mathbf{l} \mid \mathbf{X}) \tag{1}
$$

trong đó $\hat{\mathbf{l}}$ là chuỗi đọc ra và $p(\mathbf{l} \mid \mathbf{X})$ là xác suất CTC của chuỗi $\mathbf{l}$. Cách tính xác suất này nằm trong `05-ctc.md`, còn cách tìm chuỗi nằm trong `06-beam-search-va-n-gram.md`.

Mô hình đọc ảnh theo các cột từ trái sang phải, và mỗi bước thời gian ứng với một dải cột. Cách đọc này giả định các ký tự nối tiếp nhau theo chiều ngang. Vì vậy dòng phải nằm gần như thẳng hàng, và dòng viết thành nhiều hàng phải được ghép lại trước khi nhận dạng.

## 3. Ví dụ minh họa

Giả sử người dùng viết chữ "á" theo hai thứ tự: viết chữ "a" rồi đặt dấu sắc ngay, hoặc viết hết dòng rồi quay lại đặt dấu sắc. Hai cách cho chuỗi nét khác nhau, nên mô hình dạng nét nhìn thấy hai đầu vào khác nhau. Với ảnh của dòng, nét dấu sắc nằm cùng một vị trí, nên hai đầu vào giống hệt nhau.

Ví dụ thứ hai tính số bước thời gian trên mỗi ký tự. Khung rộng 512 điểm ảnh, CNN giảm chiều rộng 2 lần, nên $T = 256$. Dòng trung bình của VNOnDB có 68 ký tự, tức khoảng 3,8 bước cho mỗi ký tự. Dòng dài nhất có 158 ký tự, tức khoảng 1,6 bước cho mỗi ký tự, vẫn thỏa điều kiện độ dài ở `05-ctc.md`, mục 2.4.

## 4. Áp dụng trong đề tài

- **Lý do dùng ảnh:** các tệp nét gốc của VNOnDB không tải được, nên đề tài huấn luyện trên bản ảnh, theo `03-du-lieu.md`, mục 1.
- **Vị trí của nét:** ứng dụng vẫn thu nét. Nét được dùng để ghép các hàng thành dòng ảo, rồi được vẽ thành ảnh, theo `02-tien-xu-ly-anh.md`.
- **Kiến trúc:** đề tài dùng CNN 2D, BiLSTM và CTC, theo `01-mo-ta-de-tai.md`, mục 7.3 và `03-cnn-2d.md`.
- **Mốc so sánh:** ngưỡng của đề tài lấy từ các mô hình dạng ảnh trên cùng tập kiểm thử [@pham2025], theo `02-yeu-cau-va-danh-gia.md`, mục 1.

## 5. Hạn chế

- **Mất thông tin thứ tự viết:** dạng ảnh không phân biệt được hai chữ có hình dạng giống nhau nhưng viết khác thứ tự, trong khi các hệ thống dạng nét tốt nhất trên VNOnDB có mức lỗi thấp hơn [@le2019].
- **Lệch cách vẽ:** ảnh huấn luyện và ảnh do ứng dụng vẽ có thể khác nhau về độ dày nét và cách co, theo `03-du-lieu.md`, mục 3.2.
- **Giả định dòng thẳng:** chữ viết lên dốc hoặc xuống dốc nhiều sẽ khó đọc theo từng cột, và lớp ghép đoạn chỉ căn đường chân chữ theo từng đoạn.
- **Dữ liệu ít:** tập huấn luyện chỉ có 4.433 dòng, nên kết quả phụ thuộc nhiều vào tăng cường dữ liệu [@puigcerver2017].
