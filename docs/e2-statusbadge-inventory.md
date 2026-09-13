# Kiểm kê StatusBadge — `UI-STATUSBADGE-001` / `CMP-SB-001`

Đếm bằng **cấu trúc** (`lxml`, mọi thuộc tính `class` / `t-attf-class` / `t-att-class`),
không grep tên lớp trần. Script: scratchpad `e2/inv.py`. Mốc: 13/09/2026.

| Mốc | Call site họ cũ | Call site component `.wj-status-badge` |
|---|---|---|
| Trước E2a | **114** (8 họ / 16 file) | 0 |
| Sau E2a | **75** | **37** |
| Sau E2b | **38** | **74** (11 module) |

Con số "77 / ≈56" ở bản trước là đếm theo CHUỖI (gộp cả dict literal trong controller và
tên lớp con BEM). Đếm lại theo PHẦN TỬ mang class thì mốc sau E2a là **75**, và trong đó
chỉ **37** là StatusBadge thật — phần còn lại là họ BA loại hoặc Khảo sát.

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

## 3. E2b đã làm — migrate 37, còn 38

| Module | Đã migrate | Còn họ cũ | Ghi chú |
|---|---|---|---|
| wujia_portal_exam | 11 | 0 | gỡ 5 override ép dáng; ô bảng PC hết cắt badge |
| wujia_portal_debt | 8 | 0 | xoá hẳn hai họ `wj-debt-badge` / `wj-debt-pc-badge` |
| wujia_portal_return | 8 | 2 | 2 còn lại = phương án xử lý (Category, BA loại) |
| wujia_portal_notification | 6 | 8 | 8 còn lại = ưu tiên · loại · đếm · đính kèm (BA loại) |
| wujia_portal_support | 2 | 1 | 1 còn lại = chip ưu tiên (BA loại) |
| wujia_portal_info_request | 2 | 2 | 2 còn lại = chip ưu tiên (BA loại) |
| **wujia_portal_inspection** | 0 | **9** | 🚫 **defer** — module khảo sát, luật 08/09 cấm đụng |
| wujia_portal_knowledge | 0 | 8 | toàn bộ là Category/Alert — BA loại, không đụng |
| wujia_portal_base | 0 | 6 | loại thông báo · mã cửa hàng · Role — BA loại |
| wujia_portal_layout | 0 | 2 | RoleBadge trong `profile_page` — BA loại |

⇒ **38 call site họ cũ còn lại = 9 defer (Khảo sát) + 29 BA loại**. Không còn StatusBadge
thật nào nằm ngoài component ⇒ điều kiện đóng `UI-STATUSBADGE-001` đã đủ.

## 4. LIMIT
`.wj-pc-badge` **không xoá được**: `wujia_portal_inspection` dùng 9 chỗ (+ `wujia_franchise_inspection`),
thuộc phạm vi cấm đụng. Rule CSS cũ ở lại; ràng buộc thay thế = "0 call site ngoài Khảo sát và ngoài
5 họ BA loại", đo bằng `inv.py` / `wj_inventory.py`.
