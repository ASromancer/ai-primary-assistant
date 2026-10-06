"""Gọi Gemini để sinh phiếu bài tập phân hóa theo TT27, đầu ra JSON có cấu trúc."""
from typing import Literal

from google import genai
from google.genai import types
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


class BanLuu(BaseModel):
    """Toàn bộ phiếu + thông số, dùng để lưu/mở lại file .json."""
    thong_so: ThongSo
    phieu: Phieu


SYSTEM = """Bạn là chuyên gia giáo dục tiểu học Việt Nam, am hiểu Chương trình GDPT 2018 và \
Thông tư 27/2020/TT-BGDĐT về đánh giá học sinh tiểu học. Bạn soạn câu hỏi phân hóa theo 3 mức của TT27:
- Mức 1: {m1}. Dành cho học sinh cần hỗ trợ: câu ngắn, trực diện, có gợi ý/mẫu.
- Mức 2: {m2}. Dành cho đại trà: tình huống quen thuộc (gia đình, trường lớp, bạn bè).
- Mức 3: {m3}. Dành cho học sinh hoàn thành tốt: tư duy mở, tìm quy luật, giải thích cách làm.
Quy tắc trình bày: văn bản thuần, KHÔNG markdown, KHÔNG LaTeX; dùng ký hiệu ×, :, =, <, > trực tiếp. \
Ngôn ngữ trong sáng, chuẩn sư phạm, phù hợp lứa tuổi, tên nhân vật Việt Nam. Số liệu và đáp án phải chính xác tuyệt đối; \
tự kiểm tra lại từng phép tính trước khi trả lời.""".format(m1=MUC[1], m2=MUC[2], m3=MUC[3])


def tao_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _goi(client, model, contents, schema, temperature=0.7):
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM,
        response_mime_type="application/json",
        response_schema=schema,
        temperature=temperature,
    )
    for _ in range(2):  # AI đôi khi trả JSON lỗi: thử lại 1 lần
        r = client.models.generate_content(model=model, contents=contents, config=cfg)
        if isinstance(r.parsed, schema):
            return r.parsed
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
}


def tao_lai_cau(client, model, ts: ThongSo, phieu: Phieu, idx: int, che_do: str) -> CauHoi:
    cu = phieu.cau_hoi[idx]
    prompt = f"""Phiếu bài tập môn {ts.mon} lớp {ts.lop}, bộ sách "{ts.bo_sach}", chủ đề: {ts.chu_de}.
Câu hiện tại (Mức {cu.muc}): {cu.model_dump_json()}
{CHE_DO[che_do]} Giữ nguyên số điểm {cu.diem}. Không trùng với các câu khác trong phiếu:
{[c.noi_dung for c in phieu.cau_hoi]}"""
    moi = chuan_hoa(_goi(client, model, [prompt], CauHoi, temperature=0.9))
    moi.muc, moi.diem = cu.muc, cu.diem
    return moi
