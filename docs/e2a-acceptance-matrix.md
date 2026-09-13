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
5. Hồi quy bắt được khi kiểm chéo: `.wujia-maccount-badgerow` là flex `align-items: stretch`,
   badge 28px kéo chip mã cửa hàng (ngoài phạm vi) 26,8 → 28 ⇒ thêm `align-items: center` + test canh.

## Bằng chứng đo

| Đích | Ngưỡng | Đo được |
|---|---|---|
| Mẫu badge component | > 0 | **96** (5 route × 6 khổ: 1440/1024/992/991/390/360) |
| Cao · min-width · padding · radius | 28 · ≥84 · `0px 14px` · 14 | **96/96 đúng** |
| Font · line-height · nowrap · số dòng | 13/600 · 1 · nowrap · 1 rect | **96/96 đúng** |
| Tràn ngang / ellipsis | 0 | **0** |
| "Đã xác nhận" | info `#EAF7FD/#168FC2` | **30/30** |
| "Sắp giao" | processing (bậc BA) | **6/6** |
| SB-3 — 5 họ BA loại đổi computed | 0 ô | **0** |
| `wj_measure` 5 route × 5 khổ | 0 lỗi JS · 0 redirect · 0 mất record · 0 đổi chiều cao | **đạt** |
| Ảnh chụp trước/sau `/portal`, `/portal/purchase-history` @1440 + @390 | bố cục không vỡ | **trùng khít** (mobile home 2635px cả hai mốc) |
| Test module bị đụng | 0 đỏ mới so đối chứng | **0 failed, 0 error / 296 test** (+ layout 244) |
| Test guard E2 mới | 9 | **9/9 xanh** |
| Mutation (phá 1 chỗ → đỏ đúng 1 test) | 14/14 | **14/14**, mỗi mutation đúng 1 test |
| Call site họ cũ trên nhóm màn E2a | 0 (trừ họ BA loại) | **đạt** — chỉ còn Role/Area/Category/mã cửa hàng |

## IMPACT
- `.wj-pc-badge--confirmed` trên purchase-history đổi chữ `#28A9DF` → **`#168FC2`** (số BA chốt).
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

## LIMIT
1. **Contrast**: giữ **đúng hex BA đưa** theo chỉ đạo của chủ dự án. Đo thực tế trên nền đã render,
   5/7 cặp dưới ngưỡng WCAG AA 4.5 cho chữ nhỏ (13px không phải chữ lớn nên ngưỡng 3.0 không áp dụng):

   | Variant | bg / fg | Tỉ lệ đo | AA 4.5 |
   |---|---|---|---|
   | processing | `#FEF3C7` / `#B45309` | 4.51 | ✅ |
   | feedback | `#F3E8FF` / `#7C3AED` | 4.83 | ✅ |
   | neutral | `#F3F4F6` / `#6B7280` | 4.39 | ❌ |
   | danger | `#FEECEC` / `#DC2626` | 4.24 | ❌ |
   | info | `#EAF7FD` / `#168FC2` | 3.35 | ❌ |
   | success | `#EAF8EF` / `#16A34A` | 3.01 | ❌ |
   | pending | `#FFF7E6` / `#D97706` | 2.99 | ❌ |

   ⇒ **Câu hỏi gửi BA** (chưa tự sửa màu): spec vừa yêu cầu "đạt WCAG AA" vừa đưa 7 cặp hex mà 5 cặp
   đo ra dưới 4.5. Dev đang theo hex. BA chọn (a) giữ hex, bỏ ràng buộc AA khỏi acceptance, hay
   (b) cho phép Dev làm đậm chữ mỗi variant tới khi ≥4.5 (nền giữ nguyên, chênh màu rất nhẹ)?
2. `.wj-pc-badge` không xoá được — Khảo sát dùng 9 chỗ, thuộc phạm vi cấm đụng (xem kiểm kê §4).
3. 3 override lệch spec (notification mobile/PC popup, exam PC min-width) **để E2b** kéo về chuẩn chung.
4. 77 call site còn lại ⇒ **issue chưa đóng**; sheet/`qa_sync.py`/deploy làm ở E2b.

## Odoo Fit
Không thêm model/field; không override core. Đúng seam sẵn có: hằng + helper trong
`wujia_portal_base/controllers/utils.py`, template chỉ đọc `t-attf-class`, CSS ở tầng dùng chung
của `wujia_portal_layout`. Bump `__manifest__.py` 6 module + `?v=` của `_variables.css` (1283) và
`_components.css` (1284) trong `assets.xml`.

## Build / Deploy
Chưa deploy. Khi deploy UAT: `-u wujia_portal_layout,wujia_portal_base,wujia_portal_purchase_history,`
`wujia_portal_delivery,wujia_portal_sale,wujia_portal_support` (**-u**, không `-i`), restart, hard-refresh.
