# E7a — Ma trận nghiệm thu · PageContainer `CMP-PC-001` (khung + gutter)

Lượt đầu cụm **E7** (`UI-PAGECONTAINER-001`, STT 129, dòng sheet 122). E7a dựng **một** lớp khung nội dung
dùng chung cho mọi route portal và tước lề khỏi các vỏ route; **E7b** làm width variant
`fluid / standard 1440 / narrow 960` rồi mới đóng issue ⇒ issue **giữ `Ready for Dev`** tới hết E7b.

- Spec nguồn: tab `UI Component` gid `488333015` dòng 38, `BA Confirmed` 26/08/2026.
- Đo: DB local `wujia_e4b1`, server **8090/8091** (không `--dev=xml`), test **8098/8099**, login `em.hcm`.
- Thước đo mới `scripts/qa/wj_pagecontainer.py`: **31 route** (14 route BA + 17 route phụ, gồm màn chi tiết
  dò động) × **6 khổ** 360/390/991/992/1024/1440, cờ `--collapsed` (sidebar thu gọn), `--breakpoints 720`
  (zoom 200%), `--diff TRƯỚC SAU`.
- Không đổi quyền / controller / dữ liệu / workflow — chỉ template khung, class, CSS, sổ test, thước đo.

Chốt đầu phiên của chủ dự án (24/09):
1. **E7a trước, phân cụm sau** — 6 issue mới STT 140–145 để một phiên phân cụm riêng sau E8; 143
   (`UI-MOB-HEADER-DENSITY-001`) và 145 (`UI-MOB-BOTTOMNAV-DENSITY-001`) phải **đo lại sau khi có khung**.
2. **Sửa tối thiểu vỏ Khảo sát** (code anh Thái): chỉ bỏ lề + nền trắng của vỏ, không đụng logic — xem
   mục *Bàn giao anh Thái*.
3. **Lề mobile: danh sách 12, còn lại 16** — mặc định 16 theo spec, màn danh sách bật biến thể `list` = 12
   (giữ LC-08 đã chốt ở E5).

## Phạm vi đã làm

| Nơi | Thay đổi |
|---|---|
| `wujia_portal_layout/views/layouts.xml` (`app_layout`) | `<main class="wj-page-container">` bọc đúng `<t t-out="0"/>`; header mobile, dải bóng navbar, sidebar, bottom-nav nằm **ngoài** (Global Shell). Biến thể `wj-page-container--list` bật bằng `<t t-set="pc_gutter" t-value="'list'"/>` |
| `_variables.css` | 4 token: `--wj-page-gutter` 24 · `--wj-page-gutter-m` 16 · `--wj-page-gutter-m-list` = `--wujia-mshell-content-pad-x` (12) · `--wj-page-pad-bottom` 32 |
| `_wujia_theme.css` | Rule container duy nhất: PC pad-top token · gutter 24 · đáy 32 · ≥992 chừa top bar 72; <992 gutter 16 (list 12) · đáy `96 + env(safe-area-inset-bottom)`; nền trong suốt. `.content-wrapper` về **0 ở mọi khổ** (thay mốc 24px chỉ ở ≥1200 — gốc lề 30,8 của tablet) |
| `_components.css` | bỏ padding `.wujia-mpage`, bỏ `padding-bottom: 96px` trên `.app-content` (đáy nay thuộc container) |
| Công nợ · Home · store picker | bỏ lề riêng `.wj-debt` / `.wj-debt--back`, `.wujia-mhome`, `.wujia-home-wrapper`; xoá rule chết `.wujia-store-mobile-strip + .content-wrapper` |
| 12 template danh sách | bật `pc_gutter='list'`: Đặt hàng (catalog) · Lịch sử · Bù hàng · Giao hàng · Công nợ (tổng quan + lịch sử TT) · Thông báo · Kiến thức · Hỗ trợ · Lịch thi · YC cập nhật thông tin · Báo cáo đơn |
| Khảo sát (tối thiểu) | xem *Bàn giao anh Thái* |
| `assets.xml` | `?v=1318` cho 3 file CSS khung · bump version **14 module** |

`pc_account_layout` (3 màn Tài khoản PC) là partial nằm **trong** `app_layout` ⇒ đã được container bọc, không
cần vỏ riêng.

## Bảng nghiệm thu — theo `Kết quả mong muốn` của BA

| # | Gạch của BA | Phép đo | Kết quả |
|---|---|---|---|
| 1 | PageContainer là component dùng chung, **sở hữu duy nhất** gutter | `wj_pagecontainer` PC-1/PC-3 + `test_mot_container_boc_noi_dung_route`, `test_arch_ghep_van_mot_container` | ✅ **186/186 ô đúng 1 container** (trước: 0) · chuỗi cha chỉ còn container giữ lề |
| 2 | PageHeader/Filter/Section/Card/List **thẳng một trục** | PC-2/PC-4: x của 5 phần tử đầu so với mép `.app-content` | ✅ 0 vi phạm. Trước: 168/186 ô tiêu đề lệch trục (rule 16px của Khảo sát rò ra mọi màn — xem IMPACT 1) |
| 3 | Gutter **24 PC/tablet · 16 mobile**; hết **30,8 / 14 / double** | phân bố x đo được | ✅ Trước: PC 24×30 · **30,8×60** · 0×3 · 316×3; mobile 12×90 · **0×3**. Sau: PC **24×93**; mobile **16×57** · **12×36** (biến thể list, chốt 2) |
| 4 | Không scroll ngang | PC-5 `scrollWidth == innerWidth` | ✅ 0 ô tràn · `wj_measure` 0 tràn |
| 5 | Không bị BottomNav/sticky che nội dung | PC-6 + đáy mobile `96 + safe-area` | ✅ 0 vi phạm · xem LIMIT 2 (sticky action) |
| 6 | Nền trang `#F3F6F8`, container trong suốt, không `overflow-x:hidden` che lỗi | PC-7 + `test_container_tang_goc` | ✅ |
| 7 | Test **1440 · 1024 · 992/991 · 390 · 360 + zoom 200%** | 31 route × 6 khổ + khổ 720 + sidebar thu gọn (992/1024/1440) | ✅ **0 vi phạm · 0 lỗi JS** ở cả 3 lượt |
| 8 | **Số cột/record nhìn thấy không giảm** | `--diff` trước/sau + `wj_measure` trước/sau | ✅ `wj_measure` **0 ô mất record**. `wj_pagecontainer` báo 2 ô (Công nợ › Lịch sử TT @360/390) — xem LIMIT 3, không phải mất thật |
| 9 | Ưu tiên migrate màn Khảo sát | danh sách · chi tiết · khắc phục | ✅ vỏ về container (tối thiểu, không đổi logic) |
| 10 | Width `fluid/standard/narrow` | — | ⏭ **E7b** |

Ngoài bảng BA: suite **746 tests, 0 đỏ** (mốc E6c 729, +17) · mutation **13/13 đỏ** · `wj_button` **0** ·
`wj_listcard` **0** · `wj_filterbar` **ĐẠT** · `wj_nesting` **0** · `b4_regression` **286/286** ·
`check_layers` chỉ 2 R7 có sẵn (mã anh Thái), không thêm · ảnh sau: `scratchpad/e7a/shots/` 14 route BA × 6 khổ.

## Chiều cao trang đổi — đều nằm trên trục đã duyệt

| Route · khổ | Δ cao | Vì sao |
|---|---|---|
| mọi route PC 1440 | **+32** | đáy 32 của container (spec) |
| đa số route 992/1024 | **≈ +20** | 30,8 của Vuexy → đỉnh token + đáy 32 |
| `/portal/order` 992/1024 · `/portal/support` 992 | **−300 … −337** | lề 30,8 → 24 rộng thêm 13,6px ⇒ lưới xếp được thêm cột, ít hàng hơn; support 992 nhìn thấy **30 → 33** record |
| `/portal` 360 | +36 | gutter 12 → 16, Home không phải màn danh sách |
| `/portal/info-request` 360 | −28 | tiêu đề hết xuống dòng khi bỏ rule 16px rò (IMPACT 1); giả lập lại CSS cũ ra đúng chiều cao cũ |
| `/portal/inspection` 360/390 | −276 | bỏ `min-height: 100vh` của vỏ Khảo sát |

## IMPACT (báo BA)

1. **Tiêu đề lệch 16px — gốc đã tìm ra**: `portal_inspection.css` có rule **không phạm vi**
   `.wj-page-header { padding-left/right: 16px !important }` (commit `ad7ffc3`, 07/08). Vì CSS portal nạp
   chung một bundle, rule này đè PageHeader của **mọi** màn portal, không riêng Khảo sát ⇒ đúng hiện tượng BA
   đo (content x=324, title x=340; mobile 16 vs 32). Đã gỡ; guard `test_khong_module_nao_de_padding_page_header`
   chặn tái phát.
2. **Tablet 992–1199 lề 30,8 → 24**: rộng thêm 13,6px mỗi bên.
3. **Mobile màn không phải danh sách 12 → 16** (Home, form, chi tiết, giỏ, Tài khoản) — đúng spec; danh sách giữ 12.
4. **PC có thêm đáy 32px** cuối trang.

## LIMIT

1. **Đệm đỉnh mobile = 10** (token `--wujia-mcontent-top`, chốt nhịp dọc mobile 18/09 của chủ dự án), không
   phải 16 như spec CMP-PC-001. Giữ để không phá nhịp đã duyệt; nếu BA muốn 16 thì đổi **một** token.
2. **Chưa có biến thể `bottomInset` cho sticky action**: giỏ hàng vẫn giữ đáy 150px riêng bên trong container.
   Làm cùng lượt E7b hoặc khi BA chốt 145 (BottomNav).
3. **Công nợ › Lịch sử thanh toán @360/390 "5 → 4 record"** là giả đo: record thứ 5 nằm ở y≈898–900, còn
   bottom-nav bắt đầu ở y=817 ⇒ **trước và sau đều bị che**, thước đo chỉ đếm theo mép 900 của viewport. Dời
   2px vì bỏ `padding-top: 8px` chồng lên đỉnh container. `wj_measure` (đếm theo vùng nhìn thấy) báo 0 mất.
4. **Khảo sát chi tiết/khắc phục không đo sống được**: DB local không có phiếu khảo sát nào (bảng
   `wujia_franchise_inspection` rỗng) ⇒ soi tĩnh template (xem dưới); đo lại trên UAT ở E7b.
5. **Sidebar 992–1199 đè lên nội dung và top bar** trong ảnh chụp: có từ trước (ảnh 05/09 y hệt), là hành vi
   overlay của Vuexy ⇒ thuộc **E8** (`UI-SIDEBAR-001`), không phải container.
6. `b4_regression` bản gốc báo 270/286 vì 4 ID cứng (`return/12`, `notification/41` đã không còn; anh.owner
   hết dữ liệu giao hàng) ⇒ chạy bản thay ID thật của `em.hcm` (`scratchpad/e7a/b4_local.py`): **286/286**.

## Bàn giao anh Thái — `wujia_portal_inspection` (sửa tối thiểu, chủ dự án duyệt 24/09)

Chỉ đụng **vỏ**, không đụng controller, dữ liệu hay JS:

| File | Trước | Sau | Lý do |
|---|---|---|---|
| `static/src/css/portal_inspection.css` | `.wj-page-header { padding-left/right: 16px !important }` | xoá | rò ra PageHeader của mọi màn (IMPACT 1) |
| `static/src/css/portal_inspection.css` | `.wj-inspection-container` max-width 900/1100 + `min-height: 100vh` | xoá | bề rộng/đáy thuộc PageContainer (width variant ở E7b) |
| `portal_inspection_list_templates.xml` | `wj-inspection-container d-lg-none p-3 bg-white` | `wj-inspection-container d-lg-none` | lề đôi + nền trắng (BA đo 14px, nền trắng) |
| `portal_inspection_detail_templates.xml` (mobile) | vỏ `p-0 bg-light pb-5` + con `p-2` | vỏ trơn + con `py-2` | thẻ đứng ở 16+8 = 24 thay vì 16 |
| `portal_inspection_remediation_templates.xml` (mobile) | vỏ `p-0 bg-light pb-5` + form `p-3` | vỏ trơn + form `py-3` | thẻ đứng ở 16+16 = 32 thay vì 16 |

Giữ khoảng dọc (`py-*`) để nhịp trong màn không đổi. Nếu anh sửa các màn này, lưu ý:
- **không đặt padding ngang** trên vỏ route hoặc trên con bọc trực tiếp — lề đã do `.wj-page-container` giữ;
- **không khai rule toàn cục** cho component chung (`.wj-page-header`, `.wj-surface-card`…) — luôn chặn bằng
  class của màn;
- guard `test_vo_route_khong_khai_le_ngang` + `test_vo_route_khong_gan_utility_le` (sổ `wujia_portal_base`)
  sẽ đỏ nếu vỏ Khảo sát có lại lề ngang bằng CSS hoặc class `p-*`/`px-*`.

Còn thấy khi soi: bản PC chi tiết/khắc phục vừa gọi `wj_page_header` PC vừa tự dựng `.wj-pc-page-header`
trong `content-wrapper` — anh xem có hai tiêu đề trên PC không (không sửa ở E7a).

## Guard + mutation

| Guard | Mutation (phá) | Kết quả |
|---|---|---|
| `test_khong_module_nao_de_padding_page_header` | trả lại rule 16px của Khảo sát | 🔴 |
| `test_content_wrapper_khong_giu_le` + `test_vo_route_khong_khai_le_ngang` | trả lại `content-wrapper` 24px ở ≥1200 | 🔴 |
| `test_mpage_khong_giu_le` + `test_vo_route_khong_khai_le_ngang` | trả padding `.wujia-mpage` | 🔴 |
| `test_vo_route_khong_khai_le_ngang` | trả padding `.wj-debt` · padding ngang `.wj-inspection-container` | 🔴 · 🔴 |
| `test_app_content_khong_giu_day` + `test_khong_ai_chua_day_tren_app_content` | trả `padding-bottom: 96px` trên `.app-content` | 🔴 |
| `test_man_danh_sach_bat_bien_the_list` | bỏ cờ `list` ở Công nợ tổng quan | 🔴 |
| `test_chi_man_danh_sach_bat_list` | bật cờ `list` ở form YC thông tin | 🔴 |
| `test_container_tang_goc` | thêm `overflow-x: hidden` vào container | 🔴 |
| `test_container_mobile` | bỏ `env(safe-area-inset-bottom)` | 🔴 |
| `test_token_gutter` | gutter 24 → 20 | 🔴 |
| `test_mot_container_boc_noi_dung_route` | đặt `t-out="0"` ra ngoài `<main>` | 🔴 |
| `test_vo_route_khong_gan_utility_le` | vỏ chi tiết Khảo sát có lại `p-3 bg-light` | 🔴 |

**13/13 đỏ**, khôi phục xong xanh lại. Harness: `scratchpad/e7a/mutate.py`.

## Việc sau

- **E7b**: width variant `fluid` / `standard 1440` / `narrow 960` (narrow chỉ giỏ, `return/new`,
  `support/new`, `info-request/new`), `bottomInset` cho sticky action, đo lại 14 route + Khảo sát chi tiết trên
  UAT (chỉ đọc) ⇒ `qa_sync` `UI-PAGECONTAINER-001` → Ready for Retest.
- **Phiên phân cụm 140–145** sau E8; 143/145 đo lại trên khung mới trước khi code.
