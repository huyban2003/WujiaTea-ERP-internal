# D5f — bảng nghiệm thu DataList lượt 5 (mobile detail-card)

**Ngày:** 2026-09-08 · **Cơ sở:** `46c8217` (D5e) · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 2 call site record — `a.wujia-mreturn-row` (`/portal/return`) và
`a.wujia-mdelivery-row` (`/portal/delivery`), cộng khối **skeleton** của delivery (không phải record).

Lượt đầu tiên dùng variant **`detail-card`**: nó **chưa từng tồn tại** trong repo — component
`wj_data_list` nhận chuỗi `'detail-card'` từ D5b (`wj_data_list.xml:19`) nhưng không có một dòng CSS
nào (`grep -rn "wj-data-list--detail-card"` = **0 hit**). Việc đầu tiên là **dựng** variant, không
phải sửa nó.

Cũng là lượt đầu tiên của cụm D5 làm trang **NGẮN LẠI** và **không thủng ô acceptance #9 nào**.

---

## 0. Ba việc kiểm chứng TRƯỚC khi code

1. **BA vẫn CHƯA trả lời `docs/ba-questions-d5-datalist.md`.** Đọc thẳng tab `5. Issue List`, dòng
   tuyệt đối **119**: `Ready for Dev` · `Ngày cập nhật 25/08/2026` · cột `Ghi chú` **rỗng** ·
   `Kết quả mong muốn` nguyên văn cũ. ⇒ giữ bộ số hiện tại, **ghi provisional**, **KHÔNG** sửa gộp
   D5d + D5e trong lượt này. Không có hai bộ số song song.
2. **Hai file CSS đúng là nằm trong `@media`** — kiểm bằng **độ sâu ngoặc**, không bằng thụt lề
   (bẫy D5e #2 ở tầng khác): `portal_return.css` mở `@media (max-width: 991.98px)` ở dòng 12, rule
   mreturn depth **1**; `portal_delivery.css` mở ở dòng 16, rule mdelivery depth **1**. Lần này tiền
   đề của prompt **đúng** (khác D5e).
3. **Một tiền đề của prompt SAI, và đo mới biết** — xem mục 8 #1: không cần bỏ `gap` ở container.

## 1. Đã làm

| | |
|---|---|
| CSS — **dựng** variant | `_components.css` tầng gốc: `.wj-data-list--detail-card .wj-data-item` mang **dáng** (min-height 96 · padding `12px 14px` · nền · viền · radius **12**, đè token chung `--wujia-morder-radius` 14 **tại chỗ**, KHÔNG sửa token) + `a.wj-data-item{text-decoration:none}` + `+ .wj-data-item{margin-top:8px}`. Đúng kiến trúc hai tầng mà D5e đã tách |
| CSS — layout theo họ | mỗi họ **một** rule trong `@media` của chính module: mreturn `flex · center · gap 8` (`portal_return.css`), mdelivery `flex column · gap 11 · color inherit` (`portal_delivery.css`). Layout **không** được khai lại padding/radius/background — ghim bằng test |
| CSS — khoá rule cũ | `.wujia-mreturn-row:not(.wj-data-item)` và `.wujia-mdelivery-row:not(.wj-data-item)`. **Cố ý KHÔNG khoá** 19 rule con BEM (`-body`, `-head`, `-code`, `-product`, `-divider`, `-meta`, `-top`, `-headmain`, `-cols`, `-col*`, `-skel*`…) — biến thể ô, đúng tiền lệ `wj-pc-td--*` (D5c) và `-bullet`/`-content` (D5d) |
| Ngoại lệ có chủ đích | `a.wujia-mdelivery-row:hover { color: inherit; }` **không khoá** — nó khai đúng **một** thuộc tính `color`, không phải dáng, và phải áp cho cả hàng đã lẫn chưa migrate (nếu khoá thì trên UAT có `website_sale`, `a:hover` của `web.assets_frontend` giành lại màu chữ — bài học C6). Guard miễn trừ theo **tính chất** (rule chỉ khai `color`), không theo tên |
| Call site | 2/2 bọc `t-call="wujia_portal_layout.wj_data_list"` + `dl_variant='detail-card'`; container cũ đi qua `dl_class`; item mang **cả hai** lớp |
| Skeleton | xem mục 6 — cũng đi qua component, mang `wj-data-item`, nhưng **không phải record** |
| DataState · Pagination | **giữ nguyên tại chỗ** (LIMIT #3/#4 của D5d/D5e). Guard `page_count > 1` ở cả hai chỗ còn nguyên, ghim bằng test |
| `-u` | **đúng một lần**: `wujia_portal_layout,wujia_portal_return,wujia_sale,wujia_portal_delivery` — RC=0, **0 ERROR** ở cả `--logfile` lẫn file log thật `<thư-mục>/2026/09/*.log` (bẫy L15) |
| Version | layout `42.0.0 → 43.0.0` · return `2.12.0 → 2.13.0` · delivery `3.10.0 → 3.11.0` · `_components.css?v=1250 → 1260` (`_pc_components.css` giữ `1240`, không bị bump lây — bẫy D5d #4). `wujia_sale` chỉ đi kèm `-u` vì phụ thuộc, **không sửa ⇒ không bump** |

Môi trường: DB copy **`wujia_tea_d5b`**, cổng **8077**, `--db-filter '^wujia_tea_d5b$'`; không đụng
`wujia_tea_19`/8019 (PID 831381). Dừng server theo **PID** (bẫy D5c #1). Trước khi đo:
`latest_version` ↔ `__manifest__.py` **21/21 khớp**, và mốc "trước" so **từng ô** với
`docs/d5e-after.json` ra **0 ô lệch** — môi trường nhất quán tuyệt đối, không phải chỉ "giống mấy con
số tổng".

## 2. Số đo trước–sau — 2 call site (khổ 991 · 390 · 360; ≥992 hai khối này không render)

| Call site | Cao item (BA 96–120) | Gap (BA 8) | Radius (BA 12) | Padding (BA `12px 14px`) |
|---|---|---|---|---|
| `/portal/return` (`mreturn`, 20 bản ghi) | 122,3 → **118,3** ✅ | 12 → **8** ✅ | 14 → **12** ✅ | `14px` → **`12px 14px`** ✅ |
| `/portal/delivery` (`mdelivery`, 14 bản ghi) | 128,98 → **128,98** ❌ | 12 → **8** ✅ | 14 → **12** ✅ | `12px 16px` → **`12px 14px`** ✅ |
| skeleton delivery (`?_preview=loading`) | 94 → **96** (sàn min-height) | — → **8** | 14 → **12** | `12px 16px` → **`12px 14px`** |

Ba khổ cho số **y hệt nhau** ở cả hai màn (nội dung không xuống dòng thêm ở 360).

- **mreturn về đúng dải BA.** 122,3 vượt trần 120 là do đệm dọc `14px`; đưa về `12px` cắt đúng 4px
  ⇒ **118,3**. Không bỏ một field nào.
- **mdelivery vẫn 128,98 — vượt trần 120, và số này CHƯA TỪNG CÓ.** Kiểm kê D5a đo delivery lúc
  cửa hàng chỉ có **1 chuyến** nên hàng này không nằm trong bảng §3.2; nó chỉ lộ ra sau khi seed đủ
  14 chuyến. Đệm dọc vốn đã là `12px` nên đổi padding **không hạ được một pixel nào**; ép về 120 là
  phải bỏ bớt thông tin (nhãn "Chuyến xe" + mã, badge, 2 ô meta có icon). **Không tự ép** — báo BA,
  cùng loại LIMIT #2 của D5c và câu 4(a) của D5e.
- **`min-height: 96` không chạm hàng thật nào** (cả hai đều cao hơn); nó chỉ nâng **skeleton** 94 → 96,
  tức kéo placeholder **gần** hàng thật hơn chứ không xa ra.
- Hẹp đệm ngang `16px → 14px` ở delivery **không** làm chữ xuống dòng: chiều cao không đổi một pixel.
  Đây là chiều ngược của bài học D5e #5 — cùng một cơ chế, khác kết quả, và chỉ số đo mới phân biệt được.

## 3. Chiều cao trang — lượt đầu tiên của cụm D5 làm trang NGẮN LẠI

| Route | 1440 | 1024 | 992 | 991 | 390 | 360 |
|---|---|---|---|---|---|---|
| `/portal/return` | 0 | 0 | 0 | 3316 → **3160** (−156) | ↑ (−156) | ↑ (−156) |
| `/portal/delivery` | 0 | 0 | 0 | 2502 → **2450** (−52) | ↑ (−52) | ↑ (−52) |
| 8 route còn lại | 0 | 0 | 0 | 0 | 0 | 0 |

Con số khớp số học đến từng pixel, nên không phải ngẫu nhiên:
`return = 20 × (122,3 − 118,3) + 19 × (12 − 8) = 80 + 76 = 156`;
`delivery = 13 × (12 − 8) = 52` (chiều cao hàng không đổi).
Ngược chiều D5e (Home +145/+245) vì hai họ này **vốn đã** là card có đệm; lượt này chỉ **thu** đệm và
gap, không dựng thêm card-trong-card.

## 4. Acceptance #9 — số record đọc được không cần cuộn

| Route | 991 | 390 | 360 |
|---|---|---|---|
| `/portal/return` | 4 → 4 ✅ | 4 → 4 ✅ | 4 → 4 ✅ |
| `/portal/delivery` | 4 → 4 ✅ | 4 → 4 ✅ | 4 → 4 ✅ |
| 8 route còn lại | y hệt ✅ | y hệt ✅ | y hệt ✅ |

**Không thủng ô nào** — lượt đầu tiên của cụm D5 đạt điều đó (D5d thủng ở knowledge 12 → 9, D5e thủng
ở Home @360 2 → 1). Hàng thấp đi mà số dòng không tăng là vì phần cắt được (4px + gap 4px) chưa đủ
nhét thêm một hàng 118px.

## 5. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | D5c/D5d/D5e công bố | D5f sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm | 0 · 0 · 0 | **0 · 0 · 0** |

Phép so là số **D5c/D5d/D5e công bố**, không phải `docs/d5-baseline.json`.
`/portal/reports/orders` vẫn 500 — lỗi có sẵn của cụm **R3** (PostgreSQL Ubuntu không biết bí danh
`Asia/Saigon`), không thuộc D5.

## 6. Ngã ba skeleton — quyết định và lý do

`portal_delivery.xml` (khối `view_state == 'loading'`) có 3 hàng `t-foreach="[1,2,3]"` mang
`.wujia-mdelivery-row` nhưng **không phải bản ghi**. Khoá legacy bằng `:not(.wj-data-item)` sẽ để
skeleton giữ dáng **cũ** (radius 14 · `12px 16px` · gap 12) trong khi hàng thật sang dáng **mới**
⇒ nhảy hình ngay lúc đổ dữ liệu — đúng thứ skeleton sinh ra để tránh.

**Chọn: skeleton mang luôn `wj-data-item` và đi qua component.** Nó là placeholder của **chính hàng
đó**; đây cũng là bất biến mà D5c đã ghim cho skeleton PC (`test_skeleton_delivery_khop_row_that`).
Đo sau khi sửa (`?_preview=loading`, khổ 390): `padding 12px 14px · radius 12 · gap 8 ·
trongDataList = true` — **khớp hàng thật từng thuộc tính**.

Hệ quả phải nói rõ: **3 lần `t-call` component, nhưng chỉ 2 call site RECORD.** Kiểm kê vẫn
**21/31**. Hai test giữ ranh giới đó và **không giẫm chân nhau**: `test_item_mang_ca_hai_lop` chỉ xét
call site record, `test_skeleton_cung_dang_nhung_khong_phai_record` chỉ xét skeleton (nhận diện bằng
token `.wujia-mdelivery-skel`).

## 7. Tương tác — hover đo lại, không suy

Không thêm rule `:hover` nào cho variant detail-card ⇒ rule duy nhất còn chi phối là `:is(…):hover`
của `_interaction.css` (đã liệt kê **cả** `.wujia-mreturn-row` lẫn `.wujia-mdelivery-row`) và
`a.wujia-mdelivery-row:hover{color:inherit}`. Cả hai **không đụng tới** trong lượt này. Vẫn đo thật
bằng `getComputedStyle` sau `mouse.move` tới tâm, có `scroll_into_view_if_needed()` trước (bẫy D5e #4):

| Đối tượng (991) | Nghỉ | Hover |
|---|---|---|
| `mreturn` đã migrate | `#FFF` · viền `#E5E7EB` 1px · radius 12 · không shadow | `#EAF7FD` · viền `#28A9DF` · shadow `rgba(17,24,39,.08) 0 4px 12px` |
| `mdelivery` đã migrate | ↑ | ↑ |
| `mhist` (mốc đối chứng, đã migrate ở D5e) | ↑ | ↑ |

Ba dòng **trùng nhau từng giá trị**, và trùng đúng chữ ký hover mà D5e công bố ⇒ **tương tác không
đổi**. Mốc đối chứng lần này phải là **họ khác đã migrate** chứ không phải "hàng cùng họ chưa
migrate" như D5e: sau lượt này **không còn** `.wujia-mreturn-row`/`.wujia-mdelivery-row` nào chưa
migrate được render (skeleton cũng đã mang `wj-data-item`).

## 8. Bẫy / phát hiện trong phiên

1. 🟠 **Tiền đề "phải bỏ gap ở container, không thì thành 20" là SAI — bằng chứng nằm sẵn trong
   D5e.** `.wujia-mknow-list { gap: 10px }` (`_components.css:2488`) **vẫn còn nguyên** sau D5e mà
   gap đo được ra đúng 8. Lý do: sau khi migrate, item nằm trong `.wj-data-viewport`, không còn là
   con trực tiếp của container mang lớp cũ, nên `gap` của container không cộng vào nữa. Giữ nguyên
   cả hai rule container (gap 12), đo lại: `gap 12×9 → 12×3`, `8×27 → 8×33` — **đúng 6 ô đổi, đúng 2
   danh sách × 3 khổ**. Sửa theo phỏng đoán ở đây là xoá một rule vô hại và mất dấu vết.
2. 🔴 **Bộ chạy mutation đọc nhầm file log ⇒ báo "0 test đỏ" cho CẢ 10 phép.** Bẫy L15 lần thứ hai
   trong cụm: `wujia_core` dời log sang `<thư-mục>/<năm>/<tháng>/<ngày>.log`, còn harness đọc file
   `--logfile`. Trông y hệt "guard rỗng toàn tập". Cái tố giác là chính con số `failed=?` — không
   phân giải được nghĩa là **không đọc trúng bản ghi nào**, chứ không phải "không có lỗi". Harness
   phải phân biệt "đọc được và thấy 0" với "không đọc được".
3. 🟠 **Một mutation làm đỏ HAI test là lỗi thiết kế test, không phải bằng chứng tốt hơn.** Gỡ
   `wj-data-item` khỏi skeleton đỏ cả `test_item_mang_ca_hai_lop` lẫn test skeleton, vì test thứ
   nhất duyệt **mọi** call site detail-card. Đã thu hẹp nó về đúng call site record ⇒ trách nhiệm rời
   nhau, và lần chạy lại ra 1-1.
4. 🟠 **Con số "trần 120" của prompt chỉ nói về mreturn; thủ phạm thật lại là mdelivery.** mreturn
   sửa được bằng đệm (122,3 → 118,3), còn mdelivery 128,98 thì không — và nó **không có trong bảng
   kiểm kê D5a** vì lúc đó chỉ có 1 chuyến. Danh sách "chỗ cần lo" dựng từ kiểm kê cũ sẽ thiếu đúng
   chỗ khó nhất; phải đo lại sau khi seed.

## 9. Guard — chứng minh bằng mutation

**45 test** (`--test-tags wujia_data_list_d5`), **0 failed / 0 error** (37 của D5b/c/d/e + **8 mới**).
Mỗi phép thay neo vào **cả selector/ngữ cảnh**; hoàn tác bằng **ảnh chụp byte lấy ngay trước khi
thay** + đối chiếu `sha256` (bẫy D5c #2), **không** `git checkout` (bẫy D5b #2).
**10/10 phép làm đỏ đúng một test và 10/10 file khớp `sha256` sau khi hoàn tác.**

| Mutation | Test đỏ |
|---|---|
| Gỡ `dl_variant='detail-card'` ở call site return | `test_hai_call_site_record` |
| Gỡ lớp `wj-data-item` ở item delivery | `test_item_mang_ca_hai_lop` |
| `min-height: 96px` → `64px` | `test_so_ba_cua_detail_card` |
| `margin-top: 8px` → `12px` | `test_so_ba_cua_detail_card` |
| Gỡ `:not(.wj-data-item)` ở rule cũ mreturn | `test_mot_chu_so_huu_dang_hai_ho` |
| Gỡ `:not(.wj-data-item)` ở rule cũ mdelivery | `test_mot_chu_so_huu_dang_hai_ho` |
| Thêm `padding` vào rule **layout** mreturn (giành lại dáng) | `test_layout_hai_ho_nam_trong_media` |
| Gỡ `wj-data-item` khỏi skeleton delivery | `test_skeleton_cung_dang_nhung_khong_phai_record` |
| Hạ guard pager return xuống "có record" | `test_pager_hai_cho_giu_guard_page_count` |
| Sửa token chung `--wujia-morder-radius` 14 → 12 | `test_radius_khong_dung_token_chung` |

Hai guard chống **tự chứng minh rỗng**: `test_mot_chu_so_huu_dang_hai_ho` bóc `:not(...)` trước khi
xét (bẫy D5e #2) và `assertGreaterEqual(kiem, 1)`; `test_layout_hai_ho_nam_trong_media` khẳng định
`_rule()` (chỉ đọc tầng gốc) trả **None** rồi mới đọc bằng `_rule_in_media` — nếu ngày nào đó rule
bị đẩy ra ngoài `@media`, test đỏ chứ không im lặng đọc trúng.

## 10. LIMIT

1. **`mdelivery` 128,98 vượt trần detail-card 120** và đệm dọc đã ở mức thấp nhất BA cho ⇒ chỉ còn
   cách bỏ field. **Không tự ép** — đã bổ vào `docs/ba-questions-d5-datalist.md` mục 5.
2. **Bộ số detail-card là số BA viết thẳng**, nhưng cả cụm D5 vẫn **provisional** cho tới khi BA trả
   lời 4 câu treo (`UI-DATALIST-001` chưa có dòng History nào từ 25/08).
3. **DataState chưa gom**: 2/2 call site giữ nhánh empty cũ tại chỗ (nằm ngoài thẻ chứa danh sách và
   mang điều kiện riêng — return phân biệt "chưa có yêu cầu" với "lọc không ra"). Việc của `CMP-ES-001`.
4. **Pagination**: 2 pager vẫn ngoài DataList (LIMIT #4 của D5e) — dồn về lượt dọn trước khi khép D5.
5. Đo trên **DB copy `wujia_tea_d5b`**, chưa soi UAT — deploy dồn một lượt cuối cụm D5
   (hàng đợi: D5b + D5c + D5d + D5e + **D5f**).
6. Số đo đã commit: `docs/d5f-{before,after,rule-after,hover}.json`.

**Tiến độ cụm: 21/31 call site.** Kế tiếp: **D5g** — Công nợ PC ×2 + mobile ×2 (`wujia_portal_debt`).
