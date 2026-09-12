# E9a — `WJ-SALE-002` (STT 138, dòng tuyệt đối 131): danh sách "Đơn hàng Ngô Gia"

**Ngày:** 2026-09-12 · **Module:** `wujia_sale` **19.0.4.4.0 → 19.0.4.5.0** · **DB đo:**
`wujia_tea_e9a` / `wujia_tea_e9a2` (clone `wujia_tea_mt4`, **có cài** `wujia_franchise_inspection`
+ `wujia_portal_inspection` giống UAT — luật E #1), cổng 8079, **không đụng** `wujia_tea_19`/8019.

## 1. Gốc rễ

Code có sẵn trên `main` (`8280459`, merge nhánh `thai` vòng 4) khai view **kế thừa dạng
extension** vào `sale.sale_order_tree` và `sale.view_sales_order_filter` ⇒ **lan sang mọi action
Sales Order chuẩn**, trái đúng điều BA cấm. Đo trước khi sửa:

```
DEFAULT_VISIBLE = [name, create_date, date_order, partner_id, franchise_id, area_id,
                   is_portal_order, is_return_order, total_planned_weight, batch_id,
                   user_id, activity_ids, amount_total, invoice_status]      ← đã lây
STD_SEARCH_FILTERS chứa filter_portal_only / filter_return_order / group_franchise …  ← đã lây
```

Cách vá: giữ `inherit_id` (đúng chữ "kế thừa" của BA) nhưng thêm **`mode primary`** — view primary
không áp lên view cha. Tiền lệ trong chính core Odoo: `sale.sale_order_view_search_inherit_sale`,
`sale_order_view_search_inherit_quotation`.

Thứ tự 13 cột ra đúng **chỉ bằng chèn field + đổi `optional`**, không cần `position="move"`: cột
`optional="hide"` không render nên thứ tự nhìn thấy chỉ phụ thuộc cột đang hiện.

## 2. Số đo sau khi sửa (XML-RPC + Playwright, chỉ đọc)

| Phép đo | Trước | Sau |
|---|---|---|
| List view **mặc định** của `sale.order` (action SO chuẩn) | 14 cột, **có** 6 field Wujia | 7 cột chuẩn Odoo, **0** field Wujia |
| Bộ lọc SO chuẩn `sale.view_sales_order_filter` | có 5 filter + 3 group-by Wujia | **0** mục Wujia |
| View "Đơn hàng Ngô Gia" | (không tồn tại riêng) | `mode=primary`, priority 99, inherit `sale.sale_order_tree` |
| Cột nhìn thấy của view Ngô Gia | — | **13/13 đúng thứ tự BA** |
| Action `view_ids` | rỗng (Odoo tự chọn) | `list → sale.order.list.inherit.wujia`, `form → sale.order.form` |
| `search_view_id` của action | `sale.order.list.select` (view chuẩn) | `sale.order.filter.wujia` |
| Lỗi JS khi mở 2 màn | — | **0** |

13 cột đo được trên trang chạy thật: `Number · Order Date · Confirmation Date · Franchise store ·
Area · Customer · Portal · Compensation · Warehouse · Planned weight · Delivery batch · Total ·
Status`.

Đọc ở `lang=vi_VN`: `Ngày đặt hàng · Ngày xác nhận · Đơn Portal · Đơn bù`; menu và action ra
**"Đơn hàng Ngô Gia"**; bộ lọc ra `Đơn từ Portal · Đơn bù hàng · Đơn thủ công · Đơn nháp · Đơn đã
gửi · Đơn đã xác nhận · Đơn đã hủy · Chưa có batch · Đã có batch`; nhóm theo `Theo cửa hàng · Theo
khu vực · Theo trạng thái · Theo kho · Theo batch`.

## 3. Lọc trên trang chạy thật ↔ đếm bằng ORM (mẫu khác 0 — luật E #5)

| Bộ lọc | Đếm trên trang | `search_count` | Khớp |
|---|---|---|---|
| Đơn nháp | 13 | 13 | ✅ |
| Đơn đã gửi | 1 | 1 | ✅ |
| Đơn đã xác nhận | 6 | 6 | ✅ |
| Đơn đã hủy | 9 | 9 | ✅ |
| Đơn từ Portal | 14 | 14 | ✅ |
| Đơn bù | 1 | 1 | ✅ |
| Đơn thủ công | 14 | 14 | ✅ |
| Chưa có Batch | 18 | 18 (0 phiếu dính batch) | ✅ |

DB đo ban đầu **không có** phiếu nào ở trạng thái *Đã gửi* (0/29) ⇒ đã dựng 1 phiếu mẫu trên bản
sao trước khi đo, để bảng không rơi vào "Pass rỗng".

## 4. Đối chiếu 10 tiêu chí `Kết quả mong muốn`

| # | Tiêu chí | Kết quả |
|---|---|---|
| 1 | Menu/action riêng, view chuẩn không bị sửa | ✅ đo + ảnh chụp 2 màn |
| 2 | Đúng 14 cột, đúng thứ tự, optional không mất cột bắt buộc | ⚠️ **13/14** — cột 14 `fulfillment_route_id` là blocker (mục 5) |
| 3 | `create_date` "Ngày đặt hàng" + `date_order` "Ngày xác nhận", ngày+giờ theo tz, readonly | ✅ `widget="datetime"`, `readonly="1"` |
| 4 | Ẩn `user_id/activity_ids/team_id/tag_ids`; `invoice_status/commitment_date/expected_date` optional hide | ✅ test_04 kiểm từng field |
| 5 | 6 field custom hiện đúng dữ liệu, đúng quyền, không sửa từ list | ✅ list không `editable`, `batch_id`/`total_planned_weight` readonly |
| 6 | `fulfillment_route_id` chỉ thêm khi field tồn tại, chưa có thì báo blocker | ✅ `grep -rn fulfillment_route custom/` = **0** ⇒ báo blocker, không tự tạo |
| 7 | Tìm kiếm/filter/group by đúng tập; tách Portal/bù/thủ công; no-batch chỉ batch rỗng | ✅ bảng mục 3 |
| 8 | Tổng tiền monetary, trạng thái đúng, đơn hủy giữ decoration | ✅ `currency_id` kế thừa sẵn, `decoration-muted` còn nguyên (ảnh) |
| 9 | Không ảnh hưởng form SO, luồng SO, invoice, picking, batch, record rule, multi-company, action khác | ✅ 0 hồi quy (mục 5), user giới hạn company thấy **0/29** |
| 10 | Retest 4 state × 3 nguồn đơn, user đủ quyền + user giới hạn | ✅ bảng mục 3 + kiểm user giới hạn |

**Đạt 9,5/10 ≈ 95% ≥ 90%.**

## 5. Hồi quy — chứng minh bằng run đối chứng (luật S57)

Cùng DB gốc `wujia_tea_mt4`, cùng bộ lệnh 6 module, chỉ khác cây mã:

| Cây mã | Kết quả |
|---|---|
| **Trước** (`57e2a2f`, worktree riêng) | **25 failed, 12 error / 233** |
| **Sau** | **24 failed, 12 error / 235** |

So tên từng test: **0 test đỏ mới**, đúng **1 test được vá** —
`TestWujiaOrderView.test_02_inherited_tree_view_structure_and_priority` (đỏ sẵn trên `main` vì XML
khai `priority 20` còn test assert `99`; đây là lỗi số 3 trong `docs/merge-thai-round4-review.md`).
36 test đỏ còn lại y hệt hai bên ⇒ **có sẵn**, không thuộc lượt này.

Riêng bộ test `wujia_sale`: **0 failed 0 error / 14** (trước: 1 failed / 12).

## 6. Mutation (luật E #7)

| Phép phá | Test đỏ |
|---|---|
| M1 **gỡ** dòng `mode primary` khỏi XML | **0 đỏ — phép phá SAI**: Odoo chỉ ghi field có trong bản ghi XML, bỏ dòng thì `mode` cũ trong DB còn nguyên |
| M1b đổi `mode primary → extension` | `test_02_view_is_primary_inherit` + `test_03_standard_views_untouched` |
| M2 đảo `warehouse_id` lên trước `is_portal_order` | `test_04_wujia_list_columns_and_order` |
| M3 đổi domain "chưa có Batch" sang `!= False` | `test_05_search_filters_and_group_by` |
| M4 trỏ action về search view chuẩn | `test_01_action_and_menu` |
| M5 `user_id` `optional hide → show` | `test_04_wujia_list_columns_and_order` |

M1 lặp lại đúng họ bẫy D6c M5: **báo 0 đỏ không có nghĩa guard rỗng, phải kiểm phép phá có thật
sự đổi trạng thái đang đo hay không**. Harness bắt buộc `assert s != before` vẫn không bắt được ca
này vì file *có* đổi — chỗ không đổi là **DB**.

## 7. Bài học i18n (mới, tốn gần nửa phiên)

Thêm msgid vào `i18n/vi_VN.po` là **chưa đủ**: `PoFileReader` (`odoo/tools/translate.py`) gọi
`pofile.merge(<module>.pot)`, mà `polib.merge` đánh **obsolete** mọi entry không có trong `.pot`,
còn `__iter__` thì `continue` qua entry obsolete ⇒ **bỏ qua im lặng, không một dòng cảnh báo**.
`wujia_sale.pot` trong repo dừng ở 11/08 nên:

- 10 msgid mới của lượt này ban đầu **không dịch**;
- và lộ ra **lỗi có sẵn**: "Manual orders"/"No batch" (anh Thái thêm 11/09) chưa bao giờ dịch, đồng
  thời menu + action **"Wujia Sales Orders"** vốn đã có dòng dịch "Đơn hàng Ngô Gia" trong `.po`
  nhưng chưa bao giờ hiện tiếng Việt trên UAT — **cùng một nguyên nhân**.

Cách đúng: `odoo-bin i18n export -c <conf> -d <db> -o <path> wujia_sale` rồi ghi đè `.pot`
(115 msgid). Sau đó **`-u wujia_sale` bình thường là đủ**, không cần `--i18n-overwrite` — đã đo
trên bản sao sạch `wujia_tea_e9a2` đúng bằng lệnh deploy thật.

Nhân tiện chuẩn hoá nốt 1 chỗ lệch quy ước: nhóm `group_batch` trước viết thẳng tiếng Việt
`string="Theo batch"` trong XML, nay về `"By batch"` + dòng dịch, đúng lối English-trong-code +
`.po` của module này.

## 8. Còn treo / LIMIT

1. **`fulfillment_route_id` không tồn tại** (`grep` = 0 trên toàn `custom/`) ⇒ bỏ cột "Tuyến cung
   ứng" và bỏ filter cùng tên. Xin BA khai field ở tab `1. Model/ Field` rồi mở phiếu phụ. Đây
   cũng là lý do bảng BA ghi "14 cột" mà chỉ liệt kê 13.
2. Hai cột Boolean *Đơn Portal* / *Đơn bù* bị Odoo thu hẹp nên **tiêu đề cột hiển thị cắt** thành
   "Đ…" — đó là cách Odoo tự tính bề rộng cột boolean, không phải lỗi nhãn; nhãn đầy đủ hiện khi
   rê chuột và trong menu chọn cột.
3. Cột `company_id` của Odoo nằm giữa `partner_id` và `amount_total`, chỉ hiện ở DB **nhiều công
   ty**; không nằm trong 13 cột BA liệt kê nên giữ nguyên hành vi chuẩn.
4. Số đo lấy trên bản sao DB, **chưa phải trên máy chạy thử** — sau khi deploy phải đo lại chỉ đọc
   trên chính UAT trước khi đánh dấu `ĐÃ DEPLOY UAT` (luật L14/L17).
