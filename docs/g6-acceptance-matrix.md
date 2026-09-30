# G6 — Bảng nghiệm thu: "Ngày xác nhận" chỉ khi đơn đã xác nhận (149)

**Issue:** `WJ-ORD-029` (149, Medium, POR-013). BA mở ngày 29/09 sau khi thấy lỗi ở đơn nháp S00075: đơn "Chờ xác
nhận" mà vẫn hiện "Ngày xác nhận". Làm ngày 30/09/2026 (Mac).

**Module `-u`:** `wujia_portal_purchase_history` 19.0.3.21.0.

**Gốc lỗi:** Odoo gán `date_order` = lúc tạo cho báo giá, rồi ghi đè khi `action_confirm`. Portal in thẳng
`date_order` dưới nhãn "Ngày xác nhận", nên đơn draft/sent hiện giờ tạo như thể đã được xác nhận.

**Chủ dự án chốt 30/09:**
- Cột "Ngày xác nhận" ở bảng PC ghi "—" khi đơn draft/sent.
- Trang chi tiết **ẩn hẳn** dòng này.
- Nhãn "Ngày tạo" ở chi tiết đổi thành **"Ngày đặt hàng"** (vẫn lấy `create_date`).
- Chỉ `state == 'sale'` mới có ngày xác nhận (Odoo 19 không còn `done`).

**Sửa:**
- Controller thêm key `confirm_date` vào `_history_row_vals` + `_history_detail_vals`. Giá trị là
  `to_local_dt(date_order, tz)` khi `state == 'sale'`, còn lại `None`.
- Key `date_order` giữ nguyên cho caller khác.
- Template: cột PC đọc `confirm_date`; kv chi tiết `t-if`; nhãn kv + dòng meta đầu trang → "Ngày đặt hàng".
- **Không đổi dữ liệu `sale.order`.**

**Cách đo:**
- DB `wujia_g5s` (đã có G5), server 8055, user `dung.multi` ở HCM-01.
- Đơn **S05267** (draft) + **S00014** (sale).
- Bộ đo `scripts/qa/wj_history_g6.py`: chỉ GET, dùng được trên UAT.

## 1. Theo "Kết quả mong muốn"

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 1 | SO draft/sent: list/detail **không hiển thị "Ngày xác nhận"** | PC 1440/1024/992: cột = **"—"**, chi tiết **không có dòng** "Ngày xác nhận". Mobile 360/390/430: trang chi tiết không có chữ "Ngày xác nhận" (mobile vốn không in ngày này). Test cả draft lẫn sent | ✅ |
| 2 | Trạng thái vẫn "Chờ xác nhận"; có thể hiện **Ngày đặt hàng = create_date** | Chi tiết: kv "Ngày đặt hàng 30/09/2026 18:30" + meta đầu trang "Ngày đặt hàng … · Người đặt …". Trạng thái "Chờ xác nhận" không đổi. Mobile vẫn nhãn "Ngày đặt" (`create_date`) như trước | ✅ |
| 3 | SO sale/done: hiện **Ngày xác nhận = date_order theo timezone người dùng** | S00014: cột "05/09/2026", kv "05/09/2026 18:33". Test giờ UTC 29/09 18:30 → VN **30/09 01:30** (qua ngày) · Tokyo 30/09 03:30 · New York 29/09 14:30. Đơn "Đang giao" (suy từ chuyến, state vẫn `sale`) vẫn có ngày | ✅ |
| 4 | Filter / sort / label dùng **đúng nghĩa** | Lọc ngày + sắp xếp danh sách vốn đã theo `create_date` (E4c), không đổi. Nhãn: "Ngày đặt hàng"/"Ngày tạo" = `create_date`, "Ngày xác nhận" = `date_order` chỉ khi đã xác nhận | ✅ |
| 5 | **Không thay đổi dữ liệu** `sale.order` | Chỉ đổi phần hiển thị (controller + QWeb), 0 write. Test kiểm `state` giữ nguyên | ✅ |

## 2. Route × khổ

| Khổ | Cột PC draft / sale | kv chi tiết draft | kv chi tiết sale | 2 card cao | Tràn |
|---|---|---|---|---|---|
| 1440 | — / 05/09/2026 | Ngày đặt hàng · Người đặt · Trạng thái | + Ngày xác nhận | 178 = 178 | 0 |
| 1024 | — / 05/09/2026 | như trên | như trên | 178 = 178 | 0 |
| 992 | — / 05/09/2026 | như trên | như trên | 178 = 178 | 0 |
| 360 / 390 / 430 | (mobile không có cột) | không chữ "Ngày xác nhận" | — | — | 0 |

- Đơn nháp mất một ô trong lưới 2 cột, nhưng hai card "Thông tin đơn hàng" | "Batch / giao hàng" vẫn cao bằng nhau
  (card giao hàng có 4 ô).
- Ảnh: `scratchpad/g5/g6shots/` (không đưa vào repo).

## 3. Kênh bên kia + hiệu năng (trước = G5, cùng DB)

- **Mobile:** `/portal/purchase-history` + `/portal`, 3 khổ, **Δ0**.
- **PC:** vân tay bố cục `/portal/purchase-history` Δ0. Vân tay là hộp + style, không gồm chữ, nên đổi "30/09/2026"
  thành "—" không làm xê dịch cột. Nội dung chữ do `wj_history_g6.py` kiểm.
- **Query:** `/portal/purchase-history` 21 → 21 · `/portal/purchase-history/5267` 29 → 29, cả hai **Δ0**.
  `confirm_date` chỉ đọc `state`/`date_order` đã có sẵn trong bản ghi.

## 4. Test + kiểm tra

- **Test mới:** `wujia_portal_purchase_history/tests/test_g6_confirm_date.py`, 7 test, tag `wujia_g6`.
  - dataset draft/sent/sale;
  - 3 múi giờ;
  - đơn đang giao;
  - giữ key `date_order`;
  - render cột PC;
  - chi tiết draft + sale (kv + meta).
- **Mutation 7/7 đỏ:**
  - mọi trạng thái đều có ngày;
  - `sent` cũng tính là đã xác nhận;
  - quên đổi múi giờ;
  - cột PC đọc lại `date_order`;
  - chi tiết ghi "—" thay vì ẩn dòng;
  - nhãn kv về "Ngày tạo";
  - meta về "Ngày tạo".
- `-u` + test `wujia_portal_base` · `wujia_portal_purchase_history` · `wujia_notification` (có test quét
  `portal_history.xml`): **393/0/0**.
- Không thêm depend, nên `check_layers` không đổi.

## 5. LIMIT

- **Đơn huỷ:** bị loại khỏi Lịch sử từ trước, nên nhánh `cancel` không hiển thị ở đâu cả.
- **Cột bảng PC:** vẫn đặt tên "Ngày tạo". Nghĩa đúng (`create_date`), và chủ dự án chỉ chốt đổi nhãn ở chi tiết.
  Nếu BA muốn đồng bộ thành "Ngày đặt hàng" thì chỉ cần đổi một dòng.
- **Home "Đơn hàng gần đây":** dòng phụ in `date_order` **không kèm nhãn**. Với đơn nháp, giá trị này ≈ giờ tạo nên
  không sai nghĩa. Ngoài phạm vi 149, ghi lại để BA quyết.

**Tổng:** 5/5 → **100% "Kết quả mong muốn"** (ngưỡng ≥ 90%).
