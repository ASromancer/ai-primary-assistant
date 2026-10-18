"""Tạo MÃ DÙNG THỬ cho Ban Giám khảo + mã QR, và (tuỳ chọn) mã QR cho link video.

Chạy:   .venv/bin/python docs/du-thi/tao_ma_demo.py                     # tạo (hoặc in lại) mã dùng thử
        .venv/bin/python docs/du-thi/tao_ma_demo.py --video <link-drive> # thêm QR video
Kết quả nằm trong docs/du-thi/ban-nop/ (KHÔNG đưa lên GitHub vì repo công khai):
  ma-demo.txt, qr-trai-nghiem.png, link-video.txt, qr-video.png
Sau đó chạy lại dien_mau.py để chèn link và QR vào slide, poster.
"""
import secrets
import sys
from pathlib import Path

import segno

APP = "https://tro-ly-giang-day.streamlit.app"
RA = Path(__file__).parent / "ban-nop"


def main():
    RA.mkdir(exist_ok=True)
    tep = RA / "ma-demo.txt"
    if not tep.exists():
        tep.write_text("gk" + secrets.token_hex(5) + "\n", encoding="utf-8")
    ma = tep.read_text(encoding="utf-8").strip()
    link = f"{APP}/?demo={ma}"
    segno.make(link, error="h").save(RA / "qr-trai-nghiem.png", scale=20, border=2)
    print(f"Link dùng thử: {link}")
    print(f'→ Thêm vào Secrets của app trên Streamlit Cloud:  MA_DEMO = "{ma}"  rồi Reboot app.')
    if "--video" in sys.argv:
        video = sys.argv[sys.argv.index("--video") + 1]
        (RA / "link-video.txt").write_text(video + "\n", encoding="utf-8")
        segno.make(video, error="h").save(RA / "qr-video.png", scale=20, border=2)
        print(f"Đã tạo QR video: {video}")


if __name__ == "__main__":
    main()
