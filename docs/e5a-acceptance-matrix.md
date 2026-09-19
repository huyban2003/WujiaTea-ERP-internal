# E5a — Ma trận nghiệm thu · ListCard `CMP-LC-001` (`UI-LISTCARD-001`, STT 136, dòng tuyệt đối 129)

Phiên 19/09/2026. Phạm vi E5a: **inventory 13 route · component `wj_list_card` · 2 route mẫu
(`/portal/purchase-history` LC-13, `/portal/delivery` LC-14) · guard `wj_listcard.py`**.
9 route còn lại là E5b; nhịp G2 + gutter LC-08 + LC-22 ProductCard là E5c.

Môi trường đo: DB `wujia_e4b1` (bản clone có 2 module Khảo sát như UAT + `data/filestore/`),
server đo `--http-port 8090 --gevent-port 8091`, server test `8098/8099`, login `em.hcm`.
**Không** đụng `wujia_tea_19` / cổng 8019.

## Bảng nghiệm thu

| # | Phép đo | Ngưỡng | Số đo được | Kết |
|---|---|---|---|---|
| 1 | Field inventory trước/sau, 2 route mẫu | 0 trường mất, 0 trường thêm | history 0/0 · delivery 0/0 | ✅ |
| 2 | `wj_listcard.py` 2 route mẫu × 5 khổ (320·360·390·430·991) | 0 vi phạm | 0/10 ô có vi phạm; badge 12px ×30, cùng hàng 30/30, cắt chữ 0 | ✅ |
| 3 | `wj_listcard.py` **đỏ đúng** trên họ chưa migrate | phải đỏ | 7/7 route đỏ "CHƯA MIGRATE" kèm số item thật (20·10·20·24·10·46·10) | ✅ |
| 4 | Guard cắn được (mutation) | mỗi mũi đỏ đúng guard của nó | 11/11 ca `judge()` tổng hợp + mũi CSS thật badge 12→13px ⇒ **20 vi phạm**, hoàn nguyên ⇒ **0** | ✅ |
| 5 | `wj_nesting.py` 7 route × 3 khổ | giữ **0** khung lồng khung | 0 | ✅ |
| 6 | `wj_datalist.py` (dáng ngoài D5) | 0 vi phạm | 0 vi phạm / 24 bảng · gap item 8 | ✅ |
| 7 | Home + bảng PC | **0 byte DOM đổi** | chữ ký DOM `/portal`@390 trước = sau = `fd881c9f4245`; `portal_home.xml` không đụng | ✅ |
| 8 | `-u` gộp `--stop-after-init` | RC=0, 0 ERROR mới | RC=0 | ✅ |
| 9 | Suite portal | 0 đỏ | **433 tests · 0 failed · 0 error** | ✅ |
| 10 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn, không thêm | 3 + 2, không thêm | ✅ |
| 11 | Tràn ngang / lỗi JS / mất record | 0 | 0 tràn · 0 lỗi JS · số record 10/10 và 20/20 | ✅ |

## Đã làm

**Component** `custom/wujia_portal_layout/views/wj_list_card.xml` — 2 template, dùng lại khuôn slot
của `wj_data_list.xml` (`t-set` thân → Markup, `t-out` cho slot thô), **không JS mới**:

- `wj_list_card`: `lc_prefix` · `lc_name` · `lc_state` · `lc_rows` · `lc_actions`.
- `wj_list_card_row`: `lcr_label` · `lcr_value` · `lcr_full` (chiếm cả hàng) · `lcr_strong` · `lcr_class`.

Thẻ item **vẫn ở call site** (QWeb không có directive đổi tên thẻ động — `ir_qweb.py:1705`), nên
`<a>`/`<div>` và href của từng route giữ nguyên; component chỉ dựng **ruột**.

**CSS** gom một chỗ ở `_components.css` họ `.wj-lc__*` theo token LC-07/LC-25: gap card 8 · header–body 8 ·
gap hàng 6 · title 15/600 · metadata 13 · badge 12 · **không** divider, **không** shadow, **không** icon
trang trí lớn. Dáng NGOÀI vẫn là `.wj-data-item` của D5 — **không dựng lớp khung thứ ba**.
Badge 12px làm bằng **modifier dùng chung** `.wj-status-badge--compact` (chỉ khai `font-size`), **không**
CSS theo route — guard E2 được nới đúng một khe hẹp cho modifier này, kèm chú thích LC-25.

**Hai route mẫu**

| Route | Trước | Sau |
|---|---|---|
| `/portal/purchase-history` | `wujia-mhist-row`, 6 rule riêng, 80px, không nhãn | `.wj-data-item.wj-lc`, 104px, nhãn "Ngày đặt"/"Tổng tiền" (LC-13), variant `detail-card` |
| `/portal/delivery` | `wujia-mdelivery-row`, 9 rule riêng, 129px, có nhãn thừa "Chuyến xe" + divider nội bộ | `.wj-data-item.wj-lc`, 104px, bỏ nhãn "Chuyến xe" + bỏ divider (LC-14) |

Nhãn đổi là **do BA yêu cầu**, không phải trường đổi — cột quyết định vẫn là *giá trị mất/thêm = 0*
(xem `docs/e5-field-inventory.md` §2).

`portal_history.xml` đổi `dl_variant` `compact-row` → `detail-card`: card thật đã cao 104px, để
`compact-row` (64–76) là **khai sai dáng**, guard D5 đỏ đúng. Bảng D5 trong
`test_scan_d5_data_list.py` cập nhật theo (mobile site 9→8, detail-card 2→1).

**CSS đã gỡ**: 6 rule họ `wujia-mhist-row*` · 9 rule họ `wujia-mdelivery-row*`.
**Giữ lại có chủ đích**: `-row-colbody` · `-row-colicon` · `-row-collabel` · `-row-divider` ·
`-row-label` vì **trang chi tiết** giao hàng (`portal_delivery.xml` ~521–529) còn dùng — E5 chỉ đụng
danh sách.

**Công cụ mới**

- `scripts/qa/wj_listcard_inventory.py` — kiểm kê trường + chữ ký DOM + nhịp/gutter, `--diff` tách
  **nhãn** khỏi **giá trị** (đổi nhãn theo BA không bị đếm nhầm là "thêm trường").
- `scripts/qa/wj_listcard.py` — guard anatomy: 1 record 1 khung (LC-01) · không divider/shadow trong
  card (LC-07) · không cắt mã/tiền (LC-03/LC-10) · badge 12px, cùng hàng hoặc xuống hàng căn phải,
  không chồng tên (LC-04) · **mẫu rỗng = vi phạm** (bài học D6d), và phân biệt rõ "chưa migrate"
  (có item, 0 ListCard) với "rỗng thật" (0 item).

**Test** (đặt chủ theo F5b)

- `wujia_portal_layout/tests/test_e5_list_card.py` — 12 test **hợp đồng component**: thứ tự tên→state ·
  slot state rỗng không đẻ thẻ · nhãn/giá trị · `--full` · `--strong` · không bọc thêm lớp vỏ · slot
  actions · token CSS · không giành dáng của `.wj-data-item` · modifier compact chỉ đổi `font-size` ·
  không `ellipsis`/`nowrap` · state căn phải.
- `wujia_portal_base/tests/test_scan_e5_list_card.py` — 6 test **quét chéo** theo sổ đăng ký
  `MIGRATED`/`GIU_NGUYEN`: call site đã migrate không còn họ class cũ · CSS cũ đã gỡ · không nhãn/giá
  trị viết tay (khối skeleton được miễn vì chỉ là thanh xám, không có nhãn/giá trị) · Home giữ nguyên
  `wujia-mdash-row`.

## Sự cố đã xử trong phiên

1. **Nhịp đo sai chỗ**: đo *thanh lọc → danh sách* cho ra 52/55/70 vì có count-meta/section-header xen
   giữa. Đổi sang *thanh lọc → phần tử anh em kế tiếp nhìn thấy được* thì lộ đúng **24px ở 7 route**
   (`.wj-filter-card { margin-bottom: 16px }` chồng `gap: 8px` của khung trang) — **nợ G2, trả ở E5c**.
2. **Guard sạch ngay lần đầu** ⇒ nghi Pass rỗng. Chứng minh nó cắn: 11/11 ca tổng hợp + mũi CSS thật.
3. **`wj_nesting.py`/`wj_datalist.py`/`wj_measure.py` mặc định `--base 127.0.0.1:8019`** — đúng cổng
   bị cấm đụng, và lần chạy đầu đã lấy số từ DB khác (delivery item=0). Đổi mặc định cả 3 về **8090**.
4. Test hợp đồng đọc CSS bằng `selector + ' {'` trượt vì rule canh cột (`…--compact    {`) → đổi sang
   regex `\s*\{`.

## Còn treo sang E5b/E5c

- **Mẫu mỏng**: `/portal/debt` 1 bản ghi, `/portal/exam/register` 1 bản ghi ⇒ **gieo thêm trước khi
  kết luận** (LC-18/LC-19/LC-21 — "không kết luận từ empty").
- **Nợ nhịp G2**: 24 → 16 ở 7 route, đo trước/sau cùng một lượt (E5c).
- **Padding item `12px 14px`** vs LC-07 ghi 12 — đi chung món gutter LC-08, xử một lần ở E5c; **không**
  sửa lẻ để khỏi đụng dáng ngoài của 22 danh sách.
- **LC-20 defer vĩnh viễn** (LIMIT): `wujia_portal_inspection` là code anh Thái, không đụng.
- **LC-27**: lệch dữ liệu BA ghi (S00045 Home "Nháp" vs list "Chờ xác nhận"; `WJ-RR/DEMO/002` lệch
  ngày/state) — **chỉ ghi nhận, không tự sửa mapping**.

## Lệnh chạy lại

```
# đo
python3 scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 --portal-login em.hcm --out inv.json
python3 scripts/qa/wj_listcard.py --portal-login em.hcm --breakpoints 320 360 390 430 991
python3 scripts/qa/wj_nesting.py --base http://127.0.0.1:8090 --portal-login em.hcm --out nest.json
python3 scripts/qa/wj_datalist.py --portal-login em.hcm
python3 scripts/qa/check_layers.py

# test (luôn kèm -u module cần test + log-handler; kết quả nằm ở logs/<năm>/<tháng>/<ngày>.log)
$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,wujia_portal_delivery \
  --test-enable --test-tags /wujia_portal_layout,/wujia_portal_base,/wujia_portal_purchase_history,/wujia_portal_delivery \
  --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Trạng thái issue: CHƯA đóng.** `UI-LISTCARD-001` chỉ ghi ledger + `Ready for Retest` ở **cuối E5c**,
khi đã đủ 22 call site + regression 8 khổ. Dev không tự đặt `Done`, không tự deploy UAT.
