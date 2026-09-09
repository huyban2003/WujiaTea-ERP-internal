# Merge nhánh `thai` đợt 3 — 09/09/2026

**Nhánh:** `dev/2026-09-09-merge-thai-3` · `origin/thai` `fa77114` (2 commit: `61c45f6` *update clear
code*, `fa77114` *them module wujia_franchise_contract*) · **merge sạch, 0 conflict**
(`git merge-tree` RC=0 trước khi merge thật).

**Quy mô:** 33 file, +1608 / −1593. Một module **MỚI** (`wujia_franchise_contract`), hai module
hiện có bị sửa (`wujia_franchise`, `wujia_franchise_inspection`).

**Chốt của chủ dự án 09/09: merge + push `main`, KHÔNG cài. Chủ dự án tự cài trên server.**

---

## 1. Nghiệm thu đã chạy (bản sao cô lập)

DB `wujia_tea_mt3` (copy của `wujia_tea_thai` — DB duy nhất có `wujia_franchise_inspection`
installed), cổng **8073**, KHÔNG đụng `wujia_tea_19`/8019.

| Phép kiểm | Kết quả |
|---|---|
| `-u wujia_franchise,wujia_franchise_inspection --stop-after-init` | **RC=0**, 0 lỗi Odoo (4 dòng ERROR trong log là docutils parse mô tả manifest, không phải lỗi) |
| `--test-enable` (220 test) | **0 failed, 3 error** — cả 3 là `setUpClass` của **test mới của anh Thái**, xem mục 2 |
| `wujia_franchise_contract` sau khi chạy | vẫn **`uninstalled`** đúng chủ ý |

⚠️ **Bẫy harness đã trả giá, ghi để khỏi lặp:** lần chạy đầu ra **24 failed + 15 error**. Không
phải hồi quy — `config/odoo.conf` có `dbfilter = ^wujia_tea_19$`, nên mọi test HTTP đăng nhập vào
`wujia_tea_mt3` **bị đá session ra** (`Logged into database 'wujia_tea_mt3', but dbfilter rejects
it`) và đọc phải trang login. Sửa `dbfilter` trong config tạm ⇒ **24 failed + 15 error → 0 failed +
3 error**. Cùng họ bẫy "đo rỗng vì redirect về `/web/login` mà vẫn trả 200" của đợt merge 22/08:
**mọi DB copy phải sửa `dbfilter` trước khi chạy test HTTP.**

---

## 2. Ba lỗi trong test MỚI của anh Thái (production code không bị)

Cả ba đều đỏ ở `setUpClass`, tức fixture của test, không phải mã chạy thật. `-u` **không** kèm
`--test-enable` vẫn RC=0.

1. `tests/test_franchise_inspection.py:20` và `tests/test_supervision_schedule.py` — tạo cửa hàng
   **không có `partner_id`** ⇒ vướng constraint `_check_partner_required_when_active`
   (`wujia_franchise/models/wujia_franchise_management.py:209`, ràng buộc của cụm C1 trên `main`).
2. `tests/test_inspection_access.py:21` — dùng **`groups_id`** trên `res.users`; Odoo 19 đã đổi tên
   thành **`group_ids`** ⇒ `ValueError: Invalid field 'groups_id' in 'res.users'`. Test viết theo
   API Odoo 17/18.

**Không sửa** theo luật thường trực (không đụng hai module Khảo sát của anh Thái). Đề nghị chuyển
nguyên hai điểm này cho anh Thái.

> ⚠️ Hệ quả deploy: nếu server chạy `-u wujia_franchise_inspection` **kèm** `--test-enable` thì sẽ
> đỏ. Deploy thường (không bật test) không ảnh hưởng.

---

## 3. 🔴 Rủi ro phải quyết TRƯỚC khi `-i wujia_franchise_contract`

`wujia_franchise_contract/models/wujia_franchise_management.py` `_inherit` cửa hàng và **đổi bản
chất hai trường**:

```
franchise_start_date = fields.Date(compute='_compute_contract_dates', store=True, readonly=True)
franchise_end_date   = fields.Date(compute='_compute_contract_dates', store=True, readonly=True)
```

Trên `main` hai trường này là `Date` thường và **đang bị GHI** ở:

- `wujia_franchise/wizards/franchise_onboarding_wizard.py` — wizard *Onboarding cửa hàng* của
  Sprint 57 (`WJ-FRANCHISE-003`, đã nghiệm thu trên UAT);
- `wujia_franchise/models/wujia_franchise_management.py:371` — nạp CSV bootstrap;
- `wujia_portal_base/data/sample_data.xml`;
- ~8 file test (`wujia_portal_*`, `wujia_account`, `wujia_franchise/tests/test_franchise_onboarding.py`).

⇒ **Cài module này là làm hỏng luồng onboarding và bộ test hiện có**, vì ngày hợp đồng khi đó chỉ
còn được sinh ra từ bản ghi `wujia.franchise.contract`. Muốn cài thì phải sửa wizard onboarding
sang **tạo một hợp đồng** thay vì ghi thẳng hai trường — đây là một lượt việc riêng, không phải
thao tác deploy.

Module có `post_init_hook` (`_migrate_legacy_franchise_contracts`) tự dựng hợp đồng từ ngày cũ của
Store, nên dữ liệu sẵn có không mất.

**Liên hệ Issue List:** đây chính là lời giải cho **`WJ-FRANCHISE-004`** (STT 135, *"mỗi Store chỉ
thể hiện được một kỳ hợp đồng"*), hiện vẫn **`Ready for Dev`**. Dev **không tự đóng** — chờ chủ dự
án/BA chốt ai là chủ issue.

---

## 4. Bốn điểm review khác

1. ✅ **Gỡ `supervision_user_id` khỏi `wujia_franchise` là ĐÚNG** — trường đã có chủ mới ở
   `wujia_franchise_inspection/models/wujia_franchise_management.py:9` (đúng hướng tách module của
   `f11dba6`). Grep `custom/wujia_franchise/` còn **0** tham chiếu treo ngoài `.po`/`.csv`.
2. 🟡 **Xoá `wujia_franchise_inspection/data/wujia_franchise_export.csv` (1376 dòng) làm mất bản
   dịch trang khảo sát.** `controllers/main.py:13` vẫn trỏ **đúng đường dẫn file vừa bị xoá**;
   hàm bọc trong `os.path.exists()` nên không vỡ, nhưng `trans_map` **rỗng** ⇒ trang khảo sát và
   báo cáo xuất ra rơi hết về nhãn mặc định ở `vi/zh/th`
   (6 chỗ gọi: `controllers/main.py:158`, `models/wujia_franchise_inspection.py:1467-69,1476,2322`).
   Bản `.po` mới thêm trong cùng commit chỉ có **9 chuỗi màn hình cài đặt Google Drive**, không
   thay được bảng 1376 dòng. Bản còn sống `wujia_franchise/data/wujia_franchise_export.csv` là
   **tập con** (1355 dòng, thiếu đúng 21 dòng riêng của khảo sát). **Xin hỏi anh Thái xem có cố ý
   không** — không tự sửa theo luật.
3. 🟡 **Manifest thêm `external_dependencies.python`:** `google-api-python-client`, `google-auth`,
   `google-auth-oauthlib`, `google-auth-httplib2`. Máy dev có đủ 4 gói. **Nếu python của server
   thiếu một gói thì `-u wujia_franchise_inspection` sẽ BỊ TỪ CHỐI** (*external dependency not
   met*) — kiểm trước khi deploy.
4. 🟡 **ACL của module hợp đồng cho `base.group_portal` quyền ĐỌC mọi hợp đồng, không có `ir.rule`.**
   Hiện chưa có route portal nào đọc model này nên chưa lộ ra, nhưng đúng chuẩn thì hoặc bỏ dòng
   ACL portal, hoặc thêm record rule giới hạn theo cửa hàng của người dùng. 3 dòng ACL còn lại đều
   có `group_id` ✅, `res.groups` khai đúng `privilege_id` của Odoo 19.
5. 🟡 **Hai module đổi mã mà KHÔNG bump version** (`wujia_franchise` giữ `19.0.5.0.0`,
   `wujia_franchise_inspection` giữ `19.0.1.0.0`) ⇒ `git pull` + restart **không** nạp lại XML/asset
   của chúng, và mất phép kiểm deploy bằng số phiên bản qua XML-RPC. Vì vậy lệnh deploy dưới đây
   gọi **đích danh** `-u`, đừng trông vào `-u all`.

---

## 5. Lệnh chủ dự án chạy trên server

```bat
:: 1) Cập nhật hai module đã đổi mã (BẮT BUỘC gọi đích danh — không bump version)
python odoo-bin -c <conf> -d <db> -u wujia_franchise,wujia_franchise_inspection --stop-after-init

:: 2) Module MỚI: chỉ cài sau khi đã quyết mục 3 ở trên
python odoo-bin -c <conf> -d <db> -i wujia_franchise_contract --stop-after-init
```

Kiểm sau deploy bằng XML-RPC như thường lệ: `ir.module.module` của
`wujia_franchise` / `wujia_franchise_inspection` / `wujia_franchise_contract`.
