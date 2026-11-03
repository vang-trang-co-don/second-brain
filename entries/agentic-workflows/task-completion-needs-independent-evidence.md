# Agent dừng chạy không có nghĩa là task đã hoàn tất

> **One-liner:** Tách tín hiệu kết thúc lượt suy luận khỏi việc nghiệm thu kết quả, rồi kiểm tra kết quả bằng một luồng độc lập.

---

## Metadata
- **Source:** Case study local `pi-assistant@269d6b9`: `.audit/issues.md` / `PIA-BUG-001`, `.audit/pi-grounding.md`, `pi_assistant/runtime.py`, `tests/test_verification.py`, `scripts/inspect_smoke.py`.
- **Author/Creator:** Dự án Pi Assistant; đúc kết từ một lượt chạy thật báo thành công sai và các lượt kiểm chứng tiếp theo.
- **Captured Date:** 2026-11-03
- **Tags:** `#agentic-workflow` `#verification` `#acceptance-evidence` `#failure-injection`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Có ít nhất ba việc khác nhau: runtime nhận prompt, agent ngừng sinh câu trả lời và công việc đạt yêu cầu. Không được dùng tín hiệu của việc trước để kết luận việc sau.

Trong lượt chạy lỗi, worker mở một agent khác rồi trả lời rằng công việc đang được xử lý. Host coi lượt hội thoại đã dừng là task đã xong, trong khi đầu ra chưa có. Sửa câu thông báo không giải quyết được lỗi: phải sửa quyền sở hữu công việc và điều kiện chuyển sang `succeeded`.

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

- **Hiểu đúng sự kiện runtime.** Trong bản Pi đã kiểm tra, phản hồi nhận prompt không phải hoàn tất. `agent_settled` báo lượt agent đã ngừng hoạt động; vẫn phải kiểm tra lỗi và điều kiện nghiệm thu. Không suy rộng tên sự kiện này sang phiên bản khác mà chưa đọc protocol.
- **Executor không tự chứng nhận thành công.** Sau khi executor dừng, mở verifier mới với công cụ chỉ đọc. Verifier nhận mục tiêu và điều kiện nghiệm thu, không chỉ bản tự đánh giá của executor.
- **Host kiểm tra bằng chứng.** Verifier phải trả JSON đúng schema. Host chỉ nhận file thường trong scratch, không nhận symlink. Host giới hạn kích thước file và tự tính hash. Hash xác nhận danh tính nội dung, không tự chứng minh nội dung đúng yêu cầu.
- **Kiểm tra lỗi ở nhiều lớp.** Văn bản không rỗng không đủ. Cần phân biệt lỗi provider, lỗi tool, dữ liệu verifier sai schema và bằng chứng không hợp lệ.
- **Đo sau bước thay đổi cuối.** Một lượt smoke test từng pass, nhưng cleanup đổi file đã ghi hash. Giữ lượt đó làm bằng chứng âm; sửa cleanup và chạy lượt mới. Không sửa lịch sử để tạo một lượt pass.
- **Verifier bằng model vẫn có thể sai.** Host kiểm tra cấu trúc; model kiểm tra độc lập. Cách này không phải chứng minh hình thức hoặc bảo đảm ngữ nghĩa tuyệt đối.

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

**Khi dùng:** Agent tạo code, báo cáo, file xuất hoặc thay đổi trạng thái bên ngoài.

Thiết kế ba mốc quan sát riêng:

```text
prompt được nhận
→ executor dừng và không còn công việc con chưa được quản lý
→ kết quả được kiểm chứng theo điều kiện nghiệm thu
```

Không bắt mọi loại task phải tạo file trong thiết kế tổng quát. Nhưng host hiện tại cần ít nhất một file hợp lệ để đặt trạng thái `succeeded`. Task chỉ có câu trả lời văn bản không thể đạt trạng thái này. Nếu verifier trả `blocked`, host chuyển task sang `waiting_owner` thay vì `failed`. Với API hoặc database, cần một phép đọc trạng thái độc lập phù hợp, không chỉ log lời gọi thành công.

**Các phép thử phải làm thất bại việc nghiệm thu:**
- Worker nói đã xong nhưng không có đầu ra.
- Worker kết thúc khi công việc con còn chạy.
- Verifier trả JSON sai hoặc không có bằng chứng.
- Bằng chứng là symlink, nằm ngoài vùng cho phép hoặc vượt giới hạn.
- File đổi sau khi ghi hash; số byte hoặc giá trị đích không khớp.

Trong repo case study, chạy `python3 scripts/check.py`. Dùng `python3 scripts/inspect_smoke.py <run-directory>` để đối chiếu bằng chứng hiện tại của lượt smoke test. Đây là các lệnh của repo `pi-assistant`, không phải của Second Brain.

## 4. Related Links & Notes
- [Quản lý vòng đời process của worker](../architecture/worker-process-ownership-and-recovery.md).
- [Thiết kế trợ lý để giảm công điều phối](attention-first-personal-assistant.md).
- [Bộ nhớ có nguồn không đồng nghĩa với thông tin đúng](source-backed-agent-memory.md).
