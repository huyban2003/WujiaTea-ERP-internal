# E8b — Ma trận nghiệm thu · SidebarNavigation `CMP-SN-001` (sidebar PC + drawer 992–1199)

Lượt thứ hai của cụm **E8** (`UI-SIDEBAR-001`, STT 131). E8a (`6bf64f7`) đo hiện trạng; E8b dựng sidebar PC
theo BA (264, brand 88, 3 nhóm, dáng mục, `aria-current`, quyền) + drawer 992–1199 + ẩn <992.
**Issue giữ Ready for Dev** — E8c làm avatar dropdown 7 mục + mobile + đo UAT chỉ-đọc rồi mới lên Ready for Retest.
**Chưa deploy UAT**, commit local.

- Spec: tab `UI Component` dòng CMP-SN-001 + kiểm kê `docs/e8a-sidebar-inventory.md` §2–§4 (chủ dự án chốt "bám BA hết").
- Đo: DB local `wujia_e4b1`, server **8090**, test **8098**. Tài khoản: `em.hcm` (owner HCM-01), `cuong.staff`
  (staff), `dung.multi` (manager HN-02 + staff HN-01/HCM-01, đo với cookie cửa hàng 1 = staff và 2 = manager).
- Không đổi controller / model / dữ liệu / quyền route — chỉ template khung, `sidenav_inherit.xml` của module sở hữu
  route, CSS, 1 file JS, sổ test, thước đo.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `layouts.xml` `layout_sidenav` | Khung chỉ còn neo: `nav_header_main` "Chức năng chính" · `nav_header_finance` "Tài chính & xử lý" · `nav_header_ops` "Hỗ trợ vận hành" · `nav_end`. Gỡ nhóm "Tiện ích" + mục Tài khoản (về avatar, E8c), spacer, `mb-5`, `img width=200 height=100`, `.sidenav-overlay` trùng (giữ 1 trong `app_layout`). Sidebar có `id="wj-main-menu"` `role="navigation"` `aria-label`, brand có nút Đóng |
| `layouts.xml` hamburger | `<a href="#">` → `<button type="button">` `aria-label="Mở menu"` `aria-controls="wj-main-menu"` `aria-expanded`; bỏ `style="color:#ccc"` (icon trắng trên topbar xanh) |
| `wj_nav_item.xml` | `aria-current="page"` khi `ni_active` |
| `_variables.css` | `--wujia-sidebar-width` 300 → **264**, `--wujia-sidebar-brand-h` 88, chữ mục 15/22; gỡ 3 token logo/gap cũ |
| `_sidebar.css` (mới) | Mọi dáng sidebar một chỗ, phạm vi `#wj-main-menu`: brand · tiêu đề nhóm · mục (44, `10px 12px`, gap 12, bo 10 mọi state, icon 20, 15/22/500) · hover chỉ đổi nền (bỏ trượt Vuexy) · active 700 + `#EAF7FD` + `#168FC2` + rail 3px (`::before`, không đổi layout) · nhóm rỗng tự ẩn tiêu đề (`:has`) · drawer 992–1199 · ẩn <992 |
| `_wujia_theme.css`, `_pc_components.css` | Gỡ khối brand/mục/active cũ (đã dời sang `_sidebar.css`) |
| `my_js.js` | `_wujiaForceMenuExpanded` chỉ ép mở ở **≥1200** (trước: ≥992 ⇒ drawer kẹt mở) |
| `wujia_sidebar.js` (mới) | Drawer 992–1199: hamburger mở · nút Đóng / Escape / bấm backdrop đóng · focus vào nút Đóng khi mở, trả về hamburger khi đóng · `aria-expanded`. Bắt click pha capture để handler Vuexy không chạy |
| `migrations/19.0.57.0.0/pre-10` | Xoá view con của `layout_sidenav` trước khi nạp khung mới (neo cũ biến mất ⇒ view con cũ làm hỏng validate); mỗi module tạo lại view của mình khi `-u` |
| 10 × `sidenav_inherit.xml` | Mỗi module sở hữu route tự khai mục, chèn `before` neo nhóm kế: bảng dưới |
| `wujia_portal_notification` | Gỡ `sidenav_inherit.xml` (Thông báo vào bằng chuông topbar; tab mobile giữ) |
| `wujia_portal_return`, `wujia_portal_report` | **File mới** `sidenav_inherit.xml` |
| `wujia_portal_inspection` (anh Thái) | **Sửa tối thiểu, chủ dự án duyệt 25/09** — xem *Bàn giao anh Thái* |
| `assets.xml` | `?v=` 1320–1322 · bump **14 module** |

### Mục menu — thứ tự, chủ sở hữu, quyền

| Nhóm | Mục | Module | Điều kiện hiện (= điều kiện controller) |
|---|---|---|---|
| Chức năng chính | Trang chủ · Đặt hàng · Giao hàng · Lịch sử đặt hàng | base · sale · delivery · purchase_history | mọi user portal |
| Tài chính & xử lý | **Công nợ & thanh toán** | debt | owner/manager của cửa hàng đang chọn, hoặc chưa chọn cửa hàng (`_debt_access`) |
| | **Đổi trả / Bù hàng** (mới) | return | mọi user portal |
| Hỗ trợ vận hành | Đăng ký thi · Kiến thức · Hỗ trợ | exam · knowledge · support | mọi user portal |
| | **Báo cáo** (mới) | report | vai trò cao nhất trên mọi cửa hàng ∈ owner/manager (`/portal/reports/orders`) |
| | Khảo sát | inspection (anh Thái) | như cũ |

Danh sách vai trò (`_nav_mgr_fids`) tính **một lần/trang** trong inherit của `base`, không query mỗi mục.
Giao hàng lên trước Lịch sử; Khảo sát xuống cuối nhóm; Thông báo và Tài khoản rời sidebar.

## Bảng nghiệm thu

Thước đo `scripts/qa/wj_sidebar.py` (mới, E8c dùng lại để đo UAT) — 9 khổ 1920/1440/1280/1200/1199/1024/992/991/390.

| # | Tiêu chí BA | Phép đo | Kết quả |
|---|---|---|---|
| SN-1 | Sidebar 264 ở ≥1200, nội dung dịch theo | `.main-menu` rect · navbar `left` · `.content margin-left` | ✅ 264 · 264 · 264 ở 1920/1440/1280/1200 (E8a: 300) |
| SN-2 | Brand 88, logo ≤160×64, không khung card | rect brand/logo | ✅ brand 263×**88** · logo **160×42,7** tại x=24 (E8a: 132 · 184×86) |
| SN-3 | 3 nhóm, đúng thứ tự + nhãn, render theo quyền, không chừa khoảng trống | danh sách `li` đã render, 4 vai trò | ✅ owner 11 mục · manager 11 · **mixed** (staff ở cửa hàng đang chọn, manager nơi khác) 10 — không Công nợ, có Báo cáo · **staff** 9 — không Công nợ, không Báo cáo; nhóm vẫn đủ 3 tiêu đề vì còn mục |
| SN-4 | Mục 44, đệm `10px 12px`, gap 12, bo 10 **mọi state**, icon 20, chữ 15/22/500, active 700 + `#EAF7FD` + `#168FC2` + rail 3 | computed style mặc định / hover / focus / active | ✅ đúng cả 4 state; hover không trượt; focus-visible còn outline |
| SN-5 | Mục sáng đúng route cha + `aria-current="page"` | 28 route (list/chi tiết/tạo mới) | ✅ **21/21** route có mục cha sáng đúng 1 mục kèm `aria-current`; **7** route không thuộc sidebar (Thông báo ×2, YC thông tin ×2, Tài khoản, Đổi mật khẩu, Hồ sơ cửa hàng) sáng **0** mục — đúng BA (chuông / avatar). Mới sáng: Bù hàng (list, chi tiết, `?q=`), Báo cáo |
| SN-6 | 992–1199: đóng mặc định; mở bằng hamburger; đóng bằng hamburger / Escape / backdrop / nút Đóng; trả focus | 1199 · 1024 · 992, 4 vòng mở–đóng | ✅ mặc định đóng (x=−264, hamburger không bị che) · mở: drawer 264, backdrop hiện, `aria-expanded=true`, **focus vào nút Đóng** · cả 4 cách đóng đều đóng + **focus về hamburger** + `aria-expanded=false` (E8a: kẹt mở, 0 cách đóng) |
| SN-7 | <992 không render sidebar PC | `display` ở 991/390 | ✅ `display:none` (E8a: có trong DOM, x=−260) |
| SN-8 | A11y | hamburger · landmark · backdrop | ✅ `<button>` "Mở menu" + `aria-controls="wj-main-menu"` · `role=navigation` + `aria-label` · đúng **1** `.sidenav-overlay` (E8a: 2) |
| SN-9 | Không scroll ngang | `scrollWidth` 9 khổ | ✅ 0 |
| — | Lỗi JS | console | ✅ 0 (cả 4 vai trò) |

Tổng `wj_sidebar`: **0 vi phạm** × owner `em.hcm` (đủ SN-5) · staff `cuong.staff` · mixed `dung.multi` cửa hàng 1 · manager
`dung.multi` cửa hàng 2 (`--quick`). Ảnh: `scratchpad/e8b/shots/` (sidebar 9 khổ + drawer 1024 mở).

### Thước đo hồi quy

| Thước đo | Kết quả |
|---|---|
| `wj_pagecontainer` 31 route × 7 khổ | ✅ 0 vi phạm · 0 lỗi JS |
| `wj_measure --diff` so E7b | ✅ 0 tràn. Báo **26 ô "mất record"** — **không phải mất dữ liệu**: toàn bộ ở 360/390, mỗi ô giảm **đúng 14** = số `li` sidebar cũ (4 của khung + 10 mục) mà thước đo đếm vì trước đây sidebar chỉ bị đẩy ra ngoài (x=−260, còn chiều cao); nay `display:none`. Khổ PC: 0 ô đổi số record |
| `wj_button` | ✅ 0 vi phạm sau khi thêm `wj-menu-toggle`, `wj-sidebar` vào boundary (shell CMP-SN-001, cùng loại bottom-nav). Lượt đầu báo 4 ô "chưa migrate" ở 992/1024 trên 2 màn rỗng: chính là hamburger — trước là `<a>` không class `btn` nên thước đo không thấy |
| `wj_listcard` | ✅ 0 |
| `wj_filterbar` | ✅ ĐẠT |
| `wj_nesting` | ✅ 0 chỗ lồng |
| `b4_local --base :8090` | ✅ 286/286 |
| `check_layers` | ✅ không thêm (3 vi phạm có sẵn, y hệt E7b) |
| `nav_dump` so mốc FR-A3 | Sidebar: đúng thứ tự/nhãn mới; **9 route đổi mục sáng, cả 9 có chủ đích** (Bù hàng ×3 và Báo cáo nay sáng; Thông báo ×2, Tài khoản/Đổi mật khẩu/Hồ sơ cửa hàng nay không sáng). Bottom-nav 0 lệch (bỏ số badge — khác DB) · sheet "Thêm" 0 lệch. Mốc mới: `docs/e8b-baseline/nav_em.json` |

## Test

- Suite 13 module portal kèm `-u`: **779 tests, 0 failed, 0 error** (mốc E7b 756, +23).
- Sửa cùng lượt, **không giảm assert**: `test_f5_menu_ownership.py` (sổ vàng 11 mục + 3 nhóm + active/`aria-current`
  10 route + quyền owner/staff/mixed), `test_f5_nav_item.py` ×10 (+2 mới return/report; notification đổi thành "không có
  mục PC, chuông còn"), `test_f5_frame_routes.py` (4 neo mới, neo cũ phải mất). Mới: `test_e8_sidebar.py` (17: token,
  CSS brand/mục/hover/active/drawer/<992/nhóm rỗng, JS ngưỡng 1200 + drawer, arch khung, trang render thật: 1 backdrop,
  hamburger `<button>` đủ aria, neo có mặt).
- `test_ownership`: tests 197 → **214**, asserts 425 → **491**, **cross 0**.
- Mutation **14/14 đỏ đúng guard** (`scratchpad/e8b/mutate.py`): token 300 · z-index drawer 1040 · hover trượt · mất rail ·
  ép mở từ 992 · không trả focus · hamburger về `<a>` · 2 backdrop · mất `aria-current` · đổi nhãn nhóm · Công nợ mất
  điều kiện · Báo cáo mất điều kiện · Bù hàng sai nhóm · Bù hàng không sáng ở route con.
  Bài học: đột biến ở module X mà guard nằm ở `portal_base` ⇒ phải `-u X,wujia_portal_base`, không thì 0 test chạy
  (lượt đầu #13 "xanh" với **0 test** — Pass rỗng).
- **DB trắng `wujia_e8b_frame` chỉ cài `wujia_portal_layout`**: 214 tests, **0 failed**, 1 error =
  `test_fra3_layer_guard.TestAvatarAclWithoutFranchise` (nợ có sẵn thuộc F6, ghi từ F5b). 17 test E8 chạy + xanh, gồm trang
  render thật: khung đứng một mình, sidebar chỉ có neo (không module nào chèn mục) vẫn render. DB đã xoá sau khi đo.

## Bàn giao anh Thái — `wujia_portal_inspection`

Chủ dự án duyệt 25/09 (tiền lệ E7a). Chỉ đụng `views/sidenav_inherit.xml` phần PC + bump version `19.0.1.7.0 → 19.0.1.8.0`:
- Neo `//li[@id='nav_item_exam']` after → **`//li[@id='nav_end']` before** (Khảo sát cuối nhóm "Hỗ trợ vận hành" theo thứ tự BA).
- Thân `<a>` tự dựng → `t-call wujia_portal_layout.wj_nav_item` (có `aria-current`, dáng chung). Truyền `ni_active = _inspection_active`.
- **Giữ nguyên**: `id="nav_item_inspection"`, priority 101, điều kiện sáng `_inspection_active`, toàn bộ phần mobile.
- Lý do không dùng `position="move"` từ module mình: không module nào của Dev portal depend `wujia_portal_inspection`
  ⇒ DB không cài Khảo sát sẽ lỗi xpath, cả portal 500.
- Khi anh Thái sửa file này: neo phải là `nav_end` (neo `nav_item_exam`/`nav_header_utils` cũ không còn nghĩa thứ tự).

## LIMIT / nợ

- Sheet "Thêm" mobile vẫn có mục Báo cáo **không kèm điều kiện vai trò** (staff bấm vào bị controller chặn) — E8c.
- Ẩn tiêu đề nhóm rỗng dùng `:has()` — cần Safari ≥ 15.4 (cùng giới hạn E7b). Trình duyệt cũ: tiêu đề nhóm rỗng hiện trơ, không vỡ layout.
- Avatar dropdown 7 mục, gỡ dropdown ngôn ngữ topbar, `aria-expanded` chuông, avatar/sheet mobile, tên gọi lệch PC↔mobile — E8c.
- `/portal/profile`, `/portal/franchise-information`, `/portal/info-request*`, `/portal/notification*` không sáng mục sidebar
  nào (đúng BA: thuộc avatar / chuông). Lối vào Tài khoản trên PC hiện là avatar dropdown sẵn có ("Thông tin tài khoản").
- Báo BA (từ E8a, vẫn mở): `/portal/info-request` không có lối vào trong UI.
