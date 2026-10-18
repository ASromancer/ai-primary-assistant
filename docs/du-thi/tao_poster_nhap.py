"""Tạo poster-nhap.pdf: bản nháp bố cục poster A0 dọc (841 × 1189 mm) để hình dung và copy nội dung.

Chạy: .venv/bin/python docs/du-thi/tao_poster_nhap.py   (cần Chrome + playwright)
Bố cục chính thức theo mẫu của Ban Tổ chức. Chỗ ⟦…⟧ là thông tin/số liệu thật cần điền.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

THU_MUC = Path(__file__).parent.resolve()
ANH = THU_MUC / "anh"


def anh(ten: str) -> str:
    duong = ANH / ten
    return duong.as_uri() if duong.exists() else ""


def qr(ten: str, nhan: str) -> str:
    src = anh(ten)
    o = f'<img src="{src}">' if src else '<div class="qr-trong">⟦tạo mã QR⟧</div>'
    return f'<div class="qr">{o}<b>{nhan}</b></div>'


ANH_DEMO = [("02-soan-phieu-kiem-dinh.png", "① Soạn phiếu 3 mức từ tên bài hoặc ảnh SGK"),
            ("03-gop-y-kiem-dinh.png", "② AI kiểm định tự giải lại, soát đáp án sai"),
            ("31-phieu-xanh.png", "③ Phiếu Xanh/Cam/Tím – phân hóa không dán nhãn"),
            ("21-hs-lam-cau.png", "③ Học sinh quét QR, chọn tên, làm bài"),
            ("10-phan-tich-loi-sai.png", "⑤ Phân tích lỗi → phiếu bổ trợ"),
            ("12-tien-bo-bieu-do.png", "⑥ Tiến bộ từng em, gợi ý nhận xét học bạ")]

HTML = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&display=swap">
<style>
@page {{ size: 841mm 1189mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: 841mm; height: 1189mm; font-family: "Be Vietnam Pro", sans-serif; color: #1A1A1A; background: #F4F8FD; }}
.dau {{ background: linear-gradient(120deg, #0D47A1, #1E88E5 60%, #42A5F5); color: #fff; padding: 26mm 40mm 20mm; }}
.dau h1 {{ font-size: 130pt; font-weight: 800; letter-spacing: 2pt; line-height: 1; }}
.dau h2 {{ font-size: 54pt; font-weight: 600; margin-top: 10mm; line-height: 1.25; }}
.dau p {{ font-size: 36pt; margin-top: 10mm; opacity: .92; }}
.than {{ padding: 12mm 30mm; display: grid; gap: 10mm; }}
.hang {{ display: grid; gap: 10mm; }}
.khoi {{ background: #fff; border-radius: 10mm; padding: 10mm 14mm; box-shadow: 0 2mm 6mm rgba(13,71,161,.08); }}
.khoi h3 {{ font-size: 48pt; color: #0D47A1; margin-bottom: 6mm; }}
.khoi li {{ font-size: 30pt; line-height: 1.45; margin: 0 0 4mm 12mm; }}
.khoi p.cc {{ font-size: 28pt; color: #444; font-style: italic; margin-top: 6mm; }}
.sodo {{ display: block; width: 100%; height: 255mm; object-fit: contain; }}
.luoi {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10mm; }}
.luoi figure {{ background: #F4F8FD; border-radius: 6mm; padding: 6mm; }}
.luoi img {{ width: 100%; height: 95mm; object-fit: contain; background: #fff; border-radius: 4mm; }}
.luoi figcaption {{ font-size: 26pt; font-weight: 600; margin-top: 4mm; text-align: center; }}
table {{ width: 100%; border-collapse: collapse; font-size: 28pt; }}
td, th {{ border-bottom: 1mm solid #E3EAF4; padding: 5mm 4mm; text-align: left; }}
th {{ color: #0D47A1; }}
.chan {{ display: flex; justify-content: space-around; align-items: flex-end; padding: 6mm 30mm 0; }}
.qr {{ text-align: center; }} .qr img, .qr-trong {{ width: 65mm; height: 65mm; }}
.qr-trong {{ border: 1mm dashed #999; display: grid; place-items: center; font-size: 22pt; color: #999; }}
.qr b {{ display: block; font-size: 30pt; margin-top: 3mm; color: #0D47A1; }}
.nho {{ text-align: center; font-size: 22pt; color: #666; margin-top: 8mm; }}
</style></head><body>
<div class="dau"><h1>TRỢ LÝ GIẢNG DẠY</h1>
<h2>Phiếu bài tập phân hóa và đánh giá học sinh tiểu học theo Thông tư 27 bằng AI</h2>
<p>⟦Họ tên⟧ · ⟦chức vụ⟧ · Trường ⟦…⟧, ⟦tỉnh/thành⟧ · Bảng A</p></div>
<div class="than">
 <div class="hang" style="grid-template-columns: 1fr 1.15fr">
  <div class="khoi"><h3>1. Bối cảnh &amp; vấn đề</h3><ul>
   <li>Lớp ⟦…⟧: ⟦…⟧ học sinh, trình độ chênh lệch rõ</li>
   <li>TT27: đánh giá thường xuyên bằng nhận xét, bài tập 3 mức</li>
   <li>Soạn 1 phiếu phân hóa có đáp án ≈ ⟦…⟧ phút; chấm &amp; nhận xét 1 lớp ≈ ⟦…⟧ phút</li>
   <li>Chatbot AI phổ thông trả lời rời rạc, không theo TT27, không tự kiểm tra đáp án</li></ul></div>
  <div class="khoi"><h3>2. Giải pháp: vòng khép kín</h3><img class="sodo" src="{anh('so-do-vong-khep-kin.png')}">
   <p class="cc">AI đề xuất – giáo viên quyết định. Dữ liệu chảy liền mạch từ soạn phiếu đến học bạ.</p></div>
 </div>
 <div class="khoi"><h3>3. AI hoạt động thế nào</h3><div class="luoi">
  {''.join(f'<figure><img src="{anh(t)}"><figcaption>{c}</figcaption></figure>' for t, c in ANH_DEMO)}
 </div></div>
 <div class="hang" style="grid-template-columns: 1.1fr 1fr">
  <div class="khoi"><h3>4. Kết quả thực tế</h3><table>
   <tr><th>Chỉ số</th><th>Trước</th><th>Sau</th></tr>
   <tr><td>Soạn 1 phiếu phân hóa</td><td>⟦…⟧ phút</td><td>⟦…⟧ phút</td></tr>
   <tr><td>Chấm &amp; nhận xét 1 lớp</td><td>⟦…⟧ phút</td><td>⟦…⟧ phút</td></tr>
   <tr><td>Tỉ lệ chưa đạt</td><td>⟦…%⟧</td><td>⟦…%⟧</td></tr>
   <tr><td>Học sinh hài lòng</td><td>–</td><td>⟦…%⟧</td></tr></table>
   <p class="cc">"⟦Trích phản hồi giáo viên⟧"</p></div>
  <div class="khoi"><h3>5. AI có trách nhiệm</h3><ul>
   <li>Giáo viên duyệt mọi đề, đáp án, điểm, nhận xét</li>
   <li>Kiểm định 2 lượt; mức TT27 theo quy tắc công khai</li>
   <li>Không gửi tên học sinh cho AI; học sinh không cần tài khoản</li></ul>
   <h3 style="margin-top:10mm">6. Bền vững &amp; nhân rộng</h3><ul>
   <li>0 đồng · chạy trên trình duyệt, điện thoại</li>
   <li>Khối 1–5 · 8 môn · 3 bộ sách giáo khoa</li>
   <li>Dữ liệu riêng từng giáo viên, dùng song song</li></ul></div>
 </div>
 <div class="chan">{qr('qr-trai-nghiem.png', 'Dùng thử')}{qr('qr-video.png', 'Video')}{qr('qr-app.png', 'Trang chủ')}</div>
 <p class="nho">Phần lập trình có sự hỗ trợ của công cụ AI Claude Code ⟦và …⟧.</p>
</div></body></html>"""


def tao():
    tam = THU_MUC / "_poster.html"
    tam.write_text(HTML, encoding="utf-8")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            pg = b.new_page()
            pg.goto(tam.as_uri())
            pg.wait_for_timeout(2000)
            pg.pdf(path=str(THU_MUC / "poster-nhap.pdf"), width="841mm", height="1189mm", print_background=True)
            b.close()
    finally:
        tam.unlink()
    print(f"Đã tạo {THU_MUC / 'poster-nhap.pdf'}")


if __name__ == "__main__":
    tao()
