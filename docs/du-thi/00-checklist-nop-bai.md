# Checklist nộp bài – Giải thưởng Tiên phong Ứng dụng AI trong Giáo dục Việt Nam 2026

**Hạn nộp: 23h59 ngày 25/10/2026 (giờ Việt Nam).** Nộp tại <https://apps.rmit.edu.vn/r/nopsanphamGTTP2026>.
Bảng dự thi: **Bảng A** (giáo viên, cán bộ quản lý Mầm non và Tiểu học).

Trong toàn bộ hồ sơ, các chỗ đánh dấu `⟦…⟧` cần điền **thông tin hoặc số liệu thật**. Tuyệt đối không ghi số liệu ước đoán như thể là số đo thật.

## 1. Việc cần làm ngay (hôm nay, Chủ nhật 18/10)

- [ ] **Gửi email hỏi Ban Tổ chức về quyền tác giả** (mẫu ở mục 6). Thể lệ ghi: *"Các trường hợp nhờ người khác hỗ trợ hoặc thực hiện thay sẽ không được công nhận."* Cần xác nhận việc giáo viên nhận hỗ trợ lập trình có được chấp nhận hay không, trước khi đầu tư thời gian cho hồ sơ.
- [x] Tải bộ mẫu PowerPoint và Poster của Ban Tổ chức (đã có trong `docs/`, đã điền vào `Slide-du-thi.pptx` và `Poster-du-thi.pptx`).
- [ ] **Thêm `MA_DEMO` vào Secrets của app rồi Reboot.** Mã đã được tạo sẵn trong `ban-nop/ma-demo.txt` (chạy `.venv/bin/python docs/du-thi/tao_ma_demo.py` để xem lại). Mở thử link dùng thử bằng cửa sổ ẩn danh.
- [ ] In [in-thi-diem.pdf](in-thi-diem.pdf) (bảng ghi chép, khảo sát giáo viên, phiếu học sinh) cho đợt thí điểm.
- [ ] Đăng nhập app bằng tài khoản Google của giáo viên dự thi. Tạo lớp thật, nhập danh sách học sinh và chia nhóm Xanh/Cam/Tím.
- [ ] Xin phép Ban Giám hiệu cho thí điểm. Nếu quay hình hoặc chụp ảnh học sinh, xin phép phụ huynh và không để lộ mặt, tên thật của học sinh.

## 2. Thí điểm và thu số liệu (thứ Hai 19/10 – thứ Sáu 23/10)

Làm theo [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md). Đầu ra cần có:

- [ ] Bảng số liệu thời gian (soạn phiếu, chấm và nhận xét) trước và sau khi dùng app.
- [ ] Kết quả phiếu bổ trợ: tỉ lệ học sinh chưa đạt, trước và sau khi dạy bổ trợ.
- [ ] Phiếu khảo sát học sinh và giáo viên (ít nhất 2–3 đồng nghiệp dùng thử).
- [ ] Ảnh chụp màn hình thống kê ở Trang chủ (số phiếu, số bài chấm) bằng tài khoản thật.
- [ ] 3–5 ảnh hoặc clip ngắn cảnh dùng trên lớp (không lộ mặt học sinh).

## 3. Làm hồ sơ (song song từ 21/10, hoàn thiện thứ Bảy 24/10)

| Thành phần | Yêu cầu của Ban Tổ chức | Nội dung soạn sẵn |
|---|---|---|
| Slide | Mẫu của Ban Tổ chức, **xuất PDF, ≤ 15 trang, ≤ 100MB** | **`Slide-du-thi.pptx`** (14 trang, đã trên mẫu); lời thuyết trình ở [02-slide.md](02-slide.md) |
| Poster | Mẫu của Ban Tổ chức, **A0 (84,1 × 118,9 cm), PDF chất lượng cao, ≤ 100MB** | **`Poster-du-thi.pptx`** (đã trên mẫu) |
| Video | **≤ 5 phút**, thuyết trình nội dung slide, gửi **link Google Drive** | [04-kich-ban-video.md](04-kich-ban-video.md) |
| Chuẩn bị trả lời giám khảo | Vòng chung kết thuyết trình trực tiếp | [06-hoi-dap-giam-khao.md](06-hoi-dap-giam-khao.md) |

Nội dung gốc chung cho cả 3 thành phần nằm ở [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md). Ảnh chụp màn hình và mã QR nằm trong thư mục [anh/](anh/).

## 4. Kiểm tra và nộp (nộp sớm trong ngày 24/10 hoặc sáng Chủ nhật 25/10, không để sát 23h59)

- [ ] Slide: đúng mẫu của Ban Tổ chức, ≤ 15 trang, mở lại được. Nộp file PDF `ban-nop/Slide-du-thi.pdf` do `dien_mau.py` xuất sẵn (đã nhúng phông Aptos của mẫu). Nếu tự xuất từ máy không có phông Aptos (WPS, Office cũ), chữ sẽ bị thay bằng phông khác và có thể tràn dòng.
- [ ] Poster: đúng mẫu, A0, PDF (`ban-nop/Poster-du-thi.pdf`, đã nhúng phông), chữ đọc được khi in (cỡ chữ nội dung ≥ 24pt), các mã QR quét được.
- [ ] Video: ≤ 5:00 (kiểm tra lại độ dài), âm thanh rõ, có phụ đề (khuyến khích).
  - Trên Drive: đặt quyền **"Bất kỳ ai có đường liên kết – Người xem"**.
  - **Không xoá hoặc sửa video sau khi nộp.**
- [ ] Mở link trải nghiệm bằng cửa sổ ẩn danh để chắc giám khảo vào được không cần đăng nhập.
- [ ] Supabase không ở trạng thái tạm dừng. Nếu tạm dừng thì bấm Restore. Mở app một lần cho app "thức".
- [ ] Mọi chỗ `⟦…⟧` đã được thay bằng thông tin thật.
- [ ] Hồ sơ có câu công khai việc sử dụng AI và hỗ trợ kỹ thuật (xem mục "Minh bạch" trong [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md)).
- [ ] Mỗi giáo viên chỉ nộp **một** sản phẩm.

## 5. Tạo mã QR cho link trải nghiệm và link video

Chạy trong thư mục dự án, thay đường dẫn bằng link thật:

```bash
.venv/bin/python -c "import segno; segno.make('https://tro-ly-giang-day.streamlit.app/?demo=MA_DEMO', error='h').save('docs/du-thi/anh/qr-trai-nghiem.png', scale=20, border=2)"
.venv/bin/python -c "import segno; segno.make('LINK_GOOGLE_DRIVE_VIDEO', error='h').save('docs/du-thi/anh/qr-video.png', scale=20, border=2)"
```

Mã QR trang chủ app có sẵn: [anh/qr-app.png](anh/qr-app.png).

## 6. Email mẫu hỏi Ban Tổ chức (gửi ieeai@rmit.edu.vn)

> **Tiêu đề:** Hỏi về quy định tác giả – Giải thưởng Tiên phong Ứng dụng AI trong Giáo dục 2026
>
> Kính gửi Ban Tổ chức,
>
> Tôi là ⟦họ tên⟧, giáo viên ⟦môn/lớp⟧ Trường ⟦tên trường⟧, dự định tham gia Bảng A với sản phẩm là một ứng dụng web hỗ trợ soạn phiếu bài tập phân hóa và đánh giá học sinh tiểu học theo Thông tư 27.
>
> Tôi là người phát hiện vấn đề, đề xuất ý tưởng, xây dựng yêu cầu sư phạm và trực tiếp triển khai sản phẩm trên lớp. Phần lập trình được thực hiện với sự hỗ trợ của công cụ AI lập trình và ⟦một người hỗ trợ kỹ thuật⟧.
>
> Xin Ban Tổ chức cho biết trường hợp này có đáp ứng yêu cầu "sản phẩm do chính tác giả tạo ra" không, và tôi cần trình bày phần hỗ trợ kỹ thuật như thế nào trong hồ sơ cho đúng quy định.
>
> Trân trọng cảm ơn.
> ⟦Họ tên – số điện thoại⟧
