# WJ-FRANCHISE-003 (STT 134) — Bảng nghiệm thu

Đối chiếu **từng gạch đầu dòng** cột `Kết quả mong muốn` của chính issue trên tab `5. Issue List`.
Bằng chứng = test tự động trên DB copy cô lập `wujia_tea_f003` (bản sao `wujia_tea_19`, cổng 8034,
KHÔNG đụng 8019) + đọc mã nguồn + đo chỉ-đọc trên UAT.

Sprint: `2026-09-04-WJ-FRANCHISE-003` · module `wujia_franchise` `19.0.3.1.1` → `19.0.4.0.0`.

## A. GIVEN HQ tạo mới cửa hàng từ Franchise Management

| # | Yêu cầu BA | Đo được | Kết quả |
|---|---|---|---|
| A1a | Store được tạo ở Draft | `default='draft'`; `test_store_created_in_draft`, `test_default_status_is_draft` | Pass |
| A1b | …và chưa cho phát sinh giao dịch | Portal đã chặn `status != 'active'` (`wujia_portal_base/controllers/portal.py:549`). Backend **không** chặn tạo/xác nhận đơn cho store Draft | **Partial — LIMIT 1** |
| A2 | HQ chọn được *Tạo Store Partner mới* hoặc *Liên kết Partner đã có* | `partner_mode` radio 2 nhánh trong wizard | Pass |
| A3a | Hệ thống tự liên kết đúng `partner_id` | `_resolve_store_partner()` gán thẳng vào `franchise.partner_id`; `test_store_created_in_draft` assert `store.partner_id` | Pass |
| A3b | Cảnh báo dữ liệu trùng | `_find_duplicate_partners()` (name / phone 8 số cuối / email / VAT) + chặn tới khi HQ tick xác nhận; `test_duplicate_partner_blocks_until_acknowledged` | Pass |
| A3c | Cảnh báo mapping không rõ | `partner_warning` dùng lại `_wujia_franchise_mapping()` (C1); `test_existing_partner_warning_when_already_store_partner` | Pass |
| A3d | Không tạo Partner trùng khi thao tác lại | Chạy lại wizard trên store đã có partner ⇒ bỏ qua bước partner; `test_partner_created_once_on_rerun` (số partner cùng tên **không đổi**) | Pass |
| A4 | Store Partner là chủ thể giao dịch/công nợ | `partner_id` giữ nguyên vai trò cũ, `res.partner._wujia_unique_franchise()` (C1) không đổi dòng nào | Pass |

## B. WHEN chọn *Tạo Portal User mới*

| # | Yêu cầu BA | Đo được | Kết quả |
|---|---|---|---|
| B1a | Kiểm tra login/email trùng | `_find_existing_account()` 1 query trên login **và** email, kể cả user archive; `test_duplicate_login_blocked`, `test_duplicate_email_blocked` | Pass |
| B1b | Tạo contact cá nhân + `res.users` **chỉ** quyền Portal | `test_new_portal_user_shape`: `has_group('base.group_portal')` True, `has_group('base.group_user')` False | Pass |
| B1c | Tạo **đúng một** membership với Store/role | `_apply()` tạo 1 dòng; constraint `_check_unique_active` chặn dòng thứ hai; `test_duplicate_membership_blocked` | Pass |
| B2 | Không yêu cầu bật debug hoặc chọn User Type kỹ thuật | Wizard **không có** field user type; vào bằng menu *Operations → Store Onboarding* hoặc nút trên form Store | Pass |
| B3 | `res.users.partner_id` không bị gán thành Store Partner | `test_new_portal_user_shape`: `partner_id.parent_id` rỗng và `!=` Store Partner | Pass |

## C. WHEN chọn *Dùng Portal User đã có*

| # | Yêu cầu BA | Đo được | Kết quả |
|---|---|---|---|
| C1a | Tìm đúng user, kiểm là Portal User | `_validate()` nhánh `existing` kiểm `group_portal`; user không phải portal ⇒ `UserError` | Pass |
| C1b | Không tạo user mới | Nhánh `existing` không gọi `_create_portal_user()`; `test_duplicate_login_blocked` assert số user không tăng | Pass |
| C1c | Chỉ tạo membership chưa tồn tại | `test_duplicate_membership_blocked`: số membership **không đổi** sau khi thao tác lại | Pass |
| C2a | Internal User ⇒ block/cảnh báo rõ, không tự sửa quyền | `test_internal_user_blocked_without_group_change`: thông báo chứa "Internal User", `group_ids` **y nguyên** | Pass |
| C2b | User đã archive ⇒ block | `test_archived_user_blocked` | Pass |
| C2c | Membership trùng ⇒ block | `test_duplicate_membership_blocked` | Pass |

## D. WHEN HQ Activate Store

| # | Yêu cầu BA | Đo được | Kết quả |
|---|---|---|---|
| D1a | Chỉ Active khi có Store Partner hợp lệ | `_assert_ready_to_activate()`; `test_activate_requires_partner_and_owner` | Pass |
| D1b | …và ít nhất một Owner/membership hiệu lực | Dùng lại compute `main_owner_member_id`; `test_activate_blocked_when_owner_missing` (store có partner nhưng chỉ có staff ⇒ chặn, giữ Draft) | Pass |
| D2 | Thao tác lỗi giữ Store ở Draft, không dữ liệu nửa vời | Toàn bộ validate chạy **trước** mọi `create` (`action_confirm` = `_validate()` rồi mới execute); `test_failing_line_creates_nothing`: không còn Store lẫn user mồ côi | Pass |
| D3 | Chỉ HQ có quyền tạo/đổi/thu hồi membership | ACL: chỉ `group_franchise_manager` write/create/unlink `wujia.franchise.member` và wizard; `_assert_hq()`; `test_non_hq_user_blocked` | Pass |
| D4 | Mật khẩu tiếp tục do HQ đổi tay tại Users | Wizard tạo user với `no_reset_password=True` ⇒ **không** gửi mail, **không** đặt mật khẩu | Pass |
| D5 | Không thay đổi mô hình hợp đồng | `franchise_start_date` / `franchise_end_date` giữ nguyên trên `wujia.franchise.management`, 0 dòng đổi | Pass |

## Tổng kết

**Pass 21 / 22 gạch đầu dòng, 1 Partial ⇒ 21,5/22 = 97,7%** (ngưỡng ≥90%).

## Build & hồi quy

| Hạng mục | Kết quả |
|---|---|
| `-u wujia_franchise --stop-after-init` (DB copy `wujia_tea_f003`) | RC=0, 0 Traceback |
| Test mới `--test-tags wujia_franchise_onboarding` | **18 test, 0 failed / 0 error** |
| Mutation check (7 guard) | Mỗi lần gỡ 1 guard ⇒ đúng test tương ứng đỏ (draft status · duplicate partner ack · duplicate login · duplicate email · internal user · activate gate · validate-before-execute) |
| Hồi quy 13 module (`--test-enable`) — code **có** thay đổi | `0 failed, 7 error(s) of 299` |
| Đối chứng cùng lệnh, code **chưa** có thay đổi (stash) | `0 failed, 7 error(s) of 282` |
| Kết luận | **7 error giống hệt ⇒ có sẵn**, do `wujia_portal_inspection` chưa cài trên DB này (test D3 `env.ref` xmlid module đó). 282 test cũ **không đổi**, +18 test mới xanh |

## Đo chỉ-đọc trên UAT trước khi bật gate (XML-RPC, không ghi gì)

`http://113.161.187.126:8019/` — 3 cửa hàng, **tất cả đang `active`**, 0 store thiếu Store Partner,
**1 store (`HN-02`) thiếu Owner hợp lệ**. Vì gate đặt ở nút `Activate` chứ không phải `@api.constrains`
(bài học L12), `HN-02` **vẫn hoạt động bình thường** và vẫn sửa được; chỉ khi HQ khoá rồi bấm Activate
lại mới bị chặn cho tới khi gán Owner.

## Kiểm trên trình duyệt sau khi deploy UAT (04/09, chỉ đọc — không ghi dữ liệu)

Đăng nhập backend UAT bằng Chromium 1600×1000, mở màn onboarding qua menu và qua nút trên cửa hàng:

| Điểm kiểm | Đo được | Kết quả |
|---|---|---|
| Module đã lên UAT | `wujia_franchise 19.0.4.0.0`, trạng thái `installed` | Đạt |
| Menu *Vận hành → Onboarding cửa hàng* | có, chỉ nhóm HQ thấy | Đạt |
| Một màn duy nhất, đủ 3 khối | Cửa hàng · Đối tác · Người dùng, cùng một hộp thoại | Đạt |
| Không phải chọn loại tài khoản kỹ thuật | 0 ô `share` / `group_ids` / `user_type` trên màn | Đạt |
| Không cần bật chế độ debug | mở thẳng từ menu, không qua Cài đặt | Đạt |
| Mở từ cửa hàng đã có | tự ẩn khối Cửa hàng + Đối tác, chỉ còn khối Người dùng | Đạt |
| Nút *Store onboarding* ẩn khi cửa hàng đã Active | đúng | Đạt |
| Xác nhận khi chưa nhập người dùng nào | báo *"Please add at least one store user."*, **không ghi gì** (số cửa hàng/membership/tài khoản/đối tác trước và sau đều là 3 / 9 / 6 / 11) | Đạt |
| Lỗi JavaScript | 0 | Đạt |
| Tràn ngang | không | Đạt |
| **Ngôn ngữ màn hình** | **hiện tiếng Anh giữa backend tiếng Việt** | **Không đạt → đã sửa** |

Chỗ không đạt đã xử lý ngay trong phiên: bổ sung bản dịch tiếng Việt vào mã nguồn
(`i18n/vi_VN.po` + `wujia_franchise.pot`), bỏ đánh số "1./2./3." ở tiêu đề khối, và đổi tiêu đề hộp
thoại theo chế độ. Đo lại trên bản sao database cô lập: **0 nhãn nào còn chưa dịch**, bộ test
**18/18 đạt**, cập nhật module RC=0. Đóng gói ở phiên bản `19.0.4.0.1`, **cần deploy lại UAT**.

> Ghi chú kỹ thuật cho lần sau: file `.po` của Odoo 19 được **ghép với file `.pot` cùng thư mục** lúc
> nạp — mọi chuỗi chỉ thêm vào `.po` mà thiếu trong `.pot` đều bị coi là lỗi thời và **bỏ qua im lặng**.
> Phải thêm vào cả hai file. Ngoài ra dạng tham chiếu `menu:<module>.<xmlid>` không còn hợp lệ, phải
> dùng `model:ir.ui.menu,name:<module>.<xmlid>`.
>
> Lượt kiểm sau khi deploy `19.0.4.0.1` còn bắt thêm hai chỗ: nút *Cancel* và tiêu đề hộp thoại vẫn
> tiếng Anh. Nguyên nhân: câu sinh ra từ **mã Python** chỉ được dịch khi mục trong `.po` có thêm dòng
> chú thích `#. odoo-python` — thiếu dòng đó thì Odoo bỏ qua, kể cả khi tham chiếu `code:` đã đúng.
> Đã bổ sung cho 27 mục và đóng gói lại ở `19.0.4.0.2`.

## LIMIT

1. **Store `Draft` chỉ bị chặn ở Portal.** Backend vẫn tạo/xác nhận được đơn hàng và ghi sổ hoá đơn cho
   cửa hàng Draft. Chủ dự án chốt không đụng `sale.order.action_confirm` / `account.move.action_post`
   để tránh hồi quy cụm C1/C2. Nếu BA muốn chặn cả backend, mở issue riêng.
2. **Ảnh QR / mật khẩu / email chào mừng** ngoài phạm vi — đúng điểm 8 của BA: HQ tự đổi mật khẩu tại
   Settings → Users và báo cửa hàng thủ công.
3. **Dò trùng partner theo số điện thoại** so 8 chữ số cuối. Odoo 19 **không còn** field `mobile` trên
   `res.partner` nên không dò được cột đó.
4. **Chưa retest trên UAT bằng thao tác thật** (phần nhìn đã kiểm, xem bảng trên) — theo giới hạn QA, phiên này không tạo cửa hàng/tài
   khoản thật trên UAT. Cần BA retest sau khi deploy.
5. **`wujia_franchise_inspection.py:1772` vẫn tự sinh portal user** bằng cách so khớp theo TÊN rồi đặt
   login ngẫu nhiên `@wujiatea.internal`. Đây là một nguồn sinh user trùng khác, nằm ở luồng khảo sát
   nên **không sửa trong issue này** — xem `wj-franchise-003-dev-decisions.md` mục 11.
