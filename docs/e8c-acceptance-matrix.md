# E8c — Ma trận nghiệm thu · `UI-SIDEBAR-001` (STT 131, `CMP-SN-001`): avatar · mobile · chuông

Lượt cuối của cụm **E8**: E8a (`6bf64f7`) đo hiện trạng, E8b (`d354e2a`) làm sidebar PC + drawer 992–1199, E8c làm phần
còn lại của cột "Kết quả mong muốn" (avatar dropdown, sheet "Thêm" mobile, chuông, tên gọi PC↔mobile) rồi đưa issue lên
**Ready for Retest** sau khi đo UAT.

- Spec: tab `5. Issue List` dòng 131 (cột "Đề xuất điều chỉnh" + "Kết quả mong muốn") · `UI Component` CMP-SN-001 · CMP-GH-001.
- Chủ dự án chốt trong phiên (25/09):
  - **Ngôn ngữ giữ trên header cả PC lẫn mobile** (CMP-GH-001 GlobalHeader = logo/ngôn ngữ/cart/avatar), **và** avatar có
    thêm nhóm Ngôn ngữ (đủ 7 mục theo issue). Chốt E8a "gỡ dropdown ngôn ngữ topbar" huỷ.
  - "Thông tin cửa hàng" → **"Hồ sơ cửa hàng"** ở menu **và** tiêu đề trang `/portal/franchise-information`.
- Đo: DB local `wujia_e4b1`, server 8090, test 8098. Tài khoản `em.hcm` (owner HCM-01), `cuong.staff` (staff),
  `dung.multi` (cookie cửa hàng 1 = staff, 2 = manager; 2 cửa hàng ⇒ có "Đổi cửa hàng").
- Không đổi controller logic / model / dữ liệu / quyền route — chỉ template, CSS, 1 file JS, 2 tiêu đề trang.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `wujia_portal_layout/views/wj_acct_menu.xml` (mới) | Thân menu avatar **dùng chung PC + mobile**: Thông tin tài khoản · Đổi mật khẩu · nhóm **Ngôn ngữ** (cờ + tên, `aria-current` + dấu chọn ở ngôn ngữ đang dùng, link `/portal/set-lang/<code>` sẵn có) · neo trung tính `data-wj-anchor="acct_store_end"` · Đăng xuất. Khung chỉ chứa route của chính nó (luật R6) |
| `layouts.xml` (PC) · `mobile_header.xml` | Cả hai `t-call` thân chung; đầu menu (tên + email) giữ riêng từng kênh. Nút avatar có `aria-label="Tài khoản"` + `aria-haspopup` + `aria-expanded`. Nút cờ ngôn ngữ trên header **giữ nguyên** (neo giỏ hàng của `portal_sale` không đổi) |
| `wujia_portal_base/views/pc_nav_inherit.xml` | **Một** inherit thay hai (`navbar_franchise_information` PC + `mheader_inherit.xml` mobile — file này đã xoá): khối "Cửa hàng hiện tại" (mã + tên, cắt 2 dòng, chip vai trò) · **Đổi cửa hàng** (`data-action="open-store-picker"`, chỉ khi >1 cửa hàng = đúng điều kiện modal render) · **Hồ sơ cửa hàng** (sáng ở hồ sơ + `/portal/info-request*`). Không cửa hàng nào ⇒ cả nhóm và divider đầu nhóm không render |
| `store_picker_navbar.xml` | `_nav_mgr_fids` dời lên inherit `app_layout` (một lần/trang) để sidebar, avatar và sheet cùng đọc — không thêm query |
| `mobile_bottomnav.xml` | Bỏ dòng "Tài khoản / Cài đặt"; neo mới `<span id="msheet_end" hidden>` |
| 6 × `bottomnav_inherit.xml` | return · exam · report · support · knowledge: neo `msheet_end`; **Báo cáo** `t-if="_nav_mgr_fids"`; debt priority 15 (đứng đầu) + **Công nợ** `t-if` = điều kiện controller (như sidebar E8b). Khảo sát (anh Thái, `position="inside"`) không đụng — vẫn cuối |
| `wujia_portal_base/views/bottomnav_inherit.xml` | Gỡ dòng "Hồ sơ cửa hàng" khỏi sheet (đã ở avatar) |
| Tên gọi | Nav trái màn Tài khoản PC + tiêu đề trang (`acct_title` PC, `ph_title` mobile, 2 `title` trong `controllers/portal.py`) → **Hồ sơ cửa hàng** |
| `wujia_portal_notification` | Chuông: `aria-haspopup` + `aria-controls="wj-noti-popup"` + `aria-expanded`; JS `setOpen()` đồng bộ `aria-expanded`/`aria-hidden`; Escape đóng xong trả focus về chuông |
| CSS | `_components.css`: nhãn nhóm, dòng ngôn ngữ, bỏ `margin-right` 7px Vuexy của `<i>` (chữ các mục lệch với mục icon SVG); menu mobile `.dropdown .wujia-mheader-menu` min-width 264 (thắng `.dropdown .dropdown-menu{min-width:8rem}`), `max-height` + cuộn dọc. `_pc_account.css`: biến đệm dùng chung. `store_picker.css`: khối cửa hàng + chip vai trò gọn |
| `migrations/19.0.58.0.0/pre-10` | Xoá view con của `layout_top_navbar` / `mobile_header` / `mobile_bottomnav` còn neo cũ (`@href` profile / change-password, `wujia-msheet-list')]/a[1]`) trước khi nạp khung mới — cùng khuôn E8b |
| Version | layout 19.0.58.0.0 · base 19.0.7.24.0 · notification 19.0.2.24.0 · debt 19.0.4.14.0 · report 19.0.2.7.0 · return 19.0.3.11.0 · exam 19.0.5.23.0 · support 19.0.3.28.0 · knowledge 19.0.3.21.0 · `?v=1323` (`_components.css`, `_pc_account.css`) |

### Avatar — thứ tự (PC = mobile)

| # | Mục | Chủ sở hữu | Điều kiện |
|---|---|---|---|
| 1 | Thông tin tài khoản | layout | luôn |
| 2 | Đổi mật khẩu | layout | luôn |
| 3 | Ngôn ngữ (nhóm, 1 dòng / ngôn ngữ đang bật) | layout | luôn |
| 4 | Cửa hàng hiện tại + vai trò | base | có cửa hàng đang chọn |
| 5 | Đổi cửa hàng | base | >1 cửa hàng |
| 6 | Hồ sơ cửa hàng | base | có cửa hàng đang chọn |
| 7 | Đăng xuất | layout | luôn |

### Sheet "Thêm" mobile — theo quyền

| Vai trò | Dòng |
|---|---|
| owner / manager | Công nợ & thanh toán · Đổi trả / Bù hàng · Đăng ký thi · Kiến thức · Hỗ trợ · Báo cáo · Khảo sát |
| mixed (staff ở cửa hàng đang chọn, manager nơi khác) | như trên, **không Công nợ** |
| staff | **không Công nợ, không Báo cáo** |

Trước E8c: sheet có "Hồ sơ cửa hàng" + "Tài khoản / Cài đặt" (trùng avatar) và Báo cáo hiện cho cả staff (bấm vào bị chặn).

## Bảng nghiệm thu — cột "Kết quả mong muốn"

| # | Ý trong "Kết quả mong muốn" | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Sidebar PC gọn, chỉ nghiệp vụ; +36px nội dung | E8b SN-1…9 (chạy lại) | ✅ 0 vi phạm × 4 vai trò × 9 khổ |
| 2 | Thông báo PC bằng chuông cạnh avatar, thấy badge chưa đọc | chuông + badge + popup "Xem tất cả thông báo" có sẵn; SN-12 | ✅ + `aria-expanded` false→true→false, Escape trả focus chuông (trước: không có `aria-expanded`) |
| 3 | Thông tin cá nhân/cửa hàng tập trung trong avatar | SN-10, 1440 | ✅ 7 mục đúng thứ tự BA (6 với user 1 cửa hàng — không có Đổi cửa hàng, không khoảng trống) |
| 4 | Mobile giữ Thông báo ở bottom-nav | `nav_dump` bottom-nav | ✅ 0 lệch |
| 5 | Mobile chuyển Hồ sơ cửa hàng + Tài khoản/Cài đặt vào avatar, không trùng trong "Thêm" | SN-10 (390) + SN-11 | ✅ avatar mobile cùng 7 mục; sheet không còn 2 dòng đó |
| 6 | Thứ tự **nhất quán PC/mobile** | SN-10 so 2 khổ; test render thật | ✅ cùng một partial ⇒ cùng thứ tự theo cấu trúc; test so từng href |
| 7 | Tên gọi nhất quán | "Hồ sơ cửa hàng" ở avatar PC + mobile, nav trái màn Tài khoản, tiêu đề trang PC + mobile | ✅ (trước: "Thông tin cửa hàng" ở menu/tiêu đề, "Hồ sơ cửa hàng" ở sheet) |
| 8 | Route nhất quán, active đúng module cha | SN-13 + test | ✅ Hồ sơ cửa hàng sáng + `aria-current` ở `/portal/franchise-information` và `/portal/info-request*`; Thông tin tài khoản / Đổi mật khẩu sáng ở route của mình |
| 9 | Quyền nhất quán PC/mobile, item ẩn không để khoảng trống | SN-11 × 4 vai trò; test so sheet ↔ sidebar | ✅ Công nợ + Báo cáo hiện/ẩn y hệt sidebar ở cả 4 vai trò; không divider đôi khi thiếu nhóm cửa hàng |
| 10 | Không ảnh hưởng dữ liệu nghiệp vụ | diff chỉ template/CSS/JS/tiêu đề | ✅ 0 model, 0 controller logic, 0 dữ liệu |
| 11 | (Đề xuất) avatar/dropdown hỗ trợ keyboard, Escape, accessible name | SN-14 | ✅ Enter mở · Escape đóng · focus về nút · `aria-expanded=false` ở 1440 + 390 × 4 vai trò; nút avatar `aria-label="Tài khoản"` |
| 12 | (Đề xuất) label dài tối đa 2 dòng | tên cửa hàng trong khối avatar | ✅ `line-clamp: 2`; menu mobile 264 ở khổ 360, không tràn ngang |

**Đạt 12/12 (100%)** ≥ 90%. Ngôn ngữ xuất hiện 2 chỗ (header + avatar) là theo chốt, ghi ở LIMIT.

### Thước đo `wj_sidebar` (mở rộng)

`scripts/qa/wj_sidebar.py` thêm SN-10…14 (`--only acct` chạy riêng phần E8c):

| # | Kiểm | owner `em.hcm` | staff `cuong.staff` | mixed `dung.multi` #1 | manager `dung.multi` #2 |
|---|---|---|---|---|---|
| SN-10 | thứ tự avatar PC 1440 + mobile 390 · nhóm Ngôn ngữ đúng 1 mục hiện tại · chữ thẳng hàng (≤1px) · aria nút · nút ngôn ngữ còn trên header | ✅ 6 mục | ✅ 6 | ✅ 7 | ✅ 7 |
| SN-11 | sheet theo quyền, không Hồ sơ/Tài khoản | ✅ 7 dòng | ✅ 5 | ✅ 6 | ✅ 7 |
| SN-12 | chuông `aria-expanded` + Escape trả focus | ✅ | ✅ | ✅ | ✅ |
| SN-13 | Đổi cửa hàng mở modal · Hồ sơ sáng ở info-request | ✅ | ✅ | ✅ modal mở | ✅ modal mở |
| SN-14 | bàn phím avatar PC + mobile | ✅ | ✅ | ✅ | ✅ |
| SN-1…9 | sidebar E8b | ✅ | ✅ | ✅ | ✅ |

Tổng: **0 vi phạm × 4 vai trò**, 0 lỗi JS. Khổ 360: menu mobile x=79, rộng 264, đáy 521 (<740), không cuộn ngang.
Ảnh: `scratchpad/e8c/shots/` (m360, sidebar 9 khổ).

### Thước đo hồi quy

| Thước đo | Kết quả |
|---|---|
| `nav_dump` so mốc E8b (28 route × 1440/390) | Sidebar **0 lệch** · bottom-nav **0 lệch**. Lệch chỉ ở menu avatar PC (`navbar`), avatar mobile (`mheader`) và sheet — đúng chủ đích: thêm nhóm Ngôn ngữ, đổi tên "Hồ sơ cửa hàng", sheet bỏ Hồ sơ/Tài khoản. Mốc mới `docs/e8c-baseline/nav_em.json` |
| `wj_measure --diff` so E8b | ✅ 0 ô mất record, 0 tràn. 1 ô đổi cao: `/portal` @360 2405 → 2380 = **trở lại đúng mốc E7a/E7b** (2380); khổ khác không đổi |
| `wj_pagecontainer` 7 khổ | ✅ 0 vi phạm · 0 lỗi JS |
| `wj_button` | ✅ 0 vi phạm (không cần thêm boundary — mục menu là `dropdown-item`, không phải nút) |
| `wj_listcard` | ✅ 0 |
| `wj_filterbar` | ✅ ĐẠT |
| `wj_nesting` | ✅ 0 chỗ lồng |
| `b4_local --base :8090` | ✅ 286/286 |
| `check_layers` | ✅ y hệt E8b (R6 khung biết route Wujia: **0**; R7: 2 có sẵn ở `wujia_franchise`) |
| `test_ownership` | ✅ cross **0** (tests 225, asserts 522) |

## Test

- Suite 15 module `wujia_portal_*` kèm `-u`: **801 tests, 0 failed, 0 error** (E8b 779, +22).
- Mới:
  - `wujia_portal_layout/tests/test_e8c_account_menu.py` (11): arch thân menu (chỉ route khung, đúng thứ tự; neo là
    data-attribute trước Đăng xuất; nhóm Ngôn ngữ `role=group` + `aria-current`); PC + mobile cùng `t-call`, không còn mục
    riêng; header PC + mobile **vẫn có** nút ngôn ngữ; sheet không còn Tài khoản + neo `msheet_end` ẩn; trang render thật:
    PC = mobile cùng thứ tự, mục hiện tại sáng, đúng 1 ngôn ngữ `aria-current`, không divider đôi, nút avatar đủ aria, nhãn.
  - `wujia_portal_base/tests/test_e8c_account_menu.py` (9): thứ tự 7 mục PC + mobile; khối cửa hàng mã/tên/chip vai trò;
    Đổi cửa hàng chỉ khi >1 cửa hàng + modal có trên trang; Hồ sơ cửa hàng sáng ở hồ sơ + info-request; tên ở menu, nav trái,
    tiêu đề PC + mobile; sheet không trùng avatar; sổ vàng sheet owner; sheet theo quyền staff/mixed×2; **sheet ↔ sidebar
    cùng quyền** ở 4 vai trò.
  - `wujia_portal_notification/tests/test_f5_nav_item.py` +2: markup chuông đủ aria + id popup tồn tại; JS đồng bộ
    `aria-expanded` và trả focus khi Escape.
- **DB trắng `wujia_e8c_frame` chỉ cài `wujia_portal_layout`**: 225 tests, 0 failed, 1 error = `TestAvatarAclWithoutFranchise`
  (nợ F6 có sẵn, y hệt E8b). 11 test E8c khung chạy + xanh — khung đứng một mình, avatar không có nhóm cửa hàng vẫn đúng.
  DB đã xoá.
- Mutation **13/13 đỏ đúng guard** (`scratchpad/e8c/mutate.py`): mất neo (base không nạp được — deploy sẽ dừng) · Công nợ
  sheet mất điều kiện · Báo cáo sheet mất điều kiện · Đổi cửa hàng mất điều kiện >1 · gỡ nút ngôn ngữ header mobile · nhóm
  cửa hàng chèn sai chỗ · chuông mất `aria-expanded` · JS chuông không đồng bộ aria · tên menu cũ · tiêu đề trang cũ ·
  divider đôi · info-request không sáng · Bù hàng lệch thứ tự sheet.
  - Bài học mới: mutation làm **một module sau** không nạp được thì Odoo **đã commit** module trước (arch đột biến ở lại
    DB) ⇒ các mutation kế tiếp hỏng dây chuyền (`result=[]`). Phải `-u` lại module đó bằng mã sạch rồi chạy tiếp; harness
    nay `-u` mọi module có trong `--test-tags` (tránh Pass rỗng như #10 lượt đầu: 0 test).

## Bàn giao anh Thái

Không đụng file nào của anh trong E8c. Lưu ý khi sửa `wujia_portal_inspection`:
- Sheet "Thêm" có neo mới `<span id="msheet_end" hidden>` cuối `.wujia-msheet-list`. Dòng Khảo sát đang `position="inside"`
  (đứng sau neo ⇒ vẫn cuối) — đúng thứ tự BA, **không cần sửa**. Nếu muốn đổi thì chèn `before` `msheet_end`.
- Neo cũ `//a[@href='/portal/profile']` trong sheet **không còn** (dòng Tài khoản đã về avatar).

## LIMIT / nợ

- Ngôn ngữ có ở **2 chỗ** (cờ trên header + nhóm trong avatar) — cố ý, theo chốt chủ dự án (CMP-GH-001 + đủ 7 mục issue).
- Trang `/portal/franchise/<id>/profile` giữ breadcrumb cũ; thẻ "Thông tin cửa hàng" trên Trang chủ giữ tên (ngoài phạm vi
  menu/tiêu đề trang đã chốt).
- Báo BA (từ E8a, vẫn mở): `/portal/info-request` không có lối vào trong UI (chỉ sáng Hồ sơ cửa hàng khi vào bằng link).
- DB local chỉ bật English (US) ⇒ nhóm Ngôn ngữ đo được 1 dòng; test C10 có sẵn (`test_selector_renders_every_active_lang`) bật th_TH + vi_VN và kiểm đủ link từng ngôn ngữ trên trang.

## Đo UAT chỉ-đọc (25/09/2026, sau deploy)

`http://113.161.187.126:8019` · DB `wujia_tea_19` · `em.hcm` (owner HCM-01) · mọi POST chặn qua `scratchpad/e6c/uat_guard.py`
— **0 lệnh phải chặn** ở mọi lượt · 0 lỗi JS.

| Cổng / thước đo | Kết quả |
|---|---|
| Phiên bản 13 module (XML-RPC `ir.module.module`) | Lượt deploy đầu: **13/13 vẫn bản E7b** (`-u` chạy khi máy chủ chưa có mã mới) — dừng đo, báo chủ dự án. Lượt 2: **13/13 đúng bản** (layout `19.0.58.0.0`, base `19.0.7.24.0`, `write_date` 09:06) |
| Tệp giao diện trang đang gọi | `_components.css?v=1323`, `_pc_account.css?v=1323` |
| Dấu hiệu trong `/portal` | nhóm Ngôn ngữ trong avatar ×2 (PC + mobile) · `msheet_end` · `nav_header_finance` · `wj-menu-toggle` · `aria-controls="wj-noti-popup"`; "Tài khoản / Cài đặt" 0; "Thông tin cửa hàng" 1 = thẻ Home (LIMIT) |
| `wj_sidebar` đầy đủ SN-1…14 | ✅ **0 vi phạm**: sidebar 264 ở 992–1920, 0 ở 991/390, không cuộn ngang 9 khổ · 14 `li` đúng thứ tự · 28 route sáng đúng · avatar PC = mobile 6 mục (Cửa hàng hiện tại "HCM-01 TP HCM Quận 1" + Owner) · sheet 7 dòng · chuông false→true→false + focus về chuông · bàn phím avatar 1440 + 390 |
| `wj_pagecontainer` 28 route × 390/1024/1440 | ✅ 0 vi phạm; 3 dòng "chuyển hướng" = `/portal/inspection` → `/vi/…` (đã biết từ E7b) — đo lại `/vi/portal/inspection` + chi tiết `/3`: 0 vi phạm |
| `wj_button` 29 route × 5 khổ (150 ô) | ✅ 0 vi phạm mới. 6 dòng báo = `/my/franchises` → `/vi/…` ×5 + `/portal/info-request` không có nút (dữ liệu) — **y hệt đo UAT E6c** |
| Vai trò khác | `cuong.staff`, `dung.multi` trên UAT không dùng mật khẩu seed ⇒ không đo (không reset mật khẩu — là ghi dữ liệu). Đã đo đủ ở local cùng mã |

Ledger `UI-SIDEBAR-001` → `qa_sync --only UI-SIDEBAR-001` dry-run → `--apply` (6 ô + 1 dòng History). Đọc lại bằng
`export?format=csv`: đúng **1 dòng** có cột ID = `UI-SIDEBAR-001` (dòng sheet 124, STT 131) — Trạng thái **Ready for Retest**,
Ngày 25/09/2026, Build/Deploy đúng nội dung; hai dòng kề (UI-PAGINATION-001, UI-BUTTON-001) không đổi.
