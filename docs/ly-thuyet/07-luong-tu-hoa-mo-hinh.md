# Lượng tử hóa mô hình

Trạng thái: Nháp

Tài liệu này trình bày lượng tử hóa sau huấn luyện, tức lưu trọng số của mô hình bằng ít bit hơn sau khi đã huấn luyện xong. Đề tài dùng kỹ thuật này ở bước chuyển mô hình sang LiteRT, để mô hình nhỏ hơn khi đưa lên điện thoại. Tài liệu dành cho người làm phần triển khai và người viết phần cơ sở lý thuyết của báo cáo.

## 1. Bài toán

Đầu vào là mô hình đã huấn luyện, mỗi trọng số lưu bằng số thực 32 bit. Đầu ra là mô hình cho kết quả gần như cũ nhưng chiếm ít dung lượng hơn. Mô hình còn phải chạy được trên điện thoại mà không có tập dữ liệu kèm theo. Vì vậy đề tài chỉ xét các cách không cần tập hiệu chỉnh.

## 2. Nguyên lý

### 2.1. Lượng tử hóa sang số nguyên

Lượng tử hóa sang số nguyên 8 bit biểu diễn mỗi trọng số bằng một số nguyên, cùng một bước lượng tử và một điểm không [@jacob2017]:

$$
\tilde{\theta} = \gamma \, (\nu - \zeta) \tag{1}
$$

trong đó $\tilde{\theta}$ là giá trị khôi phục của trọng số $\theta$, $\nu$ là số nguyên được lưu, $\gamma$ là bước lượng tử và $\zeta$ là điểm không, tức số nguyên ứng với giá trị thực 0. Với khoảng giá trị từ $\theta_{\min}$ đến $\theta_{\max}$, bước lượng tử bằng:

$$
\gamma = \frac{\theta_{\max} - \theta_{\min}}{255} \tag{2}
$$

trong đó $\theta_{\min}$ và $\theta_{\max}$ là giá trị nhỏ nhất và lớn nhất của nhóm trọng số. Sai số của mỗi trọng số không quá $\gamma / 2$, nên nhóm trọng số có khoảng giá trị rộng sẽ có sai số lớn.

### 2.2. Lượng tử hóa dynamic range

Cách này lưu trọng số bằng số nguyên 8 bit, còn giá trị kích hoạt vẫn là số thực khi chạy [@google2026e]. Cách này không cần dữ liệu mẫu, giảm dung lượng khoảng 4 lần và thường chạy nhanh hơn.

### 2.3. Lượng tử hóa float16

Cách này lưu trọng số bằng số thực 16 bit [@google2026e]. Số thực 16 bit có sai số tương đối nhỏ ở mọi độ lớn, nên hầu như không làm giảm độ chính xác. Dung lượng giảm khoảng 2 lần.

## 3. Ví dụ minh họa

Giả sử một nhóm trọng số có giá trị từ $-1{,}2$ đến $0{,}8$. Theo công thức (2), bước lượng tử bằng $2 / 255 \approx 0{,}00784$, và điểm không bằng $1{,}2 / 0{,}00784 \approx 153$. Trọng số $\theta = 0{,}5$ được lưu thành $\nu = \text{round}(0{,}5 / 0{,}00784) + 153 = 64 + 153 = 217$.

Theo công thức (1), giá trị khôi phục bằng $0{,}00784 \times (217 - 153) \approx 0{,}502$, lệch khoảng 0,002 so với giá trị gốc. Sai số này nhỏ với một trọng số, nhưng cộng dồn qua nhiều lớp và nhiều bước của lớp LSTM.

Ví dụ thứ hai tính dung lượng của mô hình M1, có 1.005.761 tham số. Bảng 1 so kết quả tính với dung lượng đo được của tệp `.tflite`, phần chênh là mô tả cấu trúc của mô hình.

Bảng 1: Dung lượng của mô hình M1 theo cách lưu trọng số

| Cách lưu | Số byte mỗi trọng số | Dung lượng tính | Dung lượng đo |
| --- | --- | --- | --- |
| Số thực 32 bit | 4 | 4,02 MB | 4,03 MB |
| Float16 | 2 | 2,01 MB | 2,03 MB |
| Dynamic range | 1 | 1,01 MB | 1,03 MB |

## 4. Áp dụng trong đề tài

- **So sánh:** đề tài đo cả hai cách trên toàn bộ tập kiểm định, theo `07-nhat-ky-thi-nghiem.md`, mục 5.
- **Lựa chọn:** đề tài dùng float16. Dynamic range làm tỷ lệ lỗi ký tự (CER) vượt ngưỡng, còn float16 cho kết quả gần như bản gốc.
- **Dung lượng:** với M1, float16 làm mô hình tăng thêm khoảng 1 MB so với dynamic range. Với M1 lớn, mô hình đang dùng trong ứng dụng, mức tăng là khoảng 2,2 MB, theo `07-nhat-ky-thi-nghiem.md`, mục 11.3. Tổng dung lượng vẫn thấp hơn ngưỡng 20 MB trong `02-yeu-cau-va-danh-gia.md`, mục 1.
- **Cách chuyển đổi:** các bước cụ thể nằm trong `06-trien-khai-android.md`, mục 1.

## 5. Hạn chế

- **Độ chính xác giảm không đều:** lỗi do lượng tử hóa dynamic range phụ thuộc vào khoảng giá trị của từng nhóm trọng số, nên phải đo lại trên dữ liệu thật sau mỗi lần chuyển đổi.
- **Float16 không nhanh hơn trên mọi máy:** khi chạy bằng CPU, trọng số thường được đổi lại sang số thực 32 bit, nên lợi ích chính là dung lượng.
- **Phụ thuộc thời gian đo:** thời gian đo trên máy tính không phản ánh thời gian trên điện thoại, nên độ trễ phải đo trên máy thật theo `02-yeu-cau-va-danh-gia.md`, mục 2.5.
