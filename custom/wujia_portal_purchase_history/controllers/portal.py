from datetime import date, datetime, timedelta

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_id
from odoo.addons.wujia_portal_base.controllers.utils import (
    local_day_range_utc, page_numbers, portal_line_price_vals, portal_money,
    portal_tax_mapper, portal_tz, to_local_dt,
)


# WJ-PH-008: mặc định 10 theo source PC v1.5. PAGE_SIZE_OPTIONS là nguồn DUY NHẤT của
# select "n / trang" — giá trị ngoài bộ này (URL sửa tay) rơi về mặc định.
PAGE_SIZE = 10
PAGE_SIZE_OPTIONS = (10, 20, 50)

# state → (label VN, status_type). status_type = key ngữ nghĩa, template map sang badge CSS
# riêng (PC/mobile). 'cancel' KHÔNG có ở đây — đơn huỷ bị loại khỏi lịch sử (BA). State custom
# thêm về sau rơi về DEFAULT_STATE_META (BA: nhãn an toàn "Đang xử lý").
SALE_STATE_META = {
    'draft': ('Chờ xác nhận', 'pending'),
    'sent': ('Đã gửi', 'sent'),
    'sale': ('Đã xác nhận', 'confirmed'),
}
DEFAULT_STATE_META = ('Đang xử lý', 'pending')

# WJ-PH-003 — phương án (a) chủ dự án chốt 03/08: cửa hàng chỉ nhìn MỘT cột trạng thái.
# sale.order.state của Odoo 19 chỉ có draft/sent/sale/cancel; "Đang giao"/"Hoàn tất" suy từ
# batch_id.delivery_batch_status và ĐÈ trạng thái đơn khi đơn đã xác nhận.
DELIVERY_OVERRIDE_META = {
    'delivering': ('Đang giao', 'transit'),
    'done': ('Hoàn tất', 'done'),
}
# Trạng thái chuyến KHÔNG đè nhãn đơn (chuyến huỷ/chưa đi không làm đơn đổi trạng thái).
# False = batch cũ chưa có delivery_batch_status — vẫn phải nằm trong nhóm "Đã xác nhận".
DELIVERY_NEUTRAL_STATUSES = ['draft', 'assigned', 'loading', 'cancelled', False]

# Nhãn VN của stock.picking.batch.delivery_batch_status. Pin cứng tại đây vì source
# wujia_delivery đã chuyển sang tiếng Anh (sprint 44) — portal phải giữ tiếng Việt.
# Key phải khớp DELIVERY_BATCH_STATUS trong wujia_delivery/models/stock_picking_batch.py.
BATCH_STATUS_LABELS = {
    'draft': 'Nháp',
    'assigned': 'Đã gán xe',
    'loading': 'Đang chất hàng',
    'delivering': 'Đang giao',
    'done': 'Đã giao xong',
    'cancelled': 'Hủy chuyến',
}
BACKEND_REQUESTER_LABEL = 'Ngô Gia tạo đơn'

ERR_NO_STORE = 'Không xác định được cửa hàng đang thao tác. Vui lòng chọn lại cửa hàng.'
ERR_NOT_FOUND = 'Không tìm thấy đơn hàng hoặc bạn không có quyền xem đơn hàng này.'
ERR_DATE_RANGE = 'Từ ngày không được lớn hơn Đến ngày'


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_page_size(value):
    """WJ-PH-008 — chỉ nhận đúng bộ option của selector; số rác/lạ về mặc định 10."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return PAGE_SIZE
    return value if value in PAGE_SIZE_OPTIONS else PAGE_SIZE


def _state_meta(state):
    return SALE_STATE_META.get(state, DEFAULT_STATE_META)


def _order_status(order):
    """(label, status_type) hiển thị — trạng thái giao đè trạng thái đơn khi đơn đã xác nhận."""
    if order.state == 'sale':
        override = DELIVERY_OVERRIDE_META.get(order.batch_id.delivery_batch_status)
        if override:
            return override
    return _state_meta(order.state)


def _status_domain(key):
    """Domain của 1 nhãn trạng thái — khớp ĐÚNG cái _order_status hiển thị.

    Dùng danh sách dương cho nhánh 'sale': `not in` trên đường dẫn m2o loại luôn đơn
    chưa có batch (batch_id NULL) — đơn chờ giao sẽ biến mất khỏi bộ lọc.
    """
    if key in DELIVERY_OVERRIDE_META:
        return [('state', '=', 'sale'), ('batch_id.delivery_batch_status', '=', key)]
    if key == 'sale':
        return [
            ('state', '=', 'sale'),
            '|', ('batch_id', '=', False),
            ('batch_id.delivery_batch_status', 'in', DELIVERY_NEUTRAL_STATUSES),
        ]
    return [('state', '=', key)]


def _requester_display(order):
    # BA: đơn portal → tên user tạo; đơn backend (không có requester) → nhãn chung,
    # KHÔNG lộ create_uid.name nội bộ lên portal.
    return order.portal_requester_user_id.name or BACKEND_REQUESTER_LABEL


def _history_row_vals(order, line_count_map, batch_status_labels, tz):
    """Dataset lõi 1 dòng list — dùng chung PC + mobile."""
    label, status_type = _order_status(order)
    batch = order.batch_id
    return {
        'id': order.id,
        'name': order.name,
        # Odoo lưu naive UTC → đổi sang giờ user, template giữ nguyên .strftime (WJ-PH-002).
        'create_date': to_local_dt(order.create_date, tz),
        'date_order': to_local_dt(order.date_order, tz),
        'state_label': label,
        'status_type': status_type,
        'amount_total': order.amount_total,
        'currency_symbol': order.currency_id.symbol or '',
        'currency_decimals': order.currency_id.decimal_places or 0,
        'product_line_count': line_count_map.get(order.id, 0),
        'batch_name': batch.name or '',
        'batch_status_label': batch_status_labels.get(batch.delivery_batch_status, '') if batch else '',
        'requester_display': _requester_display(order),
    }


def _history_line_vals(line, taxes_of=None):
    """1 dòng sản phẩm — giá đã gồm thuế (BA).

    WJ-PH-005: đơn giá đi qua tax engine chứ KHÔNG lấy price_total/qty. Phép chia
    đó chỉ đúng khi thuế là % thuần — sai với thuế cố định (fixed amount), sai khi
    một dòng gánh nhiều thuế, và sai rounding ở currency lẻ.
    Thành tiền vẫn đọc thẳng `price_total` — đó là nguồn chân lý của Odoo."""
    qty = line.product_uom_qty or 0.0
    total = line.price_total or 0.0
    product = line.product_id
    order = line.order_id
    vals = portal_line_price_vals(
        product, line.price_unit, 1, order.currency_id,
        partner=order.partner_id, discount=line.discount,
        company=order.company_id,
        taxes=taxes_of(product) if taxes_of else None,
    )
    return {
        'product_name': product.display_name or line.name,
        'spec': product.wujia_packaging or '',
        'uom_name': line.product_uom_id.name or '',
        'quantity': qty,
        'discount': line.discount or 0.0,
        'unit_price_tax_included': vals['unit_price_tax_included'],
        'line_total_tax_included': total,
    }


def _history_detail_vals(order, batch_status_labels, tz):
    label, status_type = _order_status(order)
    lines = order.order_line.filtered(lambda ln: not ln.display_type)
    batch = order.batch_id
    taxes_of = portal_tax_mapper(order.partner_id, order.company_id)
    header = {
        'id': order.id,
        'name': order.name,
        'create_date': to_local_dt(order.create_date, tz),
        'date_order': to_local_dt(order.date_order, tz),
        'state_label': label,
        'status_type': status_type,
        'amount_total': order.amount_total,
        'currency_symbol': order.currency_id.symbol or '',
        'currency_decimals': order.currency_id.decimal_places or 0,
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
            'departure': to_local_dt(batch.actual_departure or batch.planned_departure, tz),
            'delivery_note': batch.delivery_note or '',
        }
    return {
        'header': header,
        'batch': batch_vals,
        # 1 mapper cho cả đơn: fiscal position resolve 1 lần, map_tax cache theo
        # bộ thuế gốc — đơn 40 dòng vẫn không đẻ 40 query.
        'lines': [_history_line_vals(ln, taxes_of) for ln in lines],
        'note': order.portal_note or '',
    }


class WujiaPortalHistory(http.Controller):

    def _batch_status_labels(self):
        # Nhãn VN cố định cho portal — KHÔNG đọc selection của field nữa: từ sprint 44 nhãn
        # backend là tiếng Anh (source English + vi_VN.po), còn portal luôn tiếng Việt bất kể
        # ngôn ngữ user. Cùng pattern SALE_STATE_META/STATE_LABELS ở các controller khác.
        return BATCH_STATUS_LABELS

    def _state_options(self, sale_order):
        # Option lọc trạng thái = selection sale.order.state trừ 'cancel' (đơn huỷ ẩn khỏi lịch sử)
        # + 2 nhãn suy từ chuyến giao (WJ-PH-003) → lọc được đủ 5 nhãn đang hiển thị.
        # Label ưu tiên nhãn VN của portal, fallback nhãn Odoo.
        opts = []
        for value, odoo_label in sale_order._fields['state'].selection:
            if value == 'cancel':
                continue
            opts.append((value, SALE_STATE_META.get(value, (odoo_label, ''))[0]))
        opts += [(key, meta[0]) for key, meta in DELIVERY_OVERRIDE_META.items()]
        return opts

    def _history_list_values(self, page=1, page_size=PAGE_SIZE, date_from='', date_to='',
                             state='', preset='', q='', **kw):
        """Context danh sách đơn — dùng chung cho trang đầy đủ và fragment AJAX."""
        SO = request.env['sale.order'].sudo()
        base_ctx = {
            'date_from': '', 'date_to': '', 'state': '', 'preset': '', 'q': '',
            'state_options': self._state_options(SO), 'filter_error': '',
            'page_size': PAGE_SIZE, 'page_size_options': PAGE_SIZE_OPTIONS,
            # Format tiền dùng chung mọi module portal — ký hiệu theo currency của đơn.
            'money': portal_money,
        }

        fid = get_active_franchise_id()
        if not fid:
            return dict(base_ctx, no_store=True, error=ERR_NO_STORE, rows=[], pager={})

        # Preset shortcut → khoảng create_date.
        today = date.today()
        if preset == 'this_month':
            date_from = today.replace(day=1).strftime('%Y-%m-%d')
            date_to = today.strftime('%Y-%m-%d')
        elif preset == 'last_month':
            last_month_end = today.replace(day=1) - timedelta(days=1)
            date_from = last_month_end.replace(day=1).strftime('%Y-%m-%d')
            date_to = last_month_end.strftime('%Y-%m-%d')

        df, dt = _parse_date(date_from), _parse_date(date_to)

        # WJ-PH-007 — khoảng ngày đảo ngược: không chạy query, giữ nguyên 2 ô đã nhập,
        # báo lỗi TẠI FilterBar (empty state "Chưa có đơn hàng" làm người dùng tưởng hết dữ liệu).
        if df and dt and df > dt:
            return dict(base_ctx, no_store=False, error='', rows=[], pager={},
                        date_from=date_from, date_to=date_to, state=state, preset=preset,
                        q=q, filter_error=ERR_DATE_RANGE)

        tz = portal_tz()

        # Domain: current store + loại đơn huỷ (BA). Lấy cả đơn portal lẫn backend.
        domain = [('franchise_id', '=', fid), ('state', '!=', 'cancel')]
        # Mốc ngày người dùng chọn là giờ địa phương, create_date lưu UTC → phải quy đổi,
        # không thì "hôm nay" bỏ sót đơn tạo 00:00–07:00 giờ VN (WJ-PH-002).
        utc_from, utc_to = local_day_range_utc(df, dt, tz)
        if utc_from:
            domain.append(('create_date', '>=', utc_from))
        if utc_to:
            domain.append(('create_date', '<=', utc_to))
        valid_states = ({v for v, _ in SO._fields['state'].selection} - {'cancel'}
                        | set(DELIVERY_OVERRIDE_META))
        if state and state in valid_states:
            domain += _status_domain(state)
        q = (q or '').strip()
        if q:
            domain.append(('name', 'ilike', q))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        page_size = _parse_page_size(page_size)

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
        rows = [_history_row_vals(o, line_count_map, batch_status_labels, tz) for o in orders]

        last_page = max(1, (total + page_size - 1) // page_size)
        pager = {
            'page': {'num': page},
            'page_count': last_page, 'page_total': total,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'page_nums': page_numbers(page, last_page),
            'offset': offset, 'count': len(rows),
            'querystring': self._qs(date_from=date_from, date_to=date_to, state=state, q=q,
                                    page_size=page_size if page_size != PAGE_SIZE else ''),
        }

        return dict(base_ctx, no_store=False, error='', rows=rows, pager=pager,
                    date_from=date_from, date_to=date_to, state=state, preset=preset, q=q,
                    page_size=page_size)

    @http.route(['/portal/purchase-history'], type='http', auth='user', sitemap=False)
    def portal_history_list(self, **kw):
        return request.render('wujia_portal_purchase_history.portal_history_list',
                              self._history_list_values(**kw))

    @http.route(['/portal/purchase-history/results'], type='http', auth='user', sitemap=False)
    def portal_history_results(self, **kw):
        """Fragment các khối kết quả cho lọc AJAX — cùng context, bỏ shell portal."""
        return request.render('wujia_portal_purchase_history.portal_history_results',
                              self._history_list_values(**kw))

    @http.route(['/portal/purchase-history/<int:order_id>'],
                type='http', auth='user', sitemap=False)
    def portal_history_detail(self, order_id, **kw):
        order = self._get_scoped_order(order_id)
        if not order:
            # Cùng 1 message cho "không tồn tại" và "khác cửa hàng" — không lộ tồn tại (BA).
            return request.render('wujia_portal_purchase_history.portal_history_detail',
                                  {'error': ERR_NOT_FOUND, 'detail': None,
                                   'money': portal_money})
        detail = _history_detail_vals(order, self._batch_status_labels(), portal_tz())
        return request.render('wujia_portal_purchase_history.portal_history_detail',
                              {'error': '', 'detail': detail,
                               'money': portal_money})

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
