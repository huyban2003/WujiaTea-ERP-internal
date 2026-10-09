# Bàn giao nhóm Nhượng quyền — số ngày hợp đồng còn lại (WJ-PROFILE-002, issue #173)

> Lập 09/10/2026 (phiên I11). Không sửa code `wujia_franchise*` — chỉ ghi lại để chủ module tự chuyển.

## Việc BA yêu cầu

Ngày 08/10/2026, hồ sơ cửa hàng hiện "Còn lại 613 ngày" trong khi hợp đồng kết thúc 15/05/2028 (đúng là 585).
BA yêu cầu số ngày tự giảm theo lịch, cập nhật khi hợp đồng hiện hành đổi, **backend và Portal dùng cùng công thức**.

## Gốc

`wujia_franchise/models/wujia_franchise_management.py`:

- `remaining_days` và `is_expired` là field `store=True`, `@api.depends('franchise_end_date')`.
- ORM chỉ tính lại khi `franchise_end_date` đổi ⇒ qua mỗi ngày số cũ vẫn giữ nguyên (UAT lệch 28 ngày = lần tính
  cuối khoảng 10/09, lúc nạp hợp đồng nhiều kỳ). `is_expired` cũng vậy: hợp đồng vừa hết hạn vẫn là `False`.
- Không cron nào tính lại (`_cron_check_expired` chỉ nhắn tin, `_cron_refresh_state` của hợp đồng chỉ tính `state`).
- `context_today` theo tz của user chạy, không theo cửa hàng.

Ảnh hưởng backend còn lại: cột "Days remaining" ở list/form/kanban, kanban mobile "x days left", bộ lọc
"sắp hết hạn" (`remaining_days` 0–30, `wujia_franchise_management_views.xml:206`) — đều đọc số cũ.

## Portal đã làm (I11)

`wujia_portal_base` thêm `wujia.franchise.management._portal_contract_days()` → `(số ngày, đã hết hạn)`:

- `franchise_end_date − hôm nay`, **không gồm hôm nay** (= công thức backend hiện có); ngày cuối hợp đồng = 0, hôm sau = hết hạn.
- "Hôm nay" theo `partner_id.tz` của cửa hàng, tz rỗng/sai ⇒ `Asia/Ho_Chi_Minh`.
- Không có ngày kết thúc ⇒ `(None, False)`, Portal hiện "—".

Ba chỗ Portal đều dùng helper này: Hồ sơ cửa hàng PC + mobile, `/portal/franchises/<id>/profile`.

## Đề xuất cho backend

Giữ field stored (bộ lọc ≤30 ngày cần cột trong DB) và thêm cron chạy hằng ngày ngay sau nửa đêm giờ VN:

```python
@api.model
def _cron_refresh_remaining_days(self):
    recs = self.search([('franchise_end_date', '!=', False)])
    self.env.add_to_compute(self._fields['remaining_days'], recs)
    recs.flush_recordset(['remaining_days', 'is_expired'])
```

và cho `_compute_remaining_days` lấy "hôm nay" theo tz cửa hàng (giống helper portal) để hai bên không lệch 1 ngày
quanh nửa đêm. Khi chuyển xong, Portal có thể đọc lại field stored — báo nhóm Portal để gỡ helper.
