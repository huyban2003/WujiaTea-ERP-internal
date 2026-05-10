from odoo import http
from odoo.http import request


PAGE_SIZE = 24


class WujiaPortalSale(http.Controller):
    """Trang đặt hàng — catalog sản phẩm + cart side panel.

    Skeleton UI: button "Add to cart" / "Submit" chưa có handler thật, chỉ render.
    BE workflow (real cart, submit SO) sẽ làm sprint sau."""

    @http.route(['/portal/order'], type='http', auth='user', sitemap=False)
    def portal_order_catalog(self, page=1, category_id=None, keyword='', **kw):
        franchise_ids = request.env.user._get_accessible_franchise_ids()
        if not franchise_ids:
            return request.render('wujia_portal_sale.portal_order_catalog', {
                'no_franchise': True, 'products': [], 'categories': [],
                'cart_lines': [], 'pager': {}, 'keyword': '', 'category_id': None,
            })

        Product = request.env['product.template'].sudo()
        # Public products only; portal user nên chỉ thấy sản phẩm public website.
        domain = [('is_public_website', '=', True), ('active', '=', True)]
        if keyword:
            domain.append(('name', 'ilike', keyword))
        try:
            cat_id = int(category_id) if category_id else None
        except (TypeError, ValueError):
            cat_id = None
        if cat_id:
            domain.append(('categ_id', '=', cat_id))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Product.search_count(domain)
        products = Product.search(domain, limit=PAGE_SIZE, offset=offset, order='name asc')

        # Categories: dùng product.category (internal) — luôn có, nhỏ, cache OK
        Category = request.env['product.category'].sudo()
        categories = Category.search([], order='complete_name')

        pager = request.website.pager(
            url='/portal/order', total=total, page=page, step=PAGE_SIZE,
            url_args={'keyword': keyword, 'category_id': cat_id or ''},
        ) if hasattr(request, 'website') and request.website else self._fallback_pager(total, page)

        return request.render('wujia_portal_sale.portal_order_catalog', {
            'no_franchise': False,
            'products': products,
            'categories': categories,
            'cart_lines': self._get_draft_cart_lines(franchise_ids),
            'pager': pager,
            'keyword': keyword,
            'category_id': cat_id,
            'order_time_from': '06:00',
            'order_time_to': '18:00',
        })

    def _get_draft_cart_lines(self, franchise_ids):
        """Skeleton: lấy đơn nháp gần nhất của franchise hiện hoạt → render giỏ.
        Khi có store-picker thật (Phase 2) sẽ filter theo current store."""
        if not franchise_ids:
            return request.env['sale.order.line'].browse()
        SO = request.env['sale.order'].sudo()
        draft = SO.search([
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', '=', 'draft'),
            ('is_portal_order', '=', True),
        ], order='create_date desc', limit=1)
        return draft.order_line

    def _fallback_pager(self, total, page):
        last = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        return {
            'page': {'num': page, 'url': f'/portal/order?page={page}'},
            'page_count': last, 'page_total': total,
            'page_first': {'num': 1, 'url': '/portal/order?page=1'},
            'page_last': {'num': last, 'url': f'/portal/order?page={last}'},
            'page_previous': {'num': max(1, page - 1), 'url': f'/portal/order?page={max(1, page - 1)}'},
            'page_next': {'num': min(last, page + 1), 'url': f'/portal/order?page={min(last, page + 1)}'},
        }
