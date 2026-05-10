from datetime import date, datetime, timedelta

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

STATE_BADGES = {
    'draft': ('Mới', 'state-draft'),
    'sent': ('Đã gửi', 'state-sent'),
    'sale': ('Đã xác nhận', 'state-sale'),
    'done': ('Hoàn thành', 'state-done'),
    'cancel': ('Đã hủy', 'state-cancel'),
}


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


class WujiaPortalHistory(http.Controller):

    @http.route(['/portal/purchase-history'], type='http', auth='user', sitemap=False)
    def portal_history_list(self, page=1, date_from='', date_to='', state='', preset='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_purchase_history.portal_history_list', {
                'orders': [], 'pager': {}, 'no_franchise': True,
                'state_badges': STATE_BADGES, 'date_from': '', 'date_to': '',
                'state': '', 'preset': '',
            })

        # Preset shortcut: this_month / last_month
        today = date.today()
        if preset == 'this_month':
            date_from = today.replace(day=1).strftime('%Y-%m-%d')
            date_to = today.strftime('%Y-%m-%d')
        elif preset == 'last_month':
            first_this = today.replace(day=1)
            last_month_end = first_this - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            date_from = last_month_start.strftime('%Y-%m-%d')
            date_to = last_month_end.strftime('%Y-%m-%d')

        domain = [('franchise_id', 'in', list(franchise_ids))]
        df = _parse_date(date_from)
        dt = _parse_date(date_to)
        if df:
            domain.append(('date_order', '>=', datetime.combine(df, datetime.min.time())))
        if dt:
            domain.append(('date_order', '<=', datetime.combine(dt, datetime.max.time())))
        if state and state in STATE_BADGES:
            domain.append(('state', '=', state))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        SO = request.env['sale.order'].sudo()
        total = SO.search_count(domain)
        orders = SO.search(domain, limit=PAGE_SIZE, offset=offset, order='date_order desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page},
            'page_count': last_page, 'page_total': total,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': self._qs(date_from=date_from, date_to=date_to, state=state),
        }

        return request.render('wujia_portal_purchase_history.portal_history_list', {
            'no_franchise': False,
            'orders': orders, 'pager': pager,
            'date_from': date_from, 'date_to': date_to,
            'state': state, 'preset': preset,
            'state_badges': STATE_BADGES,
        })

    @http.route(['/portal/purchase-history/<int:order_id>'],
                type='http', auth='user', sitemap=False)
    def portal_history_detail(self, order_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/purchase-history')
        order = request.env['sale.order'].sudo().search([
            ('id', '=', order_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not order:
            return request.redirect('/portal/purchase-history')
        return request.render('wujia_portal_purchase_history.portal_history_detail', {
            'order': order, 'state_badges': STATE_BADGES,
        })

    def _qs(self, **kw):
        return '&'.join(f'{k}={v}' for k, v in kw.items() if v)
