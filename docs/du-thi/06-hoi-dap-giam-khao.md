# Chuẩn bị trả lời Ban Giám khảo

Tiêu chí "Chất lượng trình bày và tính thuyết phục" (15%) có yêu cầu *giáo viên trả lời được câu hỏi và thuyết phục Ban Giám khảo*. Nguyên tắc: trả lời ngắn (≤ 30 giây), có ví dụ hoặc số liệu, **nói thẳng giới hạn**. Giám khảo đánh giá cao sự trung thực hơn câu trả lời "hoàn hảo".

---

**1. AI soạn đề sai thì sao?**
Có 3 lớp bảo vệ:
1. AI soạn theo khung cấu trúc và quy tắc trình bày đáp án chuẩn tiểu học.
2. Một lượt AI thứ hai đóng vai tổ trưởng chuyên môn, tự giải lại từng câu.
3. Giáo viên duyệt và sửa trước khi phát.

Trong thí điểm, kiểm định phát hiện ⟦B3⟧ lỗi, tôi tự phát hiện thêm ⟦B4⟧ lỗi. Vì vậy app không bao giờ phát phiếu thẳng cho học sinh mà không qua giáo viên.

**2. Sản phẩm khác gì so với hỏi trực tiếp ChatGPT hay Gemini?**
Chatbot trả lời từng câu rời rạc. Ở đây là cả quy trình theo TT27, dữ liệu nối liền từ phiếu đến chấm bài, phân tích lỗi, phiếu bổ trợ và học bạ. Ngoài ra có: phiếu tự tách 3 nhóm, kiểm định tự động, chấm ảnh bài viết tay, giao bài bằng QR mà học sinh không cần tài khoản. Giáo viên không phải viết câu lệnh cho AI.

**3. Dữ liệu học sinh được bảo vệ thế nào?**
- Tên học sinh không gửi cho AI khi soạn phiếu, chấm bài online hay gợi ý học bạ. Khi chấm từ ảnh, ảnh bài làm được gửi tới dịch vụ AI để chấm và app không lưu ảnh.
- Học sinh không cần tài khoản, app không thu thập email học sinh.
- Dữ liệu mỗi giáo viên tách riêng theo tài khoản Google; cơ sở dữ liệu chặn truy cập công khai.
- Thí điểm có xin phép nhà trường và phụ huynh, theo đúng quy định hiện hành về bảo vệ dữ liệu cá nhân.

**4. Chấm chữ viết tay của học sinh có chính xác không?**
Chưa hoàn hảo. Ví dụ ở lớp 4A3, Bài 14 "So sánh các số có nhiều chữ số": số nhiều chữ số viết sát nhau, dấu >, < viết nhỏ hoặc mờ có thể bị đọc nhầm. Trong thí điểm, ⟦B7⟧ bài phải sửa. Vì vậy mọi kết quả đều hiện để giáo viên duyệt, có chấm tay từng câu. Với dạng bài điền dấu hay chọn số lớn nhất, có thể giao online dạng chạm chọn (trắc nghiệm, đúng/sai, nối cột), được chấm chính xác bằng quy tắc, không cần AI.

**5. Quy tắc xếp mức Hoàn thành tốt / Hoàn thành / Chưa hoàn thành dựa vào đâu?**
TT27 quy định 3 mức đánh giá và 3 mức câu hỏi, nhưng **không quy định ngưỡng phần trăm** cho từng bài thường xuyên. Quy tắc trong app do tôi đề xuất dựa trên tinh thần TT27:
- Chưa hoàn thành: Mức 1 đúng dưới 50%.
- Hoàn thành tốt: Mức 1 và Mức 2 đúng từ 80% trở lên, Mức 3 đúng từ 50% trở lên.
- Hoàn thành: các trường hợp còn lại.

Quy tắc này công khai, nhất quán giữa các em. Đây chỉ là gợi ý, giáo viên luôn sửa được mức cuối cùng.

**6. Chia nhóm Xanh/Cam/Tím có làm học sinh tự ti không?**
Tên nhóm là màu trung tính, trên phiếu không ghi "mức". Khi làm online, học sinh không thấy mình ở nhóm nào. Nhóm thay đổi sau mỗi lần đánh giá: app gợi ý chuyển nhóm theo kết quả mới, nên không em nào bị "đóng khung".

**7. Trường không đủ máy cho học sinh thì sao?**
Phần cốt lõi (soạn phiếu, in phiếu nhóm, chấm bằng ảnh chụp) chỉ cần một điện thoại hoặc máy tính của giáo viên. Giao bài online là tùy chọn, dùng được với máy tính bảng, phòng tin học, hoặc làm ở nhà trên điện thoại của phụ huynh.

**8. Chi phí khi cả trường hoặc cả huyện cùng dùng?**
Hiện tại 0 đồng nhờ các gói miễn phí. Gói miễn phí có giới hạn lượt AI mỗi phút và mỗi ngày. Khi mở rộng, mỗi trường có thể dùng API key riêng. Chi phí AI trả phí cho một phiếu chỉ ở mức vài trăm đồng ⟦kiểm tra bảng giá Gemini tại thời điểm thi⟧. Mã nguồn và hướng dẫn cho phép trường tự triển khai bản riêng.

**9. Thầy/cô tự làm sản phẩm này đến đâu?**
Trả lời đúng như mục "Minh bạch" trong hồ sơ. Ví dụ: *"Tôi phát hiện vấn đề, thiết kế toàn bộ yêu cầu sư phạm (cấu trúc phiếu 3 mức, cách chia nhóm, quy tắc xếp mức, chuẩn trình bày đáp án), thử nghiệm trên lớp và quyết định từng tính năng. Phần lập trình tôi làm cùng công cụ AI Claude Code ⟦và có hỗ trợ kỹ thuật của …⟧. Đây cũng là một cách ứng dụng AI: giáo viên không chuyên tin học vẫn có thể tự tạo công cụ cho lớp mình."*
Chuẩn bị sẵn: giải thích được mọi tính năng, lý do thiết kế, và demo trực tiếp không cần người hỗ trợ.

**10. Giáo viên có bị phụ thuộc vào AI, mất kỹ năng ra đề không?**
AI làm phần lặp lại (gõ đề, tính đáp án, định dạng, in theo nhóm). Giáo viên vẫn chọn bài, chọn mức, duyệt và chỉnh từng câu, quyết định nhận xét. Thời gian tiết kiệm được dành cho việc quan sát và kèm từng em.

**11. Mất mạng hoặc AI quá tải giữa giờ dạy thì sao?**
- App tự thử lại và chuyển sang mô hình AI dự phòng.
- Phiếu đã tạo được lưu trong thư viện, có thể in, tải Word hoặc lưu file trước giờ dạy.
- Trình chiếu và chấm phần trắc nghiệm không cần AI.

**12. Đánh giá "AI kiểm định AI" có thật sự hiệu quả?**
Dẫn số liệu B3/B4 và một ví dụ cụ thể trong thí điểm (câu nào bị phát hiện sai, sửa thế nào). Nếu số liệu còn ít, nói rõ là kết quả bước đầu.

**13. Kế hoạch sau cuộc thi?**
- Tiếp tục dùng trong học kỳ I và theo dõi số liệu.
- Chia sẻ trong tổ chuyên môn khối 4, Trường Tiểu học Ngô Quyền, rồi đến các khối khác trong trường.
- Phát triển chia sẻ phiếu giữa giáo viên và tin nhắn gửi phụ huynh.
- Tập huấn ngắn cho đồng nghiệp.

**14. Vì sao chọn Gemini?**
Đọc được ảnh (trang sách, bài viết tay), hỗ trợ tiếng Việt tốt, có gói miễn phí để giáo viên dùng không tốn chi phí, và trả kết quả theo khung cấu trúc nên dễ kiểm soát định dạng.

**15. Giọng trong video là giọng AI – vì sao?**
Giọng đọc AI được ghi rõ trên video ("Lồng tiếng: giọng đọc AI"). Nội dung, kịch bản và toàn bộ sản phẩm do tôi xây dựng; giọng AI giúp video rõ, đúng thời lượng. Thể lệ không cấm lồng tiếng AI, và ở vòng chung kết tôi thuyết trình trực tiếp.

**16. Sản phẩm khác gì Azota, OLM hay Quizizz?**
Theo tôi biết, các nền tảng đó chủ yếu tập trung vào ngân hàng câu hỏi và làm bài trắc nghiệm trực tuyến. Trợ Lý Giảng Dạy đi theo một vòng khép kín cho giáo viên tiểu học:
- soạn phiếu 3 mức theo TT27, đáp án trình bày theo chuẩn tiểu học;
- một lượt AI kiểm định lại phiếu;
- phiếu nhóm Xanh/Cam/Tím, không dán nhãn học sinh;
- chấm từ ảnh bài viết tay kèm nhận xét theo TT27;
- phân tích lỗi rồi soạn phiếu bổ trợ;
- gợi ý nhận xét học bạ.

Hai cách có thể dùng bổ sung cho nhau.

**17. Dữ liệu gửi Gemini gói miễn phí có bị dùng để huấn luyện không?**
Nói thẳng: với gói miễn phí, theo điều khoản hiện hành Google có thể dùng nội dung gửi lên để cải thiện dịch vụ. Vì vậy:
- ứng dụng không gửi danh sách lớp cho AI;
- gợi ý nhận xét học bạ không kèm tên học sinh;
- tôi khuyến nghị che tên trên bài làm trước khi chụp ảnh để chấm.

Nếu nhà trường cần mức bảo mật cao hơn, có thể dùng khóa API trả phí, chi phí rất thấp.

**18. Thí điểm 5 ngày có đủ để kết luận không?**
Chưa đủ để kết luận lâu dài. Đây là thí điểm bước đầu, đo thời gian soạn, chấm và mức độ cải thiện ngay sau một buổi bổ trợ trên lớp 4A3. Tôi tiếp tục theo dõi trong học kỳ I và sẽ cập nhật số liệu.

**19. Học sinh dùng thiết bị gì?**
Máy tính bảng hoặc máy tính của trường, hoặc điện thoại. Nếu thiếu thiết bị, tôi in phiếu nhóm và chấm bằng ảnh chụp bài làm, không cần máy cho từng em.

---

**Mẹo vòng chung kết:**
- Demo trực tiếp bằng link trải nghiệm; nhưng chuẩn bị sẵn video dự phòng và phiếu mẫu, đề phòng mạng yếu.
- Mở app trước 10 phút cho app "thức"; kiểm tra Supabase không tạm dừng.
- Mang theo 1 bộ phiếu in thật (Xanh, Cam, Tím, đáp án) và bài làm học sinh (đã che tên) để giám khảo cầm xem.
