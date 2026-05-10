from datetime import datetime

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

STATE_LABELS = {
    'draft': ('Nháp', 'state-draft'),
    'sent': ('Đã gửi', 'state-sent'),
    'approved': ('Đã duyệt', 'state-approved'),
    'rejected': ('Từ chối', 'state-rejected'),
    'done': ('Hoàn thành', 'state-done'),
}


class WujiaPortalReturn(http.Controller):

    @http.route(['/portal/return'], type='http', auth='user', sitemap=False)
    def portal_return_list(self, page=1, state='', date_from='', date_to='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_return.portal_return_list', {
                'returns': [], 'pager': {}, 'state_labels': STATE_LABELS,
                'no_franchise': True, 'state': '', 'date_from': '', 'date_to': '',
            })

        domain = [('franchise_id', 'in', list(franchise_ids))]
        if state and state in STATE_LABELS:
            domain.append(('state', '=', state))
        if date_from:
            try:
                df = datetime.strptime(date_from, '%Y-%m-%d')
                domain.append(('request_date', '>=', df))
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                dt = dt.replace(hour=23, minute=59, second=59)
                domain.append(('request_date', '<=', dt))
            except ValueError:
                pass

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        Model = request.env['wujia.return.request'].sudo()
        total = Model.search_count(domain)
        returns = Model.search(domain, limit=PAGE_SIZE, offset=offset, order='request_date desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in [('state', state), ('date_from', date_from), ('date_to', date_to)] if v
            ),
        }

        return request.render('wujia_portal_return.portal_return_list', {
            'no_franchise': False, 'returns': returns, 'pager': pager,
            'state_labels': STATE_LABELS, 'state': state,
            'date_from': date_from, 'date_to': date_to,
        })

    @http.route(['/portal/return/new'], type='http', auth='user', sitemap=False)
    def portal_return_new(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return')
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        # Recent orders cho dropdown chọn đơn gốc
        recent_orders = request.env['sale.order'].sudo().search([
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', 'in', ['sale', 'done']),
        ], order='date_order desc', limit=20)
        error_types = request.env['wujia.return.error.type'].sudo().search([('active', '=', True)])
        return request.render('wujia_portal_return.portal_return_form', {
            'franchises': franchises, 'recent_orders': recent_orders,
            'error_types': error_types, 'state_labels': STATE_LABELS,
        })

    @http.route(['/portal/return/<int:request_id>'], type='http', auth='user', sitemap=False)
    def portal_return_detail(self, request_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return')
        rr = request.env['wujia.return.request'].sudo().search([
            ('id', '=', request_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not rr:
            return request.redirect('/portal/return')
        return request.render('wujia_portal_return.portal_return_detail', {
            'rr': rr, 'state_labels': STATE_LABELS,
        })
