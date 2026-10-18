"""Lồng tiếng AI (tiếng Việt) cho video nháp: đọc lời thuyết trình, căn phụ đề theo giọng đọc, ghép thành video ≤ 5 phút.

Cần chạy tao_video_nhap.py trước (để có ban-nop/doan-quay/*.mp4). Giọng đọc: Microsoft Edge neural TTS (thư viện edge-tts,
cần mạng). Thể lệ không cấm lồng tiếng AI; video vẫn ghi rõ "Lồng tiếng: giọng đọc AI" để minh bạch.

Số liệu và thông tin giáo viên lấy từ ban-nop/so-lieu.json (tự tạo mẫu nếu chưa có). Ô nào để trống thì lời đọc dùng câu
chung, KHÔNG đọc số. Điền số liệu thật rồi chạy lại:
    .venv/bin/python docs/du-thi/long_tieng.py
Đầu ra (ban-nop/): video-long-tieng.mp4, loi-doc.mp3, phu-de-long-tieng.srt
"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import edge_tts

sys.path.insert(0, str(Path(__file__).parent))
from tao_video_nhap import DOAN, FFMPEG, KICH_BAN, RA, ffmpeg, srt_gio  # noqa: E402

SO_LIEU = RA / "so-lieu.json"
MAU_SO_LIEU = {
    "giong": "vi-VN-HoaiMyNeural",  # giọng nữ; giọng nam: vi-VN-NamMinhNeural
    "ho_ten": "", "truong": "", "lop": "", "si_so": "",
    "so_ngay": "", "so_hoc_sinh": "",
    "phut_soan_cu": "", "phut_soan_moi": "", "phut_cham_cu": "", "phut_cham_moi": "",
    "loi_kiem_dinh": "", "phan_tram_chua_dat_truoc": "", "phan_tram_chua_dat_sau": "",
    "phan_hoi": "",
}
DOC = [(r"\bAI\b", "ây ai"), (r"\bQR\b", "kiu a"), (r"Gemini", "Giê mi ni")]  # cách phát âm
GIOI_HAN = 298  # giây (thể lệ: tối đa 5 phút)
MINH_HOA = {"04-soan-phieu": "Minh họa giao diện – phiếu mẫu (quay lại bằng AI thật trước khi nộp)",
            "10-ket-qua": "Chờ số liệu thí điểm thật"}  # nhãn góc trên trái, chỉ hiện trong đoạn tương ứng
SR = 24000


def loi_doc(d: dict) -> dict[str, list[str]]:
    """Lời đọc từng đoạn (mỗi phần tử là một câu). Chỉ nói số liệu khi đã được điền."""
    co = lambda *k: all(str(d.get(x, "")).strip() for x in k)
    gioi_thieu = (f"Tôi là {d['ho_ten']}, giáo viên lớp {d['lop']}, {d['truong']}." if co("ho_ten", "lop", "truong") else "")
    ket_qua = ([f"Sau {d['so_ngay']} ngày thí điểm với {d['so_hoc_sinh']} học sinh, thời gian soạn một phiếu giảm từ "
                f"{d['phut_soan_cu']} xuống {d['phut_soan_moi']} phút, thời gian chấm và nhận xét một lớp giảm từ "
                f"{d['phut_cham_cu']} xuống {d['phut_cham_moi']} phút.",
                f"Ở các câu yếu, tỉ lệ học sinh chưa đạt giảm từ {d['phan_tram_chua_dat_truoc']} xuống "
                f"{d['phan_tram_chua_dat_sau']} phần trăm sau một buổi bổ trợ."]
               if co("so_ngay", "so_hoc_sinh", "phut_soan_cu", "phut_soan_moi", "phut_cham_cu", "phut_cham_moi",
                     "phan_tram_chua_dat_truoc", "phan_tram_chua_dat_sau")
               else ["Kết quả thí điểm gồm thời gian soạn phiếu, thời gian chấm và nhận xét, và mức độ tiến bộ của học sinh "
                     "sau khi được bổ trợ."])
    if d.get("phan_hoi", "").strip():
        ket_qua.append(d["phan_hoi"].strip())
    return {
        "01-mo-dau": ["Xin chào Ban Giám khảo.", *([gioi_thieu] if gioi_thieu else []),
                      "Tôi xin giới thiệu Trợ Lý Giảng Dạy, công cụ AI giúp giáo viên tiểu học soạn phiếu bài tập phân hóa "
                      "và đánh giá học sinh theo Thông tư 27."],
        "02-boi-canh": [f"Lớp tôi {'có ' + d['si_so'] + ' em, ' if co('si_so') else ''}trình độ các em rất khác nhau.",
                        "Để mỗi em được làm bài vừa sức, tôi phải soạn phiếu ba mức, in cho từng nhóm, chấm và viết nhận xét cho từng em.",
                        f"Mỗi phiếu như vậy mất khoảng {d['phut_soan_cu']} phút." if co("phut_soan_cu") else "Việc này tốn rất nhiều thời gian.",
                        "Thử dùng chatbot AI thì câu trả lời rời rạc, không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra."],
        "03-giai-phap": ["Vì vậy tôi xây dựng một vòng khép kín sáu bước: soạn phiếu, AI kiểm định, dạy và giao bài, chấm và nhận xét, "
                         "phân tích lỗi để bổ trợ, và theo dõi tiến bộ đến học bạ.",
                         "Ở mỗi bước, AI đề xuất, còn giáo viên là người quyết định."],
        "04-soan-phieu": ["Tôi chọn lớp, môn, nhập tên bài hoặc chụp trang sách giáo khoa.",
                          "Chỉ khoảng ba mươi giây, AI soạn xong phiếu ba mức theo Thông tư 27, đáp án trình bày đúng như vở của học sinh, "
                          "kèm ma trận và yêu cầu cần đạt."],
        "05-kiem-dinh": ["Điểm khác biệt là một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu để soát đáp án sai "
                         "và câu lệch mức.",
                         *([f"Trong thí điểm, nó đã phát hiện {d['loi_kiem_dinh']} lỗi."] if co("loi_kiem_dinh") else [])],
        "06-phan-hoa": ["Một phiếu tự tách thành ba phiếu Xanh, Cam và Tím cho ba nhóm.",
                        "Tên màu trung tính, nên các em không cảm thấy mình bị xếp loại."],
        "07-giao-bai": ["Trên lớp, tôi chiếu mã QR.",
                        "Các em quét bằng máy tính bảng, chạm vào tên mình mà không cần tài khoản, và tự nhận đúng phiếu của nhóm.",
                        "Câu trắc nghiệm được chấm ngay, còn tôi theo dõi trực tiếp em nào đã nộp bài."],
        "08-cham-bai": ["Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27.",
                        "Mức đạt được tính theo quy tắc công khai, và tôi có thể sửa từng câu.",
                        "Biểu đồ cho thấy cả lớp còn yếu ở đâu, và chỉ một nút bấm là có phiếu bổ trợ đúng chỗ đó."],
        "09-tien-bo": ["Kết quả được lưu theo từng em.",
                       "Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, mà không cần gửi tên học sinh."],
        "10-ket-qua": ket_qua,
        "11-trach-nhiem": ["Sản phẩm hoàn toàn miễn phí, chạy trên trình duyệt, dùng được cho khối một đến khối năm và cả ba bộ sách giáo khoa.",
                           "Tên học sinh không được gửi cho AI, và mọi đề, điểm, nhận xét đều do giáo viên duyệt."],
        "12-ket": ["Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em.",
                   "Xin trân trọng cảm ơn Ban Giám khảo."],
    }


def phat_am(cau: str) -> str:
    for mau, thay in DOC:
        cau = re.sub(mau, thay, cau)
    return cau


async def doc_cau(cau: str, giong: str, toc_do: str, ra: Path):
    await edge_tts.Communicate(phat_am(cau), giong, rate=toc_do).save(str(ra))


def wav(mp3: Path) -> bytes:
    """Giải mã mp3 → PCM 16-bit mono 24 kHz."""
    return subprocess.run([FFMPEG, "-loglevel", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                          check=True, capture_output=True).stdout


def lang(giay: float) -> bytes:
    return b"\0\0" * int(giay * SR)


def thoi_luong_clip(p: Path) -> float:
    ra = subprocess.run([FFMPEG, "-i", str(p)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", ra).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def chia_dong(cau: str, so_tu: int = 14) -> list[str]:
    tu = cau.split()
    return [" ".join(tu[i:i + so_tu]) for i in range(0, len(tu), so_tu)]


def ass(cues: list[tuple[float, float, str]], tong: float, nhan: list[tuple[float, float, str]]) -> str:
    g = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    dong = [f"Dialogue: 0,{g(a)},{g(b)},Default,,0,0,0,,{c}" for a, b, c in cues]
    dong.append(f"Dialogue: 1,{g(0)},{g(tong)},Nhan,,0,0,0,,Lồng tiếng: giọng đọc AI")
    dong += [f"Dialogue: 1,{g(a)},{g(b)},Minh,,0,0,0,,{c}" for a, b, c in nhan]
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,4,0,0,2,80,80,40,1\n"
            "Style: Nhan,DejaVu Sans,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H88000000,0,1,0,0,100,100,0,0,4,0,0,9,30,30,24,1\n"
            "Style: Minh,DejaVu Sans,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00A1470D,1,0,0,0,100,100,0,0,4,0,0,7,40,40,90,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(dong) + "\n")


def main():
    RA.mkdir(exist_ok=True)
    if not SO_LIEU.exists():
        SO_LIEU.write_text(json.dumps(MAU_SO_LIEU, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Đã tạo mẫu {SO_LIEU} – điền số liệu thật rồi chạy lại để lời đọc có số liệu.")
    d = {**MAU_SO_LIEU, **json.loads(SO_LIEU.read_text(encoding="utf-8"))}
    loi = loi_doc(d)
    tam = Path(tempfile.mkdtemp())
    clip = {ma: thoi_luong_clip(DOAN / f"{ma}.mp4") for ma, *_ in KICH_BAN}
    for toc in (0, 5, 10, 15, 20):  # tăng tốc độ đọc nếu tổng thời lượng vượt 5 phút
        toc_do = f"+{toc}%"
        doan = {}
        for ma, *_ in KICH_BAN:
            am, moc, t = lang(0.4), [], 0.4
            for k, cau in enumerate(loi[ma]):
                mp3 = tam / f"{ma}-{k}.mp3"
                asyncio.run(doc_cau(cau, d["giong"], toc_do, mp3))
                pcm = wav(mp3)
                dai = len(pcm) / 2 / SR
                moc.append((t, t + dai, cau))
                am += pcm + lang(0.35)
                t += dai + 0.35
            doan[ma] = (am, moc, max(clip[ma], t + 0.4))
        tong = sum(v[2] for v in doan.values())
        print(f"Tốc độ đọc {toc_do}: tổng {tong:.1f} giây")
        if tong <= GIOI_HAN:
            break
    else:
        raise SystemExit("Lời đọc quá dài so với 5 phút – hãy rút gọn lời trong loi_doc().")

    # Âm thanh + phụ đề toàn bài
    toan_bo, cues, t0, nhan = b"", [], 0.0, []
    for ma, *_ in KICH_BAN:
        am, moc, L = doan[ma]
        if ma in MINH_HOA:
            nhan.append((t0, t0 + L, MINH_HOA[ma]))
        toan_bo += am + lang(L - len(am) / 2 / SR)
        for a, b, cau in moc:
            phan = chia_dong(cau)
            for k, p in enumerate(phan):
                cues.append((t0 + a + (b - a) * k / len(phan), t0 + a + (b - a) * (k + 1) / len(phan), p))
        t0 += L
    with wave.open(str(tam / "loi.wav"), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR), w.writeframes(toan_bo)
    ffmpeg("-i", str(tam / "loi.wav"), "-b:a", "128k", str(RA / "loi-doc.mp3"))
    (RA / "phu-de-long-tieng.srt").write_text(
        "\n".join(f"{k}\n{srt_gio(a)} --> {srt_gio(b)}\n{c}\n" for k, (a, b, c) in enumerate(cues, 1)), encoding="utf-8")
    (tam / "pd.ass").write_text(ass(cues, t0, nhan), encoding="utf-8")

    # Hình: kéo dài khung cuối mỗi đoạn cho vừa lời đọc, ghép, chèn phụ đề và tiếng
    ds = []
    for ma, *_ in KICH_BAN:
        them = doan[ma][2] - clip[ma]
        ra = tam / f"{ma}.mp4"
        ffmpeg("-i", str(DOAN / f"{ma}.mp4"), "-vf", f"tpad=stop_mode=clone:stop_duration={max(them, 0):.3f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", str(ra))
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
