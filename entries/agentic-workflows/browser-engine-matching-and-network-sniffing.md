# Browser Engine Matching, In-Flight Network Sniffing & Zalo Session Guards

> **One-liner:** Khắc phục triệt để lỗi đăng nhập giả (Engine Mismatch khi hijack cookie Google), vượt qua sự bất ổn định của DOM SPA bằng cơ chế bắt tệp nhị phân trên đường truyền (In-Flight Sniffing), và phòng chống vòng lặp spam request đăng nhập Zalo qua Login Guard.

---

## Metadata
- **Source:** Production Pair-Programming Session (Ngon Ngon Catering Admin & Quotation Ingestion)
- **Author/Creator:** Cao Quốc Dũng & AI Assistant
- **Captured Date:** 2026-11-03
- **Tags:** `#agentic-workflow` `#session-hijacking` `#browser-fingerprint` `#network-sniffing` `#playwright` `#spa-flakiness` `#session-guard`
- **Category:** `agentic-workflows`

---

## 1. The Core Idea (Ý Tưởng Cốt Lõi)

Khi xây dựng các Agent tự động hóa tương tác với các ứng dụng Web phức tạp (Google Workspace/Gmail, Zalo Web), kỹ sư rất dễ mắc phải 2 cái bẫy kinh điển:
1. **Bẫy lệch Engine khi trích xuất Cookie (Engine Mismatch):** Trích xuất `cookies.sqlite` từ profile Firefox thật nhưng lại nạp vào Chromium của Playwright $\rightarrow$ Google nhận diện chữ ký TLS/User-Agent sai lệch, lập tức đá văng session sang trang `accountchooser` và báo `Signed out`.
2. **Bẫy mò mẫm DOM trên các Single Page App (SPA DOM Flakiness):** Bắt Agent dùng `click()`, `getByText()` để tìm và tải file đính kèm trên giao diện Gmail $\rightarrow$ Liên tục dính lỗi `TimeoutError: 30000ms exceeded`, DOM động bị render lại (`element was detached from DOM`), và popup tải file của trình duyệt bị chặn.

**Giải pháp đột phá:**
* Khớp đúng Engine trình duyệt (`firefox.launch`) khi nạp cookie Firefox.
* Kết hợp **Giao diện trực tiếp (`headless: false` trên `DISPLAY=:0`)** với **Network Sniffer chạy ngầm**: Người dùng thao tác tự nhiên trên màn hình, còn Agent chặn bắt trực tiếp dữ liệu binary (PDF) ngay trên luồng truyền tải HTTP (`page.on('response')`) dựa vào `Content-Disposition` và MIME type, không cần đụng vào bất kỳ nút bấm UI nào.
* Áp dụng **Login Guard (Exit Code 78)** khi khởi tạo session Zalo qua systemd để chặn triệt để vòng lặp spam request khóa tài khoản.

*(Lưu ý về in ấn BEO A4: Quy chuẩn khóa trần trang in A4 và ngân sách chiều dọc được quản lý tập trung tại [Ngon Ngon Catering Handbook](../architecture/ngonngon-catering-domain-and-architecture-handbook.md).)*

---

## 2. Key Mechanisms & Patterns (Chi Tiết Kỹ Thuật Cốt Lõi)

### 2.1. Đồng Bộ Hóa Engine Khi Tái Sử Dụng Cookie Phiên (Engine Matching)
- Trình duyệt hiện đại (Firefox, Chrome) lưu cookie cùng với chữ ký TLS và Client Hints gắn liền với nhân trình duyệt.
- Nếu trích xuất cookie từ `/snap/firefox/common/.mozilla/firefox/<profile>/cookies.sqlite`:
  - **Lỗi:** Inject vào `playwright.chromium` $\rightarrow$ Google Account phát hiện Fingerprint bất thường $\rightarrow$ Buộc đăng nhập lại.
  - **Khắc phục:** Bắt buộc inject vào `playwright.firefox`. Phiên đăng nhập `admin@ngonngoncatering.com.vn` hợp lệ ngay lập tức, vào thẳng Inbox mà không cần xác thực 2 bước hay mật khẩu.
- **Xử lý Expiry Timestamp:** Cookie của Firefox lưu thời hạn dạng microsecond ($> 10^{10}$), Playwright yêu cầu epoch second $\rightarrow$ Bắt buộc chuẩn hóa `expiry = Math.floor(expiry / 1000)` trước khi nạp.

### 2.2. Kỹ Thuật Headed Sniffing: Bắt Tệp Trên Đường Truyền (In-Flight Sniffing)
Thay vì bắt Agent vật lộn với các element selector phức tạp, modal preview hay trigger nút "Download":
1. Mở cửa sổ trình duyệt thật trên X11/Wayland:
   ```javascript
   const browser = await firefox.launch({ headless: false, args: ["--start-maximized"] });
   ```
2. Gắn listener thụ động giám sát toàn bộ responses:
   ```javascript
   page.on("response", async (res) => {
     const contentType = res.headers()["content-type"] || "";
     const contentDisp = res.headers()["content-disposition"] || "";

     if (contentType.includes("pdf") || contentDisp.includes(".pdf") || res.url().includes("view=att")) {
       const buffer = await res.body();
       const filename = decodeURIComponent(contentDisp.match(/filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?/i)?.[1] || `file_${Date.now()}.pdf`);
       fs.writeFileSync(`/tmp/${filename}`, buffer);
       console.log(`✓ Đã bắt tệp thành công: ${filename} (${buffer.length} bytes)`);
     }
   });
   ```
3. Người dùng hoặc Agent chỉ cần mở luồng email hoặc click xem trước $\rightarrow$ Network request gửi URL đính kèm từ CDN Google (`mail-attachment.googleusercontent.com`) $\rightarrow$ Listener chặn và lưu binary hoàn chỉnh về đĩa cứng với tỷ lệ thành công 100%.

### 2.3. Đăng Nhập Zalo Web (zca-js): Terminal Tương Tác vs Systemd
- **Bẫy:** Chạy script tạo mã QR qua `systemd` chạy ngầm. Mã QR sinh ra lưu vào `/run/...`, không ai thấy để quét; sau 90s QR hết hạn dẫn đến vòng lặp xin cấp mã mới liên tục $\rightarrow$ Zalo khóa tài khoản vì spam request.
- **Quy tắc an toàn:**
  - Không bao giờ chạy đăng nhập Zalo lần đầu qua service ngầm.
  - Phải có **Login Guard (Exit Code 78)**: Khi QR hết hạn, thoát ngay lập tức và cấu hình `RestartPreventExitStatus=78` để chặn systemd tự động khởi động lại.
  - Chỉ quét QR tương tác qua terminal 1 lần duy nhất khi người quản lý đang cầm điện thoại sẵn sàng, lưu phiên vào `session.json` (`0600`) rồi mới bàn giao cho systemd chạy vĩnh viễn.

---

## 3. Actionable Application (Cách Áp Dụng Thực Tế)

### Script Mẫu: Headed Playwright Tự Động Bắt PDF Từ Gmail
```javascript
import { firefox } from "playwright";
import fs from "node:fs";

// 1. Nạp cookies trích xuất từ Firefox profile
const cookies = JSON.parse(fs.readFileSync("/tmp/google_cookies.json", "utf8"));

// 2. Bật Firefox GUI trên DISPLAY hiện tại
const browser = await firefox.launch({ headless: false });
const context = await browser.newContext({ viewport: null });
await context.addCookies(cookies);
const page = await context.newPage();

// 3. Bắt file PDF nhị phân trực tiếp trên đường truyền
page.on("response", async (res) => {
  const cd = res.headers()["content-disposition"] || "";
  const ct = res.headers()["content-type"] || "";
  if (ct.includes("pdf") || cd.includes(".pdf")) {
    const buffer = await res.body();
    const filename = cd.match(/filename=['"]?([^;\r\n"']*)['"]?/)?.[1] || "download.pdf";
    fs.writeFileSync(`/tmp/${filename}`, buffer);
    console.log(`[Captured] ${filename} - ${buffer.length} bytes`);
  }
});

await page.goto("https://mail.google.com/mail/u/1/#inbox");
```

---

## 4. Related Links & Notes
- Liên kết chéo: [Reverse Engineering SaaS Internal API & Bypassing Immutable Constraints](reverse-engineering-saas-api-bypassing-immutable-constraints.md)
- Liên kết kiến trúc: [Ngon Ngon Catering: Cẩm Nang Nghiệp Vụ Vận Hành Thực Địa & Kiến Trúc Core (Zero-Frappe)](../architecture/ngonngon-catering-domain-and-architecture-handbook.md)
