"""Wujia portal — sale (catalog + cart + product detail + submit).

Routes:
- GET  /portal/order                           catalog (existing)
- GET  /portal/order/product/<int>             product detail page
- GET  /portal/order/cart                      full cart view
- POST /portal/order/cart/add        (json)    atomic add line
- POST /portal/order/cart/update     (json)    set qty
- POST /portal/order/cart/remove     (json)    delete line
- GET  /portal/order/cart/count      (json)    badge count
- POST /portal/order/submit          (http)    confirm SO → PRG

Race-safety: cart add dùng SQL UPDATE atomic (... + RETURNING) cho qty merge.
Rate limit: cart/add 60/min/IP. ACL: franchise_id phải thuộc accessible
franchise list của user (validated server-side).
"""
import logging

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.wujia_portal_base.controllers.portal import (
    get_active_franchise_id,
    get_active_franchise_ids_filter,
)
from odoo.addons.wujia_portal_base.controllers.utils import rate_limit

_logger = logging.getLogger(__name__)


PAGE_SIZE = 24
MAX_QTY_PER_LINE = 9999


def _float_to_hhmm(value):
    """Convert 10.5 → '10:30'. Tolerates None/invalid → '—'."""
    try:
        v = float(value or 0.0) % 24.0
    except (TypeError, ValueError):
        return '—'
    h = int(v)
    m = int(round((v - h) * 60))
    if m == 60:
        h, m = (h + 1) % 24, 0
    return f'{h:02d}:{m:02d}'


class WujiaPortalSale(http.Controller):
    """Trang đặt hàng — catalog sản phẩm + cart side panel + endpoints CRUD."""

    # ------------------------------------------------------------------ catalog
    @http.route(['/portal/order'], type='http', auth='user', sitemap=False)
    def portal_order_catalog(self, page=1, category_id=None, keyword='', **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.render('wujia_portal_sale.portal_order_catalog', {
                'no_franchise': True, 'products': [], 'categories': [],
                'cart_lines': [], 'pager': {}, 'keyword': '', 'category_id': None,
            })

        Product = request.env['product.template'].sudo()
        domain = [('is_public_website', '=', True), ('active', '=', True)]
        if keyword:
            domain.append(('name', 'ilike', keyword))
        try:
            cat_id = int(category_id) if category_id else None
        except (TypeError, ValueError):
            cat_id = None
        if cat_id:
            domain.append(('categ_id', '=', cat_id))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Product.search_count(domain)
        products = Product.search(domain, limit=PAGE_SIZE, offset=offset, order='name asc')

        Category = request.env['product.category'].sudo()
        categories = Category.search([], order='complete_name')

        pager = (
            request.website.pager(
                url='/portal/order', total=total, page=page, step=PAGE_SIZE,
                url_args={'keyword': keyword, 'category_id': cat_id or ''},
            )
            if hasattr(request, 'website') and request.website
            else self._fallback_pager(total, page)
        )

        Settings = request.env['res.config.settings'].sudo()
        # Lấy area của active franchise để áp đúng khung giờ theo khu vực.
        active_fid = get_active_franchise_id()
        area_id = False
        if active_fid:
            franchise = request.env['wujia.franchise.management'].sudo().browse(active_fid).exists()
            if franchise and franchise.area_id:
                area_id = franchise.area_id.id
        allowed, window = Settings._is_within_order_window(area_id=area_id)
        return request.render('wujia_portal_sale.portal_order_catalog', {
            'no_franchise': False,
            'products': products,
            'categories': categories,
            'cart_lines': self._get_draft_cart_lines(franchise_ids),
            'pager': pager,
            'keyword': keyword,
            'category_id': cat_id,
            'order_time_from': _float_to_hhmm(window['from']),
            'order_time_to': _float_to_hhmm(window['to']),
            'order_window_enabled': window['enabled'],
            'order_window_open': allowed,
        })

    # ----------------------------------------------------------- product detail
    @http.route(['/portal/order/product/<int:product_id>'],
                type='http', auth='user', sitemap=False)
    def portal_order_product_detail(self, product_id, **kw):
        product = request.env['product.template'].sudo().browse(int(product_id)).exists()
        if not product or not product.is_public_website or not product.active:
            return request.redirect('/portal/order')
        # Related products: cùng category, top 6
        related = request.env['product.template'].sudo().search([
            ('is_public_website', '=', True), ('active', '=', True),
            ('categ_id', '=', product.categ_id.id),
            ('id', '!=', product.id),
        ], limit=6, order='name asc')
        return request.render('wujia_portal_sale.portal_order_product_detail', {
            'product': product,
            'related': related,
        })

    # ----------------------------------------------------------------- cart view
    @http.route(['/portal/order/cart'], type='http', auth='user', sitemap=False)
    def portal_order_cart_view(self, **kw):
        franchise_ids = get_active_franchise_ids_filter()
        if not franchise_ids:
            return request.redirect('/portal/order')
        cart = self._get_active_cart()
        # Khung giờ đặt hàng theo area của active franchise (warnbar mobile v2).
        active_fid = get_active_franchise_id()
        area_id = False
        if active_fid:
            franchise = request.env['wujia.franchise.management'].sudo().browse(active_fid).exists()
            if franchise and franchise.area_id:
                area_id = franchise.area_id.id
        _allowed, window = request.env['res.config.settings'].sudo()._is_within_order_window(area_id=area_id)
        return request.render('wujia_portal_sale.portal_order_cart', {
            'cart': cart,
            'cart_lines': cart.order_line if cart else [],
            'message': kw.get('message'),
            'error': kw.get('error'),
            'order_time_from': _float_to_hhmm(window['from']),
            'order_time_to': _float_to_hhmm(window['to']),
            'order_window_enabled': window['enabled'],
        })

    # ----------------------------------------------------------------- cart add
    @http.route(['/portal/order/cart/add'], type='json', auth='user',
                methods=['POST'])
    @rate_limit(max_calls=60, window_sec=60)
    def portal_cart_add(self, product_id, qty=1, **kw):
        fid = get_active_franchise_id()
        if not fid:
            return {'error': 'no_active_franchise'}
        try:
            product_id = int(product_id)
            qty = max(1, min(int(qty), MAX_QTY_PER_LINE))
        except (TypeError, ValueError):
            return {'error': 'invalid_input'}
        product = request.env['product.template'].sudo().browse(product_id).exists()
        if not product or not product.is_public_website or not product.active:
            return {'error': 'product_unavailable'}

        cart = self._get_or_create_cart(fid)
        variant = product.product_variant_id
        line = cart.order_line.filtered(lambda l: l.product_id == variant)
        if line:
            line = line[0]
            # Atomic UPDATE — race-safe khi 2 tab cùng add cùng product.
            request.env.cr.execute(
                "UPDATE sale_order_line SET product_uom_qty = product_uom_qty + %s "
                "WHERE id = %s RETURNING product_uom_qty",
                (qty, line.id),
            )
            new_qty = request.env.cr.fetchone()[0]
            line.invalidate_recordset(['product_uom_qty'])
        else:
            line = request.env['sale.order.line'].sudo().create({
                'order_id': cart.id,
                'product_id': variant.id,
                'product_uom_qty': qty,
            })
            new_qty = qty

        return {
            'success': True,
            'line_id': line.id,
            'qty': new_qty,
            'cart_count': len(cart.order_line),
        }

    # -------------------------------------------------------------- cart update
    @http.route(['/portal/order/cart/update'], type='json', auth='user',
                methods=['POST'])
    def portal_cart_update_qty(self, line_id, qty, **kw):
        try:
            line_id = int(line_id)
            qty = max(0, min(int(qty), MAX_QTY_PER_LINE))
        except (TypeError, ValueError):
            return {'error': 'invalid_input'}
        line = self._get_owned_line(line_id)
        if not line:
            return {'error': 'line_not_found'}
        if qty == 0:
            line.unlink()
            return {'success': True, 'removed': True,
                    'cart_count': len(line.order_id.order_line)}
        line.sudo().write({'product_uom_qty': qty})
        return {'success': True, 'qty': qty,
                'cart_count': len(line.order_id.order_line)}

    # -------------------------------------------------------------- cart remove
    @http.route(['/portal/order/cart/remove'], type='json', auth='user',
                methods=['POST'])
    def portal_cart_remove(self, line_id, **kw):
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            return {'error': 'invalid_input'}
        line = self._get_owned_line(line_id)
        if not line:
            return {'error': 'line_not_found'}
        order = line.order_id
        line.unlink()
        return {'success': True, 'cart_count': len(order.order_line)}

    # --------------------------------------------------------------- cart count
    @http.route(['/portal/order/cart/count'], type='json', auth='user',
                methods=['GET', 'POST'])
    def portal_cart_count(self, **kw):
        cart = self._get_active_cart()
        return {'count': len(cart.order_line) if cart else 0}

    # ------------------------------------------------------------ submit order
    @http.route(['/portal/order/submit'], type='http', auth='user',
                methods=['POST'], sitemap=False, csrf=True)
    def portal_order_submit(self, **post):
        fid = get_active_franchise_id()
        if not fid:
            return request.redirect('/portal/order/cart?error=no_active_franchise')
        cart = self._get_active_cart()
        if not cart or not cart.order_line:
            return request.redirect('/portal/order/cart?error=cart_empty')
        franchise = cart.franchise_id
        if hasattr(franchise, 'portal_locked') and franchise.portal_locked:
            return request.redirect('/portal/order/cart?error=branch_locked')
        area_id = franchise.area_id.id if franchise and franchise.area_id else False
        allowed, _w = request.env['res.config.settings'].sudo()._is_within_order_window(area_id=area_id)
        if not allowed:
            return request.redirect('/portal/order/cart?error=outside_order_window')
        # Optional portal note / delivery info
        vals = {}
        if post.get('portal_note'):
            vals['portal_note'] = (post.get('portal_note') or '').strip()[:1000]
        if post.get('portal_delivery_phone'):
            vals['portal_delivery_phone'] = post['portal_delivery_phone'].strip()[:50]
        if post.get('portal_delivery_street'):
            vals['portal_delivery_street'] = post['portal_delivery_street'].strip()[:200]
        if vals:
            cart.sudo().write(vals)
        try:
            cart.sudo().action_confirm()
        except (UserError, ValidationError) as e:
            _logger.warning('Portal order submit failed (cart %s): %s', cart.id, e)
            return request.redirect('/portal/order/cart?error=' + str(e)[:200])
        except Exception:
            _logger.exception('Portal order submit unexpected error cart=%s', cart.id)
            return request.redirect('/portal/order/cart?error=internal_error')
        return request.redirect(
            f'/portal/purchase-history/{cart.id}?message=order_submitted'
        )

    # ============================================================== helpers
    def _get_draft_cart_lines(self, franchise_ids):
        if not franchise_ids:
            return request.env['sale.order.line'].browse()
        SO = request.env['sale.order'].sudo()
        draft = SO.search([
            ('franchise_id', 'in', list(franchise_ids)),
            ('state', '=', 'draft'),
            ('is_portal_order', '=', True),
            ('portal_requester_user_id', '=', request.env.uid),
        ], order='create_date desc', limit=1)
        return draft.order_line

    def _get_active_cart(self):
        """Trả về draft SO portal active của user trong franchise hiện hoạt."""
        fid = get_active_franchise_id()
        if not fid:
            return request.env['sale.order'].browse()
        SO = request.env['sale.order'].sudo()
        return SO.search([
            ('franchise_id', '=', fid),
            ('state', '=', 'draft'),
            ('is_portal_order', '=', True),
            ('portal_requester_user_id', '=', request.env.uid),
        ], order='create_date desc', limit=1)

    def _get_or_create_cart(self, franchise_id):
        """Find-or-create draft SO portal cho franchise + user hiện tại.

        - franchise_id phải thuộc accessible list (gate).
        - Set partner = franchise partner để pass constraint
          _check_portal_franchise_required.
        """
        accessible = set(request.env.user._get_accessible_franchise_ids())
        if franchise_id not in accessible:
            raise UserError("Cửa hàng không truy cập được.")
        SO = request.env['sale.order'].sudo()
        cart = SO.search([
            ('franchise_id', '=', franchise_id),
            ('state', '=', 'draft'),
            ('is_portal_order', '=', True),
            ('portal_requester_user_id', '=', request.env.uid),
        ], order='create_date desc', limit=1)
        if cart:
            return cart
        franchise = request.env['wujia.franchise.management'].sudo().browse(franchise_id)
        partner = franchise.partner_id or request.env.user.partner_id
        # Snapshot membership tại thời điểm tạo (audit trail).
        Member = request.env['wujia.franchise.member'].sudo()
        membership = Member.find_active_membership(
            request.env.uid, franchise_id,
        ) if hasattr(Member, 'find_active_membership') else Member.browse()
        return SO.create({
            'is_portal_order': True,
            'franchise_id': franchise_id,
            'franchise_partner_id': partner.id,
            'partner_id': partner.id,
            'portal_requester_user_id': request.env.uid,
            'portal_member_id': membership.id if membership else False,
            'origin': 'Wujia Portal',
        })

    def _get_owned_line(self, line_id):
        """Browse line, verify thuộc cart của user hiện tại."""
        Line = request.env['sale.order.line'].sudo()
        line = Line.browse(line_id).exists()
        if not line:
            return None
        order = line.order_id
        if (order.state != 'draft' or not order.is_portal_order
                or order.portal_requester_user_id.id != request.env.uid):
            return None
        return line

    def _fallback_pager(self, total, page):
        last = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        return {
            'page': {'num': page, 'url': f'/portal/order?page={page}'},
            'page_count': last, 'page_total': total,
            'page_first': {'num': 1, 'url': '/portal/order?page=1'},
            'page_last': {'num': last, 'url': f'/portal/order?page={last}'},
            'page_previous': {'num': max(1, page - 1),
                              'url': f'/portal/order?page={max(1, page - 1)}'},
            'page_next': {'num': min(last, page + 1),
                          'url': f'/portal/order?page={min(last, page + 1)}'},
        }
