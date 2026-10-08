"""Trạng thái và tiện ích dùng chung cho mọi trang."""
import re
from pathlib import Path

import streamlit as st
from google.genai import errors
from pydantic import ValidationError

from ai import BanLuu, tao_client
from danh_gia import bo_dau

TRANG = {
    "trang_chu": "trang/trang_chu.py",
    "soan_phieu": "trang/soan_phieu.py",
    "thu_vien": "trang/thu_vien.py",
    "lop_hoc": "trang/lop_hoc.py",
    "cham_bai": "trang/cham_bai.py",
    "lop_cua_toi": "trang/lop_cua_toi.py",
    "tien_bo": "trang/tien_bo.py",
}
PHIEU_MAU = Path(__file__).parent / "mau" / "phieu_mau.json"


def _secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:  # chạy local không có secrets.toml
        return default


MODEL = _secret("GEMINI_MODEL", "gemini-3.8-flash")


def api_key() -> str:
    return _secret("GEMINI_API_KEY") or st.session_state.get("api_key_nhap", "")


def truong() -> str:
    return st.session_state.get("truong", "")


def ten_gv() -> str:
    return st.session_state.get("ten_gv", "")


@st.cache_resource
def _client(key):
    return tao_client(key)


def client():
    return _client(api_key())


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


def so_vn(x: float) -> str:
    return f"{x:g}".replace(".", ",")


def bao_loi(e: Exception):
    st.error(loi_than_thien(e))
    with st.expander("Chi tiết kỹ thuật"):
        st.code(f"{type(e).__name__}: {e}")


def md(s: str) -> str:
    """Escape markdown để nội dung AI (vd '1.', '*') hiển thị đúng nguyên văn."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~<])", r"\\\1", s).replace("\n", "  \n")


def ten_file(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", bo_dau(s)).strip("_")[:50] or "Phieu"


def ban_hien_tai() -> BanLuu | None:
    ban = st.session_state.get("ban")
    if ban is not None and truong():
        ban.thong_so.truong = truong()
    return ban


def dat_phieu(ban: BanLuu):
    """Đặt phiếu đang làm việc và ghi vào lịch sử phiên (tối đa 10)."""
    lich_su = st.session_state.setdefault("lich_su", [])
    if not any(b is ban for b in lich_su):
        lich_su.insert(0, ban)
        del lich_su[10:]
    st.session_state.ban = ban
    st.session_state.pop("hoan_tac", None)


def mo_phieu(raw: bytes | str):
    try:
        dat_phieu(BanLuu.model_validate_json(raw))
    except ValidationError:
        st.error("File không đúng định dạng phiếu của ứng dụng.")


def dat_lop(moi):
    """Thay danh sách lớp và làm mới bảng nhập liệu ở trang Lớp của tôi."""
    st.session_state.lop = moi
    st.session_state.lop_ver = st.session_state.get("lop_ver", 0) + 1


def can_phieu() -> BanLuu:
    """Trả phiếu hiện tại; nếu chưa có thì hướng dẫn và dừng trang."""
    ban = ban_hien_tai()
    if ban is None:
        st.info("Chưa có phiếu nào. Hãy soạn phiếu mới hoặc mở phiếu mẫu.")
        c1, c2 = st.columns(2)
        c1.page_link(TRANG["soan_phieu"], label="Soạn phiếu", icon="✍️")
        if c2.button("👀 Mở phiếu mẫu", key="mau_can"):
            mo_phieu(PHIEU_MAU.read_text(encoding="utf-8"))
            st.rerun()
        st.stop()
    return ban


# ---------------- Cá nhân hoá: đăng nhập + database ----------------
def co_auth() -> bool:
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def co_db() -> bool:
    try:
        return "sql" in st.secrets.get("connections", {})
    except Exception:
        return False


def email() -> str:
    return st.user.email if co_auth() and st.user.is_logged_in else ""


def cho_phep_khach() -> bool:
    """Mặc định bắt buộc đăng nhập; đặt CHE_DO_KHACH = true trong Secrets để cho dùng không cần đăng nhập."""
    return bool(_secret("CHE_DO_KHACH", False))


def da_dang_nhap() -> bool:
    return bool(email())


def nut_dang_nhap(key: str, nho: bool = False):
    """Nút đăng nhập luôn hiển thị khi chưa đăng nhập; chưa cấu hình [auth] thì nút mờ kèm hướng dẫn."""
    if co_auth():
        st.button("🔐 Đăng nhập bằng Google", on_click=st.login, type="primary", key=key,
                  width="stretch" if nho else "content")
    else:
        st.button("🔐 Đăng nhập bằng Google", disabled=True, key=key, width="stretch" if nho else "content",
                  help="Quản trị viên cần thêm khối [auth] vào Secrets – xem README, mục Bật đăng nhập.")
        st.caption("⚙️ Chưa bật đăng nhập: thêm khối `[auth]` (Google OAuth) vào Secrets của app.")


def chuan_hoa_url(url: str) -> str:
    """Chuỗi Supabase dán nguyên (postgresql://...) -> dùng driver psycopg2 đã cài.
    (SQLAlchemy 2.1 mặc định 'postgresql://' là psycopg v3, không được cài.)"""
    url = url.strip()
    for dau in ("postgres://", "postgresql://", "postgresql+psycopg://"):
        if url.startswith(dau):
            return "postgresql+psycopg2://" + url[len(dau):]
    return url


def db():
    url = chuan_hoa_url(st.secrets["connections"]["sql"]["url"])
    # pool_pre_ping: kiểm tra kết nối trước khi dùng (pooler Supabase hay đóng kết nối nhàn rỗi)
    return st.connection("sql", type="sql", url=url, pool_pre_ping=True, pool_recycle=300).engine


@st.cache_data(ttl=60, show_spinner=False)
def _doc(ten: str, email_: str, *args):
    import kho
    return getattr(kho, ten)(db(), email_, *args)


def doc(ham: str, /, *args):
    """Đọc từ kho có cache 60 giây (database ở xa: mỗi truy vấn ~0,2 giây). ten: tên hàm trong kho.py."""
    return _doc(ham, email(), *args)


def ghi(ham: str, /, *args, **kw):
    """Ghi vào kho rồi xoá cache đọc để lần sau thấy dữ liệu mới."""
    import kho
    out = getattr(kho, ham)(db(), email(), *args, **kw)
    _doc.clear()
    return out


def ca_nhan() -> bool:
    """Đã đăng nhập và có database: bật lưu trữ cá nhân."""
    return bool(email()) and co_db()


def _gio_vn() -> str:
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%H:%M")


def _dau(obj) -> str:
    return obj.model_dump_json() if hasattr(obj, "model_dump_json") else repr(obj)


def nap_ho_so():
    """Lần đầu trong phiên sau khi đăng nhập: nạp hồ sơ và lớp gần nhất từ database."""
    if email() and co_auth() and st.session_state.get("ten_google") != email():
        st.session_state.ten_google = email()  # một lần mỗi phiên: điền sẵn tên tài khoản Google
        st.session_state.ten_gv = st.session_state.get("ten_gv") or st.user.to_dict().get("name", "")
    if not ca_nhan() or st.session_state.get("ho_so_nap") == email():
        return
    import kho
    try:
        hs = kho.ho_so_lay(db(), email())
        ds_lop = kho.lop_ds(db(), email())
        lop = kho.lop_mo(db(), email(), ds_lop[-1]["id"]) if ds_lop and "lop" not in st.session_state else None
    except Exception as e:
        st.sidebar.warning(f"Chưa kết nối được database: {e}")
        st.session_state.ho_so_nap = email()  # không thử lại (và không báo lỗi) ở mọi lần chạy
        return
    st.session_state.ho_so = hs
    st.session_state.ten_gv = hs.get("ten") or st.session_state.get("ten_gv", "")
    st.session_state.truong = hs.get("truong", "")
    if lop:
        st.session_state.lop = lop
    st.session_state.da_luu = {"ho_so": (st.session_state.ten_gv, st.session_state.truong),
                               "lop": _dau(st.session_state.get("lop"))}
    st.session_state.ho_so_nap = email()


def tu_luu():
    """Lưu những gì đã thay đổi (phiếu hiện tại, lớp hiện tại, tên/trường). Gọi sau mỗi lần chạy trang."""
    if not ca_nhan():
        return
    da_luu = st.session_state.setdefault("da_luu", {})
    try:
        ban = st.session_state.get("ban")
        if ban is not None and da_luu.get("phieu") != _dau(ban):
            ghi("phieu_luu", ban)
            da_luu["phieu"] = _dau(ban)
            st.session_state.luu_luc = _gio_vn()
        lop = st.session_state.get("lop")
        if lop is not None and (lop.hoc_sinh or lop.ten_lop) and da_luu.get("lop") != _dau(lop):
            ghi("lop_luu", lop)
            da_luu["lop"] = _dau(lop)
            st.session_state.luu_luc = _gio_vn()
        ho_so = (ten_gv(), truong())
        if da_luu.get("ho_so") != ho_so:
            ghi("ho_so_luu", ten=ho_so[0], truong=ho_so[1])
            da_luu["ho_so"] = ho_so
    except Exception as e:
        if st.session_state.get("loi_luu") != str(e):  # báo một lần, tránh lặp ở mọi lần chạy
            st.session_state.loi_luu = str(e)
            st.toast(f"Chưa lưu được lên database: {e}", icon="⚠️")


def luu_mac_dinh(**truong):
    """Ghi nhớ lựa chọn gần nhất (lớp, môn, bộ sách, yêu cầu thêm) làm mặc định cho lần sau."""
    st.session_state.setdefault("ho_so", {}).update(truong)
    if ca_nhan():
        try:
            ghi("ho_so_luu", **truong)
        except Exception:
            pass
