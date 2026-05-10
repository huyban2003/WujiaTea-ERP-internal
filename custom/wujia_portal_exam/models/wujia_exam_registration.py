from odoo import api, fields, models


REG_STATE = [
    ('registered', 'Đã đăng ký'),
    ('checked_in', 'Đã có mặt'),
    ('cancelled', 'Đã hủy'),
]


class WujiaExamRegistration(models.Model):
    """Skeleton — đăng ký dự thi của user × schedule."""

    _name = 'wujia.exam.registration'
    _description = 'Wujia Exam Registration'
    _order = 'register_date desc, id desc'

    name = fields.Char(string='Mã đăng ký', readonly=True, default='/')
    schedule_id = fields.Many2one(
        'wujia.exam.schedule', string='Kỳ thi',
        required=True, index=True, ondelete='cascade',
    )
    user_id = fields.Many2one(
        'res.users', string='Người dự thi',
        required=True, index=True,
        default=lambda self: self.env.user,
    )
    franchise_id = fields.Many2one(
        'wujia.franchise.management', string='Cửa hàng',
        required=True, index=True, ondelete='restrict',
    )
    register_date = fields.Datetime(
        string='Ngày đăng ký', default=fields.Datetime.now,
    )
    state = fields.Selection(
        REG_STATE, string='Trạng thái',
        default='registered', required=True, index=True,
    )
    note = fields.Char(string='Ghi chú')

    _sql_constraints = [
        ('uniq_user_schedule', 'unique(user_id, schedule_id)',
         'Mỗi user chỉ đăng ký 1 lần cho 1 kỳ thi.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'wujia.exam.registration'
                ) or '/'
        return super().create(vals_list)
