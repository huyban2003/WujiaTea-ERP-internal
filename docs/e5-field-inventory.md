# E5 — Field inventory `CMP-LC-001` (`UI-LISTCARD-001`, STT 136)

Mốc đo bằng `scripts/qa/wj_listcard_inventory.py`, DB `wujia_e4b1`, login `em.hcm`,
server đo `--http-port 8090`. JSON mốc: `docs/e5-inventory-before.json` (trước E5a) ·
`docs/e5a-inventory-after.json` (sau 2 route mẫu). Bảng này là **hợp đồng trường** cho E5b:
mỗi route migrate xong phải cho **0 trường mất, 0 trường thêm** so với cột "Trường hiển thị".

## 1. Mốc TRƯỚC — 13 route

| Route | LC | Mẫu @390 | Mẫu @1440 | Họ class item | Trường hiển thị (nhãn) |
|---|---|---|---|---|---|
| `/portal` | LC-23 (giữ nguyên) | 9 | 6 | `wujia-mdash-row`×9 | _(không nhãn, chỉ giá trị)_ |
| `/portal/purchase-history` | LC-13 | 10 | 0 | `wujia-mhist-row`×10 | _(không nhãn, chỉ giá trị)_ |
| `/portal/delivery` | LC-14 | 20 | 0 | `wujia-mdelivery-row`×20 | Chuyến xe · Xuất phát (dự kiến) · Đơn liên quan |
| `/portal/notification` | LC-16 | 10 | 0 | `wujia-mnoti-row`×10 | _(không nhãn, chỉ giá trị)_ |
| `/portal/support` | LC-18 | 20 | 0 | `wujia-mdash-row`×20 | _(không nhãn, chỉ giá trị)_ |
| `/portal/return` | LC-15 | 20 | 0 | `wujia-mreturn-row`×20 | Đơn gốc · Ngày YC |
| `/portal/knowledge` | LC-17 | 12 | 12 | `wujia-mknow-row`×12 | _(không nhãn, chỉ giá trị)_ |
| `/portal/exam` | LC-19 | 10 | 0 | `wj-surface-card`×10 | _(không nhãn, chỉ giá trị)_ |
| `/portal/exam/register` | LC-19 | 1 | 0 | `wujia-mexam-course`×1 | _(không nhãn, chỉ giá trị)_ |
| `/portal/debt` | LC-21 | 1 | 0 | `wj-debt-inv`×1 | _(không nhãn, chỉ giá trị)_ |
| `/portal/debt/payment-history` | LC-21 | 46 | 0 | `wj-debt-pay`×46 | _(không nhãn, chỉ giá trị)_ |
| `/portal/franchise-information` | LC-18 | 10 | 0 | `wujia-mdash-row`×10 | _(không nhãn, chỉ giá trị)_ |
| `/portal/order` | LC-22 (ProductCard) | 0 | 0 | — | _(không nhãn, chỉ giá trị)_ |

> `/portal/order` = 0 `.wj-data-item` **theo thiết kế** — ProductCard là họ riêng
> (`wujia-morder-row`), LC-22 chỉ đồng bộ token ở E5c.
> `/portal/debt` 1 mẫu và `/portal/exam/register` 1 mẫu là **mẫu mỏng**: E5b phải gieo thêm
> trước khi kết luận (LC-18/LC-19/LC-21 — "không kết luận từ empty").
> Cột @1440 = 0 ở phần lớn route vì PC dùng **bảng**, không dùng card (LC-23).

## 2. Hai route mẫu E5a — trước / sau

### `/portal/purchase-history` — LC-13

| | Trước | Sau |
|---|---|---|
| Số record @390 | 10 | 10 |
| Họ class | `wujia-mhist-row`×10 | `wj-lc`×10 |
| Nhãn | — | Ngày đặt · Tổng tiền |
| Cao card | 80 | 104 |
| Padding | 12px 14px | 12px 14px |
| Giá trị **mất** | — | 0 |
| Giá trị **thêm** | — | 0 |

### `/portal/delivery` — LC-14

| | Trước | Sau |
|---|---|---|
| Số record @390 | 20 | 20 |
| Họ class | `wujia-mdelivery-row`×20 | `wj-lc`×20 |
| Nhãn | Chuyến xe · Xuất phát (dự kiến) · Đơn liên quan | Xuất phát (dự kiến) · Đơn liên quan |
| Cao card | 129 | 104 |
| Padding | 12px 14px | 12px 14px |
| Giá trị **mất** | — | 0 |
| Giá trị **thêm** | — | 0 |

**Đọc hai bảng trên:** nhãn đổi là **do BA yêu cầu**, không phải trường đổi — delivery bỏ nhãn
"Chuyến xe" (LC-14: mã chuyến là *tên* record, không phải metadata), purchase-history **thêm** nhãn
"Ngày đặt"/"Tổng tiền" (LC-13: hàng phụ phải có nhãn). Cột quyết định là **giá trị mất/thêm = 0**.

**Ghi nhận cho E5c:** padding item đang là `12px 14px` (dáng ngoài của `.wj-data-item`, chủ sở hữu là
D5), trong khi LC-07 ghi padding 12. Chênh 2px chiều ngang này đi chung với món gutter LC-08 — xử một
lần ở E5c, **không** sửa lẻ ở đây để khỏi đụng dáng ngoài của 22 danh sách.

## 3. Cách chạy lại

```
python3 scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 \
  --portal-login em.hcm --out <file>.json
python3 scripts/qa/wj_listcard_inventory.py --diff <trước>.json <sau>.json
```
