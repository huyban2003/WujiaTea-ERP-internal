# F8 — Ma trận nghiệm thu · Tách `info_request` → `wujia_info_request` + controller mỏng

Phiên F8 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13"). Lần đầu **tách một phần**:
nghiệp vụ sang module L2 mới, 3 QWeb portal + controller ở lại `wujia_portal_info_request`.

- Chủ dự án chốt (26/09): **code F8, chưa deploy**, chủ dự án tự deploy sau. **Sửa luôn 5 dòng tên trong module mobile
  của anh Thái** (`wujia_mobile_portal_info_request`), không viết bàn giao. Lần sửa đầu bị cổng quyền của Claude Code chặn;
  chủ dự án bảo sửa lần nữa thì mới sửa (3 tiền tố xmlid + test + depend, version `19.0.1.0.1`).
- UAT đo chỉ-đọc trước khi làm: mobile module **đang cài**; 0 yêu cầu; sequence `INF-` number_next 1.
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_frp` (sau FR-P):
  - `wujia_f8nm`: seed 4 yêu cầu bằng code HEAD (đủ 4 trạng thái, 1 đính kèm, chatter), chụp trước, chạy deploy, chụp sau.
  - `wujia_f8nm_h`: cùng lần seed, dùng cho server HEAD so HTML.
  - `wujia_f8nm_m`: mutation hook.
  - `wujia_f8nm_u`: test + mutation model.
  - `wujia_f8base`/`wujia_f8neg`: có cài `wujia_mobile_core` + `wujia_mobile_portal_info_request` như UAT, dùng làm đối chứng mobile.
  - `wujia_f8alone`: DB trắng.
  - `wujia_f8final`: suite cuối.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_info_request/` (mới, L2, depend `wujia_franchise`, `mail`) | `git mv` model, ACL, rule, sequence, view/menu/action backend. `.po` 81 mục (tiền tố xmlid đổi). Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_info_request/hooks.py` | `migrate_ownership(names=imd_names(MODELS, extra=[menu]), models=MODELS)`, dùng tiện ích L1 `wujia_core/tools/module_split.py` |
| Model | `_franchise_value` (1 nguồn cho `_compute_old_value` và AJAX) · `_portal_scope_domain` · `_portal_can_request` (Owner/Manager) · `create_from_portal(vals, submit, attach)`: tạo + đính kèm + gửi trong **một savepoint** |
| `wujia_portal_info_request` | Còn controller + 3 QWeb + `migrations/`. Depend `wujia_portal_base, wujia_info_request`. `19.0.2.0.0`. `.po` 56 mục |
| Controller | Gọi 4 method trên. Bỏ `unlink` tay khi đính kèm lỗi (savepoint lo). Bỏ import `get_max_role_in_franchises`, `REQUEST_TYPE_FIELD_MAP`, `fields`. **263 → 239 dòng**, response/redirect/câu chữ giữ nguyên |
| Test | `wujia_info_request`: 10 test (vòng đời, huỷ, `other`, old value, gate, phạm vi, tạo + đính kèm + gửi, rollback nguyên khối, 2 test đổi chủ). Portal: +3 HttpCase (gửi thật có file, file sai không để lại gì, staff 403). Trước F8 chỉ có 3 test, đều là đường lỗi |
| `wujia_mobile_portal_info_request` (anh Thái, chủ dự án duyệt) | 5 dòng: `views/info_request_mobile_views.xml:76,80,82` + `tests/…:11` tiền tố `wujia_portal_info_request.` → `wujia_info_request.`; depend → `wujia_info_request`; `19.0.1.0.1` |
| `check_layers.py` | `wujia_info_request` = L2, bỏ khỏi `PENDING_SPLIT` |
| `deploy.yml`, `reseed_full.sh/.ps1` | Thêm `wujia_info_request` |
| Chapter 74 | Mục Quy trình: bước 5 (tách một phần + tách `.po`), bước 6 (chốt mobile + kết quả đo lúc lỗi), số đo F8, bẫy `assertRaises`; dòng P3 |

A2 (bảng badge trong `portal_base/utils.py`): info_request không có bảng nào ở đó, `STATE_LABELS` vốn đã nằm trong controller
của nó ⇒ không có việc.

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_info_request` nhận model, view backend, menu, rule, sequence, i18n phần model | `git mv`. DB trắng chỉ `-i wujia_info_request`: **10/10** | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Log `{'ir_model_data': 72, 'ir_model_constraint': 7, 'ir_model_relation': 1}` (khớp bản thử ở FR-P). Module cũ còn đúng `portal_info_request_{list,form,detail}` | ✅ |
| 3 | Đo trước/sau: record, user trong group, number_next, menu/action, rule | `split_snapshot --diff --rename`: **80 dòng đổi chủ, 0 lệch thật** (354 khoá: 2 bảng md5, 112 field en+vi, 29 selection, 4 inherit, 3 rule, 5 ACL, 3 menu, 3 action, 13 view, seq, attach, 18 pgcons) | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_info_request.*` ở module khác | 0 còn lại (`grep`), gồm 5 dòng trong module mobile anh Thái | ✅ |
| 5 | Lượt mỏng: luật controller về model | Gate, phạm vi, tạo + đính kèm + gửi, giá trị cũ: về model. Controller không còn `create` kèm hệ quả, không còn `unlink` bù | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD (`wujia_f8nm_h`) ‖ F8 (`wujia_f8nm`), cùng lần seed, `anh.owner`: `/portal/info-request`, `?state=submitted`, `/new`, `/37`, `/37?message=created` **5/5 giống từng byte** + JSON `/franchise/1/values` giống. 3 HttpCase mới chạy trên **code HEAD cũng 6/6** (run đối chứng) | ✅ |
| 7 | Test cũ xanh | Suite 15 `wujia_portal_*` + `wujia_order_window` + `wujia_info_request`: **847, 0 đỏ** (FR-P 834 + 10 + 3) | ✅ |
| 8 | `check_layers` không còn vi phạm của info_request | R4 và R3 của info_request đều hết. Tổng **2 → 1** vi phạm (còn R3 `mobile_portal_exam`, để F12) | ✅ |
| 9 | Deploy một lệnh | DB không có mobile: `-i wujia_info_request -u wujia_portal_info_request` → 0 ERROR. DB giống UAT (có mobile, `wujia_f8neg` tạo lại từ `wujia_f8base`): `-i wujia_info_request -u wujia_portal_info_request,wujia_mobile_portal_info_request` → **exit 0, 0 ERROR**; test mobile **3/3**; action vẫn list/kanban/form | ✅ |

## Mutation (3/3 đỏ)

| # | Phá | Kết quả |
|---|---|---|
| M1 | `create_from_portal` bỏ savepoint | 2 failed (`test_create_from_portal_rolls_back_whole_block`, `test_bad_attachment_leaves_nothing`). Lượt đầu chỉ 1 đỏ: test model viết bằng `assertRaises`, mà Odoo tự bọc savepoint trong đó ⇒ đã sửa sang `try/except` |
| M2 | Gate bỏ điều kiện role | 2 failed (`test_portal_gate_owner_manager_only`, `test_staff_is_forbidden`) |
| M3 | Hook quên `extra=[menu]` | `test_hook_names_cover_the_whole_module` đỏ. Snapshot bắt được menu bị tạo lại (id 330 → 366) |

## Đối chứng mobile (`wujia_f8neg` = UAT thu nhỏ, TRƯỚC khi sửa 5 dòng)

- Chạy lệnh deploy: **exit 255**, `Cannot update missing record 'wujia_portal_info_request.action_wujia_info_update_request'`
  tại `wujia_mobile_portal_info_request/views/info_request_mobile_views.xml:76`. Lỗi xảy ra đúng như dự đoán.
- **Khác với dự đoán ban đầu** (em đã nói "cả lượt bị huỷ"): Odoo 19 commit sau từng module, nên `wujia_info_request` đã
  cài xong (72 xmlid), portal đã lên `19.0.2.0.0`, chỉ mobile dừng lại. Khởi động thường (không `-u`) vẫn chạy, action mobile
  vẫn đủ list/kanban/form. Nhưng mọi lần `-u` về sau sẽ gãy cho tới khi sửa 5 dòng.

## Còn mở

1. Deploy UAT (chủ dự án chạy): `-i wujia_info_request -u wujia_portal_info_request,wujia_mobile_portal_info_request`.
   Sau deploy đo chỉ-đọc: 3 version, 72 xmlid thuộc `wujia_info_request`, portal còn 3 QWeb, action mobile list/kanban/form.
2. Báo anh Thái: đã sửa 5 dòng trong `wujia_mobile_portal_info_request` (chủ dự án duyệt).
3. Ghi nhận, không sửa: AJAX `…/values` với `request_type=other` cho portal user đọc được field bất kỳ của cửa hàng mình
   (hành vi có sẵn, không đổi trong F8).

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_frp wujia_f8x      # seed bằng code HEAD (worktree) rồi chụp trước
python3 $W/scripts/qa/split_snapshot.py --db wujia_f8x --host 127.0.0.1 --user odoo19 \
  --modules wujia_portal_info_request,wujia_info_request \
  --models wujia.info.update.request,wujia.franchise.management --seq wujia.info.update.request -o before.json
cd $W/odoo19 && $PY odoo-bin -c $W/config/odoo.conf -d wujia_f8x --db-filter='^wujia_f8x$' --http-port=8097 \
  --gevent-port=8197 --stop-after-init -i wujia_info_request -u wujia_portal_info_request      # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_info_request=wujia_info_request            # 80 đổi chủ, 0 lệch
M=$(ls $W/custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//'),wujia_order_window,wujia_info_request
$PY odoo-bin ... -d <db copy wujia_frp> --stop-after-init --test-enable -i wujia_info_request -u "$M"   # 847 / 0 / 0
python3 $W/scripts/qa/check_layers.py
```
