from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WujiaCompensationAllocation(models.Model):
    """Bản ghi phân bổ bù hàng — 1 request × 1 dòng SO bù (BA spec K).

    Persistent, hiển thị dưới dạng tab trong wujia.return.request (không menu
    riêng). Sprint K1 chỉ định nghĩa model; wizard tạo allocation + cập nhật
    delivered_qty từ picking = K2.
    """

    _name = 'wujia.compensation.allocation'
    _description = 'Wujia Compensation Allocation'
    _order = 'allocation_date desc, id desc'

    name = fields.Char(
        string='Mã phân bổ', required=True, copy=False,
        readonly=True, default=lambda self: '/',
    )
    request_id = fields.Many2one(
        'wujia.return.request', string='Yêu cầu bù',
        required=True, ondelete='cascade', index=True,
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng',
        related='request_id.franchise_id', store=True, readonly=True, index=True,
    )
    company_id = fields.Many2one(
        'res.company', string='Công ty',
        default=lambda self: self.env.company, readonly=True, index=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order', string='SO bù', readonly=True, ondelete='restrict', index=True,
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Dòng SO bù', readonly=True, ondelete='restrict',
        index=True,
    )
    allocated_qty = fields.Float(
        string='SL phân bổ', required=True, digits='Product Unit of Measure',
    )
    allocation_uom_id = fields.Many2one(
        'uom.uom', string='ĐVT phân bổ', required=True,
    )
    delivered_qty = fields.Float(
        string='SL đã giao', default=0.0, digits='Product Unit of Measure',
    )
    released_qty = fields.Float(
        string='SL hoàn lại', default=0.0, digits='Product Unit of Measure',
    )
    open_qty = fields.Float(
        string='SL còn mở', compute='_compute_open_qty', store=True,
        digits='Product Unit of Measure',
    )
    state = fields.Selection(
        [('allocated', 'Đã phân bổ'), ('partial', 'Giao một phần'),
         ('done', 'Đã giao'), ('cancel', 'Đã huỷ')],
        string='Trạng thái', default='allocated', required=True,
    )
    allocation_date = fields.Datetime(
        string='Ngày phân bổ', default=fields.Datetime.now, readonly=True,
    )
    delivered_date = fields.Datetime(string='Ngày giao', readonly=True)
    release_reason = fields.Text(string='Lý do hoàn lại')

    _check_allocated_positive = models.Constraint(
        'CHECK(allocated_qty > 0)',
        'SL phân bổ phải lớn hơn 0.',
    )
    _check_delivered_nonneg = models.Constraint(
        'CHECK(delivered_qty >= 0)',
        'SL đã giao không được âm.',
    )
    _check_released_nonneg = models.Constraint(
        'CHECK(released_qty >= 0)',
        'SL hoàn lại không được âm.',
    )
    _check_delivered_released_le_allocated = models.Constraint(
        'CHECK(delivered_qty + released_qty <= allocated_qty)',
        'Tổng đã giao + hoàn lại không được vượt SL phân bổ.',
    )

    @api.depends('allocated_qty', 'delivered_qty', 'released_qty')
    def _compute_open_qty(self):
        for rec in self:
            rec.open_qty = rec.allocated_qty - rec.delivered_qty - rec.released_qty

    @api.constrains('allocated_qty', 'released_qty', 'request_id', 'state')
    def _check_not_over_approved(self):
        for rec in self.filtered(lambda a: a.state != 'cancel'):
            siblings = rec.request_id.allocation_ids.filtered(
                lambda a: a.state != 'cancel')
            total = sum(a.allocated_qty - a.released_qty for a in siblings)
            if total > rec.request_id.approved_qty + 1e-6:
                raise ValidationError(_(
                    "Tổng phân bổ của yêu cầu '%s' vượt số lượng đã duyệt.",
                    rec.request_id.name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.compensation.allocation') or '/'
        return super().create(vals_list)
