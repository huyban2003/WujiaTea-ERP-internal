# Cụm J — Branding cấu hình được · Tool dịch backend · Portal Vận hành nhượng quyền (lập 04/10/2026)

> Chủ dự án chốt 04/10: **3 việc này làm TRƯỚC Issue List** (15 Ready for Dev — cụm I trong `next-session-clusters-H.md`
> + 10 issue mới 156–167 chưa phân cụm — chờ tới sau ★JR-O). Thứ tự trong cụm: Branding → Dịch → Vận hành.
> Chi tiết Phần T + Phần O: §5 Phụ lục cuối file. **05/10: gộp còn 7 phiên** (T1+T2 gộp, bỏ T3, O3+O4 gộp).
> **05/10 (sau T1+T2): thêm Phần V — Việt hoá source (V0–V8 + ★VR), làm TRƯỚC J-T4** (chủ dự án: "ưu tiên xử lý trước").
> Thứ tự: V0 → V1…V8 → ★VR → J-T4 → J-O0…O4 → ★JR → Issue List. Tồn đọng toàn dự án: `docs/pending-backlog.md`.

## 0. Luật áp suốt cụm

- **Không sửa code đang có của Thái**: `wujia_franchise*` (gồm `wujia_franchise_operations`), `wujia_mobile_*`,
  `wujia_portal_inspection`, `wujia_fields_value`, `dynamic_dashboard_ai_nexgen`. Chỉ **thêm file mới** khi đã được phép (J-O1).
- ADR-027: `wujia_core` = L1; `wujia_i18n` = L1 platform (portal + backend + mobile cùng cần); `wujia_portal_operations` = L3b.
- Test luôn kèm `-u`. ⚠️ **KHÔNG `-u wujia_core --test-enable`** trên DB đủ module: test `wujia_franchise` của Thái import
  file đã xoá ⇒ registry chết. Test `wujia_core` chạy trên **DB trắng** `-i wujia_core --test-enable --test-tags /wujia_core`;
  DB copy đủ module chỉ `-u` không test.
- Log: `wujia_core` đổi logfile sang `<thư mục logfile>/<năm>/<tháng>/<ngày>.log` ⇒ chạy tay thì đặt `--logfile=<scratchpad>/x.log`
  rồi đọc `<scratchpad>/2026/10/*.log`.
- Dịch: code tiếng Anh, thêm dòng VN vào `docs/i18n-glossary.csv`, sinh `.po` + `.pot` bằng `scripts/sync_translations.py`.
  Script **ưu tiên glossary hơn bản dịch cũ** ⇒ so bằng babel trước/sau, trả lại dòng cũ bị đổi ngoài ý muốn.
- Không commit/push/deploy khi chưa có lệnh. Mỗi phiên ghi `docs/f-progress.md` + ✅ bảng §2.

## 1. Hiện trạng đã đo (04/10)

**Branding**: logo PC đã lấy `res.company.logo_web`, nhưng nhúng **base64 vào mọi trang** (3 chỗ) ⇒ HTML nặng; title `'Portal'`,
`<meta author="Cloudmedia">`, favicon (= `company.logo`; head auth ghi sai `t-attf-src` trên `<link>`) hardcode ở
`wujia_portal_layout/views/layouts.xml` (2 head), `login_page.xml`, `mobile_header.xml`. Màu `#28A9DF` + token ở
`_variables.css`; hex cứng thật còn ~10 dòng: `store_picker.css:179`, `portal_delivery.css:140-141`, `portal_exam.css:542`,
`_wujia_theme.css:212`, `_components.css:478/657/715`, `portal_order.css:693`, `portal_notification.css:185`
(còn lại là chú thích; `portal_report_charts.js:39` đã đọc CSS var).

**Dịch — vì sao "lâu lâu không ăn"** (`odoo19/odoo/tools/translate.py`): (1) `-u` mặc định không ghi đè bản dịch đã có;
(2) chuỗi Python/JS chỉ đọc từ file `.po`, cache RAM theo worker (`CodeTranslations` dòng 1813) ⇒ phải restart;
(3) thiếu `.pot`/sai dạng ref ⇒ bỏ qua im lặng (L16); (4) sửa câu trong template ⇒ term đổi ⇒ mất bản dịch.
Tool của Thái: glossary CSV `key,option,VN,CN,TH` (`custom/wujia_franchise/data/wujia_franchise_export.csv`) + controller
Khảo sát đọc `.po` lúc chạy (`wujia_franchise_inspection/controllers/main.py:81` `get_survey_translations`, so khớp
`_SmartTranslationDict` không phân biệt hoa thường/`&amp;`). Bản chuẩn hoá: `docs/i18n-glossary.csv` + `scripts/sync_translations.py`.

**Vận hành**: backend Thái `wujia_franchise_operations` 19.0.1.0.0 — 6 model `wujia.franchise.employee` ·
`.employee.assignment` (job_position, date_from/to, state) · `.shift.template` · `.work.schedule` (phẳng: 1 dòng = 1 NV × 1 ngày × 1 ca,
draft/confirmed/cancelled) · `.expense` (+category, draft/confirmed/cancelled) · `.revenue` (manual/import, 1 bản/ngày/cửa hàng);
2 nhóm User/Manager; ir.rule toàn cục `[(1,'=',1)]`; **không có liên kết nhân viên ↔ tài khoản portal**. Spec BA tab Model Field mục G
(`wujia.franchise.store.*`: lịch header/dòng, chấm công, nghỉ phép, `member_id`) **lệch** backend; tab Controller CT-059…067
("Vận hành nội bộ NQ") nhiều dòng "cần chốt"; tab FE-Portal chưa có màn nào; chưa có Figma.

## 2. Bảng trạng thái

| Phiên | Nội dung | Module | Trạng thái |
|---|---|---|---|
| J-B1 | Nguồn brand trong `wujia_core` (res.company + Settings + palette + route ảnh) | wujia_core | ✅ 04/10 — `de64704` |
| J-B2 | Áp brand vào portal (head, logo, CSS var) + backend (favicon, title tab) | portal_layout, core (+ ~7 CSS module màn) | ✅ 04/10 — chưa deploy |
| J-T1+T2 | `wujia_i18n`: danh mục chuỗi + màn sửa + quét + Áp dụng ngay + áp lại sau `-u` (gộp 05/10) | wujia_i18n (mới) | ✅ 05/10 — chưa commit |
| ~~J-T3~~ | ~~Lớp phủ chuỗi Python/JS không restart~~ — **bỏ** (chủ dự án 05/10: chuỗi code đổi ⇒ xuất `.po` + restart) | — | ✗ |
| J-V0 | Chốt quy ước + công cụ Việt hoá source (xem §6) + khách portal mặc định vi_VN + bật zh_CN | docs, scripts, i18n, portal_layout | ✅ 05/10 — chưa commit |
| **J-V1** | **Phiên kế.** `wujia_portal_layout` (259) + helper `wjMsg` + khối `#wj-msgs` + xoá `lang.js` chết | portal_layout | ☐ |
| J-V2 | `wujia_portal_base` (382) | portal_base | ☐ |
| J-V3 | `wujia_portal_exam` (345) + `wujia_exam` (63) | exam ×2 | ☐ |
| J-V4 | `wujia_portal_sale` (201) + `wujia_sale` (16) + `wujia_order_window` (8) | sale ×3 | ☐ |
| J-V5 | `wujia_portal_debt` (196) + `wujia_account` (4) | debt | ☐ |
| J-V6 | `wujia_portal_return` (168) + `wujia_return` (69) | return ×2 | ☐ |
| J-V7 | support (112+2) + knowledge (46+2) + notification (86+27) | 6 module | ☐ |
| J-V8 | purchase_history (99) + delivery (93+15) + info_request (85+7) + report (69) + fleet/core/metabase (21) | 9 module | ☐ |
| ★J-VR | Review Phần V: quét lại = 0 (code team), vi_VN 0 lệch chữ/ảnh, ảnh en/th, gửi danh sách 284 chuỗi cho Thái | — | ☐ |
| J-T4 | Nhập/xuất CSV kiểu Thái + zip `.po`/`.pot`; script CLI gọi lại module | wujia_i18n, scripts | ☐ |
| J-T5 | **Dịch tự động (DeepL)**: chọn ngôn ngữ (tự bật nếu chưa có) → dịch hàng loạt chuỗi chưa dịch → BA rà → Áp dụng (xem §6b) | wujia_i18n | ☐ |
| J-O0 | Bảng đối chiếu CT-059…067 ↔ backend + danh sách màn + câu hỏi BA (0 code) | docs | ☐ |
| J-O1 | Luật portal ở L2 (file mới `portal_rules.py`, báo Thái) | franchise_operations (thêm file) | ☐ |
| J-O2 | Hub + Nhân viên + Lịch ca (chỉ đọc) | wujia_portal_operations (mới) | ☐ |
| J-O3+O4 | Chi phí + Doanh thu ngày: danh sách + tạo/khai nháp (gộp 05/10) | portal_operations | ☐ |
| ★JR | Review: ma trận role × cửa hàng × route, ảnh, query, mutation, quét chuỗi mới vào tool dịch | — | ☐ |

## 3. Đã làm ở J-B1 (để B2 dùng)

- `wujia_core` **19.0.2.0.0**, depends thêm `web`. Field `res.company`: `wj_brand_name`, `wj_primary_color` (mặc định `#28A9DF`,
  chuẩn hoá in hoa, constraint `#RRGGBB`), `wj_logo_mobile`, `wj_favicon`, `wj_login_background`. Logo PC = `logo` sẵn có.
- Settings: tab **"Thương hiệu"** (`views/res_config_settings_views.xml`, related `company_id.*`).
- `res.company._wj_brand_info()` (ormcache theo công ty; `write` chạm field brand ⇒ `registry.clear_cache()`) trả
  `name, primary, palette, css, has_logo_mobile, has_favicon, has_login_background, version`.
  `_wj_brand_url(kind, width=0)` ⇒ `/wj/brand/<cid>/<kind>?v=<version>[&width=]`.
- `tools/brand_palette.py`: màu mặc định ⇒ **đúng bộ token BA, `css` rỗng** (0 pixel đổi); màu khác ⇒ sinh HSL (lệch bộ BA ≤4/kênh khi
  thử với #28A9DF), CTA làm đậm tới chữ trắng ≥4.5:1. Key = tên biến `--wujia-<key>`; thêm `primary-rgb` (`"40 169 223"`) cho
  `rgb(var(--wujia-primary-rgb) / .04)`.
- Route `/wj/brand/<cid>/<kind>` (`auth=public`, readonly): kind `logo | logo_mobile | favicon | login_background`; mobile/favicon
  trống ⇒ rơi về `logo`; `login_background` trống ⇒ 404 (trang tự dùng ảnh mặc định); width chỉ `0/32/64/180/192/512`;
  có `?v=` ⇒ `Cache-Control immutable`. ⚠️ Công ty **không có logo** ⇒ logo/favicon 404 — B2 phải chỉ in `<link>/<img>` khi có ảnh.
- Test `tests/test_brand.py` tag `wujia_brand`: 10 test, DB trắng 0 failed; mutation 5/5 đỏ đúng.
- `vi_VN.po` + `wujia_core.pot` (mới) sinh lại; 17 dòng VN mới trong glossary; nhãn Settings + lỗi Python đọc lại tiếng Việt OK.
- DB nháp: `wujia_b1` (copy `wujia_g5s`, đã `-u wujia_core`, bật vi_VN, admin/admin) · `wujia_b1t` (DB trắng test) — xoá được.

## 3b. Đã làm ở J-T1+T2 (05/10, để T4/JR dùng)

- `wujia_i18n` 19.0.1.0.0 (L1, depends `base`,`web`; app menu "Bản dịch", nhóm `group_wujia_translator`, admin implied).
- `wujia.i18n.term` (module, kind `model|model_terms|code_python|code_js`, name, res_id, src, `key_hash` md5, active) — khoá:
  chuỗi DB theo (kind, model,field, xmlid, src); chuỗi code theo (kind, src) vì Odoo tra code theo msgid/module.
  `_wj_scan(modules, langs)` = `TranslationModuleReader` mỗi ngôn ngữ 1 lượt; upsert, **không đè `override`**, term mất ⇒ archive.
- `wujia.i18n.value` (term × lang, value, state `synced|override|missing`, `pending`); sửa tay ⇒ override + pending.
  `action_apply` ⇒ `TranslationImporter._load` + `save(overwrite=True, force_overwrite=True)` + xoá cache `default` (+`templates`
  nếu view, +`stable` nếu nhãn field). Chuỗi code không áp (chờ T4 xuất `.po` + restart).
- `ir.module.module._update_translations` override ⇒ áp lại `override` của module vừa nạp (mọi `-u`, bật ngôn ngữ).
- `wujia.i18n.coverage` (SQL view) module × lang. Wizard quét: mặc định module `wujia_%`/`wj_%` × ngôn ngữ active ≠ en_US.
- Số đo DB copy (29 module × 3 ngôn ngữ): 4 839 term / 14 517 dòng, quét 3,1 s (lại 1,8 s) ⇒ chạy đồng bộ, không cần cron.
- ⚠️ Cho T4/JR: **90% câu gốc portal (1 384/1 533) viết cứng tiếng Việt**, module portal không có `i18n/` ⇒ độ phủ portal ≈0%
  ở cả 3 tiếng; vi_VN "chưa dịch" nhưng hiển thị đúng (câu gốc đã là VN). zh/th phải dịch từ câu VN. Cân nhắc ở T4: coi
  vi_VN = câu gốc khi src có dấu tiếng Việt (để độ phủ không báo sai).

## 4. Prompt từng phiên

Dán **sau `/wujia-start`**. Áp mọi phiên: `git pull` · đọc §0–§3 file này · đo trước/sau · ghi f-progress + ✅ §2.

### J-B2 — Áp brand vào portal + backend
```text
Làm phiên J-B2 (docs/next-session-clusters-J.md §3). Đọc §3 trước.
1. wujia_portal_layout: depends thêm wujia_core; layouts.xml 2 head: <title> = "<title> · <brand>", meta author = brand,
   favicon/apple-touch-icon href = company._wj_brand_url('favicon', 32/180) — CHỈ khi company có logo/favicon; sửa t-attf-src
   sai trên <link>; chèn <style> brand.css SAU asset_frontend khi css != ''.
2. Logo sidebar/navbar mobile/mobile_header/login: data: base64 → _wj_brand_url('logo'|'logo_mobile'); alt = brand.
   Login: nền dùng login_background nếu has_login_background, không thì ảnh cũ.
3. CSS: ~10 dòng hex cứng (§1) → var(--wujia-primary*) / rgb(var(--wujia-primary-rgb) / a). Bump version + ?v=.
4. Backend: favicon + title tab theo brand (inherit web.layout / patch title service), KHÔNG đụng MuK/mobile_core.
Nghiệm thu: wj_measure trước/sau 23 route × 5 khổ ở cấu hình mặc định = 0 lệch; đổi thử #E4572E + logo khác trên wujia_b1
⇒ ảnh PC/mobile/login đổi theo; HTML /portal nhẹ đi (đo byte); suite portal_layout + base 0 đỏ mới.
```

### J-T1 → J-T4, J-O0 → J-O4, ★JR
Nội dung từng phiên = dòng tương ứng ở bảng §2 + chi tiết ở §5 Phụ lục. Điểm phải hỏi chủ dự án khi tới:
- J-T3: nếu spike lớp phủ Python/JS không ổn trên Windows/nhiều worker ⇒ báo, dùng đường lùi (xuất `.po` + restart).
- J-O1: xin phép **thêm file** `wujia_franchise_operations/models/portal_rules.py` + báo Thái trước khi code.
- J-O0: gửi BA câu hỏi chấm công / nghỉ phép / duyệt ca / Staff thấy gì / gắn nhân viên ↔ member — không tự quyết.
- Portal Vận hành dùng luật **một cửa hàng đang chọn** (`get_active_franchise_id()`, không fallback mọi cửa hàng) + **role tại
  cửa hàng đó** (`get_max_role_in_franchises((fid,))`) — đúng hướng #152/#153; chỉ Owner/Manager; Staff ⇒ trang không quyền.

---

## 5. Phụ lục — plan chi tiết (chép nguyên từ phiên lập 04/10)

## Phần T — Tool dịch trong backend, module mới `wujia_i18n` (4 phiên)

Tầng L1 platform (ADR-027 cho phép vì portal + backend + mobile đều cần). Depends `base`, `web`. Nhóm quyền `group_wujia_translator` (sửa) + admin.

**T1 — Danh mục chuỗi + màn sửa**
- `wujia.i18n.term`: `module`, `kind` (`model` · `model_terms` · `code_python` · `code_js`), `name` (ref kiểu `model_terms:ir.ui.view,arch_db:<xmlid>`), `res_id`, `src`. Unique (`module`,`name`,`res_id`,`src`).
- `wujia.i18n.value`: `term_id`, `lang`, `value`, `state` (`synced` · `override` · `missing`). Unique (`term_id`,`lang`), index (`lang`,`state`).
- Wizard **"Quét chuỗi"**: chọn module + ngôn ngữ, dùng `odoo.tools.translate.TranslationModuleReader(cr, modules, lang)`, đúng nguồn mà lệnh export `.pot` đang dùng (kế thừa thiết kế của Thái trong `sync_translations.py`). Chỉ upsert, không xoá bản sửa tay.
- Màn danh sách sửa tại chỗ, mỗi dòng là term × ngôn ngữ (giống `ir.translation` v13). Lọc: module, ngôn ngữ, "Chưa dịch", "Đã sửa tay", theo loại. Có form một term, các ngôn ngữ đặt cạnh nhau. Có bảng độ phủ % theo module × ngôn ngữ.
- Chuẩn hoá khi so khớp: dùng lại ý `_SmartTranslationDict` của Thái (`&amp;`/`&`, khoảng trắng) để nhận đúng term QWeb có thẻ HTML.

**T2 — Áp ngay + bền qua `-u`**
- Nút **"Áp dụng"**: `kind` = `model`/`model_terms` thì ghi qua `TranslationImporter.load_rows` → `save(overwrite=True, force_overwrite=True)`, là đúng đường Odoo import `.po`, rồi xoá cache `templates`. Hiệu lực ngay, không restart.
- Bền qua `-u`: override `ir.module.module._update_translations` (kiểm signature trong `odoo19/odoo/addons/base/models/ir_module.py` khi code): gọi super xong thì **áp lại** mọi `state=override` của các module vừa nạp. Đây là cách xử lý gốc của chuyện "lâu lâu không ăn".

**T3 — Lớp phủ chuỗi Python/JS (spike trước, có đường lùi)**
- Tool ghi bản sửa của chuỗi code ra file `.po` sinh tự động trong `data_dir/wujia_i18n/<db>/<module>/<lang>.po`. Thêm `post_load` hook nối đường dẫn này vào `odoo.tools.translate.get_po_paths`, để Odoo tự đọc bằng chính bộ lọc `#. odoo-python` / `odoo-javascript` của nó.
- Lưu xong thì xoá `code_translations.python_translations/web_translations` ở worker hiện tại và `registry.clear_cache()` để báo các worker khác. Patch `Registry` khi nhận tín hiệu cũng xoá 2 dict đó. Đổi hash `/web/webclient/translations` để trình duyệt tải lại.
- Đường lùi nếu spike không ổn trên Windows/nhiều worker: chuỗi code vẫn đi bằng nút xuất `.po` (T4) + restart, ghi rõ vào màn hình.

**T4 — Nhập/xuất**
- Nhập CSV glossary đúng định dạng của Thái (`key,option,VN,CN,TH`; `option` = ref). Khớp theo (ref, src), không có thì khớp theo src. Nạp được ngay `docs/i18n-glossary.csv` + `custom/wujia_franchise/data/wujia_franchise_export.csv`.
- Xuất: CSV cùng định dạng + **zip `.po` + `.pot` từng module** để dev commit vào source (L16: bản dịch chỉ nằm trong DB thì dựng lại DB là mất). Phần ghi `.po` tách từ `scripts/sync_translations.py` thành `wujia_i18n/tools/po_writer.py`: babel, `.pot` sinh cùng lượt, có `#. odoo-python`, dạng ref menu `model:ir.ui.menu,name:`. Script CLI gọi lại chính module này để khỏi có hai bản.
- Nghiệm thu: sửa 1 chuỗi QWeb portal + 1 nhãn field + 1 chuỗi `_()` + 1 chuỗi JS ở `zh_CN`. Mở màn đúng ngôn ngữ thấy đổi **không restart** (T3 đạt) hoặc sau restart (đường lùi). Chạy `-u` module đó thì bản sửa vẫn còn. Đọc chỉ-đọc qua XML-RPC `context={'lang':…}` theo L16.

Ngoài phạm vi (ghi lại để khỏi mở lại): các hằng nhãn portal đang để cứng tiếng Việt (`ROLE_LABELS`, `RETURN_STATUS_LABELS`, `SALE_STATE_META`) thì tool không dịch được. Chuyển sang `_lt()` là một đợt riêng, sau T4.

---

## Phần O — Portal Vận hành, module mới `wujia_portal_operations` (4–5 phiên)

L3b, depends `wujia_portal_base` + `wujia_franchise_operations`. Chia theo **chức năng** (ADR-027 addendum). Không model nghiệp vụ.

**O0 — Bảng đối chiếu + màn (0 code)**: `docs/operations-portal-spec.md` gồm CT-059…067 ↔ model/field thật của Thái, danh sách màn PC + mobile dựng từ component chuẩn (`portal-component-standard.pdf`: PageHeader, FilterBar, DataList/ListCard, StatusBadge, EmptyState, Pagination) và câu hỏi gửi BA (chấm công, nghỉ phép, duyệt ca, Staff có thấy gì không, gắn nhân viên ↔ member). Chưa có Figma thì bám chuẩn component.

**O1 — Luật portal ở L2** (thêm **file mới** `wujia_franchise_operations/models/portal_rules.py`, không sửa file cũ của Thái; báo Thái): `_portal_scope_domain(franchise_id)`, `_portal_can_manage(role)`, `_portal_week_schedule(fid, week)` (1 `search_read` + 1 `_read_group`), `create_from_portal` cho chi phí + doanh thu (luôn `draft`, có savepoint, trả mã lỗi form; dùng constraint có sẵn như doanh thu một bản/ngày), KPI tháng bằng `_read_group`. Test model.
- Luật phạm vi theo hướng #152/#153 ngay từ đầu: **một cửa hàng đang chọn** (`get_active_franchise_id()`, không dùng fallback "mọi cửa hàng") + **role tại cửa hàng đó** (`get_max_role_in_franchises((fid,))`). Chỉ Owner/Manager. Staff thấy trang "Không có quyền xem" như Công nợ. Chưa chọn cửa hàng thì hiện EmptyState "Chọn cửa hàng".

**O2 — Hub + Nhân viên + Lịch ca (chỉ đọc)**: `/portal/operations` có 4 KPI (NV đang làm · ca tuần này · chi phí tháng · doanh thu tháng) và lối vào các màn. `/portal/operations/employees` là danh sách + chi tiết, lọc theo vị trí/trạng thái. `/portal/operations/schedule` xem theo tuần (PC bảng ngày × ca, mobile thẻ theo ngày). Mục nav sidebar PC + sheet "Thêm" mobile chỉ hiện khi đủ role.

**O3 — Chi phí**: `/portal/operations/expenses` gồm danh sách (lọc tháng/loại/trạng thái, nhãn trạng thái một nguồn) + form tạo nháp + chi tiết. HQ xác nhận ở backend.

**O4 — Doanh thu ngày**: `/portal/operations/revenue` gồm danh sách + khai doanh thu ngày (nháp, chặn trùng ngày, thông báo tiếng Việt).

**★OR — Review**: ma trận role × cửa hàng × route bằng máy (truy cập ID cửa hàng khác thì 404), ảnh PC/mobile, `check_layers.py` 0 vi phạm, đếm query mỗi trang (danh sách ≤ hằng số, không N+1), mutation cho luật scope/role. Chuỗi mới quét vào tool dịch (Phần T).

---


---

## 6. Phần V — Việt hoá source (lập 05/10, ưu tiên trước J-T4)

**Vì sao**: quét `scripts/qa/vn_hardcode_scan.py` ra **2 659 chuỗi tiếng Việt viết cứng** (code team ≈ 2 375, Thái 284) + 945 trong
test — chi tiết `docs/vn-hardcode-inventory.{md,csv}`. Odoo chỉ dịch khi câu gốc là tiếng Anh ⇒ portal EN/ZH/TH vẫn hiện tiếng
Việt dù có tool dịch. Tool `wujia_i18n` (T1+T2) đã sẵn để kiểm độ phủ sau mỗi phiên V.

**Quy ước mỗi phiên V1–V8** (chốt ở V0):
1. Câu gốc trong QWeb/Python/JS → tiếng Anh (ngắn, rõ; không dịch máy câu dài — giữ nghĩa nghiệp vụ).
2. Dòng glossary `key=<EN>, VN=<câu cũ>` ⇒ `sync_translations.py` sinh `vi_VN.po` + `.pot` ⇒ **user vi_VN thấy y như cũ**.
3. Hằng nhãn Python (`ROLE_LABELS`, `RETURN_STATUS_LABELS`, `SALE_STATE_META`…) → `_lt()`; thông báo controller → `_()`.
4. Câu trong biểu thức `t-out="… or 'Chưa có'"` → tách `<t t-set>` (dịch được) hoặc truyền từ controller.
5. Test assert theo nhãn VN: chạy với `lang=vi_VN` (có `.po`) hoặc assert theo key; không xoá assert.
6. Nghiệm thu: quét lại module = 0 · probe text 26 route × vi_VN **0 lệch chữ** + ảnh 0 lệch · en_US/th_TH chụp ảnh không vỡ
   layout (câu tiếng Anh/Thái dài hơn) · suite module 0 đỏ mới · độ phủ trong app "Bản dịch" vi_VN ≈100%.

**J-V0 — ✅ 05/10: quy ước đã chốt + công cụ** (chủ dự án trả lời 4 câu):

| # | Câu | Chốt |
|---|---|---|
| a | JS portal (Vuexy, không có `_t`) dịch bằng gì | Chuỗi đi từ QWeb sang JS qua `data-wj-msg-*` ⇒ dịch bằng `.po` như QWeb |
| b | User `en_US` | EN thấy EN, VN thấy VN. **Mặc định vi_VN**: user portal mới (đã có, `portal_base/res_users.py`) + **khách chưa đăng nhập trên `/portal`** (mới, không theo ngôn ngữ trình duyệt). Không đổi user đã chọn en_US |
| c | Ngôn ngữ | **Bật hết** vi/en/th/**zh_CN** (`wujia_i18n` tự bật lúc `-i`); thêm ngôn ngữ ở Settings là bộ chọn portal có ngay cho mọi người (WJ-LANG-001) |
| d | BA duyệt câu EN? | **Không.** EN do dev đặt; ZH/TH dịch bằng DeepL (J-T5). Câu cần sửa gom **1 danh sách gửi BA 1 lần ở ★VR** |

**Quy ước JS (a)** — Odoo 19 chỉ dịch attribute trong `TRANSLATED_ATTRS` (`odoo/tools/translate.py:74`: `title`, `placeholder`,
`aria-label`, `alt`, `data-tooltip`…); `data-*` tuỳ ý **không** dịch. Vì vậy câu đặt trong text node `<t t-set>` (dịch được, như mẫu
`wj_txt` của J-B2) rồi gắn vào attribute:
```xml
<t t-set="wj_msg_upload_failed">Upload failed. Please try again.</t>
<form class="wj-avatar-form" t-att-data-wj-msg-upload-failed="wj_msg_upload_failed"> … </form>
```
```js
// helper đặt ở wujia_portal_layout (làm ở V1): tìm attr gần nhất từ el lên tổ tiên, rồi khối chung #wj-msgs, cuối cùng fallback.
wjMsg(el, 'upload-failed', 'Upload failed. Please try again.')
```
Câu dùng chung nhiều màn (lỗi mạng, "Có lỗi xảy ra") đặt 1 lần trong `<div id="wj-msgs" hidden …>` ở layout. Fallback trong JS là
câu tiếng Anh (không còn tiếng Việt trong `.js`).

**Công cụ (V0)** — quy trình 1 phiên V: `scripts/qa/README.md` §Phần V.
- `vn_hardcode_scan.py --module X --fail-on-any` ⇒ exit 1 khi còn chuỗi (trừ test).
- `vn_to_en_pairs.py draft|check|apply --module X` ⇒ `docs/i18n-pairs/X.csv` (cột `en` lấy sẵn từ glossary nếu VN đã có); `check`
  bắt EN trống, còn dấu tiếng Việt, placeholder/thẻ lệch, 1 EN cho nhiều VN (msgid trùng = 1 bản dịch), đụng glossary; `apply` thay
  QWeb text/attr dịch được + `_()`/`string=`, thêm glossary, in danh sách sửa tay. Chạy thử V0 trên bản copy `wujia_portal_layout`:
  thay 204/205 (1 chuỗi Python nối nhiều literal ⇒ sửa tay), XML/Python hợp lệ, phần còn lại đúng nhóm sửa tay (JS 30 · `t-*` 17 ·
  hằng Python 4 · attr không dịch 3).
- `wj_text_probe.py` ⇒ mọi text node (cả modal ẩn) + attr dịch được + `data-wj-msg-*`, số che `#`; 52 trang (21 route + 4 chi tiết +
  login khách × 1440/390). Mốc vi_VN trên DB `wujia_t1`: `docs/i18n-baseline/vi_VN.json` (2 lần đo 0/52 lệch).
- `docs/i18n-pairs/wujia_portal_layout.csv` đã draft (259 dòng: auto 205 · sửa tay 54) cho V1.

## 6b. J-T5 — Dịch tự động (chủ dự án 05/10: "chọn ngôn ngữ rồi dịch add ào")

Mục tiêu: thêm ngôn ngữ mới = chọn ngôn ngữ → bấm dịch → rà → Áp dụng, không cần dev. Làm sau J-T4 (câu nguồn EN sạch sau Phần V
thì dịch máy mới chuẩn; chuỗi code dịch xong vẫn đi đường xuất `.po` + restart của J-T4).
- **Nhà cung cấp cắm được**: lớp provider chung, DeepL trước; API key + gói (Free/Pro) trong Settings (`ir.config_parameter`,
  chỉ admin). Ngôn ngữ DeepL không hỗ trợ ⇒ báo rõ trên wizard (kiểm danh sách ngôn ngữ DeepL lúc code), chừa chỗ provider khác.
- **Wizard**: chọn ngôn ngữ đích (chưa active ⇒ bật + quét), module, phạm vi (chỉ "Chưa dịch" / cả "Đã dịch" chưa sửa tay);
  ước số ký tự trước khi gửi; chạy nền theo lô (cron + `_trigger`), không treo request.
- **Giữ nguyên định dạng**: `%s`, `%(x)s`, `{x}`, thẻ HTML/QWeb (`tag_handling=xml`), khoảng trắng đầu/cuối; kiểm lại sau dịch,
  lệch placeholder ⇒ không nhận, đánh dấu lỗi.
- **Glossary thuật ngữ** (trà sữa, nhượng quyền, tên sản phẩm) gửi kèm DeepL glossary; không bao giờ đè bản `override`.
- **Trạng thái mới `machine`** (dịch máy, chờ rà): lọc riêng, BA/người bản xứ duyệt ⇒ `synced`/`override` rồi Áp dụng; độ phủ
  tách "dịch máy" với "đã duyệt".
- Câu hỏi chủ dự án/BA: tài khoản DeepL (Free 500k ký tự/tháng hay Pro — kiểm hạn mức lúc code), đồng ý gửi chuỗi giao diện ra
  DeepL, ai rà từng ngôn ngữ.

**Code của Thái** (`wujia_portal_inspection` 178 · `wujia_franchise_inspection` 94 · `wujia_franchise` 7 · `_contract` 3 ·
`_operations` 2): KHÔNG sửa; ★VR gửi Thái danh sách (lọc CSV cột `owner=Thái`).
