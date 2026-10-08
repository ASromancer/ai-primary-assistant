import html

import streamlit as st

import state

ten = state.ten_gv().strip()
st.html(f"""<div class="banner"><div class="t">👋 Chào {html.escape(ten) if ten else "thầy cô"}! Hôm nay mình soạn gì nhé?</div>
<div class="s">Trợ lý AI soạn phiếu phân hóa 3 mức theo Thông tư 27/2020/TT-BGDĐT – soạn, kiểm định, dạy trên lớp,
chấm bài và chia nhóm học sinh trong một nơi.</div></div>""")

tk = None
if state.ca_nhan():
    try:
        tk = state.doc("thong_ke")
        cols = st.columns(4)
        cols[0].metric("📝 Phiếu đã soạn", tk["so_phieu"], border=True)
        cols[1].metric("📷 Bài đã chấm", tk["so_bai_cham"], border=True)
        cols[2].metric("👥 Lớp · học sinh", f"{tk['so_lop']} · {tk['so_hoc_sinh']}", border=True)
        cols[3].metric("⏱️ Thời gian tiết kiệm", f"~{state.so_vn(tk['gio_tiet_kiem'])} giờ", border=True,
                       help="Ước tính: 40 phút soạn một phiếu có đáp án và ma trận, 3 phút chấm và nhận xét một bài")
    except Exception as e:
        st.warning(f"Chưa đọc được thống kê từ database: {e}")
elif not state.email():
    with st.container(border=True, horizontal=True, vertical_alignment="center"):
        st.markdown("**🔐 Bạn đang dùng chế độ khách.** Đăng nhập để tự lưu phiếu vào thư viện, "
                    "quản lý nhiều lớp và theo dõi tiến bộ từng học sinh.", width="stretch")
        state.nut_dang_nhap("dang_nhap_home")

CHUC_NANG = [
    ("soan_phieu", "✍️", "Soạn phiếu", "Phiếu 3 mức TT27 từ tên bài hoặc ảnh SGK. AI tự kiểm định, in ngay hoặc tải Word."),
    ("lop_hoc", "🎬", "Lớp học", "Trình chiếu từng câu, đếm giờ, lật đáp án, gọi tên ngẫu nhiên, đọc to câu hỏi."),
    ("cham_bai", "📷", "Chấm bài", "Chụp bài làm cả lớp – AI chấm, nhận xét theo TT27, xuất sổ tổng hợp Excel."),
    ("lop_cua_toi", "👥", "Lớp của tôi", "Danh sách học sinh theo nhóm, in phiếu có sẵn tên từng em, đề A/B."),
]
cols = st.columns(4)
for col, (trang, icon, ten_cn, mo_ta) in zip(cols, CHUC_NANG):
    with col.container(border=True, height="stretch"):
        st.markdown(f"### {icon}\n**{ten_cn}**")
        st.caption(mo_ta)
        st.page_link(state.TRANG[trang], label=f"Mở {ten_cn}", icon="➡️")



def mau_kd(diem: int) -> str:
    return "green" if diem >= 85 else "orange" if diem >= 70 else "red"


trai, phai = st.columns([3, 2], gap="large")
with trai:
    st.markdown("#### 🕘 Phiếu gần đây")
    if state.ca_nhan():  # từ thư viện trên database
        gan_day = state.doc("phieu_ds")[:5]
        for p in gan_day:
            with st.container(border=True, horizontal=True, vertical_alignment="center"):
                st.markdown(f"**{'⭐ ' if p['gan_sao'] else ''}{state.md(p['chu_de'])}**  \n"
                            f"{p['mon']} · Lớp {p['lop']} · {p['so_cau']} câu · {p['sua_luc'][5:10]}", width="stretch")
                if p["diem_kd"] is not None:
                    st.badge(f"Kiểm định {p['diem_kd']}/100", color=mau_kd(p["diem_kd"]))
                if st.button("Mở", key=f"mo_{p['id']}"):
                    state.dat_phieu(state.doc("phieu_mo", p["id"]))
                    st.switch_page(state.TRANG["soan_phieu"])
        if gan_day:
            st.page_link(state.TRANG["thu_vien"], label="Xem tất cả trong Thư viện", icon="📚")
    else:
        gan_day = st.session_state.get("lich_su", [])
        for k, b in enumerate(gan_day):
            ts = b.thong_so
            with st.container(border=True, horizontal=True, vertical_alignment="center"):
                st.markdown(f"**{state.md(ts.chu_de)}**  \n{ts.mon} · Lớp {ts.lop} · {len(b.phieu.cau_hoi)} câu",
                            width="stretch")
                if b.kiem_dinh:
                    st.badge(f"Kiểm định {b.kiem_dinh.diem}/100", color=mau_kd(b.kiem_dinh.diem))
                if st.button("Mở", key=f"mo{k}"):
                    state.dat_phieu(b)
                    st.switch_page(state.TRANG["soan_phieu"])
    if not gan_day:
        st.caption("Chưa có phiếu nào.")
        if st.button("👀 Mở phiếu mẫu để xem thử", type="primary", key="mau_home"):
            state.mo_phieu(state.PHIEU_MAU.read_text(encoding="utf-8"))
            st.switch_page(state.TRANG["soan_phieu"])

with phai:
    buoc = [("Đặt tên trường (ô ở thanh bên trái)", bool(state.truong()), None),
            ("Tạo lớp và nhập danh sách học sinh", bool(tk and tk["so_lop"]), "lop_cua_toi"),
            ("Soạn phiếu đầu tiên", bool(tk and tk["so_phieu"]), "soan_phieu"),
            ("Chấm bài và lưu vào hồ sơ lớp", bool(tk and tk["so_bai_cham"]), "cham_bai")]
    xong = sum(d for _, d, _ in buoc)
    if tk is not None and xong < len(buoc):  # danh sách việc cho giáo viên mới, ẩn khi đã làm đủ
        with st.container(border=True):
            st.markdown(f"#### 🚀 Bắt đầu nhanh · {xong}/{len(buoc)}")
            st.progress(xong / len(buoc))
            for ten_buoc, da_xong, trang in buoc:
                if da_xong:
                    st.markdown(f"✅ ~~{ten_buoc}~~")
                elif trang:
                    st.page_link(state.TRANG[trang], label=ten_buoc, icon="⬜")
                else:
                    st.markdown(f"⬜ {ten_buoc}")
    else:
        st.markdown("#### 💡 Quy trình gợi ý")
        st.html("""<div class="buoc doc">
<div><b>1. Soạn & kiểm định</b><p>Nhập tên bài hoặc chụp trang SGK. AI soạn 3 mức và tự soát lỗi đáp án.</p></div>
<div><b>2. Dạy trên lớp</b><p>Trình chiếu phiếu ở trang Lớp học, gọi tên ngẫu nhiên, lật đáp án.</p></div>
<div><b>3. Chấm & chia nhóm</b><p>Chụp bài làm, AI chấm, phân tích lỗi sai và soạn phiếu bổ trợ.</p></div>
</div>""")
