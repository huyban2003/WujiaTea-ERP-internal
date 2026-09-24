# E7b — Ma trận nghiệm thu · PageContainer `CMP-PC-001` (width + bottomInset, khép issue)

Lượt cuối cụm **E7** (`UI-PAGECONTAINER-001`, STT 129, dòng sheet 122). E7a (`8ef3081`) đã dựng khung +
gutter; E7b thêm **bề rộng `fluid / standard 1440 / narrow 960`** và **đáy `stickyAction`**, rồi đối chiếu
đủ 13 tiêu chí BA. Issue lên **Ready for Retest sau khi E7a + E7b deploy UAT** và đo lại chỉ-đọc.

- Spec: tab `UI Component` gid `488333015` dòng 38 (BA Confirmed 26/08/2026) — cột mapping route.
- Đo: DB local `wujia_e4b1`, server **8090** (không `--dev=xml`), test **8098**, login `em.hcm`.
- Không đổi quyền / controller / dữ liệu / workflow — chỉ template khung, cờ `t-set`, CSS, sổ test, thước đo.

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `layouts.xml` (`app_layout`) | `<main>` nhận thêm 2 công tắc cùng kiểu `pc_gutter`: `pc_width` = `standard`/`narrow` (fluid = không đặt) → `wj-page-container--standard/--narrow`; `pc_bottom='sticky'` → `wj-page-container--sticky`. **Không thêm lớp DOM** |
| `_variables.css` | `--wj-page-width-standard` 1440 · `--wj-page-width-narrow` 960 · `--wj-sticky-action-h` 68 · `--wj-sticky-action-gap` 16 |
| `_wujia_theme.css` | `max-width: calc(width + 2 × gutter)` + `margin: auto` **trên chính container** ⇒ PageHeader và nội dung chung một bề rộng trong; `--sticky` (<992) đáy = `mnav-total + sticky-action-h + gap` |
| `portal_order.css` | gỡ `.wj-pc-cart-standalone {max-width:760}`, gỡ đáy riêng `.wujia-morder` (150 + safe) và `.wujia-mcart` (nav + 116); thanh tóm tắt giỏ khai chiều cao của nó cho container qua `:has()` (200); floatbar + thanh tóm tắt dùng token `--wj-page-gutter-m` thay số 16 |
| 29 template | cờ theo mapping BA (bảng dưới) |
| `assets.xml` | `?v=1319` · bump **13 module** |

### Mapping (cột mapping BA)

| Biến thể | Template |
|---|---|
| **fluid** (mặc định) | Home, Đặt hàng (catalog), Lịch sử, Giao hàng, Công nợ (tổng quan + lịch sử TT), Thông báo, Kiến thức, Hỗ trợ, Lịch thi + Đăng ký thi, Khảo sát, YC cập nhật thông tin (danh sách), Báo cáo đơn |
| **standard 1440** | Bù hàng (danh sách + chi tiết), Tài khoản, Đổi mật khẩu, Thông tin/hồ sơ cửa hàng (5 template), mọi màn chi tiết (hỗ trợ, kiến thức, YC thông tin, kết quả đăng ký thi, sản phẩm, thông báo, đơn đã đặt, lô giao hàng, Khảo sát chi tiết + khắc phục), Thanh toán công nợ, Công nợ không có quyền, kết quả gửi đơn (2) |
| **narrow 960** | Giỏ hàng, Tạo bù hàng, Tạo yêu cầu hỗ trợ, Tạo YC cập nhật thông tin |

`standard` chỉ thực sự thu hẹp khi viewport ≥ **1788** (1440 + sidebar 300 + 2 × 24) — ở mọi khổ BA đo nó
**không đổi gì**, đúng câu "không làm hẹp tại viewport thông thường".

## Bảng nghiệm thu — 13 tiêu chí BA

| # | Tiêu chí | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Mọi route đúng một CMP-PC-001 | PC-1 | ✅ 217/217 ô (E7a) — không đổi |
| 2 | Gutter 24 PC/tablet · 16 mobile | PC-2 (nay đo từ mép container) | ✅ 0 vi phạm |
| 3 | Không 30,8 / 14 / vw | PC-3 | ✅ 0 |
| 4 | Header/Filter/Section/Card/List cùng trục | PC-4 | ✅ 0 — kể cả màn narrow căn giữa |
| 5 | Title mobile x=16, desktop sau gutter 24 | `titleX` | ✅ 16 (12 màn danh sách, chốt LC-08) · 24 |
| 6 | fluid 100% · standard ≤1440 · narrow ≤960 | **PC-8 mới**: bề rộng trong = min(chỗ trống, 1440/960), căn giữa, khối đầu nằm trong | ✅ 0 vi phạm. Narrow: 944 @992 · **960** @1024/1440/1920 (lệch trái = phải: 8 · 66 · 306). Standard: 1092 @1440, **1440** @1920. Fluid 1572 @1920 |
| 7 | Không narrow cho màn dữ liệu dày; số cột/record không giảm | `--diff` trước/sau 31 route × 7 khổ + guard `test_khong_narrow_cho_man_danh_sach` | ✅ **0 ô mật độ giảm** (có cả 1920) · `wj_measure` 0 ô mất record |
| 8 | Nền #F3F6F8, container trong suốt | PC-7 | ✅ |
| 9 | Không scroll ngang 1440/1024/992/991/390/360 | PC-5 | ✅ 0 (+1920) |
| 10 | BottomNav/sticky không che; bottom 96 + safe | PC-6 + đo thanh sticky (`scratchpad/e7b/sticky_probe.py`) | ✅ xem *Đáy* dưới |
| 11 | Zoom 200%, sidebar mở/đóng, VI/EN/ZH, trạng thái, quyền | khổ 720 + `--collapsed` 992/1024/1440/1920 | ✅ 0 · 0. VI/EN/ZH + trạng thái rỗng/lỗi: container không đổi chữ — đã đo ở E6c (nhãn dài) |
| 12 | Khảo sát về cùng PageContainer | vỏ E7a + `standard` cho chi tiết/khắc phục | ✅ local (danh sách). Chi tiết/khắc phục: DB local 0 phiếu ⇒ **đo trên UAT sau deploy** |
| 13 | Trước/sau: mật độ không giảm, khoảng trắng chỉ tăng khi cần | diff chiều cao | ✅ bảng dưới |

Ngoài bảng BA: suite **756 tests, 0 đỏ** (mốc E7a 746, +10) · mutation **10/10 đỏ** (`scratchpad/e7b/mutate.py`) ·
`wj_button` 0 · `wj_listcard` 0 · `wj_filterbar` ĐẠT · `wj_nesting` 0 · `b4_regression` **286/286** ·
`check_layers` không thêm vi phạm (3 R3/R4 + 2 R7 có sẵn, không module nào đổi depends) · `test_ownership` cross 0.

## Đáy (bottomInset)

| Màn · khổ | Đáy container trước → sau | Cách thanh gần nhất | Ghi chú |
|---|---|---|---|
| Đặt hàng 360/390 | 96 + **150 riêng** = 246 → **167** | 103,5 → 24,5 | floatbar 59,5 nằm 8 trên nav; trang **ngắn đi 79px** |
| Giỏ hàng 360/390 | 96 + **nav + 116 riêng** = 295 → **299** | 56,5 → 60,5 | thanh tóm tắt 174,5 (4 dòng gồm Thuế); ca có thêm gợi ý ngoài giờ (+25) vẫn còn ~35 |
| mọi màn khác | 96 + safe | — | không đổi |

Hai màn này trước đây chừa đáy **chồng** lên đáy của container (tự cộng thêm). Nay chỉ container chừa đáy.

## Chiều cao / bề rộng đổi

| Route · khổ | Δ | Vì sao |
|---|---|---|
| `/portal/order` 360/390/991 | −79 | bỏ đáy 150 chồng |
| `/portal/order/cart` mobile | +4 | 295 → 299 (token 200 + gap 16 + nav 83) |
| Giỏ hàng PC | card **760 → 960** | gỡ max-width riêng của route, dùng narrow 960 theo spec (IMPACT 1) |
| 4 màn narrow ≥1024 | nội dung 976/1092 → **960**, căn giữa | narrow theo spec (IMPACT 2) |
| `/portal/order/product/4` @1920 | −22 | standard 1440 thay vì 1572 — ảnh sản phẩm co theo |

## IMPACT (báo BA)

1. **Giỏ hàng PC rộng ra 760 → 960** và **căn giữa** vùng nội dung (trước dính trái).
2. **Tạo bù hàng / Tạo yêu cầu hỗ trợ / Tạo YC cập nhật thông tin**: ở PC ≥1024 form thu về 960 căn giữa
   (trước trải hết bề ngang: 976 ở 1024, 1092 ở 1440). Tiêu đề + nút quay lại đi cùng form.
3. Ở màn ≥1788 (ví dụ 1920) các màn `standard` thu về 1440 căn giữa; màn dữ liệu dày vẫn trải hết.
4. Đặt hàng mobile: khoảng trắng cuối trang bớt 79px.

## LIMIT

1. **Khảo sát chi tiết/khắc phục** chưa đo sống (DB local 0 phiếu) — đo trên UAT sau deploy, chỉ đọc.
2. **Chiều cao thanh sticky là số khai báo** (`--wj-sticky-action-h`: 68 floatbar · 200 tóm tắt giỏ) chứ không đo
   tự động; nếu thêm dòng vào thanh tóm tắt giỏ phải chỉnh token. Thanh giỏ khai qua `:has()` (Chrome 105+,
   Safari 15.4+); trình duyệt cũ hơn rơi về 68 ⇒ dòng cuối giỏ có thể nằm dưới thanh.
3. Nút tròn nổi **Đăng ký thi** (màn Lịch thi) nằm góc phải trên nav, không phải thanh ngang ⇒ giữ đáy mặc định.
4. Đệm đỉnh mobile vẫn 10 (LIMIT 1 E7a — token nhịp dọc 18/09).

## Guard + mutation

| Guard | Mutation (phá) | Kết quả |
|---|---|---|
| `test_so_width_khop_mapping_ba` | giỏ bỏ `narrow` | 🔴 |
| `test_chi_so_width_dat_pc_width` | Home đặt `standard` | 🔴 |
| `test_khong_narrow_cho_man_danh_sach` (+2) | danh sách Bù hàng đổi `narrow` | 🔴 |
| `test_khong_khai_be_rong_trang_trong_css_route` | trả `.wj-pc-cart-standalone {max-width:760}` | 🔴 |
| `test_khong_route_tu_chua_day_bottom_nav` | trả `.wujia-morder` đáy 150 | 🔴 |
| `test_man_co_thanh_co_dinh_bat_sticky` | catalog bỏ `pc_bottom` | 🔴 |
| `test_token_width` | narrow 960 → 1024 | 🔴 |
| `test_width_tren_chinh_container` | narrow bỏ `margin-left:auto` | 🔴 |
| `test_day_sticky_mobile` | đáy sticky bỏ token nav | 🔴 |
| `test_bien_the_width_va_day_qua_co` | `app_layout` bỏ class width | 🔴 |

**10/10 đỏ**, khôi phục xong xanh lại.

## Bàn giao anh Thái — `wujia_portal_inspection`

Chỉ thêm 1 dòng `<t t-set="pc_width" t-value="'standard'"/>` vào template chi tiết và khắc phục (không đổi
logic). Nếu anh tạo màn mới: đặt bề rộng bằng `pc_width`, không khai `max-width` trên vỏ route — guard
`test_khong_khai_be_rong_trang_trong_css_route` sẽ đỏ.

## Việc sau

- Chủ dự án deploy **E7a + E7b cùng lượt** (13 module `-u`) → đo UAT chỉ-đọc (`wj_pagecontainer` 31 route ×
  6 khổ + Khảo sát chi tiết) → ledger + `qa_sync` ⇒ **Ready for Retest**.
- **E8** SidebarNavigation (`UI-SIDEBAR-001`); sau E8 phiên phân cụm STT 140–145.
