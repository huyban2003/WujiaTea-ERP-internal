# Review cụm G trên UAT — 30/09/2026 (chỉ đọc)

**Phạm vi:** G1 (143 · 145 · 144) · G2 (141 · 140) · G3a/b (142) · H150/151 (`WJ-HOME-009/010`). **G4 (146) không review**:
chưa có dòng code nào, dòng 146 đã biến khỏi sheet (session "Wujia issue G4" xác nhận 30/09).

**Môi trường:** `http://113.161.187.126:8019`, DB `wujia_tea_19`, user `em.hcm` (Chủ tiệm HCM-01, 1 cửa hàng). Version UAT
khớp manifest HEAD `ee22cb5` ở cả 6 module: `portal_base` 19.0.7.32.0 · `portal_layout` 19.0.59.1.0 · `portal_sale`
19.0.4.26.0 · `portal_exam` 19.0.6.1.0 · `purchase_history` 19.0.3.20.0 · `portal_debt` 19.0.4.16.0.

**Cách đo:** chạy lại bộ đo có sẵn ở chế độ chỉ đọc (chặn mọi request không phải GET, trừ POST đăng nhập + 2 bộ đếm badge)
⇒ **0 request bị chặn** ở mọi lượt. `wj_density.py` (mobile 26 route × 360/390/430, safe area 0 và 34) · `wj_shell_g2.py` ·
`wj_home_g3.py` (bản chép thêm chặn ghi, để ở scratchpad) · script nhỏ đối chiếu Lịch sử ↔ Home · soát ảnh bằng mắt.

## 1. Kết quả theo AC

| Issue | AC | Đo được trên UAT | KQ |
|---|---|---|---|
| 143 | PageHeader mobile dọc 8, cao 44, title 1 dòng | 26 route × 3 khổ: mọi PH 44, pad 8, 1 dòng, meta không đè | ✅ |
| 143 | SectionHeader mobile 18/24, right slot không đè | mọi SH 18px/24px, `slotHit`/`slotOverflow` = 0 | ✅ |
| 143 | 360/390/430 không tràn ngang | 78/78 ô đo 0 tràn | ✅ |
| 145 | Nav 72 + safe area, mục ~50, nhãn 12 | không SA: 72 · SA 34: 106; mục 50 × 5, nhãn 12, icon 22, 1 mục active | ✅ |
| 145 | Nhóm "Thêm" active đúng, sheet không chồng nav | đáy sheet = mép trên nav: 728/772/860 (SA 0) · 694/738/826 (SA 34) | ✅ |
| 145 | Cuộn cuối thấy và bấm được nút cuối | khoảng hở cuối ≥ 13 ở 78/78 × 2 lượt SA; ảnh form Hỗ trợ/Đổi trả thấy nút gửi trên nav | ✅ |
| 145 | Badge Thông báo không đè icon | nav của `em.hcm` không có badge lúc đo ⇒ đo lại theo G1 §5 (chuông "1" không chạm icon) | LIMIT |
| 144 | `/portal/order`: search → chip 12, chip → list 8, input 44 | 12 / 8 / 44, chip 32 ở cả 3 khổ | ✅ |
| 141 | Dải trên mọi trang mobile shell, kể cả Home | 78/78 có dải cao 48, nhãn "Chủ tiệm" | ✅ |
| 141 | 1 cửa hàng → không chevron (chủ dự án chốt) | 0 chevron ở 78/78 | ✅ |
| 141 | Bấm mọi vị trí mở chọn cửa hàng · nhấn/focus · tên dài | UAT không có user >1 cửa hàng ⇒ không kiểm được; đã đạt trên DB copy (G2 §1) | LIMIT |
| 140 | Icon giỏ/chuông giữa circle 40 (≥1200) | `/portal`, `/portal/order`, `/portal/order/cart` × 1440/1280/1200: lệch tâm (0, 0) | ✅ |
| 140 | Badge không che icon với 0 / 4 / 12 | ∩ icon = 0; số 0 ẩn — 27/27 phép đo PC đạt | ✅ |
| 140 | Chip vai trò nằm trong khối Cửa hàng | đạt 27/27; ảnh 1440 xác nhận | ✅ |
| 142 | Hàng đầu Cửa hàng \| Khung giờ chia đôi | 6 khổ (1440/1280/1200/1199/1024/992): 2 card cao bằng nhau (Δh 0) | ✅ |
| 142 | 4 KPI Đơn hàng · Thông báo · Đổi trả · Công nợ, link đúng | 4/4 ở 6 khổ, href `/portal/purchase-history` · `/notification` · `/return` · `/debt` | ✅ |
| 142 | 7 block, chỉ "Xem tất cả", không mũi tên | 7 block ở 6 khổ; chevron 0; "Xem tất cả" 5 block đúng href; khối cũ 0 | ✅ |
| 142 | Icon đúng loại từng record | đơn `file-text` · đổi trả `corner-up-left` · giao `truck` · thông báo `bell` · bài viết `file-text` · hỗ trợ `headphones/phone-call/message-circle` | ✅ |
| 142 | Không cắt chữ / cuộn ngang ở 1440 · 1024 · 992 | nội dung Home: 0 phần tử bị cắt, 0 tràn ngang ở 6 khổ | ✅ |
| 142 | ↳ nhưng top bar ở **đúng 992** | khối Cửa hàng rớt xuống hàng 2, bị mép header cắt; logo bị đẩy lên (xem §2.1) | ❌ |
| 142 | 991 ra bố cục mobile | khối PC ẩn, mobile hiện | ✅ |
| 142 | Tiền VNĐ / ₫ | Home in `192.050,00 $` — do dữ liệu UAT (xem §2.2), code in đúng tiền của đơn | LIMIT |
| 142 | Home mobile không đổi | ảnh 360 đúng bố cục mobile cũ (hero, Hành động nhanh, 8 SH 18/24) | ✅ |
| 150 | Giờ đơn Home PC đúng múi giờ, giống Lịch sử | S00075: Home PC = Home mobile = Lịch sử = **22:57 29/09/2026** | ✅ |
| 151 | Trạng thái đơn Home giống Lịch sử | S00075/S00072: Home PC + mobile "Chờ xác nhận" = danh sách + chi tiết Lịch sử (PC 1440 và mobile 390) | ✅ |

**Tổng:** 25 dòng · 20 ✅ · 1 ❌ · 4 LIMIT ⇒ 20/21 dòng đo được = **95 %** (ngưỡng §13 là 90 %).

## 2. Phát hiện

### 2.1 ❌ Top bar PC vỡ ở đúng khổ 992 (có từ trước cụm G)

- **Hiện tượng:** ở 992×… khối "Cửa hàng hiện tại" rớt xuống dưới logo + hamburger (`top 34`, header cao 72 ⇒ nửa dưới bị
  cắt), logo bị đẩy lên `top −7`. Gặp ở mọi trang PC (ảnh `/portal`, `/portal/debt`). Đo 993 · 995 · 997 · 999 · 1000 ·
  1010 · 1024 · 1050 · 1100 · 1199: **một hàng, bình thường**.
- **Gốc:** so computed style header giữa 993 và 992, chỉ khác một chỗ: `li.nav-item.mobile-menu.d-xl-none.mr-auto`
  (hamburger) có `margin-right` **0 → 451.7px**. `mr-auto` ăn hết chỗ trống nên khối 430px không còn chỗ trên hàng. Nghi một
  rule Vuexy `@media (max-width: 992px)` (vd `bootstrap-extended.css:2344/2395`) lệch 0,02px so với mốc Bootstrap `991.98`.
- **Không phải hồi quy G2:** G2 (`6745671`) không đổi `width: 430px` / margin của khối; chỉ dời nền lên khối nên chỗ bị cắt
  dễ thấy hơn.
- **Liên quan AC 142:** BA ghi đo ở "1440/1024/992–991"; 992 là một khổ BA nêu tên.
- **Đề xuất:** một lượt nhỏ ở `wujia_portal_layout`: tìm rule 992 làm `mr-auto` bung, sửa mốc hoặc chặn `margin-right` của
  `.mobile-menu` trong top bar; đo lại 991/992/993/1024/1199 + mobile Δ0.

### 2.2 LIMIT — Tiền trên UAT in `$` vì dữ liệu

Bảng giá `Default` trên UAT để **USD** trong khi công ty là **VND** ⇒ mọi đơn portal (S00070/72/75…) lưu USD. Home, Lịch sử,
Đặt hàng, Giỏ đều in `$` nhất quán theo tiền của đơn; Công nợ (hoá đơn VND) in `₫`. G3 §9 ghi "UAT in ₫" là sai với dữ liệu
hiện tại. Không phải lỗi code — cần admin UAT đổi tiền tệ bảng giá `Default` sang VND (chủ dự án quyết, **không** tự sửa).

### 2.3 Quan sát nhỏ, không chặn

- **Ô ngôn ngữ ở 992–1199:** pill rộng 118px chỉ có lá cờ, không có chữ (≥1200 có "Tiếng Việt"). Nhìn như ô trống; ngoài
  phạm vi 140 (≥1200). Hỏi BA có muốn thu pill về cỡ circle 40 ở khổ này không.
- **Mã chuyến giao ở card hẹp 1440:** `BATCH/OUT/0000` + `1` xuống dòng giữa chữ (`overflow-wrap: anywhere`, BA cấm cắt
  chữ nên đây là hành vi đã chốt ở G3b). Có thể giảm bằng cách cho badge xuống dòng thay vì mã — chỉ ghi nhận.
- **Công nợ PC 992:** cột "Thao tác" của bảng hoá đơn bị cắt (bảng cuộn ngang trong card), tiền `118.450 ₫` xuống 2 dòng.
  Ngoài cụm G (màn Công nợ) — ghi để BA biết.

## 3. Việc kế

1. Lượt sửa **top bar 992** (§2.1) — nhỏ, 1 module (`wujia_portal_layout`).
2. Chủ dự án quyết đổi tiền tệ bảng giá UAT (§2.2) trước khi BA retest 142 phần "VNĐ".
3. BA retest 140–145, 142, 150, 151 (sheet đều `Ready for Retest`); 141 phần bấm đổi cửa hàng cần một user nhiều cửa hàng trên
   UAT.
4. G4 (146) chờ BA thêm lại dòng — cách làm đã chốt ở `next-session-clusters-G.md` khối G4.
