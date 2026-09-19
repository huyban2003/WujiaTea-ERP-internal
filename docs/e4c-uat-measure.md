# E4c — Đo lại trên chính UAT sau khi chủ dự án deploy (19/09/2026)

Máy chủ `http://113.161.187.126:8019`, DB `wujia_tea_19`. **Chỉ đọc**: không tạo, không sửa, không xoá
bản ghi nào; không seed; không chạy `-u`. Tài khoản đo `em.hcm` (HCM-01, kho dữ liệu lớn nhất — bài
học D6d để tránh mẫu rỗng). Sổ ghi: `scratchpad/uat_e4c.json` · `uat_extra.json` · `uat_measure.json`.

## 0. Cổng deploy — ba bằng chứng độc lập

| Bằng chứng | Kết quả |
|---|---|
| Phiên bản 8 module bị đụng (XML-RPC `ir.module.module`) | **8/8 đúng bản đích**: layout `19.0.54.0.0` · base `19.0.7.18.0` · purchase_history `19.0.3.14.0` · delivery `19.0.3.16.0` · exam `19.0.5.17.0` · report `19.0.2.4.0` · notification `19.0.2.17.0` · return `19.0.3.6.0`; `write_date` 19/09 11:52–11:53 |
| Tệp giao diện trang **đang gọi** | `_components.css?v=1303` (không phải 1302) |
| Nội dung tệp trên máy chủ | có rule `.wj-filter-error {` |

## 1. Ngày ngược — 6/6 màn, CẢ HAI khổ

`scripts/qa/wj_filterbar.py --base http://113.161.187.126:8019 --portal-login em.hcm`

| Màn | @1440 | @390 |
|---|---|---|
| Lịch sử mua hàng | 200 · 0 bản ghi · **1 thông điệp** | **1 thông điệp** |
| Giao hàng | 200 · 0 · **1** | **1** |
| Thông báo | 200 · 0 · **1** | **1** |
| Đổi trả | 200 · 0 · **1** | **1** |
| Đăng ký thi | 200 · 0 · **1** | **1** |
| Báo cáo | 200 · 0 · **1** | **1** |

Cùng một câu chữ *Từ ngày không được lớn hơn Đến ngày* ở cả 12 ô. **Im lặng: 0 màn** (trước lượt: 5) ·
**thông điệp trùng: 0 màn**. Đây là ca lỗi nặng nhất của phiếu — màn Thông báo trước đây bỏ luôn điều
kiện ngày rồi trả **toàn bộ** danh sách.

## 2. Lỗi gốc BA nêu — mobile Đăng ký thi lọc ngày

| Phép đo @390 | Kết quả |
|---|---|
| 2 ô ngày có `name` và nằm trong `<form>` | `date_from` / `date_to`, `action="/portal/exam"` ✅ (trước: **không có `name`**, ngoài form) |
| Lọc thật theo khoảng ngày | gửi ngày = **có** · bản ghi **1 → 0** khi chọn khoảng quá khứ xa |

Bốn màn khác đo cùng cách: Lịch sử **10 → 0** · Giao hàng **2 → 0** · Đổi trả **7 → 0** ·
Báo cáo KPI **18 đơn / 8.022.405 ₫ → 0 / 0 ₫**. Thông báo khổ này không có ô ngày (ghi rõ, không
tính Pass).

## 3. Khuôn hiển thị lỗi — khi KHÔNG có lỗi

6/6 màn: đúng **2** phần tử `.wj-filter-error` (một PC, một mobile), **có mặt sẵn** trong trang,
`hidden`, `role="alert"`, nằm **trong `<form>` của chính thanh lọc**. Đây là điều kiện để AJAX thay
khối đúng chỗ — thiếu id là cả màn rơi về tải lại trang.

## 4. Bẫy `clamp` đã gỡ — dời khoảng ngày về quá khứ

Mở màn đang lọc `?date_from=2026-09-01&date_to=2026-09-30` rồi đổi sang 05/01–20/01:

| Màn | `min`/`max` trên ô ngày | `checkValidity()` | Kết quả |
|---|---|---|---|
| Lịch sử mua hàng | **không có** | `true` | **đi được** |
| Báo cáo | **không có** | `true` | **đi được** |
| Đăng ký thi | **không có** | `true` | **đi được** |

Trước lượt này biểu mẫu bị trình duyệt **từ chối câm**: bấm tìm không có request, không thông điệp.

## 5. Gõ Enter ≡ bấm nút tìm (gạch 6 của BA — trước ghi LIMIT, nay đã đo)

| Màn | Enter vs click |
|---|---|
| Lịch sử mua hàng | **cùng một đường dẫn** |
| Đổi trả | **cùng một đường dẫn** |
| Giao hàng | **cùng một đường dẫn** |

## 6. Đổi lọc → trang 1 · sang trang giữ lọc

- **Đổi lọc → trang 1**: 5/5 màn, URL sau khi lọc **không còn `page=`** (ép `page=3` trước khi submit).
- **Sang trang giữ lọc**: `/portal/purchase-history` **4/4 link** giữ đủ `date_from`+`date_to`.
  Bốn màn còn lại trên UAT chỉ có **một trang** (Đổi trả 7 · Giao hàng 1 · Thông báo 2 · Thi 1 bản ghi)
  ⇒ **không kết luận được**, xem §8.

## 7. Hồi quy trên chính UAT

`scripts/qa/wj_measure.py` — 13 route × 5 khổ (**65 ô**):

| Phép đo | Kết quả |
|---|---|
| RULE 1 HIERARCHY vi phạm | **0** |
| Tràn ngang | **0** |
| Lỗi JS | **0** |
| Màn mất bản ghi | **0** |
| "Redirect ngầm" | 5 ô, **không phải lỗi**: `/portal/inspection` → `/vi/portal/inspection` (tiền tố ngôn ngữ website). E4c không sửa file nào của `wujia_portal_inspection` |

## 8. LIMIT còn lại (hẹp, có bằng chứng thay thế)

Chưa nhìn tận mắt nút sang trang **của bốn màn ít dữ liệu** trên UAT. Ép cỡ trang nhỏ cũng không ra
trang 2: controller chỉ nhận các bậc có trong danh sách (`page_size=1` vẫn trả đủ 7 phiếu đổi trả) —
đúng thiết kế E3, và seed thì làm bẩn dữ liệu BA đang retest. Ba lớp bằng chứng thay thế:

1. **Cùng một nguồn dựng đường dẫn**: cả năm màn đi qua `build_pager()` của `wujia_portal_base` —
   nguồn duy nhất, đã chứng minh sống trên UAT ở `/portal/purchase-history` (4/4 link giữ cả hai ngày).
2. **Đường không-JS cũng vậy**: không form lọc nào để `page` trong `fb_hidden` ⇒ submit là rơi `page`.
3. **Runtime đầy đủ đã đo ở DB cô lập** (45 đơn trải 45 ngày): `docs/e4c-acceptance-matrix.md` §3 mục
   3–4, 5/5 màn về trang 1 và 6/6 link giữ lọc.

Ngoài ra: nợ nhịp G2 (*lọc → danh sách* 24px thay vì 16px ở 7 màn) vẫn còn, cố ý để cho **cụm E5**.
