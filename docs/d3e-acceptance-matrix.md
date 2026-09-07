# D3e — bảng đối chiếu acceptance (UI-CARDHEADER-001, STT 125 · `CMP-CH-001`)

**Ngày đo:** 2026-09-04 (local, chưa deploy) · **Kết quả: 22/23 Pass, 1 phần (95,7%)** — ô "phần"
duy nhất là **phạm vi cố ý**: sau D3e mới phủ **85/103** call site nên issue **giữ `Ready for Dev`**
(tiền lệ C8a→C8b, D3b–D3d) ⇒ phiên này **KHÔNG** chạy `qa_sync.py`. Kiểm kê gốc rễ →
`d3-cardheader-inventory.md`. Bốn phiên trước → `d3-acceptance-matrix.md`, `d3b-`, `d3c-`, `d3d-`.

**Phạm vi phiên:** **24 call site / 2 file / 2 module**
- `wujia_portal_return/views/portal_return_detail.xml` — **15**
- `wujia_portal_purchase_history/views/portal_history.xml` — **9**

> ⚠️ **Đính chính con số bàn giao — lần thứ BA liên tiếp.** Bảng §5 của
> `d3-cardheader-inventory.md` ghi `15 / 10`; đó là **tổng theo file**, gồm cả dòng đã bị §3 loại.
> Chạy lại `scratchpad/d3_inventory.py` trước khi lập kế hoạch: `portal_history.xml:395` là
> `.wj-pc-order-head__right` — **slot phải, không phải title** ⇒ còn **9**. Tổng làm thật **24**,
> phủ **61 → 85/103**.

**Môi trường:**
- **A/B bằng 2 DB, không phải 2 commit** (thay đổi nằm ở `arch_db`). `wujia_tea_d3e_b` = "trước"
  **:8070** · `wujia_tea_d3e_a` = "sau" **:8071**, `--db-filter` riêng từng cái — **KHÔNG đụng
  `wujia_tea_19`/8019**. Hai DB clone cùng nguồn **kèm filestore**.
- Đăng nhập form portal `anh.owner` + cookie `wujia_active_franchise_id=1`, viewport **1920 · 1440**
  (PC) và **390 · 360** (mobile).
- Harness: `scratchpad/d3e_measure.py` · `d3e_shot.py` · `d3e_probe_head.py` · `d3e_seed.py` ·
  `d3e_pwd.py` · `d3e_serve.sh` (dev-only, **không commit** — §13).
- ⚠️ **Id đơn/yêu cầu scrape từ `href` trang danh sách**, không gõ tay (bẫy D3b/D3c: id thuộc cửa
  hàng khác cookie đang ghim thì bị redirect im lặng về list, trang vẫn 200). Kết quả: hist `22`
  (mã `S00022`), return `12`.
- ⚠️ **Hai DB copy phải `-u` toàn bộ 20 module `wujia_*`** trước khi đo: bản DB local đi sau code
  trên đĩa ⇒ `column wujia_franchise_member.is_pass does not exist` (500) và 404
  `wj_section_header`. Sau `-u`: RC=0, 0 CRITICAL.

---

## 1. Giả-heading — yêu cầu cốt lõi của `CMP-CH-001`

| Route | Nền tảng | Giả-heading trước | sau | `.wj-card-header` sau |
|---|---|---|---|---|
| `/portal/purchase-history` | PC | 1 | **0** | 1 |
| `/portal/purchase-history/22` | PC | 4 | **0** | 4 |
| `/portal/purchase-history/22` | mobile | 4 | **0** | 4 |
| `/portal/return/12` | PC | 9 | **0** | 9 |
| `/portal/return/12` | mobile | 6 | **0** | 6 |

**24 → 0 trên cả hai nền tảng.** Không còn chỗ nào bị defer trong phạm vi D3e. **Pass.**

## 2. Số đo BA — 46 ô đo (mỗi header × mỗi breakpoint)

Chuẩn: PC compact **18/24/700**, PC regular **20/28/700**, mobile compact **16/22/700**, màu
**`rgb(17,24,39)`**. **46/46 ô đúng cả 4 thuộc tính.**

| Header | trước | sau |
|---|---|---|
| "Danh sách đơn hàng" (PC) | 22 / 26,4 | **18 / 24** |
| "Sản phẩm đã đặt" (PC) | 22 / 26,4 | **18 / 24** |
| "Thông tin đơn hàng", "Batch / giao hàng" (PC) | 18 / 21,6 | 18 / **24** |
| "S00022" — đầu thẻ tóm tắt (PC) | `h2` 24 / 26,4 | **20 / 28** (biến thể `regular`) |
| 5 tiêu đề card `portal_return_detail` (PC) | `h5` 20 / 24 | **`h3` 18 / 24** |
| Tiêu đề card mobile (cả 2 file) | `div` 16 / 24 | **`h3` 16 / 22** |

**4 nhãn phụ giữa thân card của `portal_return_detail`** (`Ghi chú từ cửa hàng`, `Lý do từ chối`,
`Phản hồi từ Ngô Gia`, `Đơn bù hàng`) — theo quyết định chủ dự án 2026-09-04: **chuẩn hoá cấu trúc,
giữ nguyên dáng**. Đo được **trước = sau, từng pixel**: `12,3 / 14,7 / 700`, màu
`rgba(0,0,0,.7)` (riêng "Lý do từ chối" `rgb(220,53,69)`), `gapToBody 7`. Chỉ đổi thẻ `h6 → h4`.
Đây **không phải lệch chuẩn** mà là ngoại lệ có chủ đích: chúng không mở đầu card (card đã có
tiêu đề `h3` riêng), để cỡ component thì ba dòng chữ trong một card bằng nhau, **mất phân cấp**.

Rule trả dáng ghi trong `wujia_portal_return/static/src/css/portal_return.css`, viết bằng **đơn vị
của theme** (root 14px ⇒ `h6` = `.875rem` = 12,25px, `line-height 1.2`, `margin-bottom .5rem`),
không gõ số pixel ma thuật.

## 3. Mật độ trước–sau — BA đòi *"không làm giao diện thưa hơn"*

| Route | thẻ | trước | sau | Δ |
|---|---|---:|---:|---:|
| `/portal/purchase-history` @1920 | card danh sách | 345,4 | 332 | **−13,4** |
| `/portal/purchase-history/22` @1920 | Thông tin đơn hàng | 197,6 | 194 | **−3,6** |
| `/portal/purchase-history/22` @1920 | Sản phẩm đã đặt | 256,4 | 248 | **−8,4** |
| `/portal/purchase-history/22` @390 | 4 card mobile | — | — | **−6 mỗi thẻ** |
| `/portal/return/12` @390 | 5 card mobile | — | — | **−6 mỗi thẻ** |
| `/portal/return/12` @1920 | 5 card PC | 349,8 / 131 / 393 / 84 | y hệt | **0** |

**Không thẻ nào cao thêm.** `gapToBody` mobile 12 → **8** (đúng chuẩn component) và PC 18 → **12**;
theo tiền lệ D3b/D3c đây là **đi về phía chuẩn, KHÔNG thêm rule bù**.

`textDigest` **giống hệt ở cả 10/10 ô đo** ⇒ không chữ nào mất/thêm. `overflowX = 0`, HTTP **200**,
**0 `pageerror`** ở mọi ô. **Pass.**

## 4. Cấu trúc heading

`realHeadings` mobile **1 → 5** (`purchase-history/22`) và **1 → 7** (`return/12`): trước đây toàn
bộ tiêu đề thẻ mobile là `<div>`, giờ là `<h3>` thật. PC giữ nguyên số heading (2 / 5 / 10) vì đã
là thẻ heading, chỉ đổi cấp cho đúng outline. **Pass.**

## 5. 🔴 Phát hiện chỉ ảnh chụp bắt được — thẻ tóm tắt `/portal/purchase-history/<id>` bị vỡ

**Đây là lý do quy tắc "BẮT BUỘC chụp ảnh" của D3d tồn tại, và nó vừa trả công lần thứ ba.**

Bản migrate đầu tiên map dòng meta ("Ngày tạo … · Người đặt …") vào `ch_subtitle`. **Mọi số đo đều
Pass**: font đúng, màu đúng, `overflowX = 0`, `textDigest` khớp, `trailOverflowsCard` không báo.
Ảnh chụp thì thấy rõ: badge "Đã xác nhận" **trôi ~966px** khỏi mã đơn, và mã đơn co từ 24 → 18px.

Nguyên nhân: `.wj-card-header__lead` mặc định `flex: 1 1 auto`; dòng meta **dài hơn mã đơn** nên
`lead` nở theo bề rộng của meta và **đẩy trailing (badge) đi theo mép của nó**.

Cách chữa (2 phần):
1. **Dòng meta ở lại ngoài component, là nội dung card** — không làm `ch_subtitle`. Ghi chú lý do
   ngay tại chỗ trong template để phiên sau không "dọn dẹp" nhầm.
2. `ch_variant='regular'` (20/28) cho mã đơn để không co chữ.

Chụp lại: thẻ khớp bố cục cũ. Ảnh trước/sau lưu ở `scratchpad/d3e-shots/` (10 ảnh full-page,
5 route × trước/sau).

## 6. Gom rule vá tràn `flex` về gốc

`.wj-pc-order-head` có **đúng hai consumer** (`portal_history.xml` và màn đã migrate ở D3c) ⇒ theo
quyết định chủ dự án, rule vá chuyển về gốc `wujia_portal_layout/static/assets/css/_pc_components.css`:

```css
.wj-pc-order-head .wj-card-header__lead { flex: 0 1 auto; }
```

và **xoá** bản scope trùng `.wj-pc-dlv-head .wj-card-header__lead` trong
`wujia_portal_delivery/static/src/css/portal_delivery.css`.

Chứng minh không hồi quy — `d3e_probe_head.py` đo `/portal/delivery/3` trước/sau khi xoá:
`cardH 92`, `badge gap 12`, `badgeToCardRight 1067` — **giống hệt**. **Pass.**

## 7. Bẫy specificity — trả giá lần thứ ba nếu quên

Rule component biến thể là **(0,2,0)** và nằm ở bundle khác ⇒ rule scope module **một lớp đơn sẽ
thua**. Rule trả dáng 4 nhãn phụ viết qua `.card-body >` để đạt **(0,3,0)**, và các thuộc tính bị
component đặt `!important` (màu, cỡ chữ tiêu đề) thì override cũng phải `!important`:

```css
.card-body > .wj-card-header.wj-return-sublabel .wj-card-header__title {
    font-size: .875rem !important; line-height: 1.2; color: rgba(0,0,0,.7) !important;
}
```

## 8. JS coupling — đã kiểm, sạch

`grep -n "querySelector" custom/wujia_portal_return/static/src/js/*.js` → chỉ đụng
`input[name=images]`, `select.wj-return-order/.wj-return-line`.
`wujia_portal_purchase_history` **không có file JS**. Không JS nào đọc `wujia-mhist-card-head` /
`wj-pc-order-head__code` / `wj-pc-card__title`. **Pass.**

## 9. Hồi quy

| Bộ | Số ô | Lệch |
|---|---:|---:|
| Bảng D3c (`/portal/support/new`, `/portal/support/40`, `/portal/delivery/3`, `/portal/franchise-information`) | 56 header-ô (392 thuộc tính) | **0** |
| Bảng D3d (9 route exam) | 32 header-ô (224 thuộc tính) | **0** |

## 10. Test

| Lệnh | Kết quả |
|---|---|
| `-u wujia_portal_layout --test-tags wujia_card_header_d3` | **0 failed, 0 error / 35 tests** |
| `-u` 4 module `--test-enable` (layout, return, purchase_history, delivery) | **0 failed, 0 error / 246 tests** |
| Mutation 1 — `flex: 0 1 auto` → `1 1 auto` trong `_pc_components.css` | **1 failed** ✅ |
| Mutation 2 — `font-size: .875rem` → `18px` trong `portal_return.css` | **1 failed** ✅ |
| Khôi phục sau mutation | **0 failed / 35** |

⚠️ **Test guard phải viết bằng `assertRegex` khớp cả khai báo.** Bản đầu dùng `assertIn` chuỗi con:
đổi `.wj-card-header__lead` → `.wj-card-header__leadXX` mà test **vẫn xanh** — guard vô dụng. Đã
siết lại thành `flex:\s*0 1 auto` / `font-size:\s*\.875rem`.

Test mới trong `wujia_portal_layout/tests/test_d3_card_header.py` (không đẻ file mới), lớp
`TestCardHeaderD3eLayout`: dòng meta ở lại là nội dung card · rule `flex` tồn tại ở CSS chung ·
4 nhãn phụ giữ dáng riêng. ⚠️ Hai bug trong chính test tôi viết đã sửa: `split('wj-pc-order-head')`
cắt nhầm ở attribute (→ dùng lxml xpath), và `count('wj-return-sublabel')` ra 5 vì call site
`--danger` chứa chuỗi con hai lần (→ `count("'wj-return-sublabel")`).

## 11. Bump version

| Module | trước | sau |
|---|---|---|
| `wujia_portal_return` | 19.0.2.9.0 | **19.0.2.10.0** |
| `wujia_portal_purchase_history` | 19.0.3.6.0 | **19.0.3.7.0** |
| `wujia_portal_layout` | 19.0.32.7.0 | **19.0.32.8.0** |
| `wujia_portal_delivery` | 19.0.3.8.1 | **19.0.3.8.2** |

Không module mới, **không migration**, không cần bump `?v=` (CSS nằm trong `web.assets_frontend`).

## 12. Ô "phần" duy nhất

| Yêu cầu | Đo được | Kết luận |
|---|---|---|
| `UI-CARDHEADER-001` phủ 100% call site | **85/103** sau D3e | **Phần — cố ý.** Còn D3f (`portal_debt.xml` 5 + `wujia_portal_inspection/*` 9) và phần đuôi. Issue **giữ `Ready for Dev`**, ledger giữ dạng comment, **không `qa_sync.py`**. |

## 13. Việc còn lại

- **Deploy (chủ dự án chạy tay):**
  `-u wujia_portal_layout,wujia_portal_return,wujia_portal_purchase_history,wujia_portal_delivery`
- Sau deploy: đo lại **chỉ-đọc** trên UAT rồi `qa_deploy_mark.py` với cảnh báo
  **"⚠ MỚI PHỦ 85/103"**.
- Nhóm kế: **D3f**.
- 📌 **Chủ dự án đã chốt: hết cụm D3 sẽ có một phiên review lại toàn cụm để soát vỡ giao diện.**
  Ba phiên gần nhất (D3c badge trôi · D3d mất nhịp dọc · D3e thẻ tóm tắt vỡ) đều là lỗi **số đo
  Pass nhưng mắt thấy sai** ⇒ phiên review đó phải chạy bằng ảnh chụp, không chỉ bằng bảng số.
