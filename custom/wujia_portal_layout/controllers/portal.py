from odoo import _, http
from odoo.http import request


class WujiaPortalLayout(http.Controller):
    """Layout-only routes. Route `/portal` (dashboard) đã chuyển sang
    wujia_portal_base để aggregate counter từ các module khác (xem ADR-016)."""

    @http.route('/portal/profile', type='http', auth='user', website=False, sitemap=False)
    def portal_profile(self, **kw):
        return request.render('wujia_portal_layout.profile_page', {
            'title': _('Hồ sơ'),
            'lang': request.env.lang or 'en',
            'user': request.env.user,
        })

    @http.route('/portal/change-password', type='http', auth='user', website=False, sitemap=False)
    def portal_change_password(self, **kw):
        return request.render('wujia_portal_layout.change_password_page', {
            'title': _('Đổi mật khẩu'),
            'lang': request.env.lang or 'en',
        })
