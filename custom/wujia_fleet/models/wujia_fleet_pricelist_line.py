from odoo import fields, models


class WujiaFleetPricelistLine(models.Model):
    _name = 'wujia.fleet.pricelist.line'
    _description = 'Wujia Fleet Pricelist Line — Dòng giá theo khu vực'
    _order = 'pricelist_id, sequence, id'

    pricelist_id = fields.Many2one(
        'wujia.fleet.pricelist',
        string='Bảng giá',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)

    area_ids = fields.Many2many(
        'res.area',
        'wujia_fleet_pricelist_line_area_rel',
        'line_id',
        'area_id',
        string='Khu vực áp dụng',
        required=True,
        help='Một dòng giá có thể áp dụng cho nhiều khu vực — match khi area '
             'của picking nằm trong danh sách này.',
    )
    price = fields.Monetary(
        string='Giá vận chuyển',
        required=True,
        currency_field='currency_id',
        default=0.0,
    )
    drop_fee = fields.Monetary(
        string='Phí drop',
        currency_field='currency_id',
        default=0.0,
    )
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        store=True,
        readonly=True,
    )
    active = fields.Boolean(default=True)
    note = fields.Char(string='Ghi chú')
