from odoo import api, fields, models


class FranchiseInspection(models.Model):
	"""Phiếu giám sát đồng thời là kế hoạch"""
	_name = 'wujia.franchise.inspection'
	_description = 'Franchise Inspection'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'

	name = fields.Char('Name', required=True)
	franchise_id = fields.Many2one('wujia.franchise.management', string='Franchise', required=True)
	inspector_user_id = fields.Many2one('res.users', string='Inspector')
	planned_date = fields.Datetime('Planned Date')
	started_at = fields.Datetime('Started At')
	submitted_at = fields.Datetime('Submitted At')
	template_id = fields.Many2one('wujia.franchise.inspection.template', string='Template')
	state = fields.Selection([
		('draft', 'Nháp'),
		('in_progress', 'Đang thực hiện'),
		('submitted', 'Đã nộp'),
		('approved', 'Đã duyệt'),
		('cancelled', 'Đã hủy'),
	], string='Trạng thái', default='draft', tracking=True)
	previous_inspection_id = fields.Many2one('wujia.franchise.inspection', string='Previous Inspection')
	checklist_score = fields.Float('Checklist Score', compute='_compute_scores', store=True)
	exam_score = fields.Float('Exam Score', compute='_compute_scores', store=True)
	total_score = fields.Float('Total Score', compute='_compute_scores', store=True)
	grade = fields.Selection([
		('A', 'A'),
		('B', 'B'),
		('C', 'C'),
		('D', 'D'),
	], string='Xếp loại', compute='_compute_scores', store=True)
	next_due_date = fields.Date('Next Due Date')
	test_employee_name = fields.Char('Test Employee Name')
	tenure = fields.Char('Tenure')
	currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, required=True)
	manual_revenue_snapshot = fields.Monetary('Manual Revenue Snapshot', currency_field='currency_id')
	confirmed_user_id = fields.Many2one('res.users', string='Confirmed User')
	member_id = fields.Many2one('wujia.franchise.member', string='Member')
	confirmed_at = fields.Datetime('Confirmed At')
	notes = fields.Text('Notes')
	line_ids = fields.One2many('wujia.franchise.inspection.line', 'inspection_id', string='Checklist Lines')
	exam_line_ids = fields.One2many('wujia.franchise.inspection.exam.line', 'inspection_id', string='Exam Lines')

	@api.depends('template_id.checklist_max_score', 'line_ids.deduction_score_actual', 'exam_line_ids.point')
	def _compute_scores(self):
		for record in self:
			total_deduction = sum(record.line_ids.mapped('deduction_score_actual'))
			template_max = record.template_id.checklist_max_score if record.template_id else 0.0
			record.checklist_score = max(template_max - total_deduction, 0.0)
			record.exam_score = sum(record.exam_line_ids.mapped('point'))
			record.total_score = record.checklist_score + record.exam_score
			if record.total_score >= 90:
				record.grade = 'A'
			elif record.total_score >= 75:
				record.grade = 'B'
			elif record.total_score >= 60:
				record.grade = 'C'
			else:
				record.grade = 'D'

	def action_start(self):
		self.write({'state': 'in_progress', 'started_at': fields.Datetime.now()})

	def action_complete(self):
		self.write({'state': 'submitted', 'submitted_at': fields.Datetime.now()})

	def action_approve(self):
		self.write({'state': 'approved'})
