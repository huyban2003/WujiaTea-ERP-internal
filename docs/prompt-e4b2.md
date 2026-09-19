# Prompt phiên E4b2 — FilterBar `CMP-FB-001`, phủ hết call site **mobile**

> Dán khối dưới đây sau `/wujia-start`. **Điều kiện tiên quyết: E4b1 đã xong**
> (`docs/e4b1-acceptance-matrix.md` — 9 màn PC đã gọi component, kiểm kê FB-10 render-mode 0 lệch).
> `docs/prompt-e4b.md` là prompt cũ của lượt E4b nguyên khối; chủ dự án đã **cắt đôi** 19/09:
> E4b1 = PC (xong) · **E4b2 = mobile (phiên này)**. Đọc prompt cũ chỉ để tham khảo, phạm vi lấy ở đây.

---

Làm **cụm E4b2** — lượt mobile của `UI-FILTER-001` (STT 139, dòng 132 sheet, `Ready for Dev`,
Owner Dev). Phạm vi: **nhân `wujia_portal_layout.wj_filter_bar` ra hết call site mobile còn lại**.
**KHÔNG đóng issue ở lượt này** — đóng ở E4c sau khi vá wiring ngày. **KHÔNG chạy `qa_sync.py`.**

## Phạm vi chính xác (đếm lại 19/09 trên cây mã sau E4b1 — dòng có thể trôi, grep lại trước khi sửa)

**Nhóm 1 — 5 `wj-filter-card` → gọi component** (mẫu BA là delivery mobile `:313`, E4a đã làm):

| Màn | File:dòng | Điều kiện phải giữ nguyên (FB-10) |
|---|---|---|
| Lịch sử mua hàng | `wujia_portal_purchase_history/views/portal_history.xml:241` | `page_size` hidden · `q` · `date_from` · `date_to` + 4 chip (2 preset + `state` + Xóa lọc) |
| Thông báo | `wujia_portal_notification/views/portal_notification.xml:257` | `unread` hidden · `keyword` + 4 chip (part `mchips`) |
| Hỗ trợ | `wujia_portal_support/views/portal_support.xml:127` | `state` hidden · `q` + 4 chip (`state`) |
| Kiến thức | `wujia_portal_knowledge/views/portal_knowledge.xml:146` | `keyword` + 1+N chip category (`category_id`) |
| Đổi trả | `wujia_portal_return/views/portal_return_list.xml:142` | `q` · `state` · `date_from` · `date_to` |

**Nhóm 2 — Thi mobile dùng `wj_surface_card` + `sc_class='wj-filter-card'`**:
`wujia_portal_exam/views/portal_exam.xml:126` — khối này là **demo UI-only, chưa wire** (comment tại
chỗ ghi rõ "Phase 2 wire"). Chuyển sang component nhưng **giữ nguyên trạng thái chưa wire**; việc
nối ngày là của **E4c**, không làm sớm ở đây.

**Nhóm 3 — 3 thanh mobile lẻ, CHỈ đồng bộ token/nhịp, KHÔNG nhập component:**
- `wujia_portal_report/views/portal_report_orders.xml:35` (`wj-rep-mfilter`, 2 ô ngày + nút `Tìm`
  → nhãn về **`Tìm kiếm`** theo FB-02).
- `wujia_portal_sale/views/portal_order_catalog.xml:300` (`wujia-morder-search`) — **TUYỆT ĐỐI
  không đụng ProductCard** nằm ngay dưới.
- `wujia_portal_debt/views/portal_debt.xml:17` (`wj-debt-filter`, component riêng của Công nợ,
  2 call site) — **giữ selector `f_name` + nút `Xem`** theo FB-09 item 9.

**Ngoài phạm vi:** toàn bộ PC (xong ở E4b1 — đụng lại là hồi quy) · wiring ngày 4 màn → **E4c** ·
2 call site Khảo sát (`wujia_portal_inspection`) → **defer vĩnh viễn** (luật 08/09).

## Luật bắt buộc của lượt này

1. **FB-10 là acceptance chính**: không thêm/bớt một điều kiện lọc nào. Chân lý = §1 của
   `docs/e4-filter-inventory.md`. Đo bằng **`scripts/qa/wj_filterbar_inventory.py`** (đã commit ở
   E4b1 — *không* viết lại): `--md` cho bảng tĩnh, và **`--base … --portal-login em.hcm --json` +
   `--diff` cho chế độ render** — sau migrate thì bản tĩnh không còn đọc được điều kiện nằm trong
   component, **bắt buộc dùng chế độ render**. Thêm route mobile vào `ROUTES_PC`-tương đương nếu
   thiếu.
2. Mobile giữ dáng card delivery: **radius 14 · padding 12 · gap 8**, thứ tự search → ngày →
   chip/select. Ô lọc: **visual 38, vùng chạm ≥44** (Q1 chủ dự án chốt 12/09 — **không hỏi lại**).
3. **Không thêm reset** vào màn chưa có (FB-02/FB-03); không thêm header, không bottom-sheet.
4. **Chip nằm ngoài `<form>`** ở vài màn (history, notification, support, knowledge, order) — chúng
   là link `data-wj-nav` do `wj_ajax_list.js` bắt. Giữ nguyên `data-wj-nav`, nếu đưa vào slot
   `fb_chips` thì phải giữ đúng thuộc tính, nếu không **mất AJAX** mà test tĩnh không bắt được.
5. **Xoá họ class cũ chỉ khi không ai khác dùng**; chỗ nhóm Khảo sát còn dùng thì **thu hẹp selector
   vào `.wj-inspection-m`/`.wj-inspection-pc`, tuyệt đối không xoá** (bẫy E3c).
6. Không đụng `wujia_portal_inspection` / `wujia_franchise*` / `wujia_mobile_*` (code anh Thái).
7. Không hex cứng — `var(--wujia-*)`; comment **tối đa 1 dòng**; không đẻ modifier mới khi cái sẵn có đủ.
8. **Tầng (ADR-027/F5b)**: dáng component ở `wujia_portal_layout/static/assets/css/` (khung sở hữu
   component) · CSS riêng màn ở CSS module màn · test call site đặt ở **module sở hữu màn**
   (`wujia_portal_base/tests/test_scan_e4_filter_bar.py` cho test quét chéo module), test hợp đồng
   component ở `wujia_portal_layout/tests/test_e4_filter_bar.py`.

## ⚠️ Mốc đo mobile phải chụp lại — G2 đã hạ header mobile 104 → 72

Mọi số chiều cao trang mobile trong tài liệu **trước G2** đều sai 32px. Dưới đây là mốc **sau E4b1**
(đo `wj_measure.py`, DB `wujia_e4b1`, login `em.hcm`) — dùng đúng bộ này làm "TRƯỚC" của E4b2:

| Route | 360 | 390 | record trong khung |
|---|---|---|---|
| `/portal/purchase-history` | 1037 | 1037 | 14 |
| `/portal/notification` | 1553 | 1553 | 14 |
| `/portal/support` | 900 | 900 | 14 |
| `/portal/knowledge` | 1901 | 1796 | 14 |
| `/portal/return` | 1063 | 1032 | 14 |
| `/portal/exam` | 900 | 900 | 14 |
| `/portal/reports/orders` | 1534 | 1515 | 16 |
| `/portal/order` | 1831 | 1831 | 14 |
| `/portal/debt` | 900 | 900 | 14 |
| `/portal/info-request` | 1434 | 1406 | 15 |

`/portal/info-request` **không tách PC/mobile** (một form cho cả hai khổ) và **đã vào component ở
E4b1** ⇒ E4b2 **không sửa markup màn này**, chỉ đo để chứng minh không hồi quy.

## Nghiệm thu (đo bằng máy, không nhìn ảnh)

- **Run đối chứng bắt buộc**: worktree cây mã trước lượt + DB riêng + cổng riêng (bài học S57).
  DB copy cô lập **có cài 2 module Khảo sát giống UAT** (luật 11/09), chép cả `data/filestore/`
  (bẫy E2b). Không đụng `wujia_tea_19`/8019. Truyền `--http-port` riêng (bẫy E3: `--no-http` vẫn
  bind cổng); **không** `pkill -f "<port>"` (bẫy E4a: giết chính shell đang chạy).
- **FB-10 render-diff trước = sau**, đủ 12+ route × các khổ mobile → **0 lệch**.
- Ô lọc mobile: visual 38 · chạm ≥44 · card r14/p12/g8 · 0 tràn ngang ở 360/390/430.
- `scripts/qa/wj_formcontrol.py --scope body --breakpoints 391 360`: **mẫu khác 0** (0 control =
  sai scope, không phải Pass — bẫy D6d); vi phạm giảm, không tăng.
- `wj_measure --diff` ≥13 route × 5 khổ: 0 tràn ngang · 0 lỗi JS · **0 màn mất record**; mọi ô lệch
  chiều cao phải giải trình được bằng đúng thay đổi của lượt.
- **Màn PC không đổi 1 pixel** so với mốc E4b1 (E4b1 đã là "sau" của PC).
- `-u <mod gộp> --stop-after-init` RC=0, 0 ERROR mới.
- Suite giữ **0 đỏ**. ⚠️ `work.conf` để `log_level=warn` nên dòng `odoo.tests.result` **chỉ hiện khi
  có lỗi** — muốn thấy dòng "0 failed … of N tests" phải thêm `--log-handler "odoo.tests.result:INFO"`,
  đừng suy luận "không thấy dòng = không chạy test" (mất 3 lần chạy lại ở E4b1 vì chuyện này).
  DB trắng chỉ cài khung: giữ nguyên 1 error `test_fra3_layer_guard` (**nợ có sẵn thuộc F6**).
- `check_layers.py` không thêm vi phạm (hiện 3 R1–R5 + 2 R7 có sẵn).
- Test mới **mutation-proof**: mỗi mũi phá đỏ đúng test của nó, `assert s != before` trong harness.

Ngưỡng đóng lượt: **≥90%** bảng trên.

## Kết thúc lượt

- Bump version **mọi module bị đụng** (bẫy D4) + bump `?v=` của **mọi file CSS nạp bằng `<link>` tay**
  (`wujia_portal_layout/views/assets.xml`).
- Ghi `docs/e4b2-acceptance-matrix.md`; cập nhật cột "Tiến độ theo lượt" của
  `docs/e4-filter-inventory.md` (mobile ✅).
- **Viết `docs/prompt-e4c.md`** cho lượt cuối: wiring ngày (màn Thi `kind='text'` còn chờ nối · ngày
  ngược · về trang 1 khi đổi lọc) + guard + **đóng issue** (`docs/qa-issue-ledger.yaml` + `qa_sync.py`
  → `Ready for Retest`, Dev **không** tự đặt `Done`).
- **KHÔNG** `qa_sync.py` ở lượt này, không đổi trạng thái sheet.
- Commit + push `main`, ghi rõ lệnh `-u` gộp cho lượt deploy. **Không tự deploy UAT.**
