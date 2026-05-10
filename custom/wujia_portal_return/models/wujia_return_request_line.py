from odoo import fields, models


class WujiaReturnRequestLine(models.Model):
    _name = 'wujia.return.request.line'
    _description = 'Wujia Return Request Line'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        'wujia.return.request', string='Yêu cầu',
        required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Sản phẩm',
        required=True, index=True,
    )
    qty = fields.Float(string='Số lượng', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Đơn vị')
    reason = fields.Char(string='Lý do dòng')
    sequence = fields.Integer(default=10)
