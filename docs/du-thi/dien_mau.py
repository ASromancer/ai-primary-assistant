"""Điền nội dung hồ sơ vào MẪU của Ban Tổ chức (giữ nguyên thiết kế đầu trang, logo, chân trang, phông chữ).

Đầu vào:  docs/Mẫu Slide 2026.pptx, docs/Mẫu Poster 2026.pptx
Đầu ra:   docs/du-thi/Slide-du-thi.pptx (14 trang), docs/du-thi/Poster-du-thi.pptx (A0)
Chạy:     .venv/bin/python docs/du-thi/dien_mau.py      (cần: pip install python-pptx)

Sửa nội dung ở các hằng số SLIDE_* và POSTER_* rồi chạy lại. Chỗ ⟦…⟧ là thông tin/số liệu THẬT cần điền.
Viết đậm một đoạn bằng **…**. Sau khi mở bằng PowerPoint, xuất PDF (File → Export → PDF) để nộp.
"""
import re
from copy import deepcopy
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

DU_THI = Path(__file__).parent
DOCS = DU_THI.parent
ANH = DU_THI / "anh"
NAVY = RGBColor(0x00, 0x00, 0x54)
NAVY2 = RGBColor(0x09, 0x00, 0x81)
NEN = RGBColor(0xF1, 0xF5, 0xFC)

# ---------------- Thông tin tác giả (điền thật) ----------------
TEN_SP = "TRỢ LÝ GIẢNG DẠY – PHIẾU BÀI TẬP PHÂN HÓA VÀ ĐÁNH GIÁ HỌC SINH TIỂU HỌC THEO THÔNG TƯ 27 BẰNG AI"
TEN_GV = "⟦Họ và tên⟧"
DON_VI = ["Đơn vị công tác:", "⟦Trường Tiểu học …⟧", "⟦Địa chỉ trường⟧"]
EMAIL = ["Email:", "⟦email giáo viên⟧"]
LINK_DEMO = "⟦https://tro-ly-giang-day.streamlit.app/?demo=MA_DEMO⟧"
LINK_VIDEO = "⟦link Google Drive video⟧"

# ---------------- Nội dung slide ----------------
# Mỗi trang: (tiêu đề, [(cấp, chữ)], [ảnh bên phải]) — cấp 1 = gạch đầu dòng, 2 = ý con, 0 = không gạch
DAN_Y = [(1, "Bối cảnh và vấn đề"), (1, "Ý tưởng và giải pháp: vòng khép kín 6 bước"),
         (1, "Sản phẩm: soạn – kiểm định – dạy – chấm – bổ trợ – học bạ"), (1, "AI có trách nhiệm"),
         (1, "Triển khai thực tế"), (1, "Kết quả và tác động"), (1, "Thảo luận và tổng kết"), (1, "Tài liệu đính kèm")]

BOI_CANH = [
    (1, "Lớp ⟦…⟧ có ⟦sĩ số⟧ học sinh, trình độ chênh lệch rõ; đối tượng hưởng lợi: **học sinh và giáo viên tiểu học**."),
    (1, "Thông tư 27/2020: đánh giá thường xuyên bằng nhận xét; câu hỏi, bài tập theo **3 mức** "
        "(nhận biết – kết nối – vận dụng). Chương trình GDPT 2018 đòi hỏi dạy học phân hóa."),
    (1, "Dạy phân hóa tốn thời gian: soạn 3 mức kèm đáp án, in theo nhóm, chấm, viết nhận xét từng em."),
    (2, "Soạn 1 phiếu phân hóa có đáp án ≈ ⟦…⟧ phút; chấm và nhận xét 1 lớp ≈ ⟦…⟧ phút (số liệu khảo sát)."),
    (1, "Chatbot AI phổ thông trả lời rời rạc: không theo mẫu TT27, không tự kiểm tra đáp án, "
        "không nối với chấm bài và theo dõi tiến bộ."),
    (1, "Kết quả chấm nằm trên giấy, khó phân tích để dạy bù kịp thời."),
]

Y_TUONG = [
    (1, "**Vòng khép kín 6 bước theo TT27**: soạn phiếu 3 mức → AI kiểm định → dạy và giao bài → "
        "chấm và nhận xét → phân tích lỗi, phiếu bổ trợ → tiến bộ và học bạ."),
    (1, "**AI đề xuất – giáo viên quyết định** ở mọi bước."),
    (1, "Công cụ: **Google Gemini** (đọc ảnh sách giáo khoa và ảnh bài viết tay, tạo nội dung theo khung cấu trúc) · "
        "ứng dụng web Streamlit · dữ liệu Supabase · đăng nhập Google."),
    (1, "Vì sao chọn AI: làm nhanh phần lặp lại (ra đề, tính đáp án, định dạng, chấm, nhận xét), "
        "đọc được chữ viết tay, phân tích lỗi cả lớp ngay sau khi chấm."),
    (1, "Chi phí **0 đồng**; chạy trên trình duyệt máy tính, máy chiếu, điện thoại."),
]

TINH_NANG = [
    ("① SOẠN PHIẾU · ② AI KIỂM ĐỊNH", [
        (1, "Soạn từ **tên bài** hoặc **ảnh chụp trang sách giáo khoa**; chọn lớp, môn, bộ sách, thời lượng."),
        (1, "Phiếu 3 mức TT27 kèm đáp án, hướng dẫn chấm, ma trận, yêu cầu cần đạt."),
        (1, "Đáp án chuẩn tiểu học: Bài giải – câu lời giải – phép tính (đơn vị) – Đáp số."),
        (1, "**Lượt AI thứ hai** đóng vai tổ trưởng chuyên môn: tự giải lại từng câu, soát đáp án sai, câu lệch mức."),
        (2, "Thí điểm: phát hiện ⟦…⟧ lỗi / ⟦…⟧ phiếu."),
    ], ["02-soan-phieu-kiem-dinh.png", "03-gop-y-kiem-dinh.png"]),
    ("③ PHÂN HÓA KHÔNG DÁN NHÃN", [
        (1, "Một phiếu tự tách thành **Phiếu Xanh / Cam / Tím** cho 3 nhóm; tên màu trung tính, "
            "học sinh không biết mình ở \"mức\" nào."),
        (1, "Đề A/B chống nhìn bài; phiếu in sẵn tên từng em, đúng màu nhóm."),
        (1, "In ngay khổ A4 hoặc tải Word; cỡ chữ lớn cho lớp 1–2."),
    ], ["31-phieu-xanh.png", "13-lop-cua-toi-phieu-theo-ten.png"]),
    ("③ LỚP HỌC SỐ: TRÌNH CHIẾU VÀ GIAO BÀI BẰNG QR", [
        (1, "Trình chiếu từng câu kiểu trò chơi: đếm giờ, lật đáp án, gọi tên ngẫu nhiên, đọc to câu hỏi."),
        (1, "Giao bài online: chiếu mã QR, học sinh **chạm vào tên mình**, không cần tài khoản."),
        (1, "Mỗi em tự nhận **đúng phiếu của nhóm**; câu trắc nghiệm, đúng/sai, nối cột được chấm ngay."),
        (1, "Giáo viên theo dõi trực tiếp số bài đã nộp."),
    ], ["05-lop-hoc-trinh-chieu.png", "20-hs-chon-ten.png", "21-hs-lam-cau.png"]),
    ("④ CHẤM, NHẬN XÉT TT27 · ⑤ PHÂN TÍCH LỖI", [
        (1, "Chấm từ **ảnh chụp bài viết tay** hoặc bài làm online; AI viết nhận xét theo tinh thần TT27."),
        (1, "Mức đạt theo **quy tắc công khai**: Chưa hoàn thành (Mức 1 < 50%) · Hoàn thành tốt "
            "(Mức 1, Mức 2 ≥ 80%, Mức 3 ≥ 50%) · còn lại là Hoàn thành."),
        (1, "Giáo viên **chấm tay hoặc sửa** mọi kết quả."),
        (1, "Biểu đồ tỉ lệ chưa đạt từng câu và lỗi thường gặp; **một nút soạn phiếu bổ trợ** đúng chỗ hổng."),
    ], ["09-cham-bai-so-tong-hop.png", "10-phan-tich-loi-sai.png"]),
    ("⑥ THEO DÕI TIẾN BỘ VÀ NHẬN XÉT HỌC BẠ", [
        (1, "Mức TT27 của từng em qua các lần đánh giá; biểu đồ tiến bộ từng em."),
        (1, "AI gợi ý nhận xét cuối kỳ dựa trên cả quá trình (**không gửi tên học sinh**); giáo viên duyệt, xuất Excel."),
        (1, "Thư viện phiếu tự lưu, nhiều lớp, dữ liệu riêng cho từng giáo viên."),
    ], ["12-tien-bo-bieu-do.png", "11-tien-bo.png"]),
]

TRACH_NHIEM = [
    (1, "**Giáo viên là người quyết định**: duyệt đề, sửa đáp án, chốt điểm, mức đạt, nhận xét; có chấm tay đầy đủ."),
    (1, "**Kiểm soát chất lượng**: AI kiểm định lượt 2; khung cấu trúc và quy tắc trình bày đáp án chuẩn tiểu học; "
        "mức TT27 tính bằng quy tắc công khai."),
    (1, "**Bảo vệ dữ liệu học sinh**: không gửi tên học sinh cho AI khi soạn, chấm online, gợi ý học bạ; "
        "ảnh bài làm chỉ gửi để chấm, không lưu."),
    (2, "Học sinh không cần tài khoản; dữ liệu mỗi giáo viên tách riêng; cơ sở dữ liệu chặn truy cập công khai."),
    (1, "**Công bằng**: phiếu nhóm dùng tên màu trung tính; học sinh làm online biết đúng/sai nhưng không thấy đáp án."),
    (1, "Thí điểm có sự đồng ý của nhà trường và phụ huynh; hình ảnh không lộ mặt học sinh."),
]

TRIEN_KHAI = [
    (1, "Hình thức: ứng dụng web <https://tro-ly-giang-day.streamlit.app> dùng trong soạn bài, giờ dạy và đánh giá."),
    (2, "Soạn phiếu trước giờ học; in phiếu nhóm hoặc giao bài bằng QR; chấm và phân tích lỗi sau giờ học; dạy bổ trợ."),
    (1, "Thời gian: ⟦từ …/…/2026 đến nay⟧ (thí điểm ⟦…⟧ ngày)."),
    (1, "Đối tượng: lớp ⟦…⟧ – ⟦…⟧ học sinh, môn ⟦…⟧; ⟦…⟧ đồng nghiệp dùng thử."),
    (1, "Số lượng sử dụng: ⟦…⟧ phiếu đã soạn, ⟦…⟧ bài đã chấm (thống kê trong app)."),
]

KET_QUA = [
    (1, "Kết quả thí điểm bước đầu (⟦…⟧ ngày, ⟦…⟧ học sinh, ⟦…⟧ giáo viên):"),
    (2, "Giáo viên – soạn 1 phiếu phân hóa: ⟦…⟧ → ⟦…⟧ phút; chấm và nhận xét 1 lớp: ⟦…⟧ → ⟦…⟧ phút."),
    (2, "AI kiểm định phát hiện ⟦…⟧ lỗi; giáo viên sửa thêm ⟦…⟧ lỗi (minh chứng giáo viên duyệt kết quả)."),
    (2, "Học sinh – tỉ lệ chưa đạt ở câu yếu: ⟦…%⟧ → ⟦…%⟧ sau 1 buổi bổ trợ; hoàn thành bài ⟦…%⟧."),
    (2, "⟦…%⟧ học sinh thích làm phiếu/làm bài trên app; giáo viên đánh giá ⟦…⟧/5."),
    (1, "Phản hồi: \"⟦trích nguyên văn giáo viên/học sinh⟧\"."),
    (1, "Minh chứng: bảng khảo sát, ảnh phiếu và bài làm (đã che tên), thống kê sử dụng (xem trang Tài liệu đính kèm)."),
]

THAO_LUAN = [
    (1, "So với cách cũ và chatbot AI phổ thông: một **quy trình hoàn chỉnh theo TT27**, có kiểm định, "
        "phân hóa không dán nhãn, nối liền từ soạn phiếu đến học bạ."),
    (1, "Bền vững, nhân rộng: **0 đồng**; chạy trên trình duyệt; khối 1–5, 8 môn, 3 bộ sách; "
        "nhiều giáo viên dùng song song; có hướng dẫn chuyển giao."),
    (1, "Giới hạn: gói miễn phí giới hạn lượt AI; AI vẫn có thể sai nên luôn cần giáo viên duyệt; "
        "chọn tên khi làm bài online chưa ngăn được làm hộ."),
    (1, "Định hướng: chia sẻ phiếu trong tổ chuyên môn; tin nhắn phụ huynh từ kết quả đánh giá; "
        "tiếp tục theo dõi số liệu trong học kỳ I."),
    (0, "Phần lập trình được thực hiện với sự hỗ trợ của công cụ AI Claude Code ⟦và …⟧."),
]

DINH_KEM = [
    (1, f"Dùng thử sản phẩm (dành cho Ban Giám khảo): {LINK_DEMO}"),
    (1, f"Video thuyết trình: {LINK_VIDEO}"),
    (1, "Trang chủ: https://tro-ly-giang-day.streamlit.app"),
    (1, "Thư mục minh chứng (khảo sát, ảnh, thống kê): ⟦link Google Drive công khai, rút gọn bằng tinyurl/bitly⟧"),
    (1, "Tài liệu tham khảo: Thông tư 27/2020/TT-BGDĐT; Chương trình GDPT 2018."),
]


# ---------------- Tiện ích ----------------
def tim(slide, ten):
    for sh in slide.shapes:
        if sh.name == ten:
            return sh
    raise KeyError(ten)


def xoa(shape):
    shape._element.getparent().remove(shape._element)


def _run_mau(p):
    r = p.find(qn("a:r"))
    if r is None:
        r = p.makeelement(qn("a:r"), {})
        rpr = p.find(qn("a:endParaRPr"))
        r.append(deepcopy(rpr) if rpr is not None else r.makeelement(qn("a:rPr"), {}))
        if r[0].tag == qn("a:endParaRPr"):
            r[0].tag = qn("a:rPr")
        r.append(r.makeelement(qn("a:t"), {}))
    return r


def viet(shape, dong, co=None, mau_p=None):
    """Thay nội dung khung chữ, giữ định dạng đoạn của mẫu theo cấp (0, 1, 2). **…** = chữ đậm."""
    tx = shape.text_frame._txBody
    mau = dict(mau_p or {})
    for p in tx.findall(qn("a:p")):
        ppr = p.find(qn("a:pPr"))
        cap = int(ppr.get("lvl", 0)) if ppr is not None else 0
        mau.setdefault(cap, deepcopy(p))
        tx.remove(p)
    for cap, chu in dong:
        goc = next(m for m in (mau.get(cap), mau.get(1), *mau.values()) if m is not None)
        p = deepcopy(goc)
        r0 = deepcopy(_run_mau(p))
        for e in list(p):
            if e.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
                p.remove(e)
        end = p.find(qn("a:endParaRPr"))
        for k, doan in enumerate(re.split(r"\*\*", chu)):
            if not doan:
                continue
            r = deepcopy(r0)
            rpr = r.find(qn("a:rPr"))
            if k % 2:
                rpr.set("b", "1")
            if co:
                rpr.set("sz", str(int(co * 100)))
            r.find(qn("a:t")).text = doan
            (end.addprevious(r) if end is not None else p.append(r))
        if co:
            ppr = p.find(qn("a:pPr"))
            ln = ppr.find(qn("a:lnSpc")) if ppr is not None else None
            if ln is not None:
                ln.find(qn("a:spcPts")).set("val", str(int(co * 135)))
        tx.append(p)


def anh_vua_khung(slide, ten, trai, tren, rong, cao, vien=True):
    duong = ANH / ten
    if not duong.exists():
        return None
    h = slide.shapes.add_picture(str(duong), trai, tren)
    tl = min(rong / h.width, cao / h.height)
    h.width, h.height = int(h.width * tl), int(h.height * tl)
    h.left, h.top = int(trai + (rong - h.width) / 2), int(tren + (cao - h.height) / 2)
    if vien:
        h.line.color.rgb = RGBColor(0xCF, 0xD8, 0xE6)
        h.line.width = Pt(1.5)
    return h


def nhan_ban(prs, nguon):
    """Nhân bản 1 trang (kể cả ảnh nền chân trang) và đặt cuối bản trình chiếu."""
    moi = prs.slides.add_slide(nguon.slide_layout)
    for sh in list(moi.shapes):
        xoa(sh)
    doi_rid = {rid: moi.part.relate_to(rel._target, rel.reltype)
               for rid, rel in nguon.part.rels.items() if rel.reltype.endswith("/image")}
    for el in nguon.shapes._spTree:
        if el.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue
        e = deepcopy(el)
        for n in e.iter():
            for a in (qn("r:embed"), qn("r:link"), qn("r:id")):
                if n.get(a) in doi_rid:
                    n.set(a, doi_rid[n.get(a)])
        moi.shapes._spTree.append(e)
    return moi


def xep_thu_tu(prs, thu_tu):
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for e in ids:
        lst.remove(e)
    for k in thu_tu:
        lst.append(ids[k])


def xoa_trang(prs, chi_so):
    lst = prs.slides._sldIdLst
    sld = list(lst)[chi_so]
    prs.part.drop_rel(sld.get(qn("r:id")))
    lst.remove(sld)


# ---------------- Slide ----------------
def lam_slide():
    prs = Presentation(DOCS / "Mẫu Slide 2026.pptx")
    s = list(prs.slides)
    bia, dan_y, _, boi_canh, y_tuong, trien_khai, ket_qua, thao_luan, dinh_kem = s
    mau_than = {}  # định dạng đoạn cấp 1, 2 lấy từ trang Bối cảnh
    for p in tim(boi_canh, "TextBox 4").text_frame._txBody.findall(qn("a:p")):
        ppr = p.find(qn("a:pPr"))
        mau_than.setdefault(int(ppr.get("lvl", 0)) if ppr is not None else 0, deepcopy(p))

    # Bìa: tên sản phẩm, tác giả; bỏ ảnh người mẫu của Ban Tổ chức
    viet(tim(bia, "TextBox 11"), [(0, TEN_SP)], co=34)
    nhom = tim(bia, "Group 3")
    xf = nhom._element.grpSpPr.find(qn("a:xfrm"))
    tl = int(xf.find(qn("a:ext")).get("cx")) / int(xf.find(qn("a:chExt")).get("cx"))  # nhóm được thu nhỏ
    ox, oy = int(xf.find(qn("a:chOff")).get("x")), int(xf.find(qn("a:chOff")).get("y"))
    for sh in list(nhom.shapes):
        if sh.name == "TextBox 5":
            viet(sh, [(0, TEN_GV)])
        if sh.name == "Group 6":  # ảnh người mẫu của Ban Tổ chức: thay bằng khung trống
            x = nhom.left + int((sh.left - ox) * tl)
            y = nhom.top + int((sh.top - oy) * tl)
            w, h = int(sh.width * tl), int(sh.height * tl)
            xoa(sh)
    o = bia.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    o.fill.solid(); o.fill.fore_color.rgb = RGBColor(0xE3, 0xEA, 0xF4); o.line.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    o.text_frame.text = "⟦Ảnh giáo viên⟧"
    o.text_frame.paragraphs[0].runs[0].font.size = Pt(14); o.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
    viet(tim(bia, "TextBox 12"), [(0, "**" + DON_VI[0] + "**")] + [(0, d) for d in DON_VI[1:]])
    viet(tim(bia, "TextBox 13"), [(0, "**" + EMAIL[0] + "**")] + [(0, d) for d in EMAIL[1:]])

    # Dàn ý + hình minh họa
    viet(tim(dan_y, "TextBox 9"), DAN_Y, co=24, mau_p=mau_than)
    xoa(tim(dan_y, "TextBox 10"))
    khung = tim(dan_y, "Group 4")
    anh_vua_khung(dan_y, "so-do-vong-khep-kin.png", khung.left + Inches(0.3), khung.top + Inches(0.3),
                  khung.width - Inches(0.6), khung.height - Inches(0.6), vien=False)

    viet(tim(boi_canh, "TextBox 4"), BOI_CANH, co=28)
    tim(boi_canh, "TextBox 4").height = Inches(7.6)

    than = tim(y_tuong, "TextBox 2")
    viet(than, Y_TUONG, co=25, mau_p=mau_than)
    than.width = Inches(10.6)
    anh_vua_khung(y_tuong, "so-do-vong-khep-kin.png", Inches(11.7), Inches(1.9), Inches(7.6), Inches(7.6), vien=False)

    # Trang tính năng: nhân bản từ trang Triển khai (cùng kiểu đầu, chân trang)
    trang_tn = []
    for tieu_de, dong, anh in TINH_NANG + [("ỨNG DỤNG AI CÓ TRÁCH NHIỆM", TRACH_NHIEM, [])]:
        t = nhan_ban(prs, trien_khai)
        viet(tim(t, "TextBox 2"), [(0, tieu_de)])
        tim(t, "TextBox 2").width = Inches(17)
        than = tim(t, "TextBox 3")
        viet(than, dong, co=23 if anh else 27, mau_p=mau_than)
        than.height = Inches(7.6)
        if anh:
            than.width = Inches(8.3)
            vung_x, vung_w, vung_y, vung_h = Inches(9.4), Inches(9.9), Inches(2.1), Inches(7.4)
            w = Emu(int(vung_w / len(anh)))
            for k, a in enumerate(anh):
                anh_vua_khung(t, a, vung_x + w * k, vung_y, w - Inches(0.15), vung_h)
        trang_tn.append(t)

    viet(tim(trien_khai, "TextBox 3"), TRIEN_KHAI, co=28, mau_p=mau_than)
    tim(trien_khai, "TextBox 3").height = Inches(7.4)
    viet(tim(ket_qua, "TextBox 3"), KET_QUA, co=27, mau_p=mau_than)
    tim(ket_qua, "TextBox 3").height = Inches(7.4)
    viet(tim(thao_luan, "TextBox 3"), THAO_LUAN, co=27, mau_p=mau_than)
    tim(thao_luan, "TextBox 3").height = Inches(7.6)
    than = tim(dinh_kem, "TextBox 3")
    viet(than, DINH_KEM, co=25, mau_p=mau_than)
    than.width, than.height = Inches(12.4), Inches(7.4)
    for k, (q, nhan) in enumerate([("qr-trai-nghiem.png", "Dùng thử"), ("qr-video.png", "Video"), ("qr-app.png", "Trang chủ")]):
        y = Inches(2.2 + k * 2.55)
        if not anh_vua_khung(dinh_kem, q, Inches(14.2), y, Inches(2.1), Inches(2.1), vien=False):
            o = dinh_kem.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(14.2), y, Inches(2.1), Inches(2.1))
            o.fill.background(); o.line.dash_style = 4; o.line.color.rgb = NAVY
            o.text_frame.text = "⟦tạo QR⟧"; o.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
        tb = dinh_kem.shapes.add_textbox(Inches(16.5), y + Inches(0.75), Inches(3), Inches(0.6)).text_frame
        tb.text = nhan; tb.paragraphs[0].runs[0].font.size = Pt(22); tb.paragraphs[0].runs[0].font.bold = True
        tb.paragraphs[0].runs[0].font.color.rgb = NAVY

    # Thứ tự: bìa, dàn ý, bối cảnh, ý tưởng, 5 tính năng, trách nhiệm, triển khai, kết quả, thảo luận, đính kèm
    # (chỉ số theo thứ tự hiện có: 0..8 là mẫu gốc, 9..14 là trang nhân bản; bỏ trang 2 = hướng dẫn)
    xep_thu_tu(prs, [0, 1, 2, 3, 4, 9, 10, 11, 12, 13, 14, 5, 6, 7, 8])
    xoa_trang(prs, 2)
    ra = DU_THI / "Slide-du-thi.pptx"
    prs.save(ra)
    print(f"Đã tạo {ra} ({len(prs.slides)} trang)")


# ---------------- Poster ----------------
def khoi(slide, trai, tren, rong, cao, tieu_de=None):
    o = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, trai, tren, rong, cao)
    o.adjustments[0] = 0.04
    o.fill.solid(); o.fill.fore_color.rgb = NEN; o.line.fill.background(); o.shadow.inherit = False
    if tieu_de:
        tf = slide.shapes.add_textbox(trai + Inches(0.5), tren + Inches(0.35), rong - Inches(1), Inches(1.1)).text_frame
        tf.word_wrap = True
        r = tf.paragraphs[0].add_run(); r.text = tieu_de
        r.font.size, r.font.bold, r.font.name = Pt(58), True, "Aptos"
        r.font.color.rgb = NAVY2
    return o


def doan(slide, trai, tren, rong, cao, dong, co=34):
    tf = slide.shapes.add_textbox(trai, tren, rong, cao).text_frame
    tf.word_wrap = True
    for k, chu in enumerate(dong):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.space_after = Pt(co * 0.45)
        for j, d in enumerate(re.split(r"\*\*", chu)):
            if d:
                r = p.add_run(); r.text = d
                r.font.size, r.font.name, r.font.bold = Pt(co), "Aptos", bool(j % 2)
                r.font.color.rgb = NAVY
    return tf


def lam_poster():
    prs = Presentation(DOCS / "Mẫu Poster 2026.pptx")
    s = prs.slides[0]
    tieu = tim(s, "TextBox 7")
    viet(tieu, [(0, "TRỢ LÝ GIẢNG DẠY – PHIẾU BÀI TẬP PHÂN HÓA VÀ ĐÁNH GIÁ"),
                (0, "HỌC SINH TIỂU HỌC THEO THÔNG TƯ 27 BẰNG AI")], co=54)
    tieu.height = Inches(1.9)
    tim(s, "TextBox 8").top = Inches(8.95)
    viet(tim(s, "TextBox 8"), [(0, f"**Giáo viên thực hiện:** {TEN_GV}"),
                               (0, f"**Đơn vị công tác:** {DON_VI[1]}, {DON_VI[2]}")])
    xoa(tim(s, "TextBox 5")); xoa(tim(s, "Group 2"))  # hướng dẫn + khung đứt đoạn (theo yêu cầu của mẫu)

    X, W, G = Inches(1.96), Inches(29.27), Inches(0.45)
    # Hàng 1: Bối cảnh | Giải pháp
    y, h = Inches(11.2), Inches(9.4)
    w1 = Inches(13.4)
    khoi(s, X, y, w1, h, "1. BỐI CẢNH VÀ VẤN ĐỀ")
    doan(s, X + Inches(0.5), y + Inches(1.6), w1 - Inches(1), h - Inches(1.8), [
        "• Lớp ⟦…⟧: ⟦…⟧ học sinh, trình độ chênh lệch rõ.",
        "• TT27: đánh giá thường xuyên bằng nhận xét; bài tập **3 mức**.",
        "• Soạn 1 phiếu phân hóa có đáp án ≈ ⟦…⟧ phút; chấm và nhận xét 1 lớp ≈ ⟦…⟧ phút.",
        "• Chatbot AI phổ thông: rời rạc, không theo TT27, không tự kiểm tra đáp án.",
        "• **Đối tượng hưởng lợi:** học sinh và giáo viên tiểu học."], co=34)
    x2, w2 = X + w1 + G, W - w1 - G
    khoi(s, x2, y, w2, h, "2. GIẢI PHÁP: VÒNG KHÉP KÍN")
    anh_vua_khung(s, "so-do-vong-khep-kin.png", x2 + Inches(0.4), y + Inches(1.5), w2 - Inches(0.8), h - Inches(2.6), vien=False)
    doan(s, x2 + Inches(0.5), y + h - Inches(1.1), w2 - Inches(1), Inches(1),
         ["AI đề xuất – **giáo viên quyết định**. Công cụ: Google Gemini · Streamlit · Supabase."], co=28)

    # Hàng 2: 6 ảnh
    y, h = y + h + G, Inches(13.2)
    khoi(s, X, y, W, h, "3. AI HOẠT ĐỘNG THẾ NÀO")
    anh6 = [("02-soan-phieu-kiem-dinh.png", "① Soạn phiếu 3 mức từ tên bài / ảnh SGK"),
            ("03-gop-y-kiem-dinh.png", "② AI kiểm định tự giải lại, soát đáp án sai"),
            ("31-phieu-xanh.png", "③ Phiếu Xanh/Cam/Tím – không dán nhãn"),
            ("21-hs-lam-cau.png", "③ Quét QR, chọn tên, làm bài trên điện thoại"),
            ("10-phan-tich-loi-sai.png", "④⑤ Chấm, nhận xét TT27, phân tích lỗi → bổ trợ"),
            ("12-tien-bo-bieu-do.png", "⑥ Tiến bộ từng em, gợi ý nhận xét học bạ")]
    cw, ch = (W - Inches(1.4)) / 3, Inches(5.6)
    for k, (a, cap) in enumerate(anh6):
        cx = X + Inches(0.5) + int(cw * (k % 3))
        cy = y + Inches(1.6) + (k // 3) * Inches(5.8)
        anh_vua_khung(s, a, cx, cy, int(cw) - Inches(0.3), ch - Inches(1.1))
        tf = doan(s, cx, cy + ch - Inches(1.05), int(cw) - Inches(0.3), Inches(1), [cap], co=28)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Hàng 3: Kết quả | Trách nhiệm + Bền vững
    y, h = y + h + G, Inches(7.2)
    khoi(s, X, y, w1, h, "4. KẾT QUẢ THỰC TẾ")
    doan(s, X + Inches(0.5), y + Inches(1.6), w1 - Inches(1), h - Inches(1.8), [
        "• Soạn 1 phiếu: ⟦…⟧ → ⟦…⟧ phút",
        "• Chấm và nhận xét 1 lớp: ⟦…⟧ → ⟦…⟧ phút",
        "• Câu yếu sau bổ trợ: chưa đạt ⟦…%⟧ → ⟦…%⟧",
        "• ⟦…%⟧ học sinh thích · giáo viên đánh giá ⟦…⟧/5",
        "\"⟦Trích phản hồi giáo viên⟧\""], co=32)
    khoi(s, x2, y, w2, h, "5. AI CÓ TRÁCH NHIỆM · BỀN VỮNG")
    doan(s, x2 + Inches(0.5), y + Inches(1.6), w2 - Inches(1), h - Inches(1.8), [
        "• Giáo viên duyệt mọi đề, đáp án, điểm, nhận xét; kiểm định 2 lượt.",
        "• Không gửi tên học sinh cho AI; học sinh không cần tài khoản.",
        "• **0 đồng**, chạy trên trình duyệt; khối 1–5, 8 môn, 3 bộ sách.",
        "• Định hướng: chia sẻ trong tổ chuyên môn, tin nhắn phụ huynh."], co=32)

    # Hàng 4: QR + công khai
    y = y + h + Inches(0.35)
    for k, (q, nhan) in enumerate([("qr-trai-nghiem.png", "Dùng thử"), ("qr-video.png", "Video"), ("qr-app.png", "Trang chủ")]):
        cx = X + Inches(4.2) + k * Inches(8.8)
        if not anh_vua_khung(s, q, cx, y, Inches(2.3), Inches(2.3), vien=False):
            o = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, y, Inches(2.3), Inches(2.3))
            o.fill.background(); o.line.dash_style = 4; o.line.color.rgb = NAVY
            o.text_frame.text = "⟦tạo QR⟧"
        doan(s, cx + Inches(2.5), y + Inches(0.75), Inches(4.5), Inches(1), [f"**{nhan}**"], co=40)
    doan(s, X, y + Inches(2.4), W, Inches(0.6),
         ["Phần lập trình được thực hiện với sự hỗ trợ của công cụ AI Claude Code ⟦và …⟧."], co=24
         ).paragraphs[0].alignment = PP_ALIGN.CENTER
    ra = DU_THI / "Poster-du-thi.pptx"
    prs.save(ra)
    print(f"Đã tạo {ra}")


if __name__ == "__main__":
    lam_slide()
    lam_poster()
