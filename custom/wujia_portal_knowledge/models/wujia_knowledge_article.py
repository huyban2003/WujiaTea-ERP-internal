import re

from odoo import api, fields, models


class WujiaKnowledgeArticle(models.Model):
    """Skeleton — bài viết kiến thức (SOP, công thức, marketing).

    Slug unique cho SEO-friendly URL `/portal/knowledge/<slug>`."""

    _name = 'wujia.knowledge.article'
    _description = 'Wujia Knowledge Article'
    _order = 'publish_date desc, id desc'

    name = fields.Char(string='Tiêu đề', required=True, translate=True)
    slug = fields.Char(string='Slug', required=True, copy=False, index=True)
    category_id = fields.Many2one(
        'wujia.knowledge.category', string='Danh mục',
        index=True, ondelete='set null',
    )
    summary = fields.Char(string='Tóm tắt', translate=True, size=250)
    content = fields.Html(string='Nội dung', translate=True, sanitize=True)
    cover_image = fields.Binary(string='Ảnh bìa', attachment=True)
    cover_image_filename = fields.Char()
    published = fields.Boolean(string='Đã xuất bản', default=False, index=True)
    publish_date = fields.Datetime(string='Ngày xuất bản', index=True)
    view_count = fields.Integer(string='Lượt xem', default=0, copy=False)
    author_id = fields.Many2one(
        'res.users', string='Tác giả',
        default=lambda self: self.env.user, index=True,
    )
    tag_ids = fields.Char(string='Tag (CSV)', help='Cách nhau bằng dấu phẩy')

    _sql_constraints = [
        ('uniq_slug', 'unique(slug)', 'Slug bài viết phải duy nhất.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') and not vals.get('slug'):
                vals['slug'] = self._make_slug(vals['name'])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name') and not vals.get('slug'):
            for rec in self:
                if not rec.slug:
                    rec.slug = self._make_slug(vals['name'])
        return super().write(vals)

    @staticmethod
    def _make_slug(name):
        s = re.sub(r'[^\w\s-]', '', name.lower(), flags=re.UNICODE).strip()
        s = re.sub(r'[\s_-]+', '-', s)
        return s[:80] or 'article'

    def action_increment_view(self):
        # Atomic SQL update — tránh race condition trên view_count.
        # Skeleton: chưa wire vào controller, gọi từ controller GET sau.
        self.ensure_one()
        self.env.cr.execute(
            "UPDATE wujia_knowledge_article SET view_count = view_count + 1 WHERE id = %s",
            (self.id,),
        )
        self.invalidate_recordset(['view_count'])
