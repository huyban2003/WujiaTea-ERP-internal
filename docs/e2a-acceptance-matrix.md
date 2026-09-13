# Nghiệm thu E2a — StatusBadge `CMP-SB-001` (`UI-STATUSBADGE-001`, STT 128)

Ngày 13/09/2026 · DB đo `wujia_tea_e2` (clone `wujia_tea_mt4`, **có** cài
`wujia_portal_inspection` + `wujia_franchise_inspection` giống UAT) · cổng 8092 ·
đối chứng `wujia_tea_e2base` (worktree mã trước khi sửa, cổng 8094) · login `anh.owner`.

## FIX
1. **Lỗi gốc BA nêu** — `utils.py` `'sale': ('Đã xác nhận', 'wujia-badge-success')` (xanh lá)
   → `status_badge('info')` (xanh dương). Sửa ở **Python**, nên PC và mobile hết lệch màu cùng lúc.
2. Một component nền `.wj-status-badge` + 7 variant ngữ nghĩa, token hex ở `_variables.css`,
   dáng ở `_components.css` (tầng dùng chung PC + mobile) — **không** biến thể theo route/breakpoint.
3. Gom mapping trạng thái về **một nguồn** (`STATUS_VARIANT_BY_LABEL` + `status_badge()` /
   `status_badge_for()`); xoá **4 dict literal trùng lặp** trong `portal_history.xml` và 2 dict inline
   trong `portal_home.xml`. Hai họ `wj-pc-badge--dlv-*` và `wujia-mdelivery-badge--*` hết call site.
4. Migrate 65 call site / 9 file thuộc nhóm màn BA audit.
5. **Contrast WCAG AA** (Dev tự quyết 13/09, chủ dự án giao quyền): spec BA vừa đòi "đạt WCAG AA"
   vừa đưa 7 cặp hex mà **5 cặp đo dưới 4.5** (chữ 13px không phải chữ lớn nên ngưỡng 3.0 không áp dụng).
   Chọn: **giữ nguyên 7 nền của BA, chỉ làm đậm chữ tối thiểu ở 5 variant trượt**, cùng tông (lệch hue ≤ 12°).
   Đổi nền mới là đổi nhận diện; làm đậm chữ thì mắt thường gần như không phân biệt mà acceptance đạt.

   | Variant | Nền (giữ hex BA) | Chữ BA | Tỉ lệ BA | Chữ dùng | Tỉ lệ sau |
   |---|---|---|---|---|---|
   | processing | `#FEF3C7` | `#B45309` | 4.51 ✅ | giữ nguyên | 4.51 |
   | feedback | `#F3E8FF` | `#7C3AED` | 4.83 ✅ | giữ nguyên | 4.83 |
   | neutral | `#F3F4F6` | `#6B7280` | 4.39 ❌ | **`#6A707E`** | 4.51 |
   | danger | `#FEECEC` | `#DC2626` | 4.24 ❌ | **`#D52222`** | 4.51 |
   | info | `#EAF7FD` | `#168FC2` | 3.35 ❌ | **`#1378A3`** | 4.53 |
   | success | `#EAF8EF` | `#16A34A` | 3.01 ❌ | **`#11813B`** | 4.54 |
   | pending | `#FFF7E6` | `#D97706` | 2.99 ❌ | **`#AC5E05`** | 4.52 |

   Hex gốc của BA ghi ngay cạnh từng token trong `_variables.css`. Test khoá **cả hai chiều**: nền phải
   đúng hex BA, chữ phải ≥ 4.5 **và** lệch tông ≤ 12° so với hex BA (mutation M15 hạ về hex BA → đỏ;
   M16 đổi chữ info sang tím → đỏ; mỗi cái đúng 1 test). Báo BA ở retest, không phải xin phép.
6. Hồi quy bắt được khi kiểm chéo: `.wujia-maccount-badgerow` là flex `align-items: stretch`,
   badge 28px kéo chip mã cửa hàng (ngoài phạm vi) 26,8 → 28 ⇒ thêm `align-items: center` + test canh.

## Bằng chứng đo

| Đích | Ngưỡng | Đo được |
|---|---|---|
| Mẫu badge component | > 0 | **96** (5 route × 6 khổ: 1440/1024/992/991/390/360) |
| Cao · min-width · padding · radius | 28 · ≥84 · `0px 14px` · 14 | **96/96 đúng** |
| Font · line-height · nowrap · số dòng | 13/600 · 1 · nowrap · 1 rect | **96/96 đúng** |
| Tràn ngang / ellipsis | 0 | **0** |
| "Đã xác nhận" | info `#EAF7FD` nền BA | **30/30** |
| "Sắp giao" | processing (bậc BA) | **6/6** |
| SB-3 — 5 họ BA loại đổi computed | 0 ô | **0** |
| `wj_measure` 5 route × 5 khổ | 0 lỗi JS · 0 redirect · 0 mất record · 0 đổi chiều cao | **đạt** |
| Ảnh chụp trước/sau `/portal`, `/portal/purchase-history` @1440 + @390 | bố cục không vỡ | **trùng khít** (mobile home 2635px cả hai mốc) |
| Test module bị đụng | 0 đỏ mới so đối chứng | **0 failed, 0 error / 296 test** (+ layout 244) |
| Test guard E2 mới | 9 | **9/9 xanh** |
| Contrast render thực 96 badge | ≥ AA 4.5 | **96/96 đạt · 0 vi phạm** |
| Mutation (phá 1 chỗ → đỏ đúng 1 test) | 16/16 | **16/16**, mỗi mutation đúng 1 test |
| Call site họ cũ trên nhóm màn E2a | 0 (trừ họ BA loại) | **đạt** — chỉ còn Role/Area/Category/mã cửa hàng |

## IMPACT
- `.wj-pc-badge--confirmed` trên purchase-history đổi chữ `#28A9DF` → **`#1378A3`** (hệ màu BA, làm đậm đạt AA).
- Badge mobile ở `/portal` cao 26,8 → **28px**, radius 999 → 14, font 12 → 13 ⇒ hàng dashboard cao thêm ~1px.
- `/portal/delivery`: "Sắp giao" và "Đang giao" **cùng màu processing** vì BA xếp "Chuẩn bị giao" ở bậc
  này; phân biệt bằng **chữ**, đúng luật USAGE của BA ("không truyền đạt trạng thái chỉ bằng màu").
  Trước đây Dev để "Sắp giao" = pending cho dễ phân biệt — đã bỏ theo chỉ đạo "theo BA hết".
- 6 rule ngữ cảnh trong `_components.css` (bảng, hàng dashboard, m-account) nay khớp cả class mới.

## RETEST (đề nghị BA)
1. `/portal` mobile 390 — "Đã xác nhận" phải **xanh dương**, không còn xanh lá.
2. `/portal/purchase-history` PC 1440 + mobile — cùng trạng thái = cùng màu, cùng dáng với `/portal`.
3. `/portal/delivery`, `/portal/franchise-information`, `/portal/profile` — dáng badge đồng nhất.
4. Badge vai trò (Chủ tiệm / Nhân viên), chip khu vực, badge số chưa đọc — **không được đổi**.
5. Xác nhận giúp Dev: 5 màu chữ làm đậm ở LIMIT 1 có chấp nhận được về nhận diện không. Nếu BA muốn
   giữ nguyên hex cũ thì phải bỏ ràng buộc WCAG AA khỏi acceptance — hai điều đó không cùng tồn tại.

## LIMIT
1. `.wj-pc-badge` không xoá được — Khảo sát dùng 9 chỗ, thuộc phạm vi cấm đụng (xem kiểm kê §4).
2. 3 override lệch spec (notification mobile/PC popup, exam PC min-width) **để E2b** kéo về chuẩn chung.
3. 77 call site còn lại ⇒ **issue chưa đóng**; sheet/`qa_sync.py`/deploy làm ở E2b.

## Odoo Fit
Không thêm model/field; không override core. Đúng seam sẵn có: hằng + helper trong
`wujia_portal_base/controllers/utils.py`, template chỉ đọc `t-attf-class`, CSS ở tầng dùng chung
của `wujia_portal_layout`. Bump `__manifest__.py` 6 module + `?v=` của `_variables.css` (1283) và
`_components.css` (1284) trong `assets.xml`; layout `19.0.48.1.0` sau lượt chỉnh contrast.

## Build / Deploy
Chưa deploy. Khi deploy UAT: `-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,`
`wujia_portal_delivery,wujia_portal_sale,wujia_portal_support` (**-u**, không `-i`), restart, hard-refresh.
