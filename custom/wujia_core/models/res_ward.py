from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResWard(models.Model):
    _name = 'res.ward'
    _description = 'Ward / Phường — Xã'
    _order = 'state_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Tên phường/xã', required=True)
    code = fields.Char(string='Mã phường/xã', help='Mã hành chính, ví dụ 27001.')
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
    area_id = fields.Many2one(
        'res.area',
        string='Khu vực',
        ondelete='set null',
        index=True,
        help='Khu vực kinh doanh chứa phường/xã này.',
    )
    active = fields.Boolean(default=True)

    _code_state_uniq = models.Constraint(
        'UNIQUE (state_id, code)',
        'Mã phường/xã phải duy nhất trong từng tỉnh/thành.',
    )

    @api.constrains('state_id', 'area_id')
    def _check_area_state_consistency(self):
        # Soft hint — không bắt buộc nhưng cảnh báo nếu area có manager khu vực
        # khác với tỉnh thành. Ở đây chỉ giữ chỗ; chưa enforce strict.
        return
