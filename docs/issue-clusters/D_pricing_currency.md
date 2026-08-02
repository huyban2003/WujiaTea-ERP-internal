# Cụm D — Giá & tiền tệ (giỏ hàng ↔ đơn hàng ↔ lịch sử)

**Issue:** WJ-ORD-024 (High) · WJ-ORD-025 (Medium) · WJ-PH-005 (Medium)
**Rủi ro:** **Cao** — chạm số tiền người dùng nhìn thấy. Test kỹ nhất trong 9 cụm.

---

## 1. Triệu chứng BA ghi

- **WJ-ORD-024**: giỏ hiện *Tạm tính 48.000 đ*, gửi xong SO/History ra **55.200** (+15% thuế).
  Người dùng chỉ biết mình phải trả thêm **sau khi** đã bấm gửi.
- **WJ-ORD-025**: cùng đơn S00028 — Cart `48.000 đ`, Submitted `55.200 đ`, History `55.200 $`.
- **WJ-PH-005**: Master Sheet CT-025 vẫn ghi `Unit Price = price_unit`, nhưng rule controller cuối
  yêu cầu đơn giá **sau chiết khấu, đã gồm thuế**. Hai nguồn lệch nhau.

Ba issue = **một gốc**: portal tính tiền bằng tay thay vì hỏi tax engine của Odoo,
và ký hiệu tiền bị viết cứng.

## 2. Root cause (file:dòng)

### (a) Giỏ không có thuế
`custom/wujia_portal_sale/controllers/portal.py:227-271` — `_cart_state()`:
```python
unit = unit_prices.get(line.id, 0.0)     # giá pricelist thô
'subtotal': unit * line.qty,             # ← không qua tax engine
total_amount += unit * line.qty
```
Khi submit, Odoo tự tính thuế trên `sale.order.line` → tổng nhảy lên. Chênh lệch = đúng thuế suất sản phẩm.

### (b) Ký hiệu tiền viết cứng — 8 chỗ
| File | Dòng |
|---|---|
| `controllers/portal.py` | `267` `currency.symbol or 'đ'` · `922` `... + ' đ'` |
| `views/portal_order_catalog.xml` | `99`, `233` |
| `views/portal_order_cart.xml` | `87`, `119` |
| `views/pc_cart_panel.xml` | `63`, `74`, `104` |

Tất cả nối chuỗi `' đ'` bất kể `currency_id` của đơn. Trong khi
`wujia_portal_purchase_history/controllers/portal.py:88` đọc đúng `order.currency_id.symbol`
→ đó là lý do History ra `$` còn Cart ra `đ`.

### (c) Lịch sử tính đơn giá bằng phép chia
`wujia_portal_purchase_history/controllers/portal.py:106-107`:
```python
'unit_price_tax_included': (total / qty) if qty else total,
```
Xấp xỉ được trong trường hợp đơn giản, nhưng **sai** khi có thuế cố định (fixed amount),
nhiều thuế, hoặc rounding theo currency — đúng như BA lo ở phần "bao phủ mọi trường hợp".

## 3. Cách sửa đề xuất — một helper dùng chung

BA đã chốt (30/07) công thức tổng quát:

```
discounted_unit = price_unit × (1 − discount/100)
compute_all(discounted_unit, currency, quantity=1, product=..., partner=...)
    → total_included  = đơn giá hiển thị (unit_price_tax_included)
line_total  = sale.order.line.price_total
order_total = sale.order.amount_total
ký hiệu + rounding theo sale.order.currency_id
```

**Không tạo field lưu mới.** Đây là dữ liệu controller tính tại chỗ.

### Việc cụ thể
1. Đặt helper ở nơi cả 2 module dùng được — đề xuất
   `wujia_portal_sale/controllers/utils.py` (đã tồn tại, chứa `rate_limit`, `attach_files_to_record`)
   hoặc một `models/sale_order.py` method. **Hỏi ở fork này nếu thấy nên đặt chỗ khác.**
2. `_cart_state()`: với mỗi dòng giỏ, lấy `taxes = product.taxes_id` đã lọc theo company + áp
   `fiscal_position` của partner cửa hàng (đúng bộ thuế sẽ dùng khi tạo SO) → `compute_all`.
   Trả thêm `unit_price_tax_included`, `line_total_tax_included`, `tax_amount`, `total_tax_included`.
3. Hiển thị: giỏ + màn "gửi đơn thành công" show **Tạm tính · Thuế · Tổng thanh toán**
   (BA cho phép "hoặc breakdown tương đương").
4. Thay 8 chỗ hardcode `' đ'` bằng ký hiệu từ `cart_state['currency_symbol']` /
   `order.currency_id.symbol`, giữ đúng format nghìn hiện tại.
5. `wujia_portal_purchase_history`: đổi `_history_line_vals()` sang cùng helper thay vì `total/qty`.

### Điểm dễ sai
- Currency của giỏ lấy từ `pricelist.currency_id` (`portal.py:233`) — phải **cùng** currency sẽ tạo SO.
  Nếu SO lấy currency từ chỗ khác (partner pricelist tại thời điểm tạo) thì hai bên vẫn lệch. **Kiểm lại đường tạo SO trước khi code.**
- `compute_all` cho **1 đơn vị** rồi mới nhân, KHÔNG gọi cho cả qty rồi chia — sai rounding.

## 4. Blast radius

```bash
grep -rn "' đ'" custom/ --include=*.xml --include=*.py
grep -rn "_cart_state\|currency_symbol\|total_amount" custom/wujia_portal_sale --include=*.py --include=*.xml --include=*.js
grep -rn "price_total\|price_unit\|amount_total" custom/wujia_portal_purchase_history custom/wujia_portal_sale --include=*.py
```
`_cart_state()` là **nguồn dữ liệu duy nhất** của: giỏ mobile, panel giỏ PC, badge header, JSON route
`/portal/order/cart/step`. Thêm key thì an toàn (client bỏ qua key thừa — pattern đã dùng ở S46);
**đổi kiểu/ý nghĩa key cũ thì vỡ JS.** → chỉ thêm, không sửa nghĩa `subtotal`/`total_amount`.

## 5. Verify

Bảng ma trận bắt buộc (dựng dữ liệu test trên DB copy, **không** tạo đơn thật trên UAT):

| Case | Kỳ vọng |
|---|---|
| Thuế included 15% | giỏ = SO, không nhảy số sau submit |
| Thuế excluded 10% | giỏ hiện Tạm tính + Thuế + Tổng = `amount_total` |
| Discount 10% + thuế | đơn giá = `compute_all(price_unit×0.9)` |
| 2 thuế trên 1 dòng | tổng khớp `price_total` |
| Currency ≠ VND | ký hiệu đúng ở **cả 4 màn**: Cart, PC panel, Submitted, History |
| Sản phẩm không thuế | không đổi so với hiện tại (regression) |

Bằng chứng cần chụp cho BA: cùng 1 đơn, ảnh Cart + Submitted + History List + History Detail, **cùng con số cùng ký hiệu**.

## 6. Ghi sheet

- K (WJ-ORD-024): `FIX: giỏ tính giá qua tax engine Odoo (compute_all trên đơn giá sau chiết khấu), hiển thị Tạm tính + Thuế + Tổng thanh toán trước khi gửi | IMPACT: giỏ mobile + panel giỏ PC + màn gửi đơn thành công + lịch sử | RETEST: giỏ trước submit và SO sau submit khớp từng đồng ở các case thuế included/excluded/discount | LIMIT: <ghi nếu có case chưa phủ>`
- K (WJ-ORD-025): `FIX: bỏ 8 chỗ hardcode ký hiệu 'đ', đọc currency của đơn/pricelist | IMPACT: Cart, PC cart panel, Submitted, History | RETEST: đơn currency ≠ VND hiển thị đúng ký hiệu ở cả 4 màn | LIMIT: Không có`
- K (WJ-PH-005): `FIX: đơn giá lịch sử tính bằng tax engine thay vì price_total/qty; line_total=price_total; order_total=amount_total | IMPACT: /portal/purchase-history list + detail | RETEST: đối chiếu 1 SO có discount + thuế với backend | LIMIT: không tạo field lưu mới (theo BA)`
- R: `Custom` cho cả 3.
