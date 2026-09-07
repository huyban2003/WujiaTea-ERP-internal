# D5d — bảng nghiệm thu DataList lượt 3 (danh sách PC không phải bảng)

**Ngày:** 2026-09-07 · **Cơ sở:** `9e463f2` (D5c) · **Spec:** `CMP-DL-001`, `UI-DATALIST-001` (STT 126)
· **Phạm vi:** 4 call site họ `li.wujia-content-card-row` — 3 khối preview `/portal`
(`portal_home.xml:135/164/195`) + `/portal/knowledge` (`portal_knowledge.xml:99`).

Lượt đầu tiên dùng variant **`compact-row`** (component không bọc `<table>`) và lượt đầu tiên có
call site truyền **`dl_pager`**.

Khác D5b/D5c ở một điểm phải nói thẳng: hai lượt trước chỉ áp con số BA đã viết sẵn cho DataTable.
Ở đây **BA không có số cho ô "PC + không phải bảng"** — spec chỉ cho DataTable (≥992) và
compact-row (<992). Chủ dự án chốt trong phiên: **áp bộ số compact-row 64–76 lên PC**, vì dáng cũ
(row 51.8 · gap 0 · các dòng dính nhau ngăn bằng một đường kẻ) quá dày đặc. Vì đây là số **suy
diễn chứ không phải số BA viết cho tầng này**, lượt này ghi là **provisional** và đi kèm văn bản
hỏi BA (`docs/ba-questions-d5-datalist.md`).

---

## 1. Đã làm

| | |
|---|---|
| Call site | 4/4 chuyển sang `t-call="wujia_portal_layout.wj_data_list"` với `dl_variant='compact-row'`; `<li>` mang **cả hai** lớp `wj-data-item wujia-content-card-row` |
| CSS | 4 rule hình học cũ của `.wujia-content-card-row` (gồm cả rule trong `@media 575.98`) khoá bằng `:not(.wj-data-item)` ⇒ `.wj-data-item` là chủ sở hữu DUY NHẤT dáng item. **Cố ý KHÔNG khoá** 4 rule con `-bullet` / `-content` / `-content a` / `-date` (biến thể ô, đúng tiền lệ `wj-pc-td--*` của D5c) |
| Dáng mới | lấy **cách dựng** của `.wujia-mhist-row` — mẫu duy nhất D5a §7 công nhận đã đúng chuẩn compact-row: item là card có viền, gap là khoảng cách giữa hai item (`+` selector), không phải `gap` của container |
| DataState | mỗi chỗ giữ **đúng** markup empty cũ (Home `wujia-content-card-empty`, knowledge `wujia-empty-state` có icon) — không đồng bộ hoá, ngoài phạm vi |
| Pagination | knowledge kéo **vào trong** DataList qua `dl_pager`, guard `page_count > 1` giữ nguyên. 3 khối preview **không** gắn pager (BA: "Xem tất cả" ở CardHeader) — ghim bằng test |
| `-u` | `wujia_portal_layout,wujia_portal_base,wujia_portal_knowledge` — RC=0, **0 ERROR** (kiểm cả file log thật ở `<thư-mục>/2026/09/2026-09-07.log`, bẫy L15) |
| Version | layout `19.0.40.0.0 → 19.0.41.0.0` · base `19.0.7.8.0 → 19.0.7.9.0` · knowledge `19.0.3.10.2 → 19.0.3.11.0` · `_components.css?v=1230 → 1240` |

Môi trường: DB copy cô lập **`wujia_tea_d5b`** (cổng **8077**, `--db-filter '^wujia_tea_d5b$'`),
không đụng `wujia_tea_19`/8019. Trước khi đo mốc trước đã so `latest_version` ↔ `__manifest__.py`
của **từng** module: 21/21 khớp (bài học D5a #4). Mốc "trước" đo lại ra đúng con số D5c để lại
(`th[scope]` 9/27 · header `44×18 · 50×9`) ⇒ môi trường nhất quán.

## 2. Số đo trước–sau — 4 call site × 3 khổ có khối PC

| Route | Khối | Cao item (BA 64–76) | Gap (BA 8) | Radius (BA 12) | Padding (BA 10–12px 12–14px) |
|---|---|---|---|---|---|
| `/portal` | Thông báo mới nhất | 51.8 → **64** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |
| `/portal` | Đơn hàng gần đây | 51.8 → **64** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |
| `/portal` | Yêu cầu đổi trả gần đây | 50.8–51.8 → **64** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |
| `/portal/knowledge` | Tài liệu mới cập nhật | 50.8–51.8 → **64** | 0 → **8** | 0 → **12** | `12px 0` → **`12px 14px`** |

Giống hệt ở cả **1440 · 1024 · 992**. Ở **991 · 390 · 360** cả 4 khối đều **không render** (nằm
trong wrapper `d-lg-*`; mobile dùng `wujia-mdash-row` / `wujia-mknow-row`, việc của D5e) ⇒
**mobile bất biến tuyệt đối**: `pageH` của `/portal` (2761 · 2883 · 2996) và `/portal/knowledge`
(1791 · 1916 · 2042) **không đổi một pixel**.

**27 bảng của D5b/D5c không bị đụng**: `th[scope]` 9/27 · header `44×18 · 50×9` · row
`58×12 · 54×7 · 52×4 · 55×2 · 88×2` · cell padding `10px 16px ×18 · 0px 22px ×9` — **y hệt**
trước lượt này. Mọi danh sách ngoài phạm vi (mobile 6 khối Home, mhist, mnoti, mknow, mexam,
khảo sát…) so từng ô `(itemKey, cao, gap)`: **0 ô đổi**.

## 3. Chiều cao — cái giá đo được của việc áp số 64–76 lên PC

| Đối tượng | Trước | Sau | Δ |
|---|---:|---:|---:|
| Card *Thông báo mới nhất* @1440 | 196.59 | **230** | +33.4 |
| Card *Đơn hàng gần đây* @1440 | 196.59 | **230** | +33.4 |
| Card *Yêu cầu đổi trả* @1440 | 242 | 242 | **0** (vốn đang bị card anh em kéo cao) |
| `/portal` `pageH` @1440 · @1024 | 900 · 900 | 900 · 900 | **0 · 0** |
| `/portal` `pageH` @992 | 900 | **906** | +6 |
| `/portal` @991 · 390 · 360 | 2761 · 2883 · 2996 | y hệt | **0** |
| Card *Tài liệu mới cập nhật* @1440 | 764.56 | **1000** | +235 |
| `/portal/knowledge` `pageH` @1440 · 1024 · 992 | 995 · 1007 · 1007 | **1230 · 1242 · 1242** | +235 |

Home **gần như không nở**, ngược với dự đoán trước khi đo: mỗi khối preview chỉ có 2 bản ghi, và
hai card cạnh nhau vốn đã bị card cao hơn kéo bằng chiều cao, nên phần nở bị nuốt vào chỗ trống
sẵn có. Mốc C7 (Home 2752→2634 @360) **không bị đụng** vì mobile bất biến. Chỗ nở thật là
knowledge: 12 bản ghi × ~20px.

## 4. Acceptance #9 — số record thấy trong viewport (đo ở cao 900)

| Route | Trước | Sau | |
|---|---:|---:|---|
| `/portal` ×3 khối, cả 3 khổ PC | 2 · 2 · 2 | 2 · 2 · 2 | ✅ không giảm |
| `/portal/knowledge`, cả 3 khổ PC | 12 | **9** | ❌ **giảm 3** |

Đây là **hệ quả cơ học** của việc kéo row 51.8 → 64 + gap 8: một màn cao 900 chứa được 9 thay vì
12 dòng. **Không tự lờ và không tự vá**: giảm số record đọc-không-cuộn là điều BA viết ra để cấm,
nên nó vào thẳng văn bản hỏi BA (mục 3) như bằng chứng để BA chốt giữ 64 hay hạ xuống. Trường
`rowsInViewport` được bổ sung cho **nhánh danh sách** của `wj_datalist.py` trong phiên này (trước
chỉ có ở nhánh bảng) — cộng thêm, không đổi trường cũ.

## 5. Nhịp trong card — RULE 1 + RULE 2 chạy lại

| | D5c công bố | D5d sau |
|---|---|---|
| RULE 1 `HIERARCHY` vi phạm | 0 | **0** |
| RULE 2 histogram cỡ tiêu đề card | `14.7×10 · 16×8 · 18×39 · 22×6 · 24×3` | **giống hệt** |
| Nhịp header→body | `8×2 · 12×33` | **giống hệt** |
| Tràn ngang · lỗi JS · redirect ngầm | 0 · 0 · 0 | **0 · 0 · 0** |

Phép so là chính hai con số D5c công bố, **không** phải `docs/d5-baseline.json` (baseline chụp
trước khi bổ seed). `/portal/reports/orders` vẫn 500 — lỗi có sẵn của cụm **R3** (PostgreSQL trên
Ubuntu không biết bí danh `Asia/Saigon`), không thuộc D5.

## 6. Tương tác — dò bằng `getComputedStyle`, không chỉ dò hình học

Bẫy D5c #4 (hai rule cùng độ đặc hiệu ⇒ rule mới chỉ ăn nửa vời) được kiểm trực tiếp: rê chuột
vào item đã migrate rồi đọc lại computed style.

| | Nghỉ | Hover |
|---|---|---|
| Trước | `bg: transparent` | `bg: rgba(40,169,223,0.04)` |
| Sau | `bg: #FFFFFF`, `border 1px`, `radius 12px` | `bg: rgba(40,169,223,0.04)` + `border-color: primary` |

Rule cũ `.wujia-content-card-row:hover` là (0,2,0) — sau khi khoá `:not()` nó không còn chạm item
migrate; rule mới `.wj-data-list--compact-row .wj-data-item:hover` là (0,3,0). Hover ăn ở **mọi**
hàng, không phân biệt chẵn lẻ.

## 7. Chỗ dễ vỡ do cấu trúc — đo trước, và kết luận là KHÔNG thêm rule

`.wujia-content-card` là `flex column`, `.wujia-content-card-body` mang `flex: 1 1 auto` để hai
card `col-lg-6` cạnh nhau bằng chiều cao. Chèn `.wj-data-list` + `.wj-data-viewport` vào giữa
**cắt chuỗi flex đó** — đúng họ bài học D3e. Đo thật: `listFlexGrow` vẫn `1`, 4 card vẫn bằng
chiều cao, `overflowX = false` ở cả 6 khổ ⇒ `overflow-x: auto` của viewport **không** đẻ thanh
cuộn ngang. **Không thêm rule nào** (bài học D3: đo rồi mới thêm, và kết luận có thể là không thêm).

## 8. Guard — chứng minh bằng mutation

29 test (`--test-tags wujia_data_list_d5`), **0 failed / 0 error** (23 của D5b/D5c + 6 mới). Mỗi
phép thay neo vào **cả selector**; hoàn tác bằng **ảnh chụp byte lấy ngay trước khi thay** +
đối chiếu `sha256` (bẫy D5c #2), **không** `git checkout` (bẫy D5b #2). 7/7 phép đều làm đỏ đúng
một test và 7/7 file khớp `sha256` sau khi hoàn tác.

| Mutation | Test đỏ |
|---|---|
| Gỡ `:not(.wj-data-item)` ở rule cũ `.wujia-content-card-row` | `test_mot_chu_so_huu_dang_compact_row` |
| `min-height` 64 → 52 | `test_so_ba_cua_compact_row` |
| Gỡ `margin-top: 8px` (gap giữa hai item) | `test_so_ba_cua_compact_row` |
| Gỡ lớp `wj-data-item` ở call site knowledge | `test_item_mang_ca_hai_lop` |
| Gắn `dl_pager` vào một khối preview Home | `test_home_preview_khong_gan_pagination` |
| Nới guard pager knowledge về `pager` | `test_knowledge_pager_di_qua_dl_pager` |
| Đổi `dl_variant` knowledge về `'table'` | `test_bon_call_site_dung_variant_compact_row` |

Hai test cũ phải sửa vì **chính lượt này làm sai tiền đề của chúng**, không phải vì sản phẩm hỏng:
`test_moi_th_deu_co_scope` khẳng định `portal_home.xml` có **đúng 1** DataList (nay 4) ⇒ đổi phép
chọn sang "call site có `thead`"; `test_home_preview_khong_gan_pagination` chỉ soi call site đầu ⇒
mở rộng cho **cả 3** khối preview.

## 9. Bẫy đã trả giá trong phiên

1. 🔴 **`.//ul` trong XPath vớ luôn `<ul class="pagination">` của pager.** Test
   `test_item_mang_ca_hai_lop` báo `4 != 1` ở knowledge và trông y như lỗi sản phẩm — thật ra là
   lỗi bộ đo: từ khi pager nằm **trong** DataList, `.//ul` khớp cả hai. Phải neo vào
   `ul[@class="wujia-content-card-body"]`. Cùng họ với bẫy `contains()` của D5c #3: selector rộng
   một nấc là đo nhầm đối tượng.
2. 🟠 **`sed` bump `?v=` khớp cả `_pc_components.css`** vì tên file kia kết thúc bằng chính chuỗi
   `_components.css?v=1230`. Hệ quả vô hại (bump cache thừa, cả hai nay là `1240`) nhưng là dạng
   sai duy nhất mà một `sed` neo vào đuôi chuỗi luôn mắc.
3. 🟠 **Bộ đo chỉ ghi `rowsInViewport` cho nhánh BẢNG.** Lượt này là danh sách, và là lượt duy
   nhất tới giờ làm row **cao lên** — tức lượt cần acceptance #9 nhất lại là lượt bộ đo mù. Bổ
   trường cho nhánh danh sách **trước** khi đo mốc trước, rồi đo lại mốc trước từ đầu.
4. 🟠 **Ảnh dò hover ở khổ hẹp bị sidebar chặn con trỏ** (`ElementHandle.hover` timeout 30s vì
   `.main-menu` phủ lên). Dò tương tác chỉ chạy ở ≥992 bằng `mouse.move` tới tâm hộp. Ở đúng 992
   con trỏ còn sót lại từ khổ trước nên ô "nghỉ" đọc ra màu hover — **cùng một hiện tượng có ở cả
   bảng trước và bảng sau**, nên không đọc nhầm thành thay đổi.

## 10. LIMIT

1. **Bộ số 64–76 là provisional.** BA chưa từng viết số cho danh sách PC không phải bảng; lượt này
   áp số của tầng mobile theo chỉ đạo chủ dự án. Chờ BA chốt — `docs/ba-questions-d5-datalist.md`.
2. **Acceptance #9 thủng ở knowledge** (12 → 9 dòng đọc-không-cuộn @900). Nằm trong cùng câu hỏi.
3. **Pagination**: knowledge nay nằm **trong** DataList; 6 call site của D5b/D5c vẫn để **ngoài**
   card (LIMIT #4 của cả hai lượt) ⇒ hiện portal có hai kiểu. Dồn về một lượt dọn Pagination
   trước khi khép cụm D5.
4. `dl_state` của 4 chỗ vẫn là hai kiểu markup empty khác nhau (`wujia-content-card-empty` vs
   `wujia-empty-state`). Việc của `CMP-ES-001`, không nuốt phạm vi.
5. Đo trên **DB copy `wujia_tea_d5b`**, chưa soi UAT — deploy dồn một lượt cuối cụm D5
   (hàng đợi: D5b + D5c + D5d).
6. Ảnh chụp Home/knowledge @1440·1024·992 nằm ở scratchpad phiên, **không commit** (giữ repo gọn,
   đúng thông lệ D3/D4). Số đo tương ứng đã commit: `docs/d5d-{before,after,rule-after}.json` +
   `docs/d5d-probe-{before,after}.json`.

**Tiến độ cụm: 10/31 call site.** Kế tiếp: **D5e** — mobile compact-row (`wujia-mdash-row` ×6 ·
`mhist` · `mnoti` · `mknow`), 9 call site.
