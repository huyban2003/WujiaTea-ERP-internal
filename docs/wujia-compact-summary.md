# WujiaTea — Compact summary

**Mục đích:** context inject vào mọi session. Mỗi §section search-able qua `/recall`. History chi tiết → `chapters/*.tex` + git log.

**Cập nhật:** 2026-07-30 — Sprint 41 (Backend quản lý thông báo nhượng quyền, BA spec phần F) DONE, task BA sheet tab `Tasks` row 3. State hiện tại → §5.

---

## §1 wujia-overview

**Project:** Odoo 19 ERP + custom Vuexy portal cho chuỗi nhượng quyền trà sữa (~1500 portal user). Migrate v14 → v19.

**Dir:**
- `WujiaTea/odoo19/` Odoo 19 Community (read-only) · `custom/` 18 module (§2) · `themes/` 8 Vuexy · `data/` seed · `scripts/` seed+deploy · `docs/` (`wujia-tea-doc.tex` master + `chapters/` + `wujia-design-system.md` + `0[1-3]_*` chuẩn QA/Task/OAuth).
- v14 reference: `/home/huyban/odoo-dev/wujia_tea_odoo14` — template ref, **không sửa**.

**BA spec = Google Sheet "Internal ERP Master Plan_Update"** online (§7 tab/gid). Xlsm local = legacy fallback.

**Figma (BA design, READ-ONLY):** file key = **BẢN COPY** `aoeiDYlg6vlhJZg2w6Q7o5` ("Wujia (Copy)"); gốc `vfVcqN5zPJvlcjZU4NYim0` bị throttle, không dùng. BA CHƯA xong Figma → **ưu tiên code chuẩn > Figma > xlsm (lag)**. Cách kết nối MCP + xử lý Figma phẳng: `docs/figma-mcp-setup.md`. Token/component: `docs/wujia-design-system.md`.

**Local dev:**
- Scripts: `init-db.sh` fresh · `start.sh` hot-reload · `upgrade.sh <mod>` giữ data · `reseed_full.sh` 1-shot.
- DB `wujia_tea_19`, user `odoo19/1`, `127.0.0.1:5432`.
- Log `logs/odoo.log` · config `config/odoo.conf` · python `/home/huyban/miniconda3/envs/odoo/bin/python3`.

**UAT:** → §12 (`http://113.161.187.126:8019/`, `admin/Wujia@2026`).

**Deploy:** → §6 (thủ công, Windows tay, module mới cần `-i`).

---

## §2 wujia-modules (19 active)

| Module | Vai trò |
|---|---|
| `wujia_core` | `res.area`, `res.ward` master data |
| `wujia_franchise` | `wujia.franchise.management` + `wujia.franchise.member` (có icon) |
| `wujia_sale` | `sale.order` ext + product portal fields + `wujia.product.category` |
| `wujia_fleet` | Nhà xe / loại xe / xe / bảng giá (có icon) |
| `wujia_delivery` | `stock.picking/batch` ext + cước vận chuyển |
| `wujia_portal_layout` | Vuexy shell + CSS vars + Inter + responsive + utility class |
| `wujia_portal_base` | `/portal` dashboard + `bus.bus` realtime + franchise switch |
| `wujia_portal_sale` | `/portal/order` catalog + cart (`wujia.portal.cart(.line)`) |
| `wujia_portal_purchase_history` | `/portal/purchase-history` |
| `wujia_portal_delivery` | `/portal/delivery` |
| `wujia_portal_return` | `/portal/return` single-product + duyệt + `wujia.compensation.allocation` + wizard SO 0đ FIFO + hook picking (Sprint K) |
| `wujia_portal_notification` | `/portal/notification` + **backend quản trị thông báo** (vòng đời draft/published/archived, `code` ANN/năm/số, thống kê đọc, Sprint 41) |
| `wujia_portal_exam` | `/portal/exam` + backend Đăng ký thi (7 model, Sprint M) |
| `wujia_portal_knowledge` | `/portal/knowledge` + backend admin |
| `wujia_portal_report` | `/portal/reports/orders` |
| `wujia_portal_support` | `/portal/support` + backend + POST + attachment |
| `wujia_portal_info_request` | `/portal/info-request` + HQ duyệt |
| `wujia_portal_order_window` | Khung giờ đặt hàng per-area + global fallback |
| `wujia_portal_debt` | `/portal/debt` (+ `/payment-history`, `/pay`) — 7 màn Figma công nợ tuần. **UI-ONLY** (Sprint 43): `models.AbstractModel` `wujia.portal.debt` = seam dữ liệu duy nhất, 0 query, không bảng/không migration |

> Dashboard workstream riêng: `wj_ks_dashboard_ninja` + `wj_ks_dn_advance` (state = `docs/dashboard-migration-plan.md`). Chi tiết: `wujia-tea-doc.tex` §1.3/§1.5.

---

## §3 wujia-adr-summary (16 ADR)

ADR-001 odoo19 source độc lập / 002 venv conda `odoo` py3.10 / 003 PG role `odoo19` / 004 custom portal Vuexy thay `/my` / 005 `wujia.franchise.member` / 006 realtime `bus.bus` native / 007 tách Order+History / 008 URL kebab + 301 redirect / 009 block feature→defer / 010 3 field địa chỉ / 011 branch picker TẠI LOGIN / 012 *overruled by 015* / 013 `res.area`/`res.ward` ở `wujia_core` / 014 member UI độc lập / 015 gộp `wujia_franchise_management`→`wujia_franchise` / 016 dùng `mail.message` via `message_post()`.

→ Chi tiết: `wujia-tea-doc.tex` chap 2 + 13.

---

## §4 wujia-sprint-history (compact — chi tiết ở `chapters/`)

| Sprint | Date | Outcome (1 dòng) |
|---|---|---|
| 43 | 07-31 | Công nợ & thanh toán portal mobile: module MỚI `wujia_portal_debt` dựng 7 màn Figma `5013:*` (`WJ_Debt_*_MVP_v31`) — **UI-only**, mọi số đi qua 1 `AbstractModel` (0 query, không bảng). Hồi sinh 2 điểm vào chết: KPI Home + dòng đầu sheet "Thêm" (làm bằng **view inherit từ module mới** ⇒ `wujia_portal_layout`/`_base` bất biến). 14 test, harness đo bbox/computed-style vs node JSON ALL OK. Sidenav PC **chưa nối** (chờ Figma PC). → ch.56 |
| 42 | 07-31 | Thông báo: nhãn `normal`→"Thông thường" (+fix popup chuông thiếu key `important`) · chặn ghi read-status khi chưa chọn cửa hàng (message spec F dòng 884) · **chọn đối tượng nhận** `target_mode` all/filter/manual + tiêu chí khu vực–tỉnh–trạng thái–trừ tiệm + "Xem trước danh sách nhận", chốt danh sách tại publish. 35 test, migration 19.0.2.2.0. **Portal/ir.rule/controller bất biến.** → ch.55 |
| 41 | 07-30 | Backend quản lý thông báo nhượng quyền (BA spec F, `Tasks` row 3): `wujia.notification` thêm `code`(ir.sequence)/`state`/`portal_visible`/`is_published_portal`(store+index)/`published_by_id` + rename `date`→`published_date`, bỏ cờ `published`; menu + form/list/search backend đầu tiên cho HQ; thống kê đọc batched `_read_group`; migration 19.0.2.0.0 (30 record OK); 19 unit test. **Portal bất biến** (giữ key JSON `date`). → ch.54 |
| 40 | 07-26 | Đặt hàng Mobile — trạng thái xử lý + kết quả gửi đơn (Figma 4963:2, BA `Tasks` row 5): helper `_next_order_window()` + 2 route GET `/portal/order/submitted/<id>` `/portal/order/rejected` + overlay "Đang tạo đơn" chống double-submit + BFCache reset. **PC bất biến** qua hidden `flow=m`. → ch.53 |
| 39 | 07-25 | UI Figma 2 cụm cuối: Auth 4 màn (Login/Forgot × PC+Mobile, thay boilerplate Vuexy EN) + Đăng ký thi PC 7 màn (list/create/detail + 2 modal + 4 state chi tiết + 8 UI state), UI-only. Phát hiện **4 rule tag-level `!important` của shell nuốt mọi class PC** → trung hoà trong scope. → ch.52 |
| 38 | 07-23 | Portal Order logic+UI a11y (Batch A/B: qty validate, atomic step, CTA AA #0F7CA8, aria, order-window banner) + Shell/layout re-fix (Batch C: navbar specificity 0,4,1, sidebar 300px, font-smoothing) — 28 issue → Ready for Retest; +web_icon fleet/franchise. → ch.51 |
| M | 07-18 | Backend Đăng ký thi: 7 model (time.slot/course/session/registration.line), capacity FOR-UPDATE, publish gate, migration `exam 19.0.3.0.0`. → ch.50 |
| K | 07-17 | Backend Bù hàng/Return: redesign single-product + duyệt + `compensation.allocation` + wizard SO 0đ FIFO + hook picking + portal wire tiến độ. → ch.49 |
| 37 | 07-16 | 7 issue mobile Home/Đặt hàng + chuẩn hoá page-header 4 trang → `wj_page_header`. → ch.48 |
| 35–36 + 38-dash | 07-16 | Dashboard workstream (đánh số riêng, KHÁC Sprint 38 portal ở trên): port Ninja v18→v19 (`wj_ks_dashboard_ninja` S35) + scaffold advance (`wj_ks_dn_advance` S36) + hotfix ks_speak (S38). → ch.46 + `dashboard-migration-plan.md` |
| 34 | 07-16 | Global Shell header/footer/typography theo BA Issue List UI-01..06 (Top Bar, Current Store 430px, vi_VN default, account pill, footer, Inter). → ch.45 |
| 33 | 07-14 | `wj_page_header` — chuẩn hoá header mọi trang (mobile+PC), rollout ~40 site/11 module. → ch.44 |
| 28,PC-1..3 | 06-22..07-13 | PC desktop rework: Foundation/shell + Đặt hàng (PC-1), Notification (PC-3), Tài khoản 9 màn (28), Giao hàng (27). → ch.31/38/39 |
| 30–32 | 07-12..13 | Controller theo BA FINAL: Đặt hàng (giỏ chung store, 30) + Lịch sử + realtime cart (31) + Thông báo + toolchain ba_spec (32). → ch.41-43 |
| 10–27 | 06-06..07-03 | Mobile theo Figma từng màn: Home/Order/Cart/History/Shell/More/Knowledge/Dashboard/Ticket/Return/Notification/Exam/Delivery. → ch.19-38 |
| 9 | 06-03 | Portal UI refactor UI-01..18 + empty state + cleanup (test_sprint9 7/7). → ch.18 + §9 |
| 6–8 | 05-17..21 | 30 route (forgot/reset PW, profile, cart AJAX atomic, exam lock) + `info_request` + `order_window` + design token. → ch.4-17 |
| 1–5 | 04..05-16 | Core/franchise/sale/fleet/delivery + 9 portal skeleton + Knowledge/Support full BA + test 20/20. → ch.4-17 |

---

## §5 wujia-current-status

**State (2026-07-31):** 19 module active. **Sprint 43 (Công nợ & thanh toán portal mobile, ch.56) DONE — CHƯA DEPLOY UAT** (module MỚI ⇒ **bắt buộc `-i wujia_portal_debt`** 1 lần): `-u wujia_portal_debt --test-enable --test-tags wujia_debt` RC=0, **14 test 0 failed / 0 error**, 0 ERROR/Traceback. Harness Playwright đối chiếu **node JSON Figma** (bbox + computed-style, 391×844, 7 màn) → **ALL OK**: content 359 · card tổng 142 · CTA 44 · row lịch sử 54 · card hoá đơn 62 · card thanh toán 96 · card QR 220 (khung 160/mã 144) · bank 150 · card số tiền 76 · badge 26 · title 26/22px · gap 12 (8 ở 2 trang có nút back — đã kiểm lại node JSON, **code đúng, kỳ vọng trong script sai**) · không màn nào tràn card. Smoke shell `/portal` `/portal/order` `/portal/notification` ở 391×844 + 1920×1080: 200, **overflow ngang = 0**, KPI Home nay là link thật đọc "12,7tr". **Phạm vi UI-only** (BA chưa đặc tả: tab `1. Model/ Field` mục D dòng 529 là **tiêu đề rỗng**; DB có 1 `account.move`, 0 `account.payment`, không field nối `account.move`↔franchise; Figma tự ghi QR/bank "minh họa"). **Sprint 42 (Nhãn ưu tiên + read-status theo cửa hàng + chọn đối tượng nhận thông báo, ch.55) DONE — CHƯA DEPLOY UAT** (user deploy tay): `-u wujia_portal_notification --test-enable --test-tags wujia_notification` RC=0, **35 test 0 failed / 0 error**, migration `19.0.2.2.0` sạch (22 noti → `target_mode=all`, 8 noti đang có tick → `manual`, 0 bản ghi lệch). Smoke portal local xanh: nhãn "Thông thường" đúng ở list/detail/popup, popup trả đủ 3 nhãn (`important`="Quan trọng" — **trước đây hiện nhầm "Lưu ý"**, bug FE tự chế bảng nhãn, đã bỏ, giờ đọc `priority_label` backend), mark-read/mark-all khi chưa chọn cửa hàng trả `STORE_NOT_SELECTED` + **không phát sinh row `franchise_id` NULL mới**. Sheet: **10 ô cột L phần F** (bổ sung luồng chọn đối tượng nhận, có backup workbook trước khi ghi; cột A–K của BA không đổi 1 ký tự). Sprint 41 (Backend thông báo nhượng quyền, ch.54) DONE + **ĐÃ DEPLOY UAT** — build `-u wujia_portal_notification,wujia_portal_base` RC=0 / 94 module / 0 ERROR, **19 unit test 0 failed**, migration 19.0.2.0.0 chạy sạch, **đã push `origin/main`** (`b5816c0` code + `7677f97` docs). Smoke UAT read-only 07-31 xanh: module `19.0.2.0.0` installed, `published`/`date` đã biến mất, **15/15 record có `code` + `published_date`**, menu `Franchise Management/Thông báo` + `/Cấu hình/Loại thông báo`, group `Wujia Notification / User` + `/ Administrator`, `/portal/notification` + `/portal` + popup chuông 200. Sheet tab `Tasks` row 3 → `Done-pushed`, P3/Q3 **đã viết lại tiếng Việt có dấu** (07-31). Sprint 40 (Đặt hàng Mobile — overlay + 2 màn kết quả, ch.53) DONE — build `-u wujia_portal_sale,wujia_portal_order_window,wujia_portal_layout` RC=0 / 0 ERROR, đo computed-style Playwright 391×844 khớp Figma (title 21/700, CTA 48/44, overlay card 313×178), **chưa deploy UAT** (không cần `-i`, không migration). Sprint 39 (UI Figma Auth + Đăng ký thi PC, ch.52) DONE — 2 commit local `6757f17` + `842873c` trên `master`, build 0 ERROR, **chưa deploy UAT** (cần `-u wujia_portal_layout,wujia_portal_exam`). Hết Figma tồn: 2 cụm cuối đã dựng. Sprint 38 (portal order + shell/layout, ch.51) DONE — **28 issue Issue List → Ready for Retest**, merged + push `origin/main` (`59c8086`), build 94 module 0 ERROR. +web_icon fleet/franchise app-drawer. Sprint M (backend Đăng ký thi, ch.50) + K (backend Bù hàng, ch.49) DONE.

**Pending sống (hàng đợi):**
- **Deploy UAT tồn 4 sprint**: S39 `-u wujia_portal_layout,wujia_portal_exam` + S40 `-u wujia_portal_sale,wujia_portal_order_window,wujia_portal_layout` + **S42 `-u wujia_portal_notification`** (có migration `19.0.2.2.0`) + **S43 `-i wujia_portal_debt`** (⚠️ module MỚI ⇒ **`-i`**, không `-u`; không migration). KHÔNG cần bump `?v=` — mọi asset nằm trong bundle `web.assets_frontend`, không có `<link>` tay. Gộp 1 lệnh được: `-i wujia_portal_debt -u wujia_portal_layout,wujia_portal_exam,wujia_portal_sale,wujia_portal_order_window,wujia_portal_notification`. CSS đã bump `?v=1157`. *(S41 đã deploy 07-31.)*
- **S43 — 3 việc chờ BA xác nhận** (chưa gửi): (1) **CTA Figma `#28A9DF` chữ trắng trượt WCAG AA** → đang dùng `--wujia-cta` `#0F7CA8` theo đúng issue a11y BA mở ở S38 — cần BA confirm; (2) **thiếu Figma PC cho công nợ** → sidenav PC vẫn trỏ `/portal` (nối sang sẽ ra layout mobile trong khung 1920 = đúng loại lỗi UI-01/UI-PC-SHELL-001 BA đang bắt); trang vẫn render an toàn cột 391 căn giữa nếu gõ thẳng URL; (3) đề xuất nâng `#B45309` (chữ trên nền cảnh báo `#FFF7E6`, `--wujia-mres-warn-text` `#D97706` không đạt AA) thành **token global** — hiện là hex cứng DUY NHẤT của module. Ngoài ra: sheet "Thêm" giữ icon feather cho 6 dòng cũ (Figma vẽ chữ viết tắt CN/ĐT/ĐK — đổi cả 6 ngoài scope); **QR/bank hardcode "minh họa"** đúng Figma, chờ BA chốt QR tĩnh/động (`3. Controller` CT-050…CT-055 cột ghi chú còn để ngỏ).
- **S41 — đã đồng bộ TÊN field trên sheet; việc tồn → `docs/next-session-tasks-notification.md`** (07-31, có prompt sẵn cho session sau). Đã làm: đổi tên model/field phần F (33 ô, tab `1. Model/ Field`) + `3. Controller` (E12/E42-45); `Tasks!P3/Q3/R3` viết lại có dấu. **[07-31 S42] Source đã sửa 3/4:** NOTI-03 (nhãn) ✅ · NOTI-02 **bước 1** (chặn ghi read-status khi chưa chọn cửa hàng) ✅ · NOTI-01 ✅ **theo hướng mới chủ dự án chốt — KHÔNG gỡ `franchise_ids`, mà làm cho dùng được**: `target_mode` = `all` (mặc định, gửi hết) / `filter` (lọc theo khu vực–tỉnh–trạng thái, trừ tiệm cá biệt) / `manual`; danh sách nhận **chốt tại thời điểm publish** (cửa hàng mở sau KHÔNG nhận thông báo cũ, có nút "Cập nhật danh sách nhận"). Việc còn tồn: **NOTI-02 bước 2** (11 row `franchise_id` NULL local / 6 trên UAT — gán hay xoá là quyết định của chủ dự án → rồi mới `required=True` + gỡ index `_uniq_noti_user_no_store`) · NOTI-04 vặt (`published_date`, `content`, `type.code`) · `Tasks` row 6 cột Out-of-scope vẫn ghi "không target theo cửa hàng/khu vực" — **ngược với quyết định 07-31, chưa ai sửa**.
- ⚠️ **[07-31] Dev đã ghi SAI lên sheet BA rồi phải thu hồi** — chi tiết ở `docs/next-session-tasks-notification.md` §0. Tóm tắt để không lặp lại: (1) làm quá phạm vi user chốt ("chỉ đổi field" mà lại tự thêm cột ghi chú vào spec BA); (2) kết luận "BA mâu thuẫn" trong khi **BA nhất quán** — quên đọc cột **Out-of-scope của task tương ứng trên tab `Tasks`** (row 6 ghi rõ "Không thêm cơ chế target theo cửa hàng"), chỗ lệch thật ra là source (`franchise_ids` có từ S32, trước spec F); (3) trích sai ô (POR-024 ở row **30** không phải 31) và khẳng định "đã nghiệm thu" trong khi cột `Feature Status` trống. **Quy tắc rút ra: trước khi nói tài liệu BA mâu thuẫn / cái gì "đã làm", phải đọc cột trạng thái (`Feature Status`, `Trạng thái (AI)`) và Out-of-scope của task.**
- **M — portal Đăng ký thi**: **UI PC + mobile đã dựng xong theo Figma (S39/S26)**, còn **wire thật** (chọn kỳ mở → nhập nhân sự → gửi phiếu + lịch sử + kết quả; hiện demo dict trong controller, key đã map 1-1 field Sprint M nên chỉ đổi nguồn dữ liệu); deprecate `schedule`/`result`; deploy `-u wujia_portal_exam` (có migration). Plan: `floating-nibbling-widget.md`.
- **K — Bù hàng**: (b) guard size video minh chứng (1500 user); (d) SO bù để `draft`, HQ tự confirm sinh phiếu. Deploy `-u wujia_portal_return wujia_sale`. Plan: `functional-brewing-quill.md`.
- **Dashboard (workstream riêng)**: Step 2b (tab Query render + JS widget + 4 layouts + PDF cho `wj_ks_dn_advance`) + Step 3 `wj_ks_dn_formula` chưa port. Deploy prod cần `-i` module mới + pip pandas/xlrd/openpyxl. Nguồn: `docs/dashboard-migration-plan.md` (skill `/wujia-dashboard`).
- **Controller S30/31 deploy**: prod bật `is_public_portal`+`min_qty`+tạo danh mục portal (else catalog trống); WebSocket realtime chỉ chạy prod (gevent+nginx); deploy `-u wujia_sale,wujia_portal_sale`.
- **Pre-existing**: `/portal/reports/orders` 500 do user tz `Asia/Saigon` (fix → `Asia/Ho_Chi_Minh`, ngoài scope).
- **QA Issue List (42 issue, BA cập nhật liên tục)** → **nightly interactive agent** (§12) xử lý HẾT Dev-actionable. **[07-23 Sprint 38] 28 issue ĐÃ xong → Ready for Retest**: WJ-ORD-001..022 (order logic+UI), FUNC-MOB-ORDER-005/006, UI-01/02/03/04/06, UI-MOB-HOME-002, UI-PC-SHELL-001. ⚠️ **Chờ user đo trực quan server 1920×1080** (UI-01/03/PC-SHELL-001 phụ thuộc computed-style Vuexy runtime — không verify headless). **Deferred**: UI-MOB-SHELL-001 (cần BA cấp logo mobile 100:34), RESP-MOB-SHELL-003 (page-header y regression ~10 trang). 7 issue `Need BA Confirm=Yes` chờ BA. Ledger: `docs/qa-issue-ledger.yaml`; summary: `docs/sprint-summary-2026-07-23-portal.md`.
- **NEXT**: trang desktop còn legacy theo `pc_source_ui_v1_4` (history/report/return/knowledge/support/home); controller BA giao mới (toolchain `scripts/ba_spec/`). Mobile cũ: batch status thật (S13), khung giờ cart submit (S11), i18n `.po`, field bù hàng Phase 2 (S20), exam Phase 2 (S26).

**Phase 2 (future):** account.move Công nợ (CT-014) / Employee Mgmt / Payment History / Training Reports / User Invitations.

**Non-negotiable rules (mọi session):**
- ⚠️ **ĐỌC SOURCE TRƯỚC KHI SỬA — KHÔNG ĐOÁN model/field/method.** `grep -rn "_name = '" custom/<mod>/models/`. `wujia.franchise.management` (NOT `res.franchise`) — tên thực → §11 đầy đủ. Helper portal → §11.
- ⚠️ **REGRESSION CHECK trước khi sửa CSS/token/template**: `grep -rn "<selector|token>" custom/` xem blast radius (token global `--wujia-*` ảnh hưởng MỌI page); sau ship smoke 3-5 page khác.
- CSS bắt buộc `var(--wujia-*)` + class share `_components.css`. Không hex cứng.
- Demo data KHÔNG vào manifest XML → `scripts/seed_*.py` local-only.
- Odoo 19 view: không `attrs=`, không `decoration-secondary`, `_sql_constraints`→`models.Constraint`, search group `name="group_by"`, bỏ `expand="0"`.
- Commit English Conventional Commits, KHÔNG `--no-verify`. Comment GỌN (1 dòng đủ ý).
- Field rename: pre-migrate trước `-u`. i18n: code English, BA dịch `vi_VN.po`.

→ Chi tiết: `wujia-tea-doc.tex` §1.4.

---

## §6 wujia-deploy

**Deploy = thủ công** (dev server nội bộ, chưa CI/CD). Push `main` → user `git pull` + restart Odoo service Windows `D:\wujia-tea` tay. CSS change → bump `?v=NNNN` (§9 gotcha #1).

**⚠️ GOTCHA — MODULE MỚI KHÔNG TỰ CÀI:** restart chỉ load module ĐÃ cài + upgrade module bump version. Module HOÀN TOÀN MỚI phải `-i` 1 lần: `python odoo-bin -c <conf> -d <db> -i <module> --stop-after-init` (hoặc UI Apps → Install). Áp cho mọi sprint có module mới (vd dashboard `wj_ks_*`).

**Windows reseed 1-lệnh:** `nssm stop Odoo; reseed_full.ps1; nssm start Odoo` (git pull → drop+create DB → install chain → seed → test). UTF-8 env bắt buộc (`PYTHONUTF8=1`, `chcp 65001`). → `DEPLOY_SPRINT5.md` + `CHECKLIST.tex`.

---

## §7 wujia-start-instruction

- v19 active `/home/huyban/odoo-dev/WujiaTea`; v14 ref → §1.
- **BA spec = Google Sheet** `1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE` (owner `huyhunggnguyen@gmail.com`, anyone-view, BA edit trực tiếp). Đọc tab qua CSV public: `curl -sL "https://docs.google.com/spreadsheets/d/1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE/gviz/tq?tqx=out:csv&gid=<gid>"`.
- **Tab + gid:** `Tasks` (by name) · `MILESTONE` `1864615110` · `FEATURE CHECKLIST` `729461563` · `1.Model/Field` `2041118658` · `2.FE-Portal` `1002946158` · `3.Controller` `643561224` · `4.BE-Workflow` `1703696097` · **`5.Issue List`** `335593633` · `WORK LOG` `1388773997`. (Lấy gid: `curl .../htmlview | grep gid`.)
- Issue List: BA cập nhật mỗi ngày (đánh số hiện hành UI-01…06 = GLOBAL SHELL, khác `WJ_PageHeader` Sprint 9). Trạng thái → §5 + §12.
- **Controller task (S32+):** BA gửi spec qua chat GPT share → `scripts/ba_spec/fetch_ba_chat.py <url>` + `read_xlsm.py <sheet> <kw>`, đối chiếu source model THẬT (BA hay đặt tên lý tưởng hoá ≠ thật), hỏi ở fork. Toolchain gitignored, KHÔNG lên server (`scripts/ba_spec/README.md`).
- **QA/Task workflow (2026-07-21):** xem §12.
- Sprint log `wujia-tea-doc.pdf` (compile `chapters/*.tex` qua `scripts/build-doc.sh`).
- **UI-only** (button chưa cần wire, miễn layout đúng BA). **Perf-first 1500 user** (ormcache, store+index, cron). **Ask-don't-assume + Read-before-write.**
- End session: `/wujia-end-sprint` (test → doc → PDF → ledger/qa_sync → commit → push).

Slash: `/wujia-start` `/wujia-load-feature <letters>` `/wujia-save-insight` `/wujia-end-sprint` `/wujia-dashboard`.

---

## §8 wujia-session-template

```
Session này em làm <1 câu>.
1. Ref: v14 <path>, BA <Sheet!Section>, chapter <XX>.
2. Task A/B: <mô tả>.  3. Out-of-scope: <không làm>.
Discovery → plan → user approve → code → upgrade RC=0 → screenshot → commit.
Perf: <lưu ý query 1500 user>.  Xong: /wujia-end-sprint.
```

---

## §9 wujia-sprint9-history + gotchas

**Sprint 9 (24 sub-sprint UI-01..18 + empty state + cleanup)** = DONE 2026-06-04, chi tiết → `chapters/18-*.tex`. Issue table + file-touched table đã gỡ khỏi summary (giữ trong chapter 18 + git).

**Gotchas còn tái dùng (đọc kỹ trước khi sửa UI/UoM):**
1. **Cache 7 ngày** — Odoo static `Cache-Control: max-age=604800`. CSS change PHẢI bump `?v=NNNN` trong `assets.xml` (chỉ file load qua manual `<link>`; `web.assets_frontend` auto-bundle không cần). Bump cao hơn lần user thấy cuối.
2. **CSS/màu = FILE TRÊN ĐĨA, KHÔNG ở DB.** "local khác server" về CSS = CACHE (browser / `?v=` chưa `-u` / proxy), KHÔNG bao giờ là data → **đừng drop/copy DB để sửa CSS**. Debug: `curl .../file.css` + view-source `?v=` + check proxy.
3. **Global heading `!important` đè class** (`h1,.wujia-h1{...!important}`) ép mọi `<h1>/<h2>` bare → 32/24px, đè cả class đơn. Fix: scope 2 lớp `.wujia-mpage .wujia-mxxx-h1` **+ `!important`**. Server không `--dev` → sửa CSS xong phải `-u`/`--dev=all` regen bundle.
4. **Vuexy navbar `.badge` cascade** — cùng specificity base `.badge` → env flaky (local đỏ, server tím). Fix: scope `.header-navbar … .wujia-header-badge` + `!important` bg+color, digit `inline-flex` center.
5. **Odoo 19 UoM (Sprint K)** — `uom.uom` bỏ `category_id` → cây `relative_uom_id`. `_compute_quantity(...,'UP')` không kiểm nhóm → kết quả vô nghĩa nếu khác nhóm; kiểm nhóm = so gốc cây. Chiều ngược dùng `'DOWN'` (tránh double-UP). `sale.order.line` ĐVT = `product_uom_id`; `stock.move` đã giao = `move.quantity`; backorder tạo trong `_action_done`.
6. **BA hex typo** lệch ≤4 ký tự (`#28A9DF` vs `#22A9DE`) → coi typo, dùng token; lệch nhiều → hỏi.

---

## §10 wujia-lessons (7 lesson cốt lõi)

Postmortem chi tiết → `chapters/18-*.tex`.
- **L1 — Extract full images từ xlsm + MAP image→cell** qua openpyxl `img.anchor._from.row/col` (KHÔNG cherry-pick theo số file). Annotation BA: khoanh đỏ=target / gạch chéo=xóa / gạch chân=highlight.
- **L2 — Check v14 trước khi build mới**: `grep -rln <kw> /home/huyban/odoo-dev/wujia_tea_odoo14/modules/`. Có → adapt; không → ghi rõ "v14 KHÔNG có X" + build từ đầu.
- **L3 — Visual design hỏi explicit 4 câu** trước khi code: bg color? text color? layout (inline/stacked)? icon (feather name)? KHÔNG assume hex từ ảnh.
- **L4 (S39) — Dựng Figma xong PHẢI đo computed-style, đừng nhìn ảnh.** Shell Vuexy có 4 rule **tag-level + `!important`** thắng mọi class: `_components.css` `h1/h2 {font-size !important}` · `style.css` `table th {font-size:16px !important}` · `dashboard.css` `select {width:100%;padding:5px !important}` · `bootstrap-extended` `label {padding-left:.2rem}`. Cách phát hiện: Playwright duyệt `document.styleSheets`, `el.matches(rule.selectorText)`, in ra mọi declaration + cờ `!important`. Trung hoà trong **scope component**, KHÔNG sửa 4 file shared (blast radius = toàn portal). Đồng cấp specificity thì **thứ tự source quyết định** — modifier `--sm` phải đặt sau base, và `.x .y` (0,2,0) sẽ đè `.z` (0,1,0) dù `.z` mang ý nghĩa cụ thể hơn.
- **L5 (S41) — Schema change trên bảng ĐANG có dữ liệu: 3 cái bẫy.** (1) `unique(a,b,c)` **không chặn gì** ở nhánh `c IS NULL` (Postgres coi mọi NULL khác nhau) → phải thêm `models.UniqueIndex('(a,b) WHERE c IS NULL', ...)`; kiểm SQL còn 0 cặp trùng trước khi tạo index. (2) Field mới có `default` + `unique` = Odoo backfill mọi dòng cùng một giá trị rồi constraint vỡ → **bỏ default**, để `pre-migrate.py` lấp giá trị phân biệt **trước khi** ORM tạo constraint. (3) Rename field Python nhưng **giữ nguyên key JSON** trả về client → toàn bộ JS portal không phải đụng, không có gì để hồi quy.
- **L7 (S43) — Harness đo Figma: nguồn chân lý là NODE JSON, không phải kỳ vọng mình gõ ra; harness sai thì sửa harness, đừng sửa code.** 2/7 phát hiện là báo động giả (nút back 40 vs 42 = `border-box`; gap đầu 8 vs 12 = header kết ở `y=202`, khối kế bắt đầu `210` — code vốn đã đúng). Tin script vô điều kiện là sửa hỏng phần đang khớp. Chỗ Figma **cố ý** lệch (badge tràn khỏi `__head` cao 15) thì khai báo **miễn trừ tường minh** cho đúng element, đừng nới ngưỡng cả trang. Và **giữ nguyên chỗ Figma tự mâu thuẫn + ghi lý do** (frame 02 stats 2 cột / 03-04 2 dòng vì cả 3 card đều cao 142) — đừng "chuẩn hoá cho đẹp". Kèm: 5 lỗi số đo thật đều là **shell tag-level đè** (`body{letter-spacing:.14px}` làm title ellipsis · `line-height:1.8` làm nội dung 150 tràn hộp 142 · `form{margin-bottom:15px}` làm gap 27 · type-scale shell 15/12 vs Figma 14/11 làm dòng sheet cao 83/65) → trung hoà trong scope component. Sửa CSS không thấy đổi ⇒ **nghi cache `ir.attachment` của `web.assets_frontend` trước khi nghi selector** (`--dev=xml,assets` lúc lặp, `-u` sạch lúc chốt). Và: **tiêu đề rỗng trong spec BA là một câu trả lời** ("chưa quyết"), không phải chỗ trống để dev tự điền → dựng UI-only + chừa **một** seam đổi nguồn.
- **L6 (S42) — Muốn "chọn theo tiêu chí" mà không phá tầng phân quyền: tiêu chí là CÁCH CHỌN, M2M là KẾT QUẢ.** Lưu domain-string rồi eval lúc đọc thì `ir.rule` (vốn là domain ORM) không diễn đạt nổi "thông báo có domain khớp cửa hàng tôi" → phải lọc Python, mất index, chết ở 1500 user; và chạy lại tiêu chí trên dữ liệu đã đổi cho kết quả khác lúc gửi. Giải: `target_mode` all/filter/manual, tiêu chí resolve **1 lần tại `action_publish`** rồi `Command.set` vào M2M sẵn có → portal/ir.rule/controller/index **không đụng dòng nào**, có snapshot để audit. Đánh đổi phải hỏi chủ dự án và ghi vào spec: cửa hàng mở sau ngày gửi KHÔNG nhận thông báo cũ (có nút *Cập nhật danh sách nhận* khi cần). Kèm bài học giao tiếp: user nói **"khó hiểu quá"** = lỗi ở người giải thích — bỏ tên field/thuật ngữ, kể bằng thao tác thật ("chọn Miền Bắc → Xem thử → 137 cửa hàng → Gửi") và gom về **một** câu hỏi nghiệp vụ.

---

## §11 wujia-shared-utils-cheatsheet

**CSS class chung** (`_components.css`): `.wujia-btn[-primary/-secondary]` (h42/h38) · `.wujia-badge[-success/warning/danger/info/muted]` · `.wujia-empty-state` · `.wujia-two-pane` · `.wujia-kpi-card[+ -icon-*/-separator]` · `.wujia-content-card[-header/-body/-row/-table/-empty]` · `.wujia-container/-grid-responsive/-stack-mobile`. Canonical: `wj-filter-chip[--soft/--wrap/--clear]` · `wj-count-meta[--bold/--primary]` · `wj-empty-state[--card/--compact/--rich]` · `wj_page_header` (title/back/create) · `wj-pc-*` (PC components).

**Token** (`_variables.css`): `--wujia-primary #28A9DF` (BA CẤM #22A9DE) · `--wujia-bg-page #F3F6F8` · `--wujia-text-primary #111827` · `--wujia-text-secondary #374151` · `--wujia-text-subtitle #6B7280` · `--wujia-border #E5E7EB` · danger `#EF4444` · success `#16A34A` · `--wujia-text-muted #8A939E` · `--wujia-card-radius 16px` · `--wujia-btn-height 42px`. Font Inter self-host (weight 700).

**Python helper (portal):** `get_active_franchise_id()` / `get_active_franchise_ids_filter()` ở `wujia_portal_base/controllers/portal.py` (KHÔNG `utils.py`) · `wujia.franchise.member.find_active_membership(user_id, franchise_id)` → membership record (hay `False` nếu không có); để lấy role dùng `.role` trên record trả về · `res.config.settings._is_within_order_window(area_id)` (dùng qua `self.env['res.config.settings']._is_within_order_window(area_id=...)`) · `rate_limit` + `attach_files_to_record` ở `controllers/utils.py`.

**Model names thực:** `wujia.franchise.management` / `.member` / `wujia.order.window` / `wujia.notification` / `wujia.notification.type` / `wujia.notification.read` / `wujia.knowledge.article` / `wujia.support.ticket` / `wujia.info.update.request` / `wujia.compensation.allocation` / `wujia.exam.*` / `wujia.portal.cart[.line]` / `res.area` / `res.ward`.

---

## §12 wujia-qa-uat-nightly

**QA Operating Standard** = `docs/01_NGO_GIA_QA_OPERATING_STANDARD.md`. Luồng: `New → Ready for Dev → Dev In Progress → Ready for Retest → BA Retesting → Done`. **Dev KHÔNG tự đóng `Done`** — tối đa `Ready for Retest`. Fork/thiếu spec → `Need Clarification` (owner BA), KHÔNG đoán.

**UAT** `http://113.161.187.126:8019/` (`admin/Wujia@2026`) — tự smoke-test được. Giới hạn: không tạo đơn/hoá đơn/email thật, không đổi quyền, không drop data. Server info: `docs/CREDENTIALS.md`.

**Sheet tabs BA log:** → §7 (Tasks + 5.Issue List gid=335593633). Chuẩn lên task cho AI = `docs/02_TASKS_INTAKE_SPEC_FOR_GPT.md` (đã gửi BA/GPT).

**Ghi ngược sheet (dev-only, `scripts/ba_spec/`, gitignored):** ĐỌC = CSV công khai (không auth). GHI = POST tới **Apps Script bridge** chạy as editor (Google chặn OAuth scope Sheets nên KHÔNG dùng gcloud/token). `sheet_io.py` đọc CSV + ghi qua `sheet_endpoint.json` (webapp_url+secret).
- Setup 1 lần: deploy `qa_nightly/WujiaSheetBridge.gs` (Extensions→Apps Script→Web app, execute as editor) → dán URL vào `sheet_endpoint.json`. Chi tiết `docs/03_OAUTH_SHEET_SETUP.md`.
- **Làm xong 1 issue** → thêm entry vào `docs/qa-issue-ledger.yaml` (chỉ khi code khớp expected HIỆN TẠI) → `cd scripts/ba_spec && python3 qa_sync.py --dry-run` (xem) → `--apply` (set `Ready for Retest` + Build/Deploy + FIX/IMPACT/RETEST/LIMIT + Odoo Fit + dòng `7. ISSUE HISTORY`). Idempotent; tự SKIP issue `Need BA Confirm=Yes`/`Need Clarification`.
- `task_sync.py --list` (task Ready-for-AI) / `--row N --status/--question/--result` (ghi O/P/Q/R).

**Nightly agent — INTERACTIVE trong tmux (default 2026-07-22).** Cron `0 22` → `cron-tmux-launch.sh` mở session `wujia-nightly` chạy `run-interactive.sh` (claude opus/xhigh/acceptEdits, seed `agent_prompt_interactive.md`). Trực: `tmux attach -t wujia-nightly`.

Phạm vi: Dev-actionable (`issue_queue.py --dev`) + review `Ready for Retest`; mỗi issue 1 branch, `-u` RC=0. Agent **hỏi trước push main** (1=push, 2=lặp); xong → ledger + `qa_sync --apply`.

Giới hạn: KHÔNG tự `Done` / force / no-verify / drop-DB. Fallback headless: `run.sh` (không còn cron default). Chi tiết phím tmux → `scripts/ba_spec/qa_nightly/USAGE.md`.

**Self-verify Issue List bằng headless Chromium (2026-07-23).** Env `odoo` có sẵn `playwright` + chromium → ĐO computed-style/bounding-box y như BA thay vì đoán/ghi LIMIT "không verify headless". Tool: `scripts/ba_spec/qa_visual_check.py` (login admin/UAT, `--url --w --h --measure "sel:prop" --inject "css"`). **Gotcha:** (1) portal có long-poll bus.bus → dùng `wait_until="load"` KHÔNG `networkidle`; (2) login submit bằng Enter (nút login trùng nút Search); (3) nếu inject `!important` ultra-spec mà computed KHÔNG đổi → element bị JS/plugin Vuexy điều khiển (sidebar `.main-menu` width, nút `.btn-primary.waves-effect`), CSS bất lực → defer, đừng cố. **Kinh nghiệm 07-23:** đa số "Retest Failed" của BA thực ra ĐÃ đúng trên server — BA test build cũ trước deploy; luôn đo lại server hiện tại trước khi kết luận.

**⚠️ Gotcha ghi sheet — filter ẩn Done làm LỆCH ROW (07-23, đã fix).** `sheet_io.read_values` cũ đọc bằng gviz/tq **tôn trọng filter** của BA (ẩn "Done") → trả THIẾU dòng → `find_row` đánh số theo view lọc, nhưng bridge Apps Script ghi theo **ROW TUYỆT ĐỐI** → ghi Done NHẦM sang dòng khác (đã từng hỏng UI-06/UI-PC-SHELL-001/UI-MOB-SHELL-002, khôi phục xong). ĐÃ SỬA: `read_values` cho tab có gid dùng `export?format=csv` (bỏ qua filter, row khớp tuyệt đối). Sau mọi lần ghi sheet PHẢI verify lại bằng `export?format=csv` (không dùng gviz để verify). Set Done: `scripts/ba_spec/qa_done.py` (override rule chỉ khi chủ dự án duyệt).

**⚠️ Gotcha TÊN TAB — đừng lấy tên từ `export?format=xlsx` (07-31).** Excel cấm `/` trong tên sheet nên Google **sanitize khi export**: tab thật `1. Model/ Field` ra thành `1. Model Field`; gửi tên đó cho bridge → `Error: Không tìm thấy tab`. Cũng đừng dò bằng gviz `sheet=<name>` — sai tên nó **im lặng trả tab đầu tiên** (MILESTONE), tưởng đúng mà đọc nhầm sạch. Cách đúng: `sheet_io._post({'action':'ping','sheet':'1. Model'})` → bridge trả `sheet.getName()` là tên THẬT (`_resolve` có fallback substring nên gõ một phần là đủ). `KNOWN_GID` đã có cả 2 key (thật + alias xlsx). gid: Tasks `1936593712` · `1. Model/ Field` `2041118658` · `3. Controller` `643561224`.

**Spec F ↔ source (Sprint 41, 07-31).** Đồng bộ tên bằng `scripts/ba_spec/spec_f_sync.py` (dry-run → `--apply`) + `task_s41_rewrite.py` (P3/Q3 có dấu). Nguyên tắc user chốt: **chỉ đổi TÊN model/field — KHÔNG ghi thêm bất cứ thứ gì vào tài liệu BA.** Dev từng thêm cột ghi chú rồi phải xoá (`spec_f_wipe_notes.py`), xem §5. Việc tồn + prompt session sau: `docs/next-session-tasks-notification.md`. Ghi lên sheet thì ghi ít, đúng cái BA cần; phần còn lại để file task local.
