# Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core (Zero-Frappe)

> **One-liner:** Toàn bộ bản đồ nghiệp vụ thực chiến của Ngon Ngon Catering (BEO dán tường bếp, Zalo Copilot UI, định giá tiền line_v2, 3-way matching mua hàng, và 12 bước an toàn HĐĐT) để kế thừa và tái thiết kế sang `go-ngonngon-admin`.

---

## Metadata
- **Source:** Mã nguồn & đặc tả vận hành thực tế tại `ngonngon-admin` + Google Sheets BEO 10.2026 (`1vGxShLjhL6UBRKAoq_L4qWtMpMQKf47m`).
- **Author/Creator:** Đội ngũ Vận hành & Kỹ thuật Ngon Ngon Catering (@dungcq).
- **Captured Date:** 2026-11-03
- **Tags:** `#architecture` `#catering-domain` `#beo-workflow` `#money-line-v2` `#zero-frappe` `#golang` `#3-way-matching` `#kiotviet-einvoice`
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

### A. Cấu Trúc Khung Lưới BEO Chuẩn (Google Sheets 1:1)
Mỗi tờ BEO là một trang A4 portrait (`@page { size: A4 portrait; margin: 8mm 10mm; }`) gồm 4 khối cố định:
- **Khối Header 6 dòng:**
  - `NGÀY THỰC HIỆN` (e.g. `1 & 2/10/2026`)
  - `LOẠI MENU` (e.g. `FOOD DELIVERY`, `LUNCH BENTO`, `TEA BREAK`, `BUFFET`)
  - `LOẠI HÌNH TIỆC` (`CÓ PHỤC VỤ` hoặc `KO PHỤC VỤ`)
  - `VỊ TRÍ TIỆC` (e.g. `AB2`, `B2.2.07`, `THEO LỊCH CALENDAR`)
  - `NGƯỜI NHẬN TIỆC` (Sales Coordinator, e.g. `YANMY`)
  - `MOBILE / EMAIL`
- **Banner Xám (`#a6a6a6`):** `CÁCH THỨC TỔ CHỨC`
- **Khối Khách & Logistics:**
  - `HOST / TÊN KHÁCH` | `BỘ PHẬN` (e.g. `MS HÀ`, `TST RMIT HN`)
  - `ĐỊA CHỈ` (địa chỉ giao hàng chi tiết)
  - `SỐ KHÁCH` (e.g. `33-40 PAX`, `150 PAX` — in to 12pt) | `THỜI GIAN` (e.g. `8.00 AM & 1.00 PM`)
- **Hai Cột Thực Đơn Song Song:**
  - Cột `THỨC ĂN (FOOD)`: Phân theo ca/phiên (`MORNING TEA BREAK`, `AFTERNOON`, `MENU 1 # FISH - 9P`). Tên món ghi rõ kèm định lượng (`× 33 pc`, `× 3 plt`, `× 15 Dĩa`). **Không nhét nhãn trạm bếp vào đây**.
  - Cột `THỨC UỐNG (BEVERAGE)`: Cà phê phin sữa đá, Trà Lipton, Nước suối (định lượng theo `Jug` / Bình, `Can` / Lon, `Ly`).
- **Hàng Chân:**
  - `LAYOUT / GIỜ CÓ BÀN`: e.g. `CÓ 4 BÀN`, `15 bàn tròn 10 ghế`.
  - `BỐ TRÍ VÀ YÊU CẦU KHÁC`: **In màu đỏ đậm (`#cc0000`)** cảnh báo dị ứng, ăn chay, chuẩn bị trước 15-30p.
  - `PAYMENT`: Ghi hình thức thanh toán (`PO`, `Chuyển khoản`, `Đã cọc 50%`) — **không ghi giá tiền**.

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

### C. Mua Hàng & Đối Chiếu 3 Bên (Purchasing & 3-Way Matching)
- **Ingest từ Zalo Bếp:** Đầu bếp nhắn nhu cầu vào nhóm Zalo ("Cần 5kg thịt bò, 10kg rau muống"). Bot gom lại, áp dụng debounce 180s khử trùng tin nhắn sửa chính tả.
- **Từ điển `Item Alias`:** Tự động chuẩn hóa tên gọi tắt/dân dã của bếp về mã hàng chuẩn trong kho.
- **Chụp phiếu `/capture`:** Nhân viên nhận hàng chụp ảnh phiếu giao hàng / hoá đơn viết tay. OCR bóc tách tên NCC, món, số lượng, đơn giá.
- **3-Way Matching:** Đối chiếu giữa (1) PO đặt hàng, (2) Phiếu giao hàng thực tế (OCR), (3) Báo giá NCC. Lệch số lượng hoặc giá vượt ngưỡng sẽ kích hoạt cảnh báo đỏ.
- **Thanh toán VietQR động:** Sinh mã QR chuẩn NAPAS kèm đúng số tiền và nội dung chuyển khoản để thu ngân thanh toán 1-chạm.

### D. 12 Bước Kiểm Tra An Toàn HĐĐT KiotViet KInvoice
1. Tra cứu tự động MST lấy tên công ty và địa chỉ pháp lý từ Tổng cục Thuế.
2. Kiểm tra tính hợp lệ của người mua (tên, email nhận hóa đơn, địa chỉ).
3. Đơn vị tiền tệ bắt buộc là VND.
4. Kiểm tra thuế suất từng dòng thuộc tập hợp hợp lệ (0%, 5%, 8%, 10%, không chịu thuế).
5. Khớp toán học từng dòng: $\text{Số lượng} \times \text{Đơn giá} = \text{Thành tiền}$.
6. Khớp tiền chiết khấu tổng và chiết khấu dòng.
7. Khớp tiền thuế VAT theo từng nhóm thuế suất.
8. Làm tròn tổng thanh toán là số nguyên đồng.
9. Kiểm tra định dạng email nhận hóa đơn.
10. Kiểm tra mã mẫu hóa đơn và ký hiệu hóa đơn KiotViet.
11. Xác thực token SSO KInvoice còn hạn.
12. Khóa chống xuất trùng (Idempotency Key): Đơn đã cấp số HĐĐT thì cấm hủy hoặc xuất đè.
*Lưu ý kiểm thử:* Luôn có Hard Guardrail chặn đứng API `einvoice_publish` trong môi trường test/QA để không xuất nhầm hóa đơn thật lên Thuế.

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
