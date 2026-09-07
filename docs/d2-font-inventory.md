# D2 — kiểm kê font Portal (WJ-PORTAL-UI-002)

**Ngày đo:** 2026-08-26 · **Môi trường:** đo **chỉ-đọc trên chính UAT**
`http://113.161.187.126:8019` (admin, cookie `wujia_active_franchise_id=3`) ·
**Harness:** `scratchpad/d2_font_audit.py` (Playwright + CDP `CSS.getMatchedStylesForNode`
/ `CSS.getPlatformFontsForNode`).

⚠️ **Vì sao đo trên UAT chứ không local (L14/L10):** rule sinh ra "Inter Tight" đến từ bundle
của module `website` — UAT có cài `website` + `website_sale`, local **không** ⇒ local không tái
hiện được lỗi. Cùng loại bẫy đã trả giá ở C6 và C7.

**Phạm vi:** 16 route × 5 breakpoint (360 / 390 / 430 / 500 / 1440) = **80 ô**. Quét **mọi text
node** (không chỉ leaf — bản quét đầu chỉ lấy leaf nên bỏ sót heading có `<span>` con, ví dụ
`wj_section_header`), tách **hiện** / **ẩn** theo `getClientRects()` vì khối PC nằm sẵn trong
DOM mobile (`d-none`) và ngược lại.

---

## 1. Gốc rễ (đo, không suy đoán)

CDP `CSS.getMatchedStylesForNode` trên `H2.wj-pc-card__title` của `/portal/inspection` @1440:

| Nguồn | Selector | Giá trị | `!important` |
|---|---|---|---|
| bundle Vuexy | `h1..h6, .h1..h6` | `inherit` | không |
| **bundle Odoo/website** | `h6,.h6,h5,.h5,…,h1,.h1` | `"Inter Tight","Odoo Unicode Support Noto",sans-serif` | **không** |
| `_wujia_theme.css` | `html body` (kế thừa) | `var(--wujia-font-family)` | có |

⇒ **Một rule khớp element luôn thắng kế thừa, bất kể specificity.** Rule Inter Tight chỉ
(0,0,1) nhưng vẫn thắng `html body {…!important}` vì cái sau chỉ **kế thừa** xuống.

Rule ép Inter cũ (`_wujia_theme.css:45-50`, UI-06/S39) neo `.content-wrapper` ⇒ chỉ phủ heading
nằm **trong** `.content-wrapper`. Mọi chỗ ngoài neo đó giữ Inter Tight:

- BlankShell mobile `.wujia-mpage` — cố ý đặt **ngoài** `.content-wrapper` từ pattern S15.
- `wujia_portal_inspection`: `.content-wrapper` ở `portal_inspection_list_templates.xml:303`
  **chỉ bọc page-header**; danh sách nằm trong `<div id="wj-inspection-content">` (vùng
  `wj_ajax_list` swap) — **ngoài** neo. Đo tổ tiên thật trên UAT xác nhận.
- Popup chuông (`wujia_portal_notification/views/header_bell_inherit.xml:22`) — nằm trong navbar.

🔑 **Cùng một class ra hai font khác nhau tuỳ trang**: `wj-pc-card__title` là Inter ở
`/portal/debt`, `/portal/delivery` (trong `.content-wrapper`) nhưng Inter Tight ở
`/portal/inspection` (ngoài). Quyết định là **tổ tiên DOM**, không phải tên class — đúng bài
học kiểm kê C8.

## 2. Danh sách chỗ ≠ Inter (trạng thái TRƯỚC)

**49 lượt hiện + 96 lượt ẩn = 145** trên 80 ô. Tất cả đều là
`"Inter Tight","Odoo Unicode Support Noto",sans-serif`; **0 chỗ** Montserrat / Helvetica /
Arial (Vuexy đã bị `html body{…!important}` đè từ S34/S35).

| Selector | Route | Hiện | Ẩn | Template nguồn |
|---|---|---|---|---|
| `H4.wj-pc-noti-popup__title` | **cả 16/16 route** | 0 | 80 | `wujia_portal_notification/views/header_bell_inherit.xml:22` |
| `H2.wujia-maccount-cardtitle` | `/portal/franchise-information` | 12 | 3 | `wujia_portal_base/views/portal_franchise_information.xml` (3 chỗ) |
| `H2.wj-rep-mcard__title` | `/portal/reports/orders` | 12 | 3 | `wujia_portal_report/views/portal_report_orders.xml` (3 chỗ) |
| `H2.wj-section-header__title` | `/portal/debt`, `/portal/debt/payment-history` | 4+4 | 1+1 | **component chung** `wujia_portal_layout/views/wj_section_header.xml` |
| `H3.wj-section-header__title` | `/portal/return` | 4 | 1 | nt |
| `H3.wujia-mexam-card-title` | `/portal/exam` | 4 | 1 | `wujia_portal_exam/views/portal_exam.xml` |
| `H2.wujia-maccount-cardtitle` | `/portal/profile` | 4 | 1 | `wujia_portal_layout/views/profile_page.xml:99` |
| `H3.wujia-maccount-store-name` | `/portal/franchise-information` | 4 | 1 | `portal_franchise_information.xml` |
| `H2.wj-pc-card__title` | `/portal/inspection` (chỉ @1440) | 1 | 4 | `wujia_portal_inspection/views/portal_inspection_list_templates.xml:34` |

**Khớp báo cáo BA 22/08**: desktop Khảo sát ✔ · mobile Công nợ ✔ · Đăng ký thi ✔ · Hồ sơ ✔.
BA **chưa nêu** 3 chỗ nữa mà máy bắt được: Báo cáo đặt hàng (3 tiêu đề card), Thông tin cửa
hàng (4 tiêu đề), Đổi trả (SectionHeader) — đều cùng gốc rễ, fix một lần là hết.

🔑 **`wj_section_header` là component chung của C8 (19 call site)** ⇒ sửa ở tầng `h1..h6` fix
một lần cho toàn bộ, không phải đụng 19 chỗ.

## 3. Font icon — phải giữ nguyên

Đếm `::before` / `::after` có `content`: **`feather`** (12–80 lượt/trang) và **`FontAwesome`**
(6 lượt) — không nằm trong phạm vi sửa, đã đo trước–sau để chứng minh **0 đổi** (§ acceptance).
`icomoon` chỉ có trong vendor CSS không nạp trên portal.

## 4. Fallback Unicode — hiện trạng

`--wujia-font-family` = `'Inter', sans-serif`, mà `@font-face` Inter tự host
(`static/assets/fonts/inter/inter.css`) khai
`unicode-range: U+0000-024F, U+1E00-1EFF, U+20A0-20CF, U+2DE0-2DFF, U+A640-A69F` — **chỉ Latin /
Latin-ext / tiền tệ**. ⇒ glyph Thái và Trung **rơi thẳng về generic `sans-serif`**, mỗi máy một
kết quả.

Đo `CSS.getPlatformFontsForNode` với 3 mẫu chữ (probe dựng client-side, **không** đổi ngôn ngữ
trên server):

| Mẫu | TRƯỚC (HEAD) | SAU (bản vá) |
|---|---|---|
| `Hồ sơ cá nhân — 1.234.000 đ` | **Inter Tight** | **Inter** ✅ |
| `ข้อมูลส่วนตัว` (Thái) | Noto Sans Thai *(may rủi theo OS)* | **Noto Sans Thai** *(khai tên rõ ràng)* |
| `个人资料` (Trung) | **Noto Sans CJK JP** ← sai biến thể vùng | **Noto Sans CJK SC** ✅ |

🔑 Ca chữ Trung là lý do phải thêm **`'Noto Sans CJK SC'`** cạnh `'Noto Sans SC'`: tên family
theo fontconfig trên Linux là `Noto Sans CJK SC`, thiếu alias này thì trình duyệt rơi sang bản
**JP** — chữ Hán ra đúng mã nhưng **sai hình thể vùng**.

`'Odoo Unicode Support Noto'` (font Odoo tự khai trong `web/static/fonts/fonts.scss`) chỉ phủ
**Cyrillic / Hebrew / Arabic / Telugu** — **không** phủ zh/th, nên copy nguyên stack của Odoo là
vô ích với Wujia; vẫn giữ ở cuối stack vì `unicode-range` gate sẵn ⇒ 0 byte tải thêm cho
Latin/Việt.

## 5. Bản vá

| File | Đổi |
|---|---|
| `custom/wujia_portal_layout/static/assets/css/_variables.css` | `--wujia-font-family` nối fallback **tên font hệ thống** Thai + CJK (0 byte tải thêm) |
| `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` | rule font-family heading đổi neo `.content-wrapper` → **`html body`**, phủ thêm class `.h1..h6` |
| `custom/wujia_portal_layout/views/assets.xml` | `?v=1170/1174` → **`?v=1177`** cho 2 file trên |
| `custom/wujia_portal_layout/__manifest__.py` | `19.0.32.3.0` → `19.0.32.4.0` |

🔴 **Cố ý KHÔNG nới rule `font-weight:700 !important`** ở `_wujia_theme.css:35-40` (cũng đang
neo `.content-wrapper`): nới sẽ ép mọi heading mobile về 700, **phá weight 800 của `CMP-SH-001`**
(C8a/C8b) và bảng đo B3a/B4 đã Pass.

`html body h1` = (0,0,3) đã thắng (0,0,1) của bundle; vẫn **giữ `!important`** theo đúng tiền lệ
UI-06 vì `web.assets_frontend` nạp **sau** CSS custom (bài học C6) — bỏ `!important` thì thắng
hay thua phụ thuộc thứ tự nạp, không đáng đánh cược.

**Deploy:** `-u wujia_portal_layout` — không module mới, không cập nhật dữ liệu, `?v=1177` đã bump.
