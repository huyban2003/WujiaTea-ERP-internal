# C3 — Bảng đối chiếu acceptance (WJ-DEBT-002 / 003 / 005 / 008 / 009)

**Ngày đo:** 2026-08-15 · **Môi trường:** DB copy cô lập `wujia_tea_c3` (clone từ `wujia_tea_c2`),
Odoo port **8053** (KHÔNG đụng `wujia_tea_19`/8019) · **Viewport:** 360 / 391 / 430 / 500 / 768 / 1440 ·
**Harness:** `scratchpad/c3_measure.py` (Playwright + chromium, đo bounding-box/computed-style thật,
ảnh chụp từng ca ở `scratchpad/c3_shots/`).

**Dữ liệu đo:** cửa hàng HCM-01, currency công ty USD — tuần W33 còn nợ 55.000 $ (trang pay render),
W32 quá hạn 70.000 $, W30 dư có, W29 không phát sinh (chốt chặn C2), 3 payment 2 loại tiền
(EUR + USD) trong tháng 8. Tài khoản ngân hàng portal bật/tắt bằng XML-RPC ngay trong lượt đo
để soi cả hai nhánh của WJ-DEBT-002.

## Build & test

| Bước | Kết quả |
|---|---|
| `-u wujia_portal_debt --stop-after-init` | RC=0, 0 ERROR/Traceback |
| `--test-tags wujia_debt` | **38 test, 0 failed / 0 error** (4 test mới cho C3) |
| Hồi quy `-u wujia_portal_debt,wujia_account,wujia_portal_base --test-enable` | **116 test, 0 failed / 0 error** |

## Đo giao diện — 115/115 PASS

| Issue | Viewport | Yêu cầu | Đo được | Kết quả |
|---|---|---|---|---|
| 009 | 360px | padding ngang 16 | `16` | PASS |
| 009 | 360px | filter → banner 12 | `12` | PASS |
| 009 | 360px | banner → tiêu đề 24 | `24` | PASS |
| 009 | 360px | tiêu đề → giao dịch đầu 12 | `12` | PASS |
| 009 | 360px | giữa các giao dịch 12 | `[12, 12]` | PASS |
| 009 | 360px | danh sách → Tổng cộng 12 | `12` | PASS |
| 009 | 360px | không tràn ngang | `0` | PASS |
| 009 | 360px | 0 JS pageerror | `[]` | PASS |
| 009 | 391px | padding ngang 16 | `16` | PASS |
| 009 | 391px | filter → banner 12 | `12` | PASS |
| 009 | 391px | banner → tiêu đề 24 | `24` | PASS |
| 009 | 391px | tiêu đề → giao dịch đầu 12 | `12` | PASS |
| 009 | 391px | giữa các giao dịch 12 | `[12, 12]` | PASS |
| 009 | 391px | danh sách → Tổng cộng 12 | `12` | PASS |
| 009 | 391px | không tràn ngang | `0` | PASS |
| 009 | 391px | 0 JS pageerror | `[]` | PASS |
| 009 | 430px | padding ngang 16 | `16` | PASS |
| 009 | 430px | filter → banner 12 | `12` | PASS |
| 009 | 430px | banner → tiêu đề 24 | `24` | PASS |
| 009 | 430px | tiêu đề → giao dịch đầu 12 | `12` | PASS |
| 009 | 430px | giữa các giao dịch 12 | `[12, 12]` | PASS |
| 009 | 430px | danh sách → Tổng cộng 12 | `12` | PASS |
| 009 | 430px | không tràn ngang | `0` | PASS |
| 009 | 430px | 0 JS pageerror | `[]` | PASS |
| 009 | 500px | padding ngang 16 | `16` | PASS |
| 009 | 500px | filter → banner 12 | `12` | PASS |
| 009 | 500px | banner → tiêu đề 24 | `24` | PASS |
| 009 | 500px | tiêu đề → giao dịch đầu 12 | `12` | PASS |
| 009 | 500px | giữa các giao dịch 12 | `[12, 12]` | PASS |
| 009 | 500px | danh sách → Tổng cộng 12 | `12` | PASS |
| 009 | 500px | không tràn ngang | `0` | PASS |
| 009 | 500px | 0 JS pageerror | `[]` | PASS |
| 009 | 1440px | desktop banner margin-bottom giữ 20px | `20px` | PASS |
| 009 | 1440px | mobile block ẩn | `none` | PASS |
| 003 | 360px | sidebar desktop không lọt vào (x+w <= 0) | `0` | PASS |
| 003 | 360px | không cuộn ngang | `0` | PASS |
| 003 | 360px | khối PC ẩn | `none` | PASS |
| 003 | 360px | mọi khối nằm trong viewport | `True` | PASS |
| 003 | 360px | bottom-nav không che khối cuối | `[717, 523]` | PASS |
| 008 | 360px | không còn .wj-debt-qr | `True` | PASS |
| 008 | 360px | không còn .wj-debt-pc-qr | `True` | PASS |
| 008 | 360px | không còn chữ QR minh họa / Tải mã QR | `không tìm thấy chuỗi nào` | PASS |
| 003 | 360px | 0 JS pageerror | `[]` | PASS |
| 003 | 391px | sidebar desktop không lọt vào (x+w <= 0) | `0` | PASS |
| 003 | 391px | không cuộn ngang | `0` | PASS |
| 003 | 391px | khối PC ẩn | `none` | PASS |
| 003 | 391px | mọi khối nằm trong viewport | `True` | PASS |
| 003 | 391px | bottom-nav không che khối cuối | `[761, 523]` | PASS |
| 008 | 391px | không còn .wj-debt-qr | `True` | PASS |
| 008 | 391px | không còn .wj-debt-pc-qr | `True` | PASS |
| 008 | 391px | không còn chữ QR minh họa / Tải mã QR | `không tìm thấy chuỗi nào` | PASS |
| 003 | 391px | 0 JS pageerror | `[]` | PASS |
| 003 | 430px | sidebar desktop không lọt vào (x+w <= 0) | `0` | PASS |
| 003 | 430px | không cuộn ngang | `0` | PASS |
| 003 | 430px | khối PC ẩn | `none` | PASS |
| 003 | 430px | mọi khối nằm trong viewport | `True` | PASS |
| 003 | 430px | bottom-nav không che khối cuối | `[798, 523]` | PASS |
| 008 | 430px | không còn .wj-debt-qr | `True` | PASS |
| 008 | 430px | không còn .wj-debt-pc-qr | `True` | PASS |
| 008 | 430px | không còn chữ QR minh họa / Tải mã QR | `không tìm thấy chuỗi nào` | PASS |
| 003 | 430px | 0 JS pageerror | `[]` | PASS |
| 003 | 500px | sidebar desktop không lọt vào (x+w <= 0) | `0` | PASS |
| 003 | 500px | không cuộn ngang | `0` | PASS |
| 003 | 500px | khối PC ẩn | `none` | PASS |
| 003 | 500px | mọi khối nằm trong viewport | `True` | PASS |
| 003 | 500px | bottom-nav không che khối cuối | `[798, 523]` | PASS |
| 008 | 500px | không còn .wj-debt-qr | `True` | PASS |
| 008 | 500px | không còn .wj-debt-pc-qr | `True` | PASS |
| 008 | 500px | không còn chữ QR minh họa / Tải mã QR | `không tìm thấy chuỗi nào` | PASS |
| 003 | 500px | 0 JS pageerror | `[]` | PASS |
| 003 | 768px | sidebar desktop không lọt vào (x+w <= 0) | `0` | PASS |
| 003 | 768px | không cuộn ngang | `0` | PASS |
| 003 | 768px | khối PC ẩn | `none` | PASS |
| 003 | 768px | mọi khối nằm trong viewport | `True` | PASS |
| 003 | 768px | bottom-nav không che khối cuối | `[941, 523]` | PASS |
| 008 | 768px | không còn .wj-debt-qr | `True` | PASS |
| 008 | 768px | không còn .wj-debt-pc-qr | `True` | PASS |
| 008 | 768px | không còn chữ QR minh họa / Tải mã QR | `không tìm thấy chuỗi nào` | PASS |
| 003 | 768px | 0 JS pageerror | `[]` | PASS |
| 003 | 1440px | khối PC hiện | `block` | PASS |
| 003 | 1440px | mobile ẩn | `none` | PASS |
| 003 | 1440px | không cuộn ngang | `0` | PASS |
| 005 | 391px | có 2 nút copy hiển thị | `2` | PASS |
| 005 | 391px | clipboard = giá trị nút #1 | `'0123456789' vs '0123456789'` | PASS |
| 005 | 391px | phản hồi nhìn thấy được #1 | `Đã sao chép` | PASS |
| 005 | 391px | clipboard = giá trị nút #2 | `'HCM-01 K33 55000' vs 'HCM-01 K33 55000'` | PASS |
| 005 | 391px | phản hồi nhìn thấy được #2 | `Đã sao chép` | PASS |
| 005 | 391px | 0 JS pageerror | `[]` | PASS |
| 005 | 1440px | có 2 nút copy hiển thị | `2` | PASS |
| 005 | 1440px | clipboard = giá trị nút #1 | `'0123456789' vs '0123456789'` | PASS |
| 005 | 1440px | phản hồi nhìn thấy được #1 | `Đã sao chép` | PASS |
| 005 | 1440px | clipboard = giá trị nút #2 | `'HCM-01 K33 55000' vs 'HCM-01 K33 55000'` | PASS |
| 005 | 1440px | phản hồi nhìn thấy được #2 | `Đã sao chép` | PASS |
| 005 | 1440px | 0 JS pageerror | `[]` | PASS |
| 002 | 391px | 0 nút copy | `0` | PASS |
| 002 | 391px | có thông báo chưa cấu hình | `True` | PASS |
| 002 | 391px | không dựng trường ngân hàng rỗng | `True` | PASS |
| 002 | 391px | không tràn ngang | `0` | PASS |
| 002 | 1440px | 0 nút copy | `0` | PASS |
| 002 | 1440px | có thông báo chưa cấu hình | `True` | PASS |
| 002 | 1440px | không dựng trường ngân hàng rỗng | `True` | PASS |
| 002 | 1440px | không tràn ngang | `0` | PASS |
| 002 | 1440px | modal PC: không nút copy khi chưa cấu hình | `0` | PASS |
| REG | 391px | /portal: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 391px | /portal/order: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 391px | /portal/purchase-history: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 391px | /portal/debt: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 391px | /portal/debt/payment-history: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 1440px | /portal: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 1440px | /portal/order: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 1440px | /portal/purchase-history: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 1440px | /portal/debt: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| REG | 1440px | /portal/debt/payment-history: không tràn ngang + 0 JS error | `[0, []]` | PASS |
| C2 | 391px | /pay khi hết nợ vẫn về /portal/debt?notice=no_due | `http://127.0.0.1:8053/portal/debt?week=2026-W29&notice=no_due` | PASS |
| C2 | 391px | tổng đa tệ vẫn nhiều dòng | `['Tổng đã xác nhận: 42.450,00 €', 'Tổng đã xác nhận: 60.000,00 $']` | PASS |
## Ghi chú trung thực

- **WJ-DEBT-003 — triệu chứng gốc của BA không tái hiện được ở lần tải mới.** Đo UAT ngày 15/08
  tại 500px (`/portal/debt`, `/portal/debt/payment-history`): `.main-menu` nằm ở `x=-260`
  (off-canvas), `scrollWidth == innerWidth == 500` ⇒ không có sidebar chiếm chỗ. Trang
  `/portal/debt/pay` trên UAT hiện redirect cả 6 tuần (cửa hàng hết nợ sau C2) nên không chụp
  lại được đúng ảnh BA. Cái **chắc chắn sai** và đã sửa: trang pay dựng markup mobile ở MỌI bề
  rộng (thiếu `d-lg-none`, lại còn CSS ghim cột 391 canh giữa trong shell PC) — nay tách hẳn
  khối mobile `<992` và khối PC `≥992`, đo đủ 6 breakpoint đều không tràn ngang.
- **WJ-DEBT-008** làm theo **nhánh OR** của acceptance BA (ẩn khối QR), đúng quyết định chủ dự án
  08-14. QR thật (VietQR tĩnh/động) vẫn chờ BA chốt CT-055 — sẽ mở issue riêng.
- **WJ-DEBT-005** đo bằng `navigator.clipboard.readText()` với permission `clipboard-read`;
  môi trường đo là HTTP (giống UAT) nên đường chạy thật là nhánh `execCommand`.

## Retest trên UAT sau deploy (15/08/2026, chỉ đọc)

Môi trường: `http://113.161.187.126:8019` — `wujia_portal_debt` **19.0.4.1.0** (xác nhận qua
`ir.module.module`). Harness `scratchpad/c3_uat.py` (bản UAT của `c3_measure.py`, đã **gỡ hẳn**
hàm đổi cấu hình bank — không ghi gì lên UAT). Dữ liệu đo: HCM-01, tuần `2026-W32`
(INV/2026/00001 còn dư 72.450 USD). Ảnh: `scratchpad/c3u_shots/`.

| Nhóm | Số điểm đo | Kết quả |
|---|---|---|
| WJ-DEBT-009 (spacing 360/391/430/500 + desktop 1440) | 34 | 34 PASS — đo đúng 16 / 12 / 24 / 12 / 12 / 12 ở cả 4 bề rộng |
| WJ-DEBT-003 (shell trang pay, 6 breakpoint) | 33 | 33 PASS — sidebar off-canvas, tràn ngang 0, `<992` chỉ khối mobile, `1440` chỉ khối PC |
| WJ-DEBT-008 (không còn QR) | 15 | 15 PASS — 0 element `.wj-debt-qr`/`.wj-debt-pc-qr`, HTML `/portal/debt` và `/portal/debt/pay` không còn chuỗi "Quét QR"/"QR minh họa"/"Tải mã QR" |
| WJ-DEBT-005 (copy + phản hồi, mobile & PC) | 12 | 12 PASS — 2 nút/khối, cả 4 lần bấm đều hiện "Đã sao chép" (UAT là HTTP ⇒ chạy nhánh `execCommand`) |
| WJ-DEBT-002 (nhánh đã cấu hình) | 2 | 2 PASS — đủ 4 dòng ngân hàng, không dòng rỗng, không hiện thông báo "chưa cấu hình" |
| Hồi quy 5 trang × 2 viewport | 10 | 10 PASS — 0 tràn ngang, 0 lỗi JS |
| Chốt C2 | 2 | 1 PASS (tuần hết nợ vẫn 302 `notice=no_due`) / 1 không áp dụng |

**107/108 (99,1%).** Điểm còn lại là **giả định của công cụ đo**, không phải lỗi màn hình: kịch
bản "tổng đa tệ nhiều dòng" viết cho DB copy có seed USD + EUR; UAT chỉ có **một** hoá đơn USD nên
bảng tổng đúng ra chỉ có 1 dòng (`Tổng đã xác nhận: 72.450,00 $`).

**Giới hạn của lần retest này:** nhánh **chưa cấu hình tài khoản** (WJ-DEBT-002) không đo được
trên UAT vì cần tắt `portal_payment_enabled` — là sửa cấu hình UAT, ngoài quyền chỉ-đọc. Nhánh đó
đã được phủ bằng 3 test tự động + đo Playwright trên DB copy (bảng phía trên).
