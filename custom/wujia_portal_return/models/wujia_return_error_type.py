from odoo import fields, models
from odoo.tools import ormcache


class WujiaReturnErrorType(models.Model):
    """Master data — loại lỗi đổi trả (vd: hỏng bao bì, sai sản phẩm).

    Skeleton: chỉ name/code/active. Seed qua data/return_error_type_data.xml."""

    _name = 'wujia.return.error.type'
    _description = 'Wujia Return Error Type'
    _order = 'sequence, code, id'

    name = fields.Char(string='Tên lỗi', required=True, translate=True)
    code = fields.Char(string='Mã', required=True)
    description = fields.Char(string='Mô tả ngắn', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('uniq_code', 'unique(code)', 'Mã loại lỗi phải duy nhất.'),
    ]

    @ormcache()
    def _get_active_error_types_cached(self):
        """Trả tuple (id, name, code) — dùng cho dropdown filter list. Cache toàn bộ."""
        return tuple(
            (rec.id, rec.name, rec.code)
            for rec in self.sudo().search([('active', '=', True)], order='sequence, code')
        )

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()  # invalidate ormcache toàn registry
        return res

    def create(self, vals_list):
        res = super().create(vals_list)
        self.env.registry.clear_cache()
        return res
