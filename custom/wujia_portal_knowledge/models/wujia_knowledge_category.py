from odoo import api, fields, models


class WujiaKnowledgeCategory(models.Model):
    _name = 'wujia.knowledge.category'
    _description = 'Wujia Knowledge Category'
    _order = 'sequence, name'
    _parent_store = True
    _parent_name = 'parent_id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(string='Mã', help='Slug ngắn cho URL filter')
    parent_id = fields.Many2one('wujia.knowledge.category', string='Danh mục cha',
                                ondelete='set null', index=True)
    parent_path = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    article_count = fields.Integer(compute='_compute_article_count')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('uniq_code', 'unique(code)', 'Mã danh mục phải duy nhất.'),
    ]

    def _compute_article_count(self):
        Article = self.env['wujia.knowledge.article'].sudo()
        groups = Article._read_group(
            [('category_id', 'in', self.ids), ('published', '=', True)],
            groupby=['category_id'], aggregates=['__count'],
        )
        mapping = {cat.id: count for cat, count in groups}
        for cat in self:
            cat.article_count = mapping.get(cat.id, 0)
