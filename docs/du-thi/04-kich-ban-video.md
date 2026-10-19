# Kịch bản video thuyết trình (tối đa 5 phút)

Yêu cầu của Ban Tổ chức:
- Video **≤ 5 phút**, thuyết trình nội dung slide.
- Nộp **link Google Drive**, đặt quyền "Bất kỳ ai có đường liên kết – Người xem".
- **Không xoá hoặc sửa video sau khi nộp.**

Video nộp bài là `ban-nop/video-long-tieng.mp4`, dài khoảng **3 phút 07 giây**, còn dư gần 2 phút so với giới hạn.
Video dùng slide 1, 3, 4, 12, 10, 14 của bản slide 14 trang và các đoạn quay màn hình app.

## Video hiện có

`ban-nop/video-long-tieng.mp4` gồm ảnh slide và các đoạn quay màn hình app, lồng tiếng AI, phụ đề khớp lời đọc.

- **Phiếu mẫu là kết quả thật của Gemini**: soạn từ ảnh chụp trang sách Toán 4, Bài 14 "So sánh các số có nhiều chữ số" (trang 48–50). Lượt AI kiểm định cũng là thật và đã phát hiện một lỗi trong hướng dẫn chấm câu 7.
- Đoạn "Soạn phiếu" (0:56–1:13) có nhãn **"Đã rút gọn thời gian chờ AI"**, vì phần chờ AI xử lý đã được cắt ngắn.
- Đoạn "Kết quả" (2:28–2:44) hiện trình bày **thiết kế đo và mục tiêu**, vì chưa có số đo thí điểm. Sau 23/10, điền số liệu thật vào `ban-nop/so-lieu.json` rồi chạy lại `dien_mau.py` và `long_tieng.py`: slide 12 và lời đọc tự chuyển sang số thật.
- Góc video luôn có dòng "Lồng tiếng: giọng đọc AI" để minh bạch.

### Lồng tiếng bằng AI

Thể lệ và trang giải thưởng **không cấm** lồng tiếng bằng AI. Yêu cầu chỉ có: thuyết trình nội dung PowerPoint, ≤ 5 phút, link Google Drive, không sửa sau khi nộp. Nội dung và kịch bản do tác giả xây dựng; vòng chung kết tác giả thuyết trình trực tiếp.

Có hai bộ đọc, chọn ở mục `"may_doc"` trong `ban-nop/so-lieu.json`:

| `may_doc` | Giọng | Ghi chú |
|---|---|---|
| `"edge"` (đang dùng) | Giọng đọc Microsoft (HoaiMy/NamMinh) | Không cần key |
| `"gemini"` (tùy chọn) | Gemini TTS, giọng tự nhiên hơn; chỉnh cách đọc bằng câu mô tả ở `"phong_cach"` | Cần `GEMINI_API_KEY`. Gói miễn phí chỉ **10 lượt/ngày** (video cần 12 đoạn): mỗi đoạn đọc xong được lưu ở `ban-nop/tts-cache/`, hết lượt thì chạy lại hôm sau để đọc tiếp, đoạn cũ không tốn lượt. Đổi giọng ở `"giong_gemini"`: nữ `Sulafat`, `Achernar`, `Vindemiatrix`; nam `Achird`, `Charon`, `Sadaltager` |

1. Điền `ban-nop/so-lieu.json` (số liệu thí điểm). Ô để trống thì lời đọc dùng câu chung, không đọc số.
2. Chạy:
   ```bash
   MAY_DOC=edge .venv/bin/python docs/du-thi/long_tieng.py       # giọng edge
   GEMINI_API_KEY=... .venv/bin/python docs/du-thi/long_tieng.py # giọng Gemini (đặt key trên máy, không đưa lên GitHub)
   ```
   - Có thể thêm dòng `GEMINI_API_KEY = "..."` vào `.streamlit/secrets.toml` (tệp này đã nằm trong `.gitignore`).
   - Phụ đề tự chia theo dấu câu, tối đa 2 dòng × 42 ký tự, không ngắt giữa từ ghép, thời gian khớp nhịp đọc.
3. **Nghe lại toàn bộ** để kiểm tra phát âm (AI, QR, tên riêng, số liệu) và độ dài ≤ 5:00.
4. **Khuyến nghị:** nếu kịp, thêm 10–15 giây giáo viên tự chào ở đầu và cảm ơn ở cuối, bằng giọng thật và có hình. Tiêu chí "Chất lượng trình bày và tính thuyết phục" (15%) đánh giá cả việc giáo viên thuyết phục được Ban Giám khảo.

## Nếu quay lại bằng giọng thật

- **Quay màn hình:** OBS Studio (miễn phí) hoặc tính năng ghi màn hình của PowerPoint. Độ phân giải 1920×1080, trình duyệt Chrome toàn màn hình.
- **Âm thanh:** micro cài áo hoặc tai nghe có mic, phòng yên tĩnh.
- **Dữ liệu trên màn hình:** dùng danh sách lớp 4A3 thật (phụ huynh đã được thông báo và đồng ý). Cảnh lớp học thật cần được nhà trường và phụ huynh đồng ý, và không để lộ mặt học sinh (quay từ phía sau, quay tay đang làm bài, hoặc làm mờ mặt).
- **Phụ đề:** dùng `ban-nop/phu-de-long-tieng.srt` hoặc tạo lại trong CapCut.

## Kịch bản chi tiết (theo bản lồng tiếng hiện tại)

| Thời gian | Hình ảnh | Lời thuyết trình |
|---|---|---|
| **0:00–0:18** Mở đầu | Slide 1 | "Xin chào Ban Giám khảo. Tôi là Trần Thị Hiền Minh, giáo viên lớp 4A3, Trường Tiểu học Ngô Quyền, phường Quảng Yên, thành phố Quảng Ninh. Tôi xin giới thiệu *Trợ Lý Giảng Dạy*, công cụ AI giúp giáo viên tiểu học soạn phiếu bài tập phân hóa và đánh giá học sinh theo Thông tư 27." |
| **0:18–0:40** Bối cảnh | Slide 3 | "Lớp tôi có 34 em, trình độ các em rất khác nhau. Để mỗi em được làm bài vừa sức, tôi phải soạn phiếu ba mức, in cho từng nhóm, chấm và viết nhận xét cho từng em. Việc này tốn rất nhiều thời gian. Thử dùng chatbot AI thì câu trả lời rời rạc, không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra." |
| **0:40–0:56** Giải pháp | Slide 4: sơ đồ vòng khép kín | "Vì vậy, tôi xây dựng một vòng khép kín sáu bước: soạn phiếu, AI kiểm định, dạy và giao bài, chấm và nhận xét, phân tích lỗi để bổ trợ, và theo dõi tiến bộ đến học bạ. Ở mỗi bước, AI đề xuất, còn giáo viên là người quyết định." |
| **0:56–1:13** Soạn phiếu | App: chọn Lớp 4, Toán, tải ảnh trang sách Bài 14 → phiếu 3 mức hiện ra. Nhãn "Đã rút gọn thời gian chờ AI" | "Tôi chọn lớp, môn, nhập tên bài hoặc chụp trang sách giáo khoa. Chỉ khoảng ba mươi giây, AI soạn xong phiếu ba mức theo Thông tư 27, đáp án trình bày đúng như vở của học sinh, kèm ma trận và yêu cầu cần đạt." |
| **1:13–1:24** Kiểm định | Khối "Kiểm định AI" → góp ý câu 7 (lỗi hướng dẫn chấm) | "Điểm khác biệt là một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu để soát đáp án sai và câu lệch mức." *(Khi có số liệu: "Trong thí điểm, nó đã phát hiện ⟦B3⟧ lỗi.")* |
| **1:24–1:35** Phân hóa | Tab In phiếu → Chung / Xanh / Cam / Tím | "Một phiếu tự tách thành ba phiếu Xanh, Cam và Tím cho ba nhóm. Tên màu trung tính, nên các em không cảm thấy mình bị xếp loại." |
| **1:35–2:02** Giao bài | Trang Giao bài → mã QR → học sinh chạm tên, làm bài → bảng theo dõi "x/34 đã nộp" | "Trên lớp, tôi chiếu mã QR. Các em quét bằng máy tính bảng, chạm vào tên mình mà không cần tài khoản, và tự nhận đúng phiếu của nhóm. Câu trắc nghiệm được chấm ngay, còn tôi theo dõi trực tiếp em nào đã nộp bài." |
| **2:02–2:19** Chấm & phân tích lỗi | Sổ tổng hợp → biểu đồ lỗi sai (ví dụ "so sánh từ phải sang trái", "đếm thiếu chữ số") → "Soạn phiếu bổ trợ" | "Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27. Mức đạt được tính theo quy tắc công khai, và tôi có thể sửa từng câu. Biểu đồ cho thấy cả lớp còn yếu ở đâu, và chỉ một nút bấm là có phiếu bổ trợ đúng chỗ đó." |
| **2:19–2:28** Tiến bộ | Trang Tiến bộ: biểu đồ một em | "Kết quả được lưu theo từng em. Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, mà không cần gửi tên học sinh." |
| **2:28–2:44** Kết quả (mục tiêu) | Slide 12 | Hiện tại: "Tôi thí điểm từ ngày 19 đến 23 tháng 10 tại lớp 4A3, so sánh trước và sau trên cùng lớp. Mục tiêu là giảm ít nhất một nửa thời gian soạn phiếu, giảm bốn mươi phần trăm thời gian chấm và nhận xét, và giảm tỉ lệ học sinh chưa đạt sau một buổi bổ trợ." Khi có số liệu: "Sau ⟦…⟧ ngày thí điểm với 34 học sinh, thời gian soạn một phiếu giảm từ ⟦…⟧ xuống ⟦…⟧ phút, …" |
| **2:44–2:59** Trách nhiệm | Slide 10 | "Sản phẩm hoàn toàn miễn phí, chạy trên trình duyệt, dùng được cho khối một đến khối năm, bám sát bộ sách giáo khoa dùng chung toàn quốc. Tên học sinh không được gửi cho AI. Mọi đề, điểm và nhận xét đều do giáo viên duyệt." |
| **2:59–3:07** Kết | Slide 14 + QR dùng thử | "Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em. Xin trân trọng cảm ơn Ban Giám khảo." |

## Sau khi dựng xong

1. Kiểm tra độ dài **≤ 5:00**, xuất MP4 1080p.
2. Tải lên **Google Drive của chính giáo viên dự thi**, đặt quyền "Bất kỳ ai có đường liên kết – Người xem", mở thử bằng cửa sổ ẩn danh.
3. Tạo link và mã QR video (mục 5 của [00-checklist-nop-bai.md](00-checklist-nop-bai.md)), rồi chạy lại `dien_mau.py` để chèn QR vào slide 14 và poster.
4. Sau khi nộp, **không sửa hoặc thay file video trên Drive**.
