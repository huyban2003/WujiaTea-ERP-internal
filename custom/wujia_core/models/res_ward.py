from odoo import fields, models


class ResWard(models.Model):
    _name = 'res.ward'
    _description = 'Ward / Phường — Xã'
    _order = 'state_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Tên phường/xã', required=True)
    code = fields.Char(string='Mã phường/xã', required=True, help='Mã hành chính, ví dụ 27001.')
    state_id = fields.Many2one(
        'res.country.state',
        string='Tỉnh/Thành',
        required=True,
        ondelete='restrict',
        index=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='Quốc gia',
        related='state_id.country_id',
        store=True,
        readonly=True,
    )
    active = fields.Boolean(default=True)

    _code_state_uniq = models.Constraint(
        'UNIQUE (state_id, code)',
        'Mã phường/xã phải duy nhất trong từng tỉnh/thành.',
    )
