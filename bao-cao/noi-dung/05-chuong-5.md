# CHƯƠNG 5. TRIỂN KHAI TRÊN ANDROID

Chương này trình bày cách đưa mô hình lên Android, cấu trúc của ứng dụng, cách kiểm tra bản Kotlin cho cùng kết quả với bản Python, và cách cài đặt ứng dụng.

## 5.1. Chuyển đổi mô hình

Mã `training/export_tflite.py` chuyển mô hình từ Keras sang định dạng `.tflite` của LiteRT và tạo ba bản: chưa lượng tử hóa, float16 và dynamic range [@google2026e]. Đề tài dùng bản float16, vì bản dynamic range làm CER tăng 0,64 điểm phần trăm, còn bản float16 gần như giữ nguyên CER mà chỉ nặng bằng nửa bản chưa lượng tử hóa, theo mục 4.3.3.

Mô hình phải được dựng lại bằng tf-keras và chép trọng số sang trước khi chuyển đổi, vì lớp LSTM của Keras 3 không chạy được sau chuyển đổi. Tệp tạo ra chỉ dùng các toán tử có sẵn của LiteRT, gồm cả toán tử LSTM gốc, nên không cần thư viện bổ sung trên điện thoại. Toán tử LSTM của LiteRT giữ trạng thái giữa các lần chạy, nên ứng dụng gọi `resetVariableTensors` trước mỗi dòng. Nếu không, kết quả của dòng sau sẽ phụ thuộc vào dòng trước.

## 5.2. Cấu trúc ứng dụng

Ứng dụng viết bằng Kotlin và không dùng thư viện giao diện ngoài. Thư viện ngoài duy nhất của bản phát hành là LiteRT [@google2026c]. Bản debug có thêm ML Kit và quyền truy cập mạng, chỉ để chạy bài đo so sánh ở mục 4.6.3. Bảng {{bang:tep-ung-dung}} ghi vai trò của từng tệp mã.

| Tệp | Vai trò |
| --- | --- |
| `MainActivity.kt` | Giao diện, chờ 350 ms sau khi nhấc ngón tay rồi nhận dạng lại cả dòng |
| `InkView.kt` | Khung viết có hàng kẻ cao 12 mm, nhận ngón tay hoặc bút |
| `Ink.kt` | Gán nét vào hàng, ghép đoạn và vẽ dòng thành ảnh |
| `Recognizer.kt` | Chạy mô hình và bộ giải mã trên một luồng nền |
| `CtcDecoder.kt`, `NGramModel.kt` | Beam search và mô hình ngôn ngữ n-gram âm tiết |
| `CharNGramModel.kt` | Mô hình ngôn ngữ n-gram ký tự, theo mục 4.8 |
| `BenchTest.kt` | Bài đo trên thiết bị: chạy cả luồng của ứng dụng và chạy ML Kit trên nét của tập tự thu |

Bảng: Các tệp mã của ứng dụng Android {#bang:tep-ung-dung w=32,68}

Khi người dùng viết, khung viết ghi lại tọa độ của từng nét theo thứ tự viết. Mỗi lần người dùng nhấc ngón tay và dừng quá 350 ms, ứng dụng chạy lại cả luồng ở Hình {{hinh:luong}} trên mọi nét đã có, nên kết quả tạm thời luôn hiện cho cả dòng. Việc nhận dạng chạy trên một luồng nền để khung viết không bị đứng. Người dùng chọn một trong ba ứng viên hoặc bấm Xong để chốt dòng. Khi đã nhận được bút, ứng dụng bỏ qua các điểm chạm của ngón tay, để lòng bàn tay đặt trên màn hình không tạo ra nét.

Mô hình trong ứng dụng là bản float16 của `m1l_rr_e100`, chọn theo mục 4.4.3. Bộ giải mã dùng thêm n-gram ký tự bậc 6 theo mục 4.8. Bảng {{bang:dung-luong}} ghi dung lượng các tệp đi kèm ứng dụng.

| Tệp | Dung lượng |
| --- | --- |
| `model.tflite`, bản float16 của `m1l_rr_e100` | 4,47 MB |
| `lm.bin`, mô hình ngôn ngữ n-gram âm tiết | 10,95 MB |
| `clm.bin`, mô hình ngôn ngữ n-gram ký tự | 4,10 MB |
| Tổng | 19,53 MB |

Bảng: Dung lượng các tệp đi kèm ứng dụng {#bang:dung-luong w=70,30 can=t,p}

Theo Bảng {{bang:dung-luong}}, tổng dung lượng thấp hơn ngưỡng 20 MB ở Bảng {{bang:muc-tieu}}. Cấu hình đã chốt ở mục 4.6 chưa có `clm.bin` và nặng 15,43 MB. Hai tệp nhỏ còn lại là bộ ký tự và tệp tham số gồm $\alpha$, $\beta$, độ dày nét, trọng số của n-gram ký tự và điểm thưởng mỗi ký tự.

## 5.3. Kiểm tra

### 5.3.1. Đối chiếu Python với Kotlin

Mọi kết quả ở Chương 4 được đo bằng bản Python, nên bản Kotlin trong ứng dụng phải cho cùng kết quả. Mã `training/export_assets.py` sinh một bộ mẫu từ bản Python, và phép thử `ParityTest.kt` kiểm tra bản Kotlin theo bộ mẫu đó. Ba ứng viên của bộ giải mã lấy từ đầu ra của chính mô hình trong ứng dụng, nên bộ mẫu được sinh lại mỗi khi đổi mô hình. Bảng {{bang:doi-chieu-kotlin}} ghi nội dung và kết quả của phép đối chiếu với mô hình được chọn.

| Nội dung | Cách so | Kết quả |
| --- | --- | --- |
| Gán nét vào hàng, 12 trường hợp | Giống hệt | Đạt |
| Tọa độ sau ghép đoạn, 12 trường hợp | Sai lệch không quá 0,000001 | Đạt |
| Ảnh sau khi vẽ, 12 trường hợp | Số điểm ảnh khác nhau dưới 0,05% | Đạt |
| Ba ứng viên của bộ giải mã không có n-gram ký tự, 8 dòng kiểm định | Giống hệt | Đạt |
| Ba ứng viên của bộ giải mã có n-gram ký tự, 8 dòng kiểm định | Giống hệt | Đạt |

Bảng: Kết quả đối chiếu bản Python với bản Kotlin {#bang:doi-chieu-kotlin w=40,40,20 can=t,t,g}

Bộ mẫu gồm cả các trường hợp khó của lớp ghép đoạn, như chân chữ vượt đường kẻ, nét dấu viết sau và khoảng trống lớn trong một hàng. Phép đối chiếu cho thấy bản Kotlin và bản Python cho cùng kết quả ở mọi bước, nên các số liệu ở Chương 4 áp dụng được cho ứng dụng.

Ngoài bộ mẫu, bài đo `BenchTest.kt` chạy cả luồng của ứng dụng trên thiết bị với 168 dòng của nhóm chỉnh, từ ghép đoạn, vẽ ảnh, chạy mô hình đến giải mã. Trên máy ảo, ứng dụng cho cùng kết quả với bản Python ở cả 168 dòng, với cả bộ giải mã có và không có n-gram ký tự.

### 5.3.2. Chạy thử trên máy ảo và điện thoại thật

Ứng dụng đã chạy trọn luồng trên máy ảo Android Pixel 6, với các nét giả lập bằng lệnh của máy ảo. Với mô hình được chọn, một lần nhận dạng ba nét mất 237 ms, gồm 3 ms vẽ ảnh, 108 ms chạy mô hình và 125 ms giải mã. Với mô hình `m1_v2` dùng trước đó, lần đo tương tự mất 211 ms, trong đó mô hình chỉ chạy 38 ms. Mỗi mô hình chỉ được đo một lần trên máy ảo, nên số liệu này chỉ xác nhận ứng dụng chạy được không cần mạng.

Bản dựng release của ứng dụng cũng đã được cài lên điện thoại Samsung Galaxy S23 Ultra chạy Android 15. Ứng dụng nạp mô hình không cần mạng và trả về ba ứng viên. Một lần nhận dạng ba nét ngắn trên điện thoại này mất 112 ms, gồm 4 ms vẽ ảnh, 94 ms chạy mô hình và 13 ms giải mã. Đây là một lần đo trên điện thoại cao cấp với dòng rất ngắn, nên độ trễ theo mục 1.5.3 vẫn cần được đo với các dòng dài trên một điện thoại tầm trung.

## 5.4. Cài đặt

Bản dựng dùng Android SDK và Gradle Wrapper trong thư mục `android/` của kho mã, theo các bước sau:

1. Chạy `training/export_assets.py` để tạo các tệp đi kèm từ mô hình đã chọn.
2. Trong thư mục `android/`, chạy `gradlew assembleDebug`.
3. Cài tệp `app/build/outputs/apk/debug/app-debug.apk` lên điện thoại bằng `adb install`.

Bản phát hành, tạo bằng `gradlew assembleRelease`, không chứa ML Kit và không cần quyền truy cập mạng, nên chạy được khi điện thoại tắt mạng.
