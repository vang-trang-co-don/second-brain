# Second Brain Index & Knowledge Graph

> Mục lục tra cứu nhanh các kiến thức, case studies, kiến trúc kỹ thuật và ý tưởng đã được cô đọng.

---

## 🏷️ Tag Cloud
`#agentic-workflow` • `#reverse-engineering` • `#api-sniffing` • `#saas-constraints` • `#browser-fingerprint` • `#network-sniffing` • `#playwright` • `#print-containment` • `#spa-flakiness` • `#performance` • `#zero-alloc` • `#tla-plus` • `#game-dev` • `#headless-playtesting` • `#procedural-audio` • `#architecture` • `#personal-assistant` • `#human-attention` • `#verification` • `#acceptance-evidence` • `#failure-injection` • `#process-supervision` • `#crash-recovery` • `#idempotency` • `#outbox` • `#delivery-ambiguity` • `#agent-memory` • `#provenance` • `#retrieval` • `#sqlite-fts5` • `#catering-domain` • `#beo-workflow` • `#money-line-v2` • `#zero-frappe` • `#golang` • `#3-way-matching` • `#kiotviet-einvoice` • `#fnb-restaurant` • `#p2p-procurement` • `#kitchen-zero-leakage` • `#price-volatility` • `#einvoice-tt78` • `#vietqr` • `#pos-lifecycle` • `#pre-bill` • `#stale-detection` • `#shift-handover` • `#harness-engineering` • `#negative-transfer` • `#self-evolution` • `#pruning`

---

## 📂 Danh Mục Chủ Đề (Categories)

### 1. 🤖 Agentic Workflows & AI Software Engineering
* [Lauren (@poteto) - Kiến Trúc Kỹ Thuật & Agentic Workflow Game tibo.dog](entries/agentic-workflows/poteto-tibo-dog-engineering.md)
  * *Keywords:* 1,150 PRs trong 4 ngày, rào chắn lint rule, cấm comment code, headless bot playtesting.
* [Reverse Engineering SaaS Internal API & Bypassing Immutable Constraints](entries/agentic-workflows/reverse-engineering-saas-api-bypassing-immutable-constraints.md)
  * *Keywords:* Trích xuất cookie từ trình duyệt đang mở, dịch ngược SPA JS bundle, lách rào cản immutable IAM email & giới hạn quota license SaaS.
* [Browser Engine Matching, In-Flight Network Sniffing & 1-Page A4 Print Containment](entries/agentic-workflows/browser-engine-matching-and-network-sniffing.md)
  * *Keywords:* Đồng bộ browser engine khi nạp cookie Google, headed UI kết hợp passive network sniffer bắt file PDF trên đường truyền, kỹ thuật khóa trần trang in ấn A4 (1-page containment), login guard Zalo Web.

* [Trợ lý cá nhân phải giảm công điều phối của người dùng](entries/agentic-workflows/attention-first-personal-assistant.md)
  * *Keywords:* hội thoại tự nhiên, host sở hữu task, quyết định đang chờ, giới hạn của bản local.
* [Agent dừng chạy không có nghĩa là task đã hoàn tất](entries/agentic-workflows/task-completion-needs-independent-evidence.md)
  * *Keywords:* `agent_settled`, verifier chỉ đọc, hash do host tính, bằng chứng âm, kiểm tra sau cleanup.
* [Bộ nhớ của agent cần nguồn đối chiếu, không chỉ câu tóm tắt](entries/agentic-workflows/source-backed-agent-memory.md)
  * *Keywords:* nhánh session đang hoạt động, snapshot bất biến, provenance, SQLite FTS5, truy xuất có giới hạn.
* [Retrospective Harness Adaptation & Negative Transfer: Đánh Giá Thực Nghiệm Tự Tiến Hóa Agent](entries/agentic-workflows/retrospective-harness-adaptation-and-negative-transfer.md)
  * *Keywords:* Thuế harness (+198% latency), bẫy danh sách lỗi dở dang (false regression panic), đề xuất prior-driven vs experience-driven, chu trình canary-evaluate-prune.

### 2. ⚡ Performance & Systems

### 3. 📐 Formal Methods & Architecture
* [Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core (Zero-Frappe)](entries/architecture/ngonngon-catering-domain-and-architecture-handbook.md)
  * *Keywords:* BEO dán tường bếp (zero-financial), Zalo Copilot UI, định giá tiền line_v2 (VND integer), 3-way matching mua hàng, 12 bước an toàn HĐĐT KiotViet, chuyển dịch sang Pure Go (`go-ngonngon-admin`).
* [Sở hữu vòng đời worker, không chỉ giữ PID](entries/architecture/worker-process-ownership-and-recovery.md)
  * *Keywords:* Linux guardian, readiness, process group, parent chết, pipe bị giữ, identity khi recovery; không phải sandbox.
* [Receipt bền vững: retry an toàn không đồng nghĩa exactly-once](entries/architecture/durable-tool-receipts-and-delivery-ambiguity.md)
  * *Keywords:* immutable call identity, prepared receipt, hai database, outbox mơ hồ, phân loại reminder.
* [Vận Hành Mua Hàng & Thanh Toán Nhà Hàng (F&B Restaurant P2P): Quy Trình Thực Địa, Đối Soát 3 Bên & Kiến Trúc Xử Lý Ngoại Lệ](entries/architecture/fnb-restaurant-p2p-procurement-and-settlement.md)
  * *Keywords:* 3 ô độc lập (nhận hàng - hóa đơn - thanh toán), kitchen zero-leakage, PR triage workbench (chặn đơn vô lý/sửa số lượng), dự trù dòng tiền theo giá gần nhất, cold-start món mới giá 0đ, bóc tách XML TT78 tất định, xử lý trả hàng tại chỗ, price log tự động, duyệt chi VietQR 2 tầng, quản lý nợ HĐ VAT sau thanh toán (`paid_missing_vat`).
* [Quản Lý Vòng Đời Tạm Tính POS Nhà Hàng: Nhận Diện Trực Quan & Cơ Chế Bắt Lệch Bill Thực Địa (Stale Pre-Bill Drift)](entries/architecture/fnb-pos-pre-bill-lifecycle-and-stale-drift-detection.md)
  * *Keywords:* Bộ ba trạng thái tạm tính, phân biệt pre-bill vs settled invoice, thuật toán bắt lệch bill stale drift tự động, visual semantics đa điểm (floor plan, quick switch bar, cart panel), bảo toàn qua giao ca & offline-first.
### 4. 🎨 Web Creative & Procedural Generation

---

## 🔍 Hướng Dẫn Thêm & Tra Cứu Kiến Thức
- Dùng skill `/second-brain` trong chat session để nạp thêm bài mới hoặc tra cứu.
- Các file mới cần tuân theo template chuẩn tại: `templates/ENTRY-TEMPLATE.md`.
