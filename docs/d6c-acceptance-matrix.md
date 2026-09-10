# D6c — Form Bù hàng: `UAT-BH-009` trọn + nửa dropdown `UAT-BH-007`

**Ngày:** 2026-09-10 · **Nhánh:** `dev/2026-09-10-d6` · **DB đo:** `wujia_tea_d6` (cổng 8080)
**Module:** layout `19.0.46.0.0 → 19.0.47.0.0` · return `19.0.3.0.0 → 19.0.3.1.0` ·
support `19.0.3.17.0 → 19.0.3.18.0` · info_request `19.0.1.7.0 → 19.0.1.8.0` · `?v=1280 → 1281`

---

## 1. Làm gì — và vì sao phạm vi rộng hơn hai issue

Chủ dự án chốt 10/09: chuẩn hoá control **mọi trang, trừ nhóm giám sát**. Kiểm kê bằng
`scripts/qa/wj_formcontrol.py` (guard mới) cho thấy portal có **ba họ control**, không phải một:

| Họ | Ở đâu | Trước |
|---|---|---|
| Bootstrap thô — đúng bệnh BA nêu | 3 form: `return/new` 9 · `support/new` 4 · `info-request/new` 7 = **20 control** | cao 30,4 / 35,9 · radius 5,25 · **0/20 có nhãn nối** |
| Ô lọc có dáng riêng | 6 màn danh sách + 2 select `/portal/info-request` | pill 38 · select sm 28 |
| Đã đạt chuẩn | debt 54 · change-password 44 · order search 44 | — |

⇒ **Không** dùng rule quét rộng `.app-content .form-control`: 24/44 control đang **cố ý lệch**
(Figma search 38, ô ngày trong pill, select kỳ công nợ 54, giám sát 44) — quét rộng là đè hết rồi
phải viết 5 rule miễn trừ. Cách chọn: **một lớp `wj-mform` trên thẻ `<form>`** + **một** rule chung.

| # | Issue | Thay đổi | Vì sao thế |
|---|---|---|---|
| 1 | BH-009 | `_components.css`: `@media (≤991.98px) .wj-mform .form-control/.form-select { min-height: 48px; border-radius: var(--wujia-surface-tonal-radius) }` + textarea 96 | 48 = đúng chiều cao `.wujia-mreturn-btn-*` đã có; radius lấy **token**, không số cứng |
| 2 | BH-009 | 3 form mobile mang lớp `wj-mform` | form mới sau này chỉ cần gắn lớp là đúng chuẩn |
| 3 | BH-009 | `for`/`id` cho **mọi** nhãn ở cả hai khối PC (`wj-ret-pc-*`) và mobile (`wj-ret-m-*`); 2 ô tệp dùng `aria-label` | hai khối render **đồng thời**, chỉ ẩn bằng `d-none` ⇒ trùng `id` là hỏng cả `for` |
| 4 | BH-009 | `@media (max-width: 360px) .wujia-mreturn-grid2 { 1fr }` | BA đo cặp *SL yêu cầu* + *Ngày sản xuất* chỉ còn 140–146px mỗi ô |
| 5 | BH-009 | Ô lọc: pill/select/search **38 → 44**, select `-sm` **28 → 44** (chỉ chiều cao) | ngưỡng chạm BA; radius/typography của FilterBar **chờ spec `UI-FILTER-001`** |
| 6 | BH-007 | Vùng `.wj-return-line-full` dưới ô chọn sản phẩm, in `l.label` **nguyên văn**, wrap tự do; `title` + `aria-describedby` | `<select>` cắt theo bề rộng ô; dữ liệu **không đổi**, tên sản phẩm trong Odoo **không đổi** |

**KHÔNG làm:** không dựng combobox thay `<select>` (chủ dự án chốt — control mới, chồng lấn
`UI-FILTER-001`/`UI-BUTTON-001` chưa có spec) · không khai lại stack font CJK (đã ở
`--wujia-font-family` từ D2) · **không đụng hai module giám sát** (họ dùng `.wj-inspection-container`,
tự nằm ngoài `wj-mform` — không cần một dòng miễn trừ nào).

## 2. Guard mới `scripts/qa/wj_formcontrol.py` — trước → sau

Đo mọi `input/select/textarea` nhìn thấy được, 19 route × {390, 360}. Hai chuẩn: control trong
`wj-mform` theo spec form (48 + radius 12), còn lại chỉ đòi ngưỡng chạm 44 — và **vùng chạm thật**
của ô trần trong pill là chính pill, không phải ô.

| Chỉ số (390 + 360) | Trước | Sau |
|---|---:|---:|
| control đo được | 80 | 80 |
| dưới ngưỡng chạm | **64** | **0** |
| thiếu nhãn liên kết | 58 | **18** |
| chiều cao 20 control của 3 form | 30,4×7 · 35,9×8 · 56,8 · 79,2×3 · 101,6 | **48×15 · 96×4 · 101,6** |
| radius 20 control đó | **5,25 × 20** | **12 × 20** |
| vùng chạm ô lọc | 28,1×2 · 38×15 · 44 · 54×2 | **44×18 · 54×2** |

**Không phải Pass rỗng:** mẫu đo giữ nguyên 80 control ở cả hai lượt, cùng route, cùng tên field.

18 "thiếu nhãn" còn lại **không thuộc hai issue**: đó là ô tìm kiếm/select lọc của 8 màn danh sách
(chỉ có placeholder) + 1 ô của nhóm giám sát. Đề nghị BA mở issue riêng — xem §6.

## 3. Tab-walk `/portal/return/new` (390px)

**9/9** control dừng được đúng thứ tự, **9/9 đọc được tên**, **9/9 có vòng focus**:
Đơn hàng gốc · Sản phẩm (trong đơn) · SL yêu cầu · Ngày sản xuất · Thời gian mở hàng · Loại lỗi ·
Ghi chú · Ảnh minh chứng · Video minh chứng. (Ô *Cửa hàng* ẩn vì user chỉ có 1 cửa hàng.)

## 4. Vùng tên đầy đủ — đo với tên 73 ký tự có CJK

Đo **không confirm đơn thật** (QA §10): chèn `data-lines` đúng khuôn controller sinh ra
(`scratchpad/d6c_dropdown.py`).

| Khổ | select có cắt | vùng tên: hiện | đủ chữ | số dòng | có cắt | tràn ngang |
|---:|---|---|---:|---:|---|---:|
| 390 | **có** (nên mới cần vùng này) | có | 73/73 | 2 | không | 0 |
| 360 | có | có | 73/73 | 3 | không | 0 |
| 1440 | có | có | 73/73 | 2 | không | 0 |

Tên ngắn (28 ký tự): select **không** cắt, vùng tên vẫn hiện đủ. `title` = 73 ký tự,
`aria-describedby` trỏ đúng vùng của **chính khối** đang hiển thị.

## 5. Hồi quy toàn portal — `wj_measure.py --diff`

13 route × 6 khổ = **78 ô**. RULE 1 HIERARCHY **0** · tràn ngang **0** · lỗi JS **0** · redirect **0**
(y hệt mốc trước). Histogram cỡ tiêu đề card và nhịp header→body **không đổi từng số**.

**16/78 ô đổi, 0 ô ở PC** (1440/1024/992 giống hệt), **0 ô mất record** — tất cả là hệ quả trực tiếp
của việc nâng ô lọc 38 → 44:

| Khổ 390/360 | Δ chiều cao |
|---|---:|
| `/portal/info-request` (2 select 28 → 44) | +32 |
| `/portal/return` (search + select + 2 ô ngày) | +18 |
| `/portal/delivery` | +12 |
| `/portal/purchase-history` | +7 |
| notification · knowledge · support · exam | +6 |

`wj_returncard.py` giữ **0 vi phạm** (thành quả D6b không bị đụng) · `wj_nesting.py` **0 chỗ lồng khung**.

## 6. Test — 11 test mới + 11 phép mutation

`custom/wujia_portal_return/tests/test_return_form_d6c.py`, tag `wujia_return_d6`.

| Phép phá | Test đỏ |
|---|---|
| M1 gỡ `for=` của một nhãn mobile | `test_moi_nhan_tro_toi_mot_control_co_that` (+ test tên cho trình đọc) |
| M2 cho `id` mobile trùng `id` PC | `test_id_khong_trung_giua_khoi_pc_va_mobile` |
| M3 gỡ lớp `wj-mform` ở Bù hàng | `test_form_mobile_dung_lop_chuan_hoa_control` |
| M4 hạ `min-height` 48 → 38 | `test_rule_chung_dat_48px_va_radius_token` |
| M5 thay token radius bằng `12px` cứng | `test_rule_chung_dat_48px_va_radius_token` |
| M6 trả ô lọc về 38px | `test_o_loc_dat_nguong_cham_44` |
| M7 gỡ breakpoint 360 | `test_hai_truong_chat_xuong_mot_cot_o_360` |
| M8 gỡ `aria-describedby` | `test_co_vung_ten_day_du_o_ca_hai_khoi` |
| M9 JS cắt bớt tên (`slice`) | `test_ten_day_du_lay_nguyen_van_tu_label_controller` |
| M10 vùng tên đầy đủ về `nowrap` | `test_vung_ten_day_du_khong_cat_chu` |
| M11 gỡ `wj-mform` ở form Hỗ trợ | `test_hai_form_mobile_khac_cung_theo_chuan` |

🔴 **Mutation lại bắt được một assert lỏng** (họ L8, y như S57): M9 lượt đầu **0 test đỏ** vì
`assertIn('opt.dataset.full = l.label', js)` vẫn khớp khi code thành `l.label.slice(0, 20)` —
chuỗi cũ là **tiền tố** của chuỗi mới. Siết thành `'opt.dataset.full = l.label;'` (có dấu chấm
phẩy) + cấm `slice` trong thân hàm mới đỏ. **Lượt đầu M5 cũng phải làm lại**: chuỗi
`border-radius: var(--wujia-surface-tonal-radius);` có ở **2 chỗ** trong `_components.css`,
`replace(..., 1)` sửa nhầm rule khác — mutation không ăn chứ guard không rỗng. Từ nay hàm mutation
**assert chuỗi phải thay đổi thật** trước khi chạy test.

- `--test-tags wujia_return_d6`: **0 failed, 0 error / 18**.
- 4 module × 4 tag D3/D4/D5/D6: **4 failed / 261** — đúng **bốn** test D3 CardHeader đã ghi nhận ở
  `d6b-acceptance-matrix.md` §5 là **có sẵn trên `main`**, không thêm lỗi mới.

## 7. Đối chiếu `Kết quả mong muốn`

**UAT-BH-009** — *"Form có kích thước, khoảng cách và bo góc nhất quán; thao tác chạm dễ dàng ở
360px trở lên; trình đọc màn hình xác định đúng tên của từng trường."*

| Vế | Đạt | Bằng chứng |
|---|---|---|
| kích thước nhất quán | ✅ | 20 control từ 5 cỡ (30,4 · 35,9 · 56,8 · 79,2 · 101,6) về **48 / 96** |
| bo góc nhất quán | ✅ | radius **5,25 → 12** cả 20 control, lấy token dùng chung với card/nút |
| chạm dễ ở 360 | ✅ | dưới ngưỡng chạm **64 → 0**; cặp trường chật xuống **1 cột** ở 360 |
| trình đọc màn hình đọc đúng tên | ✅ | `/portal/return/new` thiếu nhãn **9 → 0**; tab-walk 9/9 đọc được tên |
| nhất quán *toàn Portal* | ✅ | cùng chuẩn áp cho 3 form (20 control) + ô lọc 8 màn; giám sát cố ý ngoài phạm vi |

⇒ **5/5 vế đạt.**

**UAT-BH-007** — *"Portal hiển thị đúng nguyên văn tên sản phẩm từ Odoo; tên song ngữ dễ đọc, không
bị cắt giữa nội dung và không tạo cảm giác dùng font rời rạc."*

| Vế | Đạt | Bằng chứng |
|---|---|---|
| nguyên văn tên | ✅ | vùng tên in đủ 73/73 ký tự; JS lấy thẳng `l.label`, test cấm cắt chuỗi |
| không cắt giữa nội dung — **card** (D6b) | ✅ | cắt ngay dòng 1: **8 → 0**, `…` chỉ ở cuối dòng 2 |
| không cắt giữa nội dung — **form** (D6c) | ✅ | tên đầy đủ wrap 2–3 dòng, **0** chỗ cắt, 0 tràn ngang |
| font không rời rạc | ✅ | không khai lại stack font ở module (test khoá từ D6b) |

⇒ **4/4 vế đạt** ⇒ **cả hai nửa của BH-007 xong**, đủ điều kiện handoff.

## 8. LIMIT (ghi vào ledger)

1. **Vế "xem đủ option khi mở" của BH-007 giữ nguyên `<select>`.** Chủ dự án chốt 10/09: không dựng
   combobox. Đo được `<select>` vẫn cắt option theo bề rộng ô ở **trạng thái đóng** (`selCắt = true`
   cả 3 khổ) — chỗ đó nay được **vùng tên đầy đủ** bù; còn khi **mở**, trên điện thoại thật danh
   sách là control của hệ điều hành nên không cắt. Dựng combobox riêng chồng lấn `UI-FILTER-001` và
   `UI-BUTTON-001` (chưa có spec BA) ⇒ để lứa D7+.
2. **Ô lọc mới chỉ nâng CHIỀU CAO** lên 44. Radius (10) và cỡ chữ (12) của FilterBar giữ nguyên vì
   `CMP-FB-001`/`UI-FILTER-001` chưa có spec — đổi bây giờ là tự đoán số.
3. **18 ô lọc/tìm kiếm còn thiếu nhãn cho trình đọc màn hình** (8 màn danh sách, chỉ có placeholder)
   + 1 ô của nhóm giám sát. Ngoài phạm vi BH-009 (là *form*), đề nghị BA mở issue riêng.
4. **Hai module giám sát không đụng** (quyết định 08/09) — control của họ vẫn 44/r12 sẵn có.
5. `/portal/reports/orders` báo lỗi SQL `time zone "Asia/Saigon" not recognized` trên PostgreSQL
   **của máy local**, có ở cả hai lượt đo trước và sau ⇒ lỗi môi trường, không phải hồi quy D6c.
