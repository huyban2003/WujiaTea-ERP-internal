# D4e2 — SurfaceCard lượt 5: `wj-rep-mcard` + hai món nợ D4d

> Dán nguyên khối này sau khi chạy `/wujia-start`.

## 0. Bối cảnh

`UI-SURFACECARD-001` (STT 127 · `CMP-SC-001` · tab `UI Component` gid 488333015) là issue BA
`Ready for Dev` chuẩn hoá **khung card** toàn Portal: một chủ sở hữu duy nhất của
`background` / `border` / `border-radius` / `padding` / `box-shadow` / `gap`.

Component `wujia_portal_layout.wj_surface_card` dựng ở D4b, đã chạy thật trên **110/384 lượt
≈ 29%** qua D4b + D4c + D4d + **D4e1**. D4e1 (05/09) đóng trọn họ `wj-pc-metric-card` — 12 thẻ /
3 file / 3 module — và gộp **hai chữ ký dáng khung về một**.

D4e2 là **nửa còn lại của D4e**, gồm ba việc:

| Phần | Việc | Shell | Module |
|---|---|---:|---|
| **A** | `wj-rep-mcard` — 3 khối dưới của Báo cáo đặt hàng **bản mobile** | 3 | `wujia_portal_report` |
| **B** | Nợ D4d #3 — 2 chỗ `style="padding:14px 14px 0"` inline | 2 | `wujia_portal_base`, `wujia_portal_support` |
| **C** | Nợ D4d #5 — nhịp header→body PC `18/23/25` → `12` | 18 ô | `wujia_portal_layout`, `wujia_portal_exam` |

Hồ sơ phải đọc trước khi gõ dòng code đầu tiên:

| File | Đọc phần nào |
|---|---|
| `docs/d4e1-acceptance-matrix.md` | **toàn bộ** — khuôn nghiệm thu D4e2 phải theo đúng file này; đặc biệt §min-height và 7 LIMIT |
| `docs/d4-surfacecard-inventory.md` | **§13** (đính chính sau D4e1) · §12 (đính chính sau D4d) |
| `docs/next-session-clusters-D.md` | **Luật chung #1…#9** · bảng thứ tự lượt · **🔴 Bài học D4e1 (7 mục)** · 🔴 Bài học D4d (10 mục) |
| `docs/d4c-acceptance-matrix.md` | **§4** — histogram nhịp header→body, là mốc trước của phần C |
| `docs/qa-issue-ledger.yaml` | 4 khối tiến độ D4b/D4c/D4d/D4e1 — **giữ nguyên `Ready for Dev`** |
| `custom/wujia_portal_layout/views/wj_surface_card.xml` | hợp đồng props (`sc_variant`/`sc_density`/`sc_body`/`sc_tone`/`sc_href`/`sc_class`/`sc_link_class`/`sc_id`) |

---

## 1. Phạm vi — đếm lại trước khi tin

Con số dưới đây đếm ngày 05/09, **vẫn phải đếm lại** (luật "kiểm kê là SÀN, không phải TRẦN"):

| Việc | Neo | Số |
|---|---|---:|
| `wj-rep-mcard` shell | `custom/wujia_portal_report/views/portal_report_orders.xml:85 · 98 · 132` | **3** (1 `--chart` + 2 thường) |
| inline `padding:14px 14px 0` | `wujia_portal_base/views/portal_franchise_information.xml:264` (template `portal_franchise_information`) · `wujia_portal_support/views/portal_support.xml:574` (template `portal_support_detail`) | **2** |
| ô nhịp ≠ 12 | histogram D4c §4: `0×2 · 12×32 · 18×14 · 23×2 · 25×2` | **18** |

Đếm shell phải **loại con BEM `__`** (`wj-rep-mcard__head/__title/__meta/__body` = 16 lượt thô /
3 shell) — đúng lỗi đã thổi kiểm kê D4d lên 51 và inventory D4e lên 60 (bài học D4d #10).

**`xml_id` và số dòng phải TRA, không được ĐOÁN** (bài học D4d #3, D4e1 dính lại lần nữa: đoán
`pc_preview` trong khi id thật là `pc_preview_page`). Tra chủ sở hữu của một dòng bằng
`awk '/<template id="/{t=$0} NR==N{print t}'`.

---

## 2. Neo CSS

| Rule | Neo | Đang khai |
|---|---|---|
| `.wj-rep-mcard` | `wujia_portal_report/static/src/css/portal_report.css:316` — **nằm trong `@media (max-width: 991.98px)` (dòng 204→453)** | `background: var(--wujia-bg-card)` · `border-radius: var(--wujia-card-radius)` — 🔴 **KHÔNG có viền** |
| `.wj-rep-mcard__head` | `portal_report.css:320` | `display:flex · align-items:center · justify-content:space-between · gap:8px · min-height:50px · padding:0 12px` |
| `.wj-rep-mcard__body` | `portal_report.css:342` | `padding: 12px` |
| `.wj-rep-mcard--chart .wj-rep-mcard__body` | `portal_report.css:344` | `padding: 0 12px 8px` — chú thích nói *"card về đúng 258"* |
| `.wj-pc-card__head` | `wujia_portal_layout/static/assets/css/_pc_components.css:163` | `margin-bottom: 18px` ← **10 ô** của phần C |
| `.wj-exam-pc-card__head` | `wujia_portal_exam/static/src/css/portal_exam.css:759` | `margin-bottom: 25px` ← 2 ô |
| `.wj-exam-pc-dhead` | `portal_exam.css:817` | `margin-bottom: 23px` ← 2 ô |
| `.wj-exam-pc-fcard .wj-exam-pc-field` | `portal_exam.css:984` | `margin-top: 18px` ← **collapse** với header 12 |
| `.wj-exam-pc-sumlist` | `portal_exam.css:1404` | `margin-top: 18px` (+ `gap: 23px`) ← **collapse** |
| `.wujia-mdash-list` | `wujia_portal_layout/static/assets/css/_components.css:2517` | `padding: 4px 14px` — liên quan trực tiếp phần B |

Token: `--wujia-card-radius: 16px` (`_variables.css:120`) · `--wujia-surface-radius` = **16 PC /
14 mobile** (`:129` và `:362`) · `--wujia-surface-pad-compact` = **16 / 12** (`:130`, `:363`) ·
`--wujia-surface-pad-regular` = **20 / 14** (`:131`, `:364`).

---

## 3. 🔴 Bốn câu phải HỎI CHỦ DỰ ÁN trước khi sửa — đừng tự quyết

### 3.1 `.wj-rep-mcard` **không có viền**, và đây là markup **chỉ-mobile**

Ba `<section>` nằm trong `<div class="d-lg-none wujia-mpage wujia-mreport">`
(`portal_report_orders.xml:28`) — bản PC là khối riêng `d-none d-lg-block wj-rep-pc` (dòng 165).
CSS cũng nằm trọn trong `@media (max-width: 991.98px)`. **Hệ quả đo:** ở 1440/1024/992 ba thẻ này
`display:none`, số đo vô nghĩa — **bằng chứng nghiệm thu của phần A chỉ có ở 390 và 360**.

Migrate = đổi hình học thật, ba thứ cùng lúc:
- **thêm viền 1px trên/dưới** ⇒ thẻ `--chart` vốn được căn tay cho ra **đúng 258px** (chú thích ở
  `portal_report.css:344`) thành **260**;
- **radius `--wujia-card-radius` 16 → `--wujia-surface-radius` mobile 14** (đúng cột mobile của
  BA, nhưng lệch mockup 2px);
- nền không đổi (`--wujia-bg-card` là nguồn của cả hai).

**Hỏi:** chấp nhận `258 → 260` và `r16 → r14`, hay giữ hình học cũ bằng cách để component không
kẻ viền cho biến thể này? Đây là **cùng loại quyết định với `min-height` ở D4e1** — không tự chốt,
mà **đo trước rồi trình số**.

### 3.2 `sc_body="flush"` là bắt buộc — nhưng head/body ở đây **không phải** CardHeader

`__head` đã có `padding: 0 12px` + `min-height: 50px`, `__body` có `padding: 12px`. Để mặc định
`sc_body="padded"` là **cộng chồng thành 24px mỗi bên**. Vậy `flush` là bắt buộc.

Nhưng `__head` **không phải** `wj_card_header` (khác cấu trúc: có `__meta` bên phải, `min-height`
riêng). **Không migrate CardHeader kèm ở đây** — đó là cụm D3, hợp đồng riêng, issue riêng đang
`Need Clarification`. Xác nhận lại điểm này với chủ dự án cho khỏi trôi phạm vi.

### 3.3 Nợ B: số **14 không phải số mồ côi** — nó đúng bằng `--wujia-surface-pad-regular` mobile

D4d ghi LIMIT là "giữ 14 để khớp inset của `.wujia-mdash-list`". Tra lại thì:
`.wujia-mdash-list { padding: 4px 14px }` (`_components.css:2517`, **11 call site / 3 file**), và
`--wujia-surface-pad-regular` mobile **= 14px**. Nên có **hai đường**, khác nhau về rủi ro:

| | Làm gì | Đổi hình học | Rủi ro |
|---|---|---|---|
| **A** | Bỏ inline, thay bằng class trỏ `var(--wujia-surface-pad-regular)` | **0px** | thấp — thuần trả lại quyền sở hữu, đúng tinh thần "không inline style" |
| **B** | Hội tụ **14 → 12** (`--wujia-surface-pad-compact` mobile) | −2px mỗi bên | wrapper 12 **lệch 2px** với `.wujia-mdash-list` 14 ⇒ chữ trong card không thẳng cột; muốn thẳng phải kéo luôn `.wujia-mdash-list` (11 call site) vào phạm vi |

Lưu ý wrapper này **bọc một `wj_card_header`** (xem `portal_franchise_information.xml:264–270`),
nên đổi inset là đổi cả vị trí tiêu đề card, không chỉ đệm.

**Hỏi:** A hay B? (Chọn B thì phải chốt luôn có kéo `.wujia-mdash-list` vào không.)

### 3.4 Nợ C: 10 trong 18 ô là `.wj-pc-card__head` — card **đã** migrate, head thì **chưa**

| Nhịp | Ô | Neo | Module |
|---|---:|---|---|
| 18 | 10 | `.wj-pc-card__head { margin-bottom: 18px }` | `wujia_portal_layout` |
| 18 | 4 | body tự khai `margin-top: 18` — `.wj-exam-pc-fcard .wj-exam-pc-field` · `.wj-exam-pc-sumlist`, **margin collapse** với header 12 | `wujia_portal_exam` |
| 23 | 2 | `.wj-exam-pc-dhead { margin-bottom: 23px }` | `wujia_portal_exam` |
| 25 | 2 | `.wj-exam-pc-card__head { margin-bottom: 25px }` | `wujia_portal_exam` |
| 0 | 2 | không khai nhịp — `/portal/notification/41` | `wujia_portal_notification` |

⚠️ Ba điều **không được tự nới ra**:
- 10 ô `18px` chỉ hội tụ **con số nhịp**, **không** migrate CardHeader kèm (như §3.2).
- 4 ô `18` của exam là **margin collapse** — phải nhắm `margin-top` của **body**, không phải
  `margin-bottom` của header; đo lại để chắc thu về đúng **12**, không phải `12+12`.
- 2 ô `0px` ở `/portal/notification/41` **để nguyên** (còn dính lỗi outline `h3` trước `h2` của
  cụm R2) — ghi LIMIT.

**Hỏi:** kéo cả 18 ô về 12 trong lượt này, hay chỉ 10 ô `.wj-pc-card__head` (một neo, một module)
còn 8 ô của `exam` để lượt sau?

---

## 4. Chặn kỹ thuật — cách gỡ đã có tiền lệ D4e1

| Route | Vướng | Cách gỡ |
|---|---|---|
| `/portal/reports/orders` | **500 có sẵn** — `tz='Asia/Saigon'`, pytz không nhận; đã xếp cụm **R3** (`docs/refactor-plan.md:118`, fix thuộc `wujia_portal_base/controllers/utils.py:38`) | đổi tz user thành `Asia/Ho_Chi_Minh` **chỉ trên DB copy**. 🔴 **KHÔNG sửa bug** — đó là R3 |

Clone `wujia_tea_19` → `wujia_tea_d4e2`, **copy `config/odoo.conf` sửa `db_name` + `dbfilter`**
(conf gốc có `dbfilter = ^wujia_tea_19$`, không sửa là *Database not found* — bẫy S48/D3c). Cổng
**8075**. ⚠️ `8070`/`8071` là DB cụm R · `8072` là server đo · `8019` là UAT — **đừng đụng**.
Đo xong **drop DB copy + xoá `data/filestore/wujia_tea_d4e2`**.

Route của phần B và C (`/portal/franchise-information`, `/portal/support/...`, các màn exam PC)
đo được thẳng trên `wujia_tea_19`, **đăng nhập `anh.owner` / `wujia@test123`** — quá 5 lần sai
dính *Too many login failures*.

**Baseline TRƯỚC khi sửa dòng CSS đầu tiên.** Odoo 19 regenerate asset bundle theo checksum kể cả
khi không bật `--dev`. Lỡ sửa rồi thì `git stash push` đúng file → `-u` lại → đo → `stash pop` →
`-u` lại; **stash CSS không đủ vì template nằm trong DB**.

---

## 5. Việc phải làm

1. **Đếm lại + đối chiếu neo §1/§2**, ghi đính chính vào `docs/d4-surfacecard-inventory.md` **§14**.
2. **Hỏi 4 câu §3**, đo baseline, **trình số rồi mới chốt** — không sửa CSS trước khi có bảng số.
3. **CSS phần A**: rút `background` + `border-radius` khỏi `.wj-rep-mcard` (Luật #7).
   `__head`/`__body`/`__title`/`__meta` **giữ nguyên** — là nội dung, không phải khung.
4. **Call site phần A**: component render `<div>`, call site là `<section>` mang `<h2>` bên trong.
   **Giữ `<section>`, thêm thẳng class chủ sở hữu** — QWeb O19 **không có** directive đổi tên thẻ
   (`ir_qweb.py:1705`, chốt ở C8; đúng cách §12.4 đã chốt cho 9 call site không-`<div>` của D4d).
   Giữ lớp cũ qua `sc_class` (Luật #1 — `:is()` hover ở `_interaction.css` là `(0,3,0)`).
5. **Phần B/C** theo đúng đường chủ dự án chốt ở §3.3/§3.4.
6. **Test**: thêm lớp `TestSurfaceCardD4e2` vào
   `custom/wujia_portal_layout/tests/test_d4_surface_card.py` (**52 `def test_` sẵn**, 4 lớp, tag
   `wujia_surface_card_d4`) — **không đẻ file test song song**. Dùng lại helper `_declares()` /
   `_rule()` / `PROP = r'(?:^|;)\s*%s\s*:'` (so chuỗi con là bẫy: `top: var(--wj-pc-content-padding)`
   *chứa* chữ "padding"). ⚠️ `.wj-rep-mcard` nằm **trong `@media`** — hàm `_rule()` phải bắt được
   rule lồng trong media, đừng giả định rule ở mức trên cùng.
7. **Đột biến**: `scratchpad/d4e2_mutate.sh` (copy `d4e1_mutate.sh`). Ba bẫy đã dính, **đừng dính
   lại**:
   - bộ dò phải là `FAIL: (Subtest )?[A-Za-z0-9]+\.[a-z_0-9]+` — bản cũ viết `[A-Za-z]+` nên
     **không khớp tên lớp có chữ số** (`TestSurfaceCardD4e2`) ⇒ báo oan "7/7 guard rỗng";
   - đột biến XML phải **giữ file hợp lệ** (đổi `<t t-call>` thành `<div>` làm lệch `</t>` ⇒
     `ExpatError` ⇒ `-u` abort ⇒ view không đổi ⇒ **test xanh oan**);
   - `-u` của lần chạy đột biến phải liệt kê **đủ mọi module có test `post_install`**, thiếu là
     test không chạy mà vẫn "xong".
   Xác nhận đột biến **đã vào file** bằng `grep` lại trước khi kết luận (bài học D4d #2).
8. **`-u` đúng MỘT lần** (Luật #1 của cụm D4), một lệnh, danh sách module ngăn bằng dấu phẩy —
   phạm vi tuỳ chốt §3, tối đa `wujia_portal_layout,wujia_portal_report,wujia_portal_base,`
   `wujia_portal_support,wujia_portal_exam,wujia_portal_notification`.
9. **Bump**: `_pc_components.css` bị đụng ở phần C ⇒ **bắt buộc bump `?v=`** trong
   `views/assets.xml` (hiện **`?v=1200`**) + `wujia_portal_layout` → **19.0.37.0.0** (hiện
   `19.0.36.0.0`). Module chỉ đổi XML thì **không** bump.

---

## 6. Nghiệm thu — không đủ thì không ghi ledger

1. Bảng đo trước–sau **5 khổ 1440/1024/992/390/360** × mọi route đo được, gồm chiều cao trang
   **và số record thấy trong viewport** — acceptance #11 của BA: số record thấy được **không được
   giảm**. Phần A **chỉ có bằng chứng ở 390/360** (§3.1).
2. **Chiều cao 3 thẻ `wj-rep-mcard` đo thật** trước–sau, riêng thẻ `--chart` phải nói rõ
   `258 → ?` — con số này là thứ chủ dự án duyệt.
3. **Nhịp header→body đo TUYỆT ĐỐI** trước–sau (`scratchpad/d4d_rhythm.py`, copy thành
   `d4e2_rhythm.py`). Đây chính là **bằng chứng nghiệm thu của phần C**: histogram phải đi từ
   `12×32 · 18×14 · 23×2 · 25×2` về `12×48`, **giữ `0×2`**. RULE 1/2 là điều kiện **CẦN, không
   đủ** — sai số đều tay lọt sạch (bài học D4b); D4d bắt bẫy `-2px` đúng nhờ phép này.
4. **RULE 1 + RULE 2 chạy lại**: `python3 scratchpad/d3_review.py --base http://127.0.0.1:8072
   --portal-login anh.owner --out <x>.json` rồi `d3_analyze.py`. `--portal-login` là **bắt buộc**
   — mặc định `None` rơi về `admin` ⇒ 0 bề mặt mà vẫn "chạy xong" (bẫy Pass rỗng). Đối chiếu **4
   cờ có sẵn** của baseline D4e1; **cờ mới nào cũng phải giải trình**.
5. **Ảnh trước–sau @390 và @360 + soi mắt 3 thẻ** — bắt buộc, đây là lượt đổi khung. Số đo Pass
   hết mà bố cục vẫn vỡ đã xảy ra hai lần (D3e badge trôi 966px · D3d mất 28px nhịp). Cộng phép
   **diff pixel** (`PIL.ImageChops.difference(...).getbbox() is None`) trên các trang **không**
   thuộc phạm vi — D4d/D4e1 chứng minh "không rò rỉ" bằng *khác đúng 0 pixel*. ⚠️ Trang có đồng
   hồ đếm ngược sẽ khác vài pixel do nhảy giây — **cắt ảnh ra xem rồi mới kết luận**, đừng đoán
   (tiền lệ D3c, D4e1 gặp lại).
6. **Đột biến 100% đỏ đúng chỗ** + run đối chứng xanh.
7. **Quét đặc hiệu CSS toàn bộ `custom/**/*.css`**, **loại tên con BEM** khỏi phép khớp (bài học
   D4d #10: `'.wujia-mexam-card' in selector` khớp cả `.wujia-mexam-card-badge` ⇒ 9/15 "vi phạm"
   là giả), và phân biệt rule **trạng thái nghỉ** với `:hover`/`:active`.
8. 0 lỗi JS · 0 tràn ngang · 0 redirect ngầm · HTTP 200 toàn bộ.
9. Đối chiếu cột `Kết quả mong muốn` của `UI-SURFACECARD-001` — **≥90%** cho phần thuộc D4e2.

---

## 7. Hồ sơ

- `docs/d4e2-acceptance-matrix.md` theo đúng khuôn `docs/d4e1-acceptance-matrix.md`.
- `docs/d4-surfacecard-inventory.md` **§14** (đính chính con số + 4 chốt của lượt + tiến độ).
- Mục D4 của `docs/next-session-clusters-D.md`: bài học D4e2, tiến độ mới, bảng thứ tự lượt.
- `docs/qa-issue-ledger.yaml`: khối **tiến độ** dạng chú thích như D4b/D4c/D4d/D4e1, **giữ
  `Ready for Dev`** (≈113/384 ≈ 29%, chưa handoff). Chạy `qa_sync.py` **dry-run** (mặc định, không
  có cờ `--dry-run`); chỉ `--apply` khi chủ dự án chốt. **Dev không tự đóng `Done`.**
  ⚠️ `scripts/ba_spec` là **symlink** ra `~/wujia-devkit/ba_spec`, nên `qa_sync.py` tính đường dẫn
  ledger thành `/home/huyban/docs/qa-issue-ledger.yaml` và chết `FileNotFoundError` — nạp script
  với `LEDGER` trỏ đúng repo, **đừng sửa file toolchain**.
- Cuối cụm chạy `/wujia-end-sprint` (test → doc → PDF → ledger → commit → push).

---

## 8. Ngoài phạm vi — thấy cũng để yên

Bootstrap `.card` thô (75) → **D4f** · `wj-auth-card` (15) **THIẾT KẾ S39** · 9 họ còn lại của
nhóm Khảo sát (BA ghi *provisional*; D4e1 chỉ đụng khung `wj-pc-metric-card`, **không** chốt hộ
BA field mapping nào) · **26 lượt bề mặt trắng mobile** phát hiện ở D4d (inventory §12.2:
20 → `CMP-ES-001`, 4 → `UI-DATALIST-001`, 2 chưa có chủ) · hội tụ token `--wujia-border` ↔
`--wujia-morder-border` và `--wujia-border-soft` ↔ `--wujia-morder-divider` (**phải hỏi trước**) ·
**bug tz `/portal/reports/orders`** — là **R3**, D4e2 chỉ né trên DB copy · migrate CardHeader —
là cụm **D3**, issue riêng đang `Need Clarification`.

**Ba vấn đề có sẵn — không sửa lẻ:** (1) RULE 1 vỡ ở `/portal/delivery` PC 3 khổ, empty state
`h3` 28px > tiêu đề card 22px — họ `wj-empty-state` → **CMP-ES-001**; (2) tiêu đề card lệch chuẩn
18px ở 4 màn (`/portal/delivery` 22 · `/portal/order` 22 · `/portal/inspection` 24 ·
`/portal/info-request` mobile 16) — nợ RULE 2, ghép **D7+**; (3) **15 card không có
`.wj-card-header`** ⇒ không đo được nhịp — là khối lượng còn lại của cụm D3, không phải lỗi.

---

## 9. Môi trường

- v14 tham chiếu `/home/huyban/odoo-dev/wujia_tea_odoo14` (**không sửa**) · v19
  `/home/huyban/odoo-dev/WujiaTea`. Python `/home/huyban/miniconda3/envs/odoo/bin/python3`.
- **UAT `http://113.161.187.126:8019/`** — `admin/Wujia@2026`. Tự smoke-test được (đọc/nhìn),
  theo giới hạn **QA §10: không tạo đơn/hoá đơn/email thật**.
- Portal đo bằng **`anh.owner` / `wujia@test123`** — quá 5 lần sai dính *Too many login failures*.
- 🔴 **`logfile` trong `config/odoo.conf` nuốt sạch stdout** — "RC=0, 0 ERROR" đọc từ file rỗng là
  **XANH GIẢ** (D4d dính 3 lần, giấu 4 test đỏ). Bằng chứng thật ở
  `logs/<năm>/<tháng>/<năm-tháng-ngày>.log`; luôn `N=$(wc -l < $L)` **trước** mỗi lần chạy rồi
  `tail -n +$((N+1))`.
- ⚠️ Đừng `pkill -f "odoo.d4e2.conf"` — chuỗi đó nằm trong chính dòng lệnh của shell đang chạy nên
  **tự giết phiên** (D4e1 dính). Lấy PID bằng `ps aux | grep "[o]doo.d4e2.conf" | awk '{print $2}'`.
- Route trả 404 kèm *"Không tìm thấy mẫu"* = DB cũ hơn code ⇒ chạy `-u`, đừng đi tìm bug logic.
- Harness ở `scratchpad/` và toolchain `scripts/ba_spec/` là **dev-only, gitignored, KHÔNG commit,
  KHÔNG lên server**.
- Nguyên tắc xuyên suốt: **ask-don't-assume · read-before-write · perf-first (1500 user) · hạn chế
  comment trong code · kiểm kê là SÀN · chủ sở hữu DUY NHẤT của dáng khung · `gap` chỉ ở biến thể
  xếp ngang · không khoá chiều cao · đo tuyệt đối, đừng chỉ đo quan hệ.**
