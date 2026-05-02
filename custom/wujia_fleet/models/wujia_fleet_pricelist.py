from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


PRICELIST_STATE = [
    ('draft', 'Nháp'),
    ('active', 'Đang áp dụng'),
    ('expired', 'Hết hạn'),
    ('archived', 'Lưu trữ'),
]


class WujiaFleetPricelist(models.Model):
    _name = 'wujia.fleet.pricelist'
    _description = 'Wujia Fleet Pricelist — Bảng giá vận chuyển'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, date_from desc, id desc'

    name = fields.Char(string='Tên bảng giá', required=True, tracking=True)
    code = fields.Char(string='Mã bảng giá', index=True)
    sequence = fields.Integer(
        string='Độ ưu tiên',
        default=10,
        help='Số nhỏ = ưu tiên cao khi nhiều bảng giá cùng match.',
    )

    fleet_type_id = fields.Many2one(
        'wujia.fleet.type',
        string='Loại xe',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    provider_id = fields.Many2one(
        'wujia.fleet.provider',
        string='Đội xe',
        ondelete='restrict',
        tracking=True,
        index=True,
        help='Để trống nếu áp dụng chung cho mọi đội xe của loại xe này.',
    )
    trip_scope = fields.Selection(
        [
            ('city', 'Nội thành'),
            ('interprovince', 'Đi tỉnh'),
            ('other', 'Khác'),
        ],
        string='Phạm vi',
        default='interprovince',
    )

    default_drop_fee = fields.Monetary(
        string='Phí drop mặc định',
        currency_field='currency_id',
        default=0.0,
        help='Phí drop nếu dòng giá không khai báo riêng.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    date_from = fields.Date(
        string='Hiệu lực từ',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True,
    )
    date_to = fields.Date(string='Hiệu lực đến', tracking=True, index=True)

    line_ids = fields.One2many(
        'wujia.fleet.pricelist.line',
        'pricelist_id',
        string='Dòng giá',
        copy=True,
    )

    state = fields.Selection(
        PRICELIST_STATE,
        string='Trạng thái',
        required=True,
        default='draft',
        tracking=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    note = fields.Text(string='Ghi chú')

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã bảng giá phải duy nhất.',
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(_("Hiệu lực đến phải >= hiệu lực từ."))

    def action_activate(self):
        for rec in self:
            rec.state = 'active'

    def action_archive_pricelist(self):
        for rec in self:
            rec.state = 'archived'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _cron_expire_pricelists(self):
        """Chuyển state='active' → 'expired' khi date_to < today."""
        today = fields.Date.context_today(self)
        expired = self.search([
            ('state', '=', 'active'),
            ('date_to', '!=', False),
            ('date_to', '<', today),
        ])
        if expired:
            expired.write({'state': 'expired'})
