# ★FR-P — Review pilot F7 (tách `order_window`) trước khi nhân quy trình F8–F13

*Phiên 25–26/09/2026 · Mac · DB copy `wujia_frp` (= `wujia_f7r2`, đã gỡ vỏ) port 8097 · `wujia_frp_alone` (trắng) 8098 ·
`wujia_frp_trial` (thử tách một phần) · UAT `wujia_tea_19`: **1 lời gọi ghi duy nhất** = Uninstall vỏ (chủ dự án duyệt Y).*

Khối được duyệt: F7 `6b2938d` (pilot) + nợ F6 vá kèm. Trọng tâm chủ dự án đặt thêm: **tách có đúng 100% luật tầng
nghiệp vụ – portal – mobile (ADR-027) không**.

## 1. Kết luận

**ĐẠT — nhân quy trình sang F8 được**, với 3 điều kiện đã chốt trong phiên:
1. Hook đổi chủ dùng chung nằm ở L1 (`wujia_core/tools/module_split.py`), có `imd_names` suy danh sách xmlid theo model —
   tách MỘT PHẦN không còn phải liệt kê tay 75 xmlid.
2. Phần mobile của anh Thái **không thuộc phạm vi review** (chốt chủ dự án 26/09): dòng `ref()` xmlid `wujia_portal_<x>.*` bên `wujia_mobile_portal_*` là mục **bàn giao**, không chặn F8 (§6 nợ 1).
3. Vỏ `wujia_portal_order_window` đã gỡ trên UAT và xoá khỏi repo; `deploy.yml` đã đổi tên (F7 bỏ sót).

Tuân thủ tầng của `wujia_order_window` (L2): **0 vi phạm** — bảng §3.

## 2. Bảng Pass/Fail

| # | Mục (prompt FR-P) | Kỳ vọng | Đo | KQ |
|---|---|---|---|---|
| 1a | UAT trước gỡ (chỉ đọc) | vỏ installed, 0 xmlid, 0 ràng buộc, 0 module depend | `id 697` installed · imd 0 · cons 0 · dependents 0 · module mới 36 xmlid + 6 cons | ✅ |
| 1b | Gỡ vỏ trên UAT | 1 lời gọi `button_immediate_uninstall([697])` | 6.4 s, trả `act_url /odoo` như nút Apps | ✅ |
| 1c | UAT sau gỡ (chỉ đọc) so `uat_after.json` (F7) | chỉ `state` vỏ đổi | vỏ `uninstalled` · imd 36/0 · 6 cons 0 trùng 0 vỏ · `ir_model_relation` vỏ 0 · 2 khung giờ y hệt · 3 tham số y hệt · 2 menu (action 554) · 2 ACL · nhãn vi 15 field + 3 settings · form Settings có `name="wujia_order_window"`, không còn app cũ · list 528 / form 1071 ký tự · `default_get` 10.0/4.0/True | ✅ |
| 2a | Xoá thư mục vỏ + `DEPRECATED` | `check_layers` 0 vi phạm phía Dev | 34 module · **2 vi phạm, đều R3 `wujia_mobile_portal_*` (Thái)** · R6 0 · R7 2 (`_wj_ensure_contract`, Thái) | ✅ |
| 2b | Grep tên cũ toàn repo | còn đâu phải có lý do | bảng §4 | ✅ |
| 2c | `deploy.yml` | không còn `-i`/`-u` vỏ | 2 chỗ → `wujia_order_window` (**F7 bỏ sót**, FR-P sửa) | ✅ |
| 2d | DB copy `-u wujia_order_window,wujia_portal_sale` khi thư mục vỏ đã mất | 0 ERROR, không "invalid module" | 0 ERROR; WARNING đều của module anh Thái (có từ trước); dòng `ir_module_module` vỏ vẫn còn `uninstalled` | ✅ |
| 2e | Suite portal 15 module + `wujia_order_window` | 833, 0 đỏ | **833 → 834, 0 failed, 0 error** (+1 test helper) | ✅ |
| 2f | Snapshot `wujia_frp` so mốc lần ba F7 (`f7r2/u.json`) | 0 lệch | 99 khoá, **0 lệch thật** | ✅ |
| 2g | DB trắng `-i wujia_order_window` + test riêng | 10/10 | lần đầu **1 error** (`test_migrate…` tra `id` vỏ — chỉ Pass ở F7 vì vỏ còn trên đĩa) → sửa test → **11/11** | ✅ (sau sửa) |
| 3 | Rà diff `df385d1..HEAD` (34 file) | không code thừa/sử ký/rác/version sót | 1 comment L2 nhắc controller (sửa) · mã phiên chỉ trong docstring hook/manifest (giữ, là lịch sử tách) · `__pycache__` không tracked · version 3 module đúng, `portal_base` chỉ đổi comment nên không bump (đúng) | ✅ |
| 4a | Quy trình chapter 74 nhìn từ F8 | bước mơ hồ được ghi | 4 bước sửa chữ: hook ở L1 + `imd_names`; grep module mobile Thái; snapshot thêm nhóm; dòng vỏ trên DB trắng | ✅ |
| 4b | `split_snapshot` thiếu gì | inherit/sel/cron/tpl/srv/attach/rule theo module | thêm 7 nhóm; `info_request` đo ra **2 inherit + 19 selection** mà F7 không có | ✅ |
| 4c | Thử tách MỘT PHẦN `info_request` (DB `wujia_frp_trial`, module đích giả) | hook đủ, chỉ cột module đổi | helper suy **72/75** xmlid, 3 dư = 3 QWeb portal phải ở lại · moved 72 imd + 7 cons + 1 rel · `number_next` 1 → 1 · snapshot **80 dòng đổi chủ, 0 lệch thật** · đối chứng F7 36/36 | ✅ |
| 5 | Sửa nhỏ + test | mutation vẫn cắn | M3 (bỏ `names`) trên helper đã dời → **1 failed** đúng test | ✅ |

## 3. Tuân thủ tầng ADR-027 — soi từng cạnh

| Cạnh | Loại | Tầng | Luật | KQ |
|---|---|---|---|---|
| `wujia_order_window` → `wujia_sale` | depends | L2 → L2 | nghiệp vụ depend nghiệp vụ: được | ✅ |
| `wujia_order_window` dùng `res.area` | model | L2 → L1 (`wujia_core`) | qua depend bắc cầu `wujia_sale → wujia_franchise → wujia_core` | ✅ |
| `wujia_order_window` dùng `wujia.franchise.management`, `is_portal_order` | model/field | L2 → L2 (`wujia_franchise`, `wujia_sale`) | bắc cầu, khai báo | ✅ |
| `wujia_order_window` chứa controller / QWeb / asset / import `portal_layout` / `mobile_core` | — | — | **không có** (ls: models, views backend, security, i18n, tests, hooks) | ✅ |
| `wujia_portal_sale` → `wujia_order_window` (depends + `import OrderWindowClosed` + gọi 2 method) | depends/import/call | L3b → L2 | module ghép depend nghiệp vụ: được | ✅ |
| `wujia_portal_base` gọi `_is_within_order_window` | call có guard `hasattr` | L3a → L2 | L3a **cấm thêm depend** ⇒ guard là đúng thiết kế; R7 không báo; `test_fra3_layer_guard` giữ | ✅ |
| `wujia_mobile_*` ↔ `wujia_order_window` | — | — | 0 tham chiếu (grep) | ✅ |
| `portal_*` ↔ `mobile_*` | depends | L3b ↔ L3b | 2 vi phạm R3 có sẵn của anh Thái (`mobile_portal_exam`, `mobile_portal_info_request`) — ghi nhận, không sửa | ⚠️ Thái |
| Dư âm **tên** portal trong L2: ICP `wujia_portal.*`, field `portal_order_time_*`, xmlid view `…wujia_portal_window`, app "Wujia Portal Order Window", menu "Wujia Portal", 9 chữ "Portal" trong `.po`, method `_get_portal_order_window` | tên | — | không vi phạm luật depend; đổi = đổi dữ liệu/xmlid, cần migration ⇒ **nợ** (§5) | ⚠️ nợ |

## 4. Tên cũ `wujia_portal_order_window` còn ở đâu — lý do giữ

| Nơi | Lý do |
|---|---|
| `custom/wujia_order_window/hooks.py` (`OLD_MODULE`) + `__manifest__.py` mô tả | DB chưa nâng cấp vẫn cần hook đổi chủ; DB trắng chạy `UPDATE` 0 dòng |
| `scripts/qa/split_snapshot.py` docstring | ví dụ chạy thật của pilot |
| `docs/f7-acceptance-matrix.md`, `f-progress.md`, `f0-baseline.md`, `f-review-*.md`, `f5*.md`, `e5c-*.md`, `DEPLOY_SPRINT5.md`, `next-session-*.md`, chapter cũ | sử ký, không sửa |
| `scripts/ba_spec.bak.*` | gitignored |
| ~~`.github/workflows/deploy.yml`~~ | **đã đổi** sang `wujia_order_window` |
| ~~`scripts/qa/check_layers.py` `DEPRECATED` + docstring R7~~ | **đã đổi** (`DEPRECATED = set()`, giữ cơ chế cho F8+) |

## 5. Đã sửa trong phiên (đều <30 dòng/mục, không đổi hành vi)

- **Dời `migrate_ownership` về L1** `custom/wujia_core/tools/module_split.py` (chốt chủ dự án) + thêm chặn `new` không có trong
  `ir_module_module` (không thì ràng buộc bị gán chủ NULL im lặng) + **`imd_names(cr, old, models, extra)`**. `wujia_core`
  19.0.1.0.0 → **19.0.1.0.1** (chỉ thêm file Python; `-u wujia_core` không cần, và kéo test `wujia_franchise` ngã).
- `wujia_order_window/hooks.py` chỉ còn hằng + `pre_init_hook` gọi helper L1.
- `tests/test_split_ownership.py`: dòng module giả thay vì tra vỏ; +`test_imd_names_covers_everything_the_pilot_moved`
  (36/36, chỉ menu phải liệt kê tay; `sale.order` ra đúng 3 xmlid).
- `res_config_settings.py`: comment cờ `configured` không nhắc controller/BA row.
- `.github/workflows/deploy.yml`, `scripts/qa/check_layers.py` (§4).
- `scripts/qa/split_snapshot.py`: +`inherit` · `sel` · `cron` (Odoo 19 join `ir_act_server`) · `tpl` · `srv` · `attach` · rule theo module.
- Chapter 74 §Quy trình tách: 4 chỗ (xem `git diff`).

## 6. Nợ ghi lại

1. **Bàn giao anh Thái (không sửa hộ, không chặn F8):** `wujia_mobile_portal_info_request` ghi đè
   `wujia_portal_info_request.action_wujia_info_update_request` + `ref()` 2 view; `wujia_mobile_portal_exam` 4 file view + test
   dùng xmlid `wujia_portal_exam.*`. Sau khi Dev tách F8/F12 (xmlid đổi chủ sang `wujia_info_request`/`wujia_exam`), lần `-u`
   module mobile sẽ báo xmlid không tồn tại — Thái đổi tiền tố xmlid là xong. Dev báo trước khi deploy F8/F12.
2. Dư âm tên portal trong L2 (§3 dòng cuối): giữ vì "chỉ đổi chủ"; muốn đổi cần migration ICP key + field + xmlid + `.po`.
3. Hook Khảo sát `wujia_franchise_inspection/hooks.py` không được nối (`ec6d380`) + 46 dòng `ir_model_constraint` Khảo sát
   vẫn `wujia_franchise` — bàn giao Thái (từ F7).
4. 1 error có sẵn `test_wujia_supply_demand_report` (`c64de50`, không trong suite portal).
5. `wujia_franchise/tests/__init__.py` import file đã xoá ⇒ **không được `-u wujia_core`/`wujia_franchise` kèm `--test-enable`** (bẫy đã gặp F6, gặp lại FR-P: 2 lượt chết 255).

## 7. Bài học cho F8–F13

- **Tách một phần ≠ pilot**: F7 rút hết nên `names=None`; F8+ có QWeb/controller ở lại ⇒ luôn in phần dư
  `ir_model_data` module cũ trừ `imd_names` và giải trình từng dòng (info_request: 3 QWeb).
- **Odoo 19 có xmlid cho `ir.model.inherit` và `ir.model.fields.selection`** — F7 không gặp (model không mixin). `imd_names`
  đã phủ; snapshot đã đo.
- Grep tham chiếu xmlid phải quét **cả `custom/wujia_mobile_*`** để lập danh sách bàn giao Thái (không sửa hộ).
- Test không được tra `ir_module_module` của module đã rời repo (DB trắng không có dòng).
- CI/`deploy.yml` là "tham chiếu" dễ quên nhất — thêm vào bước 6 chapter 74.
- Log stdout trống vì `wujia_core` chuyển log sang `logs/<năm>/<tháng>/<ngày>.log` — đọc số test ở đó; hai lệnh Bash song
  song **dùng chung cwd** ⇒ luôn đường dẫn tuyệt đối.

## 8. Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
# DB copy giống UAT sau gỡ vỏ
createdb -h 127.0.0.1 -U odoo19 -T wujia_f7r2 wujia_frp
cd $W/odoo19 && $PY odoo-bin -c $W/config/odoo.conf -d wujia_frp --db-filter='^wujia_frp$' --http-port=8097 \
  --gevent-port=8197 --stop-after-init -u wujia_order_window,wujia_portal_sale            # 0 ERROR
M=$(ls $W/custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//'),wujia_order_window
$PY odoo-bin -c $W/config/odoo.conf -d wujia_frp --db-filter='^wujia_frp$' --http-port=8097 --gevent-port=8197 \
  --stop-after-init --test-enable -u "$M"                                                 # 834 / 0 / 0
python3 $W/scripts/qa/split_snapshot.py --db wujia_frp --modules wujia_portal_order_window,wujia_order_window \
  --models wujia.order.window --icp wujia_portal. -o now.json && python3 $W/scripts/qa/split_snapshot.py --diff u.json now.json  # 0 lệch
# DB trắng (KHÔNG -u wujia_core kèm --test-enable)
createdb -h 127.0.0.1 -U odoo19 wujia_frp_alone
$PY odoo-bin -c $W/config/odoo.conf -d wujia_frp_alone --db-filter='^wujia_frp_alone$' --http-port=8098 --gevent-port=8198 \
  --stop-after-init -i wujia_order_window
$PY odoo-bin ... -d wujia_frp_alone --stop-after-init --test-enable --test-tags /wujia_order_window -u wujia_order_window  # 11 / 0 / 0
python3 $W/scripts/qa/check_layers.py                                                     # 2 vi phạm R3 (Thái)
# Thử tách một phần (xem §2 4c): insert dòng ir_module_module giả, imd_names + migrate_ownership qua psycopg2, snapshot --seq
```

## 9. UAT (26/09, sau gỡ vỏ)

Sau gỡ vỏ: `wujia_order_window 19.0.1.0.0` installed · vỏ `uninstalled` · `wujia_portal_sale 19.0.4.25.0`.
**Deploy FR-P 26/09 (`9d2a606`) — đo lại chỉ đọc:** `wujia_core 19.0.1.0.1` · 36 xmlid + 6 ràng buộc (0 trùng) vẫn thuộc
`wujia_order_window` · vỏ `uninstalled` · 2 khung giờ · 3 tham số nguyên · form Settings chỉ còn app `wujia_order_window`.
