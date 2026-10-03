from odoo import api, fields, models


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

    @api.model
    def _mark_read(self, user, franchise_id, notifications, opened=False, touch=False):
        """Ghi "đã đọc" của user tại cửa hàng cho `notifications` — idempotent, trả số dòng tạo mới.

        opened: người dùng thật sự mở nội dung ⇒ dòng mới có `last_open_date`.
        touch: dòng đã có đổi `last_open_date` (mở lại trang chi tiết), `read_date` giữ nguyên.
        Chưa chọn cửa hàng thì không ghi (spec F §8.11 — tránh row franchise_id NULL).
        """
        if not franchise_id or not notifications:
            return 0
        existing = self.search([
            ('user_id', '=', user.id),
            ('notification_id', 'in', notifications.ids),
            ('franchise_id', '=', franchise_id),
        ])
        now = fields.Datetime.now()
        if touch and existing:
            existing.last_open_date = now
        done = set(existing.mapped('notification_id').ids)
        vals = [
            dict({'notification_id': nid, 'user_id': user.id,
                  'franchise_id': franchise_id, 'read_date': now},
                 **({'last_open_date': now} if opened else {}))
            for nid in notifications.ids if nid not in done
        ]
        if vals:
            self.create(vals)
        return len(vals)
