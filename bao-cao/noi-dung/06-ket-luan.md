@@khong-so
# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## Kết quả đạt được

Đề tài đã xây dựng hệ thống nhận dạng chữ viết tay tiếng Việt theo dòng, chạy ngay trên điện thoại Android, không cần mạng và cho phép ngắt dòng khi viết. Hệ thống gồm lớp ghép đoạn đưa dòng ngắt về một dòng ảo, bước vẽ dòng thành ảnh, mô hình gồm mạng tích chập hai chiều và hai lớp BiLSTM huấn luyện bằng CTC, và bộ giải mã beam search kết hợp mô hình ngôn ngữ n-gram âm tiết và n-gram ký tự. Các kết quả chính như sau:

- **Nhận dạng dòng liền:** trên tập kiểm thử VNOnDB, CER của bản đưa lên điện thoại là 5,97% và WER là 16,29%, đạt ngưỡng 8,4% và 24,2%, và thấp hơn mục tiêu cao hơn 7,6%. Kết quả này nằm giữa hai mốc dạng ảnh HTR-VT và OrigamiNet, trong khi mô hình chỉ có 2,23 triệu tham số.
- **Xử lý dòng ngắt:** ghép dòng ảo cho CER thấp hơn nhận dạng từng hàng 12,15 điểm phần trăm trên chữ viết bằng ngón tay. Mức tăng CER do lớp ghép đoạn là 1,57 điểm phần trăm với 2 chỗ nối, đạt ngưỡng 2 điểm phần trăm, và tăng lên 2,28 và 4,10 điểm phần trăm với 4 và 6 chỗ nối.
- **Viết bằng ngón tay:** trên tập đánh giá gồm 19 người viết bằng ngón tay trên điện thoại của mình, CER là 10,34% với dòng liền và 14,69% với dòng ngắt sau khi ghép.
- **Mô hình ngôn ngữ mức ký tự:** sau khi chốt cấu hình, n-gram ký tự 4,10 MB chấm điểm từng ký tự trong beam search, giảm CER trên nhóm chỉnh viết bằng ngón tay từ 13,48% xuống 10,80% và trên tập kiểm định từ 6,61% xuống 6,24%.
- **So sánh với ML Kit:** trên tập đánh giá, ML Kit đọc chữ tốt hơn mô hình của đề tài, với CER 5,24% so với 10,34% ở dòng liền. Nhưng ML Kit đọc nét gốc của dòng ngắt với CER 36,61%, và chỉ còn 6,92% khi nhận dòng ảo của lớp ghép đoạn, nên lớp ghép đoạn là phần đóng góp dùng được cả với bộ nhận dạng khác.
- **Chạy trên điện thoại:** mô hình và hai mô hình ngôn ngữ nặng tổng cộng 19,53 MB, dưới ngưỡng 20 MB. Bản Kotlin cho cùng kết quả với bản Python ở mọi bước, và ứng dụng chạy trọn luồng không cần mạng trên máy ảo và trên điện thoại thật.
- **Tập tự thu:** đề tài xây dựng công cụ thu nét chạy trên trình duyệt điện thoại, quy trình thu có phiếu đồng ý và mã ẩn danh, và thu được dữ liệu viết bằng ngón tay của hai nhóm người viết, kèm kết quả rà soát từng dòng.

Ngoài các kết quả trên, đề tài rút ra một số nhận xét về cách làm. Ảnh vẽ lại từ khung xương giúp mô hình học từ ảnh có sẵn đọc tốt hơn nét vẽ trên điện thoại. Độ dao động giữa các lần huấn luyện trên nét viết thật lớn hơn nhiều so với trên tập kiểm định, nên việc chọn mô hình cần nhiều hạt giống và tiêu chí chốt trước. Gán nét vào dòng chữ theo thứ tự viết đúng hơn gán theo đường kẻ, kể cả khi người viết không theo đường kẻ.

## Hướng phát triển

Từ kết quả hiện có, đề tài có thể phát triển theo các hướng sau:

- **Đo độ trễ trên điện thoại thật:** đo thời gian nhận dạng các dòng dài trên một điện thoại tầm trung, báo cáo trung vị và phân vị 95 theo mục 1.5.3, bằng bài đo trên thiết bị đã có ở mục 5.3.1.
- **Dùng thêm thông tin của nét:** ML Kit [@google2026b] đọc trực tiếp nét kèm thứ tự và thời điểm và đọc chữ tốt hơn mô hình chỉ đọc ảnh của đề tài. Mô hình có thể dùng thêm thông tin này, hoặc lớp ghép đoạn có thể đặt trước một bộ nhận dạng dùng nét.
- **Giảm mức tăng khi dòng bị ngắt nhiều lần:** thêm chỗ nối mô phỏng vào ảnh huấn luyện để mô hình quen với dòng ảo, và lọc nét lạc do chạm nhầm trước khi vẽ ảnh với luật được kiểm chứng trên dữ liệu mới.
- **Tinh chỉnh bằng nét viết ngón tay:** dùng thêm dữ liệu viết bằng ngón tay để tinh chỉnh mô hình, vì kiểu chữ là nguồn lỗi lớn nhất khi viết trên điện thoại.
- **Giảm cỡ mô hình và tăng tốc:** thử lượng tử hóa có tập hiệu chỉnh hoặc rút gọn mô hình để giảm thời gian chạy trên các máy cấu hình thấp.
- **Mở rộng phạm vi:** nhận dạng nhiều dòng liên tiếp, cho phép ngắt ở giữa từ, và cá nhân hóa theo từng người viết.
