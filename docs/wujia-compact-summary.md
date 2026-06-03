# WujiaTea — Compact summary

**Mục đích:** context file inject vào mọi session WujiaTea. Mỗi §section search-able qua `/recall`. Detail history giữ trong `wujia-tea-doc.tex` + git log.

**Cập nhật:** 2026-06-03 (**Sprint 9 ĐÓNG**: UI-18 icon menu feather đồng nhất (info-circle→icon-info, building→icon-shopping-bag, margin 2→3px) + 9.20 gom 9 empty→`.wujia-empty-state` (icon feather + text VN, icon 40→36) + 9.21 `redirects.py` auth=public 3 slug v14→kebab 301 + xóa stub `wujia_account/` + 9.22 `test_sprint9.py` 7/7 + test_sprint5 20/20 + 3 curl 301 + 9.23 chapter 18 mới + PDF RC=0. Còn 9.24 push qua `/wujia-end-sprint`. Detail §9 + chapter 18.) | 2026-06-02 (**Figma MCP**: nối Figma↔code (Framelink), verified read-only. Detail → §1 "Figma" bullet + `docs/figma-mcp-setup.md` + `docs/wujia-design-system.md`. Policy: code=chuẩn > xlsm spec (lag); BA chưa xong Figma → khi xong FOLLOW Figma, không sửa Figma. Summary giữ `.md`.) | 2026-05-30 (**UI-13 header badge HOTFIX**: server render badge cart/bell không đỏ + số đen + shape oval do Vuexy navbar `.badge` cascade — fix scoped `(0,0,5,2)` + `!important` bg/color + flexbox centering + bump `?v=1098`. 2 gotcha mới §9: #11 Vuexy badge cascade, #12 CSS=disk-không-phải-DB. Commit chain cfd0dee→adce104. | Trước đó 2026-05-29: 9.14 UI-13 verified + 9.15 UI-14 KPI Card Height DONE. Còn 9 sprint con: 9.16–9.24. **Next: gộp 9.16 UI-15 (KPI mobile) + 9.17 UI-16 (Main Content Spacing)**).

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

**Figma (BA design — READ-ONLY, follow sau):** file "Wujia" key `vfVcqN5zPJvlcjZU4NYim0` nối qua Framelink MCP (`.mcp.json` + `FIGMA_API_KEY` ở `.env.local`). **BA CHƯA XONG FIGMA → khi BA hoàn thiện thì FOLLOW THEO FIGMA của BA** (đối chiếu → cập nhật `_variables.css`, KHÔNG sửa Figma). Dùng Figma MCP để xem screens + đọc structure (type/size/màu/radius/font). ⚠️ Figma hiện PHẲNG (card = siblings, không container) → gom bằng geometry. Chi tiết §8 + đề nghị BA: `docs/figma-mcp-setup.md`. Chuẩn UI hiện tại (code-based): `docs/wujia-design-system.md`. Hiện tại nguồn ưu tiên = **code chuẩn > xlsm spec (lag)**.

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

→ Chi tiết: `chapters/04-17.tex` + `chapters/18-sprint9-issue-list-ui-refactor.tex` (cuối Sprint 9).

---

## §5 wujia-current-status

**State (2026-06-03):** 18 module active. **Sprint 9 DONE** — toàn bộ UI-01..UI-18 (18 issue BA) + empty state chuẩn hoá + cleanup + verify + doc chapter 18 đã xong (2026-06-03). Chỉ còn **9.24 commit+push** qua `/wujia-end-sprint` (approval gate → auto-deploy Windows). Đợt cuối: UI-18 (icon menu feather đồng nhất), 9.20 (9 empty → `.wujia-empty-state`), 9.21 (redirects.py 3 slug 301 + xóa `wujia_account/`), 9.22 (test_sprint9 7/7 + test_sprint5 20/20 + 3 curl 301), 9.23 (chapter 18 + PDF). Commit chưa push (uncommitted working tree).

**Phase 1.0 (BA order) — ✅ HOÀN TẤT 2026-06-03:** toàn bộ 9.1→9.23 done (UI-01..UI-18 + empty state + cleanup + verify + doc). Chỉ còn **9.24 commit+push** qua `/wujia-end-sprint`. Chi tiết status từng issue → §9 bảng.
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
- Field rename: pre-migrate trước `-u` để tránh drop column.
- i18n: code English, BA dịch `vi_VN.po` (defer Sprint 10).

→ Chi tiết: `wujia-tea-doc.tex` §1.4.

---

## §6 wujia-deploy

**Sprint 5 đã deploy.** Sprint 9.x deploy qua `git pull` + restart (no schema change). Field rename → cần `reseed_full.ps1` drop+init khi skeleton.

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
| 9.24 | — | Push: commit EN + deploy Windows | ⬜ qua `/wujia-end-sprint` (approval gate) |

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

### Handoff prompt cho session sau

```
Session này em tiếp tục Sprint 9 (Issue List UI refactor).
UI-01..UI-14 (sprint 9.15) DONE. Session này làm GỘP 2 issue:
  • 9.16 = UI-15 KPI Card Mobile (mobile <768: 1 card/dòng full-width, h88–96,
    padding 14–16, gap 12, icon 52×52 r12, icon 22–24). LƯU Ý: token mobile override
    ĐÃ CÓ sẵn trong _variables.css cuối file (@media max-width:767.98px: icon 52,
    min-height 92) + _components.css media block margin-bottom 12 — chỉ cần VERIFY +
    tinh chỉnh đúng spec, có thể nhanh.
  • 9.17 = UI-16 Main Content Spacing (header→title 24, title→KPI 12–16, KPI→content 20–24).

Rules:
1. Mở xlsm → sheet "5. Issue List" → row UI-15 + UI-16 → paste cột G+H verbatim → đợi anh xác nhận → plan + code.
2. Code English. Không .po.
3. CSS var(--wujia-*) + class _components.css. Không hex cứng.
4. Workflow: read xlsm → grep v19 → plan → approve → edit → upgrade RC=0 → restart → user xem browser thật (KHÔNG screenshot wkhtmltoimage — gotcha #7 sai flexbox) → loop → ✅ §9 → push.
5. KHÔNG bỏ qua issue, tuần tự BA order. 1 sprint con = commit+push (policy 2026-05-24).
6. 9.14 UI-13 (header cart+bell icons) ĐÃ commit 3762e53 + push (2026-05-29). View active trong DB. Nếu anh thấy header chưa đúng BA thì mở lại UI-13 — còn không thì bỏ qua, sang UI-15/16.

Out-of-scope: T-031, locust, affiliate v14 gap, .po, MẪU 03-06 sample.jpg.

Cuối: update §9 bảng (⬜ → ✅ + ngày + Files đã chạm row).
```

→ Quan trọng: đừng tin trí nhớ — mở lại xlsm mỗi issue. BA có thể edit bất kỳ lúc nào.

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
