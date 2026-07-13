from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    weight_per_unit = fields.Float(
        string='Khối lượng/đơn vị',
        digits='Stock Weight',
        readonly=True,
        copy=True,
        help='Snapshot khối lượng 1 đơn vị product tại lúc chọn sản phẩm. '
             'Không cho user nhập tay; lưu để dữ liệu cũ giữ nguyên kể cả khi product.weight đổi.',
    )
    planned_weight = fields.Float(
        string='Khối lượng dự kiến',
        compute='_compute_planned_weight',
        store=True,
        digits='Stock Weight',
        help='= product_uom_qty × weight_per_unit.',
    )

    @api.depends('product_uom_qty', 'weight_per_unit')
    def _compute_planned_weight(self):
        for line in self:
            line.planned_weight = (line.product_uom_qty or 0.0) * (line.weight_per_unit or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id_snapshot_weight(self):
        if self.product_id:
            self.weight_per_unit = self.product_id.weight or 0.0

    @api.model_create_multi
    def create(self, vals_list):
        # Snapshot weight tại lúc create — cover cả flow API/import không qua onchange.
        for vals in vals_list:
            if 'weight_per_unit' not in vals and vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                vals['weight_per_unit'] = product.weight or 0.0
        return super().create(vals_list)

    @api.constrains('product_id', 'product_uom_qty', 'order_id')
    def _check_min_max_qty_portal(self):
        """Validate min/step/max từ product.product — chỉ áp với đơn portal.
        Step = min_qty (BA); max_qty = 0 nghĩa là không giới hạn."""
        for line in self:
            if not line.order_id.is_portal_order:
                continue
            product = line.product_id
            qty = line.product_uom_qty
            if product.min_qty and qty < product.min_qty:
                raise ValidationError(_(
                    "Sản phẩm '%s' yêu cầu số lượng tối thiểu %s, đang đặt %s.",
                    product.name, product.min_qty, qty,
                ))
            if product.min_qty and qty % product.min_qty:
                raise ValidationError(_(
                    "Số lượng của '%s' phải tăng theo bước %s, đang đặt %s.",
                    product.name, product.min_qty, qty,
                ))
            if product.max_qty and qty > product.max_qty:
                raise ValidationError(_(
                    "Sản phẩm '%s' chỉ cho phép tối đa %s/đơn, đang đặt %s.",
                    product.name, product.max_qty, qty,
                ))
