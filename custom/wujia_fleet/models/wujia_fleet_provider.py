import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


class WujiaFleetProvider(models.Model):
    _name = 'wujia.fleet.provider'
    _description = 'Wujia Fleet Provider — Nhà xe / Đội xe'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tên đội xe',
        required=True,
        tracking=True,
        help='Tên đội xe / nhà xe, ví dụ "CTY TNHH Vận Tải Nguyễn Dũng".',
    )
    code = fields.Char(
        string='Mã đội xe',
        tracking=True,
        index=True,
        help='Mã ngắn dùng cho lookup, ví dụ NDUNG, AHOO.',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='restrict',
        tracking=True,
        help='Link tới contact / vendor của Odoo nếu đội xe là nhà cung cấp '
             'và cần xuất PO.',
    )
    provider_type = fields.Selection(
        [
            ('company', 'Xe công ty'),
            ('outsource', 'Thuê ngoài'),
        ],
        string='Loại đội xe',
        required=True,
        default='outsource',
        tracking=True,
        index=True,
    )
    description = fields.Text(string='Mô tả')
    contact_name = fields.Char(string='Người liên hệ')
    phone = fields.Char(string='SĐT')
    email = fields.Char(string='Email')

    vehicle_ids = fields.One2many(
        'wujia.fleet.management',
        'provider_id',
        string='Danh sách xe',
    )
    vehicle_count = fields.Integer(
        string='Số xe',
        compute='_compute_vehicle_count',
        store=True,
        compute_sudo=True,
    )

    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã đội xe phải duy nhất.',
    )

    @api.depends('vehicle_ids.active')
    def _compute_vehicle_count(self):
        for rec in self:
            rec.vehicle_count = len(rec.vehicle_ids.filtered('active'))

    @api.constrains('email')
    def _check_email_format(self):
        for rec in self:
            if rec.email and not EMAIL_RE.match(rec.email):
                raise ValidationError(_("Email '%s' không đúng định dạng.", rec.email))

    def action_view_vehicles(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Xe của %s', self.name),
            'res_model': 'wujia.fleet.management',
            'view_mode': 'list,kanban,form',
            'domain': [('provider_id', '=', self.id)],
            'context': {'default_provider_id': self.id},
        }
