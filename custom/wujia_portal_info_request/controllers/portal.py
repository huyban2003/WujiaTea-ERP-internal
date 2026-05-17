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

from werkzeug.exceptions import Forbidden

from odoo import _, fields, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
    get_max_role_in_franchises,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    DEFAULT_DOC_MIME,
    attach_files_to_record,
)
from odoo.addons.wujia_portal_info_request.models.wujia_info_update_request import (
    REQUEST_TYPE, REQUEST_TYPE_FIELD_MAP, STATE,
)

_logger = logging.getLogger(__name__)

PAGE_SIZE = 20

STATE_LABELS = {
    'draft': ('Nháp', 'state-draft'),
    'submitted': ('Đã gửi', 'state-sent'),
    'reviewing': ('Đang xem', 'state-active'),
    'approved': ('Đã duyệt', 'state-approved'),
    'rejected': ('Từ chối', 'state-rejected'),
}


class WujiaPortalInfoRequest(http.Controller):

    @http.route(['/portal/info-request'], type='http', auth='user', sitemap=False)
    def portal_info_request_list(self, page=1, state='', request_type='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render(
                'wujia_portal_info_request.portal_info_request_list',
                {'requests': [], 'pager': {}, 'state_labels': STATE_LABELS,
                 'no_franchise': True, 'state': '', 'request_type': '',
                 'request_type_options': REQUEST_TYPE},
            )
        Model = request.env['wujia.info.update.request'].sudo()
        domain = [('franchise_id', 'in', list(franchise_ids))]
        if state and state in dict(STATE):
            domain.append(('state', '=', state))
        if request_type and request_type in dict(REQUEST_TYPE):
            domain.append(('request_type', '=', request_type))
        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Model.search_count(domain)
        recs = Model.search(domain, limit=PAGE_SIZE, offset=offset,
                            order='request_date desc')
        last_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        return request.render(
            'wujia_portal_info_request.portal_info_request_list',
            {
                'requests': recs,
                'pager': {
                    'page': {'num': page}, 'page_count': last_page,
                    'page_previous': {'num': max(1, page - 1)},
                    'page_next': {'num': min(last_page, page + 1)},
                },
                'state_labels': STATE_LABELS,
                'no_franchise': False,
                'state': state, 'request_type': request_type,
                'request_type_options': REQUEST_TYPE,
            },
        )

    @http.route(['/portal/info-request/new'], type='http', auth='user',
                methods=['GET', 'POST'], sitemap=False, csrf=True)
    def portal_info_request_new(self, **post):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/info-request')

        # Role gate (Owner/Manager only).
        role = get_max_role_in_franchises(list(franchise_ids))
        if role not in ('owner', 'manager'):
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

        try:
            rec = request.env['wujia.info.update.request'].sudo().create(vals)
        except Exception as e:
            _logger.exception('Info request create failed')
            return self._render_form(error=str(e), prefill=post)

        files = request.httprequest.files.getlist('attachments')
        try:
            attachments = attach_files_to_record(
                rec, files, allowed_mime=DEFAULT_DOC_MIME,
                max_size_mb=5, max_count=6,
            )
            if attachments:
                rec.sudo().write({'attachment_ids': [(4, a.id) for a in attachments]})
        except ValidationError as e:
            rec.sudo().unlink()
            return self._render_form(error=str(e), prefill=post)

        if action == 'submit':
            rec.action_submit()
        return request.redirect(
            f'/portal/info-request/{rec.id}?message=created'
        )

    @http.route(['/portal/info-request/<int:req_id>'], type='http',
                auth='user', sitemap=False)
    def portal_info_request_detail(self, req_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        rec = request.env['wujia.info.update.request'].sudo().search([
            ('id', '=', req_id),
            ('franchise_id', 'in', list(franchise_ids) if franchise_ids else [-1]),
        ], limit=1)
        if not rec:
            return request.redirect('/portal/info-request')
        return request.render(
            'wujia_portal_info_request.portal_info_request_detail',
            {'rec': rec, 'state_labels': STATE_LABELS,
             'message': kw.get('message')},
        )

    @http.route(['/portal/info-request/<int:req_id>/cancel'], type='http',
                auth='user', methods=['POST'], sitemap=False, csrf=True)
    def portal_info_request_cancel(self, req_id, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        rec = request.env['wujia.info.update.request'].sudo().search([
            ('id', '=', req_id),
            ('franchise_id', 'in', list(franchise_ids) if franchise_ids else [-1]),
            ('created_by_user_id', '=', request.env.uid),
        ], limit=1)
        if not rec:
            return request.redirect('/portal/info-request')
        try:
            rec.action_cancel()
        except ValidationError as e:
            return request.redirect(
                f'/portal/info-request/{rec.id}?message=' + str(e)
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
        field = REQUEST_TYPE_FIELD_MAP.get(request_type)
        if not field and request_type == 'other':
            field = (field_target or '').strip()
        if not field or field not in franchise._fields:
            return {'old_value': ''}
        return {'old_value': str(franchise[field] or '')}

    # ============================================================== helpers
    def _render_form(self, error=None, prefill=None):
        franchise_ids = get_active_franchise_ids_filter()
        franchises = request.env['wujia.franchise.management'].sudo().browse(franchise_ids)
        return request.render(
            'wujia_portal_info_request.portal_info_request_form',
            {
                'franchises': franchises,
                'request_type_options': REQUEST_TYPE,
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
