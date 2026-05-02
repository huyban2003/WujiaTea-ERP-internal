from odoo import fields, models, tools


class WujiaFranchiseShippingReport(models.Model):
    _name = 'wujia.franchise.shipping.report'
    _description = 'Báo cáo chi phí giao hàng theo cửa hàng (per picking)'
    _auto = False
    _order = 'report_date desc, franchise_id'

    report_date = fields.Date(string='Ngày báo cáo', readonly=True)
    franchise_id = fields.Many2one('wujia.franchise.management', string='Cửa hàng', readonly=True)
    franchise_partner_id = fields.Many2one('res.partner', string='Partner cửa hàng', readonly=True)
    area_id = fields.Many2one('res.area', string='Khu vực', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Phiếu xuất', readonly=True)
    batch_id = fields.Many2one('stock.picking.batch', string='Batch', readonly=True)
    vehicle_id = fields.Many2one('wujia.fleet.management', string='Xe', readonly=True)
    provider_id = fields.Many2one('wujia.fleet.provider', string='Đội xe', readonly=True)
    planned_weight = fields.Float(string='KL dự kiến', readonly=True, digits='Stock Weight')
    done_weight = fields.Float(string='KL thực xuất', readonly=True, digits='Stock Weight')
    shipping_cost_allocated = fields.Monetary(
        string='Cước phân bổ',
        currency_field='currency_id',
        readonly=True,
    )
    drop_fee_allocated = fields.Monetary(
        string='Phí drop phân bổ',
        currency_field='currency_id',
        readonly=True,
    )
    total_cost_allocated = fields.Monetary(
        string='Tổng chi phí phân bổ',
        currency_field='currency_id',
        readonly=True,
    )
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    p.id AS id,
                    COALESCE(p.scheduled_date::date, p.create_date::date) AS report_date,
                    p.franchise_id AS franchise_id,
                    f.partner_id AS franchise_partner_id,
                    p.area_id AS area_id,
                    p.id AS picking_id,
                    p.batch_id AS batch_id,
                    p.vehicle_id AS vehicle_id,
                    p.provider_id AS provider_id,
                    p.planned_weight AS planned_weight,
                    p.done_weight AS done_weight,
                    p.shipping_cost AS shipping_cost_allocated,
                    p.drop_fee AS drop_fee_allocated,
                    (COALESCE(p.shipping_cost, 0) + COALESCE(p.drop_fee, 0)) AS total_cost_allocated,
                    p.currency_id AS currency_id
                FROM stock_picking p
                LEFT JOIN wujia_franchise_management f ON f.id = p.franchise_id
                WHERE p.franchise_id IS NOT NULL
            )
        """ % self._table)
