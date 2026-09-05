#!/usr/bin/env python3
"""Viết lại Tasks!P3 + Q3 (Sprint 41) bằng tiếng Việt CÓ DẤU — dev-only.

Giữ nguyên toàn bộ thông tin kỹ thuật cũ, chỉ khôi phục dấu + sửa 3 số liệu sai so với
UAT (nhóm quyền Administrator, menu Franchise Management, 30 bản ghi là môi trường build)
+ cập nhật kết quả đã deploy và đã đồng bộ tên trên sheet.

    python3 task_s41_rewrite.py [--apply]
"""
import sys

import sheet_io

TAB, ROW = "Tasks", 3
C_QUESTION, C_RESULT, C_DATE = 15, 16, 17  # P, Q, R

P3 = (
    "ĐÃ CHỐT (31/07/2026) — theo BA: mức độ 'normal' = \"Thông thường\" như đặc tả phần F mục 5 "
    "(dòng 782), giữ nguyên đặc tả. Hiện code và portal đang hiển thị \"Lưu ý\" (theo BA FINAL "
    "Sprint 32). Vì task này BA cấm đụng UI Portal nên sprint 41 chưa đổi; đã TÁCH TASK RIÊNG để "
    "đổi nhãn ở 5 chỗ đang viết cứng (model, controller portal, view portal, JS badge chuông). "
    "Lưu ý kỹ thuật: KHÔNG cần migration — 'normal' là giá trị lưu trong database, \"Lưu ý\" chỉ "
    "là nhãn hiển thị, đổi nhãn không đụng dữ liệu."
)

Q3 = """BUILD: upgrade -u wujia_portal_notification,wujia_portal_base RC=0 (94 module, 0 ERROR/Traceback). TEST: 19 unit test — 0 failed, 0 error. MIGRATE: migration 19.0.2.0.0 chạy sạch trên môi trường build (30 bản ghi thông báo, 30/30 có published_date + mã duy nhất ANN/2026/0001..0030), không mất dữ liệu. PUSH: đã push origin/main — commit b5816c0 (code) + 7677f97 (docs chương 54).

DEPLOY: ĐÃ DEPLOY UAT http://113.161.187.126:8019/ (database wujia_tea_19). Đã smoke-test lại bằng cách đọc dữ liệu, không tạo/sửa gì: module wujia_portal_notification bản 19.0.2.0.0 đã cài; field cũ 'published' và 'date' đã biến mất, toàn bộ field mới có đủ; 15/15 bản ghi trên UAT đều có code và published_date; menu và nhóm quyền đã lên đúng; portal /portal/notification, /portal và popup chuông vẫn chạy bình thường (migration không phá portal).

ĐÃ LÀM (đặc tả phần F):
1. Vòng đời draft → published → archived: field state + statusbar, nút "Gửi thông báo"/"Lưu trữ", chặn published→draft và archived→* trong write(), chặn xóa vật lý bản đã gửi trong unlink().
2. Kiểm tra khi gửi (phần F mục 8/9): thiếu tiêu đề / nội dung / loại / mức độ, hoặc expired_date < published_date thì chặn đúng thông báo lỗi BA yêu cầu. Thêm CHECK constraint ở tầng database.
3. Hiển thị portal: field mới portal_visible (HQ tắt/bật) + is_published_portal (compute, store + index) = active AND state=published AND portal_visible. ir.rule portal chuyển sang dùng field này.
4. Mã thông báo: field mới code, tự sinh bằng ir.sequence dạng ANN/<năm>/<số>, chỉ đọc + duy nhất. dispatch_number giữ nguyên là số công văn HQ nhập tay.
5. Quản lý loại thông báo (phần F mục 6): thêm description + đếm số thông báo theo loại, menu Cấu hình ▸ Loại thông báo (chỉ Administrator).
6. File đính kèm: tab riêng trên form (many2many_binary).
7. Thống kê đọc (phần F mục 15): read_count / recipient_count / unread_count + tab "Trạng thái đọc" liệt kê ai đã đọc. Tính gộp bằng _read_group (2 query cho cả danh sách) và ẩn khỏi list mặc định để không sinh N query khi HQ mở danh sách 1500 user.
8. Phân quyền (phần F mục 16/17): privilege "Wujia Notification" + 2 nhóm — "User" (chỉ xem) và "Administrator" (tạo/sửa/gửi/lưu trữ). Portal user vẫn chỉ đọc, đã có test chặn create/write.
9. Menu backend mới: Franchise Management ▸ Thông báo (trước đây HQ không có màn hình nào để soạn thông báo).
10. Chatter (mail.thread) để truy vết ai sửa gì.

>>> ĐÃ ĐỒNG BỘ TÊN TRÊN SHEET (31/07/2026). Đặc tả phần F đặt tên model/field khác source đang chạy thật; đã giữ nguyên tên source (không rename code) vì module đang chạy thật với dữ liệu live + portal 1500 user, và đã sửa thẳng tên trong đặc tả phần F (53 ô) cùng tab "3. Controller" (5 ô: E12, E42, E43, E44, E45) cho khớp. Bảng đối chiếu:
| Đặc tả F ghi | Source thật |
| wujia.announcement | wujia.notification |
| wujia.announcement.category | wujia.notification.type |
| wujia.announcement.read | wujia.notification.read |
| title | name |
| name (ANN/2026/0001) | code (field mới thêm sprint này) |
| category_id | type_id |
| announcement_id | notification_id |
| announcement_count | notification_count |
| publish_date | tên cũ thật là date, đã rename thành published_date |
Chỉ đổi TÊN, không sửa một câu nghiệp vụ nào của BA.

BA CẦN BIẾT (3 ý):
1. Dev có lỡ ghi một cột ghi chú vào phần F nói đặc tả của BA mâu thuẫn — SAI, đã xoá sạch. Đặc tả của BA nhất quán; chỗ lệch nằm ở source của Dev, Dev tự sửa.
2. Nhờ BA cập nhật ô J3 (Acceptance) theo bảng đối chiếu tên ở trên — Dev không tự sửa ô của BA.
3. Phần BA để trống và đã hỏi ở ô G3: menu backend là "Franchise Management ▸ Thông báo" (cấu hình: ▸ Cấu hình ▸ Loại thông báo); nhóm quyền là privilege "Wujia Notification" gồm "User" (chỉ xem) và "Administrator" (toàn quyền).

CÂU HỎI CHO BA: ô H12 (CT-011) và H42 (CT-041) tab "3. Controller" ghi "đúng đối tượng (nhận)". Nên hiểu là (a) chỉ trả thông báo cho user có membership hợp lệ tại cửa hàng hiện tại, hay (b) thật sự gửi theo cửa hàng? Hỏi trước vì task controller Notification chưa bắt đầu, trả lời sớm thì đỡ phải làm lại.

Ngoài lề (Dev tự xử lý, BA không cần làm gì): tuân thủ đủ out-of-scope — không đụng Controller/API, không đụng UI Portal, không thêm target_role/target_user_ids. Portal đã smoke-test lại (danh sách, chi tiết, popup chuông, badge, mark-read, tải file) — không đổi."""


def main():
    v = sheet_io.read_values(TAB)
    row = v[ROW - 1]
    assert "thông báo nhượng quyền" in row[3].lower(), f"Row {ROW} không phải task S41 -> DỪNG"
    print(f"row {ROW} = {row[3][:70]!r}  ✓")
    print(f"\nP3: {len(P3)} ký tự\nQ3: {len(Q3)} ký tự")
    if "--apply" not in sys.argv:
        print("\n(dry-run — chạy lại với --apply để ghi)")
        return
    n = sheet_io.batch_set(TAB, {
        (ROW, C_QUESTION): P3,
        (ROW, C_RESULT): Q3,
        (ROW, C_DATE): "31/07/2026",
    })
    print(f"\n✅ đã ghi {n} ô (P3, Q3, R3).")


if __name__ == "__main__":
    main()
