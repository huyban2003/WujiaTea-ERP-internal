# Cụm H — Rollout bộ component PC (pc_source_ui_v1.5)

**Issue:** UI-PC-BASE-002 · 003 · 004 · 005 · 006 · 007 · 008 · 009 · WJ-ORD-023
**Sev:** Low toàn bộ · **Rủi ro:** thấp mỗi issue, nhưng **lan rộng** (~10 trang nghiệp vụ)

> **Chạy sau cụm A.** Trước khi A xong, mọi toạ độ PC còn lệch +300/+12/+6.8px — đo sẽ ra số vô nghĩa.

---

## Tin tốt: component đã có sẵn, phần lớn chỉ là chỉnh token + thay class

`custom/wujia_portal_layout/static/assets/css/_pc_components.css` (387 dòng) đã có:

| Có sẵn | Dòng | Phục vụ issue |
|---|---|---|
| `.wj-pc-page-header` / `__title` / `__crumb` / `__actions` | 55–81 | 002, 007 |
| `.wj-pc-filterbar` / `__row` / `__grow` / `.wj-pc-filter-control` | 83–115 | 003, WJ-ORD-023 |
| `.wj-pc-badge` + 5 biến thể màu | 37–52 | 004 |
| `.wj-pc-pagination` / `__count` / `__size` / `.wj-pc-page-btn` | 195–238 | 005 |
| `.wj-pc-field` / `__label` / `.wj-pc-control` | 241–254 | 008 |
| `.wj-pc-btn` + `--primary/--secondary/--ghost/--danger` | 6–34 | 009 |

→ Việc chính là **áp component vào những trang còn dùng Bootstrap/legacy**, không phải viết mới.

---

## H1 — Chỉ token / CSS (làm trước, rẻ, ít rủi ro)

| Issue | Actual BA đo | Source v1.5 | Việc |
|---|---|---|---|
| **002** PageHeader | Dashboard 24/700 · Order/Purchase/Delivery/Notification/Knowledge 28/700 · Exam 30/700 | **30px / 800** | Sửa token title trong `wj_page_header` (`views/wj_page_header.xml` + CSS). Đây là component **dùng chung ~40 site/11 module** (rollout Sprint 33) → đổi 1 chỗ là đồng bộ hết. Variant chỉ khác breadcrumb/action, **không** khác typography. |
| **003** FilterBar | 113.6 / 100 / 80 / 89.6px | card **88px**, control 38–42px cùng hàng | Chuẩn hoá `.wj-pc-filterbar` + áp vào purchase-history, notification, delivery, exam |
| **004** Badge | `radius 999px`, w 53.6–78.1, h 26.8 | h **28**, radius **14**, **min-width 84**, padding 14–16, font 12–13/600 | Sửa `.wj-pc-badge`. ⚠️ đối chiếu `.wujia-badge-*` ở `_components.css` (mobile) — **đừng đổi nhầm sang mobile** |
| **008** FormField | select 33px · input 38.1px · radius 5.6 | **42px**, radius **10**, border `#E5E7EB`, label 14/600 | Áp `.wj-pc-field` + `.wj-pc-control` cho `/portal/support/new` |
| **009** FormActionBar | button rời, radius 8, weight 500, không separator | action bar cuối form, có separator, primary bên phải, button h40 radius12 weight 700–800 | Bọc action trong `.wj-pc-form-actions` (tạo mới nếu chưa có), dùng `.wj-pc-btn` |

**Blast radius H1:**
```bash
grep -rn "wj_page_header" custom/ --include=*.xml | wc -l      # số site dùng page header chung
grep -rn "wj-pc-badge\|wujia-badge" custom/ --include=*.xml --include=*.css
grep -rn "wj-pc-filterbar\|wj-pc-field\|wj-pc-control" custom/ --include=*.xml
```
⚠️ `wj_page_header` là component **toàn portal (PC + mobile)** — đổi typography PC phải chắc
biến thể `--m` (mobile) **không** đổi theo. Xem lại issue cũ RESP-MOB-SHELL-003 để không đẻ hồi quy dọc.

---

## H2 — Đổi cấu trúc template — ✅ XONG 04/08/2026

| Issue | Việc | Ghi chú |
|---|---|---|
| ~~**005** Pagination~~ | ✅ page-size selector 10/20/50 **submit thật** cho `/portal/purchase-history` + `/portal/notification` | ⚠️ **KHÔNG** copy `/portal/exam` như gợi ý ban đầu — selector ở đó nằm **ngoài** form và nút trang là `<span>` ⇒ UI tĩnh. Ẩn cả khối khi tổng ≤ **10** (option nhỏ nhất, không phải page size đang chọn) |
| ~~**006** BackButton~~ | ✅ "← Quay lại" **122×40** sửa **ở component** `wj_page_header` nhánh `--pc` → 13 màn đổi cùng lúc; gỡ 4 nút thừa | Mobile giữ icon 40×40 + vùng chạm 44 |
| ~~**007** Breadcrumb~~ | ✅ prop mới `ph_crumb` (nav riêng, chỉ PC) — gắn **cả 13 màn**, không chỉ 2 màn BA nêu | Giữ CẢ nút back (Navigation Rules v1.5) |
| ~~**WJ-ORD-023** FilterBar Đặt hàng~~ | ✅ **XONG 04/08/2026** — commit `63dc4bc`, đã deploy UAT | Nguyên nhân: `<select>` không khai `width` → ăn `select{width:100%}` + `padding:5px!important` của `dashboard.css` (tag-level, bẫy L4) nên wrap 3 hàng. Chữa bằng cách bỏ `.wj-pc-order-search/.wj-pc-order-cat` riêng, dùng khung chung `.wj-pc-filterbar` + `.wj-pc-filter-*`. Đo UAT: 3 control cùng `y`, cao 42, gap 12/12, card radius 16 (**cao 80 → 88 khi H1-003 deploy**), `category_id=2` ra đúng 2 SP, mobile trùng byte |
| **WJ-PH-004** | *(bỏ cột "Thao tác")* — **làm ở cụm E** cho gọn | |

**Điểm dễ sai H2:** `WJ-ORD-023` và `UI-PC-BASE-003` là **hai FilterBar khác nhau**
(BA đã ghi rõ "Đã loại trùng WJ-ORD-023"). Làm 003 trước cho chuẩn khung, rồi WJ-ORD-023 chỉ là áp khung đó vào trang Đặt hàng.

---

## Verify (chung cả H1 + H2)

Đo tại 1920×1080 trên ≥6 trang: `/portal`, `/portal/order`, `/portal/purchase-history`,
`/portal/notification`, `/portal/delivery`, `/portal/exam`, `/portal/support/new`, `/portal/order/product/<id>`.

| Kiểm | Expected |
|---|---|
| Title mọi trang | Inter **30px / 800**, cùng trục, cùng nhịp dọc |
| FilterBar mọi trang list | cao **88px**, control cùng hàng, cùng radius/border |
| Badge | h **28**, radius **14**, min-width **84**, không oval |
| Pagination | purchase-history + notification có page-size selector, style khớp exam |
| BackButton | "← Quay lại" **122×40**, có chữ |
| Breadcrumb | có ở màn create/detail, đúng đường dẫn nghiệp vụ |
| FormField | input/select **42px**, radius **10** |
| FormActionBar | có separator, primary bên phải |
| WJ-ORD-023 | search + danh mục + Tìm **một hàng**; chọn Topping → Tìm → `category_id=2`, dropdown giữ selected, ra đúng 2 sản phẩm |

Regression bắt buộc: mobile 391×844 **bất biến** ở đủ 9 route (component dùng chung!), overflow ngang = 0.

## Ghi sheet

9 issue → 9 dòng History riêng, nhưng có thể **cùng một Build/Deploy marker**.
Mẫu cột K (ví dụ 002):
`FIX: chuẩn hoá PageHeader PC về Inter 30/800 dùng chung wj_page_header | IMPACT: mọi trang PC dùng page header chung (~40 site) + kiểm biến thể mobile không đổi | RETEST: 1920×1080 đo title 6 trang đại diện đều 30/800; 391×844 mobile không đổi | LIMIT: Không có`

R: `Custom` cho toàn bộ.

---

## Kết quả H1 (2026-08-04, commit `c25a06b`) — 0 FAIL

Đo trên **DB copy cô lập `wujia_tea_h1`** (cổng 8032, KHÔNG đụng `wujia_tea_19`/8019 và không đụng
các DB copy của phiên khác đang chạy). Build `-u` 6 module: **RC=0, 0 ERROR/Traceback**.
Harness: `h1_check.py` (đo) + `h1_func.py` (submit thật) — scratchpad, gitignored.

**3 quyết định chủ dự án chốt đầu phiên:** Dashboard đổi sang component chung · ép FilterBar 88px
cả 4 trang (bỏ tiêu đề + nhãn field) · 008/009 chỉ làm `/portal/support/new`.

**002** — có **ba** hệ tiêu đề PC chứ không phải một: `wj-page-header--pc` (~9 trang, 28/700),
`wj-pc-page-header__title` (exam, 30/700) và `h2.content-header-title` của Vuexy (Dashboard, 24/700).
Gom về 30/800 ở hai rule component + đổi Dashboard sang `t-call wj_page_header`.
⚠️ Bẫy đã dính: đặt `font-weight: 800` KHÔNG có `!important` thì computed vẫn ra **700** —
`_wujia_theme.css` có `.content-wrapper h1 { font-weight: 700 !important }` ở tag-level (đúng kiểu L4).
Phải soi cascade bằng `document.styleSheets` mới thấy; nhìn ảnh không phân biệt được 700 với 800.
Đo lại: 8/8 trang PC ra **30px/800**; mobile `--m` vẫn **22px/700** ở đủ 9 route.

**003** — cả 4 trang vốn đã dùng `.wj-pc-filterbar`, chênh lệch chiều cao đến từ **nội dung thêm**:
dòng "Bộ lọc nhanh" (history, exam) và nhãn trên từng field (notification, Figma 4683:101).
Bỏ hai thứ đó, control lên 42px, padding 22 ⇒ **88px**. ⚠️ `box-sizing: border-box` vẫn **cộng
border**: 23+42+23 ra 90 chứ không phải 88 — phải trừ 1px viền mỗi cạnh.
Nhãn notification chuyển thành `aria-label` + option đầu mang tên field, không mất nghĩa cho screen reader.
Đo: 4/4 trang **h=88**, control cùng `y`, cùng `height=42`.

**004** — sửa thẳng rule `.wj-pc-badge` (radius 14, min-width 84), **không** đụng token
`--wj-pc-pill-radius` vì chip tròn của delivery/exam đang dùng chung token đó.
Miễn trừ tường minh (L7): exam giữ `min-width:118 / 12px-700` vì cột "Trạng thái đăng ký" chỉ rộng
180px, nhãn "Chờ xác nhận" ở 84px sẽ tràn — đây là chỗ Figma cố ý khác, không "chuẩn hoá cho đẹp".
Đo: history 107.5 · delivery 86.1 · notification 84 · exam 118, tất cả h28 radius14.

**008/009** — form PC đổi sang `wj-pc-card` + `wj-pc-field/__label/.wj-pc-control` +
`.wj-pc-form-actions` (component mới **duy nhất** của H1). Route POST, `name=`, `required`,
`enctype`, csrf **giữ nguyên**; block mobile không đụng.
Trung hoà 2 rule shell trong phạm vi component: `select { padding: 5px !important }` (dashboard.css)
và `label { padding-left: .2rem }` (bootstrap-extended).
Đo: 4 input/select **42px**, radius 10, border `#E5E7EB`, label 14/600; action bar có separator,
2 nút h40/radius12/700, primary bên phải.

**Regression thật (không chỉ đo style):** submit `/portal/support/new` → tạo ticket thật, redirect
đúng trang chi tiết; filter submit thật ở history/delivery/notification/exam → query string và giá trị
đã chọn giữ nguyên sau submit; mobile 9 route overflow ngang = 0, 0 JS pageerror.

**Deploy:** `-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,`
`wujia_portal_notification,wujia_portal_exam,wujia_portal_support` — không module mới, **không migration**.
`_pc_components.css?v=` đã bump 1155→**1166**. `wujia_portal_delivery` **không cần `-u`** (không sửa file,
chỉ ăn theo component chung).

**Còn tồn (đưa sang H2):** 3 form PC khác vẫn Bootstrap thuần — `portal_return_form`,
`portal_info_request_form`, `portal_info_request_detail`.

---

## Kết quả H2 (2026-08-04) — 0 FAIL

DB copy cô lập **`wujia_tea_h2`** (cổng 8034 — 8033 đã bị phiên khác chiếm; KHÔNG đụng `wujia_tea_19`).
Build `-u` 10 module: **RC=0, 0 ERROR/Traceback**. Harness `h2_check.py` (đo PC) + `h2_shots.py`
(md5 mobile) — scratchpad, gitignored.

**3 quyết định chủ dự án chốt đầu phiên:** `portal_franchise_profile` chuyển sang `wj_page_header`
(trang này chưa từng dùng component chung, nút "Quay lại" cuối trang là đường back DUY NHẤT — gỡ
suông là mất lối về) · breadcrumb gắn **cả 13 màn** · ngưỡng ẩn pagination = **≤10**, không phải
≤ page size đang chọn (chọn 50 mà còn 20 bản ghi thì khối biến mất, kẹt không bấm về 10 được).

**005** — BA gợi ý copy `/portal/exam`, nhưng đọc source thì `portal_exam.xml:103-119` có
`<select name="limit">` nằm **ngoài mọi `<form>`** và nút trang là `<span>` ⇒ **UI tĩnh, bấm không
ra gì**. Hai trang đích thì ngược lại: controller đã nhận sẵn tham số (`page_size`
`purchase_history/controllers/portal.py:227,286`; `limit` `notification/controllers/portal.py:139,188`)
và pager link chạy thật. Làm bằng `<form method="get">` nhỏ bọc select + hidden mang bộ lọc,
`onchange="this.form.submit()"` — đúng pattern đã có ở `portal_order_catalog.xml:53`, không thêm file JS.
⚠️ Phải trung hoà `form { margin-bottom: 15px }` của shell (L4) bằng
`.wj-pc-pagination__size-form { display:flex; margin:0 }`, không thì hàng pagination đội cao.
Controller history phải **thêm `page_size` vào context** (trước giờ nhận tham số nhưng không trả ra view).
Đo: option 10/20/50 · đổi → URL mang `page_size=50`/`limit=50`, bảng 15/30 dòng, select giữ giá trị,
không mang `page=` · lọc `q=S000` rồi đổi số dòng → từ khoá còn nguyên · 0 bản ghi → khối ẩn ·
bấm "Sau" ở 10/trang → `page=2&page_size=10`, trang 2 đúng 5 dòng.

**006** — variant `back` dùng ở **13 màn PC + 14 màn mobile**, nên sửa ở component là bắt buộc.
Nhãn chữ nằm trong `<span>` chung, ẩn ở nhánh `--m` bằng `display:none` ⇒ mobile không đổi 1 pixel.
Bốn nút thừa đã gỡ: `portal_support.xml` (PC-only), `portal_return_detail.xml` (PC-only),
`portal_info_request_detail.xml` (**block dùng chung** → mobile màn này cũng bớt 1 nút, đúng ý issue,
đã khai miễn trừ), `portal_franchise_profile.xml` (đổi header Vuexy `h2.content-header-title` sang
`wj_page_header`, y như H1 làm với Dashboard).
Đo 11 màn: back **122×40**, có chữ, `href` đúng danh sách cha, **đúng 1 nút back / màn**, overflow 0.

**007** — component đang dùng là `wj_page_header` (class `.wj-page-header__*`), KHÔNG phải
`.wj-pc-page-header` — chuyển 2 màn sang component kia sẽ đẻ lại hệ tiêu đề thứ hai mà H1-002 vừa gom.
Giải: prop `ph_crumb` render thành `<nav>` **riêng, đặt trước `<header>`**, chỉ khi `ph_platform='pc'`
⇒ flex-row bên trong header nguyên vẹn, mobile không nhận prop nên DOM không đổi.
Đo: 13/13 màn đúng chuỗi, 14px/500, `y` nhỏ hơn header (nằm trên tiêu đề).

**Regression mobile 391×844** — chụp full-page 14 route trước/sau trên **cùng DB copy**:
**13/14 trùng md5 tuyệt đối**. Route lệch duy nhất là `/portal`, vùng khác đúng **139×32 px** ở đồng hồ
đếm ngược khung giờ đặt hàng ("còn 06:59" → "còn 06:22") — đã crop ảnh đối chiếu, **không phải hồi quy**.
Back mobile 5 màn detail: 40×40, nhãn `display:none`, `::after` 44×44. Overflow ngang = 0 mọi route.

**Chức năng thật:** submit `/portal/support/new` → tạo ticket `#68` thật, redirect đúng trang chi tiết,
trang đó có đúng 1 nút back 122×40, bấm về `/portal/support`.

**Phát hiện thêm (KHÔNG sửa ở H2 — ngoài scope, đề nghị BA mở issue riêng):**
1. Phân trang `/portal/exam` là **UI tĩnh** (select ngoài form, nút trang là `<span>`) — bấm không có
   tác dụng. Cách sửa khác hẳn 005 nên không gộp.
2. `portal_info_request_form.xml:150` — script inline trong CDATA viết `&amp;&amp;` thay vì `&&`;
   XML **không** giải mã entity bên trong CDATA nên trình duyệt nhận literal `&amp;&amp;` và **cả khối
   script chết** (`Unexpected token ';'`). Hệ quả: ô "Giá trị hiện tại" ở màn Tạo yêu cầu cập nhật
   thông tin **chưa bao giờ tự điền**. Lỗi có từ commit `ca15c76` (15/07), **không phải do H2** —
   đã đối chiếu `git diff` (H2 chỉ thêm 1 dòng `ph_crumb` vào file này).

**Deploy:** `-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,`
`wujia_portal_notification,wujia_portal_support,wujia_portal_return,wujia_portal_info_request,`
`wujia_portal_sale,wujia_portal_knowledge,wujia_portal_delivery` — không module mới, **không migration**.
`_components.css?v=` 1165→**1167**, `_pc_components.css?v=` 1166→**1167**.
