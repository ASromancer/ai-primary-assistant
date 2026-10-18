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
| [04-kich-ban-video.md](04-kich-ban-video.md) | Kịch bản video ≤ 5 phút có bấm giờ, hướng dẫn quay |
| [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md) | Kế hoạch thí điểm 18–23/10, bảng ghi số liệu, phiếu khảo sát giáo viên và học sinh |
| [06-hoi-dap-giam-khao.md](06-hoi-dap-giam-khao.md) | 14 câu hỏi giám khảo hay hỏi và gợi ý trả lời |
| [anh/](anh/) | Ảnh chụp màn hình (dữ liệu và tên học sinh giả), ảnh phiếu in, sơ đồ vòng khép kín, mã QR |

Chỗ `⟦…⟧` trong mọi file là thông tin hoặc số liệu **thật** cần điền.

## Thư mục `ban-nop/`

Thư mục này không đưa lên GitHub vì repo công khai và trong đó có mã dùng thử.

| File | Nội dung |
|---|---|
| `Slide-du-thi.pptx` | Slide 14 trang trên **mẫu của Ban Tổ chức**, có **lời thuyết trình trong phần ghi chú** từng trang |
| `Poster-du-thi.pptx` | Poster A0 trên **mẫu của Ban Tổ chức** |
| `ma-demo.txt`, `qr-trai-nghiem.png` | Mã dùng thử cho giám khảo và mã QR. **Phải thêm `MA_DEMO = "<mã>"` vào Secrets của app** rồi Reboot |
| `video-nhap.mp4` | **Video nháp 4:50** (ảnh slide + quay màn hình app + phụ đề) để làm khung, **không nộp nguyên bản** |
| `phu-de.srt` | Phụ đề theo kịch bản, nhập vào CapCut khi dựng video thật |
| `doan-quay/` | 12 đoạn video sạch (không phụ đề), mỗi đoạn ứng với một mốc trong kịch bản |

Dựng lại khi cần:

```bash
.venv/bin/python docs/du-thi/tao_ma_demo.py                       # tạo/in lại mã dùng thử + QR
.venv/bin/python docs/du-thi/tao_ma_demo.py --video <link-drive>  # thêm QR video sau khi tải video lên Drive
.venv/bin/python docs/du-thi/dien_mau.py                          # dựng lại slide và poster (ghi đè ban-nop/)
.venv/bin/python docs/du-thi/tao_video_nhap.py                    # quay lại video nháp (khoảng 5 phút)
.venv/bin/python docs/du-thi/tao_phieu_khao_sat.py                # in lại bộ phiếu thí điểm
```

## Hoàn thiện slide và poster

Có 2 cách:

1. **Sửa trực tiếp** `ban-nop/Slide-du-thi.pptx` và `ban-nop/Poster-du-thi.pptx` bằng PowerPoint.
   - Thay các chỗ `⟦…⟧`.
   - Trang bìa: bấm vào khung "⟦Ảnh giáo viên⟧", xoá đi rồi chèn ảnh chân dung của giáo viên.
   - Mã QR dùng thử đã có sẵn. Sau khi có link video, chạy `tao_ma_demo.py --video <link>` và `dien_mau.py`, hoặc tự chèn ảnh QR vào khung "⟦tạo QR⟧".
   - Xuất **PDF**: File → Export → PDF. Slide ≤ 15 trang; poster khổ A0.
2. **Sửa nội dung trong script** `dien_mau.py` (các hằng `TEN_GV`, `DON_VI`, `BOI_CANH`, `KET_QUA`, `LOI_NOI`…), rồi chạy lại:

   ```bash
   .venv/bin/pip install python-pptx            # một lần
   .venv/bin/python docs/du-thi/dien_mau.py     # dựng lại ban-nop/Slide-du-thi.pptx và Poster-du-thi.pptx từ mẫu gốc
   ```

   Chạy lại script sẽ ghi đè 2 file trên. Nếu đã sửa tay trong PowerPoint thì đừng chạy lại.

Mẫu gốc của Ban Tổ chức nằm ở `docs/Mẫu Slide 2026.pptx` và `docs/Mẫu Poster 2026.pptx`. Có thể làm trên Canva bằng link trong 2 file `docs/Mẫu … - Link Canva.docx`.
