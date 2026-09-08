# D5g — bảng nghiệm thu DataList lượt 6 (Công nợ: PC ×2 + mobile ×2)

**Ngày:** 2026-09-08 · **Cơ sở:** `f11dba6` · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 4 call site record của `wujia_portal_debt` — bảng PC hoá đơn, bảng PC thanh toán,
danh sách mobile hoá đơn (`wj-debt-inv`), danh sách mobile thanh toán (`wj-debt-pay`).

Lượt **duy nhất của cụm D5 phải SỬA guard pager** (`page_count > 1`) — hai chỗ D5f đụng vốn đã đúng.
Cũng là lượt duy nhất bị **chặn bởi dữ liệu**: trước khi seed, hai call site thanh toán là empty
state và mọi guard sẽ tự chứng minh rỗng.

---

## 0. Bốn việc kiểm chứng TRƯỚC khi code

1. **BA vẫn CHƯA trả lời `docs/ba-questions-d5-datalist.md`.** Đọc thẳng tab `5. Issue List`, dòng
   tuyệt đối **119** qua `sheet_io.read_values`: `Ready for Dev` · `Ngày cập nhật 25/08/2026` ·
   cột `Ghi chú` **rỗng**. ⇒ giữ bộ số hiện tại, **ghi provisional**, **KHÔNG** sửa gộp D5d+D5e+D5f.
2. **Môi trường đã lệch mà không có dấu hiệu trên màn hình.** `HEAD` đi tiếp **2 commit** sau D5f
   (merge nhánh `thai`, tách `wujia_franchise_inspection`): DB `wujia_tea_d5b` thiếu 1 module và
   lệch 2 phiên bản. Đồng bộ bằng đúng lệnh của `docs/review-merge-thai-2026-09-08.md` §6
   (`-i wujia_franchise_inspection -u wujia_franchise,wujia_portal_inspection`, một lượt) trên
   **bản sao `wujia_tea_d5g`** — giữ `wujia_tea_d5b` nguyên làm mốc D5f. Sau đó **24/24 module khớp
   `__manifest__.py`**, và mốc "trước" so **từng ô** với `docs/d5f-after.json`: **2027/2027 ô, 0 lệch**.
3. **Bootstrap CSV của `wujia_franchise` không kích lại khi `-u`** — `<function>` nằm trong
   `<data noupdate="1">`. Kiểm bằng số đếm trước/sau: `3 franchise · 2 area · 10 member · 15 move`
   **không đổi một bản ghi**. Nếu nó chạy thì DB đo đã có 1.355 cửa hàng lạ.
4. **Một tiền đề của prompt SAI** — xem mục 8 #1: bảng PC thanh toán **có** render ở
   `/portal/debt/payment-history`, và mobile hoá đơn chỉ ra 2 dòng nếu thiếu `?all=1`.

## 1. Đã làm

| | |
|---|---|
| Seed | `scripts/seed_d5_datalist_demo.py` mục **[6]**: **11 hoá đơn** dồn vào đúng tuần `_default_week` trả về (`2026-W32`, 03→09/08) ⇒ bảng PC có **2 trang**; **11 payment** ngày trong tháng hiện tại ⇒ lịch sử cũng 2 trang. `franchise_id` của payment **do compute sinh ra từ đối soát thật** (wizard `account.payment.register`), **không ghi tay** — xem mục 6 |
| Call site PC ×2 | bọc `t-call="wujia_portal_layout.wj_data_list"`, `dl_class='wj-debt-pc-tablewrap'`, `dl_table_class='wj-pc-table wj-debt-pc-table'`, pager qua `dl_pager`; **14/14 `th` thêm `scope="col"`** |
| Guard pager | nút trang neo `pc_pager['page_count'] &gt; 1` ở **cả hai** bảng. Ở bảng thanh toán guard **tách đôi** (đúng cách D5c): dòng *Tổng thanh toán trong thời gian lọc* là **thông tin của kỳ lọc**, không phải điều hướng ⇒ giữ khi 1 trang; dòng đếm "Hiển thị 1–N / tổng" và dãy nút đi cùng pager |
| Call site mobile ×2 | `wj-debt-inv` → variant **`compact-row`**, `wj-debt-pay` → variant **`detail-card`**; item mang **cả hai** lớp; container cũ đi qua `dl_class` |
| CSS — layout theo họ | mỗi họ **một** rule trong `portal_debt.css`, giữ `display:grid` + `grid-template-columns` + `row/column-gap`; **bỏ `height` cứng** (62 / 96). Không khai lại padding/nền/viền/radius — ghim bằng test |
| CSS — khoá rule cũ | `.wj-debt-inv:not(.wj-data-item)` · `.wj-debt-pay:not(.wj-data-item)`. **Cố ý KHÔNG khoá** các con BEM `__name/__badge/__meta/__amount/__ref/__trace` và `--overdue/--paid` (chỉ khai `color`) — biến thể ô, đúng tiền lệ `wj-pc-td--*` (D5c) và 19 rule con (D5f) |
| Token | `--wj-debt-radius` (alias `--wujia-card-radius`) **giữ nguyên**; radius 12 đến từ tầng `.wj-data-item` của variant. Ghim bằng test |
| Container | `.wj-debt-invoices { gap: 6 }` / `.wj-debt-payments { gap: 12 }` **giữ nguyên** — sau migrate item nằm trong `.wj-data-viewport` nên gap container không cộng vào nữa (bài học D5f #1, đo lại: gap ra đúng **8**) |
| `-u` | **đúng một lần**: `wujia_portal_layout,wujia_portal_debt` — RC=0, **0 ERROR / 0 CRITICAL** đọc từ file log **THẬT** `logs/2026/09/2026-09-08.log` theo byte offset (bẫy L15) |
| Version | debt `19.0.4.4.1 → 19.0.4.5.0` · layout `19.0.43.0.0 → 19.0.44.0.0` · `_components.css?v=1260 → 1270` (`_pc_components.css` giữ **1240**, `components.css` giữ **1010** — không bump lây, bẫy D5d #4) |

## 2. Số đo trước–sau — 2 bảng PC (khổ 1440 · 1024 · 992; <992 hai bảng này không render)

| Bảng | `th[scope]` (BA 100%) | Header (BA 44) | Row (BA ≥52) | Cell padding (BA `10px 16px`) |
|---|---|---|---|---|
| `/portal/debt` hoá đơn (8 cột, 10 dòng/trang) | 0/8 → **8/8** ✅ | 50 → **44** ✅ | **58 cứng** → **54–55** ✅ | `0px 22px` → **`10px 16px`** ✅ |
| `/portal/debt/payment-history` (6 cột, 10 dòng/trang) | 0/6 → **6/6** ✅ | 50 → **44** ✅ | **58 cứng** → **52** (54–55 @992) ✅ | `0px 22px` → **`10px 16px`** ✅ |

Đúng họ `wj-pc-table` mà D5c đã chữa, và **đúng cơ chế D5c #5**: `0 22px` nghĩa là đệm dọc bằng **0**,
nên 58 là số **cứng** do `height`; padding 10/16 làm hàng co về 52–55. Hàng "nở" ở đây không xảy ra vì
không hàng nào xuống hai dòng — khác notification của D5c.

## 3. Số đo trước–sau — 2 danh sách mobile (khổ 991 · 390 · 360)

| Danh sách | Cao item | Dải BA | Gap (BA 8) | Radius (BA 12) | Padding (BA `12px 14px`) |
|---|---|---|---|---|---|
| `wj-debt-inv` (`/portal/debt?all=1`, 11 bản ghi) | **62 cứng** → **75,5** ✅ | compact-row **64–76** | 6 → **8** ✅ | 16 → **12** ✅ | `0 16px 0 14px` → **`12px 14px`** ✅ |
| `wj-debt-pay` (`/portal/debt/payment-history`, 11 bản ghi) | **96 cứng** → **104** (@991/390) · **116** (@360) ✅ | detail-card **96–120** | 12 → **8** ✅ | 16 → **12** ✅ | `0 16px 0 14px` → **`12px 14px`** ✅ |

**Cả hai vào đúng dải BA — lượt này không có LIMIT chiều cao** (khác D5e câu 4a và D5f câu 5).
`wj-debt-inv` lên 75,5 tức **sát trần 76**: đệm dọc từ 0 thành 12+12 = +24, bù lại `height: 62` cứng
bị gỡ nên nội dung tự co còn 51,5. Chỉ **0,5px** nữa là thủng — ghi ra đây vì bất kỳ field thêm vào
hàng hoá đơn sau này cũng sẽ đẩy nó vượt dải.

`wj-debt-pay` **116 ở khổ 360** (104 ở 991/390): dòng *Tham chiếu: …* xuống dòng khi bề rộng hụt —
đúng cơ chế D5e #5, và là nguyên nhân trực tiếp của ô acceptance #9 thủng ở mục 5.

## 4. Chiều cao trang

| Route | 1440 | 1024 | 992 | 991 | 390 | 360 |
|---|---|---|---|---|---|---|
| `/portal/debt` | 1314 → **1277** (−37) | 1468 → **1431** (−37) | ↑ (−37) | 900 → **921** | 916 → **945** (+29) | ↑ (+29) |
| `/portal/debt?all=1` | ↑ (−37) | ↑ (−37) | ↑ (−37) | 1504 → **1673** (+169) | ↑ (+169) | ↑ (+169) |
| `/portal/debt/payment-history` | 1228 → **1162** (−66) | 1240 → **1174** (−66) | 1240 → **1203** (−37) | 1721 → **1769** (+48) | ↑ (+48) | 1721 → **1901** (+180) |
| **9 route còn lại** | 0 | 0 | 0 | 0 | 0 | 0 |

Mọi con số khớp số học đến từng pixel, nên không phải ngẫu nhiên:

- PC hoá đơn `= 6 (header 50→44) + 31 (9 hàng ×55 + 1 ×54 thay vì 10 ×58) = 37`;
- PC thanh toán `= 6 + 10 × (58 − 52) = 66`;
- mobile hoá đơn @390 `= 2 × (75,5 − 62) + 1 × (8 − 6) = 29`; `?all=1` `= 11 × 13,5 + 10 × 2 = 168,5 ≈ 169`;
- mobile thanh toán `= 11 × (104 − 96) + 10 × (8 − 12) = 48`, và @360 `= 11 × 20 − 40 = 180`.

⚠️ Ô `991` của `/portal/debt` (900 → 921) **không so được**: 900 là **sàn** `min-height` của trang,
không phải chiều cao thật. Đọc nhầm ô này thành "+21" là suy ra một kết luận không tồn tại.

**PC ngắn lại, mobile dài ra** — hai chiều ngược nhau trong cùng một lượt, vì PC vốn bị `height` nén
còn mobile vốn có đệm dọc bằng 0.

## 5. Acceptance #9 — số record đọc được không cần cuộn

| Đối tượng | 1440 | 1024 | 992 | 991 | 390 | 360 |
|---|---|---|---|---|---|---|
| `/portal/debt` bảng PC | 5 → 5 ✅ | 2 → 2 ✅ | 2 → 2 ✅ | — | — | — |
| `/portal/debt` mobile (`?all=1`) | — | — | — | 4 → 4 ✅ | 4 → 4 ✅ | 4 → 4 ✅ |
| `/portal/debt/payment-history` bảng PC | 7 → 7 ✅ | 6 → **7** ↑ | 6 → **7** ↑ | — | — | — |
| `/portal/debt/payment-history` mobile | — | — | — | 5 → 5 ✅ | 5 → 5 ✅ | **5 → 4** ⚠️ |
| 9 route còn lại | y hệt ✅ | y hệt ✅ | y hệt ✅ | y hệt ✅ | y hệt ✅ | y hệt ✅ |

**Thủng đúng MỘT ô**: lịch sử thanh toán mobile ở khổ **360**, `5 → 4`. Nguyên nhân đo được là hàng
lên **116** (dòng *Tham chiếu* xuống dòng), không phải gap. **Không tự vá, không đổi số BA** — báo ở
mục 10 và bổ vào văn bản hỏi BA. Hai ô **tăng** ở bảng PC thanh toán là phần thưởng của row 58 → 52.

> ⚠️ **Bộ so đầu tiên mù đúng ở chỗ cần nhất.** Ghép ô theo *tên lớp* thì mọi call site đã migrate
> đổi khoá (`wj-debt-invoices` → `wj-data-viewport`) nên bị **bỏ qua im lặng**: bảng in ra "0 ô thủng"
> trong khi thật ra có 1. Phải ghép theo **vị trí call site**. Đây là bẫy D5d #2 ở tầng khác — bộ đo
> tự khai "sạch" vì không nhìn thấy gì.

## 6. Ngã ba seed payment — quyết định và lý do

`account.payment.franchise_id` là **stored compute** `@api.depends('reconciled_invoice_ids.franchise_id')`
(`wujia_account/models/account_payment.py:19`) với `readonly=False`, nên ghi tay **chạy được** —
`scripts/seed_debt_demo.py:84` (Sprint 48) làm đúng như vậy.

**Chọn: đối soát THẬT qua `account.payment.register`, không ghi tay.** Hai lý do đo được:

1. Compute sẽ **giành lại quyền** ngay khi `reconciled_invoice_ids` đổi (`pay.franchise_id = franchises
   if len(franchises) == 1 else pay.franchise_id`) — dữ liệu ghi tay là dữ liệu **không tái lập được**.
2. Nó là phép thử của chính seam Sprint 48: log seed in ra `franchise_id=1` cho **11/11** payment mà
   không dòng nào set field đó ⇒ chứng minh compute chạy, chứ không chỉ chứng minh bảng có dòng.

**Đối soát vào hoá đơn CŨ (tháng 6–7), ngoài cửa sổ 6 tuần của bộ lọc**, để `_default_week` không đổi
tuần mở sẵn — nếu trả hết nợ tuần `2026-W32` thì màn đo nhảy sang tuần khác và bảng "trước" vô nghĩa.

## 7. Tương tác — hover đo lại, và lần này KHÁC kết luận hai lượt trước

`_interaction.css` liệt kê `.wj-debt-actionrow`, `.wj-debt-pc-tab:not(.is-active)`,
`.wj-debt-pc-pagebtn:not(.is-active)` trong danh sách `:is()` — nhưng **không** có `.wj-debt-inv` /
`.wj-debt-pay`. Kết luận "hover không đổi" của D5e/D5f **không tự động đúng ở đây**. Đo thật bằng
`getComputedStyle` sau `mouse.move` tới tâm, có `scroll_into_view_if_needed()` trước (bẫy D5e #4):

| Đối tượng (991) | Nghỉ | Hover |
|---|---|---|
| `wj-debt-inv` (compact-row) | `#FFF` · viền `#E5E7EB` · radius 12 | **`rgba(40,169,223,.04)` · viền `#28A9DF`** — hover MỚI CÓ |
| `wj-debt-pay` (detail-card) | ↑ | **KHÔNG ĐỔI** |
| `mhist` (mốc đối chứng D5e) | ↑ | `#EAF7FD` · viền `#28A9DF` · shadow `rgba(17,24,39,.08) 0 4px 12px` |
| `mreturn` (mốc đối chứng D5f) | ↑ | ↑ |

Ba kết quả **khác nhau**, và mỗi cái có lý do đọc được từ CSS:

- `wj-debt-pay` không đổi vì variant `detail-card` **không có** rule `:hover` (D5f cố ý không thêm).
- `mhist`/`mreturn` ăn chữ ký của `_interaction.css` vì `:is(…)` là **(0,4,0)**, thắng rule variant.
- `wj-debt-inv` **nay có hover** do rule `.wj-data-list--compact-row .wj-data-item:hover` (D5d) —
  nó không nằm trong danh sách `:is()` nên không bị đè.

🟠 **Đây là thay đổi hành vi, và cần BA chốt:** `wj-debt-inv` là một `<div>` **không bấm được**
(khác `mhist`/`mreturn` vốn là `<a>`), nên nền đổi khi rê chuột là **gợi ý sai về khả năng bấm**.
Dev **không tự quyết** — đã bổ **câu 6** vào `docs/ba-questions-d5-datalist.md`, và hiện trạng được
ghim bằng số đo trong `docs/d5g-hover.json` để lùi lại chỉ là một rule.

## 8. Bẫy / phát hiện trong phiên

1. 🟠 **Hai tiền đề của prompt sai, và chỉ đo mới biết.** (a) "Bảng PC thanh toán không render ở
   `/portal/debt`" — đúng, nhưng nó render bình thường ở route riêng `/portal/debt/payment-history`,
   không cần tham số đặc biệt nào. (b) `?all=1` là **bắt buộc** để đo mobile hoá đơn: không có nó
   controller cắt còn `INVOICE_PREVIEW = 2` dòng, harness vẫn nhận là "danh sách" (đủ 2 con) và in
   ra một bảng **trông hợp lệ mà chỉ đo 2/11 bản ghi**.
2. 🔴 **Phép so trước–sau ghép theo tên lớp là bộ đo tự chứng minh rỗng.** Mọi call site migrate xong
   đều đổi khoá container ⇒ toàn bộ ô acceptance #9 của chính 4 call site vừa sửa bị **bỏ qua**, bảng
   in "0 thủng". Ghép lại theo vị trí call site: lộ ra 1 ô thủng thật (mục 5).
3. 🔴 **Bộ đọc kết quả mutation báo "đỏ KHÔNG test nào" cho cả 7 phép — lần thứ ba cùng một họ bẫy.**
   Lần này không phải file log (đã vá theo D5f #2) mà là **regex**: Odoo in `FAIL: TestDataListDebt.
   test_x`, tên lớp đứng trước, nên `(?:FAIL|ERROR): (test_\w+)` không khớp. Dòng tổng kết
   `1 failed of 53` vẫn hiện ngay bên cạnh và tố giác mâu thuẫn. **Hai nguồn số độc lập trong cùng
   một báo cáo là thứ đã cứu phép đo này** — nếu chỉ in danh sách test đỏ thì kết luận sai đã lọt.
4. 🟠 **Một mutation làm đỏ ba test — sửa THIẾT KẾ TEST, không sửa mutation.** `test_moi_th_deu_co_scope`
   và `test_pager_…` ban đầu chọn call site bằng "không khai `dl_variant`", nên phép thay
   `dl_variant` của call site mobile biến nó thành "bảng thứ ba" và làm đỏ luôn hai test kia. Đổi
   phép chọn sang **cấu trúc** (`có thead` cho bảng, `có lớp item` cho mobile) ⇒ trách nhiệm rời nhau,
   chạy lại ra 8/8 một-một. Đúng bài học D5f #3, gặp lại ở dạng khác.
5. 🟠 **Môi trường lệch vì việc của người khác, không phải việc của mình.** Mốc đo D5f dựng trên
   `wujia_tea_d5b`, nhưng `main` đã nhận merge nhánh `thai` giữa hai lượt. Không so `latest_version`
   từng module thì mọi số "trước" của D5g là số của portal **trước khi tách module khảo sát** — và
   không có gì trên màn hình báo điều đó (bẫy D5a #4, gặp lại vì lý do hoàn toàn mới).

## 9. Guard — chứng minh bằng mutation

**53 test** (`--test-tags wujia_data_list_d5`), **0 failed / 0 error** (45 của D5b→D5f + **8 mới**).
Mỗi phép thay neo vào **cả selector/ngữ cảnh**; hoàn tác bằng **ảnh chụp byte lấy ngay trước khi thay**
+ đối chiếu `sha256` (bẫy D5c #2), **không** `git checkout` (bẫy D5b #2).
**8/8 phép làm đỏ đúng một test và 8/8 file khớp `sha256` sau khi hoàn tác.**

| Mutation | Test đỏ |
|---|---|
| `dl_variant` `'compact-row'` → `'table'` ở mobile hoá đơn | `test_bon_call_site` |
| Gỡ `scope="col"` của một `th` bảng thanh toán | `test_moi_th_deu_co_scope` |
| Gỡ lớp `wj-data-item` ở item `wj-debt-pay` | `test_item_mobile_mang_ca_hai_lop` |
| Hạ guard pager hoá đơn `page_count > 1` → `pc_invoices` | `test_pager_hai_bang_guard_page_count` |
| Gỡ `:not(.wj-data-item)` ở rule cũ `.wj-debt-inv` | `test_mot_chu_so_huu_dang_hai_ho` |
| Thêm `padding` vào rule **layout** `wj-debt-pay` (giành lại dáng) | `test_layout_khong_gianh_lai_dang` |
| Sửa token `--wj-debt-radius` thành `12px` cứng | `test_radius_khong_dung_token_chung` |
| Gắn `wj-data-item` vào ô tóm tắt `.wj-debt-summary__meta` | `test_summary_meta_khong_phai_danh_sach` |

Ba guard chống **tự chứng minh rỗng**: `test_mot_chu_so_huu_dang_hai_ho` bóc `:not(...)` trước khi xét
+ `assertGreaterEqual(kiem, 4)`; `test_pager_…` đếm số nút đã quét (`assertGreaterEqual(thay, 2)`);
`test_summary_meta_…` ghim một khối mà **bộ đo nhận nhầm là danh sách** (2 con, xếp dọc, cao 15px)
nhưng không phải danh sách record — cùng vai trò với 10 hàng mdash của D5e.

`test_layout_khong_gianh_lai_dang` đọc ở **tầng gốc** chứ không trong `@media` như D5e/D5f, và lý do
được ghi thẳng trong test: `portal_debt.css` **không có** `@media` cho mobile — khối mobile ẩn bằng
`d-lg-none` ở XML, nên phạm vi đến từ chính lớp variant.

## 10. LIMIT

1. **Acceptance #9 thủng 1 ô**: lịch sử thanh toán mobile @360, `5 → 4`, do hàng 96 → 116 (dòng
   *Tham chiếu* xuống dòng). Trong dải BA `96–120` nên **không phải lỗi số**, nhưng vẫn là record đọc
   được ít đi — **không tự vá**, đã bổ vào văn bản hỏi BA (câu 4 mở rộng).
2. **Hover mới xuất hiện trên `wj-debt-inv`** — một `<div>` không bấm được (mục 7). Chờ BA chốt.
3. **`wj-debt-inv` cao 75,5 / trần 76** — chỉ còn 0,5px dư địa; thêm bất kỳ field nào vào hàng hoá đơn
   là vượt dải.
4. **Bộ số cả cụm D5 vẫn `provisional`** cho tới khi BA trả lời (`UI-DATALIST-001` chưa có dòng
   History nào từ 25/08).
5. **DataState chưa gom**: 4/4 call site giữ nhánh empty cũ tại chỗ (`wj-debt-pc-emptybox` ×2 +
   `wj-empty-state--rich` ×2, đều nằm ngoài thẻ chứa danh sách và mang điều kiện riêng). Việc của
   `CMP-ES-001`.
6. **Pagination**: 2 pager PC nay đi qua `dl_pager` **trong** DataList — khác D5e/D5f (LIMIT #4 của cả
   hai lượt). Hai chỗ còn lại của cụm dồn về lượt dọn trước khi khép D5.
7. Đo trên **DB copy `wujia_tea_d5g`** (nhân từ `wujia_tea_d5b` + đồng bộ merge `thai`), chưa soi UAT
   — deploy dồn một lượt cuối cụm D5 (hàng đợi: D5b + D5c + D5d + D5e + D5f + **D5g**).
8. Số đo đã commit: `docs/d5g-{before,after,rule-after,hover}.json`.

## 11. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | D5c/D5d/D5e/D5f công bố | D5g sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm | 0 · 0 · 0 | **0 · 0 · 0** |

Phép so là số **D5c/D5d/D5e/D5f công bố**, không phải `docs/d5-baseline.json`.
`/portal/reports/orders` vẫn 500 — lỗi có sẵn của cụm **R3** (PostgreSQL Ubuntu không biết bí danh
`Asia/Saigon`), không thuộc D5.

**Hồi quy ngoài phạm vi:** so từng ô toàn bộ 9 route còn lại giữa `d5g-before.json` và
`d5g-after.json` — **1857/1857 ô, 0 lệch** (gồm 27 bảng D5b/D5c, 21 call site D5b–D5f, 10 hàng mdash,
mexam/khảo sát để dành D5h).

**Tiến độ cụm: 25/31 call site.** Kế tiếp: **D5h** — Thi ×4 + Khảo sát ×2 (`_exam`, `_inspection`).
