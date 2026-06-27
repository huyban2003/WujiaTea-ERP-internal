# -*- coding: utf-8 -*-
"""Seed demo notifications (recent dates) for PC notification UI review.
Local-only (not in manifest). Idempotent by dispatch_number.

Run via odoo shell:
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \
        -c <conf> -d wujia_tea_19 --no-http < scripts/seed_notification_demo.py
"""
import base64
from datetime import timedelta

from odoo import fields  # noqa: F401  (available in shell as `env`)

Noti = env['wujia.notification'].sudo()
Type = env['wujia.notification.type'].sudo()
Read = env['wujia.notification.read'].sudo()
Att = env['ir.attachment'].sudo()

now = fields.Datetime.now()


def ty(code):
    return Type.search([('code', '=', code)], limit=1)


# (days_ago, hour, type_code, priority, dispatch, title, body, read_by_admin, attach)
ROWS = [
    (0, 9, 'URG', 'urgent', 'CV-2606-001',
     'Đơn hàng SO02541 đang chờ xác nhận',
     '<p>Đơn hàng <b>SO02541</b> đã được ghi nhận và đang chờ xác nhận. '
     'Cửa hàng vui lòng kiểm tra sản phẩm, số lượng và thời gian giao dự kiến '
     '<b>trước 16:00 hôm nay</b>.</p>', False, False),
    (1, 10, 'GEN', 'high', 'CV-2606-002',
     'Lịch giao hàng hôm nay đã được cập nhật',
     '<p>Batch <b>GIAO-0624</b> có thay đổi giờ xuất kho. Vui lòng theo dõi mục '
     'Giao hàng để biết khung giờ mới.</p>', False, False),
    (2, 8, 'URG', 'urgent', 'CV-2606-003',
     'Công nợ kỳ 06/2026 cần thanh toán trước 30/06',
     '<p>Số tiền còn phải trả: <b>8.450.000đ</b>. Đề nghị cửa hàng hoàn tất '
     'thanh toán trước hạn để tránh gián đoạn cấp hàng.</p>', False, True),
    (3, 14, 'OTH', 'normal', 'CV-2606-004',
     'Tài liệu vận hành mới đã được phát hành',
     '<p>Quy trình <b>bảo quản nguyên liệu lạnh</b> đã được cập nhật. '
     'Xem chi tiết trong tài liệu đính kèm.</p>', False, True),
    (4, 11, 'GEN', 'normal', 'CV-2606-005',
     'Ticket HT-0241 đã có phản hồi từ HQ',
     '<p>Ngô Gia đã phản hồi yêu cầu hỗ trợ của cửa hàng. Vui lòng kiểm tra '
     'mục Hỗ trợ.</p>', True, False),
    (5, 9, 'PROMO', 'high', 'CV-2606-006',
     'Chương trình ưu đãi nguyên liệu tháng 06',
     '<p>Áp dụng cho nhóm sản phẩm <b>trà và topping</b> trong kỳ. '
     'Xem điều kiện áp dụng tại mục Khuyến mãi.</p>', True, False),
    (6, 16, 'SYS', 'normal', 'CV-2606-007',
     'Cập nhật quy định nhận hàng tại kho',
     '<p>Cửa hàng kiểm tra số lượng và ký nhận ngay khi nhận hàng để đối soát '
     'chính xác.</p>', True, False),
    (8, 2, 'SYS', 'low', 'CV-2606-008',
     'Bảo trì hệ thống đặt hàng 02:00–03:00 ngày 20/06',
     '<p>Hệ thống tạm ngưng đặt hàng trong khung giờ bảo trì. '
     'Mong cửa hàng thông cảm.</p>', False, False),
    (10, 10, 'PROMO', 'normal', 'CV-2606-009',
     'Triển khai Zalo Mini App cho cửa hàng',
     '<p>Cửa hàng có thể tra cứu đơn và thông báo ngay trên <b>Zalo Mini App</b>. '
     'Hướng dẫn chi tiết đính kèm.</p>', False, False),
]

created = 0
admin = env.ref('base.user_admin')
for days, hour, code, prio, disp, title, body, read_admin, attach in ROWS:
    if Noti.search_count([('dispatch_number', '=', disp)]):
        continue
    t = ty(code)
    date = (now - timedelta(days=days)).replace(hour=hour, minute=15, second=0, microsecond=0)
    vals = {
        'name': title,
        'type_id': t.id if t else False,
        'dispatch_number': disp,
        'date': date,
        'content': body,
        'priority': prio,
        'published': True,
        'franchise_ids': [(5, 0, 0)],  # broadcast (tất cả cửa hàng)
    }
    noti = Noti.create(vals)
    if attach:
        data = base64.b64encode(("Demo file cho %s" % title).encode('utf-8'))
        a = Att.create({
            'name': 'Chi tiet %s.pdf' % disp,
            'datas': data,
            'mimetype': 'application/pdf',
            'res_model': 'wujia.notification',
            'res_id': noti.id,
        })
        noti.attachment_ids = [(4, a.id)]
    if read_admin and not Read.search_count([
        ('notification_id', '=', noti.id), ('user_id', '=', admin.id)]):
        Read.create({'notification_id': noti.id, 'user_id': admin.id})
    created += 1
    print('[CREATE] %s — %s (%s/%s)' % (disp, title, code, prio))

env.cr.commit()
print('DONE: %d notifications created (recent window).' % created)
print('TOTAL published:', Noti.search_count([('published', '=', True)]))
