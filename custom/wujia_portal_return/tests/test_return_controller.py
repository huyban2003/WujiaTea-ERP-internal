"""Task STT3 — controller Portal ↔ bù hàng (12 acceptance BA).

Chạy: `--test-tags wujia_return_ct`.

Phần thuần hàm (cửa sổ 10 ngày, cấu hình bù, minh chứng, nhãn trạng thái) test
thẳng helper của controller; phần đi qua HTTP test bằng HttpCase để bắt đúng
đường người dùng đi (guard cửa hàng, notice, redirect).
"""

import io
from datetime import timedelta

from werkzeug.datastructures import FileStorage

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase
from odoo.exceptions import ValidationError

from odoo.addons.wujia_portal_return.controllers.portal import (
    MAX_IMAGES, MAX_TOTAL_MB, MIN_IMAGES, ORDER_WINDOW_DAYS,
    WujiaPortalReturn, state_label,
)

JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 60
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 60
MP4 = b'\x00\x00\x00\x18ftypmp42' + b'\x00' * 60
MOV = b'\x00\x00\x00\x14ftypqt  ' + b'\x00' * 60
TEXT = b'just a plain text file, definitely not an image'


def _file(data, filename='a.jpg', content_type='image/jpeg', pad=0):
    return FileStorage(stream=io.BytesIO(data + b'\x00' * pad),
                       filename=filename, content_type=content_type)


class ReturnFixture:
    """1 cửa hàng + 1 cửa hàng khác, sản phẩm có/không cấu hình bù, đơn trong/ngoài 10 ngày."""

    @classmethod
    def _setup_return_data(cls):
        env = cls.env
        Partner = env['res.partner']
        Franchise = env['wujia.franchise.management']
        cls.franchise = Franchise.create({
            'code': 'CT3A', 'name': 'CT3 store A', 'franchise_end_date': '2030-01-01',
            'partner_id': Partner.create({'name': 'CT3A partner'}).id})
        cls.other = Franchise.create({
            'code': 'CT3B', 'name': 'CT3 store B', 'franchise_end_date': '2030-01-01',
            'partner_id': Partner.create({'name': 'CT3B partner'}).id})

        cls.uom_kg = env.ref('uom.product_uom_kgm')
        cls.uom_unit = env.ref('uom.product_uom_unit')
        cls.tax = env['account.tax'].create({
            'name': 'CT3 VAT 8', 'amount': 8.0, 'amount_type': 'percent',
            'type_tax_use': 'sale'})
        cls.product = env['product.product'].create({
            'name': 'CT3 tea', 'type': 'consu', 'list_price': 100_000,
            'uom_id': cls.uom_kg.id, 'taxes_id': [(6, 0, cls.tax.ids)],
            'compensation_enabled': True,
            'compensation_policy': 'accumulate',
            'compensation_claim_uom_id': cls.uom_kg.id,
            'compensation_delivery_uom_id': cls.uom_kg.id,
            'compensation_unit_qty': 10.0,
        })
        cls.product_noconf = env['product.product'].create({
            'name': 'CT3 unconfigured', 'type': 'consu', 'list_price': 50_000})

        cls.issue_type = env['wujia.return.issue.type'].create({
            'name': 'CT3 broken', 'active': True})

        cls.order_ok = cls._order(cls.franchise, cls.product, confirm=True)
        cls.order_draft = cls._order(cls.franchise, cls.product, confirm=False)
        cls.order_old = cls._order(cls.franchise, cls.product, confirm=True)
        cls.order_old.date_order = fields.Datetime.now() - timedelta(
            days=ORDER_WINDOW_DAYS + 1)
        cls.order_other = cls._order(cls.other, cls.product, confirm=True)

    @classmethod
    def _order(cls, franchise, product, confirm=False):
        order = cls.env['sale.order'].create({
            'partner_id': franchise.partner_id.id,
            'franchise_id': franchise.id,
            'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 5})],
        })
        if confirm:
            order.action_confirm()
        return order

    @classmethod
    def _request(cls, franchise=None, order=None, state='submitted', **kw):
        franchise = franchise or cls.franchise
        order = order or cls.order_ok
        vals = {
            'franchise_id': franchise.id,
            'sale_order_id': order.id,
            'sale_order_line_id': order.order_line[0].id,
            'request_uom_id': cls.uom_kg.id,
            'request_qty': 12.0,
            'opening_datetime': fields.Datetime.now(),
            'issue_type_id': cls.issue_type.id,
            'state': state,
        }
        vals.update(kw)
        return cls.env['wujia.return.request'].create(vals)


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestEligibleOrders(TransactionCase, ReturnFixture):
    """Acceptance #4 — chỉ đơn đã xác nhận, trong 10 ngày, đúng cửa hàng."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()

    def _eligible(self, franchise):
        domain = WujiaPortalReturn()._eligible_order_domain([franchise.id])
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
        cls.ctrl = WujiaPortalReturn()

    def test_configured_product_passes(self):
        self.assertIsNone(self.ctrl._check_compensation_config(self.product))

    def test_unconfigured_product_gets_business_message(self):
        msg = self.ctrl._check_compensation_config(self.product_noconf)
        self.assertIn('chưa được cấu hình chính sách bù hàng', msg)

    def test_accumulate_needs_positive_integer_ratio(self):
        self.product.compensation_unit_qty = 2.5
        self.assertIsNotNone(self.ctrl._check_compensation_config(self.product))
        self.product.compensation_unit_qty = 10.0
        self.assertIsNone(self.ctrl._check_compensation_config(self.product))

    def test_accumulate_ratio_zero_rejected(self):
        # `@api.constrains` của product chặn ghi 0 vào DB, nên dựng bản ghi
        # in-memory để kiểm đúng lớp controller (dữ liệu cũ/import có thể lọt).
        ghost = self.env['product.product'].new({
            'name': 'ghost',
            'compensation_enabled': True,
            'compensation_policy': 'accumulate',
            'compensation_claim_uom_id': self.uom_kg.id,
            'compensation_delivery_uom_id': self.uom_kg.id,
            'compensation_unit_qty': 0.0,
        })
        self.assertIsNotNone(self.ctrl._check_compensation_config(ghost))

    def test_exact_policy_rejects_uom_of_another_family(self):
        self.product.compensation_policy = 'exact'
        self.product.compensation_delivery_uom_id = self.uom_unit
        self.assertIsNotNone(self.ctrl._check_compensation_config(self.product))


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestEvidenceValidation(TransactionCase):
    """Acceptance #7 — 3–5 ảnh, ≤1 video, MIME thật, dung lượng từng tệp + tổng."""

    def setUp(self):
        super().setUp()
        self.ctrl = WujiaPortalReturn()

    def _images(self, n, data=JPEG, **kw):
        return [_file(data, filename=f'p{i}.jpg', **kw) for i in range(n)]

    def test_three_to_five_images_accepted(self):
        for n in (MIN_IMAGES, 4, MAX_IMAGES):
            self.ctrl._validate_evidence(self._images(n), [])

    def test_two_images_rejected(self):
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(self._images(2), [])

    def test_six_images_rejected(self):
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(self._images(6), [])

    def test_draft_may_have_fewer_images(self):
        self.ctrl._validate_evidence(self._images(1), [], require_min=False)

    def test_png_accepted(self):
        self.ctrl._validate_evidence(
            [_file(PNG, filename=f'p{i}.png', content_type='image/png')
             for i in range(3)], [])

    def test_fake_extension_rejected_by_real_mime(self):
        """Đổi đuôi + đổi header vẫn không qua được: MIME đọc từ nội dung."""
        files = self._images(2) + [_file(TEXT, filename='evil.jpg')]
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(files, [])

    def test_image_over_size_limit_rejected(self):
        big = self._images(2) + [_file(JPEG, filename='big.jpg', pad=6 * 1024 * 1024)]
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(big, [])

    def test_video_mp4_and_mov_accepted(self):
        self.ctrl._validate_evidence(
            self._images(3), [_file(MP4, 'v.mp4', 'video/mp4')])
        self.ctrl._validate_evidence(
            self._images(3),
            [_file(MOV, 'v.mov', 'application/octet-stream')])

    def test_video_mime_is_sniffed_not_trusted(self):
        real = self.ctrl._real_mime(_file(MOV, 'v.mov', 'application/octet-stream'))
        self.assertEqual(real, 'video/quicktime')
        self.assertEqual(self.ctrl._real_mime(_file(MP4, 'v.mp4')), 'video/mp4')

    def test_second_video_rejected(self):
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(
                self._images(3),
                [_file(MP4, 'v1.mp4', 'video/mp4'), _file(MP4, 'v2.mp4', 'video/mp4')])

    def test_video_over_size_limit_rejected(self):
        with self.assertRaises(ValidationError):
            self.ctrl._validate_evidence(
                self._images(3),
                [_file(MP4, 'v.mp4', 'video/mp4', pad=11 * 1024 * 1024)])

    def test_total_over_30mb_rejected(self):
        # Từng tệp vẫn dưới trần riêng (ảnh <5MB, video <10MB) nhưng tổng ~34MB.
        images = [_file(JPEG, filename=f'p{i}.jpg', pad=int(4.9 * 1024 * 1024))
                  for i in range(5)]
        video = [_file(MP4, 'v.mp4', 'video/mp4', pad=int(9.9 * 1024 * 1024))]
        with self.assertRaises(ValidationError) as err:
            self.ctrl._validate_evidence(images, video)
        self.assertIn(str(MAX_TOTAL_MB), str(err.exception))


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestStateLabels(TransactionCase, ReturnFixture):
    """Acceptance #8 — 6 nhãn BA, 'Đang bù một phần' suy từ tiến độ, không đổi schema."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()

    def test_basic_labels(self):
        expected = {'submitted': 'Đã gửi', 'reviewing': 'Đang xử lý',
                    'approved': 'Đã duyệt', 'rejected': 'Từ chối',
                    'done': 'Hoàn tất'}
        rr = self._request()
        for state, label in expected.items():
            rr.state = state
            self.assertEqual(state_label(rr)[0], label)

    def test_partial_compensation_label(self):
        rr = self._request(state='approved', resolution_type='compensation',
                           approved_qty=20.0, approved_uom_id=self.uom_kg.id)
        self.env['wujia.compensation.allocation'].create({
            'request_id': rr.id, 'allocated_qty': 20.0,
            'allocation_uom_id': self.uom_kg.id, 'delivered_qty': 5.0,
            'state': 'partial'})
        rr.state = 'processing'
        self.assertEqual(rr.compensation_status, 'partial')
        self.assertEqual(state_label(rr)[0], 'Đang bù một phần')


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


@tagged('post_install', '-at_install', 'wujia_return_ct')
class TestPortalRoutes(HttpCase, ReturnFixture):
    """Acceptance #2/#3/#9 — phạm vi cửa hàng, bộ lọc, phản hồi cuối cùng."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_return_data()
        cls.member_user = cls.env['res.users'].create({
            'name': 'CT3 owner', 'login': 'ct3.owner', 'password': 'ct3.owner',
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })
        cls.env['wujia.franchise.member'].create({
            'franchise_id': cls.franchise.id,
            'user_id': cls.member_user.id,
            'role': 'owner',
        })
        cls.mine = cls._request(backend_note='SECRET internal note',
                                approval_note='HQ duyệt 20kg',
                                resolution_type='compensation',
                                approved_qty=20.0,
                                approved_uom_id=cls.uom_kg.id,
                                compensation_product_id=cls.product.id)
        cls.theirs = cls._request(franchise=cls.other, order=cls.order_other)

    def _login_portal(self):
        self.authenticate('ct3.owner', 'ct3.owner')

    def test_list_shows_only_my_store(self):
        self._login_portal()
        body = self.url_open('/portal/return').text
        self.assertIn(self.mine.name, body)
        self.assertNotIn(self.theirs.name, body)

    def test_cross_store_detail_redirects_with_notice(self):
        self._login_portal()
        res = self.url_open(f'/portal/return/{self.theirs.id}')
        self.assertNotIn(self.theirs.name, res.text)
        self.assertIn('Không tìm thấy yêu cầu hoặc bạn không có quyền truy cập',
                      res.text)

    def test_detail_hides_internal_note_and_shows_final_reply(self):
        self._login_portal()
        body = self.url_open(f'/portal/return/{self.mine.id}').text
        self.assertNotIn('SECRET internal note', body)
        self.assertIn('HQ duyệt 20kg', body)

    def test_bad_date_range_returns_friendly_message(self):
        self._login_portal()
        body = self.url_open(
            '/portal/return?date_from=2026-12-31&date_to=2026-01-01').text
        self.assertIn('Bộ lọc không hợp lệ', body)

    def test_keyword_and_pagination(self):
        self._login_portal()
        hit = self.url_open(f'/portal/return?q={self.mine.name}').text
        self.assertIn(self.mine.name, hit)
        miss = self.url_open('/portal/return?q=KHONGTONTAI999').text
        self.assertNotIn(self.mine.name, miss)
        # page_size là số hợp lệ và có trần — giá trị rác không được làm nổ trang.
        self.assertEqual(self.url_open('/portal/return?page_size=abc').status_code, 200)
        self.assertEqual(self.url_open('/portal/return?page=99999').status_code, 200)
