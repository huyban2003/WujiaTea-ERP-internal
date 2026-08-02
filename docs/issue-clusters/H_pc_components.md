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

## H2 — Đổi cấu trúc template (làm sau)

| Issue | Việc | Ghi chú |
|---|---|---|
| **005** Pagination | Thêm page-size selector ("10 / trang") cho `/portal/purchase-history` và `/portal/notification` | `/portal/exam` **đã làm đúng** (10/20/50) → copy pattern đó, đừng thiết kế lại. BA cho phép ẩn toàn bộ pagination khi tổng ≤ page size |
| **006** BackButton | Thay nút icon-only 44×44 bằng "← Quay lại" **122×40** (hoặc 122×36 trong PageHeader) | Source ghi rõ **không dùng icon-only**. Áp `/portal/order/product/<id>` + `/portal/support/new`, và rà các màn detail khác. Chỉ **một** nút, không lặp ở cuối form |
| **007** Breadcrumb | Thêm breadcrumb cho màn create/detail: `Hỗ trợ / Tạo yêu cầu`, `Đặt hàng / Chi tiết sản phẩm` | Breadcrumb **không thay thế** BackButton — giữ cả hai (Navigation Rules v1.5). Dùng `.wj-pc-page-header__crumb` có sẵn |
| **WJ-ORD-023** FilterBar Đặt hàng | search + danh mục + nút Tìm về **một hàng** trong card trắng; control 40–42px, gap 12–16px | Hiện xếp dọc 3 hàng y≈172/226/280, input & select cùng rộng ~1024px. **Giữ nguyên** `<form method="get">` + controller — chỉ đổi layout. Mockup Figma node `4600:2` |
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
