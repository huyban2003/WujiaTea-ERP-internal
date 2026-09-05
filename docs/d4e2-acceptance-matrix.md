# D4e2 — bảng nghiệm thu SurfaceCard lượt 5 (`wj-rep-mcard` + 2 món nợ D4d)

Issue `UI-SURFACECARD-001` (STT 127 · `CMP-SC-001`). Lượt này khép **nửa còn lại của D4e**:
3 shell `wj-rep-mcard` + 2 inline `padding:14px 14px 0` + 18 ô nhịp header→body `18/23/25` → `12`.

Đo trên **DB copy `wujia_tea_d4e2`** (cổng 8075) — lý do §1. Tiến độ cụm sau lượt:
**113/384 ≈ 29%** ⇒ issue **giữ `Ready for Dev`**, chưa handoff.

---

## 0. Đính chính trước khi sửa dòng CSS đầu tiên

1. **`_pc_components.css:163` là SAI — neo thật ở dòng 168.** Prompt ghi 163; `grep` ra 168.
2. **"nhịp `12×48`" trong prompt sai số học.** Tổng ô đo được là **52** (`d4c_rhythm`), trong đó
   2 ô `0px` cố ý giữ ⇒ đích đúng là **`12×50 · 0×2`**, không phải 48. Đo sau xác nhận đúng 50.
3. **`.wj-rep-mcard` không hề khai viền.** Rule cũ (`portal_report.css:317`, nằm **trong**
   `@media (max-width: 991.98px)` mở ở dòng 204) chỉ có `background` + `border-radius`.
   Nên migration **thêm** 1px viền chứ không phải giữ nguyên — số đo §3 nói rõ.

## 1. Chặn kỹ thuật — gỡ bằng DB copy, KHÔNG sửa bug

| Route | Vướng | Cách gỡ trên bản copy |
|---|---|---|
| `/portal/reports/orders` | **500 có sẵn** — `anh.owner` có `tz='Asia/Saigon'` (cụm **R3**) | `UPDATE res_partner SET tz='Asia/Ho_Chi_Minh'` (4 dòng) **chỉ trên copy**. KHÔNG đụng `wujia_portal_base/controllers/utils.py:38` |
| `/portal/support/1` | **redirect ngầm** về `/portal/support` — ticket thuộc franchise khác | tìm bằng SQL ticket **`40`** (`franchise_id=1`, `created_by_id=5`, 2 bình luận) rồi đo route đó |

Bản copy tạo bằng `pg_dump | pg_restore` (không dùng `TEMPLATE` để khỏi phải giết server đo).
Cổng **8075**; `8070`/`8071` cụm R · `8072` server đo · `8019` UAT — không đụng.

### 🔴 Bẫy lớn nhất của lượt: **D4e1 chưa commit và chưa từng `-u` lên DB này**

`git diff --stat` ra **15 file đang sửa** trên nhánh `dev/2026-09-05-d4c` (commit cuối `5758495`
= D4d), và `wujia_portal_layout` cài ở **`19.0.35.0.0`** trong khi manifest ghi `19.0.36.0.0`.
D4e1 **cũng sửa `portal_report_orders.xml`** ⇒ baseline đầu tiên của tôi đọc template D4d cũ,
và cú `-u` của D4e2 sẽ nhét thay đổi D4e1 vào cột "sau" — **trước/sau lẫn hai lượt**.

Gỡ theo đúng quy trình D4e1 tự ghi: cất bài D4e2 ra `scratchpad/d4e2_work/`, khôi phục `.bak`,
`-u` (RC=0, 0 ERROR) để nạp **đúng trạng thái D4e1**, rồi đo lại từ đầu. Số bề mặt
**210 → 230** — chứng minh baseline đầu là sai.

## 2. Đã làm

**A · `wj-rep-mcard` (3 shell, `wujia_portal_report`)**
- CSS: **xoá hẳn** rule `.wj-rep-mcard` (chỉ còn 2 dòng chú thích) — theo tiền lệ D4d
  (`_components.css:2263`). Giữ nguyên `__head` (`padding: 0 12px`, `min-height: 50px`),
  `__title`, `__meta`, `__body` (`padding: 12px`) và `--chart .wj-rep-mcard__body`
  (`padding: 0 12px 8px`) — đó là **nội dung**, không phải khung.
- Call site `portal_report_orders.xml:85 · 98 · 132`: QWeb O19 **không có** directive đổi tên thẻ
  (`ir_qweb.py:1705`) và call site là `<section>` chứa `<h2>` ⇒ **giữ `<section>`, gắn thẳng
  4 lớp chủ sở hữu** `wj-surface-card wj-surface-card--section wj-surface-card--compact
  wj-surface-card--flush`, **giữ lớp cũ** `wj-rep-mcard` (+ `--chart`).
  Đã kiểm: `--section` và `--compact` **không có rule CSS nào** — chúng là mốc đánh dấu trơ,
  viết đủ 4 lớp để khớp đúng cái component sinh ra và 9 call site tay của D4d.
- Không migrate `__head` sang `wj_card_header` (§3.2 chủ dự án chốt): `__head` có `__meta` +
  `min-height:50`, không nằm trong hợp đồng CardHeader ⇒ việc của cụm **D3**.

**B · 2 inline padding**
- Thêm **một** class dùng chung ở `_components.css` (cạnh khối SurfaceCard), không đẻ 2 class
  cho 2 module:
  ```css
  .wj-surface-headpad { padding: var(--wujia-surface-pad-regular) var(--wujia-surface-pad-regular) 0; }
  ```
- Gỡ `style="padding:14px 14px 0;"` ở `wujia_portal_base/views/portal_franchise_information.xml:264`
  và `wujia_portal_support/views/portal_support.xml:574` (chủ template xác minh bằng `awk`:
  `portal_franchise_information` và `portal_support_detail`).

**C · nhịp header→body → 12 (18 ô)**
| Neo | Sửa |
|---|---|
| `_pc_components.css:**168**` `.wj-pc-card__head { margin-bottom: 18px }` | → **12px** (10 ô) |
| `portal_exam.css:759` `.wj-exam-pc-card__head { margin-bottom: 25px }` | **xoá hẳn rule** (2 ô) |
| `portal_exam.css:817` `.wj-exam-pc-dhead { margin-bottom: 23px }` | **xoá hẳn rule** (2 ô) |
| `portal_exam.css:984` `.wj-exam-pc-fcard .wj-exam-pc-field { margin-top: 18px }` | **xoá hẳn rule** (2 ô) |
| `portal_exam.css:1404` `.wj-exam-pc-sumlist` | bỏ `margin-top: 18px`, **giữ** `display/flex-direction/gap: 23px` (2 ô) |

> 🔴 **Vì sao phải XOÁ chứ không sửa số ở exam.** Header exam mang **cả hai** lớp
> (`wj-pc-card__head wj-exam-pc-card__head`), **cùng đặc hiệu `(0,1,0)`**, file exam nạp **sau**
> ⇒ chỉnh rule dùng chung về 12 mà để override exam sống thì 8 ô exam **không đổi gì**.
> Xoá override để chúng rơi về đúng **một chủ sở hữu**.

**Bump + `-u` đúng một lần**
- `assets.xml:82 · 84`: `?v=1200 → 1210` (`_components.css` và `_pc_components.css`, cả hai bị đụng).
- `wujia_portal_layout/__manifest__.py`: **`19.0.36.0.0` → `19.0.37.0.0`**. 4 module còn lại chỉ
  đổi XML/CSS-không-versioned ⇒ không bump.
- `-u wujia_portal_layout,wujia_portal_report,wujia_portal_base,wujia_portal_support,wujia_portal_exam`
  — một lệnh, một lần.

## 3. Phần A — số đo TRƯỚC → SAU (`scratchpad/d4e2_{before,after}.json`)

Ba shell **chỉ tồn tại ở mobile**; ở 1440/1024/992 đo ra `h=0`, `vis=false` — **chứng minh bằng
số đo**, không phải bằng đọc CSS.

| Thẻ | Khổ | `h` | `radius` | viền | `pad` |
|---|---:|---|---|---|---|
| `--chart` | 390 · 360 | **258 → 260** | **16 → 14** | `none` → **1px `#E5E7EB`** | `0/0/0/0` (flush) |
| shell 2 | 390 · 360 | **190 → 192** | **16 → 14** | `none` → **1px** | `0/0/0/0` |
| shell 3 | 390 · 360 | **290 → 292** | **16 → 14** | `none` → **1px** | `0/0/0/0` |
| cả 3 | 1440 · 1024 · 992 | `0` → `0` | — | — | *ẩn* |

`+2px` = **viền trên + viền dưới**, đúng con số chủ dự án duyệt ở §3.1 (`258 → 260`, `r16 → r14`).
`pageH` báo cáo mobile `1379 → 1385` và `1403 → 1409` = **3 thẻ × 2px**. Khớp chính xác.

## 4. Phần B — bỏ inline mà hình học đổi **0px**

| Route | Khổ | `inlineStyle` | `pad` | `x` | `w` | `pageH` |
|---|---:|---|---|---:|---:|---|
| `/portal/franchise-information` | 390 | `padding:14px 14px 0;` → **rỗng** | `14/14/0/14` **không đổi** | 17 | 356 | không đổi |
| `/portal/franchise-information` | 360 | → **rỗng** | `14/14/0/14` | 17 | 326 | không đổi |
| `/portal/support/40` | 390 | → **rỗng** | `14/14/0/14` | 17 | 356 | không đổi |
| `/portal/support/40` | 360 | → **rỗng** | `14/14/0/14` | 17 | 326 | không đổi |

Vẫn thẳng cột với `.wujia-mdash-list` (`padLeft=14`, `x=17`). Đúng lời hứa của **Đường A**
(§3.3): đổi chủ sở hữu, **không** đổi pixel. Ở 1440/1024/992 wrapper không tồn tại (markup
chỉ-mobile) nên token `20px` của PC hiện chưa có tác dụng ở đâu — ghi LIMIT 6.

## 5. Phần C — nhịp đo TUYỆT ĐỐI (`scratchpad/d4e2_rhythm_{before,after}.json`)

RULE 1/2 đo *độ lệch giữa các card* nên **sai số đều tay lọt sạch** (bài học D4b) ⇒ phải đo tuyệt đối.

```
TRƯỚC:  0×2 · 12×32 · 18×14 · 23×2 · 25×2      (52 ô)
SAU:    0×2 · 12×50                            (52 ô)
```

**18/18 ô hội tụ về đúng 12**, không ô nào ra `12+12` (nghi vấn margin-collapse ở
`fcard`/`sumlist` — đo thật bác bỏ). 2 ô `0px` ở `/portal/notification/41` **giữ nguyên** theo
§3.4 (lỗi outline `h3`/`h2` thuộc cụm **R2**). Tổng số ô không đổi ⇒ không ô nào biến mất.

`pageH` đổi ở **9/50** ô, tất cả đúng hướng **đặc hơn**: `/portal/change-password` −18,
`/portal/exam/register` −12 (PC 992/1024) và −6 (1440), `/portal/profile` −6 — và
`/portal/reports/orders` **+6** là 3 viền của phần A.

## 6. Sức khoẻ trang — 50 ô × 2 lượt

- **230 bề mặt** duyệt ở cả hai lượt (bằng nhau).
- **0 ô mất record trong viewport** (acceptance BA #11) · **0 bề mặt trắng lồng bề mặt trắng**.
- **0 redirect ngầm · 0 HTTP ≠ 200 · 0 tràn ngang · 0 lỗi JS · 0 ERROR** trong log xoay vòng.

## 7. Ảnh trước–sau + diff pixel (42 ảnh, 14 route × 1440/390/360)

| Trang | Kết quả | Giải trình |
|---|---|---|
| `/portal/reports/orders` @390 · @360 | bbox đúng 3 thẻ | phạm vi phần A ✓ |
| `/portal/franchise-information`, `/portal/support/40` | **0 pixel** | phần B đổi 0px ✓ |
| các trang PC phần C | bbox đúng dải header→body | ✓ |
| **`/portal`** @390 · @360 | khác vài pixel | 🔍 **đọc thẳng chữ số: "còn 04:39" → "còn 04:31"** + thanh tiến trình — đồng hồ đếm ngược, tiền lệ D3c |
| **`/portal/exam`** @390 | 8 px | thử **hoàn nguyên CSS** ⇒ vẫn **0 px** ⇒ CSS vô can, là thời gian giữa 2 lần chụp |
| **`/portal/order`** @1440 | **16 px, chênh tối đa 1/255** | control chụp 2 lần cùng trạng thái ra **0 px** ⇒ không phải nhiễu; bisect ra **`_components.css`**, tức rule `.wj-surface-headpad` tôi thêm. Kích thước trang và mọi toạ độ **y hệt** ⇒ **khử răng cưa góc bo đổi cách làm tròn, không xê dịch bố cục**. Ghi LIMIT 7 thay vì tuyên bố "0 pixel" |

## 8. Guard chứng minh bằng ĐỘT BIẾN — `scratchpad/d4e2_mutate.sh`

`-u` 5 module `--test-tags wujia_surface_card_d4` → **60 test** (mốc D4e1 là 52 ⇒ **+8 guard**).

| # | Đột biến | Test đỏ |
|---|---|---|
| 1 | trả `border-radius` vào rule họ (trong `@media`) | `test_rep_mcard_no_longer_declares_surface_shape` |
| 2 | rút nhầm đệm nội dung `__body` | `test_rep_mcard_content_rules_survive` |
| 3 | call site rơi mất lớp `--flush` | `test_rep_mcard_call_sites_carry_the_component` |
| 4 | `headpad` hardcode `14px` thay vì token | `test_headpad_class_uses_the_token` |
| 5 | inline padding sống lại ở `support` | `test_inline_padding_gone_from_both_views` |
| 6 | nhịp PC quay về `18` | `test_pc_card_head_rhythm_is_12` |
| 7 | override `.wj-exam-pc-dhead` sống lại | `test_exam_no_longer_overrides_the_rhythm` |
| 8 | `sumlist` lấy lại `margin-top` | `test_exam_sumlist_drops_margin_top_but_keeps_gap` |

**8/8 đỏ đúng chỗ.** Run đối chứng sau khi hoàn nguyên: **60 test, đúng 2 lỗi có sẵn**
(`TestSurfaceCardD4e1.test_all_metric_call_sites_use_the_component` và
`test_call_sites_bake_summary_and_flush`, cả hai vướng `wujia_portal_inspection.portal_inspection_detail`
vì module đang **`uninstalled`**) — **0 guard D4e2 đỏ**. Đã chứng minh 2 lỗi này có **trước**
D4e2 bằng run đối chứng riêng: quay về trạng thái D4e1, tạm gỡ lớp test mới ⇒ **đúng 2 lỗi ấy
trên 52 test**.

### Bẫy của chính vòng đột biến

- 🔴 `grep -qF "$4"` **nuốt chuỗi bắt đầu bằng `--`** như tuỳ chọn ⇒ đột biến 3 báo
  *"KHÔNG VÀO FILE"* oan. Phải viết `grep -qF -- "$4"`. Cùng họ với 2 bẫy đã ghi ở D4e1
  (regex trượt chữ số, XML sai cú pháp làm `-u` abort).
- 🔴 `nohup … &` báo **exit 0 ngay** trong khi script còn chạy — "xanh giả" quen thuộc.
  Phải chờ bằng `until ! pgrep -f …`.

## 9. Đặc hiệu CSS — quét toàn bộ 280 file CSS của `custom/`

Lần quét đầu báo 1 hit `.wj-pc-card__head { gap: 16px }`. **Đó là dương tính giả của chính bộ
quét tôi viết**: `__head` là con BEM — `gap` ở đây là khoảng cách *trong một hàng flex*, không
phải dáng khung; và dòng đó tôi không hề đụng. Sửa `FAMILIES` về đúng selector khung ⇒
**0 hit trên 280 file**. (Bài học D4d #10, dính lại một lần nữa ở dạng khác.)

## 10. RULE 1 + RULE 2 chạy lại

```
### debt-pay @ 1440x900 / 1920x1080 / 360x780 / 390x844
   - REDIRECT NGẦM -> /portal/debt?week=2026-W33&notice=no_due
### inspection @ 360x780
   - tràn ngang 11px
[m] chuẩn 16px ×62 · [pc] chuẩn 18px ×92 · [pc] chuẩn 20px ×2
TỔNG: 5 route/viewport có cờ · 0 nhóm cỡ chữ DRIFT chưa giải trình
```

**Y hệt baseline D4e2 ⇒ 0 cờ mới.** Hai cờ đều **truy được nguyên nhân, không đoán**:
4× `debt-pay` là redirect đúng thiết kế WJ-DEBT-007; `inspection` **404** vì
`wujia_portal_inspection` đang `uninstalled` (trang 404 của Odoo tràn 11px ở khổ 360).
Baseline D4e1 ghi 4 cờ / `18px ×94` là vì lượt đó **có cài** module inspection.

## 11. Đối chiếu `Kết quả mong muốn` (phần thuộc D4e2)

| Hạng mục BA | Kết quả |
|---|---|
| Dùng thống nhất CMP-SC-001 | ✅ 3/3 shell + 2 wrapper qua chủ sở hữu chung |
| Không thưa hơn sau migration | ✅ 8/9 trang **đặc hơn**; báo cáo mobile +6px = viền, **0 ô mất record** |
| Desktop radius 16 · gap 12 | ✅ nhịp header→body **12** trên toàn bộ 50 ô PC |
| Mobile radius 14 | ✅ `16 → 14` cả 3 thẻ |
| Border nhẹ, không shadow | ✅ `1px #E5E7EB`, `box-shadow: none` |
| Không lồng white card | ✅ 0 ô |
| Không tạo variant theo route | ✅ xoá 3 override exam + rule `.wj-rep-mcard` |
| Không còn style nội tuyến | ✅ 2/2 inline đã gỡ, geometry 0px |
| Test 1440 · 1024 · 992 · 390 · 360 | ✅ đủ 5 khổ, 50 ô |
| Nhịp header→body đồng nhất | ✅ `18/23/25` → **`12×50`**, chỉ chừa 2 ô `0` của R2 |

**10/10 hạng mục áp dụng được đạt ≈ 100%** (2 ô `0px` là lỗi cụm khác, đã ghi LIMIT).

## 12. LIMIT phải ghi vào ledger

1. **`.wujia-mdash-list` (11 call site) ngoài phạm vi** — inset `14` của nó vẫn tự khai;
   Đường A chỉ đổi chủ sở hữu của **wrapper header**, không đụng danh sách.
2. **8 ô exam sửa bằng cách XOÁ override**, không phải chỉnh số — đo lại xác nhận collapse ra
   đúng `12`, không phải `12+12`.
3. **2 ô `0px` ở `/portal/notification/41` giữ nguyên** — lỗi outline `h3`/`h2` thuộc cụm **R2**.
4. **Bug tz `/portal/reports/orders` KHÔNG sửa** — cụm **R3**
   (`wujia_portal_base/controllers/utils.py:38`), chỉ né trên DB copy.
5. **Chưa soi UAT.** Phải đo lại **chỉ-đọc** trên `http://113.161.187.126:8019/` sau deploy
   (L14/L10: UAT có `website`/`website_sale` nên bundle frontend khác local) rồi mới
   `qa_deploy_mark.py`.
6. **`.wj-surface-headpad` ở PC cho `20px`** (token `--wujia-surface-pad-regular`) trong khi
   inline cũ luôn `14px`. Hiện **không ảnh hưởng** vì cả 2 wrapper là markup chỉ-mobile
   (đo ra 0 phần tử ở 1440/1024/992) — nhưng nếu sau này bỏ `d-lg-none` thì sẽ thành 20.
7. **`/portal/order` @1440 lệch 16 pixel ở mức chênh 1/255** do thêm `.wj-surface-headpad`
   (khử răng cưa góc bo). **Không xê dịch bố cục** (kích thước trang + mọi toạ độ y hệt).
   Ghi lại thay vì tuyên bố "0 pixel".
8. **2 test đỏ có sẵn** vì `wujia_portal_inspection` đang `uninstalled` trên DB dev —
   không phải hồi quy của D4e2 (đã chứng minh bằng run đối chứng).
9. **D4e1 chưa commit** trên nhánh `dev/2026-09-05-d4c` — phải chốt chiến lược commit trước khi
   `/wujia-end-sprint` gộp nhầm hai lượt.
10. Tiến độ cụm **113/384 ≈ 29%** ⇒ issue **giữ `Ready for Dev`**. **Dev không tự đóng `Done`.**
