# C8 — Ma trận nghiệm thu `UI-SECTIONHEADER-001` (STT 83 · `CMP-SH-001`)

Phiên 2026-08-22 · branch `dev/2026-08-22-c8` · **phạm vi C8a** (component + 5 route mẫu).
Đo bằng máy: Playwright + chromium (env `odoo`), DB copy cô lập `wujia_tea_c8` port **8059**
(KHÔNG đụng `wujia_tea_19`/8019). Harness ở `scratchpad/` (`c8_measure.py`, `c8_tabwalk.py`,
`b4_regression.py`) — không đưa vào repo theo §13.

---

## 1. Theo từng gạch đầu dòng cột `Kết quả mong muốn`

| # | Yêu cầu (nguyên văn rút gọn) | Đo được | Pass/Fail |
|---|---|---|---|
| 1 | Toàn bộ trang Portal và route con được **audit** đúng loại heading | 183 heading thô → phân loại 132 heading trong scope: **12 SectionHeader / 89 CardHeader / 3 PageHeader / 24 Khác**, cộng 5 construct listhead không phải heading thật → tổng **18 call site** SectionHeader (`docs/c8-heading-inventory.md`) | **Pass** |
| 2 | Toàn bộ trang Portal và route con được **migrate** | **13/18 call site** đã chuyển (C8a). 5 site còn lại (exam, debt, notification, return, report) thuộc C8b — ranh giới ghi rõ ở §4 inventory | **Fail (một phần — 72%)** |
| 3 | PC title **22/30**/800 | 22px / 30px / **700** (xem LIMIT-1) | **Pass** (size+line-height) / LIMIT weight |
| 4 | PC spacing **20px trước / 12px sau** | `mt=20px mb=12px` | **Pass** |
| 5 | Mobile title **20/28**/800 | 20px / 28px / **700** (xem LIMIT-1) | **Pass** (size+line-height) / LIMIT weight |
| 6 | Mobile spacing **16px trước / 8px sau** | `mt=16px mb=8px` | **Pass** |
| 7 | Title là **heading thật** | `H2` (Home), `H3` (order / cart / history / delivery) — không còn `SPAN`. Unit test cấm `<span>` và ép đúng tag theo `sh_level` | **Pass** |
| 8 | Title **wrap tối đa 2 dòng** | 360px: `[1,1,1,1,1,1,1,1]` dòng; 0 phần tử dùng ellipsis | **Pass** |
| 9 | **Right slot không chồng lấn** | gap title↔slot mobile `[86,96,87,43,33]px` (≥12), PC `32px` (≥16); right slot `white-space: nowrap`, **0 slot bị ẩn** ở 360px | **Pass** |
| 10 | **Count = 0 hiển thị đúng** | `/portal/order` lọc rỗng → "**0 sản phẩm**" vẫn render (đã gỡ `t-if="products"`) | **Pass** |
| 11 | Count dùng **từ đầy đủ** | "5 sản phẩm" (trước: "5 SP"); cart giữ "1 mặt hàng" đúng ngữ nghĩa đếm SKU của WJ-ORD-022 | **Pass** (xem LIMIT-3) |
| 12 | Action đúng **quyền / keyboard** | Home giữ đúng **5 action** "Xem tất cả" như trước C8 (không thêm/bớt quyền); tab-walk **248/248** stop có focus ring; tap target `44×44` | **Pass** |
| 13 | **Không cộng dồn margin** | header→content `[8,8,18,18,18,18,18,18]px` = 8 (margin header) + 10 (gap container), không cộng đôi; modifier `--flush` xoá được nhịp khi container tự lo → `mt=0 mb=0` | **Pass** |
| 14 | "Danh sách chuyến giao" dùng **variant meta** | `/portal/delivery` PC: `H3` + meta "7 chuyến · Mới nhất trước"; chips lọc **vẫn nằm ngoài** right slot (chúng là `CMP-FC-001`, spec cấm 2 right slot) | **Pass** |
| 15 | Màu theo token | title `rgb(17,24,39)` = `#111827`; meta `rgb(107,114,128)` = `#6B7280`; action `rgb(40,169,223)` = `#28A9DF` — tất cả qua `var(--wujia-*)`, 0 hex cứng | **Pass** |
| 16 | Tách rõ **PageHeader / CardHeader / SectionHeader** | Inventory phân loại theo **tổ tiên DOM** chứ không theo tên class; 89 CardHeader giữ nguyên, 3 PageHeader thuộc `CMP-PG-001` | **Pass** (xem LIMIT-2) |
| 17 | **Tối đa MỘT right slot** | Component tự chọn ưu tiên `action` > `control` > `meta`; unit test chứng minh truyền cả 3 chỉ render `action` | **Pass** |

**Tổng: 16/17 bullet Pass (94%)** — vượt ngưỡng ≥90% của §13 về mặt chất lượng component,
**nhưng bullet #2 (migrate toàn bộ) mới đạt 13/18** ⇒ theo kế hoạch C8a/C8b đã chốt với chủ dự án,
issue **giữ ở `Ready for Dev`**, chỉ ghi tiến độ vào ledger, đóng khi C8b xong.

---

## 2. Số đo máy

| Hạng mục | Kết quả |
|---|---|
| Build `-u` 5 module, `--stop-after-init` | **RC=0**, 0 ERROR / 0 Traceback |
| Đo acceptance (391×844, 360×800, 1920×1080) | **46/46 Pass (100%)** |
| Unit test `wujia_section_header_c8` | 15/15 — 0 failed, 0 error |
| Hồi quy `wujia_debt` + `wujia_delivery_c5` + `wujia_home_c7` + C8 | **63 test — 0 failed, 0 error** |
| Hồi quy diện rộng kiểu B4 (17 route × 2 breakpoint + 5 trang ngoài lưới + 6 width) | **286/286 Pass** — HTTP 200, overflow ngang 0, 0 `pageerror` |
| Tab-walk a11y C6 (5 trang × 25 stop × 2 viewport) | **248/248 stop có focus ring** |

### Ghi chú harness — `input[type=date]` (L7/L9)

Lượt tab-walk đầu ra **240/248**, 8 stop "thiếu ring" đều là `input[type=date]` trong FilterBar
của `/portal/purchase-history` và `/portal/delivery`. Điều tra bằng CDP cho thấy đây là **giới hạn
của harness, không phải mất focus ring**: Chromium đưa focus vào field con trong shadow root của
date input, `document.activeElement` vẫn là host nhưng host **không match `:focus`** (`f: False`,
`fv: False`) nên computed style của host trả `outline: 3px none`. Ép `:focus-visible` bằng
`CSS.forcePseudoState` thì chính các input đó cho `outline: 2px solid rgb(15,124,168)`,
`outline-offset: 2px` — đúng `--wujia-focus-ring`. Đã sửa harness để fallback qua CDP ở đúng các
stop native/shadow ⇒ **248/248**. C8 cũng không đụng tới vùng này: `git diff -U0 | grep -c
"filter-control"` = **0**.

---

## 3. LIMIT — cần BA quyết

**LIMIT-1 — `CMP-SH-001` ghi weight 800, nhưng `UI-06` (Sprint 35) chốt heading TỐI ĐA 700.**
Đo bằng CDP `CSS.getMatchedStylesForNode`: `_wujia_theme.css:35`
`.content-wrapper h1..h6 { font-weight: 700 !important }` (specificity (0,1,1) + `!important`,
kèm comment "UI-06 (Sprint 35): BA yêu cầu font-weight TỐI ĐA 700") đè mọi khai báo 800 của
component. Hai spec BA **mâu thuẫn trực tiếp**. Dev giữ **700** theo đúng tiền lệ đã xử lý ở §5
compact summary (cùng ca 800-vs-700, Dev giữ 700) và để khớp `CMP-PG-001` đang chạy.
👉 **Đề nghị BA gỡ mâu thuẫn**: hoặc sửa `CMP-SH-001` về 700, hoặc nới `UI-06` cho SectionHeader.

**LIMIT-2 — cách đọc rule "heading nằm trong card thì là CardHeader".**
Spec nói heading trong card **không phải** SectionHeader, nhưng chính BA lại chỉ đích danh
"Danh sách chuyến giao" (`/portal/delivery`, nằm trong `.wj-pc-card__head`) và
"Danh sách sản phẩm" (`/portal/order` PC, trong `.wj-pc-order-card`) là SectionHeader.
Dev diễn giải: **card đóng vai container của một danh sách** thì heading đầu danh sách vẫn là
SectionHeader; card nội dung thường thì là CardHeader. Chi tiết ở §2c `docs/c8-heading-inventory.md`.
👉 **Cần BA xác nhận cách đọc này** trước khi C8b nhân ra 5 site còn lại.

**LIMIT-3 — meta của PageHeader trên `/portal/order` vẫn ghi "N SP" và ẩn khi = 0.**
`portal_order_catalog.xml:95-100` (`#wj-ord-mcount`, `#wj-ord-pccount`) là slot meta của
**`CMP-PG-001` PageHeader**, không phải SectionHeader ⇒ nằm ngoài scope C8. SectionHeader ngay
dưới đã dùng "N sản phẩm" và hiện cả khi 0.
👉 **Cần BA xác nhận** có áp luôn rule count (từ đầy đủ + hiện khi 0) cho PageHeader không —
nếu có, xử lý ở C8b cùng `CMP-PG-001`.

**LIMIT-4 — phạm vi C8a.** 5 call site còn lại (`portal_exam`, `portal_debt`,
`portal_notification`, `portal_return_list`, `portal_report`) chưa migrate. ⚠️ CSS class cũ
`.wujia-mhist-listhead*` **chưa được xoá** vì `portal_return_list.xml:189` còn dùng — chỉ xoá
sau khi C8b chuyển nốt.

---

## 4. Ngoài scope nhưng đã sửa (chặn build)

`wujia_franchise/models/wujia_franchise_inspection_question.py` seed dữ liệu trong `init()`,
gây `psycopg2.errors.UndefinedTable` (RC=255) trên **mọi** build. Đây là **bug #2 của L15 tái diễn**
(lần review merge `thai` đã sửa 3 chỗ, sót chỗ thứ 4 do commit `f09082a`). Đã gỡ override `init()`;
`data/wujia_inspection_bootstrap.xml:10` vốn đã seed bằng `<function>`, chạy sau khi bảng đã tồn tại.
⚠️ **Lỗi này có sẵn trên `main` và đang chặn hàng đợi deploy merge `thai` (`538f75e`)** — báo riêng
cho chủ dự án, không phải hệ quả của C8.
