from datetime import timedelta

from odoo import fields, http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

# Tab BA spec: "Thông báo từ HQ" (mới) vs "Lịch sử thông báo" (cũ).
TAB_RECENT = 'recent'
TAB_HISTORY = 'history'
RECENT_DAYS = 30


class WujiaPortalNotification(http.Controller):

    @http.route(['/portal/notification'], type='http', auth='user', sitemap=False)
    def portal_notification_list(self, page=1, type_id=None, keyword='',
                                 tab=TAB_RECENT, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()

        # Domain base: published + đúng franchise (broadcast hoặc targeted).
        domain = [
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ]

        # Tab filter (BA spec): tách "Mới" (30 ngày) vs "Lịch sử" (cũ hơn).
        cutoff = fields.Datetime.now() - timedelta(days=RECENT_DAYS)
        if tab == TAB_HISTORY:
            domain.append(('date', '<', cutoff))
        else:
            tab = TAB_RECENT
            domain.append(('date', '>=', cutoff))

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

        # Đếm tổng mỗi tab (cho badge số trên tab) — 1 query / tab.
        cnt_recent = Noti.search_count([
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('date', '>=', cutoff),
        ])
        cnt_history = Noti.search_count([
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('date', '<', cutoff),
        ])

        # Lookup read status — single batched query (chỉ trang hiện tại).
        Read = request.env['wujia.notification.read'].sudo()
        read_ids = set(Read.search([
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', notifications.ids),
        ]).mapped('notification_id').ids) if notifications else set()

        types = request.env['wujia.notification.type'].sudo().search(
            [('active', '=', True)], order='sequence'
        )
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in
                [('tab', tab), ('type_id', tid or ''), ('keyword', keyword)] if v
            ),
        }
        return request.render('wujia_portal_notification.portal_notification_list', {
            'notifications': notifications,
            'read_ids': read_ids, 'types': types, 'pager': pager,
            'type_id': tid, 'keyword': keyword,
            'tab': tab, 'cnt_recent': cnt_recent, 'cnt_history': cnt_history,
            'tab_recent': TAB_RECENT, 'tab_history': TAB_HISTORY,
        })

    @http.route(['/portal/notification/<int:notification_id>'],
                type='http', auth='user', sitemap=False)
    def portal_notification_detail(self, notification_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()
        noti = Noti.search([
            ('id', '=', notification_id), ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ], limit=1)
        if not noti:
            return request.redirect('/portal/notification')
        # Mark as read (idempotent — UNIQUE constraint trên DB)
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
