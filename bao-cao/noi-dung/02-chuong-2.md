# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

Chương này trình bày các kiến thức nền mà hệ thống dựa vào, theo thứ tự của luồng xử lý: bài toán nhận dạng dòng chữ viết tay dạng ảnh, cách vẽ nét thành ảnh, mạng tích chập hai chiều, mạng hồi quy LSTM và BiLSTM, hàm mất mát CTC, giải mã bằng beam search kết hợp mô hình ngôn ngữ n-gram, và lượng tử hóa mô hình. Mỗi mục nêu bài toán, nguyên lý, một ví dụ tính tay và cách áp dụng trong đề tài.

## 2.1. Nhận dạng dòng chữ viết tay dạng ảnh

### 2.1.1. Bài toán

Đầu vào là ảnh $\mathbf{X}$ của một dòng chữ viết tay. Đầu ra là chuỗi ký tự $\mathbf{l}$ của dòng đó. Dữ liệu chỉ có nhãn theo cả dòng, không có vị trí của từng ký tự trên ảnh. Bài toán vì vậy có hai khó khăn: số ký tự thay đổi theo từng dòng, và không biết trước ký tự nào nằm ở cột nào.

Chữ viết tay có thể lưu dưới hai dạng. Dạng nét giữ thứ tự viết và điểm nhấc bút, còn dạng ảnh chỉ giữ hình dạng. Bảng {{bang:d1-b1}} so sánh hai dạng theo các điểm có ảnh hưởng tới đề tài.

| Tiêu chí | Dạng nét | Dạng ảnh |
| --- | --- | --- |
| Thông tin có sẵn | Tọa độ, thứ tự viết, điểm nhấc bút | Hình dạng nét |
| Nét trễ | Nằm xa chữ cái trong chuỗi đầu vào | Nằm đúng chỗ trên ảnh |
| Phụ thuộc thứ tự viết | Có | Không |
| Kích thước đầu vào | Thay đổi theo số điểm | Khung cố định, dễ chạy trên điện thoại |
| Mức lỗi thấp nhất đã công bố trên VNOnDB | 1,02%, theo mục 1.5 | 3,45%, cùng nguồn |

Bảng: So sánh chữ viết tay dạng nét và dạng ảnh {#bang:d1-b1}

### 2.1.2. Nguyên lý

Kiến trúc phổ biến ghép ba phần [@shi2015]. Mạng nơ-ron tích chập (CNN) trích đặc trưng từ ảnh, lớp hồi quy đọc đặc trưng theo chiều ngang, và hàm mất mát Connectionist Temporal Classification (CTC) huấn luyện mô hình khi chỉ có nhãn theo dòng [@graves2006]. Puigcerver cho thấy kiến trúc CNN kết hợp LSTM hai chiều (BiLSTM) đạt kết quả tốt trên dòng chữ viết tay, kèm tăng cường dữ liệu phù hợp [@puigcerver2017].

Khi nhận dạng, mô hình tìm chuỗi có xác suất cao nhất theo ảnh:

$$\hat{\mathbf{l}} = \arg\max_{\mathbf{l}} \, p(\mathbf{l} \mid \mathbf{X})$$ {#ct:d1-1}

trong đó $\hat{\mathbf{l}}$ là chuỗi đọc ra và $p(\mathbf{l} \mid \mathbf{X})$ là xác suất CTC của chuỗi $\mathbf{l}$. Cách tính xác suất này nằm trong mục 2.5, còn cách tìm chuỗi nằm trong mục 2.6.

Mô hình đọc ảnh theo các cột từ trái sang phải, và mỗi bước thời gian ứng với một dải cột. Cách đọc này giả định các ký tự nối tiếp nhau theo chiều ngang. Vì vậy dòng phải nằm gần như thẳng hàng, và dòng viết thành nhiều hàng phải được ghép lại trước khi nhận dạng.

### 2.1.3. Ví dụ minh họa

Giả sử người dùng viết chữ "á" theo hai thứ tự: viết chữ "a" rồi đặt dấu sắc ngay, hoặc viết hết dòng rồi quay lại đặt dấu sắc. Hai cách cho chuỗi nét khác nhau, nên mô hình dạng nét nhìn thấy hai đầu vào khác nhau. Với ảnh của dòng, nét dấu sắc nằm cùng một vị trí, nên hai đầu vào giống hệt nhau.

Ví dụ thứ hai tính số bước thời gian trên mỗi ký tự. Khung rộng 512 điểm ảnh, CNN giảm chiều rộng 2 lần, nên $T = 256$. Dòng trung bình của VNOnDB có 68 ký tự, tức khoảng 3,8 bước cho mỗi ký tự. Dòng dài nhất có 158 ký tự, tức khoảng 1,6 bước cho mỗi ký tự, vẫn thỏa điều kiện độ dài ở mục 2.5.5.

### 2.1.4. Áp dụng trong đề tài

- **Lý do dùng ảnh:** các tệp nét gốc của VNOnDB không tải được, nên đề tài huấn luyện trên bản ảnh, theo mục 3.1.
- **Vị trí của nét:** ứng dụng vẫn thu nét. Nét được dùng để ghép các hàng thành dòng ảo, rồi được vẽ thành ảnh, theo mục 2.2.
- **Kiến trúc:** đề tài dùng CNN 2D, BiLSTM và CTC, theo mục 3.2.4 và mục 2.3.
- **Mốc so sánh:** ngưỡng của đề tài lấy từ các mô hình dạng ảnh trên cùng tập kiểm thử [@pham2025], theo mục 1.2.

### 2.1.5. Hạn chế

- **Mất thông tin thứ tự viết:** dạng ảnh không phân biệt được hai chữ có hình dạng giống nhau nhưng viết khác thứ tự, trong khi các hệ thống dạng nét tốt nhất trên VNOnDB có mức lỗi thấp hơn [@le2019].
- **Lệch cách vẽ:** ảnh huấn luyện và ảnh do ứng dụng vẽ có thể khác nhau về độ dày nét và cách co, theo mục 3.1.3.
- **Giả định dòng thẳng:** chữ viết lên dốc hoặc xuống dốc nhiều sẽ khó đọc theo từng cột, và lớp ghép đoạn chỉ căn đường chân chữ theo từng đoạn.
- **Dữ liệu ít:** tập huấn luyện chỉ có 4.433 dòng, nên kết quả phụ thuộc nhiều vào tăng cường dữ liệu [@puigcerver2017].

## 2.2. Vẽ nét thành ảnh và tiền xử lý ảnh

### 2.2.1. Bài toán

Mô hình nhận ảnh xám $\mathbf{X}$ cao $H$, rộng $R$ điểm ảnh. Khi huấn luyện, ảnh lấy từ bản ảnh của bộ dữ liệu HANDS-VNOnDB (VNOnDB). Trên điện thoại, đầu vào là các nét của một dòng liền hoặc một dòng ảo, mỗi nét là một chuỗi điểm có tọa độ. Bài toán gồm bốn phần:

- **Vẽ nét thành ảnh:** từ chuỗi điểm tạo ảnh xám có mép nét mềm như ảnh huấn luyện.
- **Đặt dòng vào khung:** đưa mọi dòng, dài hay ngắn, về cùng một khung mà vẫn giữ tỷ lệ của chữ.
- **Tăng cường dữ liệu:** tạo biến thể của ảnh huấn luyện để mô hình không học thuộc cách vẽ của bộ dữ liệu.
- **Vẽ lại ảnh huấn luyện:** tạo ảnh huấn luyện giống ảnh do bộ vẽ của ứng dụng tạo ra.

Mô hình chỉ học được những gì có trong ảnh huấn luyện. Khi ảnh trên điện thoại lệch ảnh huấn luyện về độ dày nét, độ đậm hay cỡ chữ, tỷ lệ lỗi ký tự (CER) tăng lên dù chữ vẫn dễ đọc với người.

### 2.2.2. Vẽ đoạn thẳng có khử răng cưa

Nét được vẽ thành các đoạn thẳng nối hai điểm liên tiếp. Nếu mỗi điểm ảnh chỉ được tô hoặc không tô, mép nét sẽ có răng cưa. Răng cưa là hiện tượng lấy mẫu chưa đủ dày, và cách khắc phục là lọc hình trước khi lấy mẫu [@crow1977]. Lấy mẫu dày là cách lọc đơn giản: vẽ trên lưới mịn gấp $\rho$ lần mỗi chiều, rồi lấy trung bình mỗi khối $\rho$ nhân $\rho$ ô thành một điểm ảnh.

Với đoạn thẳng từ $\mathbf{e}_1$ đến $\mathbf{e}_2$ và một ô có tâm $\mathbf{g}$, điểm gần $\mathbf{g}$ nhất trên đoạn ứng với vị trí:

$$\eta = \min\left(1, \max\left(0, \frac{(\mathbf{g} - \mathbf{e}_1) \cdot (\mathbf{e}_2 - \mathbf{e}_1)}{\lVert \mathbf{e}_2 - \mathbf{e}_1 \rVert^2}\right)\right)$$ {#ct:d2-1}

trong đó $\mathbf{e}_1$, $\mathbf{e}_2$ là hai đầu của đoạn thẳng, $\mathbf{g}$ là tâm ô và $\eta$ là vị trí trên đoạn, bằng 0 tại $\mathbf{e}_1$ và bằng 1 tại $\mathbf{e}_2$. Ô được tô khi tâm của nó cách đoạn thẳng không quá nửa độ dày nét:

$$\lVert \mathbf{g} - \mathbf{e}_1 - \eta \, (\mathbf{e}_2 - \mathbf{e}_1) \rVert \le \frac{\rho \, \omega}{2}$$ {#ct:d2-2}

trong đó $\rho$ là số ô của lưới mịn trên một cạnh điểm ảnh và $\omega$ là độ dày nét trên khung cuối, tính bằng điểm ảnh. Mọi tọa độ trong công thức ({{ct:d2-1}}) và công thức ({{ct:d2-2}}) tính theo ô của lưới mịn. Mỗi điểm ảnh nhận giá trị bằng 255 nhân tỷ lệ ô được tô trong $\rho^2$ ô của nó.

### 2.2.3. Đặt dòng vào khung

Phần nét rộng $\Delta_R$ và cao $\Delta_H$ được co đều hai trục với hệ số:

$$\lambda = \min\left(\frac{R - 2\delta}{\Delta_R}, \frac{H_{\text{nét}}}{\Delta_H}\right)$$ {#ct:d2-3}

trong đó $\delta$ là lề ngang của khung và $H_{\text{nét}}$ là chiều cao tối đa của phần nét sau khi co, bằng $H$ khi không giới hạn. Một hệ số chung cho hai trục giữ nguyên tỷ lệ của chữ. Sau khi co, phần nét cách mép trái $\delta$ điểm ảnh và nằm giữa khung theo chiều dọc.

Công thức ({{ct:d2-3}}) có hai trường hợp. Dòng dài chạm giới hạn chiều rộng trước, nên chữ càng nhỏ khi dòng càng dài. Dòng ngắn chạm giới hạn chiều cao trước, nên phần nét luôn cao bằng $H_{\text{nét}}$ dù dòng có ít chữ. Vì vậy, khi không giới hạn chiều cao phần nét, chữ của dòng ngắn to hơn chữ của dòng dài.

### 2.2.4. Tăng cường dữ liệu

Tăng cường dữ liệu tạo biến thể mới của ảnh huấn luyện mỗi khi ảnh được dùng, còn nhãn giữ nguyên. Puigcerver dùng biến đổi affine ngẫu nhiên cùng phép co và phép giãn ảnh xám khi huấn luyện mô hình nhận dạng dòng chữ viết tay dạng ảnh [@puigcerver2017]. Đề tài dùng bốn nhóm phép biến đổi:

- **Biến dạng đàn hồi:** mỗi điểm ảnh lấy giá trị tại một vị trí dịch đi theo trường dịch chuyển trơn ngẫu nhiên, nên chữ cong và co giãn cục bộ như khác biệt giữa các người viết [@simard2003]. Đề tài tạo trường dịch chuyển bằng cách phóng to một lưới số ngẫu nhiên thô, các nút cách nhau 12 điểm ảnh, rồi nhân với biên độ.
- **Biến đổi affine:** co giãn ngang theo hệ số $s_x$, co giãn dọc theo hệ số $s_y$, nghiêng theo hệ số $\psi$ và dịch dọc $o_y$ điểm ảnh. Điểm ảnh ở hàng $u$, cột $v$ của ảnh mới lấy giá trị của ảnh cũ tại vị trí cho bởi công thức ({{ct:d2-4}}), nội suy song tuyến tính từ bốn điểm ảnh lân cận.
- **Làm dày và làm mỏng nét:** phép giãn lấy giá trị lớn nhất trong ô 3 nhân 3 quanh mỗi điểm ảnh nên làm nét dày lên, còn phép co lấy giá trị nhỏ nhất nên làm nét mỏng đi. Ảnh mới là ảnh cũ trộn với một trong hai ảnh đó theo một hệ số ngẫu nhiên.
- **Độ đậm:** nhân mọi điểm ảnh với cùng một hệ số, rồi cắt về khoảng từ 0 đến 1.

$$v_0 = \frac{v - R/2}{s_x} + \psi \left(u - \frac{H}{2}\right) + \frac{R}{2}, \quad u_0 = \frac{u - H/2}{s_y} + \frac{H}{2} - o_y$$ {#ct:d2-4}

trong đó $u_0$, $v_0$ là hàng và cột trên ảnh cũ. Công thức ({{ct:d2-4}}) co giãn quanh tâm khung, nên nét không bị đẩy lệch về một phía của khung.

### 2.2.5. Lấy khung xương

Khung xương của một vùng nét là tập điểm ảnh rộng một điểm ảnh chạy dọc giữa nét, giữ nguyên hình dạng và các chỗ nối của nét. Thuật toán của Zhang và Suen bóc dần các điểm ảnh ở biên của vùng nét [@zhang1984]. Mỗi vòng gồm hai lượt: lượt đầu xóa các điểm biên phía dưới bên phải cùng các điểm góc phía trên bên trái, lượt sau xóa các điểm biên còn lại. Một điểm chỉ bị xóa khi việc xóa không làm đứt vùng nét, và thuật toán dừng khi không còn điểm nào bị xóa. Kết quả là đường mảnh, nối lại được thành các đoạn thẳng giống nét thu trên điện thoại.

### 2.2.6. Ví dụ minh họa

Ví dụ thứ nhất áp công thức ({{ct:d2-1}}) và công thức ({{ct:d2-2}}) với $\rho = 4$ và $\omega = 1{,}2$, nên ô được tô khi tâm ô cách đoạn thẳng không quá 2,4 ô. Xét một đoạn thẳng nằm ngang. Tâm các hàng ô cách đoạn 0,5 và 1,5 ô thì được tô, cách 2,5 ô thì không, nên mỗi cột có đúng 4 hàng ô được tô. Bảng {{bang:d2-b1}} ghi giá trị của các điểm ảnh theo vị trí của đoạn so với lưới điểm ảnh.

| Vị trí của đoạn thẳng | Số hàng ô được tô trong mỗi điểm ảnh | Giá trị điểm ảnh |
| --- | --- | --- |
| Giữa một hàng điểm ảnh | 4 trong một điểm ảnh | 255 |
| Trên ranh giới hai hàng điểm ảnh | 2 trong mỗi điểm ảnh của hai hàng | 128 và 128 |

Bảng: Một đoạn thẳng nằm ngang dày 1,2 điểm ảnh, vẽ trên lưới mịn gấp 4 lần {#bang:d2-b1}

Bảng {{bang:d2-b1}} cho thấy cùng một nét có thể thành một hàng điểm ảnh đậm hoặc hai hàng điểm ảnh xám, tùy vị trí. Tổng độ đậm của hai trường hợp bằng nhau, nên nét không dày lên hay mỏng đi khi dịch chuyển chưa tới một điểm ảnh.

Ví dụ thứ hai áp công thức ({{ct:d2-3}}) cho hai dòng của cùng một người viết, với $R = 512$, $H = 64$ và $\delta = 8$. Hai dòng cùng có phần nét cao $\Delta_H = 80$ điểm ảnh, dòng dài rộng 1.000 và dòng ngắn rộng 250 điểm ảnh. Bảng {{bang:d2-b2}} ghi kết quả khi không giới hạn và khi giới hạn chiều cao phần nét ở 40 điểm ảnh.

| Dòng | $H_{\text{nét}}$ | $\lambda$ | Chiều cao phần nét sau khi co |
| --- | --- | --- | --- |
| Dài | 64 | 0,496 | 39,7 |
| Ngắn | 64 | 0,800 | 64,0 |
| Dài | 40 | 0,496 | 39,7 |
| Ngắn | 40 | 0,500 | 40,0 |

Bảng: Hệ số co và chiều cao phần nét theo công thức ({{ct:d2-3}}) {#bang:d2-b2}

Theo Bảng {{bang:d2-b2}}, khi không giới hạn, chữ của dòng ngắn to gấp khoảng 1,6 lần chữ của dòng dài. Giới hạn $H_{\text{nét}} = 40$ đưa hai hệ số co về gần nhau và không làm đổi kết quả của dòng dài.

### 2.2.7. Áp dụng trong đề tài

- **Chuẩn hóa ảnh huấn luyện:** mã `training/data.py` đảo ảnh để nét có giá trị lớn, cắt theo khung bao của các điểm ảnh có giá trị trên 40, rồi co theo công thức ({{ct:d2-3}}) với $H = 64$, $R = 512$ và $\delta = 8$, theo mục 3.1.3.
- **Bộ vẽ:** mã `training/ink.py` và `Ink.kt` dùng công thức ({{ct:d2-1}}) và công thức ({{ct:d2-2}}) với $\rho = 4$ và $\omega = 1{,}2$, theo mục 3.2.3. Bộ vẽ trừ thêm $\omega$ ở cả hai tử số của công thức ({{ct:d2-3}}) để mép nét không vượt khung. Đề tài tự viết bộ vẽ để bản Python và bản Kotlin cho cùng một ảnh.
- **Giới hạn chiều cao phần nét:** đề tài đã thử $H_{\text{nét}} = 40$ để giảm CER của dòng ngắn, theo mục 4.7. Cách này giúp khi dùng riêng nhưng không giúp khi kết hợp với ảnh vẽ lại, nên cấu hình cuối không dùng, theo mục 4.4.
- **Mức tăng cường:** $s_x$ từ 0,88 đến 1,02, $s_y$ từ 0,85 đến 1,15, $\psi$ trong khoảng $[-0{,}25; 0{,}25]$ và $o_y$ trong khoảng $[-3; 3]$, mỗi giá trị lấy ngẫu nhiên đều. Hệ số $s_x$ không vượt 1,02, vì phóng ngang nhiều hơn làm nét rơi khỏi khung trong khi nhãn vẫn đủ ký tự, theo Chương 4. Hệ số trộn dày mỏng nằm trong khoảng $[-0{,}5; 1]$, giá trị âm làm mỏng và giá trị dương làm dày. Hệ số độ đậm từ 0,5 đến 2,5, chỉ dùng ở các lần chạy có ảnh vẽ lại. Biến dạng đàn hồi biên độ 2 điểm ảnh chỉ dùng ở lần chạy `m1_rr_el`, theo Chương 4. Lần chạy này kém hơn trên cả tập kiểm định và nét viết thật, nên cấu hình cuối không dùng biến dạng đàn hồi, theo Chương 4.
- **Vẽ lại ảnh huấn luyện:** mã `training/rerender.py` lấy khung xương của các điểm ảnh có giá trị trên 80 bằng thuật toán ở mục 2.2.5, nối mỗi cặp điểm ảnh kề nhau thành một đoạn thẳng, rồi vẽ lại bằng bộ vẽ ở mục 2.2.2 với $\omega$ bằng 0,8; 1,2 và 1,6. Từ lần chạy `m1_rr`, mỗi lần dùng một dòng, vòng huấn luyện chọn ngẫu nhiên một trong bốn ảnh của dòng đó, gồm ảnh gốc và ba ảnh vẽ lại, theo Chương 4. Cấu hình cuối dùng cách này.

### 2.2.8. Hạn chế

- **Khung xương sai lệch:** khung xương làm đứt các nét mảnh và sinh nhánh thừa ở chỗ nét giao nhau. Ảnh vẽ lại vì vậy chỉ gần đúng với ảnh vẽ từ nét thật.
- **Một độ dày cho mọi nét:** bộ vẽ không dùng lực nhấn và tốc độ viết, trong khi nét trong ảnh VNOnDB dày mỏng khác nhau.
- **Cỡ chữ phụ thuộc độ dài dòng:** theo Bảng {{bang:d2-b2}}, dòng ngắn có chữ to hơn dòng dài. Giới hạn $H_{\text{nét}}$ thu hẹp chênh lệch này nhưng làm dòng ngắn có ít điểm ảnh hơn.
- **Mức tăng cường chọn bằng tay:** các khoảng giá trị ở mục 2.2.7 chưa được dò có hệ thống.
- **Lệch giữa hai nguồn ảnh vẫn lớn:** CER của mô hình `m1_v2` tăng từ 12,12% trên ảnh kiểm định gốc lên 30,82% trên ảnh vẽ lại, theo Chương 4. Trên nét viết thật, CER còn cao hơn, theo Chương 4.

## 2.3. Mạng nơ-ron tích chập hai chiều

### 2.3.1. Bài toán

Đầu vào là ảnh xám $\mathbf{X}$ của một dòng, cao $H$ và rộng $R$ điểm ảnh. Đầu ra cần có là chuỗi $T$ véc-tơ $\mathbf{z}_t$, mỗi véc-tơ mô tả một dải cột của ảnh theo thứ tự từ trái sang phải. Lớp BiLSTM chỉ nhận chuỗi, nên mô hình cần bước chuyển từ ảnh sang chuỗi này.

Mạng kết nối đầy đủ không phù hợp với ảnh. Với khung rộng 512, cao 64 điểm ảnh, một lớp 128 ô đã cần 4.194.304 trọng số. Mạng này cũng phải học lại cùng một nét ở từng vị trí trên dòng.

### 2.3.2. Phép tích chập

Một bộ lọc là một ma trận trọng số nhỏ, trượt lần lượt qua mọi vị trí của ảnh [@lecun1998]. Với bộ lọc kích thước 3 nhân 3, đầu ra tại mỗi vị trí là:

$$y_{u,v} = \sum_{u'=-1}^{1} \sum_{v'=-1}^{1} \kappa_{u',v'} \, x_{u+u', v+v'}$$ {#ct:d3-1}

trong đó $x_{u,v}$ và $y_{u,v}$ là giá trị tại hàng $u$, cột $v$ của đầu vào và đầu ra, $\kappa_{u',v'}$ là trọng số của bộ lọc. Bộ lọc có giá trị lớn tại những nơi ảnh giống mẫu của nó, ví dụ một cạnh dọc hoặc một đoạn cong.

Phép tích chập có hai tính chất. Mỗi đầu ra chỉ nhìn một vùng nhỏ của ảnh, và cùng một bộ lọc được dùng ở mọi vị trí. Nhờ vậy, số tham số không phụ thuộc vào kích thước ảnh:

$$\text{số trọng số} = e^2 \, F_{\text{vào}} \, F$$ {#ct:d3-2}

trong đó $e$ là kích thước bộ lọc, $F_{\text{vào}}$ là số kênh đầu vào và $F$ là số bộ lọc của lớp. Công thức ({{ct:d3-2}}) tính cho lớp không có độ lệch.

### 2.3.3. Max pooling

Max pooling chia đầu ra thành các ô nhỏ và giữ giá trị lớn nhất của mỗi ô [@lecun1998]. Phép này giảm kích thước đầu ra, nên giảm khối lượng tính toán của các lớp sau. Nó cũng làm đầu ra ít nhạy hơn với các dịch chuyển nhỏ của nét.

### 2.3.4. Chuẩn hóa theo lô

Chuẩn hóa theo lô đưa đầu ra của một lớp về trung bình 0 và phương sai 1 trên từng lô, rồi học lại một độ lệch và một hệ số co [@ioffe2015]. Trong lúc nhận dạng, lớp này dùng các thống kê đã tích lũy khi huấn luyện, nên kết quả của một dòng không phụ thuộc vào các dòng khác. Lớp này giúp huấn luyện ổn định hơn với tốc độ học lớn.

### 2.3.5. Từ ảnh thành chuỗi

Sau các lớp tích chập, đầu ra vẫn là một ảnh đặc trưng có chiều cao nhỏ. Mỗi cột của ảnh đặc trưng được ghép thành một véc-tơ, theo thứ tự từ trái sang phải [@shi2015]. Puigcerver cho thấy chỉ cần lớp hồi quy một chiều chạy theo chiều ngang sau bước ghép này, không cần lớp hồi quy đa chiều [@puigcerver2017].

### 2.3.6. Vùng nhìn

Vùng nhìn là phần ảnh gốc ảnh hưởng tới một giá trị đầu ra. Theo một chiều, vùng nhìn tăng dần qua từng lớp:

$$v_\ell = v_{\ell-1} + (e_\ell - 1) \, g_{\ell-1}, \quad g_\ell = g_{\ell-1} \, \tau_\ell, \quad v_0 = g_0 = 1$$ {#ct:d3-3}

trong đó $v_\ell$ là vùng nhìn sau lớp thứ $\ell$, $g_\ell$ là bước nhảy tích lũy, $e_\ell$ là kích thước cửa sổ và $\tau_\ell$ là bước nhảy của lớp đó. Công thức ({{ct:d3-3}}) cho thấy lớp đặt sau max pooling có vùng nhìn tăng nhanh hơn.

### 2.3.7. Ví dụ minh họa

Ví dụ thứ nhất áp công thức ({{ct:d3-1}}) cho bộ lọc phát hiện cạnh dọc, có cột trái bằng $-1$, cột giữa bằng 0 và cột phải bằng 1. Trên vùng 3 nhân 3 có cột phải bằng 255 và hai cột còn lại bằng 0, đầu ra bằng $3 \times 255 = 765$. Trên vùng có mọi giá trị bằng nhau, đầu ra bằng 0.

Ví dụ thứ hai theo dõi kích thước qua CNN 2D của mô hình M1, với đầu vào cao 64 và rộng 512. Bảng {{bang:d3-b1}} ghi kết quả, số trọng số tính theo công thức ({{ct:d3-2}}) với $e = 3$.

| Khối | Số bộ lọc | Max pooling (cao, rộng) | Đầu ra (cao, rộng, kênh) | Số trọng số |
| --- | --- | --- | --- | --- |
| 1 | 32 | 2, 2 | 32, 256, 32 | 288 |
| 2 | 64 | 2, 1 | 16, 256, 64 | 18.432 |
| 3 | 128 | 2, 1 | 8, 256, 128 | 73.728 |
| 4 | 128 | 2, 1 | 4, 256, 128 | 147.456 |
| Tổng | | | | 239.904 |

Bảng: Kích thước và số trọng số qua bốn khối của mô hình M1 {#bang:d3-b1}

Đầu ra của khối 4 có 256 cột, mỗi cột gồm $4 \times 128 = 512$ giá trị. Một lớp kết nối đầy đủ giảm mỗi cột xuống 128 chiều, tạo thành $\mathbf{z}_t$ với $T = 256$.

Ví dụ thứ ba áp công thức ({{ct:d3-3}}) cho từng khối. Bảng {{bang:d3-b2}} ghi vùng nhìn sau mỗi khối, tính bằng điểm ảnh trên khung đầu vào.

| Sau khối | Theo chiều cao | Theo chiều rộng |
| --- | --- | --- |
| 1 | 4 | 4 |
| 2 | 10 | 8 |
| 3 | 22 | 12 |
| 4 | 46 | 16 |

Bảng: Vùng nhìn sau mỗi khối của mô hình M1 {#bang:d3-b2}

### 2.3.8. Áp dụng trong đề tài

- **Cấu trúc:** M0 và M1 có bốn khối, mỗi khối gồm lớp tích chập kích thước 3, chuẩn hóa theo lô, hàm ReLU và max pooling, theo mục 3.2.4. Lớp tích chập không có độ lệch, vì chuẩn hóa theo lô đã có độ lệch riêng.
- **Giảm chiều cao 16 lần, chiều rộng 2 lần:** chiều rộng chỉ giảm ở khối đầu, để còn 256 bước thời gian. Điều kiện độ dài của CTC ở mục 2.5.5, cần số bước đủ lớn cho dòng dài nhất.
- **Vùng nhìn:** theo Bảng {{bang:d3-b2}}, mỗi bước nhìn 46 điểm ảnh theo chiều cao, đủ bao phần lớn nét chữ. Chiều rộng chỉ 16 điểm ảnh, nên ngữ cảnh ngang do BiLSTM đảm nhiệm.
- **Trên điện thoại:** các lớp này chuyển sang toán tử có sẵn của LiteRT. Chuẩn hóa theo lô được gộp vào phép tính của lớp tích chập, nên không tốn thêm thời gian khi chạy.

### 2.3.9. Hạn chế

- **Nhạy với cỡ chữ:** bộ lọc có kích thước cố định, nên chữ lớn hơn nhiều so với lúc huấn luyện sẽ khó nhận ra. Vì vậy mọi dòng phải được đưa về cỡ chữ gần nhau, theo mục 2.2.
- **Khung cố định:** đầu vào có chiều rộng cố định, nên dòng dài bị co nhỏ. Dòng 158 ký tự chỉ còn khoảng 3 điểm ảnh cho mỗi ký tự.
- **Mất chi tiết nhỏ:** max pooling và ảnh độ phân giải thấp làm mất các chi tiết nhỏ như dấu chấm, dấu phẩy và một số dấu phụ.
- **Giữ cả nét không cần thiết:** chiều cao đặc trưng còn 4 hàng, nên một phần chi tiết theo chiều dọc đã bị gộp trước khi vào BiLSTM.

## 2.4. Mạng hồi quy, LSTM và BiLSTM

### 2.4.1. Bài toán

Đầu vào của bước này là chuỗi $\mathbf{z}_1, \ldots, \mathbf{z}_T$, mỗi véc-tơ mô tả một đoạn ngắn của nét viết. Đầu ra cần có là một véc-tơ $\mathbf{h}_t$ cho mỗi bước, đủ thông tin để lớp đầu ra quyết định nhãn của bước đó.

Một đoạn nét ngắn thường không đủ để biết đó là chữ gì. Nét móc có thể là phần đầu của "u" hay của "ư", và chỉ nhìn tiếp mới biết có dấu móc hay không. Với tiếng Việt, dấu thanh và dấu phụ thường được viết sau phần thân chữ, có khi sau cả một âm tiết hay một câu. Vì vậy véc-tơ $\mathbf{h}_t$ phải mang thông tin của cả những bước trước và những bước sau bước $t$.

### 2.4.2. Mạng hồi quy

Mạng hồi quy xử lý chuỗi lần lượt từng bước, và đưa trạng thái của bước trước vào bước sau:

$$\mathbf{h}_t = \tanh\big(\mathbf{V}_h [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_h\big)$$ {#ct:d4-1}

trong đó $[\mathbf{h}_{t-1}; \mathbf{z}_t]$ là véc-tơ ghép từ trạng thái trước và đầu vào hiện tại. Cùng một bộ trọng số được dùng ở mọi bước, nên mạng xử lý được chuỗi dài bất kỳ.

Khi huấn luyện, đạo hàm truyền ngược qua nhiều bước sẽ bị nhân liên tiếp với cùng một ma trận và với đạo hàm của $\tanh$. Qua vài chục bước, đạo hàm thường nhỏ dần về 0, nên mạng hồi quy đơn giản khó học quan hệ giữa hai bước cách xa nhau [@hochreiter1997].

### 2.4.3. LSTM

LSTM thêm một ô nhớ $\mathbf{C}_t$ và ba cổng điều khiển việc đọc, ghi và xóa ô nhớ [@hochreiter1997]. Cổng quên được bổ sung sau, cho phép mạng chủ động xóa thông tin cũ [@gers2000]. Mỗi cổng là một véc-tơ giá trị từ 0 đến 1, tính từ trạng thái trước và đầu vào hiện tại:

$$\begin{aligned} \mathbf{f}_t &= \sigma\big(\mathbf{V}_f [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_f\big) \\ \mathbf{i}_t &= \sigma\big(\mathbf{V}_i [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_i\big) \\ \mathbf{o}_t &= \sigma\big(\mathbf{V}_o [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_o\big) \end{aligned}$$ {#ct:d4-2}

trong đó $\mathbf{f}_t$ là cổng quên, $\mathbf{i}_t$ là cổng ghi và $\mathbf{o}_t$ là cổng ra. Giá trị ứng viên để ghi vào ô nhớ được tính theo cùng cách nhưng dùng $\tanh$:

$$\tilde{\mathbf{C}}_t = \tanh\big(\mathbf{V}_C [\mathbf{h}_{t-1}; \mathbf{z}_t] + \mathbf{b}_C\big)$$ {#ct:d4-3}

Ô nhớ mới giữ lại một phần ô nhớ cũ theo cổng quên, cộng thêm một phần giá trị ứng viên theo cổng ghi:

$$\mathbf{C}_t = \mathbf{f}_t \odot \mathbf{C}_{t-1} + \mathbf{i}_t \odot \tilde{\mathbf{C}}_t$$ {#ct:d4-4}

Trạng thái ẩn là phần ô nhớ mà cổng ra cho phép đi ra ngoài:

$$\mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{C}_t)$$ {#ct:d4-5}

Điểm mấu chốt nằm ở công thức ({{ct:d4-4}}): ô nhớ đi từ bước này sang bước sau qua phép cộng, không qua phép nhân ma trận. Khi cổng quên gần 1, thông tin và đạo hàm đi qua nhiều bước mà không bị thu nhỏ nhanh, nên LSTM học được quan hệ xa hơn nhiều so với mạng hồi quy đơn giản.

### 2.4.4. BiLSTM

LSTM ở mục 2.4.3 chỉ đọc chuỗi theo một chiều, nên $\mathbf{h}_t$ chỉ biết các bước từ 1 đến $t$. Mạng hồi quy hai chiều chạy thêm một mạng thứ hai từ bước $T$ ngược về bước 1, rồi ghép trạng thái của hai chiều tại mỗi bước [@schuster1997]:

$$\mathbf{h}_t = \big[\overrightarrow{\mathbf{h}}_t ; \overleftarrow{\mathbf{h}}_t\big]$$ {#ct:d4-6}

trong đó $\overrightarrow{\mathbf{h}}_t$ là trạng thái của chiều xuôi sau khi đọc các bước từ 1 đến $t$, còn $\overleftarrow{\mathbf{h}}_t$ là trạng thái của chiều ngược sau khi đọc các bước từ $T$ về $t$. Hai chiều có bộ trọng số riêng. Véc-tơ ghép có $2d$ chiều và là đầu vào của lớp kế tiếp.

Nhiều lớp BiLSTM có thể xếp chồng lên nhau: chuỗi $\mathbf{h}_t$ của lớp dưới là chuỗi $\mathbf{z}_t$ của lớp trên. Hệ thống nhận dạng chữ viết tay dạng nét của Google dùng nhiều lớp BiLSTM xếp chồng, huấn luyện bằng CTC [@carbune2019].

### 2.4.5. Số tham số

Mỗi cổng và giá trị ứng viên có một ma trận trọng số kích thước $d \times (d + d_{\text{vào}})$ và một véc-tơ độ lệch $d$ phần tử. Một chiều LSTM có bốn bộ như vậy, nên số tham số là:

$$4d\,(d + d_{\text{vào}} + 1)$$ {#ct:d4-7}

Một lớp BiLSTM có gấp đôi số này vì có hai chiều. Số tham số không phụ thuộc vào độ dài chuỗi $T$, nhưng thời gian chạy thì tăng theo $T$.

### 2.4.6. Ví dụ minh họa

Ví dụ đầu tính một bước của LSTM có một ô nhớ, để thấy vai trò của từng cổng. Giả sử ô nhớ trước là $C_{t-1} = 0{,}8$, các cổng có giá trị $f_t = 0{,}9$, $i_t = 0{,}1$, $o_t = 0{,}6$, và giá trị ứng viên là $\tilde{C}_t = 0{,}5$. Theo công thức ({{ct:d4-4}}) và ({{ct:d4-5}}):

$$\begin{aligned} C_t &= 0{,}9 \times 0{,}8 + 0{,}1 \times 0{,}5 = 0{,}77 \\ h_t &= 0{,}6 \times \tanh(0{,}77) \approx 0{,}6 \times 0{,}647 \approx 0{,}388 \end{aligned}$$ {#ct:d4-8}

Cổng quên lớn và cổng ghi nhỏ, nên ô nhớ gần như giữ nguyên giá trị cũ. Nếu các cổng giữ nguyên như vậy và giá trị ứng viên bằng 0 trong 10 bước, ô nhớ còn $0{,}8 \times 0{,}9^{10} \approx 0{,}279$. Thông tin vẫn còn sau 10 bước. Với mạng hồi quy đơn giản, không có đường cộng như công thức ({{ct:d4-4}}) để giữ thông tin này.

Ví dụ thứ hai áp công thức ({{ct:d4-7}}) cho hai lớp BiLSTM của mô hình M1, mỗi chiều có $d = 128$ ô. Lớp thứ nhất nhận đầu ra 128 chiều của lớp kết nối đầy đủ sau CNN 2D. Lớp thứ hai nhận véc-tơ ghép $2 \times 128 = 256$ chiều của lớp bên dưới. Bảng {{bang:d4-b1}} ghi kết quả.

| Lớp | $d_{\text{vào}}$ | Tham số một chiều | Tham số hai chiều |
| --- | --- | --- | --- |
| BiLSTM 1 | 128 | 131.584 | 263.168 |
| BiLSTM 2 | 256 | 197.120 | 394.240 |
| Tổng | | | 657.408 |

Bảng: Số tham số của hai lớp BiLSTM trong mô hình M1 {#bang:d4-b1}

Hai lớp BiLSTM chiếm khoảng 0,66 triệu trong 1,00 triệu tham số của M1 ước tính trong mục 3.2.4. Phần còn lại thuộc CNN 2D, lớp kết nối đầy đủ và lớp đầu ra.

### 2.4.7. Áp dụng trong đề tài

- **Vì sao cần hai chiều:** BiLSTM đọc ảnh theo các cột từ trái sang phải, mỗi bước ứng với một dải cột. Một ký tự trải trên nhiều bước, và các ký tự bên phải giúp phân biệt những nét giống nhau. Chiều ngược mang thông tin bên phải về bước đang xét, nên đề tài dùng BiLSTM thay cho LSTM một chiều. Phép so sánh M0 với M1 đo lợi ích này.
- **Cấu hình:** mô hình cơ sở M0 không có BiLSTM, mô hình đề xuất M1 có 2 lớp BiLSTM 128 ô sau CNN 2D, theo mục 3.2.4. Cấu hình huấn luyện khởi đầu dùng dropout 0,5 sau mỗi lớp LSTM [@carbune2019].
- **Chọn LSTM thay cho GRU:** công cụ chuyển đổi LiteRT có hướng dẫn chuyển đổi sẵn cho lớp LSTM của Keras. Chi tiết thuộc Chương 5 (dự kiến).
- **Kết quả tạm thời khi đang viết:** chiều ngược cần toàn bộ chuỗi, nên ứng dụng chạy lại cả dòng sau mỗi lần người dùng dừng bút, thay vì cập nhật từng bước.

### 2.4.8. Hạn chế

- **Không xử lý dần theo dòng chảy:** BiLSTM chỉ cho kết quả khi đã có đủ chuỗi. Mỗi lần nhận dạng lại phải chạy từ đầu, nên chi phí tăng theo độ dài dòng.
- **Tính tuần tự:** bước $t$ phải chờ bước $t - 1$ xong, nên khó tận dụng tính toán song song. Đây là lý do CNN 2D giảm chiều rộng ảnh 2 lần trước khi vào BiLSTM, còn 256 bước.
- **Quan hệ rất xa vẫn khó:** LSTM giữ thông tin tốt hơn mạng hồi quy đơn giản nhưng không phải vô hạn. Các bước ở đầu dòng và cuối dòng cách nhau đến 256 bước, nên ngữ cảnh xa chủ yếu do n-gram bổ sung.
- **Số tham số tăng nhanh theo số ô:** theo công thức ({{ct:d4-7}}), số tham số tăng gần theo bình phương của $d$. Tăng số ô để tăng độ chính xác sẽ nhanh chóng chạm giới hạn dung lượng và độ trễ trên điện thoại.

## 2.5. Hàm mất mát CTC

### 2.5.1. Bài toán

Đầu vào của mô hình là ảnh $\mathbf{X}$ của một dòng. Sau khi mạng nơ-ron tích chập hai chiều (CNN 2D) giảm kích thước ảnh, lớp BiLSTM cho ra $T$ bước thời gian. Đầu ra cần có là chuỗi ký tự $\mathbf{l} = (l_1, \ldots, l_U)$ của dòng đó.

Bộ dữ liệu HANDS-VNOnDB (VNOnDB) chỉ cho biết văn bản của cả dòng. Dữ liệu không ghi bước thời gian nào ứng với ký tự nào, nên không thể huấn luyện bằng cách phân loại từng bước. Độ dài cũng khác nhau: $T$ thường lớn hơn $U$ nhiều lần, và một ký tự kéo dài qua nhiều bước.

CTC giải bài toán này bằng cách tính xác suất của chuỗi đích $\mathbf{l}$ khi cộng dồn trên mọi cách căn chỉnh có thể [@graves2006]. Hàm mất mát chỉ cần cặp dữ liệu gồm chuỗi đặc trưng và văn bản, không cần biết vị trí của từng ký tự.

### 2.5.2. Xác suất của một đường căn chỉnh

Tại mỗi bước $t$, lớp softmax cho ra phân bố xác suất $p_t(k)$ trên tập nhãn $\mathcal{A}'$. Tập này gồm 160 ký tự của bảng ký tự $\mathcal{A}$ cộng thêm nhãn trống $\epsilon$, nghĩa là "không phát ra ký tự nào ở bước này".

Một đường căn chỉnh $\boldsymbol{\pi} = (\pi_1, \ldots, \pi_T)$ chọn một nhãn cho mỗi bước. CTC giả định các bước độc lập với nhau khi đã biết $\mathbf{X}$, nên xác suất của một đường là tích các xác suất từng bước:

$$p(\boldsymbol{\pi} \mid \mathbf{X}) = \prod_{t=1}^{T} p_t(\pi_t)$$ {#ct:d5-1}

trong đó $\pi_t$ là nhãn của đường tại bước $t$.

### 2.5.3. Phép gộp và hàm mất mát

Phép gộp $\mathcal{B}$ biến một đường căn chỉnh thành chuỗi ký tự qua hai bước: bỏ các nhãn lặp liền nhau, rồi bỏ nhãn trống. Ví dụ, với $T = 6$, đường $(m, m, \epsilon, a, a, \epsilon)$ gộp thành chuỗi "ma".

Nhãn trống cho phép mô hình viết hai ký tự giống nhau đứng liền nhau. Đường $(o, o, \epsilon, o)$ gộp thành "oo", còn đường $(o, o, o, o)$ chỉ gộp thành "o".

Nhiều đường khác nhau gộp về cùng một chuỗi. Xác suất của chuỗi đích là tổng xác suất của tất cả các đường đó:

$$p(\mathbf{l} \mid \mathbf{X}) = \sum_{\boldsymbol{\pi} \in \mathcal{B}^{-1}(\mathbf{l})} p(\boldsymbol{\pi} \mid \mathbf{X})$$ {#ct:d5-2}

trong đó $\mathcal{B}^{-1}(\mathbf{l})$ là tập mọi đường dài $T$ gộp thành $\mathbf{l}$. Hàm mất mát của một dòng là log âm của xác suất này:

$$\mathcal{L}_{\text{CTC}} = -\ln p(\mathbf{l} \mid \mathbf{X})$$ {#ct:d5-3}

Huấn luyện là giảm $\mathcal{L}_{\text{CTC}}$ trung bình trên tập huấn luyện bằng lan truyền ngược.

### 2.5.4. Tính tổng bằng quy hoạch động

Số đường trong $\mathcal{B}^{-1}(\mathbf{l})$ tăng theo hàm mũ của $T$, nên không thể cộng trực tiếp theo công thức ({{ct:d5-2}}). CTC dùng quy hoạch động trên chuỗi nhãn mở rộng $\mathbf{l}'$, tạo bằng cách chèn nhãn trống vào đầu, cuối và giữa mọi cặp ký tự của $\mathbf{l}$. Chuỗi $\mathbf{l}'$ dài $2U + 1$, với các vị trí lẻ là nhãn trống [@graves2006].

Biến tiến $\phi_t(j)$ là tổng xác suất của các đoạn đường dài $t$ dừng ở vị trí $j$ của $\mathbf{l}'$. Ở bước đầu, đường chỉ có thể bắt đầu bằng nhãn trống hoặc ký tự đầu tiên: $\phi_1(1) = p_1(\epsilon)$, $\phi_1(2) = p_1(l_1)$, các vị trí khác bằng 0. Từ bước thứ hai trở đi:

$$\phi_t(j) = \begin{cases} \big(\phi_{t-1}(j) + \phi_{t-1}(j-1)\big)\, p_t(l'_j) & \text{nếu } l'_j = \epsilon \text{ hoặc } l'_j = l'_{j-2} \\ \big(\phi_{t-1}(j) + \phi_{t-1}(j-1) + \phi_{t-1}(j-2)\big)\, p_t(l'_j) & \text{trường hợp còn lại} \end{cases}$$ {#ct:d5-4}

trong đó $l'_j$ là nhãn ở vị trí $j$ của $\mathbf{l}'$. Trường hợp thứ nhất cấm nhảy qua một nhãn trống khi hai ký tự liền nhau giống nhau, vì nếu nhảy thì phép gộp sẽ nhập hai ký tự làm một.

Đường hợp lệ phải kết thúc ở ký tự cuối hoặc ở nhãn trống cuối cùng, nên:

$$p(\mathbf{l} \mid \mathbf{X}) = \phi_T(2U + 1) + \phi_T(2U)$$ {#ct:d5-5}

Cách tính này tốn thời gian tỷ lệ với $T \cdot U$ thay vì tăng theo hàm mũ. Đạo hàm của $\mathcal{L}_{\text{CTC}}$ được tính bằng biến lùi theo cùng cách, đi từ bước $T$ về bước 1. Khi cài đặt, các phép tính làm trong miền logarit để tránh tràn số dưới khi nhân nhiều xác suất nhỏ.

### 2.5.5. Điều kiện về độ dài

Mỗi ký tự cần ít nhất một bước, và mỗi cặp ký tự giống nhau đứng liền nhau cần thêm một nhãn trống ở giữa. Vì vậy chuỗi đích chỉ có đường căn chỉnh khi:

$$T \ge U + r$$ {#ct:d5-6}

trong đó $r$ là số cặp ký tự giống nhau đứng liền nhau trong $\mathbf{l}$. Dòng vi phạm công thức ({{ct:d5-6}}) có xác suất bằng 0 và mất mát vô cùng lớn.

### 2.5.6. Giải mã đơn giản

Do các bước độc lập theo công thức ({{ct:d5-1}}), đường có xác suất lớn nhất tìm được bằng cách chọn nhãn có xác suất lớn nhất ở từng bước. Cách giải mã nhanh nhất là gộp đường đó:

$$\hat{\mathbf{l}} = \mathcal{B}\Big(\big(\arg\max_{k} p_1(k), \ldots, \arg\max_{k} p_T(k)\big)\Big)$$ {#ct:d5-7}

Cách này chỉ xét một đường, trong khi xác suất của chuỗi là tổng trên nhiều đường, nên không chắc tìm ra chuỗi có xác suất lớn nhất. Beam search kết hợp mô hình ngôn ngữ xử lý điểm yếu này, xem mục 2.6.

### 2.5.7. Ví dụ minh họa

Ví dụ dùng chuỗi đích một ký tự "a", tức $U = 1$, với $T = 3$ bước. Để tính được bằng tay, giả sử mô hình chỉ gán xác suất cho hai nhãn "a" và $\epsilon$. Bảng {{bang:d5-b1}} cho xác suất ở từng bước.

| Bước $t$ | $p_t(a)$ | $p_t(\epsilon)$ |
| --- | --- | --- |
| 1 | 0,6 | 0,4 |
| 2 | 0,6 | 0,4 |
| 3 | 0,3 | 0,7 |

Bảng: Xác suất đầu ra giả định trong ví dụ {#bang:d5-b1}

Có 8 đường dài 3 trên hai nhãn này. Sáu đường gộp thành "a", được liệt kê trong Bảng {{bang:d5-b2}} cùng xác suất tính theo công thức ({{ct:d5-1}}). Hai đường còn lại không gộp thành "a": đường $(a, \epsilon, a)$ gộp thành "aa", đường $(\epsilon, \epsilon, \epsilon)$ gộp thành chuỗi rỗng.

| Đường | Cách tính | Xác suất |
| --- | --- | --- |
| $(a, a, a)$ | $0{,}6 \times 0{,}6 \times 0{,}3$ | 0,108 |
| $(a, a, \epsilon)$ | $0{,}6 \times 0{,}6 \times 0{,}7$ | 0,252 |
| $(a, \epsilon, \epsilon)$ | $0{,}6 \times 0{,}4 \times 0{,}7$ | 0,168 |
| $(\epsilon, a, a)$ | $0{,}4 \times 0{,}6 \times 0{,}3$ | 0,072 |
| $(\epsilon, \epsilon, a)$ | $0{,}4 \times 0{,}4 \times 0{,}3$ | 0,048 |
| $(\epsilon, a, \epsilon)$ | $0{,}4 \times 0{,}6 \times 0{,}7$ | 0,168 |
| Tổng | | 0,816 |

Bảng: Các đường căn chỉnh gộp thành "a" {#bang:d5-b2}

Theo công thức ({{ct:d5-2}}), $p(\text{"a"} \mid \mathbf{X}) = 0{,}816$. Theo công thức ({{ct:d5-3}}), mất mát bằng $-\ln 0{,}816 \approx 0{,}203$. Kiểm tra lại: hai đường bị loại có xác suất 0,072 và 0,112, cộng với 0,816 được đúng 1.

Quy hoạch động cho cùng kết quả mà không phải liệt kê đường. Chuỗi mở rộng là $\mathbf{l}' = (\epsilon, a, \epsilon)$. Bảng {{bang:d5-b3}} ghi giá trị biến tiến tính theo công thức ({{ct:d5-4}}).

| Bước $t$ | $j = 1$, nhãn $\epsilon$ | $j = 2$, nhãn a | $j = 3$, nhãn $\epsilon$ |
| --- | --- | --- | --- |
| 1 | 0,4 | 0,6 | 0 |
| 2 | $0{,}4 \times 0{,}4 = 0{,}16$ | $(0{,}6 + 0{,}4) \times 0{,}6 = 0{,}6$ | $(0 + 0{,}6) \times 0{,}4 = 0{,}24$ |
| 3 | $0{,}16 \times 0{,}7 = 0{,}112$ | $(0{,}6 + 0{,}16) \times 0{,}3 = 0{,}228$ | $(0{,}24 + 0{,}6) \times 0{,}7 = 0{,}588$ |

Bảng: Biến tiến $\phi_t(j)$ trong ví dụ {#bang:d5-b3}

Theo công thức ({{ct:d5-5}}), $p = \phi_3(3) + \phi_3(2) = 0{,}588 + 0{,}228 = 0{,}816$, trùng với tổng ở Bảng {{bang:d5-b2}}.

Ví dụ cũng cho thấy giới hạn của giải mã theo công thức ({{ct:d5-7}}). Đường tốt nhất là $(a, a, \epsilon)$ với xác suất 0,252, gộp đúng thành "a". Tuy vậy đường này chỉ chiếm chưa tới một phần ba xác suất 0,816 của chuỗi "a". Khi các ứng viên gần nhau, chuỗi có tổng xác suất lớn nhất có thể khác với chuỗi gộp từ đường tốt nhất.

### 2.5.8. Áp dụng trong đề tài

- **Tập nhãn:** lớp đầu ra có 161 nhãn, gồm 160 ký tự có ở tập huấn luyện hoặc tập kiểm định và nhãn trống. Đây là con số 161 trong mục 3.2.4.
- **Lý do chọn CTC:** VNOnDB chỉ có văn bản theo dòng, không có nhãn căn chỉnh theo từng cột ảnh, đúng trường hợp CTC được thiết kế cho [@graves2006]. Hệ thống nhận dạng chữ viết tay dạng nét của Google cũng huấn luyện BiLSTM bằng CTC [@carbune2019].
- **Điều kiện độ dài:** CNN 2D giảm chiều rộng ảnh 2 lần, nên $T = 256$. Giá trị lớn nhất của $U + r$ đo được là 159 trên tập huấn luyện và 110 trên tập kiểm định, nên công thức ({{ct:d5-6}}) luôn thỏa. Nếu đổi cỡ khung ảnh hoặc mức giảm chiều rộng thì phải kiểm tra lại, vì dòng vi phạm làm hỏng cả lô huấn luyện.
- **Cài đặt:** dùng hàm CTC có sẵn của TensorFlow, chỉ định vị trí nhãn trống và độ dài thật của từng dòng sau khi giảm độ dài, không dùng độ dài đã đệm. Lựa chọn cụ thể ghi ở mục 3.2.
- **Giải mã:** giải mã theo công thức ({{ct:d5-7}}) dùng để đo tỷ lệ lỗi ký tự (CER) trên tập kiểm định trong lúc huấn luyện, vì nhanh và không cần mô hình ngôn ngữ. Bản đưa lên điện thoại dùng beam search kết hợp n-gram âm tiết.

### 2.5.9. Hạn chế

- **Giả định độc lập giữa các bước:** công thức ({{ct:d5-1}}) coi các bước độc lập khi đã biết $\mathbf{X}$, nên CTC không tự học quan hệ giữa các ký tự đầu ra. Việc chọn giữa "ma", "má", "mà" theo ngữ cảnh phải nhờ mô hình ngôn ngữ ở bước giải mã.
- **Căn chỉnh đơn điệu:** thứ tự ký tự đầu ra phải theo thứ tự các cột ảnh từ trái sang phải. Trên ảnh, dấu thanh và dấu phụ nằm đúng chỗ dù được viết trễ, nên ràng buộc này phù hợp với đầu vào. Khi chữ nghiêng nhiều, một cột ảnh có thể chứa phần của hai ký tự, và đây là nguồn lỗi cần phân tích.
- **Ràng buộc độ dài:** công thức ({{ct:d5-6}}) đặt giới hạn cho mức giảm độ dài chuỗi. Giảm mạnh hơn để chạy nhanh hơn có thể làm một số dòng dài vi phạm điều kiện.
- **Xác suất quá tự tin:** đầu ra CTC thường tập trung gần hết xác suất vào một nhãn ở mỗi bước, và mô hình quá tự tin trên chính dữ liệu đã học. Vì vậy trọng số của mô hình ngôn ngữ phải chỉnh trên dữ liệu khác với tập huấn luyện [@carbune2019].

## 2.6. Beam search và mô hình ngôn ngữ n-gram

### 2.6.1. Bài toán

Đầu vào của bước giải mã là ma trận xác suất $p_t(k)$ do mô hình cho ra, với $T$ bước thời gian và 161 nhãn. Đầu ra cần có là chuỗi ký tự $\hat{\mathbf{l}}$ hợp lý nhất cho dòng đó.

Giải mã đơn giản ở mục 2.5.6, có hai điểm yếu. Thứ nhất, nó chỉ xét một đường căn chỉnh, trong khi xác suất của một chuỗi là tổng trên nhiều đường. Thứ hai, CTC coi các bước độc lập với nhau, nên mô hình không biết âm tiết nào hay đi cùng âm tiết nào. Với tiếng Việt, điểm yếu thứ hai rõ nhất ở dấu thanh: nét viết của "ma", "má", "mà" có thể gần giống nhau, và chỉ ngữ cảnh mới phân biệt được.

Bài toán của bước giải mã vì vậy là tìm chuỗi vừa khớp với nét viết, vừa hợp với cách dùng tiếng Việt, trong thời gian đủ ngắn để chạy trên điện thoại.

### 2.6.2. Điểm kết hợp

Điểm của một chuỗi ứng viên $\mathbf{l}$ cộng ba phần: xác suất theo nét viết, xác suất theo mô hình ngôn ngữ và điểm thưởng theo số âm tiết [@hannun2014]:

$$\hat{\mathbf{l}} = \arg\max_{\mathbf{l}} \Big[ \ln p(\mathbf{l} \mid \mathbf{X}) + \alpha \ln P_{\text{LM}}\big(\mathbf{w}(\mathbf{l})\big) + \beta \, \big|\mathbf{w}(\mathbf{l})\big| \Big]$$ {#ct:d6-1}

trong đó $p(\mathbf{l} \mid \mathbf{X})$ là xác suất CTC của chuỗi, $\mathbf{w}(\mathbf{l})$ là dãy âm tiết của chuỗi, $|\mathbf{w}(\mathbf{l})|$ là số âm tiết, $\alpha$ là trọng số của mô hình ngôn ngữ và $\beta$ là điểm thưởng cho mỗi âm tiết. Mô hình ngôn ngữ luôn trừ điểm khi chuỗi dài thêm, nên thiếu $\beta$ thì bộ giải mã có xu hướng bỏ sót âm tiết.

### 2.6.3. Mô hình ngôn ngữ n-gram âm tiết

Mô hình ngôn ngữ gán xác suất cho một dãy âm tiết. Mô hình n-gram giả định mỗi âm tiết chỉ phụ thuộc vào $n - 1$ âm tiết đứng ngay trước nó:

$$P_{\text{LM}}(w_1, \ldots, w_m) \approx \prod_{i=1}^{m} P(w_i \mid w_{i-n+1}, \ldots, w_{i-1})$$ {#ct:d6-2}

trong đó $w_i$ là âm tiết thứ $i$ và $m$ là số âm tiết của dãy. Các xác suất có điều kiện được ước lượng bằng cách đếm trên kho văn bản:

$$P(w_i \mid w_{i-n+1}, \ldots, w_{i-1}) = \frac{C(w_{i-n+1}, \ldots, w_{i-1}, w_i)}{C(w_{i-n+1}, \ldots, w_{i-1})}$$ {#ct:d6-3}

trong đó $C(\cdot)$ là số lần cụm âm tiết xuất hiện. Công thức ({{ct:d6-3}}) cho xác suất bằng 0 với mọi cụm chưa gặp trong kho văn bản, kể cả cụm đúng. Vì vậy phải làm trơn: bớt một phần xác suất của các cụm đã gặp, rồi chia cho các cụm chưa gặp dựa trên cụm ngắn hơn. Kneser-Ney là phương pháp làm trơn hay dùng cho n-gram [@kneser1995].

Tiếng Việt viết cách nhau theo âm tiết, nên dùng âm tiết làm đơn vị là tự nhiên: tách theo khoảng trắng là có ngay dãy âm tiết, không cần bước tách từ.

### 2.6.4. Beam search trên tiền tố

Không thể tính điểm theo công thức ({{ct:d6-1}}) cho mọi chuỗi có thể. Beam search duyệt các bước thời gian từ 1 đến $T$ và chỉ giữ $W$ tiền tố có điểm cao nhất sau mỗi bước [@hannun2014].

Một tiền tố $\mathbf{c}$ là chuỗi ký tự đã gộp, nên nhiều đường căn chỉnh cùng dẫn tới nó. Để cộng đúng xác suất của các đường đó, mỗi tiền tố mang hai giá trị: $p_b(\mathbf{c}, t)$ cho các đường kết thúc bằng nhãn trống và $p_{nb}(\mathbf{c}, t)$ cho các đường kết thúc bằng một ký tự. Cách tách này cần thiết vì chỉ có đường kết thúc bằng nhãn trống mới được nối thêm một ký tự trùng với ký tự cuối của tiền tố, theo phép gộp ở mục 2.5.

Tại bước $t$, tiền tố giữ nguyên khi mô hình phát nhãn trống, hoặc phát lại ký tự cuối $c_{\text{cuối}}$ của nó:

$$\begin{aligned} p_b(\mathbf{c}, t) &= \big(p_b(\mathbf{c}, t-1) + p_{nb}(\mathbf{c}, t-1)\big)\, p_t(\epsilon) \\ p_{nb}(\mathbf{c}, t) &= p_{nb}(\mathbf{c}, t-1)\, p_t(c_{\text{cuối}}) \end{aligned}$$ {#ct:d6-4}

Tiền tố dài thêm một ký tự $k$ khi mô hình phát $k$. Nếu $k$ trùng ký tự cuối thì chỉ các đường kết thúc bằng nhãn trống được nối:

$$p_{nb}(\mathbf{c}k, t) \mathrel{+}= \begin{cases} p_b(\mathbf{c}, t-1)\, p_t(k) & \text{nếu } k = c_{\text{cuối}} \\ \big(p_b(\mathbf{c}, t-1) + p_{nb}(\mathbf{c}, t-1)\big)\, p_t(k) & \text{trường hợp còn lại} \end{cases}$$ {#ct:d6-5}

trong đó $\mathbf{c}k$ là tiền tố $\mathbf{c}$ nối thêm ký tự $k$, và dấu cộng bằng nghĩa là cộng dồn khi nhiều tiền tố cùng dẫn tới $\mathbf{c}k$.

Mô hình ngôn ngữ chỉ được tính khi một âm tiết vừa hoàn thành, tức là khi $k$ là khoảng trắng. Lúc đó điểm của tiền tố nhận thêm $\alpha \ln P(w \mid \text{các âm tiết trước}) + \beta$, với $w$ là âm tiết vừa xong. Sau bước cuối, âm tiết cuối cùng được tính nốt rồi chọn tiền tố có điểm cao nhất.

### 2.6.5. Chọn trọng số

Hai trọng số $\alpha$ và $\beta$ không học được cùng lúc với mô hình. Mô hình quá tự tin trên dữ liệu nó đã học, nên nếu chỉnh $\alpha$ và $\beta$ trên tập huấn luyện thì mô hình ngôn ngữ sẽ bị đánh giá thấp. Hai trọng số phải được chỉnh trên một tập dữ liệu khác, thường là tập kiểm định [@carbune2019].

### 2.6.6. Ví dụ minh họa

Giả sử sau beam search còn hai ứng viên cho một dòng, khác nhau ở một dấu phụ: "ăn côm" và "ăn cơm". Mô hình CTC hơi nghiêng về ứng viên sai. Bảng {{bang:d6-b1}} ghi các giá trị giả định dùng cho ví dụ.

| Ứng viên | $\ln p(\mathbf{l} \mid \mathbf{X})$ | $P(\text{âm tiết hai} \mid \text{"ăn"})$ | $\ln$ của xác suất đó |
| --- | --- | --- | --- |
| "ăn côm" | -1,0 | 0,0001 | -9,210 |
| "ăn cơm" | -1,4 | 0,2 | -1,609 |

Bảng: Giá trị giả định của hai ứng viên {#bang:d6-b1}

Hai ứng viên có cùng âm tiết đầu và cùng số âm tiết, nên phần điểm của âm tiết đầu và của $\beta$ bằng nhau và có thể bỏ qua khi so sánh. Chọn $\alpha = 0{,}5$ và tính theo công thức ({{ct:d6-1}}):

$$\begin{aligned} \text{"ăn côm"}: &\quad -1{,}0 + 0{,}5 \times (-9{,}210) = -5{,}605 \\ \text{"ăn cơm"}: &\quad -1{,}4 + 0{,}5 \times (-1{,}609) = -2{,}205 \end{aligned}$$ {#ct:d6-6}

"ăn cơm" có điểm cao hơn và được chọn. Nếu $\alpha = 0$, tức là không dùng mô hình ngôn ngữ, bộ giải mã sẽ chọn "ăn côm" vì $-1{,}0 > -1{,}4$. Ngược lại, nếu $\alpha$ quá lớn thì mô hình ngôn ngữ lấn át nét viết, và bộ giải mã sẽ sửa cả những âm tiết người dùng viết đúng nhưng ít gặp. Đây là lý do $\alpha$ phải được chỉnh trên tập kiểm định, theo mục 2.4.

### 2.6.7. Áp dụng trong đề tài

- **Vị trí trong hệ thống:** beam search và n-gram âm tiết tạo thành mô hình M2 trong mục 3.2.4, là bản đưa lên điện thoại. Giải mã đơn giản ở mục 2.5 chỉ dùng để theo dõi tỷ lệ lỗi ký tự (CER) trong lúc huấn luyện.
- **Kho văn bản cho n-gram:** gồm văn bản của tập huấn luyện VNOnDB và một kho văn bản khác không lấy từ VieTreeBank, vì văn bản kiểm thử của VNOnDB lấy từ VieTreeBank. Các câu trùng với tập kiểm thử và với câu đề của tập tự thu phải được loại trước khi đếm. Chi tiết thuộc mục 3.1 (dự kiến).
- **Chuẩn hóa văn bản:** kho văn bản và nhãn phải cùng chuẩn Unicode NFC và cùng kiểu đặt dấu thanh. Nếu không, một âm tiết bị đếm thành hai, và xác suất của cả hai đều thấp hơn thực tế.
- **Chỉnh trọng số:** $\alpha$, $\beta$ chỉnh trên tập kiểm định, tập kiểm thử chỉ chạy một lần ở cuối.
- **Ba ứng viên cho người dùng:** sau bước cuối, các tiền tố còn lại trong beam đã được xếp theo điểm, nên có sẵn danh sách ứng viên mà không phải tính thêm.
- **Ràng buộc trên điện thoại:** $W$ lớn thì chính xác hơn nhưng chậm hơn, và n-gram bậc cao thì chính xác hơn nhưng tốn bộ nhớ hơn. Giá trị của $W$ và $n$ sẽ chọn bằng thí nghiệm trong Chương 4, sao cho mô hình và n-gram không quá 20 MB và mỗi dòng nhận dạng không quá 1 giây (dự kiến). Bộ giải mã viết bằng Kotlin, và nên có bản tham chiếu bằng Python để so kết quả.

### 2.6.8. Hạn chế

- **Beam có thể bỏ sót đáp án:** chuỗi đúng bị loại ở một bước giữa chừng thì không quay lại được, dù điểm cuối của nó cao nhất. $W$ càng nhỏ thì rủi ro càng lớn.
- **Mô hình ngôn ngữ chỉ tác động ở ranh giới âm tiết:** trong lúc một âm tiết chưa xong, beam chỉ dựa vào xác suất của nét viết, nên âm tiết đúng có thể bị loại trước khi mô hình ngôn ngữ kịp giúp.
- **Ngữ cảnh ngắn:** n-gram chỉ nhìn $n - 1$ âm tiết trước. Nó không dùng được ngữ cảnh xa hơn hay ngữ cảnh phía sau âm tiết đang xét.
- **Lệch miền văn bản:** n-gram học từ một kho văn bản sẽ ưu tiên cách viết của kho đó. Người dùng viết nội dung khác, như tên riêng hay từ chuyên ngành, có thể bị sửa sai.
- **Chi phí:** mỗi bước phải xét $W$ tiền tố nhân với số nhãn, cộng thêm tra cứu n-gram, nên beam search chậm hơn nhiều so với giải mã đơn giản. Độ trễ này cộng vào thời gian chạy mô hình trên điện thoại.

## 2.7. Lượng tử hóa mô hình

### 2.7.1. Bài toán

Đầu vào là mô hình đã huấn luyện, mỗi trọng số lưu bằng số thực 32 bit. Đầu ra là mô hình cho kết quả gần như cũ nhưng chiếm ít dung lượng hơn. Mô hình còn phải chạy được trên điện thoại mà không có tập dữ liệu kèm theo. Vì vậy đề tài chỉ xét các cách không cần tập hiệu chỉnh.

### 2.7.2. Lượng tử hóa sang số nguyên

Lượng tử hóa sang số nguyên 8 bit biểu diễn mỗi trọng số bằng một số nguyên, cùng một bước lượng tử và một điểm không [@jacob2017]:

$$\tilde{\theta} = \gamma \, (\nu - \zeta)$$ {#ct:d7-1}

trong đó $\tilde{\theta}$ là giá trị khôi phục của trọng số $\theta$, $\nu$ là số nguyên được lưu, $\gamma$ là bước lượng tử và $\zeta$ là điểm không, tức số nguyên ứng với giá trị thực 0. Với khoảng giá trị từ $\theta_{\min}$ đến $\theta_{\max}$, bước lượng tử bằng:

$$\gamma = \frac{\theta_{\max} - \theta_{\min}}{255}$$ {#ct:d7-2}

trong đó $\theta_{\min}$ và $\theta_{\max}$ là giá trị nhỏ nhất và lớn nhất của nhóm trọng số. Sai số của mỗi trọng số không quá $\gamma / 2$, nên nhóm trọng số có khoảng giá trị rộng sẽ có sai số lớn.

### 2.7.3. Lượng tử hóa dynamic range

Cách này lưu trọng số bằng số nguyên 8 bit, còn giá trị kích hoạt vẫn là số thực khi chạy [@google2026e]. Cách này không cần dữ liệu mẫu, giảm dung lượng khoảng 4 lần và thường chạy nhanh hơn.

### 2.7.4. Lượng tử hóa float16

Cách này lưu trọng số bằng số thực 16 bit [@google2026e]. Số thực 16 bit có sai số tương đối nhỏ ở mọi độ lớn, nên hầu như không làm giảm độ chính xác. Dung lượng giảm khoảng 2 lần.

### 2.7.5. Ví dụ minh họa

Giả sử một nhóm trọng số có giá trị từ $-1{,}2$ đến $0{,}8$. Theo công thức ({{ct:d7-2}}), bước lượng tử bằng $2 / 255 \approx 0{,}00784$, và điểm không bằng $1{,}2 / 0{,}00784 \approx 153$. Trọng số $\theta = 0{,}5$ được lưu thành $\nu = \text{round}(0{,}5 / 0{,}00784) + 153 = 64 + 153 = 217$.

Theo công thức ({{ct:d7-1}}), giá trị khôi phục bằng $0{,}00784 \times (217 - 153) \approx 0{,}502$, lệch khoảng 0,002 so với giá trị gốc. Sai số này nhỏ với một trọng số, nhưng cộng dồn qua nhiều lớp và nhiều bước của lớp LSTM.

Ví dụ thứ hai tính dung lượng của mô hình M1, có 1.005.761 tham số. Bảng {{bang:d7-b1}} so kết quả tính với dung lượng đo được của tệp `.tflite`, phần chênh là mô tả cấu trúc của mô hình.

| Cách lưu | Số byte mỗi trọng số | Dung lượng tính | Dung lượng đo |
| --- | --- | --- | --- |
| Số thực 32 bit | 4 | 4,02 MB | 4,03 MB |
| Float16 | 2 | 2,01 MB | 2,03 MB |
| Dynamic range | 1 | 1,01 MB | 1,03 MB |

Bảng: Dung lượng của mô hình M1 theo cách lưu trọng số {#bang:d7-b1}

### 2.7.6. Áp dụng trong đề tài

- **So sánh:** đề tài đo cả hai cách trên toàn bộ tập kiểm định, theo mục 4.3.
- **Lựa chọn:** đề tài dùng float16. Dynamic range làm tỷ lệ lỗi ký tự (CER) vượt ngưỡng, còn float16 cho kết quả gần như bản gốc.
- **Dung lượng:** với M1, float16 làm mô hình tăng thêm khoảng 1 MB so với dynamic range. Với M1 lớn, mô hình đang dùng trong ứng dụng, mức tăng là khoảng 2,2 MB, theo mục 4.3. Tổng dung lượng vẫn thấp hơn ngưỡng 20 MB trong mục 1.2.
- **Cách chuyển đổi:** các bước cụ thể nằm trong mục 5.1.

### 2.7.7. Hạn chế

- **Độ chính xác giảm không đều:** lỗi do lượng tử hóa dynamic range phụ thuộc vào khoảng giá trị của từng nhóm trọng số, nên phải đo lại trên dữ liệu thật sau mỗi lần chuyển đổi.
- **Float16 không nhanh hơn trên mọi máy:** khi chạy bằng CPU, trọng số thường được đổi lại sang số thực 32 bit, nên lợi ích chính là dung lượng.
- **Phụ thuộc thời gian đo:** thời gian đo trên máy tính không phản ánh thời gian trên điện thoại, nên độ trễ phải đo trên máy thật theo mục 1.5.3.

