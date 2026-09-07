# Câu hỏi gửi BA — `CMP-DL-001` DataList (`UI-DATALIST-001`, STT 126)

**Gửi sau lượt D5d (2026-09-07).** Ba câu, đều đã có số đo kèm theo. Câu 1 là câu treo từ phiên
kiểm kê D5a; câu 2 và 3 là hai chỗ **mới lộ ra khi đo**, chưa từng nêu.

Trong lúc chờ trả lời, phần đã làm vẫn chạy được trên UAT; nếu BA chốt khác, chỗ phải sửa đã được
gom sẵn vào **một khối CSS duy nhất** (`.wj-data-list--compact-row .wj-data-item` trong
`_components.css`) nên lùi lại chỉ là một thao tác, không phải gỡ 4 màn.

---

## Câu 1 — Field nào của bảng PC được phép ẩn trên mobile, và ẩn rồi thì xem lại ở đâu?

Chính BA đã cảnh báo rủi ro *"ẩn field mobile không có detail sẽ làm mất thông tin nghiệp vụ"*.
Đo thật cho thấy khoảng cách đang rất rộng:

| Màn | PC | Mobile |
|---|---:|---|
| `/portal/delivery` | **8 cột** (có *Xe · tài xế*, *Biển số*, *Cập nhật*) | 4 thông tin: mã chuyến · trạng thái · giờ xuất phát · đơn liên quan |
| `/portal/support` | **8 cột** | 4 thông tin |

Dev **không tự quyết** field nào là P1 (luôn hiện) / P2 (ẩn, xem ở màn chi tiết) / P3 (bỏ hẳn).
Xin BA cho danh sách ưu tiên theo từng màn, và nói rõ field P2 xem lại ở đâu.

## Câu 2 — Preview trên Trang chủ đang lệch field theo CẢ HAI chiều

Không phải "mobile thiếu so với PC" như câu 1, mà lệch qua lại. Đọc thẳng từ mã nguồn
`portal_home.xml`:

| Khối preview | PC hiện | Mobile hiện | Lệch |
|---|---|---|---|
| Thông báo mới nhất | tiêu đề · giờ ngày · badge loại | y hệt (thêm icon) | — |
| Đơn hàng gần đây | mã đơn · giờ ngày · badge trạng thái | mã đơn · giờ ngày · **số tiền** · badge | **PC thiếu số tiền** |
| Yêu cầu đổi trả | mã · giờ ngày · badge trạng thái | mã · ngày yêu cầu · **lý do** · badge | **PC thiếu lý do** |

Xin BA chốt bản nào là chuẩn cho từng khối. Nếu PC phải có thêm *số tiền* và *lý do*, cần biết
chúng đứng ở cột nào — hàng preview PC hiện chỉ có 4 ô (chấm · nội dung · ngày · badge).

## Câu 3 — Danh sách PC **không phải bảng** lấy bộ số nào? (kèm một hệ quả đo được)

Spec cho hai bộ số: **DataTable** cho ≥992px (header 44 · row ≥52 · padding `10px 16px`) và
**compact-row** cho <992px (cao 64–76 · gap 8 · radius 12 · padding `10–12px 12–14px`).
Bốn màn sau **rơi vào giữa**: chúng ở PC (≥992) nhưng không phải bảng — 3 khối preview Trang chủ
và danh sách bài viết `/portal/knowledge`.

Trạng thái trước D5d: row **51.8px**, gap **0** (các dòng dính nhau, ngăn bằng một đường kẻ),
không bo góc — **không khớp bộ số nào**.

Lượt D5d đã áp bộ **compact-row (64 · gap 8 · radius 12 · `12px 14px`)** cho cả 4 màn. Hệ quả đo
được, xin BA cân nhắc:

| | Trước | Sau |
|---|---:|---:|
| Chiều cao trang `/portal` (PC) | 900 | 900 (@992: 906) — **gần như không đổi** |
| Chiều cao trang `/portal/knowledge` (PC) | 995 | **1230** (+235) |
| Số bài viết đọc được không cần cuộn, `/portal/knowledge` | **12** | **9** |

Dòng cuối là chỗ phải hỏi: acceptance #9 của chính BA ghi *"số record thấy trong viewport không
được giảm"*, mà kéo row từ 51.8 lên 64 thì màn cao 900 chứa được 9 thay vì 12. Hai yêu cầu này
đang mâu thuẫn nhau ở đúng màn này.

Ba hướng, xin BA chọn:

1. **Giữ 64–76 như hiện tại** — chấp nhận đọc được ít dòng hơn, đổi lấy danh sách thoáng và thống
   nhất với mobile.
2. **Cho danh sách PC một bộ số riêng** (ví dụ 52–56 · gap 4) — dung hoà, nhưng thành bộ số thứ ba
   phải bảo trì.
3. **Trả về dáng cũ** (51.8 · gap 0 · đường kẻ ngăn) và ghi nhận đây là ngoại lệ có chủ đích.

---

**Ghi chú thi hành:** tới khi có trả lời, `UI-DATALIST-001` vẫn `Ready for Dev` (cụm D5 chưa
khép), và bảng nghiệm thu D5d ghi bộ số này là **provisional** — đúng cách BA đã yêu cầu cho phần
Khảo sát ở acceptance #10.
