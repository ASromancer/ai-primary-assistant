import streamlit as st

import docx_export as dx
import html_export as hx
import state
from ai import DANG_BAI, LOAI_VAN_DE, MUC, SO_CAU, BanLuu, ThongSo, dau_van_tay, kiem_dinh, tao_lai_cau, tao_phieu
from state import MODEL, PHIEU_MAU, bao_loi, dat_phieu, md, mo_phieu, ten_file

MON_THEO_LOP = {
    1: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức"],
    2: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức"],
    3: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức", "Tin học", "Công nghệ"],
    4: ["Toán", "Tiếng Việt", "Khoa học", "Lịch sử và Địa lí", "Đạo đức", "Tin học", "Công nghệ"],
    5: ["Toán", "Tiếng Việt", "Khoa học", "Lịch sử và Địa lí", "Đạo đức", "Tin học", "Công nghệ"],
}
BO_SACH = ["Kết nối tri thức với cuộc sống", "Chân trời sáng tạo", "Cánh Diều"]
THOI_LUONG = {15: "15 phút", 20: "20 phút", 35: "35 phút"}
SAO = dx.SAO
# Màu mức độ trùng màu phiếu nhóm: Mức 1 ~ Phiếu Xanh, Mức 2 ~ Cam, Mức 3 ~ Tím
MAU_MUC = {1: "green", 2: "orange", 3: "violet"}
api_key = state.api_key()


def chay_kiem_dinh(ban: BanLuu):
    """Kiểm định không được chặn việc dùng phiếu: lỗi chỉ cảnh báo."""
    try:
        ban.kiem_dinh = kiem_dinh(state.client(), MODEL, ban.thong_so, ban.phieu)
        ban.kiem_dinh_cho = dau_van_tay(ban.phieu)
    except Exception as e:
        st.warning(f"Chưa kiểm định được phiếu: {state.loi_than_thien(e)}")


@st.cache_data(max_entries=20)
def xuat_file(ban_json: str):
    files = dx.tat_ca(BanLuu.model_validate_json(ban_json))
    return files, dx.dong_goi_zip(files)


st.markdown("## ✍️ Soạn phiếu bài tập phân hóa")
st.caption("Phân hóa 3 mức theo Thông tư 27/2020/TT-BGDĐT · Bám Chương trình GDPT 2018")
trai, phai = st.columns([1, 2], gap="large")

# ---------------- ① Nhập thông tin ----------------
with trai:
    with st.container(border=True):
        st.markdown("#### ① Thông tin bài học")
        c1, c2 = st.columns(2)
        lop = c1.selectbox("Khối lớp", list(MON_THEO_LOP), format_func=lambda x: f"Lớp {x}")
        mon = c2.selectbox("Môn học", MON_THEO_LOP[lop])
        bo_sach = st.selectbox("Bộ sách", BO_SACH)
        thoi_luong = st.segmented_control(
            "Thời lượng làm bài", list(THOI_LUONG), default=20, format_func=THOI_LUONG.get, width="stretch",
            help="15 phút: khởi động/củng cố · 20 phút: luyện tập · 35 phút: phiếu cuối tuần")
        chu_de = st.text_input("Tên bài học / Chủ đề", placeholder="VD: Phép cộng có nhớ trong phạm vi 100")
        anh = st.file_uploader("📷 Ảnh trang SGK (tuỳ chọn, tối đa 3) – AI ra đề bám sát trang sách",
                               type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, max_upload_size=5)
        with st.expander("Tuỳ chọn nâng cao"):
            dang_bai = st.pills("Dạng bài", list(DANG_BAI), selection_mode="multi", default=list(DANG_BAI),
                                format_func=DANG_BAI.get)
            ghi_chu = st.text_area("Yêu cầu thêm", height=80,
                                   placeholder="VD: Lồng ghép an toàn giao thông; dùng địa danh ở Hà Nội...")
        bam_tao = st.button("🚀 Tạo phiếu bài tập", type="primary", width="stretch")

    if bam_tao:
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key ở thanh bên trái (hoặc cấu hình trong Secrets).")
        elif not chu_de.strip() and not anh:
            st.warning("Vui lòng nhập tên bài học hoặc tải lên ảnh trang sách.")
        elif len(anh) > 3:
            st.warning("Chỉ tải tối đa 3 ảnh.")
        elif not dang_bai:
            st.warning("Vui lòng chọn ít nhất một dạng bài.")
        else:
            thoi_luong = thoi_luong or 20
            with st.status("AI đang soạn phiếu... (khoảng 20–40 giây)", expanded=True) as status:
                if anh:
                    st.write(f"📷 Đọc {len(anh)} ảnh trang sách giáo khoa")
                st.write(f"✍️ Soạn {sum(SO_CAU[thoi_luong])} câu theo 3 mức TT27, kèm đáp án")
                try:
                    ts = ThongSo(mon=mon, lop=lop, bo_sach=bo_sach, chu_de=chu_de.strip(), thoi_luong=thoi_luong)
                    phieu = tao_phieu(state.client(), MODEL, ts, dang_bai,
                                      [(a.getvalue(), a.type) for a in anh], ghi_chu)
                    ts.chu_de = ts.chu_de or phieu.ten_bai
                    ban_moi = BanLuu(thong_so=ts, phieu=phieu)
                    dat_phieu(ban_moi)
                    st.write("🔎 Tổ trưởng chuyên môn AI đang kiểm định phiếu")
                    chay_kiem_dinh(ban_moi)
                    status.update(label="Đã tạo xong phiếu!", state="complete", expanded=False)
                    st.toast("Phiếu đã sẵn sàng – xem, chỉnh và in ở bên phải", icon="🎉")
                except Exception as e:
                    status.update(label="Chưa tạo được phiếu", state="error")
                    bao_loi(e)

# ---------------- ② ③ Kết quả ----------------
with phai:
    if "ban" not in st.session_state:
        st.html("""<div class="buoc">
<div><b>① Nhập bài học</b><p>Chọn lớp, môn, bộ sách và nhập tên bài, hoặc chụp ảnh trang sách giáo khoa.</p></div>
<div><b>② Xem & chỉnh</b><p>AI soạn 3 mức độ theo TT27. Câu chưa ưng: đổi câu, làm dễ hơn/khó hơn hoặc sửa tay.</p></div>
<div><b>③ In & phát phiếu</b><p>In ngay phiếu chung hoặc 3 phiếu nhóm Xanh/Cam/Tím, kèm đáp án và ma trận.</p></div>
</div>""")
        if st.button("👀 Xem thử phiếu mẫu", type="primary", key="mau_main"):
            mo_phieu(PHIEU_MAU.read_text(encoding="utf-8"))
            st.rerun()
        st.stop()

    ban: BanLuu = state.ban_hien_tai()
    ts, phieu = ban.thong_so, ban.phieu
    thu_tu = [i for m in (1, 2, 3) for i in dx.cau_theo_muc(ban, m)]
    so_cau = {i: k + 1 for k, i in enumerate(thu_tu)}

    st.markdown(f"### 📝 {md(ts.chu_de)}")
    st.caption(f"Môn {ts.mon} · Lớp {ts.lop} · {ts.bo_sach} · {ts.thoi_luong} phút")
    cols = st.columns(4)
    for m in (1, 2, 3):
        cols[m - 1].metric(f"{SAO[m]} Mức {m}", f"{len(dx.cau_theo_muc(ban, m))} câu")
    tong = sum(c.diem for c in phieu.cau_hoi)
    cols[3].metric("Tổng điểm", dx.so(tong))
    if abs(tong - 10) > 0.01:
        st.warning(f"Tổng điểm hiện là {dx.so(tong)}, chưa bằng 10. Dùng nút ✏️ Sửa để chỉnh điểm từng câu.")

    kd = ban.kiem_dinh
    with st.container(border=True):
        if kd is None:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("🔎 **Kiểm định AI:** phiếu chưa được kiểm định.")
                if st.button("Kiểm định ngay", key="kd_chay", type="primary"):
                    if not api_key:
                        st.error("Cần Gemini API Key để kiểm định.")
                    else:
                        with st.spinner("Tổ trưởng chuyên môn AI đang kiểm định..."):
                            chay_kiem_dinh(ban)
                        st.rerun()
        else:
            mau = "green" if kd.diem >= 85 else "orange" if kd.diem >= 70 else "red"
            xep_loai = "Tốt" if kd.diem >= 85 else "Khá – nên xem lại" if kd.diem >= 70 else "Cần sửa"
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"🔎 **Kiểm định AI: {kd.diem}/100**")
                st.badge(xep_loai, color=mau)
                st.badge(f"{len(kd.van_de)} góp ý" if kd.van_de else "Không phát hiện lỗi",
                         color="orange" if kd.van_de else "green")
                if st.button("Kiểm định lại", key="kd_lai", type="tertiary", icon="🔄"):
                    if not api_key:
                        st.error("Cần Gemini API Key để kiểm định.")
                    else:
                        with st.spinner("Tổ trưởng chuyên môn AI đang kiểm định..."):
                            chay_kiem_dinh(ban)
                        st.rerun()
            st.caption(md(kd.nhan_xet_chung))
            for v in kd.van_de:
                if v.cau_so == 0:
                    st.warning(f"**{LOAI_VAN_DE[v.loai]}:** {md(v.mo_ta)} → {md(v.de_xuat)}")
            if ban.kiem_dinh_cho != dau_van_tay(phieu):
                st.caption("✏️ Phiếu đã thay đổi sau lần kiểm định gần nhất – bấm *Kiểm định lại* để cập nhật.")

    def lam_lai(i: int, che_do: str, gop_y: str = "", van_de=None):
        if not api_key:
            st.error("Cần Gemini API Key để AI soạn lại câu.")
            return
        with st.spinner("AI đang soạn lại câu..."):
            try:
                moi = tao_lai_cau(state.client(), MODEL, ts, phieu, i, che_do, gop_y=gop_y)
            except Exception as e:
                bao_loi(e)
                return
        st.session_state.hoan_tac = (id(ban), i, phieu.cau_hoi[i])
        phieu.cau_hoi[i] = moi
        if van_de is not None and kd is not None:
            kd.van_de.remove(van_de)
        st.rerun()

    def hien_cau(i: int):
        c = phieu.cau_hoi[i]
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**Câu {so_cau[i]}**")
                st.badge(f"Mức {c.muc}", color=MAU_MUC[c.muc])
                st.badge(DANG_BAI[c.dang], color="gray")
                st.badge(f"{dx.so(c.diem)} điểm", color="blue")
            st.markdown(md(c.noi_dung))
            ds = [dx.bo_tien_to(x) for x in c.lua_chon]
            if c.dang == "trac_nghiem":
                st.markdown("  \n".join(f"{'ABCDEFGH'[k]}\\. {md(x)}" for k, x in enumerate(ds[:8])))
            elif c.dang == "dung_sai":
                st.markdown("  \n".join(f"☐ {md(x)}" for x in ds))
            elif c.dang == "noi_cot":
                a, b = st.columns(2)
                a.markdown("  \n".join(f"{k + 1}\\. {md(x)}" for k, x in enumerate(ds)))
                b.markdown("  \n".join(f"{chr(97 + k)}\\. {md(dx.bo_tien_to(x))}" for k, x in enumerate(c.cot_phai[:8])))
            if c.goi_y_hs:
                st.caption(f"💡 Gợi ý: {md(c.goi_y_hs)}")
            for k, v in enumerate(kd.van_de if kd else []):
                if v.cau_so == i + 1:
                    with st.container(horizontal=True, vertical_alignment="center"):
                        st.warning(f"**{LOAI_VAN_DE[v.loai]}:** {md(v.mo_ta)} → {md(v.de_xuat)}", width="stretch")
                        if st.button("🛠 Sửa theo góp ý", key=f"gy{i}_{k}"):
                            lam_lai(i, "gop_y", gop_y=f"{v.mo_ta}. Đề xuất: {v.de_xuat}", van_de=v)
            with st.expander("Đáp án & hướng dẫn chấm"):
                st.markdown(f"**Đáp án:** {md(c.dap_an)}  \n**Hướng dẫn chấm:** {md(c.huong_dan_cham)}")

            with st.container(horizontal=True):
                if st.button("🔄 Đổi câu", key=f"doi{i}", help="AI soạn câu khác cùng mức"):
                    lam_lai(i, "doi")
                if st.button("➖ Dễ hơn", key=f"de{i}", help="AI soạn lại dễ hơn, vẫn giữ mức"):
                    lam_lai(i, "de_hon")
                if st.button("➕ Khó hơn", key=f"kho{i}", help="AI soạn lại khó hơn, vẫn giữ mức"):
                    lam_lai(i, "kho_hon")
                with st.popover("✏️ Sửa"):
                    with st.form(f"sua{i}"):
                        nd = st.text_area("Đề bài", c.noi_dung)
                        lc = st.text_area("Lựa chọn / nhận định / cột trái (mỗi dòng một ý)", "\n".join(c.lua_chon))
                        cp = st.text_area("Cột phải", "\n".join(c.cot_phai)) if c.dang == "noi_cot" else ""
                        gy = st.text_input("Gợi ý cho học sinh", c.goi_y_hs)
                        da = st.text_area("Đáp án", c.dap_an)
                        diem = st.number_input("Điểm", min_value=0.0, max_value=10.0, value=float(c.diem), step=0.25)
                        if st.form_submit_button("💾 Lưu", type="primary"):
                            tach = lambda s: [x.strip() for x in s.splitlines() if x.strip()]
                            st.session_state.hoan_tac = (id(ban), i, c)
                            phieu.cau_hoi[i] = c.model_copy(update=dict(
                                noi_dung=nd, lua_chon=tach(lc), cot_phai=tach(cp), goi_y_hs=gy, dap_an=da, diem=diem))
                            st.rerun()
                ht = st.session_state.get("hoan_tac")
                if ht and ht[:2] == (id(ban), i) and st.button("↩️ Hoàn tác", key=f"ht{i}", type="tertiary"):
                    phieu.cau_hoi[i] = ht[2]
                    del st.session_state.hoan_tac
                    st.rerun()

    tab_sua, tab_in, tab_tai, tab_da = st.tabs(["② Xem & chỉnh", "🖨️ In phiếu", "📥 Tải Word", "📊 Ma trận & đáp án"])

    with tab_sua:
        for m in (1, 2, 3):
            st.markdown(f"##### {SAO[m]} Mức {m}")
            st.caption(MUC[m])
            for i in dx.cau_theo_muc(ban, m):
                hien_cau(i)
        st.success(f"🌟 {phieu.loi_chuc}")

    with tab_in:
        trang = hx.cac_trang(ban)
        c1, c2 = st.columns([3, 2])
        chon = c1.segmented_control("Chọn phiếu cần in", [*trang, "Tất cả"], default="Phiếu chung", key="chon_in",
                                    format_func=lambda k: k.replace("Phiếu ", "").replace(" & ma trận", "").capitalize())
        co = c2.segmented_control("Cỡ chữ", [14, 16, 18], default=14, key="co_chu",
                                  format_func=lambda x: f"{x}pt", help="Lớp 1–2 nên dùng 16–18pt")
        st.caption("Bấm **🖨️ In / Lưu PDF** trong khung xem trước. Muốn file PDF: chọn máy in \"Lưu thành PDF\". "
                   "Phiếu Xanh / Cam / Tím phát cho từng nhóm học sinh – chọn số bản in trong hộp thoại in.")
        ds_trang = list(trang.values()) if chon == "Tất cả" else [trang[chon or "Phiếu chung"]]
        st.iframe(hx.trang_in(ds_trang, co or 14), height=950)

    with tab_tai:
        ban_json = ban.model_dump_json(indent=2)
        files, zip_bytes = xuat_file(ban_json)
        ten = ten_file(f"{ts.mon}_Lop{ts.lop}_{ts.chu_de}")
        st.download_button("📦 Tải trọn bộ (.zip): phiếu chung + 3 phiếu nhóm + đáp án & ma trận", zip_bytes,
                           f"{ten}.zip", "application/zip", type="primary", width="stretch", on_click="ignore")
        st.caption("File Word khổ A4, Times New Roman 14 – mở bằng Word/WPS để chỉnh thêm trước khi in.")
        with st.container(horizontal=True):
            for fname, data in files.items():
                st.download_button(f"📄 {fname[2:-5].replace('_', ' ')}", data, f"{ten}_{fname}",
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   on_click="ignore")
        st.divider()
        st.download_button("💾 Lưu phiếu (.json) để mở lại / trình chiếu khi không có mạng", ban_json,
                           f"{ten}.json", "application/json", width="stretch", on_click="ignore")

    with tab_da:
        st.markdown("**Yêu cầu cần đạt**")
        st.markdown("\n".join(f"- {md(y)}" for y in phieu.yeu_cau_can_dat))
        st.markdown("**Ma trận theo mức độ (TT27)**")
        head = ["Mức"] + list(DANG_BAI.values()) + ["Số câu", "Điểm"]
        st.table([dict(zip(head, row)) for row in dx.ma_tran(ban)], hide_index=True)
        st.markdown("**Phân phiếu theo nhóm học sinh**")
        for ten_nhom, ((chinh, them), _, nhom_hs) in dx.NHOM.items():
            st.markdown(f"- **Phiếu {ten_nhom}** – {nhom_hs}: câu Mức {chinh}"
                        + (f" + 1 câu thử thách Mức {them}" if them else ""))
        st.markdown("**Đáp án**")
        vt = dx.vi_tri_trong_phieu(ban)
        st.table([{"Vị trí": vt[i], "Mức": c.muc, "Đáp án": c.dap_an, "Hướng dẫn chấm": c.huong_dan_cham}
                  for i in thu_tu for c in [phieu.cau_hoi[i]]], hide_index=True)
