# Dữ liệu

Trạng thái: Nháp

Tài liệu này quy định nguồn dữ liệu, cách chia tập, tiền xử lý, cách sinh dòng ngắt mô phỏng, các biện pháp chống rò rỉ và quy trình thu tập tự thu. Tài liệu dành cho người viết mã xử lý dữ liệu, người chạy thí nghiệm và người viết Chương 3 của báo cáo. Các tham số chưa qua thí nghiệm đều là giá trị dự kiến, và các điểm chưa kiểm chứng được liệt kê ở mục 7.

## 1. Tổng quan các nguồn

Đề tài huấn luyện mô hình trên chữ viết tay dạng ảnh của bộ dữ liệu HANDS-VNOnDB (VNOnDB). Các tệp nét gốc không tải được, vì trang của bộ dữ liệu [@iapr2026] không truy cập được và đề tài không xin được từ nhóm tác giả. Ứng dụng vẫn thu nét và vẫn ghép dòng ngắt, sau đó vẽ dòng thành ảnh để đưa vào mô hình. Bảng 1 ghi vai trò và quy mô của từng nguồn.

Bảng 1: Các nguồn dữ liệu và vai trò

| Nguồn | Vai trò | Quy mô |
| --- | --- | --- |
| Bản ảnh VNOnDB cấp dòng | Huấn luyện và kiểm thử chính | 7.296 ảnh kèm nhãn |
| `train.ln`, `val.ln`, `test.ln` | Chia tập huấn luyện, tập kiểm định, tập kiểm thử | 3 danh sách tên tệp |
| Bản ảnh VNOnDB cấp từ | Đối chiếu nhãn, chưa dùng để huấn luyện | 110.746 ảnh kèm nhãn |
| Dòng ngắt mô phỏng | Chỉnh ngưỡng và kiểm thử lớp ghép đoạn | Sinh tự động từ tập tự thu |
| Tập tự thu | Chỉnh ngưỡng lớp ghép đoạn, kiểm thử cuối trên điện thoại | Dự kiến 30 người, mỗi người 20 dòng |

## 2. Bộ dữ liệu VNOnDB

### 2.1. Quy mô và cách chia

Bộ dữ liệu VNOnDB gồm 1.146 đoạn văn và 7.296 dòng do 200 người viết [@vohtr2018a]. Bản gốc lưu nét theo định dạng Ink Markup Language (InkML). Đề tài dùng bản đã vẽ thành ảnh, thư mục `VNOnDB_processed`, gồm 7.296 dòng và 1.144 đoạn văn. Kết quả ở mục này do đề tài đếm trực tiếp trên bản ảnh ngày 09/11/2026.

Cách chia lấy từ các danh sách của kho mã HTR-ConvText [@dairgroup2026]. Số dòng của các danh sách trùng với bản chia của cuộc thi nhận dạng chữ viết tay tiếng Việt dạng nét (VOHTR) [@le2019]. Đề tài không chia lại, để kết quả so sánh được với các công bố. Bảng 2 ghi quy mô của từng tập.

Bảng 2: Thống kê bản ảnh VNOnDB theo từng tập, đã đo

| Đại lượng | Tập huấn luyện | Tập kiểm định | Tập kiểm thử | Tổng |
| --- | --- | --- | --- | --- |
| Số dòng | 4.433 | 1.229 | 1.634 | 7.296 |
| Số ký tự cấp dòng | 298.212 | 83.806 | 111.393 | 493.411 |
| Số từ | 66.991 | 18.640 | 25.115 | 110.746 |
| Số mã người viết | 106 | 34 | 60 | 200 |

Bảng 2 khớp với Le và cộng sự về số dòng, số từ và số ký tự của hai tập đầu [@le2019]. Tập kiểm thử có 111.393 ký tự, ít hơn con số 112.769 của nguồn này 1.376 ký tự. Mục 7 ghi lại vấn đề này.

Mỗi dòng có trung bình khoảng 15 từ và 68 ký tự. Mỗi từ có trung bình khoảng 3,3 ký tự, nên "từ" của VNOnDB tương ứng với âm tiết. Nhãn cấp dòng dùng 161 ký tự khác nhau.

### 2.2. Định dạng

Bảng 3 ghi các thành phần đề tài cần đọc từ bản ảnh và danh sách chia tập.

Bảng 3: Các thành phần cần đọc

| Thành phần | Nội dung | Cách dùng trong đề tài |
| --- | --- | --- |
| `InkData_line_processed/*.png` | Ảnh một dòng, 8 bit mỗi kênh, nền trắng, kênh trong suốt luôn bằng 255 | Đầu vào của tiền xử lý |
| `InkData_line_processed/*.txt` | Nhãn một dòng, UTF-8, chuẩn NFC | Tạo chuỗi đích |
| Trường thứ hai của tên tệp | Mã số, có 200 giá trị khác nhau | Coi là mã người viết khi kiểm tra rò rỉ |
| `train.ln`, `val.ln`, `test.ln` | Mỗi dòng ghi một tên tệp ảnh | Xác định dòng thuộc tập nào |

### 2.3. Đặc điểm chi phối thiết kế

- **Không có nét:** bản ảnh không có tọa độ, thứ tự viết và điểm nhấc bút. Đầu vào của mô hình vì thế là ảnh của dòng.
- **Ảnh vẽ từ nét:** ảnh có nền trắng và nét khử răng cưa, không phải ảnh chụp giấy. Ứng dụng vẽ được ảnh tương tự từ nét thu trên điện thoại.
- **Ảnh đã co vừa khung:** 7.288 trong 7.296 ảnh dòng rộng đúng 523 điểm ảnh. Chiều cao từ 40 đến 396 điểm ảnh, và 244 ảnh cao hơn 120 điểm ảnh.
- **Lề trắng lớn:** trên mẫu 400 ảnh dòng, nét chữ chiếm trung vị 52% chiều cao ảnh.
- **Thu bằng bút:** người viết dùng bút trên máy tính bảng Fujitsu ở 120 Hz [@vohtr2018a], khác với ngón tay trên điện thoại.
- **Cấp từ không khớp cấp dòng:** nhãn cấp từ không có dấu câu, còn nhãn cấp dòng có 16.085 ký tự dấu câu. Sau khi bỏ dấu câu, 6.299 trong 7.296 dòng khớp với các từ của dòng đó. Ảnh cấp từ còn bị phóng to, nên đề tài chưa dùng cấp từ để huấn luyện.
- **Văn bản từ VieTreeBank:** người viết chép văn bản lấy từ kho VieTreeBank [@le2019], nên các biện pháp ở mục 5 phải tính đến nguồn chung này.

### 2.4. Giấy phép

Dữ liệu được cấp theo giấy phép Creative Commons cho mục đích học thuật và nghiên cứu, không cho dùng thương mại [@vohtr2018a]. Đề tài tuân theo các quy định sau:

- Không đưa dữ liệu vào kho mã. Kho mã chỉ lưu danh sách tệp của từng tập và mã băm của dữ liệu.
- Báo cáo phải ghi rõ nguồn của bản ảnh và nguồn của danh sách chia tập.
- Ứng dụng và mô hình, nếu công bố, phải ghi rõ mục đích phi thương mại.
- Muốn dùng cho mục đích khác thì liên hệ nhóm tác giả trước.

## 3. Tiền xử lý

Một quy trình tiền xử lý dùng chung cho cả huấn luyện và ứng dụng. Trên điện thoại, quy trình này chạy sau lớp ghép đoạn, nên đầu vào luôn là một dòng liền hoặc một dòng ảo. Bản Python và bản Kotlin phải cho cùng kết quả trên một bộ mẫu kiểm tra chung.

### 3.1. Chuẩn hóa nhãn

Nhãn của VNOnDB, kho văn bản của n-gram, nhãn của tập tự thu và chuỗi đọc ra khi chấm điểm đều qua cùng một bước chuẩn hóa. Nếu không, tỷ lệ lỗi sẽ bị đội lên và n-gram sẽ đếm một âm tiết thành hai.

1. Đưa chuỗi về dạng chuẩn NFC.
2. Thống nhất vị trí dấu thanh theo kiểu cũ, ví dụ "hòa" và "thủy".
3. Thay nhiều khoảng trắng liền nhau bằng một khoảng trắng và bỏ khoảng trắng ở hai đầu.

Bước này không đổi chữ hoa, chữ thường và dấu câu.

### 3.2. Vẽ dòng thành ảnh trên điện thoại

Ứng dụng vẽ nét của dòng liền hoặc dòng ảo lên nền trắng, theo cách giống ảnh huấn luyện. Bản ảnh VNOnDB cho thấy nét được co đều hai trục vào khung rộng 523, cao 396 điểm ảnh, và nét có khử răng cưa. Độ dày nét và cách co chính xác chưa biết, nên phải ước lượng từ ảnh huấn luyện.

Lệch giữa ảnh huấn luyện và ảnh vẽ trên điện thoại là rủi ro lớn nhất của hướng đọc ảnh. Đề tài chọn độ dày nét theo tỷ lệ lỗi ký tự (CER) trên nhóm chỉnh của tập tự thu, theo mục 6.

### 3.3. Chuẩn hóa ảnh

Huấn luyện và ứng dụng cùng đưa ảnh qua các bước sau:

1. Chuyển ảnh về một kênh xám.
2. Cắt lề trắng theo khung bao của nét.
3. Co ảnh giữ nguyên tỷ lệ để ảnh nằm trong khung rộng 512, cao 64 điểm ảnh (dự kiến).
4. Thêm nền trắng vào phần còn thiếu của khung.

Cỡ khung lấy theo Pham và cộng sự [@pham2025], và cần được chọn lại trên tập kiểm định. Đề tài cũng thử bỏ bước 2, vì cắt lề làm chiều cao ảnh phụ thuộc vào chữ có phần trên hay phần dưới dài.

### 3.4. Tăng cường dữ liệu

Tăng cường chỉ áp dụng cho tập huấn luyện, gồm các phép sau:

- Co giãn và nghiêng cả dòng.
- Làm dày hoặc mỏng nét, để mô hình bớt phụ thuộc vào cách vẽ.
- Làm nhiễu nhẹ hình dạng nét.
- Mô phỏng chỗ nối: cắt ảnh tại khoảng trống giữa hai từ, rồi dịch dọc và co nhẹ từng phần (dự kiến).

Mức của từng phép sẽ được chốt trong `05-ke-hoach-thi-nghiem.md` (chưa viết).

## 4. Dòng ngắt mô phỏng

Bộ mô phỏng sinh dòng ngắt từ dòng liền của tập tự thu, vì bản ảnh VNOnDB không có nét để cắt. Bộ mô phỏng chạy qua đúng các bước mà ứng dụng dùng. Nhờ vậy, lỗi gán nét vào hàng cũng được tính vào kết quả. Các bước như sau:

1. Chọn từ 1 đến 2 ranh giới từ làm chỗ ngắt (dự kiến).
2. Tách các nét của dòng thành các đoạn tại chỗ ngắt.
3. Đặt mỗi đoạn lên một hàng của khung kẻ ảo.
4. Thêm lệch cỡ chữ và lệch đường chân chữ riêng cho từng đoạn.
5. Chạy bước gán nét vào hàng và lớp ghép đoạn để tạo dòng ảo.
6. Vẽ dòng ảo thành ảnh theo mục 3.2.

Bước 4 là bắt buộc. Nếu chỉ dịch các đoạn rồi ghép lại, lớp ghép đoạn sẽ trả về đúng dữ liệu gốc và kết quả sẽ đẹp giả tạo. Dòng ngắt sinh từ nhóm chỉnh dùng để chỉnh ngưỡng, còn dòng ngắt sinh từ nhóm kiểm thử dùng để kiểm thử.

## 5. Chống rò rỉ dữ liệu

Các tập dùng chung người viết hoặc văn bản sẽ làm kết quả cao hơn thực tế. Đề tài áp dụng các biện pháp sau:

- **Người viết:** trường thứ hai của tên tệp không có giá trị nào xuất hiện ở hai tập. Trường này có đúng 200 giá trị, bằng số người viết, nhưng chưa được xác nhận là mã người viết. Báo cáo phải ghi rõ đây là suy luận.
- **Câu trùng:** cả 200 người đều chép từ VieTreeBank. Đề tài đã đo được 146 trong 1.634 dòng kiểm thử (8,9%) và 88 trong 1.229 dòng kiểm định (7,2%) có văn bản giống hệt một dòng huấn luyện. Báo cáo ghi các tỷ lệ này, và ghi thêm CER trên 1.488 dòng kiểm thử còn lại.
- **Dữ liệu cấp từ:** dữ liệu cấp từ được tách ra từ chính các dòng. Nếu sau này dùng để huấn luyện thì chỉ lấy từ thuộc tập huấn luyện.
- **N-gram:** n-gram học từ văn bản của tập huấn luyện và Wikipedia tiếng Việt [@wikimedia2026a], là kho văn bản ngoài VieTreeBank. Phải loại khỏi kho các câu trùng với tập kiểm thử và các câu dùng làm đề của tập tự thu.
- **Chỉnh tham số:** trọng số n-gram chỉ được chỉnh trên tập kiểm định. Ngưỡng của lớp ghép đoạn và độ dày nét chỉ được chỉnh trên nhóm chỉnh của tập tự thu.
- **Tập kiểm thử:** chỉ chạy một lần ở cuối, theo `02-yeu-cau-va-danh-gia.md`, mục 5.

## 6. Tập tự thu

Tập tự thu là nguồn dữ liệu nét duy nhất của đề tài, và là thước đo cuối cho việc viết bằng ngón tay trên điện thoại. Tập này không dùng để huấn luyện. Người viết chia thành hai nhóm không trùng nhau, đều là người không có trong VNOnDB:

- **Nhóm chỉnh:** khoảng 10 người (dự kiến), dùng để chỉnh ngưỡng của lớp ghép đoạn và độ dày nét.
- **Nhóm kiểm thử:** 20 người (dự kiến), chỉ chạy một lần ở cuối.

Mỗi người viết 10 dòng liền và 10 dòng ngắt. Quy trình thu gồm các bước sau:

1. Người tham gia đọc và ký phiếu đồng ý. Phiếu phải nói rõ dữ liệu sẽ được công bố, vì tập tự thu là một sản phẩm đầu ra của đề tài.
2. Hệ thống gán cho người tham gia một mã ẩn danh và không lưu tên.
3. Người tham gia thuộc một trong hai nhóm đổi chéo. Hai nhóm đổi chéo nội dung của dòng liền và dòng ngắt, để so sánh công bằng.
4. Người tham gia cầm dọc điện thoại và viết bằng ngón tay trong ứng dụng thu. Dòng liền viết trên khung cuộn ngang, dòng ngắt viết trên khung có hàng kẻ.
5. Ứng dụng lưu tọa độ, thứ tự nét, thời điểm của từng điểm, kích thước màn hình và mã thiết bị.
6. Người thu kiểm tra nhãn theo câu đề, ghi lại các chỗ người viết chép sai đề, rồi chuẩn hóa nhãn theo mục 3.1.

Câu đề lấy từ các bài Wikipedia tiếng Việt được tách riêng, và các bài này bị loại khỏi kho văn bản của n-gram. Văn bản Wikipedia được cấp theo giấy phép Creative Commons Attribution-Share-Alike 4.0 [@wikimedia2026b], nên khi công bố tập tự thu phải ghi nguồn của câu đề và giữ giấy phép tương ứng. Cả hai điều kiện viết đều cầm dọc, để hướng cầm máy không ảnh hưởng đến so sánh.

Tệp tự thu lưu thành tệp `.json` theo lược đồ `thu-net/1` của công cụ `tools/thu-net/`. Thời điểm của từng điểm chỉ dùng để phân tích, không đưa vào mô hình.

## 7. Vấn đề chưa chốt

Bảng 4 ghi các điểm chưa kiểm chứng được hoặc còn cần quyết định, cùng cách chốt từng điểm.

Bảng 4: Các vấn đề chưa chốt về dữ liệu

| Vấn đề | Ảnh hưởng | Cách chốt |
| --- | --- | --- |
| Chưa ghi nhận nguồn của bản ảnh `VNOnDB_processed` | Báo cáo và giấy phép | Ghi nguồn trước khi viết Chương 3 |
| Cách vẽ ảnh huấn luyện chưa biết | Ảnh vẽ trên điện thoại có thể lệch ảnh huấn luyện | Ước lượng độ dày nét từ ảnh, so CER trên nhóm chỉnh |
| Trường thứ hai của tên tệp chưa xác nhận là mã người viết | Mức tin cậy của phép kiểm tra rò rỉ | Hỏi nơi cung cấp bản ảnh, nếu không được thì ghi là suy luận |
| Tập kiểm thử ít hơn nguồn 1.376 ký tự, số đoạn văn ít hơn 2 | Giá trị $N$ khi tính tỷ lệ lỗi | Tìm các dòng có nhãn bất thường, ghi kết quả vào báo cáo |
| Hai giấy phép khác nhau trong kho HTR-ConvText | Việc lưu danh sách chia tập vào kho mã | Đọc lại giấy phép, ghi nguồn khi lưu |
| Cách xác định ranh giới từ trong dòng liền tự thu | Bộ mô phỏng cần biết nét nào thuộc từ nào | Tìm các khoảng trống lớn theo số khoảng trắng của câu đề, kiểm tra bằng tay |
| Số chỗ ngắt khi mô phỏng | Một dòng khoảng 15 từ có thể cần nhiều hàng hơn 3 khi cầm dọc | Cho từ 2 đến 3 người viết thử trên điện thoại, đếm số từ mỗi hàng |
