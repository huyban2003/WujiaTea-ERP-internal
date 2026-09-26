# Cụm G1–G4 — prompt cho từng session

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
| G1 | `UI-MOB-HEADER-DENSITY-001` (143) + `UI-MOB-BOTTOMNAV-DENSITY-001` (145) → cuối phiên `WJ-ORD-MOB-SPACING-001` (144) | `wujia_portal_layout` + `wujia_portal_sale` (+ `wujia_portal_exam` nếu chỉnh offset thanh dính) | ☐ |
| G2 | `UI-MOB-STORE-SWITCHER-001` (141) + `UI-PC-TOPBAR-REG-001` (140) | `wujia_portal_base` + `wujia_portal_sale` (+ `wujia_portal_layout` nếu sửa action circle) | ☐ |
| G3a | `UI-PC-HOME-REDESIGN-001` (142) — khung | `wujia_portal_base` | ☐ — **chờ mockup V4** |
| G3b | `UI-PC-HOME-REDESIGN-001` (142) — block + responsive, đóng issue | `wujia_portal_base` | ☐ |
| G4 | `WJ-PORTAL-ROUTING-001` (146) | `wujia_portal_base` (+ `wujia_portal_layout` cho AC4) | ☐ |

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
- (c) Mockup 141 chỉ có trên Drive (link trong sheet) — cần file trước phiên.

---

## G3 — Home PC theo mockup V4 (tách G3a / G3b)

**Issue:** 142 `UI-PC-HOME-REDESIGN-001` (Medium, Redesign). **Điều kiện tiên quyết:** mockup SVG V4
(BA duyệt 19/09) chỉ có trên Drive — chưa có bản local ⇒ chủ dự án chia sẻ/tải về trước G3a.

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

---
