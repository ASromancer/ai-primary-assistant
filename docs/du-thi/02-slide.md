# Slide thuyết trình (xuất PDF)

> **Bản thiết kế ban đầu – nội dung thực tế nằm trong `dien_mau.py` (slide 14 trang, poster 5 khối).** Lời thuyết trình từng trang là `LOI_NOI` trong `dien_mau.py`; file nộp là `ban-nop/Slide-du-thi.pdf`. Thứ tự và số trang dưới đây có thể khác bản thực tế.

Dùng **mẫu PowerPoint của Ban Tổ chức**. File `slide-nhap.pptx` trong thư mục này là bản nháp đã sắp sẵn chữ và ảnh: copy từng trang sang mẫu chính thức rồi chỉnh màu, phông theo mẫu. Ảnh ở thư mục [anh/](anh/).

Nguyên tắc trình bày:
- Mỗi trang một ý chính, tối đa 5 dòng chữ, chữ ≥ 20pt.
- Ảnh chiếm phần lớn diện tích.
- Mục "Lời nói" là gợi ý thuyết trình, dùng cho video và vòng chung kết.

---

### Trang 1 – Bìa
- **TRỢ LÝ GIẢNG DẠY**
- Phiếu bài tập phân hóa và đánh giá học sinh tiểu học theo Thông tư 27 bằng AI
- Trần Thị Hiền Minh – giáo viên lớp 4A3 – Trường Tiểu học Ngô Quyền, phường Quảng Yên, TP. Quảng Ninh
- Bảng A · Chủ đề: Giảng dạy, học tập và đánh giá
- Ảnh: `anh/01-trang-chu.png` (mờ làm nền) + `anh/qr-app.png`

### Trang 2 – Bối cảnh
- Lớp 4A3: 34 học sinh, trình độ chênh lệch rõ.
- TT27: đánh giá thường xuyên bằng nhận xét; bài tập 3 mức.
- Phân hóa là cần thiết nhưng **tốn thời gian**: soạn 3 mức, đáp án, in theo nhóm, chấm, nhận xét.
- Số liệu: soạn 1 phiếu ≈ ⟦…⟧ phút; chấm và nhận xét 1 lớp ≈ ⟦…⟧ phút.

**Lời nói:** "Lớp tôi có 34 em, có em làm xong bài trong 5 phút, có em cần cả tiết. Muốn mỗi em được làm bài vừa sức, tôi phải soạn 3 mức, in theo nhóm, chấm và nhận xét từng em. Mỗi phiếu mất khoảng ⟦…⟧ phút…"

### Trang 3 – Vấn đề và nguyên nhân
1. Soạn đề 3 mức đúng chuẩn TT27 tốn thời gian, chất lượng không đều.
2. Chatbot AI phổ thông: không theo mẫu TT27, không tự kiểm tra đáp án, không nối với chấm bài và theo dõi tiến bộ.
3. Kết quả chấm nằm trên giấy, khó phân tích để dạy bù kịp thời.
- **Câu hỏi đặt ra:** làm sao để AI giúp giáo viên đi hết vòng *soạn → dạy → đánh giá → bổ trợ* mà giáo viên vẫn làm chủ?

### Trang 4 – Giải pháp: vòng khép kín 6 bước
- Sơ đồ vòng tròn: ① Soạn phiếu 3 mức → ② AI kiểm định → ③ Dạy và giao bài → ④ Chấm và nhận xét TT27 → ⑤ Phân tích lỗi và phiếu bổ trợ → ⑥ Tiến bộ và học bạ.
- Dòng chân trang: *AI đề xuất – giáo viên quyết định.*

### Trang 5 – AI được dùng như thế nào
Bảng 3 cột: Bước | AI làm gì | Giáo viên làm gì. Lấy từ bảng ở mục 2 của [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md), rút gọn mỗi ô còn 1 dòng.
- Công cụ: Google Gemini (đọc ảnh sách giáo khoa và ảnh bài làm viết tay, tạo nội dung có cấu trúc) · Streamlit · Supabase · đăng nhập Google.
- **Chi phí: 0 đồng.**

### Trang 6 – ① Soạn phiếu từ tên bài hoặc ảnh sách giáo khoa
- Chọn lớp, môn, thời lượng (bộ sách Kết nối tri thức với cuộc sống); hoặc **chụp trang sách giáo khoa**.
- Phiếu 3 mức kèm đáp án, hướng dẫn chấm, ma trận, yêu cầu cần đạt.
- Đáp án theo chuẩn tiểu học: Bài giải – lời giải – phép tính (đơn vị) – Đáp số.
- Ảnh: `anh/02-soan-phieu-kiem-dinh.png`

### Trang 7 – ② AI kiểm định: tổ trưởng chuyên môn ảo
- Lượt AI thứ hai **tự giải lại từng câu**, soát đáp án sai, câu lệch mức, từ ngữ chưa phù hợp.
- Điểm chất lượng 0–100; góp ý từng câu; nút "Sửa theo góp ý".
- Số liệu thí điểm: phát hiện ⟦…⟧ lỗi / ⟦…⟧ phiếu.
- Ảnh: `anh/03-gop-y-kiem-dinh.png`

### Trang 8 – ③ Phân hóa không dán nhãn
- 1 phiếu tự tách thành **Phiếu Xanh / Cam / Tím**: tên màu trung tính, học sinh không biết mình ở "mức" nào.
- Đề A/B chống nhìn bài; phiếu in sẵn tên từng em.
- In ngay A4 hoặc tải Word.
- Ảnh: `anh/31-phieu-xanh.png` + `anh/13-lop-cua-toi-phieu-theo-ten.png`

### Trang 9 – ③ Lớp học số: trình chiếu và giao bài bằng QR
- Trình chiếu từng câu kiểu trò chơi: đếm giờ, lật đáp án, gọi tên ngẫu nhiên, đọc to câu hỏi.
- Giao bài online: chiếu mã QR, học sinh **chạm vào tên mình**, không cần tài khoản; mỗi em tự nhận phiếu đúng nhóm.
- Ảnh: `anh/05-lop-hoc-trinh-chieu.png` + `anh/20-hs-chon-ten.png` + `anh/21-hs-lam-cau.png`

### Trang 10 – ④ Chấm và nhận xét theo TT27
- Chấm từ **ảnh chụp bài viết tay** hoặc bài làm online; trắc nghiệm, đúng/sai, nối cột chấm ngay.
- Nhận xét theo TT27; mức đạt tính bằng quy tắc công khai:
  - Chưa hoàn thành: Mức 1 đúng dưới 50%.
  - Hoàn thành tốt: Mức 1 và Mức 2 đúng từ 80% trở lên, Mức 3 đúng từ 50% trở lên.
  - Hoàn thành: các trường hợp còn lại.
- Giáo viên chấm tay hoặc sửa mọi kết quả.
- Ảnh: `anh/09-cham-bai-so-tong-hop.png`

### Trang 11 – ⑤ Phân tích lỗi và phiếu bổ trợ
- Biểu đồ tỉ lệ chưa đạt từng câu (ngưỡng 40%) và lỗi thường gặp (ví dụ Bài 14: "so sánh từ phải sang trái", "đếm thiếu chữ số"…).
- 1 nút: AI soạn **phiếu bổ trợ** đúng chỗ hổng kiến thức.
- Ảnh: `anh/10-phan-tich-loi-sai.png`

### Trang 12 – ⑥ Theo dõi tiến bộ và nhận xét học bạ
- Bảng mức TT27 từng em qua các lần đánh giá; biểu đồ tiến bộ từng em.
- AI gợi ý nhận xét cuối kỳ (không gửi tên học sinh); giáo viên duyệt và xuất Excel.
- Ảnh: `anh/12-tien-bo-bieu-do.png`

### Trang 13 – Triển khai và kết quả thực tế
- Phạm vi: lớp 4A3, 34 học sinh, 5 ngày (19–23/10/2026), Toán 4 Bài 14–15, ⟦…⟧ đồng nghiệp dùng thử.
- Chưa có số đo: trang này trình bày thiết kế đo và mục tiêu; sau khi điền `ban-nop/so-lieu.json`, `dien_mau.py` tự thay bằng số thật.
- Bảng "Trước – Sau" (mục 3 của [01-noi-dung-ho-so.md](01-noi-dung-ho-so.md)), **chỉ số liệu thật**.
- 1–2 trích dẫn phản hồi của giáo viên và học sinh.
- Ảnh lớp học thật (che mặt học sinh) + ảnh thống kê Trang chủ bằng tài khoản thật.

### Trang 14 – AI có trách nhiệm · Bền vững và nhân rộng
- **Trách nhiệm:**
  - AI đề xuất, giáo viên quyết định.
  - Kiểm định 2 lượt.
  - Không gửi tên học sinh cho AI.
  - Học sinh không cần tài khoản.
  - Dữ liệu từng giáo viên tách riêng.
- **Bền vững:**
  - 0 đồng.
  - Chạy trên trình duyệt.
  - Khối 1–5, 8 môn, SGK dùng chung toàn quốc.
  - Nhiều giáo viên dùng song song.
  - Có hướng dẫn chuyển giao.
- **Giới hạn và hướng phát triển:** quota gói miễn phí; chia sẻ phiếu trong tổ chuyên môn; tin nhắn phụ huynh.

### Trang 15 – Kết luận và dùng thử
- Thông điệp: *"Để mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em."*
- QR: dùng thử (link giám khảo) · video · trang chủ.
- Công khai: phần lập trình có sự hỗ trợ của công cụ AI Claude Code ⟦và …⟧.
- Cảm ơn.
