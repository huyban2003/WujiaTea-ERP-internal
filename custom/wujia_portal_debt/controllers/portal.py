"""Portal Debt Overview — Sprint 16 (Figma Screen_3_Debt_Knowledge 2474:233).

Trang Công nợ /portal/debt. Card "Công nợ tóm tắt" = UI-ONLY (backend
account.move thuộc Phase 2 — user chốt 2026-06-12: làm UI trước, note lại,
BA fill controller/backend sau). 2 section còn lại (Kiến thức mới + Đơn hàng
gần đây) dùng data thật.
"""
from odoo import http
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_ids_filter,
)
from odoo.addons.wujia_portal_base.controllers.utils import (
    MOBILE_ORDER_BADGES,
    get_recent_orders,
)


class WujiaPortalDebt(http.Controller):

    @http.route(['/portal/debt'], type='http', auth='user', sitemap=False)
    def portal_debt_overview(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_debt.portal_debt_overview', {
                'no_franchise': True,
                'articles': [], 'm_recent_orders': [],
                'm_order_badges': MOBILE_ORDER_BADGES,
            })

        articles = request.env['wujia.knowledge.article'].sudo().search(
            [('is_published_portal', '=', True)],
            order='publish_date desc, id desc', limit=3,
        )
        return request.render('wujia_portal_debt.portal_debt_overview', {
            'no_franchise': False,
            # Công nợ: KHÔNG query gì — 3 số trên template là UI-only Phase 2.
            'articles': articles,
            'm_recent_orders': get_recent_orders(franchise_ids, limit=3),
            'm_order_badges': MOBILE_ORDER_BADGES,
        })
