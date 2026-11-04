# Quản Lý Vòng Đời Tạm Tính POS Nhà Hàng: Nhận Diện Trực Quan & Cơ Chế Bắt Lệch Bill Thực Địa (Stale Pre-Bill Drift)

> **One-liner:** Giải pháp theo dõi trạng thái Phiếu kiểm đồ tạm tính (Pre-bill Check) trên quầy POS offline-first, tự động phát hiện lệch bill khi khách gọi thêm món sau tạm tính và bảo toàn trạng thái qua giao ca.

---

## Metadata
- **Source:** Production POS F&B (`nemnem-admin`, `frontend/src/features/pos/`)
- **Author/Creator:** Công ty Cổ phần Nêm & Nếm / Engineering Team
- **Captured Date:** 2026-11-04
- **Tags:** `#fnb-restaurant` `#pos-lifecycle` `#pre-bill` `#stale-detection` `#offline-first` `#indexeddb-zustand` `#shift-handover` `#ui-indicator`
- **Category:** `architecture`

---

## 1. The Core Idea (Sự Thật Thực Địa & Vấn Đề Cốt Lõi)

Trong vận hành nhà hàng F&B ăn tại bàn (Dine-in):
1. **Khác biệt cốt lõi giữa Tạm tính (Pre-bill) và Hoá đơn (Invoice):**
   - **Phiếu tạm tính (Pre-bill / Check):** Không phải chứng từ kế toán. Đây là bảng kê chi tiết các món đã gọi để phục vụ mang ra bàn cho khách kiểm tra trước khi thanh toán.
   - **Hoá đơn thanh toán (Settled Invoice):** Là chứng từ kết thúc giao dịch, trừ kho, ghi nhận doanh thu và kích hoạt xuất hoá đơn điện tử (HĐĐT KiotViet/TT78).
2. **Nỗi đau thực tế tại quán:**
   - **Giao ca & Quên thu tiền:** Khách đông, nhân viên đổi ca giữa chừng không biết bàn nào đã đưa phiếu tạm tính cho khách, bàn nào đang ăn bình thường. Hậu quả: in trùng bill, đưa phiếu lần 2 gây phiền hà hoặc quên thu tiền khi khách chuẩn bị về.
   - **Cái bẫy "Khách gọi thêm món sau khi cầm phiếu" (Stale Pre-bill Drift):** Sau khi phục vụ đưa phiếu tạm tính, khách ngồi lại nói chuyện và gọi thêm 1 lon bia, đĩa tráng miệng hoặc xin đổi món. Nếu hệ thống không có cơ chế cảnh báo, thu ngân chỉ nhìn số tiền trên tờ phiếu cũ khách cầm hoặc thu ngân mới vào ca bấm thanh toán theo số cũ, dẫn đến thất thoát tiền hoặc in hoá đơn thiếu món.

---

## 2. Key Mechanisms & Patterns (Cơ Chế Chi Tiết)

### A. Bộ Ba Trạng Thái Tạm Tính (Provisional Triad)
Trong mỗi `TableDraft`, lưu trữ 3 trường bắt buộc:
1. `provisionalPrintedAt: number` (Epoch timestamp lúc bấm Tạm tính gần nhất).
2. `provisionalPrintedTotal: number` (Số tiền `grandTotal` chính xác tại thời điểm xuất phiếu).
3. `provisionalPrintCount: number` (Số lần phiếu tạm tính đã được xuất).

### B. Thuật Toán Phát Hiện Lệch Bill Tự Động (Stale Drift Detection)
Một bàn được coi là **"Lệch tạm tính" (Stale / Drifted)** khi và chỉ khi:
$$\text{isProvisionalStale} = (\text{provisionalPrintedAt} > 0) \land \big(|\text{grandTotal} - \text{provisionalPrintedTotal}| \ge 100 \lor \text{unsentCount} > 0\big)$$

* **Tại sao ngưỡng $\ge 100$ đồng?** Tiền VND tính số nguyên, nhưng phòng ngừa sai số làm tròn số học (floating-point epsilon). Mọi thay đổi về giá, giảm giá, bật tắt phí phục vụ hoặc thêm/bớt món sẽ làm lệch trên 1.000đ và lập tức kích hoạt cảnh báo.
* **Tại sao kiểm tra `unsentCount > 0`?** Nếu nhân viên vừa gõ thêm 1 món vào giỏ nhưng chưa bấm "Báo bếp" hay chưa xác nhận, món đó đã nằm trong đơn và bill trên tay khách đã bị lỗi thời!

### C. Ngôn Ngữ Thị Giác Đa Điểm (Multi-Touchpoint Visual Semantics)
Không giấu trạng thái trong menu con. Hiển thị đồng bộ ở 3 tầm nhìn của thu ngân:
1. **Tầm nhìn vĩ mô — Sơ đồ bàn (`FloorPlanView`):**
   - Bàn đang ăn: Viền xanh nhạt (`border-primary bg-primary/5`).
   - Bàn đã tạm tính chuẩn: Viền tím indigo `border-purple-400 bg-purple-50/60 ring-1 ring-purple-400/30` + Badge `[📋 Đã tạm tính · 12:45]`.
   - Bàn bị lệch bill sau tạm tính: Viền hổ phách nổi bật `border-amber-500 bg-amber-50/70` + Badge `[⚠️ Đổi món sau tạm tính]`.
2. **Tầm nhìn điều hướng — Thanh chuyển nhanh (`QuickSwitchBar`):**
   - Đính tag gọn `[📋 TT]` cạnh số lượng món để thu ngân lướt mắt thấy ngay cả khi đang ở tab Thực đơn.
3. **Tầm nhìn thao tác chi tiết — Cột giỏ hàng (`CartPanel` & `CartFooter`):**
   - Header: Tag `Đã tạm tính` / `Lệch tạm tính`.
   - Footer: Banner thông báo thời gian in và số lần in.
   - Nút hành động: Tự đổi từ `Tạm tính` sang `In lại TT` với nền tím nổi bật.

---

## 3. Real-World Production Cases (Các Tình Huống Thực Tế)

1. **Khách xin hoá đơn kiểm đồ nhưng ngồi tiếp 45 phút:**  
   Thu ngân in tạm tính lúc 13:00. Bàn hiển thị badge tím `[Đã tạm tính · 13:00]`. 13:40 thu ngân mới vào ca nhìn vào sơ đồ bàn biết ngay bàn này đã xuất phiếu, chủ động hỏi bàn xem có cần thanh toán không mà không cần hỏi lại nhân viên ca trước.
2. **Khách gọi thêm nước ngọt sau khi xem bill:**  
   Lúc 13:05 khách gọi thêm 2 lon Coca (40.000đ). Ngay khi nhân viên thêm món vào giỏ, `isProvisionalStale` chuyển thành `true`. Sơ đồ bàn lập tức đổi sang viền cam hổ phách `[⚠️ Đổi món sau tạm tính]`. Khi khách gọi tính tiền, thu ngân biết chắc chắn phiếu trên bàn khách đã sai, bấm ngay `In lại TT` để in bản cập nhật mới nhất.
3. **Tách bàn hoặc Gộp bàn sau khi đã in tạm tính:**  
   Nếu bàn thực hiện chuyển món (partial transfer) sang bàn khác, tổng tiền bàn cũ giảm đi $\to$ tự động kích hoạt `isProvisionalStale` cảnh báo bill đã thay đổi.

---

## 4. Reconstructability Blueprint (Bản Vẽ Tái Dựng Độc Lập)

### A. Authoritative TypeScript Model & State Shape

```typescript
// Cấu trúc giỏ hàng theo bàn lưu trữ trong Zustand + IndexedDB
export interface CartLine {
  lineId: string;
  item_code: string;
  item_name: string;
  qty: number;
  sent_qty: number;
  rate: number;
  vat_rate: number;
  discount_percentage: number;
  note: string;
  is_takeaway?: boolean;
}

export interface TableDraft {
  tableKey: string;           // "Bàn 01" hoặc "__TAKEAWAY__"
  tableLabel: string;
  orderType: "Tại bàn" | "Mang về";
  guests: number;
  customer: string;
  customerName: string;
  lines: CartLine[];
  discount: { type: "percent" | "amount"; value: number };
  noService: boolean;
  remarks: string;
  openedAt: number;
  
  // === BỘ BA TẠM TÍNH (PROVISIONAL TRIAD) ===
  provisionalPrintedAt?: number;      // Epoch millis
  provisionalPrintedTotal?: number;   // Số tiền VND nguyên vẹn lúc in
  provisionalPrintCount?: number;     // Số lần in
}

export interface TableSummary {
  hasItems: boolean;
  totalQty: number;
  unsentCount: number;
  grandTotal: number;
  guests: number;
  openedAt: number;
  provisionalPrintedAt?: number;
  provisionalPrintedTotal?: number;
  isProvisionalStale?: boolean;
  provisionalPrintCount?: number;
}
```

### B. Thuật Toán Tính Toán Summary & Lệch Bill (Pure Function)

```typescript
export function computeTableSummary(
  draft: TableDraft,
  computedTotals: { grandTotal: number; totalQty: number; unsentCount: number }
): TableSummary {
  if (!draft || draft.lines.length === 0) {
    return {
      hasItems: false,
      totalQty: 0,
      unsentCount: 0,
      grandTotal: 0,
      guests: draft?.guests || 2,
      openedAt: draft?.openedAt || Date.now(),
    };
  }

  const isProvisional = Boolean(draft.provisionalPrintedAt);
  // Tiêu chí lệch bill: lệch tiền >= 100đ HOẶC có món chưa gửi bếp
  const isProvisionalStale = Boolean(
    isProvisional &&
      (Math.abs(computedTotals.grandTotal - (draft.provisionalPrintedTotal || 0)) >= 100 ||
        computedTotals.unsentCount > 0)
  );

  return {
    hasItems: true,
    totalQty: computedTotals.totalQty,
    unsentCount: computedTotals.unsentCount,
    grandTotal: computedTotals.grandTotal,
    guests: draft.guests,
    openedAt: draft.openedAt,
    provisionalPrintedAt: draft.provisionalPrintedAt,
    provisionalPrintedTotal: draft.provisionalPrintedTotal,
    isProvisionalStale,
    provisionalPrintCount: draft.provisionalPrintCount,
  };
}
```

### C. State Machine & Vòng Đời

```
 [ Bàn Trống ]
      │ (Chọn bàn, thêm món)
      ▼
 [ Đang Dùng Bữa ] ◄────────────────────────────────────┐
      │                                                 │
      │ (Bấm "Tạm tính" -> In phiếu thành công)          │
      ▼                                                 │
 [ Đã Xuất Tạm Tính ] ──(Khách gọi thêm món / Sửa giá)──┘
      │               (isProvisionalStale = true)
      │
      ├──(Bấm "In lại TT") ──> Cập nhật provisionalPrintedTotal & In lại
      │
      └──(Khách thanh toán thành công OR Huỷ bàn)
            │
            ▼
       [ Bàn Trống ] (Reset sạch toàn bộ Draft)
```

---

## 5. Lessons Encoded In Structure (Quy Tắc Lint & Đúc Kết)

1. **Quy tắc Type Contract Discipline (`tsc -b` tự động):**  
   Khi thêm props vào component lớn, không bao giờ giả định các hook con re-export lại prop của component cha (như lỗi truy cập nhầm `checkout.currentTotals`). Đưa `tsc -b frontend` vào bộ test runner tự động (`check_pos_ui.py`) để mọi lỗi truy cập thuộc tính không tồn tại đều chặn đứng lệnh build / deploy ngay lập tức.
2. **Quy tắc Đồng bộ Cache Busting Version:**  
   Mọi thay đổi frontend bắt buộc đi kèm kiểm tra đồng nhất số version `?v=XXX` trong file shell HTML duy nhất giữa file JS và file CSS.

---

## 6. Related Links & Notes
- [Vận Hành Mua Hàng & Thanh Toán Nhà Hàng F&B P2P](fnb-restaurant-p2p-procurement-and-settlement.md)
- [Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core Ngon Ngon Catering](ngonngon-catering-domain-and-architecture-handbook.md)
