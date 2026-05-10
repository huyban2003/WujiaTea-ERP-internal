from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

STATE_LABELS = {
    'new': ('Mới', 'state-sent'),
    'in_progress': ('Đang xử lý', 'state-in_progress'),
    'resolved': ('Đã giải quyết', 'state-done'),
    'closed': ('Đã đóng', 'state-closed'),
}

CATEGORY_LABELS = dict([
    ('order', 'Đặt hàng'),
    ('delivery', 'Giao hàng'),
    ('product', 'Sản phẩm'),
    ('pos', 'POS'),
    ('operation', 'Vận hành'),
    ('account', 'Tài khoản'),
    ('other', 'Khác'),
])


class WujiaPortalSupport(http.Controller):

    @http.route(['/portal/support'], type='http', auth='user', sitemap=False)
    def portal_support_list(self, page=1, state='', **kw):
        Ticket = request.env['wujia.support.ticket'].sudo()
        domain = [('user_id', '=', request.env.user.id)]
        if state and state in STATE_LABELS:
            domain.append(('state', '=', state))
        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Ticket.search_count(domain)
        tickets = Ticket.search(domain, limit=PAGE_SIZE, offset=offset, order='create_date desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': f'state={state}' if state else '',
        }
        return request.render('wujia_portal_support.portal_support_list', {
            'tickets': tickets, 'pager': pager,
            'state_labels': STATE_LABELS,
            'category_labels': CATEGORY_LABELS,
            'state': state,
        })

    @http.route(['/portal/support/new'], type='http', auth='user', sitemap=False)
    def portal_support_new(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/support')
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        return request.render('wujia_portal_support.portal_support_form', {
            'franchises': franchises,
            'category_labels': CATEGORY_LABELS,
        })

    @http.route(['/portal/support/<int:ticket_id>'],
                type='http', auth='user', sitemap=False)
    def portal_support_detail(self, ticket_id, **kw):
        ticket = request.env['wujia.support.ticket'].sudo().search([
            ('id', '=', ticket_id),
            ('user_id', '=', request.env.user.id),
        ], limit=1)
        if not ticket:
            return request.redirect('/portal/support')
        return request.render('wujia_portal_support.portal_support_detail', {
            'ticket': ticket,
            'state_labels': STATE_LABELS,
            'category_labels': CATEGORY_LABELS,
        })
