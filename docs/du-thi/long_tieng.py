"""Lồng tiếng AI (tiếng Việt) cho video nháp: đọc lời thuyết trình, căn phụ đề theo giọng đọc, ghép thành video ≤ 5 phút.

Cần chạy tao_video_nhap.py trước (để có ban-nop/doan-quay/*.mp4). Thể lệ không cấm lồng tiếng AI; video luôn ghi rõ
"Lồng tiếng: giọng đọc AI" để minh bạch.

Hai bộ đọc (chọn trong ban-nop/so-lieu.json, mục "may_doc"):
  - "gemini" (mặc định): Gemini TTS – giọng tự nhiên, chỉnh phong cách bằng mô tả. Cần GEMINI_API_KEY (biến môi trường
    hoặc .streamlit/secrets.toml trên máy). Gói miễn phí dùng được.
  - "edge": Microsoft Edge neural TTS (thư viện edge-tts) – không cần key nhưng nghe "máy" hơn. Tự dùng khi thiếu key.

Số liệu và thông tin giáo viên lấy từ ban-nop/so-lieu.json (tự tạo mẫu nếu chưa có). Ô nào để trống thì lời đọc dùng câu
chung, KHÔNG đọc số. Chạy:
    GEMINI_API_KEY=... .venv/bin/python docs/du-thi/long_tieng.py
Đầu ra (ban-nop/): video-long-tieng.mp4, loi-doc.mp3, phu-de-long-tieng.srt
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import tomllib
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tao_video_nhap import DOAN, FFMPEG, GOC, KICH_BAN, RA, ffmpeg, srt_gio  # noqa: E402

SO_LIEU = RA / "so-lieu.json"
MAU_SO_LIEU = {
    "may_doc": "gemini",                 # "gemini" (tự nhiên) hoặc "edge" (không cần key)
    "giong_gemini": "Sulafat",           # nữ ấm: Sulafat, Achernar, Vindemiatrix · nam: Achird, Charon, Sadaltager
    "phong_cach": ("Giọng cô giáo tiểu học người Việt, giọng chuẩn miền Bắc, ấm áp, tự nhiên, rõ ràng, tự tin, "
                   "tốc độ vừa phải, như đang thuyết trình trước hội đồng giám khảo."),
    "giong_edge": "vi-VN-HoaiMyNeural",  # giọng nam: vi-VN-NamMinhNeural
    "ho_ten": "", "truong": "", "dia_chi": "", "email": "", "lop": "", "si_so": "",
    "so_ngay": "", "so_hoc_sinh": "",
    "phut_soan_cu": "", "phut_soan_moi": "", "phut_cham_cu": "", "phut_cham_moi": "",
    "loi_kiem_dinh": "", "phan_tram_chua_dat_truoc": "", "phan_tram_chua_dat_sau": "",
    "phan_hoi": "",
}
MODEL_TTS = "gemini-3.8-flash-tts"
DOC_EDGE = [(r"\bAI\b", "ây ai"), (r"\bQR\b", "kiu a"), (r"Gemini", "Giê mi ni"), (r"chatbot", "chát bót")]  # phát âm cho edge-tts
GIOI_HAN = 298  # giây (thể lệ: tối đa 5 phút)
MINH_HOA = {"04-soan-phieu": r"Đã rút gọn\Nthời gian chờ AI"}  # nhãn góc trên trái, chỉ hiện trong đoạn tương ứng
CAT_DUOI = {"07-giao-bai": 23}  # giây cuối đoạn quay chỉ còn màn hình đứng yên sau khi nộp bài: cắt bỏ
TUA_TOI_DA = 1.8  # đoạn quay app dài hơn lời đọc: tua nhanh tối đa 1,8 lần để không có khoảng lặng dài
SR = 24000
DONG = 42                                   # ký tự tối đa mỗi dòng phụ đề, tối đa 2 dòng mỗi khung
GIU_NGUYEN = ["Thông tư 27", "Ban Giám khảo", "tổ trưởng chuyên môn", "Trợ Lý Giảng Dạy", "sách giáo khoa", "mã QR",
              "yêu cầu cần đạt", "máy tính bảng", "một nửa", "chưa đạt", "19 đến 23", "đáp án sai", "nhận xét học bạ", "chatbot AI", "bốn mươi phần trăm", "một buổi bổ trợ", "tháng 10", "ba mươi giây", "khối một", "khối năm", "ba mức", "thứ hai",
              "Xanh, Cam và Tím", "phiếu bài tập phân hóa", "soạn xong"]
# Từ ghép 2 âm tiết: không xuống dòng giữa từ (phụ đề tiếng Việt ngắt theo từ, không theo âm tiết)
TU_GHEP = ("học sinh", "giáo viên", "nhận xét", "đáp án", "công cụ", "bài tập", "phân hóa", "đánh giá", "tiểu học",
           "trình độ", "khác nhau", "vừa sức", "thời gian", "câu trả lời", "rời rạc", "kiểm tra", "khép kín", "kiểm định",
           "phân tích", "bổ trợ", "theo dõi", "tiến bộ", "học bạ", "đề xuất", "quyết định", "trình bày", "ma trận",
           "khác biệt", "đóng vai", "tự giải", "trung tính", "xếp loại", "tài khoản", "trắc nghiệm", "trực tiếp",
           "viết tay", "chụp ảnh", "quy tắc", "công khai", "biểu đồ", "nút bấm", "cuối kỳ", "gợi ý", "quá trình",
           "kết quả", "thí điểm", "mức độ", "sản phẩm", "hoàn toàn", "miễn phí", "trình duyệt", "trân trọng", "cảm ơn",
           "soạn phiếu", "giao bài", "nộp bài", "lệch mức", "chatbot AI")


def loi_doc(d: dict) -> dict[str, list[str]]:
    """Lời đọc từng đoạn (mỗi phần tử là một câu). Chỉ nói số liệu khi đã được điền."""
    co = lambda *k: all(str(d.get(x, "")).strip() for x in k)
    noi_day = ", ".join(x for x in (d["truong"], d["dia_chi"].replace("TP. ", "thành phố ")) if x.strip())
    gioi_thieu = (f"Tôi là {d['ho_ten'] + ', ' if co('ho_ten') else ''}giáo viên lớp {d['lop']}, {noi_day}."
                  if co("lop", "truong") else "")
    ket_qua = ([f"Sau {d['so_ngay']} ngày thí điểm với {d['so_hoc_sinh']} học sinh, thời gian soạn một phiếu giảm từ "
                f"{d['phut_soan_cu']} xuống {d['phut_soan_moi']} phút, thời gian chấm và nhận xét một lớp giảm từ "
                f"{d['phut_cham_cu']} xuống {d['phut_cham_moi']} phút.",
                f"Tỉ lệ học sinh chưa đạt giảm từ {d['phan_tram_chua_dat_truoc']} xuống "
                f"{d['phan_tram_chua_dat_sau']} phần trăm sau một buổi bổ trợ."]
               if co("so_ngay", "so_hoc_sinh", "phut_soan_cu", "phut_soan_moi", "phut_cham_cu", "phut_cham_moi",
                     "phan_tram_chua_dat_truoc", "phan_tram_chua_dat_sau")
               else [f"Tôi đang thí điểm từ ngày 19 đến 23 tháng 10 tại lớp {d['lop'] or 'mình'}, so sánh trước và sau trên cùng lớp.",
                     "Mục tiêu là giảm ít nhất một nửa thời gian soạn phiếu, giảm bốn mươi phần trăm thời gian chấm và nhận xét, "
                     "và giảm tỉ lệ học sinh chưa đạt sau một buổi bổ trợ."])
    if d.get("phan_hoi", "").strip():
        ket_qua.append(d["phan_hoi"].strip())
    return {
        "01-mo-dau": ["Xin chào Ban Giám khảo.", *([gioi_thieu] if gioi_thieu else []),
                      "Tôi xin giới thiệu Trợ Lý Giảng Dạy, công cụ AI giúp giáo viên tiểu học soạn phiếu bài tập phân hóa "
                      "và đánh giá học sinh theo Thông tư 27."],
        "02-boi-canh": [f"Lớp tôi có {d['si_so']} em, trình độ các em rất khác nhau." if co("si_so")
                        else "Học sinh lớp tôi có trình độ rất khác nhau.",
                        "Để mỗi em được làm bài vừa sức, tôi phải soạn phiếu ba mức, in cho từng nhóm, chấm và viết nhận xét cho từng em.",
                        f"Mỗi phiếu như vậy mất khoảng {d['phut_soan_cu']} phút." if co("phut_soan_cu") else "Việc này tốn rất nhiều thời gian.",
                        "Thử dùng chatbot AI thì câu trả lời rời rạc, không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra."],
        "03-giai-phap": ["Vì vậy, tôi xây dựng một vòng khép kín sáu bước: soạn phiếu, AI kiểm định, dạy và giao bài, chấm và nhận xét, "
                         "phân tích lỗi để bổ trợ, và theo dõi tiến bộ đến học bạ.",
                         "Ở mỗi bước, AI đề xuất, còn giáo viên là người quyết định."],
        "04-soan-phieu": ["Tôi chọn lớp, môn, nhập tên bài hoặc chụp trang sách giáo khoa.",
                          "Chưa đầy một phút, AI soạn xong phiếu ba mức theo Thông tư 27, đáp án trình bày đúng như vở của học sinh, "
                          "kèm ma trận và yêu cầu cần đạt."],
        "05-kiem-dinh": ["Điểm khác biệt là một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu để soát đáp án sai "
                         "và câu lệch mức.",
                         *([f"Trong thí điểm, nó đã phát hiện {d['loi_kiem_dinh']} lỗi."] if co("loi_kiem_dinh") else [])],
        "06-phan-hoa": ["Một phiếu tự tách thành ba phiếu Xanh, Cam và Tím cho ba nhóm.",
                        "Tên màu trung tính, nên các em không cảm thấy mình bị xếp loại."],
        "07-giao-bai": ["Trên lớp, tôi chiếu mã QR.",
                        "Các em quét mã bằng máy tính bảng hoặc điện thoại, chạm vào tên mình mà không cần tài khoản, và tự nhận đúng phiếu của nhóm.",
                        "Câu trắc nghiệm được chấm ngay, còn tôi theo dõi trực tiếp em nào đã nộp bài."],
        "08-cham-bai": ["Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27.",
                        "Mức đạt được tính theo quy tắc công khai, và tôi có thể sửa từng câu.",
                        "Biểu đồ cho thấy cả lớp còn yếu ở đâu, và chỉ một nút bấm là có phiếu bổ trợ đúng chỗ đó."],
        "09-tien-bo": ["Kết quả được lưu theo từng em.",
                       "Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, mà không cần gửi tên học sinh."],
        "10-ket-qua": ket_qua,
        "10b-so-sanh": ["So với chatbot AI phổ thông hay các nền tảng tạo đề và trắc nghiệm trực tuyến, điểm khác biệt là một vòng khép kín theo Thông tư 27.",
                        "Phiếu ba mức có AI kiểm định, phân nhóm không dán nhãn, chấm bài viết tay kèm nhận xét, "
                        "phân tích lỗi thành phiếu bổ trợ, và gợi ý nhận xét học bạ."],
        "11-trach-nhiem": ["Sản phẩm hoàn toàn miễn phí, chạy trên trình duyệt, dùng được cho khối một đến khối năm, bám sát bộ sách giáo khoa dùng chung toàn quốc.",
                           "Danh sách lớp không được gửi cho AI.", "Mọi đề, điểm và nhận xét đều do giáo viên duyệt."],
        "12-ket": ["Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em.",
                   "Xin trân trọng cảm ơn Ban Giám khảo."],
    }


# ---------------- Phụ đề ----------------
NBSP = " "


def _khoa(s: str) -> str:
    for c in (*GIU_NGUYEN, *TU_GHEP):
        s = re.sub(rf"(?<!\w){re.escape(c)}(?!\w)", c.replace(" ", NBSP), s)
    return s


def _chia_dong(khung: str) -> str:
    """Khung > 42 ký tự: xuống dòng ở khoảng trắng gần giữa, ưu tiên ngay sau dấu phẩy, không tách từ ghép."""
    if len(khung) <= DONG:
        return khung
    vi_tri = [m.start() for m in re.finditer(" ", khung) if max(m.start(), len(khung) - m.start() - 1) <= DONG]
    if not vi_tri:  # không chia được 2 dòng vừa khung: để libass tự xuống dòng
        return khung
    k = min(vi_tri, key=lambda i: abs(i - len(khung) / 2) - (12 if khung[i - 1] in ",:;" else 0))
    return khung[:k] + "\n" + khung[k + 1:]


def _chia_deu(menh: str) -> list[str]:
    """Mệnh đề dài hơn 2 dòng: chia thành các phần dài gần bằng nhau (tránh mẩu cụt ở cuối)."""
    n = -(-len(menh) // (2 * DONG))
    tu, phan, cur = menh.split(" "), [], ""
    for t in tu:
        if cur and len(phan) < n - 1 and len(cur) + len(t) + 1 > len(menh) / n:
            phan.append(cur)
            cur = t
        else:
            cur = f"{cur} {t}".strip()
    return [*phan, cur]


def _vua(khung: str) -> bool:
    return all(len(x) <= DONG for x in _chia_dong(khung).split("\n"))


def chia_khung(cau: str) -> list[str]:
    """Chia câu thành các khung phụ đề ≤ 2 dòng × 42 ký tự, ngắt ở dấu câu, gộp mẩu quá ngắn."""
    menh = re.split(r"(?<=[,:;]) ", _khoa(cau).strip())
    khung, cur = [], ""
    for m in menh:
        if _vua(f"{cur} {m}".strip()):
            cur = f"{cur} {m}".strip()
            continue
        if cur:
            khung.append(cur)
        *dau, cur = [m] if _vua(m) else _chia_deu(m)
        khung += dau
    khung.append(cur)
    return [_chia_dong(k).replace(NBSP, " ") for k in khung]


def khung_thoi_gian(cau: str, a: float, b: float) -> list[tuple[float, float, str]]:
    """Chia [a, b] cho các khung theo số ký tự (khớp nhịp đọc)."""
    khung = chia_khung(cau)
    tong = sum(len(k) for k in khung)
    out, t = [], a
    for k in khung:
        dai = (b - a) * len(k) / tong
        out.append((t, t + dai, k))
        t += dai
    return out


# ---------------- Đọc ----------------
def lang(giay: float) -> bytes:
    return b"\0\0" * int(max(giay, 0) * SR)


def pcm(tep: Path) -> bytes:
    """Giải mã mọi định dạng âm thanh → PCM 16-bit mono 24 kHz."""
    return subprocess.run([FFMPEG, "-loglevel", "error", "-i", str(tep), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                          check=True, capture_output=True).stdout


def cat_lang(am: bytes, nguong: int = 300) -> bytes:
    """Bỏ khoảng lặng đầu/cuối của đoạn âm thanh."""
    mau = memoryview(am).cast("h")
    dau = next((i for i, v in enumerate(mau) if abs(v) > nguong), 0)
    cuoi = next((i for i in range(len(mau) - 1, -1, -1) if abs(mau[i]) > nguong), len(mau) - 1)
    return am[max(dau - 1200, 0) * 2:(cuoi + 2400) * 2]


def key_gemini() -> str:
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    tep = GOC / ".streamlit" / "secrets.toml"
    if tep.exists():
        return tomllib.loads(tep.read_text(encoding="utf-8")).get("GEMINI_API_KEY", "")
    return ""


def doc_gemini(van_ban: str, d: dict, tam: Path, ten: str) -> bytes:
    """Gói miễn phí chỉ ~10 lượt/ngày/model: mỗi đoạn đã đọc được lưu lại (ban-nop/tts-cache), chạy lại không tốn lượt."""
    from google import genai
    from google.genai import types
    loi_nhac = f"{d['phong_cach']} Đọc nguyên văn đoạn sau:\n{van_ban}"
    kho = RA / "tts-cache" / (hashlib.sha1(f"{MODEL_TTS}|{d['giong_gemini']}|{loi_nhac}".encode()).hexdigest()[:16] + ".pcm")
    if kho.exists():
        return kho.read_bytes()
    client = genai.Client(api_key=key_gemini(), http_options=types.HttpOptions(timeout=120_000))
    cau_hinh = types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=types.SpeechConfig(
        language_code="vi-VN",
        voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=d["giong_gemini"]))))
    for lan in range(4):
        try:
            r = client.models.generate_content(model=MODEL_TTS, config=cau_hinh, contents=loi_nhac)
            break
        except Exception as e:  # noqa: BLE001
            if "PerDay" in str(e):
                raise SystemExit(f"Hết lượt Gemini TTS miễn phí trong ngày (đoạn {ten}). Các đoạn đã đọc được lưu lại; "
                                 "chạy lại sau khi hạn mức reset (khoảng 7 giờ sáng giờ Việt Nam) để đọc tiếp.")
            if lan == 3 or "429" not in str(e):
                raise
            print("  … quá giới hạn lượt/phút, chờ 30 giây")
            time.sleep(30)
    am = r.candidates[0].content.parts[0].inline_data.data
    if am[:4] == b"RIFF":
        tep = tam / f"{ten}.wav"
        tep.write_bytes(am)
        am = pcm(tep)
    am = cat_lang(am)  # PCM thô 24 kHz
    kho.parent.mkdir(exist_ok=True)
    kho.write_bytes(am)
    return am


def doc_edge(van_ban: str, d: dict, tam: Path, ten: str, toc_do: str) -> bytes:
    import edge_tts
    for mau, thay in DOC_EDGE:
        van_ban = re.sub(mau, thay, van_ban)
    tep = tam / f"{ten}.mp3"
    asyncio.run(edge_tts.Communicate(van_ban, d["giong_edge"], rate=toc_do).save(str(tep)))
    return cat_lang(pcm(tep))


def thoi_luong_clip(p: Path) -> float:
    ra = subprocess.run([FFMPEG, "-i", str(p)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", ra).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def doc_doan(ma: str, cau: list[str], d: dict, tam: Path, toc_do: str) -> tuple[bytes, list]:
    """Âm thanh 1 đoạn + mốc thời gian từng khung phụ đề (tính từ đầu đoạn)."""
    am, moc, t = lang(0.5), [], 0.5
    if d["may_doc"] == "gemini":  # 1 lượt gọi mỗi đoạn (tiết kiệm quota), chia thời gian câu theo số ký tự
        doc = doc_gemini(" ".join(cau), d, tam, ma)
        dai = len(doc) / 2 / SR
        tong = sum(len(c) for c in cau)
        for c in cau:
            phan = dai * len(c) / tong
            moc += khung_thoi_gian(c, t, t + phan)
            t += phan
        return am + doc + lang(0.5), moc
    for k, c in enumerate(cau):  # edge: đọc từng câu, mốc thời gian chính xác theo câu
        doc = doc_edge(c, d, tam, f"{ma}-{k}", toc_do)
        dai = len(doc) / 2 / SR
        moc += khung_thoi_gian(c, t, t + dai)
        am += doc + lang(0.3)
        t += dai + 0.3
    return am + lang(0.2), moc


PHU_DE_THAP = ("01-mo-dau", "10b-so-sanh")  # trang có nội dung sát đáy (thông tin GV, bảng): phụ đề xuống sát mép dưới


def ass(cues, tong, nhan, thap=()) -> str:
    g = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    # trang bìa: phụ đề xuống sát đáy (vùng trắng) để không che tên, email giáo viên
    dong = [f"Dialogue: 0,{g(a)},{g(b)},Default,,0,0,{30 if any(x <= a < y for x, y in thap) else 0},,{c.replace(chr(10), chr(92) + 'N')}"
            for a, b, c in cues]
    dong.append(f"Dialogue: 1,{g(0)},{g(tong)},Nhan,,0,0,0,,Lồng tiếng: giọng đọc AI")
    dong += [f"Dialogue: 1,{g(a)},{g(b)},Minh,,0,0,0,,{c}" for a, b, c in nhan]
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,DejaVu Sans,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H30000000,0,0,0,0,100,100,0,0,4,0,0,2,80,80,135,1\n"
            "Style: Nhan,DejaVu Sans,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H88000000,0,1,0,0,100,100,0,0,4,0,0,9,30,30,24,1\n"
            "Style: Minh,DejaVu Sans,28,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00A1470D,1,0,0,0,100,100,0,0,4,0,0,7,30,30,560,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(dong) + "\n")


def main():
    RA.mkdir(exist_ok=True)
    if not SO_LIEU.exists():
        SO_LIEU.write_text(json.dumps(MAU_SO_LIEU, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Đã tạo mẫu {SO_LIEU} – điền số liệu thật rồi chạy lại để lời đọc có số liệu.")
    d = {**MAU_SO_LIEU, **json.loads(SO_LIEU.read_text(encoding="utf-8"))}
    d["may_doc"] = os.environ.get("MAY_DOC", d["may_doc"])  # MAY_DOC=edge: dựng nhanh bản giọng edge, không tốn lượt Gemini
    if d["may_doc"] == "gemini" and not key_gemini():
        print("⚠ Chưa có GEMINI_API_KEY (biến môi trường hoặc .streamlit/secrets.toml trên máy) – tạm dùng giọng edge-tts.")
        d["may_doc"] = "edge"
    print(f"Bộ đọc: {d['may_doc']} ({d['giong_gemini'] if d['may_doc'] == 'gemini' else d['giong_edge']})")
    loi = loi_doc(d)
    GIU_NGUYEN.extend(x for x in (d["ho_ten"], d["truong"]) if x.strip())  # không ngắt dòng giữa tên riêng
    for cau in (c for ds in loi.values() for c in ds):  # tự kiểm: mọi dòng phụ đề ≤ 42 ký tự, không mất chữ
        khung = chia_khung(cau)
        assert all(len(x) <= DONG for k in khung for x in k.split("\n")), khung
        assert " ".join(khung).replace("\n", " ") == cau, khung
    tam = Path(tempfile.mkdtemp())
    clip = {ma: thoi_luong_clip(DOAN / f"{ma}.mp4") - CAT_DUOI.get(ma, 0) for ma, *_ in KICH_BAN}
    for toc in (0, 6, 12, 18):  # edge: tăng tốc độ đọc nếu vượt 5 phút (gemini: chỉnh trong phong_cach)
        doan = {}
        for ma, _, loai, _ in KICH_BAN:
            am, moc = doc_doan(ma, loi[ma], d, tam, f"+{toc}%")
            noi = len(am) / 2 / SR
            dai = max(noi + 0.8, clip[ma] / TUA_TOI_DA if loai.startswith("app") else 0)  # slide: vừa lời đọc
            doan[ma] = (am, moc, dai)
        tong = sum(v[2] for v in doan.values())
        print(f"Tổng thời lượng: {tong:.1f} giây")
        if tong <= GIOI_HAN or d["may_doc"] == "gemini":
            break
    if tong > GIOI_HAN:
        raise SystemExit("Lời đọc quá dài so với 5 phút – rút gọn lời trong loi_doc() hoặc yêu cầu đọc nhanh hơn trong phong_cach.")

    toan_bo, cues, t0, nhan, khoang = b"", [], 0.0, [], {}
    for ma, *_ in KICH_BAN:
        am, moc, L = doan[ma]
        toan_bo += am + lang(L - len(am) / 2 / SR)
        cues += [(t0 + a, t0 + b, c) for a, b, c in moc]
        if ma in MINH_HOA:
            nhan.append((t0, t0 + L, MINH_HOA[ma]))
        khoang[ma] = (t0, t0 + L)
        t0 += L
    with wave.open(str(tam / "loi.wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR), w.writeframes(toan_bo)
    ffmpeg("-i", str(tam / "loi.wav"), "-b:a", "128k", str(RA / "loi-doc.mp3"))
    (RA / "phu-de-long-tieng.srt").write_text(
        "\n".join(f"{k}\n{srt_gio(a)} --> {srt_gio(b)}\n{c}\n" for k, (a, b, c) in enumerate(cues, 1)), encoding="utf-8")
    (tam / "pd.ass").write_text(ass(cues, t0, nhan, [khoang[ma] for ma in PHU_DE_THAP if ma in khoang]), encoding="utf-8")

    ds = []
    for ma, _, loai, _ in KICH_BAN:  # hình: app tua nhanh cho vừa lời đọc, slide cắt bớt; thiếu thì giữ khung cuối
        L, ra = doan[ma][2], tam / f"{ma}.mp4"
        tua = min(L / clip[ma], 1) if loai.startswith("app") else 1
        ffmpeg("-i", str(DOAN / f"{ma}.mp4"), "-vf",
               f"setpts={tua:.4f}*PTS,tpad=stop_mode=clone:stop_duration={max(L - clip[ma] * tua, 0):.3f}",
               "-t", f"{L:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", str(ra))
        ds.append(f"file '{ra}'\n")
    (tam / "ds.txt").write_text("".join(ds), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(tam / "ds.txt"), "-c", "copy", str(tam / "hinh.mp4"))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", "hinh.mp4", "-i", "loi.wav",
                    "-vf", "ass=pd.ass:fontsdir=/usr/share/fonts/truetype/dejavu",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    str(RA / "video-long-tieng.mp4")], cwd=tam, check=True)
    print(f"Đã tạo {RA / 'video-long-tieng.mp4'} ({int(t0 // 60)}:{int(t0 % 60):02d}), loi-doc.mp3, phu-de-long-tieng.srt")


if __name__ == "__main__":
    main()
