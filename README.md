# Second Brain (Kho Tri Thức Kỹ Thuật Động Của Cá Nhân)

> Kho lưu trữ, chắt lọc và tái sử dụng các ý tưởng, kiến trúc phần mềm, bài phân tích kỹ thuật và workflow độc đáo lượm lặt trên Internet. Được thiết kế tối ưu cho việc tương tác trực tiếp với AI Coding Agents.

---

## 🎯 Mục Tiêu Thiết Kế

1. **Executable Knowledge (Tri thức có thể thực thi):** Không phải là nơi "chôn" bookmark. Mỗi ghi chú đều phải có giá trị ứng dụng thực tế, đi kèm snippet, lint rule, hoặc pattern mẫu có thể nạp ngay vào session làm việc với AI.
2. **Atomic & Structured (Gọn gàng & Đơn nguyên):** Mỗi ghi chú giải quyết một ý tưởng hoặc một case study trọn vẹn, có metadata rõ ràng (`Source`, `Author`, `Tags`).
3. **Agent-Friendly:** Tích hợp với skill `second-brain` giúp AI tự động đọc, tìm kiếm theo ngữ cảnh, hoặc tự động nạp thêm kiến thức mới mà không gây ô nhiễm (bloat) prompt context.

---

## 📁 Cấu Trúc Thư Mục

```text
second-brain/
├── INDEX.md               # Mục lục tìm kiếm nhanh, cây tag và liên kết danh mục
├── README.md              # Giới thiệu & hướng dẫn vận hành
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

## 🚀 Cách Sử Dụng Với AI Agent

### 1. Nạp bài mới (Ingest):
Khi bạn gặp một bài viết, tweet, repo hay trên mạng, chỉ cần nói với AI:
> *"Lưu bài viết này vào second-brain: [URL hoặc nội dung]*"

AI sẽ:
- Trích xuất ý tưởng cốt lõi, cơ chế và cách ứng dụng.
- Tìm xem đã có bài liên quan chưa (để bổ sung) hay tạo mục mới trong `entries/`.
- Tự động cập nhật `INDEX.md`.

### 2. Tra cứu & Tái sử dụng (Recall / Query):
Khi gặp bài toán cần giải quyết, chỉ cần hỏi:
> *"Trong second-brain có pattern nào tối ưu game loop hoặc zero-allocation không?"*

AI sẽ tìm trong `INDEX.md` và các ghi chú liên quan để lấy đúng kiến thức ra áp dụng vào bài toán hiện tại.
