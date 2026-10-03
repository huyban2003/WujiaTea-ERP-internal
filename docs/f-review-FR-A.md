# ★FR-A — Review toàn khối A (F1, F6, F7–F13): clean · performance · cấu trúc ADR-027 · Issue List

*Phiên 26/09/2026 · Mac · HEAD `164d8ec` (main) · đối chứng worktree `9d2a606` (sau FR-P, trước F8) ·
DB `wujia_fra` (= `wujia_frp` + replay 6 đợt deploy đúng thứ tự UAT) port 8097 ‖ `wujia_fra_ref` port 8098 (cùng seed) ·
`wujia_fra_alone` (trắng) · `wujia_fra_test` (suite) · `wujia_fra_mut` (mutation) · UAT `wujia_tea_19` **chỉ đọc**.*

Khối được duyệt: F1 `aebcd56` + F6 `df385d1` → F7 → FR-P → F8–F13 (`a138d21`) = **207 file, +9936 −8509** trong `custom/`.
Ba câu hỏi chủ dự án: (1) code sạch, chạy nhanh, đúng tầng như plan? (2) Issue List còn component nào phải chuẩn hoá? (3)
lệch plan → chỉ ghi.

## 1. Kết luận

**ĐẠT — khối A khép.** Không có lệch cấu trúc nào phía Dev; hiệu năng không đổi; phần "chưa sạch" đều là vụn vặt và
đã sửa ngay theo luật ★ (<30 dòng, không đổi hành vi). Cụ thể:

1. **Cấu trúc**: `check_layers` 0 vi phạm phía Dev (R7 còn 2 của anh Thái, `_wj_ensure_contract`). 7 module nghiệp vụ L2
   không có controller/static/`http`/xmlid portal trong `.po` (bảng §3). Module ghép L3b chỉ giữ đúng 2 ngoại lệ đã chốt
   ADR-027 (`wujia.portal.cart`, AbstractModel `wujia.portal.debt`). Mọi chỗ `portal_base` gọi L2 đều qua `hasattr`.
2. **Performance**: số query mỗi route **giống hệt** HEAD ‖ đối chứng ở 17 route × 4 user (bảng §5); index có đủ trên
   `franchise_id`/`state`/ngày của 6 bảng chính; không `search()` trong vòng lặp ở method `_portal_*` mới.
3. **Clean**: xoá 4 hàm chết + 1 `ormcache` thừa + 3 import thừa, 1 bẫy `number_next` (sequence INF reset khi `-i`), 14
   comment dẫn mã phiên trong code khối A; diff sửa nhỏ **11 file, +16 −112**. Suite sau sửa **914/0/0**.
4. **Issue List**: 138 issue, 123 Done · 8 Ready for Dev · 4 Ready for Retest · 3 Need Clarification. 17/23 component đã có
   issue; 6 chưa (EmptyState, InfoBanner, CountMeta, DetailSummary, StatCard, ProductCard). Kết luận §6: **tạm tương đối**,
   chỉ EmptyState đáng mở issue mới; 8 issue mở chia 4 cụm.
5. **Nợ retest thật** `UI-DATALIST-001` (BA fail 26/09 ở `/portal/debt/payment-history` mobile) — sửa trong phiên, commit
   riêng, **chưa deploy** (§7b).

## 2. Bảng Pass/Fail

| # | Mục (prompt ★FR-A) | Kỳ vọng | Đo | KQ |
|---|---|---|---|---|
| 0 | Replay 6 đợt deploy UAT lên `wujia_fra` | 0 ERROR | `replay.out` 0 ERROR/Traceback | ✅ |
| 1 | Suite 15 portal + 7 L2 | ≥912, 0 đỏ | trước sửa **912/0/0** · sau sửa nhỏ + fix debt **914/0/0** (+2 test debt) | ✅ |
| 2 | DB trắng: `-i` 7 L2 không portal, rồi test | 0 đỏ | install EXIT 0 · tag 7 module **123/0/0** | ✅ |
| 3 | `split_snapshot` trước/sau replay | lệch = đã giải trình | 1031 dòng đổi chủ · 12 lệch đều thuộc danh sách giải trình F8–F13 · **+1 phát hiện mới**: `INF/` `number_next` reset về 1 (sửa, §7a) | ✅ |
| 4 | HTML so từng byte HEAD ‖ `9d2a606`, 17 route × 4 user | khác = cố ý | **63/68 giống**; 5 khác = Home ×4 (nhãn F13 "Đã gửi"/"Đang bù một phần") + payment-history mobile em.hcm (fix §7b); khối PC payment-history md5 giống ở 3 biến thể trang | ✅ |
| 5 | `check_layers` · `nav_dump --diff` · `wj_measure --diff` HEAD ‖ ref | 0 · 0 · 0 mất record | 0 Dev (R7 Thái 2) · nav 0 lệch · wj_measure chỉ `/portal` 390/360 lệch chiều cao +18/−36 (nhãn F13 dài hơn, xuống dòng), **0 mất record** | ✅ |
| 6 | Playwright 16 màn × PC 1440 + mobile 390 × 2 user | 200, 0 tràn, 0 JS error | 16/16 200, 0 tràn; `/portal/order/new` 404 ở cả HEAD và ref (route không tồn tại, không thuộc khối A); console chỉ `/app-assets/data/locales/en.json` 404 (có từ trước) | ✅ |
| 7 | UAT chỉ-đọc | version khớp HEAD, sequence, nhóm, menu | 43 version khớp (kể cả `wujia_support 19.0.1.0.1` = F10-fix đã lên; `wujia_portal_order_window` uninstalled) · số kế RTN 5 · CA 1 · ANN 20 · KNW 28 · WJ-TK 17 · INF 1 · WJ-CRS 5 · WJ-EXR 17 · WJ-EXS 6 · nhóm Administrator 1 người, User 0 (Return/Exam/Notification) · 7 user portal · menu dưới "Franchise Management" | ✅ |
| 8 | Mutation xuyên khối M0–M7 | đỏ đúng test | M0 0/81 · M1 5 · M2 1 · M3 3 · M4 4 · M5 2 · M6 3 · **M7 0** (bỏ `extra` hook return: pre_init chỉ chạy khi cài, `split_snapshot` mới bắt — ghi nợ) | ✅ (7/8, M7 giải trình) |
| 9 | Review đọc code 3 trục | ghi bảng | §3–§5 | ✅ |
| 10 | Issue List | kết luận a/b/c | §6 | ✅ |

## 3. Tuân thủ tầng (ADR-027)

**7 module nghiệp vụ L2** (`ls controllers`, `ls static`, grep `odoo.http`, grep `wujia_portal_` trong `.po`):

| Module | controllers | static | import http | `.po` xmlid portal |
|---|---|---|---|---|
| `wujia_info_request` · `wujia_knowledge` · `wujia_support` · `wujia_notification` · `wujia_exam` · `wujia_return` · `wujia_order_window` | 0 | 0 | 0 | 0 |

**Module ghép L3b có model** (`grep _name`): `wujia_portal_sale` = `wujia.portal.cart` + `.line` (giỏ, chốt ADR-027);
`wujia_portal_debt` = AbstractModel `wujia.portal.debt` (seam đọc kế toán, chốt ADR-027 §auto_install "soi lại khi áp");
`wujia_portal_layout` chỉ `ir.http`; `wujia_portal_base` 0 `_name`. Các portal khác 0 model.

**Seam `hasattr` của `portal_base` (L3a, cấm thêm depend)** — đúng thiết kế, liệt kê để BA/Thái biết:

| File:dòng | Gọi | Chủ (L2) |
|---|---|---|
| `portal_base/controllers/portal.py:165` | `_portal_visible_domain` | `wujia_knowledge` |
| `…/portal.py:224–225` | `_is_within_order_window` / `_user_now_hours` | `wujia_order_window` |
| `…/portal.py:312/316` | `_portal_unread_count` / `_portal_open_domain` | `wujia_notification` |
| `…/portal.py:328/332` | `_portal_effective_domain` / `_portal_recent_domain` | `wujia_return` |
| `portal_base/controllers/utils.py:357, 544` | `_portal_status_key` | `wujia_return` |

**Controller mỏng** (dòng, ref `9d2a606` → HEAD, `wc -l`): info_request 264→240 · knowledge 181→154 · support 201→166 ·
notification 434→337 · exam 750→579 · return 609→378 · sale 863→863 (F6 nằm trước mốc ref). `controller_inventory`
HEAD = ref: 103 route / 106 path / 21 class — không mất route.

**`auto_install: True`** hiện chỉ 3 module, đều của anh Thái (`wujia_mobile_franchise_operations`,
`wujia_mobile_portal_info_request`, `wujia_mobile_portal_exam`); ADR-027 ý #3 (bật đồng loạt cho module ghép thuần) chưa
áp — nợ, đúng plan "chỉ ghi".

## 4. Clean

Đã sửa ngay (luật ★, mỗi mục <30 dòng, không đổi hành vi, pyflakes sạch) — chi tiết §7a. Còn lại (chỉ ghi):

- Comment dẫn mã phiên/issue trong code sản phẩm (không tính test/hook/manifest) — đếm máy ở `wujia_portal_*` + 7 L2:
  **49 dòng `.py`**, **349 dòng nếu tính cả xml/css/js** (đa số là mã issue `UI-*`/`WJ-*`/`CMP-*` trong template). Nợ
  FR-A3 ghi "148 dòng trong 14 module" là phạm vi khác; số mới do lệnh ở §10.
- `_sql_constraints` (Odoo 19 bỏ) — **16 file** toàn `custom/`, trong đó 8 file phía Dev: `wujia_support_category`,
  `wujia_info_update_request`, `wujia_knowledge_{article,category,tag}`, `wujia_audit` ×2, `wj_ks_dashboard_ninja`; 8 file
  còn lại thuộc module anh Thái (bàn giao).
- `wujia_portal_sale` còn `line.write/unlink`, `cart.write` ở route update · remove · note (F6 chốt chỉ 3 phần); `wujia_portal_return`
  còn `rr.write(vals)` gắn đính kèm sau `create_from_portal`.
- Dư âm tên portal trong L2: ICP `wujia_portal.*`, field `portal_order_time_*`, xmlid view, app/menu "Wujia Portal" — giữ vì
  đổi là migration dữ liệu.

## 5. Performance (đo, không đoán)

Số query mỗi request lấy từ dòng werkzeug INFO (Odoo 19 in `<nq> <sqltime> <othertime>`), min qua 4 user, 2 server cùng seed:

| Route | HEAD | ref | Δ |
|---|---|---|---|
| `/portal` | 34 | 34 | 0 |
| `/portal/order` | 27 | 27 | 0 |
| `/portal/notification` | 21 | 21 | 0 |
| `/portal/knowledge` | 18 | 18 | 0 |
| `/portal/return` | 17 | 17 | 0 |
| `/portal/delivery` | 16 | 16 | 0 |
| `/portal/info-request` | 15 | 15 | 0 |
| `/portal/return/new` | 14 | 14 | 0 |
| `/portal/support` · `/portal/support/new` | 13 | 13 | 0 |
| `/portal/debt` · `/portal/debt/payment-history` · `/portal/exam` · `/portal/info-request/new` · `/portal/purchase-history` | 11 | 11 | 0 |
| `/portal/order/new` | 8 | 8 | 0 |
| `/portal/exam/register` | 1 | 1 | 0 |

Rà tĩnh method `_portal_*` mới ở 7 L2: không `search()`/`browse` trong vòng lặp (AST báo 1 false positive ở
`_portal_day_states` — vòng qua ngày, không ORM); mọi `search` có domain theo cửa hàng và `limit`/phân trang; `sudo()` chỉ
trong method model đã ghi rõ "gọi trên recordset sudo". Index (`pg_indexes`, `wujia_fra`): `wujia_return_request`
(franchise_id, state, request_date, requester_user_id…), `wujia_support_ticket` (franchise_id, state, created_by_id,
last_message_date, portal_visible…), `wujia_notification` (state, is_published_portal, published_date, expired_date…),
`wujia_knowledge_article` (is_published_portal, publish_date, expired_date, slug, state…), `wujia_exam_registration`
(franchise_id, state, session_id…) — đủ cho domain portal đang dùng; không cần thêm index.

## 6. Issue List — còn component nào cần chuẩn hoá?

Dump `issue_queue.py --json`: **138 issue** (123 Done · 8 Ready for Dev · 4 Ready for Retest · 3 Need Clarification), 45 `UI-*`.

| Nhóm | Component (23) | Issue liên quan | Trạng thái |
|---|---|---|---|
| Global Shell | GlobalHeader `CMP-GH-001` | UI-01, UI-PC-BASE-011 → hồi quy **140 UI-PC-TOPBAR-REG-001** | Ready for Dev |
| | StoreContextBar `CMP-SCB-001` | **141 UI-MOB-STORE-SWITCHER-001** (mockup đã chốt) | Ready for Dev |
| Navigation | SidebarNavigation `CMP-SN-001` | UI-SIDEBAR (F5a) | Done |
| | BottomNavigation `CMP-BN-001` | **145 UI-MOB-BOTTOMNAV-DENSITY-001** | Ready for Dev |
| | BackPageHeader `CMP-BPH-001` · Pagination `CMP-PGN-001` | E3/E4 (D-series) | Done |
| Page Structure | PageContainer `CMP-PC-001` | 129 UI-PAGECONTAINER-001 | Ready for Retest |
| | PageHeader `CMP-PG-001` · SectionHeader `CMP-SH-001` | E-series | Done |
| | CountMeta `CMP-CM-001` | — | chưa có issue |
| Container | SurfaceCard `CMP-SC-001` | UI-SURFACECARD-001 | Done |
| | CardHeader | 125 UI-CARDHEADER-001 | Need Clarification |
| Filter | FilterBar · SearchField · FilterChipGroup | E-series | Done |
| Detail | DetailSummary `CMP-DS-001` | — | chưa có issue |
| Status | StatusBadge `CMP-SB-001` | E2 | Done |
| Data Display | DataList `CMP-DL-001` | **126 UI-DATALIST-001** (retest fail 1 màn → sửa phiên này) | Ready for Retest (sau deploy) |
| | ListCard `CMP-LC-001` | E5, UAT-BH-007/008 | Done |
| | StatCard `CMP-KPI-001` | — (142 Home PC redesign sẽ đụng) | chưa có issue |
| Feedback | EmptyState `CMP-ES-001` | — (FR-A3 §7: 92 chỗ viết tay) | chưa có issue |
| | InfoBanner `CMP-IB-001` | — | chưa có issue |
| Action | Button `CMP-BTN-001` | 132 UI-BUTTON-001 | Ready for Retest |
| Domain | ProductCard `CMP-PRD-001` | — | chưa có issue |
| Mobile shell | (không phải component 23) | 14 UI-MOB-SHELL-001 · 143 UI-MOB-HEADER-DENSITY-001 · 144 WJ-ORD-MOB-SPACING-001 | Need Clarification · Ready for Dev ×2 |
| Routing | — | 146 WJ-PORTAL-ROUTING-001 | Ready for Dev |

Kết luận cho chủ dự án:

- **(a) Nên mở issue tiếp**: chỉ **EmptyState** (92 chỗ viết tay, mỗi màn một kiểu chữ/icon — đo FR-A3). StatCard và
  InfoBanner chờ 142 Home PC redesign, làm chung một lượt sẽ rẻ hơn.
- **(b) Tạm tương đối**: CountMeta, DetailSummary, ProductCard — mỗi cái ≤3 call site, đã đi qua template chung, chưa có spec
  BA riêng; mở issue lúc này chỉ tạo giấy.
- **(c) 8 issue đang mở → 4 cụm** (chỉ đề xuất): **140+141** shell header/store (PC topbar + mobile store switcher, cùng
  `wujia_portal_layout`) · **143+144+145** mật độ mobile (đo lại trên khung E7 trước, một bảng số) · **142** Home PC redesign
  (lớn, mockup V4, đụng StatCard/InfoBanner) · **146** routing `/` (`portal_base`, functional, không UI).
- Reconcile code ↔ sheet: 7 issue mới (140–146) **0 dòng code** trong repo (`git log -S`, `grep`); 126 = D5 đã có, retest
  fail 1 màn.

## 7. Đã sửa trong phiên

### 7a. Sửa nhỏ theo luật ★ (commit `review(FR-A)`, 11 file, +16 −112, không đổi hành vi)

- `wujia_info_request/data/ir_sequence_data.xml`: bỏ `number_next=1` (noupdate; `-i` lại module là sequence `INF/` về 1 —
  UAT đang 1 và 0 phiếu nên chưa gây hại).
- `portal_base/controllers/utils.py`: xoá 4 hàm không còn nơi gọi (`render_form_with_error`, `get_recent_orders`,
  `require_role`, `portal_unit_price_tax_included`) + import `UserError`, `ormcache`; comment mã phiên → nói *vì sao*.
- `wujia_notification`: xoá `get_display_summary`, `is_read_by` (nợ F11). `wujia_return_issue_type`: xoá `ormcache` không dùng.
- `wujia_knowledge` ×2: import thừa. Comment dẫn `F10/F11/F13/FR-A3/E2/E4c/Sprint 17` ở `portal_base`, `portal_notification`,
  `portal_support`, `wujia_return`, `wujia_support` → 0 mã phiên trong code khối A.
- `portal_base/tests/test_scan_e3_pagination.py`: số call site pager `portal_debt` 2 → 3 (mobile payment-history có pager, §7b).

### 7b. `UI-DATALIST-001` — retest fail `/portal/debt/payment-history` mobile (commit `fix(debt)`, `wujia_portal_debt` 19.0.4.15.0)

- BA (History 26/09): mobile in đủ 12 giao dịch không pager (PC cùng dữ liệu 1–10/12); card 124px > trần 120.
- Sửa: controller trả **một** lát phân trang `payments` (`_pc_paginate`) cho cả 2 kênh; template mobile `t-foreach="payments"`
  + `dl_pager` gọi `wujia_portal_layout.wj_pagination`; card chỉ dùng hàng chuẩn `wj_list_card_row`: hàng 1 = phương thức •
  nội dung chuyển khoản, hàng 2 = ngày giờ | Số tiền (2 hàng `--inline`). **Không** CSS riêng của màn (lần đầu thử
  `.wj-debt-pay__meta .wj-lc__value{nowrap}` bị 2 test quét E5 chặn đúng luật LC-24 — bỏ, làm lại bằng bố cục).
- Đo (`wj_datalist`, em.hcm, 47 giao dịch/tháng): 390 và 360 **47 thẻ 124 → 10 thẻ 104**, pager hiện; với memo dài như UAT
  (23 ký tự) vẫn 104. Khối PC md5 giống HEAD‖ref ở `/`, `?page=2`, `?page_size=50`. Test mới: cấu trúc (d5g) + HttpCase 12
  giao dịch (10+2, `page_size=50` → 12 không nav). Suite **914/0/0**.
- Ledger: khoá `UI-DATALIST-001` lượt 2, `qa_sync --only UI-DATALIST-001` dry-run = 1 dòng Ready for Retest; **chưa `--apply`**
  (tiền lệ E6: chờ deploy).

## 8. Nợ / lệch plan — CHỈ GHI

1. `wujia_portal_sale` còn write ở update/remove/note; `portal_return` `rr.write` đính kèm — chờ phiên controller.
2. `_sql_constraints` 8 file Dev (+8 Thái) — chuyển `models.Constraint` khi có phiên "Odoo 19 deprecations".
3. Comment mã issue/phiên: 49 `.py` / 349 mọi file — dọn dần theo màn khi chạm Issue List, không mở phiên riêng.
4. `auto_install` ADR-027 ý #3 chưa áp đồng loạt; 3 ý ADR-027 chưa ghi + 7 câu hỏi BA (chapter 74).
5. `portal_base` chưa tự test một mình; `test_scan_e2b`.
6. M7: hook `imd_names(extra=)` chỉ chạy `pre_init` ⇒ test đơn vị không bắt được bỏ `extra`; `split_snapshot` là chốt duy nhất —
   ghi vào quy trình tách (chapter 74 bước 4).
7. Câu hỏi BA tồn F9–F13: phạm vi support theo người tạo · `publish_date` bài hẹn · KPI đổi trả có tính `reviewing` · phụ đề
   noti "còn hiệu lực" · tiêu đề exam "Khung giờ ngày —" · AJAX `/values` info_request · 4b D5h (3 hàng có nhãn cho card
   thanh toán ⇒ hạ nhịp ListCard chung).
8. Bàn giao anh Thái: R7 ×2 `_wj_ensure_contract` · 3 `mobile_*` auto_install · `wujia_franchise/tests/__init__.py` import file
   đã xoá · 8 file `_sql_constraints`.
9. Tooling: gid tab "UI Component" lệch · local `wujia_tea_19` lỗi thời · scratchpad lớn · `wujia_audit`/`metabase_connector`
   chưa phân tầng · DB copy không filestore phải xoá `ir_attachment` `/web/assets/%` mới đo browser được · `qa_sync.py` chạy
   từ gốc repo (symlink `~/wujia-devkit` làm lệch `LEDGER`) · `/app-assets/data/locales/en.json` 404.
10. UAT: nhóm "User" của Return/Exam/Notification 0 người — hỏi BA có cần gán không.

## 9. Bài học

- **Test quét component là hàng rào thật**: CSS "chỉ 1 dòng" cho một màn bị chặn ngay; cách đúng là đổi bố cục bằng hàng
  chuẩn của component. Đo lại 4 lần bố cục mới ra 104 ổn định ở 360 với dữ liệu dài như UAT.
- **Đo trên dữ liệu giống UAT**: memo 23 ký tự trên UAT làm bố cục "ngày giờ • memo" xuống dòng ở 360 mà seed 15 ký tự
  không lộ — phải mồi 1 bản ghi đúng độ dài rồi xoá.
- Bản sao DB không filestore ⇒ bundle `/web/assets` 500, mọi số Playwright sai; xoá attachment asset + restart trước khi đo.
- `md5` khối PC khác nhau chưa chắc là template: 1 bản ghi mồi lệch giữa 2 DB cũng đổi md5 — so lại sau khi xoá mồi.

## 10. Lệnh chạy lại

```
# server đo (HEAD ‖ ref)
odoo19/odoo-bin -c scratchpad/fra/head_srv.conf -d wujia_fra
odoo19/odoo-bin -c scratchpad/fra/ref_srv.conf  -d wujia_fra_ref
python3 scratchpad/fra/cmp_http.py                       # 17 route × 4 user, cmp2.json
python3 scripts/qa/wj_datalist.py --base http://127.0.0.1:8097 --portal-login em.hcm --password frapass \
  --routes /portal/debt/payment-history --breakpoints 390 360 --out scratchpad/fra/dl_after6_em.hcm.json
python3 scripts/qa/check_layers.py
# suite
odoo19/odoo-bin -c scratchpad/fra/test.conf -d wujia_fra_test -u <15 portal + 7 L2> --test-enable --stop-after-init
# đếm comment mã phiên (.py, không test/hook/manifest)
grep -rnE '#.*\b(F[0-9]{1,2}|FR-[A-Z0-9]+|E[1-8][a-z]?|WJ-[A-Z]+-[0-9]+|UI-[A-Z-]+-[0-9]+|CMP-[A-Z]+-[0-9]+|D[1-6][a-z]?|UAT-BH-[0-9]+)\b' \
  $(find custom/wujia_portal_* custom/wujia_{info_request,knowledge,support,notification,exam,return,order_window} -name '*.py' \
    -not -path '*/tests/*' -not -name hooks.py -not -name __manifest__.py) | wc -l
# sheet
python3 scripts/ba_spec/qa_sync.py --only UI-DATALIST-001      # dry-run; --apply SAU khi deploy
```

## 11. UAT

Chỉ đọc (RPC admin): 43 version khớp HEAD `164d8ec`; `wujia_portal_debt` **19.0.4.14.0** (fix §7b chưa lên). Lệnh cho chủ dự
án sau `git pull`: `-u wujia_portal_debt` (bắt buộc, có XML) · `-u wujia_info_request` (XML data noupdate — không đổi gì trên
DB đã cài, chạy cho đồng bộ) · các module chỉ đổi `.py` (`portal_base`, `wujia_notification`, `wujia_return`, `wujia_knowledge`,
`wujia_support`, `portal_notification`, `portal_support`) chỉ cần restart. Sau deploy: đổi `build_override` ledger thành ĐÃ DEPLOY
rồi `qa_sync.py --only UI-DATALIST-001 --apply`.
