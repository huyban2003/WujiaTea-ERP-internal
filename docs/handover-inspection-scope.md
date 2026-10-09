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
Sau I4b (08/10) Khảo sát là **màn duy nhất** còn gọi helper này — mọi màn portal khác đã theo một cửa hàng đang chọn.

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
- Tệp: phát qua route có lọc theo phiếu + cửa hàng (mẫu `/portal/info-request/<id>/attachment/<att>` ở I4b), không dùng `/web/content`.
- Tham khảo cách làm ở `wujia_portal_delivery` (I4a): list + fragment AJAX + chi tiết + `.ics`, và test
  `wujia_portal_delivery/tests/test_i4a_delivery_scope.py` (ma trận chưa chọn / A / B / ID cửa hàng khác).
- Bảng lời gọi đầy đủ: `docs/i4-scope-callers.md`.

---

# Bàn giao nhóm Khảo sát — ngôn ngữ header (WJ-INSPECT-001, issue #164)

> Lập 09/10/2026 (phiên I9). Không sửa code `wujia_portal_inspection` — đã vá ở khung `wujia_portal_layout`.

## Gốc

4 route Khảo sát (`/portal/inspection`, `/ajax`, `/detail/<id>`, `/remediation/<id>` + `/submit`) khai `website=True`;
mọi route portal khác `website=False`. Route `website=True` đi nhánh frontend của `http_routing`: ngôn ngữ lấy theo
URL › cookie `frontend_lang` › context, lệch ngôn ngữ mặc định (`en_US`) thì redirect `/vi/portal/inspection`.
UAT: vừa đăng nhập trình duyệt đã có `frontend_lang=en_US` ⇒ header Khảo sát ra cờ Mỹ / "English (US)" trong khi
Home ra tiếng Việt (đo chỉ-đọc 09/10). Nội dung Khảo sát vẫn tiếng Việt vì chuỗi trong template viết cứng.

## Đã vá ở khung (không cần nhóm Khảo sát làm gì để hết lỗi)

`wujia_portal_layout/models/ir_http.py` `_match`: user đã đăng nhập trên `/portal*` ⇒ bỏ nhánh frontend ⇒ ngôn ngữ
theo `res.users.lang` như mọi màn portal, không redirect `/vi/...`. Khách chưa đăng nhập giữ nguyên.

## Khuyến nghị khi tiện

- Bỏ `website=True` ở 4 route trên (website không cài trên portal; route không dùng `request.lang` / `request.website`).
- Chuỗi tiếng Việt viết cứng trong template (vd `'DANH MỤC TIÊU CHÍ'` ở controller) ⇒ đưa qua `_()` / QWeb dịch được
  để đổi ngôn ngữ thì nội dung đổi theo header.
