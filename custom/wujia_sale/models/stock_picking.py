from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    planned_weight = fields.Float(
        string='Khối lượng dự kiến',
        compute='_compute_planned_weight',
        store=True,
        digits='Stock Weight',
        help='Tổng khối lượng dự kiến của phiếu xuất = sum(move_ids.planned_weight). '
             'Đây là nguồn chính để sắp batch/chuyến xe.',
    )
    done_weight = fields.Float(
        string='Khối lượng đã xuất',
        compute='_compute_done_weight',
        store=True,
        digits='Stock Weight',
    )

    @api.depends('move_ids.planned_weight')
    def _compute_planned_weight(self):
        for pick in self:
            pick.planned_weight = sum(pick.move_ids.mapped('planned_weight'))

    @api.depends('move_ids.done_weight')
    def _compute_done_weight(self):
        for pick in self:
            pick.done_weight = sum(pick.move_ids.mapped('done_weight'))
