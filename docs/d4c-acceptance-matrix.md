# D4c — bảng nghiệm thu SurfaceCard lượt 2

**Ngày:** 2026-09-05 · **Nhánh:** `dev/2026-09-05-d4c` · **Spec:** `CMP-SC-001`,
`UI-SURFACECARD-001` (STT 127) · **Phạm vi:** `wj-pc-card` (34) + `wj-pc-acct-headcard` (2)
= **36 call site / 20 file**, 8 modifier CSS, 1 biến thể mới (`--tonal`).

Đây là **lượt rủi ro cao nhất cụm D4**: `wj-pc-card` là shell chung của toàn bộ giao diện PC,
đổi **radius 18→16** và **padding 24→16** chạm mọi màn desktop.

---

## 1. Đã làm

| | |
|---|---|
| Token | `--wj-pc-card-radius` **18 → 16** (hội tụ về `--wujia-surface-radius`); thêm `--wujia-surface-tonal: #F8FAFC` + `--wujia-surface-tonal-radius: 12px` |
| Component | thêm **một** prop `sc_tone` (`tonal`) — nền D4b giữ nguyên |
| CSS mới | `.wj-surface-card--tonal` (nền tonal, **không viền, không bóng**, radius 12) |
| CSS rút dáng khung | `.wj-pc-card` · `.wj-pc-acct-headcard` · 7 modifier (`wj-debt-pc-card`, `wj-exam-pc-{card,dcard,fcard,sumcard}`, `wj-pc-order-card`, `wj-rep-pccard`) |
| CSS giữ nguyên có chủ đích | `.wj-debt-pc-paycard { max-width: 720px }` · `.wj-exam-pc-sumcard { align-self/sticky/top }` · `.wj-exam-pc-{cal,slots} { min-height: 310px }` + đệm riêng · `.wj-pc-acct-headcard__box` (#F8FAFC, mẫu tonal của BA) |
| Call site | **31/36** chuyển `t-call`; **5/36** giữ thẻ gốc `<form>`/`<aside>`/`<section>` và **thêm thẳng class `.wj-surface-card`** (QWeb Odoo 19 không có directive đổi tên thẻ — `ir_qweb.py:1705`, đã chốt ở C8) |
| Lồng thẻ trắng | `.wj-exam-pc-cal` + `.wj-exam-pc-slots` → `--flush --tonal` |
| `-u` | đúng **một lần**, 10 module, **RC=0, 0 ERROR** |
| Version | `wujia_portal_layout` 19.0.33.0.0 → **19.0.34.0.0** (module chỉ đổi XML: không bump) |

**5 call site giữ thẻ gốc** — quyết định của chủ dự án (giữ route POST và landmark a11y):

| File | Thẻ | Vì sao không thành `<div>` |
|---|---|---|
| `wujia_portal_support/views/portal_support.xml:236` | `<form method="post">` | mất `<form>` là mất route gửi phiếu |
| `wujia_portal_exam/views/portal_exam.xml:448` | `<aside>` | landmark phụ của trang đăng ký |
| `wujia_portal_report/views/portal_report_orders.xml` 244/264/294 | `<section>` ×3 | landmark của 3 khối báo cáo |

## 2. Số đo bề mặt trước–sau (`getComputedStyle`, 19 route × 5 khổ)

| Lớp | Khổ | TRƯỚC | SAU |
|---|---|---|---|
| `wj-pc-card` | 1440 | r18 · p24 | **r16 · p16** |
| `wj-pc-card` | 390 | r18 · p24 | **r14 · p12** |
| `wj-pc-acct-headcard` | 1440 | r18 · p22/24 | **r16 · p20** (regular) |
| `wj-debt-pc-card` | 1440 | r18 · p22/24 | **r16 · p16** |
| `wj-exam-pc-card` | 1440 | r18 · p22/24/24/24 | **r16 · p16** |
| `wj-exam-pc-dcard` | 1440 | r18 · p20/24/24/24 | **r16 · p16** |
| `wj-exam-pc-fcard` | 1440 | r18 · p18/24/10/24 | **r16 · p16** |
| `wj-exam-pc-sumcard` | 1440 | r18 · p18/24/24/24 | **r16 · p16** |
| `wj-pc-order-card` | 1440 | r18 · p20/24 | **r16 · p16** |
| `wj-rep-pccard` | 1440 | r18 · p0 | **r16 · p0** (`--flush`) |

**4 bề mặt NGOÀI họ** cùng ăn token radius (chốt #2 của chủ dự án) — chỉ hội tụ bo góc,
**giữ nguyên đệm riêng**, đúng ý đồ:

| Lớp | TRƯỚC | SAU |
|---|---|---|
| `wj-pc-acct-nav` | r18 · p18 | **r16** · p18 |
| `wj-pc-empty` | r18 · p40/24 | **r16** · p40/24 |
| `wj-pc-order-head` | r18 · p22/24 | **r16** · p22/24 |
| `wj-pc-cart` | r18 · p20/22 | **r16** · p20/22 |

Đối chiếu cột `Kết quả mong muốn` của BA: desktop **radius 16 ✅ · compact 16 ✅ · regular 20 ✅**;
mobile **radius 14 ✅ · compact 12 ✅**; **viền nhẹ 1px `rgb(238,242,245)` ✅ · shadow `none` ✅**.

## 3. Sức khoẻ trang — acceptance BA #11

95/95 ô trả trang · **185 bề mặt duyệt được cả trước lẫn sau** (0 ⇒ đo rỗng, không phải sạch) ·
**0 lỗi JS** · **0 tràn ngang** · 0 redirect ngầm ngoài dự kiến.

- **Không ô nào giảm số record trong viewport.** Tổng 116 → **118** (+2, dày hơn).
- `recordsTotal` **không đổi** ở mọi ô (280 → 280) — không mất dữ liệu render.
- **26/95 ô GIẢM chiều cao trang**, không ô nào tăng ⇒ mật độ tốt lên đúng mục tiêu BA.
- **Vi phạm lồng thẻ trắng: 6 → 0.**

## 4. Nhịp header→body — đo TUYỆT ĐỐI (câu hỏi §3.4 chờ chủ dự án quyết)

RULE 1/RULE 2 đo *sự không đều giữa các card* nên sai số **đều tay** lọt qua sạch (bài học D4b).
Vì vậy D4c đo tuyệt đối: **histogram giống hệt trước và sau** — D4c **không** làm xê dịch nhịp.

```
0px ×2 · 12px ×32 · 18px ×14 · 23px ×2 · 25px ×2
```

Truy nguyên đầy đủ 5 giá trị (đây là **số thật để chủ dự án quyết**, Dev không tự sửa):

| Nhịp | Số ô | Nguồn | Màn |
|---|---|---|---|
| **12px** | 32 | `wj-card-header` đã migrate CMP-CH-001 (`margin-bottom: 12`) | đa số |
| **18px** | 10 | `.wj-pc-card__head { margin-bottom: 18px }` — **chưa** migrate CardHeader | profile, change-password ×3, delivery |
| **18px** | 4 | header 12 **collapse** với body `margin-top: 18` (`.wj-exam-pc-fcard .wj-exam-pc-field` `:994`, `.wj-exam-pc-sumlist` `:1417`) | exam/register |
| **23px** | 2 | `.wj-exam-pc-dhead { margin-bottom: 23px }` `:827` | exam/registration/14 |
| **25px** | 2 | `.wj-exam-pc-card__head { margin-bottom: 25px }` `:769` | /portal/exam |
| **0px** | 2 | không khai nhịp | notification/41 |

**Đính chính `d3-review-matrix.md` §3.4:** con số **36px** ghi cho `.wj-exam-pc-sumlist` không còn
đúng — CSS hiện tại là `margin-top: 18px`, và **hai** card của `/portal/exam/register` đo **18px
bằng nhau**, không lệch. Việc cần quyết là *có kéo 18/23/25 về 12 hay không*, chứ không phải sửa
một chỗ lệch.

## 5. Chạy lại bảng đo C3 màn Công nợ (chốt #4)

`scratchpad/d4c_c3_recheck.py` — 6 khổ (360/391/430/500/768/1440), `anh.owner` trên `wujia_tea_19`.

| Cam kết C3 | Đo lại 05/09 | |
|---|---|---|
| WJ-DEBT-009 · padding ngang 16 (mobile, 4 khổ) | **16** | ✅ |
| WJ-DEBT-009 · filter → banner 12 | **12** | ✅ |
| WJ-DEBT-008 · không còn `.wj-debt-qr` / `.wj-debt-pc-qr` / chữ QR | **0 / 0 / không có** | ✅ |
| WJ-DEBT-003 · không tràn ngang 6 khổ | **0** ở cả 6 | ✅ |
| WJ-DEBT-003 · `<992` chỉ khối mobile, `≥992` chỉ khối PC | `pc=none/m=flex` ↔ `pc=block/m=none` | ✅ |
| Hồi quy 5 trang × 2 khổ, 0 lỗi JS | **10/10 overflowX=0 · 0 lỗi JS** | ✅ |
| Chốt C2 · `/pay` hết nợ vẫn 302 `notice=no_due` | `?week=2026-W36&notice=no_due` | ✅ |
| `.wj-debt-pc-card` (thứ D4c đổi) | r18 p22/24 → **r16 p16**, nền trắng giữ nguyên | ✅ |

**Delta thật cần ghi:** nhịp *banner → tiêu đề* đo **28px**, bảng C3 gốc (15/08) ghi **24px**.
**Không phải do D4c** — diff của `wujia_portal_debt` ở lượt này **chỉ chạm phần PC**
(1 dòng CSS `.wj-debt-pc-card` + 3 call site XML); phần mobile không đổi một ký tự. Chênh lệch
đến từ cụm **D3b** (`f3a9d06`/`0d8366d`) khi `wj_section_header` được dựng thành component.
Ghi lại để chủ dự án biết, không tự sửa trong lượt này.

**Không đo được (LIMIT, đã biết trước):** các dòng của `/portal/debt/pay` và “giữa các giao dịch /
danh sách → Tổng cộng” — `wujia_tea_19` hết nợ ⇒ `/pay` redirect `no_due` (WJ-DEBT-007) và kỳ
hiện tại chưa có giao dịch đã xác nhận. Đây là **giới hạn dữ liệu**, không phải lỗi màn hình.

## 6. 6 call site trước đây KHÔNG đo được ở local — nay đã đo

DB copy cô lập **`wujia_tea_d4c`** (clone `wujia_tea_19`), cổng **8074** — không đụng
`wujia_tea_19`/8019/8070/8071.

- `-i wujia_portal_inspection` → **RC=0, 0 ERROR** (module đang `uninstalled` trên DB chính).
- Seed 1 phiếu khảo sát `need_remediation` + 1 tiêu chí `fail` để mở được 2 route chi tiết.
- Đổi tz `anh.owner` `Asia/Saigon → Asia/Ho_Chi_Minh` **trên bản copy** ⇒ `/portal/reports/orders`
  trả **200**. Chỉ sửa **dữ liệu**, **không** đụng code lỗi tz của cụm R3.

| Route | HTTP | Lớp đo được | r / pad @1440 |
|---|---|---|---|
| `/portal/inspection` | 200 | `wj-surface-card --section --compact --padded wj-pc-card` | **16 / 16** |
| `/portal/inspection/detail/1` | 200 | `… wj-pc-card mb-4` | **16 / 16** |
| `/portal/inspection/remediation/2` | 200 | `… wj-pc-card` | **16 / 16** |
| `/portal/reports/orders` (chart) | 200 | `… --flush wj-pc-card wj-rep-pccard--chart` | **16 / 0** |
| `/portal/reports/orders` (state) | 200 | `… --flush … --state` | **16 / 0** |
| `/portal/reports/orders` (top) | 200 | `… --flush … --top` | **16 / 0** |

5 khổ, **0 lỗi JS, 0 tràn ngang**; `<992` ẩn đúng khối PC. Vẫn nên soi lại trên UAT sau deploy.

## 7. RULE 1 / RULE 2 (`d3_review.py --portal-login anh.owner`)

**Giống hệt baseline**: 5 cờ có sẵn từ trước (4× `debt-pay` redirect `no_due`, `inspection@360`
tràn 11px), **0 DRIFT không giải trình được**, histogram `[m]16×62 · [pc]18×86 · [pc]20×2`.
⚠️ `--portal-login` là **bắt buộc**: mặc định `None` rơi về `admin` ⇒ 0 bề mặt mà vẫn “chạy xong”.

## 8. Test + chứng minh bằng đột biến

`custom/wujia_portal_layout/tests/test_d4_surface_card.py`, tag `wujia_surface_card_d4`:
**33 test — 0 failed / 0 error** (22 của D4b + 11 mới của D4c, **không đẻ file test song song**).

`scratchpad/d4c_mutate.sh` — **10/10 đột biến đỏ đúng chỗ**, kèm run đối chứng không đột biến:

| Đột biến | Test đỏ |
|---|---|
| trả `padding` về `.wj-pc-card` | `test_pc_card_no_longer_declares_surface_shape` |
| trả `padding` về `.wj-pc-acct-headcard` | `test_acct_headcard_keeps_layout_but_drops_shape` |
| trả `padding` về `.wj-exam-pc-sumcard` | `test_modifiers_no_longer_declare_padding` (subTest) |
| gỡ `max-width` khỏi `.wj-debt-pc-paycard` | `test_paycard_keeps_its_non_shape_rule` |
| token radius PC về 18px | `test_pc_card_radius_token_converged_to_sixteen` |
| gỡ token `--wujia-surface-tonal` | `test_tonal_tokens_exist` |
| khoá `sc_tone` không sinh `--tonal` | `test_tone_tonal_adds_the_modifier` |
| cho `--tonal` có viền | `test_tonal_variant_has_no_border_and_no_shadow` |
| trả nền trắng cho panel lồng exam | `test_nested_exam_panels_no_longer_paint_white` |
| gỡ class chủ sở hữu khỏi `<form>` support | `test_non_div_call_sites_carry_the_owner_class` |

⚠️ Bộ dò phải bắt `FAIL: (Subtest )?Lop.test` — thiếu chữ `Subtest` báo guard rỗng oan (dính ở D4b).
Log **cắt theo số dòng trước mỗi lần chạy**, không `tail` cả ngày.

**Một guard sai đã tự bắt được:** `test_modifiers_no_longer_declare_padding` đỏ vì so **chuỗi con**
— `top: var(--wj-pc-content-padding)` chứa chữ “padding” mà không hề khai `padding`. Sửa **test**
(thêm regex `(?:^|;)\s*padding\s*:`), **không** sửa code.

## 9. Đặc hiệu CSS

Rule mới `.wj-surface-card--tonal` = **(0,1,0)**, không nằm trong `@media`. Rà toàn bundle: sau khi
rút dáng khung, **không còn** rule nào của module khác khai `background`/`border`/`border-radius`/
`padding` cho 9 lớp đã migrate ⇒ không có bẫy “cùng đặc hiệu, thắng theo thứ tự nguồn”. Các rule
còn lại của `portal_exam.css` (`padding: 16px 12px 18px 22px`, `16px 22px 14px`) **cố ý** thắng
`--flush` (`padding: 0`) — đó là đệm riêng của panel, có chủ đích, đo lại đúng như thiết kế.
Đã **không** dùng `:not()` (bẫy đặc hiệu đã tái xuất 2 lần ở D3): bản nháp đầu viết
`.wj-surface-card:not(.wj-surface-card--tonal)` = (0,2,0), đã hoàn nguyên về (0,1,0) vì `--tonal`
đã `border: 0` nên `border-color` là vô nghĩa.

## 10. Ảnh trước–sau

`scratchpad/shots_d4c_{before,after}/` — 12 ảnh: `/portal/exam/register` @1440 **và** @390
(bắt buộc), `/portal/debt`, `/portal/profile`, `/portal/purchase-history/22`,
`/portal/change-password`, `/portal/franchise-information`, `/portal/order`, `/portal/delivery/3`.
Soi mắt `/portal/exam/register@1440`: bố cục nguyên vẹn, **nền tonal làm ô ngày trong lịch dễ đọc
hơn hẳn** so với thẻ trắng lồng thẻ trắng.

## 11. Đối chiếu `Kết quả mong muốn` (phần thuộc D4c)

| Yêu cầu BA | Kết quả |
|---|---|
| Desktop radius 16 | ✅ đo 16 ở toàn bộ 13 lớp |
| Desktop compact padding 16 | ✅ |
| Desktop regular padding 20 | ✅ (`wj-pc-acct-headcard`) |
| Mobile radius 14 / compact 12 | ✅ |
| Viền nhẹ, không shadow mặc định | ✅ 1px `rgb(238,242,245)` · `none` |
| **Không lồng white card** | ✅ 6 → 0 |
| **Không thưa hơn sau migration** | ✅ 26/95 ô thấp xuống, 0 ô mất record |
| Test 1440 / 1024 / 992 / 390 / 360 | ✅ đủ 5 khổ |
| Desktop gap 12 | ⏭ chỉ áp cho biến thể `--summary` (Luật #8) — D4c không dùng |
| Mobile regular 14 / gap 8 | ⏭ họ D4c là PC-only |
| Slot title/badge/metadata của record | ⏭ đã dựng ở D4b, D4c không đụng |
| Màn Khảo sát nghiệm thu field mapping | ⏭ BA ghi *provisional*, chờ seed data |

**8/8 hạng mục áp dụng được = 100%**; 4 hạng mục còn lại không thuộc phạm vi lượt này.

## 12. LIMIT phải ghi vào ledger

1. `/portal/debt/pay` không đo được trên `wujia_tea_19` (hết nợ ⇒ redirect `no_due`, WJ-DEBT-007)
   ⇒ `wj-debt-pc-paycard` chỉ chứng minh bằng test tĩnh + đọc CSS, chưa có số đo runtime.
2. 6 call site inspection/report đã đo trên **DB copy** `wujia_tea_d4c` — **vẫn nên soi lại UAT**
   sau deploy (inspection đang `uninstalled` trên DB chính; `/portal/reports/orders` vẫn 500 với
   tz `Asia/Saigon` — lỗi có sẵn của cụm R3, D4c **không** sửa).
3. `.wj-debt-summary { height: 142px }` giữ nguyên — **THIẾT KẾ S43**, ngoài phạm vi.
4. Nhịp *banner → tiêu đề* màn Công nợ 24 → 28px: đến từ **D3b**, không phải D4c (§5).
5. Câu hỏi nhịp §3.4 (18/23/25 có kéo về 12 không) **chờ chủ dự án quyết** — Dev đã trình số thật.
6. Tiến độ cụm: **~48/384 lượt ≈ 12%** ⇒ issue **giữ `Ready for Dev`**, chưa handoff.
