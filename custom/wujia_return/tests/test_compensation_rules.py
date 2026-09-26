"""Task STT3 — luật bù hàng dùng chung mọi kênh (12 acceptance BA; phần HTTP ở wujia_portal_return).

Chạy: `--test-tags wujia_return_ct`.
"""
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .common import ReturnFixture


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestEligibleOrders(TransactionCase, ReturnFixture):
    """Acceptance #4 — chỉ đơn đã xác nhận, trong 10 ngày, đúng cửa hàng."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()

    def _eligible(self, franchise):
        domain = self.env['wujia.return.request']._portal_eligible_order_domain([franchise.id])
        return self.env['sale.order'].search(domain)

    def test_confirmed_recent_order_is_eligible(self):
        self.assertIn(self.order_ok, self._eligible(self.franchise))

    def test_draft_order_excluded(self):
        self.assertNotIn(self.order_draft, self._eligible(self.franchise))

    def test_order_older_than_window_excluded(self):
        self.assertNotIn(self.order_old, self._eligible(self.franchise))

    def test_other_store_order_excluded(self):
        self.assertNotIn(self.order_other, self._eligible(self.franchise))


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestCompensationConfig(TransactionCase, ReturnFixture):
    """Acceptance #6 — thiếu cấu hình bù thì báo bằng câu nghiệp vụ."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()
        cls.Req = cls.env['wujia.return.request']

    def test_configured_product_passes(self):
        self.assertIsNone(self.Req._portal_check_product_config(self.product))

    def test_unconfigured_product_gets_business_message(self):
        msg = self.Req._portal_check_product_config(self.product_noconf)
        self.assertIn('chưa được cấu hình chính sách bù hàng', msg)

    def test_accumulate_needs_positive_integer_ratio(self):
        self.product.compensation_unit_qty = 2.5
        self.assertIsNotNone(self.Req._portal_check_product_config(self.product))
        self.product.compensation_unit_qty = 10.0
        self.assertIsNone(self.Req._portal_check_product_config(self.product))

    def test_accumulate_ratio_zero_rejected(self):
        # `@api.constrains` của product chặn ghi 0 vào DB, nên dựng bản ghi
        # in-memory để kiểm đúng lớp luật portal (dữ liệu cũ/import có thể lọt).
        ghost = self.env['product.product'].new({
            'name': 'ghost',
            'compensation_enabled': True,
            'compensation_policy': 'accumulate',
            'compensation_claim_uom_id': self.uom_kg.id,
            'compensation_delivery_uom_id': self.uom_kg.id,
            'compensation_unit_qty': 0.0,
        })
        self.assertIsNotNone(self.Req._portal_check_product_config(ghost))

    def test_exact_policy_rejects_uom_of_another_family(self):
        self.product.compensation_policy = 'exact'
        self.product.compensation_delivery_uom_id = self.uom_unit
        self.assertIsNotNone(self.Req._portal_check_product_config(self.product))


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestCompensationOrder(TransactionCase, ReturnFixture):
    """Acceptance #10/#11/#12 — SO bù 0đ + đúng thuế + 'sent'; huỷ SO thì đóng quyền lợi."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()

    def _approved_request(self, qty=20.0):
        rr = self._request(state='approved', resolution_type='compensation',
                           approved_qty=qty, approved_uom_id=self.uom_kg.id,
                           compensation_product_id=self.product.id,
                           compensation_delivery_uom_id=self.uom_kg.id,
                           compensation_unit_qty=10.0,
                           compensation_policy='accumulate')
        rr.approved_date = fields.Datetime.now()
        return rr

    def _process(self, requests):
        wizard = self.env['wujia.compensation.process.wizard'].with_context(
            active_ids=requests.ids).create({})
        wizard.action_confirm()
        return requests.allocation_ids.sale_order_id

    def test_so_is_zero_priced_sent_and_not_confirmed(self):
        rr = self._approved_request()
        order = self._process(rr)
        self.assertEqual(order.state, 'sent')
        self.assertEqual(order.amount_untaxed, 0.0)
        self.assertTrue(order.is_return_order)
        line = order.order_line[0]
        self.assertEqual(line.price_unit, 0.0)
        # Thuế lấy theo cấu hình sản phẩm, không bị ép rỗng.
        self.assertEqual(line.tax_ids, self.tax)

    def test_progress_fields_after_allocation(self):
        rr = self._approved_request()
        self._process(rr)
        self.assertEqual(rr.allocated_qty, 20.0)
        self.assertEqual(rr.compensated_qty, 0.0)   # chưa giao thì chưa tính
        self.assertEqual(rr.remaining_qty, 20.0)
        self.assertEqual(rr.compensation_status, 'allocated')
        self.assertEqual(rr.state, 'processing')

    def test_cancel_so_closes_request_without_restoring_entitlement(self):
        rr = self._approved_request()
        order = self._process(rr)
        order._action_cancel()
        self.assertEqual(rr.allocation_ids.mapped('state'), ['cancel'])
        self.assertEqual(rr.allocation_ids.released_qty, 0.0)  # KHÔNG hoàn quyền lợi
        self.assertEqual(rr.state, 'done')
        self.assertTrue(rr.resolved_date)

    def test_cancelled_request_is_not_reprocessable(self):
        rr = self._approved_request()
        order = self._process(rr)
        order._action_cancel()
        wizard = self.env['wujia.compensation.process.wizard']
        self.assertFalse(wizard._is_eligible(rr))

    def test_cancel_normal_order_does_not_touch_requests(self):
        rr = self._approved_request()
        self._process(rr)
        self.order_ok._action_cancel()
        self.assertEqual(rr.state, 'processing')
        self.assertEqual(rr.allocation_ids.mapped('state'), ['allocated'])
