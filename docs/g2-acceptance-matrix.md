# G2 — Bảng nghiệm thu: dải cửa hàng mobile + top bar PC (141 · 140)

**Issue:** `UI-MOB-STORE-SWITCHER-001` (141) · `UI-PC-TOPBAR-REG-001` (140).
**Phiên:** G2 · 29/09/2026 · Mac. **Module `-u`:** `wujia_portal_base` 19.0.7.29.0 · `wujia_portal_layout` 19.0.59.1.0
(`wujia_portal_sale` không đụng). **Chủ dự án chốt đầu phiên:** (a) user 1 cửa hàng → **ẩn chevron**, dải tĩnh ·
(b) nhãn vai trò **tiếng Việt một nguồn** (`ROLE_LABELS`: Chủ tiệm / Quản lý / Nhân viên) ở mọi chỗ in vai trò, mobile
lẫn PC · (d) **hiện dải cả trên Home** theo mockup · (e) theo 140: chip vai trò nằm trong khối, FYI BA mockup V4 vẽ tách.

**Cách đo:** DB `wujia_g2s` = copy `wujia_g1` (đã replay `deploy.yml` ở G1) + `-u` 2 module. Bộ đo
`scripts/qa/wj_shell_g2.py` (Playwright) với `dung.multi` (3 cửa hàng, Nhân viên) và `anh.owner` (1 cửa hàng, Chủ tiệm).
Mobile 27 route × 360×800 · 390×844 · 430×932; PC `/portal` · `/portal/order` · `/portal/order/cart` × 1440 · 1280 ·
1200, badge gán 0/4/12 trên DOM y như JS thật (0 ⇒ `hidden`), không đụng giỏ thật. Kênh bên kia so **vân tay bố cục**
`wj_density.py` trước/sau trên cùng DB. Số "trước" lấy trước khi sửa code (`before_multi.json`).

## 1. Kết quả theo issue (đối chiếu cột "Kết quả mong muốn")

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 141 | Dải giống mockup: `[mã] Tên — [vai trò] — chevron-down` | chip mã · tên đậm · pill "Nhân viên"/"Quản lý"/"Chủ tiệm" viền · chevron xanh `--wujia-primary`, mép phải = W − 16 (344/374/414), giữa dọc dải 48 | ✅ |
| 141 | Bấm mọi vị trí trong vùng mở chọn/chuyển cửa hàng | bấm mã, tên, vai trò, chevron: **4/4 mở** overlay `#wujiaStoreOverlay`; cả dải là một thẻ `<a>` | ✅ |
| 141 | Có trạng thái nhấn / focus | nhấn: nền trắng → `rgb(224,247,255)`; focus bàn phím: viền 2px liền màu chính | ✅ |
| 141 | Chevron không lệch / tràn | 27 route × 3 khổ: chevron 20×20, cùng toạ độ mọi trang, 0 tràn ngang | ✅ |
| 141 | Tên dài không làm mất vai trò / chevron | tên cửa hàng dài: tên co lại 121/151/191 + "…", vai trò + chevron giữ nguyên chỗ, 0 tràn | ✅ |
| 141 | 360/390/430, mọi trang dùng mobile shell | 26/27 route có dải cả 3 khổ (thêm **Home**, trước bị ẩn); route thứ 27 `/portal/info-request/new` trả 403 cho Nhân viên cả trước lẫn sau — `anh.owner` đo được, có dải | ✅ |
| 141 | Không đổi dữ liệu / quyền | chỉ QWeb + CSS; chỉ user >1 cửa hàng mới bấm được (như cũ); user 1 cửa hàng: `<div>` tĩnh, **không chevron** (quyết định a) | ✅ |
| 141 | PC không đổi vì 141 | dải `d-lg-none`; vân tay PC chỉ lệch ở vùng 140 sửa (§3) | ✅ |
| 140 | Icon giỏ + chuông nằm giữa circle 40×40 | lệch tâm **(−9.4, −9.5) → (0, 0)** (±0.1) ở 1440/1280/1200 × 3 route | ✅ |
| 140 | Cỡ / nét đồng nhất | 21/21 → giỏ **19**, chuông **20** (bù khác biệt khung glyph feather), cùng màu trắng | ✅ |
| 140 | Badge neo trên-phải, không che icon, không tràn với 0 / 4 / 2 chữ số | badge ∩ hộp icon: "12" **59.4 px² → 0**, "4" 0 → 0; số 0: badge ẩn; badge nằm trong mép phải header | ✅ |
| 140 | Current Store là một block, chip vai trò trong block | khối 430×48 có nền `rgba(255,255,255,.18)` bo 10 (trước: trong suốt, chỉ pill 318 có nền ⇒ chip lơ lửng bên ngoài); chip 614–696 nằm trong khối 288–718; hover tô cả khối, không còn "pill trong pill" | ✅ |
| 140 | Tên dài ellipsis | tên dài: "…", chip vai trò giữ nguyên chỗ ở 1440/1200 | ✅ |
| 140 | Không đổi click target, số lượng giỏ, account / language | thẻ bấm không đổi (vẫn `<a data-action="open-store-picker">` trong khối, circle 40×40 cũ); logic `hidden`/`is-active` của badge không đụng; menu tài khoản / ngôn ngữ chỉ đổi chữ vai trò sang tiếng Việt | ✅ |
| 140 | Mobile không đổi vì 140 | sửa nằm trong `@media (min-width: 1200px)`; test cấm đụng `.wujia-header-badge` gốc (8 module + header mobile dùng); vân tay mobile Δ0 ngoài dải 141 | ✅ |

**15/15 ý đạt.**

## 2. Route × khổ

### 2a. Mobile (141) — 360/390/430, sau sửa

| Route | Trước (`dung.multi`, mẫu 3 route) | Sau `dung.multi` (3 cửa hàng) | Sau `anh.owner` (1 cửa hàng) |
|---|---|---|---|
| `/portal` | Staff · không chevron · 0 tràn | `a` · Nhân viên · chevron 344/374/414 · 0 tràn | `div` · Chủ tiệm · không chevron · 0 tràn |
| `/portal/order` | Staff · không chevron · 0 tràn | `a` · Nhân viên · chevron 344/374/414 · 0 tràn | `div` · Chủ tiệm · không chevron · 0 tràn |
| `/portal/notification` | Staff · không chevron · 0 tràn | `a` · Nhân viên · chevron 344/374/414 · 0 tràn | `div` · Chủ tiệm · không chevron · 0 tràn |
| 23 route khác ¹ | — | `a` · Nhân viên · chevron 344/374/414 · 0 tràn | `div` · Chủ tiệm · không chevron · 0 tràn |
| `/portal/info-request/new` | 403 (Nhân viên) | 403 (Nhân viên) | `div` · Chủ tiệm · không chevron · 0 tràn |

¹ `/portal/order/cart` · `/portal/purchase-history` · `/portal/delivery` · `/portal/return` · `/portal/return/new` ·
`/portal/knowledge` · `/portal/support` · `/portal/support/new` · `/portal/exam` · `/portal/debt` ·
`/portal/debt/payment-history` · `/portal/debt/pay` · `/portal/info-request` · `/portal/reports/orders` ·
`/portal/profile` · `/portal/change-password` + 7 trang chi tiết (sản phẩm, đơn mua, giao hàng, đổi trả, thông báo,
bài viết, yêu cầu thông tin). Chi tiết của `anh.owner` lấy theo dữ liệu của user đó (`/portal/purchase-history/1799`,
`/portal/return/464`). Số từng ô: `scratchpad/g2/shell_after_{multi,single}.json`.

### 2b. PC (140) — `/portal`, `/portal/order`, `/portal/order/cart`

| Khổ | Lệch tâm icon giỏ / chuông trước → sau | Badge ∩ icon "4" / "12" trước → sau | Số 0 | Chip vai trò trong khối | Nền khối | Mobile Δ0 |
|---|---|---|---|---|---|---|
| 1440 | (−9.4, −9.5) → (0, 0) | 0 / 59.4 → 0 / 0 | ẩn | ngoài → **trong** | trong suốt → .18 | ✅ |
| 1280 | (−9.4, −9.5) → (−0.1, 0) | 0 / 59.4 → 0 / 0 | ẩn | ngoài → **trong** | trong suốt → .18 | ✅ |
| 1200 | (−9.4, −9.5) → (−0.1, 0) | 0 / 59.4 → 0 / 0 | ẩn | ngoài → **trong** | trong suốt → .18 | ✅ |

Cả 3 route cho cùng số ở mỗi khổ (27 phép đo × 2 user, 0 lỗi). 992–1199: khối cũng có nền (rule khối không nằm trong
`@media ≥1200`), circle giỏ/chuông ở khổ đó không đổi.

## 3. Kênh bên kia Δ0 (vân tay bố cục `wj_density.py`, trước/sau cùng DB)

- **PC 81 route × khổ**: 78 lệch **chỉ** ở nền khối Cửa hàng, nền pill và chữ vai trò dưới avatar (Staff → Nhân viên);
  3 còn lại là `/portal/info-request/new` (403 với Nhân viên) nên giống hệt. Id ngẫu nhiên của apexcharts là nhiễu nền (lượt đối chứng cùng mã cũng lệch).
- **Mobile**: PageHeader, SectionHeader, nav dưới, khoảng cuộn cuối **Δ0**; chỉ dải cửa hàng đổi (chevron, chữ vai trò,
  thêm dải trên Home).

## 4. Gốc rễ (140)

- **Icon lệch**: commit cụm B `157814a` (04/08) dựng circle 40×40 trong `_pc_account.css` nhưng không khai lại
  `display`. `.wujia-header-icon-btn { display: inline-flex }` (`_components.css`) thua `.nav-link { display: block }` của
  `web.assets_frontend` vì bundle Odoo nạp **sau** CSS của mình ⇒ circle thành `block`, icon dồn góc trên-trái, và badge
  "12" đè nét icon 59 px². Vá: circle ≥1200 tự khai `inline-flex` + căn giữa.
- **Cỡ icon**: Vuexy `.header-navbar .navbar-container ul.nav li i.ficon { font-size: 1.5rem }` có specificity (0,4,3) ⇒
  selector cỡ icon phải cao hơn (`.wujia-navbar .navbar-container ul.nav li… > i.icon-*`).
- **Chip vai trò lơ lửng**: từ UI-01, nền nằm trên pill `<a>` (318) còn chip là anh em bên phải (x 614) ⇒ nhìn như 2
  khối. Vá bằng CSS: nền chuyển lên `.wujia-store-current-block`, pill trong suốt; **DOM và vùng bấm không đổi**.

## 5. Bằng chứng khác

- **Suite** 20 module (7 L2 + 13 portal) `-u … --test-enable`: **941 / 0 failed / 0 error** (930 + 11 test G2:
  tag `wujia_store_switcher_g2`, `wujia_pc_topbar_g2`).
- **Mutation** 9/9 đỏ đúng test (`scratchpad/g2/mutate.py`): bỏ chevron · nhãn Anh ở dải · nhãn Anh ở hero Home ·
  chevron cho user 1 cửa hàng · bỏ nền khối · trả `capitalize` · bỏ `inline-flex` circle · badge về top 2 · selector cỡ icon
  yếu hơn Vuexy.
- **`check_layers`**: 0 vi phạm Dev (R7 ×2 của `wujia_franchise`, có từ trước); `portal_base` không thêm depend.
- Ảnh trước/sau: `scratchpad/g2/{before,after}_{pc,m}.png`, tên dài `afterlong_{m,pc,pc1200}.png`, 1 cửa hàng `after1_{m,pc}.png`.

## 6. Ngoài phạm vi / LIMIT

- Mockup V4 (142) vẽ pill vai trò **tách ngoài** khối — làm theo 140 (trong khối), FYI BA.
- Nhãn vai trò đổi sang tiếng Việt ở **5 chỗ**: dải mobile, khối PC, chữ dưới avatar PC, menu tài khoản, hero Home mobile.
  Giao diện EN/ZH vẫn thấy tiếng Việt ở các nhãn này (một nguồn, chưa dịch).
- User 1 cửa hàng: dải không có chevron, không bấm được (không có gì để chuyển).
- Trạng thái nhấn/focus đo bằng ép pseudo-class (CDP), chưa bấm trên máy thật.
- Chưa đo UAT — chờ deploy, rồi chạy `wj_shell_g2.py --readonly`.
