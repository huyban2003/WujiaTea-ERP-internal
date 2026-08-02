# Cụm F — Đồng bộ giỏ hàng (đa tab · back/forward · badge)

**Issue:** WJ-ORD-003 (High) · WJ-ORD-002 (High) · WJ-ORD-020 (Low)
**Rủi ro:** Trung bình — có thay đổi hạ tầng realtime
**File chính:** `custom/wujia_portal_sale/static/src/js/portal_cart_sync.js` (284 dòng) ·
`header_cart_badge.js` (29 dòng) · template header

---

## WJ-ORD-003 — Back/Forward hiện snapshot cũ

**BA đo (25/07):** list thấy Pudding ×3 → mở detail, tăng thành ×4 → Back → vẫn ×3/tổng 9,
reload mới ra ×4/tổng 10.

**Root cause** — `portal_cart_sync.js:41-42`:
```js
this._onPageShow = (ev) => { if (ev.persisted) { this.refresh(); } };
window.addEventListener("pageshow", this._onPageShow);
```
Chỉ refresh khi trang được khôi phục từ **BFCache** (`persisted === true`). Chrome rất hay phục vụ
back-navigation từ **HTTP cache thường** → `persisted === false` → không refresh → đúng hiện tượng BA thấy.
Sprint 38 fix đúng một nửa.

**Sửa:** refresh trên **mọi** `pageshow` (bỏ điều kiện `persisted`), cộng thêm
`document.addEventListener("visibilitychange", …)` khi tab quay lại hiển thị.
Cân nhắc thêm `Cache-Control: no-store` cho các route portal có trạng thái giỏ — nhưng
JS refresh là đủ và rẻ hơn; **đừng làm cả hai rồi không biết cái nào có tác dụng.**

---

## WJ-ORD-002 — Hai tab không đồng bộ

**BA đo (25/07):** 2 tab cùng giỏ, giảm gần đồng thời. Server sau reload đúng (×3),
nhưng ngay sau thao tác tab 1 vẫn ×5, tab 2 ×4 — chỉ khớp sau reload.

**Phân tích:** phần **atomic phía server đã xong** (route `/portal/order/cart/step` xử lý inc/dec nguyên tử,
Sprint 2026-07-22-A). Cái còn thiếu là **đẩy thay đổi sang tab khác**.

**Root cause** — `portal_cart_sync.js:46-61`, khối subscribe bị comment nguyên:
```js
// const bus = this.services.bus_service;
// bus.addChannel(`wujia.franchise_${this.franchiseId}`);
// bus.subscribe("wujia_cart_changed", this.onCartChanged.bind(this));
```
Trong khi server **đã publish sẵn** (`controllers/portal.py:273-290` `_publish_cart_event()` →
`bus.bus._sendone('wujia.franchise_<id>', 'wujia_cart_changed', …)`) và channel **đã được authorize**
theo membership ở `wujia_portal_base/models/ir_websocket.py`.

**Quyết định chủ dự án (02/08): bật lại `bus.bus`.**

**Sửa:** bỏ comment, nối `onCartChanged` → `refresh()`. Bỏ qua event do chính tab này phát
(so `updated_at` hoặc gắn client-id) để không refresh thừa.

⚠️ **Bắt buộc ghi lại:**
- WebSocket chỉ chạy ổn định trên **prod gevent + nginx**; môi trường dev/UAT hiện tại rơi về long-poll.
- Với **1500 portal user**, long-poll = 1 kết nối treo/user. Phải **đo** trước khi coi là xong,
  và ghi con số vào cột K/LIMIT. Nếu tải không chấp nhận được → báo chủ dự án, chuyển sang
  phương án poll khi tab active (đã cân nhắc, chưa chọn).

---

## WJ-ORD-020 — Badge nháy số 0 lúc tải

**BA đo:** reload 5 lần, **1/5** lần cả badge giỏ lẫn thông báo hiện `0` rồi mới nhảy về số thật.

**Root cause (tin cậy ~70% — cần xác nhận bằng thực nghiệm):**
template render sẵn `<span class="wujia-header-badge wujia-header-cart-count">0</span>`;
badge chỉ ẩn nhờ CSS (`.is-active` mới hiện) và `header_cart_badge.js` bật sau `DOMContentLoaded`.
Portal nạp CSS bằng **`<link>` tay** (26 file, xem `views/assets.xml`) → có cửa sổ FOUC:
HTML đã parse, CSS chưa apply → chữ `0` lộ ra. Tần suất 1/5 khớp với đặc trưng race.

**Sửa (không phụ thuộc CSS, không phụ thuộc JS):**
- Server render **số thật** ngay trong template (controller đã có count sẵn — `cart_state['line_count']`,
  bell count ở `wujia_portal_notification`), và
- Dùng thuộc tính HTML `hidden` khi count = 0 (áp dụng trước cả khi CSS load), JS chỉ việc cập nhật sau.

**Cách xác nhận trước khi sửa:** chạy Playwright reload 20 lần, chụp DOM ở thời điểm
`document.readyState === 'interactive'`, đếm số lần badge `visible && textContent === '0'`.
Nếu không tái hiện → ghi bằng chứng, hỏi BA trình duyệt/máy, **đừng sửa mò**.

---

## Blast radius

```bash
grep -rn "wujia-header-badge\|wujia-header-cart-count\|is-active" custom/ --include=*.js --include=*.css --include=*.xml
grep -rn "wujia_cart_changed\|_publish_cart_event\|bus_service" custom/ --include=*.py --include=*.js
grep -rn "WujiaCartSync" custom/ --include=*.js --include=*.xml
```
- Badge header dùng chung **PC + mobile** (`header_cart_inherit.xml`, `mobile_header.xml`,
  `header_bell_inherit.xml`) → sửa 1 chỗ ảnh hưởng 3 nơi.
- `WujiaCartSync.refresh()` được `portal_order.js` gọi sau khi thêm giỏ → đổi hành vi refresh
  ảnh hưởng cả luồng thêm sản phẩm.

## Verify

| Kịch bản | Expected |
|---|---|
| Back/Forward sau khi đổi số lượng ở detail | list + panel giỏ + badge + tổng tiền hiện số mới, **không cần reload** |
| 2 tab cùng cửa hàng, tab A giảm 1 | tab B tự cập nhật trong vài giây, không cần reload |
| 2 tab giảm gần đồng thời từ ×4 | kết quả cuối ×2, **cả 2 tab** hiển thị ×2 |
| Reload 20 lần | 0/20 lần thấy badge `0` visible |
| Không có websocket (dev) | trang vẫn chạy bình thường, không lỗi JS, chỉ mất realtime |

Bắt buộc: 0 JS `pageerror` ở `/portal`, `/portal/order`, `/portal/order/cart`, cả 2 breakpoint.

## Ghi sheet

- K (WJ-ORD-003): `FIX: refresh giỏ trên mọi pageshow (không chỉ BFCache) + visibilitychange | IMPACT: mọi trang portal có giỏ | RETEST: Back/Forward sau khi đổi số lượng — số mới hiện ngay, không reload | LIMIT: Không có`
- K (WJ-ORD-002): `FIX: bật subscribe bus.bus channel wujia.franchise_<id>, nhận wujia_cart_changed → refresh giỏ ở mọi tab | IMPACT: giỏ hàng đa tab/đa thiết bị cùng cửa hàng | RETEST: 2 tab cùng giỏ, giảm gần đồng thời từ x4 → cả hai tab hiển thị x2 không cần reload | LIMIT: websocket chỉ ổn định trên prod gevent+nginx; UAT rơi về long-poll — <ghi số đo tải cho 1500 user>`
- K (WJ-ORD-020): `FIX: render count từ server + thuộc tính hidden thay vì đợi JS bật class | IMPACT: badge giỏ + chuông, PC và mobile | RETEST: reload 20 lần, không lần nào thấy số 0 | LIMIT: <nếu không tái hiện được thì ghi rõ và xin thông tin trình duyệt của BA>`
- R: `Custom`
