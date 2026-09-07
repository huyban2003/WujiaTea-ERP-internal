# C8 — Ma trận nghiệm thu `UI-SECTIONHEADER-001` (STT 83 · `CMP-SH-001`)

§1–§5 = phiên 2026-08-22, branch `dev/2026-08-22-c8`, **phạm vi C8a** (component + 5 route mẫu),
DB copy `wujia_tea_c8` port **8059**. **§6 = phiên 2026-08-23, branch `dev/2026-08-23-c8b`**,
6 call site còn lại, DB copy `wujia_tea_c8b` port **8061**.
Đo bằng máy: Playwright + chromium (env `odoo`); KHÔNG đụng `wujia_tea_19`/8019. Harness ở
`scratchpad/` (`c8_measure.py`, `c8b_measure.py`, `c8_tabwalk.py`, `b4_regression.py`) —
không đưa vào repo theo §13.

---

## 1. Theo từng gạch đầu dòng cột `Kết quả mong muốn`

| # | Yêu cầu (nguyên văn rút gọn) | Đo được | Pass/Fail |
|---|---|---|---|
| 1 | Toàn bộ trang Portal và route con được **audit** đúng loại heading | 183 heading thô → phân loại 132 heading trong scope: **12 SectionHeader / 89 CardHeader / 3 PageHeader / 24 Khác**, cộng 5 construct listhead không phải heading thật → tổng **19 call site** SectionHeader (18 chốt ở C8a + 1 chỗ sót phát hiện ở C8b, `docs/c8-heading-inventory.md` §2d) | **Pass** |
| 2 | Toàn bộ trang Portal và route con được **migrate** | **19/19 call site** đã chuyển (13 ở C8a + 6 ở C8b, xem §6) | **Pass** (từ 72% → 100%) |
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

**Tổng: 17/17 bullet Pass (100%)** sau C8b — bullet #2 từ 13/18 lên **19/19**. Hai LIMIT ở §3
(weight 800-vs-700 và cách đọc rule card) **giữ nguyên**: đó là hai chỗ **hai tài liệu BA mâu
thuẫn nhau**, Dev không tự quyết. Issue chuyển **`Ready for Retest`** (Dev không tự đóng `Done`).

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
👉 **Cần BA xác nhận cách đọc này.** C8b không nhân thêm chỗ nào theo diễn giải này — chỗ duy
nhất rơi vào ca đó (`wujia_portal_inspection` list:34) đã **để lại chờ BA**, xem mục dưới.

**LIMIT-3 — meta của PageHeader trên `/portal/order` vẫn ghi "N SP" và ẩn khi = 0.**
`portal_order_catalog.xml:95-100` (`#wj-ord-mcount`, `#wj-ord-pccount`) là slot meta của
**`CMP-PG-001` PageHeader**, không phải SectionHeader ⇒ nằm ngoài scope C8. SectionHeader ngay
dưới đã dùng "N sản phẩm" và hiện cả khi 0.
👉 **Cần BA xác nhận** có áp luôn rule count (từ đầy đủ + hiện khi 0) cho PageHeader không —
nếu có, xử lý ở C8b cùng `CMP-PG-001`.

~~**LIMIT-4 — phạm vi C8a.**~~ ✅ **Đóng ở C8b 23/08**: 6 call site còn lại đã migrate,
`.wujia-mhist-listhead*` + `.wj-debt-section*` + `.wujia-mexam-sectitle` đã xoá.

**Need Clarification (mới, C8b) — 1 chỗ ở `wujia_portal_inspection`.**
Module giám sát nay đã installed trên UAT nên vào phạm vi. Kiểm kê ra 3 PageHeader + 12
CardHeader + **1 chỗ lửng lơ**: `portal_inspection_list_templates.xml:34` "Danh sách phiếu
khảo sát" nằm trong `.wj-pc-card__head` — **cấu trúc giống hệt** "Danh sách chuyến giao" mà BA
đã tự chỉ đích danh là SectionHeader. Tức là nó phụ thuộc thẳng vào **LIMIT-2**.
👉 Chủ dự án chốt: **để lại chờ BA trả lời câu LIMIT-2**, không đoán. `wujia_portal_remediation`
**cố ý bỏ ngoài** (code đã bị xoá ở `f789a56`, UAT `uninstalled`).

---

## 4. Ngoài scope nhưng đã sửa (chặn build)

`wujia_franchise/models/wujia_franchise_inspection_question.py` seed dữ liệu trong `init()`,
gây `psycopg2.errors.UndefinedTable` (RC=255) trên **mọi** build. Đây là **bug #2 của L15 tái diễn**
(lần review merge `thai` đã sửa 3 chỗ, sót chỗ thứ 4 do commit `f09082a`). Đã gỡ override `init()`;
`data/wujia_inspection_bootstrap.xml:10` vốn đã seed bằng `<function>`, chạy sau khi bảng đã tồn tại.
⚠️ **Lỗi này có sẵn trên `main` và đang chặn hàng đợi deploy merge `thai` (`538f75e`)** — báo riêng
cho chủ dự án, không phải hệ quả của C8.

---

## 5. Đo lại NGAY TRÊN UAT sau khi deploy (22/08/2026)

Deploy xác nhận bằng XML-RPC chỉ-đọc: `wujia_portal_layout **19.0.32.0.0**`, view
`wujia_portal_layout.wj_section_header` có mặt, 6 module cùng ghi lúc 16:07 22/08; trình duyệt
nhận đúng `_components.css?v=1172` + `_pc_components.css?v=1172`.
Đo bằng tài khoản `admin`, **chỉ đọc**: không tạo đơn/hoá đơn/email, không đổi quyền, không sửa
dữ liệu (cookie `wujia_active_franchise_id` là cookie phía trình duyệt, không ghi gì vào DB;
harness bản UAT đã **gỡ hẳn** bước thêm vào giỏ mà bản local dùng).

| Hạng mục | Local (`wujia_tea_c8`) | **UAT sau deploy** |
|---|---|---|
| Acceptance `CMP-SH-001` @391/360/1920 | 46/46 | **46/46** |
| Hồi quy diện rộng kiểu B4 | 286/286 | **286/286** |
| Tab-walk a11y (5 trang × 2 viewport) | 248/248 | **250/250** |

Vì UAT có `website_sale` + 5 `website_sale_*` nên bundle frontend khác local (L10/L14 —
đúng chỗ C6 và C7 từng "local đẹp, UAT than"). Lần này số đo trùng khít: title 20/28 mobile và
22/30 PC, nhịp 16/8 và 20/12, màu `rgb(17,24,39)` / `rgb(107,114,128)` / `rgb(40,169,223)`,
count "5 sản phẩm" và "0 sản phẩm" khi lọc rỗng, `/portal/delivery` PC ra variant meta
"2 chuyến · Mới nhất trước" và chips lọc vẫn nằm ngoài right slot.

### Hai lần harness sai, KHÔNG phải code sai (L7/L9)

1. **Lượt B4 đầu ra 270/286.** 16 ô đỏ đều ở 4 trang chi tiết
   (`/portal/delivery/3`, `/portal/notification/41`, `/portal/support/40`, `/portal/return/12`):
   trang **redirect về danh sách** kể cả khi đã chọn cửa hàng. Nguyên nhân: đó là **id của DB
   local**, đọc XML-RPC trên UAT thì cả 4 đều `KHÔNG TỒN TẠI` (id thật lần lượt là 2 / 19 / 16 / 10).
   Sửa id trong harness ⇒ **286/286**. C8 không đụng template chi tiết nào.
2. **`input[type=date]` trong FilterBar** — như đã ghi ở §2, host không match `:focus` khi
   Chromium đưa focus vào shadow root; harness đã fallback qua CDP nên UAT ra 250/250.

⇒ Không phát hiện khác biệt nào giữa local và UAT. Ba LIMIT ở §3 giữ nguyên, chờ BA.

---

## 6. C8b — 6 call site còn lại (23/08/2026, branch `dev/2026-08-23-c8b`)

DB copy cô lập **`wujia_tea_c8b` port 8061** (nền `wujia_tea_mt2` = DB đã cài sẵn + merge
`thai`, gần UAT nhất; KHÔNG đụng `wujia_tea_19`/8019 lẫn `wujia_tea_c8`/8059). Worktree
`WujiaTea-c8b`. Harness `c8b_measure.py` + `b4_regression.py` + `c8b_tabwalk.py` ở scratchpad,
không vào repo (§13).

### 6a. Đã migrate

| Route | File:dòng | Level | Right slot | Đo được |
|---|---|:---:|---|---|
| `/portal/debt` | `portal_debt.xml:209` | H2 | `action` khi còn hoá đơn ẩn, không thì `meta` | 20/28/700, `#111827`; meta `1 hóa đơn` 14/20/700 `#6B7280`; nhịp 16/8; tối đa 1 slot |
| `/portal/debt/payment-history` | `:512` | H2 | `meta` | 20/28/700; `1 giao dịch`; header nằm THẲNG trong slot `#wj-debt-hist-mbody` |
| `/portal/debt/pay` | `:688` | H2 | — | Heading thật, giữ dáng nhãn 11px, thẻ vẫn cao **150px**, nội dung không tràn (ca dung hoà §2e inventory) |
| `/portal/exam/register` bước 3 | `portal_exam.xml:759` | H2 | — | 20/28/700 — **chỗ C8a sót** |
| `/portal/exam` chi tiết | `:1036` | H2 | — | 20/28/700; hai chỗ "Danh sách nhân sự" nay **cùng một cỡ** (trước 16 vs 20) |
| `/portal/return` | `portal_return_list.xml:189` | H3 | `meta` | Từ `div`+`span` thành `H3` thật; `5 yêu cầu`; nhịp 16/8 |

### 6b. Số đo máy

| Hạng mục | Kết quả |
|---|---|
| Build `-u` 6 module (`layout,debt,exam,return,sale,inspection`), `--stop-after-init` | **RC=0** |
| Acceptance C8b @391/360/1920 | **62/62 Pass (100%)** |
| Acceptance C8a chạy lại (13 call site cũ) | **46/46** — không hồi quy dù đã xoá CSS dùng chung |
| Test `wujia_section_header_c8` + `wujia_debt` + `wujia_delivery_c5` + `wujia_home_c7` | **64 test — 0 failed, 0 error** |
| Hồi quy diện rộng kiểu B4 (17 route × 2 breakpoint + 5 trang ngoài lưới + 6 width) | **286/286** |
| Tab-walk a11y **9 trang** × 2 viewport (thêm debt / payment-history / return / exam) | **447/447 stop có focus ring** |

### 6c. Thay đổi CSS + nhịp dọc

- **Xoá hẳn**: `.wujia-mhist-listhead` + `.wujia-mhist-listhead-title` (`_components.css`),
  `.wj-debt-section*` (`portal_debt.css`), `.wujia-mpage .wujia-mexam-sectitle`
  (`portal_exam.css`). Có unit test `test_retired_heading_classes_are_gone` chống tái phát.
- **Nhịp debt đổi theo hướng ĐỒNG BỘ** (chủ dự án chốt 23/08): C3/WJ-DEBT-009 từng chốt riêng
  cho `#wj-debt-hist-mbody` là `gap 12 + margin-top 12` = **24 trên / 12 dưới**. Nay bỏ rule
  riêng đó, debt dùng đúng margin **16/8** của `CMP-SH-001` y hệt 13 chỗ C8a ⇒ thị giác thành
  **28 trên / 20 dưới** (16 + gap 12 và 8 + gap 12) — **cùng cách tính với toàn portal**.
  👉 Đây là con số BA từng nghiệm thu ở C3; đổi là **cố ý**, để một mình một luật thì đúng
  bullet #16 "tách rõ và dùng chung" lại hỏng. Nhờ BA ghi nhận khi retest.
- `?v=1172` → **`?v=1173`** (`_components.css` + `_pc_components.css`). 4 manifest bump:
  layout `19.0.32.1.0` · debt `19.0.4.2.0` · exam `19.0.5.7.0` · return `19.0.2.5.0`.

### 6d. Hai lần harness sai, KHÔNG phải code sai (L7/L9 lặp lại)

1. **Lượt đầu 50/55**, 5 ô đỏ đều ở `/portal/debt` và `/portal/debt/pay`. Nguyên nhân: DB copy
   chỉ có **1 hoá đơn nháp, `franchise_id` NULL** ⇒ trang ra empty state / `/pay` redirect
   (đúng rule C2), không có gì để đo. Chạy `scripts/seed_debt_demo.py` ⇒ **62/62**.
2. **Lưới B4 lượt đầu 282/286**, 4 ô đỏ ở `/portal/support/40`. Đọc DB: ticket 40 thuộc
   **cửa hàng 1**, phiên đo đang ở HCM-01 (id 3) ⇒ bị đẩy về danh sách, đúng như thiết kế.
   Đổi sang ticket 19 (đúng cửa hàng) ⇒ **286/286**. Đây chính là "4 ô đỏ sẵn có" mà C6/C7 ghi
   nhận — nay đã truy ra gốc, **không phải lỗi phân quyền**.

### 6e. Lỗi tự gây, ghi để khỏi lặp

Comment XML chứa `--flush` ⇒ `XMLSyntaxError: Comment must not contain '--'`, build RC=255.
**XML cấm hai gạch nối trong comment** — viết tên modifier BEM có `--` vào comment là chết
build. Diễn đạt bằng lời ("modifier flush") thay vì dán tên class.

---

## §7. Đo lại TRÊN UAT sau khi deploy C8b — 23/08/2026

Chủ dự án deploy `aa26e0e` lên `http://113.161.187.126:8019/` chiều 23/08. Đo lại bằng chính
bộ harness của phiên, chỉ đổi base URL + tài khoản (`admin` / mật khẩu UAT). **Thao tác chỉ
đọc**: chỉ điều hướng GET và đổi cookie chọn cửa hàng, không tạo đơn/hoá đơn/email nào.

| Bộ đo | Kết quả UAT | Ghi chú |
|---|---|---|
| Acceptance C8b (6 call site mới) | **58/60** | 2 ô không đo được, xem dưới |
| Acceptance C8a (13 call site cũ) | **46/46** | không hồi quy dù đã xoá CSS rời |
| Lưới hồi quy B4 (17 route × 2 khổ + 6 chiều rộng) | **286/286** | |
| Đi phím Tab (9 trang × 2 khổ) | **448/448** | mọi điểm dừng còn viền chỉ dấu |

Xác nhận bản build đúng: trang phục vụ `_components.css?v=1173`, và số phần tử mang class rời
`mhist-listhead` trên `/portal/return` là **0**.

**Hai ô không đo được là do DỮ LIỆU UAT, không phải lỗi code.** `/portal/debt/pay` trên UAT
chuyển hướng về `/portal/debt?...&notice=no_due` vì cửa hàng đang xem **không có hoá đơn đến
hạn**, nên khối "Thông tin chuyển khoản" không hề được dựng ra để đo. Đây đúng là hành vi đã
chốt ở C2. Chỗ này đã đo đủ trên DB copy có dữ liệu mồi (thẻ vẫn cao đúng 150px, tiêu đề đi
qua component mà vẫn giữ dáng nhãn 11px) — xem §6b. Nhờ tester khi retest chọn tuần **có hoá
đơn đến hạn** rồi mới bấm Thanh toán để nhìn khối này.

Thêm một phát hiện về dữ liệu UAT: trong 14 cửa hàng, **chỉ cửa hàng thứ 3 có hoá đơn và có
đăng ký thi**. Tester nên chọn đúng cửa hàng đó, nếu không các màn công nợ và đăng ký thi sẽ
ra trạng thái rỗng và tưởng nhầm là lỗi.
