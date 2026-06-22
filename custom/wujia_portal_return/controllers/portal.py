"""Wujia portal — Return Request controller.

Routes:
- GET  /portal/return                              list (filter state/date)
- GET, POST /portal/return/new                     create draft or send
- GET  /portal/return/<int>                        detail
- GET  /portal/return/<int>/attachment/<int>       download attachment
"""
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

STATE_LABELS = {
    'draft': ('Nháp', 'wujia-badge-muted'),
    'sent': ('Đã gửi', 'wujia-badge-info'),
    'approved': ('Đã duyệt', 'wujia-badge-success'),
    'rejected': ('Từ chối', 'wujia-badge-danger'),
    'done': ('Hoàn thành', 'wujia-badge-success'),
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
        # S20: tìm Mã YC / Mã đơn (ilike)
        q = (q or '').strip()
        if q:
            domain += ['|', ('name', 'ilike', q), ('order_id.name', 'ilike', q)]
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
            'state_labels': STATE_LABELS, 'state': state,
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

        # ---------- POST ----------
        try:
            vals, lines, action = self._parse_payload(post, franchise_ids)
        except ValidationError as e:
            return self._render_form(error=str(e), prefill=post)

        try:
            rr = request.env['wujia.return.request'].sudo().create({
                **vals,
                'line_ids': [(0, 0, l) for l in lines],
            })
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
                rr.sudo().write({'image_ids': [(4, a.id) for a in attachments]})
        except ValidationError as e:
            # Cleanup nửa-vời: delete record nếu attachment fail (atomic feel).
            rr.sudo().unlink()
            return self._render_form(error=str(e), prefill=post)

        if action == 'send':
            if len(rr.image_ids) < MIN_IMAGES_BEFORE_SEND:
                return self._render_form(
                    error=f'Cần ít nhất {MIN_IMAGES_BEFORE_SEND} ảnh trước khi gửi.',
                    prefill=post,
                )
            rr.sudo().write({'state': 'sent'})
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
        if att_id not in rr.image_ids.ids:
            raise Forbidden()
        att = request.env['ir.attachment'].sudo().browse(att_id).exists()
        if not att:
            raise NotFound()
        return request.env['ir.binary']._get_stream_from(att).get_response(
            as_attachment=False,
        )

    # ============================================================== helpers
    def _render_form(self, error=None, prefill=None):
        franchise_ids = get_active_franchise_ids_filter()
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        recent_orders = request.env['sale.order'].sudo().search([
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', 'in', ['sale', 'done']),
        ], order='date_order desc', limit=20)
        error_types = request.env['wujia.return.error.type'].sudo().search(
            [('active', '=', True)]
        )
        return request.render('wujia_portal_return.portal_return_form', {
            'franchises': franchises, 'recent_orders': recent_orders,
            'error_types': error_types, 'state_labels': STATE_LABELS,
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

        error_id = post.get('error_id')
        try:
            error_id = int(error_id) if error_id else 0
        except (TypeError, ValueError):
            error_id = 0
        if not error_id:
            raise ValidationError("Vui lòng chọn loại lỗi.")

        order_id = post.get('order_id')
        try:
            order_id = int(order_id) if order_id else False
        except (TypeError, ValueError):
            order_id = False

        expected = post.get('expected_delivery_date') or False

        vals = {
            'franchise_id': franchise_id,
            'error_id': error_id,
            'order_id': order_id,
            'expected_delivery_date': expected,
            'note': (post.get('note') or '').strip()[:5000],
            'state': 'draft',
        }

        # Lines — multipart with list[]
        form = request.httprequest.form
        names = form.getlist('line_product_name[]')
        qtys = form.getlist('line_qty[]')
        reasons = form.getlist('line_reason[]')
        lines = []
        for name, qty, reason in zip(names, qtys, reasons):
            name = (name or '').strip()
            if not name:
                continue
            try:
                q = float(qty or 0)
            except (TypeError, ValueError):
                q = 0.0
            if q <= 0:
                continue
            lines.append({
                'product_name': name,
                'qty': q,
                'reason': (reason or '').strip()[:500],
            })
        if not lines:
            raise ValidationError("Vui lòng thêm ít nhất 1 dòng sản phẩm với số lượng > 0.")

        action = (post.get('action') or 'draft').strip()
        if action not in ('draft', 'send'):
            action = 'draft'
        return vals, lines, action
