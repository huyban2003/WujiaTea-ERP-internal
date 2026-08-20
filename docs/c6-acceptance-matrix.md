# C6 — WJ-PORTAL-UI-001 · bảng đối chiếu nghiệm thu

**Issue:** WJ-PORTAL-UI-001 (`5. Issue List` STT 97, Severity Low, phạm vi toàn Portal)
**Ngày đo:** 19/08/2026 · **Build:** `wujia_portal_layout 19.0.31.19.0`
**Môi trường đo:** DB copy cô lập `wujia_tea_c6` (port 8057, KHÔNG đụng `wujia_tea_19`/8019)
\+ đối chứng trên **UAT `http://113.161.187.126:8019`**
**Harness:** `scratchpad/c6_state_audit.py` (Playwright + CDP `CSS.forcePseudoState`),
`c6_verdict.py`, `c6_tab_walk.py`, `c6_b4_regression.py` — kiểm kê **22 route** (17 route
PAGE NAMING MATRIX + 5 route ngoài matrix) × **2 breakpoint** (1920×1080, 391×844),
4 trạng thái mỗi phần tử: default / hover / focus-visible / pressed.

---

## 0. Điều phải nói trước: local KHÔNG tái hiện được lỗi

Rule sinh ra gạch chân là **`a:hover { text-decoration: underline }` của
`web.assets_frontend.min.css`** (Bootstrap 5 trong Odoo 19), specificity `(0,1,1)`, nạp
**sau** toàn bộ CSS custom ⇒ mọi component khai `text-decoration:none` ở base `(0,1,0)` đều
thua.

Đo được: rule này **có trên UAT nhưng KHÔNG có trên DB local**. Nguồn khác biệt là UAT
có cài `website_sale` + 5 module `website_sale_*` (§5 compact summary) kéo theo bundle
frontend khác. Cùng một element `.wujia-mknow-row`, hover:

| Môi trường | `text-decoration-line` khi hover |
|---|---|
| UAT (code hiện tại) | `underline` |
| Local `wujia_tea_c6` (code hiện tại) | `none` |

⇒ **Lặp lại đúng bài học L10**: "local chạy ngon" không chứng minh gì. Vì vậy phần
underline được nghiệm thu **trên chính UAT**, bằng cách nạp thêm `_variables.css` +
`_interaction.css` vào trang UAT rồi đo lại — tức thử đúng cascade thật của production.
Các hạng mục còn lại đo trên DB copy có đối chứng before/after cùng phiên chạy (chặn
`_interaction.css` để dựng baseline trên **cùng** server, cùng user, cùng dữ liệu).

---

## 1. Đối chiếu từng dòng `Kết quả mong muốn` của BA

Acceptance BA viết dạng GIVEN/WHEN/THEN, tách thành 8 gạch đầu dòng.

| # | Yêu cầu BA | Đo được | Kết quả |
|---|---|---|---|
| 1 | WHEN hiển thị mặc định THEN chữ không gạch chân, trừ inline text link | 0/53 phần tử bấm được gạch chân ở default (cả 2 breakpoint, UAT + local) | **Pass** |
| 2 | Card/row/menu/button/chip/tab/icon-button: `text-decoration:none` cho component và nội dung con, ở mọi trạng thái | **UAT 1920: 18 → 0** key dính underline · **UAT 391: 34 → 0** | **Pass** |
| 3 | Inline text link thực sự VẪN giữ underline | `.wj-pc-link` hover = `underline`; 3 vùng nội dung người dùng nhập (`.article-content`, `.wujia-mknow-body`, `.wujia-mticket-bubble`) được chừa bằng bộ chọn theo tổ tiên | **Pass** |
| 4 | WHEN hover PC THEN card/row/menu đổi nền `#EAF7FD` và/hoặc viền `#28A9DF`; shadow nhẹ | Số component **không có phản hồi hover nào**: UAT 1920 `28 → 16`, UAT 391 `33 → 7`; local 1920 `26 → 15`, local 391 `30 → 10`. Nhóm còn lại là nhóm **cố ý giữ nguyên** (mục 2 dưới) | **Pass** |
| 5 | Shadow không được làm layout dịch chuyển | **0/53 phần tử** đổi `width`/`height` giữa default ↔ hover ↔ pressed, cả 2 breakpoint, cả UAT lẫn local. `border-width` không đổi ở 0/53 | **Pass** |
| 6 | WHEN điều hướng bàn phím THEN focus-visible bao quanh toàn bộ component, outline ≥2px, tương phản rõ, không chỉ dựa vào màu chữ | Thiếu ring: **UAT 1920 `46 → 0`**, **UAT 391 `43 → 0`**, local `45 → 0` / `44 → 0`. Ring đo được `2px solid rgb(15,124,168)` offset `2px` ở **100%** phần tử (53/53 và 50/50), **một** token màu duy nhất | **Pass** |
| 7 | WHEN nhấn/chạm THEN có phản hồi pressed ngắn, không giữ underline sau thao tác | `:active` đổi nền `--wujia-primary-light` + viền `--wujia-primary` cho toàn bộ nhóm bề mặt trung tính; `text-decoration` ở `:active` = `none` trên 53/53 | **Pass** |
| 8 | Áp thống nhất mọi màn hiện có, desktop/mobile, component tái dùng; không đổi kích thước / xuống dòng / tràn ngang / vị trí nội dung | 22/22 route HTTP 200; **0 trang tràn ngang**; **0/22 trang đổi chiều cao**; 0 lỗi JS — cả 2 breakpoint | **Pass** |

**8/8 Pass (100%)** — ngưỡng yêu cầu ≥90%.

### Đi bằng bàn phím thật (không ép pseudo-class)

`c6_tab_walk.py` — bấm Tab 25 lần trên 5 trang (`/portal`, `/portal/order`,
`/portal/knowledge`, `/portal/debt`, `/portal/exam`):

| | Trước | Sau |
|---|---|---|
| Điểm dừng có vòng focus nhìn thấy | **7/124** | **124/124** |
| Thứ tự điểm dừng | — | **giống hệt trước khi sửa** |

---

## 2. Nhóm CỐ Ý giữ nguyên (không phải bỏ sót)

Chủ dự án chốt 19/08: công thức hover của BA chỉ áp cho **bề mặt trung tính**. Các
component dưới đây **đã có** trạng thái thiết kế theo Figma PC v1.5 / Mobile v2.3 và được
giữ nguyên — chúng vẫn được hưởng phần "bỏ underline" và "vòng focus" của C6:

| Nhóm | Ví dụ | Vì sao giữ |
|---|---|---|
| Nút primary / CTA | `.wj-pc-btn--primary`, `.btn-primary`, `.wj-cta-btn`, `.wujia-mcart-submit`, `.wj-page-header__create`, `.wujia-mexam-fab` | Hover đã là `primary_dark` (`#0F7CA8 → #0C6688`) đúng như BA yêu cầu. Nếu ép nền `#EAF7FD` thì chữ trắng chỉ còn ~1.2:1, **fail WCAG AA** |
| Chip / tab / mục menu **ĐANG chọn** | `.wj-filter-chip.is-active`, `.wj-pc-dlv-chip.is-active`, `.wj-debt-pc-tab.is-active`, `.wj-pc-acct-nav__item.is-active`, `.wj-pc-page-btn.is-active` | Nền `#28A9DF` chính là dấu hiệu "đang chọn"; đổi sang `#EAF7FD` khi hover sẽ xoá mất dấu hiệu đó |
| Action trên thanh header tối | `.wujia-mheader-action`, `.wujia-active-store-badge`, `.nav-link` | Nền tối, đã có hover riêng (`rgba(255,255,255,.18) → .30`); nền `#EAF7FD` sẽ chọi với thanh header |
| Text link | `.wujia-mdash-link`, `.wujia-content-card-header-link`, `.wj-debt-section__more`, `.wj-pc-dlv-codelink`, `.wujia-morder-row-name`, `.wujia-mexam-back` | Là chữ, không phải bề mặt — chỉ đổi màu chữ khi hover |
| Ô lịch thi đã khoá | `.wj-exam-pc-day--none`, `.wj-exam-pc-day--out` | Có thuộc tính `disabled` (`portal_exam_pc.js:148`, `portal_exam.xml:315`) — không bấm được thì không cần hover/ring |
| Tên sản phẩm trong bảng PC | `.wj-pc-order-prod` | Bề mặt hover là **dòng** `.wj-pc-order-row` (đã có hover riêng), không phải cái link. Chỉ **gỡ** gạch chân cố ý ở `portal_order.css` |

---

## 3. Hồi quy

| Phép đo | Kết quả |
|---|---|
| Build `-u wujia_sale,wujia_portal_layout,wujia_portal_sale --stop-after-init` | **RC=0**, 0 ERROR / 0 Traceback |
| Test Odoo 2 module bị `-u` | **148 test, 0 failed, 0 error** |
| Lưới hồi quy B4 (17 route matrix + 5 ngoài matrix + 6 chiều rộng) | **282/286 trước = 282/286 sau** ⇒ C6 gây **0 hồi quy**. 4 ô đỏ là **sẵn có**: `/portal/support/40` với tài khoản `admin` không thấy màn chi tiết (dữ liệu/quyền), đỏ y hệt khi chặn `_interaction.css` |
| Nút Quay lại CMP-BPH-001 ở 6 chiều rộng | 360/391/768 = 42×42 header 52 · 1366/1440/1920 = 122×40 header 64 · tràn ngang 0 — **giữ nguyên bảng B4** |
| Chiều cao trang, 22 route × 2 breakpoint | **0 trang đổi** |
| Lỗi JS | **0** |

> ⚠️ Khi đo trên UAT có thấy 6 trang lệch 4–12px chiều cao. Đã truy: nguyên nhân là **nhúng
> lặp `_variables.css`** trong chính phép thử (file bị đẩy xuống cuối `<head>` nên đè vài
> rule Vuexy vốn đang thắng), **không phải** `_interaction.css`. Đối chứng: cột "chỉ nhúng
> token" và cột "token + C6" cho **cùng** một con số (1107/1337/1131). Khi deploy thật
> `_variables.css` vẫn nằm nguyên vị trí cũ nên không có hiện tượng này.

---

## 3b. Đo lại TRÊN UAT sau khi chủ dự án deploy (19/08/2026)

Deploy xong, chạy lại **đúng bộ đo cũ** trên `http://113.161.187.126:8019` (chỉ đọc, không
sửa dữ liệu), lần này **không nhúng CSS** nữa — đo chính bản đang chạy:

| Phép đo | Trước deploy (UAT) | Sau deploy (UAT) |
|---|---|---|
| Thành phần bấm được còn gạch chân @1920 | 18 | **0** |
| Thành phần bấm được còn gạch chân @391 | 34 | **0** |
| Thiếu vòng focus @1920 | 46 | **0** |
| Thiếu vòng focus @391 | 43 | **0** |
| Ring đúng `2px solid` + offset `2px` | — | **53/53**, một màu duy nhất `rgb(15,124,168)` |
| Component không có phản hồi hover @1920 / @391 | 28 / 33 | **16 / 7** (phần còn lại là nhóm cố ý giữ, mục 2) |
| Hover/pressed làm đổi kích thước | — | **0/53** |
| Hover ra tím Vuexy | 1 | **0** |
| 22 route: HTTP 200 · tràn ngang · đổi chiều cao · lỗi JS | — | **22/22 · 0 · 0 · 0** |
| Đi Tab thật 5 trang × 25 stop | 7/124 | **124/124** |

⇒ **13/13 Pass @1920** và **12/12 Pass @391** trên UAT thật.

**Hồi quy B4 trên UAT: `282/286`** — đúng bằng con số đo trên bản sao local. Lần chạy đầu ra
`270/286` vì **ID bản ghi trong bộ đo là ID của DB local**: `stock.picking.batch` id 3,
`wujia.notification` id 41, `wujia.support.ticket` id 40, `wujia.return.request` id 12 **không
tồn tại trên UAT** (kiểm bằng XML-RPC), nên 4 trang chi tiết rơi về trang danh sách. Thay bằng
ID thật của UAT (2 / 18 / 16 / 10) thì 16 ô đỏ còn **4**, đều ở `/portal/notification/18` —
đây là thông báo QA nhắm theo khu vực mà cửa hàng đang chọn của `admin` không thuộc, nên
portal trả về danh sách; `/portal/notification/1` mở bình thường, có đủ tiêu đề và nút Quay
lại. **Không phải hồi quy của C6**: 5 trang chi tiết đó có `page_h` và số phần tử bấm được
**giống hệt nhau trước và sau khi deploy**.

---

## 4. LIMIT (đã ghi vào sheet cho BA)

1. **Màu vòng focus dùng `--wujia-cta #0F7CA8`, không dùng `--wujia-primary-dark #168FC2`
   như spec BA viết.** Lý do: `#0F7CA8` chính là ring đang có sẵn trên nút CTA/`wj-pc-btn`
   (đo được trước khi sửa), tương phản 4.71:1 trên nền trắng (so với 3.32:1), và giữ nguyên
   được chỗ BA đã Pass ở sprint trước. Nếu BA muốn đúng `#168FC2` thì đổi **một** token
   `--wujia-focus-ring` là xong.
2. **Nút Quay lại `.wj-page-header__back`**: ghi chú token `--wujia-primary-border-soft`
   (`#BFE8F7`) nói hover của CMP-BPH-001 dùng viền soft, nhưng thực tế **chưa bao giờ được
   cài** (đo trước khi sửa: hover không đổi gì). C6 cho nó dùng công thức chung
   `#EAF7FD` + viền `#28A9DF`. Nếu BA muốn giữ `#BFE8F7` riêng cho nút này, báo lại.
3. **Chưa đo trên thiết bị chạm thật**: trạng thái pressed được đo bằng ép `:active` trong
   Chromium headless. Rule hover đã bọc `@media (hover: hover) and (pointer: fine)` nên
   không bị dính "sticky hover" trên điện thoại, nhưng BA nên retest bằng máy thật.
4. Nhóm ở mục 2 **cố ý** không đổi hover — nếu BA muốn đồng loạt thì cần chốt lại cách xử
   lý tương phản của nút primary và dấu hiệu "đang chọn" của chip.
