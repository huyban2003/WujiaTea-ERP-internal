"""Seed dữ liệu công nợ để smoke màn Công nợ portal (Sprint 48, BA Tasks!STT9).

Tạo cho cửa hàng ĐẦU TIÊN: vài hoá đơn (có 1 quá hạn) + 1 credit note + 1 payment đã
ghi sổ, và bật 1 tài khoản ngân hàng công ty lên portal. Chạy XONG mới thấy số thật ở
/portal/debt, /portal/debt/payment-history, /portal/debt/pay.

LOCAL-ONLY (gitignored theo rule §5) — KHÔNG chạy trên production. Idempotent: đánh dấu
bằng ref='SEED-DEBT' / memo, chạy lại không nhân đôi.

Cách chạy (Linux):
  cd /home/huyban/odoo-dev/WujiaTea/odoo19
  python odoo-bin shell -c ../config/odoo.conf -d wujia_tea_19 --no-http \\
      < ../scripts/seed_debt_demo.py
"""
from datetime import date, timedelta

print("=== SEED DEBT DEMO ===")

franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
if not franchise:
    raise SystemExit("Không có franchise nào — seed franchise trước.")
print(f"Franchise: [{franchise.code}] {franchise.name} (id={franchise.id})")

company = env.company
partner = franchise.partner_id or env.ref('base.user_admin').partner_id
income = env['account.account'].search([('account_type', '=', 'income')], limit=1)
sale_journal = env['account.journal'].search(
    [('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
if not (income and sale_journal):
    raise SystemExit("Thiếu account income / sale journal — cài l10n/account chart trước.")

today = date.today()
monday = today - timedelta(days=today.weekday())


def make_move(move_type, inv_date, due, amount, tag):
    ref = 'SEED-DEBT-%s' % tag
    existing = env['account.move'].search([('ref', '=', ref)], limit=1)
    if existing:
        return existing
    move = env['account.move'].create({
        'move_type': move_type,
        'partner_id': partner.id,
        'invoice_date': inv_date,
        'journal_id': sale_journal.id,
        'franchise_id': franchise.id,
        'ref': ref,
        'invoice_payment_term_id': False,
        'invoice_line_ids': [(0, 0, {
            'name': 'Nguyên liệu tuần %s' % inv_date.isocalendar()[1],
            'quantity': 1, 'price_unit': amount,
            'account_id': income.id, 'tax_ids': [(6, 0, [])],
        })],
    })
    move.action_post()
    move.invoice_date_due = due
    return move


# Tuần hiện tại: 1 quá hạn + 1 chưa tới hạn + 1 credit note.
m1 = make_move('out_invoice', monday + timedelta(days=1), monday - timedelta(days=2),
               3_400_000, 'W0-OVERDUE')
m2 = make_move('out_invoice', monday + timedelta(days=2), monday + timedelta(days=9),
               5_250_000, 'W0-OPEN')
cn = make_move('out_refund', monday + timedelta(days=2), monday + timedelta(days=2),
               1_150_000, 'W0-CREDIT')
# Tuần trước: đã thanh toán đủ (để state 'paid' hiển thị).
m3 = make_move('out_invoice', monday - timedelta(days=6), monday - timedelta(days=1),
               2_000_000, 'W1-PAID')
print(f"Invoices: {m1.name}, {m2.name}, credit {cn.name}, prev-week {m3.name}")

# Payment đã ghi sổ trong THÁNG HIỆN TẠI — để hiện ngay ở lịch sử thanh toán (bộ lọc
# mặc định = tháng này). Dùng `today` thay vì monday-3 vì đầu tháng monday-3 rơi sang
# tháng trước → khoản thu bị lọc mất khỏi màn mặc định.
pay_ref = 'SEED-DEBT-PAY1'
payment = env['account.payment'].search([('memo', '=', pay_ref)], limit=1)
if not payment:
    payment = env['account.payment'].create({
        'amount': 4_150_000, 'date': today,
        'payment_type': 'inbound', 'partner_type': 'customer',
        'partner_id': partner.id, 'memo': pay_ref,
    })
    payment.action_post()
    payment.franchise_id = franchise
print(f"Payment: {payment.name} ({payment.state})")

# Bật 1 tài khoản ngân hàng công ty lên portal (QR/chuyển khoản).
bank = env['res.partner.bank'].search([
    ('id', 'in', company.bank_ids.ids), ('portal_payment_enabled', '=', True)], limit=1)
if not bank:
    bank = env['res.partner.bank'].search([('id', 'in', company.bank_ids.ids)], limit=1)
    if not bank:
        vn_bank = env['res.bank'].search([], limit=1)
        bank = env['res.partner.bank'].create({
            'acc_number': '0123456789', 'acc_holder_name': company.name,
            'partner_id': company.partner_id.id,
            'bank_id': vn_bank.id if vn_bank else False,
            'sequence': 1,
        })
    bank.portal_payment_enabled = True
print(f"Portal bank: {bank.acc_number} (portal_payment_enabled={bank.portal_payment_enabled})")

# Tính lại badge công nợ.
franchise._recompute_portal_debt_batch()
print(f"Badge → overdue={franchise.portal_overdue_invoice_count} "
      f"remaining={franchise.portal_debt_remaining}")

env.cr.commit()
print("=== DONE (committed) ===")
