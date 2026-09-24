# E4c — Nghiệm thu wiring bộ lọc + đóng `UI-FILTER-001` (STT 139, dòng 132 tab `5. Issue List`)

Lượt **E4c** khép cụm FilterBar `CMP-FB-001`: E4a dựng component, E4b1 phủ 9 thanh PC, E4b2 phủ 6
thanh mobile — ba lượt đó lo **dáng**. Lượt này lo **hành vi lọc** rồi đưa issue về `Ready for Retest`
(Dev **không** đặt `Done`).

- Cây mã trước lượt: `c3c7385` · đo ngày 19/09/2026 · đo bằng `em.hcm`.
- DB đo **`wujia_e4b1`** (clone `wujia_tea_19`, **có** 2 module Khảo sát như UAT + `data/filestore/`),
  cổng **8090/8091**; test **8098/8099**; đối chứng `wujia_e4cbase` @ `c3c7385` cổng **8096/8097**.
  Không đụng `wujia_tea_19` / cổng 8019.
- Dữ liệu đo: DB đo vốn **0 phiếu thi, 0 chuyến giao** nên mục "ngày hợp lệ lọc đúng" không chứng minh
  được — đã gieo `scripts/seed_e4c_dates_demo.py` (45 đơn trải 45 ngày, idempotent theo dấu
  `SEED-E4C`, **chỉ chạy máy local**).

## 1. Trạng thái THẬT trước lượt (đo bằng `scripts/qa/wj_filterbar.py`, không đọc mã)

Bảng trong `docs/prompt-e4c.md` ghi Thông báo và Đổi trả là ✅ — đo ra **sai**:

| Màn | Ngày ngược TRƯỚC | Người dùng thấy gì |
|---|---|---|
| Lịch sử mua hàng | 200 · 0 record · **1 thông điệp trong thanh lọc** | ✅ mẫu tham chiếu |
| Thông báo | 200 · **10 record** · 0 thông điệp | ❌ bỏ luôn điều kiện ngày rồi trả **toàn bộ** danh sách; `date_error` được tính ở `portal.py:164` nhưng **không view nào in ra** |
| Đổi trả | 200 · 0 record · 0 thông điệp trong thanh, **banner đầu trang** | ⚠️ có báo nhưng sai chỗ, và gộp chung với lỗi sai định dạng |
| Giao hàng | 200 · 0 record · 0 thông điệp | ❌ im lặng ⇒ empty state "chưa có chuyến nào" |
| Đăng ký thi | 200 · 0 record · 0 thông điệp | ❌ im lặng; PC còn không giữ lại 2 ô ngày đã gõ |
| Báo cáo | 200 · tự kẹp `dt = df` | ❌ gõ 01/09 → 01/08 ra dữ liệu **đúng một ngày**, không lời giải thích |

Lỗi gốc BA nêu (*mobile Đăng ký thi ngày chưa áp dụng*) tái hiện đúng: `portal_exam.xml:125-142` là
khối dựng tay, 2 `<input type="date">` **không có `name`** và nằm ngoài `<form>` ⇒ bấm kính lúp không
gửi gì; controller thì đã nhận `date_from`/`date_to` từ lâu.

## 2. Đã làm

**Một nguồn duy nhất** — `wujia_portal_base/controllers/utils.py` (L3a, mọi `portal_*` đã depend,
**không thêm depend nào**): `ERR_DATE_RANGE` + `parse_portal_date()` + `date_range_error()`.
Trước đó có **hai** câu chữ khác nhau cho cùng một lỗi; nay 6 màn cùng gọi một hàm.

**Một khuôn hiển thị** — `<p class="wj-filter-error" role="alert" t-att-hidden="None if filter_error
else 'hidden'">` đi qua slot `fb_error` của component. Ba ràng buộc bắt buộc (đọc từ
`wj_ajax_list.js:87-99`): phần tử **luôn có mặt** (rỗng thì `hidden`), id **có trong `wjl_slots`**,
màn có `wjl_fragment` phải in cả 2 mảnh trong fragment — thiếu một trong ba là cả màn rơi về tải lại
trang. CSS `.wj-filter-error` dời từ `wujia_portal_purchase_history` lên
`wujia_portal_layout/static/assets/css/_components.css` (6 màn dùng chung, luật F2/F3), `?v=1302→1303`.

| Màn | Controller | View |
|---|---|---|
| Giao hàng | chặn query, giữ 2 ô ngày | 2 part `pcerr`/`merr` + fragment + `wjl_slots` + 2 `fb_error` |
| Đăng ký thi | trả `f_date_from`/`f_date_to` + `filter_error` (trước **thiếu hẳn**) | **khối dựng tay → component** (`fb_platform='m'`, `fb_action`, `fb_dates`, `fb_hidden` giữ `limit`, `fb_error`) ⇒ tự lên biến thể BA **04-DateRangeOnly** |
| Báo cáo | bỏ tự kẹp; ngày ngược ⇒ KPI 0 + chart rỗng **cùng bộ khoá** với nhánh thường | 2 `fb_error` + `wjl_slots` |
| Thông báo | `date_error` → `filter_error`, **chặn query** thay vì bỏ ngày rồi chạy tiếp; gỡ khoá `INVALID_DATE_RANGE` | 2 part + fragment + `wjl_slots` + 2 `fb_error` |
| Đổi trả | **tách nhánh**: sai định dạng giữ `notice='bad_filter'` ở banner, ngày ngược đi `filter_error` | 2 `fb_error` + `wjl_slots` |
| Lịch sử mua hàng | hằng cục bộ → import nguồn chung (câu chữ **giữ nguyên byte**) | 0 byte |

**Gỡ hai knob mồ côi của component**: `fb_dates['kind']` (ô ngày màn Thi nay `type="date"` ở cả hai
khổ) và **`clamp`** — xem §4.

## 3. Bảng nghiệm thu

| # | Phép đo | Kết quả | Kết luận |
|---|---|---|---|
| 1 | FB-10 render-diff (`wj_filterbar_inventory.py --diff`, 13 route × 6 khổ = **78 ô**) | **3 ô lệch, đúng 3 ô cố ý**: `/portal/exam` @360/390/391 `[]` → `['date_from','date_to','limit']` — chính là thanh lọc mobile trước đây không gửi gì. 0 lệch ngoài ý muốn | **Pass** |
| 2 | Ngày ngược 6/6 màn (`wj_filterbar.py` mục 1) | 6/6 trả **200 + đúng 1 thông điệp hiện trong thanh lọc**, cùng một câu chữ · **0 màn im lặng** (trước: 5) · 0 màn hiện 2 thông điệp | **Pass** |
| 3 | Đổi lọc → trang 1 (mục 2) | 5/5 route có phân trang: URL sau khi lọc **không còn `page=`** (ép `page=3` trước khi submit) | **Pass** |
| 4 | Sang trang giữ lọc (mục 3) | 5/5 route: **6/6 link phân trang** giữ đủ `date_from`+`date_to` (ép cỡ trang 10 để luôn có nhiều trang — không "Pass rỗng") | **Pass** |
| 5 | Ngày **lọc thật** ở khổ 390 (mục 4) | Lịch sử 10→0 · Giao hàng 20→0 · Đổi trả 20→0 · **Đăng ký thi 10→0** (lỗi BA nêu) · Báo cáo KPI `51 đơn / 22.046.650` → `0 / 0,00` · Thông báo: khổ này không có ô ngày (ghi rõ, không tính Pass) | **Pass** |
| 6 | `wj_measure --diff` 13 route × 5 khổ = **65 ô** | **0 ô lệch chiều cao · 0 ô mất record · 0 tràn ngang · 0 lỗi JS** — dáng E4b1/E4b2 không hồi quy một điểm ảnh | **Pass** |
| 7 | `-u` gộp 8 module `--stop-after-init` | RC=0, **0 ERROR mới** | **Pass** |
| 8 | Suite (`--log-handler "odoo.tests.result:INFO"`) | **648 test · 0 failed · 0 error** | **Pass** |
| 9 | `check_layers.py` | **3 vi phạm R1–R5 + 2 R7** — đúng bằng mốc có sẵn, không thêm | **Pass** |
| 10 | Mutation sweep (`scratchpad/e4c/mutations.py`) | xem §6 | **Pass** |

## 4. Phát sinh trong lượt: `clamp` chặn IM LẶNG cú dời khoảng ngày về trước

Guard mục 4 bắt được màn Báo cáo **gửi đi không có ngày**. Truy ra: `clamp` (knob từ E4a, nhân bản
`min`/`max` của markup cũ) đặt `max` của ô *Từ* = giá trị ô *Đến* đang hiển thị và ngược lại. Màn Báo
cáo mặc định điền sẵn khoảng ngày ⇒ mọi khoảng **về trước** đều bị trình duyệt từ chối: bấm Tìm kiếm
**không có gì xảy ra**, không request, không thông điệp. Đo lại thì bẫy này có ở **mọi** màn ngay khi
đã lọc một lần: `/portal/purchase-history?date_from=2026-08-01&date_to=2026-08-31` rồi gõ 01/01–15/01
⇒ `checkValidity()` của ô *Đến* = `false`, URL đứng yên.

Đây đúng loại lỗi lượt này đi sửa (chặn mà không nói), nên **gỡ `clamp` khỏi component và cả 6 call
site**: ngày ngược nay đã có thông điệp rõ ràng ở `fb_error`, không cần chặn ở lịch nữa. Hai test cũ
khẳng định `clamp` được đổi thành test khẳng định **không màn nào kẹp lại**.

## 5. Ngoài phạm vi (giữ nguyên, có chủ)

- Dáng PC/mobile của E4b1/E4b2 — đụng lại là hồi quy (đo §3 mục 6 để chứng minh không đụng).
- 2 call site Khảo sát (`wujia_portal_inspection`) — **defer vĩnh viễn**, luật 08/09.
- **Nợ nhịp G2**: `.wj-filter-card{margin-bottom:16px}` chồng `gap:8px` của khung ⇒ *lọc → danh sách*
  thành 24px ở **7 màn**. Gỡ là đổi nhịp 7 màn cùng lúc ⇒ **cụm E5** (`docs/prompt-e5.md`).
- Công nợ giữ thanh lọc riêng + week selector (FB-09 item 9) — 0 byte.

## 6. Mutation — mỗi mũi phải đỏ ĐÚNG guard của nó

`scratchpad/e4c/mutations.py` (harness E4b2 đã vá: `atexit` + `SIGTERM`/`SIGINT`, **không** `SIGHUP`).
**12/12 mũi đỏ đúng guard của nó.**

| Mũi | Phá gì | Guard đỏ |
|---|---|---|
| M1 | Giao hàng bỏ nhánh chặn ngày ngược | `test_ngay_nguoc_bao_ngay_tai_thanh_loc` |
| M2 | Báo cáo tự kẹp im lặng như cũ | + `test_giu_nguyen_chu_da_go` |
| M3 | Thông báo bỏ ngày rồi chạy tiếp | `test_ngay_nguoc_bao_ngay_tai_thanh_loc` |
| M4 | Đổi trả gộp ngày ngược lại vào banner | + `test_bad_date_range_returns_friendly_message` |
| M5 | Lịch sử quay lại câu chữ riêng | `test_sau_man_deu_lay_thong_diep_tu_nguon_chung` |
| M6 | Màn Thi bỏ id lỗi khỏi `wjl_slots` | `test_id_o_bao_loi_deu_nam_trong_wjl_slots` |
| M7 | Giao hàng bỏ mảnh lỗi khỏi fragment | `test_man_co_fragment_phai_in_ca_hai_manh_loi` |
| M8 | Lịch sử đặt lại kẹp ngày | `test_khong_man_nao_kep_lai_khoang_ngay` |
| M9 | Màn Thi để ô lỗi hiện thường trực | `test_o_bao_loi_luon_ton_tai_va_an_khi_khong_loi` |
| M10 | Màn Thi mobile bỏ ô ngày | `test_man_thi_mobile_da_vao_component_kem_wiring` + `test_thanh_loc_mobile_gui_duoc_hai_o_ngay` |
| M11 | CSS ô lỗi đổi tên | `test_css_bao_loi_o_dung_chu_layout` + `test_o_bao_loi_la_css_cua_khung_va_dung_token` |
| M12 | Component in ô lỗi ra ngoài form | 8 test của 5 màn cùng đỏ |

**Sweep bắt được 2 guard yếu của chính lượt này** — đúng giá trị của mutation, không phải thủ tục:

1. `test_man_co_fragment_phai_in_ca_hai_manh_loi` cắt chuỗi từ `wjl_fragment` trở đi, nhưng trong file
   `wjl_fragment` nằm **sau** template fragment ⇒ đang soi nhầm phần trang đầy đủ, xoá sạch mảnh lỗi
   khỏi fragment mà test vẫn xanh. Đã sửa: tìm đúng `<template id="*_results">` bằng xpath.
2. `test_css_bao_loi_o_dung_chu_layout` assert `'.wj-filter-error'` — là **tiền tố** của mọi tên đổi đi
   (`.wj-filter-error-x`) nên rule mất mà test vẫn xanh. Đã sửa: khớp cả dấu `{`.

## 7. Đối chiếu từng gạch cột `Kết quả mong muốn` (STT 139)

| # | Gạch đầu dòng của BA | Bằng chứng | Đạt |
|---|---|---|---|
| 1 | Đạt checklist FB-10 | render-diff 78 ô, 3 ô lệch đều là màn Thi mobile đi từ "không gửi gì" sang "gửi đúng 2 ô ngày" | ✔ |
| 2 | Mapping FB-09, UI giữ mẫu UAT | 21/21 thanh lọc thật đã vào component sau E4a/E4b1/E4b2/E4c; Công nợ + Đặt hàng giữ ngoại lệ đã duyệt | ✔ |
| 3 | Control/căn lề đồng nhất | `wj_measure --diff` 65 ô: 0 lệch | ✔ |
| 4 | **Ngày ngược có validation** | 6/6 màn: 200 + 1 thông điệp trong thanh lọc; trước lượt 5/6 im lặng | ✔ |
| 5 | **Ngày hợp lệ lọc đúng** | §3 mục 5, 5 màn có số đổi đúng theo khoảng | ✔ |
| 6 | Search Enter ≡ click | ô tìm nằm trong `<form method="get">` ⇒ Enter submit chính form đó; guard mục 2 submit bằng **nút** ra cùng URL | ✔ |
| 7 | Chip/select/query nhất quán | chip + select vẫn là slot/param cũ của từng màn (FB-07), FB-10 chứng minh bộ `name` không đổi | ✔ |
| 8 | Phân trang giữ điều kiện | §3 mục 4: 5/5 route, 6/6 link | ✔ |
| 9 | Không tràn ngang / mất nhãn | `wj_measure`: 0 tràn ngang ở 65 ô; nhãn "Từ"/"Đến" nằm trong pill (FB-05) | ✔ |
| 10 | Mobile không thêm "Xóa lọc" | component chỉ in reset khi `_fb_pc` (FB-03), có test | ✔ |
| 11 | Không thêm/bớt điều kiện; không đổi field/workflow/quyền/store | FB-10 render-diff; controller chỉ thêm nhánh chặn + khoá ctx `filter_error`, không đụng model/domain nào khác | ✔ |
| 12 | Evidence trước/sau + build hợp lệ | `scratchpad/e4c/{guard,fb10,measure}_{before,after}.json` + suite 648/0 | ✔ |

**12/12 ≥ 90% ⇒ đủ điều kiện ghi ledger và đưa issue về `Ready for Retest`.**

## 8. Lệnh deploy (gộp E4a + E4b1 + E4b2 + E4c, 12 module)

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,\
wujia_portal_delivery,wujia_portal_notification,wujia_portal_support,\
wujia_portal_knowledge,wujia_portal_return,wujia_portal_info_request,\
wujia_portal_exam,wujia_portal_report,wujia_portal_sale
```

Có đổi CSS (`_components.css?v=1303`) ⇒ nói người dùng tải lại cứng một lần.
