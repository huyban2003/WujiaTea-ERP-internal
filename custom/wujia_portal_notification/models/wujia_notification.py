from odoo import api, fields, models


# BA FINAL (sheet "1. Model Field" wujia.announcement): 3 technical key, nhãn hiển thị
# "Lưu ý / Quan trọng / Cần làm". FE không hardcode label — đọc priority_label backend trả.
PRIORITY_SELECTION = [
    ('normal', 'Lưu ý'),
    ('important', 'Quan trọng'),
    ('urgent', 'Cần làm'),
]
PRIORITY_LABELS = dict(PRIORITY_SELECTION)


class WujiaNotification(models.Model):
    """Skeleton — thông báo HQ → cửa hàng nhượng quyền.

    franchise_ids empty = broadcast cho tất cả cửa hàng đang hoạt động.
    Trạng thái đọc/chưa đọc lưu ở `wujia.notification.read` (table riêng để
    đếm unread nhanh — pattern v14)."""

    # Mapping BA (wujia.announcement) → model thật: title←name, mã thông báo←dispatch_number,
    # publish_date/published_date←date, category_id←type_id. "state=published + portal_visible"
    # ⟺ published=True; "thu hồi" ⟺ published=False (ẩn hẳn); "hết hiệu lực" ⟺ published + expired.
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
    expired_date = fields.Datetime(
        string='Hết hiệu lực', index=True,
        help='Trống = không hết hạn. Sau thời điểm này: ẩn khỏi popup/badge, còn ở lịch sử.',
    )
    is_expired = fields.Boolean(
        string='Đã hết hiệu lực', compute='_compute_is_expired',
    )
    priority_label = fields.Char(
        string='Nhãn ưu tiên', compute='_compute_priority_label',
    )
    summary = fields.Char(string='Tóm tắt', size=200, compute='_compute_summary', store=True)

    @api.depends('expired_date')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_expired = bool(rec.expired_date and rec.expired_date < now)

    @api.depends('priority')
    def _compute_priority_label(self):
        for rec in self:
            rec.priority_label = PRIORITY_LABELS.get(rec.priority, '')

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
