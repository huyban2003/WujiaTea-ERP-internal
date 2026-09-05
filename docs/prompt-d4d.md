# Prompt phiên D4d — SurfaceCard lượt 3 (họ **mobile** + `wj-filter-card`)

> Dán nguyên khối dưới đây vào phiên mới. Phiên đó **không có** ngữ cảnh D4a/D4b/D4c, nên mọi thứ cần đã nằm sẵn ở đây.

---

Chạy `/wujia-start` trước, rồi làm cụm **D4d** — lượt migrate thứ ba của `UI-SURFACECARD-001`
(STT 127, component `CMP-SC-001`, tab `UI Component` gid 488333015).

## Đọc bắt buộc trước khi gõ dòng code nào

1. `docs/d4c-acceptance-matrix.md` — **lượt trước vừa xong**, khuôn bảng đo và 4 bài học đã trả giá.
   Đọc §4 (đo nhịp tuyệt đối), §6 (cách mở route không đo được), §9 (đặc hiệu) trước tiên.
2. `docs/d4-surfacecard-inventory.md` — kiểm kê D4a chủ dự án đã duyệt: **§4 bảng họ**,
   §6 bốn chỗ Dev tự quyết (có `wj-filter-card`), §8 bảng token, **§11 đính chính sau D4c**.
3. `docs/next-session-clusters-D.md` mục **D4** — **Luật chung #1…#9** và **🔴 Bài học D4c**.
4. `docs/d4b-acceptance-matrix.md` §4.1 — vì sao `min-height` **không** làm các thẻ cao bằng nhau.
5. `docs/01_NGO_GIA_QA_OPERATING_STANDARD.md` — Dev không tự đóng `Done`, chỉ tới `Ready for Retest`.

## Nền đã có sẵn — ĐỪNG dựng lại

Component `wujia_portal_layout.wj_surface_card` (`views/wj_surface_card.xml`) đã chạy thật trên
**48 thẻ** qua D4b + D4c:

- Props: `sc_variant` (`section`/`record`/`summary`/`transactional`, mặc định `section`) ·
  `sc_density` (`compact`/`regular`) · `sc_body` (`padded`/`flush`) · **`sc_tone` (`tonal`)** ·
  `sc_href` (⇒ bọc `<a class="wj-surface-card-link">`) · `sc_id` · `sc_class` · `sc_link_class`.
  Thân card đi qua **slot `0`**.
- Token: `--wujia-surface-radius` (16/**14**) · `--wujia-surface-pad-compact` (16/**12**) ·
  `--wujia-surface-pad-regular` (20/**14**) · `--wujia-surface-gap` (12/**8**) ·
  `--wujia-surface-tonal` (`#F8FAFC`) + `--wujia-surface-tonal-radius` (12) — số sau `/` là giá
  trị trong `@media (max-width: 991.98px)` của `_variables.css`, **tức là đúng cột mobile của BA**.
- CSS chủ sở hữu duy nhất `.wj-surface-card` + `--regular` / `--summary` / `--flush` / `--tonal`.
- Test: `custom/wujia_portal_layout/tests/test_d4_surface_card.py` (**33 test**, tag
  `wujia_surface_card_d4`) — thêm lớp `TestSurfaceCardD4d` vào đây, **đừng đẻ file test song song**.

🟢 **D4d là lượt ĐẦU TIÊN dùng cột mobile của component.** D4b/D4c đều là họ PC-only nên nhánh
`@media` mobile của `.wj-surface-card` **viết rồi nhưng gần như chưa ai chạy qua**. Coi như code
mới: đo kỹ ở 390/360, đừng tin là nó đúng vì đã có trong file.

## Phạm vi D4d — 10 họ mobile, **50 call site / 18 file / 10 module**

| Họ | Lượt | File | Số đo hiện tại | Việc phải làm |
|---|---:|---|---|---|
| `wujia-mdash-card` | **30** | 8 | r14 · b1 `#E5E7EB` · **p14** | **đã đúng radius+viền**, chỉ `p 14→12` |
| `wj-filter-card` | **7** | 7 | r14 · b1 `#EEF2F5` · p12 · **gap 10** | viền `#EEF2F5`→`#E5E7EB` · **gap 10→8** (xem bẫy #3) |
| `wujia-mhist-card` | 4 | 1 | r14 · b1 `#E5E7EB` · p16 | `p 16→12` |
| `wujia-mexam-cfcard` | 2 | 1 | r14 · b1 `#EEF2F5` · p16 · gap 14 | `p 16→12` · viền → `#E5E7EB` · gap → 8 |
| `wujia-mexam-selcard` | 2 | 1 | **bg `#F8FAFC`** · r14 · b1 `#EEF2F5` · p`14 16` | ⇒ **`sc_tone="tonal"`** (D4c vừa đẻ) · viền → `#E5E7EB` |
| `wujia-mexam-card` | 1 | 1 | r14 · b1 `#EEF2F5` · p`14 16` · **`<a t-foreach>`** | `p→12` · viền → `#E5E7EB` · **wholeCard** |
| `wujia-mknow-card` | 1 | 1 | r14 · b1 `#E5E7EB` · p14 | `p 14→12` — ⚠️ **thẻ `<article>`**, xem bẫy #2 |
| `wujia-mnoti-detail-card` | 1 | 1 | r14 · b1 `#E5E7EB` · p16 | `p 16→12` |
| `wujia-mres-card` | 1 | 1 | r14 · b1 **`#EEF2F5`** · p`20 16` · `max-width: 420px` | `regular` ⇒ p→14 · viền → `#E5E7EB` · **giữ `max-width`** |
| `wujia-mdelivery-prodcard` | 1 | 1 | r14 · b1 `#E5E7EB` · **p0** + `overflow:hidden` | ⇒ **`sc_body="flush"`**, giữ `overflow` |

⚠️ **Kiểm kê D4a ghi lượt D4d là 51, grep tĩnh ra 50.** Chênh lệch này **phải giải trình trước
khi sửa** (D4c đã có tiền lệ: kiểm kê gom class con BEM vào họ cha). Nhớ luật **kiểm kê là SÀN
không phải TRẦN** — tìm ra lượt bỏ sót thì **ghi bổ sung** vào inventory, đừng lặng lẽ sửa.

### Call site (đã grep, đừng grep lại từ đầu)

`wujia-mdash-card` — 30 lượt, 8 file:

| File | Dòng |
|---|---|
| `wujia_portal_base/views/portal_home.xml` | 377, 422, 457, 493, 523 (đều trong `t-else`), 552, 584 |
| `wujia_portal_return/views/portal_return_detail.xml` | 239, 251, 272, **289** (`t-if="comp"`), 344, **356** (`t-if="rr.image_attachment_ids"`), 370 |
| `wujia_portal_support/views/portal_support.xml` | **180** (`t-else`), 313, 514, 524, **559** (`style="padding:0"`) |
| `wujia_portal_return/views/portal_return_form.xml` | 142, 175, 195, 210 |
| `wujia_portal_base/views/portal_franchise_information.xml` | 189, 227, **255** (`style="padding:0"`) |
| `wujia_portal_delivery/views/portal_delivery.xml` | 524, 543 |
| `wujia_portal_layout/views/profile_page.xml` | 102 |
| `wujia_portal_layout/views/change_password_page.xml` | 113 |

9 họ còn lại:

| File | Dòng | Họ |
|---|---|---|
| `wujia_portal_purchase_history/views/portal_history.xml` | 4 lượt `wujia-mhist-card` + 1 `wj-filter-card` | |
| `wujia_portal_exam/views/portal_exam.xml` | **200** (`<a t-foreach="m_exam_items">`) · 2× `cfcard` · 2× `selcard` · 1× `wj-filter-card` | |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | **349** (`<article>`) · 1× `wj-filter-card` | |
| `wujia_portal_notification/views/portal_notification.xml` | 1× `mnoti-detail-card` · 1× `wj-filter-card` | |
| `wujia_portal_sale/views/portal_order_result.xml` | 1× `wujia-mres-card` | 🔴 **không đo được**, xem dưới |
| `wujia_portal_delivery/views/portal_delivery.xml` | 1× `mdelivery-prodcard` · 1× `wj-filter-card` (`id="wj-dlv-mform"`) | |
| `wujia_portal_support/views/portal_support.xml` · `wujia_portal_return/views/portal_return_list.xml` | 1× `wj-filter-card` mỗi file | |

### 🟡 Một chỗ KHÔNG đo được — hỏi chủ dự án ngay đầu phiên

`wujia-mres-card` (`portal_order_result.xml`) chỉ render **sau `POST /portal/order/submit`** với
`flow=m` (PRG, màn "đã gửi đơn" / "ngoài khung giờ"). Muốn đo là phải **tạo đơn thật**.

- Trên **UAT tuyệt đối không** — QA §10 cấm tạo đơn/hoá đơn/email thật.
- Trên **DB copy cô lập** thì được (tiền lệ D4c: `wujia_tea_d4c` cổng 8074).

**Đề xuất của Dev** (nêu ra rồi chờ chốt): dựng DB copy, POST đúng một đơn để chụp 2 màn kết quả,
rồi **xoá DB copy**. Không chốt thì migrate CSS + XML và ghi **LIMIT**, đo trên UAT sau deploy.

## Neo CSS chính xác (đã đọc, đừng grep lại từ đầu)

`custom/wujia_portal_layout/static/assets/css/_variables.css`
- `:248-264` — **cả họ mobile đứng trên bộ token `--wujia-morder-*`**:
  `--wujia-morder-card-bg: #FFFFFF` · `--wujia-morder-border: #E5E7EB` (**= đúng số BA**) ·
  `--wujia-morder-divider: #EEF2F5` · `--wujia-morder-radius: 14px` (**= đúng số BA**).
  ⇒ **radius và viền của họ mobile phần lớn ĐÃ ĐÚNG.** Việc thật của D4d là **padding** và
  **mấy chỗ dùng nhầm `--wujia-morder-divider` / `--wujia-border-soft` làm màu viền**.
- `:34` `--wujia-border: #E5E7EB` · `:35` `--wujia-border-soft: #EEF2F5` — hai token này **cùng
  hex** với `morder-border` / `morder-divider`. **Hỏi trước khi hội tụ**, ngoài phạm vi D4d.

`custom/wujia_portal_layout/static/assets/css/_components.css`
- `:230-239` `.wj-filter-card` — `gap 10` · `padding 12` · `margin-bottom 16` · viền
  `--wujia-border-soft`. `:240` `.wj-filter-card > .wj-filter-chips { margin-top: -2px }` ← **bẫy #3**.
- `:1767-1774` `.wujia-mres-card` — `max-width: 420px` (**không phải dáng khung, giữ lại**) ·
  `padding: 20px 16px` · viền `--wujia-morder-divider`.
- `:2059-2065` `.wujia-mhist-card` — `padding 16` · `margin-bottom 14` (**margin không phải dáng
  khung** — giữ, hoặc chuyển sang gap của danh sách, **quyết một lần rồi ghi**).
- `:2276-2281` `.wujia-mknow-card` · `:2526-2534` `.wujia-mdash-card` (+ `:2535`
  `a.wujia-mdash-card:hover { color: inherit }` — **giữ**, đó là màu chữ, không phải dáng khung).

CSS module khác — nạp **sau** `_components.css`, cùng đặc hiệu `(0,1,0)` mà **thắng theo thứ tự
nguồn** (chỗ "sửa xong vẫn y như cũ"):

| Rule | Neo | Đè |
|---|---|---|
| `.wujia-mexam-card` | `wujia_portal_exam/static/src/css/portal_exam.css:78` | bg **`#FFFFFF` hex thô** · r **14 hex thô** · `p 14 16` |
| `.wujia-mexam-selcard` | `portal_exam.css:213` | bg **`#F8FAFC`** · r14 · gap 12 |
| `.wujia-mexam-cfcard` | `portal_exam.css:533` | bg `#FFFFFF` · r14 · p16 · gap 14 |
| `.wujia-mnoti-detail-card` | `wujia_portal_notification/static/src/css/portal_notification.css:155` | bg/viền/radius/`p 16` |
| `.wujia-mdelivery-prodcard` | `wujia_portal_delivery/static/src/css/portal_delivery.css:133` | bg/viền/radius + **`overflow: hidden`** (giữ) |
| **`.wujia-mnoti .wujia-mknow-card`** | `portal_notification.css:26` | `padding: 9px 12px` — **đặc hiệu (0,2,0)**, xem bẫy #4 |

## 🔴 Năm cái bẫy đã dò sẵn

1. **`:is()` mang đặc hiệu của THAM SỐ MẠNH NHẤT.** `_interaction.css:61/87/111` có 3 danh sách
   `:is(… .wujia-mdash-card, .wujia-mexam-card …)` cho hover/pressed, và trong danh sách có
   `.wj-pc-page-btn:not(.is-active):not(.is-disabled)` ⇒ **cả selector là (0,3,0)**, `:hover` thành
   **(0,4,0)** — đè mọi thứ `.wj-surface-card` viết. Hệ quả: **phải giữ nguyên lớp cũ** qua
   `sc_class` (đúng khuôn D4b/D4c), nếu không hover/pressed của thẻ bấm-cả-khối **chết câm**.
   Đây là lần **thứ ba** bẫy đặc hiệu `:not()`/`:is()` xuất hiện trong cụm D — đếm bằng tay, đừng đoán.
2. **`<article>` và `<a>` không thành `<div>` được.** QWeb Odoo 19 **không có** directive đổi tên
   thẻ (`ir_qweb.py:1705`, chốt ở C8) ⇒ `t-call` sẽ nuốt mất thẻ. Hai ca:
   - `portal_knowledge.xml:349` `<article class="wujia-mknow-card wujia-mknow-article">` — landmark.
   - `portal_exam.xml:200` `<a t-foreach="m_exam_items" t-att-href=…>` — **wholeCard**, mất `<a>`
     là mất link. Component **có** `sc_href` (bọc `<a class="wujia-surface-card-link">`) nhưng nó
     đặt link **NGOÀI** card, còn ở đây `<a>` **CHÍNH LÀ** card ⇒ đổi cấu trúc là đổi cả hover.
     Cách D4c đã chốt cho ca này: **thêm thẳng class `.wj-surface-card`** vào thẻ gốc, giữ nguyên tag.
     **Trình cho chủ dự án chọn**, đừng tự đổi tag.
3. **`wj-filter-card` gap 10 là con số BÙ, không phải con số thiết kế.** `:240` có
   `.wj-filter-card > .wj-filter-chips { margin-top: -2px }` với comment *"dates→chips gap 8
   (bù gap card 10)"* ⇒ **kéo gap về 8 thì PHẢI gỡ luôn `-2px`**, không thì khoảng cách thành 6px.
   Đây đúng kiểu lỗi "đều tay" mà RULE 1/2 **không bắt được** — phải **đo tuyệt đối**.
4. **`.wujia-mnoti .wujia-mknow-card` là rule LIÊN MODULE, đặc hiệu (0,2,0).** Màn Thông báo
   **mượn lại** class của màn Kiến thức rồi ép `padding: 9px 12px`. Rút padding khỏi rule gốc mà
   quên rule này thì `/portal/notification` giữ nguyên 9/12 trong khi `/portal/knowledge` về 12
   ⇒ **hai màn lệch nhau**. Quyết: hoặc giữ có chủ đích (ghi LIMIT), hoặc hội tụ về 12 (đo lại cả
   hai màn). **Không im lặng.**
5. **Hai `style="padding:0;"` inline** (`portal_franchise_information.xml:255`,
   `portal_support.xml:559`) — inline **thắng mọi CSS**. Đó chính là ca `flushBody`: chuyển sang
   `sc_body="flush"` và **xoá inline style**, đừng để cả hai cùng tồn tại.

## Số BA phải đạt (`CMP-SC-001`) — D4d là cột **mobile**

| | mobile | desktop (để đối chiếu) |
|---|---|---|
| radius | **14** | 16 |
| border | **1px `#E5E7EB`** | 1px `#EEF2F5` |
| shadow mặc định | **không** | không |
| padding | **compact 12 · regular 14** | 16 · 20 |
| gap trong | **8** | 12 |
| chiều cao | **không khoá cứng** | — |
| touch target | **44×44px** cho action | — |

⚠️ Riêng D4d có thêm **acceptance touch target 44×44** (BA ghi *"action mobile 44×44px"*) —
`wujia-mdash-card` và `wujia-mexam-card` là **wholeCard** nên phải đo cả vùng bấm, không chỉ dáng.

## Nghiệm thu — không đủ thì không được ghi ledger

1. **Bảng đo trước–sau** đủ **5 khổ BA (1440 / 1024 / 992 / 390 / 360)** × mọi route đo được:
   `/portal` · `/portal/purchase-history` · `/portal/knowledge` · `/portal/notification` +
   `/portal/notification/<id>` · `/portal/exam` · `/portal/exam/register` · `/portal/delivery` +
   `/portal/delivery/<id>` · `/portal/return` + `/portal/return/new` + `/portal/return/<id>` ·
   `/portal/support` + `/portal/support/new` · `/portal/profile` · `/portal/change-password` ·
   `/portal/franchise-information`.
   Mỗi ô ghi: chiều cao trang · **số record thấy trong viewport** (nghiệm thu BA #11: **không được
   giảm**) · radius/border/padding/shadow/gap bằng `getComputedStyle` · **tổng node đã duyệt**
   (0 = đo rỗng, **không phải** sạch). Khuôn: `scratchpad/d4c_measure.py`.
   🔴 **Trọng số ngược với D4c**: đây là họ mobile ⇒ **390/360 là khổ chính**, 1440 chỉ để chứng
   minh **không rò rỉ sang PC**.
2. 🔴 **Đo TUYỆT ĐỐI nhịp header→body** (`scratchpad/d4c_rhythm.py`) — **RULE 1 + RULE 2 là điều
   kiện CẦN, KHÔNG ĐỦ**: chúng đo *sự không đều giữa các card*, nên sai số **đều tay trên mọi
   card** lọt qua sạch sẽ (D4b dính đúng bẫy này). Thêm phép đo riêng cho **bẫy #3** (gap chips).
3. **Đo touch target** của `wujia-mdash-card` / `wujia-mexam-card` @390: cạnh nhỏ nhất **≥44px**.
4. **Chạy lại RULE 1 + RULE 2**: `python3 scratchpad/d3_review.py --base http://127.0.0.1:8072
   --portal-login anh.owner --out <x>.json` rồi `d3_analyze.py`. **`--portal-login` mặc định là
   `None` ⇒ rơi về `admin` ⇒ 0 bề mặt mà vẫn chạy xong** (bẫy "Pass rỗng"). Bắt buộc truyền.
5. **Chụp ảnh trước–sau** @390 **và** @360 (`scratchpad/d4c_shot.py`): `/portal` (7 thẻ
   `mdash-card` — màn dày nhất) · `/portal/return/<id>` (7 thẻ) · `/portal/support` (5 thẻ) ·
   `/portal/exam` (wholeCard) · `/portal/knowledge` (thẻ `<article>`). Bài học D3e: số Pass hết
   mà bố cục vẫn vỡ, **chỉ ảnh mới bắt được**.
6. **Guard chứng minh bằng đột biến** — `scratchpad/d4c_mutate.sh` là khuôn **đã chạy đúng 10/10**,
   copy sang `d4d_mutate.sh` và đổi tên lớp test. Sửa CSS/template cho sai → **đúng test đó phải
   đỏ** → hoàn nguyên. Test xanh sẵn không chứng minh gì.
   ⚠️ `subTest` in ra `FAIL: Subtest Lop.test (params)` — bộ dò thiếu chữ `Subtest` báo guard rỗng
   oan. Và **cắt log theo số dòng trước mỗi lần chạy**, đừng `tail` cả ngày.
   ⚠️ Guard **so chuỗi con là bẫy**: `top: var(--wj-pc-content-padding)` *chứa* chữ "padding" mà
   không hề khai `padding`. Dùng lại helper `_declares()` / `PROP` đã có sẵn trong file test D4c.
7. **Đặc hiệu CSS** đếm so với **các rule cùng file** và **cùng bundle**, không chỉ so với
   component. Nhớ bẫy #1: `:is()` lấy đặc hiệu của tham số mạnh nhất.
8. **Chụp baseline TRƯỚC khi sửa dòng CSS đầu tiên.** Odoo 19 **tự regenerate asset bundle theo
   checksum** kể cả khi không bật `--dev` ⇒ lỡ sửa rồi thì phải `git stash push` đúng file CSS,
   đo, `stash pop`.
9. `-u` **đúng một lần**, chỉ module `installed`:
   `wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_notification,wujia_portal_knowledge,wujia_portal_exam,wujia_portal_sale,wujia_portal_support,wujia_portal_return`
   **Không** `-u`/`-i` `wujia_portal_inspection` (đang `uninstalled`), `wj_ks_*`.
10. Đối chiếu cột `Kết quả mong muốn` của `UI-SURFACECARD-001`, **≥90% cho phần thuộc D4d**.
11. Xong → ghi `docs/qa-issue-ledger.yaml` dạng **tiến độ** (FIX/IMPACT/RETEST/LIMIT của riêng
    lượt D4d), **giữ status `Ready for Dev`** — sau D4d mới phủ ~98/384 lượt (~26%), chưa đủ để
    bàn giao BA retest (tiền lệ `UI-CARDHEADER-001` giữ `Ready for Dev` suốt D3a→D3e).
    Viết `docs/d4d-acceptance-matrix.md` (khuôn `d4c-acceptance-matrix.md`), cập nhật
    `docs/d4-surfacecard-inventory.md` + mục D4 của `docs/next-session-clusters-D.md`.
    Chạy `cd scripts/ba_spec && python3 qa_sync.py` (mặc định dry-run) để **xem**;
    chỉ `--apply` khi chủ dự án chốt. **Dev không tự đóng `Done`.**

## Việc CHỜ CHỦ DỰ ÁN QUYẾT — mang sang từ D4c, đừng tự làm

**Nhịp header→body toàn portal PC** đo được (D4c matrix §4): `12px×32 · 18px×14 · 23px×2 ·
25px×2 · 0px×2`. Truy nguyên đủ 5 giá trị: phần lớn độ lệch do **`.wj-pc-card__head`** (18px) và
2 override của exam (23/25px) **chưa migrate CMP-CH-001**, không phải do khung. Chủ dự án chưa
chốt "kéo hết về 12 hay giữ". **Hỏi lại đầu phiên** — nếu chốt kéo về 12 thì đó là 4 dòng CSS ở
3 module, làm gọn trong D4d luôn.

## Ngoài phạm vi D4d — thấy cũng để yên

- `wj-pc-metric-card` (44) — **D4e**, cùng lượt với `wj-rep-mcard`.
- `wj-rep-mcard` (16) — **D4e**; `/portal/reports/orders` **500 có sẵn** với tz `Asia/Saigon`
  (cụm R3). D4c đã chứng minh cách mở: đổi tz user **trên DB copy** thì route trả 200.
- Bootstrap `.card` thô (75) — **D4f**, cuối cùng.
- `wj-auth-card` (15) — THIẾT KẾ Figma S39, giữ dáng.
- `wujia-msubmit-card` · `modal-card` · `summary-2x2-card` · `wj-dist-card` — overlay / nhóm
  Khảo sát, inventory §5 đã loại.
- Nhóm Khảo sát (21) — BA ghi *provisional*, module `uninstalled` trên DB dev.
- Hội tụ `--wujia-border` ↔ `--wujia-morder-border` (cùng `#E5E7EB`) và
  `--wujia-border-soft` ↔ `--wujia-morder-divider` (cùng `#EEF2F5`) — **hỏi trước**, không tự làm.
- `.wujia-mhist-card { margin-bottom: 14px }` — **margin không phải dáng khung**; đổi nó là đổi
  nhịp danh sách, quyết một lần rồi ghi, đừng tiện tay.

## Môi trường

- DB dev `wujia_tea_19`, `wujia_portal_layout` đang ở **19.0.34.0.0** (D4c). Route trả 404 kèm
  *"Không tìm thấy mẫu"* = DB cũ hơn code ⇒ chạy `-u`, đừng đi tìm bug logic.
- Server đo: `http://127.0.0.1:8072` (D4c đã tắt, bật lại khi cần).
  ⚠️ **`8070`/`8071` là DB `wujia_tea_d3f_a`/`_b` của cụm R — đừng đụng.** `8019` là UAT.
- ⚠️ **`config/odoo.conf` có `dbfilter = ^wujia_tea_19$`** ⇒ chạy DB copy phải **copy conf và
  sửa `db_name`/`dbfilter`**, không thì `Database not found` (đã dính ở D4c).
- Đăng nhập portal: **`anh.owner` / `wujia@test123`**. **Đừng dùng `admin`** — uid 2 không phải
  user portal franchise, mọi route portal sẽ 404 mà harness vẫn báo "đo được N surface".
  Dò mật khẩu quá 5 lần dính *"Too many login failures"*, phải restart server.
- Harness trong `scratchpad/` (**gitignored, không commit**): `d4c_measure.py` · `d4c_rhythm.py` ·
  `d4c_shot.py` · `d4c_mutate.sh` · `d4c_c3_recheck.py` · `d4c_six.py` (khuôn đo trên DB copy) ·
  `d3_review.py` + `d3_analyze.py`. **Copy sang `d4d_*` rồi sửa, đừng viết lại từ đầu.**
- Bump `wujia_portal_layout` **19.0.34.0.0 → 19.0.35.0.0**; module chỉ đổi XML thì không bump.

## Nguyên tắc xuyên suốt

**Ask-don't-assume** · **Read-before-write** · **Perf-first** (portal 1500 user) ·
comment trong code **gọn, 1 dòng đủ ý** · **kiểm kê là SÀN không phải TRẦN** ·
**chủ sở hữu DUY NHẤT của dáng khung** · **`gap` chỉ ở biến thể xếp ngang, cấm ở rule gốc** ·
**không khoá chiều cao — `min-height` chưa bao giờ làm các thẻ cao bằng nhau, `height: 100%`
mới đúng** · **đo tuyệt đối, đừng chỉ đo quan hệ**.
