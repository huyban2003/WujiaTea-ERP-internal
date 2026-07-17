from odoo import fields, models


class WujiaExamResult(models.Model):
    """DEPRECATED (Sprint M) — kết quả thi cũ (skeleton). Kết quả giờ nhập
    trực tiếp trên `wujia.exam.registration.line`. Giữ để portal demo bind."""

    _name = 'wujia.exam.result'
    _description = 'Wujia Exam Result'
    _order = 'create_date desc'

    registration_id = fields.Many2one(
        'wujia.exam.registration', string='Đăng ký',
        required=True, index=True, ondelete='cascade',
    )
    user_id = fields.Many2one(
        related='registration_id.requester_user_id', store=True, index=True,
    )
    session_id = fields.Many2one(
        related='registration_id.session_id', store=True, index=True,
    )
    franchise_id = fields.Many2one(
        related='registration_id.franchise_id', store=True, index=True,
    )
    score = fields.Float(string='Điểm', digits=(5, 2))
    passed = fields.Boolean(string='Đạt')
    note = fields.Text(string='Nhận xét')
    certificate_url = fields.Char(string='URL chứng nhận')
