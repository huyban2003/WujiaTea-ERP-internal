# C7 — bảng đối chiếu acceptance (WJ-HOME-001/002/006/007/008)

Nguồn: cột `Kết quả mong muốn` của từng issue trên tab `5. Issue List` (STT 106/107/109/110/111).

**Cách đo.** DB copy cô lập `wujia_tea_c7` (port 8058, không đụng `wujia_tea_19`/8019),
`-u wujia_portal_base,wujia_portal_layout,wujia_sale` RC=0 / 0 ERROR. Playwright headless
360 / 391 / 430 / 500 (mobile) và 1366 / 1920 (PC). Trạng thái **trước khi sửa** đo trên DB
`wujia_tea_c6` (port 8057) — cùng dữ liệu, view cũ. Riêng WJ-HOME-001 đo thêm **trực tiếp
trên UAT** bằng cách nhúng CSS mới (L14), vì UAT có `website_sale` nên bundle khác local.

| # | Yêu cầu (rút từ acceptance BA) | Đo được | Kết quả |
|---|---|---|---|
| **WJ-HOME-001 — nhãn 4 KPI bị cắt** |||
| 1 | 4 KPI hiện đủ tên ở 360/391/430/500 | 0 nhãn bị cắt ở cả 4 khổ (`scrollWidth <= clientWidth`) | Pass |
| 2 | Ưu tiên nằm trên **một hàng** | 4 tile cùng `top`, mỗi nhãn **1 dòng** (đo bằng `Range.getClientRects()`) | Pass |
| 3 | Số liệu, nhãn, đường phân cách không chồng lấn | `label.bottom <= value.top` ở cả 4 tile × 4 khổ; ép số tiền dài `12.345.678 ₫` vào ô Công nợ vẫn nằm trong tile (spill −5/−8px), tràn ngang 0 | Pass |
| 4 | Không có nhãn cắt bằng “…” | Bỏ hẳn `text-overflow: ellipsis`; trên UAT 360px nhãn bị cắt **1 → 0** sau khi nhúng CSS mới | Pass |
| 5 | Không đủ chỗ ở khổ nhỏ nhất thì chuyển 2×2 | **Không kích hoạt** — 360px đã đủ chỗ (thiếu đúng 2px, bù bằng letter-spacing + padding) | N/A (theo đúng thứ tự ưu tiên BA) |
| 6 | Desktop/tablet không bị ảnh hưởng | Khối desktop của Home không sửa dòng nào; quy tắc thu hẹp nằm trong `@media (max-width:380px)`; PC 1366/1920: 4 trang status 200, tràn ngang 0 | Pass |
| **WJ-HOME-002 — mã đơn bị rút thành “S0…”** |||
| 7 | Mỗi đơn đủ thông tin để phân biệt | Mã đơn in đầy đủ trên dòng 1, ngày và số tiền xuống dòng phụ | Pass |
| 8 | Không còn nhiều mã hiện thành “S…” | Tiêu đề dòng bị cắt: **trước 1** (`S00022` 360px) → **sau 0** ở cả 4 khổ. Mã chuyến giao (`BATCH/2026/06/28/004`) cũng hết cắt | Pass |
| 9 | Mã, ngày, tiền, trạng thái không chồng lấn | Dòng dạng `is-stacked`, badge `align-self:flex-start`; 0 chồng lấn ở 4 khổ | Pass |
| 10 | Xác định đúng đơn trước khi mở chi tiết | Mã đầy đủ + trạng thái + số tiền cùng hiển thị | Pass |
| 11 | Không phát sinh cuộn ngang | `scrollWidth − clientWidth = 0` ở 360/391/430/500 | Pass |
| **WJ-HOME-006 — mỗi block 2 bản ghi** |||
| 12 | Block > 2 bản ghi chỉ hiện 2 | Test `wujia_home_c7`: tạo 4 đơn → Home hiện đúng 2. Đo trang: mọi block preview `rows = 2` | Pass |
| 13 | Thứ tự mới → cũ theo ngày nghiệp vụ | Test assert đúng 2 đơn **mới nhất** theo `date_order desc`; các block giữ nguyên `order` cũ | Pass |
| 14 | “Xem tất cả” mở đúng danh sách đầy đủ | 5 link “Xem tất cả” còn nguyên ở cả 4 khổ, đường dẫn không đổi | Pass |
| 15 | Tổng số bản ghi thực tế không đổi | Chỉ đổi `limit` hiển thị; 4 con số KPI vẫn đếm bằng `search_count` riêng, không dùng danh sách preview | Pass |
| 16 | Block 0 hoặc 1 bản ghi vẫn hiển thị đúng | Nhánh `t-if` rỗng và `.wj-empty-state--row` (S50) giữ nguyên, không sửa dòng nào | Pass |
| 17 | Home ngắn lại, không bị bottom nav che | Cùng dữ liệu: chiều cao trang **2752 → 2634** (360px), **2663 → 2563** (391px); `navspacer` giữ nguyên | Pass |
| **WJ-HOME-007 — bỏ chevron cấp dòng** |||
| 18 | Không còn chevron “xem chi tiết” trong dòng/card | `.wujia-mdash-chev` **11 (UAT) / 7 (DB copy) → 0**; test Python assert chuỗi không còn trong HTML | Pass |
| 19 | Áp đồng nhất cho 6 block (Giao hàng, Đơn hàng, Kiến thức, Đổi trả, Thông báo, Hỗ trợ) | Đếm trên cả trang = 0, không sót block nào | Pass |
| 20 | Giữ “Xem tất cả” ở tiêu đề block | 5 link giữ nguyên (đo ở 4 khổ) | Pass |
| 21 | Toàn vùng dòng/card bấm được, pressed/focus theo component chung | Mỗi dòng là một thẻ `<a>` bọc trọn nội dung; class `.wujia-mdash-row`/`-card` đã nằm trong 3 danh sách của `_interaction.css` (C6) nên hover/pressed/focus áp sẵn — đi Tab thật 5 trang: **124/124** điểm dừng có vòng focus | Pass |
| 22 | Bỏ icon không để lại khoảng trống thừa | Dòng là flex, không có ô giữ chỗ; 0 tràn ngang, chiều cao trang giảm chứ không tăng | Pass |
| **WJ-HOME-008 — mỗi block một card** |||
| 23 | Mỗi block danh sách đúng **một** card container | Giao hàng **2 → 1**, Đổi trả **2 → 1**, Thông báo **0 → 1** (trước không có card), Đơn hàng/Kiến thức/Hỗ trợ/Thông tin cửa hàng giữ 1 | Pass |
| 24 | Bản ghi là dòng trong card, phân cách bằng divider chung | Dùng lại rule sẵn có `.wujia-mdash-row + .wujia-mdash-row { border-top }` | Pass |
| 25 | Padding, bo góc, icon, chữ, badge, khoảng cách dùng chung component/token | Tất cả về `.wujia-mdash-card/-list/-row/-tile/-row-title/-row-sub`; không thêm token màu mới | Pass |
| 26 | Không tách mỗi bản ghi thành card riêng | `.wujia-mdash-item` / `.wujia-mdash-stack` / `.wujia-mhome-noti-row` = **8 → 0** phần tử; rule CSS chết đã xoá | Pass |
| 27 | Hành động nhanh + Tổng quan KPI giữ layout riêng | Hai khối này không đụng dòng nào (`cards=0, rows=0` khi đo) | Pass |
| 28 | Responsive không tràn ngang, không card lồng card | Tràn ngang 0 ở 6 khổ; card không lồng nhau (mỗi block đúng 1) | Pass |

**Tổng: 27 Pass / 0 Fail / 1 N/A → 27/27 mục áp dụng được = 100%** (ngưỡng BA ≥ 90%).

## Hồi quy

| Hạng mục | Kết quả |
|---|---|
| Test mới `--test-tags wujia_home_c7` | 5/5, 0 failed |
| Test hồi quy `wujia_portal_support` + `_return` + `_debt` + `_delivery` | 43/43, 0 failed |
| Lưới B4 (17 route × 2 breakpoint + 5 trang ngoài matrix + 6 chiều rộng) | **282/286** — đúng bằng số của C6 (4 ô đỏ có sẵn: `/portal/support/40` tài khoản admin không vào được màn chi tiết) |
| Vòng focus C6 — đi Tab thật 5 trang | **124/124** điểm dừng có viền, không phá |
| PC 1366/1920 × 4 trang dùng chung `.wujia-mdash-*` | 200, tràn ngang 0, 0 lỗi JS, 0 class chết |

## LIMIT

- Phần **template** (bỏ chevron, gộp card, mã đơn đầy đủ) mới đo trên DB copy; UAT chưa có
  bản này. Sau khi deploy phải đo lại trên UAT — riêng phần CSS của WJ-HOME-001 đã chứng
  minh ngay trên UAT bằng cách nhúng (nhãn bị cắt 1 → 0 ở 360px).
- Ô KPI **Công nợ** trên UAT đang là “—” (cửa hàng của tài khoản đo chưa có chứng từ kế
  toán), nên trường hợp số tiền dài chỉ ép được bằng trình duyệt chứ chưa gặp dữ liệu thật:
  đo cho thấy số tiền tự xuống dòng trong ô, không tràn và không đẩy lệch 4 KPI.
- Trạng thái *pressed* khi chạm vẫn đo bằng trình duyệt giả lập điện thoại, chưa đo máy thật
  (kế thừa LIMIT của C6).
