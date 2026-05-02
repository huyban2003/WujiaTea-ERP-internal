from odoo import _, api, fields, models


DELIVERY_STATUS = [
    ('pending', 'Chờ điều phối'),
    ('assigned', 'Đã sắp chuyến'),
    ('loaded', 'Đã chất hàng'),
    ('delivering', 'Đang giao'),
    ('done', 'Đã giao'),
    ('cancelled', 'Hủy giao'),
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Cửa hàng nhượng quyền',
        index=True,
        tracking=True,
        help='Cửa hàng nhượng quyền nhận hàng. Tự copy từ SO khi confirm; có thể '
             'set thủ công cho picking nội bộ.',
    )
    area_id = fields.Many2one(
        'res.area',
        string='Khu vực',
        related='franchise_id.area_id',
        store=True,
        readonly=True,
        index=True,
    )
    delivery_sequence = fields.Integer(
        string='Thứ tự giao',
        default=10,
        help='Thứ tự giao trong batch.',
    )
    vehicle_id = fields.Many2one(
        'wujia.fleet.management',
        string='Xe giao',
        related='batch_id.vehicle_id',
        store=True,
        readonly=True,
        index=True,
    )
    provider_id = fields.Many2one(
        'wujia.fleet.provider',
        string='Đội xe',
        related='vehicle_id.provider_id',
        store=True,
        readonly=True,
        index=True,
    )
    delivery_status = fields.Selection(
        DELIVERY_STATUS,
        string='Trạng thái giao',
        default='pending',
        tracking=True,
        index=True,
        help='Trạng thái điều phối — KHÔNG thay state chuẩn của picking.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    shipping_cost = fields.Monetary(
        string='Chi phí vận chuyển (phân bổ)',
        currency_field='currency_id',
        compute='_compute_shipping_allocation',
        store=True,
        help='Chi phí vận chuyển phân bổ theo tỉ lệ planned_weight của picking '
             'trong tổng planned_weight của batch.',
    )
    drop_fee = fields.Monetary(
        string='Phí drop',
        currency_field='currency_id',
        compute='_compute_shipping_allocation',
        store=True,
    )
    delivery_note = fields.Text(string='Ghi chú giao hàng')

    @api.depends(
        'batch_id',
        'batch_id.shipping_cost',
        'batch_id.drop_fee_total',
        'batch_id.planned_weight',
        'planned_weight',
    )
    def _compute_shipping_allocation(self):
        for pick in self:
            batch = pick.batch_id
            if not batch or not batch.planned_weight:
                pick.shipping_cost = 0.0
                pick.drop_fee = 0.0
                continue
            ratio = (pick.planned_weight or 0.0) / batch.planned_weight
            pick.shipping_cost = (batch.shipping_cost or 0.0) * ratio
            pick.drop_fee = (batch.drop_fee_total or 0.0) * ratio

    def write(self, vals):
        # Auto-transition delivery_status khi picking được gán vào batch.
        if 'batch_id' in vals:
            new_batch = vals.get('batch_id')
            for pick in self:
                if new_batch and pick.delivery_status == 'pending':
                    vals.setdefault('delivery_status', 'assigned')
                elif not new_batch and pick.delivery_status == 'assigned':
                    vals.setdefault('delivery_status', 'pending')
        return super().write(vals)

    def _action_done(self):
        res = super()._action_done()
        # Khi picking native state = done thì delivery_status = done.
        for pick in self:
            if pick.state == 'done' and pick.delivery_status not in ('done', 'cancelled'):
                pick.delivery_status = 'done'
        return res

    def action_cancel(self):
        res = super().action_cancel()
        for pick in self:
            if pick.delivery_status not in ('done', 'cancelled'):
                pick.delivery_status = 'cancelled'
        return res
