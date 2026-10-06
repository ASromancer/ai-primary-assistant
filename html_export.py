"""Dựng trang in HTML (A4) cho phiếu: xem trước trên web + in/lưu PDF bằng trình duyệt.

Mọi nội dung do AI/người dùng nhập đều được html.escape vì trang chạy trong iframe có JavaScript.
"""
import html

from ai import DANG_BAI, MUC, BanLuu, CauHoi
from docx_export import (NHOM, SAO, ban_de_b, bo_tien_to, cau_cua_nhom, cau_theo_muc, dung_de_b, ma_tran, so,
                         vi_tri_trong_phieu)

XANH_DAM = "#003366"

CSS = """
@page { size: A4; margin: 15mm 15mm 15mm 20mm; }
* { box-sizing: border-box; }
body { font-family: "Times New Roman", Times, serif; font-size: %(co)dpt; color: #111; margin: 0; background: #e9edf2; }
.thanh { position: sticky; top: 0; z-index: 1; background: #fff; padding: 10px; text-align: center;
         border-bottom: 1px solid #dde3ea; font: 14px system-ui, sans-serif; color: #555; }
.thanh button { font: 600 15px system-ui, sans-serif; background: #1565C0; color: #fff; border: 0;
                border-radius: 8px; padding: 10px 26px; cursor: pointer; margin-right: 10px; }
.thanh button:hover { background: #0D47A1; }
.trang { background: #fff; width: 210mm; min-height: 297mm; margin: 16px auto; padding: 15mm 15mm 15mm 20mm;
         box-shadow: 0 2px 12px rgba(0,0,0,.15); }
.dau { display: flex; justify-content: space-between; gap: 2em; font-size: .85em; line-height: 1.5; }
h1 { text-align: center; font-size: 1.2em; margin: .8em 0 .15em; }
.phu { text-align: center; font-style: italic; font-size: .9em; }
.chude { text-align: center; font-weight: bold; font-size: .9em; margin-bottom: .5em; }
.muc { font-weight: bold; margin: .9em 0 .2em; }
.cau { margin: .55em 0; break-inside: avoid; line-height: 1.45; }
.goiy { font-style: italic; font-size: .85em; color: #444; }
.lc { margin-left: 1.6em; }
table { border-collapse: collapse; width: 100%%; margin: .3em 0; }
td, th { border: 1px solid #333; padding: 3px 7px; vertical-align: top; text-align: left; }
th { background: #f1f4f8; }
td.ds { width: 3cm; }
table.noi td { border: 0; padding: 4px 0; }
.dong { border-bottom: 1px dotted #555; height: 1.7em; }
.cuoi { margin-top: 1.2em; break-inside: avoid; font-size: .9em; }
.chuc { text-align: center; font-style: italic; color: #003366; font-size: 1.05em; margin-bottom: .6em; }
.gv { font-size: .8em; }
.gv h2 { font-size: 1.05em; margin: 1em 0 .3em; }
@media print {
  body { background: #fff; }
  .thanh { display: none; }
  .trang { width: auto; min-height: 0; margin: 0; padding: 0; box-shadow: none; break-after: page; }
  .trang:last-child { break-after: auto; }
}
@media screen and (max-width: 840px) { .trang { width: auto; min-height: 0; margin: 8px; padding: 6mm; } }
"""


def t(s: str) -> str:
    return html.escape(s).replace("\n", "<br>")


def _dau(ban: BanLuu, ten_phieu: str, mau: str = XANH_DAM, ho_ten: str = "", ten_lop: str = "") -> str:
    ts = ban.thong_so
    return f"""<div class="dau">
<div>Trường Tiểu học: {t(ts.truong) or '....................'}<br>Lớp: {t(ten_lop) or '............'}</div>
<div>Họ và tên: {f"<b>{t(ho_ten)}</b>" if ho_ten else '......................................'}<br>Ngày: ......./......./...........</div></div>
<h1 style="color:{mau}">{t(ten_phieu)}</h1>
<div class="phu">Môn {t(ts.mon)} – Lớp {ts.lop} – Thời gian: {ts.thoi_luong} phút</div>
<div class="chude">Chủ đề: {t(ts.chu_de)}</div>"""


def _cau(stt: int, c: CauHoi) -> str:
    out = [f'<div class="cau"><b>Câu {stt} ({so(c.diem)} điểm).</b> {t(c.noi_dung)}']
    if c.goi_y_hs:
        out.append(f'<div class="goiy">Gợi ý: {t(c.goi_y_hs)}</div>')
    ds = [bo_tien_to(x) for x in c.lua_chon]
    if c.dang == "trac_nghiem":
        out += [f'<div class="lc">{"ABCDEFGH"[i]}. {t(x)}</div>' for i, x in enumerate(ds[:8])]
    elif c.dang == "dung_sai":
        out.append("<table><tr><th>Nhận định</th><th>Đ / S</th></tr>"
                   + "".join(f'<tr><td>{t(x)}</td><td class="ds"></td></tr>' for x in ds) + "</table>")
    elif c.dang == "noi_cot":
        phai = [bo_tien_to(x) for x in c.cot_phai][:8]
        rows = "".join(
            f"<tr><td>{f'{i + 1}. {t(ds[i])} &nbsp;•' if i < len(ds) else ''}</td><td style='width:30%'></td>"
            f"<td>{f'• &nbsp;{chr(97 + i)}. {t(phai[i])}' if i < len(phai) else ''}</td></tr>"
            for i in range(max(len(ds), len(phai))))
        out.append(f'<table class="noi">{rows}</table>')
    elif c.dang == "tu_luan":
        out.append('<div class="dong"></div>' * (c.muc + 2))
    return "".join(out) + "</div>"


def _cuoi(ban: BanLuu) -> str:
    return f"""<div class="cuoi"><div class="chuc">{t(ban.phieu.loi_chuc)}</div>
Em tự đánh giá: &nbsp; ☐ Em làm được hết &nbsp;&nbsp; ☐ Em làm được một phần &nbsp;&nbsp; ☐ Em cần cô giúp thêm
<div style="margin-top:.5em">Nhận xét của giáo viên:</div><div class="dong"></div><div class="dong"></div></div>"""


def phieu_chung(ban: BanLuu) -> str:
    out, stt = [_dau(ban, "PHIẾU HỌC TẬP")], 0
    for muc in (1, 2, 3):
        ids = cau_theo_muc(ban, muc)
        if ids:
            out.append(f'<div class="muc" style="color:{XANH_DAM}">{SAO[muc]} &nbsp;THỬ THÁCH {muc} SAO</div>')
        for i in ids:
            stt += 1
            out.append(_cau(stt, ban.phieu.cau_hoi[i]))
    return f'<div class="trang">{"".join(out)}{_cuoi(ban)}</div>'


def phieu_nhom(ban: BanLuu, ten: str, ho_ten: str = "", ten_lop: str = "", de_b: bool = False) -> str:
    mau = f"#{NHOM[ten][1]}"
    chinh, them = cau_cua_nhom(ban, ten)
    tieu_de = f"PHIẾU HỌC TẬP – PHIẾU {ten.upper()}" + (" – ĐỀ B" if de_b else "")
    out = [_dau(ban, tieu_de, mau, ho_ten, ten_lop)]
    out += [_cau(stt, ban.phieu.cau_hoi[i]) for stt, i in enumerate(chinh, 1)]
    if them:
        out.append(f'<div class="muc" style="color:{mau}">★ THỬ THÁCH THÊM (nếu em còn thời gian)</div>')
        out.append(_cau(len(chinh) + 1, ban.phieu.cau_hoi[them[0]]))
    return f'<div class="trang">{"".join(out)}{_cuoi(ban)}</div>'


def dap_an(ban: BanLuu) -> str:
    ts, phieu = ban.thong_so, ban.phieu
    head = ["Mức"] + list(DANG_BAI.values()) + ["Số câu", "Điểm"]
    mt = "".join("<tr>" + "".join(f"<td>{so(v) if isinstance(v, float) else v}</td>" for v in row) + "</tr>"
                 for row in ma_tran(ban))
    vt = vi_tri_trong_phieu(ban)
    da = "".join(
        f"<tr><td>{t(vt[i])}</td><td>Mức {c.muc} – {DANG_BAI[c.dang]} ({so(c.diem)}đ)</td>"
        f"<td>{t(c.dap_an)}</td><td>{t(c.huong_dan_cham)}</td></tr>"
        for i in (i for m in (1, 2, 3) for i in cau_theo_muc(ban, m)) for c in [phieu.cau_hoi[i]])
    nhom = "".join(
        f"<li>Phiếu {ten}: {hs} (câu Mức {chinh}" + (f" + 1 câu thử thách Mức {them})" if them else ")") + "</li>"
        for ten, ((chinh, them), _, hs) in NHOM.items())
    return f"""<div class="trang gv">
<h1 style="color:{XANH_DAM}">ĐÁP ÁN – MA TRẬN ĐỀ (dành cho giáo viên)</h1>
<div class="phu">Môn {t(ts.mon)} – Lớp {ts.lop} – Bộ sách {t(ts.bo_sach)} – {ts.thoi_luong} phút<br>Chủ đề: {t(ts.chu_de)}</div>
<h2>1. Yêu cầu cần đạt</h2><ul>{"".join(f"<li>{t(y)}</li>" for y in phieu.yeu_cau_can_dat)}</ul>
<h2>2. Ma trận theo mức độ (Thông tư 27/2020/TT-BGDĐT)</h2>
<table><tr>{"".join(f"<th>{h}</th>" for h in head)}</tr>{mt}</table>
<div class="goiy">{"<br>".join(f"Mức {m}: {d}." for m, d in MUC.items())}</div>
<h2>3. Phân phiếu theo nhóm</h2><ul>{nhom}</ul>
<h2>4. Đáp án và hướng dẫn chấm</h2>
<table><tr><th>Câu (vị trí)</th><th>Mức – Dạng</th><th>Đáp án</th><th>Hướng dẫn chấm</th></tr>{da}</table></div>"""


def phieu_theo_ten(ban: BanLuu, hoc_sinh: list, xen_ke_ab: bool, ten_lop: str = "") -> list[str]:
    out = []
    for hs in hoc_sinh:
        b = dung_de_b(ban, hs, xen_ke_ab)
        out.append(phieu_nhom(ban_de_b(ban) if b else ban, hs.nhom, hs.ten, ten_lop, b))
    return out


def cac_trang(ban: BanLuu) -> dict[str, str]:
    out = {"Phiếu chung": phieu_chung(ban)}
    out.update({f"Phiếu {ten}": phieu_nhom(ban, ten) for ten in NHOM})
    out["Đáp án & ma trận"] = dap_an(ban)
    return out


def trang_in(trang: list[str], co_chu: int = 14) -> str:
    return f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><style>{CSS % {"co": co_chu}}</style></head>
<body><div class="thanh"><button onclick="window.print()">🖨️ In / Lưu PDF</button>
Khổ A4 · {len(trang)} phiếu · chọn số bản in trong hộp thoại in</div>{"".join(trang)}</body></html>"""
