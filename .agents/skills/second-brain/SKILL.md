---
name: second-brain
description: Quản lý và tra cứu Second Brain cá nhân (kho lưu trữ ý tưởng, case study kỹ thuật, kiến trúc, agentic workflow). Dùng khi người dùng muốn lưu lại một bài viết/tweet/ý tưởng hay trên internet, hoặc khi cần tra cứu các pattern/giải pháp đã từng lưu trữ trong second-brain.
---

# Second Brain Skill

Kỹ năng này biến AI thành **Người Thủ Thư Tri Thức Cá Nhân (Personal Knowledge Librarian)**, quản lý kho lưu trữ `/home/dungcq/projects/second-brain`.

Nhiệm vụ chính:
1. **Ingest (Nạp & Cô đọng):** Chắt lọc các bài viết, tweet, case study hay trên internet thành các ghi chú đơn nguyên (Atomic Notes) có cấu trúc chuẩn, tự động phân loại và cập nhật mục lục `INDEX.md`.
2. **Recall / Query (Truy xuất):** Khi người dùng đặt câu hỏi hoặc làm một task liên quan, tự động tra cứu trong `INDEX.md` và các file `entries/` để lấy ra pattern, code mẫu hoặc giải pháp đã lưu.

---

## 1. Nguyên Tắc Cốt Lõi Khi Nạp Kiến Thức (Ingest Workflow)

Khi người dùng nói: *"Lưu bài này vào second brain..."* hoặc đưa một link/tweet/tài liệu:

### Bước 1: Thu thập & Đánh giá nội dung
- Đọc hoặc fetch nội dung nguồn (qua fetch_content, web_search hoặc curl fxtwitter/vxtwitter nếu là post từ X/Twitter).
- Phân tích xem nội dung thuộc mảng nào: `agentic-workflows`, `performance`, `formal-methods`, `architecture`, `web-creative`, hoặc đề xuất thư mục mới nếu chưa có.

### Bước 2: Kiểm tra trùng lặp hoặc liên quan
- Đọc file `/home/dungcq/projects/second-brain/INDEX.md` và kiểm tra trong `entries/` xem đã có bài nào cùng chủ đề hoặc cùng tác giả chưa.
- **Nếu đã có bài liên quan:** Cập nhật/bổ sung vào bài đó hoặc tạo liên kết chéo (`[Link](../category/file.md)`).
- **Nếu là chủ đề mới:** Tạo file markdown mới trong `entries/<category>/<tên-ngắn-gọn-kebab-case>.md`.

### Bước 3: Soạn thảo theo chuẩn `templates/ENTRY-TEMPLATE.md`
Bài ghi chú bắt buộc gồm 4 phần:
1. **Metadata:** Nguồn link gốc, tác giả, ngày lưu, tags, category.
2. **The Core Idea:** 1-2 đoạn tóm tắt ý tưởng đột phá/lý do đáng lưu.
3. **Key Mechanisms & Patterns:** Liệt kê các chi tiết kỹ thuật cốt lõi (bullet points rõ ràng).
4. **Actionable Application:** Khi nào dùng và cách áp dụng cụ thể (snippet code, config, rule lint nếu có).

### Bước 4: Đồng bộ Mục Lục & Git
1. Cập nhật đường link và mô tả ngắn vào `/home/dungcq/projects/second-brain/INDEX.md`.
2. Thêm tags mới vào phần `# Tag Cloud` trong `INDEX.md`.
3. Tự động commit vào git repo: `git add . && git commit -m "feat(brain): add note on <topic>"`.
4. Nếu remote github đã cấu hình, push lên GitHub.

---

## 2. Nguyên Tắc Truy Xuất (Recall / Query Workflow)

Khi người dùng hỏi: *"Trong second brain có bài nào nói về X không?"* hoặc khi đang code mà cần tham khảo giải pháp:

1. Đọc `/home/dungcq/projects/second-brain/INDEX.md` hoặc dùng lệnh grep/ripgrep để tìm keywords trong `entries/`.
2. Đọc file entry tương ứng.
3. Trích xuất đúng thông tin cần thiết trả lời cho người dùng hoặc áp dụng trực tiếp vào đoạn code đang viết.
