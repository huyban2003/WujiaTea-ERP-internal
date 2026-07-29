from odoo import api, fields, models


class FranchiseInspectionTemplate(models.Model):
    """Bộ tiêu chuẩn đánh giá cho cửa hàng nhượng quyền"""
    _name = 'wujia.franchise.inspection.template'
    _description = 'Franchise Inspection Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Tên mẫu phiếu giám sát', required=True)
    code = fields.Char('Mã mẫu', required=True)
    version = fields.Char('Phiên bản', required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('active', 'Đang hoạt động'),
        ('archived', 'Đã lưu trữ'),
    ], string='Trạng thái', default='draft', required=True)
    effective_date = fields.Date('Ngày có hiệu lực')
    checklist_max_score = fields.Float('Điểm tối đa checklist', default=95.0)
    exam_max_score = fields.Float('Điểm tối đa bài thi', default=5.0)
    total_max_score = fields.Float('Tổng điểm tối đa', default=100.0, compute='_compute_total_max_score', store=True)
    line_ids = fields.One2many('wujia.franchise.inspection.template.line', 'template_id', 'Danh sách tiêu chí')

    @api.depends('checklist_max_score', 'exam_max_score')
    def _compute_total_max_score(self):
        for record in self:
            record.total_max_score = (record.checklist_max_score or 0.0) + (record.exam_max_score or 0.0)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_active(self):
        self.write({'state': 'active'})

    def action_archive(self):
        self.write({'state': 'archived'})