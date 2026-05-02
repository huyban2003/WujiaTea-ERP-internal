from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WujiaFleetType(models.Model):
    _name = 'wujia.fleet.type'
    _description = 'Wujia Fleet Type — Loại xe'
    _order = 'sequence, payload_capacity_ton, name'

    name = fields.Char(
        string='Tên loại xe',
        required=True,
        translate=True,
        help='Ví dụ "Xe tải 1.9T", "Xe đông lạnh 17T".',
    )
    code = fields.Char(string='Mã loại xe', index=True)
    sequence = fields.Integer(default=10)
    vehicle_category = fields.Selection(
        [
            ('truck', 'Xe tải'),
            ('pickup', 'Bán tải'),
            ('van', 'Van'),
            ('other', 'Khác'),
        ],
        string='Nhóm xe',
        required=True,
        default='truck',
    )
    payload_capacity_ton = fields.Float(
        string='Tải trọng (tấn)',
        required=True,
        default=0.0,
        digits=(10, 2),
    )
    max_payload_kg = fields.Float(
        string='Tải trọng tối đa (kg)',
        compute='_compute_max_payload_kg',
        store=True,
        digits='Stock Weight',
        help='= payload_capacity_ton × 1000. Dùng để compare với planned_weight '
             'cho cảnh báo vượt tải batch.',
    )
    description = fields.Text(string='Mô tả')

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã loại xe phải duy nhất.',
    )

    @api.depends('payload_capacity_ton')
    def _compute_max_payload_kg(self):
        for rec in self:
            rec.max_payload_kg = (rec.payload_capacity_ton or 0.0) * 1000.0

    @api.constrains('payload_capacity_ton')
    def _check_payload(self):
        for rec in self:
            if rec.payload_capacity_ton < 0:
                raise ValidationError(_("Tải trọng phải >= 0."))
