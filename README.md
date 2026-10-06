# 📚 Trợ Lý Phân Hóa Bài Tập Tiểu Học – Chuẩn TT27

Ứng dụng web giúp giáo viên tiểu học soạn **phiếu bài tập phân hóa 3 mức độ** theo Thông tư 27/2020/TT-BGDĐT, bám Chương trình GDPT 2018, bằng AI Gemini (miễn phí).

## Tính năng

**✍️ Soạn phiếu**
- Phiếu 3 mức TT27 (nhận biết – kết nối – vận dụng), chọn lớp, môn, bộ sách (Kết nối tri thức, Chân trời sáng tạo, Cánh Diều), dạng bài, thời lượng 15/20/35 phút.
- **Chụp ảnh trang SGK** (tối đa 3 ảnh): AI ra đề bám sát trang sách.
- **AI kiểm định**: lượt AI thứ hai đóng vai tổ trưởng chuyên môn, soát đáp án sai, câu lệch mức, ngôn ngữ chưa hợp lứa tuổi. Kết quả là điểm chất lượng 0–100 và cảnh báo trên từng câu, kèm nút 🛠 *Sửa theo góp ý*.
- Chỉnh từng câu: 🔄 Đổi câu · ➖ Dễ hơn · ➕ Khó hơn · ✏️ Sửa tay · ↩️ Hoàn tác.
- **In ngay** trên trình duyệt (khổ A4, cỡ chữ 14/16/18) hoặc tải Word/ZIP: phiếu chung, 3 phiếu nhóm **Xanh / Cam / Tím** (tên màu trung tính, học sinh không thấy nhãn mức độ), đáp án + ma trận + yêu cầu cần đạt.

**🎬 Lớp học**: trình chiếu từng câu trên máy chiếu với thẻ màu kiểu Kahoot, đồng hồ đếm ngược, lật đáp án kèm pháo giấy, 🎲 gọi tên ngẫu nhiên, 🔊 đọc to câu hỏi (giọng tiếng Việt của trình duyệt), toàn màn hình, phím tắt. Không tốn lượt AI.

**👥 Lớp của tôi**: danh sách học sinh theo nhóm (dán từ Excel). **Đề A/B** chống nhìn bài: cùng cấu trúc, khác số liệu. **Phiếu theo tên**: mỗi em một trang có sẵn tên, đúng màu nhóm, có thể xen kẽ đề A/B. Tên học sinh không gửi cho AI.

**📷 Chấm bài**: tải ảnh bài làm cả lớp, AI chấm từng câu và viết nhận xét theo TT27. Mức Hoàn thành tốt / Hoàn thành / Chưa hoàn thành được tính bằng quy tắc cố định:
- Chưa hoàn thành: làm đúng dưới 50% số câu Mức 1.
- Hoàn thành tốt: Mức 1 và Mức 2 đúng từ 80% trở lên, Mức 3 đúng từ 50% trở lên.
- Hoàn thành: các trường hợp còn lại.

Sổ tổng hợp sửa được trực tiếp và xuất Excel. Một nút cập nhật nhóm Xanh/Cam/Tím cho phiếu lần sau.

**💾 Lưu/mở lại phiếu (.json)** và **phiếu mẫu có sẵn** (kèm kết quả kiểm định): trình chiếu được cả khi không có mạng.

## Cấu trúc

```text
app.py               Điều hướng, thanh bên cài đặt dùng chung
state.py             Trạng thái phiên, client AI, báo lỗi
trang/               Các trang: trang_chu, soan_phieu, lop_hoc, cham_bai, lop_cua_toi
ai.py                Gọi Gemini: soạn phiếu, kiểm định, đề B, chấm bài (JSON schema, tự chuyển model dự phòng)
danh_gia.py          Mức TT27, khớp tên học sinh, sổ tổng hợp Excel
docx_export.py       Xuất Word + ZIP (phiếu chung, phiếu nhóm, phiếu theo tên, đáp án)
html_export.py       Trang in A4 trên trình duyệt
classroom_html.py    Ứng dụng trình chiếu Lớp học (HTML/JS tự chứa)
mau/phieu_mau.json   Phiếu mẫu Toán lớp 2 (demo)
test_app.py          Kiểm thử (không cần API key)
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
- Kịch bản demo: chụp trang SGK → AI ra phiếu và tự kiểm định → *Sửa theo góp ý* → trình chiếu ở trang Lớp học (gọi tên, lật đáp án) → chấm vài bài mẫu bằng ảnh → cập nhật nhóm → in phiếu theo tên cho buổi sau.
- Streamlit Cloud cho app "ngủ" sau vài ngày không ai dùng: mở link trước buổi thi khoảng 5 phút để app kịp khởi động lại.
