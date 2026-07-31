"""Test module Công nợ portal — chạy bằng `--test-tags wujia_debt`.

Vì scope là UI-only, test tập trung vào 2 thứ có thể vỡ thật:
  1. `wujia.portal.debt` — seam dữ liệu: đủ key, số cộng đúng, filter không raise.
  2. Route + 2 view inherit — render 200, không 500 kể cả khi chưa chọn cửa hàng.
"""

from datetime import date, timedelta

from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

SUMMARY_KEYS = {
    'franchise_id', 'franchise_code', 'week_key', 'week_label', 'week_number',
    'week_short', 'weeks', 'state', 'total', 'paid', 'remaining', 'invoice_count',
    'has_overdue', 'overdue_count', 'nearest_due', 'confirmed_date', 'invoices',
}


@tagged('post_install', '-at_install', 'wujia_debt')
class TestPortalDebtModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.debt = cls.env['wujia.portal.debt']
        cls.franchise = cls.env['wujia.franchise.management'].search([], limit=1)
        cls.franchise_id = cls.franchise.id or 1

    def _all_states(self):
        """1 summary cho mỗi state, lấy qua các tuần trong dropdown."""
        found = {}
        for opt in self.debt._week_options():
            summary = self.debt.get_summary(self.franchise_id, week=opt['key'])
            found.setdefault(summary['state'], summary)
        return found

    def test_summary_keys_all_states(self):
        """Mọi state trả ĐỦ key — template không phải .get() phòng thủ."""
        states = self._all_states()
        self.assertEqual(set(states), {'outstanding', 'partial', 'paid', 'empty'},
                         'Dropdown tuần phải chạm được cả 4 biến thể Figma 02-05')
        for state, summary in states.items():
            self.assertTrue(SUMMARY_KEYS.issubset(set(summary)),
                            'Thiếu key ở state %s: %s' % (state, SUMMARY_KEYS - set(summary)))

    def test_amounts_are_consistent(self):
        """paid + remaining == total, và remaining == tổng dư của các hoá đơn."""
        for state, summary in self._all_states().items():
            self.assertEqual(summary['paid'] + summary['remaining'], summary['total'],
                             'Cộng sai ở state %s' % state)
            if state in ('outstanding', 'partial'):
                self.assertEqual(sum(i['amount'] for i in summary['invoices']),
                                 summary['remaining'],
                                 'Dư hoá đơn không khớp còn phải trả (%s)' % state)
            self.assertEqual(summary['invoice_count'], len(summary['invoices']))

    def test_state_matches_amounts(self):
        """State suy ra đúng từ số tiền (điều kiện template dùng để chọn biến thể)."""
        for state, summary in self._all_states().items():
            if state == 'empty':
                self.assertEqual(summary['total'], 0)
            elif state == 'paid':
                self.assertEqual(summary['remaining'], 0)
                self.assertTrue(summary['confirmed_date'])
            elif state == 'partial':
                self.assertTrue(0 < summary['paid'] < summary['total'])
                self.assertFalse(summary['has_overdue'])
            else:
                self.assertTrue(summary['has_overdue'])
                self.assertTrue(summary['nearest_due'])

    def test_invalid_week_falls_back(self):
        """Query param người dùng sửa tay được → fallback tuần hiện tại, không raise."""
        default = self.debt.get_summary(self.franchise_id)
        for bad in (None, '', 'abc', '9999-W99', '2026-W', 0, False):
            summary = self.debt.get_summary(self.franchise_id, week=bad)
            self.assertEqual(summary['week_key'], default['week_key'])

    def test_no_franchise_returns_empty_not_error(self):
        """Chưa chọn cửa hàng → empty state đầy đủ key, KHÔNG exception."""
        summary = self.debt.get_summary(False)
        self.assertEqual(summary['state'], 'empty')
        self.assertEqual(summary['invoices'], [])
        self.assertTrue(SUMMARY_KEYS.issubset(set(summary)))

    def test_week_options_are_consecutive_mondays(self):
        options = self.debt._week_options(today=date(2026, 7, 31))
        self.assertEqual(len(options), 6)
        self.assertEqual(options[0]['monday'], date(2026, 7, 27))
        for prev, nxt in zip(options, options[1:]):
            self.assertEqual(prev['monday'] - nxt['monday'], timedelta(days=7))

    def test_payments_within_range_and_total(self):
        history = self.debt.get_payments(self.franchise_id, today=date(2026, 7, 31))
        self.assertEqual(history['date_from'], date(2026, 7, 1))
        self.assertEqual(history['date_to'], date(2026, 7, 31))
        self.assertTrue(history['payments'])
        self.assertEqual(history['total'], sum(p['amount'] for p in history['payments']))
        for pay in history['payments']:
            self.assertTrue(history['date_from'] <= pay['date'] <= history['date_to'])

    def test_payments_invalid_month_falls_back(self):
        default = self.debt.get_payments(self.franchise_id)
        for bad in (None, '', 'nope', '1999-01'):
            self.assertEqual(self.debt.get_payments(self.franchise_id, month=bad)['month_key'],
                             default['month_key'])

    def test_bank_info_is_illustrative(self):
        """Figma ghi rõ "minh họa" — giữ nguyên đến khi BA chốt QR tĩnh/động."""
        bank = self.debt.get_bank_info(self.franchise_id, 12650000, 28)
        self.assertIn('minh họa', bank['name'])
        self.assertIn('K28', bank['memo'])
        self.assertIn('12650000', bank['memo'])

    def test_shell_badge_shape(self):
        """2 điểm vào ở shell chỉ đọc 3 key này — đổi shape là vỡ Home + sheet Thêm."""
        badge = self.debt.get_shell_badge()
        self.assertEqual(set(badge), {'overdue_count', 'remaining', 'remaining_label'})


@tagged('post_install', '-at_install', 'wujia_debt')
class TestPortalDebtRoutes(HttpCase):

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')

    def _get(self, url):
        res = self.url_open(url, timeout=30)
        self.assertEqual(res.status_code, 200, 'HTTP %s cho %s' % (res.status_code, url))
        return res.text

    def test_routes_render_without_store_selected(self):
        """Admin không thuộc franchise nào → empty state, KHÔNG 500."""
        for url in ('/portal/debt', '/portal/debt/payment-history', '/portal/debt/pay'):
            self.assertIn('wj-debt', self._get(url))

    def test_overview_week_filter_and_all(self):
        weeks = self.env['wujia.portal.debt']._week_options()
        body = self._get('/portal/debt?week=%s&all=1' % weeks[1]['key'])
        self.assertIn(weeks[1]['label'], body)

    def test_pay_page_shows_illustrative_notice(self):
        body = self._get('/portal/debt/pay')
        self.assertIn('QR minh họa', body)
        self.assertIn('Vietcombank (minh họa)', body)

    def test_inherited_views_still_render(self):
        """2 view inherit không được làm vỡ shell/Home."""
        body = self._get('/portal')
        # 2 điểm vào: dòng sheet "Thêm" + tile KPI Home (QWeb xuất '&' thô, không escape).
        self.assertEqual(body.count('href="/portal/debt"'), 2,
                         'Thiếu điểm vào Công nợ ở Home hoặc sheet Thêm')
        self.assertIn('wujia-msheet-item wujia-msheet-item--debt', body)
        self.assertIn('Hóa đơn, công nợ và thanh toán', body)
