from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_portal_order = fields.Boolean(
        string='Đơn từ Portal',
        default=False,
        index=True,
        tracking=True,
        help='Đánh dấu đơn được tạo từ portal (phân biệt với đơn admin tạo manual).',
    )
    franchise_partner_id = fields.Many2one(
        'res.partner',
        string='Partner cửa hàng',
        domain="[('is_franchise', '=', True)]",
        index=True,
        tracking=True,
        help='Partner đại diện cửa hàng nhượng quyền sở hữu đơn — bắt buộc khi is_portal_order=True.',
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management',
        string='Cửa hàng nhượng quyền',
        index=True,
        tracking=True,
        help='Cửa hàng sở hữu đơn — bắt buộc khi is_portal_order=True.',
    )
    portal_requester_user_id = fields.Many2one(
        'res.users',
        string='Người tạo (portal)',
        readonly=True,
        index=True,
        help='User portal trực tiếp bấm tạo đơn. Set tại thời điểm tạo, không đổi sau đó (audit trail).',
    )
    portal_member_id = fields.Many2one(
        'wujia.franchise.member',
        string='Member tạo đơn',
        readonly=True,
        ondelete='restrict',
        help='Snapshot membership user × cửa hàng tại thời điểm tạo đơn.',
    )
    area_id = fields.Many2one(
        'res.area',
        string='Khu vực',
        related='franchise_id.area_id',
        store=True,
        readonly=True,
    )
    portal_delivery_street = fields.Char(string='Địa chỉ giao (portal)')
    portal_delivery_phone = fields.Char(string='SĐT giao (portal)')
    portal_note = fields.Text(string='Ghi chú đơn (portal)')

    is_return_order = fields.Boolean(
        string='Đơn bù hàng',
        default=False,
        index=True,
        tracking=True,
        help='Đánh dấu SO tạo tự động từ quản lý bù/đổi trả (Function K).',
    )

    # Weight aggregate
    total_planned_weight = fields.Float(
        string='Khối lượng dự kiến',
        compute='_compute_total_planned_weight',
        store=True,
        digits='Stock Weight',
        help='Tổng khối lượng dự kiến của SO = sum(line.planned_weight). '
             'Tham khảo sớm, không phải nguồn chính sắp xe.',
    )

    batch_id = fields.Many2one(
        'stock.picking.batch',
        string='Delivery batch',
        compute='_compute_batch_id',
        store=True,
        index=True,
        help='Batch of the first non-cancelled delivery picking (id ASC). '
             'Auto-derived from picking_ids — null if SO has no picking yet.',
    )

    @api.depends('order_line.planned_weight')
    def _compute_total_planned_weight(self):
        for order in self:
            order.total_planned_weight = sum(order.order_line.mapped('planned_weight'))

    @api.depends('picking_ids.batch_id', 'picking_ids.state')
    def _compute_batch_id(self):
        # picking_ids đã prefetch sẵn qua O2m relation cache — sorted in-memory,
        # không gọi search() để tránh O(n) query khi compute trên list nhiều SO.
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda p: p.state != 'cancel' and p.batch_id
            ).sorted('id')
            order.batch_id = pickings[:1].batch_id

    @api.constrains('is_portal_order', 'franchise_id', 'franchise_partner_id')
    def _check_portal_franchise_required(self):
        for order in self:
            if order.is_portal_order:
                if not order.franchise_id:
                    raise ValidationError(_(
                        "Đơn '%s' từ portal phải có cửa hàng nhượng quyền (franchise_id).",
                        order.name or order.display_name,
                    ))
                if not order.franchise_partner_id:
                    raise ValidationError(_(
                        "Đơn '%s' từ portal phải có partner cửa hàng (franchise_partner_id).",
                        order.name or order.display_name,
                    ))

    @api.constrains('portal_requester_user_id', 'franchise_id', 'portal_member_id')
    def _check_portal_franchise_membership(self):
        """Defense in depth: nếu có portal_requester_user_id thì user phải có
        membership active trong franchise_id (controller cũng đã check)."""
        Member = self.env['wujia.franchise.member'].sudo()
        for order in self:
            if not order.portal_requester_user_id:
                continue
            if not order.franchise_id:
                raise ValidationError(_(
                    "Đơn '%s' tạo từ portal phải có cửa hàng (franchise_id).",
                    order.name or order.display_name,
                ))
            if order.portal_member_id:
                m = order.portal_member_id
                if (m.user_id != order.portal_requester_user_id
                        or m.franchise_id != order.franchise_id):
                    raise ValidationError(_(
                        "Member của đơn '%s' không khớp user/cửa hàng đã chọn.",
                        order.name or order.display_name,
                    ))
            else:
                membership = Member.find_active_membership(
                    order.portal_requester_user_id.id,
                    order.franchise_id.id,
                )
                if not membership:
                    raise ValidationError(_(
                        "User '%s' không có membership active trong cửa hàng '%s'.",
                        order.portal_requester_user_id.name,
                        order.franchise_id.display_name,
                    ))

    @api.onchange('franchise_id')
    def _onchange_franchise_id(self):
        if self.franchise_id and self.franchise_id.partner_id:
            self.franchise_partner_id = self.franchise_id.partner_id
