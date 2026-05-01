from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_public_website = fields.Boolean(
        string='Hiện trên portal',
        default=False,
        index=True,
        help='Đánh dấu sản phẩm hiển thị trong catalog /portal/order. '
             'Chỉ những sản phẩm có flag này mới được phép user portal đặt mua.',
    )
    min_qty = fields.Integer(
        string='Số lượng tối thiểu/đơn',
        default=1,
        help='Tối thiểu mỗi dòng cart. 0 hoặc 1 = không giới hạn dưới.',
    )
    max_qty = fields.Integer(
        string='Số lượng tối đa/đơn',
        default=0,
        help='Tối đa mỗi dòng cart. 0 = không giới hạn trên.',
    )

    @api.constrains('min_qty', 'max_qty')
    def _check_min_max_qty_bounds(self):
        for tmpl in self:
            if tmpl.min_qty < 0:
                raise ValidationError(_("Số lượng tối thiểu không thể âm."))
            if tmpl.max_qty < 0:
                raise ValidationError(_("Số lượng tối đa không thể âm."))
            if tmpl.max_qty and tmpl.min_qty and tmpl.max_qty < tmpl.min_qty:
                raise ValidationError(_(
                    "Số lượng tối đa (%s) phải >= số lượng tối thiểu (%s).",
                    tmpl.max_qty, tmpl.min_qty,
                ))
