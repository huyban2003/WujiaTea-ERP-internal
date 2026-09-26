# F13 — Ma trận nghiệm thu · Tách `return` → `wujia_return` + controller mỏng

Phiên F13 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13", phân hệ "return"), gộp F13a (chuyển
model/quyền) + F13b (controller mỏng) một phiên. **Phân hệ cuối của khối A** (ADR-027): xong ⇒ `PENDING_SPLIT` rỗng ⇒
mở ★FR-A. Tách một phần như F8–F12: nghiệp vụ sang module L2 mới; 3 QWeb portal + 2 mục nav + controller ở lại
`wujia_portal_return`. Home ở lại `wujia_portal_base` (ADR-027: không tách Home) — chỉ đổi sang gọi luật của model.

- Chủ dự án chốt (26/09): tên module **`wujia_return`** · giữ nguyên `_name` mọi model · gộp a+b, **commit + push
  `main`**, deploy để chủ dự án · A2 làm "chuẩn nhất": luật trạng thái về model + **một bảng nhãn duy nhất** (lấy theo
  bảng PC hiện tại; Dev tự chốt chữ, màu giữ nguyên, báo BA sau).
- UAT đo chỉ-đọc trước khi làm (RPC): F12 đã deploy (`wujia_exam 19.0.1.0.0`), `wujia_portal_return 19.0.3.11.0`;
  14 phiếu (duyệt 5 · hoàn tất 2 · nháp 3 · từ chối 2 · đã gửi 2) · 5 loại lỗi · 0 allocation; 236 xmlid; nhóm Quản lý
  1 người / Người dùng 0. 2 sequence noupdate (`RTN/%(y)s/` số kế **5** · `CA/%(y)s/` **1**): XML không có
  `number_next` ⇒ `-i` không reset. 5 loại lỗi noupdate khớp XML ⇒ không có câu hỏi noupdate.
- Không module mobile nào của anh Thái ref `wujia_portal_return` ⇒ **không sửa code Thái** (khác F8/F12).
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_f13base` (giống UAT, code HEAD `020c5f2`):
  - Seed bằng code HEAD (`scratchpad/f13/seed_f13.py`): phiếu đủ trạng thái + bù một phần, có/không allocation, SO bù
    huỷ, dòng đơn accumulate/exact/tỉ lệ sai/chưa cấu hình, đơn quá 10 ngày, đơn cửa hàng khác; `anh.owner` (1 cửa
    hàng) và `dung.multi` (3 cửa hàng).
  - `wujia_f13`: chụp trước → deploy F13 → chụp sau · worktree HEAD `scratchpad/f13/head` chạy cùng seed để so HTML.
  - `wujia_f13suite`: suite · `wujia_f13ctl`: test portal mới trên code HEAD · `wujia_f13alone`: DB trắng ·
    `wujia_f13t`: mutation.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_return/` (mới, L2, depend `mail, wujia_sale, wujia_franchise`) | `git mv` 6 file model (request, issue type, allocation + kế thừa `sale.order`/`stock.picking`/`product.product`), wizard xử lý bù (3 model), 2 nhóm + privilege, ACL, rule, 2 sequence, 5 loại lỗi, 4 view backend + menu, `test_compensation_wizard_d1`. ACL/menu/`groups=` arch đổi sang **`wujia_return.`** đủ tiền tố (bài học F12). `.po` 239 mục. Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_return/hooks.py` | `imd_names(MODELS, extra=[privilege, 2 nhóm, 6 menu, 5 loại lỗi])` + `migrate_ownership`; MODELS = 6 model riêng + 3 model kế thừa |
| Model `wujia.return.request` | Hằng số (10 ngày, MIME, số/MB ảnh–video, `OPEN_STATES`) về model. `_portal_scope_domain` · `_portal_open_domain` · `_portal_recent_domain` · `_portal_status_key` (8 khoá, `partial` = đang xử lý + bù một phần, `reviewing` gộp `processing`) · `_portal_status_domain` · `_portal_eligible_order_domain` · `_portal_check_product_config` · `_portal_check_evidence(images, videos, require_min)` nhận `(size, mime)` · `_portal_prepare_vals` · **`create_from_portal`** (kiểm → tạo → `attach(rr)` → gửi, **trong savepoint**, thay `unlink` thủ công) · `_portal_compensation_view` (số, %, huỷ hết, đơn bù). Giữ nguyên mọi câu báo lỗi |
| `wujia_portal_return` | Còn controller + 3 QWeb + 2 mục nav + CSS/JS + `migrations/` cũ. Depend `wujia_portal_base, wujia_return`. `19.0.4.0.0`. `.po` 94 mục (333 = 94 + 239) |
| Controller | **588 → 357 dòng**. Còn: đọc stream + sniff MIME thật (`_sniff`), lưu file qua `attach_files_to_record` (callback chạy trong savepoint của model), nhãn, render. Hết: `STATE_LABELS`, `state_filter_domain`, ghép domain 10 ngày/cửa hàng, kiểm cấu hình bù, kiểm minh chứng, parse payload, `create`/`unlink` |
| A2 — bảng nhãn một nguồn | `RETURN_STATUS_LABELS` ở `wujia_portal_base/controllers/utils.py` (base cấm depend `portal_*`; Home + portal_return cùng dùng) + `return_status_label(rr)` có guard `hasattr`. Xoá `MOBILE_RETURN_BADGES` (base), `STATE_LABELS` (portal), dict nhãn inline trong `portal_home.xml`. `FILTER_OPTIONS` sinh từ bảng |
| Home (`portal_base` `19.0.7.28.0`) | `_safe_count`/`_safe_list` gọi `_portal_open_domain`/`_portal_recent_domain` qua `hasattr` (khuôn F9/F11); PC + mobile gọi `wj_return_status(rr)` |
| Test | `wujia_return`: `test_compensation_rules` (đơn hợp lệ, cấu hình bù, đơn bù) + `test_portal_rules` (7: luật cấm sửa đầu vào, minh chứng, tạo nháp/gửi, **rollback cả phiếu khi gửi lỗi**, 8 khoá trạng thái, domain lọc = khoá, domain Home) + `test_split_ownership` (3, gồm nút Quản lý hiện trong arch). Fixture `common.py`. Portal: `test_return_controller` viết lại theo model + `test_portal_return_f13` 5 HttpCase (8 bộ lọc, gửi → 303, lỗi render form + không tạo gì, cửa hàng khác, Home cùng nhãn danh sách). Base: 2 test quét badge theo bảng mới |
| `check_layers.py`, `deploy.yml`, `reseed_full.sh/.ps1` | `wujia_return` = L2, **`PENDING_SPLIT = set()`**; thêm vào `-i/-u` và reseed |

## Đổi chữ có chủ đích (báo BA)

Chỉ **Home mobile** đổi chữ; màu badge giữ nguyên. PC Home, danh sách, bộ lọc, chi tiết: giữ nguyên từng byte.

| Trạng thái | Home mobile trước | Sau (= bảng PC) |
|---|---|---|
| `submitted` | Chờ xử lý | **Đã gửi** |
| `reviewing`/`processing` | Đang xét / Đang xử lý | **Đang xử lý** |
| `done` | Hoàn thành | **Hoàn tất** |
| đang xử lý + bù một phần | Đang xử lý | **Đang bù một phần** |

Câu hỏi BA (không sửa): KPI "đổi trả đang mở" trên Home **không tính `reviewing`** (luật cũ, giữ nguyên) — có nên tính?

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_return` nhận model, view backend, menu, **group**, rule, sequence, i18n phần model | `git mv`. DB trắng chỉ `wujia_core, wujia_franchise, wujia_sale, wujia_return` (cài rồi `-u --test-tags /wujia_return`): **0 đỏ, 0 ERROR** | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Module mới 230 xmlid (150 field · 26 selection · 11 ACL · 9 model · 7 view · 6 menu · 5 loại lỗi · 4 constraint · 4 action · 2 nhóm · 2 inherit · 2 sequence · privilege · rule). Module cũ còn đúng 5 view: `portal_return_{list,form,detail}`, `layout_sidenav_return`, `mobile_bottomnav_return` | ✅ |
| 3 | Đo trước/sau: record, **user trong group**, sequence, menu/action, rule | `split_snapshot --diff --rename`: **287 dòng đổi chủ**. Bản ghi request/allocation md5 giống · 2 sequence **kèm `last_value`** giữ · người trong 2 nhóm giữ. 3 lệch có giải trình: arch form phiếu + form sản phẩm (tên module trong `groups=`, cố ý) · bảng loại lỗi chỉ khác `write_date` (hook ghi lại noupdate) | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_return.*` ở module khác | Không module nào ngoài portal ref phần nghiệp vụ; 3 QWeb được ref ở lại portal. Test `portal_base` đổi import bảng nhãn. Mobile Thái: 0 ref | ✅ |
| 5 | Lượt mỏng: luật controller về model | Luật 10 ngày, phạm vi cửa hàng, cấu hình bù, minh chứng, tạo + gửi phiếu, trạng thái/lọc, tiến độ bù đều ở model. Controller không còn `create`/`unlink`/`timedelta`/domain tự ghép; `write` duy nhất là gắn attachment vừa lưu (tầng HTTP, trong savepoint) | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD ‖ F13, cùng seed, 4 phiên, chuẩn hoá hash asset + csrf: **298/306 giống từng byte, chạy 2 lần**; 8 khác đều là nhãn Home mobile ở bảng trên (cùng class). Phủ: danh sách (trang, limit rác, tìm, ngày ngược/rác, 8 bộ lọc + `reviewing` + rác), form, 20 chi tiết (gồm cửa hàng khác, không tồn tại), 5 attachment (gồm chéo cửa hàng), **28 nhánh gửi phiếu × 2 user** (thành công nháp/gửi/video/PNG/exact; thiếu ảnh, quá ảnh/MB/tổng, sai MIME, đơn quá hạn/cửa hàng khác/không tồn tại, dòng lệch đơn, SL ≤0/rác, cấu hình bù sai, giờ mở hàng rác…) + đọc lại sau ghi. DB sau ghi giống hệt (phiếu, attachment, bảng rel, chatter, sequence) | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Focused `wujia_return,wujia_portal_return,wujia_portal_base`: **355, 0 đỏ**. Suite 13 `wujia_portal_*` + 7 module tách: **912, 0 đỏ, 0 ERROR**. Đối chứng: 5 HttpCase portal mới trên code HEAD ⇒ 4 xanh, chỉ test nhãn Home đỏ (đúng phần đổi có chủ đích) | ✅ |
| 8 | `check_layers` | **0 vi phạm tầng**, `PENDING_SPLIT` rỗng; R7 giữ 2 (anh Thái, `wujia_franchise`) | ✅ |
| 9 | Deploy một lệnh | DB giống UAT: `-i wujia_return -u wujia_portal_return,wujia_portal_base` → exit 0, 0 ERROR | ✅ |

Thay đổi hành vi nhỏ có chủ đích: bắt lỗi chung khi tạo phiếu giờ bao cả bước đính kèm/gửi (trong savepoint) ⇒ lỗi
bất ngờ ở bước đó cũng trả form + rollback cả phiếu, thay vì phiếu nháp mồ côi.

## Mutation

M0 (không đổi) = 0 đỏ / 81 test.

| # | Phá | Kết quả (test `wujia_return` + `wujia_portal_return`) |
|---|---|---|
| M1 | Bỏ hạn 10 ngày của đơn gốc | 2 đỏ |
| M2 | Bỏ kiểm cấu hình chính sách bù | 4 đỏ |
| M3 | Bỏ tối thiểu ảnh khi gửi | 3 đỏ |
| M4 | `create_from_portal` bỏ savepoint | 1 đỏ (`test_failed_submit_rolls_back_whole_request`) |
| M5 | Bỏ phạm vi cửa hàng | 5 đỏ |
| M6 | Bù một phần hiện như đang xử lý | 3 đỏ |
| M7 | KPI đang mở tính cả nháp | 1 đỏ |

## Playwright (không gửi phiếu)

PC 1440 + mobile 390, 16 màn (danh sách, lọc bù một phần/đã gửi, form tạo, chi tiết bù một phần/hoàn tất/đã gửi, Home):
0 tràn ngang; lỗi duy nhất 404 `/app-assets/data/locales/en.json` (HEAD cũng vậy). Home mobile hiện "Đã gửi".

## Còn mở

1. Chờ deploy UAT (chủ dự án). Lệnh: `-i wujia_return -u wujia_portal_return,wujia_portal_base` (không đụng module
   Thái). Sau deploy đo chỉ-đọc: `wujia_return 19.0.1.0.0` · `portal_return 19.0.4.0.0` · `portal_base 19.0.7.28.0`;
   portal còn 5 view; số kế `RTN` **5** · `CA` **1**; nhóm Quản lý 1 người; 14 phiếu; `/portal/return` 200.
2. Báo BA: đổi chữ Home mobile (bảng trên) + câu hỏi `reviewing` trong KPI đang mở.
3. `migrations/` cũ của portal để nguyên (đã chạy trên UAT).
4. Kế tiếp: **★FR-A** — review lại toàn khối A (F7–F13), không làm tính năng.

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_f13base wujia_f13      # + cp filestore; seed_f13.py bằng code HEAD
python3 $W/scripts/qa/split_snapshot.py --db wujia_f13 ... -o before.json
cd $W/odoo19 && $PY odoo-bin -c <conf> -d wujia_f13 --stop-after-init \
  -i wujia_return -u wujia_portal_return,wujia_portal_base                                  # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_return=wujia_return                   # 287 đổi chủ, 3 lệch
$PY odoo-bin ... --stop-after-init --test-enable --test-tags /wujia_return,/wujia_portal_return,/wujia_portal_base \
  -u wujia_return,wujia_portal_return,wujia_portal_base                                     # 355/0
python3 $W/scripts/qa/check_layers.py                                                        # 0 vi phạm
```
So HTML: `scratchpad/f13/cmp_http.py` (8097 HEAD ‖ 8098 F13). Mutation: `scratchpad/f13/mutate.py`.
