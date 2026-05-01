from odoo import _, http
from odoo.http import request


class WujiaPortalLayout(http.Controller):

    @http.route('/portal', type='http', auth='user', website=False, sitemap=False)
    def portal_home(self, **kw):
        return request.render('wujia_portal_layout.dashboard_page', {
            'title': _('Trang chủ - Portal'),
            'lang': request.env.lang or 'en',
        })

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
