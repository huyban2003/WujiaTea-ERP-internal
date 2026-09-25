"""F6 — đặc tả hành vi giỏ + gửi đơn portal (response JSON, mã lỗi, câu chữ, redirect).

Viết trước khi dời luật từ controller về model: mọi assert ở đây phải xanh
cả trước lẫn sau F6.
"""
from unittest.mock import patch
from urllib.parse import urlsplit

from odoo import http
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.wujia_order_window.models.sale_order import OrderWindowClosed
from odoo.addons.wujia_portal_base.controllers.utils import _RateLimiter

OPEN = (True, {'from': 10.0, 'to': 4.0, 'enabled': True, 'configured': True,
               'source': 'global', 'windows': []})
CLOSED = (False, dict(OPEN[1]))

ADD_KEYS = {'success', 'line_id', 'qty', 'cart_count', 'cart'}
UPDATE_KEYS = {'success', 'qty', 'cart_count', 'line', 'cart'}
STEP_KEYS = {'success', 'removed', 'qty', 'cart_count', 'cart', 'line'}
REMOVED_KEYS = {'success', 'removed', 'cart_count', 'cart'}


@tagged('post_install', '-at_install', 'wujia_f6')
class TestF6CartSubmit(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.partner = env['res.partner'].create({'name': 'F6 partner'})
        cls.franchise = env['wujia.franchise.management'].create({
            'code': 'F6ST', 'name': 'F6 store', 'franchise_end_date': '2030-01-01',
            'partner_id': cls.partner.id})
        cls.user = env['res.users'].create({
            'name': 'f6_owner', 'login': 'f6_owner', 'password': 'f6_owner',
            'group_ids': [(6, 0, [env.ref('base.group_portal').id])]})
        cls.member = env['wujia.franchise.member'].create({
            'user_id': cls.user.id, 'franchise_id': cls.franchise.id, 'role': 'owner'})
        Product = env['product.product']
        cls.p_max = Product.create({
            'name': 'F6 Max', 'type': 'consu', 'list_price': 10000,
            'is_public_portal': True, 'min_qty': 2, 'max_qty': 10})
        cls.p_free = Product.create({
            'name': 'F6 Free', 'type': 'consu', 'list_price': 5000,
            'is_public_portal': True, 'min_qty': 3})
        cls.p_one = Product.create({
            'name': 'F6 One', 'type': 'consu', 'list_price': 1000,
            'is_public_portal': True, 'min_qty': 1})
        cls.Settings = type(env['res.config.settings'])

    def setUp(self):
        super().setUp()
        _RateLimiter._store.clear()
        self.authenticate('f6_owner', 'f6_owner')

    # ------------------------------------------------------------ helpers
    def rpc(self, route, **params):
        return self.make_jsonrpc_request(route, params)

    def cart(self):
        self.env.invalidate_all()
        return self.env['wujia.portal.cart'].search([('franchise_id', '=', self.franchise.id)])

    def qty_of(self, product):
        line = self.cart().line_ids.filtered(lambda l: l.product_id == product)
        return line.qty if line else 0

    def put(self, product, qty):
        cart = self.cart() or self.env['wujia.portal.cart'].create({'franchise_id': self.franchise.id})
        line = cart.line_ids.filtered(lambda l: l.product_id == product)
        if line:
            line.qty = qty
        else:
            line = self.env['wujia.portal.cart.line'].create(
                {'cart_id': cart.id, 'product_id': product.id, 'qty': qty})
        return line

    def submit(self, window=OPEN, **data):
        data['csrf_token'] = http.Request.csrf_token(self)
        side = window if isinstance(window, list) else None
        kw = {'side_effect': side} if side else {'return_value': window}
        with patch.object(self.Settings, '_is_within_order_window', **kw):
            res = self.url_open('/portal/order/submit', data=data, allow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        loc = urlsplit(res.headers['Location'])
        return loc.path + (f'?{loc.query}' if loc.query else '')

    def portal_orders(self):
        self.env.invalidate_all()
        return self.env['sale.order'].search([('franchise_id', '=', self.franchise.id)])

    # ------------------------------------------------------------ add
    def test_add_default_step_then_accumulates(self):
        res = self.rpc('/portal/order/cart/add', product_id=self.p_free.id)
        self.assertEqual(set(res), ADD_KEYS)
        self.assertEqual((res['success'], res['qty'], res['cart_count']), (True, 3, 1))
        res = self.rpc('/portal/order/cart/add', product_id=self.p_free.id)
        self.assertEqual(res['qty'], 6)
        self.assertEqual(res['cart']['lines'][0]['qty'], 6)

    def test_add_explicit_qty_invalid(self):
        cases = [
            ('abc', 'invalid_input', "Dữ liệu gửi lên không hợp lệ."),
            ('1.5', 'QTY_INVALID_STEP', "Số lượng của F6 Max phải là số nguyên."),
            (1, 'QTY_BELOW_MIN', "Số lượng tối thiểu của F6 Max là 2."),
            (5, 'QTY_INVALID_STEP', "Số lượng của F6 Max phải tăng theo bước 2."),
            (12, 'QTY_ABOVE_MAX', "Số lượng tối đa của F6 Max là 10."),
        ]
        for qty, code, msg in cases:
            with self.subTest(qty=qty):
                res = self.rpc('/portal/order/cart/add', product_id=self.p_max.id, qty=qty)
                self.assertEqual(res, {'error': code, 'message': msg})
        self.assertEqual(self.qty_of(self.p_max), 0)

    def test_add_explicit_qty_valid(self):
        res = self.rpc('/portal/order/cart/add', product_id=self.p_max.id, qty=4)
        self.assertEqual(res['qty'], 4)
        self.assertNotIn('warning', res)

    def test_add_caps_at_max_with_warning(self):
        self.put(self.p_max, 8)
        res = self.rpc('/portal/order/cart/add', product_id=self.p_max.id, qty=6)
        self.assertEqual(res['qty'], 10)
        self.assertEqual(res['warning'], 'QTY_ABOVE_MAX')
        self.assertEqual(res['message'], "Số lượng tối đa của F6 Max là 10.")
        self.assertEqual(self.qty_of(self.p_max), 10)

    def test_add_product_not_available(self):
        hidden = self.env['product.product'].create({'name': 'F6 Hidden', 'type': 'consu'})
        res = self.rpc('/portal/order/cart/add', product_id=hidden.id)
        self.assertEqual(res['error'], 'PRODUCT_NOT_AVAILABLE')
        self.assertEqual(res['message'], "Sản phẩm này hiện không còn được phép đặt hàng.")
        res = self.rpc('/portal/order/cart/add', product_id='x')
        self.assertEqual(res['error'], 'invalid_input')

    def test_add_min_not_configured(self):
        self.env.cr.execute('UPDATE product_product SET min_qty = 0 WHERE id = %s', (self.p_one.id,))
        self.env.invalidate_all()
        res = self.rpc('/portal/order/cart/add', product_id=self.p_one.id)
        self.assertEqual(res['error'], 'MIN_QTY_NOT_CONFIGURED')

    # ------------------------------------------------------------ update
    def test_update_valid_and_zero_removes(self):
        line = self.put(self.p_max, 2)
        res = self.rpc('/portal/order/cart/update', line_id=line.id, qty=6)
        self.assertEqual(set(res), UPDATE_KEYS)
        self.assertEqual((res['qty'], res['line']['qty']), (6, 6))
        res = self.rpc('/portal/order/cart/update', line_id=line.id, qty=-3)
        self.assertEqual(set(res), REMOVED_KEYS)
        self.assertTrue(res['removed'])
        self.assertEqual(self.qty_of(self.p_max), 0)
        res = self.rpc('/portal/order/cart/update', line_id=line.id, qty=4)
        self.assertEqual(set(res), REMOVED_KEYS)

    def test_update_invalid(self):
        line = self.put(self.p_max, 2)
        cases = [
            (1, 'QTY_BELOW_MIN', "Số lượng tối thiểu của F6 Max là 2."),
            (3, 'QTY_INVALID_STEP', "Số lượng của F6 Max phải tăng theo bước 2."),
            (14, 'QTY_ABOVE_MAX', "Số lượng tối đa của F6 Max là 10."),
            ('x', 'invalid_input', "Dữ liệu gửi lên không hợp lệ."),
        ]
        for qty, code, msg in cases:
            with self.subTest(qty=qty):
                res = self.rpc('/portal/order/cart/update', line_id=line.id, qty=qty)
                self.assertEqual(res, {'error': code, 'message': msg})
        self.assertEqual(self.qty_of(self.p_max), 2)

    # ------------------------------------------------------------ step
    def test_step_inc_dec_by_line(self):
        line = self.put(self.p_max, 2)
        res = self.rpc('/portal/order/cart/step', line_id=line.id, direction='inc')
        self.assertEqual(set(res), STEP_KEYS)
        self.assertEqual((res['qty'], res['removed'], res['line']['qty']), (4, False, 4))
        res = self.rpc('/portal/order/cart/step', line_id=line.id, direction='dec')
        self.assertEqual(res['qty'], 2)
        res = self.rpc('/portal/order/cart/step', line_id=line.id, direction='dec')
        self.assertEqual(set(res), STEP_KEYS - {'line'})
        self.assertEqual((res['qty'], res['removed']), (0, True))
        self.assertEqual(self.qty_of(self.p_max), 0)
        res = self.rpc('/portal/order/cart/step', line_id=line.id, direction='dec')
        self.assertEqual(set(res), REMOVED_KEYS)

    def test_step_by_product_and_cap(self):
        self.put(self.p_max, 8)
        res = self.rpc('/portal/order/cart/step', product_id=self.p_max.id, direction='inc')
        self.assertEqual(res['qty'], 10)
        self.assertEqual(res['warning'], 'QTY_ABOVE_MAX')
        res = self.rpc('/portal/order/cart/step', product_id=self.p_max.id, direction='inc')
        self.assertEqual(res['qty'], 10)
        res = self.rpc('/portal/order/cart/step', product_id=self.p_max.id, direction='up')
        self.assertEqual(res['error'], 'invalid_input')
        res = self.rpc('/portal/order/cart/step', direction='inc')
        self.assertEqual(res['error'], 'invalid_input')

    # ------------------------------------------------------------ remove
    def test_remove_idempotent(self):
        line = self.put(self.p_free, 3)
        res = self.rpc('/portal/order/cart/remove', line_id=line.id)
        self.assertEqual(set(res), {'success', 'cart_count', 'cart'})
        self.assertEqual(res['cart_count'], 0)
        res = self.rpc('/portal/order/cart/remove', line_id=line.id)
        self.assertTrue(res['success'])

    # ------------------------------------------------------------ submit
    def test_submit_empty_cart(self):
        self.assertEqual(self.submit(), '/portal/order/cart?error=CART_EMPTY')

    def test_submit_store_locked(self):
        self.franchise.portal_locked = True
        self.assertEqual(self.submit(), '/portal/order/cart?error=branch_locked')
        self.assertFalse(self.cart())
        self.put(self.p_free, 3)
        self.assertEqual(self.submit(), '/portal/order/cart?error=branch_locked')

    def test_submit_outside_window(self):
        self.put(self.p_free, 3)
        self.assertEqual(self.submit(CLOSED), '/portal/order/cart?error=ORDER_TIME_CLOSED')
        self.assertEqual(self.submit(CLOSED, flow='m'),
                         '/portal/order/rejected?reason=ORDER_TIME_CLOSED')
        self.assertEqual(self.qty_of(self.p_free), 3)
        self.assertFalse(self.portal_orders())

    def test_submit_window_closes_during_create(self):
        self.put(self.p_free, 3)
        self.assertEqual(self.submit([OPEN, CLOSED]), '/portal/order/cart?error=ORDER_TIME_CLOSED')
        self.assertEqual(self.qty_of(self.p_free), 3)

    def test_submit_create_error_mapped_by_class_not_text(self):
        self.put(self.p_free, 3)
        SO = type(self.env['sale.order'])
        cases = [
            (OrderWindowClosed('closed'), '/portal/order/cart?error=ORDER_TIME_CLOSED'),
            (ValidationError('Sai khung giờ giao'), '/portal/order/cart?error=ORDER_CREATE_FAILED'),
        ]
        for exc, expected in cases:
            with self.subTest(exc=exc), patch.object(SO, 'create', side_effect=exc):
                self.assertEqual(self.submit(), expected)
        self.assertEqual(self.qty_of(self.p_free), 3)

    def test_submit_invalid_lines(self):
        self.put(self.p_free, 4)
        self.assertEqual(self.submit(), '/portal/order/cart?error=CART_QUANTITY_INVALID')
        self.p_one.is_public_portal = False
        self.put(self.p_one, 1)
        self.assertEqual(self.submit(), '/portal/order/cart?error=CART_HAS_INVALID_PRODUCT')
        self.assertFalse(self.portal_orders())

    def test_submit_locked_old_quotation(self):
        with patch.object(self.Settings, '_is_within_order_window', return_value=OPEN):
            old = self.env['sale.order'].create({
                'partner_id': self.partner.id, 'franchise_id': self.franchise.id,
                'is_portal_order': True, 'locked': True})
        self.put(self.p_free, 3)
        self.assertEqual(self.submit(), '/portal/order/cart?error=OLD_PORTAL_QUOTATION_CANCEL_FAILED')
        self.assertEqual(self.portal_orders(), old)
        self.assertEqual(self.qty_of(self.p_free), 3)

    def test_submit_success_pc(self):
        with patch.object(self.Settings, '_is_within_order_window', return_value=OPEN):
            old = self.env['sale.order'].create({
                'partner_id': self.partner.id, 'franchise_id': self.franchise.id,
                'is_portal_order': True})
        self.put(self.p_free, 6)
        self.put(self.p_max, 2)
        self.cart().note = 'Giao sớm'
        SO = type(self.env['sale.order'])
        with patch.object(SO, 'action_cancel', side_effect=AssertionError('action_cancel')):
            loc = self.submit(portal_note='Giao <b>sớm</b>\ndòng 2')
        new = self.portal_orders() - old
        self.assertEqual(len(new), 1)
        self.assertEqual(loc, f'/portal/purchase-history/{new.id}?message=order_submitted')
        self.assertEqual(new.state, 'draft')
        self.assertEqual(new.create_uid, self.user)
        self.assertEqual(new.portal_requester_user_id, self.user)
        self.assertEqual(new.portal_member_id, self.member)
        self.assertEqual(new.origin, 'Wujia Portal')
        self.assertEqual(new.portal_note, 'Giao <b>sớm</b>\ndòng 2')
        self.assertIn('&lt;b&gt;', str(new.note))
        self.assertEqual(sorted(new.order_line.mapped('product_uom_qty')), [2, 6])
        self.assertEqual(old.state, 'cancel')
        cart = self.cart()
        self.assertFalse(cart.line_ids)
        self.assertFalse(cart.note)

    def test_submit_success_mobile_uses_cart_note(self):
        self.put(self.p_free, 3)
        self.cart().note = 'Ghi chú giỏ'
        loc = self.submit(flow='m')
        new = self.portal_orders()
        self.assertEqual(loc, f'/portal/order/submitted/{new.id}')
        self.assertEqual(new.portal_note, 'Ghi chú giỏ')

    def test_submit_create_failure_leaves_no_order(self):
        SO = type(self.env['sale.order'])
        orig = SO.create

        def create_then_fail(self_, vals):
            orig(self_, vals)
            raise ValidationError('f6 boom')

        self.put(self.p_free, 3)
        with patch.object(SO, 'create', create_then_fail):
            loc = self.submit()
        self.assertEqual(loc, '/portal/order/cart?error=ORDER_CREATE_FAILED')
        self.assertFalse(self.portal_orders())
        self.assertEqual(self.qty_of(self.p_free), 3)


@tagged('post_install', '-at_install', 'wujia_f6')
class TestF6LineConstraint(HttpCase):

    def test_constraint_messages_unchanged(self):
        env = self.env
        partner = env['res.partner'].create({'name': 'F6c'})
        franchise = env['wujia.franchise.management'].create({
            'code': 'F6C', 'name': 'F6 C store', 'franchise_end_date': '2030-01-01',
            'partner_id': partner.id})
        product = env['product.product'].create({
            'name': 'F6 C', 'type': 'consu', 'is_public_portal': True,
            'min_qty': 2, 'max_qty': 6})
        Settings = type(env['res.config.settings'])
        cases = [
            (1, "Sản phẩm 'F6 C' yêu cầu số lượng tối thiểu 2, đang đặt 1.0."),
            (3, "Số lượng của 'F6 C' phải tăng theo bước 2, đang đặt 3.0."),
            (8, "Sản phẩm 'F6 C' chỉ cho phép tối đa 6/đơn, đang đặt 8.0."),
        ]
        with patch.object(Settings, '_is_within_order_window', return_value=OPEN):
            for qty, msg in cases:
                with self.subTest(qty=qty), self.assertRaises(ValidationError) as cm:
                    env['sale.order'].create({
                        'partner_id': partner.id, 'is_portal_order': True,
                        'franchise_id': franchise.id,
                        'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': qty})]})
                self.assertEqual(str(cm.exception.args[0]), msg)
            loose = env['product.product'].create({
                'name': 'F6 L', 'type': 'consu', 'min_qty': 0, 'max_qty': 6})
            with self.assertRaises(ValidationError) as cm:
                env['sale.order'].create({
                    'partner_id': partner.id, 'is_portal_order': True, 'franchise_id': franchise.id,
                    'order_line': [(0, 0, {'product_id': loose.id, 'product_uom_qty': 7})]})
            self.assertEqual(str(cm.exception.args[0]),
                             "Sản phẩm 'F6 L' chỉ cho phép tối đa 6/đơn, đang đặt 7.0.")
            order = env['sale.order'].create({
                'partner_id': partner.id,
                'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 1})]})
            self.assertTrue(order)
            gift = env['sale.order'].create({
                'partner_id': partner.id, 'is_portal_order': True,
                'franchise_id': franchise.id,
                'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 1,
                                       'wujia_is_gift': True})]})
            self.assertTrue(gift)
