# E4b1 — Nghiệm thu FilterBar `CMP-FB-001`, phủ hết call site **PC** (`UI-FILTER-001`, STT 139)

Lượt **E4b1** = nhân component `wj_filter_bar` của E4a ra **toàn bộ thanh lọc PC**.
Issue **CHƯA đóng** (đóng ở E4c), **không** chạy `qa_sync.py`, **không** đổi trạng thái sheet.
Lượt mobile tách riêng: prompt sẵn ở `docs/prompt-e4b2.md`.

- Cây mã trước lượt: `8ac15f8` · đo ngày 19/09/2026.
- DB copy cô lập **`wujia_e4b1`** (clone `wujia_tea_19`, **có** 2 module Khảo sát như UAT, chép cả
  `data/filestore/`), cổng **8090/8091**; test cổng **8096/8097**; sweep mutation cổng **8098/8099**.
  Không đụng `wujia_tea_19`/8019.
- **Run đối chứng**: worktree `scratchpad/e4b1/base` @ `8ac15f8` + DB `wujia_e4b1base`, cổng
  **8092/8093** — mọi số "trước" lấy từ đây, không suy đoán (bài học S57).
- Đo bằng **`em.hcm`**, `--scope body`. Khổ PC **1440 · 1024 · 992**, mobile **391 · 390 · 360**.
- Công cụ kiểm kê FB-10 **dựng lại và commit**: `scripts/qa/wj_filterbar_inventory.py`
  (bản E4a nằm ở `scratchpad/e4/`, thư mục đã mất) — có thêm **chế độ render** đọc DOM thật, vì sau
  khi migrate thì quét tĩnh không còn đọc được điều kiện nằm trong component.

## 1. Chín call site PC đã vào component

| Màn | File | Điều kiện giữ nguyên | Ghi chú lượt này |
|---|---|---|---|
| Hỗ trợ | `wujia_portal_support/views/portal_support.xml` | `state` | Bootstrap `row g-2` → component |
| Kiến thức | `wujia_portal_knowledge/views/portal_knowledge.xml` | `keyword` | nt |
| Đổi trả | `wujia_portal_return/views/portal_return_list.xml` | `q` · `date_from` · `date_to` · `state` | nt |
| Yêu cầu cập nhật | `wujia_portal_info_request/views/portal_info_request_list.xml` | `state` · `request_type` | nt — màn **dùng chung PC+mobile** |
| Giao hàng | `wujia_portal_delivery/views/portal_delivery.xml` | `q` · `date_from` · `date_to` · `bs` | `wj-pc-filterbar` tự dựng → component |
| Thông báo | `wujia_portal_notification/views/portal_notification.xml` | `tab`(hidden) · `keyword` · `date_from` · `date_to` · `type_id` · `unread` | nt + biến thể `--dense` |
| Thi | `wujia_portal_exam/views/portal_exam.xml` | `q` · `date_from`(**text**) · `date_to`(**text**) · `state` · `result` | nt + `--dense`; giữ ô ngày dạng chữ cho **E4c** |
| Báo cáo | `wujia_portal_report/views/portal_report_orders.xml` | `date_from` · `date_to` | nt |
| Đặt hàng | `wujia_portal_sale/views/portal_order_catalog.xml` | `keyword` · `category_id` | nt, giữ auto-submit của `category_id` |

**Công nợ PC** (`portal_debt.xml:293` + `:580`, nhóm 3 của plan): **0 byte thay đổi** — đo ra đã
đúng chuẩn sẵn (control **42**, radius 10, nhãn `Xem` giữ theo FB-09 item 9, `Tìm kiếm` đúng FB-02),
không có gì để căn lại. Sửa cho có là thêm rủi ro chứ không thêm giá trị.

## 2. Bảng nghiệm thu

| # | Yêu cầu (nguồn) | Đo được | Kết luận |
|---|---|---|---|
| 1 | **FB-10** — kiểm kê điều kiện lọc trước = sau | chế độ render, **12 route × 4 khổ = 48 ô**: **0 ô lệch bộ điều kiện**. 3 màn (exam · notification · return) **đổi thứ tự hiển thị** sang chuẩn component search → ngày → select — cùng bộ `name`, không thêm/bớt cái nào | **Pass** |
| 2 | FB-02 PC: control **42**, cùng baseline | hộp control: info-request **28.08→42** · knowledge **26.72→42** · support **28.08→42** · return **26.72/28.08→42** · report **50→42**; số baseline: return **2→1**, exam **2→1**, còn lại giữ 1. 12/12 thanh PC nay đo ra **[42]** | **Pass** |
| 3 | ≥1200px 1 hàng, không tràn ngang | `overflowX = false` ở **toàn bộ** ô trước và sau (13 route × 5 khổ); chiều cao card @1440 = **88** ở cả 9 màn migrate (delivery 142→88, exam 144→88) | **Pass** |
| 4 | FB-02 nhãn submit/reset | submit: `Tìm`→**Tìm kiếm** (delivery · order), `Lọc`→**Tìm kiếm** (support · return · info-request), `Áp dụng`→**Tìm kiếm** (report), icon trần→**Tìm kiếm** (knowledge). reset: `Đặt lại`→**Xóa lọc** (exam · report), `Làm mới`→**Xóa lọc** (notification). 0 màn còn nhãn cũ | **Pass** |
| 5 | Không thêm reset vào màn chưa có | số thanh PC có reset: **5 trước = 5 sau** (delivery · exam · history · notification · report). 7 màn còn lại vẫn không có | **Pass** |
| 6 | `info-request` hợp cả PC lẫn mobile | 1440 `1153→1172` · 1024/992 `1165→1184` · 390 `1428→1406` · 360 `1456→1434`; **0 tràn ngang**, record trong khung **15 = 15** ở mọi khổ | **Pass** |
| 7 | Công nợ PC giữ week/month | `wujia_portal_debt` **không đổi byte nào**; render-diff: `week` · `month` · `q` · nhãn `Xem`/`Tìm kiếm` · cao 107.5 **giống hệt** trước/sau | **Pass** |
| 8 | `wj_formcontrol.py --scope body` | mẫu **101 control** (khác 0 ⇒ scope đúng, bẫy D6d) · vi phạm **88 → 75** (giảm 13, không tăng ô nào) | **Pass** |
| 9 | `wj_measure --diff` 13 route × 5 khổ | **0 tràn ngang · 0 lỗi JS · 0 redirect ngầm**. Mất record: **knowledge −1** (30→29 @1440 · 32→31 @1024/992) — xem §3, giải trình được | **Pass có ngoại lệ** |
| 10 | Màn chưa migrate (mobile) không đổi 1 pixel | 360/390: **mọi route giống hệt** run đối chứng, trừ `/portal/info-request` (màn dùng chung, đã migrate, **thấp đi 22px**) | **Pass** |
| 11 | `-u <mod gộp> --stop-after-init` | RC=0, **0 ERROR mới** | **Pass** |
| 12 | Suite giữ 0 đỏ | `0 failed, 0 error(s) of 601 tests` trên `wujia_e4b1` (+21 test mới của lượt). DB trắng chỉ cài khung (`wujia_fra3_layout`): **0 failed / 1 error / 142 test** — đúng một `test_fra3_layer_guard` **nợ có sẵn thuộc F6**, không phải do lượt này. ⚠️ `log_level=warn` nuốt dòng INFO tổng kết — phải `--log-handler "odoo.tests.result:INFO"` mới thấy | **Pass** |
| 13 | `check_layers.py` | giống hệt cây đối chứng: **3 R1–R5 + 2 R7 có sẵn**, không thêm vi phạm | **Pass** |
| 14 | Test mới **mutation-proof** | `scratchpad/e4b1/mutations.py` — **11 mũi M1–M11**, mỗi mũi `assert s != before` (phép phá phải ăn). Kết quả: **11/11 đỏ đúng guard của nó**; mốc chạy sạch trước sweep = **0 đỏ**. 21 test mới: 16 ở `wujia_portal_base/tests/test_scan_e4_filter_bar.py` (quét chéo module, đúng F5b) + 5 ở `wujia_portal_layout/tests/test_e4_filter_bar.py` (hợp đồng component) | **Pass** |
| 15 | Không đụng code anh Thái | 0 byte trong `wujia_portal_inspection` / `wujia_franchise*` / `wujia_mobile_*`; họ class cũ mà Khảo sát còn dùng (`wj-pc-filter-control`, `wj-pc-filter-search`) **thu hẹp vào `.wj-inspection-pc`** chứ không xoá (bẫy E3c), có test chặn | **Pass** |
| 16 | Bump version + `?v=` | 11 module: layout `19.0.52.0.0` · support `3.22.0` · knowledge `3.15.0` · return `3.4.0` · info_request `1.11.0` · delivery `3.15.0` · notification `2.15.0` · exam `5.16.0` · report `2.2.0` · sale `4.18.0` · base `19.0.7.17.10`; `_pc_components.css` `?v=1295→1301` | **Pass** |

## 3. Hai thứ phải nói rõ với BA (không giấu)

1. **Kiến thức PC cao thêm 42px và mất 1 record trong khung** (30→29 @1440). Trước lượt, thanh lọc
   màn này là một ô tìm kiếm trần cao **39px**; chuẩn BA (control 42 trong card 88) làm nó cao lên
   đúng bằng 9 màn còn lại. Đây là **hệ quả trực tiếp của chính chuẩn FB-02**, không phải lỗi dựng.
   Báo cáo PC cũng lên **80 → 88** vì cùng lý do. Nếu BA muốn giữ record, phải đổi **chuẩn**, không
   phải đổi riêng màn này.
2. **Nút "Xóa lọc" của Thông báo đổi cách chạy**: trước là reload cả trang, nay là link
   `data-wj-nav` do `wj_ajax_list.js` bắt (giống 8 màn kia) — **cùng URL đích**, chỉ khác là không
   nháy trang. Đây là hệ quả của việc thống nhất về một component, cố ý.

## 4. Điều kiện lọc: bộ giống hệt, thứ tự hiển thị đổi ở 3 màn

| Màn | Trước | Sau |
|---|---|---|
| Thi | `state` · `result` · `q` · `date_from` · `date_to` | `q` · `date_from` · `date_to` · `state` · `result` |
| Thông báo | `keyword` · `type_id` · `unread` · `date_from` · `date_to` · `tab` | `tab` · `keyword` · `date_from` · `date_to` · `type_id` · `unread` |
| Đổi trả | `state` · `q` · `date_from` · `date_to` | `q` · `date_from` · `date_to` · `state` |

Thứ tự mới = thứ tự chuẩn của component (search → ngày → select), đúng thứ tự BA mô tả ở FB-02.
FB-10 nói về **bộ điều kiện**, không nói về thứ tự — nên vẫn tính Pass, nhưng ghi ra đây để retest
không tưởng là mất/thêm ô.

## 5. Chốt lượt

- Không đóng issue (E4c mới đóng) · không `qa_sync.py` · không đổi sheet · **không tự deploy UAT**.
- Lệnh `-u` gộp cho lượt deploy:

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_knowledge,\
wujia_portal_return,wujia_portal_info_request,wujia_portal_delivery,wujia_portal_notification,\
wujia_portal_exam,wujia_portal_report,wujia_portal_sale
```
