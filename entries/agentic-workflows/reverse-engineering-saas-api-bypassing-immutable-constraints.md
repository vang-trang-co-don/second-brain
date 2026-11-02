# Reverse Engineering SaaS Internal API & Bypassing Immutable Constraints

> **One-liner:** Thay vì dùng Agent click UI mò mẫm (chậm và dễ vỡ), trích xuất token từ session trình duyệt sống để dịch ngược REST API nội bộ, từ đó vượt qua các rào cản bất biến (immutable IAM email & giới hạn license SaaS).

---

## Metadata
- **Source:** Production Case Study (iPOS HRM Data Synchronization)
- **Author/Creator:** Pair-programming Session (Cao Quốc Dũng & Agent)
- **Captured Date:** 2026-11-02
- **Tags:** `#agentic-workflow` `#reverse-engineering` `#api-sniffing` `#saas-constraints` `#session-hijacking` `#automation`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea (Ý tưởng cốt lõi)

Khi cần đồng bộ dữ liệu vào một hệ thống SaaS kín (iPOS HRM) không có Open API công khai:
- Web không cho phép import Excel để ghi đè cập nhật nhân viên cũ (chỉ cho thêm mới).
- Trường `Email` trên giao diện bị khóa cứng (`readonly`) vì gắn chặt với tài khoản định danh iPOS ID trong hệ thống IAM.
- Giới hạn gói dịch vụ SaaS (License Limit): Gói HR30 chỉ cho phép tối đa 30 nhân sự hoạt động; chi nhánh đã có 26 người, nếu import thêm 11 người mới sẽ bị chặn lỗi `402 Payment Required (LIMIT_EMPLOYEE_LICENSE)`.

**Sai lầm phổ biến:** Cho AI Agent dùng Playwright click mò mẫm từng form trên DOM. Cách này cực kỳ chậm, dễ vướng modal quảng cáo/popup ngẫu nhiên, strict mode locator collision và không giải quyết được các ô bị khóa readonly.

**Giải pháp đột phá:** 
1. Trích xuất Bearer Token trực tiếp từ SQLite cookie của trình duyệt đang mở mà không làm gián đoạn phiên người dùng.
2. Dịch ngược (reverse-engineer) các file JavaScript chunk của SPA để tìm danh mục toàn bộ 31 API endpoint nội bộ.
3. Thiết kế chiến lược tuần tự: Giải phóng hạn ngạch license $\rightarrow$ Phân nhánh xử lý dị biệt $\rightarrow$ Import hàng loạt $\rightarrow$ Chuẩn hóa metadata qua API cập nhật thông tin.

---

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

### 2.1. Non-blocking Session Hijacking từ Trình duyệt Đang Mở
- Khi trình duyệt (Firefox Snap/Chrome) đang chạy, file cookie bị khóa (`.parentlock`, lock file).
- **Giải pháp:** Copy nóng `cookies.sqlite` sang `/tmp` để truy vấn:
  ```bash
  cp ~/snap/firefox/common/.mozilla/firefox/<profile>/cookies.sqlite /tmp/cookies.sqlite
  ```
- Giải mã token JWT từ cookie để lấy `Bearer token`, `company_id`, `employee_id` và thời hạn `exp`.

### 2.2. Dịch ngược Client Bundle (SPA Asset Sniffing)
- Từ 1 network request ban đầu, xác định base URL và các file asset JS.
- Quét các regex template string trong bundle JS (`newVersionNotice-*.js`, `detail-*.js`) để bóc tách toàn bộ API router:
  - `GET employee/list` & `GET employee/detail/{id}`
  - `POST employee/check-import-employee` (Dry-run validator trước khi import thật)
  - `POST employee/import-employee` (Import Excel vào database)
  - `PUT employee/manager/update-profile/{id}` (Cập nhật họ tên, SĐT, ngày sinh, giới tính)
  - `PUT employee/manager/update-work/{id}` (Cập nhật mã NV, phòng ban, chức vụ)
  - `PUT employee/manager/resign/{id}` (Thôi việc nhân viên)
  - `PUT employee/manager/cancel-resign-in-past/{id}` (Khôi phục nhân viên đã thôi việc)

### 2.3. Vượt rào cản Immutable Email & Giới hạn License SaaS (HR30)
1. **Lách giới hạn License Quota:** 
   - Quota tối đa: 30 người. Đang active: 26 người. Cần thêm: 11 người $\rightarrow$ Tổng 37 > 30 (Lỗi 402).
   - **Xử lý:** Gọi API `resignByManager` cho 11 mã cũ trước để hạ số lượng active xuống 16 người $\rightarrow$ Import 11 người mới an toàn trong quota (16 + 11 = 27 < 30).
2. **Lách lỗi "Mã nhân viên đã tồn tại":**
   - Mã nhân viên cũ dù đã nghỉ việc vẫn được lưu trong DB lịch sử.
   - **Xử lý:** Cấp mã mới với hậu tố phân biệt (`IPOS-4` $\rightarrow$ `IPOS-4A`) đảm bảo tính duy nhất và người quản lý vẫn nhận biết được danh tính.
3. **Phát hiện dị biệt bằng Dry-run API:**
   - Khi đẩy qua `check-import-employee`, phát hiện `IPOS-13` bị báo lỗi trùng email vì `DuongMinhTruong` và `duongminhtruong` là một.
   - **Xử lý linh hoạt:** Gọi API `cancelResignInPastByManager` khôi phục `IPOS-13` nguyên bản, chỉ import 10 người thực sự đổi email.
4. **Bypass cơ chế gửi thư mời:**
   - Dùng trực tiếp endpoint `import-employee` thay vì luồng "Mời nhân viên" (`inviteEmployee`), giúp tạo tài khoản trực tiếp mà nhân sự không cần qua bước xác nhận phức tạp.
5. **Đồng bộ hậu kỳ 2 chiều:**
   - Chạy script gọi `updateProfileByManager` chuẩn hóa lại Họ tên, SĐT và Ngày sinh đúng chuẩn tiếng Việt.
   - Ghi ngược các mã có hậu tố `A` vào file Excel nội bộ (`form chuan.xlsx`) để làm Single Source of Truth (SSOT).

---

## 3. Actionable Application (Cách áp dụng thực tế vào dự án)

### Khi nào nên dùng:
- Khi phải làm việc với các hệ thống SaaS đóng (HRM, CRM, ERP, POS) không mở Open API cho khách hàng vừa và nhỏ.
- Khi web UI cấm chỉnh sửa trường nhạy cảm hoặc không có tính năng cập nhật hàng loạt.
- Khi cần tự động hóa một tác vụ mà nếu click UI sẽ mất hàng giờ và rủi ro sai sót cao.

### Quy tắc triển khai chuẩn cho Agent (Agentic Golden Rule):
1. **API First, DOM Last:** Đừng vội viết script điều khiển DOM (click, type, wait selector). Hãy mở trang 1 lần bằng Playwright để bắt network token và cấu trúc request.
2. **Deterministic over Flaky:** Gọi REST API trực tiếp bằng HTTP client (requests, fetch, urllib) đạt độ tin cậy 100%, phản hồi mili-giây, không phụ thuộc vào layout CSS hay modal popup ngẫu nhiên.
3. **Dry-run Trước Khi Mutate:** Luôn tìm xem hệ thống có endpoint validate (`check-import`, preview) để kiểm thử dữ liệu trước khi commit vào database thật.

---

## 4. Related Links & Notes
- Liên kết chéo: [Kiến Trúc Kỹ Thuật & Agentic Workflow Game tibo.dog](poteto-tibo-dog-engineering.md)
