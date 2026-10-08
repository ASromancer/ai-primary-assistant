import streamlit as st

import state
from danh_gia import bo_dau

st.markdown("## 📚 Thư viện phiếu của tôi")
st.caption("Mọi phiếu đã soạn được lưu tự động. Tìm lại, gắn sao, nhân bản để soạn phiếu mới từ phiếu cũ.")

if not state.ca_nhan():
    st.info("🔐 Đăng nhập để lưu và xem lại thư viện phiếu."
            if not state.email() else "⚠️ Chưa cấu hình database (khối [connections.sql] trong Secrets).")
    if not state.email():
        state.nut_dang_nhap("tv_dang_nhap")
    st.stop()

with st.popover("📥 Nhập phiếu từ file .json"):
    f = st.file_uploader("File .json đã lưu từ ứng dụng", type="json", key="tv_nhap")
    if f and st.button("Nhập vào thư viện", type="primary", key="tv_nhap_btn"):
        state.mo_phieu(f.getvalue())
        if "ban" in st.session_state:
            st.session_state.ban.id = ""  # luôn tạo bản ghi mới của mình
            st.switch_page(state.TRANG["soan_phieu"])

try:
    ds = state.doc("phieu_ds")
except Exception as e:
    state.bao_loi(e)
    st.stop()

if not ds:
    st.info("Thư viện còn trống. Phiếu bạn soạn sẽ tự xuất hiện ở đây.")
    st.page_link(state.TRANG["soan_phieu"], label="Soạn phiếu đầu tiên", icon="✍️")
    st.stop()

c1, c2, c3, c4 = st.columns([3, 1.4, 1, 1.2], vertical_alignment="bottom")
tim = c1.text_input("Tìm theo chủ đề", placeholder="VD: phep cong (gõ có dấu hay không dấu đều được)")
mon = c2.selectbox("Môn", ["Tất cả", *sorted({p["mon"] for p in ds})])
lop = c3.selectbox("Lớp", ["Tất cả", *sorted({p["lop"] for p in ds})])
chi_sao = c4.toggle("⭐ Đã gắn sao")

khoa = bo_dau(tim).lower().split()
loc = [p for p in ds
       if all(k in bo_dau(p["chu_de"]).lower() for k in khoa)
       and mon in ("Tất cả", p["mon"]) and lop in ("Tất cả", p["lop"]) and (p["gan_sao"] or not chi_sao)]
st.caption(f"Hiển thị {len(loc)}/{len(ds)} phiếu")

dang_mo = getattr(st.session_state.get("ban"), "id", "")


def mo(id: str, nhan_ban: bool = False):
    ban = state.doc("phieu_mo", id)
    if ban is None:
        st.error("Không tìm thấy phiếu.")
        return
    if nhan_ban:
        ban.id = ""  # lần tự lưu kế tiếp sẽ tạo bản ghi mới
        ban.thong_so.chu_de += " (bản sao)"
    state.dat_phieu(ban)
    st.switch_page(state.TRANG["soan_phieu"])


cols = st.columns(2)
for k, p in enumerate(loc):
    with cols[k % 2].container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**{'⭐ ' if p['gan_sao'] else ''}{state.md(p['chu_de'])}**")
            if p["id"] == dang_mo:
                st.badge("Đang mở", color="blue")
        with st.container(horizontal=True, vertical_alignment="center"):
            st.caption(f"{p['mon']} · Lớp {p['lop']} · {p['so_cau']} câu · sửa {p['sua_luc']}")
            if p["diem_kd"] is not None:
                st.badge(f"Kiểm định {p['diem_kd']}/100",
                         color="green" if p["diem_kd"] >= 85 else "orange" if p["diem_kd"] >= 70 else "red")
        with st.container(horizontal=True):
            if st.button("Mở", key=f"tv_mo_{p['id']}", type="primary"):
                mo(p["id"])
            if st.button("⧉ Nhân bản", key=f"tv_nb_{p['id']}", help="Tạo bản sao để chỉnh thành phiếu mới"):
                mo(p["id"], nhan_ban=True)
            if st.button("☆ Bỏ sao" if p["gan_sao"] else "⭐ Gắn sao", key=f"tv_sao_{p['id']}"):
                state.ghi("phieu_sao", p["id"], not p["gan_sao"])
                st.rerun()
            with st.popover("🗑️", help="Xoá phiếu"):
                st.markdown("Xoá vĩnh viễn phiếu này?")
                if st.button("Xoá", key=f"tv_xoa_{p['id']}", type="primary"):
                    state.ghi("phieu_xoa", p["id"])
                    if p["id"] == dang_mo:
                        st.session_state.ban.id = ""  # phiếu đang mở thành phiếu chưa lưu
                        st.session_state.setdefault("da_luu", {})["phieu"] = st.session_state.ban.model_dump_json()
                    st.rerun()
