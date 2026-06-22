# -*- coding: utf-8 -*-
"""Sprint PC-1 — dev-only gallery of the wj-pc-* desktop component layer
(BA pc_source_ui_v1_4). Internal users only: it is a living reference used to
QA components against the BA SVGs and to copy markup when reworking desktop
screens in later sprints. Not linked in any portal menu; harmless static markup.
"""
from odoo import http
from odoo.http import request


class WujiaPcPreview(http.Controller):

    @http.route('/portal/_pc-preview', type='http', auth='user',
                website=False, sitemap=False)
    def pc_preview(self, **kw):
        # Restrict to internal staff — franchise portal users have no reason to see it.
        if not request.env.user.has_group('base.group_user'):
            return request.redirect('/portal')
        return request.render('wujia_portal_layout.pc_preview_page', {})
