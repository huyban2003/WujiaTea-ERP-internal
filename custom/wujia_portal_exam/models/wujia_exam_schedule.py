from odoo import fields, models


SCHEDULE_STATE = [
    ('open', 'Đang mở đăng ký'),
    ('closed', 'Đã đóng đăng ký'),
    ('done', 'Đã thi xong'),
    ('cancelled', 'Đã hủy'),
]


class WujiaExamSchedule(models.Model):
    """Skeleton — lịch thi / kiểm tra kiến thức cho cửa hàng nhượng quyền."""

    _name = 'wujia.exam.schedule'
    _description = 'Wujia Exam Schedule'
    _order = 'exam_date desc, id desc'

    name = fields.Char(string='Tên kỳ thi', required=True)
    exam_date = fields.Datetime(
        string='Thời gian thi', required=True, index=True,
    )
    location = fields.Char(string='Địa điểm')
    description = fields.Text(string='Nội dung / mô tả')
    franchise_ids = fields.Many2many(
        'wujia.franchise.management',
        'wujia_exam_schedule_franchise_rel',
        'schedule_id', 'franchise_id',
        string='Cửa hàng được mời',
        help='Để trống = mở cho tất cả cửa hàng đang hoạt động.',
    )
    max_participants = fields.Integer(string='Số người tối đa', default=0)
    state = fields.Selection(
        SCHEDULE_STATE, string='Trạng thái',
        default='open', required=True, index=True,
    )
    registration_count = fields.Integer(
        string='SL đã đăng ký', compute='_compute_registration_count',
    )
    active = fields.Boolean(default=True)

    def _compute_registration_count(self):
        Reg = self.env['wujia.exam.registration'].sudo()
        groups = Reg._read_group(
            domain=[('schedule_id', 'in', self.ids)],
            groupby=['schedule_id'], aggregates=['__count'],
        )
        mapping = {sched.id: count for sched, count in groups}
        for rec in self:
            rec.registration_count = mapping.get(rec.id, 0)
