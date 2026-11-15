# Triển khai trên Android

Trạng thái: Nháp

Tài liệu này mô tả cách đưa mô hình lên Android, cấu trúc ứng dụng, cách kiểm tra và cách cài đặt. Tài liệu dành cho người làm ứng dụng và người viết Chương 5 của báo cáo. Kết quả đo độ chính xác sau chuyển đổi nằm ở `07-nhat-ky-thi-nghiem.md`, mục 5.

## 1. Chuyển đổi mô hình

Mã `training/export_tflite.py` chuyển mô hình từ Keras sang `.tflite` và tạo ba bản: chưa lượng tử hóa, float16 và dynamic range [@google2026e]. Đề tài dùng bản float16, vì bản dynamic range làm CER của `m1_v2` vượt ngưỡng, theo `07-nhat-ky-thi-nghiem.md`, mục 5, và làm CER của `m1l_rr_e100` tăng 0,64 điểm phần trăm, theo mục 11.3 của tài liệu đó. Mô hình phải được dựng lại bằng tf-keras và chép trọng số sang, vì lớp LSTM của Keras 3 không chạy được sau chuyển đổi. Tệp tạo ra chỉ dùng các toán tử có sẵn của LiteRT, gồm cả toán tử LSTM gốc.

Toán tử LSTM của LiteRT giữ trạng thái giữa các lần chạy. Ứng dụng phải gọi `resetVariableTensors` trước mỗi dòng, nếu không kết quả của dòng sau sẽ phụ thuộc vào dòng trước.

## 2. Cấu trúc ứng dụng

Ứng dụng nằm trong thư mục `android/`, viết bằng Kotlin và không dùng thư viện giao diện ngoài. Thư viện ngoài duy nhất là LiteRT [@google2026c]. Bảng 1 ghi vai trò của từng tệp.

Bảng 1: Các tệp mã của ứng dụng

| Tệp | Vai trò |
| --- | --- |
| `MainActivity.kt` | Giao diện, chờ 350 ms sau khi nhấc bút rồi nhận dạng lại cả dòng |
| `InkView.kt` | Khung viết có hàng kẻ cao 12 mm, nhận ngón tay hoặc bút |
| `Ink.kt` | Gán nét vào hàng, ghép đoạn, vẽ ảnh |
| `Recognizer.kt` | Chạy mô hình và bộ giải mã trên một luồng nền |
| `CtcDecoder.kt`, `NGramModel.kt` | Beam search và mô hình ngôn ngữ |

Khi đã nhận được bút, ứng dụng bỏ qua các điểm chạm của ngón tay, để lòng bàn tay không tạo ra nét. Mô hình trong ứng dụng là bản float16 của `m1l_rr_e100`, chọn theo `07-nhat-ky-thi-nghiem.md`, mục 10.9. Bảng 2 ghi dung lượng các tệp đi kèm ứng dụng.

Bảng 2: Dung lượng các tệp đi kèm, đã đo

| Tệp | Dung lượng |
| --- | --- |
| `model.tflite`, bản float16 của `m1l_rr_e100` | 4,47 MB |
| `lm.bin` | 10,95 MB |
| Tổng | 15,43 MB |

Theo Bảng 2, tổng dung lượng thấp hơn ngưỡng 20 MB trong `02-yeu-cau-va-danh-gia.md`, mục 1. Mô hình M1 lớn làm tổng dung lượng tăng 2,45 MB so với mô hình `m1_v2` dùng trước đó.

## 3. Kiểm tra

### 3.1. Đối chiếu Python với Kotlin

Mã `training/export_assets.py` sinh một bộ mẫu từ bản Python, và `ParityTest.kt` kiểm tra bản Kotlin theo bộ mẫu đó. Ba ứng viên của bộ giải mã lấy từ đầu ra của chính mô hình trong ứng dụng, nên bộ mẫu được sinh lại mỗi khi đổi mô hình. Bảng 3 ghi nội dung và kết quả của phép đối chiếu, chạy lại với `m1l_rr_e100` ngày 11/11/2026.

Bảng 3: Kết quả đối chiếu Python với Kotlin

| Nội dung | Cách so | Kết quả |
| --- | --- | --- |
| Gán nét vào hàng, 12 trường hợp | Giống hệt | Đạt |
| Tọa độ sau ghép đoạn, 12 trường hợp | Sai lệch không quá 0,000001 | Đạt |
| Ảnh sau khi vẽ, 12 trường hợp | Điểm ảnh khác nhau dưới 0,05% | Đạt |
| Ba ứng viên của bộ giải mã, 3 dòng kiểm định | Giống hệt | Đạt |

### 3.2. Chạy thử trên máy ảo

Ứng dụng đã chạy trọn luồng trên máy ảo Android Pixel 6, với các nét giả lập bằng lệnh của máy ảo. Với mô hình `m1l_rr_e100`, một lần nhận dạng ba nét mất 237 ms, gồm 3 ms vẽ ảnh, 108 ms chạy mô hình và 125 ms giải mã. Với mô hình `m1_v2` dùng trước đó, lần đo tương tự mất 211 ms, trong đó mô hình chỉ chạy 38 ms. Mỗi mô hình chỉ được đo một lần, nên số liệu này chỉ xác nhận ứng dụng chạy được, không thay thế phép đo độ trễ trên điện thoại thật.

## 4. Cài đặt

Bản dựng dùng Android SDK và Gradle Wrapper trong `android/`:

1. Chạy `training/export_assets.py` để tạo các tệp đi kèm.
2. Trong thư mục `android/`, chạy `gradlew assembleDebug`.
3. Cài tệp `app/build/outputs/apk/debug/app-debug.apk` lên điện thoại bằng `adb install`.

## 5. Vấn đề chưa chốt

Bảng 4 ghi các việc cần điện thoại thật.

Bảng 4: Các việc còn lại trên điện thoại thật

| Việc | Ảnh hưởng | Cách làm |
| --- | --- | --- |
| Đo độ trễ theo `02-yeu-cau-va-danh-gia.md`, mục 2.5 | Cổng 3. Mô hình M1 lớn chạy lâu hơn `m1_v2` khoảng 2,8 lần trên máy ảo | Viết các dòng dài trên một máy tầm trung, ghi trung vị và phân vị 95 |
| Xác nhận mô hình chạy trên điện thoại thật | Cổng 1 | Cài ứng dụng và viết thử |
