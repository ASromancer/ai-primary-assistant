# Design: Personalization (login + database)

Date: 2026-10-06. Approved by the user in chat.

## Decisions
- Login: Google via `st.login()` / `st.user` (flat `[auth]` config in Secrets). Guest mode (not logged in) keeps today's behaviour, with data held in the session only.
- Database: the user's **personal** Supabase project (the user creates it and runs `sql/schema.sql`). The app connects through `st.connection("sql")` (SQLAlchemy + psycopg2) using the **Session pooler** string (IPv4).
- Security: tables in `public` with an `tl_` prefix, RLS enabled with no policies, privileges revoked from `anon` and `authenticated` → the public Supabase API cannot read anything. Only `kho.py` touches the DB; every function takes `email` and every query filters by owner. Student names are never sent to the AI.
- If `[auth]` or `[connections.sql]` is missing → personalization is hidden; the app does not error.

## Data
`tl_giao_vien`(email PK, ten, truong, lop_mac_dinh, mon_mac_dinh, bo_sach_mac_dinh, yeu_cau_mau)
`tl_phieu`(id, email, mon, lop, chu_de, du_lieu JSON text, gan_sao, tao_luc, sua_luc)
`tl_lop`(id, email, ten_lop, tao_luc) · `tl_hoc_sinh`(id, lop_id → cascade, stt, ten, nhom)
`tl_lan_cham`(id, email, lop_id → set null, mon, chu_de, loai_phieu, tao_luc) · `tl_ket_qua`(id, lan_cham_id → cascade, ten, diem, muc_tt27, nhan_xet, chi_tiet JSON text)

## Features
1. Profile: name/school saved automatically; class/subject/textbook/extra requirements of the last worksheet become the defaults for the next one.
2. Auto-save: worksheets and class rosters are saved when their content changes (fingerprint comparison), triggered in `app.py` inside `try/finally` around `pg.run()`.
3. 📚 Library page: accent-insensitive search, filter by subject/class/starred, open, duplicate, delete (with confirmation).
4. My class: multiple classes (pick/create/delete).
5. Grading: "Save to class record".
6. 📈 Progress page: student × grading-session matrix of TT27 levels, a per-student chart, an AI-suggested end-of-term report-card comment (rule for the suggested level: most frequent level, ties broken by the most recent), Excel export.
7. Home page: worksheet count, papers graded, classes/students, estimated hours saved (40 min/worksheet, 3 min/paper).

## Limitations
- Progress is tracked by the student's name within a class (renaming a student breaks their history).
- Free-tier Supabase pauses a project after 7 days of inactivity.

## Testing
`kho.py` tested on SQLite (fast) + a full run on Postgres 17 (Docker) against the real `sql/schema.sql`; a teacher-to-teacher data isolation test; logged-in UI tests with mocked `state.email`/`state.db`.
