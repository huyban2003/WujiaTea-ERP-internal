"""Wujia portal — sale (catalog + giỏ hàng chung theo cửa hàng + submit).

Sprint 30 — theo BA controller mapping FINAL ("Controller Product + Cart"):
- Giỏ = `wujia.portal.cart` DÙNG CHUNG theo store (1 store 1 giỏ, mọi user
  membership hợp lệ thao tác chung, last-write-wins, mutation trả full state).
- Sản phẩm = product.product `is_public_portal` + giá theo pricelist của partner
  cửa hàng (backend là nguồn giá duy nhất — không tin giá FE).
- Step đặt hàng = min_qty; max_qty=0 nghĩa là không giới hạn.
- Submit: SO luôn DRAFT + huỷ draft/sent portal cũ cùng store (nguyên khối) +
  khoá giỏ FOR UPDATE NOWAIT (savepoint — tránh Odoo retry nuốt LockNotAvailable).
- Khung giờ chỉ chặn tại submit; thao tác giỏ ngoài giờ vẫn cho (BA).

Routes:
- GET  /portal/order                        catalog (PC combined + mobile)
- GET  /portal/order/product/<int>          product detail (variant)
- GET  /portal/order/cart                   full cart view
- POST /portal/order/cart/add     (json)    atomic upsert +min_qty
- POST /portal/order/cart/update  (json)    set qty (min/step/max)
- POST /portal/order/cart/remove  (json)    delete line (idempotent)
- GET  /portal/order/cart/count   (json)    badge count
- POST /portal/order/cart/note    (json)    save shared note
- POST /portal/order/submit       (http)    draft SO + cancel old + clear cart
"""
import logging
from collections import defaultdict
from urllib.parse import urlencode

import psycopg2
from psycopg2 import errors as pg_errors

from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import plaintext2html

from odoo.addons.wujia_portal_base.controllers.portal import (
    ACTIVE_FRANCHISE_COOKIE,
    get_active_franchise_id,
)
from odoo.addons.wujia_portal_base.controllers.utils import rate_limit

_logger = logging.getLogger(__name__)


PAGE_SIZE = 24

# Bảng mã lỗi BA (chat "Controller Product + Cart" FINAL) + mã legacy còn lưu hành.
ERROR_MESSAGES = {
    'STORE_NOT_SELECTED': "Vui lòng chọn cửa hàng trước khi đặt hàng.",
    'STORE_ACCESS_DENIED': "Bạn không có quyền thao tác tại cửa hàng này.",
    'MEMBERSHIP_INACTIVE': "Tài khoản của bạn hiện không còn hiệu lực tại cửa hàng này.",
    'ORDER_TIME_NOT_CONFIGURED': "Chưa có cấu hình thời gian đặt hàng. Vui lòng liên hệ Ngô Gia.",
    'ORDER_TIME_CLOSED': "Hiện ngoài khung giờ đặt hàng. Vui lòng gửi đơn trong thời gian cho phép.",
    'PRODUCT_NOT_AVAILABLE': "Sản phẩm này hiện không còn được phép đặt hàng.",
    'MIN_QTY_NOT_CONFIGURED': "Sản phẩm chưa được cấu hình số lượng đặt tối thiểu. Vui lòng liên hệ Ngô Gia.",
    'QTY_BELOW_MIN': "Số lượng thấp hơn mức tối thiểu của sản phẩm.",
    'QTY_ABOVE_MAX': "Số lượng vượt mức tối đa của sản phẩm.",
    'QTY_INVALID_STEP': "Số lượng phải tăng theo bước bằng số lượng tối thiểu.",
    'CART_EMPTY': "Giỏ hàng chưa có sản phẩm.",
    'CART_LOAD_FAILED': "Không thể tải giỏ hàng. Vui lòng thử lại.",
    'CART_HAS_INVALID_PRODUCT': "Một số sản phẩm trong giỏ không còn được phép đặt. Vui lòng kiểm tra lại.",
    'CART_QUANTITY_INVALID': "Số lượng một số sản phẩm chưa hợp lệ. Vui lòng kiểm tra lại.",
    'CART_IS_PROCESSING': "Giỏ hàng đang được một người dùng khác gửi đơn. Vui lòng thử lại sau.",
    'STORE_CUSTOMER_NOT_CONFIGURED': "Cửa hàng chưa được cấu hình khách hàng đặt hàng. Vui lòng liên hệ Ngô Gia.",
    'ORDER_CREATE_FAILED': "Không thể tạo đơn hàng. Vui lòng thử lại hoặc liên hệ Ngô Gia.",
    'OLD_PORTAL_QUOTATION_CANCEL_FAILED': "Không thể hoàn tất đơn hàng do đơn nháp cũ chưa được xử lý. Vui lòng thử lại.",
    'PRODUCT_LIST_UNAVAILABLE': "Không thể tải danh sách sản phẩm. Vui lòng thử lại.",
    'invalid_input': "Dữ liệu gửi lên không hợp lệ.",
    # legacy codes (redirect cũ có thể còn bookmark)
    'no_active_franchise': "Vui lòng chọn cửa hàng trước khi đặt hàng.",
    'cart_empty': "Giỏ hàng chưa có sản phẩm.",
    'branch_locked': "Cửa hàng đang tạm khóa đặt hàng. Vui lòng liên hệ Ngô Gia.",
    'outside_order_window': "Hiện ngoài khung giờ đặt hàng. Vui lòng gửi đơn trong thời gian cho phép.",
    'internal_error': "Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ Ngô Gia.",
}

SUCCESS_MESSAGES = {
    'order_submitted': "Đã gửi đơn đặt hàng thành công.",
}

# Dòng giỏ không hợp lệ (đánh dấu per-line trên cart view — BA row 11).
LINE_INVALID_MESSAGES = {
    'PRODUCT_NOT_AVAILABLE': "Sản phẩm không còn được phép đặt.",
    'MIN_QTY_NOT_CONFIGURED': "Sản phẩm chưa cấu hình số lượng tối thiểu.",
    'CART_QUANTITY_INVALID': "Số lượng chưa hợp lệ (min/bước/max).",
}


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
    """Trang đặt hàng — catalog + giỏ hàng chung theo store + submit tạo SO draft."""

    # ============================================================== helpers
    def _store_gate(self):
        """Resolve current store — trả (fid, error_code).

        get_active_franchise_id() chỉ trả fid nằm trong accessible list
        (build từ membership đang hiệu lực) → fid truthy = membership hợp lệ.
        Phân loại lỗi theo BA row 1 khi không resolve được.
        """
        fid = get_active_franchise_id()
        if fid:
            return fid, None
        raw = request.httprequest.cookies.get(ACTIVE_FRANCHISE_COOKIE)
        try:
            cookie_fid = int(raw) if raw else 0
        except (TypeError, ValueError):
            cookie_fid = 0
        if cookie_fid:
            had_membership = request.env['wujia.franchise.member'].sudo().search_count([
                ('user_id', '=', request.env.uid),
                ('franchise_id', '=', cookie_fid),
            ])
            return False, 'MEMBERSHIP_INACTIVE' if had_membership else 'STORE_ACCESS_DENIED'
        return False, 'STORE_NOT_SELECTED'

    def _err(self, code, **extra):
        res = {'error': code, 'message': ERROR_MESSAGES.get(code, code)}
        res.update(extra)
        return res

    def _get_franchise(self, fid):
        return request.env['wujia.franchise.management'].sudo().browse(fid).exists()

    def _get_store_cart(self, fid, create=False):
        """Giỏ chung của store — KHÔNG filter theo user (BA row 5).

        Race 2 request cùng tạo giỏ đầu tiên: unique(franchise_id) →
        IntegrityError bọc savepoint (không savepoint = abort cả transaction),
        thua thì search lại lấy giỏ của request thắng.
        """
        Cart = request.env['wujia.portal.cart'].sudo()
        cart = Cart.search([('franchise_id', '=', fid)], limit=1)
        if cart or not create:
            return cart
        try:
            with request.env.cr.savepoint():
                cart = Cart.create({'franchise_id': fid})
        except psycopg2.IntegrityError:
            cart = Cart.search([('franchise_id', '=', fid)], limit=1)
        return cart

    def _get_store_line(self, line_id, fid):
        """Browse line, verify thuộc giỏ của store hiện tại (guard theo store)."""
        line = request.env['wujia.portal.cart.line'].sudo().browse(line_id).exists()
        if not line or line.cart_id.franchise_id.id != fid:
            return None
        return line

    def _get_pricelist(self, franchise):
        partner = franchise.partner_id if franchise else None
        if partner and partner.property_product_pricelist:
            return partner.property_product_pricelist
        return None

    def _price_products(self, pricelist, products, qty=1):
        """{product_id: đơn giá} — 1 call batch; fallback giá chuẩn khi chưa có pricelist."""
        if pricelist and products:
            return pricelist._get_products_price(products, qty)
        return {p.id: p.lst_price for p in products}

    def _price_lines(self, pricelist, lines):
        """{line_id: đơn giá theo qty dòng} — batch theo qty (pricelist có thể theo bậc)."""
        if not pricelist:
            return {line.id: line.product_id.lst_price for line in lines}
        result = {}
        by_qty = defaultdict(list)
        for line in lines:
            by_qty[line.qty or 1].append(line)
        Product = request.env['product.product'].sudo()
        for qty, qty_lines in by_qty.items():
            products = Product.browse([l.product_id.id for l in qty_lines])
            prices = pricelist._get_products_price(products, qty)
            for line in qty_lines:
                result[line.id] = prices.get(line.product_id.id, line.product_id.lst_price)
        return result

    def _line_invalid_reason(self, line):
        product = line.product_id
        if not product.active or not product.is_public_portal:
            return 'PRODUCT_NOT_AVAILABLE'
        if product.min_qty <= 0:
            return 'MIN_QTY_NOT_CONFIGURED'
        if (line.qty < product.min_qty or line.qty % product.min_qty
                or (product.max_qty and line.qty > product.max_qty)):
            return 'CART_QUANTITY_INVALID'
        return None

    def _cart_state(self, cart, franchise):
        """Full state của giỏ — mọi mutation + cart view dùng chung (BA: FE không tự cộng)."""
        Line = request.env['wujia.portal.cart.line'].sudo()
        lines = cart.line_ids if cart else Line.browse()
        pricelist = self._get_pricelist(franchise)
        unit_prices = self._price_lines(pricelist, lines)
        currency = (pricelist.currency_id if pricelist
                    else request.env.company.currency_id)
        lines_data = []
        total_qty = 0
        total_amount = 0.0
        for line in lines:
            product = line.product_id
            unit = unit_prices.get(line.id, 0.0)
            invalid = self._line_invalid_reason(line)
            lines_data.append({
                'line_id': line.id,
                'product_id': product.id,
                'name': product.name,
                'name_chinese': product.name_chinese or '',
                'default_code': product.default_code or '',
                'uom': product.uom_id.name or '—',
                'spec': product.description_ecommerce or '',
                'qty': line.qty,
                'min_qty': product.min_qty,
                'max_qty': product.max_qty,
                'unit_price': unit,
                'subtotal': unit * line.qty,
                'invalid_reason': invalid,
                'invalid_message': LINE_INVALID_MESSAGES.get(invalid, ''),
            })
            total_qty += line.qty
            total_amount += unit * line.qty
        return {
            'cart_id': cart.id if cart else False,
            'note': (cart.note or '') if cart else '',
            'line_count': len(lines_data),
            'total_qty': total_qty,
            'total_amount': total_amount,
            'currency': currency.name or 'VND',
            'currency_symbol': currency.symbol or 'đ',
            'lines': lines_data,
            'has_invalid_line': any(l['invalid_reason'] for l in lines_data),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def _publish_cart_event(self, fid, state, action):
        """Realtime ADR-006: publish để thiết bị/user khác cùng store nhận biết.

        Channel `wujia.franchise_<id>` đã được authorize theo membership trong
        wujia_portal_base/models/ir_websocket.py. JS subscribe = sprint sau
        (deferred — hiện client thấy thay đổi khi reload).
        """
        request.env['bus.bus'].sudo()._sendone(
            f'wujia.franchise_{fid}', 'wujia_cart_changed',
            {
                'franchise_id': fid,
                'action': action,
                'line_count': state['line_count'],
                'total_qty': state['total_qty'],
                'total_amount': state['total_amount'],
            },
        )

    def _cart_fragments(self, fid, franchise, cart):
        """Realtime reconcile: render lại partial giỏ (PC + mobile) + state gọn.

        Dùng chung QWeb với server-render (1 nguồn, không dựng lại row bằng JS).
        JS swap fragment + cập nhật badge catalog/header theo qty_map."""
        cart_state = self._cart_state(cart, franchise)
        # request cần cho request.csrf_token() trong template submit form.
        values = dict(self._order_window_context(franchise),
                      cart_state=cart_state, request=request)
        Qweb = request.env['ir.qweb']
        return {
            'pc_html': str(Qweb._render('wujia_portal_sale.pc_cart_panel', values)),
            'mobile_html': str(Qweb._render('wujia_portal_sale.mcart_panel', values)),
            'qty_map': {ln['product_id']: ln['qty'] for ln in cart_state['lines']},
            'line_count': cart_state['line_count'],
            'total_qty': cart_state['total_qty'],
            'total_amount': cart_state['total_amount'],
        }

    @http.route(['/portal/order/cart/fragment'], type='json', auth='user')
    def portal_order_cart_fragment(self, **kw):
        """State + partial giỏ hiện tại cho client reconcile (bus event / sau mutation)."""
        fid, _gate = self._store_gate()
        if not fid:
            return {'error': 'STORE_NOT_SELECTED'}
        franchise = self._get_franchise(fid)
        cart = self._get_store_cart(fid)
        return self._cart_fragments(fid, franchise, cart)

    def _order_window_context(self, franchise):
        """Context khung giờ cho catalog + cart view (BA row 2: list windows + nguồn)."""
        area_id = franchise.area_id.id if franchise and franchise.area_id else False
        allowed, window = request.env['res.config.settings'].sudo()._is_within_order_window(area_id=area_id)
        return {
            'order_time_from': _float_to_hhmm(window['from']),
            'order_time_to': _float_to_hhmm(window['to']),
            'order_window_enabled': window['enabled'],
            'order_window_open': allowed,
            'order_window_source': window.get('source', 'global'),
            'order_windows': [
                {'name': w.get('name') or '', 'from': _float_to_hhmm(w['from']), 'to': _float_to_hhmm(w['to'])}
                for w in window.get('windows', [])
            ],
            'order_window_not_configured': window['enabled'] and not window.get('configured', True),
        }

    def _resolve_messages(self, kw):
        # Chỉ resolve mã đã biết — không reflect chuỗi lạ từ query string ra UI.
        return {
            'error': ERROR_MESSAGES.get(kw.get('error') or '', ''),
            'message': SUCCESS_MESSAGES.get(kw.get('message') or '', ''),
        }

    # ------------------------------------------------------------------ catalog
    @http.route(['/portal/order'], type='http', auth='user', sitemap=False)
    def portal_order_catalog(self, page=1, category_id=None, keyword='', **kw):
        if not request.env.user._get_accessible_franchise_ids():
            return request.render('wujia_portal_sale.portal_order_catalog', {
                'no_franchise': True, 'products': [], 'categories': [],
                'cart': False, 'cart_state': None, 'price_map': {},
                'pager': {}, 'keyword': '', 'category_id': None,
            })
        fid, gate_error = self._store_gate()
        franchise = self._get_franchise(fid) if fid else None

        Product = request.env['product.product'].sudo()
        domain = [('is_public_portal', '=', True), ('active', '=', True)]
        if keyword:
            # BA row 4: tìm theo tên HOẶC mã sản phẩm.
            domain += ['|', ('name', 'ilike', keyword), ('default_code', 'ilike', keyword)]
        try:
            cat_id = int(category_id) if category_id else None
        except (TypeError, ValueError):
            cat_id = None
        if cat_id:
            domain.append(('public_categ_id', '=', cat_id))

        try:
            page = max(1, int(page))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * PAGE_SIZE
        total = Product.search_count(domain)
        products = Product.search(domain, limit=PAGE_SIZE, offset=offset, order='name asc')

        # Chỉ trả danh mục đang có sản phẩm public (BA row 3) — 1 read_group + 1 search.
        cat_groups = Product._read_group(
            [('is_public_portal', '=', True), ('active', '=', True),
             ('public_categ_id', '!=', False)],
            ['public_categ_id'], [],
        )
        categories = request.env['wujia.product.category'].sudo().search([
            ('id', 'in', [c.id for (c,) in cat_groups]),
        ])

        pricelist = self._get_pricelist(franchise)
        price_map = self._price_products(pricelist, products)

        cart = self._get_store_cart(fid) if fid else False
        cart_state = self._cart_state(cart, franchise)

        pager = self._fallback_pager(total, page, keyword, cat_id)

        msgs = self._resolve_messages(kw)
        return request.render('wujia_portal_sale.portal_order_catalog', {
            'no_franchise': False,
            'active_franchise_id': fid,
            'products': products,
            'price_map': price_map,
            'categories': categories,
            'cart': cart,
            'cart_state': cart_state,
            'pager': pager,
            'product_count': total,
            'page_size': PAGE_SIZE,
            'keyword': keyword,
            'category_id': cat_id,
            'message': msgs['message'],
            'error': msgs['error'] or (ERROR_MESSAGES.get(gate_error, '') if gate_error else ''),
            **self._order_window_context(franchise),
        })

    # ----------------------------------------------------------- product detail
    @http.route(['/portal/order/product/<int:product_id>'],
                type='http', auth='user', sitemap=False)
    def portal_order_product_detail(self, product_id, **kw):
        product = request.env['product.product'].sudo().browse(int(product_id)).exists()
        if not product or not product.is_public_portal or not product.active:
            return request.redirect('/portal/order')
        related = request.env['product.product'].sudo().search([
            ('is_public_portal', '=', True), ('active', '=', True),
            ('public_categ_id', '=', product.public_categ_id.id),
            ('id', '!=', product.id),
        ], limit=6, order='name asc') if product.public_categ_id else \
            request.env['product.product'].sudo().browse()
        fid, _gate_error = self._store_gate()
        franchise = self._get_franchise(fid) if fid else None
        pricelist = self._get_pricelist(franchise)
        price_map = self._price_products(pricelist, product | related)
        return request.render('wujia_portal_sale.portal_order_product_detail', {
            'active_franchise_id': fid,
            'product': product,
            'related': related,
            'price_map': price_map,
        })

    # ----------------------------------------------------------------- cart view
    @http.route(['/portal/order/cart'], type='http', auth='user', sitemap=False)
    def portal_order_cart_view(self, **kw):
        if not request.env.user._get_accessible_franchise_ids():
            return request.redirect('/portal/order')
        fid, gate_error = self._store_gate()
        franchise = self._get_franchise(fid) if fid else None
        cart = self._get_store_cart(fid) if fid else False
        cart_state = self._cart_state(cart, franchise)
        msgs = self._resolve_messages(kw)
        return request.render('wujia_portal_sale.portal_order_cart', {
            'active_franchise_id': fid,
            'cart': cart,
            'cart_state': cart_state,
            'message': msgs['message'],
            'error': msgs['error'] or (ERROR_MESSAGES.get(gate_error, '') if gate_error else ''),
            **self._order_window_context(franchise),
        })

    # ----------------------------------------------------------------- cart add
    @http.route(['/portal/order/cart/add'], type='json', auth='user',
                methods=['POST'])
    @rate_limit(max_calls=60, window_sec=60)
    def portal_cart_add(self, product_id, qty=None, **kw):
        fid, gate_error = self._store_gate()
        if gate_error:
            return self._err(gate_error)
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return self._err('invalid_input')
        product = request.env['product.product'].sudo().browse(product_id).exists()
        if not product or not product.active or not product.is_public_portal:
            return self._err('PRODUCT_NOT_AVAILABLE')
        step = product.min_qty
        if step <= 0:
            return self._err('MIN_QTY_NOT_CONFIGURED')

        # Bước tăng mặc định = min_qty (BA row 6). FE gửi qty tường minh
        # (trang chi tiết) → phải là bội số của bước.
        try:
            increment = int(qty) if qty else step
        except (TypeError, ValueError):
            return self._err('invalid_input')
        if increment < step:
            increment = step
        if increment % step:
            return self._err('QTY_INVALID_STEP')

        franchise = self._get_franchise(fid)
        cart = self._get_store_cart(fid, create=True)
        if not cart:
            return self._err('CART_LOAD_FAILED')

        # Upsert atomic — race-safe khi nhiều user/thiết bị cùng add (giỏ chung).
        # LEAST(cap) chặn trần max_qty ngay trong SQL; audit columns set tay
        # vì raw INSERT không qua ORM.
        cap = product.max_qty if product.max_qty > 0 else 2147483647
        request.env.cr.execute(
            """
            INSERT INTO wujia_portal_cart_line
                   (cart_id, product_id, qty, create_uid, create_date, write_uid, write_date)
            VALUES (%(cart)s, %(product)s, LEAST(%(inc)s, %(cap)s),
                    %(uid)s, now() AT TIME ZONE 'UTC', %(uid)s, now() AT TIME ZONE 'UTC')
            ON CONFLICT (cart_id, product_id) DO UPDATE
               SET qty = LEAST(wujia_portal_cart_line.qty + %(inc)s, %(cap)s),
                   write_uid = %(uid)s,
                   write_date = now() AT TIME ZONE 'UTC'
            RETURNING id, qty
            """,
            {'cart': cart.id, 'product': product_id, 'inc': increment,
             'cap': cap, 'uid': request.env.uid},
        )
        line_id, new_qty = request.env.cr.fetchone()
        request.env['wujia.portal.cart.line'].sudo().invalidate_model()
        cart.invalidate_recordset()

        state = self._cart_state(cart, franchise)
        self._publish_cart_event(fid, state, 'add')
        res = {
            'success': True,
            'line_id': line_id,
            'qty': new_qty,
            'cart_count': state['line_count'],
            'cart': state,
        }
        if product.max_qty and new_qty >= product.max_qty:
            res['warning'] = 'QTY_ABOVE_MAX'
            res['message'] = f"Số lượng tối đa của {product.name} là {product.max_qty}."
        return res

    # -------------------------------------------------------------- cart update
    @http.route(['/portal/order/cart/update'], type='json', auth='user',
                methods=['POST'])
    def portal_cart_update_qty(self, line_id, qty, **kw):
        fid, gate_error = self._store_gate()
        if gate_error:
            return self._err(gate_error)
        try:
            line_id = int(line_id)
            qty = max(0, int(qty))
        except (TypeError, ValueError):
            return self._err('invalid_input')
        franchise = self._get_franchise(fid)
        line = self._get_store_line(line_id, fid)
        cart = line.cart_id if line else self._get_store_cart(fid)
        if not line:
            # Idempotent: dòng đã bị user khác xoá → trả state mới, không lỗi.
            state = self._cart_state(cart, franchise)
            return {'success': True, 'removed': True,
                    'cart_count': state['line_count'], 'cart': state}
        product = line.product_id
        if qty == 0:
            line.unlink()
            state = self._cart_state(cart, franchise)
            self._publish_cart_event(fid, state, 'remove')
            return {'success': True, 'removed': True,
                    'cart_count': state['line_count'], 'cart': state}
        step = product.min_qty
        if step <= 0:
            return self._err('MIN_QTY_NOT_CONFIGURED')
        if qty < step:
            return self._err('QTY_BELOW_MIN',
                             message=f"Số lượng tối thiểu của {product.name} là {step}.")
        if qty % step:
            return self._err('QTY_INVALID_STEP',
                             message=f"Số lượng của {product.name} phải tăng theo bước {step}.")
        if product.max_qty and qty > product.max_qty:
            return self._err('QTY_ABOVE_MAX',
                             message=f"Số lượng tối đa của {product.name} là {product.max_qty}.")
        line.write({'qty': qty})
        state = self._cart_state(cart, franchise)
        self._publish_cart_event(fid, state, 'update')
        line_state = next((l for l in state['lines'] if l['line_id'] == line.id), None)
        return {'success': True, 'qty': qty,
                'cart_count': state['line_count'],
                'line': line_state, 'cart': state}

    # -------------------------------------------------------------- cart remove
    @http.route(['/portal/order/cart/remove'], type='json', auth='user',
                methods=['POST'])
    def portal_cart_remove(self, line_id, **kw):
        fid, gate_error = self._store_gate()
        if gate_error:
            return self._err(gate_error)
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            return self._err('invalid_input')
        franchise = self._get_franchise(fid)
        line = self._get_store_line(line_id, fid)
        cart = line.cart_id if line else self._get_store_cart(fid)
        if line:
            line.unlink()
        state = self._cart_state(cart, franchise)
        self._publish_cart_event(fid, state, 'remove')
        return {'success': True, 'cart_count': state['line_count'], 'cart': state}

    # --------------------------------------------------------------- cart count
    @http.route(['/portal/order/cart/count'], type='json', auth='user',
                methods=['GET', 'POST'])
    def portal_cart_count(self, **kw):
        fid, gate_error = self._store_gate()
        if gate_error:
            return {'count': 0, 'line_count': 0, 'total_qty': 0}
        Line = request.env['wujia.portal.cart.line'].sudo()
        groups = Line._read_group(
            [('cart_id.franchise_id', '=', fid)], [], ['__count', 'qty:sum'],
        )
        line_count, total_qty = groups[0] if groups else (0, 0)
        # `count` giữ nguyên cho badge JS cũ = số dòng (SKU) — BA row 10 phân biệt 2 số.
        return {'count': line_count, 'line_count': line_count,
                'total_qty': int(total_qty or 0)}

    # ---------------------------------------------------------------- cart note
    @http.route(['/portal/order/cart/note'], type='json', auth='user',
                methods=['POST'])
    @rate_limit(max_calls=30, window_sec=60)
    def portal_cart_note(self, note='', **kw):
        fid, gate_error = self._store_gate()
        if gate_error:
            return self._err(gate_error)
        cart = self._get_store_cart(fid, create=True)
        if not cart:
            return self._err('CART_LOAD_FAILED')
        # Lưu plain text (render qua t-esc); escape sang Html khi map vào SO note.
        cart.write({'note': (note or '').strip()[:1000]})
        franchise = self._get_franchise(fid)
        state = self._cart_state(cart, franchise)
        self._publish_cart_event(fid, state, 'note')
        return {'success': True, 'note': cart.note or '',
                'updated_at': state['updated_at']}

    # ------------------------------------------------------------ submit order
    @http.route(['/portal/order/submit'], type='http', auth='user',
                methods=['POST'], sitemap=False, csrf=True)
    def portal_order_submit(self, **post):
        fid, gate_error = self._store_gate()
        if gate_error:
            return request.redirect(f'/portal/order/cart?error={gate_error}')
        franchise = self._get_franchise(fid)
        if not franchise:
            return request.redirect('/portal/order/cart?error=STORE_ACCESS_DENIED')
        if franchise.portal_locked:
            return request.redirect('/portal/order/cart?error=branch_locked')
        cart = self._get_store_cart(fid)
        if not cart or not cart.line_ids:
            return request.redirect('/portal/order/cart?error=CART_EMPTY')

        # Khoá giỏ chung — savepoint BẮT BUỘC: LockNotAvailable nằm trong danh sách
        # Odoo tự retry request; bọc savepoint thì exception dừng ở đây và ta trả
        # CART_IS_PROCESSING thay vì retry 5 lần (2 user cùng bấm Gửi đơn).
        # Row lock sống tới hết transaction (RELEASE SAVEPOINT không nhả lock);
        # snapshot lines đọc ngay trong block để giữ đúng ý "snapshot-at-lock" —
        # thay đổi đến sau thời điểm này rơi vào giỏ mới (BA: last-write-wins).
        try:
            with request.env.cr.savepoint():
                request.env.cr.execute(
                    "SELECT id FROM wujia_portal_cart WHERE id = %s FOR UPDATE NOWAIT",
                    (cart.id,),
                )
                request.env['wujia.portal.cart.line'].sudo().invalidate_model()
                cart.invalidate_recordset()
                lines = cart.line_ids
        except pg_errors.LockNotAvailable:
            return request.redirect('/portal/order/cart?error=CART_IS_PROCESSING')
        if not lines:
            return request.redirect('/portal/order/cart?error=CART_EMPTY')

        # Chưa cấu hình khung giờ → helper dùng default 10:00–04:00 (BA row 2:
        # ORDER_TIME_NOT_CONFIGURED chỉ là banner cảnh báo, không chặn submit).
        area_id = franchise.area_id.id if franchise.area_id else False
        allowed, _w = request.env['res.config.settings'].sudo()._is_within_order_window(area_id=area_id)
        if not allowed:
            return request.redirect('/portal/order/cart?error=ORDER_TIME_CLOSED')

        invalid_reasons = {self._line_invalid_reason(l) for l in lines} - {None}
        if invalid_reasons:
            code = ('CART_QUANTITY_INVALID'
                    if invalid_reasons == {'CART_QUANTITY_INVALID'}
                    else 'CART_HAS_INVALID_PRODUCT')
            return request.redirect(f'/portal/order/cart?error={code}')

        partner = franchise.partner_id
        if not partner:
            return request.redirect('/portal/order/cart?error=STORE_CUSTOMER_NOT_CONFIGURED')

        # Huỷ draft/sent portal cũ = rule "1 store 1 draft" (POR-022). Check locked
        # TRƯỚC khi tạo SO mới — fail sớm, không cần rollback (BA row 13 nguyên khối).
        SO = request.env['sale.order'].sudo()
        old_quotations = SO.search([
            ('franchise_id', '=', fid),
            ('is_portal_order', '=', True),
            ('state', 'in', ('draft', 'sent')),
        ])
        if any(old_quotations.mapped('locked')):
            _logger.warning('Portal submit blocked: locked portal quotation(s) %s (store %s)',
                            old_quotations.filtered('locked').ids, fid)
            return request.redirect('/portal/order/cart?error=OLD_PORTAL_QUOTATION_CANCEL_FAILED')

        member = request.env['wujia.franchise.member'].sudo().find_active_membership(
            request.env.uid, fid,
        )
        note_text = (post.get('portal_note') or cart.note or '').strip()[:1000]
        so_vals = {
            'is_portal_order': True,
            'franchise_id': fid,
            'franchise_partner_id': partner.id,
            'partner_id': partner.id,
            # Pricelist tường minh = pricelist đã dùng tính giá catalog/giỏ →
            # price_unit SO line (Odoo tự compute) khớp giá đã hiển thị.
            'pricelist_id': partner.property_product_pricelist.id or False,
            # sudo() giữ env.uid → create_uid = user portal (POR-019).
            'portal_requester_user_id': request.env.uid,
            'portal_member_id': member.id if member else False,
            'origin': 'Wujia Portal',
            # Ghi 2 field: portal_note (Text — trang Lịch sử portal render field này)
            # + note theo BA mapping. note là Html field: plaintext2html escape user
            # input + giữ xuống dòng (bare str bị sanitize làm hỏng; Markup thô = XSS).
            'portal_note': note_text or False,
            'note': plaintext2html(note_text) if note_text else False,
            'order_line': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'product_uom_id': line.product_id.uom_id.id,
                }) for line in lines
            ],
        }
        try:
            order = SO.create(so_vals)  # SO ở DRAFT — BA: không action_confirm
        except ValidationError as e:
            msg = str(e)
            _logger.warning('Portal order create rejected (store %s): %s', fid, msg)
            code = 'ORDER_TIME_CLOSED' if 'khung giờ' in msg else 'ORDER_CREATE_FAILED'
            return request.redirect(f'/portal/order/cart?error={code}')
        except (UserError, Exception):
            _logger.exception('Portal order create failed (store %s)', fid)
            return request.redirect('/portal/order/cart?error=ORDER_CREATE_FAILED')

        # write state trực tiếp (không action_cancel): tránh cascade huỷ draft
        # invoice + chatter storm; đã loại locked ở trên. Nguyên khối BA row 13:
        # bất kỳ lỗi nào ở bước huỷ/clear → rollback cả SO mới vừa tạo.
        try:
            old_quotations.write({'state': 'cancel'})
            still_open = old_quotations.filtered(lambda o: o.state != 'cancel')
            if still_open:
                raise UserError(f'cancel failed: {still_open.ids}')
            # Clear giỏ cuối cùng, cùng transaction — commit thì thiết bị khác thấy giỏ trống.
            lines.unlink()
            cart.write({'note': False})
        except Exception:
            _logger.exception('Portal submit: cancel-old/clear-cart failed (store %s)', fid)
            request.env.cr.rollback()
            return request.redirect('/portal/order/cart?error=OLD_PORTAL_QUOTATION_CANCEL_FAILED')
        state = self._cart_state(cart, franchise)
        self._publish_cart_event(fid, state, 'submit')
        return request.redirect(
            f'/portal/purchase-history/{order.id}?message=order_submitted'
        )

    # ============================================================== pager
    def _fallback_pager(self, total, page, keyword='', cat_id=None):
        last = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        def _u(n):
            args = {'page': n}
            if keyword:
                args['keyword'] = keyword
            if cat_id:
                args['category_id'] = cat_id
            return '/portal/order?' + urlencode(args)

        return {
            'page': {'num': page, 'url': _u(page)},
            'page_count': last, 'page_total': total,
            'page_first': {'num': 1, 'url': _u(1)},
            'page_last': {'num': last, 'url': _u(last)},
            'page_previous': {'num': max(1, page - 1), 'url': _u(max(1, page - 1))},
            'page_next': {'num': min(last, page + 1), 'url': _u(min(last, page + 1))},
            'pages': [{'num': n, 'url': _u(n)} for n in range(1, last + 1)],
        }
