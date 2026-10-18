"""In sẵn bộ phiếu thí điểm (A4, PDF): bảng ghi chép giáo viên, khảo sát giáo viên, phiếu mặt cười học sinh.

Chạy: .venv/bin/python docs/du-thi/tao_phieu_khao_sat.py  →  docs/du-thi/in-thi-diem.pdf
Nội dung khớp 05-ke-hoach-thi-diem-va-khao-sat.md.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

RA = Path(__file__).parent / "in-thi-diem.pdf"

MAT = {  # mặt cười vẽ bằng SVG để in chắc chắn đúng
    "vui": '<path d="M30 58 Q50 76 70 58" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>',
    "binh": '<path d="M32 64 L68 64" stroke="#222" stroke-width="5" stroke-linecap="round"/>',
    "buon": '<path d="M30 70 Q50 52 70 70" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>',
}


def mat(kieu: str, nhan: str) -> str:
    return (f'<div class="mat"><svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="none" stroke="#222" stroke-width="5"/>'
            f'<circle cx="35" cy="40" r="5" fill="#222"/><circle cx="65" cy="40" r="5" fill="#222"/>{MAT[kieu]}</svg><span>{nhan}</span></div>')


def phieu_hs() -> str:
    cau = [("1. Em có thích làm phiếu bài tập hôm nay không?", ("Thích", "Bình thường", "Không thích")),
           ("2. Bài tập hôm nay có vừa sức với em không?", ("Vừa sức", "Hơi khó / hơi dễ", "Quá khó / quá dễ")),
           ("3. Em có thích làm bài trên máy không? (nếu có làm)", ("Thích", "Bình thường", "Không thích"))]
    noi = "".join(f'<p class="cau">{c}</p><div class="hang">{mat("vui", a)}{mat("binh", b)}{mat("buon", d)}</div>'
                  for c, (a, b, d) in cau)
    return (f'<div class="hs"><b>PHIẾU Ý KIẾN CỦA EM</b> <i>(không ghi tên – tô vào mặt em chọn)</i>{noi}'
            f'<p class="cau">4. Em muốn nói gì với cô/thầy? ………………………………………………</p></div>')


def thang() -> str:
    return "".join(f'<td class="o">{k}</td>' for k in range(1, 6))


HTML = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&display=swap">
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ font-family: "Be Vietnam Pro", sans-serif; font-size: 11pt; color: #111; }}
h1 {{ font-size: 15pt; color: #0D47A1; margin: 0 0 2mm; }} h2 {{ font-size: 12.5pt; color: #0D47A1; margin: 5mm 0 2mm; }}
table {{ width: 100%; border-collapse: collapse; }} td, th {{ border: 1px solid #555; padding: 1.8mm 2mm; vertical-align: top; }}
th {{ background: #EAF1FB; }} td.o {{ width: 9mm; text-align: center; color: #888; }}
.trang {{ page-break-after: always; }}
.luoi {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; height: 270mm; }}
.hs {{ border: 1px dashed #999; padding: 4mm; font-size: 10.5pt; }}
.cau {{ margin: 3mm 0 1mm; font-weight: 600; }}
.hang {{ display: flex; justify-content: space-around; }}
.mat {{ text-align: center; width: 28mm; }} .mat svg {{ width: 17mm; height: 17mm; }} .mat span {{ display: block; font-size: 8.5pt; }}
.ghi {{ color: #555; font-size: 9.5pt; }}
</style></head><body>
<div class="trang">
<h1>BẢNG GHI CHÉP CỦA GIÁO VIÊN – THÍ ĐIỂM TRỢ LÝ GIẢNG DẠY</h1>
<p>Giáo viên: …………………………… Lớp: ……… Sĩ số: ……… Môn: ……………… Từ ngày …/10 đến …/10/2026</p>
<table><tr><th>Mã</th><th>Chỉ số</th><th style="width:30mm">Cách cũ</th><th style="width:30mm">Dùng app</th><th style="width:34mm">Ghi chú / ngày đo</th></tr>
<tr><td>B1</td><td>Thời gian soạn 1 phiếu phân hóa có đáp án (phút)</td><td></td><td></td><td></td></tr>
<tr><td>B2</td><td>Thời gian in / chia phiếu theo nhóm (phút)</td><td></td><td></td><td></td></tr>
<tr><td>B3</td><td>Số lỗi đáp án/câu do AI kiểm định phát hiện</td><td>–</td><td></td><td></td></tr>
<tr><td>B4</td><td>Số lỗi giáo viên tự phát hiện thêm sau kiểm định</td><td>–</td><td></td><td></td></tr>
<tr><td>B5</td><td>Thời gian chấm và nhận xét 1 lớp (phút)</td><td></td><td></td><td></td></tr>
<tr><td>B6</td><td>Số học sinh hoàn thành bài / sĩ số</td><td></td><td></td><td></td></tr>
<tr><td>B7</td><td>Số bài AI chấm sai, giáo viên phải sửa / tổng số bài</td><td>–</td><td></td><td></td></tr>
<tr><td>B8</td><td>Tỉ lệ học sinh chưa đạt ở câu yếu – TRƯỚC bổ trợ</td><td colspan="2"></td><td>Câu số: ……</td></tr>
<tr><td>B9</td><td>Tỉ lệ học sinh chưa đạt ở câu yếu – SAU 1 buổi bổ trợ</td><td colspan="2"></td><td></td></tr>
</table>
<p class="ghi">Ghi trung thực cả B4 và B7: đó là minh chứng giáo viên luôn duyệt kết quả của AI. Bấm giờ bằng đồng hồ điện thoại.</p>
<h2>Ghi chú quan sát trong giờ học</h2>
<table><tr><td style="height:30mm"></td></tr></table>
<h2>Phản hồi nổi bật (ghi nguyên văn, xin phép trích dẫn)</h2>
<table><tr><td style="height:18mm"></td></tr></table>
</div>
<div class="trang">
<h1>PHIẾU KHẢO SÁT GIÁO VIÊN</h1>
<p>Họ tên: …………………………… Trường: ……………………………… Lớp/môn: ……………… (đồng ý trích dẫn: ☐ Có ☐ Không)</p>
<h2>A. Trước khi dùng</h2>
<table>
<tr><td>A1. Mỗi tháng thầy/cô soạn phiếu bài tập phân hóa (nhiều mức) khoảng bao nhiêu lần?</td><td style="width:60mm">☐ 0 ☐ 1–2 ☐ 3–4 ☐ &gt;4</td></tr>
<tr><td>A2. Thời gian trung bình soạn 1 phiếu phân hóa có đáp án</td><td>………… phút</td></tr>
<tr><td>A3. Thời gian trung bình chấm và viết nhận xét cho 1 lớp</td><td>………… phút</td></tr>
<tr><td colspan="2">A4. Khó khăn lớn nhất khi dạy phân hóa và đánh giá theo TT27:<br><br><br></td></tr></table>
<h2>D. Sau khi dùng thử <span class="ghi">(1 = hoàn toàn không đồng ý … 5 = hoàn toàn đồng ý; khoanh tròn)</span></h2>
<table>
<tr><td>D1. Phiếu do app soạn đúng chuẩn kiến thức và đúng mức TT27.</td>{thang()}</tr>
<tr><td>D2. Đáp án và cách trình bày phù hợp với học sinh tiểu học.</td>{thang()}</tr>
<tr><td>D3. Phần AI kiểm định giúp tôi yên tâm hơn về chất lượng đề.</td>{thang()}</tr>
<tr><td>D4. App giúp tôi tiết kiệm thời gian soạn và chấm.</td>{thang()}</tr>
<tr><td>D5. Phiếu Xanh/Cam/Tím giúp tổ chức dạy phân hóa dễ hơn.</td>{thang()}</tr>
<tr><td>D6. Tôi sẽ tiếp tục dùng và giới thiệu cho đồng nghiệp.</td>{thang()}</tr>
<tr><td colspan="6">D7. Điều thầy/cô thích nhất:<br><br><br>Điều cần cải thiện:<br><br><br></td></tr></table>
</div>
<div class="trang"><div class="luoi">{phieu_hs() * 4}</div></div>
<div><div class="luoi">{phieu_hs() * 4}</div></div>
</body></html>"""


if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page()
        pg.set_content(HTML)
        pg.wait_for_timeout(1500)
        pg.pdf(path=str(RA), format="A4", print_background=True)
        b.close()
    print(f"Đã tạo {RA}")
