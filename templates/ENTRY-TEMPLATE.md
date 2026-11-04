# [Title / Topic Name]

> **One-liner:** [Tóm tắt giá trị kỹ thuật cốt lõi trong đúng 1 câu]

---

## Metadata
- **Source:** [URL / Paper / Repo / Production Database]
- **Author/Creator:** [Tên tác giả, handle @, tổ chức]
- **Captured Date:** [YYYY-MM-DD]
- **Tags:** `#tag1` `#tag2` `#tag3`
- **Category:** `[architecture | agentic-workflows | performance | formal-methods | web-creative]`

---

## 1. The Core Idea (Sự Thật Thực Địa & Vấn Đề Cốt Lõi)
- Vấn đề thực tế khác gì so với giả định ban đầu hoặc lý thuyết sách vở.
- Các bất biến cốt lõi (Domain Invariants) và những ràng buộc không được vi phạm.

---

## 2. Key Mechanisms & Patterns (Cơ Chế Chi Tiết)
- Mô hình kiến trúc, phân vùng hoặc luồng điều phối chính.
- Các rào chắn kiểm soát, cơ chế bảo vệ trạng thái hoặc chống suy giảm hiệu năng.

---

## 3. Real-World Production Cases (Các Tình Huống Thực Tế)
- Mô tả 2-4 tình huống ngoại lệ hoặc điểm nghẽn đo đạc được trên thực địa.
- Phân tích nguyên nhân gốc rễ và cách xử lý triệt để.

---

## 4. Reconstructability Blueprint (Bản Vẽ Tái Dựng Độc Lập)

> **Tiêu chuẩn:** Cung cấp đầy đủ thông số kỹ thuật, schema, hoặc mã nguồn mẫu để kỹ sư khác tái lập lại toàn bộ giải pháp mà không cần tra cứu thêm. Chọn các khối tương ứng với bản chất bài toán; không thêm schema giả lập cho các bài thuần quy trình/tooling.

### A. Authoritative Schema & Types (Nếu có lưu trữ / giao tiếp)
```sql
-- DDL bảng, khóa ngoại, kiểu dữ liệu, chỉ mục (nếu là hệ thống dữ liệu)
```
```go
// hoặc TypeScript types / structs mô tả shape dữ liệu
```

### B. State Machine & Transition Guards (Nếu có vòng đời / trạng thái)
- Danh sách trạng thái và điều kiện tiên quyết (guards) để chuyển đổi.

### C. Core Logic, Parsers & Algorithms
- Biểu thức chính quy, hàm tính toán, bộ giải mã hoặc lệnh thực thi tất định.

### D. Verification Probes & Anti-Regression Checks
- Cách thức kiểm tra độc lập để xác minh giải pháp hoạt động trên thực tế.

---

## 5. Related Links & Notes
- Liên kết chéo: `[Tên Note](../category/note.md)`
