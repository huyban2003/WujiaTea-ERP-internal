# Cụm G — Accessibility lẻ

**Issue:** WJ-ORD-012 (Medium) · WJ-ORD-011 (Medium) · WJ-ORD-019 *(phần còn lại)* (Medium)
**Rủi ro:** Thấp · Chi phí thấp — nên chạy sớm

---

## WJ-ORD-012 — Tương phản nút primary 2.68:1

**Sprint 39 kết luận: "DEV BLOCKED — CSS bất lực, cần rework template."**
**Kết luận đó đúng hướng nhưng phóng đại độ khó.**

Grep toàn bộ `custom/`:
```
wujia_portal_sale/views/portal_order_product_detail.xml:65   class="btn btn-primary btn-add-cart-detail"
```
→ **Chỉ còn đúng 1 template** dùng `.btn-primary`. Rule đè nó là
`_components.css:61-66`: `.btn-primary, .wujia-btn-primary { background: var(--wujia-primary) /* #28A9DF */ !important; color:#FFF !important }`
→ 2.68:1, trượt WCAG AA.

**Sửa:** đổi class ở template đó sang `.wujia-btn-primary`… **nhưng chú ý**: hiện `.btn-primary` và
`.wujia-btn-primary` **dùng chung một khối rule** nên đổi class không giải quyết gì.
Việc thật sự cần làm:
1. Tách khối, cho CTA dùng token `--wujia-cta #0F7CA8` (đã có sẵn `_variables.css:16`, ratio ≥ 4.5:1)
   — đây đúng là token S38 đã chốt cho lỗi a11y do chính BA mở.
2. Hoặc dùng class PC sẵn có `.wj-pc-btn--primary` như các trang khác.
3. Kiểm đủ 4 trạng thái: default / hover / focus / disabled.

⚠️ `.btn-primary` là class Bootstrap — đổi màu nó ảnh hưởng **mọi nút Bootstrap trong portal**.
Nên: **giữ `.btn-primary` như cũ, chỉ đổi class ở template product detail** sang class CTA riêng.

**Còn tồn (S43, chưa gửi BA):** BA vẽ Figma CTA `#28A9DF` chữ trắng — trượt AA.
Đang dùng `#0F7CA8`. **Cần BA confirm** (đã có trong danh sách câu hỏi ở cụm I).

---

## WJ-ORD-011 — Vùng chạm quá nhỏ

**BA đo lại (25/07):** mobile catalog `+/−` ≈ 26×28.5px; cart `+/−` ≈ 30×28px; delete ≈ 28×28px.
Sprint 38 khai đã nới (PC step 30 / delete 34, mobile add 44×40, cart step/delete 36×36) → **vẫn chưa đạt**.

**BA DECISION ghi trong cột K:** dùng **mockup đính kèm trong cột "Hình ảnh minh hoạ"** làm chuẩn;
vùng chạm tối thiểu **44×44** mobile, desktop 32–36px.

**Chưa đo lại được ở phiên review:** stepper chỉ render khi sản phẩm **đã có trong giỏ**;
tài khoản admin dùng để đo có giỏ rỗng (đo ra `0×0`). → **phiên fix phải dựng giỏ có hàng trên DB copy** rồi mới đo.

**Cách sửa:** nới hit-area bằng `padding` hoặc pseudo-element `::after` phủ 44×44
(**giữ nguyên kích thước thị giác** để không vỡ layout card 92px). Không phóng to icon.

---

## WJ-ORD-019 — Chỉ còn phần focus ring mobile

Đo lại trên UAT hiện tại (02/08):

| Điểm BA báo fail | Đo lại | Kết luận |
|---|---|---|
| Enter không submit trên **PC** | gõ "Tra" + Enter → `/portal/order?keyword=Tra&category_id=` | ✅ **đã chạy đúng** |
| Enter không submit trên **mobile** | 391×844 → `/portal/order?keyword=Tra` | ✅ **đã chạy đúng** |
| Focus ring PC < 2px | `outline: rgb(40,169,223) solid 2px` | ✅ **đạt** |
| Focus ring **mobile** | `outline-style: none` | ❌ **còn thật** |
| Tab chạm input keyword trùng/ẩn | chưa đo bằng tab-walk | ⚠️ cần đo |

Trong DOM luôn tồn tại **2 form search**: `.wj-pc-order-filter` (PC) và `.wujia-morder-search` (mobile),
cái không dùng bị ẩn bằng class `d-none`/`d-lg-none` ở **phần tử cha**. Phần tử trong cây `display:none`
không nhận tab — nhưng phải **chạy tab-walk thật** để chốt, đừng suy luận.

**Sửa:** thêm focus ring ≥2px cho ô search mobile (copy đúng khối đã dùng cho bản PC),
rồi chạy tab-walk in ra thứ tự focus để đối chiếu kỳ vọng
`search → filter/submit → product actions → cart`.

---

## Blast radius

```bash
grep -rn "btn-primary" custom/ --include=*.xml --include=*.css | grep -v "\.min\."
grep -rn "wujia-cta" custom/ --include=*.css
grep -rn "morder-mstep\|wj-pc-order-step\|wujia-mcart-step" custom/ --include=*.css --include=*.xml
grep -rn "focus-visible" custom/ --include=*.css
```

## Verify

- **Contrast:** đo bằng script tính ratio từ computed `background-color`/`color`, cả 4 state, cả PC + mobile → **≥ 4.5:1**.
- **Touch target:** dựng giỏ có ≥2 sản phẩm trên DB copy → đo `getBoundingClientRect` mọi nút `+ − xoá thêm`
  ở `/portal/order` và `/portal/order/cart`, 391×844 (≥44×44) và 1920 (≥32).
  Kiểm layout không vỡ: card mobile vẫn 92px, không chồng hit-area.
- **Focus:** tab-walk in danh sách `document.activeElement` theo thứ tự; mọi control có outline ≥2px nhìn thấy được.

## Ghi sheet

- K (WJ-ORD-012): `FIX: nút Thêm vào giỏ ở trang chi tiết dùng class CTA riêng với token --wujia-cta #0F7CA8 thay .btn-primary #28A9DF | IMPACT: /portal/order/product/<id> (chỉ nút CTA, không đụng .btn-primary dùng chung) | RETEST: đo contrast ≥4.5:1 ở default/hover/focus/disabled trên PC và mobile | LIMIT: Figma của BA ghi CTA #28A9DF chữ trắng (2.68:1) — đang dùng #0F7CA8 theo issue a11y BA mở ở S38, cần BA confirm`
- K (WJ-ORD-011): `FIX: nới vùng chạm bằng padding/pseudo-element — mobile ≥44×44, PC 32–36px, giữ nguyên kích thước thị giác | IMPACT: catalog + giỏ, PC và mobile | RETEST: 391×844 và 1920 đo mọi nút +/−/xoá/thêm, layout card không vỡ | LIMIT: cần giỏ có hàng mới đo được`
- K (WJ-ORD-019): `FIX: thêm focus ring ≥2px cho ô tìm kiếm mobile | IMPACT: /portal/order mobile | RETEST: tab tới ô search thấy viền rõ; Enter submit ở cả PC lẫn mobile (đã đo lại 02/08 — cả hai đang chạy đúng, evidence kèm) | LIMIT: Không có`
- R: `Custom`

---

## Kết quả (2026-08-04, commit `9e335f3`) — 0 FAIL

Đo trên **DB copy cô lập `wujia_tea_g`** (cổng 8033, không đụng `wujia_tea_19`/8019), giỏ seed 2 sản
phẩm (stepper chỉ render khi SP đã trong giỏ — đúng lý do phiên review trước đo ra `0×0`).
Harness: `scripts/ba_spec/g_a11y_verify.py` · log đầy đủ: `scripts/ba_spec/g_a11y_result.txt` (gitignored).

**WJ-ORD-012** — nguyên nhân thật KHÔNG phải "CSS bất lực": override đã có ở `portal_order.css:192`
nhưng thiếu `!important` nên thua khối `.btn-primary` của `_components.css:61`. Giải bằng class mới
`.wj-cta-btn` (`_components.css`, `?v=1163`), `.btn-primary` giữ nguyên. Grep ra **3 nút nữa cùng lỗi**
BA chưa mở phiếu (store picker + 2 nút "Vào cửa hàng") → chủ dự án chốt sửa cả 4.
Đo: 4,7:1 default · 6,42:1 hover · 4,7:1 focus · **4,83:1 disabled** (Bootstrap hạ `opacity .65` kéo
disabled về ~2,5:1 → ép `opacity:1`, phân biệt bằng màu).

**WJ-ORD-011** — hit-area 44×44 bằng `::after` trong suốt, kích thước thị giác giữ nguyên.
Bẫy đã dính: 2 stepper có `overflow:hidden` **cắt mất `::after`** → phải `overflow:visible` + bo góc
dời sang `:first-child`/`:last-child`. Đo: catalog thêm 44×40→hit 44×44 · catalog step 38×40→44×44 ·
giỏ step/xoá 36×36→44×44 · PC step 30→32. `elementFromPoint` ở dx −14/0/+14: mỗi nút nhận đúng cú chạm
của mình. Layout so **trước/sau** (tắt đúng 2 rule mới rồi đo lại): row `357.4×82` và card giỏ
`357.4×111.5` **giống hệt** ⇒ không đụng mật độ.

**WJ-ORD-019** — chỉ ô search mobile là lỗi thật (`outline-style:none`), đã thêm ring 2px + phủ mọi
control mobile của trang. Ring đổi `#28A9DF`→`--wujia-cta` ở **cả PC lẫn mobile** (brand chỉ 2,6:1 với
nền trắng, dưới ngưỡng non-text 3:1 của WCAG 2.2; nay 4,7:1). Enter submit **đúng ở cả 2 viewport**
(đo lại). **Tab-walk thật 22 bước**: 0 control ẩn nhận focus (bản không dùng nằm trong cây
`display:none`) — chốt được nghi vấn của BA bằng dữ liệu, không suy luận từ class `d-none`.

Regression: 5 route × 2 viewport đều 200, overflow ngang 0, 0 JS pageerror.

**Còn tồn:** liên kết ở header/sidenav (khung dùng chung) chưa có focus ring — ngoài phạm vi cụm G.

**Deploy:** `-u wujia_portal_layout,wujia_portal_base,wujia_portal_sale` (không module mới, không
migration). `?v=` của `_components.css` đã bump 1157→1163.
