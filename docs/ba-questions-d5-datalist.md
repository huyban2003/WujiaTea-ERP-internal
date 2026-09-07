# Câu hỏi gửi BA — `CMP-DL-001` DataList (`UI-DATALIST-001`, STT 126)

**Gửi sau lượt D5d (2026-09-07), bổ sung câu 4 sau lượt D5e và câu 5 sau lượt D5f.** Năm câu, đều đã có số đo kèm theo. Câu 1 là câu treo từ phiên
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

## Câu 4 — Hàng mobile cao vượt trần 76px, và cái giá của việc thống nhất dáng (bổ sung sau lượt D5e)

Lượt D5e đã đưa **9 danh sách mobile** về một bộ dáng (cao 64–76 · gap 8 · radius 12 · padding
`12px 14px`). Ba con số đo được xin BA xem, vì Dev **không tự quyết**:

**(a) Hai màn vượt trần 76px vì nội dung tự xuống dòng.**

| Màn | Cao thật của hàng | Trần BA |
|---|---|---:|
| `/portal/notification` | **99,9 – 129,3** | 76 |
| `/portal/knowledge` | **79,8 – 129,4** | 76 |

Hàng thông báo mang tiêu đề + nguồn + tối đa 3 badge (ưu tiên · hết hiệu lực · có file); hàng bài
viết mang tiêu đề 2 dòng + badge + ngày cập nhật. **Ép về 76 là phải bỏ bớt thông tin nghiệp vụ**
— cùng loại với LIMIT đã được BA nghiệm thu ở D5c (hàng hai dòng 77–89 giữ nguyên theo cột ≥52).
Dev **không tự ép**; xin BA chốt: (1) chấp nhận trần 76 chỉ áp cho hàng một dòng, hay (2) chỉ ra
field nào bỏ được.

**(b) Trang chủ mobile và Hỗ trợ dài thêm.**

| Trang | 390px | 360px |
|---|---|---|
| `/portal` | 2883 → **3028** (+145) | 2996 → **3241** (+245) |
| `/portal/support` | 2664 → **2935** (+271) | 2762 → **2935** (+173) |
| `/portal/knowledge` | 1916 → **1852** (−64) | 2042 → **1978** (−64) |

Nở **không phải** vì gap 8 mà vì đệm ngang 14px hai bên làm bề rộng chữ hụt 30px ⇒ xuống dòng
thêm. Nếu BA muốn giữ trang ngắn, cách rẻ nhất là hạ đệm ngang về **12px** (vẫn trong dải BA
`12–14px`) cho riêng các khối nằm trong thẻ.

**(c) Acceptance #9 thủng đúng một ô.** `/portal` khổ **360**, khối *Thông báo mới nhất*: số dòng
đọc được không cần cuộn **2 → 1**. Mọi ô còn lại giữ nguyên. Đây là hệ quả trực tiếp của (b).

Xin BA chốt một trong ba: **giữ nguyên** (đổi độ dài trang lấy dáng thống nhất) · **hạ đệm ngang
về 12px** · **cho khối preview Trang chủ một bộ số riêng**.

## Câu 5 — Hàng *chuyến giao* mobile cao 129px, trần detail-card là 120 (bổ sung sau lượt D5f)

Lượt D5f đưa hai danh sách mobile **nhiều metadata** về bộ số `detail-card` của BA (cao 96–120 ·
gap 8 · radius 12 · padding `12px 14px`). Một trong hai vào đúng dải, một thì không:

| Màn | Cao hàng trước | Cao hàng sau | Trần BA |
|---|---:|---:|---:|
| `/portal/return` | 122,3 | **118,3** ✅ | 120 |
| `/portal/delivery` | 128,98 | **128,98** ❌ | 120 |

`/portal/return` hạ được vì đệm dọc của nó đang là `14px`, thu về `12px` là đủ. `/portal/delivery`
**đã** ở `12px` — mức thấp nhất trong dải BA — nên không còn pixel nào để cắt. Ép về 120 chỉ còn cách
bỏ bớt nội dung của hàng, hiện gồm: nhãn *Chuyến xe* + mã chuyến · badge trạng thái · đường kẻ ·
hai ô meta có icon (*Ngày xuất phát*, *Đơn liên quan*).

Dev **không tự cắt field** (cùng loại LIMIT BA đã nghiệm thu ở D5c). Xin BA chốt một trong hai:
**(1)** trần 120 chỉ áp cho hàng ít metadata, hàng nhiều metadata được vượt — hoặc **(2)** chỉ ra
field nào bỏ được / đẩy sang màn chi tiết.

⚠️ Số 128,98 này **chưa từng xuất hiện** trong kiểm kê ngày 25/08: lúc đó mỗi cửa hàng chỉ có **1
chuyến giao** nên hàng này không đo được. Nó chỉ lộ ra sau khi bổ dữ liệu thử theo đúng acceptance #7
của BA (0/1/2/10/11/50+).

**Tin tốt của lượt này:** `/portal/return` **ngắn đi 156px** và `/portal/delivery` **ngắn đi 52px**
ở mọi khổ mobile, và **acceptance #9 không thủng ô nào** (4 record đọc-không-cuộn, giữ nguyên ở cả
hai màn, cả ba khổ) — ngược chiều với cái giá đã báo ở câu 4.

---

**Ghi chú thi hành:** tới khi có trả lời, `UI-DATALIST-001` vẫn `Ready for Dev` (cụm D5 chưa
khép), và bảng nghiệm thu D5d ghi bộ số này là **provisional** — đúng cách BA đã yêu cầu cho phần
Khảo sát ở acceptance #10.
