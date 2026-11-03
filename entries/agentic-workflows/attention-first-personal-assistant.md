# Trợ lý cá nhân phải giảm công điều phối của người dùng

> **One-liner:** Giữ hội thoại tự nhiên ở lớp ngoài; để host quản lý công việc, trạng thái và thông báo ở lớp trong.

---

## Metadata
- **Source:** Case study local `pi-assistant@269d6b9`: `.audit/requirements.md`, `.audit/design.md`, `.audit/pi-grounding.md`, `docs/morning-report.md`. Repo này chưa có nguồn công khai.
- **Author/Creator:** Dự án Pi Assistant; đúc kết từ thiết kế và các lượt chạy thực tế.
- **Captured Date:** 2026-11-03
- **Tags:** `#agentic-workflow` `#personal-assistant` `#human-attention` `#architecture`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Trợ lý không đạt mục tiêu nếu người dùng vẫn phải chia ticket và chọn agent. Người dùng còn phải canh tiến độ và kiểm tra lời báo xong. Đích đến là giảm công điều phối, không phải tăng số agent chạy cùng lúc.

Tách hai phần. Agent chính hiểu hội thoại và đề xuất hành động. Host sở hữu trạng thái bền vững, quyền công cụ, vòng đời worker và gửi kết quả. Cách này cho phép thay model mà không giao toàn bộ tính đúng đắn của hệ thống cho lời nhắc.

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

- **Chat không đồng nghĩa với giao việc.** Brainstorm có thể chỉ cần trao đổi. Tạo task khi có ý định thực hiện và điều kiện hoàn tất đủ rõ, không ép mọi tin nhắn thành biểu mẫu.
- **Hội thoại khác trạng thái công việc.** Tin nhắn giữ mạch trao đổi. Task có ID, trạng thái, kết quả và câu hỏi đang chờ. Không lấy câu trả lời cuối làm cơ sở duy nhất để khôi phục công việc sau restart.
- **Dùng công cụ có cấu trúc.** Model gọi native tool với tham số được kiểm tra. Không phân tích văn xuôi của model để đoán rằng nó muốn chạy lệnh hay đổi trạng thái.
- **Đọc hợp đồng runtime trước khi bọc API.** Đối chiếu source và chạy probe nhỏ. Trong bản Pi đã kiểm tra, `--models` không phải allowlist cưỡng chế. Không nhầm cấu hình chọn model với giới hạn quyền hoặc chi phí.
- **Một host sở hữu các tác vụ chạy nền.** Worker không tự mở thêm tiến trình rồi bỏ mặc chúng. Khi cần agent con, phải có cơ chế theo dõi vòng đời phù hợp.
- **Chờ quyết định nhưng không làm phiền liên tục.** Phân biệt nhắc lịch thông thường với nhắc trả lời câu hỏi đang chờ. Loại sau cần giãn khoảng nhắc và dừng sau khi có quyết định.
- **Giao kết quả đến người dùng.** Đường dẫn file trên máy chủ chưa phải trải nghiệm dùng điện thoại hoàn chỉnh.

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

**Khi dùng:** Xây trợ lý qua chat, hệ thống giao việc bằng ngôn ngữ tự nhiên hoặc một agent điều phối nhiều worker.

**Trước khi thêm tính năng, kiểm tra một hành trình ngắn:**
1. Người dùng trao đổi ý tưởng mà không tạo công việc ngoài ý muốn.
2. Người dùng giao một việc có kết quả quan sát được.
3. Người dùng tiếp tục nói chuyện trong khi việc đó chạy.
4. Host chỉ báo xong sau bước kiểm chứng riêng.
5. Restart không làm mất task, quyết định đang chờ hoặc kết quả chưa gửi.

**Giữ kết luận đúng phạm vi:** Case study đã chạy hành trình local với model thật. Telegram thật, tải file về điện thoại và workflow pstack phức tạp vẫn là việc tiếp theo. Quyền công cụ hạn chế giúp sở hữu worker rõ hơn, nhưng có thể làm mất khả năng gọi subagent mà một workflow cần. Các playbook như `arena`, `swarm`, `thermos` thiếu native tool `agent` trong worker hiện tại. Phải kiểm chứng sự tương thích, không coi đó là đánh đổi miễn phí.

**Câu hỏi thiết kế nên giữ:** Người dùng còn phải quay lại máy để làm gì? Ghi rõ những bước còn đòi hỏi người dùng quay lại máy. Đó có thể là tìm file, xử lý trạng thái mơ hồ hoặc giám sát agent con.

## 4. Related Links & Notes
- [Không đồng nhất agent dừng với task hoàn tất](task-completion-needs-independent-evidence.md).
- [Bộ nhớ có nguồn đối chiếu](source-backed-agent-memory.md).
- [Retry, receipt và gửi tin mơ hồ](../architecture/durable-tool-receipts-and-delivery-ambiguity.md).
- [Case study tibo.dog: mã hóa rào chắn vào hệ thống](poteto-tibo-dog-engineering.md). Áp dụng cùng hướng: đưa quy tắc quan trọng vào cấu trúc và kiểm tra, không chỉ thêm lời nhắc.
