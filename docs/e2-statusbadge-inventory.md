# Kiểm kê StatusBadge — `UI-STATUSBADGE-001` / `CMP-SB-001`

Đếm bằng **cấu trúc** (`lxml`, mọi thuộc tính `class` / `t-attf-class` / `t-att-class`),
không grep tên lớp trần. Script: scratchpad `e2/inv.py`. Mốc: 13/09/2026.

| Mốc | Call site còn mang họ badge cũ |
|---|---|
| Trước E2a | **114** (8 họ / 16 file) |
| Sau E2a | **77** |
| Call site component mới `.wj-status-badge` | **65** (9 file) |

## 1. Bảng mapping nguồn (sau E2a) — `wujia_portal_base/controllers/utils.py`

Một nguồn duy nhất cho PC lẫn mobile: `STATUS_VARIANT_BY_LABEL` + `status_badge()` /
`status_badge_for()`. Variant theo **đúng bậc BA ghi trong spec**.

| Module | Model | State | Nhãn | Class cũ | Variant BA |
|---|---|---|---|---|---|
| portal_base | sale.order | draft | Nháp | `wujia-badge-muted` | neutral |
| portal_base | sale.order | sent | Đã gửi | `wujia-badge-warning` | pending |
| portal_base | sale.order | sale | **Đã xác nhận** | `wujia-badge-success` ❌ | **info** ✅ (lỗi BA nêu) |
| portal_base | sale.order | done | Hoàn tất | `wujia-badge-success` | success |
| portal_base | sale.order | cancel | Đã hủy | `wujia-badge-danger` | danger |
| portal_base / delivery | wujia.delivery.batch | draft/assigned/loading | Chuẩn bị giao · Sắp giao | `wj-pc-badge--dlv-prep` / `wujia-mdelivery-badge--prep` | **processing** |
| portal_base / delivery | wujia.delivery.batch | delivering | Đang giao | `--dlv-going` | processing |
| portal_base / delivery | wujia.delivery.batch | done | Đã giao xong | `--dlv-done` | success |
| portal_base / delivery | wujia.delivery.batch | cancelled | Hủy chuyến | `--dlv-cancel` | danger |
| portal_base | wujia.return.request | submitted | Chờ xử lý | `wujia-badge-warning` | pending |
| portal_base | wujia.return.request | approved | Đã duyệt | `wujia-badge-success` | success |
| portal_base | wujia.return.request | rejected | Từ chối | `wujia-badge-danger` | danger |
| portal_base | wujia.support.ticket | new | Mới | `wujia-badge-info` | info |
| portal_base | wujia.support.ticket | processing | Đang xử lý | `wujia-badge-warning` | processing |
| portal_base | wujia.support.ticket | resolved/closed | Đã giải quyết · Đã đóng | `wujia-badge-success` / `-muted` | success / neutral |
| purchase_history | sale.order | (nhãn) | Chờ xác nhận · Đã xác nhận · Đang giao · Hoàn tất · Đã hủy | `wj-pc-badge--*` (PC) + `wujia-badge-*` (mobile), **2 dict trùng nhau** | pending · info · processing · success · danger |
| portal_sale | sale.order | (kết quả đặt hàng) | như trên | `wujia-mres-badge--*` | theo nhãn |
| portal_base | wujia.store / member | active | Đang hoạt động · Active | `wujia-badge-success` | success |
| portal_base | wujia.store.member | !active | Tạm khóa | `wujia-badge-warning` | pending |
| franchise | wujia.franchise | active/draft/khác | (hồ sơ) | `state-badge state-#{...}` | success / neutral / danger |

## 2. Họ BA **loại khỏi** migration (giữ nguyên, guard kiểm chéo 0 đổi)

`wujia-store-role-badge` (Role) · `wj-pc-badge--confirmed/--staff` trong bảng thành viên và
`profile_page` (Role) · `wj-pc-badge--area` (AreaBadge) · `wujia-header-badge`,
`wujia-bnav-noti-badge`, `wujia-mhome-nav-badge`, `wujia-msheet-item-badge` (Count) ·
`wj-filter-chip` · `wujia-mknow-badges` (Category) · `wujia-mexam-stepbadge` (Step) ·
`noti_badge_cls` ở `portal_home.xml:148,417` (loại thông báo = CategoryBadge) · `.badge*` Bootstrap.

## 3. Còn lại cho E2b — 77 call site

| Module | Còn | Ghi chú |
|---|---|---|
| wujia_portal_notification | 14 | + 2 override lệch spec (`portal_notification.css:104` 11px/3px 8px; `:429` height auto) |
| wujia_portal_exam | 13 | + override `portal_exam.css:796` min-width 118 |
| wujia_portal_return | 10 | map `COMPENSATION_STATUS_LABELS` kéo về nguồn chung |
| **wujia_portal_inspection** | **9** | 🚫 **defer** — module khảo sát, luật 08/09 cấm đụng |
| wujia_portal_knowledge | 8 | phần lớn là CategoryBadge → chỉ lọc badge trạng thái thật |
| wujia_portal_debt | 8 | 2 họ riêng `wj-debt-badge` / `wj-debt-pc-badge` |
| wujia_portal_base | 6 | 2 = notification type (loại), 2 = `wujia-badge-info` mã cửa hàng (loại), 2 = role (loại) |
| wujia_portal_info_request | 4 | |
| wujia_portal_support | 3 | 3 site còn lại (2 site dùng map chung đã migrate ở E2a) |
| wujia_portal_layout | 2 | RoleBadge trong `profile_page` — loại |

⇒ Phần **thật sự phải migrate ở E2b ≈ 56 call site**; 21 còn lại là defer (9) hoặc họ BA loại (12).

## 4. LIMIT
`.wj-pc-badge` **không xoá được**: `wujia_portal_inspection` dùng 9 chỗ (+ `wujia_franchise_inspection`),
thuộc phạm vi cấm đụng. Rule CSS cũ ở lại; ràng buộc thay thế = "0 call site ngoài Khảo sát và ngoài
5 họ BA loại", đo bằng `inv.py` / `wj_inventory.py`.
