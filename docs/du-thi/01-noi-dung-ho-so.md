# Nội dung hồ sơ dự thi

**Tên sản phẩm:** Trợ Lý Giảng Dạy – Phiếu bài tập phân hóa và đánh giá học sinh tiểu học theo Thông tư 27 bằng AI
**Tác giả:** ⟦Họ tên⟧ – ⟦chức vụ, môn/lớp phụ trách⟧ – Trường ⟦tên trường⟧, ⟦tỉnh/thành⟧
**Bảng:** A (Mầm non và Tiểu học)
**Chủ đề chính:** Giảng dạy, học tập và đánh giá. **Chủ đề liên quan:** Lớp học số tích hợp AI; Ứng dụng AI có trách nhiệm.
**Địa chỉ sản phẩm:** <https://tro-ly-giang-day.streamlit.app> · Link trải nghiệm cho Ban Giám khảo: ⟦https://tro-ly-giang-day.streamlit.app/?demo=MA_DEMO⟧

> Tài liệu này là nội dung gốc cho slide, poster và video. Thứ tự các phần theo đúng 5 nội dung thể lệ yêu cầu. Chỗ `⟦…⟧` cần điền thông tin hoặc số liệu thật sau khi thí điểm.

---

## 1. Bối cảnh và vấn đề  *(tiêu chí Tính thực tiễn – 25%)*

**Bối cảnh.** Thông tư 27/2020/TT-BGDĐT yêu cầu đánh giá học sinh tiểu học thường xuyên bằng nhận xét. Câu hỏi, bài tập được thiết kế theo 3 mức:
- **Mức 1:** nhận biết, nhắc lại.
- **Mức 2:** kết nối, sắp xếp.
- **Mức 3:** vận dụng giải quyết vấn đề mới.

Chương trình GDPT 2018 đồng thời đòi hỏi dạy học phân hóa, phù hợp năng lực từng em.

**Vấn đề thực tế tại lớp ⟦tên lớp⟧ (⟦sĩ số⟧ học sinh).** Trình độ học sinh trong lớp chênh lệch rõ. Muốn dạy phân hóa, mỗi tuần giáo viên phải:
- soạn phiếu bài tập ở 3 mức kèm đáp án và ma trận;
- in phiếu riêng cho từng nhóm;
- chấm bài, viết nhận xét cho từng em;
- tìm ra những chỗ cả lớp còn yếu để dạy bù;
- cuối kỳ tổng hợp nhận xét vào học bạ.

Theo ⟦khảo sát/ghi nhận của tác giả⟧, soạn một phiếu phân hóa có đáp án mất khoảng ⟦…⟧ phút; chấm và nhận xét một lớp mất khoảng ⟦…⟧ phút. Vì vậy phiếu phân hóa thường chỉ được làm ⟦…⟧ lần/tháng.

**Nguyên nhân.**
1. Soạn đề 3 mức đúng chuẩn tốn thời gian và khó giữ chất lượng đồng đều.
2. Chatbot AI phổ thông trả lời rời rạc: không theo mẫu TT27, không kiểm tra lại đáp án, không in được phiếu theo nhóm, không nối với việc chấm và theo dõi tiến bộ.
3. Kết quả chấm nằm rải rác trên giấy, khó phân tích để dạy bổ trợ kịp thời.

**Nhu cầu.** Cần một công cụ miễn phí, dễ dùng trên điện thoại và máy tính của trường. Công cụ phải giúp giáo viên đi hết vòng **soạn → dạy → đánh giá → bổ trợ** theo đúng TT27. Giáo viên vẫn là người quyết định cuối cùng.

## 2. Ý tưởng, giải pháp, công cụ AI và hình thức triển khai  *(tiêu chí Tính sáng tạo – 20%)*

**Ý tưởng cốt lõi:** một **vòng khép kín** gồm 6 bước, AI hỗ trợ ở từng bước, giáo viên duyệt và quyết định.

```text
① Soạn phiếu 3 mức ──► ② AI kiểm định ──► ③ Dạy trên lớp / Giao bài online
        ▲                                              │
        │                                              ▼
⑥ Tiến bộ & học bạ ◄── ⑤ Phân tích lỗi → phiếu bổ trợ ◄── ④ Chấm & nhận xét TT27
```

| Bước | AI làm gì | Giáo viên làm gì |
|---|---|---|
| ① Soạn phiếu | Từ tên bài hoặc **ảnh chụp trang sách giáo khoa**, AI soạn phiếu 3 mức TT27 kèm đáp án, hướng dẫn chấm, ma trận, yêu cầu cần đạt. Đáp án trình bày theo chuẩn tiểu học ("Bài giải – câu lời giải – phép tính (đơn vị) – Đáp số"). | Chọn lớp, môn, bộ sách, thời lượng; đổi câu, làm dễ hơn hoặc khó hơn, sửa tay. |
| ② Kiểm định | Một **lượt AI thứ hai đóng vai tổ trưởng chuyên môn**: tự giải lại từng câu, phát hiện đáp án sai, câu lệch mức, từ ngữ chưa phù hợp lứa tuổi. Kết quả là điểm chất lượng 0–100 và góp ý từng câu. | Đọc góp ý, bấm "Sửa theo góp ý" hoặc giữ nguyên. |
| ③ Dạy và giao bài | Phiếu tự tách thành **3 phiếu nhóm Xanh/Cam/Tím**. Tên màu trung tính để học sinh không bị "dán nhãn". Có thêm đề A/B chống nhìn bài, phiếu in sẵn tên từng em, chế độ trình chiếu kiểu trò chơi, và **giao bài online bằng mã QR**: học sinh chọn tên, tự nhận đúng phiếu nhóm mình. | Chia nhóm, in phiếu hoặc chiếu mã lên lớp. |
| ④ Chấm và nhận xét | **Chấm từ ảnh chụp bài làm viết tay** hoặc bài làm online. Câu trắc nghiệm, đúng/sai, nối cột được chấm ngay; AI viết **nhận xét theo tinh thần TT27**. Mức Hoàn thành tốt / Hoàn thành / Chưa hoàn thành được tính bằng **quy tắc cố định, công khai** (không để AI tự quyết). | Xem lại, **chấm tay hoặc sửa** từng câu, chốt mức và nhận xét. |
| ⑤ Phân tích lỗi | Thống kê tỉ lệ chưa đạt từng câu và lỗi thường gặp, rồi **soạn phiếu bổ trợ** nhắm đúng chỗ hổng kiến thức. | Dạy bổ trợ cho nhóm cần thiết. |
| ⑥ Tiến bộ và học bạ | Theo dõi mức TT27 của từng em qua các lần đánh giá; **gợi ý nhận xét cuối kỳ** để ghi học bạ. | Duyệt, sửa, xuất Excel. |

**Điểm mới so với cách làm hiện có.**
- Không phải một chatbot rời rạc, mà một **quy trình sư phạm hoàn chỉnh theo TT27**, từ soạn đến bổ trợ và học bạ, dữ liệu chảy liền mạch giữa các bước.
- **AI kiểm định AI:** lượt thứ hai rà soát, giảm rủi ro đáp án sai, là lỗi đáng ngại nhất khi dùng AI soạn đề.
- **Phân hóa không dán nhãn:** phiếu Xanh/Cam/Tím và giao bài online tự giao đúng phiếu theo nhóm.
- **Kết hợp AI và quy tắc minh bạch:** mức đạt TT27 được tính bằng quy tắc công khai; AI chỉ đề xuất, giáo viên quyết định.
- **Không cần tài khoản cho học sinh:** quét mã QR, chạm vào tên là làm bài được; phù hợp học sinh tiểu học.

**Công cụ AI sử dụng.**
- Mô hình ngôn ngữ đa phương thức **Google Gemini (dòng Flash)**: đọc ảnh trang sách và ảnh bài làm viết tay; tạo nội dung có cấu trúc (JSON schema) để kiểm soát định dạng.
- Ứng dụng web xây dựng bằng **Streamlit (Python)**; dữ liệu lưu trên **Supabase (PostgreSQL)**; giáo viên đăng nhập bằng **tài khoản Google**.
- Phần lập trình được thực hiện với sự hỗ trợ của **công cụ AI lập trình (Claude Code)** ⟦và người hỗ trợ kỹ thuật: …⟧ (xem mục Minh bạch).

**Hình thức triển khai.**
- Chạy trên trình duyệt (máy tính, máy chiếu, điện thoại); không cần cài đặt.
- **Chi phí 0 đồng**: dùng các gói miễn phí của Streamlit Community Cloud, Supabase và Gemini API.

## 3. Kết quả và tác động  *(tiêu chí Tác động và kết quả thực tế – 25%)*

> **Phần này chỉ được điền bằng số liệu thật từ đợt thí điểm** (kế hoạch ở [05-ke-hoach-thi-diem-va-khao-sat.md](05-ke-hoach-thi-diem-va-khao-sat.md)). Nếu số liệu còn ít, hãy ghi đúng là "kết quả thí điểm bước đầu, ⟦n⟧ ngày, ⟦n⟧ học sinh".

**Phạm vi thí điểm:** lớp ⟦…⟧, ⟦sĩ số⟧ học sinh, môn ⟦…⟧, từ ⟦ngày⟧ đến ⟦ngày⟧. Có ⟦n⟧ đồng nghiệp dùng thử.

| Chỉ số | Trước (cách làm cũ) | Sau (dùng sản phẩm) |
|---|---|---|
| Thời gian soạn 1 phiếu phân hóa có đáp án, ma trận | ⟦… phút⟧ | ⟦… phút⟧ |
| Thời gian chấm và nhận xét 1 lớp | ⟦… phút⟧ | ⟦… phút⟧ |
| Số đáp án sai AI kiểm định phát hiện được / số phiếu | – | ⟦…⟧ |
| Tỉ lệ học sinh hoàn thành bài (giao online hoặc phiếu nhóm) | ⟦…%⟧ | ⟦…%⟧ |
| Tỉ lệ chưa đạt, trước và sau phiếu bổ trợ | ⟦…%⟧ | ⟦…%⟧ |
| Mức độ hài lòng của học sinh (phiếu mặt cười) | – | ⟦…% 😊⟧ |
| Đánh giá của giáo viên dùng thử (thang 5) | – | ⟦…/5⟧ |

**Phản hồi tiêu biểu:**
- Giáo viên: "⟦trích nguyên văn⟧" – ⟦tên, trường⟧.
- Học sinh: "⟦trích nguyên văn, không ghi tên⟧".

**Tác động:**
- **Với giáo viên:** ⟦tiết kiệm … giờ/tuần⟧; có dữ liệu để dạy bổ trợ đúng chỗ; nhận xét học bạ dựa trên quá trình thay vì trí nhớ.
- **Với học sinh:** mỗi em làm bài vừa sức; được phản hồi ngay ở các câu tự chấm; học bổ trợ đúng phần còn yếu.
- **Với nhà trường:** ⟦…⟧

## 4. Tính bền vững và khả năng nhân rộng  *(tiêu chí 15%)*

- **Chi phí 0 đồng** và chạy bằng trình duyệt trên thiết bị sẵn có của trường. Học sinh dùng điện thoại hoặc máy tính phòng tin học; không cần tài khoản.
- **Mỗi giáo viên có không gian dữ liệu riêng** khi đăng nhập Google, nên nhiều giáo viên trong trường dùng cùng lúc được.
- **Áp dụng cho khối 1–5**, gồm các môn: Toán, Tiếng Việt, Tự nhiên và Xã hội, Khoa học, Lịch sử và Địa lí, Đạo đức, Tin học, Công nghệ; bám sát bộ sách **Kết nối tri thức với cuộc sống** – bộ sách giáo khoa dùng thống nhất toàn quốc từ năm học 2026–2027 (Quyết định 3588/QĐ-BGDĐT ngày 26/12/2025).
- **Dễ chuyển giao:** có hướng dẫn cài đặt và sử dụng; trường khác có thể tự triển khai bản riêng trên hạ tầng miễn phí.
- **Hướng phát triển:** chia sẻ phiếu trong tổ chuyên môn; tin nhắn gửi phụ huynh từ kết quả đánh giá; báo cáo minh chứng cho nhà trường.
- **Giới hạn hiện tại (nêu thẳng):**
  - Gói miễn phí giới hạn số lượt AI và khoảng 30–40 học sinh làm bài online cùng lúc.
  - AI vẫn có thể sai, nên luôn cần giáo viên duyệt.
  - Chọn tên khi làm bài online không ngăn được việc làm hộ (giáo viên có thể mở lại bài cho từng em).

## 5. Ứng dụng AI có trách nhiệm

- **Giáo viên luôn là người quyết định:** AI đề xuất; giáo viên duyệt đề, sửa đáp án, chốt điểm, mức đạt và nhận xét. Có chấm tay đầy đủ, không phụ thuộc AI.
- **Kiểm soát chất lượng:** lượt AI kiểm định thứ hai; đáp án theo chuẩn trình bày của sách giáo khoa tiểu học; mức TT27 tính bằng quy tắc công khai.
- **Bảo vệ dữ liệu học sinh:**
  - **Tên học sinh không được gửi cho AI** khi soạn phiếu, chấm bài online hay gợi ý học bạ. Riêng khi chấm từ ảnh, ảnh bài làm (có thể có tên viết tay) được gửi tới dịch vụ AI để chấm và app không lưu ảnh.
  - Học sinh không cần tài khoản, app không thu thập email học sinh.
  - Dữ liệu của mỗi giáo viên được tách riêng; cơ sở dữ liệu chặn truy cập công khai.
- **Công bằng:** phiếu nhóm dùng tên màu trung tính; học sinh làm bài online thấy mình làm đúng hay sai nhưng không thấy đáp án, để đảm bảo công bằng giữa các em.

## Minh bạch về quá trình xây dựng sản phẩm

> ⟦Điều chỉnh đoạn này theo trả lời của Ban Tổ chức (email trong [00-checklist-nop-bai.md](00-checklist-nop-bai.md)).⟧
>
> Tác giả là người phát hiện vấn đề, đề xuất ý tưởng, xây dựng toàn bộ yêu cầu sư phạm (cấu trúc phiếu 3 mức theo TT27, cách phân nhóm, quy tắc xếp mức, chuẩn trình bày đáp án), trực tiếp thử nghiệm và triển khai trên lớp. Phần lập trình được thực hiện với sự hỗ trợ của công cụ AI lập trình Claude Code ⟦và hỗ trợ kỹ thuật của …⟧.
