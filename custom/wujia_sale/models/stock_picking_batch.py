from odoo import api, fields, models


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    planned_weight = fields.Float(
        string='Khối lượng dự kiến',
        compute='_compute_planned_weight',
        store=True,
        digits='Stock Weight',
        help='Tổng khối lượng dự kiến của batch = sum(picking_ids.planned_weight). '
             'Dùng để chọn xe phù hợp.',
    )
    done_weight = fields.Float(
        string='Khối lượng đã xuất',
        compute='_compute_done_weight',
        store=True,
        digits='Stock Weight',
    )

    @api.depends('picking_ids.planned_weight')
    def _compute_planned_weight(self):
        for batch in self:
            batch.planned_weight = sum(batch.picking_ids.mapped('planned_weight'))

    @api.depends('picking_ids.done_weight')
    def _compute_done_weight(self):
        for batch in self:
            batch.done_weight = sum(batch.picking_ids.mapped('done_weight'))
