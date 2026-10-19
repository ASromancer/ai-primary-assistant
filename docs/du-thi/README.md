# Hồ sơ dự thi – Giải thưởng Tiên phong Ứng dụng AI trong Giáo dục Việt Nam 2026

Hạn nộp: **23h59 ngày 25/10/2026**. Bắt đầu từ checklist.

| File | Nội dung |
|---|---|
| [00-checklist-nop-bai.md](00-checklist-nop-bai.md) | Lịch làm việc, yêu cầu kỹ thuật, kiểm tra trước khi nộp, email hỏi Ban Tổ chức về quyền tác giả |
| [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md) | Nội dung gốc cho cả slide, poster, video (theo 5 phần thể lệ và tiêu chí chấm) |
| **`ban-nop/`** (chỉ có trên máy, không đưa lên GitHub) | **File nộp bài**, xem bảng bên dưới |
| [in-thi-diem.pdf](in-thi-diem.pdf) | **In ngay cho đợt thí điểm:** bảng ghi chép giáo viên, phiếu khảo sát giáo viên, 8 phiếu mặt cười cho học sinh |
| [02-slide.md](02-slide.md) · `slide-nhap.pptx` | Lời thuyết trình từng trang (bản nháp cũ, chỉ để tham khảo) |
| [03-poster-A0.md](03-poster-A0.md) · `poster-nhap.pdf` | Ghi chú bố cục poster (bản nháp cũ, chỉ để tham khảo) |
| [04-kich-ban-video.md](04-kich-ban-video.md) | Kịch bản video (bản lồng tiếng khoảng 3:07) có bấm giờ, hướng dẫn quay |
| [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md) | Kế hoạch thí điểm 19–23/10 (Toán 4 Bài 14–15), bảng ghi số liệu, phiếu khảo sát giáo viên và học sinh |
| [06-hoi-dap-giam-khao.md](06-hoi-dap-giam-khao.md) | Các câu hỏi giám khảo hay hỏi và gợi ý trả lời |
| [anh/](anh/) | Ảnh chụp màn hình cũ (dữ liệu và tên học sinh giả), ảnh phiếu in, sơ đồ vòng khép kín, mã QR trang chủ. Ảnh dùng cho slide và poster hiện nay được chụp lại bằng `tao_anh.py` vào `ban-nop/` |

Chỗ `⟦…⟧` trong mọi file là thông tin hoặc số liệu **thật** cần điền.

## Thư mục `ban-nop/`

Thư mục này không đưa lên GitHub vì repo công khai: trong đó có mã dùng thử, thông tin liên hệ và ảnh có tên học sinh thật.

| File | Nội dung |
|---|---|
| **`Slide-du-thi.pdf`** · `Slide-du-thi.pptx` | Slide 14 trang trên **mẫu của Ban Tổ chức**. Bản PPTX có **lời thuyết trình trong phần ghi chú** từng trang (lấy từ `LOI_NOI` trong `dien_mau.py`). **Nộp bản PDF** (đã nhúng phông) |
| **`Poster-du-thi.pdf`** · `Poster-du-thi.pptx` | Poster A0 trên **mẫu của Ban Tổ chức**, 5 khối nội dung. **Nộp bản PDF** (đã nhúng phông) |
| `*.png` (ảnh màn hình) | Ảnh chụp app bằng dữ liệu lớp thật, do `tao_anh.py` tạo; `dien_mau.py` ưu tiên dùng ảnh ở đây hơn ảnh trong `anh/` |
| `email-gui-ban-to-chuc.txt` | Email hỏi Ban Tổ chức về quyền tác giả, đã điền sẵn thông tin |
| `link-video.txt`, `qr-video.png` | Link Google Drive của video và mã QR, tạo bằng `tao_ma_demo.py --video <link>` |
| `ma-demo.txt`, `qr-trai-nghiem.png` | Mã dùng thử cho giám khảo và mã QR. **Phải thêm `MA_DEMO = "<mã>"` vào Secrets của app** rồi Reboot |
| `video-nhap.mp4` | Video nháp cũ (ảnh slide + quay màn hình app + phụ đề), chưa có tiếng |
| **`video-long-tieng.mp4`** | **Video nộp bài, khoảng 3:07**, lồng tiếng AI (hiện dùng giọng edge; có thể đổi sang Gemini TTS), phụ đề khớp lời đọc, nhãn "Lồng tiếng: giọng đọc AI". Dùng slide 1, 3, 4, 12, 10, 14 và các đoạn quay app |
| `so-lieu.json` | Thông tin giáo viên và số liệu thí điểm. Hiện chưa có số đo; sau 23/10 điền số liệu thật rồi chạy lại `dien_mau.py` và `long_tieng.py`, trang kết quả tự chuyển từ "thiết kế đo và mục tiêu" sang số thật |
| `loi-doc.mp3`, `phu-de-long-tieng.srt` | Riêng phần tiếng và phụ đề, để dựng lại trong CapCut |
| `phu-de.srt` | Phụ đề theo kịch bản, nhập vào CapCut khi dựng video thật |
| `doan-quay/` | 12 đoạn video sạch (không phụ đề), mỗi đoạn ứng với một mốc trong kịch bản |

Dựng lại khi cần:

```bash
.venv/bin/python docs/du-thi/tao_ma_demo.py                       # tạo/in lại mã dùng thử + QR
.venv/bin/python docs/du-thi/tao_ma_demo.py --video <link-drive>  # thêm QR video sau khi tải video lên Drive
.venv/bin/python docs/du-thi/tao_anh.py                           # chụp lại ảnh màn hình app vào ban-nop/
.venv/bin/python docs/du-thi/dien_mau.py                          # dựng lại slide, poster và xuất PDF (ghi đè ban-nop/)
.venv/bin/python docs/du-thi/tao_video_nhap.py                    # quay lại các đoạn video nháp
.venv/bin/python docs/du-thi/long_tieng.py                        # lồng tiếng AI theo so-lieu.json (cần mạng; MAY_DOC=edge để dùng giọng edge)
.venv/bin/python docs/du-thi/tao_phieu_khao_sat.py                # in lại bộ phiếu thí điểm
```

## Hoàn thiện slide và poster

Có 2 cách:

1. **Sửa trực tiếp** `ban-nop/Slide-du-thi.pptx` và `ban-nop/Poster-du-thi.pptx` bằng PowerPoint.
   - Thay các chỗ `⟦…⟧`.
   - Trang bìa: đặt ảnh chân dung vuông (đã cắt) ở `ban-nop/chan-dung.jpg`, chạy lại `dien_mau.py` để tự cắt tròn và chèn.
   - Mã QR dùng thử đã có sẵn. Sau khi có link video, chạy `tao_ma_demo.py --video <link>` và `dien_mau.py`, hoặc tự chèn ảnh QR vào khung "⟦tạo QR⟧".
   - Xuất **PDF**: File → Export → PDF. Slide ≤ 15 trang; poster khổ A0. Lưu ý máy không có phông Aptos sẽ thay phông khác, chữ có thể tràn dòng.
2. **Sửa nội dung trong script** `dien_mau.py` (các hằng `TEN_GV`, `DON_VI`, `BOI_CANH`, `KET_QUA`, `LOI_NOI`…), rồi chạy lại:

   ```bash
   .venv/bin/pip install python-pptx            # một lần
   .venv/bin/python docs/du-thi/dien_mau.py     # dựng lại Slide-du-thi.pptx/.pdf và Poster-du-thi.pptx/.pdf từ mẫu gốc
   ```

   Script tự xuất PDF có nhúng phông (cần LibreOffice). Đây là cách đang dùng: **nộp `Slide-du-thi.pdf` và `Poster-du-thi.pdf`**. Chạy lại script sẽ ghi đè các file trên; nếu đã sửa tay trong PowerPoint thì đừng chạy lại.

Mẫu gốc của Ban Tổ chức nằm ở `docs/Mẫu Slide 2026.pptx` và `docs/Mẫu Poster 2026.pptx`. Có thể làm trên Canva bằng link trong 2 file `docs/Mẫu … - Link Canva.docx`.
