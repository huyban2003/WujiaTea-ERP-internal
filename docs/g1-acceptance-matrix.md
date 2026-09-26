# G1 — Bảng nghiệm thu: mật độ khung mobile (143 · 145 · 144)

**Issue:** `UI-MOB-HEADER-DENSITY-001` (143) · `UI-MOB-BOTTOMNAV-DENSITY-001` (145) · `WJ-ORD-MOB-SPACING-001` (144).
**Phiên:** G1 · 26/09/2026 · Mac. **Module `-u`:** `wujia_portal_layout` 19.0.59.0.0 · `wujia_portal_sale` 19.0.4.26.0 ·
`wujia_portal_exam` 19.0.6.1.0. **Chủ dự án chốt đầu phiên:** PageHeader mobile cả 3 kiểu (title/back/create) cùng cao 44.

**Cách đo:** DB `wujia_g1` = copy `wujia_frp` + replay đúng lệnh `deploy.yml` (RC 0) ⇒ giống UAT. Bộ đo
`scripts/qa/wj_density.py` (Playwright, user `dung.multi` 3 cửa hàng — Staff; `/portal/info-request/new` đo bằng
`anh.owner`). 27 route (20 danh sách/form + 7 chi tiết) × 360×800 · 390×844 · 430×932, có và không có safe area
(CDP `Emulation.setSafeAreaInsetsOverride` bottom 34). PC 1440 · 1024 · 992 so **vân tay bố cục** (hộp + cỡ chữ +
khoảng cách của mọi phần tử đang hiện), trước sửa = `git stash` + `-u` trên cùng DB.

## 1. Kết quả theo issue (đối chiếu cột "Kết quả mong muốn")

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 143 | `/portal/order` PageHeader pad dọc 8 | pad 12 → **8**, cao 52 → **44** (360/390/430) | ✅ |
| 143 | SectionHeader mobile 18/24 | 20/28 → **18/24** ở mọi SectionHeader mobile đang hiện (Home, Đặt hàng, Giỏ, Lịch sử, Đổi trả) | ✅ |
| 143 | Mọi trang dùng component có nhịp gọn, nhất quán | 27/27 route có PageHeader: **44** cả 3 khổ (title pad 8 · back pad 1 · create pad 0) | ✅ |
| 143 | Title/count không đè, không xuống dòng bất thường, không tràn ngang | title 1 dòng, meta/slot không đè title, 0 tràn ngang — 27 route × 3 khổ | ✅ |
| 143 | PC giữ nguyên | vân tay bố cục **76/81 giống**; 5 lệch = bộ đếm lượt xem Kiến thức (icon mắt), lượt đối chứng cùng mã cũng lệch đúng chỗ đó | ✅ |
| 143 | Danh sách route + evidence trước/sau | §2 dưới + ảnh `scratchpad/g1/{before,after}` | ✅ |
| 145 | Thanh 72 + safe area thực tế | 83 → **72**; có safe area 34: 91 → **106** (= 72 + 34) | ✅ |
| 145 | Nhãn 12, mục ~50, icon 22, không tràn | nhãn 11 → **12**, mục **50**, icon 22, rộng mục 72/78/86, 0 tràn | ✅ |
| 145 | Trang nhóm "Thêm" active đúng | Đổi trả, Kiến thức, Hỗ trợ, Thi, Công nợ, Báo cáo, Tài khoản… sáng **Thêm** | ✅ |
| 145 | Badge 1–2 chữ số không đè icon | "8", "12", "44" (thật), "99+": badge nằm ngoài nét chuông ở 3 khổ | ✅ |
| 145 | Cuộn cuối thấy và bấm được nút cuối | 27 route × 3 khổ × có/không safe area: phần tử cuối nằm trên nav ≥ **13** | ✅ |
| 145 | Kiểm có và không có safe area | cả hai; sheet Thêm trước **chồng nav 8px** khi có safe area → nay sát mép (0) | ✅ |
| 144 | search → chip 12, chip → "Danh sách sản phẩm" 8 | 23 → **12**, 14 → **8** ở 360/390/430, giữ nguyên sau lọc AJAX và sau tìm | ✅ |
| 144 | Giữ input 44, chip, vùng bấm, card/nút giỏ | ô tìm 44, chip 32, card/nút giỏ không đổi | ✅ |
| 144 | Tìm/lọc/số lượng/thêm giỏ như cũ | smoke: lọc chip AJAX, tìm, +/− (2→3→2), thêm giỏ (3→4 mặt hàng), 0 lỗi JS | ✅ |
| 144 | Trang khác không đổi vì 144 | rule chỉ dưới `.wujia-morder`; test cấm chạm `.wj-filter-*` chung | ✅ |

## 2. Route × khổ (390; 360/430 cùng số trừ khi ghi) — trước → sau

| Route | Kiểu PH | PH 360/390/430 trước → sau | SH trước → sau | Nav trước → sau (safe 34) | Cuộn cuối: khoảng trên nav (390) | Tràn ngang |
|---|---|---|---|---|---|---|
| `/portal` | — | —/—/— → —/—/— | 20/28 → 18/24 | 83 (91) → 72 (106) | 42 → 42 | không |
| `/portal/order` | title | 52/52/52 → 44/44/44 | 20/28 → 18/24 | 83 (91) → 72 (106) | 84 → 84 | không |
| `/portal/order/cart` | back | 52/52/52 → 44/44/44 | 20/28 → 18/24 | 83 (91) → 72 (106) | 235 → 235 | không |
| `/portal/purchase-history` | title | 52/52/52 → 44/44/44 | 20/28 → 18/24 | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/delivery` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/return` | create | 52/52/52 → 44/44/44 | 20/28 → 18/24 | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/return/new` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 29 → 29 | không |
| `/portal/notification` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/knowledge` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/support` | create | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 328 → 347 | không |
| `/portal/support/new` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 28 → 28 | không |
| `/portal/exam` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 13 → 13 | không |
| `/portal/debt` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 377 → 396 | không |
| `/portal/debt/payment-history` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 377 → 396 | không |
| `/portal/debt/pay` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 377 → 396 | không |
| `/portal/info-request` | create | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 679 → 679 | không |
| `/portal/info-request/new` ¹ | back | — → 44/44/44 | — → — | — → 72 | — → 41 | không |
| `/portal/reports/orders` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 31 → 31 | không |
| `/portal/profile` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 201 → 220 | không |
| `/portal/change-password` | title | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 226 → 245 | không |
| `/portal/order/product/4` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 26 → 26 | không |
| `/portal/purchase-history/653` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 37 → 37 | không |
| `/portal/delivery/162` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 134 → 153 | không |
| `/portal/return/123` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 26 → 26 | không |
| `/portal/notification/20` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 237 → 256 | không |
| `/portal/knowledge/seed-e3-bài-viết-mẫu-số-01` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 356 → 375 | không |
| `/portal/info-request/16` | back | 52/52/52 → 44/44/44 | — → — | 83 (91) → 72 (106) | 338 → 356 | không |

¹ 403 với Staff `dung.multi` ⇒ chỉ đo sau sửa bằng `anh.owner` (Owner).
Khoảng "cuộn cuối" tăng ở trang ngắn (vd 328 → 347) vì nav thấp đi 11 — không phải lệch.

## 3. Bằng chứng khác

- **Suite** 21 module (14 portal + 7 L2) `-u … --test-enable` trên DB copy: **930 / 0 failed / 0 error** (914 + 16 test G1).
- **Mutation** 11/11 đỏ đúng test (`scratchpad/g1/mutate.py`): pad 12 · back pad 5 · `--any` 18 ra ngoài @media · nav 83 ·
  nav `min-height` · nhãn 11 · sheet bám `-height` · exam bám `-height` · margin search 15 · rule chạm `.wj-filter-chips` · SH `--m` 20.
- **`check_layers`**: 0 vi phạm Dev (R7 còn 2 của `wujia_franchise`, có từ trước).
- **Log `-u`**: RC 0. Các dòng ERROR trong log đều là `FileNotFoundError` do bản copy `wujia_frp` không kèm filestore (dữ liệu, không do code);
  bundle JS 500 vì cùng lý do ⇒ xoá attachment `/web/assets/%` trên DB copy rồi đo lại với JS chạy — số không đổi.

## 4. Ngoài phạm vi / LIMIT

- Back/create pad 1/0 (không phải 8) — chủ dự án chốt cùng cao 44; khoảng thở thật do nút 42/44 lấp.
- Safe area đo bằng giả lập Chromium, chưa trên iPhone thật.
- 145 đi ngược ghi chú "BA final 83px" (Sprint 12) — theo issue mới (Need confirm = No), FYI BA.
- Khảo sát (`wujia_portal_inspection`) không khai `ph_platform` ⇒ không ăn `--m`, không đụng (code anh Thái).

## 5. Đo UAT chỉ-đọc (26/09/2026, sau deploy `fcce811`)

`http://113.161.187.126:8019` · `em.hcm` (Owner HCM-01) · `wj_density.py --readonly`: chặn mọi request không phải GET, chỉ cho
qua POST đăng nhập + 2 bộ đếm badge (`/portal/notification/unread-count`, `/portal/order/cart/count` — soi controller: chỉ
đọc) ⇒ **0 request bị chặn**, không lỗi kịch bản. Không thử thêm giỏ/đổi số lượng trên UAT (smoke đã chạy trên DB copy).

| Kiểm | Kết quả UAT |
|---|---|
| Mobile 26 route × 360/390/430, không safe area | PH 44 (title/back/create), SH 18/24, nav 72 · mục 50 · nhãn 12, cuộn cuối ≥13, 0 tràn — 1 lệch: Giỏ hàng @360 PH 100 (title 2 dòng) **1 lần**, đo lại 3 lượt đủ + 6 lần tải lại @360 đều 44 / 1 dòng ⇒ thoáng qua |
| Mobile 26 route × 3 khổ, safe area 34 | **0 lệch**: nav 106, sheet "Thêm" đáy = nav top (694/738/826) |
| `/portal/order` | search → chip **12**, chip → list **8**, input 44, chip 32 ở 3 khổ |
| Badge | chuông "1" không chạm lõi icon |
| PC 20 route × 1440/1024/992 | không nav mobile, PH `pc` 64, SH `--pc` 22/30 (`_pc_components.css:446`, G1 không đụng), 0 tràn ngang |

Không có vân tay PC trước-deploy trên UAT ⇒ PC Δ0 dựa vào số đo DB copy (§1) + các số tuyệt đối trên.
