# Gửi BA — `UI-SURFACECARD-001` (STT 127): **không có câu hỏi nào chặn việc**

**Từ:** Dev · **Gửi:** BA · **Ngày:** 04/09/2026 · **Đây là thông báo, không phải câu hỏi.**

Dev đã đối chiếu bảng thành phần SurfaceCard với **toàn bộ mã nguồn thật** (442 chỗ dùng thẻ →
67 nhóm → **27 nhóm là "khung thẻ" thật**) và **mở trang thật trên trình duyệt** ở hai khổ màn
hình để soát chỗ *"thẻ trắng lồng trong thẻ trắng"*. Có **bốn chỗ** ban đầu tưởng phải hỏi BA;
rà kỹ thì **cả bốn đều tự quyết được**. Dev nêu ra đây để BA nắm, **không cần trả lời** — BA
thấy chỗ nào không ổn thì báo, Dev sửa gọn.

---

## 1. Màn *Khảo sát cửa hàng* — để nguyên đợt này

**Chính BA đã viết sẵn trong bảng thành phần:** *"Khảo sát: provisional record; UAT chưa có
seed data nên chưa khóa field mapping"*, và điều kiện nghiệm thu số 12: *"Màn Khảo sát chỉ
nghiệm thu field mapping sau khi có seed data"*.

⇒ **Dev làm đúng chữ BA: để nguyên.** Ghi nhận để BA biết mức độ lệch: nhóm này có **21 chỗ
dùng thẻ nhưng 11 kiểu thẻ khác nhau**, bo góc chạy từ 12 đến 24 — là chỗ lệch nặng nhất toàn
Portal. Khi nào BA có dữ liệu mẫu, báo Dev để xếp lịch làm gọn một lượt.

## 2. Thẻ "Tổng công nợ" giữ nguyên chiều cao 142

Bảng thành phần ghi *"không đặt fixed height"*. Nhưng thẻ này dựng ở **Sprint 43 theo đúng bản
vẽ Figma của BA**, kích thước **359 × 142**, và đang có một bài kiểm thử tự động canh giữ.

⇒ **Dev giữ 142**, theo đúng nguyên tắc đã áp cho cả cụm trước: **bản vẽ cụ thể BA đã duyệt thì
thắng quy tắc chung**; chỗ nào là lệch chuẩn thì cho về chuẩn, chỗ nào là thiết kế có chủ đích
thì giữ. Nếu BA muốn thẻ này co giãn theo nội dung thì báo — sửa mất một dòng, nhưng khi đó nó
sẽ **lệch bản vẽ Figma Sprint 43**.

## 3. Màn đăng nhập giữ nguyên dáng

`wj-auth-card` có khoảng đệm `69/48/44` và có đổ bóng, khác con số BA chốt. Đây là bản dựng theo
Figma đã duyệt ở **Sprint 39** ⇒ **thiết kế có chủ đích**, không phải lệch chuẩn. Thêm nữa, cột
phạm vi của BA cho SurfaceCard liệt kê **14 đường dẫn và không có màn đăng nhập**. ⇒ **Giữ nguyên.**

## 4. Thẻ bộ lọc + Thẻ đầu trang *Thông tin cửa hàng* — **làm được phần khung ngay**

Hai chỗ này đang treo ở issue *trước* (`UI-CARDHEADER-001`, câu (a)/(d)/(e)). Rà lại thì thấy:
**các câu đó chỉ hỏi về dòng tiêu đề và khối bên phải**, không hỏi gì về khung thẻ.

⇒ Dev **tách đôi**: phần **khung** (bo góc, viền, khoảng đệm, khoảng cách giữa các thẻ) làm luôn
ở đợt này; phần **tiêu đề / khối bên phải** vẫn chờ BA trả lời câu (a)/(d)/(e) như cũ. Nhờ vậy
**27 chỗ** không phải nằm chờ.

---

## Một điều đáng mừng cho BA

**Hai trong ba mã màu BA chốt đã có sẵn tên trong hệ thống** — `#EEF2F5` và `#E5E7EB` đều đã là
màu chuẩn từ trước. Chỉ `#F8FAFC` (nền vùng phụ) là phải đặt tên mới. Nghĩa là bộ số BA đưa **rất
sát với cái hệ thống vốn đã có**, phần việc thật nằm ở **khoảng đệm** (máy tính đang 22–28, BA
chốt 16/20) chứ không phải ở màu.
