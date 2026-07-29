from odoo import fields, models


class FranchiseInspectionQuestion(models.Model):
    """Thư viện câu hỏi trắc nghiệm kiểm tra nhân viên"""
    _name = 'wujia.franchise.inspection.question'
    _description = 'Franchise Inspection Question'

    code = fields.Char('Mã câu hỏi')
    question_text = fields.Text('Nội dung câu hỏi')
    correct_answer = fields.Text('Đáp án đúng')
    category = fields.Char('Nhóm câu hỏi')
    active = fields.Boolean('Kích hoạt', default=True)