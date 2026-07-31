import re
from html import unescape

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


# Spec F §5 (sheet "1. Model/ Field"): 3 technical key, nhãn hiển thị
# "Thông thường / Quan trọng / Cần làm". FE không hardcode label — đọc priority_label backend trả.
PRIORITY_SELECTION = [
    ('normal', 'Thông thường'),
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

# Chủ dự án chốt 31/07/2026 — ghi chú bổ sung cột L phần F, dòng 741-746:
# thông báo được chọn đối tượng nhận, mặc định `all` = gửi toàn hệ thống (giữ hành vi MVP).
# Tiêu chí chỉ là CÁCH CHỌN; kết quả luôn được chốt vào `franchise_ids` để portal/ir.rule
# đọc như cũ (không đổi tầng phân quyền, giữ index cho 1500 user).
TARGET_MODE_SELECTION = [
    ('all', 'Tất cả cửa hàng'),
    ('filter', 'Theo tiêu chí'),
    ('manual', 'Chọn tay'),
]

# Spec F §18 — message nghiệp vụ, không lộ lỗi kỹ thuật.
MSG_PUBLISH_VALIDATION = (
    'Vui lòng nhập đầy đủ tiêu đề, nội dung, loại và mức độ thông báo; '
    'ngày hết hiệu lực không được nhỏ hơn ngày gửi.'
)
MSG_TARGET_NO_CRITERIA = (
    'Chọn "Theo tiêu chí" thì phải có ít nhất một tiêu chí: khu vực, tỉnh/thành '
    'hoặc cửa hàng loại trừ.'
)
MSG_TARGET_EMPTY = 'Tiêu chí hiện không khớp cửa hàng nào. Vui lòng chỉnh lại trước khi gửi.'
MSG_TARGET_MANUAL_EMPTY = 'Vui lòng chọn ít nhất một cửa hàng nhận.'
MSG_TARGET_ALL_HAS_STORES = 'Gửi cho "Tất cả cửa hàng" thì không được chọn cửa hàng nhận.'


class WujiaNotification(models.Model):
    """Thông báo HQ → cửa hàng nhượng quyền. Backend HQ soạn/publish/archive, portal chỉ đọc.

    franchise_ids empty = broadcast cho tất cả cửa hàng đang hoạt động; `target_mode`
    quyết định field này được điền thế nào (tất cả / theo tiêu chí / chọn tay).
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
        help='Để trống = broadcast cho mọi cửa hàng. Chế độ "Theo tiêu chí" tự điền field này '
             'khi gửi.',
    )
    target_mode = fields.Selection(
        TARGET_MODE_SELECTION, string='Gửi cho', default='all',
        required=True, tracking=True,
        help='Tất cả = mọi cửa hàng, không cần chọn gì. Theo tiêu chí = lọc theo khu vực/'
             'tỉnh thành/trạng thái. Chọn tay = tự tick từng cửa hàng.',
    )
    target_area_ids = fields.Many2many(
        'res.area', 'wujia_notification_target_area_rel',
        'notification_id', 'area_id', string='Khu vực',
    )
    target_state_ids = fields.Many2many(
        'res.country.state', 'wujia_notification_target_state_rel',
        'notification_id', 'state_id', string='Tỉnh/Thành',
    )
    target_status = fields.Selection(
        [('active', 'Đang hoạt động'), ('any', 'Mọi trạng thái')],
        string='Trạng thái cửa hàng', default='active', required=True,
        help='Mặc định chỉ gửi cho cửa hàng đang hoạt động, bỏ qua nháp/khoá/đóng/hết hạn.',
    )
    target_exclude_franchise_ids = fields.Many2many(
        'wujia.franchise.management', 'wujia_notification_target_exclude_rel',
        'notification_id', 'franchise_id', string='Trừ cửa hàng',
        help='Loại vài cửa hàng cá biệt ra khỏi kết quả lọc.',
    )
    target_preview_count = fields.Integer(
        string='Số cửa hàng khớp', compute='_compute_target_preview_count',
        help='Số cửa hàng sẽ nhận nếu gửi ngay bây giờ.',
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

    @api.depends('target_mode', 'target_status', 'target_area_ids', 'target_state_ids',
                 'target_exclude_franchise_ids', 'franchise_ids')
    def _compute_target_preview_count(self):
        Franchise = self.env['wujia.franchise.management'].sudo()
        total = None
        for rec in self:
            if rec.target_mode == 'manual':
                rec.target_preview_count = len(rec.franchise_ids)
            elif rec.target_mode == 'filter':
                rec.target_preview_count = Franchise.search_count(rec._target_domain())
            else:
                # Broadcast: mọi cửa hàng đều thấy, kể cả không active — đếm 1 lần cho recordset.
                if total is None:
                    total = Franchise.search_count([])
                rec.target_preview_count = total

    def _compute_read_stats(self):
        """Spec F §15 + ghi chú cột L dòng 762/863. Perf 1500 user: 2 query cho CẢ recordset."""
        read_by_noti = {}
        if self.ids:
            read_by_noti = {
                noti.id: count
                for noti, count in self.env['wujia.notification.read'].sudo()._read_group(
                    [('notification_id', 'in', self.ids)],
                    groupby=['notification_id'], aggregates=['__count'],
                )
            }
        # 1 query cho mọi record: cặp (user, cửa hàng) còn hiệu lực, gom theo cửa hàng để
        # thông báo có target đếm được đúng phạm vi của nó.
        pairs = self.env['wujia.franchise.member'].sudo()._read_group(
            [('is_currently_valid', '=', True)], groupby=['franchise_id', 'user_id'],
        )
        per_franchise = {}
        for franchise, _user in pairs:
            per_franchise[franchise.id] = per_franchise.get(franchise.id, 0) + 1
        total = len(pairs)
        for rec in self:
            rec.read_count = read_by_noti.get(rec._origin.id or rec.id, 0)
            # franchise_ids rỗng = broadcast toàn hệ thống; có giá trị = chỉ đếm cửa hàng nhận.
            fids = rec.franchise_ids.ids
            rec.recipient_count = (
                sum(per_franchise.get(fid, 0) for fid in fids) if fids else total
            )
            rec.unread_count = 0 if rec.is_expired else max(
                rec.recipient_count - rec.read_count, 0
            )

    # -----------------------------------------------------------------
    # Create / write / unlink
    # -----------------------------------------------------------------
    @api.onchange('target_mode')
    def _onchange_target_mode(self):
        # Đổi sang "Tất cả" thì bỏ hết cửa hàng đã chọn — tránh gửi nhầm phạm vi hẹp.
        if self.target_mode == 'all':
            self.franchise_ids = [fields.Command.clear()]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('target_mode') == 'all':
                vals['franchise_ids'] = [fields.Command.clear()]
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'wujia.notification'
                )
            if vals.get('state') == 'published':
                vals.setdefault('published_date', fields.Datetime.now())
                vals.setdefault('published_by_id', self.env.user.id)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('target_mode') == 'all':
            vals.setdefault('franchise_ids', [fields.Command.clear()])
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

    @api.constrains('target_mode', 'target_area_ids', 'target_state_ids',
                    'target_exclude_franchise_ids', 'franchise_ids')
    def _check_target(self):
        for rec in self:
            if rec.target_mode == 'filter' and not (
                rec.target_area_ids or rec.target_state_ids
                or rec.target_exclude_franchise_ids
            ):
                # Tiêu chí rỗng khớp toàn bộ cửa hàng — trùng ý nghĩa "Tất cả", chặn cho rõ ràng.
                raise ValidationError(_(MSG_TARGET_NO_CRITERIA))
            if rec.target_mode == 'all' and rec.franchise_ids:
                raise ValidationError(_(MSG_TARGET_ALL_HAS_STORES))

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
            vals = {
                'state': 'published',
                'published_date': now,
                'published_by_id': self.env.user.id,
            }
            # Chốt danh sách nhận tại thời điểm gửi (ghi chú cột L dòng 745): cửa hàng mở
            # sau ngày gửi KHÔNG nhận thông báo cũ; HQ dùng action_refresh_recipients nếu muốn.
            if rec.target_mode == 'filter':
                franchises = rec._resolve_target_franchises()
                if not franchises:
                    raise UserError(_(MSG_TARGET_EMPTY))
                vals['franchise_ids'] = [fields.Command.set(franchises.ids)]
            elif rec.target_mode == 'manual' and not rec.franchise_ids:
                raise UserError(_(MSG_TARGET_MANUAL_EMPTY))
            rec.write(vals)
        return True

    def action_preview_recipients(self):
        """Xem trước cửa hàng sẽ nhận — HQ kiểm tra trước khi gửi, không phải tick từng tiệm."""
        self.ensure_one()
        if self.target_mode == 'all':
            domain = []
        elif self.target_mode == 'filter':
            domain = self._target_domain()
        else:
            domain = [('id', 'in', self.franchise_ids.ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cửa hàng nhận'),
            'res_model': 'wujia.franchise.management',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'create': False},
        }

    def action_refresh_recipients(self):
        """Chốt lại danh sách nhận theo tiêu chí hiện tại — dùng khi có cửa hàng mới mở."""
        for rec in self:
            if rec.target_mode != 'filter':
                raise UserError(_(
                    'Chỉ thông báo gửi "Theo tiêu chí" mới cập nhật lại được danh sách nhận.'
                ))
            franchises = rec._resolve_target_franchises()
            if not franchises:
                raise UserError(_(MSG_TARGET_EMPTY))
            rec.franchise_ids = [fields.Command.set(franchises.ids)]
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
    def _target_domain(self):
        """Tiêu chí → domain trên wujia.franchise.management. OR trong nhóm, AND giữa nhóm."""
        self.ensure_one()
        domain = []
        if self.target_status == 'active':
            domain.append(('status', '=', 'active'))
        if self.target_area_ids:
            domain.append(('area_id', 'in', self.target_area_ids.ids))
        if self.target_state_ids:
            domain.append(('state_id', 'in', self.target_state_ids.ids))
        if self.target_exclude_franchise_ids:
            domain.append(('id', 'not in', self.target_exclude_franchise_ids.ids))
        return domain

    def _resolve_target_franchises(self):
        """Dịch tiêu chí thành danh sách cửa hàng thật. Mode khác `filter` giữ nguyên lựa chọn."""
        self.ensure_one()
        if self.target_mode != 'filter':
            return self.franchise_ids
        return self.env['wujia.franchise.management'].sudo().search(self._target_domain())

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
