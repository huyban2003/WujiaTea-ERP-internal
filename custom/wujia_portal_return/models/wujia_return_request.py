from odoo import api, fields, models


STATE_SELECTION = [
    ('draft', 'Nháp'),
    ('sent', 'Đã gửi'),
    ('approved', 'Đã duyệt'),
    ('rejected', 'Từ chối'),
    ('done', 'Hoàn thành'),
]


class WujiaReturnRequest(models.Model):
    """Skeleton model — yêu cầu đổi trả từ cửa hàng nhượng quyền.

    Chỉ field tối thiểu để render template list/form/detail. Workflow approve,
    auto-create SO 0đ bù hàng (POR-043) sẽ làm sprint sau.
    """

    _name = 'wujia.return.request'
    _description = 'Wujia Return Request'
    _order = 'request_date desc, id desc'

    name = fields.Char(string='Mã yêu cầu', required=True, copy=False,
                       readonly=True, default=lambda self: '/')
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng nhượng quyền',
        required=True, index=True, ondelete='restrict',
    )
    partner_id = fields.Many2one(
        'res.partner', string='Partner cửa hàng',
        related='franchise_id.partner_id', store=True, index=True,
    )
    order_id = fields.Many2one(
        'sale.order', string='Đơn hàng gốc',
        domain="[('franchise_id', '=', franchise_id)]",
    )
    request_date = fields.Datetime(
        string='Ngày yêu cầu', default=fields.Datetime.now,
        index=True, required=True,
    )
    expected_delivery_date = fields.Date(string='Ngày giao dự kiến')
    state = fields.Selection(
        STATE_SELECTION, string='Trạng thái',
        default='draft', required=True, index=True,
    )
    error_id = fields.Many2one(
        'wujia.return.error.type', string='Loại lỗi',
        ondelete='restrict',
    )
    note = fields.Text(string='Ghi chú')
    refuse_reason = fields.Text(string='Lý do từ chối')
    image_ids = fields.Many2many(
        'ir.attachment', 'wujia_return_image_rel',
        'request_id', 'attachment_id',
        string='Ảnh minh chứng',
        help='Tối thiểu 3 ảnh khi gửi yêu cầu (BA spec POR-036).',
    )
    line_ids = fields.One2many(
        'wujia.return.request.line', 'request_id',
        string='Sản phẩm cần đổi trả', copy=True,
    )
    created_by_user_id = fields.Many2one(
        'res.users', string='Người tạo',
        default=lambda self: self.env.user, readonly=True, index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.return.request'
                ) or '/'
        return super().create(vals_list)
