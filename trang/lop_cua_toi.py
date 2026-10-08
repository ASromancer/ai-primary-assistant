import pandas as pd
import streamlit as st
from pydantic import ValidationError

import docx_export as dx
import html_export as hx
import state
from ai import HocSinh, LopHoc, tao_de_b

NHOM = list(dx.NHOM)  # Xanh, Cam, Tím
MAU_NHOM = {"Xanh": "green", "Cam": "orange", "Tím": "violet"}

st.markdown("## 👥 Lớp của tôi")
st.caption("Danh sách học sinh theo nhóm Xanh/Cam/Tím – dùng để in phiếu có sẵn tên, gọi tên ở chế độ Lớp học "
           "và cập nhật nhóm sau khi chấm bài. Tên học sinh chỉ nằm trên trình duyệt, không gửi cho AI.")

lop: LopHoc = st.session_state.setdefault("lop", LopHoc())
dat_lop = state.dat_lop

if state.ca_nhan():  # nhiều lớp, lưu trên database
    ds_lop = state.doc("lop_ds")
    ten = {x["id"]: f"{x['ten_lop'] or '(chưa đặt tên)'} · {x['si_so']} học sinh" for x in ds_lop}
    with st.container(horizontal=True, vertical_alignment="bottom"):
        if ds_lop:
            chon = st.selectbox("Lớp đang làm việc", list(ten), index=list(ten).index(lop.id) if lop.id in ten else None,
                                format_func=ten.get, placeholder="Chọn lớp", key=f"chon_lop_{st.session_state.get('lop_ver', 0)}")
            if chon and chon != lop.id:
                dat_lop(state.doc("lop_mo", chon))
                st.rerun()
        if st.button("➕ Lớp mới", key="lop_moi"):
            dat_lop(LopHoc())
            st.rerun()
        if lop.id:
            with st.popover("🗑️ Xoá lớp"):
                st.markdown(f"Xoá lớp **{state.md(lop.ten_lop or '(chưa đặt tên)')}** và danh sách học sinh? "
                            "Kết quả chấm đã lưu vẫn được giữ.")
                if st.button("Xoá lớp", type="primary", key="xoa_lop"):
                    state.ghi("lop_xoa", lop.id)
                    st.session_state.setdefault("da_luu", {})["lop"] = LopHoc().model_dump_json()
                    dat_lop(LopHoc())
                    st.rerun()

trai, phai = st.columns([2, 3], gap="large")

with trai:
    with st.container(border=True):
        st.markdown("#### 📋 Danh sách học sinh")
        ten_lop = st.text_input("Tên lớp", value=lop.ten_lop, placeholder="VD: 2A")
        if ten_lop != lop.ten_lop:
            lop.ten_lop = ten_lop

        # data_editor lưu thay đổi so với dữ liệu gốc: gốc phải giữ nguyên tới khi danh sách được thay mới
        ver = st.session_state.get("lop_ver", 0)
        if st.session_state.get("lop_goc_ver") != ver:
            st.session_state.lop_goc = pd.DataFrame([{"Họ và tên": h.ten, "Nhóm": h.nhom} for h in lop.hoc_sinh],
                                                    columns=["Họ và tên", "Nhóm"])
            st.session_state.lop_goc_ver = ver
        sua = st.data_editor(
            st.session_state.lop_goc, num_rows="dynamic", width="stretch", key=f"bang_lop_{ver}",
            column_config={
                "Họ và tên": st.column_config.TextColumn(required=True, width="medium"),
                "Nhóm": st.column_config.SelectboxColumn(options=NHOM, required=True, default="Cam", width="small"),
            })
        moi = [HocSinh(stt=k + 1, ten=str(r["Họ và tên"]).strip(), nhom=r["Nhóm"] if r["Nhóm"] in NHOM else "Cam")
               for k, r in enumerate(sua.to_dict("records")) if str(r["Họ và tên"] or "").strip() not in ("", "None", "nan")]
        lop.hoc_sinh = moi

        if lop.hoc_sinh:
            with st.container(horizontal=True):
                st.badge(f"{len(lop.hoc_sinh)} học sinh", color="blue")
                for n in NHOM:
                    st.badge(f"Phiếu {n}: {sum(h.nhom == n for h in lop.hoc_sinh)}", color=MAU_NHOM[n])

        with st.expander("📥 Dán nhanh danh sách tên"):
            dan = st.text_area("Mỗi dòng một tên (copy cột tên từ Excel)", height=120, key="dan_ten")
            if st.button("Thêm vào danh sách", key="them_ten"):
                ten_moi = [x.strip() for x in dan.splitlines() if x.strip()]
                ds = lop.hoc_sinh + [HocSinh(stt=0, ten=x) for x in ten_moi]
                dat_lop(LopHoc(ten_lop=lop.ten_lop, hoc_sinh=[h.model_copy(update={"stt": k + 1}) for k, h in enumerate(ds)]))
                st.rerun()

        c1, c2 = st.columns(2)
        c1.download_button("💾 Lưu (.json)", lop.model_dump_json(indent=2),
                           f"Lop_{state.ten_file(lop.ten_lop or 'cua_toi')}.json", "application/json",
                           width="stretch", on_click="ignore", disabled=not lop.hoc_sinh)
        with c2.popover("📂 Mở file", width="stretch"):
            f = st.file_uploader("File lop.json", type="json", key="mo_lop")
            if f and st.button("Mở", key="mo_lop_btn"):
                try:
                    dat_lop(LopHoc.model_validate_json(f.getvalue()))
                    st.rerun()
                except ValidationError:
                    st.error("File không đúng định dạng danh sách lớp.")

with phai:
    ban = state.ban_hien_tai()
    if ban is None:
        st.info("Soạn hoặc mở một phiếu để tạo đề B và in phiếu theo tên học sinh.")
        st.page_link(state.TRANG["soan_phieu"], label="Đi tới Soạn phiếu", icon="✍️")
        st.stop()

    with st.container(border=True):
        st.markdown("#### 🅰️🅱️ Đề A/B chống nhìn bài")
        st.caption(f"Phiếu hiện tại: **{state.md(ban.thong_so.chu_de)}**. Đề B giữ nguyên mức, dạng bài và điểm "
                   "từng câu nhưng đổi số liệu, ngữ liệu.")
        if ban.phieu_b:
            with st.expander("✅ Đã có đề B – xem nhanh"):
                for k, (a, b) in enumerate(zip(ban.phieu.cau_hoi, ban.phieu_b.cau_hoi), 1):
                    st.markdown(f"**Câu {k}** · A: {state.md(a.noi_dung)}  \nB: {state.md(b.noi_dung)}")
        if st.button("🔄 Tạo lại đề B" if ban.phieu_b else "✨ Tạo đề B bằng AI", key="tao_de_b",
                     type="secondary" if ban.phieu_b else "primary"):
            if not state.api_key():
                st.error("Cần Gemini API Key để tạo đề B.")
            else:
                with st.spinner("AI đang soạn đề B tương đương..."):
                    try:
                        ban.phieu_b = tao_de_b(state.client(), state.MODEL, ban.thong_so, ban.phieu)
                        st.toast("Đã tạo đề B", icon="✅")
                        st.rerun()
                    except Exception as e:
                        state.bao_loi(e)

    with st.container(border=True):
        st.markdown("#### 🧾 Phiếu theo tên từng học sinh")
        if not lop.hoc_sinh:
            st.info("Thêm học sinh vào danh sách bên trái để in phiếu có sẵn tên.")
            st.stop()
        c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
        xen_ke = c1.toggle("Xen kẽ đề A/B (STT chẵn làm đề B)", key="xen_ke", disabled=ban.phieu_b is None,
                           help="Cần tạo đề B trước")
        co = c2.segmented_control("Cỡ chữ", [14, 16, 18], default=14, key="co_ten", format_func=lambda x: f"{x}pt")
        ten = state.ten_file(f"Phieu_theo_ten_{lop.ten_lop}_{ban.thong_so.chu_de}")
        st.download_button(f"📄 Tải Word: {len(lop.hoc_sinh)} phiếu, mỗi em một trang",
                           dx.phieu_theo_ten(ban, lop.hoc_sinh, xen_ke, lop.ten_lop), f"{ten}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           type="primary", width="stretch", on_click="ignore")
        st.iframe(hx.trang_in(hx.phieu_theo_ten(ban, lop.hoc_sinh, xen_ke, lop.ten_lop), co or 14), height=820)
