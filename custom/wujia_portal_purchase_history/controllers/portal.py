from datetime import date, datetime, time as dt_time, timedelta

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_id


PAGE_SIZE = 20
PAGE_SIZE_MAX = 100

# state → (label VN, status_type). status_type = key ngữ nghĩa, template map sang badge CSS
# riêng (PC/mobile). 'cancel' KHÔNG có ở đây — đơn huỷ bị loại khỏi lịch sử (BA). State custom
# thêm về sau rơi về DEFAULT_STATE_META (BA: nhãn an toàn "Đang xử lý").
SALE_STATE_META = {
    'draft': ('Chờ xác nhận', 'pending'),
    'sent': ('Đã gửi', 'sent'),
    'sale': ('Đã xác nhận', 'confirmed'),
}
DEFAULT_STATE_META = ('Đang xử lý', 'pending')
BACKEND_REQUESTER_LABEL = 'Ngô Gia tạo đơn'

ERR_NO_STORE = 'Không xác định được cửa hàng đang thao tác. Vui lòng chọn lại cửa hàng.'
ERR_NOT_FOUND = 'Không tìm thấy đơn hàng hoặc bạn không có quyền xem đơn hàng này.'


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


def _state_meta(state):
    return SALE_STATE_META.get(state, DEFAULT_STATE_META)


def _requester_display(order):
    # BA: đơn portal → tên user tạo; đơn backend (không có requester) → nhãn chung,
    # KHÔNG lộ create_uid.name nội bộ lên portal.
    return order.portal_requester_user_id.name or BACKEND_REQUESTER_LABEL


def _history_row_vals(order, line_count_map, batch_status_labels):
    """Dataset lõi 1 dòng list — dùng chung PC + mobile."""
    label, status_type = _state_meta(order.state)
    batch = order.batch_id
    return {
        'id': order.id,
        'name': order.name,
        'create_date': order.create_date,
        'date_order': order.date_order,
        'state_label': label,
        'status_type': status_type,
        'amount_total': order.amount_total,
        'currency_symbol': order.currency_id.symbol or '',
        'product_line_count': line_count_map.get(order.id, 0),
        'batch_name': batch.name or '',
        'batch_status_label': batch_status_labels.get(batch.delivery_batch_status, '') if batch else '',
        'requester_display': _requester_display(order),
    }


def _history_line_vals(line):
    """1 dòng sản phẩm — giá đã gồm thuế (BA)."""
    qty = line.product_uom_qty or 0.0
    total = line.price_total or 0.0
    return {
        'product_name': line.product_id.display_name or line.name,
        'spec': line.product_id.description_ecommerce or '',
        'uom_name': line.product_uom_id.name or '',
        'quantity': qty,
        'discount': line.discount or 0.0,
        # Đơn giá sau chiết khấu, đã gồm thuế = thành tiền đã thuế / số lượng.
        'unit_price_tax_included': (total / qty) if qty else total,
        'line_total_tax_included': total,
    }


def _history_detail_vals(order, batch_status_labels):
    label, status_type = _state_meta(order.state)
    lines = order.order_line.filtered(lambda ln: not ln.display_type)
    batch = order.batch_id
    header = {
        'id': order.id,
        'name': order.name,
        'create_date': order.create_date,
        'date_order': order.date_order,
        'state_label': label,
        'status_type': status_type,
        'amount_total': order.amount_total,
        'currency_symbol': order.currency_id.symbol or '',
        'franchise_code': order.franchise_id.code or '',
        'franchise_name': order.franchise_id.name or '',
        'requester_display': _requester_display(order),
        'product_line_count': len(lines),
    }
    batch_vals = None
    if batch:
        batch_vals = {
            'name': batch.name or '',
            'status_label': batch_status_labels.get(batch.delivery_batch_status, ''),
            'departure': batch.actual_departure or batch.planned_departure,
            'delivery_note': batch.delivery_note or '',
        }
    return {
        'header': header,
        'batch': batch_vals,
        'lines': [_history_line_vals(ln) for ln in lines],
        'note': order.portal_note or '',
    }


class WujiaPortalHistory(http.Controller):

    def _batch_status_labels(self):
        # Label lấy động từ selection của field → không hardcode, tự theo wujia_delivery.
        return dict(request.env['stock.picking.batch']._fields['delivery_batch_status'].selection)

    def _state_options(self, sale_order):
        # Option lọc trạng thái = selection sale.order.state trừ 'cancel' (đơn huỷ ẩn khỏi lịch sử).
        # Label ưu tiên nhãn VN của portal, fallback nhãn Odoo.
        opts = []
        for value, odoo_label in sale_order._fields['state'].selection:
            if value == 'cancel':
                continue
            opts.append((value, SALE_STATE_META.get(value, (odoo_label, ''))[0]))
        return opts

    @http.route(['/portal/purchase-history'], type='http', auth='user', sitemap=False)
    def portal_history_list(self, page=1, page_size=PAGE_SIZE, date_from='', date_to='',
                            state='', preset='', q='', **kw):
        SO = request.env['sale.order'].sudo()
        base_ctx = {
            'date_from': '', 'date_to': '', 'state': '', 'preset': '', 'q': '',
            'state_options': self._state_options(SO),
        }

        fid = get_active_franchise_id()
        if not fid:
            return request.render('wujia_portal_purchase_history.portal_history_list', dict(
                base_ctx, no_store=True, error=ERR_NO_STORE, rows=[], pager={}))

        # Preset shortcut → khoảng create_date.
        today = date.today()
        if preset == 'this_month':
            date_from = today.replace(day=1).strftime('%Y-%m-%d')
            date_to = today.strftime('%Y-%m-%d')
        elif preset == 'last_month':
            last_month_end = today.replace(day=1) - timedelta(days=1)
            date_from = last_month_end.replace(day=1).strftime('%Y-%m-%d')
            date_to = last_month_end.strftime('%Y-%m-%d')

        # Domain: current store + loại đơn huỷ (BA). Lấy cả đơn portal lẫn backend.
        domain = [('franchise_id', '=', fid), ('state', '!=', 'cancel')]
        df, dt = _parse_date(date_from), _parse_date(date_to)
        if df:
            domain.append(('create_date', '>=', datetime.combine(df, dt_time.min)))
        if dt:
            domain.append(('create_date', '<=', datetime.combine(dt, dt_time.max)))
        valid_states = {v for v, _ in SO._fields['state'].selection} - {'cancel'}
        if state and state in valid_states:
            domain.append(('state', '=', state))
        q = (q or '').strip()
        if q:
            domain.append(('name', 'ilike', q))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = min(max(1, int(page_size)), PAGE_SIZE_MAX)
        except (TypeError, ValueError):
            page_size = PAGE_SIZE

        total = SO.search_count(domain)
        offset = (page - 1) * page_size
        orders = SO.search(domain, limit=page_size, offset=offset, order='create_date desc')

        # Perf: đếm dòng SP (loại section/note) bằng 1 read_group thay vì len(order_line)/đơn
        # → không load toàn bộ line của cả trang (an toàn 1500 user).
        line_count_map = {}
        if orders:
            for group in request.env['sale.order.line'].sudo().read_group(
                [('order_id', 'in', orders.ids), ('display_type', '=', False)],
                ['order_id'], ['order_id'],
            ):
                line_count_map[group['order_id'][0]] = group['order_id_count']

        batch_status_labels = self._batch_status_labels()
        rows = [_history_row_vals(o, line_count_map, batch_status_labels) for o in orders]

        last_page = max(1, (total + page_size - 1) // page_size)
        pager = {
            'page': {'num': page},
            'page_count': last_page, 'page_total': total,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'page_nums': _page_numbers(page, last_page),
            'offset': offset, 'count': len(rows),
            'querystring': self._qs(date_from=date_from, date_to=date_to, state=state, q=q,
                                    page_size=page_size if page_size != PAGE_SIZE else ''),
        }

        return request.render('wujia_portal_purchase_history.portal_history_list', dict(
            base_ctx, no_store=False, error='', rows=rows, pager=pager,
            date_from=date_from, date_to=date_to, state=state, preset=preset, q=q))

    @http.route(['/portal/purchase-history/<int:order_id>'],
                type='http', auth='user', sitemap=False)
    def portal_history_detail(self, order_id, **kw):
        order = self._get_scoped_order(order_id)
        if not order:
            # Cùng 1 message cho "không tồn tại" và "khác cửa hàng" — không lộ tồn tại (BA).
            return request.render('wujia_portal_purchase_history.portal_history_detail',
                                  {'error': ERR_NOT_FOUND, 'detail': None})
        detail = _history_detail_vals(order, self._batch_status_labels())
        return request.render('wujia_portal_purchase_history.portal_history_detail',
                              {'error': '', 'detail': detail})

    @http.route(['/portal/purchase-history/<int:order_id>.pdf'],
                type='http', auth='user', sitemap=False)
    def portal_history_download_pdf(self, order_id, **kw):
        """Render hóa đơn PDF qua Odoo native report engine."""
        order = self._get_scoped_order(order_id)
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

    def _get_scoped_order(self, order_id):
        """Đơn thuộc current store + không huỷ. Kiểm tra lại quyền mọi lần, không tin
        việc user vừa mở từ list (chống IDOR đổi URL)."""
        fid = get_active_franchise_id()
        if not fid:
            return request.env['sale.order'].browse()
        return request.env['sale.order'].sudo().search([
            ('id', '=', order_id),
            ('franchise_id', '=', fid),
            ('state', '!=', 'cancel'),
        ], limit=1)

    def _qs(self, **kw):
        return '&'.join(f'{k}={v}' for k, v in kw.items() if v)
