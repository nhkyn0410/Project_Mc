# Mạng hồi quy, LSTM và BiLSTM

Trạng thái: Nháp

Tài liệu này trình bày mạng nơ-ron hồi quy, ô nhớ dài ngắn hạn (LSTM) và LSTM hai chiều (BiLSTM). Ba lớp BiLSTM là phần chính của mô hình nhận dạng, nằm giữa mạng nơ-ron tích chập một chiều (CNN 1D) và lớp đầu ra của hàm mất mát CTC. Tài liệu dành cho người viết phần thiết kế mô hình và phần cơ sở lý thuyết của báo cáo, và là nền cho `05-ctc.md`.

## 1. Bài toán

Đầu vào của bước này là chuỗi $\mathbf{z}_1, \ldots, \mathbf{z}_T$, mỗi véc-tơ mô tả một đoạn ngắn của nét viết. Đầu ra cần có là một véc-tơ $\mathbf{h}_t$ cho mỗi bước, đủ thông tin để lớp đầu ra quyết định nhãn của bước đó.

Một đoạn nét ngắn thường không đủ để biết đó là chữ gì. Nét móc có thể là phần đầu của "u" hay của "ư", và chỉ nhìn tiếp mới biết có dấu móc hay không. Với tiếng Việt, dấu thanh và dấu phụ thường được viết sau phần thân chữ, có khi sau cả một âm tiết hay một câu. Vì vậy véc-tơ $\mathbf{h}_t$ phải mang thông tin của cả những bước trước và những bước sau bước $t$.

## 2. Nguyên lý

### 2.1. Mạng hồi quy

Mạng hồi quy xử lý chuỗi lần lượt từng bước, và đưa trạng thái của bước trước vào bước sau:

$$
\mathbf{h}_t = \tanh\big(\mathbf{V}_h [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_h\big) \tag{1}
$$

trong đó $[\mathbf{h}_{t-1}; \mathbf{z}_t]$ là véc-tơ ghép từ trạng thái trước và đầu vào hiện tại. Cùng một bộ trọng số được dùng ở mọi bước, nên mạng xử lý được chuỗi dài bất kỳ.

Khi huấn luyện, đạo hàm truyền ngược qua nhiều bước sẽ bị nhân liên tiếp với cùng một ma trận và với đạo hàm của $\tanh$. Qua vài chục bước, đạo hàm thường nhỏ dần về 0, nên mạng hồi quy đơn giản khó học quan hệ giữa hai bước cách xa nhau [@hochreiter1997].

### 2.2. LSTM

LSTM thêm một ô nhớ $\mathbf{C}_t$ và ba cổng điều khiển việc đọc, ghi và xóa ô nhớ [@hochreiter1997]. Cổng quên được bổ sung sau, cho phép mạng chủ động xóa thông tin cũ [@gers2000]. Mỗi cổng là một véc-tơ giá trị từ 0 đến 1, tính từ trạng thái trước và đầu vào hiện tại:

$$
\begin{aligned}
\mathbf{f}_t &= \sigma\big(\mathbf{V}_f [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_f\big) \\
\mathbf{i}_t &= \sigma\big(\mathbf{V}_i [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_i\big) \\
\mathbf{o}_t &= \sigma\big(\mathbf{V}_o [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_o\big)
\end{aligned} \tag{2}
$$

trong đó $\mathbf{f}_t$ là cổng quên, $\mathbf{i}_t$ là cổng ghi và $\mathbf{o}_t$ là cổng ra. Giá trị ứng viên để ghi vào ô nhớ được tính theo cùng cách nhưng dùng $\tanh$:

$$
\tilde{\mathbf{C}}_t = \tanh\big(\mathbf{V}_C [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_C\big) \tag{3}
$$

Ô nhớ mới giữ lại một phần ô nhớ cũ theo cổng quên, cộng thêm một phần giá trị ứng viên theo cổng ghi:

$$
\mathbf{C}_t = \mathbf{f}_t \odot \mathbf{C}_{t-1} + \mathbf{i}_t \odot \tilde{\mathbf{C}}_t \tag{4}
$$

Trạng thái ẩn là phần ô nhớ mà cổng ra cho phép đi ra ngoài:

$$
\mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{C}_t) \tag{5}
$$

Điểm mấu chốt nằm ở công thức (4): ô nhớ đi từ bước này sang bước sau qua phép cộng, không qua phép nhân ma trận. Khi cổng quên gần 1, thông tin và đạo hàm đi qua nhiều bước mà không bị thu nhỏ nhanh, nên LSTM học được quan hệ xa hơn nhiều so với mạng hồi quy đơn giản.

### 2.3. BiLSTM

LSTM ở mục 2.2 chỉ đọc chuỗi theo một chiều, nên $\mathbf{h}_t$ chỉ biết các bước từ 1 đến $t$. Mạng hồi quy hai chiều chạy thêm một mạng thứ hai từ bước $T$ ngược về bước 1, rồi ghép trạng thái của hai chiều tại mỗi bước [@schuster1997]:

$$
\mathbf{h}_t = \big[\overrightarrow{\mathbf{h}}_t ; \overleftarrow{\mathbf{h}}_t\big] \tag{6}
$$

trong đó $\overrightarrow{\mathbf{h}}_t$ là trạng thái của chiều xuôi sau khi đọc các bước từ 1 đến $t$, còn $\overleftarrow{\mathbf{h}}_t$ là trạng thái của chiều ngược sau khi đọc các bước từ $T$ về $t$. Hai chiều có bộ trọng số riêng. Véc-tơ ghép có $2d$ chiều và là đầu vào của lớp kế tiếp.

Nhiều lớp BiLSTM có thể xếp chồng lên nhau: chuỗi $\mathbf{h}_t$ của lớp dưới là chuỗi $\mathbf{z}_t$ của lớp trên. Hệ thống nhận dạng chữ viết tay dạng nét của Google dùng nhiều lớp BiLSTM xếp chồng, huấn luyện bằng CTC [@carbune2019].

### 2.4. Số tham số

Mỗi cổng và giá trị ứng viên có một ma trận trọng số kích thước $d \times (d + d_{\text{vào}})$ và một véc-tơ độ lệch $d$ phần tử. Một chiều LSTM có bốn bộ như vậy, nên số tham số là:

$$
4d\,(d + d_{\text{vào}} + 1) \tag{7}
$$

Một lớp BiLSTM có gấp đôi số này vì có hai chiều. Số tham số không phụ thuộc vào độ dài chuỗi $T$, nhưng thời gian chạy thì tăng theo $T$.

## 3. Ví dụ minh họa

Ví dụ đầu tính một bước của LSTM có một ô nhớ, để thấy vai trò của từng cổng. Giả sử ô nhớ trước là $C_{t-1} = 0{,}8$, các cổng có giá trị $f_t = 0{,}9$, $i_t = 0{,}1$, $o_t = 0{,}6$, và giá trị ứng viên là $\tilde{C}_t = 0{,}5$. Theo công thức (4) và (5):

$$
\begin{aligned}
C_t &= 0{,}9 \times 0{,}8 + 0{,}1 \times 0{,}5 = 0{,}77 \\
h_t &= 0{,}6 \times \tanh(0{,}77) \approx 0{,}6 \times 0{,}647 \approx 0{,}388
\end{aligned} \tag{8}
$$

Cổng quên lớn và cổng ghi nhỏ, nên ô nhớ gần như giữ nguyên giá trị cũ. Nếu các cổng giữ nguyên như vậy và giá trị ứng viên bằng 0 trong 10 bước, ô nhớ còn $0{,}8 \times 0{,}9^{10} \approx 0{,}279$. Thông tin vẫn còn sau 10 bước. Với mạng hồi quy đơn giản, không có đường cộng như công thức (4) để giữ thông tin này.

Ví dụ thứ hai áp công thức (7) cho ba lớp BiLSTM của mô hình M1, mỗi chiều có $d = 128$ ô. Lớp thứ nhất nhận đầu ra 128 chiều của CNN 1D. Hai lớp sau nhận véc-tơ ghép $2 \times 128 = 256$ chiều của lớp bên dưới. Bảng 1 ghi kết quả.

Bảng 1: Số tham số của ba lớp BiLSTM trong mô hình M1

| Lớp | $d_{\text{vào}}$ | Tham số một chiều | Tham số hai chiều |
| --- | --- | --- | --- |
| BiLSTM 1 | 128 | 131.584 | 263.168 |
| BiLSTM 2 | 256 | 197.120 | 394.240 |
| BiLSTM 3 | 256 | 197.120 | 394.240 |
| Tổng | | | 1.051.648 |

Ba lớp BiLSTM chiếm khoảng 1,05 triệu trong 1,14 triệu tham số của M1 ước tính trong `01-mo-ta-de-tai.md`, mục 7.3. Phần còn lại thuộc CNN 1D và lớp đầu ra.

## 4. Áp dụng trong đề tài

- **Vì sao cần hai chiều:** CTC chỉ cho phép đầu ra theo đúng thứ tự thời gian của đầu vào, theo `05-ctc.md`, mục 5. Nét dấu thanh viết trễ xuất hiện sau chữ cái của nó trong chuỗi. Chiều ngược mang thông tin của nét trễ về đúng bước của chữ cái, nên mô hình mới phát ra được ký tự có dấu ở đúng chỗ. Đây là lý do đề tài dùng BiLSTM thay cho LSTM một chiều.
- **Cấu hình:** mô hình cơ sở M0 có 2 lớp BiLSTM 100 ô, mô hình đề xuất M1 có 3 lớp BiLSTM 128 ô sau CNN 1D, theo `01-mo-ta-de-tai.md`, mục 7.3. Cấu hình huấn luyện khởi đầu dùng dropout 0,5 sau mỗi lớp LSTM [@carbune2019].
- **Chọn LSTM thay cho GRU:** công cụ chuyển đổi LiteRT có hướng dẫn chuyển đổi sẵn cho lớp LSTM của Keras. Chi tiết thuộc `06-trien-khai-android.md` (dự kiến).
- **Kết quả tạm thời khi đang viết:** chiều ngược cần toàn bộ chuỗi, nên ứng dụng chạy lại cả dòng sau mỗi lần người dùng dừng bút, thay vì cập nhật từng bước.

## 5. Hạn chế

- **Không xử lý dần theo dòng chảy:** BiLSTM chỉ cho kết quả khi đã có đủ chuỗi. Mỗi lần nhận dạng lại phải chạy từ đầu, nên chi phí tăng theo độ dài dòng.
- **Tính tuần tự:** bước $t$ phải chờ bước $t - 1$ xong, nên khó tận dụng tính toán song song. Đây là lý do CNN 1D giảm độ dài chuỗi 4 lần trước khi vào BiLSTM.
- **Quan hệ rất xa vẫn khó:** LSTM giữ thông tin tốt hơn mạng hồi quy đơn giản nhưng không phải vô hạn. Dấu thêm vào một hàng đã viết từ lâu có thể cách chữ cái hàng trăm bước, và cần đo trong kịch bản "Dấu thêm muộn".
- **Số tham số tăng nhanh theo số ô:** theo công thức (7), số tham số tăng gần theo bình phương của $d$. Tăng số ô để tăng độ chính xác sẽ nhanh chóng chạm giới hạn dung lượng và độ trễ trên điện thoại.
