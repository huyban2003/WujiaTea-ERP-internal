from odoo import http
from odoo.http import request


PAGE_SIZE = 12


class WujiaPortalKnowledge(http.Controller):

    @http.route(['/portal/knowledge'], type='http', auth='user', sitemap=False)
    def portal_knowledge_list(self, page=1, category_id=None, tag_id=None,
                              keyword='', **kw):
        Article = request.env['wujia.knowledge.article'].sudo()
        Category = request.env['wujia.knowledge.category'].sudo()
        Tag = request.env['wujia.knowledge.tag'].sudo()

        domain = [('is_published_portal', '=', True)]
        if keyword:
            domain.append(('name', 'ilike', keyword))
        try:
            cat_id = int(category_id) if category_id else None
        except (TypeError, ValueError):
            cat_id = None
        if cat_id:
            domain.append(('category_id', '=', cat_id))
        try:
            t_id = int(tag_id) if tag_id else None
        except (TypeError, ValueError):
            t_id = None
        if t_id:
            domain.append(('tag_ids', 'in', [t_id]))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Article.search_count(domain)
        articles = Article.search(
            domain, limit=PAGE_SIZE, offset=offset,
            order='sequence, publish_date desc, id desc',
        )

        categories = Category.search([('active', '=', True)], order='sequence, name')
        tags = Tag.search([('active', '=', True)], order='name')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in [
                    ('category_id', cat_id or ''),
                    ('tag_id', t_id or ''),
                    ('keyword', keyword),
                ] if v
            ),
        }
        return request.render('wujia_portal_knowledge.portal_knowledge_list', {
            'articles': articles, 'categories': categories, 'tags': tags,
            'pager': pager, 'keyword': keyword,
            'category_id': cat_id, 'tag_id': t_id,
            'current_category': Category.browse(cat_id) if cat_id else None,
            'current_tag': Tag.browse(t_id) if t_id else None,
        })

    @http.route(['/portal/knowledge/<string:slug>'],
                type='http', auth='user', sitemap=False)
    def portal_knowledge_detail(self, slug, **kw):
        article = request.env['wujia.knowledge.article'].sudo().search([
            ('slug', '=', slug), ('is_published_portal', '=', True),
        ], limit=1)
        if not article:
            return request.redirect('/portal/knowledge')
        article.action_increment_view()
        related = request.env['wujia.knowledge.article'].sudo().search([
            ('category_id', '=', article.category_id.id),
            ('id', '!=', article.id),
            ('is_published_portal', '=', True),
        ], order='publish_date desc', limit=4)
        return request.render('wujia_portal_knowledge.portal_knowledge_detail', {
            'article': article, 'related': related,
        })
