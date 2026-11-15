# Mạng nơ-ron tích chập hai chiều

Trạng thái: Nháp

Tài liệu này trình bày phép tích chập hai chiều và cách mạng nơ-ron tích chập hai chiều (CNN 2D) biến ảnh của một dòng thành chuỗi véc-tơ. CNN 2D là phần đầu của mô hình nhận dạng, nằm trước LSTM hai chiều (BiLSTM). Tài liệu dành cho người viết phần thiết kế mô hình và phần cơ sở lý thuyết của báo cáo, và nên đọc trước `04-lstm-va-bilstm.md`.

## 1. Bài toán

Đầu vào là ảnh xám $\mathbf{X}$ của một dòng, cao $H$ và rộng $R$ điểm ảnh. Đầu ra cần có là chuỗi $T$ véc-tơ $\mathbf{z}_t$, mỗi véc-tơ mô tả một dải cột của ảnh theo thứ tự từ trái sang phải. Lớp BiLSTM chỉ nhận chuỗi, nên mô hình cần bước chuyển từ ảnh sang chuỗi này.

Mạng kết nối đầy đủ không phù hợp với ảnh. Với khung rộng 512, cao 64 điểm ảnh, một lớp 128 ô đã cần 4.194.304 trọng số. Mạng này cũng phải học lại cùng một nét ở từng vị trí trên dòng.

## 2. Nguyên lý

### 2.1. Phép tích chập

Một bộ lọc là một ma trận trọng số nhỏ, trượt lần lượt qua mọi vị trí của ảnh [@lecun1998]. Với bộ lọc kích thước 3 nhân 3, đầu ra tại mỗi vị trí là:

$$
y_{u,v} = \sum_{u'=-1}^{1} \sum_{v'=-1}^{1} \kappa_{u',v'} \, x_{u+u', v+v'} \tag{1}
$$

trong đó $x_{u,v}$ và $y_{u,v}$ là giá trị tại hàng $u$, cột $v$ của đầu vào và đầu ra, $\kappa_{u',v'}$ là trọng số của bộ lọc. Bộ lọc có giá trị lớn tại những nơi ảnh giống mẫu của nó, ví dụ một cạnh dọc hoặc một đoạn cong.

Phép tích chập có hai tính chất. Mỗi đầu ra chỉ nhìn một vùng nhỏ của ảnh, và cùng một bộ lọc được dùng ở mọi vị trí. Nhờ vậy, số tham số không phụ thuộc vào kích thước ảnh:

$$
\text{số trọng số} = e^2 \, F_{\text{vào}} \, F \tag{2}
$$

trong đó $e$ là kích thước bộ lọc, $F_{\text{vào}}$ là số kênh đầu vào và $F$ là số bộ lọc của lớp. Công thức (2) tính cho lớp không có độ lệch.

### 2.2. Max pooling

Max pooling chia đầu ra thành các ô nhỏ và giữ giá trị lớn nhất của mỗi ô [@lecun1998]. Phép này giảm kích thước đầu ra, nên giảm khối lượng tính toán của các lớp sau. Nó cũng làm đầu ra ít nhạy hơn với các dịch chuyển nhỏ của nét.

### 2.3. Chuẩn hóa theo lô

Chuẩn hóa theo lô đưa đầu ra của một lớp về trung bình 0 và phương sai 1 trên từng lô, rồi học lại một độ lệch và một hệ số co [@ioffe2015]. Trong lúc nhận dạng, lớp này dùng các thống kê đã tích lũy khi huấn luyện, nên kết quả của một dòng không phụ thuộc vào các dòng khác. Lớp này giúp huấn luyện ổn định hơn với tốc độ học lớn.

### 2.4. Từ ảnh thành chuỗi

Sau các lớp tích chập, đầu ra vẫn là một ảnh đặc trưng có chiều cao nhỏ. Mỗi cột của ảnh đặc trưng được ghép thành một véc-tơ, theo thứ tự từ trái sang phải [@shi2015]. Puigcerver cho thấy chỉ cần lớp hồi quy một chiều chạy theo chiều ngang sau bước ghép này, không cần lớp hồi quy đa chiều [@puigcerver2017].

### 2.5. Vùng nhìn

Vùng nhìn là phần ảnh gốc ảnh hưởng tới một giá trị đầu ra. Theo một chiều, vùng nhìn tăng dần qua từng lớp:

$$
v_\ell = v_{\ell-1} + (e_\ell - 1) \, g_{\ell-1}, \quad g_\ell = g_{\ell-1} \, \tau_\ell, \quad v_0 = g_0 = 1 \tag{3}
$$

trong đó $v_\ell$ là vùng nhìn sau lớp thứ $\ell$, $g_\ell$ là bước nhảy tích lũy, $e_\ell$ là kích thước cửa sổ và $\tau_\ell$ là bước nhảy của lớp đó. Công thức (3) cho thấy lớp đặt sau max pooling có vùng nhìn tăng nhanh hơn.

## 3. Ví dụ minh họa

Ví dụ thứ nhất áp công thức (1) cho bộ lọc phát hiện cạnh dọc, có cột trái bằng $-1$, cột giữa bằng 0 và cột phải bằng 1. Trên vùng 3 nhân 3 có cột phải bằng 255 và hai cột còn lại bằng 0, đầu ra bằng $3 \times 255 = 765$. Trên vùng có mọi giá trị bằng nhau, đầu ra bằng 0.

Ví dụ thứ hai theo dõi kích thước qua CNN 2D của mô hình M1, với đầu vào cao 64 và rộng 512. Bảng 1 ghi kết quả, số trọng số tính theo công thức (2) với $e = 3$.

Bảng 1: Kích thước và số trọng số qua bốn khối của mô hình M1

| Khối | Số bộ lọc | Max pooling (cao, rộng) | Đầu ra (cao, rộng, kênh) | Số trọng số |
| --- | --- | --- | --- | --- |
| 1 | 32 | 2, 2 | 32, 256, 32 | 288 |
| 2 | 64 | 2, 1 | 16, 256, 64 | 18.432 |
| 3 | 128 | 2, 1 | 8, 256, 128 | 73.728 |
| 4 | 128 | 2, 1 | 4, 256, 128 | 147.456 |
| Tổng | | | | 239.904 |

Đầu ra của khối 4 có 256 cột, mỗi cột gồm $4 \times 128 = 512$ giá trị. Một lớp kết nối đầy đủ giảm mỗi cột xuống 128 chiều, tạo thành $\mathbf{z}_t$ với $T = 256$.

Ví dụ thứ ba áp công thức (3) cho từng khối. Bảng 2 ghi vùng nhìn sau mỗi khối, tính bằng điểm ảnh trên khung đầu vào.

Bảng 2: Vùng nhìn sau mỗi khối của mô hình M1

| Sau khối | Theo chiều cao | Theo chiều rộng |
| --- | --- | --- |
| 1 | 4 | 4 |
| 2 | 10 | 8 |
| 3 | 22 | 12 |
| 4 | 46 | 16 |

## 4. Áp dụng trong đề tài

- **Cấu trúc:** M0 và M1 có bốn khối, mỗi khối gồm lớp tích chập kích thước 3, chuẩn hóa theo lô, hàm ReLU và max pooling, theo `01-mo-ta-de-tai.md`, mục 7.3. Lớp tích chập không có độ lệch, vì chuẩn hóa theo lô đã có độ lệch riêng.
- **Giảm chiều cao 16 lần, chiều rộng 2 lần:** chiều rộng chỉ giảm ở khối đầu, để còn 256 bước thời gian. Điều kiện độ dài của CTC ở `05-ctc.md`, mục 2.4, cần số bước đủ lớn cho dòng dài nhất.
- **Vùng nhìn:** theo Bảng 2, mỗi bước nhìn 46 điểm ảnh theo chiều cao, đủ bao phần lớn nét chữ. Chiều rộng chỉ 16 điểm ảnh, nên ngữ cảnh ngang do BiLSTM đảm nhiệm.
- **Trên điện thoại:** các lớp này chuyển sang toán tử có sẵn của LiteRT. Chuẩn hóa theo lô được gộp vào phép tính của lớp tích chập, nên không tốn thêm thời gian khi chạy.

## 5. Hạn chế

- **Nhạy với cỡ chữ:** bộ lọc có kích thước cố định, nên chữ lớn hơn nhiều so với lúc huấn luyện sẽ khó nhận ra. Vì vậy mọi dòng phải được đưa về cỡ chữ gần nhau, theo `02-tien-xu-ly-anh.md`.
- **Khung cố định:** đầu vào có chiều rộng cố định, nên dòng dài bị co nhỏ. Dòng 158 ký tự chỉ còn khoảng 3 điểm ảnh cho mỗi ký tự.
- **Mất chi tiết nhỏ:** max pooling và ảnh độ phân giải thấp làm mất các chi tiết nhỏ như dấu chấm, dấu phẩy và một số dấu phụ.
- **Giữ cả nét không cần thiết:** chiều cao đặc trưng còn 4 hàng, nên một phần chi tiết theo chiều dọc đã bị gộp trước khi vào BiLSTM.
