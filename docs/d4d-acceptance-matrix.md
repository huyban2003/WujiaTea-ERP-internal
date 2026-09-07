# D4d — bảng nghiệm thu SurfaceCard lượt 3 (họ mobile + `wj-filter-card`)

**Ngày:** 2026-09-05 · **Nhánh:** `dev/2026-09-05-d4c` · **Spec:** `CMP-SC-001`,
`UI-SURFACECARD-001` (STT 127) · **Phạm vi:** 10 họ mobile = **50 call site / 18 file /
10 module**.

Đây là **lượt ĐẦU TIÊN dùng cột mobile của component**. Nhánh `@media (max-width: 991.98px)`
của `.wj-surface-card` viết từ D4b nhưng D4b/D4c đều là họ PC-only ⇒ coi như code mới.

---

## 0. Kiểm kê 51 ↔ 50 — giải trình trước khi sửa

Grep tĩnh ra **đúng 50** call site shell. Phần dư của các con số thô là **class con BEM**
(`wujia-mexam-card-top/-line/-badge`, `wujia-mexam-selcard-main/-meta/-badge`) — `mexam-card`
thô 10 lượt nhưng shell chỉ 1, `mexam-selcard` thô 8 nhưng shell chỉ 2.

Cộng lại **§4 của `d4-surfacecard-inventory.md`** (10 dòng họ): 30+7+4+2+2+1+1+1+1+1 = **50**.
Con số **51** chỉ xuất hiện ở bảng tóm tắt D4 (`next-session-clusters-D.md:529`) ⇒ **lỗi cộng
của bảng tóm tắt, không call site nào bị bỏ sót**.

### Nhưng luật "kiểm kê là SÀN" vẫn bắt được 26 lượt ngoài kiểm kê

Grep **từng token** (`--wujia-morder-radius`, `--wujia-morder-border`, `--wujia-morder-divider`,
`--wujia-border-soft`) ra **8 bề mặt trắng mobile không có chữ "card" trong tên**, đều khai đủ
nền + viền + bo góc + đệm ⇒ **shell thật** theo chính phép thử của inventory:

| Lớp | Lượt | Neo | Chủ hợp đồng thật |
|---|---:|---|---|
| `wj-empty-state--rich` | 15 | `_components.css:359` | **CMP-ES-001** (EmptyState) |
| `wj-empty-state--card` | 5 | `_components.css:344` | **CMP-ES-001** |
| `wujia-mknow-feat` | 1 | `_components.css:2335` | `UI-DATALIST-001` (STT 126) |
| `wujia-mknow-row` | 1 | `_components.css:2370` | `UI-DATALIST-001` |
| `wujia-mreturn-row` | 1 | `portal_return.css:33` | `UI-DATALIST-001` |
| `wujia-mdelivery-row` | 1 | `portal_delivery.css:49` | `UI-DATALIST-001` |
| `wujia-mhist-summary` | 1 | `_components.css:2030` | chưa có chủ |
| `wujia-mticket-reply` | 1 | `_components.css:2712` | chưa có chủ |

🔴 **Đính chính inventory §C**: dòng *"`wj-empty-state` (5 → CMP-ES-001) … **Không có CSS khai
nền + bo góc** ⇒ ngoài hợp đồng"* là **SAI** — cả `--card` lẫn `--rich` đều khai đủ. Số lượt
cũng sai: 5 là của `--card`, còn `--rich` thêm 15 nữa.

**Chốt của chủ dự án:** ghi bổ sung, **KHÔNG kéo vào D4d** — 20 lượt thuộc `CMP-ES-001`,
4 lượt là dòng danh sách thuộc `UI-DATALIST-001`, 2 lượt chưa có chủ thì xếp lịch sau.

## 1. Đã làm

| | |
|---|---|
| CSS rút dáng khung | `.wj-filter-card` · `.wujia-mres-card` · `.wujia-mhist-card` · `.wujia-mknow-card` · `.wujia-mdash-card` (`_components.css`) + `.wujia-mexam-card` · `.wujia-mexam-selcard` · `.wujia-mexam-cfcard` (`portal_exam.css`) · `.wujia-mnoti-detail-card` (`portal_notification.css`) · `.wujia-mdelivery-prodcard` (`portal_delivery.css`) |
| CSS gỡ hẳn | `.wj-filter-card > .wj-filter-chips { margin-top: -2px }` (bẫy #3) · `.wujia-mnoti .wujia-mknow-card { padding: 9px 12px }` (bẫy #4) · `.wujia-mknow-article { padding: 16px }` (kiểm kê bỏ sót) |
| CSS giữ nguyên có chủ đích | `.wujia-mres-card { max-width: 420px }` + `text-align` · `.wujia-mhist-card { margin-bottom: 14px }` · `.wujia-mdash-card { display/text-decoration/color }` + `a.wujia-mdash-card:hover` · `.wujia-mdelivery-prodcard { overflow: hidden }` · `.wujia-mdash-list { padding: 4px 14px }` · `.wujia-mexam-selcard { background: var(--wujia-surface-tonal) }` |
| Call site | **41/50** chuyển `t-call`; **9/50** giữ thẻ gốc và **thêm thẳng class chủ sở hữu** |
| Bỏ style inline | 2 chỗ `style="padding:0;"` → `sc_body="flush"` (bẫy #5) |
| `-u` | đúng **một lần**, 10 module, **RC=0, 0 ERROR** |
| Version | `wujia_portal_layout` 19.0.34.0.0 → **19.0.35.0.0** (module chỉ đổi XML: không bump) |

### 9 call site giữ thẻ gốc — nhiều gấp 4,5 lần dự đoán của prompt

Prompt D4d chỉ cảnh báo **2** ca (`<article>` và `<a>`). Thực tế **cả 7 `wj-filter-card` đều là
`<form method="get">`** (6 trong số đó không đi qua `t-call` được), cộng thêm màn kết quả mang
`role="status" aria-live="polite"` mà component không có chỗ nhận:

| File | Thẻ | Vì sao không thành `<div>` |
|---|---|---|
| `portal_support.xml` · `portal_history.xml` · `portal_notification.xml` · `portal_knowledge.xml` · `portal_return_list.xml` · `portal_delivery.xml` | `<form method="get">` ×6 | mất `<form>` là mất route lọc GET |
| `portal_knowledge.xml:349` | `<article>` | landmark a11y của trang bài viết |
| `portal_exam.xml:199` | `<a t-foreach>` | wholeCard — `<a>` **chính là** card, mất là mất link |
| `portal_order_result.xml:19` | `<div role="status" aria-live="polite">` | component không mang được `role`/`aria-live` |

> `portal_exam.xml:172` là `wj-filter-card` dạng `<div>` nên vẫn đi `t-call` — 7 filter-card
> chứ không phải 7 `<form>`.

### Vì sao `wj-filter-card` / `mexam-cfcard` / `mexam-selcard` nhận biến thể `--summary`

Ba họ này là họ **duy nhất** trong D4d có khai `gap` (10 · 14 · 12). Luật chung #8 chốt
**`gap` chỉ đặt ở biến thể xếp ngang `--summary`, cấm ở rule gốc** (cộng chồng với margin của
`wj_card_header` thành 24px — bài học D4b). Cho ba họ này đi qua `--summary` là cách **duy nhất**
lấy được `gap: var(--wujia-surface-gap)` = **8px** đúng số BA mà không phá luật.

### Vì sao `mexam-selcard` KHÔNG dùng `sc_tone="tonal"`

Kiểm kê đề xuất `--tonal`, nhưng biến thể đó **bỏ hẳn viền** (`border: 0`) vì nó dành cho vùng
phụ **lồng trong** card. `mexam-selcard` là card **cấp cao nhất** của bước 2/3, và BA vẫn đòi
viền 1px `#E5E7EB`. ⇒ dùng biến thể thường + giữ **đúng một** khai báo nền
`background: var(--wujia-surface-tonal)` ở `portal_exam.css` (cùng tiền lệ D4c giữ
`.wj-pc-acct-headcard__box`).

## 2. Bảng đo TRƯỚC → SAU (5 khổ × 19 route, `scratchpad/d4d_{before,after}.json`)

95 ô (19 route × 1440/1024/992/390/360) · **trả trang 95/95** · **0 lỗi JS** · **0 tràn ngang** ·
**225 bề mặt duyệt được** cả trước lẫn sau (0 ⇒ đo rỗng, không phải sạch).

Số BA cột mobile: **radius 14 · viền 1px `#E5E7EB` (`rgb(229,231,235)`) · shadow `none` ·
compact 12 · regular 14 · gap 8**.

| Họ | pad TRƯỚC | pad SAU | viền TRƯỚC | viền SAU | gap TRƯỚC → SAU |
|---|---|---|---|---|---|
| `wj-filter-card` | 12 | **12** ✅ | `238,242,245` | **`229,231,235`** ✅ | 10 → **8** ✅ |
| `wujia-mdash-card` | 14 | **12** ✅ | `229,231,235` ✅ | ✅ | — |
| `wujia-mdash-card` (flush) | 0 | **0** ✅ | ✅ | ✅ | — |
| `wujia-mdash-card` (`mdash-list`) | 4/14 | **4/14** ✅ giữ có chủ đích | ✅ | ✅ | — |
| `wujia-mhist-card` | 16 | **12** ✅ | ✅ | ✅ | — |
| `wujia-mknow-card` | 16 | **12** ✅ | ✅ | ✅ | — |
| `wujia-mnoti-detail-card` | 16 | **12** ✅ | ✅ | ✅ | — |
| `wujia-mexam-card` | 14/16 | **12** ✅ | `238,242,245` | **`229,231,235`** ✅ | — |
| `wujia-mexam-cfcard` | 16 | **12** ✅ | `238,242,245` | **`229,231,235`** ✅ | 14 → **8** ✅ |
| `wujia-mexam-selcard` | 14/16 | **12** ✅ | `238,242,245` | **`229,231,235`** ✅ | 12 → **8** ✅ |
| `wujia-mdelivery-prodcard` (flush) | 0 | **0** ✅ | ✅ | ✅ | — |
| `wujia-mres-card` (§6) | 20/16 | **14** ✅ regular | `238,242,245` | **`229,231,235`** ✅ | — |

**radius 14 và `box-shadow: none` đúng ở cả 12 dòng, trước lẫn sau.** `mexam-selcard` giữ nền
`rgb(248,250,252)` ✅. Ba họ đang lệch viền sang tông nhạt `#EEF2F5` nay đã về đúng tông mobile.

## 3. Sức khoẻ trang — acceptance BA #11 (không được thưa đi)

```
❗ ô GIẢM record trong viewport : 0
❗ ô đổi recordsTotal           : 0
   ô THẤP xuống (mật độ tốt lên): 14
   ô CAO lên                    : 0
   tổng record trong viewport   : 121 → 122
   tổng bề mặt duyệt            : 225 → 225
   vi phạm lồng thẻ trắng       : 0 → 0
```

**Không ô nào giảm record**, `recordsTotal` không đổi ở mọi ô ⇒ không mất dữ liệu render.
14/95 ô thấp xuống, **0 ô cao lên** ⇒ mật độ tốt lên đúng mục tiêu BA.

## 4. Không rò rỉ sang PC — hai phép độc lập

| Khổ | Bề mặt mobile NHÌN THẤY, trước | sau | |
|---|---:|---:|---|
| @992 | 0 | 0 | ✅ |
| @1024 | 0 | 0 | ✅ |
| @1440 | 0 | 0 | ✅ |

Cộng thêm phép mạnh hơn: **ảnh `/portal` @1440 khác nhau đúng 0 pixel** trước/sau
(`PIL.ImageChops` — `vùng khác = None`). Đây là bằng chứng ảnh, không chỉ bằng chứng số.

## 5. Nhịp header→body — đo TUYỆT ĐỐI (`d4d_rhythm.py`)

RULE 1/2 chỉ bắt *sự không đều giữa các card*, sai số đều tay lọt sạch (bài học D4b) ⇒ đo tuyệt đối.

```
trước: 0px ×16 · 6px ×2 · 8px ×40 · 10px ×8 · 12px ×4 · 241px ×8
sau  : 0px ×16 · 6px ×2 · 8px ×42 · 10px ×6 · 12px ×4 · 241px ×8
```

**56 khoá đo trùng khớp hoàn toàn giữa hai lần; đúng 2 ô đổi nhịp**, cả hai là
`/portal/return` @390 và @360, cặp `wj-filter-search → wj-filter-select`: **10px → 8px** —
**chính là `gap` BA yêu cầu**, không phải xê dịch ngoài ý muốn.

**Bẫy #3 được chứng minh bằng số tuyệt đối**: trước khi sửa, cặp `wj-filter-dates → wj-filter-chips`
đo **8px** trong khi mọi cặp anh em khác đo **10px** — đúng bằng `gap 10 − 2px` của
`margin-top: -2px`. Sau khi gap về 8 và gỡ `-2px`, **cả 5 cặp con đều đo đúng 8px**, không còn ô
nào 6px. Giữ `-2px` sẽ thành 6px và **RULE 1/2 vẫn xanh** — đây là ca sai số đều tay điển hình.

## 6. `wujia-mres-card` — đo được mà KHÔNG cần DB copy, KHÔNG tạo đơn

Chốt #1 đầu phiên là dựng DB copy `wujia_tea_d4d` + POST một đơn. **Không cần nữa**, và tốt hơn
vì không sinh dữ liệu:

- `/portal/order/rejected?reason=ORDER_TIME_CLOSED` là **route GET thuần**, chỉ qua `_store_gate`.
- `/portal/order/submitted/<id>` chỉ cần **một SO portal sẵn có** của franchise đang chọn — đơn
  `S00002` (`franchise_id = 1`, `state = sale`) đã thoả, đúng franchise của `anh.owner`.

`scratchpad/d4d_mres.py` (không tạo/sửa bản ghi nào — đúng giới hạn QA §10):

| Khổ | radius | viền | padding | shadow | rộng |
|---|---|---|---|---|---|
| @390 | 14 ✅ | 1px `229,231,235` ✅ | **14** ✅ regular | none ✅ | 356 |
| @360 | 14 ✅ | ✅ | **14** ✅ | ✅ | 326 |
| @1440 | 16 | 1px `238,242,245` | 20 | none | **420** — `max-width` còn sống ✅ |

⚠️ **Tác dụng phụ có chủ đích ở khổ PC**: màn này là màn *luồng mobile* nhưng mở được bằng URL
trên desktop. Trước D4d nó khai cứng `padding: 20px 16px` + `radius 14` ở **mọi** khổ; nay ≥992
nó nhận **đúng cột PC của BA** (r16 · pad 20 · `#EEF2F5`). Ngang 16 → 20 và bo 14 → 16 là **đi
đúng spec**, không phải rò rỉ.

## 7. Touch target ≥ 44×44 (BA)

`wholeCard` @390 và @360: **n=3 · cạnh nhỏ nhất = 109px** ✅ (BA đòi ≥44). Trước D4d `mexam-card`
đo 113 ⇒ giảm 4px do padding 14→12, **vẫn dư 65px** so với ngưỡng.

## 8. RULE 1 + RULE 2 chạy lại (bắt buộc `--portal-login anh.owner`)

```
TỔNG: 5 route/viewport có cờ · 0 nhóm cỡ chữ DRIFT chưa giải trình
```

Đúng **5 cờ có sẵn từ baseline D4c**, **0 cờ mới**:

| Cờ | Giải trình |
|---|---|
| `debt-pay` @1440/1920/390/360 — redirect ngầm `notice=no_due` | hết nợ trên `wujia_tea_19`, WJ-DEBT-007, có từ D4c |
| `inspection` @360 — tràn ngang 11px | module `uninstalled`, có từ D4c |

Cỡ tiêu đề mở đầu card: `[m] 16px ×62` · `[pc] 18px ×86` · `[pc] 20px ×2` — **0 drift**.

## 9. Ảnh trước–sau @390 và @360 (bài học D3e)

12 cặp ảnh, `scratchpad/shots_d4d_{before,after}/`. Chiều cao trang **giống hệt từng cặp**, khác
biệt pixel nằm **đúng trong vùng card**:

| Ảnh | px khác | vùng |
|---|---:|---|
| `portal_1440` | **0** | `None` — chứng minh không rò rỉ PC |
| `portal_390` / `portal_360` | 998 / 64 | dải chữ nhỏ |
| `portal_return_15_390` / `_360` | 64.076 / 60.866 | (16,241)–(374,854) |
| `portal_exam_390` | 38.644 | (16,277)–(374,735) |
| `portal_delivery_3_390` | 37.973 | (15,241)–(374,704) |
| `portal_knowledge_…_390` | 30.949 | (16,248)–(374,577) |
| `portal_purchase-history_390` | 27.475 | (17,228)–(373,703) |
| `portal_notification_390` · `portal_support_390/360` | ~950 | (16,228)–(374,334) |

Soi mắt `portal_return_15_390`: 6 card giữ nguyên bố cục, chữ và badge không trôi, dải nhấn trái
của card "Phản hồi của Ngô Gia" còn nguyên, **card đặc lại đúng 2px mỗi bên**.

## 10. Guard chứng minh bằng ĐỘT BIẾN (test xanh không chứng minh gì)

`TestSurfaceCardD4d` — **12 test, cộng bộ cũ = 45 test, 0 failed**.
`scratchpad/d4d_mutate.sh`: **1 run đối chứng xanh + 11/11 đột biến đỏ ĐÚNG test kỳ vọng**.

| Đột biến | Test phải đỏ | |
|---|---|---|
| trả `padding` về `.wj-filter-card` | `test_shared_mobile_families_no_longer_declare_shape` | ✅ |
| trả `border-radius` về `.wujia-mhist-card` | như trên | ✅ |
| trả `background` về `.wujia-mdelivery-prodcard` | `test_module_owned_families_no_longer_declare_shape` | ✅ |
| trả `gap: 12` về `.wujia-mexam-selcard` | `test_selcard_keeps_only_its_tonal_fill` | ✅ |
| gỡ nền tonal của `.wujia-mexam-selcard` | như trên | ✅ |
| trả lại `-2px` bù gap (**bẫy #3**) | `test_filter_chips_compensation_is_gone` | ✅ |
| trả lại override liên module (**bẫy #4**) | `test_notification_no_longer_overrides_knowledge_card` | ✅ |
| token compact mobile 12 → 16 | `test_mobile_tokens_match_ba` | ✅ |
| gỡ `max-width` của `.wujia-mres-card` | `test_non_shape_rules_survive` | ✅ |
| gỡ lớp chủ sở hữu khỏi `<article>` | `test_mobile_non_div_call_sites_carry_the_owner_class` | ✅ |
| trả lại `style` inline `padding:0` (**bẫy #5**) | `test_no_inline_padding_left_on_migrated_cards` | ✅ |

### Hai bài học từ chính vòng đột biến này

1. **Đột biến không áp được cũng báo "xanh"** — `sed` neo `^    --wujia-surface-pad-compact`
   trượt vì dòng thật thụt **8 dấu cách**, nên lần chạy đầu ghi "🔴 KHÔNG ĐỎ" *cho một guard hoàn
   toàn tốt*. Phải kiểm chứng đột biến **đã thực sự vào file** trước khi kết luận guard yếu.
2. **`--log-level` và `logfile` trong `odoo.conf` nuốt sạch stdout** — 3 lần chạy trước đó đọc
   ra "RC=0, 0 ERROR" trên một file log **rỗng**. Bằng chứng thật nằm ở
   `logs/<năm>/<tháng>/<ngày>.log`, và phải **cắt theo số dòng** trước mỗi lần chạy.
   Chính nhờ đọc đúng log mới lộ **4 test đỏ** (3 `xml_id` đoán sai + 1 khoá view sai) —
   ba lần "xanh" trước đó là **xanh giả**.

## 11. Đặc hiệu CSS — quét toàn bộ 280 file CSS của `custom/`

Không chỉ so với component: quét **mọi rule trong mọi bundle** còn khai
`background`/`border`/`border-radius`/`padding`/`box-shadow`/`gap` cho 10 họ.

| Kết quả | |
|---|---|
| Rule khai dáng khung ở **trạng thái nghỉ** cho 10 họ | **1** — `.wujia-mexam-selcard { background }`, giữ có chủ đích (§1) |
| Rule khớp theo **tên con BEM** (`-badge`, `-top`, `-line`) | 9 — không phải shell, không tính |
| Rule `:is(...)` ở `_interaction.css:85/109` | **`:hover`/`:active`** — phản hồi tương tác, không phải dáng nghỉ |

`:is()` lấy đặc hiệu của **đối số mạnh nhất** ⇒ ba danh sách này là **(0,3,0)** (vì chứa
`.wj-pc-page-btn:not(.is-active):not(.is-disabled)`), `:hover` đẩy lên (0,4,0) — **đúng lý do
Luật #1 bắt giữ lớp cũ ở call site**. Bỏ lớp cũ là hover/pressed của 41 thẻ bấm-cả-khối chết câm.
Chủ sở hữu `.wj-surface-card` là (0,1,0) và **không rule nghỉ nào cạnh tranh với nó**.

## 12. Đối chiếu `Kết quả mong muốn` (phần thuộc D4d)

| Yêu cầu BA | Kết quả |
|---|---|
| Mobile radius 14 | ✅ 12/12 lớp |
| Mobile compact padding 12 | ✅ 9 họ về đúng 12 |
| Mobile regular padding 14 | ✅ `wujia-mres-card` |
| Mobile gap 8 | ✅ 3 họ có `gap` (10/14/12 → 8) |
| Viền 1px `#E5E7EB` tông mobile | ✅ 4 họ đang lệch `#EEF2F5` đã về đúng |
| Không shadow mặc định | ✅ `none` ở mọi lớp, mọi khổ |
| Không khoá chiều cao | ✅ không họ nào khai `height`/`min-height` |
| Touch target ≥44×44 | ✅ đo 109px |
| Không lồng white card | ✅ 0 → 0 |
| **Không thưa hơn sau migration** | ✅ 14/95 ô thấp xuống, **0 ô mất record** |
| Test 1440 / 1024 / 992 / 390 / 360 | ✅ đủ 5 khổ |
| Desktop radius 16 / compact 16 / regular 20 / gap 12 | ⏭ đã nghiệm thu ở D4c |
| Slot title/badge/metadata của record | ⏭ dựng ở D4b |
| Màn Khảo sát | ⏭ BA ghi *provisional* |

**11/11 hạng mục áp dụng được = 100%**; 3 hạng mục còn lại không thuộc lượt này.

## 13. LIMIT phải ghi vào ledger

1. **Đo trên `wujia_tea_19` (dev), chưa soi UAT.** UAT `8019` chỉ đọc/nhìn được sau deploy.
2. `wujia-mres-card` ở khổ **≥992** đổi từ `pad 20/16 · r14` sang cột PC của BA `pad 20 · r16`
   (§6) — đúng spec nhưng là **thay đổi nhìn thấy được** trên desktop, cần BA xác nhận khi retest.
3. Hai card `flush` (`portal_franchise_information`, `portal_support_detail`) còn **inline
   `style="padding:14px 14px 0"`** ở wrapper con — **có từ trước D4d**, giữ để khớp inset 14 của
   `.wujia-mdash-list`. Hội tụ cả hai về 12 là việc của **D4e**, không sửa lẻ ở đây.
4. **26 lượt bề mặt trắng mobile ngoài kiểm kê** (§0) chưa xử lý — chủ dự án chốt ghi bổ sung,
   20 thuộc `CMP-ES-001`, 4 thuộc `UI-DATALIST-001`, 2 chưa có chủ.
5. Nhịp header→body PC **18/23/25** vẫn **để nguyên** (chốt #4) — mang sang lượt CardHeader/D4e.
6. Hội tụ token `--wujia-border` ↔ `--wujia-morder-border`, `--wujia-border-soft` ↔
   `--wujia-morder-divider` (cùng hex) **chưa làm** — phải hỏi trước.
7. Tiến độ cụm: **~98/384 lượt ≈ 26%** ⇒ issue **giữ `Ready for Dev`**, chưa handoff.
   **Dev không tự đóng `Done`.**
