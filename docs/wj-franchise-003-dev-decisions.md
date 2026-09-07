# WJ-FRANCHISE-003 — Những chỗ Dev tự quyết mà spec BA không nói

**Gửi BA rà.** Spec của issue STT 134 để mở khá nhiều chi tiết kỹ thuật. Dưới đây là **toàn bộ** chỗ
Dev phải tự chọn, kèm lý do và hậu quả nếu BA muốn đổi. Không mục nào đã được BA duyệt trước —
xin BA đọc và xác nhận (hoặc yêu cầu đổi) trước khi đóng issue.

Ngày: 04/09/2026 · Module `wujia_franchise` `19.0.4.0.0`.

---

### 1. Cửa hàng tạo mới **luôn** ở trạng thái Nháp, kể cả khi không đi qua wizard
- **BA nói:** "Tạo `wujia.franchise.management` ở trạng thái Draft" — trong ngữ cảnh luồng onboarding.
- **Dev chọn:** đổi mặc định của trường Trạng thái từ *Đang hoạt động* sang *Nháp* cho **mọi** cửa hàng
  tạo mới, kể cả HQ tạo tay bằng nút New như cũ.
- **Vì sao:** nếu chỉ wizard mới ra Nháp thì vẫn còn đường tạo cửa hàng Đang-hoạt-động mà chưa có chủ
  tiệm — đúng cái lỗ hổng issue muốn bịt.
- **Nếu BA muốn đổi:** quay lại mặc định cũ là 1 dòng code, nhưng khi đó phải chấp nhận cửa hàng tạo tay
  không đi qua kiểm tra nào.

### 2. Cửa hàng **cũ** giữ nguyên trạng thái, không viết script sửa dữ liệu
- **BA nói:** không đề cập.
- **Dev chọn:** không đụng bản ghi cũ. Trên UAT hiện có 3 cửa hàng, cả 3 đang *Đang hoạt động* và giữ nguyên.
- **Vì sao:** ghi đè trạng thái dữ liệu thật là việc không thể hoàn tác, phải do BA quyết.

### 3. Cửa hàng Nháp **chỉ** bị chặn ở Portal, backend vẫn phát sinh chứng từ được
- **BA nói:** "Store được tạo ở Draft và chưa cho phát sinh giao dịch".
- **Dev chọn:** giữ nguyên lớp chặn Portal đã có (cửa hàng không *Đang hoạt động* thì không vào Portal
  được); **không** thêm chặn ở bước Xác nhận đơn bán và Ghi sổ hoá đơn.
- **Vì sao:** hai chỗ đó là code vừa nghiệm thu ở cụm C1/C2 (WJ-FRANCHISE-001/002, WJ-DEBT-006). Thêm
  điều kiện vào đó buộc phải chạy lại toàn bộ hồi quy của cụm ấy, và có thể chặn nhầm dữ liệu UAT.
- **Nếu BA muốn chặn cả backend:** xin mở issue riêng, Dev làm kèm hồi quy C1/C2.

### 4. Hồ sơ cá nhân của tài khoản Portal **không** làm hồ sơ con của Đối tác cửa hàng
- **BA nói:** "res.users.partner_id là contact cá nhân", không nói đặt ở đâu.
- **Dev chọn:** tạo hồ sơ cá nhân đứng độc lập, không gắn cha.
- **Vì sao:** nếu gắn làm con của Đối tác cửa hàng thì Odoo coi "đối tác thương mại" của người đó chính
  là cửa hàng, và bộ quy tắc suy ra cửa hàng từ đối tác (làm ở cụm C1) sẽ tự gán cửa hàng cho **mọi**
  chứng từ mang tên cá nhân đó. Rủi ro lẫn công nợ.
- **Đánh đổi:** trong danh bạ, người dùng của cửa hàng **không** hiện gom dưới cửa hàng.

### 5. Đối tác cửa hàng tạo mới ở dạng **Công ty**
- **BA nói:** không đề cập.
- **Dev chọn:** `company_type = 'company'`; hồ sơ cá nhân của tài khoản Portal thì `'person'`.
- **Vì sao:** Đối tác cửa hàng là chủ thể giao dịch/công nợ.

### 6. Tiêu chí dò trùng khi tạo Đối tác cửa hàng mới
- **BA nói:** "cảnh báo trùng", không nói dò theo gì.
- **Dev chọn:** trùng **tên** hoặc **8 chữ số cuối của điện thoại** hoặc **email** hoặc **mã số thuế**
  ⇒ hiện danh sách tối đa 10 ứng viên và **chặn** cho tới khi HQ tick ô xác nhận "tôi đã xem, vẫn tạo mới".
- **Vì sao:** cảnh báo mà bấm qua được thì không ai đọc; chặn cứng thì không tạo nổi hai cửa hàng cùng
  một chủ. Ô tick là điểm giữa.
- **Ghi chú kỹ thuật:** Odoo 19 đã bỏ trường *Di động* trên đối tác nên không dò được cột đó.

### 7. Điều kiện Kích hoạt đặt ở **nút bấm**, không phải ràng buộc dữ liệu
- **BA nói:** "Activate Store chỉ khi đã có Store Partner hợp lệ và tối thiểu một Owner/membership hợp lệ".
- **Dev chọn:** kiểm tra khi HQ bấm nút *Kích hoạt*, không phải mỗi lần lưu bản ghi.
- **Vì sao:** nếu làm thành ràng buộc dữ liệu thì cửa hàng cũ đang hoạt động mà thiếu chủ tiệm sẽ **không
  sửa nổi bất cứ trường nào**, kể cả ghi chú.
- **Ảnh hưởng thật đã đo trên UAT:** 1 cửa hàng (`HN-02`) đang hoạt động nhưng **không có chủ tiệm hiệu
  lực**. Với lựa chọn hiện tại nó vẫn chạy bình thường; chỉ khi khoá rồi kích hoạt lại mới bị chặn.
  Nhờ BA xác nhận `HN-02` có đúng là thiếu chủ tiệm không.

### 8. Quyền tạo tài khoản: nâng quyền **bên trong** wizard thay vì cấp quyền quản trị cho HQ
- **BA nói:** "Chỉ HQ được chạy onboarding/quản lý membership".
- **Dev chọn:** wizard kiểm tra người dùng thuộc nhóm *Wujia Franchise / Administrator* rồi mới chạy
  bằng quyền hệ thống để tạo đối tác + tài khoản + membership.
- **Vì sao:** cách còn lại là cấp quyền quản trị người dùng cho HQ — khi đó HQ sửa được **mọi** tài
  khoản kể cả tài khoản nội bộ, rộng hơn nhiều so với điều BA cần.

### 9. Quy tắc đặt tên đăng nhập
- **BA nói:** không đề cập.
- **Dev chọn:** lấy đúng ô *Tên đăng nhập (email)* HQ nhập, chuyển thành chữ thường. Không tự sinh.
- **Vì sao:** tự sinh tên đăng nhập là nguồn gốc của mớ tài khoản rác đang có (xem mục 11).

### 10. Giá trị mặc định của membership tạo qua wizard
- **BA nói:** không đề cập.
- **Dev chọn:** *Hiệu lực từ* = hôm nay, *Hiệu lực đến* để trống, vai trò mặc định *Nhân viên*.

### 11. ⚠️ Ngoài phạm vi nhưng BA cần biết — còn một chỗ khác đang tự đẻ tài khoản trùng
- Màn **phiếu giám sát cửa hàng** (`wujia_franchise/models/wujia_franchise_inspection.py` dòng 1772)
  đang tìm người dùng **theo TÊN**, không thấy thì tự tạo tài khoản Portal với tên đăng nhập ngẫu nhiên
  dạng `ten.nhan.vien.1234@wujiatea.internal`.
- Đây đúng là kiểu sinh tài khoản trùng mà WJ-FRANCHISE-003 muốn dẹp, nhưng nằm ở luồng giám sát chứ
  không phải luồng onboarding ⇒ Dev **không tự sửa** trong issue này.
- **Đề xuất:** BA mở issue riêng để đưa chỗ đó về dùng chung luồng onboarding.

### 12. Điểm vào wizard
- **BA nói:** "Đề xuất Dev triển khai wizard hoặc staged form trong Store Master".
- **Dev chọn:** wizard, vào được từ **3 chỗ**: menu *Vận hành → Onboarding cửa hàng* (tạo mới), nút
  *Store onboarding* trên cửa hàng Nháp, nút *Add store users* trên mọi cửa hàng.
- **Vì sao:** nếu chỉ có luồng tạo mới thì cửa hàng đã tồn tại vẫn phải thêm người dùng bằng cách cũ.

### 13. Dịch màn hình mới sang tiếng Việt (phát sinh khi test trên UAT ngày 04/09)
- **BA nói:** không đề cập ngôn ngữ.
- **Phát hiện khi test:** sau khi deploy, toàn bộ màn onboarding hiện **tiếng Anh** giữa một backend
  tiếng Việt — nút *Add store users*, tiêu đề *Store onboarding*, các cột *Full name / Login (email) /
  Role*, và cả câu báo lỗi *"Please add at least one store user."*. Người dùng màn này là nhân sự HQ
  người Việt nên đây không phải chuyện thẩm mỹ.
- **Dev chọn:** dịch bằng file ngôn ngữ trong mã nguồn (`i18n/vi_VN.po`), không dịch tay trên giao diện.
- **Vì sao:** bản dịch tiếng Việt hiện có của module nằm **trong database chứ không nằm trong mã nguồn**
  — dựng lại database là mất sạch, và bản chạy thật sau này sẽ phải dịch lại từ đầu. Đưa vào mã nguồn
  thì bản dịch đi theo mọi lần cài đặt.
- **Việc kèm theo:** bỏ đánh số "1. / 2. / 3." ở tiêu đề ba khối, vì khi mở ở chế độ *thêm người dùng*
  thì khối 1 và 2 bị ẩn, chỉ còn mỗi nhãn "3." đứng trơ. Tiêu đề hộp thoại nay đổi theo chế độ:
  *Onboarding cửa hàng* khi tạo mới, *Thêm người dùng cửa hàng* khi bổ sung người dùng.
- **Nếu BA muốn đổi chữ:** sửa trong `custom/wujia_franchise/i18n/vi_VN.po` rồi deploy lại, không cần
  sửa mã.

- **Ghi chú kỹ thuật (phát hiện ở lượt kiểm lần hai):** câu báo lỗi và tiêu đề hộp thoại sinh từ mã
  chương trình cần một dòng đánh dấu riêng trong file ngôn ngữ thì mới được dịch. Thiếu dòng đó thì
  không có lỗi nào hiện ra, chữ chỉ lặng lẽ giữ nguyên tiếng Anh — nên bản dịch phải kiểm bằng cách
  mở màn hình thật chứ không tin vào việc "file đã có chữ tiếng Việt".
