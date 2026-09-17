# E4 — Kiểm kê Filter (`CMP-FB-001` / `UI-FILTER-001`, STT 139)

Đếm bằng **`lxml` theo cấu trúc** (node `<form>` có `method="get"` và có hậu duệ là
`input`/`select`/`textarea` hoặc chip), **không** bằng grep tên lớp — bài học D4e: grep thô bắt cả tên
con BEM nên đếm ra 36 trong khi sự thật là 7, phải đính chính ba lần; E3 đếm bằng cấu trúc nên không
đính chính lần nào.

Script: `scratchpad/e4/e4_inventory.py` · ngày đo: 2026-09-17 · cây mã `018cf6c`.

```
python3 scratchpad/e4/e4_inventory.py          # bản chi tiết từng control
python3 scratchpad/e4/e4_inventory.py --md     # đúng bảng §1 dưới đây
```

Đây là **chân lý của acceptance FB-10** — *“không tự thêm/bớt điều kiện giữa PC/mobile; ghi inventory
trước/sau từng màn”*. Bảng §1 là ảnh chụp **TRƯỚC** khi sửa byte nào; E4b/E4c so lại chính bảng này.

## 1. 24 form GET có control — 21 thanh lọc thật

| Màn / file | Dòng | VP | Họ class | Điều kiện (`name` · kiểu · nhãn) | Chip | Submit | Reset |
|---|---|---|---|---|---|---|---|
| `wujia_portal_debt/views/portal_debt.xml` | 17 | m | `wj-debt-filter` | `f_name` · select (component, 2 call site: 122 overview · 506 payment-history) | — | Xem | — |
| `wujia_portal_debt/views/portal_debt.xml` | 293 | pc | `wj-debt-pc-filter` | `week` · select · Tuần hóa đơn | — | Xem | — |
| `wujia_portal_debt/views/portal_debt.xml` | 580 | pc | `wj-debt-pc-filter` | `month` · select · Thời gian thanh toán<br>`q` · text · Tìm mã thanh toán, tham chiếu… | — | Tìm kiếm | — |
| `wujia_portal_delivery/views/portal_delivery.xml` | 267 | pc | `wj-pc-filterbar` | `q` · text<br>`date_from` · date<br>`date_to` · date<br>`bs` · select | — | **Tìm** | Xóa lọc |
| `wujia_portal_delivery/views/portal_delivery.xml` | **313** | m | `wj-filter-card` | `bs` · hidden<br>`q` · text<br>`date_from` · date<br>`date_to` · date | 4 (part `mchips`, `bs`) | (icon) | — |
| `wujia_portal_exam/views/portal_exam.xml` | 31 | pc | `wj-pc-filterbar` | `state` · select<br>`result` · select<br>`q` · text<br>`date_from` · **text**<br>`date_to` · **text** | 3 (ngoài form, JS) | Tìm kiếm | **Đặt lại** |
| `wujia_portal_info_request/views/portal_info_request_list.xml` | 34 | **pc+m** | `row g-2` | `state` · select<br>`request_type` · select | — | **Lọc** | — |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 36 | pc | `row g-2` | `keyword` · text | — | (icon) | — |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 156 | m | `wj-filter-card` | `keyword` · text | 1 + N category (`category_id`) | (icon) | — |
| `wujia_portal_notification/views/portal_notification.xml` | 208 | pc | `wj-pc-filterbar` | `keyword` · text<br>`type_id` · select<br>`unread` · select<br>`date_from` · date<br>`date_to` · date<br>`tab` · hidden | — | Tìm kiếm | **Làm mới** |
| `wujia_portal_notification/views/portal_notification.xml` | 276 | m | `wj-filter-card` | `unread` · hidden<br>`keyword` · text | 4 (part `mchips`) | (icon) | — |
| `wujia_portal_purchase_history/views/portal_history.xml` | **187** | pc | `wj-pc-filterbar` | `page_size` · hidden<br>`q` · text<br>`date_from` · date<br>`date_to` · date<br>`state` · select | — | **Tìm** | **Reset** |
| `wujia_portal_purchase_history/views/portal_history.xml` | 253 | m | `wj-filter-card` | `page_size` · hidden<br>`q` · text<br>`date_from` · date<br>`date_to` · date | 4 (part `mchips`: 2 preset + `state` + Xóa lọc) | (icon) | — |
| `wujia_portal_report/views/portal_report_orders.xml` | 35 | m | `wj-rep-mfilter` | `date_from` · date<br>`date_to` · date | — | Tìm | — |
| `wujia_portal_report/views/portal_report_orders.xml` | 176 | pc | `wj-pc-filterbar` | `date_from` · date<br>`date_to` · date | — | **Áp dụng** | **Đặt lại** |
| `wujia_portal_return/views/portal_return_list.xml` | 38 | pc | `row g-2` | `state` · select<br>`q` · text<br>`date_from` · date<br>`date_to` · date | — | **Lọc** | — |
| `wujia_portal_return/views/portal_return_list.xml` | 165 | m | `wj-filter-card` | `q` · text<br>`state` · select<br>`date_from` · date<br>`date_to` · date | — | (icon) | — |
| `wujia_portal_sale/views/portal_order_catalog.xml` | 237 | pc | `wj-pc-filterbar` | `keyword` · text<br>`category_id` · select | — | **Tìm** | — |
| `wujia_portal_sale/views/portal_order_catalog.xml` | 312 | m | `wujia-morder-search` | `keyword` · text<br>`category_id` · hidden | 1 + N category (part `mchips`) | (icon) | — |
| `wujia_portal_support/views/portal_support.xml` | 24 | pc | `row g-2` | `state` · select | — | **Lọc** | — |
| `wujia_portal_support/views/portal_support.xml` | 141 | m | `wj-filter-card` | `state` · hidden<br>`q` · text | 4 (`state`) | (icon) | — |
| `wujia_portal_inspection/.../portal_inspection_list_templates.xml` | 12 | pc | `wj-pc-filterbar wj-ajax-search-form` | `tab` · hidden<br>`search` · text | — | Tìm kiếm | Đặt lại | **defer** |
| `wujia_portal_inspection/.../portal_inspection_list_templates.xml` | 147 | m | `wj-ajax-search-form` | `tab` · hidden<br>`search` · text | — | — | — | **defer** |
| `wujia_portal_layout/views/wj_pagination.xml` | 19 | — | `wj-pagination__size-form` | `page_size` · select | — | — | — | **không phải Filter** (E3) |

**21 thanh lọc thật** = 24 − 2 Khảo sát (defer, luật 08/09) − 1 form cỡ trang của Pagination.

## 2. Bốn thứ chỉ lộ ra khi đếm theo cấu trúc

1. **`grep 'row g-2'` ra 10 chỗ nhưng chỉ 4 là thanh lọc** (support:24 · knowledge:36 · return:38 ·
   info-request:34). 6 chỗ còn lại là lưới trong form tạo/chi tiết — đụng vào là hỏng màn khác.
2. **`/portal/info-request` KHÔNG tách PC/mobile** (không có `d-none d-lg-*`, chú thích tại
   `portal_info_request_list.xml:76` ghi rõ) ⇒ **một** form phục vụ cả hai viewport. FB-10 “điều kiện
   PC = mobile” ở màn này là hiển nhiên đúng, nhưng hình học phải hợp cả hai khổ.
3. **Công nợ đã có component filter riêng** `wujia_portal_debt.wj_debt_filter` (2 call site mobile) —
   FB-09 item 9 cho giữ week selector, nên nó **không** nhập vào `wj_filter_bar`, chỉ căn lề/nhãn ở E4b.
4. **Ngày ở màn Thi là `type="text"`**, không phải `type="date"` (`portal_exam.xml:31`) — đây là đầu
   mối của lỗi BA nêu “mobile Đăng ký thi ngày chưa áp dụng”. Không sửa ở lượt này (E4c, phải tái hiện
   bằng UI trước).

## 3. Nhãn đang có 6 kiểu

| Nhãn | Màn | Theo FB-02 |
|---|---|---|
| submit `Tìm` | history PC · delivery PC · order PC · report mobile | → **Tìm kiếm** |
| submit `Lọc` | support PC · return PC · info-request | → **Tìm kiếm** |
| submit `Áp dụng` | report PC | → **Tìm kiếm** |
| submit `Xem` | debt PC ×1 · debt mobile | giữ (week/month selector, FB-09 item 9) |
| reset `Reset` | history PC | → **Xóa lọc** |
| reset `Đặt lại` | exam PC · report PC | → **Xóa lọc** |
| reset `Làm mới` | notification PC | → **Xóa lọc** |
| không có reset | 13 màn | **không thêm** (FB-02) |

## 4. Tiến độ theo lượt

| Call site | Lượt | Trạng thái |
|---|---|---|
| `portal_history.xml:187` (PC mẫu BA) | E4a | ✅ |
| `portal_delivery.xml:313` (mobile mẫu BA) | E4a | ✅ |
| `pc_preview.xml:92` (gallery, `div` không form) | E4a | ✅ |
| support:24 · knowledge:36 · return:38 · info-request:34 (PC Bootstrap) | E4b | ☐ |
| delivery:267 · notification:208 · exam:31 · report:176 · order:237 (PC `wj-pc-filterbar`) | E4b | ☐ |
| debt:293 · debt:580 (PC, giữ week/month) | E4b | ☐ |
| history:253 · notification:276 · support:141 · knowledge:156 · return:165 (mobile `wj-filter-card`) | E4b | ☐ |
| report:35 · order:312 · debt:17 (mobile lẻ) | E4b | ☐ |
| wiring ngày 4 màn + về trang 1 + guard | E4c | ☐ |
| 2 call site Khảo sát | — | **defer** (luật 08/09) |

**Nghiệm thu lượt E4a:** `docs/e4a-acceptance-matrix.md` (26/26 tiêu chí · 21/21 mũi mutation).
