# WujiaTea — Compact summary

**Mục đích:** context inject vào mọi session. Mỗi §section search-able qua `/recall`. History chi tiết → `chapters/*.tex` + git log.

**Cập nhật:** 2026-07-22 — Nightly agent chuyển **headless → INTERACTIVE trong tmux** (opus/xhigh, hỏi ở fork; §12 + `scripts/ba_spec/qa_nightly/USAGE.md`). State hiện tại → §5.

---

## §1 wujia-overview

**Project:** Odoo 19 ERP + custom Vuexy portal cho chuỗi nhượng quyền trà sữa (~1500 portal user). Migrate v14 → v19.

**Dir:**
- `WujiaTea/odoo19/` Odoo 19 Community (read-only) · `custom/` 18 module (§2) · `themes/` 8 Vuexy · `data/` seed · `scripts/` seed+deploy · `docs/` (`wujia-tea-doc.tex` master + `chapters/` + `wujia-design-system.md` + `0[1-3]_*` chuẩn QA/Task/OAuth).
- v14 reference: `/home/huyban/odoo-dev/wujia_tea_odoo14` — template ref, **không sửa**.

**BA spec = Google Sheet "Internal ERP Master Plan_Update"** online (§7 tab/gid). Xlsm local = legacy fallback.

**Figma (BA design, READ-ONLY):** dùng **BẢN COPY** team Pro `aoeiDYlg6vlhJZg2w6Q7o5` ("Wujia (Copy)") = source of truth (gốc `vfVcqN5zPJvlcjZU4NYim0` bị throttle). BA edit trực tiếp vào copy. Kết nối: Framelink MCP (`.mcp.json` root, gitignored). BA CHƯA xong Figma → khi xong follow Figma (đối chiếu → cập nhật `_variables.css`, KHÔNG sửa). Figma hiện PHẲNG → gom bằng geometry. Ưu tiên: **code chuẩn > xlsm (lag)**. Chi tiết: `docs/figma-mcp-setup.md` + `docs/wujia-design-system.md`.

**Local dev:**
- Scripts: `init-db.sh` fresh · `start.sh` hot-reload · `upgrade.sh <mod>` giữ data · `reseed_full.sh` 1-shot.
- DB `wujia_tea_19`, user `odoo19/1`, `127.0.0.1:5432`.
- Log `logs/odoo.log` · config `config/odoo.conf` · python `/home/huyban/miniconda3/envs/odoo/bin/python3`.

**UAT:** → §12 (`http://113.161.187.126:8019/`, `admin/Wujia@2026`).

**Deploy:** → §6 (thủ công, Windows tay, module mới cần `-i`).

---

## §2 wujia-modules (18 active)

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
| `wujia_portal_notification` | `/portal/notification` + models |
| `wujia_portal_exam` | `/portal/exam` + backend Đăng ký thi (7 model, Sprint M) |
| `wujia_portal_knowledge` | `/portal/knowledge` + backend admin |
| `wujia_portal_report` | `/portal/reports/orders` |
| `wujia_portal_support` | `/portal/support` + backend + POST + attachment |
| `wujia_portal_info_request` | `/portal/info-request` + HQ duyệt |
| `wujia_portal_order_window` | Khung giờ đặt hàng per-area + global fallback |

> `wujia_portal_debt` đã XÓA (Sprint 17). Dashboard workstream riêng: `wj_ks_dashboard_ninja` + `wj_ks_dn_advance` (state = `docs/dashboard-migration-plan.md`). Chi tiết: `wujia-tea-doc.tex` §1.3/§1.5.

---

## §3 wujia-adr-summary (16 ADR)

ADR-001 odoo19 source độc lập / 002 venv conda `odoo` py3.10 / 003 PG role `odoo19` / 004 custom portal Vuexy thay `/my` / 005 `wujia.franchise.member` / 006 realtime `bus.bus` native / 007 tách Order+History / 008 URL kebab + 301 redirect / 009 block feature→defer / 010 3 field địa chỉ / 011 branch picker TẠI LOGIN / 012 *overruled by 015* / 013 `res.area`/`res.ward` ở `wujia_core` / 014 member UI độc lập / 015 gộp `wujia_franchise_management`→`wujia_franchise` / 016 dùng `mail.message` via `message_post()`.

→ Chi tiết: `wujia-tea-doc.tex` chap 2 + 13.

---

## §4 wujia-sprint-history (compact — chi tiết ở `chapters/`)

| Sprint | Date | Outcome (1 dòng) |
|---|---|---|
| M | 07-18 | Backend Đăng ký thi: 7 model (time.slot/course/session/registration.line), capacity FOR-UPDATE, publish gate, migration `exam 19.0.3.0.0`. → ch.50 |
| K | 07-17 | Backend Bù hàng/Return: redesign single-product + duyệt + `compensation.allocation` + wizard SO 0đ FIFO + hook picking + portal wire tiến độ. → ch.49 |
| 37 | 07-16 | 7 issue mobile Home/Đặt hàng + chuẩn hoá page-header 4 trang → `wj_page_header`. → ch.48 |
| 35–36,38 | 07-16 | Dashboard workstream: port Ninja v18→v19 (`wj_ks_dashboard_ninja` S35) + scaffold advance (`wj_ks_dn_advance` S36) + hotfix ks_speak (S38). → ch.46 + `dashboard-migration-plan.md` |
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

**State (2026-07-22):** 18 module active. Sprint M (backend Đăng ký thi, ch.50) + K (backend Bù hàng, ch.49) DONE. Hôm nay: icon franchise/fleet commit+push main.

**Pending sống (hàng đợi):**
- **M — portal Đăng ký thi**: wire thật (chọn kỳ mở → nhập nhân sự → gửi phiếu + lịch sử + kết quả; hiện demo-safe stub); deprecate `schedule`/`result`; deploy `-u wujia_portal_exam` (có migration). Plan: `floating-nibbling-widget.md`.
- **K — Bù hàng**: (b) guard size video minh chứng (1500 user); (d) SO bù để `draft`, HQ tự confirm sinh phiếu. Deploy `-u wujia_portal_return wujia_sale`. Plan: `functional-brewing-quill.md`.
- **Dashboard (workstream riêng)**: Step 2b (tab Query render + JS widget + 4 layouts + PDF cho `wj_ks_dn_advance`) + Step 3 `wj_ks_dn_formula` chưa port. Deploy prod cần `-i` module mới + pip pandas/xlrd/openpyxl. Nguồn: `docs/dashboard-migration-plan.md` (skill `/wujia-dashboard`).
- **Controller S30/31 deploy**: prod bật `is_public_portal`+`min_qty`+tạo danh mục portal (else catalog trống); WebSocket realtime chỉ chạy prod (gevent+nginx); deploy `-u wujia_sale,wujia_portal_sale`.
- **Pre-existing**: `/portal/reports/orders` 500 do user tz `Asia/Saigon` (fix → `Asia/Ho_Chi_Minh`, ngoài scope).
- **QA Issue List (42 issue, BA cập nhật liên tục)** → **nightly interactive agent** (§12) xử lý HẾT Dev-actionable. Hàng đợi nổi bật: UI-04 44→38px, WJ-ORD-001 (Critical) + WJ-ORD-002..022, shell/order mobile (UI-MOB-SHELL-001/002, RESP-MOB-SHELL/ORDER), FUNC-MOB-ORDER-005/006. 7 issue `Need BA Confirm=Yes` chờ BA. Review 17 issue đầu: `docs/qa-review-first17-2026-07-22.md`.
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
- ⚠️ **Issue List đã bị BA RESET** (07-14): Sprint-9 cũ gỡ, thay UI-01…06 GLOBAL SHELL (khác WJ_PageHeader). BA active cập nhật sheet mỗi ngày.
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

## §10 wujia-lessons (3 lesson cốt lõi)

Postmortem chi tiết → `chapters/18-*.tex`.
- **L1 — Extract full images từ xlsm + MAP image→cell** qua openpyxl `img.anchor._from.row/col` (KHÔNG cherry-pick theo số file). Annotation BA: khoanh đỏ=target / gạch chéo=xóa / gạch chân=highlight.
- **L2 — Check v14 trước khi build mới**: `grep -rln <kw> /home/huyban/odoo-dev/wujia_tea_odoo14/modules/`. Có → adapt; không → ghi rõ "v14 KHÔNG có X" + build từ đầu.
- **L3 — Visual design hỏi explicit 4 câu** trước khi code: bg color? text color? layout (inline/stacked)? icon (feather name)? KHÔNG assume hex từ ảnh.

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
