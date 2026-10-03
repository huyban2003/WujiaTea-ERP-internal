# F6 — Ma trận nghiệm thu · Controller Đặt hàng mỏng (`wujia_portal_sale`)

Phiên đầu nhánh sau cổng F (`docs/next-session-clusters-F.md` §1.C3 dòng `portal_sale`, prompt §3 "Prompt F6").
Mục tiêu: luật Đặt hàng rời controller về model; **không đổi response JSON, mã lỗi, câu chữ, redirect**.

- Chủ dự án chốt (25/09): (1) **một savepoint cho cả khối** tạo đơn + huỷ báo giá cũ + xoá giỏ, vá đơn mồ côi, chứng
  minh lỗi trên HEAD trước; (2) **đúng 3 phần** trong prompt, báo số dòng thật (`_cart_state`/giá để lại);
  (3) **gộp nợ `portal_base`** tự test một mình + 1 error DB trắng chỉ khung, làm sau phần sale.
- Đo: DB `wujia_f6` (bản sao giống UAT) · `wujia_f6base` (chỉ `portal_base`) · `wujia_f6frame` (chỉ `portal_layout`).
- Trước khi sửa: **không test nào gọi cart/add · update · step · remove · submit** ⇒ viết lưới đặc tả chạy trên HEAD trước.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `wujia_sale/models/product_product.py` | `_portal_qty_error(qty)` → `None` hoặc `(mã, ngưỡng)`: `MIN_QTY_NOT_CONFIGURED` · `QTY_BELOW_MIN` · `QTY_INVALID_STEP` · `QTY_ABOVE_MAX`. **Một nguồn** cho add · update · dòng giỏ · constraint |
| `wujia_sale/models/sale_order_line.py` | `_check_min_max_qty_portal` gọi helper; 3 câu ValidationError giữ nguyên chữ; min = 0 vẫn chặn vượt max như cũ |
| `wujia_portal_sale/models/wujia_portal_cart.py` | `PortalOrderError(code)` · `cart._get_for_store` · `cart._lock_lines` (NOWAIT trong savepoint) · `cart.action_submit_order(note)` · `line._portal_add` (nguyên SQL upsert + `LEAST` trần) · `line._portal_step` (nguyên `UPDATE … RETURNING`) · `line._portal_invalid_reason` |
| `wujia_portal_sale/controllers/portal.py` | Chỉ còn gate cửa hàng · parse input · dựng JSON/state · bus · map mã lỗi → redirect. Câu chữ lỗi số lượng gom vào `QTY_MESSAGES` (thay 6 f-string lặp). Bỏ `cr.rollback()` và import `psycopg2`/`pg_errors`/`UserError`/`ValidationError`/`plaintext2html`. **1047 → 862 dòng (−185)** |
| Submit chưa có giỏ | Controller dựng giỏ ảo `new()` (không ghi DB) để thứ tự mã lỗi giữ như cũ: `branch_locked` trước `CART_EMPTY` |
| `wujia_portal_sale/tests/test_f6_cart_submit.py` (mới, tag `wujia_f6`) | **21 test**: add/update/step/remove/submit + khoá response + constraint 3 câu + đơn mồ côi + khung giờ đóng giữa lúc tạo đơn |
| `scripts/qa/cart_race.py` (mới) | Đua 2 phiên thật: (a) cùng bấm giảm từ 4 → còn 2; (b) cùng gửi đơn → đúng 1 đơn, giỏ trống, **bắt buộc chạm khoá NOWAIT ≥ 1 vòng** |
| `wujia_portal_base/tests/common.py` (mới) + 7 file test | `need()` / `need_suite()` / `find_view()`: test quét nhiều module tự skip khi module chủ chưa cài — suite đủ vẫn chạy như cũ |
| `test_fra3_layer_guard.py` (base + layout) | `patch.object(…, create=True)` — trên DB chỉ khung, method nghiệp vụ không tồn tại nên patch cũ ném AttributeError |
| `wujia_sale/tests/__init__.py` | Bỏ `import test_wujia_mobile_sale` (anh Thái đã dời file sang `wujia_mobile_sale` ở `6202c44`) |
| Bump | `wujia_sale` 19.0.4.6.1 · `wujia_portal_sale` 19.0.4.24.1 (không đổi XML/CSS) |

## Ma trận nghiệm thu (prompt F6)

| # | Yêu cầu | Bằng chứng | KQ |
|---|---|---|---|
| 1 | Luật số lượng 1 nguồn cho add/update/step + constraint | `_portal_qty_error` là nơi duy nhất so min/bước/max; mutation M1 (bỏ kiểm bước) đỏ 6 test + 1 error, M6 (constraint bỏ max khi min=0) đỏ | ✅ |
| 2 | Mã lỗi + câu chữ giữ nguyên | Test so **từng chữ** `message` add/update + 3 câu constraint; M5 (đổi 1 câu) đỏ 2 subTest | ✅ |
| 3 | SQL upsert/step về model, giữ `LEAST` cap + invalidate | `_portal_add` / `_portal_step` giữ nguyên SQL; M2 (bỏ `LEAST`) đỏ `test_add_caps_at_max_with_warning`; M8 (step không xoá dòng dưới min) đỏ | ✅ |
| 4 | Submit về `action_submit_order()`: NOWAIT, khung giờ, huỷ báo giá cũ bằng write, tạo SO, xoá giỏ, raise mã lỗi | 21 test xanh; M4 (`action_cancel` thay `write`) đỏ; M7 (bỏ giỏ ảo) đỏ `test_submit_store_locked`; M9 (bỏ kiểm SP public) đỏ | ✅ |
| 5 | Controller map mã → redirect | PC `/portal/order/cart?error=<mã>`, mobile `ORDER_TIME_CLOSED` → `/portal/order/rejected`; test cả hai kênh | ✅ |
| 6 | Không đổi response JSON | Test khoá tập key từng route · HTML `/portal/order`, `/portal/order/cart`, `/portal/product/<id>`, `cart?error=…` + các fragment: HEAD vs mới **giống từng byte** (521.912 byte) | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Bộ test mới chạy trên **code HEAD**: xanh hết, chỉ đỏ test đơn mồ côi (HEAD để lại `sale.order(3974)`) = bằng chứng lỗi ẩn; sau F6 xanh 21/21 | ✅ |
| 8 | Test đồng thời | `cart_race.py` 5 vòng: HEAD và F6 cho **cùng JSON** — step 2/2/2/2/2, submit đúng 1 đơn/vòng, giỏ trống, `CART_IS_PROCESSING` 5/5 · M10 (bỏ NOWAIT) ⇒ `nowait_hits = 0` ⇒ **FAIL** | ✅ |
| 9 | Vá đơn mồ côi (chốt 1) | Ép `SO.create` lỗi sau khi insert: HEAD dư 1 đơn, F6 0 đơn; M3 (bỏ savepoint) đỏ đúng test này | ✅ |
| 10 | Nợ `portal_base` tự test một mình | DB chỉ `portal_base`: **39 failed + 82 error → 0 / 0** trên 274 test (117 dòng skip "chưa cài …") | ✅ |
| 11 | 1 error DB trắng chỉ khung | DB chỉ `portal_layout` (lệnh chuẩn `-i … --test-tags /wujia_portal_layout`): **225 test, 0 failed, 0 error** (E8c: 1 error) | ✅ |

## Số đo khác

- Suite portal đầy đủ 15 module trên `wujia_f6`: **822 test, 0 failed, 0 error** (E8c 801, +21).
- `wujia_sale` + `wujia_portal_sale`: 54 test, 0 failed, **1 error có sẵn** — `test_wujia_supply_demand_report` setUpClass
  "Quants cannot be created for consumables" (commit anh Thái `c64de50`; trước đây bị import hỏng che mất). Không sửa.
- `check_layers`: không thêm vi phạm nào dính `wujia_sale` / `wujia_portal_sale` (R3 `mobile_portal_*` và R7
  franchise→contract là của anh Thái, có từ trước) · `test_ownership` cross 0.
- Mutation **10/10** đỏ (M1–M9 qua test, M10 qua `cart_race.py`).

## Bài học

- **Server cũ chiếm port làm test HTTP đỏ hàng loạt**: lượt đầu DB chỉ khung ra 12 failed, tất cả là request chạy tư
  cách public / về `/web/login`. Nguyên nhân: một server của phiên E4b2 (thứ Bảy) vẫn nghe `127.0.0.1:8092`, HttpCase gửi
  request vào đó. Đổi port 8094 ⇒ 0 đỏ. Trước khi chạy test: `lsof -nP -iTCP:<port> -sTCP:LISTEN`.
- Cài mới DB có `--test-enable` import test của **mọi** module đã nạp ⇒ `wujia_franchise/tests/__init__.py` (import file
  đã xoá) làm ngã; cài không test trước rồi `-u X --test-tags`.
- Patch một method có thể không tồn tại (module nghiệp vụ tắt) phải `create=True`, không thì chính test ném AttributeError.

## LIMIT

- `_cart_state` + helper giá (WJ-ORD-024), `_order_window_context`, bus event, route catalog/detail **để nguyên** (chốt 2).
- Mã `ORDER_TIME_CLOSED` khi tạo đơn vẫn nhận ra bằng chuỗi "khung giờ" trong ValidationError của `portal_order_window`
  (như HEAD) — F7 tách order_window sẽ thay bằng mã có cấu trúc.
- Chưa deploy UAT.

## Bàn giao anh Thái

- Đã bỏ dòng `from . import test_wujia_mobile_sale` trong `wujia_sale/tests/__init__.py` (file đã dời ở `6202c44`).
- `test_wujia_supply_demand_report` error setUpClass (consumable không tạo được quant) — `c64de50`.
- `wujia_franchise/tests/__init__.py` vẫn import file đã xoá.
- `check_layers`: R3 `mobile_portal_*`, R7 franchise → contract.
