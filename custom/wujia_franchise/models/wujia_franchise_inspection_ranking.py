from odoo import fields, models


class FranchiseInspectionRanking(models.Model):
    """Xếp hạng giám sát"""
    _name = 'wujia.franchise.inspection.ranking'
    _description = 'Franchise Inspection Ranking'
    _order = 'min_score desc, id desc'

    name = fields.Char('Tên xếp hạng', required=True)
    code = fields.Char('Mã xếp hạng')
    min_score = fields.Float('Điểm tối thiểu', required=True)
    max_score = fields.Float('Điểm tối đa', required=True)
    description = fields.Text('Mô tả')
    active = fields.Boolean('Kích hoạt', default=True)