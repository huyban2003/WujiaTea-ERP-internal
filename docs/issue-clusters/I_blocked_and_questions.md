# Cụm I — Không code: blocked · fork · đã đúng · câu hỏi gửi BA

**Issue:** UI-MOB-SHELL-001 · WJ-PH-003 · UI-PC-BASE-012 · UI-02 (phần cờ) ·
FUNC-MOB-ORDER-006 · RESP-MOB-ORDER-003 · RESP-MOB-ORDER-001

**Nên chạy cụm này TRƯỚC TIÊN** — rẻ nhất, gỡ blocker sớm nhất, và trả lại 2 issue cho BA retest.

---

## 1. Ba issue KHÔNG còn tái hiện trên UAT hiện tại

BA đo ngày 23–25/07 trên build `cd1025d`/`bd55ef9`. UAT nay đã deploy tới hết **Sprint 47 (02/08)**.
Đo lại 02/08/2026, headless Chromium, login admin:

### FUNC-MOB-ORDER-006 — Tìm kiếm mobile
```
391×844 · /portal/order · gõ "Tra" vào .wujia-morder-search input[name=keyword] · nhấn Enter
→ URL: http://113.161.187.126:8019/portal/order?keyword=Tra
```
**Enter submit đúng.** Nút "Tìm" đã có từ Sprint 2026-07-22-B. Form là GET thật, không JS chặn Enter.
→ **Không sửa code.** Chụp evidence → `Ready for Retest`.

### WJ-ORD-019 phần Enter + focus PC
```
1920×1080 · gõ "Tra" · Enter → /portal/order?keyword=Tra&category_id=
focus ô search PC → outline: rgb(40,169,223) solid 2px
```
Cả hai **đạt**. Phần **còn thật** = ô search mobile `outline-style: none` → đã đưa sang **cụm G**.

### RESP-MOB-ORDER-003 — Floating Cart Bar
`_components.css:1500-1507` đã `left: 16px; right: 16px;` + `bottom: calc(var(--wujia-mnav-height) + 8px)`.
Cột O (Current Owner) = **BA/Tester**, cột K đã ghi FIX/IMPACT/RETEST/LIMIT đầy đủ.
→ Theo QA Standard §4, issue đang ở phía BA. **Dev không làm gì**, chỉ nhắc BA retest.

---

## 2. Một issue blocked vì thiếu asset

### UI-MOB-SHELL-001 — Logo mobile
```
actual: container x=16 y=30 116×44 · artwork 64.34 × 34.31
source: container x=16 y=32 116×44 · artwork 100 × 34
```
`mobile_header.xml:24` dùng `env.company.logo_web` — ảnh logo công ty **gần vuông**.
Với `object-fit: contain` và khung cao 34px, chiều rộng tự co còn ~64px. Ép `width:100px` sẽ **méo logo**.

→ **Không có cách CSS nào tạo ra artwork 100×34 từ ảnh gần vuông.** Cần BA cấp file logo mobile tỉ lệ ~3:1.
Phần sửa được ngay: container `y=30 → 32` (2px). Nhưng làm lẻ thì BA vẫn fail → **để nguyên, chờ asset**.

*(Việc này đã nằm trong "Deferred" từ Sprint 38 với đúng lý do — nhắc lại để BA không tưởng Dev quên.)*

---

## 3. Một fork thiết kế — không được tự quyết

### WJ-PH-003 — Phạm vi trạng thái Lịch sử đặt hàng

BA chốt 30/07: hiển thị **Chờ xác nhận · Đã xác nhận · Đang giao · Hoàn tất**, loại đơn hủy do thay thế.

**Vấn đề kỹ thuật:** `sale.order.state` của **Odoo 19** chỉ có `draft / sent / sale / cancel`
(trạng thái "done/locked" đã bị bỏ khỏi selection từ Odoo 17). Code hiện tại
(`wujia_portal_purchase_history/controllers/portal.py:17-22`) map:
```
draft → Chờ xác nhận   sent → Đã gửi   sale → Đã xác nhận
```
→ **"Đang giao" và "Hoàn tất" không tồn tại trên `sale.order`.** Hai trạng thái này chỉ có thể suy từ
`order.batch_id.delivery_batch_status` (`stock.picking.batch`, các giá trị
`draft/assigned/loading/delivering/done/cancelled` — đã pin nhãn VN ở `portal.py:27-34`).

**Ba phương án, cần chọn:**
1. Trạng thái hiển thị = **kết hợp**: `sale.order.state` cho 2 nấc đầu, `delivery_batch_status` cho "Đang giao"/"Hoàn tất".
   Bộ lọc phải lọc trên 2 field → domain phức tạp, cần index.
2. Chỉ hiển thị 3 trạng thái có thật trên `sale.order`, bỏ "Đang giao"/"Hoàn tất" khỏi filter
   (đã có cột "Chuyến giao" riêng hiển thị trạng thái giao).
3. Thêm field computed store trên `sale.order` gom 2 nguồn → lọc/sort nhanh, nhưng là schema change + migration.

**Cũng chưa rõ:** "đơn đã hủy **do bị thay thế**" phân biệt bằng gì? Hiện code loại **mọi** `state = cancel`.
→ Nếu BA muốn phân biệt thì cần một dấu hiệu trên dữ liệu (lý do hủy / SO thay thế) mà source **chưa có**.

→ **Chuyển `Need Clarification`, owner BA.**

---

## 4. Hai issue cần BA xác nhận dữ liệu / quyết định

### UI-02 (phần cờ + nhãn ngôn ngữ) — code đúng, nghi dữ liệu user
Đo 6 route (`/portal`, `/order`, `/delivery`, `/notification`, `/support`, `/purchase-history`):
**6/6 đều ra `flag-icon-vn` + "Việt Nam".**

`layouts.xml:57` bám `lang == 'vi_VN'` = **ngôn ngữ của chính user đang đăng nhập** — đúng thiết kế.
BA thấy cờ Mỹ + "English" nhiều khả năng vì tài khoản test có `lang = en_US`.

→ Hỏi BA; nếu đúng thì đây là **Configuration**, không phải Custom. Phần hình học của UI-02 vẫn ở **cụm B**.

### UI-PC-BASE-012 — Sidebar sáng 2 mục trên `/portal`
`pc_sidenav.xml:46-50`:
```xml
<!-- Công nợ: UI-only (debt build lại theo ADR-007) → Home. -->
<a href="/portal"> … <span class="menu-title">Công nợ</span></a>
```
Vuexy `app-menu.js` đánh dấu active bằng cách so `href` với URL hiện tại → ở `/portal`,
cả "Trang chủ" lẫn "Công nợ" cùng khớp. Đo xác nhận: `/portal` → active = `["Trang chủ", "Công nợ"]`;
4 route khác (`/order`, `/delivery`, `/notification`, `/profile`) đều **chỉ 1 mục** → đúng như BA ghi.

**Chú thích trong code đã lỗi thời:** module `wujia_portal_debt` **đã tồn tại** (Sprint 43 + 48),
route `/portal/debt` chạy được. Nhưng trang mới chỉ có **bản mobile** (BA chưa vẽ Figma PC),
mở ở 1920 sẽ ra một cột hẹp ~391px căn giữa.

**Quyết định chủ dự án (02/08):** hỏi BA về việc bật link.
**Phần làm được ngay, độc lập:** sửa logic active để `/portal` chỉ sáng "Trang chủ"
(gắn active theo `request.httprequest.path` khớp chính xác thay vì để Vuexy tự dò href).

### RESP-MOB-ORDER-001 — mâu thuẫn nội bộ trong dòng issue
- Cột N `Need BA Confirm` = **No**, cột I = `Ready for Dev`, cột O = **BA/Tester**
- Cột "Đề xuất" ghi **BA đã chốt 22/07 phương án B**: tên tối đa **2 dòng** (line-clamp 2), card cao ~92px
- Nhưng cột K vẫn còn ghi `LIMIT: Need BA Confirm=Yes — BA chưa chốt số dòng clamp` (ghi chú cũ chưa xoá)

→ Chỉ cần **1 câu xác nhận** rồi gộp việc vào **cụm C** (mobile shell). Không cần issue mới.

---

## 5. Danh sách câu hỏi gửi BA — gửi MỘT LẦN

> Theo bài học L6: bỏ tên field/thuật ngữ, kể bằng thao tác thật, gom về câu hỏi nghiệp vụ.

1. **Logo mobile (UI-MOB-SHELL-001):** logo hiện dùng chung với logo công ty nên bị co lại còn ~64px ngang
   thay vì 100px. Anh/chị gửi giúp **file logo riêng cho mobile, tỉ lệ khoảng 100×34** được không?
   Chưa có file thì chưa sửa được.

2. **Lịch sử đặt hàng — trạng thái (WJ-PH-003):** Odoo chỉ ghi trên đơn hàng 3 nấc
   *Chờ xác nhận / Đã gửi / Đã xác nhận*. **"Đang giao" và "Hoàn tất"** nằm ở **chuyến giao hàng**, không nằm trên đơn.
   Anh/chị muốn: (a) ghép hai nguồn lại thành một cột trạng thái duy nhất, hay
   (b) giữ cột "Chuyến giao" riêng như hiện nay và bỏ 2 trạng thái đó khỏi bộ lọc?
   Thêm nữa: **"đơn hủy do bị thay thế"** hiện hệ thống không phân biệt được với đơn hủy thường —
   anh/chị có muốn thêm chỗ ghi lý do hủy không?

3. **Menu "Công nợ" bản PC (UI-PC-BASE-012):** trang Công nợ hiện **chỉ có bản mobile**; mở trên màn hình
   máy tính sẽ thấy một cột hẹp căn giữa, hai bên trống. Anh/chị muốn bật menu Công nợ trên PC luôn
   (chấp nhận tạm như vậy), hay chờ có thiết kế PC rồi mới bật?
   *(Phần lỗi "sáng 2 mục cùng lúc" chúng tôi sửa ngay, không phụ thuộc câu trả lời này.)*

4. **Cờ ngôn ngữ (UI-02):** ô ngôn ngữ hiển thị theo **ngôn ngữ của chính tài khoản đang đăng nhập**.
   Kiểm tra ngày 02/08 trên 6 màn đều ra **cờ Việt Nam + "Việt Nam"**.
   Nhờ anh/chị xem lại tài khoản dùng để test — có đang để English không?
   Và có muốn đặt mặc định **tiếng Việt** cho tất cả tài khoản cửa hàng không?

5. **Tên sản phẩm trên mobile (RESP-MOB-ORDER-001):** xác nhận lại giúp phương án đã chốt 22/07 —
   tên hiển thị **tối đa 2 dòng**, thẻ sản phẩm cao cố định ~92px, dài hơn thì cắt bằng dấu "…". Đúng chứ ạ?

6. **Màu nút chính (WJ-ORD-012, tồn từ S43):** Figma vẽ nút xanh `#28A9DF` chữ trắng — độ tương phản 2.68:1,
   dưới mức đọc an toàn 4.5:1 (chính là lỗi a11y anh/chị mở ở Sprint 38). Chúng tôi đang dùng xanh đậm hơn
   `#0F7CA8`. Anh/chị confirm giữ `#0F7CA8` hay đổi Figma?

7. **Lịch sử — người đặt (WJ-PH-006):** code đã chạy đúng rule 2 nhánh anh/chị chốt 30/07.
   Nhờ anh/chị cập nhật **CT-025** trên Master Sheet cho khớp (hiện chỉ ghi nhánh đơn Portal).

---

## 6. Việc Dev làm trong cụm này

| Việc | Issue |
|---|---|
| Sửa logic active sidebar (chỉ 1 mục sáng mỗi route) | UI-PC-BASE-012 *(phần sửa được)* |
| Chụp evidence + đẩy `Ready for Retest` | FUNC-MOB-ORDER-006 |
| Nhắc BA retest (Owner đã là BA/Tester) | RESP-MOB-ORDER-003 |
| Chuyển `Need Clarification`, owner BA | WJ-PH-003 |
| Giữ nguyên, ghi rõ đang chờ asset | UI-MOB-SHELL-001 |
| Gửi 7 câu hỏi trên trong **một** lần | — |

⚠️ **Không** tự sửa nội dung cột A–H của BA. Thắc mắc thì ghi ở cột K + thêm dòng History
(QA Standard §3) — đây chính là lỗi Dev đã mắc ngày 31/07, xem `docs/next-session-tasks-notification.md` §0.
