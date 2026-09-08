# Synconics BI Dashboard — ghi chú của Ngô Gia (08/09/2026)

Bản gốc `synconics_bi_dashboard-19.0.1.0.3` (BA tải về, Odoo Apps, **license OPL-1**).
Đưa vào `custom/` để đánh giá. **Hiện `installable = False`** — đọc mục 2 trước khi bật lại.

## 1. Đã bỏ bớt khi đưa vào repo
Xoá `static/description/img/` (26 MB), `index.html` và `chart_images/` — chỉ là trang quảng cáo
trên Odoo Apps, không ảnh hưởng chức năng. Còn lại **11 MB** (5,9 MB là thư viện amCharts/gridstack/
jsPDF/html2canvas). Mã nguồn: 5 031 dòng Python + 5 926 dòng JS/XML/SCSS.

## 2. 🔴 XUNG ĐỘT: cài vào là TRẮNG MÀN toàn bộ backend

Đo trên bản sao `wujia_tea_d5g` ngày 08/09/2026, bật/tắt hai lần, kết quả lặp lại y hệt:

| Trạng thái | Backend (`/odoo/settings`) | Lỗi JS |
|---|---|---|
| Chưa cài | tải bình thường | 0 |
| **Đã cài** | **trắng trơn, `body` rỗng** | `TypeError: Cannot read properties of undefined (reading 'call')` + `@muk_web_refresh/core/utils`, `@muk_web_chatter/...` "not defined" |
| Gỡ ra | tải bình thường trở lại | 0 |

**Nguyên nhân đã truy được, không phải phỏng đoán:** `wj_ks_dashboard_ninja` (Dashboard Ninja của
Ksolves, đã cài từ trước) **cũng đóng gói amCharts 5**. Đếm trong chính gói asset đang chạy:

| Dấu hiệu trong `web.assets_web.js` | DB sạch chỉ có Synconics | DB Ngô Gia (có cả hai) |
|---|---:|---:|
| `webpackChunk_am5` | 28 | **48** |
| `jsPDF` | 95 | **191** |
| `GridStack` | 13 | **49** |

Hai bản runtime webpack của amCharts nằm trong **một** gói ⇒ chunk của bản này chạy vào runtime của
bản kia ⇒ ném lỗi giữa gói ⇒ **mọi module định nghĩa SAU đó không kịp đăng ký** (đó là lý do
`muk_web_refresh` và `muk_web_chatter` báo "not defined" — chúng là nạn nhân, không phải thủ phạm).

**Module KHÔNG hỏng:** cài trên một DB trắng (`base` + `web` + Synconics) → backend chạy, **0 lỗi JS**;
thêm cả `muk_web_theme` + `muk_web_refresh` + `muk_web_chatter` vào → vẫn **0 lỗi JS**. Nó chỉ không
sống chung được với Dashboard Ninja.

⇒ **Muốn dùng thì phải chọn một trong hai**, hoặc gỡ trùng thư viện amCharts/jsPDF/html2canvas ở một
bên. Cả hai đều là OPL-1 nên sửa thư viện của bên thứ ba là việc phải cân nhắc.

## 3. Điều kiện chạy khác
- `external_dependencies: python: ["imgkit"]` ⇒ máy chủ phải `pip install imgkit` **và** có sẵn
  `wkhtmltoimage`. Máy dev đã cài đủ; **UAT chưa kiểm**.
- Cài đặt trên Odoo 19 sạch: **RC=0, 0 ERROR** (99 module nạp trong 1,73 s).
- `version` trong manifest là `1.0.3`, **không** theo quy ước `19.0.x.y.z` của dự án.

## 4. Đánh giá kỹ thuật (nếu sau này chọn dùng)
- **Hiệu năng — điểm trừ nặng với 1500 user:** toàn bộ 3 460 dòng `models/dashboard_chart.py`
  **không dùng `read_group`/`_read_group` một lần nào**; mọi biểu đồ đều `record_obj.search(domain)`
  rồi `.filtered()` + gom nhóm bằng Python. Nghĩa là **nạp toàn bộ bản ghi vào RAM mỗi lần vẽ**.
  Trái thẳng luật "Performance-first" của dự án (§7 compact summary).
- **Phân quyền:** `ir.model.access.csv` cấp **CRUD đầy đủ cho `base.group_user`** trên cả 9 model
  của nó ⇒ mọi nhân viên nội bộ tạo/sửa/xoá được dashboard, và dashboard đọc được **model bất kỳ**
  qua domain tự nhập. Không ảnh hưởng portal (module chỉ nạp `web.assets_backend`), nhưng nếu dùng
  thì phải siết lại nhóm.
- `sudo()` 16 chỗ, đều là tra `ir.model` / `ir.model.fields` / `ir.config_parameter` — không phải
  đường ghi dữ liệu nghiệp vụ.
- **Không có gì dùng lại được cho Portal**: 100 % là backend (`web.assets_backend`), không có
  template portal, không có route `/portal`. Thư viện amCharts thì đã có sẵn ở Dashboard Ninja.

## 5. Kết luận đề xuất
Giữ mã ở đây để BA/chủ dự án xem, **chưa cài lên UAT**. Nếu muốn thử: gỡ `wj_ks_dashboard_ninja`
+ `wj_ks_dn_advance` trên một bản sao trước, đo lại, rồi mới quyết. Bật lại bằng cách đổi
`installable` về `True` trong `__manifest__.py`.
