from odoo import api, fields, models


class FranchiseInspectionTemplateLine(models.Model):
    """Dòng tiêu chí cấu hình chi tiết"""
    _name = 'wujia.franchise.inspection.template.line'
    _description = 'Franchise Inspection Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one('wujia.franchise.inspection.template', 'Template', ondelete='cascade', required=True)
    criterion_code = fields.Char('Criterion Code', required=True)
    category_id = fields.Many2one('wujia.franchise.inspection.category', string='Category')
    category_code = fields.Char(
        string='Mã danh mục',
        compute='_compute_category_code',
        inverse='_inverse_category_code',
        store=True
    )
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

    @api.depends('category_id')
    def _compute_category_code(self):
        for record in self:
            record.category_code = record.category_id.code if record.category_id else False

    def _inverse_category_code(self):
        for record in self:
            if record.category_code:
                category = self.env['wujia.franchise.inspection.category'].search([
                    ('code', '=', record.category_code)
                ], limit=1)
                record.category_id = category if category else False
            else:
                record.category_id = False