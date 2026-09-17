# Cụm F — Chuẩn hoá kiến trúc portal trước khi fix tiếp Issue List (lập 17/09/2026)

> **Issue List TẠM DỪNG** theo chốt chủ dự án 17/09: *"chuẩn hoá gấp hơn, làm xong mới fix issue
> chuẩn component được"*. Các lượt E còn dở (E4b, E4c, E5–E8) chờ tới khi qua **cổng F** (F0–F5).
> Cơ sở kiến trúc: ADR-027 (`docs/adr-027-module-layering.pdf`, chapter 74).
> HEAD lúc lập: `4896ac1` (đã pull 8 commit anh Thái, có `wujia_mobile_core`).

## 0. Phạm vi — chỉ code của mình

**KHÔNG đụng** (code anh Thái): `wujia_franchise`, `wujia_franchise_contract`,
`wujia_franchise_inspection`, `wujia_franchise_operations`, `wujia_portal_inspection`,
`wujia_mobile_core`, `wujia_mobile_franchise`, `wujia_mobile_franchise_inspection`, `wujia_mobile_sale`. Chỗ nào chuẩn hoá chạm tới phần dùng chung với nhóm Khảo sát
(vd class `wj-inspection-pc`, selector dùng chung) ⇒ **thu hẹp selector, không xoá; không chắc thì
dừng hỏi chủ dự án**.

Luật chung kế thừa nguyên văn: luật refactor `docs/refactor-plan.md` §"LUẬT BẤT DI BẤT DỊCH"
(tra ledger trước khi đụng, đo trước–sau bằng máy) + 9 luật chung lứa E
(`docs/next-session-clusters-E.md` §"Luật chung").

---

## 1. Kết quả review (17/09) — đo trên HEAD `4896ac1`

Chuẩn mong muốn: **nghiệp vụ** (model, menu backend, quyền, sequence, luật) → **portal nghiệp vụ**
(controller mỏng + QWeb + CSS/JS của màn) → **`portal_layout`** (khung Vuexy + component dùng chung,
không biết màn nào của Wujia).

### A. Chia vai trò module

| # | Vấn đề | Số đo | Mức | Xử lý ở |
|---|---|---|---|---|
| A1 | 7 module `portal_*` ôm nghiệp vụ backend | order_window 1 model/2 menu/**0 route** · info_request 1/1 · knowledge 4/4 · support 3/4 · notification 3/4/2 group · exam 5/7/2 group/3 seq · return 6 model/1.101 dòng/6 menu/2 group | Cao | F7–F13 |
| A2 | Bảng map trạng thái → badge của mọi phân hệ nằm ở `portal_base/controllers/utils.py:440–520` | 5 bảng, 43 file import | Thấp | gộp F8–F13 |
| A3 | `portal_layout` biết màn Wujia | `pc_sidenav.xml` 10 link cứng, `mobile_bottomnav.xml` 11, `mobile_header.xml` 7 · 9/10 test layout gọi template module khác · `redirects.py` giữ route return/exam/purchase_history | TB | F5 |
| — | **Đúng chuẩn** | 5 module nghiệp vụ của mình sạch; `portal_base/debt/delivery/purchase_history/report/sale` thuần kênh; `portal_layout` depend `base, web, auth_signup` | | |

### B. Component chuẩn hoá

| # | Vấn đề | Số đo | Mức | Xử lý ở |
|---|---|---|---|---|
| B1 | **CSS của từng màn nằm trong `portal_layout`** | 380 nhóm class, **193** là của 1 màn (Đặt hàng 78 · Home/KPI 49 · Kiến thức 23 · Lịch sử 19 · Hỗ trợ 7 · Khảo sát 4 (Thái) · debt/exam/return 3 · delivery/notification 2) — đếm F0 bằng `css_owner.py`; 54 nhóm định nghĩa ở **cả** layout lẫn module | Cao | F2, F3 |
| B2 | Module viết đè component chung, loại **đổi dáng** | exam 15 · debt 9 · notification 6 · sale 4 · delivery 3 · return 3 · report 1 = **41 rule** (Phụ lục B, đếm F0) | TB | F4 |
| B3 | Component chưa có template, viết class tay | EmptyState ~124 · `wj-pc-btn` ~64 | Đúng tiến độ | E5–E8 + cụm EmptyState (sau cổng) |
| — | **Đúng chuẩn** | PageHeader 24 file · CardHeader 19 · SurfaceCard 18 · DataList 11 · Pagination 11 · SectionHeader 8 · FilterBar 2 (E4a) | | |

### C. Controller (89 route, 13 module của mình)

Luật: **controller chỉ tiếp khách** (parse, xác định cửa hàng, gọi method, render/redirect).
Luật nghiệp vụ, chuyển trạng thái, tạo record kèm hệ quả ⇒ method trên model. Phép thử: *HQ làm
cùng thao tác trên backend/mobile/cron thì logic phải ở model*.

**C1 — An toàn / độ bền (vá nhanh, F1)**

| Chỗ | Lỗi | Hậu quả |
|---|---|---|
| `portal_support/controllers/portal.py:93–94` | `int(post.get(...))` không bọc try | Gửi `franchise_id=abc` ⇒ 500 |
| `portal_support/controllers/portal.py:94,117` | `category_id` không kiểm tồn tại/active | Tạo ticket với danh mục rác qua `sudo()` |
| `portal_support/controllers/portal.py:120–131` | Tự `ir.attachment.sudo().create` — **không kiểm MIME, dung lượng, số file** (mọi màn khác dùng `attach_files_to_record`) | Upload được file bất kỳ (html/svg/exe), không giới hạn |
| `portal_base/controllers/portal.py:406` | `redirect.startswith('/')` cho qua `//evil.com` | Open redirect sau khi đổi cửa hàng (layout `set_lang:236` đã kiểm `netloc` đúng — tái dùng) |
| `portal_info_request/controllers/portal.py:131–133` | `except Exception as e` → `error=str(e)` | Lộ thông báo lỗi nội bộ (SQL/traceback text) ra portal |
| `portal_info_request/controllers/portal.py:185`, `portal_layout/controllers/portal.py:120` | Ghép `str(e)` thẳng vào query string, không encode | Thông báo vỡ khi có ký tự `&`,`#`; |

**C2 — Controller đi tắt qua workflow của model (F1)**

| Chỗ | Đang làm | Model đã có | Hậu quả |
|---|---|---|---|
| `portal_return/controllers/portal.py:212` | `rr.sudo().write({'state': 'submitted'})` | `wujia.return.request.action_submit()` (`models/wujia_return_request.py:263`) kiểm ≥ảnh + `message_post` | Phiếu gửi từ portal **không có dòng chatter "Yêu cầu đã được gửi"**; luật ≥ảnh viết 2 nơi |
| `portal_sale/controllers/portal.py:950` | `old_quotations.write({'state': 'cancel'})` (cố ý tránh cascade) + `cr.rollback()` `:959` | — | Luật "1 cửa hàng 1 báo giá portal" (POR-022) chỉ sống trong controller → F6 |

**C3 — Luật nghiệp vụ nằm trong controller (F6, F8–F13)**

| Module | Luật đang ở controller | Đích |
|---|---|---|
| `portal_sale` | Luật số lượng min/bước/max viết **3 lần** (`:584–602`, `:675–686`, `:739`) + trùng constraint `wujia_sale/models/sale_order_line.py:84` · SQL upsert/step giỏ (`:612`, `:750`) · submit 130 dòng (`:841–970`): khoá giỏ, khung giờ, huỷ báo giá cũ, tạo SO, xoá giỏ | `product._portal_qty_error(qty)` 1 nguồn · `wujia.portal.cart.line._add/_step` · `wujia.portal.cart.action_submit_order()` (F6) |
| `portal_return` | Đơn hợp lệ trong 10 ngày `:293`, cấu hình bù `:306`, số/dung lượng minh chứng `:370`, parse → vals `:495–580` | `wujia.return.request._portal_eligible_order_domain()`, `create_from_portal()` (F13b) |
| `portal_exam` | Kiểm session published, tối đa người/phiếu, create + flush savepoint `:426–475` | `wujia.exam.registration.register_from_portal()` (F12b) |
| `portal_info_request` | Gate Owner/Manager, create + đính kèm + submit `:108–152` | `create_from_portal()` (F8) |
| `portal_notification` | Ghi "đã đọc" lặp **3 lần** (detail `:256`, mark-all `:312`, mark-read `:342`) | `wujia.notification.read._mark_read(user, fid, notis, opened)` (F11) |
| `portal_support` | create ticket + đính kèm `:92–133` | `create_from_portal()` (F10) |

**C4 — Mẫu hệ thống, ghi nhận, CHƯA sửa:** mọi route dùng `sudo()` + tự lọc `franchise_id in accessible`
(record rule portal có nhưng bị bỏ qua). Đúng hiện tại (đã soi 23/08, fail-closed nhất quán), nhưng
route mới quên lọc là lộ dữ liệu ⇒ khi tách phân hệ, đưa domain phạm vi vào model
(`_portal_scope_domain(fids)`) để controller gọi 1 chỗ.

**Controller đã tốt:** debt, delivery, purchase_history (`_get_scoped_order`), report, knowledge
(tăng view qua `action_increment_view`), exam photo (lọc theo cửa hàng), sale submitted (guard đúng
store), 0 `csrf=False`, rate-limit ở cart add/note.

### D. Phát hiện ngoài phạm vi — ✅ ĐÃ GIẢI (anh Thái, merge `c80a6e2`, xác nhận phiên F1 17/09)

Trước: commit anh Thái 17/09 (`67c42a0`…`4896ac1`) cho `wujia_franchise`, `wujia_franchise_inspection`,
`wujia_sale` depend `wujia_mobile_core` + `sale.order` kế thừa `wujia.mobile.mixin` — ngược ADR-027.

Nay (đọc manifest HEAD): 3 module nghiệp vụ **không còn** depend `wujia_mobile_core`; mixin/field mobile gỡ khỏi
`wujia_sale/models/sale_order.py`; view mobile dời sang 3 module ghép mới `wujia_mobile_franchise`
(franchise + mobile_core) · `wujia_mobile_franchise_inspection` · `wujia_mobile_sale` (sale, wujia_sale, mobile_core).
`wujia_mobile_core` depend `base, web`. `check_layers.py`: 4 → **1** vi phạm (chỉ còn `portal_order_window` R4, xử lý F7).

Còn lệch nhỏ, chỉ báo anh Thái (không chặn F7):
- 3 module `wujia_mobile_*` đang `auto_install: False` — ADR-027 đề xuất `True` để tự cài khi đủ nghiệp vụ + khung.
- `wujia_franchise/tests/__init__.py` còn `from . import test_wujia_franchise_mobile` (file đã xoá) ⇒ chạy test không
  `-u` chết import. Mọi phiên F chạy test phải kèm `-u` module cần test.

---

## 2. Lộ trình

```
CỔNG F (bắt buộc trước khi mở lại Issue List)
  F0 Công cụ + mốc đo ─► F1 Controller vá an toàn ─► F2 CSS màn nhỏ ─► F3 CSS Đặt hàng + Home
  ─► F4 Duyệt 41 rule đè ─► ★FR-B review khối B ─► F5 Khung thuần ─► ★FR-A3 review cổng
                                   │
                                   ▼
  MỞ LẠI ISSUE LIST: E4b → E4c → E5 → E6a/b → E7a/b → E8 (+ đề xuất BA cụm EmptyState)

NHÁNH SAU CỔNG (xen kẽ Issue, ~1 phiên/tuần; mục D đã giải 17/09 — F7 không còn bị chặn)
  F6 Sale controller mỏng
  F7 pilot order_window → ★FR-P review pilot
  → F8 info_request → F9 knowledge → F10 support → F11 announcement → F12a/b exam → F13a/b return
  → ★FR-A review toàn khối A + controller
```

**★ Phiên review (chốt chủ dự án 17/09):** xong mỗi khối A hoặc B phải có **một phiên review lại
toàn bộ** khối đó trước khi đi tiếp — không làm tính năng, chỉ soi lại bằng máy + ảnh, sửa lỗi sót
nhỏ, ghi nợ còn lại. Tiền lệ: phiên review toàn cụm D3 bằng ảnh chụp (04/09) bắt được lỗi mà số đo
từng lượt đều Pass.

**Vì sao cổng là F0–F5:** đó là những gì các cụm E5–E8 đụng trực tiếp (CSS layout, override
component, sidebar/menu). Làm E trước thì mỗi cụm lại sửa 2 nơi và phải dọn lại lần nữa.
F6–F13 là backend/controller — không chặn component, nhưng chặn mobile và tách repo.

| Phiên | Nội dung | Module `-u` | Rủi ro | Trạng thái |
|---|---|---|---|---|
| F0 | Script đo sở hữu CSS + check tầng + mốc ảnh/B4 | 0 | Thấp | ✅ 17/09 |
| F1 | C1 + C2(return) | support, base, info_request, layout, return | Thấp | ✅ 17/09 |
| F2 | CSS 8 màn nhỏ ra khỏi layout (62 nhóm) | layout, knowledge, purchase_history, support, notification | Thấp | ✅ 17/09 |
| F3 | CSS Đặt hàng (55) + Home/KPI (56) | layout, sale, base | TB | ☐ |
| F4 | Duyệt 41 rule đổi dáng (dừng giữa phiên xin duyệt) | layout + 7 module | TB | ☐ |
| **FR-B** | **Review toàn khối B (F2–F4)** | 0 hoặc vá nhỏ | — | ☐ |
| F5 | Menu đăng ký theo module, test layout dùng fixture, redirect về module | layout + ~12 module | TB | ☐ |
| **FR-A3** | **Review cổng F (F0–F5) → quyết mở lại Issue List** | 0 hoặc vá nhỏ | — | ☐ |
| F6 | Sale: luật số lượng 1 nguồn, giỏ + submit về model | sale, wujia_sale | Cao | ☐ |
| F7 | Pilot tách order_window | order_window, portal_sale | Cao | ☐ |
| **FR-P** | **Review pilot trước khi nhân quy trình** | 0 | — | ☐ |
| F8–F13 | Tách phân hệ + controller mỏng | theo phân hệ | Cao | ☐ |
| **FR-A** | **Review toàn khối A + controller (F1, F6–F13)** | 0 hoặc vá nhỏ | — | ☐ |

---

## 3. Prompt từng phiên

Mỗi phiên: dán **sau `/wujia-start`**. Nhắc lại cho mọi phiên: *Issue List đang tạm dừng — bỏ qua
Step 2b đề xuất issue; không đụng module anh Thái (§0); code ít, comment ≤1 dòng; chưa được yêu cầu
thì không commit/push/deploy.*

**Kết thúc MỌI phiên (kể cả dừng giữa chừng):** thêm 1 mục vào `docs/f-progress.md` theo mẫu
(kết quả, commit, số đo, nợ, phiên kế) + đánh ✅/◐ bảng §2. Prompt F1–F13 không nhắc lại nhưng vẫn áp dụng.

### Prompt F0 — Công cụ đo + mốc trước chuẩn hoá

```text
Làm phiên F0 cụm chuẩn hoá (docs/next-session-clusters-F.md). Issue List đang tạm dừng.
Đọc trước: docs/next-session-clusters-F.md §0–§2, scripts/qa/README.md, docs/refactor-plan.md §LUẬT.

Mục tiêu: có công cụ + mốc đo để F1–F5 chứng minh "trước = sau" bằng máy.
1. scripts/qa/css_owner.py (thay heuristic scratchpad):
   --layout-domain: liệt kê nhóm class (gốc BEM) trong wujia_portal_layout/static/assets/css/_*.css
   kèm file:dòng, gắn module ứng viên theo map tên; đánh dấu class ĐÃ dùng ở ≥2 module portal
   (đếm bằng lxml trên views/*.xml, không grep trần) ⇒ đó là component, GIỮ ở layout.
   --overrides: rule trong module portal chạm component chung, tách "chỉ bố cục" / "đổi dáng".
   Kiểm chứng: số ra phải khớp Phụ lục A/B (±, lệch thì sửa doc, ghi lý do).
2. scripts/qa/check_layers.py: đọc __manifest__.py, báo vi phạm luật ADR-027 (nghiệp vụ depend
   khung/ghép, khung depend nghiệp vụ, portal_* ↔ mobile_*, portal_* không depend portal_base).
   Chế độ report-only, exit 0; in rõ vi phạm hiện có (kể cả của anh Thái — chỉ báo, không sửa).
3. Mốc đo trên DB copy giống UAT (có cài inspection, luật E #1), port riêng:
   wj_measure.py --portal-login <tài khoản có dữ liệu> --screenshots → scratchpad/f0-before/
   + b4_regression.py + test các module portal. Ghi lệnh + số vào docs/f0-baseline.md.
Nghiệm thu: 2 script chạy được, khớp Phụ lục ±; baseline có mẫu khác 0 ở mọi route.
Dừng hỏi nếu: DB copy không dựng được, hoặc số lệch Phụ lục >10%.
Cuối phiên: ghi mục vào docs/f-progress.md (theo mẫu) + ✅ bảng Trạng thái §2 + compact summary §5.
```

### Prompt F1 — Controller: vá an toàn + gọi đúng workflow

```text
Làm phiên F1 (docs/next-session-clusters-F.md §1.C1, §1.C2). Điều kiện: F0 xong (có baseline).
Môi trường (F0): DB wujia_f0 port 8099 giống UAT — lệnh bật + bẫy ở docs/f0-baseline.md §1; suite đối chứng
10 module portal = 520/520; mốc wj_measure ở docs/f0-baseline/measure_{anh,em}.json (so bằng --diff).

Sửa đúng 6 điểm, không mở rộng:
1. portal_support create (:92–133): parse int an toàn → redirect error=invalid_input; category phải
   tồn tại + active; đính kèm đi qua attach_files_to_record (MIME tài liệu/ảnh, ≤5MB, ≤6 file —
   tra acceptance/ledger support trước, có số BA thì theo BA).
2. portal_base franchise_switch (:406): chặn redirect ngoài site (//host, \\host, scheme) — tái dùng
   cách kiểm netloc của portal_layout set_lang (:236), gom thành 1 helper trong utils.
3. portal_info_request create (:131): không trả str(e) của Exception chung; ValidationError/UserError
   giữ thông điệp, lỗi khác → câu chung + _logger.exception.
4. Query string ghép str(e) (info_request :185, layout profile :120): url-encode.
5. portal_return new (:212): thay write state bằng rr.action_submit(); bỏ phần kiểm ≥ảnh trùng ở
   controller nếu model đã kiểm đúng số BA (đối chiếu MIN_IMAGES vs MIN_IMAGES_BEFORE_SEND trước).
6. Test HTTP cho từng điểm (mỗi test phải đỏ khi revert đúng điểm đó — mutation, luật E #7).
Tra docs/qa-issue-ledger.yaml cho từng file trước khi sửa (luật refactor #1).
Nghiệm thu: test mới xanh + suite portal 0 đỏ mới (có run đối chứng) + chatter phiếu đổi trả gửi từ
portal có dòng "Yêu cầu đã được gửi". Bump version module bị đụng.
```

### Prompt F2 — CSS 8 màn nhỏ ra khỏi `portal_layout`

```text
Làm phiên F2 (docs/next-session-clusters-F.md §1.B1, Phụ lục A). Điều kiện: F0 xong.

Chuyển CSS riêng của màn từ wujia_portal_layout/static/assets/css/_components.css,
_interaction.css, _pc_components.css về file CSS của module (số đếm F0): knowledge (23), purchase_history (19),
support (7), debt (3), exam (3), return (3), delivery (2), notification (2). Khảo sát (4) là của anh Thái — để yên.
Luật:
- Chạy scripts/qa/css_owner.py --layout-domain trước; class dùng ở ≥2 module = component, GIỮ.
- CHỈ DI CHUYỂN, không sửa giá trị. Giữ thứ tự cascade: file module phải nạp SAU layout
  (kiểm assets.xml / manifest; module chưa có file CSS thì tạo và khai báo đúng bundle/link + ?v=).
- Selector dùng chung trong :is() hover ở _interaction.css: tách phần của màn ra, không làm đứt
  phần còn lại. Dính wj-inspection-pc ⇒ để yên.
- Semantic diff CSS (mẫu phiên 23/08): tập rule MẤT ở layout = tập rule THÊM ở module, 0 khác.
Nghiệm thu: semantic diff khớp tuyệt đối; wj_measure --diff với baseline F0 = 0 thay đổi computed
style/chiều cao/số record ở 5 khổ; ảnh chụp 2 khổ mỗi màn giống; B4 286/286; css_owner báo 0
nhóm của 8 màn này còn ở layout. Bump ?v= + version mọi module bị đụng.
```

### Prompt F3 — CSS Đặt hàng + Home ra khỏi `portal_layout`

```text
Làm phiên F3 (docs/next-session-clusters-F.md Phụ lục A: portal_sale 78, portal_base 49).
Điều kiện: F2 xong (docs/f-progress.md mục F2). DB wujia_f0 port 8099 như F2; suite đối chứng 534/534.
Chạy test luôn kèm -u module cần test.

Công cụ dựng ở F2: scripts/qa/css_move/ (README) — plan → apply → semdiff → cstyle/cdiff.
Quy trình (bài học F2, bắt buộc):
1. css_owner --layout-domain trước. Tự grep lại nhóm "của 1 màn" trước khi dời: script gán nhầm chủ khi
   class bật bằng JS của layout (F2: wujia-msheet-open) hoặc nằm trong component layout (wj-filter-select) ⇒ GIỮ.
2. KHÔNG tách class khỏi các danh sách :is() ở _interaction.css (hover/active/transition dòng 61/87/110,
   gạch chân dòng 24): độ đặc hiệu :is() = đối số mạnh nhất (0,4,0 do wj-inspection-pc) ⇒ tách ra là tụt,
   thua rule khác (vd hover .wj-data-list--compact-row .wj-data-item). Để nguyên cho F4.
3. Bundle web.assets_frontend nạp SAU mọi <link> layout ⇒ rule dời có thể lật cascade (cả với rule layout
   đứng sau, kể cả shorthand margin/padding/border). Static check của plan.py KHÔNG đủ ⇒ phải đo:
   cstyle.py 2 lần trước khi sửa (ổn định 0 khác) → sửa → xoá ir_attachment /web/assets/% + restart →
   cstyle.py → cdiff = 0. Rule nào lật thì trả về layout đúng chỗ, comment 1 dòng, ghi nợ F4.
4. semdiff khớp tuyệt đối; test đọc thẳng _components.css phải trỏ sang file module (không để guard rỗng —
   nhưng guard "vắng mặt" thì rỗng là đúng, đừng thêm assertTrue).
5. wj_measure lệch chiều cao ⇒ run đối chứng CSS HEAD cùng route trước khi kết luận (F2: em.hcm /portal
   +16, /portal/order −20 là dữ liệu trôi, có cả trên code trước F2 — F3 đụng đúng 2 màn này, đối chứng
   NGAY đầu phiên để lấy mốc mới thay F0 cho 2 route đó).
Lưu ý riêng F3:
- wujia-kpi-* / wujia-kpi-card-link nằm trong :is() hover ⇒ phần đó giữ; chỉ dời rule thường.
- Đặt hàng có realtime/JS đọc class (wujia-mcart-*, morder-*): grep static/src JS trước, không đổi tên class.
- ProductCard/giỏ là vùng WJ-ORD-001/002/021/023 đã QA: đo thêm luồng thêm giỏ → bước → gửi đơn trên
  DB copy (không gửi đơn thật trên UAT). cstyle ACC/PREF: /portal, /portal/order (+ giỏ), 390 + 1440, 2 tài khoản.
Nghiệm thu như F2: semdiff tuyệt đối · cdiff 0 · wj_measure --diff 0 (sau đối chứng) · ảnh 2 khổ chỉ lệch dữ liệu ·
B4 286/286 · suite 534/534 · css_owner 0 nhóm sale/base ngoài danh sách giữ lại có giải trình.
Bump ?v= + version module bị đụng. Không commit/push/deploy khi chưa được yêu cầu. Cuối phiên ghi f-progress + ✅ §2 + §5.
```

### Prompt F4 — Duyệt 41 rule viết đè component

```text
Làm phiên F4 (docs/next-session-clusters-F.md §1.B2, Phụ lục B). Điều kiện: F2, F3 xong.

Bước 1 (không sửa code): với mỗi rule trong Phụ lục B (đếm lại bằng css_owner --overrides),
tra ledger/acceptance xem có issue nào đóng dấu dáng đó; chụp ảnh component đó ở màn gốc vs màn đè.
Phân 3 loại: (a) nên thành biến thể chuẩn trong layout (vd wj-card-header--sm) vì ≥2 màn cần;
(b) lệch vô lý → bỏ, về dáng chuẩn; (c) BA đã duyệt riêng → giữ, ghi chú.
Viết bảng vào docs/f4-override-review.md rồi DỪNG, hỏi chủ dự án duyệt bảng (có ảnh).
Thêm vào bảng 2 món F2 để lại: (1) các danh sách :is() ở _interaction.css (hover/active/transition + gạch
chân) liệt kê tên màn — đề xuất hover theo component (wj-data-item/…) thay vì tên màn, và chốt 1 màu hover
vì .wj-data-list--compact-row .wj-data-item:hover (rgba .04) đang THUA :is() (primary-soft); (2)
.wujia-mknow-article > .wj-card-header{margin-top:16px} giữ ở layout — rule chết (thua CardHeader compact).
Bước 2 (sau khi duyệt): áp (a) và (b). Loại (b) có đổi giao diện ⇒ ghi rõ trong bảng để báo BA.
Nghiệm thu: css_owner --overrides chỉ còn loại "chỉ bố cục" + loại (c) có ghi chú;
wj_measure --diff chỉ khác đúng các màn trong bảng; test component layout xanh.
```

### Prompt F5 — Khung `portal_layout` thuần

```text
Làm phiên F5 (docs/next-session-clusters-F.md §1.A3). Điều kiện: F0–F4 xong. Đọc thêm §E8 của
docs/next-session-clusters-E.md (Sidebar) để thiết kế không chặn E8.

1. Menu: pc_sidenav (10 link), mobile_bottomnav (11), mobile_header (7) đang ghi cứng route Wujia.
   Layout chỉ giữ khung + slot; mục menu do module sở hữu route chèn vào (xpath vào slot có
   sequence) hoặc portal_base giữ danh sách nếu mục dùng chung. Thứ tự, nhãn, icon, active state,
   badge chuông/giỏ phải GIỐNG HỆT. Gỡ 1 module portal ⇒ mục của nó biến mất (test).
2. Test: 9/10 file tests của portal_layout gọi template module khác → template mẫu viết trong
   tests của layout; test trên màn thật chuyển về module của màn. Tổng số assert không giảm.
3. redirects.py: route cũ return/exam/purchase_history chuyển về đúng module.
Nghiệm thu: layout test chạy được trên DB chỉ cài portal_layout; wj_measure --diff = 0 trên menu
(PC + mobile, user owner và staff); check_layers không báo layout biết route Wujia.
Dừng hỏi nếu: mục menu có điều kiện hiển thị theo quyền nằm trong layout (không đoán).
```

### Prompt F6 — Controller Đặt hàng mỏng

```text
Làm phiên F6 (docs/next-session-clusters-F.md §1.C3 dòng portal_sale). Sau cổng F.
Tra ledger WJ-ORD-001/002/021/023, POR-019/022 trước khi đụng.
1. Luật số lượng: 1 nguồn product._portal_qty_error(qty) → trả (code, message) hoặc None;
   controller add/update/step + constraint sale_order_line dùng chung. Mã lỗi + câu chữ giữ nguyên.
2. Giỏ: SQL upsert/step atomic chuyển thành method trên wujia.portal.cart.line (giữ nguyên SQL,
   giữ LEAST cap, giữ invalidate); controller chỉ gọi và dựng state.
3. Submit: wujia.portal.cart.action_submit_order() làm khoá NOWAIT, khung giờ, huỷ báo giá cũ,
   tạo SO, xoá giỏ; trả order hoặc raise lỗi có mã. Controller map mã → redirect như cũ.
   Giữ nguyên hành vi "write state cancel, không action_cancel" và rollback nguyên khối.
Nghiệm thu: test cũ của sale xanh y hệt (run đối chứng) + test đồng thời 2 request submit/step
như WJ-ORD-002 + controller portal_sale giảm ≥300 dòng. Không đổi response JSON.
```

### Prompt F7 — Pilot tách `order_window`

```text
Làm phiên F7 (ADR-027 §Quy trình tách, chapter 74). Điều kiện: FR-A3 xong (mục D đã giải,
merge c80a6e2). Khuôn: custom/wujia_franchise_inspection/hooks.py.
Tạo wujia_order_window (nghiệp vụ, depend wujia_sale) nhận model wujia.order.window + kế thừa
sale.order, view/menu/ACL/data từ wujia_portal_order_window. pre_init_hook đổi chủ ir_model_data
(model_*, field_*, xmlid view/menu/access). wujia_portal_order_window: nếu không còn gì ⇒ để module
rỗng depend wujia_order_window (không gỡ trong phiên này), portal_sale đổi depend.
Đo TRƯỚC/SAU trên DB copy: số record, xmlid mỗi module, menu/action, ACL, cấu hình khung giờ đọc
ra giống hệt; lệnh deploy 1 dòng (-i wujia_order_window -u wujia_portal_order_window,wujia_portal_sale).
Viết quy trình thực tế + bẫy gặp vào chapter 74 §Quy trình (để F8+ dùng lại).
```

### Prompt F8–F13 — Tách phân hệ + controller mỏng (dùng chung, thay `<x>`)

```text
Làm phiên F<n>: tách <x> (ADR-027, quy trình đã chuẩn hoá ở F7). Điều kiện: F7 xong.
Phân hệ: F8 info_request · F9 knowledge · F10 support · F11 announcement (từ portal_notification,
giữ _name wujia.notification) · F12a/F12b exam · F13a/F13b return (lượt a = chuyển model/quyền,
lượt b = controller mỏng).
Lượt chuyển: wujia_<x> nhận models, view backend, menu, group, rule, sequence, cron, data, i18n phần
model; pre_init_hook đổi chủ xmlid; sửa mọi tham chiếu wujia_portal_<x>.group_* ở module khác;
đo trước/sau: số record, user trong group, number_next sequence, menu/action, rule.
Lượt mỏng: luật trong controller (§1.C3 dòng <x>) → method model create_from_portal /
register_from_portal / _mark_read; bảng badge của <x> rời portal_base/utils.py về portal_<x> (A2);
domain phạm vi cửa hàng → model._portal_scope_domain (C4). Response/redirect/thông điệp giữ nguyên.
Nghiệm thu: test cũ xanh (run đối chứng), check_layers không còn vi phạm của <x>, controller <x>
không còn write state/create kèm hệ quả.
```

### Prompt phiên review ★ (FR-B · FR-A3 · FR-P · FR-A — thay `<khối>`)

```text
Làm phiên review <khối> (docs/next-session-clusters-F.md §2). KHÔNG làm tính năng mới.
Phạm vi: FR-B = F2+F3+F4 · FR-A3 = cả cổng F0–F5 · FR-P = F7 · FR-A = F1, F6, F7–F13.
1. Soi lại bằng máy trên DB copy giống UAT (luật E #1), so với baseline F0:
   - FR-B: css_owner --layout-domain/--overrides (0 nhóm màn ở layout, override chỉ còn loại giữ);
     wj_measure --diff 5 khổ + ẢNH CHỤP mọi route 2 khổ, xem bằng mắt từng cặp (số Pass vẫn có thể
     giấu vỡ — bài học D3e); B4 286/286; các danh sách :is() hover ở _interaction.css không đứt.
   - FR-A3: như FR-B + menu PC/mobile theo 2 vai trò + test layout chạy độc lập + check_layers.
   - FR-P / FR-A: check_layers 0 vi phạm của phân hệ đã tách; đo ir_model_data/record/group/sequence
     trước–sau; controller còn write state/create kèm hệ quả không; test cũ xanh (run đối chứng);
     đã deploy UAT thì đo lại chỉ-đọc trên chính UAT (version + menu + quyền).
2. Rà diff toàn khối (từ commit đầu khối): code thừa, comment sử ký, file rác, bump version/?v= sót,
   selector đụng nhầm nhóm Khảo sát.
3. Lỗi sót nhỏ (<30 dòng, không đổi hành vi) ⇒ sửa + test; lớn hơn ⇒ ghi nợ, KHÔNG sửa trong phiên.
4. Ghi docs/f-review-<khối>.md: bảng kiểm Pass/Fail kèm lệnh chạy lại, ảnh đáng chú ý, nợ còn lại,
   bài học cho khối sau. Ghi mục vào docs/f-progress.md + ✅ §2 Trạng thái + compact summary §5.
FR-A3 riêng: kết luận "mở lại Issue List được chưa"; nếu được, ghi thứ tự E4b → E4c → E5 → E6 → E7
→ E8 và soạn đề xuất gửi BA mở cụm EmptyState (~124 chỗ viết tay).
```

---

## Phụ lục A — Nhóm class của từng màn đang nằm trong `portal_layout`

Đếm lại 17/09 (phiên F0) bằng `scripts/qa/css_owner.py --layout-domain` — thay bản heuristic tên class.
Nhóm = gốc BEM (bỏ `__x`, `--x`); chủ = module dùng thật (view lxml + JS + controller). Tổng **380 nhóm**
(khớp heuristic), trong đó **193 của 1 màn** · 88 component · 84 khung layout tự dùng · 15 orphan.
Lệch so với bản heuristic 176: heuristic gán theo tên (cả họ `wujia-msheet-*` → debt) còn script theo nơi
dùng thật (`wujia-msheet-item*` dùng ở debt + Khảo sát ⇒ component; `wujia-msheet`/`-title` chỉ layout ⇒ khung;
`wujia-msheet-open` exam bật ⇒ exam — F2 soi lại vì đây là cờ body của bottom sheet chung); heuristic bỏ sót
nhóm chỉ có con BEM trong view. Đếm lại: `python3 scripts/qa/css_owner.py --layout-domain` (python env Odoo, cần lxml).

### → `wujia_portal_sale` — 78

- `wj-pc-cart-del` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wj-pc-cart-step` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wujia-mcart` — _components.css:1689
- `wujia-mcart-del` — _components.css:1790, _components.css:1805, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-mcart-grand` — _components.css:1861
- `wujia-mcart-note` — _components.css:1817, _components.css:1829
- `wujia-mcart-note-label` — _components.css:1810
- `wujia-mcart-noteblock` — _components.css:1809
- `wujia-mcart-row` — _components.css:1697
- `wujia-mcart-row-amount` — _components.css:1777
- `wujia-mcart-row-amount-label` — _components.css:1778
- `wujia-mcart-row-amount-value` — _components.css:1783
- `wujia-mcart-row-controls` — _components.css:1740
- `wujia-mcart-row-main` — _components.css:1724
- `wujia-mcart-row-meta` — _components.css:1734
- `wujia-mcart-row-name` — _components.css:1725
- `wujia-mcart-row-thumb` — _components.css:1707
- `wujia-mcart-scroll` — _components.css:1692
- `wujia-mcart-step` — _components.css:1756, _components.css:1769, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-mcart-step-qty` — _components.css:1770
- `wujia-mcart-stepper` — _components.css:1746
- `wujia-mcart-submit` — _components.css:1862, _components.css:1873, _components.css:1874
- `wujia-mcart-submit-hint` — _components.css:1846
- `wujia-mcart-summary` — _components.css:1832
- `wujia-mcart-summary-line` — _components.css:1853, _components.css:1860
- `wujia-mcart-summary-rows` — _components.css:1852
- `wujia-morder` — _components.css:1400
- `wujia-morder-add-btn` — _components.css:1604
- `wujia-morder-cartctl` — _components.css:1602, _components.css:1603, _components.css:1604, _components.css:1605
- `wujia-morder-chips` — _components.css:1479
- `wujia-morder-floatbar` — _components.css:1636
- `wujia-morder-floatbar-btn` — _components.css:1675
- `wujia-morder-floatbar-icon` — _components.css:1654
- `wujia-morder-floatbar-info` — _components.css:1665
- `wujia-morder-floatbar-sub` — _components.css:1673
- `wujia-morder-floatbar-title` — _components.css:1672
- `wujia-morder-list` — _components.css:1484
- `wujia-morder-mstep` — _components.css:1613, _components.css:1626, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-morder-mstep-qty` — _components.css:1627
- `wujia-morder-mstepper` — _components.css:1603, _components.css:1605, _components.css:1606
- `wujia-morder-row` — _components.css:1491
- `wujia-morder-row-add` — _components.css:1564, _components.css:1580, _components.css:1581, _interaction.css:61 (+2)
- `wujia-morder-row-meta` — _components.css:1543
- `wujia-morder-row-name` — _components.css:1530
- `wujia-morder-row-price` — _components.css:1557
- `wujia-morder-row-qty` — _components.css:1582
- `wujia-morder-row-spec` — _components.css:1550
- `wujia-morder-row-thumb` — _components.css:1506
- `wujia-morder-row-thumb-img` — _components.css:1519
- `wujia-morder-row-thumb-ph` — _components.css:1525
- `wujia-morder-search` — _components.css:1429
- `wujia-morder-search-btn` — _components.css:1435, _components.css:1449, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-morder-search-input` — _components.css:1450, _components.css:1456, _components.css:1465, _components.css:1475
- `wujia-morder-warnbar` — _components.css:1404, _components.css:1416, _components.css:1419, _components.css:1423
- `wujia-mres` — _components.css:1946, _components.css:1977
- `wujia-mres-card` — _components.css:1947
- `wujia-mres-cta` — _components.css:2079, _components.css:2092, _components.css:2093, _components.css:2094 (+2)
- `wujia-mres-icon` — _components.css:1952, _components.css:1961, _components.css:1962, _components.css:1973 (+1)
- `wujia-mres-icon-inner` — _components.css:1963, _components.css:1973, _components.css:1974
- `wujia-mres-info` — _components.css:1994
- `wujia-mres-info-label` — _components.css:2012
- `wujia-mres-info-row` — _components.css:2002, _components.css:2011
- `wujia-mres-info-value` — _components.css:2018, _components.css:2025
- `wujia-mres-note` — _components.css:2043, _components.css:2052, _components.css:2056, _components.css:2075
- `wujia-mres-note-body` — _components.css:2072
- `wujia-mres-note-dot` — _components.css:2057
- `wujia-mres-note-icon` — _components.css:2071
- `wujia-mres-note-label` — _components.css:2073, _components.css:2075
- `wujia-mres-note-text` — _components.css:2074
- `wujia-mres-note-value` — _components.css:2076
- `wujia-mres-sub` — _components.css:1984
- `wujia-mres-sub-line` — _components.css:1991
- `wujia-mres-title` — _components.css:1977
- `wujia-msubmit` — _components.css:1881, _components.css:1891
- `wujia-msubmit-card` — _components.css:1892
- `wujia-msubmit-spinner` — _components.css:1906, _components.css:1913, _components.css:1929
- `wujia-msubmit-sub` — _components.css:1937
- `wujia-msubmit-title` — _components.css:1931

### → `wujia_portal_base` — 49

- `wj-empty-state-body` — _components.css:456
- `wj-pc-acct-field` — _pc_account.css:85, _pc_account.css:89, _pc_account.css:90, _pc_account.css:91
- `wj-pc-acct-headcard` — _pc_account.css:54, _pc_account.css:57, _pc_account.css:58, _pc_account.css:63 (+9)
- `wj-pc-acct-kv-grid` — _pc_account.css:83, _pc_account.css:84
- `wj-pc-acct-members` — _pc_account.css:105, _pc_account.css:106, _pc_account.css:107, _pc_account.css:108 (+1)
- `wj-pc-acct-staff` — _pc_account.css:115, _pc_account.css:116, _pc_account.css:121, _pc_account.css:122 (+2)
- `wujia-content-card-empty` — _components.css:631
- `wujia-home-wrapper` — _components.css:1011
- `wujia-kpi-arrow` — _components.css:550
- `wujia-kpi-card` — _components.css:484, _components.css:490
- `wujia-kpi-card-link` — _components.css:475, _components.css:490, _components.css:559, _components.css:563 (+3)
- `wujia-kpi-content` — _components.css:522
- `wujia-kpi-desc` — _components.css:543
- `wujia-kpi-icon` — _components.css:497
- `wujia-kpi-icon-danger` — _components.css:512
- `wujia-kpi-icon-info` — _components.css:513
- `wujia-kpi-icon-primary` — _components.css:510
- `wujia-kpi-icon-warning` — _components.css:511
- `wujia-kpi-label` — _components.css:530
- `wujia-kpi-separator` — _components.css:515
- `wujia-kpi-value` — _components.css:536
- `wujia-maccount-badgerow` — _components.css:2952
- `wujia-maccount-kv` — _components.css:2926, _components.css:2933
- `wujia-maccount-kv-key` — _components.css:2934
- `wujia-maccount-kv-val` — _components.css:2939, _components.css:2948
- `wujia-maccount-kvlist` — _components.css:2925
- `wujia-maccount-store-sub` — _components.css:2961
- `wujia-mdash-sec` — _components.css:2648
- `wujia-mdash-tile` — _components.css:2697, _components.css:2708, _components.css:2709
- `wujia-mhome` — _components.css:1002, _components.css:2748, _wujia_theme.css:454
- `wujia-mhome-action` — _components.css:1192, _components.css:1205, _components.css:1206, _interaction.css:61 (+2)
- `wujia-mhome-action-icon` — _components.css:1207, _components.css:1217
- `wujia-mhome-action-label` — _components.css:1222
- `wujia-mhome-actions-grid` — _components.css:1187
- `wujia-mhome-hero` — _components.css:1018
- `wujia-mhome-hero-addr` — _components.css:1058
- `wujia-mhome-hero-area` — _components.css:1064
- `wujia-mhome-hero-label` — _components.css:1043, _components.css:1050
- `wujia-mhome-hero-left` — _components.css:1031
- `wujia-mhome-hero-right` — _components.css:1035, _components.css:1050
- `wujia-mhome-hero-store` — _components.css:1051
- `wujia-mhome-hero-top` — _components.css:1025
- `wujia-mhome-role-badge` — _components.css:1070
- `wujia-mhome-window` — _components.css:1130
- `wujia-mhome-window-caption` — _components.css:1172
- `wujia-mhome-window-progress` — _components.css:1160
- `wujia-mhome-window-progress-bar` — _components.css:1167
- `wujia-mhome-window-status` — _components.css:1148, _components.css:1153, _components.css:1154, _components.css:1155 (+1)
- `wujia-store-mobile-strip` — _interaction.css:61, _interaction.css:87, _interaction.css:110

### → `wujia_portal_knowledge` — 23

- `wujia-mknow-article` — _components.css:2566
- `wujia-mknow-article-title` — _components.css:2552
- `wujia-mknow-att` — _components.css:2613, _components.css:2624
- `wujia-mknow-att-main` — _components.css:2625
- `wujia-mknow-att-name` — _components.css:2632
- `wujia-mknow-att-sub` — _components.css:2640
- `wujia-mknow-badges` — _components.css:2536
- `wujia-mknow-body` — _components.css:2574, _components.css:2579, _components.css:2580, _components.css:2585 (+6)
- `wujia-mknow-date` — _components.css:2542
- `wujia-mknow-feat` — _components.css:2466, _components.css:2478, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-mknow-feat-main` — _components.css:2488
- `wujia-mknow-lead` — _components.css:2567
- `wujia-mknow-list` — _components.css:2497
- `wujia-mknow-meta` — _components.css:2559
- `wujia-mknow-row` — _components.css:2502, _components.css:2507, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-mknow-row-foot` — _components.css:2530
- `wujia-mknow-row-main` — _components.css:2517
- `wujia-mknow-row-title` — _components.css:2524
- `wujia-mknow-sechead` — _components.css:2422
- `wujia-mknow-sechead-pill` — _components.css:2438
- `wujia-mknow-sechead-sub` — _components.css:2434
- `wujia-mknow-sechead-title` — _components.css:2429
- `wujia-mknow-tile` — _components.css:2452, _components.css:2463

### → `wujia_portal_purchase_history` — 19

- `wujia-mhist-card` — _components.css:2205
- `wujia-mhist-list` — _components.css:2125
- `wujia-mhist-prod` — _components.css:2236, _components.css:2244
- `wujia-mhist-prod-amount` — _components.css:2260
- `wujia-mhist-prod-main` — _components.css:2245
- `wujia-mhist-prod-name` — _components.css:2251
- `wujia-mhist-prod-spec` — _components.css:2256
- `wujia-mhist-row` — _components.css:882, _components.css:2130, _interaction.css:61, _interaction.css:87 (+1)
- `wujia-mhist-row-amount` — _components.css:2164
- `wujia-mhist-row-code` — _components.css:2148
- `wujia-mhist-row-date` — _components.css:2153
- `wujia-mhist-row-main` — _components.css:2142
- `wujia-mhist-row-side` — _components.css:2157
- `wujia-mhist-summary` — _components.css:2173
- `wujia-mhist-summary-amount` — _components.css:2197
- `wujia-mhist-summary-bottom` — _components.css:2180, _components.css:2187
- `wujia-mhist-summary-code` — _components.css:2188
- `wujia-mhist-summary-date` — _components.css:2193
- `wujia-mhist-summary-top` — _components.css:2180

### → `wujia_portal_support` — 7

- `wujia-mticket-bubble` — _components.css:2820, _components.css:2828, _components.css:2829, _components.css:2835 (+2)
- `wujia-mticket-bubble-meta` — _components.css:2842, _components.css:2847, _components.css:2848
- `wujia-mticket-reply` — _components.css:2851
- `wujia-mticket-reply-input` — _components.css:2857, _components.css:2868
- `wujia-mticket-rowside` — _components.css:2792
- `wujia-mticket-tag` — _components.css:2801
- `wujia-mticket-thread` — _components.css:2814

### → `wujia_portal_inspection` (code anh Thái — KHÔNG dời, chỉ ghi nhận) — 4

- `wj-inspection-pc` — _interaction.css:61, _interaction.css:87, _interaction.css:110, _pc_components.css:204 (+5)
- `wj-pc-page-btn` — _interaction.css:61, _interaction.css:87, _interaction.css:110, _pc_components.css:216 (+3)
- `wj-pc-pagination` — _pc_components.css:204, _pc_components.css:210
- `wj-surface-card-link` — _components.css:686

### → `wujia_portal_debt` — 3

- `wj-debt-actionrow` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wj-debt-pc-pdf` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wj-debt-pc-tab` — _interaction.css:61, _interaction.css:87, _interaction.css:110

### → `wujia_portal_exam` — 3

- `wj-exam-pc-navbtn` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wujia-mexam-card` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wujia-msheet-open` — _components.css:2270

### → `wujia_portal_return` — 3

- `wj-filter-select` — _components.css:336, _components.css:3437, _components.css:3634, _pc_components.css:512
- `wujia-mreturn-btn-cancel` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wujia-mreturn-row` — _interaction.css:61, _interaction.css:87, _interaction.css:110

### → `wujia_portal_delivery` — 2

- `wj-pc-dlv-chip` — _interaction.css:61, _interaction.css:87, _interaction.css:110
- `wujia-mdelivery-row` — _interaction.css:61, _interaction.css:87, _interaction.css:110

### → `wujia_portal_notification` — 2

- `wj-pc-noti-head-actions` — _pc_components.css:441
- `wujia-mnoti-row` — _interaction.css:61, _interaction.css:87, _interaction.css:110

---

## Phụ lục B — Rule trong module portal viết đè component chung, loại "đổi dáng"

Đếm lại 17/09 (phiên F0) bằng `scripts/qa/css_owner.py --overrides` — **41 rule** (bản heuristic ghi 30;
chủ dự án chốt dùng số mới). Chỉ tính khi **phần tử đích** của selector mang class component/khung
(`.wj-pc-table thead th` tính, `.wujia-mpage .wujia-mexam-title` không). Lệch: +14 rule đè lên tên con BEM
heuristic bỏ sót (`wj-empty-state-title`, `wj-pc-td--muted`, `wj-pc-metric-card__value`, `wujia-badge`…);
−3 rule heuristic tính nhầm là đổi dáng nhưng chỉ đổi bố cục (`portal_debt.css:227,296` column/row-gap,
`portal_support.css:2` min-height). "Chỉ bố cục" không liệt kê — mặc định giữ.

| Module | Đổi dáng | Chỉ bố cục |
|---|---|---|
| `wujia_portal_debt` | 9 | 11 |
| `wujia_portal_delivery` | 3 | 1 |
| `wujia_portal_exam` | 15 | 18 |
| `wujia_portal_notification` | 6 | 5 |
| `wujia_portal_report` | 1 | 1 |
| `wujia_portal_return` | 3 | 2 |
| `wujia_portal_sale` | 4 | 1 |
| `wujia_portal_support` | 0 | 1 |

### `wujia_portal_debt` — 9 rule đổi dáng

- `portal_debt.css:215` `.wj-debt-inv:not(.wj-data-item)` — đổi: background, border-radius
- `portal_debt.css:246` `.wj-debt-empty .wj-empty-state-icon` — đổi: background
- `portal_debt.css:247` `.wj-debt-empty .wj-empty-state-icon > i` — đổi: font-size
- `portal_debt.css:248` `.wj-debt-empty .wj-empty-state-title` — đổi: font-size
- `portal_debt.css:249` `.wj-debt-empty .wj-empty-state-sub` — đổi: font-size
- `portal_debt.css:284` `.wj-debt-pay:not(.wj-data-item)` — đổi: background, border-radius
- `portal_debt.css:346` `.wj-debt-bank .wj-section-header__title` — đổi: color, font-size, letter-spacing, line-height
- `portal_debt.css:707` `.wj-debt-hint .wj-card-header.wj-debt-hint-head .wj-card-header__title` — đổi: color, font-size, line-height
- `portal_debt.css:721` `.wj-debt-summary__head .wj-card-header.wj-debt-summary__hb .wj-card-header__title` — đổi: color, font-size, font-weight, letter-spacing, line-height

### `wujia_portal_delivery` — 3 rule đổi dáng

- `portal_delivery.css:46` `.wj-data-list--detail-card .wujia-mdelivery-row.wj-data-item` — đổi: color
- `portal_delivery.css:49` `.wujia-mdelivery-row:not(.wj-data-item)` — đổi: background, border, border-radius, color, text-decoration
- `portal_delivery.css:183` `.wujia-dlv-pc .wj-pc-page-header__title` — đổi: font-size

### `wujia_portal_exam` — 15 rule đổi dáng

- `portal_exam.css:169` `.wujia-mexam-course:not(.wj-data-item)` — đổi: background, border, border-radius
- `portal_exam.css:574` `.wujia-mexam-rrow:not(.wj-data-item)` — đổi: background, border, border-radius
- `portal_exam.css:687` `.wj-exam-pc .wj-pc-page-header__title` — đổi: font-size, font-weight
- `portal_exam.css:693` `.wj-exam-pc .wj-pc-page-header__crumb` — đổi: font-weight
- `portal_exam.css:694` `.wj-exam-pc .wj-pc-btn` — đổi: font-weight
- `portal_exam.css:705` `.wj-exam-pc .wj-pc-card__title` — đổi: font-size
- `portal_exam.css:720` `.wj-exam-pc .wj-card-header.wj-exam-pc-sechead--sm .wj-card-header__title, .wj-exam-pc .wj…` — đổi: font-size, line-height
- `portal_exam.css:727` `.wj-exam-pc .wj-pc-table thead th` — đổi: font-size
- `portal_exam.css:774` `.wj-exam-pc-list-table .wj-pc-td--code` — đổi: font-weight
- `portal_exam.css:775` `.wj-exam-pc-list-table .wj-pc-td--muted` — đổi: font-weight
- `portal_exam.css:855` `.wj-exam-pc-res-table .wj-pc-td--muted` — đổi: font-weight
- `portal_exam.css:1316` `.wj-exam-pc-tablebox .wj-pc-table thead th:first-child, .wj-exam-pc-tablebox .wj-pc-table …` — đổi: border-radius
- `portal_exam.css:1318` `.wj-exam-pc-tablebox .wj-pc-table tbody tr:last-child td` — đổi: border-bottom
- `portal_exam.css:1338` `.wj-exam-pc-part-table .wj-pc-td--muted` — đổi: font-weight
- `portal_exam.css:1658` `.wj-exam-pc-sum-table .wj-pc-td--muted` — đổi: font-weight

### `wujia_portal_notification` — 6 rule đổi dáng

- `portal_notification.css:24` `.wujia-mnoti .wj-filter-chip` — đổi: font-size
- `portal_notification.css:42` `.wujia-mnoti-row:not(.wj-data-item)` — đổi: background, border, border-radius, text-decoration
- `portal_notification.css:104` `.wujia-mnoti-row-tags .wujia-badge` — đổi: font-size
- `portal_notification.css:105` `.wujia-mnoti-row-tags .wujia-badge i, .wujia-mnoti-detail-badges .wujia-badge i` — đổi: font-size
- `portal_notification.css:248` `.wj-data-table.wj-pc-noti-table tbody tr:hover` — đổi: background
- `portal_notification.css:408` `.wj-pc-noti-popup__item-tags .wj-pc-badge` — đổi: font-size, font-weight, line-height

### `wujia_portal_report` — 1 rule đổi dáng

- `portal_report.css:88` `.wj-rep-pcmetrics .wj-pc-metric-card__value` — đổi: font-size

### `wujia_portal_return` — 3 rule đổi dáng

- `portal_return.css:33` `.wujia-mreturn-row:not(.wj-data-item)` — đổi: background, border, border-radius, text-decoration
- `portal_return.css:134` `.wj-surface-card__body > .wj-card-header.wj-return-sublabel .wj-card-header__title` — đổi: color
- `portal_return.css:137` `.wj-surface-card__body > .wj-card-header.wj-return-sublabel--danger .wj-card-header__title` — đổi: color

### `wujia_portal_sale` — 4 rule đổi dáng

- `portal_order.css:37` `.wj-pc-order-filter select.wj-pc-filter-control` — đổi: cursor
- `portal_order.css:206` `.wj-pc-order-add:focus-visible, .wj-pc-cart-step:focus-visible, .wj-pc-cart-del:focus-visi…` — đổi: outline, outline-offset
- `portal_order.css:269` `.wj-empty-state-icon.wujia-mcart-empty-icon` — đổi: background
- `portal_order.css:276` `.wj-empty-state.wujia-mcart-empty-card .wj-empty-state-title` — đổi: font-size
