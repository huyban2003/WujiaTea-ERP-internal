from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_public_portal = fields.Boolean(
        string='Show on portal',
        default=False,
        index=True,
        help="Turn on to publish the product on the ordering portal (/portal/order). A published product must have a minimum quantity > 0.",
    )
    min_qty = fields.Integer(
        string='Minimum quantity',
        default=0,
        help='Minimum order quantity. The portal steps up/down by this value.',
    )
    max_qty = fields.Integer(
        string='Maximum quantity',
        default=0,
        help='0 = unlimited. If > 0 it must be >= min and a multiple of min.',
    )
    # Đặt tiền tố wujia_: tên `description_ecommerce` trùng field Html dịch được của
    # website_sale trên product.template, đụng độ làm cột đổi sang jsonb (WJ-PROD-001).
    wujia_packaging = fields.Char(
        string='Packaging',
        help='Packaging shown on the portal, e.g. 10kg/bag, 120 pcs/carton.',
    )
    name_chinese = fields.Char(
        string='Chinese name',
        help='Displayed under the product name on the portal. Entered manually, never auto-translated.',
    )
    public_categ_id = fields.Many2one(
        'wujia.product.category',
        string='Portal category',
        index=True,
        ondelete='set null',
    )

    def _portal_qty_error(self, qty):
        """Luật đặt hàng portal (bước = min_qty, max 0 = không giới hạn) → None hoặc (mã, ngưỡng)."""
        self.ensure_one()
        step = self.min_qty
        if step <= 0:
            return 'MIN_QTY_NOT_CONFIGURED', 0
        if qty < step:
            return 'QTY_BELOW_MIN', step
        if qty % step:
            return 'QTY_INVALID_STEP', step
        if self.max_qty and qty > self.max_qty:
            return 'QTY_ABOVE_MAX', self.max_qty
        return None

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
