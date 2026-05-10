from odoo import http
from odoo.http import request


PAGE_SIZE = 12


class WujiaPortalKnowledge(http.Controller):

    @http.route(['/portal/knowledge'], type='http', auth='user', sitemap=False)
    def portal_knowledge_list(self, page=1, category_id=None, keyword='', **kw):
        Article = request.env['wujia.knowledge.article'].sudo()
        Category = request.env['wujia.knowledge.category'].sudo()

        domain = [('published', '=', True)]
        if keyword:
            domain.append(('name', 'ilike', keyword))
        try:
            cat_id = int(category_id) if category_id else None
        except (TypeError, ValueError):
            cat_id = None
        if cat_id:
            domain.append(('category_id', '=', cat_id))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Article.search_count(domain)
        articles = Article.search(domain, limit=PAGE_SIZE, offset=offset,
                                  order='publish_date desc')

        categories = Category.search([('active', '=', True)], order='sequence, name')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in [('category_id', cat_id or ''), ('keyword', keyword)] if v
            ),
        }
        return request.render('wujia_portal_knowledge.portal_knowledge_list', {
            'articles': articles, 'categories': categories,
            'pager': pager, 'keyword': keyword, 'category_id': cat_id,
            'current_category': Category.browse(cat_id) if cat_id else None,
        })

    @http.route(['/portal/knowledge/<string:slug>'],
                type='http', auth='user', sitemap=False)
    def portal_knowledge_detail(self, slug, **kw):
        article = request.env['wujia.knowledge.article'].sudo().search([
            ('slug', '=', slug), ('published', '=', True),
        ], limit=1)
        if not article:
            return request.redirect('/portal/knowledge')
        # Atomic increment view count
        article.action_increment_view()
        # Related: same category, exclude self, top 4 by recent
        related = request.env['wujia.knowledge.article'].sudo().search([
            ('category_id', '=', article.category_id.id),
            ('id', '!=', article.id),
            ('published', '=', True),
        ], order='publish_date desc', limit=4)
        return request.render('wujia_portal_knowledge.portal_knowledge_detail', {
            'article': article, 'related': related,
        })
