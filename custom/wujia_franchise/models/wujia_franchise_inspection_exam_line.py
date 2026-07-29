from odoo import api, fields, models


class FranchiseInspectionExamLine(models.Model):
    """Kết quả trả lời bài thi 5 câu"""
    _name = 'wujia.franchise.inspection.exam.line'
    _description = 'Franchise Inspection Exam Line'
    _order = 'sequence, id'

    inspection_id = fields.Many2one('wujia.franchise.inspection', 'Inspection', ondelete='cascade', required=True)
    question_id = fields.Many2one('wujia.franchise.inspection.question', 'Question', required=True)
    question_code_snapshot = fields.Char('Question Code Snapshot')
    question_text_snapshot = fields.Text('Question Text Snapshot')
    correct_answer_snapshot = fields.Text('Correct Answer Snapshot')
    employee_answer = fields.Text('Employee Answer')
    is_correct = fields.Boolean('Correct', compute='_compute_is_correct', store=True)
    point = fields.Float('Point', compute='_compute_point', store=True)
    sequence = fields.Integer('Sequence', default=10)
    locked = fields.Boolean('Locked', default=False)

    @api.depends('employee_answer', 'correct_answer_snapshot')
    def _compute_is_correct(self):
        for record in self:
            correct_answer = (record.correct_answer_snapshot or '').strip().lower()
            employee_answer = (record.employee_answer or '').strip().lower()
            record.is_correct = bool(correct_answer and employee_answer and employee_answer == correct_answer)

    @api.depends('is_correct')
    def _compute_point(self):
        for record in self:
            record.point = 1.0 if record.is_correct else 0.0
