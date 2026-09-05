#!/usr/bin/env python3
"""Đồng bộ tên model/field phần F (tab `1. Model Field`) theo source Sprint 41 — dev-only.

Phạm vi CHỐT với user (31/07/2026):
  1. CHỈ đổi TÊN model/field. KHÔNG sửa một mệnh đề nghiệp vụ nào của BA.
  2. Chỗ spec F sai/mâu thuẫn -> KHÔNG tự sửa, chỉ ghi chú vào CỘT L (rỗng hoàn toàn
     trong F, nên không đẩy dòng, link `A731:K896` của BA vẫn đúng), tiếng Việt CÓ DẤU,
     nêu rõ xung đột với controller nào để BA sửa spec trước.
  3. KHÔNG đụng source code trong lượt này.

Đọc bằng export?format=csv&gid= (BỎ QUA filter -> row tuyệt đối khớp bridge ghi).

    python3 spec_f_sync.py            # dry-run
    python3 spec_f_sync.py --apply
"""
import sys

import sheet_io

TAB = "1. Model/ Field"  # tên THẬT (có `/`); xlsx export sanitize thành "1. Model Field"
F_FROM, F_TO = 731, 895
C_NOTE = 11  # cột L (0-based)

# ---------------------------------------------------------------- 1. đổi TÊN
# Thay trên mọi ô A..K trong phần F. Dài trước ngắn sau để không nuốt chuỗi.
GLOBAL = [
    ("wujia.announcement.category", "wujia.notification.type"),
    ("wujia.announcement.read", "wujia.notification.read"),
    ("wujia.announcement", "wujia.notification"),
    ("announcement_count", "notification_count"),
    ("announcement_id", "notification_id"),
    ("category_id", "type_id"),
]

# Ô phải sửa tay: (row, col0) -> [(cũ, mới), ...]. Chỉ danh từ kỹ thuật.
EXPLICIT = {
    (734, 3): [("Announcement", "Notification")],
    (735, 3): [("Announcement Category", "Notification Type")],
    (749, 0): [("Announcement Number", "Notification Code")],
    (749, 1): [("name", "code")],
    (750, 1): [("title", "name")],
    (751, 0): [("Category", "Type")],
    (777, 8): [("validate title,", "validate name,")],
    (791, 0): [("Announcement Count", "Notification Count")],
    (795, 0): [("Announcement", "Notification")],
    (803, 1): [("name của announcement", "code của announcement")],
    (804, 1): [("title và content", "name và content")],
    (810, 1): [("publish_date", "date")],
    (820, 3): [("Validate title,", "Validate name,")],
    (821, 3): [("Field publish_date cũ", "Field date cũ")],
    (830, 3): [("Trả title,", "Trả name,")],
    (841, 3): [("Trả title,", "Trả name,")],
}

# ------------------------------------------------- 2. ghi chú cho BA (cột L)
NOTES = {
731: '⚠ ĐỐI CHIẾU SOURCE — do Dev ghi ngày 31/07/2026, sau khi Sprint 41 đã deploy UAT. '
     'Cột này KHÔNG phải đặc tả, chỉ là ghi chú để BA đối chiếu. Tên model/field ở cột A–K '
     'đã được đồng bộ theo code đang chạy thật. Những dòng có ghi chú bên dưới là chỗ spec F '
     'đang mâu thuẫn với chính tài liệu khác của BA hoặc với code đã nghiệm thu — nhờ BA sửa '
     'lại đặc tả trước, Dev sẽ làm tiếp sau khi BA chốt.',

734: 'Đã đổi tên model theo source: wujia.announcement → wujia.notification; '
     'wujia.announcement.category → wujia.notification.type; wujia.announcement.read → '
     'wujia.notification.read. Đây là tên đã chạy thật từ Sprint 32, hiện có 15 bản ghi trên '
     'UAT nên không đổi ngược lại được.',

742: '❗XUNG ĐỘT — nhờ BA sửa. Dòng này ghi "không target theo cửa hàng", nhưng chính tài liệu '
     'của BA lại yêu cầu ngược lại: tab "3. Controller" ô H12 (CT-011 – Lấy thông báo mới nhất): '
     '"Chỉ lấy thông báo còn hiệu lực, đúng đối tượng"; ô H42 (CT-041 – Lấy danh sách thông báo): '
     '"đúng đối tượng nhận"; tab "FEATURE CHECKLIST" ô E31 (POR-024): "Portal hiển thị đúng danh '
     'sách thông báo theo đối tượng nhận". Source đang có field franchise_ids ("Cửa hàng nhận", '
     'Many2many) làm đúng theo CT-011/CT-041, và ir.rule của portal đang lọc bằng field này. '
     'Lưu ý: để TRỐNG franchise_ids nghĩa là gửi toàn hệ thống, nên hành vi mặc định vẫn đúng '
     '"global" như MVP mô tả. Nhờ BA chốt: giữ franchise_ids (Dev bổ sung vào đặc tả) hay bỏ hẳn '
     '(Dev phải sửa CT-011/CT-041, ir.rule portal và view backend — 11 chỗ trong controller).',

749: 'Khác source ở cột Default. Source sinh mã trong create() bằng ir.sequence, KHÔNG dùng '
     'default= như cột I đang ghi. Lý do: field mới vừa có default vừa unique sẽ backfill giá trị '
     'trùng nhau cho các bản ghi cũ rồi vỡ constraint ngay khi cập nhật. Thực tế trên UAT: 15/15 '
     'bản ghi đều có mã, dạng ANN/2026/0001. Nhãn hiển thị ở backend: "Mã thông báo".',

750: 'Field đổi tên title → name (nhãn backend: "Tiêu đề"). Lý do bắt buộc: Odoo dùng field tên '
     '"name" làm display name của bản ghi; nếu đặt là "title" thì mọi chỗ trỏ tới thông báo sẽ '
     'hiển thị trống.',

751: 'Field đổi tên category_id → type_id, trỏ tới model wujia.notification.type (nhãn backend: '
     '"Loại").',

753: '⚠ Spec F đang tự mâu thuẫn — nhờ BA chốt. Dòng này ghi content Required = Yes, nhưng mục 9 '
     '(dòng 819) lại ghi "HQ có thể lưu draft tại backend". Không thể vừa bắt buộc ở tầng field '
     'vừa lưu được bản nháp còn trống. Source hiện làm: không bắt buộc ở tầng field, chỉ kiểm tra '
     'khi bấm Gửi — đúng như thông báo lỗi ở dòng 895. Nếu BA giữ Required = Yes thì HQ sẽ không '
     'lưu nháp được nữa.',

765: 'Khác source — nhờ BA xác nhận. Spec ghi Required = Conditional, Default = Empty; source đang '
     'để bắt buộc + mặc định là thời điểm hiện tại. Lý do: danh sách backend sắp xếp theo '
     'published_date, để trống thì bản nháp sẽ nhảy loạn thứ tự. Trên UAT 15/15 bản ghi đều có '
     'published_date. Nếu BA giữ nguyên đặc tả, Dev tách task sửa lại (có ảnh hưởng thứ tự sắp xếp).',

769: 'Field CÓ trong source nhưng CHƯA có dòng trong đặc tả — nhờ BA bổ sung: dispatch_number '
     '("Số công văn", HQ nhập tay, khác với code là mã hệ thống sinh tự động); franchise_ids '
     '("Cửa hàng nhận", Many2many, để trống = gửi toàn hệ thống — xem ghi chú dòng 742); '
     'pin_expiry_date ("Ghim đến", tự hết ghim khi tới hạn); priority_label (compute, để giao diện '
     'lấy nhãn mức độ từ backend thay vì tự viết cứng).',

788: 'Khác source — nhờ BA xác nhận. Spec ghi code Required = No; source đang bắt buộc + unique. '
     'Lý do: portal trả type_code cho giao diện dùng để chọn màu/tag loại thông báo, để trống thì '
     'giao diện không map được. Nếu BA giữ "No", Dev tách task bỏ bắt buộc.',

792: 'Field CÓ trong source nhưng CHƯA có dòng trong đặc tả — nhờ BA bổ sung: bg_color, text_color, '
     'icon (dùng để vẽ tag loại thông báo trên portal).',

795: 'Field đổi tên announcement_id → notification_id, trỏ tới model wujia.notification.',

796: '❗XUNG ĐỘT — nhờ BA sửa. Spec ghi franchise_id Required = Yes, và mục 18 (dòng 884) đã có sẵn '
     'thông báo lỗi "Vui lòng chọn cửa hàng trước khi thao tác". Nhưng CT-043 (đánh dấu đã đọc) và '
     'CT-044 (đánh dấu tất cả) hiện vẫn cho thao tác khi user chưa chọn cửa hàng và ghi '
     'franchise_id rỗng — trên UAT đang có 6/9 bản ghi rỗng. Làm đúng theo đặc tả thì phải CHẶN và '
     'trả về đúng thông báo ở dòng 884. Nhờ BA xác nhận chặn; Dev sẽ tách 2 bước: (1) chặn ở '
     'controller và trả thông báo lỗi; (2) xử lý 6 bản ghi cũ rồi mới đặt bắt buộc.',

810: 'Tên field cũ trong code thật là "date", không phải "publish_date" (đã sửa lại ở cột B cho '
     'khớp). Đã rename date → published_date bằng migration 19.0.2.0.0, chạy sạch trên UAT. Riêng '
     'key JSON trả cho portal vẫn giữ tên "date" để không phải sửa phần JS đang chạy.',

811: 'Ghi chú kỹ thuật. Ràng buộc unique(notification_id, user_id, franchise_id) KHÔNG chặn được ở '
     'nhánh franchise_id rỗng, vì Postgres coi mọi giá trị rỗng là khác nhau — vẫn tạo được bản ghi '
     'trùng. Source đang bịt bằng một partial unique index riêng cho nhánh rỗng. Nếu BA chốt bắt '
     'buộc phải chọn cửa hàng (xem ghi chú dòng 796) thì gỡ index này đi được.',

816: 'Xem ghi chú dòng 742. Dòng này chỉ cấm THÊM target_store_ids / target_role / target_user_ids '
     '— source không có 3 field đó. franchise_ids là chuyện khác, có từ Sprint 32 và sinh ra để '
     'phục vụ CT-011 / CT-041.',

821: 'Đã thực hiện. Tên field cũ là "date", đã migrate/rename sang published_date ở phiên bản '
     '19.0.2.0.0. Hiện trong code chỉ còn duy nhất published_date.',

866: 'Bổ sung phần BA còn để trống (BA đã hỏi ở tab Tasks ô G3). Vị trí menu backend thật: '
     '"Franchise Management ▸ Thông báo"; cấu hình loại thông báo: "Franchise Management ▸ Cấu hình '
     '▸ Loại thông báo" (chỉ nhóm Administrator nhìn thấy).',

871: 'Tên nhóm quyền thật: privilege "Wujia Notification" gồm 2 nhóm — "User" (chỉ xem) và '
     '"Administrator" (tạo/sửa/gửi/lưu trữ và cấu hình loại thông báo).',

872: '❗XUNG ĐỘT — nhờ BA sửa. Câu "không có franchise_id trên wujia.notification" hiện SAI so với '
     'code đang chạy: model có field franchise_ids ("Cửa hàng nhận", Many2many). Nó tồn tại vì '
     'chính CT-011 (ô H12) và CT-041 (ô H42) của BA yêu cầu "đúng đối tượng nhận", và POR-024 '
     '(FEATURE CHECKLIST ô E31) nghiệm thu theo đúng yêu cầu đó. Nhờ BA sửa lại câu này cho khớp; '
     'hoặc nếu chốt bỏ targeting thì Dev tách task gỡ (ảnh hưởng ir.rule portal, 11 chỗ trong '
     'controller và view backend).',
}


def build():
    values = sheet_io.read_values(TAB)
    # Chốt chặn lệch dòng trước khi làm bất cứ việc gì.
    assert values[F_FROM - 1][0].strip().startswith("F. Quản lý thông báo"), \
        f"Row {F_FROM} không phải đầu phần F -> DỪNG"
    assert values[897 - 1][0].strip().startswith("G."), "Row 897 không phải đầu phần G -> DỪNG"

    cell_map, diffs = {}, []
    for r in range(F_FROM, F_TO + 1):
        row = values[r - 1] if r - 1 < len(values) else []
        for c in range(0, 11):  # A..K
            old = row[c] if c < len(row) else ""
            if not old.strip():
                continue
            new = old
            for a, b in EXPLICIT.get((r, c), []):
                new = new.replace(a, b)
            for a, b in GLOBAL:
                new = new.replace(a, b)
            if new != old:
                cell_map[(r, c)] = new
                diffs.append((r, sheet_io.col_letter(c), old, new))

    for r, note in NOTES.items():
        cur = values[r - 1][C_NOTE] if r - 1 < len(values) and C_NOTE < len(values[r - 1]) else ""
        assert not cur.strip(), f"L{r} KHÔNG rỗng ({cur[:40]!r}) -> DỪNG, không ghi đè"
        cell_map[(r, C_NOTE)] = note
    return cell_map, diffs


def main():
    cell_map, diffs = build()
    print(f"=== ĐỔI TÊN: {len(diffs)} ô ===")
    for r, cl, old, new in diffs:
        print(f"{cl}{r}\n   cũ : {old}\n   mới: {new}")
    print(f"\n=== GHI CHÚ CỘT L: {len(NOTES)} ô (đều đang rỗng) ===")
    for r in sorted(NOTES):
        print(f"L{r}: {NOTES[r][:110]}…")
    print(f"\nTổng {len(cell_map)} ô.")

    if "--apply" not in sys.argv:
        print("\n(dry-run — chạy lại với --apply để ghi)")
        return
    n = sheet_io.batch_set(TAB, cell_map)
    print(f"\n✅ đã ghi {n} ô.")


if __name__ == "__main__":
    main()
