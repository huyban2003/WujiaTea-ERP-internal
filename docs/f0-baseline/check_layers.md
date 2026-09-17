# check_layers — 25 module wujia_*, 4 vi phạm

L1 core           1  wujia_core
L2 nghiệp vụ      8  wujia_account, wujia_delivery, wujia_fleet, wujia_franchise, wujia_franchise_contract, wujia_franchise_inspection, wujia_franchise_operations, wujia_sale
L2 khung          2  wujia_mobile_core, wujia_portal_layout
L3a portal_base   1  wujia_portal_base
L3b ghép         13  wujia_portal_debt, wujia_portal_delivery, wujia_portal_exam, wujia_portal_info_request, wujia_portal_inspection, wujia_portal_knowledge, wujia_portal_notification, wujia_portal_order_window, wujia_portal_purchase_history, wujia_portal_report, wujia_portal_return, wujia_portal_sale, wujia_portal_support

| Module | Depend | Luật | Chủ code | Ghi chú |
|---|---|---|---|---|
| `wujia_franchise` | `wujia_mobile_core` | R1 nghiệp vụ/core không depend khung hay module ghép | Thái | mục D, chờ chốt với anh Thái |
| `wujia_franchise_inspection` | `wujia_mobile_core` | R1 nghiệp vụ/core không depend khung hay module ghép | Thái | mục D, chờ chốt với anh Thái |
| `wujia_portal_order_window` | `(thiếu) wujia_portal_base` | R4 mọi portal_<x> depend portal_base | Dev portal | chờ tách F7–F13 |
| `wujia_sale` | `wujia_mobile_core` | R1 nghiệp vụ/core không depend khung hay module ghép | Thái | mục D, chờ chốt với anh Thái |
