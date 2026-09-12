# Merge nhánh `thai` — vòng 4 (11/09/2026)

**Người merge:** Dev portal (Claude) · **Kết quả:** đã merge + push lên `main`, **KHÔNG sửa
một dòng code nào của anh Thái** (chốt của chủ dự án trong phiên).

Tài liệu này để **anh Thái đọc và tự vá**. Mọi kết luận dưới đây đều có **log chạy thật** kèm
theo, không suy từ đọc code.

---

## 1. Phạm vi vòng 4 — nhỏ hơn hẳn 3 vòng trước

Khác 3 vòng merge trước, lần này anh Thái đã **tự push thẳng 6 commit lên `origin/main`**:

| Commit | Nội dung |
|---|---|
| `8280459` | `wujia_sale` view đơn bán + i18n + test + `scripts/test_wj_sale_search_challenger.py`; thêm dependency **`sale_stock`** |
| `66f1949` | chuẩn hoá cách đặt tên (1 dòng) |
| `6dd9e08` | `wujia_franchise_inspection` — controller + model + CSS/JS khảo sát |
| `6e77edb` | merge |
| `95f3843` | **module mới `wujia_franchise_operations`** (Employee · Shift · Schedule · Expense · Revenue) |
| `6628b01` | bỏ link ngoài trong manifest |

Nhánh `thai` do đó chỉ còn **đúng 1 commit** chưa vào main:

- **`5f291be` "add code update"** — 10 file, toàn bộ nằm trong `wujia_franchise_operations`:
  thêm `wizard/` import doanh thu (Excel/CSV), 2 dòng ACL, 1 test, đổi nhãn 2 key Selection,
  sửa `views/revenue_views.xml`.

**Merge là fast-forward sạch, 0 conflict.** `merge-base(main, thai)` trùng đúng `origin/main`.

```
git pull --ff-only origin main      # 7bb20a1 → 6628b01
git merge  --ff-only origin/thai    # 6628b01 → 5f291be
```

---

## 2. 🔴 Lỗi chặn #1 — wizard import doanh thu **không chạy được lần nào**

**File:** `custom/wujia_franchise_operations/wizard/wujia_franchise_revenue_import_wizard.py`

Wizard suy ra nguồn nhập từ đuôi file rồi ghi thẳng vào field `source`:

```python
ext = self.file_name.lower().split('.')[-1]
if ext in ('xlsx', 'xls'):
    source_val = 'excel'          # ← key này không tồn tại
elif ext == 'csv':
    source_val = 'csv'            # ← key này cũng không tồn tại
...
new_rec = self.env['wujia.franchise.revenue'].create({
    ...
    'source': source_val,
})
```

Nhưng `models/wujia_franchise_revenue.py:50` chỉ khai **hai** key:

```python
source = fields.Selection([
    ('manual', 'Manual'),
    ('import', 'Import (Excel/CSV)'),
], string='Entry Source', required=True, default='manual', tracking=True)
```

⇒ `create()` nổ ở **mọi** lần import, cả Excel lẫn CSV. Đây là lỗi **mới sinh trong chính
commit `5f291be`** (commit đó đổi *nhãn* hai key nhưng không đổi *key*), không phải nợ cũ.

### Bằng chứng — log chạy thật

Cài module + chạy test trên DB copy `wujia_tea_mt4` (bản sao `wujia_tea_mt3` của vòng merge 3,
đã có `wujia_franchise_inspection` installed):

```
ERROR wujia_tea_mt4 odoo.addons.wujia_franchise_operations.tests.test_franchise_operations:
    ERROR: TestFranchiseOperations.test_10_revenue_import_wizard
Traceback (most recent call last):
  File ".../wujia_franchise_operations/tests/test_franchise_operations.py", line 206,
      in test_10_revenue_import_wizard
    action = wizard.action_import()
  File ".../wizard/wujia_franchise_revenue_import_wizard.py", line 102, in action_import
    new_rec = self.env['wujia.franchise.revenue'].create({
  ...
  File ".../odoo/orm/fields_selection.py", line 235, in convert_to_cache
    raise ValueError("Wrong value for %s: %r" % (self, value))
ValueError: Wrong value for wujia.franchise.revenue.source: 'csv'

ERROR wujia_tea_mt4 odoo.tests.result: 0 failed, 1 error(s) of 10 tests
```

Chính test `test_10_revenue_import_wizard` anh Thái viết kèm trong commit cũng assert
`all(r.source == 'csv' ...)` ⇒ **test đó chưa từng được chạy trước khi push**.

### Hai cách vá — mời anh Thái chọn, bên portal **không tự áp**

- **(a) Mở rộng Selection** — thêm `('excel', …)` và `('csv', …)`, giữ `('import', …)` cho bản
  ghi cũ. Giữ được thông tin "nhập bằng định dạng gì" ngay trên field, nhưng làm Selection có
  4 key mà nghiệp vụ chỉ cần 2 trạng thái (tay / nhập file) ⇒ báo cáo, group-by sau này phải
  gộp lại.
- **(b) Map cả hai về `'import'`** — bỏ biến `source_val`, luôn ghi `'import'`. Đuôi file đã
  nằm sẵn trong `source_reference` (wizard đang ghi `self.file_name`) nên **không mất thông
  tin nào**. Ít rủi ro hơn, không đụng schema. Nhớ sửa luôn assert của
  `test_10_revenue_import_wizard`.

---

## 3. 🔴 Lỗi chặn #2 — `wujia_franchise_operations` **thiếu dependency**, không cài được

`views/wujia_franchise_management_views.xml` kế thừa form Cửa hàng và dùng field
`supervision_user_id`. Field đó **chỉ được khai trong `wujia_franchise_inspection`**
(`models/wujia_franchise_management.py:9`), trong khi manifest của
`wujia_franchise_operations` chỉ khai:

```python
'depends': ['base', 'mail', 'wujia_franchise'],
```

⇒ trên DB chưa cài `wujia_franchise_inspection`, lệnh `-i wujia_franchise_operations` **chết**:

```
odoo.tools.convert.ParseError: while parsing
    .../wujia_franchise_operations/views/wujia_franchise_management_views.xml:4
Error while validating view near:
<form string="Franchise store"> ...
Field `supervision_user_id` does not exist
View error context: {'name': 'wujia.franchise.management.form.inherit.operations', ...}
```

Trên UAT hiện `wujia_franchise_inspection` **đang installed** nên module có thể cài được
**do may mắn về thứ tự**, chứ manifest vẫn sai. Đề nghị anh Thái thêm
`'wujia_franchise_inspection'` vào `depends` (hoặc tách phần view dùng
`supervision_user_id` sang một module cầu nối).

---

## 4. 🔴 Lỗi #3 — test `wujia_sale` của chính anh Thái mâu thuẫn với view của chính anh Thái

`custom/wujia_sale/views/sale_order_views.xml:59` khai `<field name="priority">20</field>`,
còn `custom/wujia_sale/tests/test_wujia_order_view.py:49` lại assert `priority == 99`:

```
FAIL: TestWujiaOrderView.test_02_inherited_tree_view_structure_and_priority
AssertionError: 20 != 99 : Priority must be 99
```

Cần chốt một con số rồi sửa **một trong hai** phía. (View filter cùng file đang để `99`, nên
nhiều khả năng ý định ban đầu là 99.)

---

## 5. Điểm tốt — ghi nhận

- **ACL chấm đúng theo group** (`group_franchise_operations_user` / `_manager`), không có dòng
  nào mở cho `base.group_user`. Khác hẳn vòng merge 1 (khi đó phải sửa hộ ACL mở toang).
- **Không có `sudo()` nào ở đường ghi** của wizard.
- Wizard **có kiểm trùng (idempotency)** theo `(franchise_id, business_date, state)` trước khi
  tạo bản ghi doanh thu — đúng hướng.
- Có fallback parse CSV khi `openpyxl` hỏng, và có `default_franchise_id` khi dòng thiếu mã
  cửa hàng.

---

## 6. Hồi quy: merge **không** làm hỏng gì của Portal — chứng minh bằng run đối chứng

Hai bằng chứng độc lập:

**(a) Code portal không đổi một byte.**

```
git diff 7bb20a1 HEAD --stat -- 'custom/wujia_portal_*'     → RỖNG
grep -rc "wj-mform" …                                        → 4 / 1 / 1 / 1 / 6 (khớp trước merge)
```

**(b) Run đối chứng** (bài học S57 — 7 error tưởng mới hoá ra có sẵn). Cùng một DB gốc
`wujia_tea_mt3`, cùng bộ lệnh, chỉ khác cây mã nguồn:

| Cây mã | DB | Kết quả |
|---|---|---|
| **Trước merge** (`7bb20a1`, worktree riêng) | `wujia_tea_mt5` | **4 failed, 3 error(s) / 474 tests** |
| **Sau merge** (`5f291be`) | `wujia_tea_mt4` | **5 failed, 4 error(s) / 488 tests** |

7 lỗi của bản trước merge **xuất hiện y hệt** ở bản sau merge ⇒ **có sẵn**. Hai lỗi mới đều
nằm trong code anh Thái:

- `wujia_franchise_operations::test_10_revenue_import_wizard` (mục 2)
- `wujia_sale::test_02_inherited_tree_view_structure_and_priority` (mục 4)

**⇒ 0 hồi quy do merge.**

### 7 lỗi có sẵn — để anh Thái và bên portal cùng biết

- **3 error `wujia_franchise_inspection`** (`test_franchise_inspection`, `test_inspection_access`,
  `test_supervision_schedule`) — cả ba chết ở `setUpClass` vì **cùng một nguyên nhân**:

  ```
  odoo.exceptions.ValidationError: Active store '[TEST-STORE-01] Test Store 01'
      must have an associated Partner for sales orders/invoicing.
  ```

  Đây là **va chạm giữa hai bên**: Sprint 57 (`WJ-FRANCHISE-003`) thêm ràng buộc
  `_check_partner_required_when_active` ở `wujia_franchise/models/wujia_franchise_management.py:209`,
  còn test khảo sát tạo cửa hàng `active` mà không gán Partner. **Cách vá rẻ nhất là ở phía
  test khảo sát**: thêm `partner_id` vào `setUpClass`, hoặc tạo store ở `status='draft'`.
  Bên portal **không tự sửa** vì theo luật không đụng hai module khảo sát.

- **4 fail `wujia_portal_layout::test_d3_card_header`** — đây là lỗi **của bên portal**, chỉ lộ
  ra trên DB **có cài `wujia_franchise_inspection`** (DB dev `wujia_tea_19` đang để module này
  `uninstalled` nên cụm D3–D6 chưa từng thấy). Bên portal sẽ tự xử lý, ghi nhận ở đây để đủ
  bức tranh.

---

## 7. Ba lưu ý khi deploy UAT

1. **`wujia_franchise_operations` là module MỚI** ⇒ phải `-i wujia_franchise_operations`,
   **không phải `-u`**. Và phải chắc `wujia_franchise_inspection` đã installed trước (mục 3).
2. **`wujia_sale` thêm dependency `sale_stock`** ⇒ phải chắc module đó cài được trên UAT.
3. **`wujia_franchise_operations/__manifest__.py` không bump version** (vẫn `19.0.1.0.0`) dù
   commit `5f291be` thêm 1 file view + 2 dòng ACL ⇒ **mất phép kiểm deploy bằng số phiên bản**.
   Đây đúng cái bẫy cụm D4 đã trả giá (13/14 module không bump ⇒ restart không nạp lại XML mà
   không ai biết). Đề nghị bump `19.0.1.1.0`.

---

## 8. Phạm vi bên portal **không đụng**

Theo quyết định 08/09/2026 của chủ dự án: **không sửa** `wujia_portal_inspection` và
`wujia_franchise_inspection`. Vòng merge này bên portal **cũng không sửa**
`wujia_franchise_operations` và `wujia_sale` của anh Thái — chỉ merge và báo cáo.
