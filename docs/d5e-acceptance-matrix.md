# D5e — bảng nghiệm thu DataList lượt 4 (mobile compact-row)

**Ngày:** 2026-09-07 · **Cơ sở:** `80cf9d1` (D5d) · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 9 call site mobile thuộc **bốn** họ CSS khác nhau — `wujia-mdash-row` ×6
(5 khối `/portal` + `/portal/support`) · `wujia-mhist-row` · `wujia-mnoti-row` · `wujia-mknow-row`.

Lượt đầu tiên **một variant phủ nhiều họ**: D5b/c/d mỗi lượt một họ, ở đây bốn họ có bốn kiểu
layout khác nhau (mdash flex 3 vùng · mhist `space-between` · mnoti `stretch` + thanh accent 4px ·
mknow `flex-start`) phải cùng về một bộ dáng mà **không** cùng một layout.

---

## 0. Hai việc kiểm chứng TRƯỚC khi code

1. **BA chưa trả lời `docs/ba-questions-d5-datalist.md`.** Đọc thẳng tab `5. Issue List`, dòng
   tuyệt đối **119**: `Ready for Dev`, `Ngày cập nhật 25/08/2026`, cột `Kết quả mong muốn` nguyên
   văn cũ, không dòng History nào về 3 câu hỏi ⇒ giữ bộ số hiện tại, **vẫn ghi provisional**.
   Không có hai bộ số song song.
2. **Một tiền đề của prompt sai, kiểm bằng quét độ sâu ngoặc chứ không bằng thụt lề.**
   `.wujia-mdash-row` **KHÔNG** nằm trong `@media`: `@media (max-width: 991.98px)` mở ở
   `_components.css:2383` và **đóng ở 2609**, khối mdash bắt đầu ở 2611 — tầng gốc. Hai họ thật
   sự trong `@media` là **mknow** (`_components.css:2467`) và **mnoti**
   (`portal_notification.css:33`). Helper đọc-trong-`@media` vẫn cần, nhưng cho hai họ đó.

## 1. Đã làm

| | |
|---|---|
| **Tách rule D5d làm hai** (việc đầu tiên) | `.wj-data-list--compact-row .wj-data-item` nay **chỉ mang dáng** (min-height 64 · padding `12px 14px` · nền · viền · radius 12); phần layout (`display:grid` + 4 cột) đẩy về `.wj-data-list--compact-row .wujia-content-card-row.wj-data-item`. Đắp nguyên rule cũ lên hàng mobile là ép lưới 4 cột, vỡ cả 9 chỗ |
| Call site | 9/9 bọc `t-call="wujia_portal_layout.wj_data_list"` + `dl_variant='compact-row'`; item mang **cả hai** lớp; container cũ đi qua `dl_class` (`wujia-mhist-list`/`mnoti-list`/`mknow-list`), riêng 6 khối mdash thì DataList nằm **trong** `wj_surface_card` nên container cũ ở lại trên thẻ |
| CSS | 4 họ khoá bằng `:not(.wj-data-item)`; mỗi họ có **một** rule layout riêng cho item đã migrate. Rule con (`-main`, `-title`, `-tile`, `-side`, `-date`, `.is-stacked …`) và `::before` của `is-unread` **cố ý không khoá** — biến thể ô, đúng tiền lệ `wj-pc-td--*` (D5c) và `-bullet/-content` (D5d) |
| Ngoại lệ có chủ đích | **mnoti giữ `padding-left: 16px`** (thanh accent `is-unread::before` rộng 4px sát mép trái; về 14 là chữ đè lên nó) — vẫn nằm trong dải BA `12–14px` cho ba mép còn lại |
| DataState | 9/9 **giữ nguyên** nhánh empty cũ tại chỗ (xem LIMIT #3) |
| Pagination | 3 pager (`mhist`/`mnoti`/`mknow`) **giữ ngoài** DataList — LIMIT #3 của D5d, dồn về lượt dọn Pagination |
| `-u` | **đúng một lần**, 6 module, RC=0, **0 ERROR** ở cả `--logfile` lẫn file log thật `<thư-mục>/2026/09/2026-09-07.log` (bẫy L15) |
| Version | layout `41.0.0 → 42.0.0` · base `7.9.0 → 7.10.0` · purchase_history `3.8.0 → 3.9.0` · notification `2.10.0 → 2.11.0` · knowledge `3.11.0 → 3.12.0` · support `3.15.0 → 3.16.0` · `_components.css?v=1240 → 1250` (`_pc_components.css` **không** bị bump lây — bẫy D5d #4) |

Môi trường: DB copy **`wujia_tea_d5b`**, cổng **8077**, `--db-filter '^wujia_tea_d5b$'`; không đụng
`wujia_tea_19`/8019 (đang chạy PID 831381). Dừng server theo **PID** (bẫy D5c #1). Trước khi đo:
`latest_version` ↔ `__manifest__.py` **21/21 khớp**, và mốc "trước" ra **đúng** con số D5d để lại
(`th[scope]` 9/27 · header `44×18 · 50×9` · item mobile `64.5×4 · 201×3 · 92×3 · 64×3 · 111×3 ·
63×3 · 74.3×3 · 122.3×3` · gap `0×24 · 12×9 · 8×6 · 18×3 · 4×3 · 10×3 · 14×3`).

**Nghiệm thu bước tách rule, đo riêng trước khi đụng call site mobile:** chạy lại toàn bộ bộ đo →
**0/183 ô đổi**, 4 call site D5d vẫn `64 · gap 8 · radius 12 · 12px 14px`. Không hồi quy lượt trước.

## 2. Số đo trước–sau — 9 call site (khổ 991 · 390 · 360; ≥992 các khối này không render)

| Call site | Cao item | Gap | Radius | Padding |
|---|---|---|---|---|
| `/portal` Thông báo (mdash) | 64–84 → **66–104** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |
| `/portal` Chuyến sắp giao (mdash, stacked) | 134.5–188.5 → **136.5–231** | 0 → **8** | 0 → **12** | ↑ |
| `/portal` Đơn hàng (mdash, stacked) | 92 → **94** | 0 → **8** | 0 → **12** | ↑ |
| `/portal` Bài viết (mdash) | 64 → **66–84.5** | 0 → **8** | 0 → **12** | ↑ |
| `/portal` Đổi trả (mdash, stacked) | 111–130 → **113–149** | 0 → **8** | 0 → **12** | ↑ |
| `/portal/support` ticket (mdash) | 90–110.5 → **92–111.5** | 0 → **8** | 0 → **12** | ↑ |
| `/portal/purchase-history` (mhist) | 74.3 → **78.3** | 8 (giữ) | 12 (giữ) | `10px 14px` → **`12px 14px`** |
| `/portal/notification` (mnoti) | 99.89–129.28 → **y hệt** | 8 (giữ) | 12 (giữ) | **y hệt** `12px 14px 12px 16px` |
| `/portal/knowledge` (mknow) | 83.8–133.39 → **79.8–129.39** | 10 → **8** | 14 → **12** | `14px` → **`12px 14px`** |

**mnoti không đổi một pixel** — họ này vốn đã đúng chuẩn compact-row; lượt này chỉ đổi *ai sở hữu*
các con số đó, không đổi giá trị. mhist +4px vì `10px` → `12px` đệm dọc (cả hai đều nằm trong dải
BA `10–12px`); mknow **thấp đi** 4px và thu radius/gap về số BA.

**Ngoài phạm vi: 0 ô đổi.** 27 bảng của D5b/D5c y hệt (`th[scope]` 9/27 · `44×18 · 50×9` ·
`58×12 · 54×7 · 52×4 · 55×2 · 88×2` · `10px 16px ×18 · 0px 22px ×9`); **10 hàng `wujia-mdash-row`
KHÔNG phải danh sách** (lối tắt Home ×3, hàng thông tin tĩnh Home ×3 và support ×4) giữ nguyên
`64.5/63 · gap 0 · padding 12px 0 · radius 0`; `mreturn`/`mdelivery` (D5f), `mexam`/khảo sát (D5h),
debt — không ô nào đổi.

> ⚠️ Prompt phiên ghi "12 chỗ mdash không phải danh sách"; đếm lại trên mã nguồn ra **10**
> (home `609/616/623` + `644/651/658`, support `543/550/558/565`). Con số 10 nay được ghim bằng test.

## 3. Chiều cao trang — cái giá của card-trong-card trên Home mobile

| Route | 991 | 390 | 360 |
|---|---|---|---|
| `/portal` | 2761 → **2816** (+55) | 2883 → **3028** (+145) | 2996 → **3241** (+245) |
| `/portal/support` | 2372 → **2545** (+173) | 2664 → **2935** (+271) | 2762 → **2935** (+173) |
| `/portal/knowledge` | 1791 → **1727** (−64) | 1916 → **1852** (−64) | 2042 → **1978** (−64) |
| `/portal/notification` · 6 route mobile còn lại | y hệt | y hệt | y hệt |
| **Mọi khổ PC (1440/1024/992)** | **0** | **0** | **0** |

Nở **không phải** vì gap 8 (chỉ +8 × số khoảng) mà chủ yếu vì **đệm ngang 14px hai bên** làm bề
rộng nội dung hụt 30px ⇒ chữ xuống dòng thêm: khổ 360 khối *Chuyến sắp giao* 188.5 → 231. Đây là
hệ quả cơ học của quyết định "card-trong-card" (chủ dự án chốt trong phiên, theo tiền lệ D5d), đã
**đo và công bố**, không bù bằng cách cắt bớt bản ghi. Mốc C7 (Home 2752 → 2634 @360) là mốc của
lượt tối ưu khác; lượt này đi ngược chiều đó **+245** và số đó cần BA biết.

## 4. Acceptance #9 — số record đọc được không cần cuộn

| Route | 991 | 390 | 360 |
|---|---|---|---|
| `/portal` khối Thông báo | 2 → 2 ✅ | 2 → 2 ✅ | 2 → **1** ❌ |
| `/portal/purchase-history` · `/portal/notification` · `/portal/knowledge` · `/portal/support` | y hệt ✅ | y hệt ✅ | y hệt ✅ |

**Một ô thủng**: khổ 360, khối preview đầu của Home, 2 → 1 dòng. Nguyên nhân: hàng nở 84 → 104 vì
tiêu đề thông báo xuống dòng ở bề rộng hẹp hơn. Theo đúng cách D5d xử lý knowledge 12 → 9:
**không tự vá, không tự đổi số BA** — vào thẳng văn bản hỏi BA (mục 4).

## 5. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | D5c/D5d công bố | D5e sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm | 0 · 0 · 0 | **0 · 0 · 0** |

Phép so là hai con số D5c/D5d công bố, **không** phải `docs/d5-baseline.json`.
`/portal/reports/orders` vẫn 500 — lỗi có sẵn của cụm **R3** (PostgreSQL Ubuntu không biết bí danh
`Asia/Saigon`), không thuộc D5.

## 6. Tương tác — và một kết luận ngược với dự đoán

Dự đoán trước khi đo: rule mới `.wj-data-list--compact-row .wj-data-item:hover` (0,3,0) sẽ đè
`:is(…):hover` của `_interaction.css` ⇒ nền hover 4 họ mobile đổi từ `--wujia-primary-soft` sang
`rgba(40,169,223,0.04)`. **Đo ra ngược lại.**

| Đối tượng (991, `mouse.move` tới tâm sau `scroll_into_view`) | Nghỉ | Hover |
|---|---|---|
| mdash **đã** migrate | `#FFF` · viền `#E5E7EB` 1px · radius 12 | `#EAF7FD` · viền `#28A9DF` · shadow |
| mdash **chưa** migrate (10 hàng ngoài phạm vi, cùng trang) | trong suốt · 0px · radius 0 | `#EAF7FD` · viền `#28A9DF` · shadow |
| mhist · mnoti · mknow đã migrate | `#FFF` · viền · radius 12 | `#EAF7FD` · viền `#28A9DF` · shadow |
| `content-card-row` của D5d (1440) | `#FFF` · viền · radius 12 | `rgba(40,169,223,0.04)` · viền · **không** shadow |

Hàng chưa migrate là **mốc "trước" duy nhất còn đo được** sau khi XML đã đổi, và nó cho hover y
hệt hàng đã migrate ⇒ **tương tác 4 họ mobile không đổi**. Lý do: `:is()` mang độ đặc hiệu của
**tham số đặc hiệu nhất** — trong danh sách có `.wj-pc-page-btn:not(.is-active):not(.is-disabled)`
(0,3,0) ⇒ cả khối là (0,3,0), cộng `:hover` thành (0,4,0), thắng rule compact-row (0,3,0). Đúng
bài học `:not()` của D3, lần này ở chiều có lợi. Họ `content-card-row` không nằm trong danh sách
`:is()` nên giữ nền hover của D5d — hai chế độ hover cùng tồn tại, cố ý.

## 7. Guard — chứng minh bằng mutation

**37 test** (`--test-tags wujia_data_list_d5`), **0 failed / 0 error** (23 D5b/c + 6 D5d + **8 mới**).
Mỗi phép thay neo vào cả selector/ngữ cảnh; hoàn tác bằng **ảnh chụp byte lấy ngay trước khi thay**
+ đối chiếu `sha256` (bẫy D5c #2), **không** `git checkout` (bẫy D5b #2). **9/9 phép làm đỏ đúng
một test và 9/9 file khớp `sha256` sau khi hoàn tác.**

| Mutation | Test đỏ |
|---|---|
| Gỡ `dl_variant='compact-row'` ở call site support | `test_chin_call_site_mobile` |
| Gỡ lớp `wj-data-item` ở call site knowledge | `test_item_mang_ca_hai_lop` |
| Gỡ `is-stacked` ở khối Đơn hàng gần đây | `test_is_stacked_con_du_ba_cho` |
| Gắn `wj-data-item` vào **hàng thông tin tĩnh** support | `test_muoi_hang_mdash_khong_phai_danh_sach_giu_nguyen` |
| Gỡ `:not(.wj-data-item)` ở rule cũ `.wujia-mhist-row` | `test_mot_chu_so_huu_dang_bon_ho` |
| Trả `display:grid` về rule dáng dùng chung | `test_layout_tung_ho_tach_khoi_dang` |
| Đổi `align-items` của rule mknow **trong `@media`** | `test_layout_hai_ho_nam_trong_media` |
| Bỏ `padding-left: 16px` của mnoti | `test_layout_hai_ho_nam_trong_media` |
| Khoá `::before` của `is-unread` bằng `:not(.wj-data-item)` | `test_thanh_accent_chua_doc_van_song` |

Ba test cũ phải sửa vì **chính lượt này làm sai tiền đề của chúng**: `_compact_calls` và
`test_home_preview_khong_gan_pagination` từng nhận diện call site D5d bằng "variant compact-row" /
"không có `thead`" — nay mobile cũng vậy ⇒ đổi phép chọn sang container PC thật
(`ul[@class="wujia-content-card-body"]`); `test_mot_chu_so_huu_dang_compact_row` phải bỏ qua rule
layout **mới** của chính item đã migrate.

## 8. Bẫy đã trả giá trong phiên

1. 🔴 **`class="wujia-mdash-row[^"]*"` bắt luôn `wujia-mdash-row-main/-title/-sub`** ⇒ lượt chạy
   đầu gắn `wj-data-item` vào **31** phần tử thay vì 6. Cùng một dạng sai với `grep` thô của D4,
   `contains()` của D5c #3 và `sed` đuôi chuỗi của D5d #4 — **bốn lượt liên tiếp**. Phải neo ranh
   giới `(?![-\w])`. Hoàn tác bằng ảnh chụp byte, làm lại từ đầu.
2. 🔴 **`:not(.wj-data-item)` cũng chứa chuỗi `.wj-data-item`** ⇒ điều kiện "bỏ qua rule dáng mới"
   nuốt luôn mọi rule cũ, guard đếm được **0** rule và tự chứng minh rỗng. Chính assert
   `assertGreaterEqual(kiem, 1)` bắt được — guard phải tự kiểm "đã quét trúng cái gì chưa", không
   chỉ kiểm "không thấy vi phạm". Bóc `:not(...)` trước khi kiểm.
3. 🟠 **Không thể dựng lại mốc "trước" bằng cách thay riêng CSS**: bản CSS ở `HEAD` đã có
   `.wj-data-item` (D5d), mà XML thì đã migrate ⇒ hàng mobile ăn luôn dáng D5d và bảng đo "trước"
   ra y hệt "sau" — trông như bộ đo hỏng. Mốc "trước" đúng là **hàng cùng họ chưa migrate trên
   cùng trang**.
4. 🟠 **`mouse.move` tới phần tử nằm dưới màn không hover được**: hàng lối tắt Home ở y≈2000 đọc ra
   "không có hover" và trông như hồi quy. Phải `scroll_into_view_if_needed()` trước. Cùng họ bẫy
   D5d #5, khác nguyên nhân.

## 9. LIMIT

1. **Bộ số 64–76 vẫn provisional** cho phần PC (D5d); phần mobile là số BA viết thẳng, nhưng
   **mnoti 99.9–129.3 và mknow 79.8–129.4 vượt trần 76** vì nội dung tự xuống dòng — đã bổ thành
   **mục 4** của `docs/ba-questions-d5-datalist.md`, **không tự ép trần** (ép là cắt dữ liệu
   nghiệp vụ, cùng loại LIMIT #2 của D5c).
2. **Acceptance #9 thủng một ô** (`/portal` @360, khối Thông báo, 2 → 1) + Home mobile nở
   **+145/+245** và support **+271** — cả ba nằm trong mục 4 văn bản hỏi BA.
3. **DataState chưa gom**: 9/9 call site giữ nhánh empty cũ tại chỗ vì nó nằm **ngoài** thẻ chứa
   danh sách (6 khối mdash) hoặc mang thêm điều kiện riêng (`filter_error` của mhist). Việc của
   `CMP-ES-001`.
4. **Pagination**: 3 pager mobile vẫn ngoài DataList (LIMIT #3 của D5d) ⇒ portal hiện có hai kiểu.
   Dồn về một lượt dọn trước khi khép D5.
5. Đo trên **DB copy `wujia_tea_d5b`**, chưa soi UAT — deploy dồn một lượt cuối cụm D5
   (hàng đợi: D5b + D5c + D5d + D5e).
6. Số đo đã commit: `docs/d5e-{before,after,rule-after,hover}.json`.

**Tiến độ cụm: 19/31 call site.** Kế tiếp: **D5f** — mobile detail-card (`mreturn` · `mdelivery`).
