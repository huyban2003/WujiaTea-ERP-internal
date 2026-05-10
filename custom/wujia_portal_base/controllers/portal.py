from datetime import timedelta

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


ROLE_LABELS = {
    'owner': 'Chủ tiệm',
    'manager': 'Quản lý',
    'staff': 'Nhân viên',
}


class WujiaPortal(CustomerPortal):

    # ------------------------------------------------------------------
    # Counter for portal homepage card
    # ------------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'franchise_count' in counters:
            values['franchise_count'] = len(
                request.env.user._get_active_franchise_memberships()
            )
        return values

    # ------------------------------------------------------------------
    # /portal — Dashboard (4 stat card + 4 list block, BA spec)
    # ------------------------------------------------------------------
    @http.route(['/portal'], type='http', auth='user', website=False, sitemap=False)
    def portal_home(self, **kw):
        franchise_ids = request.env.user._get_accessible_franchise_ids()
        values = self._dashboard_values(franchise_ids)
        values.update({
            'title': _('Trang chủ - Portal'),
            'lang': request.env.lang or 'en',
            'role_labels': ROLE_LABELS,
        })
        return request.render('wujia_portal_base.portal_home_page', values)

    def _dashboard_values(self, franchise_ids):
        """Pre-compute mọi count + list cho dashboard. 1 batched query / metric.

        Module phụ (return/notification/...) có thể chưa cài → counter = 0,
        list = empty (try/except KeyError per ADR-016)."""
        SO = request.env['sale.order'].sudo()
        today = fields.Datetime.now()
        last_30d = today - timedelta(days=30)

        # ---- 4 stat cards ----
        unread_count = self._safe_count(
            'wujia.notification', 'unread_count', franchise_ids
        )
        recent_orders_count = SO.search_count([
            ('franchise_id', 'in', franchise_ids),
            ('date_order', '>=', last_30d),
            ('state', '!=', 'cancel'),
        ]) if franchise_ids else 0
        waiting_orders_count = SO.search_count([
            ('franchise_id', 'in', franchise_ids),
            ('state', 'in', ['draft', 'sent']),
        ]) if franchise_ids else 0
        return_requests_count = self._safe_count(
            'wujia.return.request', 'open_count', franchise_ids
        )

        # ---- 4 list blocks ----
        latest_notifications = self._safe_list(
            'wujia.notification', franchise_ids, limit=5,
        )
        recent_orders = SO.search([
            ('franchise_id', 'in', franchise_ids),
            ('state', '!=', 'cancel'),
        ], order='date_order desc', limit=5) if franchise_ids else SO.browse()
        latest_returns = self._safe_list(
            'wujia.return.request', franchise_ids, limit=5,
        )
        top_products = self._top_products(franchise_ids, limit=5)

        return {
            'unread_count': unread_count,
            'recent_orders_count': recent_orders_count,
            'waiting_orders_count': waiting_orders_count,
            'return_requests_count': return_requests_count,
            'latest_notifications': latest_notifications,
            'recent_orders': recent_orders,
            'latest_returns': latest_returns,
            'top_products': top_products,
            'franchise_ids': franchise_ids,
        }

    def _safe_count(self, model_name, kind, franchise_ids):
        """Đếm safe — nếu module chứa model chưa cài, return 0."""
        if not franchise_ids:
            return 0
        Model = request.env.get(model_name)
        if Model is None:
            return 0
        Model = Model.sudo()
        if kind == 'unread_count':
            user_id = request.env.user.id
            published_total = Model.search_count([
                ('published', '=', True),
                '|', ('franchise_ids', '=', False),
                     ('franchise_ids', 'in', list(franchise_ids)),
            ])
            Read = request.env.get('wujia.notification.read')
            if Read is None:
                return published_total
            read_count = Read.sudo().search_count([
                ('user_id', '=', user_id),
                ('notification_id.published', '=', True),
            ])
            return max(0, published_total - read_count)
        if kind == 'open_count':
            return Model.search_count([
                ('franchise_id', 'in', list(franchise_ids)),
                ('state', 'in', ['draft', 'sent', 'approved']),
            ])
        return 0

    def _safe_list(self, model_name, franchise_ids, limit=5):
        if not franchise_ids:
            return []
        Model = request.env.get(model_name)
        if Model is None:
            return []
        Model = Model.sudo()
        if model_name == 'wujia.notification':
            return Model.search([
                ('published', '=', True),
                '|', ('franchise_ids', '=', False),
                     ('franchise_ids', 'in', list(franchise_ids)),
            ], order='date desc', limit=limit)
        if model_name == 'wujia.return.request':
            return Model.search([
                ('franchise_id', 'in', list(franchise_ids)),
            ], order='request_date desc', limit=limit)
        return []

    def _top_products(self, franchise_ids, limit=5):
        """Top product cho dashboard (read_group thay vì N+1 search).

        Trả list dict {name, qty, uom, total} — đã pre-format sẵn cho template."""
        if not franchise_ids:
            return []
        SOL = request.env['sale.order.line'].sudo()
        groups = SOL._read_group(
            domain=[
                ('order_id.franchise_id', 'in', list(franchise_ids)),
                ('order_id.state', 'in', ['sale', 'done']),
            ],
            groupby=['product_id'],
            aggregates=['product_uom_qty:sum', 'price_total:sum'],
            limit=limit,
            order='product_uom_qty:sum desc',
        )
        return [{
            'name': product.display_name,
            'qty': qty or 0,
            'uom': product.uom_id.name or '',
            'total': total or 0,
        } for product, qty, total in groups]

    # ------------------------------------------------------------------
    # Franchise profile (đầy đủ thông tin nhượng quyền — BA spec mục 10)
    # ------------------------------------------------------------------
    @http.route(['/portal/franchises/<int:franchise_id>/profile'],
                type='http', auth='user', sitemap=False)
    def wujia_portal_franchise_profile(self, franchise_id, **kw):
        membership = self._get_membership_or_redirect(franchise_id)
        if isinstance(membership, http.Response):
            return membership
        membership_sudo = membership.sudo()
        return request.render(
            'wujia_portal_base.portal_franchise_profile_full', {
                'title': _('Hồ sơ cửa hàng'),
                'franchise': membership_sudo.franchise_id,
                'membership': membership_sudo,
                'role_labels': ROLE_LABELS,
            },
        )

    # ------------------------------------------------------------------
    # /my/franchises  + /portal/franchises (Vuexy layout mirror)
    # ------------------------------------------------------------------
    @http.route(['/my/franchises'], type='http', auth='user', website=True)
    def portal_my_franchises(self, **kw):
        memberships = request.env.user._get_active_franchise_memberships().sudo()
        return request.render('wujia_portal_base.portal_my_franchises', {
            'page_name': 'franchises',
            'memberships': memberships,
            'role_labels': ROLE_LABELS,
        })

    @http.route(['/portal/franchises'], type='http', auth='user', sitemap=False)
    def wujia_portal_franchises(self, **kw):
        memberships = request.env.user._get_active_franchise_memberships().sudo()
        return request.render('wujia_portal_base.portal_franchises_list', {
            'memberships': memberships,
            'role_labels': ROLE_LABELS,
        })

    @http.route(['/portal/franchises/<int:franchise_id>'],
                type='http', auth='user', sitemap=False)
    def wujia_portal_franchise_detail(self, franchise_id, **kw):
        membership = self._get_membership_or_redirect(franchise_id)
        if isinstance(membership, http.Response):
            return request.redirect('/portal/franchises')
        membership_sudo = membership.sudo()
        members = request.env['wujia.franchise.member'].sudo().search([
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ])
        return request.render('wujia_portal_base.portal_franchise_detail', {
            'franchise': membership_sudo.franchise_id,
            'membership': membership_sudo,
            'members': members,
            'role_labels': ROLE_LABELS,
        })

    @http.route(['/my/franchises/<int:franchise_id>'],
                type='http', auth='user', website=True)
    def portal_my_franchise_detail(self, franchise_id, **kw):
        membership = self._get_membership_or_redirect(franchise_id)
        if isinstance(membership, http.Response):
            return membership
        membership_sudo = membership.sudo()
        members = request.env['wujia.franchise.member'].sudo().search([
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ])
        return request.render('wujia_portal_base.portal_my_franchise_detail', {
            'page_name': 'franchise_detail',
            'franchise': membership_sudo.franchise_id,
            'membership': membership_sudo,
            'members': members,
            'role_labels': ROLE_LABELS,
        })

    @http.route(['/my/franchises/<int:franchise_id>/members'],
                type='jsonrpc', auth='user')
    def portal_franchise_members_json(self, franchise_id, **kw):
        membership = request.env['wujia.franchise.member'].sudo().search([
            ('user_id', '=', request.env.user.id),
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ], limit=1)
        if not membership:
            return {'error': 'forbidden'}
        members = request.env['wujia.franchise.member'].sudo().search([
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ])
        return {
            'members': [{
                'id': m.id,
                'user_name': m.user_id.name,
                'role': m.role,
                'role_label': ROLE_LABELS.get(m.role, m.role),
                'is_primary_owner': m.is_primary_owner,
                'date_from': m.date_from.isoformat() if m.date_from else None,
                'date_to': m.date_to.isoformat() if m.date_to else None,
            } for m in members],
        }

    # ------------------------------------------------------------------
    # Backwards-compat redirects: /my/branches → /my/franchises
    # ------------------------------------------------------------------
    @http.route(['/my/branches'], type='http', auth='user', sitemap=False)
    def _redirect_my_branches(self, **kw):
        return request.redirect('/my/franchises', code=301)

    @http.route(['/my/branches/<int:branch_id>'], type='http', auth='user', sitemap=False)
    def _redirect_my_branch_detail(self, branch_id, **kw):
        return request.redirect(f'/my/franchises/{branch_id}', code=301)

    @http.route(['/portal/branches'], type='http', auth='user', sitemap=False)
    def _redirect_portal_branches(self, **kw):
        return request.redirect('/portal/franchises', code=301)

    @http.route(['/portal/branches/<int:branch_id>'],
                type='http', auth='user', sitemap=False)
    def _redirect_portal_branch_detail(self, branch_id, **kw):
        return request.redirect(f'/portal/franchises/{branch_id}', code=301)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_membership_or_redirect(self, franchise_id):
        membership = request.env['wujia.franchise.member'].search([
            ('user_id', '=', request.env.user.id),
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ], limit=1)
        if not membership:
            return request.redirect('/my/franchises')
        return membership
