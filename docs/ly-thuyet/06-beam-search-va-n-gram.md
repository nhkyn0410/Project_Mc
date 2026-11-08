# Beam search và mô hình ngôn ngữ n-gram

Trạng thái: Nháp

Tài liệu này trình bày cách giải mã đầu ra của mô hình Connectionist Temporal Classification (CTC) bằng beam search kết hợp mô hình ngôn ngữ n-gram âm tiết. Đây là bước biến xác suất từng bước thời gian thành văn bản tiếng Việt có dấu, và là nơi ngữ cảnh giúp chọn đúng dấu thanh. Tài liệu dành cho người viết bộ giải mã và phần cơ sở lý thuyết của báo cáo, và nên đọc sau `05-ctc.md`.

## 1. Bài toán

Đầu vào của bước giải mã là ma trận xác suất $p_t(k)$ do mô hình cho ra, với $T$ bước thời gian và 162 nhãn. Đầu ra cần có là chuỗi ký tự $\hat{\mathbf{l}}$ hợp lý nhất cho dòng đó.

Giải mã đơn giản ở `05-ctc.md`, mục 2.5, có hai điểm yếu. Thứ nhất, nó chỉ xét một đường căn chỉnh, trong khi xác suất của một chuỗi là tổng trên nhiều đường. Thứ hai, CTC coi các bước độc lập với nhau, nên mô hình không biết âm tiết nào hay đi cùng âm tiết nào. Với tiếng Việt, điểm yếu thứ hai rõ nhất ở dấu thanh: nét viết của "ma", "má", "mà" có thể gần giống nhau, và chỉ ngữ cảnh mới phân biệt được.

Bài toán của bước giải mã vì vậy là tìm chuỗi vừa khớp với nét viết, vừa hợp với cách dùng tiếng Việt, trong thời gian đủ ngắn để chạy trên điện thoại.

## 2. Nguyên lý

### 2.1. Điểm kết hợp

Điểm của một chuỗi ứng viên $\mathbf{l}$ cộng ba phần: xác suất theo nét viết, xác suất theo mô hình ngôn ngữ và điểm thưởng theo số âm tiết [@hannun2014]:

$$
\hat{\mathbf{l}} = \arg\max_{\mathbf{l}} \Big[ \ln p(\mathbf{l} \mid \mathbf{X}) + \alpha \ln P_{\text{LM}}\big(\mathbf{w}(\mathbf{l})\big) + \beta \, \big|\mathbf{w}(\mathbf{l})\big| \Big] \tag{1}
$$

trong đó $p(\mathbf{l} \mid \mathbf{X})$ là xác suất CTC của chuỗi, $\mathbf{w}(\mathbf{l})$ là dãy âm tiết của chuỗi, $|\mathbf{w}(\mathbf{l})|$ là số âm tiết, $\alpha$ là trọng số của mô hình ngôn ngữ và $\beta$ là điểm thưởng cho mỗi âm tiết. Mô hình ngôn ngữ luôn trừ điểm khi chuỗi dài thêm, nên thiếu $\beta$ thì bộ giải mã có xu hướng bỏ sót âm tiết.

### 2.2. Mô hình ngôn ngữ n-gram âm tiết

Mô hình ngôn ngữ gán xác suất cho một dãy âm tiết. Mô hình n-gram giả định mỗi âm tiết chỉ phụ thuộc vào $n - 1$ âm tiết đứng ngay trước nó:

$$
P_{\text{LM}}(w_1, \ldots, w_m) \approx \prod_{i=1}^{m} P(w_i \mid w_{i-n+1}, \ldots, w_{i-1}) \tag{2}
$$

trong đó $w_i$ là âm tiết thứ $i$ và $m$ là số âm tiết của dãy. Các xác suất có điều kiện được ước lượng bằng cách đếm trên kho văn bản:

$$
P(w_i \mid w_{i-n+1}, \ldots, w_{i-1}) = \frac{C(w_{i-n+1}, \ldots, w_{i-1}, w_i)}{C(w_{i-n+1}, \ldots, w_{i-1})} \tag{3}
$$

trong đó $C(\cdot)$ là số lần cụm âm tiết xuất hiện. Công thức (3) cho xác suất bằng 0 với mọi cụm chưa gặp trong kho văn bản, kể cả cụm đúng. Vì vậy phải làm trơn: bớt một phần xác suất của các cụm đã gặp, rồi chia cho các cụm chưa gặp dựa trên cụm ngắn hơn. Kneser-Ney là phương pháp làm trơn hay dùng cho n-gram [@kneser1995].

Tiếng Việt viết cách nhau theo âm tiết, nên dùng âm tiết làm đơn vị là tự nhiên: tách theo khoảng trắng là có ngay dãy âm tiết, không cần bước tách từ.

### 2.3. Beam search trên tiền tố

Không thể tính điểm theo công thức (1) cho mọi chuỗi có thể. Beam search duyệt các bước thời gian từ 1 đến $T$ và chỉ giữ $W$ tiền tố có điểm cao nhất sau mỗi bước [@hannun2014].

Một tiền tố $\mathbf{c}$ là chuỗi ký tự đã gộp, nên nhiều đường căn chỉnh cùng dẫn tới nó. Để cộng đúng xác suất của các đường đó, mỗi tiền tố mang hai giá trị: $p_b(\mathbf{c}, t)$ cho các đường kết thúc bằng nhãn trống và $p_{nb}(\mathbf{c}, t)$ cho các đường kết thúc bằng một ký tự. Cách tách này cần thiết vì chỉ có đường kết thúc bằng nhãn trống mới được nối thêm một ký tự trùng với ký tự cuối của tiền tố, theo phép gộp ở `05-ctc.md`.

Tại bước $t$, tiền tố giữ nguyên khi mô hình phát nhãn trống, hoặc phát lại ký tự cuối $c_{\text{cuối}}$ của nó:

$$
\begin{aligned}
p_b(\mathbf{c}, t) &= \big(p_b(\mathbf{c}, t-1) + p_{nb}(\mathbf{c}, t-1)\big)\, p_t(\epsilon) \\
p_{nb}(\mathbf{c}, t) &= p_{nb}(\mathbf{c}, t-1)\, p_t(c_{\text{cuối}})
\end{aligned} \tag{4}
$$

Tiền tố dài thêm một ký tự $k$ khi mô hình phát $k$. Nếu $k$ trùng ký tự cuối thì chỉ các đường kết thúc bằng nhãn trống được nối:

$$
p_{nb}(\mathbf{c}k, t) \mathrel{+}=
\begin{cases}
p_b(\mathbf{c}, t-1)\, p_t(k) & \text{nếu } k = c_{\text{cuối}} \\
\big(p_b(\mathbf{c}, t-1) + p_{nb}(\mathbf{c}, t-1)\big)\, p_t(k) & \text{trường hợp còn lại}
\end{cases} \tag{5}
$$

trong đó $\mathbf{c}k$ là tiền tố $\mathbf{c}$ nối thêm ký tự $k$, và dấu cộng bằng nghĩa là cộng dồn khi nhiều tiền tố cùng dẫn tới $\mathbf{c}k$.

Mô hình ngôn ngữ chỉ được tính khi một âm tiết vừa hoàn thành, tức là khi $k$ là khoảng trắng. Lúc đó điểm của tiền tố nhận thêm $\alpha \ln P(w \mid \text{các âm tiết trước}) + \beta$, với $w$ là âm tiết vừa xong. Sau bước cuối, âm tiết cuối cùng được tính nốt rồi chọn tiền tố có điểm cao nhất.

### 2.4. Chọn trọng số

Hai trọng số $\alpha$ và $\beta$ không học được cùng lúc với mô hình. Mô hình quá tự tin trên dữ liệu nó đã học, nên nếu chỉnh $\alpha$ và $\beta$ trên tập huấn luyện thì mô hình ngôn ngữ sẽ bị đánh giá thấp. Hai trọng số phải được chỉnh trên một tập dữ liệu khác, thường là tập kiểm định [@carbune2019].

## 3. Ví dụ minh họa

Giả sử sau beam search còn hai ứng viên cho một dòng, khác nhau ở một dấu phụ: "ăn côm" và "ăn cơm". Mô hình CTC hơi nghiêng về ứng viên sai. Bảng 1 ghi các giá trị giả định dùng cho ví dụ.

Bảng 1: Giá trị giả định của hai ứng viên

| Ứng viên | $\ln p(\mathbf{l} \mid \mathbf{X})$ | $P(\text{âm tiết hai} \mid \text{"ăn"})$ | $\ln$ của xác suất đó |
| --- | --- | --- | --- |
| "ăn côm" | -1,0 | 0,0001 | -9,210 |
| "ăn cơm" | -1,4 | 0,2 | -1,609 |

Hai ứng viên có cùng âm tiết đầu và cùng số âm tiết, nên phần điểm của âm tiết đầu và của $\beta$ bằng nhau và có thể bỏ qua khi so sánh. Chọn $\alpha = 0{,}5$ và tính theo công thức (1):

$$
\begin{aligned}
\text{"ăn côm"}: &\quad -1{,}0 + 0{,}5 \times (-9{,}210) = -5{,}605 \\
\text{"ăn cơm"}: &\quad -1{,}4 + 0{,}5 \times (-1{,}609) = -2{,}205
\end{aligned} \tag{6}
$$

"ăn cơm" có điểm cao hơn và được chọn. Nếu $\alpha = 0$, tức là không dùng mô hình ngôn ngữ, bộ giải mã sẽ chọn "ăn côm" vì $-1{,}0 > -1{,}4$. Ngược lại, nếu $\alpha$ quá lớn thì mô hình ngôn ngữ lấn át nét viết, và bộ giải mã sẽ sửa cả những âm tiết người dùng viết đúng nhưng ít gặp. Đây là lý do $\alpha$ phải được chỉnh trên tập kiểm định, theo mục 2.4.

## 4. Áp dụng trong đề tài

- **Vị trí trong hệ thống:** beam search và n-gram âm tiết tạo thành mô hình M2 trong `01-mo-ta-de-tai.md`, mục 7.3, là bản đưa lên điện thoại. Giải mã đơn giản ở `05-ctc.md` chỉ dùng để theo dõi tỷ lệ lỗi ký tự (CER) trong lúc huấn luyện.
- **Kho văn bản cho n-gram:** gồm văn bản của tập huấn luyện VNOnDB và một kho văn bản khác không lấy từ VieTreeBank, vì văn bản kiểm thử của VNOnDB lấy từ VieTreeBank. Các câu trùng với tập kiểm thử và với câu đề của tập tự thu phải được loại trước khi đếm. Chi tiết thuộc `03-du-lieu.md` (dự kiến).
- **Chuẩn hóa văn bản:** kho văn bản và nhãn phải cùng chuẩn Unicode NFC và cùng kiểu đặt dấu thanh. Nếu không, một âm tiết bị đếm thành hai, và xác suất của cả hai đều thấp hơn thực tế.
- **Chỉnh trọng số:** $\alpha$, $\beta$ chỉnh trên tập kiểm định, tập kiểm thử chỉ chạy một lần ở cuối.
- **Ba ứng viên cho người dùng:** sau bước cuối, các tiền tố còn lại trong beam đã được xếp theo điểm, nên có sẵn danh sách ứng viên mà không phải tính thêm.
- **Ràng buộc trên điện thoại:** $W$ lớn thì chính xác hơn nhưng chậm hơn, và n-gram bậc cao thì chính xác hơn nhưng tốn bộ nhớ hơn. Giá trị của $W$ và $n$ sẽ chọn bằng thí nghiệm trong `05-ke-hoach-thi-nghiem.md`, sao cho mô hình và n-gram không quá 20 MB và mỗi dòng nhận dạng không quá 1 giây (dự kiến). Bộ giải mã viết bằng Kotlin, và nên có bản tham chiếu bằng Python để so kết quả.

## 5. Hạn chế

- **Beam có thể bỏ sót đáp án:** chuỗi đúng bị loại ở một bước giữa chừng thì không quay lại được, dù điểm cuối của nó cao nhất. $W$ càng nhỏ thì rủi ro càng lớn.
- **Mô hình ngôn ngữ chỉ tác động ở ranh giới âm tiết:** trong lúc một âm tiết chưa xong, beam chỉ dựa vào xác suất của nét viết, nên âm tiết đúng có thể bị loại trước khi mô hình ngôn ngữ kịp giúp.
- **Ngữ cảnh ngắn:** n-gram chỉ nhìn $n - 1$ âm tiết trước. Nó không dùng được ngữ cảnh xa hơn hay ngữ cảnh phía sau âm tiết đang xét.
- **Lệch miền văn bản:** n-gram học từ một kho văn bản sẽ ưu tiên cách viết của kho đó. Người dùng viết nội dung khác, như tên riêng hay từ chuyên ngành, có thể bị sửa sai.
- **Chi phí:** mỗi bước phải xét $W$ tiền tố nhân với số nhãn, cộng thêm tra cứu n-gram, nên beam search chậm hơn nhiều so với giải mã đơn giản. Độ trễ này cộng vào thời gian chạy mô hình trên điện thoại.
