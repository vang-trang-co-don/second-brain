# [projects-root] tui có ý tưởng này, thằng second brain của mình hiện tại nó cũng hoạt động na...

- **Source:** `pi`
- **Session ID:** `01a1abc2-aada-76d2-8d1e-a8c56fcbbc7e`
- **Workspace:** `projects-root`
- **Timestamp:** `2026-11-05T12:50:24.090Z`
- **Raw Path:** `/home/dungcq/.pi/agent/sessions/--home-dungcq-projects--/2026-11-05T12-50-24-090Z_01a1abc2-aada-76d2-8d1e-a8c56fcbbc7e.jsonl`

## 1. User Goal
tui có ý tưởng này, thằng second brain của mình hiện tại nó cũng hoạt động na ná cái thư viện, mục lục. Nếu so sánh nó với cách pstack hoạt động thì ní thấy sao?

## 2. Key Decisions & Invariants
- **Ưu điểm:** Zero-click cho người dùng, AI luôn có sẵn kiến thức mà không cần gọi tool.
- **Zero Context Waste:** Chỉ kéo lát cắt cần thiết tại đúng thời điểm cần thiết.
- **Ghép (Graft) từ Candidate 1:** Bổ sung `triggers` trong `MANIFEST.json` để AI tự động nhận diện domain mà không cần con người nhắc.
