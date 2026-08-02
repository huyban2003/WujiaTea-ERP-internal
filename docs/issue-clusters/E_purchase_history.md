# Cụm E — Lịch sử đặt hàng (controller)

**Issue:** WJ-PH-002 (Medium) · WJ-PH-007 (Medium) · WJ-PH-004 (Low) · WJ-PH-006 (Medium — chỉ verify)
**Rủi ro:** Thấp — gói gọn trong 1 controller + 1 template
**File chính:** `custom/wujia_portal_purchase_history/controllers/portal.py` (291 dòng) · `views/portal_history.xml`

> WJ-PH-003 (phạm vi trạng thái) **không** ở cụm này — là fork thiết kế, xem cụm I.
> WJ-PH-005 (giá) ở cụm D.

---

## WJ-PH-002 — Lệch −7 giờ

**BA đo:** SO S00027 backend/chatter 20:22, Portal hiện 13:22. Tái hiện với cả Manager và Staff.

**Root cause:** controller trả thẳng datetime naive UTC ra template, không đổi sang giờ người dùng:
- `portal.py:83-84` (`_history_row_vals`): `'create_date': order.create_date, 'date_order': order.date_order`
- `portal.py:119-120` (`_history_detail_vals`): y hệt
- `portal.py:135` (`batch['departure']`) — **cùng lỗi, BA chưa bắt** → sửa luôn kẻo đẻ issue mới.

**Bộ lọc ngày cũng sai cùng lý do** — `portal.py:190-194`:
```python
domain.append(('create_date', '>=', datetime.combine(df, dt_time.min)))
```
`df` là ngày **giờ địa phương** người dùng chọn, nhưng `create_date` lưu UTC → lọc "hôm nay" bỏ sót
các đơn tạo từ 00:00–07:00 giờ VN và lấy nhầm đơn của ngày hôm trước.

**Sửa:**
- Hiển thị: `fields.Datetime.context_timestamp(order, order.create_date)` (dùng tz của `env.user`).
- Lọc: quy đổi mốc local → UTC trước khi đưa vào domain (đảo chiều `context_timestamp`).
- Mapping đã đúng theo BA, **không đổi**: Ngày đặt hàng = `create_date`, Ngày xác nhận = `date_order`.

⚠️ **Bẫy đã biết:** có user để `tz = 'Asia/Saigon'` (tên tz cũ) làm `/portal/reports/orders` **500**
(xem §5 "Pre-existing"). Cụm này phải **phòng thủ**: tz không hợp lệ → fallback `Asia/Ho_Chi_Minh`,
không để nổ trang. Ghi rõ vào LIMIT nếu chưa dọn dữ liệu user.

---

## WJ-PH-007 — Khoảng ngày đảo ngược không bị chặn

**BA đo:** `?date_from=2026-07-30&date_to=2026-07-29` → trả 0 bản ghi + empty state "Chưa có đơn hàng",
người dùng tưởng không có dữ liệu.

**Root cause:** `_parse_date()` (`portal.py:57-63`) chỉ parse, không so sánh. Không có nhánh nào kiểm `df <= dt`.

**Sửa:** trong `portal_history_list()`, sau khi parse:
- nếu `df` và `dt` và `df > dt` → **không chạy query**, render lại với `date_from`/`date_to` giữ nguyên
  + thông báo `Từ ngày không được lớn hơn Đến ngày` hiển thị **tại FilterBar** (không dùng empty state).
- Thêm `min`/`max` attribute ở input date (UI) để chặn sớm — nhưng **server vẫn phải kiểm**, không tin frontend.

---

## WJ-PH-004 — Cột "Thao tác" thừa ở bảng PC

**BA đo:** mã đơn đã là link `/portal/purchase-history/<id>`, cột "Thao tác" lại có link "Xem" **cùng URL**.
Mockup PC chỉ có 7 cột, không có cột này.

**Sửa:** bỏ `<th>Thao tác</th>` + `<td>` tương ứng trong `views/portal_history.xml` (nhánh PC).
Giữ mã đơn là link duy nhất. **Không đụng bản mobile.**

---

## WJ-PH-006 — Đã đúng, chỉ cần bằng chứng

`portal.py:70-73`:
```python
def _requester_display(order):
    return order.portal_requester_user_id.name or BACKEND_REQUESTER_LABEL   # 'Ngô Gia tạo đơn'
```
Đúng **nguyên văn** rule BA chốt 30/07: đơn portal → tên requester; đơn backend → chuỗi cố định;
không lộ `create_uid.name`.

**Việc cần làm:** không sửa code. Chụp bằng chứng 2 nhánh (1 đơn portal + 1 đơn tạo ở backend),
ghi vào cột K, đẩy `Ready for Retest`. Đồng thời **BA cần cập nhật CT-025 trên Master Sheet**
(hiện chỉ ghi nhánh portal) — nêu trong danh sách câu hỏi ở cụm I.

---

## Blast radius

```bash
grep -rn "create_date\|date_order" custom/wujia_portal_purchase_history --include=*.py --include=*.xml
grep -rn "context_timestamp" custom/ --include=*.py            # xem module khác đã có pattern chưa
grep -rn "portal_requester_user_id" custom/ --include=*.py
```
Controller này chỉ phục vụ `/portal/purchase-history*`. Nhưng **format ngày** có thể đang được
các trang khác (Giao hàng, Đổi trả) làm theo cách khác → nếu định làm helper chung thì kiểm cả các module đó.

## Verify

| Kiểm tra | Expected |
|---|---|
| Đơn tạo 20:22 giờ VN | List + Detail hiện **20:22**, khớp backend/chatter |
| Lọc "hôm nay" với đơn tạo 06:00 sáng | có trong kết quả |
| `?date_from=2026-07-30&date_to=2026-07-29` | báo lỗi tiếng Việt tại FilterBar, **không** empty state, 2 ô giữ nguyên giá trị |
| Bảng PC | 7 cột, không có "Thao tác"; mã đơn mở detail |
| Người đặt | đơn portal → tên user; đơn backend → "Ngô Gia tạo đơn" |
| User `tz` lạ/rỗng | trang vẫn 200, không 500 |

Regression: phân trang, sắp xếp, preset "tháng này/tháng trước", lọc trạng thái, tìm theo mã đơn;
mobile `/portal/purchase-history` vẫn render đúng.

## Ghi sheet

- K (WJ-PH-002): `FIX: quy đổi create_date/date_order/departure sang timezone người dùng khi hiển thị VÀ khi lọc theo khoảng ngày | IMPACT: /portal/purchase-history list + detail, bộ lọc ngày | RETEST: đơn tạo 20:22 giờ VN phải hiện 20:22; lọc hôm nay bắt được đơn tạo lúc 06:00 | LIMIT: user có tz không hợp lệ được fallback Asia/Ho_Chi_Minh — dữ liệu user cần dọn riêng`
- K (WJ-PH-007): `FIX: chặn date_from > date_to ở controller + UI, giữ giá trị đã nhập, báo lỗi tại FilterBar | IMPACT: bộ lọc lịch sử đặt hàng | RETEST: mở URL khoảng ngày đảo ngược → thấy thông báo, không thấy empty state | LIMIT: Không có`
- K (WJ-PH-004): `FIX: bỏ cột Thao tác ở bảng PC, mã đơn là link duy nhất | IMPACT: /portal/purchase-history PC | RETEST: bảng còn 7 cột, bấm mã đơn mở detail | LIMIT: Không có`
- K (WJ-PH-006): `FIX: không cần sửa — rule 2 nhánh đã có sẵn ở _requester_display() | IMPACT: không | RETEST: đối chiếu 1 đơn portal và 1 đơn backend | LIMIT: BA cập nhật CT-025 trên Master Sheet cho khớp nhánh backend`
- R: `Custom` (WJ-PH-002/004/007) · `Custom` (WJ-PH-006, đã có sẵn).
