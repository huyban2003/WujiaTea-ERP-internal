# check_layers — 31 module wujia_*, 2 vi phạm

L1 core           1  wujia_core
L2 nghiệp vụ      8  wujia_account, wujia_delivery, wujia_fleet, wujia_franchise, wujia_franchise_contract, wujia_franchise_inspection, wujia_franchise_operations, wujia_sale
L2 khung          2  wujia_mobile_core, wujia_portal_layout
L3a portal_base   1  wujia_portal_base
L3b ghép         18  wujia_mobile_franchise, wujia_mobile_franchise_contract, wujia_mobile_franchise_inspection, wujia_mobile_portal_info_request, wujia_mobile_sale, wujia_portal_debt, wujia_portal_delivery, wujia_portal_exam, wujia_portal_info_request, wujia_portal_inspection, wujia_portal_knowledge, wujia_portal_notification, wujia_portal_order_window, wujia_portal_purchase_history, wujia_portal_report, wujia_portal_return, wujia_portal_sale, wujia_portal_support

chưa phân tầng: wujia_metabase_connector

| Module | Depend | Luật | Chủ code | Ghi chú |
|---|---|---|---|---|
| `wujia_mobile_portal_info_request` | `wujia_portal_info_request` | R3 portal_* ↔ mobile_* không depend chéo | Dev portal |  |
| `wujia_portal_order_window` | `(thiếu) wujia_portal_base` | R4 mọi portal_<x> depend portal_base | Dev portal | chờ tách F7–F13 |

# R6 — khung wujia_portal_layout biết route Wujia: 0 vi phạm

# R7 — gọi method module không depend mà KHÔNG có guard: 2 vi phạm

| Module | File:dòng | Method | Chủ method |
|---|---|---|---|
| `wujia_franchise` | `custom/wujia_franchise/models/wujia_franchise_management.py`:366 | `_wj_ensure_contract` | `wujia_franchise_contract` |
| `wujia_franchise` | `custom/wujia_franchise/wizards/franchise_onboarding_wizard.py`:236 | `_wj_ensure_contract` | `wujia_franchise_contract` |
