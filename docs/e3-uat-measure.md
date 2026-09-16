# E3 — Đo lại trên chính UAT sau khi nâng cấp (16/09/2026)

Máy chủ `http://113.161.187.126:8019`, DB `wujia_tea_19`. **Chỉ đọc**: không tạo, không sửa, không
xoá bản ghi nào; không chạy `-u`; không seed.

## 0. Cổng deploy — mở bằng ba bằng chứng độc lập

Chủ dự án báo "đã deploy nhưng chưa nâng cấp module". Đo ra ngược lại — **đã nâng cấp xong**:

| Bằng chứng | Kết quả |
|---|---|
| Phiên bản 23/23 module wujia đọc qua XML-RPC | khớp **tuyệt đối** repo `ad2ec8b`: layout `19.0.50.0.0` · base `19.0.7.17.0` · exam `19.0.5.15.0` · debt `19.0.4.8.0` · sale `19.0.4.17.0` · `wujia_sale` `19.0.4.6.0` · franchise `19.0.6.0.0` · franchise_contract `19.0.2.0.0`; `write_date` 16/09 16:30–16:31 |
| Template có thật trên máy chủ | `ir.ui.view` `wujia_portal_layout.wj_pagination` (id 3023) + **14 view gọi nó** |
| Tệp giao diện | `_components.css?v=1292` trả 200, chứa **23** rule `wj-pagination` |

Một lần nâng cấp này gánh cả **E1 + E2a/b + E3a/b/c + E9a + E9b**.

## 1. Đối chiếu 10 gạch đầu dòng `Kết quả mong muốn` của `UI-PAGINATION-001`

Tài khoản đo `em.hcm` (HCM-01 — kho dữ liệu lớn nhất, chọn theo bài học D6d để tránh mẫu rỗng).

| # | Bullet BA | Kết quả | Bằng chứng đo trên UAT |
|---|---|---|---|
| 1 | Một component chung, không mỗi route một kiểu | **Pass** | 10 route × 6 khổ = **60 ô**: `wj-pagination` **36 nút**, họ pager cũ **0**, 0 lỗi JS |
| 2 | PC ≥992: count + page-size + numbered nav | **Pass** | `/portal/purchase-history@1440`: `‹ 1 2 ›` + `aria-current="page"` ở nút 1; `/portal/knowledge@1440` 4 nút |
| 3 | Mobile <992: Prev + "Trang x / y" + Next | **Pass** | `@991/390/360` mỗi ô còn **2 nút** (Trang trước/Trang sau) — đúng bố cục gọn |
| 4 | Visual 36 · radius 10 · gap 8 · 14/20/600 · chevron 16 | **Pass** | 36/36 nút: `h=36 w=36 radius=10 font=14 line=20 weight=600 chev=16`, `gap=8` trên `nav[aria-label="Phân trang"]` |
| 5 | Vùng chạm ≥44 mobile, visual không nở | **Pass** | `::before` `position=absolute` `44×44` trên **mọi** nút, trong khi hộp nhìn thấy vẫn 36×36 |
| 6 | Ẩn hẳn khi `totalPages <= 1` | **Pass** | **48/48 ô** của 8 route một trang ra `nav = 0` (support 8 · return 7 · delivery 3 · notification 3 · info-request · exam 1 · debt 8 hoá đơn · order 8 SP) — bằng chứng dương, không phải thiếu dữ liệu |
| 7 | Đổi trang không mất filter/sort/keyword | **Pass** | xem §2 |
| 8 | a11y: `nav[aria-label]`, `aria-current`, tên đọc được, không `href="#"` | **Pass** | `label="Phân trang"`, `aria-current="page"`, `name="Trang trước"/"Trang sau"`, mọi `href` là URL thật |
| 9 | Nút vô hiệu không phải link | **Pass** | trang 1: `<span class="… is-disabled" aria-disabled="true">`, `tabbable=false`, `href=null` |
| 10 | Không tạo variant theo route | **Pass** | cùng một bộ class/giá trị đo được ở cả purchase-history lẫn knowledge, PC lẫn mobile |

**10/10 Pass.**

## 2. Giữ bộ lọc khi đổi trang — đo bằng link thật trên UAT

| Biến thể mở trên UAT | Link nút trang đo được |
|---|---|
| `?q=S0&page_size=10` | `?q=S0&page_size=10&page=2` |
| `?q=a` (knowledge) | `?q=a&page=2` |
| `?page=2&page_size=10` | `?page_size=10&page=1` — `page` bị **thay**, không nhân đôi |
| `?date_from=2020-01-01&date_to=2030-12-31&q=S0&page_size=10` | giữ **nguyên cả bốn** tham số + `page=2` |

Dòng cuối là **chính họ lỗi E3c đã vá** ("lịch sử thanh toán rơi `date_from`/`date_to` khi sang
trang"): trên UAT `payment-history` chỉ có 6 thanh toán ⇒ 1 trang ⇒ không có nút để bấm, nhưng
`/portal/purchase-history` đi qua **đúng cùng một** `build_pager()` — nguồn duy nhất dựng query-string —
nên ca lỗi được chứng minh trên chính máy chủ. 24 nút của các biến thể có bộ lọc: **0 vi phạm**.

## 3. Hai màn mobile không đủ dữ liệu — chứng minh bằng ba lớp thay cho một dòng LIMIT trần

E3c vá "mobile Thi và Đặt hàng không có nút trang nào". UAT có **1** phiếu thi và **8** sản phẩm
(bậc cỡ trang nhỏ nhất là 10 và 24) ⇒ ép `?page_size` cũng không ra trang 2, mà seed thì làm bẩn
dữ liệu BA đang retest. Thay vì ghi LIMIT trần:

1. **Call site có thật trên máy chủ** — đọc `ir.ui.view.arch_db` trên UAT: `portal_exam_schedule` và
   `portal_order_catalog_results_part` mỗi view có **hai** lần gọi `wj_pagination`, một nằm cạnh khối
   PC (`wj-pc-*`), một nằm cạnh khối mobile (`wujia-mexam-card-line`, `wujia-morder-mstep`). Đúng
   call site mobile mà E3c thêm, ghi 16/09 16:31.
2. **Chính component đó render đúng ở khổ mobile trên UAT** — component là *một markup, hai bố cục
   bằng CSS*, và ở `@390/@360` nó đo ra 2 nút, 36 visual, 44 chạm (§1 dòng 3–5).
3. **Runtime đầy đủ đã đo ở DB cô lập** `wujia_tea_e3c` (45 phiếu thi, 60 sản phẩm):
   `docs/e3-acceptance-matrix.md` §1 dòng 3, có ảnh `portal_exam@390`, `portal_order@390`.

**LIMIT còn lại (hẹp):** chưa nhìn tận mắt nút trang 2 của Thi/Đặt hàng *trên UAT*; ba lớp trên thay thế.
Cùng lý do đó, ô chọn cỡ trang thật của Công nợ (10/20/50, trước là nhãn giả) và bậc 24/48/96 của
Đặt hàng chưa quan sát được trên UAT vì component tự ẩn khi ≤1 trang.

## 4. Hồi quy trên chính UAT

`scripts/qa/wj_measure.py` — 13 route × 5 khổ (65 ô):

| Phép đo | Kết quả |
|---|---|
| RULE 1 HIERARCHY vi phạm | **0** |
| Tràn ngang | **0** |
| Lỗi JS | **0** |
| Màn mất bản ghi | **0** |
| "Redirect ngầm" | 5 ô, **không phải lỗi**: `/portal/inspection` → `/vi/portal/inspection`, status 200 (tiền tố ngôn ngữ của website). E3c không sửa file nào của `wujia_portal_inspection` |

## 5. Sổ ghi

`scratchpad/e3-uat-all.json` (60 ô) · `scratchpad/e3-uat-filter.json` · `scratchpad/e3-uat-dates.json` ·
`scratchpad/e3-uat-measure.json`.
