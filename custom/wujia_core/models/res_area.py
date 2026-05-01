from odoo import _, api, fields, models


class ResArea(models.Model):
    _name = 'res.area'
    _description = 'Sales / Operation Area — Khu vực'
    _order = 'sequence, code, name'
    _rec_name = 'name'

    code = fields.Char(string='Mã khu vực', required=True, help='Ví dụ KV-HCM-01.')
    name = fields.Char(string='Tên khu vực', required=True, translate=True)
    sequence = fields.Integer(default=10)
    manager_user_id = fields.Many2one(
        'res.users',
        string='Người phụ trách',
        help='Người chịu trách nhiệm vận hành khu vực.',
    )
    ward_ids = fields.Many2many(
        'res.ward',
        'res_area_ward_rel',
        'area_id',
        'ward_id',
        string='Phường/Xã',
        help='Danh sách phường/xã thuộc khu vực — chọn từ danh mục res.ward.',
    )
    state_ids = fields.Many2many(
        'res.country.state',
        string='Tỉnh/Thành',
        compute='_compute_state_ids',
        store=True,
        help='Danh sách tỉnh/thành tổng hợp từ phường/xã thuộc khu vực — cập nhật tự động.',
    )
    description = fields.Text(string='Mô tả phạm vi khu vực')
    note = fields.Text(string='Ghi chú nội bộ')
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint(
        'UNIQUE (code)',
        'Mã khu vực phải duy nhất.',
    )

    @api.depends('ward_ids.state_id')
    def _compute_state_ids(self):
        for rec in self:
            rec.state_ids = rec.ward_ids.mapped('state_id')

    def action_view_wards(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Phường/Xã thuộc %s', self.name),
            'res_model': 'res.ward',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.ward_ids.ids)],
        }
