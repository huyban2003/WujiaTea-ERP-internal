from odoo import fields, models


class WujiaExamResult(models.Model):
    """Skeleton — kết quả kỳ thi của 1 đăng ký."""

    _name = 'wujia.exam.result'
    _description = 'Wujia Exam Result'
    _order = 'create_date desc'

    registration_id = fields.Many2one(
        'wujia.exam.registration', string='Đăng ký',
        required=True, index=True, ondelete='cascade',
    )
    user_id = fields.Many2one(
        related='registration_id.user_id', store=True, index=True,
    )
    schedule_id = fields.Many2one(
        related='registration_id.schedule_id', store=True, index=True,
    )
    franchise_id = fields.Many2one(
        related='registration_id.franchise_id', store=True, index=True,
    )
    score = fields.Float(string='Điểm', digits=(5, 2))
    passed = fields.Boolean(string='Đạt')
    note = fields.Text(string='Nhận xét')
    certificate_url = fields.Char(string='URL chứng nhận')
