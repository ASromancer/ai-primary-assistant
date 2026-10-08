import altair as alt
import pandas as pd
import streamlit as st

import danh_gia as dg
import state
from ai import nhan_xet_hoc_ba

st.markdown("## 📈 Tiến bộ học sinh")
st.caption("Theo dõi mức đạt TT27 của từng em qua các lần chấm và gợi ý nhận xét cuối kỳ để ghi học bạ. "
           "AI chỉ nhận lịch sử mức và nhận xét, không nhận tên học sinh.")

if not state.ca_nhan():
    st.info("🔐 Đăng nhập để lưu kết quả chấm và theo dõi tiến bộ của lớp."
            if not state.email() else "⚠️ Chưa cấu hình database (khối [connections.sql] trong Secrets).")
    if not state.email():
        state.nut_dang_nhap("tb_dang_nhap")
    st.stop()

ds_lop = state.doc("lop_ds")
if not ds_lop:
    st.info("Chưa có lớp nào. Tạo lớp ở trang Lớp của tôi, chấm bài rồi bấm *Lưu vào hồ sơ lớp*.")
    st.page_link(state.TRANG["lop_cua_toi"], label="Đi tới Lớp của tôi", icon="👥")
    st.stop()

ten_lop = {x["id"]: x["ten_lop"] or "(chưa đặt tên)" for x in ds_lop}
lop_hien = getattr(st.session_state.get("lop"), "id", "")
lop_id = st.selectbox("Lớp", list(ten_lop), format_func=ten_lop.get,
                      index=list(ten_lop).index(lop_hien) if lop_hien in ten_lop else 0)
du_lieu = state.doc("tien_bo", lop_id)
if not du_lieu:
    st.info("Lớp này chưa có kết quả chấm nào được lưu. Ở trang Chấm bài, bấm *💾 Lưu vào hồ sơ lớp* sau khi chấm.")
    st.stop()

NHAN = {"Hoàn thành tốt": "🌟 HTT", "Hoàn thành": "✅ HT", "Chưa hoàn thành": "🌱 CHT"}
BAC = {"Chưa hoàn thành": 1, "Hoàn thành": 2, "Hoàn thành tốt": 3}

# Các lần chấm theo thời gian
lan, nhan_lan = [], {}
for r in du_lieu:
    if r["lan_cham_id"] not in nhan_lan:
        lan.append(r["lan_cham_id"])
        nhan_lan[r["lan_cham_id"]] = f"{len(lan)}. {r['ngay'][8:10]}/{r['ngay'][5:7]} · {r['chu_de'][:20]}"

lop = state.doc("lop_mo", lop_id)
ten_hs = [h.ten for h in lop.hoc_sinh] + sorted({r["ten"] for r in du_lieu} - {h.ten for h in lop.hoc_sinh})
theo_hs = {t: [r for r in du_lieu if r["ten"] == t] for t in ten_hs}
goi_y = {t: dg.muc_cuoi_ky([r["muc_tt27"] for r in rs]) for t, rs in theo_hs.items()}

c1, c2, c3 = st.columns(3)
c1.metric("Số lần chấm đã lưu", len(lan), border=True)
c2.metric("Học sinh có kết quả", sum(1 for rs in theo_hs.values() if rs), border=True)
c3.metric("🌟 Gợi ý Hoàn thành tốt cuối kỳ", sum(1 for m in goi_y.values() if m == "Hoàn thành tốt"), border=True)

st.markdown("#### 🗂️ Bảng theo dõi")
bang = []
for t in ten_hs:
    o = {"Học sinh": t}
    for r in theo_hs[t]:
        o[nhan_lan[r["lan_cham_id"]]] = NHAN.get(r["muc_tt27"], r["muc_tt27"])
    o["Gợi ý cuối kỳ"] = NHAN.get(goi_y[t], "–")
    bang.append(o)
st.dataframe(pd.DataFrame(bang, columns=["Học sinh", *nhan_lan.values(), "Gợi ý cuối kỳ"]).fillna("–"),
             hide_index=True, width="stretch")
st.caption("🌟 HTT: Hoàn thành tốt · ✅ HT: Hoàn thành · 🌱 CHT: Chưa hoàn thành. "
           "Gợi ý cuối kỳ = mức xuất hiện nhiều nhất (hoà thì lấy lần gần nhất); giáo viên quyết định cuối cùng.")

# ---------------- Từng học sinh ----------------
st.markdown("#### 👤 Từng học sinh")
co_kq = [t for t in ten_hs if theo_hs[t]]
em = st.selectbox("Chọn học sinh", co_kq, key=f"tb_em_{lop_id}")
rs = theo_hs[em]
df = pd.DataFrame([{"Lần": nhan_lan[r["lan_cham_id"]], "Thứ tự": lan.index(r["lan_cham_id"]) + 1,
                    "Bậc": BAC.get(r["muc_tt27"], 0), "Mức": r["muc_tt27"], "Chủ đề": r["chu_de"],
                    "Điểm": r["diem"], "Ngày": r["ngay"]} for r in rs])
truc_y = alt.Axis(values=[1, 2, 3], title=None, grid=True, gridColor="#EEF1F5",
                  labelExpr="datum.value == 3 ? 'Hoàn thành tốt' : datum.value == 2 ? 'Hoàn thành' : 'Chưa hoàn thành'")
goc = alt.Chart(df).encode(
    x=alt.X("Thứ tự:Q", title="Lần chấm", axis=alt.Axis(tickMinStep=1, format="d", grid=False)),
    y=alt.Y("Bậc:Q", scale=alt.Scale(domain=[0.7, 3.3]), axis=truc_y),
    tooltip=["Lần", "Chủ đề", "Mức", "Điểm", "Ngày"])
st.altair_chart((goc.mark_line(color="#1565C0", strokeWidth=2)
                 + goc.mark_point(color="#1565C0", filled=True, size=110))
                .properties(height=240, title=f"Mức đạt TT27 của {em} qua các lần chấm"), width="stretch")

hb = st.session_state.setdefault("hoc_ba", {}).setdefault(lop_id, {})


khoi = next((int(ch) for ch in ten_lop[lop_id] if ch in "12345"), 0)  # "2A" -> lớp 2


def goi_y_hoc_ba(ten: str):
    hb[ten] = {"muc": goi_y[ten], "nx": nhan_xet_hoc_ba(state.client(), state.MODEL, khoi, theo_hs[ten], goi_y[ten])}


with st.container(horizontal=True):
    if st.button(f"✨ Gợi ý nhận xét học bạ cho {em}", key="hb_mot", type="primary"):
        if not state.api_key():
            st.error("Cần Gemini API Key.")
        else:
            with st.spinner("AI đang viết nhận xét..."):
                try:
                    goi_y_hoc_ba(em)
                    st.session_state.hb_ver = st.session_state.get("hb_ver", 0) + 1
                except Exception as e:
                    state.bao_loi(e)
    if st.button(f"✨ Gợi ý cho cả lớp ({len(co_kq)} em)", key="hb_ca_lop"):
        if not state.api_key():
            st.error("Cần Gemini API Key.")
        else:
            tien = st.progress(0.0)
            for k, t in enumerate(co_kq):
                tien.progress(k / len(co_kq), text=f"Đang viết nhận xét {k + 1}/{len(co_kq)}")
                try:
                    goi_y_hoc_ba(t)
                except Exception as e:
                    st.warning(f"{t}: {state.loi_than_thien(e)}")
            tien.progress(1.0, text="Xong")
            st.session_state.hb_ver = st.session_state.get("hb_ver", 0) + 1

if hb:
    st.markdown("#### 📝 Nhận xét học bạ cuối kỳ")
    ver = st.session_state.get("hb_ver", 0)
    if st.session_state.get("hb_goc_ver") != (lop_id, ver):
        st.session_state.hb_goc = pd.DataFrame([{"Học sinh": t, "Mức cuối kỳ": v["muc"], "Nhận xét học bạ": v["nx"]}
                                                for t, v in hb.items()])
        st.session_state.hb_goc_ver = (lop_id, ver)
    sua = st.data_editor(st.session_state.hb_goc, hide_index=True, width="stretch", key=f"hb_bang_{lop_id}_{ver}",
                         disabled=["Học sinh"], column_config={
                             "Mức cuối kỳ": st.column_config.SelectboxColumn(options=dg.MUC_TT27, required=True),
                             "Nhận xét học bạ": st.column_config.TextColumn(width="large")})
    for r in sua.to_dict("records"):  # giữ chỉnh sửa của giáo viên
        hb[r["Học sinh"]] = {"muc": r["Mức cuối kỳ"], "nx": r["Nhận xét học bạ"]}
    st.download_button("📊 Tải nhận xét học bạ (.xlsx)",
                       dg.so_tong_hop_excel([{"STT": k + 1, "Họ tên": r["Học sinh"], "Mức cuối kỳ": r["Mức cuối kỳ"],
                                              "Nhận xét": r["Nhận xét học bạ"]} for k, r in enumerate(sua.to_dict("records"))]),
                       state.ten_file(f"Nhan_xet_hoc_ba_{ten_lop[lop_id]}") + ".xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       type="primary", on_click="ignore")
