# ★IR — Nghiệm thu cụm I trên UAT (09/10/2026)

UAT `http://113.161.187.126:8019`, đo **chỉ đọc** bằng Playwright + XML-RPC sau khi chủ dự án deploy toàn cụm I
(I1→I13, 21 issue). Kiểm version trước khi đo: manifest repo = `ir.module.module.latest_version`, **0 module lệch**.
Dữ liệu đã cập nhật đúng: khung giờ đặt hàng 1, 2 giữ khu vực `[1]`; múi giờ cửa hàng điền `Asia/Ho_Chi_Minh`
(TEST-134 giữ `Asia/Bangkok`); 15 dấu đã đọc thông báo sau gộp.

Script: `scripts/qa/wj_ir_matrix.py` (ma trận) · `scripts/qa/wj_ir_checks.py` (từng issue) · `scripts/qa/wj_contrast.py` (#170).
Kết quả thô: `docs/i-review/matrix.json`, `checks.json`, `contrast.json`, ảnh ô lỗi `docs/i-review/shots/`.

## 1. Ma trận role × cửa hàng × route

5 ngữ cảnh × 2 khổ (1440, 390) × 28 route + trang chi tiết = **274 ô, 252 đạt**, 0 HTTP ≥500, 0 lỗi JS, 0 tràn ngang.

| Ngữ cảnh | Ghi chú |
|---|---|
| `em.hcm` (owner, 1 cửa hàng, tự chọn) | toàn xanh |
| `anh.owner` (1 cửa hàng) | toàn xanh |
| `admin` chưa chọn cửa hàng (nhiều cửa hàng) | 20 ô "lệch" = kỳ vọng script quá chặt, xem dưới |
| `admin` @ HCM-01 (quản lý) | toàn xanh |
| `admin` @ HN-01 (nhân viên) | 2 ô `/portal/reports/orders` 403 = **đúng #153** (script cắt route sai tiền tố) |

**admin chưa chọn cửa hàng — quét lộ dữ liệu:**
- Đặt hàng, giỏ, lịch sử, công nợ và chi tiết sản phẩm hiện lời nhắc riêng của từng màn: "Vui lòng chọn cửa hàng…", "Chưa chọn cửa hàng", "0 hóa đơn". Không có mã chứng từ nào.
- Đặt hàng chỉ hiện catalog sản phẩm chung.
- Thông báo, hỗ trợ tạo mới và hồ sơ cửa hàng hiện khối nhắc chọn.
- Thông báo chỉ liệt kê 2 tin `target_mode='all'` (id 1, 19), đúng tooltip "chỉ thông báo áp dụng mọi cửa hàng".

## 2. Từng issue

| # | Issue | Kết quả UAT |
|---|---|---|
| 62 | WJ-PH-003 | Lọc Đã hủy có S00076 · chi tiết đơn huỷ 200 · đơn HN-01 không đọc được từ HCM-01 |
| 152 | WJ-PORTAL-SCOPE-001 | Chưa chọn cửa hàng: Trang chủ/Giao hàng/Báo cáo/Đổi trả/YC cập nhật hiện khối nhắc, 0 mã chứng từ |
| 153 | WJ-PORTAL-ROLE-001 | Nhân viên HN-01: Công nợ, Lịch sử TT, Báo cáo, YC cập nhật (+/new) ⇒ 403; Home không có ô Công nợ; menu ẩn. Quản lý HCM-01 ⇒ 200 |
| 154 | WJ-ORD-030 | Dữ liệu sau cập nhật đúng (khu vực, múi giờ); /portal/order 200 mọi ngữ cảnh. Không đo được kịch bản gửi đơn ngoài giờ trên UAT (§10, không tạo đơn) — đã đo ở DB copy I3 |
| 155 | WJ-ORD-031 | Danh sách/chi tiết/giỏ 200, 0 lỗi JS. Kịch bản SP thiếu danh mục cần sửa dữ liệu ⇒ không đo trên UAT — đã đo ở DB copy I1 |
| 156 | WJ-RETURN-001 | Form đổi trả 1440/390: 0 chỗ "Lưu nháp" |
| 157 | WJ-EXAM-001 | Chưa chọn cửa hàng: /portal/exam hiện khối nhắc, 0 mã |
| 159 | WJ-NOTI-001 | em.hcm@HCM-01: chuông = KPI Home = lọc Chưa đọc = endpoint = **1** (đo tay; lần chạy script cũ gọi GET vào endpoint JSON nên báo sai, đã sửa script) |
| 160 | WJ-ORD-032 | Chi tiết SP @360/390/430: số lượng/Thêm/Xem giỏ trong viewport, 0 tràn |
| 162 | WJ-SUPPORT-002 | Mobile WJ-TK/26/00016 có khối Nội dung, 0 tràn |
| 163 | WJ-PH-009 | S00077 có "Ghi chú khi đặt hàng" trên PC và mobile |
| 164 | WJ-INSPECT-001 | Khảo sát @1440/1920: header Tiếng Việt |
| 166 | WJ-EXAM-008 | Modal Thêm người @1440/1920: chưa chọn ("Chưa chọn ảnh", nút Chọn ảnh, ẩn Xoá) ↔ đã chọn ("Ảnh đã được chọn", Thay ảnh, Xoá, tên tệp, ảnh) ↔ xoá về chưa chọn — không bao giờ đồng thời (chỉ thao tác phía trình duyệt, không gửi) |
| 167 | WJ-LANG-002 | Cờ đang chọn 20×15 @1440/1920 |
| 168 | UI-LISTCARD-002 | ListCard title 15/600/20 · label 12/500/18 · value 13/500/18 |
| 169 | WJ-PORTAL-UI-005 | Dialog @1440/390: role dialog, aria-modal, có tên, focus vào trong, Tab không thoát, Esc đóng + trả focus |
| 170 | WJ-PORTAL-UI-006 | **UAT 32 cặp <4.5** (local 0) ⇒ sửa thêm, xem §3 |
| 171 | WJ-HOME-001 | Home @1440/390: đúng 1 H1 (ẩn), không câu chào |
| 172 | WJ-PROFILE-001 | PC + mobile cùng nhóm trường và giá trị; mobile ghi nhãn "SĐT" (rút gọn), cùng `franchise.phone` |
| 173 | WJ-PROFILE-002 | Còn lại 584 ngày = 15/05/2028 − 09/10/2026 (tz cửa hàng) — khớp 585 của BA ngày 08/10 |
| 174 | WJ-PROFILE-003 | Thành viên @320/360/390/430: 0 tên bị cắt, 0 tràn |

## 3. Sửa trong ★IR — #170 tương phản trên UAT

Nguyên nhân local đo 0 mà UAT ra 32:
1. Chip lọc Giao hàng (Tất cả/Sắp giao/Đã giao) và chip mã đơn ở chi tiết giao hàng **chỉ hiện khi có dữ liệu giao hàng**. Local không có nên không đo được. Token chữ của chúng còn màu gốc: `#28A9DF` 2.45, `#D97706` 2.86, `#059669` 3.43, `#8A939E` 2.83.
2. Số "Đã thanh toán" bên Công nợ trên điện thoại dùng `--wujia-success` `#16A34A`, chỉ đạt 3.30.
3. Placeholder chung `:where(input, textarea)::placeholder` có đặc hiệu 0. Trên UAT có `website`, nên `.form-control::placeholder` của `web.assets_frontend` (`#909294`, 3.12) nạp sau và đè mất (bài học L14).

Sửa:
- `portal_delivery.css`: 4 token chữ chuyển sang `brand-text`/`warning-text`/`success-text`/`text-muted`.
- `portal_debt.css`: `--wj-debt-success` → `--wujia-success-text`.
- `_components.css`: thêm `body .form-control::placeholder`.
- `?v=1336`. Version: `portal_layout` 19.0.60.10.1, `portal_delivery` 19.0.4.2.1, `portal_debt` 19.0.5.2.1.

Deploy:
`nssm stop Odoo; python D:\wujia-tea\odoo19\odoo-bin -c D:\wujia-tea\config\odoo-server.conf -d wujia_tea_19 --addons-path "D:\wujia-tea\custom,D:\wujia-tea\odoo19\addons" -u wujia_portal_layout,wujia_portal_delivery,wujia_portal_debt --stop-after-init; nssm start Odoo`
— sau đó chạy lại `wj_contrast.py --base <UAT> --login em.hcm` (mục tiêu 0 cặp).

## 4. Rà diff cụm I

- Phạm vi: `0b5834d2^..HEAD -- custom/`. Không chạm module anh Thái (thay đổi `muk_*` đến từ merge nhánh thai).
- Mọi module đều bump version ở commit code cuối. Không còn code debug.
- `check_layers`: R6 0 · R7 2 (cũ, nằm trong `wujia_franchise`). `vn_hardcode_scan` module team: 0.
- Comment ghi mã issue là quy ước sẵn có (108 chỗ trước cụm I). Có 7 comment ghi ngày, mức nhỏ, để nguyên.

## 5. Nợ / LIMIT

- #142 UI-PC-HOME-REDESIGN-001 (BA RETEST FAIL 08/10 vì Home hiện `$`): **do dữ liệu, không phải code**. Công ty dùng VND nhưng partner HCM-01 gắn pricelist "Default (USD)" (id 1) ⇒ đơn ra USD. Chờ chủ dự án chọn sửa dữ liệu UAT hay trả lời BA.
- `wj_ir_matrix.py`: `expect()` chưa biết các màn tự xử lý `no_store` (đặt hàng, giỏ, lịch sử, công nợ) và các màn cố ý hiện khối nhắc (thông báo, hỗ trợ tạo mới, hồ sơ). Route `/portal/reports/orders` bị cắt còn `/portal/reports`. Chỉ cần sửa kỳ vọng, không có lỗi sản phẩm.
- Kịch bản cần ghi dữ liệu (#154 gửi đơn ngoài giờ, #155 SP thiếu danh mục) không đo trên UAT theo §10; bằng chứng nằm ở DB copy của I1/I3.
