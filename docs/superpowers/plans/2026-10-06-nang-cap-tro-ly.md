# Upgrading the TT27 Assistant – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a multipage UI, AI worksheet review, classroom presentation mode, class roster with per-student sheets and version A/B, and photo grading with a TT27 gradebook.

**Architecture:** Streamlit multipage via `st.navigation(position="top")`; shared logic in `state.py`; pure-logic modules (`ai.py`, `danh_gia.py`, `docx_export.py`, `html_export.py`, `classroom_html.py`) are tested without the network via a FakeClient; pages live in `trang/`.

**Tech Stack:** Python 3.12+, Streamlit ≥1.65, google-genai, pydantic v2, python-docx, openpyxl.

**Spec:** `docs/superpowers/specs/2026-10-06-nang-cap-tro-ly-design.md`

## Global Constraints

- All user-facing text in Vietnamese; code identifiers keep the existing Vietnamese-without-diacritics style (`tao_phieu`, `ban`, `phieu`).
- Any AI/user content placed into HTML must go through `html.escape` (print view) or `json.dumps` + `textContent` (classroom mode). JSON inside `<script>` must escape `</` as `<\/`.
- Student names are never sent to the AI.
- Tests: `python test_app.py` (plain asserts, no pytest); every new function gets a test in that file.
- Deploy: Streamlit Community Cloud, `requirements.txt` adds `openpyxl>=3.1`.
- Commit + push after each task (the user has already approved pushes to `main`).

---

### Task 1: Multipage foundation + theme + home page

**Files:**
- Create: `state.py`, `trang/__init__.py` (empty), `trang/trang_chu.py`, `trang/soan_phieu.py`, `trang/lop_hoc.py`, `trang/cham_bai.py`, `trang/lop_cua_toi.py` (the last 3 are temporary placeholder pages: title + "Coming soon")
- Modify: `app.py` (becomes the router), `.streamlit/config.toml`, `test_app.py`

**Interfaces:**
- Produces (`state.py`): `MODEL: str`, `PHIEU_MAU: Path`, `api_key() -> str`, `client() -> genai.Client`, `loi_than_thien(e) -> str`, `bao_loi(e) -> None`, `md(s) -> str`, `ten_file(s) -> str`, `dat_phieu(ban: BanLuu) -> None`, `mo_phieu(raw) -> None`, `ban_hien_tai() -> BanLuu | None`, `truong() -> str`, `ten_gv() -> str`, `TRANG: dict[str, st.Page]` (keys: `trang_chu`, `soan_phieu`, `lop_hoc`, `cham_bai`, `lop_cua_toi`).
- Shared sidebar widgets in `app.py` with keys `api_key_nhap`, `truong`, `ten_gv`.

- [ ] **Step 1: Write the failing test** (in `test_app.py`, replacing `test_giao_dien_phieu_mau` and `test_doi_cau_va_hoan_tac`)

```python
def _app(secret_key=None):
    at = AppTest.from_file("app.py", default_timeout=30)
    if secret_key:
        at.secrets["GEMINI_API_KEY"] = secret_key
    return at.run()


def test_trang_chu_va_dieu_huong():
    at = _app()
    assert not at.exception
    for trang in ["trang/soan_phieu.py", "trang/lop_hoc.py", "trang/cham_bai.py", "trang/lop_cua_toi.py"]:
        at.switch_page(trang).run()
        assert not at.exception, trang


def test_soan_phieu_mau_doi_cau_hoan_tac():
    goc = ai.tao_lai_cau
    ai.tao_lai_cau = lambda client, model, ts, phieu, i, che_do: phieu.cau_hoi[i].model_copy(update={"noi_dung": "CÂU MỚI"})
    try:
        at = _app("fake")
        at.switch_page("trang/soan_phieu.py").run()
        at.button(key="mau_main").click().run()
        assert len(at.session_state.lich_su) == 1
        cu = at.session_state.ban.phieu.cau_hoi[0].noi_dung
        at.button(key="doi0").click().run()
        assert at.session_state.ban.phieu.cau_hoi[0].noi_dung == "CÂU MỚI"
        at.button(key="ht0").click().run()
        assert at.session_state.ban.phieu.cau_hoi[0].noi_dung == cu
    finally:
        ai.tao_lai_cau = goc
```

- [ ] **Step 2: Run** `python test_app.py` → FAIL (`trang/...` does not exist).
- [ ] **Step 3: Implement**
  - `state.py`: move `_secret`, `MODEL`, `PHIEU_MAU`, `loi_than_thien`, `bao_loi`, `md`, `ten_file`, `dat_phieu`, `mo_phieu` out of `app.py`. `api_key()` returns `_secret("GEMINI_API_KEY") or st.session_state.get("api_key_nhap", "")`. `client()` = `_client(api_key())` with `@st.cache_resource`. `TRANG` built from `st.Page("trang/<file>.py", title=..., icon=..., default=(name=="trang_chu"))`.
  - `app.py`: `set_page_config`, CSS (banner, `.the`, `.buoc`), sidebar (key / school / teacher name / history / open JSON / sample), `pg = st.navigation(list(state.TRANG.values()), position="top"); pg.run()`.
  - `trang/soan_phieu.py`: the full content of the current `app.py` from `trai, phai = st.columns(...)` onward, with helpers read from `state`; on create, call `st.switch_page` is not needed (stay on the page).
  - `trang/trang_chu.py`: `st.html` greeting (`Chào {ten_gv}`), 4 cards using `st.page_link(state.TRANG[...], label=..., icon=...)` inside `st.container(border=True)`, "Recent worksheets" = `lich_su` (button opens it and `st.switch_page(state.TRANG["soan_phieu"])`).
  - `config.toml`: `font = "'Be Vietnam Pro':https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap"`, `baseRadius = "0.75rem"`, keep `primaryColor`.
- [ ] **Step 4: Run** `python test_app.py` → all PASS; Chrome screenshot of home + worksheet page.
- [ ] **Step 5: Commit + push** `feat: multipage navigation, home page, Be Vietnam Pro theme`.

### Task 2: AI worksheet review

**Files:** Modify `ai.py`, `trang/soan_phieu.py`, `test_app.py`

**Interfaces:**
- Produces (`ai.py`):

```python
class VanDe(BaseModel):
    cau_so: int = Field(description="Số thứ tự câu trong phiếu (bắt đầu từ 1); 0 nếu là vấn đề chung")
    loai: Literal["dap_an_sai", "lech_muc", "ngon_ngu", "trinh_bay"]
    mo_ta: str
    de_xuat: str

class KiemDinh(BaseModel):
    diem: int = Field(description="Điểm chất lượng 0-100")
    nhan_xet_chung: str
    van_de: list[VanDe]

# BanLuu adds: kiem_dinh: KiemDinh | None = None; kiem_dinh_cho: str = ""   (fingerprint of the reviewed worksheet)
def dau_van_tay(phieu: Phieu) -> str  # sha1 of phieu.model_dump_json()
def kiem_dinh(client, model, ts: ThongSo, phieu: Phieu) -> KiemDinh  # clamp diem 0..100, drop van_de with cau_so out of range
def tao_lai_cau(client, model, ts, phieu, idx, che_do: str, gop_y: str = "") -> CauHoi  # gop_y appended to the prompt
```

- [ ] **Step 1: Failing tests**

```python
def test_kiem_dinh_kep_diem_va_loc_cau():
    kd = ai.KiemDinh(diem=140, nhan_xet_chung="ok", van_de=[
        ai.VanDe(cau_so=2, loai="dap_an_sai", mo_ta="sai", de_xuat="sửa"),
        ai.VanDe(cau_so=99, loai="ngon_ngu", mo_ta="x", de_xuat="y")])
    out = ai.kiem_dinh(FakeClient(kd), "m", BAN.thong_so, BAN.phieu)
    assert out.diem == 100 and [v.cau_so for v in out.van_de] == [2]


def test_dau_van_tay_doi_khi_sua():
    p = BAN.phieu.model_copy(deep=True)
    a = ai.dau_van_tay(p)
    p.cau_hoi[0].noi_dung += "!"
    assert a != ai.dau_van_tay(p)
```

- [ ] **Step 2:** run → FAIL. **Step 3:** implement the review prompt (role: TT27 review lead; check every answer by recomputing, level match, age-appropriate wording, presentation; return issues with question numbers). `CHE_DO["gop_y"] = "Soạn lại câu này để khắc phục góp ý sau, giữ nguyên mức."`.
- [ ] **UI:** after `tao_phieu` succeeds → call `kiem_dinh` inside the same `st.status` ("🔎 AI đang kiểm định"); store `ban.kiem_dinh`, `ban.kiem_dinh_cho = dau_van_tay(phieu)`. A "Review" block at the top of the results: `st.metric("Điểm kiểm định", f"{diem}/100")`, badge green ≥85 / orange ≥70 / red, overall comment, "🔎 Re-review" button; if the fingerprint differs → caption "Worksheet changed since the last review". On each question card: for every `VanDe` with `cau_so == i+1` → `st.warning(f"{LOAI[v.loai]}: {v.mo_ta} → {v.de_xuat}")` + button `🛠 Sửa theo góp ý` (key `gy{i}`) calling `tao_lai_cau(..., "gop_y", gop_y=...)`. A review failure must not block the worksheet (only `st.warning`).
- [ ] **Step 4:** tests PASS. **Step 5:** commit + push `feat: AI worksheet review with per-question warnings`.

### Task 3: Classroom mode

**Files:** Create `classroom_html.py`; modify `trang/lop_hoc.py`, `test_app.py`

**Interfaces:**
- Produces: `dap_an_dung(c: CauHoi) -> int | None` (index of the correct option for multiple choice, parsed from the first `A–H` letter of `dap_an`); `trinh_chieu(ban: BanLuu, ten_hs: list[str], giay: int, doc_to: bool) -> str` (full HTML document; `giay=0` = no timer).
- Consumes: `ban_hien_tai()`, `st.session_state.lop` (Task 4; until then use `[]`).

- [ ] **Step 1: Failing tests**

```python
def test_dap_an_dung():
    c = BAN.phieu.cau_hoi[0]
    assert cx.dap_an_dung(c) == 1  # "B. 43"
    assert cx.dap_an_dung(c.model_copy(update={"dap_an": "Đáp án: C"})) == 2
    assert cx.dap_an_dung(BAN.phieu.cau_hoi[1]) is None  # not multiple choice


def test_trinh_chieu_an_toan():
    ban = BAN.model_copy(deep=True)
    ban.phieu.cau_hoi[0].noi_dung = "</script><script>alert(1)</script>"
    h = cx.trinh_chieu(ban, ["An", "Bình"], 60, True)
    assert "</script><script>alert" not in h and "<\\/script>" in h
    assert '"giay": 60' in h and "speechSynthesis" in h
```

- [ ] **Step 2:** FAIL. **Step 3:** implement `classroom_html.py`: `DATA = json.dumps({...}, ensure_ascii=False).replace("</", "<\\/")`; HTML: 16:9 layout, a `#slide` area, bottom bar with buttons `◀ ▶ ⏱ 🔊 👁 🎲 ⛶`; JS renders with `textContent`; Kahoot-style cards (4 colours `#E53935 #1E88E5 #FDD835 #43A047`); SVG circular timer; a small hand-written canvas confetti function (~30 lines, no CDN); `speechSynthesis` with `lang="vi-VN"`; the wheel picks a random name from `ten_hs` with an 1.5s "rolling" animation; `document.documentElement.requestFullscreen()`; keys ← → Space(reveal answer) T(timer).
- [ ] **UI `trang/lop_hoc.py`:** no worksheet → info + button to the worksheet page; options `segmented_control` timer (Off/30/60/90 s), toggle read aloud; `st.iframe(trinh_chieu(...), height=720)`; caption with the key shortcuts.
- [ ] **Step 4:** PASS + Chrome screenshot of the slide. **Step 5:** commit + push `feat: classroom presentation mode`.

### Task 4: My class, version B, per-student sheets

**Files:** Modify `ai.py`, `docx_export.py`, `html_export.py`, `trang/lop_cua_toi.py`, `test_app.py`

**Interfaces:**
- Produces (`ai.py`): `HocSinh(stt: int, ten: str, nhom: Literal["Xanh","Cam","Tím"])`, `LopHoc(ten_lop: str = "", hoc_sinh: list[HocSinh] = [])`; `BanLuu.phieu_b: Phieu | None = None`; `tao_de_b(client, model, ts, phieu) -> Phieu` (requires the same number of questions; copies `muc/dang/diem` from A onto B; raises `ValueError` if the count differs).
- Produces (`docx_export.py`): `ban_de_b(ban) -> BanLuu` (copy with `phieu = phieu_b`); `phieu_theo_ten(ban, hs: list[HocSinh], xen_ke_ab: bool) -> bytes` (one Word file, one page per student, page break between pages, the name filled into "Họ và tên", title "PHIẾU {NHOM}" + " – ĐỀ B" if version B).
- Produces (`html_export.py`): `phieu_theo_ten(ban, hs, xen_ke_ab) -> list[str]` (list of `.trang`).
- Refactor: `docx_export._viet_phieu_nhom(doc, ban, ten, ho_ten="", nhan="")` writes into an existing doc; `phieu_nhom()` calls it. `_tieu_de(..., ho_ten="")`. The same for `html_export._dau(..., ho_ten="")`.
- Rule: `xen_ke_ab and ban.phieu_b and hs.stt % 2 == 0` → version B.

- [ ] **Step 1: Failing tests**

```python
def test_de_b_giu_cau_truc():
    b = BAN.phieu.model_copy(deep=True)
    for c in b.cau_hoi:
        c.muc, c.diem = 3, 9
    out = ai.tao_de_b(FakeClient(b), "m", BAN.thong_so, BAN.phieu)
    assert [(c.muc, c.dang, c.diem) for c in out.cau_hoi] == [(c.muc, c.dang, c.diem) for c in BAN.phieu.cau_hoi]


def test_phieu_theo_ten():
    ban = BAN.model_copy(update={"phieu_b": BAN.phieu.model_copy(deep=True)})
    hs = [ai.HocSinh(stt=1, ten="Nguyễn An", nhom="Xanh"), ai.HocSinh(stt=2, ten="Lê Bình", nhom="Tím")]
    trang = hx.phieu_theo_ten(ban, hs, True)
    assert len(trang) == 2 and "Nguyễn An" in trang[0] and "PHIẾU XANH" in trang[0]
    assert "ĐỀ B" in trang[1] and "ĐỀ B" not in trang[0]
    d = Document(io.BytesIO(dx.phieu_theo_ten(ban, hs, True)))
    text = "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    assert "Nguyễn An" in text and "Lê Bình" in text
```

- [ ] **Step 2:** FAIL. **Step 3:** implement. **UI `trang/lop_cua_toi.py`:** class name input; `st.data_editor(rows, num_rows="dynamic", column_config={"nhom": SelectboxColumn(options=[Xanh,Cam,Tím])})` stored in `st.session_state.lop: LopHoc`; buttons to save/load `lop.json`; a "Version A/B" section (button `✨ Tạo đề B` → `tao_de_b`, store `ban.phieu_b`); a "Per-student sheets" section: toggle alternate A/B, print preview `st.iframe(hx.trang_in(...))`, download Word. A note "Student names stay in the browser and are not sent to the AI".
- [ ] **Step 4:** PASS. **Step 5:** commit + push `feat: class roster, version B and per-student sheets`.

### Task 5: Grading from photos + gradebook

**Files:** Create `danh_gia.py`; modify `ai.py`, `trang/cham_bai.py`, `requirements.txt`, `test_app.py`

**Interfaces:**
- Produces (`ai.py`): `KetQuaCau(cau_so: int, dat: Literal["dung","mot_phan","sai","bo_trong"], diem_dat: float, ghi_chu: str)`, `KetQuaCham(ten_tren_phieu: str, cau: list[KetQuaCau], nhan_xet: str)`; `cham_bai(client, model, ts, phieu, ids: list[int], anh: tuple[bytes, str]) -> KetQuaCham` (the prompt lists the sheet's questions numbered 1..len(ids) with their answer and marking guide; clamp `diem_dat` to `[0, diem]`).
- Produces (`danh_gia.py`):

```python
TY_LE = {"dung": 1.0, "mot_phan": 0.5, "sai": 0.0, "bo_trong": 0.0}
NHOM_DE_XUAT = {"Hoàn thành tốt": "Tím", "Hoàn thành": "Cam", "Chưa hoàn thành": "Xanh"}
def muc_tt27(phieu, ids: list[int], kq: KetQuaCham) -> str
def khop_ten(ten: str, ds_ten: list[str]) -> str  # difflib.get_close_matches(cutoff=0.6), case-insensitive; returns the input name if no match
def so_tong_hop_excel(rows: list[dict]) -> bytes  # openpyxl, bold header, column widths, wrap the comment column
```

- [ ] **Step 1: Failing tests**

```python
def _kq(*dat):
    return ai.KetQuaCham(ten_tren_phieu="An", nhan_xet="", cau=[
        ai.KetQuaCau(cau_so=k + 1, dat=d, diem_dat=0, ghi_chu="") for k, d in enumerate(dat)])

def test_muc_tt27():
    ids = list(range(7))  # 3 level-1 questions, 2 level-2, 2 level-3
    assert dg.muc_tt27(BAN.phieu, ids, _kq(*["dung"] * 7)) == "Hoàn thành tốt"
    assert dg.muc_tt27(BAN.phieu, ids, _kq("sai", "sai", "dung", "dung", "dung", "dung", "dung")) == "Chưa hoàn thành"
    assert dg.muc_tt27(BAN.phieu, ids, _kq("dung", "dung", "dung", "dung", "mot_phan", "sai", "sai")) == "Hoàn thành"
    xanh = [0, 1, 2, 3]  # Xanh sheet: no level 3 → level 3 counts as met
    assert dg.muc_tt27(BAN.phieu, xanh, _kq("dung", "dung", "dung", "dung")) == "Hoàn thành tốt"

def test_khop_ten():
    assert dg.khop_ten("nguyen van an", ["Nguyễn Văn An", "Lê Bình"]) == "Nguyễn Văn An"
    assert dg.khop_ten("Trần C", ["Nguyễn Văn An"]) == "Trần C"

def test_excel():
    from openpyxl import load_workbook
    b = dg.so_tong_hop_excel([{"STT": 1, "Họ tên": "An", "Điểm": 9.5, "Mức TT27": "Hoàn thành tốt", "Nhận xét": "Tốt"}])
    ws = load_workbook(io.BytesIO(b)).active
    assert ws["B2"].value == "An" and ws["A1"].font.bold

def test_cham_bai_kep_diem():
    kq = _kq("dung"); kq.cau[0].diem_dat = 99
    out = ai.cham_bai(FakeClient(kq), "m", BAN.thong_so, BAN.phieu, [0], (b"x", "image/png"))
    assert out.cau[0].diem_dat == BAN.phieu.cau_hoi[0].diem
```

`khop_ten` compares after stripping diacritics (reuse `unicodedata` NFKD + `đ→d`).

- [ ] **Step 2:** FAIL. **Step 3:** implement. **UI `trang/cham_bai.py`:**
  - The sheet handed out: `segmented_control` Shared/Xanh/Cam/Tím → `ids` (Shared = order by level; group = `cau_cua_nhom` main + bonus).
  - `file_uploader` multiple photos (≤ 40, 5MB); privacy note.
  - "Grade N papers" button → loop with `st.progress`, each photo `try/except` (record the error, continue).
  - Result per student: `{"STT", "Ảnh", "Họ tên" (khop_ten with the roster), "Điểm", "Mức TT27", "Nhóm đề xuất", "Nhận xét", "Câu 1".."Câu n" (✓/½/✗/–)}` stored in `st.session_state.ket_qua_cham`.
  - `st.data_editor` (editable name, TT27 level, comment); 3 metric tiles HTT/HT/CHT counts (+ %); "Apply suggested groups to My class" button (match by name); download Excel.
  - `requirements.txt` adds `openpyxl>=3.1`.
- [ ] **Step 4:** PASS + screenshot. **Step 5:** commit + push `feat: photo grading with TT27 levels and Excel gradebook`; update README.
