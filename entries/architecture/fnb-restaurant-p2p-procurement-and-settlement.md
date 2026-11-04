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

### B1. Thẩm Định Yêu Cầu Mua Hàng & Lớp Can Thiệp Thu Mua (PR Triage & Editing)
- **Lý do thực địa:** Bếp nhắn tin trong giờ vận hành cao điểm rất dễ gõ nhầm số lượng (ví dụ: cần 100 quả trứng nhưng gõ nhầm 1000 quả, hoặc gõ thừa số 0). Nếu hệ thống hoặc bot tự động chuyển PR thành PO gửi nhà cung cấp mà không qua kiểm duyệt, nhà hàng sẽ gánh chịu lượng hàng thừa khổng lồ gây hỏng hóc và đóng băng vốn lưu động.
- **Cơ chế kiểm soát tại Workbench Gom đơn:**
  - Bot chỉ bóc tách tin nhắn chat và lưu vào danh sách đề xuất (Draft Intake Lines), tuyệt đối không tự động phát hành PO chính thức.
  - Nhân viên Thu mua đóng vai trò người gác cổng (Gatekeeper) với đầy đủ 4 quyền can thiệp trước khi tạo PO:
    1. **Sửa số lượng:** Điều chỉnh trực tiếp số lượng vô lý (ví dụ: từ 1000 quả về 100 quả trứng).
    2. **Đổi món / Ghép mã:** Chuẩn hóa lại mã hàng nếu Bếp dùng từ lóng chưa có trong từ điển Alias.
    3. **Hoãn (Defer):** Đưa món chưa cần gấp sang danh sách "Chờ mua sau" để gom vào các đợt tiếp theo.
    4. **Xóa / Từ chối (Reject):** Hủy dòng yêu cầu nếu kiểm tra thấy kho mát vẫn còn đủ lượng tồn kho an toàn.
  - Chỉ khi Thu mua xác nhận danh sách hợp lệ và bấm "Tạo PO", hệ thống mới phân tách thành các PO gửi nhà cung cấp.

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

### E. Ghi Vết Biến Động Giá Tức Thì (`Price Log`), Dự Trù Dòng Tiền & Xử Lý Cold Start (Món Mới)
- **Bản chất thực tế của Đơn giá mua gần nhất:** 
  - Trong F&B, giá thực phẩm tươi sống biến động liên tục theo ngày và thời giá thị trường. Việc so sánh với đơn giá gần nhất **không nhằm mục đích ngăn chặn nhà cung cấp tăng giá**, mà để **dự trù dòng tiền chi tiêu (Cashflow Forecasting)**: giúp Quản lý và Kế toán biết trước hôm nay sẽ chi khoảng bao nhiêu tiền (`ordered_grand_total`) để chuẩn bị ngân quỹ.
- **Cơ chế ghi vết biến động giá (`tabPrice Log`):**
  - Khi nhận hàng, nếu đơn giá thực tế (`actual_rate`) trên phiếu giao lệch so với đơn giá dự tính ban đầu (`rate`):
    * Hệ thống ghi một dòng kiểm toán vào `tabPrice Log` gồm: `item_code`, `old_rate`, `new_rate`, tỷ lệ chênh lệch `change_pct`, nguồn chứng từ `source_ref`.
    * Tự động cập nhật `Item.buying_price` mới nhất vào danh mục để lần đặt hàng tiếp theo tự động lấy mốc giá thị trường này.
- **Xử lý món mới chưa từng mua (Cold Start / Missing Price):**
  - Khi món hàng chưa có lịch sử mua từ nhà cung cấp: Hệ thống khởi tạo đơn giá dự tính bằng `0 ₫` (`rate = 0`) và gắn nhãn cảnh báo màu vàng "Chưa có giá".
  - Thu mua có hai lựa chọn xử lý:
    1. Nhập giá báo trước từ nhà cung cấp (Manual Quote) sau khi gọi điện/nhắn tin hỏi giá.
    2. Giữ nguyên giá `0 ₫` để gửi PO đặt hàng, và chốt giá thực tế khi nhận hàng kèm phiếu giao.
  - **Khóa chặn an toàn (Guard Condition):** Hệ thống chặn nút "Duyệt chi" (`payment_approved`) nếu đơn giá thực tế vẫn bằng `0 ₫` (ngoại trừ hàng tặng/hàng bù khuyến mãi có cờ `is_free_item = 1`). Khi đơn hoàn tất, đơn giá thực nhận đầu tiên này tự động trở thành `buying_price` cho các PO kế tiếp.

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

### Case 5: Bếp gõ nhầm 1000 quả trứng và cơ chế chặn tại PR Triage Workbench
- **Chứng từ:** Đề xuất mua hàng từ nhóm chat Zalo Bếp ca sáng.
- **Thực tế:** Nhân viên bếp gõ tin nhắn: *"Trứng gà 1000 quả, hành lá 2kg, dầu ăn 5 lít"*. Nhu cầu thực tế của nhà hàng chỉ là 100 quả trứng dùng trong 2 ngày.
- **Xử lý:**
  - Bot intake bóc tách dòng `Trứng gà: qty = 1000` và hiển thị trên màn hình Gom đơn.
  - Thu mua phát hiện số lượng bất thường so với mức tiêu thụ trung bình, nhấn chỉnh sửa trực tiếp `qty` từ `1000` về `100` ngay tại giao diện Workbench trước khi tạo PO.
  - Kết quả: Đơn PO gửi NCC Fresh Food chỉ đặt đúng 100 quả trứng. Hệ thống ngăn chặn việc nhập thừa 900 quả trứng gây vỡ, hỏng hóc và tránh lãng phí hơn 2.5 triệu đồng tiền hàng.

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

## 5. Go Architecture Blueprint (Bản Vẽ Kỹ Thuật Tái Dựng Bằng Pure Go)

Hệ thống được thiết kế để có thể chuyển dịch hoàn toàn sang một microservice viết bằng **Go (Golang)** duy nhất (`go-nemnem-admin`), binary ~15MB, không cần Python hay Frappe runtime, cắm trực tiếp vào Frontend React SPA hiện tại.

### A. SQL Schema DDL (Tương thích PostgreSQL & SQLite)
```sql
-- 1. Bảng Nhà cung cấp
CREATE TABLE suppliers (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(64),
    tax_id VARCHAR(32),
    bank_code VARCHAR(32),        -- VCB, MB, ACB, TCB...
    bank_account VARCHAR(64),     -- Số tài khoản nhận tiền
    bank_account_name VARCHAR(255),
    payment_terms_days INT DEFAULT 0, -- Số ngày cho nợ (0 = thanh toán ngay)
    default_outlet VARCHAR(64) DEFAULT 'Bếp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Danh mục Hàng hoá / Nguyên vật liệu
CREATE TABLE items (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    uom VARCHAR(32) NOT NULL DEFAULT 'Kg',
    buying_price BIGINT NOT NULL DEFAULT 0, -- VND nguyên, không dùng float
    min_order_qty NUMERIC(10, 2) DEFAULT 1.0,
    default_supplier_id VARCHAR(64) REFERENCES suppliers(id),
    default_outlet VARCHAR(64) DEFAULT 'Bếp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Từ điển Tên gọi tắt (Item Alias)
CREATE TABLE item_aliases (
    id SERIAL PRIMARY KEY,
    alias_name VARCHAR(255) NOT NULL UNIQUE,
    item_id VARCHAR(64) NOT NULL REFERENCES items(id),
    confidence NUMERIC(3, 2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_item_aliases_alias ON item_aliases(alias_name);

-- 4. Bảng Đơn đặt hàng (Purchase Order)
CREATE TABLE purchase_orders (
    id VARCHAR(64) PRIMARY KEY,            -- PO-YYYY-XXXXX
    company VARCHAR(255) NOT NULL,
    supplier_id VARCHAR(64) NOT NULL REFERENCES suppliers(id),
    status VARCHAR(32) NOT NULL DEFAULT 'Draft', -- Draft, Confirmed, Receiving, To Bill, Settled, Cancelled
    schedule_date DATE NOT NULL,
    due_date DATE,
    delivery_time VARCHAR(16) DEFAULT '06:00',
    
    -- Baseline (Dự kiến ban đầu)
    ordered_grand_total BIGINT NOT NULL DEFAULT 0,
    
    -- Ô 1: Nhận hàng & Trả lại
    per_received NUMERIC(5, 2) DEFAULT 0.0,
    actual_total BIGINT NOT NULL DEFAULT 0,
    returned_total BIGINT NOT NULL DEFAULT 0,
    delivery_note_file TEXT,
    
    -- Ô 2: Hóa đơn điện tử VAT
    has_vat_invoice SMALLINT DEFAULT 0,
    bill_no VARCHAR(64),
    bill_date DATE,
    vat_invoice_amount BIGINT DEFAULT 0,
    vat_tax_amount BIGINT DEFAULT 0,
    vat_status VARCHAR(32) DEFAULT 'Chờ HĐ VAT', -- Chờ HĐ VAT, Đã đủ HĐ VAT, Không có HĐ VAT
    vat_invoice_file TEXT,
    
    -- Ô 3: Duyệt chi & Thanh toán
    purchasing_reviewed SMALLINT DEFAULT 0,
    purchasing_reviewed_by VARCHAR(128),
    purchasing_reviewed_at TIMESTAMP,
    payment_approved SMALLINT DEFAULT 0,
    payment_approved_by VARCHAR(128),
    payment_approved_at TIMESTAMP,
    paid_amount BIGINT NOT NULL DEFAULT 0,
    outstanding_amount BIGINT NOT NULL DEFAULT 0,
    payment_mode VARCHAR(64),
    payment_ref VARCHAR(128),
    paid_at TIMESTAMP,
    
    created_by VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_po_status ON purchase_orders(status);
CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_po_schedule_date ON purchase_orders(schedule_date);

-- 5. Bảng Chi tiết dòng đơn mua (Purchase Order Item)
CREATE TABLE purchase_order_items (
    id SERIAL PRIMARY KEY,
    purchase_order_id VARCHAR(64) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    item_id VARCHAR(64) REFERENCES items(id),
    raw_name VARCHAR(255) NOT NULL,
    qty NUMERIC(10, 2) NOT NULL,
    uom VARCHAR(32) NOT NULL,
    rate BIGINT NOT NULL,                  -- Đơn giá baseline
    amount BIGINT NOT NULL,
    received_qty NUMERIC(10, 2) DEFAULT 0.0,
    returned_qty NUMERIC(10, 2) DEFAULT 0.0,
    actual_rate BIGINT DEFAULT 0,          -- Đơn giá thực nhận trên phiếu giao
    actual_amount BIGINT DEFAULT 0
);

-- 6. Bảng Chứng từ mua hàng (Purchase Document)
CREATE TABLE purchase_documents (
    id VARCHAR(64) PRIMARY KEY,            -- PDC-YYYY-XXXXX
    purchase_order_id VARCHAR(64) REFERENCES purchase_orders(id),
    supplier_id VARCHAR(64) REFERENCES suppliers(id),
    file_path TEXT NOT NULL,
    is_delivery_note SMALLINT DEFAULT 0,
    is_vat_invoice SMALLINT DEFAULT 0,
    is_payment_proof SMALLINT DEFAULT 0,
    invoice_no VARCHAR(64),
    invoice_date DATE,
    amount BIGINT DEFAULT 0,
    issuer_name VARCHAR(255),
    issuer_tax_id VARCHAR(32),
    raw_ocr_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Bảng Lịch sử biến động giá (Price Log)
CREATE TABLE price_logs (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(64) NOT NULL REFERENCES items(id),
    supplier_id VARCHAR(64) NOT NULL REFERENCES suppliers(id),
    old_rate BIGINT NOT NULL,
    new_rate BIGINT NOT NULL,
    change_pct NUMERIC(5, 2) NOT NULL,
    source_type VARCHAR(64) NOT NULL,     -- 'Phiếu giao', 'Hoá đơn VAT', 'Báo giá'
    source_ref VARCHAR(64) NOT NULL,      -- Mã PO hoặc mã chứng từ
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Bảng Tin nhắn Chat Ingest (WhatsApp / Chat Bridge Buffer)
CREATE TABLE chat_message_logs (
    id VARCHAR(64) PRIMARY KEY,
    chat_id VARCHAR(128) NOT NULL,
    sender_name VARCHAR(128) NOT NULL,
    message_text TEXT NOT NULL,
    outlet VARCHAR(64) DEFAULT 'Bếp',
    summary_status VARCHAR(32) DEFAULT 'Chờ xử lý', -- 'Chờ xử lý', 'Đã gom PO', 'Bỏ qua'
    summary_ref VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### B. Core Go Structs & Idiomatic Domain Models
```go
package domain

import (
	"time"
)

type Money = int64 // Tiền tệ lưu bằng VND nguyên, tuyệt đối không dùng float

type UnifiedPOStage string
const (
	StageDraft            UnifiedPOStage = "draft"
	StageConfirmed        UnifiedPOStage = "confirmed"
	StageReceiving        UnifiedPOStage = "receiving"
	StageAwaitingApproval UnifiedPOStage = "awaiting_approval"
	StageAwaitingPayment  UnifiedPOStage = "awaiting_payment"
	StagePaidMissingVat   UnifiedPOStage = "paid_missing_vat"
	StageSettled          UnifiedPOStage = "settled"
	StageCancelled        UnifiedPOStage = "cancelled"
)

type PurchaseOrder struct {
	ID                string         `json:"name"`
	Company           string         `json:"company"`
	SupplierID        string         `json:"supplier"`
	SupplierName      string         `json:"supplier_name"`
	Status            string         `json:"status"`
	Stage             UnifiedPOStage `json:"stage"`
	ScheduleDate      string         `json:"schedule_date"`
	DueDate           string         `json:"due_date"`
	
	// Financials
	OrderedGrandTotal Money          `json:"ordered_grand_total"`
	ActualTotal       Money          `json:"actual_total"`
	ReturnedTotal     Money          `json:"returned_total"`
	PaidAmount        Money          `json:"paid_amount"`
	OutstandingAmount Money          `json:"outstanding_amount"`
	
	// Proof Flags
	PerReceived        float64       `json:"per_received"`
	PurchasingReviewed bool          `json:"purchasing_reviewed"`
	PaymentApproved    bool          `json:"payment_approved"`
	HasVatInvoice      bool          `json:"has_vat_invoice"`
	VatStatus          string        `json:"vat_status"`
	BillNo             string        `json:"bill_no"`
	
	Items []POItem `json:"items,omitempty"`
}

type POItem struct {
	ID           int64   `json:"id"`
	ItemID       string  `json:"item_code"`
	RawName      string  `json:"item_name"`
	Qty          float64 `json:"qty"`
	UOM          string  `json:"uom"`
	Rate         Money   `json:"rate"`
	Amount       Money   `json:"amount"`
	ReceivedQty  float64 `json:"received_qty"`
	ReturnedQty  float64 `json:"returned_qty"`
	ActualRate   Money   `json:"actual_rate"`
	ActualAmount Money   `json:"actual_amount"`
}
```

---

### C. Chat Message Tokenizer & Intake Parser (Thuần Go Regex)
Chuyển đổi chuỗi tin nhắn của nhân viên thành mảng thực thể món:
```go
package intake

import (
	"regexp"
	"strconv"
	"strings"
)

type ParsedRequestItem struct {
	RawName string
	Qty     float64
	UOM     string
}

// ItemRegex khớp: "Thịt bò phi lê 2 Kg", "Dưa hấu 30 kg", "Hoành thánh tôm 5 Hộp"
var lineItemRegex = regexp.MustCompile(`(?i)^(.+?)\s+([0-9]+(?:[\.,][0-9]+)?)\s*([a-zA-Z\p{L}]+)$`)

func ParseChatText(text string) []ParsedRequestItem {
	var items []ParsedRequestItem
	// Tách theo dấu phẩy hoặc xuống dòng
	rawTokens := strings.FieldsFunc(text, func(r rune) bool {
		return r == ',' || r == '\n' || r == ';'
	})

	for _, token := range rawTokens {
		trimmed := strings.TrimSpace(token)
		if trimmed == "" {
			continue
		}
		matches := lineItemRegex.FindStringSubmatch(trimmed)
		if len(matches) == 4 {
			name := strings.TrimSpace(matches[1])
			qtyStr := strings.ReplaceAll(matches[2], ",", ".")
			qty, _ := strconv.ParseFloat(qtyStr, 64)
			uom := strings.TrimSpace(matches[3])

			items = append(items, ParsedRequestItem{
				RawName: name,
				Qty:     qty,
				UOM:     uom,
			})
		}
	}
	return items
}
```

---

### D. Parser Hóa Đơn Điện Tử TT78 Bằng `encoding/xml` Chuẩn
Bóc tách file XML hóa đơn gốc trong 0ms, không cần AI:
```go
package einvoice

import (
	"encoding/xml"
	"strconv"
)

type HDonTT78 struct {
	XMLName xml.Name `xml:"HDon"`
	DLHDon  struct {
		TTChung struct {
			KHMSHDon string `xml:"KHMSHDon"`
			KHHDon   string `xml:"KHHDon"`
			SHDon    string `xml:"SHDon"`
			NLap     string `xml:"NLap"`
		} `xml:"TTChung"`
		NDHDon struct {
			NBan struct {
				Ten string `xml:"Ten"`
				MST string `xml:"MST"`
			} `xml:"NBan"`
			DSHHDVu struct {
				HHDVu []struct {
					THHDVu string  `xml:"THHDVu"`
					DVTinh string  `xml:"DVTinh"`
					SLuong float64 `xml:"SLuong"`
					DGia   float64 `xml:"DGia"`
					ThTien float64 `xml:"ThTien"`
				} `xml:"HHDVu"`
			} `xml:"DSHHDVu"`
			TToan struct {
				TgTThue float64 `xml:"TgTThue"`
				TgTTTBSo float64 `xml:"TgTTTBSo"`
			} `xml:"TToan"`
		} `xml:"NDHDon"`
	} `xml:"DLHDon"`
}

func ParseEInvoiceXML(data []byte) (*HDonTT78, error) {
	var invoice HDonTT78
	if err := xml.Unmarshal(data, &invoice); err != nil {
		return nil, err
	}
	return &invoice, nil
}
```

---

### E. Bộ Sinh Mã VietQR Chuẩn NAPAS Trong Go
```go
package vietqr

import (
	"fmt"
	"net/url"
)

func GenerateVietQRUrl(bankCode, bankAccount, accountName string, amount int64, content string) string {
	escapedName := url.QueryEscape(accountName)
	escapedContent := url.QueryEscape(content)
	// Chuẩn VietQR Quicklink compact2
	return fmt.Sprintf(
		"https://img.vietqr.io/image/%s-%s-compact2.png?amount=%d&addInfo=%s&accountName=%s",
		bankCode, bankAccount, amount, escapedContent, escapedName,
	)
}
```

---

### F. Khế Ước REST JSON API Tương Thích 1:1 Với React SPA
Các endpoint Go cần phục vụ để chạy trực tiếp với `frontend/`:
1. `GET /api/v1/purchasing/bootstrap` $\rightarrow$ Trả về danh sách đơn mua, nhà cung cấp, thống kê nợ và việc cần làm (`AttentionQueue`).
2. `POST /api/v1/purchasing/orders/:id/receive` $\rightarrow$ Nhập `actual_qty`, `returned_qty`, `actual_rate`. Tự động tính `actual_total`, cập nhật `Price Log` và `per_received`.
3. `POST /api/v1/purchasing/orders/:id/review` $\rightarrow$ Thu mua chốt công nợ (`purchasing_reviewed = 1`), chuyển đơn sang giai đoạn chờ duyệt chi.
4. `POST /api/v1/purchasing/orders/approve-batch` $\rightarrow$ Body: `{"orders": ["PO-01", "PO-02"]}`. Quản lý duyệt chi (`payment_approved = 1`).
5. `GET /api/v1/purchasing/debt-list` $\rightarrow$ Trả về bảng công nợ phân loại: `overdue`, `due_soon`, `unpaid`, `paid_missing_vat`, `settled` kèm URL VietQR tương ứng.
6. `POST /api/v1/purchasing/pay` & `POST /api/v1/purchasing/batch-pay` $\rightarrow$ Xác nhận thanh toán, đính kèm ảnh UNC, trừ `outstanding_amount`.

---

## 6. Bài Học Thẩm Định Thực Địa & Bằng Chứng Âm (Negative Evidence Trap)

Khi phân tích hoặc trích xuất dữ liệu từ một hệ thống đang vận hành:
1. **Bẫy dữ liệu Seed/Test (`Administrator` trap):** Luôn kiểm tra trường `owner` và `created_at`. Nếu một loạt record tạo cùng phút bởi `Administrator` kèm file `.txt`, đó là test script của lập trình viên, tuyệt đối không được nhầm là giao dịch thật của người dùng.
2. **Kênh đầu vào gốc (Input Stream Grounding):** Đọc bảng dữ liệu cuối (`Purchase Order`) sẽ không thấy được vấn đề bằng việc đọc bảng tin nhắn thô (`chat_message_logs`). Tin nhắn của nhân viên Bếp mới là nơi phản ánh chính xác nhất tên gọi thực tế và chu kỳ sinh đơn mỗi ca.
3. **Ý nghĩa của Bằng Chứng Âm:** Một hệ thống có đầy đủ tính năng nhưng toàn bộ đơn hàng đều dừng ở `payment_approved = 0` và `paid_amount = 0` không có nghĩa là tính năng bị lỗi, mà là **quy trình thực tế bị đứt gãy ở bước chuyển giao con người** (nhân viên quên bấm nút nhận hàng $\rightarrow$ đơn kẹt ở `Draft` $\rightarrow$ màn hình của sếp bị trống $\rightarrow$ quay lại gửi email thủ công).

---

## 7. Related Links & Notes
- [Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core](ngonngon-catering-domain-and-architecture-handbook.md)
- [Receipt bền vững: retry an toàn không đồng nghĩa exactly-once](../architecture/durable-tool-receipts-and-delivery-ambiguity.md)

