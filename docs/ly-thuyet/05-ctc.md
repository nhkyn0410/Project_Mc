# Hàm mất mát CTC

Trạng thái: Nháp

Tài liệu này trình bày hàm mất mát Connectionist Temporal Classification (CTC), cách đề tài huấn luyện mô hình khi không có nhãn căn chỉnh giữa nét và ký tự. CTC nằm ở cuối mô hình, ngay sau lớp BiLSTM (Bidirectional Long Short-Term Memory), và quyết định cả cách giải mã đầu ra. Tài liệu dành cho người viết phần thiết kế mô hình và phần cơ sở lý thuyết của báo cáo.

## 1. Bài toán

Đầu vào của mô hình là chuỗi đặc trưng $\mathbf{X}$ của một dòng. Sau khi mạng nơ-ron tích chập một chiều (CNN 1D) giảm độ dài chuỗi, lớp BiLSTM cho ra $T$ bước thời gian. Đầu ra cần có là chuỗi ký tự $\mathbf{l} = (l_1, \ldots, l_U)$ của dòng đó.

Bộ dữ liệu HANDS-VNOnDB (VNOnDB) chỉ cho biết văn bản của cả dòng. Dữ liệu không ghi bước thời gian nào ứng với ký tự nào, nên không thể huấn luyện bằng cách phân loại từng bước. Độ dài cũng khác nhau: $T$ thường lớn hơn $U$ nhiều lần, và một ký tự kéo dài qua nhiều bước.

CTC giải bài toán này bằng cách tính xác suất của chuỗi đích $\mathbf{l}$ khi cộng dồn trên mọi cách căn chỉnh có thể [@graves2006]. Hàm mất mát chỉ cần cặp dữ liệu gồm chuỗi đặc trưng và văn bản, không cần biết vị trí của từng ký tự.

## 2. Nguyên lý

### 2.1. Xác suất của một đường căn chỉnh

Tại mỗi bước $t$, lớp softmax cho ra phân bố xác suất $p_t(k)$ trên tập nhãn $\mathcal{A}'$. Tập này gồm 161 ký tự của VNOnDB cộng thêm nhãn trống $\epsilon$, nghĩa là "không phát ra ký tự nào ở bước này".

Một đường căn chỉnh $\boldsymbol{\pi} = (\pi_1, \ldots, \pi_T)$ chọn một nhãn cho mỗi bước. CTC giả định các bước độc lập với nhau khi đã biết $\mathbf{X}$, nên xác suất của một đường là tích các xác suất từng bước:

$$
p(\boldsymbol{\pi} \mid \mathbf{X}) = \prod_{t=1}^{T} p_t(\pi_t) \tag{1}
$$

trong đó $\pi_t$ là nhãn của đường tại bước $t$.

### 2.2. Phép gộp và hàm mất mát

Phép gộp $\mathcal{B}$ biến một đường căn chỉnh thành chuỗi ký tự qua hai bước: bỏ các nhãn lặp liền nhau, rồi bỏ nhãn trống. Ví dụ, với $T = 6$, đường $(m, m, \epsilon, a, a, \epsilon)$ gộp thành chuỗi "ma".

Nhãn trống cho phép mô hình viết hai ký tự giống nhau đứng liền nhau. Đường $(o, o, \epsilon, o)$ gộp thành "oo", còn đường $(o, o, o, o)$ chỉ gộp thành "o".

Nhiều đường khác nhau gộp về cùng một chuỗi. Xác suất của chuỗi đích là tổng xác suất của tất cả các đường đó:

$$
p(\mathbf{l} \mid \mathbf{X}) = \sum_{\boldsymbol{\pi} \in \mathcal{B}^{-1}(\mathbf{l})} p(\boldsymbol{\pi} \mid \mathbf{X}) \tag{2}
$$

trong đó $\mathcal{B}^{-1}(\mathbf{l})$ là tập mọi đường dài $T$ gộp thành $\mathbf{l}$. Hàm mất mát của một dòng là log âm của xác suất này:

$$
\mathcal{L}_{\text{CTC}} = -\ln p(\mathbf{l} \mid \mathbf{X}) \tag{3}
$$

Huấn luyện là giảm $\mathcal{L}_{\text{CTC}}$ trung bình trên tập huấn luyện bằng lan truyền ngược.

### 2.3. Tính tổng bằng quy hoạch động

Số đường trong $\mathcal{B}^{-1}(\mathbf{l})$ tăng theo hàm mũ của $T$, nên không thể cộng trực tiếp theo công thức (2). CTC dùng quy hoạch động trên chuỗi nhãn mở rộng $\mathbf{l}'$, tạo bằng cách chèn nhãn trống vào đầu, cuối và giữa mọi cặp ký tự của $\mathbf{l}$. Chuỗi $\mathbf{l}'$ dài $2U + 1$, với các vị trí lẻ là nhãn trống [@graves2006].

Biến tiến $\phi_t(j)$ là tổng xác suất của các đoạn đường dài $t$ dừng ở vị trí $j$ của $\mathbf{l}'$. Ở bước đầu, đường chỉ có thể bắt đầu bằng nhãn trống hoặc ký tự đầu tiên: $\phi_1(1) = p_1(\epsilon)$, $\phi_1(2) = p_1(l_1)$, các vị trí khác bằng 0. Từ bước thứ hai trở đi:

$$
\phi_t(j) =
\begin{cases}
\big(\phi_{t-1}(j) + \phi_{t-1}(j-1)\big)\, p_t(l'_j) & \text{nếu } l'_j = \epsilon \text{ hoặc } l'_j = l'_{j-2} \\
\big(\phi_{t-1}(j) + \phi_{t-1}(j-1) + \phi_{t-1}(j-2)\big)\, p_t(l'_j) & \text{trường hợp còn lại}
\end{cases} \tag{4}
$$

trong đó $l'_j$ là nhãn ở vị trí $j$ của $\mathbf{l}'$. Trường hợp thứ nhất cấm nhảy qua một nhãn trống khi hai ký tự liền nhau giống nhau, vì nếu nhảy thì phép gộp sẽ nhập hai ký tự làm một.

Đường hợp lệ phải kết thúc ở ký tự cuối hoặc ở nhãn trống cuối cùng, nên:

$$
p(\mathbf{l} \mid \mathbf{X}) = \phi_T(2U + 1) + \phi_T(2U) \tag{5}
$$

Cách tính này tốn thời gian tỷ lệ với $T \cdot U$ thay vì tăng theo hàm mũ. Đạo hàm của $\mathcal{L}_{\text{CTC}}$ được tính bằng biến lùi theo cùng cách, đi từ bước $T$ về bước 1. Khi cài đặt, các phép tính làm trong miền logarit để tránh tràn số dưới khi nhân nhiều xác suất nhỏ.

### 2.4. Điều kiện về độ dài

Mỗi ký tự cần ít nhất một bước, và mỗi cặp ký tự giống nhau đứng liền nhau cần thêm một nhãn trống ở giữa. Vì vậy chuỗi đích chỉ có đường căn chỉnh khi:

$$
T \ge U + r \tag{6}
$$

trong đó $r$ là số cặp ký tự giống nhau đứng liền nhau trong $\mathbf{l}$. Dòng vi phạm công thức (6) có xác suất bằng 0 và mất mát vô cùng lớn.

### 2.5. Giải mã đơn giản

Do các bước độc lập theo công thức (1), đường có xác suất lớn nhất tìm được bằng cách chọn nhãn có xác suất lớn nhất ở từng bước. Cách giải mã nhanh nhất là gộp đường đó:

$$
\hat{\mathbf{l}} = \mathcal{B}\Big(\big(\arg\max_{k} p_1(k), \ldots, \arg\max_{k} p_T(k)\big)\Big) \tag{7}
$$

Cách này chỉ xét một đường, trong khi xác suất của chuỗi là tổng trên nhiều đường, nên không chắc tìm ra chuỗi có xác suất lớn nhất. Beam search kết hợp mô hình ngôn ngữ xử lý điểm yếu này, xem `06-beam-search-va-n-gram.md`.

## 3. Ví dụ minh họa

Ví dụ dùng chuỗi đích một ký tự "a", tức $U = 1$, với $T = 3$ bước. Để tính được bằng tay, giả sử mô hình chỉ gán xác suất cho hai nhãn "a" và $\epsilon$. Bảng 1 cho xác suất ở từng bước.

Bảng 1: Xác suất đầu ra giả định trong ví dụ

| Bước $t$ | $p_t(a)$ | $p_t(\epsilon)$ |
| --- | --- | --- |
| 1 | 0,6 | 0,4 |
| 2 | 0,6 | 0,4 |
| 3 | 0,3 | 0,7 |

Có 8 đường dài 3 trên hai nhãn này. Sáu đường gộp thành "a", được liệt kê trong Bảng 2 cùng xác suất tính theo công thức (1). Hai đường còn lại không gộp thành "a": đường $(a, \epsilon, a)$ gộp thành "aa", đường $(\epsilon, \epsilon, \epsilon)$ gộp thành chuỗi rỗng.

Bảng 2: Các đường căn chỉnh gộp thành "a"

| Đường | Cách tính | Xác suất |
| --- | --- | --- |
| $(a, a, a)$ | $0{,}6 \times 0{,}6 \times 0{,}3$ | 0,108 |
| $(a, a, \epsilon)$ | $0{,}6 \times 0{,}6 \times 0{,}7$ | 0,252 |
| $(a, \epsilon, \epsilon)$ | $0{,}6 \times 0{,}4 \times 0{,}7$ | 0,168 |
| $(\epsilon, a, a)$ | $0{,}4 \times 0{,}6 \times 0{,}3$ | 0,072 |
| $(\epsilon, \epsilon, a)$ | $0{,}4 \times 0{,}4 \times 0{,}3$ | 0,048 |
| $(\epsilon, a, \epsilon)$ | $0{,}4 \times 0{,}6 \times 0{,}7$ | 0,168 |
| Tổng | | 0,816 |

Theo công thức (2), $p(\text{"a"} \mid \mathbf{X}) = 0{,}816$. Theo công thức (3), mất mát bằng $-\ln 0{,}816 \approx 0{,}203$. Kiểm tra lại: hai đường bị loại có xác suất 0,072 và 0,112, cộng với 0,816 được đúng 1.

Quy hoạch động cho cùng kết quả mà không phải liệt kê đường. Chuỗi mở rộng là $\mathbf{l}' = (\epsilon, a, \epsilon)$. Bảng 3 ghi giá trị biến tiến tính theo công thức (4).

Bảng 3: Biến tiến $\phi_t(j)$ trong ví dụ

| Bước $t$ | $j = 1$, nhãn $\epsilon$ | $j = 2$, nhãn a | $j = 3$, nhãn $\epsilon$ |
| --- | --- | --- | --- |
| 1 | 0,4 | 0,6 | 0 |
| 2 | $0{,}4 \times 0{,}4 = 0{,}16$ | $(0{,}6 + 0{,}4) \times 0{,}6 = 0{,}6$ | $(0 + 0{,}6) \times 0{,}4 = 0{,}24$ |
| 3 | $0{,}16 \times 0{,}7 = 0{,}112$ | $(0{,}6 + 0{,}16) \times 0{,}3 = 0{,}228$ | $(0{,}24 + 0{,}6) \times 0{,}7 = 0{,}588$ |

Theo công thức (5), $p = \phi_3(3) + \phi_3(2) = 0{,}588 + 0{,}228 = 0{,}816$, trùng với tổng ở Bảng 2.

Ví dụ cũng cho thấy giới hạn của giải mã theo công thức (7). Đường tốt nhất là $(a, a, \epsilon)$ với xác suất 0,252, gộp đúng thành "a". Tuy vậy đường này chỉ chiếm chưa tới một phần ba xác suất 0,816 của chuỗi "a". Khi các ứng viên gần nhau, chuỗi có tổng xác suất lớn nhất có thể khác với chuỗi gộp từ đường tốt nhất.

## 4. Áp dụng trong đề tài

- **Tập nhãn:** lớp đầu ra có 162 nhãn, gồm 161 ký tự của VNOnDB và nhãn trống. Đây là con số 162 trong `01-mo-ta-de-tai.md`, mục 7.3.
- **Lý do chọn CTC:** VNOnDB chỉ có văn bản theo dòng, không có nhãn căn chỉnh theo từng điểm, đúng trường hợp CTC được thiết kế cho [@graves2006]. Hệ thống nhận dạng chữ viết tay dạng nét của Google cũng huấn luyện BiLSTM bằng CTC [@carbune2019].
- **Điều kiện độ dài:** CNN 1D giảm độ dài chuỗi 4 lần, nên phải kiểm tra công thức (6) cho mọi dòng huấn luyện. Dòng vi phạm làm mất mát vô cùng lớn và hỏng cả lô huấn luyện. Cách kiểm tra và xử lý thuộc `03-du-lieu.md` (dự kiến).
- **Cài đặt:** dùng hàm CTC có sẵn của TensorFlow, chỉ định vị trí nhãn trống và độ dài thật của từng dòng sau khi giảm độ dài, không dùng độ dài đã đệm. Lựa chọn cụ thể ghi ở `04-thiet-ke-he-thong.md`.
- **Giải mã:** giải mã theo công thức (7) dùng để đo tỷ lệ lỗi ký tự (CER) trên tập kiểm định trong lúc huấn luyện, vì nhanh và không cần mô hình ngôn ngữ. Bản đưa lên điện thoại dùng beam search kết hợp n-gram âm tiết.

## 5. Hạn chế

- **Giả định độc lập giữa các bước:** công thức (1) coi các bước độc lập khi đã biết $\mathbf{X}$, nên CTC không tự học quan hệ giữa các ký tự đầu ra. Việc chọn giữa "ma", "má", "mà" theo ngữ cảnh phải nhờ mô hình ngôn ngữ ở bước giải mã.
- **Căn chỉnh đơn điệu:** thứ tự ký tự đầu ra phải theo thứ tự thời gian của đầu vào. Nét dấu thanh viết trễ, nhất là dấu thêm vào sau khi đã viết sang hàng khác, nằm xa chữ cái của nó trong chuỗi. Lớp BiLSTM phải mang thông tin của nét trễ về đúng bước của chữ cái, nên đây là rủi ro cần đo trong kịch bản "Dấu thêm muộn".
- **Ràng buộc độ dài:** công thức (6) đặt giới hạn cho mức giảm độ dài chuỗi. Giảm mạnh hơn để chạy nhanh hơn có thể làm một số dòng dài vi phạm điều kiện.
- **Xác suất quá tự tin:** đầu ra CTC thường tập trung gần hết xác suất vào một nhãn ở mỗi bước, và mô hình quá tự tin trên chính dữ liệu đã học. Vì vậy trọng số của mô hình ngôn ngữ phải chỉnh trên dữ liệu khác với tập huấn luyện [@carbune2019].
