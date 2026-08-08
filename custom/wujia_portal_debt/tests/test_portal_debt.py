"""Test module Công nợ portal — wire backend thật (Sprint 48, BA Tasks!STT9).

Chạy: `--test-tags wujia_debt`.

  1. `TestPortalDebtWired` — seam đọc account.move/account.payment thật: scope franchise
     (isolation), credit note giảm nợ, overdue, payment history lọc trạng thái, bank info,
     badge store.
  2. `TestPortalDebtAccess` — controller chặn Staff, cho Owner/Manager, empty khi chưa
     chọn cửa hàng (HttpCase).

⚠️ KHÔNG import `odoo.addons.account.tests.common` — chuỗi import của nó kéo theo
`base.tests.test_date_utils` dùng `freeze_time(as_kwarg=...)`, vỡ với freezegun cũ trong
env. Dựng fixture kế toán bằng ORM thuần trên chart `generic_coa` đã cài sẵn.
"""

from datetime import date, timedelta

from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

SUMMARY_KEYS = {
    'franchise_id', 'franchise_code', 'week_key', 'week_label', 'week_number',
    'week_short', 'weeks', 'state', 'total', 'paid', 'remaining', 'invoice_count',
    'has_overdue', 'overdue_count', 'nearest_due', 'confirmed_date', 'invoices',
}
INVOICE_KEYS = {'name', 'date', 'due', 'status', 'amount'}
# PC (STT10) mở rộng additive: bảng cần 3 số/hoá đơn.
PC_INVOICE_KEYS = {'total', 'paid', 'remaining'}
PAYMENT_KEYS = {'ref', 'date', 'time', 'method', 'trace', 'amount', 'state'}


@tagged('post_install', '-at_install', 'wujia_debt')
class TestPortalDebtWired(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.debt = cls.env['wujia.portal.debt']
        cls.company = cls.env.company
        cls.income = cls.env['account.account'].search(
            [('account_type', '=', 'income'), ('company_ids', 'in', cls.company.id)], limit=1) \
            or cls.env['account.account'].search([('account_type', '=', 'income')], limit=1)
        cls.sale_journal = cls.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', cls.company.id)], limit=1)
        cls.bank_journal = cls.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('company_id', '=', cls.company.id)], limit=1)
        cls.customer = cls.env['res.partner'].create({'name': 'Debt Test Customer'})

        Partner = cls.env['res.partner']
        Franchise = cls.env['wujia.franchise.management']
        cls.franchise = Franchise.create({
            'code': 'HDEBT1', 'name': 'Debt store 1', 'franchise_end_date': '2030-01-01',
            'partner_id': Partner.create({'name': 'HDEBT1 partner'}).id})
        cls.other = Franchise.create({
            'code': 'HDEBT2', 'name': 'Debt store 2', 'franchise_end_date': '2030-01-01',
            'partner_id': Partner.create({'name': 'HDEBT2 partner'}).id})

        # Tuần thử: Mon 2026-07-13 → Sun 2026-07-19; "hôm nay" của logic tuần = 2026-07-15.
        cls.week_today = date(2026, 7, 15)

        cls.inv_overdue = cls._move('out_invoice', cls.franchise, date(2026, 7, 14),
                                    date(2026, 7, 14), 1_000_000)   # due < 07-15 → overdue
        cls.inv_open = cls._move('out_invoice', cls.franchise, date(2026, 7, 16),
                                 date(2026, 7, 25), 2_000_000)      # chưa tới hạn trong tuần
        cls.credit = cls._move('out_refund', cls.franchise, date(2026, 7, 16),
                               date(2026, 7, 16), 500_000)           # credit note giảm nợ
        cls._move('out_invoice', cls.other, date(2026, 7, 16),      # cửa hàng khác — KHÔNG lọt
                  date(2026, 7, 25), 9_000_000)

        cls.pay_ok = cls._payment(4_150_000, date(2026, 7, 10), cls.franchise, post=True)
        cls.pay_draft = cls._payment(999_000, date(2026, 7, 12), cls.franchise, post=False)

    @classmethod
    def _move(cls, move_type, franchise, inv_date, due, amount):
        move = cls.env['account.move'].create({
            'move_type': move_type,
            'partner_id': cls.customer.id,
            'invoice_date': inv_date,
            'journal_id': cls.sale_journal.id,
            'franchise_id': franchise.id,
            'invoice_payment_term_id': False,
            'invoice_line_ids': [(0, 0, {
                'name': 'line', 'quantity': 1, 'price_unit': amount,
                'account_id': cls.income.id, 'tax_ids': [(6, 0, [])],
            })],
        })
        move.action_post()
        move.invoice_date_due = due   # sau post → payment term không tính đè
        return move

    @classmethod
    def _payment(cls, amount, pay_date, franchise, post):
        payment = cls.env['account.payment'].create({
            'amount': amount, 'date': pay_date, 'payment_type': 'inbound',
            'partner_type': 'customer', 'partner_id': cls.customer.id,
            'journal_id': cls.bank_journal.id,
        })
        if post:
            payment.action_post()
        payment.franchise_id = franchise
        return payment

    def _summary(self):
        return self.debt.get_summary(self.franchise.id, week='2026-W29', today=self.week_today)

    # ---- summary -----------------------------------------------------
    def test_summary_keys_and_types(self):
        s = self._summary()
        self.assertTrue(SUMMARY_KEYS.issubset(set(s)))
        self.assertEqual(s['invoice_count'], len(s['invoices']))
        for inv in s['invoices']:
            self.assertTrue(INVOICE_KEYS.issubset(set(inv)))
            self.assertIsInstance(inv['date'], date)   # template gọi .strftime
            self.assertIsInstance(inv['due'], date)
            self.assertIn(inv['status'], ('overdue', 'unpaid', 'partial', 'paid'))

    # ---- PC (STT10): invoice enrichment total/paid/remaining --------
    def test_invoice_enrichment_total_paid_remaining(self):
        s = self._summary()
        for inv in s['invoices']:
            self.assertTrue(PC_INVOICE_KEYS.issubset(set(inv)),
                            'thiếu key PC total/paid/remaining trên hoá đơn')
            # Bất biến bảng PC: Tổng = Đã trả + Còn phải trả (giữ cả với credit note âm).
            self.assertAlmostEqual(inv['total'], inv['paid'] + inv['remaining'], places=2)
        # Tổng 3 cột khớp tổng tuần (credit note out_refund vẫn âm nhất quán).
        self.assertAlmostEqual(sum(i['total'] for i in s['invoices']), s['total'], places=2)
        self.assertAlmostEqual(sum(i['remaining'] for i in s['invoices']), s['remaining'], places=2)
        by_name = {i['name']: i for i in s['invoices']}
        ov = by_name[self.inv_overdue.name]                 # chưa trả đồng nào
        self.assertEqual((ov['total'], ov['paid'], ov['remaining']), (1_000_000, 0, 1_000_000))
        cn = by_name[self.credit.name]                       # credit note giữ dấu âm
        self.assertEqual(cn['total'], -500_000)
        self.assertEqual(cn['paid'], 0)

    def test_credit_note_reduces_debt_and_totals_consistent(self):
        s = self._summary()
        self.assertEqual(s['total'], 2_500_000)        # 1,000,000 + 2,000,000 − 500,000
        self.assertEqual(s['remaining'], 2_500_000)
        self.assertEqual(s['paid'] + s['remaining'], s['total'])
        self.assertEqual(s['invoice_count'], 3)

    def test_overdue_within_week(self):
        s = self._summary()
        self.assertTrue(s['has_overdue'])
        self.assertEqual(s['overdue_count'], 1)        # chỉ inv_overdue trong tuần
        self.assertEqual(s['state'], 'outstanding')
        self.assertEqual(s['nearest_due'], date(2026, 7, 14))

    def test_franchise_isolation(self):
        s = self._summary()
        self.assertEqual(s['total'], 2_500_000)        # 9tr của cửa hàng khác không cộng vào
        other_name = self.env['account.move'].search(
            [('franchise_id', '=', self.other.id)], limit=1).name
        self.assertNotIn(other_name, {inv['name'] for inv in s['invoices']})

    def test_no_franchise_returns_empty(self):
        s = self.debt.get_summary(False, today=self.week_today)
        self.assertEqual(s['state'], 'empty')
        self.assertEqual(s['invoices'], [])
        self.assertTrue(SUMMARY_KEYS.issubset(set(s)))

    def test_invalid_week_falls_back(self):
        default = self.debt.get_summary(self.franchise.id, today=self.week_today)
        for bad in (None, '', 'abc', '9999-W99', 0, False):
            self.assertEqual(
                self.debt.get_summary(self.franchise.id, week=bad, today=self.week_today)['week_key'],
                default['week_key'])

    # ---- payment history --------------------------------------------
    def test_payment_history_excludes_draft(self):
        h = self.debt.get_payments(self.franchise.id, today=date(2026, 7, 31))
        self.assertEqual(h['date_from'], date(2026, 7, 1))
        refs = {p['ref'] for p in h['payments']}
        self.assertIn(self.pay_ok.name, refs)
        self.assertNotIn(self.pay_draft.name, refs)    # draft bị loại
        self.assertEqual(h['total'], 4_150_000)
        for p in h['payments']:
            self.assertTrue(PAYMENT_KEYS.issubset(set(p)))
            self.assertIsInstance(p['date'], date)

    def test_payment_history_franchise_isolation(self):
        other_pay = self._payment(7_000_000, date(2026, 7, 5), self.other, post=True)
        h = self.debt.get_payments(self.franchise.id, today=date(2026, 7, 31))
        self.assertNotIn(other_pay.name, {p['ref'] for p in h['payments']})

    # ---- PC (STT10): keyword filter (mã payment / nội dung) ---------
    def test_payment_history_keyword_filters(self):
        base = self.debt.get_payments(self.franchise.id, today=date(2026, 7, 31))
        self.assertIn(self.pay_ok.name, {p['ref'] for p in base['payments']})
        # Khớp theo mã payment → còn giao dịch; không khớp → rỗng.
        hit = self.debt.get_payments(self.franchise.id, today=date(2026, 7, 31),
                                     keyword=self.pay_ok.name)
        self.assertIn(self.pay_ok.name, {p['ref'] for p in hit['payments']})
        miss = self.debt.get_payments(self.franchise.id, today=date(2026, 7, 31),
                                      keyword='ZZ-KHONG-KHOP-QWERTY')
        self.assertEqual(miss['payments'], [])
        # keyword rỗng/None ⇒ không đổi hành vi (mobile không truyền).
        for empty in (None, '', '   '):
            self.assertEqual(len(self.debt.get_payments(
                self.franchise.id, today=date(2026, 7, 31), keyword=empty)['payments']),
                len(base['payments']))

    # ---- bank info ---------------------------------------------------
    def test_bank_info_picks_smallest_sequence_enabled(self):
        Bank = self.env['res.partner.bank']
        partner = self.company.partner_id
        Bank.create({'acc_number': 'ACC-DISABLED', 'partner_id': partner.id,
                     'sequence': 1, 'portal_payment_enabled': False})
        Bank.create({'acc_number': 'ACC-WIN', 'partner_id': partner.id,
                     'sequence': 5, 'portal_payment_enabled': True})
        Bank.create({'acc_number': 'ACC-LATE', 'partner_id': partner.id,
                     'sequence': 9, 'portal_payment_enabled': True})
        bank = self.debt.get_bank_info(self.franchise.id, 2_500_000, 29)
        self.assertEqual(bank['account'], 'ACC-WIN')          # enabled + sequence nhỏ nhất
        self.assertEqual(bank['memo'], 'HDEBT1 K29 2500000')  # backend tự tính nội dung CK

    def test_bank_info_not_configured_message(self):
        bank = self.debt.get_bank_info(self.franchise.id, 100, 29)
        self.assertIn('chưa được cấu hình', bank['name'])     # không TK nào bật portal
        self.assertEqual(bank['account'], '')

    # ---- PC (STT10): tách empty → empty_week / no_debt (rule 10c/10d) ----
    def test_empty_substate(self):
        # Cửa hàng còn công nợ ở kỳ khác → 'empty_week'.
        self.franchise.invalidate_recordset(['portal_debt_remaining'])
        self.assertGreater(self.franchise.portal_debt_remaining, 0)
        self.assertEqual(self.debt._empty_substate(self.franchise.id), 'empty_week')
        # Cửa hàng không phát sinh gì → hết nợ mọi kỳ → 'no_debt'.
        clean = self.env['wujia.franchise.management'].create({
            'code': 'HDEBT0', 'name': 'Debt store empty', 'franchise_end_date': '2030-01-01',
            'partner_id': self.env['res.partner'].create({'name': 'HDEBT0 partner'}).id})
        self.assertEqual(clean.portal_debt_remaining or 0, 0)
        self.assertEqual(self.debt._empty_substate(clean.id), 'no_debt')
        # Chưa chọn cửa hàng → 'no_debt' (không raise).
        self.assertEqual(self.debt._empty_substate(False), 'no_debt')

    # ---- badge store (perf) -----------------------------------------
    def test_badge_aggregates_stored(self):
        self.franchise.invalidate_recordset(
            ['portal_overdue_invoice_count', 'portal_debt_remaining'])
        # Badge quá hạn theo NGÀY THẬT: cả 2 hoá đơn (due 07-14 & 07-25) đều đã qua hạn.
        self.assertEqual(self.franchise.portal_overdue_invoice_count, 2)
        self.assertEqual(self.franchise.portal_debt_remaining, 2_500_000)


@tagged('post_install', '-at_install', 'wujia_debt')
class TestPortalDebtAccess(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.franchise = cls.env['wujia.franchise.management'].create({
            'code': 'HACC1', 'name': 'Access store', 'franchise_end_date': '2030-01-01',
            'partner_id': cls.env['res.partner'].create({'name': 'HACC1 partner'}).id})
        cls.owner = cls._portal_user('debt_owner', 'owner')
        cls.staff = cls._portal_user('debt_staff', 'staff')

    @classmethod
    def _portal_user(cls, login, role):
        user = cls.env['res.users'].create({
            'name': login, 'login': login, 'password': login,
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })
        cls.env['wujia.franchise.member'].create({
            'user_id': user.id, 'franchise_id': cls.franchise.id, 'role': role})
        return user

    def test_owner_can_view(self):
        self.authenticate('debt_owner', 'debt_owner')
        res = self.url_open('/portal/debt', timeout=30)
        self.assertEqual(res.status_code, 200)
        self.assertIn('wj-debt', res.text)
        self.assertNotIn('Không có quyền xem', res.text)

    def test_owner_pc_blocks_render(self):
        """Khối desktop STT10 render không lỗi (500 sẽ trượt): tab strip + filter PC."""
        self.authenticate('debt_owner', 'debt_owner')
        res = self.url_open('/portal/debt', timeout=30)
        self.assertEqual(res.status_code, 200)
        self.assertIn('wj-debt-pc', res.text)          # wrapper desktop
        self.assertIn('wj-debt-pc-tabs', res.text)     # tab Công nợ / Lịch sử
        self.assertIn('wj-debt-pc-filter', res.text)   # filter row PC

    def test_payment_history_pc_keyword_renders(self):
        """PC lịch sử + tham số tìm kiếm ?q= render 200 (ô search hiện đúng)."""
        self.authenticate('debt_owner', 'debt_owner')
        res = self.url_open('/portal/debt/payment-history?q=abc', timeout=30)
        self.assertEqual(res.status_code, 200)
        self.assertIn('wj-debt-pc', res.text)
        self.assertIn('Tìm mã thanh toán', res.text)   # placeholder ô search PC

    def test_staff_is_denied(self):
        self.authenticate('debt_staff', 'debt_staff')
        for url in ('/portal/debt', '/portal/debt/payment-history', '/portal/debt/pay'):
            res = self.url_open(url, timeout=30)
            self.assertEqual(res.status_code, 200)     # thông báo dễ hiểu, KHÔNG 500
            self.assertIn('Không có quyền xem', res.text)

    def test_admin_without_store_gets_empty_not_error(self):
        self.authenticate('admin', 'admin')
        for url in ('/portal/debt', '/portal/debt/payment-history', '/portal/debt/pay'):
            res = self.url_open(url, timeout=30)
            self.assertEqual(res.status_code, 200)
            self.assertIn('wj-debt', res.text)
