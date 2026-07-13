from odoo import fields, models


class WujiaNotificationRead(models.Model):
    """Tracking đã đọc — theo (thông báo + user + cửa hàng hiện tại) theo BA FINAL.

    Thông báo là global nhưng trạng thái đọc riêng từng tài khoản tại từng cửa hàng:
    1 user ở 2 cửa hàng đọc độc lập. Đếm unread = effective_count − read_count(user, store)."""

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
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng',
        index=True, ondelete='cascade',
    )
    read_date = fields.Datetime(
        string='Đọc lần đầu', default=fields.Datetime.now, required=True,
    )
    last_open_date = fields.Datetime(string='Mở gần nhất')

    _uniq_noti_user_store = models.Constraint(
        'unique(notification_id, user_id, franchise_id)',
        'Mỗi user chỉ ghi nhận đọc 1 lần / thông báo / cửa hàng.',
    )
