# Receipt bền vững: retry an toàn không đồng nghĩa exactly-once

> **One-liner:** Giữ nguyên danh tính một thao tác qua crash, làm hiệu ứng có tính idempotent và lưu riêng trạng thái không biết chắc đã gửi hay chưa.

---

## Metadata
- **Source:** Case study local `pi-assistant@269d6b9`: `.audit/issues.md` / `PIA-BUG-004`, `PIA-BUG-005`, `PIA-BUG-006`; `pi_assistant/store.py`, `pi_assistant/memory.py`, `pi_assistant/telegram.py`, `extensions/assistant-tools.ts`, `tests/test_store.py`, `tests/test_telegram.py`, `tests/extension.test.mjs`.
- **Author/Creator:** Dự án Pi Assistant; đúc kết từ lỗi ở ranh giới hai database và phân loại reminder.
- **Captured Date:** 2026-11-03
- **Tags:** `#architecture` `#idempotency` `#crash-recovery` `#outbox` `#delivery-ambiguity`
- **Category:** `architecture`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Một transaction ở database A không bao trùm hiệu ứng đã commit ở database B. Nếu hiệu ứng thành công nhưng receipt chưa được ghi, host có thể không biết lần gọi trước đã làm gì. Chỉ deduplicate hiệu ứng vẫn chưa đủ. Nếu thiếu identity bất biến, cùng call ID có thể bị replay với tham số khác.

Khi gửi qua mạng, có thêm trạng thái khác: server có thể đã nhận tin nhưng client không nhận được phản hồi. Không được biến “không biết” thành “chưa gửi”, rồi retry mù và gọi đó là exactly-once.

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

- **Reserve trước hiệu ứng.** Key là `(turn_id, call_id)`; `name` và `args` là payload bất biến. Persist bản ghi `prepared` trước khi gọi memory store. Đây là reservation, chưa phải receipt hoàn tất. So sánh tham số theo dạng chuẩn hóa nhất quán.
- **Replay giữ nguyên danh tính.** Cùng ID và cùng tham số được tiếp tục hoặc trả kết quả đã lưu. Cùng ID nhưng đổi tên tool hay tham số phải bị từ chối trước hiệu ứng tiếp theo.
- **Kiểm tra hợp đồng tool ở boundary.** TypeScript không tự kiểm tra JSON nhận từ mạng. Kiểm tra schema và variant; giới hạn payload lẫn thời gian chờ. Không đưa bearer capability vào lỗi hoặc context. Không theo redirect khi gửi capability.
- **Hiệu ứng xuyên DB phải idempotent.** Memory store dùng ID theo hash của text và source refs. Ghi lại cùng nội dung không tạo memory mới. Receipt ở host không thay thế được cơ chế này.
- **Phân biệt hiệu ứng cùng DB.** Task và reminder dùng chung state DB với receipt. Hiệu ứng và bản ghi `done` nằm trong cùng transaction. Không suy ra rằng replay mọi tool đều dựa vào dedup của memory.
- **Không có atomicity xuyên hai database.** Reserve, effect và complete là các bước có thể bị ngắt. Bảo đảm đến từ identity và khả năng replay, không phải một transaction chung giả định.
- **Outbox cần trạng thái mơ hồ.** Phân biệt từ chối rõ ràng với lỗi mạng. Timeout có thể xảy ra sau khi server đã nhận tin. Sau crash giữa lúc gửi, không tự động coi tin là chưa gửi.
- **Tách loại reminder trong dữ liệu.** Nhắc theo lịch thông thường khác follow-up cho task đang chờ chủ quyết định. Một reminder gắn task không tự động thuộc loại thứ hai. Nếu trộn chúng, bộ lọc trạng thái task có thể làm mất lịch nhắc hợp lệ.

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

**Khi dùng:** Native tool gây hiệu ứng, xử lý event, webhook, nhiều database hoặc outbound notification.

Pseudocode minh họa, không phải API có sẵn:

```text
identity = reserve_immutable(call_key, operation, canonical_args)
if identity has completed_result:
    return completed_result
result = apply_idempotently(call_key, canonical_args)
complete_receipt(call_key, result)
return result
```

**Chèn lỗi tại đúng ranh giới:**
1. Crash sau reserve nhưng trước effect: replay phải tiếp tục được.
2. Crash sau effect nhưng trước complete: replay không lặp hiệu ứng.
3. Replay cùng ID với args khác: phải bị từ chối, kể cả receipt còn ở trạng thái prepared.
4. Server nhận tin nhưng client mất phản hồi: không ghi sai thành “chưa gửi”.
5. Reminder bình thường gắn với task không ở `waiting_owner`: vẫn phải được gửi theo lịch.

**Chọn chính sách gửi rõ ràng:** Case study giữ tin mơ hồ để operator xử lý thay vì tự gửi lại. Cách này giảm nguy cơ trùng nhưng có thể khiến người dùng bỏ lỡ tin. Nếu phía nhận hỗ trợ idempotency key, dùng hợp đồng đó và kiểm chứng hiệu lực của nó. Không tuyên bố exactly-once chỉ vì có SQLite hoặc outbox.

## 4. Related Links & Notes
- [Sở hữu worker và thu hồi sau restart](worker-process-ownership-and-recovery.md).
- [Bộ nhớ có nguồn đối chiếu](../agentic-workflows/source-backed-agent-memory.md).
- [Giảm công điều phối thay vì đẩy trạng thái mơ hồ về người dùng](../agentic-workflows/attention-first-personal-assistant.md).
