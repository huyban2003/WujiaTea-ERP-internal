#!/usr/bin/env python3
"""Ghi chú bổ sung cột L phần F — luồng chọn đối tượng nhận thông báo.

Chủ dự án chốt 31/07/2026: giữ franchise_ids, thêm target_mode (all/filter/manual),
mặc định `all` = gửi toàn hệ thống; chế độ `filter` chọn theo khu vực/tỉnh/trạng thái
thay vì tick từng cửa hàng; danh sách nhận chốt tại thời điểm publish.

CHỈ ghi cột L (ô trống, ngoài bảng A..K). KHÔNG sửa chữ của BA, KHÔNG chèn dòng.
Có guard: mỗi ô kiểm tra text mỏ neo ở cột A/B trước khi ghi -> lệch dòng thì dừng.

    python3 spec_f_targeting_note.py            # dry-run
    python3 spec_f_targeting_note.py --apply
"""
import sys

import sheet_io

TAB = "1. Model/ Field"
C_NOTE = 11  # cột L

# row1 -> (cột kiểm tra 0-based, mỏ neo phải khớp prefix, nội dung ghi)
NOTES = {
    741: (0, 'Phạm vi MVP đã chốt',
          'Bổ sung 31/07/2026 — chủ dự án chốt luồng chọn đối tượng nhận. '
          'Ghi chú bổ sung, không sửa nội dung cột bên trái.'),
    742: (1, 'Thông báo áp dụng global',
          'Có chọn đối tượng nhận. Field target_mode trên wujia.notification: '
          'all = Tất cả cửa hàng (mặc định) / filter = Theo tiêu chí / manual = Chọn tay. '
          'Không chọn gì = gửi toàn hệ thống, giữ đúng hành vi MVP hiện tại.'),
    743: (1, 'Admin/HQ tạo, sửa, publish',
          'Chế độ filter chọn theo target_area_ids (res.area), target_state_ids '
          '(res.country.state), target_status (mặc định Đang hoạt động), trừ '
          'target_exclude_franchise_ids. Không phải tick từng cửa hàng.'),
    744: (1, 'Trạng thái đọc tách theo từng announcement',
          'Nút "Xem trước danh sách nhận": hiện số cửa hàng khớp tiêu chí trước khi publish.'),
    745: (1, 'PC có bell popup',
          'Danh sách nhận chốt tại thời điểm publish: hệ thống dịch tiêu chí thành danh sách '
          'cửa hàng và lưu vào franchise_ids. Cửa hàng mở sau ngày publish không nhận thông báo '
          'cũ; HQ dùng nút "Cập nhật danh sách nhận" nếu muốn bổ sung.'),
    746: (1, 'Thông báo hết hạn vẫn nằm trong lịch sử',
          'Ràng buộc: filter phải có tối thiểu 1 tiêu chí; nếu lọc ra 0 cửa hàng thì chặn '
          'publish. all không ghi dòng franchise_ids nào (rỗng = broadcast).'),
    762: (1, 'recipient_count',
          'Bổ sung 31/07/2026: khi target_mode khác all, recipient_count đếm theo danh sách '
          'cửa hàng nhận đã chốt, không phải toàn hệ thống.'),
    816: (1, 'MVP global cho toàn bộ portal account',
          'Bổ sung 31/07/2026 — xem ghi chú dòng 742-746: đã chốt có target theo cửa hàng/'
          'khu vực. Vẫn không thêm target_role, target_user_ids.'),
    863: (0, 'recipient_count',
          'Bổ sung 31/07/2026: phạm vi đếm là danh sách cửa hàng nhận (xem dòng 745), '
          'không phải global khi target_mode khác all.'),
    872: (0, 'Announcement là global',
          'Bổ sung 31/07/2026: wujia.notification có franchise_ids (Cửa hàng nhận, M2M) — '
          'rỗng = gửi toàn hệ thống. current_store_id vẫn chỉ dùng cho membership và '
          'read-status như mô tả bên trái.'),
}


def main():
    apply = "--apply" in sys.argv
    values = sheet_io.read_values(TAB)  # export?format=csv -> row tuyệt đối
    cell_map, problems = {}, []
    for row1, (anchor_col, anchor, text) in sorted(NOTES.items()):
        row = values[row1 - 1] if row1 - 1 < len(values) else []
        got = row[anchor_col].strip() if len(row) > anchor_col else ''
        if not got.startswith(anchor):
            problems.append(f'  L{row1}: mỏ neo lệch — cần "{anchor}...", thấy "{got[:60]}"')
            continue
        cur = row[C_NOTE].strip() if len(row) > C_NOTE else ''
        if cur:
            problems.append(f'  L{row1}: ô KHÔNG trống ("{cur[:60]}") — bỏ qua để khỏi đè.')
            continue
        cell_map[(row1, C_NOTE)] = text
        print(f'L{row1} <- {text[:90]}...')
    if problems:
        print('\n⚠️  Vấn đề:')
        print('\n'.join(problems))
        print('\nDừng — sửa mỏ neo rồi chạy lại.')
        return 1
    print(f'\n{len(cell_map)} ô sẵn sàng.')
    if apply:
        print('Đã ghi', sheet_io.batch_set(TAB, cell_map), 'ô.')
    else:
        print('Dry-run — thêm --apply để ghi.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
