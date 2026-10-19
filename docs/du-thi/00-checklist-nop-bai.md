# Checklist nộp bài – Giải thưởng Tiên phong Ứng dụng AI trong Giáo dục Việt Nam 2026

**Hạn nộp: 23h59 ngày 25/10/2026 (giờ Việt Nam).** Nộp tại <https://apps.rmit.edu.vn/r/nopsanphamGTTP2026>.
Bảng dự thi: **Bảng A** (giáo viên, cán bộ quản lý Mầm non và Tiểu học).
Tác giả: Trần Thị Hiền Minh – giáo viên lớp 4A3 (34 học sinh) – Trường Tiểu học Ngô Quyền, phường Quảng Yên, TP. Quảng Ninh.

Trong toàn bộ hồ sơ, các chỗ đánh dấu `⟦…⟧` cần điền **thông tin hoặc số liệu thật**. Tuyệt đối không ghi số liệu ước đoán như thể là số đo thật. Hiện chưa có số đo thí điểm: trang kết quả đang trình bày **thiết kế đo và mục tiêu**; khi điền `ban-nop/so-lieu.json` sau 23/10, `dien_mau.py` tự chuyển sang số thật.

## 1. Việc cần làm ngay (Thứ Hai 19/10)

- [ ] **Gửi email hỏi Ban Tổ chức về quyền tác giả.** Bản đã điền sẵn nằm ở `ban-nop/email-gui-ban-to-chuc.txt` (gửi ieeai@rmit.edu.vn từ email của giáo viên). Thể lệ ghi: *"Các trường hợp nhờ người khác hỗ trợ hoặc thực hiện thay sẽ không được công nhận."* Cần xác nhận việc giáo viên nhận hỗ trợ lập trình có được chấp nhận hay không.
- [ ] **Thêm `MA_DEMO` vào Secrets của app trên Streamlit Cloud rồi Reboot.** Mã nằm trong `ban-nop/ma-demo.txt` (chạy `.venv/bin/python docs/du-thi/tao_ma_demo.py` để in lại). Mở thử link dùng thử bằng **cửa sổ ẩn danh**. Không ghi mã này vào bất kỳ file nào trên GitHub.
- [x] Tải bộ mẫu PowerPoint và Poster của Ban Tổ chức (đã có trong `docs/`, đã điền vào `Slide-du-thi.pptx` và `Poster-du-thi.pptx`).
- [ ] Xin phép **Ban Giám hiệu** cho thí điểm trong tuần này; gửi **thông báo cho phụ huynh** lớp 4A3. Thông báo cần nói rõ hồ sơ dự thi có hiện họ tên học sinh trong ảnh chụp màn hình phần mềm (xin đồng ý); ảnh, clip trên lớp không để lộ mặt học sinh.
- [ ] In [in-thi-diem.pdf](in-thi-diem.pdf):
  - Trang 1 (bảng ghi chép giáo viên): 1 bản.
  - Trang 2 (khảo sát giáo viên A và D): 1 bản cho mình + 1 bản cho mỗi đồng nghiệp dùng thử (thường 3–4 bản).
  - Trang 3–4 (phiếu mặt cười, 8 phiếu/bộ): **5 bộ = 40 phiếu** cho 34 em, dư vài phiếu dự phòng.
- [ ] Đăng nhập app bằng tài khoản Google của giáo viên dự thi. Kiểm tra lớp 4A3 đã có danh sách và chia nhóm Xanh/Cam/Tím.
- [ ] Xác nhận sản phẩm là **sản phẩm gốc** và **chưa từng đạt giải cấp quốc gia** (đúng điều kiện thể lệ).

## 2. Lịch từng ngày 19–25/10

| Ngày | Việc làm |
|---|---|
| **T2 19/10** | Gửi email Ban Tổ chức; thêm `MA_DEMO` + Reboot + thử ẩn danh; xin phép Ban Giám hiệu, thông báo phụ huynh; in phiếu; giáo viên làm khảo sát **A (trước)**; bấm giờ **B1** soạn phiếu theo cách cũ. |
| **T3 20/10** | Dạy **Bài 14 "So sánh các số có nhiều chữ số"** bằng phiếu nhóm in hoặc giao bài qua QR; bấm giờ chấm và nhận xét **B5** (cách cũ và dùng app). |
| **T4 21/10** | Phân tích lỗi sai → soạn phiếu bổ trợ → dạy bổ trợ → kiểm tra lại, ghi **B8/B9**. Dạy **Bài 15 "Làm quen với dãy số tự nhiên"**. |
| **T5 22/10** | Phát phiếu khảo sát học sinh (C) và đồng nghiệp (D); chụp 3–5 ảnh không lộ mặt; chụp màn hình thống kê ở Trang chủ. |
| **T6 23/10** | Điền `ban-nop/so-lieu.json`; chạy `dien_mau.py` và `long_tieng.py`. |
| **T7 24/10** | Tải video lên Drive; tạo link + QR (mục 5); xuất lại slide, poster; đọc soát PDF (không còn `⟦…⟧`); **nộp bài** và lưu xác nhận nộp. |
| **CN 25/10** | Dự phòng. Không để sát 23h59. |

## 3. Thí điểm và thu số liệu (Thứ Hai 19/10 – Thứ Sáu 23/10)

Làm theo [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md) (Toán 4, Bài 14 và Bài 15). Đầu ra cần có:

- [ ] Bảng số liệu thời gian (soạn phiếu, chấm và nhận xét) trước và sau khi dùng app.
- [ ] Kết quả phiếu bổ trợ: tỉ lệ học sinh chưa đạt, trước và sau khi dạy bổ trợ.
- [ ] Phiếu khảo sát học sinh và giáo viên (ít nhất 2–3 đồng nghiệp dùng thử).
- [ ] Ảnh chụp màn hình thống kê ở Trang chủ (số phiếu, số bài chấm) bằng tài khoản thật.
- [ ] 3–5 ảnh hoặc clip ngắn cảnh dùng trên lớp (không lộ mặt học sinh).

## 4. Hồ sơ nộp

| Thành phần | Yêu cầu của Ban Tổ chức | File nộp |
|---|---|---|
| Slide | Mẫu của Ban Tổ chức, **xuất PDF, ≤ 15 trang, ≤ 100MB** | **`ban-nop/Slide-du-thi.pdf`** (14 trang, `dien_mau.py` xuất sẵn, đã nhúng phông); lời thuyết trình là `LOI_NOI` trong `dien_mau.py` |
| Poster | Mẫu của Ban Tổ chức, **A0 (84,1 × 118,9 cm), PDF chất lượng cao, ≤ 100MB** | **`ban-nop/Poster-du-thi.pdf`** (đã nhúng phông) |
| Video | **≤ 5 phút**, thuyết trình nội dung slide, gửi **link Google Drive** | **`ban-nop/video-long-tieng.mp4`** (khoảng 3:07), xem [04-kich-ban-video.md](04-kich-ban-video.md) |
| Chuẩn bị trả lời giám khảo | Vòng chung kết thuyết trình trực tiếp | [06-hoi-dap-giam-khao.md](06-hoi-dap-giam-khao.md) |

Nội dung gốc chung nằm ở [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md). Ảnh chụp màn hình dùng cho slide và poster được `tao_anh.py` tạo lại trong `ban-nop/` (không đưa lên GitHub).

## 5. Kiểm tra và nộp (nộp trong ngày Thứ Bảy 24/10, Chủ nhật 25/10 để dự phòng)

- [ ] Slide: đúng mẫu của Ban Tổ chức, ≤ 15 trang, mở lại được. Nộp `ban-nop/Slide-du-thi.pdf` do `dien_mau.py` xuất sẵn (đã nhúng phông Aptos của mẫu). Nếu tự xuất từ máy không có phông Aptos (WPS, Office cũ), chữ sẽ bị thay bằng phông khác và có thể tràn dòng.
- [ ] Poster: đúng mẫu, A0, PDF (`ban-nop/Poster-du-thi.pdf`), chữ đọc được khi in, các mã QR quét được.
- [ ] Đọc soát cả 2 file PDF: **không còn chỗ `⟦…⟧`**, đúng tên, lớp, trường.
- [ ] Video: ≤ 5:00, âm thanh rõ, có phụ đề.
  - Tải video lên **Google Drive của chính giáo viên dự thi** (không dùng Drive của người khác).
  - Đặt quyền **"Bất kỳ ai có đường liên kết – Người xem"**, mở thử link bằng cửa sổ ẩn danh.
  - **Sau khi nộp, không xoá, không sửa, không thay file video trên Drive.**
- [ ] Tạo link và mã QR video:

  ```bash
  .venv/bin/python docs/du-thi/tao_ma_demo.py --video <link-drive>   # ghi ban-nop/link-video.txt và ban-nop/qr-video.png
  .venv/bin/python docs/du-thi/dien_mau.py                           # chèn QR vào slide, poster và xuất lại PDF
  ```

  Mọi file sinh ra đều nằm trong `ban-nop/` (không đưa lên GitHub). Không tự tạo mã QR dùng thử vào thư mục `anh/`, vì `anh/` được đưa lên GitHub và sẽ làm lộ mã dùng thử. Mã QR trang chủ app có sẵn: [anh/qr-app.png](anh/qr-app.png).
- [ ] Mở link trải nghiệm bằng cửa sổ ẩn danh để chắc giám khảo vào được không cần đăng nhập.
- [ ] Hồ sơ có câu công khai việc sử dụng AI và hỗ trợ kỹ thuật (xem mục "Minh bạch" trong [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md)).
- [ ] Mỗi giáo viên chỉ nộp **một** sản phẩm.
- [ ] Nộp xong: chụp màn hình hoặc lưu email **xác nhận nộp bài**.

## 6. Giữ app hoạt động đến vòng chung kết

Mỗi tuần một lần (và trước mỗi vòng chấm), cho đến hết vòng chung kết:

- [ ] Mở app để app "thức" (Streamlit Cloud cho app ngủ khi lâu không có người dùng).
- [ ] Vào Supabase kiểm tra dự án **không bị tạm dừng**; nếu tạm dừng thì bấm Restore.
- [ ] Mở link dùng thử bằng cửa sổ ẩn danh.

## 7. Email mẫu hỏi Ban Tổ chức (đã thay bằng bản trong `ban-nop/`)

Mẫu này chỉ để tham khảo. **Bản đã điền đầy đủ để gửi là `ban-nop/email-gui-ban-to-chuc.txt`.**

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
