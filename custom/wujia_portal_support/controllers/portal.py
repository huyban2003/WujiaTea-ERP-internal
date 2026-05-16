from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

# Display labels for portal templates — keys map to ticket.state values.
STATE_LABELS = {
    'new': ('Mới', 'state-sent'),
    'in_progress': ('Đang xử lý', 'state-in_progress'),
    'waiting_customer': ('Chờ phản hồi', 'state-warning'),
    'resolved': ('Đã giải quyết', 'state-done'),
    'closed': ('Đã đóng', 'state-closed'),
    'cancelled': ('Đã huỷ', 'state-cancel'),
}


def _categories():
    return request.env['wujia.support.category'].sudo().search(
        [('active', '=', True)], order='sequence, name',
    )


class WujiaPortalSupport(http.Controller):

    @http.route(['/portal/support'], type='http', auth='user', sitemap=False)
    def portal_support_list(self, page=1, state='', **kw):
        Ticket = request.env['wujia.support.ticket'].sudo()
        # Portal user only sees own visible tickets, not cancelled.
        domain = [
            ('created_by_id', '=', request.env.user.id),
            ('portal_visible', '=', True),
            ('state', '!=', 'cancelled'),
        ]
        if state and state in STATE_LABELS:
            domain.append(('state', '=', state))
        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Ticket.search_count(domain)
        tickets = Ticket.search(
            domain, limit=PAGE_SIZE, offset=offset, order='create_date desc',
        )
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
            'state': state,
        })

    @http.route(['/portal/support/new'], type='http', auth='user', sitemap=False,
                methods=['GET'])
    def portal_support_new(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/support')
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        return request.render('wujia_portal_support.portal_support_form', {
            'franchises': franchises,
            'categories': _categories(),
            'error': kw.get('error', ''),
        })

    @http.route(['/portal/support/new'], type='http', auth='user', sitemap=False,
                methods=['POST'], csrf=True)
    def portal_support_create(self, **post):
        franchise_id = int(post.get('franchise_id') or 0)
        category_id = int(post.get('category_id') or 0)
        priority = post.get('priority', 'normal')
        # Accept both 'title' (new) and 'subject' (legacy) form keys.
        title = (post.get('title') or post.get('subject') or '').strip()
        description = (post.get('description') or '').strip()

        if not title or not franchise_id or not category_id:
            return request.redirect('/portal/support/new?error=missing_fields')

        # Verify user has access to the selected franchise.
        franchise_ids = get_active_franchise_ids_filter()
        if franchise_id not in franchise_ids:
            return request.redirect('/portal/support/new?error=invalid_franchise')

        if priority not in ('normal', 'urgent'):
            priority = 'normal'

        ticket = request.env['wujia.support.ticket'].sudo().create({
            'title': title,
            'description': description,
            'franchise_id': franchise_id,
            'created_by_id': request.env.user.id,
            'category_id': category_id,
            'priority': priority,
        })

        files = request.httprequest.files.getlist('attachments')
        for f in files:
            if f and f.filename:
                data = f.read()
                if data:
                    request.env['ir.attachment'].sudo().create({
                        'name': f.filename,
                        'datas': data,
                        'res_model': 'wujia.support.ticket',
                        'res_id': ticket.id,
                    })

        return request.redirect(f'/portal/support/{ticket.id}')

    @http.route(['/portal/support/<int:ticket_id>'],
                type='http', auth='user', sitemap=False)
    def portal_support_detail(self, ticket_id, **kw):
        ticket = request.env['wujia.support.ticket'].sudo().search([
            ('id', '=', ticket_id),
            ('created_by_id', '=', request.env.user.id),
            ('portal_visible', '=', True),
        ], limit=1)
        if not ticket:
            return request.redirect('/portal/support')
        return request.render('wujia_portal_support.portal_support_detail', {
            'ticket': ticket,
            'state_labels': STATE_LABELS,
        })

    @http.route(['/portal/support/<int:ticket_id>/reply'],
                type='http', auth='user', sitemap=False,
                methods=['POST'], csrf=True)
    def portal_support_reply(self, ticket_id, **post):
        ticket = request.env['wujia.support.ticket'].sudo().search([
            ('id', '=', ticket_id),
            ('created_by_id', '=', request.env.user.id),
            ('portal_visible', '=', True),
        ], limit=1)
        if not ticket:
            return request.redirect('/portal/support')
        body = (post.get('body') or '').strip()
        if body:
            # message_post triggers _update_response_analytics on the ticket.
            ticket.with_user(request.env.user).message_post(
                body=body, message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
        return request.redirect(f'/portal/support/{ticket_id}')
