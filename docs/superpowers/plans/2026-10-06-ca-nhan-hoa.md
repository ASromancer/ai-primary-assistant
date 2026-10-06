# Personalization – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Google login + a Supabase database to store teacher profiles, the worksheet library, classes, grading history and progress.
**Architecture:** `kho.py` (repository, the only module that queries the DB, every function takes `email`), `state.py` adds `co_auth/co_db/email/db/ca_nhan/tu_luu`, two new pages `trang/thu_vien.py` and `trang/tien_bo.py`.
**Tech Stack:** Streamlit ≥1.65 (`st.login`, `st.connection`), SQLAlchemy 2, psycopg2-binary, Authlib, Supabase Postgres 17.
**Spec:** `docs/superpowers/specs/2026-10-06-ca-nhan-hoa-design.md`

## Global Constraints
- Every SQL statement in `kho.py` filters by `email` (directly or via a JOIN to the owner's table). Never interpolate strings into SQL; always bind parameters.
- `sql/schema.sql` must run on both SQLite (the part above `-- POSTGRES ONLY`) and Postgres.
- Tests: `python test_app.py`; the Postgres test runs when `TEST_PG_URL` is set.

### Task 1: schema + kho.py
- [ ] Test: profile upsert; save/list/open/star/delete a worksheet; save/open/delete a class (replace the student list); save a grading session; progress; stats; **isolation**: B cannot open/delete/star A's worksheet, cannot overwrite A's class, cannot save grading into A's class.
- [ ] Implement `sql/schema.sql`, `kho.py`, add `id: str = ""` to `BanLuu`, `LopHoc`.
- [ ] Run SQLite + Postgres 17 (Docker) → PASS. Commit.

### Task 2: login, auto-save, profile, statistics
- [ ] `state`: `co_auth()`, `co_db()`, `email()`, `db()`, `ca_nhan()`, `tu_luu()`; `app.py`: login/logout block in the sidebar, load the profile once, `try/finally` auto-save; Worksheet page uses profile defaults; Home page statistics.
- [ ] Logged-in UI test (patch `state.email`, `state.db`, `state.co_db`). Commit.

### Task 3: Library · Task 4: multiple classes · Task 5: save grading + Progress + report-card comments (`ai.nhan_xet_hoc_ba`, `danh_gia.muc_cuoi_ky`) · Task 6: README setup + requirements
- [ ] Each task: test first → implement → `python test_app.py` → Chrome screenshot (with seeded data) → commit + push.
