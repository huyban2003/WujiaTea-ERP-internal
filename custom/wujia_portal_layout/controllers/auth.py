import odoo
from odoo import _, http
from odoo.http import request
from odoo.addons.web.controllers.home import Home, ensure_db


class WujiaAuthController(Home):

    @http.route('/portal/login', type='http', auth='public', sitemap=False)
    def portal_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False

        if request.httprequest.method == 'GET' and request.session.uid:
            return request.redirect(redirect or '/portal/redirect')

        values = {k: v for k, v in request.params.items() if k != 'password'}

        if request.httprequest.method == 'POST':
            try:
                credential = {
                    'login': request.params.get('login') or '',
                    'password': request.params.get('password') or '',
                    'type': 'password',
                }
                request.session.authenticate(request.env, credential)
                request.params['login_success'] = True
                if redirect:
                    return request.redirect(redirect)
                if request.env.user.has_group('base.group_user'):
                    return request.redirect('/odoo')
                return request.redirect('/portal')
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        return request.render('wujia_portal_layout.login', values)

    @http.route('/portal/logout', type='http', auth='public', sitemap=False)
    def portal_logout(self, redirect='/portal/login'):
        request.session.logout(keep_db=True)
        return request.redirect(redirect)

    @http.route('/portal/redirect', type='http', auth='user', sitemap=False)
    def portal_post_login_redirect(self, **kw):
        if request.env.user.has_group('base.group_user'):
            return request.redirect('/odoo')
        return request.redirect('/portal')
