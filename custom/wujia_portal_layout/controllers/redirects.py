# -*- coding: utf-8 -*-
"""Sprint 9.21 — 301 redirects from legacy v14 slugs to v19 kebab-case routes.

The v14 portal used underscore / verbose slugs. ~1500 franchise users may still
have old bookmarks or HQ emails pointing at them. Permanent (301) redirects keep
those links working and let search engines update. Each legacy slug below was
confirmed to exist in the v14 source (wujia_tea_odoo14) — we do NOT invent
redirects for slugs that never shipped.
"""
from odoo import http
from odoo.http import request


class WujiaLegacyRedirects(http.Controller):

    @http.route('/portal/purchase_history', type='http', auth='public', sitemap=False)
    def legacy_purchase_history(self, **kw):
        return request.redirect('/portal/purchase-history', code=301)

    @http.route('/portal/return-request-list', type='http', auth='public', sitemap=False)
    def legacy_return_list(self, **kw):
        return request.redirect('/portal/return', code=301)

    @http.route('/portal/exam-registration', type='http', auth='public', sitemap=False)
    def legacy_exam_registration(self, **kw):
        return request.redirect('/portal/exam', code=301)
