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

**🔐 Cá nhân hoá (đăng nhập Google + database)**: hồ sơ giáo viên (form tự điền lựa chọn gần nhất), **📚 Thư viện** phiếu tự lưu (tìm không dấu, gắn sao, nhân bản), nhiều lớp lưu lâu dài, lưu kết quả chấm vào hồ sơ lớp. **📈 Tiến bộ**: bảng mức TT27 của từng em qua các lần chấm, biểu đồ từng em, AI gợi ý **nhận xét học bạ cuối kỳ** (không gửi tên học sinh), xuất Excel. Trang chủ có thống kê: số phiếu, số bài chấm, giờ tiết kiệm ước tính. Không cấu hình thì app chạy ở chế độ khách như bình thường.

**💾 Lưu/mở lại phiếu (.json)** và **phiếu mẫu có sẵn** (kèm kết quả kiểm định): trình chiếu được cả khi không có mạng.

## Cấu trúc

```text
app.py               Điều hướng, thanh bên cài đặt dùng chung
state.py             Trạng thái phiên, client AI, đăng nhập, tự lưu
kho.py               Truy cập database (mọi truy vấn lọc theo email giáo viên)
sql/schema.sql       Tạo bảng trên Supabase (chạy một lần)
trang/               Các trang: trang_chu, soan_phieu, thu_vien, lop_hoc, cham_bai, lop_cua_toi, tien_bo
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

## Bật đăng nhập và lưu dữ liệu (tuỳ chọn, ~20 phút)

Streamlit Cloud không giữ được file trên ổ đĩa, nên dữ liệu được lưu trên **Supabase** (Postgres miễn phí) và giáo viên đăng nhập bằng **Google**.

**A. Tạo database Supabase**
1. Vào <https://supabase.com>, tạo tài khoản rồi bấm **New project**. Chọn Region **Southeast Asia (Singapore)**, đặt mật khẩu database và ghi lại mật khẩu này.
2. Mở **SQL Editor** → **New query**, dán toàn bộ nội dung file [sql/schema.sql](sql/schema.sql), rồi bấm **Run**.
3. Bấm **Connect** (trên cùng) và chọn **Session pooler**. Copy chuỗi URI, thay `[YOUR-PASSWORD]` bằng mật khẩu ở bước 1, rồi đổi `postgresql://` thành `postgresql+psycopg2://`.
   (Streamlit Cloud không kết nối được tới địa chỉ "Direct connection" vì địa chỉ đó chỉ có IPv6; phải dùng Session pooler.)

**B. Tạo đăng nhập Google**
1. Vào <https://console.cloud.google.com>, tạo một project mới.
2. Vào **Google Auth Platform → Branding**: điền tên ứng dụng và email hỗ trợ. Ở mục **Audience** chọn *External*, sau đó bấm **Publish app** để mọi tài khoản Google đều đăng nhập được. Nếu để chế độ *Testing* thì chỉ những email được thêm vào danh sách Test users mới đăng nhập được.
3. Vào **Clients → Create client**, chọn loại *Web application*. Ở **Authorized redirect URIs** thêm hai địa chỉ:
   - `https://TEN-APP.streamlit.app/oauth2callback`
   - `http://localhost:8501/oauth2callback`
4. Copy **Client ID** và **Client secret**.

**C. Dán vào Secrets** (Streamlit Cloud → App settings → Secrets), theo mẫu trong [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example):

```toml
[auth]
redirect_uri = "https://TEN-APP.streamlit.app/oauth2callback"
cookie_secret = "..."   # tạo bằng: python -c "import secrets; print(secrets.token_hex(32))"
client_id = "....apps.googleusercontent.com"
client_secret = "GOCSPX-..."
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[connections.sql]
url = "postgresql+psycopg2://postgres.MA_PROJECT:MAT_KHAU@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
```

**Bảo mật:** các bảng đã bật RLS và bị chặn với vai trò `anon`/`authenticated`, nên API công khai của Supabase không đọc được dữ liệu. Chỉ app (giữ chuỗi kết nối bí mật) mới truy cập được, và mọi truy vấn đều lọc theo email của giáo viên. Tên học sinh không gửi cho AI, trừ trường hợp tên nằm sẵn trong ảnh bài làm khi chấm.

**Lưu ý:** project Supabase gói miễn phí tự tạm dừng sau 7 ngày không ai dùng. Trước buổi demo, vào dashboard Supabase bấm **Restore** nếu project đang tạm dừng.

## Mẹo trình chiếu (thi sáng kiến / giáo viên giỏi)

- Trước buổi thi, tạo sẵn 2–3 phiếu đẹp rồi bấm **Lưu phiếu (.json)**. Nếu mạng chập chờn thì mở lại file đó, không phải chờ AI.
- Kịch bản demo: chụp trang SGK → AI ra phiếu và tự kiểm định → *Sửa theo góp ý* → trình chiếu ở trang Lớp học (gọi tên, lật đáp án) → chấm vài bài mẫu bằng ảnh → cập nhật nhóm → in phiếu theo tên cho buổi sau.
- Streamlit Cloud cho app "ngủ" sau vài ngày không ai dùng: mở link trước buổi thi khoảng 5 phút để app kịp khởi động lại.
