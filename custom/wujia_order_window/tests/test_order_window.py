"""Đặc tả khung giờ đặt hàng: khu vực trước, fallback cấu hình chung, qua nửa đêm, chặn đơn portal."""
from datetime import date, datetime
from unittest.mock import patch

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.wujia_order_window.models.sale_order import OrderWindowClosed

TODAY = date(2026, 9, 25)


@tagged('post_install', '-at_install', 'wujia_order_window')
class TestOrderWindow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Area = env['res.area']
        cls.area = Area.create({'code': 'F7-A', 'name': 'F7 có khung'})
        cls.area_empty = Area.create({'code': 'F7-B', 'name': 'F7 không khung'})
        cls.Window = env['wujia.order.window']
        cls.morning = cls.Window.create({
            'name': 'Sáng', 'area_id': cls.area.id, 'order_time_from': 7.0,
            'order_time_to': 11.5, 'sequence': 1})
        cls.evening = cls.Window.create({
            'name': 'Tối', 'area_id': cls.area.id, 'order_time_from': 20.0,
            'order_time_to': 2.0, 'sequence': 2})
        cls.Window.create({
            'name': 'Cũ', 'area_id': cls.area.id, 'order_time_from': 12.0,
            'order_time_to': 13.0, 'active': False})
        cls.ICP = env['ir.config_parameter'].sudo()
        cls.ICP.set_param('wujia_portal.portal_order_time_from', '9.0')
        cls.ICP.set_param('wujia_portal.portal_order_time_to', '3.0')
        cls.ICP.set_param('wujia_portal.portal_order_time_limit_enabled', 'True')
        cls.Settings = env['res.config.settings']
        cls.partner = env['res.partner'].create({'name': 'F7 partner'})
        cls.franchise = env['wujia.franchise.management'].create({
            'code': 'F7ST', 'name': 'F7 store', 'franchise_end_date': '2030-01-01',
            'partner_id': cls.partner.id, 'area_id': cls.area.id})

    def at(self, hours):
        cls = type(self.Settings)
        now_dt = datetime.combine(TODAY, datetime.min.time())
        return _Clock(cls, hours, now_dt)

    def check(self, hours, area=None):
        with self.at(hours):
            return self.Settings._is_within_order_window(area_id=area.id if area else None)

    def test_area_windows_take_priority(self):
        for hours, expected in [(6.99, False), (7.0, True), (11.5, True), (15.0, False),
                                (12.5, False), (20.0, True), (1.0, True), (2.5, False)]:
            with self.subTest(hours=hours):
                self.assertEqual(self.check(hours, self.area)[0], expected)
        allowed, window = self.check(9.0, self.area)
        self.assertEqual(window['source'], 'area:%s' % self.area.id)
        self.assertEqual((window['from'], window['to'], window['window_name']), (7.0, 11.5, 'Sáng'))
        self.assertEqual(window['window_count'], 2)
        self.assertEqual([w['name'] for w in window['windows']], ['Sáng', 'Tối'])

    def test_area_without_window_uses_global(self):
        for hours, expected in [(8.9, False), (9.0, True), (23.0, True), (3.0, True), (3.1, False)]:
            with self.subTest(hours=hours):
                self.assertEqual(self.check(hours, self.area_empty)[0], expected)
        _allowed, window = self.check(12.0)
        self.assertEqual(window['source'], 'global')
        self.assertEqual(window['windows'], [{'name': '', 'from': 9.0, 'to': 3.0}])
        self.assertTrue(window['configured'])

    def test_global_same_day_window(self):
        self.ICP.set_param('wujia_portal.portal_order_time_from', '8.0')
        self.ICP.set_param('wujia_portal.portal_order_time_to', '17.0')
        self.assertEqual([self.check(h)[0] for h in (7.9, 8.0, 17.0, 17.1)], [False, True, True, False])

    def test_disabled_always_open(self):
        self.ICP.set_param('wujia_portal.portal_order_time_limit_enabled', 'False')
        allowed, window = self.check(15.0, self.area)
        self.assertTrue(allowed)
        self.assertEqual((window['source'], window['windows'], window['enabled']), ('global', [], False))
        with self.at(15.0):
            self.assertIsNone(self.Settings._next_order_window(area_id=self.area.id))

    def test_not_configured_flag(self):
        self.ICP.search([('key', '=', 'wujia_portal.portal_order_time_from')]).unlink()
        _allowed, window = self.check(12.0)
        self.assertFalse(window['configured'])
        self.assertEqual(window['from'], 10.0)

    def test_next_window_today_then_tomorrow(self):
        with self.at(5.0):
            nxt = self.Settings._next_order_window(area_id=self.area.id)
        self.assertEqual((nxt['name'], nxt['from'], nxt['date'], nxt['is_today']), ('Sáng', 7.0, TODAY, True))
        with self.at(15.0):
            nxt = self.Settings._next_order_window(area_id=self.area.id)
        self.assertEqual((nxt['name'], nxt['is_today']), ('Tối', True))
        with self.at(21.0):
            nxt = self.Settings._next_order_window(area_id=self.area.id)
        self.assertEqual((nxt['name'], nxt['date'], nxt['is_today']), ('Sáng', date(2026, 9, 26), False))

    def test_window_constraints(self):
        self.assertTrue(self.evening.is_overnight)
        self.assertFalse(self.morning.is_overnight)
        with self.assertRaises(ValidationError):
            self.Window.create({'name': 'Rỗng', 'area_id': self.area.id,
                                'order_time_from': 8.0, 'order_time_to': 8.0})
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.Window.create({'name': 'Quá 24', 'area_id': self.area.id,
                                'order_time_from': 24.0, 'order_time_to': 8.0})

    def so_vals(self, portal=True):
        return {'partner_id': self.partner.id, 'franchise_id': self.franchise.id, 'is_portal_order': portal}

    def test_portal_order_blocked_outside_window(self):
        SO = self.env['sale.order']
        with self.at(15.0), self.assertRaises(OrderWindowClosed) as err:
            SO.create(self.so_vals())
        self.assertIn('khung giờ nhận đơn', str(err.exception))
        self.assertIsInstance(err.exception, ValidationError)
        with self.at(15.0):
            self.assertTrue(SO.create(self.so_vals(portal=False)))
        with self.at(9.0):
            self.assertTrue(SO.create(self.so_vals()))


class _Clock:
    """Đóng băng giờ người dùng cho cả hai helper đọc đồng hồ."""

    def __init__(self, cls, hours, now_dt):
        self.patches = [patch.object(cls, '_user_now_hours', return_value=hours),
                        patch.object(cls, '_user_now_dt', return_value=now_dt)]

    def __enter__(self):
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in self.patches:
            p.stop()
