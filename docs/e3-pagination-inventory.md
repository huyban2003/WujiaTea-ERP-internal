# E3 — Kiểm kê Pagination (`CMP-PGNT-001` / `UI-PAGINATION-001`, STT 130)

Đếm bằng **`lxml` theo cấu trúc** (node container có hậu duệ mang link/nút trang), không bằng grep
tên lớp — bài học D4: grep thô bắt cả tên con BEM nên đếm sai 3 lần trong một cụm.

Script: `scratchpad/e3_inventory.py` · ngày đo: 2026-09-15 · cây mã `8c458d1`.

## 1. Khối pager — 21 container / 14 file

| File | Dòng | Thẻ | Họ class | Lượt |
|---|---|---|---|---|
| `wujia_portal_base/views/portal_franchise_information.xml` | 137, 150 | `div` | `wj-pc-pagination` | ✅ E3b — phân trang thật |
| `wujia_portal_purchase_history/views/portal_history.xml` | 86 | `div` | `wj-pc-pagination` | ✅ E3a |
| | 175 | `nav` | `wujia-mhist-pager` | ✅ E3a |
| `wujia_portal_support/views/portal_support.xml` | 110 | `ul` | `pagination wujia-pagination` | ✅ E3a |
| | 209 | `ul` | `pagination wujia-pagination` | ✅ E3b |
| `wujia_portal_notification/views/portal_notification.xml` | 98 | `div` | `wj-pc-pagination` | ✅ E3b |
| | 208 | `div` | `wujia-mnoti-pager` | ✅ E3b |
| `wujia_portal_delivery/views/portal_delivery.xml` | 84 | `div` | `wj-pc-pagination` | ✅ E3b |
| | 191 | `nav` | `wujia-mhist-pager` | ✅ E3b |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 106 | `ul` | `pagination wujia-pagination` | ✅ E3b |
| | 268 | `nav` | `wujia-mknow-pager` | ✅ E3b |
| `wujia_portal_return/views/portal_return_list.xml` | 139 | `ul` | `pagination wujia-pagination` | ✅ E3b |
| | 290 | `nav` | `wujia-mhist-pager` | ✅ E3b |
| `wujia_portal_info_request/views/portal_info_request_list.xml` | 131 | `ul` | `pagination wujia-pagination` | ✅ E3b |
| `wujia_portal_exam/views/portal_exam.xml` | 97 | `div` | `wj-pc-pagination wj-exam-pc-pagination` | ✅ E3c (+ pager mobile MỚI) |
| `wujia_portal_debt/views/portal_debt.xml` | 396, 642 | `div` | `wj-debt-pc-pagination` | ✅ E3c (+ ô cỡ trang thật) |
| `wujia_portal_sale/views/portal_order_catalog.xml` | 78 | `nav` | `wj-pc-pagination wj-pc-order-pager` | ✅ E3c (+ pager mobile MỚI, bậc 24/48/96) |
| `wujia_portal_layout/views/pc_preview.xml` | 164 | `div` | `wj-pc-pagination` | ✅ E3c |
| `wujia_portal_inspection/views/portal_inspection_list_templates.xml` | 115 (+ 6 `page-nav-btn` 260–276) | `div` | `wj-pc-pagination`, `page-nav-btn` | **defer** (luật 08/09) |

## 2. Gốc rễ thật — `paginate()` là CODE CHẾT

`wujia_portal_base/controllers/utils.py:225 paginate()` **không có call site nào** trong toàn repo
(chỉ khai, chưa ai dùng). Hệ quả: **7 controller tự viết lại cùng một phép toán** `last_page =
max(1, (total + size - 1) // size)` và **6 cách nối query-string khác nhau**.

| Route | `page_size` | Dạng pager | Query-string dựng thế nào | Ẩn khi 1 trang? | Form page-size |
|---|---|---|---|---|---|
| purchase-history | 10 (opt 10/20/50) | `page.num` + `page_nums`/`offset`/`count`/`page_total` | `self._qs(**kw)` liệt kê tay 5 param | có (`page_count > 1`) | có, `page_size`, 4 hidden input tay |
| notification | 10 | `page.num` + `page_count` | join tay 9 cặp | có | có, `limit` |
| support | 20 | `page.num` + `page_count` | join tay 2 cặp (`state`, `q`) | có | không |
| return | 20 (max 100) | `page.num` + `page_count` | join tay 5 cặp | có | không |
| knowledge | 12 | `page.num` + `page_count` | join tay 3 cặp | có | không |
| info-request | 20 | `page.num` + `page_count` | **KHÔNG CÓ** — template tự nối `?page=&state=&request_type=` | có | không |
| delivery | 20 | `m_pager`: `page.num` + `page_nums`/`offset`/`count`/`page_total` | join tay 4 cặp | có | `<select disabled>` giả |
| exam | 10 (opt 10/20/50) | `pc_pager`: `from/to/total/size/page/pages/numbers` | join tay 6 cặp, **biến riêng** `querystring` | có (`pages > 1`) | có, `limit` |
| debt ×2 | 10 | `_pc_paginate` trên list RAM: `page` **int** + `pages` list đầy đủ | không có — link tự nối trong template | có | nhãn tĩnh `10 / trang` |
| order catalog | 24 | `_fallback_pager`: `pages[].url` dựng sẵn bằng `urlencode` | `urlencode` trong `_u()` | có | không |
| franchise-info ×2 | — | **không có pager** | — | — | `<select>` tĩnh, 0 link |

⇒ **5 hình dạng** + 6 cách dựng URL. Đây là lý do BA nêu rủi ro "route tự xây query string có thể
làm mất filter" — và info-request là ca vi phạm thật (rơi `q`, `date_from`, `date_to`).

## 3. Quyết định rút ra cho E3a

1. `paginate()` chết ⇒ thay bằng **`build_pager()`** trong `utils.py`: nhận `total, page, page_size`
   (không cần model — debt phân trang list trong RAM), trả **một** dict chuẩn. 7 bản sao phép toán
   biến mất.
2. **Query-string lấy từ `request.httprequest.args`** trừ `page` + blocklist (`notice`, `csrf_token`),
   thay vì mỗi route liệt kê tay. Vá luôn lỗi info-request và xoá 4 hidden input của form page-size.
3. Tên param page-size **giữ nguyên theo route** (`page_size` ở history, `limit` ở
   notification/exam) — đổi là vỡ bookmark và vỡ `syncFilterControls` của `wj_ajax_list.js`.
   `build_pager(size_param=...)`.
4. Template `wj_pagination` chỉ đọc dict chuẩn; **một markup**, hai bố cục bằng CSS
   (`≥992` desktopFull / `<992` mobileCompact) — không render hai khối rồi `d-none` (bẫy id trùng D6c).

## Tiến độ (cập nhật 16/09/2026, cụm ĐÃ KHÉP)

| Lượt | Trạng thái | Bảng nghiệm thu |
|---|---|---|
| E3a — nền `build_pager` + component + 2 route mẫu | ✅ `b9c50cc` | `docs/e3a-acceptance-matrix.md` |
| E3b — 5 màn còn lại + ô cỡ trang thật + phân trang thành viên | ✅ `41bbfd5` | `docs/e3b-acceptance-matrix.md` |
| E3c — thi, công nợ ×2, catalog, `pc_preview`, xoá 10 họ CSS cũ | ✅ 16/09 | `docs/e3-acceptance-matrix.md` (**đóng issue**) |

**Còn 0 khối tự dựng pager** trong portal. Ngoài 20 call site của kiểm kê, E3c thêm **2 khối pager
mobile hoàn toàn mới** (Thi, Đặt hàng) — hai màn này server đã cắt trang từ lâu nhưng giao diện điện
thoại không có nút trang nào, người dùng không sang được trang 2.

Riêng `wujia_portal_inspection` giữ **defer** (luật 08/09): 1 khối `wj-pc-pagination` + 6 `page-nav-btn`.
Hai họ CSS của nó **không xoá mà thu hẹp selector vào `.wj-inspection-pc`** để màn Khảo sát không đổi
dáng — "không đụng module khảo sát" gồm cả không làm hỏng gián tiếp.
