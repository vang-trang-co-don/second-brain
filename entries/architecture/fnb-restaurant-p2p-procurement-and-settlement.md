# Vận Hành Mua Hàng & Thanh Toán Nhà Hàng (F&B Restaurant P2P): Quy Trình Thực Địa, Đối Soát 3 Bên & Kiến Trúc Xử Lý Ngoại Lệ

> **One-liner:** Kiến trúc và quy luật nghiệp vụ P2P (Procure-to-Pay) giải quyết triệt để các góc khuất thực tế của nhà hàng Việt Nam: 3 ô độc lập, Kitchen Zero-Leakage, bóc tách hóa đơn VAT TT78 tất định, biến động giá tức thì và duyệt chi VietQR 2 tầng.

---

## Metadata
- **Source:** Hệ thống Nêm & Nếm Admin (`nemnem-admin`) + Dữ liệu thực chiến vận hành nhà hàng tại Việt Nam.
- **Author/Creator:** Đội ngũ Kỹ thuật & Vận hành Nêm & Nếm (@dungcq).
- **Captured Date:** 2026-11-03
- **Tags:** `#architecture` `#fnb-restaurant` `#p2p-procurement` `#kitchen-zero-leakage` `#three-way-matching` `#vietqr` `#price-volatility` `#einvoice-tt78`
- **Category:** `architecture`

---

## 1. The Core Idea (Sự Thật Vận Hành Thực Địa Ngành Nhà Hàng)

Triển khai quy trình mua hàng (Procure-to-Pay / P2P) từ các phần mềm ERP truyền thống (như SAP, MISA, ERPNext) vào nhà hàng thường thất bại vì giả định sai về thực tế vận hành tại Việt Nam:

1. **Sai lầm thác nước cứng nhắc (Waterfall Fallacy):** ERP ép buộc trình tự `Yêu cầu (PR) -> Đặt mua (PO) -> Nhập kho (GRN) -> Hóa đơn (Invoice) -> Thanh toán (Payment)`. Thực tế ở nhà hàng, hàng tươi sống giao lúc 5:00 - 6:00 sáng. Bếp phải nấu lúc 10:00 sáng. Nếu bắt đủ hóa đơn mới cho nhập kho hoặc chặn không cho thanh toán khi chưa có phiếu nhập thì nhà hàng phải đóng cửa.
2. **Phiếu giao hàng viết tay khác biệt hoàn toàn với Hóa đơn VAT:** Người giao rau, thịt chỉ cầm phiếu in nhiệt hoặc mẩu giấy viết tay nhàu nát. Hóa đơn VAT điện tử (TT78) chỉ về vào cuối tháng qua email hoặc Zalo, gom từ 10 đến 30 lần giao hàng.
3. **Bếp tuyệt đối không được nhìn thấy giá nhập (Kitchen Zero-Leakage):** Bếp nhìn thấy giá nhập và nhà cung cấp sẽ dễ phát sinh tiêu cực: thông đồng nâng giá hưởng hoa hồng, làm lộ bí mật tỷ suất lợi nhuận món ăn, hoặc so bì chi phí chế biến.
4. **Hao hụt và biến động giá xảy ra tại cửa kho mỗi ngày:** Rau dập, thịt mỡ, cân thiếu vài lạng là chuyện thường xuyên. Bắt nhân viên làm thêm "Phiếu trả hàng nhà cung cấp" (Debit Note) cồng kềnh sẽ khiến nhân viên bỏ qua khâu ghi chép, gây thất thoát số liệu.

Hệ thống P2P thực chiến tái cấu trúc toàn bộ quy trình xoay quanh **sự độc lập của 3 ô chứng từ**, **đối soát 3 bên linh hoạt**, và **tự động hóa đối soát thuế**.

---

## 2. Key Mechanisms & Patterns (Chi Tiết Cơ Chế & Kỹ Thuật)

### A. Mô Hình 3 Ô Độc Lập (Uncoupled 3-Box Execution)
Thay vì xâu chuỗi tuần tự, hệ thống quản lý 3 ô trạng thái song song trên cùng một đơn mua hàng:
1. **Ô Nhận Hàng (Receiving):** Kiểm soát số lượng thực tế đưa vào bếp (`actual_qty`, `returned_qty`, `per_received`).
2. **Ô Hóa Đơn (Billing / VAT Invoice):** Kiểm soát chứng từ pháp lý thuế (`bill_no`, `bill_date`, `issuer_tax_id`, `has_vat_invoice`, `vat_status`).
3. **Ô Thanh Toán (Payment):** Kiểm soát dòng tiền thực xuất (`paid_amount`, `outstanding_amount`, `payment_mode`, `payment_ref`).

Thứ tự thực thi hoàn toàn tự do:
- Nhận hàng trước $\rightarrow$ Hóa đơn VAT tới sau $\rightarrow$ Thanh toán sau.
- Tạm ứng tiền trước $\rightarrow$ Nhận hàng $\rightarrow$ Hóa đơn VAT gom cuối tháng.
- Nhà cung cấp lẻ không có hóa đơn VAT $\rightarrow$ Chốt công nợ và đóng đơn (`Closed`) mà không bị kẹt nghiệp vụ.

```
                  ┌──────────────────────┐
                  │ 1. Nhận hàng (Stock) │
                  └──────────┬───────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                                               ▼
┌───────────────────────────┐             ┌──────────────────────────┐
│ 2. Hóa đơn VAT (E-Invoice)│             │ 3. Thanh toán (Payment)  │
└───────────────────────────┘             └──────────────────────────┘
```

---

### B. Kitchen Zero-Leakage & Item Alias Dictionary
- **Phân quyền RBAC nghiêm ngặt:**
  - Role `kitchen` (Bếp) và `cashier` (Thu ngân): Chỉ được thao tác với tên hàng, số lượng yêu cầu (`qty`), số lượng thực nhận (`actual_qty`), và số lượng trả lại (`returned_qty`). Toàn bộ cột đơn giá (`rate`), thành tiền (`amount`), tổng tiền (`grand_total`), và thông tin nhà cung cấp bị ẩn hoàn toàn ở cả giao diện lẫn payload API trả về.
  - Role `purchasing` (Thu mua), `accountant` (Kế toán), `manager` (Quản lý): Nhìn thấy đầy đủ dữ liệu tài chính.
- **Từ điển tên gọi tắt (Item Alias):**
  - Tiếng Việt ngành F&B rất đa dạng: Bếp gõ "ba rọi", phiếu giao ghi "ba chỉ heo", hóa đơn ghi "thịt lợn ba chỉ loại 1".
  - Bảng `tabItem Alias` đóng vai trò bộ phân giải tên tự động: chuyển đổi các biến thể ngôn ngữ đời thường về duy nhất một mã nguyên vật liệu chuẩn (`Item Code`). Bếp không cần nhớ mã SKU.

---

### C. Xử Lý Trả Hàng & Hao Hụt Ngay Cửa Kho (Direct Return at Door)
- Khi nhà cung cấp giao hàng, nhân viên kiểm đếm và ghi nhận trực tiếp trên giao diện nhận hàng:
  - `actual_qty`: Số lượng thực nhận đạt chuẩn giữ lại dùng.
  - `returned_qty`: Số lượng trả lại do dập nát, hỏng, ươn hoặc giao thừa.
- Hệ thống tự động tính toán tức thì:
  $$\text{actual\_total} = \sum (\text{actual\_qty} \times \text{actual\_rate})$$
  $$\text{returned\_total} = \sum (\text{returned\_qty} \times \text{actual\_rate})$$
  $$\text{outstanding\_amount} = \text{actual\_total} - \text{paid\_amount}$$
- Không cần tạo thêm chứng từ "Phiếu trả hàng" (Purchase Return) rườm rà. Công nợ chốt trả cho nhà cung cấp tự động loại trừ tiền hàng hoàn trả ngay từ đầu.

---

### D. Bóc Tách Chứng Từ Kép: Vision OCR vs XML TT78 Tất Định
Hệ thống xử lý song song hai định dạng chứng từ với độ chính xác và chi phí tối ưu:
1. **Phiếu giao hàng viết tay / in nhiệt (Delivery Note):**
   - Chụp qua mobile web `/capture` hoặc upload ảnh.
   - Sử dụng AI Vision OCR bóc tách số phiếu, ngày giao, số lượng và đơn giá thực tế.
2. **Hóa đơn điện tử VAT (TT78/2021 XML):**
   - Xử lý hoàn toàn tất định bằng bộ phân tích XML (`lxml`), tốc độ < 5ms, độ chính xác 100%, không tiêu tốn token AI.
   - Trích xuất: Ký hiệu mẫu số (`KHMSHDon`), Ký hiệu hóa đơn (`KHHDon`), Số hóa đơn (`SHDon`), Ngày lập (`NLap`), MST đơn vị bán (`MST`), Tổng tiền trước thuế và Tiền thuế VAT (`TgTThue`).
   - Cảnh báo tự động nếu MST hoặc Tên đơn vị xuất trên hóa đơn không khớp với danh mục nhà cung cấp (`Supplier Issuer`).

---

### E. Ghi Vết Biến Động Giá Tức Thì (`Price Log`) & Cập Nhật Giá Forecast
- Giá nông sản, thực phẩm tươi sống biến động hàng ngày theo thị trường.
- Khi nhận hàng, nếu đơn giá thực tế (`actual_rate`) trên phiếu giao lệch so với đơn giá dự tính ban đầu (`rate`):
  - Hệ thống ghi một dòng kiểm toán vào `tabPrice Log` gồm: `item_code`, `old_rate`, `new_rate`, tỷ lệ chênh lệch `change_pct`, nguồn chứng từ `source_ref`.
  - Tự động cập nhật `Item.buying_price` mới nhất vào danh mục để lần đặt hàng tiếp theo tự động áp dụng đơn giá thị trường chuẩn.

---

### F. Cơ Chế Duyệt Chi 2 Bước (Two-Step Payment Approval)
Để đảm bảo an toàn dòng tiền và tránh thất thoát chi tiêu, hệ thống áp dụng nguyên tắc kiểm soát 2 tầng độc lập:
- **Tầng 1 — Thu mua Duyệt đối chiếu & Chốt công nợ (`purchasing_reviewed = 1`):**
  - Điều kiện: Đơn đã có NCC xác nhận (`supplier_confirmed = 1`) và Đã kiểm nhận hàng thực tế (`per_received > 0`).
  - Chuyên viên Thu mua kiểm tra tính hợp lệ giữa số thực nhận, số hàng trả lại và ảnh phiếu giao, sau đó bấm chốt đối chiếu. Đơn chuyển sang trạng thái `Chờ thanh toán` (`awaiting_payment`).
- **Tầng 2 — Quản lý / Giám đốc Duyệt chi (`payment_approved = 1`):**
  - Quản lý vào phân hệ Sổ nợ, kiểm tra chứng từ đính kèm và hạn nợ rồi bấm duyệt chi (hỗ trợ duyệt chi đơn lẻ hoặc duyệt chi hàng loạt).
  - Đơn chuyển sang trạng thái sẵn sàng để Kế toán xuất quỹ. Kế toán không thể thanh toán nếu chưa có cờ duyệt chi này.

---

### G. VietQR 1-Chạm & Quản Lý Hóa Đơn VAT Sau Thanh Toán
- **VietQR động gắn theo Pháp nhân:**
  - Sinh mã VietQR chuẩn NAPAS theo đúng tài khoản ngân hàng của từng nhà cung cấp.
  - Nội dung chuyển khoản chuẩn hóa gắn mã đơn (ví dụ: `PO-2026-00032`). Kế toán quét mã bằng app ngân hàng 1-chạm, không cần gõ tay số tài khoản hay số tiền.
  - Hỗ trợ **Thanh toán gộp (Batch Pay):** Gom nhiều đơn trong tuần của 1 NCC thành 1 lệnh chuyển tiền duy nhất.
- **Phân loại công nợ & Trạng thái nợ hóa đơn (`classify_ap_due_status`):**
  - `overdue`: Đơn còn nợ và đã quá hạn thanh toán (`due_date < today`).
  - `due_soon`: Đơn sắp tới hạn thanh toán trong vòng 3 ngày tới.
  - `unpaid`: Đơn chưa tới hạn thanh toán.
  - `paid_missing_vat`: **Đã thanh toán 100% tiền nhưng NCC chưa xuất HĐ VAT.** Trạng thái này giúp Kế toán có danh sách cụ thể để đòi hóa đơn đầu vào trước ngày 20 hàng tháng phục vụ báo cáo thuế.
  - `settled`: Đã thanh toán đủ tiền và đã đủ hóa đơn VAT (hoặc NCC không có VAT). Đơn chính thức đóng sổ.

---

## 3. Real-World Production Cases (Dữ Liệu Thực Tế Từ Production)

Dữ liệu khai thác trực tiếp từ Production `nemnem-admin`:

### Case 1: 1 Yêu cầu Bếp 29 món $\rightarrow$ Tự động phân bổ ra 6 PO riêng biệt
- **Chứng từ:** Đề xuất mua hàng `PSG-2026-02510` (Bếp yêu cầu 29 mặt hàng).
- **Thực tế:** Bếp chỉ cần gõ tên món thô và số lượng. Hệ thống tự động phân tách thành 6 đơn đặt hàng cho 6 nhà cung cấp khác nhau:
  - `PO-2026-00085`: 8 mặt hàng nông sản, rau củ, tôm sú gửi cho **Fresh Food**.
  - `PO-2026-00088`: Phô mai xanh Dana Blue 3kg và Nạc dăm heo gửi cho **Lovefood**.
  - `PO-2026-00089`: Thịt bò phi lê cắt sẵn gửi cho **Huỳnh Nữ Vissan**.
  - `PO-2026-00086`: Thanh cua Hoso Maki gửi cho **Green Food**.
  - `PO-2026-00090`: Bánh tráng cuốn gửi cho **Annam Gourmet Phú Mỹ Hưng**.
  - Các món chưa có nhà cung cấp cố định (*Bóng tôm* mua Shopee, *Hạt óc chó* mua Nhất Hương) được giữ lại ở hàng đợi xử lý ngoại lệ mà không làm tắc nghẽn toàn bộ ca bếp.

### Case 2: Đột biến giá +45.8% ghi nhận tự động vào `Price Log`
- **Chứng từ:** Đơn hàng `PO-2026-00032` (Nhà cung cấp: Fresh Food — Tổng tiền: 12,057,400 ₫).
- **Thực tế:** Khi kiểm nhận phiếu giao hàng `PDC-2026-02244`, hệ thống tự động phát hiện và ghi nhận vết biến động giá:
  - Đậu Hà Lan hạt: Giá dự tính đặt hàng `240,000 ₫/kg` $\rightarrow$ Phiếu giao thực tế tăng vọt lên `350,000 ₫/kg` (+45.8%).
  - Su hào: Tăng từ `22,000 ₫` lên `25,000 ₫/kg` (+13.6%).
  - Bắp Mỹ: Giảm từ `10,000 ₫` xuống `9,000 ₫/trái` (-10.0%).
  - Toàn bộ được lưu vết trong `tabPrice Log` và tự động cập nhật giá mua mới vào danh mục sản phẩm.

### Case 3: Đơn hàng quà tặng / Hàng bù 0 đồng (Zero-Cost PO)
- **Chứng từ:** Đơn hàng `PO-2026-00036` (Nhà cung cấp: Trái Cây Hải Sơn — Phiếu giao `HS-20261028-SAM`).
- **Thực tế:** Nhà cung cấp giao 7 bó Sâm (hàng bù đợt giao trước thiếu hoặc hàng tặng).
- **Xử lý:** Đơn giá = `0.0 ₫`, Thành tiền = `0.0 ₫`. Hệ thống xác nhận nhận đủ 100% để Bếp có số liệu nấu nước sâm, nhưng công nợ ghi nhận bằng `0.0 ₫`. Không sinh công nợ ảo, không yêu cầu duyệt chi hay thanh toán.

### Case 4: Mua ngoài siêu thị bán lẻ tự động bóc tách thuế VAT 8%
- **Chứng từ:** Các đơn mua ngoài phát sinh cho sự kiện:
  - `PO-2026-00039`: Bột ngàn lớp Montclair mua lẻ tại Annam Gourmet (Phiếu `SPMH-MH03-10203304`). Tiền hàng `90,000 ₫` $\rightarrow$ Công nợ chốt trả: `97,200 ₫` (8% VAT).
  - `PO-2026-00038`: Gói đồ trang trí Halloween từ Phong Thái (Phiếu `HD-HALLOWEEN-2810`). Tiền hàng `356,000 ₫` $\rightarrow$ Công nợ chốt trả: `384,480 ₫` (8% VAT).
  - `PO-2026-00037`: Ống hút từ Thành Phát Packing (Phiếu `D5408`). Tiền hàng `60,000 ₫` $\rightarrow$ Công nợ chốt trả: `64,800 ₫` (8% VAT).

---

## 4. Actionable Application: Data Shape & State Model

### A. State Model Vòng Đời Đơn Hàng (PO Lifecycle)
```typescript
export type POWorkflowStage = 
  | 'draft'               // Mới tạo từ PR, chưa gửi NCC
  | 'confirmed'           // NCC đã chốt đơn, đang chờ giao hàng
  | 'receiving'           // Đang nhận hàng, có hàng trả lại hoặc đang kiểm đếm
  | 'awaiting_approval'   // Thu mua đã đối chiếu, chờ Quản lý duyệt chi
  | 'awaiting_payment'    // Quản lý đã duyệt chi, chờ Kế toán chuyển tiền
  | 'paid_missing_vat'    // Đã chuyển tiền xong, đang đòi hóa đơn VAT
  | 'settled'             // Hoàn tất: Đã trả đủ tiền và đã đủ hóa đơn VAT
  | 'cancelled';          // Đã hủy đơn
```

### B. Core Purchase Order Data Shape
```typescript
export interface PurchaseOrderRecord {
  name: string;                   // Mã đơn: PO-YYYY-XXXXX
  company: string;                // Pháp nhân thanh toán
  supplier: string;               // Tên Nhà cung cấp
  supplier_tax_id?: string;       // Mã số thuế NCC
  
  // 1. Ô Nhận hàng & Hàng trả lại
  per_received: number;           // Tỷ lệ nhận hàng (%)
  actual_total: number;           // Tổng tiền hàng thực nhận giữ lại
  returned_total: number;         // Tổng tiền hàng trả lại tại chỗ
  delivery_note_file?: string;    // Link ảnh chụp phiếu giao hàng
  
  // 2. Ô Hóa đơn VAT điện tử
  has_vat_invoice: 0 | 1;         // Đã có hóa đơn VAT hay chưa
  bill_no?: string;               // Số hóa đơn (VD: 1C26TNN-0001234)
  bill_date?: string;             // Ngày lập hóa đơn
  vat_invoice_amount: number;     // Tổng tiền trên hóa đơn VAT
  vat_tax_amount: number;         // Tiền thuế VAT
  vat_status: 'Chờ HĐ VAT' | 'Đã đủ HĐ VAT' | 'Không có HĐ VAT';
  
  // 3. Ô Thanh toán & Duyệt chi
  purchasing_reviewed: 0 | 1;     // Thu mua đã duyệt đối chiếu công nợ
  payment_approved: 0 | 1;        // Quản lý đã duyệt chi
  paid_amount: number;            // Số tiền đã thanh toán
  outstanding_amount: number;     // Công nợ còn lại phải trả
  payment_mode?: string;          // Chuyển khoản VietQR, Tiền mặt...
  payment_ref?: string;           // Mã giao dịch ngân hàng / UNC
  
  // Trạng thái công nợ tổng hợp
  ap_status: 'overdue' | 'due_soon' | 'unpaid' | 'paid_missing_vat' | 'settled';
}
```

---

## 5. Related Links & Notes
- [Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core](ngonngon-catering-domain-and-architecture-handbook.md)
- [Receipt bền vững: retry an toàn không đồng nghĩa exactly-once](../architecture/durable-tool-receipts-and-delivery-ambiguity.md)
