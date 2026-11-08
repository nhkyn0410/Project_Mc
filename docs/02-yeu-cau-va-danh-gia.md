# Yêu cầu và đánh giá

Trạng thái: Nháp

Tài liệu này quy định các ngưỡng đề tài phải đạt, cách tính từng chỉ số, các kịch bản kiểm thử và các mốc so sánh. Tài liệu dành cho người chạy thí nghiệm và người viết Chương 1, Chương 4 của báo cáo. Mọi ngưỡng trong tài liệu là giá trị dự kiến, có thể chỉnh sau khi có kết quả của mô hình cơ sở.

## 1. Mục tiêu và ngưỡng

Đề tài đạt yêu cầu khi đạt các ngưỡng trong Bảng 1. Chỉ số chính là tỷ lệ lỗi ký tự (CER) và tỷ lệ lỗi từ (WER), định nghĩa ở mục 2. Ngưỡng được kiểm tra trên bản chạy trên điện thoại, tức mô hình M2 sau lượng tử hóa kèm bộ giải mã Kotlin. Bản chưa lượng tử hóa cũng được đo để biết mức giảm do lượng tử hóa.

Bảng 1: Mục tiêu và ngưỡng dự kiến

| Mục tiêu | Chỉ số | Ngưỡng dự kiến |
| --- | --- | --- |
| Nhận dạng dòng liền | CER trên tập kiểm thử VNOnDB cấp dòng | ≤ 6,86% |
| Nhận dạng dòng liền | WER trên tập kiểm thử VNOnDB cấp dòng | ≤ 19% |
| Nhận dạng dòng liền, mục tiêu cao hơn | CER trên tập kiểm thử VNOnDB cấp dòng | Tiến gần 3,24% |
| Xử lý dòng ngắt | CER tăng thêm so với cùng dòng viết liền | ≤ 2 điểm phần trăm |
| Chạy trên điện thoại | Tổng dung lượng mô hình và n-gram | ≤ 20 MB |
| Phản hồi nhanh | Thời gian nhận dạng một dòng trên điện thoại thật | ≤ 1 giây |
| Viết bằng ngón tay | CER trên tập tự thu | Đo và báo cáo |

Ngưỡng CER và WER bằng mốc GoogleTask2 trong Bảng 3. Hệ thống này xử lý dữ liệu dạng nét, không huấn luyện trên VNOnDB [@carbune2019] và không dùng VieTreeBank [@le2019], nên là mốc công bằng nhất. Mục tiêu cao hơn lấy theo IVTOVTask2 và không bắt buộc. Đề tài xem lại các ngưỡng này sau khi có kết quả của mô hình cơ sở M0. Ngưỡng 20 MB ngang kích thước mô hình ML Kit cho mỗi ngôn ngữ [@google2026a].

## 2. Chỉ số

### 2.1. Tỷ lệ lỗi ký tự

Tỷ lệ lỗi dựa trên khoảng cách sửa Levenshtein giữa chuỗi đúng và chuỗi mô hình đọc ra. Đề tài tính theo hai cách, vì các nguồn dùng cách tính khác nhau. Cách thứ nhất lấy tổng lỗi chia cho tổng độ dài:

$$
\mathrm{CER}_{\text{tổng}} = \frac{\sum_{q=1}^{Q} E_q}{\sum_{q=1}^{Q} N_q} \tag{1}
$$

trong đó $Q$ là số dòng, $E_q$ là khoảng cách sửa của dòng thứ $q$, bằng tổng số ký tự bị thay, chèn và xóa $S + I + D$ của dòng đó, và $N_q$ là số ký tự của chuỗi đúng ở dòng thứ $q$. Cách thứ hai tính tỷ lệ của từng dòng rồi lấy trung bình, là cách Le và cộng sự dùng [@le2019]:

$$
\mathrm{CER}_{\text{dòng}} = \frac{1}{Q} \sum_{q=1}^{Q} \frac{E_q}{N_q} \tag{2}
$$

Hai cách cho kết quả khác nhau khi độ dài dòng khác nhau. Giả sử có hai dòng: dòng thứ nhất có $N_1 = 10$ và $E_1 = 1$, dòng thứ hai có $N_2 = 100$ và $E_2 = 5$. Công thức (1) cho 6/110, khoảng 5,45%, còn công thức (2) cho trung bình của 10% và 5%, tức 7,5%.

Đề tài dùng công thức (2) để so với ngưỡng trong Bảng 1 và các mốc trong Bảng 3, và báo cáo thêm công thức (1). Chuỗi đúng và chuỗi đọc ra đều được chuẩn hóa trước theo `03-du-lieu.md`, mục 3.1. Khoảng trắng được tính là một ký tự.

### 2.2. Tỷ lệ lỗi từ

WER tính theo công thức (1) và công thức (2), với đơn vị là từ thay cho ký tự. Từ được tách theo khoảng trắng, nên trong tiếng Việt, WER thực chất là tỷ lệ lỗi âm tiết. Báo cáo phải ghi rõ điều này khi so sánh với các hệ thống của ngôn ngữ khác.

### 2.3. Tỷ lệ lỗi bỏ dấu

Đề tài đo lại CER sau khi biến đổi cả hai chuỗi theo hai mức:

- **CER bỏ dấu thanh:** bỏ sắc, huyền, hỏi, ngã, nặng và giữ ă, â, ê, ô, ơ, ư, đ.
- **CER bỏ dấu thanh và dấu phụ:** đưa toàn bộ chữ về 26 chữ cái Latinh cơ bản.

Phần chênh giữa CER thường và CER của từng mức cho biết tỷ lệ lỗi do dấu thanh, và do dấu thanh cùng dấu phụ.

### 2.4. Mức tăng khi dòng bị ngắt

Mức tăng là hiệu giữa CER của dòng ngắt và CER của chính các dòng đó khi viết liền, tính bằng điểm phần trăm. Hai phép đo dùng cùng một mô hình và cùng một danh sách dòng. Báo cáo ghi mức tăng theo từng số lượng chỗ nối.

### 2.5. Dung lượng và độ trễ

- **Dung lượng:** tổng kích thước các tệp mô hình `.tflite`, bộ ký tự và n-gram mà ứng dụng cần khi chạy.
- **Độ trễ:** thời gian từ lúc nhấc bút lần cuối đến khi kết quả hiện ra, gồm ghép đoạn, tiền xử lý, mô hình và beam search.
- **Cách báo cáo:** đo trên điện thoại Android thật, ghi tên máy, báo cáo trung vị, phân vị 95 và thời gian của dòng dài nhất.

### 2.6. Độ bất định trên tập tự thu

Tập tự thu chỉ có 20 người viết (dự kiến), nên kết quả cần kèm khoảng tin cậy. Đề tài dùng bootstrap 95% với đơn vị lấy mẫu lại là người viết. Khi so sánh dòng liền với dòng ngắt, hoặc so với ML Kit, phép so sánh ghép cặp trên cùng một người viết.

## 3. Kịch bản kiểm thử

Bảng 2 ghi bốn kịch bản kiểm thử. Dữ liệu của từng kịch bản được tạo theo `03-du-lieu.md`, mục 4 và mục 6.

Bảng 2: Kịch bản kiểm thử

| Kịch bản | Dữ liệu | Câu hỏi cần trả lời |
| --- | --- | --- |
| Dòng liền | 1.634 dòng kiểm thử của VNOnDB | Mô hình đứng ở đâu so với các mốc công bố? |
| Ngắt mô phỏng | Cùng 1.634 dòng, cắt 1-2 lần tại ranh giới từ | Lớp ghép đoạn làm CER tăng bao nhiêu? |
| Dấu thêm muộn | Cùng 1.634 dòng, chuyển nét dấu thanh và dấu phụ xuống cuối chuỗi | Mô hình có giữ được dấu thanh và dấu phụ khi nét trễ đến rất muộn? |
| Viết tay thật | Tập tự thu, mỗi người 10 dòng liền và 10 dòng ngắt | Kết quả có giữ được khi viết bằng ngón tay? |

## 4. Mốc so sánh

Bảng 3 ghi các mốc so sánh, tất cả đều đo trên tập kiểm thử 1.634 dòng của VNOnDB. Các nguồn đã đọc không nêu cách tính trung bình của cuộc thi, nên số liệu chỉ mang tính tham khảo.

Bảng 3: Mốc so sánh trên tập kiểm thử VNOnDB

| Hệ thống | Dạng dữ liệu | CER (%) | WER (%) | Ghi chú |
| --- | --- | --- | --- | --- |
| MyScriptTask2_1 [@le2019] | Nét | 1,02 | 2,02 | Mô hình ngôn ngữ dùng VieTreeBank |
| IVTOVTask2 [@le2019] | Nét | 3,24 | 14,11 | 2 lớp BiLSTM 100 ô, ràng buộc từ điển lấy từ VieTreeBank |
| HTR-ConvText [@pham2025] | Ảnh | 3,45 | 8,9 | 65,9 triệu tham số |
| GoogleTask2 [@le2019] | Nét | 6,86 | 19,00 | Không huấn luyện trên VNOnDB [@carbune2019] |
| GFCN [@pham2025] | Ảnh | 8,4 | 24,2 | 1,4 triệu tham số |
| CNN + BiLSTM [@pham2025] | Ảnh | 10,53 | 29,1 | 8,3 triệu tham số |

Trong Bảng 3, mốc CNN + BiLSTM là mô hình gồm mạng nơ-ron tích chập (CNN) và LSTM hai chiều (BiLSTM). MyScript và IVTOV khó làm mục tiêu vì cả hai đều dùng VieTreeBank, cùng nguồn với văn bản kiểm thử [@le2019]. Cuộc thi còn có một tập kiểm thử riêng gồm 15 người viết mới [@vohtr2018b]. Trên tập này, CER của IVTOV tăng từ 3,2% lên 5,6%, và CER của Google tăng từ 6,9% lên 10,3% [@carbune2019]. Vì vậy, tập tự thu phải dùng người viết mới.

ML Kit có mô hình tiếng Việt với mã `vi` [@google2026b], nên đề tài chạy cùng tập tự thu trên ML Kit để có mốc thực tế nhất.

## 5. Quy tắc đo

- **Chọn mô hình:** mô hình tốt nhất được chọn theo CER trên tập kiểm định.
- **Tập kiểm thử:** kịch bản trên tập kiểm thử chỉ chạy một lần ở cuối, sau khi đã chốt mô hình và mọi tham số.
- **Kiểm tra bộ giải mã:** bộ giải mã Kotlin phải cho cùng kết quả với bản Python tham chiếu trên một bộ mẫu chung.
- **Ghi nhận:** mọi lần chạy ghi vào `07-nhat-ky-thi-nghiem.md` (chưa viết), số liệu trong báo cáo phải chỉ ra được lần chạy tạo ra nó.

## 6. Vấn đề chưa chốt

Bảng 4 ghi các điểm cần quyết định trước khi chạy thí nghiệm chính thức.

Bảng 4: Các vấn đề chưa chốt về đánh giá

| Vấn đề | Ảnh hưởng | Hướng đề xuất |
| --- | --- | --- |
| Ngưỡng 2 điểm phần trăm chưa gắn với số chỗ nối | Kết quả phụ thuộc vào số lần cắt | Ghi ngưỡng theo số chỗ nối sau khi đo số hàng thực tế |
| Thiếu mốc nhận dạng từng hàng rồi nối chuỗi | Chưa chứng minh được dòng ảo tốt hơn cách đơn giản | Thêm mốc này vào kịch bản Ngắt mô phỏng và Viết tay thật |
| Cách đưa dòng ngắt vào ML Kit | So sánh có thể thiếu công bằng | Đưa từng hàng kèm ngữ cảnh chữ đã nhận dạng |
| Điện thoại dùng để đo | Độ trễ phụ thuộc vào máy | Chọn một máy tầm trung và ghi cấu hình |
| Cách tính trung bình của cuộc thi | So sánh với Bảng 3 có thể lệch | Đọc bài tổng kết cuộc thi [@le2018] |
