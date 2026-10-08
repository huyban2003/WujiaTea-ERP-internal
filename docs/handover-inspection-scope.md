# Bàn giao nhóm Khảo sát — phạm vi cửa hàng (WJ-PORTAL-SCOPE-001, issue #152)

> Lập 08/10/2026 (phiên I4a). Không sửa code `wujia_portal_inspection` — chỉ ghi lại để nhóm Khảo sát tự chuyển.

## Việc BA yêu cầu

Issue #152 (High) đưa **Khảo sát** vào phạm vi: `/portal/inspection` cùng AJAX, chi tiết, khắc phục và tệp liên quan
phải chỉ đọc/ghi dữ liệu của **một cửa hàng đang chọn**. Chưa chọn ⇒ không hiện dữ liệu gộp, yêu cầu chọn cửa hàng.
Sửa ID phiếu / ID tệp / tham số cửa hàng sang cửa hàng khác ⇒ không đọc/ghi được.

## Hiện trạng module Khảo sát

`wujia_portal_inspection/controllers/portal.py` gọi `get_active_franchise_ids_filter()` ở 3 chỗ (dòng 51, 207, 355).
Helper này khi user nhiều cửa hàng **chưa chọn** trả **mọi** cửa hàng ⇒ danh sách/chi tiết Khảo sát gộp nhiều cửa hàng.

Helper cũ **giữ nguyên hành vi** (chủ dự án chốt 08/10: không đổi màn của nhóm khác) và đã ghi DEPRECATED.

## Đề xuất chuyển

```python
from odoo.addons.wujia_portal_base.controllers.portal import (
    get_current_store_ids, get_store_scope_state,
)

franchise_ids = get_current_store_ids()          # () hoặc (fid,)
if not franchise_ids:
    # render khối nhắc chọn dùng chung, không truy vấn phiếu
    values['store_scope'] = get_store_scope_state()   # 'need_pick' | 'no_store'
```

```xml
<t t-if="not franchise_ids" t-call="wujia_portal_base.wj_store_scope_prompt">
    <t t-set="sp_scope" t-value="store_scope"/>
</t>
```

- Chi tiết / khắc phục / tải tệp: kiểm `record.franchise_id.id in get_current_store_ids()` (không dùng danh sách mọi cửa hàng).
- Tham khảo cách làm ở `wujia_portal_delivery` (I4a): list + fragment AJAX + chi tiết + `.ics`, và test
  `wujia_portal_delivery/tests/test_i4a_delivery_scope.py` (ma trận chưa chọn / A / B / ID cửa hàng khác).
- Bảng lời gọi đầy đủ: `docs/i4-scope-callers.md`.
