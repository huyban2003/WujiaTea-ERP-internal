from odoo import _, api, fields, models


DELIVERY_BATCH_STATUS = [
    ('draft', 'Nháp'),
    ('assigned', 'Đã gán xe'),
    ('loading', 'Đang chất hàng'),
    ('delivering', 'Đang giao'),
    ('done', 'Đã giao xong'),
    ('cancelled', 'Hủy chuyến'),
]


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    vehicle_id = fields.Many2one(
        'wujia.fleet.management',
        string='Xe',
        domain=[('active', '=', True)],
        tracking=True,
        help='Xe được chọn cho chuyến.',
    )
    provider_id = fields.Many2one(
        'wujia.fleet.provider',
        string='Đội xe',
        related='vehicle_id.provider_id',
        store=True,
        readonly=True,
    )
    fleet_type_id = fields.Many2one(
        'wujia.fleet.type',
        string='Loại xe',
        related='vehicle_id.fleet_type_id',
        store=True,
        readonly=True,
    )
    vehicle_capacity_ton = fields.Float(
        string='Tải trọng (tấn)',
        related='vehicle_id.payload_capacity_ton',
        store=True,
        readonly=True,
        digits=(10, 2),
    )
    vehicle_capacity_kg = fields.Float(
        string='Tải trọng (kg)',
        related='vehicle_id.max_payload_kg',
        store=True,
        readonly=True,
        digits='Stock Weight',
    )

    capacity_usage_percent = fields.Float(
        string='% sử dụng tải trọng',
        compute='_compute_capacity_usage',
        store=True,
        digits=(8, 2),
    )
    is_over_capacity = fields.Boolean(
        string='Vượt tải',
        compute='_compute_capacity_usage',
        store=True,
    )
    over_capacity_weight = fields.Float(
        string='Khối lượng vượt tải (kg)',
        compute='_compute_capacity_usage',
        store=True,
        digits='Stock Weight',
    )

    franchise_count = fields.Integer(
        string='Số cửa hàng',
        compute='_compute_franchise_area',
        store=True,
    )
    area_ids = fields.Many2many(
        'res.area',
        'wujia_batch_area_rel',
        'batch_id',
        'area_id',
        string='Khu vực',
        compute='_compute_franchise_area',
        store=True,
    )

    pricelist_id = fields.Many2one(
        'wujia.fleet.pricelist',
        string='Bảng giá',
        compute='_compute_pricelist_id',
        store=True,
        readonly=False,
        tracking=True,
        help='Bảng giá vận chuyển. Auto-suggest theo loại xe + đội xe + ngày; '
             'có thể override thủ công.',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    shipping_cost = fields.Monetary(
        string='Chi phí vận chuyển',
        currency_field='currency_id',
        compute='_compute_shipping_cost',
        store=True,
        readonly=False,
        help='Auto-tính từ pricelist khi đủ vehicle + area; có thể override.',
    )
    drop_fee_total = fields.Monetary(
        string='Tổng phí drop',
        currency_field='currency_id',
        compute='_compute_shipping_cost',
        store=True,
        readonly=False,
    )
    total_shipping_cost = fields.Monetary(
        string='Tổng chi phí giao hàng',
        currency_field='currency_id',
        compute='_compute_total_shipping_cost',
        store=True,
    )

    planned_departure = fields.Datetime(string='Dự kiến xuất phát')
    actual_departure = fields.Datetime(string='Thực tế xuất phát')

    delivery_batch_status = fields.Selection(
        DELIVERY_BATCH_STATUS,
        string='Trạng thái điều phối',
        default='draft',
        tracking=True,
        help='Song song với state chuẩn — không thay state Odoo.',
    )
    delivery_note = fields.Text(string='Ghi chú điều phối')

    # ===========================================================
    # Compute
    # ===========================================================
    @api.depends('planned_weight', 'vehicle_capacity_kg')
    def _compute_capacity_usage(self):
        for batch in self:
            cap = batch.vehicle_capacity_kg or 0.0
            planned = batch.planned_weight or 0.0
            if cap <= 0:
                batch.capacity_usage_percent = 0.0
                batch.is_over_capacity = False
                batch.over_capacity_weight = 0.0
            else:
                batch.capacity_usage_percent = (planned / cap) * 100.0
                batch.is_over_capacity = planned > cap
                batch.over_capacity_weight = max(planned - cap, 0.0)

    @api.depends('picking_ids.franchise_id', 'picking_ids.area_id')
    def _compute_franchise_area(self):
        for batch in self:
            franchises = batch.picking_ids.mapped('franchise_id')
            areas = batch.picking_ids.mapped('area_id')
            batch.franchise_count = len(franchises)
            batch.area_ids = [(6, 0, areas.ids)]

    @api.depends('vehicle_id', 'fleet_type_id', 'provider_id', 'scheduled_date', 'area_ids')
    def _compute_pricelist_id(self):
        Pricelist = self.env['wujia.fleet.pricelist']
        for batch in self:
            if batch.pricelist_id:
                # Người dùng đã chọn → giữ nguyên (readonly=False).
                continue
            if not batch.fleet_type_id:
                batch.pricelist_id = False
                continue
            ref_date = (batch.scheduled_date and batch.scheduled_date.date()) or fields.Date.context_today(batch)
            domain = [
                ('state', '=', 'active'),
                ('fleet_type_id', '=', batch.fleet_type_id.id),
                ('date_from', '<=', ref_date),
                '|', ('date_to', '=', False), ('date_to', '>=', ref_date),
            ]
            if batch.provider_id:
                domain.extend(['|', ('provider_id', '=', batch.provider_id.id), ('provider_id', '=', False)])
            else:
                domain.append(('provider_id', '=', False))
            batch.pricelist_id = Pricelist.search(domain, order='sequence, id', limit=1)

    @api.depends(
        'pricelist_id',
        'pricelist_id.line_ids',
        'pricelist_id.default_drop_fee',
        'area_ids',
        'picking_ids.area_id',
    )
    def _compute_shipping_cost(self):
        for batch in self:
            pl = batch.pricelist_id
            if not pl or not batch.area_ids:
                batch.shipping_cost = 0.0
                batch.drop_fee_total = 0.0
                continue
            batch_area_ids = set(batch.area_ids.ids)
            matched_lines = pl.line_ids.filtered(
                lambda l: l.active and (set(l.area_ids.ids) & batch_area_ids)
            )
            # Cước cơ bản: lấy giá cao nhất trong các line match.
            batch.shipping_cost = max(matched_lines.mapped('price'), default=0.0)
            # Drop fee: với mỗi picking, cộng line.drop_fee match (nếu không có dùng default).
            drop_total = 0.0
            for pick in batch.picking_ids:
                if not pick.area_id:
                    continue
                pick_lines = matched_lines.filtered(lambda l: pick.area_id.id in l.area_ids.ids)
                if pick_lines:
                    drop_total += sum(pick_lines.mapped('drop_fee'))
                else:
                    drop_total += pl.default_drop_fee
            batch.drop_fee_total = drop_total

    @api.depends('shipping_cost', 'drop_fee_total')
    def _compute_total_shipping_cost(self):
        for batch in self:
            batch.total_shipping_cost = (batch.shipping_cost or 0.0) + (batch.drop_fee_total or 0.0)

    # ===========================================================
    # Actions trạng thái điều phối
    # ===========================================================
    def action_delivery_assign(self):
        for batch in self:
            batch.delivery_batch_status = 'assigned'

    def action_delivery_loading(self):
        for batch in self:
            batch.delivery_batch_status = 'loading'

    def action_delivery_start(self):
        for batch in self:
            batch.delivery_batch_status = 'delivering'
            batch.actual_departure = fields.Datetime.now()
            # Đẩy delivery_status của các picking → delivering.
            batch.picking_ids.filtered(
                lambda p: p.delivery_status not in ('done', 'cancelled')
            ).write({'delivery_status': 'delivering'})

    def action_delivery_done(self):
        for batch in self:
            batch.delivery_batch_status = 'done'

    def action_delivery_cancel(self):
        for batch in self:
            batch.delivery_batch_status = 'cancelled'
