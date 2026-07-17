import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

PHONE_RE = re.compile(r'^(0|\+84)[0-9]{8,10}$')

RESULT_STATE = [
    ('pending', 'Chưa có kết quả'),
    ('passed', 'Đạt'),
    ('failed', 'Không đạt'),
]


class WujiaExamRegistrationLine(models.Model):
    """1 nhân sự dự thi trong 1 phiếu đăng ký (nhập tay, free-text)."""

    _name = 'wujia.exam.registration.line'
    _description = 'Wujia Exam Registration Line'
    _order = 'registration_id, sequence, id'

    registration_id = fields.Many2one(
        'wujia.exam.registration', string='Phiếu đăng ký',
        required=True, ondelete='cascade', index=True,
    )
    sequence = fields.Integer(default=10)
    session_id = fields.Many2one(
        related='registration_id.session_id', store=True, index=True,
    )
    franchise_id = fields.Many2one(
        related='registration_id.franchise_id', store=True, index=True,
    )
    employee_name = fields.Char(string='Họ tên nhân sự', required=True)
    phone = fields.Char(string='Số điện thoại', required=True)
    birth_year = fields.Integer(string='Năm sinh')
    job_position = fields.Char(string='Vị trí công việc')
    image_1920 = fields.Image(
        string='Ảnh dự thi', max_width=1920, max_height=1920,
    )
    result = fields.Selection(
        RESULT_STATE, string='Kết quả', default='pending', required=True,
        index=True, tracking=True,
    )
    result_note = fields.Text(string='Ghi chú kết quả')
    result_entered_by_id = fields.Many2one(
        'res.users', string='Người nhập KQ', readonly=True,
    )
    result_entered_date = fields.Datetime(string='Ngày nhập KQ', readonly=True)

    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and not PHONE_RE.match(rec.phone.strip()):
                raise ValidationError(_(
                    "Số điện thoại '%s' không hợp lệ (vd 0901234567).", rec.phone))

    @api.constrains('birth_year')
    def _check_birth_year(self):
        current = fields.Date.context_today(self).year
        for rec in self:
            if rec.birth_year and not (1900 <= rec.birth_year <= current):
                raise ValidationError(_(
                    "Năm sinh phải trong khoảng 1900–%s.", current))

    def write(self, vals):
        if 'result' in vals:
            vals.setdefault('result_entered_by_id', self.env.uid)
            vals.setdefault('result_entered_date', fields.Datetime.now())
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_guard(self):
        for rec in self:
            if rec.session_id.results_published:
                raise ValidationError(_(
                    "Không thể xóa thí sinh sau khi kỳ thi đã công bố kết quả."))
            if len(rec.registration_id.line_ids) <= 1 and \
                    rec.registration_id.state in ('submitted', 'confirmed'):
                raise ValidationError(_(
                    "Phiếu phải còn ít nhất 1 nhân sự dự thi."))
