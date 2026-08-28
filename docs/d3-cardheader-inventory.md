# D3 — Kiểm kê & phân loại heading TRONG CARD (`UI-CARDHEADER-001`, STT 125)

**Ngày:** 2026-08-27 · **Branch:** `dev/2026-08-27-d3a` · **Cơ sở:** `9fd35de`

Bước 1 của cụm D3 theo spec `CMP-CH-001` (tab `UI Component` gid 488333015, dòng 34). Chân lý
phân loại vẫn là **ngữ cảnh DOM (tổ tiên)**, không phải tên class — y hệt C8, kiểm kê bằng lxml
đi ngược cây tìm ancestor là **card thật**.

**"Là card"** = có class nào đó khai trong CSS đủ cả ba: `background` + `border*` + `padding`.
Đây đúng phép thử C8 đã dùng để hạ `portal_home.xml:292` xuống CardHeader và giữ
`.wujia-mdash-sec` là SectionHeader.

**Khác C8 một điểm quan trọng:** C8 chỉ quét `h1..h6` (+5 chỗ `div>span` giả heading). D3 phải
quét **cả `<p>/<span>/<div>` đang đóng vai tiêu đề card** — chính là ca BA nêu đích danh trong
issue (*"Form bù hàng mobile dùng `wujia-mdash-title` 18px nhưng markup là thẻ P"*).

---

## 1. Phạm vi

`custom/wujia_portal_*/views/*.xml` + `templates/*.xml`. Loại trừ trước khi phân loại:

| Loại trừ | Lý do |
|---|---|
| `*_backend_views.xml` | Backend Odoo, không phải portal |
| `wujia_portal_layout/views/pc_preview.xml` | Trang demo nội bộ |
| `login_page` · `forgot_pass` · `change_password_page` · `profile_page` | Auth, S39 dựng riêng (giữ ranh giới C8) |
| `wj_ks_dashboard_ninja` · `wj_ks_dn_advance` | Workstream Dashboard riêng (`dashboard-migration-plan.md`) |
| `wujia_portal_remediation` | Code đã xoá (`f789a56`), UAT `uninstalled` |

**Loại trừ theo VAI TRÒ** (91 chỗ) — không phải tiêu đề của card mà là nội dung/nhãn trong thân
card, hoặc thuộc component khác: `*__label` / `form-label` / `*-kv-*` (cặp nhãn–giá trị) ·
`*empty*` / `*modal*` (thuộc `CMP-ES-001` và spec modal, BA chưa viết) · `*-row` / `*-item` /
`*-line` (tiêu đề MỘT bản ghi trong danh sách ⇒ việc của `CMP-DL-001`, cụm D5) · `*chip` /
`*badge` / `*nav-*` · `wj-page-header*` / `wj-section-header*` (**component đã chuẩn hoá xong**
ở B3a/B3b và C8a/C8b — không đụng lại) · `*-link` / `*__actions` (slot phải, không phải title).

## 2. Kết quả

| | Số |
|---|---:|
| Ứng viên tiêu đề nằm trong card | 218 |
| − loại theo vai trò (§1) | 91 |
| **= CardHeader (máy)** | **127** |
| − loại bằng soi tay (§3) | 23 |
| **= call site trong scope D3** | **104** |
| ↳ gộp 1 chỗ subtitle vào header cùng card (§4) | **103 call site thật** |

Trong 127 chỗ máy nhận: **96 là heading thật**, **31 là giả heading** (`<p>` / `<span>` /
`<div>` có chữ trực tiếp) — con số 31 này chính là triệu chứng BA mô tả.

Chia theo vị trí trong card:

| | Số | Nghĩa |
|---|---:|---|
| **A. Đầu card** | 112 | Là header của chính card đó |
| **B. Giữa card** | 15 | Tiêu đề khối con nằm sâu trong card |

> ⚠️ **Không lấy "phải ở đầu card" làm điều kiện loại.** Ranh giới spec chỉ có hai vế: trong
> card ⇒ CardHeader, ngoài card ⇒ SectionHeader. Bản kiểm kê đầu tiên của phiên này đã lỡ dùng
> "phải là con đầu tiên" và **rơi mất 31 chỗ hợp lệ**, trong đó có
> `wj-pc-acct-headcard__title` (nằm trong wrapper `__main`, sau `__icon`). Vị trí A/B chỉ dùng
> để **xếp thứ tự migrate**, không dùng để loại.

## 3. Loại bằng soi tay (23 chỗ)

| File · dòng | Hiện trạng | Vì sao KHÔNG phải CardHeader |
|---|---|---|
| `portal_franchises_in_layout.xml:106` · `portal_templates.xml:108` | `h4/h5.card-title` | Route legacy `/my/franchises` — ADR-004 đã thay bằng portal Vuexy (C8 cũng loại) |
| `layouts.xml:187` | `span.menu-title` | Nhãn sidebar — thuộc `UI-SIDEBAR-001` (lứa D7) |
| `mobile_bottomnav.xml:58` | `div.wujia-msheet-title` | Bottom sheet là overlay, không phải SurfaceCard |
| `header_bell_inherit.xml:22` | `h4.wj-pc-noti-popup__title` | Popup chuông là dropdown, không phải card trong trang |
| `portal_delivery.xml:118, 126` | `h3.wj-pc-dlv-inner__title` | Empty / error state ⇒ `CMP-ES-001` |
| `portal_franchise_information.xml:267` | `h4` trong `.card-body` | Trạng thái khoá cửa hàng ⇒ `CMP-ES-001` |
| `portal_inspection_success_templates.xml:13` | `h2` | Màn kết quả gửi — hero của trang, không phải header card |
| `portal_order_cart.xml:196` | `p.wujia-msubmit-title` | Overlay "Đang tạo đơn…" (S40), không phải card |
| `portal_order_catalog.xml:350` | `span.wujia-morder-floatbar-title` | Thanh giỏ nổi, không phải card |
| `portal_exam.xml:279` | `div.wj-exam-pc-cal__head` | Chỉ có nút `‹ ›`, **không có title** ⇒ không có gì để chuẩn hoá |
| `portal_exam.xml:378` · `portal_history.xml:395` | `__side` / `__right` | Là **slot phải** của header, không phải title |
| `portal_exam.xml:521, 527` | `__title` / `__droptitle` | Chữ trạng thái của vùng kéo-thả ảnh |
| `portal_franchise_information.xml:49` | `div.wj-pc-acct-headcard__box` | Là slot phải — xem **§6 Fork** |
| `portal_knowledge.xml:287, 337` | `h1` tiêu đề bài viết | **Nội dung**, không phải header card — cùng luật BA cấm dùng CardHeader cho tên sản phẩm |
| `portal_notification.xml:364, 448` | `h2` tiêu đề thông báo | ″ |
| `portal_order_product_detail.xml:34` | `h3` tên sản phẩm | ″ — BA ghi thẳng: *"Không dùng CardHeader cho tên sản phẩm"* |
| `portal_order_result.xml:25` | `h2.wujia-mres-title` | *(thêm ở D3b)* Màn kết quả gửi đơn — **hero của trang**, không phải header card; đúng tiền lệ `portal_inspection_success_templates.xml:13` ngay trên |

## 4. Map về 7 nhóm MAPPING của BA

| Nhóm BA | Call site | Nơi tiêu biểu |
|---|---:|---|
| **List/content card** | 38 | `wj-pc-card__title` (23) — danh sách thông báo/đơn/hoá đơn/chuyến · `wujia-content-card-header-title` (8) |
| **FormCard** | 27 | `card-title mb-0` + `h5/h6.mb-0` trong `.card-header` (support, return detail, franchise profile) · `wujia-mdash-title` dạng `<p>` (return form, support) |
| **Dashboard card** | 14 | `wujia-content-card-header-title` ở Home · `wujia-mhist-card-head` |
| **Summary/StatCard** | 12 | `wj-debt-summary__head` · `wj-pc-order-head__code` · `wujia-mexam-rsum-title` · report orders |
| **Cart** | 1 | `wj-pc-cart-title` "Giỏ hàng" (`pc_cart_panel.xml:12`) |
| **FilterCard** | 0 | ⚠️ **Chưa có chỗ nào** — đúng như BA viết: *"FilterCard PC/mobile hiện đưa control trực tiếp vào card, không có header"*. Đây là việc **THÊM MỚI**, không phải migrate |
| **Card nhỏ — không bắt buộc** | 12 | `wj-debt-hint__title` · `wj-exam-pc-slots__title` · `wujia-mexam-person-head`… |

**Chỗ subtitle đã gộp:** `portal_franchise_information.xml:187` (`h3.wujia-maccount-store-name`)
nằm cùng card với `:181` ⇒ là **subtitle của header đó**, không phải call site riêng ⇒ 104 → 103.

## 5. Phân bố theo file — kế hoạch chia D3b…D3n

| File | Call site | Dự kiến |
|---|---:|---|
| `wujia_portal_exam/views/portal_exam.xml` | 21 | D3d (một mình một session) |
| `wujia_portal_return/views/portal_return_detail.xml` | 15 | D3e |
| `wujia_portal_purchase_history/views/portal_history.xml` | 10 | D3e |
| `wujia_portal_base/views/portal_franchise_information.xml` | 10 | **D3a (mẫu 3)** — 2 xong, **6 còn → D3c** |
| `wujia_portal_delivery/views/portal_delivery.xml` | 8 | **D3a (mẫu 2)** — 3 xong, **3 còn → D3c** |
| `wujia_portal_notification/views/portal_notification.xml` | 7 | **D3b ✅** (5 chỗ; 2 chỗ còn lại là §3 tiêu đề thông báo) |
| `wujia_portal_support/views/portal_support.xml` | 7 | **D3a (mẫu 1)** — 1 xong, **6 còn → D3c** |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 7 | **D3b ✅** (5 chỗ; 2 chỗ còn lại là §3 tiêu đề bài viết) |
| `wujia_portal_base/views/portal_home.xml` | 5 | **D3b ✅** |
| `wujia_portal_debt/views/portal_debt.xml` | 5 | D3f (đụng số đo S43/C3 — cẩn thận) |
| `wujia_portal_base/views/portal_franchise_profile.xml` | 4 | **D3b ✅** |
| `wujia_portal_inspection/*` (4 file) | 9 | D3f (xem §6) |
| `wujia_portal_return/views/portal_return_form.xml` | 4 | **D3a (mẫu 4)** — 4 xong ✅ |
| `wujia_portal_report/views/portal_report_orders.xml` | 3 | **D3b ✅** |
| `wujia_portal_sale/*` (3 file) | 3 | **D3b ✅** (2 chỗ; `portal_order_result.xml` đã loại → §3) |
| Còn lại (`info_request`, `return_list`) | 2 | **D3b ✅** |

**D3a phủ 4 file / 29 call site** — nhưng cố ý **không migrate hết 4 file**, chỉ lấy đủ mẫu mỗi
họ markup (xem `docs/d3-acceptance-matrix.md`); phần còn lại của chính 4 file đó rơi vào **D3c**.

**Tiến độ (2026-08-28, sau D3b): 36/103.** D3a 10 · D3b 26.
Nhóm kế: **D3c = 15 chỗ còn lại của 4 file D3a** (support 6 · delivery 3 · franchise-information 6).

> ⚠️ Con số cột "Call site" là **tổng theo file**, gồm cả chỗ đã bị loại ở §3, nên cộng dồn
> ra 113 chứ không phải 103 — bám `scratchpad/d3_inventory.py` mới ra danh sách đúng.

## 6. Chỗ KHÔNG đụng — chờ BA (kế thừa LIMIT của C8, đừng quyết lại)

1. **`portal_delivery.xml:15` + `portal_order_catalog.xml:17`** — nằm trong `.wj-pc-card` ⇒ theo
   `CMP-CH-001` phải là CardHeader, **nhưng BA tự chỉ đích danh là SectionHeader** và C8a đã
   migrate sang `wj_section_header`. Đây là **LIMIT-2 đang treo**. Script đã tự bỏ qua wrapper
   nào chứa `t-call` tới `wj_section_header`.
2. **`portal_debt.xml:688`** "THÔNG TIN CHUYỂN KHOẢN" — nhãn 11px trong `.wj-debt-bank`
   (`height:150px` cố định). C8b dung hoà bằng `wj_section_header` + `--flush` + dáng nhãn scope
   trong `portal_debt.css`. BA **nêu lại đúng chỗ này** trong `CMP-CH-001` (*"Debt summary dùng
   label 11px viết hoa"*) ⇒ đây là **ứng viên số 1 để reclassify sang CardHeader**, nhưng phải
   chờ BA trả lời câu hỏi C8 rồi mới đổi.
3. **`portal_inspection_list_templates.xml:34`** "Danh sách phiếu khảo sát" — cùng họ với (1),
   C8b đã ghi `Need Clarification`.

**Fork mới của D3a — `wj-pc-acct-headcard` có HAI vùng phải.** `__chips` (trạng thái cửa hàng)
và `__box` (Quyền xem hiện tại), trong khi spec ghi **tối đa MỘT trailing**. D3a làm theo hướng
an toàn: **chips + box đứng ngoài CardHeader**, là nội dung card ⇒ giữ nguyên hiển thị, đúng
chữ spec, 0 rủi ro hồi quy. Đã ghi LIMIT; BA trả lời thì D3b chỉnh.

## 7. CSS chờ xoá (sau khi migrate đủ 100%)

**KHÔNG xoá ở D3a** — ràng buộc thứ tự y hệt C8a→C8b (`.wujia-mhist-listhead` dùng ở 2 file,
xoá sớm là vỡ). Danh sách phải grep ra 0 hit rồi mới xoá:

`.wujia-content-card-header*` · `.wj-pc-card__title` (+ `--sm`) · `.wujia-mdash-title` ·
`.wujia-mhist-card-head` · `.wujia-maccount-cardtitle` · `.wj-pc-acct-panel-title` ·
`.wj-pc-acct-staff__title` · `.wujia-mexam-*title` · `.wj-exam-pc-sectitle` ·
`.wj-pc-cart-title` · `.wujia-mknow-h` · `.wujia-mnoti-detail-sectitle` · `.wj-debt-summary__head`

Chống tái phát bằng unit test quét `arch_db` mọi view qweb — đúng khuôn
`test_retired_heading_classes_are_gone` của C8b.

## 8. Cách tái lập

Script: `scratchpad/d3_inventory.py` (harness, **không** commit vào repo theo §13).
`python3 scratchpad/d3_inventory.py [--out]` — `--out` in thêm 91 chỗ bị loại theo vai trò để
kiểm chứng bộ lọc không cắt nhầm.
