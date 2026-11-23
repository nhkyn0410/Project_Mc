# Chủ đề 4 – Sử dụng dịch vụ điện toán đám mây: Nội dung thuyết trình

Nov 12, 2026 · @Kyn

## 1. Định hướng và phạm vi

Bài nói đi theo góc nhìn của người dùng dịch vụ: từ lúc chọn nhà cung cấp đến lúc xóa tài nguyên, bám một ví dụ xuyên suốt và có demo. Các nhóm khác trả lời “đám mây là gì”; nhóm 4 trả lời “bắt tay vào dùng thì làm gì”.

**Thông điệp chính:** dùng được đám mây nghĩa là chọn đúng dịch vụ, tạo được bằng nhiều cách, kiểm soát được chi phí và tự lo phần vận hành thuộc về mình.

**Căn cứ phạm vi.** Tên năm chủ đề của lớp trùng tên chương 1–5 trong giáo trình [Điện toán đám mây](https://thuvien.utm.edu.vn/ktpm/%C4%90i%E1%BB%87n%20to%C3%A1n%20%C4%91%C3%A1m%20m%C3%A2y%20v%C3%A0%20%E1%BB%A9ng%20d%E1%BB%A5ng.pdf) (Huỳnh Quyết Thắng chủ biên). Chương “Sử dụng dịch vụ” của giáo trình có ba mục: dịch vụ phần mềm, dịch vụ nền tảng, dịch vụ hạ tầng IaaS. Bài nói giữ đủ ba mục này và cập nhật công cụ đến tháng 11/2026.

Đây là suy luận từ tên chương, chưa phải đề cương của lớp. [Một đề cương công khai của học phần cùng tên](https://nctu.edu.vn/uploads/technology/2021_12/51_Dien_toan_dam_may.pdf) cũng xếp chương theo đúng thứ tự này; bạn nên đối chiếu với đề cương thầy cô phát.

**Ví dụ xuyên suốt:** một web app nhỏ của nhóm sinh viên, gồm API, cơ sở dữ liệu và ảnh người dùng tải lên, phục vụ vài trăm người dùng.

### Nội dung dễ trùng và cách xử lý

| Nội dung | Nhóm đã hoặc sẽ trình bày | Cách xử lý ở chủ đề 4 |
| --- | --- | --- |
| Định nghĩa IaaS, PaaS, SaaS; ai quản lý tầng nào; khi nào chọn mô hình nào | CĐ1, slide 12–19 | Không định nghĩa lại. Một câu dẫn, rồi vào thao tác sử dụng từng loại. |
| Năm đặc tính NIST, ảo hóa, bốn mô hình triển khai | CĐ1, slide 4–11 và 20–27 | Bỏ hẳn. |
| CapEx và OpEx, FinOps, Reserved Instances, Savings Plans | CĐ1, slide 5 và 28 | Chỉ nói phần thực hành: hóa đơn tính từ đâu, ước tính trước, đặt ngân sách, dọn tài nguyên. |
| Trách nhiệm chia sẻ, IAM, MFA | CĐ1 slide 17–18, CĐ2 slide 14, CĐ3 (dự kiến) | Gói trong một dòng ở danh sách thiết lập tài khoản. |
| Object, Block, File Storage; NoSQL; bảng dịch vụ lưu trữ của AWS, GCP, Azure; Presigned URL; case LMS | CĐ2, slide 3–13 | Không nhắc lại. Ví dụ xuyên suốt khác LMS. |
| Mã hóa, sao lưu 3-2-1-1-0, RPO và RTO | CĐ2 slide 14–15, CĐ3 (dự kiến) | Bỏ. |
| Mối đe dọa, kiểm soát truy nhập, kiến trúc bảo mật | CĐ3, theo mục 3.1–3.3 của giáo trình | Bỏ. Chỉ nêu yêu cầu lưu dữ liệu trong nước như một tiêu chí chọn nhà cung cấp. |
| Hệ thống giám sát, đảm bảo chất lượng dịch vụ, kiểm soát lỗi | CĐ5, theo mục 5.1–5.4 của giáo trình | Chạm nhẹ ở slide 15–16: đọc SLA và bốn việc người dùng phải tự bật. Kết bằng câu chuyển giao cho nhóm 5. |

### Phần riêng của chủ đề 4

- Bốn cách thao tác với đám mây: Console, CLI, SDK, IaC.
- Quy trình sử dụng cụ thể của từng loại dịch vụ: máy ảo, nền tảng, hàm serverless, SaaS.
- Gói dùng thử cho sinh viên, đặt ngân sách, tránh hóa đơn bất ngờ.
- Cách đọc SLA từ phía người dùng, kèm sự cố AWS tháng 10/2025 (giáp ranh chủ đề 5).
- Bảy chiến lược đưa hệ thống cũ lên mây (7R) và cách giữ đường lui.
- Bối cảnh Việt Nam: Local Zone Hà Nội của AWS, Điều 26 Nghị định 53/2022/NĐ-CP.

## 2. Dàn ý và thời lượng

Bản đầy đủ có 18 slide cho 20 phút, gồm 16 phút nói và 4 phút demo. Bản rút gọn khoảng 15 phút: bỏ bốn slide tùy chọn (6, 11, 16, 17) và thay demo trực tiếp bằng video 2 phút 30 giây.

Chưa rõ thời lượng lớp giao cho mỗi nhóm; con số 20 phút dựa trên ghi chú “15–20 phút” trong slide của nhóm CĐ2.

| Slide | Phần | Tiêu đề | Thời lượng | Ghi chú |
| --- | --- | --- | --- | --- |
| 1 | Mở đầu | Sử dụng dịch vụ điện toán đám mây | 0:20 |  |
| 2 | Mở đầu | Từ “biết” sang “dùng” | 1:00 | Số liệu mở bài, lộ trình sáu chặng |
| 3 | 1. Chuẩn bị | Chọn nhà cung cấp và Region | 1:10 |  |
| 4 | 1. Chuẩn bị | Năm việc làm ngay khi có tài khoản | 0:50 |  |
| 5 | 2. Cách thao tác | Bốn cách “nói chuyện” với đám mây | 1:10 |  |
| 6 | 2. Cách thao tác | Một máy chủ, ba cách tạo | 0:50 | Tùy chọn |
| 7 | 3. Dùng từng loại | Dùng IaaS: thuê và tự quản một máy ảo | 1:10 |  |
| 8 | 3. Dùng từng loại | Dùng PaaS: đưa mã lên, nền tảng lo phần còn lại | 1:10 |  |
| 9 | 3. Dùng từng loại | Dùng serverless: chỉ viết hàm | 1:00 |  |
| 10 | 3. Dùng từng loại | Dùng SaaS: ba vai người dùng | 1:00 |  |
| 11 | 3. Dùng từng loại | Một ứng dụng, bốn cách đưa lên mây | 0:50 | Tùy chọn |
| 12 | Demo | Cùng một trang web trên máy ảo và trên hàm serverless | 4:00 | Kịch bản ở mục 4 |
| 13 | 4. Chi phí | Hóa đơn đám mây tính từ đâu | 1:00 |  |
| 14 | 4. Chi phí | Dùng thử miễn phí và tránh hóa đơn bất ngờ | 1:00 |  |
| 15 | 5. Vận hành | Đọc SLA từ phía người dùng | 1:10 | Giáp ranh CĐ5 |
| 16 | 5. Vận hành | Bốn việc người dùng phải tự bật | 0:50 | Tùy chọn, giáp ranh CĐ5 |
| 17 | 6. Đường dài | Đưa hệ thống cũ lên mây và giữ đường lui | 0:50 | Tùy chọn |
| 18 | Kết | Bảy việc khi bắt đầu dùng đám mây | 0:40 | Chuyển giao cho nhóm 5, hỏi đáp |

## 3. Nội dung chi tiết từng slide

Mỗi slide có ba phần: chữ đưa lên slide, lời thuyết trình và gợi ý hình minh họa. Lời thuyết trình là phần lời cốt lõi, đọc hết mất khoảng một nửa thời lượng của slide; phần còn lại dùng để dẫn người nghe qua bảng và ví dụ trên slide.

### Slide 1 — Tiêu đề

**Trên slide**

- Sử dụng dịch vụ điện toán đám mây
- Dòng phụ: Từ tài khoản đầu tiên đến hóa đơn đầu tiên
- Chủ đề 4, học phần Điện toán đám mây; tên nhóm và thành viên

**Lời thuyết trình**

Kính chào thầy cô và các bạn. Các nhóm trước đã trả lời đám mây là gì, dữ liệu nằm ở đâu và được bảo vệ thế nào. Nhóm em trả lời câu hỏi tiếp theo: bắt tay vào dùng thì làm gì, theo thứ tự nào.

### Slide 2 — Từ “biết” sang “dùng”

**Trên slide**

- 167,7 tỉ USD: chi tiêu toàn cầu cho dịch vụ hạ tầng đám mây trong quý 3/2026, tăng 55% so với cùng kỳ.
- 85% người trả lời khảo sát coi quản lý chi tiêu đám mây là thách thức hàng đầu; khoảng 29% chi tiêu IaaS và PaaS bị chính họ ước tính là lãng phí.
- Lộ trình sáu chặng: Chọn → Thiết lập → Tạo tài nguyên → Triển khai → Vận hành → Tối ưu và thu hồi.
- Ví dụ xuyên suốt: web app của một nhóm sinh viên.

**Lời thuyết trình**

Quý 3 năm nay, thế giới chi gần 168 tỉ đô cho hạ tầng đám mây, tăng 55% chỉ sau một năm. Dùng nhiều chưa chắc là dùng giỏi: trong khảo sát Flexera 2026, các tổ chức tự ước tính khoảng 29% chi tiêu đám mây của họ là lãng phí.

Vì vậy bài này đi đúng hành trình của một người dùng, qua sáu chặng trên màn hình. Xuyên suốt, nhóm dùng một ví dụ: đưa web app nhỏ của nhóm lên đám mây.

**Hình minh họa:** hai con số lớn ở nửa trên; sáu chặng vẽ thành một đường đi ở nửa dưới, dùng lại làm thanh tiến độ cho các slide sau.

**Nguồn:** [Synergy Research Group, công bố qua TechInsights ngày 30/10/2026](https://www.techinsights.com/node/61958); [Flexera 2026 State of the Cloud Report, 18/3/2026](https://www.flexera.com/about-us/press-center/flexera-finds-cloud-value-is-rising-while-ai-waste-grows); [TechInformed, 10/4/2026](https://techinformed.com/ai-workloads-drive-estimated-cloud-waste-to-29/) giải thích con số 29%.

### Slide 3 — Chọn nhà cung cấp và Region

**Trên slide**

| Tiêu chí | Câu hỏi cần trả lời | Với ví dụ của nhóm |
| --- | --- | --- |
| Vị trí hạ tầng | Người dùng ở đâu, Region nào gần nhất? | Singapore (ap-southeast-1); AWS có thêm Local Zone Hà Nội từ 19/6/2026 |
| Quy định dữ liệu | Dữ liệu có buộc lưu trong nước không? | Xem Điều 26 Nghị định 53/2022/NĐ-CP |
| Danh mục dịch vụ | Có đủ máy ảo, cơ sở dữ liệu managed, serverless mình cần? | So danh mục trước khi chọn |
| Chi phí và thanh toán | Có gói dùng thử không, chấp nhận cách thanh toán nào? | Xem slide 14 |
| Tài liệu và hỗ trợ | Tài liệu, cộng đồng, hỗ trợ tiếng Việt ra sao? | Hỏi thử trước khi cam kết |

- Hai nhóm nhà cung cấp: toàn cầu (Amazon 26%, Microsoft 19%, Google 16% thị trường quý 3/2026) và trong nước (Viettel, VNPT, FPT, CMC).

**Lời thuyết trình**

Nhóm 1 đã nói cách chọn mô hình. Khi bắt tay vào dùng, câu hỏi cụ thể hơn: nhà cung cấp nào, đặt ở Region nào. Region quyết định độ trễ, giá và cả nghĩa vụ pháp lý.

Với người dùng ở Việt Nam, lựa chọn quen thuộc là Singapore. Từ tháng 6 năm nay, AWS có thêm Local Zone tại Hà Nội, cho phép đặt máy ảo và dữ liệu ngay trong nước.

Nếu ứng dụng giữ dữ liệu cá nhân của người dùng Việt Nam, cần đọc Điều 26 Nghị định 53: doanh nghiệp trong nước phải lưu nhóm dữ liệu này tại Việt Nam. Phần pháp lý sâu hơn thuộc chủ đề 3.

**Hình minh họa:** bản đồ Đông Nam Á đánh dấu Singapore và Hà Nội.

**Nguồn:** thị phần theo [Synergy Research Group](https://www.techinsights.com/node/61958); [AWS công bố Local Zone Hà Nội, 19/6/2026](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-local-zones-hanoi-vietnam/); [Nghị định 53/2022/NĐ-CP](https://vcci.com.vn/legal-document/nghi-dinh-532022nd-cp-huong-dan-luat-an-ninh-mang).

### Slide 4 — Năm việc làm ngay khi có tài khoản

**Trên slide**

1. Chọn gói dùng thử phù hợp: Free plan hoặc gói sinh viên.
2. Khóa tài khoản gốc: bật MFA, tạo người dùng riêng cho việc hằng ngày.
3. Đặt ngân sách và cảnh báo chi phí qua email.
4. Chọn Region mặc định và xem hạn mức (quota) của tài khoản mới.
5. Thống nhất cách đặt tên và gắn thẻ (tag) cho mọi tài nguyên.

**Lời thuyết trình**

Tạo tài khoản chỉ mất vài phút, nhưng năm việc này quyết định về sau có gặp rắc rối hay không. Việc số 2 thuộc chủ đề bảo mật nên nhóm chỉ nhắc tên.

Việc số 3 hay bị bỏ qua nhất. AWS có sẵn mẫu Zero spend budget: chỉ cần nhập email, hệ thống báo khi chi tiêu vượt mức miễn phí. Việc số 5 giúp cuối tháng biết tiền đi vào đâu và xóa cho đủ.

**Hình minh họa:** danh sách đánh số kèm ảnh chụp màn hình tạo ngân sách.

**Nguồn:** [AWS Budgets, các mẫu ngân sách](https://docs.aws.amazon.com/cost-management/latest/userguide/budget-templates.html).

### Slide 5 — Bốn cách “nói chuyện” với đám mây

**Trên slide**

| Cách | Bản chất | Hợp khi | Ví dụ |
| --- | --- | --- | --- |
| Console | Nhấp chuột trên giao diện web | Học, khám phá, làm một lần | AWS Management Console, Azure Portal |
| CLI | Gõ lệnh trong terminal | Việc lặp lại, viết script | `aws`, `az`, `gcloud` |
| SDK | Gọi dịch vụ từ mã nguồn ứng dụng | Ứng dụng tự dùng dịch vụ | AWS SDK cho JavaScript, boto3 cho Python |
| IaC (hạ tầng dưới dạng mã) | Mô tả hạ tầng trong tệp, công cụ tự dựng | Dựng lại cả môi trường, review, lưu Git | Terraform, OpenTofu, CloudFormation |

- Cả bốn cách cùng gọi một API; khác nhau ở mức tự động hóa.

**Lời thuyết trình**

Đặc tính tự phục vụ mà nhóm 1 nêu hiện ra thành bốn cách thao tác này. Console dễ nhất nhưng không lặp lại được: nhấp khác đi một lần là môi trường khác đi.

CLI và SDK biến thao tác thành lệnh và mã. IaC đi xa nhất: toàn bộ hạ tầng nằm trong tệp văn bản, lưu Git và review như mã nguồn. Điều cần nhớ: bên dưới cả bốn cách là cùng một API.

**Hình minh họa:** bốn ô xếp theo trục “thủ công → tự động”, cùng chỉ mũi tên vào một ô API.

### Slide 6 — Một máy chủ, ba cách tạo (tùy chọn)

**Trên slide**

Ba cột cạnh nhau: ảnh chụp màn hình Console có đánh số các lần nhấp, một lệnh CLI, một khối mã Terraform.

```bash
aws lightsail create-instances \
  --instance-names demo-cd4 \
  --availability-zone ap-southeast-1a \
  --blueprint-id ubuntu_24_04 \
  --bundle-id nano_3_0
```

```hcl
resource "aws_lightsail_instance" "web" {
  name              = "demo-cd4"
  availability_zone = "ap-southeast-1a"
  blueprint_id      = "ubuntu_24_04"
  bundle_id         = "nano_3_0"
}
```

Mã image và mã gói có thể đổi theo thời gian. Kiểm tra trước khi chiếu bằng `aws lightsail get-blueprints` và `aws lightsail get-bundles`.

**Lời thuyết trình**

Cùng một máy chủ ảo gói 5 đô một tháng. Trên Console là vài lần nhấp chuột. Trên CLI là một lệnh. Với Terraform là một khối mã vài dòng; muốn dựng lại y hệt ở Region khác thì sửa một dòng.

Nhóm sẽ chạy thật hai cách đầu trong phần demo.

### Slide 7 — Dùng IaaS: thuê và tự quản một máy ảo

**Trên slide**

- Sáu quyết định khi tạo máy ảo: Region và vùng sẵn sàng → image hệ điều hành → cấu hình vCPU và RAM → đĩa → mạng và tường lửa → khóa SSH.
- Việc của mình sau khi tạo: vá hệ điều hành, cài runtime, đưa mã lên, mở cổng, sao lưu, theo dõi.
- Hai kiểu tính tiền: gói cố định theo tháng (Amazon Lightsail 5 USD: 2 vCPU, 0,5 GB RAM, 20 GB SSD, 1 TB băng thông) hoặc theo giây máy chạy (Amazon EC2, tối thiểu 60 giây).

**Lời thuyết trình**

Với IaaS, mình nhận về một máy trống. Sáu lựa chọn này xuất hiện ở mọi nhà cung cấp, chỉ khác tên gọi.

Tạo xong mới là lúc bắt đầu. Vá hệ điều hành, cài Node.js, đưa mã lên, mở cổng, sao lưu: tất cả là việc của mình. Đổi lại, mình có toàn quyền trên máy.

Về giá có hai kiểu: gói cố định theo tháng như Lightsail, hoặc tính theo từng giây máy chạy như EC2.

**Hình minh họa:** sáu ô nối tiếp, mỗi ô một biểu tượng; bên cạnh là ảnh chụp màn hình tạo máy thật.

**Nguồn:** [bảng giá Amazon Lightsail](https://aws.amazon.com/lightsail/pricing); [bảng giá Amazon EC2](https://aws.amazon.com/ec2/pricing/).

### Slide 8 — Dùng PaaS: đưa mã lên, nền tảng lo phần còn lại

**Trên slide**

1. Chuẩn bị mã nguồn và tệp khai báo, ví dụ `package.json` hoặc `Dockerfile`.
2. Chọn runtime, Region và gói dịch vụ.
3. Khai báo biến môi trường, nối với cơ sở dữ liệu managed.
4. Triển khai bằng một lệnh hoặc một lần `git push`.

- Lệnh ví dụ: `az webapp up` (Azure App Service), `gcloud app deploy` (Google App Engine), `eb deploy` (AWS Elastic Beanstalk).
- Nền tảng tự lo: máy chủ, hệ điều hành, HTTPS, tên miền mặc định, co giãn.

**Lời thuyết trình**

Với PaaS, đơn vị làm việc không còn là máy chủ mà là ứng dụng. Mình đưa mã nguồn kèm vài dòng cấu hình; nền tảng tự dựng, cấp HTTPS và co giãn.

Trên Azure, cả quy trình gói trong một lệnh az webapp up. Cơ sở dữ liệu cũng dùng theo kiểu này: tạo bản managed, lấy chuỗi kết nối, đặt vào biến môi trường.

**Hình minh họa:** bốn bước nằm ngang; bên dưới là một cửa sổ terminal với đúng một lệnh.

Lời mở đầu của giáo trình cho biết chương này minh họa bằng nền tảng Azure, nên ví dụ Azure ở đây khớp với giáo trình.

### Slide 9 — Dùng serverless: chỉ viết hàm

**Trên slide**

- Ba bước: viết hàm → gắn nguồn kích hoạt (yêu cầu HTTP, tệp mới tải lên, lịch hẹn giờ) → nền tảng chạy hàm khi có sự kiện.
- Không có sự kiện thì không tốn tiền chạy. AWS Lambda miễn phí mỗi tháng 1 triệu lượt gọi và 400.000 GB-giây.
- Giới hạn cần biết: mỗi lần chạy tối đa 15 phút; lần gọi đầu chậm hơn (cold start); mã gắn với nhà cung cấp.
- Hợp với: API nhỏ, xử lý ảnh sau khi tải lên, tác vụ định kỳ.

**Lời thuyết trình**

Serverless đi thêm một bước: mình không thấy máy chủ, cũng không có ứng dụng chạy thường trực. Mình viết một hàm và khai báo khi nào chạy nó.

Trong ví dụ của nhóm, hàm tạo ảnh thu nhỏ mỗi khi người dùng tải ảnh lên là ứng viên điển hình. Điểm hấp dẫn nhất là giá: không ai gọi thì không mất tiền chạy.

Điểm phải cân nhắc là giới hạn 15 phút và độ trễ ở lần gọi đầu.

**Hình minh họa:** một sự kiện (ảnh tải lên) → một hàm → một kết quả (ảnh thu nhỏ); đồng hồ tính tiền chỉ chạy ở ô giữa.

**Nguồn:** [bảng giá AWS Lambda](https://aws.amazon.com/lambda/pricing/); [giới hạn thời gian chạy của Lambda](https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html).

### Slide 10 — Dùng SaaS: ba vai người dùng

**Trên slide**

| Vai | Việc làm | Ví dụ |
| --- | --- | --- |
| Người dùng cuối | Đăng nhập và dùng ngay trên trình duyệt | Soạn tài liệu, họp trực tuyến, lưu tệp |
| Quản trị viên | Tạo tài khoản, phân quyền, đăng nhập một lần (SSO), chính sách chia sẻ | Trang quản trị Google Workspace, Microsoft 365 |
| Lập trình viên | Ghép dịch vụ vào sản phẩm qua API, OAuth 2.0, webhook | Đăng nhập bằng Google, gửi email, thanh toán, gọi mô hình AI |

- Ba câu hỏi trước khi chọn: xuất dữ liệu ra được không, API giới hạn bao nhiêu lượt gọi, giá tính theo người dùng hay theo lượng dùng?

**Lời thuyết trình**

SaaS là loại ai cũng đang dùng, nên nhóm không giới thiệu lại sản phẩm. Điều ít được để ý là có ba cách dùng.

Người dùng cuối chỉ cần trình duyệt. Quản trị viên quyết định ai được vào và được chia sẻ gì. Lập trình viên ghép SaaS vào sản phẩm của mình: web app của nhóm không tự viết đăng nhập, gửi thư hay thanh toán mà gọi dịch vụ có sẵn.

Gọi mô hình AI qua API là kiểu dùng mới nhất: trong khảo sát Flexera 2026, 81% người trả lời cho biết đang dùng AI tạo sinh.

**Hình minh họa:** ba hình người với ba màn hình khác nhau: ứng dụng, trang quản trị, đoạn mã gọi API.

**Nguồn:** [Flexera 2026 State of the Cloud Report](https://www.flexera.com/about-us/press-center/flexera-finds-cloud-value-is-rising-while-ai-waste-grows).

### Slide 11 — Một ứng dụng, bốn cách đưa lên mây (tùy chọn)

**Trên slide**

| Tiêu chí | Máy ảo (IaaS) | Nền tảng (PaaS) | Hàm (serverless) | Mua sẵn (SaaS) |
| --- | --- | --- | --- | --- |
| Thứ mình đưa lên | Cả máy: hệ điều hành, runtime, mã | Mã nguồn | Từng hàm | Chỉ cấu hình |
| Việc tự làm sau khi tạo | Vá hệ điều hành, mở cổng, sao lưu | Biến môi trường, theo dõi ứng dụng | Thiết kế theo sự kiện, cấp quyền cho hàm | Quản lý người dùng và dữ liệu |
| Trả tiền khi không ai dùng | Có, máy vẫn chạy | Thường có | Không | Có, theo thuê bao |
| Hợp với phần nào của ví dụ | Thành phần cần cài đặt riêng | API và giao diện web | Xử lý ảnh, tác vụ hẹn giờ | Email, đăng nhập, thanh toán |

Khi tập demo, đo thời gian đến bản chạy đầu tiên của từng cách rồi thêm thành một dòng của bảng.

**Lời thuyết trình**

Bảng này không so khái niệm, vì nhóm 1 đã làm, mà so công sức thực tế. Dòng đáng chú ý nhất là dòng thứ ba: ai trả tiền khi không có người dùng.

Kết luận thực tế: một ứng dụng thật thường dùng cả bốn loại cùng lúc, mỗi phần một kiểu.

### Slide 12 — Demo

**Trên slide**

- Tiêu đề: Cùng một trang web, hai cách đưa lên mây.
- Hai ô trống để dán địa chỉ của máy ảo và của hàm khi demo chạy xong.

Kịch bản, mã và phương án dự phòng nằm ở mục 4.

### Slide 13 — Hóa đơn đám mây tính từ đâu

**Trên slide**

- Bốn đồng hồ đo: thời gian tính toán (giây, giờ) · dung lượng lưu trữ (GB-tháng) · dữ liệu truyền ra Internet (GB) · số yêu cầu (triệu lượt).
- Gói cố định: máy ảo Lightsail 5 USD mỗi tháng, đã gồm 1 TB băng thông.
- Trả theo lượng dùng: hàm Lambda nhận 3 triệu lượt gọi mỗi tháng, mỗi lượt 200 ms với 128 MB bộ nhớ. Thời gian chạy 75.000 GB-giây nằm trong mức miễn phí; chỉ trả 2 triệu lượt × 0,20 USD = 0,40 USD.
- Ba cách mua máy ảo: theo nhu cầu, cam kết dài hạn (nhóm 1 đã trình bày), Spot — máy dư công suất, giảm đến 90% nhưng có thể bị thu hồi.
- Trước khi tạo: ước tính bằng công cụ tính giá của nhà cung cấp.

Phép tính Lambda dùng giá x86 bậc đầu, chưa gồm phí log và truyền dữ liệu; kiểm tra lại theo Region dùng thật.

**Lời thuyết trình**

Hóa đơn đám mây dài đến đâu cũng quy về bốn đồng hồ đo này. Hai ví dụ cho thấy hai kiểu trả tiền.

Gói cố định dễ dự đoán: 5 đô, hết. Trả theo lượng dùng thì phải tính: ba triệu lượt gọi một tháng nghe lớn, nhưng chỉ tốn 40 xu vì phần lớn nằm trong mức miễn phí.

Thói quen cần có: mở công cụ tính giá trước khi tạo bất cứ thứ gì chạy lâu dài.

**Hình minh họa:** bốn đồng hồ đo; hai hóa đơn mẫu đặt cạnh nhau.

**Nguồn:** [bảng giá Amazon Lightsail](https://aws.amazon.com/lightsail/pricing); [bảng giá AWS Lambda](https://aws.amazon.com/lambda/pricing/); [bảng giá Amazon EC2](https://aws.amazon.com/ec2/pricing/).

### Slide 14 — Dùng thử miễn phí và tránh hóa đơn bất ngờ

**Trên slide**

| Nhà cung cấp | Ưu đãi cho người mới | Điều cần biết |
| --- | --- | --- |
| AWS | 100 USD credit khi đăng ký, thêm tối đa 100 USD khi khám phá dịch vụ; Free plan tối đa 6 tháng | Free plan không tính tiền; tài khoản tự đóng sau 6 tháng hoặc khi hết credit nếu không nâng cấp |
| Azure for Students | 100 USD credit, dùng trong 12 tháng | Không cần thẻ; dành cho sinh viên đại học hệ toàn thời gian, gia hạn hằng năm |
| Google Cloud | 300 USD credit trong 90 ngày | Cần thẻ hoặc phương thức thanh toán để xác minh; hết hạn không tự tính tiền |

- Bốn thói quen: đặt ngân sách và cảnh báo · gắn tag · xóa máy ảo, đĩa, IP tĩnh, snapshot ngay sau buổi thực hành · xem trang Billing hằng tuần.

**Lời thuyết trình**

Tin tốt cho sinh viên: cả ba nhà cung cấp lớn đều cho dùng thử. Azure for Students không cần thẻ ngân hàng, nên là cách dễ nhất để cả lớp thực hành.

Điều cần cẩn trọng: hóa đơn bất ngờ thường đến từ thứ mình quên tắt, như một máy ảo, một ổ đĩa hay một địa chỉ IP tĩnh. Từ tháng 7/2025, tài khoản AWS mới có thể chọn Free plan: không tính tiền cho đến khi mình chủ động nâng cấp.

**Hình minh họa:** ba thẻ ưu đãi; bên dưới là bốn biểu tượng thói quen.

**Nguồn:** [AWS Free Tier](https://aws.amazon.com/free/); [thông báo của AWS ngày 16/7/2025](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan); [Azure for Students](https://azure.microsoft.com/students); [Google Cloud Free Program](https://docs.cloud.google.com/free). Số liệu tra ngày 12/11/2026.

### Slide 15 — Đọc SLA từ phía người dùng

**Trên slide**

Ví dụ: cam kết của Amazon EC2.

| Cam kết hằng tháng | Điều kiện | Thời gian ngừng tối đa trong tháng 30 ngày |
| --- | --- | --- |
| 99,99% ở cấp Region | Máy chạy trên ít nhất hai vùng sẵn sàng (AZ) | 4,3 phút |
| 99,5% ở cấp từng máy | Một máy đơn lẻ | 3,6 giờ |

- Bồi thường là credit 10%, 30% hoặc 100% tiền dịch vụ đó, trừ vào kỳ sau. Phải tự gửi yêu cầu trước khi hết kỳ hóa đơn thứ hai sau sự cố.
- Credit tính theo hóa đơn dịch vụ, không theo thiệt hại kinh doanh của mình.
- Sự cố thật: từ 13:48 ngày 20/10/2025 đến 04:20 ngày 21/10/2025 (giờ Việt Nam), lỗi DNS của DynamoDB tại Region Bắc Virginia gây gián đoạn nhiều dịch vụ AWS, tổng cộng 14 giờ 32 phút.

**Lời thuyết trình**

SLA hay được hiểu là lời hứa gần như không bao giờ sập. Đọc kỹ thì thấy ba điều.

Một, con số đẹp có điều kiện. Bốn số 9 chỉ áp dụng khi mình tự triển khai trên hai vùng sẵn sàng. Một máy đơn lẻ chỉ được cam kết 99,5%, tức có thể ngừng hơn ba tiếng rưỡi mỗi tháng.

Hai, bồi thường là credit trừ vào hóa đơn sau và mình phải tự yêu cầu. Ba, sự cố lớn vẫn xảy ra: tháng 10 năm ngoái, một lỗi DNS ở một Region của AWS kéo dài hơn mười bốn tiếng.

Vì vậy độ sẵn sàng là thứ người dùng phải tự thiết kế. Cách làm thuộc phần của nhóm 5.

**Hình minh họa:** hai thanh thời gian của một tháng, tô đậm phần được phép ngừng: 4,3 phút so với 3,6 giờ.

**Nguồn:** [Amazon Compute Service Level Agreement](https://aws.amazon.com/ec2-sla/); [báo cáo sau sự cố của AWS](https://aws.amazon.com/message/101925/).

### Slide 16 — Bốn việc người dùng phải tự bật (tùy chọn)

**Trên slide**

1. Giám sát và cảnh báo: CPU, bộ nhớ, tỉ lệ lỗi; gửi email khi vượt ngưỡng.
2. Kiểm tra sức khỏe và cân bằng tải: tự loại máy hỏng khỏi vòng phục vụ.
3. Tự co giãn: thêm bớt máy theo tải, đặt cả giới hạn trên để chặn chi phí.
4. Sao lưu tự động và thử khôi phục.

- Công cụ có sẵn ở mọi nhà cung cấp, nhưng người dùng phải tự cấu hình.

**Lời thuyết trình**

Sau khi ứng dụng chạy, còn bốn việc mà nhà cung cấp không làm thay. Cả bốn đều có công cụ sẵn, nhưng phải tự bật và tự đặt ngưỡng.

Nhóm chỉ nêu tên để khép lại hành trình sử dụng. Nguyên lý và cách làm của từng việc là nội dung của chủ đề 5.

### Slide 17 — Đưa hệ thống cũ lên mây và giữ đường lui (tùy chọn)

**Trên slide**

| Chiến lược (7R) | Nghĩa là |
| --- | --- |
| Retire | Tắt hoặc lưu trữ ứng dụng không còn giá trị |
| Retain | Giữ ở môi trường cũ, chưa chuyển |
| Rehost | Chuyển nguyên trạng, không sửa ứng dụng (lift and shift) |
| Relocate | Chuyển cả loạt máy chủ sang phiên bản đám mây của cùng nền tảng, không đổi kiến trúc |
| Repurchase | Thay bằng sản phẩm khác, thường là SaaS (drop and shop) |
| Replatform | Chuyển kèm tối ưu nhẹ, ví dụ đổi sang cơ sở dữ liệu managed |
| Refactor | Thiết kế lại kiến trúc để tận dụng tính năng cloud-native |

- Giữ đường lui: đóng gói bằng container · viết hạ tầng bằng IaC · ưu tiên chuẩn mở như PostgreSQL, Kubernetes · tách cấu hình khỏi mã · xuất dữ liệu định kỳ.

**Lời thuyết trình**

Phần lớn tổ chức không bắt đầu từ số không mà đã có hệ thống đang chạy. AWS gom các lựa chọn thành bảy chữ R.

Với web app của nhóm đang chạy trên một máy chủ thuê, bước đầu hợp lý là Rehost lên máy ảo. Bước sau là Replatform: chuyển cơ sở dữ liệu sang bản managed.

Nhóm 1 đã cảnh báo rủi ro phụ thuộc nhà cung cấp. Năm thói quen ở cuối slide là cách giảm rủi ro đó ngay trong lúc dùng.

**Nguồn:** [AWS Prescriptive Guidance, các chiến lược di chuyển](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html).

### Slide 18 — Kết: bảy việc khi bắt đầu dùng đám mây

**Trên slide**

1. Chọn Region theo người dùng và quy định dữ liệu.
2. Bật MFA, không làm việc bằng tài khoản gốc.
3. Đặt ngân sách trước khi tạo tài nguyên đầu tiên.
4. Bắt đầu bằng Console; chuyển sang CLI hoặc IaC khi phải làm lần thứ hai.
5. Chọn loại dịch vụ cho từng phần của ứng dụng.
6. Đọc điều kiện của SLA, tự thiết kế phần sẵn sàng.
7. Xóa tài nguyên sau khi dùng và giữ đường lui.

**Lời thuyết trình**

Bảy dòng này tóm lại hành trình sáu chặng. Nếu chỉ nhớ một điều: đám mây cho mình công cụ, còn dùng tốt hay không là việc của người dùng.

Câu hỏi còn lại, khi hệ thống đã chạy thì giám sát và đảm bảo chất lượng thế nào, xin nhường cho nhóm 5. Cảm ơn thầy cô và các bạn đã lắng nghe.

## 4. Kịch bản demo

Demo 4 phút đưa cùng một trang web lên mây theo hai cách, máy ảo và hàm serverless, để người xem thấy chênh lệch công sức. Kịch bản viết cho AWS: Lightsail và Lambda tại Region Singapore.

### Chuẩn bị trước buổi

- [ ] Tập trọn kịch bản ít nhất hai lần trên đúng tài khoản sẽ dùng, ghi thời gian từng bước.
- [ ] Chọn Region Singapore trên Console, mở CloudShell và tạo sẵn tệp `setup.sh` trong đó.
- [ ] Lưu mã hàm Lambda vào một tệp ghi chú để dán.
- [ ] Tạo một máy dự phòng 10 phút trước giờ nói, mở sẵn địa chỉ của máy trên một tab.
- [ ] Xem tab Networking của máy: cổng 80 phải mở; nếu chưa, thêm luật HTTP.
- [ ] Mở sẵn ba tab Lightsail, CloudShell, Lambda; phóng to chữ để cuối lớp đọc được.
- [ ] Quay video toàn bộ demo và chụp ảnh từng bước để dự phòng.

### Kịch bản theo thời gian

| Thời điểm | Thao tác | Câu nói kèm theo |
| --- | --- | --- |
| 0:00–0:40 | Console Lightsail: Create instance, chọn Linux và Ubuntu, dán launch script, chọn gói 5 USD, đặt tên `demo-cd4`, bấm Create | Sáu quyết định ở slide 7 nằm gọn trên một màn hình. |
| 0:40–1:20 | CloudShell: chạy lệnh tạo máy thứ hai `demo-cd4-cli`, rồi lệnh liệt kê máy | Cùng kết quả, lần này là một lệnh và chạy lại bao nhiêu lần cũng được. |
| 1:20–2:00 | Mở địa chỉ IP công khai của máy trên trình duyệt; mở SSH trên trình duyệt, gõ `uptime` | Đây là máy của mình: toàn quyền, và cũng tự lo toàn bộ. |
| 2:00–3:10 | Console Lambda: Create function, runtime Node.js, dán mã, bật Function URL với Auth type NONE, mở URL | Không tạo máy, không cài gì. Không ai gọi thì không tốn tiền chạy. |
| 3:10–3:40 | Đặt hai tab cạnh nhau, nêu số bước và thời gian của từng cách | Cùng một trang web, hai mức công sức khác nhau. |
| 3:40–4:00 | Xóa máy bằng lệnh, xóa hàm trên Console | Bước cuối của việc sử dụng là thu hồi tài nguyên. |

Nếu máy mới chưa cài xong nginx ở phút 1:20, mở tab của máy dự phòng và nói rõ đó là máy tạo trước.

### Mã dùng trong demo

Launch script `setup.sh`, viết không dấu để tránh lỗi mã hóa:

```bash
#!/bin/bash
apt-get update -y
apt-get install -y nginx
echo '<h1>Xin chao lop Dien toan dam may - may ao (IaaS)</h1>' > /var/www/html/index.html
```

Lệnh chạy trong CloudShell:

```bash
aws lightsail create-instances \
  --instance-names demo-cd4-cli \
  --availability-zone ap-southeast-1a \
  --blueprint-id ubuntu_24_04 \
  --bundle-id nano_3_0 \
  --user-data file://setup.sh

aws lightsail get-instances \
  --query "instances[].{ten:name,ip:publicIpAddress,trangthai:state.name}" \
  --output table

aws lightsail delete-instance --instance-name demo-cd4-cli
```

Mã hàm Lambda (Node.js):

```js
export const handler = async () => ({
  statusCode: 200,
  headers: { "Content-Type": "text/html; charset=utf-8" },
  body: "<h1>Xin chào lớp Điện toán đám mây - hàm serverless</h1>",
});
```

### Dự phòng và dọn dẹp

- Mạng chậm hoặc Console lỗi: chờ tối đa 20 giây rồi chuyển sang video quay sẵn, vẫn nói theo kịch bản.
- Tài khoản Free plan chỉ dùng được một số dịch vụ; thử đủ các bước trước trên đúng tài khoản đó.
- Sau buổi nói: xóa hai máy demo, máy dự phòng và hàm; hôm sau mở trang Billing để chắc không còn gì chạy.
- Muốn bám sát ba mục của giáo trình hơn: thay phần Lambda bằng PaaS, ví dụ `az webapp up` trên Azure App Service, và dùng video quay sẵn vì triển khai lâu hơn.

## 5. Câu hỏi có thể gặp

Mười câu dưới đây là những chỗ người nghe dễ hỏi nhất, kèm ý trả lời trong một hai câu.

| Câu hỏi | Ý trả lời |
| --- | --- |
| Lightsail khác EC2 ở đâu? | Cùng là máy ảo của AWS. Lightsail bán theo gói cố định hằng tháng, gồm sẵn đĩa và băng thông; EC2 tính theo giây và cho cấu hình chi tiết từng thành phần. |
| Sinh viên không có thẻ quốc tế thì thực hành bằng gì? | Azure for Students: 100 USD credit, không cần thẻ, đăng ký bằng email trường. Cũng có thể hỏi chương trình dùng thử của nhà cung cấp trong nước. |
| Hết Free plan của AWS có bị trừ tiền không? | Không. Tài khoản tự đóng sau 6 tháng hoặc khi hết credit; chỉ bị tính tiền khi tự nâng lên Paid plan. |
| PaaS và serverless khác nhau thế nào? | PaaS chạy cả ứng dụng thường trực và tính tiền theo gói. Serverless chạy từng hàm khi có sự kiện, tính theo lượt gọi và thời gian chạy; Lambda giới hạn 15 phút mỗi lần. |
| Nhà cung cấp sập như tháng 10/2025 thì người dùng được gì? | Credit theo SLA nếu đủ điều kiện và gửi yêu cầu đúng hạn. Credit tính trên hóa đơn dịch vụ, nên cách giảm thiệt hại thật sự là thiết kế trên nhiều vùng sẵn sàng. |
| Dữ liệu người dùng Việt Nam đặt ở Singapore được không? | Tùy loại dữ liệu và loại doanh nghiệp. Điều 26 Nghị định 53/2022 yêu cầu doanh nghiệp trong nước lưu tại Việt Nam ba nhóm dữ liệu của người dùng dịch vụ. Cần đọc văn bản và hỏi ý kiến pháp lý. |
| Vì sao phải học CLI và IaC khi Console nhanh hơn? | Console nhanh cho lần đầu nhưng không lặp lại và không review được. IaC dựng lại môi trường giống hệt và lưu lịch sử thay đổi trong Git. |
| Terraform hay CloudFormation? | CloudFormation chỉ dùng cho AWS. Terraform và OpenTofu làm việc với nhiều nhà cung cấp, hợp với mục tiêu giữ đường lui. |
| Làm sao biết trước chi phí? | Liệt kê bốn đồng hồ đo của hệ thống, nhập vào công cụ tính giá của nhà cung cấp, rồi đặt ngân sách bằng con số đó. |
| Con số 29% lãng phí đo thế nào? | Đây là con số người trả lời tự ước tính trong khảo sát Flexera 2026 với 753 người, không phải số đo từ hóa đơn. |

## 6. Nguồn tham khảo

Các trang dưới đây đã được mở và đối chiếu ngày 12/11/2026. Giá và ưu đãi thay đổi thường xuyên; nên kiểm tra lại trong tuần thuyết trình.

**Tài liệu của lớp**

- Slide CĐ1 “Nền tảng và phân loại điện toán đám mây” (29 slide) và slide CĐ2 “Lưu trữ & xử lý dữ liệu đám mây” (16 slide), dùng để lập bảng tránh trùng.
- [Giáo trình Điện toán đám mây, Huỳnh Quyết Thắng chủ biên](https://thuvien.utm.edu.vn/ktpm/%C4%90i%E1%BB%87n%20to%C3%A1n%20%C4%91%C3%A1m%20m%C3%A2y%20v%C3%A0%20%E1%BB%A9ng%20d%E1%BB%A5ng.pdf): mục lục và lời mở đầu.
- [Đề cương học phần Điện toán đám mây, Đại học Nam Cần Thơ](https://nctu.edu.vn/uploads/technology/2021_12/51_Dien_toan_dam_may.pdf): thứ tự chương.

**Thị trường và khảo sát**

- [Synergy Research Group qua TechInsights: thị trường hạ tầng đám mây quý 3/2026](https://www.techinsights.com/node/61958), 30/10/2026.
- [Flexera: thông cáo về 2026 State of the Cloud Report](https://www.flexera.com/about-us/press-center/flexera-finds-cloud-value-is-rising-while-ai-waste-grows), 18/3/2026.
- [TechInformed: AI workloads drive estimated cloud waste to 29%](https://techinformed.com/ai-workloads-drive-estimated-cloud-waste-to-29/), 10/4/2026.

**AWS**

- [AWS Free Tier](https://aws.amazon.com/free/) và [thông báo ngày 16/7/2025](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan).
- [Bảng giá Amazon Lightsail](https://aws.amazon.com/lightsail/pricing), [Amazon EC2](https://aws.amazon.com/ec2/pricing/), [AWS Lambda](https://aws.amazon.com/lambda/pricing/).
- [Giới hạn thời gian chạy của Lambda](https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html).
- [Amazon Compute Service Level Agreement](https://aws.amazon.com/ec2-sla/).
- [Báo cáo sau sự cố DynamoDB tại Region Bắc Virginia, 19–20/10/2025](https://aws.amazon.com/message/101925/).
- [Công bố Local Zone Hà Nội](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-local-zones-hanoi-vietnam/), 19/6/2026.
- [AWS Budgets: các mẫu ngân sách](https://docs.aws.amazon.com/cost-management/latest/userguide/budget-templates.html).
- [AWS Prescriptive Guidance: bảy chiến lược di chuyển](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html).

**Nhà cung cấp khác**

- [Azure for Students](https://azure.microsoft.com/students).
- [Google Cloud Free Program](https://docs.cloud.google.com/free).

**Pháp lý**

- [Nghị định 53/2022/NĐ-CP, Điều 26 và 27](https://vcci.com.vn/legal-document/nghi-dinh-532022nd-cp-huong-dan-luat-an-ninh-mang), bản đăng trên trang VCCI.
