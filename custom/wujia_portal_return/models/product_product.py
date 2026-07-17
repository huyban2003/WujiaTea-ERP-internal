from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    """Cấu hình bù hàng ở mức sản phẩm (BA spec K — product.product extend).

    Dùng khi HQ duyệt yêu cầu bù: snapshot policy + ĐVT quyền lợi/giao bù vào
    request. compensation_unit_qty (hệ số quy đổi) nhập tại thời điểm duyệt.
    """

    _inherit = 'product.product'

    compensation_enabled = fields.Boolean(
        string='Bật bù hàng',
        default=False,
        help='Cho phép sản phẩm này được xử lý bù hàng (tạo SO 0đ).',
    )
    compensation_policy = fields.Selection(
        [('exact', 'Bù đúng số lượng'),
         ('accumulate', 'Cộng dồn nguyên kiện')],
        string='Chính sách bù',
        default='exact',
        help='exact: bù đúng số lượng còn thiếu; '
             'accumulate: cộng dồn đủ một đơn vị giao mới bù (phần lẻ chuyển kỳ sau).',
    )
    compensation_claim_uom_id = fields.Many2one(
        'uom.uom',
        string='ĐVT quyền lợi',
        help='Đơn vị ghi nhận quyền lợi bù (vd: kg, cây).',
    )
    compensation_product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm bù',
        help='Sản phẩm thực tế đưa vào SO bù. Để trống = dùng chính sản phẩm này.',
    )
    compensation_delivery_uom_id = fields.Many2one(
        'uom.uom',
        string='ĐVT giao bù',
        help='Đơn vị thực tế đặt trên SO bù (vd: bịch, thùng, cây).',
    )
    compensation_unit_qty = fields.Float(
        string='SL quyền lợi / đơn vị giao',
        digits='Product Unit of Measure',
        help='SL quyền lợi tương ứng một đơn vị giao bù (vd 1 bịch = 10 kg). '
             'Gợi ý mặc định khi HQ duyệt yêu cầu.',
    )

    @api.constrains('compensation_enabled', 'compensation_policy',
                    'compensation_claim_uom_id', 'compensation_delivery_uom_id',
                    'compensation_unit_qty')
    def _check_compensation_config(self):
        for product in self:
            if not product.compensation_enabled:
                continue
            if not product.compensation_claim_uom_id:
                raise ValidationError(_(
                    "Sản phẩm '%s' bật bù hàng phải có ĐVT quyền lợi.",
                    product.display_name,
                ))
            if product.compensation_policy == 'accumulate':
                if not product.compensation_delivery_uom_id:
                    raise ValidationError(_(
                        "Sản phẩm '%s' theo chính sách cộng dồn phải có ĐVT giao bù.",
                        product.display_name,
                    ))
                if product.compensation_unit_qty <= 0:
                    raise ValidationError(_(
                        "Sản phẩm '%s' theo chính sách cộng dồn phải có SL quyền lợi / đơn vị giao > 0.",
                        product.display_name,
                    ))
