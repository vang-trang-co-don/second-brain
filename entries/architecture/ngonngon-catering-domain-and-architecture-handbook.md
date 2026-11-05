# Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core (Zero-Frappe)

> **One-liner:** Toàn bộ bản đồ nghiệp vụ thực chiến của Ngon Ngon Catering (BEO dán tường bếp, Zalo Copilot UI, định giá tiền line_v2, 3-way matching mua hàng, và 12 bước an toàn HĐĐT) để kế thừa và tái thiết kế sang `go-ngonngon-admin`.

---

## Metadata
- **Source:** Mã nguồn & đặc tả vận hành thực tế tại `ngonngon-admin` + Google Sheets BEO 10.2026 (`1vGxShLjhL6UBRKAoq_L4qWtMpMQKf47m`).
- **Author/Creator:** Đội ngũ Vận hành & Kỹ thuật Ngon Ngon Catering (@dungcq).
- **Captured Date:** 2026-11-03
- **Tags:** `#architecture` `#catering-domain` `#beo-workflow` `#money-line-v2` `#zero-frappe` `#golang` `#print-containment`
- **Category:** `architecture`

---

## 1. The Core Idea (Ý Tưởng & Sự Thật Vận Hành Thực Địa)

Xây dựng hệ thống quản trị F&B/Catering thường thất bại vì dev tự ngồi vẽ ra các giả định sai lầm (như bắt bếp cầm tablet quẹt quẹt, hay chia món theo trạm bếp lý thuyết). 

Ngon Ngon Catering vận hành theo các sự thật thực địa bất biến:
1. **BEO (Banquet Event Order) là Tờ Dán Tường Bếp**: Bếp không ai cầm máy chạy lòng vòng. Phiếu BEO giấy cứng A4 được dán cố định tại 1 vị trí trung tâm trong bếp để mọi người đi qua liếc nhìn định lượng. Khi có thay đổi phút chót, Manager in tờ mới dán đè lên.
2. **Zero-Financial Leakage**: BEO cho Bếp **tuyệt đối không có giá tiền, không có VAT, không có chiết khấu**. Bếp chỉ cần biết: Giờ ăn, số khách, tên món trơn tuột kèm số lượng/ĐVT, và lưu ý dị ứng/ăn chay.
3. **Manager Hotline Zalo là UI Làm Việc Chính**: Manager không rảnh ngồi gõ form web. Manager cầm điện thoại nhắn tin Zalo với khách và điều khiển AI Agent Copilot qua chat để sinh báo giá, duyệt BEO, và đối soát.
4. **Từ bỏ Monolith Frappe/ERPNext**: 55 DocTypes cồng kềnh, ORM chậm và lệch type giữa Python Dict và TypeScript đã được cô đọng về **Pure Go (`go-ngonngon-admin`)** khởi động < 0.01s, binary 13MB không cần Docker.

---

## 2. Key Mechanisms & Patterns (Chi Tiết Kỹ Thuật Cốt Lõi)

### A. Cấu Trúc Khung Lưới BEO Chuẩn & Kỹ Thuật Khóa Trần Trang In A4 (1-Page Containment)
Mỗi tờ BEO là một trang A4 portrait cố định, bắt buộc dán trọn vẹn trong 1 trang duy nhất để đầu bếp liếc nhanh trên tường:
- **Quy chuẩn trang in:** `@page { size: A4 portrait; margin: 6mm 8mm; }`.
- **Khóa trần chiều dọc (Vertical Budgeting):** Chiều cao vật lý của A4 là 297mm (~1122px). Trừ lề in 6mm–8mm, chiều cao khả dụng tối đa là **284mm** (~1070px).
- **CSS bắt buộc:** `.page-container { max-height: 284mm; overflow: hidden; page-break-inside: avoid; }`.
- **Nén ngân sách chiều dọc:** Bảng header hành chính nén padding `1px 4px` (không quá 160px), dành 70% diện tích cho 2 cột Món ăn và Đồ uống.
- **Khung 4 khối cố định:**
  - **Khối Header 6 dòng:** `NGÀY THỰC HIỆN`, `LOẠI MENU`, `LOẠI HÌNH TIỆC`, `VỊ TRÍ TIỆC`, `NGƯỜI NHẬN TIỆC`, `MOBILE / EMAIL`.
  - **Banner Xám (`#a6a6a6`):** `CÁCH THỨC TỔ CHỨC`.
  - **Khối Khách & Logistics:** `HOST / TÊN KHÁCH`, `BỘ PHẬN`, `ĐỊA CHỈ`, `SỐ KHÁCH` (in to 12pt), `THỜI GIAN`.
  - **Hai Cột Thực Đơn Song Song:**
    - Cột `THỨC ĂN (FOOD)`: Phân theo ca/phiên, tên món kèm định lượng (`× 33 pc`, `× 3 plt`). Không nhét nhãn trạm bếp.
    - Cột `THỨC UỐNG (BEVERAGE)`: Cà phê phin, trà, nước suối (định lượng theo `Jug`, `Can`, `Ly`).
  - **Hàng Chân:** `LAYOUT / GIỜ CÓ BÀN`, `BỐ TRÍ VÀ YÊU CẦU KHÁC` (in đỏ đậm `#cc0000` cảnh báo dị ứng/ăn chay), `PAYMENT` (ghi hình thức thanh toán, tuyệt đối không ghi giá tiền).

### B. Lõi Tính Tiền Báo Giá `line_v2` (Quotation Money Policy)
- **Đơn vị tiền:** Đồng nguyên (VND integer), cấm dùng float/cents. Làm tròn `math.RoundHalfUp`.
- **Thuế suất đa tầng theo dòng:**
  - Món ăn chế biến: 8% VAT.
  - Đồ uống có cồn / bia / dịch vụ phục vụ: 10% VAT.
  - Nông sản thô / chay đặc thù: 0% hoặc miễn thuế.
- **Hai cơ chế tính giá (`PriceBasis`):**
  - `exclusive`: Đơn giá chưa thuế:
    $$\text{LineNet} = \text{round}(\text{Qty} \times \text{UnitPrice})$$
    $$\text{LineTax} = \text{round}(\text{LineNet} \times \frac{\text{TaxRate}}{100})$$
    $$\text{LineGross} = \text{LineNet} + \text{LineTax}$$
  - `inclusive`: Đơn giá đã bao gồm thuế (dành cho tiệc trọn gói bao VAT):
    $$\text{RawGross} = \text{Qty} \times \text{UnitPrice}$$
    $$\text{LineNet} = \text{round}\left(\frac{\text{RawGross}}{1 + \text{TaxRate}/100}\right)$$
    $$\text{LineTax} = \text{round}(\text{RawGross}) - \text{LineNet}$$
- **Chiết khấu & Phí phục vụ:**
  - Chiết khấu tính trên `Subtotal Net`.
  - Phí phục vụ tính trên `Subtotal Net sau chiết khấu`.
  - $\text{GrandTotal} = \text{Subtotal} - \text{Discount} + \text{ServiceCharge} + \text{TotalVat}$.

### C. Mua Hàng & Đối Soát 3 Bên (P2P Procurement)
Toàn bộ đặc tả nghiệp vụ mua hàng thực địa, mô hình 3 ô độc lập, Kitchen Zero-Leakage, bóc tách XML hóa đơn VAT TT78 tất định, xử lý biến động giá và duyệt chi VietQR 2 tầng được chuẩn hóa tại tài liệu chuyên sâu độc lập:
$\rightarrow$ Xem chi tiết tại: [Vận Hành Mua Hàng & Thanh Toán Nhà Hàng (F&B Restaurant P2P)](fnb-restaurant-p2p-procurement-and-settlement.md).

---

## 3. Actionable Application (Bản Đồ Kế Thừa Sang `go-ngonngon-admin`)

Khi tiếp tục phát triển `go-ngonngon-admin` (`/home/dungcq/projects/go-ngonngon-admin`), cấu trúc module đã hoàn thiện như sau:

```
go-ngonngon-admin/
├── cmd/
│   ├── server/               # HTTP REST, Web Editor, Print & MCP Server (:8090)
│   └── cli/                  # CLI Runner (calc-quote, render-beo, bridge-quote, mcp)
├── pkg/
│   ├── domain/               # Lõi nghiệp vụ: Booking, Quotation line_v2 (VND integer), BEO SHA-256
│   ├── qr/                   # Bộ sinh mã VietQR Napas247 động cho tài khoản công ty
│   ├── render/               # Render HTML A4 BEO, Báo giá có VietQR, Dashboard & Web Editor (/edit)
│   ├── bridge/               # Cầu nối thực đơn bếp (MenuSessions) sang dòng báo giá thương mại
│   ├── excel/                # Đọc/ghi bảng tính Excel .xlsx đa sheet (excelize/v2)
│   ├── sheets/               # Đồng bộ hai chiều Google Sheets API v4 (batchUpdate)
│   ├── zalo/                 # Ingestion tin nhắn Zalo cá nhân, khử trùng lặp 24h & bóc tách tệp
│   ├── mcp/                  # Máy chủ MCP chuẩn JSON-RPC 2.0 (stdio & HTTP) cho AI Agent
│   ├── threads/              # Quản lý nhật ký chat JSONL bất biến
│   └── store/                # Thread-safe in-memory + JSON persistence
├── scripts/
│   ├── sync_zalo_history.mjs # Lắng nghe Zalo, tự tải nhị phân PDF/ảnh và đẩy webhook
│   ├── lint_rules.py         # 18 luật lint tĩnh bảo vệ kiến trúc và print standards
│   └── verify_app.py         # Verification harness (doctor, drive beo/quote/dashboard/bridge/excel)
└── .agents/skills/verify/    # Project-local verification skill & feature map
```

### Triển Khai Thực Tế Trên VPS nnc.erp
- **Go Core Service (`/etc/systemd/system/go-ngonngon.service`):** Chạy binary `bin/server` trên cổng `8090`, chỉ chiếm ~3MB RAM, chạy song song độc lập với Frappe (`:18080`) và POS (`:3000`).
- **Zalo Capture Service (`/etc/systemd/system/zalo-capture.service`):** Chạy script `sync_zalo_history.mjs` với `session.json` (`chmod 600`), tự động tải file nhị phân vào `evidence/media/` và đẩy webhook nội bộ.
- **Lưu trữ đám mây S3:** Tích hợp Vietnix S3 (`s3://nnc-erp/go-ngonngon/`) để sao lưu session và tài liệu tiệc.
- **Đấu nối AI Agent:** Cụm Beacon WeClaw (`weclaw-ngonngon-1` trên `:18790`) kết nối trực tiếp với MCP Server qua endpoint nội bộ `http://172.17.0.1:8090/api/mcp`. Agent `booking_manager_copilot` được gán binding trực tiếp với UID của Quản lý (`857989458439277100`).

### Snippet Thao Tác CLI & MCP
```bash
# 1. Khởi chạy MCP Server cho AI Agent
./bin/go-ngonngon-cli mcp

# 2. Cầu nối tự động thực đơn bếp sang báo giá có VietQR
./bin/go-ngonngon-cli bridge-quote --booking-id CASE-01-RMIT-HN-MULTI-DAY

# 3. Đồng bộ hai chiều với bảng tính BEO Google Sheets
./bin/go-ngonngon-cli import-beo-excel --file "BEO 10.2026.xlsx"
```

---

## 4. Related Links & Notes
- Dự án mới (Go): `/home/dungcq/projects/go-ngonngon-admin`
- Google Sheets thực tế BEO 10.2026: `https://docs.google.com/spreadsheets/d/1vGxShLjhL6UBRKAoq_L4qWtMpMQKf47m/edit`
- [Kỹ thuật Process Supervision & Worker Lifecycle](../architecture/worker-process-ownership-and-recovery.md)
- [Receipt bền vững & Transactional Outbox](../architecture/durable-tool-receipts-and-delivery-ambiguity.md)
