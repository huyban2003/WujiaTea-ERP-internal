# D4 — Kiểm kê & phân loại SurfaceCard (`UI-SURFACECARD-001`, STT 127)

**Ngày:** 2026-09-04 · **Cơ sở:** `c9073c7` · **Spec:** `CMP-SC-001`, tab `UI Component`
gid `488333015`, dòng 34 · **Phiên:** D4a — kiểm kê, **0 dòng code**.

Bước 1 của cụm D4. Đây là cụm **to nhất từ trước tới nay**: 442 lượt dùng / 67 họ class, gấp
hơn bốn lần D3 (105 chỗ, 6 phiên + 1 phiên review). Và **nguy hiểm hơn D3** — D3 chỉ đổi cỡ chữ
*bên trong* thẻ, D4 đổi **chính cái khung**: mọi trang sẽ đổi chiều cao thật, và padding khung
đổi thì **nhịp header→body 12px mà D3 vừa hội tụ cũng đổi theo**.

---

## 1. Phép thử phân loại — và nó KHÁC D3 ở đâu

C8/D3 hỏi *"tổ tiên của chỗ này có phải card không"*. **D4 không dùng lại được nguyên xi**, vì
lần này **chính cái card là đối tượng**, không phải tổ tiên của đối tượng. Chân lý vẫn là
**CSS đã khai gì**, không phải tên class.

> **Phép thử D4.** Một class **LÀ SurfaceCard** khi CSS khai cho nó, ở tầng rule **dáng mặc
> định** (không `:hover`/`:active`, không selector có tổ tiên):
> **`background`/`background-color` không trong suốt** **+** **`border-radius`**.

**Ba khác biệt cố ý so với D3, mỗi cái sinh ra từ một ca thật:**

| Điều kiện | D3 (C8) | D4 | Vì sao đổi |
|---|---|---|---|
| `padding` | **bắt buộc** | **bỏ** | BA cho `bodyMode: flushBody` ⇒ card padding 0 vẫn là card. Ca thật: `.wj-rep-pccard { padding: 0 }` |
| `border`/`box-shadow` | bắt buộc | **thành SỐ ĐO, không phải điều kiện** | BA viết thẳng *"border/shadow không thống nhất"*. Lấy nó làm điều kiện là **tự loại đúng những ca lệch cần tìm**. Ca thật: `.wj-rep-mcard` có nền + bo góc mà **KHÔNG viền** (16 lượt) |
| Tầng rule | gộp mọi rule | **tách 3 tầng**: dáng mặc định / `@media max-width` / trạng thái | xem bẫy harness §8 |

### Phép thử này bắt và bỏ sót ca nào

**Bắt được mà D3 sẽ bỏ sót:** `wj-rep-pccard` (padding 0) · `wj-rep-mcard` (không viền) —
đúng 27 lượt của cụm báo cáo.

**Bỏ sót — và đó là lý do phải có §3:** hộp trắng dựng bằng utility Bootstrap không có class
riêng; và **lồng nhau qua biên `t-call`** (thẻ ngoài và thẻ trong ở hai file khác nhau).
Quét tĩnh **không thể** thấy hai thứ này ⇒ §3 đo lúc chạy.

## 2. Phạm vi

`custom/wujia_portal_*/views|templates/*.xml` + `wujia_franchise` (trang khảo sát). Loại trừ
trước khi phân loại:

| Loại trừ | Lý do |
|---|---|
| `*_backend_views.xml` | Backend Odoo, không phải portal |
| `wj_ks_dashboard_ninja` · `wj_ks_dn_advance` | Workstream Dashboard riêng |
| `wujia_portal_remediation` | Code đã xoá (`f789a56`), UAT `uninstalled` — **không `-u`, không `-i`** |
| `portal_templates.xml` · `portal_franchises_in_layout.xml` | Route legacy `/my/franchises`, ADR-004 đã thay bằng portal Vuexy. **Kế thừa nguyên D3 §3** |
| `pc_preview.xml` | Trang demo nội bộ |

**Dương tính giả theo TÊN** (có chữ "card" nhưng không phải bề mặt card): `icon-credit-card`
(tên icon) · `wj-card-header` (**component D3 vừa dựng** — là nội dung *của* card) ·
`oe_kanban_card` (kanban backend).

### Đối chiếu con số

| | Lượt | Họ |
|---|---:|---:|
| Quét thô toàn bộ `class="…"` chứa "card" | **442** | **69** |
| − 3 file loại trừ §2 · − 3 họ dương tính giả | −58 | −4 |
| **= trong phạm vi kiểm kê** | **384** | **65** |

> ⚠️ **Đừng cộng cột "lượt" của bảng §4 để suy ra việc còn lại.** D3 cộng dư **ba phiên liên
> tiếp**. Luôn chạy lại `scratchpad/d4_inventory.py`.

## 3. Độ lồng — chiều đo MỚI, đo LÚC CHẠY

BA cấm **thẻ trắng lồng trong thẻ trắng**; vùng phụ phải dùng nền tonal `#F8FAFC` radius 12.

**Quét tĩnh ra 2 ca** (`forgot_pass.xml:21`, `portal_order_product_detail.xml:90`, đều
`card` trong `card`) — và **con số đó là SÀN, không phải TRẦN**, vì lồng thật xảy ra qua
`t-call` và qua hộp trắng không mang chữ "card" trong tên.

**Đo lúc chạy** (`scratchpad/d4_nesting.py`, Playwright đọc-chỉ, user `anh.owner`,
19 route × 2 khổ 1440/390 = **38 lượt, 38/38 trả trang, 124 bề mặt duyệt, 0 lỗi JS,
0 tràn ngang**):

### 🔴 2 vi phạm thật — **cả hai quét tĩnh KHÔNG thấy**

| Chỗ | Trong | Route |
|---|---|---|
| `.wj-exam-pc-cal` (lịch chọn ngày thi) | `.wj-pc-card.wj-exam-pc-fcard` | `/portal/exam/register` @1440 |
| `.wj-exam-pc-slots` (khung giờ) | `.wj-pc-card.wj-exam-pc-fcard` | `/portal/exam/register` @1440 |

⇒ **`/portal/exam/register` là chỗ PHẢI CHỤP ẢNH** ở lượt D4c. Đáng chú ý: đây **đúng cái màn**
mà D3 REVIEW §3.4 đang treo câu hỏi nhịp header→body 18/12/24/36px — hai vấn đề cùng một chỗ,
nên xử một lần.

### ✅ 3 chỗ lồng nhưng nền KHÁC — đúng ý BA, giữ nguyên

`.wj-pc-acct-headcard__box` (`#F8FAFC` — **đã đúng chuẩn tonal BA**) ·
`.wj-exam-pc-banner--info` (`#F2FBFF`) · `.wj-pc-cart-warnbar--open` (`#EAF8EF`).

### Không đo được — LIMIT

| Route | Vì sao | Kéo theo họ nào | Xử lý |
|---|---|---|---|
| `/portal/inspection` (+ detail, remediation) | `wujia_portal_inspection` **`uninstalled`** trên DB dev local (UAT có cài) | nhóm Khảo sát (21) + **24 lượt `wj-pc-metric-card`** | Đo lại trên UAT; §5 |
| `/portal/reports/orders` | **500 có sẵn** — tz `Asia/Saigon`, đã xếp cụm **R3** của `refactor-plan.md` | `wj-rep-mcard` (16) + **20 lượt `wj-pc-metric-card`** | Không phải lỗi D4; chạy **R3 trước** hoặc đo trên UAT |

> 🔴 **Hệ quả nặng nhất của bảng này: `wj-pc-metric-card` (44 lượt — họ to thứ nhì) nằm TRỌN
> trong hai route không đo được.** Nó gọn nhất về số file (2) nên trông như ứng viên số 1 cho
> lượt migrate đầu, nhưng **không có bảng đo trước–sau thì không được migrate**. Lượt hiệu
> chỉnh vì vậy đổi sang `wujia-kpi-card` + `wujia-content-card` (12 lượt, 5/5 route đo được).
> **Ràng buộc "đo được" quyết định thứ tự lượt nhiều hơn cả kích cỡ họ.**

## 4. Kiểm kê — 65 họ

Số đo đọc thẳng từ CSS, **token đã giải tới hex/px thật**. Số BA: PC radius 16 / border 1px
`#EEF2F5` / không shadow / padding 16 (compact) · 20 (regular) / gap 12 — mobile radius 14 /
border 1px `#E5E7EB` / padding 12 · 14 / gap 8.

### A. SHELL — LÀ SurfaceCard (27 họ / 246 lượt)

> **Tiến độ:** ✅ **D4b xong 12 lượt** (`wujia-content-card` 8 + `wujia-kpi-card` 4) —
> component `wujia_portal_layout.wj_surface_card` + 4 token density đã dựng, số đo trước–sau ở
> `docs/d4b-acceptance-matrix.md`. Còn **234 lượt / 25 họ** cho D4c…D4f.

| Lượt | Họ | File | Nền | Biến thể | density | bodyMode | interactive | Số đo hiện tại | Lệch so với BA |
|---:|---|---:|---|---|---|---|---|---|---|
| 47 | `wj-pc-card` | 14 | PC | `section` | compact | padded | none | r18 · b1 `#EEF2F5` · p24 | **r 18→16** · **p 24→16** |
| 44 | `wj-pc-metric-card` | 2 | PC | **`summary`** | compact | padded | none | r16 · b1 `#EEF2F5` · p`0 22` | p 22→16 (radius + viền **đã đúng**) |
| 30 | `wujia-mdash-card` | 8 | mobile | `section`/`record` | compact | padded | **wholeCard** | r14 · b1 `#E5E7EB` · p14 | **đã đúng cả 3 số** |
| 29 | `card` (Bootstrap) | 13 | cả hai | `section` | compact | padded | none | r`.5rem` · b1 `rgba(34,41,47,.125)` · shadow | r 8→16 · viền · **bỏ shadow** |
| 20 | `wj-pc-acct-headcard` | 2 | PC | `record` | regular | padded | none | r18 · b1 `#EEF2F5` · p`22 24` | **r 18→16** · p 22/24→20 · ⏳ **chờ BA** |
| 16 | `wj-rep-mcard` | 1 | mobile | `section` | compact | flushBody | none | r16 · **KHÔNG viền** · p0 | r 16→14 · **thiếu viền hẳn** |
| 15 | `wj-auth-card` | 1 | cả hai | `section` | regular | padded | none | r12 · p`69 48 44` · shadow · @media p`57 20 26` | 🔒 **THIẾT KẾ S39 — giữ dáng** (§6) |
| 11 | `wj-rep-pccard` | 1 | PC | `section` | compact | **flushBody** | none | p0, đè lên `.wj-pc-card` | modifier — theo `wj-pc-card` |
| 8 | `wujia-content-card` | 5 | PC | `section` | regular | padded | none | r16 · **không viền** · p22 · shadow | ✅ **XONG D4b** — r16/14 · b1 · p20/14 · no-shadow |
| 7 | `wj-filter-card` | 7 | cả hai | `section` | compact | padded | none | r14 · b1 `#EEF2F5` · p12 | ⏳ **chờ BA** (§6) |
| 4 | `wujia-kpi-card` | 1 | PC | **`summary`** | compact | padded | **wholeCard** | r16 · **không viền** · p14 · shadow · min-h100 | ✅ **XONG D4b** — r16/14 · b1 · p16/12 · gap12/8 · no-shadow · **bỏ min-height** |
| 4 | `wujia-mhist-card` | 1 | mobile | `record` | compact | padded | none | r14 · b1 `#E5E7EB` · p16 | p 16→12 |
| 3 | `modal-card` | 1 | khảo sát | — | — | — | none | r16 · shadow đậm | overlay — **không phải SurfaceCard** (§5) |
| 2 | `wujia-mexam-selcard` | 1 | mobile | `record` | compact | padded | none | bg **`#F8FAFC`** · r14 · b1 `#EEF2F5` · p`14 16` | nền tonal — **đúng ý BA**; viền → `#E5E7EB` |
| 2 | `wujia-mexam-cfcard` | 1 | mobile | `section` | compact | padded | none | r14 · b1 `#EEF2F5` · p16 | p 16→12 · viền → `#E5E7EB` |
| 2 | `summary-2x2-card` | 1 | khảo sát | `summary` | compact | padded | **wholeCard** | r14 · b1.5 `#38bdf8` · p12 · shadow | §5 |
| 2 | `wj-dist-card` | 1 | khảo sát | `summary` | compact | padded | **wholeCard** | r12 · b2 `#e2e8f0` + top 4px | §5 |
| 1 | `wujia-mres-card` | 1 | mobile | `section` | regular | padded | none | r14 · b1 `#EEF2F5` · p`20 16` | p 20/16→14 · viền → `#E5E7EB` |
| 1 | `wujia-mknow-card` | 1 | mobile | `record` | compact | padded | none | r14 · b1 `#E5E7EB` · p14 | p 14→12 |
| 1 | `wujia-mnoti-detail-card` | 1 | mobile | `section` | compact | padded | none | r14 · b1 `#E5E7EB` · p16 | p 16→12 |
| 1 | `wujia-mdelivery-prodcard` | 1 | mobile | `section` | compact | **flushBody** | none | r14 · b1 `#E5E7EB` · p0 | **đã đúng** |
| 1 | `wujia-mexam-card` | 1 | mobile | `record` | compact | padded | **wholeCard** | r14 · b1 `#EEF2F5` · p`14 16` | p→12 · viền → `#E5E7EB` |
| 1 | `wujia-msubmit-card` | 1 | mobile | — | — | — | none | r16 · p`24 20` · shadow đậm | overlay "Đang tạo đơn" (S40) — **loại**, tiền lệ D3 §3 |
| 1 | `detail-card-box` · `wj-success-card` · `wj-warning-card` · `table-card` · `exam-card` · `inspection-card-item` | 5 | khảo sát | — | — | — | mixed | r12–24, shadow đủ kiểu | §5 |

### A2. MODIFIER chồng lên shell khác — **không phải shell riêng** (7 họ / 9 lượt)

Bằng chứng: markup thật là `class="wj-pc-card wj-debt-pc-card"`. Chúng chỉ **đè padding**:

| Họ | Đè | Ghi chú |
|---|---|---|
| `wj-debt-pc-card` (2) | `p 22 24` | `/portal/debt` — ⚠️ chỏi S43/C3, xem §6 |
| `wj-exam-pc-card` (2) · `wj-exam-pc-fcard` · `wj-exam-pc-sumcard` · `wj-exam-pc-dcard` | `p 22 24 24` · `18 24 10` · `18 24 24` · `20 24 24` | `wj-exam-pc-fcard` là **thẻ ngoài của 2 vi phạm lồng §3** |
| `wj-pc-order-card` | `p 20 24` | |
| `wj-debt-pc-paycard` | — | |
| `wj-rep-pccard` (11) | `p 0` | ca `flushBody` mẫu |

⇒ **9 họ này đi theo `wj-pc-card` trong CÙNG một lượt** (D4c). Sửa `.wj-pc-card` mà quên
chúng thì padding cũ vẫn thắng — đây chính là chỗ dễ "sửa xong vẫn y như cũ".

### B. Bề mặt nhưng là THÀNH PHẦN trong shell (5 họ / 24 lượt)

`card-header` (13) · `card-footer` (4) · `wujia-content-card-row-bullet` (4) ·
`wujia-mexam-selcard-badge` (2) · `inspection-card-item` (1). Đi theo shell chứa nó.

### C. Không phải bề mặt card (33 họ / 114 lượt)

`card-body` (25) · `wj-empty-state` (5 → `CMP-ES-001`) · toàn bộ `*__title/__head/__meta/__row`.
**Không có CSS khai nền + bo góc** ⇒ ngoài hợp đồng `CMP-SC-001`.

## 5. Nhóm Khảo sát — BA ghi *"provisional, chưa có seed data"*

BA viết thẳng: *"Khảo sát: provisional record; UAT chưa có seed data nên chưa khóa field
mapping"* + acceptance #12. **21 lượt / 5 file** (`wujia_portal_inspection` + trang khảo sát
trong `wujia_franchise`) có tới **11 họ card riêng, radius 12/14/16/20/24, shadow đủ kiểu** —
là chỗ lệch nặng nhất toàn portal, nhưng **không xếp lịch migrate**: BA chưa khoá field mapping,
và §3 cho thấy DB dev local còn `uninstalled` nên **chưa đo được lúc chạy**.

## 6. Bốn chỗ tưởng phải hỏi BA — **cả bốn tự quyết được, 0 câu chặn việc**

Văn bản gửi BA (thông báo, không phải câu hỏi): `docs/ba-notice-d4-surfacecard.md`.

| # | Chỗ | Lượt | Phán quyết Dev | Căn cứ |
|---|---|---:|---|---|
| 1 | `wj-filter-card` | 7 | **Làm phần KHUNG ngay** (radius/border/padding/gap); phần **tiêu đề** vẫn chờ câu (d) | Câu (d) của `ba-questions-ui-cardheader-001.md` hỏi *"có thêm dòng tiêu đề cho thẻ bộ lọc không"* — **không đụng gì tới khung**. Hai hợp đồng tách rời được |
| 2 | `wj-pc-acct-headcard` | 20 | **Làm phần KHUNG ngay** (r18→16, p 22/24→20), **giữ nguyên vị trí hai khối phải**; phần slot vẫn chờ câu (a)/(e) | Y hệt lý do trên — câu (a)/(e) chỉ hỏi *khối nào lên làm trailing*, không hỏi bo góc/khoảng đệm |
| 3 | `wj-auth-card` | 15 | 🔒 **Giữ dáng, không migrate** | `p 69 48 44` + shadow là **THIẾT KẾ** dựng theo Figma S39, không phải DRIFT ⇒ luật D3f. Cột SCOPE của BA liệt kê 14 route, **không có màn đăng nhập** |
| 4 | Nhóm Khảo sát | 21 | **Để nguyên đợt này** | **Chính BA đã viết**: *"provisional… chưa khoá field mapping"* + acceptance #12. Đây là chỉ dẫn có sẵn, không phải chỗ mơ hồ ⇒ hỏi lại là thừa |

⇒ **27 lượt (`wj-filter-card` + `wj-pc-acct-headcard`) được gỡ khỏi hàng chờ**, xếp vào lượt
migrate bình thường. Không lượt D4 nào bị chặn bởi BA.

## 7. Chỗ CHỎI issue đã nghiệm thu — ghi LIMIT, **KHÔNG tự đè**

| # | Số của D4 | Chỏi với | Bằng chứng | Đề xuất |
|---|---|---|---|---|
| 1 | gap card **12 / 8** | nhịp SectionHeader **16 / 8** chốt ở **C8b** | `_components.css:3033` `.wj-section-header--any { margin: 16px 0 8px }` | Section trước→header 16 là **khoảng cách NGOÀI card**, gap card 12 là **giữa hai card**. Hai đại lượng khác nhau ⇒ **không chỏi thật**. Ghi để khỏi nhầm |
| 2 | *"không đặt fixed height"* | **S43** khoá `height: 142px` | `portal_debt.css:104-107` + test `test_debt_summary_keeps_its_head_wrapper` | 🔴 **CHỎI THẬT** — nhưng **Dev tự quyết: GIỮ 142**, cùng luật với `wj-auth-card` (bản vẽ Figma cụ thể BA đã duyệt thắng quy tắc chung). Ghi LIMIT + báo BA ở `ba-notice-d4-surfacecard.md`; BA đảo ý thì sửa 1 dòng |
| 3 | padding PC 24→16 | **C3** đã Pass số đo màn Công nợ | `d4c` sẽ chạm `wj-debt-pc-card` (`p 22 24`) | Chạy lại bảng đo C3 trong bảng trước–sau của D4c |
| 4 | **nhịp header→body 12px** mà D3 vừa hội tụ | chính D3 REVIEW RULE 1/RULE 2 | `d3-review-matrix.md` §1 | 🔴 **D4b XÁC NHẬN CÓ THẬT**: `gap` ở rule gốc SurfaceCard cộng chồng margin header ⇒ nhịp 24px. Nhưng **RULE 1/2 KHÔNG bắt được** vì lỗi đều tay mọi card, mà hai luật đó đo *sự không đều*. ⇒ mỗi lượt D4 phải kèm **một phép đo TUYỆT ĐỐI** nhịp header→body (`scratchpad/d4b_rhythm.py`), chạy RULE 1/2 là cần nhưng **không đủ** |
| 5 | radius PC 16 | `--wj-pc-card-radius: **18px**` | `_variables.css:84` vs `:120` `--wujia-card-radius: 16px` | **DRIFT** (hai token cho cùng một vai trò) ⇒ hội tụ 18→16. ⚠️ blast radius **71 lượt** |

## 8. Token — cái nào đã có, cái nào phải thêm (**chưa thêm ở phiên này**)

| Hex BA chốt | Vai trò | Token hiện có | Việc |
|---|---|---|---|
| `#EEF2F5` | viền PC | ✅ `--wujia-border-soft` (`_variables.css:35`) → `--wj-pc-border-soft` (`:77`) | dùng lại, **không thêm** |
| `#E5E7EB` | viền mobile | ✅ `--wujia-border` (`:34`) · `--wujia-morder-border` (`:240`) | dùng lại |
| `#F8FAFC` | **nền tonal vùng phụ** | ⚠️ **chưa có token ngữ nghĩa** — cùng hex đang nằm dưới 3 tên vai-trò: `--wj-pc-table-header-bg` (`:99`) · `--wujia-mres-info-bg` (`:257`) · `--wujia-filter-field-bg` (`:269`) | **thêm 1 token** `--wujia-surface-tonal` + `--wujia-surface-tonal-radius: 12px` |
| radius 16 PC | | ⚠️ **hai token chỏi**: `--wujia-card-radius: 16px` (`:120`) ✅ vs `--wj-pc-card-radius: 18px` (`:84`) ❌ | hội tụ 18→16 ở D4c |
| radius 14 mobile | | ✅ `--wujia-morder-radius: 14px` (`:252`) | dùng lại |
| padding 16/20/12/14 | | ✅ **D4b đã thêm** `--wujia-surface-pad-compact` · `--wujia-surface-pad-regular` (+ override `@media`) | dùng lại |
| gap 12/8 | | ✅ **D4b đã thêm** `--wujia-surface-gap` — ⚠️ chỉ khai ở biến thể `--summary`, **cấm đặt ở rule gốc** (§7 dòng 4) | dùng lại |
| radius 16/14 | | ✅ **D4b đã thêm** `--wujia-surface-radius` — token RIÊNG, cố ý không đụng `--wujia-card-radius` (còn nuôi `wj-auth-card` S39) | dùng lại |

> Rule "không hex cứng": mọi hex mới phải vào `_variables.css` thành `--wujia-*`.
> **2 trong 3 hex BA chốt đã có tên sẵn** — đây là tin tốt, D4 đẻ ít token hơn dự tính.

## 9. Bẫy harness đã trả giá ngay trong phiên kiểm kê

Ghi để phiên sau khỏi chẩn đoán lại. **Cả bốn đều là harness sai, không phải code sai.**

1. 🔴 **`split(",")` cắt vào trong `:is(...)`.** `_interaction.css` gom ~30 lớp vào một
   `:is( .a, .b, … ):hover`. Cắt thô ở dấu phẩy làm `:hover` chỉ dính vào mảnh cuối ⇒ rule
   **hover** bị đọc thành **dáng mặc định** của mọi lớp trong danh sách ⇒ `wujia-mdash-card`
   bị báo oan *"có shadow"*. Đã sửa: tách ở dấu phẩy **cấp ngoài cùng** + bung `:is()`.
   *(Phụ thu: chính danh sách `:is()` này là **nguồn chuẩn cho cột `interactive`** — họ nào
   nằm trong đó thì đang là `wholeCard`. Đọc từ CSS, không đoán.)*
2. 🔴 **Gộp rule `@media` vào rule gốc.** `wj-auth-card` bị đọc thành `p 57 20 26` (bản mobile)
   thay vì `69 48 44`. Đã sửa: duyệt ngoặc thủ công để biết rule nằm trong `@media` nào.
3. 🔴 **Rule scope đè lên rule base.** `.wj-rep-pcmetrics .wj-pc-metric-card { padding: 0 16px }`
   ghi đè số gốc `0 22px`. Đã sửa: phân loại selector `base` / `variant` / `scoped` / `state`,
   chỉ `base|variant` mới là "dáng mặc định".
4. 🔴 **"Pass rỗng" ở bước đo lúc chạy — hai lần liên tiếp.** Lần 1: đăng nhập bằng `admin`
   (không phải thành viên nhượng quyền) ⇒ mọi route **404 mà vẫn có kết quả**, "18 bề mặt".
   Lần 2: DB dev local **cũ hơn code** (`wujia_portal_layout 19.0.31.13.0`, thiếu template
   `wj_card_header` của D3) ⇒ **0 bề mặt**. ⇒ **Trước khi tin một bảng đo sạch, phải nhìn
   TỔNG SỐ NODE ĐÃ DUYỆT.** 0 hay 18 trên 19 route portal là dấu hiệu đo rỗng, không phải
   dấu hiệu sạch.
5. ⚠️ **Phép thử bề mặt bắt nhầm ô nhập và nút.** Lượt đầu ra **31 "vi phạm"**, tất cả là
   `.wj-pc-filter-control`, `.select`, `.wj-pc-btn`. Đã siết: loại thẻ form, phần tử trong
   `button`/`a.btn`, tên class chứa `btn|chip|badge|pill|control|input|select|field|tab`, và
   đòi tối thiểu 160×56px. **31 → 2.**
6. ⚠️ **`networkidle` treo ở `/portal/order` + `/cart`** (bus.bus long-poll không bao giờ
   idle) ⇒ 4 lượt đo mất trắng. Đổi sang `domcontentloaded` + chờ 1200ms.
7. ⚠️ **Dò mật khẩu làm Odoo khoá đăng nhập** (*"Too many login failures"*). Mật khẩu demo
   đúng là **`wujia@test123`** (`scripts/test_sprint32_http.py:7`). Khoá rồi thì **khởi động
   lại server** là hết.

## 10. Cách tái lập

```
python3 scratchpad/d4_inventory.py            # bảng §4  (--sites để in call site)
python3 scratchpad/d4_nesting.py              # §3, cần server 8072 + DB đã -u
```

Cả hai là **harness dev-only, gitignored, KHÔNG commit** — đúng §13, y như
`d3_inventory.py` / `d3_review.py`.

**Trạng thái môi trường đã đụng ở phiên này** (không phải code):
`wujia_tea_19` đã `-u` 14 module portal (`wujia_portal_layout` 19.0.31.13.0 → **19.0.32.9.0**,
RC=0, 0 ERROR) vì DB cũ hơn code; mật khẩu `anh.owner`/`dung.multi` đặt lại `wujia@test123`.
**0 file thay đổi dưới `custom/`.**

---

## 11. Đính chính & bổ sung sau lượt D4c (05/09/2026)

Kiểm kê là **SÀN không phải TRẦN** — lượt migrate thật đã lộ 3 chỗ bảng §4 nói chưa đủ:

### 11.1 Chênh lệch 47 ↔ 34 của `wj-pc-card`: **không lượt nào bị bỏ sót**

`d4_inventory.py` gom **class con BEM vào họ cha** và loại `pc_preview.xml`:

```
34 call site shell + 17 lượt wj-pc-card__{head,title,subtitle,count} = 51
51 − 4 lượt trong pc_preview.xml (EXCLUDE_FILES)                     = 47  ✓
wj-pc-acct-headcard: 2 shell + 18 con = 20                            ✓
```

⇒ **số call site shell thật = 34 + 2 = 36**, không phải `t-foreach` như từng đoán.

### 11.2 `wj-dlv-pc-card` **không phải class** — gạch khỏi bảng modifier

Nó là `id="wj-dlv-pc-card"` (`portal_delivery.xml:12`), không có ở CSS lẫn class attr.
**Bảng modifier thật là 8, không phải 9.**

### 11.3 Token `--wj-pc-card-radius` có **6** rule tiêu thụ, không phải 4

4 rule ngoài họ D4c là bề mặt trắng PC thật nhưng **tên không chứa chữ “card”** nên quét D4a
không ra. D4c đã hội tụ radius 18→16 cho cả 4, **giữ nguyên đệm riêng** của chúng:

| Rule | Neo | Đệm giữ nguyên |
|---|---|---|
| `.wj-pc-acct-nav` | `_pc_account.css:19` | 18 |
| `.wj-pc-empty` | `_pc_components.css:288` | 40/24 |
| `.wj-pc-order-head` | `_pc_components.css:358` | 22/24 |
| `.wj-pc-cart` | `portal_order.css:86` | 20/22 |

### 11.4 Tiến độ cụm

| Lượt | Phạm vi | Lượt phủ |
|---|---|---|
| D4b | `wujia-kpi-card` (4) + `wujia-content-card` (8) | 12 |
| **D4c** | `wj-pc-card` (34) + `wj-pc-acct-headcard` (2) | **36** |
| | | **48 / 384 ≈ 12%** |

Còn lại: `wj-pc-metric-card` (44) → D4e · mobile `wujia-m*` + `wj-filter-card` → D4d ·
Bootstrap `.card` thô (75) → D4f.
