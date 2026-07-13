from odoo import api, fields, models


class WujiaPortalCart(models.Model):
    """Giỏ hàng portal DÙNG CHUNG theo cửa hàng (BA FINAL: 1 store = 1 giỏ active,
    mọi user có membership đều thao tác cùng giỏ, last-write-wins).
    Cart persistent — sau submit chỉ clear line + note, không xoá record.
    Truy cập từ portal luôn qua controller (sudo + gate franchise), không có ACL trực tiếp.
    """
    _name = 'wujia.portal.cart'
    _description = 'Wujia Portal Cart (shared per store)'

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        required=True,
        ondelete='cascade',
        index=True,
    )
    note = fields.Text(string='Ghi chú đơn hàng')
    line_ids = fields.One2many('wujia.portal.cart.line', 'cart_id')

    _franchise_uniq = models.Constraint(
        'UNIQUE (franchise_id)',
        'Mỗi cửa hàng chỉ có một giỏ hàng.',
    )

    @api.depends('franchise_id')
    def _compute_display_name(self):
        for cart in self:
            cart.display_name = f'Giỏ [{cart.franchise_id.code or "?"}] {cart.franchise_id.name or ""}'


class WujiaPortalCartLine(models.Model):
    """1 sản phẩm = 1 dòng/giỏ (unique cart+product — điều kiện cho SQL upsert
    ON CONFLICT ở controller). Không lưu giá: giá luôn tính lại từ pricelist."""
    _name = 'wujia.portal.cart.line'
    _description = 'Wujia Portal Cart Line'

    cart_id = fields.Many2one(
        'wujia.portal.cart',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='cascade',
    )
    qty = fields.Integer(default=0)

    _cart_product_uniq = models.Constraint(
        'UNIQUE (cart_id, product_id)',
        'Mỗi sản phẩm chỉ có một dòng trong giỏ.',
    )
