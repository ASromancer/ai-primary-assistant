from pathlib import Path

import pandas as pd
import streamlit as st

import danh_gia as dg
import docx_export as dx
import state
from ai import HocSinh, LopHoc, cham_bai

st.markdown("## 📷 Chấm bài bằng ảnh")
st.caption("Chụp bài làm của cả lớp – AI chấm từng câu, viết nhận xét theo Thông tư 27, xếp mức "
           "Hoàn thành tốt / Hoàn thành / Chưa hoàn thành và gợi ý phiếu Xanh/Cam/Tím cho lần sau.")

ban = state.can_phieu()
lop: LopHoc = st.session_state.get("lop") or LopHoc()
ds_ten = [h.ten for h in lop.hoc_sinh]

# ---------------- Chọn phiếu & tải ảnh ----------------
with st.container(border=True):
    st.markdown("#### ① Phiếu đã phát và ảnh bài làm")
    c1, c2 = st.columns([3, 1])
    loai = c1.segmented_control("Học sinh đã làm phiếu nào?", ["Phiếu chung", *[f"Phiếu {n}" for n in dx.NHOM]],
                                default="Phiếu chung", key="cb_phieu") or "Phiếu chung"
    de_b = c2.toggle("Đề B", key="cb_de_b", disabled=ban.phieu_b is None,
                     help="Bật nếu học sinh làm đề B (tạo ở trang Lớp của tôi)")
    ban_cham = dx.ban_de_b(ban) if de_b and ban.phieu_b else ban
    if loai == "Phiếu chung":
        ids = [i for m in (1, 2, 3) for i in dx.cau_theo_muc(ban_cham, m)]
    else:
        chinh, them = dx.cau_cua_nhom(ban_cham, loai.removeprefix("Phiếu "))
        ids = chinh + them
    st.caption(f"{len(ids)} câu sẽ được chấm theo đáp án của **{loai}{' – đề B' if de_b else ''}**.")

    anh = st.file_uploader("Ảnh bài làm – mỗi ảnh một học sinh (chụp thẳng, đủ sáng, tối đa 40 ảnh)",
                           type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, max_upload_size=5)
    st.caption("🔒 Ảnh được gửi tới Google Gemini để chấm và không được ứng dụng lưu lại. "
               "Nên dùng API key của trường và thông báo với phụ huynh theo quy định của nhà trường.")
    bam = st.button(f"🤖 Chấm {len(anh)} bài" if anh else "🤖 Chấm bài", type="primary", width="stretch",
                    disabled=not anh or len(anh) > 40, key="cb_cham")

if bam:
    if not state.api_key():
        st.error("Cần Gemini API Key để chấm bài.")
    else:
        rows, loi = [], []
        tien = st.progress(0.0, text="Đang chấm...")
        for k, f in enumerate(anh):
            tien.progress(k / len(anh), text=f"Đang chấm bài {k + 1}/{len(anh)}: {f.name}")
            try:
                kq = cham_bai(state.client(), state.MODEL, ban_cham.thong_so, ban_cham.phieu, ids,
                              (f.getvalue(), f.type))
            except Exception as e:
                loi.append(f"{f.name}: {state.loi_than_thien(e)}")
                continue
            muc = dg.muc_tt27(ban_cham.phieu, ids, kq)
            row = {
                "STT": len(rows) + 1,
                "Họ tên": dg.khop_ten(kq.ten_tren_phieu, ds_ten) or Path(f.name).stem,
                "Điểm": round(sum(c.diem_dat for c in kq.cau), 2),
                "Mức TT27": muc,
                "Nhận xét": kq.nhan_xet,
            }
            row.update({f"Câu {c.cau_so}": dg.KY_HIEU[c.dat] + (f" {c.ghi_chu}" if c.ghi_chu else "") for c in kq.cau})
            row["Ảnh"] = f.name
            rows.append(row)
        tien.progress(1.0, text=f"Đã chấm xong {len(rows)}/{len(anh)} bài")
        st.session_state.cham = {"rows": rows, "loi": loi, "ver": st.session_state.get("cham", {}).get("ver", 0) + 1}
        st.toast(f"Đã chấm {len(rows)} bài", icon="✅")

# ---------------- Kết quả ----------------
cham = st.session_state.get("cham")
if not cham:
    st.info("Kết quả chấm sẽ hiện ở đây: bảng tổng hợp có thể sửa, thống kê mức TT27 và nút xuất Excel.")
    st.stop()

for x in cham["loi"]:
    st.warning(f"Chưa chấm được {x}")
if not cham["rows"]:
    st.stop()

with st.container(border=True):
    st.markdown("#### ② Sổ tổng hợp")
    o_thong_ke = st.container()  # thống kê hiển thị trước bảng, tính từ bảng đã sửa
    if st.session_state.get("cham_goc_ver") != cham["ver"]:
        st.session_state.cham_goc = pd.DataFrame(cham["rows"])
        st.session_state.cham_goc_ver = cham["ver"]
    df = st.data_editor(
        st.session_state.cham_goc, hide_index=True, width="stretch", key=f"bang_cham_{cham['ver']}",
        disabled=[c for c in st.session_state.cham_goc.columns if c not in ("Họ tên", "Mức TT27", "Nhận xét")],
        column_config={
            "Mức TT27": st.column_config.SelectboxColumn(options=dg.MUC_TT27, required=True, width="medium"),
            "Nhận xét": st.column_config.TextColumn(width="large"),
            "Họ tên": st.column_config.TextColumn(width="medium"),
            "Điểm": st.column_config.NumberColumn(format="%.2f"),
        })
    st.caption("Có thể sửa họ tên, mức TT27 và nhận xét trực tiếp trong bảng. "
               "✓ đúng · ½ đúng một phần · ✗ sai · – bỏ trống.")

    tong = len(df)
    cols = o_thong_ke.columns(3)
    for col, (muc, icon) in zip(cols, [("Hoàn thành tốt", "🌟"), ("Hoàn thành", "✅"), ("Chưa hoàn thành", "🌱")]):
        n = int((df["Mức TT27"] == muc).sum())
        col.metric(f"{icon} {muc}", f"{n} em", f"{n / tong:.0%} · gợi ý Phiếu {dg.NHOM_DE_XUAT[muc]}",
                   delta_color="off", delta_arrow="off", border=True)

    df_xuat = df.assign(**{"Phiếu tiếp theo": df["Mức TT27"].map(dg.NHOM_DE_XUAT)})
    c1, c2 = st.columns(2)
    c1.download_button("📊 Tải sổ tổng hợp (.xlsx)", dg.so_tong_hop_excel(df_xuat.to_dict("records")),
                       state.ten_file(f"So_tong_hop_{lop.ten_lop}_{ban.thong_so.chu_de}") + ".xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       type="primary", width="stretch", on_click="ignore")
    if c2.button("👥 Cập nhật nhóm Xanh/Cam/Tím vào Lớp của tôi", width="stretch", key="cb_ap_nhom"):
        theo_ten = {r["Họ tên"]: dg.NHOM_DE_XUAT[r["Mức TT27"]] for r in df.to_dict("records") if r["Họ tên"]}
        hs = [h.model_copy(update={"nhom": theo_ten.get(h.ten, h.nhom)}) for h in lop.hoc_sinh]
        moi = [t for t in theo_ten if t not in ds_ten]
        hs += [HocSinh(stt=len(hs) + k + 1, ten=t, nhom=theo_ten[t]) for k, t in enumerate(moi)]
        state.dat_lop(LopHoc(ten_lop=lop.ten_lop, hoc_sinh=hs))
        st.toast(f"Đã cập nhật nhóm cho {len(theo_ten)} học sinh" + (f" (thêm mới {len(moi)} em)" if moi else ""),
                 icon="👥")

    if state.ca_nhan():
        lop_hien = st.session_state.get("lop") or LopHoc()
        da_luu = st.session_state.get("cham_da_luu") == cham["ver"]
        if not lop_hien.id:
            st.caption("💡 Chọn hoặc tạo lớp ở trang *Lớp của tôi* để lưu kết quả vào hồ sơ tiến bộ của lớp.")
        elif st.button("✅ Đã lưu vào hồ sơ lớp" if da_luu else
                       f"💾 Lưu vào hồ sơ lớp {lop_hien.ten_lop or ''} (theo dõi tiến bộ)",
                       disabled=da_luu, width="stretch", key="cb_luu"):
            cot_cau = [c for c in df.columns if c.startswith("Câu ")]
            state.ghi("cham_luu", lop_hien.id, ban_cham.thong_so.mon, ban_cham.thong_so.chu_de,
                         loai + (" – đề B" if de_b else ""),
                         [{"ten": r["Họ tên"], "diem": float(r["Điểm"]) if pd.notna(r["Điểm"]) else None, "muc_tt27": r["Mức TT27"], "nhan_xet": r["Nhận xét"],
                           "chi_tiet": {c: r[c] for c in cot_cau}} for r in df.to_dict("records") if r["Họ tên"]])
            st.session_state.cham_da_luu = cham["ver"]
            st.rerun()
