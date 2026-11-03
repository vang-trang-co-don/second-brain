# Sở hữu vòng đời worker, không chỉ giữ PID

> **One-liner:** Dùng process group, guardian và danh tính có thể đối chiếu để thu hồi worker sau crash; đừng gọi cơ chế đó là sandbox.

---

## Metadata
- **Source:** Case study local `pi-assistant@269d6b9`: `.audit/issues.md` / `PIA-BUG-002`, `PIA-BUG-003`; `pi_assistant/supervisor.py`, `pi_assistant/pi.py`, `tests/test_supervisor.py`, `tests/test_pi.py`.
- **Author/Creator:** Dự án Pi Assistant; đúc kết từ worker sống qua restart và tiến trình con giữ pipe.
- **Captured Date:** 2026-11-03
- **Tags:** `#architecture` `#process-supervision` `#crash-recovery` `#failure-injection`
- **Category:** `architecture`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Một worker thường là cây tiến trình, không phải một PID. Process chạy lệnh có thể thoát nhưng các process con vẫn chạy hoặc giữ stdout/stderr mở. Nếu host chờ EOF vô hạn, một task đã dừng có thể tiếp tục chiếm slot.

Restart host cũng không tự thu hồi những process thuộc phiên chạy cũ. Xác định thành phần sở hữu cây process. Xác định thời điểm bắt đầu quyền sở hữu. Đối chiếu danh tính trước khi thu hồi. Đây là bài toán vòng đời; giới hạn quyền truy cập là bài toán khác.

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

- **Tạo nhóm thực thi riêng.** Guardian là session leader và process group leader trong case study. Workload chạy dưới guardian và kế thừa group. Guardian thu hồi các thành viên còn lại khi workload thoát.
- **Không bỏ qua khoảng trống khi khởi động.** Guardian dùng parent-death signal và kiểm tra parent. Bên gọi đợi bắt tay readiness trước khi coi worker đã sẵn sàng. Chỉ thêm một lời gọi đặt tín hiệu chưa đủ để xử lý mọi race quanh lúc parent chết.
- **Lưu danh tính, không chỉ PID.** Hồ sơ sở hữu có boot identity, thông tin khởi tạo process và nonce. Recovery đối chiếu chúng trước khi xử lý nhóm cũ; PID hoặc file registry đơn lẻ không phải bằng chứng quyền sở hữu.
- **Thu hồi hậu duệ khi workload đã thoát.** `poll()` báo workload đã xong không chứng minh group đã sạch. Tiến trình con giữ pipe là một phép thử quan trọng.
- **Bound thời gian đọc và shutdown.** Chờ process, đọc RPC và đóng pipe cần deadline. Tiến trình không hợp tác không được giữ vô hạn một slot của host.
- **Giới hạn bảo đảm.** Process group và guardian không ngăn worker đọc file, dùng mạng hay gọi dịch vụ bằng quyền của chủ máy. Không mặc định chúng bắt được một tiến trình cố ý thoát group bằng cơ chế như `setsid`.

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

**Khi dùng:** Job runner, coding agent, browser worker, lệnh chạy lâu hoặc bất kỳ hệ thống nào phải sống qua restart.

**Thiết kế theo thứ tự:**
1. Chỉ định một thành phần sở hữu việc tạo, dừng và thu hồi worker.
2. Tách process group và vùng trạng thái của từng worker.
3. Xử lý crash ngay trong giai đoạn khởi động, không chỉ khi worker đã chạy ổn định.
4. Ghi hồ sơ có đủ danh tính để recovery từ chối PID cũ hoặc registry giả.
5. Thu hồi hậu duệ ngay cả khi workload đã thoát.
6. Giải phóng slot và pipe trong giới hạn thời gian.

**Ma trận lỗi nên chạy:**

| Tình huống | Điều cần quan sát |
|---|---|
| Parent chết khi bắt tay | Không còn worker chưa có chủ sở hữu |
| Workload thoát, child giữ pipe | Host không treo; slot được giải phóng |
| Host restart | Task cũ không bị giả định vẫn đang được quản lý |
| Registry có nonce hoặc boot identity sai | Không gửi tín hiệu đến process không xác định |
| Worker phớt lờ dừng nhẹ | Có deadline và đường thu hồi cưỡng bức |

Không chép một lệnh kill theo PID từ ghi chú này vào production. Đối chiếu danh tính và phạm vi sở hữu trước. Đánh giá containment riêng nếu cần hạn chế truy cập hoặc chống cố ý thoát phạm vi. Có thể dùng cgroup, user riêng hoặc container. Kiểm chứng quyền thực tế, không chỉ tên cơ chế.

## 4. Related Links & Notes
- [Agent dừng không đồng nghĩa task hoàn tất](../agentic-workflows/task-completion-needs-independent-evidence.md).
- [Receipt bền vững và trạng thái sau crash](durable-tool-receipts-and-delivery-ambiguity.md).
- [Trợ lý cá nhân và quyền sở hữu worker](../agentic-workflows/attention-first-personal-assistant.md).
