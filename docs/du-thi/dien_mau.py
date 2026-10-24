"""Điền nội dung hồ sơ vào MẪU của Ban Tổ chức (giữ nguyên thiết kế đầu trang, logo, chân trang, phông chữ).

Đầu vào:  docs/Mẫu Slide 2026.pptx, docs/Mẫu Poster 2026.pptx
Đầu ra:   docs/du-thi/ban-nop/Slide-du-thi.pptx (14 trang, có lời thuyết trình trong phần ghi chú),
          docs/du-thi/ban-nop/Poster-du-thi.pptx (A0). Thư mục ban-nop/ không đưa lên GitHub.
Link/QR dùng thử và video lấy từ ban-nop/ nếu đã tạo bằng tao_ma_demo.py.
Chạy:     .venv/bin/python docs/du-thi/dien_mau.py      (cần: pip install python-pptx)

Sửa nội dung ở các hằng số SLIDE_* và POSTER_* rồi chạy lại. Chỗ ⟦…⟧ là thông tin/số liệu THẬT cần điền.
Viết đậm một đoạn bằng **…**. Sau khi mở bằng PowerPoint, xuất PDF (File → Export → PDF) để nộp.
"""
import json
import re
import tempfile
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
RA = DU_THI / "ban-nop"  # chứa mã dùng thử, QR, file nộp – không đưa lên GitHub công khai
NAVY = RGBColor(0x00, 0x00, 0x54)
NAVY2 = RGBColor(0x09, 0x00, 0x81)
NEN = RGBColor(0xF1, 0xF5, 0xFC)

# ---------------- Thông tin tác giả (điền thật) ----------------
TEN_SP = "TRỢ LÝ GIẢNG DẠY – PHIẾU BÀI TẬP PHÂN HÓA VÀ ĐÁNH GIÁ HỌC SINH TIỂU HỌC THEO THÔNG TƯ 27 BẰNG AI"
# Thông tin thật lấy từ ban-nop/so-lieu.json (không đưa lên GitHub); ô trống giữ chỗ ⟦…⟧
_sl = RA / "so-lieu.json"
_tt = json.loads(_sl.read_text(encoding="utf-8")) if _sl.exists() else {}
_g = lambda k, mac_dinh="⟦…⟧": str(_tt.get(k, "")).strip() or mac_dinh
TEN_GV = _g("ho_ten", "⟦Họ và tên⟧")
DON_VI = ["Đơn vị công tác:", _g("truong", "⟦Trường Tiểu học …⟧"), _g("dia_chi", "⟦Địa chỉ trường⟧")]
EMAIL = ["Email:", _g("email", "⟦email giáo viên⟧")]
LOP, SI_SO = _g("lop"), _g("si_so")
_co = lambda *k: all(str(_tt.get(x, "")).strip() for x in k)
# Chưa có số liệu thí điểm thật: slide/poster/lời nói trình bày MỤC TIÊU và cách đo, không ghi số giả định như kết quả
CO_KQ = _co("so_ngay", "so_hoc_sinh", "phut_soan_cu", "phut_soan_moi", "phut_cham_cu", "phut_cham_moi",
            "phan_tram_chua_dat_truoc", "phan_tram_chua_dat_sau")
CO_CU = _co("phut_soan_cu", "phut_cham_cu")
PHAN_HOI = str(_tt.get("phan_hoi", "")).strip()
HO_TRO = "và một người hỗ trợ kỹ thuật"  # chỉnh theo trả lời của Ban Tổ chức về quyền tác giả
_ma = RA / "ma-demo.txt"
LINK_DEMO = (f"https://tro-ly-giang-day.streamlit.app/?demo={_ma.read_text(encoding='utf-8').strip()}" if _ma.exists()
             else "⟦https://tro-ly-giang-day.streamlit.app/?demo=MA_DEMO⟧")
_vd = RA / "link-video.txt"
LINK_VIDEO = _vd.read_text(encoding="utf-8").strip() if _vd.exists() else "⟦link Google Drive video⟧"

# ---------------- Nội dung slide ----------------
# Mỗi trang: (tiêu đề, [(cấp, chữ)], [ảnh bên phải]) — cấp 1 = gạch đầu dòng, 2 = ý con, 0 = không gạch
DAN_Y = [(1, "Bối cảnh và vấn đề"), (1, "Ý tưởng và giải pháp: vòng khép kín 6 bước"),
         (1, "Toàn cảnh 8 nhóm tính năng; chi tiết: soạn – kiểm định – dạy – chấm – bổ trợ – học bạ"), (1, "AI có trách nhiệm"),
         (1, "Triển khai thực tế"), (1, "Kết quả và tác động"), (1, "Thảo luận: so sánh, bền vững, định hướng"), (1, "Tài liệu đính kèm")]

BOI_CANH = [
    (1, f"Lớp {LOP} có {SI_SO} học sinh, trình độ chênh lệch rõ; đối tượng hưởng lợi: **học sinh và giáo viên tiểu học**."),
    (1, "Thông tư 27/2020: đánh giá thường xuyên bằng nhận xét; đề kiểm tra định kỳ theo **3 mức** "
        "(nhận biết – kết nối – vận dụng), giáo viên vận dụng 3 mức khi ra bài tập phân hóa. "
        "Chương trình GDPT 2018 đòi hỏi dạy học phân hóa."),
    (1, "Dạy phân hóa tốn thời gian: soạn 3 mức kèm đáp án, in theo nhóm, chấm, viết nhận xét từng em."),
    *([(2, f"Soạn 1 phiếu phân hóa có đáp án ≈ {_g('phut_soan_cu')} phút; chấm và nhận xét 1 lớp ≈ {_g('phut_cham_cu')} phút "
            "(giáo viên tự ước tính).")] if CO_CU else []),
    (1, "Chatbot AI phổ thông trả lời rời rạc: không theo mẫu TT27, không có bước kiểm tra đáp án riêng, "
        "không nối với chấm bài và theo dõi tiến bộ."),
    (1, "Kết quả chấm nằm trên giấy, khó phân tích để dạy bổ trợ kịp thời."),
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
        (1, "Soạn từ **tên bài** hoặc **ảnh chụp trang sách giáo khoa**; bám sát bộ sách **Kết nối tri thức với cuộc sống** (dùng thống nhất toàn quốc từ 2026–2027)."),
        (1, "Phiếu 3 mức TT27 kèm đáp án, hướng dẫn chấm, ma trận, yêu cầu cần đạt."),
        (1, "Đáp án chuẩn tiểu học: Bài giải – câu lời giải – phép tính (đơn vị) – Đáp số."),
        (1, "**Lượt AI thứ hai** đóng vai tổ trưởng chuyên môn: tự giải lại từng câu, soát đáp án sai, câu lệch mức."),
        (1, "Chỉnh từng câu: **đổi câu, dễ hơn, khó hơn**, sửa tay, hoàn tác; một nút **Sửa theo góp ý**."),
        *([(2, f"Thí điểm: phát hiện {_g('loi_kiem_dinh')} lỗi.")] if _co("loi_kiem_dinh") else []),
    ], ["02-soan-phieu-kiem-dinh.png"]),
    ("③a PHÂN HÓA KHÔNG DÁN NHÃN", [
        (1, "Một phiếu tự tách thành **Phiếu Xanh / Cam / Tím** cho 3 nhóm; tên màu trung tính, "
            "học sinh không biết mình ở \"mức\" nào."),
        (1, "Đề A/B chống nhìn bài; phiếu in sẵn tên từng em, đúng màu nhóm."),
        (1, "In ngay khổ A4 (cỡ chữ 14–18pt) hoặc **tải Word**, tải trọn bộ phiếu và đáp án (.zip)."),
    ], ["31-phieu-xanh.png", "13-lop-cua-toi-phieu-theo-ten.png"]),
    ("③b LỚP HỌC SỐ: TRÌNH CHIẾU VÀ GIAO BÀI BẰNG QR", [
        (1, "Trình chiếu từng câu kiểu trò chơi: đếm giờ, lật đáp án, gọi tên ngẫu nhiên, đọc to câu hỏi."),
        (1, "Giao bài online: chiếu mã QR, học sinh **chạm vào tên mình**, không cần tài khoản."),
        (1, "Mỗi em tự nhận **đúng phiếu của nhóm**; câu trắc nghiệm, đúng/sai, nối cột được chấm ngay."),
        (1, "Giáo viên **theo dõi trực tiếp**; đặt hạn nộp, đóng/mở bài, cho em làm lại; câu điền, tự luận do AI chấm "
            "hoặc giáo viên chấm tay."),
    ], ["05-lop-hoc-trinh-chieu.png", "21-hs-lam-cau.png"]),
    ("④ CHẤM, NHẬN XÉT TT27 · ⑤ PHÂN TÍCH LỖI", [
        (1, "Chấm từ **ảnh chụp bài viết tay** (tối đa 40 bài một lượt) hoặc bài làm online; AI viết nhận xét theo tinh thần TT27."),
        (1, "Mức hoàn thành bài theo **quy tắc cố định, công khai**: Hoàn thành tốt khi đúng ≥ 80% câu Mức 1 và Mức 2, "
            "≥ 50% câu Mức 3; Chưa hoàn thành khi đúng < 50% câu Mức 1; còn lại là Hoàn thành."),
        (1, "Đánh giá thường xuyên bằng **nhận xét, không cho điểm** (TT27)."),
        (1, "Giáo viên **chấm tay hoặc sửa** mọi kết quả."),
        (1, "Biểu đồ tỉ lệ chưa đạt từng câu và lỗi thường gặp; **một nút soạn phiếu bổ trợ** đúng chỗ hổng."),
        (1, "Xuất **sổ tổng hợp Excel**; cập nhật nhóm Xanh/Cam/Tím cho lần sau; lưu vào hồ sơ lớp."),
    ], ["09-cham-bai-so-tong-hop.png", "10-phan-tich-loi-sai.png"]),
    ("⑥ THEO DÕI TIẾN BỘ VÀ NHẬN XÉT HỌC BẠ", [
        (1, "Mức hoàn thành của từng em qua các lần đánh giá; biểu đồ tiến bộ từng em."),
        (1, "AI gợi ý nhận xét học bạ **cho cả lớp một lần**, dựa trên cả quá trình (không gửi tên học sinh); "
            "giáo viên duyệt, xuất Excel."),
        (1, "**Thư viện phiếu** tự lưu: gắn sao, nhân bản, nhập/xuất file; **Lớp của tôi**: nhiều lớp, dán nhanh danh sách tên."),
        (1, "Đăng nhập Google, dữ liệu riêng từng giáo viên; Trang chủ thống kê số phiếu, bài đã chấm, thời gian tiết kiệm."),
    ], ["12-tien-bo-bieu-do.png"]),
]

TRACH_NHIEM = [
    (1, "**Giáo viên là người quyết định**: duyệt đề, sửa đáp án, chốt mức đạt và nhận xét; có chấm tay đầy đủ."),
    (1, "**Kiểm soát chất lượng**: AI kiểm định lượt 2; khung cấu trúc và quy tắc trình bày đáp án chuẩn tiểu học; "
        "mức TT27 tính bằng quy tắc công khai."),
    (1, "**Bảo vệ dữ liệu học sinh**: không gửi danh sách lớp cho AI; gợi ý nhận xét học bạ không kèm tên; "
        "ảnh bài làm chỉ gửi để chấm, ứng dụng không lưu ảnh (khuyến nghị che tên trước khi chụp)."),
    (1, "**Riêng tư**: học sinh không cần tài khoản; dữ liệu mỗi giáo viên tách riêng; cơ sở dữ liệu chặn truy cập công khai."),
    (1, "**Công bằng**: phiếu nhóm dùng tên màu trung tính; học sinh làm online biết đúng/sai nhưng không thấy đáp án."),
    (1, "Thí điểm có sự đồng ý của nhà trường và phụ huynh; hình ảnh không lộ mặt học sinh."),
]

TRIEN_KHAI = [
    (1, "Hình thức: ứng dụng web tro-ly-giang-day.streamlit.app dùng trong soạn bài, giờ dạy và đánh giá."),
    (2, "Trước giờ học: soạn phiếu · Trên lớp: in phiếu nhóm hoặc giao bài bằng mã QR · Sau giờ học: chấm, phân tích lỗi · "
        "Buổi sau: dạy bổ trợ."),
    (1, f"Thí điểm: 19–23/10/2026 tại lớp {LOP} ({SI_SO} học sinh), Toán 4 – Bài 14 \"So sánh các số có nhiều chữ số\" và "
        "Bài 15 \"Làm quen với dãy số tự nhiên\"; mời 2–3 đồng nghiệp khối 4 dùng thử."),
    (1, "Quy trình đo: soạn phiếu, giao bài → chấm, phân tích lỗi → 1 buổi bổ trợ → đo lại; "
        "ghi chép bằng bảng in sẵn, khảo sát học sinh và giáo viên."),
    *([(1, f"Số lượng sử dụng: {_g('so_phieu')} phiếu đã soạn, {_g('so_bai')} bài đã chấm (thống kê trong app).")]
      if _co("so_phieu", "so_bai") else []),
]

KET_QUA = [
    (1, f"Kết quả thí điểm bước đầu ({_g('so_ngay')} ngày, {_g('so_hoc_sinh')} học sinh):"),
    (2, f"Giáo viên – soạn 1 phiếu phân hóa: {_g('phut_soan_cu')} → {_g('phut_soan_moi')} phút; "
        f"chấm và nhận xét 1 lớp: {_g('phut_cham_cu')} → {_g('phut_cham_moi')} phút."),
    *([(2, f"AI kiểm định phát hiện {_g('loi_kiem_dinh')} lỗi; giáo viên duyệt và sửa trước khi dùng.")] if _co("loi_kiem_dinh") else []),
    (2, f"Học sinh – tỉ lệ chưa đạt: {_g('phan_tram_chua_dat_truoc')}% → {_g('phan_tram_chua_dat_sau')}% sau 1 buổi bổ trợ."),
    *([(1, f"Phản hồi: \"{PHAN_HOI}\".")] if PHAN_HOI else []),
    (1, "Minh chứng: bảng ghi chép, khảo sát, ảnh phiếu và bài làm (đã che tên), thống kê sử dụng."),
] if CO_KQ else [
    (1, "Thiết kế đánh giá: so sánh trước – sau trên cùng lớp, cùng giáo viên, đo bằng bảng ghi chép và khảo sát."),
    (1, "Chỉ số và mục tiêu thí điểm:"),
    (2, "Thời gian soạn 1 phiếu phân hóa có đáp án: mục tiêu giảm ≥ 50%."),
    (2, "Thời gian chấm và nhận xét 1 lớp: mục tiêu giảm ≥ 40%."),
    (2, "Chất lượng đề: ghi số lỗi AI kiểm định phát hiện và số lỗi giáo viên sửa thêm; 100% đề được giáo viên duyệt."),
    (2, "Học sinh: tỉ lệ chưa đạt giảm sau 1 buổi bổ trợ; ít nhất 80% học sinh thấy bài vừa sức."),
    (1, "Kết quả đo trong tuần thí điểm được trình bày tại vòng chung kết."),
]

THAO_LUAN = [
    (1, "So với cách cũ và chatbot AI phổ thông: một **quy trình hoàn chỉnh theo TT27**, có kiểm định, "
        "phân hóa không dán nhãn, nối liền từ soạn phiếu đến học bạ."),
    (1, "Bền vững, nhân rộng: **0 đồng**; chạy trên trình duyệt; khối 1–5, các môn văn hóa, SGK dùng chung toàn quốc; "
        "nhiều giáo viên dùng song song; có hướng dẫn chuyển giao."),
    (1, "Giới hạn: gói miễn phí giới hạn lượt AI; AI vẫn có thể sai nên luôn cần giáo viên duyệt; "
        "chọn tên khi làm bài online chưa ngăn được làm hộ."),
    (1, "Định hướng: chia sẻ phiếu trong tổ chuyên môn; tin nhắn phụ huynh từ kết quả đánh giá; "
        "tiếp tục theo dõi số liệu trong học kỳ I."),
    (1, "Tác giả phát hiện vấn đề, thiết kế quy trình sư phạm và yêu cầu, trực tiếp triển khai trên lớp; "
        f"phần lập trình có sự hỗ trợ của công cụ AI Claude Code {HO_TRO}."),
]

DINH_KEM = [
    (1, f"Dùng thử sản phẩm (dành cho Ban Giám khảo): {LINK_DEMO}"),
    *([(1, f"Video thuyết trình: {LINK_VIDEO}")] if "⟦" not in LINK_VIDEO else []),
    (1, "Trang chủ: https://tro-ly-giang-day.streamlit.app"),
    *([(1, f"Thư mục minh chứng (khảo sát, ảnh, thống kê): {_g('link_minh_chung')}")] if _co("link_minh_chung") else []),
    (1, "Tài liệu tham khảo: Thông tư 27/2020/TT-BGDĐT; Chương trình GDPT 2018; Quyết định 3588/QĐ-BGDĐT; "
        "SGK Toán 4 – Kết nối tri thức với cuộc sống."),
]


# Lời thuyết trình từng trang (đưa vào phần ghi chú của slide; khớp kịch bản video)
LOI_NOI = [
    f"Xin chào Ban Giám khảo. Tôi là {TEN_GV}, giáo viên lớp {LOP}, {DON_VI[1]}, {DON_VI[2]}. Tôi xin giới thiệu Trợ Lý Giảng Dạy – công cụ AI "
    "giúp giáo viên tiểu học soạn phiếu phân hóa và đánh giá học sinh theo Thông tư 27.",
    "Bài trình bày gồm: bối cảnh và vấn đề, ý tưởng giải pháp theo vòng khép kín 6 bước, các tính năng, cách tôi bảo đảm dùng AI "
    "có trách nhiệm, quá trình triển khai, kết quả và hướng phát triển.",
    f"Lớp tôi có {SI_SO} em với trình độ rất khác nhau. Để mỗi em làm bài vừa sức, tôi phải soạn phiếu ba mức, in cho từng nhóm, chấm và "
    + (f"nhận xét từng em – mỗi phiếu mất khoảng {_g('phut_soan_cu')} phút, chấm cả lớp mất {_g('phut_cham_cu')} phút. " if CO_CU
       else "nhận xét từng em – rất tốn thời gian. ") + "Thử dùng chatbot AI thì câu trả lời rời rạc, "
    "không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra.",
    "Giải pháp của tôi là một vòng khép kín 6 bước theo Thông tư 27. Ở mỗi bước AI đề xuất, giáo viên quyết định. Tôi dùng Google "
    "Gemini vì đọc được ảnh trang sách và chữ viết tay, hỗ trợ tiếng Việt tốt và có gói miễn phí; toàn bộ chi phí là 0 đồng.",
    "Toàn cảnh sản phẩm gồm tám nhóm tính năng: soạn phiếu từ tên bài hoặc ảnh sách giáo khoa; AI kiểm định; in và tải phiếu, "
    "đề A/B, phiếu theo tên; trình chiếu trên lớp; giao bài online bằng mã QR; chấm bài và phân tích lỗi; theo dõi tiến bộ, gợi ý "
    "nhận xét học bạ; và thư viện phiếu, quản lý lớp. Các trang sau đi vào từng bước.",
    "Tôi chỉ cần nhập tên bài hoặc chụp trang sách giáo khoa. Chưa đầy một phút, AI soạn xong phiếu ba mức có đáp án trình bày đúng như "
    "vở học sinh. Sau đó một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu để soát lỗi"
    + (f" – trong thí điểm đã phát hiện {_g('loi_kiem_dinh')} lỗi." if _co("loi_kiem_dinh") else "."),
    "Một phiếu tự tách thành ba phiếu Xanh, Cam, Tím. Tên màu trung tính để các em không cảm thấy bị xếp loại. Có thêm đề A/B "
    "và phiếu in sẵn tên từng em.",
    "Trên lớp, tôi trình chiếu từng câu như trò chơi, hoặc chiếu mã QR để các em làm bài trên máy: chạm vào tên mình, không cần "
    "tài khoản, tự nhận đúng phiếu nhóm, câu trắc nghiệm được chấm ngay.",
    "Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27. Mức đạt tính theo quy tắc công khai và tôi sửa "
    "được từng câu. Biểu đồ cho thấy cả lớp còn yếu ở đâu; một nút bấm là có phiếu bổ trợ đúng chỗ đó.",
    "Kết quả lưu theo từng em; cuối kỳ AI gợi ý nhận xét học bạ dựa trên cả quá trình mà không cần gửi tên học sinh.",
    "Tôi dùng AI có trách nhiệm: giáo viên duyệt mọi đề, mức đạt, nhận xét; có lượt AI thứ hai kiểm định; không gửi danh sách lớp cho AI; "
    "học sinh không cần tài khoản; dữ liệu từng giáo viên tách riêng.",
    f"Tôi đang thí điểm từ 19 đến 23 tháng 10 tại lớp {LOP} với {SI_SO} học sinh, với Bài 14 So sánh các số có nhiều chữ số "
    "và Bài 15 Làm quen với dãy số tự nhiên, và mời đồng nghiệp khối 4 dùng thử.",
    (f"Sau {_g('so_ngay')} ngày thí điểm: soạn phiếu giảm từ {_g('phut_soan_cu')} xuống {_g('phut_soan_moi')} phút, chấm và nhận xét "
     f"từ {_g('phut_cham_cu')} xuống {_g('phut_cham_moi')} phút; tỉ lệ chưa đạt giảm từ {_g('phan_tram_chua_dat_truoc')} "
     f"xuống {_g('phan_tram_chua_dat_sau')} phần trăm sau một buổi bổ trợ. {PHAN_HOI}" if CO_KQ else
     "Tôi đánh giá bằng so sánh trước và sau trên cùng lớp: thời gian soạn phiếu, thời gian chấm và nhận xét, số lỗi AI kiểm định "
     "phát hiện, và tỉ lệ học sinh chưa đạt trước và sau một buổi bổ trợ. Kết quả đo sẽ được trình bày tại vòng chung kết."),
    "So với chatbot AI phổ thông hay các nền tảng tạo đề, trắc nghiệm trực tuyến, điểm khác biệt là một vòng khép kín theo "
    "Thông tư 27: phiếu ba mức có AI kiểm định, phân nhóm không dán nhãn, chấm bài viết tay kèm nhận xét, phân tích lỗi thành "
    "phiếu bổ trợ và gợi ý nhận xét học bạ. Đây là một quy trình hoàn chỉnh theo Thông tư 27. Sản phẩm miễn phí, chạy trên trình duyệt, dùng được cho khối "
    "1 đến 5, bám sát bộ sách giáo khoa dùng chung toàn quốc. Giới hạn hiện tại là quota gói miễn phí và AI vẫn cần giáo viên duyệt. Hướng tới: chia sẻ trong tổ "
    "chuyên môn và tin nhắn phụ huynh.",
    "Mời Ban Giám khảo quét mã QR để dùng thử. Xin cảm ơn!",
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


# Vùng cắt (x0, y0, x1, y1) theo pixel ảnh gốc: bỏ thanh menu, lề trắng để chữ trong ảnh đủ to khi chèn
CAT = {  # ảnh chụp 1600×900 @2x (tao_anh.py), có thanh bên trái
    "02-soan-phieu-kiem-dinh.png": (1560, 380, 3060, 1800),
    "03-gop-y-kiem-dinh.png": (740, 100, 3060, 1800),
    "05-lop-hoc-trinh-chieu.png": (750, 120, 3040, 1730),
    "09-cham-bai-so-tong-hop.png": (740, 300, 3060, 1150),
    "10-phan-tich-loi-sai.png": (740, 540, 3060, 1650),
    "12-tien-bo-bieu-do.png": (740, 440, 3060, 1800),
    "13-lop-cua-toi-phieu-theo-ten.png": (1720, 600, 3060, 1800),
    "20-hs-chon-ten.png": (0, 190, 1170, 1600),
    "21-hs-lam-cau.png": (0, 190, 1170, 2160),
    "31-phieu-xanh.png": (0, 110, 1588, 1950),
    "32-dap-an-ma-tran.png": (0, 110, 1588, 1500),
}


def tep_anh(ten):
    duong = RA / ten if (RA / ten).exists() else ANH / ten
    if not duong.exists() or ten not in CAT:
        return duong
    from PIL import Image
    ra = Path(tempfile.gettempdir()) / f"cat-{ten}"
    Image.open(duong).crop(CAT[ten]).save(ra)
    return ra


def xep_anh(slide, ds, trai, tren, rong, cao, khe=Inches(0.2)):
    """Xếp các ảnh vào vùng cho trước: thử 1 hàng (cùng cao) và 1 cột (cùng rộng), chọn cách cho ảnh to hơn."""
    from PIL import Image
    tl = [(lambda im: im.width / im.height)(Image.open(tep_anh(a))) for a in ds]
    h_hang = min(cao, (rong - khe * (len(ds) - 1)) / sum(tl))
    w_cot = min(rong, (cao - khe * (len(ds) - 1)) / sum(1 / t for t in tl))
    if h_hang * h_hang * sum(tl) >= w_cot * w_cot * sum(1 / t for t in tl):
        x = trai + (rong - h_hang * sum(tl) - khe * (len(ds) - 1)) / 2
        for a, t in zip(ds, tl):
            anh_vua_khung(slide, a, int(x), int(tren + (cao - h_hang) / 2), int(h_hang * t), int(h_hang))
            x += h_hang * t + khe
    else:
        y = tren + (cao - w_cot * sum(1 / t for t in tl) - khe * (len(ds) - 1)) / 2
        for a, t in zip(ds, tl):
            anh_vua_khung(slide, a, int(trai + (rong - w_cot) / 2), int(y), int(w_cot), int(w_cot / t))
            y += w_cot / t + khe


def anh_vua_khung(slide, ten, trai, tren, rong, cao, vien=True):
    duong = tep_anh(ten)
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
    for rpr in tim(bia, "TextBox 11")._element.iter(qn("a:rPr")):  # mẫu đặt giãn chữ âm (-322): chữ dính nhau
        rpr.set("spc", "0")
    nhom = tim(bia, "Group 3")
    xf = nhom._element.grpSpPr.find(qn("a:xfrm"))
    tl = int(xf.find(qn("a:ext")).get("cx")) / int(xf.find(qn("a:chExt")).get("cx"))  # nhóm được thu nhỏ
    ox, oy = int(xf.find(qn("a:chOff")).get("x")), int(xf.find(qn("a:chOff")).get("y"))
    for sh in list(nhom.shapes):
        if sh.name == "TextBox 5":
            viet(sh, [(0, TEN_GV)])
            sh.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            sh.left, sh.width = sh.left - sh.width // 2, sh.width * 2  # đủ rộng cho họ tên 4 chữ trên 1 dòng
        if sh.name == "Group 6":  # ảnh người mẫu của Ban Tổ chức: thay bằng khung trống
            x = nhom.left + int((sh.left - ox) * tl)
            y = nhom.top + int((sh.top - oy) * tl)
            w, h = int(sh.width * tl), int(sh.height * tl)
            xoa(sh)
    if (RA / "chan-dung.jpg").exists():  # ảnh chân dung vuông (ban-nop/, không đưa lên GitHub) → cắt tròn
        from PIL import Image, ImageDraw
        anh = Image.open(RA / "chan-dung.jpg").convert("RGBA")
        mat_na = Image.new("L", anh.size, 0)
        ImageDraw.Draw(mat_na).ellipse((0, 0, *anh.size), fill=255)
        anh.putalpha(mat_na)
        anh.save(RA / "chan-dung-tron.png")
        d = min(w, h)
        bia.shapes.add_picture(str(RA / "chan-dung-tron.png"), x + (w - d) // 2, y + (h - d) // 2, d, d)
    else:
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
            than.width = Inches(7.4)
            xep_anh(t, anh, Inches(8.3), Inches(2.25), Inches(11.2), Inches(7.55))  # dưới tiêu đề dài
        trang_tn.append(t)

    viet(tim(trien_khai, "TextBox 3"), TRIEN_KHAI, co=28, mau_p=mau_than)
    tim(trien_khai, "TextBox 3").height = Inches(7.4)
    viet(tim(ket_qua, "TextBox 3"), KET_QUA, co=27, mau_p=mau_than)
    tim(ket_qua, "TextBox 3").height = Inches(7.4)
    viet(tim(thao_luan, "TextBox 3"), THAO_LUAN[1:], co=19, mau_p=mau_than)  # ý so sánh đã nằm trong bảng
    tim(thao_luan, "TextBox 3").top, tim(thao_luan, "TextBox 3").height = Inches(6.65), Inches(3.1)
    than = tim(dinh_kem, "TextBox 3")
    viet(than, DINH_KEM, co=25, mau_p=mau_than)
    than.width, than.height = Inches(12.4), Inches(7.4)
    for k, (q, nhan) in enumerate(qr_co_san()):
        y = Inches(2.2 + k * 2.55)
        anh_vua_khung(dinh_kem, q, Inches(14.2), y, Inches(2.1), Inches(2.1), vien=False)
        tb = dinh_kem.shapes.add_textbox(Inches(16.5), y + Inches(0.75), Inches(3), Inches(0.6)).text_frame
        tb.text = nhan; tb.paragraphs[0].runs[0].font.size = Pt(22); tb.paragraphs[0].runs[0].font.bold = True
        tb.paragraphs[0].runs[0].font.color.rgb = NAVY

    trang_toan_canh(prs, trien_khai)
    bang_so_sanh(thao_luan, Inches(2.2), Inches(4.25), 14)
    # Thứ tự: bìa, dàn ý, bối cảnh, ý tưởng, toàn cảnh, 5 tính năng, trách nhiệm, triển khai, kết quả, thảo luận (+ bảng so sánh),
    # đính kèm (chỉ số hiện có: 0..8 là mẫu gốc, 9..15 là trang nhân bản; bỏ trang 2 = hướng dẫn) → 15 trang
    xep_thu_tu(prs, [0, 1, 2, 3, 4, 15, 9, 10, 11, 12, 13, 14, 5, 6, 7, 8])
    xoa_trang(prs, 2)
    for trang, loi in zip(prs.slides, LOI_NOI):  # lời thuyết trình vào phần ghi chú (không hiện khi xuất PDF)
        trang.notes_slide.notes_text_frame.text = loi
    RA.mkdir(exist_ok=True)
    ra = RA / "Slide-du-thi.pptx"
    prs.save(ra)
    print(f"Đã tạo {ra} ({len(prs.slides)} trang)")


def qr_co_san() -> list[tuple[str, str]]:
    """Các mã QR đã có ảnh (QR video chỉ có sau khi tải video lên Drive)."""
    ds = [("qr-trai-nghiem.png", "Dùng thử"), ("qr-video.png", "Video"), ("qr-app.png", "Trang chủ")]
    return [(q, n) for q, n in ds if (RA / q).exists() or (ANH / q).exists()]


SO_SANH = [  # (tiêu chí, chatbot AI phổ thông, nền tảng tạo đề / trắc nghiệm trực tuyến, Trợ Lý Giảng Dạy)
    ("Soạn phiếu 3 mức TT27, đáp án trình bày chuẩn tiểu học",
     "Được nếu tự viết lệnh; định dạng không cố định", "Chủ yếu chọn từ ngân hàng câu hỏi", "Tự soạn từ tên bài hoặc ảnh trang SGK"),
    ("Kiểm tra lại đáp án, mức độ", "Người dùng tự kiểm tra", "Tùy nền tảng", "Lượt AI thứ hai tự giải lại, góp ý từng câu"),
    ("Phân hóa theo nhóm", "Không có sẵn", "Giao bài theo lớp/nhóm", "Tự tách phiếu Xanh/Cam/Tím, không dán nhãn"),
    ("Chấm bài viết tay, nhận xét TT27", "Đọc được ảnh, cần hướng dẫn từng lần", "Chủ yếu chấm bài làm trực tuyến",
     "Chụp ảnh cả lớp → mức hoàn thành + nhận xét"),
    ("Từ lỗi sai đến dạy bổ trợ", "Không có sẵn", "Thống kê kết quả", "Phân tích lỗi → một nút soạn phiếu bổ trợ"),
    ("Nhận xét học bạ cuối kỳ", "Không có sẵn", "Tùy nền tảng", "Gợi ý theo cả quá trình, không gửi tên học sinh"),
    ("Chi phí với giáo viên", "Miễn phí hoặc trả phí", "Có gói miễn phí và trả phí", "0 đồng"),
]


def bang_so_sanh(slide, tren, cao, co):
    """Bảng so sánh với các cách làm hiện nay (tiêu chí Sáng tạo), đặt trên trang Thảo luận."""
    hang, cot = len(SO_SANH) + 1, 4
    bang = slide.shapes.add_table(hang, cot, Inches(0.8), tren, Inches(18.4), cao).table
    for j, w in enumerate((4.6, 4.2, 4.2, 5.4)):
        bang.columns[j].width = Inches(w)
    tieu_de = ("So sánh với cách làm hiện nay", "Chatbot AI phổ thông", "Nền tảng tạo đề, trắc nghiệm trực tuyến",
               "Trợ Lý Giảng Dạy")
    for i, dong in enumerate([tieu_de, *SO_SANH]):
        bang.rows[i].height = int(cao / hang)
        for j, chu in enumerate(dong):
            o = bang.cell(i, j)
            o.text = chu
            o.margin_left = o.margin_right = Inches(0.1)
            o.margin_top = o.margin_bottom = Inches(0.03)
            o.fill.solid()
            o.fill.fore_color.rgb = NAVY if i == 0 else (RGBColor(0xE3, 0xF2, 0xE8) if j == 3 else (NEN if i % 2 else RGBColor(0xFF, 0xFF, 0xFF)))
            for para in o.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size, r.font.name = Pt(co), "Aptos"
                    r.font.bold = i == 0 or j in (0, 3)
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if i == 0 else (RGBColor(0x1B, 0x5E, 0x20) if j == 3 else NAVY)


TOAN_CANH = [  # 8 nhóm tính năng (mỗi nhóm một khu vực của ứng dụng)
    ("① Soạn phiếu", ["Từ tên bài hoặc ảnh trang SGK (tối đa 3 ảnh)", "Phiếu 3 mức TT27, 5 dạng bài, 15/20/35 phút",
                     "Đáp án chuẩn tiểu học, hướng dẫn chấm, ma trận, yêu cầu cần đạt", "Đổi câu, dễ hơn, khó hơn, sửa tay, hoàn tác"]),
    ("② AI kiểm định", ["\"Tổ trưởng chuyên môn\" AI tự giải lại từng câu", "Chấm chất lượng phiếu (VD 95/100), chỉ ra lỗi từng câu",
                       "Một nút \"Sửa theo góp ý\"; kiểm định lại sau khi sửa", "Tự chuyển mô hình AI dự phòng khi quá tải"]),
    ("③ In & tải phiếu", ["Phiếu chung, Phiếu Xanh/Cam/Tím, đáp án", "In A4, chọn cỡ chữ 14–18pt",
                         "Tải Word, tải trọn bộ (.zip)", "Đề A/B chống nhìn bài; phiếu in sẵn tên từng em"]),
    ("④ Trình chiếu trên lớp", ["Từng câu toàn màn hình, kiểu trò chơi", "Đếm giờ, lật đáp án", "Gọi bạn ngẫu nhiên, đọc to câu hỏi",
                               "Điều khiển bằng phím tắt"]),
    ("⑤ Giao bài online", ["Mã QR/link, học sinh chạm tên, không cần tài khoản", "Mỗi em nhận đúng phiếu của nhóm",
                          "Đặt hạn nộp, đóng/mở bài, cho em làm lại", "Theo dõi trực tiếp; tự chấm trắc nghiệm, AI chấm tự luận"]),
    ("⑥ Chấm & phân tích lỗi", ["Chụp ảnh tối đa 40 bài, AI đọc chữ viết tay", "Nhận xét từng em theo TT27; chấm tay, sửa mọi ô",
                               "Biểu đồ câu sai, lỗi thường gặp → phiếu bổ trợ", "Sổ tổng hợp Excel; cập nhật nhóm Xanh/Cam/Tím"]),
    ("⑦ Tiến bộ & học bạ", ["Mức hoàn thành từng em qua các lần đánh giá", "Biểu đồ tiến bộ từng em",
                           "Gợi ý nhận xét học bạ cả lớp, không gửi tên", "Xuất nhận xét học bạ Excel"]),
    ("⑧ Thư viện & lớp của tôi", ["Phiếu tự lưu; gắn sao, nhân bản, nhập/xuất file", "Nhiều lớp; dán nhanh danh sách tên",
                                 "Đăng nhập Google, dữ liệu riêng từng giáo viên", "Trang chủ: thống kê, thời gian tiết kiệm"]),
]


def trang_toan_canh(prs, mau):
    """Trang tổng quan: 8 nhóm tính năng thành lưới 4 × 2."""
    t = nhan_ban(prs, mau)
    viet(tim(t, "TextBox 2"), [(0, "TOÀN CẢNH TÍNH NĂNG")])
    tim(t, "TextBox 2").width = Inches(17)
    xoa(tim(t, "TextBox 3"))
    X, Y, W, H, G = Inches(0.8), Inches(2.2), Inches(18.4), Inches(7.5), Inches(0.22)
    w, h = (W - 3 * G) / 4, (H - G) / 2
    for k, (ten, ds) in enumerate(TOAN_CANH):
        x, y = X + int((w + G) * (k % 4)), Y + int((h + G) * (k // 4))
        o = t.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, int(w), int(h))
        o.adjustments[0] = 0.05
        o.fill.solid(); o.fill.fore_color.rgb = NEN; o.line.color.rgb = RGBColor(0xCF, 0xD8, 0xE6); o.shadow.inherit = False
        dau = t.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, int(w), Inches(0.7))
        dau.adjustments[0] = 0.25
        dau.fill.solid(); dau.fill.fore_color.rgb = NAVY2; dau.line.fill.background(); dau.shadow.inherit = False
        tf = dau.text_frame
        tf.margin_left = Inches(0.15)
        r = tf.paragraphs[0].add_run(); r.text = ten
        r.font.size, r.font.bold, r.font.name, r.font.color.rgb = Pt(20), True, "Aptos", RGBColor(0xFF, 0xFF, 0xFF)
        than = t.shapes.add_textbox(x + Inches(0.1), y + Inches(0.8), int(w) - Inches(0.2), int(h) - Inches(0.85)).text_frame
        than.word_wrap = True
        for i, chu in enumerate(ds):
            para = than.paragraphs[0] if i == 0 else than.add_paragraph()
            para.space_after = Pt(7)
            r = para.add_run(); r.text = "• " + chu
            r.font.size, r.font.name, r.font.color.rgb = Pt(17), "Aptos", NAVY
    return t


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
    y, h = Inches(11.2), Inches(8.4)
    w1 = Inches(13.4)
    khoi(s, X, y, w1, h, "1. BỐI CẢNH VÀ VẤN ĐỀ")
    doan(s, X + Inches(0.5), y + Inches(1.6), w1 - Inches(1), h - Inches(1.8), [
        f"• Lớp {LOP}: {SI_SO} học sinh, trình độ chênh lệch rõ.",
        "• TT27: nhận xét thường xuyên; đề định kỳ theo **3 mức**.",
        *([f"• Soạn 1 phiếu phân hóa có đáp án ≈ {_g('phut_soan_cu')} phút; chấm và nhận xét 1 lớp ≈ {_g('phut_cham_cu')} phút."]
          if CO_CU else ["• Soạn 3 mức kèm đáp án, in theo nhóm, chấm và nhận xét từng em: tốn nhiều thời gian."]),
        "• Chatbot AI phổ thông: rời rạc, không theo TT27, không có bước kiểm tra đáp án.",
        "• **Đối tượng hưởng lợi:** học sinh và giáo viên tiểu học."], co=36)
    x2, w2 = X + w1 + G, W - w1 - G
    khoi(s, x2, y, w2, h, "2. GIẢI PHÁP: VÒNG KHÉP KÍN")
    anh_vua_khung(s, "so-do-vong-khep-kin.png", x2 + Inches(0.4), y + Inches(1.5), w2 - Inches(0.8), h - Inches(2.6), vien=False)
    doan(s, x2 + Inches(0.5), y + h - Inches(1.1), w2 - Inches(1), Inches(1),
         ["AI đề xuất – **giáo viên quyết định**. Công cụ AI: Google Gemini (soạn, kiểm định, chấm ảnh, gợi ý nhận xét)."], co=28)

    # Hàng 2: 6 ảnh
    y, h = y + h + G, Inches(15.6)
    khoi(s, X, y, W, h, "3. AI HOẠT ĐỘNG THẾ NÀO")
    anh6 = [("02-soan-phieu-kiem-dinh.png", "①② Soạn phiếu 3 mức từ ảnh SGK, AI tự kiểm định"),
            ("32-dap-an-ma-tran.png", "Ma trận và đáp án trình bày chuẩn tiểu học"),
            ("31-phieu-xanh.png", "③a Phiếu Xanh/Cam/Tím – không gọi \"yếu/giỏi\""),
            ("21-hs-lam-cau.png", "③b Quét QR, chọn tên, làm bài trên điện thoại"),
            ("10-phan-tich-loi-sai.png", "④⑤ Chấm, nhận xét, phân tích lỗi → phiếu bổ trợ"),
            ("12-tien-bo-bieu-do.png", "⑥ Tiến bộ từng em, gợi ý nhận xét học bạ")]
    cw, ch = (W - Inches(1.4)) / 3, (h - Inches(1.8)) / 2
    for k, (a, cap) in enumerate(anh6):
        cx = X + Inches(0.5) + int(cw * (k % 3))
        cy = y + Inches(1.6) + int((k // 3) * (ch + Inches(0.1)))
        anh_vua_khung(s, a, cx, cy, int(cw) - Inches(0.3), int(ch) - Inches(1.1))
        tf = doan(s, cx, cy + int(ch) - Inches(1.05), int(cw) - Inches(0.3), Inches(1), [cap], co=28)
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Hàng 3: Kết quả | Trách nhiệm + Bền vững
    y, h = y + h + G, Inches(6.6)
    khoi(s, X, y, w1, h, "4. KẾT QUẢ THỰC TẾ" if CO_KQ else "4. THÍ ĐIỂM & MỤC TIÊU")
    doan(s, X + Inches(0.5), y + Inches(1.6), w1 - Inches(1), h - Inches(1.8), [
        f"• Soạn 1 phiếu: {_g('phut_soan_cu')} → {_g('phut_soan_moi')} phút",
        f"• Chấm và nhận xét 1 lớp: {_g('phut_cham_cu')} → {_g('phut_cham_moi')} phút",
        f"• Sau bổ trợ: chưa đạt {_g('phan_tram_chua_dat_truoc')}% → {_g('phan_tram_chua_dat_sau')}%",
        *([f"\"{PHAN_HOI}\""] if PHAN_HOI else [])] if CO_KQ else [
        f"• Lớp {LOP} ({SI_SO} học sinh), 19–23/10/2026.",
        "• Soạn 1 phiếu: mục tiêu giảm ≥ 50% thời gian.",
        "• Chấm, nhận xét 1 lớp: mục tiêu giảm ≥ 40% thời gian.",
        "• Tỉ lệ chưa đạt giảm sau 1 buổi bổ trợ.",
        "• Khảo sát học sinh 4A3 và đồng nghiệp dùng thử."], co=34)
    khoi(s, x2, y, w2, h, "5. TRÁCH NHIỆM · BỀN VỮNG")
    doan(s, x2 + Inches(0.5), y + Inches(1.6), w2 - Inches(1), h - Inches(1.8), [
        "• Giáo viên duyệt mọi đề, mức đạt, nhận xét; AI kiểm định lượt 2.",
        "• Không gửi danh sách lớp cho AI; học sinh không cần tài khoản.",
        "• **0 đồng**, chạy trên trình duyệt; lớp 1–5, SGK dùng chung toàn quốc.",
        "• Định hướng: nhân rộng trong tổ chuyên môn; gửi nhận xét cho phụ huynh."], co=34)

    # Hàng 4: QR + công khai
    y = y + h + Inches(0.35)
    qr = qr_co_san()
    buoc = W / len(qr)
    for k, (q, nhan) in enumerate(qr):  # chia đều bề ngang, mỗi nhóm (QR 2,3" + nhãn) căn giữa ô của mình
        cx = X + int(buoc * k + (buoc - Inches(6.8)) / 2)
        anh_vua_khung(s, q, cx, y, Inches(2.3), Inches(2.3), vien=False)
        doan(s, cx + Inches(2.5), y + Inches(0.75), Inches(4.5), Inches(1), [f"**{nhan}**"], co=40)
    doan(s, X, y + Inches(2.4), W, Inches(0.6),
         ["Tác giả thiết kế quy trình sư phạm và triển khai trên lớp; phần lập trình có sự hỗ trợ của công cụ AI "
          f"Claude Code {HO_TRO}."], co=24
         ).paragraphs[0].alignment = PP_ALIGN.CENTER
    RA.mkdir(exist_ok=True)
    ra = RA / "Poster-du-thi.pptx"
    prs.save(ra)
    print(f"Đã tạo {ra}")


def xuat_pdf():
    """Xuất PDF để nộp (nhúng phông Aptos có sẵn trong mẫu, hiển thị giống nhau trên mọi máy)."""
    import subprocess
    for ten in ("Slide-du-thi", "Poster-du-thi"):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(RA), str(RA / f"{ten}.pptx")],
                       check=True, capture_output=True)
        print(f"Đã xuất {RA / ten}.pdf")


if __name__ == "__main__":
    lam_slide()
    lam_poster()
    xuat_pdf()
