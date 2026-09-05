# Prompt D4e — SurfaceCard `CMP-SC-001` cho trang Báo cáo đặt hàng

> Dán nguyên khối này vào đầu phiên. Đọc `docs/d4-surfacecard-inventory.md` **§13** trước,
> rồi mới tới §4 và §9 — §13 sửa lại con số mà §11.4/§12.5 ghi sai.

## Phạm vi — **7 call site / 1 file / 1 module**

`custom/wujia_portal_report/views/portal_report_orders.xml`

| Họ | Dòng | Thẻ | Ghi chú |
|---|---|---|---|
| `wj-rep-mcard` ×3 | 85 · 98 · 132 | **`<section>`** | mobile; `:85` có kèm `--chart` |
| `wj-pc-metric-card` ×4 | 198 · 209 · 219 · 230 | `<div>` | PC, 4 ô KPI của `.wj-rep-pcmetrics` |

`-u wujia_portal_report,wujia_portal_layout` — **đúng một lần**. Không module mới, không
migration. Bump `?v=` **chỉ khi** đụng 1 trong 4 file CSS nạp bằng `<link>` tay
(`_variables` · `_components` · `_pc_components` · `_pc_account`, hiện `?v=1200`);
`portal_report.css` nằm trong bundle nên không cần.

**Chạy lại phép đếm trước khi tin bảng trên** — quy tắc cứng, đã sai 3 lần liên tiếp:

```
python3 scripts/qa/wj_inventory.py --sites wj-rep-mcard wj-pc-metric-card
```

## Ba fork phải hỏi chủ dự án TRƯỚC khi code

1. **4 lượt gallery `pc_preview.xml`** (`/portal/_pc-preview`, inventory §13.2) — kiểm kê
   bỏ sót. Đây là bản tham chiếu component để đối chiếu SVG của BA, **để lệch thì gallery
   nói dối**. Kéo vào D4e hay tách lượt riêng?
   Route này **`auth='user'` + chặn user không phải nội bộ** ⇒ phải đăng nhập `admin`
   (mật khẩu dev: `admin` — **không** phải `wujia_admin`, đó là mật khẩu master của trình
   quản lý CSDL). Đã bấm thử 05/09: HTTP **200**, render đúng **4** shell.

2. **4 lượt `wj-pc-metric-card` màn Khảo sát** — trước xếp "không đo được" vì
   `wujia_portal_inspection` `uninstalled`; nay DB dev đã cài và `/portal/inspection` trả
   200. Tách khỏi nhóm *provisional* hay vẫn chờ BA chốt field mapping?
3. **Hai món nợ D4d mang sang** — nhịp header→body PC **18/23/25** (D4d #6) và hai card còn
   `style="padding:14px 14px 0"` inline ở `portal_franchise_information` /
   `portal_support_detail` (D4d chốt #3). Hội tụ ở D4e hay để riêng?

## Rủi ro riêng của lượt này

- **`wj-rep-mcard` không có viền hẳn** (`portal_report.css:318`). Thêm viền là **đổi hình
  học thật** của 3 khối báo cáo, không phải đổi màu. Phải có ảnh trước/sau.
- **Rule scope đè rule base:** `.wj-rep-pcmetrics .wj-pc-metric-card { padding: 0 16px }`
  (inventory §9 mục 3). Theo **luật D4 #7**: khi migrate phải **rút hẳn**
  `background`/`border`/`border-radius`/`padding`/`box-shadow`/`gap` khỏi rule cũ — đừng để
  hai rule cùng `(0,1,0)` rồi phân xử bằng thứ tự nguồn.
- **Cả 3 `wj-rep-mcard` là `<section>`.** QWeb Odoo 19 **không có directive đổi tên thẻ**
  (`ir_qweb.py:1705`, chốt ở C8) ⇒ `t-call` sẽ nuốt mất `<section>`. Cách đúng, đã chốt ở
  D4c: **thêm thẳng class `.wj-surface-card…`** vào chính thẻ đó, giữ lớp cũ.
- `:85` mang `--chart` và bọc ApexCharts. S55 đã có tiền lệ `yaxis.title=undefined` làm
  ApexCharts chết câm ⇒ sau khi sửa phải xác nhận **biểu đồ vẫn vẽ**, không chỉ xem HTML.

## Luật đã trả giá — đừng phát minh lại

1. **Giữ lớp cũ** qua `sc_class`. `:is()` lấy đặc hiệu của **đối số mạnh nhất**, ba danh
   sách hover/pressed ở `_interaction.css` là `(0,3,0)`; bỏ lớp cũ là hover chết câm (D4d #9).
2. **Đặc hiệu đếm so với rule CÙNG FILE**, không chỉ so với component. Bẫy này đã nổ **hai
   lần** (D3b `--flush`, D3d `--sechead`).
3. **Đo rồi mới thêm rule** — hai lượt D4b/D4c đều kết luận là *không thêm gì*.
4. **Guard chứng minh bằng đột biến**, và phải `grep` xác nhận đột biến **đã vào file** rồi
   mới kết luận (D4d #2: `sed` neo trượt thụt lề ⇒ báo "guard rỗng" oan cho guard tốt).
5. **`xml_id` phải TRA, không đoán** (D4d #3). Một file XML có nhiều `<template id=…>`.
6. **Đọc log ĐÚNG CHỖ.** `logfile` trong `odoo.conf` nuốt stdout, và `wujia_core` xoay log
   sang `logs/<năm>/<tháng>/<ngày>.log`. "RC=0, 0 ERROR" trên file rỗng là **xanh giả**
   (D4d #1). Ghi `N=$(wc -l < $L)` trước, `tail -n +$((N+1))` sau.
7. Chạy test thì phải **đổi cổng** nếu server dev đang chạy: `--http-port 8099
   --gevent-port 8100`. Không đổi thì RC=1 vì *Address already in use*, dễ đọc nhầm là test đỏ.

## Nghiệm thu

```
# mốc trước
python3 scripts/qa/wj_measure.py --portal-login anh.owner --screenshots --settle 700 \
        --out scratchpad/d4e-before.json
#  … sửa code, -u một lần …
python3 scripts/qa/wj_measure.py --portal-login anh.owner --screenshots --settle 700 \
        --out scratchpad/d4e-after.json
python3 scripts/qa/wj_measure.py --diff scratchpad/d4e-before.json scratchpad/d4e-after.json
```

**Mốc đã đo sẵn ngày 05/09 trên `main` (sau D4d)** — dùng làm bản "trước" nếu chưa sửa gì:
`scratchpad/baseline-after-d4d.json` · 127 bề mặt / 65 ô · **0 lỗi JS · 0 tràn ngang ·
0 redirect ngầm** · RULE 2 histogram `16×2 · 18×54 · 22×6 · 24×3` · nhịp `0×9 · 8×2 · 12×33`.

Riêng `/portal/reports/orders`: `1440 h=907 card=7 rec=29` · `1024 h=919 card=7 rec=31` ·
`992 h=925 card=7 rec=31` · `390 h=1255 card=3 rec=14` · `360 h=1255 card=3 rec=14`.

Ngưỡng phải đạt:

- **0 ô mất record** (acceptance #11 của BA — `--diff` in thẳng `⚠ MẤT RECORD`);
- RULE 1 `HIERARCHY` **không tăng** so với mốc;
- nhịp header→body **không rời khỏi 12** ở những ô đang là 12;
- 0 lỗi JS · 0 tràn ngang · 0 redirect ngầm;
- **ảnh chụp** 5 khổ, soi mắt 3 thẻ `wj-rep-mcard` — đây là lượt đổi *khung*, mà số đo Pass
  hết mà bố cục vẫn vỡ đã xảy ra hai lần (D3e badge trôi 966px, D3d mất 28px nhịp);
- test `-u wujia_portal_layout --test-tags wujia_surface_card_d4` giữ **0 failed / 0 error**
  (mốc hiện tại **45 test**), test mới phải chứng minh bằng đột biến.

## Ba vấn đề có sẵn phát hiện lúc đo mốc — **không phải việc của D4e**, đừng sửa lẻ

1. **RULE 1 vỡ ở `/portal/delivery` PC (3 ô: 1440 · 1024 · 992).** Empty state
   `<h3 class="wj-pc-dlv-inner__title">Không có chuyến giao"` render **28px** trong khi tiêu
   đề card là **22px**. Thuộc họ empty-state — inventory §12.2 đã xếp `wj-empty-state` về
   **CMP-ES-001** (20 lượt). Đề nghị mở lượt riêng.
2. **Tiêu đề card lệch chuẩn 18px ở 4 màn:** `/portal/delivery` **22** · `/portal/order`
   **22** · `/portal/inspection` **24** · `/portal/info-request` mobile **16**. Nợ RULE 2,
   ghép **D7+** hoặc làm kèm khi lượt nào động đúng file đó.
3. **15 card không có `.wj-card-header` nào** ⇒ không đo được nhịp. Là số lượng công việc
   còn lại của cụm D3, không phải lỗi.
