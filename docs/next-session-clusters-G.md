# Cụm G1–G6 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-09-26 (7 issue `Ready for Dev` STT 140–146 trên `5. Issue List`, tra
bằng `issue_queue.py --dev` cùng ngày; Owner=Dev, Need BA Confirm=No, 0 `Retest Failed`). Kế hoạch
phiên: `~/.claude/plans/buzzing-prancing-waterfall.md`; chuẩn nghiệm thu ≥90% → §13
`wujia-compact-summary.md`. Chủ dự án chốt tên lứa là **cụm G**.

> ⚠️ **Đừng nhầm với "G1/G2" ngày 18/09** trong `docs/f-progress.md` — đó là 2 cần gạt nhịp dọc lẻ
> (G2 cũ = hạ header mobile 104 → 72, `7873175`). Từ 26/09, "G<n>" = cụm Issue List trong file này.

**Cách dùng:** `/wujia-start` → nói **"làm cụm G&lt;n&gt;"** → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay. Xong cụm nào thì đánh ✅ + ngày + commit vào bảng "Tiến độ" và viết
mục "🔴 Bài học G&lt;n&gt;" ngay dưới khối prompt (tiền lệ D/E). Mỗi phiên ghi 1 mục vào
`docs/f-progress.md`.

**Ba quyết định chủ dự án chốt 26/09 (đừng hỏi lại):**
1. **Chuẩn hoá component làm trước**, trang/chức năng làm sau: G1 (component mobile dùng chung) →
   G2 (component shell) → G3 (Home PC dùng lại component) → G4 (routing, Suggestion).
2. `WJ-ORD-MOB-SPACING-001` (144) **làm cuối phiên G1**, đo sau khi 143 đã đổi token — BA ghi rõ 144
   phụ thuộc 143 (`Related = UI-MOB-HEADER-DENSITY-001`).
3. Mỗi cụm 1 phiên, 1 lần `-u`, 1 deploy; cụm to (G3) tách a/b.

---

## Tiến độ

| Lượt | Issue (STT) | Module `-u` | Trạng thái |
|---|---|---|---|
| G1 | `UI-MOB-HEADER-DENSITY-001` (143) + `UI-MOB-BOTTOMNAV-DENSITY-001` (145) → cuối phiên `WJ-ORD-MOB-SPACING-001` (144) | `wujia_portal_layout` + `wujia_portal_sale` + `wujia_portal_exam` | ✅ 26/09 — code + đo xong, commit `feat(G1)` (xem git log); **chưa deploy**, ledger chờ `--apply` |
| G2 | `UI-MOB-STORE-SWITCHER-001` (141) + `UI-PC-TOPBAR-REG-001` (140) | `wujia_portal_base` + `wujia_portal_layout` (`wujia_portal_sale` không đụng) | ✅ 29/09 — code + đo xong, commit `6745671`; **đã deploy UAT 30/09**, đo chỉ-đọc đạt; ledger chờ `--apply`. Nghiệm thu `docs/g2-acceptance-matrix.md` |
| G3a | `UI-PC-HOME-REDESIGN-001` (142) — khung | `wujia_portal_base` + `wujia_portal_debt` | ✅ 30/09 — code + đo xong, commit `feat(G3a)` (xem git log); deploy UAT 30/09 cùng G3b, ledger 142 ghi ở G3b. Nghiệm thu `docs/g3-acceptance-matrix.md` |
| G3b | `UI-PC-HOME-REDESIGN-001` (142) — block + responsive, đóng issue | `wujia_portal_base` | ✅ 30/09 — code + đo xong, commit `feat(G3b)` (xem git log), deploy UAT 30/09 16:04 cùng G3a, đo chỉ-đọc sạch, 142 → Ready for Retest. Nghiệm thu `docs/g3-acceptance-matrix.md` §6–§10 (12/12) |
| G4 | `WJ-PORTAL-ROUTING-001` (146) | `wujia_portal_base` (+ `wujia_portal_layout` cho AC4) | ⏸ 30/09 — **dòng 146 không còn trên sheet** (STT nhảy 145 → 147), chờ BA xác nhận xoá hay chuyển chỗ. Cách làm đã chốt, xem khối G4 |
| G5 | `WJ-ORD-028` (148, High) → `WJ-ORD-027` (147) | `wujia_portal_sale` + `wujia_portal_base` + `wujia_portal_layout` | ✅ 30/09 — code + đo xong, commit `887da0a`, push 30/09 ~19:05 · ĐÃ DEPLOY UAT 19:46 (cùng G6) · Nghiệm thu `docs/g5-acceptance-matrix.md` (148 6/6, 147 4/4) |
| G6 | `WJ-ORD-029` (149) | `wujia_portal_purchase_history` | ✅ 30/09 — code + đo xong, commit `9efa67f`, push 30/09 19:39 · ĐÃ DEPLOY UAT 19:46, đo UAT chỉ-đọc 12/12 · Nghiệm thu `docs/g6-acceptance-matrix.md` (5/5) |
| Chốt sổ | End-sprint 64 — chapter 78 + PDF | — (chỉ docs) | ✅ 01/10 — `chapters/78-sprint64-cluster-g-issue-list.tex`, PDF build lại; hàng đợi Dev = 0 |

**Reconcile 26/09** (`git log --all -S"<ID>"` + `grep -rn "<ID>" custom/ docs/qa-issue-ledger.yaml`
cho cả 7 ID): commit nhắc tới chỉ là docs (`1c4f1a0`, `2835f8e`, `8ef3081` — ghi chú review/chapter),
**0 dòng dưới `custom/`, 0 dòng ledger** ⇒ cả 7 chưa fix, không có lượt "chỉ ledger" kiểu B0.

---

## Luật chung cho MỌI lượt G

Dùng nguyên **9 luật chung của cụm E** (`docs/next-session-clusters-E.md` §"Luật chung") — DB giống UAT,
đếm call site bằng cấu trúc, không đụng Khảo sát, bump `?v=` + manifest, ảnh trước/sau ≥2 khổ,
specificity, mutation test, code ít, ledger → `qa_sync.py`. Thêm cho lứa G:

1. **Tầng ADR-027**: sửa dáng ở khung (`wujia_portal_layout`) hoặc ở module sở hữu màn; `portal_base`
   **cấm thêm depend**; không đụng code anh Thái (`wujia_franchise*`, `wujia_portal_inspection`,
   `wujia_mobile_*`).
2. **Khổ đo**: mobile **360×800 · 390×844 · 430** (BA ghi ở cả 141/143/144/145); PC **1440 · 1024 ·
   992/991** (142) và **≥1200** (140). Mọi issue đều yêu cầu **kênh bên kia không đổi** ⇒ bảng đo phải
   có cột "kênh bên kia Δ0".
3. Local `wujia_tea_19` còn trước F7 ⇒ dựng DB copy từ `wujia_frp` + replay `deploy.yml` (bài học
   END-SPRINT 63); Python Mac = env `odoo19`.
4. Thước đo nhịp dọc có sẵn: `docs/mobile-rhythm-acceptance.md` §2 (phép đo 5–6) + `wj_measure`.

---

## G1 — Mật độ mobile: PageHeader · SectionHeader · BottomNav (+ nhịp trang Đặt hàng)

**Issue:** 143 `UI-MOB-HEADER-DENSITY-001` (Medium, Component) · 145 `UI-MOB-BOTTOMNAV-DENSITY-001`
(Low, Component/Accessibility) · 144 `WJ-ORD-MOB-SPACING-001` (Low, trang).
**Thứ tự trong phiên:** 143 → 145 → đo lại `/portal/order` → 144.

**Kết quả mong muốn (nguyên văn BA, rút gọn):**
- 143: mọi trang Portal mobile dùng PageHeader/SectionHeader có nhịp dọc gọn, nhất quán; `/portal/order`
  PageHeader **padding dọc 8px**, SectionHeader **18px/24px**; 360/390/430 title/count không đè, không
  xuống dòng bất thường, không tràn ngang; **PC giữ nguyên**. Dev lập **danh sách route** dùng component +
  evidence trước/sau.
- 145: thanh dưới gọn hơn (**72px + safe area thực tế**), nhãn **12px** đọc rõ, mỗi mục vẫn chạm ~50px,
  không tràn; trang nhóm "Thêm" active đúng; badge Thông báo 1–2 chữ số không đè icon; cuộn cuối
  danh sách/form thấy và bấm được nút cuối; kiểm máy có và không có safe area. PC không đổi.
- 144: `/portal/order` mobile search → chip **12px**, chip → "Danh sách sản phẩm" **8px**; giữ input 44,
  chip, vùng bấm, card/nút giỏ; tìm/lọc/số lượng/thêm giỏ chạy như cũ; **trang khác không đổi vì 144**.

**Seam đã soi (26/09):**
- PageHeader mobile: `wujia_portal_layout/static/assets/css/_components.css:1860`
  `.wj-page-header--m { padding: 12px 0; margin: 0 0 8px; min-height: 52px }` → chỉ hạ **dọc** 12 → 8.
  BA đo "12px 16px" trên UAT: 16 ngang là của PageContainer (E7), **không cộng thêm**. Còn `min-height
  52` + biến thể `--back` (`:1879` padding 5) / `--create` (`:1888` padding 4, nút 44) — phải xét để
  8px thật sự hiện ra. Title `:1873` 22/28 — BA không yêu cầu đổi.
- SectionHeader mobile: `_components.css:1961–1965` `.wj-section-header--m/--any .wj-section-header__title
  { font-size: 20px !important; line-height: 28px }` → 18/24; margin do token `--wujia-m-sechead-mt/mb`
  (`_variables.css:264`). Giữ meta/count không lấn title (`:1920` right slot `nowrap`).
- Call site (đếm grep, phải đếm lại bằng cấu trúc): PageHeader **77 chỗ / 14 module**, SectionHeader
  **57 chỗ / 8 module** ⇒ sửa ở component/token, **cấm override từng trang**.
- BottomNav: token `--wujia-mnav-height: 83px` (`_variables.css:372`) + `--wujia-mnav-total` (`:375`,
  đã cộng safe-area); vỏ `_components.css:1083` (`padding: 6px 0 max(6px, env(safe-area-inset-bottom))`,
  comment "BA final 83px" `:1091`), item `8px 0 4px` gap 5, icon 22, nhãn 11 (`:1100–1120`).
  Người đọc token (phải đo lại hết khi đổi 83 → 72): `_components.css:1314/1329/1331` (thanh dính +
  popup), `_wujia_theme.css:290` (padding cuối trang có sticky action), `wujia_portal_sale/static/src/css/
  portal_order.css:235/405`, `wujia_portal_exam/static/src/css/portal_exam.css:64`.
- 144: nợ **"nhịp G2 cũ"** (`f-progress.md` 18/09): `.wj-filter-card` (`_components.css:238`)
  `margin-bottom:16` chồng `gap` 8 của khung. BA cấm đụng FilterBar chung ⇒ chỉ đặt nhịp ở wrapper
  `.wujia-morder` của `wujia_portal_sale`.

**Câu hỏi treo (hỏi đầu phiên):** 145 đi ngược "BA final 83px" — issue mới thắng (Need confirm = No),
chỉ ghi FYI BA ở LIMIT; không chặn phiên.

**Nghiệm thu:** bảng route × 3 khổ (height PageHeader, cỡ title SectionHeader, cao bottom nav, khoảng
144) + cột PC Δ0 + ảnh trước/sau `/portal/order`, `/portal/return`, 1 trang nhóm "Thêm", 1 form dài.

### 🔴 Bài học G1

- **Số BA đo lệch token không phải do token**: search → chip 23 = `form { margin-bottom: 15px }` toàn cục của
  shell + gap 8. Đo computed style từng phần tử giữa hai khối trước khi đổi token; vá bằng `margin-bottom: calc(12px
  - var(--wujia-mshell-content-gap))` trên chính `form` của trang, không đụng `form` chung.
- **Công thức `--wujia-mnav-total` sai từ trước** (`83 + max(0, safe − 6)` = 111 trong khi nav thật 91) ⇒ sheet
  "Thêm" chồng nav 8px trên máy có safe area. Chỉ lộ khi giả lập safe area bằng CDP
  `Emulation.setSafeAreaInsetsOverride` — Playwright `viewport`/`isMobile` **không** cho `env()` giá trị ≠ 0. Mọi
  lượt đụng nav/sticky phải đo **cả có và không có** safe area.
- **md5 ảnh chụp PC vô dụng**: thanh `.pace` chạy ⇒ 74/81 ảnh lệch dù cùng mã. Dùng **vân tay bố cục** (rect + font +
  padding mọi phần tử đang hiện, bỏ `.pace`) — `scripts/qa/wj_density.py`. Vẫn còn nhiễu bộ đếm lượt xem Kiến thức ⇒
  luôn chạy 1 lượt đối chứng cùng mã để biết nhiễu nền.
- **`--any` nằm ngoài `@media`**: SectionHeader `--any` hiện ở mọi khổ ⇒ cỡ mobile phải bọc `@media (max-width:
  991.98px)`, nếu không PC đổi theo. Kiểu `--m` đã `d-lg-none` nên để ở rule gốc được.
- **DB copy `wujia_frp` không kèm filestore ⇒ bundle JS 500**, trang vẫn vẽ nên dễ tưởng JS chạy. Trước khi smoke
  JS: `delete from ir_attachment where url like '/web/assets/%'` trên DB copy (Odoo tự dựng lại bundle).
- **Chiều cao hàng PageHeader 3 kiểu**: pad 8 cho kiểu back/create thành 58/60 (nút 42/44 tự chiếm chỗ) — phải
  hỏi, chủ dự án chốt cùng 44 (pad 1/0) để chuyển màn không nhảy.

---

## G2 — Shell: Current Store Switcher (mobile) + Top Bar giỏ/Current Store (PC)

**Issue:** 141 `UI-MOB-STORE-SWITCHER-001` (Medium, Component) · 140 `UI-PC-TOPBAR-REG-001`
(Medium, Regression).

**Kết quả mong muốn (nguyên văn BA, rút gọn):**
- 141: dải dưới topbar giống mockup: `[HCM-01] TP HCM Quận 1 — [Quản lý] — chevron-down`; bấm mọi vị
  trí trong vùng mở chọn/chuyển cửa hàng; có trạng thái nhấn/focus; chevron không lệch/tràn; tên dài
  không làm mất vai trò/chevron; 360/390/430 trên mọi trang dùng mobile shell. Không đổi dữ liệu/quyền.
- 140 (PC ≥1200): icon giỏ và chuông nằm giữa circle 40×40, cỡ/nét đồng nhất; badge neo góc trên-phải,
  **không che icon**, không tràn với 0, 4, 2 chữ số; Current Store là **một block**, chip vai trò nằm
  **trong** block, tên dài ellipsis; kiểm `/portal`, `/portal/order`, `/portal/order/cart`; không đổi
  click target, số lượng giỏ, account/language.

**Seam đã soi (26/09):**
- Mobile strip: `wujia_portal_base/views/store_picker_navbar.xml:45–72` (chip `.wujia-store-strip-code`,
  tên, `.wujia-store-strip-role`); chỉ bấm được khi `_wujia_strip_clickable` = có **>1** cửa hàng (modal
  `store_picker_modal` không render khi chỉ 1). CSS `wujia_portal_base/static/src/css/store_picker.css`.
- PC block: template `layout_top_navbar_inherit_store_badge` (`store_picker_navbar.xml:83–113`) — pill vai
  trò là `<span>` **anh em** của `<a.wujia-active-store-badge>` trong `.wujia-store-current-block`
  (`store_picker.css:81–110`) ⇒ nhìn như pill tách rời. Gốc rễ hồi quy phải tìm bằng cascade
  (`git log -L` trên `store_picker.css` + `_pc_account.css` từ UI-01 S34 tới nay), không đoán.
- Giỏ PC: markup `wujia_portal_sale/views/header_cart_inherit.xml:16` (`.wujia-header-cart-count`);
  circle 40×40 cart + bell ở `wujia_portal_layout/static/assets/css/_pc_account.css:241+` (Cụm B
  UI-PC-BASE-011, `@media ≥1200`, thứ tự nạp sau `_components.css` là cố ý).

**Câu hỏi treo (hỏi đầu phiên, KHÔNG tự quyết):**
- (a) User chỉ có **1 cửa hàng**: hiện dải không bấm được — có hiện chevron không (chevron mà không làm
  gì là sai tín hiệu)?
- (b) Nhãn vai trò đang in `Manager/Owner/Staff` (chuỗi Anh trong QWeb), mockup ghi "Quản lý" — kiểm bản
  dịch vi_VN có ăn không hay phải đổi chuỗi nguồn.
- (c) Mockup 141 (BA chốt 19/09): `docs/mockups/UI-MOB-STORE-SWITCHER-001_mockup.png` (1576×3416, Drive
  `1kyhE0p_68wOh79hw2_Rc5mpdBri9i_4O`). Đọc từ ảnh: chip mã `HCM-01` nền xanh nhạt · tên đậm · pill "Quản lý"
  **viền, nền trắng** · chevron-down xanh sát mép phải; vùng dưới header nền trắng/xanh rất nhạt.
- (d) Mockup vẽ dải cửa hàng **cả trên Home**, trong khi code đang cố ý ẩn dải trên `/portal` (Sprint 10, vì hero
  Home đã có cửa hàng + vai trò) — hỏi: bật lại trên Home theo mockup hay giữ ẩn.
- (e) **Mâu thuẫn 140 ↔ mockup V4 (142)**: topbar của V4 vẫn vẽ pill "Quản lý" **tách ngoài** khối Cửa hàng hiện
  tại, còn 140 đòi chip nằm **trong** khối (theo UI-01). V4 ghi "giữ nguyên topbar" ⇒ theo 140; ghi FYI BA ở LIMIT.

**Chủ dự án chốt 29/09:** (a) 1 cửa hàng → ẩn chevron · (b) nhãn vai trò tiếng Việt một nguồn `ROLE_LABELS`
(`wujia_portal_base/models/wujia_franchise_member.py`, `member._portal_role_label()`) ở cả mobile lẫn PC · (d) hiện dải
trên Home · (e) theo 140.

### 🔴 Bài học G2

- **CSS của mình thua `web.assets_frontend` vì thứ tự nạp, không vì specificity**: `.nav-link { display: block }` của
  Bootstrap Odoo (0,1,0) nạp sau ⇒ đè `.wujia-header-icon-btn { display: inline-flex }` cùng specificity. Circle giỏ/chuông
  thành `block` từ cụm B `157814a` (04/08) — không ai thấy vì icon vẫn nằm trong circle, chỉ lệch góc. Mọi rule dáng trên
  phần tử có class Bootstrap (`nav-link`, `badge`, `btn`) phải **tự khai lại `display`** ở rule có specificity cao hơn,
  và đo bằng computed style, không nhìn ảnh.
- **Vuexy `ficon` (0,4,3)**: `.header-navbar .navbar-container ul.nav li i.ficon { font-size: 1.5rem }` — đổi cỡ icon topbar
  phải dùng selector ≥ (0,4,4). Test tĩnh tính specificity (`test_g2_pc_topbar._specificity`).
- **Transition làm sai computed style lúc đo trạng thái**: ép `:active` bằng CDP `CSS.forcePseudoState` rồi đọc ngay ⇒
  vẫn nền trắng. Chờ ≥ thời lượng transition (400ms) rồi mới đọc.
- **Log test không nằm ở `--logfile`**: `wujia_core` chuyển log sang `<logdir>/YYYY/MM/YYYY-MM-DD.log` — tưởng test không
  chạy vì file log trống.
- **Test `post_install` cần `-u` module**: mutation mà không `-u` ⇒ "0 tests", dễ tưởng mutation không đỏ.
- **`display_name` của `wujia.franchise.management` là cột stored**: đo tên dài phải sửa cả `display_name` (SQL tạm, trả
  lại sau đo), sửa mỗi `name` thì trang vẫn in tên cũ.
- **Popup chọn cửa hàng là `#wujiaStoreOverlay` + class `wujia-store-overlay--show`** (JS riêng), không phải modal
  Bootstrap — kịch bản bấm phải chờ đúng id đó.
- **Hai server local dùng chung source**: server của DB cũ (8031) phục vụ luôn CSS mới (bundle dựng lại theo file) trong
  khi view vẫn bản cũ ⇒ "trước" phải chụp **trước khi sửa code** (hoặc worktree riêng), không đo "trước" trên DB cũ sau đó.
- **Probe badge phải bắt chước JS thật**: JS để `hidden` khi số 0; probe gỡ `hidden` sẽ thấy badge "0" hiện (class `badge`
  của Bootstrap thắng `display: none`) — lỗi của probe, không phải của trang.

---

## G3 — Home PC theo mockup V4 (tách G3a / G3b)

**Issue:** 142 `UI-PC-HOME-REDESIGN-001` (Medium, Redesign). **Mockup V4** (BA duyệt 19/09, 1440×1019):
`docs/mockups/Ngo-Gia-Portal-Home-PC-Mockup-V4-1440.svg` (tải 26/09 từ link trong sheet, Drive
`1qRiQp7qB0zo1HCZ6o8ldZ6aH3A9o_JS_`). Xem nhanh: `rsvg-convert -w 1440 <svg> -o /tmp/v4.png`. Chỉ là thước
đo — BA cấm nhúng SVG/ảnh làm màn hình.

**Kết quả mong muốn (nguyên văn BA, rút gọn):** desktop 1440 bám đúng V4; topbar/sidebar giữ nguyên;
hàng đầu chia đôi Cửa hàng hiện tại | Khung giờ đặt hàng; không block xanh đậm lớn, không Thao tác
nhanh; 4 KPI Đơn hàng · Thông báo · Đổi trả · Công nợ; block Đơn hàng gần đây · Yêu cầu đổi trả gần
đây · Giao hàng sắp tới · Thông báo nổi bật · Bài viết/kiến thức mới · Hỗ trợ nhanh · Thông tin cửa
hàng; không mũi tên phải trên KPI/card, chỉ "Xem tất cả"; icon đúng loại từng record; thuật ngữ, nguồn
dữ liệu, trạng thái **như mobile**, tiền VNĐ/₫; không cắt chữ/cuộn ngang ở 1440/1024/992–991; link
hành động như cũ; **Home mobile không đổi**; chuỗi VI/EN/ZH dài.

**Chia lượt:**
- **G3a** — khung: hàng đầu 50/50, 4 KPI (SurfaceCard), bỏ hero + Thao tác nhanh, PageContainer/
  SectionHeader; đo 3 khổ.
- **G3b** — 7 block record (ListCard/DataList + StatusBadge + icon theo loại), VNĐ, chuỗi dài, đóng issue.

**Seam đã soi (26/09):** `wujia_portal_base/views/portal_home.xml` khối desktop `d-none d-lg-block` (từ
dòng 10; comment "home cũ giữ NGUYÊN 100%" — nay là lúc thay). Dữ liệu mỗi block phải lấy **đúng
nguồn Home mobile đang dùng** qua 7 seam `hasattr` sang module L2 (liệt kê ở `docs/f-review-FR-A.md`
§3) — ADR-027: `portal_base` **cấm thêm depend**, không kéo query mới khi seam đã có. Perf 1500 user:
đếm query Home trước/sau (★FR-A đo 17 route × 4 user), Δ query phải giải thích được. Làm **sau G2**
vì khối "Cửa hàng hiện tại" dùng chung ngôn ngữ dáng với block của G2.

### G3a đã xong (30/09) — cái G3b nhận lại

Khối desktop là `<div class="d-none d-lg-block wujia-home-pc">` và có các phần sau:
- `PageHeader`.
- `row wujia-home-toprow`: card `wujia-home-store` | card `wujia-home-window`.
- `section.wujia-home-kpis`: 4 KPI.
- **3 block list cũ** (Thông báo · Đơn · Đổi trả), nằm dưới comment "Block list cũ — G3b thay bằng 7 block V4". G3b xoá
  cả đoạn này.

CSS PC nằm ở `wujia_portal_base/static/src/css/portal_dashboard.css`, khối `@media (min-width: 992px)`. Mọi selector
phải bắt đầu bằng `.wujia-home-pc ` (test `TestHomePcCss` ép luật này).

Công nợ dùng khe biến `home_debt_kpi`: `wujia_portal_debt` đặt biến **trước** khối PC, khối mobile ở sau cùng cấp nên
cũng thấy. Đừng gọi `get_home_debt_kpi()` lần hai (test spy sẽ đỏ).

**Seam cho G3b:**
- ~~Dáng dòng record mobile `.wujia-mdash-row` hiện chỉ có trong `@media (max-width: 991.98px)`.~~ **Sửa ở G3b:** các rule
  `.wujia-mdash-*` ở `wujia_portal_layout/static/assets/css/_components.css:1464–1558` nằm **ngoài** mọi `@media` (khối
  media 1310–1461 đóng trước đó), nên PC cũng nhận. G3b dùng lại markup mobile, chỉ thêm rule PC có tiền tố
  `.wujia-home-pc` để gỡ `nowrap`/ellipsis. Không nới media của layout.
- `HOME_PREVIEW_LIMIT = 2` trùng với số dòng V4 vẽ mỗi block. Nguồn 7 block lấy qua các seam `hasattr` Home mobile đang
  dùng.
- "Tổng tiền" của yêu cầu đổi trả: model không có trường số tiền, nên in "—" hoặc hỏi BA. Hotline "Hỗ trợ nhanh": chưa có
  nguồn, in "—".
- Chữ "…" duy nhất đang còn trên PC nằm ở 3 block list cũ. G3b phải đo lại cắt chữ ở 4 khổ bằng `wj_home_g3.py`.

### 🔴 Bài học G3a

- **DB copy phải thuộc owner `odoo19`**: `createdb -T` chạy bằng user Mac thì DB thuộc `huyban2003`. Odoo
  (`db_user = odoo19`, `list_db`) không thấy DB, `/portal` trả 404 rồi chuyển sang `/web/database/selector`. Sửa bằng
  `alter database <db> owner to odoo19`. `psql` không có `-d` thì hỏng vì không có DB `huyban2003`, nên dùng
  `-d postgres`.
- **Đếm query cần server riêng chạy `--log-handler=werkzeug:INFO`.** Server để mặc định không in dòng
  `"GET /portal" 200 - <nq>`. Log nằm trong `<logdir>/YYYY/MM/<ngày UTC>.log`: 17h55 ngày 30 giờ VN vẫn ghi vào file
  ngày 29.
- **Δ query lớn hơn số lệnh gọi đã xoá.** Plan dự tính −3, đo ra −7: `display_name` / đơn vị tính của sản phẩm top được
  đọc kèm (prefetch). Muốn giải thích Δ thì đo từng đoạn bằng `cr.sql_log_count` trong odoo shell, đừng đếm theo code.
- **`t-set` chèn bằng xpath `position="before"`** dùng chung phạm vi với mọi anh em phía sau cùng cha. Cách này cho hai
  kênh dùng chung một lần gọi mà không cần depend.
- **Test đọc chuỗi arch phải bỏ comment trước**: comment giải thích "không Thao tác nhanh" làm test cấm chuỗi đó tự đỏ.
  Xem helper `_src()` trong `test_g3a_home_pc.py`.
- **Patch `request` của controller bằng `new=SimpleNamespace(env=…)`.** Để `patch()` tự tạo MagicMock thì nó soi werkzeug
  `LocalProxy` và sập ngoài request.
- **Đổi nhãn trên Home thì grep test của module khác.** F11 (`wujia_portal_notification`) dùng regex bám nhãn PC "Thông
  báo chưa đọc", và chỉ suite đủ 20 module mới bắt được. Test tag riêng của phiên thì xanh.

### 🔴 Bài học G3b

- **Sửa CSS mà không `-u` thì bundle cũ vẫn phục vụ.** Server đang chạy không build lại `web.assets_frontend` khi file CSS
  đổi. Đo ngay sau khi sửa thì xoá `delete from ir_attachment where url like '/web/assets/%'` rồi tải lại trang.
- **Đừng tin ghi chú seam về media query, mở file ra đếm ngoặc.** Ghi chú G3a nói `.wujia-mdash-*` chỉ ở mobile; thực tế
  nằm ngoài `@media`. Soi sai sẽ dẫn tới chép cả khối dáng dòng sang PC.
- **Trang cổng nạp cả BS5 (`web.assets_frontend`) và BS4 `bootstrap.css` của Vuexy.** `.col-lg-6` nạp sau có thể đè
  `.col-xxl-4`, nên lưới nhiều ngưỡng dùng CSS grid riêng (`grid-template-columns`) thay cho class cột.
- **Sidebar PC chỉ hiện từ 1200.** Vùng nội dung ở 1200 (~890) hẹp hơn ở 1199 (~1150). Chọn ngưỡng cột theo bề rộng vùng
  nội dung đo được, đừng theo khổ màn. Đo cả 1200 và 1199.
- **CardHeader trong card hẹp tự xuống dòng**: `flex-wrap` mặc định đẩy "Xem tất cả" xuống dòng riêng khi tiêu đề dài.
  Trong card hẹp đặt `nowrap` + `__lead{flex:1 1 0}` + `__action{flex:0 0 auto}`.
- **Empty state `--row` có khung riêng** (nền, viền, min-height). Đặt trong SurfaceCard thì thành card lồng card, phải bỏ khung
  trong phạm vi PC.
- **`conda run` không chuyền stdin**: heredoc vào `conda run -n odoo19 python -` chạy rỗng, không báo lỗi. Gọi thẳng
  `/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python`.
- **BSD `sed` trên Mac** không nhận `sed -n "$((n-1)),…"` khi biểu thức ra số âm/rỗng ("illegal option"). Dùng Read tool
  hoặc `awk 'NR>=a && NR<=b'`.
- **`-u wujia_portal_base` kéo theo module phụ thuộc** (`wujia_portal_debt` …) nên một lệnh `-u` phủ cả hai. `deploy.yml`
  cũng chỉ ghi `wujia_portal_base`; debt đi theo.
- **Push lên `main` tự deploy UAT** (runner self-hosted của `.github/workflows/deploy.yml`). Push = deploy, phải qua cổng
  duyệt.
- **Test render tài khoản chủ tiệm**: ô Người phụ trách in tên chính chủ, không ra "—". Test "—" chỉ bám ô Địa chỉ /
  Điện thoại của cửa hàng mới.

---

## G4 — Điều hướng URL gốc `/` theo phiên + loại user

**Issue:** 146 `WJ-PORTAL-ROUTING-001` (Suggestion, Functional). BA chốt module: `wujia_portal_base`,
không đặt ở `wujia_core`, không model/field mới. Odoo Fit = **Need Dev Confirm**.

**Kết quả mong muốn (AC nguyên văn BA):** AC1 chưa đăng nhập / hết phiên → `/portal/login`, không hiện
Website Odoo · AC2 internal user → `/web` · AC3 portal user → `/portal` (giữ quyền/membership) · AC4
internal login tại `/portal/login` từ luồng `/` → `/web`, portal user → `/portal` · AC5 không redirect
loop, link chi tiết mở thẳng không bị ép về trang chủ, không tăng quyền, hồi quy login/logout/hết phiên
trên PC/mobile.

**Seam đã soi (26/09):** `custom/` chưa có route `/`; trang Website hiện ra ⇒ module `website` đang giữ
`/` trên UAT. Luồng sau đăng nhập: `portal_post_login_redirect` (`wujia_portal_layout/controllers/
auth.py:79`) — AC4 bám vào đây.

**Câu hỏi treo (hỏi đầu phiên):** `portal_base` không được depend `website` ⇒ fork cách giành `/`
(kế thừa `web` Home + xử lý khi `website` có cài theo thứ tự MRO, hay tắt trang chủ website bằng cấu
hình). Đầu phiên: đọc RPC chỉ-đọc UAT `ir.module.module` xem `website` có `installed` không, rồi hỏi.

**Đã soi + chủ dự án chốt 30/09 (đừng hỏi lại):**
- UAT: `website` + `website_sale` **installed**, `website.homepage_url` rỗng ⇒ `/` trả 200 "Home | My Website".
  `/portal` khi chưa đăng nhập → `/web/login?redirect=/portal` (không phải `/portal/login`).
- **Override `Home.index` KHÔNG ăn**: `website.Website` kế thừa `portal.Home`, `portal` depend `auth_signup` ⇒ lá
  `WujiaAuthController(AuthSignupHome)` định nghĩa trước; `odoo/http.py:872` ghép `type(..., reversed(leaf_controllers))`
  ⇒ lá website đứng trước trong MRO và thắng. `homepage_url=/portal` không tách được user nội bộ / cửa hàng.
- **Cách chốt:** kế thừa model `ir.http` trong `wujia_portal_base`, `_pre_dispatch` bắt rule `/` (cả `/<lang>/` nếu
  website đổi) → chưa đăng nhập `/portal/login` · `base.group_user` → `/odoo` (= `/web` bản 19) · còn lại `/portal`.
  Không depend `website`, cùng hành vi dù `website` có cài hay không. AC4 (`/portal/login` POST) code hiện đã đúng.
- **Phạm vi hết phiên chốt rộng:** mọi route `/portal/*` hết phiên/chưa đăng nhập → `/portal/login?redirect=<url>`
  (thay vì `/web/login`), link sâu mở lại đúng trang sau đăng nhập (AC5). Test hồi quy login/logout/hết phiên PC + mobile,
  không redirect loop, `/web/login` của user nội bộ giữ nguyên.

---

**Vì sao bỏ G4 (ghi 30/09):** BA xoá dòng 146 khỏi sheet sau khi phân cụm; lúc đó G4 **chưa có dòng code nào** (git + UAT
đều không có). Khối trên giữ nguyên để làm tiếp nếu BA mở lại. Lứa mới đánh số tiếp **G5, G6**.

---

## G5 — Đặt hàng: hộp xác nhận gửi đơn (148) + tìm/lọc giữ query cũ (147)

**Nguồn:** `issue_queue.py --dev` 30/09 ra 3 issue BA mở 29/09 (exploratory UAT, đơn test S00075). Reconcile
`git log --all -S` + `grep custom/` + ledger: 0 dòng code (028 chỉ có dòng nhắc trong nhật ký `de5b913`).
Plan phiên: `~/.claude/plans/wondrous-munching-taco.md`.

**148 `WJ-ORD-028` (High, POR-018) — AC nguyên văn BA:** GIVEN giỏ có dữ liệu WHEN bấm "Gửi đơn đặt hàng" THEN chưa
tạo SO và hiển thị modal tóm tắt. WHEN bấm Hủy THEN đóng modal, giữ nguyên giỏ và không tạo dữ liệu. WHEN bấm Xác nhận
THEN tạo đúng một SO, chuyển sang màn kết quả và làm rỗng giỏ. Double-click/refresh không tạo đơn trùng. Modal tối thiểu:
số mặt hàng, tổng số lượng, tổng thanh toán, cửa hàng đang thao tác, ghi chú; 2 action Hủy | Xác nhận gửi đơn.

**147 `WJ-ORD-027` (Medium, POR-015) — AC nguyên văn BA:** GIVEN đang có kết quả Matcha WHEN đổi keyword sang chuỗi
không tồn tại và bấm Tìm kiếm THEN URL/query dùng keyword mới và hiển thị trạng thái không có kết quả. GIVEN đổi danh
mục THEN request và danh sách dùng đúng danh mục mới. Desktop/mobile tương đương; Enter và click tương đương; không giữ
kết quả cũ. Đề xuất: reset về trang 1, giữ điều kiện khi phân trang và Back/Forward.

**Chủ dự án chốt 30/09 (đừng hỏi lại):** 148 **không đổi schema** — khoá nút + overlay cả PC lẫn mobile; server giữ
khoá NOWAIT `_lock_lines`; submit gặp `CART_EMPTY` mà có đơn portal draft/sent của đúng cửa hàng + user vừa tạo ≤2 phút
⇒ chuyển sang màn kết quả của đơn đó thay vì báo giỏ trống. 147 **tái hiện trước rồi mới sửa ở gốc**.

**Seam:** nút submit `pc_cart_panel.xml:123` · `portal_order_cart.xml:143`; overlay mobile `portal_order.js` (#wj-order-submitting);
route `portal_order_submit` (`controllers/portal.py`); modal PC mẫu `wj-pc-modal` (`wujia_portal_debt`). 147: form FilterBar PC +
form mobile cùng `name=keyword` trên `/portal/order`; lọc không reload `wujia_portal_base/static/src/js/wj_ajax_list.js`
(dùng chung 11 màn); fragment `/portal/order/results`. Đua submit: `scripts/qa/cart_race.py`.

### 🔴 Bài học G5

- **Khoá dùng chung phải có đường nhả cho trang không tải lại.** CMP-BTN-001 (E6a) cắm cờ `wjSubmitting` lên form và chỉ
  gỡ ở `pageshow`. Mọi form gửi bằng JS rồi Ở LẠI trang (lọc `wj_ajax_list`) chỉ gửi được 1 lần — 147 là triệu chứng
  trên 11 màn, BA chỉ thấy ở Đặt hàng. Nay: `wj:form:release` (bắn trên form) là hợp đồng nhả khoá; trang nào tự
  submit bằng JS mà không rời trang phải bắn nó.
- **Không kiểm lại cờ của lớp khác.** Listener overlay mobile tự kiểm `wjSubmitting` — cờ do khoá chung (pha capture)
  cắm TRƯỚC ⇒ tự chặn lần gửi đầu: nút "Gửi đơn đặt hàng" mobile chết lặng từ E6a, không test nào bắt vì không có
  test bấm thật. Bộ đo tạo đơn thật (`wj_order_confirm.py`, chỉ localhost) bắt được ngay.
- **Đo "gửi lại" phải so URL, không chỉ đếm request.** Lượt đầu bộ `wj_resubmit` đếm 0 request ở 3 màn vì chúng tải
  route fragment `<path>/results` — khớp cả `path` lẫn `path + '/results'`.
- **Test E6 ghim móc JS** (`MOC_JS`): đổi cách JS bắt nút (lớp → data-attr) thì sửa móc trong test, đừng nhét lại lớp
  cũ vào JS cho xanh.
- **Kế thừa class test của module khác:** import MODULE (`from . import test_f6 as f6`), không import class — loader
  Odoo gom mọi TestCase trong namespace nên sẽ chạy lại cả F6. Tắt test cha bằng gán `None`, nhưng chỉ cho method
  (`test_cursor_lock_timeout` cũng bắt đầu bằng `test_` — gán None ⇒ mọi request HttpCase 500).
- **Đo trước/sau cùng DB, cùng giỏ:** git worktree HEAD làm `--addons-path` + `-u` qua lại; vân tay `wj_density` là
  hộp + style (không gồm chữ) — đổi chữ không xê dịch sẽ ra Δ0, nội dung chữ phải có bộ đo riêng.
- Runner deploy có thể bỏ lỡ một lượt push (lần 2: G3a, G5) — luôn đọc version UAT qua XML-RPC, đừng tin "đã push".

---

## G6 — Lịch sử: "Ngày xác nhận" chỉ khi đơn đã xác nhận (149)

**149 `WJ-ORD-029` (Medium, POR-013) — AC nguyên văn BA:** GIVEN SO ở draft hoặc sent WHEN mở list/detail lịch sử THEN
không hiển thị "Ngày xác nhận"; trạng thái vẫn là Chờ xác nhận và có thể hiển thị Ngày đặt hàng = create_date. GIVEN SO ở
sale/done THEN hiển thị Ngày xác nhận = date_order theo timezone người dùng. Filter/sort/label dùng đúng nghĩa; không thay
đổi dữ liệu sale.order.

**Chủ dự án chốt 30/09:** cột "Ngày xác nhận" bảng PC ghi "—" khi draft/sent; chi tiết ẩn hẳn dòng, nhãn "Ngày tạo" →
"Ngày đặt hàng" (vẫn `create_date`). Chỉ `state == 'sale'` mới có ngày xác nhận (Odoo 19 không có `done`).

**Seam:** `_history_row_vals` / `_history_detail_vals` (`wujia_portal_purchase_history/controllers/portal.py`) + `views/portal_history.xml`
(cột PC, kv chi tiết). Lọc ngày đã dùng `create_date` — không đổi. Đơn huỷ bị loại khỏi Lịch sử ⇒ nhánh cancel ghi LIMIT.

### 🔴 Bài học G6

- `sale.order.date_order` của Odoo = giờ tạo cho báo giá, bị ghi đè lúc `action_confirm` ⇒ KHÔNG bao giờ in nó dưới
  nhãn "Ngày xác nhận" mà không kiểm `state == 'sale'`. Tách key mới (`confirm_date`) thay vì đổi nghĩa key cũ để
  caller khác (Home) không vỡ.
- Ẩn một ô trong lưới kv 2 cột: đo lại chiều cao 2 card cạnh nhau (ở đây vẫn bằng nhau vì card giao hàng 4 ô).
- Bộ đo chỉ-đọc cho user nhiều cửa hàng phải cho lọt `/portal/franchise/switch` (overlay bắt chọn cửa hàng lúc vào);
  thiếu thì điều hướng bị huỷ → `chrome-error://`.
- `qa_sync --apply` văng `JSONDecodeError` **sau khi** bridge đã ghi 6 ô ⇒ bước History bị bỏ. Đọc lại bằng CSV
  trước; đừng chạy lại `--apply` (History sẽ ghi "cũ = Ready for Retest"), chỉ `append_row` dòng thiếu rồi đọc lại.
