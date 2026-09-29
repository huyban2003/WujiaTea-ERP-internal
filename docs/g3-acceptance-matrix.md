# G3 — Bảng nghiệm thu: Home PC theo mockup V4 (142)

**Issue:** `UI-PC-HOME-REDESIGN-001` (142, Medium, Redesign). Mockup V4 1440×1019
(`docs/mockups/Ngo-Gia-Portal-Home-PC-Mockup-V4-1440.svg`).
Issue tách hai lượt. **G3a (khung)** đã làm ở phiên 30/09/2026 (Mac). **G3b** (7 block record) chưa làm. Issue chỉ
đóng và chỉ deploy sau G3b, `-u` một lần, để BA không thấy Home PC nửa mới nửa cũ.

**Module `-u` (chưa deploy):** `wujia_portal_base` 19.0.7.30.0 · `wujia_portal_debt` 19.0.4.16.0.

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

Còn lại cho **G3b**: 7 block record, VNĐ trong block, "Xem tất cả", icon theo loại record, chuỗi VI/EN/ZH trong block.

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
