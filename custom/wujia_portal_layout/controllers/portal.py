"""Wujia portal — profile + change password controllers.

Routes:
- /portal/profile (GET) — render hồ sơ user.
- /portal/profile/update (POST) — update name/email/phone/street + avatar upload.
- /portal/profile/avatar/<int:user_id> (GET) — serve avatar (ETag + Cache-Control).
- /portal/change-password (GET/POST) — đổi mật khẩu (validate old qua _check_credentials).
"""
import base64
import logging
import re

from werkzeug.exceptions import Forbidden, NotFound

from odoo import _, http
from odoo.exceptions import AccessDenied, UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


_PHONE_RE = re.compile(r'^[+]?[0-9\s().\-]{7,20}$')
_AVATAR_MAX_BYTES = 2 * 1024 * 1024  # 2MB
_AVATAR_MIME = ('image/png', 'image/jpeg', 'image/jpg', 'image/webp')


class WujiaPortalLayout(http.Controller):
    """Layout-only routes. Route `/portal` (dashboard) đã chuyển sang
    wujia_portal_base để aggregate counter từ các module khác (xem ADR-016)."""

    # ------------------------------------------------------------------ profile
    @http.route('/portal/profile', type='http', auth='user', website=False,
                sitemap=False)
    def portal_profile(self, **kw):
        return request.render('wujia_portal_layout.profile_page', {
            'title': _('Hồ sơ'),
            'lang': request.env.lang or 'en',
            'profile': request.env.user.partner_id,
            'user': request.env.user,
            'message': kw.get('message'),
            'error': kw.get('error'),
        })

    @http.route('/portal/profile/update', type='http', auth='user',
                methods=['POST'], website=False, sitemap=False, csrf=True)
    def portal_profile_update(self, **post):
        """Validate + persist partner fields + optional avatar upload.

        PRG redirect on success (anti F5 double-submit).
        """
        user = request.env.user
        partner = user.partner_id
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()
        street = (post.get('street') or '').strip()

        # Validation
        if not name:
            return request.redirect('/portal/profile?error=' + _('Họ tên không được trống'))
        if phone and not _PHONE_RE.match(phone):
            return request.redirect('/portal/profile?error=' + _('Số điện thoại không hợp lệ'))

        # Build partner vals — KHÔNG cho đổi login email (chỉ partner contact email).
        vals = {'name': name, 'phone': phone, 'street': street}
        if email and email != partner.email:
            vals['email'] = email
            _logger.info('Portal user %s changed contact email %s → %s',
                         user.login, partner.email, email)

        try:
            partner.sudo().write(vals)
        except (UserError, ValidationError) as e:
            return request.redirect('/portal/profile?error=' + str(e))

        # Avatar upload — optional. Size + MIME validation backend.
        avatar = request.httprequest.files.get('avatar')
        if avatar and avatar.filename:
            data = avatar.read()
            if len(data) > _AVATAR_MAX_BYTES:
                return request.redirect('/portal/profile?error=' + _('Ảnh đại diện vượt quá 2MB'))
            if avatar.mimetype not in _AVATAR_MIME:
                return request.redirect('/portal/profile?error=' + _('Định dạng ảnh không hỗ trợ'))
            try:
                # image_1920 → Odoo auto-generate _128/_256/_512.
                user.sudo().write({'image_1920': base64.b64encode(data)})
            except Exception:
                _logger.exception('Avatar write failed for user %s', user.login)
                return request.redirect('/portal/profile?error=' + _('Lưu ảnh thất bại'))

        return request.redirect('/portal/profile?message=' + _('Cập nhật thành công'))

    @http.route('/portal/profile/avatar/<int:user_id>', type='http',
                auth='user', website=False, sitemap=False)
    def portal_profile_avatar(self, user_id, **kw):
        """Serve avatar ảnh với ACL theo accessible franchise.

        ETag + Cache-Control: private, max-age=300 → giảm DB load 1500 user.
        """
        User = request.env['res.users'].sudo()
        target = User.browse(int(user_id)).exists()
        if not target:
            raise NotFound()

        # ACL: self luôn OK, còn lại phải share franchise.
        if target.id != request.env.uid:
            accessible_fids = set(request.env.user._get_accessible_franchise_ids())
            target_fids = set(
                target.mapped('member_ids.franchise_id.id')
            ) if 'member_ids' in target._fields else set()
            if not (accessible_fids & target_fids):
                raise Forbidden()

        stream = request.env['ir.binary']._get_image_stream_from(
            target, 'avatar_256',
        )
        response = stream.get_response(as_attachment=False)
        response.headers['Cache-Control'] = 'private, max-age=300'
        return response

    # ----------------------------------------------------------- change password
    @http.route('/portal/change-password', type='http', auth='user',
                methods=['GET', 'POST'], website=False, sitemap=False,
                csrf=True)
    def portal_change_password(self, **post):
        values = {
            'title': _('Đổi mật khẩu'),
            'lang': request.env.lang or 'en',
        }
        if request.httprequest.method != 'POST':
            return request.render('wujia_portal_layout.change_password_page', values)

        old_pwd = post.get('old-password') or ''
        new_pwd = post.get('new-password') or ''
        confirm = post.get('con-password') or ''

        if not old_pwd or not new_pwd:
            values['error'] = _('Vui lòng nhập đầy đủ.')
        elif new_pwd != confirm:
            values['error'] = _('Mật khẩu mới và xác nhận không khớp.')
        elif len(new_pwd) < 8:
            values['error'] = _('Mật khẩu mới tối thiểu 8 ký tự.')
        elif new_pwd == old_pwd:
            values['error'] = _('Mật khẩu mới phải khác mật khẩu cũ.')
        else:
            try:
                # change_password(old, new) tự verify old qua _check_credentials.
                request.env['res.users'].change_password(old_pwd, new_pwd)
                values['message'] = _('Đổi mật khẩu thành công.')
            except AccessDenied:
                values['error'] = _('Mật khẩu cũ không đúng.')
            except UserError as e:
                values['error'] = str(e)
            except Exception:
                _logger.exception('Change password failed for %s',
                                  request.env.user.login)
                values['error'] = _('Có lỗi xảy ra. Vui lòng thử lại.')

        return request.render('wujia_portal_layout.change_password_page', values)
