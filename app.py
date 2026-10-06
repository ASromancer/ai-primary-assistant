import streamlit as st

import state

st.set_page_config(page_title="Trợ Lý Phân Hóa Tiểu Học - TT27", page_icon="📚", layout="wide")

st.html("""<style>
.block-container { padding-top: 4.5rem; }
.banner { background: linear-gradient(120deg, #0D47A1, #1E88E5 60%, #42A5F5); color: #fff;
          padding: 20px 28px; border-radius: 18px; margin-bottom: 6px; box-shadow: 0 6px 20px rgba(21,101,192,.18); }
.banner .t { font-size: 1.7rem; font-weight: 700; line-height: 1.25; }
.banner .s { opacity: .92; margin-top: 4px; font-size: .95rem; }
.buoc { display: flex; gap: 14px; flex-wrap: wrap; margin: 8px 0 14px; }
.buoc > div { flex: 1 1 200px; background: #F1F6FD; border: 1px solid #DCE8F8; border-radius: 14px; padding: 16px; }
.buoc b { color: #0D47A1; font-size: 1.05rem; }
.buoc p { margin: 6px 0 0; color: #444; font-size: .92rem; }
.buoc.doc { flex-direction: column; }
.buoc.doc > div { flex: none; }
</style>""")

# Giữ giá trị ô cài đặt khi chuyển trang (Streamlit xoá state của widget không còn hiển thị)
for k in ("api_key_nhap", "ten_gv", "truong"):
    if k in st.session_state:
        st.session_state[k] = st.session_state[k]

with st.sidebar:
    st.subheader("⚙️ Cài đặt")
    if not state._secret("GEMINI_API_KEY"):
        st.text_input("Gemini API Key", type="password", key="api_key_nhap",
                      help="Lấy miễn phí tại https://aistudio.google.com/apikey")
    st.text_input("Tên giáo viên", key="ten_gv", placeholder="VD: Nguyễn Thị Lan")
    st.text_input("Tên trường (in trên phiếu)", key="truong", placeholder="VD: Tiểu học Nguyễn Trãi")

    st.subheader("🕘 Phiếu trong phiên này")
    lich_su = st.session_state.get("lich_su", [])
    if not lich_su:
        st.caption("Chưa có phiếu nào.")
    for k, b in enumerate(lich_su):
        if st.button(f"{b.thong_so.mon} {b.thong_so.lop} · {b.thong_so.chu_de[:38]}", key=f"ls{k}", width="stretch",
                     type="primary" if b is st.session_state.get("ban") else "secondary"):
            state.dat_phieu(b)
            st.rerun()

    st.subheader("📂 Mở phiếu đã lưu")
    f = st.file_uploader("File .json đã lưu từ ứng dụng", type="json", label_visibility="collapsed")
    if f and st.button("Mở phiếu này", width="stretch"):
        state.mo_phieu(f.getvalue())
        st.rerun()
    if st.button("👀 Phiếu mẫu (không cần API key)", width="stretch", key="mau_sb"):
        state.mo_phieu(state.PHIEU_MAU.read_text(encoding="utf-8"))
        st.rerun()
    st.caption(f"Mô hình AI: `{state.MODEL}` (tự chuyển model dự phòng khi quá tải).")

st.navigation([
    st.Page(state.TRANG["trang_chu"], title="Trang chủ", icon="🏠", default=True),
    st.Page(state.TRANG["soan_phieu"], title="Soạn phiếu", icon="✍️"),
    st.Page(state.TRANG["lop_hoc"], title="Lớp học", icon="🎬"),
    st.Page(state.TRANG["cham_bai"], title="Chấm bài", icon="📷"),
    st.Page(state.TRANG["lop_cua_toi"], title="Lớp của tôi", icon="👥"),
], position="top").run()
