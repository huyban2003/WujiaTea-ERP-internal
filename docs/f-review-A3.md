# ★FR-A3 — Review cổng cụm F (F0 → F5b) → quyết mở lại Issue List

*Phiên 18/09/2026 · Mac · DB `wujia_f0` port 8099 (giống UAT) · commit + push `main`, **KHÔNG deploy UAT***

Cổng này duyệt 7 phiên:

| Phiên | Commit | Nội dung |
|---|---|---|
| F0 | `0f44aad` | công cụ đo (`css_owner`, `check_layers`) + mốc `wujia_f0` |
| F1 | `aebcd56` | 6 điểm controller vá an toàn (open redirect · MIME/cỡ đính kèm · `str(e)` · `action_submit`) |
| F2 | `dab6f4c` | dời CSS 8 màn nhỏ khỏi `wujia_portal_layout` |
| F3 | `584e3aa` | dời CSS Đặt hàng + Home khỏi layout |
| F4 | `52c7650` | duyệt 44 rule module viết đè component |
| ★FR-B | (trong `099a5a6`) | review khối B + trả 2 khoản nợ F4 |
| F5a | `099a5a6` | menu về module sở hữu route — khung hết biết đường dẫn |
| F5b | `33240c0` | test của khung về đúng chủ — cross-module 236 → 0 |

**Vì sao bắt buộc có phiên này:** mỗi phiên F tự đo bằng mốc của chính nó. FR-B đo suốt F0 → `52c7650`,
nhưng F5a/F5b đo bằng **mốc F5 mới** (mốc F0 mù 16 route + 11 trạng thái rỗng) ⇒ **chưa từng có phép đo
đi suốt F0 → HEAD**. Tiền lệ D3e: mọi số từng lượt đều Pass mà thẻ tóm tắt vẫn vỡ, chỉ ảnh bắt được.

---

## 1. Kết luận

✅ **Cổng F ĐẠT — đề nghị mở lại Issue List.**

Đi suốt từ mốc F0 tới HEAD, giao diện **không đổi ngoài bảng đã duyệt của FR-B** (chuẩn đầu bảng 14px)
và **một thay đổi mới của chính phiên này** (mục 4.1, đã chụp ảnh đối chứng). Suite **574/574**,
mutation **10/10 đỏ→xanh**, khung `portal_layout` giữ được cả hai tuyên bố của F5 (0 route nghiệp vụ,
0 test cross-module).

Nhưng phiên này **không phải chỉ đóng dấu**. Nó bắt được 3 thứ mà cả 7 phiên trước bỏ lọt:

1. **2 lỗi thật về tầng** (mục 4.2) — khung và `portal_base` gọi hàm của module mình không depend ⇒
   cài riêng là 500. `check_layers` không thấy vì nó chỉ đọc `__manifest__.py`.
2. **5/6 lỗi HIERARCHY "trạng thái rỗng" là thước đo báo nhầm**, không phải lỗi giao diện (mục 4.1) —
   suýt nữa sửa nhầm một thiết kế đã duyệt theo Figma.
3. **4 con số chép tay trong nhật ký sai so với máy** (mục 6) — đúng bài học #2 của FR-B.

## 2. Bảng Pass/Fail

Mốc: `docs/f0-baseline/` (26 + 15 route × 5 khổ) và `docs/f5-baseline/` (46 + 28 route × 2 khổ).

| # | Phép đo | Ngưỡng | Kết quả | Pass |
|---|---|---|---|---|
| 1 | Suite 15 module portal (`-u`, DB `wujia_f0`) | 0 failed / 0 error | **574/574** (572 + 2 guard mới) | ✅ |
| 2 | **Phép đo quyết định**: DB mới, chỉ cài khung `-i wujia_portal_layout --test-enable` | 0/0 | **0 failed 0 error / 129 test** | ✅ |
| 3 | DB mới, chỉ cài `-i wujia_portal_base` (không test) | cài được | **exit 0** — L3a dựng được một mình | ✅ |
| 4 | Test của `portal_base` trên DB chỉ có `portal_base` | — | **41 failed / 81 error** — *đúng thiết kế*, xem mục 5.1 | ⚠️ ghi nợ |
| 5 | `wj_measure` bộ F0, anh.owner (26 route × 5 khổ) vs mốc F0 | lệch quy được về dữ liệu/đồng hồ/bảng duyệt | **8 ô, cả 8 do chuẩn 14px của FR-B** · 0 ô mất record | ✅ |
| 6 | `wj_measure` bộ F0, em.hcm (15 route × 5 khổ) vs mốc F0 | nt | **6 ô, cùng nguyên nhân** · 0 ô mất record | ✅ |
| 7 | `wj_measure` bộ F5, 2 vai trò (46 + 28 route × 2 khổ) vs mốc F5 | 0 lệch, 0 ô mất record | **0 / 0** | ✅ |
| 8 | Ảnh mọi route × 2 khổ, 2 vai trò — xem **từng cặp** | 0 khác biệt chưa duyệt | **148 cặp: 81 giống hệt · 66 nhiễu/đồng hồ/khử răng cưa · 1 cố ý** | ✅ |
| 9 | `nav_dump --diff` 2 vai trò × 2 khổ | 0 lệch | **chỉ còn dư âm `id` của 2 `<li>` tiêu đề (184 + 112, 100%)** — đã chụp lại mốc | ✅ |
| 10 | `b4_regression.py` | 286/286 | **286/286** | ✅ |
| 11 | `css_owner.py --layout-domain` | 0 nhóm 1 màn ngoài danh sách giữ | **26 nhóm, cả 26 trong danh sách giữ** (mục 6) | ✅ |
| 12 | `css_owner.py --overrides` | mọi rule đổi dáng có comment `F4(c)` | **8 rule, đủ comment** (mục 6) | ✅ |
| 13 | `check_layers.py` R1–R5 | đúng vi phạm cũ đã biết | **2** (mục 6) | ✅ |
| 14 | `check_layers.py` R6 (khung biết route nghiệp vụ) | 0 | **0** | ✅ |
| 15 | `check_layers.py` **R7 mới** (gọi chéo tầng lúc chạy) | 0 của mình | **2 — cả 2 trong code anh Thái** | ✅ |
| 16 | `test_ownership.py` khung | cross = 0 | **0 test / 0 assert** | ✅ |
| 17 | `test_ownership.py` toàn portal | assert không giảm (F5b: 1549) | **1586** | ✅ |
| 18 | Mutation xuyên khối (F1 ×3 · FR-B ×2 · F5a ×2 · F5b ×1 · FR-A3 ×2) | mọi phép: phá → đúng guard đó đỏ → hoàn tác xanh | **10/10** | ✅ |
| 19 | Kiểm sống 5 điểm F1 trên cổng 8099 (không chỉ qua test) | 5/5 | **5/5 ĐẠT** | ✅ |
| 20 | Phiên bản manifest ↔ phiên bản đã cài trong DB (25 module) | 0 lệch | **0 lệch** | ✅ |
| 21 | `?v=` của mọi CSS layout bị sửa trong khối F | bump hết | **4/4 bump** (`_components` 1293→1297 · `_interaction` 1292→1293 · `_pc_components` 1293→1295 · `style` 1010→1300) | ✅ |
| 22 | `ir.ui.view` mồ côi trên `wujia_f0` | 0 | **0** | ✅ |
| 23 | Template portal không inherit mà không ai gọi | 0 | **0 / 103** | ✅ |
| 24 | File rác (`.bak`, `.orig`, `__pycache__`) bị git theo dõi | 0 | **0** | ✅ |
| 25 | File của anh Thái bị 7 commit cụm F đụng vào | 0 | **0** | ✅ |

## 3. Số đo

### 3.1 Hình học — mốc F0 → HEAD (lần đầu đo suốt cả cổng)

`wj_measure --diff docs/f0-baseline/measure_{anh,em}.json` — **0 ô mất record** ở cả 2 vai trò.
Ô lệch chiều cao, **cả 14 ô đều quy về đúng một nguyên nhân đã duyệt**: FR-B gỡ luật
`table th{font-size:16px!important}` ⇒ đầu bảng PC về 14px ⇒ bảng ngắn lại.

| Vai trò | Route | Khổ | Trước | Sau | Δ |
|---|---|---|---|---|---|
| anh.owner | `/portal/support` | 992 | 2234 | 1894 | **−340** (20 hàng × 17px) |
| anh.owner | `/portal/info-request` | 992 | 1654 | 1603 | −51 |
| anh.owner | `/portal/debt/payment-history` | 992 | 1226 | 1197 | −29 |
| anh.owner | `/portal/order` | 1024 | 2356 | 2336 | −20 |
| anh.owner | `/portal/return` | 992 | 1744 | 1732 | −12 |
| anh.owner | `/portal/order` | 1440 / 992 | 1950 / 2778 | 1947 / 2775 | −3 |
| anh.owner | `/portal/debt` | 1440 | 1294 | 1292 | −2 |
| em.hcm | `/portal/order` | 1440…360 | — | — | −3 … −20 (cùng nguyên nhân) |
| em.hcm | `/portal/purchase-history` | 1024 | 905 | 900 | −5 |

### 3.2 Hình học — mốc F5 → HEAD (F5a + F5b + FR-A3 có đổi gì không)

**0 ô lệch, 0 ô mất record** trên 46 + 28 route × 2 khổ. Tức là F5a/F5b **không đụng một pixel nào**,
đúng như hai phiên đó tuyên bố — nay có bằng chứng đi suốt.

### 3.3 Trước vá → sau vá (cô lập đúng việc phiên này làm)

`--diff` 4 bộ đo trước/sau khi vá: **0 ô lệch cả 4 bộ**. Vá 18→16px không đổi chiều cao trang;
chỉ RULE 1 đổi: **HIERARCHY 6 → 5** (mất đúng `/portal/exam/register`).

### 3.4 Ảnh — 148 cặp, xem từng cặp

| Nhóm | Số cặp |
|---|---|
| Giống hệt từng pixel | **81** |
| Thanh nạp trang 3px ở góc trên trái (nhiễu **có sẵn trong mốc F0**, 18/41 ảnh) | 50 |
| Đồng hồ khung giờ đặt hàng ở Home | 2 |
| Nhiễu ≤ 6×10px | 1 |
| **Cố ý**: cỡ chữ "Người tham gia" ở `/portal/exam/register` | **1** |
| Khử răng cưa chữ/biểu đồ SVG vẽ bằng JS (đã soi từng cái: ≤ **0,11%** số pixel, nội dung giống hệt) | 13 |

⇒ **0 khác biệt chưa được duyệt.** Ảnh đối chứng: `docs/f-review-A3-img/`.

### 3.5 Điều hướng — `nav_dump --diff` vs mốc F5

| Vai trò | Mục lệch | Bản chất |
|---|---|---|
| anh.owner | 184 | **184/184** là 2 `<li>` tiêu đề nhóm ("MENU CHÍNH", "TIỆN ÍCH") có thêm `id="nav_header_*"` — neo của F5a |
| em.hcm | 112 | **112/112** y hệt |

0 mục menu đổi thứ tự / đổi `href` / đổi trạng thái sáng / đổi badge trên 74 route × 2 khổ.
Đã **chụp lại mốc** vào `docs/fra3-baseline/nav_{anh,em}.json` ⇒ trả xong khoản nợ dư âm của F5a.

## 4. Đã sửa trong phiên

### 4.1 Lỗi HIERARCHY trạng thái rỗng: máy báo 6, **chỉ 1 là lỗi thật**

Chủ dự án chốt đầu phiên: sửa luôn nếu < 30 dòng/lỗi. Nhật ký F5a ghi "4 lỗi trạng thái rỗng + 1 ở
`/portal/exam/register`". **Đo lại bằng máy ra 6** (thêm `/portal/notification/1`). Soi từng cái bằng
ảnh thì 5/6 **không phải lỗi**:

| Route | Chữ bị báo | Cỡ | Tiêu đề card | Kết luận |
|---|---|---|---|---|
| `/portal/purchase-history` (rỗng) | "Chưa có đơn hàng" | 20 | 18 | **báo nhầm** — khối rỗng căn giữa có icon, là nội dung chính của thân card, không phải nhãn phụ |
| `/portal/delivery` (rỗng) | "Không có chuyến giao" | 28 | 22 | **báo nhầm** — nt (khung nét đứt + icon, Figma) |
| `/portal/notification` (rỗng) | "Không có thông báo" | 20 | 18 | **báo nhầm** — nt |
| `/portal/reports/orders` (rỗng) | "Chưa có dữ liệu" | 20 | 18 | **báo nhầm** — nt |
| `/portal/notification/1` | "Thông báo demo #1" | 24 | 18 | **báo nhầm** — đây là TIÊU ĐỀ của chính thông báo trong card "Nội dung thông báo", to hơn là đúng |
| `/portal/exam/register` | "Người tham gia" | 18 | 18 | ✅ **lỗi thật** — khối con bằng đúng tiêu đề card |

RULE 1 của `wj_measure` coi mọi chữ trong card là "nhãn phụ". Khối trạng thái rỗng và tiêu đề bản ghi
không phải nhãn phụ ⇒ 5 ô trên là **giới hạn của thước đo**, ghi vào bảng đã duyệt như FR-B §8 từng làm,
**không sửa pixel**. Ảnh: `docs/f-review-A3-img/`.

**Sửa cái thật (2 dòng):** `wj-exam-pc-sectitle--sm` 18 → **16px** ở `portal_exam.css`, áp đúng chốt của
chủ dự án ngày 04/09 *"khối con trong card = 16px"* — 3 anh em của nó (`--2`, `sechead--sm`,
`slots__head`) đã 16px từ F4, riêng chỗ này sót vì không dùng class `wj-card-header`.

**Việc thật sự phải làm** không phải 6 ô này mà là: 4 màn rỗng đang dùng **3 cỡ khác nhau**
(28 / 20 / 18px) và 2 kiểu khung (nét đứt / nét liền). Đó là cụm **EmptyState** — mục 7.

### 4.2 Hai lỗi tầng thật, cả hai chưa ai bắt suốt 7 phiên

Phép đo mới của phiên này — **cài `wujia_portal_base` một mình trên DB trắng** — làm lộ ra:

| Chỗ | Gọi | Chủ hàm | Hậu quả khi module kia tắt |
|---|---|---|---|
| `wujia_portal_base/controllers/portal.py:222` (Home mobile) | `_is_within_order_window`, `_user_now_hours` | `wujia_portal_order_window` (L3b) | Home **500** — đúng 5 lần `500 != 200` trong phép đo |
| `wujia_portal_layout/controllers/portal.py:155` (ACL ảnh đại diện) | `_get_accessible_franchise_ids` | `wujia_franchise` (nghiệp vụ) | Khung cài một mình → mở ảnh người khác là **500** |

Cái thứ hai đáng nói: **khung gọi thẳng hàm nghiệp vụ** — đúng thứ cả cụm F đang đi dọn. `check_layers`
không thấy vì nó chỉ đọc `depends` trong manifest; `test_ownership` không thấy vì đây là code chạy, không
phải test. Cả hai **có từ trước cụm F** (`b91ad56`), không phải do F1–F5b gây ra.

**Cách sửa** không phải thêm `depends` (thêm là vi phạm R2/R5 thật sự) mà là **bọc guard**:

- `portal_base`: thiếu module khung giờ ⇒ coi như không đặt khung giờ (`state='always'`), Home vẫn sống.
- `portal_layout`: thiếu nghiệp vụ ⇒ **đóng** (403), không phải mở — hướng an toàn.

Kèm **2 test guard mới** (`test_fra3_layer_guard.py` ở cả hai module) giả lập module tắt bằng descriptor
ném `AttributeError`; gỡ guard là test đỏ ngay (mutation M9, M10).

### 4.3 `check_layers.py` có thêm luật **R7**

Chỗ mù ở trên là chỗ mù của **công cụ**, nên vá luôn công cụ: R7 quét AST mọi module, tìm lời gọi
`_method` mà module không depend, bỏ qua tên trùng với method của Odoo core, và **chỉ báo khi không có
`hasattr`/`getattr` bọc quanh**. Chạy 2,5 giây. Kết quả hiện tại: **2 vi phạm, cả 2 trong code anh Thái**
(mục 8).

## 5. Nợ ghi lại

### 5.1 `wujia_portal_base` không tự test được một mình (41 failed / 81 error)

Cài `portal_base` một mình thì **cài được** (exit 0) nhưng **test của nó không chạy được**: 78/81 lỗi là
`External ID not found` cho view của module chưa cài (`wujia_portal_support.portal_support_list`,
`wujia_portal_return.portal_return_detail`, …), 41 fail còn lại là `search([('key','=',...)])` ra rỗng.

**Đúng thiết kế, không phải hỏng:** 6 file test đang quét toàn portal —
`test_scan_d3_card_header` (60) · `test_scan_d4_surface_card` (29) · `test_scan_c8_section_header` (12) ·
`test_handover_inspection` (12) · `test_home_c7` (5) · `test_f5_menu_ownership` (4). Trong đó
`test_scan_d4_surface_card` + `test_home_c7` **có từ trước cụm F** (commit `4110f71`, `b33b46f`) ⇒ tình
trạng này **không phải do F5b gây ra**, F5b chỉ làm nó rõ hơn (thêm 84 điểm).

**Nợ:** gắn nhãn cho nhóm test "quét cả cổng" (vd `@tagged('portal_suite')`) hoặc cho chúng tự bỏ qua khi
module chủ chưa cài. > 30 dòng, chạm 6 file ⇒ **để phiên F6**, không sửa trong phiên review.

### 5.2 148 dòng comment nhắc mã phiên trong code portal

Chủ dự án đã nhắc **2 lần** về việc hạn chế comment. Đếm bằng máy: **148 dòng** trong 14 module nhắc
`F4(c)` / `FR-B` / `F5a` / `D3d` / `D3e`… (`portal_base` 42 · `portal_layout` 41 · `portal_exam` 20 …).
Phần lớn giải thích *vì sao* (giữ được), phần còn lại là biên niên sử (mã phiên thuộc về `git log` và
`docs/`, không thuộc code). Dọn cần đọc từng chỗ ⇒ **ghi nợ**, đề xuất kèm luật: *comment nói VÌ SAO,
không nói PHIÊN NÀO*.

### 5.3 Nợ cũ vẫn treo

- `wujia_portal_order_window` thiếu depend `portal_base` (R4) — chờ **F7** tách pilot.
- Bảng kết quả màn Thi giữ 13px — chờ BA xác nhận (nợ FR-B).
- `/portal/exam/register` mục "Người tham gia" vẫn là chỗ defer chờ BA về **nội dung** (chỉ typography
  được sửa trong phiên này).

## 6. Bốn con số nhật ký sai so với máy

Đúng bài học #2 của FR-B — **không tin số chép tay**:

| Ghi trong nhật ký | Máy đo lại | Vì sao |
|---|---|---|
| `check_layers` "1 vi phạm cũ" | **2** | thêm `wujia_mobile_portal_info_request` depend `wujia_portal_info_request` (R3 chéo kênh) — module mới của anh Thái |
| `css_owner --layout-domain` "20 nhóm" | **26** | F5a dời markup menu khỏi khung làm 6 nhóm chrome đổi quy kết; **không có CSS mới**. Đề nghị chốt giữ 6 nhóm này ở layout và ghi vào danh sách giữ |
| `css_owner --overrides` "9 rule" | **8** | chính FR-B đã xoá rule `!important` màn Thi |
| "~124 chỗ EmptyState viết tay" | **92 viết tay / 124 dùng component** | con số 124 chép tay thực ra là số chỗ **đã** dùng component |

## 7. Đề xuất gửi BA — mở cụm **EmptyState**

Đếm bằng máy (lxml, mọi `class` chứa `empty` trong 13 module portal, bỏ màn Khảo sát):

- **124** khối đã dùng component chung `wj-empty-state`
- **92** khối **viết tay** bằng class riêng, rải 13 module — `portal_debt` 25 · `portal_exam` 16 ·
  `portal_purchase_history` 12 · `portal_base` 9 · `portal_report` 6 · `portal_sale` 6 · `portal_delivery` 5 …
- **6 họ tên class đối chọi nhau**: `wj-pc-empty__*` (14) · `wujia-empty-state` (6) ·
  `wujia-content-card-empty` (4) · `wj-debt-pc-emptybox__*` (3) · `wj-exam-pc-panel-empty__*` (2) ·
  `wj-rep-mempty` (2)
- **3 cỡ tiêu đề khác nhau** trên 4 màn rỗng PC: **28px** (Giao hàng) · **20px** (Lịch sử, Thông báo,
  Báo cáo) · **18/16px** (component `wj-empty-state`) — và 2 kiểu khung (nét đứt / nét liền)

**Câu hỏi cho BA (3 câu, không hơn):**

1. Trạng thái rỗng PC chốt **một** cỡ tiêu đề nào — 20px (đa số hiện tại) hay 18px (bằng component mobile)?
2. Khung khối rỗng: **nét đứt** (Giao hàng) hay **nét liền** (Lịch sử, Báo cáo)?
3. Khối rỗng có **luôn** kèm nút hành động không (giỏ trống đang có "Chọn sản phẩm", 91 chỗ còn lại không)?

Trả lời xong là gom được 92 chỗ về 1 component, và `wj_measure` RULE 1 chuyển từ "cấm chữ to trong card"
sang "mọi trạng thái rỗng phải cùng một cỡ" — đo được thay vì phải nhìn.

## 8. Báo anh Thái (không sửa hộ)

| # | Việc | Bằng chứng |
|---|---|---|
| 1 | `wujia_franchise/tests/__init__.py` còn `from . import test_wujia_franchise_mobile` — file đã xoá ⇒ mọi lần `-i` kèm test là `ImportError` | `ls custom/wujia_franchise/tests/` chỉ có `test_franchise_onboarding.py` |
| 2 | **File bàn giao** `wujia_portal_base/tests/test_handover_inspection.py` (286 dòng, 17 guard màn Khảo sát) — F5b để tạm, cần dời trọn về `wujia_portal_inspection/tests/` | mục 5.1 |
| 3 | `wujia_mobile_portal_info_request` depend `wujia_portal_info_request` ⇒ **vi phạm R3** (portal ↔ mobile không depend chéo) | `check_layers` |
| 4 | 4/6 module `wujia_mobile_*` còn `auto_install: False` (chốt ADR-027: module ghép thuần nên True) | manifest |
| 5 | **R7 mới**: `wujia_franchise` gọi `_wj_ensure_contract` của `wujia_franchise_contract` (2 chỗ) mà không depend, không guard | `wujia_franchise_management.py:366`, `franchise_onboarding_wizard.py:236` |
| 6 | **Rủi ro deploy**: view `res_config_settings_view_form_wujia_inspection` (id 1554) còn trong DB trỏ tới field `metabase_instance_url` đã dời sang `wujia_metabase_connector` (chưa cài) ⇒ `-u` module khác là `ParseError`. Gỡ bằng `-u wujia_franchise_inspection` | log 08:5x hôm nay |
| 7 | `wujia_metabase_connector` chưa có trong bảng phân tầng của `check_layers` | `check_layers` |
| 8 | `origin/thai` đã có **2 commit** chưa merge (`8328b32` — `wujia_mobile_franchise_operations`) | `git log origin/main..origin/thai` |

## 9. Mở lại Issue List — thứ tự nhận việc

Đủ điều kiện mở lại (25 phép đo mục 2, mutation 10/10, nợ đã ghi). Thứ tự **E4b → E4c → E5 → E6a/b →
E7a/b → E8**, đối chiếu 5 issue `Ready for Dev` hiện có:

| Cụm | Issue | Reconcile code ↔ sheet |
|---|---|---|
| **E4b, E4c** | `UI-FILTER-001` (STT 139) | E4a **đã làm nền** (`12750a2`: FilterBar CMP-FB-001 + 2 route mẫu, ghi rõ "chưa đóng") ⇒ nhận tiếp E4b phủ hết call site, **không làm lại từ đầu** |
| **E5** | `UI-LISTCARD-001` (STT 136) | chỉ có trong docs, chưa có code |
| **E6** | `UI-PAGECONTAINER-001` (STT 129) | chỉ có trong docs |
| **E7** | `UI-BUTTON-001` (STT 132) | chỉ có trong docs |
| **E8** | `UI-SIDEBAR-001` (STT 131) | chỉ có trong docs — **lưu ý**: F5a vừa đổi chủ sở hữu mọi mục sidebar, làm E8 phải sửa ở 11 module chứ không phải 1 |

Không có bẫy WJ-ORD-023 (issue đã fix mà sheet chưa sync) trong 5 cái này.

## 10. Bài học cho khối sau (F6–F13)

1. **Công cụ đo cũng có chỗ mù, và chỗ mù của nó là chỗ lỗi trốn.** `check_layers` đọc manifest ⇒ không
   thấy call chéo tầng lúc chạy; 2 lỗi 500 sống suốt 7 phiên. Mỗi phiên nên hỏi: *công cụ này KHÔNG
   nhìn thấy cái gì?*
2. **Cài module một mình là phép đo rẻ nhất mà mạnh nhất.** 2 lỗi tầng, 1 khoản nợ test đều từ đúng một
   lệnh `-i <module> --test-enable` trên DB trắng. Đưa vào chuẩn nghiệm thu mọi phiên tách module.
3. **Máy báo lỗi không có nghĩa là có lỗi.** 5/6 ô HIERARCHY là thước đo báo nhầm; nếu tin số mà sửa thì
   đã phá một thiết kế Figma đã duyệt. Số chỉ cho biết *chỗ nào cần nhìn*, ảnh mới kết luận.
4. **Số chép tay sai đều đặn** — 4 con số lệch trong phiên này, sau khi FR-B đã bắt 3 con số lệch của F4.
   Nhật ký nên ghi *lệnh* để chạy lại, không ghi *kết quả*.
5. **Guard mới phải qua `test_ownership` trước khi commit**: 2 test mới của phiên này thoạt đầu làm khung
   có lại 1 test cross-module — chỉ vì **tên module nằm trong chuỗi thông báo lỗi**. Đưa tên module vào
   docstring, đừng đưa vào code.

## 11. Lệnh chạy lại

```bash
cd ~/odoo-dev/WujiaTea
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3

# server đo
cd odoo19 && $PY odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' \
  --http-port=8099 --gevent-port=8199

# suite 15 module portal (kèm -u; tests/__init__ của wujia_franchise còn import file đã xoá)
M=$(ls custom | grep -E '^wujia_portal_' | grep -v inspection | tr '\n' ',' | sed 's/,$//')
$PY odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' --http-port=8097 \
  --gevent-port=8197 --stop-after-init --test-enable -u "$M"      # → 574/574

# phép đo quyết định: DB trắng, chỉ cài khung / chỉ cài nền ghép
createdb -h 127.0.0.1 -U odoo19 wujia_fra3_layout
$PY odoo-bin -c ../config/odoo.conf -d wujia_fra3_layout --db-filter='^wujia_fra3_layout$' \
  --stop-after-init -i wujia_portal_layout --test-enable        # → 129/129
createdb -h 127.0.0.1 -U odoo19 wujia_fra3_base
$PY odoo-bin -c ../config/odoo.conf -d wujia_fra3_base --db-filter='^wujia_fra3_base$' \
  --stop-after-init -i wujia_portal_base                        # → exit 0 (cài được)

# hình học + ảnh, so mốc F0 và mốc F5
R=$(tr '\n' ' ' < docs/fra3-baseline/routes_f0_anh.txt)
$PY scripts/qa/wj_measure.py --base http://127.0.0.1:8099 --portal-login anh.owner --routes ${=R} \
  --breakpoints 1440 1024 992 390 360 --screenshots --out /tmp/a3_anh.json
$PY scripts/qa/wj_measure.py --diff docs/f0-baseline/measure_anh.json /tmp/a3_anh.json
$PY scripts/qa/nav_dump.py --diff docs/f5-baseline/nav_anh.json /tmp/a3_nav_anh.json

# sở hữu CSS · tầng (R1–R7) · sở hữu test · B4
$PY scripts/qa/css_owner.py --layout-domain ; $PY scripts/qa/css_owner.py --overrides
$PY scripts/qa/check_layers.py ; $PY scripts/qa/test_ownership.py --all-portal --quiet
$PY scripts/ba_spec/b4_regression.py --base http://127.0.0.1:8099
```

## 12. UAT

**UAT vẫn là bản TRƯỚC F5a.** Phiên này commit + push `main` nhưng **không deploy**. BA đừng retest menu
sidebar / bottom-nav trên UAT — bản trên đó chưa có thay đổi của F5a/F5b/FR-A3.

Khi deploy: `-u` 3 module đã bump (`wujia_portal_layout` 19.0.51.0.10 · `wujia_portal_base` 19.0.7.17.8 ·
`wujia_portal_exam` 19.0.5.15.5) kèm các module F5a/F5b chưa lên, và **xử lý trước** rủi ro view cũ ở
mục 8 #6.
