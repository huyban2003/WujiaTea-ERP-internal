from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


STATE_SELECTION = [
    ('draft', 'Nháp'),
    ('submitted', 'Đã gửi'),
    ('reviewing', 'Đang xét'),
    ('approved', 'Đã phê duyệt'),
    ('processing', 'Đang xử lý'),
    ('done', 'Đã xử lý'),
    ('rejected', 'Từ chối'),
    ('cancelled', 'Đã huỷ'),
]

RESOLUTION_SELECTION = [
    ('exchange', 'Đổi hàng'),
    ('return', 'Trả hàng'),
    ('compensation', 'Bù hàng'),
    ('refuse', 'Từ chối'),
]

MIN_IMAGES_BEFORE_SEND = 3


class WujiaReturnRequest(models.Model):
    """Yêu cầu đổi trả / bù hàng — 1 sản phẩm/phiếu (BA spec K, model/field tab).

    Sprint K1: redesign từ multi-line → single-product header + approval block +
    allocation tracking (compute). Xử lý bù hàng (wizard + SO 0đ) = K2.
    """

    _name = 'wujia.return.request'
    _description = 'Wujia Return Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'

    name = fields.Char(
        string='Mã yêu cầu', required=True, copy=False,
        readonly=True, default=lambda self: '/', tracking=True,
    )
    request_date = fields.Datetime(
        string='Ngày yêu cầu', default=fields.Datetime.now,
        index=True, required=True, readonly=True, tracking=True,
    )
    requester_user_id = fields.Many2one(
        'res.users', string='Người tạo',
        default=lambda self: self.env.user, readonly=True, index=True,
        tracking=True,
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng nhượng quyền',
        required=True, index=True, ondelete='restrict', tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Partner cửa hàng',
        related='franchise_id.partner_id', store=True, index=True,
    )

    # --- Đơn hàng gốc (1 sản phẩm/phiếu) ---
    sale_order_id = fields.Many2one(
        'sale.order', string='Đơn hàng gốc',
        domain="[('franchise_id', '=', franchise_id)]",
        ondelete='restrict', tracking=True,
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Dòng đơn hàng',
        domain="[('order_id', '=', sale_order_id)]",
        ondelete='restrict', tracking=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Sản phẩm',
        related='sale_order_line_id.product_id', store=True,
        readonly=True, index=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom', string='ĐVT đơn gốc',
        related='sale_order_line_id.product_uom_id', store=True, readonly=True,
    )
    batch_id = fields.Many2one(
        'stock.picking.batch', string='Chuyến giao',
        related='sale_order_id.batch_id', store=True, readonly=True, index=True,
    )
    picking_id = fields.Many2one(
        'stock.picking', string='Phiếu giao', ondelete='set null',
    )

    # --- Nội dung yêu cầu ---
    request_qty = fields.Float(
        string='Số lượng yêu cầu', default=1.0,
        digits='Product Unit of Measure',
    )
    request_uom_id = fields.Many2one(
        'uom.uom', string='ĐVT yêu cầu', required=True,
        help='Đơn vị nhượng quyền ghi nhận quyền lợi (quy đổi được với ĐVT quyền lợi bù).',
    )
    opening_datetime = fields.Datetime(string='Thời gian mở hàng', required=True)
    production_date = fields.Date(string='Ngày sản xuất')
    issue_type_id = fields.Many2one(
        'wujia.return.issue.type', string='Loại lỗi',
        required=True, ondelete='restrict', tracking=True,
    )
    note = fields.Text(string='Ghi chú từ cửa hàng')
    image_attachment_ids = fields.Many2many(
        'ir.attachment', 'wujia_return_image_rel',
        'request_id', 'attachment_id', string='Ảnh minh chứng',
        help='Tối thiểu 3 ảnh khi gửi yêu cầu (BA POR-036).',
    )
    video_attachment_ids = fields.Many2many(
        'ir.attachment', 'wujia_return_video_rel',
        'request_id', 'attachment_id', string='Video minh chứng',
    )

    # --- Workflow / xử lý ---
    state = fields.Selection(
        STATE_SELECTION, string='Trạng thái',
        default='submitted', required=True, index=True, tracking=True,
    )
    backend_note = fields.Text(string='Ghi chú nội bộ')
    reject_reason = fields.Text(string='Lý do từ chối', tracking=True)
    resolution_type = fields.Selection(
        RESOLUTION_SELECTION, string='Phương án xử lý', tracking=True,
    )
    resolved_date = fields.Datetime(string='Ngày hoàn tất', readonly=True, tracking=True)

    # --- Duyệt ---
    approved_qty = fields.Float(
        string='SL duyệt bù', digits='Product Unit of Measure', tracking=True,
    )
    approved_uom_id = fields.Many2one('uom.uom', string='ĐVT duyệt')
    approved_by_id = fields.Many2one('res.users', string='Người duyệt', readonly=True)
    approved_date = fields.Datetime(string='Ngày duyệt', readonly=True)
    approval_note = fields.Text(string='Ghi chú duyệt')
    compensation_product_id = fields.Many2one(
        'product.product', string='Sản phẩm bù (snapshot)',
    )
    compensation_delivery_uom_id = fields.Many2one(
        'uom.uom', string='ĐVT giao bù (snapshot)',
    )
    compensation_unit_qty = fields.Float(
        string='SL quyền lợi / đơn vị giao', digits='Product Unit of Measure',
        help='Số lượng quyền lợi tương ứng một đơn vị giao bù (vd 1 bịch = 10 kg).',
    )
    compensation_policy = fields.Selection(
        [('exact', 'Bù đúng số lượng'), ('accumulate', 'Cộng dồn nguyên kiện')],
        string='Chính sách bù (snapshot)',
    )

    # --- Theo dõi phân bổ bù (K2 populate qua allocation) ---
    allocation_ids = fields.One2many(
        'wujia.compensation.allocation', 'request_id', string='Phân bổ bù',
    )
    allocated_qty = fields.Float(
        string='Đã phân bổ', compute='_compute_allocation_totals', store=True,
        digits='Product Unit of Measure',
    )
    compensated_qty = fields.Float(
        string='Đã bù thực tế', compute='_compute_allocation_totals', store=True,
        digits='Product Unit of Measure',
    )
    unallocated_qty = fields.Float(
        string='Chưa phân bổ', compute='_compute_allocation_totals', store=True,
        digits='Product Unit of Measure',
    )
    remaining_qty = fields.Float(
        string='Còn thiếu', compute='_compute_allocation_totals', store=True,
        digits='Product Unit of Measure',
    )
    compensation_status = fields.Selection(
        [('none', 'Chưa phân bổ'), ('allocated', 'Đã phân bổ'),
         ('partial', 'Bù một phần'), ('done', 'Đã bù đủ')],
        string='Tình trạng bù', compute='_compute_allocation_totals', store=True,
    )
    compensation_so_ids = fields.Many2many(
        'sale.order', string='SO bù hàng',
        compute='_compute_compensation_so_ids',
    )
    compensation_so_count = fields.Integer(
        string='Số SO bù', compute='_compute_compensation_so_ids',
    )

    @api.depends('allocation_ids.allocated_qty', 'allocation_ids.released_qty',
                 'allocation_ids.delivered_qty', 'allocation_ids.state',
                 'approved_qty')
    def _compute_allocation_totals(self):
        # 1 query read_group thay vì loop từng allocation (perf 1500 user).
        data = {}
        if self.ids:
            groups = self.env['wujia.compensation.allocation'].sudo()._read_group(
                domain=[('request_id', 'in', self.ids),
                        ('state', '!=', 'cancel')],
                groupby=['request_id'],
                aggregates=['allocated_qty:sum', 'released_qty:sum',
                            'delivered_qty:sum'],
            )
            for req, alloc, rel, deliv in groups:
                data[req.id] = (alloc or 0.0, rel or 0.0, deliv or 0.0)
        for rec in self:
            alloc, rel, deliv = data.get(rec.id, (0.0, 0.0, 0.0))
            rec.allocated_qty = alloc - rel
            rec.compensated_qty = deliv
            rec.unallocated_qty = (rec.approved_qty or 0.0) - rec.allocated_qty
            rec.remaining_qty = (rec.approved_qty or 0.0) - rec.compensated_qty
            if not rec.allocation_ids:
                rec.compensation_status = 'none'
            elif rec.remaining_qty <= 0:
                rec.compensation_status = 'done'
            elif rec.compensated_qty > 0:
                rec.compensation_status = 'partial'
            else:
                rec.compensation_status = 'allocated'

    @api.depends('allocation_ids.sale_order_id')
    def _compute_compensation_so_ids(self):
        for rec in self:
            sos = rec.allocation_ids.mapped('sale_order_id')
            rec.compensation_so_ids = sos
            rec.compensation_so_count = len(sos)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.return.request') or '/'
        return super().create(vals_list)

    @api.constrains('sale_order_line_id', 'sale_order_id')
    def _check_line_belongs_to_order(self):
        for rec in self:
            if rec.sale_order_line_id and rec.sale_order_id and \
                    rec.sale_order_line_id.order_id != rec.sale_order_id:
                raise ValidationError(_(
                    "Dòng sản phẩm phải thuộc đơn hàng gốc đã chọn."))

    @api.onchange('resolution_type', 'product_id')
    def _onchange_prefill_compensation(self):
        """Gợi ý snapshot bù từ cấu hình product khi HQ chọn phương án bù.

        Chỉ điền ô còn trống → HQ sửa tay không bị ghi đè.
        """
        for rec in self:
            if rec.resolution_type != 'compensation' or not rec.product_id:
                continue
            product = rec.product_id
            if not rec.compensation_product_id:
                rec.compensation_product_id = (
                    product.compensation_product_id or product)
            if not rec.compensation_delivery_uom_id:
                rec.compensation_delivery_uom_id = (
                    product.compensation_delivery_uom_id or product.uom_id)
            if not rec.compensation_unit_qty:
                rec.compensation_unit_qty = product.compensation_unit_qty
            if not rec.compensation_policy:
                rec.compensation_policy = product.compensation_policy
            if not rec.approved_uom_id:
                rec.approved_uom_id = (
                    product.compensation_claim_uom_id or rec.request_uom_id)
            if not rec.approved_qty:
                rec.approved_qty = rec.request_qty

    # ============================================================ workflow
    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if len(rec.image_attachment_ids) < MIN_IMAGES_BEFORE_SEND:
                raise ValidationError(_(
                    "Cần ít nhất %s ảnh minh chứng trước khi gửi.",
                    MIN_IMAGES_BEFORE_SEND))
            rec.state = 'submitted'
            rec.message_post(body=_("Yêu cầu đã được gửi."))

    def action_start_review(self):
        for rec in self:
            if rec.state == 'submitted':
                rec.state = 'reviewing'

    def action_approve(self):
        for rec in self:
            if rec.state not in ('submitted', 'reviewing'):
                raise ValidationError(_("Chỉ duyệt được yêu cầu đã gửi/đang xét."))
            if rec.approved_qty <= 0:
                raise ValidationError(_("Nhập SL duyệt bù (> 0) trước khi duyệt."))
            if not rec.resolution_type:
                raise ValidationError(_("Chọn phương án xử lý trước khi duyệt."))
            rec.write({
                'state': 'approved',
                'approved_by_id': self.env.uid,
                'approved_date': fields.Datetime.now(),
            })
            rec.message_post(body=_("Yêu cầu đã được phê duyệt."))

    def action_reject(self):
        for rec in self:
            if rec.state in ('done', 'cancelled', 'rejected'):
                raise ValidationError(_("Yêu cầu này không thể từ chối."))
            if not rec.reject_reason:
                raise ValidationError(_("Nhập lý do từ chối trước khi từ chối."))
            rec.write({'state': 'rejected', 'resolved_date': fields.Datetime.now()})
            rec.message_post(body=_("Yêu cầu bị từ chối: %s", rec.reject_reason))

    def action_cancel(self):
        for rec in self:
            if rec.state in ('done', 'cancelled'):
                raise ValidationError(_("Yêu cầu này không thể huỷ."))
            rec.state = 'cancelled'
            rec.message_post(body=_("Yêu cầu đã bị huỷ."))

    def action_mark_done(self):
        for rec in self:
            if rec.state != 'approved' or rec.resolution_type == 'compensation':
                raise ValidationError(_(
                    "Chỉ đánh dấu hoàn thành cho yêu cầu đã duyệt không phải bù hàng."))
            rec.write({'state': 'done', 'resolved_date': fields.Datetime.now()})
            rec.message_post(body=_("Yêu cầu đã hoàn tất."))

    def _apply_compensation_delivery(self):
        """Chuyển processing→done khi đã bù đủ (gọi từ hook stock.picking).

        Rollup số liệu do `_compute_allocation_totals` lo; đây chỉ chuyển state
        sau khi delivered_qty của allocation được cập nhật từ giao thực tế.
        """
        for rec in self:
            if rec.state != 'processing':
                continue
            if rec.approved_qty > 0 and rec.remaining_qty <= 1e-6:
                rec.write({'state': 'done', 'resolved_date': fields.Datetime.now()})
                rec.message_post(body=_("Đã bù đủ số lượng — yêu cầu hoàn tất."))

    def action_view_compensation_sos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('SO bù hàng'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.compensation_so_ids.ids)],
        }
