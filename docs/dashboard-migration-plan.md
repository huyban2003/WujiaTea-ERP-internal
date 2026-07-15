# Wujia Dashboard Migration — State file

**Mục đích:** source of truth cho workstream migrate Dashboard Ninja → Odoo 19. Skill `/wujia-dashboard` đọc file này lúc kickoff; **update cuối mỗi step** (như compact-summary của workstream này). Full plan gốc: `/home/huyban/.claude/plans/tingly-juggling-boot.md` (session 2026-07-15).

**Cập nhật:** 2026-07-16 — **Step 1 DONE (Sprint 35)**: `wj_ks_dashboard_ninja` 19.0.1.0.0 installed trên `wujia_tea_19`, dashboard render tile + bar chart amCharts + list view, 0 JS console error, test_sprint9 7/7. Demo: board "WJ Demo Dashboard" (`scripts/seed_dashboard_demo.py`, idempotent). Deferred trong step: avatar-initials navbar (UserMenu xpath fail trên 19 — cosmetic, gỡ), 1 rule CSS chết `.ks-generateAI-body` trong style.css.

---

## §1 Bối cảnh + quyết định đã chốt

- **Mục tiêu:** dashboard backend cho BOD trên Odoo 19 (DB `wujia_tea_19`). KHÔNG đụng portal 1500 user.
- **Nguồn:** v16 `vietthuong/tools/{ks_dashboard_ninja,ks_dn_advance,ks_dn_formula}` (formula = custom của user) + v18 core `WujiaTea/ks_dashboard_ninja_v18/ks_dashboard_ninja` (18.0.1.0.1).
- **Base = v18 core** (OWL 2 full + amCharts 5 + SCSS design system) → port 18→19. v16 chỉ là tham chiếu feature cho advance/formula.
- **Rename cả 3:** `wj_ks_dashboard_ninja` / `wj_ks_dn_advance` / `wj_ks_dn_formula` trong `WujiaTea/custom/`. **Model `_name` GIỮ NGUYÊN `ks_dashboard_ninja.*`/`ks_dn.*`** (không đổi — blast radius DB).
- **STRIP AI** (không có API key Ksolves): arti_int/ai_dashboard/fetch_key/chat wizard/gTTS/SQLAlchemy.
- **BỎ TV mode/carousel.** Advance chỉ port: Custom SQL Query + 4 list layouts + redirect link + PDF print/mail.
- **Theme:** giữ nguyên v18 (pink `#E84A5F`/Poppins); reskin Wujia brand = step CUỐI optional. **Tính năng trước, giao diện sau** (user 2026-07-15).
- **License GIỮ `OPL-1`** — code Ksolves, KHÔNG relabel LGPL. Repo private, không redistribute. `ks_dashboard_ninja_v18/` gốc gitignore, chỉ commit `wj_ks_*`.
- Python deps sau strip: `pandas`, `xlrd`, `openpyxl` (+`xlsxwriter` cho pivot export Step 3) — **đã có sẵn trong conda env `odoo`** (verified 2026-07-15).

## §2 Step table

| Step | Nội dung | Sprint | Status | DoD gate |
|---|---|---|---|---|
| 1 | Skill + state file + scaffold/rename/strip AI/port core 18→19 | 35 | **✅ DONE 2026-07-16** | install RC=0 + 0 ERROR log; browser render tile + amCharts bar + list (Playwright); 0 JS console error; test_sprint9 7/7 |
| 2 | Port `wj_ks_dn_advance` subset (SQL query, 4 layouts, redirect, PDF) | TBD | TODO | query item render chart từ SQL; layout_2 ≠ layout_1; PDF download |
| 3 | Port `wj_ks_dn_formula` (formula + pivot + calc columns + grand total) | TBD | TODO | formula ra số; pivot render + totals; XLSX export; grand total row |
| 4 | Demo seed + test_sprint35 + Playwright suite | TBD | TODO | seed RC=0, test pass |
| 5 | `read_group`→`formatted_read_group` cả 3 module (`__domain`→`__extra_domain`) | TBD | TODO | 0 deprecation warning trong log sau 5' dùng |
| 6 | Reskin Wujia brand (`variable.scss`: primary→`#28A9DF`, Inter) — optional | TBD | TODO | screenshot so trước/sau |

**Active step: 2** (port `wj_ks_dn_advance` subset — SQL query, 4 list layouts, redirect link, PDF print/mail).

## §3 Rename discriminator rules (áp cho mọi step)

RENAME `ks_dashboard_ninja` → `wj_ks_dashboard_ninja` khi: `@ks_dashboard_ninja/` (JS import) · `ks_dashboard_ninja/static/...` (asset path có `/`) · `loadBundle("ks_dashboard_ninja.ks_dashboard_lib")` · `t-name=`/`t-call=`/`t-inherit="ks_dashboard_ninja.` (template) · XML external id `id=`/`ref=` + `ks_dashboard_ninja.board_menu_root` trong JS · route `/ks_dashboard_ninja/...`.

KEEP nguyên khi: model `_name`/`_inherit` (`ks_dashboard_ninja.board|item|child_board|...`) · `model:` trong JS rpc (kể cả template literal `${model}`) · field `ks_*` · CSS class `ks_*` · selection values (`ks_tile`, `ks_bar_chart`...).

Soát sót sau sed: `grep -rn "ks_dashboard_ninja" <module>/ | grep -v "ks_dashboard_ninja\."`.

## §4 Gotchas log

1. **CRITICAL (v18 bug sẵn):** `loadBundle("ks_dashboard_ninja.ks_dashboard_lib")` ở `ks_dashboard_ninja_new.js:310` trỏ bundle KHÔNG tồn tại trong manifest → crash render chart. Fix Step 1: khai báo bundle lazy, chuyển 11 lib amCharts vào (`index.js, percent.js, xy.js, radar.js, map.js, worldLow.js, Animated.js, Dataviz.js, Material.js, Moonrise.js, exporting.js`).
2. **`Ksdashboardlistview` v18 bị comment TOÀN BỘ** (231 dòng, import về `undefined`) — list view thật render qua `Ksdashboardgraph` (`ks_dashboard_graphs.js:26` branch `ks_list_view`). Hook list (layouts Step 2, grand total Step 3) phải patch `Ksdashboardgraph` hoặc `t-inherit` template, KHÔNG patch class chết.
3. Class KPI v18 tên **`Ksdashboardkpiview`** (không phải `KsDashboardKpiView`) — patch đúng tên.
4. **`safe_eval(formula, ctx, nocopy=True)` → TypeError trên 19** (signature mới `safe_eval(expr,/,context=None,*,mode,filename)`). Sửa Step 3: `ks_formula_engine.py:220`, `ks_calc_measure.py:114`, `ks_list_calc_column.py:115`.
5. **`formatted_read_group` trả `__extra_domain` thay `__domain`** (`odoo19/addons/web/models/models.py:860`). `read_group` deprecated vẫn chạy + trả `__domain` như cũ → Step 2/3 giữ read_group, Step 5 migrate + đổi key.
6. Advance v16 JS (`ks_labels.js`/`ks_ylabels.js`/`ks_dn_kpi_preview.js`) còn import legacy `web.core`/`web.field_utils`/`web.session`/`web.utils` → Step 2 thay: `formatFloat` từ `@web/core/utils/numbers`, `renderToString` từ `@web/core/utils/render`, `import { session } from "@web/session"`.
7. Advance v16 Python: `self.pool.cursor()` → `self.env.cr`; `eval(gridstack_config)` → `json.loads`; bundle key `web.assets_qweb` chết từ 17 → dồn vào `web.assets_backend`.
8. `patch()` Odoo 19: 2 arg + `super.x()` chuẩn JS (không `_super`, không named patch).
9. v18 pre-existing: `new BlockUI()` imperative + `complete: unblockUI` (undefined) + `self.call('crash_manager',...)` (service chết 17+) tại `ks_dashboard_ninja_new.js` ~:1234–1241 và ~:1313–1320 → `useService("ui")` block/unblock + `notification.add`.
10. `ks_dn_gridstack.scss` tồn tại trên disk nhưng v18 quên khai manifest → thêm vào.
11. Template strip AI logic NGƯỢC: dòng ~455–530 `t-if="...ks_ai_explain_dash"` = block AI → xóa; dòng ~69/~230 `t-if="!...ks_ai_explain_dash"` = nội dung THƯỜNG → giữ nội dung, gỡ wrapper.
12. ACL strip đủ **3 row**: `access_ks_dashboard_ninja_arti_int` + `access_ks_dashboard_ninja_ai_dashboard` + `access_ks_dashboard_ninja_fetch_key`.
13. `widgets/ks_ai_keyword/` gọi rpc model `arti_int` — glob widgets sẽ load nó → phải xóa dir khi strip.
14. Poppins CDN comment trong `common.scss` → fallback sans-serif nếu offline; xử ở step reskin.
15. Module MỚI trên prod KHÔNG tự cài qua auto-deploy — cần `-i` thủ công 1 lần (gotcha §6 compact summary).

### Gotchas phát hiện trong Step 1 (2026-07-16, áp cho Step 2–3)

16. **RC=0 NÓI DỐI**: `odoo-bin -i/-u --stop-after-init` với `logfile=` trong config exit 0 KỂ CẢ khi "Failed to initialize database"/CRITICAL. Verify gate = `: > logs/odoo.log` trước chạy + `grep -cE 'ERROR|CRITICAL'` sau chạy, KHÔNG tin RC.
17. **Rename sed ăn nhầm identifier**: token `ks_dashboard_ninja_<suffix>` (underscore) là FIELD/xmlid — global sed đổi nhầm `ks_dashboard_ninja_board_id`; revert bằng protect-list file-stems (new/items/templates/item_templates/view/item_view/demo/pro/item.css/.scss) rồi revert phần còn lại. Xmlid local-part TRÙNG model suffix (`id="ks_dashboard_ninja.item"`, `.board_defined_filters`) bị revert-model regex bắt nhầm → phải sửa tay 2 chỗ.
18. **Odoo 19 API đổi (đã đụng + fix trong core, advance/formula sẽ đụng lại)**: `from odoo.fields import datetime/date` chết (→ `datetime` module); `odoo.tools.misc.xlsxwriter` re-export chết (→ `import xlsxwriter`); `pycompat`/`ExportXlsxWriter`/`content_disposition` CÒN SỐNG (không cần sửa); `res.users.groups_id` → `group_ids` (explicit) / `all_group_ids` (implied — dùng trong ir.rule domain); `ir.ui.menu.groups_id` → `group_ids`; `res.groups.category_id` → `privilege_id` (chèn record `res.groups.privilege` trung gian, privilege giữ `category_id` → ir.module.category); `ir.actions.act_window` target `inline` chết → `current`; company service JS bị bỏ → `user.context` từ `@web/core/user` (đã gồm `allowed_company_ids`), `session.name` → `user.name`; `useLoadFieldInfo` → `useService("field").loadFieldInfo`; `useGetTreeDescription` → `useService("tree_processor").getDomainTreeDescription`; `treeFromDomain`/`domainFromTree` rời `condition_tree` → `tree_from_domain`/`domain_from_tree`.
19. **M2M monkey-patch Ksolves**: `fields.Many2many.read = ks_read` (re-implement API 18, `get_domain_list` chết ở 19) đầu độc MỌI M2M toàn registry ngay khi import module → viết lại thành wrapper: gọi `read` gốc rồi re-order cache (`self._insert_cache`) cho 4 field ordering của item. KHÔNG copy pattern cũ khi port advance.
20. **`--dev=reload` KHÔNG reload bytecode Python đang chạy** sau khi sed hàng loạt: server giữ code cũ trong RAM, traceback hiện source MỚI nhưng lỗi CŨ → restart server thật (`kill` + `scripts/start.sh`) trước khi verify browser.
21. **Audit import JS trước khi chạy browser**: script scan `import ... from "@web/..."` đối chiếu file + export symbol trong odoo19 source bắt được toàn bộ unmet dependency 1 lượt (đỡ N vòng browser).
22. `ks_fetch_dashboard_data` đọc `context['allowed_company_ids'][0]` không guard → crash shell/cron; đã fix fallback `env.company.id`. Pattern này có thể còn ở advance.

## §5 Module paths

- `wj_ks_dashboard_ninja`: `WujiaTea/custom/wj_ks_dashboard_ninja` (Step 1)
- `wj_ks_dn_advance`: `WujiaTea/custom/wj_ks_dn_advance` (Step 2)
- `wj_ks_dn_formula`: `WujiaTea/custom/wj_ks_dn_formula` (Step 3)
- v18 gốc (read-only, gitignored): `WujiaTea/ks_dashboard_ninja_v18/ks_dashboard_ninja`
- v16 gốc (read-only): `/home/huyban/odoo-dev/vietthuong/tools/{ks_dashboard_ninja,ks_dn_advance,ks_dn_formula}`
- Discovery reports (scratchpad session 2026-07-15, có thể đã mất): kết luận chính đã chép vào file này + plan file.

## §6 Kiến trúc port advance/formula (Step 2–3)

- **Python:** `_inherit` + `super()` chaining giữ nguyên — 12/13 hook method (ks_fetch_item_data, ks_export_item_data, _ksGetRecordCount, _ks_get_chart_data, _ksGetListViewData, _ksGetKpiData, ks_get_next_offset, ks_convert_into_proper_domain, get_list_view_record, ks_precision_digits, ks_fetch_dashboard_data, ks_create_item) còn nguyên trong v18 core (verified grep 2026-07-15).
- **JS advance:** `patch(Ksdashboardkpiview.prototype)` cho query-KPI; list layouts qua `t-inherit`; PDF qua `patch(KsDashboardNinja.prototype)` + `orm.call('ks_dashboard_ninja.board','ks_dashboard_send_mail',...)`.
- **JS formula:** 2 OWL component MỚI `components/ks_dashboard_formula_view/` + `ks_dashboard_pivot_view/` theo pattern components/ v18 + patch dispatch `KsDashboardNinja`; sum/grand-total qua `t-inherit`; controller export route `/wj_ks_dashboard_ninja/export/pivot_xls`.
