"""Dựng VIDEO NHÁP (≤ 5 phút) theo kịch bản 04-kich-ban-video.md: ảnh slide + đoạn quay màn hình app + phụ đề.

Giáo viên dùng video này làm khung: thu giọng thuyết trình đè lên (hoặc ghép trong CapCut), thay đoạn
"Kết quả" bằng số liệu/cảnh lớp học thật, thêm hình giáo viên. KHÔNG nộp nguyên video nháp.

Chạy:   .venv/bin/python docs/du-thi/tao_video_nhap.py
Cần:    Chrome, playwright, imageio-ffmpeg, LibreOffice (để chuyển slide sang ảnh)
Đầu ra (thư mục ban-nop/, không đưa lên GitHub):
  - video-nhap.mp4         video nháp có phụ đề
  - phu-de.srt             phụ đề (nhập vào CapCut nếu dựng lại)
  - doan-quay/*.mp4        từng đoạn quay màn hình sạch (không phụ đề) để ghép tự do

Dữ liệu trong video là dữ liệu giả (tên học sinh giả). Đoạn soạn phiếu dùng AI giả lập trả phiếu mẫu
(máy dựng video không có API key) và được ghi rõ "minh họa" trên phụ đề.
"""
import json
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
    ("07-giao-bai", 35, "app:giaobai", "Trên lớp, tôi chiếu mã QR. Các em quét bằng máy tính bảng, chạm vào tên mình, không cần tài khoản, "
     "và tự nhận đúng phiếu của nhóm. Câu trắc nghiệm được chấm ngay. Tôi theo dõi trực tiếp em nào đã nộp."),
    ("08-cham-bai", 30, "app:chambai", "Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27; mức đạt tính theo quy tắc công khai "
     "và tôi sửa được từng câu. Biểu đồ cho thấy cả lớp còn yếu ở đâu – một nút bấm là có phiếu bổ trợ đúng chỗ đó."),
    ("09-tien-bo", 15, "app:tienbo", "Kết quả được lưu theo từng em. Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, không cần gửi tên học sinh."),
    ("10-ket-qua", 33, "slide:12", "Sau ⟦…⟧ ngày thí điểm với ⟦…⟧ học sinh: thời gian soạn phiếu giảm từ ⟦…⟧ xuống ⟦…⟧ phút, chấm và nhận xét "
     "từ ⟦…⟧ xuống ⟦…⟧ phút; tỉ lệ chưa đạt ở câu yếu giảm từ ⟦…⟧ xuống ⟦…⟧ sau một buổi bổ trợ. (Thay bằng số liệu và cảnh lớp học thật.)"),
    ("11-trach-nhiem", 20, "slide:10", "Sản phẩm miễn phí, chạy trên trình duyệt, dùng cho khối 1 đến 5 và cả ba bộ sách. Tên học sinh không được gửi cho AI; "
     "mọi đề, điểm và nhận xét đều do giáo viên duyệt."),
    ("12-ket", 13, "slide:14", "Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em. "
     "Xin cảm ơn Ban Giám khảo!"),
]

HARNESS = r'''
# Tệp tạm do tao_video_nhap.py sinh ra – dựng dữ liệu giả để quay màn hình
import time
import streamlit as st
from sqlalchemy import create_engine
import ai, state
DB = create_engine("sqlite:///__DB__")
state.email, state.co_db, state.db = (lambda: "co.lan@truong.vn"), (lambda: True), (lambda: DB)
state.tu_luu = lambda: None
MAU = ai.BanLuu.model_validate_json(open("mau/phieu_mau.json", encoding="utf-8").read())
def _tao(client, model, ts, dang, anh, ghi_chu=""):
    time.sleep(4); return MAU.phieu.model_copy(deep=True)
def _kd(client, model, ts, phieu):
    time.sleep(3); return MAU.kiem_dinh
ai.tao_phieu, ai.kiem_dinh = _tao, _kd
che_do = st.query_params.get("kb", "")
if "khoi_tao" not in st.session_state and not st.query_params.get("ma"):
    st.session_state.khoi_tao = True
    st.session_state.ho_so = {"lop_mac_dinh": 2, "mon_mac_dinh": "Toán"}
    if che_do != "soan":
        state.dat_phieu(MAU.model_copy(deep=True))
    o = [["✓","✓","✓","✓","✓","✓","½ chưa nêu quy luật"],["✓","✗ quên nhớ 1","✓","½ thiếu đáp số","✓","✗ nhầm ít hơn thành trừ","–"],
         ["✓","✗ quên nhớ 1","½","✗","✗","–","–"],["✓","✓","✓","✓","✓","✗ nhầm ít hơn thành trừ","✓"],
         ["✗","✗ quên nhớ 1","✓","½ thiếu đáp số","✓","✗ nhầm ít hơn thành trừ","–"],["✓","✓","✓","✓","½","½ thiếu bước tìm số của Hà","✓"],
         ["✓","✓","✓","✓","✓","✗ nhầm ít hơn thành trừ","½"],["✓","✗ quên nhớ 1","✓","✓","✓","✓","✓"]]
    ten = ["Nguyễn Minh An","Lê Gia Bình","Trần Bảo Chi","Phạm Đức Duy","Hoàng Thu Hà","Vũ Khánh Linh","Đỗ Gia Huy","Bùi Ngọc Mai"]
    muc = ["Hoàn thành tốt","Hoàn thành","Chưa hoàn thành","Hoàn thành tốt","Hoàn thành","Hoàn thành tốt","Hoàn thành","Hoàn thành"]
    nx = ["Em tính nhanh, trình bày rõ ràng.","Em cần đọc kỹ đề bài toán có lời văn.","Em cần luyện thêm phép cộng có nhớ.",
          "Em làm bài cẩn thận, chính xác.","Em chú ý dạng toán ít hơn.","Em trình bày đủ các bước giải nhé.","Em đọc kỹ câu hỏi nhé.","Em nhớ thêm 1 khi cộng có nhớ."]
    st.session_state.cham = {"ver": 1, "loi": [], "cau": MAU.phieu.cau_hoi, "ts": MAU.thong_so, "loai": "Phiếu chung",
        "rows": [{"STT": k + 1, "Họ tên": t, "Điểm": [9.5,6,3.5,9,5.5,8.5,7,7.5][k], "Mức TT27": muc[k], "Nhận xét": nx[k],
                  **{f"Câu {j + 1}": o[k][j] for j in range(7)}, "Ảnh": f"bai_{k + 1}.jpg"} for k, t in enumerate(ten)]}
exec(open("app.py", encoding="utf-8").read())
'''


def tao_du_lieu(db_path: str) -> str:
    """Dữ liệu giả: hồ sơ, 5 phiếu, lớp 2A (8 em), 4 lần chấm, 1 bài giao online. Trả mã bài."""
    sys.path.insert(0, str(GOC))
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import create_engine

    import ai
    import kho
    db, e = create_engine(f"sqlite:///{db_path}"), "co.lan@truong.vn"
    kho.tao_bang(db)
    ban = ai.BanLuu.model_validate_json((GOC / "mau/phieu_mau.json").read_text(encoding="utf-8"))
    kho.ho_so_luu(db, e, ten="Nguyễn Thị Lan", truong="Tiểu học Hoa Sen")
    for cd, mon in [("Bài toán về nhiều hơn, ít hơn", "Toán"), ("Cây xanh quanh em", "Tự nhiên và Xã hội"),
                    ("Đọc hiểu: Chuyện quả bầu", "Tiếng Việt"), ("Phép cộng có nhớ trong phạm vi 100", "Toán")]:
        b = ban.model_copy(deep=True)
        b.thong_so.chu_de, b.thong_so.mon = cd, mon
        kho.phieu_luu(db, e, b)
    ten = [("Nguyễn Minh An", "Xanh"), ("Lê Gia Bình", "Cam"), ("Trần Bảo Chi", "Xanh"), ("Phạm Đức Duy", "Tím"),
           ("Hoàng Thu Hà", "Cam"), ("Vũ Khánh Linh", "Tím"), ("Đỗ Gia Huy", "Cam"), ("Bùi Ngọc Mai", "Cam")]
    lop = ai.LopHoc(ten_lop="2A", hoc_sinh=[ai.HocSinh(stt=k + 1, ten=t, nhom=n) for k, (t, n) in enumerate(ten)])
    kho.lop_luu(db, e, lop)
    m = ["Chưa hoàn thành", "Hoàn thành", "Hoàn thành tốt"]
    tien = [[0, 1, 1, 2], [1, 1, 2, 2], [0, 0, 1, 1], [2, 2, 2, 2], [1, 1, 1, 2], [1, 2, 2, 2], [1, 1, 1, 1], [0, 1, 1, 1]]
    goc = kho._bay_gio
    for k, cd in enumerate(["Phép cộng có nhớ", "Phép trừ có nhớ", "Bài toán nhiều hơn", "Ôn tập cuối tháng"]):
        kho._bay_gio = lambda k=k: datetime(2026, 9, 21, 2, tzinfo=timezone.utc) + timedelta(days=7 * k)
        kho.cham_luu(db, e, lop.id, "Toán", cd, "Phiếu chung",
                     [{"ten": t, "diem": 4 + 2.5 * tien[i][k], "muc_tt27": m[tien[i][k]], "nhan_xet": "..."} for i, (t, _) in enumerate(ten)])
    kho._bay_gio = goc
    gb = kho.giao_bai_tao(db, e, ban, lop.id, "nhom", None)
    kq = lambda *d: [{"cau_so": i + 1, "dat": x, "diem_dat": 1 if x == "dung" else 0, "ghi_chu": ""} for i, x in enumerate(d)]
    for t, p, d in [("Phạm Đức Duy", "Tím", ("dung", "dung", "dung")), ("Bùi Ngọc Mai", "Cam", ("dung", "dung", "dung")),
                    ("Hoàng Thu Hà", "Cam", ("dung", "sai", "cho_cham"))]:
        kho.hs_nop_bai(db, gb["id"], t, p, [], kq(*d), 3, "", "cho_ai")
    return gb["ma"]


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


def main():
    RA.mkdir(exist_ok=True)
    DOAN.mkdir(exist_ok=True)
    tam = Path(tempfile.mkdtemp())
    db_path = tam / "demo.db"
    ma = tao_du_lieu(str(db_path))
    harness = GOC / "_video_harness.py"
    harness.write_text(HARNESS.replace("__DB__", str(db_path)), encoding="utf-8")
    secrets = GOC / ".streamlit" / "secrets.toml"
    sao_luu = secrets.read_bytes() if secrets.exists() else None
    secrets.write_text('APP_URL = "https://tro-ly-giang-day.streamlit.app"\nGEMINI_API_KEY = "khong-dung"\n', encoding="utf-8")
    port = cong_trong()
    sv = subprocess.Popen([PY, "-m", "streamlit", "run", str(harness), "--server.headless", "true", "--server.port", str(port),
                           "--client.toolbarMode", "viewer"], cwd=GOC, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    U = f"http://localhost:{port}"
    try:
        time.sleep(8)
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
    finally:
        sv.terminate()
        harness.unlink(missing_ok=True)
        if sao_luu is None:
            secrets.unlink(missing_ok=True)
        else:
            secrets.write_bytes(sao_luu)
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
        hs.get_by_text("Lê Gia Bình", exact=True).click(); cho(2500)
        hs.get_by_role("button", name="Bắt đầu làm bài").click(); cho(4000)
        tiep = lambda: hs.get_by_role("button").filter(has_text="▶").last.click()
        hs.get_by_role("textbox").first.press_sequentially("28 + 17 = 45 (bạn)", delay=70); cho(1000); tiep(); cho(2500)
        for k, chon in enumerate(["Đúng", "Sai", "Đúng"]):  # câu đúng/sai: a) Đ, b) S, c) Đ
            hs.get_by_text(chon, exact=True).nth(k).click(); cho(900)
        tiep(); cho(2000); tiep(); cho(2500)
        hs.get_by_role("button", name="📤 Nộp bài").click(); cho(6000)
    else:
        url = {"soan": "/soan_phieu?kb=soan", "kiemdinh": "/soan_phieu", "inphieu": "/soan_phieu",
               "chambai": "/cham_bai", "tienbo": "/tien_bo"}[canh]
        pg.goto(U + url); cho(7000)
        moc = time.monotonic() - bat_dau
        if canh == "soan":
            cho(1500)
            o = pg.get_by_placeholder("VD: Phép cộng có nhớ trong phạm vi 100")
            o.click(); o.press_sequentially("Phép cộng có nhớ trong phạm vi 100", delay=60); o.press("Enter"); cho(1500)
            pg.get_by_role("button", name="🚀 Tạo phiếu bài tập").click(); cho(9500)
            cuon_toi("★ Mức 1"); cho(4000)
            pg.mouse.wheel(0, 700); cho(4000)
        elif canh == "kiemdinh":
            cuon_toi("Kiểm định AI"); cho(5000)
            cuon_toi("🛠 Sửa theo góp ý"); cho(9000)
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
