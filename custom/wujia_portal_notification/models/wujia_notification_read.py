from odoo import fields, models


class WujiaNotificationRead(models.Model):
    """Bảng tracking user đã đọc thông báo nào — pattern v14.

    Đếm unread = published_count - read_count(user) — query nhanh, dùng index."""

    _name = 'wujia.notification.read'
    _description = 'Wujia Notification Read Tracking'
    _order = 'read_date desc'

    notification_id = fields.Many2one(
        'wujia.notification', string='Thông báo',
        required=True, ondelete='cascade', index=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Người đọc',
        required=True, index=True, ondelete='cascade',
    )
    read_date = fields.Datetime(
        string='Đọc lúc', default=fields.Datetime.now, required=True,
    )

    _sql_constraints = [
        ('uniq_noti_user', 'unique(notification_id, user_id)',
         'Mỗi user chỉ ghi nhận đọc 1 lần / thông báo.'),
    ]
