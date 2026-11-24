# Nhật ký thí nghiệm

Trạng thái: Nháp

Tài liệu này ghi môi trường, cấu hình và kết quả của từng lần chạy, để mọi số liệu đã đo trong báo cáo đều chỉ ra được lần chạy tạo ra nó. Tài liệu dành cho người chạy thí nghiệm và người viết Chương 4 của báo cáo. Tập kiểm thử chưa được chạy lần nào, theo `02-yeu-cau-va-danh-gia.md`, mục 5.

## 1. Môi trường

Bảng 1 ghi môi trường của mọi lần chạy trong tài liệu này. Mã nguồn nằm trong thư mục `training/` của kho mã, còn dữ liệu và kết quả nằm trong `~/vnhw/` trên máy huấn luyện.

Bảng 1: Môi trường chạy

| Thành phần | Giá trị |
| --- | --- |
| Card đồ họa | NVIDIA GeForce RTX 4050 Laptop, 6 GB |
| Hệ điều hành | Ubuntu chạy trong Windows 11 |
| Thư viện huấn luyện | TensorFlow 2.21.0, Keras 3.15.1 |
| Thư viện chuyển đổi | tf-keras 2.21.0 |
| Bộ ký tự | 160 ký tự của tập huấn luyện và tập kiểm định, cộng nhãn trống |

## 2. Các lần huấn luyện

Mọi lần chạy dùng chung cấu hình sau, trừ khi Bảng 2 ghi khác:

- **Mô hình:** M1 theo `01-mo-ta-de-tai.md`, mục 7.3, có 1.005.761 tham số tính cả BatchNorm.
- **Đầu vào:** ảnh theo `03-du-lieu.md`, mục 3.3, rộng 512, cao 64 điểm ảnh.
- **Huấn luyện:** Adam, tốc độ học giảm theo hàm cosin từ 0,001 xuống 0,00001, lô 32 dòng, dropout 0,5, cắt chuẩn gradient ở 5, hạt giống 1.
- **Đo:** giải mã đơn giản theo `ly-thuyet/05-ctc.md`, mục 2.5, không dùng n-gram, trên 1.229 dòng kiểm định.

Bảng 2 ghi kết quả của epoch tốt nhất. Các cột (1) và (2) là công thức tính trong `02-yeu-cau-va-danh-gia.md`, mục 2.1. CER là tỷ lệ lỗi ký tự và WER là tỷ lệ lỗi từ.

Bảng 2: Kết quả huấn luyện trên tập kiểm định

| Lần chạy | Số epoch | Thay đổi so với cấu hình chung | CER (2) | WER (2) | CER (1) | WER (1) |
| --- | --- | --- | --- | --- | --- | --- |
| `m1_base` | 50 | Tăng cường có lỗi, xem mục 8 | 11,97% | 36,69% | 11,03% | 34,86% |
| `m1_v2` | 60 | Đã sửa lỗi tăng cường, ảnh có lề 8 điểm ảnh | 11,06% | 33,26% | 9,93% | 31,21% |
| `m1_rr` | 60 | Như `m1_v2`, thêm ba ảnh vẽ lại cho mỗi dòng, độ đậm nhân từ 0,5 đến 2,5 | 12,20% | 36,98% | 11,40% | 35,39% |
| `m1_cap40` | 60 | Như `m1_v2`, giới hạn chiều cao phần nét ở 40 điểm ảnh | 10,62% | 32,26% | 9,84% | 30,74% |
| `m1_rr_cap40` | 60 | Như `m1_rr`, giới hạn chiều cao phần nét ở 40 điểm ảnh | 12,91% | 37,99% | 12,12% | 36,72% |
| `m1l_rr` | 60 | Như `m1_rr`, dùng M1 lớn có 2.228.945 tham số | 9,88% | 30,07% | 9,10% | 28,55% |
| `m1_rr_el` | 60 | Như `m1_rr`, thêm biến dạng đàn hồi biên độ 2 điểm ảnh | 15,48% | 45,18% | 14,33% | 43,08% |
| `m1_rr_e100` | 100 | Như `m1_rr`, huấn luyện 100 epoch | 10,04% | 30,39% | 9,28% | 28,93% |
| `m0_rr` | 60 | Như `m1_rr`, dùng M0 không có BiLSTM, có 327.745 tham số | 24,68% | 64,22% | 21,73% | 61,20% |
| `m1l_rr_e100` | 100 | Như `m1l_rr`, huấn luyện 100 epoch | 8,27% | 25,09% | 7,70% | 23,98% |
| `m1_rr_e100_s2` | 100 | Như `m1_rr_e100`, hạt giống 2 | 10,08% | 30,61% | 9,45% | 29,32% |
| `m1l_rr_e100_s2` | 100 | Như `m1l_rr_e100`, hạt giống 2 | 8,73% | 26,20% | 7,98% | 24,71% |
| `m1_rr_e100_s3` | 100 | Như `m1_rr_e100`, hạt giống 3 | 10,46% | 30,83% | 9,47% | 29,11% |
| `m1l_rr_e100_s3` | 100 | Như `m1l_rr_e100`, hạt giống 3 | 8,51% | 25,37% | 7,89% | 24,14% |
| `m1l_rr_e150` | 150 | Như `m1l_rr_e100`, huấn luyện 150 epoch, theo mục 10.11 | 7,95% | 24,14% | 7,30% | 22,61% |

Thời gian huấn luyện đo được là khoảng 30 giây mỗi epoch. Lần chạy `m1_base` đạt kết quả tốt nhất ở epoch cuối cùng. Lần chạy `m1_v2` đạt kết quả tốt nhất ở epoch 56. Lần chạy `m1_rr` vẽ lại ảnh huấn luyện theo `ly-thuyet/02-tien-xu-ly-anh.md`, mục 4, với độ dày nét 0,8; 1,2 và 1,6, và mỗi lần dùng một dòng thì chọn ngẫu nhiên một trong bốn ảnh. Lần chạy này đạt kết quả tốt nhất ở epoch cuối cùng, nên có thể còn cải thiện nếu huấn luyện lâu hơn. Lần chạy `m1_cap40` cũng đạt kết quả tốt nhất ở epoch cuối cùng, còn lần chạy `m1_rr_cap40` đạt kết quả tốt nhất ở epoch 52. Lần chạy `m1l_rr` dùng M1 lớn, mô tả ở `05-ke-hoach-thi-nghiem.md`, mục 3. Lần chạy này mất khoảng 70 giây mỗi epoch và đạt kết quả tốt nhất ở epoch 56.

Ba lần chạy `m1_rr_el`, `m1_rr_e100` và `m0_rr` chạy ngày 11/11/2026, mỗi epoch mất lần lượt khoảng 35, 31 và 26 giây. Hai lần chạy `m1_rr_el` và `m1_rr_e100` đạt kết quả tốt nhất ở epoch cuối cùng, còn `m0_rr` ở epoch 58. Với `m1_rr_e100`, CER (2) giảm từ 11,24% ở epoch 60 xuống 10,27% ở epoch 85, rồi chỉ giảm thêm 0,23 điểm phần trăm trong 15 epoch cuối, nên đường học đã gần phẳng. Ở epoch 60, khi tốc độ học còn lớn, lần chạy này đã thấp hơn kết quả cuối của `m1_rr` 0,96 điểm phần trăm.

Lần chạy `m1l_rr_e100` chạy sau ba lần chạy trên, mỗi epoch mất khoảng 42 giây, và đạt kết quả tốt nhất ở epoch 97. CER (2) giảm từ 9,33% ở epoch 60 xuống 8,42% ở epoch 85, rồi chỉ giảm thêm 0,14 điểm phần trăm tới epoch 97. Đường học của hai lần chạy 100 epoch có vài epoch CER tăng vọt khi tốc độ học còn lớn, ví dụ 48,75% ở epoch 31 của `m1l_rr_e100`, rồi trở lại mức cũ ngay ở epoch sau. Các epoch này không được chọn, vì mỗi lần chạy chỉ giữ trọng số của epoch có CER (2) thấp nhất.

Bốn lần chạy có đuôi `_s2` và `_s3` lặp lại `m1_rr_e100` và `m1l_rr_e100` với hạt giống khác, theo mục 10.9. Cả bốn lần chạy đạt kết quả tốt nhất từ epoch 91 trở đi. Trên tập kiểm định, CER (2) của ba hạt giống chênh nhau không quá 0,42 điểm phần trăm với M1 và 0,46 điểm phần trăm với M1 lớn.

Lần chạy `m1l_rr_e150` chạy ngày 13/11/2026, theo mục 10.11, cũng mất khoảng 42 giây mỗi epoch và đạt kết quả tốt nhất ở epoch 128. Vì tốc độ học giảm theo hàm cosin trải trên 150 epoch, lần chạy này đi chậm hơn `m1l_rr_e100` ở cùng epoch: CER (2) là 10,44% ở epoch 60 và 8,47% ở epoch 100, so với 9,33% và 8,38% của `m1l_rr_e100`. Sau epoch 100, CER (2) giảm tiếp xuống 7,95% ở epoch 128, rồi dao động từ 8,01% đến 8,14% trong 20 epoch cuối, nên đường học đã phẳng. So với `m1l_rr_e100`, thêm 50 epoch giảm CER (2) 0,32 điểm phần trăm và WER (2) 0,95 điểm phần trăm trên tập kiểm định với giải mã đơn giản. Mức giảm này lớn hơn độ lệch chuẩn 0,23 điểm phần trăm của CER (2) giữa ba hạt giống của `m1l_rr_e100`, nhưng chỉ là một lần chạy, và cách chọn ở mục 10.11 dựa vào M2.

## 3. Phép học thuộc

Phép học thuộc của Cổng 1 huấn luyện trên 100 dòng đầu, không tăng cường, không dropout, và đo trên chính 100 dòng đó. Lần chạy `overfit100` dùng 150 epoch với lô 16 dòng, tức 900 bước, và đạt CER (2) 27,55%. Lần chạy `overfit100_b` tăng lên 600 epoch, tức 3.600 bước, và đạt CER (2) 0% ở epoch 365. Phép học thuộc của Cổng 1 đạt yêu cầu không quá 1%.

## 4. Bộ giải mã

Bảng 3 ghi kết quả của mô hình `m1_v2` với từng cách giải mã, trên 1.229 dòng kiểm định. Lần đo đầu dùng n-gram có cả câu của tập kiểm định và cho CER (2) 8,11%, nên đề tài học lại n-gram sau khi loại các câu đó, cùng các câu của tập kiểm thử và câu đề của công cụ thu. Bảng 3 chỉ ghi n-gram đã loại. Trọng số $\alpha$ và $\beta$ chọn trên 410 dòng kiểm định.

Bảng 3: Kết quả các cách giải mã mô hình `m1_v2` trên tập kiểm định

| Cách giải mã | CER (2) | WER (2) | CER (1) | WER (1) |
| --- | --- | --- | --- | --- |
| Giải mã đơn giản | 11,06% | 33,24% | 9,93% | 31,19% |
| Beam search rộng 30, không n-gram | 10,75% | 32,63% | 9,71% | 30,70% |
| M2: beam search rộng 10, n-gram, $\alpha = 0{,}45$, $\beta = 4$ | 8,65% | 23,35% | 7,63% | 21,65% |
| M2: beam search rộng 20 | 8,31% | 22,45% | 7,37% | 20,78% |
| M2: beam search rộng 30 | 8,20% | 22,06% | 7,24% | 20,38% |
| M2: beam search rộng 50 | 8,10% | 21,79% | 7,15% | 20,14% |

Bảng 3 cho thấy n-gram giảm CER (2) từ 10,75% xuống 8,20%, tức 2,55 điểm phần trăm. Đề tài chọn độ rộng 30, vì tăng lên 50 chỉ giảm thêm 0,10 điểm phần trăm. Bản đo này dùng mô hình Keras và n-gram chưa nén. Kho n-gram gồm 1.503.954 câu, có 30.000 âm tiết phủ 98,64% số âm tiết của kho.

## 5. Chuyển đổi sang LiteRT

Bảng 4 ghi kết quả chuyển đổi mô hình `m1_v2`, đo trên 100 dòng kiểm định lấy cách đều và giải mã đơn giản. Thời gian đo trên CPU của máy huấn luyện với 4 luồng, chưa phải thời gian trên điện thoại.

Bảng 4: Kết quả chuyển đổi mô hình `m1_v2` sang LiteRT

| Bản | Dung lượng | CER (2) | Số dòng giống bản Keras | Thời gian trung vị một dòng |
| --- | --- | --- | --- | --- |
| Keras | Không đo | 11,12% | 100 | Không đo |
| LiteRT, chưa lượng tử hóa | 4,03 MB | 11,17% | 94 | 18,5 ms |
| LiteRT, lượng tử hóa float16 | 2,03 MB | 11,17% | 94 | 16,2 ms |
| LiteRT, lượng tử hóa dynamic range | 1,03 MB | 11,73% | 26 | 12,3 ms |

Theo Bảng 4, lượng tử hóa dynamic range làm CER tăng 0,61 điểm phần trăm so với bản Keras trên 100 dòng này, còn float16 không làm tăng so với bản chưa lượng tử hóa. Bảng 5 ghi kết quả của cấu hình triển khai trên cả 1.229 dòng kiểm định, gồm mô hình LiteRT, `lm.bin`, $\alpha = 0{,}45$, $\beta = 4$ và độ rộng 30.

Bảng 5: Kết quả của cấu hình triển khai trên tập kiểm định

| Bản mô hình | CER (2) | WER (2) | CER (1) | WER (1) | So với ngưỡng 8,4% và 24,2% |
| --- | --- | --- | --- | --- | --- |
| Dynamic range | 8,56% | 22,80% | 7,54% | 21,10% | Chưa đạt CER |
| Float16 | 8,22% | 22,03% | 7,23% | 20,34% | Đạt |

Đề tài chọn float16, vì dynamic range không đạt ngưỡng CER, còn 2,03 MB vẫn nằm trong giới hạn dung lượng. Hai điểm sau là yêu cầu bắt buộc khi triển khai:

- **Phải chuyển qua tf-keras:** lớp LSTM của Keras 3 chuyển thành vòng lặp có biến và lỗi khi chạy. Mã trong `training/export_tflite.py` dựng lại mô hình bằng tf-keras và chép trọng số sang, nên tệp dùng toán tử LSTM gốc của LiteRT.
- **Phải đặt lại trạng thái trước mỗi dòng:** toán tử LSTM của LiteRT giữ trạng thái giữa các lần chạy. Với mô hình `m1_base`, nếu không đặt lại thì CER trên 100 dòng tăng từ 11,64% lên 12,98%.

## 6. Phân tích lỗi

Phần này phân tích kết quả của M2 trên tập kiểm định, với mô hình `m1_v2`, $\alpha = 0{,}45$, $\beta = 4$, độ rộng 30. Bảng 6 ghi CER sau khi bỏ dấu, theo `02-yeu-cau-va-danh-gia.md`, mục 2.3.

Bảng 6: CER của M2 sau khi bỏ dấu trên 1.229 dòng kiểm định

| Cách tính | CER (2) | CER (1) |
| --- | --- | --- |
| Giữ nguyên | 8,20% | 7,24% |
| Bỏ dấu thanh | 7,51% | 6,62% |
| Bỏ dấu thanh và dấu phụ | 7,06% | 6,20% |

Theo Bảng 6, dấu thanh gây 0,69 điểm phần trăm, còn dấu thanh và dấu phụ gây 1,14 điểm phần trăm. Phần lớn lỗi còn lại là nhầm chữ cái, hay gặp nhất là cặp m và n, cặp n và u, và nhầm chữ hoa với chữ thường. Trên 1.229 dòng có 4.007 lỗi thay, 1.522 lỗi xóa và 539 lỗi chèn.

Bảng 7 ghi CER theo độ dài dòng của mô hình `m1_v2` và năm lần chạy sau. Năm cột sau dùng bản float16 và `lm.bin`, theo mục 10.5. Dòng ngắn có CER cao hơn hẳn, trong khi dòng từ 41 ký tự trở lên có CER gần nhau.

Bảng 7: CER (2) của M2 theo độ dài dòng trên tập kiểm định

| Số ký tự của dòng | Số dòng | `m1_v2` | `m1_cap40` | `m1_rr` | `m1l_rr` | `m1_rr_e100` | `m1l_rr_e100` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1-20 | 44 | 29,63% | 27,62% | 29,30% | 22,91% | 25,51% | 22,44% |
| 21-40 | 61 | 17,61% | 12,33% | 16,33% | 12,20% | 12,40% | 10,89% |
| 41-60 | 134 | 6,55% | 6,44% | 7,62% | 5,94% | 6,40% | 5,70% |
| 61-80 | 735 | 6,58% | 6,50% | 7,82% | 6,29% | 6,53% | 5,51% |
| Từ 81 | 255 | 7,77% | 8,16% | 9,21% | 7,61% | 7,70% | 6,52% |

Nguyên nhân dự kiến là ảnh của dòng ngắn bị phóng tới chiều cao của khung, nên chữ to hơn khoảng 2 lần so với dòng dài, theo `ly-thuyet/02-tien-xu-ly-anh.md`, mục 3. Theo Bảng 7, giới hạn chiều cao phần nét ở 40 điểm ảnh giảm CER của dòng từ 21 đến 40 ký tự 5,28 điểm phần trăm, nhưng dòng từ 1 đến 20 ký tự chỉ giảm 2,01 điểm phần trăm. Giả thuyết vì vậy chỉ đúng một phần. Ảnh vẽ lại làm tăng CER chủ yếu ở dòng từ 41 ký tự trở lên, nên giới hạn chiều cao phần nét khó bù được phần tăng này.

Mô hình `m1l_rr` có CER thấp hơn `m1_rr` ở mọi nhóm độ dài. Mức giảm lớn nhất ở dòng ngắn: 6,39 điểm phần trăm với dòng từ 1 đến 20 ký tự và 4,13 điểm phần trăm với dòng từ 21 đến 40 ký tự. Với dòng từ 41 ký tự trở lên, mức giảm từ 1,53 đến 1,68 điểm phần trăm, đủ bù phần tăng do ảnh vẽ lại.

Huấn luyện 100 epoch giảm CER của `m1_rr` ở mọi nhóm độ dài, từ 1,22 đến 3,93 điểm phần trăm, và mức giảm cũng lớn nhất ở dòng ngắn. Dù vậy, `m1_rr_e100` vẫn cao hơn `m1l_rr` ở mọi nhóm, nhiều nhất là 2,60 điểm phần trăm với dòng từ 1 đến 20 ký tự.

Mô hình `m1l_rr_e100` có CER thấp nhất ở mọi nhóm độ dài. So với `m1l_rr`, huấn luyện 100 epoch giảm CER từ 0,24 đến 1,31 điểm phần trăm tùy nhóm. So với `m1_rr_e100`, M1 lớn giảm nhiều nhất ở dòng từ 1 đến 20 ký tự, 3,07 điểm phần trăm, còn các nhóm khác giảm từ 0,70 đến 1,51 điểm phần trăm.

## 7. Độ nhạy với cách vẽ

Tập tự thu chưa có, nên đề tài đo độ nhạy của mô hình `m1_v2` với cách vẽ bằng dữ liệu VNOnDB. Mã `training/rerender.py` lấy khung xương của nét trên ảnh gốc, rồi vẽ lại bằng đúng bộ vẽ của ứng dụng. Bảng 8 ghi CER (2) của giải mã đơn giản trên 400 dòng kiểm định đầu tiên.

Bảng 8: CER của mô hình `m1_v2` trên các biến thể của ảnh kiểm định

| Biến thể | CER (2) |
| --- | --- |
| Ảnh gốc | 12,12% |
| Độ đậm nhân 0,7 | 12,05% |
| Độ đậm nhân 1,3 | 13,07% |
| Độ đậm nhân 2 | 16,20% |
| Độ đậm nhân 3 | 19,55% |
| Đen trắng, ngưỡng 0,25 | 38,23% |
| Đen trắng, ngưỡng 0,4 | 51,00% |
| Vẽ lại, khung xương ngưỡng 80, độ dày nét 1,2 | 30,82% |
| Vẽ lại, khung xương ngưỡng 100, độ dày nét 1,2 | 32,51% |
| Vẽ lại, khung xương ngưỡng 130, độ dày nét 1,2 | 49,84% |
| Vẽ lại, làm mờ trước khi lấy khung xương | 46,84% |

Theo Bảng 8, mô hình phụ thuộc nhiều vào độ đậm và độ mềm của ảnh. Ảnh vẽ lại cho CER khoảng 30%, cao hơn ảnh gốc khoảng 2,5 lần. Con số này bi quan hơn thực tế, vì khung xương làm đứt một số nét mảnh và sinh nhánh thừa, điều mà nét thật trên điện thoại không có. Đề tài vì vậy không coi mô hình `m1_v2` là bản cuối, và cần huấn luyện lại trên cả ảnh gốc lẫn ảnh vẽ lại, theo mục 9.

Trên toàn bộ 1.229 dòng kiểm định, với khung xương ngưỡng 100, độ dày nét 1,2 cho CER (2) thấp nhất là 29,75%, so với 31,16% ở độ dày 0,8. Ứng dụng vì vậy dùng độ dày 1,2.

## 8. Lỗi đã phát hiện

Bảng 9 ghi các lỗi tìm thấy trong quá trình chạy, để không lặp lại.

Bảng 9: Các lỗi đã phát hiện

| Lỗi | Dấu hiệu | Cách sửa |
| --- | --- | --- |
| Tăng cường phóng ngang tới 8% làm mất phần cuối dòng, trong khi nhãn vẫn đủ ký tự | Mô hình `m1_base` hay bỏ các ký tự cuối dòng | Thêm lề 8 điểm ảnh ở hai bên, giới hạn hệ số co giãn ngang ở 1,02, co giãn quanh tâm khung |
| Lớp ghép đoạn gán nét theo tâm nét và đường kẻ | Trên nét thật, chân chữ bị đẩy sang đoạn sau, hai dòng chữ trong một hàng kẻ bị chồng lên nhau | Gán nét theo thứ tự viết, theo `04-thiet-ke-he-thong.md`, mục 2.1 |
| Buổi thu nhập chiều rộng màn hình 50 mm, trong khi màn hình rộng khoảng 73 mm | Hàng kẻ cao hơn dự định khoảng 1,46 lần, người viết viết hai dòng chữ trong một hàng | Công cụ thu cảnh báo khi chiều rộng nhập vào không hợp lý |

## 9. Các lần chạy bị dừng hoặc không chạy

Bảng 10 ghi các lần chạy bị dừng giữa chừng hoặc không chạy, và cách xử lý. Ba lần chạy đồng thời `m1_cap40`, `m1_rr` và `m0_v1b` bị hệ thống dừng ngày 10/11/2026 vì máy sắp hết bộ nhớ. Từ đó, các lần chạy xếp hàng và chạy lần lượt, mỗi lúc một lần, và ba thư mục chạy dở được xóa để chạy lại từ đầu. Hàng đợi được tạm dừng ngày 10/11/2026 sau khi `m1l_rr` xong, rồi chạy tiếp ngày 11/11/2026. Mã huấn luyện không chạy tiếp được từ giữa chừng, nên mỗi lần chạy bị dừng đều được xóa thư mục chạy dở và chạy lại từ đầu.

Bảng 10: Các lần chạy bị dừng hoặc không chạy

| Lần chạy | Mục đích | Tình trạng |
| --- | --- | --- |
| `m1_rr_el` | Như `m1_rr`, thêm biến dạng đàn hồi biên độ 2 điểm ảnh | Bị dừng ở epoch 11 khi tạm dừng hàng đợi và ở epoch 10 khi máy tắt. Đã chạy lại từ đầu ngày 11/11/2026, kết quả ở mục 2 |
| `m1_rr_e100` | Như `m1_rr`, huấn luyện 100 epoch | Đã chạy ngày 11/11/2026, kết quả ở mục 2 |
| `m1_rr_cap_w768` | Như `m1_rr_cap40`, với khung rộng 768 điểm ảnh | Không chạy, vì giới hạn chiều cao phần nét không giúp khi kết hợp với ảnh vẽ lại, theo mục 10.5 |
| `m0_v1` | Mô hình cơ sở M0, không có BiLSTM | Dừng ở epoch 49 trên 60. Thay bằng `m0_rr`, dùng cấu hình dữ liệu của `m1_rr`, kết quả ở mục 2 |
| `m1l_rr_e150` | Như `m1l_rr_e100`, huấn luyện 150 epoch, theo mục 10.11 | Bị hệ thống dừng ở epoch 47 trên 150 ngày 12/11/2026, vì máy sắp hết bộ nhớ. Đã xóa thư mục chạy dở và chạy lại từ đầu ngày 13/11/2026, kết quả ở mục 2 và mục 10.11 |

## 10. Thử trên nét viết thật

### 10.1. Dữ liệu thử

Đề tài thử trên hai tệp do công cụ `tools/thu-net/` thu ngày 09/11/2026, theo giao thức thử. Hai người viết có mã K01 và P01, cùng viết bằng bút S Pen trên điện thoại Galaxy S23 Ultra. Bảng 11 ghi quy mô và các vấn đề của hai tệp.

Bảng 11: Hai tệp nét viết thật của buổi thử

| Người viết | Dòng ngắt | Dòng liền | Vấn đề |
| --- | --- | --- | --- |
| K01 | 10 | 5 | 1 dòng thêm chữ "mưa" không có trong đề |
| P01 | 10 | 1 | Tệp bị cắt cụt, chỉ đọc được 11 dòng đầu. 7 dòng viết tắt, ví dụ "hs", "vc", "HN", "11h" |

Hai buổi thu đều nhập chiều rộng màn hình là 50 mm. Màn hình của máy rộng khoảng 73 mm, ước lượng từ đường chéo 6,8 inch và tỷ lệ 19,3:9. Vì vậy, hàng ghi là 10 mm thực tế cao khoảng 14,6 mm, còn hàng ghi là 14 mm cao khoảng 20,4 mm. Với hàng cao khoảng 20,4 mm, K01 viết hai dòng chữ trong một hàng kẻ.

Người thu đã đánh dấu chỗ ngắt trên công cụ thu nhưng chưa đánh dấu dòng chép khác đề, nên đề tài tự rà soát bằng cách xem hình nét gốc của từng dòng. Các dòng chép khác đề trong Bảng 11 được ghi vào một tệp rà soát riêng, không sửa tệp gốc, và bị loại khỏi phép đo chính. Sau khi loại, còn 18 dòng: 13 dòng ngắt, gồm 9 dòng của K01 và 4 dòng của P01, cùng 5 dòng liền của K01.

Mỗi dòng ngắt dài 15 hoặc 16 âm tiết và chiếm từ 4 đến 7 hàng chữ, trung vị 4 hàng với K01 và 6 hàng với P01. Mỗi hàng chữ có trung bình từ 2,7 đến 3,6 âm tiết. Số hàng này nhiều hơn mức 2 đến 3 hàng mà bộ mô phỏng dự kiến ban đầu, nên bộ mô phỏng chuyển sang cắt 2, 4 và 6 lần.

### 10.2. Lớp ghép đoạn trên nét thật

Bản đầu của lớp ghép đoạn gán nét vào hàng kẻ chứa tâm nét. Trên nét thật, bản này gặp hai lỗi:

- **Chân chữ vượt đường kẻ:** người viết đặt chân chữ trên đường kẻ, nên phần dưới của g và y là nét riêng có tâm nằm ở hàng dưới. Phần này bị gán sang hàng dưới và hiện ở đầu đoạn sau.
- **Hai dòng chữ trong một hàng kẻ:** hai dòng chữ bị gán vào cùng một đoạn, nên nằm chồng lên nhau trong dòng ảo và bị co nhỏ.

Đề tài thay bằng cách gán nét theo thứ tự viết và thêm bước thu khoảng trống quá lớn, theo `04-thiet-ke-he-thong.md`, mục 2. Bản đầu của cách gán mới còn tách nhầm ở dấu nặng viết sau và gộp nhầm khi hàng chỉ có một từ ngắn, nên đề tài sửa thêm các quy tắc ở `04-thiet-ke-he-thong.md`, mục 2.1. Với bản sau khi sửa, cả 20 dòng ngắt đều được tách đúng khi kiểm tra bằng mắt, kể cả 2 dòng có hai dòng chữ trong một hàng kẻ. Trên 90 dòng ngắt mô phỏng từ 6 dòng liền, mỗi dòng cắt 2, 4 hoặc 6 lần với 5 hạt giống, chỉ 1 dòng bị tách sai số đoạn. Bản Kotlin cho cùng kết quả với bản Python trên bộ mẫu đối chiếu mới, gồm cả chân chữ, nét dấu viết sau và khoảng trống lớn.

### 10.3. Kết quả

Bảng 12 ghi CER (2) của mô hình `m1_v2` bản float16 trên hai tệp, với độ dày nét 1,2. M2 dùng `lm.bin`, $\alpha = 0{,}45$, $\beta = 4$ và độ rộng 30. Dòng liền là các dòng viết trên khung cuộn ngang. "Bản cũ" và "bản mới" là hai bản của lớp ghép đoạn.

Bảng 12: CER (2) trên nét viết thật của hai người viết, mô hình `m1_v2`

| Kịch bản | Bản cũ, mọi dòng, M2 | Bản mới, mọi dòng, M2 | Bản mới, dòng chép đúng đề, M1 | Bản mới, dòng chép đúng đề, M2 |
| --- | --- | --- | --- | --- |
| Dòng ngắt, ghép thành dòng ảo | 42,22% | 25,31% | 25,66% | 21,09% |
| Dòng ngắt, nhận dạng từng hàng rồi nối | 60,48% | 56,69% | 54,88% | 53,96% |
| Dòng liền | 39,65% | 38,33% | 40,26% | 38,53% |

Hai cột "mọi dòng" tính trên 20 dòng ngắt và 6 dòng liền, hai cột "dòng chép đúng đề" tính trên 13 dòng ngắt và 5 dòng liền. Trên các dòng chép đúng đề, WER (2) của M2 là 54,36% khi ghép và 93,56% khi nhận dạng từng hàng. Bộ mô phỏng với 2, 4 và 6 chỗ nối trên 5 dòng liền cho CER (2) của M2 từ 35,18% đến 38,11% khi ghép, và từ 59,52% đến 62,93% khi nhận dạng từng hàng. Với M1 trên dòng ngắt chép đúng đề, độ dày nét 1,0 cho CER (2) 25,21%, độ dày 1,2 cho 25,66% và độ dày 1,5 cho 27,09%. Chênh lệch này nhỏ so với cỡ mẫu, nên ứng dụng giữ độ dày 1,2.

### 10.4. Nhận xét

- **Dòng ảo tốt hơn nhận dạng từng hàng:** với M2, ghép dòng cho CER chưa bằng một nửa so với nhận dạng từng hàng rồi nối. Đây là kết quả đầu tiên trên nét thật ủng hộ hướng của đề tài.
- **Mô hình đọc nét thật kém:** CER của M2 là 21,09% với dòng ngắt và 38,53% với dòng liền, gấp 2,5 đến 4,5 lần mức 8,22% trên tập kiểm định ở Bảng 5. Kiểu chữ là nguyên nhân chính, vì K01 viết nhanh và nhiều chữ dính liền nhau, khác hẳn chữ trong VNOnDB. Dòng liền của K01 viết trên khung cuộn ngang có chữ nhỏ hơn và dính liền hơn dòng ngắt. Mô hình ngôn ngữ chỉ giảm CER 4,57 điểm phần trăm trên dòng ảo và 1,73 điểm phần trăm trên dòng liền.
- **Thu khoảng trống ít tác dụng:** khung cuộn ngang để lại khoảng trống rộng trong dòng liền, nhưng thu khoảng trống chỉ đổi CER của M2 trên mọi dòng liền từ 39,65% xuống 38,33%.
- **Người viết hay viết tắt:** 7 trên 11 dòng của P01 có chữ viết tắt. Giao thức thu phải dặn người viết chép đúng từng chữ, và người thu phải rà soát trước khi dùng tệp, theo `03-du-lieu.md`, mục 6.
- **Số liệu chỉ để định hướng:** dữ liệu có 2 người viết, cùng viết bằng bút, chưa có người viết bằng ngón tay. Sau khi loại dòng chép khác đề chỉ còn 18 dòng.

Từ kết quả này, đề tài chọn mô hình theo cả CER trên nét viết thật, theo `02-yeu-cau-va-danh-gia.md`, mục 5. Hai tệp của buổi thử chỉ dùng để chỉnh và so sánh, không dùng để huấn luyện và không tính vào kết quả cuối.

### 10.5. So sánh các mô hình

Bảng 13 so sánh các mô hình trên tập kiểm định và trên nét viết thật của buổi thử. Cột ảnh vẽ lại dùng khung xương ngưỡng 80 và độ dày nét 1,2 trên 400 dòng kiểm định đầu tiên, theo mục 7. Các cột nét viết thật tính trên 18 dòng chép đúng đề, độ dày nét 1,2. M2 dùng bản float16, `lm.bin`, $\alpha = 0{,}45$, $\beta = 4$ và độ rộng 30.

Bảng 13: CER (2) của các mô hình trên tập kiểm định và nét viết thật

| Mô hình | Kiểm định, M2 | Ảnh vẽ lại, M1 | Dòng ngắt ghép, M2 | Dòng ngắt từng hàng, M2 | Dòng liền, M2 |
| --- | --- | --- | --- | --- | --- |
| `m1_v2` | 8,22% | 30,82% | 21,09% | 53,96% | 38,53% |
| `m1_rr` | 9,28% | 21,27% | 16,86% | 26,25% | 28,11% |
| `m1_cap40` | 7,88% | 30,53% | 23,91% | 38,51% | 40,99% |
| `m1_rr_cap40` | 10,10% | 21,38% | 20,76% | 26,16% | 32,80% |
| `m1l_rr` | 7,41% | 18,22% | 14,96% | 26,66% | 29,08% |

Theo Bảng 13, ảnh vẽ lại giảm CER trên nét viết thật từ 4,23 đến 27,71 điểm phần trăm, nhưng làm CER của M2 trên tập kiểm định tăng 1,06 điểm phần trăm và vượt ngưỡng 8,4%. Theo quy tắc chọn ở `02-yeu-cau-va-danh-gia.md`, mục 5, mô hình `m1_rr` vì vậy chưa được chọn. Dòng ngắn đóng góp khoảng 1,9 điểm phần trăm vào CER (2) của M2 trên tập kiểm định, theo Bảng 7, nên lần chạy `m1_rr_cap40` thử giới hạn chiều cao phần nét để giảm phần này.

Mô hình `m1_cap40` đạt ngưỡng trên tập kiểm định với CER 7,88%, thấp nhất trong các lần chạy, nhưng không tốt hơn `m1_v2` trên nét viết thật. Dòng ngắt ghép và dòng liền của hai mô hình này chênh nhau từ 2,46 đến 2,82 điểm phần trăm, trong khi ảnh đưa vào mô hình gần như giống nhau, vì dòng ảo và dòng liền đều dài. Chênh lệch giữa hai lần huấn luyện cùng cấu hình dữ liệu vì vậy có thể tới khoảng 3 điểm phần trăm trên 13 dòng. Chỉ những chênh lệch lớn hơn mức này mới đủ để chọn mô hình theo nét viết thật.

Lần chạy `m1_rr_cap40` kém `m1_rr` ở mọi cột của Bảng 13 trừ cột nhận dạng từng hàng, nơi hai mô hình gần như bằng nhau. Mức kém là 0,82 điểm phần trăm với M2 trên tập kiểm định và từ 3,90 đến 4,69 điểm phần trăm trên dòng ngắt ghép và dòng liền. Giới hạn chiều cao phần nét giúp khi dùng riêng nhưng không giúp khi kết hợp với ảnh vẽ lại. Đề tài vì vậy dựng các lần chạy sau trên cấu hình của `m1_rr`. Lần chạy M1 lớn với giới hạn chiều cao phần nét được dừng ở epoch 4 và chạy lại thành `m1l_rr`.

Mô hình `m1l_rr` dùng M1 lớn với cấu hình dữ liệu của `m1_rr`. Đây là lần chạy đầu tiên đạt cả hai điều kiện của quy tắc chọn ở `02-yeu-cau-va-danh-gia.md`, mục 5. CER của M2 trên tập kiểm định là 7,41%, dưới ngưỡng 8,4%, và WER (2) là 19,78%. CER trên dòng ngắt ghép là 14,96%, thấp nhất trong Bảng 13. Trong các mô hình đạt ngưỡng, `m1l_rr` thấp hơn `m1_v2` 6,13 điểm phần trăm trên dòng ngắt ghép, lớn hơn mức dao động khoảng 3 điểm phần trăm nêu ở trên. So với `m1_rr`, M1 lớn giảm CER của M2 trên tập kiểm định 1,87 điểm phần trăm. Trên nét viết thật, M1 lớn chỉ giảm 1,90 điểm phần trăm với dòng ngắt ghép, còn hai cột kia gần bằng `m1_rr`. Phần lợi chắc chắn của M1 lớn vì vậy là đạt ngưỡng trên tập kiểm định mà vẫn giữ mức cải thiện của ảnh vẽ lại trên nét viết thật.

Theo quy tắc chọn, `m1l_rr` là mô hình được chọn tạm thời. Bản float16 nặng 4,47 MB, nên tổng dung lượng với `lm.bin` khoảng 15,4 MB, dưới giới hạn 20 MB. Thời gian chạy mô hình trên CPU của máy huấn luyện là 52,9 ms mỗi dòng, gấp khoảng 2,9 lần mức 18,4 ms của `m1_rr`. Cả hai số đo được lấy trong lúc máy đang huấn luyện một lần chạy khác. Độ trễ trên điện thoại thật cần đo theo `02-yeu-cau-va-danh-gia.md`, mục 2.5 trước khi chốt. Khi đó, hai lần chạy `m1_rr_el` và `m1_rr_e100` đang tạm dừng, theo mục 9. Mục 10.7 kiểm tra lại lựa chọn này trên sáu người viết, còn mục 10.8 so sánh thêm các lần chạy ngày 11/11/2026.

### 10.6. Buổi thử thứ hai

Ngày 10/11/2026, 4 người viết thêm theo giao thức thử, cùng viết bằng bút S Pen trên điện thoại Galaxy S23 Ultra. Mã gốc của bốn người có chứa tên, nên đề tài đổi sang mã V03 đến V06 theo thứ tự thu, theo `03-du-lieu.md`, mục 6. Mỗi người viết đủ 15 dòng, gồm 10 dòng ngắt và 5 dòng liền, và tệp đọc được trọn vẹn. Buổi thu nhập chiều rộng màn hình 62 mm, nên hàng ghi 10 mm và 14 mm cao thực tế khoảng 11,8 mm và 16,5 mm. Bảng 14 ghi thống kê dòng ngắt của sáu người viết của hai buổi thử. Mỗi ô có hai số, lần lượt cho hàng ghi 10 mm và hàng ghi 14 mm.

Bảng 14: Dòng ngắt của sáu người viết theo cỡ hàng ghi trên công cụ thu

| Người viết | Dòng chữ mỗi dòng ngắt, trung vị | Âm tiết mỗi dòng chữ | Dòng có hai dòng chữ trong một hàng kẻ | Phút viết, quy đổi 20 dòng | Dòng chép khác đề |
| --- | --- | --- | --- | --- | --- |
| K01 | 5 và 4 | 3,43 và 3,69 | 0 và 4 | 19,3 | 1 |
| P01 | 7 và 5 | 2,48 và 3,02 | 0 và 0 | 16,9 | 7 |
| V03 | 4 và 4 | 3,90 và 4,35 | 0 và 0 | 15,7 | 2 |
| V04 | 4 và 4 | 4,42 và 4,10 | 0 và 0 | 13,8 | 0 |
| V05 | 3 và 4 | 4,87 và 4,42 | 2 và 5 | 17,5 | 2 |
| V06 | 5 và 4 | 3,31 và 3,42 | 0 và 0 | 18,8 | 3 |

Trên cả sáu người, dòng ngắt có trung vị 4 dòng chữ, tức 3 chỗ nối, và nhiều nhất 7 dòng chữ. Thân chữ cao từ 0,23 đến 0,34 lần hàng kẻ tùy người viết và cỡ hàng, thấp hơn giá trị dự đoán 0,35 của lớp ghép đoạn nhưng vẫn nằm trong khoảng kẹp ở `04-thiet-ke-he-thong.md`, mục 2.1. Người viết chữ nhỏ như K01 và V05 viết hai dòng chữ trong một hàng kẻ khi hàng cao. Mọi người viết xong trong chưa tới 20 phút nếu quy đổi ra 20 dòng.

So với chỗ ngắt người thu đánh dấu, lớp ghép đoạn tách đúng số dòng chữ ở cả 40 dòng ngắt của buổi thứ hai, kể cả 7 dòng có hai dòng chữ trong một hàng kẻ. Ở buổi đầu, 2 trong 20 dòng lệch với đánh dấu. Hình nét của hai dòng này cho thấy người thu bỏ sót một chỗ ngắt, còn lớp ghép đoạn tách đúng. Như vậy lớp ghép đoạn tách đúng cả 60 dòng ngắt của hai buổi thử mà không cần chỉnh tham số.

Người thu không đánh dấu dòng chép khác đề nào. Đề tài xem hình nét gốc của các dòng có CER cao và các dòng mà mọi mô hình đọc ra ít từ hơn câu đề, và tìm thấy 7 dòng chép khác đề, đều là dòng ngắt. Trong đó 5 dòng thiếu một từ, 1 dòng viết chữ số 1 thay cho chữ "một" và 1 dòng bỏ dở. Các dòng này được ghi vào tệp rà soát riêng và bị loại khỏi phép đo, như buổi thử đầu. Cách rà soát này có thể bỏ sót dòng chép sai một từ mà số từ không đổi.

### 10.7. So sánh các mô hình trên sáu người viết

Bảng 15 đo lại các mô hình của Bảng 13 trên cả hai buổi thử, sau khi bỏ các dòng chép khác đề, gồm 46 dòng ngắt và 25 dòng liền. Cách đo giống mục 10.5. Khoảng tin cậy 95% trong ngoặc lấy bằng bootstrap với đơn vị lấy mẫu lại là người viết, theo `02-yeu-cau-va-danh-gia.md`, mục 2.6. Cột hiệu là hiệu ghép cặp trên cùng các dòng so với `m1_v2`, mô hình đang có trong ứng dụng, tính bằng điểm phần trăm.

Bảng 15: CER (2) của M2 trên nét viết thật của sáu người viết

| Mô hình | Kiểm định, M2 | Dòng ngắt ghép | Hiệu dòng ngắt ghép so với `m1_v2` | Dòng ngắt từng hàng | Dòng liền |
| --- | --- | --- | --- | --- | --- |
| `m1_v2` | 8,22% | 20,28% (13,91-26,08) | Mốc so sánh | 51,13% | 26,80% |
| `m1_rr` | 9,28% | 16,51% (11,77-21,67) | $-3{,}78$ $[-5{,}83; -1{,}30]$ | 28,15% | 21,31% |
| `m1_cap40` | 7,88% | 21,12% (14,64-27,27) | $+0{,}84$ $[-0{,}27; +2{,}53]$ | 36,90% | 25,81% |
| `m1_rr_cap40` | 10,10% | 18,46% (12,29-24,25) | $-1{,}82$ $[-2{,}55; -0{,}56]$ | 24,56% | 23,37% |
| `m1l_rr` | 7,41% | 15,77% (10,78-21,23) | $-4{,}51$ $[-5{,}95; -2{,}81]$ | 25,34% | 20,26% |

Thứ tự của buổi thử đầu vẫn giữ khi có sáu người viết. Mô hình `m1l_rr` có CER thấp nhất trên dòng ngắt ghép và dòng liền. Trên dòng ngắt ghép, mô hình này giảm CER 4,51 điểm phần trăm so với `m1_v2`, và khoảng tin cậy không chứa 0. Trong ba mô hình đạt ngưỡng 8,4% trên tập kiểm định, `m1l_rr` tốt nhất trên nét viết thật, nên vẫn là mô hình được chọn tạm thời theo quy tắc chọn. So với `m1_rr`, cùng cấu hình dữ liệu nhưng dùng M1, M1 lớn chỉ giảm 0,73 điểm phần trăm trên dòng ngắt ghép, với khoảng tin cậy từ giảm 1,86 đến tăng 0,38 điểm phần trăm. Phần lợi chắc chắn của M1 lớn vẫn là đạt ngưỡng trên tập kiểm định, như mục 10.5 đã nêu.

Ghép dòng ảo tốt hơn nhận dạng từng hàng ở mọi mô hình. Với `m1l_rr`, CER của dòng ngắt ghép thấp hơn nhận dạng từng hàng 9,57 điểm phần trăm. Chênh lệch giữa người viết lớn hơn chênh lệch giữa các mô hình: với `m1l_rr`, CER của dòng ngắt ghép từ 7,16% với V06 đến 26,46% với V04, người viết chữ liền nét nhiều nhất. Vì chỉ có sáu người viết, khoảng tin cậy rộng và chủ yếu dùng cho so sánh ghép cặp.

Trên 25 dòng liền của năm người viết, dòng ngắt mô phỏng của `m1l_rr` có mức tăng 1,40 điểm phần trăm với 2 chỗ nối, 2,32 điểm phần trăm với 4 chỗ nối và 3,68 điểm phần trăm với 6 chỗ nối, so với chính các dòng đó viết liền. Ngưỡng 2 điểm phần trăm ở `02-yeu-cau-va-danh-gia.md`, mục 1 chỉ đạt với 2 chỗ nối. Dòng ngắt thật có trung vị 3 chỗ nối, nên mức tăng điển hình nằm sát ngưỡng. Khoảng tin cậy của mức tăng rộng, ví dụ từ giảm 0,27 đến tăng 5,78 điểm phần trăm với 4 chỗ nối, nên cần thêm dữ liệu của nhóm chỉnh để kết luận. Mọi kết quả của mục này chỉ gồm người viết bằng bút, vì dữ liệu viết bằng ngón tay chưa có.

### 10.8. Các lần chạy ngày 11/11/2026

Bảng 16 ghi kết quả của các lần chạy ngày 11/11/2026, cùng hai mô hình `m1_rr` và `m1l_rr` để so sánh. Cách đo giống mục 10.7, với $\alpha = 0{,}45$ và $\beta = 4$ cho mọi mô hình. Cột "Ngắt ghép và liền" gộp 46 dòng ngắt sau khi ghép và 25 dòng liền, tức mọi dòng viết thật đi qua đúng luồng của ứng dụng. Hai cột hiệu là hiệu ghép cặp so với `m1_rr`, cấu hình gốc của các lần chạy này, tính bằng điểm phần trăm, kèm khoảng tin cậy 95% lấy mẫu lại theo người viết.

Bảng 16: CER (2) của M2 của các lần chạy ngày 11/11/2026 trên tập kiểm định và nét viết thật

| Mô hình | Kiểm định, M2 | Dòng ngắt ghép | Hiệu dòng ngắt ghép | Dòng liền | Ngắt ghép và liền | Hiệu ngắt ghép và liền |
| --- | --- | --- | --- | --- | --- | --- |
| `m1_rr` | 9,28% | 16,51% | Mốc so sánh | 21,31% | 18,20% | Mốc so sánh |
| `m1_rr_el` | 12,09% | 21,09% | $+4{,}59$ $[+3{,}02; +5{,}91]$ | 24,24% | 22,20% | $+4{,}00$ $[+2{,}61; +5{,}46]$ |
| `m1_rr_e100` | 7,73% | 13,57% | $-2{,}94$ $[-4{,}67; -1{,}42]$ | 20,63% | 16,05% | $-2{,}14$ $[-3{,}20; -1{,}42]$ |
| `m0_rr` | 19,57% | 38,05% | $+21{,}54$ $[+14{,}88; +27{,}46]$ | 44,16% | 40,20% | $+22{,}00$ $[+17{,}07; +26{,}56]$ |
| `m1l_rr` | 7,41% | 15,77% | $-0{,}73$ $[-1{,}86; +0{,}38]$ | 20,26% | 17,35% | $-0{,}85$ $[-1{,}68; -0{,}11]$ |
| `m1l_rr_e100` | 6,61% | 14,33% | $-2{,}18$ $[-3{,}99; -0{,}73]$ | 19,02% | 15,98% | $-2{,}21$ $[-3{,}42; -1{,}14]$ |

Theo Bảng 16, biến dạng đàn hồi làm `m1_rr` kém đi trên cả tập kiểm định và nét viết thật, nên đề tài không chạy lại thay đổi này với M1 lớn. Huấn luyện 100 epoch giảm CER của M2 trên tập kiểm định 1,55 điểm phần trăm và giảm CER của dòng ngắt ghép 2,94 điểm phần trăm, với khoảng tin cậy không chứa 0. Theo `05-ke-hoach-thi-nghiem.md`, mục 3, thay đổi nào giúp M1 thì được chạy lại với M1 lớn, nên đề tài chạy thêm `m1l_rr_e100`.

Mô hình `m0_rr` không có BiLSTM có CER cao hơn `m1_rr` khoảng 2,1 lần trên tập kiểm định và 2,3 lần trên dòng ngắt ghép. Khi nhận dạng từng hàng, CER của M0 lên tới 67,48%. BiLSTM vì vậy đáng giữ, dù M0 chỉ có khoảng một phần ba số tham số của M1.

Mô hình `m1l_rr_e100` có CER của M2 trên tập kiểm định là 6,61% và WER (2) là 17,71%, thấp nhất trong mọi lần chạy. Con số này thấp hơn cả mục tiêu cao hơn 7,6% ở `02-yeu-cau-va-danh-gia.md`, mục 1, nhưng mục tiêu đó tính trên tập kiểm thử, nên chưa thể kết luận trước lần chạy cuối. So với `m1l_rr`, huấn luyện 100 epoch giảm CER trên tập kiểm định 0,80 điểm phần trăm. Trên nét viết thật, mức giảm là 1,44 điểm phần trăm với dòng ngắt ghép, khoảng tin cậy từ 0,27 đến 2,72, và 1,37 điểm phần trăm với nhóm ngắt ghép và liền, khoảng tin cậy từ 0,39 đến 2,44.

Trên nét viết thật, `m1l_rr_e100` và `m1_rr_e100` gần ngang nhau. Khi so ghép cặp trực tiếp, `m1l_rr_e100` cao hơn 0,76 điểm phần trăm trên dòng ngắt ghép, khoảng tin cậy từ tăng 0,25 đến tăng 1,23, nhưng thấp hơn 1,60 điểm phần trăm trên dòng liền, khoảng tin cậy từ giảm 3,54 đến tăng 0,22. Trên nhóm ngắt ghép và liền, hiệu chỉ là giảm 0,07 điểm phần trăm, khoảng tin cậy từ giảm 0,85 đến tăng 0,43. Các khoảng tin cậy này chỉ tính độ dao động giữa người viết, chưa tính độ dao động giữa các lần huấn luyện, mà mục 10.5 ước lượng có thể tới khoảng 3 điểm phần trăm trên 13 dòng. Đề tài vì vậy chạy thêm hai hạt giống cho mỗi cấu hình trước khi chọn, theo mục 10.9.

Huấn luyện lâu hơn không làm giảm rõ mức tăng của dòng ngắt mô phỏng. Với `m1l_rr_e100`, mức tăng là 1,40; 2,92 và 3,61 điểm phần trăm với 2, 4 và 6 chỗ nối, gần bằng `m1l_rr`. Với `m1_rr_e100`, mức tăng là giảm 0,07; tăng 2,67 và tăng 2,10 điểm phần trăm. Ngưỡng 2 điểm phần trăm vẫn chỉ đạt với 2 chỗ nối. Người viết V04 vẫn khó nhất, với CER của dòng ngắt ghép từ 26% đến 27% ở cả hai mô hình 100 epoch, trong khi V06 chỉ từ 4% đến 5%.

### 10.9. Độ dao động giữa các hạt giống

Mọi lần chạy ở các mục trên dùng hạt giống 1. Để biết chênh lệch giữa `m1_rr_e100` và `m1l_rr_e100` có lớn hơn độ dao động do ngẫu nhiên không, đề tài chạy lại hai cấu hình này với hạt giống 2 và 3, theo `05-ke-hoach-thi-nghiem.md`, mục 6. Hạt giống đổi khởi tạo trọng số, thứ tự các dòng trong lô, ảnh vẽ lại được chọn cho mỗi dòng, phép tăng cường và dropout, còn dữ liệu và mọi tham số khác giữ nguyên. Tên lần chạy có thêm đuôi `_s2` hoặc `_s3`.

Cách chọn được chốt trước khi có kết quả của các hạt giống mới. Chỉ số chính là CER (2) của M2 trên nhóm ngắt ghép và liền, lấy trung bình qua ba hạt giống, vì nhóm này gồm mọi dòng viết thật đi qua đúng luồng của ứng dụng. Cấu hình có chỉ số chính thấp hơn được chọn nếu hiệu giữa hai cấu hình rõ hơn cả độ dao động giữa người viết lẫn độ dao động giữa các hạt giống. Nếu không, hai cấu hình được xem là ngang nhau trên nét viết thật, và đề tài chọn cấu hình có CER của M2 trên tập kiểm định thấp hơn. Lý do là tập kiểm định có 1.229 dòng, nhiều hơn hẳn nét viết thật, và ngưỡng 8,4% ở `02-yeu-cau-va-danh-gia.md`, mục 1 phải đạt trên tập kiểm thử. Mô hình đưa vào ứng dụng là lần chạy hạt giống 1 của cấu hình được chọn, vì $\alpha$ và $\beta$ đã chỉnh cho lần chạy này. Hai hạt giống còn lại chỉ dùng để đo độ dao động.

Bảng 17 ghi kết quả của sáu lần chạy, đo như mục 10.8.

Bảng 17: Kết quả của ba hạt giống của hai cấu hình 100 epoch

| Lần chạy | Epoch tốt nhất | Kiểm định, giải mã đơn giản | Kiểm định, M2 | Dòng ngắt ghép | Dòng liền | Ngắt ghép và liền |
| --- | --- | --- | --- | --- | --- | --- |
| `m1_rr_e100` | 100 | 10,04% | 7,73% | 13,57% | 20,63% | 16,05% |
| `m1_rr_e100_s2` | 91 | 10,08% | 7,74% | 15,50% | 21,76% | 17,71% |
| `m1_rr_e100_s3` | 93 | 10,46% | 8,11% | 14,82% | 20,69% | 16,89% |
| `m1l_rr_e100` | 97 | 8,27% | 6,61% | 14,33% | 19,02% | 15,98% |
| `m1l_rr_e100_s2` | 99 | 8,73% | 6,93% | 14,04% | 19,41% | 15,93% |
| `m1l_rr_e100_s3` | 95 | 8,51% | 6,82% | 13,54% | 18,90% | 15,43% |

Bảng 18 so hai cấu hình qua ba hạt giống. Các cột của bảng như sau:

- **M1 và M1 lớn:** trung bình qua ba hạt giống, độ lệch chuẩn mẫu ghi trong ngoặc.
- **Hiệu:** M1 lớn trừ M1, tính bằng điểm phần trăm.
- **Theo người viết:** khoảng tin cậy 95% của hiệu, lấy mẫu lại theo người viết trên CER của mỗi dòng đã lấy trung bình qua ba hạt giống.
- **Theo hạt giống:** tỷ số giữa hiệu và sai số chuẩn của phép thử t của Welch trên ba giá trị của mỗi cấu hình, kèm giá trị tới hạn hai phía ở mức 5%. Hiệu rõ hơn độ dao động giữa các hạt giống khi trị tuyệt đối của tỷ số vượt giá trị tới hạn.

Bảng 18: So sánh M1 và M1 lớn qua ba hạt giống

| Chỉ số | M1 | M1 lớn | Hiệu | Theo người viết | Theo hạt giống |
| --- | --- | --- | --- | --- | --- |
| Kiểm định, M2 | 7,86% (0,22) | 6,79% (0,16) | $-1{,}07$ | Không áp dụng | $-6{,}89$, tới hạn 2,87 |
| Dòng ngắt ghép | 14,63% (0,98) | 13,97% (0,40) | $-0{,}66$ | $[-1{,}13; -0{,}16]$ | $-1{,}08$, tới hạn 3,44 |
| Dòng liền | 21,03% (0,64) | 19,11% (0,27) | $-1{,}92$ | $[-2{,}53; -1{,}29]$ | $-4{,}78$, tới hạn 3,40 |
| Ngắt ghép và liền | 16,88% (0,83) | 15,78% (0,31) | $-1{,}10$ | $[-1{,}33; -0{,}87]$ | $-2{,}17$, tới hạn 3,53 |

Theo Bảng 18, M1 lớn thấp hơn M1 ở mọi chỉ số. Trên chỉ số chính, M1 lớn thấp hơn 1,10 điểm phần trăm, và khoảng tin cậy theo người viết không chứa 0. Tuy vậy, trị tuyệt đối của tỷ số theo hạt giống chỉ là 2,17, dưới giá trị tới hạn 3,53. Hiệu này vì vậy chưa rõ hơn độ dao động giữa các hạt giống, nên theo cách chọn đã chốt, hai cấu hình được xem là ngang nhau trên nét viết thật.

Trên tập kiểm định, M1 lớn thấp hơn M1 1,07 điểm phần trăm, và tỷ số theo hạt giống vượt giá trị tới hạn. Mọi hạt giống của cả hai cấu hình đều có CER của M2 dưới ngưỡng 8,4%. Đề tài vì vậy chọn M1 lớn, và mô hình đưa vào ứng dụng là `m1l_rr_e100`, theo mục 11.

Độ dao động giữa các hạt giống trên nét viết thật lớn hơn nhiều so với trên tập kiểm định. Với M1, hai hạt giống 1 và 2 chỉ chênh 0,01 điểm phần trăm trên tập kiểm định, nhưng chênh 1,93 điểm phần trăm trên dòng ngắt ghép. Khoảng tin cậy theo người viết của hiệu này từ 1,17 đến 2,57, không chứa 0, dù hai lần chạy cùng cấu hình. Khoảng tin cậy theo người viết vì vậy chưa tính hết độ không chắc chắn khi so hai lần huấn luyện. M1 lớn ổn định hơn M1, với độ lệch chuẩn 0,31 so với 0,83 điểm phần trăm trên nhóm ngắt ghép và liền.

Các hiệu dưới khoảng 2 điểm phần trăm trên nét viết thật giữa hai lần chạy đơn lẻ ở các mục 10.5 đến 10.8 vì vậy cần đọc thận trọng. Các quyết định trước vẫn giữ, vì mỗi quyết định đều có bằng chứng trên tập kiểm định, nơi độ lệch chuẩn giữa các hạt giống không quá 0,22 điểm phần trăm:

- **Ảnh vẽ lại:** giảm CER trên ảnh vẽ lại của tập kiểm định từ 30,82% xuống 21,27%, theo Bảng 13.
- **Huấn luyện 100 epoch:** giảm CER của M2 trên tập kiểm định 1,55 điểm phần trăm với M1 và 0,80 điểm phần trăm với M1 lớn.
- **Các thay đổi bị loại:** biến dạng đàn hồi, giới hạn chiều cao phần nét khi đã có ảnh vẽ lại và mô hình M0 làm CER của M2 trên tập kiểm định tăng từ 0,82 đến 10,29 điểm phần trăm.

### 10.10. Thử viết bằng ngón tay

Ngày 11/11/2026, người thu gửi ba buổi thu viết bằng ngón tay trên iPhone, qua trình duyệt của công cụ `tools/thu-net/`. Ba buổi này thuộc hai người viết, vì người thu xác nhận hai buổi là của cùng một người. Mã gốc có tên người viết, nên bản phân tích `~/vnhw/data/ngon-tay-1/` đổi sang mã V07 và V08, còn tệp gốc giữ nguyên ở máy của người thu. Bảng 19 ghi nội dung và các điểm lệch so với quy trình ở `03-du-lieu.md`, mục 6.

Bảng 19: Ba buổi thu viết bằng ngón tay ngày 11/11/2026

| Buổi | Quy trình | Số dòng ngắt và dòng liền | Câu đề | Dòng bị loại |
| --- | --- | --- | --- | --- |
| V07 | Buổi thử, hàng kẻ cao 14 và 10 mm | 10 và 5 | Câu của buổi thử bị cắt ngắn | 2 dòng: câu đề gõ sai, một nét chấm lạc xa dòng chữ |
| V08, buổi 1 | Buổi thử, hàng kẻ cao 14 và 10 mm | 10 và 5 | Câu của buổi thử, đủ | 3 dòng liền: viết lặp, viết lại nhiều lần, viết dở |
| V08, buổi 2 | Nhóm chỉnh, hàng kẻ cao 12 mm | 10 và 10 | Câu của nhóm chỉnh bị sửa ở cả 20 dòng | Không |

Theo Bảng 19, không buổi nào đúng hẳn quy trình của nhóm chỉnh, nên ba buổi chỉ dùng như một buổi thử viết bằng ngón tay và không tính vào nhóm chỉnh. Người thu không đánh dấu dòng chép sai trên công cụ, nên các dòng bị loại được tìm bằng cách xem ảnh của các dòng có CER cao. Nhãn của mỗi dòng là câu đề hiện trên công cụ lúc viết. Với V07, người thu nhập bề rộng màn hình 60 mm, trong khi màn hình thật khoảng 65 mm, nên hàng kẻ lớn hơn dự định khoảng 8%.

Sau khi loại 5 dòng, còn 29 dòng ngắt và 16 dòng liền. Với mô hình `m1l_rr_e100` và cấu hình triển khai, CER (2) của M2 là 18,56% với dòng ngắt sau khi ghép và 26,00% với dòng liền, so với 14,33% và 19,02% khi viết bằng bút ở mục 10.8. Gộp hai nhóm, CER (2) khoảng 21,2%, so với 15,98% khi viết bằng bút. Dòng liền của V07 có CER 45,85% trên 4 dòng, dù ảnh vẽ ra rõ, còn của V08 là 19,39% trên 12 dòng.

Với hai người viết, các số này chưa đủ để kết luận về viết bằng ngón tay, và chưa thể lấy khoảng tin cậy theo người viết. Độ dày nét 1,0 và 1,5 không cho thứ tự nhất quán: độ dày 1,2 thấp nhất với dòng ngắt sau khi ghép, còn độ dày 1,5 thấp nhất với dòng liền. Ứng dụng vì vậy giữ độ dày 1,2 cho tới khi có nhóm chỉnh.

### 10.11. Huấn luyện 150 epoch

Ở mục 10.9, cả ba hạt giống của M1 lớn đạt epoch tốt nhất từ 95 đến 99 trên 100 epoch, nên mô hình có thể còn giảm CER nếu huấn luyện lâu hơn. Ngày 12/11/2026, đề tài bắt đầu chạy `m1l_rr_e150`, giống hệt `m1l_rr_e100` với hạt giống 1, chỉ đổi số epoch thành 150. Tốc độ học vẫn giảm theo hàm cosin, nhưng trải trên 150 epoch.

Cách chọn được chốt trước khi có kết quả. `m1l_rr_e150` chỉ là ứng viên thay `m1l_rr_e100` khi thỏa cả hai điều kiện sau, đo như mục 10.8 với $\alpha = 0{,}45$ và $\beta = 4$:

- **Tập kiểm định:** CER của M2 thấp hơn trung bình ba hạt giống của M1 lớn, 6,79%, quá ba lần độ lệch chuẩn 0,16 điểm phần trăm, tức dưới 6,31%.
- **Nét viết thật:** CER của M2 trên nhóm ngắt ghép và liền không cao hơn 16,40%, bằng trung bình ba hạt giống cộng hai lần độ lệch chuẩn ở Bảng 18.

Nếu là ứng viên, đề tài chạy thêm hạt giống 2 và 3 của cấu hình 150 epoch và so như mục 10.9 trước khi đổi mô hình trong ứng dụng. Nếu không, ứng dụng giữ `m1l_rr_e100`, và kết quả chỉ ghi lại để biết thêm epoch có còn lợi không. Lần chạy đầu bị dừng ở epoch 47, theo Bảng 10, và được chạy lại từ đầu ngày 13/11/2026.

Lần chạy lại xong ngày 13/11/2026, kết quả huấn luyện ở Bảng 2. Bảng 20 ghi kết quả đo như mục 10.8, cùng trung bình và độ lệch chuẩn mẫu của ba hạt giống của `m1l_rr_e100` ở Bảng 17 và Bảng 18 để so. Cột hiệu là hiệu so với `m1l_rr_e100`, tính bằng điểm phần trăm; với nét viết thật, hiệu ghép cặp theo dòng, kèm khoảng tin cậy 95% lấy mẫu lại theo người viết.

Bảng 20: Kết quả của `m1l_rr_e150` so với ba hạt giống của `m1l_rr_e100`

| Chỉ số | Ba hạt giống của `m1l_rr_e100` | Ngưỡng ứng viên | `m1l_rr_e150` | Hiệu so với `m1l_rr_e100` |
| --- | --- | --- | --- | --- |
| Kiểm định, giải mã đơn giản | 8,50% (0,23) | Không áp dụng | 7,95% | $-0{,}32$ |
| Kiểm định, M2 | 6,79% (0,16) | Dưới 6,31% | 6,38% | $-0{,}24$ |
| Dòng ngắt ghép | 13,97% (0,40) | Không áp dụng | 15,59% | $+1{,}26$ $[+0{,}30; +2{,}18]$ |
| Dòng liền | 19,11% (0,27) | Không áp dụng | 17,93% | $-1{,}09$ $[-2{,}31; +0{,}18]$ |
| Ngắt ghép và liền | 15,78% (0,31) | Không quá 16,40% | 16,41% | $+0{,}43$ $[-0{,}04; +0{,}76]$ |

Theo Bảng 20, `m1l_rr_e150` không đạt điều kiện nào trong hai điều kiện đã chốt. CER của M2 trên tập kiểm định là 6,38%, cao hơn ngưỡng 6,31% 0,07 điểm phần trăm. CER trên nhóm ngắt ghép và liền là 16,41%, cao hơn ngưỡng 16,40% 0,01 điểm phần trăm. Lần chạy này vì vậy không phải ứng viên, đề tài không chạy thêm hạt giống của cấu hình 150 epoch, và ứng dụng giữ `m1l_rr_e100`.

Thêm 50 epoch vẫn có lợi trên tập kiểm định. So với `m1l_rr_e100`, CER của M2 giảm 0,24 điểm phần trăm, và so với trung bình ba hạt giống giảm 0,41 điểm phần trăm, bằng 2,5 lần độ lệch chuẩn 0,16. WER (2) của M2 giảm từ 17,71% xuống 17,10%. Trên ảnh vẽ lại của 400 dòng kiểm định với độ dày nét 1,2, CER giảm từ 16,51% xuống 15,92%. Trên nét viết thật, hai nhóm đi ngược chiều nhau. Dòng liền giảm 1,09 điểm phần trăm, nhưng khoảng tin cậy chứa 0. Dòng ngắt ghép tăng 1,26 điểm phần trăm với khoảng tin cậy không chứa 0, tăng ở 4 trong 6 người viết, và so với trung bình ba hạt giống tăng 1,62 điểm phần trăm, bằng 4 lần độ lệch chuẩn 0,40 của nhóm này. CER khi nhận dạng từng hàng của dòng ngắt cũng tăng từ 22,60% lên 24,81%. Mức tăng của dòng ngắt mô phỏng so với chính dòng đó viết liền là 2,39; 4,52 và 3,34 điểm phần trăm với 2, 4 và 6 chỗ nối, so với 1,40; 2,92 và 3,61 của `m1l_rr_e100`.

Một cách giải thích là huấn luyện lâu hơn với tốc độ học nhỏ làm mô hình bám sát hơn cách vẽ của dữ liệu huấn luyện, nên đọc tốt hơn các dòng dài và giống tập kiểm định, nhưng kém đi với các mảnh hàng ngắn và chỗ nối của dòng ngắt ghép. Với một lần chạy, đây mới là giả thuyết, vì mục 10.9 cho thấy hai hạt giống cùng cấu hình có thể chênh tới 2 điểm phần trăm trên nhóm này. Kết quả chỉ ghi lại để tham khảo: nếu nhóm chỉnh cho thấy dòng ngắt ghép là điểm yếu chính, thì tăng số epoch không phải hướng nên thử tiếp.

### 10.12. Đợt thu đầu của nhóm chỉnh và nhóm kiểm thử

Ngày 15/11/2026, đề tài nhận 10 buổi thu viết bằng ngón tay, thu từ ngày 12/11/2026 đến ngày 15/11/2026 bằng bản công cụ ngày 12/11/2026. Mỗi người viết dùng máy của mình và mở công cụ khi chưa đăng nhập, nên không tải được tệp mà phải sao chép dữ liệu. Cả 10 tệp đọc được đủ 20 dòng, đúng câu đề đã khóa, đúng cách nhập bằng ngón tay và có mã ẩn danh. Có 6 buổi thuộc nhóm chỉnh và 4 buổi thuộc nhóm kiểm thử. Bản phân tích nằm ở `~/vnhw/data/nhom-chinh/` và `~/vnhw/data/nhom-kiem-thu/`, mỗi thư mục có tệp `review.json` ghi kết quả rà soát lại.

Bảng 21 ghi các điểm lệch so với quy trình ở `03-du-lieu.md`, mục 6. Hàng kẻ thật được tính từ mật độ điểm ảnh của phần cứng, với giả thiết trang không bị phóng to.

Bảng 21: Mười buổi thu ngày 12/11/2026 đến 15/11/2026

| Mã | Nhóm | Đổi chéo | Máy | Nguồn kích thước | Hàng kẻ thật | Dòng chép khác đề tìm thấy khi rà soát lại |
| --- | --- | --- | --- | --- | --- | --- |
| NV-34C4 | Chỉnh | B | Galaxy S23 Ultra | Bảng máy | 12 mm | Không |
| NV-3ET7 | Chỉnh | A | Galaxy A16 5G | Bảng máy | 12 mm | Không |
| NV-5JCD | Chỉnh | A | iPhone XS Max hoặc 11 Pro Max | Bảng máy | 12 mm | 2 dòng, đổi một từ |
| NV-GPQJ | Chỉnh | A | iPhone 16 Pro Max hoặc 17 Pro Max | Bảng máy | 12 mm | 1 dòng, thiếu một từ |
| NV-Q9T3 | Chỉnh | A | iPhone 16 Pro Max hoặc 17 Pro Max | Bảng máy | 12 mm | Không |
| NV-XVJ7 | Chỉnh | A | iPhone 12 Pro Max, 13 Pro Max hoặc 14 Plus | Thẻ, lệch 22% | Khoảng 9,3 mm | Không |
| NV-BXDB | Kiểm thử | A | iPhone 14 Pro, 15, 15 Pro hoặc 16 | Thẻ, khớp bảng máy | 12 mm | 2 dòng, thiếu từ |
| NV-542R | Kiểm thử | B | iPhone 14 Pro Max và các máy cùng màn hình | Bảng máy | 12 mm | 1 dòng, thiếu một từ |
| NV-QSA9 | Kiểm thử | B | iPad 10,2 inch | Thẻ, lệch 33% | Khoảng 16 mm | Không |
| NV-Y7CU | Kiểm thử | B | iPad Pro 11 inch | Thẻ, lệch 33% | Khoảng 16 mm | 2 dòng, thiếu một từ |

Theo Bảng 21, đợt thu lệch quy trình ở năm điểm:

- **Thu xen kẽ hai nhóm:** nhóm kiểm thử được thu cùng lúc với nhóm chỉnh, trong khi quy trình yêu cầu thu xong nhóm chỉnh trước.
- **Lệch nhóm đổi chéo:** nhóm chỉnh có 5 buổi A và 1 buổi B, nhóm kiểm thử có 1 buổi A và 3 buổi B.
- **Máy tính bảng:** hai buổi của nhóm kiểm thử viết trên iPad, có khung viết rộng gấp đôi điện thoại, nên một dòng ngắt chỉ chiếm từ 2 đến 6 hàng, so với từ 4 đến 11 hàng trên điện thoại.
- **Số đo bằng thẻ sai:** ba trên bốn buổi đo bằng thẻ lệch từ 22% đến 33% so với thông số của máy. Ở buổi NV-XVJ7, công cụ đã nhận đúng máy, nhưng số đo bằng thẻ để đối chiếu lại thay số của bảng máy.
- **Rà soát không kỹ:** người rà soát chọn Chép đúng cho 199 trên 200 dòng, có buổi rà soát 20 dòng trong 27 giây. Dòng duy nhất được chọn Chép khác lại khớp câu đề.

Đề tài rà soát lại cả 200 dòng bằng mắt trên ảnh vẽ từ nét gốc. Với nhóm kiểm thử, việc rà soát chỉ dùng ảnh nét, không chạy mô hình và không chạy lớp ghép đoạn. Kết quả là 3 dòng chép khác đề ở nhóm chỉnh và 5 dòng ở nhóm kiểm thử, đều là thiếu từ hoặc đổi một từ. Các dòng này bị loại khỏi phép đo. Dòng mà người rà soát chọn Chép khác vẫn bị loại. Nhóm chỉnh còn 5 dòng liền có nét lạc do chạm nhầm, gồm chấm nhỏ cách xa dòng chữ và một nét thẳng dài. Các dòng có nét lạc được giữ lại, vì người dùng thật cũng có thể chạm nhầm, và quy tắc này áp dụng cho cả nhóm kiểm thử.

Ngày 16/11/2026, buổi NV-XVJ7 được để riêng vì hàng kẻ thật khoảng 9,3 mm không đúng quy trình, nên nhóm chỉnh còn 5 buổi đủ điều kiện, gồm 4 buổi A và 1 buổi B. Với 5 buổi này, mô hình `m1l_rr_e100` và cấu hình triển khai, còn 48 dòng liền và 49 dòng ngắt. CER (2) của M2 là 15,02% với dòng liền và 17,22% với dòng ngắt sau khi ghép, gộp hai nhóm là 16,13%. Khi nhận dạng từng hàng, CER (2) là 29,46%. Mức này gần mức 15,98% của sáu người viết bằng bút ở mục 10.8 và thấp hơn mức khoảng 21,2% của buổi thử ngón tay ở mục 10.10. CER của dòng ngắt ghép theo người viết trải từ 4,28% đến 23,20%. Với độ dày nét 1,0; 1,2 và 1,5, CER (2) của dòng liền là 15,81%; 15,02% và 15,28%, còn của dòng ngắt ghép là 17,60%; 17,22% và 17,28%, nên độ dày 1,2 vẫn được giữ. Dòng ngắt mô phỏng 2, 4 và 6 chỗ nối có CER (2) 16,40%; 17,60% và 20,64%, tức tăng 1,38; 2,58 và 5,62 điểm phần trăm so với dòng liền. Khi tính cả NV-XVJ7, như lần đo ngày 15/11/2026, CER (2) là 14,46% với dòng liền và 16,94% với dòng ngắt ghép.

Hai dòng liền của NV-GPQJ có nét lạc xa dòng chữ có CER 70,7% và 89,4%. Chấm lạc và nét lạc không mở được dòng chữ mới trong lớp ghép đoạn, nên chúng kéo giãn khung của dòng và làm chữ bị thu nhỏ khi vẽ ảnh. Nếu bỏ hai dòng này, CER (2) của dòng liền là 12,20%. Đây là điểm yếu của lớp ghép đoạn cần xử lý ở bước 6, bằng cách bỏ các nét nằm quá xa thân chữ trước khi ghép.

Các số trên mới là số tạm, vì nhóm chỉnh mới có 5 trên 10 người đủ điều kiện và lệch về nhóm A. Hai buổi trên iPad không tính vào nhóm kiểm thử của điện thoại và được để riêng. Nhóm kiểm thử vì vậy mới có 2 buổi hợp lệ, và mô hình chưa được chạy trên buổi nào của nhóm này. Bản phân tích của các buổi để riêng nằm ở `~/vnhw/data/nhom-chinh-de-rieng/` và `~/vnhw/data/nhom-kiem-thu-de-rieng/`, mỗi thư mục có tệp ghi lý do.

Cùng ngày, công cụ thu được sửa thành bản 2026-11-15 để các lỗi trên không lặp lại, theo `03-du-lieu.md`, mục 6.

### 10.13. Đợt thu thứ hai của nhóm chỉnh

Ngày 18/11/2026, đề tài nhận một bộ dữ liệu khảo sát mới để thay bộ ở mục 10.12. Bộ mới có 10 buổi, đều thuộc nhóm chỉnh. Năm buổi nhóm A giống từng byte với bản cũ, kể cả buổi NV-XVJ7 đã để riêng. Năm buổi còn lại thuộc nhóm đổi chéo B, thu ngày 16/11/2026 bằng bản công cụ 2026-11-15, mở ngoài khung claude.ai. Bộ mới không còn buổi NV-34C4 của nhóm chỉnh và bốn buổi của nhóm kiểm thử.

Năm buổi mới đều đủ 20 dòng, đúng câu đề đã khóa, viết bằng ngón tay trên điện thoại và có mã ẩn danh. Bảng 22 ghi máy, cỡ hàng và kết quả rà soát lại của năm buổi này. Hàng kẻ thật được tính như Bảng 21, từ thông số màn hình của máy.

Bảng 22: Năm buổi nhóm B của nhóm chỉnh thu ngày 16/11/2026

| Mã | Máy | Nguồn kích thước | Hàng kẻ thật | Thời gian rà soát của người thu | Dòng chép khác đề tìm thấy khi rà soát lại |
| --- | --- | --- | --- | --- | --- |
| NV-8GTX | Galaxy A12 | Thẻ, rộng hơn thông số máy 3,3% | Khoảng 11,6 mm | 609 giây | Không |
| NV-BJVH | Galaxy A33 5G | Thẻ, hẹp hơn thông số máy 2,9% | Khoảng 12,4 mm | 117 giây | 4 dòng, thiếu một từ hoặc đổi từ |
| NV-DQK4 | Galaxy A13 | Thẻ, hẹp hơn thông số máy 2,3% | Khoảng 12,3 mm | 289 giây | Không |
| NV-GPBG | iPhone 12 Pro Max, 13 Pro Max hoặc 14 Plus | Bảng máy | 12 mm | 53 giây | 2 dòng, thừa một từ hoặc thiếu một từ |
| NV-H8XR | iPhone 14 Pro, 15, 15 Pro hoặc 16 | Bảng máy | 12 mm | 83 giây | 3 dòng, thiếu từ hoặc đổi một từ |

Theo Bảng 22, ba máy Galaxy không có trong bảng máy của công cụ nên được đo bằng thẻ. Lần này số đo bằng thẻ chỉ lệch thông số máy từ 2,3% đến 3,3%, so với 22% đến 33% ở mục 10.12. Hàng kẻ thật vì vậy cao từ khoảng 11,6 đến 12,4 mm. Mức lệch này nhỏ hơn nhiều so với mức 22% khiến NV-XVJ7 bị để riêng, nên đề tài nhận cả năm buổi.

Người thu chọn Chép đúng cho cả 100 dòng, có buổi rà soát 20 dòng trong 53 giây. Đề tài rà soát lại cả 100 dòng bằng mắt trên ảnh vẽ từ nét gốc, như mục 10.12. Vì đây là nhóm chỉnh, đề tài chạy thêm mô hình để đối chiếu các dòng có CER cao. Kết quả là 9 dòng chép khác đề, đều ở ba buổi có thời gian rà soát ngắn nhất. Hai người viết cùng viết "hiện tại" thay cho "hiện đại", một người viết "đẹp" thay cho "hẹp", còn các dòng khác thiếu hoặc thừa từ.

Theo yêu cầu thay dữ liệu, thư mục nhóm chỉnh đủ điều kiện và bản phân tích `~/vnhw/data/nhom-chinh/` được thay theo bộ mới. Nhóm chỉnh nay có 9 buổi đủ điều kiện, gồm 4 buổi A cũ và 5 buổi B mới, và tệp `review.json` có thêm 9 dòng chép khác đề. Buổi NV-34C4 vẫn đúng quy trình nhưng không có trong bộ mới, nên được chuyển sang `~/vnhw/data/nhom-chinh-de-rieng/` để chờ người phụ trách xác nhận lý do. Buổi NV-XVJ7 vẫn để riêng như mục 10.12. Năm buổi mới không có nét lạc xa dòng chữ.

Thư mục phiếu đồng ý của bộ mới giống hệt bộ cũ, gồm 10 phiếu ký từ ngày 12/11/2026 đến ngày 15/11/2026. Ngày 23/11/2026, người phụ trách xác nhận năm người viết ngày 16/11/2026 đều là người đã viết ở đợt thu đầu, nên đã có phiếu đồng ý. Người thu đã cấp mã mới cho họ thay vì dùng lại mã cũ, nên tệp không cho biết buổi mới nào thay buổi cũ nào.

Theo `tools/thu-net/quy-trinh-thu.md`, mục 1, mỗi người chỉ thuộc một nhóm và chỉ viết một buổi. Vì vậy cần biết mã cũ của từng người viết lại. Nếu người đó trước đây viết ở nhóm kiểm thử, buổi kiểm thử của họ phải bị loại, vì mô hình đã được chỉnh trên chữ của họ. Nếu người đó trước đây viết ở nhóm chỉnh, nhóm chỉnh chỉ giữ một buổi của họ. So nét chữ trên cùng câu đề không đủ chắc để ghép mã. Trong lúc chờ, nhóm kiểm thử giữ nguyên như mục 10.12 và chưa được dùng.

Bảng 23 ghi kết quả đo lại nhóm chỉnh với `m1l_rr_e100` và cấu hình triển khai, độ dày nét 1,2, sau khi bỏ 12 dòng chép khác đề. Cột 5 buổi là lần đo ngày 16/11/2026 ở mục 10.12, gồm 4 buổi A và buổi NV-34C4. Hai nhóm đổi chéo viết cùng 20 câu đề, chỉ đổi chéo câu nào viết liền và câu nào viết ngắt.

Bảng 23: CER (2) của M2 trên nhóm chỉnh trước và sau khi thay dữ liệu

| Kịch bản | 5 buổi, ngày 16/11/2026 | 9 buổi | 4 buổi A | 5 buổi B mới |
| --- | --- | --- | --- | --- |
| Số dòng liền và dòng ngắt | 48 và 49 | 87 và 81 | 38 và 39 | 49 và 42 |
| Dòng liền | 15,02% | 12,43% | 15,48% | 10,07% |
| Dòng ngắt sau khi ghép | 17,22% | 14,60% | 15,90% | 13,40% |
| Gộp dòng liền và dòng ngắt ghép | 16,13% | 13,48% | 15,69% | 11,61% |
| Dòng ngắt, nhận dạng từng hàng | 29,46% | 26,11% | 26,96% | 25,32% |

Theo Bảng 23, CER (2) gộp giảm từ 16,13% xuống 13,48%, vì mô hình đọc năm người viết mới tốt hơn. Nhóm B mới có CER gộp 11,61%, so với 15,69% của nhóm A. Dòng ngắt sau khi ghép vẫn cao hơn dòng liền 2,17 điểm phần trăm, nhưng thấp hơn cách nhận dạng từng hàng 11,51 điểm phần trăm. CER của dòng ngắt ghép theo người viết trải từ 4,28% đến 23,20%, như lần đo trước. Với độ dày nét 1,0; 1,2 và 1,5, CER (2) của dòng liền là 13,34%; 12,43% và 13,16%, còn của dòng ngắt ghép là 14,84%; 14,60% và 14,68%, nên độ dày 1,2 vẫn được giữ.

Dòng ngắt mô phỏng 2, 4 và 6 chỗ nối có CER (2) 13,60%; 15,49% và 17,53%, tức tăng 1,17; 3,06 và 5,10 điểm phần trăm so với dòng liền. Hai dòng liền có nét lạc của NV-GPQJ vẫn có CER 70,7% và 89,4%, và nếu bỏ hai dòng này thì CER (2) của dòng liền là 10,84%. Các số trên vẫn là số tạm, vì nhóm chỉnh mới có 9 trên 10 người và còn thiếu 1 người nhóm A. Kết quả đo nằm ở `~/vnhw/runs/m1l_rr_e100/nhom-chinh-9/`.

### 10.14. Sửa công cụ thu sau đợt thu thứ hai

Ở màn rà soát, mỗi dòng được thu nhỏ cho vừa bề ngang màn hình. Dòng liền của đợt thu thứ hai rộng từ 1.273 đến 2.314 điểm ảnh CSS, nên trên điện thoại rộng khoảng 390 điểm ảnh, chữ chỉ còn cao khoảng 19 điểm ảnh và gần như không đọc được dấu. Trong 9 dòng chép khác đề bị sót ở mục 10.13, có 8 dòng là dòng liền. Bản công cụ ngày 23/11/2026 có ba thay đổi:

- Dòng liền ở màn rà soát được cắt thành nhiều đoạn xếp chồng, mỗi đoạn có băng viết cao khoảng 56 điểm ảnh, hai đoạn liền nhau chồng lên nhau 30 điểm ảnh.
- Người thu rà dưới 10 giây một dòng thì công cụ nhắc đọc lại và phải bấm Hoàn tất lần nữa. Tệp ghi thêm thời gian rà soát và việc đã bị nhắc hay chưa.
- Ở đợt thu chính thức, người thu phải xác nhận người viết chưa từng viết ở đợt thu nào. Người viết lại theo yêu cầu của người phụ trách phải dùng lại mã cũ. Tệp ghi thêm trường `firstSession`.

Bảng máy Android có thêm 25 mã máy Galaxy A đời cũ, gồm A12, A13 và A33 5G của đợt thu thứ hai, để không phải đo bằng thẻ. Quy trình thu `tools/thu-net/quy-trinh-thu.md` được sửa theo. Bản mới chưa được đăng lên đường link của công cụ.

### 10.15. Bộ lọc nét lạc trong lớp ghép đoạn

Ở mục 10.12 và mục 10.13, các dòng có nét lạc có CER từ 70% đến 89%. Nét lạc gồm hai loại. Loại thứ nhất là chấm chạm nhầm nằm cách dòng chữ từ 2,3 đến 15 lần chiều cao thân chữ. Loại thứ hai là một nét quẹt dọc cao 992 điểm ảnh, gấp khoảng 24 lần chiều cao thân chữ. Bước vẽ ảnh co dòng theo khung bao của mọi nét, nên một nét lạc làm chữ thật co lại còn vài điểm ảnh.

Luật sau được ghi trước khi đo. Sau khi gán nét vào dòng chữ, lớp ghép đoạn bỏ một nét khi thỏa một trong hai điều kiện, với $h$ là chiều cao thân chữ của dòng chữ chứa nét đó:

- Khoảng cách theo chiều dọc từ nét tới dải thân chữ, tức khoảng giữa đỉnh thân chữ và đường chân chữ, lớn hơn $2h$.
- Nét cao hơn $5h$.

Dấu thanh và chân chữ nằm trong khoảng $1h$ quanh dải thân chữ, còn chữ cao nhất như g, h, y cao khoảng $3h$, nên luật không chạm tới nét của chữ. Luật được nhận khi đạt cả ba tiêu chí sau, với độ dày nét 1,2 và cấu hình triển khai:

1. CER (2) gộp dòng liền và dòng ngắt ghép trên 9 buổi nhóm chỉnh thấp hơn 13,48% ở Bảng 23.
2. CER (2) trên hai buổi thử viết bằng S Pen và buổi thử viết bằng ngón tay của mục 10.6 và mục 10.10 không tăng quá 0,2 điểm phần trăm ở mọi kịch bản.
3. Mọi nét bị bỏ ở các dòng không ghi là có nét lạc đều được xem bằng mắt, và không nét nào là một phần của chữ hay dấu.

Hai ngưỡng $2h$ và $5h$ không được chỉnh theo kết quả đo. Nếu luật không đạt, ngưỡng mới phải được ghi trước ở một mục mới. Bộ lọc không chạy trên nhóm kiểm thử trước bước 7.

Tiêu chí 3 được xét trước, vì không cần chạy mô hình. Trên nhóm chỉnh và ba buổi thử, luật bỏ 27 nét. Ở dòng liền, 13 nét bị bỏ đều là nét lạc thật, gồm các chấm chạm nhầm và nét quẹt dọc của NV-GPQJ. Ở dòng ngắt, 3 trên 14 nét bị bỏ là chấm lạc thật. 11 nét còn lại là nét nhỏ của hàng dưới mà bước gán nét đã xếp nhầm lên hàng trên, như một dấu phẩy, chấm của chữ i và một mẩu nét của chữ g. Vì vậy luật không đạt tiêu chí 3 và không được đo CER. Luật sửa được ghi ở mục 10.16.

### 10.16. Bộ lọc nét lạc có chuyển hàng

Mục 10.15 cho thấy ở dòng ngắt, nét nằm xa dải thân chữ của hàng chứa nó thường là nét của một hàng khác bị gán nhầm, chứ không phải nét lạc. Luật sau được ghi trước khi đo, sau khi đã xem danh sách nét bị bỏ của mục 10.15 nhưng chưa chạy mô hình lần nào:

- Nét cao hơn $5h$ bị bỏ, với $h$ là chiều cao thân chữ của hàng chứa nét.
- Nét cách dải thân chữ của hàng chứa nó không quá $2h$ thì giữ ở hàng đó.
- Nét cách xa hơn $2h$ được chuyển sang hàng có dải thân chữ gần nhất, nếu khoảng cách tới dải đó không quá $2h$ của hàng đó. Nếu không có hàng nào như vậy, nét bị bỏ.

Ở dòng liền chỉ có một hàng, nên luật này cho cùng kết quả với luật ở mục 10.15. Luật được nhận theo ba tiêu chí của mục 10.15, trong đó tiêu chí 3 xét cả nét bị bỏ lẫn nét bị chuyển hàng: không nét nào của chữ hay dấu bị bỏ, và không nét nào bị chuyển sang sai hàng. Hai ngưỡng vẫn là $2h$ và $5h$.

Luật đạt tiêu chí 3. Luật bỏ 16 nét, đều là chấm lạc hoặc nét quẹt thật, và chuyển 11 nét về đúng hàng chứa chúng. Lần đo không bộ lọc cho lại đúng các số của Bảng 23, nên hai lần đo chỉ khác nhau ở bộ lọc. Trên 9 buổi nhóm chỉnh, CER (2) của dòng liền giảm từ 12,43% xuống 10,75%, còn của dòng ngắt ghép tăng từ 14,60% lên 14,93%. CER (2) gộp giảm từ 13,48% xuống 12,77%, nên luật đạt tiêu chí 1. Hai dòng NV-GPQJ có nét lạc giảm từ 70,7% xuống 26,0% và từ 89,4% xuống 3,0%.

Luật không đạt tiêu chí 2. Ở buổi thử viết bằng ngón tay, CER (2) của dòng mô phỏng 4 và 6 chỗ nối tăng 0,53 và 2,21 điểm phần trăm. Phần tăng đến từ vài dòng có nét bị chuyển hàng, trong khi ở hai buổi thử viết bằng S Pen, mọi kịch bản đều giảm hoặc tăng không quá 0,17 điểm phần trăm. Ở dòng ngắt thật, chuyển một nét đúng hàng vẫn làm CER của dòng thay đổi tới 0,12, theo cả hai chiều, nên bước chuyển hàng không có lợi rõ ràng. Theo luật đã ghi trước, luật này không được nhận. Kết quả đo nằm ở `~/vnhw/runs/m1l_rr_e100/loc-net-lac/`.

### 10.17. Bộ lọc chỉ bỏ nét lạc xa mọi hàng

Mục 10.16 cho thấy phần lợi đến từ việc bỏ nét lạc ở dòng liền, còn bước chuyển hàng có hại. Luật sau được ghi trước khi đo:

- Nét cao hơn $5h$ bị bỏ, với $h$ là chiều cao thân chữ của hàng chứa nét.
- Nét cách dải thân chữ của mọi hàng xa hơn $2h$ của hàng đó thì bị bỏ.
- Mọi nét khác giữ nguyên ở hàng mà bước gán nét đã chọn, không chuyển hàng.

Ở dòng liền, luật này cho cùng kết quả với luật ở mục 10.15 và mục 10.16. Luật được nhận theo ba tiêu chí của mục 10.15. Hai ngưỡng vẫn là $2h$ và $5h$. Nếu luật này không đạt, đề tài giữ lớp ghép đoạn như cũ và không thử thêm luật nào trên các dữ liệu này.

Luật đạt tiêu chí 3, vì chỉ bỏ 16 nét lạc thật và không chuyển nét nào. Trên 9 buổi nhóm chỉnh, CER (2) của dòng liền giảm từ 12,43% xuống 10,75%, của dòng ngắt ghép tăng từ 14,60% lên 14,87%, và CER (2) gộp giảm từ 13,48% xuống 12,74%, nên luật đạt tiêu chí 1. Phần tăng ở dòng ngắt đến từ hai dòng của NV-5JCD, nơi bỏ 3 chấm lạc thật vẫn làm CER thay đổi theo chiều xấu. Ở hai buổi thử viết bằng S Pen, mọi kịch bản cho đúng số của lần đo không bộ lọc.

Luật không đạt tiêu chí 2. Ở buổi thử viết bằng ngón tay, CER (2) của dòng mô phỏng 4 và 6 chỗ nối vẫn tăng 0,53 và 2,21 điểm phần trăm như ở mục 10.16. Các dòng đổi kết quả đều là dòng mô phỏng của những dòng liền không có nét lạc. Nguyên nhân có thể là một hàng mô phỏng chỉ có vài nét ngắn, nên chiều cao thân chữ của hàng rất nhỏ và nét bình thường bị coi là quá cao. Điều này chưa được kiểm chứng.

Theo điều đã ghi trước khi đo, lớp ghép đoạn giữ như cũ và không thử thêm luật nào trên các dữ liệu này. Hàm `clean_rows` vẫn nằm trong `training/ink.py` nhưng tắt theo mặc định, còn ứng dụng không dùng. Lệnh `eval_selfcollected.py --drop-strays` bật lại bộ lọc để đo. Một luật mới, ví dụ đặt sàn cho chiều cao thân chữ khi xét nét quá cao, chỉ được thử trên dữ liệu nhóm chỉnh thu sau ngày 23/11/2026 và phải ghi trước ở một mục mới.

### 10.18. Đợt thu thứ ba của nhóm chỉnh

Ngày 24/11/2026, đề tài nhận đợt thu thứ ba, gồm 20 buổi thu từ ngày 17/11/2026 đến ngày 19/11/2026 bằng bản công cụ 2026-11-15 mở ngoài khung claude.ai, cùng 20 phiếu đồng ý. Cả 20 buổi thuộc nhóm chỉnh, viết bằng ngón tay trên điện thoại, đủ 20 dòng và đúng câu đề đã khóa, gồm 11 buổi nhóm A và 9 buổi nhóm B. Tệp NV-8ZS8 là tệp gộp theo lược đồ `thu-net-bundle/1`, chứa một buổi. Không buổi nào và không dòng nào trùng nét với 35 buổi của ba đợt thu.

Buổi NV-EM4Y không dùng được. Cả 20 dòng chỉ viết hai chữ "Đó là", mỗi dòng khoảng 3 giây. Tên máy ghi trong tệp là iPhone 14 Pro, trong khi chuỗi nhận dạng trình duyệt là của một máy OPPO, và số đo bằng thẻ 55 mm ứng với màn hình khoảng 5,3 inch. Buổi này được để riêng ở `~/vnhw/data/nhom-chinh-de-rieng/`.

Bảng 24 ghi năm buổi còn lại được đo bằng thẻ, vì máy không có trong bảng máy của bản công cụ 2026-11-15. Bề rộng theo thông số được tính từ đường chéo và độ phân giải của máy. Hàng kẻ thật bằng 12 mm nhân với tỷ số giữa bề rộng theo thông số và số đo bằng thẻ.

Bảng 24: Năm buổi đo bằng thẻ của đợt thu thứ ba

| Mã | Nhóm | Máy | Số đo bằng thẻ | Bề rộng theo thông số máy | Hàng kẻ thật |
| --- | --- | --- | --- | --- | --- |
| NV-28E5 | B | Galaxy A12 | 70 mm, dùng lại số đo của NV-8GTX | 67,8 mm | Khoảng 11,6 mm |
| NV-2SVT | B | Redmi K40 Gaming | 70 mm | 69,5 mm | Khoảng 11,9 mm |
| NV-6BYK | B | Galaxy A13 | 67 mm, dùng lại số đo của NV-DQK4 | 68,6 mm | Khoảng 12,3 mm |
| NV-DT73 | B | iQOO Z9 Turbo | 65 mm | 70,7 mm | Khoảng 13,0 mm |
| NV-EMBS | A | Redmi Note 9S | 65 mm | 69,5 mm | Khoảng 12,8 mm |

Công cụ lưu số đo bằng thẻ trong trình duyệt và dùng lại ở lần mở sau trên cùng máy. Vì vậy NV-28E5 và NV-6BYK được thu trên đúng máy và trình duyệt của NV-8GTX và NV-DQK4 ở mục 10.13. Khung thẻ bắt đầu ở cỡ của màn hình rộng 70 mm, nên số 70 mm của NV-2SVT và NV-8GTX cho thấy người thu đã không chỉnh khung. Hai số này chỉ tình cờ lệch thông số máy 0,7% và 3,3%. Quy tắc nhận được đặt trước khi xem kết quả của mô hình trên đợt này: hàng kẻ thật lệch 12 mm không quá 10%. Theo Bảng 24, cả năm buổi đều đạt, với hàng kẻ thật từ khoảng 11,6 đến 13,0 mm. Mười bốn buổi còn lại lấy bề rộng từ bảng máy.

Hai mươi phiếu đồng ý đều điền đủ họ tên, chữ ký và ngày 18/11/2026 hoặc 19/11/2026, do hai người thu ký. Bảy phiếu là bản chép của phiếu đợt đầu, chỉ đổi ngày, nên bảy người viết của đợt này đã viết ở đợt đầu. Đợt đầu có 6 người nhóm chỉnh và 4 người nhóm kiểm thử, nên ít nhất một người nhóm kiểm thử của đợt đầu đã viết cho nhóm chỉnh. Phiếu không ghi mã, nên không biết buổi nào của đợt này là của bảy người đó.

Thông tin máy trong tệp cho thêm manh mối. Ngoài hai cặp dùng chung số đo bằng thẻ, NV-FUY3, NV-8E9T và NV-QZ3F có cùng đời máy và cùng chuỗi nhận dạng trình duyệt, kể cả phiên bản hệ điều hành, với NV-H8XR, NV-5JCD và NV-GPQJ. Vì người viết dùng máy của mình, 5 trong 9 buổi nhóm chỉnh ở mục 10.13 có lẽ do người của đợt này viết.

Từ các điểm trên, đề tài chốt hai việc:

- **Mười chín buổi đủ điều kiện:** 10 buổi A và 9 buổi B được chép vào `~/vnhw/data/nhom-chinh-dot3/`. Mỗi buổi có một phiếu riêng và thu trên một máy riêng, nên 19 buổi là của 19 người khác nhau. Vai trò của 19 buổi này được chốt ở mục 10.19.
- **Hai buổi nhóm kiểm thử của đợt đầu:** NV-BXDB và NV-542R được để riêng cùng hai buổi trên iPad ở `~/vnhw/data/nhom-kiem-thu-de-rieng/`, vì có thể là của người đã viết cho nhóm chỉnh.

Người thu chọn Chép đúng cho cả 380 dòng của 19 buổi. Thời gian rà soát mỗi buổi từ 26 đến 552 giây, trung vị 152 giây. Đề tài rà soát lại cả 380 dòng bằng mắt trên ảnh vẽ từ nét gốc, có đối chiếu kết quả đọc của mô hình như mục 10.13. Kết quả là 42 dòng chép khác đề ở 16 trên 19 buổi, gồm 26 dòng liền và 16 dòng ngắt. Trong đó, 19 dòng nằm ở 6 trong 8 buổi rà soát lâu hơn 10 giây mỗi dòng, nên rà soát lâu hơn chưa đủ để bắt các dòng này. Có 22 dòng thiếu một hoặc hai từ, 7 dòng viết "sinh nhau" thay cho "sinh nhai", trong đó 6 dòng là dòng liền của nhóm A, 6 dòng đổi một từ, như "phù hợp" thay cho "kết hợp" và "tranh cãi" thay cho "tranh luận", và 3 dòng thừa một từ. Bốn dòng còn lại gồm một chữ viết dở, một cặp từ đảo thứ tự, một chữ bị gạch và một chữ thừa. Dòng có chữ bị gạch hoặc chữ thừa cũng bị loại, vì nét mực không còn khớp với nhãn. Dòng chỉ khác dấu câu được giữ như các lần rà soát trước, và năm dòng có nét lạc xa dòng chữ cũng được giữ. Kết quả rà soát nằm ở `~/vnhw/data/nhom-chinh-dot3/review.json`.

Bảng 25 ghi kết quả đo 19 buổi này với `m1l_rr_e100` và cấu hình triển khai, độ dày nét 1,2, sau khi bỏ 42 dòng chép khác đề. Cột 9 buổi nhóm chỉnh lấy từ Bảng 23 để so.

Bảng 25: CER (2) của M2 trên 19 buổi của đợt thu thứ ba

| Kịch bản | 9 buổi nhóm chỉnh | 19 buổi đợt 3 | 10 buổi A | 9 buổi B |
| --- | --- | --- | --- | --- |
| Số dòng liền và dòng ngắt | 87 và 81 | 164 và 174 | 83 và 94 | 81 và 80 |
| Dòng liền | 12,43% | 10,34% | 8,39% | 12,34% |
| Dòng ngắt sau khi ghép | 14,60% | 14,69% | 12,39% | 17,39% |
| Gộp dòng liền và dòng ngắt ghép | 13,48% | 12,58% | 10,52% | 14,85% |
| Dòng ngắt, nhận dạng từng hàng | 26,11% | 26,83% | 22,76% | 31,61% |

Theo Bảng 25, CER (2) gộp của 19 buổi là 12,58%, thấp hơn 0,90 điểm phần trăm so với 9 buổi nhóm chỉnh. Dòng liền thấp hơn 2,09 điểm phần trăm, còn dòng ngắt sau khi ghép gần như không đổi. Vì vậy dòng ngắt ghép cao hơn dòng liền 4,34 điểm phần trăm, so với 2,17 điểm phần trăm ở nhóm chỉnh, dù vẫn thấp hơn cách nhận dạng từng hàng 12,15 điểm phần trăm. Dòng ngắt mô phỏng 2, 4 và 6 chỗ nối có CER (2) 11,91%; 12,62% và 14,44%, tức tăng 1,57; 2,28 và 4,10 điểm phần trăm so với dòng liền, nên dòng ngắt thật sau khi ghép còn cao hơn dòng mô phỏng 6 chỗ nối. CER theo người viết trải từ 3,10% đến 27,21% với dòng liền và từ 6,84% đến 34,73% với dòng ngắt ghép, và NV-E4UA cao nhất ở cả hai. Nhóm A thấp hơn nhóm B 4,33 điểm phần trăm ở CER gộp. Nếu không bỏ 42 dòng chép khác đề, CER (2) là 10,54% với dòng liền và 15,04% với dòng ngắt ghép.

Với độ dày nét 1,0; 1,2 và 1,5, CER (2) gộp là 12,71%; 12,58% và 12,51%. Quy tắc chọn được đặt trước khi xem kết quả: chọn độ dày có CER (2) gộp thấp nhất, nhưng giữ 1,2 nếu độ dày đó chỉ thấp hơn 1,2 không quá 0,2 điểm phần trăm, vì đổi độ dày phải sinh lại tệp cho ứng dụng và đo lại. Độ dày 1,5 thấp hơn 1,2 là 0,07 điểm phần trăm, nên độ dày 1,2 được giữ.

Kết quả đo nằm ở `~/vnhw/runs/m1l_rr_e100/nhom-chinh-dot3/`.

### 10.19. Chốt cấu hình và tập đánh giá viết bằng ngón tay

Ngày 24/11/2026, người phụ trách cho biết đề tài không thu thêm dữ liệu. Đề tài vì vậy kết thúc bước 6 của `05-ke-hoach-thi-nghiem.md`, mục 4, và chốt ba việc:

- **Cấu hình:** `m1l_rr_e100` bản float16, $\alpha = 0{,}45$, $\beta = 4$, beam 30, độ dày nét 1,2, lớp ghép đoạn không bật bộ lọc nét lạc. Đây là cấu hình của ứng dụng theo mục 11.
- **Nhóm chỉnh:** 9 buổi ở mục 10.13. Trên nhóm này, phép kiểm tra độ dày nét và ba luật lọc nét lạc ở mục 10.15 đến mục 10.17 đều giữ nguyên cấu hình.
- **Tập đánh giá:** 19 buổi của đợt thu thứ ba ở mục 10.18, thay cho nhóm kiểm thử ở `03-du-lieu.md`, mục 6. Tập này dùng cho hai kịch bản Ngắt mô phỏng và Viết tay thật của `02-yeu-cau-va-danh-gia.md`, mục 3.

Cấu hình này đã có trong ứng dụng từ trước khi nhận đợt thu thứ ba, và phép kiểm tra độ dày nét ở mục 10.18 cũng giữ 1,2, nên không tham số nào được đổi theo tập đánh giá. Đề tài không đo lại thứ tự các cấu hình của bước 3 trên dữ liệu ngón tay, để tập đánh giá chỉ được đo với một cấu hình. Phép đo ngày 24/11/2026 ở mục 10.18 là lần đo duy nhất của tập đánh giá, và kết quả cuối nằm ở mục 12.2. Nhóm chỉnh và tập đánh giá chép cùng 20 câu đề của nhóm chỉnh, và có chung một số người viết, theo mục 10.18. Hai buổi NV-BXDB và NV-542R không được dùng.

## 11. Mô hình đưa vào ứng dụng

Mục này ghi các bước sau khi chọn `m1l_rr_e100`, theo bước 5 của `05-ke-hoach-thi-nghiem.md`, mục 4. Các bước gồm chỉnh lại trọng số n-gram, kiểm tra độ dày nét, chuyển đổi sang LiteRT, phân tích lỗi và đưa mô hình vào ứng dụng.

### 11.1. Trọng số n-gram

Đề tài chỉnh lại $\alpha$ và $\beta$ theo cách của mục 4, gồm hai bước. Bước đầu dò lưới trên 410 dòng kiểm định với mô hình Keras, gồm 4 giá trị của $\alpha$ từ 0,3 đến 0,8 và 6 giá trị của $\beta$ từ 1 đến 8. Cặp $\alpha = 0{,}45$ và $\beta = 3$ cho CER (2) thấp nhất, 6,13%, còn cặp đang dùng $\alpha = 0{,}45$ và $\beta = 4$ cho 6,17%. Bước sau đo hai cặp này với cấu hình triển khai trên cả 1.229 dòng kiểm định và trên nét viết thật, ghi ở Bảng 26.

Bảng 26: Hai cặp trọng số n-gram của `m1l_rr_e100` với cấu hình triển khai

| Cặp trọng số | Kiểm định, CER (2) | Kiểm định, WER (2) | Kiểm định, CER (1) | Kiểm định, WER (1) | Nét viết thật, ngắt ghép và liền |
| --- | --- | --- | --- | --- | --- |
| $\alpha = 0{,}45$, $\beta = 3$ | 6,615% | 17,57% | 5,98% | 16,52% | 16,33% |
| $\alpha = 0{,}45$, $\beta = 4$ | 6,613% | 17,71% | 5,99% | 16,68% | 15,98% |

Theo Bảng 26, hai cặp gần như bằng nhau trên tập kiểm định. Cặp $\beta = 4$ thấp hơn 0,002 điểm phần trăm ở CER (2), còn cặp $\beta = 3$ thấp hơn từ 0,01 đến 0,17 điểm phần trăm ở ba chỉ số còn lại. Trên nét viết thật, cặp $\beta = 4$ thấp hơn 0,34 điểm phần trăm, khoảng tin cậy theo người viết từ giảm 0,64 đến tăng 0,03. Đề tài giữ $\alpha = 0{,}45$ và $\beta = 4$, vì cặp này có CER (2) thấp nhất trên tập kiểm định và nét viết thật cho cùng chiều. Tệp `params.txt` của ứng dụng vì vậy không đổi.

Với cặp $\beta = 3$ và mô hình Keras, tăng độ rộng beam từ 30 lên 50 chỉ giảm CER (2) thêm 0,07 điểm phần trăm, nên đề tài giữ độ rộng 30.

### 11.2. Độ dày nét

Với $\alpha = 0{,}45$ và $\beta = 4$, độ dày nét 1,0; 1,2 và 1,5 điểm ảnh cho CER (2) của nhóm ngắt ghép và liền lần lượt là 16,79%, 15,98% và 16,59%. So với độ dày 1,2, độ dày 1,0 tăng 0,81 điểm phần trăm, khoảng tin cậy từ giảm 0,09 đến tăng 1,57. Độ dày 1,5 tăng 0,61 điểm phần trăm, khoảng tin cậy từ 0,18 đến 1,06. Độ dày 1,2 cũng thấp nhất khi tách riêng dòng ngắt ghép và dòng liền, nên ứng dụng giữ độ dày này. Riêng khi nhận dạng từng hàng, độ dày 1,0 thấp hơn 1,77 điểm phần trăm, nhưng ứng dụng không dùng cách này.

### 11.3. Chuyển đổi sang LiteRT

Bảng 27 ghi kết quả chuyển đổi `m1l_rr_e100`, đo như Bảng 4 nhưng trên 200 dòng kiểm định lấy cách đều. Thời gian được đo khi máy đang huấn luyện lần chạy khác, nên chỉ dùng để so giữa các bản.

Bảng 27: Kết quả chuyển đổi mô hình `m1l_rr_e100` sang LiteRT

| Bản | Dung lượng | CER (2) | Số dòng giống bản Keras | Thời gian trung vị một dòng |
| --- | --- | --- | --- | --- |
| Keras | Không đo | 8,22% | 200 | Không đo |
| LiteRT, chưa lượng tử hóa | 8,92 MB | 8,28% | 185 | 39,8 ms |
| LiteRT, lượng tử hóa float16 | 4,47 MB | 8,29% | 185 | 38,0 ms |
| LiteRT, lượng tử hóa dynamic range | 2,26 MB | 8,86% | 80 | 21,7 ms |

Theo Bảng 27, dynamic range làm CER tăng 0,64 điểm phần trăm so với bản Keras, gần bằng mức 0,61 điểm phần trăm của `m1_v2` ở Bảng 4. Float16 chỉ làm CER tăng 0,07 điểm phần trăm, nên đề tài giữ float16. Bản float16 nặng 4,47 MB, gấp khoảng 2,2 lần bản float16 của `m1_v2`. Khi đo cấu hình triển khai trên máy tính, mô hình chạy chậm hơn `m1_rr_e100` khoảng 2,6 lần, nên độ trễ phải đo lại trên điện thoại thật.

### 11.4. Phân tích lỗi

Với cấu hình triển khai, `m1l_rr_e100` đạt CER (2) 6,61% và WER (2) 17,71% trên tập kiểm định, theo Bảng 26. So với `m1_v2` ở Bảng 5, CER (2) giảm 1,61 điểm phần trăm và WER (2) giảm 4,32 điểm phần trăm. Bảng 28 so CER sau khi bỏ dấu của hai mô hình. Cột của `m1_v2` lấy từ Bảng 6, còn cột của `m1l_rr_e100` dùng cấu hình triển khai. CER theo độ dài dòng của `m1l_rr_e100` nằm ở Bảng 7.

Bảng 28: CER của M2 sau khi bỏ dấu trên 1.229 dòng kiểm định, `m1_v2` và `m1l_rr_e100`

| Cách tính | `m1_v2`, CER (2) | `m1_v2`, CER (1) | `m1l_rr_e100`, CER (2) | `m1l_rr_e100`, CER (1) |
| --- | --- | --- | --- | --- |
| Giữ nguyên | 8,20% | 7,24% | 6,61% | 5,99% |
| Bỏ dấu thanh | 7,51% | 6,62% | 6,12% | 5,54% |
| Bỏ dấu thanh và dấu phụ | 7,06% | 6,20% | 5,74% | 5,19% |

Theo Bảng 28, dấu thanh gây 0,49 điểm phần trăm CER (2) của `m1l_rr_e100`, còn dấu thanh và dấu phụ gây 0,88 điểm phần trăm. Hai mức này thấp hơn mức 0,69 và 1,14 điểm phần trăm của `m1_v2`. So với `m1_v2`, phần lỗi do dấu chỉ giảm 0,26 điểm phần trăm, còn CER sau khi bỏ mọi dấu giảm 1,32 điểm phần trăm. Phần lớn mức giảm CER vì vậy đến từ việc đọc đúng chữ cái hơn, không phải đọc đúng dấu hơn.

Các cặp hay nhầm nhất vẫn giống `m1_v2`: m và n, n và u, và chữ hoa với chữ thường như C và c, T và t. Lỗi xóa và lỗi chèn hay gặp nhất là dấu cách, với 172 lần xóa và 128 lần chèn, nên một phần lỗi từ đến từ việc tách hoặc nối nhầm âm tiết. Trên 1.229 dòng có 3.511 lỗi thay, 1.009 lỗi xóa và 502 lỗi chèn, so với 4.007, 1.522 và 539 của `m1_v2`.

### 11.5. Đưa vào ứng dụng

Mã `training/export_assets.py` sinh lại các tệp đi kèm từ `m1l_rr_e100`, với $\alpha = 0{,}45$, $\beta = 4$ và độ dày nét 1,2. Chỉ tệp `model.tflite` thay đổi, còn `lm.bin`, `chars.txt` và `params.txt` giống hệt bản trước, kiểm tra bằng mã băm SHA-256. Tổng dung lượng các tệp đi kèm là 15,43 MB, dưới ngưỡng 20 MB. Kết quả đối chiếu Python với Kotlin và chạy thử trên máy ảo nằm ở `06-trien-khai-android.md`, mục 3.

## 12. Kết quả cuối

Mục này ghi kết quả của bước 7 ở `05-ke-hoach-thi-nghiem.md`, mục 4, với cấu hình chốt ở mục 10.19. Mỗi tập chỉ được đo một lần.

### 12.1. Tập kiểm thử VNOnDB

Ngày 24/11/2026, đề tài chạy 1.634 dòng kiểm thử của VNOnDB một lần bằng `training/eval_deployed.py` với cờ `--confirm-test`. Bảng 29 ghi kết quả, cùng kết quả của cấu hình này trên tập kiểm định ở Bảng 26 để so. Các nguồn của mốc so sánh không nêu cách tính trung bình, nên bảng ghi cả hai công thức của CER và WER. Dòng cuối là M1 giải mã đơn giản, tức cùng mô hình nhưng không dùng n-gram.

Bảng 29: Kết quả của cấu hình chốt trên tập kiểm thử VNOnDB

| Chỉ số | Tập kiểm định, 1.229 dòng | Tập kiểm thử, 1.634 dòng |
| --- | --- | --- |
| CER (2) của M2 | 6,61% | 5,97% |
| CER (1) của M2 | 5,99% | 5,59% |
| WER (2) của M2 | 17,71% | 16,29% |
| WER (1) của M2 | 16,68% | 15,47% |
| CER (2) của M1 | 8,31% | 7,79% |

Theo Bảng 29, CER (2) của M2 trên tập kiểm thử là 5,97%, đạt ngưỡng không quá 8,4% và thấp hơn mục tiêu cao hơn 7,6% ở `02-yeu-cau-va-danh-gia.md`, mục 1. Mọi chỉ số trên tập kiểm thử đều thấp hơn trên tập kiểm định, từ 0,40 đến 1,42 điểm phần trăm, nên các lựa chọn làm trên tập kiểm định không cho thấy dấu hiệu quá khớp. So với các mốc dạng ảnh ở `02-yeu-cau-va-danh-gia.md`, Bảng 3, CER của M2 theo cả hai công thức nằm giữa HTR-VT với 4,26% và OrigamiNet với 7,6%, và WER cũng nằm giữa hai mốc này. Mô hình có 2,23 triệu tham số, so với 53,5 triệu của HTR-VT và 39,1 triệu của OrigamiNet. Khi không dùng n-gram, CER (2) của M1 là 7,79%, gần mức 7,6% của OrigamiNet. Kết quả từng dòng nằm ở `~/vnhw/runs/m1l_rr_e100/deployed_test_pred.txt`.

### 12.2. Tập đánh giá viết bằng ngón tay

Bảng 30 ghi kết quả của 19 người viết trong tập đánh giá, lấy từ phép đo ở mục 10.18 với độ dày nét 1,2, sau khi bỏ 42 dòng chép khác đề. Khoảng tin cậy 95% lấy bằng bootstrap 10.000 lần, với đơn vị lấy mẫu lại là người viết, theo `02-yeu-cau-va-danh-gia.md`, mục 2.6.

Bảng 30: Kết quả trên tập đánh giá viết bằng ngón tay

| Kịch bản | Số dòng | CER (2) | Khoảng tin cậy 95% của CER (2) | WER (2) |
| --- | --- | --- | --- | --- |
| Viết tay thật, dòng liền | 164 | 10,34% | 8,07-12,87% | 24,81% |
| Viết tay thật, dòng ngắt sau khi ghép | 174 | 14,69% | 11,77-18,01% | 35,43% |
| Viết tay thật, gộp hai loại dòng | 338 | 12,58% | 10,16-15,35% | 30,28% |
| Viết tay thật, dòng ngắt nhận dạng từng hàng | 174 | 26,83% | 22,48-31,40% | 58,40% |
| Ngắt mô phỏng, 2 chỗ nối | 164 | 11,91% | 9,64-14,45% | 28,40% |
| Ngắt mô phỏng, 4 chỗ nối | 164 | 12,62% | 10,40-15,04% | 29,84% |
| Ngắt mô phỏng, 6 chỗ nối | 164 | 14,44% | 11,68-17,72% | 34,97% |

Theo Bảng 30, khi viết bằng ngón tay trên điện thoại, CER (2) của dòng liền là 10,34%, cao hơn tập kiểm thử VNOnDB 4,37 điểm phần trăm. So ghép cặp trên cùng người viết, dòng ngắt sau khi ghép cao hơn dòng liền 4,34 điểm phần trăm, khoảng tin cậy từ 2,43 đến 6,39, và thấp hơn cách nhận dạng từng hàng 12,15 điểm phần trăm, khoảng tin cậy từ 9,80 đến 14,33. Với dòng ngắt mô phỏng, lớp ghép đoạn làm CER tăng 1,57; 2,28 và 4,10 điểm phần trăm so với chính dòng đó viết liền khi có 2, 4 và 6 chỗ nối, với khoảng tin cậy từ 0,48 đến 2,72, từ 1,33 đến 3,23 và từ 2,61 đến 5,66. Nếu giữ cả 380 dòng, kể cả các dòng chép khác đề, CER (2) là 10,54% với dòng liền, 15,04% với dòng ngắt sau khi ghép và 27,61% với nhận dạng từng hàng. Kết quả từng dòng nằm ở `~/vnhw/runs/m1l_rr_e100/nhom-chinh-dot3/`.
