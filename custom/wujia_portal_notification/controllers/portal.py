from odoo import http
from odoo.http import request


PAGE_SIZE = 20


class WujiaPortalNotification(http.Controller):

    @http.route(['/portal/notification'], type='http', auth='user', sitemap=False)
    def portal_notification_list(self, page=1, type_id=None, keyword='', **kw):
        franchise_ids = request.env.user._get_accessible_franchise_ids()
        Noti = request.env['wujia.notification'].sudo()

        domain = [('published', '=', True),
                  '|', ('franchise_ids', '=', False),
                       ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1])]
        try:
            tid = int(type_id) if type_id else None
        except (TypeError, ValueError):
            tid = None
        if tid:
            domain.append(('type_id', '=', tid))
        if keyword:
            domain.append(('name', 'ilike', keyword))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Noti.search_count(domain)
        notifications = Noti.search(domain, limit=PAGE_SIZE, offset=offset, order='date desc')

        # Lookup read status — single batched query
        Read = request.env['wujia.notification.read'].sudo()
        read_ids = set(Read.search([
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', notifications.ids),
        ]).mapped('notification_id').ids)

        types = request.env['wujia.notification.type'].sudo().search(
            [('active', '=', True)], order='sequence'
        )
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in [('type_id', tid or ''), ('keyword', keyword)] if v
            ),
        }
        return request.render('wujia_portal_notification.portal_notification_list', {
            'notifications': notifications,
            'read_ids': read_ids, 'types': types, 'pager': pager,
            'type_id': tid, 'keyword': keyword,
        })

    @http.route(['/portal/notification/<int:notification_id>'],
                type='http', auth='user', sitemap=False)
    def portal_notification_detail(self, notification_id, **kw):
        franchise_ids = request.env.user._get_accessible_franchise_ids()
        Noti = request.env['wujia.notification'].sudo()
        noti = Noti.search([
            ('id', '=', notification_id), ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ], limit=1)
        if not noti:
            return request.redirect('/portal/notification')
        # Mark as read (idempotent)
        Read = request.env['wujia.notification.read'].sudo()
        if not Read.search_count([
            ('notification_id', '=', noti.id),
            ('user_id', '=', request.env.user.id),
        ]):
            Read.create({
                'notification_id': noti.id,
                'user_id': request.env.user.id,
            })
        return request.render('wujia_portal_notification.portal_notification_detail', {
            'noti': noti,
        })
