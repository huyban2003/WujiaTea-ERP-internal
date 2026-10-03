# F7 — Ma trận nghiệm thu · Pilot tách `order_window` (ADR-027 §Quy trình tách)

Phiên F7 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F7"). Mục tiêu: chuyển nghiệp vụ khung giờ đặt
hàng từ `wujia_portal_order_window` sang module nghiệp vụ `wujia_order_window` **mà không đổi một bản ghi nào ngoài cột
chủ sở hữu**, và chuẩn hoá quy trình cho F8–F13.

- Chủ dự án chốt (25/09): (1) module cũ để **vỏ rỗng** chỉ depend `wujia_order_window`, deploy xong đo 0 xmlid thì
  Uninstall trên Apps, FR-P xoá thư mục; (2) **vá luôn nợ F6** — bắt lỗi khung giờ theo lớp, không dò chữ "khung giờ".
- Đo trên DB copy của `wujia_f6` (giống UAT, có Khảo sát): `wujia_f7` (seed 3 khung giờ + 3 tham số + bật `vi_VN`),
  `wujia_f7u` (như trên, deploy chỉ `-u`), `wujia_f7r2` (bản sạch, đo lại bằng công cụ đã vá), `wujia_f7m` (mutation hook),
  `wujia_f7alone` (DB trắng chỉ cài module mới). Không đụng `wujia_tea_19`.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_order_window/` (mới, L2 nghiệp vụ, depend `wujia_sale`) | `git mv` nguyên models/views/security/i18n từ module cũ. Manifest `19.0.1.0.0` + `pre_init_hook`. `<app name>` Settings đổi theo tên module. `.po` đổi tiền tố xmlid `wujia_portal_order_window.` → `wujia_order_window.` |
| `wujia_order_window/hooks.py` | `migrate_ownership(cr, old, new, names=None, models=None)` — đổi chủ `ir_model_data` **và** `ir_model_constraint`/`ir_model_relation` (cột `module` là FK, không nằm trong `ir_model_data`). Dùng lại cho F8+ |
| `wujia_order_window/models/sale_order.py` | Lớp lỗi `OrderWindowClosed(ValidationError)`; câu chữ giữ nguyên |
| `wujia_order_window/tests/` (mới) | 10 test: khu vực ưu tiên, fallback chung, qua nửa đêm, nhiều khung, khung lưu trữ bị bỏ qua, tắt giới hạn, cờ "chưa cấu hình", `_next_order_window` hôm nay/ngày mai, 2 ràng buộc, chặn đơn portal, 0 xmlid còn ở module cũ, hook đổi đúng phần được giao. Trước F7: **0 test** tạo `wujia.order.window` |
| `wujia_portal_order_window` | Vỏ: `__init__.py` trống, `data: []`, depend `wujia_order_window`, `19.0.3.0.0` |
| `wujia_portal_sale` | Depend `wujia_order_window`; `action_submit_order` bắt `OrderWindowClosed` thay cho `'khung giờ' in str(e)`; +1 test; `19.0.4.25.0` |
| `wujia_portal_base` | Chỉ sửa chú thích tên module (guard `hasattr` giữ nguyên, **không** thêm depend — ADR-027 cấm) |
| `scripts/qa/split_snapshot.py` (mới) | Chụp trước/sau + `--diff --rename old=new` |
| `scripts/qa/check_layers.py` | `wujia_order_window` = L2; `DEPRECATED` cho vỏ chờ gỡ; bỏ khỏi `PENDING_SPLIT`; nhãn chủ code `wujia_mobile_*` = Thái |
| `scripts/reseed_full.sh/.ps1`, `controller_spec_tex.py` | Đổi tên module |
| `docs/chapters/74-adr027-module-layering.tex` | §Quy trình tách viết lại theo thực tế + số đo pilot; dòng P2 lộ trình |

## Ma trận nghiệm thu (prompt F7)

| # | Yêu cầu | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_order_window` nhận model + kế thừa `sale.order`/`res.config.settings`, view/menu/ACL | `git mv`; DB trắng chỉ `-i wujia_order_window` (kéo `wujia_sale`/`franchise`/`core`) → **10 test, 0 failed, 0 error** | ✅ |
| 2 | `pre_init_hook` đổi chủ `ir_model_data` | Log: `{'ir_model_data': 36, 'ir_model_constraint': 6, 'ir_model_relation': 0}`; `test_old_module_owns_nothing` | ✅ |
| 3 | Module cũ rỗng depend module mới, portal_sale đổi depend | Manifest; `check_layers` R4 của order_window **hết** (3 → 2 vi phạm, 2 còn lại là R3 `wujia_mobile_portal_*` của anh Thái) | ✅ |
| 4 | Đo TRƯỚC/SAU: record, xmlid, menu/action, ACL, cấu hình khung giờ giống hệt | `split_snapshot --diff --rename`: **42 dòng đổi chủ, 1 lệch thật** = view Settings đổi `name="wujia_portal_order_window"` → `wujia_order_window` (+ `_block`), đã `diff` arch: đúng 2 thuộc tính đó. Số dòng + md5 bảng, 3 tham số `wujia_portal.*`, 22 nhãn field (en + vi), 2 ACL, 2 menu, action, 7 ràng buộc Postgres: **0 lệch** | ✅ |
| 5 | Lệnh deploy 1 dòng | `-i wujia_order_window -u wujia_portal_order_window,wujia_portal_sale` → 0 ERROR. Chỉ `-u wujia_portal_order_window` cũng tự cài module mới, cùng kết quả (đo `wujia_f7u`) | ✅ |
| 6 | Gỡ vỏ an toàn (chốt 1) | `button_immediate_uninstall` trên `wujia_f7` và `wujia_f7r2` → chụp lần ba **0 lệch** | ✅ |
| 7 | Vá nợ F6 (chốt 2) | `OrderWindowClosed` → `ORDER_TIME_CLOSED`; `ValidationError('Sai khung giờ giao')` → `ORDER_CREATE_FAILED` (trước đây bị nhận nhầm là khung giờ) | ✅ |
| 8 | Test cũ xanh | Suite 15 module `wujia_portal_*` + `wujia_order_window`, kèm `-u`: **833 test, 0 failed, 0 error** (F6: 822 + 10 + 1). Run đối chứng: 822 đo ở F6 trên chính HEAD `df385d1` | ✅ |
| 9 | Không đổi giao diện | Server HEAD (`git archive`, DB `wujia_f6`) ‖ server F7 (`wujia_f7r2`), cùng `anh.owner`: `/portal`, `/portal/order`, `/portal/order/cart`, `…?error=ORDER_TIME_CLOSED`, `/portal/order/rejected?…` **5/5 giống từng byte** (chuẩn hoá hash asset + `registry_hash`); bundle CSS 617.029 byte + JS 2.008.139 byte **cùng md5** | ✅ |
| 10 | Quy trình vào chapter 74 | §Quy trình tách: 9 bước + danh mục đo + số đo pilot + 3 bẫy | ✅ |

## Mutation (5/5 đỏ)

| # | Phá | Kết quả |
|---|---|---|
| M1 | Cart quay về dò chữ `'khung giờ' in str(e)` | 2 failed (`test_submit_create_error_mapped_by_class_not_text`) |
| M2 | `sale.order.create` raise `ValidationError` thường | 1 failed + 1 error (`test_submit_window_closes_during_create`, `test_portal_order_blocked_outside_window`) |
| M3 | Hook bỏ qua `names` (luôn chuyển tất cả) | 1 failed (`test_migrate_moves_only_named_rows_and_models`) |
| M4 | `any()` → `all()` khi xét nhiều khung của khu vực | 4 failed + 1 error |
| M5 | Hook không đổi chủ `ir_model_constraint` (DB `wujia_f7m`) | `split_snapshot --diff` báo **7 lệch thật**: 2 CHECK trùng tên (một dòng mỗi module) + 6 dòng mồ côi sau khi gỡ vỏ |

## Bài học (đã ghi vào chapter 74)

- **Hook khuôn không còn được nối.** `wujia_franchise_inspection/hooks.py` vẫn nằm đó nhưng `pre_init_hook` bị gỡ khỏi
  manifest ở `ec6d380` (16/09). Nếu chỉ chép file thì hook không chạy mà không báo gì.
- **`ir_model_constraint` không nằm trong `ir_model_data`.** Khuôn Khảo sát bỏ sót. Plan dự đoán "gỡ vỏ sẽ DROP
  CHECK", nhưng đo cho thấy **không**: Odoo gỡ theo xmlid, và `unlink` tự bỏ qua khi còn dòng cùng tên. Hậu quả thật là dòng
  trùng + dòng mồ côi (M5).
- **Công cụ đo từng có điểm mù**: bản đầu khoá `cons` theo tên nên 2 dòng trùng tên gộp làm một. M5 lộ ra, nay gom
  thành danh sách theo tên. Tiền lệ "Pass rỗng" lần thứ n: phải phá thử thì mới biết công cụ đo có mắt.
- **`.po` mang tên module trong xmlid** (`…:wujia_portal_order_window.field_…`). Không đổi thì bản dịch không gắn được vào
  xmlid mới mà không có log. Snapshot so nhãn `vi_VN` để bắt.
- Module cũ giữ cả xmlid field trên model **kế thừa**, kể cả `display_name`/`id` ⇒ tách một phần (F8+) phải liệt kê cả nhóm này.
- zsh không tách từ trong biến (`$SNAP` chứa lệnh có tham số) ⇒ dùng hàm shell.

## LIMIT

- Vỏ `wujia_portal_order_window` còn trong repo tới FR-P (chốt 1). Settings vẫn hiện tiêu đề "Wujia Portal Order Window"
  và menu "Wujia Portal" — giữ nguyên chữ, chỉ đổi chủ.
- Chưa deploy UAT, chưa commit.

## Hướng dẫn deploy UAT (khi được yêu cầu)

1. `git pull` → `odoo-bin … -i wujia_order_window -u wujia_portal_order_window,wujia_portal_sale --stop-after-init` → restart.
2. Đo chỉ-đọc: version 3 module; `ir_model_data` của `wujia_portal_order_window` = **0**; menu *Bán hàng › Cấu hình › Wujia
   Portal › Khung giờ đặt hàng* mở được, số khung giờ như trước; 3 tham số `wujia_portal.*` như trước.
3. Apps → *Wujia Portal Order Window (vỏ chờ gỡ)* → Uninstall (màn xác nhận phải liệt kê **chỉ** module đó).

## Bàn giao anh Thái

- `wujia_franchise_inspection/hooks.py` không còn được gọi (gỡ ở `ec6d380`). Đã cài trên mọi DB nên không hại, nhưng nếu cài
  mới trên DB từng có Khảo sát trong `wujia_franchise` thì hook không chạy. Nên xoá file hoặc nối lại.
- Khuôn đó cũng không đổi chủ `ir_model_constraint` của model Khảo sát: đo `wujia_f6` còn **46 dòng** ghi `wujia_franchise`
  (4 dòng `wujia_franchise_inspection`). Không hại khi không gỡ `wujia_franchise`.
