# Wujia / Ngô Gia — Odoo 19 module icons

Phương án đã chốt:

- `franchise-management-f1`: mạng lưới cửa hàng nhượng quyền.
- `fleet-management-v1`: xe đội vận hành.

## File triển khai

- Dùng file PNG 128×128 làm icon module trên Odoo.
- Đặt file vào thư mục module thực tế tại `static/description/icon.png`.
- Nếu manifest đang khai báo `web_icon`, giữ đúng tên technical module hiện hữu; không đổi theo tên file trong gói này.
- SVG là source vector để chỉnh sửa về sau. PNG 256×256 dùng cho tài liệu hoặc màn hình mật độ điểm ảnh cao.

## Màu sử dụng

- Wujia cyan: `#28A9DF`
- Odoo plum: `#9B4F86`
- Dark blue: `#1E6B8F` / `#274D61`
- Accent gold: `#FFB547`

Icon dùng nền trắng, hình khối phẳng, không chữ và không hiệu ứng bóng trong file để tương thích với cách launcher Odoo tự hiển thị bo góc/bóng.
