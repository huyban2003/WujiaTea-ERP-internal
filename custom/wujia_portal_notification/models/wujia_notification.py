from odoo import api, fields, models


PRIORITY_SELECTION = [
    ('low', 'Thấp'),
    ('normal', 'Bình thường'),
    ('high', 'Cao'),
    ('urgent', 'Khẩn cấp'),
]


class WujiaNotification(models.Model):
    """Skeleton — thông báo HQ → cửa hàng nhượng quyền.

    franchise_ids empty = broadcast cho tất cả cửa hàng đang hoạt động.
    Trạng thái đọc/chưa đọc lưu ở `wujia.notification.read` (table riêng để
    đếm unread nhanh — pattern v14)."""

    _name = 'wujia.notification'
    _description = 'Wujia Notification'
    _order = 'date desc, id desc'

    name = fields.Char(string='Tiêu đề', required=True, index=True)
    type_id = fields.Many2one(
        'wujia.notification.type', string='Loại',
        index=True, ondelete='restrict',
    )
    dispatch_number = fields.Char(string='Số công văn', copy=False)
    date = fields.Datetime(
        string='Ngày phát hành', default=fields.Datetime.now,
        index=True, required=True,
    )
    content = fields.Html(string='Nội dung', sanitize=True, translate=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'wujia_notification_attachment_rel',
        'notification_id', 'attachment_id',
        string='File đính kèm',
    )
    franchise_ids = fields.Many2many(
        'wujia.franchise.management',
        'wujia_notification_franchise_rel',
        'notification_id', 'franchise_id',
        string='Cửa hàng nhận',
        help='Để trống = broadcast cho mọi cửa hàng.',
    )
    published = fields.Boolean(string='Đã phát hành', default=False, index=True)
    priority = fields.Selection(
        PRIORITY_SELECTION, string='Mức độ',
        default='normal', required=True, index=True,
    )
    is_pinned = fields.Boolean(string='Ghim trên cùng', default=False)
    pin_expiry_date = fields.Datetime(string='Ghim đến')
    summary = fields.Char(string='Tóm tắt', size=200, compute='_compute_summary', store=True)

    @api.depends('content')
    def _compute_summary(self):
        for rec in self:
            text = (rec.content or '')
            # Strip HTML tags simple
            from html import unescape
            import re
            text = re.sub(r'<[^>]+>', ' ', text)
            text = unescape(text)
            text = re.sub(r'\s+', ' ', text).strip()
            rec.summary = text[:200] + ('...' if len(text) > 200 else '')

    def is_read_by(self, user_id):
        self.ensure_one()
        return bool(self.env['wujia.notification.read'].sudo().search_count([
            ('notification_id', '=', self.id),
            ('user_id', '=', user_id),
        ]))
