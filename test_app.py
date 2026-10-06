"""Chạy: python test_app.py (không cần API key, không gọi mạng)."""
import io
import zipfile
from types import SimpleNamespace

from docx import Document
from streamlit.testing.v1 import AppTest

import ai
import docx_export as dx

BAN = ai.BanLuu.model_validate_json(open("mau/phieu_mau.json", encoding="utf-8").read())


class FakeClient:
    """Trả lần lượt các kết quả parsed định sẵn, thay cho Gemini."""
    def __init__(self, *parsed):
        self.parsed, self.calls = list(parsed), 0
        self.models = self

    def generate_content(self, model, contents, config):
        self.calls += 1
        return SimpleNamespace(parsed=self.parsed.pop(0))


def test_tao_phieu_sap_xep_va_thu_lai():
    p = BAN.phieu.model_copy(deep=True)
    p.cau_hoi.reverse()
    p.cau_hoi[0].muc = 7  # AI trả mức sai -> kẹp về 3
    client = FakeClient(None, p)  # lần 1 JSON hỏng -> thử lại
    out = ai.tao_phieu(client, "m", BAN.thong_so, list(ai.DANG_BAI), [])
    assert client.calls == 2
    assert [c.muc for c in out.cau_hoi] == sorted(c.muc for c in out.cau_hoi)
    assert max(c.muc for c in out.cau_hoi) == 3


def test_chuyen_model_du_phong_khi_qua_tai():
    class Client503(FakeClient):
        def generate_content(self, model, contents, config):
            self.models_used.append(model)
            if model == "m":
                raise ai.errors.APIError(503, {"error": {"message": "overloaded", "status": "UNAVAILABLE"}})
            return super().generate_content(model, contents, config)
    client = Client503(BAN.phieu.model_copy(deep=True))
    client.models_used = []
    ai.tao_phieu(client, "m", BAN.thong_so, list(ai.DANG_BAI), [])
    assert client.models_used == ["m", ai.MODEL_DU_PHONG[0]]

    sai_key = FakeClient()
    sai_key.generate_content = lambda **kw: (_ for _ in ()).throw(ai.errors.APIError(400, {"error": {"message": "API key not valid"}}))
    try:
        ai.tao_phieu(sai_key, "m", BAN.thong_so, list(ai.DANG_BAI), [])
        assert False, "lỗi 400 phải báo ngay, không chuyển model"
    except ai.errors.APIError as e:
        assert e.code == 400


def test_tao_lai_cau_giu_muc_va_diem():
    moi = BAN.phieu.cau_hoi[0].model_copy(update=dict(muc=3, diem=5, noi_dung="Câu mới"))
    out = ai.tao_lai_cau(FakeClient(moi), "m", BAN.thong_so, BAN.phieu, 0, "de_hon")
    assert (out.muc, out.diem, out.noi_dung) == (1, 1, "Câu mới")


def test_xuat_word():
    files = dx.tat_ca(BAN)
    assert len(files) == 5
    with zipfile.ZipFile(io.BytesIO(dx.dong_goi_zip(files))) as z:
        assert sorted(z.namelist()) == sorted(files)

    def text(b):
        d = Document(io.BytesIO(b))
        return "\n".join([p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells])

    chung = text(files["1_Phieu_chung.docx"])
    assert all(c.noi_dung in chung for c in BAN.phieu.cau_hoi)
    assert "Mức" not in chung  # phiếu học sinh không lộ nhãn mức độ
    xanh = text(files["2_Phieu_Xanh.docx"])  # 3 câu mức 1 + 1 câu thử thách mức 2
    assert "Câu 4" in xanh and "Câu 5" not in xanh and "THỬ THÁCH THÊM" in xanh
    assert "THỬ THÁCH THÊM" not in text(files["4_Phieu_Tim.docx"])
    da = text(files["5_Dap_an_Ma_tran.docx"])
    assert "B. 43" in da and "Chung: 1; Xanh: 1" in da
    assert dx.ma_tran(BAN)[-1][-2:] == [7, 10.0]


def test_bo_tien_to():
    assert dx.bo_tien_to("A. 43") == "43"
    assert dx.bo_tien_to("2) quả cam") == "quả cam"
    assert dx.bo_tien_to("1.5 kg") == "1.5 kg"


def test_giao_dien_phieu_mau():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    at.sidebar.button[0].click().run()  # Xem phiếu mẫu
    assert not at.exception
    assert any("Phép cộng có nhớ" in s.value for s in at.subheader)
    at.button(key="doi0").click().run()  # chưa có API key -> báo lỗi, không crash
    assert not at.exception and at.error


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("OK", name)
