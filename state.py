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
    "lop_hoc": "trang/lop_hoc.py",
    "cham_bai": "trang/cham_bai.py",
    "lop_cua_toi": "trang/lop_cua_toi.py",
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
