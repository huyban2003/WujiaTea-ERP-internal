# F10 — Ma trận nghiệm thu · Tách `support` → `wujia_support` + controller mỏng

Phiên F10 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13"). Tách một phần như F8/F9:
nghiệp vụ sang module L2 mới, 3 QWeb portal + 2 mục nav + controller ở lại `wujia_portal_support`.

- Chủ dự án chốt (26/09): **code + commit + push `main`**, deploy để chủ dự án · **dời luôn phần trả lời ticket**
  (`message_post` + phân tích phản hồi) về model.
- Mobile anh Thái: `grep support custom/wujia_mobile_*` = 0 ⇒ không có mục bàn giao.
- Không có nhóm quyền riêng (ACL/rule chỉ dùng `base.group_portal` / `base.group_user`) ⇒ không có tham chiếu
  `wujia_portal_support.group_*` nào phải sửa.
- UAT đo chỉ-đọc trước khi làm (RPC): `wujia_portal_support 19.0.3.28.0`, 15 ticket, sequence `WJ-TK/%(y)s/` số kế
  **17** (đã không có `number_next` trong XML); 7 danh mục noupdate **khớp XML** (name en_US/code/sequence), cả 7 có
  bản dịch vi_VN ⇒ không phải dừng hỏi (bẫy noupdate bước 2).
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_f8final` → chạy lệnh deploy F9 bằng code HEAD = `wujia_f10base`:
  - Seed bằng code HEAD: bật vi_VN, 24 ticket `anh.owner` (đủ 6 trạng thái, 1 ẩn portal, 1 archived, gắn SO/batch),
    chatter hai chiều, đính kèm res_id + m2m cũ + 1 file lạc, 1 ticket của `cuong.staff` cùng cửa hàng. Sequence 207.
  - `wujia_f10`: chụp trước → deploy F10 → chụp sau. `wujia_f10_h`: cùng lần seed, server HEAD (worktree) để so HTML.
    `wujia_f10_m`: cùng lần seed, giả lập bản dịch/giá trị tuỳ biến trên danh mục.
  - `wujia_f10suite`: suite · `wujia_f10ctl`: test portal mới trên code HEAD · `wujia_f10alone`: DB trắng.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_support/` (mới, L2, depend `mail, wujia_franchise, sale, stock_picking_batch, sales_team`) | `git mv` 2 model, ACL, rule, sequence, 7 danh mục, view/menu/action backend. `.po` 129 mục (tiền tố xmlid đổi). Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_support/hooks.py` | `imd_names(MODELS, extra=[4 menu + 7 danh mục])` + `migrate_ownership` |
| Model | `_portal_scope_domain(user)` · `create_from_portal(vals, franchise_ids, attach)` → `(ticket, mã lỗi)`, kiểm + tạo + đính kèm trong **một savepoint** (thay `ticket.unlink()`) · `_portal_reply(user, body)` · `_portal_get_attachment(att_id)` |
| `wujia_portal_support` | Còn controller + 3 QWeb + 2 nav + CSS. Depend `wujia_portal_base, wujia_support`. `19.0.4.0.0`. `.po`/`.pot` 75 mục |
| Controller | Parse form → gọi model → redirect/render. **200 → 166 dòng** (tính cả bảng badge dời vào, +12). Mã lỗi, redirect, câu chữ giữ nguyên |
| A2 — `MOBILE_TICKET_BADGES` | Dời từ `portal_base/controllers/utils.py` về `portal_support/controllers/portal.py` (kèm ghi chú drift nhãn). Test quét badge của `portal_base`: phần ticket dời sang `test_scan_e2b` (đã import từng module), `test_scan_e2` giữ chạy được khi `portal_base` cài một mình. `portal_base 19.0.7.26.0` |
| Test | `wujia_support` 11: mã/vai trò/ngày mở, mốc ngày theo trạng thái, lý do huỷ, phạm vi, `create_from_portal` (ok + 6 input sai + rollback khi đính kèm lỗi — method trả mã lỗi, test không bọc `assertRaises`), trả lời + phân tích, đính kèm thuộc ticket, 2 test đổi chủ. Portal: 5 HttpCase mới (danh sách, ticket người khác, trả lời, tải đính kèm 200/403/404, POST cửa hàng ngoài phạm vi) |
| `check_layers.py`, `deploy.yml`, `reseed_full.sh/.ps1`, `seed_support_demo.py` | `wujia_support` = L2, bỏ khỏi `PENDING_SPLIT`; thêm vào `-i/-u` và reseed; docstring seed |
| Chapter 74 | Bước 2 bẫy noupdate thêm dữ liệu danh mục, bước 5 số `.po`, đoạn F10, dòng P5 |

C4: phạm vi portal của support là **theo người tạo** (`created_by_id = user`, `portal_visible`), không theo cửa hàng —
giữ nguyên hành vi, gom về `_portal_scope_domain` (ghi nợ hỏi BA bên dưới).

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_support` nhận model, view backend, menu, rule, sequence, data, i18n phần model | `git mv`. DB trắng chỉ `-i wujia_support` (cài rồi `-u --test-tags /wujia_support`): **11/11** | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Log `{'ir_model_data': 113, 'ir_model_constraint': 16, 'ir_model_relation': 1}`. Module cũ còn đúng 5 view: `portal_support_{list,form,detail}`, `layout_sidenav_support`, `mobile_bottomnav_support` | ✅ |
| 3 | Đo trước/sau: record, user trong group, sequence, menu/action, rule | `split_snapshot --diff --rename`: **130 dòng đổi chủ, 1 lệch có giải trình** (313 khoá: 2 bảng md5, 69 field en+vi, 19 selection, 2 inherit, 4 ACL, 2 rule, 4 menu, 3 action, 10 view, seq **kèm `last_value` 207**, attach, 16 pgcons). Lệch duy nhất: md5 bảng danh mục — soi từng dòng chỉ `write_date` đổi (nạp lại noupdate ghi cùng giá trị), name en/vi, code, sequence giữ | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_support.*` ở module khác | Không có `group_*`. Còn lại chỉ trỏ QWeb/controller ở lại portal (test quét của `portal_base`) — đúng | ✅ |
| 5 | Lượt mỏng: luật controller về model | Phạm vi, kiểm + tạo + đính kèm, trả lời, "đính kèm thuộc ticket" về model; controller không còn `create`/`unlink`/`message_post`/search `ir.attachment` | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD (`wujia_f10_h`) ‖ F10 (`wujia_f10`), cùng lần seed, `anh.owner`, chuẩn hoá hash asset + csrf: **18/18 GET giống từng byte** (danh sách, lọc trạng thái đúng/rác, tìm theo tiêu đề/mã, trang 2, form, form có lỗi, 2 chi tiết, ticket ẩn/archived/người khác 303, đính kèm res_id + m2m 200, file lạc/đính kèm ticket khác 403, ticket người khác 404) + **9/9 POST cùng `Location`** (thiếu field, id rác, cửa hàng lạ, danh mục lạ, file HTML, tạo thành công với `subject` + priority lạ, trả lời, trả lời rỗng, trả lời ticket người khác). DB sau POST giống hệt (ticket 209, đính kèm, chatter, phân tích, sequence). Bundle CSS/JS cùng md5 | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Suite 16 `wujia_portal_*` + `wujia_order_window,wujia_info_request,wujia_knowledge,wujia_support`: **872, 0 đỏ** (F9 856 + 16). 5 HttpCase portal mới chạy trên code HEAD: **12/12 test portal xanh** ⇒ hành vi không đổi | ✅ |
| 8 | `check_layers` không còn vi phạm của support | Tổng giữ **1** (R3 `mobile_portal_exam`, để F12); R7 giữ 2 (anh Thái); `wujia_portal_support` rời `PENDING_SPLIT` | ✅ |
| 9 | Deploy một lệnh | `-i wujia_support -u wujia_portal_support,wujia_portal_base` → exit 0, 0 ERROR | ✅ |

## Bẫy `noupdate` — dữ liệu danh mục (đo trong phiên)

- Lần `-i` nạp lại 7 bản ghi `wujia.support.category` noupdate lên xmlid vừa đổi chủ. Trên `wujia_f10_m` giả lập UAT
  (thêm vi_VN "Đặt hàng" cho danh mục po để trống, đổi vi_VN "Vận hành" → "Vận hành cửa hàng" và `sequence` 50 → 55):
  sau deploy **bản dịch vi_VN giữ nguyên cả hai**, còn **`sequence` bị đưa về 50** (giá trị XML).
- Kết luận: field ghi trong XML bị ghi đè bằng giá trị XML, bản dịch không bị `.po` đè. UAT đang khớp XML
  (sequence 10…99, name en_US như XML) ⇒ deploy an toàn. Ghi vào chapter 74 bước 2.

## Mutation

| # | Phá | Kết quả |
|---|---|---|
| M1 | `create_from_portal` bỏ kiểm cửa hàng ngoài phạm vi | 2 đỏ: `test_create_from_portal_rejects_bad_input`, `test_post_to_store_outside_scope_is_rejected` |
| M2 | `_portal_get_attachment` bỏ kiểm `res_id` | 2 đỏ: `test_get_attachment_only_returns_ticket_files`, `test_attachment_download_only_serves_ticket_files` (lượt đầu test portal không bắt — thêm ca "đính kèm ticket khác qua URL ticket mình") |
| M3 | Bỏ savepoint (tạo rồi đính kèm lỗi không rollback) | 3 đỏ: `test_create_from_portal_rolls_back_when_attachment_fails` + 2 test F1 (`html_attachment_rejected_without_ticket`, `more_than_six_files_rejected`) |
| M4 | `_portal_scope_domain` bỏ `portal_visible` | 1 đỏ: `test_scope_domain_is_own_visible_tickets` |

## Còn mở

1. ✅ Đã deploy UAT 26/09: đo chỉ-đọc đạt. 3 version đúng. Module mới 114 xmlid (113 + `field_wujia_support_ticket__rating_ids`
   vì UAT cài `rating`, như F8/F9), portal còn 5 view. Số kế `WJ-TK` **17**, 7 danh mục + vi_VN nguyên, menu/action/rule giữ id.
   Portal PC + mobile, backend 200; `anh.owner` chỉ thấy ticket mình tạo; attachment lạ 403. Chi tiết ở `f-progress.md` mục F10, dòng Deploy.
   Phát hiện có từ trước: chi tiết ticket chỉ hiện đính kèm m2m cũ, file tải từ portal (gắn `res_id`) không có link tải.
2. Nợ hỏi BA: portal support lọc theo **người tạo**, không theo cửa hàng — quản lý cửa hàng không thấy ticket nhân viên
   cùng cửa hàng tạo (đã nằm trong 7 điểm DOC-CTRL). Giữ nguyên tới khi BA chốt.
3. Nợ chung: `_sql_constraints` danh mục (unique name/code) hết hiệu lực trên Odoo 19 (như F9).
4. Test đa module `test_scan_e2b` của `portal_base` import thẳng từng `portal_*` — không chạy được khi `portal_base`
   cài một mình (có từ trước, không thuộc F10).
5. Dọn DB đo `wujia_f10*` + worktree `scratchpad/f10/head` (đã dọn cuối phiên).

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_f8final wujia_f10base      # + cp filestore; -i wujia_knowledge -u …knowledge,base bằng code HEAD; seed
python3 $W/scripts/qa/split_snapshot.py --db wujia_f10 --host 127.0.0.1 --user odoo19 \
  --modules wujia_portal_support,wujia_support \
  --models wujia.support.ticket,wujia.support.category --seq wujia.support.ticket -o before.json
cd $W/odoo19 && $PY odoo-bin -c <conf> -d wujia_f10 --db-filter='^wujia_f10$' --http-port=8098 --gevent-port=8198 \
  --stop-after-init -i wujia_support -u wujia_portal_support,wujia_portal_base          # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_support=wujia_support             # 130 đổi chủ, 1 lệch (write_date)
M=$(ls $W/custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//'),wujia_order_window,wujia_info_request,wujia_knowledge,wujia_support
$PY odoo-bin ... -d <db copy wujia_f8final> --stop-after-init --test-enable -i wujia_knowledge,wujia_support -u "$M"   # 872 / 0 / 0
# DB trắng: -i wujia_support (không --test-enable, tests wujia_franchise import file đã xoá) rồi
$PY odoo-bin ... --stop-after-init --test-enable --test-tags /wujia_support -u wujia_support                   # 11 / 0 / 0
python3 $W/scripts/qa/check_layers.py
```
Bundle asset trên DB copy từ `wujia_f8final` trả 500: filestore gốc thiếu file bundle cũ (bài học F9) — xoá
`ir_attachment` `/web/assets/%` trên DB đo để Odoo sinh lại, rồi so md5 nội dung (hash URL khác vì Odoo tính theo mtime file:
worktree ≠ cây chính).
