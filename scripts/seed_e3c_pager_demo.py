"""Seed cho lượt E3c (Pagination — 3 màn cuối: Thi · Công nợ ×2 · Đặt hàng).

Vì sao cần: pager chỉ render khi >1 trang. Đo trên `wujia_tea_e3c` 16/09/2026,
HCM-01 chỉ có **2 phiếu thi · 5 sản phẩm public · 0 hoá đơn · 0 thanh toán** ⇒ cả
ba màn của lượt này không bao giờ vẽ pager, bảng nghiệm thu sẽ xanh mà chưa đo gì
(đúng họ "Pass rỗng" của D6a). Seed đủ >=4 trang để kiểm trang đầu/giữa/cuối + "…".

Idempotent: mọi bản ghi mang dấu SEED-E3C và được search-or-create.

LOCAL-ONLY — chạy trên DB copy, KHÔNG chạy trên wujia_tea_19 hay production.

    cd /home/huyban/odoo-dev/WujiaTea
    python3 odoo19/odoo-bin shell -c config/odoo.conf -d <db-copy> --no-http \
        < scripts/seed_e3c_pager_demo.py
"""
from datetime import date, datetime, timedelta

MARK = 'SEED-E3C'
TARGET_REGS = 45        # thi: 10/trang ⇒ 5 trang
TARGET_PRODUCTS = 60    # catalog: 24/trang ⇒ 3 trang
TARGET_INVOICES = 45    # công nợ: 10/trang ⇒ 5 trang (cùng MỘT tuần)
TARGET_PAYMENTS = 45    # lịch sử thanh toán: 10/trang (cùng MỘT tháng)

print('=== SEED E3C — PAGINATION (thi · công nợ · đặt hàng) ===')

franchise = env['wujia.franchise.management'].search([('code', '=', 'HCM-01')], limit=1)
if not franchise:
    franchise = env['wujia.franchise.management'].search([], order='code', limit=1)
print('Franchise: [%s] %s (id=%s)' % (franchise.code, franchise.name, franchise.id))

owner = env['res.users'].search([('login', '=', 'em.hcm')], limit=1)
if not owner:
    raise SystemExit('Không có user em.hcm — seed portal user trước.')

# --------------------------------------------------------------- 1. Thi
Reg = env['wujia.exam.registration']
have = Reg.search_count([('franchise_id', '=', franchise.id)])
session = env['wujia.exam.session'].search([], order='id desc', limit=1)
member = env['wujia.franchise.member'].search(
    [('franchise_id', '=', franchise.id)], limit=1)
if not session:
    print('! Không có kỳ thi nào — bỏ qua phần thi')
else:
    # Kỳ thi mẫu có sức chứa 4 ⇒ phiếu thứ 5 là ValidationError. Nới sức chứa TRƯỚC
    # (dữ liệu thử trên DB copy) thay vì né bằng cách seed toàn phiếu đã huỷ.
    if session.capacity < TARGET_REGS * 2:
        session.sudo().capacity = TARGET_REGS * 2
        print('Kỳ thi %s: nới sức chứa → %d' % (session.name, session.capacity))
    made = 0
    for i in range(have, TARGET_REGS):
        vals = {
            'franchise_id': franchise.id,
            'session_id': session.id,
            'request_date': datetime.now() - timedelta(days=i),
            'requester_user_id': owner.id,
            # Ràng buộc `_check_participant_bounds`: phiếu submitted/confirmed phải
            # có >=1 dòng nhân sự ⇒ tạo kèm dòng ngay, không tạo phiếu rỗng.
            'line_ids': [(0, 0, {
                'employee_name': 'Nhân sự mẫu %02d (%s)' % (i, MARK),
                'phone': '09%08d' % (10000000 + i),
                'birth_year': 1995 + (i % 10),
            })],
        }
        if member:
            vals['member_id'] = member.id
        reg = Reg.sudo().create(vals)
        # Trải đều 4 trạng thái để bảng không đơn sắc khi chụp ảnh.
        reg.state = ['submitted', 'confirmed', 'rejected', 'cancelled'][i % 4]
        made += 1
    print('Thi: %d → %d phiếu (+%d)' % (have, have + made, made))

# ------------------------------------------------------------ 2. Sản phẩm
Product = env['product.product']
have = Product.search_count([('is_public_portal', '=', True), ('active', '=', True)])
uom = env.ref('uom.product_uom_unit', raise_if_not_found=False)
categ = env['wujia.product.category'].search([], limit=1)
made = 0
for i in range(have, TARGET_PRODUCTS):
    code = '%s-P%03d' % (MARK, i)
    if Product.search_count([('default_code', '=', code)]):
        continue
    vals = {
        'name': 'Nguyên liệu mẫu %02d (%s)' % (i, MARK),
        'default_code': code,
        'is_public_portal': True,
        'list_price': 25000 + i * 1000,
        'type': 'consu',
        # `_check_portal_qty_rules` (wujia_sale): SP public bắt buộc min_qty > 0.
        'min_qty': 1,
    }
    if uom:
        vals['uom_id'] = uom.id
    if categ:
        vals['public_categ_id'] = categ.id
    Product.create(vals)
    made += 1
print('Sản phẩm public: %d → %d (+%d)' % (have, have + made, made))

# ------------------------------------------------------- 3. Công nợ tuần
Move = env['account.move']
partner = franchise.partner_id
company = env.company
income = env['account.account'].search([('account_type', '=', 'income')], limit=1)
journal = env['account.journal'].search(
    [('type', '=', 'sale'), ('company_id', '=', company.id)], limit=1)
if not (partner and income and journal):
    print('! Thiếu partner/account/journal — bỏ qua phần công nợ')
else:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    have = Move.search_count([('franchise_id', '=', franchise.id),
                              ('move_type', '=', 'out_invoice'),
                              ('ref', 'like', MARK)])
    made = 0
    for i in range(have, TARGET_INVOICES):
        ref = '%s-INV%03d' % (MARK, i)
        if Move.search_count([('ref', '=', ref)]):
            continue
        move = Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'franchise_id': franchise.id,
            'ref': ref,
            # Cùng MỘT tuần: pager của màn Công nợ phân trang trong phạm vi tuần.
            'invoice_date': monday + timedelta(days=i % 5),
            'invoice_date_due': monday + timedelta(days=11),
            'invoice_line_ids': [(0, 0, {
                'name': 'Hàng hoá tuần %s dòng %d' % (monday.isocalendar()[1], i),
                'quantity': 1,
                'price_unit': 150000 + i * 1000,
                'account_id': income.id,
            })],
        })
        move.action_post()
        made += 1
    print('Hoá đơn tuần %s: %d → %d (+%d)' % (monday, have, have + made, made))

    # ------------------------------------------- 4. Lịch sử thanh toán
    Payment = env['account.payment']
    bank_journal = env['account.journal'].search(
        [('type', 'in', ('bank', 'cash')), ('company_id', '=', company.id)], limit=1)
    if not bank_journal:
        print('! Không có journal bank/cash — bỏ qua phần thanh toán')
    else:
        have = Payment.search_count([('partner_id', '=', partner.id),
                                     ('memo', 'like', MARK)])
        made = 0
        first_of_month = today.replace(day=1)
        for i in range(have, TARGET_PAYMENTS):
            memo = '%s-PAY%03d' % (MARK, i)
            if Payment.search_count([('memo', '=', memo)]):
                continue
            pay = Payment.create({
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': partner.id,
                'amount': 100000 + i * 5000,
                # Cùng MỘT tháng: màn lịch sử lọc theo tháng.
                'date': min(first_of_month + timedelta(days=i % 27), today),
                'journal_id': bank_journal.id,
                'memo': memo,
                # `_query_payments` lọc THEO franchise_id trên chính payment —
                # thiếu field này là màn lịch sử ra 0 dòng (Pass rỗng).
                'franchise_id': franchise.id,
            })
            pay.action_post()
            made += 1
        print('Thanh toán tháng %s: %d → %d (+%d)' % (
            first_of_month.strftime('%m/%Y'), have, have + made, made))

env.cr.commit()
print('=== XONG ===')
