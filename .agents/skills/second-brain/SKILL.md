---
name: second-brain
description: Quản lý và tra cứu Second Brain cá nhân (/home/dungcq/projects/second-brain). BẮT BUỘC tự động rà soát file cũ trước (Search-Before-Write), ưu tiên cập nhật file đã có để tránh trùng lặp; chỉ tạo file mới khi là domain hoàn toàn mới.
---

# Second Brain Skill

Kỹ năng này biến AI thành **Người Thủ Thư Tri Thức Cá Nhân (Personal Knowledge Librarian)**, quản lý kho lưu trữ `/home/dungcq/projects/second-brain`.

Nhiệm vụ chính:
1. **Ingest (Nạp & Cô đọng):** Chắt lọc bài viết, tweet, session postmortem thành Atomic Notes chuẩn; **bắt buộc rà soát chống trùng lặp trước khi viết**.
2. **Recall / Query (Truy xuất):** Khi người dùng đặt câu hỏi hoặc làm task liên quan, tra cứu trong `INDEX.md` và `entries/` để lấy pattern và code mẫu thực chiến.

---

## 1. Quy Trình Nạp Bài Học Mới Tự Động (Auto-Ingest Workflow)

Khi người dùng nói: *"Lưu bài này vào second brain..."*, đưa link/tweet/tài liệu, hoặc yêu cầu *"học được gì từ session này lưu lại"*:

### Bước 1: Rà Soát Trùng Lặp Bắt Buộc (Search-Before-Write Gate)
**AI KHÔNG ĐƯỢC TỰ Ý TẠO FILE MỚI NGAY LẬP TỨC.** Bắt buộc chạy script kiểm tra:
```bash
/home/dungcq/projects/second-brain/scripts/check-duplicate.sh "<từ_khóa_1>" "<từ_khóa_2>"
```

### Bước 2: Rẽ Nhánh Hành Động (Branching Decision)

* **Trường hợp A: ĐÃ CÓ FILE CÙNG CHỦ ĐỀ / CÙNG DOMAIN (Mặc định)**
  - **Hành động:** Đọc file cũ, bổ sung nội dung mới vào đúng mục liên quan (ví dụ: thêm ca ngoại lệ vào Mục 3, thêm hàm parser/code vào Mục 4, hoặc thêm lưu ý vào Mục 2).
  - **Thông báo cho người dùng:** 
    > `[Second Brain] Đã rà soát: Chủ đề liên quan đến entries/<category>/<file_name>.md. Tiến hành cập nhật trực tiếp thay vì tạo file mới.`
  - **Tuyệt đối:** Không tạo file con xé lẻ (ví dụ: đã có `fnb-restaurant-p2p` thì không tạo thêm `fnb-invoice`).

* **Trường hợp B: CHỦ ĐỀ HOÀN TOÀN MỚI (0 match và khác domain)**
  - **Hành động:** Tạo file mới tại `entries/<category>/<tên-ngắn-gọn-kebab-case>.md` theo template chuẩn `templates/ENTRY-TEMPLATE.md`.
  - **Cập nhật mục lục:** Thêm link và keywords vào `/home/dungcq/projects/second-brain/INDEX.md` và bổ sung tags vào `# Tag Cloud`.
  - **Thông báo cho người dùng:**
    > `[Second Brain] Xác nhận chủ đề mới độc lập. Đã khởi tạo file: entries/<category>/<file_name>.md.`

### Bước 3: Nguyên Tắc Một Nguồn Sự Thật (Single Source of Truth)
- Nếu bài học có nhắc đến khái niệm của domain khác (ví dụ: BEO, VietQR, Zalo token, Docker), **chỉ dùng link chéo 1 dòng** (`[Xem chi tiết](../path/file.md)`), cấm chép lại định nghĩa hay code của file kia.

### Bước 4: Tự Động Đồng Bộ Git
Sau khi sửa/tạo file xong:
```bash
cd /home/dungcq/projects/second-brain && git add . && git commit -m "feat(brain): <mô tả ngắn>" && git push origin main
```

---

## 2. Nguyên Tắc Truy Xuất (Recall / Query Workflow)

Khi người dùng hỏi: *"Trong second brain có bài nào nói về X không?"* hoặc khi cần giải pháp kiến trúc:
1. Chạy `grep` / `ripgrep` hoặc đọc `INDEX.md` để xác định file chủ quyền.
2. Đọc file entry tương ứng và trích xuất đúng code, regex, hoặc bất biến nghiệp vụ trả lời người dùng.

---

## 3. Tiêu Chuẩn "Clean-Room Reconstructability" (Không Cưỡi Ngựa Xem Hoa)

Một ghi chú đạt chuẩn bắt buộc phải có đủ các tầng kỹ thuật thực chất (tùy theo bản chất chủ đề):

- **Đối với Hệ thống / Kiến trúc dữ liệu:**
  1. **Domain Invariants:** Sự thật vận hành thực tế vs lý thuyết sách vở; các ràng buộc cấm kỵ.
  2. **Authoritative Data Schema:** SQL DDL hoàn chỉnh (`BIGINT` thay vì `FLOAT` cho tiền tệ, khóa ngoại, chỉ mục) và struct/model.
  3. **State Machine & Guards:** Toàn bộ trạng thái vòng đời và điều kiện tiên quyết (guards) để chuyển trạng thái.
  4. **Core Algorithms & Parsers:** Regex chính xác, cấu trúc bóc tách dữ liệu cụ thể, công thức tính toán.
  5. **Edge Cases & Data Provenance:** Ít nhất 3 tình huống ngoại lệ thực địa; phân biệt rõ dữ liệu giả lập/seed với dữ liệu người dùng thật.

- **Đối với Agentic Workflows / Harness / Tooling:**
  1. **Failure Signature & Mechanism:** Lỗi cụ thể ở mức công cụ hoặc quy trình thực tế; phân biệt nguyên nhân kinh nghiệm (experience-driven) vs giáo điều (prior-driven).
  2. **Executable Harness / CLI Blueprint:** Cấu hình, script, schema theo dõi hoặc lệnh thực thi tất định để tái lập giải pháp.
  3. **Negative Transfer & Verification Probe:** Cơ chế đo lường độc lập để xác minh giải pháp thực sự giải quyết vấn đề mà không làm phình thời gian chạy hoặc tạo báo động giả.

---

## 4. Vòng Lặp Đánh Giá & Tỉa Bớt (Harness Retrospective & Pruning)

Theo nghiên cứu thực nghiệm về tự tiến hóa của agent harness (Baltes et al., 2026):
1. **Không nạp quy tắc giáo điều (prior-driven boilerplate):** Không đưa vào Second Brain các hướng dẫn chung chung không giải quyết lỗi đã xảy ra.
2. **Đo lường thuế ngữ cảnh (Harness Tax):** Các ghi chú phải súc tích, đi thẳng vào cơ chế và dữ liệu cần tái lập, tránh câu từ hoa mỹ làm loãng mật độ tìm kiếm.
3. **Chủ động tỉa bớt (Active Pruning):** Khi tra cứu hoặc đối chiếu, nếu phát hiện một ghi chú có quy tắc gây hiểu lầm hoặc tạo báo động giả trên tác vụ mới, chủ động cập nhật hoặc loại bỏ phần thừa.
