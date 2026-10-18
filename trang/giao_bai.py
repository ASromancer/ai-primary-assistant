import io
from datetime import datetime
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import pandas as pd
import segno
import streamlit as st

import danh_gia as dg
import docx_export as dx
import kho
import state
from ai import DANG_BAI, KetQuaCau, KetQuaCham, cham_bai

VN = ZoneInfo("Asia/Ho_Chi_Minh")
TRANG_THAI = {"cho_ai": "📥 Đã nộp – chờ chấm", "da_cham": "✅ Đã chấm"}
NHAN_DAT = {"dung": "✓ Đúng", "mot_phan": "½ Một phần", "sai": "✗ Sai", "bo_trong": "– Bỏ trống"}


def diem_tu_tinh(dat: str, diem_cau: float) -> float:
    return {"dung": diem_cau, "mot_phan": diem_cau / 2}.get(dat, 0.0)

st.markdown("## 📡 Giao bài online")
st.caption("Học sinh quét mã QR hoặc mở link, chọn tên mình rồi làm bài trên điện thoại/máy tính – không cần tài khoản. "
           "Câu trắc nghiệm, đúng/sai, nối cột được chấm ngay; phần còn lại AI chấm khi thầy cô bấm nút.")

if not state.ca_nhan():
    st.info("🔐 Cần đăng nhập và cấu hình database để giao bài online.")
    st.stop()

db, email = state.db(), state.email()


def link_lam_bai(ma: str) -> str:
    """Ưu tiên APP_URL trong Secrets (tên miền chính thức), sau đó địa chỉ trình duyệt đang mở."""
    url = urlsplit(st.context.url or "") if st.context.url else None
    goc = state._secret("APP_URL", "") or (f"{url.scheme}://{url.netloc}" if url and url.netloc else "http://localhost:8501")
    return f"{goc.rstrip('/')}/?ma={ma}"


def qr_png(noi_dung: str, scale: int = 8) -> bytes:
    bio = io.BytesIO()
    segno.make(noi_dung, error="m").save(bio, kind="png", scale=scale, border=2)
    return bio.getvalue()


def gio_vn(v) -> str:
    try:
        t = v if isinstance(v, datetime) else datetime.fromisoformat(str(v))
        return t.astimezone(VN).strftime("%H:%M %d/%m")
    except ValueError:
        return str(v)[:16]


def ids_cua_phieu(ban, phieu: str) -> list[int]:
    if phieu in dx.NHOM:
        chinh, them = dx.cau_cua_nhom(ban, phieu)
        return chinh + them
    return [i for m in (1, 2, 3) for i in dx.cau_theo_muc(ban, m)]


# ---------------- Giao bài mới ----------------
ds_gb = state.doc("giao_bai_ds")
ban_hien = state.ban_hien_tai()
with st.expander("➕ Giao bài mới", expanded=not ds_gb):
    if ban_hien is None:
        st.info("Mở hoặc soạn một phiếu trước, rồi quay lại đây để giao.")
        st.page_link(state.TRANG["soan_phieu"], label="Đi tới Soạn phiếu", icon="✍️")
    else:
        st.markdown(f"Phiếu: **{state.md(ban_hien.thong_so.chu_de)}** · {len(ban_hien.phieu.cau_hoi)} câu")
        ds_lop = state.doc("lop_ds")
        ten_lop = {x["id"]: f"{x['ten_lop'] or '(chưa đặt tên)'} · {x['si_so']} học sinh" for x in ds_lop}
        lua_chon = [*ten_lop, ""]
        lop_hien = getattr(st.session_state.get("lop"), "id", "")
        lop_id = st.selectbox("Lớp", lua_chon, index=lua_chon.index(lop_hien) if lop_hien in lua_chon else 0,
                              format_func=lambda x: ten_lop.get(x, "Không chọn lớp – học sinh tự gõ tên"))
        che_do = st.segmented_control(
            "Học sinh làm phiếu nào?", ["nhom", "chung"], default="nhom" if lop_id else "chung", key="gb_che_do",
            format_func={"nhom": "Theo nhóm Xanh/Cam/Tím của từng em", "chung": "Cả lớp làm phiếu chung"}.get,
            disabled=not lop_id, help="Theo nhóm: app tự giao phiếu đúng nhóm trong Lớp của tôi (phân hoá TT27)")
        han_nop = None
        if st.toggle("Đặt hạn nộp", key="gb_co_han"):
            c1, c2 = st.columns(2)
            ngay = c1.date_input("Ngày", format="DD/MM/YYYY")
            gio = c2.time_input("Giờ", value=datetime.now(VN).replace(hour=21, minute=0).time())
            han_nop = datetime.combine(ngay, gio, tzinfo=VN).astimezone(ZoneInfo("UTC")).isoformat()
        if st.button("📡 Giao bài và lấy mã", type="primary", key="gb_tao"):
            moi = state.ghi("giao_bai_tao", ban_hien, lop_id or None, (che_do or "chung") if lop_id else "chung", han_nop)
            st.session_state.gb_chon = moi["id"]
            st.rerun()

if not ds_gb:
    st.stop()

# ---------------- Bài đã giao ----------------
nhan_gb = {g["id"]: f"{g['ma']} · {g['tieu_de'][:45]} · {g['ten_lop'] or 'tự gõ tên'} · "
                    f"{'🟢 đang mở' if g['dang_mo'] else '🔒 đã đóng'} · {g['so_nop']} bài nộp" for g in ds_gb}
if st.session_state.get("gb_chon") not in nhan_gb:
    st.session_state.gb_chon = ds_gb[0]["id"]
gb_id = st.selectbox("Bài đã giao", list(nhan_gb), format_func=nhan_gb.get, key="gb_chon")
gb = next(g for g in ds_gb if g["id"] == gb_id)
chi_tiet = state.doc("giao_bai_mo", gb_id)
ban = chi_tiet["ban"]
link = link_lam_bai(gb["ma"])


@st.dialog("Mã vào làm bài", width="large")
def chieu_ma():
    st.html(f"""<div style="text-align:center"><div style="font-size:1.3rem">Mở <b>{state.html_an_toan(link.split('/?')[0])}</b>
và nhập mã, hoặc quét mã QR</div><div style="font-size:5.5rem;font-weight:800;letter-spacing:.6rem;color:#0D47A1">{gb['ma']}</div></div>""")
    _, giua, _ = st.columns([1, 2, 1])
    giua.image(qr_png(link, 14), width="stretch")


with st.container(border=True):
    trai, phai = st.columns([3, 1], vertical_alignment="center")
    with trai:
        st.html(f"""<div style="font-size:.95rem;color:#555">Mã bài</div>
<div style="font-size:3rem;font-weight:800;letter-spacing:.4rem;color:#0D47A1;line-height:1.1">{gb['ma']}</div>""")
        st.code(link, language=None)
        st.caption(f"{'🟢 Đang nhận bài' if gb['dang_mo'] else '🔒 Đã đóng'}"
                   + (f" · Hạn nộp {gio_vn(gb['han_nop'])}" if gb["han_nop"] else "")
                   + f" · {'Theo nhóm Xanh/Cam/Tím' if gb['che_do'] == 'nhom' else 'Phiếu chung'}")
        with st.container(horizontal=True):
            if st.button("📺 Chiếu mã lên lớp", type="primary", key="gb_chieu"):
                chieu_ma()
            if st.button("🔒 Đóng bài" if gb["dang_mo"] else "🔓 Mở lại", key="gb_dong_mo"):
                state.ghi("giao_bai_dong_mo", gb_id, not gb["dang_mo"])
                st.rerun()
    phai.image(qr_png(link), width="stretch")


# ---------------- Theo dõi trực tiếp ----------------
def doc_bai_lam() -> list[dict]:
    return kho.bai_lam_ds(db, email, gb_id)


@st.fragment(run_every="5s")
def theo_doi():
    bl = doc_bai_lam()
    theo_ten = {b["ten"]: b for b in bl}
    lop = state.doc("lop_mo", chi_tiet["lop_id"]) if chi_tiet["lop_id"] else None
    hang = []
    for h in (lop.hoc_sinh if lop else []):
        b = theo_ten.pop(h.ten, None)
        hang.append((h.ten, b["phieu"] if b else (h.nhom if gb["che_do"] == "nhom" else "Chung"), b))
    hang += [(t, b["phieu"], b) for t, b in theo_ten.items()]  # tên tự gõ / không còn trong lớp
    tong = len(hang)
    cols = st.columns(3)
    cols[0].metric("📥 Đã nộp", f"{len(bl)}/{tong}" if lop else len(bl), border=True)
    cols[1].metric("⏳ Chờ chấm", sum(b["trang_thai"] == "cho_ai" for b in bl), border=True)
    cols[2].metric("✅ Đã chấm", sum(b["trang_thai"] == "da_cham" for b in bl), border=True)
    bang = pd.DataFrame([{
        "Học sinh": t, "Phiếu": p,
        "Trạng thái": TRANG_THAI.get(b["trang_thai"], "") if b else "— chưa nộp",
        "Nộp lúc": gio_vn(b["nop_luc"]) if b else "",
        "Điểm": state.so_vn(b["diem"]) if b and b["diem"] is not None else "",  # ô trống, không hiện "None"
        "Mức TT27": b["muc_tt27"] if b else ""} for t, p, b in hang])
    st.dataframe(bang, hide_index=True, width="stretch")
    st.caption("🔄 Tự cập nhật mỗi 5 giây. Điểm của bài chờ chấm mới gồm phần tự chấm (trắc nghiệm, đúng/sai, nối cột).")


st.markdown("#### 👀 Theo dõi nộp bài")
theo_doi()

bl = doc_bai_lam()
if not bl:
    st.stop()

# ---------------- Chấm, cho làm lại, mở trong Chấm bài ----------------
cho_cham = [b for b in bl if b["trang_thai"] == "cho_ai" or not b["nhan_xet"]]
c1, c2 = st.columns(2)
with c1.container(border=True):
    st.markdown("**🤖 AI chấm & nhận xét**")
    st.caption("Chấm phần điền khuyết, tự luận và viết nhận xét TT27. AI chỉ nhận bài làm, không nhận tên học sinh.")
    if st.button(f"Chấm {len(cho_cham)} bài" if cho_cham else "Đã chấm hết", type="primary", key="gb_ai_cham",
                 disabled=not cho_cham, width="stretch"):
        if not state.api_key():
            st.error("Cần Gemini API Key.")
        else:
            tien = st.progress(0.0)
            for k, b in enumerate(cho_cham):
                tien.progress(k / len(cho_cham), text=f"Đang chấm bài {k + 1}/{len(cho_cham)}")
                ids = ids_cua_phieu(ban, b["phieu"])
                cau = [ban.phieu.cau_hoi[i] for i in ids]
                da_cham = {x["cau_so"]: KetQuaCau(**x) for x in b["ket_qua"] if x["dat"] != "cho_cham"}
                try:
                    kq = cham_bai(state.client(), state.MODEL, ban.thong_so, ban.phieu, ids,
                                  tra_loi=[dg.hien_thi_tra_loi(c, t) for c, t in zip(cau, b["tra_loi"])], da_cham=da_cham)
                except Exception as e:
                    st.warning(f"Bài {k + 1}: {state.loi_than_thien(e)}")
                    continue
                state.ghi("bai_lam_cham", b["id"], [x.model_dump() for x in kq.cau],
                          round(sum(x.diem_dat for x in kq.cau), 2), dg.muc_tt27(ban.phieu, ids, kq), kq.nhan_xet)
            tien.progress(1.0, text="Xong")
            st.rerun()

with c2.container(border=True):
    st.markdown("**↩️ Cho học sinh làm lại**")
    ten = st.selectbox("Học sinh", [b["ten"] for b in bl], index=None, placeholder="Chọn tên", key="gb_lam_lai_ten",
                       label_visibility="collapsed")
    if st.button("Xoá bài đã nộp để em làm lại", key="gb_lam_lai", disabled=not ten, width="stretch"):
        state.ghi("bai_lam_xoa", next(b["id"] for b in bl if b["ten"] == ten))
        st.rerun()

with st.container(border=True):
    st.markdown("**✍️ Chấm tay**")
    st.caption("Xem bài làm của từng em cạnh đáp án, chọn kết quả từng câu và viết nhận xét – không cần AI. "
               "Câu trắc nghiệm, đúng/sai, nối cột đã được chấm sẵn, thầy cô vẫn sửa được.")
    ten_ct = st.selectbox("Bài của học sinh", [b["ten"] for b in bl], index=None, placeholder="Chọn tên học sinh",
                          key="gb_ct_ten", format_func=lambda t: t + (" ✅" if next(
                              b for b in bl if b["ten"] == t)["trang_thai"] == "da_cham" else " ⏳"))
    if ten_ct:
        b = next(x for x in bl if x["ten"] == ten_ct)
        ids = ids_cua_phieu(ban, b["phieu"])
        kq_cu = {x["cau_so"]: x for x in b["ket_qua"]}
        with st.form(f"gb_ct_{b['id']}"):
            chon = []
            for k, i in enumerate(ids, 1):
                c, cu = ban.phieu.cau_hoi[i], kq_cu.get(k, {})
                tl = b["tra_loi"][k - 1] if k - 1 < len(b["tra_loi"]) else None
                st.markdown(f"**Câu {k}** · {DANG_BAI[c.dang]} · {state.so_vn(c.diem)} điểm  \n{state.md(c.noi_dung)}")
                st.info(f"✏️ **Bài làm:** {state.md(dg.hien_thi_tra_loi(c, tl))}")
                st.caption(f"**Đáp án:**  \n{state.md(c.dap_an)}")
                c1, c2, c3 = st.columns([3, 1.3, 3], vertical_alignment="bottom")
                dat = c1.segmented_control("Kết quả", list(NHAN_DAT), format_func=NHAN_DAT.get, key=f"gb_ct_{b['id']}_{k}",
                                           default=cu.get("dat") if cu.get("dat") in NHAN_DAT else None)
                diem = c2.number_input("Điểm", 0.0, float(c.diem), step=0.25, placeholder="tự tính",
                                       key=f"gb_ct_{b['id']}_{k}_d", help="Để trống: Đúng = đủ điểm, Một phần = nửa điểm",
                                       # chỉ điền sẵn điểm sửa tay; điểm đúng quy tắc để trống -> đổi kết quả là tính lại
                                       value=float(cu["diem_dat"]) if cu.get("dat") in NHAN_DAT and
                                       cu["diem_dat"] != diem_tu_tinh(cu["dat"], c.diem) else None)
                ghi = c3.text_input("Ghi chú lỗi (tuỳ chọn)", value=cu.get("ghi_chu", ""), key=f"gb_ct_{b['id']}_{k}_g")
                chon.append((k, c, dat, diem, ghi))
                st.divider()
            nx = st.text_area("Nhận xét (theo Thông tư 27)", value=b["nhan_xet"], height=90,
                              placeholder="Nêu điều em làm tốt, điều cần cố gắng và lời động viên")
            if st.form_submit_button("💾 Lưu kết quả chấm", type="primary"):
                if any(dat is None for _, _, dat, _, _ in chon):
                    st.error("Thầy cô chọn kết quả cho tất cả các câu trước khi lưu nhé.")
                else:
                    kq = KetQuaCham(ten_tren_phieu="", nhan_xet=nx.strip(), cau=[KetQuaCau(
                        cau_so=k, dat=dat, ghi_chu=ghi.strip(),
                        diem_dat=diem if diem is not None else diem_tu_tinh(dat, c.diem))
                        for k, c, dat, diem, ghi in chon])
                    state.ghi("bai_lam_cham", b["id"], [x.model_dump() for x in kq.cau],
                              round(sum(x.diem_dat for x in kq.cau), 2), dg.muc_tt27(ban.phieu, ids, kq), kq.nhan_xet)
                    st.toast(f"Đã lưu kết quả của {ten_ct}", icon="✅")
                    st.rerun()

with st.container(border=True):
    st.markdown("**📊 Phân tích & lưu hồ sơ**")
    st.caption("Mở kết quả đã chấm trong trang Chấm bài để dùng sổ tổng hợp, phân tích lỗi sai, phiếu bổ trợ "
               "và lưu vào hồ sơ tiến bộ của lớp.")
    phieu_co = [p for p in ["Chung", *dx.NHOM] if any(b["phieu"] == p and b["trang_thai"] == "da_cham" for b in bl)]
    if not phieu_co:
        st.caption("Chưa có bài nào đã chấm xong.")
    else:
        p = st.segmented_control("Phiếu", phieu_co, default=phieu_co[0], key="gb_phieu_mo",
                                 format_func=lambda x: "Phiếu chung" if x == "Chung" else f"Phiếu {x}") or phieu_co[0]
        if st.button(f"Mở kết quả {'Phiếu chung' if p == 'Chung' else 'Phiếu ' + p} trong Chấm bài", key="gb_mo_cham"):
            ids = ids_cua_phieu(ban, p)
            rows = []
            for b in (b for b in bl if b["phieu"] == p and b["trang_thai"] == "da_cham"):
                rows.append({"STT": len(rows) + 1, "Họ tên": b["ten"], "Điểm": b["diem"], "Mức TT27": b["muc_tt27"],
                             "Nhận xét": b["nhan_xet"],
                             **{f"Câu {x['cau_so']}": dg.KY_HIEU.get(x["dat"], "–") + (f" {x['ghi_chu']}" if x["ghi_chu"] else "")
                                for x in b["ket_qua"]}, "Ảnh": "online"})
            st.session_state.cham = {"rows": rows, "loi": [], "ver": st.session_state.get("cham", {}).get("ver", 0) + 1,
                                     "cau": [ban.phieu.cau_hoi[i] for i in ids], "ts": ban.thong_so,
                                     "loai": f"Online {gb['ma']} – {'Phiếu chung' if p == 'Chung' else 'Phiếu ' + p}"}
            st.switch_page(state.TRANG["cham_bai"])
