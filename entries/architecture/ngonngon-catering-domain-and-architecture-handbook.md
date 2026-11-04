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

Khi tiếp tục phát triển `go-ngonngon-admin` (`/home/dungcq/projects/go-ngonngon-admin`), cấu trúc module được kế thừa như sau:

```
go-ngonngon-admin/
├── cmd/
│   ├── server/               # HTTP REST & Print Server (:8090)
│   └── cli/                  # CLI command runner (calc-quote, render-beo)
├── pkg/
│   ├── domain/
│   │   ├── money.go          # Lõi tính tiền line_v2 (100% VND integer)
│   │   ├── booking.go        # Struct Booking, Quotation, BEO snapshot (SHA256)
│   │   └── beo.go            # Operational model
│   ├── render/
│   │   └── beo_html.go       # HTML A4 portrait template chuẩn Google Sheets
│   ├── store/
│   │   └── store.go          # Thread-safe in-memory + JSON persistence
│   └── purchasing/           # Sắp tới: PO lifecycle, 3-way matching, VietQR
├── scripts/
│   └── verify_app.py         # Verification harness (launch, doctor, drive beo/quote, cleanup)
└── .agents/skills/verify/    # Project-local verification skill
```

### Snippet Test BEO Print & Money Parity (CLI)
```bash
# 1. Tính thử báo giá chuẩn line_v2
./bin/go-ngonngon-cli calc-quote --payload '{
  "lines": [
    {"line_id": "L1", "description": "Set VIP Cá Hồi", "qty": 10, "unit_price": 3500000, "tax_rate": 8}
  ],
  "discount_percentage": 5
}'

# 2. Sinh và in trực tiếp form BEO chuẩn A4 portrait
./bin/go-ngonngon-cli render-beo --out /tmp/beo_test.html
```

---

## 4. Related Links & Notes
- Dự án mới (Go): `/home/dungcq/projects/go-ngonngon-admin`
- Google Sheets thực tế BEO 10.2026: `https://docs.google.com/spreadsheets/d/1vGxShLjhL6UBRKAoq_L4qWtMpMQKf47m/edit`
- [Kỹ thuật Process Supervision & Worker Lifecycle](../architecture/worker-process-ownership-and-recovery.md)
- [Receipt bền vững & Transactional Outbox](../architecture/durable-tool-receipts-and-delivery-ambiguity.md)
