# Online Assignments – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Spec: `docs/superpowers/specs/2026-10-12-giao-bai-online-design.md`

**Goal:** Students take worksheets online by code, picking their name; mixed grading; live teacher dashboard.
**Tech Stack:** Streamlit 1.65 (`st.query_params`, `st.fragment(run_every)`, `st.dialog`), SQLAlchemy, segno (QR).

## Global Constraints
- The student page never renders `dap_an`, `huong_dan_cham`, or other students' results.
- Teacher functions in `kho.py` always filter by email; `hs_*` functions take no email and expose only what the student page needs.
- `sql/schema.sql` (fresh installs) and `sql/2026-10-12-giao-bai.sql` (upgrade) both create the 2 new tables; everything runs again without errors.

### Task 1: schema + kho (giao_bai_*, bai_lam_*, hs_*) — tests: create/code/fetch by code, submit + name lock, closed/past deadline/name not in roster → refused, isolation between teachers; SQLite + Postgres 17.
### Task 2: auto-grading `danh_gia` (so_cho_trong, dap_an_dung_sai, dap_an_noi_cot, tu_cham, hien_thi_tra_loi) — tests for each type, partial credit, unparseable → None (falls to AI).
### Task 3: `ai.cham_bai` accepts typed answers (`tra_loi`) instead of a photo — test with FakeClient: prompt contains the answers, code-graded results override the AI.
### Task 4: student page + routing in `app.py` — AppTest: `?ma=` without login → pick name → answer → submit → locked; wrong code/closed → message; answers absent from the page.
### Task 5: teacher page `trang/giao_bai.py` — AppTest: create assignment, dashboard, let a student retry, AI grading (patched), open in Grading.
### Task 6: mobile screenshots, README (+ SQL upgrade step), requirements `segno`, push.
