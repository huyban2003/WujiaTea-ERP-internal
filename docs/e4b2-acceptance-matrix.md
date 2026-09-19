# E4b2 — Nghiệm thu FilterBar `CMP-FB-001`, phủ hết call site **mobile** (`UI-FILTER-001`, STT 139)

Lượt **E4b2** = nhân component `wj_filter_bar` của E4a/E4b1 ra **toàn bộ thanh lọc mobile**.
Issue **CHƯA đóng** (đóng ở E4c sau khi vá wiring ngày), **không** chạy `qa_sync.py`, **không** đổi
trạng thái sheet, **không** tự deploy UAT.

- Cây mã trước lượt: `7818f36` · đo ngày 19/09/2026.
- DB copy cô lập **`wujia_e4b1`** (bản clone `wujia_tea_19` của lượt trước, **có** 2 module Khảo sát
  như UAT, có `data/filestore/`), cổng **8090/8091**; test **8096/8097**; sweep mutation **8098/8099**.
  Không đụng `wujia_tea_19`/8019.
- **Run đối chứng**: worktree `scratchpad/e4b2/base` @ `7818f36` + DB `wujia_e4b2base`, cổng
  **8092/8093** — mọi số "trước" lấy từ đây (bài học S57), không tin bảng chép tay trong prompt.
- Đo bằng **`em.hcm`**, `--scope body`. Khổ PC **1440 · 1024 · 992**, mobile **391 · 390 · 360**
  (+ **430** cho phép đo tràn ngang).

## 1. Sáu call site mobile đã vào component

| Màn | File | Điều kiện giữ nguyên | Ghi chú lượt này |
|---|---|---|---|
| Lịch sử mua hàng | `wujia_portal_purchase_history/views/portal_history.xml` | `page_size`(hidden) · `q` · `date_from` · `date_to` | kẹp ngày `max`/`min` → `clamp` của component; chip + lỗi đi qua slot `fb_chips`/`fb_error` |
| Thông báo | `wujia_portal_notification/views/portal_notification.xml` | `unread`(hidden) · `keyword` | chip = part template `mchips`, giữ trong form |
| Hỗ trợ | `wujia_portal_support/views/portal_support.xml` | `state`(hidden) · `q` | chip `#wj-sup-mchips` giữ nguyên văn |
| Kiến thức | `wujia_portal_knowledge/views/portal_knowledge.xml` | `keyword` | chip `#wj-know-mchips` giữ nguyên văn |
| Đổi trả | `wujia_portal_return/views/portal_return_list.xml` | `q` · `date_from` · `date_to` · `state` | select `state` **xuống sau 2 ô ngày** theo thứ tự component (xem §4), giữ auto-submit |
| Báo cáo đặt hàng | `wujia_portal_report/views/portal_report_orders.xml` | `date_from` · `date_to` | vào hẳn component theo **biến thể BA 04-DateRangeOnly**: nút tìm nằm **cùng hàng** với 2 ô ngày |

**Đặt hàng mobile** (`portal_order_catalog.xml`): giữ dáng **hàng trần** (màn này không có thẻ lọc —
bọc thẻ là đổi thiết kế màn, không phải chuẩn hoá) nhưng **kéo hình học về đúng chuẩn**: ô tìm và nút
kính lúp **44/r12 → 38/r10**, vùng chạm giữ **44** (ô tìm bọc `<label>`, nút dùng `::before` 44×44).
ProductCard và khối khung giờ **không đụng byte nào**; chip `#wj-ord-mchips` giữ nguyên vị trí.

**Công nợ mobile** (`portal_debt.xml:17`, 2 call site): **0 byte thay đổi** — thanh lọc riêng đã được
duyệt Figma v31 (control **54**, giữ `f_name` + nút `Xem` theo FB-09 item 9). Đo lại trước/sau để
chứng minh không hồi quy: `54/54` giống hệt.

**Màn Thi mobile** (`portal_exam.xml:130`): **cố ý không đụng** — chốt của chủ dự án 19/09
("làm chuẩn, phiên này không ổn thì phiên sau, miễn giải quyết tới nơi"): khối ngày của màn này
**chưa nối controller**, nên **E4c** sẽ vừa đưa vào component vừa nối ngày **một thể**, thay vì đẻ
một knob tạm `fb_demo` trong component rồi phiên sau gỡ. Có test chặn đi kèm (ghi nợ).

## 2. Bảng nghiệm thu

| # | Yêu cầu (nguồn) | Đo được | Kết luận |
|---|---|---|---|
| 1 | **FB-10** — điều kiện lọc trước = sau | chế độ render, **13 route × 6 khổ = 78 ô**: in ra `FB-10 (render): ĐẠT — 0 lệch`. Đổi thứ tự hiển thị ở **1 màn** (Đổi trả, xem §4) — cùng bộ `name`, không thêm/bớt cái nào | **Pass** |
| 2 | Ô lọc mobile: nhìn thấy **38**, chạm **≥44** (Q1 12/09) | 6/6 thanh migrate + Đặt hàng đo ra **38/44** ở cả 3 loại control (ô tìm · ô ngày · select) và nút kính lúp. Trước lượt: ô tìm **44/44**, ô ngày Báo cáo **22** trong nút **48** | **Pass** |
| 3 | Thẻ lọc mobile **r14 / p12 / gap 8** | 6/6 thẻ: `border-radius 14px · padding 12px · gap 8px` (token `--wujia-surface-*` khổ ≤991) | **Pass** |
| 4 | Không tràn ngang @360/390/430 | `scrollWidth == innerWidth` ở **toàn bộ** 10 route × 3 khổ, trước và sau | **Pass** |
| 5 | `wj_formcontrol.py --scope body --breakpoints 391 360` | mẫu **82 control** (khác 0 ⇒ scope đúng, bẫy D6d) · vi phạm **14 → 4**, không ô nào tăng. 4 ô còn lại = 2 select PC của `/portal/info-request` (màn dùng chung, PC 42 < ngưỡng chạm 44) — **có y hệt ở run đối chứng**, không phải do lượt này | **Pass** |
| 6 | `wj_measure --diff` 13 route × 5 khổ | **0 tràn ngang · 0 lỗi JS · 0 màn mất record**. Đúng **1 ô lệch chiều cao**: `/portal/reports/orders` `1515→1529` (390) và `1534→1548` (360), **+14** — giải trình ở §3 | **Pass** |
| 7 | Mốc PC **không đổi 1 pixel** | 1440 · 1024 · 992: **0 route lệch** so với mốc E4b1 (`wj_measure --diff` không in dòng nào ở 3 khổ PC) | **Pass** |
| 8 | `-u <9 module> --stop-after-init` | RC=0, **0 ERROR** | **Pass** |
| 9 | Suite giữ 0 đỏ | `0 failed, 0 error(s) of **621** tests` trên `wujia_e4b1` (E4b1 là 601 ⇒ +20 test của lượt này). DB trắng chỉ cài khung (`wujia_fra3_layout`): **0 failed / 1 error / 149 test** — đúng một `test_fra3_layer_guard`, **nợ có sẵn thuộc F6**. ⚠️ `log_level=warn` nuốt dòng INFO tổng kết ⇒ luôn `--log-handler "odoo.tests.result:INFO"` | **Pass** |
| 10 | `check_layers.py` | giống hệt cây đối chứng: **3 R1–R5 + 2 R7 có sẵn**, không thêm vi phạm | **Pass** |
| 11 | Test mới **mutation-proof** | `scratchpad/e4b2/mutations.py` — **20 mũi M1–M20**, mỗi mũi `assert s != before` (phép phá phải ăn). **20/20 đỏ đúng guard của nó**; mốc chạy sạch trước và sau sweep đều **0 đỏ**. 20 test mới: **13** ở `wujia_portal_base/tests/test_scan_e4_filter_bar.py` (quét chéo module) + **7** ở `wujia_portal_layout/tests/test_e4_filter_bar.py` (hợp đồng component) — đúng luật sở hữu F5b. Guard `test_khong_dung_module_anh_thai` **cố ý không có mũi phá** (phá = sửa file anh Thái) | **Pass** |
| 12 | Không đụng code anh Thái | **0 byte** trong `wujia_portal_inspection` / `wujia_franchise*` / `wujia_mobile_*`; đã kiểm trước khi dọn CSS: nhóm Khảo sát **không dùng** họ `wj-filter-*` ở mobile (chỉ `wj-ajax-search-form` + `wj-inspection-*`) nên lượt này không phải thu hẹp selector như E4b1 làm ở PC. Có test chặn | **Pass** |
| 13 | Bump version + `?v=` | 9 module: layout `19.0.53.0.0` · base `19.0.7.17.11` · purchase_history `19.0.3.13.0` · notification `19.0.2.16.0` · support `19.0.3.23.0` · knowledge `19.0.3.16.0` · return `19.0.3.5.0` · report `19.0.2.3.0` · sale `19.0.4.19.0`; `_components.css` `?v=1299 → 1302` | **Pass** |

## 3. Ba thứ phải nói rõ với BA (không giấu)

1. **Màn Báo cáo (mobile) cao thêm 14px** — và đây là **cộng dồn của hai thay đổi ngược chiều**:
   thẻ lọc **thấp đi 2px** (72 → **70**, vì ô ngày về chuẩn 38 thay cho nút `Tìm` cao 48), nhưng thẻ
   chuẩn `.wj-filter-card` có `margin-bottom: 16px` trong khi thanh cũ `.wj-rep-mfilter` cố ý đặt
   `margin-bottom: 0`. **−2 + 16 = +14**. Đây là cái giá của việc Báo cáo dùng **chung một vỏ** với 6
   màn còn lại; giữ `margin-bottom: 0` riêng cho Báo cáo là dựng lại đúng cái ngoại lệ mà lượt này đi
   xoá.
2. **Nợ nhịp trang (G2) — 16px chồng lên gap 8px.** Luật G2 nói nhịp dọc mobile chỉ đến từ `gap` của
   khung trang (8px), nhưng `.wj-filter-card` đang thêm `margin-bottom: 16px` ⇒ khoảng cách
   *thanh lọc → danh sách* là **24px** trong khi mọi cặp thẻ khác là **8px**. Nợ này **có sẵn từ E4a**
   và áp lên **cả 7 màn** dùng `.wj-filter-card`, không phải do E4b2 đẻ ra; lượt này chỉ làm nó lộ ra
   ở màn Báo cáo. **Không sửa trong E4b2** vì gỡ 16px là đổi nhịp 7 màn cùng lúc — việc của cụm nhịp
   (E5), đã ghi vào `docs/prompt-e4c.md` để không rơi.
3. **Nhãn nút Báo cáo đổi từ chữ `Tìm` sang nút kính lúp** (cùng hàng với 2 ô ngày, đúng biến thể BA
   04-DateRangeOnly). Nút vẫn có **tên đọc được** `aria-label="Tìm kiếm"` (FB-02) và vùng chạm 44.
   Màn **Đặt hàng** thì ô tìm nhỏ lại về 38 — nhìn "gầy" hơn trước nhưng **vùng bấm không đổi** (44).

## 4. Điều kiện lọc: bộ giống hệt, thứ tự hiển thị đổi ở 1 màn

| Màn | Trước | Sau |
|---|---|---|
| Đổi trả (mobile) | `q` → `state` → `date_from` → `date_to` | `q` → `date_from` → `date_to` → `state` |

Thứ tự của component là **tìm → ngày → select** (E4b1 đã áp đúng như vậy cho 3 màn PC). Bộ `name`
không thêm/bớt cái nào — FB-10 render-diff xác nhận 0 lệch. Retest thấy ô trạng thái "chuyển chỗ" là
đúng thiết kế, không phải mất ô.

## 5. Dọn CSS: xoá cái chết, thu hẹp cái còn người dùng

| Việc | Chi tiết |
|---|---|
| Xoá | họ `.wj-rep-mfilter*` (52 dòng, `wujia_portal_report/static/src/css/portal_report.css`) — đã hết call site sau khi Báo cáo vào component; đã grep XML/JS, không còn ai tham chiếu |
| Thu hẹp | khối 44px của **D6c** trong `_components.css` (`.wj-filter-date`, `.wj-filter-search-btn`…) **không xoá** mà thu về `.wujia-mexam …` — màn Thi còn dùng, xoá là đẻ vi phạm vùng chạm ở chính màn ta đã hẹn không đụng (bẫy E3c) |
| Giữ | `.wj-mform .form-control { min-height: 48px }` — **chuẩn form BH-009**, khác chuẩn ô lọc (38); có test chặn gỡ nhầm |
| Thêm | `align-items: center` cho `.wj-filter-search` và `.wujia-morder-search` — nút 38 đứng cạnh wrapper 44, thiếu dòng này là nút lệch lên 3px ở mọi màn |

## 6. Hai công cụ đo bị sai phép đo, đã vá

Cả hai đều là **lỗi công cụ, không phải lỗi giao diện** — và cả hai đều báo "vi phạm" ở đúng chỗ ta
vừa làm đúng, nên nếu tin máy thì đã đi sửa hỏng code:

1. `scripts/qa/wj_filterbar_inventory.py` — metric vùng chạm dùng
   `el.closest('label, .wj-filter-search-field, .wj-filter-date__box')`: `closest()` trả về tổ tiên
   **gần nhất khớp bất kỳ selector nào**, nên bắt trúng hộp 38 thay vì `<label>` 44 ⇒ báo 38.
   Sửa: tìm `label` trước, rồi mới tới wrapper. Đồng thời sửa nhận diện redirect (route có `?query`
   bị so cả chuỗi với path đã strip ⇒ báo `redirect:` giả).
2. `scripts/qa/wj_formcontrol.py` — `el.closest('label, .wj-filter-date, .wj-filter-select')` khớp
   **cả chính nó**: `select.wj-filter-select` tự khớp mình (38) thay vì wrapper `.wj-filter-selectwrap`
   (44) ⇒ đếm nhầm 1 vi phạm vùng chạm ở màn Đổi trả. Sửa: tìm wrapper từ **phần tử cha** trở lên.

## 7. Ba test cũ phải sửa theo chuẩn mới (không phải "nới test cho xanh")

| Test | Vì sao phải sửa |
|---|---|
| `wujia_portal_return/tests/test_return_form_d6c.py::test_o_loc_dat_nguong_cham_44` | khẳng định **luật 44 quét rộng của D6c** còn sống. Q1 (12/09) đã thay luật đó bằng **38 nhìn thấy + 44 vùng chạm** ⇒ test đổi sang khẳng định wrapper `.wj-filter-date--hit` / `.wj-filter-selectwrap` / `label.wj-filter-search-field` cao 44. Vẫn là **một** khẳng định cứng, không nới |
| `…layout/tests/…::test_nut_tim_38_co_vung_cham_44_bang_pseudo` | selector nay gộp thêm bố cục biến thể 04 (nút cùng hàng ngày) ⇒ đọc theo nhóm selector mới |
| `…base/tests/…::test_pc_lich_su_dat_hang_goi_component_va_giu_page_size` | màn Lịch sử nay có **2** call site trong cùng file (PC + mobile) ⇒ lọc đúng cái PC, như test màn Giao hàng đã làm từ E4a |

## 8. Một sự cố của harness, đã vá tận gốc

Sweep mutation bị dừng giữa chừng (Ctrl-C ngoài kế hoạch) **để lại file đã phá trong cây mã** —
`id="wj-sup-mchips2"` nằm lại, và lần chạy suite ngay sau đó đỏ đúng cái guard AJAX của nó. Không
mất gì (guard bắt được), nhưng harness đã được vá: `atexit` + bắt `SIGTERM`/`SIGINT` phục hồi mọi
file trước khi thoát. **Không bắt `SIGHUP`** — `nohup` đang vô hiệu nó, bắt lại là tự chết khi shell
thoát (đã dính một lần ở chính lượt này).

## 9. Lệnh deploy (gộp một lượt)

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,\
wujia_portal_notification,wujia_portal_support,wujia_portal_knowledge,\
wujia_portal_return,wujia_portal_report,wujia_portal_sale
```

**Chưa đóng issue.** Lượt cuối `E4c` (prompt: `docs/prompt-e4c.md`) mới nối wiring ngày, đưa màn Thi
mobile vào component, rồi ghi `docs/qa-issue-ledger.yaml` + `qa_sync.py` → `Ready for Retest`
(Dev **không** tự đặt `Done`).
