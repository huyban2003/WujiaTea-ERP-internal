# Prompt chạy từng cụm

Mỗi cụm = **một phiên riêng**. Mở phiên mới → `/wujia-start` → khi hỏi "Sprint/task nào hôm nay?"
thì dán nguyên khối prompt tương ứng bên dưới.

**Thứ tự đề xuất:** ~~I~~ ~~A~~ ~~E~~ ~~G~~ ~~B~~ ~~D~~ ~~C~~ (xong 03–04/08) → F → H1 → H2
(WJ-ORD-023 của H2 đã tách ra làm xong 04/08 — xem mục H2.)

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
| (3) UI-PC-BASE-012 (phần sáng đôi) | Đã sửa + deploy UAT (`8888dc5`), đo lại 6/6 route đúng 1 mục. **`Ready for Retest`** (row 44) |
| (4) WJ-PH-003 | **`Need Clarification`**, owner BA/Tester (row 35) — nhưng chủ dự án chốt 03/08 **tự làm phương án (a)**, xem prompt cụm E |
| Thêm: WJ-PH-006 | Đo UAT đủ 2 nhánh requester → **`Ready for Retest`** (row 33), kèm lời nhắc BA cập nhật CT-025 |
| Thêm: UI-MOB-SHELL-001 | **`Need Clarification`** (row 8) — chờ BA gửi file logo mobile ~100×34, không sửa được bằng code |

**Chi tiết fix (3)** — thủ phạm thật **không phải** `app-menu.js` như prompt đoán:
- `static/assets/js/app.js:112-118` gắn `.active` cho **mọi** `<a>` có `href === location.pathname`
  → ở `/portal` sáng cả “Trang chủ”, “Công nợ” (href placeholder) **và** logo trong `.navbar-header`.
- Đã sửa: `pc_sidenav.xml` tính active **tại server** cho từng mục (`_p` = `request.httprequest.path`);
  `app.js` bỏ qua hoàn toàn khi phát hiện sidebar portal (`#main-menu-navigation .wujia-nav-header`),
  giữ nguyên hành vi cũ cho menu bcore legacy. Bump `app.js?v=1158` (file này trước giờ **không có** cache-buster).
- Chưa đổi `href="/portal"` của mục Công nợ → **đã chuyển sang cụm A** (chủ dự án chốt nối thẳng `/portal/debt`).

**Chốt của chủ dự án 03/08 — 5 câu trước định hỏi BA nay tự quyết, đã nhúng vào prompt từng cụm:**

| Quyết định | Nằm ở cụm |
|---|---|
| Nối menu Công nợ PC về `/portal/debt` | A |
| Ghép trạng thái chuyến giao vào cột trạng thái đơn (phương án a) | E |
| Giữ CTA `#0F7CA8`, không theo `#28A9DF` của Figma | G |
| Đặt mặc định tiếng Việt cho tài khoản cửa hàng | B |
| Clamp tên sản phẩm 2 dòng (BA đã chốt 22/07) | C |

**Chỉ còn 2 việc thật sự phải nhờ người khác:** file logo mobile (UI-MOB-SHELL-001) và
BA cập nhật CT-025 (WJ-PH-006) — cả hai đã ghi rõ trong cột Ghi chú trên sheet.

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

LÀM LUÔN, KHÔNG HỎI BA (chủ dự án chốt 03/08) — phần còn lại của UI-PC-BASE-012:
nối mục "Công nợ" trong pc_sidenav.xml về href="/portal/debt". Trang có thật (S43/S48) nhưng mới
chỉ có bản mobile nên ở 1920 sẽ ra cột hẹp căn giữa — vẫn hơn bấm vào quay về Trang chủ như hiện tại.
Điều kiện active của mục này đã khoá sẵn theo /portal/debt nên CHỈ đổi href, không đụng logic.
Xoá comment cũ "Công nợ: UI-only (debt build lại theo ADR-007) → Home" — đã lỗi thời.
Verify: bấm Công nợ ở /portal → mở /portal/debt (200), mục Công nợ sáng, Trang chủ tắt.
Ghi cột K: PC chưa có Figma riêng, tạm dùng layout mobile.

Verify 1920×1080: sidebar 0,0,300×1080 · navbar 300,0,1620×72 · navbar-container x=300 ·
store block x=324,y=12,430×48, role x≈650,82×26 · content-wrapper y=72 padding 24px đều, content-body x=324 ·
không còn dải trống x=260–300. Đo đủ 5 route PC.
Regression: 391×844 phải BẤT BIẾN (mọi rule trong @media min-width:1200px). Overflow ngang = 0.
```

**Kết quả thực tế 03/08/2026 — commit `117e634`, ĐÃ DEPLOY UAT + đo lại trên server:**

| Điểm đo (1920×1080, 5 route PC) | Trước | Sau |
|---|---|---|
| `.main-menu` | 260×1080 | **0,0,300×1080** + divider 1px `#EEF2F5` @x=299 |
| `.navbar-container` | x=600 | **x=300** |
| logo card | không có (header cao 200) | **20,16,260×132** radius 18 |
| logo img | 44.5,61.8,180×96 | **58,26,184×86** |
| MENU CHÍNH | y=260 | **x=28, y=188** |
| item menu | 229 @ x=35 | **260 @ x=20** |
| store block / role | 430×48 / 103×46 | **324,12,430×48** / **650,23,82×26** |
| `.content-wrapper` | y=84, pad 24/30.8 | **y=72, pad 24px đều**, content-body **x=324** |

Đo trên **DB copy cô lập `wujia_tea_a01`** (port 8101) → **0 FAIL / 5 route**, overflow ngang 0.
Regression 391×844 snapshot before/after 5 route → **0 diff**. Tablet 1199 + 992: 7 route đều 200,
sidebar giữ 260px, 0 lỗi JS. UI-PC-BASE-012: bấm Công nợ → `/portal/debt` (200), đúng 1 mục active/route.

**Đo lại trên UAT thật sau khi deploy (03/08, `113.161.187.126:8019`, 1920×1080): 0 FAIL / 5 route** —
toàn bộ số trong bảng trên khớp y hệt bản local, overflow ngang 0, divider `1px rgb(238,242,245)`,
card radius 18px, wrapper `padding 24px 24px 0` + `margin-top 72px`. Bấm Công nợ → `/portal/debt` (200),
6 route mỗi route đúng 1 mục sáng. Mobile 391×844 5 route: overflow 0, hình học y hệt (chỉ khác chiều
cao do dữ liệu và bề rộng chip role do nhãn "Manager" vs "Owner").

**2 chỗ doc cụm A đoán sai, đã sửa khác:**
1. `:not(.navbar-container)` **không đủ** — bỏ `.navbar-container` khỏi rule sẽ để
   `style.css:147 html body .content{margin-left:260px}` (0,2,1) rơi vào → x=560. Phải zero
   tường minh `html body .navbar-container.content{margin-left:0!important}` (0,2,2).
2. Item 260px **không chỉ do `margin`** — thủ phạm là `components.css:411`
   `.main-menu.menu-light .navigation > li{padding:0 15px}` (0,4,0), phải khớp specificity.

Thêm 1 báo động giả của harness (L7): kỳ vọng `.content-wrapper.x=324` là **sai** — padding 24px
nằm *trong* wrapper nên bbox wrapper = 300, con đầu mới = 324. Sửa harness, không sửa code.

**Ghi sheet 03/08:** 4 issue → `Ready for Retest` (rows 2/22/45/62); UI-PC-BASE-012 (row 64) giữ
trạng thái, chỉ cập nhật K/P cho phần nối link. Lúc mới push cột P ghi **"CHƯA DEPLOY UAT"** để BA
không retest nhầm build cũ; sau khi deploy đã đổi về `UAT | 2026-08-03 | commit: 117e634` cho cả 5
dòng + 5 dòng `7. ISSUE HISTORY` ghi kết quả đo lại. Verify bằng `export?format=csv`.

⚠️ **2 bẫy công cụ ghi sheet, gặp trong phiên này:**
1. **Bridge Apps Script trả `HTTP 404` NHƯNG ĐÃ GHI XONG** — lỗi nằm ở bước đọc response sau
   redirect, không phải ở lệnh ghi. **Luôn verify bằng `export?format=csv` trước khi chạy lại**,
   nếu không sẽ ghi trùng (phiên này lỡ đẻ 1 dòng History thừa cho UI-01).
   Lô lớn (15 ô) dễ dính hơn lô nhỏ → chia nhỏ theo từng issue như `qa_sync --only`.
2. **`sio.read_values("ISSUE HISTORY")` trả về tab MILESTONE** (gviz sai tên thì im lặng trả tab
   đầu tiên — §12). Muốn đọc tab này phải dùng gid: **`7. ISSUE HISTORY` = `1363122631`**
   (`export?format=csv&gid=1363122631`). Tên thật lấy bằng `sio._post({'action':'ping','sheet':...})`.

**LIMIT đã ghi:** giữ nguyên item height 44px / font menu 16px / radius 8px / accent bar
(source v1.5 ghi 48/15/14 nhưng ngoài "Kết quả mong muốn" của issue) · 2 dòng chữ trong logo card
của bản vẽ chưa dựng · trang Công nợ chưa có Figma PC nên ở 1920 ra cột hẹp căn giữa ·
cụm nút phải header để cụm B.

---

## E — Lịch sử đặt hàng (controller) — ✅ ĐÃ XONG 03/08/2026

> **Kết quả:** `wujia_portal_base` 19.0.5.15.0 · `wujia_portal_purchase_history` 19.0.3.0.0 ·
> `wujia_portal_delivery` 19.0.3.3.0. Không migration, CSS nằm trong `web.assets_frontend`
> (bundle) nên **không** phải bump `?v=`. Deploy: `-u wujia_portal_base,wujia_portal_purchase_history,wujia_portal_delivery`.
> Verify trên DB copy `wujia_tea_s49` (cổng 8049): build RC=0, **14 unit test `wujia_history` 0 failed/0 error**,
> smoke Playwright **48/48 OK** (PC + mobile + regression 3 trang × 2 viewport).
>
> 4 điều đáng nhớ:
> 1. **Helper tz nay dùng chung** ở `wujia_portal_base/controllers/utils.py`:
>    `portal_tz()` / `to_local_dt()` / `local_day_range_utc()`. Module portal khác đừng viết lại.
>    `to_local_dt` trả **naive local** → template giữ nguyên `.strftime`, không phải sửa QWeb.
> 2. **Lỗi tz lan sang cả `wujia_portal_delivery` và widget Home "Giao hàng sắp tới"** (BA chưa bắt) —
>    đã sửa luôn trong cụm này. Bên Giao hàng chỉ cần đụng 3 hàm format (`_hhmm`,
>    `_short_departure`, `_full_departure`) là bịt hết ~10 điểm hiển thị. **KHÔNG đụng `_ics_dt`**:
>    file ICS dùng hậu tố `Z` = UTC, đang đúng chuẩn.
> 3. **Lọc trạng thái gộp (WJ-PH-003, phương án a)** — nhánh "Đã xác nhận" phải viết bằng
>    **danh sách dương** (`'|' batch_id = False` / `delivery_batch_status in [draft, assigned,
>    loading, cancelled, False]`). Dùng `not in` trên đường dẫn m2o là **mất sạch đơn chưa có chuyến**.
> 4. Bẫy harness (đã dính): password `admin` trên DB copy khác UAT → login thất bại nhưng script
>    vẫn chạy tiếp và **mọi assert pass rỗng**. Phải `sys.exit` ngay khi còn ở `/web/login`.
>    Và 2 assert đầu tiên "fail" hoá ra do chọn nhầm đơn của cửa hàng khác (S00025 thuộc HCM-01) —
>    **sửa harness, không sửa code** (L7).

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

WJ-PH-006: XONG RỒI 03/08 (Ready for Retest, đo trên UAT đủ 2 nhánh) — bỏ khỏi cụm này, đừng làm lại.

WJ-PH-003: LÀM LUÔN, KHÔNG CHỜ BA (chủ dự án chốt 03/08) — chọn phương án (a): ghép trạng thái
  chuyến giao vào MỘT cột trạng thái đơn. sale.order.state chỉ có draft/sent/sale; "Đang giao" và
  "Hoàn tất" suy từ batch_id.delivery_batch_status. Thứ tự ưu tiên: trạng thái giao hàng đè trạng
  thái đơn khi đơn đã xác nhận (sale + đang giao → "Đang giao"; sale + đã giao xong → "Hoàn tất";
  còn lại giữ nhãn theo SALE_STATE_META). Bộ lọc trạng thái phải lọc được cả 5 nhãn.
  Trên sheet issue này đang Need Clarification — sửa xong thì đẩy thẳng Ready for Retest,
  ghi rõ ở cột K là Dev đã chọn phương án (a) và vì sao (đây là cái người dùng cửa hàng cần thấy).
  Phần "đơn hủy do bị thay thế": CHƯA làm, cần thêm trường lý do hủy — ghi vào cột K là scope sau.

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

CHỐT SẴN, KHÔNG HỎI BA (chủ dự án 03/08): giữ #0F7CA8 cho CTA, KHÔNG dùng #28A9DF của Figma.
  Lý do ghi vào cột K: #28A9DF chữ trắng = 2.68:1, chính là lỗi a11y BA tự mở ở Sprint 38 —
  không thể vừa giữ đúng màu Figma vừa hết lỗi. Nếu BA muốn giữ màu Figma thì phải đổi màu chữ,
  và đó là quyết định của BA, không chặn Dev làm phần còn lại.

Ghi evidence phần đã đạt vào cột K để BA không fail lại vì lý do cũ.
```

---

## B — Header PC: cụm hành động bên phải — ✅ ĐÃ XONG 04/08/2026

> **Kết quả:** commit `157814a` · `wujia_portal_layout` `19.0.31.8.0` · `wujia_portal_base` `19.0.5.17.0`
> (+ migration `19.0.5.17.0` backfill lang). CSS bump `_pc_account.css?v=1164`.
> Deploy: `-u wujia_portal_layout,wujia_portal_base`. **CHƯA DEPLOY UAT.**
>
> Đo trên DB copy cô lập `wujia_tea_b01` (port 8102) — **0 FAIL**:
>
> | Điểm đo (1920×1080, 5 route PC) | Trước | Sau (= source v1.5) |
> |---|---|---|
> | language pill `<a>` | 1491.7,4.9 118×40 | **1450,16 118×40** |
> | cart | 1609.7,4.9 42.1×62.3, không nền | **1590,16 40×40** r20 glass |
> | bell | 1651.9,4.9 42.1×62.3, không nền | **1642,16 40×40** r20 glass |
> | account pill | 1694,9.9 202×52, nền trong suốt | **1696,10 204×52** r18 glass |
> | avatar | 1812.9 40×40 **bên phải**, viền trắng 3px | **tâm (1724,36) 36×36 bên TRÁI** |
> | mép phải cụm | 1920 (dính biên) | **1900** |
>
> Dropdown ngôn ngữ + tài khoản mở bình thường; badge cart/bell vẫn trong circle, số đúng.
> Mobile 391×844 bất biến 5 route (header 391×104, overflow 0); tablet 1100 sạch; 0 lỗi JS.
>
> **3 chỗ prompt/doc đoán sai — đừng lặp lại:**
> 1. Số "Actual" trong `B_header_pc.md` là bbox của `<li>` (nav-item cao hết 62.3), **không phải pill**.
>    Account pill 202×52 và language pill 118×40 **vốn đã đúng từ S34/S39** — thiếu là nền glass +
>    thứ tự avatar. Đo `<a>`, đừng đo `<li>` (L7).
> 2. **KHÔNG viết CSS vào `_wujia_theme.css`** — rule của đúng các selector này đã nằm ở
>    `_pc_account.css`, nạp SAU (assets.xml L81 vs L86) nên bản ở theme sẽ thua. Sửa tại chỗ.
> 3. `.wujia-header-icon-btn` và `.dropdown-user-link` bị Vuexy `bootstrap-extended.css:1800/1819`
>    đè `padding` ở **(0,4,1)** → phải viết ở **(0,5,2)** (`.wujia-navbar .navbar-container ul.nav
>    li.<x> > a.<y>`), thay vì sửa `_components.css` dùng chung.
>
> **Bẫy mới ghi nhận:** selector `li + li` **không ăn** ở ngữ cảnh này — cùng một khối CSS mà cart
> nhận `margin-left` còn bell computed ra `0px`, không có rule nào cạnh tranh (đã quét đệ quy toàn bộ
> `document.styleSheets`). Đặt `margin-left` inline lên cùng element thì lại ăn. → dùng `gap` trên
> flex container + 2 margin cộng thêm (10 cho cart, 2 cho account) để ra 22/12/14 của source.
>
> **B4 ngôn ngữ (Odoo Fit = Configuration):** header render cờ theo `lang` — code ĐÚNG, BA thấy cờ Mỹ
> vì tài khoản test để `en_US`. Migration S34 (`19.0.5.12.0`) chỉ chạy 1 lần và có seed
> `base.template_portal_user_id`, nhưng user portal tạo THẲNG bằng `res.users.create` lấy lang theo
> người tạo — mà backend chạy `en_US` từ S44. Đã bịt: `res_users.create` mặc định `vi_VN` cho user
> `group_portal` khi vals không truyền `lang` tường minh, + migration `19.0.5.17.0` quét lại
> (**local đổi 1 user: `anh.owner`** — số trên UAT lấy từ log lúc deploy để ghi cột K).
> Test 4/4: portal không lang→`vi_VN` · portal `lang=en_US`→giữ EN · user backend→không đụng ·
> `Command(4)`→`vi_VN`.
>
> **Còn tồn:** deploy UAT + đo lại trên server, rồi ghi ledger/sheet (`Ready for Retest`, R=`Custom`;
> UI-02 ghi thêm Odoo Fit=Configuration + số user đã đổi). Test suite `1 failed/74` là
> `wujia_portal_sale/tests/test_pricing.py` của **cụm D đang dở trong cây thư mục**, không thuộc cụm B.
> Badge giỏ hiện chữ "0" (`display:block`) — đo trên server cụm G trước cụm B cũng y hệt ⇒
> **có sẵn, đúng WJ-ORD-020 của cụm F**, không phải hồi quy của B.
>
> Harness: `scripts/ba_spec/b_header_measure.py` (đo trần) + `b_header_verify.py` (assert đầy đủ).

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
Phần cờ/nhãn ngôn ngữ (UI-02): code ĐÚNG — đo 6 route ngày 02/08 đều ra cờ VN + "Việt Nam".
BA thấy cờ Mỹ là do tài khoản test để lang=en_US. LÀM LUÔN, KHÔNG HỎI (chủ dự án 03/08):
đặt mặc định tiếng Việt cho mọi tài khoản cửa hàng — kiểm migration đã có ở Sprint 34
(activate vi_VN + set lang cho group_portal) xem còn chạy đúng với user tạo MỚI sau S34 không;
thiếu thì bổ sung (default lang khi tạo user portal + data migration cho user hiện hữu).
Ghi cột K: Odoo Fit = Configuration cho phần này, kèm số user đã đổi.
```

---

## D — Giá & tiền tệ — ✅ ĐÃ XONG 04/08/2026 *(rủi ro cao nhất, test kỹ nhất)*

> **Kết quả:** WJ-ORD-024 · WJ-ORD-025 · WJ-PH-005 fix bằng MỘT helper dùng chung.
> `wujia_portal_base` `19.0.5.19.0` · `wujia_portal_sale` `19.0.4.8.0` ·
> `wujia_portal_purchase_history` `19.0.3.1.0` · `wujia_portal_debt` `19.0.2.1.0`.
> Deploy: `-u wujia_portal_base,wujia_portal_purchase_history,wujia_portal_sale,wujia_portal_debt`
> — **không migration, không bump `?v=`** (asset trong bundle `web.assets_frontend`).
> **CHƯA DEPLOY UAT.** Không tạo đơn nào trên UAT — toàn bộ chạy trên DB copy `wujia_tea_sd` (8110).
>
> **Helper đặt ở `wujia_portal_base/controllers/utils.py`, KHÔNG phải `wujia_portal_sale`** như doc
> cụm đề xuất: `wujia_portal_sale` **depends** `wujia_portal_purchase_history` (chiều ngược với doc),
> nên helper ở portal_sale thì history không import được. Chủ dự án chốt đặt ở base — cả 2 đều depends.
> API: `portal_tax_mapper` (factory, cache fiscal position) · `portal_product_taxes` ·
> `portal_unit_price_tax_included` · `portal_line_price_vals` · `portal_money`.
>
> **Bẫy lớn nhất — `compute_all` KHÔNG tái hiện được số của SO.** Công ty đặt
> `tax_calculation_rounding_method = round_globally`; `compute_all` làm tròn **theo dòng**, còn
> `sale.order.line` đi qua `_prepare_base_line_for_taxes_computation` + `_add_tax_details_in_base_line`
> + `_round_base_lines_tax_details`. Hai đường lệch **1 xu** (giá 3,33 · giảm 33% · qty 3 · thuế 7,5%
> → 7,20 vs 7,19) — mà lệch 1 xu giữa giỏ và đơn thì đúng bằng WJ-ORD-024 đang phải sửa. Helper vì
> vậy đi ĐÚNG pipeline của Odoo, không dùng `compute_all` ⇒ khớp ở **cả hai** chế độ làm tròn.
> Công thức BA (`compute_all` cho 1 đơn vị rồi mới nhân) vẫn giữ nguyên về **ngữ nghĩa**: đơn giá
> hiển thị tính cho 1 đơn vị, thành tiền dòng tính cho `qty` đơn vị — **không** nhân đơn giá đã làm tròn.
>
> **Rounding cũng là lỗi, không chỉ ký hiệu.** Format cũ `'{:,.0f}'` cắt phần thập phân: SO
> `amount_total = 10.99` in ra **"11 $"**. BA chốt "ký hiệu **+ rounding** theo currency của đơn" →
> `portal_money(amount, symbol, decimals)` đọc `currency.decimal_places`, thập phân dấu phẩy kiểu VN.
> VND (0 số lẻ) ra byte-for-byte y hệt bản cũ. `formatMoney` trong JS dùng cùng quy tắc.
>
> **`_cart_state` chỉ THÊM key** (JS + fragment + badge đang dùng `subtotal`/`total_amount`):
> per-line `unit_price_tax_included` · `line_total_tax_included` · `tax_amount`; state
> `total_untaxed` · `total_tax_amount` · `total_tax_included` · `currency_decimals`.
>
> **Đã kiểm trước khi code (BA yêu cầu):** currency giỏ ≡ currency SO — cả hai đều lấy
> `franchise.partner_id.property_product_pricelist`, nhánh không pricelist cùng rơi về company
> currency ⇒ không có bẫy lệch currency.
>
> **Verify** (DB copy `wujia_tea_sd`, port 8110 — không đụng 8019/8033/8102/8103):
> build `-u` 4 module RC=0 · 0 ERROR; unit test mới `wujia_portal_sale/tests/test_pricing.py`
> (tag `wujia_pricing`) phủ đủ ma trận BA: thuế included 15% · excluded 10% · discount trước thuế ·
> 2 thuế 1 dòng · thuế cố định · currency ≠ VND · **sản phẩm không thuế (regression)** · rounding ·
> perf mapper; regression toàn bộ 4 module **77 test, 0 failed / 0 error**.
> E2E `e2e_cluster_d.py` **FAILS=0**: cùng đơn `S00284` (untaxed 9,99 · thuế 1,00 · tổng 10,99) →
> **Cart · panel PC · Submitted · History list · History detail đều ra `10,99 $`**, không màn nào
> còn ký hiệu `đ` cứng; smoke `/portal` `/portal/notification` `/portal/debt` 200.
>
> **Ghi nhớ về harness (L7):** regex bắt ký hiệu tiền `\s*đ` báo động giả vì khớp "4 **đơn** gần
> nhất" — sửa **harness** (`đ(?![^\W\d_])`), không sửa code. Và test giả định "thuế cố định làm
> `price_total/qty` sai" là **sai**: thuế `fixed` của Odoo tính **theo đơn vị** nên phép chia vẫn
> khớp — chỗ phép chia thật sự sai là **rounding**, đã pin bằng ca đo được thay vì ca tự nghĩ ra.
>
> **LIMIT:** giá ở catalog + chi tiết SP nay là **giá đã gồm thuế** (chủ dự án chốt) — BA cần biết
> khi đối chiếu với bảng giá backend (vốn là giá chưa thuế).

---

## D — Giá & tiền tệ *(prompt gốc)*

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
+ RESP-MOB-ORDER-001 (LÀM LUÔN, KHÔNG HỎI — BA đã chốt 22/07 phương án B: tên sản phẩm tối đa
2 dòng line-clamp, card cao ~92px, dài hơn thì cắt bằng "…". Ghi chú "Need BA Confirm=Yes"
còn sót ở cột K là ghi chú CŨ chưa xoá, cột N thực tế = No).

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

> **WJ-ORD-023 ✅ ĐÃ XONG 04/08/2026** (tách ra chạy trước vì H1/F đang chạy song song ở phiên khác —
> đây là issue duy nhất của H2 không đụng file của H1). Commit `63dc4bc`, đã deploy UAT + đo lại xanh:
> 3 control cùng `y=245.5`, cao 42, gap 12/12, card trắng radius 16, `category_id=2` → đúng 2 sản phẩm,
> mobile ảnh trùng byte, smoke 4 trang × 2 viewport 200/overflow 0.
> Nguyên nhân thật: `<select>` không khai `width` nên ăn `select{width:100%}` + `padding:5px!important`
> tag-level của `dashboard.css` (bẫy L4) → wrap 3 hàng. Cách chữa: bỏ class riêng của trang, dùng khung
> chung `.wj-pc-filterbar` + `.wj-pc-filter-*` để chuẩn hoá của UI-PC-BASE-003 tự lan tới.
> **Còn lại**: card đang 80px, lên 88px khi H1 (padding filterbar 18→22) deploy — ghi ở LIMIT.

```
Làm nốt cụm H2 trong docs/issue-clusters/H_pc_components.md — UI-PC-BASE-005, 006, 007.
(WJ-ORD-023 đã xong 04/08, đừng làm lại.) CHẠY SAU H1 — 3 issue này sửa đúng file H1 đang giữ:
portal_history.xml, portal_notification.xml, wj_page_header.xml, _components.css.
Việc đầu tiên: `git log --oneline -5` xem H1 đã merge chưa; chưa merge thì DỪNG, báo tôi.

005 Pagination: thêm page-size selector cho /portal/purchase-history và /portal/notification.
   ⚠️ ĐỪNG copy /portal/exam như BA gợi ý — đã kiểm source: selector của exam nằm NGOÀI form và
   nút trang là <span>, tức UI tĩnh không bấm được. Hai trang này ngược lại đã có pager link CHẠY THẬT
   và controller đã nhận tham số (`page_size` ở purchase_history/controllers/portal.py:227,
   `limit` ở notification/controllers/portal.py:139) → làm selector 10/20/50 SUBMIT THẬT, giữ nguyên
   pager link hiện có. BA cho phép ẩn cả khối pagination khi tổng bản ghi ≤ page size.
   Ghi vào ledger phần "phát hiện thêm": pagination /portal/exam là UI tĩnh, cần issue riêng.
006 BackButton: sửa Ở COMPONENT `wj_page_header` nhánh --pc (chủ dự án đã chốt), không sửa lẻ 2 màn.
   variant 'back' PC hiện là icon-only 44×44 dùng chung ~14 màn detail (support, delivery, knowledge,
   notification, return, exam, history, order product…) → đổi thành nút chữ "← Quay lại" 122×40.
   ⚠️ nhánh --m (mobile) GIỮ NGUYÊN icon 40×40 + vùng chạm 44 (chống hồi quy RESP-MOB-SHELL-003).
   Chỉ MỘT nút back, không lặp ở cuối form → gỡ nút "Quay lại" thừa ở portal_support.xml:444,
   portal_return_detail.xml:160, portal_info_request_detail.xml:116, portal_franchise_profile.xml:134.
007 Breadcrumb: thêm cho màn create/detail theo hierarchy thật (Hỗ trợ / Tạo yêu cầu;
   Đặt hàng / Chi tiết sản phẩm). Dùng .wj-pc-page-header__crumb có sẵn — nhưng CHÚ Ý component
   đang dùng là `wj_page_header` (class .wj-page-header__*), không phải .wj-pc-page-header:
   đọc wj_page_header.xml trước, quyết định thêm prop ph_crumb hay đổi sang component kia, rồi HỎI.
   Breadcrumb KHÔNG thay thế BackButton — giữ cả hai (Navigation Rules v1.5).

Verify: DB copy cô lập (công thức ở đầu file này, KHÔNG đụng 8019) + đo ≥6 trang PC 1920
+ regression mobile 391×844 đủ 9 route (wj_page_header dùng chung toàn portal!).
Mẹo đo đã dùng ở WJ-ORD-023: chụp full-page mobile trước/sau rồi so md5 — trùng byte là bằng chứng
"mobile bất biến" mạnh nhất, rẻ hơn liệt kê bbox.
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
