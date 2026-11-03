# Bộ nhớ của agent cần nguồn đối chiếu, không chỉ câu tóm tắt

> **One-liner:** Giữ snapshot nguồn và đường truy xuất đến đoạn gốc; chỉ đưa phần cần dùng vào context, rồi quản lý riêng kiến thức đã chọn lọc.

---

## Metadata
- **Source:** Case study local `pi-assistant@269d6b9`: `pi_assistant/memory.py`, `tests/test_memory.py`, `.audit/design.md`, `docs/morning-report.md`.
- **Author/Creator:** Dự án Pi Assistant; đúc kết từ index lịch sử Pi và tài liệu được phép đọc.
- **Captured Date:** 2026-11-03
- **Tags:** `#agentic-workflow` `#agent-memory` `#provenance` `#retrieval` `#sqlite-fts5`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Bộ nhớ dài hạn không nhất thiết bắt đầu bằng cách gửi toàn bộ lịch sử cho model hoặc dựng một dịch vụ embedding. Có thể index nguồn trên máy, tìm vài đoạn liên quan và cho agent đọc lại bằng công cụ có giới hạn.

Bản tóm tắt cần trả lời ba câu hỏi. Thông tin đến từ đâu? Thông tin thuộc nhánh hội thoại nào? Có thể đọc lại đúng phiên bản đã trích không? Tuy nhiên, có nguồn không tự làm cho một kết luận đúng hoặc còn hiệu lực.

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

- **Tách dữ liệu nguồn và memory đã chọn lọc.** Archive giữ lịch sử và tài liệu. Curated memory giữ sự kiện hoặc sở thích đã chọn, kèm tham chiếu nguồn. Không biến mọi đoạn chat thành một sự thật bền vững.
- **Index nhánh đang hoạt động.** Với session dạng cây, không gộp mọi entry theo thứ tự ghi file. Nhánh đã bỏ có thể chứa quyết định bị thay thế. Cần dựng đúng chuỗi parent từ nhánh được chọn.
- **Snapshot bất biến cho provenance.** Nguồn hiện tại có thể đổi. Giữ phiên bản nội dung dùng để trích dẫn để ref cũ không âm thầm trỏ sang câu chữ mới. Reindex đánh dấu snapshot cũ không active, không xóa snapshot nguồn. Search bỏ qua snapshot cũ; đọc trực tiếp bằng ref vẫn truy xuất được.
- **Không dùng memory để chứng minh memory.** Curated memory chỉ dẫn snapshot nguồn session hoặc document. Case study từ chối lấy curated memory khác làm nguồn.
- **Tìm kiếm nhẹ trước.** Case study dùng SQLite FTS5 và chuẩn hóa dấu tiếng Việt để tìm kiếm từ vựng. Cách này không đồng nghĩa với hiểu ngữ nghĩa hay truy hồi được mọi câu diễn đạt lại.
- **Giới hạn phần đưa vào model.** Tìm ref, đọc đoạn liên quan rồi mới trả lời. Giới hạn số kết quả, độ dài đoạn đọc và kích thước phản hồi tool.
- **Dữ liệu không phải chỉ thị.** Lịch sử, tài liệu và ví dụ lệnh không có quyền điều khiển agent. Không cho phép một đoạn được retrieve tự nâng quyền hoặc thay chính sách hiện tại.
- **Kiểm tra ref khác kiểm tra ý nghĩa.** Ref tồn tại chưa chứng minh nguồn hỗ trợ phát biểu. Snapshot đọc được cũng chưa kiểm chứng ý nghĩa của memory.

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

**Khi dùng:** Trợ lý cá nhân, lịch sử quyết định hoặc dự án dài ngày. Áp dụng khi câu trả lời cần dẫn nguồn.

Bắt đầu với luồng nhỏ:

```text
nguồn được phép đọc → snapshot + index
câu hỏi → search → đọc đoạn nguồn → câu trả lời có ref
sự kiện cần giữ → memory có source_refs
```

**Kiểm tra trước khi thêm embedding:**
- Query có/không dấu có tìm được thông tin cần thiết không?
- Query diễn đạt khác bỏ sót bao nhiêu trường hợp thực tế?
- Nhánh bị bỏ có làm lẫn quyết định cũ vào kết quả không?
- Sau khi sửa file nguồn, ref cũ có đọc đúng nội dung đã lưu không?
- Agent có nhầm câu ví dụ, câu của assistant hoặc một suy đoán thành quyết định của người dùng không?
- Thông tin đã được sửa có còn bị lấy ra như một sự thật hiện hành không?

Đây là bộ câu hỏi để đánh giá tiếp, không phải tuyên bố case study đã chứng minh toàn bộ chất lượng memory. Case study kiểm chứng lưu và truy xuất nguồn trong hành trình local. Chất lượng ngữ nghĩa, sửa tri thức và refresh dài hạn vẫn cần đánh giá riêng.

Không index toàn máy theo mặc định. Chọn nguồn được phép, giữ dữ liệu thô cục bộ và tách quyền index khỏi quyết định gửi nội dung cho model. Không đưa dữ liệu cá nhân vào ghi chú công khai chỉ để minh họa provenance.

## 4. Related Links & Notes
- [Trợ lý giảm công điều phối của người dùng](attention-first-personal-assistant.md).
- [Bằng chứng đúng danh tính chưa đồng nghĩa đúng yêu cầu](task-completion-needs-independent-evidence.md).
- [Receipt bất biến khi ghi memory qua hai database](../architecture/durable-tool-receipts-and-delivery-ambiguity.md).
