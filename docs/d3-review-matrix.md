# D3 REVIEW — soát lại TOÀN cụm `CMP-CH-001` bằng phép đo QUAN HỆ

Phiên 2026-09-04. **Không migrate thêm chỗ nào** (D3 vẫn 95/105, 4 chỗ chờ BA + các chỗ §3).
Ba việc: (A) soát vỡ giao diện toàn cụm · (B) vá 2 vùng D3f chưa từng chạy trên server thật ·
(C) dọn code + đo hiệu năng.

> **Vì sao phải có phiên này.** D3c (badge trôi 966px), D3d (mất nhịp 28px) và D3e (thẻ tóm tắt
> vỡ) **đều Pass sạch mọi bảng số** mà giao diện vẫn vỡ. Lý do: bảng số cũ chỉ hỏi *"giá trị này
> có đúng chuẩn không"*, **không bao giờ** hỏi *"nó có ăn khớp với các card khác cùng trang / các
> màn khác không"*. Phiên này đổi hẳn cách đo.

---

## 1. Cách đo — quan hệ thay cho hằng số

`scratchpad/d3_review.py` mở **31 route × 4 viewport (1920/1440/390/360) = 124 lượt đo**, thu về
**174 CardHeader** (162 cái mở đầu card). Mỗi phép thử so với **hàng xóm**, không so với hằng số:

| # | Kiểu vỡ đã có tiền lệ | Phép thử quan hệ |
|---|---|---|
| 1 | Trailing trôi khỏi lead (D3c) | `TRAIL_OVERFLOW` trailing vượt mép phải card · `TRAIL_PAD` lề phải lệch > 4px giữa các header **cùng trang** |
| 2 | Nhịp header→body không đều (D3d) | `RHYTHM` độ chênh `gap(header, body)` > 2px giữa các card **cùng trang** |
| 3 | Nhãn phụ ≥ tiêu đề card (RULE 1) | `HIERARCHY` header lồng có cỡ ≥ header mở đầu **của chính card đó** (gom theo `cardKey` duy nhất) |
| 4 | Mất màu ngữ nghĩa vì cascade (D3f) | `CONTRAST` tương phản chữ/nền tổ tiên < 4.5 (WCAG AA) |
| 5 | Lệch chuẩn giữa các MÀN (RULE 2) | `CROSS` histogram cỡ tiêu đề mở đầu card toàn portal, đối chiếu whitelist THIẾT KẾ |

Cộng thêm: redirect ngầm (vẫn trả 200 → "Pass rỗng" biến tướng), lỗi JS, tràn ngang, và đếm các
lớp giả-heading đã nghỉ hưu.

**Chỉ route bị khoanh cờ mới đáng chụp ảnh** — đó là chỗ tiết kiệm token mà vẫn chặt hơn cách cũ.

### Harness tự sai thì sửa harness, không sửa kết luận

Lượt quét đầu cho ~40 cờ, **phần lớn là dương tính giả của chính tôi**:

- `LEAD_STRETCH` bắn vào gần như mọi header, kể cả header **không có trailing** — đã thay hẳn bằng
  `TRAIL_OVERFLOW` + `TRAIL_PAD` mới thật sự là quan hệ.
- `HIERARCHY` gom nhầm hai card khác nhau vì nhóm theo **chuỗi className** — đã đổi sang `cardKey`
  duy nhất phát từ JS.
- `RHYTHM` đem header `--flush` (margin 0 là **chủ đích**) so với header thường — đã loại.
- `REDIRECT` bắn 12 cờ giả vì server local bật đa ngữ, URL có tiền tố `/vi` — đã chuẩn hoá.
- 🔴 Tôi từng **tự bịa** một dòng whitelist (`wj-exam-pc-sechead`) **không có nguồn trong inventory
  §6** — nó che mất đúng phát hiện chính của phiên. Đã bỏ. **Whitelist chỉ được chứa thứ chủ dự án
  đã chốt.**

---

## 2. Bảng soát — 31 route

Cột "Ảnh": `soi mắt` = đã chụp và nhìn · `0 cờ` = không chụp (đo quan hệ sạch, tiết kiệm token,
đúng chỉ đạo *"nếu ổn rồi thì thôi"*).

| Route | Header (1920/1440/390/360) | Kết quả | Ảnh |
|---|---|---|---|
| `/portal` | 4/4/1/1 | đạt | soi mắt (đối chứng mobile) |
| `/portal/order` · `/order/cart` · `/order/product/1` | 1/1/0/0 · 1/1/0/0 · 0 | đạt | 0 cờ |
| `/portal/purchase-history` | 1/1/0/0 | đạt | 0 cờ |
| `/portal/purchase-history/22` | 4/4/4/4 | đạt — **chỗ D3e từng vỡ**, badge "Đã xác nhận" bám sát mã `S00044`, không trôi | soi mắt (đối chứng) |
| `/portal/delivery` · `/delivery/3` | 0 · 4/4/0/0 | đạt | 0 cờ |
| `/portal/return` · `/return/new` · `/return/12` | 1 · 4 (m) · 4/4/4/4 | đạt | soi mắt (đối chứng) |
| `/portal/notification` · `/notification/40` | 1 · 3/3/1/1 | đạt (xem §6 ghi nhận ngoài phạm vi) | soi mắt (`--flush`) |
| `/portal/knowledge` · `/knowledge/ui12-01` | 2 · 1/1/2/2 | đạt | 0 cờ |
| `/portal/support` · `/support/new` · `/support/40` | 1 · 1 (m) · 3/3/1/1 | đạt | 0 cờ |
| `/portal/info-request` | 1/1/1/1 | đạt | 0 cờ |
| `/portal/exam` | 1/1/3/3 | đạt | 0 cờ |
| `/portal/exam/register` | 4/4/1/1 | **vỡ RULE 1 → đã sửa** (§3.1); còn 1 ghi nhận nhịp (§3.4) | soi mắt (sau sửa) |
| `/portal/exam/registration/22` | 2/2/1/1 | **vỡ RULE 1 → đã sửa** cùng rule với trên | 0 cờ sau sửa |
| `/portal/franchise-information` · `/franchises/1/profile` | 2/2/3/3 · 4/4/4/4 | đạt | 0 cờ |
| `/portal/reports/orders` | 0 | đạt (không có call site) | 0 cờ |
| `/portal/debt?week=…` · `/debt/payment-history` | 1 · 1 | đạt | soi mắt (đối chứng) |
| `/portal/debt/pay` | — | **redirect ngầm** `notice=no_due` — đúng hành vi WJ-DEBT-007, xem §4 | — |
| `/portal/inspection` | 0 | đạt — 1 lớp giả-heading còn sót là `inspection_list:34`, **chỗ chờ BA** (inventory §6.3) | 0 cờ |
| `/portal/inspection/detail/3` | 4/4/2/2 | **tương phản 3.74 → đã sửa** (§3.2); nhánh nghiêm trọng chữ TRẮNG trên nền ĐỎ đúng cả PC lẫn mobile | soi mắt (đối chứng) |
| `/portal/inspection/remediation/3` | 2/2/0/0 | đạt | 0 cờ |

**Sức khoẻ chung: 0 lỗi JS · 0 trang tràn ngang · 124/124 lượt đo trả về trang đúng** (trừ
`/portal/debt/pay` đã giải thích ở §4).

---

## 3. Phán quyết từng chỗ lệch — DRIFT hay THIẾT KẾ

### 3.1 Màn thi: nhãn khối con **bằng** tiêu đề card — DRIFT, đã hội tụ

Trong **cùng một card**, tiêu đề card và các nhãn khối con đều **18px** ⇒ mất hẳn một tầng phân cấp.

Truy được gốc trong CSS + git: trước D3d thang bậc là `.wj-pc-card__title` 22px → `.wj-exam-pc-sectitle`
20px → `--sm` 18px. **D3d hội tụ tiêu đề card 22→18 (đúng RULE 2) nhưng không hạ khối con theo**, nên
ba bậc sập thành một. `d3d-acceptance-matrix.md:60,63` ghi **Pass** cho cả hai số — vì mỗi số chỉ được
so với chuẩn, **không bao giờ so với nhau**. Đây đúng là điểm mù mà RULE 1 sinh ra để bịt.

Chủ dự án chốt: **khối con = 16px** (đã là cỡ chuẩn của component, không đẻ số mới).

```css
/* portal_exam.css — đặc hiệu (0,4,0) + !important: rule component là (0,3,0)!important,
   viết ngắn hơn là THUA (bẫy đặc hiệu đã trả giá 2 lần: D3e §7, D3f). */
.wj-exam-pc .wj-card-header.wj-exam-pc-sechead--sm .wj-card-header__title,
.wj-exam-pc .wj-card-header.wj-exam-pc-sechead--2  .wj-card-header__title,
.wj-exam-pc .wj-card-header.wj-exam-pc-slots__head .wj-card-header__title {
    font-size: 16px !important;
    line-height: 22px;
}
```

Ảnh sau sửa (`/portal/exam/register` @1920): "Thông tin đăng ký" 18px > "Chọn lịch thi" /
"Người tham gia" / "Khung giờ ngày" 16px — **thang bậc đọc được ngay từ xa**.

### 3.2 Khảo sát: head danh mục bản mobile chìm chữ — lỗi CÓ SẴN, chủ dự án chốt sửa luôn

`#0284c7` trên nền `#f1f5f9` chỉ đạt **3.74** (< AA 4.5). Đậm thêm một bậc **cùng hệ xanh nhận diện**
→ `#0369a1`, đo lại **5.42**. Chữ vẫn là "xanh danh mục" như thiết kế, không đổi cỡ, không đổi vai trò.

### 3.3 Nhãn phụ giữa thân card — THIẾT KẾ, nhưng gom về MỘT khai báo

`portal_return.css` (D3e) và `portal_inspection.css` (D3f) có **hai bản trùng tuyệt đối** cho **cùng
một vai trò**. Đã gom thành modifier dùng chung `wj-card-header--sublabel` ở `_components.css`;
màu riêng của từng module vẫn ở module đó. Đây chính là **"đồng bộ" ở tầng code**: sửa một chỗ là
sửa hết, phiên sau không phải nhớ có hai bản.

### 3.4 Màn Đăng ký thi: nhịp header→body 18 / 12 / 24 / 36px — **ghi nhận, CHƯA tự sửa**

CardHeader đóng góp `margin-bottom: 12px` **giống hệt nhau ở cả 4 card**; chênh lệch đến từ
`margin-top` của **phần tử thân đầu tiên** của từng card (`.wj-pc-field` 18px · `.wj-exam-pc-schedule`
9px · `.wj-exam-pc-slots__list` 12px · `.wj-exam-pc-sumlist` **36px**). Tức là nhịp của **thân card**,
không thuộc hợp đồng của `CMP-CH-001`.

Nghiêng về **DRIFT** (bốn card một trang, bốn nhịp khác nhau, không lý do hình học) ⇒ đề nghị hội tụ
`.wj-exam-pc-sumlist` 36 → 18px. **Không tự sửa** vì đây là spacing thân card của module khác cụm và
"không chắc thì hỏi" — xin chủ dự án chốt (§8, câu hỏi 6).

### 3.5 Đối chiếu NGANG toàn portal — bằng chứng chính của "đồng bộ"

162 tiêu đề **mở đầu card** trên mọi màn, mọi viewport:

| Nền tảng | Cỡ | Số chỗ | Phán quyết |
|---|---:|---:|---|
| PC | 18px | 90 | **chuẩn component** |
| PC | 20px | 2 | **chuẩn component** (biến thể regular — `purchase-history/<id>`) |
| PC | 15px | 4 | THIẾT KẾ — head danh mục khảo sát (đầu MỘT nhóm trong card) |
| Mobile | 16px | 62 | **chuẩn component** |
| Mobile | 13.3px (.95rem) | 4 | THIẾT KẾ — bản mobile của cùng head đó |

**0 nhóm cỡ chữ DRIFT chưa giải trình.** Mọi giá trị lệch chuẩn đều có nguồn dẫn trong
`d3-cardheader-inventory.md` §6.

---

## 4. Việc B — hai vùng D3f chưa từng chạy trên server thật

### 4.1 Hộp "Sau khi chuyển khoản" (`/portal/debt/pay`) — vẫn là LIMIT, và **không tạo hoá đơn**

Đọc thẳng dữ liệu UAT qua XML-RPC: cửa hàng HCM-01 (id 3) có 4 hoá đơn đã ghi sổ, trong đó
`INV/2026/00003` còn dư 1.15 ở W33 — **nhưng** `wujia.portal.debt.get_summary(3, '2026-W33')` trả
`state='credit'`, `remaining=-72448.85` vì giấy báo có `RINV/2026/00001` (72.450) bù trừ cả tuần.
Không tuần nào còn nợ ⇒ **redirect `notice=no_due` là ĐÚNG hành vi WJ-DEBT-007**, không phải lỗi.
(Ghi chú §5 bẫy 6 *"W33 = dư có"* nghĩa là **dư CÓ**, tức không còn nợ — tôi đọc nhầm ở lượt đầu.)

Không tạo `account.move` trên UAT (QA §10). Xác minh gián tiếp, đủ mạnh:
`arch_db` của `wujia_portal_debt.portal_debt_pay` trên UAT có **1×** `wj_card_header`, **1×**
`wj-debt-hint-head`, **0×** lớp `wj-debt-hint__title` đã nghỉ hưu; `portal_debt.css` phục vụ trên UAT
có đủ rule scope; **diff hợp nhất local ↔ UAT = 0 dòng** (lệch 764 byte chỉ do CRLF của server Windows).

⚠️ **LIMIT giữ nguyên: khối này chưa từng render bằng dữ liệu thật.**

### 4.2 Màn Khảo sát — đã seed demo trên UAT (đúng phạm vi được cho phép)

`scratchpad/d3_uat_seed.py` (bản XML-RPC của `d3f_seed.py`, thêm tham số `--franchise`).
**Chỉ dữ liệu khảo sát demo — không đơn hàng, không hoá đơn, không email.**

| Thứ đã tạo trên UAT | Định danh |
|---|---|
| Phiếu khảo sát | `KS/D3REVIEW/001` — **inspection id = 3** |
| Dòng chi tiết | id **1–6** (2 danh mục, 1 nghiêm trọng; có dòng đạt + không đạt) |
| Dòng chờ khắc phục | id **3** và **5** |
| Mẫu | `Mẫu D3 REVIEW (demo)` |
| Lịch giám sát | `ir.sequence` đổi tên khi tạo → thành `LGS-HCM-01-0001` |

**Lệnh xoá khi chủ dự án muốn dọn:**
```bash
cd scratchpad && python3 d3_uat_seed.py --franchise 3 --purge
```
(`--purge` xoá phiếu + mẫu; **lịch giám sát phải xoá tay** vì bị đổi tên, script chỉ cảnh báo.)

Kết quả soi ảnh trên UAT `@390`: nhánh danh mục **nghiêm trọng** ra **chữ trắng trên nền đỏ** (đúng),
nhánh thường ra xanh — và chính chỗ này làm lộ lỗi tương phản 3.74 ở §3.2.

---

## 5. Việc C — dọn code

### 5.1 Xoá CSS chết (inventory §7)

**17 lớp / 21 selector** đã xoá, mỗi lớp đều grep ra **0 call site** trong view + template + JS trước
khi cắt (biên từ `\.CLASS([^-_a-zA-Z0-9]|$)`):

`.wujia-content-card-header` (+ `-icon`, `-title`, `-link`, `-link:hover`, `-link i`, và biến thể
`--flush >`) · `.wujia-mhome .wujia-mhome-section-title` + `.wujia-mhome .wujia-mdash-title` ·
`.wujia-mdash-title` · `.wujia-mhist-card-head` · `.wujia-mknow-h` · `.wujia-maccount-store-name` ·
`.wj-pc-acct-staff__title` · `.wj-pc-order-head__code` (+ `__code-row`) · `.wj-pc-cart-title` ·
`.wj-pc-dlv-head-meta` · `.wujia-mexam-rsum-title` · `.wujia-mnoti-detail-sectitle` ·
`.wj-exam-pc-sectitle--2`.

**Semantic diff CSS** (`scratchpad/css_semdiff.py`, so theo *(ngữ cảnh @media, selector) → tập khai
báo*, không so dòng):

| So với | MẤT | THÊM | ĐỔI |
|---|---:|---:|---:|
| ảnh chụp trước khi xoá | **21 (đúng danh sách chủ đích)** | **0** | **0** |
| `git HEAD` | 23 (21 trên + 2 rule nhãn phụ chuyển về modifier chung) | 7 (4 modifier chung + 3 selector phân cấp exam) | 2 (màu tương phản + cỡ nhãn phụ dời đi) |

**Không xoá gì ngoài danh sách, không thêm gì ngoài chủ đích.**

### 5.2 Hai lần suýt xoá nhầm — ghi lại để phiên sau không lặp

1. **`wj-exam-pc-sectitle` CHƯA chết.** Áp Fix 3.1 tôi đã xoá rule 20px của nó, nhưng lớp này còn
   **1 call site sống** ở `portal_exam.xml:398` ("Người tham gia" — chỗ defer chờ BA). Kiểm lại thấy
   rule heading global chỉ phủ `h1`/`h2` còn phần tử là `h3` nên **chưa vỡ mắt thường** — vẫn khôi
   phục cả hai rule và ghi chú tại chỗ. **Danh sách xoá phải suy ra lại, không được kế thừa mù.**
2. **`.wujia-mhome .wujia-mdash-title` được nhắc NGUYÊN VĂN trong ledger** (`qa-issue-ledger.yaml:465`,
   UI-MOB-HOME-002, 18px/24/700). Đo trên UAT trước khi cắt: tiêu đề section Home nay render qua
   `wj-section-header__title` **20/28/700** theo `CMP-SH-001` (BA duyệt 11/08 — quyết định SAU và đè
   lên con số 18px cũ), còn CardHeader duy nhất ("Khung giờ đặt hàng") là 16px, **vẫn nhỏ hơn** tiêu
   đề section ⇒ **ý định của ledger vẫn được giữ**. Cả hai selector đã 0 call site nên rule là vô
   hiệu; xoá không đổi một pixel nào. Chú thích tại chỗ đã viết lại theo đúng sự thật này.

### 5.3 QWeb — gom lặp

- **Khối badge `ch_meta` 3 nhánh của khảo sát (PC + mobile): KHÔNG gom.** Hai bản khác nhau thật:
  13px vs 12px, mobile thêm `border-radius: 20px` + `padding: 4px 10px`, và nhánh `else` dùng hai lớp
  khác nhau (`wj-pc-badge--pending` vs `wj-detail-max-chip`). Gom lại phải tham số hoá 4 điểm khác
  biệt ⇒ **lãi không bù rủi ro**. Ghi nhận để D4 xử cùng lúc với SurfaceCard.
- **Điều kiện tính lại nhiều lần trong một template: đã sửa 1 chỗ.** `c_sum.get('is_severe')` được
  gọi **2 lần mỗi vòng lặp × 2 vòng (PC + mobile)** ⇒ đưa về `t-set _cs_sev` đúng một lần mỗi vòng,
  giống hệt lối `_sec_sev` của D3f. Không đổi một ký tự HTML nào ra ngoài.

### 5.4 `!important` — gốc rễ KHÔNG nằm ở component (đề xuất, **chờ duyệt**)

Component đặt `!important` lên `font-size` **chỉ để thắng hai rule GLOBAL**:

| Rule global | Vị trí | Phủ |
|---|---|---|
| `h2, .wujia-h2 { font-size: 24px !important }` | `_components.css:6` | **mọi** `<h2>` toàn portal |
| `.card .card-title, .card-header h4, .card-header h5 { … !important }` | `_components.css:8` | **mọi** `.card-header` toàn portal |

Sửa gốc = thu hẹp phạm vi hai rule này ⇒ component bỏ được `!important` ⇒ **95 call site khỏi phải
chống đỡ**. Nhưng blast radius là *toàn bộ* `<h2>` và *toàn bộ* `.card-header` của portal ⇒
**chỉ đề xuất, không tự làm** (đúng ràng buộc "đụng `wj_card_header.xml` / `_pc_components.css` phải
hỏi trước"). Cần một phiên riêng có lưới hồi quy đủ rộng.

### 5.5 Hiệu năng — đo, không khẳng định

A = DB `wujia_tea_d3f_a` (arch **trước** D3f) · B = DB `wujia_tea_d3f_b` (arch **sau**, đã nạp mọi
thay đổi của phiên này). Đếm query từ chính access log của Odoo, lấy **min của 3 lượt** sau 2 lượt
làm nóng.

| Route | query A | query B | Δ | ms A | ms B |
|---|---:|---:|---:|---:|---:|
| `/portal` | 41 | 41 | **0** | 33 | 31 |
| `/portal/debt?week=2026-W33` | 17 | 17 | **0** | 15 | 15 |
| `/portal/debt/payment-history` | 17 | 17 | **0** | 13 | 13 |
| `/portal/inspection` | 23 | 23 | **0** | 21 | 21 |
| `/portal/inspection/detail/<id>` | 25 | 25 | **0** | 25 | 23 |
| `/portal/exam` | 19 | 19 | **0** | 15 | 16 |
| `/portal/return/<id>` | 17 | 17 | **0** | 17 | 17 |

**7/7 route Δquery = 0**, thời gian render ngang nhau trong sai số. Đúng như dự đoán (D3 chỉ đụng
template + CSS) — nhưng giờ có **số đo**, không phải lời khẳng định.

---

## 6. Ghi nhận NGOÀI phạm vi D3 — không sửa trong phiên

1. **Nút "Quay lại" cắt chữ** ở `/portal/purchase-history/<id>` và `/portal/notification/<id>` —
   thuộc `CMP-BPH-001` (B4), không phải CardHeader.
2. **`/portal/notification/<id>`**: card trái có đường kẻ dưới header, card phải thì không —
   lệch nhỏ trong cùng một trang, thuộc quyết định `ch_divider` của từng call site.
3. **Thẻ tổng S43** khai `height: 142px` nhưng UAT ra 144px (dư có) / 138px (đã trả) vì nó là flex
   item trong cột cha co giãn. **Không phải do D3f** — phần D3f đo vẫn đúng 15px, và A/B cục bộ ra
   142 ở cả 5 biến thể. Nếu Figma S43 khoá cứng 142 thì **mở issue riêng**.

---

## 7. Test

`custom/wujia_portal_layout/tests/test_d3_card_header.py` → **thêm lớp `TestCardHeaderD3Review`**,
**không đẻ file mới**. Bộ `wujia_card_header_d3`: **0 failed / 52 test** (baseline D3f là 44).

Ba guard cũ phải cập nhật theo thay đổi của phiên (nhãn phụ chuyển sang modifier chung, chú thích
trỏ vào lớp đã xoá) — đã sửa **giữ nguyên quan hệ mà chúng bảo vệ**, không nới lỏng.

**Mutation cố ý 8 lần → mỗi lần guard tương ứng đỏ:**

| Phá hỏng | Test đỏ |
|---|---|
| modifier chung .875rem → .9rem | `test_sublabel_size_lives_in_one_shared_rule` |
| chép lại cỡ chữ vào CSS module (đẻ bản trùng) | `test_module_css_no_longer_redeclares_sublabel_size` |
| call site khảo sát rụng modifier chung | `test_sublabel_call_sites_carry_the_shared_modifier` (+ guard D3f cùng chỗ) |
| khối con exam trở lại 18px | `test_exam_nested_labels_step_down_from_the_card_title` |
| xoá rule `sectitle` còn call site sống | `test_exam_sectitle_rules_survive_because_a_call_site_is_still_live` |
| head danh mục mobile trở lại màu 3.74 | `test_mobile_category_head_meets_wcag_aa` |
| bỏ `t-set`, tính lại điều kiện trong vòng lặp | `test_category_severe_flag_computed_once_per_loop` |
| hồi sinh một lớp CSS đã xoá | `test_dead_card_header_classes_stay_deleted` |

Guard tương phản **tự tính tỉ số WCAG** chứ không so chuỗi màu — đổi sang màu khác mà vẫn tối thì
vẫn đỏ. Mọi guard dùng `assertRegex` khớp **cả khai báo** (bài học D3e §10: `assertIn` là guard giả).

> 🔴 **Bẫy mới của chính bộ mutation:** hàm thay chuỗi chạy `replace(..., 1)` — thay **lần xuất hiện
> đầu tiên**. Khi khôi phục màu `#0284c7`, nó vá nhầm `.active-tab-line` ở dòng 83 và bỏ quên dòng
> 760. Semantic diff bắt được ngay (`ĐỔI = 2` bất thường). **Đã khôi phục đúng cả hai dòng và diff
> về sạch.** Bài học: script mutation phải neo bằng chuỗi **duy nhất**, không dùng "lần đầu tiên".

---

## 8. Chờ chủ dự án / BA

**5 câu hỏi gộp một lượt gửi BA** (bám nguyên văn inventory §6, **không quyết lại**):

1. `portal_franchise_information.xml:40` + `:49` — `wj-pc-acct-headcard` có **HAI** vùng phải
   (`__chips` trạng thái cửa hàng, `__box` quyền xem) trong khi spec cho **tối đa MỘT** trailing.
   D3a tạm để cả hai **ngoài** CardHeader. BA muốn vùng nào là trailing chính thức?
2. `portal_exam.xml:375` `wj-exam-pc-parthead` — hai trailing: ô nhập "Ghi chú" + nút "Thêm người".
   **Cả hai đều là control tương tác**, không cái nào rõ ràng là "nội dung card". Chọn cái nào?
3. `portal_exam.xml:769` `wujia-mexam-person-head` — hai trailing (badge "Bắt buộc" + nút xoá), và
   node này còn bị `portal_exam_wizard.js` `cloneNode` làm khuôn dựng người mới ⇒ **rủi ro chết im
   lặng cao nhất cụm D3**. Có bắt buộc migrate không, hay giữ nguyên?
4. `portal_inspection_list_templates.xml:34` "Danh sách phiếu khảo sát" — cùng họ với hai chỗ BA đã
   tự chỉ đích danh là SectionHeader. Đây là CardHeader hay SectionHeader?
5. `portal_debt.xml:688` "THÔNG TIN CHUYỂN KHOẢN" — nhãn 11px trong `.wj-debt-bank` (`height:150px`
   cố định), hiện là `wj_section_header`. BA lại nêu đúng chỗ này trong `CMP-CH-001` (*"Debt summary
   dùng label 11px viết hoa"*) ⇒ **ứng viên số 1 để đổi sang CardHeader**. Xác nhận giúp.

**1 câu hỏi cho chủ dự án:**

6. `/portal/exam/register` — bốn card cùng trang có nhịp header→body 18 / 12 / 24 / **36**px, chênh
   lệch nằm ở `margin-top` của thân card chứ không ở CardHeader (§3.4). Hội tụ `.wj-exam-pc-sumlist`
   36 → 18px cho khớp card bên cạnh, hay giữ vì thẻ tóm tắt cần thoáng hơn?

---

## 9. LIMIT

1. ~~Chưa deploy UAT.~~ ✅ **GỠ 04/09** — commit `0d8366d` đã deploy, đo lại chỉ-đọc trên chính UAT
   (§13). LIMIT này đóng.
2. Hộp "Sau khi chuyển khoản" **chưa từng render bằng dữ liệu thật** (§4.1).
3. `UI-CARDHEADER-001` **vẫn chưa 100%** (95/105) ⇒ ledger giữ dạng **COMMENT**, **KHÔNG chạy
   `qa_sync.py`**.
4. Dữ liệu khảo sát demo **vẫn đang nằm trên UAT** — lệnh xoá ở §4.2.

## 10. Hồi quy sau khi xoá CSS

| Lưới | Kết quả |
|---|---|
| `scripts/ba_spec/b4_regression.py` (`CMP-BPH-001`) | **286/286 PASS** — 17 route × 2 breakpoint sạch, 5 trang ngoài matrix sạch, 6 chiều rộng trên route detail đúng 42×42 / 122×40 và header 52/64, `overflow` 0 |
| Tab-walk a11y (`scratchpad/d2_tabwalk.py`) | 317 điểm dừng · 313 có viền chỉ dấu · **12/12 route giữ nguyên thứ tự và viền** |
| Bộ test `wujia_card_header_d3` | **0 failed / 52** |
| Semantic diff CSS | MẤT đúng 21 selector chủ đích · THÊM 0 · ĐỔI 0 |
| Δquery 7 route D3 | **0** |

## 11. `UI-STATUSBADGE-001` (STT 128) — KHÔNG làm trong phiên này

BA đã mở dòng (`Ready for Dev`, Medium, `fit=Need Dev Confirm`) — nhưng đọc kỹ mô tả thì đây là
**chuẩn hoá cả component StatusBadge** (*"Dashboard và mobile đang dùng `wujia-badge`, một số danh
sách PC dùng `wj-pc-badge`"*), tức **một cụm cỡ D3**, không phải lỗi badge mờ mà tôi đã truy gốc.

Lỗi badge mờ vẫn là **tập con** của nó và đã sẵn sàng: `.state-badge` khai **sau** `.wujia-badge-*`
trong cùng `_components.css`, cùng đặc hiệu (0,1,0) nên nuốt màu ngữ nghĩa; sửa = bỏ
`badge state-badge`, dùng `wujia-badge` như chính dòng 243 cùng file, tại
`portal_return_detail.xml:18` + `portal_info_request_detail.xml:23`.

⇒ **Đề nghị tách phiên riêng** cho STT 128, bắt đầu bằng việc đọc cột `Kết quả mong muốn` của chính
dòng đó (fit=`Need Dev Confirm` nghĩa là BA còn chờ Dev xác nhận cách xử). Nhét đuôi phiên này vào
là đúng kiểu "làm hết một lượt" mà quy trình đã cấm.

## 12. Module đã bump

`wujia_portal_layout` 19.0.32.9.0 · `wujia_portal_exam` 19.0.5.10.0 · `wujia_portal_inspection`
19.0.1.3.0 · `wujia_portal_return` 19.0.2.11.0 · `wujia_portal_notification` 19.0.2.9.0 ·
`wujia_portal_delivery` 19.0.3.9.0 · `wujia_portal_sale` 19.0.4.15.0.

CSS đổi ⇒ `?v=` lên **1190** cho `_components.css`, `_pc_components.css`, `_pc_account.css`
(§9 gotcha #1).

---

## 13. Đo lại trên chính UAT sau deploy (04/09, commit `0d8366d`)

Mọi số ở §3/§5.5 là của DB clone. Đây là lượt đo **chỉ-đọc trên `113.161.187.126:8019`**, cùng harness,
cookie `wujia_active_franchise_id=3` (HCM-01). Id bản ghi do `discover()` scrape từ chính UAT — **khác id
local**, nên không tái dùng số cũ: `order=44 · batch=1 · ret=13 · noti=19 · ticket=16 · reg=4 · insp=3 ·
prod=3 · fr=3`.

### 13.1 Ba ngưỡng chủ dự án đặt

| Ngưỡng | Kết quả UAT |
|---|---|
| 0 cờ `HIERARCHY` | **0** ✅ |
| 0 cờ `CONTRAST` | **0** ✅ |
| 0 nhóm `DRIFT` chưa giải trình | **0** ✅ |

**124/124 lượt đo trả về trang đúng · 0 lỗi tải · 0 lỗi JS · 0 trang tràn ngang · 176 CardHeader.**

### 13.2 Bằng chứng deploy đã ăn — không phải "Pass rỗng"

Bài học D3c (tưởng đã deploy mà quên merge) nên phải chứng minh bằng **giá trị chỉ tồn tại sau khi sửa**,
không chỉ nhìn cờ sạch:

| Chỗ sửa | Trước (mã cũ) | Đo được trên UAT |
|---|---|---|
| §3.2 head danh mục khảo sát mobile | `#0284c7` → tương phản **3.74** | `rgb(3,105,161)` = `#0369a1` → **5.42** |
| §3.1 khối con màn thi | 18px, bằng tiêu đề card | **16px** dưới tiêu đề card 18px |

Nhánh nghiêm trọng vẫn **trắng trên đỏ**: `rgb(255,255,255)` trên `rgb(185,28,28)` = **6.47**, đúng cả
PC lẫn mobile. Head danh mục bản PC `#111827` trên `#f8fafc` = 16.96.

### 13.3 Sáu cờ còn lại — đều đã giải trình từ trước, không có cờ mới

- `debt-pay` × 4 viewport: **REDIRECT NGẦM** `notice=no_due` — đúng hành vi WJ-DEBT-007 (§4.1), HCM-01
  đang dư CÓ nên không tuần nào còn nợ.
- `exam-register` @1920 + @1440: **RHYTHM lệch 18px** giữa `'Thông tin đăng ký'`=18 và
  `'Tóm tắt đăng ký'`=36 — đúng chỗ §3.4 **cố ý chưa sửa**, đang chờ chủ dự án chốt câu hỏi 6.
  (Trên UAT chỉ lộ 2 card nên chênh lệch là 18px thay vì dải 18/12/24/36 của clone — cùng một gốc.)

### 13.4 Giả-heading còn sót: **2**, đều là chỗ đã biết

`/portal/inspection` @1920 và @1440, mỗi trang 1 — chính là `portal_inspection_list_templates.xml:34`
"Danh sách phiếu khảo sát", **chỗ chờ BA** (§8 câu 4). Bản mobile: 0. Không phải hồi quy.

### 13.5 Lệch số header UAT ↔ clone — do DỮ LIỆU, không do mã

`report-orders` 0→3 · `exam-register` mobile 1→3 · `notification-detail` 3→2 · `delivery` 4→0. UAT và
clone khác nhau về đơn/phiếu/thông báo đang tồn tại, mà số CardHeader phụ thuộc số khối có dữ liệu.
Đã kiểm chéo: mọi cỡ chữ ở §13.1 vẫn nằm trong nhóm chuẩn hoặc nhóm THIẾT KẾ có nguồn dẫn.
