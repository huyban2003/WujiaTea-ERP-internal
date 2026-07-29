from odoo import fields, models


class FranchiseInspectionTemplateLine(models.Model):
    """Dòng tiêu chí cấu hình chi tiết"""
    _name = 'wujia.franchise.inspection.template.line'
    _description = 'Franchise Inspection Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one('wujia.franchise.inspection.template', 'Template', ondelete='cascade', required=True)
    criterion_code = fields.Char('Criterion Code', required=True)
    category = fields.Char('Category')
    content = fields.Text('Content', required=True)
    criterion_type = fields.Selection([
        ('normal', 'Normal'),
        ('critical', 'Critical'),
    ], string='Criterion Type', default='normal', required=True)
    deduction_score = fields.Float('Deduction Score', default=1.0)
    require_note_if_fail = fields.Boolean('Require Note If Fail', default=False)
    require_evidence_if_fail = fields.Boolean('Require Evidence If Fail', default=False)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)