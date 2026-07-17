from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WujiaExamTimeSlot(models.Model):
    """Ca thi (khung giờ) — config dùng chung cho khóa thi / kỳ thi."""

    _name = 'wujia.exam.time.slot'
    _description = 'Wujia Exam Time Slot'
    _order = 'time_from, id'

    name = fields.Char(string='Tên ca thi', required=True)
    code = fields.Char(string='Mã ca', required=True)
    time_from = fields.Float(string='Giờ bắt đầu', required=True)
    time_to = fields.Float(string='Giờ kết thúc', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _uniq_code = models.Constraint(
        'unique(code)', 'Mã ca thi phải duy nhất.',
    )

    @api.constrains('time_from', 'time_to')
    def _check_time_range(self):
        for rec in self:
            if not (0.0 <= rec.time_from < rec.time_to <= 24.0):
                raise ValidationError(_(
                    "Ca thi '%s': giờ phải thỏa 0 ≤ bắt đầu < kết thúc ≤ 24.",
                    rec.name))
