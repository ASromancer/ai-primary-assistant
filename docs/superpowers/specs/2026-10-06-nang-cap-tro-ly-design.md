# Design: Upgrading the TT27 differentiated-worksheet assistant

Date: 2026-10-06. Context: a demo app for a teaching-innovation contest. Runs on free Streamlit Community Cloud with the free Gemini tier.

## Goals
Grow the app from a "worksheet generator" into a teacher's working tool: generate → verify → teach in class → grade → regroup students, with a professional, bright UI.

## Architecture
- `app.py`: router `st.navigation(position="top")`, theme/CSS, shared sidebar (API key, school name, teacher name).
- `state.py`: shared session state (current worksheet, history, class roster, grading results), cached Gemini client, error reporting, the `md()` escape helper.
- `pages/trang_chu.py`, `pages/soan_phieu.py`, `pages/lop_hoc.py`, `pages/cham_bai.py`, `pages/lop_cua_toi.py`.
- `ai.py` adds: `kiem_dinh()`, `sua_theo_gop_y()`, `tao_de_b()`, `cham_bai()`; all use the existing `_goi()` (retry + backup models).
- `classroom_html.py`: a self-contained HTML/JS classroom presentation app.
- `docx_export.py` / `html_export.py`: per-student sheets (one page each), version B.
- New dependency: `openpyxl` (export the summary gradebook to Excel).

## Batch 1 – Foundation & UI
- Top navigation menu, Be Vietnam Pro font, bright blue-led theme, rounded cards.
- Home page: greeting with the teacher's name, 4 feature cards (`st.page_link`), recent worksheets with their review score.
- Settings are shared across all pages via the sidebar.

## Batch 2 – AI worksheet review
- Model `KiemDinh{diem: 0-100, nhan_xet_chung, van_de: [VanDe{cau_so, loai, mo_ta, de_xuat}]}`; `loai` ∈ dap_an_sai | lech_muc | ngon_ngu | trinh_bay.
- Runs automatically after a worksheet is created. The result is cached by a hash of the worksheet content; if the content changes, it is marked "needs re-review" (with a re-run button).
- Each question card shows its warnings + a "🛠 Fix per feedback" button (regenerates the question with the feedback included).

## Batch 3 – Classroom mode
- An HTML/JS app inside `st.iframe` (the sandbox allows scripts/modals/fullscreen). Data is passed via `json.dumps` (escaping `</`) and rendered with `textContent` only.
- Slides: cover → each question (large text, Kahoot-style coloured cards for multiple choice, circular countdown timer of 30/60/90s or off) → final slide with the encouragement message.
- Buttons/keys: ← → to navigate, 🔊 read aloud (`speechSynthesis` vi-VN), 👁 reveal answer (correct card highlighted + confetti), 🎲 name wheel (from "My class"), ⛶ fullscreen.
- The correct option is parsed from `dap_an` (first letter A–H) for multiple choice; other types show the answer text.

## Batch 4 – My class, per-student sheets, version A/B
- Model `HocSinh{stt, ten, nhom}`; roster edited with `st.data_editor` (pasting from Excel works); save/load `lop.json`.
- Student names are used locally only, never sent to the AI.
- `tao_de_b(phieu)`: same structure (level/type/points per question), different numbers and wording; stored on `BanLuu.phieu_b` (optional).
- Per-student sheets: one page per student with the name pre-filled, matching their group colour; option to alternate A/B by odd/even roll number. Print in the browser or download a single Word file.

## Batch 5 – Grading from photos + summary gradebook
- Pick the worksheet that was handed out (shared/Xanh/Cam/Tím), upload multiple photos (one per student).
- `cham_bai(phieu_da_phat, anh)` → `KetQuaCham{ten_tren_phieu, cau: [{cau_so, dat: dung|mot_phan|sai|bo_trong, diem_dat, ghi_chu}], nhan_xet}`.
- Grades photo by photo with a progress bar; a failed photo is recorded and grading continues.
- Name matched against the class roster with `difflib.get_close_matches`; the teacher can edit it.
- TT27 level computed by **code** (deterministic) from the correct ratio per level (dung = 1, mot_phan = 0.5):
  - Not yet completed (CHT): level-1 ratio < 50%.
  - Completed well (HTT): level 1 ≥ 80%, level 2 ≥ 80%, level 3 ≥ 50% (a level with no questions counts as met).
  - Otherwise: Completed (HT).
- Suggested group: CHT→Xanh, HT→Cam, HTT→Tím; one button applies the groups to "My class".
- Gradebook: table + level distribution, Excel export. Notice: the photos are sent to Google for grading and are not stored by the app.

## Errors
- Reuse `bao_loi()` (friendly message + technical details). Grading continues with the next photo on error.

## Testing
- Each AI function tested with a FakeClient; tests for the TT27 level rule, name matching, HTML/JSON escaping, per-student sheets, Excel export; AppTest smoke test for every page; Chrome screenshots after each batch.

## Out of scope
- Streaming output, QR codes for online student work, a cloud worksheet library (needs a database and login).
