# Dữ liệu

Trạng thái: Nháp

Tài liệu này quy định nguồn dữ liệu, cách chia tập, tiền xử lý, cách sinh dòng ngắt mô phỏng, các biện pháp chống rò rỉ và quy trình thu tập tự thu. Tài liệu dành cho người viết mã xử lý dữ liệu, người chạy thí nghiệm và người viết Chương 3 của báo cáo. Các tham số chưa qua thí nghiệm đều là giá trị dự kiến, và các điểm chưa kiểm chứng được liệt kê ở mục 7.

## 1. Tổng quan các nguồn

Đề tài dùng bốn nguồn dữ liệu, mỗi nguồn có một vai trò riêng. Bảng 1 ghi vai trò và quy mô của từng nguồn. Quy mô của hai tệp nén lấy từ trang của bộ dữ liệu [@iapr2026] và chưa kiểm chứng. Quy mô của hai nguồn còn lại là dự kiến.

Bảng 1: Các nguồn dữ liệu và vai trò

| Nguồn | Vai trò | Quy mô |
| --- | --- | --- |
| `InkData_line.zip` | Huấn luyện và kiểm thử chính | Tệp 239 MB |
| `InkData_word.zip` | Huấn luyện trước ở cấp từ, ghép dòng giả | Tệp 246 MB |
| Dòng ngắt mô phỏng | Chỉnh ngưỡng và kiểm thử lớp ghép đoạn, tăng cường dữ liệu | Sinh tự động từ VNOnDB |
| Tập tự thu | Kiểm thử cuối trên điện thoại | 20 người, mỗi người 20 dòng |

## 2. Bộ dữ liệu VNOnDB

### 2.1. Quy mô và cách chia

Bộ dữ liệu HANDS-VNOnDB (VNOnDB) gồm 1.146 đoạn văn và 7.296 dòng do 200 người viết [@vohtr2018a]. Dữ liệu được cung cấp ở cấp đoạn văn, rồi được tách thành cấp dòng và cấp từ [@le2019]. Đề tài dùng bản chia có sẵn của cuộc thi nhận dạng chữ viết tay tiếng Việt dạng nét (VOHTR), và không chia lại, để kết quả so sánh được với các công bố. Bảng 2 ghi quy mô của từng tập.

Bảng 2: Thống kê VNOnDB theo [@le2019], cột Tổng do đề tài cộng

| Cấp | Đại lượng | Tập huấn luyện | Tập kiểm định | Tập kiểm thử | Tổng |
| --- | --- | --- | --- | --- | --- |
| Dòng | Số dòng | 4.433 | 1.229 | 1.634 | 7.296 |
| Dòng | Số nét | 284.642 | 86.079 | 110.013 | 480.734 |
| Dòng | Số ký tự | 298.212 | 83.806 | 112.769 | 494.787 |
| Từ | Số từ | 66.991 | 18.640 | 25.115 | 110.746 |
| Từ | Số nét | 272.320 | 82.166 | 105.973 | 460.459 |
| Từ | Số ký tự | 222.586 | 62.370 | 83.499 | 368.455 |

Theo Bảng 2, mỗi dòng có trung bình khoảng 15 từ, 68 ký tự và 66 nét. Mỗi từ có trung bình khoảng 3,3 ký tự, nên "từ" của VNOnDB tương ứng với âm tiết.

### 2.2. Định dạng

Dữ liệu lưu theo định dạng Ink Markup Language (InkML), mã hóa UTF-8 [@vohtr2018a]. Bảng 3 ghi các thành phần đề tài cần đọc từ mỗi tệp.

Bảng 3: Các thành phần cần đọc trong tệp InkML

| Thành phần | Nội dung | Cách dùng trong đề tài |
| --- | --- | --- |
| `Writer_ID` trong phần đầu tệp | Mã người viết | Kiểm tra người viết không trùng giữa các tập |
| `traceGroup` | Một nhóm nét có nhãn chung | Ghép nhãn của dòng, xác định ranh giới từ nếu nhóm tương ứng với từ |
| `Tg_Truth` | Nhãn văn bản của nhóm nét | Tạo chuỗi đích |
| `trace` | Một nét, gồm dãy cặp tọa độ $x$, $y$ | Đầu vào của tiền xử lý |

Tệp có các trường khác về người viết như tuổi, giới tính và nghề nghiệp. Đề tài không dùng các trường này làm đặc trưng.

### 2.3. Đặc điểm chi phối thiết kế

- **Chỉ có tọa độ:** mẫu tệp của bộ dữ liệu chỉ ghi $x$ và $y$ cho mỗi điểm, thời gian chỉ có một mốc cho cả tệp [@vohtr2018a]. Đầu vào của mô hình vì thế không chứa thời gian dừng.
- **Thu bằng bút:** người viết dùng bút trên máy tính bảng Fujitsu ở 120 Hz [@vohtr2018a], khác với ngón tay trên điện thoại.
- **Có nét trễ:** dấu thanh, dấu phụ và các chữ Đ, đ, j, t, f thường có nét trễ, có khi viết sau cả một câu [@vohtr2018a]. Điều ngược lại cũng xảy ra: dấu thanh và dấu phụ không phải lúc nào cũng là nét trễ.
- **Không có nhãn từng nét:** trang của bộ dữ liệu không mô tả nhãn cho từng nét, nên đề tài không biết sẵn nét nào là dấu thanh hay dấu phụ.
- **Văn bản từ VieTreeBank:** người viết chép văn bản lấy từ kho VieTreeBank [@le2019], nên các biện pháp ở mục 5 phải tính đến nguồn chung này.

### 2.4. Giấy phép

Dữ liệu được cấp theo giấy phép Creative Commons cho mục đích học thuật và nghiên cứu, không cho dùng thương mại [@vohtr2018a]. Đề tài tuân theo các quy định sau:

- Không đưa dữ liệu gốc vào kho mã. Kho mã chỉ lưu danh sách tệp của từng tập và mã băm của tệp tải về.
- Ứng dụng và mô hình, nếu công bố, phải ghi rõ mục đích phi thương mại.
- Muốn dùng cho mục đích khác thì liên hệ nhóm tác giả trước.

## 3. Tiền xử lý

Một hàm tiền xử lý dùng chung cho cả huấn luyện và ứng dụng. Trên điện thoại, hàm này chạy sau lớp ghép đoạn, nên đầu vào luôn là một dòng liền hoặc một dòng ảo. Bản Python và bản Kotlin phải cho cùng kết quả trên một bộ mẫu kiểm tra chung.

### 3.1. Chuẩn hóa nhãn

Nhãn của VNOnDB, kho văn bản của n-gram, nhãn của tập tự thu và chuỗi đọc ra khi chấm điểm đều qua cùng một bước chuẩn hóa. Nếu không, tỷ lệ lỗi sẽ bị đội lên và n-gram sẽ đếm một âm tiết thành hai.

1. Đưa chuỗi về dạng chuẩn NFC.
2. Thống nhất vị trí dấu thanh theo kiểu cũ, ví dụ "hòa" và "thủy".
3. Thay nhiều khoảng trắng liền nhau bằng một khoảng trắng và bỏ khoảng trắng ở hai đầu.

Bước này không đổi chữ hoa, chữ thường và dấu câu.

### 3.2. Chuẩn hóa nét

Tiền xử lý tịnh tiến và co giãn cả dòng theo cùng một tỷ lệ cho hai trục, để chiều cao khung bao của dòng nằm trong khoảng từ 0 đến 1. Cách làm này khác Carbune và cộng sự, vì nhóm đó chuẩn hóa theo vùng viết chứ không theo khung bao của nét [@carbune2019]. VNOnDB không có thông tin về vùng viết nên đề tài dùng khung bao. Khung bao phụ thuộc vào chữ có phần trên hay phần dưới dài, nên cần đo ảnh hưởng này ở thí nghiệm.

### 3.3. Lấy mẫu lại và đặc trưng

Tiền xử lý đặt các điểm cách đều dọc theo từng nét, giữ nguyên thứ tự viết. Khoảng cách dự kiến là 0,05 đơn vị chiều cao, theo giá trị của Carbune và cộng sự [@carbune2019]. Vì cách chuẩn hóa khác nhau, giá trị này cần được chọn lại trên tập kiểm định. Mỗi điểm sau đó được mô tả bằng độ dời so với điểm liền trước:

$$
\Delta x_i = x_i - x_{i-1}, \quad \Delta y_i = y_i - y_{i-1} \tag{1}
$$

trong đó $(x_i, y_i)$ là tọa độ của điểm thứ $i$ sau chuẩn hóa và lấy mẫu lại. Điểm đầu tiên của dòng có độ dời bằng 0. Điểm mở đầu một nét tính độ dời từ điểm cuối của nét trước, và có cờ $s_i = 1$. Chuỗi đặc trưng $\mathbf{X}$ gồm các véc-tơ $(\Delta x_i, \Delta y_i, s_i)$.

### 3.4. Tăng cường dữ liệu

Tăng cường chỉ áp dụng cho tập huấn luyện, gồm các phép sau:

- Co giãn và nghiêng cả dòng.
- Làm nhiễu tọa độ của nét.
- Ghép các từ của tập huấn luyện thành dòng giả.
- Cho dòng của tập huấn luyện đi qua bộ mô phỏng ở mục 4, để mô hình quen với chỗ nối giữa các đoạn.

Mức của từng phép sẽ được chốt trong `05-ke-hoach-thi-nghiem.md` (chưa viết).

## 4. Dòng ngắt mô phỏng

Bộ mô phỏng sinh dòng ngắt từ dòng liền của VNOnDB, và chạy qua đúng các bước mà ứng dụng dùng. Nhờ vậy, lỗi gán nét vào hàng cũng được tính vào kết quả. Các bước như sau:

1. Chọn từ 1 đến 2 ranh giới từ làm chỗ ngắt (dự kiến).
2. Tách các nét của dòng thành các đoạn tại chỗ ngắt.
3. Đặt mỗi đoạn lên một hàng của khung kẻ ảo.
4. Thêm lệch cỡ chữ và lệch đường chân chữ riêng cho từng đoạn.
5. Chạy bước gán nét vào hàng và lớp ghép đoạn để tạo dòng ảo.

Bước 4 là bắt buộc. Nếu chỉ dịch các đoạn rồi ghép lại, lớp ghép đoạn sẽ trả về đúng dữ liệu gốc và kết quả sẽ đẹp giả tạo.

Kịch bản Dấu thêm muộn cần một bước khác: chuyển các nét dấu thanh và dấu phụ xuống cuối chuỗi. Bước này cần quy tắc nhận ra các nét đó, vì dữ liệu không có nhãn từng nét. Mục 7 ghi lại vấn đề này.

## 5. Chống rò rỉ dữ liệu

Các tập dùng chung người viết hoặc văn bản sẽ làm kết quả cao hơn thực tế. Đề tài áp dụng các biện pháp sau:

- **Người viết:** kiểm tra bằng `Writer_ID` rằng không người viết nào có mặt ở hai tập. Nếu có trùng thì ghi vào báo cáo và giữ nguyên bản chia để so sánh được với các công bố.
- **Câu trùng:** cả 200 người đều chép từ VieTreeBank, nên phải đo tỷ lệ câu trùng giữa tập huấn luyện và tập kiểm thử, rồi ghi vào báo cáo.
- **Dữ liệu cấp từ:** dữ liệu cấp từ được tách ra từ chính các dòng. Huấn luyện trước và ghép dòng giả chỉ dùng từ thuộc tập huấn luyện.
- **N-gram:** n-gram học từ văn bản của tập huấn luyện và Wikipedia tiếng Việt [@wikimedia2026a], là kho văn bản ngoài VieTreeBank. Phải loại khỏi kho các câu trùng với tập kiểm thử và các câu dùng làm đề của tập tự thu.
- **Chỉnh tham số:** ngưỡng của lớp ghép đoạn và trọng số n-gram chỉ được chỉnh trên dữ liệu sinh từ tập kiểm định.
- **Tập kiểm thử:** chỉ chạy một lần ở cuối, theo `02-yeu-cau-va-danh-gia.md`, mục 5.

## 6. Tập tự thu

Tập tự thu là thước đo cuối cho việc viết bằng ngón tay trên điện thoại. Tập này chỉ dùng để kiểm thử, không dùng để huấn luyện hay chỉnh tham số. Quy mô dự kiến là 20 người viết không có trong VNOnDB, mỗi người viết 10 dòng liền và 10 dòng ngắt.

Quy trình thu gồm các bước sau:

1. Người tham gia đọc và ký phiếu đồng ý. Phiếu phải nói rõ dữ liệu sẽ được công bố, vì tập tự thu là một sản phẩm đầu ra của đề tài.
2. Hệ thống gán cho người tham gia một mã ẩn danh và không lưu tên.
3. Người tham gia thuộc một trong hai nhóm. Hai nhóm đổi chéo nội dung của dòng liền và dòng ngắt, để so sánh công bằng.
4. Người tham gia cầm dọc điện thoại và viết bằng ngón tay trong ứng dụng thu. Dòng liền viết trên khung cuộn ngang, dòng ngắt viết trên khung có hàng kẻ.
5. Ứng dụng lưu tọa độ, thứ tự nét, thời điểm của từng điểm, kích thước màn hình và mã thiết bị.
6. Người thu kiểm tra nhãn theo câu đề, ghi lại các chỗ người viết chép sai đề, rồi chuẩn hóa nhãn theo mục 3.1.

Câu đề lấy từ các bài Wikipedia tiếng Việt được tách riêng, và các bài này bị loại khỏi kho văn bản của n-gram. Văn bản Wikipedia được cấp theo giấy phép Creative Commons Attribution-Share-Alike 4.0 [@wikimedia2026b], nên khi công bố tập tự thu phải ghi nguồn của câu đề và giữ giấy phép tương ứng. Cả hai điều kiện viết đều cầm dọc, để hướng cầm máy không ảnh hưởng đến so sánh.

Tệp tự thu lưu cùng định dạng InkML với VNOnDB để dùng chung mã đọc. Thời điểm của từng điểm chỉ dùng để phân tích, không đưa vào mô hình.

## 7. Vấn đề chưa chốt

Bảng 4 ghi các điểm chưa kiểm chứng được hoặc còn cần quyết định, cùng cách chốt từng điểm.

Bảng 4: Các vấn đề chưa chốt về dữ liệu

| Vấn đề | Ảnh hưởng | Cách chốt |
| --- | --- | --- |
| Tệp cấp dòng có `traceGroup` theo từ hay không | Bộ mô phỏng cần biết nét nào thuộc từ nào | Đọc tệp thật khi tải về |
| Tên tệp chia tập và dung lượng tệp nén, trang TC-11 chưa truy cập được | Bảng 1 và bước tải dữ liệu | Đối chiếu khi tải về |
| Số ký tự cấp dòng hơn cấp từ 126.332, còn số khoảng trắng dự kiến là 103.450 | Giá trị $N$ khi tính tỷ lệ lỗi | Đếm lại trên dữ liệu thật |
| Người viết có tách biệt giữa các tập hay không | Mức tin cậy của so sánh | Kiểm tra theo mục 5 |
| Quy tắc nhận nét dấu thanh và dấu phụ | Kịch bản Dấu thêm muộn | Thử quy tắc theo kích thước nét và vị trí, kiểm tra bằng tay trên một mẫu nhỏ |
| Số chỗ ngắt khi mô phỏng | Một dòng khoảng 15 từ có thể cần nhiều hàng hơn 3 khi cầm dọc | Cho từ 2 đến 3 người viết thử trên điện thoại, đếm số từ mỗi hàng |
