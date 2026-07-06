# WujiaTea — Compact summary

**Mục đích:** context file inject vào mọi session WujiaTea. Mỗi §section search-able qua `/recall`. Detail history giữ trong `wujia-tea-doc.tex` + git log.

**Cập nhật:** 2026-07-07 — **Sprint 28 DONE: PC Tài khoản 9 màn (Figma `wujia_pc_01..09_v3`, page 4792) — `wujia_portal_layout` + `wujia_portal_base`, chapter 39.** 3 trang desktop (`/portal/profile` chỉ đọc / `/portal/franchise-information` 3 state owner/empty/staff / `/portal/change-password` 4 state) + dropdown avatar (frame 09) + **rework toàn bộ sidebar** theo menu Figma (1 view `priority=99` + `position=replace`) + TIỆN ÍCH/Tài khoản. Shell chung `pc_account_shell.xml` (nav card trái + page-header) + `_pc_account.css` page-scoped (blast radius 0). Controller: 3 chuỗi lỗi khớp Figma + franchise context cho change-pw. Verify upgrade RC=0 91 mod, Playwright 1920px 8/9 frame khớp Figma, test_sprint9 7/7, 15/15 route 200. _(Trước, 2026-07-03: Sprint 27 PC Giao hàng desktop, chapter 38.)_ _(Trước, 2026-07-01:)_ **Sprint 26 DONE: Mobile Đăng ký thi (Exam Registration) 7 màn theo Figma `#4755:2` — `wujia_portal_exam` `19.0.2.0.0`, chapter 37.** `wujia_portal_exam` lần đầu có mobile: **s0** list (search + badge trạng thái Đã đăng ký/Chờ duyệt/Có kết quả + FAB "+ Đăng ký mới") + **wizard 1 trang JS s1→s5** (Chọn khóa thi → calendar Chọn lịch thi → popup Chọn khung giờ bottom-sheet → Nhập nhân sự thêm/xóa người → Xác nhận) + **s6** Kết quả (Danh sách kết quả Đạt/Không đạt + điểm theo người). **UI-only + demo** (nội dung hardcode khớp Figma, nút Xác nhận = stub toast, s0 đọc data thật nếu có; model đa-nhân-sự/khung-giờ/kết-quả-theo-người = Phase 2). Route mới GET `/portal/exam/register` + `/portal/exam/registration/<id>`; JS mới `portal_exam_wizard.js`. **GOTCHA mới:** `_components.css` có `h1,.wujia-h1{font-size:var(--wujia-font-size-h1)!important}` (+ bản h2) đè MỌI `<h1>/<h2>` bare về 32/24px → heading mexam sai size, fix scope `.wujia-mpage .wujia-mexam-h1` + `!important` (h3 không dính). Verify upgrade RC=0 91 mod, Playwright 390px 7 màn khớp Figma, interactions (thêm/xóa/đánh-số người, đổi step, slot highlight, submit toast) OK; fix bug "bấm card ko ăn" (card data-thật gán `link='#'`→`/portal/exam/registration/<r.id>`). → chapter 37. _(Trước, 2026-07-01:)_ **Sprint 25 DONE: Home Mobile Quick Action UI v4 theo Figma `#4712:2` — chapter 36.** Block "Hành động nhanh" rework: gradient cyan → card trắng (`#FFFFFF`), layout dọc → ngang (horizontal row), icon thêm circle 32×32 nền `#E9F7FC` / icon cyan 16px, text đen 12px, section title 20px. 4 file: `_variables.css` (3 token mới) + `_components.css` (CSS block) + `portal_home.xml` (icon wrapper span) + `assets.xml` (`?v=1146`). Upgrade RC=0, 91 modules. _(Trước, 2026-07-01:)_ **Sprint 24 DONE: Mobile Giao hàng 5 màn (List/Detail/Empty/Loading/Error) theo Figma `4731`, batch-centric — `wujia_portal_delivery` `19.0.2.0.0`, chapter 35.** Mobile list = thẻ theo CHUYẾN XE (1 thẻ = 1 chuyến nhiều đơn, khác desktop liệt kê theo picking) → controller +query batch franchise-scoped + chip trạng thái (soon/going/done) + lọc ngày `planned_departure` + 5 `view_state` (try/except→error, `?_preview=` QA). Detail wire batch route sẵn có + bảng SP gom từ move line. Badge màu Figma (Sắp giao `#FEF3C7`, Đang giao soft cyan, Đã giao `#ECFDF5`); icon Xuất phát = **lịch cyan** (BA QA). Desktop GIỮ NGUYÊN (`d-none d-lg-block`). Verify upgrade RC=0, Playwright 390px 5 màn khớp Figma, desktop intact, return/history smoke OK. _(Trước, 2026-06-28:)_ **Sprint PC-3 DONE: PC Notification (List + Form + Popup) theo Figma `4683`.** Desktop `/portal/notification` chuyển sang hệ `wj-pc-*` (giữ nguyên mobile S22): List (filter 5-field 1 hàng + chips ngoài card + bảng type-chip/unread-bar/status-badge + bulk mark-read), Form (`wj-pc-two-col` content + info/attachment), Popup (chuông header lazy-load endpoint MỚI `/portal/notification/recent`, card-per-item). Controller +`date_from`/`date_to`/`priority`. **Audit Figma bằng Playwright + 3 sub-agent** → fix filter wrap / bảng tràn viền (`tr::before`→box-shadow) / chips placement / popup chip. Seed `seed_notification_demo.py`. manifest `19.0.1.6.0`. Verify upgrade RC=0, test 21/0+7/0, route 200, Playwright khớp Figma. → chapter 34. _(Chi tiết §5 + 2 gotcha mới.)_ _(Trước, 2026-06-24:)_ **Sprint 22: Mobile Thông báo (List+Detail) + chuẩn hoá typography heading.** `wujia_portal_notification` lần đầu có bản mobile `d-lg-none` theo Figma `4651:655` (2 màn): list card-per-row (accent bar + dot + bold khi chưa đọc, source `type • dispatch`, badge, date) + detail (type header + mô tả loại + badges + body + **"Liên kết liên quan"** + file đính kèm download thật). Controller +filter `unread` (chip "Chưa đọc" wire read state) + `cnt_unread`/`total`. **UI-only đa dạng icon/màu/badge** derive từ `type_id.code` (tone red/cyan/amber/violet/green + icon) + `priority` (badge Cần làm/Quan trọng/Lưu ý) — map tạm `WJ_TONE/WJ_ICON/WJ_TDESC/WJ_PTAG` đầu template, controller wire sau. **Cross-page fix typography:** heading mobile `font-weight 800→700` theo Figma từng trang (Figma dùng 700, không phải 800) — `mknow-title` 22/800→**25/700**, `mnoti-title` 22/800→22/700 + detail titles, `mticket-h1` (ticket/return/support), `maccount-pagetitle`/`store-name`, `mknow-sechead`/`article`; mknow search 42→**38**, noti search **compact 30**, noti card-title màu #6B7280→#374151/#111827. GIỮ 800 ở số liệu nhấn mạnh (history amount/code, PC grand). history/order/cart title 24/700 đã khớp Figma sẵn. layout `19.0.25.0.0` `?v=1138` / notification `19.0.1.4.0`. Verify upgrade RC=0, 7 trang 200, test 21/0+7/0. → chapter 32. _(Trước: Sprint PC-1 chi tiết chapter 31.)_

**(Sprint PC-1, 2026-06-22):** Part A = Foundation+Shell theo BA `pc_source_ui_v1_4`: token `--wj-pc-*` (radius 18/12, table 50/58, soft palette) + `_pc_components.css` MỚI (10 component `wj-pc-*`, scoped zero-blast) + sidebar active → BA (soft `#EAF7FD` + accent bar cyan) + gallery dev-only `/portal/_pc-preview`. Part B = màn **Đặt hàng PC combined** (Figma `4600:2` → `wujia_portal_sale`): gộp catalog trái + **giỏ hàng đầy đủ phải 1 trang**, table header cyan, nút add **badge qty**, **dòng in-cart sáng nền cyan**, stepper live + **sync 2 chiều** cart↔catalog (cùng tab, không reload), warning-bar khung giờ, pagination numbered + count, partial `pc_cart_panel` dùng chung cho `/portal/order/cart` standalone (bỏ SĐT/địa chỉ). UI-only: Quy cách + tên CN (chờ field). **▶ NEXT: realtime cart không-reload cross-session (bus.bus, §5) + tiếp các trang desktop khác.** Chi tiết → §4 + §5 + chapter 31. _(Sprint 21 = mobile Product/Cart+History v2, chi tiết chapter 30. Lịch sử prose cũ GỠ giữ compact.)_

---

## §1 wujia-overview

**Project:** Odoo 19 ERP + custom Vuexy portal cho chuỗi nhượng quyền trà sữa (~1500 portal user). Migrate v14 → v19.

**Dir:**
- `WujiaTea/odoo19/` Odoo 19 Community source (read-only).
- `WujiaTea/custom/` 18 custom module active (§2).
- `WujiaTea/themes/` 8 Vuexy theme.
- `WujiaTea/data/` seed master (area/ward).
- `WujiaTea/scripts/` seed + deploy script (Python + PowerShell).
- `WujiaTea/docs/` `wujia-tea-doc.tex` master + chapters + `Wujia_Internal ERP Master Plan.xlsm` (BA spec) + `wujia-design-system.md` (chuẩn UI người-đọc) + `figma-mcp-setup.md` (Figma connect guide).
- v14 reference (legacy): `/home/huyban/odoo-dev/wujia_tea_odoo14` — template ref, không sửa.

**Figma (BA design — READ-ONLY, follow sau):** file gốc "Wujia" key `vfVcqN5zPJvlcjZU4NYim0` (team người khác, Starter → API throttle) — **MCP đọc dùng BẢN COPY ở team Pro của mình: `aoeiDYlg6vlhJZg2w6Q7o5` ("Wujia (Copy)", HTTP 200, không throttle). BA/host EDIT TRỰC TIẾP vào copy → copy = source of truth (BA cần quyền edit copy; đừng đụng gốc nữa).** Nối qua Framelink MCP (`/home/huyban/odoo-dev/.mcp.json` ở workspace root + key nhúng, gitignored). **BA CHƯA XONG FIGMA → khi BA hoàn thiện thì FOLLOW THEO FIGMA của BA** (đối chiếu → cập nhật `_variables.css`, KHÔNG sửa Figma). Dùng Figma MCP để xem screens + đọc structure (type/size/màu/radius/font). ⚠️ Figma hiện PHẲNG (card = siblings, không container) → gom bằng geometry. Chi tiết §8 + đề nghị BA: `docs/figma-mcp-setup.md`. Chuẩn UI hiện tại (code-based): `docs/wujia-design-system.md`. Hiện tại nguồn ưu tiên = **code chuẩn > xlsm spec (lag)**.

**Local dev:** `scripts/init-db.sh` fresh / `scripts/start.sh` hot-reload / `scripts/upgrade.sh <module>` giữ data / `scripts/reseed_full.sh` 1-shot. DB `wujia_tea_19`, user `odoo19/1`, host `127.0.0.1:5432`. Log: `WujiaTea/logs/odoo.log`. Config: `WujiaTea/config/odoo.conf`.

**Auto-deploy:** push `main` → GitHub Actions self-hosted runner trên Windows `D:\wujia-tea` → `git pull` + restart Odoo service.

---

## §2 wujia-modules (18 active)

| Module | Vai trò |
|---|---|
| `wujia_core` | `res.area`, `res.ward` master data |
| `wujia_franchise` | `wujia.franchise.management` + `wujia.franchise.member` |
| `wujia_sale` | `sale.order` ext + 6 field + tính khối lượng |
| `wujia_fleet` | Nhà xe / loại xe / xe / bảng giá |
| `wujia_delivery` | `stock.picking/batch` ext + cước vận chuyển |
| `wujia_portal_layout` | Vuexy shell + CSS vars + Inter self-host + responsive (hamburger + fluid font 14→16px) + 3 utility class shared |
| `wujia_portal_base` | `/portal` dashboard + `bus.bus` realtime + franchise switch |
| `wujia_portal_sale` | `/portal/order` catalog + cart |
| `wujia_portal_purchase_history` | `/portal/purchase-history` |
| `wujia_portal_delivery` | `/portal/delivery` |
| `wujia_portal_return` | `/portal/return` + models |
| `wujia_portal_notification` | `/portal/notification` + models |
| `wujia_portal_exam` | `/portal/exam` + models |
| `wujia_portal_knowledge` | `/portal/knowledge` + backend admin |
| `wujia_portal_report` | `/portal/reports/orders` |
| `wujia_portal_support` | `/portal/support` + backend admin + POST + attachment |
| `wujia_portal_info_request` | `/portal/info-request` — yêu cầu cập nhật info franchise + HQ duyệt |
| `wujia_portal_order_window` | Khung giờ portal đặt hàng — `wujia.order.window` per-area + `res.config.settings` global fallback |

> Sprint 17: `wujia_portal_debt` đã XÓA (Công nợ chuyển về Home + bỏ build, route /portal/debt = 404). Dựng lại theo ADR-007 khi BA build account.move Phase 2.

→ Chi tiết: `wujia-tea-doc.tex` §1.3, §1.5.

---

## §3 wujia-adr-summary (16 ADR)

ADR-001 odoo19 source độc lập / ADR-002 venv conda `odoo` (py3.10) / ADR-003 PG role `odoo19` / ADR-004 custom portal Vuexy thay `/my` / ADR-005 model mới `wujia.franchise.member` / ADR-006 realtime `bus.bus` Odoo native / ADR-007 tách module Order+History / ADR-008 URL kebab-case + 301 redirect / ADR-009 block portal feature → defer / ADR-010 3 field địa chỉ giao / ADR-011 active branch picker TẠI LOGIN / ADR-012 *overruled by ADR-015* / ADR-013 `res.area`/`res.ward` ở `wujia_core` / ADR-014 `wujia.franchise.member` UI độc lập / ADR-015 gộp `wujia_franchise_management` → `wujia_franchise` / ADR-016 (Sprint 5) dùng `mail.message` chuẩn via `message_post()`, không tạo `wujia.support.ticket.message`.

→ Chi tiết: `wujia-tea-doc.tex` chap 2 + chap 13.

---

## §4 wujia-sprint-history (compact)

| Sprint | Date | Outcome |
|---|---|---|
| 1–2 | 2026-04 | `wujia_core/franchise/sale` + perf (ormcache, store+index, cron) |
| 3 | 2026-05-02 | `wujia_fleet` + `wujia_delivery` + BA section A refactor |
| 4.0–4.4 | 2026-05-15 | 9 portal skeleton + Vuexy + BA palette 19 màu + backend admin Knowledge/Support + POST ticket |
| 5 | 2026-05-16 (deployed) | Knowledge full BA + Support full BA + ADR-016 + i18n skel + test 20/20 pass + `reseed_full.{sh,ps1}` |
| 6 | 2026-05-17 | 18 portal route mới: forgot/reset PW (rate-limit anti-enum), profile+avatar ETag, cart hybrid AJAX atomic SQL, exam SELECT FOR UPDATE, shared `rate_limit` + `attach_files_to_record` utils |
| 7 | 2026-05-17 | `wujia_portal_info_request` (model + 5 route + chatter) + 8 ext route (noti mark-read jsonrpc, knowledge SAYT, attachment dl, PDF/ICS/XLSX export). 30 route Sprint 6+7 |
| 8 | 2026-05-21 | favicon fix + BA §A `/portal/franchise-information` readonly + BA §B order portal mapping + module mới `wujia_portal_order_window` (per-area + global fallback) + design token `_variables.css` + `_components.css` shared (`wujia-btn`/`wujia-badge-*`/`wujia-empty-state`/`wujia-two-pane`) |
| 9.1–9.13b | 2026-05-23..27 | Portal UI refactor theo BA sheet "5. Issue List" — xem §9 |
| 9 (DONE) | 2026-06-03 | **Sprint 9 đóng**: UI-01..UI-18 (18 issue) + empty state chuẩn hoá + cleanup (301 redirect + xóa stub) + verify (test_sprint9 7/7) + doc chapter 18. Còn 9.24 push qua `/wujia-end-sprint`. → chapter 18 |
| 10 | 2026-06-06 | **Mobile Home theo Figma** (frame 2474:2): hero nền tối 2 cột (cửa hàng \| Vai trò+badge) + 4 KPI nhúng (Công nợ UI-only "0đ") + card khung giờ 3 state (wire `_order_window_view`) + grid 6 quick-action + noti nổi bật + bottom-nav active đỏ. Desktop giữ nguyên (`d-lg-none`/`d-none d-lg-block`). + logo navbar mobile + ẩn mobile store-strip trên `/portal`. test 7/7+20/20, upgrade RC=0. → chapter 19 |
| 11 | 2026-06-07 | **Mobile Đặt hàng theo Figma** (frame 2480:2) + **dứt điểm item 10.1** + **BA Registry v3** (`UI/Wujia_Source_UI_Final_Pack_v2.1` = source of truth component mobile). 2 màn: Sản phẩm (warning bar khung giờ + search + product row compact + qty badge xanh + floating cart bar **gradient `#0B2430→#1B5C75`** nút "Xem giỏ" nền trắng chữ cyan) + Giỏ hàng (stepper ± + Thành tiền + summary CTA "Gửi đơn" submit thẳng, no field địa chỉ). **Bottom-nav** (`mobile_bottomnav.xml` share) + **Current Store Strip** `[code] tên · role` promote TOÀN portal mobile (strip ẩn ở Home + `/portal/order*`). Badge noti bottom-nav dùng lại poll bell (0 query thêm). Header GIỮ NGUYÊN (chờ BA final). Desktop giữ nguyên. Token `--wujia-morder-*`/`--wujia-mcart-*`, asset v=1115. test 7/7+20/20, upgrade RC=0. → chapter 20 |

| 12 | 2026-06-07 | **Mobile Shell FINAL** (BA `UI/Wujia_Source_UI_FINAL_v1`, thay mọi pack cũ): Header(104 cyan, logo slot, lang/cart/avatar, **no bell**) + Current Store Strip(48) + Footer(83, **active CYAN** ≠ đỏ) thành shared shell render 1 lần trong `app_layout` → mọi trang mobile. File mới `mobile_header.xml`. "Thêm"→sidebar (interim, NOTE). Strip hiện mọi trang (user chốt "cho đều"). Fix root-cause gap dưới header (Vuexy `content-wrapper margin-top:6rem`). Cart JS querySelectorAll. Desktop giữ nguyên. test 7/7+20/20, upgrade RC=0, v=1118. → chapter 21 |
| 14 | 2026-06-11 | **Mobile bottom sheet "Thêm chức năng" + BlankShell chuẩn** (Figma WJ_MoreBottom 4477:242 + WJ_Mobile_BlankShell 4447:11). Tab "Thêm" gỡ toggle sidebar interim Sprint 12 → sheet thật trượt lên TRÊN footer (backdrop #111827 28%, z 1028/1029 < footer 1030): 7 row (6 Figma + **Báo cáo ngoài Figma** — user chốt giữ đường vào /portal/reports/orders). JS mới `wujia_mobile_more_sheet.js` (tab/backdrop/close/ESC + scroll-lock + tab active cyan khi mở). **BlankShell** = class `.wujia-mpage` (pad-x 16/gap 14/pad-bottom 96, tiêu thụ token Sprint 12 chưa ai dùng) cho trang mobile MỚI, KHÔNG retrofit trang cũ. 0 backend. Token `--wujia-msheet-*`, v=1122, manifest 19.0.14.0.0. test 7/7+20/20, upgrade RC=0, 7 route đích 200. → chapter 23 |
| 13 | 2026-06-10 | **Mobile Lịch sử đặt hàng** (Figma frame 4445:4, 2 màn List+Detail). `/portal/purchase-history` thêm bản `d-lg-none` theo Figma (desktop GIỮ NGUYÊN, bọc `d-none d-lg-block`). List: card tìm kiếm (Mã + Từ/Đến + chip Tháng này/Tháng trước/Đã xử lý/Xóa lọc) + list-row (mã·giờ ngày ··· badge + tổng tiền). Detail: 4 card (tóm tắt / thông tin đơn / batch-giao hàng / ghi chú / sản phẩm). **0 field backend mới** — batch_id.name+planned_departure, portal_requester, len(order_line) đều có sẵn. Controller chỉ thêm `q` (ilike name, trigram). **Status = UI tạm** (`MOBILE_STATE_BADGES` tách desktop; "Đang giao" để sẵn chưa wire). Ghi chú dùng `portal_note` (luôn hiện card, rỗng→placeholder). kv value căn TRÁI cột 110px (user feedback). Token `--wujia-mhist-chip-*` + class `.wujia-mhist-*` reuse palette morder. v=1120→1121. test 7/7+20/20, upgrade RC=0, HTTP 200. → chapter 22 |
| 16 | 2026-06-14 | **Mobile Dashboard 3 màn** (Figma `mobile_dashboard` 2474:2, đọc structure qua MCP). Screen_2_Orders 2474:119→`/portal/delivery` mobile (Đơn hàng gần đây + Giao hàng sắp tới + Đổi trả gần đây) / Screen_3_Debt_Knowledge 2474:233→**trang MỚI `/portal/debt`** (module `wujia_portal_debt` = module thứ 19, ADR-007) / Screen_4_Support 2474:346→`/portal/support` mobile (Hỗ trợ nhanh + Thông tin cửa hàng + Giao hàng sắp tới). Desktop GIỮ NGUYÊN (`d-none d-lg-block`). **Helper chung `utils.py`** `get_recent_orders`/`get_upcoming_batches`/`format_batch_departure` + map MOBILE_ORDER/BATCH_BADGES, guard `_fields` (no dep chéo). UI-only (model chưa có): Công nợ "0đ" (account.move Phase 2), Tổng tiền đổi trả "—" (no field), Chat href # ; hotline=company.phone. KPI Công nợ Home→`/portal/debt`. Shell FINAL giữ nguyên (footer đỏ Figma=drift chủ đích). Token `--wujia-mdash-*`, v=1124, manifest layout 19.0.16.0.0/base 19.0.5.6.0/delivery 19.0.1.3.0/support 19.0.3.3.0/debt 19.0.1.0.0. test 7/7+0 FAIL, upgrade RC=0, HTTP 6 trang 200. Gotcha #13 lặp (route mới cần restart). → chapter 25 |
| 17 | 2026-06-15 | **Mobile Ticket Hỗ trợ** (Figma `Mobile_Ticket` 4 màn) **+ sửa Sprint 16: gộp dashboard về Home + XÓA module debt**. (A) 3 trang `wujia_portal_support` bản mobile `d-lg-none .wujia-mpage .wujia-mticket`: List (title+pill Tạo / search param MỚI `q` ilike name\|title / chip lọc scroll-x dùng lại `state`: Tất cả/Mới/Đang xử lý/Có phản hồi=waiting_customer / list-row + Empty màn 4) / Create (3 chip ưu tiên radio ẩn `:has(input:checked)`, **Gấp+Khẩn→urgent UI-only** note BA / upload) / Detail (meta + **bubble chat** khách trái xám / HQ phải cyan: `msg.author_id.id == created_by_id.partner_id.id` + reply box, route POST CŨ). KHÔNG thêm route (reuse) → no Gotcha #13. Token `--wujia-mticket-*` + class `.wujia-mticket-*`, reuse `.wujia-mknow-search*`+`.wujia-mdash-*`. Map MỚI `MOBILE_TICKET_BADGES` (`utils.py`). (B) **3 màn dashboard Sprint 16 gộp về Home** dedupe 6 section (Đơn hàng/Giao hàng/Đổi trả/Kiến thức/Hỗ trợ nhanh/Thông tin CH, comment "BA reviewing"); strip delivery (bỏ mdash + bỏ d-none d-lg-block) + support (= ticket list). Home controller thêm `m_upcoming_batches`/`articles`(guard registry)/`m_hotline`/badges; `MOBILE_RETURN_BADGES` chuyển delivery→utils. (C) **Công nợ BỎ hẳn** (build sau): KPI Công nợ → `<div>` inert "0₫". (D) **XÓA HẲN `wujia_portal_debt`** (uninstall+rm dir+dọn CSS) → /portal/debt 404, **module 19→18**. v=1125, manifest layout 19.0.17.0.0/base 19.0.5.7.0/support 19.0.3.4.0/delivery 19.0.1.4.0. test 7/7+21/0, upgrade RC=0, HTTP 4 trang 200 + /portal/debt 404, ticket demo `WJ-TK/26/00040` bubble 2 phía OK. → chapter 26 |
| 15 | 2026-06-12 | **Mobile Kiến thức** (Figma WJ_Knowledge_Mobile 4475:2, ảnh phẳng). `/portal/knowledge` + `/<slug>` bản `d-lg-none`; desktop GIỮ NGUYÊN. **Consumer ĐẦU TIÊN của `.wujia-mpage`** (fix double padding: bỏ pad-bottom 96 vì app-content đã clearance; block đặt NGOÀI content-wrapper). List: search + chips functional, "Bài nổi bật" + đếm bài = **UI-only** (chốt user — wire controller sau), icon chung file-text. Detail: badge important→ĐỎ (Figma, tách desktop), body CSS (bullet cyan/blockquote xám/`div.wujia-note` cam), **đính kèm DOWNLOAD THẬT** — route mới `/portal/knowledge/<slug>/attachment/<id>` (published + thuộc bài, att lạ 403). Token `--wujia-mknow-*`, v=1123, manifest 19.0.15.0.0 + 19.0.3.3.0. test 7/7+20/20, upgrade RC=0. Gotcha #13: `--dev=reload` không bắt route mới → restart. → chapter 24 |
| 19 | 2026-06-21 | **Chuẩn hóa UI theo BA Source Component** (BA giao `WujiaTea/UI/mobile_source_ui_v2_3` + `pc_source_ui_v1_4`). **(A) Token reconcile** `_variables.css` về BA source-of-truth: brand `#22A9DE→#28A9DF` (BA CẤM #22A9DE), danger `→#EF4444`, success `→#16A34A`, page bg `→#F3F6F8`, border-soft `→#EEF2F5`, muted `→#8A939E` → desktop+mobile brand ĐỒNG NHẤT; alias `--wj-*`/`--wj-pc-*`; sync seed notification (noupdate) + JS report fallback. **(B) Canonical `wj-*`** gom duplicate thật (modifier giữ visual): FilterChip 3→`wj-filter-chip`(`--soft`/`--wrap`/`--clear`), CountMeta 3→`wj-count-meta`(`--bold`/`--primary`), EmptyState mobile 3→`wj-empty-state`(`--card`/`--compact`/`--rich`); migrate knowledge/support/history/catalog/base, xóa CSS+token chết. **(C)** search-bar/title-row/form-field/menu-row = screen-tuned per-Figma → GIỮ (không ép gộp). Desktop `.wujia-empty-state` (13 view) giữ nguyên. v=1128→1130, layout 19.0.18.0.0. Verify upgrade RC=0 91 mod, test 7/7+21/0, HTTP 14/14 trang 200, render canonical 0 class cũ, brace 470/470. ⚠️ tree còn Sprint 18 chưa commit. DEFERRED: PC reconcile `pc_source_ui_v1_4`, full screen-rework+QA, unify card-radius, comment-trim toàn repo. → chapter 28 |
| 18 | 2026-06-21\* | **Mobile Account / Tài khoản** (Figma Mobile_Account_Info, 4 màn) — *build session trước, commit `d28bd3b` + push cùng S19 (tách commit)*. 01 Thông tin tài khoản (`profile_page.xml`) / 02 Thông tin cửa hàng (`portal_franchise_information.xml`) / 03 Đổi mật khẩu (`change_password_page.xml` + JS MỚI `wujia_password_toggle.js` eye-toggle) / 04 Avatar dropdown header (`mobile_header.xml`). Controller `_resolve_active_store`. Token/class `--wujia-maccount-*`, BlankShell `.wujia-mpage`. 6 file +310/-10. Verify (trong S19): upgrade RC=0, `/portal/profile` 200. → chapter 27. \*=commit date, build sớm hơn. |
| 21 | 2026-06-22 | **Mobile Product/Cart v2 + Order History v2** (chuẩn hoá theo BA Figma copy, dùng canonical `wj-*` S19, desktop giữ nguyên, UI-only). **(A) Product/Cart v2** (`4575:777` → `wujia_portal_sale`): catalog `<select>`→**chips** `wj-filter-chips`/`wj-filter-chip--soft` (link `?category_id`, giữ keyword) + title-row `wj-count-meta` + product **card-per-row** (h58 gap6) + thumb text ĐVT + add btn 46×32 + **qty badge green→cyan** (token `--wujia-morder-qty-badge`→primary, blast radius 1); cart title-row + back 38px + **warnbar khung giờ MỚI** (reuse `.wujia-morder-warnbar`, BE `portal_order_cart_view` +`order_window_enabled`/`order_time_from/to` reuse `_float_to_hhmm`+`_is_within_order_window`) + cart **card-per-row** (h76) thumb40 text + meta 1 dòng + stepper 106×28 `#F8FAFC` + del 28×28 góc phải + summary **giữ sticky** restyle. JS `portal_order.js` KHÔNG đổi (giữ class/data-attr). **(B) Order History v2** (`4577:1112` → `wujia_portal_purchase_history` `portal_history.xml`): list title-row count + search box (icon+placeholder, bỏ head/label) + **order card-per-row** (h54 gap8) badge **đổi màu theo state** (`MOBILE_STATE_BADGES` sẵn có) + detail **PageHeader back-button** 42×42 + kv 12.5px. BE history KHÔNG đổi. Verify upgrade RC=0, browser 390px 4 màn khớp v2, desktop intact, test 21/0+7/0. asset `?v=1133`, sale 19.0.2.5.0 / history 19.0.1.4.0 / layout 19.0.21.0.0. → chapter 30 |
| PC-1 | 2026-06-22 | **PC Foundation/Shell + màn Đặt hàng PC** (BA `pc_source_ui_v1_4` + Figma `4600:2`). **(A)** token `--wj-pc-*` (radius 18/12, table 50/58, metric 96, soft palette) + `_pc_components.css` MỚI 10 component `wj-pc-*` (scoped, zero-blast) + sidebar active → BA (soft `#EAF7FD` + accent bar cyan `::before`) + gallery dev-only `/portal/_pc-preview` (`pc_preview.{py,xml}`, internal). TopHeader verify-only. **(B)** `wujia_portal_sale` màn Đặt hàng **combined** (catalog trái + cart panel phải 1 trang): controller +`cart`/`product_count`/`page_size`/`message`/`error` + `_fallback_pager` numbered+giữ filter; partial `pc_cart_panel.xml` dùng chung (`/portal/order` + `/portal/order/cart` standalone, bỏ SĐT/địa chỉ); table header cyan + nút add **badge qty** + **dòng `wj-pc-order-row--incart`** nền cyan + warning-bar khung giờ + pagination numbered+count; JS `portal_order_pc.js` MỚI stepper/remove live + **sync 2 chiều `syncCatalogBadge`** (cùng tab, no reload), add reload 1 lần; CSS `wj-pc-order/cart-*` + hover đầy đủ. header cart→`/portal/order`. UI-only: Quy cách + tên CN (chờ field). DEFERRED: realtime cross-session bus.bus (§5). Verify upgrade RC=0, render 200 (combined+cart+pager `PAGE_SIZE=2`), test 21/0+7/0. layout 19.0.22.0.0 / sale 19.0.2.6.0, `?v=1134`. → chapter 31 |
| 22 | 2026-06-24 | **Mobile Thông báo (List+Detail) + chuẩn hoá typography heading** (Figma `4651:655`). `wujia_portal_notification` lần đầu có mobile `d-lg-none`: list card-per-row (accent/dot/bold chưa đọc, source `type • dispatch`, badge, date) + detail (type header + mô tả + badges + body + **Liên kết liên quan** + file đính kèm download). Controller +`unread` filter (chip "Chưa đọc" wire read state) + `cnt_unread`/`total`. **UI-only đa dạng icon/màu/badge** derive `type_id.code`→tone+icon / `priority`→badge (map tạm `WJ_*` đầu template, controller sau). **Cross-page:** heading mobile `800→700` theo Figma từng trang (mknow 22/800→25/700, mnoti 22/700, mticket-h1, maccount; search 42→38, noti compact 30; card-title #6B7280→#374151/#111827; GIỮ 800 ở amount/code/PC-grand). history/order/cart 24/700 đã khớp sẵn. layout 19.0.25.0.0 `?v=1138` / notification 19.0.1.4.0. Verify upgrade RC=0, 7 trang 200, test 21/0+7/0. → chapter 32 |
| 20 | 2026-06-22 | **Mobile Đổi trả / Bù hàng** (`wujia_portal_return`, Figma Mobile_Return `4449:81` 4 màn, BA `mobile_source_ui_v2_3` ListScreen). **Chốt: "bù hàng" = "đổi trả" = cùng module** (BA gọi lẫn). 4 màn `d-lg-none .wujia-mpage .wujia-mreturn` (desktop bọc `d-none d-lg-block`): List (PageHeader+search `q`+`wj-count-meta`+ReturnCard `wujia-mreturn-row`+2 empty `wj-empty-state--rich`) / Tạo YC (4 card, single-product, route POST cũ) / Chi tiết (kv reuse `wujia-mhist-kv`+ảnh+Phản hồi HQ). **UI-only**: field Figma chưa có backend (Đã nhận/ngày mở-sản xuất/video/response) input no-`name` không submit; reuse `_parse_payload`. Controller +`q`(ilike name\|order)+`today`. **(C) Fix gốc back-icon kẹt MỌI trang**: Vuexy `.drag-target` (z1036, `left:-10px;width:40px`) phủ mép trái nuốt click icon back → tắt `<768px` ở `_wujia_theme.css` (phone dùng bottom-nav); +tap-target 44px; tiêu đề nowrap (font-boost). return 19.0.1.3.0, layout 19.0.20.0.0, `?v=1131`. Verify upgrade RC=0, browser 390px 3 route 200 khớp Figma, test 21/0+7/0, desktop/tablet intact. → chapter 29 |
| 25 | 2026-07-01 | **Home Mobile Quick Action UI v4** (Figma `#4712:2`): rework block "Hành động nhanh" — layout dọc → ngang, gradient cyan → card trắng `#FFFFFF`, icon circle 32×32 nền `#E9F7FC`/icon cyan 16px, text đen 12px, gap 10px. Section title scope 20px (không ảnh hưởng section title khác 18px). Token mới `--wujia-mhome-action-bg/border/icon-bg`, class mới `.wujia-mhome-action-icon`. 4 file + `?v=1146`. Upgrade RC=0. → chapter 36 |
| 27 | 2026-07-03 | **PC Giao hàng desktop 5 màn** (Figma `4766:858`, batch-centric): rework `/portal/delivery` desktop (trang portal cuối còn legacy) sang hệ `wj-pc-*`. Controller gộp query batch nuôi cả desktop+mobile + `q` search + `_chip_counts` + numbered pager + `view_state`/`?_preview=` drive desktop. Template 2 khối `d-none d-lg-block` (list filterbar/table/pager + chips-count; detail order-head/two-col/timeline 3 bước/SO chips/products). CSS `wj-pc-dlv-*` page-scoped (không đụng `_pc_components`/`_variables`). manifest `→19.0.3.0.0`. Mobile S24 giữ nguyên. Verify upgrade RC=0, Playwright 1920px 5 màn khớp Figma, regression sạch (mobile/history/notification/.ics), test 21/0+7/0. → chapter 38 |
| 26 | 2026-07-01 | **Mobile Đăng ký thi (Exam Registration) 7 màn** (Figma `#4755:2`, board s0–s6). `wujia_portal_exam` lần đầu có mobile (`d-lg-none`, desktop giữ nguyên). s0 `/portal/exam` list (search + badge trạng thái + FAB) + wizard 1-trang-JS s1→s5 `/portal/exam/register` (Chọn khóa thi chips → calendar → **popup Chọn khung giờ** bottom-sheet slot highlight → Nhập nhân sự thêm/xóa → Xác nhận) + s6 `/portal/exam/registration/<id>` Kết quả (Đạt/Không đạt theo người). **UI-only + demo**: hardcode khớp Figma, submit=stub toast, s0 đọc reg thật (else demo); model Phase 2 (course/round, slot capacity, đa nhân sự, kết quả/người). CSS `wujia-mexam-*` + 5 token tint; JS mới `portal_exam_wizard.js`; manifest `19.0.1.1.0→19.0.2.0.0`. **Gotcha**: global `h1,.wujia-h1{...!important}` đè heading → scope+`!important`. Verify upgrade RC=0 91 mod, Playwright 390px 7 màn khớp Figma, interactions OK, fix link card `#`→result route. → chapter 37 |
| 28 | 2026-07-07 | **PC Tài khoản 9 màn** (Figma `wujia_pc_01..09_v3`, page 4792): 3 trang desktop rework — `/portal/profile` (chỉ đọc, header card + KV boxed + note HQ), `/portal/franchise-information` (3 state owner-members/empty/staff suy từ `membership.role`), `/portal/change-password` (4 state error/message, viền đỏ field suy từ chuỗi lỗi) — + dropdown avatar (frame 09) + **rework toàn bộ sidebar** (1 view `priority=99` + `position=replace`: menu Figma Trang chủ/Đặt hàng/Lịch sử/Giao hàng/Công nợ/Thông báo/Kiến thức/Hỗ trợ/Đăng ký thi + TIỆN ÍCH/Tài khoản active). Shell chung `pc_account_shell.xml` (nav card trái + page-header) + `_pc_account.css` page-scoped (blast radius 0). Controller: 3 chuỗi lỗi khớp Figma + franchise context cho change-pw. Verify upgrade RC=0 91 mod, Playwright 1920px 8/9 frame khớp Figma, test_sprint9 7/7, 15/15 route 200 (4 mục bỏ khỏi menu vẫn sống). → chapter 39 |

→ Chi tiết: `chapters/04-17.tex` + `chapters/18-sprint9-issue-list-ui-refactor.tex` (cuối Sprint 9) + `chapters/19-sprint10-mobile-home-figma.tex` + `chapters/20-sprint11-mobile-order.tex` + `chapters/21-sprint12-mobile-shell-final.tex` + `chapters/22-sprint13-mobile-order-history.tex` + `chapters/23-sprint14-mobile-more-sheet.tex` + `chapters/24-sprint15-mobile-knowledge.tex` + `chapters/25-sprint16-mobile-dashboard-3screens.tex` + `chapters/26-sprint17-mobile-ticket.tex` + `chapters/27..29` (S18 account / S19 chuẩn hóa / S20 đổi trả-bù hàng) + `chapters/30-sprint21-mobile-product-cart-history-v2.tex` + `chapters/31-sprintpc1-pc-foundation-and-order.tex` + `chapters/32-sprint22-mobile-notification.tex` + `chapters/33-sprint23-mobile-figma-spacing.tex` + `chapters/34-sprintpc3-pc-notification.tex` + `chapters/35-sprint24-mobile-delivery.tex` + `chapters/36-sprint25-home-quick-action-v4.tex` + `chapters/37-sprint26-mobile-exam-registration.tex` + `chapters/38-sprint27-pc-delivery.tex` + `chapters/39-sprint28-pc-account.tex`.

---

## §5 wujia-current-status

**State (2026-07-07) — SPRINT 28 DONE: PC Tài khoản 9 màn theo Figma `wujia_pc_01..09_v3` (page 4792), `wujia_portal_layout` + `wujia_portal_base`, chapter 39.** 18 module active. _(Trước: Sprint 27 PC Giao hàng desktop, chapter 38.)_
- **S28 — PC Tài khoản (Figma `wujia_pc_01..09_v3`, 9 màn 1920×1080):** rework 3 trang account desktop (nhóm màn cuối còn layout Vuexy cũ) sang hệ `wj-pc-*`, UI-only, mobile S18 `d-lg-none` GIỮ NGUYÊN. **Shell chung** file mới `pc_account_shell.xml` (`pc_account_layout`, id global cho cả base t-call): page-header (crumb/title/subtitle) + grid 2 cột (**nav card trái** avatar+tên+role+store pill+3 mục active-cyan-accent + Đăng xuất đỏ | content `t-out=0`); mỗi trang `t-set acct_page/title/subtitle/store/role`, nav card đọc `request.env.user` trực tiếp. **(01/09) `/portal/profile` CHỈ ĐỌC** (user chốt, HQ quản lý): header card (avatar 92 + tên + email + chip role/status + box "Cửa hàng hiện tại") + panel KV **boxed** `#F8FAFC` 6 field + note-bar; bỏ form sửa (route `/update` còn sống, no UI). **(02/03/04) `/portal/franchise-information`**: header card (icon + code·name + badges + box "Quyền xem hiện tại") + KV 3 cột + panel "Thành viên" **3 nhánh suy từ `membership.role`** (owner+members=table+pager / owner+rỗng=`wj-pc-empty` / staff=panel hạn chế + chip "Chế độ xem cơ bản") — không đổi controller. **(05/06/07/08) `/portal/change-password`**: form giữa (3 field + nút text "Hiện" reuse `wujia_password_toggle.js` mở rộng selector) + aside phải (Lưu ý bảo mật / Cần hỗ trợ) + 4 state qua `error`/`message`, **viền đỏ field suy từ nội dung `error`** (chứa "hiện tại không đúng"→cũ; "xác nhận không khớp"→confirm), nút Lưu success=`wj-pc-btn--disabled`. **Controller** `wujia_portal_layout/controllers/portal.py`: 3 chuỗi khớp Figma ("Mật khẩu hiện tại không đúng. Vui lòng kiểm tra lại." / "...xác nhận không khớp với mật khẩu mới." / "...đã được cập nhật thành công.") + thêm `franchise_name/code/role_label` vào context change-pw (reuse `_resolve_active_store`). **(09) dropdown avatar** `layouts.xml` restyle (`wj-pc-acct-menu`, active theo `request.httprequest.path`, thêm mục "Thông tin cửa hàng", VN hoá). **Sidebar rework toàn cục** file mới `pc_sidenav.xml`: **1 view `priority=99` + `position=replace`** trên `layout_sidenav` (chạy sau 10 inject module, xoá `<ul>` chèn → thay menu Figma inline) → KHÔNG phải sửa 10 module. Menu: Trang chủ/Đặt hàng/Lịch sử đặt hàng/Giao hàng/**Công nợ (UI-only→`/portal`)**/Thông báo/Kiến thức/Hỗ trợ/Đăng ký thi + **TIỆN ÍCH/Tài khoản** (active cyan cả 3 trang account qua `_acct_active`). CSS mới `_pc_account.css` (`wj-pc-acct-*`, hex Figma-exact slate/`#CC5138`/`#D9E7EF`/`#F8FAFC`, blast radius 0), `?v=1147`. Verify upgrade RC=0 91 mod, Playwright 1920px **8/9 frame khớp Figma** (03 rỗng verify cấu trúc — người xem luôn là 1 member), `test_sprint9` 7/7, **15/15 route 200** (Đổi trả/Cập nhật thông tin/Báo cáo/Cửa hàng bỏ khỏi menu vẫn vào qua URL), desktop delivery/notification/home + mobile account intact. → chapter 39. ⚠️ **Pending/deviation**: (a) frame 03 (0 thành viên) không test được với data thật; (b) **store pill header** vẫn badge "Owner" cam (component chung sprint trước) ≠ Figma "· Quản lý" cyan — chưa đụng (blast radius toàn portal, chờ user quyết); (c) logo "Your logo" local = `company.logo_web` chưa set (prod OK); (d) tree còn WIP song song "Mobile Filter canonical" (`wj-filter-*`, 7 module + `_components.css`) chưa commit — KHÔNG thuộc S28.
- **S27 — PC Giao hàng desktop (Figma `4766:858`, 5 màn 1920×1080):** desktop `/portal/delivery` là trang portal **cuối cùng còn legacy** (bảng picking-centric + `wujia-content-card`/`wujia-badge-*`) → rework sang **batch-centric** trên hệ `wj-pc-*` (UI-only, mobile S24 `d-lg-none` GIỮ NGUYÊN). **Controller** gộp query batch nuôi **cả desktop + mobile** (dict batch thêm keys PC `pc_label/pc_modifier/departure_full/vehicle/plate/updated`, không đụng keys mobile) + `q` search (mã chuyến/SO) + `_chip_counts` (4 `search_count` Tất cả/Đang giao/Sắp giao/Đã giao, field index) + `_page_numbers` (pager numbered) + `view_state`+`?_preview=` giờ **drive luôn desktop** (5 state). Detail thêm `pc_badge/pc_orders/so_names/tl_steps/tl_times/src_location/store_label`; bỏ 2 map legacy. **Template** thay 2 khối `d-none d-lg-block` (list `wj-pc-page-header→filterbar→card→table→pagination`; detail `wj-pc-order-head + wj-pc-two-col + kv-grid + timeline 3 bước + SO chips`). **CSS** `wj-pc-dlv-*` page-scoped trong `portal_delivery.css` (badge dlv-going/soon/done hex Figma `#EAF7FD/#FEF3C7/#DCFCE7`, chips-count, skeleton 7×7, panel empty/error, timeline dot 26, codelink dark, title 32/crumb-trên scoped) — **KHÔNG đụng `_pc_components.css`/`_variables.css`** (giữ `?v=1141/1146`, blast radius 0). manifest `→19.0.3.0.0`. Verify upgrade RC=0, Playwright 1920px 5 màn khớp Figma, mobile 390px intact + history/notification desktop intact + `.ics` 200 + 0 legacy badge, test 21/0+7/0. → chapter 38. ⚠️ **UI-only/pending**: Export + Tải danh sách + "10/trang" chưa wire; Tải lại=reload; native date input (house pattern); default date trống.
- **S26 — Mobile Đăng ký thi (Figma `#4755:2`, 7 màn s0–s6):** `wujia_portal_exam` lần đầu có mobile (`d-lg-none`, desktop bọc `d-none d-lg-block`). **s0** `/portal/exam`: title/subtitle + search card (từ ngày–đến ngày + "Tất cả" + nút tìm) + list card (badge Đã đăng ký/Chờ duyệt/Có kết quả) + FAB "+ Đăng ký mới". **Wizard 1 trang JS** `/portal/exam/register` (s1→s5, step 1/4→4/4): Chọn khóa thi (chips lọc client-side, card "Đã đóng" mờ) → **calendar** Chọn lịch thi (ngày còn chỗ viền cyan + chấm) → tap ngày mở **popup Chọn khung giờ** (bottom-sheet slide-up + backdrop + ESC; slot chọn sáng lên viền cyan+check, "Hết chỗ" disabled) → Nhập nhân sự (thêm/xóa/đánh-số-lại người, form Họ tên/SĐT/Năm sinh/Chức vụ) → Xác nhận (KV lịch thi + nhân sự, ngày/giờ tự đổ theo lựa chọn). **s6** `/portal/exam/registration/<id>` Kết quả: summary + Danh sách kết quả (✓ Đạt xanh / ✗ Không đạt đỏ + điểm/người) + info note + CTA. **UI-only + demo**: nội dung hardcode khớp Figma, submit=stub (toast "Đã gửi yêu cầu đăng ký!" → redirect); s0 build `m_exam_items` từ reg thật (else demo); card thật link `/portal/exam/registration/<r.id>`. Controller demo `DEMO_COURSES/SLOTS/PEOPLE/RESULT` + `_build_demo_calendar()`. CSS `wujia-mexam-*` (@media <992px) + 5 token tint mới; JS mới `portal_exam_wizard.js`; manifest `→19.0.2.0.0`. Verify upgrade RC=0 91 mod, Playwright 390px 7 màn khớp Figma, interactions OK, regression Home/Noti intact. → chapter 37. ⚠️ **Phase 2**: build model `wujia.exam.course/round` + `wujia.exam.slot` (capacity→Còn/Hết chỗ) + `registration.person` (đa nhân sự) + kết quả theo người; s6 gắn data thật theo reg_id + phân nhánh trạng thái (Đã đăng ký→màn trạng thái, Có kết quả→bảng điểm); submit thật race-safe.
- **S25 — Home Mobile Quick Action UI v4 (Figma `#4712:2`):** rework block "Hành động nhanh" trên Home mobile. Grid giữ 3 cột, gap `10px`. Card: layout dọc → **ngang** (flex-row), bg gradient → **`#FFFFFF`**, border `#EEF2F5`, height **58px** fixed, border-radius 12px. Thêm `.wujia-mhome-action-icon` (circle 32×32 bg `#E9F7FC`, border-radius 8px); icon Feather 16px màu cyan `#28A9DF` bên trong. Label: 14px trắng → **12px `#1F2933`**. Section title scoped **20px** (các section title khác 18px). Tokens: xóa `--wujia-mhome-action-grad`, thêm `--wujia-mhome-action-bg/border/icon-bg`. 4 file: `_variables.css` + `_components.css` + `portal_home.xml` + `assets.xml` (`?v=1146`). Upgrade RC=0, 91 modules. Desktop giữ nguyên. → chapter 36.
- **S24 — Mobile Giao hàng (Figma 4731:2, 5 màn):** `wujia_portal_delivery` lần đầu có mobile `d-lg-none .wujia-mpage .wujia-mdelivery` (desktop bảng picking GIỮ NGUYÊN). **List batch-centric** (1 thẻ = 1 chuyến xe): controller +query `stock.picking.batch` franchise-scoped (qua `picking_ids.franchise_id`/`sale_id.franchise_id`) + lọc ngày `planned_departure` (`date_from/to`) + chip nhóm `bs` (soon=draft/assigned/loading, going=delivering, done) + map badge/departure/orders; **5 `view_state`** (list/empty/error via try/except/loading) + QA `?_preview=`. **Detail** dùng route batch sẵn có + gom `own_pickings.move_ids` → bảng SP; Xe/tài xế/biển số từ `batch.vehicle_id`. Reuse canonical (mpage/mdash-card/mhist-kv/wj-filter-chip--soft/wj-empty-state--rich/mticket-h1) + `wujia-mdelivery-*` (badge token soon `#FEF3C7`/done `#ECFDF5`, icon Xuất phát = **lịch cyan**). 2 pager tách (desktop/mobile). manifest `19.0.1.4.0→19.0.2.0.0`; CSS auto-bundle. Verify upgrade RC=0, Playwright 390px 5 màn khớp Figma, desktop 1440 intact, return/history smoke OK. → chapter 35. ⚠️ Loading skeleton UI-only (server-render no async, chừa cho AJAX); date filter trống mặc định; thẻ giữ viền 1px (đồng bộ trang khác, khác Figma phẳng).
- **PC-3 — PC Notification desktop (Figma 4683:101/2/285):** thay khối desktop `/portal/notification` bằng hệ `wj-pc-*`, giữ nguyên mobile S22. **List:** page header + nút "Đánh dấu đã đọc" (bulk, JS `portal_notification_pc.js` dùng endpoint `mark-read` sẵn có) + filter bar 5 field có label 1 hàng (grid) + chips **ngoài** card (Tất cả/Chưa đọc/Quan trọng/Cần làm) + bảng `wj-pc-table` (type chip xám, dòng chưa đọc thanh cyan via **box-shadow inset** + dot, badge Chưa đọc đỏ/Đã đọc xám). Controller +`date_from`/`date_to`/`priority`. **Form:** `wj-pc-two-col` (nội dung trái + Thông tin/Tài liệu phải, Mã→`dispatch_number`, bỏ "Liên kết liên quan" no-field). **Popup:** chuông header → dropdown **lazy-load** endpoint MỚI `/portal/notification/recent` (JSON, ~3 query chỉ khi mở, 0 query/page-load) card-per-item (icon tone, chip ưu tiên + "Có file", dot+date); desktop intercept `matchMedia`, mobile giữ link. **Audit Figma (Playwright + 3 sub-agent)** bắt & fix: filter wrap (`.wj-pc-filter-search flex:280px` thành **chiều cao** trong flex-column → grid + reset flex), bảng tràn viền (`tr::before` bị table coi như **cell phụ** → box-shadow), chips ra ngoài card, popup chip gọn (base badge 28px → `padding:3px 8px;font-size:11px`). Seed `seed_notification_demo.py` (9 demo). manifest `19.0.1.6.0`. Verify upgrade RC=0, test 21/0+7/0, 4 route 200, Playwright 3 màn khớp Figma. → chapter 34. ⚠️ **2 GOTCHA mới:** (a) `tr::before` trong table = 1 cell phụ → đẩy lệch cả hàng, dùng `box-shadow inset` cho accent bar; (b) `flex:N px` đổi trục khi bỏ vào flex-column (basis thành height) → reset flex theo trục mới.
- **S23 — Chốt sổ UI mobile theo Figma (batch 1):** đưa spacing/typography 6 trang mobile khớp số đo Figma (copy `aoeiDYlg6vlhJZg2w6Q7o5`). **Gốc rễ 2 cơ chế top-pad:** BlankShell `.wujia-mpage` = 14px (ngoài content-wrapper); trang cũ (Đặt hàng/Giỏ/Lịch sử) trong `.content-wrapper` dính `padding-top:24px` desktop (override mobile chỉ tắt margin-top, không tắt padding-top) → ~28px = lý do "Sản phẩm xa header". Fix top-pad nhóm content-wrapper bằng `.content-wrapper:has(.wujia-morder/.wujia-mcart/.wujia-mhist)` trong `@media <992px` (desktop giữ 24px). Theo Figma từng trang: **Đặt hàng** top ~28→12, title 24→25, search 44→34/#F9FAFB, chip 30; **Thông báo** top 14→10, count 700, chip 12; **Giỏ** top→12; **Lịch sử** top→5, search 42→38, chip 28/12; **Đổi trả** top→16, title 22→26 (scoped `.wujia-mreturn .wujia-mticket-h1`, Hỗ trợ giữ 22), search 36; **Kiến thức** top→11, count--primary 700; base `.wujia-mknow-search-input` bg #F3F6F8→**#F8FAFC** (1 chỗ đúng cho knowledge/ticket/return/noti). `_components ?v=1145` / `_wujia_theme ?v=1145`; layout `→19.0.28.0.0`, notification `→19.0.1.5.0`, return `→19.0.1.4.0`. Verify upgrade RC=0, test 7/7+21/0, curl static OK. **CHƯA soi 390px (sign-off thị giác user) — batch 2.** → chapter 33.
- **Sprint PC-2 — History desktop wj-pc-* (Figma 4643):** rework `/portal/purchase-history` desktop theo `pc_source_ui_v1_4` (DataTable/badge/KV panel/pagination) + `_pc_components.css` thêm component (status badge, sub-count, KV panel, table footer, 2-col), `portal_order.css` stepper/badge ring, `layouts.xml` "MENU CHÍNH" header. Code anh làm session trước, **chưa có chapter riêng** (commit cùng đợt S23). layout 19.0.27.0.0 / history 19.0.1.6.0 / sale 19.0.2.7.0, `_pc_components ?v=1141`.
- **S22 — Mobile Thông báo (List+Detail) + typography heading:** `wujia_portal_notification` lần đầu có mobile `d-lg-none` (Figma `4651:655`): list card-per-row (accent/dot/bold chưa đọc) + detail (type header + mô tả + badges + **Liên kết liên quan** + file đính kèm download). Controller +`unread` filter (chip "Chưa đọc" wire) + `cnt_unread`/`total`. UI-only đa dạng icon/màu/badge derive `type_id.code`/`priority` (map `WJ_*` đầu template). **Cross-page fix:** heading `800→700` theo Figma (mknow 22/800→25/700, mnoti, mticket-h1, maccount; search 42→38, noti compact 30; card-title #6B7280→#374151/#111827; GIỮ 800 ở amount/code/PC-grand). layout `19.0.25.0.0` `?v=1138` / notification `19.0.1.4.0`. Verify upgrade RC=0, 7 trang 200, test 21/0+7/0. → chapter 32.
- **Fix (2026-06-23, follow-up Sprint 10/chapter 19) — lề kép home mobile:** root cause = Vuexy `.content-wrapper` có padding ngang ~16.8px CỘNG DỒN với `.wujia-mhome` → lề ~27-33px thay vì 16px BA. Fix: `.wujia-mhome` về `padding:16px` (BA) + class `wujia-home-wrapper` trên content-wrapper home + CSS scoped `@media <992px` bỏ padding-x content-wrapper CHỈ ở home → inset DUY NHẤT 16px. `_components.css ?v=1136`, base `19.0.5.10.0` + layout `19.0.24.0.0`. Verify upgrade RC=0 + browser 390px hero left=16px (trước 27px), cả trang thẳng hàng. **CHƯA COMMIT.** ⚠️ Trang mobile khác (`.wujia-mpage`) cũng dính lề kép tương tự — chưa sửa (chỉ user yêu cầu home).
- **PC-1 — PC Foundation/Shell + màn Đặt hàng PC:** **(A)** token `--wj-pc-*` + `_pc_components.css` MỚI (10 component `wj-pc-*`, scoped zero-blast, radius 18/12 table 50/58 metric 96 soft palette) + sidebar active → BA (soft `#EAF7FD` + accent bar cyan) + gallery dev `/portal/_pc-preview`. **(B)** `wujia_portal_sale` Đặt hàng **combined** (Figma `4600:2`): catalog trái + cart panel phải 1 trang, partial `pc_cart_panel` dùng chung cho `/portal/order/cart` standalone (bỏ SĐT/địa chỉ), table header cyan + add **badge qty** + **dòng in-cart nền cyan** + stepper live + **sync 2 chiều cart↔catalog** (cùng tab, no reload) + warning-bar khung giờ + pagination numbered+count; controller +cart/product_count/page_size + `_fallback_pager` numbered & giữ filter. layout 19.0.22.0.0 / sale 19.0.2.6.0, `?v=1134`. Verify upgrade RC=0, render 200, test 21/0+7/0. → chapter 31.
- **S21 — Mobile Product/Cart v2 + Order History v2:** chuẩn hoá v2 theo BA Figma (`4575:777` + `4577:1112`), tinh chỉnh kích thước component + canonical `wj-*` S19. Product/Cart: chips danh mục thay select, card-per-row, qty badge cyan, **warnbar khung giờ wire vào giỏ** (BE read-only), summary sticky restyle. Order History: list card-per-row + badge đổi màu theo state + search box icon, detail back-button. Desktop giữ nguyên, UI-only. asset `?v=1133`, sale 19.0.2.5.0 / history 19.0.1.4.0 / layout 19.0.21.0.0. Verify upgrade RC=0, browser 390px 4 màn khớp v2, test 21/0+7/0. → chapter 30.
- **S20 — Mobile Đổi trả / Bù hàng** (`wujia_portal_return`, Figma `4449:81` 4 màn): List + Tạo YC + Chi tiết theo BA `mobile_source_ui_v2_3`, UI-only (wire field có sẵn, gap để no-submit). **"bù hàng" = "đổi trả" = cùng module.** Class mới `wujia-mreturn-*`, reuse `wj-*`/`wujia-mhist-kv`/`wujia-mticket-*`. **Fix gốc back-icon kẹt toàn portal**: tắt Vuexy `.drag-target` (z1036 phủ mép trái) ở `<768px` trong `_wujia_theme.css`. return 19.0.1.3.0, layout 19.0.20.0.0, `?v=1131`. Verify upgrade RC=0, browser 390px 3 route 200, test 21/0+7/0. → chapter 29.
- **S19 — Chuẩn hóa UI theo BA Source Component:** token `_variables.css` unify về BA (brand `#28A9DF` bỏ `#22A9DE`, danger `#EF4444`, success `#16A34A`, bg `#F3F6F8`); alias `--wj-*`/`--wj-pc-*`; canonical `wj-filter-chip` / `wj-count-meta` / `wj-empty-state` (gom duplicate thật, modifier giữ visual 100%). search-bar/title-row/form-field = tuned per-Figma → GIỮ. Comment CSS trim. asset v→1130, manifest layout 19.0.19.0.0 + 5 module. Verify: upgrade RC=0 91 mod, test 7/7+21/0, HTTP 14/14 trang 200, render 0 class cũ. → chapter 28.
- **S18 — Mobile Account 4 màn** (Thông tin tài khoản / cửa hàng / đổi mật khẩu + JS eye-toggle / avatar dropdown header). Token/class `--wujia-maccount-*`, BlankShell `.wujia-mpage`. commit `d28bd3b` (build session trước). → chapter 27.
- **▶ NEXT — S23 batch 2 (chốt sổ mobile tiếp):** soi 390px sign-off thị giác TỪNG trang cùng user (đặc biệt Thông báo top-pad 10px Figma — ngược cảm giác "chật", xác nhận store-strip render); pull Figma reconcile **Hỗ trợ + Tài khoản**; soi nhẹ **Home**; ~~Delivery chờ frame BA~~ → **Delivery DONE (S24, chapter 35)**. _(nudge tại chỗ nếu vẫn lệch: Đặt hàng 24→25 chỉ +1px, Lịch sử top 5px rất sát.)_
- **▶ NEXT SESSION: tiếp PC/desktop.** (1) **Realtime cart không-reload cross-session** (bus.bus + controller publish — xem bullet DEFERRED dưới); (2) ráp các trang desktop còn lại theo `pc_source_ui_v1_4` (history/report/return/knowledge/support/home — "từng trang sửa sau"). Pending S22: wire controller cho chip "Quan trọng"/"Cần làm" + badge ưu tiên + field mô tả-loại / "Liên kết liên quan" (hiện UI-only/static); soi size title px riêng cho ticket/return/account (mới sửa weight 800→700). Pending mobile cũ: status giao hàng batch thật (S13); khung giờ cart submit (S11); i18n `.po`; field bù hàng Phase 2 (S20). UI-only PC: Quy cách + tên CN (chờ field BA).
- **DEFERRED (S19, làm sau):** PC/desktop reconcile theo `pc_source_ui_v1_4` (DataTable/MetricCard/Modal/Pagination/Sidebar/TopHeader, radius 18, padding 24); full per-screen rework + QA checklist; unify `--wujia-card-radius`; migrate `bg_color` notification trên DB (noupdate); trim comment file Python/XML.
- **DEFERRED (Sprint PC-1 note → session sau, làm với controller) — REALTIME cart không-reload:** PC Order combined `/portal/order` hiện: add từ catalog → **reload 1 lần**; sửa trong giỏ (stepper ±/xoá) → **live cùng-tab** (JS `syncCatalogBadge` cập nhật panel + badge catalog + highlight). User chốt UI vầy OK sprint này. Cần làm sau: (a) bỏ reload-on-add → update DOM cart panel live (chèn/tăng dòng, empty→populated); (b) **CROSS-SESSION/CROSS-DEVICE** (doc BA: realtime cho ~1500 user): account login 2 máy, máy A đổi cart/data → máy B tự nhảy KHÔNG reload. Hướng: **`bus.bus`** Odoo native (đã dùng noti — ADR-006) publish per-user channel khi cart mutate (add/update/remove/submit) → client subscribe reconcile. Backend đã race-safe (atomic SQL UPDATE…RETURNING ở `/cart/add`) → realtime layer chỉ broadcast state. **Phân loại: UI/JS + publish controller, KHÔNG phải lỗi backend** (endpoint đã lưu DB đúng, reload là thấy đúng). Files: `wujia_portal_sale/static/src/js/portal_order_pc.js` + `portal_order.js` + `controllers/portal.py` + `views/pc_cart_panel.xml`.

> _State chi tiết sprint 9–17 đã GỠ khỏi §5 (giữ compact) → xem `chapters/` + bảng §4._

**Phase 1.0 (BA order) — ✅ HOÀN TẤT 2026-06-04:** toàn bộ 9.1→9.24 done (UI-01..UI-18 + empty state + cleanup + verify + doc + push). **Sprint 9 100% DONE + PUSHED.** Chi tiết status từng issue → §9 bảng.
- Defer (chưa làm, ngoài Sprint 9): T-031 mockup ops, locust 100+ load test, affiliate v14 gap, Dashboard ApexChart, TOTP 2FA, Calendar booking, QR scan, MẪU 03-06 từ `docs/sample.jpg`, i18n `.po` (Sprint 10).

**Phase 2.0 (future):** Employee Mgmt / Debt Overview / Payment History / Training Reports / User Invitations.

**Non-negotiable rules cho mọi session:**
- ⚠️ **ĐỌC SOURCE TRƯỚC KHI SỬA — KHÔNG ĐOÁN tên model/field/method.** `grep -rn "_name = '" custom/<mod>/models/` + `grep -rn "def <method>" custom/`. Tên thực: `wujia.franchise.management` (NOT `res.franchise`), `wujia.franchise.member`, `wujia.order.window`, `res.area`, `res.ward`. Helper portal: `get_active_franchise_id()` / `get_active_franchise_ids_filter()` ở `wujia_portal_base/controllers/portal.py` (KHÔNG `utils.py`).
- ⚠️ **REGRESSION CHECK — XEM CÁC UI CŨ TRƯỚC KHI FIX UI MỚI.** Trước khi sửa CSS/token/template cho 1 issue mới, BẮT BUỘC:
  - `grep -rn "<selector|token|class>" custom/` xem rule hiện có ai dùng → tránh sửa nhầm style chung làm UI cũ vỡ (vd token `--wujia-card-radius` ảnh hưởng MỌI `.card`, `--wujia-text-primary` ảnh hưởng MỌI text — phải hiểu blast radius).
  - Đọc lại §9 "Files đã chạm" của các sprint con trước để biết file/selector nào đã touch và spec ràng buộc nào còn áp.
  - Sau khi ship: visual smoke 3-5 page khác (không chỉ page đang sửa) để bắt regression. CSS scope càng global thì test càng rộng.
  - Cụ thể với token typography/color/radius/spacing: bump = side-effect toàn portal, KHÔNG inline override.
- CSS bắt buộc dùng `var(--wujia-*)` trong `_variables.css` + class share `_components.css` (`.wujia-btn`, `.wujia-badge-*`, `.wujia-empty-state`, `.wujia-content-card*`, `.wujia-kpi-card*`). Không hex cứng.
- Demo data: KHÔNG vào manifest XML → `scripts/seed_*.py` local-only.
- View Odoo 19: không `attrs=`, không `decoration-secondary`, group search `name="group_by"`, **bỏ `expand="0"` ở `<group>` search**, **`_sql_constraints` → `models.Constraint`**.
- Commit: English Conventional Commits. Không `--no-verify`.
- **Comment GỌN** (user 2026-06-22): ít comment, không banner `===` dài; 1 dòng ngắn đủ ý (vd `<!-- Mobile <992px — Figma X (Sxx) -->`). Không comment hiển nhiên.
- Field rename: pre-migrate trước `-u` để tránh drop column.
- i18n: code English, BA dịch `vi_VN.po` (defer Sprint 10).

→ Chi tiết: `wujia-tea-doc.tex` §1.4.

---

## §6 wujia-deploy

**Sprint 5 đã deploy.** Sprint 9.x deploy qua `git pull` + restart (no schema change). Field rename → cần `reseed_full.ps1` drop+init khi skeleton.

**⚠️ GOTCHA DEPLOY — MODULE MỚI KHÔNG TỰ CÀI (note 2026-06-14, Sprint 16):** auto-deploy (push `main` → GitHub Actions self-hosted runner Windows `D:\wujia-tea` → `git pull` + restart Odoo service) **CHỈ** restart → load lại module ĐÃ CÀI + upgrade module có bump version. **Module HOÀN TOÀN MỚI (chưa từng cài trên prod) KHÔNG được restart cài tự động** — phải chạy install 1 lần thủ công: `python odoo-bin -c <conf> -d <db> -i <module> --stop-after-init` (hoặc UI Apps → Update Apps List → Install). **Sprint 16 ⇒ `wujia_portal_debt` PHẢI install thủ công 1 lần trên prod** thì `/portal/debt` mới lên (các trang delivery/support/layout chỉ cần restart vì đã cài + bump version). Áp cho MỌI sprint sau có module mới: nhớ kèm bước `-i` vào deploy note.

**Windows 1-lệnh:**
```powershell
nssm stop Odoo
powershell -File D:\wujia-tea\scripts\reseed_full.ps1
nssm start Odoo
```

`reseed_full.ps1`: git pull → drop+create DB → install full chain → seed 5 script → `test_sprint5.py` 20 PASS. UTF-8 env vars BẮT BUỘC trước seed (`PYTHONUTF8=1`, `chcp 65001`, `[Console]::OutputEncoding=UTF8`).

→ `DEPLOY_SPRINT5.md` + `CHECKLIST.tex` + `setup-server.ps1`.

---

## §7 wujia-start-instruction

Slash `/wujia-start` apply operating rules cho session:

- v14 ref `/home/huyban/odoo-dev/wujia_tea_odoo14` — không sửa.
- v19 active `/home/huyban/odoo-dev/WujiaTea`.
- BA spec xlsm `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` (sheet "1. Model Field" backend, "2. FE - Portal" frontend, "5. Issue List" UI sprint 9, "FEATURE CHECKLIST").
- Sprint log `wujia-tea-doc.pdf` (compile từ `chapters/*.tex` qua `scripts/build-doc.sh`).
- Scope hiện tại: ✅ Model/Field A+B done / 🟡 Portal FE skeleton / ⏳ C+E chưa / ❌ D skip.
- **UI-only:** button có chưa cần wire backend, miễn layout đúng BA.
- **Perf-first 1500 user:** ormcache, store+index, cron daily, prefetch.
- **Ask-don't-assume + Read-before-write.**
- End session: `/wujia-end-sprint` (test → doc → PDF → commit → push).

Slash commands: `/wujia-start` `/wujia-load-feature <letters>` `/wujia-save-insight` `/wujia-end-sprint`.

---

## §8 wujia-session-template

Pattern paste sau `/wujia-start` để giao task:

```
Session này em làm <1 câu tóm tắt>.

Cụ thể:
1. Ref: v14 <path>, BA <Sheet!Section>, chapter <XX>.
2. Task A: <mô tả>.
3. Task B: <mô tả>.
4. Out-of-scope: <không làm>.

Discovery → plan → user approve → code → upgrade RC=0 → screenshot → commit.

Perf: <điểm cần lưu ý, vd query trên 1500 user>.

Xong: /wujia-end-sprint.
```

---

## §9 wujia-sprint9-issue-list-state

**Sprint 9 = 24 sprint con (sau BA rescale 2026-05-29 thêm UI-15..UI-18), 1 issue = 1 sprint con, BA order.** Sheet "5. Issue List" trong xlsm = **single source of truth**. Mỗi sprint BẮT ĐẦU = đọc cột G + H của issue verbatim → user xác nhận → mới code.

### Status table (BA spec exact, cập nhật 2026-05-29)

| # | ID | Khu vực | Spec ngắn | Status |
|---|---|---|---|---|
| 9.1 | UI-01 | Sidebar | Active menu icon/text white, icon 20-22, text 16, height 44-48 | ✅ 2026-05-23 |
| 9.2 | UI-02 | Sidebar | Bỏ user-pic block | ✅ 2026-05-24 |
| 9.3 | UI-03 | Header PC | Current Store pill + role badge + language + avatar | ✅ 2026-05-24 (3 attempts, §10) |
| 9.4 | UI-04 | Header mobile | Sub-strip below navbar 3-row stacked | ✅ 2026-05-24 |
| 9.5 | UI-05 | Button | Primary cyan/white h42, Secondary white/border h38 | ✅ 2026-05-24 |
| 9.6 | Mobile fix | Hamburger 768-1199 + fluid font 14→16 + utility class | ✅ 2026-05-25 |
| 9.7 | UI-06 | Page bg #E8ECEF (đậm hơn BA #F5F7FA — user override) | ✅ 2026-05-25 |
| 9.8 | UI-07 | Sidebar logo height 200px fix | ✅ 2026-05-25 |
| 9.9 | UI-08 | Header height 72px + vertical center | ✅ 2026-05-25 |
| 9.10 | UI-09 | Page Subtitle #6B7280 14-15px 400 | ✅ 2026-05-27 |
| 9.11 | UI-10 | Font Inter consistency (xóa Montserrat CDN + Arial outlier) | ✅ 2026-05-27 |
| 9.12 | UI-11 | KPI Card icon-left 72×72 + separator 1px #D1D5DB | ✅ 2026-05-27 (8 card / 2 page) |
| 9.13 | UI-12 | Content Card (home only — "Xem tất cả" pattern) | ✅ 2026-05-27 |
| 9.13b | UI-12 ext | MẪU 01/02 (sample.jpg) cho 3 listing + noti badge refactor | ✅ 2026-05-27 (4 commit: 0ce1886/4d36452/ba4245d/a85d9c3) |
| 9.14 | UI-13 | Header Right Actions: Language + Cart + Noti + Account(name+avatar) | ✅ verified 2026-05-29 (Lang dropdown layouts.xml:45 + cart inherit prio20 + bell inherit prio30 + user.name+avatar layouts.xml:68; JS badge poll động cart+noti) |
| 9.15 | UI-14 | KPI Card Height: gap 12, min-height 100, chevron neo mép phải, icon giữ 56 | ✅ 2026-05-29 |
| 9.16 | UI-15 | KPI Card Mobile: 1 card/dòng full width, h88–96, icon 52×52 r12 | ✅ 2026-06-02 (full-width <992px cả tablet — drop col-md-6; padding 14, gap 12 via link margin) |
| 9.17 | UI-16 | Main Content Spacing: header→title 24, title→KPI 12–16, KPI→content 20–24 | ✅ 2026-06-02 (token page-content-top 24 / page-title-gap 14 / kpi-content-gap 22, scoped portal shell) |
| 9.18 | UI-17 | Product Best Seller Card: chuẩn theo content card listing, bỏ table thô | ✅ 2026-06-02 (đổi sang `.wujia-content-card` + `.wujia-content-card-table`, icon-trending-up) |
| 9.19 | UI-18 | Main menu: row h44–48, margin 4–6, icon set đồng nhất 20–22 stroke | ✅ 2026-06-03 (2 icon FA→feather: info-circle→icon-info, building→icon-shopping-bag; margin 2→3px gap 6) |
| 9.20 | Empty | Empty state: icon + text + spacing chuẩn | ✅ 2026-06-03 (9 listing empty → `.wujia-empty-state` icon feather contextual + text VN; icon 40→36px; 2 outlier exam/support gom về) |
| 9.21 | — | Cleanup: 301 redirect kebab + xóa `wujia_account/` stub | ✅ 2026-06-03 (`redirects.py` auth=public 3 slug v14→kebab 301; xóa stub rỗng `wujia_account/`) |
| 9.22 | — | Verify: upgrade RC=0 + `test_sprint9.py` + curl + browser | ✅ 2026-06-03 (upgrade RC=0; test_sprint9 7/7; test_sprint5 20/20 regression; 3 curl 301) |
| 9.23 | — | Doc: `chapters/18-*.tex` + PDF + update §2/§4/§5/§9 | ✅ 2026-06-03 (chapter 18 mới + include + build-doc RC=0; summary updated) |
| 9.24 | — | Push: commit EN + deploy Windows | ✅ 2026-06-04 (toàn bộ commit 9.x đã push `origin/main` sync 0/0; auto-deploy qua GitHub Actions runner; chốt sổ qua `/wujia-end-sprint`) |

### File chạm history (compact — chi tiết trong git log + chapter 18)

| Sprint | Module touched |
|---|---|
| 9.1 | `wujia_portal_layout/_wujia_theme.css` + `layouts.xml` + 11×`sidenav_inherit.xml` |
| 9.2 | `wujia_portal_layout/layouts.xml` + `style.css` (xoá user-pic block) |
| 9.3-9.4 | `wujia_portal_base/store_picker_navbar.xml` + `store_picker.css` + `_variables.css` + `layouts.xml` |
| 9.5 | `_components.css` button refactor + `_variables.css` btn-height token + cleanup 4 legacy CSS |
| 9.6 | `wujia_responsive_menu.js` (NEW) + `_variables.css` fluid font + `_components.css` 3 utility class |
| 9.7 | `_variables.css` bg-page `#E8ECEF` + `_wujia_theme.css` specificity fix + 3 home buttons primary |
| 9.8-9.9 | `_wujia_theme.css` sidebar logo height 200 + header height 72 |
| 9.10 | `_variables.css` `--wujia-text-subtitle: #6B7280` + `_wujia_theme.css` rule subtitle |
| 9.11 | `layouts.xml` xoá Montserrat CDN + `member_dashboard_style.css` Arial → token |
| 9.12 | `_variables.css` 7 KPI token + `_components.css` `.wujia-kpi-card*` + portal_home.xml + portal_report_orders.xml |
| 9.13 | `_variables.css` typography Tailwind gray + `_components.css` `.wujia-content-card*` + portal_home 3 card |
| 9.13b | (1) `wujia_portal_base/portal_home.xml` noti badge class map / (2) `_components.css` `.wujia-content-card-table` / (3) `wujia_portal_notification/portal_notification.xml` MẪU 01 / (4) `wujia_portal_purchase_history/{controllers/portal.py,views/portal_history.xml}` + `wujia_portal_sale/views/portal_order_catalog.xml` MẪU 02 |
| 9.15 | `_variables.css` KPI token (gap 14→12, min-height 96→100) + `_components.css` (`.wujia-kpi-content flex:1 1 auto`, `.wujia-kpi-arrow margin-left:auto + font 18`) + `assets.xml` bump v=1092/v=1053 |
| 9.16 (UI-15) | `portal_home.xml` 4 KPI col `col-lg-3 col-md-6 col-12 mb-2`→`col-lg-3 col-12` + `_variables.css` mobile override `@media max-width:991.98px` (icon 52, min-h 92, padding 14) + `_components.css` mobile KPI gap (`.wujia-kpi-card-link margin-bottom:12`, gỡ grandchild selector chết) + `assets.xml` bump `_components` v=1098→1100 |
| 9.17 (UI-16) | `_variables.css` 3 token spacing (`--wujia-page-content-top:24` / `--wujia-page-title-gap:14` / `--wujia-kpi-content-gap:22`) + `_wujia_theme.css` rule scoped (`content-wrapper padding-top`, `.content-header margin`, `#dashboard-stats margin-bottom`) + `portal_home.xml` gỡ `mt-3`/`mb-1` + `assets.xml` bump `_variables` v→1101, `_wujia_theme` v=1061→1101 |
| 9.18 (UI-17) | `portal_home.xml` best-seller card `.card/.table.dashboard-list` → `.wujia-content-card` + `.wujia-content-card-header[-icon/-title]` (feather icon-trending-up) + `.wujia-content-card-table` + `.wujia-content-card-empty` |
| 9.19 (UI-18) | `portal_franchises_in_layout.xml` (`fa fa-building`→`feather icon-shopping-bag`) + `portal_franchise_information.xml` menu (`fa fa-info-circle`→`feather icon-info`) + `_wujia_theme.css` `.main-menu .navigation>li>a` margin `2px`→`3px` + `assets.xml` bump `_wujia_theme`+`_components` v=1102. OUT-OF-SCOPE: fa-* page body giữ nguyên |
| 9.20 (Empty) | 9 view listing empty → `.wujia-empty-state` (icon feather contextual + `<p>` text VN): history(inbox)/return(corner-up-left)/support(life-buoy)+comments(message-square)/info-request(edit)/knowledge(book)/report(bar-chart-2)/sale(package)/exam(award, bỏ alert-info) + `_components.css` `.wujia-empty-state i` 40→36px |
| 9.21 (Cleanup) | `wujia_portal_layout/controllers/redirects.py` (NEW, auth=public) 3 slug v14→kebab 301 + `controllers/__init__.py` import. Xóa `custom/wujia_account/` stub rỗng |
| 9.22 (Verify) | `scripts/test_sprint9.py` (NEW, ORM shell: icon menu feather-only + ≥8 view empty-state + wujia_account absent) 7/7. upgrade RC=0, test_sprint5 20/20, curl 3×301 |
| 9.23 (Doc) | `docs/chapters/18-sprint9-issue-list-ui-refactor.tex` (NEW) + `wujia-tea-doc.tex` include + `build-doc.sh` RC=0 + summary §4/§5/§9 |

### Policy update (2026-05-24)

**Mỗi sprint con UI xong = commit + push luôn.** Không gộp tới Sprint 9.17. Sprint 9.17 chỉ còn deploy + recap nghiệp vụ.

### Non-negotiable Sprint 9 rules

1. **KHÔNG BỊA SPEC.** Mở xlsm → sheet "5. Issue List" → đọc cột G + H verbatim → user confirm → mới code.
2. **English code.** Không tạo `.po` Sprint 9 (BA tự lo Sprint 10).
3. **Read-before-write.** `grep -rn` trong `custom/` xem rule hiện có.
4. **1 issue = nhiều iteration nhỏ** — screenshot vs mockup → loop fix → 100% khớp → next.
5. **CSS var bắt buộc** trong `_variables.css`. Component reuse class `_components.css`.
6. **Verify gate:** `bash scripts/upgrade.sh "<modules>"` RC=0 → restart → screenshot vs BA mockup col F → user OK → ✅ trong §9.
7. **Update §9 table khi DONE.**
8. **EXTRACT FULL IMAGES TỪ XLSM + MAP IMAGE TO CELL** qua openpyxl `ws._images[i].anchor._from.row/col` (xem §10 L1). Cherry-pick image theo số file KHÔNG đủ — phải map cell.
9. **CHECK V14 TRƯỚC KHI BUILD MỚI** (§10 L2). Grep `co_*wujia*` modules. Nếu KHÔNG có → ghi rõ "v14 KHÔNG có pattern X" + build từ đầu.
10. **VISUAL DESIGN: hỏi explicit 4 câu** (bg/text color/layout/icon) trước khi code visual (§10 L3).
11. **REGRESSION CHECK** — trước khi edit CSS/token: `grep -rn "<selector|token>" custom/` xem ai đang dùng. Token global (`--wujia-card-radius`, `--wujia-text-*`, `--wujia-btn-height`...) bump = ảnh hưởng MỌI page → smoke test 3-5 page khác sau ship, không chỉ page đang sửa. Đọc §9 "Files đã chạm" sprint trước để biết constraint nào còn áp.

### Gotcha tổng hợp (Sprint 8-9.13b)

1. **Browser cache 7 ngày** — Odoo serve static với `Cache-Control: public, max-age=604800`. Mọi CSS change PHẢI bump `?v=NNNN` trong `assets.xml` (chỉ áp file load qua manual `<link>` — files `web.assets_frontend` auto-bundle Odoo không cần). Bump version cao hơn lần cuối user thấy, không chỉ lần bump trước.
2. **Vuexy `.btn { line-height: 1 }`** gây icon Font Awesome lệch baseline. Fix: `.btn > i { line-height: 1; display: inline-flex; align-items: center }` — KHÔNG đụng `.btn` base.
3. **Sprint 4.2 `!important` force-show sidebar break toggle range 768-1199px.** Lesson: scope override `@media (min-width: 1200px)` thay vì `>=992px`. Mobile menu = vấn đề BODY CLASS swap, không phải CSS gap — Vuexy native overlay-menu CSS đủ một khi body class đúng.
4. **`html, body` vs `html body` specificity** — Vuexy `html body` (0,0,2) thắng `html, body` (0,0,1 mỗi vế). Token bg-page 4+ tháng render sai vì specificity bug. Audit token bằng DevTools computed-value, không chỉ grep `var(--*)`.
5. **`<h2>` semantic trong KPI card** — Sprint 9.12 chuyển sang `<div class="wujia-kpi-value">`. Sprint UI = cơ hội fix HTML semantic.
6. **BA hex typo** (`#28A9DF` vs `--wujia-primary #22A9DE`): lệch ≤4 ký tự → coi typo, dùng token có sẵn; lệch nhiều → hỏi BA.
7. **`--flush` blank render (Sprint 9.13)** — `padding: 0; display: block` huỷ flex container, page list render trắng trong wkhtmltoimage (Qt-WebKit). Sprint 9.13b mới = `.wujia-content-card-table` dùng negative margin + width calc thay vì display:block. wkhtmltoimage KHÔNG đáng tin cho debug CSS modern → verify browser thật.
8. **Token typography global bump** (`#1F2933` → `#111827` Tailwind gray Sprint 9.13) ảnh hưởng MỌI page. BA design dùng Tailwind chuẩn — convergence chậm theo sprint.
9. **Notification badge data-dep fragile (Sprint 9.13b commit 1)** — Inline `t-attf-style="background-color: #{bg_color}"` phụ thuộc `noupdate="1"` data XML → server stale = empty hex = no badge. Refactor sang class map `type_id.code → wujia-badge-*` xoá data dependency.
10. **`bg_color`/`text_color` field**: giữ trong model `wujia.notification.type` (backward compat) — drop sau khi BA confirm không cần admin override.
11. **Vuexy navbar `.badge` cascade fight (Sprint 9.14 UI-13 hotfix 2026-05-30)** — header cart/bell badge của ta đặt TRONG navbar Vuexy nên dính 3 rule chọi: (a) base `.badge { background-color:#7367F0; color:#FFFFFF }` (0,0,1,0) **cùng specificity** với `.wujia-header-badge` → ai thắng tùy LOAD ORDER nên **local đỏ mà server tím/không đỏ** (flaky env); (b) `.header-navbar .navbar-container ul.nav li .badge` (0,0,4,2) set padding → méo shape thành oval; (c) `.header-navbar … li > a.nav-link { color:#626262 }` → chữ số bị tối trên nền đỏ. Fix dứt điểm: rule scope `.header-navbar .navbar-container ul.nav li .wujia-header-badge` (0,0,5,2) + **`!important`** cho `background-color` VÀ `color` (white digit) + bump `?v=`. Đã thử specificity-only KHÔNG đủ vì env flaky → `!important` scoped (zero blast radius) mới chắc. Centering digit dùng `inline-flex` (align/justify center, line-height:1) thay line-height=height (Inter ascender/descender lệch). Commit chain: cfd0dee→a0a4cbd→df56153→d6d9e72→adce104, `?v=1098`.
12. **CSS/màu = FILE TRÊN ĐĨA, KHÔNG nằm DB (2026-05-30, đắt giá)** — `_components.css` là static file Odoo serve từ đĩa; DB chỉ giữ markup view + số `?v=` trong template. ⇒ Mọi triệu chứng "**local khác server**" về CSS/màu = **CACHE LAYER** (browser 7-ngày / `?v=` template chưa `-u` / reverse-proxy IIS-nginx cache static), **KHÔNG BAO GIỜ là vấn đề data** → **đừng nghĩ tới drop/copy DB để sửa CSS** (vô ích + rủi ro mất data). Quy trình debug "server không khớp local": (1) `curl localhost:<port>/…/file.css` xem đĩa có rule chưa; (2) mở thẳng URL CSS trên browser server + Ctrl+F rule; (3) View-Source check `?v=` template; (4) `Get-Service W3SVC,nginx` xem có proxy cache không. Fix = bust cache (`?v=` mới + `-u wujia_portal_layout` để DB phát URL mới), KHÔNG đụng DB.
13. **Global heading `!important` đè class (Sprint 26)** — `_components.css` có rule chuẩn-hóa `h1, .wujia-h1 { font-size: var(--wujia-font-size-h1) !important }` (và bản `h2`) → MỌI thẻ `<h1>/<h2>` bare bị ép 32px/24px, **đè cả class đơn `.wujia-mxxx-title` (0,0,1,0)** vì có `!important`. Triệu chứng: title render to bất thường dù CSS class set nhỏ hơn (đo computed = 32px). Thẻ `<h3>` KHÔNG dính (không có rule h3 !important). Fix: scope 2 lớp `.wujia-mpage .wujia-mxxx-h1` **+ `!important`** (scoped important thắng element important, đúng gotcha #11). Debug bằng Playwright `getComputedStyle` + duyệt `document.styleSheets` tìm rule thắng (đừng đoán). Lưu ý: server chạy KHÔNG `--dev` cache bundle asset → sửa CSS module xong phải chạy `--dev=all` hoặc `-u` để regen bundle mới thấy.

### Handoff prompt cho session sau

```
Session sau: LÀM LẠI TRANG HOME mobile theo Figma BA.
Frame: "ngo_gia_mobile_dashboard_header_blue_variant 1".

BƯỚC 0: Figma MCP phải active — chưa thấy tool figma → bảo user RESTART Claude Code
(load .mcp.json), rồi ĐỌC FRAME trước khi code.

QUY TẮC: block/button nào ĐÃ CÓ backend → build + móc nối. Block CHƯA CÓ → tra sheet
"3. Controller" (CT-xxx) xem BE build+wire chưa; CHƯA → ghi lại + làm UI-only, build cái khả thi.

Blocks Home (Figma) + backend (đã tra 2026-06-04):
 1. Header cart/bell/account — CÓ (UI-13), giữ.
 2. Hero card NỀN TỐI "Tổng quan cửa hàng": [H000]+tên+khu vực+role badge + 4 KPI nhúng:
    Đơn hàng / Thông báo / Đổi trả = CÓ BE (sale.order, notification, return.request);
    CÔNG NỢ = account.move CHƯA build (Phase 2, CT-014) → UI-only, hỏi BA nguồn.  [component mới]
 3. Card "KHUNG GIỜ ĐẶT HÀNG" + progress bar — CÓ BE (wujia.order.window._is_within_order_window).
 4. Grid "Hành động nhanh" 6 nút (Đặt hàng/Lịch sử/Giao hàng/Đổi trả/Kiến thức/Hỗ trợ) — link route CÓ.
 5. "Thông báo nổi bật" + badge màu — CÓ BE (notification). restyle theo Figma.
 6. BOTTOM-NAV (=10.1): Trang chủ/Đặt hàng/Giao hàng/Thông báo/Thêm. ACTIVE=ĐỎ (≠cyan).
    "Thêm"=drawer. Hiện <992px, ẩn desktop.

Figma KHÁC brief/code (active đỏ, page-bg #F6F8FB, cyan #28A9DF) → THEO FIGMA (không sửa Figma).
Hỏi BA: có làm bản DESKTOP Home không?

Code English, CSS var(--wujia-*)+_components.css. Workflow: Figma→grep portal_home.xml→plan→
approve→upgrade RC=0→BROWSER THẬT mobile<992px (KHÔNG wkhtmltoimage)→commit+push. Cuối /wujia-end-sprint.

CHƯA COMMIT: wujia-figma-brief.{tex,pdf}, build-brief.sh, design-system.md → /wujia-end-sprint gom luôn.
```

→ Quan trọng: đừng tin trí nhớ — mở lại Figma frame + xlsm mỗi lần. BA có thể edit bất kỳ lúc nào.

---

## §10 wujia-lessons (3 lesson tuyệt đối)

Postmortem Sprint 9.3 UI-03 (3 attempts) + Sprint 9.4 UI-04 (5 attempts) chi tiết → `chapters/18-sprint9-*.tex`. Chỉ giữ 3 lesson cốt lõi áp cho mọi session sau:

### L1 — EXTRACT FULL IMAGES TỪ XLSM + MAP IMAGE → CELL

Trước khi code 1 issue, làm đủ 3 step:

```bash
# Step 1: list + extract binary
unzip -l "WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm" | grep "xl/media/image"
mkdir -p /tmp/wujia_<issue>_mockup && cd /tmp/wujia_<issue>_mockup
unzip -o -j "WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm" "xl/media/image*.png"
```

```python
# Step 2: map image →a cell qua openpyxl (NON-NEGOTIABLE)
from openpyxl import load_workbook
wb = load_workbook('WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm', data_only=True)
ws = wb['5. Issue List']
for i, img in enumerate(ws._images):
    r = img.anchor._from.row + 1
    c = chr(65 + img.anchor._from.col)
    print(f"Image {i}: cell {c}{r}, path={img.path}")
```

**Step 3:** Read TẤT CẢ image anchor vào row issue đó (col E/F/G/H), KHÔNG cherry-pick. BA có thể đặt mockup chính ở G chứ không phải F.

**Annotation BA:** khoanh đỏ = TARGET CHÍNH / gạch chéo = XÓA / gạch chân = highlight detail / không annotation = variant.

### L2 — CHECK V14 TRƯỚC KHI BUILD MỚI

```bash
ls /home/huyban/odoo-dev/wujia_tea_odoo14/modules/wujia-erp/ | grep -E "^co_.*(wujia|portal|franchise)"
grep -rln "<keyword1>\|<keyword2>" /home/huyban/odoo-dev/wujia_tea_odoo14/modules/ \
     --include="*.xml" --include="*.html" --include="*.css" --include="*.scss" --include="*.py"
```

Nếu có → copy + adapt. Nếu KHÔNG → ghi rõ "v14 KHÔNG có pattern X" trong plan + build từ đầu. **Self-discipline:** trước Edit file mới, đọc lại L2 + chạy grep — đừng đợi user nhắc.

### L3 — VISUAL DESIGN: HỎI EXPLICIT 4 CÂU

Trước khi code visual, hỏi:
1. Bg color exact (hex / token / rgba)?
2. Text color (white / dark / token)?
3. Layout (1-row inline / 2-row stacked)?
4. Icon có/không (nếu có: feather name)?

KHÔNG assume từ ảnh — eye nhìn hex sai dễ. Đặc biệt khi mockup pill chồng bg cùng tông (cyan-on-cyan), translucent vs solid khó phân biệt.

---

## §11 wujia-shared-utils-cheatsheet

CSS class chung — dùng được mọi template:

| Class | Mục đích |
|---|---|
| `.wujia-btn` / `.wujia-btn-primary` / `.wujia-btn-secondary` | Button chuẩn h42/h38 |
| `.wujia-badge` + `.wujia-badge-{success,warning,danger,info,muted}` | Pill badge soft |
| `.wujia-empty-state` | Empty state container |
| `.wujia-two-pane` | Responsive 2-pane layout |
| `.wujia-kpi-card` + `.wujia-kpi-icon-{primary,success,warning,danger,info}` + `.wujia-kpi-separator` | KPI summary card (Sprint 9.12) |
| `.wujia-content-card` + `.wujia-content-card-header[-icon,-title,-link]` + `.wujia-content-card-body` + `.wujia-content-card-row[-bullet,-content,-date]` + `.wujia-content-card-empty` | Content card "Xem tất cả" (Sprint 9.13 home) |
| `.wujia-content-card-table` | Table body variant cho listing (Sprint 9.13b — negative margin edge-to-edge, KHÔNG flex-collapse) |
| `.wujia-container` / `.wujia-grid-responsive` / `.wujia-stack-mobile[.wujia-row-md]` | Responsive utility (Sprint 9.6) |

Token: `--wujia-primary #22A9DE` / `--wujia-bg-page #E8ECEF` / `--wujia-text-primary #111827` / `--wujia-text-secondary #374151` / `--wujia-text-subtitle #6B7280` / `--wujia-border #E5E7EB` / `--wujia-card-radius 16px` / `--wujia-btn-height 42px` / `--wujia-content-card-padding 22px`.

Python helper (portal):
- `get_active_franchise_id()` / `get_active_franchise_ids_filter()` ở `wujia_portal_base/controllers/portal.py`.
- `wujia.franchise.member.find_active_membership(user_id, franchise_id)` → role.
- `wujia.order.window._is_within_order_window(area_id=None)` cascade.
- Shared: `rate_limit` decorator + `attach_files_to_record` ở `wujia_portal_base/controllers/utils.py`.

Model names thực:
- `wujia.franchise.management` / `wujia.franchise.member` / `wujia.order.window` / `wujia.notification` / `wujia.notification.type` / `wujia.knowledge.article` / `wujia.support.ticket` / `wujia.info.update.request` / `res.area` / `res.ward`.
