# E9b — `WJ-FRANCHISE-004` · bảng nghiệm thu

**Nguồn chuẩn:** cột `Kết quả mong muốn` của issue, tab `5. Issue List` **dòng tuyệt đối 128** (STT 135),
đọc bằng `sheet_io.read_values('Issue List')` ngày 13/09/2026.

**Môi trường đo:** `wujia_tea_e9b` (clone `wujia_tea_mt4` — **có cài** `wujia_franchise_inspection` +
`wujia_portal_inspection`, giống UAT), cổng 8091/8092. Mốc đối chứng `wujia_tea_e9bbase` cùng gốc.

---

## Khối 1 — Store Master xem được hợp đồng

| Gạch đầu dòng BA | Bằng chứng | Kết |
|---|---|---|
| Xem số lượng + danh sách toàn bộ hợp đồng qua tab/smart button | `test_01_store_master_sees_all_contracts` (`contract_count`=2); smoke §2 smart button trả `domain [('franchise_id','=',575)]` | ✅ |
| Mở/tạo/sửa HĐ trong đúng Store, không nhập lại liên kết | `action_view_contracts` trả `context {'default_franchise_id': 575}`; tab `contracts_page` truyền `default_franchise_id` | ✅ |

## Khối 2 — Tạo hợp đồng

| Gạch đầu dòng BA | Bằng chứng | Kết |
|---|---|---|
| Nhập Store + Start + End hợp lệ → lưu được | smoke §1: wizard sinh `FC/2026/xxxx`, `contract_count`=1 | ✅ |
| End Date không nhỏ hơn Start Date | `test_03_end_before_start_rejected` (`assertRaisesRegex` + `flush_all`) · mutation **M6** đỏ đúng 1 test | ✅ |
| Không lưu được khoảng ngày chồng lấn với HĐ không Cancelled cùng Store | `test_04a/b/c/d` (4 ca lồng nhau) + `test_04e` (chạm biên 1 ngày) · smoke §3 · mutation **M4** đỏ | ✅ |
| HĐ lịch sử + HĐ tương lai không chồng vẫn tồn tại | `test_05_history_and_future_contracts_coexist` (expired + effective + draft trên 1 Store); smoke §4 ra đúng 3 trạng thái | ✅ |
| HĐ Cancelled không chặn khoảng ngày | `test_06_cancelled_contract_frees_its_range` · mutation **M5** đỏ | ✅ |
| Số HĐ cho nhập, trống ⇒ sequence | `test_02_contract_number_falls_back_to_sequence` (`FC/2026/…`) | ✅ |

## Khối 3 — Trạng thái theo ngày, không khoá Store

| Gạch đầu dòng BA | Bằng chứng | Kết |
|---|---|---|
| Hôm nay trong khoảng → Store hiện đúng HĐ hiện hành + ngày còn lại, read-only | `test_08_store_shows_current_contract_and_remaining_days` (`remaining_days`=30) · 2 field ngày là computed store readonly · mutation **M11** đỏ | ✅ |
| Qua End Date → hiển thị Expired/cảnh báo | `test_07c` · `test_09` (`_cron_check_expired` trả >0) · mutation **M2/M14** đỏ | ✅ |
| Store KHÔNG tự bị khoá / đóng / chặn đặt hàng | `test_09_expiry_never_locks_the_store`: sau cron `status='active'`, `portal_locked=False`. Gốc rễ đã sửa: `_cron_check_expired` **bỏ** `write({'status':'expired'})`, chỉ `message_post` · mutation **M13** (trả lại lệnh khoá) đỏ đúng test này | ✅ |
| Effective/Expired phản ánh ngày, không cần workflow phê duyệt | `state` là stored computed (`_compute_state`), nút *Confirm* đã gỡ; `is_cancelled` là đòn bẩy thủ công duy nhất · `test_07a/b/c/d` · mutation **M1/M2/M3** đỏ | ✅ |
| (phát sinh) Cron phải thật sự đổi trạng thái khi qua mốc ngày | `ir_cron_refresh_contract_state` mới — bản cũ gọi hàm **không có record cron nào** ⇒ code chết. `test_10_cron_flips_state_when_a_boundary_is_crossed` · mutation **M8** đỏ | ✅ |

## Khối 4 — Migration

| Gạch đầu dòng BA | Bằng chứng | Kết |
|---|---|---|
| Mỗi Store có ngày cũ → tạo **tối đa một** contract | Cài thật trên `wujia_tea_e9b`: *"migration created 3 contracts"*, 3/3 store giữ **đúng** ngày cũ `2026-05-16 → 2028-05-15` · `test_11` · mutation **M10** đỏ | ✅ |
| Chạy lại migration **không** tạo trùng | Gọi lần 2 qua shell: `before 3 / after 3` · `test_11` + `test_13` (kể cả khi xoá cờ `ir.config_parameter`) · mutation **M9** đỏ 3 test | ✅ |
| Sau migration chỉ model HĐ là nguồn nhập liệu, **không hai nơi** sửa Start/End | 2 field trên Store là computed store **readonly** (không có inverse ⇒ ORM không ghi được); form Store hiện read-only qua view inherit; wizard onboarding nay **tạo contract** thay vì ghi ngày (`test_17`, mutation **M15** đỏ); bootstrap CSV cũng đi qua `_wj_ensure_contract` | ✅ |
| Attachment dùng cơ chế chuẩn Odoo | `attachment_ids` = `ir.attachment` m2m + `widget="many2many_binary"`, `mail.thread` chatter; không DMS | ✅ |
| Không workflow phê duyệt / ký số / phụ lục / phí / notification nâng cao | 0 dòng code cho các mục này; nút Confirm bị **gỡ** chứ không thêm | ✅ |
| Không xoá cứng HĐ đã hiệu lực | `unlink()` chặn `effective`/`expired`, cho phép `draft` · `test_16` · mutation **M7** đỏ | ✅ |

**Tổng: 17/17 gạch đầu dòng đạt = 100% (ngưỡng ≥90%).**

---

## Số đo hồi quy

| Phép đo | Mốc (`wujia_tea_e9bbase`, cây mã chưa sửa) | Sau E9b (`wujia_tea_e9b`) |
|---|---|---|
| Test | **0 failed, 5 error / 501** | **0 failed, 6 error / 526** |
| Lỗi có sẵn | 3 × `wujia_franchise_inspection` setUpClass · 1 × `wujia_franchise_operations.test_10_revenue_import_wizard` · 1 × `wujia_sale.test_wujia_supply_demand_report` setUpClass | y hệt |
| Lỗi thứ 6 | — | `wujia_sale.TestWujiaOrderView.test_06` — **flake theo giờ**, chứng minh bằng run đối chứng trên chính DB mốc lúc 04:02 ra **cùng một đỏ** (khung giờ đặt hàng 10:00–04:00) |
| **Đỏ mới do E9b** | — | **0** |
| Test mới | — | **+25** (501 → 526) |
| Mutation | — | **15/15 đỏ đúng guard của nó** |
| 18 test onboarding S57 | xanh | xanh |

## Rehearsal nâng cấp (`wujia_tea_e9bup`)

Dựng lại đúng hình dạng UAT (tên HĐ `HD-*`, chưa có cột `is_cancelled`, 1 HĐ `state='cancelled'`,
`latest_version` lùi về `19.0.1.0.0`) rồi `-u`:

- HĐ `cancelled` **sống sót** → `is_cancelled=t`, state vẫn `cancelled` (nhờ `migrations/19.0.2.0.0/pre-migrate.py`).
- Hai HĐ còn lại recompute từ ngày → `effective`.
- Store chỉ còn HĐ bị huỷ → `current_contract_id` rỗng, 2 field ngày **về trống** (nhờ `post-migrate.py`).
- `status` / `portal_locked` của cả 3 store **không đổi**.

## Đo UAT chỉ đọc (13/09, XML-RPC)

- `wujia_franchise_contract` **đã cài sẵn bản `19.0.1.0.0`** (anh Thái) ⇒ deploy là **`-u`, KHÔNG phải `-i`**.
- 4 hợp đồng đã migrate (`HD-HCM-01`, `HD-HN-01`, `HD-HN-02`, `HD-TEST-134-0509-A`), cờ
  `wujia_franchise_contract.legacy_migrated = True`.
- **0 cửa hàng đang kẹt `status='expired'`** ⇒ không có store nào bị khoá oan, không cần sửa dữ liệu.
- Cron `Wujia: Auto-expire franchise contract` **đang bật** với mã cũ ⇒ tới `2028-05-15` sẽ khoá 3 cửa hàng.
  Bản này vá đúng chỗ đó.

## Defer

- `wujia_portal_inspection`, `wujia_franchise_inspection`: **không đụng** (luật §7). Cụm E9b không giao cắt.
- `wujia_franchise_operations` (anh Thái, thiếu depend + wizard `ValueError`): không sửa hộ, đã báo cáo 11/09.
