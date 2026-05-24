# WujiaTea — Compact summary cho agentmemory

**Mục đích:** file này được agentmemory inject context cho mọi session làm WujiaTea. Mỗi section là 1 entry độc lập, search-able qua `/recall`. Khi cập nhật, chạy lại `scripts/import_wujia_compact_summary.py`. Chi tiết đầy đủ vẫn ở `wujia-tea-doc.tex` (2611 dòng, 14 chapter).

Cập nhật lần cuối: 2026-05-23 (Sprint 9 in progress — UI-01 done, 12 issue + Empty còn lại).

---

## §1 wujia-overview

**Project type:** Odoo 19 ERP + custom Vuexy portal cho chuỗi nhượng quyền trà sữa, ~1500 portal user. Migrate từ v14 (folder `wujia_tea_odoo14/`) sang v19 (folder `WujiaTea/`).

**Dir layout:**
- `WujiaTea/odoo19/` — Odoo 19 Community source (read-only).
- `WujiaTea/custom/` — 16 custom module active (xem §wujia-modules).
- `WujiaTea/themes/` — 8 Vuexy theme (muk_web_*).
- `WujiaTea/data/` — seed master (area, ward).
- `WujiaTea/scripts/` — 14 seed/test/deploy script Python + PowerShell.
- `WujiaTea/docs/` — `wujia-tea-doc.tex` master + `CHECKLIST.tex` + `DEPLOY_SPRINT5.md`.

**Cách chạy local (Linux dev):**
- `scripts/init-db.sh` — fresh DB + install full chain.
- `scripts/start.sh` — start Odoo với hot-reload.
- `scripts/upgrade.sh <module>` — upgrade giữ data.
- `scripts/reseed_full.sh` — drop + init + seed + smoke test (1 lệnh).
- DB: `wujia_tea_19`, user/pass `odoo19/1`, host `127.0.0.1:5432`.

**Auto-deploy:** push lên `main` → GitHub Actions self-hosted runner trên Windows server `D:\wujia-tea` → `git pull` + restart (chi tiết → reference_credentials).

→ Chi tiết: `WujiaTea/docs/wujia-tea-doc.tex` chap 1.

---

## §2 wujia-modules

**18 module active trong `/custom/`** (cập nhật 2026-05-21, sau Sprint 8):

| Module | Vai trò |
|---|---|
| `wujia_core` | `res.area`, `res.ward` master data địa bàn |
| `wujia_franchise` | `wujia.franchise.management` + `wujia.franchise.member` |
| `wujia_sale` | `sale.order` ext + 6 field mới + tính khối lượng |
| `wujia_fleet` | Nhà xe / loại xe / xe / bảng giá |
| `wujia_delivery` | `stock.picking/batch` ext + cước vận chuyển |
| `wujia_portal_layout` | Vuexy shell, CSS vars, Inter self-host |
| `wujia_portal_base` | `/portal` dashboard + `bus.bus` realtime + franchise switch |
| `wujia_portal_sale` | `/portal/order` catalog + cart |
| `wujia_portal_purchase_history` | `/portal/purchase-history` |
| `wujia_portal_delivery` | `/portal/delivery` |
| `wujia_portal_return` | `/portal/return` + models |
| `wujia_portal_notification` | `/portal/notification` + models |
| `wujia_portal_exam` | `/portal/exam` + models |
| `wujia_portal_knowledge` | `/portal/knowledge` + backend admin (v19.0.2.0.0, Sprint 5) |
| `wujia_portal_report` | `/portal/reports/orders` |
| `wujia_portal_support` | `/portal/support` + backend admin + POST handler (v19.0.2.0.0, Sprint 5) + attachment download (Sprint 7) |
| `wujia_portal_info_request` | `/portal/info-request` — yêu cầu cập nhật thông tin franchise + HQ duyệt chatter (v19.0.1.0.0, Sprint 7) |
| `wujia_portal_order_window` | Khung giờ portal đặt hàng theo khu vực — model `wujia.order.window` per-area (BA Mục I R638-R646: name, area_id required M2o `res.area`, from/to Float [0,24), is_overnight compute store, sequence, multi-window per area: cho phép sáng+tối) + `res.config.settings` global fallback (3 field `ir.config_parameter` keys `wujia_portal.portal_order_time_*`, áp dụng khi area chưa cấu hình) + helper cascade `_is_within_order_window(area_id=None)` (priority: enabled? → per-area windows OR-merge → global) + `sale.order.create` defense-in-depth resolve `area_id` từ `franchise_id.area_id` + backend menu Sales → Configuration → Wujia Portal (v19.0.2.0.0, Sprint 8) |

→ Chi tiết: `wujia-tea-doc.tex` §1.3 (modules đã hoàn thành) + §1.5 (dependency tree).

---

## §3 wujia-adr-summary

**15 ADR + ADR-016 mới (Sprint 5).** Ngắn gọn 1 dòng/ADR:

1. ADR-001 — Tách `odoo19` source ra khỏi project khác để upgrade độc lập.
2. ADR-002 — Dùng venv conda `odoo` (Python 3.10) thay vì system Python.
3. ADR-003 — Postgres role riêng `odoo19` để tránh đụng project khác.
4. ADR-004 — Custom portal Vuexy thay vì `/my` chuẩn Odoo (BA spec).
5. ADR-005 — Model mới `wujia.franchise.member` thay vì sửa `franchise.management` v14.
6. ADR-006 — Real-time qua `bus.bus` + WebSocket Odoo native (không Socket.IO ngoài).
7. ADR-007 — Tách 3 module cho Sprint Order + History để phân quyền và deploy độc lập.
8. ADR-008 — URL kebab-case (`/portal/purchase-history`) + 301 redirect từ snake_case v14.
9. ADR-009 — Block portal feature → defer sprint sau (chấp nhận skeleton trước).
10. ADR-010 — 3 field địa chỉ giao trên `sale.order` (province/district/ward) thay vì 1 free text.
11. ADR-011 — Active branch picker xảy ra TẠI LOGIN (1 user nhiều chi nhánh).
12. ADR-012 — *bị overrule bởi ADR-015* — định tách `wujia_franchise_management` ra module riêng.
13. ADR-013 — `res.area` / `res.ward` đặt trong `wujia_core` (master data dùng chung).
14. ADR-014 — `wujia.franchise.member` có UI độc lập, không sửa form `res.users` gốc.
15. ADR-015 — Gộp `wujia_franchise_management` → `wujia_franchise` chống circular dep.
16. ADR-016 (Sprint 5) — Không tạo `wujia.support.ticket.message`; dùng `mail.message` chuẩn thông qua `message_post()` override.

→ Chi tiết: `wujia-tea-doc.tex` chap 2 + chap 13 (ADR-016).

---

## §4 wujia-sprint-history

**Sprint 1+2** — `wujia_core`, `wujia_franchise`, `wujia_sale`. Master data địa bàn + franchise + sale.order ext + tính khối lượng (Day 1) + perf optimizations (Day 2: ormcache lookup chi nhánh user, store + index `is_currently_valid` + cron daily recompute).

**Sprint 3** (2026-05-02) — `wujia_fleet` + `wujia_delivery`. Nhà xe, loại xe, xe, bảng giá; `stock.picking/batch` ext + cước vận chuyển; refactor 2026-04-30 (BA spec mục A): `res.ward`, `res.area`, `wujia.franchise.management/member`, mass calc trên `sale.order.line`, `sale.order`, `stock.move`, `stock.picking[.batch]`.

**Sprint 4.0–4.2** — 9 portal skeleton (`portal_layout` → `portal_support`) + Vuexy sidebar + sidebar overlay + card header convention.

**Sprint 4.3** (2026-05-15) — BA color palette 19 màu qua CSS vars trong `_variables.css`; Inter font self-host; card-header flush 6px convention.

**Sprint 4.4** (2026-05-15) — Backend admin view cho `wujia_portal_knowledge` (category/article CRUD) + `wujia_portal_support` (ticket form/list/kanban/search + action buttons); POST handler portal ticket create với file attachment; docs sync 7 chỗ.

**Sprint 5** (2026-05-16, đã deploy) — `sale.order.batch_id` compute store; knowledge full BA (state Selection, portal_badge, tag M2m model mới, sequence KNW-, cron daily, `is_published_portal` compute store); support full BA (rename `subject→title`, `user_id→created_by_id`, `handler→assigned`, category M2o model mới, 6-state, analytics `message_post` override, `sale_order_id` + `picking_batch_id` link); ADR-016; i18n `.pot` + `vi_VN.po` skeleton. **Test 20/20 pass.** Wrapper `scripts/reseed_full.{sh,ps1}` cho drop+install+seed+test 1 lệnh.

**Sprint 6** (2026-05-17) — Portal controller wiring + performance hardening cho 1500 user. 18 routes mới: forgot/reset password (rate-limit 10/h, anti email-enum), profile editable + avatar serve (ETag + Cache-Control private 300s) + change-password POST, franchise switch POST explicit, cart hybrid AJAX (`/cart/add|update|remove|count` jsonrpc + atomic SQL `UPDATE ... RETURNING` chống race 2 tab, rate-limit 60/min) + `/order/product/<id>` + `/order/cart` view + `/order/submit` PRG, return POST với multi-upload (shared `attach_files_to_record` helper validate MIME + size + `secure_filename`), exam register jsonrpc với `SELECT FOR UPDATE` race-safe + cancel. Shared utils `wujia_portal_base/controllers/utils.py` (rate-limit decorator + attach helper). RC=0, smoke 14 routes pass.

**Sprint 7** (2026-05-17) — Module mới `wujia_portal_info_request` (model `wujia.info.update.request` với sequence INF-, request_type 7-option, state draft→submitted→reviewing→approved/rejected, chatter inherit, record rule franchise scope + self-edit only, 5 routes portal + backend HQ duyệt) + 8 extension routes: notification mark-read/unread-count jsonrpc, knowledge search-as-you-type jsonrpc, support/return attachment download stream (ACL franchise gate), purchase-history `.pdf` qua `sale.action_report_saleorder`, delivery `.ics` cho Google/Outlook, report orders `.xlsx` qua `xlsxwriter` in-memory. **Tổng 30 routes Sprint 6+7.** 12 portal modules verified `installed`. Fix inline khi install: search view v19 `<group name=>` không `string=`, button form không cho `name="write"+context=` → dùng method riêng `action_start_review`. Known issue pre-existing (Sprint 4): `layouts.xml` dùng `env.company.favicon` không tồn tại v19 → fix Sprint 8 follow-up.

**Sprint 8** (2026-05-21) — Gói 4 mục tiêu trong 1 sprint sau khi BA Hùng bổ sung 3 task T-031/T-032/T-033 + sheet mới "5. Issue List": (1) **Fix-up** favicon 500 (`env.company.favicon` → `env.company.logo or ''`). (2) **BA Section A** — route mới `/portal/franchise-information` readonly menu top-level (cookie active franchise, 3 card: store details / contract / member tab, gate `portal_locked` + `status != 'active'` → locked page); inject sidenav link priority 20 sau `nav_item_home`. (3) **BA Section B + B.5 + Mục I** — audit mapping `sale.order` portal (9/9 BA field đã có sẵn từ Sprint 2-5; chỉ thêm `origin="Wujia Portal"`), module mới `wujia_portal_order_window` triển khai cả BA Mục I (model `wujia.order.window` per-area, multi-record/khu vực) lẫn Section B.5 (global fallback `res.config.settings`). Helper cascade `_is_within_order_window(area_id)` ưu tiên window theo area (OR-merge nhiều ca), fallback global; controller resolve area từ active franchise; `sale.order.create` extract `franchise_id.area_id` cho defense-in-depth. Backend menu Sales → Configuration → Wujia Portal → Khung giờ đặt hàng. **Lưu ý — initial impl chỉ global; user feedback yêu cầu refactor về per-area theo Mục I, đã sửa cùng Sprint 8.** (4) **Sheet "5. Issue List"** — refactor design token `_variables.css` (UI-04 `primary-soft #EAF7FD`, UI-09 `bg-page #F6F8FA`, UI-11 `card-radius 14px` + `border #E5E7EB`, UI-06 sidebar logo 200px, UI-03 menu-height 44 + icon 20, UI-08 header padding 28, UI-12 btn-height 42, UI-10 body 15px) + tạo `_components.css` shared (`.wujia-btn` chuẩn, `.wujia-badge[-success/warning/danger/info/muted]` soft pill, `.wujia-empty-state`, `.wujia-two-pane` responsive) + override active menu nền soft trong `_wujia_theme.css`. **Install + upgrade 4 module RC=0.** 18 module `/custom/` active.

**Sprint 9** (2026-05-23, IN PROGRESS — 1 issue = 1 sprint con, BA order) — Refactor Portal UI theo sheet **"5. Issue List"** (13 issue UI-01..UI-15 + 1 unnumbered Empty state), BA Hùng cập nhật 2026-05-22 kèm 12 mockup ảnh `xl/media/image22-33.png`. Nguyên tắc tuyệt đối: **không bịa spec** — mỗi sprint con đọc lại 2 cột G ("Đề xuất điều chỉnh") + H ("Kết quả mong muốn") trực tiếp từ xlsm, không suy diễn, không tự thêm thuộc tính. Code thuần English (BA tự lo `.po`, không tạo `.po` Sprint 9). Workflow: paste BA spec exact → grep v19 hiện trạng → plan ngắn → user approve → edit → `scripts/upgrade.sh` RC=0 → restart Odoo → screenshot vs BA mockup col F/G → loop fix → next issue. **Trạng thái:** **UI-01 DONE** (2026-05-23) — `_wujia_theme.css` active menu item BG `--wujia-primary` #22A9DE + text/icon `#FFFFFF` (BA: "chuyển icon và text sang màu trắng" — chỉ apply khi active, không phải tất cả menu); 11 sidenav_inherit.xml + `layouts.xml` main "Home" replace `fa fa-*` solid → `feather icon-*` outline (truck/shopping-cart/edit/clock/bar-chart-2/bell/award/calendar/user-check/corner-up-left/life-buoy/book/home). Upgrade 11 portal module RC=0. **Còn lại 16 sprint con** (xem §9): UI-02, UI-03, UI-04, UI-05, UI-06, UI-07, UI-09, UI-11, UI-12, UI-14, UI-15, Empty + cleanup (301 redirect + xóa `wujia_account` stub) + final verify + doc + push.

→ Chi tiết: `wujia-tea-doc.tex` chap 4-17 + `chapters/18-sprint9-issue-list-ui-refactor.tex` (sẽ tạo cuối Sprint 9).

---

## §5 wujia-current-status-and-remaining

**Tình trạng (2026-05-23):** 18 module active. Sprint 8 đã merge + push `main`. **Sprint 9 IN PROGRESS** — issue list portal UI refactor, 1 sprint con / issue, BA order. **Sprint 9.1 (UI-01) DONE** local (chưa push). Còn 12 issue UI + Empty + cleanup + verify + doc + push. Xem §9 wujia-sprint9-issue-list-state.

**Còn lại Phase 1.0** (BA spec):
- **Sprint 9 (in progress)** — 12 issue UI + Empty state còn lại (xem §9 bảng trạng thái từng issue).
- T-031 "Mockup quản lý vận hành nội bộ" (BA Hùng đã mockup) → defer Sprint 10.
- Load test 100+ concurrent user qua locust (Task `scripts/locust_portal.py` chưa làm).
- Affiliate/commission portal 12 route v14 — defer roadmap (`chapters/19-roadmap-v14-gaps.tex`).
- Dashboard ApexChart, TOTP 2FA, Portal Signup, Calendar booking, Upload video, QR scan in/out — defer (xem bảng "Deferred v14 features" chap 16).
- Phase 1.0 các trang khác sẽ liệt kê khi anh start sprint mới.

**Phase 2.0 (future):**
- Employee Management.
- Debt Overview.
- Payment History.
- Training Reports.
- User Invitations / Permissions.

**Lưu ý kỹ thuật cần follow ở mọi sprint mới:**
- ⚠️ **BẮT BUỘC ĐỌC SOURCE CODE TRƯỚC KHI SỬA — KHÔNG ĐOÁN TÊN MODEL/FIELD/METHOD.** Trước khi reference bất kỳ model nào (vd `wujia.franchise.management` vs `res.franchise`), method nào (vd `_get_accessible_franchise_ids` vs `get_franchise_ids`), helper nào (`get_active_franchise_id` ở `wujia_portal_base/controllers/portal.py` chứ KHÔNG ở `utils.py`) → `grep -rn "_name = '" custom/<module>/models/` + `grep -rn "def <method_name>" custom/`. Tên model thực: `wujia.franchise.management` (NOT `res.franchise`), `wujia.franchise.member`, `wujia.order.window`, `res.area`, `res.ward`. Lỗi 500 do đoán bừa tên model làm production xuống → user feedback nghiêm khắc 2026-05-21.
- Portal CSS: bắt buộc dùng CSS var trong `_variables.css` + class share trong `_components.css` (`.wujia-btn`, `.wujia-badge-*`, `.wujia-empty-state`), không hex cứng → [[feedback_wujia_portal_conventions]].
- Demo data: KHÔNG đưa vào manifest XML → dùng `scripts/seed_*.py` local-only → [[feedback_demo_data]].
- View Odoo 19: không `attrs=`, không `decoration-secondary`, group search dùng `name="group_by"`, **bỏ `expand="0"` ở `<group>` search (RNG schema v19 không còn chấp nhận)**, **`_sql_constraints` → `models.Constraint`** → [[reference_odoo19_gotchas]].
- Commit message: tiếng Anh, Conventional Commits → [[feedback_git_commit_english]].
- Field rename: pre-migrate trước khi `-u` để tránh drop column → [[feedback_field_rename_data_loss]].
- i18n: viết string tiếng Anh, BA dịch `vi_VN.po` → [[feedback_odoo_i18n_workflow]].

→ Chi tiết: `wujia-tea-doc.tex` §1.4 (Còn lại Sprint 5+).

---

## §6 wujia-deploy-sprint5

**Lý do Sprint 5 cần deploy đặc biệt:** field rename trên skeleton module (`wujia_portal_support`: subject→title, user_id→created_by_id, handler→assigned; `wujia_portal_knowledge` thêm state Selection). Odoo 19 `-u` sẽ drop column orphan ngay → mất data.

**Vì là skeleton chưa có data thật → chọn drop+init thay vì pre-migrate.**

**1-lệnh trên Windows server:**
```powershell
nssm stop Odoo
powershell -File D:\wujia-tea\scripts\reseed_full.ps1
nssm start Odoo
```

**Các bước reseed_full.ps1 thực hiện:**
1. `git pull` ở `D:\wujia-tea`.
2. PostgreSQL: drop + create DB `wujia_tea_19` (user `odoo19/1`).
3. Install full chain 16 module (đặt UTF-8 encoding env trước: `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, `chcp 65001`, `[Console]::OutputEncoding=UTF8`).
4. Seed 5 script: `seed_admin_franchise`, `seed_fleet_demo`, `seed_portal_demo`, `seed_knowledge_demo`, `seed_support_demo`.
5. Smoke test `test_sprint5.py` — expect 20 PASS / 0 FAIL.

**Tham khảo:** `WujiaTea/docs/DEPLOY_SPRINT5.md` + `WujiaTea/docs/CHECKLIST.tex` (server setup ban đầu) + `scripts/setup-server.ps1` (Git/Docker/SSH 1 lần đầu).

→ Chi tiết: `wujia-tea-doc.tex` chap 13 + `DEPLOY_SPRINT5.md`.

---

## §7 wujia-start-instruction

**Operating rules — áp cho MỌI session WujiaTea.** Slash command `/wujia-start` đọc section này + apply.

> - Dự án **WujiaTea** v14 (legacy, công ty khác làm): `/home/huyban/odoo-dev/wujia_tea_odoo14` — **template tham khảo**, không sửa.
> - Dự án v19 (đang làm): `/home/huyban/odoo-dev/WujiaTea` — migrate + optimize + thêm feature.
> - BA spec + analytics: `/home/huyban/odoo-dev/WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` (xlsm, đọc qua openpyxl). Sheet quan trọng: `1. Model Field` (backend), `2. FE - Portal` (frontend), `FEATURE CHECKLIST` (tổng quan).
> - Sprint log + tiến độ: `/home/huyban/odoo-dev/WujiaTea/docs/wujia-tea-doc.pdf` (compile từ `chapters/*.tex` qua `scripts/build-doc.sh`). Đã split theo chapter từ 2026-05-16.
>
> **Phạm vi feature hiện tại (cập nhật 2026-05-17):**
> - ✅ Model/Field A (quản lý nhượng quyền) + B (quản lý đội xe) — xong, BA có 1 vài điều chỉnh nhỏ.
> - 🟡 Portal FE (sheet "2 - FE portal") — sơ bộ; KHÔNG làm tiếp trong các session backend.
> - ⏳ Model/Field C (quản lý kiến thức nhượng quyền), E (quản lý ticket) — chưa làm.
> - ❌ Model/Field D — BA chưa phân tích, **skip**.
>
> **Cách làm:**
> 1. Mỗi feature có folder code v14 làm template tham khảo + sheet BA cho yêu cầu v19.
> 2. Giai đoạn hiện tại **CHỈ làm giao diện**: button có nhưng chưa cần wire backend, miễn show layout đúng BA.
> 3. Khi xong: update sprint log trong `chapters/` (file con riêng cho sprint mới) + master `\include` + recompile PDF.
> 4. Tự test bằng script trong `WujiaTea/scripts/` + thao tác trực tiếp.
> 5. Khi xong + anh OK: push GitHub (token `~/.git-credentials`).
>
> **Hiệu năng — bắt buộc:** portal **1500 user** → code phải mượt, không "chạy được là được". Tối ưu từ đầu:
> - `ormcache` cho method tính toán phổ biến.
> - `store=True` + `index=True` cho computed field hay query.
> - Cron daily thay vì compute on-the-fly khi không cần realtime.
> - Tránh N+1: prefetch, `read_group` thay vì loop.
>
> **Quy tắc (NON-NEGOTIABLE):**
> - **TUYỆT ĐỐI KHÔNG ĐOÁN TÊN MODEL/FIELD/HELPER.** Mỗi khi cần reference model (`env['xxx']`) hoặc field/method → `grep -rn "_name = '" custom/<mod>/models/` + `grep -rn "def <name>" custom/` trước. Không có exception. Tên thực: `wujia.franchise.management` / `wujia.franchise.member` / `wujia.order.window` / `res.area` / `res.ward`. Helper portal: `get_active_franchise_id()` / `get_active_franchise_ids_filter()` định nghĩa trong `wujia_portal_base/controllers/portal.py` (KHÔNG phải utils.py).
> - **Không chắc → HỎI**, đừng tự ý code.
> - **Read-before-write**: xem code v19 hiện tại có gì rồi mới làm tiếp.
> - **Không demo data trong manifest XML** (Odoo gốc tránh load demo khi production). Nếu cần demo: viết script Python riêng.
> - **Commit message: English + Conventional Commits** (vd `feat(wujia_franchise): add batch_id m2o on sale.order`).
> - **Không `git --no-verify`**, không bypass hook.
> - **Cuối session**: end-of-sprint ritual qua `/wujia-end-sprint` (test → doc → PDF → commit → push → recap).

**→ Slash command: `~/.claude/commands/wujia-start.md`.**

---

## §8 wujia-session-required-template

**Pattern cho session-specific block** — paste sau `/wujia-start` để giao task cụ thể cho session.

Template (anh fill in các `<...>`):

```
Trong session này, em làm <tóm tắt 1 câu>.

Cụ thể:
1. Reference: v14 ở <path nếu có>, sheet BA <Sheet!Section>, sprint log chapter <XX-...>.
2. Task A: <mô tả>.
3. Task B (nếu có): <mô tả>.
4. Out-of-scope: <việc không làm dù liên quan, để khỏi lan man>.

Discovery trước, code sau:
- Xem code v19 hiện có chạm chưa.
- Đối chiếu BA spec — chỗ nào không rõ HỎI.
- Đề xuất plan (model/field/view) → đợi anh duyệt → mới code.

Tối ưu performance: <điểm cần lưu ý cụ thể, vd "field này sẽ query trên 1500 user/ngày">.

Xong xuôi: chạy /wujia-end-sprint để test → doc → push.
```

**Ví dụ thực tế** (session 2026-05-17 — bổ sung A/B + review C/E):

```
Trong session này, em hoàn thiện model/field A+B (bổ sung field BA mới) và review C+E.

Cụ thể:
1. Reference: v14 ở /home/huyban/odoo-dev/wujia_tea_odoo14, sheet BA "1. Model Field" mục A+B+C+E, sprint log chapters/04-sprint2-day1-wujia-sale.tex + chapters/07-sprint3-fleet-delivery.tex.
2. Task A: thêm field Batch (batch_id, Many2one → stock.picking.batch) trên sale.order. Compute: lấy picking_ids → lấy batch_id của picking đầu tiên không bị cancel. Yêu cầu store=True + index=True (portal hay query).
3. Task B: review C (quản lý kiến thức nhượng quyền) + E (quản lý ticket) trong sheet BA, đối chiếu code v19 hiện có — thiếu gì bổ sung.
4. Out-of-scope: KHÔNG làm portal FE session này.

Discovery trước, code sau (xem v19 + đối chiếu BA + đề xuất plan → đợi duyệt → mới code).

Tối ưu performance: batch_id sẽ hiển thị ở portal danh sách đơn hàng — store=True bắt buộc.

Xong xuôi chạy /wujia-end-sprint.
```

**Slash command helper:** `/wujia-load-feature <letter>` (vd `/wujia-load-feature C E`) → tự extract BA spec sheet rows cho feature đó vào context.

**→ Slash commands list:**
- `/wujia-start` — load operating rules (đầu session).
- `/wujia-load-feature <letters>` — load BA spec cho feature cụ thể.
- `/wujia-save-insight` — lưu insight mới (append markdown + agentmemory).
- `/wujia-end-sprint` — end-of-session ritual (test → doc → PDF → commit → push → recap).

---

## §9 wujia-sprint9-issue-list-state

**Sprint 9 = 17 sprint con, 1 issue = 1 sprint con, BA order.** Sheet "5. Issue List" trong `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` là **single source of truth**. Mỗi sprint con BẮT ĐẦU bằng việc đọc lại 2 cột G + H của issue đó từ xlsm — **TUYỆT ĐỐI KHÔNG bịa**, không suy diễn thêm thuộc tính ngoài cột G/H.

### Bảng BA spec exact (paste từ xlsm sheet "5. Issue List" 2026-05-22)

| # | ID | Khu vực | Đề xuất điều chỉnh (cột G) / Vấn đề | Kết quả mong muốn (cột H) | Trạng thái |
|---|---|---|---|---|---|
| 9.1 | UI-01 | Sidebar | Chuyển icon và text sang **màu trắng** (khi active) | icon **20–22px**, text **16px**, item height **44–48px**, gap **12px** | ✅ DONE 2026-05-23 |
| 9.2 | UI-02 | Sidebar | **Bỏ phần thông tin user** tại sidebar | (none) | ⬜ pending |
| 9.3 | UI-03 | Header PC | Xây dựng lại hiển thị thông tin cửa hàng trên header PC | block **Current Store [H000] tên** + **role badge** + **language** + **avatar** | ⬜ pending |
| 9.4 | UI-04 | Header mobile | Như UI-03 nhưng mobile | block Current Store + role badge + language + avatar (responsive) | ⬜ pending |
| 9.5 | UI-05 | Button | Chuẩn hoá button toàn portal | Primary: **nền xanh, chữ trắng, h 40–44px**. Secondary: **nền trắng, viền xám, h 36–40px** (BA KHÔNG nói "text xám" — không bịa). Cùng loại phải giống nhau mọi page. | ⬜ pending |
| 9.6 | UI-06 | Card | Background page chưa chuẩn, cần đậm thêm | Page **#F5F7FA hoặc #F6F8FA**; card **trắng #FFFFFF**. | ⬜ pending |
| 9.7 | UI-07 | Sidebar | Khoảng cách logo→menu không đồng đều | Logo area height **180–220px**, menu bắt đầu cùng vị trí mọi page | ⬜ pending |
| 9.8 | UI-09 | Header | Header chưa thống nhất height/padding | Height **72–80px**, padding **24–32px**, **align center** toàn item | ⬜ pending |
| 9.9 | UI-11 | Font | Font + độ đậm chưa thống nhất | Font **Inter/Arial**. Body **15–16px**, title **32–36px**, card title **20–22px**, table **15–16px** | ⬜ pending |
| 9.10 | UI-12 | Card | Card Home + Support khác radius/shadow/border | Border **1px solid #E5E7EB**, radius **12–16px**, shadow **rất nhẹ hoặc không** | ⬜ pending |
| 9.11 | UI-14 | Badge | Status có chỗ là text thường ("Draft") | Tất cả status dùng **badge mềm** | ⬜ pending |
| 9.12 | UI-15 | Responsive | Detail panel Support cắt khi màn nhỏ | Desktop **2 cột**, tablet/mobile detail xuống dưới hoặc **drawer/modal** | ⬜ pending |
| 9.13 | Empty | Empty state | Empty state "Chưa có dữ liệu" còn thô | **icon nhỏ + dòng text + khoảng trắng chuẩn** | ⬜ pending |
| 9.14 | — | Cleanup | (Quick wins, không trong Issue List) | 301 redirect `/portal/purchase_history` → `/portal/purchase-history`, `/portal/return-request-list`, `/portal/exam-registration` + xóa `custom/wujia_account/` stub trống | ⬜ pending |
| 9.15 | — | Verify | — | `scripts/reseed_full.sh` RC=0 + `scripts/test_sprint9.py` (13 route + 13 CSS assertion) + 8 screenshot | ⬜ pending |
| 9.16 | — | Doc | — | `chapters/18-sprint9-issue-list-ui-refactor.tex` 13 sub-section + `chapters/19-roadmap-v14-gaps.tex` (affiliate/dashboard/TOTP) + master `\include` + recompile PDF qua `scripts/build-doc.sh` + update §2/§4/§5/§9 file này | ⬜ pending |
| 9.17 | — | Push | — | Commit Conventional EN + push `main` + cho lệnh deploy Windows | ⬜ pending |

### Files đã chạm (Sprint 9.1)

- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — active state BG primary + color #FFF + icon color #FFF (cũ: primary-soft + active-text).
- `custom/wujia_portal_layout/views/layouts.xml` — `fa fa-home` → `feather icon-home` + "Trang chủ" → "Home".
- `custom/wujia_portal_{delivery,sale,info_request,purchase_history,report,notification,exam,return,support,knowledge}/views/sidenav_inherit.xml` — 11 file, replace toàn bộ `fa fa-*` solid → `feather icon-*` outline.

### Nguyên tắc tuyệt đối cho mọi session Sprint 9 tiếp theo

1. **KHÔNG BỊA SPEC.** Trước khi code 1 issue, MỞ `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` → sheet "5. Issue List" → đọc đúng row của issue đó → paste lại cột G + H verbatim vào chat → user xác nhận → mới code. Cột E + F là Vấn đề + Hình minh hoạ tham khảo, KHÔNG phải spec; G/H mới là spec.
2. **Code English-only.** Chuỗi tiếng Việt chỉ chấp nhận ở template UI text hiện hữu (chưa migrate). Không tạo `.po` Sprint 9 — BA tự lo Sprint 10.
3. **Read-before-write.** `grep -rn` trong `custom/` xem rule CSS / template hiện có rồi mới sửa. Không đoán selector.
4. **1 issue ≠ 1 commit lớn.** 1 issue = 1 sprint con = nhiều iteration nhỏ. User screenshot vs mockup → loop fix → 100% khớp → next issue.
5. **CSS var bắt buộc.** Mọi giá trị (color, radius, height, font-size) PHẢI là `var(--wujia-*)` trong `_variables.css`. Không hex/px cứng trong template hay file CSS module-level.
6. **Component reuse.** Class chung trong `_components.css` (`.wujia-btn`, `.wujia-badge-*`, `.wujia-empty-state`, `.wujia-two-pane`). Nếu thiếu class — bổ sung ở `_components.css`, không inline style/class riêng từng template.
7. **Verify gate.** Mỗi sprint con: `bash scripts/upgrade.sh "<module1>,<module2>"` RC=0 → restart Odoo → screenshot trang liên quan → so vs mockup col F → nếu lệch, sửa tiếp → đạt 100% → user OK → mới đánh dấu DONE trong §9 bảng này.
8. **Update §9 bảng này khi DONE 1 issue.** Đổi ⬜ → ✅ + thêm ngày + 1 dòng "Files đã chạm".

### Handoff prompt cho session sau (paste sau `/wujia-start`)

```
Trong session này, em tiếp tục Sprint 9 (Issue List UI refactor). UI-01 đã DONE local.
Em làm Sprint con kế tiếp = <UI-XX> (xem §9 bảng wujia-compact-summary.md).

Quy tắc Sprint 9 (BẮT BUỘC):
1. Mở WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm → sheet "5. Issue List" → đọc row UI-XX → paste cột G + H verbatim vào chat → đợi anh xác nhận → mới plan + code. KHÔNG bịa spec ngoài G/H.
2. Code English-only. Không tạo .po.
3. CSS dùng var(--wujia-*) trong _variables.css; component reuse class trong _components.css. Không hex cứng, không inline.
4. Workflow per issue: read xlsm exact → grep v19 hiện trạng → plan ngắn → anh approve → edit → bash scripts/upgrade.sh "<modules>" RC=0 → restart Odoo → screenshot vs BA mockup col F → loop fix → 100% khớp → anh OK → đánh dấu ✅ trong §9 bảng → next issue.
5. KHÔNG bỏ qua issue, làm tuần tự BA order. KHÔNG gộp nhiều issue 1 commit. KHÔNG push lên main đến hết Sprint 9.17.

Out-of-scope session này: T-031 mockup operations, locust load test, affiliate v14 gap, .po dịch.

Khi hết session: update §9 bảng wujia-compact-summary.md (đổi ⬜ → ✅ + ngày + Files đã chạm) trước khi đóng session.
```

**→ Quan trọng cho future session:** đừng tin trí nhớ về spec — luôn mở lại xlsm cho mỗi issue. BA Hùng có thể edit sheet bất kỳ lúc nào.
