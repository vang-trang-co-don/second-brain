# Triết Lý & Định Luật Phổ Quát Trong Kỹ Thuật Phần Mềm & Thiết Kế Kiến Trúc (Software Engineering Laws & Universal Heuristics)

> **One-liner:** Bộ cẩm nang thực chiến chắt lọc các định luật tự nhiên của phần mềm (Gall, Lehman, Conway, Hyrum), 3 la bàn kiến trúc bất biến (Coupling/Cohesion, Reversibility, State Scope) và 6 khẩu quyết thiết kế giúp kỹ sư xây dựng hệ thống bền vững trước sự tàn phá của thời gian.

---

## Metadata
- **Source:** *Software Engineering at Google* (Titus Winters), *A Philosophy of Software Design* (John Ousterhout), *Designing Data-Intensive Applications* (Martin Kleppmann), *Clean Architecture* (Robert C. Martin), và các bài học tái cấu trúc thực chiến.
- **Author/Creator:** dungcq x Antigravity pair-programming session
- **Captured Date:** 2026-11-06
- **Tags:** `#software-engineering` `#system-architecture` `#universal-laws` `#heuristics` `#clean-architecture` `#hexagonal` `#coupling-cohesion` `#reversibility` `#state-management` `#observability`
- **Category:** `architecture`

---

## 1. The Core Idea (Sự Thật Thực Địa & Vấn Đề Cốt Lõi)

### Sự khác biệt bản chất: Lập trình (Programming) vs Kỹ thuật phần mềm (Engineering)
* **Giả định sai lầm:** Dev thường đồng nhất "kỹ thuật phần mềm" với việc viết code chạy đúng logic, dùng ngôn ngữ xịn (Go, Rust), hoặc tách microservices cho hợp xu thế.
* **Sự thật thực địa (*Titus Winters - Google*):**
  > **"Software Engineering is programming integrated over time."**  
  > *(Kỹ thuật phần mềm là lập trình được tích phân theo chiều thời gian).*
* **Programming:** Giải quyết một bài toán ở thời điểm hiện tại $T_0$ (script cào dữ liệu, bài thi thuật toán, prototype làm một lần rồi bỏ). Không cần quan tâm ai đọc, ai bảo trì.
* **Engineering:** Đoạn code đó phải tồn tại qua $T_1, T_2, ... T_n$ (3 năm, 5 năm, 10 năm). Nó phải sống sót qua những đợt thay đổi nhân sự, đổi hệ điều hành, đổi thư viện, và quy mô người dùng tăng 100 lần.
* **Hai kẻ thù lớn nhất của Engineering:** **Sự thay đổi (Change)** và **Độ phức tạp (Complexity)**. Mọi nguyên lý kiến trúc sinh ra chỉ để kiềm chế hai kẻ thù này.

---

## 2. Bốn Định Luật Vật Lý Của Phần Mềm (Universal Laws)

Giống như UI/UX bị chi phối bởi các định luật tâm lý học nhận thức (Fitts, Hick, Miller), Kỹ thuật phần mềm bị chi phối bởi 4 định luật tự nhiên:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. ĐỊNH LUẬT GALL: Hệ phức tạp sống sót BẮT BUỘC tiến hóa từ hệ đơn giản│
├────────────────────────────────────────────────────────────────────────┤
│ 2. ĐỊNH LUẬT LEHMAN: Độ phức tạp tự tăng theo thời gian nếu không dọn   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. ĐỊNH LUẬT CONWAY: Kiến trúc phần mềm sao chép cấu trúc tổ chức team │
├────────────────────────────────────────────────────────────────────────┤
│ 4. ĐỊNH LUẬT HYRUM: Mọi hành vi quan sát được của API đều bị phụ thuộc │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Định luật Gall (Gall's Law)
* **Nội dung:** *Một hệ thống phức tạp mà hoạt động được, luôn luôn được tiến hóa từ một hệ thống đơn giản hoạt động được. Một hệ thống phức tạp được thiết kế mới toanh từ con số 0 sẽ không bao giờ hoạt động và không thể chắp vá cho nó hoạt động được.*
* **Ứng dụng:** Tránh bẫy Over-engineering. Bắt đầu bằng Monolith sạch sẽ, giải quyết trọn vẹn nghiệp vụ thực tế trước khi tính đến chuyện xé nhỏ microservices.

### 2. Định luật Lehman (Lehman's Laws of Software Evolution)
* **Nội dung:**
  1. *Continuing Change:* Một phần mềm đang được sử dụng thực tế bắt buộc phải biến đổi liên tục, nếu ngừng thay đổi nó sẽ trở nên vô dụng.
  2. *Increasing Complexity:* Khi phần mềm thay đổi, độ phức tạp của nó sẽ tự động tăng dần lên, trừ khi ta chủ động bỏ công sức ra tái cấu trúc (Refactoring) để hạ nó xuống.
* **Ứng dụng:** Refactoring không phải là việc "rảnh thì làm", mà là bảo dưỡng định kỳ bắt buộc như thay nhớt xe máy.

### 3. Định luật Conway (Conway's Law)
* **Nội dung:** *Cấu trúc hệ thống phần mềm phản ánh cấu trúc giao tiếp của tổ chức tạo ra nó.*
* **Ứng dụng:** Nếu team chỉ có 1–2 người làm chung một sản phẩm, việc xé ra 3 service viết bằng 3 ngôn ngữ khác nhau (Go, Python, PHP) sẽ tạo ra thảm họa giao tiếp và phân mảnh vận hành. Kiến trúc phải khớp với quy mô và khả năng vận hành của team.

### 4. Định luật Hyrum (Hyrum's Law)
* **Nội dung:** *Khi một API có đủ số lượng người dùng, tất cả mọi hành vi quan sát được của hệ thống (kể cả lỗi ngầm, thứ tự trả về, header không tài liệu) đều sẽ bị ai đó phụ thuộc vào.*
* **Ứng dụng:** Luôn khóa hợp đồng dữ liệu (API Contracts / Schemas / Envelopes) ngay tại biên giới giao tiếp. Không để lộ chi tiết nội bộ ra ngoài public API.

---

## 3. Ba La Bàn Đánh Giá Kiến Trúc (Architecture Evaluation Framework)

> **Martin Fowler:** *"Kiến trúc là tập hợp những quyết định khó thay đổi nhất (Architecture is the decisions that are hard to change)."*

Một kiến trúc tốt hay dở được đo lường bằng 3 la bàn độc lập với ngôn ngữ:

### La bàn 1: Coupling (Độ phụ thuộc) vs Cohesion (Độ gắn kết)
* **High Cohesion (Gắn kết cao):** Những thứ có lý do thay đổi cùng một thời điểm thì phải nằm cạnh nhau trong một module.
* **Low Coupling (Phụ thuộc thấp):** Khi đập vỡ hoặc sửa đổi module A, module B không được phép lăn ra chết theo.
* **Phép thử 30 giây:** Khi sếp đổi một quy tắc kinh doanh (ví dụ: công thức VAT hoặc điều kiện chiết khấu):
  * *Kiến trúc tồi:* Phải mở 5 file ở 3 repo khác nhau để sửa.
  * *Kiến trúc tốt:* Sửa đúng 1 file trong `core/domains/`, chạy unit test trong 0.01s là xong.

### La bàn 2: Tính có thể đảo ngược (Reversibility / Two-Way Door)
* Mọi quyết định kỹ thuật chia làm 2 loại:
  * **Cửa 2 chiều (Two-Way Door):** Bước qua rồi quay lại dễ dàng với chi phí thấp (đổi thư viện parse JSON, đổi UI button component).
  * **Cửa 1 chiều (One-Way Door):** Bước qua là khóa chết, quay lại tốn hàng năm trời và ngân sách khổng lồ (chia database, phân tán microservices, chọn framework độc quyền trói chặt ORM).
* **Quy tắc vàng:** Kiến trúc xuất sắc là kiến trúc trì hoãn các quyết định cửa 1 chiều lâu nhất có thể, giữ cho hệ thống luôn có đường lui.

### La bàn 3: Thu hẹp phạm vi trạng thái (State & Mutability Management)
* Toán học không bao giờ có bug ($1 + 1$ luôn bằng $2$). Bug phần mềm sinh ra do: **Một vùng nhớ (State) bị thay đổi bởi quá nhiều tác nhân vào những thời điểm không thể kiểm soát.**
* **Nguyên tắc xử lý:**
  1. *Pure Functions:* Lõi nghiệp vụ chỉ nhận input và trả output, không làm biến đổi biến bên ngoài (no side-effects).
  2. *Single Writer:* Một thực thể dữ liệu chỉ được phép có duy nhất một nơi sở hữu quyền ghi.
  3. *Immutability & Audit Trail:* Ưu tiên ghi nối tiếp (append-only log / outbox pattern) thay vì ghi đè trực tiếp làm mất dấu vết lịch sử.

---

## 4. Sáu Khẩu Quyết Kỹ Thuật Cốt Lõi (The 6 Universal Heuristics)

| Khẩu quyết | Bản chất kỹ thuật | Dấu hiệu vi phạm | Thực tế áp dụng |
|---|---|---|---|
| **1. Lõi sạch, Vỏ dơ** | Hexagonal / Clean Architecture (Pure Core vs Adapters) | Hàm tính tiền, duyệt đơn phải truyền `request`, `db_session` | `core/` 100% pure Python, không import ORM, test chạy 0.010s |
| **2. Giao diện mỏng, Ruột sâu** | Deep Modules (*Ousterhout*): Bề mặt đơn giản, nội lực xử lý mạnh mẽ | Gọi 1 hàm phải pass 10 tham số config hoặc gọi 3 hàm phụ | Nút `Esc` trong UI B2B: đóng đúng cửa sổ nổi mà không cần hỏi lại |
| **3. Dán biển số ngay từ cổng** | Correlation ID & Dual Envelope Tracing | Lỗi 500 nhưng không biết request từ ai, payload gì, chết ở đâu | Nginx/Gateway tiêm `X-Request-ID`, log in kèm ID, trả `fnb_meta` |
| **4. Soi căn cước tại cửa** | Boundary Discipline & Parse, Don't Validate | Cùng một điều kiện check dữ liệu lặp lại ở 4 tầng khác nhau | Chốt chặn DTO ở API Route; vào trong lõi thì tin tưởng dữ liệu 100% |
| **5. Xóa trước, Xây sau** | Subtract Before You Add (*Laziness Protocol*) | Chưa có khách đã dựng Microservices, Kafka, K8s để "đón đầu" | Gạt bỏ microservices thừa, gom về Monolith gọn gàng, giảm phí bảo trì |
| **6. Mách có lệnh chạy** | Command-First Execution & Independent Evidence | Sửa code xong click tay trên web xem có đúng không | Viết unit test hoặc lệnh CLI chạy ra kết quả kiểm chứng trước khi lên UI |

---

## 5. Khung Tư Duy 3 Câu Hỏi Khi Thẩm Định Thiết Kế (The 3-Question Compass)

Trước bất kỳ quyết định kiến trúc nào, kỹ sư chỉ cần trả lời 3 câu hỏi:

1. **Dữ liệu di chuyển như thế nào? (Dataflow):**
   * Vẽ được dòng chảy dữ liệu trên 1 trang giấy từ lúc nhận Input $\rightarrow$ qua các trạm biến đổi $\rightarrow$ Output/Lưu trữ. Nếu dòng chảy bị ngoằn ngoèo, vòng lặp ngược hoặc nhảy cóc, kiến trúc đang bị hỏng.
2. **Ai sở hữu dữ liệu này? (Single Source of Truth):**
   * Miếng dữ liệu này do ai quyết định trạng thái cuối cùng? Tuyệt đối không để 2 service cùng quản lý và tự tính một thông tin nghiệp vụ.
3. **Vùng ảnh hưởng khi chết là bao xa? (Blast Radius):**
   * Nếu thành phần này sập, mạng chập chờn hoặc DB nghẽn: sự cố dừng lại ở phạm vi nào? Nó cô lập tại chỗ hay kéo theo hiệu ứng domino làm sập toàn bộ hệ thống?

---

## 6. Related Links & Notes
- [Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core](ngonngon-catering-domain-and-architecture-handbook.md)
- [Triết Lý Thiết Kế & Công Thức Kỹ Thuật UI/UX B2B SaaS Tốc Độ Cao](b2b-saas-ui-ux-design-heuristics-and-engineering-patterns.md)
- [Receipt bền vững: retry an toàn không đồng nghĩa exactly-once](durable-tool-receipts-and-delivery-ambiguity.md)
- [Agent dừng chạy không có nghĩa là task đã hoàn tất](../agentic-workflows/task-completion-needs-independent-evidence.md)
