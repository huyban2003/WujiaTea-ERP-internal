from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_public_portal = fields.Boolean(
        string='Hiện trên portal',
        default=False,
        index=True,
        help='Bật để public sản phẩm lên portal đặt hàng (/portal/order). '
             'Sản phẩm public bắt buộc có số lượng tối thiểu > 0.',
    )
    min_qty = fields.Integer(
        string='Số lượng tối thiểu',
        default=0,
        help='Số lượng đặt tối thiểu. Bước tăng/giảm trên portal = giá trị này.',
    )
    max_qty = fields.Integer(
        string='Số lượng tối đa',
        default=0,
        help='0 = không giới hạn. Nếu > 0 phải >= min và chia hết cho min.',
    )
    description_ecommerce = fields.Char(
        string='Quy cách',
        help='Quy cách hiển thị trên portal, ví dụ: 10kg/bao, 120 cái/thùng.',
    )
    name_chinese = fields.Char(
        string='Tên tiếng Hoa',
        help='Hiển thị dưới tên sản phẩm trên portal. User nhập tay, không dịch tự động.',
    )
    public_categ_id = fields.Many2one(
        'wujia.product.category',
        string='Danh mục portal',
        index=True,
        ondelete='set null',
    )

    @api.constrains('is_public_portal', 'min_qty', 'max_qty')
    def _check_portal_qty_rules(self):
        for product in self:
            if product.min_qty < 0 or product.max_qty < 0:
                raise ValidationError(_("Số lượng tối thiểu/tối đa không thể âm."))
            if product.is_public_portal and product.min_qty <= 0:
                raise ValidationError(_(
                    "Sản phẩm public portal '%s' phải có số lượng tối thiểu > 0 "
                    "(bước đặt hàng = số lượng tối thiểu).", product.display_name,
                ))
            if product.max_qty:
                if product.max_qty < product.min_qty:
                    raise ValidationError(_(
                        "Số lượng tối đa (%s) phải >= số lượng tối thiểu (%s).",
                        product.max_qty, product.min_qty,
                    ))
                if product.min_qty and product.max_qty % product.min_qty:
                    raise ValidationError(_(
                        "Số lượng tối đa (%s) phải chia hết cho số lượng tối thiểu (%s).",
                        product.max_qty, product.min_qty,
                    ))
