# Cụm C5 — bảng đối chiếu acceptance (WJ-DELIVERY-005/006/007, WJ-HOME-003)

**Ngày:** 15/08/2026 · **Module:** `wujia_portal_delivery` `19.0.3.5.0` → `19.0.3.6.0`,
`wujia_portal_base` `19.0.7.2.0` → `19.0.7.3.0` (không migration, deploy chỉ cần
`-u wujia_portal_delivery,wujia_portal_base`).

**Cách đo:** DB copy cô lập `wujia_tea_c5` (tạo từ `wujia_tea_c4`), Odoo riêng **port 8055** —
không đụng `wujia_tea_19`/8019. Playwright + chromium ở **391×844** và **1920×1080**
(`scratchpad/measure_c5.py`, login qua `/web/session/authenticate` rồi gắn cookie), cộng 9 test
mới `--test-tags wujia_delivery_c5`.

**Kết quả tổng:** đo **20/20 đạt (100%)** · test mới **9/9 xanh** · hồi quy **75 test** 4 module
khác (`wujia_account` C1, `wujia_portal_debt` C2+C3, `wujia_portal_knowledge` C4,
`wujia_portal_purchase_history`) 0 failed · build `-u` RC=0, 0 ERROR.

**Dữ liệu đo (DB copy):** 7 chuyến — 3 `Sắp giao` (lịch 30/06–01/07), 2 `Đang giao` (có
`actual_departure`), 2 `Đã giao`; 8 đơn chưa giao trên các chuyến chưa hoàn thành (đối chiếu SQL
`count(distinct sale_id)` = 8).

---

## WJ-DELIVERY-007 — "Xuất phát" phải là giờ thực tế khi đã xuất phát

| Yêu cầu (Kết quả mong muốn) | Đo được | Pass |
|---|---|---|
| Chưa có giờ thực tế → hiện giờ dự kiến | `/portal/delivery/8` (Sắp giao): "Xuất phát (dự kiến) 01/07/2026 · 17:00" — đúng `planned_departure` | ✅ |
| Đã có giờ thực tế → **danh sách** hiện giờ thực tế | mobile: "Xuất phát (thực tế) 29/06 · 16:20"; PC bảng: "28/06/2026 · 14:10 (thực tế)" | ✅ |
| Đã có giờ thực tế → **chi tiết** hiện giờ thực tế | `/portal/delivery/7`: "Xuất phát (thực tế) 29/06/2026 · 16:20" ở cả 2 viewport | ✅ |
| Không tiếp tục hiện giờ dự kiến thay giờ thực tế | chuyến 7 có `planned 09:00` — chuỗi giờ dự kiến không còn xuất hiện ở ô Xuất phát (test `test_list_shows_actual_departure` assertNotIn) | ✅ |
| Đúng timezone người dùng/Portal | DB `actual_departure = 2026-06-29 09:20 UTC` → portal in **16:20** (+7, `to_local_dt`/`portal_tz`) | ✅ |

## WJ-DELIVERY-006 — status count phải theo kết quả đã lọc

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Danh sách chỉ hiển thị bản ghi phù hợp | `?q=SO02848` → đúng 1 chuyến (`BATCH/2026/06/30/003`) | ✅ |
| Badge "Tất cả" = tổng bản ghi trong kết quả đã lọc | `?q=SO02848` → **Tất cả 1** (trước: 7) | ✅ |
| Từng badge trạng thái = số bản ghi của trạng thái đó trong kết quả lọc | `?q=SO02848` → Tất cả 1 · Đang giao 1 · Sắp giao 0 · Đã giao 0 | ✅ |
| Áp bộ lọc khoảng ngày cũng phải khớp | `?date_from=2026-06-29&date_to=2026-06-30` → Tất cả 3 · Đang giao 2 · Sắp giao 1 · Đã giao 0, đúng 3 dòng | ✅ |
| Xoá search/filter → count về tập đầy đủ theo current store | `/portal/delivery` → Tất cả 7 · 2 · 3 · 2 | ✅ |
| Chọn 1 chip trạng thái không làm 0 các chip còn lại | `?bs=done` → chips vẫn 7 · 2 · 3 · 2, danh sách 2 dòng | ✅ |

## WJ-HOME-003 — block "Giao hàng sắp tới" phải đúng nghĩa

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Chỉ hiện giao hàng chưa hoàn thành, lịch sắp tới | Home mobile chỉ còn 2 chuyến `Đang giao` (`…/004`, `…/003`) | ✅ |
| Không hiện bản ghi Đã giao xong / Đã hủy | 2 chuyến `done` (`…/005`, `…/006`) biến mất khỏi Home (trước sprint có mặt) | ✅ |
| Ngày, giờ và trạng thái khớp backend | badge "Đang giao" = `delivery_batch_status=delivering`; giờ 16:20/15:15 = `actual_departure` +7 | ✅ |
| Thứ tự ưu tiên theo lịch dự kiến gần nhất | `order='planned_departure asc'` — `…/004` (29/06 07:30) đứng trước `…/003` (29/06 09:00) | ✅ |
| Không có dữ liệu → empty state phù hợp | khối `wj-empty-state--row` "Chưa có chuyến giao sắp tới" giữ nguyên, chỉ đổi nguồn dữ liệu | ✅ |

## WJ-DELIVERY-005 — Home phải cho thấy đơn chưa giao của current store

| Yêu cầu | Đo được | Pass |
|---|---|---|
| Hiện các chuyến đang giao / chưa hoàn thành của current store | 2 chuyến `Đang giao` hiện trên Home | ✅ |
| Hiện **tổng số đơn chưa giao** | dòng đếm "**8 đơn chưa giao**" dưới tiêu đề block; SQL `count(distinct sale_id)` = 8 | ✅ |
| Hiện **danh sách đúng các đơn** chưa giao | card in mã đơn: `SO02812` · `SO02848, SO02870` (khớp picking chưa giao của chính chuyến đó) | ✅ |
| Không gồm chuyến/đơn đã giao xong, hoàn tất, huỷ | test `test_home_counts_only_undelivered_orders`: đơn của phiếu `cancel` và của chuyến `done` không xuất hiện trong block | ✅ |
| Không hiển thị dữ liệu cửa hàng khác | test `test_home_hides_finished_batches`: chuyến của cửa hàng B vắng mặt; cùng domain `batch_franchise_domain` với `/portal/delivery` | ✅ |
| Trạng thái đổi → Home phản ánh sau khi tải lại | dữ liệu tính tại request, không cache; chuyến chuyển `done` biến khỏi block ngay lần tải kế | ✅ |

## Hồi quy

| Trang | 391×844 (HTTP · tràn ngang · lỗi JS) | 1920×1080 |
|---|---|---|
| `/portal` | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/delivery` (+ 3 biến thể lọc, 2 chi tiết) | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/debt` (C2+C3) | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/knowledge` (C4) | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/purchase-history` | 200 · 0 · 0 | 200 · 0 · 0 |
| `/portal/order` | 200 · 0 · 0 | 200 · 0 · 0 |

Test tự động: `wujia_delivery_c5` 9/9 · hồi quy `wujia_account` 17 + `wujia_portal_debt` 38 +
`wujia_portal_knowledge` 18 + `wujia_portal_purchase_history` 18 = **75 test, 0 failed**.

## LIMIT / ghi chú

- **Technical mapping WJ-DELIVERY-007 (BA nhờ Dev xác nhận):** field đúng là
  `stock.picking.batch.actual_departure`, được set tự động khi chuyến chuyển `delivering`
  (`wujia_delivery/models/stock_picking_batch.py`). Portal đọc `actual_departure or
  planned_departure` ở một chỗ duy nhất (`departure_value`), nhãn đổi theo dữ liệu
  ("Xuất phát (thực tế)" / "Xuất phát (dự kiến)") để phân biệt được bằng mắt.
- Chuyến **đang bốc hàng / đang giao** vẫn hiện trên Home dù lịch dự kiến đã qua — nếu chỉ lọc
  "lịch từ hôm nay" thì chuyến đang chạy dở sẽ biến mất, trái WJ-DELIVERY-005.
- Dòng "**N đơn chưa giao**" đếm trên **mọi** chuyến chưa hoàn thành của cửa hàng, còn 2 card
  bên dưới là 2 chuyến gần lịch nhất (số card đang là 2, thuộc phạm vi cụm **C7**) ⇒ tổng có thể
  lớn hơn tổng đơn của 2 card.
- Block giao hàng ở Home vẫn **chỉ có bản mobile** (`d-lg-none`) — dựng bản PC là fork, chủ dự án
  chốt 15/08 giữ nguyên mobile-only.
- Bộ lọc khoảng ngày vẫn lọc theo **lịch dự kiến** (`planned_departure`); C5 không đổi ý nghĩa
  bộ lọc, chỉ đổi giá trị hiển thị ở cột Xuất phát.
