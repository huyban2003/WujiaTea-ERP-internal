# D4e — SurfaceCard lượt 4: `wj-pc-metric-card` + `wj-rep-mcard`

> Dán nguyên khối này sau khi chạy `/wujia-start`.

## 0. Bối cảnh

`UI-SURFACECARD-001` (STT 127 · `CMP-SC-001` · tab `UI Component` gid 488333015) là issue BA
`Ready for Dev` chuẩn hoá **khung card** toàn Portal. Component
`wujia_portal_layout.wj_surface_card` đã dựng ở D4b và chạy thật trên **98 thẻ** qua D4b + D4c +
D4d — tiến độ **98/384 lượt ≈ 26%**.

Hồ sơ phải đọc trước khi gõ dòng code đầu tiên:

| File | Đọc phần nào |
|---|---|
| `docs/d4-surfacecard-inventory.md` | §4 dòng 124 + 128 · §6 bảng "không đo được" dòng 100–103 · §9 bẫy #3 dòng 233 · **§12 (đính chính sau D4d)** |
| `docs/next-session-clusters-D.md` | **Luật chung #1…#9** · bảng thứ tự lượt · **🔴 Bài học D4d (10 mục)** |
| `docs/d4d-acceptance-matrix.md` | khuôn bảng nghiệm thu — D4e viết `docs/d4e-acceptance-matrix.md` theo đúng khuôn này |
| `docs/qa-issue-ledger.yaml` | 4 entry tiến độ D4b/D4c/D4d — **giữ nguyên `Ready for Dev`** |
| `custom/wujia_portal_layout/views/wj_surface_card.xml` | hợp đồng props (`sc_variant`/`sc_density`/`sc_body`/`sc_tone`/`sc_href`/`sc_class`/`sc_link_class`/`sc_id`) |

---

## 1. 🔴 Việc ĐẦU TIÊN: kiểm kê lại. Con số của inventory SAI ba lần.

Inventory ghi **44 + 16 = 60 lượt / 2 file**. Đếm shell thật (`class="…"`, loại con BEM `__`):

| File | `wj-pc-metric-card` shell | `wj-rep-mcard` shell |
|---|---:|---:|
| `custom/wujia_portal_report/views/portal_report_orders.xml` | **4** | **3** (2 thường + 1 `--chart`) |
| `custom/wujia_portal_inspection/views/portal_inspection_detail_templates.xml` | **4** | 0 |
| `custom/wujia_portal_layout/views/pc_preview.xml` | **4** | 0 |
| | **12** | **3** |

**Phạm vi thật ≈ 15 shell / 3 file**, không phải 60 / 2. Ba sai lệch:

1. **Đếm thô bắt cả con BEM** — `wj-pc-metric-card` có `__icon` `__body` `__label` `__value`
   (68 lượt thô / 12 shell); `wj-rep-mcard` có `__head` `__title` `__meta` `__body`
   (16 lượt thô / 3 shell). **Đúng lỗi đã làm kiểm kê D4d phồng 50 → 51** (bài học D4d #10).
2. **Bỏ sót nguyên một file**: `wujia_portal_layout/views/pc_preview.xml` (route
   `/portal/_pc-preview`, gallery component nội bộ). 44 của inventory = 20 report + 24 inspection —
   không có pc_preview.
3. Dòng 124 ghi `wj-pc-metric-card` là *"2 file"* và đệm *"`0 22`, việc cần làm p 22→16"* —
   **file là 3**, và xem §3 dưới đây: đệm dọc **bằng 0**, chiều cao do `min-height` gánh.

**Vẫn phải làm lại luật "kiểm kê là SÀN không phải TRẦN"**: grep từng token
(`--wj-pc-metric-h`, `--wj-pc-card`, `--wj-pc-border-soft`, `--wujia-card-radius`,
`--wujia-bg-card`) tìm bề mặt trắng **không có chữ "card"/"metric" trong tên**. Tìm ra thì **ghi
bổ sung vào inventory §13 rồi HỎI**, đừng lặng lẽ kéo vào phạm vi. D4d bắt được 26 lượt kiểu này.

---

## 2. Neo CSS

| Rule | Neo | Đang khai |
|---|---|---|
| `.wj-pc-metric-card` | `wujia_portal_layout/static/assets/css/_pc_components.css:132` | `display:flex · align-items:center · gap:16px · min-height:var(--wj-pc-metric-h) · padding:0 22px · background:var(--wj-pc-card) · border:1px solid var(--wj-pc-border-soft) · border-radius:16px` |
| `.wj-rep-pcmetrics .wj-pc-metric-card` | `wujia_portal_report/static/src/css/portal_report.css:74` | 🔴 **override liên module (0,2,0)**: `min-height:100px · gap:14px · padding:0 16px` |
| `.wj-rep-mcard` | `wujia_portal_report/static/src/css/portal_report.css:318` (**trong `@media` mobile**) | `background:var(--wujia-bg-card) · border-radius:var(--wujia-card-radius)` — **KHÔNG viền** |
| `.wj-rep-mcard--chart .wj-rep-mcard__body` | `portal_report.css:346` | `padding: 0 12px 8px` — chú thích nói *"card về đúng 258"* |

Token liên quan: `--wj-pc-metric-h: 96px` (`_variables.css:94`) · `--wujia-card-radius: 16px`
(`:120`) · `--wj-pc-card` → `--wujia-bg-card` (`:75`) · `--wj-pc-border-soft` →
`--wujia-border-soft` (`:77`).

---

## 3. 🔴 Bốn câu phải HỎI CHỦ DỰ ÁN trước khi sửa — đừng tự quyết

### 3.1 Gỡ `min-height: 96px` sẽ làm thẻ KPI **thấp đi**, không phải cao bằng nhau

BA cấm khoá chiều cao, Luật #9 chốt cách đúng là `height: 100%`. Nhưng họ này **đệm dọc = 0**
(`padding: 0 22px`) — toàn bộ chiều cao 96px đến từ `min-height`. Tính thật:

| Cách | Chiều cao thẻ |
|---|---|
| hiện tại | **96** (report override thành **100**) |
| bỏ `min-height`, dùng `--compact` (đệm 16) | icon 52 + 16×2 = **84** |
| bỏ `min-height`, dùng `--regular` (đệm 20) | icon 52 + 20×2 = **92** |

Không cách nào ra đúng 96/100. Thêm nữa: 4 thẻ nằm trong
`.wj-pc-metric-grid { display:grid; grid-template-columns:repeat(4,1fr) }` ⇒ **grid item mặc định
`align-self: stretch`, đã cao bằng nhau sẵn** — `min-height` ở đây là **sàn chiều cao thiết kế**,
không phải mẹo cân hàng. Bỏ nó là **đổi hình học dải KPI của trang báo cáo**.

**Hỏi:** (a) chấp nhận thẻ thấp xuống 96→92 (`regular`) hay 96→84 (`compact`)? (b) hay giữ
`min-height` và ghi LIMIT "THIẾT KẾ" như `.wj-debt-summary { height:142px }` của D4c? — **Dev
trình số, không tự chọn.**

### 3.2 `.wj-rep-mcard` **không có viền** — thêm viền là đổi hình học 3 khối báo cáo mobile

Inventory §1 dòng 28 lấy chính ca này làm ví dụ *"BA viết thẳng border/shadow không thống nhất"*.
Nhưng `--chart` được căn để card ra **đúng 258px**; thêm viền 1px trên+dưới thành **260**. Và
đây là họ **mobile** dùng `--wujia-card-radius: 16px` trong khi BA cột mobile đòi **14**.

**Hỏi:** thêm viền + r16→14 (đúng BA, lệch mockup 2px), hay giữ dáng và ghi LIMIT?

### 3.3 Override liên module `.wj-rep-pcmetrics .wj-pc-metric-card` — **lần này SỐNG**

Khác bẫy #4 của D4d (rule chết, 0 phần tử khớp). Đặc hiệu **(0,2,0)** thắng chủ sở hữu
`.wj-surface-card` (0,1,0), lại **nạp sau** ⇒ rút dáng khung khỏi rule base mà để nguyên rule này
thì **report vẫn giữ đệm 16 / gap 14 / min-height 100**, ba file còn lại đổi — thành **variant
theo route, đúng thứ BA cấm**.

**Bắt buộc đo trước:** đếm phần tử khớp lúc chạy (như D4d đã làm với bẫy #4) rồi mới quyết hội tụ
hay giữ. Cùng rule này còn có `.wj-rep-pcmetrics .wj-pc-metric-card__value { font-size: 24px }`
(component chung 30px) — **cỡ chữ không phải dáng khung, để yên**, nhưng phải ghi vào matrix.

### 3.4 `gap: 16px` đang ở **rule gốc** — vi phạm Luật #8

Luật #8: `gap` **chỉ** ở biến thể `--summary`. Inventory dòng 124 đã xếp họ này vào `summary` ⇒
`gap` về `var(--wujia-surface-gap)` = **12 (PC) / 8 (mobile)**, không còn 16/14.

⚠️ **`.wj-surface-card--summary` chỉ khai `gap`, KHÔNG khai `display:flex`** — xem
`_components.css:634`. Phải **giữ `display:flex; align-items:center`** ở rule họ (không phải dáng
khung), y như D4d giữ `display:flex; flex-direction:column` cho `.wj-filter-card`. Bỏ đi là
`gap` vô tác dụng và icon/label vỡ hàng.

---

## 4. Chặn kỹ thuật — và cách gỡ đã có sẵn tiền lệ

**8/15 shell nằm trên route KHÔNG đo được ở local:**

| Route | Vướng | Shell |
|---|---|---:|
| `/portal/reports/orders` | **500 có sẵn** — tz `Asia/Saigon` (pytz không nhận), đã xếp cụm **R3** `docs/refactor-plan.md:118` | 4 metric + 3 mcard |
| `/portal/inspection/detail/<id>` | `wujia_portal_inspection` đang **`uninstalled`** trên `wujia_tea_19` | 4 metric |
| `/portal/_pc-preview` | đo được, **nhưng** controller chặn `base.group_user` ⇒ `anh.owner` (portal) bị redirect | 4 metric |

**Đừng kết luận "D4e bị chặn".** D4c đã đi qua đúng ba việc này trên **DB copy cô lập**
(ledger D4c LIMIT 2): clone `wujia_tea_19` → `wujia_tea_d4e`, **copy `config/odoo.conf` sửa
`db_name` + `dbfilter`** (conf gốc có `dbfilter = ^wujia_tea_19$`, không sửa là *Database not
found*), `-i wujia_portal_inspection`, seed 1 phiếu, và đổi tz user **chỉ trên bản copy**
`Asia/Saigon` → `Asia/Ho_Chi_Minh` để `/portal/reports/orders` trả 200. **KHÔNG sửa bug tz** —
đó là cụm R3. Đo xong **drop DB copy**.

⚠️ **`8070`/`8071` là DB cụm R · `8072` là server đo · `8019` là UAT — đừng đụng.** DB copy dùng
cổng **8075**.

Với `/portal/_pc-preview`: đây là gallery **nội bộ**, đăng nhập `admin` là đúng vai — nhưng
**mọi route portal khác vẫn phải đo bằng `anh.owner`**, và `d3_review.py` **bắt buộc**
`--portal-login anh.owner` (mặc định `None` rơi về `admin` ⇒ 0 bề mặt mà vẫn "chạy xong").

---

## 5. Việc phải làm

1. **Kiểm kê lại + đính chính** (§1) → ghi `docs/d4-surfacecard-inventory.md` §13.
2. **Hỏi 4 câu §3**, chờ chốt rồi mới sửa CSS.
3. **Baseline TRƯỚC khi sửa dòng CSS đầu tiên** — Odoo 19 regenerate asset bundle theo checksum
   kể cả khi không bật `--dev`. Lỡ sửa rồi thì `git stash push` đúng file, **`-u` lại**, đo,
   `stash pop`, `-u` lại (D4d đã đi đúng đường này; template nằm trong DB nên **stash CSS không
   đủ**).
4. **CSS**: rút `background`/`border`/`border-radius`/`padding`/`box-shadow`/`gap` về
   `.wj-surface-card`; **giữ** `display:flex; align-items:center` (§3.4) và phần đã chốt ở §3.1/3.2.
5. **Call site**: 15 shell → `t-call="wujia_portal_layout.wj_surface_card"`, **giữ lớp cũ qua
   `sc_class`** (Luật #1 — `:is()` hover ở `_interaction.css:61/85/109` là **(0,3,0)**, bỏ lớp cũ
   là hover/pressed chết câm). Thẻ nào không thành `<div>` được thì **giữ tag + thêm thẳng class
   chủ sở hữu** — QWeb O19 **không có directive đổi tên thẻ** (`ir_qweb.py:1705`, chốt ở C8).
6. **Test**: thêm lớp `TestSurfaceCardD4e` vào
   `custom/wujia_portal_layout/tests/test_d4_surface_card.py` (**45 test sẵn**, tag
   `wujia_surface_card_d4`) — **không đẻ file test song song**. Dùng lại helper `_declares()` /
   `PROP = r'(?:^|;)\s*%s\s*:'` (so chuỗi con là bẫy: `top: var(--wj-pc-content-padding)` *chứa*
   chữ "padding").
7. **Đột biến**: `scratchpad/d4e_mutate.sh` (copy `d4d_mutate.sh`) — sửa cho sai → **đúng test đó
   phải đỏ** → hoàn nguyên, kèm **run đối chứng**. Bộ dò phải bắt `FAIL: (Subtest )?Lop\.test`.
8. **`-u` đúng MỘT lần**: `wujia_portal_layout,wujia_portal_report` (+ `wujia_portal_inspection`
   **chỉ trên DB copy**). Bump `wujia_portal_layout` → **19.0.36.0.0**; module chỉ đổi XML thì
   **không** bump.
9. **Hồ sơ**: `docs/d4e-acceptance-matrix.md` · cập nhật inventory §13 + mục D4 của
   `next-session-clusters-D.md` (bài học D4e, tiến độ mới) · entry **tiến độ** trong
   `docs/qa-issue-ledger.yaml` **giữ `Ready for Dev`** · `cd scripts/ba_spec && python3 qa_sync.py`
   **dry-run**; chỉ `--apply` khi chủ dự án chốt. **Dev không tự đóng `Done`.**

---

## 6. Nghiệm thu — không đủ thì không ghi ledger

1. Bảng đo trước–sau **5 khổ 1440/1024/992/390/360** × mọi route đo được (kể cả DB copy).
2. Nhịp header→body **đo TUYỆT ĐỐI** trước–sau (RULE 1/2 là điều kiện CẦN, **không đủ** — sai số
   đều tay lọt sạch, bài học D4b; D4d bắt được bẫy `-2px` đúng nhờ phép này).
3. **Chiều cao thẻ KPI đo thật** trước–sau ở cả 3 file (§3.1) — con số này là thứ chủ dự án duyệt.
4. RULE 1 + RULE 2 chạy lại: `python3 scratchpad/d3_review.py --base http://127.0.0.1:8072
   --portal-login anh.owner --out <x>.json` rồi `d3_analyze.py`. Đối chiếu **5 cờ có sẵn** của
   baseline (4× `debt-pay` redirect `no_due` + `inspection@360` tràn 11px) — **cờ mới nào cũng
   phải giải trình**.
5. Ảnh trước–sau @1440 **và** @390 (bài học D3e: số Pass hết mà badge vẫn trôi 966px). Thêm phép
   **diff pixel** (`PIL.ImageChops`) — D4d chứng minh "không rò rỉ" bằng *khác đúng 0 pixel*.
6. **Mutation 100% đỏ đúng chỗ** + run đối chứng xanh.
7. **Đặc hiệu CSS quét toàn bộ `custom/**/*.css`**, loại tên con BEM khỏi phép khớp (bài học
   D4d #10), và phân biệt rule **trạng thái nghỉ** với `:hover`/`:active`.
8. Đối chiếu cột `Kết quả mong muốn` của `UI-SURFACECARD-001` — **≥90%** cho phần thuộc D4e.

---

## 7. Ngoài phạm vi — thấy cũng để yên

Bootstrap `.card` thô (75) → **D4f** · `wj-auth-card` (15) **THIẾT KẾ S39** · nhóm Khảo sát
(11 họ / 21 lượt) BA ghi *provisional* · **26 lượt bề mặt trắng mobile** phát hiện ở D4d
(inventory §12.2: 20 → `CMP-ES-001`, 4 → `UI-DATALIST-001`, 2 chưa có chủ) · hội tụ token
`--wujia-border` ↔ `--wujia-morder-border` và `--wujia-border-soft` ↔ `--wujia-morder-divider`
(**phải hỏi trước**) · **bug tz `/portal/reports/orders`** — là **R3**, D4e chỉ né trên DB copy ·
2 chỗ inline `style="padding:14px 14px 0"` của card `flush`
(`portal_franchise_information`, `portal_support_detail`) — D4d ghi LIMIT 3, hội tụ về 12 ở đây
**chỉ khi chủ dự án chốt**.

**Câu hỏi treo từ D4c/D4d, mang sang lượt CardHeader — KHÔNG tự sửa ở D4e:** nhịp header→body PC
`12×32 · 18×14 · 23×2 · 25×2 · 0×2` có kéo hết về 12 hay không.

---

## 8. Môi trường

- v14 tham chiếu `/home/huyban/odoo-dev/wujia_tea_odoo14` (**không sửa**) · v19
  `/home/huyban/odoo-dev/WujiaTea`.
- **UAT `http://113.161.187.126:8019/`** — `admin/Wujia@2026`. Tự smoke-test được (đọc/nhìn),
  theo giới hạn **QA §10: không tạo đơn/hoá đơn/email thật**.
- Portal đo bằng **`anh.owner` / `wujia@test123`** — quá 5 lần sai dính *Too many login failures*.
- 🔴 **`logfile` trong `config/odoo.conf` nuốt sạch stdout** — "RC=0, 0 ERROR" đọc từ file rỗng là
  **XANH GIẢ** (D4d dính 3 lần, giấu 4 test đỏ). Bằng chứng thật ở
  `logs/<năm>/<tháng>/<năm-tháng-ngày>.log`; luôn `N=$(wc -l < $L)` **trước** mỗi lần chạy rồi
  `tail -n +$((N+1))`.
- Route trả 404 kèm *"Không tìm thấy mẫu"* = DB cũ hơn code ⇒ chạy `-u`, đừng đi tìm bug logic.
- Harness ở `scratchpad/` và toolchain `scripts/ba_spec/` là **dev-only, gitignored, KHÔNG commit,
  KHÔNG lên server**.
- Nguyên tắc xuyên suốt: **ask-don't-assume · read-before-write · perf-first (1500 user) ·
  comment gọn 1 dòng · kiểm kê là SÀN · chủ sở hữu DUY NHẤT của dáng khung · `gap` chỉ ở biến thể
  xếp ngang · không khoá chiều cao · đo tuyệt đối, đừng chỉ đo quan hệ.**
