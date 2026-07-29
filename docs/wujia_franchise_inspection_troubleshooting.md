# Wujia Franchise Inspection Troubleshooting

Tài liệu này ghi lại các lỗi đã gặp khi upgrade module `wujia_franchise` và cách xử lý tương ứng.

## 1. `ir.model.access.csv` báo không tìm thấy model

### Triệu chứng

Khi upgrade module, Odoo báo:

- `No matching record found for external id 'model_wujia_franchise_inspection_template'`
- `Missing required value for the field 'Model' (model_id)`

### Nguyên nhân

Model Python chưa được đăng ký đúng vào registry. Trường hợp đã gặp là file `models/__init__.py` có dòng import sai:

- `from . import models`

Trong thư mục `models/` không có file `models.py`, nên package load bị lệch.

### Cách xử lý

- Xóa import sai trong `custom/wujia_franchise/models/__init__.py`
- Đảm bảo `__init__.py` chỉ import đúng các file model thực tế
- Kiểm tra file model có khai báo đúng `_name` khớp với XML ID trong `ir.model.access.csv`

## 2. View type `tree` không còn hợp lệ trên Odoo 19

### Triệu chứng

Odoo báo:

- `Invalid view type: 'tree'`
- `Allowed types are: list, form, graph, pivot, calendar, kanban, search, qweb, activity`

### Nguyên nhân

Từ Odoo 19, root view type cho danh sách đã đổi từ `tree` sang `list`.

### Cách xử lý

- Đổi tất cả `<tree>` root view thành `<list>`
- Đổi `view_mode` từ `tree,form` sang `list,form`
- Kiểm tra cả view con bên trong form nếu có danh sách inline

## 3. `states` và `attrs` bị loại bỏ trong view

### Triệu chứng

Odoo báo:

- `Since 17.0, the "attrs" and "states" attributes are no longer used.`

### Nguyên nhân

Nhiều XML view cũ vẫn dùng thuộc tính `states` để ẩn/hiện button theo trạng thái.

### Cách xử lý

- Thay `states="draft"` bằng biểu thức `invisible="status != 'draft'"`
- Áp dụng tương tự cho mọi button hoặc field còn dùng `states`/`attrs`

## 4. Tạo model nhưng thiếu field mà view đang gọi

### Triệu chứng

Sau khi sửa lỗi import/view, Odoo có thể tiếp tục báo lỗi field không tồn tại trong view.

### Nguyên nhân

View XML gọi các field như `description`, `active`, `line_ids`, `template_id`, `status`, `message_ids`, `activity_ids`, nhưng model chưa khai báo đầy đủ.

### Cách xử lý

- Đọc view XML trước rồi đối chiếu từng field với model Python
- Bổ sung field tối thiểu để view load được
- Nếu dùng `mail.thread` hoặc `mail.activity.mixin`, thêm `_inherit` tương ứng để có `message_ids` và `activity_ids`

## 5. Checklist xử lý nhanh cho các lỗi kiểu này

1. Đọc traceback để xác định lỗi đang nằm ở Python import, model registry hay XML view.
2. Kiểm tra `models/__init__.py` có import đúng file hay không.
3. Kiểm tra `_name` của model có khớp với `model_xxx` trong `ir.model.access.csv`.
4. Kiểm tra view root type trên Odoo 19, ưu tiên `list` thay cho `tree`.
5. Kiểm tra `states` và `attrs`, thay bằng biểu thức `invisible` hoặc `readonly` mới.
6. Parse XML trước khi upgrade để bắt lỗi sớm.
7. Restart Odoo sau khi sửa model Python, rồi upgrade module lại.

## 6. Ghi chú thực tế từ lần sửa này

- `custom/wujia_franchise/models/__init__.py` đã bị import sai `from . import models`
- `wujia_franchise_inspection_views.xml` đã phải đổi `tree` sang `list`
- `wujia_franchise_inspection_views.xml` đã phải bỏ `states` khỏi header buttons

Khi gặp lại lỗi tương tự, mở file này trước để tránh đi vòng qua cùng một nhóm nguyên nhân.
