<!-- Phần đầu báo cáo: mục lục, danh mục. Bảng ký hiệu và chữ viết tắt lấy từ docs/ky-hieu-va-viet-tat.md. -->
@@tieu-de-khong-muc-luc MỤC LỤC
@@muc-luc

# DANH MỤC KÝ HIỆU VÀ CHỮ VIẾT TẮT

Ký hiệu toán dùng trong báo cáo được liệt kê theo thứ tự xuất hiện trong luồng xử lý. Mỗi ký hiệu chỉ mang một nghĩa trong toàn bộ báo cáo.

| Ký hiệu | Nghĩa |
| --- | --- |
| $\mathbf{e}_1$, $\mathbf{e}_2$ | Hai đầu của một đoạn thẳng trên nét, khi vẽ dòng thành ảnh |
| $\mathbf{g}$ | Tâm của một ô trên lưới mịn khi vẽ dòng thành ảnh |
| $\eta$ | Vị trí trên đoạn thẳng gần tâm ô nhất, trong khoảng từ 0 đến 1 |
| $\rho$ | Số ô của lưới mịn trên một cạnh điểm ảnh |
| $\omega$ | Độ dày nét trên khung cuối khi vẽ dòng thành ảnh, tính bằng điểm ảnh |
| $\lambda$ | Hệ số co của nét khi đặt dòng vào khung ảnh |
| $\delta$ | Lề ngang của khung ảnh, tính bằng điểm ảnh |
| $\Delta_R$, $\Delta_H$ | Chiều rộng và chiều cao phần nét trước khi co |
| $H$, $R$ | Chiều cao và chiều rộng của khung ảnh đầu vào |
| $H_{\text{nét}}$ | Chiều cao tối đa của phần nét sau khi co, bằng $H$ khi không giới hạn |
| $\mathbf{X}$ | Ảnh xám của một dòng sau tiền xử lý, là đầu vào của mô hình |
| $s_x$, $s_y$ | Hệ số co giãn ngang và dọc khi tăng cường dữ liệu |
| $\psi$ | Hệ số nghiêng khi tăng cường dữ liệu |
| $o_y$ | Độ dịch dọc khi tăng cường dữ liệu, tính bằng điểm ảnh |
| $u_0$, $v_0$ | Hàng và cột trên ảnh cũ ứng với điểm ảnh ở hàng $u$, cột $v$ của ảnh sau tăng cường |
| $x_{u,v}$, $y_{u,v}$ | Giá trị tại hàng $u$, cột $v$ của đầu vào và đầu ra một bộ lọc tích chập |
| $\kappa_{u',v'}$ | Trọng số của bộ lọc tích chập tại vị trí tương đối $(u', v')$ |
| $F_{\text{vào}}$, $F$ | Số kênh đầu vào và số bộ lọc của một lớp tích chập |
| $e_\ell$ | Kích thước cửa sổ của lớp thứ $\ell$ theo một chiều |
| $\tau_\ell$ | Bước nhảy của lớp thứ $\ell$ theo một chiều |
| $v_\ell$, $g_\ell$ | Vùng nhìn và bước nhảy tích lũy sau lớp thứ $\ell$ theo một chiều |
| $T$ | Số bước thời gian sau khi CNN 2D giảm chiều rộng ảnh |
| $\mathbf{z}_t$ | Véc-tơ đầu vào của lớp hồi quy tại bước $t$, là đầu ra của lớp kết nối đầy đủ sau CNN 2D hoặc của lớp BiLSTM bên dưới |
| $d_{\text{vào}}$, $d$ | Số chiều của $\mathbf{z}_t$ và số ô của một chiều LSTM |
| $\mathbf{h}_t$ | Trạng thái ẩn tại bước $t$. Với LSTM một chiều là đầu ra của chiều đó, với BiLSTM là phần ghép từ hai chiều |
| $\overrightarrow{\mathbf{h}}_t$, $\overleftarrow{\mathbf{h}}_t$ | Trạng thái ẩn của chiều xuôi và chiều ngược trong BiLSTM |
| $\mathbf{C}_t$, $\tilde{\mathbf{C}}_t$ | Ô nhớ của LSTM tại bước $t$, và giá trị ứng viên để ghi vào ô nhớ |
| $\mathbf{f}_t$, $\mathbf{i}_t$, $\mathbf{o}_t$ | Cổng quên, cổng ghi và cổng ra của LSTM tại bước $t$ |
| $\mathbf{V}_{\ast}$, $\mathbf{b}_{\ast}$ | Ma trận trọng số và véc-tơ độ lệch của một cổng, chỉ số dưới cho biết cổng nào |
| $\sigma$ | Hàm sigmoid, cho giá trị trong khoảng từ 0 đến 1 |
| $\odot$ | Phép nhân từng phần tử của hai véc-tơ |
| $\mathcal{A}$ | Bảng ký tự của mô hình, gồm 160 ký tự có ở tập huấn luyện hoặc tập kiểm định của VNOnDB |
| $\epsilon$ | Nhãn trống của CTC |
| $\mathcal{A}'$ | Tập nhãn đầu ra $\mathcal{A} \cup \{\epsilon\}$, gồm 161 nhãn |
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
| $Q$, $q$ | Số dòng trong một tập khi tính tỷ lệ lỗi, và chỉ số của một dòng |
| $E_q$, $N_q$ | Khoảng cách sửa của dòng thứ $q$, và độ dài chuỗi đúng của dòng đó |
| $\theta$, $\tilde{\theta}$ | Một trọng số của mô hình, và giá trị khôi phục sau lượng tử hóa |
| $\nu$ | Số nguyên lưu trọng số sau lượng tử hóa |
| $\gamma$, $\zeta$ | Bước lượng tử và điểm không của phép lượng tử hóa |

{bang co=12 w=28,72}

Chữ viết tắt được liệt kê theo thứ tự chữ cái.

| Viết tắt | Viết đầy đủ | Nghĩa |
| --- | --- | --- |
| BiLSTM | Bidirectional Long Short-Term Memory | LSTM hai chiều |
| CER | Character Error Rate | Tỷ lệ lỗi ký tự |
| CER (1), CER (2) | | Tỷ lệ lỗi ký tự tính theo công thức tổng và công thức trung bình theo dòng, xem mục 1.5.1 |
| CNN | Convolutional Neural Network | Mạng nơ-ron tích chập |
| CPU | Central Processing Unit | Bộ xử lý trung tâm |
| CTC | Connectionist Temporal Classification | Hàm mất mát cho bài toán chuỗi không có nhãn căn chỉnh |
| GRU | Gated Recurrent Unit | Mạng hồi quy có cổng, gọn hơn LSTM |
| ICFHR | International Conference on Frontiers in Handwriting Recognition | Hội nghị quốc tế về nhận dạng chữ viết tay |
| InkML | Ink Markup Language | Định dạng lưu chữ viết tay dạng nét |
| LSTM | Long Short-Term Memory | Mạng hồi quy có bộ nhớ dài ngắn hạn |
| M0, M1, M2 | | Ba mô hình của đề tài, xem mục 3.2.4 |
| NFC | Normalization Form C | Dạng chuẩn Unicode dùng ký tự dựng sẵn |
| SDK | Software Development Kit | Bộ công cụ phát triển phần mềm |
| VNOnDB | HANDS-VNOnDB | Bộ dữ liệu chữ viết tay tiếng Việt dạng nét |
| VOHTR | Vietnamese Online Handwritten Text Recognition | Cuộc thi nhận dạng chữ viết tay tiếng Việt dạng nét tại ICFHR 2018 |
| WER | Word Error Rate | Tỷ lệ lỗi từ, trong đề tài tính theo âm tiết |
| WER (1), WER (2) | | Tỷ lệ lỗi từ tính theo công thức tổng và công thức trung bình theo dòng, xem mục 1.5.1 |

{bang co=12 w=20,38,42}

# DANH MỤC BẢNG
@@danh-muc-bang

# DANH MỤC HÌNH ẢNH
@@danh-muc-hinh
