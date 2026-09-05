# Prompt phiên D4c — SurfaceCard lượt 2 (`wj-pc-card` + 9 modifier + `wj-pc-acct-headcard`)

> Dán nguyên khối dưới đây vào phiên mới. Phiên đó **không có** ngữ cảnh D4a/D4b, nên mọi thứ cần đã nằm sẵn ở đây.

---

Chạy `/wujia-start` trước, rồi làm cụm **D4c** — lượt migrate thứ hai của `UI-SURFACECARD-001`
(STT 127, component `CMP-SC-001`, tab `UI Component` gid 488333015).

## Đọc bắt buộc trước khi gõ dòng code nào

1. `docs/d4b-acceptance-matrix.md` — **lượt trước vừa xong**, đây là khuôn bảng đo và là chỗ ghi
   3 cái bẫy đã trả giá. Đọc §4 trước tiên.
2. `docs/d4-surfacecard-inventory.md` — kiểm kê D4a chủ dự án đã duyệt: §3 độ lồng (2 vi phạm
   thật, **cả hai nằm đúng trong phạm vi D4c**), §4 bảng họ, §7 năm chỗ chỏi issue đã nghiệm thu,
   §8 bảng token.
3. `docs/next-session-clusters-D.md` mục **D4** — "🔴 Bài học D4b", **Luật chung #1…#9** (từ D4b có
   thêm #7 chủ-sở-hữu-duy-nhất, #8 gap, #9 chiều cao) và bảng thứ tự lượt.
4. `docs/d3-review-matrix.md` §1 (**RULE 1 / RULE 2** — đo *quan hệ*, không đo hằng số) và
   **§3.4** — câu hỏi nhịp header→body 18/12/24/36px ở `/portal/exam/register` **đang treo**.
   Cùng một màn với 2 vi phạm lồng ⇒ **xử một lần**.
5. `docs/01_NGO_GIA_QA_OPERATING_STANDARD.md` — Dev không tự đóng `Done`, chỉ tới `Ready for Retest`.

## Nền đã có sẵn — ĐỪNG dựng lại

D4b đã đẻ xong và **đã chạy thật trên 12 thẻ**:

- Component `wujia_portal_layout.wj_surface_card` (`views/wj_surface_card.xml`) — props
  `sc_variant` (`section`/`record`/`summary`/`transactional`, mặc định `section`) ·
  `sc_density` (`compact`/`regular`, mặc định `compact`) · `sc_body` (`padded`/`flush`) ·
  `sc_href` (⇒ bọc `<a class="wj-surface-card-link">`) · `sc_id` · `sc_class` · `sc_link_class`.
  Thân card đi qua **slot `0`**.
- Token `--wujia-surface-radius` (16/14) · `--wujia-surface-pad-compact` (16/12) ·
  `--wujia-surface-pad-regular` (20/14) · `--wujia-surface-gap` (12/8), override trong
  `@media (max-width: 991.98px)` của `_variables.css`.
- CSS chủ sở hữu duy nhất `.wj-surface-card` + `--regular` / `--summary` / `--flush` ở cuối khối
  card của `_components.css`.
- Test khuôn: `custom/wujia_portal_layout/tests/test_d4_surface_card.py` (22 test, tag
  `wujia_surface_card_d4`) — thêm lớp mới vào đây, đừng đẻ file test song song.

D4c **chỉ thêm đúng một thứ vào nền**: token nền tonal (xem "Việc mới" bên dưới).

## Phạm vi D4c — họ shell chung của toàn bộ PC

| Họ | Vai trò | Lượt (grep tĩnh) |
|---|---|---:|
| `wj-pc-card` | shell PC dùng chung | **34** |
| `wj-pc-acct-headcard` | shell riêng, **không** phải modifier | **2** |
| 9 modifier chồng lên `wj-pc-card` | chỉ đè padding | (đi kèm, không cộng thêm lượt) |

⚠️ **Kiểm kê D4a ghi `wj-pc-card` 47 lượt / 14 file, grep tĩnh ra 34 dòng.** Chênh lệch này
**phải giải trình trước khi sửa** (nhiều khả năng D4a đếm cả lượt render trong `t-foreach`).
Nhớ luật: **kiểm kê là SÀN không phải TRẦN** — tìm ra lượt D4a bỏ sót thì **ghi bổ sung** vào
`docs/d4-surfacecard-inventory.md`, đừng lặng lẽ sửa.

### Call site (đã grep, đừng grep lại từ đầu)

| File | Dòng | Ghi chú |
|---|---|---|
| `wujia_portal_layout/views/change_password_page.xml` | 24, 78, 89 | |
| `wujia_portal_layout/views/profile_page.xml` | 18 (**headcard**), 39 | |
| `wujia_portal_layout/views/pc_preview.xml` | 100 | route `/portal/_pc-preview` — trang xem trước nội bộ |
| `wujia_portal_base/views/portal_franchise_information.xml` | 28 (**headcard**), 59, 96 | |
| `wujia_portal_purchase_history/views/portal_history.xml` | 32, 419, 444, 472 | |
| `wujia_portal_delivery/views/portal_delivery.xml` | 12, 410, 441, 474 | |
| `wujia_portal_notification/views/portal_notification.xml` | 25, 357, 380, 403 | `:403` nằm trong `t-if` |
| `wujia_portal_debt/views/portal_debt.xml` | 379, 620 (`wj-debt-pc-card`), 780 (`wj-debt-pc-paycard`) | chạm số đo **C3** |
| `wujia_portal_exam/views/portal_exam.xml` | 71 (`wj-exam-pc-card`), 255 (`wj-exam-pc-fcard`), 448 (`wj-exam-pc-sumcard`), 951 (`wj-exam-pc-dcard`) | `:255` là **thẻ ngoài của 2 vi phạm lồng** |
| `wujia_portal_sale/views/portal_order_catalog.xml` | 16 (`wj-pc-order-card`) | |
| `wujia_portal_support/views/portal_support.xml` | 236 | |
| `wujia_portal_report/views/portal_report_orders.xml` | 244, 264, 294 (`wj-rep-pccard--chart/--state/--top`) | 🔴 **route 500 có sẵn — KHÔNG đo được** |
| `wujia_portal_inspection/views/portal_inspection_list_templates.xml` · `..._detail_...:89` · `..._remediation_...:41` | 30, 89, 41 | 🔴 **module `uninstalled` trên DB dev — KHÔNG đo được** |

### 🟡 Quyết định phải HỎI chủ dự án ngay đầu phiên

**30/36 call site đo được ở local; 6 cái không** (3 của `wujia_portal_report` vì
`/portal/reports/orders` đang 500 — cụm R3; 3 của `wujia_portal_inspection` vì module
`uninstalled`). Luật "không có bảng đo trước–sau thì không migrate" (chính nó đẩy
`wj-pc-metric-card` xuống D4e) đụng đúng chỗ này.

**Đề xuất của Dev** (nêu ra rồi chờ chốt, đừng tự làm):
- **CSS + token hội tụ cho CẢ họ** — không tránh được, `.wj-pc-card` là một rule.
- **XML chỉ migrate 30 call site đo được**; 6 cái còn lại đi cùng D4e (report) và lượt Khảo sát
  (inspection), khi route đo được. Ghi thành **LIMIT** trong ledger, không im lặng bỏ.

## Neo CSS chính xác (đã đọc, đừng grep lại từ đầu)

`custom/wujia_portal_layout/static/assets/css/_pc_components.css`
- `:161` `.wj-pc-card` — `background: var(--wj-pc-card)` · `border: 1px solid var(--wj-pc-border-soft)`
  · `border-radius: var(--wj-pc-card-radius)` = **18px** · `padding: 24px`. **Không có shadow** ⇒
  họ này khác D4b: viền và bóng **đã đúng**, việc thật là **radius 18→16 và padding 24→16**.
- `:167` `.wj-pc-card__head` (`margin-bottom: 18px`) · `:174/:175` `__title` / `__subtitle`
  · `:344/:345` `__count` / `__title--sm` — **đây là phần tiêu đề, KHÔNG thuộc SurfaceCard**,
  ranh giới `CMP-CH-001`. Đừng gộp.
- `:291`, `:364` — **hai rule KHÁC cũng ăn `--wj-pc-card-radius`**, đi kèm khi đổi token.

`custom/wujia_portal_layout/static/assets/css/_variables.css`
- `:75` `--wj-pc-card: var(--wujia-bg-card)` ← **đây là token MÀU NỀN, không phải radius.**
  Tên gần giống nhau, đọc nhầm là hỏng cả bảng màu PC.
- `:84` `--wj-pc-card-radius: 18px` ← **DRIFT** so với `:120` `--wujia-card-radius: 16px`
  (hai token cùng vai trò). Hội tụ **18→16**.
- `:77` `--wj-pc-border-soft` = `#EEF2F5` — dùng lại, đừng viết hex thô.

`custom/wujia_portal_layout/static/assets/css/_pc_account.css`
- `:19-21` (`--wj-pc-card-radius`) · `:53-56` `.wj-pc-acct-headcard` — `background`/`border`/
  `border-radius`/`padding: 22px 24px`. Đây là **shell thứ hai**, migrate cùng lượt.
- `__box` bên trong headcard **đã là `#F8FAFC`** — inventory §3 xác nhận **đúng chuẩn tonal BA**,
  giữ nguyên, dùng nó làm mẫu cho việc mới bên dưới.

### 9 modifier — sửa `.wj-pc-card` mà quên chúng thì "y như cũ"

| Modifier | Neo | Đè |
|---|---|---|
| `wj-debt-pc-card` | `wujia_portal_debt/static/src/css/portal_debt.css:557` | `padding: 22px 24px` |
| `wj-debt-pc-paycard` | `portal_debt.css:668` | `max-width: 720px` (không đè padding) |
| `wj-exam-pc-card` | `wujia_portal_exam/static/src/css/portal_exam.css:769` | `22px 24px 24px` |
| `wj-exam-pc-fcard` | `portal_exam.css:979` | `18px 24px 10px` |
| `wj-exam-pc-sumcard` | `portal_exam.css:980` | `18px 24px 24px` |
| `wj-exam-pc-dcard` | `portal_exam.css:828` | `20px 24px 24px` |
| `wj-pc-order-card` | `wujia_portal_sale/static/src/css/portal_order.css:42` | `20px 24px` |
| `wj-rep-pccard` | `wujia_portal_report/static/src/css/portal_report.css:104` | `padding: 0` ⇒ **đúng ca `flushBody`** |
| (`wj-dlv-pc-card` trong XML nhưng **không có rule CSS**) | — | kiểm lại: lớp chết? ghi vào inventory |

🔴 Chúng nằm ở **file CSS của module khác**, nạp **sau** `_pc_components.css` trong bundle ⇒
cùng đặc hiệu `(0,1,0)` nhưng **thắng theo thứ tự nguồn**. Đây chính là chỗ "sửa xong vẫn y như
cũ". Áp **Luật chung #7**: dáng khung về một chủ duy nhất là `.wj-surface-card`; modifier chỉ
được giữ phần **không phải dáng khung** (vd `max-width`), phần padding phải map sang
`sc_density` chứ không viết lại.

## 🔴 Bốn cái bẫy đã dò sẵn

1. **`--wj-pc-card` ≠ `--wj-pc-card-radius`.** Cái đầu là **màu nền**. Đọc lướt là đổi nhầm.
2. **Đổi `--wj-pc-card-radius` 18→16 kéo theo 4 rule ngoài họ**: `_pc_account.css:21`,
   `_pc_components.css:291`, `:364`, và `wujia_portal_sale/.../portal_order.css:88`
   (`border-radius` + `padding: 20px 22px`). Phải **liệt kê từng cái, xác nhận nó cũng nên là 16**,
   hoặc tách token riêng như D4b đã làm với `--wujia-surface-radius`. **Không đổi mù.**
3. **`/portal/exam/register` mang 2 vi phạm "thẻ trắng lồng thẻ trắng"** mà quét tĩnh không thấy:
   `.wj-exam-pc-cal` (lịch chọn ngày thi) và `.wj-exam-pc-slots` (khung giờ) nằm trong
   `.wj-pc-card.wj-exam-pc-fcard` @1440. **Đây là màn PHẢI CHỤP ẢNH.** Cùng màn đó, D3 REVIEW
   §3.4 còn treo câu hỏi nhịp header→body 18/12/24/36px ⇒ xử một lần, đừng chạm hai lần.
4. **Chỏi issue đã nghiệm thu — ghi LIMIT, KHÔNG tự đè** (inventory §7): số đo **C3** màn Công nợ
   đã Pass với `wj-debt-pc-card` `p 22 24`; đổi sang 16 là **đổi số đã nghiệm thu** ⇒ phải chạy lại
   bảng đo C3 và ghi rõ. Riêng `.wj-debt-summary { height: 142px }` (`portal_debt.css:104`, S43,
   có test `test_debt_summary_keeps_its_head_wrapper` giữ) **là THIẾT KẾ, ngoài phạm vi D4c** —
   thấy cũng để yên, cùng luật với `wj-auth-card`.

## Việc MỚI của lượt này — token nền tonal (D4b cố ý hoãn sang đây)

BA: *thẻ trắng không được lồng trong thẻ trắng; vùng phụ dùng nền tonal `#F8FAFC` radius 12*.
Hex này hiện nằm dưới **3 tên vai-trò khác nhau** (`--wj-pc-table-header-bg` `_variables.css:99` ·
`--wujia-mres-info-bg` `:257` · `--wujia-filter-field-bg` `:269`) — đúng định nghĩa DRIFT.

⇒ Thêm `--wujia-surface-tonal: #F8FAFC` + `--wujia-surface-tonal-radius: 12px`, và một biến thể
lồng của SurfaceCard (đề xuất: `sc_tone="tonal"` ⇒ `.wj-surface-card--tonal`, **không viền,
không bóng**). **Hỏi trước khi hội tụ 3 token cũ về nó** — đó là việc ngoài phạm vi D4c.

## Số BA phải đạt (`CMP-SC-001`)

| | desktop | mobile |
|---|---|---|
| radius | 16 | 14 |
| border | 1px `#EEF2F5` | 1px `#E5E7EB` |
| shadow mặc định | **không** | **không** |
| padding | compact 16 · regular 20 | compact 12 · regular 14 |
| gap trong | 12 | 8 |
| chiều cao | **không khoá cứng** | — |

Biến thể D4a đã map: `wj-pc-card` = **`section`**, `compact`, `padded`, `interactive: none`
(⇒ `p 24→16`, `r 18→16`) · `wj-rep-pccard` = **`flushBody`** · `wj-pc-acct-headcard` = `record`,
**`regular`**, `padded` (⇒ `p 22/24→20`, `r 18→16`).

⚠️ **`padding 24→16` là thay đổi hình học lớn nhất từ đầu cụm D** — 30+ thẻ cùng hẹp lại 8px mỗi
bên. Bảng đo trước–sau và ảnh là **bắt buộc**, không phải tuỳ chọn.

## Nghiệm thu — không đủ thì không được ghi Ready for Retest

1. **Bảng đo trước–sau** đủ **5 khổ BA (1440 / 1024 / 992 / 390 / 360)** × mọi route đo được:
   `/portal/history` · `/portal/delivery` · `/portal/notification` · `/portal/debt` ·
   `/portal/debt/history` · `/portal/exam` · `/portal/exam/register` · `/portal/order/catalog` ·
   `/portal/support` · `/portal/profile` · `/portal/change-password` ·
   `/portal/franchise-information` · `/portal/_pc-preview`.
   Mỗi ô ghi: chiều cao trang · **số record thấy trong viewport** (nghiệm thu BA #11: **không được
   giảm**) · radius/border/padding/shadow/gap bằng `getComputedStyle` · **tổng node đã duyệt**
   (0 = đo rỗng, không phải sạch). Khuôn có sẵn: `scratchpad/d4b_measure.py`.
2. 🔴 **Đo TUYỆT ĐỐI nhịp header→body** (`scratchpad/d4b_rhythm.py`) — **RULE 1 + RULE 2 là điều
   kiện CẦN, KHÔNG ĐỦ**: chúng đo *sự không đều giữa các card*, nên sai số **đều tay trên mọi
   card** lọt qua sạch sẽ. D4b đã dính đúng bẫy này (nhịp phồng 12→24px, mọi rule vẫn xanh).
3. **Chạy lại RULE 1 + RULE 2**: `python3 scratchpad/d3_review.py --base http://127.0.0.1:8072
   --portal-login anh.owner --out <x>.json` rồi `d3_analyze.py`. **`--portal-login` mặc định là
   `None` ⇒ rơi về `admin` ⇒ 0 bề mặt mà vẫn chạy xong** (bẫy "Pass rỗng"). Bắt buộc truyền.
4. **Chụp ảnh trước–sau** (`scratchpad/d4b_shot.py`): `/portal/exam/register` @1440 (**bắt buộc,
   2 vi phạm lồng**) · `/portal/debt` · `/portal/history` · `/portal/profile`, thêm @390.
   Bài học D3e: số Pass hết mà bố cục vẫn vỡ, chỉ ảnh mới bắt được.
5. **Guard chứng minh bằng đột biến** (`scratchpad/d4b_mutate.sh` là khuôn): sửa CSS/template cho
   sai → **đúng test đó phải đỏ** → hoàn nguyên. Test xanh sẵn không chứng minh gì.
   ⚠️ `subTest` in ra `FAIL: Subtest Lop.test (params)` — bộ dò thiếu chữ `Subtest` sẽ báo guard
   rỗng oan (đã dính ở D4b). Và **cắt log theo số dòng trước mỗi lần chạy**, đừng `tail` cả ngày.
6. **Đặc hiệu CSS** đếm so với **các rule cùng file** và **cùng bundle**, không chỉ so với
   component; `:not()` mang đặc hiệu của tham số (bẫy này đã tái xuất **2 lần** ở D3).
7. **Chụp baseline TRƯỚC khi sửa dòng CSS đầu tiên.** Odoo 19 **tự regenerate asset bundle theo
   checksum** kể cả khi không bật `--dev` ⇒ lỡ sửa rồi thì phải `git stash push` đúng file CSS,
   đo, `stash pop`.
8. `-u` **đúng một lần**, chỉ module `installed`:
   `wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_notification,wujia_portal_debt,wujia_portal_exam,wujia_portal_sale,wujia_portal_support,wujia_portal_report`
   **Không** `-u` / `-i` `wujia_portal_inspection` (đang `uninstalled`), `wj_ks_*`,
   `wujia_portal_remediation` (đã gỡ khỏi DB).
9. Đối chiếu cột `Kết quả mong muốn` của `UI-SURFACECARD-001`, **≥90% cho phần thuộc D4c**.
10. Xong → ghi `docs/qa-issue-ledger.yaml` dạng **tiến độ** (FIX/IMPACT/RETEST/LIMIT của riêng
    lượt D4c), **giữ status `Ready for Dev`** — sau D4c mới phủ ~48/384 lượt (~12%), chưa đủ để
    bàn giao BA retest (tiền lệ `UI-CARDHEADER-001` giữ `Ready for Dev` suốt D3a→D3e).
    Cập nhật `docs/d4-surfacecard-inventory.md` + mục D4 của `docs/next-session-clusters-D.md`.
    Chạy `cd scripts/ba_spec && python3 qa_sync.py` (mặc định là dry-run) để **xem**;
    chỉ `--apply` khi chủ dự án chốt. **Dev không tự đóng `Done`.**

## Ngoài phạm vi D4c — thấy cũng để yên

- `wj-pc-metric-card` (44) — **D4e**, chặn vì cả 2 route đều không đo được.
- Mobile: `wujia-mdash-card` + `mhist`/`mknow`/`mnoti`/`mres`/`mexam` + `wj-filter-card` — **D4d**.
- Bootstrap `.card` thô (75) — **D4f**, cuối cùng.
- `wj-auth-card` (15) — THIẾT KẾ Figma S39, giữ dáng.
- `.wj-debt-summary { height: 142px }` — THIẾT KẾ S43, giữ (inventory §7 dòng 2).
- Nhóm Khảo sát (21) — BA ghi *provisional*, module chưa cài local.
- Hội tụ 3 token cùng hex `#F8FAFC` về `--wujia-surface-tonal` — **hỏi trước**, không tự làm.

## Môi trường

- DB dev `wujia_tea_19`, `wujia_portal_layout` đang ở **19.0.33.0.0** (D4b). Route trả 404 kèm
  *"Không tìm thấy mẫu"* = DB cũ hơn code ⇒ chạy `-u`, đừng đi tìm bug logic.
- Server đo: `http://127.0.0.1:8072` (D4b đã tắt, bật lại khi cần).
  ⚠️ **Hai server trên `8070` / `8071` là DB `wujia_tea_d3f_a` / `_b` của cụm R — đừng đụng.**
- Đăng nhập portal: **`anh.owner` / `wujia@test123`**. **Đừng dùng `admin`** — uid 2 không phải
  user portal franchise, mọi route portal sẽ 404 mà harness vẫn báo "đo được N surface".
  Dò mật khẩu quá 5 lần dính *"Too many login failures"*, phải restart server.
- Harness trong `scratchpad/` (**gitignored, không commit**): `d4b_measure.py` · `d4b_rhythm.py` ·
  `d4b_shot.py` · `d4b_mutate.sh` · `d3_review.py` + `d3_analyze.py` · `d4_nesting.py`.
  Copy sang `d4c_*` rồi sửa, đừng viết lại từ đầu.
- Bump `wujia_portal_layout` **19.0.33.0.0 → 19.0.34.0.0**; module chỉ đổi XML thì không bump.

## Nguyên tắc xuyên suốt

**Ask-don't-assume** · **Read-before-write** · **Perf-first** (portal 1500 user) ·
comment trong code **gọn, 1 dòng đủ ý** · **kiểm kê là SÀN không phải TRẦN** ·
**chủ sở hữu DUY NHẤT của dáng khung** · **`gap` chỉ ở biến thể xếp ngang, cấm ở rule gốc** ·
**không khoá chiều cao — nhưng `min-height` cũng chưa bao giờ làm các thẻ cao bằng nhau,
`height: 100%` mới đúng**.
