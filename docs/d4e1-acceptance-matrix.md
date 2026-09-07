# D4e1 — bảng nghiệm thu SurfaceCard lượt 4 (họ `wj-pc-metric-card`)

Issue `UI-SURFACECARD-001` (STT 127 · `CMP-SC-001`). Lượt này migrate **toàn bộ họ
`wj-pc-metric-card`: 12 shell / 3 file / 3 module**, trong một lần `-u`.

Đo trên **DB copy `wujia_tea_d4e1`** (cổng 8075) vì bản gốc `wujia_tea_19` không đo được cả hai
route sản phẩm — xem §1.

---

## 0. Ba đính chính trước khi sửa dòng CSS đầu tiên

1. **Phạm vi 7 → 12 shell.** Prompt giới hạn ở 4 ô KPI của trang báo cáo. Chủ dự án chốt kéo
   thêm 4 lượt `pc_preview` (gallery tham chiếu, để lệch thì gallery nói dối) và 4 lượt màn
   Khảo sát (cờ *provisional* của BA chỉ gắn vào **field mapping**, không gắn vào khung).
   Chia theo **HỌ chứ không theo màn** — chẻ đôi họ giữa hai lượt là tự tạo cửa sổ
   variant-theo-route, đúng thứ BA cấm. `wj-rep-mcard` + 2 món nợ D4d tách sang **D4e2**.
2. **Kiểm kê 44/16 là đếm thô.** Shell thật: `wj-pc-metric-card` **12**, `wj-rep-mcard` **3**
   (→ inventory §13.1). `scripts/qa/wj_inventory.py` mà prompt nhắc **không tồn tại**.
3. **`?v=` hiện là 1190**, không phải 1200 (`assets.xml:81–86`).

## 1. Chặn kỹ thuật — gỡ bằng DB copy, KHÔNG sửa bug

| Route | Vướng trên `wujia_tea_19` | Cách gỡ trên bản copy |
|---|---|---|
| `/portal/reports/orders` | **500 có sẵn** — `anh.owner` có `tz='Asia/Saigon'`, pytz không nhận (cụm **R3**) | đổi `tz` → `Asia/Ho_Chi_Minh` **chỉ trên copy**. KHÔNG sửa `portal_tz()` |
| `/portal/inspection/detail/<id>` | `wujia_portal_inspection` **`uninstalled`** — prompt ghi "nay DB dev đã cài" là **SAI**, kiểm bằng `ir_module_module` | `-i wujia_portal_inspection` + seed 1 phiếu `state=done` cho franchise `HN-01` |
| `/portal/_pc-preview` | `auth='user'` + chặn user không phải nội bộ | đo bằng phiên **`admin`**; hai route kia vẫn **`anh.owner`** (bẫy "Pass rỗng") |

Cổng **8075** (`8070`/`8071` cụm R · `8072` server đo · `8019` UAT — không đụng).
Đo xong **drop DB copy**.

## 2. Đã làm

- **CSS `_pc_components.css:132`** — rút `background` / `border` / `border-radius` / `gap` khỏi
  `.wj-pc-metric-card`; đệm ngang `0 22px` → `0 16px`. **Giữ** `display:flex; align-items:center`
  (biến thể `--summary` chỉ khai `gap`, không khai `display` — bỏ đi là `gap` vô tác dụng và
  icon/label vỡ hàng, đúng cách D4d giữ cho `.wj-filter-card`) và **giữ `min-height`** (§3).
- **CSS `portal_report.css:74`** — **gỡ hẳn** override liên module
  `.wj-rep-pcmetrics .wj-pc-metric-card { min-height:100px; gap:14px; padding:0 16px }`.
  Rule này **SỐNG**, không phải rule chết như bẫy #4 của D4d: đếm lúc chạy ra **đúng 4 phần tử
  khớp ở cả 5 khổ**. Đặc hiệu `(0,2,0)` thắng chủ sở hữu `(0,1,0)` và lại nạp sau ⇒ giữ lại là
  đẻ variant theo route. **Cố ý giữ** `.wj-rep-pcmetrics { gap: 24px }` (gap của LƯỚI, không
  phải của thẻ) và `.wj-rep-pcmetrics .wj-pc-metric-card__value { font-size: 24px }` (cỡ chữ
  không phải dáng khung).
- **12 call site** → `t-call="wujia_portal_layout.wj_surface_card"` với
  `sc_variant='summary'` · `sc_body='flush'` · `sc_class='wj-pc-metric-card'`.
  `summary` là biến thể **duy nhất** khai `gap` (Luật #8); `flush` vì đệm dọc của họ này = 0.
  Lớp cũ giữ nguyên qua `sc_class` (Luật #1 — CSS con `__icon`/`__body`/`__label`/`__value`
  và 3 danh sách `:is()` `(0,3,0)` của `_interaction.css` bám vào nó).
- `wujia_portal_layout` **19.0.35.0.0 → 19.0.36.0.0**; `?v=1190 → 1200` (4 file nạp bằng
  `<link>` tay). `wujia_portal_report` / `wujia_portal_inspection` chỉ đổi XML ⇒ **không** bump.
- `-u wujia_portal_layout,wujia_portal_report,wujia_portal_inspection` — **đúng một lần**.
  Không module mới, không migration.

## 3. 🔴 `min-height` — số đo lật ngược giả định của prompt

Prompt tính "bỏ `min-height` thì thẻ còn 84 (compact) / 92 (regular)" từ giả định **nội dung =
icon 52px**. Đo thật: nội dung là khối 3 dòng (label + value + desc), cao **52–98px**.

| Route | Thẻ cao | Nội dung | `min-height` gánh | Nếu lấy compact p16 |
|---|---:|---:|---:|---:|
| `/portal/_pc-preview` PC | 96 | 56 | 40 | 88 |
| `/portal/inspection/detail/1` PC | 96 | 52–**89** | 7–44 | 84–**121** |
| `/portal/reports/orders` PC | 100 | 67–**94** | 6–33 | 99–**126** |
| `/portal/_pc-preview` @390/360 | 100 | **98** | 2 | **130** |

Đệm dọc = 0 ⇒ `min-height` là **SÀN chiều cao thiết kế**, bỏ đi thì thẻ **cao lên**, tức
*thưa hơn sau migration* — chỏi thẳng câu BA viết trong `Kết quả mong muốn` và acceptance #11.

**Chốt của chủ dự án:** giữ đệm dọc 0 + `min-height`; hội tụ hai họ về **một** bộ số
`minH 96 · pad-x 16 · gap 12` (mobile 8). Ghi LIMIT (§9 mục 1).

## 4. Kết quả cốt lõi — hai chữ ký dáng khung về MỘT

| | `pad` | `gap` | `radius` | viền | `min-height` | route |
|---|---|---|---|---|---|---|
| **trước** | `0/16/0/16` | 14px | 16 | 1px `#EEF2F5` | 100px | báo cáo |
| **trước** | `0/22/0/22` | 16px | 16 | 1px `#EEF2F5` | 96px | gallery · khảo sát |
| **sau** | `0/16/0/16` | 12px | 16 | 1px `#EEF2F5` | 96px | **cả ba** |

Đây là hạng mục chính của issue: **variant-theo-route bị xoá**, không còn "cùng một class, hai
dáng theo màn".

## 5. Bảng đo TRƯỚC → SAU (3 route × 5 khổ, `scratchpad/d4e1_{before,after}.json`)

| Route | Khổ | `h` | `pad` | `gap` | `r` | `pageH` | recInView |
|---|---:|---|---|---|---|---|---|
| `/portal/_pc-preview` | 1440 · 1024 · 992 | 96 | `0/22`→`0/16` | 16→**12** | 16 | không đổi | không đổi |
| `/portal/_pc-preview` | 390 · 360 | 100 | `0/22`→`0/16` | 16→**8** | 16→**14** | không đổi | không đổi |
| `/portal/inspection/detail/1` | 1440 · 1024 · 992 | 96 | `0/22`→`0/16` | 16→**12** | 16 | không đổi | không đổi |
| `/portal/inspection/detail/1` | 390 · 360 | *ẩn* | — | — | — | không đổi | không đổi |
| `/portal/reports/orders` | 1440 | **100→96** | `0/16` | 14→**12** | 16 | 1023→**1019** | không đổi |
| `/portal/reports/orders` | 1024 · 992 | **100→96** | `0/16` | 14→**12** | 16 | 1040→**1036** | không đổi |
| `/portal/reports/orders` | 390 · 360 | *ẩn* | — | — | — | không đổi | không đổi |

- **60/60 bề mặt duyệt** ở cả hai lượt · **0 lỗi JS · 0 tràn ngang · 0 redirect ngầm · HTTP 200**.
- **0 ô mất record trong viewport** (acceptance BA #11) · **0 ô có bề mặt trắng lồng bề mặt trắng**.
- Ở mobile, họ này chỉ còn hiện trên **gallery dev** — hai route sản phẩm bọc `d-none d-lg-*`
  (đo ra `h=0`). Nên `radius 16→14` và `gap 16→8` ở mobile **không đổi gì trên sản phẩm thật**;
  chúng chỉ làm gallery khớp cột mobile của BA.

## 6. Nhịp header→body — đo TUYỆT ĐỐI

RULE 1/2 đo *sự không đều giữa các card* nên sai số **đều tay** lọt sạch (bài học D4b). Đo tuyệt
đối trước–sau: **15/15 ô giống hệt** — `inspection` `[12]→[12]`, `report` `[0,0,0]→[0,0,0]`,
`pc_preview` `[]→[]`. **0 ô lệch nhịp** ⇒ D4e1 không xê dịch hợp đồng CardHeader.

## 7. Ảnh trước–sau + diff pixel

| Trang | Khổ | Diff pixel | Giải trình |
|---|---:|---|---|
| `report-orders` | 1440 | cao 1023→1019 | −4px, đúng `minH 100→96` |
| `report-orders` | 390 | **0 pixel** | lưới KPI ẩn ở mobile |
| `inspection/detail/1` | 1440 | bbox `(341,262,1362,317)` | đúng dải KPI |
| `inspection/detail/1` | 390 | **0 pixel** | lưới KPI ẩn ở mobile |
| `_pc-preview` | 1440 · 390 | bbox dải KPI | đúng phạm vi |
| **`/portal`** | 1440 | **0 pixel** | ngoài phạm vi ✓ |
| **`/portal`** | 390 | bbox `(349,428,357,437)` 8×9px | 🔍 **soi ảnh: đồng hồ đếm ngược `còn 06:04` → `06:05`** — tiền lệ D3c, không phải hồi quy |
| **`/portal/support`** | 1440 · 390 | **0 pixel** | ngoài phạm vi ✓ |
| **`/portal/delivery`** | 1440 · 390 | **0 pixel** | ngoài phạm vi ✓ |

**Soi mắt** dải KPI `/portal/inspection/detail/1` @1440 trước/sau: 4 thẻ cùng cao 96, cùng lề,
inset chặt hơn, **không vỡ hàng, không tràn, không trôi badge**. Trên `/portal/reports/orders`
@1440 lộ ra một **cải thiện ngoài dự tính**: "Tổng chi phí 342.200,00 $" trước đây **xuống 2
dòng**, `gap 14→12` trả lại đúng chỗ thiếu ⇒ nay **1 dòng** — đúng ý BA *"primary amount dễ quét"*.

> ⚠️ `/portal/_pc-preview` bị **modal chọn cửa hàng** (ADR-011) phủ lên khi đăng nhập `admin`,
> nên ảnh full-page của route này soi mắt không dùng được; số đo không bị ảnh hưởng (đọc
> `getComputedStyle`). Đã soi bằng route sản phẩm thay thế.

## 8. Guard chứng minh bằng ĐỘT BIẾN

`-u wujia_portal_layout,wujia_portal_report,wujia_portal_inspection --test-tags
wujia_surface_card_d4` → **52 test, 0 failed / 0 error** (mốc D4d là 45 ⇒ **+7 test mới**).
Run đối chứng sau khi hoàn nguyên toàn bộ đột biến: **52/0/0**.

| # | Đột biến | Test đỏ |
|---|---|---|
| 1 | trả `background` vào rule họ | `test_metric_card_no_longer_declares_surface_shape` |
| 2 | hồi sinh override liên module | `test_report_cross_module_override_is_gone` |
| 3 | xoá override cỡ chữ cố ý giữ | `test_report_keeps_its_non_shape_overrides` |
| 4 | gỡ `min-height` | `test_metric_card_keeps_flex_and_height_floor` |
| 5 | đệm ngang về 22 | `test_horizontal_inset_converged_to_16` |
| 6 | call site gọi nhầm component khác | `test_all_metric_call_sites_use_the_component` |
| 7 | `flush` → `padded` | `test_call_sites_bake_summary_and_flush` |

**7/7 đỏ đúng chỗ.**

### Hai lỗi của chính vòng đột biến — cả hai đều là loại "báo guard rỗng oan"

1. 🔴 **Bộ dò `FAIL:` viết `[A-Za-z]+` nên không khớp tên lớp có CHỮ SỐ.** Lớp tên
   `TestSurfaceCardD4e1` ⇒ **cả 7 đột biến đều báo "KHÔNG ĐỎ"** trong khi thật ra cả 7 đều đỏ.
   Đúng họ bẫy D4d #2, chỉ đổi chỗ: lần đó `sed` trượt thụt lề, lần này regex trượt chữ số.
   **Bảy guard cùng "rỗng" một lượt là dấu hiệu của bộ dò hỏng, không phải của guard yếu** —
   đã xác minh tay một đột biến trước khi kết luận.
2. 🔴 **Đột biến làm XML SAI CÚ PHÁP thì `-u` abort, view không đổi, test xanh oan.** Đổi
   `<t t-call>` thành `<div>` để lại thẻ đóng `</t>` lệch ⇒ `ExpatError`. Phải chọn đột biến
   **giữ XML hợp lệ** (đổi sang `wj_card_header`). Đây là bẫy MỚI, chưa có trong sổ D4.

## 9. Đặc hiệu CSS — quét toàn bộ 280 file CSS của `custom/`

`scratchpad/d4e1_spec_scan.py`, loại tên con BEM khỏi phép khớp (bài học D4d #10) và phân biệt
rule **trạng thái nghỉ** với `:hover`/`:active`:

> **1 hit duy nhất**: `padding` ở `.wj-pc-metric-card` (`_pc_components.css`) — chính là thứ
> chủ dự án **chốt giữ**. Không file nào khác khai dáng khung cho họ này.

## 10. RULE 1 + RULE 2 chạy lại

`python3 scratchpad/d3_review.py --base http://127.0.0.1:8075 --portal-login anh.owner`
(→ `d4e1_rule_after.json`) rồi `d3_analyze.py`:

```
TỔNG: 4 route/viewport có cờ · 0 nhóm cỡ chữ DRIFT chưa giải trình
```

**4 cờ = 4× `debt-pay` redirect `?notice=no_due`** — cờ có sẵn, đúng thiết kế WJ-DEBT-007
(hết nợ thì không vào trang trả tiền). **Không cờ mới nào.** RULE 2: `[pc] 18px ×94`,
`[m] 16px ×62`, `[pc] 20px ×2` (`history-detail`) — y hệt baseline.

## 11. Đối chiếu `Kết quả mong muốn` (phần thuộc D4e1)

| Hạng mục BA | Kết quả |
|---|---|
| Dùng thống nhất CMP-SC-001 | ✅ 12/12 shell qua component, 2 chữ ký → **1** |
| **Không thưa hơn sau migration** | ✅ report thấp 100→96, `pageH` −4px, **0 ô mất record** |
| Desktop radius 16 · gap 12 | ✅ 16 / 12 |
| Mobile radius 14 · gap 8 | ✅ 14 / 8 (chỉ gallery còn hiện ở mobile) |
| Desktop compact padding 16 | ⚠️ **ngang 16 ✓, dọc 0** — cố ý, xem §3 + LIMIT 1 |
| Border nhẹ, không shadow mặc định | ✅ 1px `#EEF2F5`, `box-shadow: none` |
| Không lồng white card | ✅ 0 ô |
| Không tạo variant theo route | ✅ gỡ hẳn override liên module (khớp thật 4 phần tử) |
| Primary amount dễ quét | ✅ "342.200,00 $" từ 2 dòng về 1 dòng |
| Test 1440 · 1024 · 992 · 390 · 360 | ✅ đủ 5 khổ |
| Màn Khảo sát — field mapping | ⏭ BA ghi *provisional*; D4e1 **chỉ đụng khung** |

**10/11 hạng mục áp dụng được đạt trọn + 1 đạt có điều kiện (đã ghi LIMIT) ≈ 95%.**

## 12. LIMIT phải ghi vào ledger

1. **`padding` ngang (`0 16px`) và `min-height` (`96px`) CỐ Ý ở lại rule họ**, không dời sang
   `.wj-surface-card` — vì đệm dọc của họ này bằng 0 nên `min-height` là sàn thiết kế; dời theo
   Luật #7 làm thẻ **cao lên 121–130px** ⇒ thưa hơn. Tiền lệ `.wj-debt-summary{height:142px}`
   của D4c. **Chủ dự án chốt sau khi xem số đo.**
2. **Đo trên DB copy `wujia_tea_d4e1`, chưa soi UAT.** Hai route sản phẩm không đo được trên
   `wujia_tea_19` (tz 500 + module uninstalled) ⇒ **PHẢI đo lại chỉ-đọc trên UAT sau deploy**
   (L14/L10: UAT có `website`/`website_sale` nên bundle frontend khác local, từng lật ngược kết
   quả ở C6 và D2) rồi mới `qa_deploy_mark.py`.
3. **Bug tz `/portal/reports/orders` KHÔNG được sửa** — thuộc cụm **R3**
   (`wujia_portal_base/controllers/utils.py:38`). D4e1 chỉ né trên bản copy.
4. **`wujia_portal_inspection` vẫn `uninstalled` trên `wujia_tea_19`.** Deploy UAT phải kiểm
   module này có `installed` không; nếu chưa thì 4 lượt khảo sát không hiện để retest.
5. Nhóm Khảo sát vẫn *provisional* — D4e1 **không** chốt hộ BA field mapping nào.
6. `wj-rep-mcard` (3) + 2 món nợ D4d (nhịp `18/23/25` · 2 inline `padding:14px 14px 0`) sang
   **D4e2**, chưa đụng ở lượt này.
7. Tiến độ cụm **110/384 ≈ 29%** ⇒ issue **giữ `Ready for Dev`**, chưa handoff.
   **Dev không tự đóng `Done`.**
