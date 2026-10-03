# E8a — Kiểm kê SidebarNavigation `CMP-SN-001` (`UI-SIDEBAR-001`, STT 131)

Phiên đo, **0 dòng code**. 25/09/2026 · Mac · HEAD `46b2ebd`.

- **Local**: DB `wujia_e4b1`, server 8090 (không `--dev=xml`), login `em.hcm`.
- **UAT**: `http://113.161.187.126:8019`, login `em.hcm`, chạy qua `scratchpad/e6c/uat_guard.py`. Có đúng 1 POST bị chặn:
  `/portal/notification/recent`, do chính cú bấm chuông của thước đo gây ra, cố ý không cho chạy.
- **Thước đo** (scratchpad, không commit):
  - `scratchpad/e8a/sidebar_probe.py`: 9 khổ, token 264, drawer, 32 route active, state.
  - `scratchpad/e8a/extra_probe.py`: chuông, avatar, sheet mobile.
  - Số liệu: `local_*.json` · `uat_*.json`. Ảnh: `shots_local/`, `shots_uat/`.
- **UAT khớp local tuyệt đối** ở 9 khổ (1920 · 1440 · 1280 · 1200 · 1199 · 1024 · 992 · 991 · 390) về vị trí/rộng sidebar,
  navbar, lề content, body class, token, drawer, dáng item và active. Lỗi JS: 0 ở cả hai nơi.

## 1. Năm câu hỏi của plan

| # | Câu hỏi | Kết quả đo |
|---|---|---|
| 1 | Đổi `--wujia-sidebar-width` 300→264 có ăn không, hay bị JS Vuexy ghi đè? | **Ăn ngay, chỉ cần CSS.** Ở 1440 sau `add_style_tag`: `.main-menu` 300→**264**, navbar `left` 264, `.content margin-left` 264, `main.wj-page-container` 1140→**1176 (+36px, đúng "Kết quả mong muốn")**. Bắn thêm `resize` vẫn giữ 264. Lý do: `my_js.js:300-307` đã vô hiệu `$.app.menu.init/change`, nên JS Vuexy không tự đặt width nữa. |
| 2 | Ở 992–1199, drawer mở mặc định do đâu? | **`my_js.js:284-291` `_wujiaForceMenuExpanded()`** thêm `menu-expanded menu-open` cho mọi khổ **≥992**, chạy lúc ready, load và **mỗi lần resize**. Hệ quả đo được ở 992/1024/1199: drawer luôn mở. **Hamburger (x≈90–118) nằm dưới drawer 260px** (`elementFromPoint` trúng `.navbar-header` của sidebar), nên người dùng không bấm được. Bấm lập trình, Escape, bấm ra ngoài: **cả ba đều không đóng**. Lý do: `toggle()` mở vì `expanded` = null (init đã bị no-op), sau đó `app.js:385` bắn `resize` và hàm ép mở chạy lại. Nền mờ `.sidenav-overlay` = `display:none` lúc mở ⇒ **không có backdrop**. Có **2** `div.sidenav-overlay` (`layouts.xml:200` và `:230`). Drawer rộng **260** (mặc định Vuexy), không theo token. Không có nút Đóng. |
| 3 | Thứ tự item thật (DOM) sau khi các inherit chèn | Xem §2. **10 mục + 2 tiêu đề nhóm** (MENU CHÍNH / TIỆN ÍCH). Thứ tự do `priority` của 10 file `sidenav_inherit.xml` (plan cũ ghi 12, đã lệch vì F5a dời mục về module). |
| 4 | Active cho route con | **29/32 route sáng đúng mục cha** (list/chi tiết/tạo mới của order, history, delivery, debt, notification, knowledge, support, exam, inspection, account). **Không mục nào sáng** ở `/portal/return`, `/portal/return/new`, `/portal/return/<id>`, `/portal/reports/orders`, `/portal/info-request*`: sidebar PC **không có mục** cho các route này. **0 mục có `aria-current`.** |
| 5 | Hamburger có accessible name? | **Không.** `<a href="#" class="menu-toggle">` chỉ chứa icon: không `aria-label`, `aria-expanded`, `aria-controls`, `title`. Toggle avatar PC cũng không `aria-label`/`aria-haspopup` (Bootstrap chỉ thêm `aria-expanded` khi mở). |

**Q3 (Bù hàng):** plan cụm E ghi *"source có `nav_item_return` 'Đổi trả'"*. **Sai với code hiện tại.**
Sidebar PC không có mục nào cho `/portal/return`. Mục "Đổi trả / Bù hàng" chỉ có trong sheet "Thêm" của mobile
(`wujia_portal_return/views/bottomnav_inherit.xml`, nhãn đã đúng BA). ⇒ E8b phải **tạo mới** mục PC trong
`wujia_portal_return` (thêm `sidenav_inherit.xml`), không phải đổi nhãn. "Báo cáo" cũng vậy (`wujia_portal_report`).

## 2. Hiện trạng → đích BA

### Sidebar PC (≥1200)

| Hạng mục | Hiện trạng (UAT = local) | Đích BA | E8b |
|---|---|---|---|
| Bề rộng | 300 | 264 | đổi token `_variables.css:141` (3 rule `_wujia_theme.css:113/148/153/165` đọc token) |
| Vùng brand | cao **132** (khung card 260×132), logo **184×86**, mục đầu ở y=**217** | 88, logo ≤160×64, bỏ khung card | sửa `layouts.xml:151-168` (`mb-5`, `img width=200 height=100`, spacer 12) |
| Nhóm | 2: MENU CHÍNH (9 mục) · TIỆN ÍCH (Tài khoản) | 3: Chức năng chính · Tài chính & xử lý · Hỗ trợ vận hành | đổi 2 neo thành 3 neo trong khung |
| Mục thừa | Thông báo, Tài khoản | bỏ khỏi sidebar PC | gỡ inherit notification + `nav_item_account` khung |
| Mục thiếu | Đổi trả / Bù hàng, Báo cáo | có | thêm `sidenav_inherit.xml` ở `wujia_portal_return`, `wujia_portal_report` |
| Chiều cao item | 44 | 44 | ✓ |
| Đệm | `10px 15px` (hover `10px 15px 10px 25px`: Vuexy trượt 10px) | `10px 12px` | sửa |
| Gap icon→nhãn | **26** | 12 | sửa |
| Bo góc | mặc định/hover **8**, active **4** | 10 mọi state | sửa |
| Icon | 20 | 20 | ✓ |
| Nhãn | 16/23.2/**400**, active 700 | 15/22/**500**, active 700 | sửa |
| Active | nền `#EAF7FD` ✓, chữ **`#28A9DF`**, không rail | chữ `#168FC2` (hoặc token primary), rail trái 3px | sửa |
| Focus-visible | outline 2px `#0F7CA8` ✓ | có | ✓ |
| `aria-current` | 0 mục | active = `page` | thêm vào `wj_nav_item` |
| Quyền | 0/10 mục có điều kiện | render theo quyền, không chừa khoảng trống | `t-if` theo điều kiện controller của route (§4) |

Thứ tự DOM hiện tại (priority): Trang chủ(10) · Đặt hàng(20) · Lịch sử đặt hàng(30) · Giao hàng(40) · Công nợ(45) ·
Thông báo(50) · Kiến thức(55) · Hỗ trợ(60) · Đăng ký thi(65) · Khảo sát(101, anh Thái, `after nav_item_exam`) · ‖ TIỆN ÍCH · Tài khoản.

Đích: **Chức năng chính** Trang chủ → Đặt hàng → Giao hàng → Lịch sử đặt hàng ·
**Tài chính & xử lý** Công nợ & thanh toán → Đổi trả / Bù hàng ·
**Hỗ trợ vận hành** Đăng ký thi → Kiến thức → Hỗ trợ → Báo cáo → Khảo sát.
⇒ Giao hàng lên trước Lịch sử. Khảo sát đang neo ngay sau Đăng ký thi ⇒ phải dời xuống cuối nhóm bằng
`position="move"` trong inherit **của mình** (Odoo 19 hỗ trợ: `odoo/tools/template_inheritance.py:45`), không sửa file anh Thái.

### Drawer 992–1199

| Hạng mục | Hiện trạng | Đích |
|---|---|---|
| Mặc định | **mở** (`menu-open`), đè tiêu đề trang, khối cửa hàng và hamburger | đóng |
| Bề rộng | 260 (Vuexy) | 264 |
| Mở/đóng | hamburger bị che; toggle/Escape/bấm ngoài **không đóng** | hamburger + nút Đóng + Escape + bấm ngoài, trả focus về hamburger |
| Backdrop | không (2 `.sidenav-overlay`, cả hai `display:none` khi mở) | có |

### <992

PC sidebar vẫn **có trong DOM** nhưng `x=-260 · opacity 0 · visibility hidden` (không vào cây a11y, không bấm được).
BA đã ghi "không render" ⇒ E8b làm `display:none` ở <992 (§4).

### Topbar PC + avatar

| Hạng mục | Hiện trạng | Đích BA |
|---|---|---|
| Chuông | có, `aria-label="Thông báo"`, badge = unread thật (local 42 = `unread-count` 42; UAT 1 = 1), popup 5 thông báo gần nhất + "Xem tất cả thông báo", Escape/bấm ngoài đóng | ✓. Chỉ thiếu `aria-expanded` trên nút chuông |
| Dropdown avatar | đầu (tên + email) · Thông tin tài khoản · **Thông tin cửa hàng** · Đổi mật khẩu · Đăng xuất (4/7) | Thông tin tài khoản · Đổi mật khẩu · Ngôn ngữ · cửa hàng/vai trò hiện tại · Đổi cửa hàng · Hồ sơ cửa hàng · Đăng xuất |
| Ngôn ngữ | dropdown riêng trên topbar | trong avatar dropdown |
| Cửa hàng/vai trò + Đổi cửa hàng | khối "CỬA HÀNG HIỆN TẠI" + chip vai trò riêng trên topbar (`wujia_portal_base/views/store_picker_navbar.xml`, mở modal đổi cửa hàng) | trong avatar dropdown |
| Bàn phím avatar | Enter mở ✓ · Escape đóng ✓ | ✓ |

### Mobile

| Hạng mục | Hiện trạng | Đích BA |
|---|---|---|
| Bottom-nav | Trang chủ · Đặt hàng · Giao hàng · Thông báo (badge) · Thêm | giữ nguyên ✓ |
| Sheet "Thêm" | Công nợ & thanh toán · Đổi trả / Bù hàng · Đăng ký thi · Kiến thức · Hỗ trợ · **Hồ sơ cửa hàng** · Báo cáo · **Tài khoản / Cài đặt** · Khảo sát | gỡ 2 mục in đậm |
| Avatar mobile | 3 ngôn ngữ · Thông tin tài khoản · Thông tin cửa hàng · Đổi mật khẩu · Đăng xuất | nhóm tài khoản/cửa hàng như PC (thiếu cửa hàng/vai trò + Đổi cửa hàng) |

### Tên gọi lệch PC ↔ mobile (BA: "thứ tự, tên gọi… nhất quán")

| Route | PC sidebar | PC avatar | Mobile | BA |
|---|---|---|---|---|
| `/portal/debt` | Công nợ | — | Công nợ & thanh toán | Công nợ & thanh toán |
| `/portal/franchise-information` | (sáng mục Tài khoản) | Thông tin cửa hàng | Hồ sơ cửa hàng | Hồ sơ cửa hàng |
| `/portal/profile` | Tài khoản | Thông tin tài khoản | Tài khoản / Cài đặt | Thông tin tài khoản |

## 3. Việc E8b phải đụng

- **Khung `wujia_portal_layout`**: token, brand, 3 neo nhóm, gỡ `nav_item_account`, `wj_nav_item` thêm `aria-current`,
  hamburger `<button>` có tên, drawer (gỡ `_wujiaForceMenuExpanded` ở 992–1199, backdrop, nút Đóng, Escape,
  trả focus, 1 overlay), dropdown avatar.
- **Module**: `sale`, `purchase_history`, `delivery`, `debt`, `exam`, `knowledge`, `support`, `base` (đổi neo nhóm /
  nhãn). **Mới** `return`, `report`. **Gỡ** `notification` (PC). Mobile: gỡ 2 mục sheet ở `base`/`layout`.
- **Test đang khoá sidebar** (phải cập nhật cùng lượt): `test_f5_nav_item.py` ×9 module,
  `wujia_portal_base/tests/test_f5_menu_ownership.py`, `wujia_portal_layout/tests/test_f5_frame_routes.py`.
  Mốc `nav_dump` (`docs/fra3-baseline/`) sẽ lệch **có chủ đích**, cần chụp lại.
- **Không sửa file anh Thái**: dời Khảo sát bằng `position="move"` từ inherit của mình.

## 4. Quyết định cho E8b: chốt theo BA, không còn câu hỏi treo

Chủ dự án chốt 25/09: chuẩn hoá thì bám BA hết. Cả 5 điểm đều có câu trong spec:

1. **Avatar dropdown đủ 7 mục** (*"Avatar dropdown chứa … Ngôn ngữ, cửa hàng/vai trò hiện tại, Đổi cửa hàng, Hồ sơ cửa hàng…"*).
   **Gỡ** dropdown ngôn ngữ riêng trên topbar (*"thông tin cá nhân/cửa hàng tập trung trong avatar dropdown"*).
   Khối "Cửa hàng hiện tại" trên topbar **giữ nguyên**, vì STT 140 coi nó là một block của topbar; sửa chip vai trò là việc của STT 140.
2. **Quyền = quyền vào route.** Mục hiện khi user vào được route, dùng đúng điều kiện controller đang chặn:
   Công nợ `_DEBT_ROLES` (`wujia_portal_debt/controllers/portal.py:26`), Báo cáo `max_role in (owner, manager)`
   (`wujia_portal_report/controllers/portal.py:86`). Không đặt quy tắc mới.
3. **`/portal/info-request*`**: *"List/detail/create active đúng module cha"*. Cha là hồ sơ cửa hàng
   ⇒ mục "Hồ sơ cửa hàng" trong avatar sáng; sidebar không sáng mục nào.
4. **Bỏ hover trượt 10px**: *"padding 10px 12px"* cố định, *"không thay radius giữa các state"*. State chỉ đổi màu.
5. **<992 `display:none`** cho PC sidebar (*"không render PC Sidebar"*). Server không biết khổ màn nên không bỏ khỏi HTML được.

**Báo BA (ngoài E8):** `/portal/info-request` **không có lối vào nào** trong giao diện (menu PC/mobile, trang hồ sơ
cửa hàng đều không link tới); chỉ vào được bằng URL. Thêm lối vào là tính năng mới ⇒ cần BA mở issue riêng.
