from datetime import date, datetime, timedelta

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)


PAGE_SIZE = 20

STATE_BADGES = {
    'draft': ('Mới', 'wujia-badge-muted'),
    'sent': ('Đã gửi', 'wujia-badge-info'),
    'sale': ('Đã xác nhận', 'wujia-badge-success'),
    'done': ('Hoàn thành', 'wujia-badge-success'),
    'cancel': ('Đã hủy', 'wujia-badge-danger'),
}

# Sprint 13 — Mobile order-history badges (Figma 4445:4). UI-ONLY relabel: nhãn
# theo wording Figma cho bản mobile (<992px), TÁCH khỏi STATE_BADGES desktop (giữ
# nguyên). "Đang giao" (warning) để sẵn nhưng CHƯA có state nào của sale.order trỏ
# tới — sẽ wire từ batch/delivery state ở sprint sau (D1: status = UI tạm).
MOBILE_STATE_BADGES = {
    'draft':    ('Mới', 'wujia-badge-muted'),
    'sent':     ('Đã gửi', 'wujia-badge-info'),
    'sale':     ('Đã xử lý', 'wujia-badge-success'),
    'shipping': ('Đang giao', 'wujia-badge-warning'),  # placeholder — wire batch sau
    'done':     ('Hoàn tất', 'wujia-badge-success'),
    'cancel':   ('Đã hủy', 'wujia-badge-danger'),
}

# Sprint PC-2 — PC/desktop badges (Figma 4643:258/4643:2). Map state → (label, wj-pc-badge--variant).
PC_STATE_BADGES = {
    'draft':  ('Chờ xác nhận', 'wj-pc-badge--pending'),
    'sent':   ('Đã gửi', 'wj-pc-badge--sent'),
    'sale':   ('Đã xác nhận', 'wj-pc-badge--confirmed'),
    'done':   ('Hoàn tất', 'wj-pc-badge--done'),
    'cancel': ('Đã hủy', 'wj-pc-badge--cancel'),
}


def _page_numbers(current, last, edge=1, around=1):
    """Windowed page list cho numbered pager: [1, '…', 4, 5, 6, '…', 20]."""
    if last < 1:
        return []
    keep = set(range(1, edge + 1)) | set(range(last - edge + 1, last + 1))
    keep |= set(range(current - around, current + around + 1))
    pages = sorted(p for p in keep if 1 <= p <= last)
    result, prev = [], 0
    for p in pages:
        if prev and p - prev > 1:
            result.append('…')
        result.append(p)
        prev = p
    return result


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


class WujiaPortalHistory(http.Controller):

    @http.route(['/portal/purchase-history'], type='http', auth='user', sitemap=False)
    def portal_history_list(self, page=1, date_from='', date_to='', state='', preset='', q='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_purchase_history.portal_history_list', {
                'orders': [], 'pager': {}, 'no_franchise': True,
                'state_badges': STATE_BADGES, 'mobile_state_badges': MOBILE_STATE_BADGES,
                'pc_state_badges': PC_STATE_BADGES,
                'date_from': '', 'date_to': '',
                'state': '', 'preset': '', 'q': '',
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
        # Sprint 13: tìm theo Mã đơn (sale.order.name có trigram index → ilike nhanh
        # cả trên bảng lớn, an toàn perf 1500 user).
        q = (q or '').strip()
        if q:
            domain.append(('name', 'ilike', q))

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
            'page_nums': _page_numbers(page, last_page),
            'offset': offset, 'count': len(orders),
            'querystring': self._qs(date_from=date_from, date_to=date_to, state=state, q=q),
        }

        return request.render('wujia_portal_purchase_history.portal_history_list', {
            'no_franchise': False,
            'orders': orders, 'pager': pager,
            'date_from': date_from, 'date_to': date_to,
            'state': state, 'preset': preset, 'q': q,
            'state_badges': STATE_BADGES,
            'mobile_state_badges': MOBILE_STATE_BADGES,
            'pc_state_badges': PC_STATE_BADGES,
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
            'mobile_state_badges': MOBILE_STATE_BADGES,
            'pc_state_badges': PC_STATE_BADGES,
        })

    @http.route(['/portal/purchase-history/<int:order_id>.pdf'],
                type='http', auth='user', sitemap=False)
    def portal_history_download_pdf(self, order_id, **kw):
        """Render hóa đơn PDF qua Odoo native report engine."""
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            raise NotFound()
        order = request.env['sale.order'].sudo().search([
            ('id', '=', order_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not order:
            raise NotFound()
        report_ref = 'sale.action_report_saleorder'
        report = request.env.ref(report_ref, raise_if_not_found=False)
        if not report:
            raise NotFound()
        pdf_bytes, _ = report.sudo()._render_qweb_pdf(report_ref, [order.id])
        filename = f'{order.name or "order"}.pdf'.replace('/', '_')
        return request.make_response(
            pdf_bytes,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"'),
                ('Cache-Control', 'private, no-cache'),
            ],
        )

    def _qs(self, **kw):
        return '&'.join(f'{k}={v}' for k, v in kw.items() if v)
