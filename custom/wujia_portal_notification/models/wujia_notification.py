import re
from html import unescape

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


# BA FINAL (sheet "1. Model Field" wujia.announcement): 3 technical key, nhãn hiển thị
# "Lưu ý / Quan trọng / Cần làm". FE không hardcode label — đọc priority_label backend trả.
PRIORITY_SELECTION = [
    ('normal', 'Lưu ý'),
    ('important', 'Quan trọng'),
    ('urgent', 'Cần làm'),
]
PRIORITY_LABELS = dict(PRIORITY_SELECTION)

# Spec F §3 — vòng đời do HQ điều khiển (expired_date KHÔNG tự đổi state).
STATE_SELECTION = [
    ('draft', 'Nháp'),
    ('published', 'Đã gửi'),
    ('archived', 'Lưu trữ'),
]

# Spec F §4 — ma trận chuyển trạng thái. archived = ngõ cụt trong MVP.
STATE_TRANSITIONS = {
    'draft': ('published', 'archived'),
    'published': ('archived',),
    'archived': (),
}

# Spec F §18 — message nghiệp vụ, không lộ lỗi kỹ thuật.
MSG_PUBLISH_VALIDATION = (
    'Vui lòng nhập đầy đủ tiêu đề, nội dung, loại và mức độ thông báo; '
    'ngày hết hiệu lực không được nhỏ hơn ngày gửi.'
)


class WujiaNotification(models.Model):
    """Thông báo HQ → cửa hàng nhượng quyền. Backend HQ soạn/publish/archive, portal chỉ đọc.

    franchise_ids empty = broadcast cho tất cả cửa hàng đang hoạt động.
    Trạng thái đọc/chưa đọc lưu ở `wujia.notification.read` (table riêng để
    đếm unread nhanh — pattern v14)."""

    # Mapping BA spec phần F (wujia.announcement) → model THẬT (giữ tên source, Sprint 41):
    #   title→name · name (ANN/2026/0001)→code · category_id→type_id · published_date→published_date
    #   (đã rename từ `date`) · wujia.announcement.category→wujia.notification.type.
    # `dispatch_number` = số công văn HQ nhập tay, KHÁC `code` (mã hệ thống auto).
    _name = 'wujia.notification'
    _description = 'Wujia Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'published_date desc, id desc'

    code = fields.Char(
        string='Mã thông báo', copy=False, readonly=True, index=True,
        help='Mã hệ thống tự sinh, ví dụ ANN/2026/0001.',
    )
    name = fields.Char(string='Tiêu đề', required=True, index=True, tracking=True)
    type_id = fields.Many2one(
        'wujia.notification.type', string='Loại',
        index=True, ondelete='restrict', tracking=True,
    )
    dispatch_number = fields.Char(string='Số công văn', copy=False)
    published_date = fields.Datetime(
        string='Ngày gửi', default=fields.Datetime.now,
        index=True, required=True, tracking=True,
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
    state = fields.Selection(
        STATE_SELECTION, string='Trạng thái',
        default='draft', required=True, index=True, copy=False, tracking=True,
    )
    portal_visible = fields.Boolean(
        string='Hiện trên portal', default=True,
        help='Tắt để ẩn khỏi portal mà không cần đổi trạng thái.',
    )
    is_published_portal = fields.Boolean(
        string='Đang hiện trên portal',
        compute='_compute_is_published_portal', store=True, index=True,
        help='active + state = Đã gửi + hiện trên portal. KHÔNG loại thông báo hết hiệu lực '
             'vì lịch sử portal vẫn phải mở được.',
    )
    published_by_id = fields.Many2one(
        'res.users', string='Người gửi', readonly=True, copy=False,
        help='Internal user bấm Gửi thông báo.',
    )
    internal_note = fields.Text(
        string='Ghi chú nội bộ',
        help='Chỉ HQ thấy — không trả ra portal.',
    )
    priority = fields.Selection(
        PRIORITY_SELECTION, string='Mức độ',
        default='normal', required=True, index=True, tracking=True,
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
    summary = fields.Text(
        string='Tóm tắt',
        help='Mô tả ngắn hiển thị ở danh sách/popup. Để trống → portal tự cắt từ nội dung.',
    )
    read_ids = fields.One2many(
        'wujia.notification.read', 'notification_id',
        string='Trạng thái đọc', readonly=True,
    )
    read_count = fields.Integer(
        string='Đã đọc', compute='_compute_read_stats',
        help='Số cặp người dùng/cửa hàng đã đọc thông báo này.',
    )
    recipient_count = fields.Integer(
        string='Người nhận', compute='_compute_read_stats',
        help='Tổng số cặp người dùng/cửa hàng có membership còn hiệu lực.',
    )
    unread_count = fields.Integer(
        string='Chưa đọc', compute='_compute_read_stats',
        help='Bằng 0 khi thông báo đã hết hiệu lực.',
    )
    active = fields.Boolean(string='Active', default=True)

    _uniq_code = models.Constraint(
        'unique(code)',
        'Mã thông báo phải duy nhất.',
    )
    _published_date_required = models.Constraint(
        "CHECK (state != 'published' OR published_date IS NOT NULL)",
        'Thông báo đã gửi phải có ngày gửi.',
    )
    _expired_after_published = models.Constraint(
        'CHECK (expired_date IS NULL OR published_date IS NULL'
        ' OR expired_date >= published_date)',
        'Ngày hết hiệu lực không được nhỏ hơn ngày gửi.',
    )

    # -----------------------------------------------------------------
    # Compute
    # -----------------------------------------------------------------
    @api.depends('expired_date')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_expired = bool(rec.expired_date and rec.expired_date < now)

    @api.depends('priority')
    def _compute_priority_label(self):
        for rec in self:
            rec.priority_label = PRIORITY_LABELS.get(rec.priority, '')

    @api.depends('active', 'state', 'portal_visible')
    def _compute_is_published_portal(self):
        for rec in self:
            rec.is_published_portal = bool(
                rec.active and rec.state == 'published' and rec.portal_visible
            )

    def _compute_read_stats(self):
        """Spec F §15. Perf 1500 user: 2 query cho CẢ recordset, không query/record."""
        read_by_noti = {}
        if self.ids:
            read_by_noti = {
                noti.id: count
                for noti, count in self.env['wujia.notification.read'].sudo()._read_group(
                    [('notification_id', 'in', self.ids)],
                    groupby=['notification_id'], aggregates=['__count'],
                )
            }
        # Thông báo global → recipient_count giống nhau cho mọi record, tính 1 lần.
        recipients = len(self.env['wujia.franchise.member'].sudo()._read_group(
            [('is_currently_valid', '=', True)], groupby=['user_id', 'franchise_id'],
        ))
        for rec in self:
            rec.read_count = read_by_noti.get(rec._origin.id or rec.id, 0)
            rec.recipient_count = recipients
            rec.unread_count = 0 if rec.is_expired else max(
                recipients - rec.read_count, 0
            )

    # -----------------------------------------------------------------
    # Create / write / unlink
    # -----------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'wujia.notification'
                )
            if vals.get('state') == 'published':
                vals.setdefault('published_date', fields.Datetime.now())
                vals.setdefault('published_by_id', self.env.user.id)
        return super().create(vals_list)

    def write(self, vals):
        new_state = vals.get('state')
        if new_state:
            for rec in self:
                if rec.state != new_state and new_state not in STATE_TRANSITIONS[rec.state]:
                    raise UserError(_(
                        'Không thể chuyển thông báo "%(name)s" từ "%(old)s" sang "%(new)s".',
                        name=rec.name,
                        old=dict(STATE_SELECTION)[rec.state],
                        new=dict(STATE_SELECTION)[new_state],
                    ))
            if new_state == 'published':
                vals.setdefault('published_date', fields.Datetime.now())
                vals.setdefault('published_by_id', self.env.user.id)
        return super().write(vals)

    def unlink(self):
        # Spec F §17.2 — không xoá vật lý bản đã gửi, dùng Lưu trữ / bỏ active.
        blocked = self.filtered(lambda r: r.state != 'draft')
        if blocked:
            raise UserError(_(
                'Không thể xoá thông báo đã gửi: %s. Hãy dùng Lưu trữ.',
                ', '.join(blocked.mapped('name')),
            ))
        return super().unlink()

    @api.constrains('state', 'type_id')
    def _check_published_requirements(self):
        for rec in self:
            if rec.state == 'published' and not rec.type_id:
                raise ValidationError(_(MSG_PUBLISH_VALIDATION))

    # -----------------------------------------------------------------
    # Actions (backend HQ)
    # -----------------------------------------------------------------
    def action_publish(self):
        """Spec F §9 — validate rồi mới gửi. Fail → message nghiệp vụ §18."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Chỉ thông báo ở trạng thái Nháp mới gửi được.'))
            if not (rec.name and rec._has_content() and rec.priority):
                raise UserError(_(MSG_PUBLISH_VALIDATION))
            if not rec.type_id or not rec.type_id.active:
                raise UserError(_(MSG_PUBLISH_VALIDATION))
            now = fields.Datetime.now()
            if rec.expired_date and rec.expired_date < now:
                raise UserError(_(MSG_PUBLISH_VALIDATION))
            rec.write({
                'state': 'published',
                'published_date': now,
                'published_by_id': self.env.user.id,
            })
        return True

    def action_archive_notification(self):
        """Lưu trữ — ẩn khỏi portal, giữ lịch sử. Không xoá dữ liệu đọc."""
        for rec in self:
            if rec.state == 'archived':
                continue
            rec.state = 'archived'
        return True

    def action_view_read_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trạng thái đọc'),
            'res_model': 'wujia.notification.read',
            'view_mode': 'list,form',
            'domain': [('notification_id', '=', self.id)],
            'context': {'create': False},
        }

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    def _has_content(self):
        self.ensure_one()
        return bool(self._html_to_text(self.content))

    @staticmethod
    def _html_to_text(html):
        text = re.sub(r'<[^>]+>', ' ', html or '')
        return re.sub(r'\s+', ' ', unescape(text)).strip()

    def get_display_summary(self, length=200):
        """Portal dùng: summary HQ nhập, trống thì cắt an toàn từ content (spec F §2)."""
        self.ensure_one()
        if self.summary:
            return self.summary
        text = self._html_to_text(self.content)
        return text[:length] + ('...' if len(text) > length else '')

    def is_read_by(self, user_id):
        self.ensure_one()
        return bool(self.env['wujia.notification.read'].sudo().search_count([
            ('notification_id', '=', self.id),
            ('user_id', '=', user_id),
        ]))
