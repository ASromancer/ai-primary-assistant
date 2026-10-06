import re
import unicodedata
from pathlib import Path

import streamlit as st
from google.genai import errors
from pydantic import ValidationError

import docx_export as dx
from ai import DANG_BAI, MUC, BanLuu, ThongSo, tao_client, tao_lai_cau, tao_phieu

st.set_page_config(page_title="Trợ Lý Phân Hóa Tiểu Học - TT27", page_icon="📚", layout="wide")


def _secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:  # chạy local không có secrets.toml
        return default


MODEL = _secret("GEMINI_MODEL", "gemini-3.8-flash")
PHIEU_MAU = Path(__file__).parent / "mau" / "phieu_mau.json"
MON_THEO_LOP = {
    1: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức"],
    2: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức"],
    3: ["Toán", "Tiếng Việt", "Tự nhiên và Xã hội", "Đạo đức", "Tin học", "Công nghệ"],
    4: ["Toán", "Tiếng Việt", "Khoa học", "Lịch sử và Địa lí", "Đạo đức", "Tin học", "Công nghệ"],
    5: ["Toán", "Tiếng Việt", "Khoa học", "Lịch sử và Địa lí", "Đạo đức", "Tin học", "Công nghệ"],
}
BO_SACH = ["Kết nối tri thức với cuộc sống", "Chân trời sáng tạo", "Cánh Diều"]
THOI_LUONG = {15: "15 phút – Khởi động/Củng cố", 20: "20 phút – Luyện tập", 35: "35 phút – Phiếu cuối tuần"}
SAO = dx.SAO


@st.cache_resource
def _client(api_key):
    return tao_client(api_key)


def loi_than_thien(e: Exception) -> str:
    if isinstance(e, errors.APIError):
        if e.code == 429:
            return "Đã hết lượt gọi AI miễn phí trong phút này. Vui lòng chờ khoảng 1 phút rồi thử lại."
        if e.code in (400, 401, 403) and "key" in str(e).lower():
            return "Gemini API Key không hợp lệ. Vui lòng kiểm tra lại key."
        if e.code == 404:
            return f"Model '{MODEL}' không khả dụng. Hãy đổi GEMINI_MODEL trong Secrets."
        if e.code >= 500:
            return "Máy chủ AI của Google đang quá tải (đã thử cả model dự phòng). Vui lòng thử lại sau 1–2 phút."
    return f"Đã xảy ra lỗi: {e}"


def bao_loi(e: Exception):
    st.error(loi_than_thien(e))
    with st.expander("Chi tiết kỹ thuật"):
        st.code(f"{type(e).__name__}: {e}")


def md(s: str) -> str:
    """Escape markdown để nội dung AI (vd '1.', '*') hiển thị đúng nguyên văn."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~<])", r"\\\1", s).replace("\n", "  \n")


def ten_file(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("đ", "d").replace("Đ", "D")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:50] or "Phieu"


@st.cache_data(max_entries=20)
def xuat_file(ban_json: str):
    files = dx.tat_ca(BanLuu.model_validate_json(ban_json))
    return files, dx.dong_goi_zip(files)


def mo_phieu(raw: bytes | str):
    try:
        st.session_state.ban = BanLuu.model_validate_json(raw)
    except ValidationError:
        st.sidebar.error("File không đúng định dạng phiếu của ứng dụng.")


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = _secret("GEMINI_API_KEY") or st.text_input(
        "Gemini API Key", type="password", help="Lấy miễn phí tại https://aistudio.google.com/apikey")
    truong = st.text_input("Tên trường (in trên phiếu)", placeholder="VD: Tiểu học Nguyễn Trãi")
    st.divider()
    st.subheader("📂 Phiếu đã lưu")
    if st.button("👀 Xem phiếu mẫu (không cần API key)", width="stretch"):
        mo_phieu(PHIEU_MAU.read_text(encoding="utf-8"))
    f = st.file_uploader("Mở lại phiếu (.json)", type="json")
    if f and st.button("Mở phiếu này", width="stretch"):
        mo_phieu(f.getvalue())
    st.divider()
    st.caption(f"Mô hình AI: `{MODEL}`. Ảnh tải lên được gửi tới Google Gemini để xử lý.")

# ---------------- Nhập thông số ----------------
st.title("📚 Trợ Lý Giáo Viên: Phiếu Bài Tập Phân Hóa")
st.caption("Ứng dụng AI đổi mới dạy học Tiểu học – Phân hóa 3 mức theo Thông tư 27/2020/TT-BGDĐT, "
           "bám Chương trình GDPT 2018")

c1, c2, c3, c4 = st.columns(4)
lop = c1.selectbox("Khối lớp", list(MON_THEO_LOP), format_func=lambda x: f"Lớp {x}")
mon = c2.selectbox("Môn học", MON_THEO_LOP[lop])
bo_sach = c3.selectbox("Bộ sách", BO_SACH)
thoi_luong = c4.selectbox("Thời lượng", list(THOI_LUONG), index=1, format_func=THOI_LUONG.get)

chu_de = st.text_input("Tên bài học / Chủ đề", placeholder="VD: Phép cộng có nhớ trong phạm vi 100")
c1, c2 = st.columns(2)
with c1:
    dang_bai = st.multiselect("Dạng bài", list(DANG_BAI), default=list(DANG_BAI), format_func=DANG_BAI.get)
    ghi_chu = st.text_area("Yêu cầu thêm (tuỳ chọn)", height=100,
                           placeholder="VD: Lồng ghép chủ đề an toàn giao thông; dùng tên địa danh ở Hà Nội...")
with c2:
    anh = st.file_uploader("📷 Ảnh trang sách giáo khoa (tuỳ chọn, tối đa 3 ảnh) – AI ra đề bám sát trang sách",
                           type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, max_upload_size=5)

if st.button("🚀 Tạo Phiếu Bài Tập Phân Hóa", type="primary", width="stretch"):
    if not api_key:
        st.error("Vui lòng nhập Gemini API Key ở thanh bên trái (hoặc cấu hình trong Secrets).")
    elif not chu_de.strip() and not anh:
        st.warning("Vui lòng nhập tên bài học hoặc tải lên ảnh trang sách.")
    elif len(anh) > 3:
        st.warning("Chỉ tải tối đa 3 ảnh.")
    elif not dang_bai:
        st.warning("Vui lòng chọn ít nhất một dạng bài.")
    else:
        with st.spinner("AI đang soạn phiếu 3 mức độ theo TT27... (khoảng 20–40 giây)"):
            try:
                ts = ThongSo(mon=mon, lop=lop, bo_sach=bo_sach, chu_de=chu_de.strip(), thoi_luong=thoi_luong)
                phieu = tao_phieu(_client(api_key), MODEL, ts, dang_bai,
                                  [(a.getvalue(), a.type) for a in anh], ghi_chu)
                ts.chu_de = ts.chu_de or phieu.ten_bai
                st.session_state.ban = BanLuu(thong_so=ts, phieu=phieu)
            except Exception as e:
                bao_loi(e)

if "ban" not in st.session_state:
    st.info("👆 Chọn thông số rồi bấm **Tạo phiếu**, hoặc bấm **Xem phiếu mẫu** ở thanh bên để xem thử.")
    st.stop()

# ---------------- Kết quả ----------------
ban: BanLuu = st.session_state.ban
ban.thong_so.truong = truong or ban.thong_so.truong
ts, phieu = ban.thong_so, ban.phieu
thu_tu = [i for m in (1, 2, 3) for i in dx.cau_theo_muc(ban, m)]
so_cau = {i: k + 1 for k, i in enumerate(thu_tu)}

st.divider()
st.subheader(f"📝 {ts.chu_de}")
st.caption(f"Môn {ts.mon} – Lớp {ts.lop} – {ts.bo_sach} – {ts.thoi_luong} phút")
cols = st.columns(4)
for m in (1, 2, 3):
    cols[m - 1].metric(f"{SAO[m]} Mức {m}", f"{len(dx.cau_theo_muc(ban, m))} câu")
tong = sum(c.diem for c in phieu.cau_hoi)
cols[3].metric("Tổng điểm", dx.so(tong))
if abs(tong - 10) > 0.01:
    st.warning(f"Tổng điểm hiện là {dx.so(tong)}, chưa bằng 10. Dùng nút ✏️ Sửa tay để chỉnh điểm từng câu.")


def lam_lai(i: int, che_do: str):
    if not api_key:
        st.error("Cần Gemini API Key để AI soạn lại câu.")
        return
    with st.spinner("AI đang soạn lại câu..."):
        try:
            phieu.cau_hoi[i] = tao_lai_cau(_client(api_key), MODEL, ts, phieu, i, che_do)
        except Exception as e:
            bao_loi(e)
            return
    st.rerun()


def hien_cau(i: int):
    c = phieu.cau_hoi[i]
    with st.container(border=True):
        st.markdown(f"**Câu {so_cau[i]}** · {DANG_BAI[c.dang]} · {dx.so(c.diem)} điểm")
        st.markdown(md(c.noi_dung))
        ds = [dx.bo_tien_to(x) for x in c.lua_chon]
        if c.dang == "trac_nghiem":
            st.markdown("  \n".join(f"{'ABCDEFGH'[k]}\\. {md(x)}" for k, x in enumerate(ds)))
        elif c.dang == "dung_sai":
            st.markdown("  \n".join(f"☐ {md(x)}" for x in ds))
        elif c.dang == "noi_cot":
            a, b = st.columns(2)
            a.markdown("  \n".join(f"{k + 1}\\. {md(x)}" for k, x in enumerate(ds)))
            b.markdown("  \n".join(f"{'abcdefgh'[k]}\\. {md(dx.bo_tien_to(x))}" for k, x in enumerate(c.cot_phai)))
        if c.goi_y_hs:
            st.caption(f"💡 Gợi ý: {c.goi_y_hs}")
        with st.expander("Đáp án & hướng dẫn chấm"):
            st.markdown(f"**Đáp án:** {md(c.dap_an)}  \n**Hướng dẫn chấm:** {md(c.huong_dan_cham)}")

        b1, b2, b3, b4 = st.columns(4)
        if b1.button("🔄 Đổi câu khác", key=f"doi{i}", width="stretch"):
            lam_lai(i, "doi")
        if b2.button("⬇️ Dễ hơn", key=f"de{i}", width="stretch"):
            lam_lai(i, "de_hon")
        if b3.button("⬆️ Khó hơn", key=f"kho{i}", width="stretch"):
            lam_lai(i, "kho_hon")
        with b4.popover("✏️ Sửa tay", width="stretch"):
            with st.form(f"sua{i}"):
                nd = st.text_area("Đề bài", c.noi_dung)
                lc = st.text_area("Lựa chọn / nhận định / cột trái (mỗi dòng một ý)", "\n".join(c.lua_chon))
                cp = st.text_area("Cột phải (chỉ dạng Nối cột)", "\n".join(c.cot_phai)) if c.dang == "noi_cot" else ""
                gy = st.text_input("Gợi ý cho học sinh", c.goi_y_hs)
                da = st.text_area("Đáp án", c.dap_an)
                diem = st.number_input("Điểm", min_value=0.0, max_value=10.0, value=float(c.diem), step=0.25)
                if st.form_submit_button("💾 Lưu", type="primary"):
                    tach = lambda s: [x.strip() for x in s.splitlines() if x.strip()]
                    phieu.cau_hoi[i] = c.model_copy(update=dict(
                        noi_dung=nd, lua_chon=tach(lc), cot_phai=tach(cp), goi_y_hs=gy, dap_an=da, diem=diem))
                    st.rerun()


tab1, tab2, tab3 = st.tabs(["✏️ Xem & chỉnh từng câu", "📊 Ma trận & đáp án", "📥 Tải về"])

with tab1:
    for m in (1, 2, 3):
        st.markdown(f"#### {SAO[m]} Mức {m} – {MUC[m]}")
        for i in dx.cau_theo_muc(ban, m):
            hien_cau(i)
    st.success(f"🌟 {phieu.loi_chuc}")

with tab2:
    st.markdown("**Yêu cầu cần đạt**")
    st.markdown("\n".join(f"- {md(y)}" for y in phieu.yeu_cau_can_dat))
    st.markdown("**Ma trận theo mức độ (TT27)**")
    head = ["Mức"] + list(DANG_BAI.values()) + ["Số câu", "Điểm"]
    st.table([dict(zip(head, row)) for row in dx.ma_tran(ban)], hide_index=True)
    st.markdown("**Phân phiếu theo nhóm học sinh**")
    for ten, ((chinh, them), _, nhom_hs) in dx.NHOM.items():
        st.markdown(f"- **Phiếu {ten}** – {nhom_hs}: câu Mức {chinh}" + (f" + 1 câu thử thách Mức {them}" if them else ""))
    st.markdown("**Đáp án**")
    vt = dx.vi_tri_trong_phieu(ban)
    st.table([{"Vị trí": vt[i], "Mức": c.muc, "Đáp án": c.dap_an, "Hướng dẫn chấm": c.huong_dan_cham}
              for i in thu_tu for c in [phieu.cau_hoi[i]]], hide_index=True)

with tab3:
    ban_json = ban.model_dump_json(indent=2)
    files, zip_bytes = xuat_file(ban_json)
    ten = ten_file(f"{ts.mon}_Lop{ts.lop}_{ts.chu_de}")
    st.download_button("📦 Tải trọn bộ (.zip): phiếu chung + 3 phiếu nhóm + đáp án & ma trận", zip_bytes,
                       f"{ten}.zip", "application/zip", type="primary", width="stretch", on_click="ignore")
    st.caption("Phiếu Xanh / Cam / Tím dùng tên màu trung tính để học sinh không thấy nhãn mức độ.")
    cols = st.columns(len(files))
    for col, (fname, data) in zip(cols, files.items()):
        col.download_button(f"📄 {fname[2:-5].replace('_', ' ')}", data, f"{ten}_{fname}",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            width="stretch", on_click="ignore")
    st.divider()
    st.download_button("💾 Lưu phiếu (.json) để mở lại / trình chiếu khi không có mạng", ban_json,
                       f"{ten}.json", "application/json", width="stretch", on_click="ignore")
