from odoo import http
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
