from datetime import datetime

from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
    get_active_franchise_ids_filter,
)


# BA FINAL: popup 5, view list mặc định 10 record/trang (FE gửi limit trong danh sách cho phép).
PAGE_SIZE = 10
ALLOWED_LIMITS = (10, 20, 50)
POPUP_LIMIT = 5

# Bảng mã lỗi tiếng Việt (BA controller mapping — dễ hiểu cho user portal, không lộ lỗi kỹ thuật).
ERROR_MESSAGES = {
    'SESSION_EXPIRED': 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
    'STORE_NOT_SELECTED': 'Vui lòng chọn cửa hàng trước khi thao tác.',
    'STORE_ACCESS_DENIED': 'Bạn không có quyền thao tác với cửa hàng này.',
    'INVALID_DATE_RANGE': 'Từ ngày không được lớn hơn đến ngày.',
    'INVALID_FILTER': 'Bộ lọc không hợp lệ. Vui lòng kiểm tra lại.',
    'INVALID_PAGE_SIZE': 'Số lượng bản ghi mỗi trang không hợp lệ.',
    'ANNOUNCEMENT_NOT_AVAILABLE': 'Thông báo không tồn tại, đã bị thu hồi hoặc bạn không có quyền xem.',
    'MARK_READ_FAILED': 'Chưa thể cập nhật trạng thái đã đọc. Vui lòng thử lại.',
    'ATTACHMENT_NOT_AVAILABLE': 'Tài liệu không tồn tại hoặc bạn không có quyền tải xuống.',
}

# PC desktop — type code → (tone css, feather icon); priority → (nhãn, badge css) theo keys BA.
PC_TYPE_TONE = {
    'URG': ('wj-pc-noti-type--red', 'icon-alert-triangle'),
    'GEN': ('wj-pc-noti-type--cyan', 'icon-bell'),
    'PROMO': ('wj-pc-noti-type--amber', 'icon-gift'),
    'SYS': ('wj-pc-noti-type--violet', 'icon-settings'),
    'OTH': ('wj-pc-noti-type--green', 'icon-info'),
}
# Nhãn VN của wujia.notification.priority. Pin cứng tại đây vì source đã chuyển sang
# tiếng Anh (sprint 44) — portal phải giữ tiếng Việt.
# Key phải khớp PRIORITY_SELECTION trong wujia_portal_notification/models/wujia_notification.py.
PORTAL_PRIORITY_LABELS = {
    'normal': 'Thông thường',
    'important': 'Quan trọng',
    'urgent': 'Cần làm',
}
PC_PRIORITY_TAGS = {
    'urgent': (PORTAL_PRIORITY_LABELS['urgent'], 'wj-pc-badge--done'),
    'important': (PORTAL_PRIORITY_LABELS['important'], 'wj-pc-badge--transit'),
    'normal': (PORTAL_PRIORITY_LABELS['normal'], 'wj-pc-badge--confirmed'),
}
VALID_PRIORITIES = ('normal', 'important', 'urgent')


def _err(code, **extra):
    """Payload lỗi JSON — cùng shape với wujia_portal_sale để FE portal xử lý đồng nhất."""
    res = {'success': False, 'error': code, 'message': ERROR_MESSAGES.get(code, code)}
    res.update(extra)
    return res


def _parse_date(value):
    """'YYYY-MM-DD' (HTML date input) → date, hoặc None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _franchise_clause(franchise_ids):
    """Broadcast (franchise_ids trống) HOẶC target đúng cửa hàng đang thao tác."""
    ids = list(franchise_ids) if franchise_ids else [-1]
    return ['|', ('franchise_ids', '=', False), ('franchise_ids', 'in', ids)]


def _history_domain(franchise_ids):
    """Lịch sử: mọi thông báo đã phát hành đúng đối tượng (gồm cả đã hết hiệu lực)."""
    return (
        [('is_published_portal', '=', True)]
        + _franchise_clause(franchise_ids)
        + [('published_date', '<=', fields.Datetime.now())]
    )


def _effective_domain(franchise_ids):
    """Còn hiệu lực: đã phát hành + chưa hết hạn — dùng cho popup, badge, đếm chưa đọc."""
    now = fields.Datetime.now()
    return (
        _history_domain(franchise_ids)
        + ['|', ('expired_date', '=', False), ('expired_date', '>=', now)]
    )


class WujiaPortalNotification(http.Controller):

    # ---- helpers (read status theo user + cửa hàng hiện tại, batched) ----
    def _read_ids(self, noti_ids, franchise_id):
        """1 query — id thông báo user đã đọc TẠI cửa hàng hiện tại."""
        if not noti_ids:
            return set()
        dom = [
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', list(noti_ids)),
        ]
        if franchise_id:
            dom.append(('franchise_id', '=', franchise_id))
        return set(request.env['wujia.notification.read'].sudo()
                   .search(dom).mapped('notification_id').ids)

    def _unread_count(self, franchise_ids, franchise_id):
        """Badge = số thông báo còn hiệu lực CHƯA đọc của user tại cửa hàng hiện tại.

        2 câu đếm, KHÔNG nạp id ra Python: badge chạy trên mọi trang portal, với 1500
        cửa hàng thì `search(...).ids` là kéo cả bảng về mỗi request. `any` đẩy điều
        kiện "còn hiệu lực" xuống subquery của notification_id.
        """
        eff_domain = _effective_domain(franchise_ids)
        total_eff = request.env['wujia.notification'].sudo().search_count(eff_domain)
        if not total_eff:
            return 0
        dom = [
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'any', eff_domain),
        ]
        if franchise_id:
            dom.append(('franchise_id', '=', franchise_id))
        read = request.env['wujia.notification.read'].sudo().search_count(dom)
        return max(0, total_eff - read)

    def _notification_list_values(self, page=1, type_id=None, keyword='',
                                  tab='recent', unread=None, read_status=None,
                                  date_from='', date_to='', priority='',
                                  limit=None, **kw):
        """Context danh sách thông báo — dùng chung cho trang đầy đủ và fragment AJAX."""
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        Noti = request.env['wujia.notification'].sudo()

        # Trạng thái đọc canonical {all,read,unread}; back-compat ?unread=1.
        if read_status not in ('all', 'read', 'unread'):
            read_status = 'unread' if unread else 'all'

        # List = lịch sử (gồm cả hết hiệu lực); badge "Đã hết hiệu lực" phân biệt.
        domain = _history_domain(franchise_ids)

        # Lọc theo ngày gửi + validate date_from <= date_to.
        df, dt = _parse_date(date_from), _parse_date(date_to)
        date_error = ''
        if df and dt and df > dt:
            date_error = ERROR_MESSAGES['INVALID_DATE_RANGE']
            df = dt = None
        if df:
            domain.append(('published_date', '>=', datetime.combine(df, datetime.min.time())))
        if dt:
            domain.append(('published_date', '<=', datetime.combine(dt, datetime.max.time())))

        tid = _parse_int(type_id)
        if tid:
            domain.append(('type_id', '=', tid))
        if keyword:
            domain += ['|', '|',
                       ('name', 'ilike', keyword),
                       ('dispatch_number', 'ilike', keyword),
                       ('summary', 'ilike', keyword)]
        if priority in VALID_PRIORITIES:
            domain.append(('priority', '=', priority))

        # Lọc đã đọc / chưa đọc theo user + cửa hàng.
        if read_status in ('read', 'unread'):
            read_dom = [('user_id', '=', request.env.user.id)]
            if active_fid:
                read_dom.append(('franchise_id', '=', active_fid))
            read_noti_ids = request.env['wujia.notification.read'].sudo().search(
                read_dom).mapped('notification_id').ids
            if read_status == 'read':
                domain.append(('id', 'in', read_noti_ids))
            else:  # unread — chưa đọc + CÒN hiệu lực (hết hạn không tính chưa đọc)
                now = fields.Datetime.now()
                domain += [('id', 'not in', read_noti_ids),
                           '|', ('expired_date', '=', False), ('expired_date', '>=', now)]

        # Page size — chỉ nhận giá trị cho phép, else default.
        lim = _parse_int(limit) or PAGE_SIZE
        if lim not in ALLOWED_LIMITS:
            lim = PAGE_SIZE
        page = max(1, _parse_int(page) or 1)
        offset = (page - 1) * lim

        total = Noti.search_count(domain)
        notifications = Noti.search(domain, limit=lim, offset=offset,
                                    order='is_pinned desc, published_date desc')

        read_ids = self._read_ids(notifications.ids, active_fid)
        cnt_unread = self._unread_count(franchise_ids, active_fid)

        types = request.env['wujia.notification.type'].sudo().search(
            [('active', '=', True)], order='sequence')
        last_page = max(1, (total + lim - 1) // lim)
        querystring = '&'.join(
            f'{k}={v}' for k, v in
            [('tab', tab), ('type_id', tid or ''), ('keyword', keyword),
             ('read_status', read_status), ('unread', unread or ''),
             ('date_from', date_from or ''), ('date_to', date_to or ''),
             ('priority', priority or ''), ('limit', lim)] if v
        )
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': querystring,
        }
        return {
            'notifications': notifications,
            'read_ids': read_ids, 'types': types, 'pager': pager,
            'type_id': tid, 'keyword': keyword, 'tab': tab,
            'total': total, 'cnt_unread': cnt_unread,
            'unread': '1' if read_status == 'unread' else '',
            'read_status': read_status, 'date_error': date_error,
            'date_from': date_from, 'date_to': date_to, 'priority': priority,
            'page_size': lim,
            'PC_TYPE_TONE': PC_TYPE_TONE, 'PC_PRIORITY_TAGS': PC_PRIORITY_TAGS,
        }

    @http.route(['/portal/notification'], type='http', auth='user', sitemap=False)
    def portal_notification_list(self, **kw):
        return request.render('wujia_portal_notification.portal_notification_list',
                              self._notification_list_values(**kw))

    @http.route(['/portal/notification/results'], type='http', auth='user', sitemap=False)
    def portal_notification_results(self, **kw):
        """Fragment các khối kết quả cho lọc AJAX — cùng context, bỏ shell portal."""
        return request.render('wujia_portal_notification.portal_notification_results',
                              self._notification_list_values(**kw))

    @http.route(['/portal/notification/<int:notification_id>'],
                type='http', auth='user', sitemap=False)
    def portal_notification_detail(self, notification_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        Noti = request.env['wujia.notification'].sudo()
        # History domain → cho phép mở lại thông báo đã hết hiệu lực từ lịch sử.
        noti = Noti.search(
            [('id', '=', notification_id)] + _history_domain(franchise_ids), limit=1)
        if not noti:
            return request.redirect('/portal/notification')

        # Ghi nhận đã đọc theo user + cửa hàng: tạo mới giữ read_date, mở lại chỉ đổi last_open_date.
        # Spec F §8.11 — chỉ ghi read status khi có cửa hàng hiện tại; chưa chọn thì vẫn cho ĐỌC
        # nội dung, chỉ không ghi row (tránh row franchise_id NULL).
        if active_fid:
            Read = request.env['wujia.notification.read'].sudo()
            existing = Read.search([
                ('notification_id', '=', noti.id),
                ('user_id', '=', request.env.user.id),
                ('franchise_id', '=', active_fid),
            ], limit=1)
            now = fields.Datetime.now()
            if existing:
                existing.last_open_date = now
            else:
                Read.create({
                    'notification_id': noti.id,
                    'user_id': request.env.user.id,
                    'franchise_id': active_fid,
                    'read_date': now, 'last_open_date': now,
                })
        return request.render('wujia_portal_notification.portal_notification_detail', {
            'noti': noti,
            'PC_TYPE_TONE': PC_TYPE_TONE, 'PC_PRIORITY_TAGS': PC_PRIORITY_TAGS,
        })

    @http.route(['/portal/notification/recent'], type='json',
                auth='user', methods=['POST', 'GET'])
    def portal_notification_recent(self, **kw):
        """Popup chuông header — 5 thông báo CÒN HIỆU LỰC gần nhất + đếm chưa đọc.
        Perf: 1 search(limit=5) + 1 read-lookup + đếm effective; chỉ chạy khi user mở popup."""
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        Noti = request.env['wujia.notification'].sudo()
        eff = _effective_domain(franchise_ids)
        recent = Noti.search(eff, limit=POPUP_LIMIT, order='is_pinned desc, published_date desc')
        read_ids = self._read_ids(recent.ids, active_fid)
        total_unread = self._unread_count(franchise_ids, active_fid)
        total_eff = Noti.search_count(eff)

        items = [{
            'id': n.id,
            'name': n.name,
            'dispatch_number': n.dispatch_number or '',
            'date': n.published_date.strftime('%d/%m/%Y %H:%M') if n.published_date else '',
            'type_code': n.type_id.code or 'GEN',
            'type_name': n.type_id.name or '',
            'priority': n.priority or 'normal',
            'priority_label': PORTAL_PRIORITY_LABELS.get(n.priority or 'normal', ''),
            'has_file': bool(n.attachment_ids),
            'is_read': n.id in read_ids,
            'url': '/portal/notification/%s' % n.id,
        } for n in recent]
        return {'notifications': items, 'total_unread': total_unread, 'total': total_eff}

    @http.route(['/portal/notification/mark-all-read'], type='json',
                auth='user', methods=['POST'])
    def portal_notification_mark_all_read(self, **kw):
        """BA row 6 — đánh dấu TẤT CẢ thông báo còn hiệu lực chưa đọc của user tại cửa hàng
        hiện tại. Không nhận ids/filter. Không set last_open_date (chưa thực sự mở nội dung)."""
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        if not active_fid:
            # Spec F §8.11 + §18 — chưa chọn cửa hàng thì không ghi read status.
            return _err('STORE_NOT_SELECTED')
        Noti = request.env['wujia.notification'].sudo()
        Read = request.env['wujia.notification.read'].sudo()
        eff_ids = Noti.search(_effective_domain(franchise_ids)).ids
        if not eff_ids:
            return {'success': True, 'updated_count': 0, 'unread_count': 0}
        existing = set(Read.search([
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', eff_ids),
            ('franchise_id', '=', active_fid),
        ]).mapped('notification_id').ids)
        now = fields.Datetime.now()
        to_create = [
            {'notification_id': nid, 'user_id': request.env.user.id,
             'franchise_id': active_fid, 'read_date': now}
            for nid in eff_ids if nid not in existing
        ]
        if to_create:
            Read.create(to_create)
        return {'success': True, 'updated_count': len(to_create), 'unread_count': 0}

    @http.route(['/portal/notification/mark-read'], type='json',
                auth='user', methods=['POST'])
    def portal_notification_mark_read(self, notification_ids=None, **kw):
        """Bulk mark-read theo ids (back-compat). Idempotent — unique (noti,user,store)."""
        if not notification_ids:
            return {'success': True, 'created': 0}
        try:
            ids = [int(i) for i in notification_ids]
        except (TypeError, ValueError):
            return {'error': 'invalid_ids'}
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        if not active_fid:
            # Spec F §8.11 + §18 — chưa chọn cửa hàng thì không ghi read status.
            return _err('STORE_NOT_SELECTED')
        Noti = request.env['wujia.notification'].sudo()
        accessible = Noti.search(
            [('id', 'in', ids)] + _history_domain(franchise_ids)).ids
        Read = request.env['wujia.notification.read'].sudo()
        existing = set(Read.search([
            ('user_id', '=', request.env.user.id),
            ('notification_id', 'in', accessible),
            ('franchise_id', '=', active_fid),
        ]).mapped('notification_id').ids)
        now = fields.Datetime.now()
        to_create = [
            {'notification_id': nid, 'user_id': request.env.user.id,
             'franchise_id': active_fid, 'read_date': now, 'last_open_date': now}
            for nid in accessible if nid not in existing
        ]
        if to_create:
            Read.create(to_create)
        return {'success': True, 'created': len(to_create)}

    @http.route(['/portal/notification/unread-count'], type='json',
                auth='user', methods=['POST', 'GET'])
    def portal_notification_unread_count(self, **kw):
        """Badge realtime — thông báo còn hiệu lực chưa đọc của user tại cửa hàng hiện tại."""
        franchise_ids = get_active_franchise_ids_filter()
        active_fid = get_active_franchise_id()
        return {'count': self._unread_count(franchise_ids, active_fid)}

    @http.route(['/portal/notification/<int:notification_id>/attachment/<int:attachment_id>'],
                type='http', auth='user', sitemap=False)
    def portal_notification_attachment(self, notification_id, attachment_id, **kw):
        """BA row 7 — tải file đính kèm CÓ kiểm quyền: thông báo phải accessible + attachment
        phải thuộc đúng thông báo (đóng IDOR /web/content/ir.attachment/<id>)."""
        franchise_ids = get_active_franchise_ids_filter()
        Noti = request.env['wujia.notification'].sudo()
        noti = Noti.search(
            [('id', '=', notification_id)] + _history_domain(franchise_ids), limit=1)
        if not noti:
            raise NotFound()
        att = request.env['ir.attachment'].sudo().search([
            ('id', '=', attachment_id),
            ('id', 'in', noti.attachment_ids.ids),
        ], limit=1)
        if not att:
            raise Forbidden()
        return request.env['ir.binary']._get_stream_from(att).get_response(
            as_attachment=True,
        )
