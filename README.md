# Second Brain (Kho Tri Thức Kỹ Thuật Động Của Cá Nhân)

> Kho lưu trữ, chắt lọc và tái sử dụng các ý tưởng, kiến trúc phần mềm, bài phân tích kỹ thuật và workflow độc đáo. Được thiết kế tối ưu cho việc tương tác trực tiếp với AI Coding Agents và hệ điều hành tác chiến pstack.

---

## 🎯 Mục Tiêu Thiết Kế

1. **Executable Knowledge (Tri thức có thể thực thi):** Không phải là nơi lưu bookmark thụ động. Mỗi ghi chú đều có giá trị ứng dụng thực tế, đi kèm DDL schema, state machine, hoặc pattern mẫu có thể nạp ngay vào session làm việc.
2. **Atomic & Structured (Gọn gàng & Đơn nguyên):** Mỗi ghi chú giải quyết một ý tưởng hoặc case study trọn vẹn, có metadata rõ ràng (`Source`, `Author`, `Tags`).
3. **Agent-Friendly & Zero Harness Tax:** Tích hợp với CLI `scripts/brain` và skill `second-brain`. Cho phép AI bóc tách đúng lát cắt (aspect) cần dùng mà không gây ô nhiễm (bloat) context window.

---

## 📁 Cấu Trúc Thư Mục

```text
second-brain/
├── INDEX.md               # Mục lục tìm kiếm nhanh, cây tag và liên kết danh mục
├── MANIFEST.json          # Danh mục máy đọc cho routing và aspect slicing
├── README.md              # Giới thiệu & hướng dẫn vận hành
├── scripts/
│   ├── brain              # CLI bóc tách lát cắt JIT (query, list, sync, check)
│   ├── check-duplicate.sh # Script kiểm tra chống trùng lặp trước khi viết
│   └── test_brain.py      # Bộ kiểm thử xác minh tính toàn vẹn của brain CLI
├── templates/             # Khuôn mẫu tài liệu chuẩn hóa
│   └── ENTRY-TEMPLATE.md  # Template cho mỗi bài note mới
└── entries/               # Các bài note được phân loại theo lĩnh vực
    ├── agentic-workflows/ # Kỹ thuật làm việc với AI Agent, prompt pattern, guardrails
    ├── performance/       # Kỹ thuật tối ưu hiệu năng, V8, low-memory, zero-alloc
    ├── formal-methods/    # TLA+, state machine verification, proof-based code
    ├── architecture/      # Thiết kế hệ thống, microservices, decoupling
    └── web-creative/      # Web Audio, Three.js, Canvas, Procedural generation
```

---

## 🚀 Cách Sử Dụng Với AI Agent & pstack

### 1. Nạp bài mới (Ingest):
Khi bạn gặp một bài viết, tweet, repo hay trên mạng, chỉ cần nói với AI:
> *"Lưu bài viết này vào second-brain: [URL hoặc nội dung]*"

AI sẽ:
- Rà soát trùng lặp bằng `scripts/check-duplicate.sh`.
- Trích xuất ý tưởng cốt lõi, cơ chế và cách ứng dụng.
- Bổ sung vào bài cũ hoặc tạo bài mới trong `entries/`.
- Cập nhật `INDEX.md`, đồng bộ `MANIFEST.json` và kiểm tra qua `scripts/brain check`.

### 2. Tra cứu & Tái sử dụng (Recall / Query):
Khi gặp bài toán cần giải quyết, chỉ cần hỏi hoặc gọi CLI `scripts/brain`:
```bash
# Lấy bất biến nghiệp vụ cốt lõi (Domain Invariants)
scripts/brain query <domain-id-hoặc-trigger> --aspect invariants

# Lấy schema DDL và data struct
scripts/brain query <domain-id-hoặc-trigger> --aspect schema

# Lấy các ca ngoại lệ thực địa để viết test
scripts/brain query <domain-id-hoặc-trigger> --aspect cases

# Lấy các rào chắn kiểm tra và bài học thẩm định
scripts/brain query <domain-id-hoặc-trigger> --aspect probes
```

### 3. Phối hợp nhịp nhàng với pstack:
- **/architect (Phase A: Grounding):** Tự động đối chiếu `MANIFEST.json` và nạp `invariants` vào Rationale như Hard Constraints.
- **/tdd (Viết test suite):** Nạp `cases` và `probes` để bao phủ lỗi thực địa thay vì mock lý tưởng.
- **/thermos (Review diff):** Dùng `probes` và `schema` làm tiêu chuẩn nghiệm thu độc lập.
- **/reflect & /correct:** Lưu đúc kết session vào Second Brain và đồng bộ `MANIFEST.json`.
