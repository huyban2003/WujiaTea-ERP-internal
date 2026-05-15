from odoo import api, fields, models


CATEGORIES = [
    ('order', 'Đặt hàng'),
    ('delivery', 'Giao hàng'),
    ('product', 'Sản phẩm'),
    ('pos', 'POS'),
    ('operation', 'Vận hành'),
    ('account', 'Tài khoản / Mật khẩu'),
    ('other', 'Khác'),
]

PRIORITIES = [
    ('low', 'Thấp'),
    ('normal', 'Bình thường'),
    ('high', 'Cao'),
    ('urgent', 'Khẩn'),
]

STATES = [
    ('new', 'Mới'),
    ('in_progress', 'Đang xử lý'),
    ('resolved', 'Đã giải quyết'),
    ('closed', 'Đã đóng'),
]


class WujiaSupportTicket(models.Model):
    """Skeleton — yêu cầu hỗ trợ từ cửa hàng nhượng quyền.

    Có mail.thread + activity → cho phép HQ và cửa hàng trao đổi qua chatter."""

    _name = 'wujia.support.ticket'
    _description = 'Wujia Support Ticket'
    _order = 'create_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Mã ticket', readonly=True, copy=False, default='/')
    subject = fields.Char(string='Tiêu đề', required=True, tracking=True)
    description = fields.Text(string='Mô tả chi tiết')
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng',
        required=True, index=True, ondelete='restrict', tracking=True,
    )
    user_id = fields.Many2one(
        'res.users', string='Người gửi',
        default=lambda self: self.env.user, required=True, index=True,
    )
    category = fields.Selection(
        CATEGORIES, string='Phân loại',
        default='other', required=True, index=True, tracking=True,
    )
    priority = fields.Selection(
        PRIORITIES, string='Mức độ',
        default='normal', required=True, tracking=True,
    )
    state = fields.Selection(
        STATES, string='Trạng thái',
        default='new', required=True, index=True, tracking=True,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment', 'wujia_support_ticket_attachment_rel',
        'ticket_id', 'attachment_id',
        string='File đính kèm',
    )
    handler_user_id = fields.Many2one(
        'res.users', string='Người xử lý (HQ)',
        domain="[('share', '=', False)]",
        tracking=True,
    )
    resolved_date = fields.Datetime(string='Ngày giải quyết', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.support.ticket'
                ) or '/'
        return super().create(vals_list)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'resolved':
            vals.setdefault('resolved_date', fields.Datetime.now())
        return super().write(vals)

    def action_set_in_progress(self):
        self.filtered(lambda t: t.state == 'new').write({'state': 'in_progress'})

    def action_set_resolved(self):
        self.filtered(lambda t: t.state in ('new', 'in_progress')).write({
            'state': 'resolved',
            'resolved_date': fields.Datetime.now(),
        })

    def action_set_closed(self):
        self.filtered(lambda t: t.state != 'closed').write({'state': 'closed'})
