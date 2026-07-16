# WujiaTea — Compact summary

**Mục đích:** context file inject vào mọi session WujiaTea. Mỗi §section search-able qua `/recall`. Detail history giữ trong `wujia-tea-doc.tex` + git log.

**Cập nhật:** 2026-07-16 — **Sprint 37 DONE: 7 issue mobile Home/Đặt hàng (BA Issue List gid 335593633) + chuẩn hoá page-header 4 trang (3 account + Báo cáo) — chapter 48.** Home: gap sau store strip 40→16px (`.content-wrapper:has(.wujia-mhome)` pad-top 0, 1 lớp spacing) + unify title section 18px (scope `.wujia-mhome`, `!important` thắng global h2) + noti clamp 2 dòng. Đặt hàng: tên SP clamp 2 dòng + thumbnail `image_128`/icon-package (hết "Units" đôi) + floatbar `left/right:16` + `padding-bottom:150` (không che card cuối) + search 34→44px. Page-header: franchise-info/profile/change-pw (cụm account, S33 EXCLUDE) + report bỏ bespoke `wujia-maccount-pagetitle` (render 32px+icon do global h1 !important) → `wj_page_header` 22px không icon; report subtitle → `wj-count-meta`; fix card-title `wujia-maccount-cardtitle` 24→16px `!important` (gotcha #13 lại xuất hiện). Verify `-u wujia_portal_layout,wujia_portal_sale,wujia_portal_base,wujia_portal_report` RC=0 + Playwright 391px 7 issue/4 header + test_sprint9 7/7, `?v=1155`, UI-only không schema. _(Sprint 34 trước, chi tiết dưới:)_ **Sprint 34 DONE: Global Shell header/footer/typography theo BA Issue List MỚI (Google Sheet online) — chapter 45.** BA chuyển spec sang **Google Sheet "Internal ERP Master Plan_Update"** (thay xlsm local; tab/gid + cách kéo CSV thô ở §7 + §1). Tab "5. Issue List" bị BA **reset** → 6 issue UI-01..06 về **GLOBAL SHELL** (Top Bar, Current Store, Language, Account, mobile Footer, Typography) — **KHÁC** WJ_PageHeader Sprint 33 (header nội dung từng trang) → grep shell = 0 hit `wj_page_header`, cả 6 còn nguyên. User chốt làm cả 6 (UI-only + 1 migration). **UI-01** Top Bar bám đỉnh (override Vuexy `.header-navbar.floating-nav`: margin0/left=sidebar/right0 → x=300,y=0,w=1620,h=72) + Current Store gộp **1 container `.wujia-store-current-block` 430px** (store pill flex:1 + role neo phải; **ellipsis** `min-width:0` cho cột text — bug tên cửa hàng dài đè role). **UI-02** default portal user→**vi_VN** (migration `wujia_portal_base/19.0.5.12.0` activate vi_VN + set group_portal, gồm template user → user mới cũng VN) + PC pill 118×40; **route đổi ngôn ngữ MỚI** `/portal/set-lang/<code>` thay `/website/lang/*` (website UNINSTALLED → 404) + **cập nhật `request.session.context['lang']`** (session cache từ login, không thì đổi không có hiệu lực ngay). **UI-03** account pill 202×52 + **role dưới tên** (`_wujia_active_role` sẵn scope) + chevron. **UI-04** mobile action 38→**44**/radius22 + avatar `t-if image_128` ảnh thật else feather user-icon. **UI-05** footer icon 20→**22** + gap/padding đẩy label; active `#28A9DF` giữ. **UI-06** token `'Inter', sans-serif` (bỏ Roboto) + override vendor Montserrat (`.header-navbar/.navigation/.breadcrumb`) về Inter + `font-weight:800→700` (9 chỗ, hết nhòe) + bỏ inline Arial ở layouts.xml. Verify: upgrade RC=0, migration OK (6 user portal vi_VN), Playwright PC 1920 + mobile 391 **6/6 khớp BA** (top bar x300/y0/w1620, store 430, account 202×52+role, lang 118+"Việt Nam", action 44, footer 22, Inter/700) + tên dài truncate không đè + đổi lang hết 404, regression **10/11 200** (report 500 pre-existing tz `Asia/Saigon`), test_sprint9 7/7. Deploy: `-u wujia_portal_layout,wujia_portal_base` (base có **migration** — không chỉ restart), `?v=1152`, route mới cần restart. **Lệch pixel nhỏ** (lang h46 vs40, account x1718 vs1694) — size/cấu trúc khớp. _(Trước: Sprint 33 WJ_PageHeader chuẩn hoá header nội dung từng trang — chapter 44; Sprint 32 controller Thông báo BA FINAL + toolchain — chapter 43; Sprint 31 lịch sử + realtime cart — chapter 42; Sprint 30 order controller — chapter 41. Prose sprint cũ → §4 bảng + chapters/.)_

---

## §1 wujia-overview

**Project:** Odoo 19 ERP + custom Vuexy portal cho chuỗi nhượng quyền trà sữa (~1500 portal user). Migrate v14 → v19.

**Dir:**
- `WujiaTea/odoo19/` Odoo 19 Community source (read-only).
- `WujiaTea/custom/` 18 custom module active (§2).
- `WujiaTea/themes/` 8 Vuexy theme.
- `WujiaTea/data/` seed master (area/ward).
- `WujiaTea/scripts/` seed + deploy script (Python + PowerShell).
- `WujiaTea/docs/` `wujia-tea-doc.tex` master + chapters + `wujia-design-system.md` (chuẩn UI người-đọc) + `figma-mcp-setup.md` (Figma connect guide). **BA spec = Google Sheet online** (§7, thay xlsm local); `Wujia_Internal ERP Master Plan.xlsm` giữ làm legacy fallback.
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
| `wujia_sale` | `sale.order` ext + 6 field + tính khối lượng + product portal fields (S30: `is_public_portal`/min/max/quy cách/tên Hoa) + `wujia.product.category` |
| `wujia_fleet` | Nhà xe / loại xe / xe / bảng giá |
| `wujia_delivery` | `stock.picking/batch` ext + cước vận chuyển |
| `wujia_portal_layout` | Vuexy shell + CSS vars + Inter self-host + responsive (hamburger + fluid font 14→16px) + 3 utility class shared |
| `wujia_portal_base` | `/portal` dashboard + `bus.bus` realtime + franchise switch |
| `wujia_portal_sale` | `/portal/order` catalog + cart (S30: `wujia.portal.cart(.line)` giỏ chung theo store + controller BA mapping FINAL) |
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
| 30 | 2026-07-12 | **Controller Đặt hàng theo BA mapping FINAL** (chat GPT "Controller Product + Cart" + sheet H/I/L): giỏ chung theo store `wujia.portal.cart(.line)` thay draft-SO-per-user; product fields → variant (`is_public_portal` default False, min/step/max, `description_ecommerce`, `name_chinese`, `public_categ_id` → model MỚI `wujia.product.category`); add = SQL upsert atomic; submit = lock NOWAIT+savepoint → SO **draft** + huỷ draft portal cũ + clear giỏ nguyên khối; giá pricelist batch; bus publish `wujia_cart_changed` (JS subscribe sprint sau); route mới `/portal/order/cart/note`; migration template→variant. wujia_sale 19.0.4.0.0 / portal_sale 19.0.3.0.0. Verify: RC=0, ORM 16/16 + HTTP 17/17 (2 user chung giỏ, race), lock CART_IS_PROCESSING, regression 7/7+21/21, Playwright PC+mobile 0 JS error. → chapter 41 |
| 31 | 2026-07-13 | **Controller Lịch sử đơn hàng (CT-024/025) + realtime giỏ cross-session** (chat GPT + BA FINAL): dataset dict PC+mobile, giá ĐÃ THUẾ, người đặt backend="Ngô Gia tạo đơn", ẩn đơn cancel, strict store + chống IDOR; bus.bus realtime cart (route `/portal/order/cart/fragment` swap DOM không reload, event delegation). Gotcha: `t-set` trong `t-call` không lan → map badge inline; WebSocket chỉ chạy prod (gevent). Verify RC=0, test ORM 26/0 + HTTP 19/0, Playwright PC+mobile + realtime 16/0. → chapter 42 |
| 32 | 2026-07-13 | **Controller Thông báo theo BA FINAL + toolchain đọc spec BA** (`wujia_portal_notification` 19.0.1.8.0): giữ model `wujia.notification*` map field BA; THÊM expired_date/is_expired/priority_label; priority → normal/important/urgent (migration); read theo (noti,user,store); effective/history domain + filter read_status/priority/date + `/mark-all-read` + attachment **guarded (đóng IDOR)** + ERROR_MESSAGES BA. Toolchain dev-only `scripts/ba_spec/` (parse chat GPT share turbo-stream + dump xlsm) + skill "Controller task workflow". Verify RC=0 migration, test ORM 15/0 + HTTP 15/0, regression 7/0. → chapter 43 |
| 36 | 2026-07-16 | **Dashboard BOD Step 2a/6 — scaffold `wj_ks_dn_advance`** (workstream riêng, state `docs/dashboard-migration-plan.md`, skill `/wujia-dashboard`): module MỚI `custom/wj_ks_dn_advance` 19.0.1.0.0 copy từ v16 `ks_dn_advance` + rename `wj_` (giữ model `_name`) + **STRIP TV/carousel/website/AI-bundle**. Python query-engine port + Odoo-19 fix (`self.pool.cursor()`→`env.registry.cursor()`, `fields.datetime`→`datetime`, `eval`→`json.loads`, `sql_db` bỏ, uninstall_hook `(cr,registry)`→`(env)`, common_lib path→`wj_ks_dashboard_ninja`). Manifest dep `wj_ks_dashboard_ninja`, data-only (bỏ `web.assets_qweb`/`web.assets_frontend`). Views: board **Mail Config** page + mail template (fix Odoo-19 eager render `ctx['x']`→`ctx.get('x')` — gotcha #24). **⚠️ item-view inherit CỐ Ý HOÃN** (v18 base đã merge query-awareness → replay v16 sẽ đè hỏng form v18 — gotcha #23; reconcile ADD-only ở Step 2b). Verify: `-i` RC=0 + 0 ERROR log, ORM fields+`ks_run_query` engine present + croessel stripped, board/item form assemble, demo board intact, test_sprint9 7/7. NEXT Step 2b: tab Query render + JS widget + 4 layouts + PDF. Chưa commit (chờ user Y/N). |
| 35 | 2026-07-16 | **Dashboard BOD Step 1/6 — migrate Dashboard Ninja v18→v19** (workstream riêng, state file `docs/dashboard-migration-plan.md`, skill `/wujia-dashboard`): module MỚI `custom/wj_ks_dashboard_ninja` 19.0.1.0.0 (copy v18 + rename wj_ks giữ model `_name ks_dashboard_ninja.*` + STRIP AI/chat/TTS + bỏ TV). Fix Odoo 19: `fields.datetime` alias, `xlsxwriter` re-export, `groups_id→group_ids/all_group_ids`, `res.groups.privilege_id`, target `inline→current`, **viết lại M2M monkey-patch Ksolves** (get_domain_list chết — đầu độc mọi M2M), company service JS→`user.context`, tree_editor moves, `name_get→_compute_display_name`, `_context/_cr`, manifest rewrite (amCharts eager — form widgets cần, dedupe, +modal.scss+ks_dn_gridstack.scss). Verify: install 0 ERROR log (⚠️ RC=0 nói dối khi logfile — gotcha #16 state file), seed `scripts/seed_dashboard_demo.py`, Playwright tile+bar amCharts+list render 0 console error, test_sprint9 7/7. NEXT Step 2: advance subset (SQL query/layouts/PDF). Theme v18 giữ nguyên (reskin = Step 6). |
| 34 | 2026-07-16 | **Global Shell header/footer/typography theo BA Issue List MỚI** (Google Sheet online thay xlsm; 6 issue UI-01..06 về shell, KHÁC WJ_PageHeader S33). **UI-01** Top Bar bám đỉnh (override Vuexy `floating-nav` x=300,y=0,w=1620,h=72) + Current Store 1 container 430px (ellipsis fix tên dài đè role); **UI-02** default portal user→vi_VN (migration `base` 19.0.5.12.0 activate vi_VN + set group_portal) + pill 118×40 + **route `/portal/set-lang/<code>`** thay `/website/lang/*` (website uninstalled→404) + update session context; **UI-03** account pill 202×52 + role dưới tên + chevron; **UI-04** action 38→44 + avatar ảnh thật/fallback icon; **UI-05** footer icon 20→22; **UI-06** Inter thuần (override vendor Montserrat) + weight 800→700 (hết nhòe). Verify upgrade RC=0 + migration (6 user vi_VN) + Playwright 6/6 khớp BA + regression 10/11 (report 500 pre-existing tz) + test_sprint9 7/7. `-u wujia_portal_layout,wujia_portal_base`, `?v=1152`. → chapter 45 |
| 37 | 2026-07-16 | **7 issue mobile Home/Đặt hàng (BA Issue List gid 335593633) + chuẩn hoá page-header 4 trang.** Home: gap strip 40→16px (`:has(.wujia-mhome)` pad-top 0) + unify title section 18px (scope `.wujia-mhome`, `!important` thắng global h2 — KHÔNG đụng `.wujia-mdash-title` chung Support/Return) + noti clamp 2 dòng. Đặt hàng: tên SP clamp 2 dòng + thumbnail `image_128`/icon-package (bỏ ĐVT "Units" đôi, ĐVT còn dưới tên) + floatbar `left/right:16`+`padding-bottom:150` (không che card cuối) + search 34→44px+icon center. Page-header: franchise-info/profile/change-pw (account, S33 EXCLUDE — user chốt ghi đè) + report bỏ bespoke `wujia-maccount-pagetitle` (32px+icon) → `wj_page_header` 22px; report subtitle `text-muted small`→`wj-count-meta`; card-title `wujia-maccount-cardtitle` 24→16px `!important` (gotcha #13); xoá CSS chết. Verify `-u` 4 mod RC=0 + Playwright 391px (7 issue+4 header) + desktop 1920 sạch + test_sprint9 7/7. + follow-up căn top-spacing trang Báo cáo (non-mpage) khớp mpage (`.wujia-mreport-wrap`). `?v=1155`, layout 31.4.0/sale 4.3.0/base 5.13.0/report 1.6.0. UI-only, auto-deploy đủ. → chapter 48 |
| 33 | 2026-07-14 | **WJ_PageHeader — chuẩn hoá header mọi trang portal (Mobile+PC)** theo BA spec `docs/WJ_PageHeader/`. Component QWeb MỚI `wj_page_header` (3 variant title/back/create, props t-call, visibility bake, modifier `--m`/`--pc`) + CSS `.wj-page-header*` (token `--wj-*`; mobile 22/28 w800 back40 create112 · PC 28/36 w800 back44 create122). Rollout ~40 site/11 module: reconcile 4 PC cũ (bỏ crumb, back→icon-trái), header-swap 6 PC legacy (chỉ header row), mobile thay hết bespoke; GIỮ đặc thù (order warn-bar/floatbar, cart realtime, exam wizard, Home); EXCLUDE Tài khoản+Home. Fix **gotcha #13** (global `h1 !important` ép 32px → scope+`!important` 22/28). Verify upgrade 11 mod RC=0, Playwright font 22/28 khớp mockup, test_sprint9 7/0. UI-only, bump 11 manifest + `?v=1151`. → chapter 44 |
| 28 | 2026-07-07 | **PC Tài khoản 9 màn** (Figma `wujia_pc_01..09_v3`, page 4792): 3 trang desktop rework — `/portal/profile` (chỉ đọc, header card + KV boxed + note HQ), `/portal/franchise-information` (3 state owner-members/empty/staff suy từ `membership.role`), `/portal/change-password` (4 state error/message, viền đỏ field suy từ chuỗi lỗi) — + dropdown avatar (frame 09) + **rework toàn bộ sidebar** (1 view `priority=99` + `position=replace`: menu Figma Trang chủ/Đặt hàng/Lịch sử/Giao hàng/Công nợ/Thông báo/Kiến thức/Hỗ trợ/Đăng ký thi + TIỆN ÍCH/Tài khoản active). Shell chung `pc_account_shell.xml` (nav card trái + page-header) + `_pc_account.css` page-scoped (blast radius 0). Controller: 3 chuỗi lỗi khớp Figma + franchise context cho change-pw. Verify upgrade RC=0 91 mod, Playwright 1920px 8/9 frame khớp Figma, test_sprint9 7/7, 15/15 route 200 (4 mục bỏ khỏi menu vẫn sống). → chapter 39 |

→ Chi tiết: `chapters/04-17.tex` + `chapters/18-sprint9-issue-list-ui-refactor.tex` (cuối Sprint 9) + `chapters/19-sprint10-mobile-home-figma.tex` + `chapters/20-sprint11-mobile-order.tex` + `chapters/21-sprint12-mobile-shell-final.tex` + `chapters/22-sprint13-mobile-order-history.tex` + `chapters/23-sprint14-mobile-more-sheet.tex` + `chapters/24-sprint15-mobile-knowledge.tex` + `chapters/25-sprint16-mobile-dashboard-3screens.tex` + `chapters/26-sprint17-mobile-ticket.tex` + `chapters/27..29` (S18 account / S19 chuẩn hóa / S20 đổi trả-bù hàng) + `chapters/30-sprint21-mobile-product-cart-history-v2.tex` + `chapters/31-sprintpc1-pc-foundation-and-order.tex` + `chapters/32-sprint22-mobile-notification.tex` + `chapters/33-sprint23-mobile-figma-spacing.tex` + `chapters/34-sprintpc3-pc-notification.tex` + `chapters/35-sprint24-mobile-delivery.tex` + `chapters/36-sprint25-home-quick-action-v4.tex` + `chapters/37-sprint26-mobile-exam-registration.tex` + `chapters/38-sprint27-pc-delivery.tex` + `chapters/39-sprint28-pc-account.tex`.

---

## §5 wujia-current-status

**State (2026-07-16) — SPRINT 37 DONE: 7 issue mobile Home/Đặt hàng (BA Issue List) + chuẩn hoá page-header 4 trang (3 account + Báo cáo), chapter 48.** 18 module active.
- **S37 — mobile issue-list + page-header DONE (2026-07-16):** 7 issue UI (Home spacing/typography/clamp + Đặt hàng name/thumbnail/floatbar/search) + 4 page-header về `wj_page_header`. UI-only, không schema. **Deploy**: auto-deploy đủ (bump layout 31.3.0 / sale 4.3.0 / base 5.13.0 / report 1.5.0, `?v=1155`), **KHÔNG cần `-i`**. ⚠️ Pending: (a) các issue "Need Confirm: Yes" — user uỷ quyền default (section 18px, clamp 2 dòng, spacing 16px), BA có thể chốt token khác; (b) report mobile top-spacing ĐÃ căn khớp trang mpage (follow-up: marker `.wujia-mreport-wrap` + `padding-top:14px` + header `margin-top:0` → title top=174 = franchise; `?v=1155`, layout 31.4.0/report 1.6.0); (c) UI-MOB-ORDER-002 thumbnail dùng `image_128` — SP chưa có ảnh sẽ hiện icon-package placeholder (đúng ý BA).
- **S36 — Dashboard BOD Step 2a/6 (scaffold) DONE (2026-07-16, workstream riêng):** `wj_ks_dn_advance` 19.0.1.0.0 **installed** trên `wujia_tea_19` (Python query-engine + manifest + board Mail Config + mail template; TV/carousel/website/AI stripped). `-i` RC=0, test_sprint9 7/7. **⚠️ Feature UI/JS CÒN (Step 2b):** item-view inherit HOÃN vì v18 base đã merge query-awareness (gotcha #23 trong dashboard-migration-plan.md); chưa có tab Query render + JS widget + 4 layouts + PDF. Nguồn sự thật workstream = `docs/dashboard-migration-plan.md`.
- **S35 — Dashboard BOD Step 1/6 DONE (2026-07-16, workstream riêng):** `wj_ks_dashboard_ninja` 19.0.1.0.0 installed, dashboard render tile+chart+list 0 lỗi. **Nguồn sự thật của workstream = `docs/dashboard-migration-plan.md`** (step table + 22 gotchas), kickoff qua skill `/wujia-dashboard`. ⚠️ Pending: (a) 2 module còn lại `wj_ks_dn_advance` (Step 2) + `wj_ks_dn_formula` (Step 3) chưa port; (b) deploy prod cần `-i wj_ks_dashboard_ninja` thủ công (module MỚI — gotcha §6) + pip pandas/xlrd/openpyxl trên server; (c) `ks_dashboard_ninja_v18/` + `vietthuong/tools` = nguồn read-only, đã gitignore bản v18; (d) OPL-1 — repo private, không redistribute.
- **S34 — Global Shell 6 issue:** chi tiết xem "Cập nhật" đầu file + chapter 45. ⚠️ **Pending/deferred:** (a) **DEPLOY prod `-u wujia_portal_layout,wujia_portal_base`** — base có **migration** `19.0.5.12.0` (activate vi_VN + set group_portal lang), **KHÔNG chỉ restart**; route mới `/portal/set-lang` cần restart (đã có trong restart); CSS `?v=1152`; **không schema drop**; (b) **lệch pixel nhỏ** BA có thể muốn pixel-perfect: lang pill h=46 vs 40, account pill x=1718 vs 1694, current-store x=314 vs 324 (size/cấu trúc/role/lang đều đúng); (c) UI-06 hạ mọi `font-weight:800→700` **gồm cả `wj-page-header__title` S33** → nếu BA muốn giữ 800 phải thêm Inter-800 woff2; (d) `/portal/reports/orders` vẫn **500 pre-existing** (user tz `Asia/Saigon`, sửa tz→`Asia/Ho_Chi_Minh` — chưa làm, ngoài scope); (e) user mới tạo qua flow khác template portal có thể vẫn en_US (migration set template user nên phần lớn OK).
- **S33 — WJ_PageHeader:** chi tiết xem "Cập nhật" đầu file + chapter 44. ⚠️ **Pending/deferred:** (a) **DEPLOY**: UI-only không schema → auto-deploy bump 11 manifest (`wujia_portal_layout` 31.0.0 + history/notification/return/delivery/knowledge/support/info-request/report/sale/exam) + CSS `?v=1151`, **không cần `-i`**; (b) **DEFERRED cleanup**: gỡ ~30 block CSS bespoke chết (title/titlerow/back — grep 0-usage XML; **KHÔNG** đụng `wujia-mexam-back/head/*` còn 4-8 usage do giữ wizard, `wj-pc-page-header` còn ở `pc_preview.xml` dev-only); (c) report `/portal/reports/orders` **500 pre-existing** (`time zone "Asia/Saigon" not recognized` — tz DB, fix user tz→`Asia/Ho_Chi_Minh`, KHÔNG liên quan header); (d) Tài khoản + Home cố ý EXCLUDE; (e) back = link route fallback (history.back + giữ filter = enhancement optional chưa làm).
- **S32 — Controller Thông báo:** chi tiết xem "Cập nhật" đầu file + chapter 43. ⚠️ **Pending/deferred:** (a) **DEPLOY prod phải `-u wujia_portal_notification`** (schema: read model +franchise_id/last_open_date, notification +expired_date, priority selection đổi → migration; restart suông không đủ); (b) backend admin form tạo/publish thông báo (POR-023) chưa có UI — ngoài scope controller, build sau; (c) read line legacy backfill franchise_id best-effort (user 1 store) else NULL; (d) `published` bool = gate "state=published + portal_visible" (không thêm state/portal_visible — map); "thu hồi"=published=False (ẩn hẳn), "hết hiệu lực"=expired_date<now (ẩn popup/badge, còn lịch sử); (e) **BA cần đối chiếu sheet**: model thật `wujia.notification*` ≠ tên BA `wujia.announcement*` (đã map + ghi chú trong model); priority key thật đã khớp BA.
- **S31/S30 (order controller) — pending còn sống:** WebSocket realtime chỉ chạy prod (gevent + nginx `/websocket`); prod sau deploy bật `is_public_portal` + `min_qty` + tạo danh mục portal (else catalog trống); deploy `-u wujia_sale,wujia_portal_sale` (S30 schema+migration chưa từng commit). Chi tiết → chapter 41/42.
- **Các sprint cũ (S18–S29):** mỗi sprint 1 dòng → §4 bảng + chapters/.
- **▶ NEXT:** tiếp các trang desktop `pc_source_ui_v1_4` (history/report/return/knowledge/support/home); controller feature khác BA giao (dùng toolchain `scripts/ba_spec/` — xem §7). Pending mobile cũ: status batch thật (S13), khung giờ cart submit (S11), i18n `.po`, field bù hàng Phase 2 (S20), exam Phase 2 models (S26).
- **DEFERRED (S19+):** PC/desktop reconcile đầy đủ `pc_source_ui_v1_4`; unify `--wujia-card-radius`; migrate `bg_color` notification DB (noupdate); trim comment Python/XML.

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
- **BA spec = Google Sheet "Internal ERP Master Plan_Update" (NGUỒN CHÍNH từ 2026-07-15, thay xlsm local).** File `1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE` (owner `huyhunggnguyen@gmail.com`, link "anyone with link → view", **BA cập nhật trực tiếp**). User sẽ chỉ tab nào cần đọc mỗi session. Đọc qua Google Drive MCP `read_file_content` **chỉ trả sheet đầu (truncate 4MB)** → kéo tab cụ thể bằng CSV công khai: `curl -sL "https://docs.google.com/spreadsheets/d/1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE/gviz/tq?tqx=out:csv&gid=<gid>"`. **Tab + gid:** MILESTONE `1864615110` · FEATURE CHECKLIST `729461563` · 1. Model/Field `2041118658` · 2. FE-Portal `1002946158` · 3. Controller `643561224` · 4. BE-Workflow `1703696097` · **5. Issue List `335593633`** · WORK LOG `1388773997` · TIMELINE `576605186`. (gid map: `curl .../htmlview` rồi grep `{name:…,gid:…}`.) ⚠️ **Issue List đã bị BA RESET** (2026-07-14): danh sách Sprint-9 cũ GỠ hẳn, thay bằng **UI-01…UI-06 mới về GLOBAL SHELL** (Top Bar/Current Store/Language/Account/Footer/Typography) — KHÁC WJ_PageHeader (Sprint 33). Xlsm local `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` = **legacy fallback**.
- **Controller task (S32+):** BA gửi spec qua **chat GPT share** → dùng toolchain dev-only `scripts/ba_spec/fetch_ba_chat.py <url>` (parse) + `read_xlsm.py <sheet> <kw>` (dump), đối chiếu source model THẬT (BA hay đặt tên lý tưởng hoá ≠ thật), hỏi ở fork. Toolchain gitignored, KHÔNG lên server. Xem `scripts/ba_spec/README.md`.
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
