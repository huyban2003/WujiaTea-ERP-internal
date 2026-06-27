from datetime import datetime, timedelta

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

# PC desktop (Sprint PC-3) — type code → (tone css, feather icon); priority → (nhãn, badge css).
# Đồng bộ mapping với mobile WJ_PTAG (urgent=Cần làm/xanh, high=Quan trọng/cam, low/normal=Lưu ý/cyan).
PC_TYPE_TONE = {
    'URG': ('wj-pc-noti-type--red', 'icon-alert-triangle'),
    'GEN': ('wj-pc-noti-type--cyan', 'icon-bell'),
    'PROMO': ('wj-pc-noti-type--amber', 'icon-gift'),
    'SYS': ('wj-pc-noti-type--violet', 'icon-settings'),
    'OTH': ('wj-pc-noti-type--green', 'icon-info'),
}
PC_PRIORITY_TAGS = {
    'urgent': ('Cần làm', 'wj-pc-badge--done'),
    'high': ('Quan trọng', 'wj-pc-badge--transit'),
    'normal': ('Lưu ý', 'wj-pc-badge--confirmed'),
    'low': ('Lưu ý', 'wj-pc-badge--confirmed'),
}


def _parse_date(value):
    """'YYYY-MM-DD' (HTML date input) → date, hoặc None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


class WujiaPortalNotification(http.Controller):

    @http.route(['/portal/notification'], type='http', auth='user', sitemap=False)
    def portal_notification_list(self, page=1, type_id=None, keyword='',
                                 tab=TAB_RECENT, unread=None,
                                 date_from='', date_to='', priority='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()

        # Domain base: published + đúng franchise (broadcast hoặc targeted).
        domain = [
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ]

        # Date range (PC) thắng cutoff tab; rỗng → cutoff "Mới" (30 ngày) / "Lịch sử".
        cutoff = fields.Datetime.now() - timedelta(days=RECENT_DAYS)
        df, dt = _parse_date(date_from), _parse_date(date_to)
        if df or dt:
            if df:
                domain.append(('date', '>=', datetime.combine(df, datetime.min.time())))
            if dt:
                domain.append(('date', '<=', datetime.combine(dt, datetime.max.time())))
        elif tab == TAB_HISTORY:
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
        # Chip "Quan trọng"/"Cần làm" (PC) — lọc theo mức ưu tiên.
        if priority in ('high', 'urgent'):
            domain.append(('priority', '=', priority))
        # Chip "Chưa đọc" — loại bỏ noti user đã mở.
        if unread:
            read_noti_ids = request.env['wujia.notification.read'].sudo().search([
                ('user_id', '=', request.env.user.id),
            ]).mapped('notification_id').ids
            domain.append(('id', 'not in', read_noti_ids))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Noti.search_count(domain)
        notifications = Noti.search(domain, limit=PAGE_SIZE, offset=offset, order='date desc')

        # Recent set (30 ngày) — dùng cho badge tab "Mới" + đếm chưa đọc (mobile).
        recent_ids = Noti.search([
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('date', '>=', cutoff),
        ]).ids
        cnt_recent = len(recent_ids)
        cnt_history = Noti.search_count([
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('date', '<', cutoff),
        ])
        # Chưa đọc (= số bell badge): recent − đã đọc.
        read_recent = request.env['wujia.notification.read'].sudo().search_count([
            ('notification_id', 'in', recent_ids),
            ('user_id', '=', request.env.user.id),
        ]) if recent_ids else 0
        cnt_unread = max(0, cnt_recent - read_recent)

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
                [('tab', tab), ('type_id', tid or ''), ('keyword', keyword),
                 ('unread', unread or ''), ('date_from', date_from or ''),
                 ('date_to', date_to or ''), ('priority', priority or '')] if v
            ),
        }
        return request.render('wujia_portal_notification.portal_notification_list', {
            'notifications': notifications,
            'read_ids': read_ids, 'types': types, 'pager': pager,
            'type_id': tid, 'keyword': keyword,
            'tab': tab, 'cnt_recent': cnt_recent, 'cnt_history': cnt_history,
            'tab_recent': TAB_RECENT, 'tab_history': TAB_HISTORY,
            'total': total, 'cnt_unread': cnt_unread, 'unread': unread,
            'date_from': date_from, 'date_to': date_to, 'priority': priority,
            'page_size': PAGE_SIZE,
            'PC_TYPE_TONE': PC_TYPE_TONE, 'PC_PRIORITY_TAGS': PC_PRIORITY_TAGS,
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
            'PC_TYPE_TONE': PC_TYPE_TONE, 'PC_PRIORITY_TAGS': PC_PRIORITY_TAGS,
        })

    @http.route(['/portal/notification/recent'], type='json',
                auth='user', methods=['POST', 'GET'])
    def portal_notification_recent(self, **kw):
        """Popup chuông header (PC) — lazy-load 5 thông báo gần nhất + đếm chưa đọc.
        Perf: 1 search(limit=5) + 1 read-state lookup; chỉ chạy khi user mở popup."""
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()
        base = [
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ]
        recent = Noti.search(base, limit=5, order='date desc')
        Read = request.env['wujia.notification.read'].sudo()
        read_ids = set(Read.search([
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', recent.ids),
        ]).mapped('notification_id').ids) if recent else set()

        # Đếm chưa đọc trong 30 ngày (= bell badge) — đồng bộ unread-count.
        cutoff = fields.Datetime.now() - timedelta(days=RECENT_DAYS)
        accessible_ids = Noti.search(base + [('date', '>=', cutoff)]).ids
        read_count = Read.search_count([
            ('notification_id', 'in', accessible_ids),
            ('user_id', '=', request.env.user.id),
        ]) if accessible_ids else 0
        total_unread = max(0, len(accessible_ids) - read_count)

        items = [{
            'id': n.id,
            'name': n.name,
            'dispatch_number': n.dispatch_number or '',
            'date': n.date.strftime('%d/%m/%Y %H:%M') if n.date else '',
            'type_code': n.type_id.code or 'GEN',
            'type_name': n.type_id.name or '',
            'priority': n.priority or 'normal',
            'has_file': bool(n.attachment_ids),
            'is_read': n.id in read_ids,
            'url': '/portal/notification/%s' % n.id,
        } for n in recent]
        return {'notifications': items, 'total_unread': total_unread,
                'total': len(accessible_ids)}

    @http.route(['/portal/notification/mark-read'], type='json',
                auth='user', methods=['POST'])
    def portal_notification_mark_read(self, notification_ids=None, **kw):
        """Bulk mark-read. Idempotent — unique constraint trên DB."""
        if not notification_ids:
            return {'success': True, 'created': 0}
        try:
            ids = [int(i) for i in notification_ids]
        except (TypeError, ValueError):
            return {'error': 'invalid_ids'}
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()
        accessible = Noti.search([
            ('id', 'in', ids), ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ]).ids
        Read = request.env['wujia.notification.read'].sudo()
        existing = set(Read.search([
            ('notification_id', 'in', accessible),
            ('user_id', '=', request.env.user.id),
        ]).mapped('notification_id').ids)
        to_create = [
            {'notification_id': nid, 'user_id': request.env.user.id}
            for nid in accessible if nid not in existing
        ]
        if to_create:
            Read.create(to_create)
        return {'success': True, 'created': len(to_create)}

    @http.route(['/portal/notification/unread-count'], type='json',
                auth='user', methods=['POST', 'GET'])
    def portal_notification_unread_count(self, **kw):
        """Badge realtime — đếm noti accessible chưa đọc trong 30 ngày."""
        franchise_ids = get_active_franchise_ids_filter()
        cutoff = fields.Datetime.now() - timedelta(days=RECENT_DAYS)
        Noti = request.env['wujia.notification'].sudo()
        accessible_ids = Noti.search([
            ('published', '=', True),
            '|', ('franchise_ids', '=', False),
                 ('franchise_ids', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('date', '>=', cutoff),
        ]).ids
        if not accessible_ids:
            return {'count': 0}
        read_count = request.env['wujia.notification.read'].sudo().search_count([
            ('notification_id', 'in', accessible_ids),
            ('user_id', '=', request.env.user.id),
        ])
        return {'count': max(0, len(accessible_ids) - read_count)}
