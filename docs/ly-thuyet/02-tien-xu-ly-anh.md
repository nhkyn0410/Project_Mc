# Vẽ nét thành ảnh và tiền xử lý ảnh

Trạng thái: Nháp

Tài liệu này trình bày các bước đưa một dòng chữ viết tay về ảnh đầu vào của mô hình: vẽ nét thành ảnh, đặt dòng vào khung cố định, tăng cường dữ liệu và lấy khung xương để vẽ lại ảnh huấn luyện. Các bước này quyết định ảnh trên điện thoại có giống ảnh huấn luyện hay không. Tài liệu dành cho người viết phần tiền xử lý và phần cơ sở lý thuyết của báo cáo, nên đọc sau `01-nhan-dang-chu-viet-tay-tu-anh.md` và trước `03-cnn-2d.md`.

## 1. Bài toán

Mô hình nhận ảnh xám $\mathbf{X}$ cao $H$, rộng $R$ điểm ảnh. Khi huấn luyện, ảnh lấy từ bản ảnh của bộ dữ liệu HANDS-VNOnDB (VNOnDB). Trên điện thoại, đầu vào là các nét của một dòng liền hoặc một dòng ảo, mỗi nét là một chuỗi điểm có tọa độ. Bài toán gồm bốn phần:

- **Vẽ nét thành ảnh:** từ chuỗi điểm tạo ảnh xám có mép nét mềm như ảnh huấn luyện.
- **Đặt dòng vào khung:** đưa mọi dòng, dài hay ngắn, về cùng một khung mà vẫn giữ tỷ lệ của chữ.
- **Tăng cường dữ liệu:** tạo biến thể của ảnh huấn luyện để mô hình không học thuộc cách vẽ của bộ dữ liệu.
- **Vẽ lại ảnh huấn luyện:** tạo ảnh huấn luyện giống ảnh do bộ vẽ của ứng dụng tạo ra.

Mô hình chỉ học được những gì có trong ảnh huấn luyện. Khi ảnh trên điện thoại lệch ảnh huấn luyện về độ dày nét, độ đậm hay cỡ chữ, tỷ lệ lỗi ký tự (CER) tăng lên dù chữ vẫn dễ đọc với người.

## 2. Nguyên lý

### 2.1. Vẽ đoạn thẳng có khử răng cưa

Nét được vẽ thành các đoạn thẳng nối hai điểm liên tiếp. Nếu mỗi điểm ảnh chỉ được tô hoặc không tô, mép nét sẽ có răng cưa. Răng cưa là hiện tượng lấy mẫu chưa đủ dày, và cách khắc phục là lọc hình trước khi lấy mẫu [@crow1977]. Lấy mẫu dày là cách lọc đơn giản: vẽ trên lưới mịn gấp $\rho$ lần mỗi chiều, rồi lấy trung bình mỗi khối $\rho$ nhân $\rho$ ô thành một điểm ảnh.

Với đoạn thẳng từ $\mathbf{e}_1$ đến $\mathbf{e}_2$ và một ô có tâm $\mathbf{g}$, điểm gần $\mathbf{g}$ nhất trên đoạn ứng với vị trí:

$$
\eta = \min\left(1, \max\left(0, \frac{(\mathbf{g} - \mathbf{e}_1) \cdot (\mathbf{e}_2 - \mathbf{e}_1)}{\lVert \mathbf{e}_2 - \mathbf{e}_1 \rVert^2}\right)\right) \tag{1}
$$

trong đó $\mathbf{e}_1$, $\mathbf{e}_2$ là hai đầu của đoạn thẳng, $\mathbf{g}$ là tâm ô và $\eta$ là vị trí trên đoạn, bằng 0 tại $\mathbf{e}_1$ và bằng 1 tại $\mathbf{e}_2$. Ô được tô khi tâm của nó cách đoạn thẳng không quá nửa độ dày nét:

$$
\lVert \mathbf{g} - \mathbf{e}_1 - \eta \, (\mathbf{e}_2 - \mathbf{e}_1) \rVert \le \frac{\rho \, \omega}{2} \tag{2}
$$

trong đó $\rho$ là số ô của lưới mịn trên một cạnh điểm ảnh và $\omega$ là độ dày nét trên khung cuối, tính bằng điểm ảnh. Mọi tọa độ trong công thức (1) và công thức (2) tính theo ô của lưới mịn. Mỗi điểm ảnh nhận giá trị bằng 255 nhân tỷ lệ ô được tô trong $\rho^2$ ô của nó.

### 2.2. Đặt dòng vào khung

Phần nét rộng $\Delta_R$ và cao $\Delta_H$ được co đều hai trục với hệ số:

$$
\lambda = \min\left(\frac{R - 2\delta}{\Delta_R}, \frac{H_{\text{nét}}}{\Delta_H}\right) \tag{3}
$$

trong đó $\delta$ là lề ngang của khung và $H_{\text{nét}}$ là chiều cao tối đa của phần nét sau khi co, bằng $H$ khi không giới hạn. Một hệ số chung cho hai trục giữ nguyên tỷ lệ của chữ. Sau khi co, phần nét cách mép trái $\delta$ điểm ảnh và nằm giữa khung theo chiều dọc.

Công thức (3) có hai trường hợp. Dòng dài chạm giới hạn chiều rộng trước, nên chữ càng nhỏ khi dòng càng dài. Dòng ngắn chạm giới hạn chiều cao trước, nên phần nét luôn cao bằng $H_{\text{nét}}$ dù dòng có ít chữ. Vì vậy, khi không giới hạn chiều cao phần nét, chữ của dòng ngắn to hơn chữ của dòng dài.

### 2.3. Tăng cường dữ liệu

Tăng cường dữ liệu tạo biến thể mới của ảnh huấn luyện mỗi khi ảnh được dùng, còn nhãn giữ nguyên. Puigcerver dùng biến đổi affine ngẫu nhiên cùng phép co và phép giãn ảnh xám khi huấn luyện mô hình nhận dạng dòng chữ viết tay dạng ảnh [@puigcerver2017]. Đề tài dùng bốn nhóm phép biến đổi:

- **Biến dạng đàn hồi:** mỗi điểm ảnh lấy giá trị tại một vị trí dịch đi theo trường dịch chuyển trơn ngẫu nhiên, nên chữ cong và co giãn cục bộ như khác biệt giữa các người viết [@simard2003]. Đề tài tạo trường dịch chuyển bằng cách phóng to một lưới số ngẫu nhiên thô, các nút cách nhau 12 điểm ảnh, rồi nhân với biên độ.
- **Biến đổi affine:** co giãn ngang theo hệ số $s_x$, co giãn dọc theo hệ số $s_y$, nghiêng theo hệ số $\psi$ và dịch dọc $o_y$ điểm ảnh. Điểm ảnh ở hàng $u$, cột $v$ của ảnh mới lấy giá trị của ảnh cũ tại vị trí cho bởi công thức (4), nội suy song tuyến tính từ bốn điểm ảnh lân cận.
- **Làm dày và làm mỏng nét:** phép giãn lấy giá trị lớn nhất trong ô 3 nhân 3 quanh mỗi điểm ảnh nên làm nét dày lên, còn phép co lấy giá trị nhỏ nhất nên làm nét mỏng đi. Ảnh mới là ảnh cũ trộn với một trong hai ảnh đó theo một hệ số ngẫu nhiên.
- **Độ đậm:** nhân mọi điểm ảnh với cùng một hệ số, rồi cắt về khoảng từ 0 đến 1.

$$
v_0 = \frac{v - R/2}{s_x} + \psi \left(u - \frac{H}{2}\right) + \frac{R}{2}, \quad u_0 = \frac{u - H/2}{s_y} + \frac{H}{2} - o_y \tag{4}
$$

trong đó $u_0$, $v_0$ là hàng và cột trên ảnh cũ. Công thức (4) co giãn quanh tâm khung, nên nét không bị đẩy lệch về một phía của khung.

### 2.4. Lấy khung xương

Khung xương của một vùng nét là tập điểm ảnh rộng một điểm ảnh chạy dọc giữa nét, giữ nguyên hình dạng và các chỗ nối của nét. Thuật toán của Zhang và Suen bóc dần các điểm ảnh ở biên của vùng nét [@zhang1984]. Mỗi vòng gồm hai lượt: lượt đầu xóa các điểm biên phía dưới bên phải cùng các điểm góc phía trên bên trái, lượt sau xóa các điểm biên còn lại. Một điểm chỉ bị xóa khi việc xóa không làm đứt vùng nét, và thuật toán dừng khi không còn điểm nào bị xóa. Kết quả là đường mảnh, nối lại được thành các đoạn thẳng giống nét thu trên điện thoại.

## 3. Ví dụ minh họa

Ví dụ thứ nhất áp công thức (1) và công thức (2) với $\rho = 4$ và $\omega = 1{,}2$, nên ô được tô khi tâm ô cách đoạn thẳng không quá 2,4 ô. Xét một đoạn thẳng nằm ngang. Tâm các hàng ô cách đoạn 0,5 và 1,5 ô thì được tô, cách 2,5 ô thì không, nên mỗi cột có đúng 4 hàng ô được tô. Bảng 1 ghi giá trị của các điểm ảnh theo vị trí của đoạn so với lưới điểm ảnh.

Bảng 1: Một đoạn thẳng nằm ngang dày 1,2 điểm ảnh, vẽ trên lưới mịn gấp 4 lần

| Vị trí của đoạn thẳng | Số hàng ô được tô trong mỗi điểm ảnh | Giá trị điểm ảnh |
| --- | --- | --- |
| Giữa một hàng điểm ảnh | 4 trong một điểm ảnh | 255 |
| Trên ranh giới hai hàng điểm ảnh | 2 trong mỗi điểm ảnh của hai hàng | 128 và 128 |

Bảng 1 cho thấy cùng một nét có thể thành một hàng điểm ảnh đậm hoặc hai hàng điểm ảnh xám, tùy vị trí. Tổng độ đậm của hai trường hợp bằng nhau, nên nét không dày lên hay mỏng đi khi dịch chuyển chưa tới một điểm ảnh.

Ví dụ thứ hai áp công thức (3) cho hai dòng của cùng một người viết, với $R = 512$, $H = 64$ và $\delta = 8$. Hai dòng cùng có phần nét cao $\Delta_H = 80$ điểm ảnh, dòng dài rộng 1.000 và dòng ngắn rộng 250 điểm ảnh. Bảng 2 ghi kết quả khi không giới hạn và khi giới hạn chiều cao phần nét ở 40 điểm ảnh.

Bảng 2: Hệ số co và chiều cao phần nét theo công thức (3)

| Dòng | $H_{\text{nét}}$ | $\lambda$ | Chiều cao phần nét sau khi co |
| --- | --- | --- | --- |
| Dài | 64 | 0,496 | 39,7 |
| Ngắn | 64 | 0,800 | 64,0 |
| Dài | 40 | 0,496 | 39,7 |
| Ngắn | 40 | 0,500 | 40,0 |

Theo Bảng 2, khi không giới hạn, chữ của dòng ngắn to gấp khoảng 1,6 lần chữ của dòng dài. Giới hạn $H_{\text{nét}} = 40$ đưa hai hệ số co về gần nhau và không làm đổi kết quả của dòng dài.

## 4. Áp dụng trong đề tài

- **Chuẩn hóa ảnh huấn luyện:** mã `training/data.py` đảo ảnh để nét có giá trị lớn, cắt theo khung bao của các điểm ảnh có giá trị trên 40, rồi co theo công thức (3) với $H = 64$, $R = 512$ và $\delta = 8$, theo `03-du-lieu.md`, mục 3.3.
- **Bộ vẽ:** mã `training/ink.py` và `Ink.kt` dùng công thức (1) và công thức (2) với $\rho = 4$ và $\omega = 1{,}2$, theo `04-thiet-ke-he-thong.md`, mục 3. Bộ vẽ trừ thêm $\omega$ ở cả hai tử số của công thức (3) để mép nét không vượt khung. Đề tài tự viết bộ vẽ để bản Python và bản Kotlin cho cùng một ảnh.
- **Giới hạn chiều cao phần nét:** đề tài đã thử $H_{\text{nét}} = 40$ để giảm CER của dòng ngắn, theo `07-nhat-ky-thi-nghiem.md`, mục 6. Cách này giúp khi dùng riêng nhưng không giúp khi kết hợp với ảnh vẽ lại, nên cấu hình cuối không dùng, theo `07-nhat-ky-thi-nghiem.md`, mục 10.5.
- **Mức tăng cường:** $s_x$ từ 0,88 đến 1,02, $s_y$ từ 0,85 đến 1,15, $\psi$ trong khoảng $[-0{,}25; 0{,}25]$ và $o_y$ trong khoảng $[-3; 3]$, mỗi giá trị lấy ngẫu nhiên đều. Hệ số $s_x$ không vượt 1,02, vì phóng ngang nhiều hơn làm nét rơi khỏi khung trong khi nhãn vẫn đủ ký tự, theo `07-nhat-ky-thi-nghiem.md`, mục 8. Hệ số trộn dày mỏng nằm trong khoảng $[-0{,}5; 1]$, giá trị âm làm mỏng và giá trị dương làm dày. Hệ số độ đậm từ 0,5 đến 2,5, chỉ dùng ở các lần chạy có ảnh vẽ lại. Biến dạng đàn hồi biên độ 2 điểm ảnh chỉ dùng ở lần chạy `m1_rr_el`, theo `05-ke-hoach-thi-nghiem.md`, mục 3. Lần chạy này kém hơn trên cả tập kiểm định và nét viết thật, nên cấu hình cuối không dùng biến dạng đàn hồi, theo `07-nhat-ky-thi-nghiem.md`, mục 10.8.
- **Vẽ lại ảnh huấn luyện:** mã `training/rerender.py` lấy khung xương của các điểm ảnh có giá trị trên 80 bằng thuật toán ở mục 2.4, nối mỗi cặp điểm ảnh kề nhau thành một đoạn thẳng, rồi vẽ lại bằng bộ vẽ ở mục 2.1 với $\omega$ bằng 0,8; 1,2 và 1,6. Từ lần chạy `m1_rr`, mỗi lần dùng một dòng, vòng huấn luyện chọn ngẫu nhiên một trong bốn ảnh của dòng đó, gồm ảnh gốc và ba ảnh vẽ lại, theo `07-nhat-ky-thi-nghiem.md`, mục 2. Cấu hình cuối dùng cách này.

## 5. Hạn chế

- **Khung xương sai lệch:** khung xương làm đứt các nét mảnh và sinh nhánh thừa ở chỗ nét giao nhau. Ảnh vẽ lại vì vậy chỉ gần đúng với ảnh vẽ từ nét thật.
- **Một độ dày cho mọi nét:** bộ vẽ không dùng lực nhấn và tốc độ viết, trong khi nét trong ảnh VNOnDB dày mỏng khác nhau.
- **Cỡ chữ phụ thuộc độ dài dòng:** theo Bảng 2, dòng ngắn có chữ to hơn dòng dài. Giới hạn $H_{\text{nét}}$ thu hẹp chênh lệch này nhưng làm dòng ngắn có ít điểm ảnh hơn.
- **Mức tăng cường chọn bằng tay:** các khoảng giá trị ở mục 4 chưa được dò có hệ thống.
- **Lệch giữa hai nguồn ảnh vẫn lớn:** CER của mô hình `m1_v2` tăng từ 12,12% trên ảnh kiểm định gốc lên 30,82% trên ảnh vẽ lại, theo `07-nhat-ky-thi-nghiem.md`, mục 7. Trên nét viết thật, CER còn cao hơn, theo `07-nhat-ky-thi-nghiem.md`, mục 10.
