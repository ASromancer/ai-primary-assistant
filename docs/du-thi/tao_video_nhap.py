"""Dựng VIDEO NHÁP (≤ 5 phút) theo kịch bản 04-kich-ban-video.md: ảnh slide + đoạn quay màn hình app + phụ đề.

Giáo viên dùng video này làm khung: thu giọng thuyết trình đè lên (hoặc ghép trong CapCut), thay đoạn
"Kết quả" bằng số liệu/cảnh lớp học thật, thêm hình giáo viên. KHÔNG nộp nguyên video nháp.

Chạy:   .venv/bin/python docs/du-thi/tao_video_nhap.py
Cần:    Chrome, playwright, imageio-ffmpeg, LibreOffice (để chuyển slide sang ảnh)
Đầu ra (thư mục ban-nop/, không đưa lên GitHub):
  - video-nhap.mp4         video nháp có phụ đề
  - phu-de.srt             phụ đề (nhập vào CapCut nếu dựng lại)
  - doan-quay/*.mp4        từng đoạn quay màn hình sạch (không phụ đề) để ghép tự do

Dữ liệu: giáo viên, trường, lớp và danh sách học sinh thật (ban-nop/so-lieu.json, ban-nop/danh-sach-lop.xlsx);
điểm, nhận xét là dữ liệu minh họa. Phiếu mẫu lớp 4 do Gemini soạn và kiểm định thật (ban-nop/phieu-mau-lop4.json);
khi quay, AI được giả lập trả lại phiếu đó để rút gọn thời gian chờ.
"""
import contextlib
import json
import re
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

DU_THI = Path(__file__).parent.resolve()
GOC = DU_THI.parents[1]
RA = DU_THI / "ban-nop"
DOAN = RA / "doan-quay"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PY = sys.executable
W, H = 1920, 1080

# (mã, thời lượng giây, loại, lời thuyết trình) — lời lấy từ 04-kich-ban-video.md
KICH_BAN = [
    ("01-mo-dau", 18, "slide:1", "Xin chào Ban Giám khảo. Tôi là ⟦họ tên⟧, giáo viên lớp ⟦…⟧ Trường ⟦…⟧. "
     "Tôi xin giới thiệu Trợ Lý Giảng Dạy – công cụ AI giúp giáo viên tiểu học soạn phiếu phân hóa và đánh giá học sinh theo Thông tư 27."),
    ("02-boi-canh", 33, "slide:3", "Lớp tôi có ⟦…⟧ em với trình độ rất khác nhau. Để mỗi em được làm bài vừa sức, tôi phải soạn phiếu ba mức, "
     "in cho từng nhóm, chấm và viết nhận xét từng em – mỗi phiếu mất khoảng ⟦…⟧ phút. Thử dùng chatbot AI thì câu trả lời rời rạc, "
     "không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra."),
    ("03-giai-phap", 23, "slide:4", "Vì vậy tôi xây dựng một vòng khép kín 6 bước: soạn phiếu, AI kiểm định, dạy và giao bài, chấm và nhận xét, "
     "phân tích lỗi để bổ trợ, và theo dõi tiến bộ đến học bạ. AI đề xuất – giáo viên quyết định."),
    ("04-soan-phieu", 30, "app:soan", "(Minh họa giao diện) Tôi chọn lớp, môn, nhập tên bài hoặc chụp trang sách giáo khoa. "
     "Khoảng 30 giây, AI soạn xong phiếu ba mức theo Thông tư 27, đáp án trình bày đúng như vở học sinh, kèm ma trận và yêu cầu cần đạt."),
    ("05-kiem-dinh", 20, "app:kiemdinh", "Điểm khác biệt: một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu để soát đáp án sai "
     "và câu lệch mức. Trong thí điểm, nó đã phát hiện ⟦…⟧ lỗi."),
    ("06-phan-hoa", 20, "app:inphieu", "Một phiếu tự tách thành ba phiếu Xanh, Cam, Tím cho ba nhóm. Tên màu trung tính, nên các em "
     "không cảm thấy bị xếp loại."),
    ("07-giao-bai", 50, "app:giaobai", "Trên lớp, tôi chiếu mã QR. Các em quét bằng máy tính bảng, chạm vào tên mình, không cần tài khoản, "
     "và tự nhận đúng phiếu của nhóm. Câu trắc nghiệm được chấm ngay. Tôi theo dõi trực tiếp em nào đã nộp."),
    ("08-cham-bai", 30, "app:chambai", "Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27; mức đạt tính theo quy tắc công khai "
     "và tôi sửa được từng câu. Biểu đồ cho thấy cả lớp còn yếu ở đâu – một nút bấm là có phiếu bổ trợ đúng chỗ đó."),
    ("09-tien-bo", 15, "app:tienbo", "Kết quả được lưu theo từng em. Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, không cần gửi tên học sinh."),
    ("10-ket-qua", 33, "slide:12", "Sau ⟦…⟧ ngày thí điểm với ⟦…⟧ học sinh: thời gian soạn phiếu giảm từ ⟦…⟧ xuống ⟦…⟧ phút, chấm và nhận xét "
     "từ ⟦…⟧ xuống ⟦…⟧ phút; tỉ lệ chưa đạt giảm từ ⟦…⟧ xuống ⟦…⟧ sau một buổi bổ trợ. (Thay bằng số liệu và cảnh lớp học thật.)"),
    ("11-trach-nhiem", 20, "slide:10", "Sản phẩm miễn phí, chạy trên trình duyệt, dùng cho khối 1 đến 5 và bộ sách giáo khoa dùng chung toàn quốc. Tên học sinh không được gửi cho AI; "
     "mọi đề, điểm và nhận xét đều do giáo viên duyệt."),
    ("12-ket", 13, "slide:14", "Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em. "
     "Xin cảm ơn Ban Giám khảo!"),
]

HARNESS = r'''
# Tệp tạm do tao_video_nhap.py sinh ra – dựng dữ liệu minh họa để quay màn hình
import json, time
import streamlit as st
from sqlalchemy import create_engine
import ai, state
DB = create_engine("sqlite:///__DB__")
DL = json.load(open("__DL__", encoding="utf-8"))
state.email, state.co_db, state.db = (lambda: "gv@truong.vn"), (lambda: True), (lambda: DB)
state.tu_luu = lambda: None
MAU = ai.BanLuu.model_validate_json(open("__MAU__", encoding="utf-8").read())
def _tao(client, model, ts, dang, anh, ghi_chu=""):
    time.sleep(4); return MAU.phieu.model_copy(deep=True)
def _kd(client, model, ts, phieu):
    time.sleep(3); return MAU.kiem_dinh
ai.tao_phieu, ai.kiem_dinh = _tao, _kd
che_do = st.query_params.get("kb", "")
if "khoi_tao" not in st.session_state and not st.query_params.get("ma"):
    st.session_state.khoi_tao = True
    st.session_state.ho_so = {"lop_mac_dinh": MAU.thong_so.lop, "mon_mac_dinh": "Toán"}
    if che_do != "soan":
        state.dat_phieu(MAU.model_copy(deep=True))
    st.session_state.cham = {"ver": 1, "loi": [], "cau": MAU.phieu.cau_hoi, "ts": MAU.thong_so, "loai": "Phiếu chung",
                             "rows": DL["rows"]}
exec(open("app.py", encoding="utf-8").read())
'''


CHU_DE = "Phép cộng các số có nhiều chữ số"
PHIEU_MAU = RA / "phieu-mau-lop4.json"  # phiếu lớp 4 do Gemini soạn và kiểm định thật (sinh 1 lần, dùng lại)
DANH_SACH = RA / "danh-sach-lop.xlsx"  # danh sách học sinh thật – chỉ nằm trong ban-nop/, không đưa lên GitHub


def thong_tin() -> dict:
    """Giáo viên, trường, lớp (ban-nop/so-lieu.json) và danh sách học sinh (ban-nop/danh-sach-lop.xlsx)."""
    import openpyxl
    d = json.loads((RA / "so-lieu.json").read_text(encoding="utf-8")) if (RA / "so-lieu.json").exists() else {}
    hs = []
    if DANH_SACH.exists():
        for r in openpyxl.load_workbook(DANH_SACH, read_only=True).active.iter_rows(values_only=True):
            if isinstance(r[0], int) and r[1]:
                hs.append(" ".join(str(r[1]).split()))
    truong = (d.get("truong") or "Hoa Sen").replace("Trường", "").replace("Tiểu học", "").strip()
    return {"ten_gv": d.get("ho_ten") or "Nguyễn Thị Lan", "truong": truong,  # phiếu in sẵn "Trường Tiểu học: …"
            "lop": d.get("lop") or "4A", "hoc_sinh": hs or [f"Học sinh {k}" for k in range(1, 9)]}


def phieu_mau():
    sys.path.insert(0, str(GOC))
    import ai
    if PHIEU_MAU.exists():
        return ai.BanLuu.model_validate_json(PHIEU_MAU.read_text(encoding="utf-8"))
    import tomllib

    from google import genai
    key = os.environ.get("GEMINI_API_KEY") or tomllib.loads((GOC / ".streamlit/secrets.toml").read_text())["GEMINI_API_KEY"]
    client, model = genai.Client(api_key=key), "gemini-3.8-flash"
    ts = ai.ThongSo(mon="Toán", lop=4, bo_sach="Kết nối tri thức với cuộc sống", chu_de=CHU_DE, thoi_luong=20,
                    truong=thong_tin()["truong"])
    phieu = ai.tao_phieu(client, model, ts, list(ai.DANG_BAI), [])
    ban = ai.BanLuu(thong_so=ts, phieu=phieu, kiem_dinh=ai.kiem_dinh(client, model, ts, phieu), kiem_dinh_cho=ai.dau_van_tay(phieu))
    PHIEU_MAU.write_text(ban.model_dump_json(indent=1), encoding="utf-8")
    return ban


# Lỗi minh họa theo dạng câu (dùng cho sổ tổng hợp, phân tích lỗi)
LOI = {"trac_nghiem": ["✗ chọn sai"], "dung_sai": ["½ sai 1 ý"], "noi_cot": ["½ nối sai 1 cặp"],
       "dien_khuyet": ["✗ quên nhớ", "½ đúng 1 chỗ"], "tu_luan": ["½ thiếu đáp số", "✗ đặt tính sai hàng", "½ thiếu câu lời giải"]}
NHAN_XET = {"Hoàn thành tốt": ["Em tính nhanh, trình bày rõ ràng.", "Em làm bài cẩn thận, chính xác."],
            "Hoàn thành": ["Em nhớ đặt tính thẳng hàng nhé.", "Em trình bày đủ câu lời giải và đáp số nhé.", "Em kiểm tra lại phép tính có nhớ."],
            "Chưa hoàn thành": ["Em cần luyện thêm cộng có nhớ.", "Em đọc kỹ đề và đặt tính thẳng hàng nhé."]}


def du_lieu_lop(ban, hoc_sinh: list[str]) -> tuple[list, list[dict]]:
    """Chia nhóm và dựng sổ chấm minh họa (cố định, tái lập được) cho cả lớp."""
    import random
    r = random.Random(4)
    nhom = [("Xanh", "Cam", "Tím")[0 if x < 0.25 else 1 if x < 0.75 else 2] for x in (r.random() for _ in hoc_sinh)]
    cau, rows = ban.phieu.cau_hoi, []
    for k, (ten, n) in enumerate(zip(hoc_sinh, nhom)):
        gioi = {"Xanh": 0.55, "Cam": 0.78, "Tím": 0.93}[n]
        o = []
        for c in cau:
            x = r.random() * (1.15 if c.muc == 3 else 1)
            o.append("✓" if x < gioi else "–" if c.muc == 3 and x > 1.05 else r.choice(LOI[c.dang]))
        diem = sum(c.diem * (1 if v == "✓" else 0.5 if v.startswith("½") else 0) for c, v in zip(cau, o))
        tl = {m: [1 if v == "✓" else 0.5 if v.startswith("½") else 0 for c, v in zip(cau, o) if c.muc == m] for m in (1, 2, 3)}
        dat = lambda m, ng: not tl[m] or sum(tl[m]) / len(tl[m]) >= ng
        muc = "Chưa hoàn thành" if not dat(1, 0.5) else "Hoàn thành tốt" if dat(1, .8) and dat(2, .8) and dat(3, .5) else "Hoàn thành"
        rows.append({"STT": k + 1, "Họ tên": ten, "Điểm": round(diem * 2) / 2, "Mức TT27": muc,
                     "Nhận xét": r.choice(NHAN_XET[muc]), **{f"Câu {j + 1}": v for j, v in enumerate(o)}, "Ảnh": f"bai_{k + 1}.jpg"})
    return nhom, rows


def tao_du_lieu(db_path: str) -> tuple[str, Path]:
    """Dữ liệu minh họa: hồ sơ giáo viên, thư viện phiếu, lớp thật (danh sách), 4 lần chấm, 1 bài giao online."""
    sys.path.insert(0, str(GOC))
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import create_engine

    import ai
    import kho
    tt, ban = thong_tin(), phieu_mau()
    db, e = create_engine(f"sqlite:///{db_path}"), "gv@truong.vn"
    kho.tao_bang(db)
    kho.ho_so_luu(db, e, ten=tt["ten_gv"], truong=tt["truong"], lop_mac_dinh=ban.thong_so.lop, mon_mac_dinh="Toán")
    for cd, mon in [("Số có sáu chữ số", "Toán"), ("Danh từ", "Tiếng Việt"), ("Một số tính chất của nước", "Khoa học"),
                    ("Đo góc, đơn vị đo góc", "Toán"), (CHU_DE, "Toán")]:
        b = ban.model_copy(deep=True)
        b.thong_so.chu_de, b.thong_so.mon = cd, mon
        kho.phieu_luu(db, e, b)
    nhom, rows = du_lieu_lop(ban, tt["hoc_sinh"])
    lop = ai.LopHoc(ten_lop=tt["lop"], hoc_sinh=[ai.HocSinh(stt=k + 1, ten=t, nhom=n)
                                                for k, (t, n) in enumerate(zip(tt["hoc_sinh"], nhom))])
    kho.lop_luu(db, e, lop)
    m = ["Chưa hoàn thành", "Hoàn thành", "Hoàn thành tốt"]
    goc = kho._bay_gio
    for k, cd in enumerate(["Số có sáu chữ số", "Hàng và lớp", "Đo góc", CHU_DE]):
        kho._bay_gio = lambda k=k: datetime(2026, 9, 21, 2, tzinfo=timezone.utc) + timedelta(days=7 * k)
        cuoi = {r["Họ tên"]: m.index(r["Mức TT27"]) for r in rows}
        kho.cham_luu(db, e, lop.id, "Toán", cd, "Phiếu chung",  # tiến bộ dần đến lần chấm cuối
                     [{"ten": t, "diem": 4 + 2.5 * max(0, cuoi[t] - (3 - k) // 2 * (i % 2)), "nhan_xet": "...",
                       "muc_tt27": m[max(0, cuoi[t] - (3 - k) // 2 * (i % 2))]} for i, t in enumerate(tt["hoc_sinh"])])
    kho._bay_gio = goc
    gb = kho.giao_bai_tao(db, e, ban, lop.id, "nhom", None)
    kq = lambda *d: [{"cau_so": i + 1, "dat": x, "diem_dat": 1 if x == "dung" else 0, "ghi_chu": ""} for i, x in enumerate(d)]
    for i in (3, 9, 14, 20, 27):  # vài em đã nộp sẵn
        kho.hs_nop_bai(db, gb["id"], tt["hoc_sinh"][i], nhom[i], [], kq("dung", "dung", "cho_cham"), 3, "", "cho_ai")
    dl = Path(db_path).with_suffix(".json")
    dl.write_text(json.dumps({"ten_gv": tt["ten_gv"], "truong": tt["truong"], "rows": rows,
                              "hs_demo": tt["hoc_sinh"][1]}, ensure_ascii=False), encoding="utf-8")
    return gb["ma"], dl


def cong_trong() -> int:
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close(); return p


def ffmpeg(*args):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args], check=True)


def slide_png(thu_muc: Path) -> list[Path]:
    """Chuyển Slide-du-thi.pptx (trong ban-nop/ hoặc du-thi/) sang ảnh 1920×1080."""
    nguon = next(p for p in (RA / "Slide-du-thi.pptx", DU_THI / "Slide-du-thi.pptx") if p.exists())
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(thu_muc), str(nguon)],
                   check=True, capture_output=True)
    pdf = thu_muc / "Slide-du-thi.pdf"
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(W), "-scale-to-y", str(H), str(pdf), str(thu_muc / "sl")], check=True)
    return sorted(thu_muc.glob("sl-*.png"))


def srt_gio(t: float) -> str:
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"


def phu_de() -> str:
    """Chia lời mỗi đoạn thành câu ngắn (≤ 14 chữ), chia đều thời lượng đoạn."""
    out, t0, so = [], 0.0, 1
    for _, dai, _, loi in KICH_BAN:
        tu = loi.split()
        cum = [" ".join(tu[i:i + 14]) for i in range(0, len(tu), 14)]
        for k, c in enumerate(cum):
            a, b = t0 + dai * k / len(cum), t0 + dai * (k + 1) / len(cum) - 0.1
            out.append(f"{so}\n{srt_gio(a)} --> {srt_gio(b)}\n{c}\n")
            so += 1
        t0 += dai
    return "\n".join(out)


@contextlib.contextmanager
def may_chu():
    """Chạy app với dữ liệu minh họa (database tạm, AI giả lập trả phiếu mẫu). Trả (URL, mã bài giao, thư mục tạm)."""
    global HS_DEMO
    tam = Path(tempfile.mkdtemp())
    db_path = tam / "demo.db"
    ma, dl = tao_du_lieu(str(db_path))
    HS_DEMO = json.loads(dl.read_text(encoding="utf-8"))["hs_demo"]
    harness = GOC / "_video_harness.py"
    harness.write_text(HARNESS.replace("__DB__", str(db_path)).replace("__DL__", str(dl)).replace("__MAU__", str(PHIEU_MAU)),
                       encoding="utf-8")
    secrets = GOC / ".streamlit" / "secrets.toml"
    sao_luu = secrets.read_bytes() if secrets.exists() else None
    secrets.write_text('APP_URL = "https://tro-ly-giang-day.streamlit.app"\nGEMINI_API_KEY = "khong-dung"\n', encoding="utf-8")
    port = cong_trong()
    sv = subprocess.Popen([PY, "-m", "streamlit", "run", str(harness), "--server.headless", "true", "--server.port", str(port),
                           "--client.toolbarMode", "viewer"], cwd=GOC, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(8)
        yield f"http://localhost:{port}", ma, tam
    finally:
        sv.terminate()
        harness.unlink(missing_ok=True)
        if sao_luu is None:
            secrets.unlink(missing_ok=True)
        else:
            secrets.write_bytes(sao_luu)


def main():
    RA.mkdir(exist_ok=True)
    DOAN.mkdir(exist_ok=True)
    with may_chu() as (U, ma, tam):
        anh_slide = slide_png(tam)
        with sync_playwright() as p:
            trinh_duyet = p.chromium.launch(channel="chrome")
            for ma_doan, dai, loai, _ in KICH_BAN:
                ra = DOAN / f"{ma_doan}.mp4"
                if loai.startswith("slide:"):
                    anh = anh_slide[int(loai.split(":")[1]) - 1]
                    ffmpeg("-loop", "1", "-t", str(dai), "-i", str(anh), "-vf", f"scale={W}:{H},format=yuv420p",
                           "-r", "30", "-c:v", "libx264", "-preset", "veryfast", str(ra))
                else:
                    quay(trinh_duyet, U, loai.split(":")[1], dai, ma, tam, ra)
                print("✓", ma_doan)
            trinh_duyet.close()
    # Ghép + phụ đề
    ds = tam / "ds.txt"
    ds.write_text("".join(f"file '{DOAN / f'{k[0]}.mp4'}'\n" for k in KICH_BAN), encoding="utf-8")
    (RA / "phu-de.srt").write_text(phu_de(), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(ds), "-c", "copy", str(tam / "ghep.mp4"))
    shutil.copy(RA / "phu-de.srt", tam / "pd.srt")
    os.chdir(tam)
    ffmpeg("-i", "ghep.mp4", "-vf", "subtitles=pd.srt:fontsdir=/usr/share/fonts/truetype/dejavu:force_style='FontName=DejaVu Sans,FontSize=11,PrimaryColour=&H00FFFFFF,"
           "BackColour=&H99000000,BorderStyle=4,Outline=0,MarginV=18'", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           str(RA / "video-nhap.mp4"))
    tong = sum(k[1] for k in KICH_BAN)
    print(f"Đã tạo {RA / 'video-nhap.mp4'} ({tong // 60}:{tong % 60:02d}), {RA / 'phu-de.srt'}, {DOAN}/")


def lam_bai(hs, ten, cho):
    """Học sinh chọn tên rồi làm lần lượt từng câu theo đáp án của phiếu mẫu, cuối cùng nộp bài."""
    import ai  # noqa: F401  (đường dẫn GOC đã thêm khi dựng dữ liệu)
    phieu = phieu_mau().phieu
    hs.get_by_text(ten, exact=True).click(); cho(2000)
    hs.get_by_role("button", name="Bắt đầu làm bài").click(); cho(3500)
    for _ in range(len(phieu.cau_hoi)):
        c = next((c for c in phieu.cau_hoi if hs.get_by_text(c.noi_dung.split("\n")[0][:30]).count()), None)
        if c and c.dang == "trac_nghiem":
            chu = c.dap_an.strip()[:1].upper()
            k = "ABCD".index(chu) if chu in "ABCD" else 0
            hs.get_by_role("radio").nth(k).check(force=True); cho(1200)
        elif c and c.dang == "dung_sai":
            for i, x in enumerate(re.findall(r"\b([ĐS])\b", c.dap_an)):
                hs.get_by_text("Đúng" if x == "Đ" else "Sai", exact=True).nth(i).click(); cho(700)
        elif c and c.dang == "dien_khuyet":
            for i, x in enumerate(c.dap_an.split(";")):
                o = hs.get_by_label(f"Chỗ trống {i + 1}")
                if o.count():
                    o.press_sequentially(x.strip(), delay=60)
            cho(800)
        elif c and c.dang == "tu_luan":
            dong = next((d for d in c.dap_an.splitlines() if "=" in d), c.dap_an.splitlines()[0])
            hs.get_by_role("textbox").first.press_sequentially(dong.strip(), delay=45); cho(800)
        nut = hs.get_by_role("button").filter(has_text="▶")
        if not nut.count():
            break
        nut.last.click(); cho(1800)
        if hs.get_by_role("button", name="📤 Nộp bài").count():
            break
    hs.get_by_role("button", name="📤 Nộp bài").click(); cho(5000)


def quay(trinh_duyet, U, canh, dai, ma, tam, ra):
    """Quay một cảnh app (1920×1080), cắt bỏ phần chờ tải, xuất mp4 đúng thời lượng."""
    ctx = trinh_duyet.new_context(viewport={"width": W, "height": H}, record_video_dir=str(tam / "webm"),
                                  record_video_size={"width": W, "height": H})
    bat_dau = time.monotonic()
    pg = ctx.new_page()

    def cho(ms):
        pg.wait_for_timeout(ms)

    def cuon_toi(chu):
        pg.get_by_text(chu).first.scroll_into_view_if_needed()

    if canh == "giaobai":  # màn hình chia đôi: giáo viên (trái) + điện thoại học sinh (phải)
        pg.set_content(f"""<body style="margin:0;background:#E9EEF6;display:flex;gap:40px;align-items:center;padding:20px 40px">
<iframe id="gv" src="{U}/giao_bai" style="width:1280px;height:1040px;border:0;border-radius:12px;background:#fff"></iframe>
<div style="width:430px;height:900px;border-radius:48px;background:#111;padding:28px 20px;box-shadow:0 20px 50px rgba(0,0,0,.35)">
<iframe id="hs" src="{U}/?ma={ma}" style="width:390px;height:844px;border:0;border-radius:28px;background:#fff"></iframe></div></body>""")
        cho(9000)
        moc = time.monotonic() - bat_dau
        hs = pg.frame_locator("#hs")
        cho(3000)
        lam_bai(hs, HS_DEMO, cho)
    else:
        url = {"soan": "/soan_phieu?kb=soan", "kiemdinh": "/soan_phieu", "inphieu": "/soan_phieu",
               "chambai": "/cham_bai", "tienbo": "/tien_bo"}[canh]
        pg.goto(U + url); cho(7000)
        moc = time.monotonic() - bat_dau
        if canh == "soan":
            cho(1500)
            o = pg.get_by_placeholder("VD: Phép cộng có nhớ trong phạm vi 100")
            o.click(); o.press_sequentially(CHU_DE, delay=60); o.press("Enter"); cho(1500)
            pg.get_by_role("button", name="🚀 Tạo phiếu bài tập").click(); cho(9500)
            cuon_toi("★ Mức 1"); cho(4000)
            pg.mouse.wheel(0, 700); cho(4000)
        elif canh == "kiemdinh":
            cuon_toi("Kiểm định AI"); cho(6000)
            if pg.get_by_text("🛠 Sửa theo góp ý").count():
                cuon_toi("🛠 Sửa theo góp ý"); cho(8000)
            else:  # phiếu đạt, không có góp ý: lướt xem các câu Mức 3
                cuon_toi("★★★ Mức 3"); cho(8000)
        elif canh == "inphieu":
            pg.get_by_role("tab", name="🖨️ In phiếu").click(); cho(3000)
            for nhom in ("Xanh", "Cam", "Tím"):
                pg.get_by_text(nhom, exact=True).first.click(); cho(4500)
        elif canh == "chambai":
            cuon_toi("② Sổ tổng hợp"); cho(7000)
            cuon_toi("③ Phân tích lỗi sai"); cho(9000)
            cuon_toi("Nội dung cần bổ trợ"); cho(9000)
        elif canh == "tienbo":
            cho(4000)
            cuon_toi("👤 Từng học sinh"); cho(8000)
    con = moc + dai - (time.monotonic() - bat_dau)
    if con > 0:
        cho(int(con * 1000))
    webm = pg.video.path()
    ctx.close()
    ffmpeg("-ss", f"{moc:.2f}", "-i", str(webm), "-t", str(dai), "-vf", f"scale={W}:{H},fps=30,format=yuv420p",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(ra))


if __name__ == "__main__":
    main()
