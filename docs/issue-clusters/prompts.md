# Prompt chạy từng cụm

Mỗi cụm = **một phiên riêng**. Mở phiên mới → `/wujia-start` → khi hỏi "Sprint/task nào hôm nay?"
thì dán nguyên khối prompt tương ứng bên dưới.

**Thứ tự đề xuất:** I → A → E → G → B → D → C → F → H1 → H2

---

## Ràng buộc chung (đã nhúng sẵn trong mọi prompt)

- Đây **không phải sprint** — không ghi sprint log, không cập nhật `.tex`/PDF.
- **Đọc source trước khi sửa**, `grep -rn` blast radius trước khi đụng CSS/token dùng chung.
- Verify trên **DB copy cô lập** (`pg_dump` từ `wujia_tea_19` → DB riêng, port ≠ 8019). **Không đụng UAT 8019.**
- CSS portal nạp bằng `<link>` tay có `?v=` → **sửa CSS là phải bump `?v=`** trong `views/assets.xml`.
- **Dev không tự đóng `Done`** — tối đa `Ready for Retest`, cột P/K/R theo mẫu `01_NGO_GIA_QA_OPERATING_STANDARD.md`.
- Gặp fork (đổi tên model, schema change, quyết định nghiệp vụ) → **hỏi, đừng tự quyết**.

---

## Công thức dựng DB copy để verify *(rút ra khi chạy cụm I — dùng lại cho mọi cụm)*

```bash
export PGPASSWORD=1
createdb -h 127.0.0.1 -U odoo19 wujia_tea_iXXX
pg_dump -h 127.0.0.1 -U odoo19 -d wujia_tea_19 --no-owner | psql -h 127.0.0.1 -U odoo19 -d wujia_tea_iXXX -q
cp -r WujiaTea/data/filestore/wujia_tea_19 WujiaTea/data/filestore/wujia_tea_iXXX

cd WujiaTea/odoo19
python odoo-bin -c ../config/odoo.conf -d wujia_tea_iXXX --http-port=81XX -u <module> --stop-after-init
python odoo-bin -c ../config/odoo.conf -d wujia_tea_iXXX --db-filter='^wujia_tea_iXXX$' --http-port=81XX
```

4 cái bẫy đã dính, đừng dính lại:

1. `createdb -T wujia_tea_19` **fail** khi server 8019 đang chạy (“source database is being accessed”)
   → dùng `pg_dump | psql`.
2. **Bắt buộc `--db-filter`**: không có nó, request HTTP rơi về `wujia_tea_19` (db_name trong conf)
   → đo nhầm DB gốc, tưởng fix không ăn.
3. Mật khẩu `admin` trên DB **local** khác UAT → set lại trong `odoo-bin shell`:
   `env['res.users'].browse(2).write({'password':'Wujia@2026'}); env.cr.commit()`.
4. Playwright: `wait_for_load_state("networkidle")` **treo** (longpoll bus) → dùng `domcontentloaded` + `wait_for_timeout`.
   Trên UAT, admin thuộc nhiều cửa hàng ⇒ overlay `#wujiaStoreOverlay` chặn click:
   `check()` radio `input.wujia-store-radio` rồi `form.wujia-store-form.submit()`.
   Log không ra stdout — nó vào `WujiaTea/logs/odoo.log` (trừ khi truyền `--logfile`).

---

## I — Hỏi BA + đóng gói bằng chứng *(chạy đầu tiên)* — ✅ ĐÃ XONG 03/08/2026

```
Làm cụm I trong docs/issue-clusters/I_blocked_and_questions.md. KHÔNG sửa code trừ 1 việc ở mục (3).

(1) Soạn 7 câu hỏi gửi BA thành MỘT tin nhắn (bản trong doc đã viết sẵn, rà lại rồi đưa tôi
    duyệt trước khi gửi): logo mobile 100×34 · trạng thái Đang giao/Hoàn tất lấy từ đâu +
    phân biệt đơn hủy do thay thế · menu Công nợ PC · cờ ngôn ngữ theo lang của user ·
    clamp tên sản phẩm 2 dòng · màu CTA #0F7CA8 vs #28A9DF · BA cập nhật CT-025.
    Viết bằng thao tác thật, không dùng tên field/thuật ngữ kỹ thuật.

(2) Đo lại + chụp evidence trên UAT cho FUNC-MOB-ORDER-006 (Enter mobile submit đúng) và
    xác nhận RESP-MOB-ORDER-003 (floatbar đã left/right:16). Ghi cột P/K/R đúng chuẩn QA,
    đẩy Ready for Retest cho FUNC-MOB-ORDER-006; RESP-MOB-ORDER-003 Owner đã là BA/Tester
    nên chỉ nhắc, không đổi trạng thái.

(3) Sửa RIÊNG phần "sáng đôi" của UI-PC-BASE-012: ở /portal sidebar đang active cả
    "Trang chủ" lẫn "Công nợ" vì pc_sidenav.xml:46-50 để href="/portal" placeholder.
    Gắn active theo request.httprequest.path khớp chính xác thay vì để Vuexy app-menu.js
    tự dò href. KHÔNG đổi href (đang chờ BA trả lời). Verify 5 route: mỗi route đúng 1 mục active.

(4) Chuyển WJ-PH-003 sang Need Clarification, owner BA, ghi câu hỏi cụ thể vào cột K.

Không sửa nội dung cột A–H của BA.
```

**Kết quả thực tế 03/08/2026:**

| Việc | Kết quả |
|---|---|
| (1) 7 câu hỏi BA | Đã soạn xong trong `I_blocked_and_questions.md` §5 — **chờ chủ dự án duyệt rồi mới gửi** |
| (2) FUNC-MOB-ORDER-006 | Đo lại UAT 391×844: “Tra” + Enter → `?keyword=Tra`, danh sách 5 → 2 sản phẩm. **Đã đẩy `Ready for Retest`** (row 11) |
| (2) RESP-MOB-ORDER-003 | Đo lại UAT: floatbar `position:fixed`, `left/right = 16px`, box `x=16 w=359` (lề phải 16). **Đã đẩy `Ready for Retest`** (row 6) |
| (3) UI-PC-BASE-012 (phần sáng đôi) | **Đã sửa, verify 6/6 route đúng 1 mục active** — nhưng **chưa deploy** nên chưa ghi sheet |
| (4) WJ-PH-003 | **Đã chuyển `Need Clarification`**, owner BA/Tester, câu hỏi ghi ở cột K (row 55) |

**Chi tiết fix (3)** — thủ phạm thật **không phải** `app-menu.js` như prompt đoán:
- `static/assets/js/app.js:112-118` gắn `.active` cho **mọi** `<a>` có `href === location.pathname`
  → ở `/portal` sáng cả “Trang chủ”, “Công nợ” (href placeholder) **và** logo trong `.navbar-header`.
- Đã sửa: `pc_sidenav.xml` tính active **tại server** cho từng mục (`_p` = `request.httprequest.path`);
  `app.js` bỏ qua hoàn toàn khi phát hiện sidebar portal (`#main-menu-navigation .wujia-nav-header`),
  giữ nguyên hành vi cũ cho menu bcore legacy. Bump `app.js?v=1158` (file này trước giờ **không có** cache-buster).
- Chưa đổi `href="/portal"` của mục Công nợ — chờ BA trả lời câu hỏi 3.

⚠️ **Việc còn nợ:** deploy UAT rồi mới `qa_sync` được UI-PC-BASE-012.

---

## A — Shell PC: hình học khung

```
Làm cụm A trong docs/issue-clusters/A_shell_pc.md — fix UI-PC-SHELL-001 + UI-PC-BASE-010 + UI-01 + UI-PC-BASE-001.

Root cause đã xác minh trên UAT 02/08 (đừng đi tìm lại từ đầu):
1. Sidebar kẹt 260px KHÔNG phải do JS. style.css?v=1010 có
   @media(min-width:1200px) body.vertical-layout.vertical-menu-modern .main-menu{width:260px!important}
   (spec 0,3,0) thắng _wujia_theme.css:132-140 .main-menu{width:var(--wujia-sidebar-width)!important} (0,1,0).
   → nâng specificity trong _wujia_theme.css, KHÔNG sửa style.css (legacy dùng chung).
2. UI-01: _wujia_theme.css:137-139 html body .content{margin-left:300px} dính CẢ
   div.navbar-container.content (layouts.xml:33) → header content x=600, store block x=624.
   → loại .navbar-container khỏi rule (:not) hoặc đổi target.
3. UI-PC-BASE-001: Vuexy .content-wrapper{padding: calc(2.2rem-.4rem) 2.2rem 0; margin-top:6rem}
   với html{font-size:14px} → 30.8px / 84px. Ép padding ngang 24px + margin-top 72px ở ≥1200px.
4. UI-PC-BASE-010 còn phần grid sidebar: logo card 260×132 @20/16, MENU CHÍNH y≈188, item rộng 260 lề x=20.

Đừng đổi giá trị token --wujia-sidebar-width (300px đã đúng) — chỉ đổi selector.
Bump ?v= cho _wujia_theme.css.

Verify 1920×1080: sidebar 0,0,300×1080 · navbar 300,0,1620×72 · navbar-container x=300 ·
store block x=324,y=12,430×48, role x≈650,82×26 · content-wrapper y=72 padding 24px đều, content-body x=324 ·
không còn dải trống x=260–300. Đo đủ 5 route PC.
Regression: 391×844 phải BẤT BIẾN (mọi rule trong @media min-width:1200px). Overflow ngang = 0.
```

---

## E — Lịch sử đặt hàng (controller)

```
Làm cụm E trong docs/issue-clusters/E_purchase_history.md — fix WJ-PH-002 + WJ-PH-007 + WJ-PH-004, verify WJ-PH-006.
File chính: custom/wujia_portal_purchase_history/controllers/portal.py + views/portal_history.xml

WJ-PH-002 (lệch -7h): controller trả thẳng datetime naive UTC ở portal.py:83-84 (row),
  :119-120 (detail) và :135 (batch departure — BA chưa bắt, sửa luôn).
  → dùng fields.Datetime.context_timestamp khi hiển thị.
  QUAN TRỌNG: bộ lọc ngày :190-194 cũng sai cùng lý do — datetime.combine(df, time.min) là giờ
  địa phương nhưng so với create_date lưu UTC → lọc "hôm nay" bỏ sót đơn tạo 00:00–07:00 giờ VN.
  Phải quy đổi local→UTC trước khi đưa vào domain.
  Phòng thủ: đã biết có user để tz='Asia/Saigon' làm /portal/reports/orders 500 → tz lạ thì
  fallback Asia/Ho_Chi_Minh, không để nổ trang.
  Mapping giữ nguyên theo BA: Ngày đặt hàng=create_date, Ngày xác nhận=date_order.

WJ-PH-007: _parse_date() chỉ parse, không so sánh. Chặn date_from > date_to ở CẢ controller lẫn UI,
  không chạy query, giữ nguyên 2 giá trị đã nhập, báo "Từ ngày không được lớn hơn Đến ngày"
  tại FilterBar (KHÔNG dùng empty state).

WJ-PH-004: bỏ cột "Thao tác" ở bảng PC trong views/portal_history.xml, mã đơn là link duy nhất.
  Không đụng bản mobile.

WJ-PH-006: KHÔNG sửa — _requester_display() ở portal.py:70-73 đã đúng rule 2 nhánh BA chốt 30/07.
  Chỉ chụp evidence 1 đơn portal + 1 đơn backend, ghi cột K, đẩy Ready for Retest,
  và nhắc BA cập nhật CT-025 trên Master Sheet.

Regression: phân trang, sort, preset tháng này/tháng trước, lọc trạng thái, tìm theo mã đơn, bản mobile.
```

---

## G — Accessibility lẻ

```
Làm cụm G trong docs/issue-clusters/G_a11y.md — fix WJ-ORD-012 + WJ-ORD-011 + phần còn lại của WJ-ORD-019.

WJ-ORD-012: kết luận "DEV BLOCKED, CSS bất lực" ở Sprint 39 là phóng đại. Toàn custom/ chỉ còn
  MỘT template dùng .btn-primary: wujia_portal_sale/views/portal_order_product_detail.xml:65.
  Lưu ý bẫy: _components.css:61 gộp .btn-primary và .wujia-btn-primary CÙNG một khối
  → đổi class suông không giải quyết gì. Phải tách khối, cho CTA dùng token --wujia-cta #0F7CA8
  (_variables.css:16, ≥4.5:1), hoặc dùng .wj-pc-btn--primary. GIỮ NGUYÊN .btn-primary
  (class Bootstrap dùng chung toàn portal). Kiểm đủ default/hover/focus/disabled.

WJ-ORD-011: BA decision = dùng mockup trong cột "Hình ảnh minh hoạ" làm chuẩn; mobile ≥44×44, PC 32–36px.
  Nới hit-area bằng padding hoặc pseudo-element ::after, GIỮ NGUYÊN kích thước thị giác (card 92px không vỡ).
  Phải dựng giỏ có ≥2 sản phẩm trên DB copy mới đo được — stepper chỉ render khi SP đã trong giỏ.

WJ-ORD-019: đo lại 02/08 — Enter submit ĐÚNG ở cả PC lẫn mobile, focus ring PC = 2px solid #28A9DF (đạt).
  Còn thật: ô search MOBILE outline-style:none → thêm focus ring ≥2px như bản PC.
  Chạy tab-walk thật (in document.activeElement theo thứ tự) để chốt phần "tab chạm input ẩn trùng lặp",
  đừng suy luận từ class d-none.

Ghi evidence phần đã đạt vào cột K để BA không fail lại vì lý do cũ.
```

---

## B — Header PC: cụm hành động bên phải

```
Làm cụm B trong docs/issue-clusters/B_header_pc.md — fix UI-03 + UI-PC-BASE-011 + phần hình học UI-02.
CHẠY SAU CỤM A và ĐO LẠI trước khi sửa (cụm A dịch .navbar-container từ x=600 về x=300).

Actual đo 02/08 (1920×1080): language pill 1491.7,4.9,118×62.3 · cart 1609.7,4.9,42.1×62.3 ·
notification 1651.9,4.9,42.1×62.3 · account 1694,4.9,226×62.3 · mép phải cụm = 1920 (thiếu padding phải 20px).
Account đang là text → avatar 40×40 bên PHẢI → chevron, nền trong suốt.

Source v1.5: cart 1590,16,40×40 và notification 1642,16,40×40 (circle glass, nền trắng opacity .18, radius 20);
account 1696,10,204×52 glass pill radius 18, avatar/user-icon 36px BÊN TRÁI rồi mới tên+role+chevron
(tâm avatar 1724,36); language pill 1450,16,118×40.

Sửa: đảo thứ tự DOM trong a.dropdown-user-link ở layouts.xml (avatar lên trước) + thêm khối CSS
scope .wujia-navbar trong _wujia_theme.css, đặt SAU các rule hiện có.
KHÔNG đụng _components.css (8 module dùng chung) và style.css (legacy). Bump ?v=.
Giữ nguyên hành vi click/dropdown/badge — .wujia-header-icon-item được cả
wujia_portal_sale/header_cart_inherit.xml và wujia_portal_notification/header_bell_inherit.xml dùng.

Verify: 4 toạ độ trên + mở 2 dropdown + badge còn đúng số. Mobile 391×844 bất biến.
Phần cờ/nhãn ngôn ngữ KHÔNG thuộc cụm này (đang chờ BA — xem cụm I).
```

---

## D — Giá & tiền tệ *(rủi ro cao nhất, test kỹ nhất)*

```
Làm cụm D trong docs/issue-clusters/D_pricing_currency.md — fix WJ-ORD-024 + WJ-ORD-025 + WJ-PH-005
bằng MỘT helper dùng chung.

Root cause: wujia_portal_sale/controllers/portal.py:227-271 _cart_state() tính subtotal = unit × qty,
không qua tax engine → submit xong SO cộng thuế 15% nên tổng nhảy. Và ký hiệu tiền hardcode ' đ' ở 8 chỗ:
controllers/portal.py:267 (fallback) và :922 · views/portal_order_catalog.xml:99,233 ·
views/portal_order_cart.xml:87,119 · views/pc_cart_panel.xml:63,74,104.
Trong khi purchase_history/controllers/portal.py:88 đọc đúng order.currency_id.symbol → đó là lý do
Cart ra "đ" còn History ra "$".
WJ-PH-005: purchase_history portal.py:106-107 tính unit_price = price_total/qty — xấp xỉ, sai khi có
thuế cố định / nhiều thuế / rounding.

Công thức BA chốt 30/07 (dùng chung cho cả 3):
  discounted_unit = price_unit × (1 − discount/100)
  compute_all(discounted_unit, currency, quantity=1, product, partner) → total_included
  line_total = sale.order.line.price_total ; order_total = sale.order.amount_total
  ký hiệu/rounding theo sale.order.currency_id. KHÔNG tạo field lưu mới.
Gọi compute_all cho 1 ĐƠN VỊ rồi mới nhân — không gọi cho cả qty rồi chia (sai rounding).

Việc: (a) đặt helper dùng chung — đề xuất wujia_portal_sale/controllers/utils.py, HỎI TÔI nếu thấy nên
chỗ khác; (b) _cart_state trả thêm unit_price_tax_included / line_total_tax_included / tax_amount /
total_tax_included — CHỈ THÊM key, không đổi nghĩa subtotal & total_amount (JS đang dùng);
(c) giỏ + màn gửi đơn thành công hiện Tạm tính · Thuế · Tổng thanh toán; (d) bỏ 8 chỗ hardcode ' đ';
(e) purchase_history dùng cùng helper.

KIỂM TRƯỚC KHI CODE: currency của giỏ lấy từ pricelist.currency_id (portal.py:233) — xác nhận nó
đúng bằng currency sẽ tạo SO, nếu không thì hai bên vẫn lệch.

Test ma trận trên DB copy (KHÔNG tạo đơn thật trên UAT): thuế included · thuế excluded · discount ·
2 thuế 1 dòng · currency ≠ VND · sản phẩm không thuế (regression).
Bằng chứng: cùng 1 đơn, 4 màn Cart / PC panel / Submitted / History phải cùng số cùng ký hiệu.
```

---

## C — Mobile shell

```
Làm cụm C trong docs/issue-clusters/C_mobile_shell.md — fix UI-04 + RESP-MOB-SHELL-003
(+ RESP-MOB-ORDER-001 nếu BA đã xác nhận clamp 2 dòng).

UI-04 (đo 02/08, 391×844): 3 action circle 38×38 đang y=33..71 (cần 39..77), tâm x 248/302/356
(cần 247/301/355); glyph avatar i.feather.icon-user có margin-right:7px thừa → tâm 352.5 vs circle 356;
nét font Feather 18px mảnh hơn SVG source stroke 2.4 round.
→ neo cụm action về y=39, dịch tâm x −1px, xoá margin-right, thay glyph bằng SVG inline stroke 2.4
linecap/linejoin round (tái dùng pattern SVG đã có ở bottomnav/store_picker, đừng viết mới).

RESP-MOB-SHELL-003: store strip kết ở y=152 mọi trang, nhưng page header ra 162/163/166/168/169/176
tuỳ route. Gốc: _wujia_theme.css:392-403 đặt padding-top RIÊNG từng trang bằng :has(.wujia-morder|
.wujia-mcart|.wujia-mhist|.wujia-mhome) + .wujia-mreport-wrap, cộng margin nội bộ mỗi trang.
→ thêm token --wujia-mcontent-top:16px vào _variables.css, BỎ HẾT 5 rule :has() per-page,
thay bằng 1 rule chung trong @media max-width:991.98px, rồi trung hoà margin-top của phần tử đầu
mỗi wrapper trang.

CẢNH BÁO: đây đúng là việc từng bị defer ở Sprint 38 với lý do "page-header y regression ~10 trang".
Phải đo TRƯỚC và SAU cho đủ 9 route: /portal /order /order/cart /purchase-history /delivery
/notification /knowledge /support /profile /return. Expected y=168 ±1, x=16.
PC 1920 phải bất biến. Bump ?v= cho _wujia_theme.css và _variables.css.
```

---

## F — Đồng bộ giỏ hàng

```
Làm cụm F trong docs/issue-clusters/F_cart_sync.md — fix WJ-ORD-003 + WJ-ORD-002 + WJ-ORD-020.
File chính: custom/wujia_portal_sale/static/src/js/portal_cart_sync.js

WJ-ORD-003: dòng 41-42 chỉ refresh khi ev.persisted (BFCache). Chrome hay trả back-nav từ HTTP cache
thường → persisted=false → giữ snapshot cũ, đúng hiện tượng BA thấy. Refresh trên MỌI pageshow
+ visibilitychange. Đừng làm cả no-store lẫn JS refresh rồi không biết cái nào có tác dụng.

WJ-ORD-002 — CHỦ DỰ ÁN ĐÃ CHỐT: bật lại bus.bus. Phần atomic server đã xong (route
/portal/order/cart/step); server đã publish sẵn (controllers/portal.py:273-290 _publish_cart_event
→ bus.bus._sendone 'wujia.franchise_<id>', 'wujia_cart_changed'); channel đã authorize theo membership
ở wujia_portal_base/models/ir_websocket.py. Chỉ thiếu client: bỏ comment khối subscribe ở dòng 46-61,
nối onCartChanged → refresh(). Bỏ qua event do chính tab này phát để không refresh thừa.
BẮT BUỘC ghi vào LIMIT: websocket chỉ ổn định trên prod gevent+nginx, UAT rơi về long-poll;
ĐO và ghi lại chi phí long-poll cho 1500 user. Nếu tải không chấp nhận được → báo tôi, đừng tự
đổi sang phương án khác.

WJ-ORD-020 (tin cậy chỉ ~70%): nghi FOUC — template render sẵn chữ "0", badge chỉ ẩn nhờ CSS,
mà portal nạp 26 file CSS bằng <link> tay. XÁC NHẬN TRƯỚC KHI SỬA: Playwright reload 20 lần,
chụp DOM lúc readyState='interactive', đếm số lần badge visible && text==='0'.
Nếu tái hiện → render count từ server + thuộc tính hidden (không phụ thuộc CSS lẫn JS).
Nếu KHÔNG tái hiện → ghi evidence, hỏi BA trình duyệt/máy, đừng sửa mò.

Verify: back/forward · 2 tab giảm gần đồng thời từ x4 → cả hai tab ra x2 không reload ·
reload 20 lần không thấy badge 0 · môi trường không websocket vẫn chạy, không lỗi JS.
```

---

## H1 — Component PC: token / CSS

```
Làm cụm H1 trong docs/issue-clusters/H_pc_components.md — UI-PC-BASE-002, 003, 004, 008, 009.
CHẠY SAU CỤM A (trước đó mọi toạ độ PC còn lệch +300/+12/+6.8px).

Tin tốt: _pc_components.css (387 dòng) ĐÃ CÓ sẵn wj-pc-page-header, wj-pc-filterbar, wj-pc-badge,
wj-pc-pagination, wj-pc-field, wj-pc-control, wj-pc-btn. Việc chính là áp component vào trang còn
dùng Bootstrap/legacy + chỉnh token, KHÔNG viết component mới.

002 PageHeader: hiện Dashboard 24/700, Order/Purchase/Delivery/Notification/Knowledge 28/700, Exam 30/700.
   Source 30px/800. Sửa ở wj_page_header (dùng chung ~40 site/11 module) → 1 chỗ đồng bộ hết.
   ⚠️ kiểm biến thể mobile (--m) KHÔNG đổi theo.
003 FilterBar: 113.6/100/80/89.6px → card 88px, control 38–42px cùng hàng. Áp cho purchase-history,
   notification, delivery, exam. (Trang Đặt hàng là WJ-ORD-023, làm ở H2 — BA đã ghi rõ loại trùng.)
004 Badge: radius 999px w53.6–78.1 h26.8 → h28, radius 14, min-width 84, padding ngang 14–16, font 12–13/600.
   ⚠️ đối chiếu .wujia-badge-* ở _components.css (mobile) — đừng đổi nhầm.
008 FormField: /portal/support/new select 33px, input 38.1px, radius 5.6 → 42px, radius 10,
   border #E5E7EB, label 14/600. Áp .wj-pc-field + .wj-pc-control. Không đổi field nghiệp vụ/validation.
009 FormActionBar: action rời radius8 weight500 không separator → bọc action bar cuối form card,
   có separator, primary bên phải, button h40 radius12 weight700-800.

Grep blast radius từng class trước khi sửa. Bump ?v=.
Verify 1920 trên ≥6 trang PC + regression 391×844 bất biến đủ 9 route (component dùng chung!).
```

---

## H2 — Component PC: đổi cấu trúc template

```
Làm cụm H2 trong docs/issue-clusters/H_pc_components.md — UI-PC-BASE-005, 006, 007 + WJ-ORD-023.
CHẠY SAU H1.

005 Pagination: thêm page-size selector ("10 / trang") cho /portal/purchase-history và
   /portal/notification. /portal/exam ĐÃ làm đúng (10/20/50) → copy pattern đó, đừng thiết kế lại.
   BA cho phép ẩn toàn bộ pagination khi tổng bản ghi ≤ page size.
006 BackButton: /portal/order/product/<id> và /portal/support/new đang dùng nút icon-only 44×44.
   Source v1.5 ghi RÕ không dùng icon-only → thay bằng "← Quay lại" 122×40 (hoặc 122×36 trong
   PageHeader). Chỉ MỘT nút, không lặp ở cuối form. Rà thêm các màn detail khác.
007 Breadcrumb: thêm cho màn create/detail theo hierarchy thật (Hỗ trợ / Tạo yêu cầu;
   Đặt hàng / Chi tiết sản phẩm). Dùng .wj-pc-page-header__crumb có sẵn.
   Breadcrumb KHÔNG thay thế BackButton — giữ cả hai (Navigation Rules v1.5).
WJ-ORD-023: filter /portal/order PC đang xếp dọc 3 hàng y≈172/226/280, input & select cùng rộng ~1024px.
   Đưa search + danh mục + nút Tìm về MỘT hàng trong card trắng, control 40–42px, gap 12–16px.
   GIỮ NGUYÊN <form method="get"> và controller — chỉ đổi layout. Mockup Figma node 4600:2.
   Verify chức năng: chọn Topping → Tìm → URL giữ category_id=2, dropdown vẫn selected, ra đúng 2 sản phẩm.

Verify: đo ≥6 trang PC 1920 + regression mobile 9 route.
```

---

## Sau khi mỗi cụm deploy UAT xong

```
1. Thêm entry vào docs/qa-issue-ledger.yaml (chỉ khi code khớp expected HIỆN TẠI của BA).
2. cd scripts/ba_spec && python3 qa_sync.py --dry-run   → xem
3. python3 qa_sync.py --apply                            → ghi sheet
4. Verify lại bằng export?format=csv (KHÔNG dùng gviz — gviz tôn trọng filter, lệch row).
5. Dev KHÔNG set Done.
```
