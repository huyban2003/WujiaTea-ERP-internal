import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


class WujiaFranchiseManagement(models.Model):
    _name = 'wujia.franchise.management'
    _description = 'Wujia Franchise Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'code, name'

    code = fields.Char(
        string='Mã cửa hàng',
        required=True,
        index=True,
        tracking=True,
        help='Mã cửa hàng nhượng quyền, ví dụ H010 hoặc HN-01.',
    )
    name = fields.Char(
        string='Tên cửa hàng',
        required=True,
        tracking=True,
        help='Tên hiển thị, ví dụ "[H010] Cửa hàng 219 Vĩnh Viễn".',
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='restrict',
        tracking=True,
        help='Link tới res.partner đại diện cửa hàng — entity transactional cho '
             'sale.order, account.move, membership.',
    )

    opening_date = fields.Date(string='Ngày khai trương', tracking=True)
    address = fields.Text(string='Địa chỉ', tracking=True)
    state_id = fields.Many2one(
        'res.country.state',
        string='Tỉnh/Thành',
        tracking=True,
    )
    phone = fields.Char(string='SĐT')
    email = fields.Char(string='Email')

    franchise_start_date = fields.Date(
        string='Ngày bắt đầu nhượng quyền',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    franchise_end_date = fields.Date(
        string='Ngày kết thúc nhượng quyền',
        required=True,
        tracking=True,
    )
    remaining_days = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_remaining_days',
        store=True,
    )
    is_expired = fields.Boolean(
        string='Đã hết hạn',
        compute='_compute_remaining_days',
        store=True,
    )

    area_id = fields.Many2one(
        'res.area',
        string='Khu vực',
        tracking=True,
        ondelete='restrict',
    )
    area_name = fields.Char(related='area_id.name', store=True, readonly=True)

    description = fields.Text(
        string='Mô tả vận hành',
        help='Lưu ý vận hành, giao hàng, cấm tải, cấm đỗ...',
    )
    note = fields.Text(string='Ghi chú nội bộ')

    portal_locked = fields.Boolean(
        string='Khóa portal',
        default=False,
        tracking=True,
        help='Khóa toàn bộ truy cập portal của cửa hàng (vd vi phạm hợp đồng).',
    )
    invoiced = fields.Boolean(
        string='Đã xuất hóa đơn',
        default=False,
        help='Cờ theo dõi đã xuất hóa đơn liên quan.',
    )

    status = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('active', 'Đang hoạt động'),
            ('locked', 'Khóa'),
            ('closed', 'Đã đóng'),
            ('expired', 'Hết hạn'),
        ],
        string='Trạng thái',
        required=True,
        default='active',
        tracking=True,
    )

    member_ids = fields.One2many(
        'wujia.franchise.member',
        'franchise_id',
        string='Thành viên',
    )
    member_count = fields.Integer(
        string='Số thành viên',
        compute='_compute_member_count',
    )
    main_owner_member_id = fields.Many2one(
        'wujia.franchise.member',
        string='Chủ chính',
        compute='_compute_main_owner_member',
        help='Thành viên có role=owner đang active của cửa hàng (BA spec).',
    )

    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã cửa hàng phải duy nhất.',
    )

    # ===========================================================
    # Compute / depends
    # ===========================================================
    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            if rec.code and rec.name:
                rec.display_name = f'[{rec.code}] {rec.name}'
            else:
                rec.display_name = rec.name or rec.code or _('New Franchise')

    @api.depends('franchise_end_date')
    def _compute_remaining_days(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.franchise_end_date:
                delta = (rec.franchise_end_date - today).days
                rec.remaining_days = delta
                rec.is_expired = delta < 0
            else:
                rec.remaining_days = 0
                rec.is_expired = False

    @api.depends('member_ids.is_currently_valid')
    def _compute_member_count(self):
        for rec in self:
            rec.member_count = len(
                rec.member_ids.filtered('is_currently_valid')
            )

    @api.depends('member_ids.role', 'member_ids.is_currently_valid')
    def _compute_main_owner_member(self):
        for rec in self:
            owner = rec.member_ids.filtered(
                lambda m: m.role == 'owner' and m.is_currently_valid
            )[:1]
            rec.main_owner_member_id = owner

    # ===========================================================
    # Constraints
    # ===========================================================
    @api.constrains('franchise_start_date', 'franchise_end_date')
    def _check_franchise_dates(self):
        for rec in self:
            if (rec.franchise_end_date and rec.franchise_start_date
                    and rec.franchise_end_date < rec.franchise_start_date):
                raise ValidationError(_(
                    "Ngày kết thúc nhượng quyền phải >= ngày bắt đầu."
                ))

    @api.constrains('email')
    def _check_email_format(self):
        for rec in self:
            if rec.email and not EMAIL_RE.match(rec.email):
                raise ValidationError(_("Email '%s' không đúng định dạng.", rec.email))

    @api.constrains('status', 'partner_id')
    def _check_partner_required_when_active(self):
        for rec in self:
            if rec.status == 'active' and not rec.partner_id:
                raise ValidationError(_(
                    "Cửa hàng '%s' đang Active phải có Partner để hỗ trợ tạo "
                    "sale.order / hóa đơn.", rec.display_name,
                ))

    # ===========================================================
    # Onchange / Actions
    # ===========================================================
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.name or self.partner_id.name
            self.phone = self.phone or self.partner_id.phone
            self.email = self.email or self.partner_id.email
            self.state_id = self.state_id or self.partner_id.state_id

    def action_view_members(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Thành viên cửa hàng %s', self.display_name),
            'res_model': 'wujia.franchise.member',
            'view_mode': 'list,form',
            'domain': [('franchise_id', '=', self.id)],
            'context': {'default_franchise_id': self.id},
        }

    def action_set_active(self):
        for rec in self:
            rec.status = 'active'
            rec.portal_locked = False

    def action_lock_portal(self):
        for rec in self:
            rec.status = 'locked'
            rec.portal_locked = True

    def action_close(self):
        for rec in self:
            rec.status = 'closed'
            rec.portal_locked = True

    @api.model
    def _cron_check_expired(self):
        """Tự động set status='expired' khi đến hạn (ir.cron daily)."""
        today = fields.Date.context_today(self)
        expired = self.search([
            ('franchise_end_date', '<', today),
            ('status', 'not in', ['expired', 'closed']),
            ('active', '=', True),
        ])
        expired.write({'status': 'expired'})
