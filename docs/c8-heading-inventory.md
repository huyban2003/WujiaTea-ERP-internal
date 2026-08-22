# C8 — Kiểm kê & phân loại heading portal (`UI-SECTIONHEADER-001`, STT 83)

**Ngày:** 2026-08-22 · **Branch:** `dev/2026-08-22-c8` · **Cơ sở:** `75fa97d`

Bước 1 của cụm C8 theo spec `CMP-SH-001` (tab `UI Component` gid 488333015 dòng 33, Status
BA Confirmed). Chân lý phân loại là **ngữ cảnh DOM (tổ tiên)**, không phải tên class — kiểm kê
bằng lxml đi ngược cây tìm ancestor `card` / `modal` / `empty-state`.

---

## 1. Phạm vi

`custom/wujia_portal_*/views/*.xml` — **183 heading** thô. Loại trừ trước:

| Loại trừ | Lý do |
|---|---|
| `*_backend_views.xml` | Backend Odoo, không phải portal |
| `wujia_portal_layout/views/pc_preview.xml` | Trang demo nội bộ |
| `login_page.xml` · `forgot_pass.xml` · `change_password_page.xml` · `profile_page.xml` | Auth (`CMP-*` chưa phủ, S39 dựng riêng) |
| `wujia_portal_inspection` · `wujia_portal_remediation` | Merge `thai` 19/08, **chưa deploy UAT** → để C8b (đã kiểm kê ở §6) |

Còn **132 heading / 22 file** đưa vào phân loại.

## 2. Kết quả phân loại

| Loại | Số lượng | Xử lý |
|---|---:|---|
| **SectionHeader** | **13** | ✅ Trong scope C8 (12 khi kiểm kê C8a + 1 chỗ sót, xem §2d) |
| CardHeader | 89 | ❌ Spec nói rõ: heading nằm trong card **KHÔNG** phải SectionHeader |
| PageHeader | 3 | ❌ Đã có `CMP-PG-001` (B3a/B3b) |
| Khác (EmptyState / Modal / DetailSummary) | 24 | ❌ Thuộc `CMP-ES-001` / `CMP-DS-001`, BA chưa viết spec |

Cộng thêm **5 call site KHÔNG phải heading thật** (đang là `<div>` + `<span>`) — chính là
triệu chứng BA mô tả trong issue, cộng `portal_delivery.xml:15` được BA promote ở §2c
⇒ tổng **19 call site** trong scope (18 khi chốt C8a, +1 chỗ sót phát hiện ở C8b — §2d).

### 2a. SectionHeader — heading thật (13)

| File | Dòng | Tag | Class hiện tại | Nội dung |
|---|---:|---|---|---|
| `wujia_portal_base/views/portal_home.xml` | 313 | h3 | `wujia-mhome-section-title` | Hành động nhanh |
| ″ | 345 | h3 | `wujia-mhome-section-title` | Thông báo nổi bật |
| ″ | 385 | h2 | `wujia-mdash-title` | Giao hàng sắp tới |
| ″ | 419 | h2 | `wujia-mdash-title` | Đơn hàng gần đây |
| ″ | 452 | h2 | `wujia-mdash-title` | Bài viết / Kiến thức mới |
| ″ | 479 | h2 | `wujia-mdash-title` | Yêu cầu đổi trả gần đây |
| ″ | 514 | h2 | `wujia-mdash-title` | Hỗ trợ nhanh |
| ″ | 544 | h2 | `wujia-mdash-title` | Thông tin cửa hàng |
| `wujia_portal_debt/views/portal_debt.xml` | 209 | h2 | `wj-debt-section__title` | Hóa đơn còn số dư / trong tuần |
| ″ | 512 | h2 | `wj-debt-section__title` | Các khoản thanh toán |
| ″ | 688 | h2 | `wj-debt-bank__title` | THÔNG TIN CHUYỂN KHOẢN (ca dung hoà — §2e) |
| `wujia_portal_exam/views/portal_exam.xml` | 759 | h2 | `wujia-mexam-sectitle` | Danh sách nhân sự (**sót ở C8a** — §2d) |
| ″ | 1036 | h2 | `wujia-mexam-sectitle` | Danh sách nhân sự |

### 2b. SectionHeader — chưa là heading thật (5) ⚠️ đúng ca BA than

Spec: *"Title là heading THẬT (không `<span>`)"*. Cả 5 chỗ đang là `<div>` bọc `<span>`:

| File | Dòng | Hiện trạng | Ghi chú |
|---|---:|---|---|
| `wujia_portal_sale/views/portal_order_catalog.xml` | 114 | `div.wujia-morder-listhead` > `span` | **mobile** — count viết tắt **"N SP"**, spec cấm |
| ″ | 17 | `div.wj-pc-order-cardhead` > `h3.wj-pc-order-cardtitle` | **PC** — count "N sản phẩm" |
| `wujia_portal_sale/views/portal_order_cart.xml` | 47 | `div.wujia-mcart-listhead` > `span` (không class) | count "N mặt hàng" |
| `wujia_portal_purchase_history/views/portal_history.xml` | 129 | `div.wujia-mhist-listhead` > `span` | count "N đơn gần nhất" |
| `wujia_portal_return/views/portal_return_list.xml` | 189 | `div.wujia-mhist-listhead` > `span` | count "N yêu cầu" |

Cặp `portal_order_catalog.xml:17` (PC, H3) ↔ `:114` (mobile, SPAN) **chính là ví dụ BA viết
trong issue**: *"/portal/order PC dùng H3 18px/700, mobile dùng SPAN 15px/700"*.

### 2c. ⚠️ Diễn giải cần BA xác nhận — "list-container card head"

Spec viết *"Heading nằm trong card = CardHeader, không phải SectionHeader"*. Nhưng BA **tự
chỉ đích danh** hai chỗ nằm trong card và gọi chúng là SectionHeader:

- `/portal/delivery` "Danh sách chuyến giao" (`portal_delivery.xml:15`, trong `div.wj-pc-card`)
  — spec ghi rõ *dùng variant `meta`*.
- `/portal/order` PC (`portal_order_catalog.xml:17`, trong `div.wj-pc-card.wj-pc-order-card`)
  — issue lấy làm ví dụ đối chiếu với mobile.

⇒ **Diễn giải Dev:** card **bao trọn danh sách của trang** (list container) thì đầu card là
SectionHeader; card **là một mẩu nội dung trong trang** (KPI, thông tin vận chuyển, sản phẩm
trong chuyến…) thì đầu card là CardHeader. Áp diễn giải này, `portal_delivery.xml:15` và
`portal_order_catalog.xml:15` vào scope ⇒ **18 call site**. Ghi LIMIT, nhờ BA xác nhận khi retest.

### 2d. ⚠️ Chỗ SÓT của kiểm kê C8a — `portal_exam.xml:759` (phát hiện ở C8b)

Chữ "Danh sách nhân sự" xuất hiện **2 lần** trong `portal_exam.xml`, cùng thẻ `<h2>`, cùng
class `wujia-mexam-sectitle`: dòng **759** (bước 3 wizard tạo đăng ký) và **1036** (trang chi
tiết đăng ký). Bảng §3 của C8a ghi `portal_exam.xml` Sec=**1** — script kiểm kê gộp hai dòng
trùng (class + text giống hệt) làm một.

Soi tay chuỗi tổ tiên của :759 ⇒ `section.wujia-mexam-panel` › `div.d-lg-none.wujia-mpage
.wujia-mexam-wizard`. `.wujia-mexam-panel` là **flex column không nền, không bo góc, không
padding** ⇒ đúng phép thử tổ tiên DOM thì đây là SectionHeader thật, y hệt :1036.

Chủ dự án chốt 23/08: **đưa vào scope** ⇒ tổng **19 call site**. Bỏ nó lại thì hai dòng chữ
y hệt nhau render hai cỡ khác nhau (16px ở wizard vs 20px ở chi tiết) — đúng loại lỗi issue
này đang đòi dẹp. Đo sau khi migrate: cả hai đều `20px`.

### 2e. Ca dung hoà — `portal_debt.xml:688` "THÔNG TIN CHUYỂN KHOẢN"

Đo CSS: `.wj-debt-bank` có `background` + `border-radius` + `padding` + **`height: 150px` cố
định** ⇒ theo **chính phép thử tổ tiên DOM** đã hạ `portal_home.xml:292` xuống CardHeader thì
dòng này cũng là CardHeader. Bản thân nó là nhãn `11px` + `letter-spacing` viết hoa gõ tay,
không phải tiêu đề khối.

Chủ dự án chốt 23/08 — **dung hoà**: vẫn chuyển sang component (thành heading thật, đi qua một
khuôn duy nhất, chịu rule "tối đa MỘT right slot"), nhưng tắt nhịp bằng modifier `--flush` và
giữ dáng nhãn bằng **CSS scope trong `portal_debt.css`** (`.wj-debt-bank .wj-section-header*`),
KHÔNG đẻ modifier trong `_components.css` dùng chung. Đo sau khi migrate: `H2`, `11px`, thẻ
vẫn cao đúng **150px**, nội dung không tràn. BA chốt sau chỉ cần gỡ khối CSS scope đó.
👉 **Cần BA xác nhận** đây là CardHeader (gỡ khỏi scope) hay SectionHeader thật (nới chiều cao thẻ).

## 3. Phân bố theo file (132 heading)

| File | Sec | Card | Page | Khác |
|---|---:|---:|---:|---:|
| `wujia_portal_base/views/portal_home.xml` | 8* | 5 | 0 | 0 |
| `wujia_portal_debt/views/portal_debt.xml` | 3 | 3 | 0 | 5 |
| `wujia_portal_base/views/portal_franchises_in_layout.xml` | 2* | 1 | 0 | 0 |
| `wujia_portal_exam/views/portal_exam.xml` | 1 | 19 | 2 | 5 |
| `wujia_portal_base/views/portal_franchise_information.xml` | 1* | 7 | 0 | 2 |
| `wujia_portal_base/views/portal_templates.xml` | 1* | 1 | 0 | 0 |
| `wujia_portal_delivery/views/portal_delivery.xml` | 0 | 6 | 0 | 2 |
| `wujia_portal_notification/views/portal_notification.xml` | 0 | 6 | 0 | 2 |
| `wujia_portal_report/views/portal_report_orders.xml` | 0 | 6 | 0 | 1 |
| `wujia_portal_support/views/portal_support.xml` | 0 | 6 | 0 | 0 |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 0 | 5 | 0 | 2 |
| `wujia_portal_return/views/portal_return_detail.xml` | 0 | 9 | 0 | 0 |
| `wujia_portal_purchase_history/views/portal_history.xml` | 0 | 4 | 0 | 4 |
| `wujia_portal_base/views/portal_franchise_profile.xml` | 0 | 4 | 0 | 0 |
| `wujia_portal_sale/*` (4 file) | 0 | 5 | 0 | 0 |
| `wujia_portal_info_request` · `wujia_portal_layout` · `wujia_portal_notification/header_bell` | 0 | 1 | 1 | 1 |

`*` = classifier đánh SectionHeader nhưng **soi tay ⇒ loại**:

- `portal_franchises_in_layout.xml:25,88` + `portal_templates.xml:90` — `content-header-title`
  là **tiêu đề TRANG** (boilerplate Vuexy `content-header`), thuộc `CMP-PG-001`. Ngoài ra
  `/my/franchises*` là route **legacy Odoo `portal.portal_layout`** mà ADR-004 đã thay bằng
  portal Vuexy ⇒ ngoài scope hẳn.
- `portal_franchise_information.xml:40` — `wj-pc-acct-headcard__title` nằm trong
  `div.wj-pc-acct-headcard` ⇒ **CardHeader**.
- `portal_home.xml:292` — `wujia-mhome-window-title` nằm trong `section.wujia-mhome-window`,
  mà `_components.css:995` cho khối này `background` + `border` + `border-radius:14px` +
  `padding` ⇒ **là card thật** ⇒ **CardHeader**. (Ngược lại `.wujia-mdash-sec` chỉ là flex
  column không nền — card `.wujia-mdash-card` nằm BÊN TRONG, sau tiêu đề ⇒ tiêu đề đứng
  ngoài card ⇒ SectionHeader.)

## 4. Ranh giới C8a ↔ C8b

**C8a (phiên 22/08)** — component + 5 route mẫu, phủ **13/18** call site:

| Route | File | Call site |
|---|---|---:|
| `/portal` mobile | `portal_home.xml` | 8 |
| `/portal/delivery` PC | `portal_delivery.xml` | 1 |
| `/portal/order` PC + mobile | `portal_order_catalog.xml` | 2 |
| `/portal/purchase-history` | `portal_history.xml` | 1 |
| `/portal/order/cart` | `portal_order_cart.xml` | 1 |

**C8b (phiên 23/08)** ✅ — **6 call site** còn lại ⇒ đủ **19/19**:

| File | Dòng | Đã làm |
|---|---:|---|
| `wujia_portal_debt/views/portal_debt.xml` | 209 | Right slot có điều kiện: `sh_action_url` khi còn hoá đơn ẩn, không thì `sh_meta` count ⇒ component tự ép "tối đa MỘT" |
| ″ | 512 | Nằm trong slot `#wj-debt-hist-mbody` của `wj_ajax_list` (swap cả khối) |
| ″ | 688 | Ca dung hoà §2e — component + `--flush` + dáng nhãn scope ở `portal_debt.css` |
| `wujia_portal_exam/views/portal_exam.xml` | 759 | Chỗ C8a sót (§2d) |
| ″ | 1036 | |
| `wujia_portal_return/views/portal_return_list.xml` | 189 | Xong chỗ này mới xoá `.wujia-mhist-listhead*` |
| `wujia_portal_inspection` | — | Kiểm kê §6 ⇒ **0 call site chắc chắn**, 1 chỗ chờ BA |
| ~~`wujia_portal_remediation`~~ | — | **Cố ý bỏ ngoài**: anh Thái đã xoá code (`f789a56`), UAT `uninstalled` |

⚠️ **Ràng buộc thứ tự (đã thoả):** `wujia-mhist-listhead` dùng ở **2 file**
(`portal_history.xml:129` và `portal_return_list.xml:189`). C8a chỉ chuyển history nên phải
giữ CSS; C8b chuyển nốt return rồi mới xoá `.wujia-mhist-listhead*` khỏi `_components.css`.
Cùng lượt xoá `.wj-debt-section*` (`portal_debt.css`) và `.wujia-mexam-sectitle`
(`portal_exam.css`) — grep xác nhận 0 hit trước khi xoá, có unit test chống tái phát.

## 5. Cách tái lập

Script kiểm kê: `scratchpad/c8_inventory.py` (harness, **không** commit vào repo theo §13).

## 6. Kiểm kê `wujia_portal_inspection` (bổ sung ở C8b)

Module giám sát/chấm điểm cửa hàng của anh Thái **đã installed trên UAT 22/08** ⇒ nay thuộc
phạm vi. Soi bằng lxml theo tổ tiên DOM, 4 file template (bỏ `sidenav_inherit.xml`):

| Loại | Số | Ghi chú |
|---|---:|---|
| PageHeader `wj-pc-page-header__title` | 3 | Thuộc `CMP-PG-001`, ngoài scope C8 |
| CardHeader (trong `.wj-pc-card` / trang success) | 12 | Ngoài scope theo spec |
| **Lửng lơ — chờ BA** | **1** | `portal_inspection_list_templates.xml:34` "Danh sách phiếu khảo sát" |

Khối mobile (`d-lg-none`, `list:143`) chỉ có ô tìm kiếm + danh sách, **không có** section head.

⚠️ Chỗ lửng lơ nằm trong `.wj-pc-card__head` — **cấu trúc giống hệt** `/portal/delivery`
"Danh sách chuyến giao" mà BA tự chỉ đích danh là SectionHeader (§2c). Tức là nó rơi đúng vào
**LIMIT-2 đang chờ BA trả lời**. Chủ dự án chốt 23/08: **để lại, không migrate**, ghi
`Need Clarification`; BA trả lời câu 2 xong mới áp. Vẫn `-u` module này trong lượt nghiệm thu
để chứng minh việc xoá CSS dùng chung không làm vỡ nó.
