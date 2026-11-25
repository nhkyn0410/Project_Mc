# Kế hoạch thí nghiệm

Trạng thái: Nháp

Tài liệu này ghi các thí nghiệm của đề tài, câu hỏi mỗi thí nghiệm trả lời, thứ tự chạy và cách chọn cấu hình cuối. Tài liệu dành cho người chạy thí nghiệm và người viết Chương 4 của báo cáo. Kết quả của từng lần chạy nằm ở `07-nhat-ky-thi-nghiem.md`, còn tài liệu này chỉ ghi kế hoạch và các quyết định rút ra.

## 1. Nguyên tắc

- **Một thay đổi mỗi lần:** mỗi thí nghiệm đổi một yếu tố so với một cấu hình gốc đã có kết quả, để biết thay đổi nào gây ra chênh lệch.
- **Một lần huấn luyện mỗi lúc:** máy huấn luyện không đủ bộ nhớ cho nhiều lần chạy cùng lúc, theo `07-nhat-ky-thi-nghiem.md`, mục 9. Các lần chạy xếp hàng và chạy lần lượt.
- **Hạt giống cố định:** mọi lần chạy dùng hạt giống 1, trừ thí nghiệm hạt giống ở Bảng 2. Trên nét viết thật, hai lần chạy cùng cấu hình có thể chênh gần 2 điểm phần trăm, theo `07-nhat-ky-thi-nghiem.md`, mục 10.9. Chênh lệch nhỏ hơn mức này giữa hai lần chạy đơn lẻ vì vậy chưa đủ để kết luận.
- **Không chạm tập kiểm thử:** tập kiểm thử VNOnDB và tập đánh giá của tập tự thu chỉ được đo một lần ở cuối, theo `02-yeu-cau-va-danh-gia.md`, mục 5.

## 2. Dữ liệu đo

Bảng 1 ghi các tập dữ liệu dùng để so sánh các cấu hình trong lúc phát triển.

Bảng 1: Các tập dữ liệu dùng khi so sánh cấu hình

| Tập | Quy mô | Đo gì |
| --- | --- | --- |
| Tập kiểm định VNOnDB | 1.229 dòng | CER của M1 khi huấn luyện, CER của M2 cho điều kiện ở mục 4 |
| Ảnh vẽ lại của tập kiểm định | 400 dòng đầu, độ dày nét 1,2 | Độ nhạy với bộ vẽ của ứng dụng |
| Nét viết thật của hai buổi thử | 6 người viết bằng bút S Pen, các dòng chép đúng đề | CER của M2 trên dòng ngắt, dòng liền và dòng ngắt mô phỏng, kèm khoảng tin cậy theo người viết |
| Nhóm chỉnh của tập tự thu | Khoảng 10 người (dự kiến), viết bằng ngón tay | Như buổi thử, thay buổi thử khi đã thu |

Nét viết thật của buổi thử chỉ dùng để chỉnh và so sánh. Dữ liệu này không dùng để huấn luyện và không tính vào kết quả cuối.

## 3. Các thí nghiệm

Bảng 2 ghi các thí nghiệm theo thứ tự dự kiến. Cấu hình gốc là `m1_v2`, theo `07-nhat-ky-thi-nghiem.md`, mục 2.

Bảng 2: Các thí nghiệm, câu hỏi và tình trạng

| Thí nghiệm | Thay đổi so với cấu hình gốc | Câu hỏi | Tình trạng |
| --- | --- | --- | --- |
| Ảnh vẽ lại | Thêm ba ảnh vẽ lại cho mỗi dòng, tăng cường độ đậm | Có thu hẹp khoảng cách với nét viết thật không? | Đã đo: tốt hơn rõ trên nét viết thật, nhưng M2 trên tập kiểm định vượt ngưỡng |
| Giới hạn chiều cao phần nét | $H_{\text{nét}} = 40$ | Có giảm CER của dòng ngắn không? | Đã đo: giảm một phần, M2 trên tập kiểm định thấp nhất, không tốt hơn trên nét viết thật |
| Kết hợp | Ảnh vẽ lại và $H_{\text{nét}} = 40$ | Hai thay đổi có cộng dồn không? | Đã đo: không, kém hơn chỉ dùng ảnh vẽ lại |
| Mô hình lớn hơn | Như thí nghiệm ảnh vẽ lại, dùng M1 lớn thay cho M1 | Mô hình lớn hơn có đạt cả ngưỡng trên tập kiểm định và CER thấp trên nét viết thật không? | Đã đo: có. M1 lớn huấn luyện 100 epoch là mô hình được chọn |
| Biến dạng đàn hồi | Như thí nghiệm ảnh vẽ lại, thêm biến dạng đàn hồi biên độ 2 điểm ảnh | Mô hình có đọc kiểu chữ lạ tốt hơn không? | Đã đo: không, kém hơn trên cả tập kiểm định và nét viết thật |
| Huấn luyện lâu hơn | Như thí nghiệm ảnh vẽ lại, 100 epoch thay cho 60 | Mô hình còn cải thiện sau epoch 60 không? | Đã đo: có, tốt hơn rõ trên cả tập kiểm định và nét viết thật |
| M1 lớn huấn luyện lâu hơn | Như thí nghiệm mô hình lớn hơn, 100 epoch thay cho 60 | Huấn luyện lâu hơn có giúp cả M1 lớn không? | Đã đo: có trên tập kiểm định, gần ngang M1 huấn luyện 100 epoch trên nét viết thật |
| Hạt giống | Chạy lại hai cấu hình 100 epoch của M1 và M1 lớn với hạt giống 2 và 3 | Chênh lệch giữa hai cấu hình có lớn hơn độ dao động do ngẫu nhiên không? | Đã đo: trên nét viết thật thì chưa, trên tập kiểm định thì có, M1 lớn tốt hơn |
| Mô hình M0 | Bỏ BiLSTM, giữ cấu hình dữ liệu được chọn | BiLSTM có đáng giữ không? | Đã đo: có, bỏ BiLSTM làm CER tăng khoảng gấp đôi |
| Độ dày nét | Từ 0,8 đến 2 điểm ảnh khi vẽ nét thật | Độ dày nào cho CER thấp nhất? | Đã đo trên buổi thử, đo lại với mô hình được chọn, giữ 1,2 |
| Lớp ghép đoạn | Gán nét theo thứ tự viết | Dòng ảo có tốt hơn nhận dạng từng hàng không? | Đã đo, theo `07-nhat-ky-thi-nghiem.md`, mục 10 |
| Trọng số n-gram | $\alpha$, $\beta$ | Trọng số nào hợp với mô hình được chọn? | Đã chỉnh lại, giữ $\alpha = 0{,}45$ và $\beta = 4$ |
| Lượng tử hóa | Float16 và dynamic range | Bản nào giữ được CER? | Đã chọn float16, kiểm tra lại với mô hình được chọn |
| N-gram ký tự | Thêm n-gram ký tự vào bộ giải mã của cấu hình đã chốt | Chấm điểm từng ký tự có giảm lỗi trên chữ viết bằng ngón tay không? | Đã đo sau khi chốt cấu hình, chỉ trên tập kiểm định và nhóm chỉnh: có. Bản 4,10 MB giảm CER (2) của nhóm chỉnh từ 13,48% xuống 10,80% và đã đưa vào ứng dụng, theo `07-nhat-ky-thi-nghiem.md`, mục 14 |
| So sánh với ML Kit | Chạy ML Kit trên nét gốc và trên dòng ảo của lớp ghép đoạn | Hệ thống của đề tài đứng ở đâu so với ML Kit? | Đã đo: ML Kit đọc chữ tốt hơn, nhưng chỉ đọc được dòng ngắt khi nhận dòng ảo của lớp ghép đoạn, theo `07-nhat-ky-thi-nghiem.md`, mục 15 |

Biến dạng đàn hồi khi tăng cường giúp mô hình gặp nhiều kiểu chữ hơn, theo `ly-thuyet/02-tien-xu-ly-anh.md`, mục 2.3. M1 lớn giữ cấu trúc của M1, nhưng bốn khối tích chập có 48, 96, 192 và 192 bộ lọc, lớp kết nối đầy đủ và mỗi chiều của BiLSTM có 192 ô. Mô hình này có 2.228.945 tham số. Bản float16 của lần chạy `m1l_rr` nặng 4,47 MB, nên tổng dung lượng với `lm.bin` khoảng 15,4 MB, dưới giới hạn 20 MB. Đề tài thử M1 lớn ngay sau thí nghiệm kết hợp, vì lần chạy `m1_rr` vẫn còn cải thiện ở epoch cuối, dấu hiệu mô hình chưa đủ sức học cả ảnh gốc lẫn ảnh vẽ lại. Thí nghiệm kết hợp kém hơn thí nghiệm ảnh vẽ lại, nên ba thí nghiệm mô hình lớn hơn, biến dạng đàn hồi và huấn luyện lâu hơn dựng trên cấu hình của `m1_rr`, theo `07-nhat-ky-thi-nghiem.md`, mục 10.5.

M1 lớn đạt CER 7,41% với M2 trên tập kiểm định và có CER thấp nhất trên nét viết thật của sáu người viết ở hai buổi thử, nên là mô hình được chọn tạm thời, theo `07-nhat-ky-thi-nghiem.md`, mục 10.7. Hàng đợi được tạm dừng ngày 10/11/2026 sau thí nghiệm này, nên hai thí nghiệm biến dạng đàn hồi và huấn luyện lâu hơn chưa có kết quả. Hai thí nghiệm này dùng M1 để so trực tiếp với `m1_rr`. Nếu một thay đổi giúp M1, đề tài chạy lại thay đổi đó với M1 lớn trước khi chốt mô hình.

Hàng đợi chạy tiếp ngày 11/11/2026. Biến dạng đàn hồi không giúp M1, còn huấn luyện 100 epoch giúp rõ, nên đề tài chạy lại thay đổi này với M1 lớn. Hai cấu hình 100 epoch của M1 và M1 lớn gần ngang nhau trên nét viết thật, dù M1 lớn tốt hơn rõ trên tập kiểm định, theo `07-nhat-ky-thi-nghiem.md`, mục 10.8. Đề tài vì vậy đo độ dao động giữa các hạt giống của cả hai cấu hình trước khi chọn.

Với ba hạt giống mỗi cấu hình, M1 lớn thấp hơn M1 1,10 điểm phần trăm trên nét viết thật, nhưng hiệu này chưa rõ hơn độ dao động giữa các hạt giống. Trên tập kiểm định, M1 lớn thấp hơn 1,07 điểm phần trăm và hiệu này rõ hơn độ dao động đó. Theo cách chọn chốt trước ở `07-nhat-ky-thi-nghiem.md`, mục 10.9, đề tài chọn M1 lớn, và lần chạy `m1l_rr_e100` được đưa vào ứng dụng, theo mục 11 của tài liệu đó.

## 4. Thứ tự chạy và cách chọn

1. Chạy lần lượt các thí nghiệm từ ảnh vẽ lại đến huấn luyện lâu hơn của Bảng 2.
2. Với mỗi lần chạy, chuyển sang LiteRT rồi đo trên ba tập đầu của Bảng 1.
3. Chọn cấu hình dữ liệu theo quy tắc chọn mô hình của `02-yeu-cau-va-danh-gia.md`, mục 5: CER của M2 trên tập kiểm định không quá 8,4%, và CER của M2 trên nét viết thật thấp nhất.
4. Chạy M0 với cấu hình dữ liệu đã chọn.
5. Chỉnh $\alpha$ và $\beta$ trên tập kiểm định, đo lại cấu hình triển khai, sinh tệp cho ứng dụng và chạy phép đối chiếu Kotlin.
6. Thu nhóm chỉnh, chỉnh lại tham số của lớp ghép đoạn và độ dày nét, rồi lặp lại bước 3 nếu kết quả đổi thứ tự các cấu hình.
7. Chốt mọi tham số, rồi đo tập kiểm thử VNOnDB và tập đánh giá của tập tự thu, mỗi tập một lần.

Đến ngày 11/11/2026, các bước từ 1 đến 5 đã xong. Bước 6 chờ dữ liệu của nhóm chỉnh, còn bước 7 chạy sau bước 6. Trong lúc chờ, đề tài chạy thử M1 lớn với 150 epoch, theo cách chọn đã chốt trước ở `07-nhat-ky-thi-nghiem.md`, mục 10.11. Lần chạy này xong ngày 13/11/2026 và không đạt hai điều kiện đã chốt, nên ứng dụng giữ `m1l_rr_e100`.

Ngày 15/11/2026, nhóm chỉnh có 5 trên 10 người đủ điều kiện và nhóm kiểm thử có 2 buổi hợp lệ trên 20, theo `07-nhat-ky-thi-nghiem.md`, mục 10.12. Ngày 18/11/2026, bộ dữ liệu mới nâng nhóm chỉnh lên 9 buổi đủ điều kiện, gồm 4 buổi nhóm A và 5 buổi nhóm B, theo mục 10.13 của tài liệu đó. Năm buổi nhóm B do người đã viết ở đợt thu đầu viết lại, nên số người viết khác nhau chưa rõ cho tới khi biết mã cũ của từng người. Ngày 23/11/2026, bước 6 thử bộ lọc nét lạc cho lớp ghép đoạn. Bộ lọc không đạt tiêu chí ghi trước nên lớp ghép đoạn giữ như cũ, theo mục 10.15 đến mục 10.17 của tài liệu đó. Ngày 24/11/2026, đợt thu thứ ba cho 19 buổi đủ điều kiện của 19 người khác nhau, gồm 10 buổi nhóm A và 9 buổi nhóm B, theo mục 10.18 của tài liệu đó. Cùng ngày, đề tài kết thúc bước 6, chốt cấu hình của ứng dụng và dùng 19 buổi này làm tập đánh giá, theo mục 10.19 của tài liệu đó.

Bước 7 xong ngày 24/11/2026, theo `07-nhat-ky-thi-nghiem.md`, mục 12. Trên tập kiểm thử VNOnDB, CER (2) của M2 là 5,97%, đạt ngưỡng 8,4% ở `02-yeu-cau-va-danh-gia.md`, mục 1. Trên tập đánh giá viết bằng ngón tay, CER (2) của M2 là 10,34% với dòng liền và 14,69% với dòng ngắt sau khi ghép.

## 5. Mức tăng cường

Mức tăng cường cuối là cấu hình dữ liệu của `m1_rr`, chốt ở bước 3 của mục 4. Mức này gồm các phép biến đổi hình học và hệ số trộn dày mỏng ở `ly-thuyet/02-tien-xu-ly-anh.md`, mục 4, cộng ba ảnh vẽ lại với độ dày nét 0,8; 1,2 và 1,6 và hệ số độ đậm từ 0,5 đến 2,5. Cấu hình cuối không dùng giới hạn chiều cao phần nét và biến dạng đàn hồi, vì hai thay đổi này không giúp trên nét viết thật, theo `07-nhat-ky-thi-nghiem.md`, mục 10.5 và mục 10.8. Mức này chỉ đổi nếu nhóm chỉnh viết bằng ngón tay đổi thứ tự các cấu hình, theo bước 6 của mục 4.

## 6. Vấn đề chưa chốt

Bảng 3 ghi các điểm có thể làm sai quyết định chọn cấu hình.

Bảng 3: Các vấn đề chưa chốt về thí nghiệm

| Vấn đề | Ảnh hưởng | Hướng xử lý |
| --- | --- | --- |
| Độ dao động giữa các hạt giống trên nét viết thật tới gần 2 điểm phần trăm | So sánh hai lần chạy đơn lẻ trên nét viết thật kém tin cậy | Với thí nghiệm mới, chạy ba hạt giống khi hiệu trên nét viết thật dưới 2 điểm phần trăm và tập kiểm định không phân định được |
| Điều kiện 8,4% trên tập kiểm định có thể loại cấu hình tốt nhất trên nét viết thật | Phải đánh đổi giữa so sánh với công bố và chất lượng trên điện thoại | Ghi cả hai kết quả, quyết định cùng giảng viên hướng dẫn nếu xảy ra |
