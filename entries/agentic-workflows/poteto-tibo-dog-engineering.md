# Lauren (@poteto) - Kiến Trúc Kỹ Thuật & Agentic Workflow Game tibo.dog

> **One-liner:** Xây dựng web game 3D trong 4 ngày với ~1,150 PRs bằng cách kết hợp AI Agent, Zero-Allocation Lint rules, kiểm chứng hình thức TLA+, và Headless Bot Simulation.

---

## Metadata
- **Source:** [https://x.com/poteto/status/2117043478140276847](https://x.com/poteto/status/2117043478140276847)
- **Author/Creator:** Lauren (@poteto) — React Compiler Core Team, cựu Cursor, Meta, Netflix
- **Captured Date:** 2026-11-02
- **Tags:** `#agentic-workflow` `#performance` `#zero-alloc` `#tla-plus` `#game-dev` `#headless-playtesting` `#procedural-audio`
- **Category:** `agentic-workflows` / `performance`

---

## 1. The Core Idea (Ý tưởng cốt lõi)
Tác giả phát triển tựa game web 3D [tibo.dog](https://tibo.dog) như một dự án side project trong vòng 4 ngày với hơn 1.150 PRs được merge vào production. Thay vì chỉ dùng AI agent để gõ code đơn thuần, tác giả thiết lập một hệ thống **rào chắn cấu trúc (structural guardrails)** để AI không thể mắc lại sai lầm cũ, kết hợp cùng các kỹ thuật tối ưu hóa phần mềm cấp cao (Low GC, Formal verification, Live Synthesis).

---

## 2. Key Mechanisms & Patterns (Cơ chế & Kỹ thuật chi tiết)

### 2.1. Agent Guardrails: Biến lỗi thành Lint Rule thay vì sửa tay
* Khi phát hiện bất kỳ issue hay bad pattern nào do AI viết ra, tác giả **không nhắc đi nhắc lại trong prompt** mà yêu cầu Agent tạo ngay một **Custom Lint Rule** để cấm triệt để pattern đó.
* **Cấm viết comment code (No Comments Lint):** Code phải tự giải thích bằng tên biến/hàm tường minh hoặc bằng Unit Test. Nếu một đoạn code cần comment giải thích $\rightarrow$ Lint báo lỗi ngay lúc commit.

### 2.2. Zero-Allocation Hot Path (`.hot.ts`)
* **Vấn đề:** Trong JavaScript/TypeScript, việc khởi tạo object trong game loop 60 FPS sẽ khiến V8 Garbage Collector kích hoạt liên tục, gây ra hiện tượng khựng khung hình (stutter/frame drop).
* **Giải pháp:**
  - Mọi file code thực thi ở mỗi frame hoặc tick game loop đều mang hậu tố: `.hot.ts`.
  - Một lint rule đặc biệt cấm toàn bộ hành vi cấp phát bộ nhớ trong file `.hot.ts`: **cấm object literal (`{}`), cấm closures/arrow functions, cấm toán tử `new`**.
  - Kết quả: Game loop gần như không tạo rác (zero garbage), giữ vững 60 FPS ổn định ngay cả khi có 500 enemies trên điện thoại tầm trung.

### 2.3. Kiểm chứng hình thức State Machine bằng TLA+
* Sử dụng ngôn ngữ đặc tả toán học **TLA+** để mô hình hóa và model-check các máy trạng thái phức tạp trong game:
  - Tiến trình cốt truyện (Story state)
  - Phân cảnh cắt cảnh (Cutscenes)
  - Các hệ thống tương tác nội bộ game
* Tạo riêng các formal verification skills cho từng phân hệ lớn để đảm bảo không tồn tại race condition hay dead-lock.

### 2.4. Tính Tất Định (Determinism) & Chống Hack (Anti-Cheat)
* Tách rời hoàn toàn **Simulation logic** khỏi **Rendering (Three.js)**.
* Simulation hoàn toàn tất định (deterministic lockstep): Cùng một danh sách input sẽ tái hiện lại chính xác 100% ván chơi.
* Chống hack điểm số: Khi nộp High Score, client chỉ gửi chuỗi input log. Server chạy lại toàn bộ ván chơi trong vòng vài chục mili-giây để xác minh tính hợp lệ.

### 2.5. Zero-Asset Architecture (Code-Only Media)
* **Không file âm thanh (.mp3, .wav):** Toàn bộ nhạc nền và hiệu ứng âm thanh được tổng hợp thời gian thực (synthesized live) thông qua Web Audio API giả lập chip Game Boy (2 pulse voices, 1 wave voice, 1 noise) + 1 lớp synthwave. Nhạc được viết trực tiếp dạng ký âm văn bản trong code.
* **Nhạc chuyển biome mượt mà:** Giai điệu chuyển biến tự nhiên giữa các vùng đất mà không bị ngắt nhạc.
* **Không file ảnh tĩnh:** Mọi sprite pixel art đều là code được vẽ theo 1 bảng màu cố định và pack thành sprite atlas lúc build.
* **Dung lượng siêu nhẹ:** Build CI fail nếu bundle ban đầu vượt ngân sách. Toàn bộ game chỉ nặng **~124 KB (gzipped)**, chạy trực tiếp trong thẻ nhúng iframe 245px của bài post trên X.

### 2.6. Headless Bot Playtesting & Auto-Balancing
* Bot tự động chơi game ở chế độ không màn hình (headless) với tốc độ mô phỏng cực nhanh.
* Tự động cân bằng độ khó của từng cấp độ dựa trên tỷ lệ sống sót mục tiêu (target survival rates).

---

## 3. Actionable Application (Ứng dụng vào thực tế)

### Khi nào nên dùng:
1. **Dự án Real-time / Game Web:** Khi gặp vấn đề GC stutter hoặc giật lag trên mobile $\rightarrow$ Áp dụng quy ước file `.hot.ts` và ESLint rule chặn cấp phát.
2. **Quản lý AI Coding Agent:** Khi thấy agent liên tục lặp lại một lỗi quen thuộc $\rightarrow$ Yêu cầu agent viết lint rule/test chặn cứng ở CI thay vì mất công prompt sửa lại mỗi lần.
3. **Sản phẩm có logic nghiệp vụ phức tạp:** Tách rời lõi simulation/logic khỏi giao diện UI để có thể viết headless bot test toàn bộ kịch bản tự động.

---

## 4. Related Links & Notes
- Game demo: [https://tibo.dog](https://tibo.dog)
- Thư viện liên quan: TLA+, Three.js, ESLint AST rule
- Bài viết liên kết trong Second Brain:
  - `[Zero-Alloc Hotpath Performance](../performance/zero-alloc-hot-path.md)`
  - `[Headless Bot Simulation Pattern](../agentic-workflows/headless-simulation-playtesting.md)`
