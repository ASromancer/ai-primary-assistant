# Poster A0 (84,1 × 118,9 cm, dọc)

> **Bản thiết kế ban đầu – nội dung thực tế nằm trong `dien_mau.py` (slide 14 trang, poster 5 khối).** File nộp là `ban-nop/Poster-du-thi.pdf`; bố cục 6 khối dưới đây chỉ để tham khảo.

Dùng **mẫu Poster của Ban Tổ chức**, xuất **PDF chất lượng cao, ≤ 100MB**. File `poster-nhap.pdf` là bản nháp bố cục, dựng bằng `tao_poster_nhap.py`, để hình dung và copy nội dung. Bố cục chính thức theo mẫu của Ban Tổ chức.

Nguyên tắc:
- Người xem đứng cách 1–2 m vẫn đọc được: tiêu đề ≥ 90pt, đề mục ≥ 48pt, nội dung ≥ 28pt.
- Mỗi khối tối đa khoảng 60 chữ; ảnh và sơ đồ chiếm khoảng 60% diện tích.
- 3 mã QR ở chân poster, mỗi mã ≥ 6 × 6 cm.

## Bố cục đề xuất

```text
┌───────────────────────────────────────────────────────────┐
│  TIÊU ĐỀ + tên tác giả, trường, Bảng A                    │
├──────────────────────────┬────────────────────────────────┤
│ 1. BỐI CẢNH & VẤN ĐỀ     │ 2. GIẢI PHÁP: sơ đồ vòng khép  │
│                          │    kín 6 bước (lớn)            │
├──────────────────────────┴────────────────────────────────┤
│ 3. AI HOẠT ĐỘNG THẾ NÀO – dải 6 ảnh màn hình có chú thích │
├──────────────────────────┬────────────────────────────────┤
│ 4. KẾT QUẢ THỰC TẾ       │ 5. AI CÓ TRÁCH NHIỆM           │
│    (bảng Trước – Sau)    │ 6. BỀN VỮNG & NHÂN RỘNG        │
├──────────────────────────┴────────────────────────────────┤
│  QR dùng thử · QR video · QR trang chủ · công khai dùng AI │
└───────────────────────────────────────────────────────────┘
```

## Nội dung từng khối

**Tiêu đề:** TRỢ LÝ GIẢNG DẠY
**Phụ đề:** Phiếu bài tập phân hóa và đánh giá học sinh tiểu học theo Thông tư 27 bằng AI
**Dòng tác giả:** Trần Thị Hiền Minh · giáo viên lớp 4A3 · Trường Tiểu học Ngô Quyền, phường Quảng Yên, TP. Quảng Ninh · Bảng A

**1. Bối cảnh và vấn đề**
- Lớp 4A3 có 34 học sinh, trình độ chênh lệch rõ.
- TT27 yêu cầu đánh giá thường xuyên bằng nhận xét, bài tập 3 mức.
- Soạn 1 phiếu phân hóa có đáp án mất ⟦…⟧ phút; chấm và nhận xét 1 lớp mất ⟦…⟧ phút.
- Chatbot AI phổ thông trả lời rời rạc, không theo TT27, không tự kiểm tra đáp án.

**2. Giải pháp: vòng khép kín theo TT27**
- Sơ đồ: `anh/so-do-vong-khep-kin.png`
- Chú thích: *AI đề xuất – giáo viên quyết định. Dữ liệu chảy liền mạch từ soạn phiếu đến học bạ.*

**3. AI hoạt động thế nào** (6 ảnh, mỗi ảnh một dòng chú thích)
1. `anh/02-soan-phieu-kiem-dinh.png`: Soạn phiếu 3 mức từ tên bài hoặc ảnh sách giáo khoa.
2. `anh/03-gop-y-kiem-dinh.png`: AI kiểm định tự giải lại từng câu, soát đáp án sai.
3. `anh/31-phieu-xanh.png`: Phiếu Xanh/Cam/Tím, phân hóa không dán nhãn.
4. `anh/21-hs-lam-cau.png`: Học sinh quét QR, chọn tên, làm bài trên điện thoại.
5. `anh/10-phan-tich-loi-sai.png`: Phân tích lỗi, sinh phiếu bổ trợ.
6. `anh/12-tien-bo-bieu-do.png`: Theo dõi tiến bộ, gợi ý nhận xét học bạ.

**4. Kết quả thực tế** (chỉ số liệu thật, lấy từ mục 3 của [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md); trước khi có số đo thì trình bày thiết kế đo và mục tiêu)
- Soạn phiếu: ⟦…⟧ → ⟦…⟧ phút
- Chấm và nhận xét 1 lớp: ⟦…⟧ → ⟦…⟧ phút
- Sau bổ trợ: chưa đạt ⟦…%⟧ → ⟦…%⟧
- ⟦…%⟧ học sinh thích làm bài trên phiếu hoặc app
- "⟦Trích phản hồi giáo viên⟧"

**5. AI có trách nhiệm**
- Giáo viên duyệt mọi đề, đáp án, điểm và nhận xét.
- AI kiểm định 2 lượt; mức TT27 tính bằng quy tắc công khai.
- Không gửi tên học sinh cho AI; học sinh không cần tài khoản.

**6. Bền vững và nhân rộng**
- 0 đồng; chạy trên trình duyệt; điện thoại dùng được.
- Khối 1–5, 8 môn, bộ sách Kết nối tri thức với cuộc sống (dùng thống nhất toàn quốc từ 2026–2027).
- Mỗi giáo viên có dữ liệu riêng, nhiều giáo viên dùng song song.

**Chân poster:**
- QR **Dùng thử** (`ban-nop/qr-trai-nghiem.png`, không đưa lên GitHub)
- QR **Video** (`ban-nop/qr-video.png`, tạo theo mục 5 của checklist)
- QR **Trang chủ** (`anh/qr-app.png`)
- Dòng nhỏ: *Phần lập trình có sự hỗ trợ của công cụ AI Claude Code ⟦và …⟧.*
