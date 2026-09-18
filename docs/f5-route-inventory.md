# F5a — Kiểm kê route portal + vá điểm mù của mốc đo

*Phiên F5a · 18/09/2026 · Mac · DB `wujia_f0` port 8099 · đếm bằng máy
(`scratchpad/f5/route_inventory.py` → `scratchpad/f5/routes.json`)*

Nợ ★FR-B để lại: mốc F0 **không có** `/portal/franchise-information` (4 chỗ gắn marker sai ở màn này
lọt qua cả F4 lẫn vòng soi tay của FR-B), và **không màn nào được đo ở trạng thái rỗng**.

## 1. Tổng quan 97 `@http.route` / 13 module portal

| Nhóm | Số | Xử lý trong phép đo |
|---|---|---|
| Trang HTML GET | 44 | đo (trừ ngoại lệ dưới) |
| Có converter (`<int:id>`, slug) | 27 | đo bằng bản ghi mẫu có thật trên DB |
| POST-only | 9 | không đo bằng trình duyệt (test HTTP lo) |
| `type='json'` | 17 | không đo |

**Không đưa vào danh sách đo, có lý do:**

| Route | Lý do |
|---|---|
| `/portal/logout` | huỷ phiên đăng nhập ⇒ mọi ô đo sau đó thành Pass rỗng |
| `/portal/login`, `/portal/forgot-pass`, `/portal/reset_password` | ngoài shell portal, không có menu; đang đăng nhập thì redirect |
| `/portal/_pc-preview` | công cụ dev |
| `*/results`, `/portal/inspection/ajax` | fragment cho AJAX, không phải trang |
| `/portal/reports/orders/export.xlsx` | tải tệp |
| `/my/branches`, `/my/franchises`, `/portal/branches`, `/portal/redirect` | chỉ chuyển hướng |
| `/portal/purchase_history`, `/portal/return-request-list`, `/portal/exam-registration` | 301 cũ — **Việc 3** đo bằng test, không bằng trình duyệt |

## 2. Route mới thêm vào mốc F5a (không có ở mốc F0)

`/portal/franchise-information` · `/portal/franchises` · `/portal/change-password` ·
`/portal/order/cart` · `/portal/order/rejected` · `/portal/info-request/new` ·
`/portal/exam/register` · `/portal/debt/pay` · `/portal/remediation` (của anh Thái — đo, không sửa)

## 3. Trạng thái rỗng — 11 route, tìm bằng cách THỬ THẬT

DB seed không bao giờ ra trạng thái rỗng ⇒ mọi rule của nó đi qua mọi phép đo mà không ai thấy
(nợ (c) của FR-B). Tham số lọc **không đồng nhất** giữa các màn, nên phải đọc chữ ký controller rồi
thử, không đoán `?q=`:

| Màn | URL ép rỗng | Tham số |
|---|---|---|
| Lịch sử đặt hàng | `/portal/purchase-history?q=zzzkhongcogi` | `q` |
| Giao hàng | `/portal/delivery?q=zzzkhongcogi` | `q` |
| Đổi trả | `/portal/return?q=zzzkhongcogi` | `q` |
| Hỗ trợ | `/portal/support?q=zzzkhongcogi` | `q` |
| Lịch sử thanh toán | `/portal/debt/payment-history?q=zzzkhongcogi` | `q` |
| Đăng ký thi | `/portal/exam?q=zzzkhongcogi` | `q` |
| Kiến thức | `/portal/knowledge?keyword=zzzkhongcogi` | **`keyword`** |
| Thông báo | `/portal/notification?keyword=zzzkhongcogi` | **`keyword`** |
| Đặt hàng | `/portal/order?keyword=zzzkhongcogi` | **`keyword`** |
| Yêu cầu cập nhật TT | `/portal/info-request?state=draft` | **`state`** (chuỗi rác bị bỏ qua) |
| Báo cáo đặt hàng | `/portal/reports/orders?date_from=2001-01-01&date_to=2001-01-02` | khoảng ngày |

**Không ép được:** `/portal/debt` — số liệu tới từ seam `AbstractModel` `wujia.portal.debt` (dữ liệu
giả S48), tham số `week` không lọc. Trạng thái rỗng của phân hệ Công nợ đã phủ bằng
`/portal/debt/payment-history`. `/portal/inspection` là của anh Thái — chỉ đo nguyên trạng.

## 4. Phát hiện ngay khi mốc hết mù (lỗi CÓ SẴN, F5a không sửa)

`wj_measure` trên mốc mới báo **6 HIERARCHY** cho `anh.owner` (mốc F0 báo 3). 4 cờ mới chỉ tồn tại ở
những chỗ trước nay không ai đo:

| Chỗ | Cờ | Ghi chú |
|---|---|---|
| `/portal/purchase-history?q=` @1440 | tiêu đề EmptyState 20 > tiêu đề card 18 | 4 màn cùng kiểu |
| `/portal/delivery?q=` @1440 | 28 > 22 | |
| `/portal/notification?keyword=` @1440 | 20 > 18 | |
| `/portal/reports/orders?` khoảng ngày rỗng @1440 | 20 > 18 | |
| `/portal/exam/register` @1440 | 18 = 18 "Người tham gia" | màn mới thêm vào mốc |

⇒ **Tiêu đề trạng thái rỗng đang to hơn tiêu đề của card chứa nó ở 4 màn.** Đây là đầu vào cho cụm
**EmptyState** (~124 chỗ viết tay, `docs/next-session-clusters-F.md` §1.B3) — đổi dáng nên F5a không
đụng, chỉ ghi nhận.

Ngoài ra: `/portal/order/rejected` redirect về `/portal/order/cart?error=internal_error` (route cần
tham số đơn); `/portal/inspection`, `/portal/inspection/detail/1`, `/portal/remediation` tự thêm tiền
tố `/vi/` — cờ có sẵn của module Khảo sát, đã ghi từ F0.

## 5. Bộ đo mới: `scripts/qa/nav_dump.py`

`wj_measure` đo hình học nên **một mục menu đổi chủ / đổi thứ tự / mất active đi qua nó mà không ai
thấy** — đúng thứ F5a sửa. `nav_dump.py` chép lại theo thứ tự mọi link điều hướng: sidebar PC,
bottom-nav, sheet "Thêm", header mobile, navbar PC (`href · nhãn · icon · active · badge · hiện/ẩn`).
`--diff` tách **lệch cấu trúc** khỏi **lệch chỉ ở con số** (badge chuông, số hoá đơn quá hạn đổi theo
dữ liệu giữa hai lượt đo).

Mốc: `docs/f5-baseline/nav_{anh,em}.json` · `measure_{anh,em}.json` · `routes_{anh,em}.txt`
(46 + 28 route × 2 khổ) · ảnh `scratchpad/f5/shots-before/{anh,em}/`.

**Danh sách vàng của menu (đo được, 2 tài khoản giống hệt nhau ⇒ không mục nào theo quyền):**
sidebar 13 `<li>` = 2 tiêu đề nhóm + 11 mục (Trang chủ · Đặt hàng · Lịch sử đặt hàng · Giao hàng ·
Công nợ · Thông báo · Kiến thức · Hỗ trợ · Đăng ký thi · **Khảo sát** · Tài khoản) · bottom-nav 5 tab ·
sheet "Thêm" 9 dòng · header mobile 11 link · navbar PC 15 link.

> ⚠️ Đính chính plan cụm F §1.A3 ("`pc_sidenav.xml` 10 link cứng"): mục **Khảo sát** của anh Thái
> dùng `priority=101`, chạy SAU `layout_sidenav_figma` (99) nên nó **vẫn hiện** — sidebar PC thật
> đang có **11 mục**, không phải 10. Ảnh mốc F0 `shots/anh/portal@1440.png` xác nhận.
