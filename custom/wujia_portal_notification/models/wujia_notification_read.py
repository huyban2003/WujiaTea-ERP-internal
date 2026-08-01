from odoo import fields, models


class WujiaNotificationRead(models.Model):
    """Tracking đã đọc — theo (thông báo + user + cửa hàng hiện tại) theo BA FINAL.

    Thông báo là global nhưng trạng thái đọc riêng từng tài khoản tại từng cửa hàng:
    1 user ở 2 cửa hàng đọc độc lập. Đếm unread = effective_count − read_count(user, store)."""

    _name = 'wujia.notification.read'
    _description = 'Wujia Notification Read Tracking'
    _order = 'read_date desc'

    notification_id = fields.Many2one(
        'wujia.notification', string='Notification',
        required=True, ondelete='cascade', index=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Reader',
        required=True, index=True, ondelete='cascade',
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Store',
        index=True, ondelete='cascade',
    )
    member_id = fields.Many2one(
        'wujia.franchise.member', string='Membership',
        index=True, ondelete='set null',
        help='Membership snapshot at the store when the read was recorded (spec F §7).',
    )
    read_date = fields.Datetime(
        string='First read', default=fields.Datetime.now, required=True,
    )
    last_open_date = fields.Datetime(string='Last opened')

    _uniq_noti_user_store = models.Constraint(
        'unique(notification_id, user_id, franchise_id)',
        'Mỗi user chỉ ghi nhận đọc 1 lần / thông báo / cửa hàng.',
    )
    # unique() coi mọi NULL là khác nhau → session chưa chọn cửa hàng vẫn tạo được row trùng.
    # Partial index bịt nốt nhánh đó (spec F §8.9 — mark-read phải idempotent).
    _uniq_noti_user_no_store = models.UniqueIndex(
        '(notification_id, user_id) WHERE franchise_id IS NULL',
        'Mỗi user chỉ ghi nhận đọc 1 lần / thông báo khi chưa chọn cửa hàng.',
    )
