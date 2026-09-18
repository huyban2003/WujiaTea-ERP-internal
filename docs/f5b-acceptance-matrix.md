# F5b — bảng nghiệm thu

Tất cả đo trên máy, 18/09/2026. DB đo `wujia_f0` (cổng 8099), DB sạch `wujia_f5b` tạo mới.

| # | Phép đo | Ngưỡng | Kết quả | Đạt |
|---|---|---|---|---|
| 1 | **DB CHỈ cài `wujia_portal_layout`** (`wujia_f5b` tạo mới, `-i wujia_portal_layout --test-enable --test-tags /wujia_portal_layout`) | 0 failed 0 error | **0 failed, 0 error / 129 test** | ✅ |
| 2 | Suite 15 module `wujia_portal_*` trên `wujia_f0` kèm `-u` | ≥ 571, 0 failed 0 error | **0 failed, 0 error / 572 test** | ✅ |
| 3 | `scripts/ba_spec/b4_regression.py --base http://127.0.0.1:8099` | 286/286 | **286/286 PASS** | ✅ |
| 4 | `scripts/qa/check_layers.py` | R1–R5 đúng 1 vi phạm cũ · R6 = 0 | **1 vi phạm (`wujia_portal_order_window` thiếu `portal_base`, chờ F7)** · **R6 = 0** | ✅ |
| 5 | `nav_dump.py --diff` vs `docs/f5-baseline/` (anh.owner 46 route + em.hcm 28 route × 1440/390) | 0 lệch | chỉ lệch thuộc tính `id` của 2 `<li>` tiêu đề menu (`nav_header_main`, `nav_header_utils`) — **dư âm F5a, 0 pixel**; href/nhãn/thứ tự/active/badge **khớp tuyệt đối** | ✅ |
| 6 | `wj_measure.py --diff` vs `docs/f5-baseline/` | 0 lệch | **0 dòng lệch chiều cao · 0 ô mất record** (cả 2 tài khoản) | ✅ |
| 7 | Tổng assert trước/sau | không giảm | **1548 → 1549** (+1 test, +1 assert) · khung 711 → 261, file mới giữ 451 | ✅ |
| 8 | Mutation mọi guard đổi đường dẫn / đổi nội dung | phá → đỏ, hoàn tác → xanh | 5/5 (bảng dưới) | ✅ |
| 9 | Bump `version` mọi module bị đụng | 0 sót | `portal_layout` 51.0.8→51.0.9 · `portal_base` 7.17.6→7.17.7 · `portal_debt` 4.8.2→4.8.3 · `portal_exam` 5.15.3→5.15.4 (không sửa CSS ⇒ không đụng `?v=`) | ✅ |

## Mutation (bản sao `.bak`, `rm -rf __pycache__` sau khi hoàn tác — không `git checkout`)

| # | Phá gì | Guard được chứng minh | Phá | Hoàn tác |
|---|---|---|---|---|
| M1 | `portal_layout/_pc_components.css`: `.wj-pc-order-head .wj-card-header__lead` `flex: 0 1 auto` → `1 1 auto` | `portal_base/test_scan_d3_card_header.test_order_head_lead_shrinks_in_shared_css` (đường dẫn vừa sửa lại trỏ về `portal_layout`) | 1 failed / 33 | 0 failed / 33 |
| M2 | `portal_layout/_components.css`: `.wujia-mhome-kpi-value` `white-space: nowrap` → `normal` | `portal_layout/test_e1_home_kpi` (3) + `portal_base/test_home_kpi_e1` (1) | 1 failed / 4 | 0 failed / 4 |
| M3 | `portal_exam/portal_exam_wizard.js`: `.wj-card-header__title` → `…__titleX` | `portal_exam/test_card_header_d3d` (đường dẫn `_js()` viết lại) | 1 failed / 3 | 0 failed / 3 |
| M4 | `portal_debt/portal_debt.css`: `--wj-debt-radius: var(--wujia-card-radius)` → `12px` | `portal_debt/test_data_list_d5g` qua helper dùng chung `portal_base/tests/css_probe.py` | 1 failed / 8 | 0 failed / 8 |
| M5 | `portal_layout/views/wj_pagination.xml`: `aria-label="Phân trang"` → `"Phan trang"` | `portal_layout/test_e3_pagination` — chứng minh **fixture nội bộ** thật sự render template khung (không còn mượn `build_pager` của `portal_base`) | 1 failed / 38 | 0 failed / 38 |

Guard của màn Khảo sát (`test_handover_inspection.py`) **không mutation**: muốn phá phải sửa CSS trong
`wujia_portal_inspection` — code anh Thái, luật cụm F §0 cấm. Thay bằng kiểm dương: mọi đường dẫn tĩnh
trong test đã dời đều trỏ tới file có thật (14/14), và đọc file thiếu là **lỗi to tiếng** — chính lỗi đó
đã bắt được sai đường dẫn của M1 trong phiên này.

## Hai lỗi phiên này tự bắt được

1. `test_scan_d3_card_header` đọc `_pc_components.css` theo đường dẫn cũ ⇒ `FileNotFoundError` sau khi dời
   file sang `portal_base`. Sửa: trỏ thẳng về `wujia_portal_layout/static/assets/css/`.
2. **Khung chưa cài nổi một mình**: `portal_layout` kế thừa `http_routing.404` nhưng không khai
   `http_routing` trong `depends` — trên `wujia_f0` nó có sẵn nhờ module khác nên không ai thấy. Thêm
   `http_routing` vào `depends`. Và `test_c10_lang` giả định `vi_VN` đã bật sẵn ⇒ tự `_activate_lang('vi_VN')`
   trong `setUp`. Đây đúng là thứ phép đo quyết định sinh ra để bắt.
