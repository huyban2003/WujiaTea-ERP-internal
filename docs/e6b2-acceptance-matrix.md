# E6b2 — Ma trận nghiệm thu · Button `CMP-BTN-001` cho màn Đặt hàng/giỏ + màn auth

Lượt thứ ba của cụm **E6** (`UI-BUTTON-001`, STT 132). E6a dựng atom + thước đo + 21 call site mẫu;
E6b1 migrate 32 call site nghiệp vụ + luật ranh giới thanh lọc. **E6b2** phủ nốt hai nhóm khó nhất:
**giỏ hàng/đặt hàng** (có JS bám class) và **màn auth** (nằm ngoài vỏ portal, CSS nạp sau design system).
**Issue vẫn mở** — đóng ở E6c. **Chưa deploy UAT** (E6c gộp một lần), theo chốt của chủ dự án đầu phiên.

- Spec nguồn: tab `UI Component` gid `488333015` dòng 40, `BA Confirmed` 26/08/2026.
- Đo: DB local `wujia_e4b1`, server **8090/8091** (`--dev=assets`), test **8098/8099**, login `em.hcm`
  (+ `anh.owner` cho trạng thái **giỏ rỗng**, + context **chưa đăng nhập** cho 2 màn auth).
- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (mã anh Thái).
- Không đổi quyền / controller / dữ liệu / workflow — chỉ class + CSS + sổ test + thước đo.

## Phạm vi đã làm — 19 call site / 6 file / 2 module

| Module | File | Call site về atom |
|---|---|---|
| `wujia_portal_sale` | `views/portal_order_cart.xml` | 3 — CTA giỏ rỗng · xóa dòng · gửi đơn |
| `wujia_portal_sale` | `views/pc_cart_panel.xml` | 3 — tiếp tục chọn · xóa dòng · gửi đơn |
| `wujia_portal_sale` | `views/portal_order_product_detail.xml` | 2 — thêm vào giỏ · xem giỏ |
| `wujia_portal_layout` | `views/login_page.xml` | 6 — đăng nhập · 2FA · quên MK · đặt lại MK · 2 nút khối đăng ký |
| `wujia_portal_layout` | `views/forgot_pass.xml` | 2 — khối legacy tiếng Anh |
| `wujia_portal_layout` | `views/change_password_page.xml` | 3 — Hủy · Lưu (PC) · Lưu (mobile) |
| **Tổng** | 6 file / 2 module | **19 call site** |

Lệch plan: plan đếm 20; thực tế `change_password_page.xml` chỉ có **3** nút (plan tách nhầm cặp
Hủy/Lưu PC thành 2 dòng rồi cộng thêm 1) ⇒ **19**.

## Bảng nghiệm thu — theo 12 gạch `Kết quả mong muốn` của BA

| # | Gạch của BA | Phép đo | Kết quả |
|---|---|---|---|
| 1 | Mọi action dùng atom chung, hết Bootstrap/class riêng theo route | `test_khong_con_ho_class_cu` (18 dòng sổ) · thước đo mã `HỌ CŨ` | ✅ 19/19 call site · **họ `wj-cta-btn` bị xoá hẳn** (người dùng cuối cùng đã đi) · sạch `btn-primary/outline-primary/outline-secondary/btn-block`, `wj-empty-state-btn`, `wj-pc-btn--secondary`, `wj-pc-btn--disabled` |
| 2 | Variant đúng nghĩa · **≤1 Primary mỗi action area** | thước đo mã `PRIMARY` | ✅ 0 vi phạm. 60 ô atom của 5 màn E6b2: **primary 28 · ghost 24 · secondary 8** |
| 3 | PC 32/40/46 · mobile 36/44/48 · chạm ≥44 | thước đo `getComputedStyle` + hộp chạm (kể cả pseudo), **29 route × 5 khổ** | ✅ **338 ô atom** toàn portal: PC **32**×219, **40**×57, **46**×12; mobile **36**×8, **44**×30, **48**×12 · hộp chạm mobile nhỏ nhất **44**. Riêng 5 màn E6b2: PC 32×18 / 40×12 / 46×12 · mobile 44×10 / 48×8 |
| 4 | Radius / typo / padding / gap / màu theo token | thước đo `RADIUS`/`TYPO` | ✅ radius **8**×227 (sm) / **12**×111 (md-lg) · typo 3 bậc đúng · 0 vi phạm |
| 5 | Đủ default/hover/focus-visible/pressed/disabled/loading | hợp đồng khung E6a + `test_ghost_tu_khai_trang_thai_nhan` | ✅ thêm **trạng thái nhấn cho variant `ghost`** (xem *Quyết định 4*) · 0 màn nào khai lại dáng |
| 6 | Semantic đúng · IconButton có tên đọc được · Tab/Enter/Space · focus nhìn rõ | tab-walk thật + `test_icon_only_co_ten_doc_duoc` | ✅ 0 nút thiếu focus ring · **2 nút icon mới có `aria-label`**: xóa dòng giỏ (mobile + PC) |
| 7 | Điều hướng = link, tại chỗ = button, disabled không click/focus | mã `SEMANTIC` | ✅ 0 vi phạm — *Chọn sản phẩm*, *Tiếp tục chọn*, *Xem giỏ* là `<a>`; gửi đơn/xóa/lưu là `<button>` |
| 8 | FormActionBar: Primary ngoài cùng phải | soi 3 vùng hành động có ≥2 nút | ✅ chi tiết sản phẩm `Thêm vào giỏ(primary) ← Xem giỏ(secondary)`; đổi MK PC `Hủy(secondary) → Lưu(primary)`; panel giỏ PC `Tiếp tục chọn(secondary)` trên, `Gửi đơn(primary)` dưới |
| 9 | Không đổi quyền/dữ liệu/controller/workflow | `git status`: **0 file `.py`** ngoài 2 `__manifest__.py` + 2 sổ test + thước đo `scripts/qa/` | ✅ |
| 10 | Không scroll ngang / layout shift / bị BottomNav che | `wj_measure` + đo `scrollWidth` từng màn | ⚠️ giỏ/đặt hàng **0 tràn**; `/portal/login@390` **tràn 74px** — xem *Phát hiện ngoài phạm vi* |
| 11 | Regression 1440/1024/992/390/360 + **zoom 200%** | 29 route × 5 khổ; zoom 200% = khổ **720**/**512** | ✅ **0 vi phạm** cả hai lượt · **0 lỗi JS** |
| 12 | Retest 13 route đại diện, nhãn dài, submit lặp, bàn phím | — | ◻ **để E6c** (nhãn dài VI/EN/ZH + submit lặp trên máy chủ) |

Ngoài bảng BA: `wj_filterbar` **0 lệch so với mốc E4** · `wj_listcard` **0** · `wj_nesting` **0** ·
`b4_regression` **286/286** · `check_layers` **3 R1–R5 + 2 R7 có sẵn**, không thêm.

## Hai IMPACT (cần BA nhìn ảnh)

| IMPACT | Trước | Sau | Vì sao |
|---|---|---|---|
| Nút submit màn auth (đăng nhập · quên MK · đặt lại MK · 2FA) trên PC | **50px** (`_auth.css` tự khai) | **46px** | bậc `lg` của `CMP-BTN-001` là 46 trên PC. Mobile **giữ 48** — trùng luôn với bậc `lg` mobile |
| Nút *Lưu mật khẩu* mobile (`/portal/change-password`) | **46px** | **48px** | 46 là số PC dùng nhầm cho mobile; bậc `lg` mobile của BA là 48 |

Nhịp dọc Figma S39 **không đổi**: `.wj-auth-submit` chỉ còn giữ `margin-top: 21px` (PC) /
`20.5px` (mobile), mọi khai dáng khác đã gỡ. Ảnh: `scratchpad/e6b2/before|after/portal_login@*.png`,
`portal_change-password@390.png`.

## Ảnh trước/sau (`scratchpad/e6b2/before|after`, 6 màn × 2 khổ)

| Màn | @1440 | @390 | Đọc số |
|---|---|---|---|
| `/portal/login` | cao **−4px** (917→913) | 3.87% | submit 50→46; mobile chỉ đổi vài px nhịp dọc |
| `/portal/forgot-pass` | 5.12% | 3.87% | như trên |
| `/portal/change-password` | 0.56% | 5.28% | PC đổi cặp Hủy/Lưu về atom; mobile submit 46→48 |
| `/portal/order/cart` | 0.74% | 8.09% | nút xóa về `wj-iconbtn--ghost`, submit về bậc `lg` |
| `/portal/order/product/4` | 0.29% | cao **+2px** | *Thêm vào giỏ* rời họ `wj-cta-btn` |
| `/portal/order` | 0.14% | 0.06% | **chỉ khác dữ liệu** — xem dưới |

`/portal/order` là màn chứa toàn bộ nhóm **boundary**. Chênh lệch đã soi bằng hộp bao
(`scratchpad/e6b2/diff_box.py`): @1440 chỉ khác ở **x ≥ 930** — đúng vùng panel giỏ bên phải; @390 khác
ở đúng ô số lượng và dòng tổng tiền. Cắt ảnh ra xem (`crop_order390_*.png`): số lượng 1→2, tổng
395.000→908.500 — **do chính tôi gieo giỏ để đo**, không phải đổi dáng. Nút thêm-vào-giỏ theo hàng,
stepper, nút tìm của thanh lọc, thanh nổi *Xem giỏ*: **giống hệt**.

## Boundary — giữ nguyên, ghim bằng test chiều ngược

| Nhóm | Class | Lý do |
|---|---|---|
| Nút bước số lượng | `wujia-mcart-step*`, `wujia-morder-mstep*`, `wj-pc-cart-step` | BA liệt QuantityStepper là component riêng |
| Thêm-vào-giỏ theo hàng | `wujia-morder-row-add`, `wujia-morder-add-btn`, `wj-pc-order-add` | **chốt của chủ dự án**: cùng thể với stepper — đổi dáng theo trạng thái giỏ bằng JS |
| Nút tìm của thanh lọc | `wujia-morder-search-btn` | E4 FB-08 sở hữu (42/38/32) |
| Thanh nổi *Xem giỏ* | `wujia-morder-floatbar-btn` | là `<span>` trong link — cùng loại BottomNavigation |
| Con mắt trong ô mật khẩu | `wj-auth-eye`, `wj-pc-acct-eye`, `wujia-maccount-eye` | affordance **trong** field (absolute), không phải nút hành động — đo ra 17–19px (PC) / 34px (mobile), đúng thiết kế |
| Nút icon navbar · `/my/franchises` | — | LIMIT đã ký ở E6b1 |

`TestBoundaryManDatHang` bắt hai chiều: (A) không nhóm nào mang `.wj-btn`/`.wj-iconbtn`;
(B) từng nhóm vẫn còn khối CSS dáng riêng của nó.

## Móc JS — luật kế thừa từ E6b1

Grep ra **đúng hai** tên class mà JS bám: `.btn-add-cart-detail` (`portal_order.js:67`) và
`.wujia-mcart-submit` (`:143`, `:158`) ⇒ **giữ nguyên hai tên đó làm móc**, nhưng **gỡ sạch khai dáng**
của chúng khỏi `portal_order.css`. Bốn tên còn lại (`wj-pc-cart-submit`, `wj-pc-cart-del`,
`wujia-mcart-del`, `wujia-mcart-empty-cta`) **không ai bắt** ⇒ chỉ còn giữ phần bố cục
(`flex`, `margin-top`), dáng về atom. `TestMocJsGioHang` ghim cả hai vế: móc còn đủ hai phía,
và móc **không được khai** `height|border-radius|background|font-size|font-weight`.

## Test và mutation

- Suite: **722 tests, 0 failed, 0 error** (mốc E6b1 **714** ⇒ **+8 test mới**).
- Mutation **11/11 mũi đỏ đúng guard của nó** — M1–M10 trong `scratchpad/e6b2/mutations.py`,
  M11 chạy tay sau khi thêm guard cho `ghost`:

| Mũi | Phá | Phải đỏ ở |
|---|---|---|
| M1 | nút thêm-vào-giỏ theo hàng bị kéo về atom | `test_nhom_boundary_khong_mang_atom` |
| M2 | stepper giỏ mobile bị kéo về atom | `test_nhom_boundary_khong_mang_atom` |
| M3 | đổi tên móc JS ở view (giỏ chết lặng) | `test_moc_con_du_hai_phia` |
| M4 | móc JS giành lại dáng | `test_moc_js_chi_la_moc_khong_con_dang` |
| M5 | `_auth.css` giành lại chiều cao 50px cũ | `test_khung_khong_con_khai_dang_nut_auth` |
| M6 | họ `.wj-pc-btn--disabled` sống lại | `test_trang_thai_disabled_dung_cua_atom` |
| M7 | nối controller cho template auth chết | `test_template_auth_chet_van_chua_ai_render` |
| M8 | rớt call site: nút *Xem giỏ* về Bootstrap | `test_khong_con_ho_class_cu` |
| M9 | atom bậc `lg` lệch số BA (46 → 36) | thước đo mã `SIZE` |
| M10 | sổ `MIGRATED` ghi route không dựng nổi nút | thước đo `KHÔNG CÓ NÚT HÀNH ĐỘNG NÀO` |
| M11 | gỡ trạng thái nhấn của `ghost` | `test_ghost_tu_khai_trang_thai_nhan` |

M9 bản đầu là "bỏ `wj-btn--lg`" — **vô hiệu**, vì nút rơi xuống bậc `md` 40px **vẫn là một số hợp lệ**
của BA nên không guard nào đỏ. Đã đổi thành ép `.wj-btn--lg { height: 36px }`: thước đo đỏ mã `SIZE`
**ở cả màn giỏ lẫn màn auth** — tiện chứng minh luôn rằng màn auth thật sự đang được đo.

## Thước đo — sửa trong phiên

1. **Đo được màn chưa đăng nhập.** Thước đo cũ `login()` rồi mới chạy nên không với tới auth. Thêm
   danh sách **`ANON`** (`/portal/login`, `/portal/forgot-pass`) đo trong context trình duyệt sạch sau
   vòng chính, kèm cờ `--no-anon`.
2. **Báo mã HTTP.** Lần đo đầu màn quên mật khẩu báo "KHÔNG CÓ NÚT HÀNH ĐỘNG NÀO" — sai sự thật: trang
   trả **HTTP 429**. `/portal/forgot-pass` có `rate_limit(max_calls=10, window_sec=3600)` theo IP
   (`controllers/auth.py:89`), đo lặp là hết lượt. Nay thước đo in thẳng `HTTP <mã> — mọi số đo bên
   dưới vô nghĩa`, và bộ đếm nằm trong RAM nên **khởi động lại server là sạch**.
3. Chuyển `/portal/order`, `/portal/order/cart`, `/portal/change-password` từ `WATCH` sang `MIGRATED`;
   thêm màn **chi tiết sản phẩm dò động** (`DYNAMIC['@product_detail']`).
4. `wait_until='load'` thay `networkidle` — `/portal/order` có long-poll `bus.bus` nên `networkidle`
   không bao giờ tới.

## Bẫy "Pass rỗng" gặp lại — trạng thái giỏ

Nút *Gửi đơn* và *Xóa dòng* **không tồn tại khi giỏ rỗng**, còn CTA *Chọn sản phẩm* **chỉ tồn tại khi
giỏ rỗng** — một tài khoản không đo nổi cả hai. Cách giải: đo trạng thái có hàng bằng `em.hcm` (gieo
3 dòng qua đúng giao diện, `scratchpad/e6b2/seed_cart.py`), đo trạng thái rỗng bằng `anh.owner` —
giỏ rỗng sẵn (`empty_cart_probe.py`): **4 action / 4 atom / 0 vi phạm**, mobile `lg/primary 48 r12`,
PC `sm/ghost 32 r8` + `lg/primary 46 r12`.

## Quyết định trong phiên

1. **Auth migrate HẾT, kể cả khối legacy tiếng Anh** (chốt của chủ dự án). Ba template
   `signup`, `login_totp`, `forgot_pass_back` **không controller nào render** — vẫn migrate cho đồng
   bộ nhưng **không có bằng chứng đo bằng trình duyệt** ⇒ ghim đúng sự thật đó bằng
   `test_template_auth_chet_van_chua_ai_render`: ngày nào có controller render, test đỏ để bắt đi đo thật.
2. **`_auth.css` phải nhường atom.** Màn auth **có** nạp design system (`login_layout` → `asset_frontend`),
   nên không cần đụng asset bundle — nhưng `asset_css_authentication` nạp **SAU** `_components.css`,
   nên mọi khai dáng còn sót ở đó đều **thắng** atom. Đó chính là cơ chế đã giữ nút auth ở 50px. Đã gỡ
   dáng, chỉ để lại `margin-top` (bố cục Figma).
3. **Xoá hẳn họ `wj-cta-btn`** (31 dòng `_components.css`): sau E6b1 chỉ còn đúng một người dùng là
   nút *Thêm vào giỏ*; migrate xong là họ này hết người.
4. **Variant `ghost` tự khai trạng thái nhấn, không mượn marker `wj-state-surface` của F4.** Nút xóa
   dòng giỏ trước đây mang marker để có hover/nhấn; nay là atom nên bỏ marker (F4 đếm 3 → 2, đúng tiền
   lệ E6b1 với nút PDF công nợ). Nhưng danh sách bề mặt của `_interaction.css` hover thêm **viền + bóng**
   — sai dáng cho nút icon trong hàng ⇒ khai riêng `:active` cho `ghost` ngay tại atom.

## Phát hiện ngoài phạm vi (không sửa trong E6b2)

**`/portal/login` tràn ngang 74px ở khổ 390** (`scrollWidth` 464 > 390). Thủ phạm: khối trang trí
`.wj-auth__decor--1` (mép phải **479px**) và cụm đổi ngôn ngữ `.wj-auth__lang-text`. Ảnh **trước và sau
giống hệt** ⇒ lỗi **có sẵn**, không do E6b2, và nằm ở nhịp/bố cục của cụm auth — cụm đang **KHÓA THIẾT KẾ
S39** (LIMIT #5 của D4f). Đề xuất cho E6c: `overflow-x: hidden` trên vỏ `.wj-auth`, cần chủ dự án/BA
duyệt vì sẽ cắt bớt khối trang trí.

## Bump

| Module | Version |
|---|---|
| `wujia_portal_layout` | `19.0.56.2.0` |
| `wujia_portal_sale` | `19.0.4.21.0` |

`?v=` trong `views/assets.xml`: `_components.css` 1316→**1317** · `_auth.css` 1170→**1171** ·
`_pc_account.css` 1200→**1201**.

## Nợ để lại

- **E6c**: màn Thi (30 nút XML + nút dựng bằng JS), gạch **12** của BA, **một lần deploy UAT**, rồi
  đóng `UI-BUTTON-001`. Kèm quyết định về tràn ngang màn đăng nhập.
- Ba template auth chết vẫn chưa ai render (LIMIT ở trên).
- Cụm **EmptyState** (~124 chỗ viết class tay) — đề xuất BA sau cổng F.

## Lệnh đã chạy

```bash
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python

$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --json scratchpad/e6b2/button-after.json
$PY scripts/qa/wj_button.py    --base http://127.0.0.1:8090 --portal-login em.hcm --breakpoints 720 512
$PY scratchpad/e6b2/empty_cart_probe.py                    # trạng thái giỏ rỗng (anh.owner)
$PY scripts/qa/wj_filterbar.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_measure.py   --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_listcard.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_nesting.py   --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/check_layers.py
$PY scratchpad/e6a/b4_emhcm.py --base http://127.0.0.1:8090
$PY scratchpad/e6b2/mutations.py
$PY scratchpad/e6b2/shots.py   scratchpad/e6b2/after
$PY scratchpad/e6b1/diff_shots.py scratchpad/e6b2/before scratchpad/e6b2/after
$PY scratchpad/e6b2/diff_box.py                            # hộp bao chênh lệch của /portal/order

$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_delivery,wujia_portal_knowledge,\
wujia_portal_info_request,wujia_portal_purchase_history,wujia_portal_debt,wujia_portal_sale,wujia_portal_notification \
  --test-enable --log-handler "odoo.tests.result:INFO" --stop-after-init
```

**Lệnh deploy khi tới lượt (E6c gộp):** `-u wujia_portal_layout,wujia_portal_sale` cộng danh sách của E6b1.
