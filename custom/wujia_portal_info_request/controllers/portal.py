"""Wujia portal — Info Update Request controller.

Routes:
- GET  /portal/info-request                            list (filter)
- GET, POST /portal/info-request/new                   create
- GET  /portal/info-request/<int>                      detail
- POST /portal/info-request/<int>/cancel               cancel (form)
- GET  /portal/info-request/franchise/<int>/values     AJAX old_value lookup

Role gate: chỉ Owner/Manager mới được tạo (BA spec — gửi cập nhật thông tin
là quyết định cấp shop, không phải Staff).
"""
import logging
from urllib.parse import quote

from werkzeug.exceptions import Forbidden

from odoo import _, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import get_active_franchise_ids_filter
from odoo.addons.wujia_portal_base.controllers.utils import (
    DEFAULT_DOC_MIME,
    PAGE_SIZE_OPTIONS,
    attach_files_to_record,
    build_pager,
    parse_page_size,
    status_badge_for,
)
from odoo.addons.wujia_info_request.models.wujia_info_update_request import REQUEST_TYPE, STATE

_logger = logging.getLogger(__name__)

PAGE_SIZE = 20

# Nhãn VN của wujia.info.update.request.request_type. Pin cứng tại đây vì source đã chuyển
# sang tiếng Anh (sprint 44) — portal phải giữ tiếng Việt.
# Key phải khớp REQUEST_TYPE trong wujia_info_request (giữ đúng thứ tự).
REQUEST_TYPE_LABELS = {
    'address': 'Địa chỉ',
    'phone': 'Số điện thoại',
    'email': 'Email',
    'owner_name': 'Tên chủ cửa hàng',
    'bank_info': 'Thông tin ngân hàng',
    'representative': 'Người đại diện',
    'other': 'Khác',
}
REQUEST_TYPE_OPTIONS = [(code, REQUEST_TYPE_LABELS[code]) for code, _label in REQUEST_TYPE]

STATE_LABELS = {k: (v, status_badge_for(v)) for k, v in {
    'draft': 'Nháp',
    'submitted': 'Đã gửi',
    'reviewing': 'Đang xem',
    'approved': 'Đã duyệt',
    'rejected': 'Từ chối',
}.items()}


class WujiaPortalInfoRequest(http.Controller):

    @http.route(['/portal/info-request'], type='http', auth='user', sitemap=False)
    def portal_info_request_list(self, page=1, state='', request_type='',
                                 page_size=None, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render(
                'wujia_portal_info_request.portal_info_request_list',
                {'requests': [], 'pgn': None, 'state_labels': STATE_LABELS,
                 'no_franchise': True, 'state': '', 'request_type': '',
                 'request_type_options': REQUEST_TYPE_OPTIONS},
            )
        Model = request.env['wujia.info.update.request'].sudo()
        domain = Model._portal_scope_domain(franchise_ids)
        if state and state in dict(STATE):
            domain.append(('state', '=', state))
        if request_type and request_type in dict(REQUEST_TYPE):
            domain.append(('request_type', '=', request_type))
        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        size = parse_page_size(page_size, PAGE_SIZE)
        total = Model.search_count(domain)
        pgn = build_pager(total, page, size, path='/portal/info-request',
                          item_label='yêu cầu',
                          page_size_options=PAGE_SIZE_OPTIONS)
        recs = Model.search(domain, limit=size, offset=pgn['offset'],
                            order='request_date desc')
        return request.render(
            'wujia_portal_info_request.portal_info_request_list',
            {
                'requests': recs,
                'pgn': pgn,
                'state_labels': STATE_LABELS,
                'no_franchise': False,
                'state': state, 'request_type': request_type,
                'request_type_options': REQUEST_TYPE_OPTIONS,
            },
        )

    @http.route(['/portal/info-request/new'], type='http', auth='user',
                methods=['GET', 'POST'], sitemap=False, csrf=True)
    def portal_info_request_new(self, **post):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/info-request')

        Model = request.env['wujia.info.update.request'].sudo()
        if not Model._portal_can_request(franchise_ids):
            raise Forbidden(description=_(
                "Chỉ Owner / Manager mới được tạo yêu cầu cập nhật thông tin."
            ))

        if request.httprequest.method != 'POST':
            return self._render_form()

        # ---------- POST ----------
        try:
            vals, action = self._parse_payload(post, franchise_ids)
        except ValidationError as e:
            return self._render_form(error=str(e), prefill=post)

        files = request.httprequest.files.getlist('attachments')
        try:
            rec = Model.create_from_portal(
                vals, submit=action == 'submit',
                attach=lambda r: attach_files_to_record(
                    r, files, allowed_mime=DEFAULT_DOC_MIME, max_size_mb=5, max_count=6),
            )
        except (ValidationError, UserError) as e:
            return self._render_form(error=str(e), prefill=post)
        except Exception:
            _logger.exception('Info request create failed')
            return self._render_form(
                error=_("Không thể gửi yêu cầu. Vui lòng kiểm tra lại thông tin và thử lại."),
                prefill=post)
        return request.redirect(
            f'/portal/info-request/{rec.id}?message=created'
        )

    @http.route(['/portal/info-request/<int:req_id>'], type='http',
                auth='user', sitemap=False)
    def portal_info_request_detail(self, req_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Model = request.env['wujia.info.update.request'].sudo()
        rec = Model.search([('id', '=', req_id)] + Model._portal_scope_domain(franchise_ids), limit=1)
        if not rec:
            return request.redirect('/portal/info-request')
        return request.render(
            'wujia_portal_info_request.portal_info_request_detail',
            {'rec': rec, 'state_labels': STATE_LABELS,
             'request_type_labels': REQUEST_TYPE_LABELS,
             'message': kw.get('message')},
        )

    @http.route(['/portal/info-request/<int:req_id>/cancel'], type='http',
                auth='user', methods=['POST'], sitemap=False, csrf=True)
    def portal_info_request_cancel(self, req_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        Model = request.env['wujia.info.update.request'].sudo()
        rec = Model.search([('id', '=', req_id), ('created_by_user_id', '=', request.env.uid)]
                           + Model._portal_scope_domain(franchise_ids), limit=1)
        if not rec:
            return request.redirect('/portal/info-request')
        try:
            rec.action_cancel()
        except ValidationError as e:
            return request.redirect(
                f'/portal/info-request/{rec.id}?message=' + quote(str(e))
            )
        return request.redirect(
            f'/portal/info-request/{rec.id}?message=cancelled'
        )

    @http.route(['/portal/info-request/franchise/<int:fid>/values'],
                type='json', auth='user', methods=['POST', 'GET'])
    def portal_info_request_get_current(self, fid, request_type=None,
                                        field_target=None, **kw):
        """AJAX: trả giá trị hiện tại trên franchise theo request_type."""
        accessible = set(request.env.user._get_accessible_franchise_ids())
        if int(fid) not in accessible:
            return {'error': 'forbidden'}
        franchise = request.env['wujia.franchise.management'].sudo().browse(int(fid))
        if not franchise.exists():
            return {'error': 'not_found'}
        return {'old_value': request.env['wujia.info.update.request'].sudo()._franchise_value(
            franchise, request_type, field_target)}

    # ============================================================== helpers
    def _render_form(self, error=None, prefill=None):
        franchise_ids = get_active_franchise_ids_filter()
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        return request.render(
            'wujia_portal_info_request.portal_info_request_form',
            {
                'franchises': franchises,
                'request_type_options': REQUEST_TYPE_OPTIONS,
                'error': error,
                'values': prefill or {},
            },
        )

    def _parse_payload(self, post, accessible_fids):
        try:
            franchise_id = int(post.get('franchise_id') or 0)
        except (TypeError, ValueError):
            raise ValidationError(_("Cửa hàng không hợp lệ."))
        if franchise_id not in set(accessible_fids):
            raise ValidationError(_("Cửa hàng không truy cập được."))

        request_type = post.get('request_type') or ''
        if request_type not in dict(REQUEST_TYPE):
            raise ValidationError(_("Loại thông tin không hợp lệ."))

        new_value = (post.get('new_value') or '').strip()
        if not new_value:
            raise ValidationError(_("Vui lòng nhập giá trị mới."))

        field_target = (post.get('field_target') or '').strip()
        if request_type == 'other' and not field_target:
            raise ValidationError(_("Khi chọn 'Khác' phải nhập tên field."))

        action = (post.get('action') or 'draft').strip()
        if action not in ('draft', 'submit'):
            action = 'draft'

        priority = post.get('priority') or 'normal'
        if priority not in ('normal', 'urgent'):
            priority = 'normal'

        return {
            'franchise_id': franchise_id,
            'request_type': request_type,
            'field_target': field_target or False,
            'new_value': new_value[:5000],
            'note': (post.get('note') or '').strip()[:2000],
            'priority': priority,
        }, action
