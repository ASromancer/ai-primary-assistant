"""Chụp ảnh màn hình app cho slide/poster bằng dữ liệu lớp thật (xem tao_video_nhap.may_chu).

Chạy: .venv/bin/python docs/du-thi/tao_anh.py  →  ban-nop/*.png (dien_mau.py ưu tiên ảnh trong ban-nop/ hơn anh/).
Ảnh có tên học sinh thật nên chỉ nằm trong ban-nop/, không đưa lên GitHub.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
import tao_video_nhap as T  # noqa: E402


def main():
    with T.may_chu() as (U, ma, _), sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)

        def chup(ten, cho=2500):
            pg.wait_for_timeout(cho)
            pg.screenshot(path=str(T.RA / f"{ten}.png"))

        def den(chu):
            pg.get_by_text(chu).first.scroll_into_view_if_needed()
            pg.wait_for_timeout(800)

        def len_dau(chu):  # đưa tiêu đề mục lên sát đầu màn hình (vùng cắt trong dien_mau.CAT ổn định)
            pg.get_by_text(chu).first.evaluate("e => e.scrollIntoView({block: 'start'})")
            pg.wait_for_timeout(500); pg.mouse.move(1000, 500); pg.mouse.wheel(0, -90); pg.wait_for_timeout(900)

        pg.goto(U); chup("01-trang-chu", 7000)
        pg.goto(U + "/soan_phieu"); chup("02-soan-phieu-kiem-dinh", 6000)
        den("★★★ Mức 3"); chup("03-gop-y-kiem-dinh", 800)
        pg.goto(U + "/soan_phieu"); pg.wait_for_timeout(5000)
        pg.get_by_role("tab", name="🖨️ In phiếu").click(); pg.wait_for_timeout(1500)
        pg.get_by_text("Xanh", exact=True).first.click(); chup("04-in-phieu-xanh", 3000)
        pg.goto(U + "/lop_hoc"); pg.wait_for_timeout(6000)
        fr = [f for f in pg.frames if f != pg.main_frame][-1]
        fr.get_by_role("button", name="Sau ▶").click(); chup("05-lop-hoc-trinh-chieu", 1500)
        pg.goto(U + "/giao_bai"); chup("07-giao-bai-ma-qr", 7000)
        den("👀 Theo dõi nộp bài"); chup("08-giao-bai-theo-doi", 1500)
        pg.goto(U + "/cham_bai"); pg.wait_for_timeout(6000)
        len_dau("② Sổ tổng hợp"); chup("09-cham-bai-so-tong-hop", 1000)
        len_dau("③ Phân tích lỗi sai"); chup("10-phan-tich-loi-sai", 1500)
        pg.goto(U + "/tien_bo"); chup("12-tien-bo-bieu-do", 7000)
        pg.goto(U + "/lop_cua_toi"); chup("13-lop-cua-toi-phieu-theo-ten", 7000)
        pg.goto(U + "/thu_vien"); chup("14-thu-vien", 6000)
        m = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        m.goto(f"{U}/?ma={ma}"); m.wait_for_timeout(6000); m.screenshot(path=str(T.RA / "20-hs-chon-ten.png"))
        m.get_by_text(T.HS_DEMO, exact=True).click(); m.wait_for_timeout(1500)
        m.get_by_role("button", name="Bắt đầu làm bài").click(); m.wait_for_timeout(2500)
        m.screenshot(path=str(T.RA / "21-hs-lam-cau.png"))
        # Phiếu in (khổ A4) từ phiếu mẫu lớp 4: chung, nhóm Xanh, đáp án
        import html_export as hx
        ban, lop = T.phieu_mau(), T.thong_tin()["lop"]
        a4 = b.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        for ten, trang in [("30-phieu-chung", hx.phieu_chung(ban)), ("31-phieu-xanh", hx.phieu_nhom(ban, "Xanh", ten_lop=lop)),
                           ("32-dap-an-ma-tran", hx.dap_an(ban))]:
            a4.set_content(hx.trang_in([trang])); a4.wait_for_timeout(1500)
            a4.screenshot(path=str(T.RA / f"{ten}.png"), full_page=True)
        b.close()
    print(f"Đã chụp ảnh vào {T.RA}")


if __name__ == "__main__":
    main()
