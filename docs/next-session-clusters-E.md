# Cụm E1–E9 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-09-12 (10 issue `Ready for Dev` STT 128–139 trên `5. Issue List`,
tra bằng `issue_queue.py --dev` cùng ngày: 8 chuẩn component/UI portal + 2 backend). Kế hoạch
phiên: `~/.claude/plans/piped-tumbling-clarke.md`; chuẩn nghiệm thu ≥90% → §13
`wujia-compact-summary.md`. Lứa này chủ dự án chốt tên **cụm E** (không gọi "D7+").

**Cách dùng:** `/wujia-start` → nói **"làm cụm E&lt;n&gt;"** → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay. Xong cụm nào thì đánh ✅ + ngày + commit vào bảng "Tiến độ" bên dưới
và viết mục "🔴 Bài học E&lt;n&gt;" ngay dưới khối prompt (tiền lệ D).

**Hai quyết định chủ dự án chốt 12/09 (đừng hỏi lại):**
1. `WJ-SALE-002` (138) và `WJ-FRANCHISE-004` (135) **là việc của portal Dev**, sửa thẳng trên code
   đã có trên `main` (commit `8280459` view SO; module `wujia_franchise_contract` merge 09/09, chưa cài).
   Nguyên văn: *"2 cái đó của mình mà… mình sửa luôn cho đồng bộ, không có vụ sửa của người ta"*.
2. Thứ tự UI theo **blast radius tăng dần**: E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8. E9a/E9b (backend)
   độc lập với chuỗi UI, **chen ngay sau E1** vì BA chờ từ 02/09 và 08/09.

---

## Tiến độ

| Lượt | Issue (STT) | Module `-u` | Trạng thái |
|---|---|---|---|
| E1 | `UI-MOB-HOME-004` (133) + nợ 4 test D3 | `wujia_portal_layout` + `wujia_portal_debt` | ✅ 12/09 · `9354618` |
| E9a | `WJ-SALE-002` (138) | `wujia_sale` | ✅ 12/09 · `65c04c8` (merge upstream `ea9e5a6`) |
| E9b | `WJ-FRANCHISE-004` (135) | `wujia_franchise` + **`-u wujia_franchise_contract`** (UAT đã cài sẵn bản cũ) | ✅ 13/09 |
| E2a | `UI-STATUSBADGE-001` (128) — nền component + nhóm màn BA audit | `wujia_portal_layout`, `_base`, `_purchase_history`, `_delivery`, `_sale`, `_support` | ✅ 13/09 · `fa2ed9c` · 114→77 call site cũ, 65 call site mới |
| E2b | `UI-STATUSBADGE-001` (128) — 7 màn còn lại + 3 override lệch spec + đóng issue | `notification`, `exam`, `return`, `debt`, `knowledge`, `info_request`, `support` | ☐ (kiểm kê sẵn ở `docs/e2-statusbadge-inventory.md`) |
| E3 | `UI-PAGINATION-001` (130) | `wujia_portal_layout` + 9 module | ☐ |
| E4 | `UI-FILTER-001` (139) | `wujia_portal_layout` + 9 module | ☐ |
| E5 | `UI-LISTCARD-001` (136) | `wujia_portal_layout` + 8 module | ☐ |
| E6a / E6b | `UI-BUTTON-001` (132) | `wujia_portal_layout` + 13 module | ☐ |
| E7a / E7b | `UI-PAGECONTAINER-001` (129) | `wujia_portal_layout` + mọi module portal | ☐ |
| E8 | `UI-SIDEBAR-001` (131) | `wujia_portal_layout` + 12 module có `sidenav_inherit` | ☐ |

**Reconcile 12/09** (`git log --all -S"<ID>"` + `grep -rn "<ID>" custom/` cho cả 10 ID): 8 issue UI
= 0 code (chỉ hit trong `docs/` + 1 comment CSS `_components.css:3459` chờ spec Filter). 2 issue
backend **đã có code** — xem E9a/E9b. Không issue nào "đã fix mà sheet chưa sync" ⇒ không có lượt
B0 kiểu WJ-ORD-023.

---

## Luật chung cho MỌI lượt E (rút từ C, D — đọc trước khi mở bất kỳ cụm nào)

1. **Đo hồi quy trên DB có trạng thái module GIỐNG UAT** — tức **có cài** `wujia_franchise_inspection`
   + `wujia_portal_inspection` (luật 11/09; 4 test D3 đỏ chỉ lộ ở DB đó). Dựng DB copy cô lập, port
   riêng, không đụng `wujia_tea_19`/8019.
2. **Đếm call site bằng cấu trúc** (`lxml`, tổ tiên DOM, `t-foreach`, `scripts/qa/wj_inventory.py`),
   không grep tên lớp trần — D4 đính chính 3 lần, D5 đếm cấu trúc 0 lần. Mọi số trong file này đều
   kèm lệnh đếm lại; **số lệch thì sửa doc, không sửa số tay**.
3. **Không đụng hai module Khảo sát** (`wujia_portal_inspection`, `wujia_franchise_inspection`) — ghi
   `defer` + lý do vào bảng nghiệm thu. Mọi cụm dưới đây đều có dòng defer sẵn.
4. **Deploy = bump cả hai**: `?v=` của mọi file CSS nạp bằng `<link>` tay (`assets.xml`) **và**
   `__manifest__.py` của **mọi** module bị đụng (bẫy D4: 13/14 module không bump ⇒ restart không nạp XML,
   mất luôn phép kiểm deploy qua XML-RPC). Trước khi nói "đã lên main/UAT": `git fetch` + đọc
   `ir.module.module.latest_version` trên máy chủ (L17).
5. **Số đo Pass hết vẫn có thể đang giấu vỡ bố cục** (D3d/D3e) ⇒ mỗi lượt có **ảnh chụp** trước/sau
   ở ít nhất 2 khổ, và bảng đo phải có **mẫu khác 0** (D6: `--scope body`, chọn tài khoản có dữ liệu).
6. **Specificity**: hook spacing scope module phải viết `.wj-<component>.<lớp-của-mình>` (0,2,0);
   `:not()` mang độ đặc hiệu tham số; `web.assets_frontend` nạp SAU CSS custom (C6) ⇒ đo `c6_why`
   trước khi leo, không rải `!important`.
7. **Mutation test** cho guard mới: mỗi guard phải đỏ đúng 1 test khi phá; harness bắt buộc
   `assert s != before` (D6c M5); assert `in` khi chuỗi cũ là tiền tố chuỗi mới = assert rỗng (L8/D6c M9).
8. **Code ít, comment ≤1 dòng** (chủ dự án nhắc 2 lần). Fix ở gốc, 1 helper dùng chung, không đẻ
   file/harness rác trong repo (harness đo → `scratchpad/`, guard tái dùng → `scripts/qa/`).
9. Xong issue → đối chiếu **từng gạch đầu dòng** cột `Kết quả mong muốn` (đọc bằng `export?format=csv`,
   dòng tuyệt đối) ≥90% → ledger → `qa_sync.py --dry-run` → `--apply` → verify CSV **đúng ID dòng vừa ghi**.
   Dev không tự `Done`.

---

## ✅ 5 điểm tưởng là fork — chủ dự án chốt 12/09: **tự quyết, không chặn cụm nào chờ BA**

Soi kỹ thì BA đã viết sẵn luật ưu tiên, hoặc đó chỉ là việc đo. Ghi lý do vào cột FIX/IMPACT/LIMIT của
issue để BA thấy khi retest; chỉ Q5 gửi BA **một dòng FYI** (chạm màn đã retest), không chờ trả lời.

| # | Cụm | Vấn đề | Quyết định | Ghi ledger |
|---|---|---|---|---|
| Q1 | E4 | D6c nâng ô lọc mobile 8 màn lên 44 (mở rộng do chủ dự án, không phải BA ghi); FB-03/FB-04 (spec Filter, mới hơn) chốt **visual 38, vùng chạm ≥44** | Ô lọc: **visual 38 + hit-area 44** (padding/pseudo). Form (`wj-mform`) giữ 48 của BH-009 | IMPACT ở `UAT-BH-009`: ô lọc lùi 44→38 visual, vùng chạm giữ 44 |
| Q2 | E5 ↔ E7 | LC-08 12px trang danh sách vs CMP-PC-001 16px | BA đã tự giải ở acceptance LC-08 *"phạm vi list ưu tiên quyết định mới; default toàn Portal giữ nguyên"* ⇒ **danh sách mobile 12, còn lại 16** | E7 LIMIT: 1 biến thể gutter `--list` theo LC-08 (lệch chữ "không variant theo route" của PC-001, BA đã ưu tiên) |
| Q3 | E8 | BA: "Bù hàng không có menu"; source có `nav_item_return` "Đổi trả" | Không phải fork, là **phép đo** (E8a). BA đã chốt tên item "Đổi trả / Bù hàng" ⇒ có sẵn thì đổi nhãn + kiểm active route con | FIX: kết quả đo UAT + nhãn mới |
| Q4 | E9a | `fulfillment_route_id` không tồn tại (`grep -rn fulfillment_route custom/` = 0) | BA đã chỉ thị: *"Dev báo blocker, không tự tạo"* ⇒ bỏ cột/filter Tuyến cung ứng | LIMIT + blocker: cần field ở tab `1. Model/ Field` trước |
| Q5 | E9b | Wizard onboarding S57 nhập 2 ngày lên Store; FRANCHISE-004 cấm "hai nơi sửa cùng Start/End" | Wizard **giữ 2 ô ngày nhưng tạo hợp đồng đầu tiên** thay vì ghi lên Store — form BA nhìn không đổi, thoả cả hai spec | IMPACT ở cả `WJ-FRANCHISE-003` và `-004`; gửi BA 1 dòng FYI |

## E1 — Home mobile KPI Công nợ (`UI-MOB-HOME-004`, STT 133) + trả nợ 4 test D3 — `-u wujia_portal_layout`

> Prompt: "làm cụm E1". Lượt khởi động: 1 rule CSS, 1 route, và dọn nợ kỹ thuật để các cụm sau đo
> đúng môi trường.

**Gốc rễ (đã soi):** `custom/wujia_portal_layout/static/assets/css/_components.css:1114`
```
.wujia-mhome-kpi-value { font-size: 22px; font-weight: 700; line-height: 1.1; color: #FFF;
                         overflow-wrap: anywhere;  /* ô Công nợ in số tiền */ }
@media (max-width: 380px) { .wujia-mhome-kpi-value { font-size: 20px; } }   /* :1126 */
```
Chính `overflow-wrap: anywhere` (thêm ở C7 cho ô Công nợ) **cho phép** bẻ `-72449 $` thành `-7244` /
`9 $`. Ô Công nợ render từ `wujia_portal_debt/views/home_kpi_inherit.xml:19` (`_debt_kpi['remaining_label']`);
3 ô kia ở `wujia_portal_base/views/portal_home.xml:304/308/312`; tile inert `:320` (`—`).

**Việc:**
1. Mốc đo trước: `/portal` mobile 360/390/391 với tài khoản có công nợ dài (seed `-999,999,999 $` nếu
   UAT không có) — `pageH`, `getBoundingClientRect` của 4 `.wujia-mhome-kpi-value`, số dòng
   (`getClientRects().length`).
2. Sửa **một** rule: bỏ `overflow-wrap:anywhere`; thêm `white-space: nowrap; font-variant-numeric:
   tabular-nums; min-width: 0` (cả ô cha `.wujia-mhome-kpi`); cỡ chữ về **một token responsive dùng
   chung cho cả 4 giá trị** (`clamp()` hoặc breakpoint) — BA cấm giảm riêng Công nợ. Không đổi nhãn,
   thứ tự, dữ liệu.
3. Nợ D3: dựng DB copy **có cài** `wujia_franchise_inspection`, chạy
   `--test-tags /wujia_portal_layout:TestCardHeaderCallSites,TestCardHeaderD3eLayout,TestCardHeaderD3Review`
   → 4 test đỏ (danh sách ở `next-session-clusters-D.md` mục 11/09) → sửa **phía portal** (test hoặc
   template portal), không sửa module khảo sát.
4. Hồi quy: Home mobile 3 khổ + `wj_measure` 3 route × 2 khổ; 0 tràn ngang, 0 JS error.

**Ràng buộc đo được:** 4 chỉ số 1 hàng ở 360/390/391 · 4 giá trị cùng `font-size/weight/line-height`
(đọc computed) · Công nợ + ký hiệu tiền **1 dòng** · card không cao thêm so với mốc · `-999,999,999 $`
vẫn 1 dòng · 4 test D3 xanh trên DB giống UAT.

**Ledger:** `UI-MOB-HOME-004` → `Ready for Retest`; bump `_components.css ?v=` + `wujia_portal_layout` patch.

### 🔴 Bài học E1 (làm 12/09/2026, `9354618`, `Ready for Retest`)

**1. Prompt E1 ở trên chỉ soi ra 1 trong 2 tầng gốc rễ — và tầng bị bỏ sót mới là tầng chính.**
Tầng CSS (`overflow-wrap: anywhere`) chỉ *cho phép* bẻ dòng. Thứ *tạo ra* chuỗi 8 ký tự là
`_short_amount()` (`wujia_portal_debt/models/wujia_portal_debt.py`): nó so bậc **trực tiếp trên giá
trị** (`amount >= 1_000_000`), nên **mọi số âm** rớt qua cả hai bậc xuống nhánh `'%d %s'` và in nguyên
`-72449 $` — đúng chuỗi trong ảnh BA, trong khi `+72449` chỉ in `72k`. Vá riêng CSS như prompt viết thì
chuỗi dài **tràn ngang** thay vì xuống dòng, tệ hơn trạng thái BA báo. ⇒ **Luật:** với issue "chữ bị
cắt/bẻ", luôn truy ngược tới chỗ *sinh ra chuỗi*, không dừng ở rule CSS đang cho phép bẻ.

**2. Số âm là ca bị bỏ quên có hệ thống trong mọi hàm rút gọn.** Cùng lỗi hình dạng còn nằm ở chuỗi
`('%.1f' % x).replace('.', ',').replace(',0', '')` — nó xoá **mọi** cụm `,0` chứ không chỉ phần thập
phân (`1,05tr` → `15tr`). Đã đổi sang cắt đuôi `.0` **trước** khi đổi dấu thập phân. Thêm bậc `tỷ`.

**3. Đo số dòng bằng `getClientRects().length` trên flex item luôn ra 1 — sai hoàn toàn.**
`.wujia-mhome-kpi-value` là flex item (block) ⇒ 1 rect kể cả khi text 3 dòng. Phải đo bằng
`document.createRange().selectNodeContents(el)` **cộng** một phép độc lập `round(height/lineHeight)`.
Chỉ sau khi đổi cách đo mới thấy trạng thái BEFORE thật: `-72449 $` = **2 dòng**, `-999999999 $` =
**3 dòng** — trước đó harness báo "1 dòng, không lỗi" và gần như làm mình kết luận issue đã tự hết.
Tương tự, `scrollWidth == clientWidth` **không** chứng minh không tràn (làm tròn block) ⇒ so
`Range.getBoundingClientRect().width` với bề ngang ô.

**4. Mutation phải chứng minh chuỗi bị phá là DUY NHẤT (tái hiện đúng bẫy D6c M5).** M1/M2 báo 0 test
đỏ; thủ phạm là `'    white-space: nowrap;'` xuất hiện **25 lần** trong `_components.css`, `replace(old,
new, 1)` vá nhầm rule khác mà `assert after != before` vẫn qua. Harness nay bắt buộc
`assert before.count(old) == 1`, và neo mutation vào **cặp dòng** `white-space + font-variant-numeric`.

**5. "4 test D3 đỏ do DB chưa cài khảo sát" (phỏng đoán 11/09) là SAI.** Thủ phạm là chính lượt
**D4e2 `3d83af2`**: đổi `card-header` → `wj-surface-card__head`, `div.wujia-mdash-card` → `t-call
wj_surface_card`, `.card-body` → `.wj-surface-card__body`, và gỡ `margin-top: 18px` của
`.wj-exam-pc-sumlist`. LIMIT của chính commit đó đã **mô tả sai** nguyên nhân 2 test nó vừa làm đỏ.
⇒ **Luật:** LIMIT nói "đỏ do môi trường" phải kèm `git log -S` chứng minh, không thì lượt sau mất công
dựng lại cả DB để phát hiện là nội tại.

**6. Test của mình tự làm hỏng test của mình.** Script seed `scratchpad/e1/seed_debt_demo.py` tạo bank
`0123456789` với `sequence: 1`, làm 2 test bank cũ đỏ (`'0123456789' != 'ACC-WIN'`) — đã có test khác
ghi sẵn cảnh báo hazard này mà vẫn sập. Đã sửa 3 test: tắt `portal_payment_enabled` của **mọi** bank
sẵn có trước khi tạo bank test, thay vì tin vào `sequence` (ties → `id` nhỏ hơn thắng).
**Run đối chứng** cùng cây mã trên DB chưa seed (0 đỏ/271) là thứ chứng minh 2 lỗi này do seed.

**7. `pkill -f` giết luôn shell đang chạy nó** (`pgrep -f` khớp cả dòng `bash -c`) ⇒ exit 144. Dùng
`ps -eo pid,args | grep odoo-bin | grep <db> | grep -v 'bash -c' | awk '{print $1}' | xargs -r kill`.

**8. `qa_sync.py` ghi lệch cột vì BA chèn cột giữa bảng.** `C_ODOOFIT` cứng `17` — BA chèn
`Primary Feature ID` nên `Odoo Fit` trượt sang `18`, qa_sync ghi `Custom` lấn vào
`Related Reference IDs`. Đã dọn ô và đổi `qa_sync.py` sang **dò index theo tên tiêu đề** mỗi lần chạy
(thiếu tiêu đề thì dừng, không ghi theo index cũ). Đọc tab cũng có bẫy: `gviz?sheet=ISSUE HISTORY` sai
tên thì Google **im lặng trả tab đầu tiên**; tên thật `7. ISSUE HISTORY` (đã ghi vào `sheet_io.py`).

**9. Soi UAT sau khi anh báo "deploy rồi" ⇒ deploy CHƯA vào — và LIMIT tôi vừa viết cũng sai một ý.**
Kiểm 3 tầng chứ không tin lời: `ir.module.module` qua XML-RPC còn `wujia_portal_layout 19.0.47.0.0`
+ `wujia_portal_debt 19.0.4.5.0`; tải thẳng `_components.css` từ UAT thấy vẫn `overflow-wrap: anywhere`,
`Last-Modified: 10/09 15:59`, `Server: Werkzeug` (không proxy ⇒ không phải cache); trang vẫn nhả
`?v=1281`. ⇒ `git pull` chưa tới thư mục mà service đang chạy (nếu pull rồi mà quên restart thì tệp
CSS tĩnh **đã** mới, vì Odoo đọc thẳng từ đĩa). **Luật:** "đã deploy" phải xác minh bằng *phiên bản
mô đun trong DB* **và** *`Last-Modified` của tệp tĩnh*, không bằng mắt nhìn trang.
Đo chỉ-đọc tại chỗ (`scratchpad/e1_uat_check.py`) còn cho một thứ quý hơn: **UAT CÓ cửa hàng âm công
nợ** — `[HCM-01] TP HCM Quận 1` đang `-72449 $`, bẻ thành `-7244`/`9 $`, **trùng từng ký tự với ảnh
BA**. Tức LIMIT tôi viết ("UAT không có cửa hàng nào đang âm nên không đo được ở đó") là **sai**; đã
sửa lại ledger + ô Ghi chú trên sheet, và đổi RETEST sang chỉ đích danh cửa hàng đó cho BA.
**Luật:** đừng suy ra "UAT không có dữ liệu ca đó" từ việc DB dev không có — mở UAT ra xem.

**10. Deploy thật + nâng cấp mô đun tay, đo lại trên UAT ⇒ PASS.** Vòng 2: `git pull` đã tới
(`_components.css` trên UAT `Last-Modified 12/09 03:38`, đã có `nowrap`) nhưng **mô đun vẫn 47.0.0 /
4.5.0** ⇒ template còn nhả `?v=1281`. Đây là trạng thái "pull rồi, chưa `-u`" — phân biệt được với
"chưa pull" bằng đúng `Last-Modified` của tệp tĩnh. Nâng cấp tay qua XML-RPC
`ir.module.module.button_immediate_upgrade([700, 667])` (8,5s, trả `ir.actions.act_url`), sau đó 16
mô đun portal đều `installed` (`wujia_portal_remediation` `uninstalled` là có sẵn, không phải do lượt
này). Đo lại trên UAT, `[HCM-01]` âm 72.449: **`-72k`, 1 dòng, cả 3 khổ**; `ws=nowrap`,
`ovw=normal`, `fvn=tabular-nums`; hero height **216,19 → 194,19** @360 và **198,47 → 174,28**
@390/391 (thấp đi đúng 1 dòng); `overflowX=0`; 0 JS error. Soi thêm `/portal/debt`: vẫn in **đủ số**
`72.450,00 $` — rút gọn không lây sang màn phải in đủ.

**11. IMPACT tôi viết rộng hơn sự thật.** Tôi ghi "khay Thêm của thanh dưới cũng đổi vì dùng chung
hàm". Đọc lại `bottomnav_inherit.xml:30` thì khay đó chỉ `t-out` **`overdue_count`**, còn
`remaining_label` của `get_shell_badge()` **không template nào render**. ⇒ bề mặt đổi thật sự **chỉ
có 1**. Đã sửa ledger + ô Ghi chú. **Luật:** "hai chỗ dùng chung hàm" chưa đủ để kết luận hai bề mặt
đổi — phải `grep` xem khoá trả về đó có được render không.

**Số đo nghiệm thu (7/7 PASS, DB copy có cài khảo sát, cổng 8078):** 4 tile 1 hàng ở 360/390/391 ·
cùng font `20px/700/22px` @360 và `22px/700/24.2px` @390-391 · Công nợ **1 dòng** (2 phép đo độc lập)
với cả `-72449` và `-999999999` · text rộng nhất 48,56/63px (không tràn, `overflowX=False` 9/9) ·
hero height `238.28/260.28` → **`216.28`** = đúng mốc ca thường (card **không** cao thêm) · 0 JS error ·
hồi quy 4 route × 2 khổ: 0 dòng đổi chiều cao, 0 bản ghi mất · 339/339 test xanh.

---

## E9a — Danh sách "Đơn hàng Ngô Gia" (`WJ-SALE-002`, STT 138) — `-u wujia_sale`

> Prompt: "làm cụm E9a". Backend, độc lập chuỗi UI. Code có sẵn: `custom/wujia_sale/views/sale_order_views.xml:54-110`
> (`8280459`) + test `custom/wujia_sale/tests/test_wujia_order_view.py` **đang đỏ**.

**Hiện trạng ↔ spec BA (14 cột, 10 tiêu chí):**
- Code hiện **kế thừa thẳng `sale.sale_order_tree`** (priority 20) ⇒ đổi **mọi** action SO chuẩn.
  Spec: *"view riêng kế thừa… không sửa trực tiếp view chuẩn, không ảnh hưởng action Sales Order khác"*
  ⇒ đổi thành **list view độc lập** (`<list>` mới, không `inherit_id`) gắn vào action "Đơn hàng Ngô Gia"
  (action đã có: "Wujia Sales Orders" `:77`, cần đổi tên + `view_ids`/`search_view_id` riêng).
- Cột đã có: `create_date`, `franchise_id`, `area_id`, `is_portal_order`, `is_return_order`,
  `total_planned_weight`, `batch_id`. **Thiếu:** `warehouse_id`; nhãn `create_date`="Ngày đặt hàng",
  `date_order`="Ngày xác nhận" (widget datetime, tz user); thứ tự 13 cột đúng spec; ẩn
  `user_id/activity_ids/team_id/tag_ids` khỏi mặc định; `invoice_status/commitment_date/expected_date`
  `optional="hide"`; `state` badge, `amount_total` monetary; decoration hủy giữ của Odoo.
- Search view (`:101`, inherit `view_sales_order_filter`): cần tìm mã SO/cửa hàng/Batch; filter Đơn Portal
  · Đơn bù · **Đơn thủ công** (`is_portal_order = False and is_return_order = False`) · trạng thái · khu
  vực · kho · **chưa có Batch** (`batch_id = False`); group by cửa hàng/khu vực/trạng thái/kho/Batch.
  Field/domain thật, không field mới.
- `fulfillment_route_id`: **không tồn tại** → bỏ cột/filter, ghi blocker vào LIMIT (Q4), không tự tạo.
- Test: sửa `priority 99` cho khớp; thêm assert **arch `sale.sale_order_tree` không đổi** (đọc
  `get_views` của action chuẩn trước/sau) — đó là bằng chứng cho tiêu chí 1/9.

**Ràng buộc đo được (XML-RPC chỉ đọc trên DB copy):** action mới trả đúng list view riêng với 14 cột
theo thứ tự; action `sale.action_orders` trả arch **y hệt** trước; filter "chưa có Batch" chỉ ra
`batch_id = False`; 4 state × 3 nguồn đơn (portal/bù/thủ công) hiện đúng; user bị giới hạn company
không thấy thêm record. Hồi quy: test `wujia_sale` + `wujia_portal_sale` 0 đỏ.

**Ledger:** `WJ-SALE-002` → `Ready for Retest`; bump `wujia_sale`.

---

### 🔴 Bài học E9a (làm 12/09/2026, `65c04c8`, `Ready for Retest`, **chờ deploy UAT**)

1. **`mode primary` là lời giải cho mâu thuẫn "kế thừa" ↔ "không ảnh hưởng action khác"** — bản
   phân cụm 12/09 định dựng `<list>` độc lập, nhưng primary vừa giữ đúng chữ của BA vừa thừa
   hưởng những thứ vô hình mà bản dựng tay dễ quên: `currency_id` (widget monetary cần),
   `message_needaction`, `decoration-muted` đơn huỷ, nút header *Create Invoices*. Tiền lệ nằm
   ngay trong core: `sale.sale_order_view_search_inherit_sale`.
2. **Cột `optional="hide"` không render ⇒ thứ tự nhìn thấy chỉ phụ thuộc cột đang hiện.** Nhờ
   vậy ra đúng 13 cột theo thứ tự BA mà **không cần `position="move"`** một lần nào — chỉ chèn
   field + đổi thuộc tính `optional`.
3. **Mutation "gỡ một dòng XML" có thể là phép phá RỖNG** (họ D6c M5, biến thể mới): bỏ dòng
   `<field name="mode">primary</field>` ra khỏi bản ghi thì Odoo **không ghi lại** cột đó, giá trị
   cũ trong DB còn nguyên ⇒ 0 test đỏ mà guard vẫn tốt. Phải phá bằng **giá trị đối lập**
   (`extension`) mới đo được. `assert s != before` không cứu được ca này vì file *có* đổi — chỗ
   không đổi là **cơ sở dữ liệu**.
4. **Thêm msgid vào `vi_VN.po` là chưa đủ.** `PoFileReader` (`odoo/tools/translate.py`) gọi
   `pofile.merge(<module>.pot)`; `polib.merge` đánh **obsolete** mọi entry vắng mặt trong `.pot`
   và `__iter__` bỏ qua entry obsolete — **im lặng tuyệt đối, không một dòng log**. `.pot` của
   `wujia_sale` đứng im từ 11/08 nên menu *Đơn hàng Ngô Gia* tuy đã có dòng dịch vẫn chưa bao giờ
   ra tiếng Việt trên UAT. Cách đúng: `odoo-bin i18n export -c <conf> -d <db> -o <path> <module>`
   rồi ghi đè `.pot`; sau đó `-u <module>` **không cần** `--i18n-overwrite`. Bẫy này áp cho **mọi
   module** — lứa E còn lại ai thêm nhãn mới đều phải xuất lại `.pot`.
5. **Lấy cột hiển thị phải đo trên arch ĐÃ hợp nhất** (`get_view`), không đọc `arch_base` của bản
   ghi — bản ghi primary chỉ chứa phần chèn thêm, đọc thẳng là thấy 5 field thay vì 13.
6. Bản sao DB dùng để chụp màn phải **copy kèm filestore** và **xoá attachment gói giao diện**
   (`DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%'`), nếu không backend trả 500 cho cả
   ba gói và Playwright chỉ thấy trang trắng.
7. **Hệ quả của bài học 4 khi merge:** vòng merge `origin/main` ngày 13/09 cho thấy `.pot` xuất tay
   là **con dao hai lưỡi** — anh Thái thêm ~30 msgid cho *Báo cáo cung cầu kho xuất* mà `.pot` E9a
   (xuất 12/09) chưa có, nên nếu giữ `.pot` thì đúng ~30 dòng dịch đó bị nuốt im lặng. Anh Thái đã
   **xoá** `custom/wujia_sale/i18n/wujia_sale.pot` ở `c64de50`; lượt merge **nhận xoá**: không có
   `.pot` ⇒ `PoFileReader` bỏ qua bước merge ⇒ **mọi** entry trong `.po` được nạp. Kết luận cho lứa
   E còn lại: **một là không giữ `.pot`, hai là bắt buộc xuất lại `.pot` trong CÙNG commit với mọi
   lần thêm nhãn** — giữ `.pot` cũ là tệ nhất trong ba lựa chọn. Các module còn `.pot`
   (`wujia_franchise`, `wujia_franchise_inspection`, `wujia_portal_knowledge`,
   `wujia_portal_support`) đang mang đúng bẫy này, cần rà ở một lượt riêng.
8. **Lỗi upstream ghi nhận, KHÔNG tự sửa:** `custom/wujia_sale/tests/test_wujia_supply_demand_report.py:40`
   (`setUpClass`) tạo `stock.quant` cho sản phẩm không khai `is_storable=True` ⇒ Odoo 19 mặc định
   `consu` ⇒ `ValidationError: Quants cannot be created for consumables or services.` Đây là test
   **mới của anh Thái** ở `c64de50`, đỏ độc lập với E9a (E9a không đụng product/quant). Sau merge:
   `wujia_sale` + `wujia_portal_sale` = **31 test, 0 failed, 1 error**, error duy nhất là ca này.
   Để anh Thái sửa (một dòng `'is_storable': True` ở cả hai `Product.create`) — báo, không sửa hộ.


## E9b — Hợp đồng nhượng quyền nhiều kỳ (`WJ-FRANCHISE-004`, STT 135) — `-u wujia_franchise` + `-i wujia_franchise_contract`

> Prompt: "làm cụm E9b". **Schema change + migration** — đọc `docs/merge-thai-2026-09-09.md` (rủi ro
> khi `-i`). Q5 đã chốt: wizard onboarding tạo hợp đồng đầu tiên. Cụm duy nhất có module mới ⇒ deploy UAT phải `-i`.

**Hiện trạng:** module `wujia_franchise_contract` (merge 09/09) có model + view, **chưa cài** vì nó biến
`franchise_start_date/franchise_end_date` của `wujia.franchise.management` thành **computed store
readonly**, trong khi `main` đang **ghi** hai field đó ở: wizard onboarding S57 (`WJ-FRANCHISE-003`),
CSV bootstrap `wujia_franchise/models/wujia_franchise_management.py:371`, `sample_data.xml`, ~8 file
test. Cài là hỏng onboarding + test.

**Việc (đối chiếu 4 khối GIVEN/WHEN/THEN của BA):**
1. Kiểm kê chỗ ghi 2 field ngày: `grep -rn "franchise_start_date\|franchise_end_date" custom/ --include=*.py --include=*.xml --include=*.csv`
   → bảng "nơi ghi → cách chuyển sang tạo contract".
2. Model hợp đồng: Store (bắt buộc) · số HĐ (nhập, trống ⇒ sequence) · start/end (bắt buộc, `end ≥ start`)
   · state `draft/effective/expired/cancelled` **tính theo ngày** (cron daily + compute, perf-first) ·
   note · attachment chuẩn (`mail.thread` đủ, không DMS). Constraint **không chồng lấn** khoảng ngày giữa
   các HĐ non-cancelled cùng Store (SQL/`@api.constrains` + index `(franchise_id, start, end)`).
   Không xoá cứng HĐ đã effective (`unlink` chặn → dùng cancel/archive).
3. Store Master: smart button + tab "Hợp đồng" (count), khối read-only HĐ hiện hành + ngày còn lại;
   2 field ngày cũ → related/readonly, **bỏ khỏi form nhập**.
4. **Migration idempotent** (`migrations/<ver>/post-migrate.py`): mỗi Store có ngày cũ → tạo **≤1**
   contract; chạy lại **0 trùng** (kiểm bằng `search_count` trước/sau lần 2).
5. Vá 4 nơi ghi: wizard onboarding tạo contract đầu tiên (Q5), bootstrap CSV/seed/test chuyển sang
   tạo contract. Hết hạn chỉ cảnh báo — **không** đổi `status` Store, không `portal_locked`, không chặn đặt hàng.
6. Test: 18 test onboarding S57 vẫn xanh + test mới cho 4 khối BA + mutation cho constraint chồng lấn.

**Ràng buộc đo được:** tạo HĐ chồng ngày → `ValidationError`; HĐ lịch sử + tương lai không chồng → lưu
được; hôm nay trong khoảng → Store hiện đúng HĐ + số ngày còn lại; qua end → `expired` + cảnh báo, Store
`status`/portal không đổi; migration ×2 = số contract không đổi; onboarding wizard chạy tay 6/6 như S57.

**Ledger:** `WJ-FRANCHISE-004` → `Ready for Retest`; cột Build/Deploy ghi rõ **`-i wujia_franchise_contract`**
+ bump `wujia_franchise`.

### 🔴 Bài học E9b (13/09/2026)

1. **`-i` hay `-u` phải ĐO trên máy chủ, đừng suy từ git.** Kế hoạch ghi `-i wujia_franchise_contract`
   vì `main` chưa từng cài. Đo XML-RPC UAT ra **`installed`, `19.0.1.0.0`** — chủ dự án đã tự cài
   bản của anh Thái từ 09/09. Sai một chữ này là mất nguyên đường migration: `-i` trên module đã cài
   **không chạy lại** `post_init_hook`, còn `migrations/<ver>/` thì chỉ chạy khi `-u`.
2. **Đổi field thường → stored computed là XOÁ dữ liệu cũ trước khi hook chạy.** `post_init_hook` đọc
   `store.franchise_start_date` qua ORM sẽ thấy `False`. Phải `cr.execute` đọc **thẳng cột**, và đọc
   **TRƯỚC mọi lệnh ORM** (kể cả `ir.config_parameter.get_param`) vì bất kỳ lệnh nào cũng có thể flush
   compute đè lên cột.
3. **Cột `state` cũ mang thông tin không tái tạo được từ ngày.** `cancelled` là quyết định của người,
   không suy ra từ `start/end`. Chuyển `state` sang computed mà không có `pre-migrate` **đắp cột
   `is_cancelled` từ `state` cũ** là im lặng bỏ huỷ. Rehearsal nâng cấp bắt được — test không bắt được,
   vì test luôn chạy trên schema mới.
4. **Recompute dây chuyền không tự lan trong migration.** `post-migrate` ép tính `current_contract_id`
   là chưa đủ: `franchise_start/end_date` phụ thuộc nó vẫn giữ giá trị cũ. Phải `add_to_compute` +
   `flush_recordset` cho **cả ba** field theo đúng thứ tự.
5. **`migrate()` ở build Odoo 19 này bắt buộc chữ ký `(cr, version)`.** Viết `(env, version)` là
   `TypeError` giữa lúc nâng cấp — registry hỏng, DB kẹt nửa chừng.
6. **`assertRaises` trần là assert rỗng (họ L8, lần thứ hai).** `test_03` bắt `ValidationError` và
   **pass cả khi gỡ hẳn guard `end ≥ start`** — mutation M6 ra 0 đỏ mới lộ. `@api.constrains` chạy lúc
   flush nên một ngoại lệ khác đã lấp chỗ. Vá: `assertRaisesRegex` + `flush_all()` trong khối.
   Mutation M12 cũng sống sót vì **không có test nào** canh "HĐ đã huỷ không được làm HĐ hiện hành".
7. **Code chết không lộ ra bằng đọc diff.** `_cron_update_contract_states` của bản cũ trông hoàn chỉnh
   nhưng `data/` **không có record `ir.cron` nào** ⇒ chưa từng chạy, `expired` chưa từng tự lên.
   Kiểm bằng `grep -rn "ir.cron" <module>/`, đừng tin tên hàm.
8. **Luật "đo hồi quy trên DB giống UAT" cứu một lần nữa, nhưng đồng hồ cũng là biến.** Đỏ thứ 6
   (`TestWujiaOrderView.test_06`) do khung giờ đặt hàng 10:00–04:00, mốc chạy 03:56 lọt, lượt sau 04:01
   rớt. Chỉ **run đối chứng trên chính DB mốc cùng thời điểm** mới phân biệt được với hồi quy thật.

---

## E2 — StatusBadge `CMP-SB-001` (`UI-STATUSBADGE-001`, STT 128) — `-u wujia_portal_layout` + 10 module

> Prompt: "làm cụm E2". Atom đầu tiên của lứa E; E5 ListCard tiêu thụ nó (LC-04).

**Gốc rễ (đã soi):** hai họ tĩnh + mapping động rải trong Python.

| Họ | Chỗ (đếm thẻ có class, lệnh bên dưới) | Ghi chú |
|---|---|---|
| `wujia-badge` + `-info/-muted/-success/-danger/-warning` | 52 thẻ tĩnh | mobile + dashboard, radius 999, 26,8px |
| `wj-pc-badge` + `--done/--pending/--cancel/--confirmed/--warn/--sent/--transit` | 46 thẻ tĩnh | PC list, 28px/13/600/r14 = **đã đúng geometry BA** |
| `wj-debt-badge`, `wj-debt-pc-badge` | 12 | debt tự dựng |
| `state-badge` | 3 | **Khảo sát → defer** |
| **Động trong controller** | 75 chuỗi: `wujia_portal_base/controllers/utils.py` 26 · `exam` 19 · `return` 14 · `support` 8 · `info_request` 5 · `notification` 3 | `utils.py:389-431` **đã gom** map `(nhãn, class)` cho SO/chuyến/bù hàng/support ⇒ **seam có sẵn** |

Static theo file: `portal_notification.xml` 13 · `portal_franchise_information.xml` 12 · `portal_exam.xml` 11 ·
`pc_preview.xml` 9 · `portal_knowledge.xml` 8 · `portal_debt.xml` 8 · `portal_home.xml` 7 ·
`portal_return_detail.xml` 6 · `portal_support.xml` 5 · `profile_page.xml` 5 · `portal_return_list.xml` 4 ·
`portal_history.xml` 4 · `portal_info_request_list.xml` 3 · `portal_delivery.xml` 2 · 4 file ×1.
(Inspection 9 → defer.)

**Bằng chứng lỗi BA nêu nằm ở Python, không ở CSS:** `utils.py:391` `'sale': ('Đã xác nhận', 'wujia-badge-success')`
— BA: "Đã xác nhận" phải **info xanh dương**.

**Ngoài phạm vi (không đổi byte computed):** `wujia-store-role-badge` (Role) · `wujia-header-badge` (Count)
· `wj-filter-chip` · `wujia-mknow-badges` (Category) · `wujia-mexam-stepbadge` · `wujia-mdelivery-badge`
(kiểm: là state hay count?) · `wj-exam-pc-rbadge` (kiểm).

**Lệnh đếm lại:**
```
grep -rhoE 'class="[^"]*"' custom/wujia_portal_*/views/ | grep -oE '\b[a-z0-9_-]*badge[a-z0-9_-]*\b' | sort | uniq -c | sort -rn
grep -rn "badge" custom/wujia_portal_*/controllers/*.py | grep -oE "['\"][a-z_-]*badge[a-z_-]*['\"]" | sort | uniq -c
```

**Việc:**
1. **E2 = 1 lượt kiểm kê + 1 lượt code** nếu bảng mapping trạng thái > 40 dòng; ngược lại gộp. Kiểm kê:
   bảng `module · model · state · nhãn hiện tại · class hiện tại · variant BA` (7 variant) — lấy nhãn
   từ map thật trong controller, không từ mô tả BA.
2. CSS: `.wj-status-badge` + `--neutral/--info/--pending/--processing/--success/--danger/--feedback`
   trong `_components.css` (token màu vào `_variables.css`, không hex ở call site). Geometry: 28 ×
   ≥84, `padding 0 14px`, r14, 13/600, `line-height 1`, `white-space nowrap`, không border/shadow. **Một
   class cho cả PC/mobile**, không biến thể theo route/breakpoint.
3. Python: giữ các map ở `utils.py:389-431`, đổi giá trị class sang `wj-status-badge--<variant>`; **kéo
   map của exam/info_request/notification/debt về cùng chỗ** (1 nguồn). Template chỉ `t-att-class`.
4. Migrate 110 thẻ tĩnh + 75 chuỗi động; xoá rule `wujia-badge*`/`wj-pc-badge*`/`wj-debt-*badge` khi
   `wj_inventory.py` ra 0 (trừ inspection).
5. Guard `scripts/qa/wj_statusbadge.py`: đo computed 5 khổ (1440/1024/992/991/390/360) mọi
   `.wj-status-badge`: height/minW/padding/radius/font, `getClientRects().length == 1`, màu đúng variant;
   và **kiểm tra chéo** Role/Count/Chip/Category không đổi computed so với mốc.
6. LIMIT có thể gặp: cột hẹp bảng PC với min-width 84 + nhãn ZH — đo trước ở `/portal/purchase-history`.

**Ràng buộc đo được:** 100% badge trạng thái trong scope là `.wj-status-badge` (inspection defer ghi số) ·
28/84/14/14/13-600 · 0 xuống dòng, 0 ellipsis, 0 tràn ngang 5 khổ · "Đã xác nhận" info · contrast AA ·
5 họ ngoài phạm vi 0 đổi · test 0 đỏ trên DB có khảo sát.

### 🔴 Bài học E2a (13/09)

1. **Sửa ở Python, không ở CSS.** Lỗi BA nêu nằm ở `utils.py` `'sale': (…, 'wujia-badge-success')`.
   Đổi 1 dòng map là PC + mobile hết lệch cùng lúc; nếu chữa bằng CSS thì mỗi màn phải chữa một lần.
2. **Đếm thật trước khi nhận lượt.** File này ghi "110 + 75"; đếm bằng `lxml` ra **114 element / 8 họ**,
   trong đó 21 là defer hoặc họ BA loại ⇒ chia E2a/E2b là đúng.
3. **Badge mới cao hơn badge cũ ⇒ hàng flex xung quanh bị kéo.** `.wujia-maccount-badgerow` để
   `align-items: stretch`, chip mã cửa hàng (ngoài phạm vi) phình 26,8 → 28. Chỉ SB-3 (kiểm chéo họ
   ngoài phạm vi) bắt được — số đo của chính component vẫn Pass sạch.
4. **Restart KHÔNG nạp lại XML.** Một lượt đo cho ra badge vai trò mang class `wj-status-badge--info`
   trong khi file ghi `wj-pc-badge--confirmed`: arch trong DB cũ hơn file. Mọi lần đo phải đi sau `-u`,
   không chỉ sau restart, nếu không sẽ điều tra nhầm một "hồi quy" không có thật.
5. **Danh sách OUT phải neo theo container.** `.wj-pc-badge--confirmed` vừa là RoleBadge (profile,
   thành viên) vừa là StatusBadge (purchase-history) — không neo thì migrate đúng cũng báo đỏ.
6. **Spec BA tự mâu thuẫn thì tách ra mà xử, đừng chọn bừa một vế.** Vừa đòi WCAG AA vừa đưa 7 cặp hex
   mà 5 cặp đo dưới 4.5. Cách giải: **nền = hex BA (nhận diện), chữ = làm đậm tối thiểu cùng tông
   (đạt AA)** — vế nào của BA cũng còn. Test phải khoá **hai chiều** (nền đúng hex + chữ ≥4,5 +
   lệch hue ≤12°), nếu không thì lần sau ai đó đổi bừa màu vẫn xanh. Với mapping thì ngược lại:
   nhãn nào BA đã nêu thì theo đúng bậc BA, kể cả khi hai nhãn cạnh nhau trùng màu.

---

## E3 — Pagination `CMP-PGNT-001` (`UI-PAGINATION-001`, STT 130) — `-u wujia_portal_layout` + 9 module

> Prompt: "làm cụm E3". Chạy sau E2 (không phụ thuộc mã, nhưng chung lượt deploy nếu gộp).

**Gốc rễ (đã soi):** 10 họ pager, **seam có sẵn** — `wujia_portal_layout/views/wj_data_list.xml:13/36`
slot `dl_pager` (markup thô, D5 cố ý để pager ngoài viewport component) ⇒ dựng template
`wj_pagination` rồi truyền vào slot; call site nào chưa qua `wj_data_list` thì gọi thẳng.

| Họ | Chỗ | File |
|---|---|---|
| `wj-pc-pagination` (+`__count/__size/__size-form`) | 10 | history, notification, delivery, support, knowledge, return… |
| `wj-debt-pc-pagination` (+4 con) | 2 | `portal_debt.xml` |
| Bootstrap `wujia-pagination`/`pagination` | 5 + 5 | knowledge, info-request, franchise-info… |
| `wj-exam-pc-pagination`, `wj-pc-order-pager` | 1 + 1 | exam, catalog |
| mobile `wujia-mhist-pager` 3 · `wujia-mknow-pager` 1 · `wujia-mnoti-pager(-btn)` 3 · `m_pager` slot 4 | 11 | |
| `page-nav-btn` | 6 | **Khảo sát → defer** (nhưng là **mẫu mobile** BA chọn: Prev + "Trang x/y" + Next) |

13 file: `portal_franchise_information · portal_debt · portal_delivery · portal_exam ·
portal_info_request_list · portal_knowledge · pc_preview · wj_data_list · portal_notification ·
portal_history · portal_return_list · portal_order_catalog · portal_support` (+ inspection list, defer).
Form page-size hiện là `<form method="get" class="wj-pc-pagination__size-form">` ở history `:94`,
notification `:103` — **query-string tự xây theo route** (rủi ro BA nêu: đổi trang làm mất filter).

**Lệnh đếm lại:**
```
grep -rhoE 'class="[^"]*"' custom/wujia_portal_*/views/ | grep -oE '\b[a-z0-9_-]*(pag(er|ination)|page-nav)[a-z0-9_-]*\b' | sort | uniq -c
grep -rlE 'pagination|pager|page-nav' custom/wujia_portal_*/views/
```

**Việc:**
1. Kiểm kê **theo cấu trúc**: mỗi route — tổng record, `page_size`, cách dựng URL trang (helper nào?
  `wj_ajax_list` hay GET thường?), có form page-size không, có ẩn khi 1 trang không (D5 guard đã bắt
  pager giả ở franchise-info + nút trang hiện với 1 trang ở Thi/Công nợ).
2. Template `wj_pagination` (`wujia_portal_layout/views/`): tham số `page, total, page_size,
  page_size_options, item_label, url_builder/qs`, render **desktopFull** (`≥992`: count trái "Hiển thị
  a–b / n <đơn vị>" + page-size + `1 … 4 5 6 … 20`) và **mobileCompact** (`<992`: Prev + "Trang x / y"
  + Next, visual 36 nhưng touch ≥44). `<nav aria-label="Phân trang">`, `aria-current="page"`, nút
  icon có tên "Trang trước/Trang sau", **không `href="#"`**, disabled không focus. Ẩn hẳn khi
  `total_pages <= 1`.
3. **Một helper dựng query-string** giữ `q/state/from/to/page_size` (tái dùng seam của
  `wj_ajax_list`/`_wj_back_url` nếu hợp) — đây là chỗ D5 guard đo "pager giả".
4. Migrate 13 file; xoá 10 họ class; token: 36/r10/gap8, 14/20/600, chevron 16, màu default/active/
  disabled/hover đúng bảng BA.
5. Seed để có >1 trang ở history/knowledge/notification (BA: "màn chưa đủ seed cần test lại khi >1 trang").
6. Guard: mở rộng `scripts/qa/wj_datalist.py` (đã có phần pager) — đo 0/1/10/11/50+ record, trang
  đầu/giữa/cuối, filter còn nguyên sau đổi trang (so query-string), mobile không bị bottom-nav che.

**Ràng buộc đo được:** 0 class pager theo route (trừ inspection) · PC 36/r10/gap8 · mobile Prev+x/y+Next,
touch ≥44 · `total_pages<=1` ⇒ 0 node pager · đổi trang giữ `q/filter/sort` (so URL) · a11y 3 tiêu chí ·
6 khổ 0 tràn.

---

## E4 — FilterBar `CMP-FB-001` (`UI-FILTER-001`, STT 139) — `-u wujia_portal_layout` + 9 module

> Prompt: "làm cụm E4". Q1 đã chốt: ô lọc mobile visual 38 + vùng chạm 44 (xem bảng "5 điểm").

**Gốc rễ (đã soi):** **25 form GET** trong 11 file, ba họ PC + ba họ mobile, mỗi màn tự dựng.

| Họ | Form | Route |
|---|---|---|
| PC `wj-pc-filterbar` | history `:234` · delivery `:288` · exam `:31` · notification `:256` | mẫu BA = history; delivery = biến thể nhiều điều kiện |
| PC Bootstrap `row g-2` | support `:24` · knowledge `:36` · return `:38` · info-request `:34` | control 28–32px (BA đo) → về 42 |
| PC `wj-debt-pc-filter` | debt `:295`, `:593` | **giữ week selector**, chỉ căn lề/nhãn |
| mobile `wj-filter-card` (`wj-surface-card` bọc) | history `:300` · delivery `:334` · notification `:324` · support `:155` · knowledge `:174` · return `:181` | mẫu BA = delivery; notification = search + chips |
| mobile khác | order `:322 wujia-morder-search` + `:246` · report `:35 wj-rep-mfilter` + `:175` · exam `:102` · debt `:17 wj-debt-filter` | order: chỉ đồng bộ token, không đụng ProductCard |

Sub-component đã có: `wj-filter-chip[--soft/--wrap/--clear]` (30 chỗ) · `wj-pc-filter-control` (25) ·
`wj-filter-search[-field/-btn]` · `wj-filter-date[s/-sep]` (8) · `wj-filter-error` (2 — cảnh báo ngày ngược
chỉ ở history/return). Lỗi wiring BA nêu: delivery/exam ngày ngược trả **empty** thay vì lỗi; **mobile
exam ngày chưa áp dụng** — phải **tái hiện bằng UI** (Playwright điền ngày → so query → so record) rồi mới đọc controller.

**Lệnh đếm lại:**
```
grep -rnE '<form' custom/wujia_portal_*/views/*.xml | grep -v inspection | grep -iE 'get|filter|search'
grep -rhoE 'class="[^"]*"' custom/wujia_portal_*/views/ | grep -oE '\b[a-z0-9_-]*(filter|search|chip)[a-z0-9_-]*\b' | grep -v __ | sort | uniq -c
```

**Việc:**
1. Kiểm kê **điều kiện lọc từng màn × viewport** (inventory trước/sau là acceptance FB-10): tên
  param, kiểu control, có ngày/chip/select không — **không thêm/bớt điều kiện** giữa PC/mobile.
2. PC: gom token từ `wj-pc-filterbar` của history: control **42px**, cùng baseline, wrap theo nhóm,
  nhãn submit "Tìm kiếm", reset hiện có → "Xóa lọc" (không thêm reset vào màn chưa có). Migrate 4 màn
  Bootstrap + căn hàng delivery.
3. Mobile: giữ card delivery (r14/p12/g8), thứ tự search → ngày (nếu có) → chip/select (nếu có);
  **không** thêm header/reset/bottom sheet. Chiều cao search theo **Q1**.
4. SearchField: Enter ≡ click, giữ điều kiện khác; icon-only có tên "Tìm kiếm"; touch ≥44.
5. Ngày: nhãn "Từ ngày/Đến ngày" kể cả khi đã chọn; ngược → lỗi cạnh trường (tái dùng `wj-filter-error`),
  không empty; sửa wiring exam mobile **sau khi tái hiện**.
6. Phân trang giữ lọc (phối hợp E3 helper query-string); đổi lọc → trang 1.
7. Guard: mở rộng `scripts/qa/wj_formcontrol.py` (D6c) đo control filter 8 màn + test wiring ngày
  (HTTP test: `from > to` → 200 + thông báo, không 0 record).

**Ràng buộc đo được:** FB-10 12 ô · PC control 42 cùng hàng/wrap · mobile r14/p12/g8, chip 32 (search
theo Q1) · inventory điều kiện trước = sau · ngày ngược có lỗi ở 4 màn có ngày · 8 khổ 0 tràn.

---

## E5 — ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136) — `-u wujia_portal_layout` + 8 module

> Prompt: "làm cụm E5". Chạy **sau E2** (badge 12px compact context). Q2 đã chốt: gutter danh sách 12. Là cụm
> *tiêu thụ* D4/D5/E2 — không dựng lớp khung thứ ba.

**Gốc rễ (đã soi):** D5 đã đưa 22 danh sách mobile về `wj_data_list` variant `compact-row` (16) /
`detail-card` (6); ListCard = **anatomy bên trong item** (header tên trái + state phải, 2–3 hàng phụ,
cột linh hoạt) mà D5 chưa chuẩn hoá (D5 chuẩn *dáng ngoài*: 64–76/96–120, gap 8, r12).

| File | `dl_variant` | Route / LC |
|---|---|---|
| `portal_home.xml` | 8 | **Home preview được giữ grouped rows** (LC-23) → chỉ token, không 1-record-1-card |
| `portal_exam.xml` | 3 | LC-19 — cần bản ghi thật |
| `portal_knowledge.xml` | 2 | LC-17 — không state giả, giữ nhóm Nổi bật/Mới |
| `portal_delivery.xml` | 2 | LC-14 — bỏ nhãn "Chuyến xe" + divider, đơn liên quan wrap; mẫu BATCH/OUT/00001 |
| `portal_debt.xml` | 2 | LC-21 — retest bằng role được phép |
| `portal_support.xml` · `portal_return_list.xml` · `portal_history.xml` · `portal_notification.xml` · `portal_franchise_information.xml` | 1 mỗi file | LC-18 / LC-15 (nhãn "Ngày yêu cầu", đủ năm) / LC-13 / LC-16 (read state) / — |
| inspection | — | LC-20 → **defer** |

`wj_returncard.py` (D6b) đã đo phân cấp trong card bù hàng — **mở rộng thành `wj_listcard.py`** cho
mọi route thay vì viết mới.

**Lệnh đếm lại:** `grep -rcE "dl_variant\" t-value=\"'(compact-row|detail-card)'" custom/wujia_portal_*/views/*.xml`

**Việc:**
1. **Field inventory trước** (LC-09/LC-18): mỗi route, bảng `field hiện hiển thị · viewport · nguồn`. Seed
  dữ liệu support/exam/debt trước khi đo (mở rộng `scripts/seed_d6_return_demo.py` — idempotent, lái
  state bằng nghiệp vụ thật).
2. Slot chuẩn trong `wj_data_list` item: `name / state? / meta rows / actions?` — **1 implementation +
  adapter nội dung theo route**, không CSS theo route. p12/r12/gap8, header–body 8, hàng 6–8, title
  15–16/600, badge **12px** (variant compact của E2, tập trung ở component), meta 13–14; không divider/
  shadow/icon lớn; trường ngắn cùng hàng, dài chiếm hàng; thiếu → "—".
3. Gutter danh sách mobile 12 (Q2); **không** cộng 12 + 16.
4. Guard `wj_listcard.py`: 1 record = 1 khung (mở rộng định nghĩa "khung" của `wj_nesting.py`), tên trái/
  badge phải cùng hàng hoặc badge xuống hàng căn phải khi hẹp, không ellipsis mã, không tách chữ số tiền,
  số field trước = sau.
5. Regression 8 khổ (320/360/390/430/991/992/1024/1440) + keyboard/touch ≥44 + sticky bar không che record cuối.

**Ràng buộc đo được:** LC-01…LC-32 (bảng 32 dòng) · field inventory trước = sau ở mọi route · 0 lồng
khung (`wj_nesting` giữ 0) · 8 khổ 0 tràn · Home/bảng PC không đổi byte DOM.

---

## E6 — Button `CMP-BTN-001` (`UI-BUTTON-001`, STT 132) — E6a + E6b — `-u wujia_portal_layout` + 13 module

> Prompt: "làm cụm E6a" (atom + 3 route mẫu) → đo → "làm cụm E6b" (10 route còn lại). Tiền lệ B3a/B3b, C8a/C8b.

**Gốc rễ (đã soi):** ~150 action trong template portal (không tính backend + gallery `pc_preview.xml`),
đếm theo phần tử: `<button>` 102 + `<a class="…btn…">` ~50.

| File | action | Họ chính |
|---|---|---|
| `portal_exam.xml` | 31 | `wujia-mexam-btn[-primary/-outline]` 14 + `wj-pc-btn` |
| `portal_debt.xml` | 11 | Bootstrap `btn` |
| `portal_support.xml` | 10 | `wj-pc-btn` + `btn` |
| `login_page.xml` 9 · `change_password_page.xml` 9 | 18 | `btn-primary` (auth shell, kiểm S39 giữ hay migrate) |
| `portal_order_catalog.xml` 8 · `portal_order_cart.xml` 5 · `pc_cart_panel.xml` 5 · `product_detail` 2 | 20 | `btn-add-cart`, `wujia-morder-*-btn` — **QuantityStepper là boundary riêng** |
| `portal_notification.xml` 6 · `portal_delivery.xml` 6 · `return_list/form` 10 · `portal_history.xml` 5 · `portal_knowledge.xml` 5 · info-request 6 · `mobile_bottomnav.xml` 3 (**boundary BN**) · `store_picker_modal.xml` 3 · `portal_report_orders.xml` 2 · `header_bell_inherit.xml` 2 · `forgot_pass.xml` 2 | ~50 | |

Họ class: `wj-pc-btn` 68 (+`--primary` 32/`--secondary` 37/`--ghost`/`--danger`/`--disabled` 1 mỗi) ·
Bootstrap `btn*` 40+ (`btn-primary` 21, `btn-sm` 15, `btn-outline-*` 13, `btn-success` 4, `btn-danger` 3,
`btn-xs` 3…) · `wj-pc-page-btn` 26 · `wj-empty-state-btn` 14 · `wujia-mexam-btn*` 14 · `wj-filter-search-btn`
7 (→ **E4 sở hữu**, FB-08 ưu tiên context Filter) · `wj-cta-btn` 4 · ~15 class lẻ ×1.

**Boundary giữ nguyên (không gộp):** Pagination (E3) · BottomNavigation · FilterChip · QuantityStepper ·
BackPageHeader (B4) · inline text link. Interaction state (hover/focus/pressed) **đã có** ở
`_interaction.css` (C6, `WJ-PORTAL-UI-001`) — E6 chỉ thêm variant/size/loading, không đẻ token trùng.

**Lệnh đếm lại:**
```
for f in $(ls custom/wujia_portal_*/views/*.xml | grep -v inspection); do b=$(grep -c "<button" $f); a=$(grep -cE '<a [^>]*class="[^"]*btn' $f); echo "$((b+a)) ${f#custom/}"; done | sort -rn
grep -rhoE 'class="[^"]*"' custom/wujia_portal_*/views/ | grep -oE '\b(btn[a-z0-9_-]*|[a-z0-9_-]*-btn[a-z0-9_-]*)\b' | sort | uniq -c | sort -rn
```

**E6a:** `.wj-btn` (+`--primary/--secondary/--outline/--danger/--ghost`, `--sm/--md/--lg`, `.is-loading`,
`:disabled`) và `.wj-iconbtn` (`--sm/--md`, bắt buộc `aria-label`); size PC 32/40/46, mobile 36/44/48,
touch ≥44 (pseudo-element, không phình visual); radius sm 8 / md-lg 12; typo 13/18/600 · 14/20/700 ·
15/22/700; màu theo bảng BA; loading giữ width + chặn submit lặp (JS nhỏ ở `static/src/js/`, **không
inline `&&` trong QWeb** — L11). Migrate 3 route mẫu **support, return, notification** (đủ 3 họ:
`wj-pc-btn`, Bootstrap, class lẻ), đo, viết guard `scripts/qa/wj_button.py` (computed height/radius/
font, đếm Primary ≤1 mỗi action area, tab-walk thật). Rồi mới E6b.

**E6b:** 10 route còn lại theo blast radius: exam (31) cuối cùng. Cart/QuantityStepper chỉ tái dùng atom.
Auth shell (`login/change_password/forgot`) hỏi chủ dự án giữ S39 hay migrate (tiền lệ `wj-auth-card` D4h: giữ + LIMIT).

**Ràng buộc đo được:** ~150 action → 0 class button theo route (trừ inspection + boundary) · size đúng
6 số · ≤1 Primary/action area · loading giữ width · Tab/Enter/Space + focus ring (C6) · 6 khổ + zoom 200%
0 tràn, 0 layout shift · không đổi controller/quyền.

---

## E7 — PageContainer `CMP-PC-001` (`UI-PAGECONTAINER-001`, STT 129) — E7a + E7b — `-u` mọi module portal

> Prompt: "làm cụm E7a" (container + gutter) → đo → "làm cụm E7b" (width variant + đo 14 route). Lớp shell
> — chạy sau khi các atom xong để chỉ đo trục **một lần**.

**Gốc rễ (đã soi):**
- **Seam duy nhất:** `wujia_portal_layout/views/layouts.xml:203-224` template `app_layout` — `<div class="app-content content">`
  → `mobile_header` → `<t t-out="0"/>` (`:218`). Mọi route đổ vào đây.
- **~40 template route** dưới `app_layout`/`pc_account_layout`, **ba họ vỏ**: Vuexy `content-wrapper`
  (+`content-body`, đa số PC `d-none d-lg-block`) · `wujia-mpage` (mobile, `_components.css:2434`, pad
  `--wujia-mcontent-top` 16 / `--wujia-mshell-content-pad-x` 16) · `wj-debt` (4 màn công nợ mobile, tự
  quản) · `wujia-home-wrapper` · Khảo sát `wj-inspection-container` (14px, nền trắng → **defer**).
- **Gốc 30,8px tablet:** `_wujia_theme.css:400-406` chỉ ép `padding-left/right: 24px !important` trong
  `@media (min-width: 1200px)` ⇒ **992–1199 rơi về Vuexy** `components.css:67` `padding: calc(2.2rem-.4rem) 2.2rem`
  (14px × 2.2 = 30,8). Sửa mốc về **992**.
- **Lệch 16px PageHeader:** chưa kết luận — `.wj-page-header--pc { padding: 16px 0 }` (0 ngang) nhưng
  `.wj-pc-page-header` (`_pc_components.css:59`) và `.wujia-mpage > .wj-page-header--m` cần **đo** x của
  title vs content edge ở 14 route; nghi ngờ vỏ `content-wrapper` (24) + `.content-body`/`.row` Bootstrap
  (−12/+12) hoặc `wujia-mpage` 16 + header tự pad 16.

**Lệnh đếm lại (wrapper đầu tiên dưới mỗi `t-call` layout):**
```
python3 - <<'PY'
import glob,re
for f in sorted(glob.glob('custom/wujia_portal_*/views/*.xml')):
    if 'inspection' in f or 'backend' in f: continue
    s=open(f,encoding='utf-8').read()
    for m in re.finditer(r't-call="wujia_portal_layout\.(app_layout|pc_account_layout)"',s):
        cl=re.findall(r'<(?:div|section|main)[^>]*class="([^"]{0,80})"',s[m.end():m.end()+900])[:2]
        print(f.split('/')[1], m.group(1), cl)
PY
```

**E7a:**
1. Mốc "trước": 14 route BA × 5 khổ: `padding` computed của wrapper, x của title/filter/card/list đầu
  tiên, `document.scrollWidth`, số record nhìn thấy (bài học D4: mật độ không được giảm).
2. `<main class="wj-page-container">` bọc `<t t-out="0"/>` tại `app_layout:218` (+ `pc_account_layout`);
  token `--wj-pc-gutter 24 / --wj-pc-gutter-m 16`, pad-top 24/16, pad-bottom 32 / `calc(96px + env(safe-area-inset-bottom))`
  khi có bottom-nav/sticky (prop `bottomInset` qua `t-set`); nền transparent (trang `#F3F6F8`).
3. **Tước gutter** khỏi 3 họ vỏ: `content-wrapper` (sửa `_wujia_theme.css:394-406` + nhánh mobile
  `:433-446`), `.wujia-mpage` (bỏ pad ngang, giữ pad-top nếu là "một mốc đầu nội dung" RESP-MOB-SHELL-003),
  `.wj-debt`. Route wrapper chỉ còn layout nghiệp vụ. Không `overflow-x:hidden` để che.
4. Đo lại: 0 ô 30,8 / 14 / double; title x = 16 mobile / 24 + sidebar PC.

**E7b:** width variant `fluid` (mặc định) / `standard` 1440 / `narrow` 960 theo mapping BA (narrow chỉ
`order/cart`, `return/new`, `support/new`, info-request/new); `t-set="pc_width"` trước `t-call`; PageHeader
cùng inner width. Đo 14 route × 5 khổ + zoom 200% + sidebar mở/đóng; **số cột/record không giảm**
(đặc biệt bảng PC `standard` ở 1440 vẫn 100%). Khảo sát: defer, ghi LIMIT tiêu chí 12.

**Ràng buộc đo được:** 1 container/route (đếm `.wj-page-container` = 1) · gutter 24/24/16 ở ≥1200 /
992–1199 / <992 · 0 giá trị 30,8/14/vw · 5 phần tử đầu (header/filter/section/card/list) cùng x ·
5 khổ `scrollWidth == innerWidth` · bottom inset 96+safe · mật độ trước = sau.

---

## E8 — SidebarNavigation (`UI-SIDEBAR-001`, STT 131) — `-u wujia_portal_layout` + 12 module

> Prompt: "làm cụm E8". Cụm **rủi ro defer cao nhất lứa** (JS Vuexy) — mở bằng **lượt đo E8a** rồi mới code.

**Gốc rễ (đã soi):**
- Template: `wujia_portal_layout/views/pc_sidenav.xml` (`layout_sidenav_figma`, 10 item cứng: home, order,
  history, delivery, debt, notification, knowledge, support, exam + "TIỆN ÍCH" account) + **12 file
  `sidenav_inherit.xml`** chèn item: sale, exam, knowledge, delivery, info_request, notification, return,
  purchase_history, support, report, base (`portal_franchises_in_layout.xml`), **inspection (defer)**.
- Width: `--wujia-sidebar-width: 300px` (`_variables.css:112`) + 3 chỗ `!important` `_wujia_theme.css:113/148/153`
  (navbar `left`, `.main-menu width`, `.content margin-left`) chỉ ≥1200. ⚠ §12 gotcha: **`.main-menu` width
  do JS Vuexy điều khiển** — đổi token có thể không ăn ⇒ đo trước.
- Chuông PC **đã có** (`wujia_portal_notification/views/header_bell_inherit.xml`: icon + badge chưa đọc +
  popup recent + "Xem tất cả") ⇒ phần chuông chỉ đo/chỉnh. Avatar dropdown (`layouts.xml:86-141`) hiện có
  Thông tin tài khoản, Đổi mật khẩu — **thiếu** Ngôn ngữ, cửa hàng/vai trò, Đổi cửa hàng, Hồ sơ cửa hàng.
- Bù hàng **đã có** `nav_item_return` "Đổi trả" (`wujia_portal_return/views/sidenav_inherit.xml`) → Q3: đo rồi đổi nhãn "Đổi trả / Bù hàng".
- Mobile: bottom-nav (`mobile_bottomnav.xml`) + menu "Thêm" (tìm `d-lg-none` more-menu) — giữ Thông báo ở
  bottom-nav, chuyển Hồ sơ cửa hàng + Tài khoản/Cài đặt vào avatar mobile (`mobile_header.xml`).

**Lệnh đếm lại:** `grep -rln "main-menu-navigation\|nav_item_" custom/*/views/*.xml`

**E8a (đo, 0 code):** trên UAT + local: (1) đổi `--wujia-sidebar-width` 300→264 bằng `add_style_tag` xem
`.main-menu` có ăn không (nếu JS ghi đè → tìm config Vuexy `menu.js`/`app-menu` trong `static/assets/js`);
(2) 992–1199: drawer đang mở mặc định do class nào (`menu-expanded`? `vertical-overlay-menu`?); (3) thứ tự
item thật sau khi 12 inherit chèn (đọc DOM, không đọc XML); (4) active state cho route con
(`/portal/return/123`, `/portal/order/cart`); (5) hamburger có `aria-label` chưa. Ra bảng
"hiện trạng → đích BA" + trả lời Q3.

**E8b (code):** width 264 (`_variables` + 3 rule theme), brand 88px/logo ≤160×64; item 44/`10px 12px`/gap 12/
r10 mọi state, icon 20, 15/22/500 (active 700, bg `#EAF7FD`, chữ `#168FC2`, rail 3px), `aria-current="page"`;
**3 nhóm menu** theo thứ tự BA (Chức năng chính / Tài chính & xử lý / Hỗ trợ vận hành) — sắp lại
`pc_sidenav.xml` + 12 inherit (dùng `position="after"` theo id, không `sequence` mới); bỏ Thông báo/Hồ sơ/
Tài khoản khỏi sidebar PC; drawer 992–1199 đóng mặc định + backdrop + Escape + trả focus; avatar dropdown
đủ 8 mục; mobile: avatar mở nhóm tài khoản/cửa hàng, gỡ 2 mục khỏi "Thêm". Render theo quyền, không
chừa khoảng trống. Item Khảo sát của inspection: **giữ nguyên file của anh Thái**, chỉ đặt vị trí bằng
inherit của mình.

**Ràng buộc đo được:** `.main-menu` width 264 ≥1200 (content +36px) · 992–1199 drawer `display:none`
mặc định, mở/đóng bằng hamburger/Escape/click ngoài, focus trả về hamburger · item 44/r10 mọi state ·
thứ tự 11 item đúng 3 nhóm · `/portal/return*` active · chuông badge = số chưa đọc thật · mobile
bottom-nav không đổi · 0 tràn ngang 5 khổ.

---

## Bài học C/D áp thẳng vào lứa E (đọc trước mỗi cụm)

- **D3d/D3e** — số đo Pass hết mà bố cục vẫn vỡ ⇒ ảnh chụp bắt buộc; specificity `.wj-x.<mine>`; JS đọc
  thẳng tên class (grep `querySelector` trong JS module trước khi đổi class — E2/E6 đổi rất nhiều class).
- **D4** — UAT không phải git (fetch + đo version); bump `?v=` **và** manifest; grep thô bắt tên con BEM.
- **D5** — đếm bằng cấu trúc; call site chỉ lộ khi dữ liệu vào đúng trạng thái (seed đủ state trước khi đo).
- **D5h.2** — "thẻ trắng lồng thẻ trắng": E5 ListCard đụng đúng chỗ này, `wj_nesting.py` phải giữ 0.
- **D6** — Pass rỗng: `--scope body`, tài khoản có dữ liệu; mutation phải `assert s != before`.
- **11/09** — đo trên DB có cài khảo sát; hồi quy phải có **run đối chứng** (stash/worktree) trước khi quy lỗi.
- **L11** — không `&&`/`<` trong `<script>` inline QWeb (E3/E6 có JS nhỏ).
- **L15/L17** — nhận code có sẵn (E9a/E9b) phải **chạy** chứ không đọc diff; `git fetch` trước khi kết luận.
