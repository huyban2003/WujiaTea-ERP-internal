# Tài liệu cập nhật tính năng Lịch Giám Sát (Custom OWL Calendar Dashboard)

Tài liệu này ghi lại toàn bộ các thay đổi và cấu hình liên quan đến việc triển khai giao diện **Lịch Giám Sát tùy chỉnh** trong module `wujia_franchise` trên Odoo 19.

---

## 1. Danh sách các File được tạo mới và cập nhật

### A. Python Backend (Models & Cấu hình)

#### 1. [wujia_franchise_inspection.py](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/models/wujia_franchise_inspection.py)
* **Nhiệm vụ**: Thêm các hàm nghiệp vụ phục vụ giao diện OWL:
  * `get_schedule_data`: Truy vấn dữ liệu từ DB (Cửa hàng hoạt động, danh sách người giám sát, danh sách khu vực và các lịch đã có trong hệ thống) chuyển về dạng JSON cho máy khách.
  * `save_schedule_data`: Xử lý lưu lịch hàng loạt. Tự động thêm phiếu mới kèm việc sao chép toàn bộ dòng tiêu chí từ mẫu template hoạt động, hoặc tự động hủy các lịch cũ ở trạng thái nháp khi người dùng bỏ tích chọn.

#### 2. [__manifest__.py](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/__manifest__.py)
* **Nhiệm vụ**: 
  * Đăng ký phụ thuộc vào module base `'calendar'` để nạp đầy đủ thư viện lịch.
  * Khai báo tệp XML mới `views/wujia_franchise_inspection_schedule_views.xml`.
  * Khai báo các tệp tài nguyên tĩnh (assets) trong nhóm `'web.assets_backend'` gồm: JS, XML và SCSS của lịch tùy biến.

---

### B. XML Giao diện & Cấu hình Menu

#### 3. [wujia_franchise_inspection_schedule_views.xml](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/views/wujia_franchise_inspection_schedule_views.xml)
* **Nhiệm vụ**: 
  * Khai báo Client Action mới `action_inspection_schedule_custom` liên kết với tag của OWL Component (`wujia_franchise.inspection_schedule_custom`).
  * Khai báo phục hồi lại Window Action mặc định `action_inspection_schedule` để giữ an toàn cho CSDL khi nâng cấp.

#### 4. [wujia_franchise_menu.xml](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/views/wujia_franchise_menu.xml)
* **Nhiệm vụ**: Cập nhật menu **Lịch giám sát** (`menu_giam_sat_lich`) để khi người dùng nhấp vào sẽ mở Client Action tùy biến mới (`action_inspection_schedule_custom`).

#### 5. [wujia_franchise_inspection_extra_views.xml](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/views/wujia_franchise_inspection_extra_views.xml)
* **Nhiệm vụ**: Dọn dẹp/comment bỏ định nghĩa action cũ tránh bị xung đột Model khi nâng cấp.

---

### C. Giao diện tùy biến Frontend (OWL JS, XML Template, SCSS Styles)

#### 6. [inspection_schedule.js](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/static/src/js/inspection_schedule.js) (TẠO MỚI)
* **Nhiệm vụ**: 
  * Khởi tạo OWL Component và đăng ký vào Odoo Actions Registry.
  * Tích hợp bộ tải động tự động (Dynamic Loader) tải FullCalendar từ CDN khi mở trang lịch.
  * Quản lý trạng thái giao diện (Ngày chọn, danh sách cửa hàng, bộ lọc tìm kiếm khu vực/trạng thái, người giám sát).
  * Đồng bộ hiển thị dạng `[Mã cửa hàng] Tên cửa hàng` lên lịch và danh sách chọn.
  * Tự động cập nhật (refetch) và vẽ lại các sự kiện thời gian thực khi chuyển tháng hoặc khi Lưu lịch.

#### 7. [inspection_schedule.xml](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/static/src/xml/inspection_schedule.xml) (TẠO MỚI)
* **Nhiệm vụ**: Xây dựng cấu trúc HTML/XML cho giao diện 2 cột:
  * Bên trái: Khối lịch FullCalendar.
  * Bên phải: Panel chọn người giám sát, lọc tìm kiếm/khu vực/trạng thái, danh sách hộp kiểm cửa hàng dạng `[Mã] Tên`, nút **Lưu lịch**, và danh sách lịch sắp tới.

#### 8. [inspection_schedule.scss](file://wsl.localhost/Ubuntu/home/khang04/WujiaTea-ERP-internal/custom/wujia_franchise/static/src/scss/inspection_schedule.scss) (TẠO MỚI)
* **Nhiệm vụ**: Căn chỉnh kích thước giao diện, bo tròn viền, đổ bóng và tạo phong cách hiển thị cao cấp cho bảng điều khiển.

---

## 2. Luồng nghiệp vụ chính của Giao diện
1. Người điều hành chọn ngày cần giám sát trên Lịch tháng (cột trái).
2. Panel bên phải tự động hiển thị ngày đã chọn và tải trạng thái lịch của ngày đó.
3. Người điều hành chọn Người giám sát -> lọc nhanh cửa hàng bằng ô tìm kiếm/Khu vực/Trạng thái nếu cần.
4. Tích chọn các cửa hàng cần đi giám sát trong ngày đã chọn.
5. Nhấp nút **Lưu lịch giám sát**:
   * Odoo gửi dữ liệu lưu về Backend.
   * Hệ thống sinh tự động các Phiếu giám sát Nháp, nạp sẵn danh mục và tiêu chí kiểm tra cho các cửa hàng được chọn.
   * Lịch vẽ thêm các sự kiện mới vừa lập và danh sách "Lập Lịch Sắp Tới" tự động cập nhật.
