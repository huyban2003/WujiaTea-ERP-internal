"""Wujia portal — Return Request controller (single-product, BA spec K).

Routes:
- GET  /portal/return                              list (filter state/date/q)
- GET, POST /portal/return/new                     create draft or submit
- GET  /portal/return/<int>                        detail
- GET  /portal/return/<int>/attachment/<int>       download attachment
"""
import json
import logging
from datetime import datetime

from werkzeug.exceptions import Forbidden, NotFound

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    DEFAULT_DOC_MIME,
    attach_files_to_record,
)

_logger = logging.getLogger(__name__)

PAGE_SIZE = 20
MIN_IMAGES_BEFORE_SEND = 3

# Trạng thái portal thấy (label + badge class).
STATE_LABELS = {
    'draft': ('Nháp', 'wujia-badge-muted'),
    'submitted': ('Đã gửi', 'wujia-badge-info'),
    'reviewing': ('Đang xét', 'wujia-badge-warning'),
    'approved': ('Đã duyệt', 'wujia-badge-success'),
    'processing': ('Đang xử lý', 'wujia-badge-warning'),
    'done': ('Đã xử lý', 'wujia-badge-success'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'cancelled': ('Đã huỷ', 'wujia-badge-muted'),
}

# Phương án xử lý HQ chốt khi duyệt.
RESOLUTION_LABELS = {
    'exchange': 'Đổi hàng',
    'return': 'Trả hàng',
    'compensation': 'Bù hàng',
    'refuse': 'Từ chối',
}

# Tình trạng bù hàng (label + badge class) — hiển thị tiến độ bù cho cửa hàng.
COMPENSATION_STATUS_LABELS = {
    'none': ('Chưa xử lý', 'wujia-badge-muted'),
    'allocated': ('Đã lên đơn bù', 'wujia-badge-info'),
    'partial': ('Đang bù', 'wujia-badge-warning'),
    'done': ('Đã bù đủ', 'wujia-badge-success'),
}


class WujiaPortalReturn(http.Controller):

    @http.route(['/portal/return'], type='http', auth='user', sitemap=False)
    def portal_return_list(self, page=1, state='', date_from='', date_to='', q='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_return.portal_return_list', {
                'returns': [], 'pager': {}, 'state_labels': STATE_LABELS,
                'no_franchise': True, 'state': '', 'date_from': '', 'date_to': '',
                'q': '',
            })

        domain = [('franchise_id', 'in', list(franchise_ids))]
        if state and state in STATE_LABELS:
            domain.append(('state', '=', state))
        q = (q or '').strip()
        if q:
            domain += ['|', ('name', 'ilike', q), ('sale_order_id.name', 'ilike', q)]
        if date_from:
            try:
                df = datetime.strptime(date_from, '%Y-%m-%d')
                domain.append(('request_date', '>=', df))
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                dt = dt.replace(hour=23, minute=59, second=59)
                domain.append(('request_date', '<=', dt))
            except ValueError:
                pass

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        Model = request.env['wujia.return.request'].sudo()
        total = Model.search_count(domain)
        returns = Model.search(domain, limit=PAGE_SIZE, offset=offset,
                               order='request_date desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        pager = {
            'page': {'num': page}, 'page_count': last_page,
            'page_previous': {'num': max(1, page - 1)},
            'page_next': {'num': min(last_page, page + 1)},
            'querystring': '&'.join(
                f'{k}={v}' for k, v in
                [('state', state), ('date_from', date_from), ('date_to', date_to),
                 ('q', q)]
                if v
            ),
        }
        return request.render('wujia_portal_return.portal_return_list', {
            'no_franchise': False, 'returns': returns, 'pager': pager,
            'state_labels': STATE_LABELS,
            'comp_status_labels': COMPENSATION_STATUS_LABELS, 'state': state,
            'date_from': date_from, 'date_to': date_to, 'q': q,
        })

    @http.route(['/portal/return/new'], type='http', auth='user',
                methods=['GET', 'POST'], sitemap=False, csrf=True)
    def portal_return_new(self, **post):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return')

        if request.httprequest.method != 'POST':
            return self._render_form()

        try:
            vals, action = self._parse_payload(post, franchise_ids)
        except ValidationError as e:
            return self._render_form(error=str(e), prefill=post)

        try:
            rr = request.env['wujia.return.request'].sudo().create(vals)
        except (ValidationError, Exception) as e:
            _logger.exception('Return request create failed')
            return self._render_form(error=str(e), prefill=post)

        # Attachments — multipart files['images'].
        files = request.httprequest.files.getlist('images')
        try:
            attachments = attach_files_to_record(
                rr, files,
                allowed_mime=DEFAULT_DOC_MIME, max_size_mb=5, max_count=10,
            )
            if attachments:
                rr.sudo().write(
                    {'image_attachment_ids': [(4, a.id) for a in attachments]})
        except ValidationError as e:
            rr.sudo().unlink()
            return self._render_form(error=str(e), prefill=post)

        if action == 'send':
            if len(rr.image_attachment_ids) < MIN_IMAGES_BEFORE_SEND:
                return self._render_form(
                    error=f'Cần ít nhất {MIN_IMAGES_BEFORE_SEND} ảnh trước khi gửi.',
                    prefill=post,
                )
            rr.sudo().write({'state': 'submitted'})
        return request.redirect(f'/portal/return/{rr.id}?message=created')

    @http.route(['/portal/return/<int:request_id>'], type='http',
                auth='user', sitemap=False)
    def portal_return_detail(self, request_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/return')
        rr = request.env['wujia.return.request'].sudo().search([
            ('id', '=', request_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not rr:
            return request.redirect('/portal/return')
        return request.render('wujia_portal_return.portal_return_detail', {
            'rr': rr, 'state_labels': STATE_LABELS,
            'resolution_labels': RESOLUTION_LABELS,
            'comp': self._build_compensation_ctx(rr),
            'message': kw.get('message'),
        })

    @http.route(['/portal/return/<int:request_id>/attachment/<int:att_id>'],
                type='http', auth='user', sitemap=False)
    def portal_return_attachment_download(self, request_id, att_id, **kw):
        """Stream attachment — ACL: chỉ user truy cập franchise của RR."""
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            raise Forbidden()
        rr = request.env['wujia.return.request'].sudo().search([
            ('id', '=', request_id),
            ('franchise_id', 'in', list(franchise_ids)),
        ], limit=1)
        if not rr:
            raise NotFound()
        allowed = set(rr.image_attachment_ids.ids) | set(rr.video_attachment_ids.ids)
        if att_id not in allowed:
            raise Forbidden()
        att = request.env['ir.attachment'].sudo().browse(att_id).exists()
        if not att:
            raise NotFound()
        return request.env['ir.binary']._get_stream_from(att).get_response(
            as_attachment=False,
        )

    # ============================================================== helpers
    def _build_compensation_ctx(self, rr):
        """Context hiển thị tiến độ bù cho cửa hàng (read-only).

        Trả None khi HQ chưa chốt phương án → template ẩn card, không lộ số 0.
        Chỉ đọc field compute đã có trên record → không đổi schema.
        """
        if not rr.resolution_type:
            return None
        ctx = {
            'resolution_label': RESOLUTION_LABELS.get(
                rr.resolution_type, rr.resolution_type),
            'is_compensation': rr.resolution_type == 'compensation',
        }
        if not ctx['is_compensation']:
            return ctx
        approved = rr.approved_qty or 0.0
        compensated = rr.compensated_qty or 0.0
        remaining = rr.remaining_qty or 0.0
        ctx.update({
            'approved_qty': approved,
            'approved_uom': rr.approved_uom_id.name or '',
            'product_label': rr.compensation_product_id.display_name or '—',
            'compensated_qty': compensated,
            'remaining_qty': remaining,
            'progress_pct': min(100, round(compensated / approved * 100))
                            if approved > 0 else 0,
            'status': COMPENSATION_STATUS_LABELS.get(
                rr.compensation_status,
                (rr.compensation_status or '—', 'wujia-badge-muted')),
            'approval_note': rr.approval_note or '',
            'orders': [
                {
                    'name': so.name,
                    'state_label': dict(so._fields['state']._description_selection(
                        request.env)).get(so.state, so.state),
                    'delivery_label': self._so_delivery_label(so),
                }
                for so in rr.compensation_so_ids
            ],
        })
        return ctx

    def _so_delivery_label(self, so):
        """Nhãn tiến độ giao của 1 đơn bù (đếm phiếu giao done/tổng)."""
        if 'picking_ids' not in so._fields:
            return ''
        pickings = so.picking_ids
        total = len(pickings)
        if not total:
            return 'Chưa tạo phiếu giao'
        done = len(pickings.filtered(lambda p: p.state == 'done'))
        if done == 0:
            return 'Chưa giao'
        if done >= total:
            return 'Đã giao đủ'
        return 'Đã giao %d/%d phiếu' % (done, total)

    def _render_form(self, error=None, prefill=None):
        franchise_ids = get_active_franchise_ids_filter()
        franchises = request.env['wujia.franchise.management'].sudo().browse(
            franchise_ids)
        orders = request.env['sale.order'].sudo().search([
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', 'in', ['sale', 'done']),
        ], order='date_order desc', limit=30)
        issue_types = request.env['wujia.return.issue.type'].sudo().search(
            [('active', '=', True)])
        # Map order_id -> [{id, label}] cho cascade select sản phẩm.
        order_lines = {
            o.id: [{
                'id': line.id,
                'label': '%s (%s %s)' % (
                    line.product_id.display_name,
                    ('{:,.0f}'.format(line.product_uom_qty or 0)),
                    line.product_uom_id.name or ''),
            } for line in o.order_line if line.product_id]
            for o in orders
        }
        return request.render('wujia_portal_return.portal_return_form', {
            'franchises': franchises, 'orders': orders,
            'order_lines_json': json.dumps(order_lines),
            'issue_types': issue_types, 'state_labels': STATE_LABELS,
            'error': error, 'values': prefill or {},
            'today': datetime.now(),
        })

    def _parse_payload(self, post, accessible_fids):
        try:
            franchise_id = int(post.get('franchise_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError("Cửa hàng không hợp lệ.")
        if franchise_id not in set(accessible_fids):
            raise ValidationError("Cửa hàng không truy cập được.")

        # Đơn gốc + dòng sản phẩm (bắt buộc — SP phải thuộc đơn).
        try:
            sale_order_id = int(post.get('sale_order_id') or 0)
            sale_order_line_id = int(post.get('sale_order_line_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError("Đơn hàng / sản phẩm không hợp lệ.")
        if not sale_order_id or not sale_order_line_id:
            raise ValidationError("Vui lòng chọn đơn hàng gốc và sản phẩm.")
        line = request.env['sale.order.line'].sudo().browse(sale_order_line_id).exists()
        if (not line or line.order_id.id != sale_order_id
                or line.order_id.franchise_id.id != franchise_id):
            raise ValidationError("Sản phẩm phải thuộc đơn hàng gốc của cửa hàng.")

        issue_type_id = post.get('issue_type_id')
        try:
            issue_type_id = int(issue_type_id) if issue_type_id else 0
        except (TypeError, ValueError):
            issue_type_id = 0
        if not issue_type_id:
            raise ValidationError("Vui lòng chọn loại lỗi.")

        try:
            request_qty = float(post.get('request_qty') or 0)
        except (TypeError, ValueError):
            request_qty = 0.0
        if request_qty <= 0:
            raise ValidationError("Số lượng yêu cầu phải lớn hơn 0.")

        opening = post.get('opening_datetime') or ''
        opening_dt = False
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                opening_dt = datetime.strptime(opening, fmt)
                break
            except ValueError:
                continue
        if not opening_dt:
            raise ValidationError("Vui lòng nhập thời gian mở hàng hợp lệ.")

        production_date = post.get('production_date') or False

        action = (post.get('action') or 'draft').strip()
        if action not in ('draft', 'send'):
            action = 'draft'

        vals = {
            'franchise_id': franchise_id,
            'sale_order_id': sale_order_id,
            'sale_order_line_id': sale_order_line_id,
            'request_uom_id': line.product_uom_id.id,
            'request_qty': request_qty,
            'opening_datetime': opening_dt,
            'production_date': production_date,
            'issue_type_id': issue_type_id,
            'note': (post.get('note') or '').strip()[:5000],
            'state': 'draft',
        }
        return vals, action
