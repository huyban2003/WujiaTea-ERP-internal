# E3 — Bảng nghiệm thu CẢ CỤM (Pagination `CMP-PGNT-001` / `UI-PAGINATION-001`, STT 130)

Lượt cuối **E3c** (16/09/2026) khép cụm: phủ nốt 5 khối pager còn sót, vá 2 màn mobile vốn
**không có nút trang nào**, xoá 10 họ CSS cũ. Đây là bảng dùng để **đóng issue** — E3a/E3b cố ý
không đóng. Bảng chi tiết từng lượt: `docs/e3a-acceptance-matrix.md`, `docs/e3b-acceptance-matrix.md`.

- DB đo: `wujia_tea_e3c` (clone từ `wujia_tea_mt4`, **có** cài 2 module Khảo sát như UAT, chép cả
  `data/filestore/`), cổng 8097.
- Run đối chứng: worktree `scratchpad/e3/base_e3c` @ `41bbfd5` → DB `wujia_tea_e3cbase`, cổng 8099.
- Tài khoản đo: `em.hcm` (chủ HCM-01) — không dùng `admin` (bẫy "Pass rỗng", E3a §5).
- Seed: `scripts/seed_e3_pager_demo.py` + `scripts/seed_e3c_pager_demo.py` (`MARK='SEED-E3C'`):
  45 phiếu thi · 60 sản phẩm public · 45 hoá đơn · 45 thanh toán.

## 1. Đối chiếu từng gạch đầu dòng `Kết quả mong muốn` của issue

| # | Bullet BA | Kết quả | Bằng chứng (cả cụm) |
|---|---|---|---|
| 1 | Một component chung, không mỗi route một kiểu | **Pass** | 21 khối pager của kiểm kê nay là **20 call site `t-call` + 1 `defer` Khảo sát**; quét 10 route × 6 khổ: **201 nút component, 0 họ cũ ngoài Khảo sát** |
| 2 | PC ≥992: count + page-size + numbered nav | **Pass** | ảnh `portal_order@1440`: "Hiển thị 1–24 / 60 sản phẩm" · ô `24 / trang` · `‹ 1 2 3 ›`; `portal_debt@1440` cũng đủ 3 phần |
| 3 | Mobile <992: Prev + "Trang x / y" + Next | **Pass** | ảnh `portal_exam@390` và `portal_order@390` — **hai màn này trước E3c không có nút trang nào** |
| 4 | Visual 36 / radius 10 / gap 8 / 14·20·600 / chevron 16 | **Pass** | `wj_pagination.py` đo hình học 201 nút → **0 lệch** |
| 5 | Vùng chạm ≥44 mobile, không tăng chiều cao danh sách | **Pass** | `::before` tuyệt đối; diff `wj_measure` chỉ 13 ô đổi cao, đều đúng chiều cao khối pager mới |
| 6 | Ẩn hẳn khi `totalPages <= 1` | **Pass** | ô 1 trang → `nav=0`, mobile thêm `is-navless` |
| 7 | **Đổi trang không mất filter/sort/keyword** | **Pass** | xem §2 — ca lỗi thật của công nợ đã vá; PG-4 trên 7+ biến thể có bộ lọc: **0 vi phạm** |
| 8 | a11y: `nav[aria-label]`, `aria-current`, tên đọc được, không `href="#"` | **Pass** | 4 test template + đo runtime `aria-current` |
| 9 | Nút vô hiệu không phải link | **Pass** | render `<span aria-disabled="true">`, ngoài tab order |
| 10 | Không tạo variant theo route | **Pass** | một markup, hai bố cục bằng CSS; khác biệt duy nhất giữa route là `size_param` + bậc cỡ trang |

**10/10 bullet Pass.** Một mục `defer` có chủ đích: nhóm Khảo sát (§6).

## 2. Lỗi nghiệp vụ THẬT đã vá trong E3c (không chỉ là dọn giao diện)

| Lỗi | Trước | Sau |
|---|---|---|
| **Lịch sử thanh toán rơi bộ lọc ngày** | link trang chỉ mang `month` + `q` ⇒ `/portal/debt/payment-history?month=2026-09&q=SEED&page=2` **âm thầm bỏ** `date_from`/`date_to`, người dùng sang trang 2 là thấy dữ liệu ngoài kỳ đang lọc | link trang lấy nguyên query hiện tại: `?date_from=2026-09-01&date_to=2026-09-16&q=SEED&page=2` — cùng họ lỗi BA nêu ở `info-request` |
| **Mobile Thi không có nút trang** | server vẫn cắt 10 dòng/trang nhưng khối mobile không render pager ⇒ **điện thoại không bao giờ xem được trang 2** | có pager component (Prev · "Trang x / y" · Next) |
| **Mobile Đặt hàng không có nút trang** | như trên, 60 sản phẩm chỉ xem được 24 | có pager component |
| **Ô "10 / trang" của Công nợ là nhãn giả** | chữ tĩnh, bấm không được — người dùng tưởng đổi được | bậc thật 10/20/50, đi qua `parse_page_size` |
| **Đặt hàng không có ô cỡ trang** | cố định 24 | bậc 24/48/96 (bội của 24 để không vỡ hàng cuối lưới 3 cột) |

## 3. Bằng chứng máy

| Phép đo | Kết quả |
|---|---|
| Build `-u` 5 module | RC=0 |
| Test hồi quy 5 module đụng tới | **0 failed, 0 error / 493** |
| **Run đối chứng** `41bbfd5` (DB riêng, worktree riêng) | **0 failed, 0 error / 488** → +5 test = **đúng số guard mới**, 0 đỏ mới |
| Đột biến **10/10 mũi** | mỗi mũi **đỏ đúng guard của nó**; sau đó chạy lại suite sạch → 493 / 0 đỏ |
| `wj_pagination.py` 10 route × 6 khổ | **201 nút, 0 vi phạm PG-1..PG-4, 0 lỗi JS**, 0 họ cũ ngoài Khảo sát |
| Biến thể có bộ lọc | thêm **44 nút, 0 vi phạm** |
| `wj_measure.py --diff` 13 route × 5 khổ | **0 tràn ngang · 0 lỗi JS · 0 ô mất record**; chỉ 13 ô đổi chiều cao, tất cả trên 3 màn E3c |
| Ảnh thật | `/portal/exam`, `/portal/debt`, `/portal/debt/payment-history`, `/portal/order` ở 1440 và 390 |
| Viewport đo | 1440 · 1024 · 992 · 991 · 390 · 360 |

## 4. Kiểm kê khép sổ

`docs/e3-pagination-inventory.md`: 21 khối / 14 file ban đầu → **0 khối còn tự dựng pager**.
`paginate()` chết trong `utils.py` đã được thay bằng `build_pager()`; **7 bản sao phép toán** và
**6 cách nối query-string** biến mất. 10 họ CSS cũ bị xoá khỏi 8 file CSS portal.

## 5. Quyết định Dev tự chốt trong E3c

1. **Hai họ `wj-pc-pagination` / `wj-pc-page-btn` không xoá mà THU HẸP vào `.wj-inspection-pc`.**
   Xoá hẳn là màn Khảo sát (defer, không được đụng) mất dáng ngay — "không đụng" phải bao gồm cả
   không làm hỏng gián tiếp. Test cho đúng một ngoại lệ này và bắt mọi rule khác.
2. **Dòng "Tổng thanh toán trong thời gian lọc" tách ra `wj-debt-pc-histfoot`, nằm NGOÀI component.**
   Component tự ẩn khi `total_pages <= 1`; để dòng tổng bên trong là mất số tổng ngay khi kỳ lọc chỉ
   có 1 trang. Có guard riêng chống tái phát.
3. **`pc_preview.py` import `build_pager` TẠI CHỖ**, không ở đầu file: `wujia_portal_base` phụ thuộc
   `wujia_portal_layout`, import ngược ở module level là vòng tròn.
4. **Bậc Đặt hàng là bội của mặc định 24** (24/48/96) — bậc lẻ làm vỡ hàng cuối của lưới 3 cột.
5. **Giữ nguyên tên param từng route** (`limit` ở Thi, `page_size` ở phần còn lại) — kế thừa E3a.

## 6. `defer` — nhóm Khảo sát (luật 08/09/2026)

`wujia_portal_inspection/views/portal_inspection_list_templates.xml` còn 1 khối `wj-pc-pagination`
+ 6 nút `page-nav-btn`. **Không migrate, không xoá CSS của nó** theo quyết định của chủ dự án về hai
module của anh Thái. Dáng được giữ nguyên bằng cách thu hẹp selector (§5.1), nên màn Khảo sát không
đổi gì. Khi chủ dự án mở khoá, việc còn lại chỉ là đổi 1 khối sang `t-call` — nền đã sẵn.

## 7. LIMIT (ghi để BA retest biết, không phải lỗi mới)

- Dòng "Tổng thanh toán trong thời gian lọc" trước đây **dính liền số tiền** (`lọc:9.450.000`) do
  QWeb nuốt khoảng trắng đầu dòng. Đã sửa bằng `&#160;` ngay trong lượt này. Đối chứng xác nhận lỗi
  có sẵn từ trước E3c, không phải hồi quy.
- 10 dòng ERROR `Model wujia.franchise.revenue.compute.wizard has no table` trong log nâng cấp là của
  nhóm module khác, **có trước E3c** và không liên quan phân trang.
- Phải **tải lại trang bỏ cache** (Ctrl+Shift+R) khi retest: CSS đã bump `?v=1292`.
