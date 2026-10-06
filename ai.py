"""Gọi Gemini để sinh phiếu bài tập phân hóa theo TT27, đầu ra JSON có cấu trúc."""
import hashlib
from typing import Literal

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field

DANG_BAI = {
    "trac_nghiem": "Trắc nghiệm",
    "dung_sai": "Đúng/Sai",
    "noi_cot": "Nối cột",
    "dien_khuyet": "Điền vào chỗ trống",
    "tu_luan": "Tự luận/Trình bày",
}

MUC = {
    1: "Nhận biết, nhắc lại được kiến thức, kĩ năng đã học",
    2: "Kết nối, sắp xếp kiến thức, kĩ năng đã học để giải quyết vấn đề tương tự",
    3: "Vận dụng kiến thức, kĩ năng đã học để giải quyết vấn đề mới trong học tập, cuộc sống",
}

# Số câu mỗi mức theo thời lượng (phút)
SO_CAU = {15: (2, 2, 1), 20: (3, 2, 2), 35: (4, 3, 3)}


class CauHoi(BaseModel):
    muc: int = Field(description="Mức độ theo TT27: 1, 2 hoặc 3")
    dang: Literal["trac_nghiem", "dung_sai", "noi_cot", "dien_khuyet", "tu_luan"]
    noi_dung: str = Field(description="Lệnh/đề bài. Điền khuyết dùng '.......' cho chỗ trống.")
    lua_chon: list[str] = Field(
        description="Trắc nghiệm: các phương án (không ghi A/B/C). Đúng/Sai: các nhận định. "
        "Nối cột: các ý cột trái. Dạng khác: để rỗng."
    )
    cot_phai: list[str] = Field(description="Chỉ dùng cho Nối cột: các ý cột phải (đã xáo trộn). Dạng khác: rỗng.")
    goi_y_hs: str = Field(description="Gợi ý/mẫu in trên phiếu cho học sinh (bắt buộc với Mức 1, có thể rỗng với mức khác)")
    dap_an: str
    huong_dan_cham: str = Field(description="Tiêu chí chấm/nhận xét ngắn cho giáo viên")
    diem: float


class Phieu(BaseModel):
    ten_bai: str = Field(description="Tên bài học ngắn gọn (lấy từ ảnh trang sách nếu có)")
    yeu_cau_can_dat: list[str] = Field(description="Yêu cầu cần đạt của bài theo Chương trình GDPT 2018")
    cau_hoi: list[CauHoi]
    loi_chuc: str


class ThongSo(BaseModel):
    mon: str
    lop: int
    bo_sach: str
    chu_de: str
    thoi_luong: int
    truong: str = ""


LOAI_VAN_DE = {
    "dap_an_sai": "Đáp án sai",
    "lech_muc": "Lệch mức độ",
    "ngon_ngu": "Ngôn ngữ",
    "trinh_bay": "Trình bày",
}


class VanDe(BaseModel):
    cau_so: int = Field(description="Số thứ tự câu trong phiếu (bắt đầu từ 1); 0 nếu là vấn đề chung")
    loai: Literal["dap_an_sai", "lech_muc", "ngon_ngu", "trinh_bay"]
    mo_ta: str
    de_xuat: str = Field(description="Cách sửa cụ thể")


class KiemDinh(BaseModel):
    diem: int = Field(description="Điểm chất lượng phiếu 0-100")
    nhan_xet_chung: str = Field(description="1-2 câu nhận xét tổng quát")
    van_de: list[VanDe]


class BanLuu(BaseModel):
    """Toàn bộ phiếu + thông số, dùng để lưu/mở lại file .json."""
    thong_so: ThongSo
    phieu: Phieu
    kiem_dinh: KiemDinh | None = None
    kiem_dinh_cho: str = ""  # dấu vân tay của phiếu lúc kiểm định


def dau_van_tay(phieu: Phieu) -> str:
    return hashlib.sha1(phieu.model_dump_json().encode()).hexdigest()


SYSTEM = """Bạn là chuyên gia giáo dục tiểu học Việt Nam, am hiểu Chương trình GDPT 2018 và \
Thông tư 27/2020/TT-BGDĐT về đánh giá học sinh tiểu học. Bạn soạn câu hỏi phân hóa theo 3 mức của TT27:
- Mức 1: {m1}. Dành cho học sinh cần hỗ trợ: câu ngắn, trực diện, có gợi ý/mẫu.
- Mức 2: {m2}. Dành cho đại trà: tình huống quen thuộc (gia đình, trường lớp, bạn bè).
- Mức 3: {m3}. Dành cho học sinh hoàn thành tốt: tư duy mở, tìm quy luật, giải thích cách làm.
Quy tắc trình bày: văn bản thuần, KHÔNG markdown, KHÔNG LaTeX; dùng ký hiệu ×, :, =, <, > trực tiếp. \
Ngôn ngữ trong sáng, chuẩn sư phạm, phù hợp lứa tuổi, tên nhân vật Việt Nam. Số liệu và đáp án phải chính xác tuyệt đối; \
tự kiểm tra lại từng phép tính trước khi trả lời.""".format(m1=MUC[1], m2=MUC[2], m3=MUC[3])


# Model dự phòng khi model chính quá tải (5xx), hết lượt (429) hoặc không tồn tại (404).
MODEL_DU_PHONG = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
CHUYEN_MODEL = {404, 429, 500, 502, 503, 504}


def tao_client(api_key: str) -> genai.Client:
    # SDK tự thử lại 1 lần sau 2 giây khi máy chủ lỗi tạm thời
    retry = types.HttpRetryOptions(attempts=2, initial_delay=2, http_status_codes=[500, 502, 503, 504])
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(retry_options=retry))


def _goi(client, model, contents, schema, temperature=0.7):
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=temperature,
    )
    loi = None
    for m in dict.fromkeys([model, *MODEL_DU_PHONG]):
        try:
            for _ in range(2):  # AI đôi khi trả JSON lỗi: thử lại 1 lần
                r = client.models.generate_content(model=m, contents=contents, config=cfg)
                if isinstance(r.parsed, schema):
                    return r.parsed
        except errors.APIError as e:
            if e.code not in CHUYEN_MODEL:
                raise
            loi = e
    if loi:
        raise loi
    raise ValueError("AI trả về dữ liệu không đúng định dạng. Vui lòng bấm tạo lại.")


def chuan_hoa(cau: CauHoi) -> CauHoi:
    cau.muc = min(3, max(1, int(cau.muc)))
    if cau.dang != "noi_cot":
        cau.cot_phai = []
    if cau.dang in ("dien_khuyet", "tu_luan"):
        cau.lua_chon = []
    return cau


def tao_phieu(client, model, ts: ThongSo, dang_bai: list[str], anh: list[tuple[bytes, str]], ghi_chu: str = "") -> Phieu:
    n1, n2, n3 = SO_CAU[ts.thoi_luong]
    dang = ", ".join(f"{k} ({DANG_BAI[k]})" for k in dang_bai)
    prompt = f"""Soạn phiếu bài tập phân hóa môn {ts.mon} lớp {ts.lop}, bộ sách "{ts.bo_sach}".
Chủ đề/bài học: {ts.chu_de or "(xem ảnh trang sách đính kèm)"}. Thời lượng làm bài: {ts.thoi_luong} phút.
Số câu: Mức 1 = {n1} câu, Mức 2 = {n2} câu, Mức 3 = {n3} câu. Sắp xếp theo mức tăng dần.
Chỉ dùng các dạng bài: {dang}. Đa dạng dạng bài giữa các câu.
Tổng điểm 10, chia theo độ khó. Lời chúc cuối phiếu ngắn gọn, động viên, vui tươi."""
    if anh:
        prompt += "\nẢnh đính kèm là trang sách giáo khoa: bám sát kiến thức, ngữ liệu trong ảnh; ra câu tương tự, không chép nguyên văn bài trong sách."
    if ghi_chu.strip():
        prompt += f"\nYêu cầu thêm của giáo viên: {ghi_chu.strip()}"
    contents = [types.Part.from_bytes(data=b, mime_type=m) for b, m in anh] + [prompt]
    phieu = _goi(client, model, contents, Phieu)
    phieu.cau_hoi = sorted((chuan_hoa(c) for c in phieu.cau_hoi), key=lambda c: c.muc)
    return phieu


CHE_DO = {
    "doi": "Soạn một câu KHÁC hẳn (khác ngữ liệu, có thể khác dạng bài), cùng mức độ và cùng mục tiêu.",
    "de_hon": "Soạn lại câu này DỄ HƠN rõ rệt (số nhỏ hơn, ít bước hơn, thêm gợi ý) nhưng vẫn thuộc cùng mức.",
    "kho_hon": "Soạn lại câu này KHÓ HƠN rõ rệt (nhiều bước hơn, cần lập luận) nhưng vẫn thuộc cùng mức.",
    "gop_y": "Soạn lại câu này để khắc phục góp ý của tổ chuyên môn bên dưới, vẫn thuộc cùng mức.",
}


def tao_lai_cau(client, model, ts: ThongSo, phieu: Phieu, idx: int, che_do: str, gop_y: str = "") -> CauHoi:
    cu = phieu.cau_hoi[idx]
    prompt = f"""Phiếu bài tập môn {ts.mon} lớp {ts.lop}, bộ sách "{ts.bo_sach}", chủ đề: {ts.chu_de}.
Câu hiện tại (Mức {cu.muc}): {cu.model_dump_json()}
{CHE_DO[che_do]} Giữ nguyên số điểm {cu.diem}. Không trùng với các câu khác trong phiếu:
{[c.noi_dung for c in phieu.cau_hoi]}"""
    if gop_y:
        prompt += f"\nGóp ý cần khắc phục: {gop_y}"
    moi = chuan_hoa(_goi(client, model, [prompt], CauHoi, temperature=0.9))
    moi.muc, moi.diem = cu.muc, cu.diem
    return moi


def kiem_dinh(client, model, ts: ThongSo, phieu: Phieu) -> KiemDinh:
    """Lượt AI thứ hai đóng vai tổ trưởng chuyên môn, soát lỗi phiếu."""
    cau = "\n".join(f"Câu {k}: {c.model_dump_json()}" for k, c in enumerate(phieu.cau_hoi, 1))
    prompt = f"""Bạn là tổ trưởng chuyên môn tiểu học, thẩm định phiếu bài tập môn {ts.mon} lớp {ts.lop}, \
chủ đề "{ts.chu_de}", {ts.thoi_luong} phút. Kiểm tra từng câu:
1. dap_an_sai: tự giải lại từng câu, đối chiếu đáp án; phương án trắc nghiệm có đúng một đáp án đúng.
2. lech_muc: câu có đúng mức TT27 đã gán không (mô tả mức ở hướng dẫn hệ thống).
3. ngon_ngu: từ ngữ có phù hợp học sinh lớp {ts.lop}, rõ ràng, không đánh đố.
4. trinh_bay: lệnh rõ, đủ dữ kiện, thời lượng hợp lý.
Chỉ nêu vấn đề THỰC SỰ cần sửa (không nêu ý khen). Phiếu tốt thì danh sách vấn đề rỗng.
Chấm điểm 0-100: trừ nặng khi đáp án sai.

{cau}"""
    kd = _goi(client, model, [prompt], KiemDinh, temperature=0.2)
    kd.diem = min(100, max(0, kd.diem))
    kd.van_de = [v for v in kd.van_de if 0 <= v.cau_so <= len(phieu.cau_hoi)]
    return kd
