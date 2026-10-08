# I4 — Bảng lời gọi phạm vi cửa hàng (WJ-PORTAL-SCOPE-001, issue #152)

> Lập phiên I4a (08/10/2026). Dùng tiếp ở I4b. Luật BA 01/10: dữ liệu nghiệp vụ chỉ theo **một**
> cửa hàng đang chọn; chưa chọn ⇒ yêu cầu chọn; không có chế độ tổng hợp nhiều cửa hàng.

## Helper (`wujia_portal_base/controllers/portal.py`)

| Helper | Trả về | Dùng khi |
|---|---|---|
| `get_active_franchise_id()` | id hoặc `False`. Cookie hợp lệ ⇒ id; chỉ 1 cửa hàng ⇒ tự chọn; cookie không còn quyền ⇒ **xoá cookie** (I4a) | cần đúng 1 id |
| `get_current_store_ids()` **(mới, I4a)** | `()` hoặc `(fid,)` — không bao giờ nhiều cửa hàng | domain `('franchise_id', 'in', …)` |
| `get_store_scope_state()` **(mới, I4a)** | `'ok'` · `'need_pick'` (nhiều cửa hàng, chưa chọn) · `'no_store'` (chưa được gán) | chọn khối hiển thị khi rỗng |
| `get_active_franchise_ids_filter()` | chưa chọn ⇒ **mọi** cửa hàng | **DEPRECATED** — chỉ còn cho Khảo sát |

Khối hiển thị khi chưa có cửa hàng (một nguồn): `wujia_portal_base.wj_store_scope_prompt`, tham số `sp_scope`
(= `store_scope`). `need_pick` ⇒ "Chọn cửa hàng" + nút mở cùng modal chọn cửa hàng; `no_store` ⇒ liên hệ quản trị.

## Lời gọi

| Module | Route / chỗ gọi | Helper cũ | Hành vi trước I4a khi chưa chọn | Phiên |
|---|---|---|---|---|
| `wujia_portal_base` | `/portal` (Home, KPI + 7 block) | `_filter` | cộng mọi cửa hàng | **I4a ✅** |
| `wujia_portal_delivery` | `/portal/delivery`, `/results`, `/<id>`, `/<id>.ics` | `_filter` (3) | cộng; mở được chuyến của cửa hàng khác | **I4a ✅** |
| `wujia_portal_report` | `/portal/reports/orders`, `/export.xlsx` | `_filter` (2) | cộng | **I4a ✅** |
| `wujia_portal_return` | list, detail, create, đính kèm, form | `_filter` (5) | cộng | **I4b ✅** |
| `wujia_portal_info_request` | list, create, detail, cancel, AJAX values, **tệp đính kèm (route mới thay `/web/content`)** | `_filter` (5) + accessible | cộng; tệp mở được qua `/web/content` theo mọi cửa hàng | **I4b ✅** |
| `wujia_portal_support` + `wujia_support._portal_scope_domain` | list, create, detail, reply, tệp | `_filter` (2) | theo người tạo, mọi cửa hàng ⇒ nay **người tạo + cửa hàng đang chọn** | **I4b ✅** |
| `wujia_portal_notification` | list, detail, đọc, đếm chưa đọc, chuông | `_filter` (8) | cộng | **I4b ✅** — chưa chọn ⇒ chỉ thông báo toàn hệ + khối nhắc chọn (luật đã đọc: I6) |
| `wujia_portal_base` | `utils.check_attachment_access` (0 lời gọi) | accessible | mọi cửa hàng | **I4b ✅** (cửa hàng đang chọn) |
| `wujia_portal_inspection` (nhóm Khảo sát) | `portal.py:51,207,355` | `_filter` (3) | cộng (rỗng ⇒ fail-closed, không nhắc chọn) | bàn giao — `docs/handover-inspection-scope.md` |
| `wujia_portal_exam` | list | `get_active_franchise_id` | chưa chọn ⇒ "Chưa có đăng ký thi" | **I4b ✅** khối nhắc chọn (#157) |
| `wujia_portal_purchase_history` · `_debt` · `_sale` · franchise-information | — | `get_active_franchise_id` | đã theo 1 cửa hàng | regression (xanh I4a, I4b) |

## Còn ngoài I4 (ghi lại để không mở lại)

- Báo cáo vẫn kiểm role **cao nhất trên mọi cửa hàng** để vào trang — đổi theo role tại cửa hàng đang chọn là I5 (#153).
- Chuông thông báo khi chưa chọn cửa hàng: I4b đã về **chỉ thông báo toàn hệ**; luật đã đọc theo cửa hàng là I6.
- Navbar (`store_picker_navbar.xml`) tự tính lại cửa hàng đang chọn bằng QWeb — cùng kết quả với helper, chưa gộp.
- Sau I4b chỉ còn Khảo sát gọi `get_active_franchise_ids_filter()`. `_get_accessible_franchise_ids()` còn ở ir.rule, ảnh đại diện
  (`portal_layout`), mặc định `wujia_exam` và chọn cửa hàng — không phải truy vấn dữ liệu màn portal.
