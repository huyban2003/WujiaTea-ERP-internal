# D3c — bảng đối chiếu acceptance (UI-CARDHEADER-001, STT 125 · `CMP-CH-001`)

**Ngày đo:** 2026-09-02 (local, chưa deploy) · **Kết quả: 20/21 Pass, 1 phần (97,6%)** — ô
"phần" là **phạm vi cố ý**: sau D3c mới phủ **47/103** call site nên issue **giữ
`Ready for Dev`** (tiền lệ C8a→C8b) ⇒ phiên này **KHÔNG** chạy `qa_sync.py`.
Kiểm kê gốc rễ → `d3-cardheader-inventory.md`. Hai phiên trước → `d3-acceptance-matrix.md`,
`d3b-acceptance-matrix.md`.

**Phạm vi phiên:** **11 call site / 3 file / 3 module** — nốt phần còn lại của chính 4 file
D3a (`portal_return_form.xml` đã xong 4/4 từ D3a).

> ⚠️ **Đính chính con số bàn giao.** Doc bàn giao D3b ghi "15 chỗ (support 6 · delivery 3 ·
> franchise-information 6)". Chạy lại `scratchpad/d3_inventory.py` cho thấy con số đó **cộng
> cả dòng đã bị loại ở §3 inventory**. Số thật sau 3 phán quyết fork của chủ dự án hôm nay là
> **11**: support **6** · delivery **1** · franchise-information **4**.

**Môi trường:**
- **A/B bằng 2 DB, không phải 2 commit.** `wujia_tea_d3c` clone từ `wujia_tea_d3b` (kèm
  filestore) ⇒ **dữ liệu y hệt**, chỉ khác `arch_db`. Server "trước" **:8067**
  (`wujia_tea_d3b`), "sau" **:8068** (`wujia_tea_d3c`), `--db-filter` riêng từng cái —
  **KHÔNG đụng `wujia_tea_19`/8019**.
- **CSS dùng chung đĩa được.** Diff CSS của D3c đúng **1 rule mới** (§9), selector
  `.wj-pc-dlv-head .wj-card-header__lead` — element `.wj-card-header` **không tồn tại** trong
  arch "trước" của chính khối đó ⇒ rule trơ hoàn toàn với DB trước. Không suy luận: đã kiểm
  bằng `pseudoLeft`/`cardHeaders` của route `/portal/delivery/3` (trước: 2 giả-heading,
  3 `.wj-card-header`; đó là 3 header D3a ở nơi khác, không nằm trong `.wj-pc-dlv-head`).
- Đăng nhập form portal `anh.owner` (L13/3) + cookie `wujia_active_franchise_id=1`, viewport
  BA **1440 · 390 · 360**, cộng **1920** để nối lưới B4 cũ.
- Harness: `scratchpad/d3c_measure.py` · `d3c_probe_gap.py` · `d3c_tabwalk.py` ·
  `d3c_shot.py` · `d3c_cmp.py` + chạy lại `d3_measure.py`, `d3b_measure.py`,
  `scripts/ba_spec/b4_regression.py` (dev-only, không commit — §13).
- ⚠️ **Dữ liệu phải bơm để 2 call site không tàng hình** (bài học D3b): ticket không có
  attachment và không có comment thì card "File đính kèm" / "Lịch sử trao đổi" không render.
  Đã thêm **1 attachment + 2 comment vào ticket 40 giống hệt nhau trên CẢ HAI DB copy**.
  Riêng attachment phải chèn vào bảng nối `wujia_support_ticket_attachment_rel` (M2M), đặt
  `res_id` là **không đủ**.
- ⚠️ **Đo đúng trang.** `/portal/support/1` và `/2` **âm thầm redirect** về trang danh sách vì
  2 ticket đó thuộc cửa hàng 3 trong khi cookie ghim cửa hàng 1 — đúng bẫy "đo nhầm trang" của
  D3b. Id thật lấy bằng cách scrape `href` từ chính trang danh sách → **ticket 40**.

---

## 1. Mật độ trước–sau — BA đòi *"không làm giao diện thưa hơn"*

`scrollHeight` toàn trang, 4 route × 4 breakpoint = **16 ô**. Tổng **−19px**.

| Route | 1920 | 1440 | 390 | 360 |
|---|---|---|---|---|
| `/portal/support/new` | 1080 → 1080 | 900 → 900 | 912 → **907** | 912 → **907** |
| `/portal/support/40` | 1080 → 1080 | 956 → **975** ⚠️ | 1338 → **1331** | 1380 → **1373** |
| `/portal/delivery/3` | 1080 → 1080 | 900 → 900 | 844 → 844 | 812 → 812 |
| `/portal/franchise-information` | 1185 → 1185 | 1256 → 1256 | 1381 → **1374** | 1401 → **1394** |

Ô bằng nhau ở 1920/1440/844/812 là trang **ngắn hơn viewport** ⇒ `scrollHeight` bị viewport
kẹp, không phải "không đổi". Mật độ thật của các trang đó đọc ở cột `cardH` mục 3.

`records` và `recordsInViewport` **không đổi ô nào** (9/9, 4/4, 7/7, 12/12 và 9/2/1/7/8 tương
ứng) ⇒ số bản ghi nhìn thấy trong màn hình đầu tiên giữ nguyên. **Pass.**

### ⚠️ 3 thẻ PC cao lên ở `/portal/support/40` — do chuẩn BA, không phải lỗi

| Card | `cardH` | Nguyên nhân |
|---|---|---|
| File đính kèm | 82,2 → **91,5** | `h6` cũ render **12,3px / line-height 14,7** |
| Trao đổi | 511,9 → **521,2** | ″ |
| Thông tin | 332,2 → **341,5** (1440: 354,7 → 364) | ″ |

Ba thẻ này trước đây dùng `<h6>` **thừa hưởng cỡ chữ 12,3px của theme Vuexy** — thấp hơn chuẩn
BA (PC compact **18px**) tới 5,7px. Nâng đúng chuẩn thì mỗi thẻ cao thêm **9,3px**. Đây là
**hệ quả trực tiếp của yêu cầu BA**, cùng dạng với 4 thẻ đã ghi ở D3b §1. Thẻ "Nội dung yêu
cầu" (`h5`, 20px) thì **giảm xuống 18px** và `cardH` **không đổi** (118 → 118).

---

## 2. `gapToBody` — đo trước rồi mới quyết, **kết luận: KHÔNG thêm rule nhịp nào**

Đo bằng `d3c_probe_gap.py` (đo thẳng trên `.wj-card-header`, leo lên wrapper khi header là con
duy nhất — `d3c_measure.py` leo theo mép trên nên với họ `.card-header` nó trả `None`).

| Chỗ | trước | sau | Nhận xét |
|---|---|---|---|
| `support/new` · Thông tin ticket | 14 | **8** | về đúng nhịp mobile BA |
| `support/40` · 4 card `.card-header` PC | 0 | **0** | padding 14/14 nằm ở chính header, y nguyên |
| `support/40` · Lịch sử trao đổi | 0 | **0** | card `padding:0`, đệm ở wrapper `14 14 0` |
| `franchise-information` · Cửa hàng nhượng quyền | 12 | **8** | |
| `franchise-information` · Hợp đồng nhượng quyền | 12 | **8** | |
| `franchise-information` · Thành viên cửa hàng | 12 | **8** | qua wrapper `padding:14 14 0` |
| `delivery/3` · 3 header D3a | 12 | **12** | không đụng tới |

`marginTop/marginBottom` của header sau migrate là **0/8** (mobile) hoặc **0/0** (biến thể
flush) — **không ô nào cộng chồng**, đúng kết luận D3b. **Không thêm rule CSS nhịp nào.**
Ứng viên đã soi và loại: `.card-body`, `.list-group`, `.wujia-mticket-thread`,
`.wujia-maccount-kvlist`, `.wujia-maccount-badgerow`, `.wj-pc-dlv-head-kv`,
`.wujia-mdash-list`. **Pass.**

---

## 3. Số BA theo computed style

| Ô BA | Chuẩn | Đo được | |
|---|---|---|---|
| PC · compact | 18 / 24 / 700 | `support/40` ×4 = **18 / 24 / 700** · `delivery/3` mã chuyến = **18 / 24 / 700** | Pass |
| Mobile · compact | 16 / 22 / 700 | `support/new` = **16 / 22 / 700** · `support/40` = **16 / 22 / 700** · `franchise-information` ×3 = **16 / 22 / 700** | Pass |
| Màu tiêu đề | `#111827` | **`rgb(17, 24, 39)`** ở **toàn bộ 11 call site × 4 breakpoint** | Pass |

Trước migrate `line-height` lệch chuẩn ở khắp nơi: **19,2** (mobile `wujia-maccount-cardtitle`),
**21** (`wujia-mdash-title`), **28,8** (h2 16px inline), **26,4** (h2 24px delivery), **14,7**
(h6 PC). Sau migrate **tất cả về đúng 22 (mobile) / 24 (PC)**.

Bẫy màu của D3b (`:not()` của theme Vuexy ở specificity (0,4,1) thắng
`.wj-card-header__title`) đã được vá từ D3b — phiên này **đo lại và vẫn đúng**, không tái phát
kể cả ở họ `.card-header` của Bootstrap. **Pass.**

---

## 4. Giả-heading → 0 · biến thể flush · count 0 vẫn hiển thị

| Route | `pseudoLeft` trước → sau | `.wj-card-header` trước → sau |
|---|---|---|
| `/portal/support/new` (390/360) | 1 → **0** | 0 → **1** |
| `/portal/support/40` (1920/1440) | 0 → 0 | 0 → **4** |
| `/portal/support/40` (390/360) | 1 → **0** | 0 → **1** |
| `/portal/delivery/3` (1920/1440) | 2 → **0** | 3 → **4** |
| `/portal/franchise-information` (390/360) | 4 → **0** | 0 → **3** |

Lớp bị xoá sổ trong 3 file: `wujia-mdash-title`, `wujia-maccount-cardtitle`,
`wujia-maccount-store-name`, `wj-pc-order-head__code`, `wj-pc-dlv-head-meta`,
`wj-pc-acct-staff__title`. Có unit test khoá lại (§7).

**Count 0 vẫn hiển thị:** header "Lịch sử trao đổi" mang `ch_meta` = "N phản hồi". Với ticket
0 comment, card vẫn render và meta vẫn in "0 phản hồi" — khoá bằng test
`ZERO_COUNT_VIEWS['wujia_portal_support.portal_support_detail'] = 'comments'`. **Pass.**

**Biến thể flush** dùng đúng 5 chỗ + 2 chỗ ở delivery/franchise (`FLUSH_VIEWS`): mọi chỗ đều
đi kèm `ch_platform` (`--m`/`--pc`), không chỗ nào flush "trần" — đúng bài học specificity của
D3b. Riêng `franchise-information` "Thành viên cửa hàng" **cố ý KHÔNG flush**: nhịp spec 8px
nhỏ hơn 12px cũ ⇒ đặc hơn, không thưa ra. **Pass.**

---

## 5. Outline heading — 2 route tốt lên, 1 route thêm heading đúng chỗ

| Route | trước | sau | |
|---|---|---|---|
| `/portal/support/new` (mobile) | `H1` | `H1 H2` | giả-heading `<p>` thành heading thật |
| `/portal/support/40` (PC) | `H1 H5 H6 H6 H6` | `H1 H3 H3 H3 H3` | hết nhảy cấp H1→H5 |
| `/portal/franchise-information` (mobile) | `H1 H2 H3 H2 H2` | `H1 H2 H2 H2` | H3 lạc giữa các H2 biến mất (thành dòng phụ) |
| 5 tổ hợp còn lại | — | **không đổi** | |

Component không có directive đổi tên thẻ động (Odoo 19 `ir_qweb.py:1705`) nên `h5`/`h6` buộc
đổi cấp; đã kiểm **không tụt cấp**, chỉ lên. **Pass.**

---

## 6. Chữ hiển thị không đổi

`textDigest` (toàn bộ `innerText` chuẩn hoá khoảng trắng) khớp **12/16 ô**. 4 ô lệch là **2 chỗ
đổi thứ tự DOM đã được chủ dự án duyệt**, và lệch **đúng kiểu hoán vị**:

| Route | Đoạn bị dời | Multiset token |
|---|---|---|
| `/portal/delivery/3` (1920, 1440) | `Sắp giao` xuống sau dòng phụ | **bằng nhau** |
| `/portal/franchise-information` (390, 360) | `HN-01 Đang hoạt động` xuống sau tên cửa hàng | **bằng nhau** |

Không token nào bị thêm/mất. **Pass.**

---

## 7. Build · unit test · mutation

| Bước | Kết quả |
|---|---|
| `-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_delivery` trên `wujia_tea_d3c` | **RC=0**, **0 ERROR** |
| `--test-tags wujia_card_header_d3` | **32 tests · 0 failed · 0 error** |
| Mutation (trả 1 markup cũ về) | **đúng 1 test đỏ** |

⚠️ **Bẫy đã trả giá:** `-u wujia_portal_support --test-tags …` chạy ra **"0 tests"** vì test
nằm ở `wujia_portal_layout` và là `post_install` ⇒ mutation phải chạy `-u wujia_portal_layout`.
Và log **rỗng giả**: `wujia_core` dời logfile giữa chừng sang
`<thư-mục-logfile>/<năm>/<tháng>/<ngày>.log`, file `--logfile` chỉ giữ ~49 dòng đầu.

Test mới thêm phiên này:
- `test_bootstrap_card_header_wrapper_class_is_kept` — 4 chỗ họ Bootstrap phải giữ nguyên
  `class="card-header wj-card-header--flush"` (mất `card-header` là vỡ nền/viền của Bootstrap).
- `test_store_name_became_subtitle_not_a_second_heading` — tên cửa hàng phải là `ch_subtitle`
  (đúng 1 chỗ) **và** header phải đứng **trước** `.wujia-maccount-badgerow` trong DOM.

---

## 8. Hồi quy

| Phép đo | Kết quả |
|---|---|
| Lưới B4 (17 route matrix + 5 ngoài matrix + 6 chiều rộng) | **286/286 Pass** |
| Tab-walk A/B, 6 route × 2 breakpoint, **250 điểm dừng** | số stop **12/12**, thứ tự **12/12**, focus ring **12/12** (246/250 có ring) |
| Chạy lại bảng **D3a** (`d3_measure.py`, 4 route × 4 vp) | **0 lệch ngoài ý muốn** — 6 trường lệch đều là thay đổi D3c cố ý ở `franchise-information` mobile (`realHeadings` 5→4, `lineHeight` 19,2→22, `gapToBody` 12→qua wrapper) |
| Chạy lại bảng **D3b** (`d3b_measure.py`, 11 route × 4 vp) | **0 lệch** |
| `pageerror` | **0** trên mọi route × breakpoint |
| Tràn ngang (`overflowX`) | **0** trên mọi route × breakpoint |
| HTTP status | **200** trên mọi route × breakpoint |

⚠️ **Một báo động giả đã truy tới cùng, đừng tin ngay lần đo đầu:** bảng D3b báo `/portal` 360px
`cardH` 97 → 122,4 ở thẻ "Khung giờ đặt hàng", kèm `textDigest` lệch `11:41` ↔ `11:40`. Đo lại
**cả hai server đều cho 122,4** ⇒ thẻ chứa **đồng hồ**, chiều cao đổi theo phút xuống dòng, không
phải hồi quy. Bài học D3b "harness đo sai còn nguy hơn không đo" lặp lại y hệt.

---

## 9. 🔴 Một lỗi bố cục thật, chỉ lộ ra khi chụp ảnh — đã sửa trong phiên

Sau khi migrate `.wj-pc-dlv-head`, badge trạng thái **"Sắp giao" trôi ra mép phải cột trái**,
cách mã chuyến cả trăm px — nhìn như lỗi, dù mọi con số đo đều đạt.

Nguyên nhân (đọc CSS, không đoán): `.wj-card-header` là `display:flex; width:100%` còn
`.wj-card-header__lead` là **`flex: 1 1 auto`** ⇒ vùng lead nở hết bề rộng cột và đẩy slot
trailing ra biên. Bố cục cũ (`.wj-pc-dlv-head-coderow`) thì co theo nội dung.

Sửa **trong scope module delivery**, không đụng component dùng chung:

```css
/* custom/wujia_portal_delivery/static/src/css/portal_delivery.css */
.wj-pc-dlv-head .wj-card-header__lead { flex: 0 1 auto; }
```

Sau sửa: badge bám ngay sau khối tiêu đề, `cardH` của summary head **105 → 92** (thấp hơn bản
cũ 13px). Ảnh chứng minh: `scratchpad/d3c-shots/dlv_head_{before,after}.png`.
File CSS này nạp qua **asset bundle** (`__manifest__.py:15`), **không** phải `<link>` tay ⇒
**không cần bump `?v=`** ở `wujia_portal_layout/views/assets.xml`.

---

## 10. Hai chỗ đổi thứ tự DOM — chủ dự án duyệt trước khi code

1. **`portal_franchise_information.xml:179` (mobile).** Trước: `h2 tiêu đề → badgerow →
   h3 tên cửa hàng → p khu vực`. Sau: `[h2 tiêu đề + tên cửa hàng làm dòng phụ] → badgerow →
   p khu vực`. Lý do chọn phương án này: **bản PC của chính card đó**
   (`wj-pc-acct-headcard`, dòng 40–47) vốn đã xếp `title → sub → chips` ⇒ mobile khớp PC.
2. **`portal_delivery.xml:377` (PC).** Badge trạng thái từ cùng dòng với mã chuyến chuyển
   thành **slot trailing** của header (spec cho **tối đa MỘT** trailing), khối 3 cặp KV bên
   phải **ở lại là nội dung card** — đúng cách D3a đã xử `wj-pc-acct-headcard__chips/__box`.

Ảnh trước/sau: `scratchpad/d3c-shots/{dlv_head,acct_card}_{before,after}.png`.
Chữ hiển thị **không mất token nào** (§6). Cần BA xác nhận lại lúc retest.

---

## 11. LIMIT — ghi nhận, KHÔNG sửa ở D3c

| # | Chỗ | Vì sao để lại |
|---|---|---|
| 1 | `portal_franchise_information.xml:40/:49` `wj-pc-acct-headcard__title` + `__box` | fork **2 vùng trailing** vs spec cho tối đa 1 — **chờ BA**, kế thừa từ D3b |
| 2 | `portal_delivery.xml:118/:126` | đã loại ở inventory §3 (slot phải / `CMP-ES-001`) — mobile `/portal/delivery/3` vẫn còn 2 `div` tiêu đề 18/27 và 15/22,5 |
| 3 | `portal_franchise_information.xml:290` `h4` khoá cửa hàng | như trên |
| 4 | 3 heading EmptyState | thuộc `CMP-ES-001`, không phải CardHeader |
| 5 | 3 chỗ SectionHeader ↔ CardHeader treo từ C8 | **chờ BA** |
| 6 | FilterCard | **0 call site** ⇒ dựng mới, không phải migrate |
| 7 | Xoá các class CSS đã nghỉ hưu (inventory §7) | **khoá tới khi phủ 100%** — hiện 47/103 |
| 8 | Nhãn option rỗng bộ lọc lệch 4 màn | → **D7+** |
| 9 | `/portal/reports/orders` 500 khi tz `Asia/Saigon` | → **R3** |
| 10 | `portal_home.xml` còn `.strftime()` · `/portal/notification/41` outline `H3` trước `H2` | → **R2** |

---

## 12. Bàn giao deploy

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_delivery
```

Không module mới · không migration · không cập nhật dữ liệu · **không** cần kèm `wujia_sale`
(không đụng `wujia_portal_return`) · **không** cần bump `?v=` (CSS đổi nằm trong asset bundle).

| Module | Version |
|---|---|
| `wujia_portal_layout` | `19.0.32.7.0` (không đổi — chỉ thêm test) |
| `wujia_portal_base` | `19.0.7.6.0` → **`19.0.7.7.0`** |
| `wujia_portal_support` | `19.0.3.13.0` → **`19.0.3.14.0`** |
| `wujia_portal_delivery` | `19.0.3.7.0` → **`19.0.3.8.1`** |

`UI-CARDHEADER-001` **vẫn `Ready for Dev`** (47/103) ⇒ **KHÔNG** chạy `qa_sync.py`; entry
ledger giữ dạng comment cuối `docs/qa-issue-ledger.yaml`.

---

## 13. Sau deploy — bắt buộc

L14/L10 đã lật ngược kết quả **3 lần** (C6, D2, D3b): UAT có `website`/`website_sale` nên bundle
frontend khác local. ⇒ Sau khi chủ dự án `-u`, **đo lại chỉ-đọc ngay trên UAT** bằng
`scratchpad/d3b_uat_verify.py` (kỳ vọng suy từ **chính modifier của element**, không phải bảng
cứng theo route), rồi mới `scripts/ba_spec/qa_deploy_mark.py`.
Trước khi kết luận "lỗi", kiểm 2 thứ đã trả giá: **slug/route có tồn tại thật không** và **kỳ
vọng có quá rộng không**.

---

## 14. Tổng kết 21 ô acceptance

| Nhóm | Ô | Pass |
|---|---|---|
| Mật độ (§1) | 3 | 3 |
| Nhịp `gapToBody` (§2) | 2 | 2 |
| Số BA + màu (§3) | 3 | 3 |
| Giả-heading · flush · count 0 (§4) | 3 | 3 |
| Outline (§5) | 2 | 2 |
| Chữ hiển thị (§6) | 1 | 1 |
| Build · test · mutation (§7) | 3 | 3 |
| Hồi quy (§8) | 3 | 3 |
| Phủ call site | 1 | **phần** (47/103, cố ý) |
| **Tổng** | **21** | **20 + 1 phần = 97,6%** |
