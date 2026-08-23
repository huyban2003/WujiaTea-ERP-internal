# Batch a11y — WJ-PORTAL-UI-003 + WJ-PORTAL-UI-004 (2026-08-23)

DB copy `wujia_tea_a11y` (nền `wujia_tea_mt2`, port 8062, không đụng 8019). Build `-u wujia_portal_layout` RC=0. Harness: `scratchpad/a11y_batch_measure.py` + `a11y_tabwalk_regr.py` (Playwright, login POST `/web/session/authenticate` theo L13/3).

## WJ-PORTAL-UI-003 — Sidebar PC ẩn vẫn nhận Tab (viewport mobile)

Fix: 1 rule CSS `_wujia_theme.css` — `@media (max-width:1199.98px) body:not(.menu-open) .main-menu { visibility: hidden }`. `visibility` gỡ phần tử khỏi cả tab order lẫn a11y tree; `.menu-open` khôi phục.

| Kết quả mong muốn (BA) | Đo được | Pass |
|---|---|---|
| Tab/Shift+Tab không vào logo/menu/link sidebar ẩn | 40 Tab @391: 0 stop trong `.main-menu` | ✅ |
| Chỉ đi qua control đang hiển thị, thứ tự hợp lý | 40 stop đều visible, bbox x≥0 | ✅ |
| Focus indicator luôn trong viewport | 0 stop bbox x<0; ring C6 giữ nguyên (tab-walk 298 stop) | ✅ |
| Sidebar mở chủ động → control nhận focus | Tablet 1024 `menu-open`: visibility=visible, link focus OK | ✅ |
| Đóng lại → hết focus được | Click overlay → `visibility:hidden`, `focus()` trượt | ✅ |
| Không ảnh hưởng tab order desktop | @1920: `.main-menu` visible, 16 stop sidebar y nguyên | ✅ |

**6/6 (100%).**

## WJ-PORTAL-UI-004 — Bottom sheet "Thêm" không nhận focus khi mở

Fix: nút "Thêm" `<a href="#">`→`<button type="button">` (Space hoạt động) + `aria-expanded` + sheet `aria-modal="true"`; JS `open()` focus nút đóng, focus-trap Tab/Shift+Tab, `close()` trả focus về nút Thêm. Gotcha: `visibility` nằm trong `transition 0.25s` nên focus() cùng frame trượt → state `.is-open` chỉ transition `transform` (visibility flip tức thời khi mở, chiều đóng vẫn delay).

| Kết quả mong muốn (BA) | Đo được | Pass |
|---|---|---|
| Enter/Space mở → focus vào nút đóng | Enter ✅ + Space ✅ → activeElement = `.wujia-msheet-close` | ✅ |
| Tab/Shift+Tab giữ trong sheet | 15 Tab đều trong sheet; Shift+Tab từ nút đóng wrap | ✅ |
| Nội dung nền không nhận focus | trap kéo focus ngoài sheet vào trong | ✅ |
| Esc đóng | ✅ (hành vi sẵn có, giữ nguyên) | ✅ |
| Sau đóng focus về đúng nút Thêm | Esc + backdrop + nút X đều trả focus | ✅ |
| Thao tác chạm giữ nguyên | tap backdrop đóng, scroll-lock gỡ | ✅ |

**6/6 (100%).**

## Hồi quy

- Lưới B4 `b4_regression.py --base :8062`: **286/286 PASS**.
- Tab-walk 6 route × 2 viewport (`a11y_tabwalk_regr.py`): 298 stop, 0 stop ẩn/x<0/thiếu ring, **12/12 route PASS**.
- 3 trang × 2 viewport: HTTP 200, overflow ngang 0, 0 pageerror; footer bar 5 tab đồng chiều cao (button không vỡ layout).
- Unit test `wujia_section_header_c8` + `wujia_lang_c10`: **24 test, 0 failed** (phải nâng `freezegun` 0.3.15→1.1.0 theo `odoo19/requirements.txt` — gotcha S48 tái hiện, lỗi env không phải code).

## Deploy

`-u wujia_portal_layout` (19.0.32.2.0) — không data update, không module mới; bump `?v=1174` (`_wujia_theme.css`, `_components.css`, `wujia_mobile_more_sheet.js`); sau quick-win dead-CSS: 19.0.32.2.1, `_components.css?v=1175`.

## Đo lại trên UAT sau deploy (23/08)

Chủ dự án deploy `-u wujia_portal_layout`, xác nhận XML-RPC bản `19.0.32.2.1`. Harness `scratchpad/a11y_uat_check.py` (admin, POST authenticate L13/3, cookie cửa hàng 3):

- Asset sanity: `_components.css?v=1175` + `_wujia_theme.css?v=1174` + `more_sheet.js?v=1174` có mặt trong HTML.
- **UI-003: 11/11** — `.main-menu` hidden @391 (40 Tab 0 stop lọt), visible @1920 (16 stop y nguyên), tablet 1024 mở→focus được / đóng qua overlay→hết focus.
- **UI-004: 13/13** — Enter + Space mở → focus nút đóng, trap 15 Tab + Shift+Tab wrap, Esc/backdrop/nút X đóng + trả focus, scroll-lock gỡ, aria-expanded đúng 2 chiều.
- Hồi quy dead-CSS 6 trang × 2 viewport: overflow 0, 0 pageerror, footer 5 tab đồng cao.
- **Lưới B4 trên UAT: 286/286 PASS** (`scratchpad/b4_uat.py` = `b4_regression.py` thay ID thật cửa hàng 3: SO 41 / batch 2 / notification 19 / ticket 16 / return 9; login form `anh.owner` không dùng được trên UAT → admin + POST authenticate).

⇒ Cả 2 issue giữ nguyên `Ready for Retest`, chờ BA; quick-win xoá CSS chết **không ảnh hưởng** issue đã fix nào.
