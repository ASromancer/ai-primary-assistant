# 📚 Trợ Lý Phân Hóa Bài Tập Tiểu Học – Chuẩn TT27

Ứng dụng web giúp giáo viên tiểu học soạn **phiếu bài tập phân hóa 3 mức độ** theo Thông tư 27/2020/TT-BGDĐT, bám Chương trình GDPT 2018, bằng AI Gemini (miễn phí).

## Tính năng

- **Phiếu 3 mức (TT27)**: Mức 1 nhận biết – Mức 2 kết nối – Mức 3 vận dụng, số câu tự điều chỉnh theo thời lượng 15/20/35 phút.
- **Chọn lớp, môn, bộ sách** (Kết nối tri thức, Chân trời sáng tạo, Cánh Diều) và **dạng bài** (trắc nghiệm, đúng/sai, nối cột, điền khuyết, tự luận).
- **Chụp ảnh trang SGK**: tải lên tối đa 3 ảnh, AI ra đề bám đúng nội dung trang sách.
- **Chỉnh từng câu**: 🔄 Đổi câu khác · ⬇️ Dễ hơn · ⬆️ Khó hơn · ✏️ Sửa tay, không phải tạo lại cả phiếu.
- **Xuất Word để in** (Times New Roman 14, khổ A4), tải trọn bộ một file ZIP:
  - Phiếu chung (đủ 3 mức, ghi là "Thử thách 1/2/3 sao")
  - 3 phiếu nhóm **Xanh / Cam / Tím**: tên màu trung tính, học sinh không thấy nhãn mức độ; mỗi phiếu có thêm 1 câu thử thách ở mức kế tiếp
  - Đáp án + ma trận đề + yêu cầu cần đạt + hướng dẫn chấm (dành cho giáo viên)
  - Có mục **học sinh tự đánh giá** và **nhận xét của giáo viên**, đúng tinh thần TT27
- **Lưu/mở lại phiếu (.json)** và **phiếu mẫu có sẵn**: trình chiếu được cả khi không có mạng hoặc chưa có API key.

## Cấu trúc

```text
app.py              Giao diện Streamlit
ai.py               Gọi Gemini, cấu trúc dữ liệu phiếu (JSON schema)
docx_export.py      Xuất Word + ZIP
mau/phieu_mau.json  Phiếu mẫu Toán lớp 2 (demo)
test_app.py         Kiểm thử (không cần API key)
```

## Chạy trên máy

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # rồi điền key
streamlit run app.py
python test_app.py   # kiểm thử
```

Lấy Gemini API Key miễn phí tại <https://aistudio.google.com/apikey>

## Triển khai lên Streamlit Community Cloud (miễn phí)

1. Đẩy code lên GitHub (repo Public hoặc Private đều được).
2. Vào <https://share.streamlit.io>, đăng nhập bằng GitHub.
3. Bấm **Create app** → **Deploy a public app from GitHub** → chọn repo, nhánh `main`, file `app.py`.
4. Mở **Advanced settings**: chọn Python **3.12**, rồi dán vào ô **Secrets**:

   ```toml
   GEMINI_API_KEY = "key_gemini_cua_ban"
   ```

5. Bấm **Deploy**, đợi 2–3 phút là app chạy.

Muốn đổi model AI (khi Google ngừng model cũ): thêm `GEMINI_MODEL = "ten-model-moi"` vào Secrets. Mặc định là `gemini-3.8-flash`.

> **Lưu ý:** key nằm trong Secrets thì mọi người mở link đều dùng chung key của bạn. Gói miễn phí có giới hạn số lượt mỗi phút/ngày. Nếu chỉ dùng để demo, có thể bỏ trống Secrets để mỗi người tự nhập key ở thanh bên.

## Mẹo trình chiếu (thi sáng kiến / giáo viên giỏi)

- Trước buổi thi, tạo sẵn 2–3 phiếu đẹp rồi bấm **Lưu phiếu (.json)**. Nếu mạng chập chờn thì mở lại file đó, không phải chờ AI.
- Kịch bản demo ấn tượng: chụp trang SGK bằng điện thoại → tải lên → AI ra phiếu → bấm "Dễ hơn" một câu → tải ZIP → mở phiếu Xanh/Cam/Tím.
- Streamlit Cloud cho app "ngủ" sau vài ngày không ai dùng: mở link trước buổi thi khoảng 5 phút để app kịp khởi động lại.
