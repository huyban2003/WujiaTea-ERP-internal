# F9 — Ma trận nghiệm thu · Tách `knowledge` → `wujia_knowledge` + controller mỏng

Phiên F9 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13"). Tách một phần như F8:
nghiệp vụ sang module L2 mới, 3 QWeb portal + 2 mục nav + controller ở lại `wujia_portal_knowledge`.

- Chủ dự án chốt (26/09): **Home dùng chung luật hiển thị, vá luôn** (bài hẹn giờ tương lai thôi hiện ở Home) ·
  **code + commit + push `main`**, deploy để chủ dự án.
- Mobile anh Thái: `grep knowledge custom/wujia_mobile_*` = 0 ⇒ không có mục bàn giao.
- UAT đo chỉ-đọc trước khi làm (RPC): 27 bài, sequence `KNW-` số kế **28**; cron hạ bài hết hạn active, 1 ngày,
  OdooBot (khớp XML); `wujia_portal_knowledge 19.0.3.21.0`, `wujia_portal_base 19.0.7.24.0`.
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_f8final` (sau F8):
  - `wujia_f9`: seed bằng code HEAD (worktree) — thêm danh mục con, tag, 4 bài (có đính kèm m2m + res_id, hẹn giờ
    +5 ngày, inactive, sắp hết hạn), chatter, view_count. Chụp trước, chạy deploy, chụp sau.
  - `wujia_f9_h`: cùng lần seed, server HEAD để so HTML. `wujia_f9_m`: bản dự phòng cùng lần seed.
  - `wujia_f9final`: suite · `wujia_f9ctl`: test mới trên code HEAD · `wujia_f9alone`: DB trắng ·
    `wujia_f9m1/m2/m3`: mutation.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_knowledge/` (mới, L2, depend `wujia_franchise`, `mail`) | `git mv` 3 model, ACL, sequence, cron, view/menu/action backend. `.po` 97 mục (tiền tố xmlid đổi). Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_knowledge/hooks.py` | `imd_names(MODELS, extra=[4 menu])` + `migrate_ownership`, tiện ích L1 `wujia_core/tools/module_split.py` |
| `data/ir_sequence_data.xml` | **Bỏ `<field name="number_next">1</field>`** — xem "Bẫy noupdate" dưới |
| Model | `_portal_visible_domain` (luật hiển thị, 1 nguồn) · `_portal_search_domain(keyword)` · `_portal_get_attachment(att_id)` (attachment phải thuộc bài: m2m hoặc res_model/res_id) |
| `wujia_portal_knowledge` | Còn controller + 3 QWeb + 2 nav + CSS. Depend `wujia_portal_base, wujia_knowledge`. `19.0.4.0.0`. `.po`/`.pot` 26 mục |
| Controller | Bỏ 2 hàm domain module-level + tự search attachment; gọi 3 method trên. **180 → 153 dòng**, response/redirect/câu chữ giữ nguyên |
| `wujia_portal_base` (Home) | `Article._portal_visible_domain()` qua guard `env.get` + `hasattr` (không thêm depend). `19.0.7.25.0` |
| Test | `wujia_knowledge`: 10 (4 dời từ portal + slug/mã/ngày phát hành, publish từ nháp, cron hạ bài hết hạn, attachment thuộc bài, tìm kiếm, 2 test đổi chủ). Portal: 13 (10 cũ + giờ địa phương dời vào + tải đính kèm 200/403 + **Home không hiện bài hẹn giờ**) |
| `scripts/qa/split_snapshot.py` | Nhóm `seq` đọc thêm `last_value` của sequence Postgres (điểm mù F7–F8) |
| `check_layers.py`, `deploy.yml`, `reseed_full.sh/.ps1` | `wujia_knowledge` = L2, bỏ khỏi `PENDING_SPLIT`; thêm vào `-i/-u` và reseed |
| Chapter 74 | Bước 2 bẫy `noupdate`, bước 5 số `.po`, đoạn đo sequence, đoạn F9, dòng P4 |

A2 (bảng badge `portal_base/utils.py`): không có bảng nào của knowledge ⇒ không có việc. C4: knowledge là toàn cục
(không lọc cửa hàng) ⇒ phạm vi = `_portal_visible_domain`.

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_knowledge` nhận model, view backend, menu, cron, sequence, i18n phần model | `git mv`. DB trắng chỉ `-i wujia_knowledge`: **10/10** | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Log `{'ir_model_data': 107, 'ir_model_constraint': 13, 'ir_model_relation': 2}`. Module cũ còn đúng 5 view: `portal_knowledge_{notice,list,detail}`, `layout_sidenav_knowledge`, `mobile_bottomnav_knowledge` | ✅ |
| 3 | Đo trước/sau: record, user trong group, sequence, menu/action, cron | `split_snapshot --diff --rename`: **122 dòng đổi chủ, 0 lệch thật** (303 khoá: 3 bảng md5, 72 field en+vi, 12 selection, 2 inherit, 6 ACL, 4 menu, 3 action, 12 view, cron, srv, seq **kèm `last_value` 438**, attach, 12 pgcons). Menu id 331–334 và cron id 26 giữ nguyên; `number_next_actual` 439 | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_knowledge.*` ở module khác | Còn lại chỉ trỏ vào QWeb/controller ở lại portal (test quét của `portal_base`) — đúng | ✅ |
| 5 | Lượt mỏng: luật controller về model | Luật hiển thị, tìm kiếm, "đính kèm thuộc bài" về model; controller không còn domain nghiệp vụ, không tự search `ir.attachment` | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD (`wujia_f9_h`) ‖ F9 (`wujia_f9`), cùng lần seed, `anh.owner`, chuẩn hoá hash asset + `registry_hash`: **12/12 route giống từng byte** (list, lọc danh mục/tag/rác, tìm kiếm ×2, trang 2, chi tiết, bài hẹn giờ 303, 2 đính kèm 200, đính kèm lạ 403) + JSON search 2/2. Bundle CSS/JS cùng md5. `/portal` (Home) lệch **đúng 1 chỗ theo chốt**: bài hẹn giờ biến mất, bài kế lên thay | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Suite 15 `wujia_portal_*` + `wujia_order_window,wujia_info_request,wujia_knowledge`: **856, 0 đỏ** (F8 847 + 9). Test mới trên code HEAD: **chỉ test Home đỏ** (chứng minh lỗi có thật), test tải đính kèm xanh | ✅ |
| 8 | `check_layers` không còn vi phạm của knowledge | Tổng giữ **1** (R3 `mobile_portal_exam`, để F12); R7 giữ 2 (anh Thái) — lời gọi Home có guard `hasattr` | ✅ |
| 9 | Deploy một lệnh | `-i wujia_knowledge -u wujia_portal_knowledge,wujia_portal_base` → exit 0, 0 ERROR | ✅ |

## Bẫy `noupdate` — sequence bị reset (bắt được trong phiên)

- Lượt deploy đầu trên `wujia_f9`: snapshot cũ báo **0 lệch**, nhưng sequence Postgres `ir_sequence_023` về
  `last_value 1, is_called false` (HEAD: 438). Bài kế sẽ ra `KNW-000001` — trùng mã, và `_sql_constraints` không
  còn hiệu lực trên Odoo 19 nên không có gì chặn.
- Gốc: `-i` chạy chế độ `init` ⇒ `convert.py` nạp lại mọi bản ghi `noupdate="1"` lên xmlid vừa đổi chủ;
  `number_next` trong XML ⇒ `ir.sequence.write` ⇒ `ALTER SEQUENCE RESTART`.
- Sửa: bỏ dòng `number_next` khỏi XML (mặc định vẫn 1 khi cài mới) + snapshot đọc `last_value`. Chạy lại: 438 giữ.
- F8 cùng bẫy trên UAT nhưng **vô hại**: 0 yêu cầu, `INF-` số kế 1 (đo RPC 26/09). F10–F13 có sequence thật
  (support, announcement ANN, exam ×3, return) ⇒ bỏ `number_next` là bước bắt buộc (ghi chapter 74 bước 2).
- Cron cũng bị nạp lại theo XML: UAT khớp XML (active, 1 ngày, OdooBot) nên không đổi gì.

## Mutation

| # | Phá | Kết quả |
|---|---|---|
| M1 | Hook quên `extra` (4 menu) | Test đơn vị **không** đỏ (trạng thái cuối giống hệt, chỉ khác id menu). `split_snapshot` bắt **10 lệch thật** (menu tạo lại id 367+). Lỗi hook thuộc phép đo trước/sau |
| M2 | `_portal_visible_domain` bỏ điều kiện ngày phát hành | 2 đỏ: `test_visible_domain_excludes_hidden_articles`, `test_home_hides_scheduled_article` |
| M3 | `_portal_get_attachment` bỏ kiểm `res_id` | 2 đỏ: `test_get_attachment_only_returns_article_files`, `test_attachment_download_only_serves_article_files` |
| M4 | Giữ `number_next` trong XML sequence (lượt đầu, không cố ý) | Snapshot mới: `seq` 438 → null (1 lệch thật) |

## Còn mở

1. ✅ Đã deploy UAT 26/09: đo chỉ-đọc đạt. 3 version đúng. Module mới 108 xmlid (107 + `field_wujia_knowledge_article__rating_ids`
   vì UAT cài `rating`, như F8). Sequence số kế **28**, cron nguyên, menu/action không tạo lại. Portal + Home + JSON 200, attachment lạ
   403. UAT không có bài hẹn giờ/đính kèm nên hai nhánh đó dựa vào test local. Chi tiết ở `f-progress.md` mục F9, dòng Deploy.
2. Nợ ghi nhận, không sửa trong F9: `_sql_constraints` (unique slug/mã bài, mã danh mục, tên tag) **không còn hiệu lực
   trên Odoo 19** (log `Model attribute '_sql_constraints' is no longer supported`; DB không có UNIQUE) — cần đổi sang
   `models.Constraint` + kiểm dữ liệu trùng trước. Cùng lỗi ở nhiều module khác.
3. Nợ ghi nhận: `write` đặt lại `publish_date = now` khi publish một bài nháp **đã có ngày hẹn** (mất lịch hẹn) — hành
   vi có sẵn, cần BA xác nhận ý muốn trước khi đổi.
4. Dọn DB đo `wujia_f9*` (đã dọn cuối phiên).

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_f8final wujia_f9x      # seed bằng code HEAD (worktree) rồi chụp trước
python3 $W/scripts/qa/split_snapshot.py --db wujia_f9x --host 127.0.0.1 --user odoo19 \
  --modules wujia_portal_knowledge,wujia_knowledge \
  --models wujia.knowledge.article,wujia.knowledge.category,wujia.knowledge.tag --seq wujia.knowledge.article -o before.json
cd $W/odoo19 && $PY odoo-bin -c <conf> -d wujia_f9x --db-filter='^wujia_f9x$' --http-port=8097 --gevent-port=8197 \
  --stop-after-init -i wujia_knowledge -u wujia_portal_knowledge,wujia_portal_base          # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_knowledge=wujia_knowledge             # 122 đổi chủ, 0 lệch
M=$(ls $W/custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//'),wujia_order_window,wujia_info_request,wujia_knowledge
$PY odoo-bin ... -d <db copy wujia_f8final> --stop-after-init --test-enable -i wujia_knowledge -u "$M"   # 856 / 0 / 0
python3 $W/scripts/qa/check_layers.py
```
Port 8092 còn bị server cũ (pid 23706) chiếm — HttpCase phải chạy với `--http-port` khác.
