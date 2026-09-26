# F11 — Ma trận nghiệm thu · Tách `notification` → `wujia_notification` + controller mỏng

Phiên F11 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13", phân hệ "announcement").
Tách một phần như F8–F10: nghiệp vụ sang module L2 mới, 4 QWeb portal + chuông header + mục nav + controller ở
lại `wujia_portal_notification`.

- Chủ dự án chốt (26/09): tên module **`wujia_notification`** · giữ nguyên `_name` cả 3 model
  (`wujia.notification`, `wujia.notification.type`, `wujia.notification.read`) · **Home vá luôn, dùng luật chung**
  (KPI "chưa đọc" = badge chuông, list Home không hiện bài hẹn giờ/hết hạn) · **code + commit + push `main`**, deploy để
  chủ dự án · 4 màu nền loại thông báo trên UAT **để về theo code** (xem "Bẫy noupdate" bên dưới).
- Mobile anh Thái: `grep notification custom/wujia_mobile_*` = 0 ⇒ không có mục bàn giao.
- 2 nhóm quyền `group_notification_user/_manager` + privilege đi theo module mới; ngoài module **không có** tham chiếu
  `wujia_portal_notification.group_*` nào (chỉ ACL csv + menu trong chính module, đã đổi sang ref cục bộ).
- UAT đo chỉ-đọc trước khi làm (RPC): `wujia_portal_notification 19.0.2.24.0`, 19 thông báo (16 đã gửi, 3 lưu trữ),
  20 dòng đã đọc, sequence `ANN/%(year)s/` số kế **20**, nhóm User 0 người / Administrator 1 người, 147 xmlid.
  5 loại noupdate: code/tên/icon/thứ tự **khớp XML**, nhưng **4/5 `bg_color` lệch** (UAT còn bảng màu Sprint 4.3 —
  `f4e5a3d`; XML đã đổi sang bảng màu Sprint 19 — `83f98b6`, noupdate nên UAT chưa từng nhận) ⇒ dừng hỏi, chủ dự án chốt để về theo code.
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_f8final` → chạy lệnh deploy F9 + F10 bằng code HEAD = `wujia_f11base`:
  - Seed bằng code HEAD (`scratchpad/f11/seed_f11.py`): bật vi_VN, 11 thông báo đủ nhánh (2 ghim còn hiệu lực, 2 hẹn giờ,
    2 hết hạn, riêng cửa hàng 1/2/3, nháp, lưu trữ), 2 đính kèm + 1 file lạc, đã đọc của `anh.owner` (1 cửa hàng) và
    `dung.multi` (cùng thông báo ở 2 cửa hàng); giả lập UAT: màu Khẩn cấp `#EC3845` + tên vi_VN tuỳ biến loại GEN.
  - `wujia_f11`: chụp trước → deploy F11 → chụp sau. `wujia_f11_h`: cùng lần seed, server HEAD (worktree) để so HTML.
  - `wujia_f11suite`: suite · `wujia_f11ctl`: test portal mới trên code HEAD · `wujia_f11alone`: DB trắng.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_notification/` (mới, L2, depend `mail, wujia_franchise`) | `git mv` 3 model, 2 nhóm quyền + privilege, ACL, 2 rule, sequence `ANN/` (**bỏ `number_next`**), 5 loại mẫu, view/menu/action backend. `.po` 159 mục (tiền tố xmlid + đường dẫn `code:` đổi). Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_notification/hooks.py` | `imd_names(MODELS, extra=[privilege, 2 nhóm, 4 menu, 5 loại])` + `migrate_ownership` |
| Model | `_portal_history_domain` / `_portal_effective_domain` (dời từ controller) · `_portal_read_domain` · `_portal_read_ids` · `_portal_unread_count` (giữ 2 câu đếm + `any`) · `_portal_get_attachment` · `wujia.notification.read._mark_read(user, cửa hàng, thông báo, opened, touch)` — **một nguồn** cho 3 chỗ ghi "đã đọc" (chi tiết / mark-read / mark-all), trả số dòng tạo |
| `wujia_portal_notification` | Còn controller + 4 QWeb + chuông + nav + CSS/JS. Depend `wujia_portal_base, wujia_notification`. `19.0.3.0.0`. `.po` 55 mục. Thư mục `migrations/` (≤ 19.0.2.2.0) để nguyên: đã chạy trên UAT, không chạy lại |
| Controller | Parse tham số → gọi model → render/JSON. **433 → 336 dòng**. Response, mã lỗi, redirect giữ nguyên. Bảng tone/nhãn portal (`PC_TYPE_TONE`, `PORTAL_PRIORITY_LABELS`) ở lại portal |
| Home `portal_base` | `_safe_count`/`_safe_list` nhánh thông báo gọi `_portal_unread_count` (cửa hàng đang chọn) + `_portal_effective_domain` (thứ tự như popup chuông) qua `hasattr` — không thêm depend. `19.0.7.27.0` |
| A2 | `portal_base/controllers/utils.py` không có bảng badge thông báo ⇒ không có gì phải dời |
| Test | `wujia_notification`: dời 2 file test model (backend, chọn đối tượng) + `test_portal_rules` (4: phạm vi lịch sử/còn hiệu lực, chưa đọc theo cửa hàng, 3 chế độ `_mark_read`, đính kèm thuộc thông báo) + `test_split_ownership` (2). Fixture `NotificationCommon` dùng chung. Portal: `test_portal_notification_f11` 5 HttpCase (KPI Home = badge, list Home, mở lại chi tiết giữ `read_date`, mark-read chỉ id truy cập được, tải đính kèm 200/403/404). `test_notification_timezone` ở lại portal (dùng tiện ích `portal_base`) |
| `check_layers.py`, `deploy.yml`, `reseed_full.sh/.ps1`, `test_sprint32.py` | `wujia_notification` = L2, bỏ khỏi `PENDING_SPLIT`; thêm vào `-i/-u` và reseed; script sprint 32 gọi domain từ model |

C4: phạm vi portal của thông báo là **theo cửa hàng** (broadcast hoặc gắn cửa hàng đang thao tác) — gom về
`_portal_history_domain`/`_portal_effective_domain`, controller không còn tự ghép domain.

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_notification` nhận model, view backend, menu, **group**, rule, sequence, data, i18n phần model | `git mv`. DB trắng chỉ `-i wujia_notification` (cài rồi `-u --test-tags /wujia_notification`): **37/37**; DB trắng chỉ có `wujia_core, wujia_franchise, wujia_notification` | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Log `{'ir_model_data': 140, 'ir_model_constraint': 28, 'ir_model_relation': 5}`. Module cũ còn đúng 6 view: `portal_notification_{list,results,results_part,detail}`, `layout_top_navbar_bell_icon`, `mobile_bottomnav_notification` | ✅ |
| 3 | Đo trước/sau: record, **user trong group**, sequence, menu/action, rule | `split_snapshot --diff --rename`: **173 dòng đổi chủ, 1 lệch có giải trình** (389 khoá). Bảng thông báo (56) + đã đọc (13) md5 giống hệt · sequence **kèm `last_value` 1166** giữ · nhóm Administrator 1 / User 0 / Portal 30 giữ. Lệch duy nhất: md5 bảng loại — soi từng dòng: `bg_color` URG `#EC3845` → `#EF4444` (giá trị XML, đúng dự kiến), tên vi_VN tuỳ biến giữ | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_notification.group_*` ở module khác | Không có ngoài module. Trong module: ACL csv + `backend_menu.xml` đổi sang ref cục bộ. Còn lại chỉ trỏ QWeb/CSS ở lại portal (test quét của `portal_base`) — đúng | ✅ |
| 5 | Lượt mỏng: luật controller về model (`_mark_read`, domain phạm vi) | "Đã đọc" viết 3 lần → `_mark_read`; domain lịch sử/còn hiệu lực, đếm chưa đọc, "đính kèm thuộc thông báo" về model. Controller không còn `create`/`write` bản ghi đọc hay search `ir.attachment` | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD (`wujia_f11_h`) ‖ F11 (`wujia_f11`), cùng lần seed, 3 phiên (`anh.owner` 1 cửa hàng · `dung.multi` chưa chọn · `dung.multi` cửa hàng 2), chuẩn hoá hash asset + csrf + `registry_hash`: **117/120 giống từng byte** — 28 GET (danh sách, trang 2, limit hợp lệ/rác, lọc đọc/chưa đọc/`unread=1`, loại đúng/rác, từ khoá, mức độ đúng/rác, ngày đúng/ngược/rác, fragment, chi tiết hẹn giờ/cửa hàng khác/nháp/lưu trữ/không tồn tại, đính kèm của mình/của thông báo khác/file lạc) + 2 JSON + 7 lượt ghi (mở chi tiết, mở lại, 3 mark-read id lẫn lộn/rỗng, mark-all) + 2 JSON sau ghi. **3 lệch đều là Home** (đúng chỗ vá). DB đã đọc sau ghi giống hệt (104 dòng, cả `last_open_date`). Bundle CSS/JS cùng md5 | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Suite 16 `wujia_portal_*` + `wujia_order_window,wujia_info_request,wujia_knowledge,wujia_support,wujia_notification`: **885, 0 đỏ** (F10-fix + 9 test mới + 2 đổi chủ). Đối chứng: 5 HttpCase portal mới chạy trên code HEAD ⇒ **đúng 2 đỏ** (2 test Home — lỗi cũ), 56 xanh ⇒ route thông báo không đổi hành vi | ✅ |
| 8 | `check_layers` không còn vi phạm của notification | Tổng giữ **1** (R3 `mobile_portal_exam`, để F12); R7 giữ 2 (anh Thái); `wujia_portal_notification` rời `PENDING_SPLIT` | ✅ |
| 9 | Deploy một lệnh | `-i wujia_notification -u wujia_portal_notification,wujia_portal_base` → exit 0, 0 ERROR | ✅ |

## Home — lệch cũ đã vá (chủ dự án chốt)

Home đếm "chưa đọc" bằng luật riêng: mọi thông báo đang hiện (kể cả **hẹn giờ** và **hết hạn**) trừ số dòng đã đọc của
user ở **mọi cửa hàng**. List "Thông báo mới nhất" cũng không lọc ngày phát hành ⇒ bài hẹn giờ nằm đầu Home.
Đo cùng DB, sau lượt ghi (KPI Home ‖ badge chuông):

| Phiên | HEAD | F11 |
|---|---|---|
| `anh.owner` (1 cửa hàng, đã "đánh dấu tất cả") | 3 ‖ 0 | **0 ‖ 0** |
| `dung.multi` chưa chọn cửa hàng | 6 ‖ 3 | **3 ‖ 3** |
| `dung.multi` cửa hàng 2 | 1 ‖ 0 | **0 ‖ 0** |
| `dung.multi` cửa hàng 3 | 4 ‖ 48 | **48 ‖ 48** |

List Home F11: 2 bài ghim còn hiệu lực thay cho 2 bài hẹn giờ. Playwright local PC 1440 + mobile 390 (Home, danh sách,
lọc chưa đọc, 2 chi tiết, popup chuông): KPI PC 47 = mobile 47 = popup "47 chưa đọc" = badge 47; 0 tràn ngang; lỗi
duy nhất 404 `/app-assets/data/locales/en.json` (có từ trước).

## Bẫy `noupdate` — 4 màu nền loại thông báo (đo trong phiên)

- Lần `-i` nạp lại 5 bản ghi `wujia.notification.type` noupdate lên xmlid vừa đổi chủ. Trên `wujia_f11` (màu Khẩn cấp
  giả lập `#EC3845` như UAT + tên vi_VN GEN tuỳ biến "Thông báo chung (HQ)"): sau deploy **`bg_color` về giá trị XML
  `#EF4444`**, **tên vi_VN tuỳ biến giữ nguyên** — đúng kết luận F10.
- Trên UAT sẽ đổi 4 ô màu: Khẩn cấp `#EC3845→#EF4444` · Thông báo chung `#22A9DE→#28A9DF` · Hệ thống `#8A9099→#8A939E` ·
  Khác `#24B269→#16A34A` (Khuyến mãi giữ). Chỉ hiện ở ô màu form Loại thông báo backend; portal tô màu bằng class CSS
  (`PC_TYPE_TONE`), không đọc field này. Chủ dự án chốt để UAT theo code.

## Mutation

| # | Phá | Kết quả (64 test notification + portal notification) |
|---|---|---|
| M1 | `_portal_history_domain` bỏ lọc ngày phát hành | 5 đỏ: domain model, chưa đọc theo cửa hàng, list Home, mark-read chỉ id truy cập được, đính kèm thông báo hẹn giờ 404 |
| M2 | `_mark_read` ghi cả khi chưa chọn cửa hàng | 2 đỏ: `test_mark_read_modes`, `test_detail_readable_without_store_but_no_read_row` (test cũ NOTI-02) |
| M3 | `_mark_read` bỏ `touch` (mở lại không đổi `last_open_date`) | 1 đỏ: `test_mark_read_modes` |
| M4 | Đếm chưa đọc bỏ lọc cửa hàng | 1 đỏ: `test_unread_count_is_per_store` |
| M5 | `_portal_get_attachment` bỏ kiểm "thuộc thông báo" | 2 đỏ: test model + test portal tải đính kèm |

## Còn mở

1. Chờ deploy UAT (chủ dự án). Sau deploy đo chỉ-đọc: 3 version (`wujia_notification 19.0.1.0.0` · `portal_notification
   19.0.3.0.0` · `portal_base 19.0.7.27.0`), module mới 141 xmlid (140 + `field_…__rating_ids` như F8–F10), portal còn 6 view,
   số kế `ANN/` **20**, nhóm Administrator 1 người, 4 ô màu đổi như trên, KPI Home = badge chuông.
2. Phát hiện có từ trước (không thuộc F11, HTML HEAD ‖ F11 giống từng byte): phụ đề danh sách ghi "Hiển thị thông báo còn
   hiệu lực" nhưng danh sách là lịch sử (có cả bài hết hạn, gắn nhãn "Đã hết hiệu lực"); bài hết hạn chưa mở vẫn gắn
   "Chưa đọc". Ghi lại, hỏi BA nếu cần.
3. `is_read_by()` trên model không còn nơi gọi (đếm đọc không theo cửa hàng) — để nguyên, dọn ở ★FR-A.
4. Dọn DB đo `wujia_f11*` + worktree `scratchpad/f11/head` (dọn cuối phiên).

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_f8final wujia_f11base    # + cp filestore; -i wujia_knowledge,wujia_support -u …knowledge,…support,base bằng code HEAD; seed_f11.py
python3 $W/scripts/qa/split_snapshot.py --db wujia_f11 --host 127.0.0.1 --user odoo19 \
  --modules wujia_portal_notification,wujia_notification \
  --models wujia.notification,wujia.notification.type,wujia.notification.read --seq wujia.notification -o before.json
cd $W/odoo19 && $PY odoo-bin -c <conf> -d wujia_f11 --stop-after-init \
  -i wujia_notification -u wujia_portal_notification,wujia_portal_base                         # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_notification=wujia_notification        # 173 đổi chủ, 1 lệch (màu loại)
M=$(ls $W/custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//'),wujia_order_window,wujia_info_request,wujia_knowledge,wujia_support,wujia_notification
$PY odoo-bin ... -d <copy wujia_f11base> --stop-after-init --test-enable -i wujia_notification -u "$M"   # 885 / 0 / 0
# DB trắng: -i wujia_notification (không --test-enable) rồi
$PY odoo-bin ... --stop-after-init --test-enable --test-tags /wujia_notification -u wujia_notification     # 37 / 0 / 0
python3 $W/scripts/qa/check_layers.py
```
So HTML: `scratchpad/f11/cmp_http.py` (2 server 8097 HEAD ‖ 8098 F11). Bundle trên DB copy trả 500 vì filestore gốc thiếu
file bundle cũ (bài học F9) — xoá `ir_attachment` `/web/assets/%` trên DB đo rồi so md5 nội dung.
