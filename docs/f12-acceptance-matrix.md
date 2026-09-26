# F12 — Ma trận nghiệm thu · Tách `exam` → `wujia_exam` + controller mỏng

Phiên F12 nhánh sau cổng F (`docs/next-session-clusters-F.md` §3 "Prompt F8–F13", phân hệ "exam"), gộp F12a (chuyển
model/quyền) + F12b (controller mỏng) một phiên. Tách một phần như F8–F11: nghiệp vụ sang module L2 mới, 3 QWeb portal +
2 mục nav + controller ở lại `wujia_portal_exam`. Đây là chỗ gỡ **vi phạm tầng cuối cùng** của `check_layers`
(R3: `wujia_mobile_portal_exam` → `wujia_portal_exam`).

- Chủ dự án chốt (26/09): tên module **`wujia_exam`** · giữ nguyên `_name` cả 5 model (`wujia.exam.course`,
  `.session`, `.time.slot`, `.registration`, `.registration.line`) · **sửa luôn mobile anh Thái như F8** (đổi depend + ref
  xmlid, bump version, báo Thái trước deploy) · gộp a+b, **commit + push `main`**, deploy để chủ dự án · constraint
  "tối đa người/phiếu" **dùng chung một nguồn** với portal (ca thi → để trống thì lấy của khoá).
- UAT đo chỉ-đọc trước khi làm (RPC): `wujia_portal_exam 19.0.5.23.0`, `wujia_mobile_portal_exam 19.0.1.0.0` đã cài;
  3 ca giờ · 3 khoá · 4 kỳ thi · 12 phiếu · 12 thí sinh; 221 xmlid; nhóm Quản lý 1 người / Người dùng 0.
  3 sequence noupdate (`WJ-CRS/` số kế 5 · `WJ-EXR/%(y)s/` 17 · `WJ-EXS/%(y)s/` 6): prefix/padding/bước **khớp XML**,
  XML không có `number_next` ⇒ lần `-i` không reset số kế. Không có data noupdate nào khác ⇒ không có câu hỏi noupdate.
- DB đo (không đụng `wujia_tea_19`), gốc `wujia_f12base` (sau deploy F11 bằng code HEAD `fe20159`):
  - Seed bằng code HEAD (`scratchpad/f12/seed_f12.py`): khoá published + nháp + lưu trữ; 7 kỳ thi (mở, đầy, quá hạn, đóng,
    huỷ, nháp, đã công bố kết quả); phiếu chờ duyệt/từ chối/huỷ/đã có kết quả; thí sinh có ảnh/không ảnh; phiếu của
    cửa hàng 2; `anh.owner` (1 cửa hàng) và `dung.multi` (3 cửa hàng).
  - `wujia_f12`: chụp trước → deploy F12 → chụp sau. `wujia_f12_h`: cùng lần seed, server HEAD (worktree) để so HTML.
  - `wujia_f12s`: suite · `wujia_f12ctl`: test portal mới trên code HEAD · `wujia_f12alone`: DB trắng ·
    `wujia_f12m`: giống UAT có mobile (cài HEAD rồi chạy lệnh deploy) · `wujia_f12t`: mutation.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `custom/wujia_exam/` (mới, L2, depend `mail, wujia_franchise`) | `git mv` 5 model, 2 nhóm quyền + privilege, ACL, 2 rule, 3 sequence, 4 view + menu backend, `test_c10_quota`. ACL + menu đổi ref nhóm sang cục bộ. `.po` 216 mục. Manifest `19.0.1.0.0` + `pre_init_hook` |
| `wujia_exam/hooks.py` | `imd_names(MODELS, extra=[privilege, 2 nhóm, 7 menu])` + `migrate_ownership` |
| View backend | `groups=` trong arch của 3 form (10 nút) đổi `group_exam_manager` → **`wujia_exam.group_exam_manager`** (xem "Bẫy groups trong arch") |
| Model | Session: `_effective_max_per_registration` (**nguồn duy nhất**: ca thi, trống thì khoá — dùng cho hướng dẫn, chặn portal và constraint) · `_portal_in_deadline` · `_portal_is_selectable` · `_portal_slot_status` (closed/expired/full/open). Course: `_portal_published` · `_portal_day_states` (trạng thái từng ngày trong tháng, tôn trọng horizon) · `_portal_sessions_on` · `_portal_booking_meta`. Registration: `_portal_scope_domain` · `_portal_result_counts` · **`register_from_portal`** (kiểm khoá published, 1 ≤ số người ≤ max, dựng dòng, tìm membership, savepoint + `flush_all`) + lớp lỗi `ExamPortalError(kind)` phân biệt `not_found`/`validation`. Line: `_portal_scope_domain` · `_portal_prepare_vals` (SĐT, năm sinh, ảnh) · `_portal_clean_photo` (MIME, 5 MB, `image_process`) |
| `_check_participant_bounds` | Đọc `session._effective_max_per_registration()` thay vì chỉ field của ca (chủ dự án chốt) |
| `wujia_portal_exam` | Còn controller + 3 QWeb + 2 mục nav + CSS/JS. Depend `wujia_portal_base, wujia_exam`. `19.0.6.0.0`. `.po` 177 mục. `migrations/` cũ để nguyên |
| Controller | Parse tham số → gọi model → render/JSON. **729 → 558 dòng**. Nhãn khung giờ (`SLOT_STATUS_LABELS`), `_max_hint`, bảng badge, mapper `_m_*`/`_pc_*` ở lại portal. Không còn `create`/`flush`/`savepoint`/`image_process`/`PHONE_RE` |
| Mobile anh Thái `wujia_mobile_portal_exam` | Depend `wujia_portal_exam` → `wujia_exam`; 18 dòng `wujia_portal_exam.` → `wujia_exam.` (4 view XML + test); `19.0.1.0.1`. Không đổi gì khác |
| A2 | `portal_base` không có bảng badge exam ⇒ không có gì phải dời |
| Test | `wujia_exam`: `test_c10_quota` (dời, quota qua model; test chặn server dùng ca để trống ⇒ khoá chặn) + `test_portal_rules` (7: trạng thái khung giờ, lịch tháng + horizon, meta đầy/đóng, tạo phiếu, từ chối đầu vào, lỗi nghiệp vụ rollback, đếm kết quả) + `test_split_ownership`. Fixture `ExamCommon` dùng chung. Portal: `test_portal_exam_f12` 5 HttpCase (hướng dẫn tối đa, lịch + khung giờ JSON, gửi phiếu → redirect chi tiết + ảnh, 5 mã lỗi + câu báo + rollback, cửa hàng khác 303/404) |
| `check_layers.py`, `deploy.yml`, `reseed_full.sh/.ps1` | `wujia_exam` = L2, `PENDING_SPLIT` chỉ còn `return`; thêm vào `-i/-u` và reseed. `test_sprint32.py` không có exam |

C4: phạm vi portal của thi là **theo cửa hàng** (`franchise_id` phiếu/dòng) — gom về `_portal_scope_domain` hai model,
controller không còn tự ghép domain.

## Ma trận nghiệm thu

| # | Yêu cầu (prompt F8–F13) | Bằng chứng | KQ |
|---|---|---|---|
| 1 | `wujia_exam` nhận model, view backend, menu, **group**, rule, sequence, i18n phần model | `git mv`. DB trắng chỉ `wujia_core, wujia_franchise, wujia_exam` (cài rồi `-u --test-tags /wujia_exam`): **13/13** | ✅ |
| 2 | `pre_init_hook` đổi chủ xmlid | Log `{'ir_model_data': 214, 'ir_model_constraint': 30, 'ir_model_relation': 1}`. Module cũ còn đúng 5 view: `portal_exam_{schedule,register,registration_detail}`, `layout_sidenav_exam`, `mobile_bottomnav_exam` | ✅ |
| 3 | Đo trước/sau: record, **user trong group**, sequence, menu/action, rule | `split_snapshot --diff --rename`: **245 dòng đổi chủ**. Bản ghi 5 model md5 giống hệt · 3 sequence **kèm `last_value`** giữ · người trong 2 nhóm giữ. 3 lệch có giải trình: arch 3 form backend, chỉ khác tên module trong `groups=` (sửa cố ý, bẫy bên dưới) | ✅ |
| 4 | Sửa mọi tham chiếu `wujia_portal_exam.*` ở module khác | Mobile Thái: depend + 18 dòng ref action/view/group (F8-style). Còn lại chỉ trỏ QWeb/controller ở lại portal (4 test quét của `portal_base`) — đúng | ✅ |
| 5 | Lượt mỏng: luật controller về model (`register_from_portal`, phạm vi, quota) | Controller không còn tạo phiếu, savepoint, kiểm SĐT/ảnh, ghép domain; lịch/khung giờ/meta khoá gọi method model. `grep create\|flush\|savepoint\|image_process\|PHONE_RE` controller = 0 | ✅ |
| 6 | Response/redirect/thông điệp giữ nguyên | Server HEAD (`wujia_f12_h`) ‖ F12 (`wujia_f12`), cùng lần seed, 3 phiên (`anh.owner` · `dung.multi` chưa chọn · `dung.multi` cửa hàng 2), chuẩn hoá hash asset + csrf + `registry_hash`: **234/234 giống từng byte, chạy 2 lần** — 36 GET (danh sách lọc/trang/limit rác/ngày ngược/rác, trang đăng ký theo khoá/tháng/khoá nháp/không tồn tại, 8 chi tiết gồm cửa hàng khác, 4 ảnh gồm cửa hàng khác) + 15 JSON lịch/khung giờ (tháng có/không ca, khoá nháp/lưu trữ/0, ngày sai định dạng) + **19 nhánh gửi phiếu** (ca 0/nháp/đầy/quá hạn/đóng/huỷ, 0 người, thiếu key, quá max, SĐT/tên/năm sinh sai, ảnh sai MIME/hỏng/không phải ảnh/thiếu dữ liệu, 2 lượt thành công) + đọc lại sau ghi. DB sau lượt ghi giống hệt | ✅ |
| 7 | Test cũ xanh (run đối chứng) | Focused `wujia_exam,wujia_portal_exam,wujia_mobile_portal_exam` **49/49**. Suite 16 `wujia_portal_*` + 6 module tách: **897, 0 đỏ, 0 ERROR**. Đối chứng: 5 HttpCase portal mới chạy trên code HEAD ⇒ **xanh hết** ⇒ route thi không đổi hành vi | ✅ |
| 8 | `check_layers` không còn vi phạm của exam | **0 vi phạm tầng** (lần đầu từ khi có script); R7 giữ 2 (anh Thái); `PENDING_SPLIT` chỉ còn `wujia_portal_return` | ✅ |
| 9 | Deploy một lệnh | DB giống UAT (có `wujia_mobile_core` + `wujia_mobile_portal_exam`, cài bằng HEAD): `-i wujia_exam -u wujia_portal_exam,wujia_mobile_portal_exam` → exit 0, 0 ERROR, không action trùng; test mobile 3/3 | ✅ |

## Bẫy `groups` trong arch view (phát hiện ở F12)

- ACL csv và `<menuitem groups="...">` đổi sang tên cục bộ được (loader dùng `ref()`, tự thêm module đang nạp).
- **`groups=` trên phần tử trong arch view thì không**: Odoo 19 parse bằng
  `res.groups._get_group_definitions().parse(..., raise_if_not_found=False)` — tên thiếu tiền tố không khớp nhóm nào và
  **bị bỏ qua im lặng** ⇒ phần tử bị ẩn với mọi người, kể cả Administrator. Đo: `group_exam_manager` → manager=False,
  `wujia_exam.group_exam_manager` → True. Snapshot bắt được (md5 arch 3 form lệch) trước khi thấy trên màn.
- Đã soát F8–F11: chỉ có `menuitem groups=` ⇒ sạch. Luật cho F13: **`groups=` trong arch luôn ghi đủ `module.xmlid`**.

## Mutation

| # | Phá | Kết quả (test `wujia_exam` + `wujia_portal_exam`) |
|---|---|---|
| M1 | Max/phiếu bỏ rơi về khoá (chỉ đọc ca) | 5 đỏ |
| M2 | Chọn được ca bỏ kiểm còn chỗ | 4 đỏ |
| M3 | Trạng thái khung giờ bỏ kiểm hạn đăng ký | 2 đỏ |
| M4 | `register_from_portal` bỏ savepoint | 2 đỏ (rollback) |
| M5 | Ảnh thí sinh bỏ phạm vi cửa hàng | 1 đỏ (`test_other_store_is_out_of_scope` — sau khi cho dòng cửa hàng khác có ảnh; bản đầu không bắt) |
| M6 | Constraint quay về chỉ đọc field ca thi | 1 đỏ (`test_server_rejects_over_limit`) |

## Playwright (không gửi phiếu)

PC 1440 + mobile 390, 12 màn (danh sách, lọc, trang đăng ký, chọn ngày, khung giờ, chi tiết có ảnh): 0 tràn ngang; lỗi
duy nhất 404 `/app-assets/data/locales/en.json` (có cả trên HEAD).

## Còn mở

1. **Báo anh Thái trước deploy**: `wujia_mobile_portal_exam` đã đổi depend + ref sang `wujia_exam` (18 dòng, `19.0.1.0.1`).
2. Chờ deploy UAT (chủ dự án). Lệnh: `-i wujia_exam -u wujia_portal_exam,wujia_mobile_portal_exam`. Sau deploy đo
   chỉ-đọc: 3 version (`wujia_exam 19.0.1.0.0` · `portal_exam 19.0.6.0.0` · `mobile_portal_exam 19.0.1.0.1`), module mới
   ~216 xmlid (214 + `rating_ids` như F8–F11), portal còn 5 view, số kế `WJ-EXR` **17** · `WJ-CRS` **5** · `WJ-EXS` **6**,
   nhóm Quản lý 1 người, 10 nút form backend hiện với Quản lý, portal `/portal/exam` 200.
3. Phát hiện có từ trước (không thuộc F12, HEAD cũng vậy): tiêu đề PC "Khung giờ ngày —" không điền ngày sau khi chọn.
   Ghi lại, hỏi BA nếu cần.
4. `migrations/` cũ của portal để nguyên (đã chạy trên UAT).

## Lệnh chạy lại

```bash
W=~/odoo-dev/WujiaTea; PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3
createdb -h 127.0.0.1 -U odoo19 -T wujia_f12base wujia_f12      # + cp filestore; seed_f12.py bằng code HEAD
python3 $W/scripts/qa/split_snapshot.py --db wujia_f12 --host 127.0.0.1 --user odoo19 \
  --modules wujia_portal_exam,wujia_exam \
  --models wujia.exam.course,wujia.exam.session,wujia.exam.time.slot,wujia.exam.registration,wujia.exam.registration.line \
  --seq wujia.exam.course,wujia.exam.session,wujia.exam.registration -o before.json
cd $W/odoo19 && $PY odoo-bin -c <conf> -d wujia_f12 --stop-after-init \
  -i wujia_exam -u wujia_portal_exam,wujia_mobile_portal_exam                                     # 0 ERROR
python3 $W/scripts/qa/split_snapshot.py ... -o after.json && python3 $W/scripts/qa/split_snapshot.py \
  --diff before.json after.json --rename wujia_portal_exam=wujia_exam                        # 245 đổi chủ, 3 lệch (groups arch)
$PY odoo-bin ... --http-port 8093 --gevent-port 8094 --stop-after-init --test-enable \
  --test-tags /wujia_exam,/wujia_portal_exam,/wujia_mobile_portal_exam -u wujia_exam,wujia_portal_exam,wujia_mobile_portal_exam  # 49/0
# DB trắng: -i wujia_exam (không --test-enable) rồi -u wujia_exam --test-enable --test-tags /wujia_exam     # 13/0
python3 $W/scripts/qa/check_layers.py                                                           # 0 vi phạm
```
So HTML: `scratchpad/f12/cmp_http.py` (8097 HEAD ‖ 8098 F12). Mutation: `scratchpad/f12/mutate.py`. Xoá `ir_attachment`
`/web/assets/%` trên DB copy trước khi chạy server (bài học F9).
