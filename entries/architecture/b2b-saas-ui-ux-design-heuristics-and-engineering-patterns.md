# Triết Lý Thiết Kế & Công Thức Kỹ Thuật UI/UX B2B SaaS Tốc Độ Cao (Linear, Base.vn, Raycast, Plane)

> **One-liner:** Bộ cẩm nang thực chiến chắt lọc các nguyên lý tâm lý học nhận thức, kiến trúc phân tầng UI/UX (Table, Drawer, Shortcuts) và stack kỹ thuật "ăn ngay" (Local-first, Optimistic UI, Shadcn/Tailwind) giúp B2B SaaS đạt trải nghiệm mượt mà, không gián đoạn ngữ cảnh và triệt tiêu tải nhận thức của người dùng.

---

## Metadata
- **Source:** Nghiên cứu đối chuẩn thực tế: Base.vn, Linear.app, Raycast, Plane.so, Twenty, Refactoring UI (Adam Wathan & Steve Schoger).
- **Author/Creator:** dungcq x Claude (Antigravity pair-programming session)
- **Captured Date:** 2026-11-05
- **Tags:** `#ui-ux` `#b2b-saas` `#design-systems` `#frontend-architecture` `#optimistic-ui` `#local-first` `#shadcn-ui` `#refactoring-ui`
- **Category:** `architecture`

---

## 1. The Core Idea (Sự Thật Thực Địa & Vấn Đề Cốt Lõi)

### Vấn đề thực tế vs Giả định sách vở
- **Giả định sai lầm:** Dev thường nghĩ giao diện "đẹp và xịn" là phải có màu sắc bắt mắt, hiệu ứng animation phức tạp, hình minh họa 3D hoặc nhiều biểu đồ đồ sộ.
- **Sự thật thực địa trong B2B SaaS:** Người dùng phần mềm doanh nghiệp mở app lên trong giờ làm việc với áp lực cao; mục tiêu duy nhất của họ là **hoàn thành tác vụ nhanh nhất để đi về**. Họ không vào để "thưởng thức mỹ thuật".
- **Định nghĩa của sự "Sướng" (Delight):** Không phải là sự hào nhoáng, mà là **sự vắng mặt của ma sát (Frictionless)**. Ứng dụng phản hồi dưới ngưỡng nhận thức của não bộ (<100ms), không làm gián đoạn dòng suy nghĩ (unbroken flow), không làm mất ngữ cảnh đang làm việc và triệt tiêu cảm giác hoang mang mù mờ về dữ liệu.

### Bất biến cốt lõi (Domain Invariants)
1. **Zero Full-page Reload for In-place Actions:** Mọi thao tác duyệt, sửa, xóa, gắn nhãn, chuyển trạng thái tuyệt đối không được kích hoạt tải lại toàn trang (F5/full reload).
2. **Context Preservation (Bảo toàn ngữ cảnh):** Khi người dùng đang ở vị trí dòng $N$ trong một bảng dữ liệu 500 dòng, việc xem chi tiết, chỉnh sửa hoặc comment không được phép làm cuộn trang về đầu hay làm mất bộ lọc tìm kiếm hiện tại.
3. **Psychological State Determinism (Xác định trạng thái tâm lý):** Mọi hành động gửi yêu cầu (request, đơn từ, thanh toán) bắt buộc phải có vết tích kiểm toán (Audit Trail) hiển thị tức thì: Ai đang giữ? Bước tiếp theo là gì? Đã duyệt lúc mấy giờ? Không bao giờ để dữ liệu rơi vào trạng thái "im lặng vô định".
4. **Universal Escape Hatch:** Bất kỳ cửa sổ nổi (Modal, Drawer, Dropdown, Command Menu) nào mở ra được thì bắt buộc phải đóng được bằng phím `Esc` và click ra vùng ngoài backdrop.

---

## 2. Key Mechanisms & Patterns (4 Tầng Ngầm Tạo Trải Nghiệm "Siêu Đã")

```
┌─────────────────────────────────────────────────────────────┐
│ Tầng 4: Micro-Copywriting & Empty States (Giao tiếp người)   │
├─────────────────────────────────────────────────────────────┤
│ Tầng 3: Keyboard Ergonomics (Cmd+K, Esc, J/K, Shortcuts)     │
├─────────────────────────────────────────────────────────────┤
│ Tầng 2: Data Density & Table Layout (Right-align numbers)   │
├─────────────────────────────────────────────────────────────┤
│ Tầng 1: Tâm lý học nhận thức (Doherty <100ms, Progressive)  │
└─────────────────────────────────────────────────────────────┘
```

### Tầng 1: Tâm lý học hành vi & Giảm tải nhận thức
1. **Định luật Doherty (Doherty Threshold - Ngưỡng 400ms / 100ms):**
   - Phản hồi > 400ms: Dòng suy nghĩ bị đứt gãy, não bắt đầu chú ý đến việc "máy tính đang tải".
   - Phản hồi < 100ms: Não cảm nhận đây là phản ứng vật lý tự nhiên (như bấm công tắc đèn bật sáng ngay).
   - *Kỹ thuật đạt được:* Dùng client-side caching (TanStack Query/SWR) kết hợp **Optimistic UI** (cập nhật state giao diện ngay lập tức 0ms, gửi HTTP request chạy ngầm dưới nền).
2. **Tiết lộ lũy tiến (Progressive Disclosure):**
   - Loại bỏ ác mộng form 40 ô nhập liệu kiểu ERP cổ điển.
   - Mặc định chỉ hiển thị 20% trường dữ liệu tối cần thiết (Title, Amount, Due Date). 80% trường mở rộng chỉ xuất hiện động (dynamic disclosure) khi người dùng chọn điều kiện liên quan hoặc bấm "Thêm chi tiết".
3. **Audit Trail bất biến (Bí quyết Base Request):**
   - Mỗi record nghiệp vụ gắn liền với một danh sách sự kiện tuyến tính (`timeline events`): Thời gian thực, avatar người thao tác, hành động cụ thể và ghi chú đính kèm.

### Tầng 2: Data Density & Chuẩn mực Thiết kế Bảng (Data Table)
Chiếm 80% thời gian tương tác trong B2B SaaS:
- **Căn lề dữ liệu theo quy tắc vàng:**
  - **Chữ (Text, Name, Description):** Căn lề TRÁI (`text-left`) để mắt quét tự nhiên từ trái sang phải.
  - **Số (Currency, Quantity, Date, Percentage):** BẮT BUỘC căn lề PHẢI (`text-right`) kèm thuộc tính `font-variant-numeric: tabular-nums` (font đơn khoảng cách cho chữ số). Các hàng đơn vị, chục, trăm, nghìn thẳng tắp giúp mắt đối soát sai lệch trong 0.2 giây.
  - **Trạng thái, Badge, Checkbox, Avatar:** Căn GIỮA (`text-center`).
- **Ghim cấu trúc (Sticky Elements):**
  - Sticky Header: Cuộn xuống hàng trăm dòng tiêu đề cột vẫn cố định.
  - Sticky Left Column: Cột định danh (Mã đơn / Tên) đứng yên khi cuộn ngang bảng nhiều thuộc tính.
- **Floating Action Bar (Thao tác hàng loạt):**
  - Khi tick chọn $\ge 1$ checkbox, thanh công cụ trôi (floating bar) xuất hiện ở đáy màn hình với các hành động: `[Duyệt tất cả]`, `[Gán người phụ trách]`, `[Xuất Excel]`, `[Xóa]`.

### Tầng 3: Bàn phím & Tương tác phi gián đoạn (Keyboard & Drawer)
- **Side-over Sheet / Drawer (Thanh trượt bên phải):**
  - Thay vì nhảy trang URL mới (`/requests/123`) hoặc mở modal pop-up to đùng che khuất màn hình: Mở thanh trượt từ cạnh phải chiếm 35% - 50% chiều ngang màn hình. Người dùng vừa đọc chi tiết vừa nhìn thấy dòng dữ liệu phía sau.
- **Command Palette (`Cmd + K` / `Ctrl + K`):**
  - Cung cấp hộp lệnh tập trung cho phép tìm kiếm bất kỳ thực thể nào và thực thi hành động không cần rời tay khỏi bàn phím.
- **Hotkeys tiêu chuẩn:**
  - `J` / `K`: Di chuyển focus dòng xuống / lên trong bảng.
  - `Enter`: Mở chi tiết dòng đang focus.
  - `Cmd + Enter`: Submit form / Duyệt nhanh.
  - `Esc`: Đóng tầng nổi cao nhất hiện tại.

### Tầng 4: Micro-Copywriting & Trạng thái rỗng (Empty States)
- Không dùng từ ngữ kỹ thuật vô cảm (`Error 500`, `Invalid parameter`). Dùng câu văn chủ động, giải thích nguyên nhân và nút khắc phục:
  - *Ví dụ:* "Không thể lưu đề xuất do thiếu email người phê duyệt. [Bấm vào đây để bổ sung]".
- Empty State có tính hướng dẫn: Có icon nhẹ, 1 dòng mô tả giá trị và 1 nút Primary Action kích hoạt tạo mới ngay tại chỗ.

---

## 3. Real-World Production Cases (Các Tình Huống Thực Tế & Đối Sánh)

| Tiêu chí | Phần mềm truyền thống (Legacy ERP / MISA / Cũ) | B2B SaaS Hiện Đại (Base.vn, Linear, Plane) |
| :--- | :--- | :--- |
| **Xem chi tiết bản ghi** | Chuyển trang hoặc mở pop-up modal to đùng, mất vị trí cuộn trang cũ. | **Slide-over Drawer** bên phải, danh sách nền giữ nguyên vị trí cuộn 100%. |
| **Thao tác đổi trạng thái** | Bấm nút -> Hiện spinner xoay 1.5s -> Trang giật nảy F5 lại. | **Optimistic UI:** Checkbox tick xanh ngay lập tức (0ms), sync nền, lỗi thì rollback. |
| **Nhập liệu đề xuất** | Form 30-50 trường dài ngoằng, không biết ô nào bắt buộc. | **Progressive Disclosure:** 4 ô chính, chọn đến đâu bung thêm trường đến đó. |
| **Đối soát số liệu** | Số căn trái hoặc giữa, font co giãn, số lệch hàng không so sánh được. | Số **căn phải**, bật **tabular-nums**, các hàng thẳng tắp từ trên xuống dưới. |
| **Thao tác tìm kiếm** | Click chuột vào dropdown menu 3 cấp phức tạp. | Bấm **`Cmd + K`**, gõ tên dự án / nhân sự / action là ra ngay. |

---

## 4. Reconstructability Blueprint (Bản Vẽ Tái Dựng Thực Chiến Cho Dev)

### A. Authoritative Tech Stack ("Bộ đồ nghề ăn sẵn" chuẩn B2B SaaS)
Không tự viết lại bánh xe lịch sử bằng CSS thuần. Stack chuẩn mực nhất hiện nay:
1. **Core UI Kit:** `shadcn/ui` (xây trên nền Radix UI primitives + Tailwind CSS).
2. **Notification Toast:** `sonner` (xếp chồng mượt mà, có action undo, không che nội dung chính).
3. **Command Bar:** `cmdk` (nền tảng của thanh phím tắt `Cmd+K`).
4. **Slide Drawer:** `vaul` (thư viện drawer kéo trượt 60fps trên cả mobile lẫn desktop).
5. **Data Table:** `@tanstack/react-table` (xử lý virtualization, sticky, sorting, multi-select).
6. **Data Sync & Cache:** `@tanstack/react-query` (quản trị stale data, optimistic mutations).
7. **Prototyping Siêu Tốc:** `v0.dev` (prompt sinh layout chuẩn Shadcn UI chỉ trong 30 giây).

---

### B. Code Mẫu: Optimistic Mutation với Rollback & Toast Undo (React Query + Sonner)

Đây là mã nguồn mẫu giải quyết triệt để vấn đề "đợi server phản hồi mới đổi UI", mang lại cảm giác phản hồi 0ms:

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface Task {
  id: string;
  title: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

export function useApproveTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      const res = await fetch(`/api/tasks/${taskId}/approve`, { method: 'POST' });
      if (!res.ok) throw new Error('Duyệt thất bại trên máy chủ');
      return res.json();
    },

    // 1. KHI VỪA CLICK: Cập nhật UI ngay lập tức trong 0ms (Optimistic Update)
    onMutate: async (taskId: string) => {
      // Hủy mọi fetch đang chạy dở để tránh ghi đè dữ liệu cũ
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      // Lưu lại snapshot dữ liệu hiện tại để rollback nếu gặp lỗi
      const previousTasks = queryClient.getQueryData<Task[]>(['tasks']);

      // Ép giao diện chuyển sang trạng thái APPROVED ngay tức thì
      queryClient.setQueryData<Task[]>(['tasks'], (old = []) =>
        old.map((t) => (t.id === taskId ? { ...t, status: 'APPROVED' } : t))
      );

      // Hiển thị Toast thông báo tức thời kèm nút Hoàn tác (Undo)
      toast.success('Đã duyệt đề xuất thành công', {
        action: {
          label: 'Hoàn tác',
          onClick: () => {
            // Rollback thủ công nếu người dùng ấn Undo
            queryClient.setQueryData(['tasks'], previousTasks);
          },
        },
      });

      return { previousTasks };
    },

    // 2. NẾU LỖI SERVER: Tự động hoàn tác về trạng thái cũ và báo lỗi
    onError: (err, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks);
      }
      toast.error('Có lỗi xảy ra khi phê duyệt. Đã khôi phục trạng thái cũ.');
    },

    // 3. KHI XONG: Đồng bộ lại chuẩn xác với database
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
```

---

### C. Code Mẫu: Data Table Căn Chỉnh Chuẩn & Bật Tabular Numbers (Tailwind CSS)

```tsx
// Table cell cho tiền tệ & số liệu đối soát
export function CurrencyCell({ value }: { value: number }) {
  return (
    <td className="px-4 py-2.5 text-right font-mono font-medium text-slate-900 dark:text-slate-100 tabular-nums">
      {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value)}
    </td>
  );
}

// Table cell cho tên & mô tả
export function TextCell({ title, subtext }: { title: string; subtext?: string }) {
  return (
    <td className="px-4 py-2.5 text-left">
      <div className="font-medium text-slate-800 dark:text-slate-200">{title}</div>
      {subtext && <div className="text-xs text-slate-500">{subtext}</div>}
    </td>
  );
}
```

---

### D. Cheat-Sheet "5 Quy Tắc 3 Giây" Cho Dev Bận Rộn

Khi dev đang chạy deadline vài project cùng lúc, chỉ cần tuân thủ 5 gạch đầu dòng này trước khi commit code:

1. **Table:** Số căn PHẢI (`text-right` + `tabular-nums`), Chữ căn TRÁI (`text-left`), Status căn GIỮA (`text-center`).
2. **Chi tiết:** Mở Side-over Drawer từ bên phải đè lên, **cấm** chuyển trang làm mất vị trí cuộn của bảng.
3. **Phím bấm:** Mọi Modal, Drawer, Dropdown bắt buộc phải tắt được bằng phím `Esc` và click ra ngoài backdrop.
4. **Lưu dữ liệu:** Nút Save phải chuyển sang loading/disabled khi bấm, bắn Toast Sonner góc dưới khi xong; **không bao giờ** F5 reload toàn bộ trang web.
5. **Độ tương phản:** Phân chia các khối bằng viền mỏng màu nhạt (`border-slate-200` / `border-zinc-800`), tuyệt đối không kẻ viền đen đậm hoặc đổ màu nền sặc sỡ.

---

## 5. Related Links & Notes
- [Quản Lý Vòng Đời Tạm Tính POS Nhà Hàng: Visual Semantics Đa Điểm & Stale Drift](../architecture/fnb-pos-pre-bill-lifecycle-and-stale-drift-detection.md)
- [Vận Hành Mua Hàng & Thanh Toán F&B P2P: Đối Soát 3 Bên & Workflow Bất Biến](../architecture/fnb-restaurant-p2p-procurement-and-settlement.md)
