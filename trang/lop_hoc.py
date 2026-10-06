import streamlit as st

import classroom_html as cx
import state

st.markdown("## 🎬 Chế độ Lớp học")
st.caption("Trình chiếu phiếu lên máy chiếu/TV: từng câu chữ lớn, đếm giờ, lật đáp án, gọi tên ngẫu nhiên, đọc to câu hỏi.")

ban = state.can_phieu()
lop = st.session_state.get("lop")
ten_hs = [h.ten for h in lop.hoc_sinh if h.ten.strip()] if lop else []

c1, c2, c3 = st.columns([2, 1, 2], vertical_alignment="bottom")
giay = c1.segmented_control("Đếm giờ mỗi câu", [0, 30, 60, 90], default=60, key="lh_giay",
                            format_func=lambda x: "Tắt" if x == 0 else f"{x} giây")
doc_to = c2.toggle("🔊 Tự đọc câu hỏi", key="lh_doc", help="Dùng giọng tiếng Việt có sẵn của trình duyệt (Chrome/Edge)")
if ten_hs:
    c3.success(f"🎲 Vòng quay có {len(ten_hs)} học sinh từ *Lớp của tôi*")
else:
    c3.page_link(state.TRANG["lop_cua_toi"], label="Thêm danh sách lớp để gọi tên học sinh", icon="👥")

st.iframe(cx.trinh_chieu(ban, ten_hs, giay or 0, doc_to), height=720)
st.caption("⌨️ Phím tắt (bấm vào khung trình chiếu trước): → / ← chuyển câu · Space lật đáp án · T đếm giờ · "
           "R đọc to · G gọi bạn · F toàn màn hình")
