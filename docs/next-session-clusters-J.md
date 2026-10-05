# Cụm J — Branding cấu hình được · Tool dịch backend · Portal Vận hành nhượng quyền (lập 04/10/2026)

> Chủ dự án chốt 04/10: **3 việc này làm TRƯỚC Issue List** (15 Ready for Dev — cụm I trong `next-session-clusters-H.md`
> + 10 issue mới 156–167 chưa phân cụm — chờ tới sau ★JR-O). Thứ tự trong cụm: Branding → Dịch → Vận hành.
> Chi tiết Phần T + Phần O: §5 Phụ lục cuối file.

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
| J-T1 | `wujia_i18n`: danh mục chuỗi + màn sửa + quét | wujia_i18n (mới) | ☐ |
| J-T2 | Áp ngay (TranslationImporter overwrite) + tự áp lại sau `-u` | wujia_i18n | ☐ |
| J-T3 | Spike lớp phủ chuỗi Python/JS không restart (có đường lùi) | wujia_i18n | ☐ |
| J-T4 | Nhập/xuất CSV kiểu Thái + zip `.po`/`.pot`; script CLI gọi lại module | wujia_i18n, scripts | ☐ |
| J-O0 | Bảng đối chiếu CT-059…067 ↔ backend + danh sách màn + câu hỏi BA (0 code) | docs | ☐ |
| J-O1 | Luật portal ở L2 (file mới `portal_rules.py`, báo Thái) | franchise_operations (thêm file) | ☐ |
| J-O2 | Hub + Nhân viên + Lịch ca (chỉ đọc) | wujia_portal_operations (mới) | ☐ |
| J-O3 | Chi phí: danh sách + tạo nháp | portal_operations | ☐ |
| J-O4 | Doanh thu ngày: danh sách + khai nháp | portal_operations | ☐ |
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

