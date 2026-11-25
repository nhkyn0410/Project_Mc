# CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ

Chương này trình bày môi trường và cách tiến hành thí nghiệm, kết quả huấn luyện trên tập kiểm định, cách chọn mô hình trên nét viết thật, dữ liệu viết bằng ngón tay, kết quả cuối trên tập kiểm thử VNOnDB và tập đánh giá, phân tích lỗi, và đối chiếu kết quả với các mục tiêu ở Bảng {{bang:muc-tieu}}.

## 4.1. Môi trường thực nghiệm

Bảng {{bang:moi-truong}} ghi môi trường của mọi lần chạy. Mã nguồn nằm trong thư mục `training/` của kho mã, còn dữ liệu và kết quả được lưu ngoài kho mã trên máy huấn luyện.

| Thành phần | Giá trị |
| --- | --- |
| Card đồ họa | NVIDIA GeForce RTX 4050 Laptop, 6 GB |
| Hệ điều hành | Ubuntu chạy trong Windows 11 |
| Thư viện huấn luyện | TensorFlow 2.21.0, Keras 3.15.1 |
| Thư viện chuyển đổi | tf-keras 2.21.0 |
| Ứng dụng | Android, viết bằng Kotlin, chạy mô hình bằng LiteRT |
| Bộ ký tự | 160 ký tự của tập huấn luyện và tập kiểm định, cộng nhãn trống |

Bảng: Môi trường thực nghiệm {#bang:moi-truong w=30,70}

Một epoch mất khoảng 30 giây với M1 ở cấu hình gốc và khoảng 42 giây với M1 lớn có ảnh vẽ lại. Máy huấn luyện không đủ bộ nhớ cho nhiều lần chạy cùng lúc, nên các lần chạy được xếp hàng và chạy lần lượt.

## 4.2. Cách tiến hành thí nghiệm

### 4.2.1. Nguyên tắc

Các thí nghiệm tuân theo bốn nguyên tắc:

- **Một thay đổi mỗi lần:** mỗi thí nghiệm đổi một yếu tố so với một cấu hình gốc đã có kết quả, để biết thay đổi nào gây ra chênh lệch.
- **Hạt giống cố định:** mọi lần chạy dùng hạt giống 1, trừ thí nghiệm hạt giống ở mục 4.4.3.
- **Cách chọn chốt trước khi đo:** với các quyết định quan trọng, tiêu chí chọn được ghi lại trước khi có kết quả, để kết quả không làm lệch tiêu chí.
- **Không chạm tập kiểm thử:** tập kiểm thử VNOnDB và tập đánh giá của tập tự thu chỉ được đo một lần ở cuối, sau khi đã chốt mô hình và mọi tham số.

### 4.2.2. Dữ liệu dùng để so sánh và quy tắc chọn

Bảng {{bang:du-lieu-do}} ghi các tập dữ liệu dùng để so sánh các cấu hình trong lúc phát triển. Nét viết thật của buổi thử và nhóm chỉnh chỉ dùng để chỉnh và so sánh, không dùng để huấn luyện và không tính vào kết quả cuối.

| Tập | Quy mô | Đo gì |
| --- | --- | --- |
| Tập kiểm định VNOnDB | 1.229 dòng | CER khi huấn luyện, CER của M2 cho quy tắc chọn |
| Ảnh vẽ lại của tập kiểm định | 400 dòng đầu, độ dày nét 1,2 | Độ nhạy với bộ vẽ của ứng dụng |
| Nét viết thật của hai buổi thử | 6 người viết bằng bút, các dòng chép đúng đề | CER của M2 trên dòng ngắt, dòng liền và dòng ngắt mô phỏng |
| Nhóm chỉnh của tập tự thu | 9 buổi viết bằng ngón tay | Kiểm tra độ dày nét và tham số của lớp ghép đoạn |

Bảng: Các tập dữ liệu dùng khi so sánh cấu hình {#bang:du-lieu-do w=27,30,43}

Trong chương này, M2 chỉ cách giải mã của bản đưa lên điện thoại, tức beam search rộng 30 kèm n-gram âm tiết, áp cho mô hình đang xét. Giải mã đơn giản là cách giải mã ở mục 2.5.6, không dùng mô hình ngôn ngữ. Mọi kết quả của M2 dùng bản float16 của mô hình, trừ khi ghi khác.

Quy tắc chọn mô hình như sau: trong các mô hình có CER (2) của M2 trên tập kiểm định không quá 8,4%, mô hình tốt nhất là mô hình có CER của M2 thấp nhất trên nét viết thật. Quy tắc này dùng cả hai loại dữ liệu, vì CER trên tập kiểm định không phản ánh được nét viết trên điện thoại, theo mục 4.4.

### 4.2.3. Thứ tự tiến hành

Các bước được tiến hành theo thứ tự sau:

1. Chạy lần lượt các thí nghiệm trên dữ liệu và mô hình ở Bảng {{bang:thi-nghiem}}.
2. Với mỗi lần chạy, chuyển mô hình sang LiteRT rồi đo trên tập kiểm định, ảnh vẽ lại và nét viết thật của buổi thử.
3. Chọn cấu hình theo quy tắc ở mục 4.2.2.
4. Chạy mô hình cơ sở M0 với cấu hình dữ liệu đã chọn.
5. Chỉnh $\alpha$ và $\beta$ trên tập kiểm định, đo lại cấu hình triển khai, sinh tệp cho ứng dụng và đối chiếu bản Kotlin với bản Python.
6. Kiểm tra độ dày nét và lớp ghép đoạn trên nhóm chỉnh viết bằng ngón tay.
7. Chốt mọi tham số, rồi đo tập kiểm thử VNOnDB và tập đánh giá, mỗi tập một lần.

Bảng {{bang:thi-nghiem}} ghi các thí nghiệm, câu hỏi mỗi thí nghiệm trả lời và kết quả. Cấu hình gốc là lần chạy `m1_v2`, dùng M1 với tăng cường hình học và lề 8 điểm ảnh, huấn luyện 60 epoch.

| Thí nghiệm | Thay đổi so với cấu hình gốc | Câu hỏi | Kết quả |
| --- | --- | --- | --- |
| Ảnh vẽ lại | Thêm ba ảnh vẽ lại cho mỗi dòng, tăng cường độ đậm | Có thu hẹp khoảng cách với nét viết thật không? | Tốt hơn rõ trên nét viết thật, nhưng M2 trên tập kiểm định vượt ngưỡng |
| Giới hạn chiều cao phần nét | $H_{\text{nét}} = 40$ | Có giảm CER của dòng ngắn không? | Giảm một phần, không tốt hơn trên nét viết thật |
| Kết hợp | Ảnh vẽ lại và $H_{\text{nét}} = 40$ | Hai thay đổi có cộng dồn không? | Không, kém hơn chỉ dùng ảnh vẽ lại |
| Mô hình lớn hơn | Như ảnh vẽ lại, dùng M1 lớn | Có đạt cả ngưỡng trên tập kiểm định và CER thấp trên nét viết thật không? | Có |
| Biến dạng đàn hồi | Như ảnh vẽ lại, thêm biến dạng đàn hồi biên độ 2 điểm ảnh | Mô hình có đọc kiểu chữ lạ tốt hơn không? | Không, kém hơn trên cả hai loại dữ liệu |
| Huấn luyện lâu hơn | Như ảnh vẽ lại, 100 epoch thay cho 60 | Mô hình còn cải thiện sau epoch 60 không? | Có, với cả M1 và M1 lớn |
| Hạt giống | Chạy lại hai cấu hình 100 epoch với hạt giống 2 và 3 | Chênh lệch giữa M1 và M1 lớn có lớn hơn độ dao động do ngẫu nhiên không? | Trên tập kiểm định thì có, M1 lớn tốt hơn |
| Mô hình M0 | Bỏ BiLSTM, giữ cấu hình dữ liệu được chọn | BiLSTM có đáng giữ không? | Có, bỏ BiLSTM làm CER tăng khoảng gấp đôi |
| N-gram ký tự, sau khi chốt cấu hình | Thêm n-gram ký tự vào bộ giải mã | Chấm điểm từng ký tự có giảm lỗi khi viết bằng ngón tay không? | Có, theo mục 4.8 |

Bảng: Các thí nghiệm, câu hỏi và kết quả {#bang:thi-nghiem w=17,29,29,25 co=12}

## 4.3. Kết quả trên tập kiểm định

### 4.3.1. Các lần huấn luyện

Bảng {{bang:huan-luyen}} ghi kết quả của epoch tốt nhất của các lần chạy chính, đo bằng giải mã đơn giản, không dùng mô hình ngôn ngữ, trên 1.229 dòng kiểm định. Tên lần chạy gồm mô hình, cấu hình dữ liệu và số epoch: `m1` là M1, `m1l` là M1 lớn, `m0` là M0, `rr` là có ảnh vẽ lại, `cap40` là giới hạn chiều cao phần nét ở 40 điểm ảnh, `el` là biến dạng đàn hồi và `e100` là 100 epoch.

| Lần chạy | Số epoch | Thay đổi | CER (2) | WER (2) |
| --- | --- | --- | --- | --- |
| `m1_v2` | 60 | Cấu hình gốc | 11,06% | 33,26% |
| `m1_rr` | 60 | Thêm ảnh vẽ lại | 12,20% | 36,98% |
| `m1_cap40` | 60 | Giới hạn chiều cao phần nét | 10,62% | 32,26% |
| `m1_rr_cap40` | 60 | Ảnh vẽ lại và giới hạn chiều cao | 12,91% | 37,99% |
| `m1l_rr` | 60 | Như `m1_rr`, dùng M1 lớn | 9,88% | 30,07% |
| `m1_rr_el` | 60 | Như `m1_rr`, thêm biến dạng đàn hồi | 15,48% | 45,18% |
| `m1_rr_e100` | 100 | Như `m1_rr`, 100 epoch | 10,04% | 30,39% |
| `m0_rr` | 60 | Như `m1_rr`, dùng M0 | 24,68% | 64,22% |
| `m1l_rr_e100` | 100 | Như `m1l_rr`, 100 epoch | 8,27% | 25,09% |
| `m1l_rr_e150` | 150 | Như `m1l_rr`, 150 epoch | 7,95% | 24,14% |

Bảng: Kết quả huấn luyện trên tập kiểm định, giải mã đơn giản {#bang:huan-luyen w=20,12,40,14,14 can=t,g,t,p,p}

Theo Bảng {{bang:huan-luyen}}, ảnh vẽ lại làm CER trên tập kiểm định tăng khoảng 1,1 điểm phần trăm với M1, vì mô hình phải học thêm kiểu nét khác ảnh kiểm định. M1 lớn bù được phần tăng này. Huấn luyện 100 epoch giảm CER của `m1_rr` 2,16 điểm phần trăm và của `m1l_rr` 1,61 điểm phần trăm. M0 không có BiLSTM có CER khoảng gấp đôi M1, nên BiLSTM đáng giữ dù M0 chỉ có 327.745 tham số so với 1.005.761 của M1. Biến dạng đàn hồi làm M1 kém đi rõ. Lần chạy 150 epoch giảm thêm CER nhưng không đạt điều kiện đã chốt trước để thay mô hình, theo mục 4.4.3.

Trước các thí nghiệm, đề tài kiểm tra khung huấn luyện bằng phép học thuộc: huấn luyện trên 100 dòng đầu, không tăng cường và không dropout, rồi đo trên chính 100 dòng đó. Sau 600 epoch, CER (2) đạt 0% ở epoch 365, nên khung huấn luyện hoạt động đúng.

### 4.3.2. Bộ giải mã và mô hình ngôn ngữ

Bảng {{bang:giai-ma-kq}} ghi kết quả của mô hình `m1_v2` với từng cách giải mã trên 1.229 dòng kiểm định. Mô hình ngôn ngữ được học sau khi loại các câu của tập kiểm định, tập kiểm thử và câu đề của tập tự thu. Trọng số $\alpha$ và $\beta$ được chọn trên 410 dòng kiểm định. Bản đo này dùng mô hình Keras và n-gram chưa nén, trước khi chuyển đổi sang LiteRT.

| Cách giải mã | CER (2) | WER (2) | CER (1) | WER (1) |
| --- | --- | --- | --- | --- |
| Giải mã đơn giản | 11,06% | 33,24% | 9,93% | 31,19% |
| Beam search rộng 30, không n-gram | 10,75% | 32,63% | 9,71% | 30,70% |
| Beam search rộng 10, n-gram | 8,65% | 23,35% | 7,63% | 21,65% |
| Beam search rộng 20, n-gram | 8,31% | 22,45% | 7,37% | 20,78% |
| Beam search rộng 30, n-gram | 8,20% | 22,06% | 7,24% | 20,38% |
| Beam search rộng 50, n-gram | 8,10% | 21,79% | 7,15% | 20,14% |

Bảng: Kết quả các cách giải mã của mô hình m1_v2 trên tập kiểm định {#bang:giai-ma-kq w=40,15,15,15,15 can=t,p,p,p,p}

Theo Bảng {{bang:giai-ma-kq}}, mô hình ngôn ngữ giảm CER (2) từ 10,75% xuống 8,20%, tức 2,55 điểm phần trăm, và giảm WER (2) hơn 10 điểm phần trăm. Đề tài chọn độ rộng beam 30, vì tăng lên 50 chỉ giảm thêm 0,10 điểm phần trăm mà tốn thời gian hơn. Kho văn bản của mô hình ngôn ngữ gồm 1.503.954 câu, và 30.000 âm tiết của từ vựng phủ 98,64% số âm tiết của kho.

Sau khi chọn M1 lớn, đề tài chỉnh lại $\alpha$ và $\beta$ bằng cách dò lưới 4 giá trị của $\alpha$ từ 0,3 đến 0,8 và 6 giá trị của $\beta$ từ 1 đến 8. Cặp $\alpha = 0{,}45$ và $\beta = 4$ đang dùng và cặp $\beta = 3$ chênh nhau không quá 0,17 điểm phần trăm trên tập kiểm định, còn trên nét viết thật cặp $\beta = 4$ thấp hơn 0,34 điểm phần trăm. Đề tài giữ $\alpha = 0{,}45$ và $\beta = 4$.

### 4.3.3. Chuyển đổi và lượng tử hóa

Bảng {{bang:litert}} ghi kết quả chuyển đổi mô hình được chọn sang LiteRT, đo bằng giải mã đơn giản trên 200 dòng kiểm định lấy cách đều. Thời gian đo trên CPU của máy huấn luyện trong lúc máy chạy việc khác, nên chỉ dùng để so giữa các bản.

| Bản | Dung lượng | CER (2) | Số dòng giống bản Keras | Thời gian trung vị một dòng |
| --- | --- | --- | --- | --- |
| Keras | Không đo | 8,22% | 200 | Không đo |
| LiteRT, chưa lượng tử hóa | 8,92 MB | 8,28% | 185 | 39,8 ms |
| LiteRT, float16 | 4,47 MB | 8,29% | 185 | 38,0 ms |
| LiteRT, dynamic range | 2,26 MB | 8,86% | 80 | 21,7 ms |

Bảng: Kết quả chuyển đổi mô hình m1l_rr_e100 sang LiteRT {#bang:litert w=28,15,14,21,22 can=t,p,p,p,p}

Theo Bảng {{bang:litert}}, dynamic range làm CER tăng 0,64 điểm phần trăm so với bản Keras, còn float16 chỉ tăng 0,07 điểm phần trăm. Với mô hình `m1_v2`, dynamic range cũng làm CER của M2 trên tập kiểm định vượt ngưỡng 8,4%, còn float16 đạt. Đề tài vì vậy dùng float16. Bản float16 nặng 4,47 MB, nên tổng dung lượng với mô hình ngôn ngữ là 15,43 MB, dưới ngưỡng 20 MB.

Có hai điểm bắt buộc khi chuyển đổi. Thứ nhất, lớp LSTM của Keras 3 chuyển thành vòng lặp có biến và lỗi khi chạy, nên mô hình được dựng lại bằng tf-keras và chép trọng số sang, để tệp dùng toán tử LSTM gốc của LiteRT. Thứ hai, toán tử LSTM của LiteRT giữ trạng thái giữa các lần chạy, nên phải đặt lại trạng thái trước mỗi dòng. Nếu không đặt lại, CER trên 100 dòng kiểm định của một mô hình thử tăng từ 11,64% lên 12,98%.

### 4.3.4. Độ nhạy với cách vẽ

Trước khi có nét viết thật, đề tài đo độ nhạy của mô hình `m1_v2` với cách vẽ bằng dữ liệu VNOnDB. Mỗi ảnh kiểm định được lấy khung xương rồi vẽ lại bằng đúng bộ vẽ của ứng dụng. Bảng {{bang:do-nhay}} ghi CER (2) của giải mã đơn giản trên 400 dòng kiểm định đầu tiên.

| Biến thể của ảnh kiểm định | CER (2) |
| --- | --- |
| Ảnh gốc | 12,12% |
| Độ đậm nhân 0,7 | 12,05% |
| Độ đậm nhân 2 | 16,20% |
| Độ đậm nhân 3 | 19,55% |
| Đen trắng, ngưỡng 0,25 | 38,23% |
| Vẽ lại, khung xương ngưỡng 80, độ dày nét 1,2 | 30,82% |
| Vẽ lại, khung xương ngưỡng 130, độ dày nét 1,2 | 49,84% |

Bảng: CER của mô hình m1_v2 trên các biến thể của ảnh kiểm định {#bang:do-nhay w=70,30 can=t,p}

Theo Bảng {{bang:do-nhay}}, mô hình phụ thuộc nhiều vào độ đậm và độ mềm của nét. Ảnh vẽ lại cho CER khoảng 30%, cao hơn ảnh gốc khoảng 2,5 lần. Con số này bi quan hơn thực tế, vì khung xương làm đứt một số nét mảnh và sinh nhánh thừa, điều mà nét thật trên điện thoại không có. Kết quả này dẫn tới thí nghiệm ảnh vẽ lại ở Bảng {{bang:thi-nghiem}}. Trên toàn bộ tập kiểm định, độ dày nét 1,2 cho CER thấp nhất khi vẽ lại, nên ứng dụng dùng độ dày này.

## 4.4. Chọn mô hình trên nét viết thật

### 4.4.1. Hai buổi thử viết bằng bút

Hai buổi thử ngày 09/11/2026 và 10/11/2026 có 6 người viết bằng bút S Pen trên điện thoại Galaxy S23 Ultra. Sau khi loại các dòng chép khác đề, còn 46 dòng ngắt và 25 dòng liền. Mỗi dòng ngắt dài 15 hoặc 16 âm tiết và chiếm trung vị 4 dòng chữ, tức 3 chỗ nối, nhiều nhất 7 dòng chữ. Hai người viết chữ nhỏ viết hai dòng chữ trong một hàng kẻ khi hàng cao.

Bản đầu của lớp ghép đoạn gán nét vào hàng kẻ chứa tâm nét và gặp hai lỗi trên nét thật. Phần dưới của g và y có tâm nằm ở hàng dưới nên bị gán sang đoạn sau, còn hai dòng chữ trong một hàng kẻ bị chồng lên nhau trong dòng ảo. Đề tài thay bằng cách gán nét theo thứ tự viết ở mục 3.2.2. Với cách gán mới, lớp ghép đoạn tách đúng số dòng chữ ở cả 60 dòng ngắt của hai buổi thử, kể cả các dòng có hai dòng chữ trong một hàng kẻ.

### 4.4.2. So sánh các mô hình

Bảng {{bang:so-sanh}} so sánh các mô hình trên tập kiểm định và trên nét viết thật của hai buổi thử. Mọi cột dùng M2 với bản float16, mô hình ngôn ngữ trên điện thoại, $\alpha = 0{,}45$, $\beta = 4$, độ rộng beam 30 và độ dày nét 1,2. Cột nhận dạng từng hàng là mốc so sánh cho lớp ghép đoạn.

| Mô hình | Kiểm định | Dòng ngắt ghép | Dòng ngắt từng hàng | Dòng liền |
| --- | --- | --- | --- | --- |
| `m1_v2` | 8,22% | 20,28% | 51,13% | 26,80% |
| `m1_cap40` | 7,88% | 21,12% | 36,90% | 25,81% |
| `m1_rr` | 9,28% | 16,51% | 28,15% | 21,31% |
| `m1_rr_cap40` | 10,10% | 18,46% | 24,56% | 23,37% |
| `m1_rr_el` | 12,09% | 21,09% | Không ghi | 24,24% |
| `m0_rr` | 19,57% | 38,05% | 67,48% | 44,16% |
| `m1l_rr` | 7,41% | 15,77% | 25,34% | 20,26% |
| `m1_rr_e100` | 7,73% | 13,57% | Không ghi | 20,63% |
| `m1l_rr_e100` | 6,61% | 14,33% | 22,60% | 19,02% |

Bảng: CER (2) của M2 trên tập kiểm định và nét viết thật của sáu người viết bằng bút {#bang:so-sanh w=24,17,19,21,19 can=t,p,p,p,p}

Theo Bảng {{bang:so-sanh}}, ảnh vẽ lại giảm CER của dòng ngắt ghép từ 20,28% xuống 16,51%, nhưng làm CER của M2 trên tập kiểm định vượt ngưỡng 8,4%, nên `m1_rr` chưa được chọn. Mô hình `m1l_rr` là lần chạy đầu tiên đạt cả hai điều kiện của quy tắc chọn. Huấn luyện 100 epoch giảm tiếp CER trên cả hai loại dữ liệu. So với `m1_rr`, cấu hình `m1l_rr_e100` giảm CER của dòng ngắt ghép 2,18 điểm phần trăm, khoảng tin cậy 95% theo người viết từ 0,73 đến 3,99 điểm phần trăm.

Ghép dòng ảo tốt hơn nhận dạng từng hàng ở mọi mô hình. Với `m1l_rr`, CER của dòng ngắt ghép thấp hơn nhận dạng từng hàng 9,57 điểm phần trăm. Chênh lệch giữa người viết lớn hơn chênh lệch giữa các mô hình: với `m1l_rr`, CER của dòng ngắt ghép trải từ 7,16% đến 26,46% tùy người viết.

### 4.4.3. Độ dao động giữa các hạt giống

Trên nét viết thật, `m1_rr_e100` và `m1l_rr_e100` gần ngang nhau. Để biết chênh lệch có lớn hơn độ dao động do ngẫu nhiên không, đề tài chạy lại hai cấu hình này với hạt giống 2 và 3. Cách chọn được chốt trước khi có kết quả: cấu hình có CER thấp hơn trên nhóm dòng ngắt ghép và dòng liền được chọn nếu hiệu rõ hơn cả độ dao động giữa người viết lẫn độ dao động giữa các hạt giống. Nếu không, đề tài chọn cấu hình có CER của M2 trên tập kiểm định thấp hơn. Bảng {{bang:hat-giong}} ghi kết quả, với trung bình qua ba hạt giống và độ lệch chuẩn mẫu trong ngoặc.

| Chỉ số | M1 | M1 lớn | Hiệu | Khoảng tin cậy theo người viết | Tỷ số theo hạt giống |
| --- | --- | --- | --- | --- | --- |
| Kiểm định, M2 | 7,86% (0,22) | 6,79% (0,16) | -1,07 | Không áp dụng | -6,89, tới hạn 2,87 |
| Dòng ngắt ghép | 14,63% (0,98) | 13,97% (0,40) | -0,66 | -1,13 đến -0,16 | -1,08, tới hạn 3,44 |
| Dòng liền | 21,03% (0,64) | 19,11% (0,27) | -1,92 | -2,53 đến -1,29 | -4,78, tới hạn 3,40 |
| Ngắt ghép và liền | 16,88% (0,83) | 15,78% (0,31) | -1,10 | -1,33 đến -0,87 | -2,17, tới hạn 3,53 |

Bảng: So sánh M1 và M1 lớn qua ba hạt giống, huấn luyện 100 epoch {#bang:hat-giong w=17,15,15,10,22,21 co=12 can=t,p,p,p,g,g}

Theo Bảng {{bang:hat-giong}}, M1 lớn thấp hơn M1 ở mọi chỉ số. Trên nhóm ngắt ghép và liền, hiệu 1,10 điểm phần trăm rõ hơn độ dao động giữa người viết nhưng chưa rõ hơn độ dao động giữa các hạt giống, vì trị tuyệt đối của tỷ số theo phép thử t của Welch là 2,17, dưới giá trị tới hạn 3,53. Trên tập kiểm định, hiệu 1,07 điểm phần trăm vượt giá trị tới hạn. Theo cách chọn đã chốt, đề tài chọn M1 lớn, và mô hình đưa vào ứng dụng là `m1l_rr_e100`.

Kết quả này cũng cho thấy độ dao động giữa các hạt giống trên nét viết thật lớn hơn nhiều so với trên tập kiểm định. Với M1, hai hạt giống chỉ chênh 0,01 điểm phần trăm trên tập kiểm định nhưng chênh 1,93 điểm phần trăm trên dòng ngắt ghép. Vì vậy, các hiệu dưới khoảng 2 điểm phần trăm trên nét viết thật giữa hai lần chạy đơn lẻ không đủ để chọn mô hình.

Đề tài thử thêm M1 lớn huấn luyện 150 epoch với điều kiện chốt trước: CER của M2 trên tập kiểm định dưới 6,31% và CER trên nhóm ngắt ghép và liền không quá 16,40%. Lần chạy này đạt 6,38% và 16,41%, không đạt cả hai điều kiện, nên ứng dụng giữ `m1l_rr_e100`. Lần chạy 150 epoch tốt hơn trên dòng liền nhưng kém hơn trên dòng ngắt ghép, nên tăng số epoch không phải hướng cần thử tiếp.

## 4.5. Dữ liệu viết bằng ngón tay

### 4.5.1. Các đợt thu

Ngày 11/11/2026, đề tài thử ba buổi viết bằng ngón tay trên iPhone của hai người. Sau khi loại 5 dòng chép khác đề hoặc viết dở, còn 29 dòng ngắt và 16 dòng liền. Với mô hình được chọn, CER (2) là 18,56% với dòng ngắt sau khi ghép và 26,00% với dòng liền, so với 14,33% và 19,02% khi viết bằng bút. Với hai người viết, các số này chưa đủ để kết luận, nhưng cho thấy cần đo riêng chữ viết bằng ngón tay. Ba buổi này được dùng như một buổi thử và không tính vào nhóm chỉnh.

Sau đó, đề tài thu dữ liệu viết bằng ngón tay theo quy trình ở mục 3.1.6, trong ba đợt. Bảng {{bang:dot-thu}} ghi quy mô và cách dùng của từng đợt.

| Đợt | Thời gian thu | Số buổi | Buổi đủ điều kiện | Cách dùng |
| --- | --- | --- | --- | --- |
| Đợt thứ nhất | 12/11/2026 đến 15/11/2026 | 10 | 4 buổi nhóm A | Nhóm chỉnh |
| Đợt thứ hai | 16/11/2026 | 5 | 5 buổi nhóm B | Nhóm chỉnh |
| Đợt thứ ba | 17/11/2026 đến 19/11/2026 | 20 | 19 buổi, 10 nhóm A và 9 nhóm B | Tập đánh giá |

Bảng: Các đợt thu viết bằng ngón tay {#bang:dot-thu w=16,27,11,26,20 can=t,t,g,t,t}

Ở đợt thứ nhất, chỉ 4 buổi nhóm A được dùng. Một buổi không được dùng vì số đo bằng thẻ lệch 22% so với thông số của máy, nên hàng kẻ thật chỉ cao khoảng 9,3 mm. Năm buổi còn lại, gồm 2 buổi viết trên máy tính bảng, không có trong bộ dữ liệu được gửi lại cùng đợt thứ hai. Nhóm chỉnh vì vậy gồm 4 buổi nhóm A của đợt thứ nhất và 5 buổi nhóm B của đợt thứ hai. Ở đợt thứ ba, một buổi bị loại vì cả 20 dòng chỉ có hai chữ đầu của câu đề. Năm buổi đo màn hình bằng thẻ có hàng kẻ thật từ 11,6 đến 13,0 mm, lệch 12 mm không quá 10%, nên được giữ.

Người thu chọn Chép đúng cho gần như mọi dòng, nên đề tài rà soát lại từng dòng trên ảnh vẽ từ nét gốc theo mục 3.1.6. Nhóm chỉnh có 12 dòng chép khác đề trên 180 dòng. Tập đánh giá có 42 dòng chép khác đề trên 380 dòng, gồm 26 dòng liền và 16 dòng ngắt. Trong đó có 22 dòng thiếu một hoặc hai từ và 7 dòng viết "sinh nhau" thay cho "sinh nhai". Các dòng này bị loại khỏi phép đo.

### 4.5.2. Kiểm tra cấu hình trên nhóm chỉnh

Bảng {{bang:nhom-chinh}} ghi kết quả của cấu hình triển khai trên 9 buổi của nhóm chỉnh, gồm 87 dòng liền và 81 dòng ngắt sau khi loại dòng chép khác đề, với ba độ dày nét.

| Kịch bản | Độ dày 1,0 | Độ dày 1,2 | Độ dày 1,5 |
| --- | --- | --- | --- |
| Dòng liền | 13,34% | 12,43% | 13,16% |
| Dòng ngắt sau khi ghép | 14,84% | 14,60% | 14,68% |
| Dòng ngắt, nhận dạng từng hàng | Không đo | 26,11% | Không đo |
| Ngắt mô phỏng, 2 chỗ nối | Không đo | 13,60% | Không đo |
| Ngắt mô phỏng, 4 chỗ nối | Không đo | 15,49% | Không đo |
| Ngắt mô phỏng, 6 chỗ nối | Không đo | 17,53% | Không đo |

Bảng: CER (2) của M2 trên nhóm chỉnh theo độ dày nét {#bang:nhom-chinh w=40,20,20,20 can=t,p,p,p}

Theo Bảng {{bang:nhom-chinh}}, độ dày 1,2 cho CER thấp nhất ở cả dòng liền và dòng ngắt ghép, nên ứng dụng giữ độ dày này. Ghép dòng ảo thấp hơn nhận dạng từng hàng 11,51 điểm phần trăm.

Trên nhóm chỉnh, hai dòng liền có nét lạc do chạm nhầm có CER từ 70% đến 89%, vì nét lạc nằm xa dòng chữ làm bước vẽ co chữ thật lại còn vài điểm ảnh. Đề tài thử ba luật lọc nét lạc cho lớp ghép đoạn. Các luật bỏ nét nằm cách dải thân chữ xa hơn $2h$ hoặc cao hơn $5h$, với $h$ là chiều cao thân chữ, và khác nhau ở cách xử lý nét nằm xa hàng chứa nó. Mỗi luật được ghi lại trước khi đo, cùng ba tiêu chí nhận: CER gộp trên nhóm chỉnh phải giảm, CER trên ba buổi thử không được tăng quá 0,2 điểm phần trăm ở mọi kịch bản, và không nét nào của chữ hay dấu bị bỏ hoặc bị chuyển sai hàng. Luật đầu bỏ nhầm 11 nét thật của hàng dưới mà bước gán nét đã xếp lên hàng trên, như dấu phẩy và chấm của chữ i. Hai luật sau chỉ bỏ nét lạc thật và giảm CER của dòng liền trên nhóm chỉnh từ 12,43% xuống 10,75%, nhưng làm CER của dòng ngắt mô phỏng 4 và 6 chỗ nối ở buổi thử viết bằng ngón tay tăng 0,53 và 2,21 điểm phần trăm. Không luật nào đạt cả ba tiêu chí, nên lớp ghép đoạn giữ như ở mục 3.2.2.

Sau bước này, đề tài chốt cấu hình gồm mô hình `m1l_rr_e100` bản float16, $\alpha = 0{,}45$, $\beta = 4$, độ rộng beam 30, độ dày nét 1,2 và lớp ghép đoạn ở mục 3.2.2. Cấu hình này đã có trong ứng dụng từ trước khi nhận đợt thu thứ ba, và được dùng cho mọi kết quả ở mục 4.6.

## 4.6. Kết quả cuối

### 4.6.1. Tập kiểm thử VNOnDB

Tập kiểm thử VNOnDB gồm 1.634 dòng được đo một lần với cấu hình đã chốt. Bảng {{bang:kiem-thu}} ghi kết quả, cùng kết quả của cấu hình này trên tập kiểm định để so. Các nguồn của mốc so sánh không nêu cách tính trung bình, nên bảng ghi cả hai công thức. Dòng cuối là M1 giải mã đơn giản, tức cùng mô hình nhưng không dùng mô hình ngôn ngữ.

| Chỉ số | Tập kiểm định, 1.229 dòng | Tập kiểm thử, 1.634 dòng |
| --- | --- | --- |
| CER (2) của M2 | 6,61% | 5,97% |
| CER (1) của M2 | 5,99% | 5,59% |
| WER (2) của M2 | 17,71% | 16,29% |
| WER (1) của M2 | 16,68% | 15,47% |
| CER (2) của M1 | 8,31% | 7,79% |

Bảng: Kết quả của cấu hình chốt trên tập kiểm định và tập kiểm thử VNOnDB {#bang:kiem-thu w=34,33,33 can=t,p,p}

Theo Bảng {{bang:kiem-thu}}, CER (2) của M2 trên tập kiểm thử là 5,97%, đạt ngưỡng không quá 8,4% và thấp hơn mục tiêu cao hơn 7,6%. WER (2) là 16,29%, đạt ngưỡng không quá 24,2%. Mọi chỉ số trên tập kiểm thử đều thấp hơn trên tập kiểm định, từ 0,40 đến 1,42 điểm phần trăm, nên các lựa chọn làm trên tập kiểm định không cho thấy dấu hiệu quá khớp.

Có 146 trong 1.634 dòng kiểm thử có văn bản giống hệt một dòng huấn luyện, theo mục 3.1.5. Trên 1.488 dòng còn lại, CER (2) của M2 là 6,05%, CER (1) là 5,69% và WER (2) là 16,48%, chỉ cao hơn toàn tập 0,08 điểm phần trăm ở CER (2). Phần văn bản trùng vì vậy gần như không làm kết quả cao hơn thực tế.

So với các mốc dạng ảnh ở Bảng {{bang:moc}}, CER của M2 theo cả hai công thức nằm giữa HTR-VT với 4,26% và OrigamiNet với 7,6%, và WER cũng nằm giữa hai mốc này. Mô hình của đề tài có 2,23 triệu tham số, so với 53,5 triệu của HTR-VT và 39,1 triệu của OrigamiNet. Khi không dùng mô hình ngôn ngữ, CER (2) của M1 là 7,79%, đã thấp hơn mốc 8,4% của GFCN và gần mức 7,6% của OrigamiNet.

### 4.6.2. Tập đánh giá viết bằng ngón tay

Tập đánh giá gồm 19 người viết bằng ngón tay trên điện thoại của mình, được đo một lần với cấu hình đã chốt, sau khi bỏ 42 dòng chép khác đề. Bảng {{bang:danh-gia}} ghi kết quả của hai kịch bản Viết tay thật và Ngắt mô phỏng. Khoảng tin cậy 95% lấy bằng bootstrap 10.000 lần với đơn vị lấy mẫu lại là người viết.

| Kịch bản | Số dòng | CER (2) | Khoảng tin cậy 95% | WER (2) |
| --- | --- | --- | --- | --- |
| Viết tay thật, dòng liền | 164 | 10,34% | 8,07-12,87% | 24,81% |
| Viết tay thật, dòng ngắt sau khi ghép | 174 | 14,69% | 11,77-18,01% | 35,43% |
| Viết tay thật, gộp hai loại dòng | 338 | 12,58% | 10,16-15,35% | 30,28% |
| Viết tay thật, dòng ngắt nhận dạng từng hàng | 174 | 26,83% | 22,48-31,40% | 58,40% |
| Ngắt mô phỏng, 2 chỗ nối | 164 | 11,91% | 9,64-14,45% | 28,40% |
| Ngắt mô phỏng, 4 chỗ nối | 164 | 12,62% | 10,40-15,04% | 29,84% |
| Ngắt mô phỏng, 6 chỗ nối | 164 | 14,44% | 11,68-17,72% | 34,97% |

Bảng: Kết quả trên tập đánh giá viết bằng ngón tay {#bang:danh-gia w=38,11,14,22,15 can=t,p,p,g,p co=12}

Theo Bảng {{bang:danh-gia}}, khi viết bằng ngón tay trên điện thoại, CER (2) của dòng liền là 10,34%, cao hơn tập kiểm thử VNOnDB 4,37 điểm phần trăm. So ghép cặp trên cùng người viết, dòng ngắt sau khi ghép cao hơn dòng liền 4,34 điểm phần trăm, khoảng tin cậy từ 2,43 đến 6,39, và thấp hơn cách nhận dạng từng hàng 12,15 điểm phần trăm, khoảng tin cậy từ 9,80 đến 14,33. Với dòng ngắt mô phỏng, lớp ghép đoạn làm CER tăng 1,57; 2,28 và 4,10 điểm phần trăm so với chính dòng đó viết liền khi có 2, 4 và 6 chỗ nối, với khoảng tin cậy từ 0,48 đến 2,72, từ 1,33 đến 3,23 và từ 2,61 đến 5,66.

CER theo người viết trải rộng: từ 3,10% đến 27,21% với dòng liền và từ 6,84% đến 34,73% với dòng ngắt ghép, và cùng một người viết có CER cao nhất ở cả hai loại dòng. Nhóm đổi chéo A có CER gộp 10,52%, thấp hơn nhóm B với 14,85%. Nếu giữ cả 380 dòng, kể cả các dòng chép khác đề, CER (2) là 10,54% với dòng liền, 15,04% với dòng ngắt sau khi ghép và 27,61% với nhận dạng từng hàng.

### 4.6.3. So sánh với ML Kit

ML Kit có mô hình nhận dạng chữ viết tay tiếng Việt chạy ngay trên điện thoại [@google2026b], nên đề tài chạy ML Kit trên cùng nét viết của tập đánh giá để có mốc so sánh thực tế. Phép đo dùng ML Kit bản 19.0.0, chạy trên máy ảo Android, nên chỉ so độ chính xác, không so thời gian. ML Kit nhận nét kèm thời điểm của từng điểm theo hai cách: nét gốc như người viết, và dòng ảo do lớp ghép đoạn của đề tài tạo ra. Mô hình của đề tài không chạy lại trên tập đánh giá, mà dùng kết quả từng dòng của lần đo ở mục 4.6.2. Bảng {{bang:mlkit}} ghi kết quả.

| Hệ thống | Dòng liền | Dòng ngắt | Gộp | WER (2) gộp |
| --- | --- | --- | --- | --- |
| Hệ thống của đề tài, cấu hình đã chốt | 10,34% | 14,69% | 12,58% | 30,28% |
| ML Kit, nét gốc | 5,24% | 36,61% | 21,39% | 37,83% |
| ML Kit, dòng ảo của lớp ghép đoạn | 5,69% | 6,92% | 6,33% | 20,98% |

Bảng: CER (2) của ML Kit và của hệ thống trên tập đánh giá viết bằng ngón tay {#bang:mlkit w=40,15,15,15,15 can=t,p,p,p,p}

Theo Bảng {{bang:mlkit}}, ML Kit đọc chữ viết bằng ngón tay tốt hơn mô hình của đề tài. So ghép cặp trên cùng người viết, CER (2) của ML Kit với dòng liền thấp hơn 5,10 điểm phần trăm, khoảng tin cậy từ 3,37 đến 7,00. ML Kit đọc trực tiếp nét kèm thứ tự và thời điểm, và đi kèm mô hình ngôn ngữ nặng 20,80 MB, còn mô hình của đề tài chỉ đọc ảnh vẽ lại từ nét và chỉ học từ VNOnDB.

Với dòng ngắt, ML Kit đọc nét gốc rất kém, với CER (2) 36,61%, vì nét của nhiều hàng không được nối thành một dòng. Khi nhận dòng ảo của lớp ghép đoạn, CER (2) của ML Kit với dòng ngắt chỉ còn 6,92%, thấp hơn hệ thống của đề tài 7,77 điểm phần trăm, khoảng tin cậy từ 5,31 đến 10,42. Như vậy lớp ghép đoạn dùng được với một bộ nhận dạng khác và là phần ML Kit không có, còn mô hình nhận dạng là phần hệ thống của đề tài còn kém ML Kit.

## 4.7. Phân tích lỗi

### 4.7.1. Lỗi do dấu thanh và dấu phụ

Bảng {{bang:bo-dau}} ghi CER của M2 sau khi bỏ dấu theo mục 1.5.2, trên tập kiểm định và tập kiểm thử VNOnDB.

| Cách tính | Kiểm định, CER (2) | Kiểm định, CER (1) | Kiểm thử, CER (2) | Kiểm thử, CER (1) |
| --- | --- | --- | --- | --- |
| Giữ nguyên | 6,61% | 5,99% | 5,97% | 5,59% |
| Bỏ dấu thanh | 6,12% | 5,54% | 5,48% | 5,12% |
| Bỏ dấu thanh và dấu phụ | 5,74% | 5,19% | 5,11% | 4,78% |

Bảng: CER của M2 sau khi bỏ dấu trên tập kiểm định và tập kiểm thử VNOnDB {#bang:bo-dau w=28,18,18,18,18 can=t,p,p,p,p}

Theo Bảng {{bang:bo-dau}}, dấu thanh gây khoảng 0,5 điểm phần trăm CER (2) trên cả hai tập, còn dấu thanh và dấu phụ gây khoảng 0,9 điểm phần trăm. Như vậy phần lỗi do dấu chỉ chiếm khoảng một phần bảy tổng số lỗi, nhờ mô hình ngôn ngữ chọn dấu thanh theo ngữ cảnh. So với mô hình `m1_v2`, mô hình được chọn giảm phần lỗi do dấu 0,26 điểm phần trăm, còn CER sau khi bỏ mọi dấu giảm 1,32 điểm phần trăm, nên phần lớn mức giảm CER đến từ việc đọc đúng chữ cái hơn.

Trên tập kiểm định, các cặp ký tự hay nhầm nhất là m và n, n và u, và chữ hoa với chữ thường như C và c, T và t. Lỗi xóa và lỗi chèn hay gặp nhất là dấu cách, với 172 lần xóa và 128 lần chèn, nên một phần lỗi từ đến từ việc tách hoặc nối nhầm âm tiết. Trên 1.229 dòng có 3.511 lỗi thay, 1.009 lỗi xóa và 502 lỗi chèn.

### 4.7.2. Lỗi theo độ dài dòng

Bảng {{bang:do-dai}} ghi CER (2) của M2 theo độ dài dòng trên tập kiểm thử VNOnDB.

| Số ký tự của dòng | Số dòng | CER (2) |
| --- | --- | --- |
| 1-20 | 59 | 16,36% |
| 21-40 | 73 | 10,95% |
| 41-60 | 190 | 4,50% |
| 61-80 | 1.003 | 5,10% |
| Từ 81 | 309 | 6,50% |

Bảng: CER (2) của M2 theo độ dài dòng trên tập kiểm thử VNOnDB {#bang:do-dai w=40,30,30 can=g,p,p}

Theo Bảng {{bang:do-dai}}, dòng ngắn có CER cao hơn hẳn, trong khi dòng từ 41 ký tự trở lên có CER từ 4,50% đến 6,50%. Một nguyên nhân là ảnh của dòng ngắn bị phóng tới chiều cao của khung theo công thức ({{ct:d2-3}}), nên chữ to hơn khoảng 2 lần so với dòng dài, khác với phần lớn dữ liệu huấn luyện. Nguyên nhân này chỉ giải thích được một phần, vì giới hạn chiều cao phần nét ở 40 điểm ảnh giảm CER của dòng từ 21 đến 40 ký tự 5,28 điểm phần trăm, nhưng chỉ giảm 2,01 điểm phần trăm với dòng từ 1 đến 20 ký tự. Dòng ngắn cũng có ít ngữ cảnh cho mô hình ngôn ngữ, và mỗi lỗi chiếm tỷ lệ lớn hơn trong CER của dòng.

### 4.7.3. Lỗi khi viết bằng ngón tay

Trên tập đánh giá, lỗi đến từ ba nguồn chính. Thứ nhất, kiểu chữ: người viết nhanh bằng ngón tay hay viết chữ dính liền và bỏ nét, khác với chữ viết bằng bút của VNOnDB, nên chênh lệch giữa người viết lớn hơn chênh lệch giữa các mô hình. Thứ hai, chỗ nối của dòng ngắt: mỗi chỗ nối làm mô hình mất một phần ngữ cảnh và có thể làm lệch cỡ chữ giữa các đoạn, nên mức tăng CER lớn dần theo số chỗ nối. Thứ ba, nét lạc do chạm nhầm: một chấm nằm xa dòng chữ làm bước vẽ co cả dòng lại, và có thể làm CER của dòng đó vượt 70%.

## 4.8. Mô hình ngôn ngữ mức ký tự

Sau khi chốt cấu hình và chạy các tập cuối, đề tài phân tích lỗi trên nhóm chỉnh. Với chữ viết bằng ngón tay, ứng viên đúng hay bị loại khỏi beam trước khi n-gram âm tiết kịp chấm điểm, vì n-gram âm tiết chỉ chấm khi một âm tiết kết thúc. Đề tài vì vậy thử thêm một mô hình ngôn ngữ mức ký tự, chấm điểm từng ký tự ngay khi beam search thêm ký tự đó vào tiền tố. Thử nghiệm này chỉ dùng tập kiểm định và nhóm chỉnh, nên các kết quả ở mục 4.6 vẫn là kết quả của cấu hình đã chốt.

### 4.8.1. Mô hình và cách dùng

Mô hình là n-gram ký tự, học từ cùng kho văn bản với n-gram âm tiết sau khi loại thêm các câu trùng với câu đề của tập tự thu. Mỗi ký tự trong bảng ký tự của mô hình nhận dạng là một ký hiệu, thêm ba ký hiệu cho ký tự lạ, đầu câu và cuối câu, nên mô hình giữ được chữ hoa và dấu câu. Xác suất được ước lượng theo Kneser-Ney sửa đổi [@kneser1995; @chen1999], rồi tỉa các n-gram hiếm để vừa dung lượng. Bản đưa vào ứng dụng là n-gram bậc 6 nặng 4,10 MB, nên tổng dung lượng các tệp đi kèm là 19,53 MB, vẫn dưới ngưỡng 20 MB.

Bộ giải mã cộng vào điểm của mỗi tiền tố một trọng số nhân log xác suất của từng ký tự theo n-gram ký tự, cùng một điểm thưởng cho mỗi ký tự để không thiên về chuỗi ngắn. N-gram âm tiết vẫn chấm mỗi âm tiết như trước. Trọng số 0,3 và điểm thưởng 1 được chọn trên 410 dòng kiểm định, như cách chọn $\alpha$ và $\beta$.

### 4.8.2. Kết quả

Bảng {{bang:ngram-ky-tu}} ghi kết quả trên 1.229 dòng kiểm định và 168 dòng của nhóm chỉnh. N-gram ký tự 4,10 MB giảm CER (2) 0,37 điểm phần trăm trên tập kiểm định và 2,68 điểm phần trăm trên nhóm chỉnh, còn WER (2) của nhóm chỉnh giảm từ 31,24% xuống 23,81%. Trong 2,68 điểm phần trăm này, khoảng 1,80 điểm là chữ cái đọc đúng hơn, khoảng 0,56 điểm do sửa chữ hoa đặt sai giữa câu, và khoảng 0,32 điểm do thêm dấu chấm cuối câu. N-gram âm tiết không sửa được hai loại lỗi sau, vì nó đưa mọi âm tiết về chữ thường và bỏ dấu câu.

Dòng thứ hai của Bảng {{bang:ngram-ky-tu}} là bản trong ứng dụng, dùng tệp đã lượng tử hóa. Dòng cuối dùng n-gram bậc 8 chưa tỉa nặng 283,68 MB, chỉ để biết mức lợi khi không giới hạn dung lượng.

| Cấu hình | Kiểm định, CER (2) | Kiểm định, WER (2) | Nhóm chỉnh, dòng liền | Nhóm chỉnh, dòng ngắt | Nhóm chỉnh, gộp | Nhóm chỉnh, WER (2) |
| --- | --- | --- | --- | --- | --- | --- |
| Cấu hình đã chốt | 6,61% | 17,71% | 12,43% | 14,60% | 13,48% | 31,24% |
| Thêm n-gram ký tự 4,10 MB | 6,24% | 16,43% | 10,05% | 11,61% | 10,80% | 23,81% |
| Thêm n-gram ký tự bậc 8 chưa tỉa | 5,90% | 15,11% | 9,07% | 9,96% | 9,50% | 20,68% |

Bảng: CER (2) và WER (2) khi thêm n-gram ký tự {#bang:ngram-ky-tu w=28,12,12,12,12,12,12 can=t,p,p,p,p,p,p co=12}

Mức giảm trên nhóm chỉnh lớn hơn nhiều so với tập kiểm định. Câu đề của nhóm chỉnh là câu Wikipedia, cùng loại văn bản với kho văn bản, còn nhãn của VNOnDB khác văn phong và phần lớn là một đoạn của câu. Với văn bản người dùng tự viết, mức lợi vì vậy có thể thấp hơn mức đo trên nhóm chỉnh. Trong ứng dụng, bản Kotlin cho cùng kết quả với bản Python ở cả 168 dòng của nhóm chỉnh.

### 4.8.3. So với ML Kit trên nhóm chỉnh

Cấu hình có n-gram ký tự chỉ được đo trên tập kiểm định và nhóm chỉnh, nên đề tài so cấu hình này với ML Kit trên 168 dòng của nhóm chỉnh, theo Bảng {{bang:mlkit-chinh}}. N-gram ký tự thu hẹp khoảng cách giữa ứng dụng và ML Kit dùng dòng ảo, từ 6,11 xuống 3,43 điểm phần trăm CER (2) gộp. So ghép cặp trên 9 người viết, khoảng tin cậy của hiệu còn lại là từ 1,58 đến 5,14 điểm phần trăm, nên ML Kit dùng dòng ảo vẫn tốt hơn. Nhóm chỉnh chỉ có 9 người viết và dùng cùng câu đề với tập đánh giá, nên phép so sánh này chỉ để tham khảo.

Hai dòng đầu của Bảng {{bang:mlkit-chinh}} lấy từ bài đo chạy cả luồng của ứng dụng trên thiết bị, trùng kết quả của bản Python.

| Hệ thống | Dòng liền | Dòng ngắt | Gộp | WER (2) gộp |
| --- | --- | --- | --- | --- |
| Ứng dụng, cấu hình đã chốt | 12,43% | 14,60% | 13,48% | 31,24% |
| Ứng dụng, có n-gram ký tự | 10,05% | 11,61% | 10,80% | 23,81% |
| ML Kit, nét gốc | 6,70% | 24,83% | 15,44% | 32,77% |
| ML Kit, dòng ảo của lớp ghép đoạn | 8,43% | 6,23% | 7,37% | 22,85% |

Bảng: CER (2) của ứng dụng và của ML Kit trên nhóm chỉnh {#bang:mlkit-chinh w=40,15,15,15,15 can=t,p,p,p,p}

## 4.9. Đối chiếu với mục tiêu

Bảng {{bang:doi-chieu}} đối chiếu kết quả với các mục tiêu ở Bảng {{bang:muc-tieu}}.

| Mục tiêu | Ngưỡng | Kết quả | Đánh giá |
| --- | --- | --- | --- |
| CER trên tập kiểm thử VNOnDB | ≤ 8,4% | 5,97% | Đạt |
| WER trên tập kiểm thử VNOnDB | ≤ 24,2% | 16,29% | Đạt |
| Mục tiêu cao hơn về CER | Tiến gần 7,6% | 5,97% | Đạt |
| CER tăng thêm khi dòng bị ngắt | ≤ 2 điểm phần trăm | 1,57; 2,28 và 4,10 điểm phần trăm với 2, 4 và 6 chỗ nối | Đạt với 2 chỗ nối, chưa đạt với 4 và 6 chỗ nối |
| Tổng dung lượng mô hình và mô hình ngôn ngữ | ≤ 20 MB | 15,43 MB với cấu hình đã chốt, 19,53 MB khi thêm n-gram ký tự | Đạt |
| Thời gian nhận dạng một dòng trên điện thoại thật | ≤ 1 giây | Đã chạy trên máy ảo và một điện thoại cao cấp, theo mục 5.3 | Chưa đo theo cách ở mục 1.5.3 |
| CER khi viết bằng ngón tay | Đo và báo cáo | 10,34% với dòng liền, 14,69% với dòng ngắt ghép | Đã đo |

Bảng: Đối chiếu kết quả với mục tiêu {#bang:doi-chieu w=28,17,33,22 co=12}

Các mục tiêu nhận dạng dòng liền trên VNOnDB đều đạt với mô hình nhỏ, chạy được trên điện thoại. Hướng ghép dòng ảo cho CER thấp hơn rõ so với nhận dạng từng hàng trên cả nét viết bằng bút và bằng ngón tay. Mức tăng khi dòng bị ngắt nằm dưới 2 điểm phần trăm với 2 chỗ nối, nhưng vượt ngưỡng khi dòng bị ngắt nhiều lần, trong khi dòng ngắt thật thường có khoảng 3 chỗ nối. Chữ viết bằng ngón tay trên điện thoại vẫn khó hơn chữ của VNOnDB, với CER của dòng liền trên tập đánh giá cao hơn tập kiểm thử VNOnDB 4,37 điểm phần trăm. So với ML Kit, mô hình nhận dạng của đề tài còn kém hơn, nhưng lớp ghép đoạn là phần giúp cả ML Kit đọc được dòng ngắt.
