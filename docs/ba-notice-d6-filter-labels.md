# Đề nghị BA mở issue riêng — ô tìm kiếm / ô lọc của 8 màn danh sách chưa có tên cho trình đọc màn hình

**Nguồn:** lượt D6c (10/09/2026), cụm D6 Bù hàng. Phát hiện *kèm theo* khi đo `UAT-BH-009`,
**nằm ngoài phạm vi** phiếu đó nên Dev cố ý không tự sửa.

**Vì sao không gộp vào `UAT-BH-009`:** phiếu BH-009 nói về **biểu mẫu** (`/portal/return/new`).
Chỗ này là **ô lọc của màn danh sách** — khác màn, khác chuẩn (thanh lọc `CMP-FB-001` /
`UI-FILTER-001` BA chưa viết spec). Sửa kèm là nống phạm vi một phiếu đã đo xong.

---

## 1. Hiện trạng đo được

Guard `scripts/qa/wj_formcontrol.py`, 19 màn × 2 khổ điện thoại (390 và 360):

| Chỉ số | Trước D6c | Sau D6c |
|---|---:|---:|
| ô nhập không nối được nhãn | 58 lượt đo | **18 lượt đo** |

**18 lượt đo đó = 9 ô thật × 2 khổ màn.** (Ghi rõ để BA khỏi hiểu là 18 ô riêng biệt —
cùng một ô được đo ở cả 390 lẫn 360.) Chín ô nằm ở **8 màn**:

| # | Màn | Ô | Chữ gợi ý đang có | Nguồn |
|---:|---|---|---|---|
| 1 | Đặt hàng | ô tìm kiếm | *Nhập tên sản phẩm cần tìm* | `wujia_portal_sale/views/portal_order_catalog.xml:325` |
| 2 | Lịch sử đặt hàng | ô tìm kiếm | *Tìm theo mã đơn* | `wujia_portal_purchase_history/views/portal_history.xml:305` |
| 3 | Giao hàng | ô tìm kiếm | *Tìm mã chuyến / mã SO* | `wujia_portal_delivery/views/portal_delivery.xml:340` |
| 4 | Bù hàng | ô tìm kiếm | *Mã YC / mã đơn / sản phẩm* | `wujia_portal_return/views/portal_return_list.xml:185` |
| 5 | Thông báo | ô tìm kiếm | *Tìm mã / tiêu đề* | `wujia_portal_notification/views/portal_notification.xml:329` |
| 6 | Kiến thức | ô tìm kiếm | *Tìm kiếm bài viết…* | `wujia_portal_knowledge/views/portal_knowledge.xml:178` |
| 7 | Hỗ trợ | ô tìm kiếm | *Tìm mã / tiêu đề ticket* | `wujia_portal_support/views/portal_support.xml:160` |
| 8 | Yêu cầu cập nhật thông tin | ô lọc **Trạng thái** | có chữ *Trạng thái* hiện trên màn | `wujia_portal_info_request/views/portal_info_request_list.xml:37` |
| 9 | Yêu cầu cập nhật thông tin | ô lọc **Loại thông tin** | có chữ *Loại thông tin* hiện trên màn | `…/portal_info_request_list.xml:48` |

## 2. Hai kiểu thiếu khác nhau — nên tách khi viết phiếu

- **Ô 1–7 (bảy ô tìm kiếm):** chỉ có **chữ mờ gợi ý bên trong ô**. Chữ mờ **biến mất ngay khi
  người dùng gõ chữ đầu tiên**, và phần lớn trình đọc màn hình không coi nó là tên trường ⇒ người
  khiếm thị nghe được đúng chữ *"ô nhập văn bản"*, không biết đang tìm cái gì.
- **Ô 8–9 (hai ô lọc):** **đã có chữ hiện trên màn** (*Trạng thái*, *Loại thông tin*) — chỉ thiếu
  mối nối giữa chữ đó và ô. Nhìn bằng mắt thì đủ; máy đọc thì không nối được. Sửa nhẹ hơn hẳn.

## 3. Việc phải làm (ước lượng của Dev, để BA cân độ ưu tiên)

- Ô 8–9: đặt `id` cho ô + `for` cho nhãn đã có ⇒ **2 chỗ, sửa thuần XML**.
- Ô 1–7: thêm tên cho trình đọc màn hình mà **không đổi giao diện nhìn thấy** (chữ mờ giữ nguyên).
  Khuôn có sẵn ngay trong Portal: ô lọc trạng thái màn Bù hàng
  (`portal_return_list.xml:190`) đã làm đúng cách này từ trước ⇒ **chép khuôn, không phát minh**.
- Tổng: **9 ô / 7 tệp / 7 mô đun**, 1 lần `-u`, **không** đụng dữ liệu, **không** đụng luồng
  nghiệp vụ, **không** đổi một chữ nào người dùng nhìn thấy.

## 4. Ngoài phạm vi của đề nghị này

- **Bo góc và cỡ chữ của nhóm ô lọc** vẫn giữ nguyên (radius 10, cỡ 12). D6c chỉ nâng **chiều
  cao** vùng chạm lên 44. Muốn chuẩn hoá tiếp thì phải chờ spec `CMP-FB-001` / `UI-FILTER-001`.
- **Hai mô đun nhóm Khảo sát** cố ý không đụng (quyết định 08/09/2026).

## 5. Đề nghị

Xin BA mở **một phiếu riêng** cho cả 9 ô, mức Medium, gắn `Related Feature ID` về
`CMP-FB-001`, để làm một lượt cho toàn bộ 8 màn thay vì rải theo từng phiếu chức năng.
