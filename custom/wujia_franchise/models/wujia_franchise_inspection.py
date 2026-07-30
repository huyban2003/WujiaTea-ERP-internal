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

	@api.model
	def get_schedule_data(self, start_date_str=None, end_date_str=None):
		# Fetch all active franchises
		franchises = self.env['wujia.franchise.management'].search([('active', '=', True)])
		franchise_data = [{
			'id': f.id,
			'name': f.name,
			'code': f.code,
			'status': f.status,
			'area_id': f.area_id.id if f.area_id else False,
			'area_name': f.area_id.name if f.area_id else '',
		} for f in franchises]

		# Fetch all active users as inspectors
		inspectors = self.env['res.users'].search([('active', '=', True)])
		inspector_data = [{
			'id': u.id,
			'name': u.name,
		} for u in inspectors]

		# Fetch areas
		areas = self.env['res.area'].search([])
		area_data = [{
			'id': a.id,
			'name': a.name,
		} for a in areas]

		# Fetch existing inspections in the date range
		domain = []
		if start_date_str and end_date_str:
			domain += [
				('planned_date', '>=', start_date_str + ' 00:00:00'),
				('planned_date', '<=', end_date_str + ' 23:59:59'),
			]
		inspections = self.search(domain)
		inspection_data = [{
			'id': i.id,
			'name': i.name,
			'franchise_id': i.franchise_id.id,
			'franchise_name': i.franchise_id.name,
			'franchise_code': i.franchise_id.code,
			'inspector_id': i.inspector_user_id.id if i.inspector_user_id else False,
			'inspector_name': i.inspector_user_id.name if i.inspector_user_id else '',
			'planned_date': fields.Datetime.to_string(i.planned_date) if i.planned_date else '',
			'state': i.state,
		} for i in inspections]

		return {
			'franchises': franchise_data,
			'inspectors': inspector_data,
			'areas': area_data,
			'inspections': inspection_data,
			'statuses': dict(self.env['wujia.franchise.management']._fields['status'].selection),
		}

	@api.model
	def save_schedule_data(self, date_str, inspector_id, franchise_ids):
		# Validate input
		if not date_str:
			return False
		
		# Find the active template
		template = self.env['wujia.franchise.inspection.template'].search([('state', '=', 'active')], limit=1)

		# Convert date_str (YYYY-MM-DD) to Datetime bounds
		start_dt = date_str + ' 00:00:00'
		end_dt = date_str + ' 23:59:59'

		# Find existing inspections for this date
		existing_inspections = self.search([
			('planned_date', '>=', start_dt),
			('planned_date', '<=', end_dt),
		])

		existing_franchise_ids = existing_inspections.mapped('franchise_id.id')

		# 1. Delete inspections that are NOT in the checked franchise_ids (only delete if state is draft)
		to_delete = existing_inspections.filtered(lambda r: r.franchise_id.id not in franchise_ids and r.state == 'draft')
		if to_delete:
			to_delete.unlink()

		# 2. Create inspections for new checked franchise_ids
		for fid in franchise_ids:
			if fid not in existing_franchise_ids:
				franchise = self.env['wujia.franchise.management'].browse(fid)
				if not franchise.exists():
					continue
				
				# Create inspection
				inspection = self.create({
					'name': f"Giám sát {franchise.name}",
					'franchise_id': franchise.id,
					'inspector_user_id': inspector_id or False,
					'planned_date': fields.Datetime.from_string(start_dt),
					'template_id': template.id if template else False,
					'state': 'draft',
				})

				# Copy template lines
				if template:
					lines = []
					for tl in template.line_ids:
						lines.append((0, 0, {
							'template_line_id': tl.id,
							'criterion_code_snapshot': tl.criterion_code,
							'category_snapshot': tl.category_id.name if tl.category_id else '',
							'content_snapshot': tl.content,
							'criterion_type_snapshot': tl.criterion_type,
							'deduction_score_snapshot': tl.deduction_score,
							'result': 'pass',
						}))
					inspection.write({'line_ids': lines})
			else:
				# Update inspector if it changed
				insp = existing_inspections.filtered(lambda r: r.franchise_id.id == fid)
				if insp and insp.state == 'draft' and insp.inspector_user_id.id != inspector_id:
					insp.write({'inspector_user_id': inspector_id or False})

		return True
