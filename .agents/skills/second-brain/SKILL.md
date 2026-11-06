---
name: second-brain
description: Quản lý và tra cứu Second Brain cá nhân (/home/dungcq/projects/second-brain). BẮT BUỘC tự động rà soát file cũ trước (Search-Before-Write), ưu tiên cập nhật file đã có để tránh trùng lặp; chỉ tạo file mới khi là domain hoàn toàn mới.
---

# Second Brain Skill

Kỹ năng này biến AI thành Người Thủ Thư Tri Thức Cá Nhân, quản lý kho lưu trữ `/home/dungcq/projects/second-brain`.

Nhiệm vụ chính:
1. Ingest: Chắt lọc bài viết, tweet, session postmortem thành Atomic Notes chuẩn; bắt buộc rà soát chống trùng lặp trước khi viết.
2. Recall & Slicing: Khi người dùng hoặc agent làm task liên quan, tra cứu qua CLI `scripts/brain` để lấy đúng lát cắt (invariants, schema, cases, probes) thay vì nạp cả file lớn.

---

## 1. Quy trình nạp bài học mới tự động (Auto-Ingest Workflow)

Khi người dùng nói: "Lưu bài này vào second brain...", đưa link/tweet/tài liệu, hoặc yêu cầu "học được gì từ session này lưu lại":

### Bước 1: Rà soát trùng lặp bắt buộc (Search-Before-Write Gate)
AI không được tự ý tạo file mới ngay lập tức. Bắt buộc chạy script kiểm tra:
```bash
/home/dungcq/projects/second-brain/scripts/check-duplicate.sh "<từ_khóa_1>" "<từ_khóa_2>"
```

### Bước 2: Rẽ nhánh hành động (Branching Decision)

* Trường hợp A: Đã có file cùng chủ đề hoặc cùng domain (Mặc định)
  - Hành động: Đọc file cũ, bổ sung nội dung mới vào đúng mục liên quan (ví dụ: thêm ca ngoại lệ vào Mục 3, thêm hàm parser/code vào Mục 4, hoặc thêm lưu ý vào Mục 2).
  - Thông báo cho người dùng: 
    > `[Second Brain] Đã rà soát: Chủ đề liên quan đến entries/<category>/<file_name>.md. Tiến hành cập nhật trực tiếp thay vì tạo file mới.`
  - Tuyệt đối: Không tạo file con xé lẻ (ví dụ: đã có `fnb-restaurant-p2p` thì không tạo thêm `fnb-invoice`).

* Trường hợp B: Chủ đề hoàn toàn mới (0 match và khác domain)
  - Hành động: Tạo file mới tại `entries/<category>/<tên-ngắn-gọn-kebab-case>.md` theo template chuẩn `templates/ENTRY-TEMPLATE.md`.
  - Cập nhật mục lục: Thêm link và keywords vào `/home/dungcq/projects/second-brain/INDEX.md` và bổ sung tags vào `# Tag Cloud`.
  - Thông báo cho người dùng:
    > `[Second Brain] Xác nhận chủ đề mới độc lập. Đã khởi tạo file: entries/<category>/<file_name>.md.`

### Bước 3: Nguyên tắc một nguồn sự thật (Single Source of Truth)
- Nếu bài học có nhắc đến khái niệm của domain khác, chỉ dùng link chéo 1 dòng (`[Xem chi tiết](../path/file.md)`), không chép lại định nghĩa hay code của file kia.

### Bước 4: Tự động đồng bộ Manifest và Git
Sau khi sửa hoặc tạo file xong, bắt buộc đồng bộ `MANIFEST.json` và kiểm tra tính toàn vẹn:
```bash
/home/dungcq/projects/second-brain/scripts/brain sync-manifest
/home/dungcq/projects/second-brain/scripts/brain check
cd /home/dungcq/projects/second-brain && git add . && git commit -m "feat(brain): <mô tả ngắn>" && git push origin main
```

---

## 2. Truy xuất và cầu nối thực thi pstack (JIT Aspect-Sliced Memory Lever)

Tránh nạp nguyên file markdown dài vào context để không chịu thuế ngữ cảnh (Harness Tax) gây phình token và tăng độ trễ. Dùng CLI `/home/dungcq/projects/second-brain/scripts/brain` để trích xuất đúng lát cắt cần dùng.

### Lệnh tra cứu lát cắt
```bash
# Trích xuất bất biến nghiệp vụ cốt lõi (mặc định)
/home/dungcq/projects/second-brain/scripts/brain query <domain-id-hoặc-trigger> --aspect invariants

# Trích xuất schema DDL, Go/TS struct
/home/dungcq/projects/second-brain/scripts/brain query <domain-id-hoặc-trigger> --aspect schema

# Trích xuất các tình huống ngoại lệ thực địa
/home/dungcq/projects/second-brain/scripts/brain query <domain-id-hoặc-trigger> --aspect cases

# Trích xuất cơ chế kỹ thuật và luồng điều phối
/home/dungcq/projects/second-brain/scripts/brain query <domain-id-hoặc-trigger> --aspect mechanisms

# Trích xuất bài học thẩm định và bằng chứng âm
/home/dungcq/projects/second-brain/scripts/brain query <domain-id-hoặc-trigger> --aspect probes

# Liệt kê danh mục và triggers
/home/dungcq/projects/second-brain/scripts/brain list
```

### Tích hợp trực tiếp vào các skill của pstack
1. Với `/architect` (Phase A: Grounding):
   - Đối chiếu bài toán với danh mục domain trong `MANIFEST.json`.
   - Chạy `brain query <domain> --aspect invariants`. Đưa nội dung này vào Rationale của Architect như một Hard Constraint bắt buộc phải thỏa mãn.
2. Với `/tdd` (Viết test suite):
   - Trước khi viết kiểm thử, chạy `brain query <domain> --aspect cases` và `--aspect probes`.
   - Đảm bảo test suite bắt được các ca ngoại lệ thực tế thay vì mock các trường hợp lý tưởng.
3. Với `/thermos` (Review PR):
   - Chạy `brain query <domain> --aspect probes` hoặc `--aspect schema` để đối chiếu diff với các bất biến đã ghi nhận.
4. Với `/reflect` và `/correct`:
   - Khi phát hiện một lỗi lặp lại hoặc hoàn thiện một kiến trúc mới được nghiệm thu, kích hoạt Ingest vào Second Brain và chạy `brain sync-manifest`.

---

## 3. Tiêu chuẩn "Clean-Room Reconstructability"

Một ghi chú đạt chuẩn bắt buộc phải có đủ các tầng kỹ thuật thực chất:

- Đối với Hệ thống / Kiến trúc dữ liệu:
  1. Domain Invariants: Sự thật vận hành thực tế vs lý thuyết sách vở; các ràng buộc cấm kỵ.
  2. Authoritative Data Schema: SQL DDL hoàn chỉnh (`BIGINT` thay vì `FLOAT` cho tiền tệ, khóa ngoại, chỉ mục) và struct/model.
  3. State Machine & Guards: Toàn bộ trạng thái vòng đời và điều kiện tiên quyết (guards) để chuyển trạng thái.
  4. Core Algorithms & Parsers: Regex chính xác, cấu trúc bóc tách dữ liệu cụ thể, công thức tính toán.
  5. Edge Cases & Data Provenance: Ít nhất 3 tình huống ngoại lệ thực địa; phân biệt rõ dữ liệu giả lập/seed với dữ liệu người dùng thật.

- Đối với Agentic Workflows / Harness / Tooling:
  1. Failure Signature & Mechanism: Lỗi cụ thể ở mức công cụ hoặc quy trình thực tế; phân biệt nguyên nhân kinh nghiệm vs giáo điều.
  2. Executable Harness / CLI Blueprint: Cấu hình, script, schema theo dõi hoặc lệnh thực thi tất định để tái lập giải pháp.
  3. Negative Transfer & Verification Probe: Cơ chế đo lường độc lập để xác minh giải pháp thực sự giải quyết vấn đề mà không làm phình thời gian chạy hoặc tạo báo động giả.

---

## 4. Vòng lặp đánh giá và tỉa bớt (Harness Retrospective & Pruning)

Theo nghiên cứu thực nghiệm về tự tiến hóa của agent harness (Baltes et al., 2026):
1. Không nạp quy tắc giáo điều: Không đưa vào Second Brain các hướng dẫn chung chung không giải quyết lỗi đã xảy ra.
2. Đo lường thuế ngữ cảnh (Harness Tax): Các ghi chú phải súc tích, đi thẳng vào cơ chế và dữ liệu cần tái lập, tránh câu từ hoa mỹ làm loãng mật độ tìm kiếm.
3. Chủ động tỉa bớt: Khi tra cứu hoặc đối chiếu, nếu phát hiện một ghi chú có quy tắc gây hiểu lầm hoặc tạo báo động giả trên tác vụ mới, chủ động cập nhật hoặc loại bỏ phần thừa.
