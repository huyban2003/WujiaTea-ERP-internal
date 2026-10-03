# G3 — Bảng nghiệm thu: Home PC theo mockup V4 (142)

**Issue:** `UI-PC-HOME-REDESIGN-001` (142, Medium, Redesign). Mockup V4 1440×1019
(`docs/mockups/Ngo-Gia-Portal-Home-PC-Mockup-V4-1440.svg`).
Issue tách hai lượt, cả hai làm ngày 30/09/2026 (Mac):
- **G3a (khung)**: hàng đầu + 4 KPI, commit `160d13e`.
- **G3b (7 block record)**: §6–§10 bên dưới.

Issue đóng và deploy một lần sau G3b, bằng một lượt `-u`, để BA không thấy Home PC nửa mới nửa cũ.

**Module `-u`:** `wujia_portal_base` 19.0.7.31.0 · `wujia_portal_debt` 19.0.4.16.0.

**Chủ dự án chốt đầu phiên:**
- Chỉ làm G3a. Commit, deploy chung với G3b.
- KPI "Đơn chờ xử lý" và bảng "Sản phẩm mua nhiều nhất" không có trong V4, nên **bỏ** theo đúng danh sách BA. Chỗ
  nào có thể thành LIMIT thì xử lý luôn, không để nợ.

**Cách đo:**
- DB `wujia_g3s` là bản copy của `wujia_g2s` (đã có G2). Server riêng 8033 chạy `--log-handler=werkzeug:INFO`.
- Bộ đo `scripts/qa/wj_home_g3.py` (Playwright): PC `/portal` ở 1440 · 1280 · 1024 · 992, thêm 991 (phải ra mobile);
  mobile 360/390/430 so vân tay bố cục (`LAYOUT_PROBE` của `wj_density`).
- User: `dung.multi` (3 cửa hàng, Nhân viên, có công nợ) · `anh.owner` (1 cửa hàng, Chủ tiệm, chưa có chứng từ) ·
  `em.hcm` (chuỗi dài).
- Số "trước" chụp **trước khi sửa code**.

## 1. Kết quả theo "Kết quả mong muốn" — phần G3a

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 1 | Hàng đầu chia đôi **Cửa hàng hiện tại \| Khung giờ đặt hàng** | 2 card bằng nhau ở mọi khổ: 1440 → 554 \| 554 (x 288 / 863; V4 vẽ 322–850 \| 872–1416, lệch do sidebar thật 264 so với V4); 1280 → 474 \| 474; 1024 → 478 \| 478; 992 → 462 \| 462. **Chiều cao 2 card lệch 0 px** (133, và 198/240/240/264 khi chuỗi dài) | ✅ |
| 2 | Card cửa hàng: tên đậm, vùng/địa chỉ, vai trò | ô icon 56×56 + "CỬA HÀNG HIỆN TẠI" + tên 18/700 + `area_name` (không có thì lấy `address`, cả hai trống thì bỏ dòng) + pill vai trò StatusBadge success. Nhãn "Chủ tiệm / Quản lý / Nhân viên" lấy **một nguồn** `ROLE_LABELS` (G2) | ✅ |
| 3 | Khung giờ: trạng thái như mobile | 3 nhánh y như thẻ mobile: "Đang mở · còn hh:mm" + thanh tiến độ + "Có thể đặt hàng đến …" / "Đã đóng" + "Mở lại lúc …" / "Đặt hàng 24/7". Nguồn `_order_window_view()` sẵn có, **0 query mới**. Test render cả 3 nhánh | ✅ |
| 4 | Không block xanh đậm lớn, không Thao tác nhanh | khối PC không có `wujia-mhome-hero` / `-actions` / "Thao tác nhanh" (test arch, đã bỏ comment) | ✅ |
| 5 | 4 KPI **Đơn hàng · Thông báo · Đổi trả · Công nợ** | đúng thứ tự, 1 hàng ở cả 4 khổ (y 358). Nhãn + biến + link **như mobile**: `recent_orders_count` → `/portal/purchase-history` · `unread_count` → `/portal/notification` · `return_requests_count` → `/portal/return` | ✅ |
| 6 | Công nợ là số thật, không in 0đ khi chưa có dữ liệu | `dung.multi` in **"17,8tr"** → `/portal/debt`; `anh.owner` in **"—"** (chưa chứng từ). Ô PC và ô mobile dùng **chung một lần gọi** `get_home_debt_kpi()` (spy: đúng 1 lần/lượt vào Home). Gỡ `wujia_portal_debt` thì ô PC về "—" inert, `portal_base` không thêm depend (ADR-027) | ✅ |
| 7 | Không mũi tên phải trên KPI/card | 0 `wujia-kpi-arrow` / chevron ở 4 khổ; xoá cả class CSS chết (`.wujia-kpi-arrow`, `.wujia-kpi-separator`) | ✅ |
| 8 | Không cắt chữ / cuộn ngang ở 1440 / 1024 / 992–991 | 0 tràn ngang ở 4 khổ × 3 user; hàng đầu + KPI **0 chữ bị cắt**. (Chữ "…" duy nhất nằm ở 3 block list cũ, G3b sẽ thay.) 991 → khối PC ẩn, ra Home mobile | ✅ |
| 9 | Chuỗi dài không vỡ | tên cửa hàng + vùng dài (đổi tạm `display_name` stored của `em.hcm`, trả lại sau đo): tên **xuống dòng** (`overflow-wrap:anywhere`, BA cấm cắt), 2 card vẫn cao bằng nhau, KPI dời xuống theo, 0 tràn | ✅ |
| 10 | **Home mobile không đổi** | vân tay 360/390/430 **Δ0** so với "trước" (md5 trùng). Mọi rule mới nằm trong `@media (min-width: 992px)` và có tiền tố `.wujia-home-pc` (test tĩnh) | ✅ |
| 11 | Topbar/sidebar giữ nguyên; trang PC khác không đổi | `wj_density --no-mobile` 27 route: chỉ `/portal` lệch (trang ngắn lại 60–65px vì bỏ bảng Top SP). Các chỗ lệch còn lại là dữ liệu, không phải CSS: id ngẫu nhiên apexcharts (`/portal/reports/orders`) và `view_count` bài viết tăng do chính lượt đo trước (`/portal/knowledge`) | ✅ |

Phần còn lại (7 block record, VNĐ trong block, "Xem tất cả", icon theo loại record, chuỗi VI/EN/ZH) làm ở G3b, xem §6.

## 2. Route × khổ — `/portal` PC sau sửa

| Khổ | Store \| Window (x, w, h) | KPI (w × h) | Tràn | Mũi tên | Mobile Δ0 |
|---|---|---|---|---|---|
| 1440 | 288/554/133 \| 863/554/133 | 266 × 108 | 0 | 0 | 360 ✅ |
| 1280 | 288/474/133 \| 783/474/133 | 226 × 125 | 0 | 0 | 390 ✅ |
| 1024 | 24/478/133 \| 523/478/133 | 228 × 125 | 0 | 0 | 430 ✅ |
| 992 | 24/462/133 \| 507/462/133 | 220 × 125 | 0 | 0 | — |
| 991 | khối PC ẩn, Home mobile hiện | — | — | — | — |

Ảnh: `scratchpad/g3/after1/`, `g3/long/` (không đưa vào repo).

## 3. Hiệu năng — số query `/portal` (dòng werkzeug, 5 lượt/user, lấy min)

| User | Trước | Sau | Δ |
|---|---|---|---|
| `dung.multi` | 46 | 39 | **−7** |
| `anh.owner` | 43 | 36 | **−7** |
| `em.hcm` | 43 | 36 | **−7** |

Tách 7 query bằng `cr.sql_log_count` trong odoo shell trên đoạn code đã xoá:
- 1: `search_count` đơn chờ xử lý.
- 2: `_read_group` top SP + `_read_group` tiền tệ.
- 4: đọc `display_name` / đơn vị tính của sản phẩm top (prefetch).

Plan dự tính −3; thực tế −7 vì phần đọc kèm. Ô Công nợ PC **thêm 0 query** vì dùng chung lượt gọi với ô mobile.

## 4. Test

- Tag `wujia_home_pc_g3a` (15 test, `wujia_portal_base`) và `wujia_home_debt_g3a` (2 test, `wujia_portal_debt`): arch,
  controller, CSS, render HTTP 3 trạng thái khung giờ.
- `test_scan_d5_data_list`: bỏ Home khỏi `CALL_SITES` vì không còn bảng DataList. Bảo vệ chuyển sang
  `test_no_table_datalist_left_on_home`.
- `test_portal_notification_f11._home_kpis`: regex nhãn PC "Thông báo chưa đọc" → "Thông báo" (nhãn V4 = mobile). Luật
  test giữ nguyên: số PC = số mobile = badge chuông.
- **Mutation 7/7 đỏ:**
  - M1 bỏ 1 KPI;
  - M2 đảo thứ tự;
  - M3 trả mũi tên;
  - M4 gọi debt 2 lần;
  - M5 rule ra ngoài `@media`;
  - M6 ellipsis tên cửa hàng;
  - M7 trả `waiting_orders_count`.
- **Suite 20 module** (7 L2 + 13 portal), `-u`: 958 test, **1 error**. Lỗi ở F11: regex bám nhãn cũ, đã sửa như trên.
  Chạy lại `portal_notification` + `portal_base` + `portal_debt`: **384/0/0**.
- `check_layers`: 40 module, 0 vi phạm Dev. R7 còn 2 mục `wujia_franchise` có từ trước, giống G2.

## 5. LIMIT / FYI BA

- **Đơn chờ xử lý** không mất lối vào: xem ở `/portal/purchase-history`, lọc trạng thái.
- **Top sản phẩm** vẫn có ở trang Báo cáo (`wujia_portal_report` có nguồn riêng, không đụng).
- Thanh tiến độ khung giờ dùng **màu token mobile** (cam) để giữ một nguồn với thẻ mobile. V4 vẽ màu xanh. BA muốn xanh
  thì đổi token chung cho cả hai kênh.
- Pill vai trò là StatusBadge **success dạng soft** (chuẩn component). V4 vẽ nền xanh đặc.
- Token `--wujia-kpi-separator-*` ở `wujia_portal_layout/_variables.css` hiện không còn ai dùng. Để lại để khỏi phải
  `-u` layout; dọn khi layout có lượt `-u` kế.
- 🔎 **Phát hiện có từ trước, ngoài phạm vi 142:** ở 992–1199 topbar PC bị chật, logo bị khối Cửa hàng che. Pixel diff
  topbar trước/sau G3a **không lệch**, nên không do G3a. 142 ghi "topbar giữ nguyên", vì vậy báo BA như một issue riêng.

---

# G3b — 7 block record

**Chủ dự án chốt đầu phiên G3b:**
- **Giao hàng sắp tới**: "N đơn chưa giao" là dòng phụ dưới tiêu đề; góc phải là "Xem tất cả" → `/portal/delivery`.
  V4 vẽ số đơn ở góc phải và không có link.
- **Lưới**: 2 cột ở 992–1399, 3 cột từ 1400.
  - Sidebar chỉ hiện từ 1200, nên ở 1200 vùng nội dung (~890) hẹp hơn ở 1199 (~1150). Nếu chia 3 cột từ 1200 thì mỗi cột
    còn ~280px, hẹp nhất trong mọi khổ.
  - Lưới dùng CSS grid riêng, không dùng `.col-xxl-*`. Trang nạp cả BS5 (`web.assets_frontend`) lẫn `bootstrap.css` BS4 của
    Vuexy, nên `.col-lg-6` nạp sau có thể đè `.col-xxl-4`.
- **"Chuỗi VI/EN/ZH dài"**: đo bằng dữ liệu dài. `portal_base` không có i18n, nên không thêm file `.po`.
- **Dòng Thông báo**: dùng ô icon chuông như mobile, không dùng chấm xanh của V4.

## 6. Kết quả theo "Kết quả mong muốn" (nguyên văn cột H) — toàn issue 142

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 1 | Desktop 1440 bám đúng mockup V4 | Hàng 1: Đơn hàng gần đây · Yêu cầu đổi trả gần đây · Giao hàng sắp tới. Hàng 2: Thông báo nổi bật · Bài viết / Kiến thức mới · Hỗ trợ nhanh. Hàng 3: Thông tin cửa hàng rộng cả hàng, 3 ô ngang có vạch ngăn. Đo ở 1440: 3 cột 365px (V4 365), block cùng hàng lệch cao **0 px**. Ảnh đặt cạnh V4 (`rsvg-convert`) | ✅ |
| 2 | Topbar/sidebar giữ nguyên; trang PC khác không đổi | Không đụng topbar/sidebar. 13 selector G3b quét trên 27 route PC: khớp 64 phần tử ở `/portal`, **0 ở 26 route còn lại**, nên G3b không thể đổi trang khác. `wj_density --no-mobile` so với mốc G3a: chỗ lệch ngoài `/portal` đều là dữ liệu (giỏ đổi dòng do suite test, `view_count` Kiến thức, id apexcharts Báo cáo) | ✅ |
| 3 | Hàng đầu chia đôi cân đối | G3a §1 #1. Đo lại sau G3b: vẫn 554 \| 554, Δh 0 | ✅ |
| 4 | Không có Thao tác nhanh | G3a §1 #4 | ✅ |
| 5 | Đủ KPI, nội dung, icon từng record và liên kết | 4 KPI (G3a). 7 block, test `test_seven_blocks_in_v4_order`. Icon ô record: đơn/bài viết `file-text`, đổi trả `corner-up-left`, giao hàng `truck`, thông báo `bell`, trùng mobile (`test_row_icons_match_record_type`). "Xem tất cả" ở 5 block có danh sách, **href như mobile**; link chi tiết từng dòng như mobile | ✅ |
| 6 | Không có mũi tên phải trên card | 0 `chevron-right` / `arrow-right` ở 7 khổ × 3 user. CardHeader không nhận `ch_action_icon` (test + mutation M3) | ✅ |
| 7 | Hiển thị VNĐ, nhãn/màu trạng thái nhất quán | Tiền dòng đơn = `portal_money(amount_total, currency đơn)`; Tổng tiền chuyến giao = currency cửa hàng. Cùng helper và cùng chuỗi với mobile (render test so text dòng PC = dòng mobile). Badge: `m_order_badges`, `wj_return_status`, **một** map màu loại thông báo dùng chung hai kênh (`noti_badge_map`). DB copy local có đơn USD nên in `$`; UAT in `₫`, xem §9 | ✅ |
| 8 | Không cắt chữ hoặc cuộn ngang | 7 khổ (1440 · 1280 · 1200 · 1199 · 1024 · 992 + 991) × 3 user: **0 tràn, 0 chữ bị cắt, 0 badge đè chữ**. PC gỡ `nowrap`/ellipsis của `.wujia-mdash-row-title`/`-sub` (mutation M4). Tiêu đề block dài ("Yêu cầu đổi trả gần đây") xuống 2 dòng, "Xem tất cả" vẫn cùng hàng | ✅ |
| 9 | Kiểm thêm 1024 và ngưỡng 992/991 | 1024/992: 2 cột, Δh 0, 0 tràn. 991: khối PC ẩn, Home mobile hiện | ✅ |
| 10 | Link/hành động hiện có hoạt động như trước | Mọi href lấy nguyên từ block mobile. Render test so href "Xem tất cả" của 5 block. Hỗ trợ nhanh: `/portal/support/new`, `tel:` hotline, Chat `#` (UI-only, như mobile) | ✅ |
| 11 | Home mobile không bị thay đổi | Vân tay 360/390/430 × 3 user. `dung.multi`: md5 **trùng** "trước". `anh.owner`/`em.hcm`: chỉ lệch 4 phần tử của thẻ Khung giờ, do chữ đếm lùi "còn 12:26 → 12:17" và thanh tiến độ chạy theo giờ (dữ liệu, không phải CSS). Mọi rule mới nằm trong `@media ≥992` / `≥1400` và có tiền tố `.wujia-home-pc` (test) | ✅ |
| 12 | Ghi chú BA: chuỗi VI/EN/ZH dài | `em.hcm` đổi tạm tên 2 đơn (EN một từ 60 ký tự · chữ Hán), 2 đổi trả (VI có gạch nối · chữ Hán), 2 thông báo (VI 130 ký tự · chữ Hán), 2 bài viết (EN một từ · chữ Hán), tên + địa chỉ cửa hàng (VI + chữ Hán). Kết quả 6 khổ: 0 tràn, 0 cắt, 0 badge đè; chữ xuống dòng trong cột, block cùng hàng vẫn Δh 0. Trả lại dữ liệu gốc sau khi đo (bản lưu SQL) | ✅ |

**Đạt 12/12 = 100%** (ngưỡng ≥90%).

## 7. Route × khổ — `/portal` PC sau G3b (`dung.multi`)

| Khổ | Cột block | Block (w) | Δh trong hàng | Tràn | Cắt chữ | Chevron | Mobile |
|---|---|---|---|---|---|---|---|
| 1440 | 3 | 365 | 0 · 0 · 0 | 0 | 0 | 0 | — |
| 1280 | 2 | 476 | 0 · 0 · 0 · 0 | 0 | 0 | 0 | — |
| 1200 | 2 | 436 | 0 | 0 | 0 | 0 | — |
| 1199 | 2 | 568 | 0 | 0 | 0 | 0 | — |
| 1024 | 2 | 480 | 0 | 0 | 0 | 0 | — |
| 992 | 2 | 464 | 0 | 0 | 0 | 0 | — |
| 991 | khối PC ẩn | — | — | — | — | — | Home mobile ✅ |

`anh.owner` (Chủ tiệm, 0 chuyến giao) và `em.hcm` ra cùng kết quả: 0 tràn, 0 cắt, 0 badge đè. Trạng thái rỗng hiện đúng chữ như
mobile, và không lồng card: bỏ khung của bản mobile khi nằm trong card.

Ảnh: `scratchpad/g3b/{before,after,long}/` (không đưa vào repo).

## 8. Hiệu năng — số query `/portal` (werkzeug, 5 lượt/user, lấy min)

| User | Trước G3b (= sau G3a) | Sau G3b | Δ |
|---|---|---|---|
| `dung.multi` | 39 | 39 | **0** |
| `anh.owner` | 36 | 36 | **0** |
| `em.hcm` | 36 | 36 | **0** |

7 block PC đọc **cùng recordset** mà controller đã tính cho mobile (`recent_orders`, `latest_returns`,
`latest_notifications`, `m_upcoming_batches`, `articles`, `active_franchise`), dùng chung cache ORM, nên **0 query mới**.
Controller không sửa.

## 9. Test

- Tag `wujia_home_pc_g3b` (17 test, `wujia_portal_base`):
  - **arch**: 7 block đúng thứ tự V4, icon header, "Xem tất cả" không mũi tên, dòng phụ Giao hàng, icon ô record theo
    loại, nguồn trùng mobile, một map badge thông báo, 0 block cũ / chevron, lưới không dùng `.col-*`;
  - **CSS**: 2 → 3 cột, `≥1400` có tiền tố, class mới chỉ nằm trong media PC, dòng không ellipsis, action cùng hàng;
  - **render HTTP**: tiền dòng đơn = mobile, "Xem tất cả" 5 block, trạng thái rỗng, "—" ở Thông tin cửa hàng.
- Scan sửa theo:
  - `test_scan_d3_card_header`: Home 5 → 9 CardHeader (Khung giờ ×2 + 7 block).
  - `test_scan_d5_data_list`:
    - preview Home = 5 block record, không pager;
    - `COMPACT_SITES` bỏ Home, vì họ `wujia-content-card-row` đã rời Home;
    - D5e mobile loại trừ `.wujia-home-pc`;
    - hàng `mdash` không phải danh sách 10 → 13 (+3 lối tắt Hỗ trợ nhanh PC).
- **Mutation 7/7 đỏ:**
  - M1 bỏ 1 block;
  - M2 đảo thứ tự;
  - M3 trả chevron;
  - M4 ellipsis tiêu đề dòng;
  - M5 rule lưới ra ngoài `@media`;
  - M6 đổi href "Xem tất cả";
  - M7 bỏ dòng phụ Giao hàng.
- `wujia_portal_base` `-u`: **315/0/0**.
- **Suite 20 module** (7 L2 + 13 portal), `-u`: **975/0/0**.
- `check_layers`: 40 module, 0 vi phạm Dev. R7 còn 2 mục `wujia_franchise` có từ trước, giống G2/G3a.

## 10. LIMIT / FYI BA (G3b)

- **Giao hàng sắp tới** có "Xem tất cả" + dòng phụ "N đơn chưa giao". V4 không vẽ "Xem tất cả". Chủ dự án chốt thêm để giữ
  link như mobile.
- **Lưới 2 cột ở 992–1399**, 3 cột từ 1400. V4 chỉ vẽ khổ 1440. Ở 1200–1399 có sidebar nên 3 cột sẽ quá hẹp.
- **Dòng Thông báo** dùng ô icon chuông (như mobile, "icon đúng loại"). V4 vẽ chấm xanh.
- **Tiêu đề block** giữ cỡ component CardHeader PC (18px). Ở 1440, hai tiêu đề dài ("Yêu cầu đổi trả gần đây", "Bài viết /
  Kiến thức mới") xuống 2 dòng; V4 vẽ một dòng với chữ nhỏ hơn. Không cắt chữ, "Xem tất cả" vẫn cùng hàng.
- **Tổng tiền** của yêu cầu đổi trả in "—", vì model chưa có trường số tiền (như mobile, NOTE BA).
- **Hotline** lấy `company.phone`; UAT chưa khai thì in "—". **Chat** là UI-only (`#`, chưa có kênh).
- **Người phụ trách** in tên chủ tiệm. V4 vẽ kèm "(Chủ HCM-01)"; mobile cũng chỉ in tên.
- **Chuỗi VI/EN/ZH**: Portal chỉ có chuỗi giao diện tiếng Việt (không có i18n EN/ZH). Đã đo bằng dữ liệu dài 3 thứ tiếng.
- **Tiền tệ** theo currency của đơn / cửa hàng (một helper `portal_money`). Dữ liệu UAT là VND nên in `₫`.

## 11. Sau deploy UAT (30/09/2026 16:04, chỉ đọc)

Push `d8f89bf` đưa cả G3a và G3b lên UAT (G3a `160d13e` đã push trước đó nhưng UAT chưa nhận). Đo `wj_home_g3.py` với
`em.hcm`, chỉ mở trang:

| Khổ | Hàng đầu (w, Δh) | KPI | Cột block | Δh trong hàng | Tràn · chevron · badge đè · block cũ |
|---|---|---|---|---|---|
| 1440 | 549 \| 549, 0 | Đơn hàng 28 · Thông báo 1 · Đổi trả 2 · Công nợ 4,2tr | 3 (365) | 0 | 0 · 0 · 0 · 0 |
| 1280 | 469 \| 469, 0 | như trên | 2 (476) | 0 | 0 · 0 · 0 · 0 |
| 1200 | 429 \| 429, 0 | như trên | 2 (436) | 0 | 0 · 0 · 0 · 0 |
| 1199 | 561 \| 561, 0 | như trên | 2 (568) | 0 | 0 · 0 · 0 · 0 |
| 1024 | 473 \| 473, 0 | như trên | 2 (480) | 0 | 0 · 0 · 0 · 0 |
| 992 | 457 \| 457, 0 | như trên | 2 (464) | 0 | 0 · 0 · 0 · 0 |
| 991 | khối PC ẩn, Home mobile hiện | | | | |

"Xem tất cả" 5 block đúng href; Giao hàng "1 đơn chưa giao". Mobile 360/390/430 so với lượt đo UAT ngay trước deploy:
chỉ lệch 1px ở viên "Đang mở · còn hh:mm" (chữ đếm lùi), bố cục còn lại trùng.

## 12. Issue 150 `WJ-HOME-009` + 151 `WJ-HOME-010` — đơn gần đây trên Home (30/09/2026)

Hai issue BA mở sau G3 (status `New`, chủ dự án cho làm trước). Cùng đơn S00075 (draft, `date_order` 15:57 UTC).

**Chẩn đoán**
- 150: block PC **cũ** (trước G3b, `160d13e` `portal_home.xml:224`) in `order.date_order.strftime(...)` không đổi múi giờ.
  G3b (`d8f89bf`) xoá block đó và dùng `wj_dt` như mobile. BA đo S00075 trước khi G3b lên UAT (30/09 16:04).
  Đo UAT chỉ-đọc sau deploy G3b, `em.hcm`: Home PC **22:57 29/09/2026** = mobile = Lịch sử. ⇒ đã sửa, phiên này chỉ thêm
  test chặn hồi quy.
- 151: Home dùng bảng riêng `MOBILE_ORDER_BADGES` (draft → "Nháp" neutral; không có nhãn giao hàng đè), Lịch sử dùng
  `SALE_STATE_META` + `DELIVERY_OVERRIDE_META`. Sửa: dời luật trạng thái xuống `wujia_portal_base/controllers/utils.py`
  (`portal_order_status`, `portal_order_badge`), Home PC + mobile gọi `wj_order_badge(o)`, Lịch sử import cùng hàm (tên cũ
  `_state_meta`/`_order_status` giữ làm alias). Xoá `MOBILE_ORDER_BADGES`.

**Theo "Kết quả mong muốn" (nguyên văn cột H)**

| # | Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|---|
| 150-1 | Cùng SO, tz Asia/Ho_Chi_Minh: Home PC, Home mobile, danh sách + chi tiết Lịch sử cùng ngày giờ | ✅ | UAT S00075 PC/mobile/chi tiết 22:57 29/09; test `test_vietnam_user_sees_2257_on_pc_and_mobile` |
| 150-2 | S00075 hiện 22:57 29/09/2026 mọi nơi | ✅ | UAT chỉ-đọc `em.hcm` |
| 150-3 | tz khác + tz trống theo fallback dự án | ✅ | test Tokyo → 00:57 30/09; tz rỗng → `DEFAULT_PORTAL_TZ` 22:57 |
| 150-4 | Không sửa dữ liệu nguồn | ✅ | chỉ presentation (`wj_dt`) |
| 151-1 | Cùng SO: nhãn + màu badge giống nhau ở Home PC, Home mobile, danh sách, chi tiết Lịch sử | ✅ | test so 4 nơi × 5 trạng thái; local `anh.owner` đơn 1799/12 |
| 151-2 | S00075 ở trạng thái hiện tại hiện "Chờ xác nhận" trên Home | ✅ local (draft) · UAT sau deploy | local 3 user: draft → "Chờ xác nhận" pending |
| 151-3 | Kiểm draft/sent/sale/done/cancel | ✅ | sale.order Odoo 19 không có `done`: "Hoàn tất" = chuyến done đè (như Lịch sử); cancel bị loại khỏi Home và Lịch sử (test) |
| 151-4 | Không đổi quyền, dữ liệu, workflow | ✅ | không đụng model/ACL, domain Home giữ nguyên |

**Đo** (DB `wujia_g3s`, server 8033)
- Query `/portal` trước/sau: 27/36/36 → 27/36/36, **Δ0** (`batch_id` store + index, prefetch).
- `wj_home_g3.py` 1440/1280/1200/1199/1024/992: 0 tràn, 0 chữ bị cắt, 0 badge đè, Δh 0; 991 ra mobile. "Chờ xác nhận"
  vừa trong card 464px ở 992.
- Mobile 360/390/430: vân tay đổi đúng do chữ nhãn "Nháp" → "Chờ xác nhận"; không tràn.

**Test**
- `wujia_portal_purchase_history/tests/test_home_order_status.py` 9 test (tag `wujia_home_order_status`).
- Mutation (block PC về bảng cũ + `strftime` UTC): **6/6** ca có thay đổi đỏ (draft, đang giao, hoàn tất, 3 ca giờ);
  sent / sale-không-chuyến xanh vì nhãn cũ vốn trùng.
- `-u` 2 module + test 3 module: 393/0/0. Suite 20 module (`-u` cả 20, có `wujia_sale`): 939 test, **0 failed, 2 error
  ở `wujia_sale`** (`ValidationError: Quants cannot be created for consumables` trong fixture test — không liên quan, phiên
  này không đụng `wujia_sale`).
- `check_layers`: 0 vi phạm tầng; R7 2 dòng ở `wujia_franchise` (code anh Thái, có từ trước).

**LIMIT / FYI BA**
- Home dùng đúng bộ nhãn của Lịch sử, nên đơn đã xác nhận mà chuyến đang giao / đã giao xong hiện "Đang giao" /
  "Hoàn tất" (trước đây Home luôn "Đã xác nhận").
- Nhãn "Đã gửi" (state `sent`) giữ như Lịch sử.
