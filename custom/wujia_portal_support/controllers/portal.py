from werkzeug.exceptions import Forbidden, NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    DEFAULT_DOC_MIME,
    attach_files_to_record,
    build_pager,
    status_badge,
    status_badge_for,
)


PAGE_SIZE = 20

# Display labels for portal templates — keys map to ticket.state values.
STATE_LABELS = {k: (v, status_badge_for(v)) for k, v in {
    'new': 'Mới',
    'in_progress': 'Đang xử lý',
    'waiting_customer': 'Chờ phản hồi',
    'resolved': 'Đã giải quyết',
    'closed': 'Đã đóng',
    'cancelled': 'Đã huỷ',
}.items()}

# Nhãn MOBILE (Figma Mobile_Ticket), tách khỏi STATE_LABELS desktop. LƯU Ý
# 'waiting_customer'="Có phản hồi" (mobile/Figma) ≠ desktop "Chờ phản hồi" — drift chủ đích, đối chiếu BA.
MOBILE_TICKET_BADGES = {
    'new':              ('Mới', status_badge('info')),
    'in_progress':      ('Đang xử lý', status_badge('processing')),
    'waiting_customer': ('Có phản hồi', status_badge('feedback')),
    'resolved':         ('Đã giải quyết', status_badge('success')),
    'closed':           ('Đã đóng', status_badge('neutral')),
    'cancelled':        ('Đã huỷ', status_badge('danger')),
}

PRIORITY_LABELS = {
    'normal': ('Bình thường', 'wujia-badge-muted'),
    'urgent': ('Khẩn', 'wujia-badge-danger'),
}


def _categories():
    return request.env['wujia.support.category'].sudo().search(
        [('active', '=', True)], order='sequence, name',
    )


def _scoped_ticket(ticket_id):
    Ticket = request.env['wujia.support.ticket'].sudo()
    return Ticket.search(
        [('id', '=', ticket_id)] + Ticket._portal_scope_domain(request.env.user), limit=1,
    )


class WujiaPortalSupport(http.Controller):

    @http.route(['/portal/support'], type='http', auth='user', sitemap=False)
    def portal_support_list(self, page=1, state='', q='', **kw):
        Ticket = request.env['wujia.support.ticket'].sudo()
        domain = Ticket._portal_scope_domain(request.env.user) + [('state', '!=', 'cancelled')]
        if state and state in STATE_LABELS:
            domain.append(('state', '=', state))
        # Sprint 17 — tìm theo Mã (name) HOẶC Tiêu đề (title). ilike trigram-friendly.
        q = (q or '').strip()
        if q:
            domain += ['|', ('name', 'ilike', q), ('title', 'ilike', q)]
        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Ticket.search_count(domain)
        tickets = Ticket.search(
            domain, limit=PAGE_SIZE, offset=offset, order='create_date desc',
        )
        pgn = build_pager(total, page, PAGE_SIZE, path='/portal/support',
                          item_label='yêu cầu')
        return request.render('wujia_portal_support.portal_support_list', {
            'tickets': tickets, 'pgn': pgn,
            'state_labels': STATE_LABELS,
            'priority_labels': PRIORITY_LABELS,
            'm_ticket_badges': MOBILE_TICKET_BADGES,
            'state': state,
            'q': q,
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
        try:
            franchise_id = int(post.get('franchise_id') or 0)
            category_id = int(post.get('category_id') or 0)
        except (TypeError, ValueError):
            return request.redirect('/portal/support/new?error=invalid_input')
        # Accept both 'title' (new) and 'subject' (legacy) form keys.
        title = (post.get('title') or post.get('subject') or '').strip()
        files = request.httprequest.files.getlist('attachments')
        ticket, error = request.env['wujia.support.ticket'].sudo().create_from_portal({
            'title': title,
            'description': (post.get('description') or '').strip(),
            'franchise_id': franchise_id,
            'created_by_id': request.env.user.id,
            'category_id': category_id,
            'priority': post.get('priority', 'normal'),
        }, get_active_franchise_ids_filter(), attach=lambda t: attach_files_to_record(
            t, files, allowed_mime=DEFAULT_DOC_MIME, max_size_mb=5, max_count=6,
        ))
        if error:
            return request.redirect(f'/portal/support/new?error={error}')
        return request.redirect(f'/portal/support/{ticket.id}')

    @http.route(['/portal/support/<int:ticket_id>'],
                type='http', auth='user', sitemap=False)
    def portal_support_detail(self, ticket_id, **kw):
        ticket = _scoped_ticket(ticket_id)
        if not ticket:
            return request.redirect('/portal/support')
        return request.render('wujia_portal_support.portal_support_detail', {
            'ticket': ticket,
            'state_labels': STATE_LABELS,
            'priority_labels': PRIORITY_LABELS,
            'm_ticket_badges': MOBILE_TICKET_BADGES,
        })

    @http.route(['/portal/support/<int:ticket_id>/reply'],
                type='http', auth='user', sitemap=False,
                methods=['POST'], csrf=True)
    def portal_support_reply(self, ticket_id, **post):
        ticket = _scoped_ticket(ticket_id)
        if not ticket:
            return request.redirect('/portal/support')
        ticket._portal_reply(request.env.user, post.get('body'))
        return request.redirect(f'/portal/support/{ticket_id}')

    @http.route(['/portal/support/<int:ticket_id>/attachment/<int:att_id>'],
                type='http', auth='user', sitemap=False)
    def portal_support_attachment_download(self, ticket_id, att_id, **kw):
        """Stream attachment với ACL: chỉ owner ticket được tải."""
        ticket = _scoped_ticket(ticket_id)
        if not ticket:
            raise NotFound()
        att = ticket._portal_get_attachment(att_id)
        if not att:
            raise Forbidden()
        return request.env['ir.binary']._get_stream_from(att).get_response(
            as_attachment=True,
        )
