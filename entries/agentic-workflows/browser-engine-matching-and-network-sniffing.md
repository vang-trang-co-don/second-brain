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

### 2.3. Đăng Nhập Zalo Web (zca-js): Terminal Tương Tác, IP Datacenter & Paging Lịch Sử
- **Bẫy 1: Chạy đăng nhập ngầm qua systemd:** Mã QR sinh ra lưu vào `/run/...`, không ai thấy để quét; sau 90s QR hết hạn dẫn đến vòng lặp xin cấp mã mới liên tục $\rightarrow$ Zalo khóa tài khoản vì spam request.
  - *Quy tắc:* Không bao giờ chạy đăng nhập Zalo lần đầu qua service ngầm. Phải có **Login Guard (Exit Code 78)**: Khi QR hết hạn, thoát ngay lập tức và cấu hình `RestartPreventExitStatus=78` để chặn systemd tự động khởi động lại. Chỉ quét QR tương tác qua terminal 1 lần duy nhất khi người quản lý đang cầm điện thoại sẵn sàng, lưu phiên vào `session.json` (`0600`) rồi mới bàn giao cho systemd chạy vĩnh viễn.
- **Bẫy 2: Lỗi "Invalid login QR code" do IP Datacenter:** Khi chạy script sinh mã QR trực tiếp trên VPS (IP cloud/datacenter Vietnix, AWS, DigitalOcean), máy chủ Zalo vẫn trả về ảnh QR, nhưng khi điện thoại của người dùng quét vào sẽ lập tức bị chặn với thông báo: *"Invalid login QR code. Get a new code on your computer and try again"*.
  - *Khắc phục:* Bắt buộc sinh mã QR trên máy trạm cục bộ (IP mạng dân dụng sạch), dùng điện thoại quét và lưu `session.json` (`chmod 600`), sau đó SCP tệp phiên này lên VPS. Zalo chỉ kiểm tra ranh giới mạng lúc bắt tay sinh QR; một khi đã cấp phiên (`cookie` + `imei`), tiến trình WebSocket chạy trên VPS hoàn toàn bình thường.
- **Bẫy 3: Bỏ rơi tin nhắn điện thoại do cờ `selfListen: false`:** `zca-js` mặc định đặt `selfListen = false`. Khi Quản lý gửi tin nhắn từ điện thoại của mình (Outbound) hoặc nhắn vào mục "Cloud của tôi", thư viện âm thầm bỏ rơi tin nhắn (`if (messageObject.isSelf && !this.selfListen) continue`).
  - *Khắc phục:* Bắt buộc cấu hình `new Zalo({ logging: true, selfListen: true })` để không bỏ sót các giao dịch và lưu ý nội bộ do Quản lý gửi từ điện thoại.
- **Bẫy 4: Thao tác bốc session từ Firefox đang mở:** Cố gắng đọc `cookies.sqlite` hoặc LocalStorage của Firefox khi trình duyệt đang mở sẽ dính lỗi `sqlite3.OperationalError: database is locked`. Ngoài ra, Zalo Web có cơ chế phiên đơn (Single Web Session): nếu bot kết nối socket với session của trình duyệt, người dùng trên Firefox sẽ bị đá văng ra ngay lập tức với thông báo *"Tài khoản vừa đăng nhập ở một nơi khác"*.
- **Cơ chế kéo lịch sử tin nhắn ngược thời gian (Reverse Time Paging):**
  - Với tin nhắn trực tiếp 1-1: Gọi `api.listener.requestOldMessages(ThreadType.User)`. Máy chủ trả về mẻ tin nhắn gần nhất qua sự kiện `old_messages`. Tìm `msgId` nhỏ nhất (cũ nhất) trong mẻ đó làm `cursor` để gửi tiếp `requestOldMessages(ThreadType.User, cursor)` lùi dần về quá khứ từng trang cho đến khi hết tin.
  - Với nhóm chat tiệc: Gọi `api.getAllGroups()` lấy danh sách nhóm, sau đó lặp qua từng nhóm gọi `api.getGroupChatHistory(groupId, 50)` để kéo 50 tin nhắn và tệp đính kèm gần nhất.

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
