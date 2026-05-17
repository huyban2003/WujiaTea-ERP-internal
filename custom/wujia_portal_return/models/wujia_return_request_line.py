from odoo import fields, models


class WujiaReturnRequestLine(models.Model):
    _name = 'wujia.return.request.line'
    _description = 'Wujia Return Request Line'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        'wujia.return.request', string='Yêu cầu',
        required=True, ondelete='cascade', index=True,
    )
    # product_id optional vì portal cho phép user gõ tên tự do (sản phẩm chưa
    # có trong catalog hoặc sản phẩm cũ). HQ resolve sau khi duyệt.
    product_id = fields.Many2one(
        'product.product', string='Sản phẩm',
        index=True, ondelete='restrict',
    )
    product_name = fields.Char(
        string='Tên sản phẩm (free text)',
        help='Tên do user nhập từ portal. HQ sẽ match với product_id sau.',
    )
    qty = fields.Float(string='Số lượng', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Đơn vị')
    reason = fields.Char(string='Lý do dòng')
    sequence = fields.Integer(default=10)
