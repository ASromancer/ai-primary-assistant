# Kịch bản video thuyết trình (tối đa 5 phút)

Yêu cầu của Ban Tổ chức:
- Video **≤ 5 phút**, thuyết trình nội dung slide.
- Nộp **link Google Drive**, đặt quyền "Bất kỳ ai có đường liên kết – Người xem".
- **Không xoá hoặc sửa video sau khi nộp.**

Kịch bản dưới đây dài khoảng **4 phút 45 giây** (đọc chậm khoảng 130 chữ/phút), còn dư 15 giây an toàn.
Người dẫn là **giáo viên đứng tên dự thi**: vừa thể hiện quyền tác giả, vừa ghi điểm tính thuyết phục (15%).

## Video nháp có sẵn

`ban-nop/video-nhap.mp4` (4 phút 50 giây) đã ghép đúng trình tự kịch bản: ảnh slide và các đoạn quay màn hình app (dữ liệu, tên học sinh giả), kèm phụ đề là lời thuyết trình. Cách dùng nhanh nhất:

1. Mở CapCut và nhập `video-nhap.mp4`, hoặc nhập 12 đoạn sạch trong `ban-nop/doan-quay/` cùng phụ đề `phu-de.srt`.
2. Giáo viên **thu giọng đọc** theo phụ đề, đặt đè lên video, rồi xoá phụ đề cũ và tạo lại phụ đề theo giọng thật.
3. **Thay đoạn "Kết quả"** (3:44–4:17) bằng số liệu thật và cảnh lớp học thật (không lộ mặt học sinh). Thay các chỗ `⟦…⟧`.
4. **Quay lại đoạn "Soạn phiếu"** (1:14–1:44) bằng app thật có AI. Trong video nháp, đoạn này dùng AI giả lập trả phiếu mẫu và có ghi "minh họa".
5. Thêm khung hình giáo viên ở đoạn mở đầu và kết (webcam).

### Phương án lồng tiếng bằng AI (`ban-nop/video-long-tieng.mp4`)

Thể lệ và trang giải thưởng **không cấm** lồng tiếng bằng AI. Yêu cầu chỉ có: thuyết trình nội dung PowerPoint, ≤ 5 phút, link Google Drive, không sửa sau khi nộp. Video luôn hiện dòng "Lồng tiếng: giọng đọc AI" để minh bạch.

Có hai bộ đọc, chọn ở mục `"may_doc"` trong `ban-nop/so-lieu.json`:

| `may_doc` | Giọng | Ghi chú |
|---|---|---|
| `"gemini"` (mặc định) | Gemini TTS, giọng tự nhiên như người thật; chỉnh cách đọc bằng câu mô tả ở `"phong_cach"` | Cần `GEMINI_API_KEY`. Gói miễn phí chỉ **10 lượt/ngày** (video cần 12 đoạn): mỗi đoạn đọc xong được lưu ở `ban-nop/tts-cache/`, hết lượt thì chạy lại sau 7 giờ sáng hôm sau để đọc tiếp, đoạn cũ không tốn lượt. Đổi giọng ở `"giong_gemini"`: nữ `Sulafat`, `Achernar`, `Vindemiatrix`; nam `Achird`, `Charon`, `Sadaltager` |
| `"edge"` | Giọng đọc Microsoft (HoaiMy/NamMinh), nghe "máy" hơn | Không cần key. Tự dùng khi máy chưa có key Gemini |

1. Điền `ban-nop/so-lieu.json` (họ tên, lớp, trường, sĩ số, số liệu thí điểm). Ô để trống thì lời đọc dùng câu chung, không đọc số.
2. Đặt key Gemini **trên máy** (không gửi qua chat, không đưa lên GitHub), rồi chạy:
   ```bash
   GEMINI_API_KEY=... .venv/bin/python docs/du-thi/long_tieng.py
   ```
   Hoặc thêm dòng `GEMINI_API_KEY = "..."` vào `.streamlit/secrets.toml` (tệp này đã nằm trong `.gitignore`).
   - Muốn dựng nhanh bản xem thử bằng giọng edge (không tốn lượt Gemini): `MAY_DOC=edge .venv/bin/python docs/du-thi/long_tieng.py`.
   - Phụ đề tự chia theo dấu câu, tối đa 2 dòng × 42 ký tự, không ngắt giữa từ ghép ("học sinh", "Thông tư 27"…), thời gian khớp nhịp đọc.
   - Đoạn slide dài vừa lời đọc. Đoạn quay app được tua nhanh tối đa 1,8 lần cho khớp lời, không còn khoảng lặng dài.
3. **Nghe lại toàn bộ** để kiểm tra phát âm (AI, QR, tên riêng, số liệu).
4. **Trước khi nộp vẫn phải:**
   - Quay lại đoạn "Soạn phiếu" bằng AI thật. Đoạn này đang có nhãn "Minh họa giao diện".
   - Thay slide kết quả bằng bản có số liệu thật. Đoạn này đang có nhãn "Chờ số liệu thí điểm thật".
5. **Khuyến nghị:** thêm 10–15 giây giáo viên tự chào ở đầu và cảm ơn ở cuối, bằng giọng thật và có hình. Tiêu chí "Chất lượng trình bày và tính thuyết phục" (15%) đánh giá cả việc giáo viên thuyết phục được Ban Giám khảo, và vòng chung kết là thuyết trình trực tiếp.

## Chuẩn bị quay

- **Quay màn hình:** OBS Studio (miễn phí) hoặc tính năng ghi màn hình của PowerPoint. Độ phân giải 1920×1080, trình duyệt Chrome toàn màn hình, phóng to trang 125%.
- **Khung hình giáo viên:** góc dưới phải (webcam), hoặc quay riêng phần mở đầu và kết.
- **Âm thanh:** micro cài áo hoặc tai nghe có mic, phòng yên tĩnh.
- **Dữ liệu demo:**
  - Dùng tài khoản thật, nhưng tên học sinh hiển thị trên màn hình phải là tên giả (tạo lớp "Lớp demo").
  - Cảnh lớp học thật cần được phụ huynh và nhà trường đồng ý, và không để lộ mặt học sinh (quay từ phía sau, quay tay đang làm bài, hoặc làm mờ mặt).
- **Phụ đề:** thêm phụ đề tiếng Việt (CapCut hoặc YouTube Studio tạo tự động rồi sửa) để giám khảo xem không cần âm thanh.
- **Kiểm tra lần cuối:** độ dài ≤ 5:00; xuất MP4 1080p.

## Kịch bản chi tiết

| Thời gian | Hình ảnh | Lời thuyết trình |
|---|---|---|
| **0:00–0:20** Mở đầu | Giáo viên trước lớp học (không lộ mặt học sinh) → slide 1 | "Xin chào Ban Giám khảo. Tôi là ⟦họ tên⟧, giáo viên lớp ⟦…⟧ Trường ⟦…⟧. Tôi xin giới thiệu *Trợ Lý Giảng Dạy*, công cụ AI giúp giáo viên tiểu học soạn phiếu phân hóa và đánh giá học sinh theo Thông tư 27." |
| **0:20–0:55** Bối cảnh, vấn đề | Slide 2–3; ảnh chồng phiếu, vở chấm | "Lớp tôi có ⟦…⟧ em với trình độ rất khác nhau. Để mỗi em làm bài vừa sức, tôi phải soạn phiếu ba mức, in cho từng nhóm, chấm và viết nhận xét từng em. Một phiếu như vậy mất khoảng ⟦…⟧ phút, chấm cả lớp mất ⟦…⟧ phút. Thử dùng chatbot AI thì câu trả lời rời rạc, không theo mẫu Thông tư 27, và đáp án đôi khi sai mà không ai kiểm tra." |
| **0:55–1:20** Giải pháp | Slide 4: sơ đồ vòng khép kín | "Vì vậy tôi xây dựng một vòng khép kín 6 bước: soạn phiếu, AI kiểm định, dạy và giao bài, chấm và nhận xét, phân tích lỗi để bổ trợ, và theo dõi tiến bộ đến học bạ. Ở mỗi bước, AI đề xuất, còn giáo viên là người quyết định." |
| **1:20–1:50** Demo soạn phiếu | Quay màn hình: chụp trang sách giáo khoa bằng điện thoại → tải lên → bấm Tạo phiếu → phiếu 3 mức hiện ra | "Tôi chỉ cần chụp trang sách giáo khoa. Khoảng 30 giây, AI soạn xong phiếu ba mức theo Thông tư 27, có đáp án trình bày đúng như vở học sinh: bài giải, phép tính có đơn vị, đáp số, kèm ma trận và yêu cầu cần đạt." |
| **1:50–2:10** AI kiểm định | Phóng to khối "Kiểm định AI" → góp ý câu 7 → bấm "Sửa theo góp ý" | "Điểm khác biệt là một lượt AI thứ hai đóng vai tổ trưởng chuyên môn: tự giải lại từng câu để soát đáp án sai và câu lệch mức. Trong thí điểm, nó đã phát hiện ⟦…⟧ lỗi." |
| **2:10–2:30** Phân hóa | Tab In phiếu → chuyển Chung / Xanh / Cam / Tím | "Một phiếu tự tách thành ba phiếu Xanh, Cam, Tím cho ba nhóm. Tên màu trung tính, nên các em không cảm thấy bị xếp loại." |
| **2:30–3:05** Lớp học số | Trang Giao bài → Chiếu mã QR → điện thoại học sinh quét, chạm tên, làm bài → bảng theo dõi tăng "x/30 đã nộp" | "Trên lớp, tôi chiếu mã QR. Các em quét bằng máy tính bảng, chạm vào tên mình, không cần tài khoản, và tự nhận đúng phiếu của nhóm. Câu trắc nghiệm được chấm ngay. Tôi theo dõi trực tiếp em nào đã nộp." |
| **3:05–3:35** Chấm & phân tích lỗi | Trang Chấm bài: sổ tổng hợp → biểu đồ lỗi sai → bấm "Soạn phiếu bổ trợ" | "Với bài viết tay, tôi chụp ảnh để AI chấm và viết nhận xét theo Thông tư 27. Mức Hoàn thành tốt, Hoàn thành hay Chưa hoàn thành được tính theo quy tắc công khai, và tôi có thể sửa từng câu. Biểu đồ cho thấy cả lớp còn yếu ở đâu, ví dụ quên nhớ khi cộng. Một nút bấm là có phiếu bổ trợ đúng chỗ đó." |
| **3:35–3:50** Tiến bộ, học bạ | Trang Tiến bộ: biểu đồ một em | "Kết quả được lưu theo từng em. Cuối kỳ, AI gợi ý nhận xét học bạ dựa trên cả quá trình, không cần gửi tên học sinh." |
| **3:50–4:25** Kết quả thực tế | Slide 13 + cảnh lớp học thật | "Sau ⟦…⟧ ngày thí điểm với ⟦…⟧ học sinh: thời gian soạn phiếu giảm từ ⟦…⟧ xuống ⟦…⟧ phút, chấm và nhận xét giảm từ ⟦…⟧ xuống ⟦…⟧ phút. Tỉ lệ chưa đạt giảm từ ⟦…⟧ xuống ⟦…⟧ sau một buổi bổ trợ. ⟦Trích một phản hồi của học sinh hoặc đồng nghiệp⟧." |
| **4:25–4:45** Trách nhiệm, bền vững | Slide 14 | "Sản phẩm miễn phí, chạy trên trình duyệt, dùng cho khối 1 đến 5 và bộ sách giáo khoa dùng chung toàn quốc. Tên học sinh không được gửi cho AI; mọi đề, điểm và nhận xét đều do giáo viên duyệt." |
| **4:45–5:00** Kết | Slide 15 + QR dùng thử | "Phần lập trình được thực hiện với sự hỗ trợ của công cụ AI ⟦và …⟧. Mong rằng Trợ Lý Giảng Dạy sẽ giúp mỗi học sinh được học vừa sức, và giáo viên có thêm thời gian cho từng em. Xin cảm ơn Ban Giám khảo!" |

## Sau khi quay

1. Cắt các đoạn chờ AI xử lý (giữ 1–2 giây, chèn chữ "⏱ ~30 giây" để trung thực về tốc độ).
2. Chèn phụ đề, logo trường nếu có.
3. Xuất MP4 1080p, kiểm tra **≤ 5:00**.
4. Tải lên Google Drive, đặt quyền "Bất kỳ ai có đường liên kết – Người xem", mở thử bằng cửa sổ ẩn danh.
5. Tạo mã QR video (mục 5 của [00-checklist-nop-bai.md](00-checklist-nop-bai.md)) để chèn vào slide 15 và poster.
