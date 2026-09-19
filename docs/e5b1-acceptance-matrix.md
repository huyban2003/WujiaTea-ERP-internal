# E5b1 — Ma trận nghiệm thu · ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136, dòng tuyệt đối 129)

Phiên 19/09/2026. Phạm vi E5b1: **6 call site rủi ro thấp** — Thông báo (LC-16) · Hỗ trợ (LC-18) ·
Bù hàng (LC-15) · Kiến thức **mobile + PC** (LC-17) · Thành viên cửa hàng (LC-18).
Thi ×3 + Công nợ ×2 là **E5b2** (cần gieo dữ liệu + thay CardHeader lồng + JS hook `data-exam-*`).
Nhịp G2 + gutter LC-08 + LC-22 ProductCard + **đóng issue** là E5c.

Môi trường đo: DB `wujia_e4b1`, server đo `--http-port 8090 --gevent-port 8091`, server test
`8098/8099`, login đo `em.hcm` (đủ dữ liệu 6 route) và `anh.owner` (kho HN-01 — nơi có phiếu
bù hàng đã gieo). **Không** đụng `wujia_tea_19` / cổng 8019.

## Bảng nghiệm thu

| # | Phép đo | Ngưỡng | Số đo được | Kết |
|---|---|---|---|---|
| 1 | Field inventory trước/sau, 6 call site | 0 giá trị mất, 0 giá trị thêm (nhãn BA đổi không tính) | DIFF 13 route × 2 khổ = **3 dòng, cả 3 đều là món LC-15 của Bù hàng** (`%d/%m` → `%d/%m/%Y`, nhãn `Ngày YC` → `Ngày yêu cầu`); 5 route kia 0/0 | ✅ |
| 2 | `wj_listcard.py` 7 route × 5 khổ (320·360·390·430·991) | 0 vi phạm | **0** — 91 card/khổ, badge cùng hàng 91/91, cắt chữ 0 | ✅ |
| 3 | Kiến thức @1440 (mốc PC duy nhất phiên này) | 0 vi phạm | **0** — 12 card, hàng phụ 0, cao 64px (đúng bằng mốc trước) | ✅ |
| 4 | `wj_listcard.py` **đỏ đúng** trên route chưa migrate | phải đỏ | Thi ×2 + Công nợ ×2 báo "CHƯA MIGRATE" kèm số item thật (10 · 1 · 1 · 46); `/portal/exam/results` báo "rỗng thật" | ✅ |
| 5 | Mutation sweep (10 mũi) | mỗi mũi đỏ **đúng** guard của nó | **10/10**; mốc sạch 0 đỏ, phục hồi 0 đỏ | ✅ |
| 6 | `wj_returncard.py` (D6b/BH-007/BH-008) | 0 vi phạm, không Pass rỗng | `anh.owner`: 14 card · 5 cặp badge · 0 cùng hàng · **1** bố cục metadata · 0 tên cắt dòng 1 (tên dài nhất 101 ký tự) | ✅ |
| 7 | `wj_nesting.py` | giữ **0** khung lồng khung | 0 | ✅ |
| 8 | `wj_datalist.py` (dáng ngoài D5) | 0 vi phạm | 24 bảng · th[scope] 0/24 thiếu · header 44 · gap item 8×36 | ✅ |
| 9 | Home `/portal` | **chữ ký DOM trước = sau** | @390 `9553a5f77629…` và @1440 `b6b8c2ab3da8…` — 5 vùng đóng băng **giống hệt** ở cả hai khổ | ✅ |
| 10 | `wj_measure.py` | 0 tràn ngang · 0 lỗi JS · 0 màn mất record | 0 · 0 · 0 (thêm: 0 vi phạm RULE 1 HIERARCHY, 0 redirect ngầm) | ✅ |
| 11 | `-u` gộp `--stop-after-init` | RC=0, 0 ERROR mới | RC=0 | ✅ |
| 12 | Suite 8 module | 0 đỏ | **567 tests · 0 failed · 0 error** | ✅ |
| 13 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn, không thêm | 3 + 2, không thêm | ✅ |

## Đã làm

### 6 call site

| Route | Trước | Sau |
|---|---|---|
| `/portal/notification` (LC-16) | `wujia-mnoti-row` + `is-unread`, 100px | `wj-data-item wj-lc wujia-mnoti-unread`, 108–116px, ô tone vào `lc_prefix`, chấm chưa đọc + chip ưu tiên trong `lc_state` |
| `/portal/support` (LC-18) | `wujia-mdash-row` (**họ dùng chung**), 92–112px | `wj-data-item wj-lc`, 113px, chip nhóm đổi từ `.wujia-mticket-tag` riêng sang họ chung `wujia-badge wujia-badge-muted` |
| `/portal/return` (LC-15) | `wujia-mreturn-row`, 120px, nhãn "Ngày YC" + `%d/%m`, có divider nội bộ + chevron | `wj-data-item wj-lc`, 104px, **"Ngày yêu cầu" đủ năm**, bỏ divider (LC-07) + bỏ chevron (tiền lệ WJ-HOME-007) |
| `/portal/knowledge` mobile (LC-17) | `wujia-mknow-row`, 80px | `wj-data-item wj-lc`, 96px, ô icon vào `lc_prefix`, giữ nhóm Nổi bật/Mới, **không state giả** |
| `/portal/knowledge` **PC** (LC-17) | `li.wujia-content-card-row` (**họ dùng chung với Home**), 64px | `li.wj-data-item wj-lc`, **vẫn 64px**, bullet thành lớp riêng `.wujia-know-bullet` |
| `/portal/franchise-information` (LC-18) | `wujia-mdash-row` (**dùng chung**), 66–121px | `wj-data-item wj-lc`, 79–111px, badge vai trò vào `lc_prefix` |

Thẻ item vẫn ở call site (QWeb không có directive đổi tên thẻ động), component chỉ dựng **ruột**.

### Thay đổi ở khung (`_components.css`, `?v=1306 → 1311`)

- `.wj-lc__tile` — ô icon phân loại 32×32 đứng trước tên (Thông báo, Kiến thức). **Chờ BA chốt**:
  LC-06/LC-07 ghi "không icon trang trí lớn trong card"; quyết định đầu phiên của chủ dự án là
  **giữ icon, đưa vào slot** chứ không tự xoá thứ BA đang thấy.
- `.wj-lc__name { flex: 1 1 0 }` + clamp 2 dòng — trước đó tên **rớt xuống dòng dưới ô icon**
  (lead `flex-wrap`), card Thông báo phình 100 → 150px. Sửa xong: 116px.
- `.wj-lc__body` thành **lưới 2 cột** `minmax(0, 1fr) auto`; hàng thường chiếm cả hàng, hàng
  `--inline` đứng một cột ⇒ "trường ngắn cùng hàng" (BA §LC-05) mà **không đổi hợp đồng slot**
  (dùng lại `lcr_class` sẵn có, không đẻ slot mới).
- `.wj-lc__value { font-variant-numeric: tabular-nums }` — không có nó, cột phải rộng theo chữ số
  của **từng** card, `wj_returncard.py` đo ra **5 bố cục metadata khác nhau** (lệch 1–7px). Có rồi: 1.
- `.wj-lc__row--clamp2` (tên sản phẩm 2 dòng, BH-007) · `.wj-lc__meta` (ngày/lượt xem cạnh badge).

### CSS đã gỡ / giữ

- **Gỡ hẳn** (view + CSS): `wujia-mnoti-list`, `wujia-mnoti-row*` (10 lớp) · `wujia-mticket-rowside`,
  `wujia-mticket-tag` · `wujia-mreturn-row-{body,product,divider,meta,metacell,chevron,progress,badges}` ·
  `wujia-mknow-{list,row-main,row-title,row-foot,date}`.
- **Giữ có chủ đích**: `wujia-mdash-row*` (Home 50 chỗ + form chi tiết Hỗ trợ) ·
  `wujia-content-card-row*` (Home) · `wujia-mreturn-row-{head,code}` (trang chi tiết Bù hàng) ·
  `wujia-mknow-tile` (bài nổi bật + trang chi tiết).
- **Đổi tên thay vì xoá**: bài Nổi bật của Kiến thức đang dùng chung `.wujia-mknow-row-title` /
  `.wujia-mknow-date` với danh sách ⇒ gỡ rule là bài nổi bật mất cỡ chữ. Đổi sang
  `.wujia-mknow-feat-title` / `.wujia-mknow-feat-date`, `.wujia-mknow-badges` giữ nguyên vì
  **trang chi tiết** cũng dùng.

### Test (đặt chủ theo F5b)

- `wujia_portal_base/tests/test_scan_e5_list_card.py` — sổ `MIGRATED` 2 → **7 dòng**, thêm trường
  **họ dùng chung**: với `wujia-mdash-row` / `wujia-content-card-row`, luật thu hẹp thành *"không
  còn nằm trong cây con của item đã migrate"* (xoá rule của chúng = vỡ Home).
  Luật `test_khong_css_anatomy_theo_route` mở đúng một khe: rule **chỉ khai `color`** cho trạng thái
  riêng của màn (tên đậm khi chưa đọc) không phải rule dáng — miễn trừ theo tính chất, tiền lệ D5f.
- `wujia_portal_notification/tests/test_e5b_list_card_read_state.py` (**mới**) — dấu chưa đọc là
  hành vi riêng của màn: lớp `wujia-mnoti-unread`, chấm `wujia-mnoti-dot`, thanh accent `::before`,
  và trạng thái **không được giành lại dáng** (padding/radius/min-height).
- `wujia_portal_return/tests/test_return_card_d6.py` — D6b/BH-007/BH-008 chuyển neo sang anatomy
  ListCard (`lc_state`, `wj_list_card_row` + `lcr_label`), thêm `test_nhan_ngay_yeu_cau_du_nam`
  (LC-15: nhãn đủ chữ + ngày đủ năm), và "hai cột ổn định" nay đọc lưới của khung.
- `wujia_portal_base/tests/test_scan_d5_data_list.py` — D5e còn **5 call site Home**, D5f không còn
  sổ họ riêng; hai test layout-trong-@media của mknow/mnoti/mreturn bỏ (rule đã đi theo họ), thay
  bằng một test giữ luật "layout không giành dáng" cho họ mdash.
- `wujia_portal_base/tests/test_scan_e2b_status_badge.py` — luật "badge 28px không kéo chip bên
  cạnh" của danh sách mobile chuyển sang đo `.wj-lc__head` / `.wj-lc__row` ở khung.

### Công cụ

- `scripts/qa/wj_listcard.py` — thêm 5 route vào sổ `ROUTES` (guard tự phủ từ lượt sau).
- `scripts/qa/wj_returncard.py` — đổi selector sang anatomy chung (`.wj-lc__name`,
  `.wj-lc__row--clamp2 .wj-lc__value`, `.wj-lc__row--inline`), nhận cả `.wj-status-badge`.

## Sự cố đã xử trong phiên

1. **84 vi phạm giả ở lần đo đầu** — dò DOM thật thay vì đoán: `.wujia-badge` có `border-top: 1px`
   nên bị đếm là "divider nội bộ"; `.wj-lc__tile` có nền nên bị đếm là "khung con". Sửa **harness**
   (miễn badge/chip/ô icon khỏi hai phép đo) chứ không sửa mã cho vừa guard — bài học L7/L9.
   `wujia-badge--sm` 11px cũng bị bắt: BA đã **loại** nhóm chip này khỏi CMP-SB-001 ở E2b ⇒ luật
   12px thu hẹp về đúng badge trạng thái.
2. **Card cao lên** sau khi đổi ruột: Thông báo 100 → **150**. Không phải do nội dung mà do
   `.wj-lc__name` bị đẩy xuống dòng dưới ô icon. Sửa ở khung (`flex: 1 1 0`), không sửa từng màn.
3. **Bù hàng 128px** vượt dải `detail-card` 96–120 vì 3 trường ngắn nằm 3 hàng. Gộp 2 trường ngắn
   vào một hàng lưới ⇒ **104px**, đúng BA "trường ngắn cùng hàng".
4. **Suýt mất dáng bài Nổi bật + trang chi tiết Kiến thức**: rule bị gỡ theo họ danh sách nhưng
   markup khác vẫn dùng. Bắt được bằng một lượt quét *"class còn trong view mà không còn rule CSS"*
   — nên làm mặc định sau mỗi lượt gỡ CSS.
5. **Hai lớp hook chết** (`wujia-mnoti-list`, `wujia-mknow-list`): gap giờ là việc của DataList ⇒
   bỏ `dl_class` thay vì để lại tên lớp không có rule.
6. **`wj_returncard.py` Pass rỗng**: 51/51 phiếu trong DB đo có `resolution_type` rỗng ⇒ nhánh
   "Tiến độ bù" **không bao giờ render**. Gieo `scripts/seed_d6_return_demo.py` (10 phiếu, đủ 4
   trạng thái bù + tên sản phẩm 101 ký tự) và đo bằng `anh.owner` ⇒ 5 cặp badge đo thật.

## Câu hỏi cho BA

1. **Ô icon phân loại trong card** (`.wj-lc__tile` 32×32, màn Thông báo + Kiến thức): LC-06/LC-07 ghi
   "không icon trang trí lớn trước tên". Giữ như hiện tại (quyết định đầu phiên), hay bỏ để card về
   đúng chữ của spec? Bỏ thì Thông báo mất tín hiệu màu theo loại.
2. **Dải cao `detail-card` 96–120**: bản ghi Bù hàng *có* tiến độ bù **và** tên sản phẩm 2 dòng đo
   được **122–156px** (dữ liệu gieo, tên 101 ký tự). LC-02 đòi auto-height nên không ép cứng; BA
   muốn siết (cắt bớt trường) hay công nhận dải rộng hơn cho card 4 trường?

## Còn treo sang E5b2 / E5c

- **E5b2**: Thi ×3 + Công nợ ×2 — phải gieo trước (`/portal/debt` 1 bản ghi, `/portal/exam/register`
  1 bản ghi), thay CardHeader lồng trong item bằng đầu ListCard (đã chốt), giữ JS hook `data-exam-*`.
- **Nợ nhịp G2** 24 → 16 ở 7 route (E5c) · **padding item `12px 14px`** vs LC-07 ghi 12 (đi chung
  gutter LC-08, E5c) · **LC-20 defer vĩnh viễn** (code anh Thái) · **LC-27** lệch dữ liệu BA ghi.
- **Mẫu đo một chiều**: cả 10 thông báo của `em.hcm` đều **chưa đọc** ⇒ phép đo trình duyệt không
  đối chiếu được card đã đọc / chưa đọc; hợp đồng đang do test Python giữ. Gieo thêm ở E5b2.

## Lệnh chạy lại

```
# đo
python3 scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 --portal-login em.hcm \
  --out docs/e5b1-inventory-after.json --diff docs/e5b1-inventory-before.json
python3 scripts/qa/wj_listcard.py --portal-login em.hcm --breakpoints 320 360 390 430 991
python3 scripts/qa/wj_listcard.py --portal-login em.hcm --routes /portal/knowledge --breakpoints 1440
python3 scripts/qa/wj_returncard.py --base http://127.0.0.1:8090 --portal-login anh.owner
python3 scripts/qa/wj_nesting.py --portal-login em.hcm
python3 scripts/qa/wj_datalist.py --portal-login em.hcm
python3 scripts/qa/wj_measure.py --portal-login em.hcm --out after.json
python3 scripts/qa/check_layers.py

# mutation (tự phục hồi cây mã kể cả khi bị kill)
python3 scratchpad/e5b1/mutations.py

# test — LUÔN kèm -u (tests wujia_franchise còn import file đã xoá)
$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_notification,wujia_portal_support,wujia_portal_return,wujia_portal_knowledge,wujia_portal_purchase_history,wujia_portal_delivery \
  --test-enable --test-tags /wujia_portal_layout,/wujia_portal_base,/wujia_portal_notification,/wujia_portal_support,/wujia_portal_return,/wujia_portal_knowledge,/wujia_portal_purchase_history,/wujia_portal_delivery \
  --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Trạng thái issue: CHƯA đóng.** `UI-LISTCARD-001` chỉ ghi ledger + `Ready for Retest` ở **cuối E5c**,
khi đủ 22 call site + regression 8 khổ. Dev không tự đặt `Done`, không tự deploy UAT.
