# Review nhánh `thai` — tách module Khảo sát (`wujia_franchise_inspection`)

**Ngày:** 2026-09-08 · **Nhánh review:** `origin/thai` @ `fbc7945` (20 commit, 77 file)
**Nhánh tích hợp:** `dev/2026-09-08-merge-thai-3` · **Kết quả:** đã merge, đã vá 4 điểm chặn, đã đo trên
CSDL bản sao cô lập `wujia_tea_thai`. **Chưa lên `main`, chưa lên UAT.**

## 1. Đánh giá chung

Việc tách phân hệ Khảo sát ra module riêng là **đúng hướng** — `wujia_franchise` trước đó gánh cả quản lý
cửa hàng lẫn khảo sát. Phần tính năng mới (GPS, chữ ký điện tử, video Google Drive, import tiêu chí từ
Excel, màn báo cáo) là việc thật và cần thiết.

Bóc tách quy mô để khỏi hiểu nhầm con số 28.488 dòng: 15.471 dòng là `.po/.pot` máy tự sinh, 3.620 dòng
dữ liệu CSV/JSON, còn lại **2.203 dòng viết mới hoàn toàn** + **3.692 dòng nở ra từ code cũ**.

Phân quyền của module mới **làm đúng**: portal chỉ `read` trên cả 9 model, inspector/admin tách bạch.
Không có secret nào bị commit; `.gitignore` đã chặn `credentials.json` / `token.json`.

## 2. Bốn điểm CHẶN — đã vá ở nhánh tích hợp, ghi lại để tránh lặp

### 2.1 Ghi đè mất bản dịch đã nghiệm thu (nghiêm trọng nhất)

`i18n/vi_VN.po` của `wujia_franchise` bên nhánh `thai` được sinh lại ngày **29/08**, tức trước Sprint 57
(`d24bfe3` + `7568711`, 04/09 — bản `19.0.4.0.2` đã cài lên UAT và đo lại xác nhận). Commit merge
`3e89ef2` (07/09) giải quyết đụng độ bằng cách **giữ bản của nhánh `thai`**, nên:

* `Store onboarding → Onboarding cửa hàng` và `Add store users → Thêm người dùng cửa hàng` **mất hẳn**;
* tổng số câu dịch: main 506 → nhánh `thai` 298.

**Git không báo conflict** vì đụng độ đã được quyết trong commit merge. Đã khôi phục 51 câu về
`wujia_franchise` và trả 21 câu về `wujia_franchise_inspection`; 160 câu còn lại là **chuỗi lỗi thời thật
sự** (msgid không còn trong mã nguồn sau khi đổi nhãn menu) nên bỏ đúng.

> **Đề nghị:** trước khi merge `main` vào nhánh riêng, chạy `git log main -- <file>` cho các file `.po`
> và view; file nào `main` sửa sau ngày nhánh tách ra thì **lấy bản `main`** rồi sinh lại `.pot`.

### 2.2 Mất 2 nút Onboarding trên form Cửa hàng

`views/wujia_franchise_management_views.xml` bị gỡ `<button name="action_open_onboarding">` và
`<button name="action_open_add_members">` khỏi `<header>`. Method trong model, wizard, 18 test, ACL và
menu đều còn — chỉ mất đường vào từ form. `WJ-FRANCHISE-003` đang `Ready for Retest` (nghiệm thu 97,7%),
BA mở form sẽ báo mất tính năng. Đã trả lại nguyên trạng.

### 2.3 Không đánh số phiên bản khi rút ruột module

`wujia_franchise` giữ nguyên `19.0.4.0.2` dù bị gỡ 5 model, 11 view, 33 dòng ACL, 3 file security;
`wujia_portal_inspection` giữ nguyên `19.0.1.4.0` dù đổi `depends`. Hệ quả: `git pull` + restart **không
nạp lại XML**, và mất luôn phép kiểm "deploy đã ăn chưa" bằng số phiên bản qua XML-RPC — chính phép kiểm
đã bắt được 2 lần deploy hụt trong tháng 9.

Đã bump: `wujia_franchise` → **19.0.5.0.0**, `wujia_portal_inspection` → **19.0.1.5.0**.

### 2.4 Tách module không có bước chuyển quyền sở hữu bản ghi

Trên CSDL đang chạy, 9 model khảo sát + 2 nhóm quyền + 12 `ir.rule` + 33 dòng ACL vẫn ghi chủ là
`wujia_franchise` trong `ir_model_data`. Nếu cài module mới mà không đổi chủ trước:

* Odoo tạo **bản sao** xmlid dưới tên module mới, bản cũ bị `_process_end` dọn ⇒ **user rơi khỏi nhóm
  giám sát**, `ir.rule` biến mất;
* các dòng `ir.model` / `ir.model.fields` cũ bị dọn ⇒ **nguy cơ rơi bảng dữ liệu khảo sát**.

Đã bổ sung `wujia_franchise_inspection/hooks.py` chạy ở `pre_init_hook` (Odoo **không** chạy script
migration cho lần cài đầu), đổi cột `module` cho **98 xmlid + 12 field + toàn bộ `ir.model`/
`ir.model.fields`** của 2 tiền tố model. Đo thực tế: **434 bản ghi đổi chủ, 0 mất mát**.

## 3. Bốn điểm CHƯA sửa — gửi lại anh Thái

| # | Vấn đề | Vị trí | Hệ quả |
|---|---|---|---|
| 1 | `_bootstrap_franchise_data()` nạp dữ liệu cửa hàng/đối tác/nhân viên **thật** từ 4 file CSV khi cài module; dùng `except Exception` + **`print()`** thay vì `_logger`; guard là heuristic `search_count([]) < 100` | `wujia_franchise/models/wujia_franchise_management.py` (+203 dòng) | Dữ liệu vận hành đi kèm mã nguồn lên server; seed hỏng sẽ **im lặng** — đúng bệnh 3 seed chết âm thầm từ Sprint 41/42/K. `data/wujia_franchise_export.csv` (1.355 dòng) còn bị commit **trùng ở cả hai module** |
| 2 | Google Drive dùng `InstalledAppFlow` (OAuth mở trình duyệt); `credentials.json`/`token.json` đặt trong thư mục module; manifest **không khai `external_dependencies`** | `wujia_franchise_inspection/models/google_drive_client.py:27-70` | **Không chạy được trên service Windows headless**; file token **mất sau mỗi `git pull`**; thiếu thư viện thì lỗi chỉ lộ lúc chạy, không lộ lúc cài |
| 3 | Module mới **~21.000 dòng, 0 test**; 2.138 dòng JS viết tay **không dùng framework OWL** của Odoo, nhúng `<script src="...?v=">` thay vì asset bundle | `wujia_franchise_inspection/` | Không có gì bắt được hồi quy; nâng cấp Odoo về sau phải sửa tay; không dùng lại được component chung của Portal |
| 4 | Đổi hành vi ngoài phạm vi tách module: `wujia.franchise.member._rec_name` đổi `display_name` → `user_id`, **bỏ field store `display_name`** (từ `Tên @ Cửa hàng (Vai trò)` còn mỗi tên), thêm `_name_search`; hardcode chuỗi tiếng Việt `_('Chưa có tên')` trong mã nguồn tiếng Anh | `wujia_franchise/models/wujia_franchise_member.py` | Nhãn hiển thị của phân công đổi mà không ai yêu cầu; trái quy ước i18n Sprint 44 (nguồn EN, dịch qua `.po`) |

**Ba điểm nhỏ kèm theo:**

* `supervision_user_id` **khai ở cả hai module** (`wujia_franchise` bản trơ, module khảo sát bản có
  `domain`/`help`) — tách chưa dứt. Không gãy, nhưng nên dồn về một chỗ.
* Menu `Cài đặt & Google Drive` hardcode tiếng Việt trong XML, không dịch được.
* `wujia_franchise_menu.xml` còn khối comment vẽ cây menu cũ, đã lỗi thời sau khi tách.
* 4 dòng tham chiếu `#:` sai định dạng trong `.po` (thiếu tiền tố module) làm Odoo ghi `ERROR: malformed
  po file` mỗi lần nạp — có sẵn từ `main`, đã lọc ở phần chuyển sang module mới.

## 4. Bài học kỹ thuật đáng ghi (bẫy im lặng thứ tư của i18n Odoo 19)

Thêm câu dịch vào `.po` là **chưa đủ**. `PoFileReader.__init__` tự tìm file `.pot` cùng thư mục rồi gọi
`pofile.merge(pot)`, mà `merge` của polib **chỉ giữ entry có trong `.pot`**. `.pot` sinh ngày 29/08 không
có chuỗi Onboarding ⇒ 51 câu vừa thêm bị **lọc sạch, không một dòng log nào**; đo qua ORM vẫn ra tiếng
Anh trong khi `grep` thấy chuỗi nằm đúng trong file. **Phải vá `.po` VÀ `.pot` cùng lúc.**

## 5. Số đo nghiệm thu (CSDL bản sao `wujia_tea_thai`, nhân từ `wujia_tea_d4g` có phiếu thật)

Lệnh đo: `-i wujia_franchise_inspection -u wujia_franchise,wujia_portal_inspection` trong một lượt, sau
đó `-u` toàn bộ module `wujia_*` (trừ `wujia_portal_remediation` — cấm đụng).

| Phép đo | Trước | Sau | |
|---|---|---|---|
| Phiếu khảo sát / dòng chấm điểm | 1 / 2 | 1 / 2 | ✅ |
| Mẫu phiếu / câu hỏi / xếp loại | 1 / 15 / 4 | 1 / 15 / 4 | ✅ |
| Lịch giám sát | 1 | 1 | ✅ |
| User trong nhóm giám sát | 1 | 1 | ✅ |
| `ir.rule` khảo sát | 12 | 12 | ✅ |
| ACL khảo sát | 33 | 35 | ℹ +2 model mới |
| `ir.model` khảo sát | 11 | 12 | ℹ +1 model mới |
| xmlid đổi chủ sang module mới | 0 | 500 | ℹ 434 chuyển + 66 mới |
| 2 nút Onboarding trên form | — | có | ✅ |
| Tiêu đề wizard ở `lang=vi_VN` | — | *Onboarding cửa hàng* / *Thêm người dùng cửa hàng* | ✅ |
| Test `wujia_franchise` | — | **18/18, 0 failed 0 error** | ✅ |
| Route Portal | 14/14 = 200 | 14/14 = 200 | ✅ |
| Màn khảo sát `/franchise/inspection/do/1` | — | 200, phiếu giữ `need_remediation` + 2 dòng | ✅ |
| `ERROR`/`CRITICAL` khi nâng cấp | — | **0** | ✅ |

## 6. Lệnh deploy khi được duyệt lên UAT

```
git pull
python odoo-bin -c <conf> -d <db> -i wujia_franchise_inspection \
    -u wujia_franchise,wujia_portal_inspection --stop-after-init
```

`wujia_franchise_inspection` là **module hoàn toàn mới ⇒ bắt buộc `-i`**, restart không tự cài. Phải chạy
**một lượt** để `pre_init_hook` đổi chủ bản ghi trước khi Odoo dọn dữ liệu cũ. Sau deploy phải đo lại
chỉ-đọc trên chính UAT (số phiên bản + đếm phiếu khảo sát + user trong nhóm giám sát) rồi mới đánh dấu.
