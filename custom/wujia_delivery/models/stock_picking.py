from odoo import _, api, fields, models


DELIVERY_STATUS = [
    ('pending', 'Waiting for dispatch'),
    ('assigned', 'Trip planned'),
    ('loaded', 'Loaded'),
    ('delivering', 'In transit'),
    ('done', 'Delivered'),
    ('cancelled', 'Delivery cancelled'),
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Franchise store',
        index=True,
        tracking=True,
        help="Franchise store receiving the goods. Copied from the SO on confirm; "
             "can be set manually for internal pickings.",
    )
    area_id = fields.Many2one(
        'res.area',
        string='Area',
        related='franchise_id.area_id',
        store=True,
        readonly=True,
        index=True,
    )
    delivery_sequence = fields.Integer(
        string='Delivery sequence',
        default=10,
        help='Delivery sequence within the batch.',
    )
    vehicle_id = fields.Many2one(
        'wujia.fleet.management',
        string='Delivery vehicle',
        related='batch_id.vehicle_id',
        store=True,
        readonly=True,
        index=True,
    )
    provider_id = fields.Many2one(
        'wujia.fleet.provider',
        string='Carrier',
        related='vehicle_id.provider_id',
        store=True,
        readonly=True,
        index=True,
    )
    delivery_status = fields.Selection(
        DELIVERY_STATUS,
        string='Delivery status',
        default='pending',
        tracking=True,
        index=True,
        help='Dispatch status — it does NOT replace the standard picking state.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    shipping_cost = fields.Monetary(
        string='Shipping cost (allocated)',
        currency_field='currency_id',
        compute='_compute_shipping_allocation',
        store=True,
        help="Shipping cost allocated in proportion to the picking planned_weight "
             "within the total planned_weight of the batch.",
    )
    drop_fee = fields.Monetary(
        string='Drop fee',
        currency_field='currency_id',
        compute='_compute_shipping_allocation',
        store=True,
    )
    delivery_note = fields.Text(string='Delivery note')

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
