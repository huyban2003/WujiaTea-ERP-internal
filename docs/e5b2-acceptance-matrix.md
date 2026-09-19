# E5b2 — Ma trận nghiệm thu · ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136, dòng tuyệt đối 129)

Phiên 19/09/2026. Phạm vi E5b2: **5 call site cuối** — Thi ×3 (LC-19: lịch thi · chọn khoá thi ở
bước 1 wizard · danh sách nhân sự trong phiếu) + Công nợ ×2 (LC-21: hoá đơn tuần · lịch sử thanh
toán). Hết E5b thì **22/22 call site** đã về component; nhịp G2 + gutter LC-08 + **đóng issue** là E5c.

Môi trường đo: DB `wujia_e4b1`, server đo `--http-port 8090 --gevent-port 8091` (chạy kèm
`--dev=assets`), server test `8098/8099`, login đo **`em.hcm`** — đây là **chủ cửa hàng HCM-01**,
nắm toàn bộ hoá đơn/thanh toán nên `_DEBT_ROLES` không chặn (plan viết nhầm là Staff phải đo bằng
`anh.owner`). **Không** đụng `wujia_tea_19` / cổng 8019.

## Bảng nghiệm thu

| # | Phép đo | Ngưỡng | Số đo được | Kết |
|---|---|---|---|---|
| 1 | Field inventory trước/sau, 14 route × 2 khổ | 0 giá trị mất thật, 0 record lệch | **13 dòng, tất cả đúng món đã chốt**: 3 nhãn mới (`Lịch thi`, `Ghi chú kết quả`, `Còn lại/Đã trả/Được trừ`, `Số tiền/Tham chiếu`) + 2 cặp MẤT/THÊM là **cùng một giá trị bị bóc nhãn khỏi chuỗi** (`Đã trả 2.480.000,00 $` → nhãn `Đã trả` + giá trị `2.480.000,00 $`; `Tham chiếu: SEED-…` → nhãn `Tham chiếu` + mã) | ✅ |
| 2 | Số record trước = sau | 0 lệch | 0 dòng `LỆCH SỐ RECORD` trên cả 14 route | ✅ |
| 3 | `wj_listcard.py` **12 route** × 5 khổ (320·360·390·430·991) | 0 vi phạm anatomy, 0 cắt mã/tiền | **0/0** — 5 route mới: exam 10 card · register 3 · registration 2 · debt 3 · payment-history 47; badge cùng hàng **100%**, `bị_cắt` = 0 ở mọi khổ | ✅ |
| 4 | `wj_nesting.py` | giữ 0 khung lồng khung | **0** | ✅ |
| 5 | `wj_datalist.py` (dáng ngoài D5) | 0 vi phạm | 24 bảng · th[scope] thiếu 0/24 · header 44×24 · gap item 8 · `/portal/exam` item **104px** (đúng dải detail-card 96–120) | ✅ |
| 6 | `wj_measure.py` | 0 tràn ngang · 0 lỗi JS · 0 màn mất record | 0 · 0 · 0 · 0 redirect ngầm · RULE 1 HIERARCHY **0** | ✅ |
| 7 | Home `/portal` + 7 route chưa migrate | chữ ký DOM trước = sau | `/portal` @390 `9553a5f77629…` · @1440 `b6b8c2ab3da8…` — **5 vùng giống hệt**; purchase-history · delivery · notification · support · return · knowledge · franchise-information **đều giống** | ✅ |
| 8 | Bảng PC của 5 màn vừa sửa | không đổi một byte | @1440 cả 5 route: vùng **GIỐNG**; chỉ vùng mobile @390 đổi — đúng vùng phải đổi | ✅ |
| 9 | Wizard Thi 4 bước bằng trình duyệt | chọn khoá → lịch vẫn chạy | thẻ "đã chọn" nhận **đúng tên + meta**, bước hiện `['2']`, lịch render **35 ô / 1 ngày chọn được**, quay lại `['1']`, **0 lỗi JS** | ✅ |
| 10 | Nút "Chọn" theo trạng thái khoá | khoá đã đóng không có nút | 3 card = 2 mở (có nút) + 1 đóng (**không** nút); chip lọc Đã đóng → 1, Còn lịch → 2 | ✅ |
| 11 | Mutation sweep (14 mũi) | mỗi mũi đỏ **đúng** guard của nó | **14/14** — mốc sạch 0 đỏ, phục hồi 0 đỏ. M1 lần đầu ra **SAI**: bỏ lớp `wj-lc` ở một call site mà sổ đăng ký vẫn xanh (chỉ đòi "có item nào mang `wj-lc`"); siết thành **đếm >= số call site** rồi mới 14/14 | ✅ |
| 12 | Suite 10 module kèm `-u` | 0 đỏ | **653 tests · 0 failed · 0 error** (4 module lõi: 475, trước phiên 465) | ✅ |
| 13 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn | 3 + 2, không thêm | ✅ |

## Đã làm

### 5 call site

| Route | Trước | Sau |
|---|---|---|
| `/portal/exam` (LC-19) | `a.wujia-mexam-card` **lồng `wj_card_header`** trong item, 104px | `a.wj-data-item wj-lc`, **104px**, badge `--compact` ở `lc_state`, 2 hàng phụ: `Lịch thi` + meta nhân sự |
| `/portal/exam/register` bước 1 (LC-19) | `div.wujia-mexam-course` + `wj_card_header` + nút `.wujia-mexam-course-choose` | `div.wujia-mexam-course wj-data-item wj-lc` (họ cũ còn lại **chỉ để mang `is-closed`**), nút "Chọn" vào **`lc_actions`**, 96–109px |
| `/portal/exam/registration/<id>` (LC-19) | `div.wujia-mexam-rrow` compact-row, 70px | `wj-data-item wj-lc` + ô icon kết quả vào `lc_prefix` qua `wj-lc__tile`; **đổi variant `compact-row` → `detail-card`** vì đo lại 96–146px |
| `/portal/debt` (LC-21) | `div.wj-debt-inv` + `__name/__badge/__meta/__amount`, 62px | `wj-data-item wj-lc wj-debt-inv--<status>`, **80px**, 2 hàng `--inline`: meta + **nhãn tiền theo trạng thái** |
| `/portal/debt/payment-history` (LC-21) | `div.wj-debt-pay` + 5 lớp con, 96px | `wj-data-item wj-lc`, **124px**, 3 hàng: ngày/giờ/phương thức · `Tham chiếu` · `Số tiền` (đậm) |

Thẻ item vẫn ở call site (QWeb Odoo 19 không đặt được tên thẻ động — `ir_qweb.py:1705`); component chỉ dựng **ruột**.

### Quyết định của chủ dự án trong phiên

1. **Wizard "Chọn khóa thi" có migrate**, nút "Chọn" vào `lc_actions` — LC-11 (control riêng, không
   lồng interactive) được giữ bằng chính cấu trúc slot.
2. **Tiền tách nhãn**: `Còn lại` / `Đã trả` / `Được trừ` vào `lcr_label`, số tiền là `lcr_value`
   + `lcr_strong`. Đây là nguồn của 4/13 dòng diff ở phép đo #1 — **đổi nhãn, không mất giá trị**.
3. Chốt lượt: **commit + push `main`, KHÔNG deploy UAT, issue vẫn mở** (đóng ở E5c).

### Thay đổi ở khung (`_components.css`, `?v=1311 → 1312`)

- `.wj-lc__link` (7 dòng) — link hành động trong `lc_actions`: 14px/600/màu primary, không gạch chân.
  Đây là **rule duy nhất** thêm vào khung phiên này; không màn nào khai `.wj-lc*` riêng.

### CSS đã gỡ / giữ

- **Gỡ hẳn** (view + CSS) — Thi **70 dòng**: `wujia-mexam-list` · `-card` · `-card-title` ·
  `-courselist` (+ rule layout) · `-course-main/-title/-meta/-choose` · `-rlist` (+ rule layout) ·
  `-rrow-main/-name/-meta/-note`. Công nợ **30 dòng**: `wj-debt-invoices` · `wj-debt-payments` ·
  `wj-debt-inv__{name,badge,meta,amount}` · `wj-debt-pay__{ref,badge,meta,trace,amount}`.
- **Giữ có chủ đích**: `wujia-mexam-card-top` / `-card-line` — **khối tóm tắt phiếu** (không phải
  danh sách) vẫn dùng; gỡ là vỡ trang chi tiết. Sổ đăng ký E5 ghi rõ ngoại lệ này.
- **Thu hẹp thay vì xoá**: `.wujia-mexam-rrow-ico` còn đúng `color` + 3 rule nền theo kết quả;
  `.wujia-mexam-course.is-closed` còn `opacity`. `portal_debt.css` còn **2 rule màu**:
  `.wj-debt-inv--overdue .wj-lc__value--strong` và `--paid` — tô đúng **số tiền**, không tô cả card.

### JS

`portal_exam_wizard.js` gỡ hai chỗ bám lớp trình bày:
- meta khoá thi: `.wujia-mexam-course-meta` → **`.js-exam-course-meta .wj-lc__value`** (lớp *hành vi*,
  không phải lớp dáng);
- tên khoá thi: `.wj-card-header__title` → **`.wj-lc__name`**. **Đây là lỗi thật bắt được bằng phép
  đo #9**: sau migrate, item không còn `wj_card_header` nên thẻ "đã chọn" ở bước 2 hiện **tiêu đề
  rỗng** — test markup không thấy, chỉ có chạy thật mới thấy.
- `t.closest('[data-exam-choose]')` giữ nguyên: hook đã neo vào `data-*`, không vào class.

### Test (đặt chủ theo F5b)

- `wujia_portal_base/tests/test_scan_e5_list_card.py` — sổ `MIGRATED` 7 → **9 dòng**. Sửa một **bẫy
  thật**: `assertNotIn('wujia-mexam-card', view)` khớp chuỗi con nên báo đỏ giả ở
  `wujia-mexam-card-top` (đúng bẫy tên con BEM của D4e) ⇒ đổi sang **so theo token**
  `r'%s(?![-\w])'`. Miễn trừ "chỉ khai `color`" mở theo **tính chất** chứ không theo tiền tố tên lớp,
  nên `.wj-debt-inv--overdue` dùng được mà không phải nới luật.
- `wujia_portal_exam/tests/test_list_card_e5b2.py` (**mới**, 6 test) — hook wizard còn nguyên trên
  item, JS neo vào lớp hành vi + `.wj-lc__name`, nút Chọn là control riêng và ẩn khi khoá đóng,
  đủ 3 badge kết quả, ô icon đi qua `wj-lc__tile` của khung.
- `wujia_portal_debt/tests/test_list_card_e5b2.py` (**mới**, 5 test) — 3 nhãn tiền nằm trên **một**
  biểu thức, giấy báo có ra **số âm**, hai hàng tiền dùng khuôn `--inline`, `tabular-nums` còn ở
  khung, màu trạng thái bám đúng `.wj-lc__value--strong`.
- `test_data_list_d5h.py` / `test_data_list_d5g.py` — **đảo chiều** hai test layout: trước đòi màn
  *có* rule layout riêng cho item, nay cấm — bố cục bên trong item là việc của ListCard.
  D5h: variant 2 detail + 1 compact → **3 detail-card**; `test_surface_card_khong_bi_sua` đổi thành
  "item Thi **rời** `wj-surface-card`, component D4 vẫn bất biến".
- `test_scan_d3_card_header.py` (schedule 2→1, register 9→8) · `test_scan_d4_surface_card.py`
  (bỏ exam khỏi 2 tuple owner-class) — hai sổ này đếm theo call site nên phải đi theo.
- `wujia_portal_exam/tests/test_card_header_d3d.py` — guard D3d **đã làm đúng việc của nó**: nó đỏ
  ngay khi JS đổi nguồn đọc tiêu đề. Cập nhật theo thực tế mới (nguồn `.wj-lc__name`, đích vẫn
  `.wujia-mexam-selcard .wj-card-header__title`), **không** nới guard.
- `scripts/qa/wj_listcard.py` — `ROUTES` 7 → **12**. `/portal/debt` phải là **`?all=1`**: mặc định
  chỉ render 2 hoá đơn (`INVOICE_PREVIEW`), thiếu nhánh giấy báo có.

### Dữ liệu gieo — `scripts/seed_e5b2_demo.py` (mới, LOCAL-ONLY)

Idempotent, lái state bằng nghiệp vụ thật (không `write` thẳng vào `state`):
2 khoá thi (**Còn lịch** + **Đã đóng**) · phiếu `WJ-EXR/26/00009` đã công bố có **1 Đạt + 1 Không đạt
+ ghi chú** · tuần mặc định của portal có **quá hạn · giấy báo có · đã trả đủ** · 3 thông báo **đã
đọc** cho `em.hcm` (trả nợ "mẫu một chiều" của E5b1).

## Sự cố đã xử trong phiên

1. **`/portal/debt` chỉ ra 1 card sau khi gieo tuần hiện tại.** Đọc `_default_week` mới thấy
   WJ-DEBT-010: portal mở **tuần quá hạn cũ nhất còn dư nợ**, không phải tuần hiện tại. Sửa **seed**
   (tính tuần mặc định từ `get_summary()` rồi gieo vào đó), không sửa mã cho vừa phép đo, và không
   hardcode `?week=` sẽ mục theo thời gian.
2. **Hoá đơn "đã trả" không chịu `paid` ở lần gieo thứ hai** — memo thanh toán cố định bị tìm thấy
   và dùng lại, nhưng nó đã đối trừ với hoá đơn của lượt trước. Sửa: memo **khoá theo id hoá đơn**.
3. **Danh sách nhân sự 92–146px** — ra khỏi dải `compact-row` 64–76. Đổi variant sang `detail-card`
   (đúng cách E5b1 đã làm), không ép chiều cao.
4. **Thẻ "đã chọn" ở bước 2 rỗng tiêu đề** — xem mục JS ở trên. Bài học: call site nào có JS đọc DOM
   thì **phải chạy thật**, guard markup không thay được.
5. **Đỏ giả `wujia-mexam-card` vs `-card-top`** — bẫy tên con BEM, sửa bằng so token.
6. **Test in ra 0 byte, RC=1** — `config/odoo.conf` có `logfile`, log xoay sang
   `logs/2026/09/2026-09-19.log`; phải đọc file xoay chứ không phải stdout.
7. **Bundle asset không đổi theo file JS** — server đo chạy không `--dev`, bundle nằm trong
   `ir.attachment`. Khởi động lại kèm `--dev=assets` sau một lượt `-u`.

## Câu hỏi cho BA (nối tiếp E5b1, **vẫn treo**)

1. **Ô icon phân loại `.wj-lc__tile` 32×32** — nay dùng thêm ở danh sách nhân sự (Đạt/Không đạt/Chờ).
   LC-06/LC-07 ghi "không icon trang trí lớn trước tên". Giữ hay bỏ?
2. **Dải cao của hai variant không còn phủ hết thực tế.** Số đo sau E5b2:
   - `detail-card` (96–120): card nhân sự **có ghi chú kết quả** đo **146px**.
   - `compact-row` (64–76): card hoá đơn 2 hàng phụ đo **80px** — thấp hơn 96 nên không thể lên
     `detail-card`, cao hơn 76 nên cũng không đúng `compact-row`.
   Đề xuất: nới `compact-row` → 64–84 và `detail-card` → 96–150, hoặc BA cắt bớt trường. **Chưa tự đổi.**

## Còn treo sang E5c

- **Nhịp G2**: `.wj-filter-card{margin-bottom:16px}` chồng `gap:8px` ⇒ *lọc → danh sách* 24px ở 7 route.
- **Padding item `12px 14px`** vs LC-07 ghi 12 — đi chung món gutter LC-08 (đo được 16px hai bên).
- **LC-20** defer vĩnh viễn (code anh Thái) · **LC-27** lệch dữ liệu, chỉ ghi nhận.
- `/portal/order` là **mốc đóng băng rỗng**: 0 vùng `.wj-data-list`/`table.wj-data-table` nên phép so
  chữ ký ở đó không chứng minh được gì — E5c đo lại bằng chữ ký cả trang.
- Đóng issue ở E5c: đủ **22 call site** + regression **8 khổ** (thêm 992·1024·1440) rồi mới ghi ledger
  → `qa_sync.py`.

## Lệnh chạy lại

```
# gieo (chỉ DB local)
cd odoo19 && python odoo-bin shell -c ../config/odoo.conf -d wujia_e4b1 --no-http \
  < ../scripts/seed_e5b2_demo.py

# đo
python3 scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 --portal-login em.hcm \
  --routes /portal /portal/purchase-history /portal/delivery /portal/notification /portal/support \
           /portal/return /portal/knowledge /portal/exam /portal/exam/register \
           /portal/exam/registration/9 "/portal/debt?all=1" /portal/debt/payment-history \
           /portal/franchise-information /portal/order \
  --out docs/e5b2-inventory-after.json --diff docs/e5b2-inventory-before.json \
  --frozen /portal/order /portal
python3 scripts/qa/wj_listcard.py --base http://127.0.0.1:8090 --portal-login em.hcm
python3 scripts/qa/wj_nesting.py  --base http://127.0.0.1:8090 --portal-login em.hcm
python3 scripts/qa/wj_datalist.py --base http://127.0.0.1:8090 --portal-login em.hcm
python3 scripts/qa/wj_measure.py  --base http://127.0.0.1:8090 --portal-login em.hcm --out after.json
python3 scripts/qa/check_layers.py
python3 scratchpad/e5b2/wizard_check.py      # wizard 4 bước, trình duyệt thật

# mutation (tự phục hồi cây mã kể cả khi bị kill)
python3 scratchpad/e5b2/mutations.py

# test — LUÔN kèm -u (tests wujia_franchise còn import file đã xoá)
$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_exam,wujia_portal_debt,wujia_portal_base \
  --test-enable --test-tags /wujia_portal_layout,/wujia_portal_exam,/wujia_portal_debt,/wujia_portal_base \
  --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Trạng thái issue: CHƯA đóng.** `UI-LISTCARD-001` ghi ledger + `Ready for Retest` ở **cuối E5c**,
khi đủ 22 call site + regression 8 khổ. Dev không tự đặt `Done`, không tự deploy UAT.
