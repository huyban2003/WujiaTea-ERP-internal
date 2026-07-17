from datetime import timedelta

from odoo import _, fields, http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.wujia_portal_base.controllers.utils import (
    MOBILE_ORDER_BADGES,
    MOBILE_RETURN_BADGES,
    get_upcoming_batches,
)


ROLE_LABELS = {
    'owner': 'Chủ tiệm',
    'manager': 'Quản lý',
    'staff': 'Nhân viên',
}
ROLE_RANK = {'staff': 1, 'manager': 2, 'owner': 3}

ACTIVE_FRANCHISE_COOKIE = 'wujia_active_franchise_id'
ACTIVE_FRANCHISE_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 ngày


# ----------------------------------------------------------------------
# Module-level helpers — các controller portal_* khác import dùng chung.
# Cache vào `request._wujia_active_fid_cache` để 1 request chỉ tính 1 lần.
# ----------------------------------------------------------------------

def _read_active_franchise_cookie():
    raw = request.httprequest.cookies.get(ACTIVE_FRANCHISE_COOKIE)
    try:
        return int(raw) if raw else False
    except (TypeError, ValueError):
        return False


def get_active_franchise_id():
    """Trả franchise_id user đang chọn (đã validate). False nếu chưa hợp lệ.

    Cache trong request lifetime — tránh tính nhiều lần / request."""
    cached = getattr(request, '_wujia_active_fid_cache', None)
    if cached is not None:
        return cached if cached >= 0 else False

    accessible = request.env.user._get_accessible_franchise_ids()  # ormcached
    cookie_id = _read_active_franchise_cookie()
    if cookie_id and cookie_id in accessible:
        result = cookie_id
    elif len(accessible) == 1:
        # Single-franchise: auto-pick — không cần modal.
        result = accessible[0]
    else:
        result = False

    request._wujia_active_fid_cache = result if result else -1
    return result


def get_active_franchise_ids_filter():
    """Tuple cho domain `('franchise_id', 'in', ...)`.

    Đã chọn → tuple 1 phần tử. Chưa chọn (multi-franchise) → all accessible
    (fallback an toàn — vẫn thấy data, chỉ là rộng hơn)."""
    active = get_active_franchise_id()
    if active:
        return (active,)
    return request.env.user._get_accessible_franchise_ids()


def get_max_role_in_franchises(franchise_ids=None):
    """Role cao nhất user có (Owner > Manager > Staff). False nếu không thuộc."""
    memberships = request.env.user._get_active_franchise_memberships()
    if franchise_ids:
        target = set(franchise_ids)
        memberships = memberships.filtered(lambda m: m.franchise_id.id in target)
    if not memberships:
        return False
    max_rank = max(ROLE_RANK.get(m.role, 0) for m in memberships)
    for role, rank in ROLE_RANK.items():
        if rank == max_rank:
            return role
    return False


def _float_to_hhmm(value):
    """Convert float giờ 10.5 → '10:30'. Tolerates None/invalid → '—'.

    Bản local trong wujia_portal_base — KHÔNG import từ wujia_portal_sale
    (base không phụ thuộc sale, tránh reverse dependency)."""
    try:
        v = float(value or 0.0) % 24.0
    except (TypeError, ValueError):
        return '—'
    h = int(v)
    m = int(round((v - h) * 60))
    if m == 60:
        h, m = (h + 1) % 24, 0
    return f'{h:02d}:{m:02d}'


class WujiaPortal(CustomerPortal):

    # ==================================================================
    # /portal — Dashboard (4 stat card + 4 list block, BA spec)
    # ==================================================================
    @http.route(['/portal'], type='http', auth='user', website=False, sitemap=False)
    def portal_home(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        accessible_ids = request.env.user._get_accessible_franchise_ids()
        values = self._dashboard_values(franchise_ids)

        # ---- Mobile home hero (Figma BA Sprint 10): cửa hàng + role + khung giờ ----
        active_fid = get_active_franchise_id()
        Franchise = request.env['wujia.franchise.management'].sudo()
        active_franchise = Franchise.browse(active_fid).exists() if active_fid else Franchise.browse()
        membership = (
            request.env['wujia.franchise.member'].sudo()
                .find_active_membership(request.env.user.id, active_fid)
            if active_fid else False
        )
        active_role = membership.role if membership else False

        # ---- Sprint 17: 3 màn dashboard (Figma 2474:2) gộp về Home (dedupe).
        #      BA còn review. recent_orders/latest_returns/active_franchise đã có
        #      sẵn ở _dashboard_values — chỉ bổ sung batch + articles + hotline. ----
        franchise_ids_list = list(franchise_ids) if franchise_ids else []
        m_upcoming_batches = (
            get_upcoming_batches(franchise_ids_list, limit=2)
            if franchise_ids_list else []
        )
        # Knowledge — base KHÔNG depend wujia_portal_knowledge → guard registry
        # (cùng pattern _safe_count/_safe_list; KHÔNG thêm depends, tránh coupling).
        Article = request.env.get('wujia.knowledge.article')
        articles = []
        if Article is not None and 'is_published_portal' in Article._fields:
            articles = Article.sudo().search(
                [('is_published_portal', '=', True)],
                order='publish_date desc, id desc', limit=3,
            )

        values.update({
            # Sprint 17 dashboard-merge keys (mobile home d-lg-none)
            'm_upcoming_batches': m_upcoming_batches,
            'm_order_badges': MOBILE_ORDER_BADGES,
            'm_return_badges': MOBILE_RETURN_BADGES,
            'articles': articles,
            'm_hotline': request.env.company.sudo().phone or '',
            'title': _('Trang chủ - Portal'),
            'lang': request.env.lang or 'en',
            'role_labels': ROLE_LABELS,
            # Cho modal store-picker render điều kiện
            'must_pick_franchise': (
                len(accessible_ids) > 1 and not _read_active_franchise_cookie()
            ),
            'all_accessible_franchises': request.env['wujia.franchise.management']
                .sudo().browse(list(accessible_ids)) if accessible_ids
                else request.env['wujia.franchise.management'].browse(),
            'active_franchise_id': active_fid,
            # mobile home (d-lg-none) — desktop không dùng các key này
            'active_franchise': active_franchise,
            'active_role': active_role,
            'order_window': self._order_window_view(
                active_franchise.area_id.id if active_franchise else None
            ),
        })
        return request.render('wujia_portal_base.portal_home_page', values)

    def _order_window_view(self, area_id=None):
        """Trạng thái khung giờ đặt hàng cho hero mobile home.

        1 call `_is_within_order_window` (đọc config param / window set nhỏ) —
        scalar, KHÔNG ORM trong loop → OK cho 1500 user.

        Return dict `{state, from_hhmm, to_hhmm, remaining_hhmm, progress_pct}`:
          - state='always' : khung giờ tắt global → "Đặt hàng 24/7".
          - state='open'   : trong giờ → xanh "Đang mở" + còn HH:MM + progress.
          - state='closed' : ngoài giờ → đỏ "Đã đóng" + mở lại lúc from_hhmm.
        """
        Settings = request.env['res.config.settings'].sudo()
        allowed, window = Settings._is_within_order_window(area_id=area_id)
        if not window.get('enabled', True):
            return {'state': 'always'}

        f = float(window.get('from') or 0.0) % 24.0
        t = float(window.get('to') or 0.0) % 24.0
        now = Settings._user_now_hours()
        span = (t - f) % 24.0 or 24.0  # độ dài khung (xử lý qua nửa đêm)

        if allowed:
            elapsed = (now - f) % 24.0
            remaining = max(0.0, span - elapsed)
            progress = max(0, min(100, round(elapsed / span * 100))) if span else 0
            return {
                'state': 'open',
                'to_hhmm': _float_to_hhmm(t),
                'remaining_hhmm': _float_to_hhmm(remaining),
                'progress_pct': progress,
            }
        return {
            'state': 'closed',
            'from_hhmm': _float_to_hhmm(f),
            'to_hhmm': _float_to_hhmm(t),
        }

    def _dashboard_values(self, franchise_ids):
        """Pre-compute dashboard. 1 batched query / metric — KHÔNG ORM trong template loop."""
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

        # ---- 4 list blocks (BA: latest noti & latest returns limit 3) ----
        latest_notifications = self._safe_list(
            'wujia.notification', franchise_ids, limit=3,
        )
        recent_orders = SO.search([
            ('franchise_id', 'in', franchise_ids),
            ('state', '!=', 'cancel'),
        ], order='date_order desc', limit=5) if franchise_ids else SO.browse()
        latest_returns = self._safe_list(
            'wujia.return.request', franchise_ids, limit=3,
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
            # BA spec: state in ('submitted','processing','approved') — KHÔNG tính draft.
            return Model.search_count([
                ('franchise_id', 'in', list(franchise_ids)),
                ('state', 'in', ['submitted', 'processing', 'approved']),
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
            # BA spec: loại phiếu đã huỷ / từ chối khỏi danh sách gần đây.
            return Model.search([
                ('franchise_id', 'in', list(franchise_ids)),
                ('state', 'not in', ['rejected', 'cancelled']),
            ], order='request_date desc', limit=limit)
        return []

    def _top_products(self, franchise_ids, limit=5):
        """Top product 90 ngày (BA spec). 1 _read_group, không loop search."""
        if not franchise_ids:
            return []
        last_90d = fields.Datetime.now() - timedelta(days=90)
        SOL = request.env['sale.order.line'].sudo()
        groups = SOL._read_group(
            domain=[
                ('order_id.franchise_id', 'in', list(franchise_ids)),
                ('order_id.state', 'in', ['sale', 'done']),
                ('order_id.date_order', '>=', last_90d),
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

    # ==================================================================
    # Active-franchise (store picker) — cookie-based, no DB hit
    # Module-level helpers: get_active_franchise_id(),
    #     get_active_franchise_ids_filter(), get_max_role_in_franchises().
    # ==================================================================
    @http.route(['/portal/franchise/switch'], type='http', auth='user',
                methods=['POST'], website=False, csrf=True, sitemap=False)
    def portal_franchise_switch(self, franchise_id=None, redirect='/portal', **kw):
        """Set cookie active franchise. Validate user có quyền trước khi set."""
        accessible = request.env.user._get_accessible_franchise_ids()
        try:
            fid = int(franchise_id)
        except (TypeError, ValueError):
            return request.redirect('/portal')
        if fid not in accessible:
            return request.redirect('/portal')

        target = redirect if (redirect or '').startswith('/') else '/portal'
        response = request.redirect(target)
        response.set_cookie(
            ACTIVE_FRANCHISE_COOKIE,
            str(fid),
            max_age=ACTIVE_FRANCHISE_COOKIE_MAX_AGE,
            samesite='Lax',
            httponly=False,  # JS có thể đọc tên cửa hàng đang active
        )
        return response

    @http.route(['/portal/franchise/clear'], type='http', auth='user',
                methods=['POST'], website=False, csrf=True, sitemap=False)
    def portal_franchise_clear(self, **kw):
        response = request.redirect('/portal')
        response.delete_cookie(ACTIVE_FRANCHISE_COOKIE)
        return response

    # ==================================================================
    # Counter for /my homepage card (Odoo standard portal)
    # ==================================================================
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'franchise_count' in counters:
            values['franchise_count'] = len(
                request.env.user._get_active_franchise_memberships()
            )
        return values

    # ==================================================================
    # Franchise profile (đầy đủ thông tin nhượng quyền — BA spec mục 10)
    # ==================================================================
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

    # ==================================================================
    # /my/franchises  + /portal/franchises (Vuexy layout mirror)
    # ==================================================================
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

    # ==================================================================
    # Franchise Information menu (BA spec Section A — readonly snapshot
    # của cửa hàng + user tab + thông tin nhượng quyền cho cửa hàng đang
    # active. Không cho sửa — chức năng cập nhật đã có module
    # wujia_portal_info_request.)
    # ==================================================================
    @http.route(['/portal/franchise-information'], type='http', auth='user',
                website=False, sitemap=False)
    def portal_franchise_information(self, **kw):
        fid = get_active_franchise_id()
        if not fid:
            return request.redirect('/portal')
        membership = self._get_membership_or_redirect(fid)
        if isinstance(membership, http.Response):
            return membership
        membership_sudo = membership.sudo()
        franchise = membership_sudo.franchise_id
        # Hard gate per BA: portal_locked or status != 'active' → block
        if franchise.portal_locked or franchise.status != 'active':
            return request.render('wujia_portal_base.portal_franchise_information_locked', {
                'title': _('Thông tin cửa hàng'),
                'franchise': franchise,
            })
        members = request.env['wujia.franchise.member'].sudo().search([
            ('franchise_id', '=', fid),
            ('is_currently_valid', '=', True),
        ])
        return request.render('wujia_portal_base.portal_franchise_information', {
            'title': _('Thông tin cửa hàng'),
            'page_name': 'franchise_information',
            'franchise': franchise,
            'membership': membership_sudo,
            'members': members,
            'role_labels': ROLE_LABELS,
        })

    # ==================================================================
    # Backwards-compat redirects: /my/branches → /my/franchises
    # ==================================================================
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

    # ==================================================================
    # Helpers
    # ==================================================================
    def _get_membership_or_redirect(self, franchise_id):
        membership = request.env['wujia.franchise.member'].search([
            ('user_id', '=', request.env.user.id),
            ('franchise_id', '=', franchise_id),
            ('is_currently_valid', '=', True),
        ], limit=1)
        if not membership:
            return request.redirect('/my/franchises')
        return membership
