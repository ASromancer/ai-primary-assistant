# Design: Online assignments (students join by code, pick their name)

Date: 2026-10-12. Approved by the user in chat.

## Decisions
- Same Streamlit app. A URL with `?ma=XXXXXX` → student page only (`trang/lam_bai.py`), bypasses Google login, no sidebar/menu.
- Student authentication = pick a name from the class roster (with no class: type a name). A name that has submitted is locked (`unique(giao_bai_id, ten)`); the teacher can reopen it.
- Differentiation: the "by group" mode serves Xanh/Cam/Tím by the student's group in the roster; the "shared" mode gives everyone the shared sheet.
- Mixed grading: multiple choice / true-false / matching are graded by code immediately on submit (the student sees ✓/✗ but **not the correct answer**); fill-in-the-blank / essay + TT27 comments are graded by AI when the teacher presses the button (only the answers are sent, never the name).
- The assignment snapshots the worksheet at assignment time (`du_lieu` = BanLuu JSON). Answers stay on the server; the student page never renders `dap_an`/`huong_dan_cham`.
- Teacher page `📡 Giao bài`: create an assignment (worksheet, class, mode, optional deadline) → 6-character code + link + QR (segno) + full-screen view; live dashboard (fragment, 5 s); close/reopen; let a student retry; AI grading; "Open in Grading" per sheet (reuses the gradebook, error analysis, progress record).

## Data
`tl_giao_bai`(id, email → teacher, ma unique, lop_id → set null, tieu_de, du_lieu, che_do 'nhom'|'chung', dang_mo, han_nop text ISO UTC, tao_luc)
`tl_bai_lam`(id, giao_bai_id → cascade, ten, phieu, tra_loi JSON, ket_qua JSON, diem, muc_tt27, nhan_xet, trang_thai 'cho_ai'|'da_cham', nop_luc, unique(giao_bai_id, ten))
Teacher functions filter by email (JOIN tl_giao_bai); student functions `hs_*` receive only `ma`/`giao_bai_id` and check open/deadline/roster name on submit.

## Limitations
Picking a name does not prevent a student submitting on someone else's behalf; Community Cloud ~30–40 concurrent students; the app needs to be woken before class.
