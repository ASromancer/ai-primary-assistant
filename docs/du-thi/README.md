# Hồ sơ dự thi – Giải thưởng Tiên phong Ứng dụng AI trong Giáo dục Việt Nam 2026

Hạn nộp: **23h59 ngày 25/10/2026**. Bắt đầu từ checklist.

| File | Nội dung |
|---|---|
| [00-checklist-nop-bai.md](00-checklist-nop-bai.md) | Lịch làm việc, yêu cầu kỹ thuật, kiểm tra trước khi nộp, email hỏi Ban Tổ chức về quyền tác giả |
| [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md) | Nội dung gốc cho cả slide, poster, video (theo 5 phần thể lệ và tiêu chí chấm) |
| **`Slide-du-thi.pptx`** | **Slide 14 trang trên MẪU của Ban Tổ chức**, đã điền nội dung và ảnh: chỉ còn điền `⟦…⟧`, thay ảnh giáo viên, xuất PDF |
| **`Poster-du-thi.pptx`** | **Poster A0 trên MẪU của Ban Tổ chức**, đã dàn nội dung và ảnh trong vùng quy định |
| [02-slide.md](02-slide.md) · `slide-nhap.pptx` | Lời thuyết trình từng trang (bản nháp cũ, chỉ để tham khảo) |
| [03-poster-A0.md](03-poster-A0.md) · `poster-nhap.pdf` | Ghi chú bố cục poster (bản nháp cũ, chỉ để tham khảo) |
| [04-kich-ban-video.md](04-kich-ban-video.md) | Kịch bản video ≤ 5 phút có bấm giờ, hướng dẫn quay |
| [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md) | Kế hoạch thí điểm 18–23/10, bảng ghi số liệu, phiếu khảo sát giáo viên và học sinh |
| [06-hoi-dap-giam-khao.md](06-hoi-dap-giam-khao.md) | 14 câu hỏi giám khảo hay hỏi và gợi ý trả lời |
| [anh/](anh/) | Ảnh chụp màn hình (dữ liệu và tên học sinh giả), ảnh phiếu in, sơ đồ vòng khép kín, mã QR |

Chỗ `⟦…⟧` trong mọi file là thông tin hoặc số liệu **thật** cần điền.

## Hoàn thiện slide và poster

Có 2 cách:

1. **Sửa trực tiếp** `Slide-du-thi.pptx` và `Poster-du-thi.pptx` bằng PowerPoint.
   - Thay các chỗ `⟦…⟧`.
   - Trang bìa: bấm vào khung "⟦Ảnh giáo viên⟧", xoá đi rồi chèn ảnh chân dung của giáo viên.
   - Chèn mã QR video và mã QR dùng thử vào các khung "⟦tạo QR⟧".
   - Xuất **PDF**: File → Export → PDF. Slide ≤ 15 trang; poster khổ A0.
2. **Sửa nội dung trong script** `dien_mau.py` (các hằng `TEN_GV`, `DON_VI`, `BOI_CANH`, `KET_QUA`…), đặt ảnh `anh/qr-trai-nghiem.png` và `anh/qr-video.png`, rồi chạy lại:

   ```bash
   .venv/bin/pip install python-pptx            # một lần
   .venv/bin/python docs/du-thi/dien_mau.py     # dựng lại Slide-du-thi.pptx và Poster-du-thi.pptx từ mẫu gốc
   ```

   Chạy lại script sẽ ghi đè 2 file trên. Nếu đã sửa tay trong PowerPoint thì đừng chạy lại.

Mẫu gốc của Ban Tổ chức nằm ở `docs/Mẫu Slide 2026.pptx` và `docs/Mẫu Poster 2026.pptx`. Có thể làm trên Canva bằng link trong 2 file `docs/Mẫu … - Link Canva.docx`.
