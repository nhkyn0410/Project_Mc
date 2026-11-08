# Ký hiệu và chữ viết tắt

Trạng thái: Nháp

Tài liệu này là nơi duy nhất định nghĩa ký hiệu toán và chữ viết tắt dùng trong các tài liệu của đề tài. Khi viết báo cáo, Bảng 1 và Bảng 2 trở thành danh mục ký hiệu và danh mục chữ viết tắt. Cần ký hiệu hay chữ viết tắt mới thì thêm vào đây trước rồi mới dùng.

## 1. Ký hiệu toán

Bảng 1 liệt kê các ký hiệu dùng chung, xếp theo thứ tự xuất hiện trong luồng xử lý. Mỗi ký hiệu chỉ mang một nghĩa trong toàn bộ tài liệu.

Bảng 1: Ký hiệu toán dùng chung

| Ký hiệu | Nghĩa |
| --- | --- |
| $(x_i, y_i)$ | Tọa độ của điểm thứ $i$ sau chuẩn hóa và lấy mẫu lại |
| $M$ | Số điểm của một dòng sau lấy mẫu lại |
| $\Delta x_i$, $\Delta y_i$ | Độ dời của điểm thứ $i$ so với điểm liền trước |
| $s_i$ | Cờ bắt đầu nét, bằng 1 nếu điểm thứ $i$ mở đầu một nét và bằng 0 nếu không |
| $\mathbf{X}$ | Chuỗi đặc trưng đầu vào của mô hình, gồm $M$ véc-tơ $(\Delta x_i, \Delta y_i, s_i)$ |
| $T$ | Số bước thời gian sau khi CNN 1D giảm độ dài chuỗi |
| $\mathbf{z}_t$ | Véc-tơ đầu vào của lớp hồi quy tại bước $t$, là đầu ra của CNN 1D hoặc của lớp BiLSTM bên dưới |
| $d_{\text{vào}}$, $d$ | Số chiều của $\mathbf{z}_t$ và số ô của một chiều LSTM |
| $\mathbf{h}_t$ | Trạng thái ẩn tại bước $t$. Với LSTM một chiều là đầu ra của chiều đó, với BiLSTM là phần ghép từ hai chiều |
| $\overrightarrow{\mathbf{h}}_t$, $\overleftarrow{\mathbf{h}}_t$ | Trạng thái ẩn của chiều xuôi và chiều ngược trong BiLSTM |
| $\mathbf{C}_t$, $\tilde{\mathbf{C}}_t$ | Ô nhớ của LSTM tại bước $t$, và giá trị ứng viên để ghi vào ô nhớ |
| $\mathbf{f}_t$, $\mathbf{i}_t$, $\mathbf{o}_t$ | Cổng quên, cổng ghi và cổng ra của LSTM tại bước $t$ |
| $\mathbf{V}_{\ast}$, $\mathbf{b}_{\ast}$ | Ma trận trọng số và véc-tơ độ lệch của một cổng, chỉ số dưới cho biết cổng nào |
| $\sigma$ | Hàm sigmoid, cho giá trị trong khoảng từ 0 đến 1 |
| $\odot$ | Phép nhân từng phần tử của hai véc-tơ |
| $\mathcal{A}$ | Bảng ký tự của VNOnDB, gồm 161 ký tự |
| $\epsilon$ | Nhãn trống của CTC |
| $\mathcal{A}'$ | Tập nhãn đầu ra $\mathcal{A} \cup \{\epsilon\}$, gồm 162 nhãn |
| $p_t(k)$ | Xác suất mô hình gán cho nhãn $k \in \mathcal{A}'$ tại bước $t$ |
| $\mathbf{l} = (l_1, \ldots, l_U)$ | Chuỗi ký tự đích của một dòng, dài $U$ ký tự |
| $r$ | Số cặp ký tự giống nhau đứng liền nhau trong $\mathbf{l}$ |
| $\boldsymbol{\pi}$ | Đường căn chỉnh gồm $T$ nhãn thuộc $\mathcal{A}'$ |
| $\mathcal{B}$ | Phép gộp của CTC: bỏ các nhãn lặp liền nhau, rồi bỏ nhãn trống |
| $\mathbf{l}'$ | Chuỗi nhãn mở rộng: $\mathbf{l}$ có thêm nhãn trống ở đầu, cuối và giữa mọi cặp ký tự, dài $2U + 1$ |
| $\phi_t(j)$ | Biến tiến của CTC: tổng xác suất các đường căn chỉnh dừng ở vị trí $j$ của $\mathbf{l}'$ sau $t$ bước |
| $\mathcal{L}_{\text{CTC}}$ | Hàm mất mát CTC của một dòng |
| $\hat{\mathbf{l}}$ | Chuỗi ký tự mô hình đọc ra khi giải mã |
| $\mathbf{w}(\mathbf{l})$ | Dãy âm tiết của chuỗi $\mathbf{l}$, tách theo khoảng trắng |
| $w_i$, $m$ | Âm tiết thứ $i$ của một dãy âm tiết, và số âm tiết của dãy đó |
| $P_{\text{LM}}$ | Xác suất do mô hình ngôn ngữ n-gram âm tiết gán cho một dãy âm tiết |
| $n$ | Bậc của mô hình n-gram: số âm tiết trong một cụm, tính cả âm tiết đang xét |
| $C(\cdot)$ | Số lần một cụm âm tiết xuất hiện trong kho văn bản huấn luyện |
| $W$ | Độ rộng beam: số tiền tố được giữ lại sau mỗi bước giải mã |
| $\mathbf{c}$ | Một tiền tố đang xét trong beam search, là chuỗi ký tự đã gộp |
| $c_{\text{cuối}}$ | Ký tự cuối cùng của tiền tố $\mathbf{c}$ |
| $p_b(\mathbf{c}, t)$, $p_{nb}(\mathbf{c}, t)$ | Xác suất các đường dài $t$ gộp thành $\mathbf{c}$, kết thúc bằng nhãn trống và không bằng nhãn trống |
| $\alpha$, $\beta$ | Trọng số của mô hình ngôn ngữ và điểm thưởng theo số âm tiết khi giải mã |
| $S$, $I$, $D$, $N$ | Số ký tự bị thay, chèn, xóa, và số ký tự của chuỗi đúng |

## 2. Chữ viết tắt

Bảng 2 liệt kê các chữ viết tắt, xếp theo thứ tự chữ cái.

Bảng 2: Chữ viết tắt

| Viết tắt | Viết đầy đủ | Nghĩa |
| --- | --- | --- |
| BiLSTM | Bidirectional Long Short-Term Memory | LSTM hai chiều |
| CER | Character Error Rate | Tỷ lệ lỗi ký tự |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CTC | Connectionist Temporal Classification | Hàm mất mát cho bài toán chuỗi không có nhãn căn chỉnh |
| GRU | Gated Recurrent Unit | Mạng hồi quy có cổng, gọn hơn LSTM |
| ICFHR | International Conference on Frontiers in Handwriting Recognition | Hội nghị quốc tế về nhận dạng chữ viết tay |
| LSTM | Long Short-Term Memory | Mạng hồi quy có bộ nhớ dài ngắn hạn |
| NFC | Normalization Form C | Dạng chuẩn Unicode dùng ký tự dựng sẵn |
| VNOnDB | HANDS-VNOnDB | Bộ dữ liệu chữ viết tay tiếng Việt dạng nét |
| VOHTR | Vietnamese Online Handwritten Text Recognition | Cuộc thi nhận dạng chữ viết tay tiếng Việt dạng nét tại ICFHR 2018 |
| WER | Word Error Rate | Tỷ lệ lỗi từ, trong đề tài tính theo âm tiết |
