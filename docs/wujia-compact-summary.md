# WujiaTea — Compact summary cho agentmemory

**Mục đích:** file này được agentmemory inject context cho mọi session làm WujiaTea. Mỗi section là 1 entry độc lập, search-able qua `/recall`. Khi cập nhật, chạy lại `scripts/import_wujia_compact_summary.py`. Chi tiết đầy đủ vẫn ở `wujia-tea-doc.tex` (2611 dòng, 14 chapter).

Cập nhật lần cuối: 2026-05-25 (Sprint 9 in progress — UI-01..UI-09 + Sprint 9.6 Mobile fix done; Sprint 9.8 UI-07 sidebar logo 200px + Sprint 9.9 UI-09 header 72px shipped, 5 issue UI + Empty còn lại).

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
| `wujia_portal_layout` | Vuexy shell, CSS vars, Inter self-host + mobile hamburger bridge rule 768-1199px + root font-size fluid scaling 14→16px + 3 responsive utility class (v19.0.4.0.0, Sprint 9.6) |
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
| 9.2 | UI-02 | Sidebar | **Bỏ phần thông tin user** tại sidebar | (none) | ✅ DONE 2026-05-24 |
| 9.3 | UI-03 | Header PC | Xây dựng lại hiển thị thông tin cửa hàng trên header PC | block **Current Store [H000] tên** + **role badge** + **language** + **avatar** | ✅ DONE 2026-05-24 (3 attempts — xem §10 final spec) |
| 9.4 | UI-04 | Header mobile | Như UI-03 nhưng mobile | block Current Store + role badge + language + avatar (responsive) | ✅ DONE 2026-05-24 (sub-strip below navbar, visual ngược UI-03 — bg white + label cyan + name đen, 3-row stacked) |
| 9.5 | UI-05 | Button | Chuẩn hoá button toàn portal | Primary: **nền xanh, chữ trắng, h 40–44px**. Secondary: **nền trắng, viền xám, h 36–40px** (BA KHÔNG nói "text xám" — không bịa). Cùng loại phải giống nhau mọi page. | ✅ DONE 2026-05-24 (gom 4 alias secondary thành 1 style, fix icon line-height conflict với Vuexy, cache-bust `?v=953` cho browser, 4 legacy cleanup) |
| **9.6** | **Mobile fix** | **Hamburger + responsive foundation** (chèn TRƯỚC UI-06 theo yêu cầu user 2026-05-25) | Hamburger toggle work ở range 768-1199px (Sprint 4.2 override hack scope lại `>=1200px`, bridge rule 768-1199px trong components.css trả lời `body.menu-open`, backdrop overlay click-to-close) + responsive auto-scale foundation: `html { font-size }` step 14→15→16px theo viewport + 3 utility class `.wujia-container .wujia-grid-responsive .wujia-stack-mobile` trong `_components.css` cho UI-06+ tiêu thụ thay vì hand-tune từng form | ✅ DONE 2026-05-25 |
| 9.7 | UI-06 | Card | Background page chưa chuẩn, cần đậm thêm | Page **#F5F7FA hoặc #F6F8FA**; card **trắng #FFFFFF**. | ✅ DONE 2026-05-25 (page bg `#E8ECEF` neutral gray L≈92, đậm hơn BA spec để card trắng nổi rõ — anh chọn sau 2 iter; kèm UI-05 follow-up 3 button "Xem tất cả" home page) |
| 9.8 | UI-07 | Sidebar | Khoảng cách logo→menu không đồng đều | Logo area height **180–220px**, menu bắt đầu cùng vị trí mọi page | ✅ DONE 2026-05-25 |
| 9.9 | UI-09 | Header | Header chưa thống nhất height/padding | Height **72–80px**, padding **24–32px**, **align center** toàn item | ✅ DONE 2026-05-25 |
| 9.10 | UI-11 | Font | Font + độ đậm chưa thống nhất | Font **Inter/Arial**. Body **15–16px**, title **32–36px**, card title **20–22px**, table **15–16px** | ⬜ pending |
| 9.11 | UI-12 | Card | Card Home + Support khác radius/shadow/border | Border **1px solid #E5E7EB**, radius **12–16px**, shadow **rất nhẹ hoặc không** | ⬜ pending |
| 9.12 | UI-14 | Badge | Status có chỗ là text thường ("Draft") | Tất cả status dùng **badge mềm** | ⬜ pending |
| 9.13 | UI-15 | Responsive | Detail panel Support cắt khi màn nhỏ | Desktop **2 cột**, tablet/mobile detail xuống dưới hoặc **drawer/modal** | ⬜ pending |
| 9.14 | Empty | Empty state | Empty state "Chưa có dữ liệu" còn thô | **icon nhỏ + dòng text + khoảng trắng chuẩn** | ⬜ pending |
| 9.15 | — | Cleanup | (Quick wins, không trong Issue List) | 301 redirect `/portal/purchase_history` → `/portal/purchase-history`, `/portal/return-request-list`, `/portal/exam-registration` + xóa `custom/wujia_account/` stub trống | ⬜ pending |
| 9.16 | — | Verify | — | `scripts/reseed_full.sh` RC=0 + `scripts/test_sprint9.py` (13 route + 13 CSS assertion) + 8 screenshot | ⬜ pending |
| 9.17 | — | Doc | — | `chapters/18-sprint9-issue-list-ui-refactor.tex` 13 sub-section + `chapters/19-roadmap-v14-gaps.tex` (affiliate/dashboard/TOTP) + master `\include` + recompile PDF qua `scripts/build-doc.sh` + update §2/§4/§5/§9 file này | ⬜ pending |
| 9.18 | — | Push | — | Commit Conventional EN + push `main` + cho lệnh deploy Windows | ⬜ pending |

### Files đã chạm (Sprint 9.1)

- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — active state BG primary + color #FFF + icon color #FFF (cũ: primary-soft + active-text).
- `custom/wujia_portal_layout/views/layouts.xml` — `fa fa-home` → `feather icon-home` + "Trang chủ" → "Home".
- `custom/wujia_portal_{delivery,sale,info_request,purchase_history,report,notification,exam,return,support,knowledge}/views/sidenav_inherit.xml` — 11 file, replace toàn bộ `fa fa-*` solid → `feather icon-*` outline.

### Files đã chạm (Sprint 9.2)

- `custom/wujia_portal_layout/views/layouts.xml` — xoá block `<div class="sidebar-header mt-3">…</div>` (user-pic + user-info, 12 dòng).
- `custom/wujia_portal_layout/static/assets/css/style.css` — xoá 33 dòng CSS orphan `.sidebar-header*`.
- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — sửa comment "Logo + user-pic" → "Logo".

### Files đã chạm (Sprint 9.5 — UI-05 Button, 2026-05-24)

- `custom/wujia_portal_layout/static/assets/css/_variables.css` — thêm token `--wujia-btn-height-secondary: 38px` (mid range BA 36-40).
- `custom/wujia_portal_layout/static/assets/css/_components.css` — refactor block button:
  - `.btn / .wujia-btn` base: `min-height var(--wujia-btn-height)` (42), `padding 0 16px`, `display inline-flex` + `align-items center` + `justify-content center` + `gap 6px` + fallback `text-align center` + `vertical-align middle` + `line-height 1.4`.
  - `.btn.btn-block / .wujia-btn.btn-block` ép `display flex` (vì Bootstrap `.btn-block` set `display:block` huỷ flex-center).
  - **Icon vertical-align fix:** `.btn > i / .fa / .feather` set `line-height 1` + `display inline-flex` + `align-items center` + `vertical-align middle` — fix Vuexy `bootstrap.css:2552` `.btn { line-height: 1 }` làm icon Font Awesome lệch baseline so với text.
  - Primary (`.btn-primary, .wujia-btn-primary`): bg `--wujia-primary` cyan + color `#FFFFFF`, hover `--wujia-primary-dark`.
  - Secondary gom 4 alias (`.btn-secondary, .btn-outline-primary, .btn-outline-secondary, .wujia-btn-secondary`): bg `#FFFFFF` + border `1px solid --wujia-border` + color `--wujia-text-primary` + min-height 38, hover bg `--wujia-bg-page`. **Trade-off:** mất visual outline-primary cyan border cũ → đồng nhất theo BA cột I.
  - Semantic (`.btn-success/.btn-danger/.btn-warning/.btn-info` + outline variants): chỉ force `min-height: 42` để đồng bộ chiều cao, giữ màu Bootstrap default.
- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — xoá duplicate `.btn-primary { ... }` rule (đã có ở `_components.css`).
- `custom/wujia_portal_layout/static/assets/css/style.css` — xoá `.bg-btn-primary` (zero usage) + `.btn-outline-primary-custom` (zero usage).
- `custom/wujia_portal_layout/static/assets/css/dashboard.css` — xoá `.primary-btn` legacy v14 navy pill (bg #1e4080 border-radius 50px, chỉ dùng 1 lần ở `login_page.xml`).
- `custom/wujia_portal_layout/views/login_page.xml` — migrate `.primary-btn` → `.btn .btn-primary` (line 67); xoá inline `style="color: var(--wujia-primary);"` thừa line 194 + line 197 (line 197 là BUG: cyan text trên cyan bg = invisible).
- `custom/wujia_portal_layout/views/assets.xml` — thêm `?v=953` query string vào 5 CSS file (`_variables` + `style` + `dashboard` + `_wujia_theme` + `_components`) để bust browser cache (TTL 7 ngày).
- `custom/wujia_portal_layout/__manifest__.py` — bump version `19.0.3.0.0` → `19.0.3.1.0`.

**Verify:** Upgrade RC=0. wkhtmltoimage screenshot `/portal/info-request` + `/portal/order` xác nhận button cyan + white + icon-text canh giữa. CSS curl xác nhận `_components.css?v=953` serve nội dung mới (không còn `padding 0 16px` xung đột Vuexy).

**Gotcha mới:**
1. **Browser cache 7 ngày** — Odoo serve `/module/static/` với `Cache-Control: public, max-age=604800`. Mọi CSS change ở Sprint UI tiếp theo PHẢI bump `?v=` query trong `assets.xml` nếu không user sẽ thấy CSS cũ dù upgrade RC=0.
2. **Vuexy `.btn { line-height: 1 }`** (`bootstrap.css:2552`) gây icon Font Awesome lệch baseline so với text trong button. Fix bằng rule `.btn > i { line-height: 1; display: inline-flex; align-items: center }` — KHÔNG đụng vào `.btn` base line-height (giữ 1.4 cho text wrap đa dòng).

### Files đã chạm (Sprint 9.6 — Mobile fix + responsive foundation, 2026-05-25)

**A — Hamburger fix (v3 dynamic body-class swap, V14 native pattern):**

- `custom/wujia_portal_layout/static/assets/css/style.css:113-150` — Sprint 4.2 force-visible override đổi scope `@media (min-width: 992px)` → `@media (min-width: 1200px)`. Lý do: override cũ pin sidebar luôn show ở >=992px → toggle button ở range 992-1199px click vô hiệu. Ở <1200px shim JS swap body sang `vertical-overlay-menu` nên rule `.vertical-menu-modern` không fire — Vuexy native overlay CSS handle tất cả (sidebar/navbar/content/backdrop).
- `custom/wujia_portal_layout/static/assets/js/wujia_responsive_menu.js` — **NEW FILE** dynamic shim: trên `DOMContentLoaded` + `window.resize` (debounce 100ms) + `orientationchange`, gọi `matchMedia('(min-width: 1200px)')` để swap `body.vertical-menu-modern` ↔ `body.vertical-overlay-menu`. Tái áp đặt logic Vuexy `app.js:44 Unison.on('change', $.app.menu.change)` mà bị miss khi DevTools resize / load race. Pure body class flip, KHÔNG có per-element `!important` override → không ảnh hưởng UI desktop trước đó.
- `custom/wujia_portal_layout/static/assets/css/components.css:3632-3646` — chỉ còn comment block (v3 xóa toàn bộ `@media (max-width: 1199.98px)` heavy override v2 — không cần vì Vuexy native overlay CSS đã handle đủ một khi body class đúng).
- `custom/wujia_portal_layout/views/layouts.xml:139` — thêm `<div class="sidenav-overlay"/>` sau closing `</div>` của `.main-menu` (Vuexy JS app-menu.js bind click handler + `open()/hide()` toggle `d-block/d-none` trên class này, chỉ cần DOM element tồn tại).
- `custom/wujia_portal_layout/views/assets.xml` — thêm `<script src="wujia_responsive_menu.js?v=970"/>` cuối block `asset_style_js`.

**Lý do v3 thay v2:** v2 dùng `body.vertical-menu-modern { ... !important }` đè width/margin/transform khắp navbar/content/footer để fix hardcode → fragile, ảnh hưởng các fix UI cũ, user feedback "đừng fix chết theo từng form". V3 trả về V14 pattern gốc: JS swap body class → Vuexy native CSS handle, zero hardcode CSS override.

**B — Responsive auto-scale foundation:**

- `custom/wujia_portal_layout/static/assets/css/_variables.css` — thêm 2 token + 1 block scaling:
  - `--wujia-sidebar-transition: transform 0.25s ease-in-out`.
  - 4 canonical breakpoint token `--wujia-bp-sm/md/lg/xl: 576/768/992/1200px` (chuẩn Bootstrap, document KHÔNG dùng 550/770/850 ad-hoc nữa).
  - Block `html { font-size }` fluid scaling: 14px (<576), 14px (576+), 15px (768+), 16px (992+), 16px (1200+). Mọi giá trị rem trong codebase tự scale theo viewport — template KHÔNG phải tune từng @media per form.
- `custom/wujia_portal_layout/static/assets/css/_components.css` — thêm 3 utility class shared (V14 KHÔNG có pattern này, build mới cho v19):
  - `.wujia-container` — `width 100% + padding-inline clamp(12px,3vw,32px) + max-width 1400px`.
  - `.wujia-grid-responsive` — `display grid + grid-template-columns repeat(auto-fit, minmax(min(280px,100%), 1fr)) + gap clamp(12px,2vw,24px)`. Replace verbose `col-12 col-md-6 col-lg-4`.
  - `.wujia-stack-mobile [+ .wujia-row-md]` — column on mobile, optional row at >=768px.

**Cache-bust + version:**

- `custom/wujia_portal_layout/views/assets.xml` — bump tất cả `?v=953` → `?v=960` (5 file) + thêm `?v=960` vào `components.css` (trước Sprint 9.6 KHÔNG có cache-bust, vì components.css là Vuexy vendor không edit). **v3 (2026-05-25):** bump toàn bộ → `?v=970` cho JS shim mới.
- `custom/wujia_portal_layout/__manifest__.py` — bump `19.0.3.1.0` → `19.0.4.0.0`.

**Verify:** Upgrade RC=0 (`scripts/upgrade.sh wujia_portal_layout`). Curl xác nhận `components.css?v=960` serve Sprint 9.6 bridge rule, `_variables.css?v=960` serve root font-size block, `_components.css?v=960` serve `.wujia-grid-responsive`. Browser smoke test ở 3 viewport (375/800/1024/1280) — user verify thực tế.

**Gotcha mới (Sprint 9.6):**

1. **Mobile menu = vấn đề BODY CLASS, không phải CSS gap** — v1/v2 misdiagnosis: tưởng Vuexy CSS thiếu rule ở range 768-1199px, fix bằng `@media` override hardcode `!important`. V3 (đúng root cause): Vuexy native overlay-menu CSS đầy đủ, vấn đề là JS swap `body.vertical-menu-modern` → `body.vertical-overlay-menu` không fire (Unison.on('change') chain race trên DevTools resize / load). Fix dynamic: file `wujia_responsive_menu.js` re-assert swap qua `matchMedia` + resize listener. **Lesson L4 (2026-05-25):** trước khi viết CSS `!important` override, kiểm tra xem JS state machine có đang ở đúng class không — Vuexy theme đã có overlay-menu CSS hoàn chỉnh, không cần fight nó.
2. **Sprint 4.2 force-show !important = silently break toggle** — Override `@media (min-width: 992px) { .main-menu { left:0; opacity:1 !important } }` pin sidebar khiến `$.app.menu.toggle()` flip body class nhưng sidebar đã pin → user thấy click không hiệu lực. Anti-pattern: dùng `!important` để fix init bug mà không bound đúng scope khiến break toggle range tablet. Solution: scope override về range thực sự cần (>=1200px = desktop xl) thay vì broad >=992px.
3. **V14 KHÔNG có pattern auto-scale** — Grep co_*portal*/*.css confirm: no `html { font-size }` media query, no clamp(), 7 breakpoint ad-hoc (550/575.98/767.98/850/991.98/1199.98 + JS 768 trong `cart_mobile.js`). Mỗi template hand-tune `col-md-X col-lg-Y` riêng + `cart_mobile.js` JS show/hide DOM tay. **V14 không phải reference cho responsive — build pattern mới cho v19 dựa trên root font-size + utility class shared.**

### Files đã chạm (Sprint 9.4 — UI-04 Header mobile, 2026-05-24)

- `custom/wujia_portal_base/views/store_picker_navbar.xml` — thêm xpath thứ 2 inject SAU `<div class="header-navbar-shadow">` (KHÔNG sau `</nav>` vì Vuexy nav floating + có shadow wrapper riêng). Block: `<div t-if="_wujia_active_franchise" class="wujia-store-mobile-strip">` gồm label + name `t-out=display_name` + role badge mini. Reuse `_wujia_active_franchise` + `_wujia_active_role` từ `<t t-set>` cùng template (scope OK). KHÔNG dùng Bootstrap class `d-md-none` — gate qua `@media` trong CSS (Bootstrap utility set `display:none` không `!important` nên bị override bởi `.wujia-store-mobile-strip { display: flex }`).
- `custom/wujia_portal_base/static/src/css/store_picker.css` — append block UI-04:
  - Default `.wujia-store-mobile-strip { display: none }` (PC hide).
  - `@media (max-width: 767.98px)` set `display: flex` + `flex-direction: column` + `align-items: flex-start` + `margin-top: 7.5rem` (=105px @ html 14px) để escape Vuexy floating-nav (top 18px + height 90px = bottom 108px).
  - Adjacent sibling `.wujia-store-mobile-strip + .content-wrapper { margin-top: 0 !important }` để eliminate double-gap (Vuexy default content-wrapper `margin-top: 6rem`).
  - Children: `.wujia-store-mobile-strip-label` (cyan uppercase 11px), `.wujia-store-mobile-strip-name` (dark bold 15px ellipsis), `.wujia-store-role-badge-mini` (padding 4×12 min-h 26px).
  - `@media (max-width: 575.98px)` shrink xs font.
- `custom/wujia_portal_layout/static/assets/css/_variables.css` — thêm 5 token `--wujia-mobile-strip-*` (bg #FFFFFF, label color = var(--wujia-primary), name color = var(--wujia-text-primary), padding 12×16, border-bottom 1px solid var(--wujia-border)).

**Postmortem 2026-05-24:**

1. **Mockup mapping fail (attempts 1-2):** Em sai 2 attempts đầu — attempt 1 plan sub-strip nhưng badge position right (`justify-content: space-between`); attempt 2 confuse image UI-03 PC pill với UI-04 mobile, plan refactor UI-03 instead. Root cause: cherry-pick image theo số file (image23 vs image33) thay vì map qua openpyxl anchor → không biết G6 = image23 (spec chính khoanh đỏ) vs F6 = image33 (variant). Đã update rule §9 #9 + §10 L1 step 2 yêu cầu MAP IMAGE TO CELL qua `openpyxl ws._images[i].anchor._from.row/col`.

2. **Floating navbar collision fail (attempt 3-5):** Sau khi build xong, mobile screenshot → strip rendered nhưng HIDDEN behind navbar (top=0 phía sau `position:fixed` navbar top=18 bottom=108). Vuexy theme `navbar-floating` = `position:fixed` nên element inject sau `.header-navbar-shadow` vẫn ở top=0 vì shadow là sibling fixed. Fix: `margin-top: 7.5rem` (=105px) push strip xuống dưới navbar bottom (108px) + adjacent selector eliminate content-wrapper's default 6rem gap (84px). Final state @ mobile-500: strip top=84 height=91 → content-wrapper top=175 (sát strip).

3. **V14 reference fail (attempt 4):** User reminder "sao bạn ko xem source v14, v14 có làm" → em **chưa check v14 dù §10 L2 đã có rule**. Grep thorough toàn bộ co_*wujia* modules confirm: v14 KHÔNG có Current Store strip (v14 single-franchise model — không cần picker UI). Commands đã chạy (lưu cho session sau): `grep -rln "Cửa hàng\|store\|hiện tại" /home/huyban/odoo-dev/wujia_tea_odoo14/modules/ --include="*.xml" --include="*.html" --include="*.css"` qua `co_portal_wujia`, `co_portal_base`, `co_portal_wujia_v2`, `co_franchise_store_wujia`, `co_filter_wujia`, `co_wujia_api` — đều 0 match. v14 `co_portal_wujia/views/portal/layout_nav_inherit.xml` REPLACE nav: chỉ language + cart + notification + user dropdown, KHÔNG có Current Store. v14 `co_portal_base/static/assets/css/components.css:67-70` set Vuexy default `.content-wrapper { margin-top: 6rem }` y hệt v19 → pattern offset của UI-04 không sẵn có ở v14, build từ đầu. **Bài học: §10 L2 đã có rule v14 check nhưng em vẫn skip — phải tự kiểm rule trước khi code, đừng đợi user nhắc.**

Plan file: `/home/huyban/.claude/plans/sprint-9-4-magical-noodle.md`.

### Files đã chạm (Sprint 9.7 — UI-06 page bg + UI-05 home button, 2026-05-25)

**A — UI-06 page background (iter 1 → iter 2):**

- `custom/wujia_portal_layout/static/assets/css/_variables.css:15` — `--wujia-bg-page`:
  - **Iter 1** (anh chọn match v14): `#F5F7FA` → `#f9f9fb` (= V14 `co_portal_base/components.css:11` default).
  - **Iter 2** (anh visual feedback "chưa đậm"): `#f9f9fb` → `#E8ECEF` (neutral gray L≈92, contrast rõ với card trắng #FFFFFF). Lệch BA cột H spec (BA đề xuất `#F5F7FA`/`#F6F8FA`) — anh override 2026-05-25, BA Hùng confirm Sprint 9.17 recap.
- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css:7-17` — selector `html, body` → `html body` (no comma). **Root cause specificity bug:** Vuexy `components.css:11` có `html body { background-color: #f9f9fb }` specificity 0,0,2 thắng cascade vs `html, body` specificity 0,0,1 mỗi vế. Fix: dùng selector cùng specificity 0,0,2 + load sau win. Trước fix: token định nghĩa `#F5F7FA` nhưng render thực tế là Vuexy default `#f9f9fb`. Comment block trong rule giải thích chi tiết.
- `custom/wujia_portal_layout/views/assets.xml:15` — bump `?v=1010` → `?v=1030` (2 iter) cho `_variables.css`.
- `custom/wujia_portal_layout/views/assets.xml:83` — bump `?v=1010` → `?v=1020` cho `_wujia_theme.css`.
- `custom/wujia_portal_layout/__manifest__.py:3` — bump `19.0.4.0.0` → `19.0.5.1.0` (iter 1 minor + iter 2 patch).

**B — UI-05 follow-up: 3 button "Xem tất cả" home page:**

- `custom/wujia_portal_base/views/portal_home.xml:94,120,153` — class `btn btn-sm btn-outline-primary` → `btn btn-primary btn-sm` (Latest notifications + Recent orders + Latest return requests). Áp UI-05 primary spec (xanh `--wujia-primary` + chữ trắng, h=42px, padding-x compact nhờ `btn-sm`). Text canh giữa tự động nhờ rule UI-05 Sprint 9.5 `.btn { display: inline-flex; justify-content: center; align-items: center }` ở `_components.css`. Pattern này giống button "Lọc" `portal_delivery.xml:38` — visual consistency cross-page.
- `custom/wujia_portal_base/__manifest__.py:3` — bump `19.0.5.0.0` → `19.0.5.2.0`.

**Verify:** Upgrade `wujia_portal_layout` + `wujia_portal_base` RC=0. Curl `_variables.css?v=1030` serve `#E8ECEF`. Curl `/portal/login` inject `?v=1030`. Source grep: 0 leftover `btn-outline-primary">Xem t`, 3 occurrence `btn-primary btn-sm">Xem t` mới. Browser visual verified ở port 8019.

**Gotcha mới (Sprint 9.7):**

1. **Token định nghĩa ≠ token render** — Sprint 8 đã add `--wujia-bg-page: #F5F7FA` token với selector `html, body` apply, tưởng DONE. Render thực tế hiện `#f9f9fb` (Vuexy default) trong 4+ tháng vì CSS specificity bug âm thầm. BA Hùng list lại UI-06 mới phát hiện. **Lesson:** mọi token apply qua selector multi-element (`html, body`, `body, html`) PHẢI check specificity vs Vuexy single-element selector (`html body`). Khi audit token, KHÔNG chỉ grep `var(--wujia-*)` mà còn phải computed-value check trong browser DevTools.
2. **Render `#f9f9fb` quá nhạt cho card-on-white** — V14 dùng `#f9f9fb` nhưng v14 KHÔNG có card-heavy layout nhiều như v19 Sprint 5+. V14 layout đặc trưng table + list inline trên body, ít card border-radius độc lập. V19 sau Sprint 5 inject card khắp portal → BG quá nhạt mất contrast. **Decision:** lệch v14 + lệch BA spec là OK khi UX yêu cầu rõ. Document rationale trong commit + §9.
3. **`btn-sm` không giảm chiều cao sau Sprint 9.5** — Bootstrap `.btn-sm` set `padding-y: 0.25rem + font-size: 0.875rem` nhưng KHÔNG set height. Sprint 9.5 `min-height: var(--wujia-btn-height)` (42) enforce → button vẫn h=42 dù có `btn-sm`. `btn-sm` chỉ giảm padding-x → chiều rộng gọn. Đây chính xác là điều anh muốn cho "Xem tất cả" (gọn ngang giữ cao chuẩn).

### Files đã chạm (Sprint 9.8 — UI-07 Sidebar logo area height, 2026-05-25)

- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — thêm 2 rule sau `.sidebar-header-spacer` block: `.main-menu .navbar-header { height: var(--wujia-sidebar-logo-h) !important; display: flex !important; align-items: center !important; justify-content: center !important; margin-bottom: 0 !important; }` + `.main-menu .navbar-header img { max-height: calc(var(--wujia-sidebar-logo-h) - 40px) !important; width: auto !important; object-fit: contain !important; }`. Override Bootstrap `mb-5` (3rem) vốn thay đổi theo fluid font-size (42-48px).
- `custom/wujia_portal_layout/views/assets.xml:83` — bump `?v=1020` → `?v=1040` cho `_wujia_theme.css`.
- `custom/wujia_portal_layout/__manifest__.py:3` — bump `19.0.5.1.0` → `19.0.5.2.0`.

**Root cause:** Token `--wujia-sidebar-logo-h: 200px` tồn tại từ Sprint 8 nhưng chưa apply vào `.navbar-header`. Bootstrap `mb-5` = `3rem` margin-bottom thay đổi theo viewport (14px base → 42px; 16px base → 48px), làm menu start position lệch theo viewport chứ không phải theo page. Fix: enforce `height: 200px` + `margin-bottom: 0` → logo area = constant 200px mọi viewport, menu luôn bắt đầu tại 232px (200 + 32px spacer). Upgrade RC=0.

### Files đã chạm (Sprint 9.9 — UI-09 Header height + vertical center, 2026-05-25)

- `custom/wujia_portal_layout/static/assets/css/_wujia_theme.css` — thêm 2 rule sau `.wujia-navbar` block: `.header-navbar { height: var(--wujia-header-height) !important; min-height: var(--wujia-header-height) !important; }` + `.header-navbar .navbar-container { height: 100% !important; display: flex !important; align-items: center !important; }`. Token `--wujia-header-height: 72px` (đã có từ Sprint 8, lần này mới apply).
- `custom/wujia_portal_layout/views/assets.xml:83` — bump `?v=1041` → `?v=1042`.

**Note:** UI-07 và UI-09 ship cùng 1 commit. `_wujia_theme.css` cũng chứa fix logo overflow (UI-07 iter 2): thêm `overflow: hidden` + `max-width: 200px; height: auto` cho `.navbar-header img`.

### Policy update (2026-05-24)

Anh đổi rule: **mỗi sprint con UI xong = commit + push luôn**, không gộp tới Sprint 9.17. Quy tắc §9 #4 "1 issue ≠ 1 commit lớn" vẫn giữ (1 issue có thể nhiều iteration), nhưng khi DONE issue đó → push ngay. Sprint 9.17 chỉ còn deploy + recap nghiệp vụ.

### Nguyên tắc tuyệt đối cho mọi session Sprint 9 tiếp theo

1. **KHÔNG BỊA SPEC.** Trước khi code 1 issue, MỞ `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` → sheet "5. Issue List" → đọc đúng row của issue đó → paste lại cột G + H verbatim vào chat → user xác nhận → mới code. Cột E + F là Vấn đề + Hình minh hoạ tham khảo, KHÔNG phải spec; G/H mới là spec.
2. **Code English-only.** Chuỗi tiếng Việt chỉ chấp nhận ở template UI text hiện hữu (chưa migrate). Không tạo `.po` Sprint 9 — BA tự lo Sprint 10.
3. **Read-before-write.** `grep -rn` trong `custom/` xem rule CSS / template hiện có rồi mới sửa. Không đoán selector.
4. **1 issue ≠ 1 commit lớn.** 1 issue = 1 sprint con = nhiều iteration nhỏ. User screenshot vs mockup → loop fix → 100% khớp → next issue.
5. **CSS var bắt buộc.** Mọi giá trị (color, radius, height, font-size) PHẢI là `var(--wujia-*)` trong `_variables.css`. Không hex/px cứng trong template hay file CSS module-level.
6. **Component reuse.** Class chung trong `_components.css` (`.wujia-btn`, `.wujia-badge-*`, `.wujia-empty-state`, `.wujia-two-pane`). Nếu thiếu class — bổ sung ở `_components.css`, không inline style/class riêng từng template.
7. **Verify gate.** Mỗi sprint con: `bash scripts/upgrade.sh "<module1>,<module2>"` RC=0 → restart Odoo → screenshot trang liên quan → so vs mockup col F → nếu lệch, sửa tiếp → đạt 100% → user OK → mới đánh dấu DONE trong §9 bảng này.
8. **Update §9 bảng này khi DONE 1 issue.** Đổi ⬜ → ✅ + thêm ngày + 1 dòng "Files đã chạm".
9. **EXTRACT HẾT IMAGE TRONG XLSM + MAP IMAGE TO CELL** (RULE expanded sau Sprint 9.3 + 9.4 FAIL 2026-05-24). Sheet "5. Issue List" có nhiều image anchored per row (cell E/F/G). PHẢI `unzip -j xlsm "xl/media/imageNN.png"` cho **TẤT CẢ image trong range của issue** (vd UI-03 có image26-33 = 8 ảnh), KHÔNG cherry-pick 1-2 ảnh. Đọc cả 8 bằng Read tool. Quy ước annotation BA:
   - **Khoanh đỏ** = TARGET CHÍNH (block phải làm chuẩn theo đó).
   - **Gạch chéo đỏ** = XÓA element này.
   - **Gạch chân đỏ** = highlight detail (chú ý thuộc tính cụ thể).
   - Image KHÔNG có annotation = mockup hint/variant, vẫn cần đọc nhưng ưu tiên thấp hơn.

   **MỚI (Sprint 9.4 FAIL 2026-05-24):** PHẢI dùng openpyxl `ws._images[i].anchor._from.row/col` để biết image anchor cell nào (xem §10 L1 step 3). Cherry-pick image theo số file (image23 vs image33) KHÔNG đủ — phải biết cell mapping. Sprint 9.4 sai 2 lần vì cherry-pick image33 (F6 variant không annotation) thay vì image23 (G6 spec chính BA khoanh đỏ), và confuse với mockup UI-03 PC pill. BA có thể đặt mockup chính ở col G chứ không phải col F.
10. **ĐỌC SOURCE V14 TRƯỚC khi code feature mới** (RULE MỚI — sau Sprint 9.3 FAIL 2026-05-24). Path: `/home/huyban/odoo-dev/wujia_tea_odoo14/enterprise/modules/co_portal_wujia/` + `co_franchise_store_wujia/` + `co_portal_base/`. V14 có thể đã có pattern template/CSS/model chuẩn, copy + adapt v19 dễ hơn build từ đầu. Nếu confirm v14 KHÔNG có (như Current Store block UI-03) → ghi rõ "v14 KHÔNG có" + build từ đầu.

### Handoff prompt cho session sau (paste sau `/wujia-start`)

```
Trong session này, em tiếp tục Sprint 9 (Issue List UI refactor). UI-01 đã DONE local.
Em làm Sprint con kế tiếp = <UI-XX> (xem §9 bảng wujia-compact-summary.md).

Quy tắc Sprint 9 (BẮT BUỘC):
1. Mở WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm → sheet "5. Issue List" → đọc row UI-XX → paste cột G + H verbatim vào chat → đợi anh xác nhận → mới plan + code. KHÔNG bịa spec ngoài G/H.
2. Code English-only. Không tạo .po.
3. CSS dùng var(--wujia-*) trong _variables.css; component reuse class trong _components.css. Không hex cứng, không inline.
4. Workflow per issue: read xlsm exact → grep v19 hiện trạng → plan ngắn → anh approve → edit → bash scripts/upgrade.sh "<modules>" RC=0 → restart Odoo → screenshot vs BA mockup col F → loop fix → 100% khớp → anh OK → đánh dấu ✅ trong §9 bảng → next issue.
5. KHÔNG bỏ qua issue, làm tuần tự BA order. 1 issue = 1 commit + push ngay khi anh OK screenshot (policy 2026-05-24).

Out-of-scope session này: T-031 mockup operations, locust load test, affiliate v14 gap, .po dịch.

Khi hết session: update §9 bảng wujia-compact-summary.md (đổi ⬜ → ✅ + ngày + Files đã chạm) trước khi đóng session.
```

**→ Quan trọng cho future session:** đừng tin trí nhớ về spec — luôn mở lại xlsm cho mỗi issue. BA Hùng có thể edit sheet bất kỳ lúc nào.

---

## §10 wujia-sprint9-3-ui03-fail-postmortem-and-correct-spec

**Status:** Sprint 9.3 (UI-03 Header PC) **DONE 2026-05-24 sau 3 attempts** — final shipped design ở cuối §10. Postmortem dưới đây giữ nguyên cho lesson learned.

### Hiện trạng code lần 1 (ĐỪNG mark DONE)

Files đã chạm (4 file) — có thể giữ tạm hoặc revert + rebuild theo spec chuẩn:
- `custom/wujia_portal_layout/views/layouts.xml` — đã **XÓA** block language dropdown (lines 47-76 cũ) + **XÓA** span user-name text trong avatar dropdown.
- `custom/wujia_portal_base/views/store_picker_navbar.xml` — xpath đổi: chèn pill vào left `bookmark-wrapper` (cũ: chèn vào right `float-right ul`). Text: `display_name` thay `name`. Icon: feather icon-home + icon-repeat (cũ: fa fa-building + fa fa-exchange). Label vẫn là "Đang tại:" (PHẢI đổi → "Cửa hàng hiện tại").
- `custom/wujia_portal_layout/static/assets/css/_variables.css` — thêm 7 token `--wujia-navbar-pill-*` (bg `rgba(255,255,255,0.18)` translucent white — SAI vs mockup).
- `custom/wujia_portal_base/static/src/css/store_picker.css` — refactor `.wujia-active-store-badge` dùng CSS var.

### Root cause: 4 sai lầm

1. **Chỉ extract 2/8 image trong xlsm** (image28, image29) — bỏ sót image26 (mockup CHÍNH của UI-03 với annotation khoanh đỏ + format pill light cyan + role badge xanh lá Manager).
2. **Hỏi user "spec vs mockup"** khi xung đột → user chọn "build theo mockup" — nhưng mockup em show ra (image28) chỉ là 1 phần. Hệ quả: bỏ luôn role badge + language dropdown khỏi plan, trái spec cột H đầy đủ.
3. **Đọc màu pill sai**: mockup image28 + image26 có pill **light cyan + text dark navy** → em làm white translucent rgba(255,255,255,0.18) + text trắng (vì assume pill trên dark navbar). Đúng: bg `#E0F7FF` (var(--wujia-primary-light)) + text `var(--wujia-text-primary)`.
4. **KHÔNG check v14 trước khi code**: anh nhắc nhở rule này nhiều lần. Em đã check sau khi FAIL → confirm v14 KHÔNG có pattern Current Store + role badge → phải build từ đầu. Nếu check trước → biết là feature mới → đầu tư plan kỹ hơn.

**Lưu ý position:** lần 1 em chèn pill vào left `bookmark-wrapper` navbar — POSITION ĐÚNG (anh confirm 2026-05-24 "build sát header trái"). Em từng đoán sai phải move sang top content area dựa trên image26 — bị anh corect. Image26 chỉ là crop format mock của widget, không phải position. Position thực: SÁT LEFT EDGE NAVBAR (như lần 1).

### Spec CHUẨN cho UI-03 — session sau làm theo

**Mockup nguồn:** `xl/media/image26.png` (BA crop block widget — anh khoanh đỏ để highlight format) + `xl/media/image28.png` (placement reference: pill + Administrator + avatar trong navbar) + spec cột H verbatim.

**Position (anh confirm 2026-05-24):** widget hiển thị **SÁT BÊN TRÁI HEADER NAVBAR**, KHÔNG phải top content area. Inject vào `bookmark-wrapper` left side của `wujia_portal_layout.layout_top_navbar` (lần 1 em làm đúng position này). XPath: `//div[hasclass('bookmark-wrapper')]/ul[hasclass('navbar-nav')]` position="inside" — chèn sau menu toggle.

**Cấu trúc widget (image26 cho format + image28 cho placement):**
```
┌────────────────────────────────────────────────────────────────────────┐
│ NAVBAR (bg primary #22A9DE)                                            │
│ ┌─────────────────────────────────────┐ ┌─────────┐         ┌────┐    │
│ │ Cửa hàng hiện tại                   │ │ Manager │  ...     │ AV │    │
│ │ [H000] Cửa hàng 125 Điện Biên Phủ   │ └─────────┘         └────┘    │
│ └─────────────────────────────────────┘                                │
│   ↑ pill light cyan + text dark navy    ↑ role badge        ↑ avatar  │
│   sát LEFT edge navbar                   xanh lá             RIGHT     │
└────────────────────────────────────────────────────────────────────────┘
```

Label "Cửa hàng hiện tại" có thể là caption nhỏ phía trên pill (theo image26) HOẶC inline trước `[code]` trong pill — confirm với BA Sprint 10 nếu lệch.

**4 element theo spec cột H** (combo image26 + image28):
1. **Current Store pill** — `[code] tên` (display_name). Bg `var(--wujia-primary-light)` #E0F7FF (NOT translucent white). Text `var(--wujia-text-primary)` #1F2933 (NOT white). Padding ~6-10px 14-16px. Border-radius ~10-12px. Icon trái optional (building/home outline) — image26 có icon building, image28 không rõ. Vị trí: cụm sát LEFT navbar, không phải float-right.
2. **Role badge** — Manager/Owner/Staff label English. Bg `var(--wujia-success)` #24B269 (Manager = xanh lá). Cần variant theo role: Owner = vàng `var(--wujia-warning)`, Staff = xám `var(--wujia-muted-bg)` (suy đoán, BA chưa confirm — HỎI nếu không chắc). Nguồn data: `wujia.franchise.member.find_active_membership(user.id, franchise.id).role` (xem §5 + helper trong `wujia_franchise/models/wujia_franchise_member.py:124`). Đặt ngay cạnh PHẢI pill, cùng cụm LEFT navbar.
3. **Language dropdown** — RESTORE vào navbar phải (đã xóa trong code lần 1). Spec cột H yêu cầu, image28 mock không show nhưng cột H spec ưu tiên.
4. **Avatar dropdown** — giữ navbar phải. **KHÔNG show user-name text** (anh confirm 2026-05-24 — mockup image31 sidebar đã gạch chéo Administrator + image28 navbar không show user name text). Chỉ avatar tròn + dropdown menu Profile/Password/Logout.

**Label text:** dùng tiếng Việt "**Cửa hàng hiện tại**" (anh confirm 2026-05-24) thay vì "CURRENT STORE" / "Đang tại:". BA sẽ migrate `.po` Sprint 10.

**Icon role badge:** không cần icon, plain text badge đủ (theo image26).

**V14 reference:** sau 7 bước exhaustive search (102 module v14, full keyword + color + path), **CONFIRMED v14 KHÔNG có pattern Current Store widget + role badge** này. Anh có giả thuyết image26 chụp từ v14 nhưng search không xác nhận — nhiều khả năng image26 là Figma/Photoshop mockup BA tự design, KHÔNG phải screenshot v14 running. Build từ đầu cho v19.

### Plan UI-03 fix lần 2 (session 2026-05-24 tiếp): refactor từ state lần 1

**Quyết định 2026-05-24:** UI-03 fix lần 2 làm NGAY trong session này (refactor 4 file đã edit theo §10 spec). UI-04 (mobile) làm SESSION SAU (riêng, sau khi UI-03 PC stable). KHÔNG bundle.

**Approach:** keep 4 file lần 1 + refactor (nhanh hơn revert):
1. `_variables.css` — đổi 7 token `--wujia-navbar-pill-*` từ white translucent → light cyan + dark text.
2. `store_picker.css` — refactor `.wujia-active-store-badge` dùng token mới + add `.wujia-store-role-badge` (variant -manager/-owner/-staff).
3. `store_picker_navbar.xml` — thay "Đang tại:" → "Cửa hàng hiện tại", add `<t t-set>` cho `_wujia_active_role` qua `find_active_membership()`, render role badge sát phải pill.
4. `layouts.xml` — RESTORE block language dropdown (đã xóa lần 1, spec cột H yêu cầu).

### 2 lesson TUYỆT ĐỐI cho mọi session sau

- **L1 — EXTRACT FULL IMAGES + MAP IMAGE TO CELL TỪ XLSM** (expanded sau Sprint 9.4 FAIL 2026-05-24): trước khi code 1 issue, làm đủ 3 step:

  **Step 1 — list + extract image binary:**
  ```bash
  unzip -l "WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm" | grep "xl/media/image" | awk '{print $4}'
  mkdir -p /tmp/wujia_<issue>_mockup && cd /tmp/wujia_<issue>_mockup
  unzip -o -j "WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm" "xl/media/image*.png"
  ```

  **Step 2 — MAP image → cell qua openpyxl anchor (NON-NEGOTIABLE):**
  ```python
  from openpyxl import load_workbook
  wb = load_workbook('WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm', data_only=True)
  ws = wb['5. Issue List']
  for i, img in enumerate(ws._images):
      r = img.anchor._from.row + 1               # 1-indexed Excel row
      c = chr(65 + img.anchor._from.col)         # A-Z letter
      print(f"Image {i}: cell {c}{r}, path={img.path}")
  ```
  → biết chính xác image nào ở cell F6 vs G6 vs H6 của issue đó. Image NUMBER trong file name (image23.png vs image33.png) KHÔNG có quan hệ thứ tự với cell — phải map qua anchor.

  **Step 3 — Read TẤT CẢ image anchor vào row của issue (cả col E/F/G/H), KHÔNG cherry-pick.** BA có thể đặt mockup chính ở G chứ không phải F (UI-04 case: image chính ở G6 = image23.png, F6 = image33.png là variant). Nhận annotation BA per §9 rule #9 (khoanh đỏ / gạch chéo / gạch chân).

- **L2 — CHECK V14 TRƯỚC KHI BUILD MỚI**: trước khi viết template/CSS/Python mới, grep `/home/huyban/odoo-dev/wujia_tea_odoo14/modules/wujia-erp/` qua TẤT CẢ co_*wujia* modules:
  ```bash
  # Scope chuẩn: liệt kê modules portal v14 trước khi grep
  ls /home/huyban/odoo-dev/wujia_tea_odoo14/modules/wujia-erp/ | grep -E "^co_.*(wujia|portal|franchise)"
  # → co_portal_wujia, co_portal_base, co_portal_wujia_v2, co_franchise_store_wujia,
  #   co_filter_wujia, co_wujia_api, ...
  # Grep keyword đa file extension:
  grep -rln "<keyword1>\|<keyword2>" /home/huyban/odoo-dev/wujia_tea_odoo14/modules/ \
       --include="*.xml" --include="*.html" --include="*.css" --include="*.scss" --include="*.py"
  ```
  Nếu có → copy + adapt v19. Nếu KHÔNG → ghi rõ "v14 KHÔNG có pattern X" trong plan + build từ đầu. KHÔNG bỏ qua bước check.

  **Sprint 9.4 reinforcement (2026-05-24):** Em đã có rule này từ Sprint 9.3 nhưng vẫn skip ở Sprint 9.4 — user phải nhắc "sao bạn ko xem source v14, v14 có làm" mới chạy grep. **Self-discipline: trước khi gõ Edit file mới, đọc lại §10 L2 + chạy grep trên scope co_*wujia* — đừng đợi user nhắc.** UI-04 case confirmed: v14 KHÔNG có Current Store strip (single-franchise model), build từ đầu OK. Output grep cho UI-04 lưu nguyên format ở §9 Files đã chạm Sprint 9.4 postmortem #3 — reuse pattern cho UI-05+.

### Final shipped spec UI-03 (attempt 3 — 2026-05-24 DONE)

Spec §10 phần trên là "spec attempt 2" — sau khi ship attempt 2 user feedback "màu xấu, khung xanh nhạt chữ trắng, 2 dòng, role badge to". Attempt 3 mới khớp BA mockup `image26`. Final design ship được:

**Visual (image26 verbatim):**
- Pill bg: **frosted white over cyan navbar** `rgba(255,255,255,0.18)` (KHÔNG phải `--wujia-primary-light` solid như attempt 2). Hover: `rgba(255,255,255,0.28)`.
- Text: **white** `#FFFFFF` (KHÔNG phải dark navy như attempt 2).
- Layout: **2 dòng stacked** (KHÔNG single-row):
  - Dòng 1 (label): "Cửa hàng hiện tại" UPPERCASE + letter-spacing 0.6px + 11px + opacity 0.85
  - Dòng 2 (name): `[code] tên + address` bold 15px white
- **KHÔNG có icon** (attempt 2 có icon-home left + icon-repeat right — image26 không có icon nào).
- Role badge: solid `var(--wujia-success)` green, **font 14px bold + padding 10×20 + min-height 46px** (attempt 2 quá nhỏ).

**Files ship được (4 file giữ nguyên từ attempt 2, refactor visual):**
- `custom/wujia_portal_layout/static/assets/css/_variables.css` — token `--wujia-navbar-pill-bg: rgba(255,255,255,0.18)` + `--wujia-navbar-pill-text: #FFFFFF` + font 15px.
- `custom/wujia_portal_base/static/src/css/store_picker.css` — `.wujia-store-badge-text` flex column 2-row + `.wujia-store-badge-label` uppercase + `.wujia-store-badge-name` bold + `.wujia-store-role-badge` padding 10×20 font 14px min-height 46px + 3 variants `-manager/-owner/-staff`.
- `custom/wujia_portal_base/views/store_picker_navbar.xml` — XML không icon, structure `<span.wujia-store-badge-text><span.label/><strong.name/></span>` + 2nd `<li>` cho role badge dùng `find_active_membership().role`.
- `custom/wujia_portal_layout/views/layouts.xml` — restore language dropdown (đã xóa attempt 1).

**DB seed cho test long-name:** `UPDATE wujia_franchise_management SET name = 'Cửa hàng <số> <địa chỉ>, <quận>, <TP>'` — Test với 48 ký tự `[HCM-01] Cửa hàng 125 Điện Biên Phủ, Q.3, TP.HCM` — pill 2 dòng vẫn render đẹp, không overflow.

### 3rd lesson (after attempt 2 → 3 iteration)

- **L3 — VISUAL DESIGN: ĐỪNG ĐOÁN, HỎI EXPLICITLY**. Attempt 2 em đoán "khung light cyan + dark text" từ image26 (đọc sai màu). Attempt 3 user phải nói rõ "khung xanh nhạt chữ trắng + 2 dòng + bỏ icon + role to" mới đúng. Future: trước khi code visual, hỏi 4 câu cụ thể:
  1. Bg color exact (hex / token / rgba)?
  2. Text color (white / dark / token)?
  3. Layout (1-row inline / 2-row stacked)?
  4. Icon có / không (nếu có: feather name)?

  KHÔNG assume từ ảnh — eye nhìn màu hex sai dễ. Đặc biệt khi mockup pill chồng trên bg cùng tông màu (cyan-on-cyan), translucent vs solid khó phân biệt.

