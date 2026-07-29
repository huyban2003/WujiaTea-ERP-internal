from odoo import fields, models


class FranchiseInspectionLine(models.Model):
    """Kết quả đánh giá từng tiêu chí và quá trình khắc phục"""
    _name = 'wujia.franchise.inspection.line'
    _description = 'Franchise Inspection Line'
    _order = 'id desc'

    inspection_id = fields.Many2one('wujia.franchise.inspection', 'Inspection', ondelete='cascade', required=True)
    template_line_id = fields.Many2one('wujia.franchise.inspection.template.line', 'Template Line')
    criterion_code_snapshot = fields.Char('Criterion Code Snapshot')
    category_snapshot = fields.Char('Category Snapshot')
    content_snapshot = fields.Text('Content Snapshot')
    criterion_type_snapshot = fields.Selection([
        ('normal', 'Normal'),
        ('critical', 'Critical'),
    ], string='Criterion Type Snapshot')
    deduction_score_snapshot = fields.Float('Deduction Score Snapshot')
    result = fields.Selection([
        ('pass', 'Đạt'),
        ('fail', 'Không đạt'),
    ], string='Kết quả', default='pass')
    deduction_score_actual = fields.Float('Điểm trừ thực tế', default=0.0)
    note = fields.Text('Ghi chú')
    evidence_attachment_ids = fields.Many2many(
        'ir.attachment',
        'wujia_franchise_inspection_line_evidence_rel',
        'line_id',
        'attachment_id',
        string='Evidence Attachments',
    )
    previous_line_id = fields.Many2one('wujia.franchise.inspection.line', string='Previous Line')
    previous_result = fields.Selection(related='previous_line_id.result', string='Kết quả lần trước', readonly=True)
    previous_deduction_score = fields.Float(related='previous_line_id.deduction_score_actual', string='Điểm trừ lần trước', readonly=True)
    correction_feedback = fields.Text('Phản hồi khắc phục')
    correction_attachment_ids = fields.Many2many(
        'ir.attachment',
        'wujia_franchise_inspection_line_correction_rel',
        'line_id',
        'attachment_id',
        string='Correction Attachments',
    )
    correction_state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang xử lý'),
        ('done', 'Đã xong'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái khắc phục', default='draft')
    correction_review_note = fields.Text('Ghi chú đánh giá lại')
