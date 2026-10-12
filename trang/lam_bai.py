"""Trang làm bài của học sinh (mở bằng link ?ma=XXXXXX, không cần đăng nhập).

Không bao giờ hiển thị đáp án / hướng dẫn chấm: chỉ đề bài, lựa chọn và kết quả ✓/✗ sau khi nộp.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

import danh_gia as dg
import docx_export as dx
import kho
import state
from ai import KetQuaCham

st.html("""<style>
.block-container { padding-top: 3.5rem; max-width: 760px; }
div[data-testid="stRadio"] label p, div[data-testid="stMarkdownContainer"] p { font-size: 1.15rem; }
.stButton button { min-height: 3rem; font-size: 1.05rem; }
.de-bai { font-size: 1.4rem; font-weight: 600; line-height: 1.5; margin: .4rem 0 .8rem; }
</style>""")

KET_QUA = {"dung": "✅ Đúng", "mot_phan": "🟡 Đúng một phần", "sai": "❌ Chưa đúng", "bo_trong": "⬜ Bỏ trống"}


@st.cache_data(ttl=30, show_spinner=False)
def lay_bai(ma: str):
    return kho.hs_lay_bai(state.db(), ma)


def het_han(han: str | None) -> bool:
    return bool(han) and datetime.fromisoformat(han) < datetime.now(timezone.utc)


def gio_vn(han: str) -> str:
    return datetime.fromisoformat(han).astimezone(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M ngày %d/%m")


ma = st.query_params.get("ma", "").strip().upper()
if not state.co_db():
    st.error("Ứng dụng chưa được cấu hình để làm bài trực tuyến.")
    st.stop()
bai = lay_bai(ma)
if bai is None:
    st.error(f"Không tìm thấy bài có mã **{state.md(ma)}**. Em kiểm tra lại mã với thầy cô nhé.")
    st.stop()

ban = bai["ban"]
ts = ban.thong_so
st.markdown(f"### 📝 {state.md(ts.chu_de)}")
st.caption(f"Môn {ts.mon} · Lớp {ts.lop} · {ts.thoi_luong} phút" +
           (f" · Hạn nộp {gio_vn(bai['han_nop'])}" if bai["han_nop"] else ""))

hs = st.session_state.setdefault("hs", {})
if hs.get("ma") != ma:
    hs.clear()
    hs["ma"] = ma


def lam_lai_tu_dau():
    hs.clear()
    hs["ma"] = ma


# ---------------- Đã nộp: kết quả ----------------
if "ket_qua" in hs:
    tu_cham = [kq for kq in hs["ket_qua"] if kq["dat"] in KET_QUA]
    gioi = bool(tu_cham) and all(kq["dat"] == "dung" for kq in tu_cham)
    st.success(f"🎉 **{state.md(hs['ten'])}** đã nộp bài." + (" Em làm đúng hết phần trắc nghiệm, giỏi lắm!" if gioi
                                                              else " Cảm ơn em!"))
    cau = [ban.phieu.cau_hoi[i] for i in hs["ids"]]
    co_ai = False
    for k, (c, kq) in enumerate(zip(cau, hs["ket_qua"]), 1):
        nhan = KET_QUA.get(kq["dat"])
        co_ai |= nhan is None
        st.markdown(f"**Câu {k}:** {nhan or '⏳ Thầy cô sẽ chấm'}")
    if gioi and not hs.get("da_chuc"):
        st.balloons()
        hs["da_chuc"] = True
    if co_ai:
        st.info("Phần điền vào chỗ trống và tự luận thầy cô sẽ chấm và nhận xét sau.")
    st.markdown(f"🌟 *{state.md(ban.phieu.loi_chuc)}*")
    st.button("👉 Bạn tiếp theo làm bài trên máy này", on_click=lam_lai_tu_dau, width="stretch")
    st.stop()

if not bai["dang_mo"] or het_han(bai["han_nop"]):
    st.warning("⏰ Bài này đã đóng, không nhận thêm bài nộp. Em hỏi lại thầy cô nhé.")
    st.stop()

# ---------------- Chọn tên ----------------
if "ten" not in hs:
    da_nop = kho.hs_da_nop(state.db(), bai["id"])
    st.markdown("### 👋 Em là ai?")
    if bai["hoc_sinh"]:
        con_lai = [h["ten"] for h in bai["hoc_sinh"] if h["ten"] not in da_nop]
        ten = st.pills("Chạm vào tên của em", con_lai, key="hs_chon_ten")
        if da_nop:
            st.caption("✅ Đã nộp: " + ", ".join(da_nop))
    else:
        ten = st.text_input("Họ và tên của em", key="hs_go_ten").strip()
        if ten in da_nop:
            st.warning("Tên này đã nộp bài. Nếu là em, hãy báo thầy cô.")
            ten = ""
    if ten and st.button(f"Bắt đầu làm bài – em là **{ten}**", type="primary", width="stretch"):
        nhom = next((h["nhom"] for h in bai["hoc_sinh"] if h["ten"] == ten), None)
        if bai["che_do"] == "nhom" and nhom:  # phân hoá: phiếu theo nhóm của em
            chinh, them = dx.cau_cua_nhom(ban, nhom)
            hs.update(phieu=nhom, ids=chinh + them)
        else:
            hs.update(phieu="Chung", ids=[i for m in (1, 2, 3) for i in dx.cau_theo_muc(ban, m)])
        hs.update(ten=ten, buoc=0, tra_loi={})
        st.rerun()
    st.stop()

# ---------------- Làm bài: mỗi câu một màn hình ----------------
cau = [ban.phieu.cau_hoi[i] for i in hs["ids"]]
n = len(cau)
tra_loi: dict = hs["tra_loi"]


def di_toi(buoc: int):
    hs["buoc"] = buoc


def da_lam(c, v) -> bool:
    if c.dang in ("dung_sai", "noi_cot", "dien_khuyet"):
        return any(x not in (None, "") for x in (v or []))
    return v not in (None, "")


buoc = hs["buoc"]
so_da_lam = sum(da_lam(c, tra_loi.get(k)) for k, c in enumerate(cau))
st.progress(so_da_lam / n, text=f"Em là **{state.md(hs['ten'])}** · đã làm {so_da_lam}/{n} câu")

if buoc < n:
    c = cau[buoc]
    with st.container(border=True):
        st.markdown(f"**Câu {buoc + 1}/{n}** · {c.diem:g} điểm".replace(".", ","))
        st.html(f'<div class="de-bai">{state.html_an_toan(c.noi_dung)}</div>')
        cu = tra_loi.get(buoc)
        ds = [dx.bo_tien_to(x) for x in c.lua_chon]
        if c.dang == "trac_nghiem":
            tra_loi[buoc] = st.radio("Chọn đáp án đúng", range(len(ds)), index=cu, key=f"hs_{buoc}",
                                     format_func=lambda i: f"{dg.CHU[i]}. {ds[i]}")
        elif c.dang == "dung_sai":
            cu = cu or [None] * len(ds)
            tra_loi[buoc] = [{"Đúng": True, "Sai": False}.get(st.segmented_control(
                state.md(x), ["Đúng", "Sai"], key=f"hs_{buoc}_{i}",
                default={True: "Đúng", False: "Sai"}.get(cu[i]))) for i, x in enumerate(ds)]
        elif c.dang == "noi_cot":
            phai = [dx.bo_tien_to(x) for x in c.cot_phai]
            st.markdown("  \n".join(f"**{dg.CHU[j].lower()}.** {state.md(x)}" for j, x in enumerate(phai)))
            cu = cu or [None] * len(ds)
            tra_loi[buoc] = [st.segmented_control(f"{i + 1}. {state.md(x)} nối với", range(len(phai)), key=f"hs_{buoc}_{i}",
                                                  default=cu[i], format_func=lambda j: dg.CHU[j].lower())
                             for i, x in enumerate(ds)]
        elif c.dang == "dien_khuyet":
            so = dg.so_cho_trong(c.noi_dung)
            cu = (cu or []) + [""] * so
            cols = st.columns(min(so, 3))
            tra_loi[buoc] = [cols[j % len(cols)].text_input(f"Chỗ trống {j + 1}", value=cu[j], key=f"hs_{buoc}_{j}")
                             for j in range(so)]
        else:
            tra_loi[buoc] = st.text_area("Bài làm của em", value=cu or "", height=160, key=f"hs_{buoc}")

    c1, c2 = st.columns(2)
    c1.button("◀ Câu trước", on_click=di_toi, args=(buoc - 1,), disabled=buoc == 0, width="stretch")
    c2.button("Câu tiếp ▶" if buoc < n - 1 else "Xem lại bài ▶", on_click=di_toi, args=(buoc + 1,),
              type="primary", width="stretch")
    st.stop()

# ---------------- Xem lại & nộp ----------------
st.markdown("### 📋 Xem lại bài làm")
chua = [k for k, c in enumerate(cau) if not da_lam(c, tra_loi.get(k))]
for k, c in enumerate(cau):
    with st.container(horizontal=True, vertical_alignment="center"):
        st.markdown(f"**Câu {k + 1}:** " + ("⚠️ Chưa làm" if k in chua else "✅ Đã làm"), width="stretch")
        st.button("Sửa", key=f"hs_sua_{k}", on_click=di_toi, args=(k,))
if chua:
    st.warning(f"Em còn {len(chua)} câu chưa làm. Em có thể quay lại làm tiếp hoặc vẫn nộp bài.")
if st.button("📤 Nộp bài", type="primary", width="stretch", key="hs_nop"):
    ket_qua = []
    for k, c in enumerate(cau):
        kq = dg.tu_cham(c, tra_loi.get(k))
        ket_qua.append(kq.model_copy(update={"cau_so": k + 1}).model_dump() if kq else
                       {"cau_so": k + 1, "dat": "cho_cham", "diem_dat": 0, "ghi_chu": ""})
    tu_cham = [x for x in ket_qua if x["dat"] != "cho_cham"]
    het_tu_cham = len(tu_cham) == n
    muc = dg.muc_tt27(ban.phieu, hs["ids"], KetQuaCham.model_validate(
        {"ten_tren_phieu": "", "nhan_xet": "", "cau": ket_qua})) if het_tu_cham else ""
    kq_nop = kho.hs_nop_bai(state.db(), bai["id"], hs["ten"], hs["phieu"], [tra_loi.get(k) for k in range(n)],
                            ket_qua, round(sum(x["diem_dat"] for x in tu_cham), 2), muc,
                            "da_cham" if het_tu_cham else "cho_ai")
    if kq_nop == "ok":
        hs["ket_qua"] = ket_qua
        st.rerun()
    st.error({"da_nop": "Tên này đã nộp bài rồi. Nếu cần làm lại, em báo thầy cô nhé.",
              "dong": "Bài đã đóng, không nhận thêm bài nộp.", "het_han": "Đã hết hạn nộp bài.",
              "khong_co_ten": "Tên của em không có trong danh sách lớp."}.get(kq_nop, "Chưa nộp được, em thử lại nhé."))
